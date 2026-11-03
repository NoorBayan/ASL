import time
from typing import Dict, Any, List, Optional
from sqlite3 import Connection
from contextlib import contextmanager
import networkx as nx
from src.schemas.query import StructuredQueryModel, UnifiedQueryResponse
from src.query.engines import HierarchicalQueryEngine, SemanticQueryEngine, HybridQueryEngine

class QueryRouter:
    def __init__(self, conn_or_manager: Any, graph: nx.MultiDiGraph):
        self.conn_or_manager = conn_or_manager
        self.graph = graph
        self.semantic_engine = SemanticQueryEngine(graph)

    @contextmanager
    def _resolve_connection(self, override_conn: Optional[Connection] = None):
        if override_conn is not None:
            yield override_conn
        elif hasattr(self.conn_or_manager, "get_connection"):
            with self.conn_or_manager.get_connection() as conn:
                yield conn
        elif isinstance(self.conn_or_manager, Connection):
            yield self.conn_or_manager
        else:
            raise ValueError("Invalid connection source provided to QueryRouter")

    def route_and_execute(self, query: StructuredQueryModel, conn: Optional[Connection] = None) -> UnifiedQueryResponse:
        t_start = time.perf_counter()
        q_type = str(query.query_type).strip().lower()
        warnings = []
        engines_used = []

        with self._resolve_connection(conn) as active_conn:
            if q_type == "hierarchical":
                engines_used.append("SQLite_ClosureTable")
                h_engine = HierarchicalQueryEngine(active_conn)
                results = h_engine.execute_hierarchical(query)
            elif q_type in ["semantic", "multi_hop"]:
                engines_used.append("NetworkX_InProcessGraph")
                results = self.semantic_engine.execute_traversal(query)
            elif q_type == "hybrid":
                engines_used.extend(["SQLite_ClosureTable", "NetworkX_InProcessGraph"])
                hy_engine = HybridQueryEngine(active_conn, self.graph)
                results = hy_engine.execute_hybrid(query)
            else:
                engines_used.append("SQLite_Fallback")
                warnings.append(f"Unrecognized query_type '{q_type}'. Falling back to hierarchical.")
                h_engine = HierarchicalQueryEngine(active_conn)
                results = h_engine.execute_hierarchical(query)

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
