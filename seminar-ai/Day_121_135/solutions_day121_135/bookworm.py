#!/usr/bin/env python3

### IMPORTS

import re
import sys
import csv
import networkx as nx
import requests
import string

from sklearn import *
from nltk import *

from argparse import ArgumentParser

from nltk import sent_tokenize, word_tokenize, pos_tag
from nltk.corpus import stopwords, wordnet
from nltk.stem import PorterStemmer, WordNetLemmatizer


### FUNCTIONS

def get_args():
    parser = ArgumentParser(prog="bookworm")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--lexdiv", type=int, metavar="ID")
    group.add_argument("--topics", type=int, metavar="ID")
    group.add_argument("--entities", type=int, metavar="ID")
    group.add_argument("--summarize", type=int, metavar="ID")
    group.add_argument("--similar", type=int, metavar="ID")
    group.add_argument("--card", type=int, metavar="ID")

    args = parser.parse_args()
    return args

def info(book_id):

    text = text.read((string) (book_id))
    content = ""
    Result = {}

    for word in text.split():

        if word.contains.toLowerCase("chapter"):
            for row in content:
                if row["Text#"] == str(book_id):
                    return {
                        "id": row["Text#"],
                        "title": row["Title"],
                        "authors": row["Authors"],
                        "bookshelves": row["Bookshelves"]
                    }
        else:
            content += word + " "

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'): return wordnet.ADJ
    elif treebank_tag.startswith('V'): return wordnet.VERB
    elif treebank_tag.startswith('N'): return wordnet.NOUN
    elif treebank_tag.startswith('R'): return wordnet.ADV
    else: return wordnet.NOUN

def cleaner(text, lower=False):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'^.*?\*\*\* START OF THE PROJECT GUTENBERG EBOOK.*?\*\*\*', '', text, flags=re.DOTALL)
    text = re.sub(r'\*\*\* END OF THE PROJECT GUTENBERG EBOOK.*?\*\*\*$', '', text, flags=re.DOTALL)
    if lower:
        text = text.lower()
    return text

def lexdiv(book_id):
    # {
    #     "tok":int,
    #     "typ":int,
    #     "hap":int,
    #     "ttr":float,
    #     "mwl":float,
    #     "mwf":float
    # }
    return

def topics(book_id):
    # top 10 topics with their weights
    # tf-idf + lsa
    # {1: list[str], 2: list[str], ...}
    text = text.read((string) (book_id))
    chapter_content = ""
    Result = {}

    for word in text.split():
        if "chapter" in word.lower():
            if chapter_content.strip():
                chapters.append(chapter_content.strip())
            chapter_content = ""
        else:
            chapter_content += word + " "

    if chapter_content.strip():
        chapters.append(chapter_content.strip())

    results = {}

    for i, chapter in enumerate(chapters, start=1):
        tokens = chapter.split()

        tokens = [
            t.strip(string.punctuation).lower()
            for t in tokens
            if t.strip(string.punctuation)
        ]

        tagged = pos_tag(tokens)
        lemmas = [
            lemmatizer.lemmatize(word, get_wordnet_pos(tag))
            for word, tag in tagged
            if word not in stop_words
        ]

        freq = Counter(lemmas).most_common(10)
        results[f"chapter_{i}"] = freq

    return results


def entities(book_id):
    # character maps and timeline of locations with
    # spacy NER + networkx for character relationships
    # {
    #     "characters": list[str],
    #     "location": list[str]
    # }
    return
    
def summarize(book_id):
    # summary = str(book_id) + ": " + str(title) + "\n\n" + str(summary)
    # if lightweight,
    #    extractive summarization (TextRank, LSA, LexRank, cluster-based)
    # else heavyweight,
    #    abstractive summarization (transformers, BART, T5)
    # str(book_id) + ": " + str(title) + "\n\n" + str(summary)
    return
    
def similar(book_id):
    # style-based decreseasing similarity (tf-idf vectors + cosine similarity)
    # ["id1", ..., "id5"]
    # ["title1", ..., "title5"]
    # ["category1", ..., "category5"]
    return

def card(book_id):
    # {
    #     info =
    #       "id": str,
    #       "authors": str,
    #       "bookshelves": str
    #     lexdiv = tok, typ, hap, ttr, mwl, mwf
    #     topics = [("topic1", 0.5), ("topic2", 0.3), ...]
    #     entities = {
    #         "characters": list[str],
    #         "location": list[str]
    #     }
    #     summary = str
    #     similar = {
    #         "ids": list[str],
    #         "titles": list[str],
    #         "categories": list[str]
    #     }
    return


## MAIN
def main():
    args = get_args()
    if args.lexdiv is not None:
        lexdiv(args.lexdiv)
    elif args.topics is not None:
        topics(args.topics)
    elif args.entities is not None:
        entities(args.entities)
    elif args.summarize is not None:
        summarize(args.summarize)
    elif args.similar is not None:
        similar(args.similar)
    elif args.card is not None:
        card(args.card)

if __name__ == "__main__":
    main()
