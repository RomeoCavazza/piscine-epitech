import requests

from core.data import OPDS_SEARCH_URL, _parse_opds_feed, _search_local_catalog, _search_opds


def test_parse_opds_feed_skips_navigation_entries():
    feed = b"""<?xml version="1.0" encoding="utf-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>https://www.gutenberg.org/ebooks/bookshelf/1</id>
        <title>Navigation</title>
      </entry>
      <entry>
        <id>https://www.gutenberg.org/ebooks/11</id>
        <title>Alice's Adventures in Wonderland</title>
        <author><name>Carroll, Lewis</name></author>
      </entry>
      <entry>
        <id>https://www.gutenberg.org/ebooks/345</id>
        <title>Dracula</title>
        <content type="text">Stoker, Bram</content>
      </entry>
    </feed>
    """

    assert _parse_opds_feed(feed, limit=1) == [
        {
            "id": 11,
            "title": "Alice's Adventures in Wonderland",
            "authors": "Carroll, Lewis",
        }
    ]


def test_local_catalog_author_search_matches_reordered_names():
    books = _search_local_catalog(author="Conan Doyle")

    assert books
    assert all("Doyle" in book["authors"] for book in books)


def test_search_books_falls_back_to_local_catalog(monkeypatch):
    import core.data

    def fail(*args, **kwargs):
        raise requests.Timeout("offline")

    monkeypatch.setattr(core.data.requests, "get", fail)

    books = core.data.search_books(author="Conan Doyle", limit=3)

    assert books
    assert all("Doyle" in book["authors"] for book in books)


def test_search_opds_follows_next_pages(monkeypatch):
    next_url = "https://www.gutenberg.org/ebooks/search.opds/?start_index=2&query=Conan+Doyle"
    first_page = f"""<?xml version="1.0" encoding="utf-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <link rel="next" href="{next_url.replace('&', '&amp;')}" />
      <entry>
        <id>https://www.gutenberg.org/ebooks/108</id>
        <title>The Return of Sherlock Holmes</title>
        <author><name>Doyle, Arthur Conan</name></author>
      </entry>
    </feed>
    """.encode()
    second_page = b"""<?xml version="1.0" encoding="utf-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>https://www.gutenberg.org/ebooks/834</id>
        <title>The Memoirs of Sherlock Holmes</title>
        <author><name>Doyle, Arthur Conan</name></author>
      </entry>
    </feed>
    """
    pages = {OPDS_SEARCH_URL: first_page, next_url: second_page}
    calls = []

    class Response:
        def __init__(self, content):
            self.content = content

        def raise_for_status(self):
            return None

    def fake_get(url, params=None, **kwargs):
        calls.append((url, params))
        return Response(pages[url])

    monkeypatch.setattr(requests, "get", fake_get)

    books = _search_opds("Conan Doyle")

    assert [book["id"] for book in books] == [108, 834]
    assert calls == [
        (OPDS_SEARCH_URL, {"query": "Conan Doyle"}),
        (next_url, None),
    ]


def test_language_defaults_to_english_without_network(monkeypatch):
    import core.tools

    monkeypatch.setattr(core.tools, "_read_catalog", lambda book_id: None)
    monkeypatch.setattr(core.tools, "_read_cached_info", lambda book_id: None)
    monkeypatch.setattr(
        core.tools,
        "_fetch_gutendex",
        lambda book_id: (_ for _ in ()).throw(AssertionError("network not expected")),
    )

    assert core.tools.language(999999) == "en"


def test_category_dispatch_uses_topic_keyword(monkeypatch):
    import bookworm
    import core.data

    calls = {}

    def fake_search_books(**kwargs):
        calls.update(kwargs)
        return []

    monkeypatch.setattr(core.data, "search_books", fake_search_books)
    monkeypatch.setattr(core.data, "download_many", lambda ids: None)

    assert bookworm.dispatch("category", "Science Fiction") == []
    assert calls == {"topic": "Science Fiction", "limit": None}


def test_category_dispatch_forwards_limit(monkeypatch):
    import bookworm
    import core.data

    calls = {}

    def fake_search_books(**kwargs):
        calls.update(kwargs)
        return []

    monkeypatch.setattr(core.data, "search_books", fake_search_books)
    monkeypatch.setattr(core.data, "download_many", lambda ids: None)

    assert bookworm.dispatch("category", "Science Fiction", limit=3) == []
    assert calls == {"topic": "Science Fiction", "limit": 3}
