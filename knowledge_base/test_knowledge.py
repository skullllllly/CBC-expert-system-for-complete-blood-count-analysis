from medical_knowledge import (
    REFERENCE_RANGES,
    classify_value,
    get_all_statuses
)

print("Number of CBC indicators:")
print(len(REFERENCE_RANGES))

print("\nTesting individual values:")

print("Hb:", classify_value("hb", 11))
print("MCV:", classify_value("mcv", 84))
print("Platelets:", classify_value("platelets", 500))

cbc_results = {
    "hb": 11,
    "pcv": 35,
    "wbc": 5,
    "mcv": 72,
    "mch": 24,
    "platelets": 250
}

print("\nComplete CBC Results:")

results = get_all_statuses(cbc_results)

for key, item in results.items():
    print(
        item["name"],
        item["value"],
        item["unit"],
        item["status"]
    )