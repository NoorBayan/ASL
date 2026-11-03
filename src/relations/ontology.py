from typing import Dict, List, Optional
from src.schemas.relation import RelationTypeModel

PREDEFINED_RELATIONS: List[Dict[str, Any]] = [
    {
        "id": "conditions",
        "en": "Conditions",
        "ar": "قيد واشتراط",
        "cat": "regulatory",
        "directed": True,
        "inverse": "conditioned_by",
        "desc": "An operative condition restricting the legal scope of a ruling"
    },
    {
        "id": "justifies",
        "en": "Justifies",
        "ar": "تأييد واستدلال",
        "cat": "evidentiary",
        "directed": True,
        "inverse": "justified_by",
        "desc": "Evidentiary proof providing legal ground for a ruling or premise"
    },
    {
        "id": "overrides",
        "en": "Overrides / Limits",
        "ar": "استثناء وتخصيص",
        "cat": "qualifying",
        "directed": True,
        "inverse": "overridden_by",
        "desc": "An exception qualifying or limiting a general legal proposition"
    },
    {
        "id": "derives_from",
        "en": "Derives From",
        "ar": "اشتقاق وتفريع",
        "cat": "inferential",
        "directed": True,
        "inverse": "generates",
        "desc": "A specific ruling derived via deduction or analogy from a general principle"
    },
    {
        "id": "aligned_with",
        "en": "Aligned With",
        "ar": "مواءمة نظامية فقهية",
        "cat": "interoperability",
        "directed": False,
        "inverse": "aligned_with",
        "desc": "Cross-domain correspondence linking classical jurisprudence to modern statutory provisions"
    },
    {
        "id": "supported_by",
        "en": "Supported By",
        "ar": "مستند إلى",
        "cat": "evidentiary",
        "directed": True,
        "inverse": "supports",
        "desc": "Juristic dependency connecting an analysis to textual or rational evidence"
    },
    {
        "id": "has_definition",
        "en": "Has Definition",
        "ar": "يتضمن تعريفاً",
        "cat": "conceptual",
        "directed": True,
        "inverse": "definition_of",
        "desc": "Associates a legal topic with its formal technical definition"
    },
    {
        "id": "part_of",
        "en": "Part Of",
        "ar": "جزء من",
        "cat": "mereological",
        "directed": True,
        "inverse": "comprises",
        "desc": "Subsumption relation linking components to their overarching legal topic"
    }
]

class RelationOntologyRegistry:
    def __init__(self):
        self.registry: Dict[str, RelationTypeModel] = {}
        for r in PREDEFINED_RELATIONS:
            self.registry[r["id"]] = RelationTypeModel(
                relation_type_id=r["id"],
                relation_name_en=r["en"],
                relation_name_ar=r["ar"],
                category=r["cat"],
                is_directed=r["directed"],
                is_symmetric=(r["id"] == "aligned_with"),
                inverse_relation=r["inverse"],
                description=r["desc"]
            )

    def get_relation(self, predicate: str) -> RelationTypeModel:
        cleaned = str(predicate).strip().lower()
        if cleaned in self.registry:
            return self.registry[cleaned]
        return RelationTypeModel(
            relation_type_id=cleaned,
            relation_name_en=cleaned.replace("_", " ").title(),
            relation_name_ar=cleaned,
            category="general",
            is_directed=True
        )

    def get_all_predicates(self) -> List[RelationTypeModel]:
        return list(self.registry.values())
