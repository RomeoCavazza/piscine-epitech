#!/usr/bin/env python3

import pytest


def test_syntax_returns_expected_schema(syntax_result):
    assert set(syntax_result) == {"surface", "grammar", "sentences_analyzed"}
    assert syntax_result["sentences_analyzed"] > 0

    surface = syntax_result["surface"]
    assert "mean_sentence_length" in surface
    assert "median_sentence_length" in surface
    assert "sentence_length_distribution" in surface
    assert "pos_distribution" in surface
    assert "punctuation_density" in surface

    dist = surface["sentence_length_distribution"]
    assert set(dist) == {"short", "medium", "long"}
    total = dist["short"] + dist["medium"] + dist["long"]
    assert abs(total - 1.0) < 0.01

    grammar = syntax_result["grammar"]
    assert "subordination_rate" in grammar
    assert "passive_ratio" in grammar
    assert "mean_tree_depth" in grammar
    assert "nsubj_per_sentence" in grammar
    assert "dobj_per_sentence" in grammar
    assert "advmod_per_sentence" in grammar


def test_syntax_ratios_in_range(syntax_result):
    g = syntax_result["grammar"]
    assert 0 <= g["subordination_rate"] <= 1
    assert 0 <= g["passive_ratio"] <= 1
    assert g["mean_tree_depth"] > 0
    assert 0 <= g["nsubj_per_sentence"] <= 1
    assert 0 <= g["dobj_per_sentence"] <= 1
    assert 0 <= g["advmod_per_sentence"] <= 1


def test_syntax_pos_distribution_sums_to_one(syntax_result):
    pos = syntax_result["surface"]["pos_distribution"]
    total = sum(pos.values())
    assert abs(total - 1.0) < 0.01


def test_authorsyntax_valid_authors():
    from pipeline.syntax import AUTHOR_BOOKS

    assert set(AUTHOR_BOOKS) == {"Carroll", "Christie", "Doyle", "Wells"}
    for author in AUTHOR_BOOKS:
        assert len(AUTHOR_BOOKS[author]) > 0


def test_authorsyntax_rejects_unknown_author():
    from pipeline.syntax import authorsyntax

    with pytest.raises(LookupError, match="unknown author"):
        authorsyntax("ZZZ_XYZ_123")


def test_flat_features_has_12_keys(syntax_result):
    from pipeline.syntax import _flat_features

    feats = _flat_features(syntax_result)
    assert len(feats) == 12
    assert all(isinstance(v, (int, float)) for v in feats.values())
