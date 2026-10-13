"""Trim PT022's 9+ telling back to the fish fable — it was two stories in one.

Root cause is the nested-frame structure, not an adaptation slip. PT022's SOURCE
chapter is the fish fable (Forethought/Readywit/Fatalist) with the plover tale woven
on as a tail — "'My dear,' said the plover, 'why do you think me like Fatalist?'".
That plover tale also stands alone as PT020. The 4-9 adapter trimmed to the fable;
the 9+ adapter adapted the whole chapter, so the served 9+ text was two stories with
a blended moral, and carried the line "I'll burn myself".

This rewrites the 9+ telling to the fable alone, matching the 4-9 telling's scope,
with the fable's moral. The original is kept in corpus/age/9+/_rejected/ as an audit
trail. Idempotent: re-running rewrites the same text.

NOTE: even trimmed, this telling is ~145 words — well under the 500-1500 word 9+
target. The untrimmed one was 384, already under target, so the length gap is
pre-existing and needs a real 9+ re-adaptation of the fable, not just this trim.

    python3 scripts/fix_pt022_graft.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from readability import metrics  # noqa: E402

TXT = next((ROOT / "corpus" / "age" / "9+").glob("PT022-*.txt"))
ADAPTED = ROOT / "corpus" / "panchatantra_adapted.json"
MANIFEST = ROOT / "corpus" / "age" / "9+" / "manifest.json"
REJECTED = ROOT / "corpus" / "age" / "9+" / "_rejected"

TRIMMED = '''Forethought, Readywit, and Fatalist

In a great lake lived three full-grown fishes. Forethought, Readywit, and Fatalist were their names. One day, Forethought overheard fishermen talking about fishing in the lake the next day. He thought, "This is bad news. They'll definitely come here tomorrow or the day after." So, he called Readywit and Fatalist.

Readywit said, "I've lived here for a long time. I won't move just because of rumors. If fishermen come, I'll think of a plan to protect myself." Fatalist said, "There are many lakes. Maybe they won't come here at all. We shouldn't leave our birthplace just because of gossip."

Forethought realized they wouldn't listen, so he left the lake. The next day, fishermen came with nets and caught all the fish. Readywit played dead to escape, but Fatalist got stuck in the net. The fishermen hit him with clubs, and he died.

Moral: Think ahead and be prepared, or you might not survive.
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    old = TXT.read_text()
    assert "plover" in old.lower(), "PT022 9+ no longer contains the graft — nothing to fix"
    m = metrics(TRIMMED)

    print(f"9+ telling: {len(old.split())} words -> {m['words']} words")
    print(f"  contains 'plover' after trim: {'plover' in TRIMMED.lower()}")
    print(f"  contains 'burn myself' after trim: {'burn myself' in TRIMMED.lower()}")
    print(f"  metrics: wps={m['words_per_sentence']} fk={m['fk_grade']} "
          f"(9+ target: wps 9-16, fk 3.5-6.5)")
    print(f"  length {m['words']} vs 9+ target 500-1500 -> UNDER (pre-existing)")
    if args.dry_run:
        print("dry run — nothing written")
        return

    REJECTED.mkdir(parents=True, exist_ok=True)
    shutil.copy(TXT, REJECTED / TXT.name)
    TXT.write_text(TRIMMED)

    doc = json.loads(ADAPTED.read_text())
    s = next(x for x in doc["stories"] if x["story_id"] == "PT022")
    s["adapted"]["9+"]["text"] = TRIMMED
    s["adapted"]["9+"]["metrics"] = m
    ADAPTED.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

    man = json.loads(MANIFEST.read_text())
    rows = man if isinstance(man, list) else man.get("files", man.get("stories", []))
    for r in rows:
        if r.get("story_id") == "PT022":
            r.update({k: m[k] for k in r if k in m})
    MANIFEST.write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n")

    print(f"wrote {TXT.name}, panchatantra_adapted.json, manifest.json")
    print(f"original kept at {REJECTED / TXT.name}")


if __name__ == "__main__":
    main()
