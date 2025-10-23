from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.pdf_utils import extract_text
from parsers.router import parse_statement

app = Flask(__name__)
CORS(app)

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

# Main parsing endpoint
@app.post("/parse")
def parse_post():
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
    try:
        ocr_pages = int(request.args.get("ocr_pages", "10"))
    except ValueError:
        ocr_pages = 10

    force_ocr = mode == "ocr"
    auto_ocr = mode == "auto"

    text = extract_text(
        file_bytes,
        force_ocr=force_ocr,
        auto_ocr=auto_ocr,
        ocr_max_pages=ocr_pages,
    )

    if not text.strip():
        return jsonify({"error": "Unable to extract text from PDF"}), 422

    result = parse_statement(text)

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)