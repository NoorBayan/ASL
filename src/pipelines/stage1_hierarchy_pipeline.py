import json
from pathlib import Path
import pandas as pd
from typing import Dict, Any
from src.core.config import PipelineConfig
from src.storage.connection import SQLiteConnection
from src.storage.schema import init_hierarchy_schema
from src.storage.repositories import TopicRepository
from src.storage.closure_table import ClosureTableBuilder
from src.hierarchy.dag_validator import DAGValidator
from src.hierarchy.embeddings import PoincareProjectionCalculator

class Stage1HierarchyPipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.config.ensure_directories()
        self.connection_manager = SQLiteConnection(self.config.database_path)

    def _load_topics_dataframe(self) -> pd.DataFrame:
        local_file = Path("/content/ASL/data/processed/topics.csv")
        target_path = local_file if local_file.exists() else self.config.topics_csv_url
        
        encodings_to_try = ["utf-16", "utf-16-le", "utf-8-sig", "utf-8", "cp1256"]
        for enc in encodings_to_try:
            try:
                return pd.read_csv(target_path, encoding=enc)
            except (UnicodeDecodeError, UnicodeError):
                continue
        return pd.read_csv(target_path)

    def run(self) -> Dict[str, Any]:
        df_topics = self._load_topics_dataframe()
        df_topics["parent_id"] = df_topics["parent_id"].apply(
            lambda x: None if pd.isna(x) or str(x).strip().upper() == "NULL" or str(x).strip() == "" else int(float(x))
        )
        df_topics["topic_id"] = df_topics["topic_id"].astype(int)
        df_topics["topic_level"] = df_topics["topic_level"].astype(int)
        df_topics["display_order"] = df_topics["display_order"].fillna(0).astype(int)
        df_topics["is_leaf"] = df_topics["is_leaf"].fillna(0).astype(int)

        topics_records = df_topics.to_dict(orient="records")

        edges = []
        for _, row in df_topics.iterrows():
            if row["parent_id"] is not None:
                edges.append({
                    "parent_id": int(row["parent_id"]),
                    "child_id": int(row["topic_id"]),
                    "relation_type": "subsumes"
                })

        with self.connection_manager.get_connection() as conn:
            init_hierarchy_schema(conn)
            repo = TopicRepository(conn)
            repo.insert_topics(topics_records)
            repo.insert_edges(edges)

            edge_tuples = [(e["parent_id"], e["child_id"]) for e in edges]
            node_ids = [int(t["topic_id"]) for t in topics_records]
            
            closure_builder = ClosureTableBuilder(conn)
            closure_builder.build_from_edges(edge_tuples, node_ids)

            paths_data = [(int(t["topic_id"]), str(t["topic_path"]), int(t["topic_level"])) for t in topics_records]
            closure_builder.populate_materialized_paths(paths_data)

        levels_dict = {int(t["topic_id"]): int(t["topic_level"]) for t in topics_records}
        validator = DAGValidator(node_ids, edge_tuples, levels_dict)
        metrics = validator.calculate_metrics()

        poincare_calc = PoincareProjectionCalculator(max_level=metrics.max_depth)
        coordinates = poincare_calc.compute_coordinates(topics_records)

        manifest = {
            "metrics": metrics.model_dump(),
            "poincare_coordinates": [c.model_dump() for c in coordinates]
        }

        manifest_path = self.config.artifacts_dir / "stage1_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        return {
            "metrics": metrics,
            "coordinates": coordinates,
            "database_path": self.config.database_path,
            "manifest_path": manifest_path
        }
