"""Build corpus/story_items.json from data/story_items_authored.json.

Two explicit collections, because they have OPPOSITE band rules:

  measurement[]  mcq, auto-scored. Band-INVARIANT: the same item serves both bands,
                 so one child can be tracked over time and children compared.
                 Difficulty is a per-item property (difficulty_prior, later
                 calibrated to difficulty_b), NOT a band exclusion. A child who is
                 too young simply gets it wrong — which is signal, not breakage.
                 Write items answerable from the YOUNGER band's text; they then hold
                 for the richer telling too.

  discussion[]   open, adult-facilitated, NOT scored. Band-SPECIFIC: a 4-9 prompt
                 asks about feelings and choices; a 9+ prompt asks for
                 justification. Nothing is measured here, so divergence is free.

A story needs a discussion prompt for each band a child could actually READ it in —
not blanket "both bands". A 9+-only story is read in 9+ by everyone who can reach it,
so a 4-9 prompt for it is unreachable. See `required_bands`.

The old file put both kinds in one `items` list with a `band` field doing
exclusion duty — 9 items were silently unavailable to the 4-9 band, which would
have computed a child's score over a different question set depending on band.
That is the ambiguity this file removes.

Usage:
    python3 scripts/build_story_items.py            # write + validate
    python3 scripts/build_story_items.py --check    # validate existing file only
"""

import argparse
import json
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from engine.state import band_for_age  # noqa: E402  — one definition of the bands

TAGS = os.path.join(ROOT, "corpus", "story_tags.json")
AUTHORED = os.path.join(ROOT, "data", "story_items_authored.json")
OUT = os.path.join(ROOT, "corpus", "story_items.json")

BANDS = ("4-9", "9+")


def load_authored():
    """Authored banks keyed by story_id. See data/story_items_authored.json."""
    with open(AUTHORED, encoding="utf-8") as f:
        return json.load(f)["items"]


def required_bands(age_map):
    """The bands a child could actually read this story in.

    The band follows the TEXT, not the child's age alone: a story whose only band is
    '9+' is read in 9+ by everyone who can reach it, including a 9-year-old whose
    storage band is '4-9'.
    """
    bands = age_map["bands"]
    out = set()
    for age in range(age_map["min_age"], age_map["max_age"] + 1):
        child_band = band_for_age(age)
        out.add(child_band if child_band in bands else bands[0])
    return out


def requires_adult(skill):
    """M4/M5 need the co-read mode — the adult is the active ingredient."""
    return skill.startswith(("M4", "M5"))


def build(tags, authored):
    priors = {s["story_id"]: s["skills"] for s in tags["stories"]}
    measurement, discussion = [], []

    for sid in sorted(authored):
        entry = authored[sid]

        for n, row in enumerate(entry.get("measurement", []), 1):
            skill, prompt, options, correct, diff, age = row
            if priors.get(sid, {}).get(skill, 0) <= 0:
                raise SystemExit(f"{sid}: measurement skill {skill} has zero prior")
            if not skill.startswith("C"):
                raise SystemExit(f"{sid}: measurement skill {skill} is not a C skill")
            measurement.append({
                "item_id": f"{sid}-{skill.split('_')[0]}-m{n}",
                "story_id": sid,
                "skill": skill,
                "prompt": prompt,
                "options": options,
                "correct": correct,
                "difficulty_prior": diff,
                "suitable_from_age": age,
                "scored": True,
            })

        for n, row in enumerate(entry.get("discussion", []), 1):
            skill, band, prompt = row
            if priors.get(sid, {}).get(skill, 0) <= 0:
                raise SystemExit(f"{sid}: discussion skill {skill} has zero prior")
            if not skill.startswith("M"):
                raise SystemExit(f"{sid}: discussion skill {skill} is not an M skill")
            discussion.append({
                "prompt_id": f"{sid}-{skill.split('_')[0]}-{band.replace('+', 'p')}-d{n}",
                "story_id": sid,
                "skill": skill,
                "band": band,
                "prompt": prompt,
                "requires_adult": requires_adult(skill),
                "scored": False,
            })
    return measurement, discussion


def validate(doc, tags, authored):
    errs = []
    stories = {s["story_id"]: s for s in tags["stories"]}
    priors = {sid: s["skills"] for sid, s in stories.items()}
    ages = {sid: s["age_map"] for sid, s in stories.items()}

    missing = sorted(set(stories) - set(authored))
    if missing:
        errs.append(f"{len(missing)} tagged stories have no authored items: "
                    f"{', '.join(missing)}")

    for it in doc["measurement"]:
        sid, skill = it["story_id"], it["skill"]
        if not skill.startswith("C"):
            errs.append(f"{it['item_id']}: measurement item must be a C skill")
        if priors.get(sid, {}).get(skill, 0) <= 0:
            errs.append(f"{it['item_id']}: zero prior")
        if len(it["options"]) < 2:
            errs.append(f"{it['item_id']}: needs >=2 options")
        if not (0 <= it["correct"] < len(it["options"])):
            errs.append(f"{it['item_id']}: correct index out of range")
        if it.get("scored") is not True:
            errs.append(f"{it['item_id']}: scored must be True")
        if "band" in it:
            errs.append(f"{it['item_id']}: measurement items must NOT carry a band")
        if len(set(it["options"])) != len(it["options"]):
            errs.append(f"{it['item_id']}: duplicate options")

    # discussion: a prompt for every band a child could actually read the story in
    seen = {}
    for p in doc["discussion"]:
        sid, skill, band = p["story_id"], p["skill"], p["band"]
        if not skill.startswith("M"):
            errs.append(f"{p['prompt_id']}: discussion prompt must be an M skill")
        if priors.get(sid, {}).get(skill, 0) <= 0:
            errs.append(f"{p['prompt_id']}: zero prior")
        if band not in BANDS:
            errs.append(f"{p['prompt_id']}: bad band {band!r}")
        if p.get("scored") is not False:
            errs.append(f"{p['prompt_id']}: scored must be False")
        if p["requires_adult"] != requires_adult(skill):
            errs.append(f"{p['prompt_id']}: requires_adult wrong")
        if skill.startswith("M5") and (band != "9+" or ages[sid]["min_age"] < 9):
            errs.append(f"{p['prompt_id']}: M5 must be 9+ on a dilemma-capable story")
        seen.setdefault((sid, skill), set()).add(band)

    for (sid, skill), bands in seen.items():
        # M5 is a 9+ skill by definition — it is the one prompt with no younger variant
        if skill.startswith("M5"):
            continue
        # At least the reachable bands. Extra bands are harmless (they are simply
        # never served — e.g. a 4-8 story that carries 9+ prompts anyway).
        need = required_bands(ages[sid])
        if not need <= bands:
            errs.append(f"{sid}/{skill}: needs bands {sorted(need)}, has {sorted(bands)}")

    for sid in stories:
        if sid not in authored:
            continue
        items = [i for i in doc["measurement"] if i["story_id"] == sid]
        if len(items) < 3:
            errs.append(f"{sid}: fewer than 3 measurement items")
        if not any(p["story_id"] == sid for p in doc["discussion"]):
            errs.append(f"{sid}: no discussion prompts")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    with open(TAGS, encoding="utf-8") as f:
        tags = json.load(f)
    authored = load_authored()

    if args.check:
        with open(OUT, encoding="utf-8") as f:
            doc = json.load(f)
    else:
        measurement, discussion = build(tags, authored)
        drafts = sorted(sid for sid, e in authored.items() if e.get("_draft"))
        doc = {
            "meta": {
                "schema_version": "2.0",
                "built": date.today().isoformat(),
                "source": "corpus/story_tags.json + data/story_items_authored.json",
                "measurement_count": len(measurement),
                "discussion_count": len(discussion),
                "draft_unreviewed": len(drafts),
                "notes": [
                    "TWO collections, opposite band rules — see the module docstring.",
                    "measurement: mcq, auto-scored, band-INVARIANT (comparable over time and across children).",
                    "discussion: open, NOT scored, band-SPECIFIC (depth must differ by band).",
                    "difficulty is a per-item property (difficulty_prior -> difficulty_b), never a band exclusion.",
                    "suitable_from_age is a selection hint, NOT a filter — a young child simply answering wrongly is signal.",
                    "open responses are surfaced to the parent as raw text, never scored (PRODUCT_RESEARCH.md §3).",
                    "draft_unreviewed counts entries still marked _draft in data/story_items_authored.json",
                ],
            },
            "measurement": measurement,
            "discussion": discussion,
        }

    errs = validate(doc, tags, authored)
    if errs:
        print("VALIDATION FAILED:")
        for e in errs:
            print("  -", e)
        return 1

    if not args.check:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)
        print(f"wrote {OUT}")
        n = doc["meta"]["draft_unreviewed"]
        if n:
            print(f"WARNING: {n} of {len(authored)} stories' items are unreviewed drafts "
                  f"(_draft: true in data/story_items_authored.json)")

    m, d = doc["measurement"], doc["discussion"]
    adult = sum(1 for p in d if p["requires_adult"])
    print(f"OK: {len(m)} measurement items (all auto-scored, band-invariant) | "
          f"{len(d)} discussion prompts ({adult} need an adult)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
