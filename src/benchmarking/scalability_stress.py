import time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from typing import List, Dict, Any
from sqlite3 import Connection
import networkx as nx
from src.schemas.query import StructuredQueryModel, ScalabilityLevelResult
from src.query.router import QueryRouter

SCALABILITY_LEVELS = [
    {"level": "20%", "nodes": 421, "edges": 2977},
    {"level": "40%", "nodes": 523, "edges": 5646},
    {"level": "60%", "nodes": 562, "edges": 7941},
    {"level": "80%", "nodes": 647, "edges": 10327},
    {"level": "100%", "nodes": 703, "edges": 12980}
]

class ScalabilityStressTester:
    def __init__(self, conn_or_manager: Any, graph: nx.MultiDiGraph):
        self.router = QueryRouter(conn_or_manager, graph)
        self.atom_nodes = [int(n.split(":")[1]) for n in graph.nodes if n.startswith("atom:")]

    def run_concurrency_stress(self, max_workers: int = 10, queries_per_level: int = 100) -> List[ScalabilityLevelResult]:
        results: List[ScalabilityLevelResult] = []
        base_edges = 2977
        base_latency = 40.00

        for idx, lvl in enumerate(SCALABILITY_LEVELS):
            target_atoms = self.atom_nodes[:int(len(self.atom_nodes) * ((idx + 1) * 0.2))]
            if not target_atoms:
                target_atoms = self.atom_nodes

            def worker_query(q_id: int) -> float:
                atom_id = target_atoms[q_id % len(target_atoms)]
                q = StructuredQueryModel(
                    query_id=f"stress_{lvl['level']}_{q_id}",
                    query_type="semantic",
                    target_atom_id=atom_id,
                    max_hops=3
                )
                t0 = time.perf_counter()
                self.router.route_and_execute(q)
                t1 = time.perf_counter()
                return (t1 - t0) * 1000.0
                
            target_node_count = int(lvl["nodes"])
            sub_nodes = list(self.graph.nodes)[:target_node_count]
            subgraph = self.graph.subgraph(sub_nodes).copy()
            level_router = QueryRouter(self.conn_or_manager, subgraph)

            level_atoms = [int(n.split(":")[1]) for n in subgraph.nodes if n.startswith("atom:")]
            if not level_atoms:
                level_atoms = self.atom_nodes[:target_node_count]

            def worker_query_exec(q_id: int) -> float:
                atom_id = level_atoms[q_id % len(level_atoms)]
                q = StructuredQueryModel(
                    query_id=f"stress_{lvl['level']}_{q_id}",
                    query_type="semantic",
                    target_atom_id=atom_id,
                    max_hops=3
                )
                t0 = time.perf_counter()
                level_router.route_and_execute(q)
                t1 = time.perf_counter()
                return (t1 - t0) * 1000.0

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                latencies = list(executor.map(worker_query_exec, range(queries_per_level)))

            measured_median = round(float(np.median(latencies)), 2)
            if idx == 0 or base_latency is None:
                base_latency = measured_median

            actual_edges = subgraph.number_of_edges()
            edge_growth = round(((actual_edges - base_edges) / base_edges) * 100.0, 1) if base_edges > 0 else 0.0
            latency_growth = round(((measured_median - base_latency) / base_latency) * 100.0, 1) if base_latency > 0 else 0.0

            results.append(
                ScalabilityLevelResult(
                    ingestion_level=lvl["level"],
                    nodes_count=subgraph.number_of_nodes(),
                    edges_count=actual_edges,
                    edge_growth_percent=edge_growth,
                    concurrent_threads=max_workers,
                    median_latency_ms=measured_median,
                    latency_growth_percent=latency_growth
                )
            )

        return results
