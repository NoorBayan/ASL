import math
from collections import defaultdict
from typing import List, Dict, Any, Optional
from src.schemas.hierarchy import PoincareCoordinate

class PoincareProjectionCalculator:
    def __init__(self, max_level: int = 5):
        self.max_level = max_level

    def compute_coordinates(self, topics: List[Dict[str, Any]]) -> List[PoincareCoordinate]:
        children_map: Dict[Optional[int], List[Dict[str, Any]]] = defaultdict(list)
        topic_lookup: Dict[int, Dict[str, Any]] = {}

        for t in topics:
            tid = int(t["topic_id"])
            topic_lookup[tid] = t
            pid = t.get("parent_id")
            parent_id = int(pid) if pid is not None and str(pid).strip() != "" and str(pid).lower() != "none" else None
            children_map[parent_id].append(t)

        results: List[PoincareCoordinate] = []

        def layout_sector(parent_id: Optional[int], theta_min: float, theta_max: float, depth: int) -> None:
            children = children_map.get(parent_id, [])
            if not children:
                return

            num_children = len(children)
            sector_width = (theta_max - theta_min) / num_children

            for idx, child in enumerate(children):
                cid = int(child["topic_id"])
                child_theta_min = theta_min + idx * sector_width
                child_theta_max = child_theta_min + sector_width
                child_theta = (child_theta_min + child_theta_max) / 2.0

                lvl = int(child.get("topic_level", depth))
                if lvl <= 1:
                    radius = 0.0
                else:
                    norm_depth = (lvl - 1) / max(1.0, float(self.max_level))
                    radius = math.tanh(norm_depth * 1.5)

                px = radius * math.cos(child_theta)
                py = radius * math.sin(child_theta)

                results.append(
                    PoincareCoordinate(
                        topic_id=cid,
                        title=str(child.get("title", "")),
                        level=lvl,
                        x=round(px, 6),
                        y=round(py, 6),
                        r=round(radius, 6),
                        theta=round(child_theta, 6)
                    )
                )

                layout_sector(cid, child_theta_min, child_theta_max, lvl + 1)

        layout_sector(None, 0.0, 2.0 * math.pi, 1)

        processed_ids = {c.topic_id for c in results}
        remaining = [t for t in topics if int(t["topic_id"]) not in processed_ids]
        if remaining:
            step = (2.0 * math.pi) / len(remaining)
            for idx, rem in enumerate(remaining):
                lvl = int(rem.get("topic_level", 2))
                radius = math.tanh(((lvl - 1) / max(1.0, float(self.max_level))) * 1.5)
                theta = idx * step
                results.append(
                    PoincareCoordinate(
                        topic_id=int(rem["topic_id"]),
                        title=str(rem.get("title", "")),
                        level=lvl,
                        x=round(radius * math.cos(theta), 6),
                        y=round(radius * math.sin(theta), 6),
                        r=round(radius, 6),
                        theta=round(theta, 6)
                    )
                )

        return results
