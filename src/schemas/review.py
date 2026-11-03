from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class ReviewDecisionModel(BaseModel):
    review_id: Optional[int] = None
    entity_type: str
    entity_id: int
    action_type: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    reviewer_id: str
    reason: Optional[str] = None
    timestamp: Optional[str] = None

class AuditHistoryModel(BaseModel):
    history_id: int
    entity_type: str
    entity_id: int
    action_type: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    reviewer_id: str
    timestamp: str
    reason: Optional[str] = None

class DatasetVersionModel(BaseModel):
    version_id: int
    version_tag: str
    topics_count: int
    atoms_count: int
    relations_count: int
    total_nodes: int
    total_edges: int
    created_at: str

class GraphParityReportModel(BaseModel):
    sqlite_topics_count: int
    sqlite_atoms_count: int
    sqlite_total_nodes: int
    sqlite_relations_count: int
    networkx_total_nodes: int
    networkx_total_edges: int
    is_node_parity_perfect: bool
    is_edge_parity_perfect: bool
    orphan_atoms_count: int
    dag_cycles_count: int
    top_hubs: List[Dict[str, Any]]
