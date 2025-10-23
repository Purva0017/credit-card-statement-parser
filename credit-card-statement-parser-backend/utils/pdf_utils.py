import io
import os
from typing import Optional

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


def extract_text(
    file_bytes: bytes,
    *,
    force_ocr: bool = False,
    auto_ocr: bool = True,
    ocr_max_pages: int = 10,
    text_max_pages: Optional[int] = None,
) -> str:
    """
    Hybrid extraction:
    - Try text extraction (PyMuPDF → pdfplumber).
    - If empty or force_ocr, run OCR via Tesseract.
    """
    method = "none"
    text = ""

    if not force_ocr:
        text = _extract_via_pymupdf(file_bytes, max_pages=text_max_pages)
        if text.strip():
            method = "text-pymupdf"
        else:
            text = _extract_via_pdfplumber(file_bytes, max_pages=text_max_pages)
            if text.strip():
                method = "text-pdfplumber"

    if method == "none" and (force_ocr or auto_ocr):
        text = _extract_via_ocr(file_bytes, max_pages=ocr_max_pages)
        if text.strip():
            method = "ocr-tesseract"

    try:
        extract_text.last_method = method
    except Exception:
        pass

    return text or ""

def _extract_via_pdfplumber(file_bytes: bytes, max_pages: Optional[int] = None) -> str:
    if not pdfplumber:
        return ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = pdf.pages
            limit = len(pages) if max_pages is None else min(len(pages), max_pages)
            return "".join((pages[i].extract_text() or "") for i in range(limit))
    except Exception:
        return ""


def _extract_via_pymupdf(file_bytes: bytes, max_pages: Optional[int] = None) -> str:
    if not fitz:
        return ""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        page_count = doc.page_count
        limit = page_count if max_pages is None else min(page_count, max_pages)
        text = "".join(doc.load_page(i).get_text("text") or "" for i in range(limit))
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
        kwargs = {"dpi": 300, "fmt": "png", "first_page": 1, "last_page": max_pages}
        if poppler_path:
            images = convert_from_bytes(file_bytes, poppler_path=poppler_path, **kwargs)
        else:
            images = convert_from_bytes(file_bytes, **kwargs)
    except Exception:
        return ""

    parts = []
    for i, img in enumerate(images):
        try:
            txt = pytesseract.image_to_string(img, lang=os.environ.get("TESSERACT_LANG", "eng"))
        except Exception:
            txt = ""
        parts.append(txt or "")
    return "\n".join(parts)