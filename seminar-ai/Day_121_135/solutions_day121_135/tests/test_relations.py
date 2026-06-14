#!/usr/bin/env python3

from pipeline.lexdiv import lexdiv


def test_lexdiv_ignores_whitespace_noise(book, make_book):
    base = book.clean[:20000]
    noisy = base.replace(" ", "  \t ")
    assert lexdiv(make_book(base)) == lexdiv(make_book(noisy))


def test_lexdiv_duplication_doubles_tokens_not_types(book, make_book):
    base = book.clean[:20000]
    single = lexdiv(make_book(base))
    doubled = lexdiv(make_book(base + " " + base))
    assert doubled["tok"] == 2 * single["tok"]
    assert doubled["typ"] == single["typ"]
    assert doubled["hap"] == 0


def test_lexdiv_plus_duplication_stabilizes_mattr_mtld(book, make_book):
    from pipeline.lexdiv import lexdiv_plus
    
    base = book.clean[:20000]
    single = lexdiv_plus(make_book(base))
    doubled = lexdiv_plus(make_book(base + " " + base))
    
    assert abs(doubled["mattr"] - single["mattr"]) / single["mattr"] < 0.1
    assert abs(doubled["mtld"] - single["mtld"]) / single["mtld"] < 0.1


def test_similar_is_stable_under_duplicated_content(book, make_book):
    from pipeline.similar import similar

    base = make_book(book.clean)
    padded = make_book(book.clean + " " + book.clean[:5000])
    assert similar(base) == similar(padded)


def test_summary_is_stable_under_trailing_noise(book, make_book, summary_result):
    from pipeline.summarize import summarize

    noisy = make_book(book.clean + "\n\n\n   \t")
    assert summarize(noisy) == summary_result
