# Panchatantra Corpus

The full text corpus for the Panchatantra AI project. Complete, public domain, verified.

## Source and provenance

| Field | Value |
|---|---|
| Work | The Panchatantra |
| Recension | Purnabhadra's, 1199 CE (North Western Family Sanskrit text) |
| Translator | Arthur W. Ryder |
| Publisher | University of Chicago Press, 1925 |
| Source | `en.wikisource.org/wiki/Index:Panchatantra.djvu` |
| Proofreading | All 484 pages at page-quality 4 (validated against the scan) |
| Scan | `source/Panchatantra_ryder_1925.djvu` (42 MB, from Wikimedia Commons) |
| Commons file page | `commons.wikimedia.org/wiki/File:Panchatantra.djvu` |
| Copyright | Public domain. Commons marks the scan `Public domain` / `UsageTerms: Public domain`. Ryder died 1938, so the translation is PD in the US and India. |
| Underlying Sanskrit | Hertel's critical edition, Harvard Oriental Series vols 11-13 |

This is the Ryder translation specifically because it is the best-regarded public-domain
English rendering and is cleared for commercial reuse. It is not a modern children's
edition, and no modern translation or illustration is included.

## Files

```
corpus/
  panchatantra_complete.txt   the whole book, 484 printed pages, ~96,600 words
  panchatantra_paged.txt      same, with <<<PAGE n>>> markers (printed page numbers)
  stories/                    90 files, one per story, in reading order
  manifest.json               structured record per story
  panchatantra_stories.csv    same as manifest, for Excel
source/
  Panchatantra_ryder_1925.djvu   the scan
  pages_raw.json                 all 484 pages, proofread wikitext
  fullbook/                      cached rendered page-range chunks
scripts/
  fetch_wikisource.py    download all 484 proofread pages
  fetch_subpages.py      download story subpages + their page ranges
  build_complete.py      render the complete book text
  build_stories.py       slice the complete text into per-story files
  check_corpus.py        integrity checks, run after any rebuild
```

## Verification

`python3 scripts/check_corpus.py` — exits non-zero on any failure. It checks id/file
correspondence, page ordering, word counts, wiki/html/script residue, unexpected
characters, mid-sentence truncation, stranded dividers, coverage of the complete text,
and CSV round-tripping. Currently all checks pass.

**Page numbers are cross-checked against the book's own table of contents.** All 89
stories that appear in the printed TOC match it exactly. That matters because the
computed page is where a story's *heading* falls, which for the five frame stories is
the book's divider page, two pages early; the TOC number is the one a citation should
use, so the build prefers it. `toc_page` records it separately from `start_page`.

**Text fidelity was spot-checked against the scans.** Printed page 203 and printed
page 81 (both fetched from Wikimedia and read directly) match the corpus word for
word, including the hand-off lines between stories.

## Known quirk in the source, not a defect

`PT035` The Sensible Enemy ends on the half-line "Better the sensible enemy than".
That is how the 1925 printing reads — printed page 203 shows the same half-line
immediately followed by the next story's heading "THE FOOLISH FRIEND". Ryder leaves
the couplet hanging. Nothing is missing from the corpus. `check_corpus.py` carries
this as a documented exception rather than a failure.

## What is in the 90 files

87 stories across the five tantras, plus the Translator's Introduction (Ryder's own
50-page essay), the Introduction (the frame story of Vishnusharman and the three
princes), and the front matter.

| Book | Sanskrit name | Stories |
|---|---|---|
| 1 | Mitra-bheda (The Loss of Friends) | 34 |
| 2 | Mitra-samprapti (The Winning of Friends) | 10 |
| 3 | Kakolukiyam (Crows and Owls) | 18 |
| 4 | Labdha-pranasa (Loss of Gains) | 13 |
| 5 | Apariksitakaraka (Ill-considered Action) | 12 |

## Manifest fields

`story_id`, `book`, `book_name`, `title`, `title_short`, `wikisource_page`,
`first_page`, `start_page`, `end_page`, `toc_page`, `words`, `chars`.

`start_page` and `end_page` are the book's own printed page numbers (not scan
indexes), so they can be cited directly. `toc_page` is the number printed in the
book's table of contents; it is null for the front matter. `first_page` is the raw
scan page index and is only kept for tracing back to the source.

## How the story files are built, and the one thing to know

**The Wikisource story split is incomplete.** Wikisource divides the book into story
subpages, but that split truncates "The Three-breasted Princess" at printed page 474
although the text runs to 479. Building the corpus from those subpages silently loses
about 1,600 words.

**What this corpus does instead.** It renders the complete 484-page sequence, then
partitions it at each story's heading. Every printed page lands in exactly one story
file, nothing is dropped, nothing is duplicated.

**The consequence of that.** Panchatantra is a frame narrative: stories are told
inside other stories, and a frame resumes after each nested story ends. A heading
partition therefore glues the frame's resumption onto the end of the story that
preceded it. Most stories are unaffected -- what moves is a line or two of transition,
and the partition stays faithful. Two regions needed correcting by hand; both are
handled in `apply_corrections()` in `scripts/build_stories.py`, which fails loudly if
the source no longer matches rather than silently producing wrong output:

- **PT088, The Three-breasted Princess.** This story frames "The Fiend Who Washed His
  Feet", and its entire second half had landed in the child's file. Fixed: PT088 is now
  complete at ~800 words and PT087 is back to the fiend story plus the Book V close.
- **Book V back matter** (colophon, jacket blurb, author note) had landed inside the
  last story. Fixed: moved to PT090.

**PT089 Loss of Gains looks short at 53 words but is correct.** Book IV genuinely opens
with a short frame before handing off to The Monkey and the Crocodile. Do not "fix" it.

**Some files end on a teller's hand-off line** ("And the chamberlain told the story
of"). That is the frame introducing the story nested inside it, which lives in the next
file. **This was previously written up as "expected, not damage". That was wrong, and
the error is instructive — read this before trusting any hand-off ending.**

A hand-off means the *parent* story's resumption should follow the nested story, and
that resumption is what closes the parent's plot. When the partition is faithful that
resumption lands at the end of the nested story's file. When it is not, the parent's
resolution is **missing or misfiled, and nothing fails** — `check_corpus.py` does not
catch a clean cut at a sentence boundary.

Confirmed instance: **PT010** ("How the Crow-Hen Killed the Black Snake") ends mid-
sentence on `And the jackal told the story of`. Its actual ending — the crow-hen steals
a golden chain and drops it in the snake's hole so the king's men club the snake —
exists only in `panchatantra_complete.txt` (lines 2768-2774). Consequence downstream:
the 4-9 adapted telling invented a fish-bone death instead, and that fabrication served
to children for weeks.

**So: treat every hand-off ending as unverified.** Check that the parent's resolution
actually exists in `panchatantra_complete.txt` before trusting the per-story file. Any
adaptation built on a truncated file will have had to invent an ending to stand alone.

## Chunking for retrieval

`panchatantra_complete.txt` is the faithful artifact for RAG ingestion. The per-story
files are a convenience for the app's story-selection and quiz flow, where "one story =
one unit" is what the UI and the recommendation engine need. If retrieval quality
matters more than story units, chunk the complete text and keep the manifest as
metadata.

## Rebuilding

```bash
python3 scripts/fetch_wikisource.py   # 484 pages       -> source/pages_raw.json
python3 scripts/fetch_subpages.py     # 90 subpages     -> source/subpages_raw.json
python3 scripts/build_corpus.py       # per-story files (Wikisource split)
python3 scripts/build_complete.py     # complete book   -> corpus/panchatantra_complete.txt
python3 scripts/build_stories.py      # partition       -> corpus/stories/
```

`build_corpus.py` renders one file per Wikisource story subpage. Those files are
superseded by `build_stories.py` and are not kept, but the manifest it writes is what
`build_stories.py` reads its titles and reading order from, so it still has to run
first. All network responses are cached under `source/`, so re-runs are free and can
be made offline.

## Status of the known gaps

- **The adapted tellings: the 2026-10-13 defects are FIXED (2026-10-13).** A census found 23 tellings
  with an invented or truncated ending and all were fixed. A certification pass over the 119 it had
  cleared then found **42 more** — inverted causality, mis-assigned actors, unearned morals. Those 42
  are **now fixed and re-certified faithful**, together with 6 defects a re-certification itself
  caught and 3 tellings neither prior pass had read. **54 edits across 47 files.** *"Does it resolve?"*
  and *"is the plot right?"* are different questions; both have now been asked. See `WORKLOG.md`
  §2026-10-13 (later). **Still not provably clean** — each successive pass found more, so a full third-pass
  certification of all 142 tellings remains the honest bar.
- **The hand-off bug was audited by hand on 2026-10-13 and fixed.** The check is *still* not
  automated — `check_corpus.py` does not carry it — but a fan-out of 28 readers over all 142
  adapted tellings found **16 stories with an invented or truncated ending (about 15% of the
  corpus)**, and every one was repaired. Full findings: `data/census_2026-10-13_findings.md`.
  **The lesson stands: treat every hand-off ending as unverified, and do not expect a script to
  catch it** — four automated detectors have failed on this project.
- ~~**PT090 is a duplicate of PT002**~~ — **resolved 2026-10-13.** Removed from the adapted side
  only (both band files, `panchatantra_adapted.json`, `corpus/bands/*.json`, `data/curation.json`).
  The source record is kept so this file's coverage test stays valid. `build_story_tags.py`
  already skipped it via `_skipped`.

## Done since this section was first written

- Per-story moral, themes, characters, age band, difficulty — `corpus/story_tags.json`,
  **82** records (`scripts/build_story_tags.py`).
- Quiz / discussion datasets — `corpus/story_items.json`, **250** measurement + **495**
  discussion (`scripts/build_story_items.py`).
- Adaptive engine — `engine/`; see `WORKLOG.md` for the current phase.

## Decided against

- **Sanskrit text layer.** Hertel's 1908 critical edition of the same recension is
  public domain and its OCR is usable, but the layer was reviewed and dropped. It
  would have added a bilingual dataset and strengthened the Indian Knowledge Systems
  claim; it was judged not worth the alignment work. Corpus stays English-only.
- **Hindi translation layer.** Originally deferred; **removed from scope on 2026-10-13 by user
  decision** — not the same reasoning as Sanskrit above. `corpus/age/4-9-hi/` and `9+-hi/` stay
  empty. See `ADAPTATION_BRIEF.md` §8 and `WORKLOG.md` §Decisions.
