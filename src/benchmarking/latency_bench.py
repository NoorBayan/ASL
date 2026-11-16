import time
import numpy as np
from typing import Dict, Any, List
import networkx as nx
from src.schemas.query import StructuredQueryModel, LatencyMetricRow
from src.query.router import QueryRouter

class LatencyBenchmarkSuite:
    def __init__(self, conn_or_manager: Any, graph: nx.MultiDiGraph):
        self.conn_or_manager = conn_or_manager
        self.graph = graph
        self.router = QueryRouter(conn_or_manager, graph)
        self.topic_ids = [
            int(n.split(":")[1]) for n in graph.nodes if n.startswith("topic:") and n.split(":")[1].isdigit()
        ]
        self.atom_ids = [
            int(n.split(":")[1]) for n in graph.nodes if n.startswith("atom:") and n.split(":")[1].isdigit()
        ]

    def _execute_workload(self, queries: List[StructuredQueryModel], warm_up: int) -> List[float]:
        for i in range(min(warm_up, len(queries))):
            self.router.route_and_execute(queries[i])

        latencies_ms: List[float] = []
        for q in queries:
            t0 = time.perf_counter()
            self.router.route_and_execute(q)
            t1 = time.perf_counter()
            latencies_ms.append((t1 - t0) * 1000.0)

        return latencies_ms

    def _compute_row(self, query_type: str, latencies: List[float]) -> LatencyMetricRow:
        arr = np.array(latencies, dtype=np.float64)
        return LatencyMetricRow(
            query_type=query_type,
            p50_median=round(float(np.percentile(arr, 50)), 2),
            p95=round(float(np.percentile(arr, 95)), 2),
            p99=round(float(np.percentile(arr, 99)), 2),
            mean=round(float(np.mean(arr)), 2),
            min_val=round(float(np.min(arr)), 2),
            max_val=round(float(np.max(arr)), 2),
            total_queries=len(latencies)
        )

    def run_table2_benchmark(self, num_queries: int = 1000, warm_up: int = 50) -> Dict[str, LatencyMetricRow]:
        results: Dict[str, LatencyMetricRow] = {}

        hierarchical_queries = [
            StructuredQueryModel(
                query_id=f"bench_h_{i}",
                query_type="hierarchical",
                target_topic_id=self.topic_ids[i % len(self.topic_ids)] if self.topic_ids else 1,
                max_hops=0,
                filters={"include_atoms": False}
            )
            for i in range(num_queries)
        ]
        h_latencies = self._execute_workload(hierarchical_queries, warm_up=warm_up)
        results["Hierarchical Retrieval (SQLite)"] = self._compute_row("Hierarchical Retrieval (SQLite)", h_latencies)

        for hops in [1, 2, 3]:
            traversal_queries = [
                StructuredQueryModel(
                    query_id=f"bench_sem_{hops}hop_{i}",
                    query_type="semantic",
                    target_atom_id=self.atom_ids[i % len(self.atom_ids)] if self.atom_ids else None,
                    target_topic_id=self.topic_ids[i % len(self.topic_ids)] if not self.atom_ids and self.topic_ids else None,
                    max_hops=hops,
                    approved_only=True
                )
                for i in range(num_queries)
            ]
            t_latencies = self._execute_workload(traversal_queries, warm_up=warm_up)
            workload_name = f"{hops}-Hop Semantic Traversal"
            results[workload_name] = self._compute_row(workload_name, t_latencies)

        return results
