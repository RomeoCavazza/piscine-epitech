#!/usr/bin/env python3

import math
from collections import Counter


def lexdiv(book):
    words = book.words
    tok = len(words)
    frequencies = Counter(words)
    typ = len(frequencies)
    hapax = sum(1 for count in frequencies.values() if count == 1)

    return {
        "tok": tok,
        "typ": typ,
        "hap": hapax,
        "ttr": round(typ / tok, 4) if tok else 0.0,
        "mwl": round(sum(len(word) for word in words) / tok, 4) if tok else 0.0,
        "mwf": round(tok / typ, 4) if typ else 0.0,
    }


def _msttr(words, segment_size):
    if not words:
        return 0.0
    segments = [words[i:i + segment_size] for i in range(0, len(words), segment_size)]
    valid_segments = [s for s in segments if len(s) == segment_size] or [words]
    ttrs = [len(set(s)) / len(s) for s in valid_segments]
    return sum(ttrs) / len(ttrs)


def _mattr(words, window_size):
    if not words:
        return 0.0
    if len(words) <= window_size:
        return len(set(words)) / len(words)

    window_counts = Counter(words[:window_size])
    ttr_sum = len(window_counts) / window_size

    for i in range(1, len(words) - window_size + 1):
        out_word = words[i - 1]
        in_word = words[i + window_size - 1]
        window_counts[out_word] -= 1
        if window_counts[out_word] == 0:
            del window_counts[out_word]
        window_counts[in_word] += 1
        ttr_sum += len(window_counts) / window_size

    return ttr_sum / (len(words) - window_size + 1)


def _mtld_eval(words, threshold):
    if not words:
        return 0.0
    factors = 0
    current_types = set()
    current_tokens = 0

    for word in words:
        current_types.add(word)
        current_tokens += 1
        ttr = len(current_types) / current_tokens
        if ttr < threshold:
            factors += 1
            current_types = set()
            current_tokens = 0

    if current_tokens > 0:
        ttr = len(current_types) / current_tokens
        factors += (1 - ttr) / (1 - threshold)

    return len(words) / factors if factors > 0 else 0.0


def _mtld(words, threshold):
    if not words:
        return 0.0
    return (_mtld_eval(words, threshold) + _mtld_eval(list(reversed(words)), threshold)) / 2


def lexdiv_plus(book):
    words = book.words
    tok = len(words)
    frequencies = Counter(words)
    typ = len(frequencies)

    guiraud = typ / math.sqrt(tok) if tok > 0 else 0.0
    herdan_c = math.log(typ) / math.log(tok) if tok > 1 else 0.0

    m2 = sum(f ** 2 for f in frequencies.values())
    yule_k = 10000 * (m2 - tok) / (tok ** 2) if tok > 0 else 0.0

    maas_a2 = (math.log(tok) - math.log(typ)) / (math.log(tok) ** 2) if tok > 1 else 0.0

    return {
        "msttr": round(_msttr(words, 100), 4),
        "mattr": round(_mattr(words, 100), 4),
        "mtld": round(_mtld(words, 0.72), 4),
        "guiraud": round(guiraud, 4),
        "herdan_c": round(herdan_c, 4),
        "yule_k": round(yule_k, 4),
        "maas_a2": round(maas_a2, 4),
    }
