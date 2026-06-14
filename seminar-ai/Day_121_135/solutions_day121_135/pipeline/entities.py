#!/usr/bin/env python3

from collections import Counter

from pipeline.utils import chunk_sentences, CHUNK_SIZE, load_spacy

ENTITY_LABELS = {
    "PERSON": "characters",
    "PER": "characters",
    "GPE": "locations",
    "LOC": "locations",
}
LIMIT = 20
MIN_COUNT = 2
CACHE_VERSION = 1

_NER_DISABLE = ["tagger", "parser", "attribute_ruler", "lemmatizer", "tok2vec"]


def _extract_entities(chunks, nlp):
    entities = []
    for doc in nlp.pipe(chunks, batch_size=10):
        for ent in doc.ents:
            entities.append((ent.text, ent.label_))
    return entities


def _rank_entities(items, min_count, limit):
    counts = Counter(items)
    ranked = [item for item, count in counts.most_common() if count >= min_count]
    return ranked[:limit]


def entities(book):
    nlp = load_spacy(book.lang, _NER_DISABLE)
    chunks = chunk_sentences(book.sentences)
    extracted = _extract_entities(chunks, nlp)

    grouped = {"characters": [], "locations": []}
    for value, label in extracted:
        target = ENTITY_LABELS.get(label)
        if target is not None:
            grouped[target].append(value)

    return {
        "characters": _rank_entities(grouped["characters"], MIN_COUNT, LIMIT),
        "locations": _rank_entities(grouped["locations"], MIN_COUNT, LIMIT),
    }
