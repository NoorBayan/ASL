# ASL: Computational Knowledge Base & Graph Infrastructure for Islamic Jurisprudence

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Storage Engine](https://img.shields.io/badge/Storage-SQLite_%7C_NetworkX-green.svg)](https://networkx.org/)
[![Domain](https://img.shields.io/badge/Domain-Islamic_Jurisprudence_%26_Law-darkblue.svg)]()
[![Corpus Scope](https://img.shields.io/badge/Corpus_Scope-Kitab_Al--Waqf-purple.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)](https://github.com/NoorBayan/ASL/blob/main/LICENSE)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1LA56J0Cqc9jPDg-YLO9IEZuwUGFruUeD?usp=drive_link)

<p align="center">
  <img src="https://raw.githubusercontent.com/NoorBayan/ASL/main/Images/logo.png" alt="ASL Project Logo" width="220px"/>
</p>

## Overview

**ASL** is an open-source data infrastructure and software pipeline developed to convert complex classical Arabic legal texts into structured, machine-interpretable knowledge representations. 

Rather than relying on lexical search across unstructured documents, this repository models jurisprudential arguments through a dual relational-graph architecture. The system decomposes legal discourse into fine-grained propositional units, preserves character-level source provenance, indexes hierarchical topic structures via transitive closure tables, and captures explicit reasoning dependencies across classical rulings and contemporary statutory frameworks.

---

## Dataset Scope & Content

* **Current Implementation:** This release provides the processed knowledge network for the **Chapter of Endowment (*Kitab al-Waqf*)** based on the classical Hanbali text *Al-Rawd Al-Murbi'*, mapped alongside modern statutory provisions from the Saudi General Authority for Awqaf.
* **Ongoing Development:** Annotation and extraction are actively underway to extend coverage to subsequent legal chapters. The long-term goal is to incorporate multi-school comparative jurisprudence (*Madhahib*) and broader regulatory statutes.

---

## Interactive Notebook (Google Colab)

An interactive Google Colab notebook is provided to demonstrate the pipeline, execute structured queries, and inspect the underlying graphs without requiring local installation:

👉 **[Open Interactive Demonstration in Google Colab](https://colab.research.google.com/drive/1LA56J0Cqc9jPDg-YLO9IEZuwUGFruUeD?usp=drive_link)**

### Visualizations & Interactive Modules:
* **Taxonomic Sunburst Explorer:** Interactive navigation across the 115 topic categories and their nested sub-branches.
* **Poincaré Metric Projection:** Hyperbolic geometric mapping of concept abstractions within the unit disk.
* **Closure Table Ancestry Inspector:** Live SQL lookups tracing complete ancestor and descendant lineages with zero recursive overhead.
* **Semantic Span Highlighter:** Visual extraction highlighting operational roles (rulings, conditions, proofs, exceptions) in source passages.
* **Bitwise Provenance Verification:** Interactive verification confirming exact string identity between extracted propositions and raw source coordinates.
* **Micro-Legal Logic Network:** Directed graph rendering dependencies connecting legal rulings directly to their conditions and proofs.
* **Statutory Alignment View:** Comparative side-by-side mapping between classical juristic rules and modern codified articles.
* **Performance Benchmarks:** Execution scripts measuring query latencies and multi-threaded scaling behavior.

---

## Dataset Organization

The processed corpus is organized into **3,190 structural units**, consisting of **703 semantic graph nodes** (115 Topics + 588 Knowledge Atoms), **2,487 textual source segments** supporting full auditability, and **12,980 typed directed edges**.

The data files are located in the [`data/processed/`](data/processed/) directory in standard CSV format:

| File Name | Primary Representation | Record Count | Core Attributes |
| :--- | :--- | :--- | :--- |
| **`topics.csv`** | Conceptual Topic Hierarchy | **115 Nodes** | `topic_id`, `parent_id`, `title`, `topic_level`, `topic_path`, `category` |
| **`elements.csv`** | Knowledge Element Atoms | **588 Nodes** | `element_id`, `topic_id`, `element_type_en`, `element_text`, `confidence_level` |
| **`knowledge_graph.csv`** | Typed Relational Edges | **12,980 Edges** | `relation_id`, `subject_id`, `predicate`, `object_id`, `weight`, `confidence` |
| **`topic_source_contents.csv`** | Annotated Source Texts | **2,487 Segments**<br>*(Cumulative across corpus)* | `topic_id`, `text_annotated`, `annotation_map`, `reference_page` |
| **`element_source_contents.csv`** | Propositional Text Evidence | *(Referenced in cumulative segments)* | `element_id`, `topic_id`, `text_annotated`, `reference_page` |

---

## Scholarly Collaboration & Community

Structuring historical legal discourse into verifiable computational models requires close interdisciplinary collaboration between legal specialists, linguists, and computer scientists. 

We welcome interest and collaboration from researchers across these areas:
* **Islamic Jurisprudence & Legal Theory:** Contributing to domain verification, juristic reasoning chains, and expanding annotations to additional chapters or legal schools.
* **Modern Law & Comparative Informatics:** Exploring alignment between traditional jurisprudence and contemporary codified statutory systems.
* **Computational Linguistics & Arabic NLP:** Developing specialized methods for Classical Arabic discourse segmentation, rhetorical semantics, and coreference resolution.
* **Knowledge Graphs & AI Systems:** Integrating structured legal layers into neuro-symbolic reasoning, Graph-RAG, and retrieval architectures.

Researchers interested in joint work, shared datasets, or feedback are encouraged to reach out or participate via [GitHub Issues](../../issues).

---

## License

The code and datasets in this repository are released under the **[MIT License](https://github.com/NoorBayan/ASL/blob/main/LICENSE)**.
