#!/usr/bin/env python3

import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin

import requests

GUTENBERG_URL = "https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
OPDS_SEARCH_URL = "https://www.gutenberg.org/ebooks/search.opds/"
SEARCH_USER_AGENT = "bookworm-app"
DEFAULT_SEARCH_LIMIT = None
OPDS_NS = {"a": "http://www.w3.org/2005/Atom"}

TEXTS_DIR = Path(
    os.getenv("BOOKWORM_TEXTS_DIR")
    or Path(__file__).resolve().parent.parent / "data" / "input" / "texts"
)


def text_path(book_id):
    return TEXTS_DIR / f"pg{book_id}.txt"


def download(book_id):
    response = requests.get(GUTENBERG_URL.format(book_id=book_id), timeout=30)
    if response.status_code != 200:
        sys.stderr.write(f"bookworm: error: book {book_id} not found\n")
        sys.exit(84)
    path = text_path(book_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(response.text, encoding="utf-8")
    return path


def load_text(book_id):
    path = text_path(book_id)
    if not path.exists():
        download(book_id)
    return path.read_text(encoding="utf-8")


def _reached_limit(results, limit):
    return limit is not None and len(results) >= limit


def _remaining_limit(limit, current_count):
    return None if limit is None else max(limit - current_count, 0)


def _parse_opds_entries(root, limit=DEFAULT_SEARCH_LIMIT):
    results = []
    if _reached_limit(results, limit):
        return results

    for entry in root.findall("a:entry", OPDS_NS):
        entry_id = entry.find("a:id", OPDS_NS)
        entry_id_text = (entry_id.text or "") if entry_id is not None else ""
        match = re.search(r"/ebooks/(\d+)", entry_id_text)
        if not match:
            continue

        title = entry.find("a:title", OPDS_NS)
        authors = [
            (author.text or "").strip()
            for author in entry.findall("a:author/a:name", OPDS_NS)
            if author.text and author.text.strip()
        ]
        if authors:
            author_text = ", ".join(authors)
        else:
            content_node = entry.find("a:content", OPDS_NS)
            author_text = (
                (content_node.text or "").strip()
                if content_node is not None
                else "Auteur inconnu"
            )

        results.append({
            "id": int(match.group(1)),
            "title": (title.text or "").strip() if title is not None else "",
            "authors": author_text,
        })
        if _reached_limit(results, limit):
            break
    return results


def _parse_opds_feed(content, limit=DEFAULT_SEARCH_LIMIT):
    return _parse_opds_entries(ET.fromstring(content), limit=limit)


def _opds_next_url(root):
    for link in root.findall("a:link", OPDS_NS):
        if link.get("rel") == "next" and link.get("href"):
            return urljoin(OPDS_SEARCH_URL, link.get("href"))
    return None


def _terms(value):
    return value.lower().split() if value else []


def _search_local_catalog(query=None, author=None, topic=None, limit=DEFAULT_SEARCH_LIMIT):
    from core.tools import _catalog_records

    query_terms = _terms(query)
    author_terms = _terms(author)
    topic_terms = _terms(topic)
    matches = []
    
    for record in _catalog_records().values():
        title_text = record.get("title", "").lower()
        author_text = record.get("authors", "").lower()
        topic_text = f"{record.get('bookshelves', '')} {record.get('title', '')}".lower()
        search_text = f"{title_text} {author_text} {record.get('bookshelves', '').lower()}"
        
        if query_terms and not all(term in search_text for term in query_terms):
            continue
        if author_terms and not all(term in author_text for term in author_terms):
            continue
        if topic_terms and not all(term in topic_text for term in topic_terms):
            continue
            
        matches.append({
            "id": int(record["id"]),
            "title": record.get("title", ""),
            "authors": record.get("authors", ""),
        })
        if _reached_limit(matches, limit):
            break
    return matches


def _search_query(query=None, author=None, topic=None):
    parts = [query, author, topic]
    return " ".join(part.strip() for part in parts if part and part.strip())


def _search_opds(query, limit=DEFAULT_SEARCH_LIMIT):
    books = []
    seen_ids = set()
    seen_pages = set()
    url = OPDS_SEARCH_URL
    params = {"query": query}

    while url and not _reached_limit(books, limit):
        if url in seen_pages:
            break
        seen_pages.add(url)

        response = requests.get(
            url,
            params=params,
            timeout=15,
            headers={"User-Agent": SEARCH_USER_AGENT},
        )
        response.raise_for_status()
        root = ET.fromstring(response.content)

        remaining = _remaining_limit(limit, len(books))
        for book in _parse_opds_entries(root, limit=remaining):
            if book["id"] in seen_ids:
                continue
            books.append(book)
            seen_ids.add(book["id"])
            if _reached_limit(books, limit):
                break

        url = _opds_next_url(root)
        params = None
    return books


def search_books(query=None, author=None, topic=None, limit=DEFAULT_SEARCH_LIMIT):
    search_query = _search_query(query=query, author=author, topic=topic)
    if not search_query:
        return []

    try:
        books = _search_opds(search_query, limit=limit)
    except (requests.RequestException, ET.ParseError) as error:
        local = _search_local_catalog(
            query=query,
            author=author,
            topic=topic,
            limit=limit,
        )
        if local:
            sys.stderr.write(
                f"bookworm: warning: Gutenberg OPDS unavailable, using local catalog ({error})\n"
            )
            return local
        raise LookupError(f"Gutenberg OPDS search failed: {error}") from error

    if books:
        return books[:limit]
    return _search_local_catalog(
        query=query,
        author=author,
        topic=topic,
        limit=limit,
    )


def download_many(ids):
    count = len(ids)
    if count == 0:
        return
    for index, book_id in enumerate(ids):
        sys.stderr.write(f"\rDownloading {index + 1}/{count} (book {book_id})...")
        sys.stderr.flush()
        try:
            if not text_path(book_id).exists():
                download(book_id)
        except SystemExit:
            sys.stderr.write(f"\nbookworm: warning: failed to download book {book_id}\n")
        except Exception:
            sys.stderr.write(f"\nbookworm: warning: failed to download book {book_id}\n")
    sys.stderr.write("\n")


def search_opds(query, limit=5):
    return _search_opds(query, limit=limit)
