#!/usr/bin/env python3
"""Export the corpus to JSON for downstream pipelines.

Writes:
    corpus/panchatantra.json        all stories, full metadata + text
    corpus/bands/band-4-9.json      only stories curated as suitable for 4-9
    corpus/bands/band-9+.json       only stories curated as suitable for 9+
    corpus/panchatantra.jsonl       one story per line (same records, streaming)

Each story record carries both `text` (the full chapter as published) and
`fable_text` (the chapter trimmed to just the fable, where the closing formula
made that possible). Use `fable_text` when it differs -- the chapter files contain
frame narrative from the enclosing story, which is not part of this fable.

    python3 scripts/export_json.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
STORIES = os.path.join(ROOT, "corpus", "stories")
CORPUS = os.path.join(ROOT, "corpus")
DATA = os.path.join(ROOT, "data")

sys.path.insert(0, HERE)
from curate import fable_only  # noqa: E402

META = {
    "title": "The Panchatantra",
    "recension": "Purnabhadra's, 1199 CE (Panchakhyanaka)",
    "translator": "Arthur W. Ryder",
    "publisher": "University of Chicago Press, 1925",
    "source": "https://en.wikisource.org/wiki/Index:Panchatantra.djvu",
    "rights": (
        "Public domain. The translation is out of copyright in the US and India "
        "(Ryder died 1938). Adaptations and translations made from it are new "
        "copyrightable works owned by whoever makes them."
    ),
    "provenance": "corpus/README.md",
}

# The readability targets that ship in the exported JSON. These are the values the
# corpus is currently shipped against (ADAPTATION_BRIEF.md §2), NOT adapt.py's BANDS,
# which are the *enforced floor* and disagree with them (FK 4.0 vs 4.8, syllables 1.38
# vs 1.42, word floor 200 vs 70). HANDOVER §7: that disagreement is unresolved and must
# not be decided silently by a re-run — so the numbers are pinned here and exporting
# keeps them. When §7 is decided, align this, the brief, and adapt.BANDS together.
BAND_TARGETS = {
    "4-9": {
        "label": "children aged 4 to 9",
        "fk_grade": [1.0, 4.0],
        "words_per_sentence": [5, 10],
        "max_syllables_per_word": 1.38,
        "word_count": [200, 700],
    },
    "9+": {
        "label": "children aged 9 and older",
        "fk_grade": [3.5, 6.5],
        "words_per_sentence": [9, 16],
        "max_syllables_per_word": 1.55,
        "word_count": [500, 1500],
    },
}

# How to use the record fields, for whoever writes the consuming pipeline.
NOTES = {
    "text": "the chapter exactly as published; contains frame narrative around the fable",
    "fable_text": "the chapter trimmed to the fable, where the closing formula allowed it",
    "scoped_to_fable": "true when fable_text is a genuine trim, false when it equals text",
    "curation.bands": "which age bands this story may be adapted for, per data/curation.json",
    "curation.scoped_to_fable": "false means the content verdict scanned the whole chapter and is less reliable",
}


def load_story(sid, filename):
    raw = open(os.path.join(STORIES, filename), encoding="utf-8").read()
    parts = raw.split("\n\n", 1)
    text = (parts[1] if len(parts) > 1 else raw).strip()
    scoped, was_scoped = fable_only(text)
    return text, scoped.strip(), was_scoped


def build():
    manifest = {r["story_id"]: r for r in
                json.load(open(os.path.join(CORPUS, "manifest.json")))}
    curation = json.load(open(os.path.join(DATA, "curation.json")))

    stories = []
    for filename in sorted(os.listdir(STORIES)):
        if not filename.endswith(".txt"):
            continue
        sid = filename.split("-")[0]
        m = manifest[sid]
        text, fable, scoped = load_story(sid, filename)
        c = curation.get(sid, {})
        stories.append({
            "story_id": sid,
            "title": m["title_short"],
            "book": m["book"],
            "book_name": m["book_name"],
            "source_file": filename,
            "printed_page": m.get("toc_page") or m.get("start_page"),
            "word_count": len(text.split()),
            "fable_word_count": len(fable.split()),
            "scoped_to_fable": scoped,
            "curation": {
                "verdict": c.get("verdict"),
                # A story with no curation entry (front matter, e.g. PT090) gets NO bands,
                # so it is excluded from every band file — never silently defaulted to both.
                "bands": c.get("bands", []),
                "reason": c.get("reason"),
                "scoped_to_fable": c.get("scoped_to_fable"),
            },
            "text": text,
            "fable_text": fable,
        })

    doc = {
        "meta": dict(META, story_count=len(stories),
                     word_count=sum(s["word_count"] for s in stories)),
        "field_notes": NOTES,
        "band_targets": BAND_TARGETS,
        "stories": stories,
    }
    return doc


def main():
    doc = build()
    out = os.path.join(CORPUS, "panchatantra.json")
    json.dump(doc, open(out, "w"), ensure_ascii=False, indent=1)

    with open(os.path.join(CORPUS, "panchatantra.jsonl"), "w") as f:
        for s in doc["stories"]:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    band_dir = os.path.join(CORPUS, "bands")
    os.makedirs(band_dir, exist_ok=True)
    counts = {}
    for band in BAND_TARGETS:
        picked = [s for s in doc["stories"]
                  if band in (s["curation"]["bands"] or [])]
        json.dump({"meta": dict(META, band=band, story_count=len(picked),
                                word_count=sum(s["word_count"] for s in picked)),
                   "field_notes": NOTES,
                   "band_targets": {band: doc["band_targets"][band]},
                   "stories": picked},
                  open(os.path.join(band_dir, f"band-{band}.json"), "w"),
                  ensure_ascii=False, indent=1)
        counts[band] = len(picked)

    print(f"corpus/panchatantra.json      {len(doc['stories'])} stories, "
          f"{doc['meta']['word_count']:,} words")
    print(f"corpus/panchatantra.jsonl     one record per line")
    for band, n in counts.items():
        print(f"corpus/bands/band-{band}.json{' ' * (4 - len(band))} {n} stories")
    scoped = sum(1 for s in doc["stories"] if s["scoped_to_fable"])
    print(f"\n{scoped} of {len(doc['stories'])} records have a trimmed fable_text")
    return 0


if __name__ == "__main__":
    sys.exit(main())
