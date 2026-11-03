from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class RelationTypeModel(BaseModel):
    relation_type_id: str
    relation_name_en: str
    relation_name_ar: str
    category: str
    is_directed: bool = True
    is_symmetric: bool = False
    inverse_relation: Optional[str] = None
    description: Optional[str] = None

class CandidatePairModel(BaseModel):
    pair_id: str
    source_atom_id: int
    target_atom_id: int
    source_role: str
    target_role: str
    taxonomic_distance: int
    shared_topic_id: int
    is_compatible: bool

class KnowledgeRelationModel(BaseModel):
    relation_id: int
    source_id: int
    source_type: str
    predicate: str
    object_id: int
    object_type: str
    context_topic_id: Optional[int] = None
    weight: float = 1.0
    confidence_score: float = 1.0
    confidence_level: str = "high"
    relation_summary: Optional[str] = None
    relation_description: Optional[str] = None
    review_status: str = "approved"

class RelationMetricsModel(BaseModel):
    total_relations: int
    unique_predicates: int
    cross_source_alignments: int
    auto_integrated_count: int
    flagged_for_review_count: int
    review_flag_ratio: float
    confidence_threshold: float
    f1_proposed: float
    f1_regex_baseline: float
    f1_gpt4_baseline: float
