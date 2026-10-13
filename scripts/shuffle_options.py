"""De-bias MCQ answer position in the authored item bank.

Model-drafted MCQs clustered the correct answer at position 0 (65% of draft rows:
{0:136, 1:62, 2:10, 3:2}). `correct` is an *index*, so that is directly gameable —
pick the first option every time and score 65% without reading.

The shuffle is a pure function of the option *content*: options are sorted into a
canonical order, then permuted with a seed derived from the prompt. So it is
idempotent (re-running is a no-op) and independent of the order it finds, which
means reviewing the authored file reviews exactly what gets served.

Only `_draft` entries are touched. The reviewed pilot rows were human-authored and
carry no position bias ({0:4, 1:22, 2:6} across 32 rows).

    python3 scripts/shuffle_options.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "data" / "story_items_authored.json"


def shuffle_row(sid, row):
    """[skill, prompt, options, correct, diff, age] -> same, with options permuted."""
    skill, prompt, options, correct, diff, age = row
    canon = sorted(options)                       # order-independent starting point
    random.Random(f"{sid}|{prompt}").shuffle(canon)
    return [skill, prompt, canon, canon.index(options[correct]), diff, age]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="report, write nothing")
    args = ap.parse_args()

    doc = json.loads(PATH.read_text())
    before, after = Counter(), Counter()
    touched = 0
    for sid, entry in doc["items"].items():
        if not entry.get("_draft"):
            continue
        for i, row in enumerate(entry["measurement"]):
            before[row[3]] += 1
            new = shuffle_row(sid, row)
            after[new[3]] += 1
            entry["measurement"][i] = new
            touched += 1

    print(f"shuffled {touched} draft measurement rows")
    print(f"  before: {dict(sorted(before.items()))}")
    print(f"  after:  {dict(sorted(after.items()))}")
    if args.dry_run:
        print("dry run — nothing written")
        return
    PATH.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {PATH}")


if __name__ == "__main__":
    main()
