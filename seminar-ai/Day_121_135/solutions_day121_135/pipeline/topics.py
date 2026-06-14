#!/usr/bin/env python3

import string
from collections import Counter

import numpy as np
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer

from core.nlp import get_wordnet_pos, stopword_list, sklearn_stop_words
from pipeline.utils import split_chapters
import time
from sklearn.cluster import KMeans
from pipeline.bert import embed, runtime_metadata

TOP_WORDS = 10
MIN_SECTIONS_FOR_NMF = 4
MAX_TOPICS = 8
CACHE_VERSION = 1

STRIP_CHARS = string.punctuation + "\u201c\u201d\u2018\u2019\u2014\u2013"


def _preprocess(section, stop_words, lemmatizer):
    tokens = [word.strip(STRIP_CHARS).lower() for word in section.split()]
    tokens = [t for t in tokens if t.isalpha()]
    lemmas = [
        lemmatizer.lemmatize(word, get_wordnet_pos(tag))
        for word, tag in pos_tag(tokens)
        if len(word) > 2 and word not in stop_words
    ]
    return [lemma for lemma in lemmas if lemma not in stop_words and len(lemma) > 2]


def _top_terms_per_section(docs):
    non_empty = [doc for doc in docs if doc]
    if not non_empty:
        return {index: [] for index in range(1, len(docs) + 1)}

    vectorizer = TfidfVectorizer(min_df=1, sublinear_tf=True)
    matrix = vectorizer.fit_transform(docs).toarray()
    terms = np.array(vectorizer.get_feature_names_out())

    result = {}
    for index, row in enumerate(matrix, start=1):
        order = row.argsort()[::-1][:TOP_WORDS]
        result[index] = [terms[col] for col in order if row[col] > 0]
    return result


def _section_topic_words(topic_profile, section_profile, terms):
    blended = topic_profile * section_profile
    words = []
    for col in blended.argsort()[::-1]:
        if blended[col] <= 0:
            break
        words.append(terms[col])
        if len(words) == TOP_WORDS:
            return words

    for col in topic_profile.argsort()[::-1]:
        word = terms[col]
        if word not in words:
            words.append(word)
        if len(words) == TOP_WORDS:
            break
    return words


def _frequency_fallback(docs):
    result = {}
    for index, doc in enumerate(docs, start=1):
        counts = Counter(doc.split())
        result[index] = [word for word, _ in counts.most_common(TOP_WORDS)]
    return result


def build_corpus(book):
    sections = split_chapters(book.clean)
    if not sections:
        return [], []

    stop_words = set(stopword_list(book.lang))
    lemmatizer = WordNetLemmatizer()
    docs = [" ".join(_preprocess(section, stop_words, lemmatizer)) for section in sections]
    return sections, docs


def topics(book):
    sections, docs = build_corpus(book)
    if not sections:
        return {}

    if len(sections) < MIN_SECTIONS_FOR_NMF:
        return _top_terms_per_section(docs)

    vectorizer = TfidfVectorizer(max_df=0.6, min_df=2, sublinear_tf=True)
    try:
        matrix = vectorizer.fit_transform(docs)
    except ValueError:
        return _frequency_fallback(docs)
    if matrix.shape[1] == 0:
        return _top_terms_per_section(docs)

    terms = np.array(vectorizer.get_feature_names_out())

    n_topics = min(MAX_TOPICS, len(sections) - 1, matrix.shape[1])
    n_topics = max(2, n_topics)

    model = NMF(n_components=n_topics, init="nndsvd", random_state=0, max_iter=400)
    section_topic = model.fit_transform(matrix)
    topic_term = model.components_
    section_term = matrix.toarray()

    result = {}
    for index in range(len(sections)):
        dominant = int(section_topic[index].argmax())
        result[index + 1] = _section_topic_words(
            topic_term[dominant], section_term[index], terms
        )
    return result


def _cluster_keywords(sections, labels, lang):
    grouped = []
    for cluster in sorted(set(labels)):
        grouped.append(" ".join(section for section, label in zip(sections, labels) if label == cluster))

    vectorizer = TfidfVectorizer(stop_words=sklearn_stop_words(lang), max_df=0.9, min_df=1)
    matrix = vectorizer.fit_transform(grouped)
    terms = np.array(vectorizer.get_feature_names_out())

    keywords = {}
    for index, row in enumerate(matrix.toarray(), start=1):
        order = row.argsort()[::-1][:TOP_WORDS]
        keywords[index] = [terms[col] for col in order if row[col] > 0]
    return keywords


def topics_bert(book):
    start = time.perf_counter()
    sections = [section for section in split_chapters(book.clean) if section.strip()]
    if not sections:
        return {"clusters": {}, **runtime_metadata(start)}

    if len(sections) == 1:
        labels = np.array([0])
    else:
        vectors = embed(sections)
        n_clusters = min(MAX_TOPICS, len(sections))
        n_clusters = max(2, n_clusters)
        labels = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit_predict(vectors)

    try:
        keywords = _cluster_keywords(sections, labels, book.lang)
    except ValueError:
        keywords = {index + 1: [] for index in sorted(set(labels))}

    clusters = {}
    for index, cluster in enumerate(sorted(set(labels)), start=1):
        section_numbers = [
            section_index + 1
            for section_index, label in enumerate(labels)
            if label == cluster
        ]
        clusters[str(index)] = {
            "keywords": keywords.get(index, [])[:TOP_WORDS],
            "sections": section_numbers,
        }

    return {"clusters": clusters, **runtime_metadata(start)}
