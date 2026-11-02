from typing import List, Tuple
import networkx as nx
from src.schemas.hierarchy import TopologyMetrics

class DAGValidator:
    def __init__(self, nodes: List[int], edges: List[Tuple[int, int]], levels: dict):
        self.nodes = nodes
        self.edges = edges
        self.levels = levels
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(self.nodes)
        self.graph.add_edges_from(self.edges)

    def calculate_metrics(self) -> TopologyMetrics:
        total_nodes = self.graph.number_of_nodes()
        total_edges = self.graph.number_of_edges()
        is_dag = nx.is_directed_acyclic_graph(self.graph)
        
        root_nodes = [n for n, d in self.graph.in_degree() if d == 0]
        leaf_nodes = [n for n, d in self.graph.out_degree() if d == 0]
        
        non_leaf_nodes = [n for n, d in self.graph.out_degree() if d > 0]
        if non_leaf_nodes:
            total_branching = sum(self.graph.out_degree(n) for n in non_leaf_nodes)
            average_branching = round(total_branching / len(non_leaf_nodes), 2)
        else:
            average_branching = 0.0

        max_depth = max(self.levels.values()) if self.levels else 0
        intermediate_nodes = [n for n, lvl in self.levels.items() if 1 < lvl < max_depth]
        intermediate_count = len(intermediate_nodes)
        intermediate_ratio = round(intermediate_count / total_nodes, 3) if total_nodes > 0 else 0.0

        return TopologyMetrics(
            total_nodes=total_nodes,
            total_edges=total_edges,
            max_depth=max_depth,
            average_branching_factor=average_branching,
            intermediate_nodes_count=intermediate_count,
            intermediate_nodes_ratio=intermediate_ratio,
            is_dag=is_dag,
            leaf_nodes_count=len(leaf_nodes),
            root_nodes_count=len(root_nodes)
        )
