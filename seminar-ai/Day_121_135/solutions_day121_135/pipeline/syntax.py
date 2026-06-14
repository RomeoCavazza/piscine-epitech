#!/usr/bin/env python3

import csv
import random
import sys
from collections import Counter, defaultdict

import numpy as np

from core import cache
from core.tools import COLLECTION_PATH
from pipeline.utils import chunk_sentences, load_spacy

CACHE_VERSION = 1
SAMPLE_SENTENCES = 1500

def _load_author_books():
    authors = defaultdict(list)
    if not COLLECTION_PATH.exists():
        return {}
    with COLLECTION_PATH.open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            book_id = int(row["Text#"])
            author_field = row["Authors"]
            if author_field:
                last_name = author_field.split(",")[0].strip()
                authors[last_name].append(book_id)
    return {k: v for k, v in authors.items() if len(v) >= 2}

AUTHOR_BOOKS = _load_author_books()

_PARSER_DISABLE = ["ner", "lemmatizer"]


def _sample_sentences(sentences, limit):
    if len(sentences) <= limit:
        return sentences
    rng = random.Random(42)
    indices = sorted(rng.sample(range(len(sentences)), limit))
    return [sentences[i] for i in indices]


def _tree_depth(token):
    depth = 0
    while token.head != token:
        depth += 1
        token = token.head
    return depth


def _analyze_doc(doc):
    surface = {
        "lengths": [],
        "pos_counts": Counter(),
        "punct_count": 0,
        "token_count": 0,
    }
    grammar = {
        "subordinators_per_sent": [],
        "has_passive": [],
        "tree_depths": [],
        "nsubj_per_sent": [],
        "dobj_per_sent": [],
        "advmod_per_sent": [],
    }

    for sent in doc.sents:
        tokens = [t for t in sent if not t.is_space]
        words = [t for t in tokens if not t.is_punct]
        n_words = len(words)
        if n_words < 3:
            continue

        surface["lengths"].append(n_words)
        for token in tokens:
            surface["pos_counts"][token.pos_] += 1
            if token.is_punct:
                surface["punct_count"] += 1
        surface["token_count"] += len(tokens)

        subordinators = sum(
            1 for t in tokens if t.dep_ == "mark" or t.pos_ == "SCONJ"
        )
        grammar["subordinators_per_sent"].append(subordinators / n_words)

        passive = any(t.dep_ in ("nsubjpass", "auxpass") for t in tokens)
        grammar["has_passive"].append(passive)

        max_depth = max((_tree_depth(t) for t in tokens), default=0)
        grammar["tree_depths"].append(max_depth)

        grammar["nsubj_per_sent"].append(
            sum(1 for t in tokens if t.dep_ == "nsubj") / n_words
        )
        grammar["dobj_per_sent"].append(
            sum(1 for t in tokens if t.dep_ == "dobj") / n_words
        )
        grammar["advmod_per_sent"].append(
            sum(1 for t in tokens if t.dep_ == "advmod") / n_words
        )

    return surface, grammar


def _build_profile(surfaces, grammars):
    all_lengths = []
    total_pos = Counter()
    total_punct = 0
    total_tokens = 0
    all_sub = []
    all_passive = []
    all_depth = []
    all_nsubj = []
    all_dobj = []
    all_advmod = []

    for s in surfaces:
        all_lengths.extend(s["lengths"])
        total_pos.update(s["pos_counts"])
        total_punct += s["punct_count"]
        total_tokens += s["token_count"]

    for g in grammars:
        all_sub.extend(g["subordinators_per_sent"])
        all_passive.extend(g["has_passive"])
        all_depth.extend(g["tree_depths"])
        all_nsubj.extend(g["nsubj_per_sent"])
        all_dobj.extend(g["dobj_per_sent"])
        all_advmod.extend(g["advmod_per_sent"])

    n = len(all_lengths)
    if n == 0:
        return None

    lengths_arr = np.array(all_lengths)
    short = int(np.sum(lengths_arr < 10))
    medium = int(np.sum((lengths_arr >= 10) & (lengths_arr <= 30)))
    long_ = int(np.sum(lengths_arr > 30))

    pos_total = sum(total_pos.values()) or 1
    pos_dist = {k: round(v / pos_total, 4) for k, v in total_pos.most_common()}

    surface = {
        "mean_sentence_length": round(float(np.mean(lengths_arr)), 2),
        "median_sentence_length": round(float(np.median(lengths_arr)), 2),
        "sentence_length_distribution": {
            "short": round(short / n, 4),
            "medium": round(medium / n, 4),
            "long": round(long_ / n, 4),
        },
        "pos_distribution": pos_dist,
        "punctuation_density": round(total_punct / total_tokens, 4) if total_tokens else 0.0,
    }

    grammar = {
        "subordination_rate": round(float(np.mean(all_sub)), 4) if all_sub else 0.0,
        "passive_ratio": round(sum(all_passive) / len(all_passive), 4) if all_passive else 0.0,
        "mean_tree_depth": round(float(np.mean(all_depth)), 2) if all_depth else 0.0,
        "nsubj_per_sentence": round(float(np.mean(all_nsubj)), 4) if all_nsubj else 0.0,
        "dobj_per_sentence": round(float(np.mean(all_dobj)), 4) if all_dobj else 0.0,
        "advmod_per_sentence": round(float(np.mean(all_advmod)), 4) if all_advmod else 0.0,
    }

    return {"surface": surface, "grammar": grammar, "sentences_analyzed": n}


def _profile_sentences(sentences, lang):
    nlp = load_spacy(lang, _PARSER_DISABLE)
    sampled = _sample_sentences(sentences, SAMPLE_SENTENCES)
    chunks = chunk_sentences(sampled)

    surfaces, grammars = [], []
    for doc in nlp.pipe(chunks, batch_size=4):
        s, g = _analyze_doc(doc)
        surfaces.append(s)
        grammars.append(g)

    return _build_profile(surfaces, grammars)


def syntax(book):
    profile = _profile_sentences(book.sentences, book.lang)
    if profile is None:
        raise LookupError(f"not enough sentences in book {book.id} for syntax analysis")
    return profile


def profile_text(text, lang="en"):
    from nltk import sent_tokenize

    sentences = sent_tokenize(text)
    if len(sentences) < 3:
        return None

    return _profile_sentences(sentences, lang)


def _flat_features(profile):
    s = profile["surface"]
    g = profile["grammar"]
    return {
        "mean_sent_len": s["mean_sentence_length"],
        "median_sent_len": s["median_sentence_length"],
        "short_ratio": s["sentence_length_distribution"]["short"],
        "medium_ratio": s["sentence_length_distribution"]["medium"],
        "long_ratio": s["sentence_length_distribution"]["long"],
        "punct_density": s["punctuation_density"],
        "subordination": g["subordination_rate"],
        "passive": g["passive_ratio"],
        "tree_depth": g["mean_tree_depth"],
        "nsubj": g["nsubj_per_sentence"],
        "dobj": g["dobj_per_sentence"],
        "advmod": g["advmod_per_sentence"],
    }


def authorsyntax(author_name):
    matched = None
    for key in AUTHOR_BOOKS:
        if key.lower() == author_name.lower() or key.lower() in author_name.lower():
            matched = key
            break

    if matched is None:
        raise LookupError(
            f"unknown author '{author_name}'. "
            f"Supported: {', '.join(sorted(AUTHOR_BOOKS))}"
        )

    from core.book import Book

    author_ids = set(AUTHOR_BOOKS[matched])
    other_ids = set()
    for key, ids in AUTHOR_BOOKS.items():
        if key != matched:
            other_ids.update(ids)

    sys.stderr.write(f"[syntax] analyzing {matched} ({len(author_ids)} books)...\n")
    author_profiles = []
    for bid in sorted(author_ids):
        book = Book(bid)
        profile = cache.cached(bid, "syntax", lambda b=book: syntax(b), version=CACHE_VERSION)
        author_profiles.append(profile)

    sys.stderr.write(f"[syntax] analyzing rest of collection ({len(other_ids)} books)...\n")
    other_profiles = []
    for bid in sorted(other_ids):
        book = Book(bid)
        profile = cache.cached(bid, "syntax", lambda b=book: syntax(b), version=CACHE_VERSION)
        other_profiles.append(profile)

    author_feats = [_flat_features(p) for p in author_profiles]
    other_feats = [_flat_features(p) for p in other_profiles]

    keys = list(author_feats[0].keys())
    author_means = {k: round(np.mean([f[k] for f in author_feats]), 4) for k in keys}
    other_means = {k: round(np.mean([f[k] for f in other_feats]), 4) for k in keys}
    deltas = {k: round(author_means[k] - other_means[k], 4) for k in keys}

    _save_radar(matched, author_means, other_means, keys)

    return {
        "author": matched,
        "books_analyzed": len(author_ids),
        "author_profile": author_means,
        "collection_profile": other_means,
        "deltas": deltas,
    }


def _save_radar(author, author_means, other_means, keys):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir = cache.CORPUS_DIR / "authorsyntax"
    out_dir.mkdir(parents=True, exist_ok=True)

    labels = [k.replace("_", "\n") for k in keys]
    n = len(keys)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles.append(angles[0])

    def _normalize(values, all_values):
        mins = {k: min(v[k] for v in all_values) for k in keys}
        maxs = {k: max(v[k] for v in all_values) for k in keys}
        return [
            (values[k] - mins[k]) / (maxs[k] - mins[k])
            if maxs[k] != mins[k] else 0.5
            for k in keys
        ]

    all_dicts = [author_means, other_means]
    author_norm = _normalize(author_means, all_dicts)
    other_norm = _normalize(other_means, all_dicts)
    a_norm = author_norm + [author_norm[0]]
    o_norm = other_norm + [other_norm[0]]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#0f172a")

    ax.plot(angles, a_norm, "o-", color="#38bdf8", linewidth=2, label=author)
    ax.fill(angles, a_norm, color="#38bdf8", alpha=0.15)
    ax.plot(angles, o_norm, "o-", color="#f472b6", linewidth=2, label="Rest of collection")
    ax.fill(angles, o_norm, color="#f472b6", alpha=0.15)

    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=8, color="#94a3b8")
    ax.tick_params(axis="y", colors="#334155")
    ax.spines["polar"].set_color("#334155")
    ax.grid(color="#334155", linewidth=0.5)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=10,
              facecolor="#1e293b", edgecolor="#334155", labelcolor="#e2e8f0")
    ax.set_title(f"Syntax profile — {author}", fontsize=14, color="#e2e8f0", pad=20)

    path = out_dir / f"{author.lower()}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    sys.stderr.write(f"[syntax] radar chart saved to {path}\n")
