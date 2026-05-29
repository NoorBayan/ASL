import pandas as pd
from pathlib import Path

def analyze_hierarchy():
    print("="*75)
    print("ASL Topic Hierarchy Structural Analytics (Section 11.3)")
    print("="*75)

    topics_path = Path(__file__).resolve().parent.parent / "data" / "processed" / "topics.csv"
    if not topics_path.exists():
        print(f"[Error] File not found: {topics_path}")
        return

    df = pd.read_csv(topics_path, encoding='utf-8-sig', sep=None, engine='python')

    total_nodes = len(df)
    print(f"1. Total Conceptual Topic Nodes: {total_nodes:,}")

    if 'topic_level' in df.columns:
        print(f"2. Maximum Taxonomy Depth: {int(df['topic_level'].max())} levels")

    if 'parent_id' in df.columns:
        avg_branching = df.groupby('parent_id').size().mean()
        print(f"3. Average Branching Factor: {avg_branching:.2f}")

    if 'topic_level' in df.columns:
        print("\n4. Node Distribution per Hierarchy Level:")
        dist = df['topic_level'].value_counts().sort_index()
        for lvl, count in dist.items():
            pct = (count / total_nodes) * 100
            print(f"   - Level {int(lvl)}: {count} nodes ({pct:.1f}%)")

    print("="*75)

if __name__ == "__main__":
    analyze_hierarchy()
