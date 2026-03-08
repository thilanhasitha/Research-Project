import re
import camelot

def _score_table(df) -> int:
    text = " ".join(df.astype(str).fillna("").values.flatten()).lower()

    score = 0
    for kw, pts in [
        ("operating activities", 4),
        ("investing activities", 4),
        ("financing activities", 4),
        ("net cash", 3),
        ("cash and cash equivalents", 2),
    ]:
        if kw in text:
            score += pts

    # Reward presence of year-like tokens
    years = re.findall(r"(19|20)\d{2}", text)
    score += min(len(set(years)), 5)

    # Basic shape sanity
    if df.shape[0] < 8: score -= 3
    if df.shape[1] < 3: score -= 3

    return score

def extract_best_cashflow_table(pdf_path: str, pages: list[int]):
    best = None
    best_score = -10**9

    for p in pages:
        page_str = str(p)

        # Try lattice first (works when table lines exist)
        for flavor in ["lattice", "stream"]:
            try:
                tables = camelot.read_pdf(pdf_path, pages=page_str, flavor=flavor)
            except Exception:
                continue

            for t in tables:
                df = t.df
                s = _score_table(df)
                if s > best_score:
                    best_score = s
                    best = {
                        "df": df,
                        "meta": {
                            "page": p,
                            "flavor": flavor,
                            "table_accuracy": getattr(t, "accuracy", None),
                            "whitespace": getattr(t, "whitespace", None),
                            # You can later attach page text from pdfplumber if you want
                            "page_text": ""  
                        }
                    }

    return best
