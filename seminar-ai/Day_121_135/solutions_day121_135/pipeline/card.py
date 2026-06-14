#!/usr/bin/env python3

from core import cache
from pipeline import entities, lexdiv, similar, summarize, topics


def card(book):
    book_id = book.id
    info = book.info
    return {
        "info": {
            "id": info["id"],
            "authors": info["authors"],
            "bookshelves": info["bookshelves"],
        },
        "lexdiv": cache.cached(book_id, "lexdiv", lambda: lexdiv.lexdiv(book)),
        "topics": cache.cached(
            book_id,
            "topics",
            lambda: topics.topics(book),
            version=topics.CACHE_VERSION,
        ),
        "entities": cache.cached(
            book_id, "entities", lambda: entities.entities(book),
            version=getattr(entities, "CACHE_VERSION", None),
        ),
        "summary": cache.cached(
            book_id, "summarize", lambda: summarize.summarize(book),
            version=getattr(summarize, "CACHE_VERSION", None),
        ),
        "similar": cache.cached(
            book_id, "similar", lambda: similar.similar(book),
            version=getattr(similar, "CACHE_VERSION", None),
        ),
    }
