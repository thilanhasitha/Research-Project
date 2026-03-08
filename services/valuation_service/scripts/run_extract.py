import json
from pathlib import Path
from extractor.pipeline import extract_cashflow_from_pdf

INPUT_DIR = Path("data/input_pdfs")
OUTPUT_DIR = Path("data/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    for pdf_path in INPUT_DIR.glob("*.pdf"):
        print(f"\n=== Processing: {pdf_path.name} ===")
        result = extract_cashflow_from_pdf(str(pdf_path))

        out_json = OUTPUT_DIR / (pdf_path.stem + "_cashflow.json")
        out_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

        print(f"Saved -> {out_json}")

if __name__ == "__main__":
    main()
