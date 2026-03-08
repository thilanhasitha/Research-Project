from extractor.pdf_locator import find_cashflow_pages
from extractor.table_extractor import extract_best_cashflow_table
from extractor.normalizer import normalize_cashflow_table, detect_scale_multiplier
from extractor.mapper import map_cfo_capex_from_table
from extractor.validator import validate_and_score

def extract_cashflow_from_pdf(pdf_path: str) -> dict:
    # 1) Find likely cashflow pages
    pages = find_cashflow_pages(pdf_path)
    if not pages:
        return {
            "pdf": pdf_path,
            "status": "failed",
            "reason": "Cash flow section not found",
            "cashflow": []
        }

    # 2) Extract best table from candidate pages (Camelot)
    best = extract_best_cashflow_table(pdf_path, pages)
    if best is None:
        return {
            "pdf": pdf_path,
            "status": "failed",
            "reason": "No usable table extracted from candidate pages",
            "cashflow": []
        }

    raw_df, meta = best["df"], best["meta"]

    # 3) Normalize (headers, numbers, scale)
    scale_mult = detect_scale_multiplier(meta.get("page_text", ""))
    df = normalize_cashflow_table(raw_df, scale_mult=scale_mult)

    # 4) Map to CFO/CAPEX per year
    mapped = map_cfo_capex_from_table(df)

    # 5) Validate + confidence scoring
    validated = validate_and_score(mapped)

    return {
        "pdf": pdf_path,
        "status": "success",
        "candidate_pages": pages,
        "detected_scale_multiplier": scale_mult,
        "meta": meta,
        "cashflow": validated
    }
