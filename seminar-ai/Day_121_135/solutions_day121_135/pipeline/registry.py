#!/usr/bin/env python3

from dataclasses import dataclass
from importlib import import_module

from core import cache


@dataclass(frozen=True)
class PipelineCommand:
    module: str
    function: str
    cache_task: str | None = None


BOOK_COMMANDS = {
    "lexdiv": PipelineCommand("lexdiv", "lexdiv", "lexdiv"),
    "lexdiv-plus": PipelineCommand("lexdiv", "lexdiv_plus", "lexdiv-plus"),
    "topics": PipelineCommand("topics", "topics", "topics"),
    "entities": PipelineCommand("entities", "entities", "entities"),
    "summarize": PipelineCommand("summarize", "summarize", "summarize"),
    "similar": PipelineCommand("similar", "similar", "similar"),
    "compare": PipelineCommand("compare", "compare", "compare"),
    "arc": PipelineCommand("arc", "arc", "arc"),
    "syntax": PipelineCommand("syntax", "syntax", "syntax"),
    "eval-summary": PipelineCommand("rouge", "eval_summary"),
    "summarize-bert": PipelineCommand("summarize", "summarize_bert", "summarize-bert"),
    "similar-bert": PipelineCommand("similar", "similar_bert", "similar-bert"),
    "topics-bert": PipelineCommand("topics", "topics_bert", "topics-bert"),
    "card": PipelineCommand("card", "card"),
    "report": PipelineCommand("report", "report"),
}

ARG_COMMANDS = {
    "attribute": PipelineCommand("attribute", "attribute"),
    "authorsyntax": PipelineCommand("syntax", "authorsyntax"),
}


def _resolve(command):
    module = import_module(f"pipeline.{command.module}")
    return module, getattr(module, command.function)


def run_book_command(book, flag):
    command = BOOK_COMMANDS[flag]
    module, feature = _resolve(command)
    if command.cache_task is None:
        return feature(book)
    version = getattr(module, "CACHE_VERSION", None)
    return cache.cached(book.id, command.cache_task, lambda: feature(book), version=version)


def run_arg_command(flag, payload):
    _, feature = _resolve(ARG_COMMANDS[flag])
    return feature(payload)
