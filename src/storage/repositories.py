from typing import List, Dict, Any, Optional
from sqlite3 import Connection

class TopicRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    def insert_topics(self, topics: List[Dict[str, Any]]) -> None:
        allowed_columns = [
            "topic_id", "parent_id", "topic_code", "topic_parent_code", "title",
            "topic_type", "display_order", "topic_level", "topic_path", "category",
            "is_leaf", "content_text", "explanation", "content_type"
        ]
        
        sanitized_records = []
        for t in topics:
            record = {col: t.get(col, None) for col in allowed_columns}
            sanitized_records.append(record)

        sql = """
        INSERT OR REPLACE INTO topics (
            topic_id, parent_id, topic_code, topic_parent_code, title,
            topic_type, display_order, topic_level, topic_path, category,
            is_leaf, content_text, explanation, content_type
        ) VALUES (
            :topic_id, :parent_id, :topic_code, :topic_parent_code, :title,
            :topic_type, :display_order, :topic_level, :topic_path, :category,
            :is_leaf, :content_text, :explanation, :content_type
        );
        """
        cursor = self.conn.cursor()
        cursor.executemany(sql, sanitized_records)

    def insert_edges(self, edges: List[Dict[str, Any]]) -> None:
        sql = """
        INSERT OR IGNORE INTO topic_edges (parent_id, child_id, relation_type)
        VALUES (:parent_id, :child_id, :relation_type);
        """
        cursor = self.conn.cursor()
        cursor.executemany(sql, edges)

    def get_all_topics(self) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM topics ORDER BY topic_level, display_order, topic_id;")
        return [dict(row) for row in cursor.fetchall()]

    def get_all_edges(self) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM topic_edges;")
        return [dict(row) for row in cursor.fetchall()]

    def get_ancestors(self, topic_id: int) -> List[Dict[str, Any]]:
        sql = """
        SELECT 
            t.topic_id,
            t.title,
            t.topic_level,
            t.topic_code,
            c.depth
        FROM topic_closure c
        JOIN topics t ON c.ancestor_id = t.topic_id
        WHERE c.descendant_id = ?
        ORDER BY c.depth DESC;
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, (topic_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_descendants(self, topic_id: int, max_depth: Optional[int] = None) -> List[Dict[str, Any]]:
        if max_depth is not None:
            sql = """
            SELECT 
                t.topic_id,
                t.title,
                t.topic_level,
                t.topic_code,
                c.depth
            FROM topic_closure c
            JOIN topics t ON c.descendant_id = t.topic_id
            WHERE c.ancestor_id = ? AND c.depth <= ?
            ORDER BY c.depth ASC, t.display_order ASC;
            """
            params = (topic_id, max_depth)
        else:
            sql = """
            SELECT 
                t.topic_id,
                t.title,
                t.topic_level,
                t.topic_code,
                c.depth
            FROM topic_closure c
            JOIN topics t ON c.descendant_id = t.topic_id
            WHERE c.ancestor_id = ?
            ORDER BY c.depth ASC, t.display_order ASC;
            """
            params = (topic_id,)
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
