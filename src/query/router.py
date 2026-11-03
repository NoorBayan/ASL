import time
from typing import Dict, Any, List
from sqlite3 import Connection
import networkx as nx
from src.schemas.query import StructuredQueryModel, UnifiedQueryResponse
from src.query.engines import HierarchicalQueryEngine, SemanticQueryEngine, HybridQueryEngine

class QueryRouter:
    def __init__(self, conn: Connection, graph: nx.MultiDiGraph):
        self.conn = conn
        self.graph = graph
        self.hierarchical_engine = HierarchicalQueryEngine(conn)
        self.semantic_engine = SemanticQueryEngine(graph)
        self.hybrid_engine = HybridQueryEngine(conn, graph)

    def route_and_execute(self, query: StructuredQueryModel) -> UnifiedQueryResponse:
        t_start = time.perf_counter()
        q_type = str(query.query_type).strip().lower()
        warnings = []
        engines_used = []

        if q_type == "hierarchical":
            engines_used.append("SQLite_ClosureTable")
            results = self.hierarchical_engine.execute_hierarchical(query)
        elif q_type in ["semantic", "multi_hop"]:
            engines_used.append("NetworkX_InProcessGraph")
            results = self.semantic_engine.execute_traversal(query)
        elif q_type == "hybrid":
            engines_used.extend(["SQLite_ClosureTable", "NetworkX_InProcessGraph"])
            results = self.hybrid_engine.execute_hybrid(query)
        else:
            engines_used.append("SQLite_Fallback")
            warnings.append(f"Unrecognized query_type '{q_type}'. Falling back to hierarchical.")
            results = self.hierarchical_engine.execute_hierarchical(query)

        t_end = time.perf_counter()
        latency_ms = round((t_end - t_start) * 1000.0, 3)

        return UnifiedQueryResponse(
            query_id=query.query_id,
            query_type=q_type,
            execution_engine=engines_used,
            status="success",
            results=results,
            result_count=len(results),
            execution_time_ms=latency_ms,
            warnings=warnings
        )
