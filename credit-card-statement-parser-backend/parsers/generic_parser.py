import re
from datetime import datetime
from typing import Optional, List

from utils.text_utils import normalize_text, detect_currency_symbol


# Reusable tokens
DATE_TOKEN = (
    r"(?:"
    r"\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}"  # 01/09/2025 or 01-09-2025 or 01.09.2025
    r"|\d{4}-\d{2}-\d{2}"                 # 2025-09-01
    r"|[A-Za-z]{3,9}\s\d{1,2},\s\d{4}"   # September 1, 2025
    r"|\d{1,2}\s[A-Za-z]{3,9}\s\d{4}"   # 1 September 2025
    r")"
)

# Amount token: require either a decimal part or grouped commas with decimals
# This avoids accidentally capturing integers like the day from a date (e.g., 21 from 21/09/2025)
AMOUNT_TOKEN = r"(?:₹|`|\$)?\s*([0-9]{1,3}(?:,[0-9]{2,3})+(?:\.\d{2})|[0-9]+(?:\.\d{2}))"


def _try_parse_date(raw: str) -> Optional[str]:
    raw = raw.strip()
    # Common formats to try
    formats = [
        "%d-%b-%Y",  # 20-Nov-2024
        "%d-%m-%Y",  # 20-11-2024
        "%d/%m/%Y",  # 20/11/2024
        "%Y-%m-%d",  # 2024-11-20
        "%B %d, %Y", # November 20, 2024
        "%d %B %Y",  # 20 November 2024
        "%d.%m.%Y",  # 20.11.2024
    ]
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    # If we can't normalize, return the original snippet
    return raw if raw else None


def _find_date_near_label(text: str, labels: List[str]) -> Optional[str]:
    for label in labels:
        # Allow up to ~120 chars (including newlines) after the label to find a date token
        m = re.search(
            rf"{label}.{{0,120}}?({DATE_TOKEN})",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if m:
            return _try_parse_date(m.group(1))

        # Line/window-based fallback: take a 150-char window after the label and scan for a date
        pos = re.search(label, text, flags=re.IGNORECASE)
        if pos:
            start = pos.end()
            window = text[start : start + 150]
            m2 = re.search(DATE_TOKEN, window, flags=re.IGNORECASE)
            if m2:
                return _try_parse_date(m2.group(0))
    return None


def _find_amounts_in_window(window: str) -> List[str]:
    return [m.replace(",", "") for m in re.findall(AMOUNT_TOKEN, window)]


def _find_amount_near_label(text: str, labels: List[str]) -> Optional[str]:
    # Prefer amounts appearing within a short window after the label
    for label in labels:
        for match in re.finditer(label, text, flags=re.IGNORECASE):
            start = match.end()
            window = text[start : start + 200]
            amts = _find_amounts_in_window(window)
            if amts:
                return amts[0]

    # HDFC-specific fallback: the row following "Payment Due Date" often has: date total_dues min_due
    tbl = re.search(r"Payment\s*Due\s*Date[^\n]*\n([^\n]+)", text, flags=re.IGNORECASE)
    if tbl:
        row = tbl.group(1)
        amts = _find_amounts_in_window(row)
        if len(amts) >= 1:
            return amts[0]

    # Generic fallback: first decent-looking amount in doc
    m2 = re.search(AMOUNT_TOKEN, text)
    if m2:
        return m2.group(1).replace(",", "")
    return None


def _find_card_last4(text: str) -> Optional[str]:
    # Patterns: XXXX1234, **** 1234, xxxxxx 1234, Card ending 1234
    patterns = [
        r"X{4,}\s*(\d{4})",
        r"\*{4,}\s*(\d{4})",
        r"x{4,}\s*(\d{4})",
        r"ending\s*(\d{4})",
        r"last\s*4\s*digits\s*[:\-]?\s*(\d{4})",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return None


def parse_generic(text: str, bank: str = "UNKNOWN") -> dict:
    # Normalize common artifacts for better matching
    ntext = normalize_text(text)

    result = {
        "bank": bank,
        "card_last4": None,
        "statement_date": None,
        "payment_due_date": None,
        "total_amount_due": None,
        "currency_symbol": detect_currency_symbol(ntext),
    }

    # Card last 4
    result["card_last4"] = _find_card_last4(ntext)

    # Statement date
    result["statement_date"] = _find_date_near_label(
        ntext,
        labels=[
            r"statement\s*date",
            r"statement\s*generated\s*on",
            r"billing\s*date",
        ],
    )

    # Payment due date
    due = _find_date_near_label(
        ntext,
        labels=[
            r"payment\s*due\s*date",
            r"due\s*date",
            r"payment\s*by",
        ],
    )
    # Handle "No payment required" style cues
    if not due and re.search(r"no\s*payment\s*required", ntext, re.IGNORECASE):
        due = "No payment required"
    result["payment_due_date"] = due

    # Total amount due
    result["total_amount_due"] = _find_amount_near_label(
        ntext,
        labels=[
            r"total\s*dues",
            r"total\s*amount\s*due",
            r"total\s*amount\s*payable",
            r"amount\s*due",
            r"total\s*due",
        ],
    )

    return result
