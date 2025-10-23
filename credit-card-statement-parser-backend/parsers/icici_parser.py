import re
from datetime import datetime

def extract_date(text):
    match = re.search(r'([A-Za-z]+\s\d{1,2},\s\d{4})', text)
    if match:
        try:
            return datetime.strptime(match.group(1), "%B %d, %Y").strftime("%Y-%m-%d")
        except ValueError:
            return match.group(1)
    return None

def fuzzy_label_regex(label):
    """
    Build a regex to handle:
    - repeated letters (S+T+A+T+E+M+E+N+T+)
    - arbitrary spaces/newlines between letters (\s*)
    - OCR artifacts
    """
    regex = ""
    for c in label.upper():
        if c.isalpha():
            regex += f"{c}+\\s*"  # repeated letter + optional whitespace/newline
        else:
            regex += re.escape(c) + "\\s*"
    return regex

def parse_icici(text):
    result = {
        "bank": "ICICI",
        "card_last4": None,
        "statement_date": None,
        "payment_due_date": None,
        "total_amount_due": None
    }

    # --- CARD LAST 4 ---
    match_card = re.search(r'X{4,}\s*?(\d{4})', text)
    if match_card:
        result["card_last4"] = match_card.group(1)

    # --- STATEMENT DATE ---
    stmt_regex = re.compile(fuzzy_label_regex("STATEMENT DATE") + r'([A-Za-z]+\s\d{1,2},\s\d{4})', re.IGNORECASE)
    stmt_match = stmt_regex.search(text)
    if stmt_match:
        result["statement_date"] = extract_date(stmt_match.group(1))
    else:
        # fallback generic search: look for any 'STATEMENT' followed by a date within 50 chars
        stmt_fallback = re.search(r'STATEMENT.{0,50}?([A-Za-z]+\s\d{1,2},\s\d{4})', text, re.IGNORECASE | re.DOTALL)
        if stmt_fallback:
            result["statement_date"] = extract_date(stmt_fallback.group(1))

    # --- PAYMENT DUE DATE ---
    due_regex = re.compile(fuzzy_label_regex("PAYMENT DUE DATE") + r'([A-Za-z]+\s\d{1,2},\s\d{4})', re.IGNORECASE)
    due_match = due_regex.search(text)
    if due_match:
        result["payment_due_date"] = extract_date(due_match.group(1))
    else:
        # fallback generic search: look for any 'PAYMENT' + 'DUE' within 50 chars of a date
        due_fallback = re.search(r'PAYMENT.{0,50}?DUE.{0,20}?([A-Za-z]+\s\d{1,2},\s\d{4})', text, re.IGNORECASE | re.DOTALL)
        if due_fallback:
            result["payment_due_date"] = extract_date(due_fallback.group(1))

    # --- TOTAL AMOUNT DUE ---
    amt_match = re.search(r'(total\s*amount\s*due)[^\d]*[`₹]?\s?([\d,]+\.\d{2})', text, re.IGNORECASE)
    if amt_match:
        result["total_amount_due"] = amt_match.group(2).replace(",", "")

    return result
