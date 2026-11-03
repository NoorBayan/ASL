import time
import numpy as np
from typing import List, Dict, Any
from sqlite3 import Connection
import networkx as nx
from src.schemas.query import StructuredQueryModel, LatencyMetricRow
from src.query.router import QueryRouter

class LatencyBenchmarkSuite:
    def __init__(self, conn_or_manager: Any, graph: nx.MultiDiGraph):
        self.router = QueryRouter(conn_or_manager, graph)
        self.topics = [int(n.split(":")[1]) for n in graph.nodes if n.startswith("topic:")]
        self.atoms = [int(n.split(":")[1]) for n in graph.nodes if n.startswith("atom:")]

    def run_table2_benchmark(self, num_queries: int = 1000, warm_up: int = 50) -> Dict[str, LatencyMetricRow]:
        benchmark_configs = [
            ("Hierarchical Retrieval (Relational)", "hierarchical", 1, True),
            ("1-Hop Semantic Traversal (Graph)", "semantic", 1, False),
            ("2-Hop Semantic Traversal (Graph)", "semantic", 2, False),
            ("3-Hop Semantic Traversal (Graph)", "semantic", 3, False),
        ]

        summary_results: Dict[str, LatencyMetricRow] = {}

        for label, q_type, hops, is_topic in benchmark_configs:
            pool = self.topics if is_topic else self.atoms
            if not pool:
                continue

            for w in range(warm_up):
                tid = pool[w % len(pool)]
                q = StructuredQueryModel(
                    query_id=f"warmup_{w}",
                    query_type=q_type,
                    target_topic_id=tid if is_topic else None,
                    target_atom_id=None if is_topic else tid,
                    max_hops=hops
                )
                self.router.route_and_execute(q)

            latencies: List[float] = []
            for i in range(num_queries):
                tid = pool[i % len(pool)]
                q = StructuredQueryModel(
                    query_id=f"bench_{i}",
                    query_type=q_type,
                    target_topic_id=tid if is_topic else None,
                    target_atom_id=None if is_topic else tid,
                    max_hops=hops
                )
                res = self.router.route_and_execute(q)
                latencies.append(res.execution_time_ms)

            arr = np.array(latencies)
            summary_results[label] = LatencyMetricRow(
                query_type=label,
                p50_median=round(float(np.percentile(arr, 50)), 2),
                p95=round(float(np.percentile(arr, 95)), 2),
                p99=round(float(np.percentile(arr, 99)), 2),
                mean=round(float(np.mean(arr)), 2),
                min_val=round(float(np.min(arr)), 2),
                max_val=round(float(np.max(arr)), 2),
                total_queries=num_queries
            )

        return summary_results
