import re
import pdfplumber

KEY_PATTERNS = [
    r"statement\s+of\s+cash\s+flows",
    r"cash\s+flow\s+statement",
    r"cash\s+flows\s+from\s+operating\s+activities",
]

def find_cashflow_pages(pdf_path: str, max_pages_to_scan: int = 250) -> list[int]:
    hits = []
    patterns = [re.compile(p, re.IGNORECASE) for p in KEY_PATTERNS]

    with pdfplumber.open(pdf_path) as pdf:
        total = min(len(pdf.pages), max_pages_to_scan)
        for i in range(total):
            text = pdf.pages[i].extract_text() or ""
            if any(p.search(text) for p in patterns):
                hits.append(i + 1)  # Camelot uses 1-based page numbers

    # Expand around hits (tables may be on next page)
    expanded = set()
    for p in hits:
        for q in (p-1, p, p+1):
            if q >= 1:
                expanded.add(q)

    return sorted(expanded)
