from typing import Optional, List
from pydantic import BaseModel, Field

class TopicModel(BaseModel):
    topic_id: int
    parent_id: Optional[int] = None
    topic_code: str
    topic_parent_code: Optional[str] = None
    title: str
    topic_type: Optional[str] = None
    display_order: Optional[int] = None
    topic_level: int
    topic_path: str
    category: Optional[str] = None
    is_leaf: int = 0
    content_text: Optional[str] = None
    explanation: Optional[str] = None
    content_type: Optional[str] = None

class TopicEdgeModel(BaseModel):
    parent_id: int
    child_id: int
    relation_type: str = "subsumes"

class TopicClosureModel(BaseModel):
    ancestor_id: int
    descendant_id: int
    depth: int

class PoincareCoordinate(BaseModel):
    topic_id: int
    title: str
    level: int
    x: float
    y: float
    r: float
    theta: float

class TopologyMetrics(BaseModel):
    total_nodes: int
    total_edges: int
    max_depth: int
    average_branching_factor: float
    intermediate_nodes_count: int
    intermediate_nodes_ratio: float
    is_dag: bool
    leaf_nodes_count: int
    root_nodes_count: int
