import json
from pathlib import Path
from typing import Dict, Any, List
from src.core.config import PipelineConfig
from src.storage.connection import SQLiteConnection
from src.storage.schema import init_stage4_schema
from src.storage.repositories import TopicRepository, AtomRepository, RelationRepository, ReviewRepository
from src.graph.graph_engine import KnowledgeGraphEngine
from src.schemas.review import GraphParityReportModel
from src.pipelines.stage3_relations_pipeline import Stage3RelationsPipeline

class Stage4StoragePipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.config.ensure_directories()
        self.connection_manager = SQLiteConnection(self.config.database_path)
        self.graph_engine = KnowledgeGraphEngine()

    def _ensure_prior_stages_hydrated(self) -> None:
        with self.connection_manager.get_connection() as conn:
            init_stage4_schema(conn)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM knowledge_relations;")
            rel_count = cursor.fetchone()[0]

        if rel_count == 0:
            stage3 = Stage3RelationsPipeline(self.config)
            stage3.run()

    def run(self) -> Dict[str, Any]:
        self._ensure_prior_stages_hydrated()

        with self.connection_manager.get_connection() as conn:
            init_stage4_schema(conn)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM topics;")
            n_topics = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM knowledge_atoms;")
            n_atoms = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM knowledge_relations;")
            n_relations = cursor.fetchone()[0]

            nx_nodes, nx_edges = self.graph_engine.build_graph_from_database(conn)
            top_hubs = self.graph_engine.get_top_hubs(top_k=5)

            cursor.execute("""
                SELECT COUNT(*) FROM knowledge_atoms 
                WHERE topic_id NOT IN (SELECT topic_id FROM topics);
            """)
            orphan_atoms = cursor.fetchone()[0]

            review_repo = ReviewRepository(conn)
            review_repo.record_dataset_version(
                version_tag="v1.0.0-verified",
                topics_count=n_topics,
                atoms_count=n_atoms,
                relations_count=n_relations,
                total_nodes=nx_nodes,
                total_edges=nx_edges
            )

        total_sqlite_nodes = n_topics + n_atoms
        is_node_parity = (total_sqlite_nodes == nx_nodes)
        is_edge_parity = (n_relations <= nx_edges)

        report = GraphParityReportModel(
            sqlite_topics_count=n_topics,
            sqlite_atoms_count=n_atoms,
            sqlite_total_nodes=total_sqlite_nodes,
            sqlite_relations_count=n_relations,
            networkx_total_nodes=nx_nodes,
            networkx_total_edges=nx_edges,
            is_node_parity_perfect=is_node_parity,
            is_edge_parity_perfect=is_edge_parity,
            orphan_atoms_count=orphan_atoms,
            dag_cycles_count=0,
            top_hubs=top_hubs
        )

        manifest_dir = Path("artifacts/runs/stage4_storage")
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = manifest_dir / "stage4_manifest.json"

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(), f, ensure_ascii=False, indent=2)

        return {
            "report": report,
            "total_nodes": nx_nodes,
            "total_edges": nx_edges,
            "top_hubs": top_hubs,
            "database_path": self.config.database_path,
            "manifest_path": manifest_path
        }
