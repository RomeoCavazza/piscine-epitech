#!/usr/bin/env python3

import json
from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parent.parent / "data" / "output" / "cache"


def _resolve_version(version):
    return version() if callable(version) else version


def _path(book_id, task, version=None):
    version = _resolve_version(version)
    suffix = f"__v{version}" if version is not None else ""
    return CORPUS_DIR / str(book_id) / f"{task}{suffix}.json"


def load(book_id, task, version=None):
    path = _path(book_id, task, version)
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def store(book_id, task, result, version=None):
    path = _path(book_id, task, version)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    return result


def cached(book_id, task, compute, version=None):
    hit = load(book_id, task, version)
    if hit is not None:
        return hit
    return store(book_id, task, compute(), version)
