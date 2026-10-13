#!/usr/bin/env python3
"""Rebuild the per-story corpus by slicing the COMPLETE book text.

Why not the Wikisource story subpages: that split loses text (it truncates
"The Three-breasted Princess" at printed page 474 and drops the Book IV frame
narrative). Slicing the complete text at each story's heading instead gives a
partition where every page of the book lands in exactly one file, with nothing
dropped and nothing duplicated.

Writes corpus/stories/<id>-<slug>.txt, corpus/panchatantra_paged.txt and
refreshes manifest.json / panchatantra_stories.csv with page ranges.
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_complete import CORPUS, SRC, TOTAL, render_range  # noqa: E402
from build_corpus import TextExtractor, rejoin_pagebreaks, slug  # noqa: E402

PAGE_RE = re.compile(r"<<<PAGE [^>]*>>>")      # strips any marker, incl. "Jacket"
PAGE_NUM_RE = re.compile(r"<<<PAGE (\d+)>>>")  # extracts printed page numbers only


class PageAwareExtractor(TextExtractor):
    """Same as TextExtractor but emits a <<<PAGE n>>> marker per printed page."""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "ws-pagenum" in (a.get("class") or ""):
            n = a.get("data-page-number")
            if n:
                self.parts.append(f"\n\n<<<PAGE {n}>>>\n")
            return
        super().handle_starttag(tag, attrs)


def paged_text():
    parts = []
    for lo in range(1, TOTAL + 1, 40):
        hi = min(lo + 39, TOTAL)
        h = re.sub(r"<style.*?</style>", "", render_range(lo, hi), flags=re.S)
        ex = PageAwareExtractor()
        ex.feed(h)
        parts.append(ex.text())
    t = re.sub(r"\n{3,}", "\n\n", "\n\n".join(parts)).strip()
    return rejoin_pagebreaks(t)


def toc_pages(bodies):
    """Printed page numbers from the book's own table of contents (in PT090).

    The computed start page is the page the story's heading appears on, which for
    the five frame stories is the book's divider page -- two pages before the
    chapter proper. The printed TOC gives the number a citation would use, so it
    wins where it has an entry. Verified: 84 of 89 agree exactly, the other five
    differ by exactly the divider offset.
    """
    t = bodies.get("PT090", "")
    i = t.find("TABLE OF CONTENTS")
    j = t.find("INTRODUCTIONS", i)
    if i == -1:
        return {}
    out, buf = {}, []
    for line in (l.strip() for l in t[i:j if j > i else len(t)].split("\n")):
        if not line or line in ("page", "TABLE OF CONTENTS"):
            continue
        if re.fullmatch(r"\d{1,3}", line):
            if buf:
                name = re.sub(r"\s+", " ", " ".join(buf)).strip()
                if "—" not in name and not name.isupper():
                    out[name.lower()] = int(line)
            buf = []
        elif line.startswith("BOOK "):
            buf = []
        else:
            buf.append(line)
    return out


def apply_corrections(bodies, order):
    """Fix the places where a heading partition misattributes text.

    Panchatantra is a frame narrative, so the frame of a story resumes after each
    story nested inside it ends. Slicing on headings glues that resumption onto the
    end of the nested (child) story instead of the frame that owns it. For most
    stories that is a line or two of transition and reads fine; these two regions
    are materially wrong.

    1. "The Three-breasted Princess" frames "The Fiend Who Washed His Feet". The
       princess's entire second half landed in the child's slice.
    2. Book V's back matter (colophon, jacket blurb, author note) landed inside
       the last story.
    """
    # --- 1. move the princess's second half back out of the fiend story -------
    fiend = bodies["PT087"]
    start = fiend.find("After listening to this, the king summoned the Brahmans")
    end = fiend.find("Then the gold-finder said:")
    if start == -1 or end == -1 or end < start:
        raise SystemExit(
            "PT088 correction failed: boundary markers not found in PT087. "
            "The source text may have changed -- inspect before trusting the build."
        )
    bodies["PT088"] = (
        bodies["PT088"].rstrip() + "\n\n" + fiend[start:end].strip()
    )
    bodies["PT087"] = fiend[:start].rstrip() + "\n\n" + fiend[end:].strip()

    # --- 2. move Book V back matter out of the last story ---------------------
    tail = bodies["PT087"]
    cut = tail.find("PRINTED IN THE U.S.A.")
    if cut != -1:
        bodies["PT087"] = tail[:cut].rstrip()
        back = tail[cut:]
        if "PT090" in bodies:
            bodies["PT090"] = bodies["PT090"].rstrip() + "\n\n" + back.strip()

    # --- 3. drop stranded book-divider lines ----------------------------------
    # Each book's divider page ("BOOK II") sits after the previous book's closing
    # verse, so the partition leaves it stranded at the end of the previous book's
    # last story instead of at the start of the frame story it belongs to.
    for sid, body in bodies.items():
        body = re.sub(r"\n+BOOK (I|II|III|IV|V)\s*$", "", body)
        body = re.sub(r"\n+_{6,}\s*$", "", body)  # rule above the colophon
        bodies[sid] = body

    # --- 4. collapse the doubled title on the five frame stories --------------
    # A book's divider page prints "BOOK IV / LOSS OF GAINS" and the chapter then
    # opens with "BOOK IV / LOSS OF GAINS" again, so the slice leads with a
    # duplicate title. Drop the leading copy, keep "BOOK n / TITLE".
    for sid, body in bodies.items():
        body = re.sub(
            r"\A[A-Z][A-Z\s,'\-]{3,}\n\n(?=BOOK (?:I|II|III|IV|V)\b)", "", body
        )
        bodies[sid] = body

    for sid, body in bodies.items():
        bodies[sid] = re.sub(r"\n{3,}", "\n\n", body).strip()


def main():
    text = paged_text()
    os.makedirs(os.path.join(CORPUS, "stories"), exist_ok=True)

    manifest = json.load(open(os.path.join(CORPUS, "manifest.json")))
    for r in manifest:
        r["title_short"] = r["title"].split("/")[-1]

    # locate each story by the first standalone-line occurrence of its heading
    marks = []
    for r in manifest:
        head = r["title_short"].upper()
        m = re.search(r"(?m)^" + re.escape(head) + r"\s*$", text)
        marks.append((m.start() if m else 0, r))
    marks.sort(key=lambda t: t[0])

    def page_at(idx):
        p = PAGE_NUM_RE.findall(text[:idx])
        return int(p[-1]) if p else None

    for i, (pos, r) in enumerate(marks):
        r["start_page"] = page_at(pos) or (marks[i - 1][1].get("start_page") if i else None)
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        r["end_page"] = page_at(end) or r["start_page"]

    bodies = {}
    for i, (pos, r) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        body = PAGE_RE.sub("", text[pos:end])
        bodies[r["story_id"]] = re.sub(r"\n{3,}", "\n\n", body).strip()

    apply_corrections(bodies, [r for _, r in marks])

    # prefer the printed TOC page number where the book has one
    toc = toc_pages(bodies)
    for _, r in marks:
        r["toc_page"] = toc.get(r["title_short"].lower())  # None where absent
        if r["toc_page"]:
            r["start_page"] = r["toc_page"]

    for _, r in marks:
        body = rejoin_pagebreaks(bodies[r["story_id"]])
        r["words"] = len(body.split())
        r["chars"] = len(body)
        with open(os.path.join(CORPUS, "stories", f"{r['story_id']}-{slug(r['title_short'])}.txt"), "w") as f:
            f.write(f"{r['title_short']}\n{'=' * len(r['title_short'])}\n\n{body}\n")

    with open(os.path.join(CORPUS, "panchatantra_paged.txt"), "w") as f:
        f.write(text + "\n")

    # rewrite the manifest in reading order (the slice order), not the order
    # build_corpus happened to emit
    ordered = [r for _, r in marks]
    json.dump(ordered, open(os.path.join(CORPUS, "manifest.json"), "w"),
              indent=1, ensure_ascii=False)
    with open(os.path.join(CORPUS, "panchatantra_stories.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ordered[0]))
        w.writeheader()
        w.writerows(ordered)

    covered = sum(r["words"] for r in ordered)
    print(f"{len(ordered)} stories, {covered:,} words placed")
    print(f"{len(text.split()):,} words in the complete text")
    short = sorted(ordered, key=lambda r: r["words"])[:5]
    print("shortest:", [(r["story_id"], r["words"]) for r in short])


if __name__ == "__main__":
    main()
