# ASL: Knowledge Engineering Infrastructure for Islamic Jurisprudence

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Graph_Analytics](https://img.shields.io/badge/Graph_Analytics-NetworkX-orange)
![Domain](https://img.shields.io/badge/Domain-Islamic_Jurisprudence_(Fiqh)-success)
![Status](https://img.shields.io/badge/Status-Phase_1_(Waqf)-purple)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## 📌 Overview
This repository hosts the data and analytical scripts for **ASL**, a scalable knowledge engineering infrastructure designed to digitally transform and semantically model classical Islamic Jurisprudence (Fiqh). 

Historically, Fiqh relies on deeply nested prose containing interconnected rules, conditions, and evidence. ASL addresses this by systematically extracting these components into atomic units and rebuilding them as a **Hybrid Relational-Graph Knowledge Base**. This structure allows researchers, legal scholars, and AI systems to perform highly accurate, multi-hop contextual queries over complex jurisprudential arguments.

---

## 📖 Current Scope & Future Expansion
**Phase 1 (Current Release):** The current dataset serves as an extensive proof-of-concept, focusing exclusively on the **Chapter of Endowment (Kitab Al-Waqf)** from the renowned Hanbali text, *Al-Rawd Al-Murbi'*, integrated alongside contemporary Saudi statutory regulations.

**Future Vision:** ASL is architecturally designed for massive scalability. Subsequent phases will systematically expand the infrastructure to cover:
* All remaining chapters of *Al-Rawd Al-Murbi'*.
* Cross-school (Madhahib) comparative texts.
* Extended contemporary legal codifications and regulatory frameworks.

We welcome collaborations from Fiqh scholars, data scientists, and legal informatics researchers to help expand this foundational infrastructure.

---

## 🧪 Interactive Evaluation (Google Colab)
To make the evaluation metrics easily accessible to researchers—without the need for local programming environments—we have prepared an interactive Google Colab Notebook. 

This notebook contains the complete experimental pipeline, allowing you to seamlessly run, verify, and visualize the structural metrics and latency benchmarks reported in our research.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://drive.google.com/file/d/1i-EB97sjX_p9--3eZbTQ3gTmQpgCA5Io/view?usp=sharing)

*(Click the badge above to open the notebook in your browser, then click `Runtime > Run all` to generate the analytical reports and visualizations).*

---

## 📊 Dataset Highlights
The `data/processed/` directory contains the meticulously curated relational tables and semantic graph edges. This dataset links classical doctrinal reasoning with modern codified law through explicitly typed relations (e.g., `condition_of`, `supported_by`, `aligned_with`). 

Researchers in Digital Humanities and Computational Law can directly utilize these `.csv` files for:
* Structural network analysis of legal arguments.
* Prompt-engineering and Retrieval-Augmented Generation (RAG) for LLMs.
* Comparative algorithmic law studies.

---

## 📄 Citation & Usage
If you utilize this infrastructure, dataset, or evaluation methodology in your research, please cite our upcoming publication in *IEEE Access* (Citation details will be provided upon publication).

## 🤝 Contribution
Contributions are highly encouraged! Whether you are a Fiqh specialist wishing to annotate new chapters, or a data engineer proposing pipeline optimizations, please feel free to open an issue or submit a pull request.
