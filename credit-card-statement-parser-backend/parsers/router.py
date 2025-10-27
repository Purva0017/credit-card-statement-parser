import re
from parsers.icici_parser import parse_icici
from parsers.kotak_parser import parse_kotak
from parsers.generic_parser import parse_generic
from utils.text_utils import detect_currency_symbol

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
        res = parse_icici(text)
        if not res.get("currency_symbol"):
            res["currency_symbol"] = detect_currency_symbol(text)
        return res
    elif bank == "KOTAK":
        res = parse_kotak(text)
        if not res.get("currency_symbol"):
            res["currency_symbol"] = detect_currency_symbol(text)
        return res
    else:
        # Use generic parser for HDFC and all other banks
        res = parse_generic(text, bank=bank)
        if not res.get("currency_symbol"):
            res["currency_symbol"] = detect_currency_symbol(text)
        return res
