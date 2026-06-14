#!/usr/bin/env python3

import time

import numpy as np

MODEL_NAME = "distilbert-base-uncased"
MODEL_SIZE = "~268 MB"
MAX_SENTENCES_PER_BOOK = 256
BATCH_SIZE = 32
MAX_LENGTH = 256

_MODEL = None

def _bert_import_error():
    return ImportError(
        "DistilBERT support requires the optional dependencies. "
        'Install CPU torch, then run: python -m pip install -e ".[bert]"'
    )


def _model():
    global _MODEL
    if _MODEL is None:
        try:
            import torch
            from transformers import AutoModel, AutoTokenizer
        except ModuleNotFoundError as error:
            raise _bert_import_error() from error

        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            model = AutoModel.from_pretrained(MODEL_NAME)
        except OSError as error:
            raise OSError(
                f"unable to load '{MODEL_NAME}'. Install the [bert] extra and allow "
                "the first Hugging Face download, then rerun the command."
            ) from error

        model.eval()
        _MODEL = (tokenizer, model, torch)
    return _MODEL


def _peak_memory_mb():
    try:
        import resource
    except ImportError:
        return 0.0

    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if peak > 10_000_000:
        return round(peak / (1024 * 1024), 2)
    return round(peak / 1024, 2)


def runtime_metadata(start):
    return {
        "seconds": round(time.perf_counter() - start, 4),
        "peak_memory_mb": _peak_memory_mb(),
        "model": f"{MODEL_NAME} ({MODEL_SIZE})",
    }


def _sample_evenly(sentences, limit=MAX_SENTENCES_PER_BOOK):
    if len(sentences) <= limit:
        return sentences
    positions = np.linspace(0, len(sentences) - 1, num=limit, dtype=int)
    return [sentences[index] for index in positions]


def embed(texts, batch_size=BATCH_SIZE, max_length=MAX_LENGTH):
    tokenizer, model, torch = _model()
    vectors = []

    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]
        encoded = tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
        with torch.no_grad():
            output = model(**encoded)

        hidden = output.last_hidden_state
        mask = encoded["attention_mask"].unsqueeze(-1).expand(hidden.size()).float()
        summed = (hidden * mask).sum(dim=1)
        counts = mask.sum(dim=1).clamp(min=1e-9)
        pooled = summed / counts
        vectors.append(pooled.cpu().numpy())

    matrix = np.vstack(vectors).astype(np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


def _book_embedding(book):
    from pipeline.summarize import NUM_SENTENCES, _candidates
    candidates = [sentence for _, sentence in _candidates(book)]
    if not candidates:
        candidates = book.sentences[:NUM_SENTENCES] or [book.clean[:1000]]
    sentences = _sample_evenly(candidates)
    return embed(sentences).mean(axis=0)
