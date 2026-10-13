#!/usr/bin/env python3
"""Fetch the full proofread text of the Ryder Panchatantra (1925) from Wikisource.

Source: Index:Panchatantra.djvu  -- 484 pages, Purnabhadra's recension of 1199 CE,
translated by Arthur W. Ryder, University of Chicago Press, 1925. Public domain.

Writes source/pages_raw.json  (page number -> raw proofread wikitext)
Requires network. Re-run safe: skips if the file already exists.
"""
import json
import os
import time
import urllib.parse
import urllib.request

API = "https://en.wikisource.org/w/api.php"
PAGE = "Page:Panchatantra.djvu/{}"
TOTAL = 484
BATCH = 50
OUT = os.path.join(os.path.dirname(__file__), "..", "source", "pages_raw.json")


def fetch(titles):
    q = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "titles": "|".join(titles),
        "format": "json",
        "formatversion": "2",
    }
    req = urllib.request.Request(
        API + "?" + urllib.parse.urlencode(q),
        headers={"User-Agent": "PanchatantraAI-research/0.1 (educational corpus build)"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main():
    out = {}
    if os.path.exists(OUT):
        out = json.load(open(OUT))
        print(f"resuming, {len(out)} pages cached")

    todo = [n for n in range(1, TOTAL + 1) if str(n) not in out]
    for i in range(0, len(todo), BATCH):
        chunk = todo[i : i + BATCH]
        titles = [PAGE.format(n) for n in chunk]
        data = fetch(titles)
        by_title = {p["title"]: p for p in data["query"]["pages"]}
        for n, title in zip(chunk, titles):
            p = by_title.get(title, {})
            revs = p.get("revisions")
            out[str(n)] = revs[0]["slots"]["main"]["content"] if revs else ""
        print(f"  {min(i + BATCH, len(todo))}/{len(todo)} fetched")
        time.sleep(0.5)

    json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
    empty = [n for n, v in out.items() if not v.strip()]
    print(f"wrote {OUT}: {len(out)} pages, {len(empty)} empty -> {empty[:20]}")


if __name__ == "__main__":
    main()
