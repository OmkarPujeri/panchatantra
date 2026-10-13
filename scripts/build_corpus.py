#!/usr/bin/env python3
"""Build the Panchatantra corpus from the fetched Wikisource data.

Fetches each story subpage *rendered* (action=parse) so the wiki transclusion
engine resolves the nested / frame-story boundaries for us, converts the HTML to
plain text, and writes:

    corpus/stories/<NN>-<slug>.txt   one file per story, reading order
    corpus/panchatantra_full.txt     the whole book, concatenated
    corpus/manifest.json             id, book, title, pages, words, source
    corpus/panchatantra_stories.csv  same, for Excel

Source: Ryder 1925, Purnabhadra's recension. Public domain.
"""
import csv
import html
import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

API = "https://en.wikisource.org/w/api.php"
ROOT = "The Panchatantra (Purnabhadra's Recension of 1199 CE)"
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "source")
CORPUS = os.path.join(HERE, "..", "corpus")
UA = {"User-Agent": "PanchatantraAI-research/0.1 (educational corpus build)"}

SKIP_CLASSES = ("mw-editsection", "noprint", "ws-noexport", "reference")
SKIP_TAGS = ("style", "script", "link", "meta", "sup")
BLOCK_TAGS = ("p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "hr")
VOID = {"br", "hr", "img", "link", "meta", "input"}


class TextExtractor(HTMLParser):
    """HTML -> plain text.

    Drops whole subtrees of wiki chrome (the header/nav block carries class
    ws-noexport, plus edit links and footnote refs) using a depth marker rather
    than a running counter, so one unbalanced tag inside a skipped subtree cannot
    silently swallow the rest of the page.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.depth = 0
        self.skip_until = None  # element depth to unwind to when the skip ends

    @staticmethod
    def _skip_here(tag, attrs):
        cls = dict(attrs).get("class") or ""
        return tag in SKIP_TAGS or any(c in cls for c in SKIP_CLASSES)

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.depth += 1
        if self.skip_until is not None:
            return
        if tag not in VOID and self._skip_here(tag, attrs):
            self.skip_until = self.depth
            return
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_startendtag(self, tag, attrs):
        if self.skip_until is None and tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.skip_until is not None:
            if self.depth == self.skip_until:
                self.skip_until = None
            self.depth -= 1
            return
        self.depth -= 1
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.skip_until is None:
            self.parts.append(data)

    def text(self):
        t = "".join(self.parts)
        t = t.replace(" ", " ")
        t = re.sub(r"[ \t]+", " ", t)
        t = re.sub(r" *\n *", "\n", t)
        t = re.sub(r"\n{3,}", "\n\n", t)
        return normalize_text(t.strip())


def normalize_text(t):
    """Normalise characters that the transcription left inconsistent.

    - NFC first, so combining forms compare equal to precomposed ones
    - CYRILLIC SMALL LETTER IE WITH GRAVE -> e with grave. The transcriber typed
      the wrong character in "learned" (PT004); it is a typo, not Sanskrit.
    - em space and en space -> ordinary space
    - curly apostrophes stay (they are correct in this edition); curly double
      quotes are left alone too
    """
    t = unicodedata.normalize("NFC", t)
    t = t.replace("ѐ", "è")  # ѐ -> è
    t = t.replace(" ", " ").replace(" ", " ")
    t = t.replace(" ", " ")
    return t


def rejoin_pagebreaks(text):
    """Rejoin paragraphs that a printed page break split mid-sentence.

    A page turn leaves the two halves as separate blocks, so a sentence reads
    "...his throat pinched with hunger," / "and wandered into the city...".
    Only join when it is unambiguous: the left side ends in a comma/semicolon/
    colon, or both sides start with a lowercase letter. Verse lines are left
    alone -- they end in punctuation or are capitalised, so they never match.
    """
    paras = text.split("\n\n")
    out = []
    for p in paras:
        if out:
            prev = out[-1].rstrip()
            nxt = p.lstrip()
            if prev and nxt:
                if (prev[-1] in ",;:" and nxt[0].islower()) or (
                    prev[-1].islower() and nxt[0].islower()
                ):
                    out[-1] = prev + " " + nxt
                    continue
        out.append(p)
    return "\n\n".join(out)


def strip_next_story_pointer(text):
    """Remove the '...told the story of / NEXT STORY TITLE' link the wiki appends.

    Each chapter ends with a pointer to the following one. Leaving it in puts a
    dangling half-sentence and a foreign title at the tail of every story.
    """
    lines = text.split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    if lines and re.fullmatch(r"[A-Z][A-Z\s,'\-.]+", lines[-1].strip() or ""):
        lines.pop()
        while lines and not lines[-1].strip():
            lines.pop()
        if lines and re.search(r"\b(story|stories) of\s*$", lines[-1]):
            lines.pop()
    return "\n".join(lines).strip()


def api(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 5:
                raise
            wait = 10 * (attempt + 1)
            print(f"    429, sleeping {wait}s")
            time.sleep(wait)
        except Exception as e:  # noqa: BLE001 - transient network, retry
            if attempt == 5:
                raise
            print(f"    retry {attempt + 1}: {e}")
            time.sleep(3 * (attempt + 1))


def render(title):
    """Parsed HTML of a subpage, cached on disk so re-runs do not re-hit the API."""
    cache = os.path.join(SRC, "rendered", slug(title) + ".html")
    if os.path.exists(cache):
        return open(cache).read()
    d = api({
        "action": "parse", "page": title, "prop": "text",
        "format": "json", "formatversion": "2",
        "disabletoc": "1", "disableeditsection": "1",
    })
    if "parse" not in d:
        print(f"  !! FAILED {title}: {str(d)[:120]}")
        return ""
    h = d["parse"]["text"]
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    open(cache, "w").write(h)
    time.sleep(2.5)
    return h


def slug(title):
    s = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s


def book_of(title):
    m = re.search(r"/(Book \d+)/", title)
    if m:
        return int(m.group(1).split()[1])
    return 0  # front matter, introductions, frame stories


def main():
    subpages = json.load(open(os.path.join(SRC, "subpages_raw.json")))
    pages = json.load(open(os.path.join(SRC, "pages_raw.json")))

    # reading order: first printed page of each subpage's first transclusion
    def first_page(title):
        raw = subpages.get(title)
        if not isinstance(raw, dict):
            return 9999
        v = raw.get("from") or raw.get("include")
        return int(v) if str(v).isdigit() else 9999

    titles = sorted(
        (t for t in subpages if t != ROOT), key=lambda t: (first_page(t), t)
    )
    print(f"{len(titles)} subpages to render")

    os.makedirs(os.path.join(CORPUS, "stories"), exist_ok=True)
    manifest, full = [], []

    for i, title in enumerate(titles, 1):
        name = title.split("/", 1)[1]
        h = render(title)
        if not h:
            continue
        h = re.sub(r"<style.*?</style>", "", h, flags=re.S)
        ex = TextExtractor()
        ex.feed(h)
        text = ex.text()
        text = strip_next_story_pointer(text)

        sid = f"PT{i:03d}"
        book = book_of(title)
        rec = {
            "story_id": sid,
            "book": book,
            "book_name": {
                1: "Mitra-bheda (The Loss of Friends)",
                2: "Mitra-samprapti (The Winning of Friends)",
                3: "Kakolukiyam (Crows and Owls)",
                4: "Labdha-pranasa (Loss of Gains)",
                5: "Apariksitakaraka (Ill-considered Action)",
            }.get(book, "Front/Intro"),
            "title": name,
            "wikisource_page": title,
            "first_page": None if first_page(title) == 9999 else first_page(title),
            "words": len(text.split()),
            "chars": len(text),
        }
        manifest.append(rec)
        full.append(f"\n\n{'=' * 70}\n{name.upper()}\n{'=' * 70}\n\n{text}")
        with open(
            os.path.join(CORPUS, "stories", f"{sid}-{slug(name)}.txt"), "w"
        ) as f:
            f.write(f"{name}\n{'=' * len(name)}\n\n{text}\n")
        print(f"  {sid}  {rec['words']:>5} words  {name}")
        time.sleep(0.4)

    with open(os.path.join(CORPUS, "panchatantra_full.txt"), "w") as f:
        f.write(
            "THE PANCHATANTRA\n"
            "Purnabhadra's Recension of 1199 CE\n"
            "Translated by Arthur W. Ryder, University of Chicago Press, 1925\n"
            "Source: en.wikisource.org/wiki/Index:Panchatantra.djvu\n"
            "Public domain.\n"
        )
        f.write("".join(full))

    json.dump(manifest, open(os.path.join(CORPUS, "manifest.json"), "w"),
              indent=1, ensure_ascii=False)
    with open(os.path.join(CORPUS, "panchatantra_stories.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest[0]))
        w.writeheader()
        w.writerows(manifest)

    tot = sum(r["words"] for r in manifest)
    print(f"\n{len(manifest)} stories, {tot:,} words -> corpus/")


if __name__ == "__main__":
    main()
