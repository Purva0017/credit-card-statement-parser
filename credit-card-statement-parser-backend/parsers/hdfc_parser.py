import re
from datetime import datetime

def normalize_amount(s):
    if not s:
        return None
    s = s.replace("`", "").replace("₹", "").replace(",", "").strip()
    m = re.search(r"(\d+(?:\.\d{1,2})?)", s)
    return m.group(1) if m else None


def normalize_date_str(date_str):
    """Try multiple date formats and return YYYY-MM-DD or original if parsing fails."""
    if not date_str:
        return None
    date_str = date_str.strip()
    fmts = [
        "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y",
        "%d-%b-%Y", "%d %b %Y", "%B %d, %Y", "%b %d, %Y"
    ]
    date_str = re.sub(r'\s+', ' ', date_str)
    for f in fmts:
        try:
            dt = datetime.strptime(date_str, f)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            continue
    m = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', date_str)
    if m:
        token = m.group(1)
        for f in ["%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y"]:
            try:
                dt = datetime.strptime(token, f)
                return dt.strftime("%Y-%m-%d")
            except Exception:
                continue
    return date_str


def extract_last4_from_cardno(text):
    if not text:
        return None

    m = re.search(r'card\s*no[:\s]*([0-9Xx\s\-]{8,30})', text, re.IGNORECASE)
    if m:
        digits = re.findall(r'\d', m.group(1))
        if len(digits) >= 4:
            return "".join(digits[-4:])

    m2 = re.search(r'(\d{4}[\s\-]?\d{2}X{2}[\s\-]?\w*[\s\-]?\d{4})', text)
    if m2:
        digits = re.findall(r'\d', m2.group(0))
        if len(digits) >= 4:
            return "".join(digits[-4:])

    m3 = re.search(r'[Xx]{2,}[^0-9]*?(\d{4})', text)
    if m3:
        return m3.group(1)

    m4 = re.search(r'\b(?:\d[ -]?){12,19}\b', text)
    if m4:
        digits = re.findall(r'\d', m4.group(0))
        if len(digits) >= 4:
            return "".join(digits[-4:])
    return None


def find_payment_row_three_columns(text):
    pattern = re.compile(
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+[`₹]?\s*([\d,]+\.\d{2})\s+[`₹]?\s*([\d,]+\.\d{2})',
        re.IGNORECASE
    )
    m = pattern.search(text)
    if m:
        return (m.group(1), m.group(2), m.group(3))
    pattern2 = re.compile(
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*[|,]\s*[`₹]?\s*([\d,]+\.\d{2})\s*[|,]\s*[`₹]?\s*([\d,]+\.\d{2})',
        re.IGNORECASE
    )
    m2 = pattern2.search(text)
    if m2:
        return (m2.group(1), m2.group(2), m2.group(3))
    return None


def find_label_following_date(label_words, text):
    """Find a date occurring after a textual label, tolerant to OCR spacing and distortions."""
    def flexible_label_regex(label):
        r = ""
        for ch in label:
            if ch.isalpha():
                r += f"{ch}+\\s*"
            else:
                r += re.escape(ch) + "\\s*"
        return r

    lab = flexible_label_regex(label_words.upper())
    regex = re.compile(
        lab + r'.{0,80}?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|[A-Za-z]{3,9}\s+\d{1,2},\s*\d{4})',
        re.IGNORECASE | re.DOTALL
    )
    m = regex.search(text)
    if m:
        return m.group(1)
    return None


def parse_hdfc(text):
    result = {
        "bank": "HDFC",
        "card_last4": None,
        "statement_date": None,
        "payment_due_date": None,
        "total_amount_due": None
    }

    if not text:
        return result

    text_joined = re.sub(r'\r\n?', '\n', text)
    text_flat = re.sub(r'\s+', ' ', text_joined)

    # --- CARD LAST 4 ---
    result["card_last4"] = extract_last4_from_cardno(text_flat)

    # --- 3-column row fallback ---
    triple = find_payment_row_three_columns(text_flat)
    if triple:
        date_token, total_s, min_s = triple
        result["payment_due_date"] = normalize_date_str(date_token)
        result["total_amount_due"] = normalize_amount(total_s)
    else:
        # --- STATEMENT DATE ---
        stmt_token = (
            find_label_following_date("Statement Date", text_joined)
            or find_label_following_date("Statement for HDFC Bank Credit Card", text_joined)
        )
        if stmt_token:
            result["statement_date"] = normalize_date_str(stmt_token)
        else:
            m = re.search(
                r'Statement.{0,60}?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                text_joined, re.IGNORECASE | re.DOTALL
            )
            if m:
                result["statement_date"] = normalize_date_str(m.group(1))

        # --- PAYMENT DUE DATE ---
        pay_token = (
            find_label_following_date("Payment Due Date", text_joined)
            or find_label_following_date("Payment Due", text_joined)
            or find_label_following_date("Pay By", text_joined)
        )
        if pay_token:
            result["payment_due_date"] = normalize_date_str(pay_token)

        # --- TOTAL AMOUNT DUE ---
        if not result["total_amount_due"]:
            m_total = re.search(
                r'(?:Total\s+Dues|Total\s+Amount\s+Due|Total\s+Due)\D+[`₹]?\s*([\d,]+\.\d{2})',
                text_flat, re.IGNORECASE
            )
            if not m_total:
                m_total = re.search(
                    r'(?:Total\s+Dues).{0,60}?[`₹]?\s*([\d,]+\.\d{2})',
                    text_joined, re.IGNORECASE | re.DOTALL
                )
            if m_total:
                result["total_amount_due"] = normalize_amount(m_total.group(1))

    # --- Additional fallback for statement_date ---
    if not result["statement_date"]:
        top_slice = text_joined[:800]
        m = re.search(r'([A-Za-z]{3,9}\s+\d{1,2},\s*\d{4})', top_slice)
        if not m:
            m = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', top_slice)
        if m:
            result["statement_date"] = normalize_date_str(m.group(1))

    # --- Additional fallback for payment_due_date ---
    if not result["payment_due_date"]:
        m2 = re.search(
            r'(?:Due Date|Payment Due|Pay By)[^\dA-Za-z]{0,30}(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|[A-Za-z]{3,9}\s+\d{1,2},\s*\d{4})',
            text_joined, re.IGNORECASE
        )
        if m2:
            result["payment_due_date"] = normalize_date_str(m2.group(1))

    return result
