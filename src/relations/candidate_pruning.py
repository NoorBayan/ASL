from typing import Dict, List, Set, Tuple
from src.schemas.relation import CandidatePairModel

COMPATIBILITY_RULES: Dict[Tuple[str, str], List[str]] = {
    ("operative_conditions", "normative_rulings"): ["conditions", "restricts"],
    ("evidentiary_elements", "normative_rulings"): ["justifies", "supported_by"],
    ("operative_conditions", "operative_conditions"): ["prerequisite_of", "conditions"],
    ("juristic_analyses", "normative_rulings"): ["derives_from", "rationalizes"],
    ("statutory_provisions", "normative_rulings"): ["aligned_with", "formalizes"],
    ("normative_rulings", "operative_conditions"): ["conditioned_by", "overridden_by"],
    ("evidentiary_elements", "juristic_analyses"): ["supported_by", "justifies"]
}

class CandidatePairPruner:
    def __init__(self, closure_lookup: Dict[Tuple[int, int], int]):
        self.closure_lookup = closure_lookup

    def evaluate_pair_compatibility(
        self,
        source_id: int,
        source_topic: int,
        source_macro: str,
        target_id: int,
        target_topic: int,
        target_macro: str
    ) -> Tuple[bool, int, List[str]]:
        if source_id == target_id:
            return False, 0, []

        distance = 999
        if (source_topic, target_topic) in self.closure_lookup:
            distance = self.closure_lookup[(source_topic, target_topic)]
        elif (target_topic, source_topic) in self.closure_lookup:
            distance = self.closure_lookup[(target_topic, source_topic)]
        elif source_topic == target_topic:
            distance = 0

        allowed_predicates = COMPATIBILITY_RULES.get((source_macro, target_macro), [])
        
        is_taxonomically_close = distance <= 2
        is_epistemically_valid = len(allowed_predicates) > 0

        is_compatible = is_taxonomically_close and is_epistemically_valid
        return is_compatible, distance, allowed_predicates
