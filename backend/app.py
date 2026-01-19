from flask import Flask, request, jsonify
from flask_cors import CORS
import re, time
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize

# ------------------------
# App init (MUST BE FIRST)
# ------------------------
app = Flask(__name__)
CORS(app)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)


# ------------------------
# Health check
# ------------------------
@app.route("/", methods=["GET"])
def root():
    return {"status": "Humanizer backend running"}, 200

# ------------------------
# Utilities
# ------------------------
def clean(text):
    return re.sub(r"\s+", " ", text).strip()

AI_PHRASES = {
    "it is important to note that": "",
    "this clearly demonstrates": "this shows",
    "moreover": "",
    "furthermore": "",
    "in conclusion": "",
}

def remove_ai_signatures(text):
    t = text.lower()
    for k, v in AI_PHRASES.items():
        t = t.replace(k, v)
    return clean(t.capitalize())

def restructure(text):
    sentences = sent_tokenize(text)
    out = []
    for s in sentences:
        w = s.split()
        if len(w) > 22:
            mid = len(w) // 2
            out.append(" ".join(w[:mid]) + ".")
            out.append(" ".join(w[mid:]))
        else:
            out.append(s)
    return clean(" ".join(out))

def rhythm(text):
    sentences = sent_tokenize(text)
    res, buf = [], ""
    for s in sentences:
        if len(s.split()) < 6:
            buf += " " + s
        else:
            if buf:
                res.append(buf.strip())
                buf = ""
            res.append(s)
    if buf:
        res.append(buf.strip())
    return clean(" ".join(res))

def add_reasoning(text):
    s = sent_tokenize(text)
    if len(s) > 1:
        s.insert(1, "This matters because it connects the idea to real-world use.")
    return clean(" ".join(s))

def tone(text, mode):
    styles = {
        "academic": {"very": "", "clearly": "", "significantly": "notably"},
        "simple": {"utilize": "use", "demonstrate": "show"},
        "informal": {"therefore": "so", "however": "but"},
        "formal": {"so": "therefore", "but": "however"},
    }
    for k, v in styles.get(mode, {}).items():
        text = text.replace(k, v)
    return clean(text)

def human_score(text):
    s = sent_tokenize(text)
    w = text.split()
    if not s or not w:
        return 0
    variance = np.std([len(x.split()) for x in s])
    lexical = len(set(w)) / len(w)
    return min(int((variance * 12) + (lexical * 50)), 100)

# ------------------------
# Humanize Pipeline
# ------------------------
def humanize_text(text, mode, ultra):
    steps = [
        remove_ai_signatures,
        restructure,
        rhythm,
        add_reasoning
    ]

    text = clean(text)

    for fn in steps:
        text = fn(text)
        if not ultra and human_score(text) > 65:
            break

    text = tone(text, mode)
    score = human_score(text)
    return text, score

# ------------------------
# API
# ------------------------
@app.route("/humanize", methods=["POST", "OPTIONS"])
def api_humanize():
    if request.method == "OPTIONS":
        return "", 204

    start = time.time()
    data = request.json or {}

    text = data.get("text", "").strip()
    mode = data.get("mode", "standard")
    ultra = data.get("ultra", False)

    if not text:
        return jsonify({"error": "Text required"}), 400

    result, score = humanize_text(text, mode, ultra)
    elapsed = round(time.time() - start, 2)

    return jsonify({
        "result": result,
        "human_style_confidence": score,
        "processing_time": elapsed,
        "mode": mode
    })
