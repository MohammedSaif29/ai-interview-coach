"""Speech analysis: HOW you spoke, not what you said.

Measures speaking pace, filler words, hesitations and long pauses, then turns them
into a delivery score and tips. Plain Python with no AI: every rule is written here,
so you can read it, explain it, and test it (see tests/test_speech_analysis.py).

Input: the word list from speech-to-text. Each word has a start and end time in
seconds, for example {"word": "Hello,", "start": 0.0, "end": 0.42}.
"""
import re
from collections import Counter

# ---------- Rules: change a number here and the tests show what changed ----------

GOOD_PACE = (130, 150)     # words per minute that sound calm and clear in an interview
HESITATION_GAP = 0.8       # seconds of silence mid-sentence: often a dropped "um"
LONG_PAUSE = 2.0           # seconds of silence that feels long to a listener
MIN_SECONDS_FOR_PACE = 8   # shorter than this, pace isn't meaningful

# Always fillers: sounds people make while thinking
SOUND_FILLERS = {"um", "umm", "uh", "uhh", "uhm", "er", "erm", "ah", "hmm", "mm"}
# Words that add nothing to an answer
WORD_FILLERS = {"basically", "literally"}
# Only fillers when set apart by commas: "I, like, built it" but not "I would like to"
COMMA_FILLERS = {"like"}
# Two-word fillers, only when followed by a comma: "you know," and "I mean,"
COMMA_PHRASES = {("you", "know"), ("i", "mean")}

PACE_PENALTY = {
    "good": 0, "a little slow": 1, "a little fast": 1,
    "too slow": 3, "too fast": 3, "too short to judge": 0,
}


def _clean(word: str) -> str:
    """'Like,' -> 'like'  (lowercase, letters and apostrophes only)"""
    return re.sub(r"[^a-z']", "", word.lower())


def _ends_with(word: str, marks: str) -> bool:
    return word.rstrip().endswith(tuple(marks))


def find_fillers(texts: list[str]) -> list[list[int]]:
    """Finds filler words. Returns each one as a list of word positions,
    e.g. [[1], [9, 10]] means word 1 is a filler, and words 9-10 are one ("you know,")."""
    found = []
    i = 0
    while i < len(texts):
        word = _clean(texts[i])
        previous = texts[i - 1] if i > 0 else ","  # the start of the answer counts like a comma
        has_next = i + 1 < len(texts)

        if word in SOUND_FILLERS or word in WORD_FILLERS:
            found.append([i])
        elif word in COMMA_FILLERS and _ends_with(texts[i], ",") and _ends_with(previous, ",.?!"):
            found.append([i])
        elif has_next and (word, _clean(texts[i + 1])) in COMMA_PHRASES and _ends_with(texts[i + 1], ","):
            found.append([i, i + 1])
            i += 1  # skip the second word of the phrase
        i += 1
    return found


def find_pauses(words: list[dict]) -> dict[int, tuple[float, str]]:
    """Finds silences between words. Returns {position of the word BEFORE the pause:
    (seconds, kind)}. kind is "long" (any gap of 2s+) or "hesitation" (0.8s+ in the
    middle of a sentence). Pausing after a comma or full stop is natural, so those
    short gaps are not counted."""
    pauses = {}
    for i in range(len(words) - 1):
        gap = words[i + 1]["start"] - words[i]["end"]
        if gap >= LONG_PAUSE:
            pauses[i] = (round(gap, 1), "long")
        elif gap >= HESITATION_GAP and not _ends_with(words[i]["word"], ",.?!;:"):
            pauses[i] = (round(gap, 1), "hesitation")
    return pauses


def pace_label(words_per_minute: int) -> str:
    low, high = GOOD_PACE
    if words_per_minute < low - 30:
        return "too slow"
    if words_per_minute < low:
        return "a little slow"
    if words_per_minute <= high:
        return "good"
    if words_per_minute <= high + 20:
        return "a little fast"
    return "too fast"


def delivery_score(pace: str, filler_count: int, hesitation_count: int,
                   long_pause_count: int, speaking_seconds: float) -> int:
    """Start at 10 and take points off. Deliberately simple, so it's easy to explain:
    - pace: -1 if a little off, -3 if far off
    - fillers + hesitations per minute: -1 at 2/min, -2 at 4, -3 at 6, -4 at 9 or more
    - long pauses: -1 each, at most -2
    The result is always between 1 and 10."""
    score = 10 - PACE_PENALTY[pace]
    minutes = max(speaking_seconds / 60, 0.5)  # so one "um" in a 10s clip isn't "6 per minute"
    per_minute = (filler_count + hesitation_count) / minutes
    for limit in (2, 4, 6, 9):
        if per_minute >= limit:
            score -= 1
    score -= min(long_pause_count, 2)
    return max(1, min(10, score))


def delivery_tips(pace: str, words_per_minute: int, filler_words: list[str], filler_count: int,
                  hesitation_count: int, longest_pause: float | None) -> list[str]:
    """Up to 3 tips, most important first."""
    tips = []
    if pace == "too short to judge":
        tips.append("Record a longer answer, at least 30 seconds, for a reliable delivery score.")
    elif pace in ("a little fast", "too fast"):
        tips.append(
            f"You spoke at {words_per_minute} words per minute. Slow down a little: aim for "
            "130 to 150, and pause briefly at the end of each sentence."
        )
    elif pace in ("a little slow", "too slow"):
        tips.append(
            f"You spoke at {words_per_minute} words per minute, which can sound unsure. Aim for "
            "130 to 150 by deciding your main points before you start."
        )
    if filler_count >= 2:
        examples = ", ".join(f'"{word}"' for word in filler_words[:3])
        tips.append(
            f"You used {filler_count} filler words ({examples}). When you need time to think, "
            "pause silently instead. A short pause sounds more confident."
        )
    if hesitation_count >= 2:
        tips.append(
            f"You hesitated {hesitation_count} times in the middle of sentences. "
            "Practise this answer once more so the words come more easily."
        )
    if longest_pause:
        tips.append(
            f"You went silent for {longest_pause} seconds at one point. If you need a moment, "
            'say "Let me think about that" so the pause feels deliberate.'
        )
    if not tips:
        tips.append("Steady pace and almost no filler words. That's confident delivery, so keep it up.")
    return tips[:3]


def analyse_speech(words: list[dict], transcript: str, duration_seconds: float) -> dict:
    """The main function: takes the speech-to-text result, returns the full analysis."""
    if words:
        texts = [w["word"] for w in words]
        # Time from the first word to the last, so silence before/after doesn't count
        speaking_seconds = max(words[-1]["end"] - words[0]["start"], 0.0)
        pauses = find_pauses(words)
    else:
        # No word timings: we can still count words and fillers, but not pauses
        texts = transcript.split()
        speaking_seconds = duration_seconds
        pauses = {}

    word_count = len(texts)
    words_per_minute = round(word_count / (speaking_seconds / 60)) if speaking_seconds > 0 else 0
    pace = pace_label(words_per_minute) if speaking_seconds >= MIN_SECONDS_FOR_PACE else "too short to judge"

    fillers = find_fillers(texts)
    filler_positions = {i for group in fillers for i in group}
    filler_counts = Counter(" ".join(_clean(texts[i]) for i in group) for group in fillers)
    filler_words = [word for word, _ in filler_counts.most_common()]

    hesitation_count = sum(1 for _, kind in pauses.values() if kind == "hesitation")
    long_pauses = [seconds for seconds, kind in pauses.values() if kind == "long"]

    tokens = [
        {
            "text": text,
            "filler": i in filler_positions,
            "pause_seconds": pauses[i][0] if i in pauses else None,
            "pause_kind": pauses[i][1] if i in pauses else None,
        }
        for i, text in enumerate(texts)
    ]

    return {
        "word_count": word_count,
        "speaking_seconds": round(speaking_seconds, 1),
        "words_per_minute": words_per_minute,
        "pace": pace,
        "filler_count": len(fillers),
        "filler_words": [{"text": word, "count": count} for word, count in filler_counts.most_common()],
        "hesitation_count": hesitation_count,
        "long_pause_count": len(long_pauses),
        "delivery_score": delivery_score(pace, len(fillers), hesitation_count, len(long_pauses), speaking_seconds),
        "tips": delivery_tips(pace, words_per_minute, filler_words, len(fillers),
                              hesitation_count, max(long_pauses) if long_pauses else None),
        "tokens": tokens,
    }
