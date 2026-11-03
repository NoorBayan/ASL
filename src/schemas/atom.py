from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class EpistemicRoleModel(BaseModel):
    role_id: str
    role_name_en: str
    role_name_ar: str
    macro_category_en: str
    macro_category_ar: str
    description: Optional[str] = None

class ProvenanceAnchorModel(BaseModel):
    atom_id: int
    document_id: str
    topic_id: int
    source_start_char: int
    source_end_char: int
    source_text: str
    source_reference: Optional[str] = None
    page_number: Optional[int] = None
    section_id: Optional[str] = None
    is_exact_match: bool = True

class KnowledgeAtomModel(BaseModel):
    atom_id: int
    topic_id: int
    parent_element_id: Optional[int] = None
    element_type_en: str
    element_type_ar: str
    element_title: str
    element_text: str
    element_order: int
    depth_level: int
    source_type: str
    confidence_level: str
    macro_category: str
    start_char: int
    end_char: int
    page_number: Optional[int] = None

class DisambiguationSpan(BaseModel):
    span_id: str
    start_char: int
    end_char: int
    score: float
    atom_id: int

class AtomSegmentationMetrics(BaseModel):
    total_atoms: int
    unique_topics: int
    unique_epistemic_roles: int
    macro_distribution: Dict[str, int]
    provenance_match_rate: float
    strict_f1: float
    relaxed_iou_f1: float
    regex_baseline_f1: float
