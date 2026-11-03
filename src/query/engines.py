import time
from typing import List, Dict, Any, Optional
from sqlite3 import Connection
import networkx as nx
from src.storage.repositories import TopicRepository, AtomRepository, RelationRepository
from src.schemas.query import StructuredQueryModel, UnifiedQueryResponse, QueryResultItem

class HierarchicalQueryEngine:
    def __init__(self, conn: Connection):
        self.conn = conn
        self.topic_repo = TopicRepository(conn)
        self.atom_repo = AtomRepository(conn)

    def execute_hierarchical(self, query: StructuredQueryModel) -> List[QueryResultItem]:
        results: List[QueryResultItem] = []
        if query.target_topic_id is None:
            return results

        descendants = self.topic_repo.get_descendants(
            topic_id=query.target_topic_id,
            max_depth=query.max_hops if query.max_hops > 0 else None
        )

        for d in descendants:
            results.append(
                QueryResultItem(
                    entity_id=d["topic_id"],
                    entity_type="topic",
                    title_or_text=d["title"],
                    role_or_predicate="subsumes",
                    depth_or_hop=d["depth"],
                    source_reference=d.get("topic_code", "")
                )
            )

        if query.filters.get("include_atoms", False):
            atoms = self.atom_repo.get_atoms_by_topic(query.target_topic_id)
            for a in atoms:
                results.append(
                    QueryResultItem(
                        entity_id=a["atom_id"],
                        entity_type="atom",
                        title_or_text=a["element_text"],
                        role_or_predicate=a["element_type_en"],
                        depth_or_hop=0,
                        source_reference=f"Page {a.get('page_number', 1)}"
                    )
                )

        return results


class SemanticQueryEngine:
    def __init__(self, graph: nx.MultiDiGraph):
        self.graph = graph

    def execute_traversal(self, query: StructuredQueryModel) -> List[QueryResultItem]:
        results: List[QueryResultItem] = []
        start_node = f"atom:{query.target_atom_id}" if query.target_atom_id else f"topic:{query.target_topic_id}"
        
        if not self.graph.has_node(start_node):
            return results

        visited = {start_node}
        queue = [(start_node, 0, [start_node])]

        while queue:
            curr_node, curr_hop, path = queue.pop(0)
            if curr_hop >= query.max_hops:
                continue

            edges = self.graph.out_edges(curr_node, data=True)
            for _, target, data in edges:
                if target not in visited:
                    visited.add(target)
                    pred = data.get("predicate", "related_to")
                    if query.relation_types and pred not in query.relation_types:
                        continue

                    node_data = self.graph.nodes.get(target, {})
                    entity_type = node_data.get("node_type", "unknown")
                    raw_id = node_data.get("raw_id", target)
                    title = node_data.get("title", target)
                    role = node_data.get("role", pred)

                    new_path = path + [f"--({pred})-->", target]
                    results.append(
                        QueryResultItem(
                            entity_id=raw_id,
                            entity_type=entity_type,
                            title_or_text=title,
                            role_or_predicate=pred,
                            depth_or_hop=curr_hop + 1,
                            path_trace=new_path,
                            confidence=float(data.get("confidence", 1.0))
                        )
                    )
                    queue.append((target, curr_hop + 1, new_path))

        return results


class HybridQueryEngine:
    def __init__(self, conn: Connection, graph: nx.MultiDiGraph):
        self.hierarchical_engine = HierarchicalQueryEngine(conn)
        self.semantic_engine = SemanticQueryEngine(graph)

    def execute_hybrid(self, query: StructuredQueryModel) -> List[QueryResultItem]:
        combined_results: List[QueryResultItem] = []
        topic_items = self.hierarchical_engine.execute_hierarchical(query)
        combined_results.extend(topic_items)

        if query.target_atom_id or (topic_items and query.max_hops > 0):
            semantic_items = self.semantic_engine.execute_traversal(query)
            combined_results.extend(semantic_items)

        seen = set()
        deduped = []
        for item in combined_results:
            key = (item.entity_type, item.entity_id, item.role_or_predicate)
            if key not in seen:
                seen.add(key)
                deduped.append(item)

        return deduped
