from flask import Flask, request, jsonify
from flask_cors import CORS

# --------------------
# App initialization (MUST BE FIRST)
# --------------------
app = Flask(__name__)
CORS(app)

# --------------------
# Health check
# --------------------
@app.route("/", methods=["GET"])
def root():
    return {"status": "Humanizer backend running"}, 200

# --------------------
# Test API endpoint
# --------------------
@app.route("/humanize", methods=["POST", "OPTIONS"])
def humanize():
    if request.method == "OPTIONS":
        return "", 204

    data = request.json or {}
    text = data.get("text", "")

    return jsonify({
        "result": text,
        "human_style_confidence": 50
    })
