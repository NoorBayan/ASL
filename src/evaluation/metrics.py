import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

class EvaluationMetricsCalculator:
    @staticmethod
    def compute_exact_f1(gold_items: Set[Any], pred_items: Set[Any]) -> float:
        if not gold_items and not pred_items:
            return 1.0
        if not gold_items or not pred_items:
            return 0.0
        tp = len(gold_items & pred_items)
        prec = tp / len(pred_items) if pred_items else 0.0
        rec = tp / len(gold_items) if gold_items else 0.0
        return round((2 * prec * rec) / (prec + rec), 4) if (prec + rec) > 0 else 0.0

    @staticmethod
    def compute_span_iou_f1(gold_spans: List[Tuple[int, int]], pred_spans: List[Tuple[int, int]], iou_thresh: float = 0.5) -> float:
        if not gold_spans and not pred_spans:
            return 1.0
        if not gold_spans or not pred_spans:
            return 0.0
        matched_gold = set()
        matched_pred = set()
        for g_i, (g_s, g_e) in enumerate(gold_spans):
            for p_i, (p_s, p_e) in enumerate(pred_spans):
                if p_i in matched_pred:
                    continue
                inter = max(0, min(g_e, p_e) - max(g_s, p_s))
                union = (g_e - g_s) + (p_e - p_s) - inter
                iou = (inter / union) if union > 0 else 0.0
                if iou >= iou_thresh:
                    matched_gold.add(g_i)
                    matched_pred.add(p_i)
                    break
        tp = len(matched_gold)
        fp = len(pred_spans) - len(matched_pred)
        fn = len(gold_spans) - len(matched_gold)
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        return round((2 * prec * rec) / (prec + rec), 4) if (prec + rec) > 0 else 0.0

class EvaluationRegistry(BaseModel):
    chunking_relaxed_f1: float = Field(default=0.0)
    chunking_strict_f1: float = Field(default=0.0)
    chunking_regex_baseline_f1: float = Field(default=0.0)
    chunking_gpt4_baseline_f1: float = Field(default=0.0)
    relation_proposed_f1: float = Field(default=0.0)
    relation_regex_baseline_f1: float = Field(default=0.0)
    relation_gpt4_baseline_f1: float = Field(default=0.0)
    inter_annotator_fleiss_kappa: float = Field(default=0.0)
    inter_annotator_krippendorff_alpha: float = Field(default=0.0)

    @classmethod
    def load_from_benchmark_run(cls, benchmark_file: Optional[Path] = None) -> "EvaluationRegistry":
        target_path = benchmark_file or Path("artifacts/runs/evaluation/benchmark_gold_standard.json")
        if not target_path.exists():
            raise FileNotFoundError(
                f"Benchmark evaluation results file not found at: '{target_path}'. "
                "Execute the model evaluation workflow against the gold-standard corpus to generate genuine metrics."
            )
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return cls(**data)

    def get_comparative_table(self) -> List[Dict[str, Any]]:
        return [
            {
                "Task": "Semantic Knowledge Chunking (Atoms)",
                "Proposed Model": self.chunking_relaxed_f1,
                "Regex Baseline": self.chunking_regex_baseline_f1,
                "LLM Baseline (GPT-4)": self.chunking_gpt4_baseline_f1,
                "Metric": "F1-Score (IoU >= 0.5)"
            },
            {
                "Task": "Semantic Relation Extraction",
                "Proposed Model": self.relation_proposed_f1,
                "Regex Baseline": self.relation_regex_baseline_f1,
                "LLM Baseline (GPT-4)": self.relation_gpt4_baseline_f1,
                "Metric": "F1-Score (Multi-class Macro)"
            }
        ]
