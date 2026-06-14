#!/usr/bin/env python3

from dataclasses import dataclass
from functools import cached_property

from nltk import sent_tokenize, word_tokenize

from core import data
from core.nlp import cleaner
from core.tools import info as _info, language


@dataclass
class Book:
    id: int

    @cached_property
    def raw(self):
        return data.load_text(self.id)

    @cached_property
    def info(self):
        return _info(self.id)

    @cached_property
    def lang(self):
        return language(self.id)

    @cached_property
    def clean(self):
        return cleaner(self.raw)

    @cached_property
    def sentences(self):
        return sent_tokenize(self.clean)

    @cached_property
    def tokens(self):
        return word_tokenize(self.clean)

    @cached_property
    def words(self):
        return [token.lower() for token in self.tokens if token.isalpha()]
