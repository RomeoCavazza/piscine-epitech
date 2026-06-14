#!/usr/bin/env python3

import re
from pathlib import Path

from core import cache
from core.tools import book_title, info, language
from pipeline import summarize
import requests

CACHE_VERSION = 1

ROOT = Path(__file__).resolve().parent.parent
REFERENCE_DIR = ROOT / "data" / "input" / "references"
REFERENCE_CACHE_DIR = cache.CORPUS_DIR / "references"
ROUGE_METRICS = ("rouge1", "rouge2", "rougeL")
WIKIPEDIA_USER_AGENT = "Bookworm/1.0 (https://github.com/EpitechMscProPromo2028/T-AIA-600-PAR_14)"
TITLE_SUFFIXES = ("", " (novel)", " (book)", " (short story)", " (play)", " (poem)")


def _dedupe(items):
    seen = set()
    result = []
    for item in items:
        item = " ".join(str(item).split())
        key = item.casefold()
        if item and key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _title_variants(title):
    title = " ".join((title or "").split())
    title = re.sub(r"^The Project Gutenberg eBook of\s+", "", title, flags=re.I)
    variants = [title]

    for pattern in (
        r"\s*;\s*or,?\s+.+$",
        r"\s*:\s*or,?\s+.+$",
        r"\s*;\s+.+$",
        r"\s+--\s+.+$",
    ):
        stripped = re.sub(pattern, "", title, flags=re.I).strip()
        if stripped and stripped != title:
            variants.append(stripped)

    if ":" in title:
        variants.append(title.split(":", 1)[0].strip())
    return _dedupe(variants)[:5]


def _wikipedia_titles(title):
    return _dedupe(
        f"{variant}{suffix}"
        for variant in _title_variants(title)
        for suffix in TITLE_SUFFIXES
    )


def _usable_extract(extract, page=None):
    if not extract:
        return False
    if page and "disambiguation" in page.get("pageprops", {}):
        return False
    lowered = extract.lower()
    return "may refer to" not in lowered and "disambiguation" not in lowered


def _metadata(book_id):
    try:
        return info(str(book_id))
    except SystemExit:
        return {}


def _wikipedia_languages(book_id):
    try:
        primary = (language(book_id) or "en").split("-")[0].lower()
    except Exception:
        primary = "en"
    return _dedupe([primary, "en"])


def _wiki_json(lang, params, headers):
    url = f"https://{lang}.wikipedia.org/w/api.php"
    try:
        response = requests.get(url, params=params, headers=headers, timeout=8)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return {}


def _chunks(items, size):
    for index in range(0, len(items), size):
        yield items[index:index + size]


def _extract_from_pages(payload):
    query = payload.get("query", {})
    pages = query.get("pages", {})
    pageids = [str(pid) for pid in query.get("pageids", pages.keys())]
    for pid in pageids:
        page = pages.get(pid, {})
        if pid == "-1":
            continue
        extract = page.get("extract")
        if _usable_extract(extract, page):
            return extract
    return None


def _fetch_extract_for_titles(lang, titles, headers):
    for chunk in _chunks(_dedupe(titles), 20):
        payload = _wiki_json(
            lang,
            {
                "action": "query",
                "prop": "extracts|pageprops",
                "ppprop": "disambiguation",
                "exintro": "1",
                "explaintext": "1",
                "titles": "|".join(chunk),
                "format": "json",
                "redirects": "1",
                "indexpageids": "1",
            },
            headers,
        )
        extract = _extract_from_pages(payload)
        if extract:
            return extract
    return None


def _author_terms(authors):
    authors = (authors or "").split(";")[0]
    authors = re.sub(r"\([^)]*\)", "", authors)
    authors = re.sub(r"\b\d{3,4}\b.*$", "", authors).strip(" ,")
    if not authors:
        return []

    parts = [part.strip() for part in authors.split(",") if part.strip()]
    surname = parts[0] if parts else ""
    full_name = " ".join(parts[1:] + parts[:1]) if len(parts) > 1 else authors
    return _dedupe([full_name, surname])


def _search_queries(title, authors):
    queries = []
    author_terms = _author_terms(authors)
    for variant in _title_variants(title):
        queries.append(f'"{variant}"')
        for author in author_terms[:2]:
            queries.append(f'"{variant}" {author}')
            queries.append(f"{variant} {author}")
    return _dedupe(queries)[:8]


def _search_wikipedia_titles(lang, title, authors, headers):
    titles = []
    for query in _search_queries(title, authors):
        payload = _wiki_json(
            lang,
            {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": "5",
                "format": "json",
            },
            headers,
        )
        for hit in payload.get("query", {}).get("search", []):
            if hit.get("title"):
                titles.append(hit["title"])
        if len(titles) >= 10:
            break
    return _dedupe(titles)


def _fetch_wikipedia_summary(book_id):
    record = _metadata(book_id)
    title = record.get("title")
    if not title:
        try:
            title = book_title(book_id)
        except SystemExit:
            title = None
    if not title:
        return None

    headers = {"User-Agent": WIKIPEDIA_USER_AGENT}
    authors = record.get("authors", "")
    direct_titles = _wikipedia_titles(title)

    for lang in _wikipedia_languages(book_id):
        extract = _fetch_extract_for_titles(lang, direct_titles, headers)
        if extract:
            return extract

        search_titles = _search_wikipedia_titles(lang, title, authors, headers)
        extract = _fetch_extract_for_titles(lang, search_titles, headers)
        if extract:
            return extract
    return None


def _reference_text(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def _reference(book_id):
    for path in (REFERENCE_DIR / f"{book_id}.txt", REFERENCE_CACHE_DIR / f"{book_id}.txt"):
        if path.exists():
            return _reference_text(path)

    summary = _fetch_wikipedia_summary(book_id)
    if not summary:
        raise LookupError(f"no reference summary for book {book_id}")

    REFERENCE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = REFERENCE_CACHE_DIR / f"{book_id}.txt"
    path.write_text(summary, encoding="utf-8")
    return _reference_text(path)


def _score_summary(scorer, reference, summary):
    scores = scorer.score(reference, summary)
    return {
        metric: {
            "p": round(scores[metric].precision, 4),
            "r": round(scores[metric].recall, 4),
            "f": round(scores[metric].fmeasure, 4),
        }
        for metric in ROUGE_METRICS
    }


def eval_summary(book):
    from rouge_score import rouge_scorer

    reference = _reference(book.id)
    generated = cache.cached(
        book.id,
        "summarize",
        lambda: summarize.summarize(book),
        version=getattr(summarize, "CACHE_VERSION", None),
    )

    scorer = rouge_scorer.RougeScorer(ROUGE_METRICS, use_stemmer=True)
    methods = {"kmeans": _score_summary(scorer, reference, generated)}

    bert_cached = cache.load(
        book.id,
        "summarize-bert",
        version=getattr(summarize, "CACHE_VERSION", None),
    )
    if isinstance(bert_cached, dict):
        bert_summary = bert_cached.get("summary")
    else:
        bert_summary = bert_cached
    if isinstance(bert_summary, str) and bert_summary.strip():
        methods["distilbert"] = _score_summary(scorer, reference, bert_summary)

    return {
        "reference": "wikipedia",
        "reference_words": len(reference.split()),
        "methods": methods,
    }
