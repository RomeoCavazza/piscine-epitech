# Days 121–135 — Advanced NLP for Book Analysis

- **Objectives**: [OBJECTIVES.md](OBJECTIVES.md)
- **Project Deliverables**: [solutions_day121_135/](solutions_day121_135/)

## Project Overview

**15 days** (concurrent with DOP) of applied Natural Language Processing: build Bookworm, a comprehensive NLP pipeline that analyzes books across multiple dimensions—lexical diversity, entity recognition, topic clustering, automatic summarization, and content-based recommendations—with a canonical CLI entrypoint.

---

## Architecture

### Five-Pillar NLP Analysis

```
Raw Book Text
    ↓
[Preprocessing: clean, tokenize, normalize]
    ↓
┌─────────────────────────────────────────┐
│ Lexical Diversity   [5+ measures]       │
│ Named Entity Recognition [Characters]   │
│ Topic Extraction    [Latent topics]     │
│ Automatic Summarize [Key sentences]     │
│ Similarity Detect   [Content matching]  │
└─────────────────────────────────────────┘
    ↓
[Structured Output: dictionary/JSON]
    ↓
CLI Entrypoint: `bookworm.py`
```

---

## Feature Specifications

### 1. Text Preprocessing
- **Cleaning**: Remove HTML, markdown, special characters
- **Tokenization**: Sentence and word-level decomposition
- **Normalization**: Lowercasing, stemming/lemmatization
- **Stopword Removal**: Filter common words (NLTK stopwords)
- **Vectorization**: TF-IDF, word embeddings, or bag-of-words

### 2. Lexical Diversity Analysis
Compute 5+ metrics across sections:
- Type-Token Ratio (TTR): vocabulary richness
- Flesch-Kincaid Grade Level: readability
- Shannon Entropy: information density
- Unique Words per Section: segmentation
- Vocabulary Complexity: avg word length

### 3. Named Entity Recognition
Extract and classify:
- **Characters**: Person entities (spaCy NER or simple heuristic)
- **Locations**: Place entities from text
- **Organizations**: Company/institution names
- Frequency ranking and co-occurrence analysis

### 4. Topic Extraction
- Latent Semantic Analysis (LSA) or LDA
- Identify main topics per chapter/section
- Compute topic coherence
- Extract keywords per topic
- Visualize topic distribution

### 5. Automatic Summarization
- **Extractive**: Top-K important sentences
- **Scoring**: TF-IDF, position, or graph-based (TextRank)
- **Abstractive**: (optional advanced) neural summarization
- Configurable summary length (% of original)

### 6. Book Similarity & Recommendations
- **Content Matching**: Cosine similarity on TF-IDF vectors
- **Topic Matching**: Compare topic distributions
- **Metadata Matching**: Genre, author, publication date
- Recommend similar books from corpus

---

## Implementation Structure

### Core Components

**bootstrap/** — Reusable utilities (frozen base)
- [calculator.py](solutions_day121_135/bootstrap/calculator.py) — Statistical helpers
- [tools.py](solutions_day121_135/bootstrap/tools.py) — Common NLP utilities
- [instructions.pdf](solutions_day121_135/bootstrap/instructions.pdf) — Bootstrap spec
- [catalog.csv](solutions_day121_135/bootstrap/catalog.csv) — Reference book metadata

**Main Pipeline** — Bookworm implementation
- [bookworm.py](solutions_day121_135/bookworm.py) — Canonical CLI entrypoint
- [new_bookworm.py](solutions_day121_135/new_bookworm.py) — Draft/experimental features
- [helper.py](solutions_day121_135/helper.py) — Internal utilities and pipeline logic

**Data**
- [corpus/](solutions_day121_135/corpus/) — Book text files (≈29 GB gitignored)
- [diagrams/](solutions_day121_135/diagrams/) — Mermaid visualizations (lexdiv, topics, entities, etc.)

**Documentation**
- [docs/instructions.pdf](solutions_day121_135/docs/instructions.pdf) — Project specification
- [docs/kickoff.pdf](solutions_day121_135/docs/kickoff.pdf) — Project kickoff notes
- [docs/choices_explained.md](solutions_day121_135/docs/choices_explained.md) — Design decisions

---

## CLI Specification

```bash
# Canonical invocation
python bookworm.py <book_file> [options]

# Example outputs
$ python bookworm.py mobydick.txt
{
  "lexdiv": {
    "ttr": 0.045,
    "flesch_kincaid": 8.3,
    "entropy": 4.21,
    ...
  },
  "entities": {
    "characters": ["Ishmael", "Captain Ahab", "Starbuck", ...],
    "locations": ["Nantucket", "Pequod", ...]
  },
  "topics": [
    {"keywords": ["whale", "sea", "hunt"], "weight": 0.32},
    ...
  ],
  "summary": "...",
  "similar_books": ["Twenty Thousand Leagues", "Island of Doctor Moreau", ...]
}
```

---

## Evaluation Criteria

| Rubric | Description |
|--------|-------------|
| **Preprocessing** | |
| `clean` | Appropriate text cleaning applied before analysis |
| `tokenization` | Proper sentence and word tokenization |
| `stopwords` | Stopwords correctly identified and explained |
| `normalization` | 2+ normalization techniques described |
| `vectorization` | 2+ vectorization methods explained |
| `collision` | Program behavior unchanged with invalid flags |
| **Analysis Features** | |
| `lexdiv` | ≥5 lexical diversity measures in output |
| `topics` | Topic extraction for book sections |
| `topics-doc` | Mermaid diagram of topic modeling pipeline |
| `entities` | Character and location extraction |
| `entities_doc` | Mermaid diagram of NER pipeline |
| `summarize` | Automatic summarization (extractive/abstractive) |
| `summarize_doc` | Mermaid diagram of summarization pipeline |
| `similar` | Book similarity ranking and recommendations |
| `similar_doc` | Mermaid diagram of recommendation pipeline |
| `bookcard` | Output dictionary with all analysis results |
| **Code Quality** | |
| `nomenclature` | CLI names match specification |
| `maintainability` | Clean, modular, readable code |
| `robustness` | Graceful error handling and messages |
| `portability` | Functional on evaluator's machine |

---

## Key Lessons

- **Text Preprocessing**: Foundation for all downstream NLP tasks
- **Tokenization**: Word vs. sentence boundaries; handling edge cases
- **Vectorization**: TF-IDF, embeddings, and bag-of-words trade-offs
- **Lexical Analysis**: Multiple diversity metrics capture different aspects of vocabulary
- **Entity Recognition**: Pattern matching vs. neural sequence tagging
- **Topic Modeling**: LSA, LDA, and topic coherence evaluation
- **Summarization**: Extractive (position-based) vs. abstractive (generation) approaches
- **Similarity Metrics**: Cosine similarity, Euclidean distance, and semantic matching
- **CLI Design**: Argparse best practices, help messages, error handling
- **Corpus Management**: Handling large text collections efficiently
