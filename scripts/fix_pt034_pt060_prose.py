"""Two prose defects found reading the two stories the served set gained (PT034, PT060).

Both are *served content* — the band file a child actually reads — so worse than any
draft defect.

PT034, BOTH bands: the kind hermitage parrot explains ITSELF as the one that was
"taught to be cruel" / "taught to deceive". The source has the parrot relate its own
life (it is the kindly one, raised by holy men) and leaves the reader to draw the
contrast with the hunter-raised chick that shouts "Kill him!". As adapted, both
tellings name the wrong parrot, which deletes the story's point. The 4-9 telling is
the served one (max_age 9, so the 9+ telling is unreachable today); the 9+ is fixed
too, since it is one word away from being served.

PT060, 9+: "the sun, the moon, the wind, or the mountain" — the moon is invented. The
source chain is sun -> cloud -> wind -> mountain -> mouse, and the 4-9 telling has the
cloud. The moon appears in Ryder only in the child-marriage verse, which the adaptation
drops. An invented suitor that is then never summoned.

Idempotent and guarded: re-running asserts and refuses rather than no-op'ing.

    python3 scripts/fix_pt034_pt060_prose.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from readability import metrics  # noqa: E402
from adapt import BANDS  # noqa: E402  — the real thresholds; HANDOVER §7's table is stale

ADAPTED = ROOT / "corpus" / "panchatantra_adapted.json"

# (story_id, band, old, new) — each `old` must be present or the run refuses.
EDITS = [
    (
        "PT034", "4-9",
        'The parrot explained, "I was once like that parrot. I was taught to be cruel. '
        'That\'s why I acted like that."',
        'The parrot said, "I was raised among holy men. So I am kind. The other parrot '
        'was raised among hunters. So he was taught to be cruel."',
    ),
    (
        "PT034", "9+",
        "The parrot explained that its own life had been shaped by its education. It had "
        "learned to mimic the voices of its surroundings and had been taught to deceive.",
        "The parrot explained that its own life had been shaped by its education. It had "
        "grown up among holy men and learned gentleness. The other parrot had grown up "
        "among hunters and learned only cruelty.",
    ),
    (
        "PT060", "9+",
        "the sun, the moon, the wind, or the mountain",
        "the sun, the cloud, the wind, or the mountain",
    ),
]

BAND_LIMITS = {b: (*s["fk_grade"], *s["words_per_sentence"]) for b, s in BANDS.items()}


def story_file(sid: str, band: str) -> Path:
    hits = sorted((ROOT / "corpus" / "age" / band).glob(f"{sid}-*.txt"))
    assert len(hits) == 1, f"{sid} {band}: expected 1 file, found {hits}"
    return hits[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    texts, files = {}, {}
    for sid, band, old, new in EDITS:
        path = story_file(sid, band)
        files[(sid, band)] = path
        text = texts.get(path, path.read_text())
        assert old in text, (
            f"{sid} {band}: the text to fix is not present — already applied? Refusing."
        )
        texts[path] = text.replace(old, new)

    for path, text in texts.items():
        sid, band = next(k for k, v in files.items() if v == path)
        fk_lo, fk_hi, wps_lo, wps_hi = BAND_LIMITS[band]

        def overshoot(m):
            return (max(0.0, fk_lo - m["fk_grade"], m["fk_grade"] - fk_hi)
                    + max(0.0, wps_lo - m["words_per_sentence"],
                          m["words_per_sentence"] - wps_hi))

        before, after = metrics(path.read_text()), metrics(text)
        was, now = overshoot(before), overshoot(after)
        print(f"{sid} {band}: {before['words']}w fk={before['fk_grade']} "
              f"wps={before['words_per_sentence']}  ->  {after['words']}w "
              f"fk={after['fk_grade']} wps={after['words_per_sentence']}")
        print(f"    target fk {fk_lo}-{fk_hi}, wps {wps_lo}-{wps_hi} — "
              f"overshoot {was:.2f} -> {now:.2f}")
        # A telling already inside its target must stay inside it; one already outside
        # may be fixed but must not be pushed further out. (Several tellings sit a few
        # hundredths over — pre-existing, and adapt.py --check's business, not this fix's.)
        assert now <= max(was, 0.0), f"{sid} {band}: this edit worsens readability"

    if args.dry_run:
        print("dry run — nothing written")
        return

    for path, text in texts.items():
        path.write_text(text)

    doc = json.loads(ADAPTED.read_text())
    for path, text in texts.items():
        sid, band = next(k for k, v in files.items() if v == path)
        s = next(x for x in doc["stories"] if x["story_id"] == sid)
        s["adapted"][band]["text"] = text
        s["adapted"][band]["metrics"] = metrics(text)
    ADAPTED.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")

    for (sid, band), path in files.items():
        mpath = ROOT / "corpus" / "age" / band / "manifest.json"
        man = json.loads(mpath.read_text())
        rows = man if isinstance(man, list) else man.get("files", man.get("stories", []))
        for r in rows:
            if r.get("story_id") == sid:
                m = metrics(texts[path])
                r.update({k: m.get(k, r.get(k)) for k in r if k in m})
        mpath.write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n")

    print("wrote:", *[str(p.relative_to(ROOT)) for p in files.values()], "adapted json, manifests")


if __name__ == "__main__":
    main()
