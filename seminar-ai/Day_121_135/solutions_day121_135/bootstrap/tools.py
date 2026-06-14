#!/usr/bin/env python3

import sys
import re
import requests
import string
import csv
from pathlib import Path
from argparse import ArgumentParser
from nltk import sent_tokenize, word_tokenize, pos_tag
from nltk.corpus import stopwords, wordnet
from nltk.stem import PorterStemmer, WordNetLemmatizer

BOOTSTRAP_DIR = Path(__file__).resolve().parent
CATALOG_PATH = BOOTSTRAP_DIR / "catalog.csv"

class EpitechArgumentParser(ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write(f"{self.prog}: error: {message}\n")
        sys.exit(84)

def get_args():
    parser = EpitechArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--info", type=int)
    group.add_argument("--download", type=int)
    group.add_argument("--clean", type=str)
    group.add_argument("--tokenize", type=str)
    group.add_argument("--postag", type=str)
    group.add_argument("--normalize", type=str)

    parser.add_argument("--lower", action="store_true")
    parser.add_argument("--sent", action="store_true")
    parser.add_argument("--stop", action="store_true")
    parser.add_argument("--punct", action="store_true")
    parser.add_argument("--stem", action="store_true")

    return parser.parse_args()

def info(book_id):
    if not CATALOG_PATH.exists():
        print("Error: catalog.csv not found.")
        sys.exit(84)
    with CATALOG_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Text#"] == str(book_id):
                return {
                    "id": row["Text#"],
                    "title": row["Title"],
                    "authors": row["Authors"],
                    "bookshelves": row["Bookshelves"]
                }
    print("Error: Book not found.")
    sys.exit(84)

def downloader(book_id):
    url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
    response = requests.get(url)
    if response.status_code == 200:
        with open(f"{book_id}.txt", "w", encoding="utf-8") as f:
            f.write(response.text)
        return
    print("Error: Book not found.")
    sys.exit(84)

def cleaner(text, lower=False):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'^.*?\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*.*$', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = text.strip()
    if lower:
        text = text.lower()
    return text

def tokenizer(text, sent=False, stop=False, punct=False):
    tokens = sent_tokenize(text) if sent else word_tokenize(text)
    if stop:
        tokens = [word for word in tokens if word.lower() not in stopwords.words("english")]
    if punct:
        tokens = [word for word in tokens if word not in string.punctuation]
    return tokens

def postag(text):
    tokens = word_tokenize(text)
    return pos_tag(tokens)

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'): return wordnet.ADJ
    elif treebank_tag.startswith('V'): return wordnet.VERB
    elif treebank_tag.startswith('N'): return wordnet.NOUN
    elif treebank_tag.startswith('R'): return wordnet.ADV
    else: return wordnet.NOUN

def normalize(text, stem=False):
    tokens = word_tokenize(text)
    if stem:
        return [PorterStemmer().stem(word) for word in tokens]
    
    lemmatizer = WordNetLemmatizer()
    tagged = pos_tag(tokens)
    return [lemmatizer.lemmatize(word, get_wordnet_pos(tag)) for word, tag in tagged]

def main():
    args = get_args()

    if args.info is not None:
        text = info(args.info)
        print(text)
    elif args.download is not None:
        downloader(args.download)
    elif args.clean is not None:
        text = cleaner(args.clean, lower=args.lower)
        print(text)
    elif args.tokenize is not None:
        text = tokenizer(args.tokenize, sent=args.sent, stop=args.stop, punct=args.punct)
        print(text)
    elif args.postag is not None:
        text = postag(args.postag)
        print(text)
    elif args.normalize is not None:
        text = normalize(args.normalize, stem=args.stem)
        print(text)

if __name__ == "__main__":
    main()
