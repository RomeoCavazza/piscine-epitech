#!/usr/bin/env python3

import pytest


def test_flat_features_from_profile_text():
    from pipeline.attribute import profile_text, _flat_features

    text = (
        "The old house stood at the edge of the dark forest. "
        "Nobody had lived there for many years. "
        "Strange sounds could be heard at night. "
        "The villagers avoided the place entirely. "
        "But one day a stranger arrived in town. "
        "He asked about the house with great curiosity. "
        "The innkeeper warned him to stay away. "
        "Yet the stranger smiled and walked toward the forest. "
        "He carried a small leather bag. "
        "The wind howled through the empty streets."
    )
    profile = profile_text(text)
    assert profile is not None
    feats = _flat_features(profile)
    assert len(feats) == 12
    assert all(isinstance(v, (int, float)) for v in feats.values())


def test_profile_text_rejects_short_text():
    from pipeline.attribute import profile_text

    assert profile_text("One sentence.") is None
    assert profile_text("Two sentences. Here is another.") is None


def test_extract_samples_produces_correct_count():
    from pipeline.utils import extract_samples

    sentences = [f"Sentence number {i}." for i in range(200)]
    extracts = extract_samples(sentences, 30, 40)
    assert 1 <= len(extracts) <= 40
    for extract in extracts:
        assert isinstance(extract, str)
        assert len(extract) > 0


def test_extract_samples_short_text_returns_one():
    from pipeline.utils import extract_samples

    sentences = ["Short.", "Very short.", "Tiny."]
    extracts = extract_samples(sentences, 30, 40)
    assert len(extracts) == 1


def test_attribute_rejects_very_short_text():
    from pipeline.attribute import attribute

    with pytest.raises(LookupError, match="too short"):
        attribute("Hi.")


