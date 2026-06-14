#!/usr/bin/env python3

import json
import os
import sys
from importlib import import_module
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("BOOKWORM_DISABLE_FULL_INDEX", "1")

from core.book import Book  # noqa: E402

BOOK_ID = 11
GOLDEN_DIR = Path(__file__).parent / "golden" / str(BOOK_ID)


def _pipeline_fixture(fixture_name, module_name, function_name=None, transform=None):
    @pytest.fixture(scope="session", name=fixture_name)
    def fixture(book):
        module = import_module(f"pipeline.{module_name}")
        result = getattr(module, function_name or module_name)(book)
        return transform(result) if transform else result

    return fixture


def _without_seconds(result):
    for algorithm in result.get("algorithms", {}).values():
        algorithm.pop("seconds", None)
    return result


@pytest.fixture(scope="session")
def golden():
    def load(name):
        with (GOLDEN_DIR / f"{name}.json").open(encoding="utf-8") as handle:
            return json.load(handle)

    return load


@pytest.fixture(scope="session")
def book():
    return Book(BOOK_ID)


lexdiv_result = _pipeline_fixture("lexdiv_result", "lexdiv")
lexdiv_plus_result = _pipeline_fixture("lexdiv_plus_result", "lexdiv", "lexdiv_plus")
topics_result = _pipeline_fixture("topics_result", "topics")
entities_result = _pipeline_fixture("entities_result", "entities")
summary_result = _pipeline_fixture("summary_result", "summarize")
similar_result = _pipeline_fixture("similar_result", "similar")
arc_result = _pipeline_fixture("arc_result", "arc")
syntax_result = _pipeline_fixture("syntax_result", "syntax")
compare_result = _pipeline_fixture("compare_result", "compare", transform=_without_seconds)
eval_summary_result = _pipeline_fixture("eval_summary_result", "rouge", "eval_summary")
card_result = _pipeline_fixture("card_result", "card")


@pytest.fixture
def make_book():
    def factory(text, book_id=0):
        stub = Book(book_id)
        stub.__dict__.update(raw=text, lang="en")
        return stub

    return factory
