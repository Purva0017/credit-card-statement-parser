import re

def normalize_text(t: str) -> str:
    if not t:
        return ""
    t = t.replace("\xa0", " ")              # NBSP → space
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"[–—−]", "-", t)            # en/em dashes → hyphen
    t = re.sub(r"(?i)\bRs\.?\s*", "₹", t)   # Rs./Rs → ₹
    t = re.sub(r"₹\s*", "₹", t)             # remove space after ₹
    t = re.sub(r"[ \t]+", " ", t)           # collapse spaces
    return t.strip()

def detect_currency_symbol(text: str) -> str:
    """Detect currency symbol from text. Defaults to ₹ if uncertain.

    Heuristics:
    - If '₹', 'Rs', 'INR' present → ₹
    - Else if '$' or 'USD' present → $
    - Else default to ₹
    """
    t = text or ""
    if re.search(r"(₹|\bRs\.?\b|\bINR\b)", t, re.IGNORECASE):
        return "₹"
    if re.search(r"(\$|\bUSD\b)", t, re.IGNORECASE):
        return "$"
    return "₹"

def detect_currency_code(text: str) -> str:
    """Detect currency code (unit) from text. Defaults to INR if uncertain."""
    t = text or ""
    if re.search(r"(₹|\bRs\.?\b|\bINR\b)", t, re.IGNORECASE):
        return "INR"
    if re.search(r"(\$|\bUSD\b)", t, re.IGNORECASE):
        return "USD"
    return "INR"