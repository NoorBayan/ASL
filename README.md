# Fiqh Knowledge Infrastructure: Hybrid Relational-Graph Pipeline

This repository contains the data engineering pipeline and infrastructure code for transforming unstructured traditional Islamic Jurisprudence (Fiqh) texts into a structured, machine-interpretable hybrid knowledge graph. 

This project implements a **proof-of-concept architecture** that separates hierarchical taxonomy (book structures, chapters) from semantic reasoning (rules, conditions, evidence) to enable efficient, multi-hop queries over dense legal corpora without query degradation.

## 🏗️ Architecture Overview

The system utilizes a **Hybrid Relational-Graph Architecture**:
1. **Relational Layer (Topic Hierarchy):** Organizes the jurisprudential corpus into a Directed Acyclic Graph (DAG) using Materialized Path Encoding. This layer handles hierarchical filtering and limits the semantic search space.
2. **Graph Layer (Semantic Connectivity):** Encodes "Knowledge Atoms" (rulings, conditions, evidence) and their micro-relations as a semantic network, allowing for complex, dependency-aware multi-hop queries.

## ⚙️ Core Pipeline Components

The pipeline is staged to minimize error propagation, consisting of the following modules:

- **Hierarchy Construction (`src/hierarchy/`):** Builds the structural DAG using pattern-based extraction and hierarchical clustering, effectively mapping the chapters and sub-topics of the corpus.
- **Knowledge Atomization (`src/atomization/`):** Segments continuous legal prose into minimal, functionally distinct semantic units (Knowledge Atoms) using contextual boundary detection (CRF + AraBERT), bypassing brittle punctuation-based splitting.
- **Relation Extraction (`src/relations/`):** Inters semantic relations (e.g., support, restrict, contradict) between localized atoms within a constrained search space.
- **Graph Generation (`src/graph/`):** Materializes the extracted entities and relations into a formal, queryable knowledge graph.


## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.
