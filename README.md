# TechEngage: Reading Time & Readability Calculator

A small Python (Flask) tool. Paste an article, get word count, character
count, estimated reading time, a Flesch Reading Ease score with a
plain-English explanation, and the 3 longest sentences highlighted.

## What it does

- Word count, character count (with and without spaces), sentence count.
- Estimated reading time at 200 words per minute.
- Flesch Reading Ease score (0 = very hard, 100 = very easy) with a simple
  explanation of what the score means.
- The 3 longest sentences highlighted in the results.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Open http://127.0.0.1:5000 and paste any article.

## How it was tested

16 automated tests in `tests/test_app.py`, run with:

```bash
pytest -v
```

Coverage: sentence splitting, syllable counting (including silent-e words),
Flesch scoring on easy vs hard text, explanation bands, word/character
counts, reading-time math (exact and partial minutes), longest-sentence
ranking and highlighting, fewer-than-three-sentences edge case, page loads,
form submit, and empty-submit rejection.

Manual test: ran the server, pasted a sample article, verified counts,
reading time, score, and highlighted sentences in the browser.

## Limitations

- Syllable counting is heuristic (vowel groups minus silent e); it is close
  but not perfect for every English word.
- Sentence splitting is punctuation-based; abbreviations like "Dr." split
  early.
- Reading speed is fixed at 200 wpm; real speeds vary by reader and text.
- Flesch Reading Ease is designed for English; scores on other languages
  are meaningless.
- 1 MB paste cap.
