#!/usr/bin/env python3

from pathlib import Path

import pytest

pytest.importorskip("streamlit")

from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")
ANALYSIS_LABEL = "Diversité lexicale"


def _app():
    return AppTest.from_file(APP_PATH, default_timeout=60)


def _show_book_header(at, book_id):
    at.sidebar.text_input[1].input(str(book_id)).run()
    at.sidebar.multiselect[0].select(ANALYSIS_LABEL).run()
    for btn in at.sidebar.button:
        if btn.label == "Analyser":
            btn.click().run()
            break
    return at


def test_app_renders_alice_book():
    at = _show_book_header(_app().run(), 11)

    assert not at.exception
    assert any("Alice" in element.value for element in at.title)


def test_app_accepts_any_gutenberg_id():
    at = _show_book_header(_app().run(), 9999)

    assert not at.exception
    assert any("Harriet" in element.value for element in at.title)


def test_app_searches_local_catalog():
    at = _app().run()
    at.sidebar.text_input[0].input("dracula").run()

    assert not at.exception
    assert any("Dracula" in button.label for button in at.sidebar.button)
