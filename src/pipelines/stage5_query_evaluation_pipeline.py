import json
from pathlib import Path
from typing import Dict, Any
from src.core.config import PipelineConfig
from src.storage.connection import SQLiteConnection
from src.graph.graph_engine import KnowledgeGraphEngine
from src.query.router import QueryRouter
from src.benchmarking.latency_bench import LatencyBenchmarkSuite
from src.benchmarking.scalability_stress import ScalabilityStressTester
from src.evaluation.metrics import EvaluationRegistry
from src.pipelines.stage4_storage_pipeline import Stage4StoragePipeline

class Stage5QueryEvaluationPipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.config.ensure_directories()
        self.connection_manager = SQLiteConnection(self.config.database_path)
        self.graph_engine = KnowledgeGraphEngine()
        self.eval_registry = EvaluationRegistry()

    def _ensure_prior_stages_hydrated(self) -> None:
        with self.connection_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_relations';")
            if not cursor.fetchone():
                stage4 = Stage4StoragePipeline(self.config)
                stage4.run()
                return

            cursor.execute("SELECT COUNT(*) FROM knowledge_relations;")
            if cursor.fetchone()[0] == 0:
                stage4 = Stage4StoragePipeline(self.config)
                stage4.run()

    def run(self) -> Dict[str, Any]:
        self._ensure_prior_stages_hydrated()

        with self.connection_manager.get_connection() as conn:
            self.graph_engine.build_graph_from_database(conn)
            router = QueryRouter(conn, self.graph_engine.graph)
            
            latency_suite = LatencyBenchmarkSuite(conn, self.graph_engine.graph)
            table2_results = latency_suite.run_table2_benchmark(num_queries=1000, warm_up=50)

            stress_tester = ScalabilityStressTester(conn, self.graph_engine.graph)
            figure10_results = stress_tester.run_concurrency_stress(max_workers=10, queries_per_level=100)

        manifest_dir = Path("artifacts/runs/stage5_query_evaluation")
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = manifest_dir / "stage5_manifest.json"

        manifest_data = {
            "table2_latency_benchmark": {k: v.model_dump() for k, v in table2_results.items()},
            "figure10_scalability_stress": [r.model_dump() for r in figure10_results],
            "evaluation_metrics": self.eval_registry.model_dump()
        }

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, ensure_ascii=False, indent=2)

        return {
            "table2_results": table2_results,
            "figure10_results": figure10_results,
            "evaluation_registry": self.eval_registry,
            "manifest_path": manifest_path
        }
