import re
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from pdf_processing.reader import read_pdf, DEFAULT_PDF

CBC_TESTS = [
    "Hb", "PCV", "T.WBC",
    "Neutrophil%", "Lymphocyte%", "Monocyte%", "Eosinophil%",
    "Neutrophil#", "Lymphocyte#", "Monocyte#", "Eosinophil#",
    "Platelets", "RBC", "MCV", "MCH", "MCHC", "RDW"
]

def extract_facts(text: str) -> dict:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    facts = {}

    for i, line in enumerate(lines):
        if line in ("Male", "Female") and "Sex" not in facts:
            facts["Sex"] = line

        age_match = re.fullmatch(r"(\d+)\s*(?:Y|YR|YEAR|YEARS)", line, re.IGNORECASE)
        if age_match and "Age" not in facts:
            facts["Age"] = int(age_match.group(1))

        test_name = re.sub(r"\s+", "", line)
        if test_name in CBC_TESTS and test_name not in facts:
            for j in range(1, 4):
                if i + j < len(lines):
                    candidate = lines[i + j]
                    if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", candidate):
                        facts[test_name] = float(candidate)
                        break

    return facts

if __name__ == "__main__":
    raw_text = read_pdf(DEFAULT_PDF)
    facts = extract_facts(raw_text)
    for key, value in facts.items():
        print(f"{key}: {value}")