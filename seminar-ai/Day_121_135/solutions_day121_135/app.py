#!/usr/bin/env python3

import json
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from importlib.util import find_spec
from pathlib import Path

import streamlit as st

from core import cache
from core.book import Book
from core.tools import book_title as get_book_title, info, search_catalog
from pipeline import arc as arc_pipeline
from pipeline import card as card_pipeline
from pipeline import compare as compare_pipeline
from pipeline import entities as entities_pipeline
from pipeline import rouge as eval_pipeline
from pipeline import lexdiv as lexdiv_pipeline
from pipeline import similar as similar_pipeline
from pipeline import summarize as summarize_pipeline
from pipeline import topics as topics_pipeline
from pipeline.similar import COLLECTION

COVER_URL = "https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.cover.medium.jpg"
BERT_READY = find_spec("transformers") is not None and find_spec("torch") is not None
APP_NAME = "InkAlliance"
APP_ICON = Path(__file__).resolve().parent / "docs" / "assets" / "icons" / "inkalliance.png"
APP_CSS = Path(__file__).resolve().parent / "docs" / "assets" / "app.css"


def _inject_css():
    st.markdown(f"<style>{APP_CSS.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


class _StreamlitBuffer:
    def __init__(self, render):
        self.text = ""
        self._render = render

    def write(self, text):
        self.text += text
        self._render(self.text)

    def flush(self):
        pass

    def getvalue(self):
        return self.text


@contextmanager
def st_terminal(label="Exécution"):
    with st.spinner(label):
        placeholder = st.empty()
        writer = _StreamlitBuffer(lambda text: placeholder.code(text, language="shell"))
        with redirect_stdout(writer), redirect_stderr(writer):
            yield


def _sb_label(text):
    st.sidebar.markdown(f'<span class="sb-label">{text}</span>', unsafe_allow_html=True)


@st.cache_data(show_spinner=False, ttl=3600)
def gutenberg_search(query):
    from core.data import search_books
    return search_books(query=query, limit=5)


@st.cache_resource(show_spinner=False)
def figure(name, book_id, version=None):
    from pipeline import charts as charts_pipeline
    builders = {
        "kmeans": charts_pipeline.kmeans_fig,
        "silhouette": charts_pipeline.silhouette_fig,
        "arc": charts_pipeline.arc_fig,
        "galaxy": charts_pipeline.galaxy_fig,
    }
    return builders[name](Book(book_id))


def cmd_cell(cmd, key, done=False):
    c_btn, c_cmd = st.columns([1, 16])
    run = False
    with c_btn:
        if done:
            st.markdown('<div class="cell-ok">✓</div>', unsafe_allow_html=True)
        else:
            run = st.button("▶", key=key)
    with c_cmd:
        state = "done" if done else "todo"
        st.markdown(
            f'<div class="cell-cmd {state}"><code>{cmd}</code></div>',
            unsafe_allow_html=True,
        )
    return run


def run_cell(book, task, version, compute, flag):
    result = cache.load(book.id, task, version)
    run = cmd_cell(
        f"python bookworm.py --{flag} {book.id}",
        key=f"rc-{task}-{book.id}",
        done=result is not None,
    )
    if result is not None:
        return result
    if not run:
        return None
    try:
        with st_terminal(f"Exécution : {task}"):
            return cache.cached(book.id, task, lambda: compute(book), version=version)
    except (OSError, LookupError) as error:
        st.error(str(error))
        return None


def _select_book(bid):
    st.session_state["cid"] = str(bid)


def _sidebar():
    _sb_label("Livre")
    name_q = st.sidebar.text_input(
        "Titre ou auteur", placeholder="Titre ou auteur…",
        label_visibility="collapsed",
    ).strip()
    id_q = st.sidebar.text_input(
        "ID Gutenberg", key="cid", placeholder="ID Gutenberg",
        label_visibility="collapsed",
    ).strip()

    book_id = None
    if id_q.isdigit():
        book_id = int(id_q)
    elif name_q:
        results = search_catalog(name_q)
        if not results:
            try:
                with st.sidebar, st.spinner("Recherche…"):
                    results = gutenberg_search(name_q)
            except (OSError, LookupError, ValueError):
                st.sidebar.error("Gutenberg injoignable.")
                results = []
        if not results:
            st.sidebar.caption("Aucun résultat.")
        for r in results:
            st.sidebar.button(
                f"{r['title']} — {r['authors']}",
                key=f"gx-{r['id']}",
                on_click=_select_book, args=(r["id"],),
                use_container_width=True,
            )
    if book_id is None:
        param = st.query_params.get("book", "")
        book_id = int(param) if param.isdigit() else None
        
    if book_id is not None:
        st.query_params["book"] = str(book_id)
    else:
        st.query_params.pop("book", None)

    st.sidebar.divider()
    _sb_label("Analyse")
    selected_analysis = st.sidebar.multiselect(
        "Sélectionner l'analyse souhaitée :",
        [
            "Diversité lexicale",
            "Thèmes",
            "Entités",
            "Résumé",
            "Livres similaires",
            "Arc narratif",
        ],
        label_visibility="collapsed"
    )

    if st.sidebar.button("Analyser", use_container_width=True, type="primary"):
        st.session_state.active_analysis = selected_analysis
        
    st.sidebar.divider()
    _sb_label("Assistant")
    query = st.sidebar.chat_input("Question ou extrait à attribuer…")

    return book_id, query


def book_metadata(book_id):
    # Not cached with st.cache_data on purpose: a transient Gutendex outage would
    # otherwise pin a None for the whole session, so the title would stay missing
    # even after the text is downloaded and its header becomes readable. info()
    # is already cached on disk / via lru_cache, so re-calling it is cheap.
    try:
        return info(str(book_id))
    except SystemExit:
        return None


def _card_export(book):
    card = cache.load(book.id, "card", None)
    if card is None and st.button("Générer la fiche JSON", use_container_width=True):
        try:
            with st_terminal("Exécution : card"):
                card = cache.cached(book.id, "card", lambda: card_pipeline.card(book))
        except (OSError, LookupError) as error:
            st.error(str(error))
            return
    if card is not None:
        st.download_button(
            "Fiche (JSON)",
            json.dumps(card, ensure_ascii=False, indent=2),
            file_name=f"card_{book.id}.json",
            mime="application/json",
            use_container_width=True,
        )


def _book_header(book):
    record = book_metadata(book.id)
    cover, meta, actions = st.columns([1, 4, 1])
    with cover:
        st.image(COVER_URL.format(book_id=book.id), width=120)
    with meta:
        if record and record.get("title"):
            st.title(record["title"])
            category = COLLECTION.get(book.id) or record.get("bookshelves")
            parts = [record.get("authors"), category]
            st.caption("  ·  ".join(p for p in parts if p) or "Hors collection de référence.")
        else:
            st.title(f"Gutenberg #{book.id}")
            st.caption(
                "Métadonnées indisponibles — lancez une analyse pour télécharger "
                "le livre, ou Gutendex est momentanément injoignable."
            )
    with actions:
        _card_export(book)


def render_section(title, task, version, compute, flag):
    def decorator(func):
        def wrapper(book):
            st.header(title, divider="grey")
            result = run_cell(book, task, version, compute, flag)
            if result is not None:
                func(book, result)
        return wrapper
    return decorator


@render_section("Diversité lexicale", "lexdiv", None, lexdiv_pipeline.lexdiv, "lexdiv")
def lexdiv_section(book, result):
    c = st.columns(3)
    c[0].metric("Tokens", f"{result['tok']:,}")
    c[1].metric("Types", f"{result['typ']:,}")
    c[2].metric("Hapax", f"{result['hap']:,}")
    c2 = st.columns(3)
    c2[0].metric("TTR", result["ttr"])
    c2[1].metric("Longueur moy.", result["mwl"])
    c2[2].metric("Fréquence moy.", result["mwf"])
    st.subheader("Métriques avancées")
    plus = run_cell(book, "lexdiv-plus", None, lexdiv_pipeline.lexdiv_plus, "lexdiv-plus")
    if plus is not None:
        st.table({k.upper(): [v] for k, v in plus.items()})


@render_section("Thèmes", "topics", topics_pipeline.CACHE_VERSION, topics_pipeline.topics, "topics")
def topics_section(book, result):
    st.dataframe(
            {"Section": list(result), "Top 10 mots": [", ".join(w) for w in result.values()]},
            use_container_width=True,
            hide_index=True,
        )
    st.subheader("Comparatif NMF / LSA / LDA")
    comparison = run_cell(
        book, "compare", compare_pipeline.CACHE_VERSION, compare_pipeline.compare, "compare"
    )
    if comparison is not None and "algorithms" in comparison:
        rows = comparison["algorithms"]
        st.dataframe(
            {
                "Algorithme": [n.upper() for n in rows],
                "Cohérence UMass": [rows[n]["coherence_umass"] for n in rows],
                "Diversité": [rows[n]["diversity"] for n in rows],
                "Temps (s)": [rows[n]["seconds"] for n in rows],
            },
            use_container_width=True,
            hide_index=True,
        )


@render_section("Entités", "entities", entities_pipeline.CACHE_VERSION, entities_pipeline.entities, "entities")
def entities_section(book, result):
    chars, locs = st.columns(2)
    with chars:
        st.subheader("Personnages")
        for name in result["characters"]:
            st.markdown(f"- {name}")
    with locs:
        st.subheader("Lieux")
        for name in result["locations"]:
            st.markdown(f"- {name}")


@render_section("Résumé", "summarize", summarize_pipeline.CACHE_VERSION, summarize_pipeline.summarize, "summarize")
def summary_section(book, result):
    st.write(result)
    st.subheader("Visualisations K-Means")
    for name in ("kmeans", "silhouette"):
        fig = figure(name, book.id)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
    st.subheader("Évaluation ROUGE")
    if cmd_cell(f"python bookworm.py --eval-summary {book.id}", key=f"rouge-{book.id}"):
        try:
            with st_terminal("Calcul…"):
                scores = cache.cached(book.id, "eval_summary", lambda: eval_pipeline.eval_summary(book), version="v2")
        except LookupError:
            st.info("Aucun résumé de référence (Wikipédia) disponible pour évaluer ce livre.")
            scores = None
        except OSError as e:
            st.error(str(e))
            scores = None
            
        if scores is not None:
            st.caption(f"Référence : {scores['reference_words']} mots")
            for method, metrics in scores["methods"].items():
                st.markdown(f"**{method}**")
                st.dataframe(
                    {
                        "Métrique": list(metrics),
                        "Précision": [metrics[m]["p"] for m in metrics],
                        "Rappel": [metrics[m]["r"] for m in metrics],
                        "F-mesure": [metrics[m]["f"] for m in metrics],
                    },
                    use_container_width=True,
                    hide_index=True,
                )
    if BERT_READY:
        st.subheader("Variante DistilBERT")
        bert_sum = run_cell(
            book, "summarize-bert", summarize_pipeline.CACHE_VERSION,
            summarize_pipeline.summarize_bert, "summarize-bert",
        )
        if bert_sum is not None:
            st.write(bert_sum["summary"])


@render_section("Livres similaires", "similar", similar_pipeline.CACHE_VERSION, similar_pipeline.similar, "similar")
def similar_section(book, result):
    for rank, title in enumerate(result, start=1):
        st.markdown(f"{rank}. {title}")
    st.subheader("Galaxie")
    fig = figure("galaxy", book.id, similar_pipeline.cache_version())
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)
    if BERT_READY:
        st.subheader("Variante DistilBERT")
        bert_sim = run_cell(
            book, "similar-bert", similar_pipeline.CACHE_VERSION,
            similar_pipeline.similar_bert, "similar-bert",
        )
        if bert_sim is not None:
            for rank, title in enumerate(bert_sim["similar"], start=1):
                st.markdown(f"{rank}. {title}")


@render_section("Arc narratif", "arc", arc_pipeline.CACHE_VERSION, arc_pipeline.arc, "arc")
def arc_section(book, result):
    fig = figure("arc", book.id)
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("Scores par section")
    sections = sorted(result, key=int)
    st.dataframe(
        {"Section": sections, "Sentiment moyen": [result[k] for k in sections]},
        use_container_width=True,
        hide_index=True,
    )


def _render_assistant(book, query):
    if not query:
        return
    import assistant
    title = get_book_title(book.id)
    
    with st.sidebar:
        with st.chat_message("user"):
            st.write(query)
            
        with st.chat_message("assistant"):
            with st.spinner("L'agent réfléchit…"):
                log_placeholder = st.empty()
                md_placeholder = st.empty()
                stdout_writer = _StreamlitBuffer(md_placeholder.markdown)
                stderr_writer = _StreamlitBuffer(
                    lambda text: log_placeholder.code(text, language="shell")
                )
                
                try:
                    with redirect_stdout(stdout_writer), redirect_stderr(stderr_writer):
                        assistant.agent_loop(book, title, query)
                except SystemExit:
                    st.error(stderr_writer.getvalue() or "Ollama est injoignable. Lancez `ollama serve`.")
                    return


def main():
    st.set_page_config(page_title=APP_NAME, page_icon=str(APP_ICON), layout="wide")
    _inject_css()

    book_id, query = _sidebar()
    if book_id is None:
        return
        
    book = Book(book_id)

    analysis_map = {
        "Diversité lexicale": lexdiv_section,
        "Thèmes": topics_section,
        "Entités": entities_section,
        "Résumé": summary_section,
        "Livres similaires": similar_section,
        "Arc narratif": arc_section
    }

    has_analysis = "active_analysis" in st.session_state and st.session_state.active_analysis
    _book_header(book)
    _render_assistant(book, query)
    
    if has_analysis:
        st.divider()
        for analysis in st.session_state.active_analysis:
            func = analysis_map.get(analysis)
            if func:
                func(book)

if __name__ == "__main__":
    main()
