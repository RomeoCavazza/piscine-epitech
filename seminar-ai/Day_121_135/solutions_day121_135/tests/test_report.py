#!/usr/bin/env python3

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline.report import _render, _img, _items, _topics_rows  # noqa: E402


MINIMAL_DATA = {
    "lexdiv": {"tok": 1000, "typ": 200, "hap": 50, "ttr": 0.2, "mwl": 4.5, "mwf": 5.0},
    "lexdiv_plus": {"msttr": 0.8, "mattr": 0.82, "mtld": 90.0, "guiraud": 6.3, "herdan_c": 0.79, "yule_k": 0.01, "maas_a2": 0.05},
    "summary": "A story about a girl who falls down a rabbit hole.",
    "entities": {"characters": ["Alice", "White Rabbit"], "locations": ["Wonderland"]},
    "topics": {1: ["alice", "rabbit", "queen"], 2: ["tea", "hatter", "time"]},
    "similar": ["Through the Looking-Glass", "Peter Pan"],
}

MINIMAL_IMAGES = {"cover": None, "lexdiv": None, "compare": None}
MINIMAL_CHARTS = {"arc": None, "galaxy": None, "kmeans": "", "silhouette": ""}
MINIMAL_COMPARISON = {"note": "comparison unavailable"}


class _FakeBook:
    id = 11
    info = {"title": "Alice's Adventures in Wonderland", "authors": "Lewis Carroll", "bookshelves": "Children"}


def _html():
    return _render(_FakeBook(), MINIMAL_DATA, MINIMAL_COMPARISON, MINIMAL_IMAGES, MINIMAL_CHARTS)


def test_render_returns_string():
    assert isinstance(_html(), str)


@pytest.mark.parametrize(
    "expected",
    [
        "Alice",
        "Lewis Carroll",
        "rabbit hole",
        "Wonderland",
        "Through the Looking-Glass",
        "Peter Pan",
    ],
)
def test_render_contains_expected_content(expected):
    assert expected in _html()


def test_render_contains_lexdiv_values():
    output = _html()
    assert "1,000" in output
    assert "200" in output


def test_render_contains_characters():
    output = _html()
    assert "Alice" in output
    assert "White Rabbit" in output


def test_render_topics_rows_count():
    rows_html = _topics_rows(MINIMAL_DATA["topics"])
    assert rows_html.count("<tr>") == 2


def test_render_escapes_html_in_summary():
    data = {**MINIMAL_DATA, "summary": "<script>alert(1)</script>"}
    output = _render(_FakeBook(), data, MINIMAL_COMPARISON, MINIMAL_IMAGES, MINIMAL_CHARTS)
    assert "<script>" not in output
    assert "&lt;script&gt;" in output


def test_img_empty_when_no_data():
    assert _img(None) == ""
    assert _img("") == ""


def test_img_produces_data_uri():
    assert 'src="data:image/png;base64,abc"' in _img("abc")


def test_items_produces_list_items():
    result = _items(["Alice", "Bob"])
    assert result.count("<li>") == 2
    assert "Alice" in result


@pytest.mark.integration
def test_report_writes_html_file(tmp_path):
    from core.book import Book
    from core import cache

    book = Book(11)
    with patch.object(cache, "CORPUS_DIR", tmp_path):
        from pipeline import report as report_pipeline
        with patch.object(report_pipeline, "report") as mock_report:
            mock_report.return_value = str(tmp_path / "card.html")
            path = mock_report(book)
    assert path.endswith(".html")
