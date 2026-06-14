#!/usr/bin/env python3

import sys
from collections import Counter

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler

from core import cache
from pipeline.utils import extract_samples
from pipeline.syntax import (
    AUTHOR_BOOKS,
    syntax,
    profile_text,
    _flat_features,
    CACHE_VERSION as SYNTAX_CACHE_VERSION
)

MODEL_VERSION = 1
MODEL_PATH = cache.CORPUS_DIR / f"attribute_model__v{MODEL_VERSION}.joblib"
EXTRACT_SENTENCES = 30
MAX_EXTRACTS_PER_BOOK = 40


def _train_model():
    from core.book import Book

    sys.stderr.write("[attribute] training authorship model...\n")

    X_rows = []
    y_labels = []
    feature_names = None

    for author, book_ids in AUTHOR_BOOKS.items():
        for bid in book_ids:
            book = Book(bid)
            profile = cache.cached(
                bid, "syntax", lambda b=book: syntax(b), version=SYNTAX_CACHE_VERSION
            )

            extracts = extract_samples(
                book.sentences, EXTRACT_SENTENCES, MAX_EXTRACTS_PER_BOOK
            )
            sys.stderr.write(
                f"  {author} #{bid}: {len(extracts)} extracts\n"
            )

            for text in extracts:
                p = profile_text(text, book.lang)
                if p is None:
                    continue
                feats = _flat_features(p)
                if feature_names is None:
                    feature_names = list(feats)
                X_rows.append(list(feats.values()))
                y_labels.append(author)

    if not X_rows or feature_names is None:
        raise LookupError("not enough syntax samples to train the attribution model")

    X = np.array(X_rows)
    y = np.array(y_labels)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    clf = LogisticRegression(max_iter=1000, random_state=42, solver="lbfgs")

    class_counts = Counter(y_labels)
    n_splits = min(5, min(class_counts.values()))
    if n_splits < 2:
        raise LookupError("not enough samples per author to cross-validate attribution")

    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    scores = cross_val_score(clf, X_scaled, y, cv=cv, scoring="accuracy")
    cv_mean = round(float(np.mean(scores)), 2)
    cv_std = round(float(np.std(scores)), 2)
    sys.stderr.write(
        f"[attribute] CV accuracy: {cv_mean} ± {cv_std} ({len(X)} samples)\n"
    )

    clf.fit(X_scaled, y)

    coefs = clf.coef_
    classes = list(clf.classes_)
    top_features = []
    for i, cls in enumerate(classes):
        abs_coefs = np.abs(coefs[i])
        top_idx = np.argsort(abs_coefs)[-3:][::-1]
        for idx in top_idx:
            top_features.append(
                f"{cls}: {feature_names[idx]} ({coefs[i][idx]:+.3f})"
            )

    model = {
        "scaler": scaler,
        "clf": clf,
        "feature_names": feature_names,
        "cv_accuracy": f"{cv_mean} ± {cv_std}",
        "top_features": top_features,
        "training_samples": len(X),
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    sys.stderr.write(f"[attribute] model saved to {MODEL_PATH}\n")
    return model


def _load_model():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return _train_model()


def attribute(text):
    from nltk import sent_tokenize

    sentences = sent_tokenize(text)
    if len(sentences) < 5:
        sys.stderr.write(
            "bookworm: warning: text has fewer than 5 sentences — "
            "attribution may be unreliable\n"
        )

    profile = profile_text(text)
    if profile is None:
        raise LookupError(
            "text is too short for syntax analysis (need at least 3 sentences)"
        )

    model = _load_model()
    feats = _flat_features(profile)
    X = np.array([list(feats.values())])
    X_scaled = model["scaler"].transform(X)

    proba = model["clf"].predict_proba(X_scaled)[0]
    classes = list(model["clf"].classes_)
    predicted = classes[int(np.argmax(proba))]

    return {
        "author": predicted,
        "proba": {cls: round(float(p), 4) for cls, p in zip(classes, proba)},
        "cv_accuracy": model["cv_accuracy"],
        "top_features": model["top_features"],
    }
