#!/usr/bin/env python3

import os
import sys
import json
import argparse
import requests
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from core.book import Book
from core.tools import book_title
from core.agent_schema import TOOLS_SCHEMA
from pipeline.registry import run_arg_command, run_book_command

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_API = f"{OLLAMA_HOST}/api/chat"
MODEL_NAME = os.getenv("BOOKWORM_LLM_MODEL", "qwen2.5:7b")
TOP_K_CHUNKS = 3

TOOL_ROUTING = {
    "get_lexical_diversity": "lexdiv",
    "get_lexical_diversity_plus": "lexdiv-plus",
    "get_topics": "topics",
    "extract_topics_bert": "topics-bert",
    "compare_topic_models": "compare",
    "get_entities": "entities",
    "get_summary": "summarize",
    "summarize_with_bert": "summarize-bert",
    "evaluate_summary": "eval-summary",
    "get_similar_books": "similar",
    "find_similar_books_bert": "similar-bert",
    "get_narrative_arc": "arc",
    "analyze_syntax": "syntax",
    "get_book_card": "card",
}

TOOL_ROUTING_WITH_ARG = {
    "analyze_author_syntax": ("authorsyntax", "author_name"),
    "attribute_authorship": ("attribute", "text"),
}

def search_text(book, query):
    paragraphs = [p.strip() for p in book.clean.split('\n\n') if len(p.strip()) > 50]
    if not paragraphs:
        return "Le livre est vide."

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        matrix = vectorizer.fit_transform(paragraphs)
        query_vec = vectorizer.transform([query])
    except ValueError:
        return "Erreur TF-IDF."

    sim_scores = cosine_similarity(query_vec, matrix)[0]
    top_indices = np.argsort(sim_scores)[-TOP_K_CHUNKS:][::-1]
    relevant = [paragraphs[i] for i in top_indices if sim_scores[i] > 0.01]

    if not relevant:
        relevant = paragraphs[:TOP_K_CHUNKS]
    return "\n\n".join(relevant)

def _safe_tool_call(flag, callback):
    try:
        return callback()
    except Exception as e:
        return f"Erreur lors de l'execution de {flag} : {str(e)}"


def run_pipeline_tool(book, flag):
    return _safe_tool_call(flag, lambda: run_book_command(book, flag))


def run_pipeline_tool_with_arg(flag, arg):
    return _safe_tool_call(flag, lambda: run_arg_command(flag, arg))


def agent_loop(book, book_title, user_query):
    system_prompt = f"""Tu es un agent littéraire autonome intégré à la CLI Bookworm.
Le livre actuellement ouvert est "{book_title}".
Tu disposes de 17 outils NLP puissants couvrant : diversité lexicale, topics (NMF et BERT), entités, résumés (K-Means et BERT), similarité, arc narratif, syntaxe, attribution d'auteur, et comparaison de modèles.
Analyse la question de l'utilisateur, et décide si tu as besoin d'appeler un ou plusieurs de ces outils pour lui répondre précisément.
Si un outil correspond parfaitement, utilise-le ! Une fois que tu as la réponse des outils, synthétise-la en français de manière claire et concise.
Attention : ne réponds JAMAIS à la place de l'outil, laisse-le te fournir l'information d'abord. N'invente pas les métriques.
RÈGLE D'OR : Quand tu donnes ta réponse finale, ne dis JAMAIS "Selon le résumé fourni", "D'après l'outil", ou "Le texte montre". Donne la réponse directement et naturellement, comme si tu le savais."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "tools": TOOLS_SCHEMA,
        "stream": False
    }

    try:
        resp = requests.post(OLLAMA_API, json=payload, timeout=45)
        resp.raise_for_status()
        data = resp.json()
        message = data.get("message", {})

        if "tool_calls" in message and len(message["tool_calls"]) > 0:
            messages.append(message)

            for tool_call in message["tool_calls"]:
                func_name = tool_call["function"]["name"]
                args = tool_call["function"].get("arguments", {})

                sys.stderr.write(f"[Tool] L'agent utilise l'outil : {func_name}...\n")
                sys.stderr.flush()

                result = None
                if func_name == "search_text":
                    result = search_text(book, args.get("query", ""))
                elif func_name in TOOL_ROUTING:
                    result = run_pipeline_tool(book, TOOL_ROUTING[func_name])
                elif func_name in TOOL_ROUTING_WITH_ARG:
                    flag, arg_key = TOOL_ROUTING_WITH_ARG[func_name]
                    result = run_pipeline_tool_with_arg(flag, args.get(arg_key, ""))
                else:
                    result = "Outil inconnu."

                messages.append({
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False),
                    "name": func_name
                })

            payload_stream = {
                "model": MODEL_NAME,
                "messages": messages,
                "stream": True
            }

            resp_stream = requests.post(OLLAMA_API, json=payload_stream, stream=True, timeout=45)
            resp_stream.raise_for_status()

            for line in resp_stream.iter_lines():
                if line:
                    d = json.loads(line)
                    chunk = d.get("message", {}).get("content", "")
                    sys.stdout.write(chunk)
                    sys.stdout.flush()
            sys.stdout.write("\n")

        else:
            sys.stdout.write(message.get("content", "") + "\n")
            sys.stdout.flush()

    except requests.exceptions.ConnectionError:
        sys.stderr.write(
            f"\n[Erreur: Ollama injoignable sur {OLLAMA_HOST}. "
            f"Lance 'ollama serve' puis 'ollama pull {MODEL_NAME}'.]\n"
        )
        sys.exit(84)
    except Exception as e:
        sys.stderr.write(f"\n[Erreur de l'agent : {e}]\n")
        sys.exit(84)

def main():
    parser = argparse.ArgumentParser(description="Bookworm Agent")
    parser.add_argument("--book", type=int, required=True, help="ID du livre")
    parser.add_argument("--ask", type=str, required=True, help="Question de l'utilisateur")
    args = parser.parse_args()

    try:
        book = Book(args.book)
    except SystemExit:
        sys.exit(84)

    agent_loop(book, book_title(args.book), args.ask)

if __name__ == "__main__":
    main()
