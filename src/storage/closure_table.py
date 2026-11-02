from typing import List, Tuple, Set, Dict
from collections import defaultdict, deque
from sqlite3 import Connection

class ClosureTableBuilder:
    def __init__(self, conn: Connection):
        self.conn = conn

    def build_from_edges(self, edges: List[Tuple[int, int]], all_nodes: List[int]) -> None:
        adj: Dict[int, List[int]] = defaultdict(list)
        for parent, child in edges:
            adj[parent].append(child)

        closure_entries: Set[Tuple[int, int, int]] = set()

        for node in all_nodes:
            closure_entries.add((node, node, 0))

        for root in all_nodes:
            queue: deque = deque([(root, 0)])
            visited: Set[Tuple[int, int]] = set()
            while queue:
                current_node, current_depth = queue.popleft()
                for neighbor in adj.get(current_node, []):
                    next_depth = current_depth + 1
                    if (neighbor, next_depth) not in visited:
                        visited.add((neighbor, next_depth))
                        closure_entries.add((root, neighbor, next_depth))
                        queue.append((neighbor, next_depth))

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM topic_closure;")
        cursor.executemany(
            "INSERT OR IGNORE INTO topic_closure (ancestor_id, descendant_id, depth) VALUES (?, ?, ?);",
            list(closure_entries)
        )

    def populate_materialized_paths(self, topics_data: List[Tuple[int, str, int]]) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM topic_materialized_paths;")
        cursor.executemany(
            "INSERT INTO topic_materialized_paths (topic_id, path_string, level) VALUES (?, ?, ?);",
            topics_data
        )
