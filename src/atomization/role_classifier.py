from typing import Dict, List, Tuple
from src.schemas.atom import EpistemicRoleModel

MACRO_CATEGORIES: Dict[str, Tuple[str, str]] = {
    "normative_rulings": ("Normative Rulings", "الأحكام التكليفية والوضعية"),
    "operative_conditions": ("Operative Conditions", "الشروط والقيود والضوابط"),
    "evidentiary_elements": ("Evidentiary Elements", "الأدلة النصية والمستندات"),
    "juristic_analyses": ("Juristic Analyses", "التحليلات والمفاهيم الفقهية"),
    "statutory_provisions": ("Statutory Provisions", "المواد والأحكام النظامية")
}

ROLE_REGISTRY_DATA: List[Dict[str, str]] = [
    {"role": "ruling", "ar": "حكم فقهي", "macro": "normative_rulings"},
    {"role": "obligation", "ar": "إيجاب وإلزام", "macro": "normative_rulings"},
    {"role": "prohibition", "ar": "تحريم ومنع", "macro": "normative_rulings"},
    {"role": "recommendation", "ar": "ندب واستحباب", "macro": "normative_rulings"},
    {"role": "permissibility", "ar": "إباحة وجواز", "macro": "normative_rulings"},
    {"role": "validity_ruling", "ar": "صحة العقد", "macro": "normative_rulings"},
    {"role": "nullity_ruling", "ar": "بطلان وفساد", "macro": "normative_rulings"},
    {"role": "condition", "ar": "شرط صحة", "macro": "operative_conditions"},
    {"role": "prerequisite", "ar": "متطلب أساسي", "macro": "operative_conditions"},
    {"role": "restriction", "ar": "قيد تشغيلي", "macro": "operative_conditions"},
    {"role": "exception", "ar": "استثناء شرعي", "macro": "operative_conditions"},
    {"role": "suspensive_condition", "ar": "شرط واقف", "macro": "operative_conditions"},
    {"role": "endower_stipulation", "ar": "شرط الواقف", "macro": "operative_conditions"},
    {"role": "qualification", "ar": "قيد وصفي", "macro": "operative_conditions"},
    {"role": "evidence", "ar": "دليل شرعي", "macro": "evidentiary_elements"},
    {"role": "quranic_proof", "ar": "استدلال قرآني", "macro": "evidentiary_elements"},
    {"role": "hadith_proof", "ar": "استدلال حديثي", "macro": "evidentiary_elements"},
    {"role": "consensus", "ar": "إجماع الصحابة", "macro": "evidentiary_elements"},
    {"role": "juristic_analogy", "ar": "قياس أصولي", "macro": "evidentiary_elements"},
    {"role": "companion_tradition", "ar": "أثر صحابي", "macro": "evidentiary_elements"},
    {"role": "rational_proof", "ar": "استدلال عقلي", "macro": "evidentiary_elements"},
    {"role": "overview", "ar": "نظرة عامة", "macro": "juristic_analyses"},
    {"role": "legal_analysis", "ar": "تحليل فقهي", "macro": "juristic_analyses"},
    {"role": "definition", "ar": "تعريف اصطلاحي", "macro": "juristic_analyses"},
    {"role": "terminology", "ar": "دلالة لغوية", "macro": "juristic_analyses"},
    {"role": "rationale", "ar": "تعليل وحكمة", "macro": "juristic_analyses"},
    {"role": "purpose", "ar": "مقصد شرعي", "macro": "juristic_analyses"},
    {"role": "scholarly_opinion", "ar": "قول فقهي", "macro": "juristic_analyses"},
    {"role": "juristic_difference", "ar": "خلاف مذهبي", "macro": "juristic_analyses"},
    {"role": "classification", "ar": "تقسيم وتنويع", "macro": "juristic_analyses"},
    {"role": "pillar_analysis", "ar": "بيان الأركان", "macro": "juristic_analyses"},
    {"role": "statutory_provision", "ar": "مادة نظامية", "macro": "statutory_provisions"},
    {"role": "statutory_definition", "ar": "تعريف نظامي", "macro": "statutory_provisions"},
    {"role": "regulatory_obligation", "ar": "إلزام نظامي", "macro": "statutory_provisions"},
    {"role": "regulatory_exception", "ar": "استثناء نظامي", "macro": "statutory_provisions"},
    {"role": "governance_rule", "ar": "قاعدة حوكمة", "macro": "statutory_provisions"},
    {"role": "supervisory_power", "ar": "صلاحية إشرافية", "macro": "statutory_provisions"}
]

class EpistemicRoleRegistry:
    def __init__(self):
        self.roles: Dict[str, EpistemicRoleModel] = {}
        self._initialize_registry()

    def _initialize_registry(self) -> None:
        for item in ROLE_REGISTRY_DATA:
            role_key = item["role"]
            macro_key = item["macro"]
            macro_en, macro_ar = MACRO_CATEGORIES.get(macro_key, ("Juristic Analyses", "تحليلات فقهية"))
            self.roles[role_key] = EpistemicRoleModel(
                role_id=role_key,
                role_name_en=role_key.replace("_", " ").title(),
                role_name_ar=item["ar"],
                macro_category_en=macro_en,
                macro_category_ar=macro_ar
            )

    def resolve_macro_category(self, role_type: str) -> Tuple[str, str]:
        cleaned_role = str(role_type).strip().lower()
        if cleaned_role in self.roles:
            model = self.roles[cleaned_role]
            return model.macro_category_en, model.macro_category_ar
        
        for k, v in self.roles.items():
            if k in cleaned_role or cleaned_role in k:
                return v.macro_category_en, v.macro_category_ar

        return "Juristic Analyses", "التحليلات والمفاهيم الفقهية"

    def get_role_info(self, role_type: str) -> EpistemicRoleModel:
        cleaned_role = str(role_type).strip().lower()
        if cleaned_role in self.roles:
            return self.roles[cleaned_role]
        macro_en, macro_ar = self.resolve_macro_category(cleaned_role)
        return EpistemicRoleModel(
            role_id=cleaned_role,
            role_name_en=cleaned_role.replace("_", " ").title(),
            role_name_ar=cleaned_role,
            macro_category_en=macro_en,
            macro_category_ar=macro_ar
        )

    def get_all_roles(self) -> List[EpistemicRoleModel]:
        return list(self.roles.values())
