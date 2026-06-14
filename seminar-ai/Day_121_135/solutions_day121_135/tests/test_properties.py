#!/usr/bin/env python3

from nltk import sent_tokenize

from core.nlp import stopword_list


def test_lexdiv_counts_are_ordered(lexdiv_result):
    assert 0 < lexdiv_result["hap"] <= lexdiv_result["typ"] <= lexdiv_result["tok"]


def test_lexdiv_ratios_match_their_definitions(lexdiv_result):
    tok, typ = lexdiv_result["tok"], lexdiv_result["typ"]
    assert abs(lexdiv_result["ttr"] - typ / tok) < 1e-3
    assert abs(lexdiv_result["mwf"] - tok / typ) < 1e-3
    assert 0 < lexdiv_result["ttr"] <= 1
    assert lexdiv_result["mwl"] > 0


def test_topics_words_are_clean_lemmas(topics_result):
    stop_words = set(stopword_list("en"))
    for words in topics_result.values():
        for word in words:
            assert word == word.lower()
            assert word.isalpha()
            assert len(word) > 2
            assert word not in stop_words


def test_topics_words_are_unique_within_a_section(topics_result):
    for words in topics_result.values():
        assert len(set(words)) == len(words)


def test_summary_sentences_are_extracted_from_the_book(summary_result, book):
    normalized_book = " ".join(book.clean.split())
    for sentence in sent_tokenize(summary_result):
        assert sentence in normalized_book


def test_entities_respect_the_ranking_limits(entities_result):
    from pipeline.entities import LIMIT

    for values in entities_result.values():
        assert len(values) <= LIMIT
        assert len(set(values)) == len(values)


def test_arc_sections_are_numbered_from_one(arc_result):
    assert sorted(arc_result) == list(range(1, len(arc_result) + 1))


def test_arc_scores_are_bounded_vader_compounds(arc_result):
    assert len(arc_result) >= 2
    for score in arc_result.values():
        assert isinstance(score, float)
        assert -1.0 <= score <= 1.0


def test_galaxy_map_projects_the_whole_catalog():
    from pipeline.similar import COLLECTION, galaxy_map

    galaxy = galaxy_map()
    assert galaxy is not None
    assert set(galaxy["ids"]) == set(COLLECTION)
    assert len(galaxy["x"]) == len(galaxy["y"]) == len(galaxy["titles"]) == len(galaxy["ids"])
    assert set(galaxy["categories"]) == set(COLLECTION.values())
    assert len(galaxy["cluster_labels"]) == len(galaxy["ids"])


def test_summary_silhouette_profile_scores_are_bounded(book):
    from pipeline.summarize import NUM_SENTENCES, silhouette_profile

    profile = silhouette_profile(book)
    assert profile
    assert NUM_SENTENCES in profile
    assert all(isinstance(k, int) and 2 <= k <= 8 for k in profile)
    assert all(-1.0 <= score <= 1.0 for score in profile.values())


def test_catalog_cluster_validation_selects_best_k():
    from pipeline.similar import COLLECTION, cluster_catalog

    clusters = cluster_catalog()
    scores = clusters["scores"]
    assert scores
    assert clusters["k"] == max(scores, key=scores.get)
    assert clusters["score"] == scores[clusters["k"]]
    assert len(clusters["labels"]) == len(COLLECTION)
    assert len(set(clusters["labels"])) == clusters["k"]
    assert all(-1.0 <= score <= 1.0 for score in scores.values())


def test_compare_evaluates_the_three_decompositions(compare_result):
    assert set(compare_result["algorithms"]) == {"nmf", "lsa", "lda"}
    assert compare_result["best"] in compare_result["algorithms"]
    for algorithm in compare_result["algorithms"].values():
        assert len(algorithm["topics"]) == compare_result["n_topics"]
        assert 0 < algorithm["diversity"] <= 1
        assert algorithm["coherence_umass"] is not None


def test_eval_summary_is_deterministic(book, eval_summary_result):
    from pipeline.rouge import eval_summary

    assert eval_summary(book) == eval_summary_result


def test_pipelines_are_deterministic(book, topics_result, summary_result, compare_result):
    from pipeline.compare import compare
    from pipeline.summarize import summarize
    from pipeline.topics import topics

    assert topics(book) == topics_result
    assert summarize(book) == summary_result

    rerun = compare(book)
    for algorithm in rerun["algorithms"].values():
        algorithm.pop("seconds", None)
    assert rerun == compare_result
