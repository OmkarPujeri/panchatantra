"""Review the model-drafted tags and items against the text a child actually reads.

The drafts live in data/story_{tags,items}_authored.json with `_draft: true`. This
tool does the three jobs of a review pass:

    python3 scripts/review.py --list           # what is left to review, served-first
    python3 scripts/review.py --flag           # mechanically-suspicious entries
    python3 scripts/review.py PT034            # draft + the served band text(s)
    python3 scripts/review.py PT034 --approve  # clear _draft (only after reading)

Two rules the worklog learned the hard way, both encoded here:
  * read the ADAPTED text the child is served, never `curation.reason` (which
    describes the source, before the telling was softened);
  * for an age-floor call, judge harm in the band actually served, not whether the
    word appears anywhere in the whole chapter.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))          # so `engine` imports when run as a script
TAGS_AUTH = ROOT / "data" / "story_tags_authored.json"
ITEMS_AUTH = ROOT / "data" / "story_items_authored.json"
TAGS_BUILT = ROOT / "corpus" / "story_tags.json"
AGE = ROOT / "corpus" / "age"

# A candidate list, not a verdict: the worklog's third (correct) audit scanned the
# served band for harm words and read the hits. "pretend to be dead" and "a dead
# calf" are the known false positives — a hit means READ, not DEFECT.
HARM = re.compile(r"\b(kill\w*|died?|dead|death|murder\w*|blood\w*|devour\w*|"
                  r"drown\w*|slay\w*|stabbed|stabbing|stabs|corpse|flesh|cannibal\w*)\b",
                  re.I)


def load():
    auth_t = json.loads(TAGS_AUTH.read_text())
    auth_i = json.loads(ITEMS_AUTH.read_text())
    built = {s["story_id"]: s for s in json.loads(TAGS_BUILT.read_text())["stories"]}
    return auth_t, auth_i, built


def text_for(sid, band):
    hits = sorted((AGE / band).glob(f"{sid}-*.txt"))
    return hits[0].read_text() if hits else None


def served_ids():
    """Stories the engine actually reaches at some age 4-11 — review these first."""
    from engine.demo import simulate
    ids = set()
    for age in range(4, 12):
        for good in (True, False):
            _, trace = simulate("x", age, answers=good, n=8, co_read=(age >= 10))
            ids |= {t[0] for t in trace}
    return ids


def drafts(auth_t, auth_i, built):
    """Stories still carrying a _draft entry, with which files and whether served."""
    served = served_ids()
    rows = []
    for sid in sorted(built):
        t_draft = auth_t["tags"].get(sid, {}).get("_draft", False)
        i_draft = auth_i["items"].get(sid, {}).get("_draft", False)
        if t_draft or i_draft:
            rows.append((sid, built[sid]["age_map"]["min_age"],
                         "tag" if t_draft else "", "item" if i_draft else "",
                         sid in served))
    return rows


def show(sid, auth_t, auth_i, built):
    tag, item, b = auth_t["tags"].get(sid), auth_i["items"].get(sid), built.get(sid)
    if tag is None and item is None:
        sys.exit(f"{sid}: no authored entry")
    print("=" * 78)
    print(f"{sid}  {b['title'] if b else ''}   "
          f"[{b['age_map']['bands']} {b['age_map']['min_age']}-{b['age_map']['max_age']}]"
          if b else sid)
    print("=" * 78)
    if tag:
        print(f"\n--- TAG {'(DRAFT)' if tag.get('_draft') else '(reviewed)'} ---")
        for k in ("moral", "themes", "characters", "skills", "min_age", "max_age",
                  "key_beat", "tone", "complexity", "rationale"):
            if k in tag:
                print(f"  {k}: {json.dumps(tag[k], ensure_ascii=False)}")
    if item:
        print(f"\n--- ITEMS {'(DRAFT)' if item.get('_draft') else '(reviewed)'} ---")
        for skill, prompt, opts, correct, diff, age in item.get("measurement", []):
            print(f"\n  [{skill}] {prompt}")
            for i, o in enumerate(opts):
                print(f"      {'*' if i == correct else ' '} {chr(97 + i)}. {o}")
        for skill, band, prompt in item.get("discussion", []):
            print(f"\n  ({band}) [{skill}] {prompt}")
    if b:
        for band in b["age_map"]["bands"]:
            txt = text_for(sid, band)
            if txt:
                print(f"\n--- TEXT ({band}) ---\n{txt.strip()}")


def flags(auth_t, auth_i, built):
    out = []
    served = served_ids()
    for sid, entry in auth_i["items"].items():
        if not entry.get("_draft"):
            continue
        tmin = built[sid]["age_map"]["min_age"]
        for skill, prompt, opts, correct, diff, age in entry.get("measurement", []):
            lengths = [len(o) for o in opts]
            if lengths[correct] == max(lengths) and lengths.count(max(lengths)) == 1:
                out.append(("length-tell", sid, f"{skill}: the correct option is the "
                                                f"only longest — rewrite a distractor"))
            if age != tmin:
                out.append(("age-hint", sid, f"{skill}: suitable_from_age {age} vs "
                                             f"story min_age {tmin}"))
    for sid, b in built.items():
        if b["age_map"]["min_age"] > 6:
            continue
        txt = text_for(sid, "4-9") or text_for(sid, "9+")
        if not txt:
            continue
        hits = sorted({m.group(0).lower() for m in HARM.finditer(txt)})
        if hits and sid in served:
            out.append(("harm@<=6", sid, "in served band: " + ", ".join(hits)))
    return out


def approve(sid, auth_t, auth_i):
    n = 0
    for doc, coll in ((auth_t, "tags"), (auth_i, "items")):
        if sid in doc[coll] and doc[coll][sid].pop("_draft", None) is not None:
            n += 1
    TAGS_AUTH.write_text(json.dumps(auth_t, indent=2, ensure_ascii=False) + "\n")
    ITEMS_AUTH.write_text(json.dumps(auth_i, indent=2, ensure_ascii=False) + "\n")
    print(f"{sid}: cleared _draft on {n} file(s)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("story_id", nargs="*", help="story/stories to show")
    ap.add_argument("--list", action="store_true", help="drafts left, served-first")
    ap.add_argument("--flag", action="store_true", help="mechanically-suspicious entries")
    ap.add_argument("--approve", action="store_true", help="clear _draft (read first!)")
    args = ap.parse_args()

    auth_t, auth_i, built = load()

    if args.list:
        rows = drafts(auth_t, auth_i, built)
        served = [r for r in rows if r[4]]
        print(f"{len(rows)} stories still carry drafts "
              f"({len(served)} of them reachable by the engine at ages 4-11)\n")
        print("       min_age  files         story")
        for sid, mn, t, i, sv in rows:
            print(f"  {'★' if sv else ' '}    {mn:>2}      {t + ',' + i:<12}  {sid}")
        return

    if args.flag:
        out = flags(auth_t, auth_i, built)
        by = {}
        for kind, sid, msg in out:
            by.setdefault(kind, []).append((sid, msg))
        for kind in ("harm@<=6", "length-tell", "age-hint"):
            rows = by.get(kind, [])
            print(f"\n### {kind}  ({len(rows)})")
            for sid, msg in rows:
                print(f"  {sid}  {msg}")
        return

    if not args.story_id:
        ap.error("give a story id, or --list / --flag")

    if args.approve:
        for sid in args.story_id:
            approve(sid, auth_t, auth_i)
        return

    for sid in args.story_id:
        show(sid, auth_t, auth_i, built)
        print()


if __name__ == "__main__":
    main()
