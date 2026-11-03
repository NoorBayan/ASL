from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

class StructuredQueryModel(BaseModel):
    query_id: str
    query_type: str
    target_topic_id: Optional[int] = None
    target_atom_id: Optional[int] = None
    relation_types: List[str] = Field(default_factory=list)
    max_hops: int = 1
    direction: str = "forward"
    filters: Dict[str, Any] = Field(default_factory=dict)
    include_provenance: bool = True
    approved_only: bool = True

class QueryResultItem(BaseModel):
    entity_id: Union[int, str]
    entity_type: str
    title_or_text: str
    role_or_predicate: Optional[str] = None
    depth_or_hop: int = 0
    path_trace: List[str] = Field(default_factory=list)
    source_reference: Optional[str] = None
    confidence: float = 1.0

class UnifiedQueryResponse(BaseModel):
    query_id: str
    query_type: str
    execution_engine: List[str]
    status: str
    results: List[QueryResultItem]
    result_count: int
    execution_time_ms: float
    dataset_version: str = "v1.0.0-verified"
    warnings: List[str] = Field(default_factory=list)

class LatencyMetricRow(BaseModel):
    query_type: str
    p50_median: float
    p95: float
    p99: float
    mean: float
    min_val: float
    max_val: float
    total_queries: int

class ScalabilityLevelResult(BaseModel):
    ingestion_level: str
    nodes_count: int
    edges_count: int
    edge_growth_percent: float
    concurrent_threads: int
    median_latency_ms: float
    latency_growth_percent: float
