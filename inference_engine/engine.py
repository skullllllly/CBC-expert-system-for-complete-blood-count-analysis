from typing import Any, Dict, List, Optional, Tuple


KEY_ALIASES = {
    "sex": "sex",
    "gender": "sex",
    "age": "age",
    "hb": "hb",
    "hgb": "hb",
    "hemoglobin": "hb",
    "pcv": "pcv",
    "hct": "pcv",
    "hematocrit": "pcv",
    "wbc": "wbc",
    "t.wbc": "wbc",
    "t_wbc": "wbc",
    "twbc": "wbc",
    "tlc": "wbc",
    "neutrophils_pct": "neutrophils_pct",
    "neutrophil_pct": "neutrophils_pct",
    "neutrophil%": "neutrophils_pct",
    "neut%": "neutrophils_pct",
    "lymphocytes_pct": "lymphocytes_pct",
    "lymphocyte_pct": "lymphocytes_pct",
    "lymphocyte%": "lymphocytes_pct",
    "lymph%": "lymphocytes_pct",
    "monocytes_pct": "monocytes_pct",
    "monocyte_pct": "monocytes_pct",
    "monocyte%": "monocytes_pct",
    "mono%": "monocytes_pct",
    "eosinophils_pct": "eosinophils_pct",
    "eosinophil_pct": "eosinophils_pct",
    "eosinophil%": "eosinophils_pct",
    "eos%": "eosinophils_pct",
    "neutrophils_abs": "neutrophils_abs",
    "neutrophil_abs": "neutrophils_abs",
    "neutrophil#": "neutrophils_abs",
    "neut#": "neutrophils_abs",
    "lymphocytes_abs": "lymphocytes_abs",
    "lymphocyte_abs": "lymphocytes_abs",
    "lymphocyte#": "lymphocytes_abs",
    "lymph#": "lymphocytes_abs",
    "monocytes_abs": "monocytes_abs",
    "monocyte_abs": "monocytes_abs",
    "monocyte#": "monocytes_abs",
    "mono#": "monocytes_abs",
    "eosinophils_abs": "eosinophils_abs",
    "eosinophil_abs": "eosinophils_abs",
    "eosinophil#": "eosinophils_abs",
    "eos#": "eosinophils_abs",
    "rbc": "rbc",
    "mcv": "mcv",
    "mch": "mch",
    "mchc": "mchc",
    "rdw": "rdw",
    "rdw_cv": "rdw",
    "platelets": "platelets",
    "plt": "platelets",
    "platelet": "platelets",
}

TEST_METADATA: List[Tuple[str, str, str]] = [
    ("hb", "Hemoglobin", "g/dL"),
    ("pcv", "Packed Cell Volume", "%"),
    ("wbc", "Total White Blood Cells", "×10⁹/L"),
    ("neutrophils_pct", "Neutrophils Percentage", "%"),
    ("lymphocytes_pct", "Lymphocytes Percentage", "%"),
    ("monocytes_pct", "Monocytes Percentage", "%"),
    ("eosinophils_pct", "Eosinophils Percentage", "%"),
    ("neutrophils_abs", "Absolute Neutrophils", "×10⁹/L"),
    ("lymphocytes_abs", "Absolute Lymphocytes", "×10⁹/L"),
    ("monocytes_abs", "Absolute Monocytes", "×10⁹/L"),
    ("eosinophils_abs", "Absolute Eosinophils", "×10⁹/L"),
    ("rbc", "Red Blood Cells", "×10¹²/L"),
    ("mcv", "Mean Corpuscular Volume", "fL"),
    ("mch", "Mean Corpuscular Hemoglobin", "pg"),
    ("mchc", "Mean Corpuscular Hemoglobin Concentration", "g/dL"),
    ("rdw", "Red Cell Distribution Width", "%"),
    ("platelets", "Platelets", "×10⁹/L"),
]


def _normalize_facts(raw_facts: Dict[str, Any]) -> Dict[str, Any]:
    """توحيد أسماء الحقائق المستخرجة وصيغ القيم."""
    normalized: Dict[str, Any] = {key: None for key, _, _ in TEST_METADATA}
    normalized["sex"] = None
    normalized["age"] = None

    for raw_key, val in raw_facts.items():
        clean_k = str(raw_key).strip().lower().replace(" ", "_")
        std_key = KEY_ALIASES.get(clean_k, clean_k)
        if std_key == "sex" and val is not None:
            s = str(val).strip().lower()
            if s in ("m", "male", "ذكر"):
                normalized["sex"] = "male"
            elif s in ("f", "female", "أنثى", "انثى"):
                normalized["sex"] = "female"
        elif std_key == "age" and val is not None:
            try:
                normalized["age"] = int(float(val))
            except (ValueError, TypeError):
                normalized["age"] = None
        elif std_key in normalized and val is not None:
            try:
                normalized[std_key] = float(val)
            except (ValueError, TypeError):
                normalized[std_key] = None

    return normalized


def _get_reference_ranges(sex: Optional[str]) -> Dict[str, Tuple[float, float]]:
    """تحديد المجالات المرجعية المعتمدة حسب الجنس."""
    is_female = sex == "female"
    return {
        "hb": (12.0, 16.0) if is_female else (13.0, 18.0),
        "pcv": (36.0, 48.0) if is_female else (40.0, 54.0),
        "wbc": (4.0, 10.0),
        "neutrophils_pct": (40.0, 70.0),
        "lymphocytes_pct": (20.0, 45.0),
        "monocytes_pct": (2.0, 10.0),
        "eosinophils_pct": (0.0, 6.0),
        "neutrophils_abs": (1.8, 7.0),
        "lymphocytes_abs": (1.0, 4.3),
        "monocytes_abs": (0.0, 0.8),
        "eosinophils_abs": (0.0, 0.5),
        "rbc": (4.0, 5.5) if is_female else (4.5, 6.0),
        "mcv": (80.0, 100.0),
        "mch": (27.0, 32.0),
        "mchc": (32.0, 36.0),
        "rdw": (11.5, 14.5),
        "platelets": (150.0, 400.0),
    }


def _evaluate_statuses(facts: Dict[str, Any], refs: Dict[str, Tuple[float, float]]) -> Dict[str, Dict[str, Any]]:
    """مقارنة جميع الفحوصات الـ 17 بالمجال المرجعي."""
    statuses: Dict[str, Dict[str, Any]] = {}
    for key, name, unit in TEST_METADATA:
        val = facts.get(key)
        r_min, r_max = refs[key]
        if val is None:
            status = "قيمة غير متوفرة"
        elif val < r_min:
            status = "منخفض"
        elif val > r_max:
            status = "مرتفع"
        else:
            status = "طبيعي"

        statuses[key] = {
            "name": name,
            "value": val,
            "unit": unit,
            "reference": (r_min, r_max),
            "status": status,
        }
    return statuses


def run_inference(raw_facts: Dict[str, Any]) -> Dict[str, Any]:
    """محرك الاستدلال الأمامي (Forward-Chaining Engine) لتقييم 30 قاعدة طبية."""
    facts = _normalize_facts(raw_facts)
    refs = _get_reference_ranges(facts.get("sex"))

    # قاعدة R23: حساب القيم المطلقة للخلايا البيضاء تلقائياً إذا توفرت النسب المئوية وWBC
    r23_calculated: List[str] = []
    wbc = facts.get("wbc")
    if wbc is not None:
        diff_pairs = [
            ("neutrophils_pct", "neutrophils_abs"),
            ("lymphocytes_pct", "lymphocytes_abs"),
            ("monocytes_pct", "monocytes_abs"),
            ("eosinophils_pct", "eosinophils_abs"),
        ]
        for pct_k, abs_k in diff_pairs:
            if facts.get(pct_k) is not None and facts.get(abs_k) is None:
                facts[abs_k] = round((wbc * facts[pct_k]) / 100.0, 2)
                r23_calculated.append(f"{abs_k}={facts[abs_k]}")

    statuses = _evaluate_statuses(facts, refs)

    hb = facts.get("hb")
    pcv = facts.get("pcv")
    rbc = facts.get("rbc")
    mcv = facts.get("mcv")
    mch = facts.get("mch")
    mchc = facts.get("mchc")
    rdw = facts.get("rdw")
    plt = facts.get("platelets")
    age = facts.get("age")

    hb_min, hb_max = refs["hb"]
    rbc_min, _ = refs["rbc"]

    neut_abs = facts.get("neutrophils_abs")
    neut_pct = facts.get("neutrophils_pct")
    lymph_abs = facts.get("lymphocytes_abs")
    lymph_pct = facts.get("lymphocytes_pct")
    mono_abs = facts.get("monocytes_abs")
    mono_pct = facts.get("monocytes_pct")
    eos_abs = facts.get("eosinophils_abs")
    eos_pct = facts.get("eosinophils_pct")

    missing_keys = [key for key, _, _ in TEST_METADATA if facts.get(key) is None]

    # تعريف القواعد الطبية الـ 30
    rules_spec = [
        (
            "R01", "severe_anemia", "urgent",
            hb is not None and hb < 8.0,
            "فقر دم شديد (Severe Anemia)",
            f"قيمة الهيموجلوبين ({hb} g/dL) منخفضة بشكل حاد دون 8.0 g/dL، مما يستدعي تقييماً طبياً عاجلاً.",
        ),
        (
            "R02", "moderate_anemia", "warning",
            hb is not None and 8.0 <= hb < 10.0,
            "فقر دم متوسط (Moderate Anemia)",
            f"قيمة الهيموجلوبين ({hb} g/dL) تقع بين 8.0 و10.0 g/dL وتستوجب المتابعة الطبية.",
        ),
        (
            "R03", "mild_anemia", "info",
            hb is not None and 10.0 <= hb < hb_min,
            "فقر دم خفيف (Mild Anemia)",
            f"قيمة الهيموجلوبين ({hb} g/dL) أقل بقليل من الحد الطبيعي الأدنى ({hb_min} g/dL).",
        ),
        (
            "R04", "erythrocytosis_hb", "warning",
            hb is not None and hb > hb_max,
            "ارتفاع الهيموجلوبين (Elevated Hemoglobin)",
            f"قيمة الهيموجلوبين ({hb} g/dL) أعلى من الحد الطبيعي الأعلى ({hb_max} g/dL).",
        ),
        (
            "R05", "microcytosis_normal_hb", "info",
            mcv is not None and mcv < 80.0 and hb is not None and hb >= hb_min,
            "صغر الكريات دون انخفاض الهيموجلوبين",
            "MCV منخفض بينما Hb ضمن المجال المعتمد.",
        ),
        (
            "R06", "microcytic_anemia", "warning",
            hb is not None and hb < hb_min and mcv is not None and mcv < 80.0,
            "فقر دم صغير الكريات (Microcytic Anemia)",
            f"انخفاض الهيموجلوبين ({hb} g/dL) مع صغر متوسط حجم الكرية (MCV = {mcv} fL).",
        ),
        (
            "R07", "macrocytic_anemia", "warning",
            hb is not None and hb < hb_min and mcv is not None and mcv > 100.0,
            "فقر دم كبير الكريات (Macrocytic Anemia)",
            f"انخفاض الهيموجلوبين ({hb} g/dL) مع كبر متوسط حجم الكرية (MCV = {mcv} fL).",
        ),
        (
            "R08", "thalassemia_trait_pattern", "info",
            mcv is not None and mcv < 80.0 and rbc is not None and rbc >= rbc_min,
            "صغر الكريات مع RBC طبيعي أو مرتفع",
            "هذا النمط قد يرتبط بسمة الثلاسيميا، لذا لا يُؤكد التشخيص.",
        ),
        (
            "R09", "hypochromic_microcytosis", "info",
            mcv is not None and mcv < 80.0 and mch is not None and mch < 27.0,
            "نموذج صغر الكريات ناقص الصباغ",
            "MCV منخفض وMCH منخفض.",
        ),
        (
            "R10", "anisocytosis_rdw", "info",
            rdw is not None and rdw > 14.5,
            "تباين في أحجام كريات الدم الحمراء (Anisocytosis)",
            f"ارتفاع مؤشر توزيع الكريات الحمراء (RDW = {rdw}%).",
        ),
        (
            "R11", "iron_deficiency_pattern", "warning",
            hb is not None and hb < hb_min and mcv is not None and mcv < 80.0 and rdw is not None and rdw > 14.5,
            "نمط متوافق مع فقر الدم بعوز الحديد",
            "اجتماع انخفاض Hb وMCV مع ارتفاع RDW يوجه نحو احتمالية نقص الحديد.",
        ),
        (
            "R12", "severe_leukopenia", "urgent",
            wbc is not None and wbc < 2.0,
            "انخفاض شديد في كريات الدم البيضاء (Severe Leukopenia)",
            f"عدد الكريات البيضاء ({wbc} ×10⁹/L) منخفض بشدة ويزيد خطر العدوى.",
        ),
        (
            "R13", "leukopenia", "warning",
            wbc is not None and 2.0 <= wbc < 4.0,
            "انخفاض كريات الدم البيضاء (Leukopenia)",
            f"عدد الكريات البيضاء ({wbc} ×10⁹/L) أقل من الحد الطبيعي (4.0 ×10⁹/L).",
        ),
        (
            "R14", "leukocytosis", "warning",
            wbc is not None and 10.0 < wbc <= 20.0,
            "ارتفاع كريات الدم البيضاء (Leukocytosis)",
            f"عدد الكريات البيضاء ({wbc} ×10⁹/L) مرتفع عن الحد الطبيعي (10.0 ×10⁹/L).",
        ),
        (
            "R15", "marked_leukocytosis", "urgent",
            wbc is not None and wbc > 20.0,
            "ارتفاع حاد في كريات الدم البيضاء (Marked Leukocytosis)",
            f"عدد الكريات البيضاء ({wbc} ×10⁹/L) مرتفع بشكل ملحوظ ويستدعي مراجعة طبية عاجلة.",
        ),
        (
            "R16", "neutropenia", "warning",
            (neut_abs is not None and neut_abs < 1.8) or (neut_abs is None and neut_pct is not None and neut_pct < 40.0),
            "انخفاض الخلايا المتعادلة (Neutropenia)",
            "انخفاض مستوى العدلات عن المجال المرجعي المعتمد.",
        ),
        (
            "R17", "neutrophilia", "info",
            (neut_abs is not None and neut_abs > 7.0) or (neut_abs is None and neut_pct is not None and neut_pct > 70.0),
            "ارتفاع الخلايا المتعادلة (Neutrophilia)",
            "ارتفاع مستوى العدلات، وغالباً ما يرتبط بالتهاب أو عدوى بكتيرية.",
        ),
        (
            "R18", "lymphopenia", "info",
            (lymph_abs is not None and lymph_abs < 1.0) or (lymph_abs is None and lymph_pct is not None and lymph_pct < 20.0),
            "انخفاض الخلايا الليمفاوية (Lymphopenia)",
            "انخفاض مستوى الخلايا الليمفاوية عن المجال المرجعي.",
        ),
        (
            "R19", "lymphocytosis", "info",
            (lymph_abs is not None and lymph_abs > 4.3) or (lymph_abs is None and lymph_pct is not None and lymph_pct > 45.0),
            "ارتفاع الخلايا الليمفاوية (Lymphocytosis)",
            "ارتفاع مستوى الخلايا الليمفاوية، وقد يرافق العدوى الفيروسية.",
        ),
        (
            "R20", "monocytosis", "info",
            (mono_abs is not None and mono_abs > 0.8) or (mono_abs is None and mono_pct is not None and mono_pct > 10.0),
            "ارتفاع الخلايا الوحيدة (Monocytosis)",
            "ارتفاع مستوى الوحيدات عن الحد المرجعي الأعلى.",
        ),
        (
            "R21", "eosinophilia", "info",
            (eos_abs is not None and eos_abs > 0.5) or (eos_abs is None and eos_pct is not None and eos_pct > 6.0),
            "ارتفاع الخلايا الحمضية (Eosinophilia)",
            "ارتفاع الحمضات، وغالباً ما يرتبط بالحساسية أو الطفيليات.",
        ),
        (
            "R22", "pancytopenia", "urgent",
            (hb is not None and hb < hb_min) and (wbc is not None and wbc < 4.0) and (plt is not None and plt < 150.0),
            "اشتباه قلة الكريات الشاملة (Pancytopenia)",
            "انخفاض متزامن في الهيموجلوبين والكريات البيضاء والصفائح الدموية يستوجب تقييماً عاجلاً.",
        ),
        (
            "R23", "auto_calc_differential", "info",
            bool(r23_calculated),
            "حساب القيم المطلقة للخلايا البيضاء تلقائياً",
            ", ".join(r23_calculated),
        ),
        (
            "R24", "severe_thrombocytopenia", "urgent",
            plt is not None and plt < 50.0,
            "انخفاض حاد في الصفائح الدموية (Severe Thrombocytopenia)",
            f"عدد الصفائح الدموية ({plt} ×10⁹/L) منخفض بشدة مع احتمالية خطورة نزفية.",
        ),
        (
            "R25", "thrombocytopenia", "warning",
            plt is not None and 50.0 <= plt < 150.0,
            "انخفاض الصفائح الدموية (Thrombocytopenia)",
            f"عدد الصفائح الدموية ({plt} ×10⁹/L) أقل من الحد الطبيعي (150 ×10⁹/L).",
        ),
        (
            "R26", "thrombocytosis", "info",
            plt is not None and 400.0 < plt <= 700.0,
            "ارتفاع الصفائح الدموية (Thrombocytosis)",
            f"عدد الصفائح الدموية ({plt} ×10⁹/L) أعلى من الحد الطبيعي (400 ×10⁹/L).",
        ),
        (
            "R27", "marked_thrombocytosis", "urgent",
            plt is not None and plt > 700.0,
            "ارتفاع شديد في الصفائح الدموية (Marked Thrombocytosis)",
            f"عدد الصفائح الدموية ({plt} ×10⁹/L) يتجاوز 700 ×10⁹/L ويستدعي مراجعة طبية عاجلة.",
        ),
        (
            "R28", "age_range_check", "warning",
            age is not None and (age < 18 or age > 65),
            "العمر خارج نطاق النظام (18–65 سنة)",
            f"عمر المريض ({age} سنة) يقع خارج النطاق المرجعي المخصص للبالغين في هذا النظام (18–65 سنة).",
        ),
        (
            "R29", "missing_data_check", "warning",
            len(missing_keys) > 0,
            "بيانات ناقصة",
            f"البيانات التي تحتاج إلى استكمال: {', '.join(missing_keys)}",
        ),
        (
            "R30", "elevated_mchc_check", "info",
            mchc is not None and mchc > 36.0,
            "ارتفاع تركيز هيموجلوبين الكرية (Elevated MCHC)",
            f"قيمة MCHC ({mchc} g/dL) تتجاوز الحد المرجعي الأعلى (36.0 g/dL).",
        ),
    ]

    fired_rules: List[Dict[str, Any]] = []
    checked_rules: List[Dict[str, Any]] = []

    for rule_id, func_name, alert_level, is_fired, conclusion, explanation in rules_spec:
        if is_fired:
            fired_rules.append({
                "rule_id": rule_id,
                "name": func_name,
                "alert": alert_level,
                "conclusion": conclusion,
                "explanation": explanation,
                "details": {},
            })
            checked_rules.append({
                "rule_id": rule_id,
                "function": func_name,
                "status": "مفعّلة (Fired)",
                "conclusion": conclusion,
            })
        else:
            checked_rules.append({
                "rule_id": rule_id,
                "function": func_name,
                "status": "تم الفحص (غير منطبقة)",
                "conclusion": conclusion,
            })

    return {
        "facts": facts,
        "statuses": statuses,
        "total_rules": len(rules_spec),
        "checked_count": len(checked_rules),
        "fired_count": len(fired_rules),
        "fired_rules": fired_rules,
        "checked_rules": checked_rules,
    }
