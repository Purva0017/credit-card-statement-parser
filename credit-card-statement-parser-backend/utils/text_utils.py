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
    """
    Heuristic currency symbol detection from statement text.
    Defaults to '₹' when not confidently detected.
    """
    if not text:
        return "₹"
    sample = text[:8000]
    # INR cues
    if "₹" in sample or re.search(r"\bINR\b", sample, re.I) or re.search(r"\bRs\.?\b", sample, re.I):
        return "₹"
    # USD cues
    if "$" in sample or re.search(r"\bUSD\b", sample, re.I):
        return "$"
    # Extend for other currencies as needed
    return "₹"