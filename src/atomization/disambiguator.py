from typing import List
from src.schemas.atom import DisambiguationSpan

class BoundaryDisambiguator:
    def __init__(self):
        pass

    def resolve_non_overlapping_intervals(self, spans: List[DisambiguationSpan]) -> List[DisambiguationSpan]:
        if not spans:
            return []

        sorted_spans = sorted(spans, key=lambda s: (s.end_char, -s.score))
        selected_spans: List[DisambiguationSpan] = []
        last_end = -1

        for span in sorted_spans:
            if span.start_char >= last_end:
                selected_spans.append(span)
                last_end = span.end_char

        return selected_spans

    def calculate_iou(self, start_a: int, end_a: int, start_b: int, end_b: int) -> float:
        intersection_start = max(start_a, start_b)
        intersection_end = min(end_a, end_b)
        
        if intersection_end <= intersection_start:
            return 0.0

        intersection_len = intersection_end - intersection_start
        union_len = (end_a - start_a) + (end_b - start_b) - intersection_len

        if union_len <= 0:
            return 0.0

        return float(intersection_len) / float(union_len)
