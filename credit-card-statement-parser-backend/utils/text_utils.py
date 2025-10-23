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