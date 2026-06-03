# Days 121–135 — Objectives & Learning Outcomes

## Core Objectives

- **Text Preprocessing Mastery**: Cleaning, tokenization, normalization, and vectorization
- **Linguistic Analysis**: Computing and interpreting lexical diversity across multiple dimensions
- **Information Extraction**: Named entity recognition for characters, locations, and organizations
- **Unsupervised Learning**: Topic modeling and clustering techniques (LSA/LDA)
- **Text Summarization**: Both extractive and abstractive summarization methods
- **Recommendation Systems**: Content-based similarity and book recommendations
- **Production NLP**: Building production-grade CLI with robust error handling

## Key Concepts

### Preprocessing
- Text cleaning: HTML, punctuation, normalization
- Tokenization: Word and sentence boundaries
- Stopwords: Filtering common words
- Stemming vs. Lemmatization: Morphological analysis

### Vectorization Methods
- Bag-of-Words: Simple frequency counting
- TF-IDF: Term importance weighting
- Word Embeddings: Distributed representations
- LSI/LSA: Latent semantic vectors

### Lexical Diversity Metrics
- Type-Token Ratio: vocabulary richness
- Flesch-Kincaid: reading difficulty
- Shannon Entropy: information content
- Vocabulary complexity: word length and rarity

### Entity Recognition
- Pattern-based matching: regular expressions
- Sequence tagging: spaCy NER, BiLSTM models
- Heuristics: title case detection, gazetteers

### Topic Modeling
- Latent Semantic Indexing (LSI/LSA)
- Latent Dirichlet Allocation (LDA)
- Non-negative Matrix Factorization (NMF)
- Coherence scores: model evaluation

### Summarization
- Extractive: sentence ranking (TF-IDF, TextRank, position)
- Abstractive: sequence-to-sequence (optional advanced)
- Length control: percentage or sentence count
- Quality metrics: ROUGE, METEOR

### Similarity & Recommendations
- Cosine similarity on TF-IDF vectors
- Euclidean and Minkowski distances
- Collaborative filtering (optional)
- Content-based recommendations

## Learning Outcomes

By completion, students will:
1. **Preprocess** raw text for machine learning pipelines
2. **Compute** 5+ lexical diversity metrics
3. **Extract** named entities from unstructured text
4. **Identify** main topics using unsupervised learning
5. **Summarize** long documents automatically
6. **Recommend** similar items using content matching
7. **Design** production CLI applications with argparse
8. **Evaluate** NLP systems with appropriate metrics
