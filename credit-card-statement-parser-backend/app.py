import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.pdf_utils import extract_text
from parsers.router import parse_statement

app = Flask(__name__)

# Explicit CORS whitelist for frontend origins (prod + local dev + any Vercel previews)
ALLOWED_ORIGINS = [
    "https://credit-card-statement-parser-lhv3yifns-purva0017s-projects.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    re.compile(r"^https://.*\.vercel\.app$"),
]
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})

@app.route("/health", methods=["GET", "OPTIONS"])
def health():
    if request.method == "OPTIONS":
        return ("", 204)
    return jsonify({"status": "ok"})

# Main parsing endpoint
@app.route("/parse", methods=["POST", "OPTIONS"])
def parse_post():
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return ("", 204)
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    f = request.files["file"]
    file_bytes = f.read()
    if not file_bytes:
        return jsonify({"error": "Empty file"}), 400

    # Hidden overrides (not exposed in UI)
    mode = (request.args.get("mode") or "auto").lower()  # auto | ocr | text
    if mode not in ("auto", "ocr", "text"):
        mode = "auto"
    # Page limits (tunable via query params)
    try:
        text_pages = int(request.args.get("text_pages", "2"))
    except ValueError:
        text_pages = 2
    try:
        ocr_pages = int(request.args.get("ocr_pages", "3"))
    except ValueError:
        ocr_pages = 3

    # Clamp sensible minimums
    text_pages = max(1, text_pages)
    ocr_pages = max(1, ocr_pages)

    force_ocr = mode == "ocr"
    auto_ocr = mode == "auto"

    text = extract_text(
        file_bytes,
        force_ocr=force_ocr,
        auto_ocr=auto_ocr,
        ocr_max_pages=ocr_pages,
        text_max_pages=text_pages,
    )

    if not text.strip():
        return jsonify({"error": "Unable to extract text from PDF"}), 422

    result = parse_statement(text)

    # for debugging
    if request.args.get("debug") == "1":
        result["__debug"] = {
            "raw_preview": text,
            "raw_length": len(text),
            "requested_mode": mode,
            "extraction_method": getattr(extract_text, "last_method", None),
            "ocr_pages": ocr_pages,
            "text_pages": text_pages,
        }

    return jsonify(result)

if __name__ == "__main__":
    # Bind to 0.0.0.0 and use PORT env (required by many hosting providers like Render)
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)