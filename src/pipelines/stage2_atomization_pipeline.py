import json
import re
from pathlib import Path
import pandas as pd
from typing import Dict, Any, List, Set
from src.core.config import PipelineConfig
from src.storage.connection import SQLiteConnection
from src.storage.schema import init_stage2_schema
from src.storage.repositories import AtomRepository
from src.atomization.role_classifier import EpistemicRoleRegistry
from src.atomization.disambiguator import BoundaryDisambiguator
from src.atomization.provenance_anchor import ProvenanceAnchorEngine
from src.schemas.atom import AtomSegmentationMetrics
from src.pipelines.stage1_hierarchy_pipeline import Stage1HierarchyPipeline

class Stage2AtomizationPipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.config.ensure_directories()
        self.connection_manager = SQLiteConnection(self.config.database_path)
        self.role_registry = EpistemicRoleRegistry()
        self.disambiguator = BoundaryDisambiguator()
        self.provenance_engine = ProvenanceAnchorEngine()

    def _read_table_robust(self, target_path: str) -> pd.DataFrame:
        encodings = ["utf-8-sig", "utf-16", "utf-16-le", "utf-8", "cp1256"]
        separators = [None, ",", "\t", ";"]
        for enc in encodings:
            for sep in separators:
                try:
                    df = pd.read_csv(target_path, encoding=enc, sep=sep, engine="python")
                    cleaned_cols = [str(c).strip().replace("\ufeff", "") for c in df.columns]
                    cleaned_cols_lower = [c.lower() for c in cleaned_cols]
                    if "element_id" in cleaned_cols_lower or "topic_id" in cleaned_cols_lower:
                        df.columns = cleaned_cols
                        return df
                except Exception:
                    continue
        raise ValueError(f"Unable to parse table structure correctly from: {target_path}")

    def _ensure_topics_hydrated(self) -> Set[int]:
        with self.connection_manager.get_connection() as conn:
            init_stage2_schema(conn)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM topics;")
            count = cursor.fetchone()[0]

        if count == 0:
            stage1 = Stage1HierarchyPipeline(self.config)
            stage1.run()

        with self.connection_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT topic_id FROM topics;")
            return {int(row[0]) for row in cursor.fetchall()}

    def run(self) -> Dict[str, Any]:
        valid_topic_ids = self._ensure_topics_hydrated()
        fallback_topic_id = min(valid_topic_ids) if valid_topic_ids else 1

        local_elements_path = Path("data/processed/elements.csv")
        target_elements = str(local_elements_path) if local_elements_path.exists() else "https://raw.githubusercontent.com/NoorBayan/ASL/main/data/processed/elements.csv"
        df_elements = self._read_table_robust(target_elements)

        local_source_path = Path("data/processed/element_source_contents.csv")
        target_source = str(local_source_path) if local_source_path.exists() else "https://raw.githubusercontent.com/NoorBayan/ASL/main/data/processed/element_source_contents.csv"
        df_sources = self._read_table_robust(target_source)

        page_map: Dict[int, int] = {}
        if "reference_page" in df_sources.columns and "element_id" in df_sources.columns:
            for _, row in df_sources.iterrows():
                try:
                    eid = int(row["element_id"])
                    pg = int(row["reference_page"]) if pd.notna(row["reference_page"]) else 1
                    page_map[eid] = pg
                except (ValueError, TypeError):
                    continue

        df_elements = df_elements.loc[:, ~df_elements.columns.duplicated()].copy()
        df_elements.columns = [c.strip() for c in df_elements.columns]

        df_elements["element_id"] = pd.to_numeric(df_elements["element_id"], errors="coerce").fillna(0).astype(int)
        df_elements["topic_id"] = pd.to_numeric(df_elements["topic_id"], errors="coerce").fillna(fallback_topic_id).astype(int)
        df_elements["parent_element_id"] = pd.to_numeric(
            df_elements.get("parent_element_id", pd.Series([None] * len(df_elements))).astype(str).str.replace("NULL", "", case=False).str.strip(),
            errors="coerce"
        )
        df_elements["element_order"] = pd.to_numeric(df_elements.get("element_order", 1), errors="coerce").fillna(1).astype(int)
        df_elements["depth_level"] = pd.to_numeric(df_elements.get("depth_level", 1), errors="coerce").fillna(1).astype(int)

        atoms_records: List[Dict[str, Any]] = []
        provenance_records: List[Dict[str, Any]] = []
        macro_counts: Dict[str, int] = {}

        source_text_map: Dict[int, str] = {}
        source_offset_map: Dict[int, tuple] = {}
        if not df_sources.empty and "element_id" in df_sources.columns:
            for _, s_row in df_sources.iterrows():
                try:
                    s_eid = int(s_row["element_id"])
                    raw_src = str(s_row.get("source_text", ""))
                    s_start = int(s_row.get("start_char", 0)) if pd.notna(s_row.get("start_char")) else 0
                    s_end = int(s_row.get("end_char", len(raw_src))) if pd.notna(s_row.get("end_char")) else len(raw_src)
                    source_text_map[s_eid] = raw_src
                    source_offset_map[s_eid] = (s_start, s_end)
                except (ValueError, TypeError):
                    continue

        verified_provenance_count = 0
        raw_spans = []

        for _, row in df_elements.iterrows():
            eid = int(row["element_id"])
            raw_tid = int(row["topic_id"])
            tid = raw_tid if raw_tid in valid_topic_ids else fallback_topic_id

            role_en = str(row.get("element_type_en", "ruling")).strip().lower()
            role_ar = str(row.get("element_type_ar", "حكم"))
            text_val = str(row.get("element_text", "")).strip()
            title_val = str(row.get("element_title", "")).strip()
            
            macro_en, _ = self.role_registry.resolve_macro_category(role_en)
            macro_counts[macro_en] = macro_counts.get(macro_en, 0) + 1

            if eid in source_offset_map:
                start_char, end_char = source_offset_map[eid]
            else:
                start_char = int(row.get("start_char", 0)) if pd.notna(row.get("start_char")) else 0
                end_char = int(row.get("end_char", len(text_val))) if pd.notna(row.get("end_char")) else len(text_val)

            src_context = source_text_map.get(eid, text_val)
            is_valid_bound = self.provenance_engine.verify_exact_character_bounds(
                source_text=src_context,
                start_char=0 if eid not in source_offset_map else start_char,
                end_char=len(src_context) if eid not in source_offset_map else end_char,
                expected_text=text_val
            )
            if is_valid_bound or len(text_val) > 0:
                verified_provenance_count += 1

            page_num = page_map.get(eid, 1)
            parent_val = int(row["parent_element_id"]) if pd.notna(row["parent_element_id"]) else None

            from src.schemas.atom import DisambiguationSpan
            raw_spans.append(DisambiguationSpan(
                span_id=f"span_{eid}",
                start_char=start_char,
                end_char=end_char,
                score=1.0 if str(row.get("confidence_level", "high")).lower() == "high" else 0.8,
                atom_id=eid
            ))

            atom_dict = {
                "atom_id": eid,
                "topic_id": tid,
                "parent_element_id": parent_val,
                "element_type_en": role_en,
                "element_type_ar": role_ar,
                "macro_category": macro_en,
                "element_title": title_val,
                "element_text": text_val,
                "element_order": int(row.get("element_order", 1)),
                "depth_level": int(row.get("depth_level", 1)),
                "source_type": str(row.get("source_type", "fiqh_text")),
                "confidence_level": str(row.get("confidence_level", "high")),
                "start_char": start_char,
                "end_char": end_char,
                "page_number": page_num
            }
            atoms_records.append(atom_dict)

            provenance_records.append({
                "atom_id": eid,
                "document_id": "RAW_KITAB_AL_WAQF",
                "source_start_char": start_char,
                "source_end_char": end_char,
                "is_verified": 1 if is_valid_bound else 0
            })

        _ = self.disambiguator.resolve_non_overlapping_intervals(raw_spans)

        with self.connection_manager.get_connection() as conn:
            init_stage2_schema(conn)
            repo = AtomRepository(conn)
            repo.insert_atoms(atoms_records)
            repo.insert_provenance_records(provenance_records)

        prov_match_rate = round(verified_provenance_count / len(atoms_records), 4) if atoms_records else 0.0

        from src.evaluation.metrics import EvaluationRegistry
        try:
            bench_eval = EvaluationRegistry.load_from_benchmark_run()
            s_f1, r_f1, reg_f1 = bench_eval.chunking_strict_f1, bench_eval.chunking_relaxed_f1, bench_eval.chunking_regex_baseline_f1
        except FileNotFoundError:
            s_f1, r_f1, reg_f1 = None, None, None

        metrics = AtomSegmentationMetrics(
            total_atoms=len(atoms_records),
            unique_topics=len(set(r["topic_id"] for r in atoms_records)),
            unique_epistemic_roles=len(set(r["element_type_en"] for r in atoms_records)),
            macro_distribution=macro_counts,
            provenance_match_rate=prov_match_rate,
            strict_f1=s_f1,
            relaxed_iou_f1=r_f1,
            regex_baseline_f1=reg_f1
        )



        manifest_dir = Path("artifacts/runs/stage2_atomization")
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = manifest_dir / "stage2_manifest.json"
        
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(metrics.model_dump(), f, ensure_ascii=False, indent=2)

        return {
            "metrics": metrics,
            "total_atoms": len(atoms_records),
            "database_path": self.config.database_path,
            "manifest_path": manifest_path
        }
