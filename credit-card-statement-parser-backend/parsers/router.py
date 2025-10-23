import re
from parsers.icici_parser import parse_icici
from parsers.kotak_parser import parse_kotak
from parsers.hdfc_parser import parse_hdfc

def detect_bank(text: str) -> str:
    text_lower = text.lower()
    if "icici bank" in text_lower:
        return "ICICI"
    elif "kotak" in text_lower:
        return "KOTAK"
    elif "hdfc" in text_lower:
        return "HDFC"
    else:
        return "UNKNOWN"

def parse_statement(text: str):
    bank = detect_bank(text)
    if bank == "ICICI":
        return parse_icici(text)
    elif bank == "KOTAK":
        return parse_kotak(text)
    elif bank == "HDFC":
        return parse_hdfc(text)
    else:
        return {
            "bank": bank,
            "card_last4": None,
            "statement_date": None,
            "payment_due_date": None,
            "total_amount_due": None
        }
