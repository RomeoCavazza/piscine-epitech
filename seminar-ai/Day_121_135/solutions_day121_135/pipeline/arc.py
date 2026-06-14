#!/usr/bin/env python3

from nltk import sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from pipeline.utils import split_chapters

CACHE_VERSION = 2


def arc(book):
    sections = split_chapters(book.clean)
    if not sections:
        return {}

    analyzer = SentimentIntensityAnalyzer()
    result = {}
    for index, section in enumerate(sections, start=1):
        sentences = sent_tokenize(section)
        if not sentences:
            result[index] = 0.0
            continue
        scores = [analyzer.polarity_scores(sentence)["compound"] for sentence in sentences]
        result[index] = round(sum(scores) / len(scores), 4)
    return result
