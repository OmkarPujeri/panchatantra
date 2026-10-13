#!/usr/bin/env python3
"""Integrity checks for the built corpus. Run after any rebuild.

    python3 scripts/check_corpus.py

Exits non-zero if anything fails. Checks are independent; each reports its own
result so a failure names the problem rather than just going red.
"""
import csv
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "..", "corpus")
STORIES = os.path.join(CORPUS, "stories")

# characters this edition legitimately uses
ALLOWED_NON_ASCII = set("—–’‘“”…èéôà•♦¶§°½¼¾⅓⅔")

# A story ends by handing off to the story nested inside it. Because verses and
# paragraphs are separate blocks, the phrase can be the whole final line.
HANDOFF_ENDINGS = tuple(e.lower() for e in (
    "story of", "tale of", "called", "I will tell you", "and the rest of it.",
    'and the rest of it."', "July, 1925", "told", "told three stories in one,",
))

# Verified against the printed page, not a defect. PT035's moral verse is left
# hanging in the 1925 printing itself -- the scan shows "Better the sensible enemy
# than" immediately followed by the next story's heading. Nothing is missing from
# the corpus; the edition prints it that way.
KNOWN_SOURCE_QUIRKS = {
    "PT035": "verse left hanging in the 1925 printing (checked against scan p.203)",
}

STRAY_MARKUP = {
    "wiki template": re.compile(r"\{\{[^}]{0,80}\}\}"),
    "wikilink": re.compile(r"\[\[[^\]]{0,80}\]\]"),
    "html tag": re.compile(r"</?(div|span|p|br|i|b|sup|table|tr|td)\b[^>]{0,40}>"),
    "html entity": re.compile(r"&(nbsp|amp|quot|lt|gt|#\d+);"),
    "page marker": re.compile(r"<<<PAGE"),
    "section tag": re.compile(r"<section\b|</?noinclude"),
    "djvu ref": re.compile(r"Panchatantra\.djvu"),
}

failures = []
notes = []


def check(name, ok, detail=""):
    print(f"  [{'ok ' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    if not ok:
        failures.append(f"{name}: {detail}")


def parse_toc(front):
    i = front.find("TABLE OF CONTENTS")
    j = front.find("INTRODUCTIONS", i)
    if i == -1:
        return {}
    out, buf = {}, []
    for line in (l.strip() for l in front[i:j if j > i else len(front)].split("\n")):
        if not line or line in ("page", "TABLE OF CONTENTS"):
            continue
        if re.fullmatch(r"\d{1,3}", line):
            if buf:
                nm = re.sub(r"\s+", " ", " ".join(buf)).strip()
                if "—" not in nm and not nm.isupper():
                    out[nm.lower()] = int(line)
            buf = []
        elif line.startswith("BOOK "):
            buf = []
        else:
            buf.append(line)
    return out


def main():
    manifest = json.load(open(os.path.join(CORPUS, "manifest.json")))
    files = sorted(glob.glob(os.path.join(STORIES, "*.txt")))
    bodies = {
        os.path.basename(f).split("-")[0]: open(f).read() for f in files
    }
    complete = open(os.path.join(CORPUS, "panchatantra_complete.txt")).read()

    print("\nmanifest")
    ids = [r["story_id"] for r in manifest]
    check("ids unique", len(ids) == len(set(ids)), f"{len(ids)} records")
    check("every record has a file", set(ids) == set(bodies),
          f"manifest {len(set(ids))}, files {len(set(bodies))}")
    check("no zero-word stories", all(r["words"] > 0 for r in manifest))
    bad_pages = [r["story_id"] for r in manifest
                 if r.get("start_page") and r.get("end_page")
                 and r["start_page"] > r["end_page"]]
    check("start_page <= end_page", not bad_pages, str(bad_pages))
    check("word counts match files",
          all(r["words"] == len(bodies[r["story_id"]].split("\n\n", 1)[-1].split())
              for r in manifest))

    print("\npage numbers against the book's own table of contents")
    toc = parse_toc(bodies.get("PT090", ""))
    mism = [(r["story_id"], r["title_short"], r["start_page"], toc[r["title_short"].lower()])
            for r in manifest
            if r["title_short"].lower() in toc
            and r["start_page"] != toc[r["title_short"].lower()]]
    check("start_page matches TOC", not mism, f"{len(toc)} TOC entries; {mism}")
    check("TOC entry count", len(toc) >= 85, f"parsed {len(toc)}")

    print("\ntext integrity")
    check("no wiki templates", not any(STRAY_MARKUP["wiki template"].search(b)
                                       for b in bodies.values()))
    check("no wikilinks", not any(STRAY_MARKUP["wikilink"].search(b)
                                  for b in bodies.values()))
    check("no html tags", not any(STRAY_MARKUP["html tag"].search(b)
                                  for b in bodies.values()))
    check("no html entities", not any(STRAY_MARKUP["html entity"].search(b)
                                      for b in bodies.values()))
    check("no page markers in stories", not any(STRAY_MARKUP["page marker"].search(b)
                                                for b in bodies.values()))
    check("no section tags", not any(STRAY_MARKUP["section tag"].search(b)
                                     for b in bodies.values()))
    check("no djvu refs in stories", not any(STRAY_MARKUP["djvu ref"].search(b)
                                             for b in bodies.values()))
    check("no markers in complete text",
          not STRAY_MARKUP["page marker"].search(complete))

    stray = sorted({c for b in bodies.values() for c in b
                    if ord(c) > 126 and c not in ALLOWED_NON_ASCII})
    check("no unexpected characters", not stray, repr(stray))

    print("\nstructure")
    mid = []
    for sid, b in sorted(bodies.items()):
        if sid in KNOWN_SOURCE_QUIRKS:
            continue
        last = b.rstrip().split("\n")[-1].strip().lower()
        if any(last.endswith(e) for e in HANDOFF_ENDINGS):
            continue
        if last and last[-1] not in '.!?"\':;)—”’':
            mid.append((sid, b.rstrip().split("\n")[-1].strip()[-60:]))
    check("no file ends mid-sentence", not mid, str(mid[:4]))
    for sid, why in KNOWN_SOURCE_QUIRKS.items():
        notes.append(f"{sid}: {why}")

    stranded = [sid for sid, b in bodies.items()
                if re.search(r"\n+BOOK (I|II|III|IV|V)\s*$", b)]
    check("no stranded book divider", not stranded, str(stranded))

    print("\ncoverage")
    placed = sum(len(b.split("\n\n", 1)[-1].split()) for b in bodies.values())
    total = len(complete.split())
    # the complete text carries a 5-line provenance header the stories do not
    header = len(complete.split("\n\n")[0].split())
    check("story files cover the complete text",
          abs((total - header) - placed) <= 30,
          f"complete {total - header:,} vs stories {placed:,}")

    print("\ncsv")
    rows = list(csv.DictReader(open(os.path.join(CORPUS, "panchatantra_stories.csv"))))
    check("csv row count matches manifest", len(rows) == len(manifest),
          f"{len(rows)} rows")
    check("csv parses cleanly", all(r.get("story_id") for r in rows))

    print()
    for n in notes:
        print("note:", n)
    if failures:
        print(f"FAILED: {len(failures)} check(s)")
        for f in failures:
            print("  -", f)
        return 1
    print(f"\nAll checks passed. {len(manifest)} stories, {placed:,} words.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
