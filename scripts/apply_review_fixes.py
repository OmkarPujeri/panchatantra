"""Apply the review fixes that survived verification + a second read.

Source of truth for the edits is data/review_2026-10-01_workflow.json — the raw output of
the 23-agent fan-out, kept in the repo so the work is auditable and so this script never
retypes a string (a hand-copied `old` is how you corrupt a corpus).

Only the stories listed in APPLY are touched. The holds are deliberate:

  PT010  the 4-9 fish-bone death is FABRICATED — the source's real ending is the
         golden-chain device (corpus/panchatantra_complete.txt:2768-2774), misfiled by the
         same partition bug as HANDOVER bug #7. Needs a decision, not a patch.
  PT003  its verifier hallucinated ("The bull lay dead" is not in the 9+ file); the draft
         ending also names Cheek where the source names Victor.
  PT059  the band-agreement mechanism could not be confirmed against the source.
  PT084  verifier rejected it; also needs a build_story_tags.py rerun.
  PT017  its draft agent died on an API error and never ran.

TWO TRAPS the verifiers caught, both handled here:
  * tag/item edits are applied STRUCTURALLY, by story_id — never by string replace.
    '"C5": 3' occurs ~20x and '"C4": 3' 5x in data/story_tags_authored.json; a naive
    replace corrupts unrelated stories.
  * text edits locate their target by searching the story's own band files for the exact
    `old`, rather than trusting the band label the agent supplied.

Guarded and idempotent: every `old` must be present or the run refuses; a re-run that
finds `new` already in place is a no-op.

    python3 scripts/apply_review_fixes.py [--dry-run]
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / "data" / "review_2026-10-01_workflow.json"
TAGS = ROOT / "data" / "story_tags_authored.json"
ITEMS = ROOT / "data" / "story_items_authored.json"

APPLY = {"PT027", "PT031", "PT082", "PT086", "PT004", "PT023", "PT025"}

# tag edits are structural: story_id -> (locator, value). Not string replaces.
TAG_EDITS = {
    ("PT023", "characters"): "elephant_role",   # Elephant: victim -> antagonist
    ("PT025", "C5_inference"): 1,               # prior 3 overstated, narrated not inferred
    ("PT004", "moral"): "hurt_not_crush",       # text softened "crushed" to "hurt"
}


def story_files(sid: str):
    return sorted(glob.glob(str(ROOT / "corpus" / "age" / "*" / f"{sid}-*.txt")))


def find_text_target(sid: str, old: str):
    """Return (path, text) for the band file containing `old`, or (None, None)."""
    for p in story_files(sid):
        t = Path(p).read_text(encoding="utf-8")
        if old in t:
            return Path(p), t
    return None, None


def load_edits():
    doc = json.loads(WORKFLOW.read_text())
    out = {}
    for c in doc["result"]["confirmed"]:
        if c["story_id"] in APPLY:
            out[c["story_id"]] = c["edits"]
    missing = APPLY - set(out)
    assert not missing, f"workflow output has no edits for {sorted(missing)}"
    return out


def plan_text(sid, edit):
    old, new = edit["old"], edit["new"]
    # Check "already applied" FIRST. An append-style edit has `new` containing `old`, so
    # testing `old in text` first would re-fire forever and duplicate the appended text.
    for p in story_files(sid):
        if new in Path(p).read_text(encoding="utf-8"):
            return ("skip", Path(p), "text", old, new, "already applied")
    for p in story_files(sid):
        if old in Path(p).read_text(encoding="utf-8"):
            return ("write", Path(p), "text", old, new, None)
    return ("fail", None, "text", old, new,
            f"`old` not found in any band file for {sid}")


def plan_json(sid, edit, tags, items):
    kind, old, new = edit["kind"], edit["old"], edit["new"]
    if kind == "prompt":
        loc = edit.get("locator", "")
        band = edit.get("band")
        for i, e in enumerate(items[sid].get("discussion", [])):
            if e[0] == loc and e[1] == band:
                if e[2] == old:
                    return ("json", (sid, "discussion", i, 2), "prompt", old, new, None)
                if e[2] == new:
                    return ("skip", None, "prompt", old, new, "already applied")
                return ("fail", None, "prompt", old, new, f"discussion text mismatch: {e[2]!r}")
        for i, e in enumerate(items[sid].get("measurement", [])):
            if e[0] != loc:
                continue
            # agents sometimes wrap an option in literal quotes as a disambiguator
            for cand in (old, old.strip("\"'")):
                if e[1] == cand:
                    return ("json", (sid, "measurement", i, 1), "prompt", old, new, None)
                if cand in e[2]:
                    j = e[2].index(cand)
                    return ("json", (sid, "measurement", i, ("opt", j)), "prompt", old, new, None)
            if e[1] == new or new in e[2]:
                return ("skip", None, "prompt", old, new, "already applied")
            return ("fail", None, "prompt", old, new, f"measurement mismatch: {e[1]!r}")
        return ("fail", None, "prompt", old, new, f"no discussion/measurement entry {loc}@{band}")
    if kind == "tag":
        loc = edit.get("locator")
        key = (sid, loc)
        assert key in TAG_EDITS, f"unplanned tag edit {key}"
        if loc == "C5_inference":
            # the tag stores skills under the bare ordinal key, not the skill's full name
            val = tags[sid]["skills"]
            if val.get("C5") == 1:
                return ("skip", None, "tag", old, new, "already applied")
            return ("tag", (sid, "skills", "C5", 1), "tag", old, new, None)
        val = tags[sid].get(loc)
        if loc == "characters":
            roles = {c[0]: c[2] for c in val}
            if roles.get("Elephant") == "antagonist":
                return ("skip", None, "tag", old, new, "already applied")
            return ("tag", (sid, "characters", "Elephant", "antagonist"), "tag", old, new, None)
        if loc == "moral":
            if val[0] == new:
                return ("skip", None, "tag", old, new, "already applied")
            return ("tag", (sid, "moral", 0, new), "tag", old, new, None)
    return ("fail", None, kind, old, new, f"unsupported edit kind {kind}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    edits = load_edits()
    tags = json.loads(TAGS.read_text())
    items = json.loads(ITEMS.read_text())

    plan, failures = [], []
    for sid in sorted(edits):
        for edit in edits[sid]:
            r = plan_text(sid, edit) if edit["kind"] == "text" \
                else plan_json(sid, edit, tags["tags"], items["items"])
            (failures if r[0] == "fail" else plan).append((sid, r))

    for sid, r in plan:
        status, _, kind, old, new, why = r
        label = "SKIP " if status == "skip" else "APPLY"
        print(f"  {label} {sid:6} {kind:7} {why or ''}")
        print(f"        old: {old[:90]!r}")
    for sid, r in failures:
        print(f"  FAIL  {sid:6} {r[2]:7} {r[5]}")

    if failures:
        print(f"\n{len(failures)} edit(s) could not be placed — refusing to write anything.")
        return 1
    if args.dry_run:
        by = {}
        for _, r in plan:
            by[r[0]] = by.get(r[0], 0) + 1
        print(f"\ndry run: {by.get('write', 0)} text file(s), {by.get('json', 0)} item/prompt "
              f"record(s), {by.get('tag', 0)} tag record(s), {by.get('skip', 0)} already applied "
              f"— nothing written")
        return 0

    for sid, (status, target, kind, old, new, _) in plan:
        if status == "skip":
            continue
        if status == "write":
            t = target.read_text(encoding="utf-8")
            target.write_text(t.replace(old, new, 1), encoding="utf-8")
        elif status == "json":
            s, coll, i, slot = target
            if isinstance(slot, tuple):        # option inside a measurement item
                items["items"][s]["measurement"][i][2][slot[1]] = new
            else:
                items["items"][s][coll][i][slot] = new
        elif status == "tag":
            s, field, a, *rest = target
            if field == "characters":
                for c in tags["tags"][s]["characters"]:
                    if c[0] == a:
                        c[2] = rest[0]
            elif field == "skills":
                tags["tags"][s]["skills"][a] = rest[0]
            elif field == "moral":
                tags["tags"][s]["moral"][a] = rest[0]

    TAGS.write_text(json.dumps(tags, indent=2, ensure_ascii=False) + "\n")
    ITEMS.write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n")
    print(f"\napplied {len([p for p in plan if p[1][0]!='skip'])} edit(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
