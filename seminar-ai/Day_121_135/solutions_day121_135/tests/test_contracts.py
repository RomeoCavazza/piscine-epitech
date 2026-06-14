#!/usr/bin/env python3

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from nltk import sent_tokenize

ROOT = Path(__file__).resolve().parent.parent

LEXDIV_SCHEMA = {"tok": int, "typ": int, "hap": int, "ttr": float, "mwl": float, "mwf": float}
CARD_KEYS = {"info", "lexdiv", "topics", "entities", "summary", "similar"}
ROUGE_KEYS = {"rouge1", "rouge2", "rougeL"}
ROUGE_SCORE_KEYS = {"p", "r", "f"}


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "bookworm.py", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )


def cli_json(*args):
    process = run_cli(*args)
    assert process.returncode == 0, process.stderr
    return json.loads(process.stdout)


def test_lexdiv_returns_the_subject_schema(lexdiv_result):
    assert set(lexdiv_result) == set(LEXDIV_SCHEMA)
    for key, expected_type in LEXDIV_SCHEMA.items():
        assert isinstance(lexdiv_result[key], expected_type)


def test_topics_sections_are_numbered_from_one(topics_result):
    assert sorted(topics_result) == list(range(1, len(topics_result) + 1))


def test_topics_returns_exactly_ten_words_per_section(topics_result):
    for words in topics_result.values():
        assert len(words) == 10
        assert all(isinstance(word, str) for word in words)


def test_entities_returns_characters_and_locations(entities_result):
    assert set(entities_result) == {"characters", "locations"}
    for values in entities_result.values():
        assert isinstance(values, list)
        assert all(isinstance(value, str) and value for value in values)


def test_summary_is_a_few_sentences(summary_result):
    assert isinstance(summary_result, str)
    assert 2 <= len(sent_tokenize(summary_result)) <= 10


def test_summary_is_not_the_trivial_head_baseline(summary_result, book):
    from pipeline.summarize import MIN_SENTENCE_LENGTH, NUM_SENTENCES

    head = [s for s in book.sentences if len(s) > MIN_SENTENCE_LENGTH][:NUM_SENTENCES]
    assert summary_result != " ".join(head)
    assert summary_result != " ".join(" ".join(s.split()) for s in head)


def test_similar_returns_five_distinct_titles(similar_result, book):
    assert isinstance(similar_result, list)
    assert len(similar_result) == 5
    assert len(set(similar_result)) == 5


def test_card_matches_the_subject_schema(card_result):
    assert set(card_result) == CARD_KEYS
    info = card_result["info"]
    assert set(info) == {"id", "authors", "bookshelves"}
    assert all(isinstance(value, str) for value in info.values())


def test_card_reuses_the_same_topics_segmentation(card_result, topics_result):
    card_sections = {int(section) for section in card_result["topics"]}
    assert card_sections == set(topics_result)


def test_cli_rejects_invalid_input_with_exit_84():
    process = run_cli("--lexdiv", "abc")
    assert process.returncode == 84
    assert process.stderr.strip()


def test_cli_lexdiv_prints_valid_json():
    assert set(cli_json("--lexdiv", str(11))) == set(LEXDIV_SCHEMA)


def test_cli_arc_prints_one_score_per_section():
    result = cli_json("--arc", str(11))
    assert result
    assert all(isinstance(score, float) for score in result.values())


def test_cli_exposes_documented_syntax_flags():
    import bookworm

    assert "syntax" in bookworm.FEATURES
    assert "authorsyntax" in bookworm.ARG_FEATURES


def test_bert_cli_flags_point_to_owner_modules():
    from pipeline.registry import BOOK_COMMANDS

    assert BOOK_COMMANDS["summarize-bert"].module == "summarize"
    assert BOOK_COMMANDS["summarize-bert"].function == "summarize_bert"
    assert BOOK_COMMANDS["similar-bert"].module == "similar"
    assert BOOK_COMMANDS["similar-bert"].function == "similar_bert"
    assert BOOK_COMMANDS["topics-bert"].module == "topics"
    assert BOOK_COMMANDS["topics-bert"].function == "topics_bert"


def test_eval_summary_returns_rouge_scores(eval_summary_result):
    assert eval_summary_result["reference"] == "wikipedia"
    assert eval_summary_result["reference_words"] > 0
    assert "kmeans" in eval_summary_result["methods"]

    scores = eval_summary_result["methods"]["kmeans"]
    assert set(scores) == ROUGE_KEYS
    for metric in scores.values():
        assert set(metric) == ROUGE_SCORE_KEYS
        assert all(isinstance(value, float) for value in metric.values())
        assert all(0.0 <= value <= 1.0 for value in metric.values())


def test_cli_eval_summary_prints_valid_json():
    result = cli_json("--eval-summary", str(11))
    assert result["reference"] == "wikipedia"
    assert "kmeans" in result["methods"]


def test_cli_eval_summary_rejects_missing_reference():
    process = run_cli("--eval-summary", str(999999))
    assert process.returncode == 84
    assert "no reference summary" in process.stderr


@pytest.mark.skipif(shutil.which("git") is None, reason="git not available")
def test_cache_and_models_are_never_tracked():
    for path in ("data/output/", "models/"):
        process = subprocess.run(
            ["git", "check-ignore", "-q", path], cwd=ROOT, capture_output=True
        )
        assert process.returncode == 0, f"{path} must be gitignored"
