#!/usr/bin/env python3

import nltk

PACKAGES = [
    "punkt",
    "punkt_tab",
    "stopwords",
    "wordnet",
    "averaged_perceptron_tagger",
    "averaged_perceptron_tagger_eng",
    "vader_lexicon",
]


def download_nltk_data():
    for package in PACKAGES:
        nltk.download(package, quiet=False)


if __name__ == "__main__":
    download_nltk_data()
    print("NLTK setup complete.")
