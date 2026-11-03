from typing import Dict, Any, List, Tuple, Optional
import networkx as nx
from sqlite3 import Connection
from src.storage.repositories import TopicRepository, AtomRepository, RelationRepository

class KnowledgeGraphEngine:
    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def build_graph_from_database(self, conn: Connection) -> Tuple[int, int]:
        self.graph.clear()
        
        topic_repo = TopicRepository(conn)
        atom_repo = AtomRepository(conn)
        rel_repo = RelationRepository(conn)

        topics = topic_repo.get_all_topics()
        for t in topics:
            node_key = f"topic:{t['topic_id']}"
            self.graph.add_node(
                node_key,
                node_type="topic",
                raw_id=int(t["topic_id"]),
                title=str(t["title"]),
                level=int(t["topic_level"]),
                code=str(t.get("topic_code", ""))
            )

        atoms = atom_repo.get_all_atoms()
        for a in atoms:
            node_key = f"atom:{a['atom_id']}"
            self.graph.add_node(
                node_key,
                node_type="atom",
                raw_id=int(a["atom_id"]),
                title=str(a["element_title"]),
                role=str(a["element_type_en"]),
                macro=str(a["macro_category"]),
                topic_id=int(a["topic_id"])
            )

        topic_edges = topic_repo.get_all_edges()
        for e in topic_edges:
            src = f"topic:{e['parent_id']}"
            dst = f"topic:{e['child_id']}"
            if self.graph.has_node(src) and self.graph.has_node(dst):
                self.graph.add_edge(
                    src,
                    dst,
                    key=f"edge:{e['parent_id']}:{e['child_id']}:subsumes",
                    predicate="subsumes",
                    weight=1.0,
                    category="taxonomic"
                )

        relations = rel_repo.get_all_relations()
        for r in relations:
            src_type = str(r["source_type"]).strip().lower()
            dst_type = str(r["object_type"]).strip().lower()
            
            src = f"{src_type}:{r['source_id']}"
            dst = f"{dst_type}:{r['object_id']}"
            
            if not self.graph.has_node(src):
                self.graph.add_node(src, node_type=src_type, raw_id=int(r["source_id"]), title=src)
            if not self.graph.has_node(dst):
                self.graph.add_node(dst, node_type=dst_type, raw_id=int(r["object_id"]), title=dst)

            self.graph.add_edge(
                src,
                dst,
                key=f"rel:{r['relation_id']}",
                relation_id=int(r["relation_id"]),
                predicate=str(r["predicate"]),
                weight=float(r.get("weight", 1.0)),
                confidence=float(r.get("confidence_score", 1.0)),
                category="semantic"
            )

        return self.graph.number_of_nodes(), self.graph.number_of_edges()

    def get_top_hubs(self, top_k: int = 5) -> List[Dict[str, Any]]:
        degrees = dict(self.graph.degree())
        sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        hubs = []
        for node_id, deg in sorted_nodes:
            data = self.graph.nodes.get(node_id, {})
            hubs.append({
                "node_id": node_id,
                "degree": deg,
                "title": data.get("title", node_id),
                "node_type": data.get("node_type", "unknown")
            })
        return hubs

    def get_subgraph(self, center_node: str, depth: int = 1, max_nodes: int = 50) -> nx.MultiDiGraph:
        if not self.graph.has_node(center_node):
            return nx.MultiDiGraph()

        sub_nodes = {center_node}
        current_layer = {center_node}

        for _ in range(depth):
            next_layer = set()
            for node in current_layer:
                successors = set(self.graph.successors(node))
                predecessors = set(self.graph.predecessors(node))
                next_layer.update(successors | predecessors)
            
            sub_nodes.update(next_layer)
            current_layer = next_layer
            if len(sub_nodes) >= max_nodes:
                break

        final_nodes = list(sub_nodes)[:max_nodes]
        return self.graph.subgraph(final_nodes).copy()
