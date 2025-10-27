# Credit Card Statement Parser

Modern, full-stack solution to parse PDF credit card statements and extract 5 key data points using a hybrid text extraction approach (text-first with OCR fallback), plus a sleek React UI for uploads and results.

- Frontend: Vite + React + Tailwind ([credit-card-statement-parser-frontend](credit-card-statement-parser-frontend))
- Backend: Flask API with pdfplumber / PyMuPDF and optional Tesseract OCR ([credit-card-statement-parser-backend](credit-card-statement-parser-backend))

## Problem Statement (Assignment Brief)

Objective:
- Build a PDF parser that extracts 5 key data points from credit card statements across 5 major credit card issuers.

Requirements:
- Support statements from 5 providers (your choice).
- Extract any 5 data points (e.g., transaction info, card variant, card last 4 digits, billing cycle, payment due date, total balance).
- Handle real-world PDF formats.
- Deliverable: Any format that best demonstrates your work. Be ready to demo.
- Evaluation: Functionality, implementation quality, and how effectively you present your solution.

## What This Submission Demonstrates

- Currently implemented issuers: ICICI, Kotak, HDFC
  - ICICI parser: [`parsers.icici_parser.parse_icici`](credit-card-statement-parser-backend/parsers/icici_parser.py)
  - Kotak parser: [`parsers.kotak_parser.parse_kotak`](credit-card-statement-parser-backend/parsers/kotak_parser.py)
  - HDFC parser: [`parsers.hdfc_parser.parse_hdfc`](credit-card-statement-parser-backend/parsers/hdfc_parser.py)
  - Bank routing + detection: [`parsers.router.parse_statement`](credit-card-statement-parser-backend/parsers/router.py)

- Extracted data points (5):
  - bank
  - card_last4
  - statement_date
  - payment_due_date
  - total_amount_due

- Real-world PDF handling:
  - Hybrid text extraction: [`utils.pdf_utils.extract_text`](credit-card-statement-parser-backend/utils/pdf_utils.py)
    - Tries PyMuPDF → pdfplumber; falls back to OCR (Tesseract) when needed.

- Modern Web UI:
  - Upload PDF, see parsed results, download JSON
  - Source: [credit-card-statement-parser-frontend/src/App.tsx](credit-card-statement-parser-frontend/src/App.tsx)

Note: The architecture is designed to scale to 5+ issuers quickly. Adding new issuers is straightforward (see “Extending to 5+ issuers”).

## Repository Structure

- Backend ([credit-card-statement-parser-backend](credit-card-statement-parser-backend))
  - API: [app.py](credit-card-statement-parser-backend/app.py)
  - Parsing:
    - [parsers/icici_parser.py](credit-card-statement-parser-backend/parsers/icici_parser.py)
    - [parsers/kotak_parser.py](credit-card-statement-parser-backend/parsers/kotak_parser.py)
    - Router: [parsers/router.py](credit-card-statement-parser-backend/parsers/router.py)
  - PDF/OCR utilities: [utils/pdf_utils.py](credit-card-statement-parser-backend/utils/pdf_utils.py)
  - Text utils: [utils/text_utils.py](credit-card-statement-parser-backend/utils/text_utils.py)
  - Requirements: [requirements.txt](credit-card-statement-parser-backend/requirements.txt)

- Frontend ([credit-card-statement-parser-frontend](credit-card-statement-parser-frontend))
  - Entry: [index.html](credit-card-statement-parser-frontend/index.html), [src/main.tsx](credit-card-statement-parser-frontend/src/main.tsx)
  - App: [src/App.tsx](credit-card-statement-parser-frontend/src/App.tsx)
  - Styling: [src/index.css](credit-card-statement-parser-frontend/src/index.css), [tailwind.config.js](credit-card-statement-parser-frontend/tailwind.config.js)
  - Config: [vite.config.ts](credit-card-statement-parser-frontend/vite.config.ts), [package.json](credit-card-statement-parser-frontend/package.json)

## Quick Start

Prerequisites:
- Python 3.10+
- Node.js 18+
- Optional (for OCR): Tesseract OCR, Poppler

### 1) Backend

Install dependencies:
- Required:
  - pip install -r [credit-card-statement-parser-backend/requirements.txt](credit-card-statement-parser-backend/requirements.txt)
- Optional (enable OCR fallback):
  - pip install pdf2image pytesseract pillow
  - Install system tools:
    - Tesseract OCR
    - Poppler (for pdf2image)

Environment variables (Windows examples):
- TESSERACT_CMD: Full path to tesseract.exe (e.g., C:\Program Files\Tesseract-OCR\tesseract.exe)
- POPPLER_PATH: Directory of Poppler bin (e.g., C:\poppler\Library\bin)

Run API:
- python [credit-card-statement-parser-backend/app.py](credit-card-statement-parser-backend/app.py)
- Health: GET http://127.0.0.1:5000/health

Endpoints:
- POST /parse (multipart/form-data)
  - file: your PDF
  - Optional query params:
    - mode=auto|text|ocr (default: auto)
    - text_pages=<int> (default: 2) — limit initial text extraction pages
    - ocr_pages=<int> (default: 3) — limit OCR pages for scanned PDFs
    - debug=1 — include extraction metadata in the response

Example:
```bash
curl -F "file=@/path/to/statement.pdf" \
  "http://127.0.0.1:5000/parse?mode=auto&text_pages=2&ocr_pages=3&debug=1"
```

Sample response:
```json
{
  "bank": "ICICI",
  "card_last4": "9270",
  "statement_date": "2024-11-20",
  "payment_due_date": "2024-12-10",
  "total_amount_due": "88375.20"
}
```

### 2) Frontend

Install and run:
- cd credit-card-statement-parser-frontend
- npm install
- npm run dev
- App: http://localhost:5173 (by default)

Configuration:
- The frontend API base can be configured via `VITE_API_BASE_URL` (or adjusted in [src/App.tsx](credit-card-statement-parser-frontend/src/App.tsx)). For local dev, use `http://127.0.0.1:5000`.

## Design Highlights

- Robust PDF extraction:
  - PyMuPDF → pdfplumber → OCR via Tesseract
  - Implementation: [`utils.pdf_utils.extract_text`](credit-card-statement-parser-backend/utils/pdf_utils.py)

- Clean parsing boundary:
  - Bank routing: [`parsers.router.detect_bank`](credit-card-statement-parser-backend/parsers/router.py), [`parsers.router.parse_statement`](credit-card-statement-parser-backend/parsers/router.py)
  - Per-bank parsers isolate issuer-specific logic:
    - [`parsers.icici_parser.parse_icici`](credit-card-statement-parser-backend/parsers/icici_parser.py)
    - [`parsers.kotak_parser.parse_kotak`](credit-card-statement-parser-backend/parsers/kotak_parser.py)

- Modern UI/UX:
  - React + Tailwind, drag-and-drop upload, JSON download
  - Source: [credit-card-statement-parser-frontend/src/App.tsx](credit-card-statement-parser-frontend/src/App.tsx)

## Extending to 5+ Issuers

Add a new bank (e.g., SBI, Axis):
1) Create a parser module: credit-card-statement-parser-backend/parsers/<bank>_parser.py
2) Implement a `parse_<bank>(text: str) -> dict` returning the same keys.
3) Update detection and routing in [parsers/router.py](credit-card-statement-parser-backend/parsers/router.py).

Parser return shape:
```json
{
  "bank": "<BANK>",
  "card_last4": "<dddd>|null",
  "statement_date": "YYYY-MM-DD|null",
  "payment_due_date": "YYYY-MM-DD|No payment required|null",
  "total_amount_due": "<amount string>|null"
}
```

## Known Limitations and Future Work

- Currently implemented banks: ICICI, Kotak, HDFC; extend to SBI, Axis for the full assignment scope.
- OCR dependencies are optional and system-specific; ensure Tesseract/Poppler are installed for image-based PDFs.
- Date/amount formats vary across issuers; parsers can be further hardened with more patterns and robust normalization (see [utils/text_utils.py](credit-card-statement-parser-backend/utils/text_utils.py)).
- No authentication or persistence (stateless API).
- No unit tests included; can add parser-level tests and golden samples.

## Demo Checklist

- Start backend (Flask) and verify /health.
- Start frontend (Vite).
- Upload a statement PDF (ICICI/Kotak).
- Show extracted fields, then download JSON.
- Optionally demonstrate OCR by forcing `?mode=ocr`.

## Scripts

Frontend ([package.json](credit-card-statement-parser-frontend/package.json)):
- npm run dev — Start dev server
- npm run build — Production build
- npm run preview — Preview build
- npm run typecheck — TypeScript type check

Backend:
- python [app.py](credit-card-statement-parser-backend/app.py) — Start API
# Credit Card Statement Parser

Modern, full-stack solution to parse PDF credit card statements and extract 5 key data points using a hybrid text extraction approach (text-first with OCR fallback), plus a sleek React UI for uploads and results.

- Frontend: Vite + React + Tailwind ([credit-card-statement-parser-frontend](credit-card-statement-parser-frontend))
- Backend: Flask API with pdfplumber / PyMuPDF and optional Tesseract OCR ([credit-card-statement-parser-backend](credit-card-statement-parser-backend))

## Problem Statement (Assignment Brief)

Objective:
- Build a PDF parser that extracts 5 key data points from credit card statements across 5 major credit card issuers.

Requirements:
- Support statements from 5 providers (your choice).
- Extract any 5 data points (e.g., transaction info, card variant, card last 4 digits, billing cycle, payment due date, total balance).
- Handle real-world PDF formats.
- Deliverable: Any format that best demonstrates your work. Be ready to demo.
- Evaluation: Functionality, implementation quality, and how effectively you present your solution.

## What This Submission Demonstrates

- Currently implemented issuers: ICICI and Kotak
  - ICICI parser: [`parsers.icici_parser.parse_icici`](credit-card-statement-parser-backend/parsers/icici_parser.py)
  - Kotak parser: [`parsers.kotak_parser.parse_kotak`](credit-card-statement-parser-backend/parsers/kotak_parser.py)
  - Bank routing + detection: [`parsers.router.parse_statement`](credit-card-statement-parser-backend/parsers/router.py)

- Extracted data points (5):
  - bank
  - card_last4
  - statement_date
  - payment_due_date
  - total_amount_due

- Real-world PDF handling:
  - Hybrid text extraction: [`utils.pdf_utils.extract_text`](credit-card-statement-parser-backend/utils/pdf_utils.py)
    - Tries pdfplumber → PyMuPDF; falls back to OCR (Tesseract) when needed.

- Modern Web UI:
  - Upload PDF, see parsed results, download JSON
  - Source: [credit-card-statement-parser-frontend/src/App.tsx](credit-card-statement-parser-frontend/src/App.tsx)

Note: The architecture is designed to scale to 5+ issuers quickly. Adding new issuers is straightforward (see “Extending to 5+ issuers”).

## Repository Structure

- Backend ([credit-card-statement-parser-backend](credit-card-statement-parser-backend))
  - API: [app.py](credit-card-statement-parser-backend/app.py)
  - Parsing:
    - [parsers/icici_parser.py](credit-card-statement-parser-backend/parsers/icici_parser.py)
    - [parsers/kotak_parser.py](credit-card-statement-parser-backend/parsers/kotak_parser.py)
    - Router: [parsers/router.py](credit-card-statement-parser-backend/parsers/router.py)
  - PDF/OCR utilities: [utils/pdf_utils.py](credit-card-statement-parser-backend/utils/pdf_utils.py)
  - Text utils: [utils/text_utils.py](credit-card-statement-parser-backend/utils/text_utils.py)
  - Requirements: [requirements.txt](credit-card-statement-parser-backend/requirements.txt)

- Frontend ([credit-card-statement-parser-frontend](credit-card-statement-parser-frontend))
  - Entry: [index.html](credit-card-statement-parser-frontend/index.html), [src/main.tsx](credit-card-statement-parser-frontend/src/main.tsx)
  - App: [src/App.tsx](credit-card-statement-parser-frontend/src/App.tsx)
  - Styling: [src/index.css](credit-card-statement-parser-frontend/src/index.css), [tailwind.config.js](credit-card-statement-parser-frontend/tailwind.config.js)
  - Config: [vite.config.ts](credit-card-statement-parser-frontend/vite.config.ts), [package.json](credit-card-statement-parser-frontend/package.json)

## Quick Start

Prerequisites:
- Python 3.10+
- Node.js 18+
- Optional (for OCR): Tesseract OCR, Poppler

### 1) Backend

Install dependencies:
- Required:
  - pip install -r [credit-card-statement-parser-backend/requirements.txt](credit-card-statement-parser-backend/requirements.txt)
- Optional (enable OCR fallback):
  - pip install pdf2image pytesseract pillow
  - Install system tools:
    - Tesseract OCR
    - Poppler (for pdf2image)

Environment variables (Windows examples):
- TESSERACT_CMD: Full path to tesseract.exe (e.g., C:\Program Files\Tesseract-OCR\tesseract.exe)
- POPPLER_PATH: Directory of Poppler bin (e.g., C:\poppler\Library\bin)

Run API:
- python [credit-card-statement-parser-backend/app.py](credit-card-statement-parser-backend/app.py)
- Health: GET http://127.0.0.1:5000/health

Endpoints:
- POST /parse (multipart/form-data)
  - file: your PDF
  - Optional query params:
    - mode=auto|text|ocr (default: auto)
    - ocr_pages=<int> (default: 10)

Example:
```bash
curl -F "file=@/path/to/statement.pdf" "http://127.0.0.1:5000/parse?mode=auto&ocr_pages=8"
```

Sample response:
```json
{
  "bank": "ICICI",
  "card_last4": "9270",
  "statement_date": "2024-11-20",
  "payment_due_date": "2024-12-10",
  "total_amount_due": "88375.20"
}
```

### 2) Frontend

Install and run:
- cd credit-card-statement-parser-frontend
- npm install
- npm run dev
- App: http://localhost:5173 (by default)

Configuration:
- The frontend calls the backend at API_BASE_URL = http://127.0.0.1:5000 inside [src/App.tsx](credit-card-statement-parser-frontend/src/App.tsx). Adjust if your backend runs elsewhere.

## Design Highlights

- Robust PDF extraction:
  - pdfplumber → PyMuPDF → OCR via Tesseract
  - Implementation: [`utils.pdf_utils.extract_text`](credit-card-statement-parser-backend/utils/pdf_utils.py)

- Clean parsing boundary:
  - Bank routing: [`parsers.router.detect_bank`](credit-card-statement-parser-backend/parsers/router.py), [`parsers.router.parse_statement`](credit-card-statement-parser-backend/parsers/router.py)
  - Per-bank parsers isolate issuer-specific logic:
    - [`parsers.icici_parser.parse_icici`](credit-card-statement-parser-backend/parsers/icici_parser.py)
    - [`parsers.kotak_parser.parse_kotak`](credit-card-statement-parser-backend/parsers/kotak_parser.py)

- Modern UI/UX:
  - React + Tailwind, drag-and-drop upload, JSON download
  - Source: [credit-card-statement-parser-frontend/src/App.tsx](credit-card-statement-parser-frontend/src/App.tsx)

## Extending to 5+ Issuers

Add a new bank (e.g., HDFC, SBI, Axis):
1) Create a parser module: credit-card-statement-parser-backend/parsers/<bank>_parser.py
2) Implement a `parse_<bank>(text: str) -> dict` returning the same keys.
3) Update detection and routing in [parsers/router.py](credit-card-statement-parser-backend/parsers/router.py).

Parser return shape:
```json
{
  "bank": "<BANK>",
  "card_last4": "<dddd>|null",
  "statement_date": "YYYY-MM-DD|null",
  "payment_due_date": "YYYY-MM-DD|No payment required|null",
  "total_amount_due": "<amount string>|null"
}
```

## Known Limitations and Future Work

- Currently implemented banks: ICICI, Kotak; extend to HDFC, SBI, Axis for the full assignment scope.
- OCR dependencies are optional and system-specific; ensure Tesseract/Poppler are installed for image-based PDFs.
- Date/amount formats vary across issuers; parsers can be further hardened with more patterns and robust normalization (see [utils/text_utils.py](credit-card-statement-parser-backend/utils/text_utils.py)).
- No authentication or persistence (stateless API).
- No unit tests included; can add parser-level tests and golden samples.

## Demo Checklist

- Start backend (Flask) and verify /health.
- Start frontend (Vite).
- Upload a statement PDF (ICICI/Kotak).
- Show extracted fields, then download JSON.
- Optionally demonstrate OCR by forcing `?mode=ocr`.

## Scripts

Frontend ([package.json](credit-card-statement-parser-frontend/package.json)):
- npm run dev — Start dev server
- npm run build — Production build
- npm run preview — Preview build
- npm run typecheck — TypeScript type check

Backend:
- python [app.py](credit-card-statement-parser-backend/app.py) — Start API

---