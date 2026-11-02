import json
from pathlib import Path
import pandas as pd
from typing import Dict, Any, List
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

    def _read_table_robust(self, target_path: str) -> pd.DataFrame:
        encodings = ["utf-8-sig", "utf-16", "utf-16-le", "utf-8", "cp1256"]
        separators = [None, ",", "\t", ";"]
        
        for enc in encodings:
            for sep in separators:
                try:
                    df = pd.read_csv(target_path, encoding=enc, sep=sep, engine="python")
                    cleaned_cols = [str(c).strip().replace("\ufeff", "") for c in df.columns]
                    cleaned_cols_lower = [c.lower() for c in cleaned_cols]
                    
                    if "topic_id" in cleaned_cols_lower and "parent_id" in cleaned_cols_lower:
                        df.columns = cleaned_cols
                        return df
                except Exception:
                    continue
        
        raise ValueError(f"Unable to parse table structure correctly from: {target_path}")

    def run(self) -> Dict[str, Any]:
        local_path = Path("data/processed/topics.csv")
        target = str(local_path) if local_path.exists() else self.config.topics_csv_url
        
        df_topics = self._read_table_robust(target)
        df_topics = df_topics.loc[:, ~df_topics.columns.duplicated()].copy()
        df_topics.columns = [c.strip() for c in df_topics.columns]

        df_topics["parent_id"] = pd.to_numeric(
            df_topics["parent_id"].astype(str).str.replace("NULL", "", case=False).str.strip(),
            errors="coerce"
        )
        df_topics["topic_id"] = pd.to_numeric(df_topics["topic_id"], errors="coerce").fillna(0).astype(int)
        df_topics["topic_level"] = pd.to_numeric(df_topics["topic_level"], errors="coerce").fillna(1).astype(int)
        
        if "display_order" in df_topics.columns:
            df_topics["display_order"] = pd.to_numeric(df_topics["display_order"], errors="coerce").fillna(0).astype(int)
        else:
            df_topics["display_order"] = 0
            
        if "is_leaf" in df_topics.columns:
            df_topics["is_leaf"] = pd.to_numeric(df_topics["is_leaf"], errors="coerce").fillna(0).astype(int)
        else:
            df_topics["is_leaf"] = 0

        topics_records: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []

        for _, row in df_topics.iterrows():
            parent_val = int(row["parent_id"]) if pd.notna(row["parent_id"]) else None
            topic_val = int(row["topic_id"])
            
            record = row.to_dict()
            record["parent_id"] = parent_val
            record["topic_id"] = topic_val
            record["topic_level"] = int(row["topic_level"])
            record["display_order"] = int(row["display_order"])
            record["is_leaf"] = int(row["is_leaf"])
            topics_records.append(record)

            if parent_val is not None:
                edges.append({
                    "parent_id": parent_val,
                    "child_id": topic_val,
                    "relation_type": "subsumes"
                })

        with self.connection_manager.get_connection() as conn:
            init_hierarchy_schema(conn)
            repo = TopicRepository(conn)
            repo.insert_topics(topics_records)
            repo.insert_edges(edges)

            edge_tuples = [(e["parent_id"], e["child_id"]) for e in edges]
            node_ids = [r["topic_id"] for r in topics_records]
            
            closure_builder = ClosureTableBuilder(conn)
            closure_builder.build_from_edges(edge_tuples, node_ids)

            paths_data = [(r["topic_id"], str(r.get("topic_path", "")), r["topic_level"]) for r in topics_records]
            closure_builder.populate_materialized_paths(paths_data)

        levels_dict = {r["topic_id"]: r["topic_level"] for r in topics_records}
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
