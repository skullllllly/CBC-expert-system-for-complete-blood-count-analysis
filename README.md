# CBC Expert System

A Python and Streamlit decision-support prototype that extracts CBC values from text-based PDF reports, evaluates them with 30 rules, and presents findings in an Arabic dashboard.

> **Medical notice:** This project is not a diagnostic device and does not replace a qualified clinician. Its results require medical review.

## How it works

1. The user uploads a CBC PDF.
2. PyMuPDF extracts text; the parser extracts CBC facts, age, and sex.
3. The inference engine normalizes values, checks reference ranges, and evaluates rules.
4. The explanation module groups findings and the Streamlit app displays results and the rule trace.

## Project structure

```text
app.py                  Streamlit interface
pdf_processing/         PDF text extraction and CBC parsing
inference_engine/       Fact normalization, 30 rules, explanations
knowledge_base/         Reference data and standalone rule tests
requirements.txt        Pinned Python dependencies
```

The active app uses `inference_engine/engine.py`. It evaluates 17 indicators, including hemoglobin, WBC, platelets, RBC, and red-cell indices. It can calculate absolute white-cell counts when WBC and differential percentages are available.

## Setup and run

Use Python 3.10 or compatible. From the project root on Windows:

```powershell
py -3.10 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`, then upload a CBC PDF.

## Tests

Run the WBC normalization regression tests from the project root:

```powershell
.\venv\Scripts\python.exe -m unittest -v inference_engine.test_engine
```

The parser recognizes `T.WBC`; the inference engine maps `T.WBC` and `T_WBC` to the canonical `wbc` fact.

## Limitations

- PDFs must contain extractable text. Scanned/image-only reports require OCR, which is not implemented.
- Parsing depends on report labels and layout; other formats may need additional aliases or parser support.
- Reference ranges are hard-coded and do not account for every age group or laboratory.
- The repository has separate rule implementations; the Streamlit app uses the inference engine implementation.
- Clinical validation and a physician-reviewed knowledge base are required before real clinical use.
