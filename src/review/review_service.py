from sqlite3 import Connection
from typing import Dict, Any, Optional
from src.storage.repositories import ReviewRepository

class HITLReviewService:
    def __init__(self, conn: Connection):
        self.conn = conn
        self.review_repo = ReviewRepository(conn)

    def approve_relation(self, relation_id: int, reviewer_id: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT confidence_score, review_status FROM knowledge_relations WHERE relation_id = ?;", (relation_id,))
        row = cursor.fetchone()
        old_val = row["review_status"] if row else "unknown"

        cursor.execute("UPDATE knowledge_relations SET review_status = 'approved' WHERE relation_id = ?;", (relation_id,))
        self.review_repo.log_review_action(
            entity_type="relation",
            entity_id=relation_id,
            action_type="approve",
            old_value=old_val,
            new_value="approved",
            reviewer_id=reviewer_id,
            reason="Automated verification criteria confirmed by expert"
        )
        self.conn.commit()

    def modify_relation_predicate(self, relation_id: int, new_predicate: str, reviewer_id: str, reason: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT predicate FROM knowledge_relations WHERE relation_id = ?;", (relation_id,))
        row = cursor.fetchone()
        old_pred = row["predicate"] if row else "unknown"

        cursor.execute(
            "UPDATE knowledge_relations SET predicate = ?, review_status = 'modified' WHERE relation_id = ?;",
            (new_predicate, relation_id)
        )
        self.review_repo.log_review_action(
            entity_type="relation",
            entity_id=relation_id,
            action_type="modify_predicate",
            old_value=old_pred,
            new_value=new_predicate,
            reviewer_id=reviewer_id,
            reason=reason
        )
        self.conn.commit()

    def reverse_relation_direction(self, relation_id: int, reviewer_id: str, reason: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT source_id, source_type, object_id, object_type FROM knowledge_relations WHERE relation_id = ?;",
            (relation_id,)
        )
        row = cursor.fetchone()
        if not row:
            return

        s_id, s_type, o_id, o_type = row["source_id"], row["source_type"], row["object_id"], row["object_type"]
        cursor.execute(
            """
            UPDATE knowledge_relations 
            SET source_id = ?, source_type = ?, object_id = ?, object_type = ?, review_status = 'modified' 
            WHERE relation_id = ?;
            """,
            (o_id, o_type, s_id, s_type, relation_id)
        )
        self.review_repo.log_review_action(
            entity_type="relation",
            entity_id=relation_id,
            action_type="reverse_direction",
            old_value=f"{s_id}->{o_id}",
            new_value=f"{o_id}->{s_id}",
            reviewer_id=reviewer_id,
            reason=reason
        )
        self.conn.commit()
