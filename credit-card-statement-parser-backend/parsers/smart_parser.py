# import re
# from rapidfuzz import fuzz

# # ---------- Helper Functions ----------

# def find_line_by_keywords(text_lines, keywords, threshold=80):
#     """Find the line most likely containing any of the given keywords."""
#     for line in text_lines:
#         lower_line = line.lower()
#         for kw in keywords:
#             if fuzz.partial_ratio(kw, lower_line) > threshold:
#                 return line
#     return None


# def extract_date(line):
#     """Extract date in multiple formats (e.g., 15-Oct-2025, 15/10/25, 15.10.2025, October 15, 2025)."""
#     if not line:
#         return None

#     # Common date formats seen in statements
#     patterns = [
#         r"\b\d{1,2}[-/\s\.][A-Za-z]{3,9}[-/\s\.]\d{2,4}\b",  # 15-Oct-2025 or 15 October 2025
#         r"\b[A-Za-z]{3,9}[-/\s\.]\d{1,2}[-/\s\.]\d{2,4}\b",  # October-15-2025
#         r"\b\d{1,2}[-/\.\s]\d{1,2}[-/\.\s]\d{2,4}\b",        # 15/10/2025 or 15.10.25
#     ]

#     for pattern in patterns:
#         match = re.search(pattern, line, re.IGNORECASE)
#         if match:
#             return match.group(0).strip()

#     return None



# def extract_amount(line):
#     """Extract rupee or dollar amounts."""
#     match = re.search(r"₹?\s?[\d,]+\.?\d{0,2}", line)
#     return match.group(0).strip() if match else None


# # ---------- Card last-4 extraction ----------
# def extract_last4(text):
#     """Extract the card last 4 digits in a robust way.

#     Strategy:
#     1) Search for lines/segments that contain card-related keywords and masked numbers.
#     2) Prefer matches that contain X/x masking or long digit clusters (12-19 digits) to avoid dates/years.
#     3) If a candidate found, return the last 4 digits from that candidate.
#     4) As a last-ditch fallback, return None (to avoid returning a year like 2024).
#     """
#     if not text:
#         return None

#     text_lines = [l.strip() for l in text.splitlines() if l.strip()]

#     # 1) Try contextual patterns near card-related keywords
#     card_kw_patterns = [
#         r"(primarycardnumber|primary card number|primary card|card number|card no|primarycardtransactions|primarycard)\s*[:\s\-]*([0-9Xx\s\-]{8,30})",
#         r"(maskedcardnumber|cardmasked)\s*[:\s\-]*([0-9Xx\s\-]{8,30})",
#         r"(primarycardtransactions)\s*[-:\s]*([0-9Xx\s\-]{8,30})"
#     ]

#     joined_text = "\n".join(text_lines)  # preserve contiguous content for regex
#     for pat in card_kw_patterns:
#         m = re.search(pat, joined_text, flags=re.IGNORECASE)
#         if m:
#             candidate = m.group(2)
#             digits = re.findall(r"\d", candidate)
#             if len(digits) >= 4:
#                 return "".join(digits[-4:])

#     # 2) Look for masked patterns like 4147XXXXXXXX9270 or 4147XXXX9270 etc.
#     masked_patterns = [
#         r"\b\d{4}X{4,}\d{4}\b",      # 4147XXXXXXXX9270
#         r"\b\d{6,}\d{4}\b",         # long digit sequence ending with 4 digits (12+ digits)
#         r"\bX{4,}\d{4}\b",          # XXXXXXXXXXXX1234
#         r"\b\d{4}[-\s]X{4,}[-\s]?\d{4}\b"
#     ]
#     for pat in masked_patterns:
#         m = re.search(pat, joined_text, flags=re.IGNORECASE)
#         if m:
#             digits = re.findall(r"\d", m.group(0))
#             if len(digits) >= 4:
#                 return "".join(digits[-4:])

#     # 3) If nothing matched yet, try to find any 12-19 digit clusters (likely full PAN)
#     m = re.search(r"\b(?:\d[ -]?){12,19}\b", joined_text)
#     if m:
#         digits = re.findall(r"\d", m.group(0))
#         if len(digits) >= 4:
#             return "".join(digits[-4:])

#     # 4) Do NOT return any 4-digit standalone match (like years or dates).
#     #    Safer to return None so caller can handle the missing value explicitly.
#     return None


# # ---------- Bank Detection ----------
# BANK_PATTERNS = {
#     "Kotak": [r"\bkotak\b", r"\bkotak mahindra\b", r"\bkotak\.com\b"],
#     "HDFC": [r"\bhdfc\b", r"\bhdfcbank\b"],
#     "SBI": [r"\bsbi\b", r"\bsbi card\b"],
#     "ICICI": [r"\bicici\b", r"\bicici bank\b"],
#     "Axis": [r"\baxis\b", r"\baxis bank\b"],
#     "American Express": [r"\bamerican express\b", r"\bamex\b"],
#     "Commonwealth": [r"\bcommonwealth\b"],
#     "Chase": [r"\bchase\b"]
# }

# def detect_bank(text, fuzzy_threshold=75):
#     """Detect bank using exact regex matches first, then fallback to fuzzy scoring."""
#     if not text:
#         return None

#     text_lower = text.lower()

#     # 1) Exact regex search per bank (preferred)
#     for bank_name, patterns in BANK_PATTERNS.items():
#         for pat in patterns:
#             if re.search(pat, text_lower):
#                 return bank_name

#     # 2) Fallback: compute fuzzy score across bank names (use whole text vs bank name)
#     #    but only accept if best score is confidently high
#     best = ("Unknown", 0)
#     for bank_name in BANK_PATTERNS.keys():
#         score = fuzz.partial_ratio(bank_name.lower(), text_lower)
#         if score > best[1]:
#             best = (bank_name, score)

#     if best[1] >= fuzzy_threshold:
#         return best[0]

#     return "Unknown"


# # ---------- Main Smart Parser ----------

# def parse_statement_text(text):
#     lines = [l.strip() for l in text.splitlines() if l.strip()]

#     # --- Field 1: Payment Due Date ---
#     due_line = find_line_by_keywords(lines, ["payment due date", "due on", "pay by"])
#     due_date = None

#     # 1. Check if text mentions "no payment required" anywhere
#     if re.search(r"no\s*payment\s*required", text, re.IGNORECASE):
#         due_date = "No payment required"

#     # 2. Else extract date normally
#     elif due_line:
#         due_date = extract_date(due_line)

#     # 3. If still none and total amount due is 0 → treat as no payment required
#     elif total_due and re.search(r"^₹?\s?0+(\.0+)?$", total_due.strip(), re.IGNORECASE):
#         due_date = "No payment required"


#     # --- Field 2: Statement Date ---
#     statement_line = find_line_by_keywords(lines, ["statement date", "billing date", "statement generated on", "date of issue"])
#     statement_date = extract_date(statement_line) if statement_line else None


#     # --- Field 3: Total Amount Due ---
#     total_line = find_line_by_keywords(lines, ["total amount due", "total due", "amount payable"])
#     total_due = extract_amount(total_line) if total_line else None

#     # --- Field 4: Card Last 4 digits ---
#     card_last4 = extract_last4(text)
    

#     # --- Field 5: Bank Detection ---
#     bank = detect_bank(text)


#     return {
#         "bank": bank or "Unknown",
#         "statement_date": statement_date,
#         "card_last4": card_last4,
#         "payment_due_date": due_date,
#         "total_amount_due": total_due,
#     }
