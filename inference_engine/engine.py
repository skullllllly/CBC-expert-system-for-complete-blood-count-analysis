import sys
from pathlib import Path

# ضمان التعرف على مجلد knowledge_base من أي مسار تشغيل
CURRENT_DIR = Path(__file__).resolve().parent
for candidate in [CURRENT_DIR / "knowledge_base", CURRENT_DIR.parent / "knowledge_base"]:
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from medical_knowledge import REFERENCE_RANGES, get_all_statuses  # type: ignore
from rules import RULES, calculate_absolute_counts, rule_28  # type: ignore

# خريطة توحيد الأسماء بين مخرجات parser.py ومدخلات rules.py
KEY_MAPPING = {
    "age": "age",
    "sex": "sex",
    "hb": "hb",
    "hemoglobin": "hb",
    "pcv": "pcv",
    "hct": "pcv",
    "wbc": "wbc",
    "t.wbc": "wbc",
    "total wbc": "wbc",
    "neutrophils": "neutrophils_pct",
    "neutrophils%": "neutrophils_pct",
    "neutrophils_pct": "neutrophils_pct",
    "lymphocytes": "lymphocytes_pct",
    "lymphocytes%": "lymphocytes_pct",
    "lymphocytes_pct": "lymphocytes_pct",
    "monocytes": "monocytes_pct",
    "monocytes%": "monocytes_pct",
    "monocytes_pct": "monocytes_pct",
    "eosinophils": "eosinophils_pct",
    "eosinophils%": "eosinophils_pct",
    "eosinophils_pct": "eosinophils_pct",
    "neutrophils#": "neutrophils_abs",
    "neutrophils_abs": "neutrophils_abs",
    "lymphocytes#": "lymphocytes_abs",
    "lymphocytes_abs": "lymphocytes_abs",
    "monocytes#": "monocytes_abs",
    "monocytes_abs": "monocytes_abs",
    "eosinophils#": "eosinophils_abs",
    "eosinophils_abs": "eosinophils_abs",
    "platelets": "platelets",
    "plt": "platelets",
    "rbc": "rbc",
    "mcv": "mcv",
    "mch": "mch",
    "mchc": "mchc",
    "rdw": "rdw",
    "rdw-cv": "rdw",
    "units_valid": "units_valid",
}


def normalize_facts(raw_facts: dict) -> dict:
    """توحيد أسماء الحقائق المستخرجة من PDF لتتطابق مع قاعدة القواعد الطبية."""
    normalized = {key: None for key in REFERENCE_RANGES.keys()}
    normalized["age"] = None
    normalized["sex"] = None
    normalized["units_valid"] = True

    for raw_key, value in raw_facts.items():
        clean_key = str(raw_key).strip().lower()
        target_key = KEY_MAPPING.get(clean_key)
        if target_key:
            normalized[target_key] = value

    # توحيد صيغة الجنس
    if isinstance(normalized["sex"], str):
        sex_val = normalized["sex"].strip().lower()
        if sex_val in ["male", "m", "ذكر"]:
            normalized["sex"] = "male"
        elif sex_val in ["female", "f", "أنثى", "انثى"]:
            normalized["sex"] = "female"

    # حساب القيم المطلقة للخلايا البيضاء تلقائياً إذا كانت النسب المئوية موجودة
    calculated_abs = calculate_absolute_counts(normalized)
    for abs_key, calc_val in calculated_abs.items():
        if normalized.get(abs_key) is None:
            normalized[abs_key] = round(calc_val, 2)

    return normalized


def run_inference(raw_facts: dict) -> dict:
    """
    محرك الاستدلال الأمامي (Forward Chaining):
    - يفحص جميع القواعد في قاعدة المعرفة.
    - يتتبع القواعد المفحوصة (Checked Rules) والقواعد المفعّلة (Fired Rules).
    - يعيد التشخيصات وحالة كل مؤشر طبي.
    """
    facts = normalize_facts(raw_facts)
    statuses = get_all_statuses(facts)

    checked_rules = []
    fired_rules = []

    # فحص القاعدة 28 أولاً (نطاق العمر 18 - 65)
    age_check = rule_28(facts)
    if age_check is not None:
        fired_rules.append(age_check)
        checked_rules.append({
            "rule_id": "R28",
            "function": "rule_28",
            "status": "مفعّلة (Fired)",
            "conclusion": age_check["conclusion"]
        })
        for r_fn in RULES:
            if r_fn.__name__ != "rule_28":
                r_num = r_fn.__name__.replace("rule_", "R")
                checked_rules.append({
                    "rule_id": r_num,
                    "function": r_fn.__name__,
                    "status": "تم التخطي (خارج النطاق العمري)",
                    "conclusion": "—"
                })
        return {
            "facts": facts,
            "statuses": statuses,
            "fired_rules": fired_rules,
            "checked_rules": checked_rules,
            "total_rules": len(RULES),
            "fired_count": len(fired_rules),
            "checked_count": 1,
        }

    # المرور على جميع القواعد بالترتيب
    for rule_fn in RULES:
        r_id = rule_fn.__name__.replace("rule_", "R")
        result = rule_fn(facts)

        if result is None:
            checked_rules.append({
                "rule_id": r_id,
                "function": rule_fn.__name__,
                "status": "تم الفحص (غير منطبقة)",
                "conclusion": "—"
            })
        elif isinstance(result, list):
            fired_rules.extend(result)
            checked_rules.append({
                "rule_id": r_id,
                "function": rule_fn.__name__,
                "status": "مفعّلة (Fired)",
                "conclusion": f"تم تنفيذ {len(result)} عمليات حسابية"
            })
        else:
            fired_rules.append(result)
            checked_rules.append({
                "rule_id": r_id,
                "function": rule_fn.__name__,
                "status": "مفعّلة (Fired)",
                "conclusion": result["conclusion"]
            })

    return {
        "facts": facts,
        "statuses": statuses,
        "fired_rules": fired_rules,
        "checked_rules": checked_rules,
        "total_rules": len(RULES),
        "fired_count": len({r["rule_id"] for r in fired_rules}),
        "checked_count": len(RULES),
    }