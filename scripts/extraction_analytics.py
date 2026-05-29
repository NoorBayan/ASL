import pandas as pd
from pathlib import Path

def analyze_extraction():
    print("="*75)
    print("ASL Extraction Pipeline & Confidence Analytics (Section 11.4)")
    print("="*75)

    base_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
    elements_df = pd.read_csv(base_dir / "elements.csv", encoding='utf-8-sig', sep=None, engine='python')
    kg_df = pd.read_csv(base_dir / "knowledge_graph.csv", encoding='utf-8-sig', sep=None, engine='python')

    print("[1] Semantic Atomization (Epistemic Roles):")
    if 'element_type_en' in elements_df.columns:
        dist = elements_df['element_type_en'].value_counts(normalize=True) * 100
        for e_type, pct in dist.head(5).items():
            print(f"   - {str(e_type).capitalize():<15}: {pct:.1f}%")

    print("\n[2] Semantic Relation Extraction:")
    print(f"   - Total Explicit Typed Edges Extracted: {len(kg_df):,}")

    print("\n[3] Confidence-Aware Filtering Mechanism:")
    if 'confidence_level' in elements_df.columns:
        atom_conf = elements_df['confidence_level'].value_counts(normalize=True) * 100
        print("   - Atoms passing automatic integration (High Confidence): {:.1f}%".format(atom_conf.get('high', 0)))
        
    if 'confidence' in kg_df.columns:
        edge_conf = kg_df['confidence'].value_counts(normalize=True) * 100
        print("   - Relations flagged for verification (Medium Confidence): {:.1f}%".format(edge_conf.get('medium', 0)))

    print("="*75)

if __name__ == "__main__":
    analyze_extraction()
