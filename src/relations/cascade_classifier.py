from typing import Dict, Tuple, Any, List

class CascadingRelationClassifier:
    def __init__(self, confidence_threshold: float = 0.85):
        self.confidence_threshold = confidence_threshold

    def score_relation(self, raw_confidence: Any, weight: float) -> Tuple[float, str]:
        if isinstance(raw_confidence, (int, float)):
            score = float(raw_confidence)
        else:
            val_str = str(raw_confidence).strip().lower()
            if val_str == "high":
                score = 0.94
            elif val_str == "medium":
                score = 0.82
            elif val_str == "low":
                score = 0.65
            else:
                score = 0.88

        adjusted_score = round(min(1.0, max(0.0, score * weight)), 4)
        status = "auto_approved" if adjusted_score >= self.confidence_threshold else "flagged_for_review"
        return adjusted_score, status

    def evaluate_threshold_sensitivity(self, scores: List[float], threshold: float) -> float:
        if not scores:
            return 0.0
        flagged = sum(1 for s in scores if s < threshold)
        return round((flagged / len(scores)) * 100.0, 2)
