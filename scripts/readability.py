#!/usr/bin/env python3
"""Readability metrics for English text. Used to validate age-adapted output.

Standard formulas, no dependencies:

    Flesch-Kincaid Grade Level  = 0.39*(words/sentences) + 11.8*(syllables/words) - 15.59
    Flesch Reading Ease         = 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)

Syllable counting is the usual heuristic (vowel groups, minus silent endings).
It is approximate -- treat the grade level as a band, not a decimal.

Run directly for a report on any set of text files:

    python3 scripts/readability.py corpus/stories/*.txt
"""
import re
import statistics
import sys

VOWELS = re.compile(r"[aeiouy]{1,2}")


def syllables(word):
    """Approximate syllable count for an English word."""
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    return max(1, len(VOWELS.findall(w)))


def sentences(text):
    t = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?])\s+", t)
    return [p for p in parts if len(p.split()) > 1]


def metrics(text):
    """Return a dict of readability measures, or None if there is no prose."""
    sents = sentences(text)
    words = re.findall(r"[A-Za-z][A-Za-z'\-]*", text)
    if not sents or not words:
        return None
    syl = sum(syllables(w) for w in words)
    n_w, n_s = len(words), len(sents)
    asl = n_w / n_s
    asw = syl / n_w
    return {
        "words": n_w,
        "sentences": n_s,
        "words_per_sentence": round(asl, 2),
        "syllables_per_word": round(asw, 3),
        "fk_grade": round(0.39 * asl + 11.8 * asw - 15.59, 2),
        "flesch_ease": round(206.835 - 1.015 * asl - 84.6 * asw, 1),
        "long_words_pct": round(
            100 * sum(1 for w in words if syllables(w) >= 3) / n_w, 1
        ),
    }


def check_target(m, target):
    """Compare metrics against a target spec. Returns a list of failure strings."""
    fails = []
    if m is None:
        return ["no prose found"]
    for key, lo, hi in (
        ("fk_grade", target["fk_grade"][0], target["fk_grade"][1]),
        ("words_per_sentence", target["words_per_sentence"][0],
         target["words_per_sentence"][1]),
        ("words", target["word_count"][0], target["word_count"][1]),
    ):
        v = m[key]
        if v < lo:
            fails.append(f"{key} {v} below target {lo}-{hi}")
        elif v > hi:
            fails.append(f"{key} {v} above target {lo}-{hi}")
    if m["syllables_per_word"] > target["max_syllables_per_word"]:
        fails.append(
            f"syllables_per_word {m['syllables_per_word']} above "
            f"{target['max_syllables_per_word']}"
        )
    return fails


def main():
    import glob
    import json
    import os

    paths = sys.argv[1:]
    if not paths:
        print(__doc__)
        return 1
    files = [f for p in paths for f in glob.glob(p)]
    rows = []
    for f in files:
        body = open(f, encoding="utf-8").read()
        if "\n\n" in body and len(body.split("\n\n")[0]) < 200:
            body = body.split("\n\n", 1)[1]  # drop the title header
        m = metrics(body)
        if m:
            rows.append((os.path.basename(f), m))
    if not rows:
        print("no measurable text")
        return 1
    fk = [m["fk_grade"] for _, m in rows]
    print(f"{len(rows)} files")
    print(f"  median FK grade       : {statistics.median(fk):.1f}")
    print(f"  median words/sentence : "
          f"{statistics.median([m['words_per_sentence'] for _, m in rows]):.1f}")
    print(f"  median syllables/word : "
          f"{statistics.median([m['syllables_per_word'] for _, m in rows]):.3f}")
    print(f"  total words           : {sum(m['words'] for _, m in rows):,}")
    print(f"  grade <=3 : {sum(1 for x in fk if x <= 3)}   "
          f"3-6 : {sum(1 for x in fk if 3 < x <= 6)}   "
          f">6 : {sum(1 for x in fk if x > 6)}")
    if "-v" in sys.argv:
        print()
        for name, m in sorted(rows, key=lambda r: -r[1]["fk_grade"]):
            print(f"  {m['fk_grade']:>5.1f}  {m['words_per_sentence']:>5.1f}w/s  "
                  f"{m['words']:>5}w  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
