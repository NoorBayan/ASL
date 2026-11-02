import math
from typing import List, Dict, Any
from src.schemas.hierarchy import PoincareCoordinate

class PoincareProjectionCalculator:
    def __init__(self, max_level: int = 5):
        self.max_level = max_level

    def compute_coordinates(self, topics: List[Dict[str, Any]]) -> List[PoincareCoordinate]:
        levels_map: Dict[int, List[Dict[str, Any]]] = {}
        for t in topics:
            lvl = int(t["topic_level"])
            levels_map.setdefault(lvl, []).append(t)

        results: List[PoincareCoordinate] = []

        for lvl, node_list in levels_map.items():
            count = len(node_list)
            if lvl == 1:
                r = 0.0
            else:
                r = math.tanh((lvl - 1) / (self.max_level * 0.75))
            
            for index, node in enumerate(node_list):
                theta = (2.0 * math.pi * index) / count if count > 0 else 0.0
                x = r * math.cos(theta)
                y = r * math.sin(theta)
                
                results.append(
                    PoincareCoordinate(
                        topic_id=int(node["topic_id"]),
                        title=str(node["title"]),
                        level=lvl,
                        x=round(x, 6),
                        y=round(y, 6),
                        r=round(r, 6),
                        theta=round(theta, 6)
                    )
                )

        return results
