# -*- coding: utf-8 -*-
"""Automated tests for the Reading Time & Readability Calculator."""
import pytest

from app import (app, analyze, count_syllables, split_sentences,
                 flesch_reading_ease, flesch_explanation)


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


SAMPLE = ("The quick brown fox jumps over the lazy dog. "
          "Pack my box with five dozen liquor jugs! "
          "How vexingly quick daft zebras jump?")


# --- Unit: sentences -------------------------------------------------------
def test_split_sentences():
    assert split_sentences("Hello world. How are you? Fine!") == \
        ["Hello world.", "How are you?", "Fine!"]


def test_split_sentences_empty():
    assert split_sentences("   ") == []


# --- Unit: syllables -------------------------------------------------------
def test_syllables_simple():
    assert count_syllables("cat") == 1
    assert count_syllables("reading") == 2
    assert count_syllables("beautiful") == 3


def test_syllables_silent_e():
    assert count_syllables("cake") == 1
    assert count_syllables("the") == 1


# --- Unit: flesch ----------------------------------------------------------
def test_flesch_easy_text_scores_high():
    score = flesch_reading_ease(100, 10, 130)
    assert score > 80


def test_flesch_hard_text_scores_low():
    score = flesch_reading_ease(100, 4, 220)
    assert score < 50


def test_flesch_explanation_bands():
    assert "Very easy" in flesch_explanation(95)
    assert "Standard" in flesch_explanation(65)
    assert "Very difficult" in flesch_explanation(10)


# --- Unit: analyze ---------------------------------------------------------
def test_analyze_counts():
    stats = analyze(SAMPLE)
    assert stats["word_count"] == 23
    assert stats["sentence_count"] == 3
    assert stats["char_count"] == len(SAMPLE)


def test_analyze_reading_time():
    stats = analyze("word " * 400)
    assert stats["reading_minutes"] == 2
    assert stats["reading_seconds"] == 0


def test_analyze_reading_time_partial():
    stats = analyze("word " * 100)
    assert stats["reading_minutes"] == 0
    assert stats["reading_seconds"] == 30


def test_analyze_longest_sentences():
    text = "Short. This is a considerably longer sentence with many words in it. Tiny."
    stats = analyze(text)
    longest = stats["longest_sentences"]
    assert len(longest) == 3
    assert longest[0]["words"] >= longest[1]["words"] >= longest[2]["words"]
    assert "considerably longer" in longest[0]["text"]


def test_analyze_fewer_than_three_sentences():
    stats = analyze("Just one sentence here.")
    assert len(stats["longest_sentences"]) == 1


# --- Routes ----------------------------------------------------------------
def test_index_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Reading Time" in resp.data


def test_analyze_route(client):
    resp = client.post("/analyze", data={"article": SAMPLE})
    assert resp.status_code == 200
    assert b"23" in resp.data  # word count shown
    assert b"Flesch Reading Ease" in resp.data


def test_analyze_route_empty_rejected(client):
    resp = client.post("/analyze", data={"article": "   "})
    assert resp.status_code == 400


def test_result_highlights_longest(client):
    text = "Short. This is a considerably longer sentence with many words in it. Tiny."
    resp = client.post("/analyze", data={"article": text})
    assert b"<mark>" in resp.data
