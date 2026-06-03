# Bookworm: Advanced NLP Pipeline for Book Analysis

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)](https://www.python.org/)
[![NLTK](https://img.shields.io/badge/NLTK-3.8+-orange?style=flat-square&logo=python)](https://www.nltk.org/)
[![Requests](https://img.shields.io/badge/Requests-2.28+-blue?style=flat-square&logo=python)](https://requests.readthedocs.io/)
[![Argparse](https://img.shields.io/badge/Argparse-stdlib-lightgrey?style=flat-square&logo=python)](https://docs.python.org/3/library/argparse.html)

## Project Overview

Bookworm is an NLP project in active construction. At this stage, the repository focuses on a stable project layout, a reusable bootstrap foundation, a canonical CLI entrypoint for the final deliverable, and a visible draft target kept alongside it for discussion.

Current roles:
- `bookworm.py`: canonical CLI entrypoint for the final subject
- `new_bookworm.py`: visible draft target and discussion artifact, not the stable base
- `helper.py`: internal reusable helpers built from bootstrap utilities
- `bootstrap/`: frozen bootstrap deliverables kept as a stable base

## Project Structure

```text
bookworm/
|-- .gitignore
|-- README.md
|-- bookworm.py
|-- helper.py
|-- new_bookworm.py
|-- bootstrap/
|   |-- __init__.py
|   |-- calculator.py
|   |-- tools.py
|   |-- instructions.pdf
|   `-- catalog.csv
|-- diagrams/
|   |-- entities.mermaid
|   |-- lexdiv.mermaid
|   |-- topics.mermaid
|   |-- summarize.mermaid
|   `-- similar.mermaid
|-- docs/
|   |-- instructions.pdf
|   |-- kickoff.pdf
|   `-- choices_explained.md
`-- corpus/
```

## Installation

### Clone the Repository

Clone the project using one of the following methods:

**HTTPS:**
```bash
git clone https://github.com/EpitechMscProPromo2028/T-AIA-600-PAR_14.git
cd T-AIA-600-PAR_14
```

**SSH:**
```bash
git clone git@github.com:EpitechMscProPromo2028/T-AIA-600-PAR_14.git
cd T-AIA-600-PAR_14
```

### Python Environment Initialization

Initialize and activate the virtual environment, then install the dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install networkx spacy nltk scikit-learn requests
```

## Grading Criteria

| Rubric | Description |
|--------|-------------|
| **Text Preprocessing** | |
| clean | Students apply relevant cleaning steps to book text files before any other operation |
| tokenization | Students apply proper tokenization techniques to decompose text into tokens |
| stopwords | Students can explain what stopwords are and their role in preprocessing |
| normalization | Students can name 2 main normalization techniques and explain differences, pros/cons |
| vectorization | Students can name at least 2 methods of token vectorization and explain how they work |
| collision | Program behavior is NOT altered with inappropriate or non-existing flags |
| **Analysis Features** | |
| lexdiv | Program returns dictionary with at least 5 lexical diversity measures |
| topics | Program can extract main topics for each section of a book |
| topics-doc | Students deliver diagram illustrating topics modeling pipeline |
| entities | Program can extract locations and characters from a book |
| entities_doc | Students deliver diagram illustrating NER pipeline |
| summarize | Program can summarize a book in a few sentences |
| summarize_doc | Students deliver diagram illustrating text summarization pipeline |
| similar | Program suggests list of books similar to provided book |
| similar_doc | Students deliver diagram illustrating book recommendation pipeline |
| bookcard | Program returns dictionary compiling various information about a book |
| **Code Quality** | |
| nomenclature | Program complies with CLI nomenclature specified in subject |
| maintainability | Code is easily maintainable (readable names, atomic functions, clear structure) |
| robustness | Program handles errors gracefully with clear messages |
| portability | Delivery is functional on evaluators' machine, not only students' machine |
| **Professional Standards** | |
| versioning_basics | Uses versioning tool with proper workflow: branching strategy, regular commits, descriptive messages, clean gitignore |
| clean_repo | Repository is clean and well-organized; no unnecessary or large files/folders |
| doc_basic | Students deliver README with project abstraction, requirements, setup, and usage examples |
| tools_justification | Students justify package choices professionally |
| presentation | Project presented professionally with relevant support (slides and/or demo) |
| argumentation | Students support reflections and defend choices with well-developed, illustrated arguments |
