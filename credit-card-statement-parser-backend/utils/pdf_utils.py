import io
import os

try:
    import pdfplumber
except Exception:
    pdfplumber = None

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

try:
    from pdf2image import convert_from_bytes
except Exception:
    convert_from_bytes = None

try:
    import pytesseract
except Exception:
    pytesseract = None


def extract_text(file_bytes: bytes, force_ocr: bool = False, auto_ocr: bool = True, ocr_max_pages: int = 10) -> str:
    """
    Hybrid extraction:
    - Try text extraction (pdfplumber → PyMuPDF).
    - If empty or force_ocr, run OCR via Tesseract.
    """
    method = "none"
    text = ""

    if not force_ocr:
        text = _extract_via_pdfplumber(file_bytes)
        if text.strip():
            method = "text-pdfplumber"
        else:
            text = _extract_via_pymupdf(file_bytes)
            if text.strip():
                method = "text-pymupdf"

    if method == "none" and (force_ocr or auto_ocr):
        text = _extract_via_ocr(file_bytes, max_pages=ocr_max_pages)
        if text.strip():
            method = "ocr-tesseract"

    try:
        extract_text.last_method = method
    except Exception:
        pass

    return text or ""

def _extract_via_pdfplumber(file_bytes: bytes) -> str:
    if not pdfplumber:
        return ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            return "".join((p.extract_text() or "") for p in pdf.pages)
    except Exception:
        return ""


def _extract_via_pymupdf(file_bytes: bytes) -> str:
    if not fitz:
        return ""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "".join(p.get_text("text") or "" for p in doc)
        doc.close()
        return text
    except Exception:
        return ""


def _ensure_tesseract_path():
    # On Windows, set env var TESSERACT_CMD to the full path if not on PATH.
    if pytesseract:
        cmd = os.environ.get("TESSERACT_CMD")
        if cmd:
            pytesseract.pytesseract.tesseract_cmd = cmd


def _extract_via_ocr(file_bytes: bytes, max_pages: int = 10) -> str:
    if not (convert_from_bytes and pytesseract):
        return ""
    _ensure_tesseract_path()
    poppler_path = os.environ.get("POPPLER_PATH")  # Needed on Windows if poppler isn't on PATH

    try:
        if poppler_path:
            images = convert_from_bytes(file_bytes, dpi=300, fmt="png", poppler_path=poppler_path)
        else:
            images = convert_from_bytes(file_bytes, dpi=300, fmt="png")
    except Exception:
        return ""

    parts = []
    for i, img in enumerate(images):
        if i >= max_pages:
            break
        try:
            txt = pytesseract.image_to_string(img, lang=os.environ.get("TESSERACT_LANG", "eng"))
        except Exception:
            txt = ""
        parts.append(txt or "")
    return "\n".join(parts)