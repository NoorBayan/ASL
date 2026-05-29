"""
ASL Knowledge Infrastructure - Dataset Profiling (Section 11.2)
This script validates the corpus segments, cross-temporal distribution, 
and basic descriptive statistics of the constructed knowledge base.
"""

import pandas as pd
from pathlib import Path

def generate_dataset_report():
    print("="*75)
    print("ASL Dataset - Comprehensive Statistical Report (Section 11.2)")
    print("="*75)

    # Resolve local paths dynamically
    base_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
    
    files = {
        "topics": base_dir / "topics.csv",
        "elements": base_dir / "elements.csv",
        "topic_source": base_dir / "topic_source_contents.csv",
        "element_source": base_dir / "element_source_contents.csv"
    }

    # Load Data
    dfs = {}
    for name, path in files.items():
        if path.exists():
            dfs[name] = pd.read_csv(path, encoding='utf-8-sig', sep=None, engine='python')
        else:
            print(f"[Error] File not found: {path}")
            return

    print("[1] Validating Corpus Segments (Provenance Integration)...")
    t_count = len(dfs["topics"])
    e_count = len(dfs["elements"])
    ts_count = len(dfs["topic_source"])
    es_count = len(dfs["element_source"])
    
    total_nodes = t_count + e_count
    total_sources = ts_count + es_count

    print(f"  - Semantic Nodes: {total_nodes:,} ({t_count} Topics + {e_count} Atoms)")
    print(f"  - Textual Source Segments: {total_sources:,}")
    print(f"  - Total Interconnected Units: {total_nodes + total_sources:,}\n")

    print("[2] Validating Cross-Temporal Distribution...")
    if 'source_type' in dfs["elements"].columns:
        dist = dfs["elements"]['source_type'].value_counts(normalize=True) * 100
        for source, pct in dist.items():
            print(f"  - {str(source).capitalize():<15}: {pct:.1f}%")
    
    print("\n" + "="*75)

if __name__ == "__main__":
    generate_dataset_report()
