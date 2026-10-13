"""Build corpus/story_tags.json from data/story_tags_authored.json.

Mechanical fields (readability, duration, scene count, dialogue count) are computed
from the adapted text. Judgment fields (moral, themes, characters, skills priors,
age_map, video_brief) are authored in data/story_tags_authored.json and MUST be
human-reviewed — entries carrying `_draft: true` are model-drafted and unreviewed.

Every story that has adapted text must have an authored entry; the build fails and
names the ones that do not.

Usage:
    python3 scripts/build_story_tags.py            # write + validate
    python3 scripts/build_story_tags.py --check    # validate existing file only
"""

import argparse
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from readability import metrics  # noqa: E402

ADAPTED = os.path.join(ROOT, "corpus", "panchatantra_adapted.json")
AUTHORED = os.path.join(ROOT, "data", "story_tags_authored.json")
OUT = os.path.join(ROOT, "corpus", "story_tags.json")

SKILL_IDS = [
    "M1_perspective_taking", "M2_intention_vs_outcome", "M3_consequence_reasoning",
    "M4_justification_quality", "M5_moral_conflict",
    "C1_sequence", "C2_cause_effect", "C3_character_motive",
    "C4_vocabulary", "C5_inference", "C6_theme",
]


def load_authored():
    """Authored judgment keyed by story_id. See data/story_tags_authored.json.

    Returns (tags, skipped). `skipped` maps a story_id to why it is deliberately
    NOT tagged — records in the adapted corpus that are not standalone stories.
    """
    with open(AUTHORED, encoding="utf-8") as f:
        doc = json.load(f)
    return doc["tags"], doc.get("_skipped", {})


def taggable_ids(src):
    """Stories that can be tagged — those with at least one band of adapted text."""
    return {sid for sid, s in src.items() if s.get("adapted")}


def expand_skills(short):
    """{'M1':2,...} -> {'M1_perspective_taking':2,...}"""
    out = {}
    for sid in SKILL_IDS:
        key = sid.split("_")[0]
        out[sid] = short.get(key, 0)
    return out


def dialogue_lines(text):
    # adapted texts use curly quotes; match either
    return len(re.findall(r'[“"][^”"]+[”"]', text))


def text_of(payload):
    return payload["text"] if isinstance(payload, dict) else payload


def build_record(sid, src, t):
    adapted = src["adapted"]
    readability = {}
    for band, payload in adapted.items():
        m = metrics(text_of(payload))
        readability[band] = {
            "fk_grade": round(m["fk_grade"], 2),
            "words_per_sentence": round(m["words_per_sentence"], 2),
            "words": m["words"],
        }

    # video load scales off the richer (9+) telling where present
    ref = max(readability.values(), key=lambda r: r["words"])
    words = ref["words"]
    duration = max(60, int(round(words / 2.2 / 15.0) * 15))
    # dialogue: max across bands — a band's telling may drop direct speech entirely
    dlg = max(dialogue_lines(text_of(p)) for p in adapted.values())

    bands = sorted(adapted.keys())
    calibration = {k: {"difficulty_b": None, "n_observations": 0}
                   for k, v in expand_skills(t["skills"]).items() if v > 0}

    return {
        "story_id": sid,
        "title": src["title"],
        "source_file": src["source_file"],
        "age_map": {
            "bands": bands,
            "min_age": t["min_age"],
            "max_age": t["max_age"],
            "rationale": t["rationale"],
        },
        "readability": readability,
        "moral": {"text": t["moral"][0], "domain": t["moral"][1]},
        "themes": t["themes"],
        "characters": [{"name": n, "species": s, "role": r} for n, s, r in t["characters"]],
        "skills": expand_skills(t["skills"]),
        "calibration": calibration,
        "attention_load": {
            "duration_sec": duration,
            "pace": "slow" if ref["words"] < 230 else "medium",
            "scene_density": t["complexity"],
            "dialogue_lines": dlg,
        },
        "video_brief": {
            "scenes": max(4, min(12, round(words / 28))),
            "visual_complexity": t["complexity"],
            "tone": t["tone"],
            "characters_to_design": [n for n, _, _ in t["characters"]],
            "key_beat": t["key_beat"],
        },
    }


def validate(doc, taggable, skipped=()):
    errs = []
    stories = doc["stories"]

    untagged = taggable - {s["story_id"] for s in stories} - set(skipped)
    if untagged:
        missing = sorted(untagged)
        errs.append(f"{len(missing)} stories have adapted text but no authored tags: "
                    f"{', '.join(missing)}")

    for s in stories:
        sid = s["story_id"]
        sk = s["skills"]
        if set(sk) != set(SKILL_IDS):
            errs.append(f"{sid}: skills keys != taxonomy")
        for k, v in sk.items():
            if not (isinstance(v, int) and 0 <= v <= 3):
                errs.append(f"{sid}.{k}: prior {v!r} not an int 0-3")
        if not any(v > 0 for v in sk.values()):
            errs.append(f"{sid}: no skill has a non-zero prior")
        if set(s["calibration"]) != {k for k, v in sk.items() if v > 0}:
            errs.append(f"{sid}: calibration keys must match skills with prior > 0")
        if not set(s["age_map"]["bands"]) <= {"4-9", "9+"}:
            errs.append(f"{sid}: bad bands {s['age_map']['bands']}")
        if s["age_map"]["min_age"] > s["age_map"]["max_age"]:
            errs.append(f"{sid}: min_age > max_age")
        # A 9+-only story has no 4-9 text, so the 4-9 band cannot be served.
        if s["age_map"]["bands"] == ["9+"] and s["age_map"]["min_age"] < 9:
            errs.append(f"{sid}: bands ['9+'] but min_age {s['age_map']['min_age']} < 9")
        if not s["moral"]["text"].strip():
            errs.append(f"{sid}: empty moral")
        if not s["video_brief"]["characters_to_design"]:
            errs.append(f"{sid}: no characters_to_design")
    # M5 (moral conflict) is a 9+ skill — never served to the younger sub-bands
    for s in stories:
        if s["skills"]["M5_moral_conflict"] > 0 and s["age_map"]["min_age"] < 9:
            errs.append(f"{s['story_id']}: M5 prior>0 but min_age {s['age_map']['min_age']} < 9")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate existing output only")
    args = ap.parse_args()

    with open(ADAPTED, encoding="utf-8") as f:
        src = {s["story_id"]: s for s in json.load(f)["stories"]}
    taggable = taggable_ids(src)
    authored, skipped = load_authored()

    if args.check:
        with open(OUT, encoding="utf-8") as f:
            doc = json.load(f)
    else:
        orphaned = sorted(set(authored) - taggable)
        if orphaned:
            print("VALIDATION FAILED:")
            print(f"  - authored tags for stories with no adapted text: {', '.join(orphaned)}")
            return 1

        ids = sorted(set(authored) & taggable)
        drafts = [sid for sid in ids if authored[sid].get("_draft")]
        doc = {
            "meta": {
                "schema_version": "1.0",
                "built": date.today().isoformat(),
                "source": "corpus/panchatantra_adapted.json + data/story_tags_authored.json",
                "taggable_stories": len(taggable),
                "draft_unreviewed": len(drafts),
                "skipped": {k: skipped[k] for k in sorted(skipped)},
                "notes": [
                    "skills priors are ORDINAL 0-3 proposals for human review; they are never summed",
                    "calibration is engine-written; empty here by design",
                    "skills is a flat block when both bands agree; use a per-band dict when they differ",
                    "attention_load is a demand parameter, not a mastered skill (see PRODUCT_RESEARCH.md §2)",
                    "draft_unreviewed counts entries still marked _draft in data/story_tags_authored.json",
                ],
            },
            # _draft is review state, not schema — stripped from the output record
            "stories": [build_record(p, src[p], authored[p]) for p in ids],
        }

    errs = validate(doc, taggable, skipped)
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
            print(f"WARNING: {n} of {len(doc['stories'])} entries are unreviewed drafts "
                  f"(_draft: true in data/story_tags_authored.json)")
        no_text = sorted(set(src) - taggable)
        print(f"skipped {len(no_text)} stories with no adapted text: {', '.join(no_text)}")
        for sid in sorted(skipped):
            print(f"skipped {sid} (not a standalone story): {skipped[sid]}")

    print(f"OK: {len(doc['stories'])} records validated against schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
