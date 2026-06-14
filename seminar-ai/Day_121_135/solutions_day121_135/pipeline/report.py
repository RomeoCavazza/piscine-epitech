#!/usr/bin/env python3

import html
from pathlib import Path

from core import cache
from pipeline import card as card_pipeline
from pipeline import compare as compare_pipeline
from pipeline import charts as charts_module

_LEXDIV_EMPTY = {"tok": 0, "typ": 0, "hap": 0, "ttr": 0.0, "mwl": 0.0, "mwf": 0.0}


def _load_or_default(book_id, task, default, version=None):
    return cache.load(book_id, task, version=version) or default


def _img(encoded, fmt="png"):
    if not encoded:
        return ""
    return f'<img src="data:image/{fmt};base64,{encoded}" alt="">'


def _items(values):
    return "".join(f"<li>{html.escape(str(value))}</li>" for value in values)


def _topics_rows(topics):
    rows = []
    for section, words in topics.items():
        joined = html.escape(", ".join(words))
        rows.append(f"<tr><td>{html.escape(str(section))}</td><td>{joined}</td></tr>")
    return "".join(rows)


def _compare_section(comparison, image):
    if "algorithms" not in comparison:
        note = html.escape(comparison.get("note", "comparison unavailable"))
        return f"<p class='muted'>{note}</p>"

    rows = []
    for name, result in comparison["algorithms"].items():
        rows.append(
            f"<tr><td>{name.upper()}</td>"
            f"<td>{result['coherence_umass']}</td>"
            f"<td>{result['diversity']}</td>"
            f"<td>{result['seconds']}</td></tr>"
        )
    details = []
    for name, result in comparison["algorithms"].items():
        topics_list = "".join(
            f"<li><strong>#{number}</strong> {html.escape(', '.join(words))}</li>"
            for number, words in result["topics"].items()
        )
        details.append(
            f"<details><summary>{name.upper()} topics</summary><ul>{topics_list}</ul></details>"
        )

    best = comparison.get("best")
    verdict = (
        f"<p><strong>Verdict :</strong> {best.upper()} "
        f"({html.escape(comparison['criteria'])})</p>" if best else ""
    )
    return (
        f"{_img(image)}"
        f"<table><tr><th>Algorithm</th><th>UMass coherence</th>"
        f"<th>Diversity</th><th>Fit time (s)</th></tr>{''.join(rows)}</table>"
        f"{verdict}{''.join(details)}"
    )


def _render(book, data, comparison, images, charts):
    info = book.info
    title = html.escape(info.get("title", f"Book #{book.id}"))
    authors = html.escape(str(info.get("authors", "")))
    bookshelves = html.escape(str(info.get("bookshelves", "")))
    lexdiv = data["lexdiv"]
    lexdiv_plus = data.get("lexdiv_plus", {})

    cover_block = _img(images["cover"], fmt="jpeg")
    arc_block = (
        f"<section><h2>Narrative arc through sentiment</h2>{charts['arc']}</section>"
        if charts["arc"] else ""
    )
    galaxy_block = (
        f"<section><h2>Catalog galaxy</h2>{charts['galaxy']}</section>"
        if charts["galaxy"] else ""
    )

    template_path = Path(__file__).parent / "report_template.html"
    template = template_path.read_text(encoding="utf-8")

    return template.format(
        title=title,
        cover_block=cover_block,
        authors=authors,
        bookshelves=bookshelves,
        book_id=book.id,
        lexdiv_img=_img(images["lexdiv"]),
        tok=f"{lexdiv['tok']:,}",
        typ=f"{lexdiv['typ']:,}",
        hap=f"{lexdiv['hap']:,}",
        ttr=lexdiv["ttr"],
        mwl=lexdiv["mwl"],
        mwf=lexdiv["mwf"],
        msttr=lexdiv_plus.get("msttr", ""),
        mattr=lexdiv_plus.get("mattr", ""),
        mtld=lexdiv_plus.get("mtld", ""),
        guiraud=lexdiv_plus.get("guiraud", ""),
        herdan_c=lexdiv_plus.get("herdan_c", ""),
        yule_k=lexdiv_plus.get("yule_k", ""),
        maas_a2=lexdiv_plus.get("maas_a2", ""),
        summary=html.escape(data["summary"]),
        kmeans_chart=charts["kmeans"] or "",
        silhouette_chart=charts["silhouette"] or "",
        arc_block=arc_block,
        characters=_items(data["entities"]["characters"]),
        locations=_items(data["entities"]["locations"]),
        topics_count=len(data["topics"]),
        topics_rows=_topics_rows(data["topics"]),
        similar=_items(data["similar"]),
        galaxy_block=galaxy_block,
        compare_section=_compare_section(comparison, images["compare"]),
    )


def _gather_data(book, full):
    if full:
        from pipeline import lexdiv as lp
        data = card_pipeline.card(book)
        comparison = cache.cached(
            book.id, "compare",
            lambda: compare_pipeline.compare(book),
            version=compare_pipeline.CACHE_VERSION,
        )
        data["lexdiv_plus"] = cache.cached(book.id, "lexdiv-plus", lambda: lp.lexdiv_plus(book))
        return data, comparison

    from pipeline import compare as cp, entities as ep, similar as sp, summarize as sump, topics as tp
    book_info = book.info
    data = {
        "info": {
            "id": book_info["id"],
            "authors": book_info["authors"],
            "bookshelves": book_info["bookshelves"],
        },
        "lexdiv": _load_or_default(book.id, "lexdiv", _LEXDIV_EMPTY),
        "topics": _load_or_default(book.id, "topics", {}, version=tp.CACHE_VERSION),
        "entities": _load_or_default(
            book.id,
            "entities",
            {"characters": [], "locations": []},
            version=getattr(ep, "CACHE_VERSION", None),
        ),
        "summary": _load_or_default(
            book.id, "summarize", "", version=getattr(sump, "CACHE_VERSION", None)
        ),
        "similar": _load_or_default(
            book.id, "similar", [], version=getattr(sp, "CACHE_VERSION", None)
        ),
        "lexdiv_plus": _load_or_default(book.id, "lexdiv-plus", {}),
    }
    comparison = _load_or_default(
        book.id, "compare", {"note": "not computed"}, version=cp.CACHE_VERSION
    )
    return data, comparison


def report(book, full=True):
    data, comparison = _gather_data(book, full)

    out_dir = cache.CORPUS_DIR / str(book.id) / "report"
    out_dir.mkdir(parents=True, exist_ok=True)

    images = {
        "lexdiv": (
            charts_module.lexdiv_chart(data["lexdiv"], out_dir / "lexdiv.png")
            if data["lexdiv"]["tok"] else None
        ),
        "compare": (
            charts_module.compare_chart(comparison, out_dir / "compare.png")
            if "algorithms" in comparison else None
        ),
        "cover": charts_module.fetch_cover(book.id, out_dir / "cover.jpg"),
    }

    if full:
        figures = {
            "kmeans": charts_module.kmeans_fig(book),
            "silhouette": charts_module.silhouette_fig(book),
            "arc": charts_module.arc_fig(book),
            "galaxy": charts_module.galaxy_fig(book),
        }
    else:
        figures = {"kmeans": None, "silhouette": None, "arc": None, "galaxy": None}

    charts_module.write_plotly_images(figures, out_dir)
    charts = charts_module.charts_html(figures)

    html_path = out_dir / "card.html"
    html_path.write_text(_render(book, data, comparison, images, charts), encoding="utf-8")
    return str(html_path)
