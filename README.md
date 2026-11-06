# ASL: A Scalable Knowledge Engineering Infrastructure for Islamic Jurisprudence

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Storage](https://img.shields.io/badge/Storage-SQLite_%7C_NetworkX-green.svg)](https://networkx.org/)
[![Domain](https://img.shields.io/badge/Domain-Islamic_Jurisprudence_%26_Law-darkblue.svg)]()
[![Dataset Status](https://img.shields.io/badge/Corpus_Scope-Kitab_Al--Waqf-purple.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)](https://github.com/NoorBayan/ASL/blob/main/LICENSE)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1LA56J0Cqc9jPDg-YLO9IEZuwUGFruUeD?usp=drive_link)

<p align="center">
  <img src="https://raw.githubusercontent.com/NoorBayan/ASL/main/Images/logo.png" alt="ASL Project Logo" width="220px"/>
</p>

## Overview

The corpus of traditional Islamic Jurisprudence (*Fiqh*) represents one of the world's most intricate and systematically reasoned legal systems. However, its foundational knowledge—comprising legal rulings (*Ahkam*), evidentiary grounds (*Adillah*), operative conditions (*Shurut*), and exceptions (*Istithna'at*)—has historically remained embedded in layered, continuous classical Arabic prose (*Matn*, *Sharh*, and *Hashiyah*). 

**ASL** is an open-source knowledge engineering infrastructure designed to bridge this historical corpus with modern legal informatics. Rather than treating texts as flat strings for simple keyword retrieval, ASL systematically decomposes dense legal discourse into discrete, propositional units (**Knowledge Atoms**) and reconstructs them into a **Hybrid Relational–Graph Architecture**. This enables verifiable provenance tracking, low-millisecond multi-hop logical traversal, and direct semantic alignment with contemporary statutory regulations.

---

## Current Scope & Corpus Roadmap

* **Current Release (Phase 1):** The current release focuses on the **Chapter of Endowment (*Kitab al-Waqf*)** from the authoritative Hanbali manual *Al-Rawd Al-Murbi'*, mapped and harmonized alongside modern Saudi statutory regulations issued by the General Authority for Awqaf. The evaluated dataset encapsulates:
  * **115 Conceptual Topics** organized within a 5-tier Directed Acyclic Graph (DAG).
  * **588 Atomic Propositions (Knowledge Atoms)** classified across 47 operational epistemic roles.
  * **12,980 Typed Directed Dependencies** supporting structured legal reasoning.

* **Ongoing & Future Work:** Our team is actively expanding the annotation pipeline to cover the remaining chapters of *Al-Rawd Al-Murbi'*. The broader research horizon includes integrating comparative cross-school (*Madhahib*) analyses and extending interoperability mappings to wider Arab and Islamic codified jurisdictions.

---

## Interactive Verification & Reproducibility (Google Colab)

To support full scientific transparency and allow scholars to experiment with the infrastructure without configuring a local development environment, we provide a complete, interactive Google Colab notebook.

The notebook allows you to replicate all stages of the framework, inspect relational schemas, execute live query benchmarks, and render interactive visual analytics directly in your browser:

👉 **[Launch Interactive Google Colab Notebook](https://colab.research.google.com/drive/1LA56J0Cqc9jPDg-YLO9IEZuwUGFruUeD?usp=drive_link)**

### Included Demonstrations:
1. **Interactive Topic Taxonomy (Deliverable 1.1):** A navigable multi-level sunburst exploration of the 115 conceptual topics.
2. **Poincaré Hyperbolic Embedding (Deliverable 1.2):** Geometric projection of concept abstraction inside the unit disk ($\mathbb{B}^2$).
3. **Transitive Lineage Inspector (Deliverable 1.3):** Real-time SQL inspection of parent-child ancestry chains powered by Closure Tables.
4. **Semantic Passage Highlighter (Deliverable 2.1):** Color-coded visual breakdown of continuous classical passages into typed functional atoms.
5. **Bitwise Provenance Audit (Deliverable 2.3):** Zero-hallucination verification confirming exact character-level offsets against the source texts.
6. **Micro-Legal Logic Network (Deliverable 3.1):** Focused graph rendering connecting legal rulings directly to their conditions and supporting evidence.
7. **Statutory Alignment Card (Deliverable 3.2):** Visual comparative bridge linking classical jurisprudence with codified Saudi law.
8. **In-Process Latency Benchmark (Deliverable 5.3):** Live replication of the 1,000-query benchmark suite measuring sub-10ms response times.
9. **Concurrency Scalability Stress Test (Deliverable 5.4):** Real-time multi-threaded execution curve showing sublinear latency growth across expanding graph tiers.

---

## Dataset Organization

The curated datasets are available in the [`data/processed/`](data/processed/) directory as standards-compliant, tabular CSV files:

| File Name | Description | Key Fields |
| :--- | :--- | :--- |
| **`topics.csv`** | The 115 conceptual categories establishing the taxonomic DAG. | `topic_id`, `parent_id`, `title`, `topic_level`, `topic_path` |
| **`elements.csv`** | The 588 atomized propositions and their fine-grained functional roles. | `element_id`, `topic_id`, `element_type_en`, `element_text`, `confidence_level` |
| **`knowledge_graph.csv`** | The 12,980 typed dependencies connecting topics and atoms. | `relation_id`, `subject_id`, `predicate`, `object_id`, `weight`, `confidence` |
| **`topic_source_contents.csv`** | Annotated source passages linked to topic entities with tag mappings. | `topic_id`, `text_annotated`, `annotation_map`, `reference_page` |
| **`element_source_contents.csv`** | Granular textual evidence and page references for individual atoms. | `element_id`, `topic_id`, `text_annotated`, `reference_page` |

---

## An Open Invitation for Scholarly Collaboration

Building a comprehensive, machine-interpretable knowledge infrastructure for Islamic jurisprudence is fundamentally an interdisciplinary undertaking. It cannot be achieved by computer scientists in isolation, nor can it scale without the direct involvement of domain specialists.

We warmly invite colleagues from diverse disciplines to join, collaborate, and partner with us in expanding this initiative:

* **Scholars of Islamic Jurisprudence & Usul al-Fiqh:** We welcome collaboration on annotating subsequent chapters, validating complex reasoning chains, resolving juristic ambiguities, and formalizing exception hierarchies across different schools of thought (*Madhahib*).
* **Legal Scholars & Regulatory Analysts:** We seek partnerships with researchers interested in statutory codification, modern commercial law (*Mu'amalat*), and comparative legal harmonization.
* **Computational Linguists & NLP Researchers:** There are rich opportunities for joint work on Classical Arabic boundary detection, rhetorical semantic extraction, coreference resolution in elliptical prose, and domain-adapted language modeling.
* **Data Engineers & Graph AI Researchers:** We invite contributions toward federated Virtual Knowledge Graphs (VKGs), Graph-RAG architectures, and neuro-symbolic reasoning frameworks.

Whether your interest lies in formal co-authorship on expanded chapters, dataset curation, peer review, or exploring joint research proposals, please feel free to reach out. We are eager to accommodate whatever collaborative structure best aligns with your academic interests.

* **Contact & Inquiries:** You are welcome to open a discussion via [GitHub Issues](../../issues) or contact the corresponding author as listed in our published research.

---

## License

This project, its dataset, and source code are openly licensed under the **[MIT License](https://github.com/NoorBayan/ASL/blob/main/LICENSE)**. You are free to use, adapt, and distribute this work with appropriate academic attribution.

---

