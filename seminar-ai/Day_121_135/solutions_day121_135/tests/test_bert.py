#!/usr/bin/env python3

import numpy as np
from nltk import sent_tokenize


def _one_hot_embed(dim):
    def fake_embed(texts, batch_size=None, max_length=None):
        vectors = np.zeros((len(texts), dim), dtype=np.float32)
        for index in range(len(texts)):
            vectors[index, index % dim] = 1.0
        return vectors

    return fake_embed


def test_summarize_bert_contract_without_loading_model(make_book, monkeypatch):
    from pipeline import bert
    from pipeline import summarize

    text = " ".join(
        f"This is candidate sentence number {index} with enough words to pass the length filter."
        for index in range(1, 9)
    )
    book = make_book(text, book_id=11)

    monkeypatch.setattr(summarize, "embed", _one_hot_embed(4))
    monkeypatch.setattr(bert, "_peak_memory_mb", lambda: 123.0)

    result = summarize.summarize_bert(book)
    assert set(result) == {"summary", "seconds", "peak_memory_mb", "model"}
    assert 2 <= len(sent_tokenize(result["summary"])) <= 10
    assert result["peak_memory_mb"] == 123.0
    assert "distilbert-base-uncased" in result["model"]


def test_similar_bert_contract_without_loading_model(book, monkeypatch):
    from pipeline import similar
    from pipeline import bert

    ids = [11, 12, 16, 35, 36, 84]
    matrix = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.9, 0.1, 0.0],
            [0.8, 0.2, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.9, 0.1],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float32,
    )

    monkeypatch.setattr(similar, "_bert_catalog_index", lambda: {"ids": ids, "matrix": matrix})
    monkeypatch.setattr(similar, "_book_embedding", lambda _: np.array([1.0, 0.0, 0.0], dtype=np.float32))
    monkeypatch.setattr(bert, "_peak_memory_mb", lambda: 123.0)

    result = similar.similar_bert(book)
    assert set(result) == {"similar", "seconds", "peak_memory_mb", "model", "sentences_per_book"}
    assert len(result["similar"]) == 5
    assert len(set(result["similar"])) == 5
    assert book.info["title"] not in result["similar"]
    assert result["peak_memory_mb"] == 123.0
    assert result["sentences_per_book"] == bert.MAX_SENTENCES_PER_BOOK


def test_topics_bert_contract_without_loading_model(make_book, monkeypatch):
    from pipeline import bert
    from pipeline import topics

    text = "\n\n".join(
        f"CHAPTER {index}\n"
        f"Wonderland mystery garden ocean detective science adventure number {index}. "
        f"This section has enough repeated content for keyword extraction and clustering."
        for index in range(1, 7)
    )
    book = make_book(text, book_id=11)

    monkeypatch.setattr(topics, "embed", _one_hot_embed(3))
    monkeypatch.setattr(bert, "_peak_memory_mb", lambda: 123.0)

    result = topics.topics_bert(book)
    assert set(result) == {"clusters", "seconds", "peak_memory_mb", "model"}
    assert result["clusters"]
    assert result["peak_memory_mb"] == 123.0
    for cluster in result["clusters"].values():
        assert set(cluster) == {"keywords", "sections"}
        assert len(cluster["keywords"]) <= topics.TOP_WORDS
        assert all(isinstance(word, str) for word in cluster["keywords"])
        assert all(isinstance(section, int) for section in cluster["sections"])
