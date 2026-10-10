"""Tests for the speech analysis rules.

Run them from the backend folder with:   pytest
Each test checks one rule. If you change a rule in speech_analysis.py,
the tests show you exactly what changed.
"""
from app.services.speech_analysis import (
    analyse_speech,
    delivery_score,
    find_fillers,
    find_pauses,
    pace_label,
)


def timed_words(text, word_seconds=0.35, gap=0.05, silence_after=None):
    """Builds a fake speech-to-text word list: each word lasts `word_seconds`,
    with a small `gap` between words. silence_after = {word position: extra seconds}."""
    silence_after = silence_after or {}
    words, t = [], 0.0
    for i, word in enumerate(text.split()):
        words.append({"word": word, "start": round(t, 2), "end": round(t + word_seconds, 2)})
        t += word_seconds + gap + silence_after.get(i, 0)
    return words


# ---------- Filler words ----------

def test_thinking_sounds_always_count():
    assert find_fillers("So um I built it uh yesterday".split()) == [[1], [5]]


def test_like_counts_only_between_commas():
    assert find_fillers("I, like, enjoy coding".split()) == [[1]]
    assert find_fillers("I would like to join your team".split()) == []
    assert find_fillers("Tools like React are useful".split()) == []


def test_you_know_counts_as_one_filler():
    assert find_fillers("It was, you know, really hard".split()) == [[2, 3]]
    assert find_fillers("Do you know Python".split()) == []


def test_capitals_and_punctuation_are_ignored():
    assert find_fillers("Um, Basically, it works.".split()) == [[0], [1]]


# ---------- Pace ----------

def test_pace_labels():
    assert pace_label(90) == "too slow"
    assert pace_label(120) == "a little slow"
    assert pace_label(140) == "good"
    assert pace_label(160) == "a little fast"
    assert pace_label(190) == "too fast"


def test_pace_ignores_silence_before_and_after_speaking():
    words = timed_words(" ".join(["word"] * 40))  # 40 words at 0.4s each = 150 per minute
    result = analyse_speech(words, "", duration_seconds=30)  # recording was longer (silence)
    assert 145 <= result["words_per_minute"] <= 155
    assert result["pace"] == "good"


def test_very_short_answers_are_not_judged_on_pace():
    result = analyse_speech(timed_words("Hello this is Saif"), "", duration_seconds=2)
    assert result["pace"] == "too short to judge"


# ---------- Pauses ----------

def test_silence_mid_sentence_is_a_hesitation():
    pauses = find_pauses(timed_words("I built the app", silence_after={1: 1.2}))
    assert list(pauses) == [1]
    assert pauses[1][1] == "hesitation"


def test_short_silence_after_a_full_stop_is_natural():
    assert find_pauses(timed_words("I built it. Then I tested", silence_after={2: 1.2})) == {}


def test_long_silence_counts_anywhere():
    pauses = find_pauses(timed_words("I built it. Then I tested", silence_after={2: 2.5}))
    assert pauses[2][1] == "long"
    assert pauses[2][0] >= 2.5


# ---------- Delivery score ----------

def test_perfect_delivery_scores_10():
    assert delivery_score("good", 0, 0, 0, speaking_seconds=60) == 10


def test_score_never_goes_below_1():
    assert delivery_score("too fast", 30, 10, 5, speaking_seconds=60) == 1


def test_fillers_lower_the_score():
    calm = delivery_score("good", 0, 0, 0, speaking_seconds=60)
    nervous = delivery_score("good", 6, 0, 0, speaking_seconds=60)  # 6 fillers in a minute
    assert nervous < calm


# ---------- The full analysis ----------

def test_transcript_tokens_mark_fillers_and_pauses():
    words = timed_words("So, um, I built, like, an app", silence_after={0: 2.4})
    result = analyse_speech(words, "", duration_seconds=10)
    tokens = result["tokens"]
    assert tokens[1]["filler"] is True           # "um,"
    assert tokens[4]["filler"] is True           # "like," set apart by commas ("built, like,")
    assert tokens[2]["filler"] is False          # "I"
    assert tokens[0]["pause_kind"] == "long"     # 2.4s of silence after "So,"
    assert result["long_pause_count"] == 1


def test_works_without_word_timings():
    result = analyse_speech([], "So um I built an app", duration_seconds=10)
    assert result["filler_count"] == 1
    assert result["long_pause_count"] == 0
    assert len(result["tokens"]) == 6


def test_good_delivery_gets_encouragement():
    words = timed_words(" ".join(["word"] * 40))
    result = analyse_speech(words, "", duration_seconds=20)
    assert result["delivery_score"] == 10
    assert result["tips"] == ["Steady pace and almost no filler words. That's confident delivery, so keep it up."]
