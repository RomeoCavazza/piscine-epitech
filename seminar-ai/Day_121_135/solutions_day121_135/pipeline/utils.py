#!/usr/bin/env python3

import re

CHUNK_SIZE = 100000

SPACY_MODELS = {
    "en": "en_core_web_sm",
    "fr": "fr_core_news_sm",
    "de": "de_core_news_sm",
    "es": "es_core_news_sm",
    "it": "it_core_news_sm",
    "pt": "pt_core_news_sm",
    "nl": "nl_core_news_sm",
}

MIN_SECTION_WORDS = 80

_NLP_CACHE = {}


def load_spacy(lang, disable):
    name = SPACY_MODELS.get(lang, "en_core_web_sm")
    key = (name, tuple(sorted(disable)))
    if key not in _NLP_CACHE:
        import spacy
        try:
            _NLP_CACHE[key] = spacy.load(name, disable=disable)
        except OSError:
            raise OSError(
                f"spaCy model '{name}' is not installed. "
                f"Run: python -m spacy download {name}"
            )
    return _NLP_CACHE[key]


HEADING_PATTERNS = [
    re.compile(r"(?im)^\s*chapter\s+(?:[ivxlcdm]+|\d+)\.?(?:\s+.*)?$"),
    re.compile(r"(?im)^\s*book\s+(?:[ivxlcdm]+|\d+)\.?(?:\s+.*)?$"),
    re.compile(
        r"(?im)^\s*part\s+(?:[ivxlcdm]+|\d+|one|two|three|four|five|six|"
        r"seven|eight|nine|ten)\.?(?:\s+.*)?$"
    ),
    re.compile(r"(?m)^\s*[IVXLCDM]+\.\s+[A-Z][A-Za-z0-9 .,''\-]{3,70}$"),
    re.compile(r"(?m)^\s*[IVXLCDM]{1,10}\.?\s*$"),
    re.compile(r"(?m)^\s*[A-Z][A-Z \t]{4,60}\s*$"),
]


def chunk_sentences(sentences, chunk_size=CHUNK_SIZE):
    chunks, current, length = [], [], 0
    for sentence in sentences:
        sentence = " ".join(sentence.split())
        if not sentence:
            continue
        if current and length + len(sentence) + 1 > chunk_size:
            chunks.append(" ".join(current))
            current, length = [], 0
        current.append(sentence)
        length += len(sentence) + 1
    if current:
        chunks.append(" ".join(current))
    return chunks


def extract_samples(sentences, extract_size=30, max_extracts=40):
    if len(sentences) < extract_size:
        return [" ".join(sentences)]

    extracts = []
    step = max(1, len(sentences) // max_extracts)
    for start in range(0, len(sentences) - extract_size + 1, step):
        chunk = " ".join(sentences[start : start + extract_size])
        extracts.append(chunk)
        if len(extracts) >= max_extracts:
            break
    return extracts


def _split_on_pattern(text, pattern):
    matches = list(pattern.finditer(text))
    if len(matches) < 2:
        return None

    chapters = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        chapter = text[start:end].strip()
        if chapter:
            chapters.append(chapter)

    long_enough = [
        chapter for chapter in chapters if len(chapter.split()) >= MIN_SECTION_WORDS
    ]
    return long_enough or chapters or None


FALLBACK_SECTIONS = 12


def _split_evenly(text, target=FALLBACK_SECTIONS):
    """Segment a heading-less book into ~equal windows by word count.

    Books without recognizable chapter markers would otherwise collapse to a
    single section, which makes the narrative arc undrawable (one point) and
    flattens topic segmentation. Splitting by position keeps both meaningful.
    """
    words = text.split()
    if len(words) < MIN_SECTION_WORDS * 2:
        return [text]
    count = min(target, len(words) // MIN_SECTION_WORDS)
    size = len(words) // count
    bounds = [size * index for index in range(count)] + [len(words)]
    sections = [" ".join(words[bounds[i]:bounds[i + 1]]) for i in range(count)]
    return [section for section in sections if section.strip()]


def split_chapters(text):
    for pattern in HEADING_PATTERNS:
        result = _split_on_pattern(text, pattern)
        # A single "section" means the matches were clustered (e.g. a table of
        # contents) and the body never got split — reject it and keep trying,
        # otherwise the narrative arc collapses to one undrawable point.
        if result and len(result) >= 2:
            return result
    text = text.strip()
    return _split_evenly(text) if text else []
