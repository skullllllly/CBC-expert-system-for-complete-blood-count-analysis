REFERENCE_RANGES = {
    "hb": {
        "name": "Hemoglobin",
        "min": 13.0,
        "max": 18.0,
        "unit": "g/dL"
    },

    "pcv": {
        "name": "Packed Cell Volume",
        "min": 40,
        "max": 54,
        "unit": "%"
    },

    "wbc": {
        "name": "Total White Blood Cells",
        "min": 4.0,
        "max": 10.0,
        "unit": "x10^9/L"
    },

    "neutrophils_pct": {
        "name": "Neutrophils Percentage",
        "min": 40,
        "max": 70,
        "unit": "%"
    },

    "lymphocytes_pct": {
        "name": "Lymphocytes Percentage",
        "min": 20,
        "max": 45,
        "unit": "%"
    },

    "monocytes_pct": {
        "name": "Monocytes Percentage",
        "min": 2,
        "max": 10,
        "unit": "%"
    },

    "eosinophils_pct": {
        "name": "Eosinophils Percentage",
        "min": 0,
        "max": 6,
        "unit": "%"
    },

    "neutrophils_abs": {
        "name": "Absolute Neutrophils",
        "min": 1.8,
        "max": 7.0,
        "unit": "x10^9/L"
    },

    "lymphocytes_abs": {
        "name": "Absolute Lymphocytes",
        "min": 1.0,
        "max": 4.3,
        "unit": "x10^9/L"
    },

    "monocytes_abs": {
        "name": "Absolute Monocytes",
        "min": 0.0,
        "max": 0.8,
        "unit": "x10^9/L"
    },

    "eosinophils_abs": {
        "name": "Absolute Eosinophils",
        "min": 0.0,
        "max": 0.5,
        "unit": "x10^9/L"
    },

    "platelets": {
        "name": "Platelet Count",
        "min": 150,
        "max": 450,
        "unit": "x10^9/L"
    },

    "rbc": {
        "name": "Red Blood Cells",
        "min": 4.5,
        "max": 6.5,
        "unit": "x10^12/L"
    },

    "mcv": {
        "name": "Mean Corpuscular Volume",
        "min": 76,
        "max": 96,
        "unit": "fL"
    },

    "mch": {
        "name": "Mean Corpuscular Hemoglobin",
        "min": 27,
        "max": 32,
        "unit": "pg"
    },

    "mchc": {
        "name": "Mean Corpuscular Hemoglobin Concentration",
        "min": 30,
        "max": 35,
        "unit": "g/dL"
    },

    "rdw": {
        "name": "Red Cell Distribution Width",
        "min": 11.5,
        "max": 14.5,
        "unit": "%"
    }
}


def get_reference_range(test_name):
    return REFERENCE_RANGES.get(test_name)


def classify_value(test_name, value):

    reference = get_reference_range(test_name)

    if reference is None:
        return "مؤشر غير معروف"

    if value is None:
        return "قيمة غير متوفرة"

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "قيمة غير صالحة"

    if value < reference["min"]:
        return "منخفض"

    elif value > reference["max"]:
        return "مرتفع"

    else:
        return "طبيعي"


def get_all_statuses(cbc_results):

    statuses = {}

    for test_name, value in cbc_results.items():

        if test_name in REFERENCE_RANGES:

            statuses[test_name] = {
                "name": REFERENCE_RANGES[test_name]["name"],
                "value": value,
                "unit": REFERENCE_RANGES[test_name]["unit"],
                "reference": (
                    REFERENCE_RANGES[test_name]["min"],
                    REFERENCE_RANGES[test_name]["max"]
                ),
                "status": classify_value(test_name, value)
            }

    return statuses