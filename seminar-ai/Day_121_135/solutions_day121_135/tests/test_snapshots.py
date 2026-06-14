#!/usr/bin/env python3

import re

import pytest


def _int_keys(data):
    return {int(key): value for key, value in data.items()}


SNAPSHOT_CASES = [
    ("lexdiv_result", "lexdiv", None),
    ("lexdiv_plus_result", "lexdiv_plus", None),
    ("topics_result", "topics", _int_keys),
    ("entities_result", "entities", None),
    ("similar_result", "similar", None),
    ("arc_result", "arc", _int_keys),
    ("compare_result", "compare", None),
]

# The extractive summary (TF-IDF -> TruncatedSVD -> KMeans) is deterministic on a
# given machine but its float path differs across OS / BLAS, so a couple of the
# five selected sentences can swap. We therefore compare the summary and its ROUGE
# scores against the golden with a tolerance instead of byte equality. Measured
# divergence on a Windows/OpenBLAS box vs the committed golden: token Jaccard 0.607,
# max abs ROUGE score diff 0.060 — the thresholds below leave comfortable headroom
# while still catching a genuinely different summary.
SUMMARY_OVERLAP_FLOOR = 0.45
ROUGE_SCORE_TOLERANCE = 0.15


def _summary_tokens(text):
    return set(re.findall(r"[a-z']+", text.lower()))


@pytest.mark.parametrize("fixture_name,golden_name,normalize", SNAPSHOT_CASES)
def test_pipeline_matches_golden(request, golden, fixture_name, golden_name, normalize):
    expected = golden(golden_name)
    if normalize:
        expected = normalize(expected)
    assert request.getfixturevalue(fixture_name) == expected


def test_summary_overlaps_golden(summary_result, golden):
    expected = golden("summarize")
    got, want = _summary_tokens(summary_result), _summary_tokens(expected)
    overlap = len(got & want) / len(got | want)
    assert overlap >= SUMMARY_OVERLAP_FLOOR, (
        f"summary token overlap with golden {overlap:.3f} < {SUMMARY_OVERLAP_FLOOR}"
    )


def test_eval_summary_matches_golden(eval_summary_result, golden):
    expected = golden("rouge")
    assert eval_summary_result["reference"] == expected["reference"]
    assert eval_summary_result["reference_words"] == expected["reference_words"]

    got = eval_summary_result["methods"]["kmeans"]
    want = expected["methods"]["kmeans"]
    assert got.keys() == want.keys()
    for metric, scores in want.items():
        for key, value in scores.items():
            assert abs(got[metric][key] - value) <= ROUGE_SCORE_TOLERANCE, (
                f"kmeans {metric}.{key}={got[metric][key]} diverges from golden {value} "
                f"by more than {ROUGE_SCORE_TOLERANCE}"
            )
