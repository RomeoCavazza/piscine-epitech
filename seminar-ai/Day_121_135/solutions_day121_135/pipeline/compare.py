#!/usr/bin/env python3

import time

import numpy as np
from sklearn.decomposition import NMF, LatentDirichletAllocation, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from pipeline.topics import MAX_TOPICS, MIN_SECTIONS_FOR_NMF, TOP_WORDS, build_corpus

CACHE_VERSION = 1

UMASS_EPSILON = 1e-12


def _top_words(components, terms):
    topics = []
    for row in components:
        order = row.argsort()[::-1][:TOP_WORDS]
        topics.append([terms[col] for col in order])
    return topics


def _umass_coherence(topics, terms, presence):
    index = {term: col for col, term in enumerate(terms)}
    doc_freq = np.asarray(presence.sum(axis=0)).ravel()

    scores = []
    for words in topics:
        cols = [index[word] for word in words if word in index]
        if len(cols) < 2:
            continue
        sub = presence[:, cols].toarray()
        co_freq = sub.T @ sub
        pairs = []
        for i in range(1, len(cols)):
            for j in range(i):
                denominator = doc_freq[cols[j]]
                if denominator == 0:
                    continue
                pairs.append(np.log((co_freq[i, j] + 1) / (denominator + UMASS_EPSILON)))
        if pairs:
            scores.append(float(np.mean(pairs)))
    return round(float(np.mean(scores)), 4) if scores else None


def _diversity(topics):
    words = [word for topic in topics for word in topic]
    if not words:
        return None
    return round(len(set(words)) / len(words), 4)


def _evaluate(model, matrix, terms, presence):
    start = time.perf_counter()
    model.fit(matrix)
    seconds = time.perf_counter() - start

    topics = _top_words(model.components_, terms)
    return {
        "topics": {str(i + 1): words for i, words in enumerate(topics)},
        "coherence_umass": _umass_coherence(topics, terms, presence),
        "diversity": _diversity(topics),
        "seconds": round(seconds, 4),
    }


def compare(book):
    sections, docs = build_corpus(book)
    if len(sections) < MIN_SECTIONS_FOR_NMF:
        return {
            "sections": len(sections),
            "note": "not enough sections for a meaningful topic model comparison",
        }

    tfidf_vectorizer = TfidfVectorizer(max_df=0.6, min_df=2, sublinear_tf=True)
    try:
        tfidf = tfidf_vectorizer.fit_transform(docs)
    except ValueError:
        return {"sections": len(sections), "note": "vocabulary too small after filtering"}
    if tfidf.shape[1] < 3:
        return {"sections": len(sections), "note": "vocabulary too small after filtering"}

    terms = np.array(tfidf_vectorizer.get_feature_names_out())

    count_vectorizer = CountVectorizer(vocabulary=tfidf_vectorizer.vocabulary_)
    counts = count_vectorizer.fit_transform(docs)
    presence = (counts > 0).astype(np.int32)

    n_topics = min(MAX_TOPICS, len(sections) - 1, tfidf.shape[1] - 1)
    n_topics = max(2, n_topics)

    models = {
        "nmf": (NMF(n_components=n_topics, init="nndsvd", random_state=0, max_iter=400), tfidf),
        "lsa": (TruncatedSVD(n_components=n_topics, random_state=0), tfidf),
        "lda": (
            LatentDirichletAllocation(
                n_components=n_topics, learning_method="batch", random_state=0, max_iter=15
            ),
            counts,
        ),
    }

    algorithms = {
        name: _evaluate(model, matrix, terms, presence)
        for name, (model, matrix) in models.items()
    }

    ranked = sorted(
        (name for name in algorithms if algorithms[name]["coherence_umass"] is not None),
        key=lambda name: (
            algorithms[name]["coherence_umass"],
            algorithms[name]["diversity"] or 0,
        ),
        reverse=True,
    )

    return {
        "sections": len(sections),
        "n_topics": n_topics,
        "vocabulary": int(tfidf.shape[1]),
        "algorithms": algorithms,
        "best": ranked[0] if ranked else None,
        "criteria": "highest UMass coherence, topic diversity as tiebreaker",
    }
