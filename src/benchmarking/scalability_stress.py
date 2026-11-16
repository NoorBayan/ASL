import time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from typing import List, Dict, Any, Optional
from sqlite3 import Connection
import networkx as nx
from src.schemas.query import StructuredQueryModel, ScalabilityLevelResult
from src.query.router import QueryRouter

INGESTION_FRACTIONS = [
    ("20%", 0.20),
    ("40%", 0.40),
    ("60%", 0.60),
    ("80%", 0.80),
    ("100%", 1.00)
]

class ScalabilityStressTester:
    def __init__(self, conn_or_manager: Any, graph: nx.MultiDiGraph):
        self.conn_or_manager = conn_or_manager
        self.graph = graph
        self.topic_nodes = sorted([n for n in graph.nodes if n.startswith("topic:")])
        self.atom_nodes = sorted([n for n in graph.nodes if n.startswith("atom:")])

    def _build_ingestion_subgraph(self, fraction: float) -> nx.MultiDiGraph:
        if fraction >= 1.0:
            return self.graph

        topic_slice_count = max(1, int(len(self.topic_nodes) * fraction))
        selected_topics = set(self.topic_nodes[:topic_slice_count])

        selected_nodes = set(selected_topics)
        for atom_node in self.atom_nodes:
            atom_data = self.graph.nodes.get(atom_node, {})
            parent_topic_id = atom_data.get("topic_id")
            if parent_topic_id is not None and f"topic:{parent_topic_id}" in selected_topics:
                selected_nodes.add(atom_node)

        if len(selected_nodes) < 2:
            atom_slice_count = max(1, int(len(self.atom_nodes) * fraction))
            selected_nodes.update(self.atom_nodes[:atom_slice_count])

        return self.graph.subgraph(selected_nodes).copy()

    def run_concurrency_stress(self, max_workers: int = 10, queries_per_level: int = 100) -> List[ScalabilityLevelResult]:
        results: List[ScalabilityLevelResult] = []
        base_edges: Optional[int] = None
        base_latency: Optional[float] = None

        for idx, (label, fraction) in enumerate(INGESTION_FRACTIONS):
            subgraph = self._build_ingestion_subgraph(fraction)
            level_router = QueryRouter(self.conn_or_manager, subgraph)

            current_atoms = [
                int(n.split(":")[1]) for n in subgraph.nodes if n.startswith("atom:") and n.split(":")[1].isdigit()
            ]
            if not current_atoms:
                current_atoms = [
                    int(n.split(":")[1]) for n in self.atom_nodes if n.split(":")[1].isdigit()
                ]

            def execute_worker(query_index: int) -> float:
                target_atom = current_atoms[query_index % len(current_atoms)]
                q = StructuredQueryModel(
                    query_id=f"stress_{label}_{query_index}",
                    query_type="semantic",
                    target_atom_id=target_atom,
                    max_hops=3,
                    approved_only=True
                )
                t_start = time.perf_counter()
                level_router.route_and_execute(q)
                t_end = time.perf_counter()
                return (t_end - t_start) * 1000.0

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                measured_latencies = list(executor.map(execute_worker, range(queries_per_level)))

            measured_median = round(float(np.median(measured_latencies)), 2)
            actual_nodes = subgraph.number_of_nodes()
            actual_edges = subgraph.number_of_edges()

            if idx == 0 or base_edges is None:
                base_edges = actual_edges if actual_edges > 0 else 1
            if idx == 0 or base_latency is None:
                base_latency = measured_median if measured_median > 0 else 1.0

            edge_growth = round(((actual_edges - base_edges) / base_edges) * 100.0, 1)
            latency_growth = round(((measured_median - base_latency) / base_latency) * 100.0, 1)

            results.append(
                ScalabilityLevelResult(
                    ingestion_level=label,
                    nodes_count=actual_nodes,
                    edges_count=actual_edges,
                    edge_growth_percent=edge_growth,
                    concurrent_threads=max_workers,
                    median_latency_ms=measured_median,
                    latency_growth_percent=latency_growth
                )
            )

        return results
