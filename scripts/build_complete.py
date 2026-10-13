#!/usr/bin/env python3
"""Render the COMPLETE Panchatantra (all 484 printed pages) from Wikisource.

The per-story subpages on Wikisource are an editorial split and one of them
truncates a story early ("The Three-breasted Princess" stops at printed page 474
although the text runs to 479). So the page sequence, not the story split, is the
ground truth for completeness.

Renders the whole <pages> range in chunks through action=parse -- that gives the
same clean transcluded output with no wiki header/nav chrome -- and writes:

    corpus/panchatantra_complete.txt

Requires network. Chunks are cached in source/fullbook/ so re-runs are free.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_corpus import TextExtractor, api, rejoin_pagebreaks, SRC  # noqa: E402

CORPUS = os.path.join(HERE, "..", "corpus")
CHUNK = 40
TOTAL = 484
CACHE = os.path.join(SRC, "fullbook")


def render_range(lo, hi):
    cache = os.path.join(CACHE, f"{lo:03d}-{hi:03d}.html")
    if os.path.exists(cache):
        return open(cache).read()
    d = api({
        "action": "parse", "contentmodel": "wikitext", "prop": "text",
        "format": "json", "formatversion": "2",
        "text": f'<pages index="Panchatantra.djvu" from={lo} to={hi}/>',
    })
    if "parse" not in d:
        print(f"  !! FAILED {lo}-{hi}: {str(d)[:200]}")
        return ""
    h = d["parse"]["text"]
    os.makedirs(CACHE, exist_ok=True)
    open(cache, "w").write(h)
    time.sleep(2.0)
    return h


def to_text(h):
    h = re.sub(r"<style.*?</style>", "", h, flags=re.S)
    ex = TextExtractor()
    ex.feed(h)
    return ex.text()


def main():
    parts = []
    for lo in range(1, TOTAL + 1, CHUNK):
        hi = min(lo + CHUNK - 1, TOTAL)
        t = to_text(render_range(lo, hi))
        parts.append(t)
        print(f"  pages {lo:>3}-{hi:<3} {len(t.split()):>6} words")

    body = "\n\n".join(parts)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    body = rejoin_pagebreaks(body)

    out = os.path.join(CORPUS, "panchatantra_complete.txt")
    os.makedirs(CORPUS, exist_ok=True)
    with open(out, "w") as f:
        f.write(
            "THE PANCHATANTRA\n"
            "Purnabhadra's Recension of 1199 CE\n"
            "Translated by Arthur W. Ryder, University of Chicago Press, 1925\n"
            "Source: en.wikisource.org/wiki/Index:Panchatantra.djvu (proofread, validated)\n"
            "Public domain.\n\n"
        )
        f.write(body)
        f.write("\n")

    print(f"\n{len(body.split()):,} words -> {out}")


if __name__ == "__main__":
    main()
