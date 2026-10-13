#!/usr/bin/env python3
"""First-pass age-band curation for the Panchatantra corpus.

Scores every story for content that decides whether it can be given to a young
child, and records the evidence so a human can check the call rather than trust
it. This is a heuristic screening pass, NOT a final editorial judgement -- read
data/curation.json and overrule it.

    python3 scripts/curate.py            # write data/curation.json + a report
    python3 scripts/curate.py --report   # print the table only
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
STORIES = os.path.join(ROOT, "corpus", "stories")
DATA = os.path.join(ROOT, "data")

# (label, weight, regex). Weight is "how disqualifying" for the youngest band.
# EXCLUDE-level signals are ones no amount of rewriting fixes without changing
# the plot; SOFT signals a rewrite can carry.
SIGNALS = [
    # A character dying is normal in a fable -- the villain gets eaten, the lion
    # falls in the well. That is not disqualifying, so death carries low weight.
    # What is disqualifying is content a rewrite cannot remove without changing
    # the plot: sex, misogyny, dismemberment, cannibalism, harm to children.
    ("sexual",        5, r"\b(adulter\w*|paramour|harlot|prostitut\w*|concubine|"
                        r"stolen bliss|wench|slut|lewd|unchaste|fornication)\b"),
    ("misogyny",      4, r"\b(women (are|oft|will)|a woman's|fickle|no woman|"
                        r"every woman|the slut|trust a woman)\b"),
    ("dismember",     5, r"\b(dismember\w*|cut (up|off)|chopped|hacked|"
                        r"cut her body|severed)\b"),
    ("infanticide",   5, r"\b(exposed in the forest|kill the (girl|child|baby)|"
                        r"abandon\w* the (girl|child|baby)|put the child)\b"),
    ("cannibal",      4, r"\b(eat (him|her|them|me)|devour (him|her)|"
                        r"feast on (his|her) flesh)\b"),
    ("sexual-soft",   2, r"\b(seduce\w*|intrigue with|guilty love|amorous|"
                        r"paramour|elope\w*)\b"),
    ("gore-detail",   2, r"\b(brains|entrails|guts|corpse|mangled|"
                        r"torn to bits|blood (spurt|flow))\b"),
    ("murder",        1, r"\b(murder\w*|slay|slain|killed|put to death|"
                        r"poison\w*|strangl\w*|behead\w*)\b"),
]

# a story this long is hard for 4-9 even after simplification
LONG_FOR_YOUNG = 1800


CLOSING = re.compile(r"and the rest of it", re.I)

# A character dying is normal in a fable -- the villain gets eaten, the lion
# falls in the well. That is not disqualifying, so death carries low weight.
# What is disqualifying is content a rewrite cannot remove without changing
# the plot: sex, misogyny, dismemberment, cannibalism, harm to children.


def fable_only(body):
    """Trim a chapter file down to the fable it contains, where we can tell.

    These files are book chapters: the fable sits between its own heading and its
    closing formula ("...and the rest of it"), and everything after that is the
    parent frame resuming -- court intrigue and "women are fickle" verses that
    belong to a different story. Scanning the whole chapter blames the fable for
    the frame's content, which is how The Blue Jackal got excluded.

    Returns (text, scoped). scoped is False when no closing formula was found,
    meaning the scan covers the whole chapter and the verdict is less certain.
    """
    m = CLOSING.search(body)
    if m:
        # carry any trailing punctuation into the cut -- the formula is normally
        # written 'and the rest of it."' and stopping before the quote leaves the
        # fable ending mid-sentence with the period stranded in the remainder.
        end = m.end()
        while end < len(body) and body[end] in '."\'”’':
            end += 1
        return body[:end], True
    return body, False


def scan(sid, body):
    low = body.lower()
    hits, score = [], 0
    for label, weight, rx in SIGNALS:
        found = re.findall(rx, low)
        if found:
            n = len(found)
            score += weight * min(n, 3)
            snippet = re.search(rx, low)
            a = max(0, snippet.start() - 45)
            hits.append({
                "signal": label, "count": n, "weight": weight,
                "example": re.sub(r"\s+", " ", low[a:snippet.end() + 45]).strip(),
            })
    words = len(body.split())
    if words > LONG_FOR_YOUNG:
        score += 2
    return score, hits, words


def verdict(score):
    # recalibrated: death alone must not exclude (it is ordinary fable material)
    if score >= 8:
        return "EXCLUDE"
    if score >= 3:
        return "NINE_PLUS"
    return "BOTH"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    manifest = {r["story_id"]: r for r in
                json.load(open(os.path.join(ROOT, "corpus", "manifest.json")))}
    rows = []
    for f in sorted(os.listdir(STORIES)):
        if not f.endswith(".txt"):
            continue
        sid = f.split("-")[0]
        body = open(os.path.join(STORIES, f)).read().split("\n\n", 1)[-1]
        scoped_body, scoped = fable_only(body)
        score, hits, words = scan(sid, scoped_body)
        v = verdict(score)
        top = sorted(hits, key=lambda h: -h["weight"])[:2]
        reason = "; ".join(f"{h['signal']} x{h['count']}" for h in top) or "nothing flagged"
        rows.append({
            "story_id": sid,
            "title": manifest[sid]["title_short"],
            "book": manifest[sid]["book"],
            "words": words,
            "score": score,
            "verdict": v,
            "reason": reason,
            "scoped_to_fable": scoped,
            "evidence": hits,
            "bands": [b for b, keep in (("4-9", v == "BOTH"),
                                        ("9+", v in ("BOTH", "NINE_PLUS"))) if keep],
        })

    rows.sort(key=lambda r: (r["book"], r["story_id"]))
    if args.report:
        for r in rows:
            print(f"{r['story_id']}  b{r['book']}  {r['score']:>3}  "
                  f"{r['verdict']:<9} {r['title'][:38]:<40} {r['reason']}")
        return 0

    os.makedirs(DATA, exist_ok=True)
    out = {r["story_id"]: {"title": r["title"], "book": r["book"],
                           "bands": r["bands"], "verdict": r["verdict"],
                           "score": r["score"], "reason": r["reason"],
                           "scoped_to_fable": r["scoped_to_fable"],
                           "evidence": r["evidence"]}
           for r in rows}
    json.dump(out, open(os.path.join(DATA, "curation.json"), "w"), indent=1)

    from collections import Counter
    c = Counter(r["verdict"] for r in rows)
    print(f"wrote data/curation.json for {len(rows)} stories")
    print(f"  BOTH (4-9 and 9+) : {c['BOTH']}")
    print(f"  NINE_PLUS only    : {c['NINE_PLUS']}")
    print(f"  EXCLUDE           : {c['EXCLUDE']}")
    print("\nthis is a heuristic screen. review before handing it to an adapter.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
