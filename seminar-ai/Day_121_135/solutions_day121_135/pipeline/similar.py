#!/usr/bin/env python3

import csv
import os
import sys

import joblib
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity

from core import cache, data
from core.nlp import cleaner, sklearn_stop_words
from core.tools import COLLECTION_PATH, _read_catalog, book_title
from core.book import Book
import time
from pipeline.bert import _book_embedding, runtime_metadata, MAX_SENTENCES_PER_BOOK

def _load_collection():
    collection = {}
    if not COLLECTION_PATH.exists():
        return collection
    with COLLECTION_PATH.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            book_id = int(row["Text#"])
            bookshelves = row["Bookshelves"]
            if "Children & Young Adult" in bookshelves:
                collection[book_id] = "Children / Young Adult"
            elif "Crime, Thrillers" in bookshelves:
                collection[book_id] = "Crime, Mystery & Thriller"
            elif "Science-Fiction & Fantasy" in bookshelves:
                collection[book_id] = "Science-Fiction & Fantasy"
            else:
                collection[book_id] = "Other"
    return collection

COLLECTION = _load_collection()

INDEX_VERSION = 1
CLUSTER_VERSION = 1
FULL_INDEX_VERSION = 1

INDEX_PATH = cache.CORPUS_DIR / f"catalog_tfidf__v{INDEX_VERSION}.joblib"
CLUSTER_PATH = cache.CORPUS_DIR / f"catalog_clusters__v{CLUSTER_VERSION}.joblib"
FULL_INDEX_PATH = cache.CORPUS_DIR / f"fulltext_lsa__v{FULL_INDEX_VERSION}.joblib"
BERT_INDEX_PATH = cache.CORPUS_DIR / f"catalog_bert__v1.joblib"
GALAXY_NEIGHBOR_LIMIT = 400


def cache_version():
    if os.getenv("BOOKWORM_DISABLE_FULL_INDEX") == "1":
        return 1
    return 2 if FULL_INDEX_PATH.exists() else 1


CACHE_VERSION = cache_version


def _build_catalog_index(path, vectorizer_func):
    if path.exists():
        return joblib.load(path)
    ids = list(COLLECTION.keys())
    data_dict = vectorizer_func(ids)
    index = {"ids": ids, **data_dict}
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(index, path)
    return index


def _catalog_index():
    def _tfidf(ids):
        corpus = [cleaner(data.load_text(cid)) for cid in ids]
        vectorizer = TfidfVectorizer(max_features=10000, max_df=0.8, stop_words=sklearn_stop_words("en"))
        return {"vectorizer": vectorizer, "matrix": vectorizer.fit_transform(corpus)}
    return _build_catalog_index(INDEX_PATH, _tfidf)


def cluster_catalog(k_range=range(2, 9)):
    if CLUSTER_PATH.exists():
        return joblib.load(CLUSTER_PATH)

    index = _catalog_index()
    matrix = index["matrix"]
    max_k = min(max(k_range), matrix.shape[0] - 1)

    scores = {}
    labels_by_k = {}
    for k in k_range:
        if k < 2 or k > max_k:
            continue
        labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(matrix)
        if len(set(labels)) < 2:
            continue
        scores[k] = round(float(silhouette_score(matrix, labels)), 4)
        labels_by_k[k] = labels

    if not scores:
        return {"k": None, "score": None, "scores": {}, "labels": []}

    best_k = max(scores, key=scores.get)
    result = {
        "k": best_k,
        "score": scores[best_k],
        "scores": scores,
        "labels": [int(label) for label in labels_by_k[best_k]],
    }
    CLUSTER_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(result, CLUSTER_PATH)
    return result


def _cluster_vectors(matrix, k_range=range(2, 9)):
    if len(matrix) < 3:
        return {"k": None, "score": None, "scores": {}, "labels": [0] * len(matrix)}

    max_k = min(max(k_range), len(matrix) - 1)
    scores = {}
    labels_by_k = {}
    for k in k_range:
        if k < 2 or k > max_k:
            continue
        labels = KMeans(n_clusters=k, random_state=42, n_init=5).fit_predict(matrix)
        if len(set(labels)) < 2:
            continue
        scores[k] = round(float(silhouette_score(matrix, labels)), 4)
        labels_by_k[k] = labels

    if not scores:
        return {"k": None, "score": None, "scores": {}, "labels": [0] * len(matrix)}

    best_k = max(scores, key=scores.get)
    return {
        "k": best_k,
        "score": scores[best_k],
        "scores": scores,
        "labels": [int(label) for label in labels_by_k[best_k]],
    }


def _catalog_galaxy_map():
    try:
        index = _catalog_index()
    except ValueError:
        return None

    svd = TruncatedSVD(n_components=2, random_state=42)
    coords = svd.fit_transform(index["matrix"])
    clusters = cluster_catalog()

    titles = [book_title(cid) for cid in index["ids"]]

    return {
        "mode": "catalog",
        "ids": index["ids"],
        "x": [float(point[0]) for point in coords],
        "y": [float(point[1]) for point in coords],
        "titles": titles,
        "categories": [COLLECTION[cid] for cid in index["ids"]],
        "category_order": sorted(set(COLLECTION.values())),
        "cluster_k": clusters["k"],
        "cluster_score": clusters["score"],
        "cluster_labels": clusters["labels"],
        "scores": [None] * len(index["ids"]),
        "ranks": [None] * len(index["ids"]),
        "source_size": len(index["ids"]),
    }


_FULL_INDEX = None


def _full_index():
    global _FULL_INDEX
    if os.getenv("BOOKWORM_DISABLE_FULL_INDEX") == "1":
        return None
    if _FULL_INDEX is None and FULL_INDEX_PATH.exists():
        try:
            _FULL_INDEX = joblib.load(FULL_INDEX_PATH)
        except Exception as error:
            sys.stderr.write(
                f"bookworm: warning: full corpus index is not readable yet "
                f"({error}); falling back to the 21-book catalog\n"
            )
            return None
    return _FULL_INDEX


def _query_full_vector(full, book):
    query = full["vectorizer"].transform([book.clean])
    vector = full["svd"].transform(query)[0].astype(np.float32)
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector /= norm
    return vector


def _full_similarity_scores(full, book):
    query = _query_full_vector(full, book)
    return query, full["matrix"] @ query


def _rank_category(rank):
    if rank <= 25:
        return "Closest 25"
    if rank <= 100:
        return "Close 100"
    return "Nearby context"


def _project_vectors(vectors):
    if len(vectors) < 2:
        return np.zeros((len(vectors), 2), dtype=np.float32)
    return TruncatedSVD(n_components=2, random_state=42).fit_transform(vectors)


def _full_galaxy_map(book, limit=GALAXY_NEIGHBOR_LIMIT):
    full = _full_index()
    if full is None:
        return None

    query, sim_scores = _full_similarity_scores(full, book)
    order = np.argsort(sim_scores)[::-1]
    selected = []
    for idx in order:
        cid = full["ids"][idx]
        if str(cid) == str(book.id):
            continue
        selected.append(idx)
        if len(selected) >= limit:
            break

    neighbor_vectors = full["matrix"][selected]
    vectors = np.vstack([query.reshape(1, -1), neighbor_vectors]).astype(np.float32)
    coords = _project_vectors(vectors)
    clusters = _cluster_vectors(vectors)

    ids = [int(book.id)] + [int(full["ids"][idx]) for idx in selected]
    ranks = [0] + list(range(1, len(selected) + 1))
    categories = ["Selected book"] + [_rank_category(rank) for rank in ranks[1:]]
    scores = [1.0] + [float(sim_scores[idx]) for idx in selected]

    return {
        "mode": "full",
        "ids": ids,
        "x": [float(point[0]) for point in coords],
        "y": [float(point[1]) for point in coords],
        "titles": [_safe_title(cid) for cid in ids],
        "categories": categories,
        "category_order": ["Closest 25", "Close 100", "Nearby context"],
        "cluster_k": clusters["k"],
        "cluster_score": clusters["score"],
        "cluster_labels": clusters["labels"],
        "scores": scores,
        "ranks": ranks,
        "focus_index": 0,
        "source_size": len(full["ids"]),
        "neighbor_limit": limit,
    }


def galaxy_map(book=None, limit=GALAXY_NEIGHBOR_LIMIT):
    if book is not None:
        full_galaxy = _full_galaxy_map(book, limit=limit)
        if full_galaxy is not None:
            return full_galaxy
    return _catalog_galaxy_map()


def build_full_index(n_components=300):
    ids = sorted(
        int(p.stem[2:]) for p in data.TEXTS_DIR.glob("pg*.txt") if p.stem[2:].isdigit()
    )
    total = len(ids)
    if total == 0:
        sys.stderr.write("[similar] no texts found, nothing to index\n")
        return None

    def corpus():
        for i, cid in enumerate(ids):
            if i % 200 == 0:
                sys.stderr.write(f"\r[similar] vectorizing {i}/{total}")
                sys.stderr.flush()
            try:
                yield cleaner(data.load_text(cid))
            except (OSError, UnicodeError):
                yield ""

    vectorizer = TfidfVectorizer(
        max_features=10000, max_df=0.8,
        stop_words=sklearn_stop_words("en"), dtype=np.float32,
    )
    tfidf = vectorizer.fit_transform(corpus())
    sys.stderr.write(f"\r[similar] vectorized {total}/{total} — tfidf {tfidf.shape}\n")

    sys.stderr.write(f"[similar] LSA reduction to {n_components} dims...\n")
    svd = TruncatedSVD(n_components=n_components, random_state=42)
    reduced = svd.fit_transform(tfidf).astype(np.float32)
    norms = np.linalg.norm(reduced, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    reduced /= norms

    index = {"ids": ids, "vectorizer": vectorizer, "svd": svd, "matrix": reduced}
    FULL_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = FULL_INDEX_PATH.with_suffix(FULL_INDEX_PATH.suffix + ".tmp")
    joblib.dump(index, temp_path, compress=3)
    temp_path.replace(FULL_INDEX_PATH)
    sys.stderr.write(f"[similar] index saved to {FULL_INDEX_PATH}\n")
    return index


def _safe_title(cid):
    record = _read_catalog(str(cid))
    if record and record.get("title"):
        return record["title"]
    try:
        return book_title(cid)
    except SystemExit:
        return f"Gutenberg #{cid}"


def similar(book):
    full = _full_index()
    if full is not None:
        _, sim_scores = _full_similarity_scores(full, book)
        order = np.argsort(sim_scores)[::-1]
        titles = []
        for idx in order:
            cid = full["ids"][idx]
            if str(cid) == str(book.id):
                continue
            titles.append(_safe_title(cid))
            if len(titles) == 5:
                break
        return titles

    try:
        index = _catalog_index()
    except ValueError:
        return []

    query = index["vectorizer"].transform([book.clean])
    sim_scores = cosine_similarity(query, index["matrix"])[0]

    scored_books = [
        (cid, score)
        for cid, score in zip(index["ids"], sim_scores)
        if str(cid) != str(book.id)
    ]
    scored_books.sort(key=lambda x: x[1], reverse=True)

    return [book_title(cid) for cid, _ in scored_books[:5]]


def _bert_catalog_index():
    def _bert(ids):
        vectors = []
        for cid in ids:
            book = Book(cid)
            book.__dict__["raw"] = data.load_text(cid)
            book.__dict__["clean"] = cleaner(book.raw)
            vectors.append(_book_embedding(book))
        matrix = np.vstack(vectors).astype(np.float32)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return {"matrix": matrix / norms}
    return _build_catalog_index(BERT_INDEX_PATH, _bert)


def similar_bert(book):
    start = time.perf_counter()
    index = _bert_catalog_index()
    query = _book_embedding(book).reshape(1, -1)
    scores = cosine_similarity(query, index["matrix"])[0]

    scored = [
        (cid, score)
        for cid, score in zip(index["ids"], scores)
        if str(cid) != str(book.id)
    ]
    scored.sort(key=lambda item: item[1], reverse=True)

    titles = [book_title(cid) for cid, _ in scored[:5]]

    return {
        "similar": titles,
        **runtime_metadata(start),
        "sentences_per_book": MAX_SENTENCES_PER_BOOK,
    }


if __name__ == "__main__":
    build_full_index()
