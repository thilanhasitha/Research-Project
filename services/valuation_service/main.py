import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from google import genai
import config

app = FastAPI()

MODEL = "gemini-2.5-flash"

EXTRACTION_PROMPT = """
You are a financial report data extraction engine.

Task:
Extract yearly values from the company's annual report (PDF) for:
1) Net cash from operating activities (CFO)
2) Capital expenditure (CAPEX) specifically purchases/additions/acquisition of property, plant and equipment (PPE)

Rules:
- Return ONLY valid JSON. No markdown. No explanation.
- Values must be numbers (LKR) as shown in the report. If the report indicates scale (e.g., Rs '000 or in millions), include it in "scale" field.
- If a value is shown in brackets like (1,234), treat it as negative.
- If you cannot find a value for a year, set it as null.
- CAPEX should represent cash outflow (negative). If it appears positive, convert to negative.

JSON format exactly:
{
  "company_name": null,
  "currency": "LKR",
  "scale": "as_reported_or_unknown",
  "cashflow": [
    {"year": 2020, "CFO": 0, "CAPEX": 0},
    {"year": 2021, "CFO": 0, "CAPEX": 0}
  ],
  "source_notes": {
    "cashflow_statement_pages": [],
    "cfo_label_found": null,
    "capex_label_found": null
  }
}
"""

def safe_json_parse(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end+1])
        raise ValueError("Gemini response was not valid JSON")

def extract_from_pdf(pdf_path: str) -> dict:
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    client = genai.Client(api_key=config.GEMINI_API_KEY)

    uploaded = client.files.upload(file=str(pdf_path))

    resp = client.models.generate_content(
        model=MODEL,
        contents=[EXTRACTION_PROMPT, uploaded],
        config={"temperature": 0}
    )

    raw_text = (resp.text or "").strip()
    data = safe_json_parse(raw_text)
    return data

@app.get("/")
def root():
    return {"status": "ok", "message": "Gemini PDF extractor is running"}

@app.get("/extract")
def extract(pdf: str = Query(..., description="Server-side path to the PDF file, e.g. uploads/annual_report.pdf")):
    """
    Example:
      GET /extract?pdf=uploads/annual_report.pdf
    """
    # Basic safety: restrict to uploads folder
    pdf_path = Path(pdf).resolve()
    uploads_dir = Path("uploads").resolve()

    if uploads_dir not in pdf_path.parents:
        raise HTTPException(status_code=400, detail="PDF path must be inside the uploads/ directory")

    try:
        result = extract_from_pdf(str(pdf_path))
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=502, detail=f"Model did not return valid JSON: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")
