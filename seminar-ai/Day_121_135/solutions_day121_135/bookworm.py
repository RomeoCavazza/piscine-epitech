#!/usr/bin/env python3

import json
import sys
import time
from argparse import ArgumentParser
from pathlib import Path

from core import cache
from pipeline import registry as pipeline_registry

FEATURES = pipeline_registry.BOOK_COMMANDS
ARG_FEATURES = pipeline_registry.ARG_COMMANDS


class BookwormArgumentParser(ArgumentParser):

    def error(self, message):
        self.print_usage(sys.stderr)
        sys.stderr.write(f"{self.prog}: error: {message}\n")
        sys.exit(84)


def _format_topics(result):
    if not result:
        return "{}"

    lines = ["{"]
    items = list(result.items())
    for index, (section, words) in enumerate(items):
        comma = "," if index + 1 < len(items) else ""
        key = json.dumps(str(section), ensure_ascii=False)
        value = json.dumps(words, ensure_ascii=False)
        lines.append(f"  {key}: {value}{comma}")
    lines.append("}")
    return "\n".join(lines)


def get_args():
    parser = BookwormArgumentParser(prog="bookworm")
    group = parser.add_mutually_exclusive_group(required=True)
    for flag in FEATURES:
        group.add_argument(f"--{flag}", dest=flag.replace("-", "_"), type=int, metavar="ID")
    group.add_argument("--ask", nargs='+', metavar="ID", help="Ask the local assistant about a book")
    group.add_argument("--attribute", metavar="TEXT", help="Attribute text to an author")
    group.add_argument("--authorsyntax", metavar="NAME", help="Compare one author's syntax profile")
    group.add_argument("--author", metavar="NAME", help="Search books by author")
    group.add_argument("--category", metavar="TOPIC", help="Search books by topic")
    parser.add_argument("--limit", type=int, metavar="N",
                        help="Cap the number of books searched and downloaded by --author/--category")
    parser.add_argument("--profile", action="store_true", help="Generate a pyinstrument profiling report")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("argument --limit: must be a positive integer")
    return args


def _selected_flag(args):
    for flag in FEATURES:
        book_id = getattr(args, flag.replace("-", "_"))
        if book_id is not None:
            return flag, book_id

    if args.ask is not None:
        try:
            book_id = int(args.ask[0])
            query = " ".join(args.ask[1:])
            return "ask", (book_id, query)
        except ValueError:
            sys.stderr.write("bookworm: error: argument --ask: ID must be an integer\n")
            sys.exit(84)

    for flag in (*ARG_FEATURES, "author", "category"):
        value = getattr(args, flag)
        if value is not None:
            return flag, value

    return None, None


def dispatch(flag, payload, limit=None):
    if limit is not None and flag not in ("author", "category"):
        sys.stderr.write(f"bookworm: warning: --limit only applies to --author/--category, ignored for --{flag}\n")
        limit = None

    if flag == "ask":
        from core.book import Book

        book_id, query = payload
        book = Book(book_id)

        if not query.strip():
            try:
                query = input("Your question: ")
            except (EOFError, KeyboardInterrupt):
                return None
            if not query.strip():
                return None

        from core.tools import info
        book_info = info(str(book_id))
        book_title = book_info.get("title", f"Livre #{book_id}") if book_info else f"Livre #{book_id}"

        from assistant import agent_loop
        agent_loop(book, book_title, query)
        return None

    if flag in ("author", "category"):
        from core.data import download_many, search_books

        query_key = "topic" if flag == "category" else "author"
        books = search_books(**{query_key: payload}, limit=limit)
        if books:
            download_many([book["id"] for book in books])
        return books

    if flag in ARG_FEATURES:
        return pipeline_registry.run_arg_command(flag, payload)

    from core.book import Book

    book_id = payload
    book = Book(book_id)
    return pipeline_registry.run_book_command(book, flag)


def _print_result(flag, result):
    if result is None:
        return
    if flag == "topics":
        print(_format_topics(result))
    elif flag == "report":
        print(result)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


def _profile_output_path(flag, payload):
    if flag == "ask":
        book_id = payload[0]
        return cache.CORPUS_DIR / str(book_id) / "profile" / "profile_audit.html"
    if flag in FEATURES and isinstance(payload, int):
        return cache.CORPUS_DIR / str(payload) / "profile" / "profile_audit.html"
    return Path(__file__).resolve().parent / "data" / "output" / "reports" / "profile_audit.html"


def main():
    start_time = time.perf_counter()
    args = get_args()
    flag, payload = _selected_flag(args)

    profiler = None
    if getattr(args, "profile", False):
        try:
            from pyinstrument import Profiler
            profiler = Profiler()
            profiler.start()
        except ImportError:
            sys.stderr.write("bookworm: warning: pyinstrument is not installed. Run 'pip install pyinstrument'.\n")

    try:
        result = dispatch(flag, payload, limit=args.limit)
    except ModuleNotFoundError as error:
        sys.stderr.write(
            f"bookworm: error: missing dependency '{error.name}'. "
            "Install the project with 'pip install -e .' first.\n"
        )
        sys.exit(84)
    except ImportError as error:
        sys.stderr.write(
            "bookworm: error: "
            f"{error}\n"
        )
        sys.exit(84)
    except OSError as error:
        sys.stderr.write(f"bookworm: error: {error}\n")
        sys.exit(84)
    except LookupError as error:
        sys.stderr.write(f"bookworm: error: {error}\n")
        sys.exit(84)

    if profiler:
        profiler.stop()
        output_path = _profile_output_path(flag, payload)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            f.write(profiler.output_html())
        sys.stderr.write(f"\n[bookworm] profiling report saved to {output_path}\n")

    _print_result(flag, result)

    elapsed = time.perf_counter() - start_time
    sys.stderr.write(f"\n[bookworm] done in {elapsed:.3f}s\n")


if __name__ == "__main__":
    main()
