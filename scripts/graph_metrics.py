import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

def analyze_graph():
    print("="*75)
    print("ASL Graph Structural Metrics & Topology (Section 11.5)")
    print("="*75)

    base_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
    df_topics = pd.read_csv(base_dir / "topics.csv", encoding='utf-8-sig', sep=None, engine='python')
    df_elements = pd.read_csv(base_dir / "elements.csv", encoding='utf-8-sig', sep=None, engine='python')
    df_relations = pd.read_csv(base_dir / "knowledge_graph.csv", encoding='utf-8-sig', sep=None, engine='python')

    # Construct Directed Multi-Graph (Allows multiple typed edges between nodes)
    G = nx.MultiDiGraph()

    # Add Hierarchical Edges
    for _, row in df_topics.dropna(subset=['parent_id']).iterrows():
        G.add_edge(f"T_{int(float(row['parent_id']))}", f"T_{int(row['topic_id'])}")

    # Add Containment Edges
    for _, row in df_elements.dropna(subset=['topic_id']).iterrows():
        G.add_edge(f"T_{int(float(row['topic_id']))}", f"E_{int(row['element_id'])}")

    # Add Semantic Edges
    for _, row in df_relations.iterrows():
        s = f"T_{int(float(row['subject_id']))}" if str(row['subject_type']).lower() == 'topic' else f"E_{int(float(row['subject_id']))}"
        o = f"T_{int(float(row['object_id']))}" if str(row['object_type']).lower() == 'topic' else f"E_{int(float(row['object_id']))}"
        G.add_edge(s, o)

    total_nodes = G.number_of_nodes()
    total_edges = G.number_of_edges()
    avg_degree = (2 * total_edges) / total_nodes if total_nodes > 0 else 0

    print(f"1. Total Unique Nodes: {total_nodes:,}")
    print(f"2. Total Typed Edges: {total_edges:,}")
    print(f"3. Average Node Degree: {avg_degree:.2f}\n")

    print("Generating Topology Visualizations...")
    sns.set_style("whitegrid")
    degrees = [d for n, d in G.degree()]

    # Figure 1: Degree Distribution
    plt.figure(figsize=(8, 5))
    sns.histplot(degrees, bins=40, kde=True, color='#2c3e50', log_scale=(False, True))
    plt.title('Node Degree Distribution (Scale-Free Topology)', fontweight='bold')
    plt.xlabel('Degree (Number of Connections)')
    plt.ylabel('Count of Nodes (Log Scale)')
    plt.tight_layout()
    plt.savefig(base_dir.parent.parent / "degree_distribution.png") # يحفظ الصورة
    plt.show()

    print("="*75)

if __name__ == "__main__":
    analyze_graph()
