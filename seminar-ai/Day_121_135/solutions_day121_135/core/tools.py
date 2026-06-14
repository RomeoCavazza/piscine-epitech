#!/usr/bin/env python3

import csv
import json
import sys
from argparse import ArgumentParser
from functools import lru_cache
from pathlib import Path

import requests

from core.nlp import cleaner, normalize, postag, tokenizer

BOOTSTRAP_DIR = Path(__file__).resolve().parent.parent
COLLECTION_PATH = BOOTSTRAP_DIR / "data" / "input" / "collection.csv"
CATALOG_PATH = BOOTSTRAP_DIR / "data" / "input" / "pg_catalog.csv"

GUTENDEX_URL = "https://gutendex.com/books/{book_id}"


class EpitechArgumentParser(ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write(f"{self.prog}: error: {message}\n")
        sys.exit(84)


def get_args():
    parser = EpitechArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--info", type=int)
    group.add_argument("--download", type=int)
    group.add_argument("--clean", type=str)
    group.add_argument("--tokenize", type=str)
    group.add_argument("--postag", type=str)
    group.add_argument("--normalize", type=str)
    parser.add_argument("--lower", action="store_true")
    parser.add_argument("--sent", action="store_true")
    parser.add_argument("--stop", action="store_true")
    parser.add_argument("--punct", action="store_true")
    parser.add_argument("--stem", action="store_true")
    return parser.parse_args()


@lru_cache(maxsize=1)
def _catalog_records():
    records = {}
    for path in (COLLECTION_PATH, CATALOG_PATH):
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                records.setdefault(row["Text#"], {
                    "id": row["Text#"],
                    "title": row["Title"],
                    "language": row.get("Language") or "en",
                    "authors": row["Authors"],
                    "bookshelves": row["Bookshelves"],
                })
    return records


def _read_catalog(book_id):
    return _catalog_records().get(str(book_id))


def search_catalog(query, limit=5):
    terms = query.lower().split()
    if not terms:
        return []
    title_hits, author_hits = [], []
    for record in _catalog_records().values():
        title = record["title"].lower()
        if all(term in title for term in terms):
            title_hits.append(record)
        elif all(term in f"{title} {record['authors'].lower()}" for term in terms):
            author_hits.append(record)
        if len(title_hits) >= limit:
            return title_hits[:limit]
    return (title_hits + author_hits)[:limit]


def _info_cache_path(book_id):
    from core import cache
    return cache.CORPUS_DIR / str(book_id) / "info.json"


def _read_cached_info(book_id):
    path = _info_cache_path(book_id)
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _persist_info(record):
    path = _info_cache_path(record["id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)


def _fetch_gutendex(book_id):
    try:
        response = requests.get(GUTENDEX_URL.format(book_id=book_id), timeout=10)
    except requests.RequestException:
        return None
    if response.status_code != 200:
        return None
    data = response.json()
    return {
        "id": str(data.get("id", book_id)),
        "title": data.get("title", ""),
        "language": (data.get("languages") or ["en"])[0],
        "authors": ", ".join(author["name"] for author in data.get("authors", [])),
        "bookshelves": ", ".join(data.get("bookshelves", [])),
    }


def _read_text_header(book_id):
    """Offline fallback: parse Title/Author/Language from a downloaded pg<id>.txt.

    Every Project Gutenberg text carries a standard header, so a book that has
    already been downloaded can be identified without depending on Gutendex
    (which is slow/flaky enough to otherwise surface as "unknown id").
    """
    from core import data

    path = data.text_path(book_id)
    if not path.exists():
        return None

    fields = {}
    for line in path.read_text(encoding="utf-8", errors="replace")[:2000].splitlines():
        for key in ("Title", "Author", "Language"):
            if line.startswith(f"{key}:") and key not in fields:
                fields[key] = line[len(key) + 1:].strip()

    title = fields.get("Title")
    if not title:
        return None

    lang = fields.get("Language", "English")
    return {
        "id": str(book_id),
        "title": title,
        "language": "en" if lang.lower().startswith("english") else lang[:2].lower(),
        "authors": fields.get("Author", ""),
        "bookshelves": "",
    }


def info(book_id):
    record = _read_catalog(book_id) or _read_cached_info(book_id)
    if record is not None:
        return record
    # Prefer the offline text header (instant, reliable) over flaky Gutendex.
    record = _read_text_header(book_id) or _fetch_gutendex(book_id)
    if record is not None:
        _persist_info(record)
        return record
    sys.stderr.write(
        f"bookworm: error: metadata for book {book_id} not found "
        "(unknown id, or offline and not cached)\n"
    )
    sys.exit(84)


def book_title(book_id):
    return info(str(book_id)).get("title", f"Book #{book_id}")


def language(book_id):
    record = _read_catalog(book_id) or _read_cached_info(book_id) or {}
    return (record.get("language") or "en").split("-")[0].lower()


def main():
    args = get_args()
    if args.info is not None:
        print(json.dumps(info(args.info), ensure_ascii=False, indent=2))
    elif args.download is not None:
        from core import data
        data.download(args.download)
    elif args.clean is not None:
        print(cleaner(args.clean, lower=args.lower))
    elif args.tokenize is not None:
        print(tokenizer(args.tokenize, sent=args.sent, stop=args.stop, punct=args.punct))
    elif args.postag is not None:
        print(postag(args.postag))
    elif args.normalize is not None:
        print(normalize(args.normalize, stem=args.stem))


if __name__ == "__main__":
    main()
