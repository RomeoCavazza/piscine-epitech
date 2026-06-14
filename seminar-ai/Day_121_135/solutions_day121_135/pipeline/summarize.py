#!/usr/bin/env python3

from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import pairwise_distances, silhouette_score
from sklearn.preprocessing import normalize

from core.nlp import sklearn_stop_words
import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from pipeline.bert import embed, runtime_metadata

CACHE_VERSION = 2

MIN_SENTENCE_LENGTH = 40
NUM_SENTENCES = 5
LSA_COMPONENTS = 100


def _candidates(book):
    return [
        (index, sentence)
        for index, sentence in enumerate(book.sentences)
        if len(sentence) > MIN_SENTENCE_LENGTH
    ]


def _lsa_space(texts, lang):
    vectorizer = TfidfVectorizer(stop_words=sklearn_stop_words(lang))
    matrix = vectorizer.fit_transform(texts)

    n_components = min(LSA_COMPONENTS, matrix.shape[0] - 1, matrix.shape[1] - 1)
    if n_components < 1:
        raise ValueError("not enough dimensions for LSA")
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    return normalize(svd.fit_transform(matrix))


def _cluster(texts, lang, n_clusters=NUM_SENTENCES):
    reduced = _lsa_space(texts, lang)
    n_clusters = min(n_clusters, len(texts))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(reduced)
    
    distances = pairwise_distances(kmeans.cluster_centers_, reduced)
    closest_indices = []
    used = set()
    for i in range(n_clusters):
        for idx in np.argsort(distances[i]):
            if idx not in used:
                closest_indices.append(idx)
                used.add(idx)
                break
                
    return reduced, kmeans, closest_indices


def summarize(book):
    candidates = _candidates(book)
    if len(candidates) <= NUM_SENTENCES:
        return " ".join(s for _, s in candidates)

    texts = [s for _, s in candidates]
    try:
        _, _, closest_indices = _cluster(texts, book.lang)
    except Exception:
        return " ".join(texts[:NUM_SENTENCES])

    top_indices = sorted(list(closest_indices))
    summary = [candidates[i][1] for i in top_indices]

    return " ".join(" ".join(s.split()) for s in summary)


def silhouette_profile(book, k_range=range(2, 9)):
    candidates = _candidates(book)
    if len(candidates) < 3:
        return {}

    texts = [s for _, s in candidates]
    try:
        reduced = _lsa_space(texts, book.lang)
    except Exception:
        return {}

    max_k = len(texts) - 1
    result = {}
    for k in k_range:
        if k < 2 or k > max_k:
            continue
        labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(reduced)
        if len(set(labels)) < 2:
            continue
        result[k] = round(float(silhouette_score(reduced, labels)), 4)
    return result


def cluster_map(book):
    candidates = _candidates(book)
    if len(candidates) <= NUM_SENTENCES:
        return None

    texts = [s for _, s in candidates]
    try:
        reduced, kmeans, closest_indices = _cluster(texts, book.lang)
    except Exception:
        return None

    svd = TruncatedSVD(n_components=2, random_state=42)
    coords = svd.fit_transform(reduced)
    return {
        "coords": coords,
        "labels": kmeans.labels_,
        "selected": sorted(int(i) for i in closest_indices),
        "texts": texts,
    }


def summarize_bert(book):
    start = time.perf_counter()
    candidates = _candidates(book)
    if len(candidates) <= NUM_SENTENCES:
        summary = " ".join(" ".join(sentence.split()) for _, sentence in candidates)
        return {"summary": summary, **runtime_metadata(start)}

    texts = [sentence for _, sentence in candidates]
    vectors = embed(texts)
    centroid = vectors.mean(axis=0, keepdims=True)
    scores = cosine_similarity(vectors, centroid).ravel()
    chosen = sorted(np.argsort(scores)[-NUM_SENTENCES:])
    summary = " ".join(" ".join(texts[index].split()) for index in chosen)

    return {"summary": summary, **runtime_metadata(start)}
