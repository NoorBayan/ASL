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
        sanitized_records = [{col: t.get(col, None) for col in allowed_columns} for t in topics]
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
        SELECT t.topic_id, t.title, t.topic_level, t.topic_code, c.depth
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
            SELECT t.topic_id, t.title, t.topic_level, t.topic_code, c.depth
            FROM topic_closure c
            JOIN topics t ON c.descendant_id = t.topic_id
            WHERE c.ancestor_id = ? AND c.depth <= ?
            ORDER BY c.depth ASC, t.display_order ASC;
            """
            params = (topic_id, max_depth)
        else:
            sql = """
            SELECT t.topic_id, t.title, t.topic_level, t.topic_code, c.depth
            FROM topic_closure c
            JOIN topics t ON c.descendant_id = t.topic_id
            WHERE c.ancestor_id = ?
            ORDER BY c.depth ASC, t.display_order ASC;
            """
            params = (topic_id,)
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]


class AtomRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    def insert_atoms(self, atoms: List[Dict[str, Any]]) -> None:
        sql = """
        INSERT OR REPLACE INTO knowledge_atoms (
            atom_id, topic_id, parent_element_id, element_type_en,
            element_type_ar, macro_category, element_title, element_text,
            element_order, depth_level, source_type, confidence_level,
            start_char, end_char, page_number
        ) VALUES (
            :atom_id, :topic_id, :parent_element_id, :element_type_en,
            :element_type_ar, :macro_category, :element_title, :element_text,
            :element_order, :depth_level, :source_type, :confidence_level,
            :start_char, :end_char, :page_number
        );
        """
        cursor = self.conn.cursor()
        cursor.executemany(sql, atoms)

    def insert_provenance_records(self, records: List[Dict[str, Any]]) -> None:
        sql = """
        INSERT OR REPLACE INTO atom_provenance (
            atom_id, document_id, source_start_char, source_end_char, is_verified
        ) VALUES (
            :atom_id, :document_id, :source_start_char, :source_end_char, :is_verified
        );
        """
        cursor = self.conn.cursor()
        cursor.executemany(sql, records)

    def get_all_atoms(self) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM knowledge_atoms ORDER BY atom_id ASC;")
        return [dict(row) for row in cursor.fetchall()]

    def get_atoms_by_topic(self, topic_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM knowledge_atoms WHERE topic_id = ? ORDER BY element_order ASC;", (topic_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_atoms_by_macro_category(self, macro_category: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM knowledge_atoms WHERE macro_category = ? ORDER BY atom_id ASC;", (macro_category,))
        return [dict(row) for row in cursor.fetchall()]

    def get_atom_by_id(self, atom_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM knowledge_atoms WHERE atom_id = ?;", (atom_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


class RelationRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    def insert_relation_types(self, relation_types: List[Dict[str, Any]]) -> None:
        sql = """
        INSERT OR REPLACE INTO relation_types (
            relation_type_id, relation_name_en, relation_name_ar,
            category, is_directed, is_symmetric, inverse_relation, description
        ) VALUES (
            :relation_type_id, :relation_name_en, :relation_name_ar,
            :category, :is_directed, :is_symmetric, :inverse_relation, :description
        );
        """
        cursor = self.conn.cursor()
        cursor.executemany(sql, relation_types)

    def insert_relations(self, relations: List[Dict[str, Any]]) -> None:
        sql = """
        INSERT OR REPLACE INTO knowledge_relations (
            relation_id, source_id, source_type, predicate, object_id,
            object_type, context_topic_id, weight, confidence_score,
            confidence_level, relation_summary, relation_description, review_status
        ) VALUES (
            :relation_id, :source_id, :source_type, :predicate, :object_id,
            :object_type, :context_topic_id, :weight, :confidence_score,
            :confidence_level, :relation_summary, :relation_description, :review_status
        );
        """
        cursor = self.conn.cursor()
        cursor.executemany(sql, relations)

    def get_all_relations(self) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM knowledge_relations ORDER BY relation_id ASC;")
        return [dict(row) for row in cursor.fetchall()]

    def get_relations_by_source(self, source_id: int, source_type: str = "atom") -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM knowledge_relations WHERE source_id = ? AND source_type = ?;",
            (source_id, source_type)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_relations_by_predicate(self, predicate: str) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM knowledge_relations WHERE predicate = ?;", (predicate,))
        return [dict(row) for row in cursor.fetchall()]


class ReviewRepository:
    def __init__(self, conn: Connection):
        self.conn = conn

    def log_review_action(
        self,
        entity_type: str,
        entity_id: int,
        action_type: str,
        old_value: Optional[str],
        new_value: Optional[str],
        reviewer_id: str,
        reason: Optional[str]
    ) -> None:
        sql = """
        INSERT INTO review_history (
            entity_type, entity_id, action_type, old_value, new_value, reviewer_id, reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, (entity_type, entity_id, action_type, old_value, new_value, reviewer_id, reason))

    def get_review_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM review_history ORDER BY history_id DESC LIMIT ?;", (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def record_dataset_version(
        self,
        version_tag: str,
        topics_count: int,
        atoms_count: int,
        relations_count: int,
        total_nodes: int,
        total_edges: int
    ) -> None:
        sql = """
        INSERT INTO dataset_versions (
            version_tag, topics_count, atoms_count, relations_count, total_nodes, total_edges
        ) VALUES (?, ?, ?, ?, ?, ?);
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, (version_tag, topics_count, atoms_count, relations_count, total_nodes, total_edges))
