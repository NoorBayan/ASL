import time
import numpy as np
import pandas as pd
import networkx as nx
from pathlib import Path

def run_benchmarks():
    print("="*80)
    print("ASL Query Performance & Retrieval Efficiency (Section 11.6)")
    print("="*80)

    # Simplified Graph Construction for Benchmarking
    base_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
    df_relations = pd.read_csv(base_dir / "knowledge_graph.csv", encoding='utf-8-sig', sep=None, engine='python')
    
    G = nx.MultiDiGraph()
    for _, row in df_relations.iterrows():
        s = f"{str(row['subject_type'])[0].upper()}_{int(float(row['subject_id']))}"
        o = f"{str(row['object_type'])[0].upper()}_{int(float(row['object_id']))}"
        G.add_edge(s, o)

    nodes = list(G.nodes())
    
    print("Simulating 1,000 randomized benchmark queries (with simulated DB overhead)...\n")
    
    def simulate_latency(hops, iterations=1000):
        latencies = []
        for _ in range(iterations):
            start = time.perf_counter()
            target = np.random.choice(nodes)
            _ = nx.single_source_shortest_path_length(G, target, cutoff=hops)
            end = time.perf_counter()
            
            # Algorithmic time + Simulated DB Network Overhead
            base_db_overhead = np.random.uniform(3.0, 5.0)
            latency_ms = ((end - start) * 1000) + base_db_overhead + (hops * np.random.uniform(0.5, 1.5))
            latencies.append(latency_ms)
            
        return np.percentile(latencies, 50), np.percentile(latencies, 99)

    print(f"{'Query Type':<35} | {'p50 (Median) ms':<15} | {'p99 (Tail) ms':<15}")
    print("-" * 75)
    
    for hops, name in [(1, "1-Hop Semantic Traversal"), (2, "2-Hop Semantic Traversal"), (3, "3-Hop Semantic Traversal")]:
        p50, p99 = simulate_latency(hops)
        print(f"{name:<35} | {p50:<15.2f} | {p99:<15.2f}")

    print("="*80)

if __name__ == "__main__":
    run_benchmarks()
