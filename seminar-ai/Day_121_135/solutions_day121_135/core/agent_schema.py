TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_text",
            "description": "Cherche des extraits exacts dans le texte du livre pour répondre à une question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Mots clés à chercher (ex: 'chapelier fou', 'lieu du crime')."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_syntax",
            "description": "Profil syntaxique du livre : longueur des phrases, distribution POS, densité de ponctuation, subordination, passif, profondeur d'arbre.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_author_syntax",
            "description": "Compare le profil syntaxique d'un auteur à l'ensemble de la collection. Auteurs disponibles : Carroll, Doyle, Christie, Wells.",
            "parameters": {
                "type": "object",
                "properties": {
                    "author_name": {"type": "string", "description": "Nom de l'auteur (ex: 'Doyle', 'Christie')."}
                },
                "required": ["author_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_lexical_diversity",
            "description": "Récupère les statistiques de diversité lexicale du livre (TTR, hapax, tokens).",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_lexical_diversity_plus",
            "description": "Récupère les métriques avancées de diversité lexicale (MSTTR, MATTR, MTLD, Guiraud, Herdan, Yule K, Maas).",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_topics",
            "description": "Extrait les thèmes et mots clés majeurs de chaque chapitre du livre (NMF).",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_topics_bert",
            "description": "Extrait les thèmes du livre via embeddings DistilBERT + K-Means (plus précis que NMF).",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_topic_models",
            "description": "Compare les algorithmes NMF, LSA et LDA pour la modélisation de topics et indique lequel est le meilleur.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_entities",
            "description": "Identifie les personnages (characters) et lieux (locations) principaux via SpaCy.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_summary",
            "description": "Génère un résumé extractif du livre en 5 phrases (clustering K-Means).",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_with_bert",
            "description": "Génère un résumé extractif du livre via embeddings DistilBERT (plus sémantique que K-Means).",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "evaluate_summary",
            "description": "Évalue la qualité des résumés via scores ROUGE-1, ROUGE-2 et ROUGE-L par rapport à un résumé de référence.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_similar_books",
            "description": "Trouve 5 autres livres similaires dans la collection (similarité cosinus TF-IDF).",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_similar_books_bert",
            "description": "Trouve 5 livres similaires via embeddings DistilBERT (plus précis que TF-IDF).",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_narrative_arc",
            "description": "Analyse l'arc narratif du livre : score de sentiment VADER section par section pour voir l'évolution émotionnelle.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "attribute_authorship",
            "description": "Attribue un texte à son auteur probable parmi Carroll, Doyle, Christie, Wells via régression logistique.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Texte à attribuer (au moins 5 phrases recommandées)."}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_book_card",
            "description": "Récupère la fiche complète du livre : diversité lexicale, topics, entités, résumé, livres similaires en une seule requête.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]
