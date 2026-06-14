#!/usr/bin/env python3

import re
import string

from nltk import pos_tag, sent_tokenize, word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import PorterStemmer, WordNetLemmatizer

NLTK_STOPWORD_LANG = {
    "en": "english", "fr": "french", "de": "german", "es": "spanish",
    "it": "italian", "pt": "portuguese", "nl": "dutch", "ru": "russian",
}


def stopword_list(lang="en"):
    name = NLTK_STOPWORD_LANG.get(lang, "english")
    try:
        return list(stopwords.words(name))
    except (LookupError, OSError):
        return list(stopwords.words("english"))


def sklearn_stop_words(lang="en"):
    if lang == "en":
        return "english"
    return stopword_list(lang)


def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith("J"):
        return wordnet.ADJ
    if treebank_tag.startswith("V"):
        return wordnet.VERB
    if treebank_tag.startswith("R"):
        return wordnet.ADV
    return wordnet.NOUN


def cleaner(text, lower=False):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(
        r"^.*?\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*",
        "", text, flags=re.DOTALL | re.IGNORECASE,
    )
    text = re.sub(
        r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*.*$",
        "", text, flags=re.DOTALL | re.IGNORECASE,
    )
    text = text.strip()
    if lower:
        text = text.lower()
    return text


def tokenizer(text, sent=False, stop=False, punct=False, lang="en"):
    tokens = sent_tokenize(text) if sent else word_tokenize(text)
    if stop:
        stops = set(stopword_list(lang))
        tokens = [w for w in tokens if w.lower() not in stops]
    if punct:
        tokens = [w for w in tokens if w not in string.punctuation]
    return tokens


def postag(text):
    return pos_tag(word_tokenize(text))


def normalize(text, stem=False):
    tokens = word_tokenize(text)
    if stem:
        return [PorterStemmer().stem(w) for w in tokens]
    lemmatizer = WordNetLemmatizer()
    tagged = pos_tag(tokens)
    return [lemmatizer.lemmatize(w, get_wordnet_pos(tag)) for w, tag in tagged]
