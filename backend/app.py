from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import numpy as np
from nltk.tokenize import sent_tokenize
import nltk

# Ensure tokenizer
nltk.download("punkt", quiet=True)

@app.route("/humanize", methods=["POST", "OPTIONS"])

def health():
    return {"status": "Humanizer backend running"}, 200

app = Flask(__name__)
CORS(app)

# --------------------------------------------------
# Utilities
# --------------------------------------------------

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

# --------------------------------------------------
# Core Human Editing Passes
# --------------------------------------------------

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

def restructure_sentences(text):
    sentences = sent_tokenize(text)
    output = []
    for s in sentences:
        words = s.split()
        if len(words) > 24:
            mid = len(words) // 2
            output.append(" ".join(words[:mid]) + ".")
            output.append(" ".join(words[mid:]))
        else:
            output.append(s)
    return clean(" ".join(output))

def rhythm_adjustment(text):
    sentences = sent_tokenize(text)
    result, buffer = [], ""
    for s in sentences:
        if len(s.split()) < 6:
            buffer += " " + s
        else:
            if buffer:
                result.append(buffer.strip())
                buffer = ""
            result.append(s)
    if buffer:
        result.append(buffer.strip())
    return clean(" ".join(result))

def add_light_reasoning(text):
    sentences = sent_tokenize(text)
    if len(sentences) > 1:
        sentences.insert(
            1,
            "This matters because it helps explain the practical relevance of the idea."
        )
    return clean(" ".join(sentences))

def tone_smoothing(text, mode):
    replacements = {
        "academic": {"very": "", "clearly": "", "significantly": "notably"},
        "simple": {"utilize": "use", "demonstrate": "show"},
        "informal": {"therefore": "so", "however": "but"},
        "formal": {"so": "therefore", "but": "however"},
        "flowing": {},
        "standard": {},
        "free": {},
    }
    for k, v in replacements.get(mode, {}).items():
        text = text.replace(k, v)
    return clean(text)

# --------------------------------------------------
# Human-Style Quality Heuristic (Internal)
# --------------------------------------------------

def human_style_score(text):
    sentences = sent_tokenize(text)
    words = text.split()
    if not sentences or not words:
        return 0
    variance = np.std([len(s.split()) for s in sentences])
    lexical = len(set(words)) / len(words)
    score = min((variance * 12) + (lexical * 50), 100)
    return int(score)

# --------------------------------------------------
# Human Editing Pipeline
# --------------------------------------------------

def humanize(text, mode="standard", ultra=False):
    passes = [
        remove_ai_signatures,
        restructure_sentences,
        rhythm_adjustment,
        add_light_reasoning,
    ]

    text = clean(text)

    for fn in passes:
        text = fn(text)
        if not ultra and human_style_score(text) > 65:
            break

    text = tone_smoothing(text, mode)
    score = human_style_score(text)

    return text, score

# --------------------------------------------------
# API
# --------------------------------------------------

@app.route("/humanize", methods=["POST"])
def api_humanize():
    data = request.json or {}
    text = data.get("text", "").strip()
    mode = data.get("mode", "standard")
    ultra = data.get("ultra", False)

    if not text:
        return jsonify({"error": "Text is required"}), 400

    result, score = humanize(text, mode, ultra)

    return jsonify({
        "result": result,
        "human_style_confidence": score,
        "mode": mode
    })

if __name__ == "__main__":
    print("🚀 Humanizer backend running (production logic)")
app.run(host="0.0.0.0", port=5000)

