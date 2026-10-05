# -*- coding: utf-8 -*-
"""
TechEngage: Reading Time & Readability Calculator.

A small Flask tool. Paste an article, get word count, character count,
estimated reading time, a Flesch Reading Ease score with a plain-English
explanation, and the 3 longest sentences highlighted.

Fully stateless: the article text travels in the form between requests, so it
runs on serverless platforms (Vercel) as well as normal servers.

Run locally:
    pip install -r requirements.txt
    python app.py
"""
import os
import re
from flask import Flask, request, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB cap

WORDS_PER_MINUTE = 200

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
WORD_RE = re.compile(r"[A-Za-z0-9']+")
VOWEL_GROUP_RE = re.compile(r"[aeiouy]+")


# ---------------------------------------------------------------------------
# Text analysis
# ---------------------------------------------------------------------------
def split_sentences(text):
    """Split text into sentences on . ! ? followed by whitespace."""
    parts = SENTENCE_SPLIT_RE.split(text.strip())
    return [p.strip() for p in parts if p.strip()]


def count_syllables(word):
    """Heuristic syllable count: vowel groups, minus silent trailing e."""
    word = word.lower().strip("'")
    if not word:
        return 0
    groups = VOWEL_GROUP_RE.findall(word)
    count = len(groups)
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def flesch_reading_ease(words, sentences, syllables):
    """Flesch Reading Ease: 0 (very hard) to 100 (very easy)."""
    if not sentences or not words:
        return 0.0
    wps = words / sentences
    spw = syllables / words
    return 206.835 - 1.015 * wps - 84.6 * spw


def flesch_explanation(score):
    """Plain-English explanation of a Flesch score."""
    if score >= 90:
        return ("Very easy to read. A 5th grader could understand it. "
                "Short sentences, simple words.")
    if score >= 80:
        return ("Easy to read. Conversational style, like a friendly blog post.")
    if score >= 70:
        return ("Fairly easy to read. Comfortable for most adult readers.")
    if score >= 60:
        return ("Standard readability. Typical for news articles and magazines.")
    if score >= 50:
        return ("Fairly difficult. Best suited for high-school graduates.")
    if score >= 30:
        return ("Difficult. Academic or technical writing; needs focus.")
    return ("Very difficult. Dense, complex text for specialist readers.")


def analyze(text):
    """Analyze article text. Returns a dict of stats."""
    text = text.strip()
    words_list = WORD_RE.findall(text)
    word_count = len(words_list)
    char_count = len(text)
    char_no_spaces = len(re.sub(r"\s", "", text))

    sentences = split_sentences(text)
    sentence_count = len(sentences)

    syllables = sum(count_syllables(w) for w in words_list)

    minutes = word_count / WORDS_PER_MINUTE
    read_min = int(minutes)
    read_sec = int(round((minutes - read_min) * 60))
    if read_sec == 60:
        read_min += 1
        read_sec = 0

    score = flesch_reading_ease(word_count, sentence_count, syllables)

    # 3 longest sentences by word count (stable: keep original order on ties)
    ranked = sorted(
        ((len(WORD_RE.findall(s)), i, s) for i, s in enumerate(sentences)),
        key=lambda t: (-t[0], t[1]),
    )
    longest = [{"text": s, "words": n} for n, _, s in ranked[:3]]

    return {
        "word_count": word_count,
        "char_count": char_count,
        "char_no_spaces": char_no_spaces,
        "sentence_count": sentence_count,
        "reading_minutes": read_min,
        "reading_seconds": read_sec,
        "flesch": round(score, 1),
        "flesch_explanation": flesch_explanation(score),
        "longest_sentences": longest,
        "sentences": sentences,
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze_route():
    text = request.form.get("article", "")
    if not text.strip():
        return render_template("index.html",
                               error="Please paste some article text first."), 400
    stats = analyze(text)
    return render_template("result.html", stats=stats, article=text)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
