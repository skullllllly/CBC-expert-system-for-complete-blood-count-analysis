from medical_knowledge import REFERENCE_RANGES


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def create_result(rule_id, name, conclusion, explanation,
                  alert="info", details=None):

    return {
        "rule_id": rule_id,
        "name": name,
        "conclusion": conclusion,
        "explanation": explanation,
        "alert": alert,
        "details": details or {}
    }


def get_value(facts, key):
    return facts.get(key)


def is_below(value, test_name):
    if value is None:
        return False

    reference = REFERENCE_RANGES[test_name]
    return value < reference["min"]


def is_above(value, test_name):
    if value is None:
        return False

    reference = REFERENCE_RANGES[test_name]
    return value > reference["max"]


def is_normal(value, test_name):
    if value is None:
        return False

    reference = REFERENCE_RANGES[test_name]

    return (
        reference["min"] <= value <= reference["max"]
    )


def get_hb_limit(sex):
    if sex == "male":
        return 13

    elif sex == "female":
        return 12

    return None


def is_low_hb(facts):
    hb = get_value(facts, "hb")
    limit = get_hb_limit(get_value(facts, "sex"))

    return (
        hb is not None
        and limit is not None
        and hb < limit
    )


def is_normal_hb(facts):
    hb = get_value(facts, "hb")
    limit = get_hb_limit(get_value(facts, "sex"))

    return (
        hb is not None
        and limit is not None
        and limit <= hb <= REFERENCE_RANGES["hb"]["max"]
    )


# --------------------------------------------------
# Rule 01 - Low Hemoglobin
# --------------------------------------------------

def rule_01(f):

    if is_low_hb(f):
        return create_result(
            "R01",
            "Low Hemoglobin",
            "انخفاض الهيموغلوبين",
            "قيمة Hb أقل من الحد المعتمد للجنس."
        )

    return None


# --------------------------------------------------
# Rule 02 - Microcytic Anemia
# --------------------------------------------------

def rule_02(f):

    hb = get_value(f, "hb")
    mcv = get_value(f, "mcv")

    if is_low_hb(f) and mcv is not None and mcv < 80:
        return create_result(
            "R02",
            "Microcytic Anemia Pattern",
            "نمط فقر دم صغير الكريات",
            "Hb منخفض وMCV أقل من 80 fL."
        )

    return None


# --------------------------------------------------
# Rule 03 - Normocytic Anemia
# --------------------------------------------------

def rule_03(f):

    mcv = get_value(f, "mcv")

    if is_low_hb(f) and mcv is not None and 80 <= mcv <= 100:
        return create_result(
            "R03",
            "Normocytic Anemia Pattern",
            "نمط فقر دم طبيعي الكريات",
            "Hb منخفض وMCV بين 80 و100 fL."
        )

    return None


# --------------------------------------------------
# Rule 04 - Macrocytic Anemia
# --------------------------------------------------

def rule_04(f):

    mcv = get_value(f, "mcv")

    if is_low_hb(f) and mcv is not None and mcv > 100:
        return create_result(
            "R04",
            "Macrocytic Anemia Pattern",
            "نمط فقر دم كبير الكريات",
            "Hb منخفض وMCV أكبر من 100 fL."
        )

    return None


# --------------------------------------------------
# Rule 05 - Microcytosis Without Anemia
# --------------------------------------------------

def rule_05(f):

    mcv = get_value(f, "mcv")

    if (
        is_normal_hb(f)
        and mcv is not None
        and mcv < 80
    ):
        return create_result(
            "R05",
            "Microcytosis Without Anemia",
            "صغر الكريات دون انخفاض الهيموغلوبين",
            "MCV منخفض بينما Hb ضمن المجال المعتمد."
        )

    return None


# --------------------------------------------------
# Rule 06 - Macrocytosis Without Anemia
# --------------------------------------------------

def rule_06(f):

    mcv = get_value(f, "mcv")
    if (
        is_normal_hb(f)
        and mcv is not None
        and mcv > 100
    ):
        return create_result(
            "R06",
            "Macrocytosis Without Anemia",
            "كبر الكريات دون انخفاض الهيموغلوبين",
            "MCV مرتفع بينما Hb ضمن المجال المعتمد."
        )

    return None


# --------------------------------------------------
# Rule 07 - Low Hb and High RDW
# --------------------------------------------------

def rule_07(f):

    rdw = get_value(f, "rdw")

    if is_low_hb(f) and is_above(rdw, "rdw"):
        return create_result(
            "R07",
            "Low Hb and High RDW",
            "انخفاض Hb مع ارتفاع RDW",
            "Hb منخفض وRDW مرتفع، مما يشير إلى تفاوت أحجام كريات الدم الحمراء."
        )

    return None


# --------------------------------------------------
# Rule 08 - Microcytosis with Normal or High RBC
# --------------------------------------------------

def rule_08(f):

    mcv = get_value(f, "mcv")
    rbc = get_value(f, "rbc")

    if (
        mcv is not None
        and mcv < 80
        and rbc is not None
        and rbc >= REFERENCE_RANGES["rbc"]["min"]
    ):
        return create_result(
            "R08",
            "Microcytosis with Normal or High RBC",
            "صغر الكريات مع RBC طبيعي أو مرتفع",
            "هذا النمط قد يرتبط بسمة الثلاسيميا، لكنه لا يؤكد التشخيص."
        )

    return None


# --------------------------------------------------
# Rule 09 - Microcytic Hypochromic Pattern
# --------------------------------------------------

def rule_09(f):

    mcv = get_value(f, "mcv")
    mch = get_value(f, "mch")

    if (
        mcv is not None
        and mcv < 80
        and is_below(mch, "mch")
    ):
        return create_result(
            "R09",
            "Microcytic Hypochromic Pattern",
            "نمط صغير الكريات ناقص الصباغ",
            "MCV منخفض وMCH منخفض."
        )

    return None


# --------------------------------------------------
# Rule 10 - High RBC Indicators
# --------------------------------------------------

def rule_10(f):

    hb = get_value(f, "hb")
    pcv = get_value(f, "pcv")
    rbc = get_value(f, "rbc")

    if (
        hb is not None
        and hb > REFERENCE_RANGES["hb"]["max"]
        and is_above(pcv, "pcv")
        and is_above(rbc, "rbc")
    ):
        return create_result(
            "R10",
            "High RBC Indicators",
            "ارتفاع مؤشرات كريات الدم الحمراء",
            "Hb وPCV وRBC جميعها أعلى من حدودها المرجعية."
        )

    return None


# --------------------------------------------------
# Rule 11 - Leukopenia
# --------------------------------------------------

def rule_11(f):

    wbc = get_value(f, "wbc")

    if is_below(wbc, "wbc"):
        return create_result(
            "R11",
            "Leukopenia",
            "انخفاض كريات الدم البيضاء",
            "T.WBC أقل من 4 x10^9/L."
        )

    return None


# --------------------------------------------------
# Rule 12 - Leukocytosis
# --------------------------------------------------

def rule_12(f):

    wbc = get_value(f, "wbc")

    if is_above(wbc, "wbc"):
        return create_result(
            "R12",
            "Leukocytosis",
            "ارتفاع كريات الدم البيضاء",
            "T.WBC أعلى من 10 x10^9/L."
        )

    return None


# --------------------------------------------------
# Rule 13 - Low Absolute Neutrophils
# --------------------------------------------------

def rule_13(f):

    neut = get_absolute_value(
    f, "neutrophils_abs", "neutrophils_pct"
    )

    if is_below(neut, "neutrophils_abs"):
        return create_result(
            "R13",
            "Low Absolute Neutrophils",
            "انخفاض العدد المطلق للعدلات",
            "Neutrophils# أقل من 1.8 x10^9/L."
        )

    return None


# --------------------------------------------------
# Rule 14 - Severe Neutropenia
# --------------------------------------------------

def rule_14(f):

    neut = get_value(f, "neutrophils_abs")
    if neut is not None and neut < 0.5:
            return create_result(
                "R14",
                "Severe Neutropenia",
                "انخفاض شديد في العدلات",
                "Neutrophils# أقل من 0.5 x10^9/L. يتطلب تقييماً طبياً عاجلاً.",
                alert="urgent"
            )

    return None


# --------------------------------------------------
# Rule 15 - Lymphocytopenia
# --------------------------------------------------

def rule_15(f):

    lymph = get_absolute_value(
    f, "lymphocytes_abs", "lymphocytes_pct"
    )

    if is_below(lymph, "lymphocytes_abs"):
        return create_result(
            "R15",
            "Lymphocytopenia",
            "انخفاض الخلايا اللمفاوية",
            "Lymphocytes# أقل من 1 x10^9/L."
        )

    return None


# --------------------------------------------------
# Rule 16 - High Absolute Lymphocytes
# --------------------------------------------------

def rule_16(f):

    lymph = get_absolute_value(
    f, "lymphocytes_abs", "lymphocytes_pct"
    )

    if is_above(lymph, "lymphocytes_abs"):
        return create_result(
            "R16",
            "High Absolute Lymphocytes",
            "ارتفاع الخلايا اللمفاوية",
            "Lymphocytes# أعلى من 4.3 x10^9/L."
        )

    return None


# --------------------------------------------------
# Rule 17 - Eosinophilia
# --------------------------------------------------

def rule_17(f):

    eeos = get_absolute_value(
    f, "eosinophils_abs", "eosinophils_pct"
    )

    if is_above(eeos, "eosinophils_abs"):
        return create_result(
            "R17",
            "Eosinophilia",
            "ارتفاع الخلايا الحمضية",
            "Eosinophils# أعلى من 0.5 x10^9/L."
        )

    return None


# --------------------------------------------------
# Rule 18 - High Absolute Monocytes
# --------------------------------------------------

def rule_18(f):

    mono = get_absolute_value(
    f, "monocytes_abs", "monocytes_pct"
    )

    if is_above(mono, "monocytes_abs"):
        return create_result(
            "R18",
            "High Absolute Monocytes",
            "ارتفاع الخلايا الوحيدة",
            "Monocytes# أعلى من 0.8 x10^9/L."
        )

    return None


# --------------------------------------------------
# Rule 19 - Thrombocytopenia
# --------------------------------------------------

def rule_19(f):

    platelets = get_value(f, "platelets")

    if is_below(platelets, "platelets"):
        return create_result(
            "R19",
            "Thrombocytopenia",
            "انخفاض الصفائح الدموية",
            "Platelets أقل من 150 x10^9/L."
        )

    return None


# --------------------------------------------------
# Rule 20 - Low Platelets
# --------------------------------------------------

def rule_20(f):

    platelets = get_value(f, "platelets")

    if platelets is not None and platelets < 50:
        return create_result(
            "R20",
            "Low Platelets",
            "انخفاض واضح في الصفائح الدموية",
            "Platelets أقل من 50 x10^9/L. يتطلب تقييماً طبياً سريعاً.",
            alert="warning"
        )

    return None


# --------------------------------------------------
# Rule 21 - Critical Platelet Count
# --------------------------------------------------

def rule_21(f):

    platelets = get_value(f, "platelets")

    if platelets is not None and platelets < 20:
        return create_result(
            "R21",
            "Critical Platelet Count",
            "انخفاض حرج في الصفائح الدموية",
            "Platelets أقل من 20 x10^9/L. يتطلب تقييماً طبياً عاجلاً.",
            alert="urgent"
        )

    return None


# --------------------------------------------------
# Rule 22 - Thrombocytosis
# --------------------------------------------------

def rule_22(f):

    platelets = get_value(f, "platelets")

    if is_above(platelets, "platelets"):
        return create_result(
            "R22",
            "Thrombocytosis",
            "ارتفاع الصفائح الدموية",
            "Platelets أعلى من 450 x10^9/L."
        )

    return None


# --------------------------------------------------
# Rule 23 - Calculate Absolute Cell Counts
# --------------------------------------------------

def calculate_absolute_counts(facts):

    cell_types = {
        "neutrophils_pct": "neutrophils_abs",
        "lymphocytes_pct": "lymphocytes_abs",
        "monocytes_pct": "monocytes_abs",
        "eosinophils_pct": "eosinophils_abs"
    }

    calculated = {}

    wbc = get_value(facts, "wbc")

    if wbc is None:
        return calculated

    for percentage_key, absolute_key in cell_types.items():

        percentage = get_value(facts, percentage_key)

        if percentage is not None:
            calculated[absolute_key] = (
                wbc * percentage / 100
            )

    return calculated


def rule_23(f):

    calculated = calculate_absolute_counts(f)

    results = []

    for key, value in calculated.items():

        reference = REFERENCE_RANGES[key]

        results.append(
            create_result(
                "R23",
                "Absolute Cell Count Calculation",
                f"حساب العدد المطلق: {reference['name']}",
                (
                    f"WBC x النسبة المئوية / 100 = "
                    f"{value:.2f} {reference['unit']}"
                ),
                details={
                    "parameter": key,
                    "calculated_value": round(value, 2)
                }
            )
        )

    return results


# --------------------------------------------------
# Rule 24 - Relative Lymphocytosis
# --------------------------------------------------

def rule_24(f):

    percentage = get_value(f, "lymphocytes_pct")
    absolute = get_value(f, "lymphocytes_abs")

    if absolute is None:
        absolute = calculate_absolute_counts(f).get(
            "lymphocytes_abs"
        )

    if (
        is_above(percentage, "lymphocytes_pct")
        and is_normal(absolute, "lymphocytes_abs")
    ):
        return create_result(
            "R24",
            "Relative Lymphocytosis",
            "ارتفاع نسبي في نسبة الخلايا اللمفاوية",
            "نسبة اللمفاويات مرتفعة بينما عددها المطلق ضمن المجال المرجعي."
        )

    return None


# --------------------------------------------------
# Rule 25 - Relative Neutrophilia
# --------------------------------------------------

def rule_25(f):

    percentage = get_value(f, "neutrophils_pct")
    absolute = get_value(f, "neutrophils_abs")

    if absolute is None:
        absolute = calculate_absolute_counts(f).get(
            "neutrophils_abs"
        )

    if (
        is_above(percentage, "neutrophils_pct")
        and is_normal(absolute, "neutrophils_abs")
    ):
        return create_result(
            "R25",
            "Relative Neutrophilia",
            "ارتفاع نسبي في نسبة العدلات",
            "نسبة العدلات مرتفعة بينما عددها المطلق ضمن المجال المرجعي."
        )

    return None


# --------------------------------------------------
# Rule 26 - Pancytopenia Pattern
# --------------------------------------------------

def rule_26(f):

    wbc = get_value(f, "wbc")
    platelets = get_value(f, "platelets")

    if (
        is_low_hb(f)
        and is_below(wbc, "wbc")
        and is_below(platelets, "platelets")
    ):
        return create_result(
            "R26",
            "Pancytopenia Pattern",
            "نمط انخفاض خطوط خلايا الدم الثلاثة",
            "Hb وWBC والصفائح جميعها منخفضة. يتطلب تقييماً طبياً متخصصاً.",
            alert="warning"
        )

    return None


# --------------------------------------------------
# Rule 27 - Two Low Blood Cell Lines
# --------------------------------------------------

def rule_27(f):

    wbc = get_value(f, "wbc")
    platelets = get_value(f, "platelets")

    low_hb = is_low_hb(f)
    low_wbc = is_below(wbc, "wbc")
    low_platelets = is_below(platelets, "platelets")

    if (
        (low_hb and low_wbc)
        or (low_hb and low_platelets)
    ):
        return create_result(
            "R27",
            "Two Low Blood Cell Lines",
            "انخفاض متزامن في خطين من خلايا الدم",
            "Hb منخفض مع انخفاض WBC أو الصفائح الدموية.",
            alert="warning"
        )

    return None

# --------------------------------------------------
# Rule 28 - Age Out of Scope
# --------------------------------------------------

def rule_28(f):

    age = get_value(f, "age")

    if age is not None and (age < 18 or age > 65):
        return create_result(
            "R28",
            "Age Out of Scope",
            "العمر خارج نطاق النظام",
            "النظام مخصص للأعمار من 18 إلى 65 سنة.",
            alert="warning"
        )

    return None


# --------------------------------------------------
# Rule 29 - Missing Data
# --------------------------------------------------

def rule_29(f):

    required = [
        "age",
        "sex",
        "hb",
        "pcv",
        "wbc",
        "neutrophils_pct",
        "lymphocytes_pct",
        "monocytes_pct",
        "eosinophils_pct",
        "neutrophils_abs",
        "lymphocytes_abs",
        "monocytes_abs",
        "eosinophils_abs",
        "platelets",
        "rbc",
        "mcv",
        "mch",
        "mchc",
        "rdw"
    ]

    missing = [
        key for key in required
        if f.get(key) is None
    ]

    if missing:
        return create_result(
            "R29",
            "Missing Data",
            "بيانات ناقصة",
            "البيانات التي تحتاج إلى استكمال: "
            + ", ".join(missing),
            alert="warning",
            details={"missing_fields": missing}
        )

    return None


# --------------------------------------------------
# Rule 30 - Invalid Units
# --------------------------------------------------

def rule_30(f):

    if f.get("units_valid") is not True:
        return create_result(
            "R30",
            "Invalid or Unknown Units",
            "وحدات القياس غير معروفة أو غير متوافقة",
            "يجب التحقق من وحدات القياس قبل تفسير نتائج المؤشرات.",
            alert="warning"
        )

    return None


# --------------------------------------------------
# All 30 Rules
# --------------------------------------------------

RULES = [
    rule_01,
    rule_02,
    rule_03,
    rule_04,
    rule_05,
    rule_06,
    rule_07,
    rule_08,
    rule_09,
    rule_10,
    rule_11,
    rule_12,
    rule_13,
    rule_14,
    rule_15,
    rule_16,
    rule_17,
    rule_18,
    rule_19,
    rule_20,
    rule_21,
    rule_22,
    rule_23,
    rule_24,
    rule_25,
    rule_26,
    rule_27,
    rule_28,
    rule_29,
    rule_30
]


# --------------------------------------------------
# Evaluate All Rules
# --------------------------------------------------

def evaluate_rules(facts):

    results = []

    age_result = rule_28(facts)

    if age_result is not None:
        return [age_result]

    for rule in RULES:

        rule_result = rule(facts)

        if rule_result is None:
            continue

        if isinstance(rule_result, list):
            results.extend(rule_result)

        else:
            results.append(rule_result)

    return results


def get_absolute_value(facts, absolute_key, percentage_key):

    value = facts.get(absolute_key)

    if value is not None:
        return value

    wbc = facts.get("wbc")
    percentage = facts.get(percentage_key)

    if wbc is not None and percentage is not None:
        return wbc * percentage / 100

    return None


