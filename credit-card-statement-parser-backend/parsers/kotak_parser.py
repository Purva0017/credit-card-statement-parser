import re
from datetime import datetime
from utils.text_utils import detect_currency_symbol

def extract_date(text):
    """Extract date in format like 20-Nov-2024 or 20/11/2024 and normalize to YYYY-MM-DD"""
    match = re.search(r'\d{1,2}[-/]\w{3,}[-/]\d{2,4}', text)
    if match:
        try:
            return datetime.strptime(match.group(0), "%d-%b-%Y").strftime("%Y-%m-%d")
        except ValueError:
            # fallback for other formats
            return match.group(0)
    return None

def extract_amount(text):
    """Extract amount like Rs.88,375.20 or `88,375.20 and normalize"""
    match = re.search(r'(?:₹|`)?\s?([\d,]+\.\d{2})', text)
    return match.group(1).replace(",", "") if match else None

def parse_kotak(text):
    result = {
        "bank": "KOTAK",
        "card_last4": None,
        "statement_date": None,
        "payment_due_date": None,
        "total_amount_due": None,
        "currency_symbol": None,
    }

    # --- CARD LAST 4 ---
    match_card = re.search(r'X{4,}(\d{4})', text)
    if match_card:
        result["card_last4"] = match_card.group(1)

    # --- STATEMENT DATE ---
    stmt_line = re.search(r'(statement\s*date|statement\s*generated\s*on)[:\s]*([\d]{1,2}-[A-Za-z]{3}-[\d]{4})', text, re.IGNORECASE)
    if stmt_line:
        result["statement_date"] = extract_date(stmt_line.group(2))
    else:
        # fallback: search line containing StatementDate
        stmt_fallback = re.search(r'StatementDate\s*([\d]{1,2}-[A-Za-z]{3}-[\d]{4})', text)
        if stmt_fallback:
            result["statement_date"] = extract_date(stmt_fallback.group(1))

    # --- PAYMENT DUE DATE ---
    due_line = re.search(r'(payment\s*due\s*date|remember\s*to\s*pay\s*by)[:\s]*(No payment required|[\d]{1,2}-[A-Za-z]{3}-[\d]{4})', text, re.IGNORECASE)
    if due_line:
        if due_line.group(1).lower().find("no payment required") >= 0 or due_line.group(2).lower() == "no payment required":
            result["payment_due_date"] = "No payment required"
        else:
            result["payment_due_date"] = extract_date(due_line.group(2))
    else:
        # fallback: if total_amount_due = 0, mark as no payment required
        amt_match = re.search(r'TotalAmountDue.*?([\d,]+\.\d{2})', text, re.IGNORECASE)
        if amt_match and float(amt_match.group(1).replace(",", "")) == 0:
            result["payment_due_date"] = "No payment required"

    # --- TOTAL AMOUNT DUE ---
    total_line = re.search(r'TotalAmountDue.*?([\d,]+\.\d{2})', text, re.IGNORECASE)
    if total_line:
        result["total_amount_due"] = total_line.group(1).replace(",", "")

    # Ensure currency symbol present
    result["currency_symbol"] = result.get("currency_symbol") or detect_currency_symbol(text)

    return result
