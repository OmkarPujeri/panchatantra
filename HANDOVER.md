# Panchatantra AI — Handover

Everything that has been built, why, and what state it is in. Read this first; it
assumes no prior context.

Last updated: 13 October 2026.

---

## 1. What this project is

An AI tutoring platform that turns the Panchatantra into an interactive learning
experience for children, built around Indian Knowledge Systems and
Retrieval-Augmented Generation. The full product idea — features, architecture,
stack, research contributions — is in `PROJECT_CONTEXT.md`. Read that for the
*vison*. Read this for the *data*, which is what actually exists so far.

The corpus work was done because everything else depends on it: RAG needs a
trustworthy source text, the adaptive-storytelling feature needs age-graded text,
and the quiz generator needs stories with known morals.

## 2. What exists right now

```
HANDOVER.md                  this file — start here
WORKLOG.md                   build log + RESUME HERE + every session's findings
ADAPTATION_BRIEF.md          work package for whoever adapts stories for children
PROJECT_CONTEXT.md           the original product/vision document
STORY_TAGGING_SCHEMA.md      the tag/item schema — the handoff contract to video

corpus/
  panchatantra.json          ★ all 90 stories, metadata + text (source, unadapted)
  panchatantra.jsonl         ★ same, one story per line
  panchatantra_complete.txt    the whole book continuous, 96,541 words ← THE AUTHORITY
  panchatantra_paged.txt      same, with <<<PAGE n>>> markers for citation
  stories/                    90 plain-text files (see §9 note: some end mid-sentence)
  bands/band-{4-9,9+}.json    source stories curated per band
  manifest.json, .csv         per-story metadata
  README.md                   provenance, method, verification, known quirks
  panchatantra_adapted.json   ★ the adapted tellings, both bands, with metrics
  age/4-9/     63 files  ★ English, ages 4-9   (+ manifest.json)
  age/9+/      82 files  ★ English, ages 9+    (+ manifest.json, _rejected/)
  age/4-9-hi/          EMPTY — Hindi not started
  age/9+-hi/           EMPTY — Hindi not started
  story_tags.json            ★ 82 records: moral, themes, chars, skills, age_map
  story_items.json           ★ 250 measurement + 495 discussion items

engine/                      ★ the adaptive engine (v0 prototype)
  state.py  select.py  update.py  demo.py    `python3 -m engine.demo` = self-check

data/
  curation.json              per-story age-band verdict + evidence (heuristic)
  story_tags_authored.json   ← EDIT HERE for tags; build_story_tags.py reads it
  story_items_authored.json  ← EDIT HERE for items; build_story_items.py reads it
  review_2026-10-01_workflow.json   raw output of the 23-agent review fan-out
  review_2026-10-13_workflow.json   raw output of the 2026-10-13 content-fix fan-out
  adapt_config.json          model settings for the generation pipeline (unused)

scripts/                     19 Python scripts, all runnable and cached
source/
  Panchatantra_ryder_1925.djvu   the original scan
  pages_raw.json                 all 484 proofread pages
  fullbook/, rendered/           render caches, safe to delete
```

**Nothing in this project is under version control.** There is no git repository. Every
finding above was found by re-reading files, and there is no history to diff against —
the edit scripts are guarded and idempotent precisely because that safety net is absent.
Initialising a repo is the cheapest un-taken improvement here.

### Confirm you have the state these docs describe

Since there is no history to diff, check the artifacts directly. Hashes as of
1 October 2026 (first 16 hex of SHA-256):

```bash
shasum -a 256 corpus/story_tags.json corpus/story_items.json corpus/panchatantra_adapted.json
```

```
story_tags.json            404bca6c966f3700
story_items.json           0bbf7284d8aba646
panchatantra_adapted.json  5e910e2638d44c39
```

If these differ, you have a different state than this document describes — **read
`WORKLOG.md`'s RESUME HERE before acting**, not this file.

## 3. The corpus

### Where it came from

| | |
|---|---|
| Work | The Panchatantra |
| Recension | Purnabhadra's, 1199 CE (Panchakhyanaka) |
| Translator | Arthur W. Ryder |
| Publisher | University of Chicago Press, 1925 |
| Source | `en.wikisource.org/wiki/Index:Panchatantra.djvu` |
| Scan | Wikimedia Commons, marked Public Domain |
| Rights | Public domain. Ryder died 1938. Safe for commercial use. |

**The single most important fact about this text:** it is *not* a children's book.
Ryder's Panchatantra is a *niti-shastra* — a political manual for training princes.
It contains adultery, murder, dismemberment, cannibalism, an infanticide threat, and
a great deal of misogyny. The children's Panchatantra everyone remembers is a
sanitised retelling tradition that came much later. This drives the curation in §5.

### Size

| | |
|---|---|
| Stories | 87 fables + 3 front/intro pieces = 90 records |
| Full text | 96,541 words |
| Fable-only (frame narrative removed) | 72,800 words |
| Books | 1: 34 stories · 2: 10 · 3: 18 · 4: 13 · 5: 12 |

### The frame-narrative problem — read this, it causes most of the difficulty

Panchatantra is a chain of nested stories: a fable is told inside another fable,
which is told inside another. So a "story file" is really a **book chapter**, and
contains three things:

1. the tail of the *parent* story that was still talking
2. **the fable**, introduced by its own heading in capitals
3. the *parent* story resuming — often with court intrigue and a
   "women are fickle" verse belonging to a different tale

Concrete example: `PT016` The Blue Jackal is **1,271 words as a chapter but only 494
as a fable**. The other 777 words are the lion-and-bull frame story.

This caused three separate bugs before it was understood, and it is why the JSON has
two text fields (§4). It is also why the curation needed a fix (§5).

## 4. The JSON — what to use

```python
import json
doc = json.load(open("corpus/panchatantra.json"))
for story in doc["stories"]:
    for band in story["curation"]["bands"]:
        source = story["fable_text"] if story["scoped_to_fable"] else story["text"]
        # send `source` + doc["band_targets"][band] to your model
```

Per-story record:

| field | meaning |
|---|---|
| `story_id` | `PT001`…`PT090` |
| `title`, `book`, `book_name` | metadata; `book` is 0 for front/intro pieces |
| `source_file` | filename in `corpus/stories/` |
| `printed_page` | page number from the book's own table of contents |
| `word_count` | words in the full chapter |
| `fable_word_count` | words in the trimmed fable |
| `scoped_to_fable` | **true** = `fable_text` is a real trim; **false** = it equals `text` |
| `curation.verdict` | `BOTH` / `NINE_PLUS` / `EXCLUDE` |
| `curation.bands` | which bands this story may be adapted for |
| `curation.reason` | what triggered the verdict |
| `text` | the **entire** chapter, complete, nothing removed |
| `fable_text` | the chapter trimmed to just the fable — a shorter *extract*, not a damaged copy |

**`text` is never truncated.** It is byte-identical to the source files, verified on
all 90 records. `fable_text` is a shorter piece of it.

**Only 47 of 90 records have a real trim.** For the other 43, `scoped_to_fable` is
`false`, `fable_text` equals `text`, and the reader gets the whole chapter and must
find the fable themselves. The brief explains how.

## 5. Age-band curation

`data/curation.json`. Every story scored for content that decides whether a young
child may see it, with the evidence recorded so the call can be checked.

| verdict | count | meaning |
|---|---|---|
| `BOTH` | 63 | fine for 4-9 and 9+ |
| `NINE_PLUS` | 20 | 9+ only — mostly ordinary fable deaths |
| `EXCLUDE` | 6 | not suitable for children at all |

The six excluded: The Weaver's Wife (adultery, a body dismembered), The Heron That
Liked Crab-Meat, The Brahman the Thief and the Ghost (cannibalism), The
Butter-blinded Brahman, The Pert Hen-Sparrow, The Three-breasted Princess
(infanticide threat, adultery, murder).

**Three caveats, all important:**

1. **This is a heuristic screen, not a human read.** It counts keyword signals. The
   `reason` field names what triggered each verdict, and `evidence` holds the matched
   phrases. Overrule it freely.
2. **Death is weighted low on purpose.** A character dying is normal in a fable —
   the villain gets eaten, the lion falls in the well. That is why 20 stories sit in
   `NINE_PLUS` rather than being excluded.
3. **`scoped_to_fable` matters here too.** For the 43 unscoped files the scan saw the
   whole chapter, so a verdict may reflect the *frame's* content rather than the
   fable's. Where it is `false`, read the story before trusting the verdict.

An early version of this screen wrongly excluded **The Blue Jackal** — one of the
most-retold Panchatantra stories for children — because it was reading the frame's
misogynist verse and blaming the fable for it. That is the failure mode to watch for.
**Corrected 2026-10-13 (PT016):** the screen still scored it `NINE_PLUS` on the fable's own
"gore-detail/murder" (the jackal is torn to bits), but the death is one line, both tellings
existed, and `story_tags.json` had already overruled it — so the verdict is now `BOTH`, with
the screen's reason kept in the record. `band-4-9.json` and the 63 4-9 tellings agree again.

## 6. The scripts

All are runnable, all cache their network responses, none need a paid API.

| script | what it does |
|---|---|
| `fetch_wikisource.py` | downloads all 484 proofread pages → `source/pages_raw.json` |
| `fetch_subpages.py` | downloads story subpages + their page ranges |
| `build_corpus.py` | renders per-story files; writes the manifest |
| `build_complete.py` | renders the whole book as continuous text |
| `build_stories.py` | partitions the complete text into `corpus/stories/` |
| `check_corpus.py` | **integrity checks — run after any rebuild** |
| `readability.py` | Flesch-Kincaid etc.; usable on any text |
| `curate.py` | writes `data/curation.json` |
| `export_json.py` | writes `corpus/panchatantra.json`, `.jsonl`, and the band files |
| `adapt.py` | generation pipeline (see §7) |

Rebuild from scratch:

```bash
python3 scripts/fetch_wikisource.py && python3 scripts/fetch_subpages.py
python3 scripts/build_corpus.py && python3 scripts/build_complete.py
python3 scripts/build_stories.py && python3 scripts/curate.py
python3 scripts/export_json.py && python3 scripts/check_corpus.py
```

## 7. The generation pipeline — built but never run

`scripts/adapt.py` rewrites stories for a band using a language model, validates the
result against readability targets, retries on misses, and quarantines failures in
`_rejected/` rather than shipping them.

```bash
python3 scripts/adapt.py --band 4-9 --all --dry-run   # inspect prompts, no API
python3 scripts/adapt.py --band 4-9 --all             # generate
python3 scripts/adapt.py --band 4-9 --check           # validate what exists
```

Targets the adaptation is held to. **Two lists disagree; the disagreement is unresolved —
read both, do not pick one silently.**

| enforced by `adapt.py --check` | 4-9 | 9+ |
|---|---|---|
| Flesch-Kincaid grade | 1.0–4.8 | 3.5–8.5 |
| Words per sentence | 5.0–13.0 | 8.0–18.5 |
| Max syllables/word | 1.42 | 1.55 |
| Length | 70–700 w | 70–1,500 w |

| **intended** (`ADAPTATION_BRIEF.md` §2, and what this doc said before) | 4-9 | 9+ |
|---|---|---|
| Flesch-Kincaid grade | 1.0–4.0 | 3.5–6.5 |
| Words per sentence | 5–10 | 9–16 |
| Length | 200–700 w | 500–1,500 w |

The first table is `BANDS` in `scripts/adapt.py` — the values the validator actually
enforces. The second is the spec the brief gives a human adapter. **The gap is
load-bearing:** `adapt.py --check` passes PT022's 9+ telling at 157 words, because the
enforced floor is 70 while the intended floor is 500. That discrepancy is the reason
§10 still lists PT022 as needing a real re-adaptation. **Decide which is the spec**, then
align `ADAPTATION_BRIEF.md` §2, this page, and `BANDS` to it.

**It has never made a real API call.** The key available in the development
environment is rejected by its own gateway (`401 unauthorized client detected`). The
dry-run works and the prompt is written, but the output has never been seen. Do not
assume it works.

**The current plan is not to use it for generation.** A human adapter will do the
rewriting (§8), and this script then serves as the **validator** — `--check` reports
which files missed the band. That is its most useful role.

## 8. The adaptation plan

`ADAPTATION_BRIEF.md` is the work package for a human adapter. Summary:

- **Two bands**: ages 4-9 and 9+. (The brief's Hindi stage is **out of scope** — user decision
  2026-10-13. Read the brief's English sections only.)
- **Rules**: same plot and moral, short sentences, drop all verse, no inventions, no
  added moralising, keep character names.
- **Output**: one file per story per band per language, same filename as the source,
  in `corpus/age/{4-9, 9+, 4-9-hi, 9+-hi}/`.
- **Start with 10 stories, not 87.** 87 × 2 bands × 2 languages = 348 texts. Correct
  the style at 10 before spending weeks on the rest.
- **Get the rights assigned in writing.** Public domain covers Ryder's translation;
  an adaptation and a Hindi translation are *new* copyrightable works owned by the
  person who makes them. For a commercial app this needs assigning. One email.

## 9. Verification — what has actually been checked

| check | result |
|---|---|
| JSON `text` byte-identical to source files | all 90 records, zero differences |
| Word total, JSON vs manifest | 96,541 = 96,541 |
| Story page numbers vs the book's own table of contents | **89 of 89 exact** |
| Text fidelity vs the physical scans | 2 pages read directly, word-for-word match |
| No wiki/HTML/script residue anywhere | clean |
| No story truncated mid-sentence | **WRONG — corrected 1 Oct 2026.** See the note below |
| Every printed page lands in exactly one story file | clean |
| CSV round-trips | 90 rows, 12 columns |
| Adapted tellings faithful to the source | **Checked 2026-10-13→14 and certified** — census, certification and re-certification each read tellings against the source; all 54 fixes re-read and certified. Full 142 not re-certified as a third pass. See §10 |

> **Two of these rows are not what they claim.**
>
> **Truncation.** This row used to read "clean". It is not. `corpus/stories/PT010-*.txt`
> ends mid-sentence on a teller's hand-off — `"How was that?" asked the crow. And the
> jackal told the story of` — and so do others. `check_corpus.py` passes anyway: its
> truncation check does not catch a clean cut at a sentence boundary, and this project had
> written down that hand-off endings are *expected, not damage* (`corpus/README.md`). That
> belief is what hid the bug. **A hand-off ending means the parent story's resumption is
> filed elsewhere, and it may not be there at all.** PT010's real ending (the golden-chain
> device, `panchatantra_complete.txt:2768-2774`) is reachable only from the complete text.
>
> **Faithfulness.** *(Until 2026-10-13.)* Nothing had ever checked that an adapted telling says what
> its source says. The validator measures sentence length, not plot. PT010's 4-9 telling invented a
> death that appears nowhere in Ryder, and it shipped. Any adaptation built on a truncated
> file *had* to invent an ending to stand alone — which makes the truncation bug and the
> fabrication bug the same bug.
>
> **Both rows are now addressed (2026-10-13→14).** A census (28 readers) and then a certification
> pass and a re-certification each read tellings against the source; every defect found was fixed and
> re-read. See §10.
>
> Re-run both checks against `panchatantra_complete.txt`, not the per-story files.

Run `python3 scripts/check_corpus.py` any time; it exits non-zero on failure.

### Bugs found and fixed during the sweep

For the record, because they show the kinds of errors this corpus is prone to:

1. `start_page` was null on all 90 records — a regex capture bug
2. A Cyrillic `ѐ` typed instead of `è` in "learnѐd"
3. em-space characters from verse indentation
4. Book dividers (`BOOK I`…`BOOK V`) stranded at the end of the *previous* book
5. Doubled titles at the head of the five frame stories
6. Book V back matter (colophon, jacket blurb) inside the last story
7. **PT088's entire second half was misfiled into PT087** — the princess story frames
   the fiend story, and the heading-based partition gave the parent's continuation to
   the child
8. `fable_text` endings missing their final period

### Two things that look like bugs and are not

- **PT035 ends "Better the sensible enemy than".** The 1925 printing reads exactly
  that, then goes into the next story. Ryder leaves the couplet hanging. Verified
  against the scan.
- **PT089 Loss of Gains is only 53 words.** Book IV genuinely opens with a short
  frame. Correct as-is; do not "fix" it.

## 10. What is not done

> **Updated 2026-10-13.** The five open defects below were **fixed and applied** — see
> `WORKLOG.md` §2026-10-13 (content fixes) for the evidence, the diffs and the two new bugs found while
> applying them. The project is **not** under version control — a temporary git repo was created and then
> removed at the user's request on 2026-10-13.
> What remains open is listed at the end of this section.

**Content gaps**

> ## ⚠️ FIXED, BUT NOT PROVABLY CLEAN (updated 2026-10-13)
>
> Three passes found content defects: **23** (census), then **42** (certification), then **6**
> (re-certification of the 2026-10-13 edits). **All 42 + 6 are now fixed**, and every file this
> session touched — **47 files, 54 edits** — was re-read against Ryder and certified faithful. The 3
> tellings neither of the first two passes had read (`PT028 9+`, `PT029 9+`, `PT030 9+`) were audited
> too (PT028 faithful; PT029/PT030 fixed). See `WORKLOG.md` §2026-10-13 (later).
>
> The defect class was real: pass 1 asked *"does the telling resolve?"*; pass 2 asked *"is the plot
> right?"* and found inverted causality, wrong actors, unearned morals — a telling can resolve
> perfectly and still say the **opposite** of the source. All three spot-checks held (PT002 9+ PT005
> 4-9 PT006 9+).
>
> **Still not provably clean.** Each successive pass found more, so the honest bar remains a full
> third-pass certification of all 142 tellings — **not run**. What is true: no file changed on
> 2026-10-13 is unverified, and `check_corpus.py` + `adapt.py --check` are green.

- **Hindi translations — OUT OF SCOPE (user decision, 2026-10-13).** `corpus/age/4-9-hi/` and
  `9+-hi/` are both empty and will stay that way. Not deferred-with-a-trigger; removed from the
  plan. English is done (63 + 82 files).
- **PT060's 9+ child-marriage line — rewritten 2026-10-13.** It now reads "saying that
  the time had come for her to be married". This is the one deliberate departure from Ryder
  in the project; the plot is unchanged. See WORKLOG §2026-10-13 (content fixes) to revert.
- ~~**The 9+ band is short of the brief's floor.**~~ **CLOSED 2026-10-13 — not a defect.** The
  bands are separated by reading complexity, not length: FK 3.17 → 6.33 and words/sentence
  10.24 → 15.36, both enforced and passing. 9+ median is 283 words against 4-9's 197, and only 8
  of 82 nine-plus stories fall below the 4-9 median. The brief's 500-word row is deliberate —
  it calls itself the spec and the code the floor — so the corpus sits at about half the length
  aim while meeting the complexity aim. Accepted by decision 2026-10-13.

**The five held defects — all now closed (2026-10-13)**

| | |
|---|---|
| **PT010** | ✅ fixed — the fabricated fish-bone death (4-9) *and* the unresolved ending (9+) both replaced with the source's golden-chain device |
| **PT003** | ✅ fixed — both bands now run to Lively's death and Rusty's repentance; the earlier "hallucinated quote" was itself confirmed to be a hallucination (grep returns nothing) |
| **PT059** | ✅ fixed — both bands and the 4-9 moral aligned to the source's single mechanism (the death passes to the lover) |
| **PT084** | ✅ fixed — prose was correct; the `C4_vocabulary` tag is now **2** (3 was a 5-story top tier; 2 is the 51-story norm) |
| **PT017** | ✅ fixed — the 9+ incoherent motive ("the archer thought the *swan* was a threat" — the swan is asleep) replaced with the source's omen |

Also this session: **PT022 9+** 157 → 512 words; **PT013 9+** and **PT047 9+** now exist
(1,467 and 695 words) with tags and items, so `build_story_tags.py` passes again at 82
records; **PT090** removed from the adapted side only — it is the book's **front matter**,
and its "duplicate of PT002" label was imprecise (35% source overlap).

> **PT010 raised a question bigger than PT010, and it has now been answered.**
> **The census ran on 2026-10-13: 142 tellings audited, ~16 stories carry a real defect —
> about 15% of the corpus.** Full findings in `data/census_2026-10-13_findings.md`, every
> claim verified against the source. The mechanism is the partition bug described above: an
> adapter handed a chapter that ends on a hand-off either invented an ending or stopped at
> the hand-off. **This is now the largest remaining content job and it is a shipping defect
> in the English corpus, not a translation blocker.**

**Engine — known weaknesses, not bugs**
- **No difficulty term.** Add +400 to every rating and a child gets the identical
  sequence: the score measures gaps *between* skills, so a uniform shift moves them all.
- **Weak exploration**, ~4 distinct stories per child in 8 draws, at any age.
- **Capacity only ramps upward** — shrinking needs the drop-off *point*, which is telemetry.
- **`calibration` is never written** — needs `n_observations` across many children.
- **Cold start is a binary** — strong and weak children get identical openings.

**Blocked / not owned**
- **Step 3 telemetry and Step 4 co-read** both need an app/player that does not exist.
  This blocks `calibration` and the capacity ramp together.
- **The engine is a prototype**, to be ported into the app.
- **Video generation** is the team-mate's half, consuming the `video_brief` block.

**Trust these less than they look**
- `scripts/adapt.py` has **never made a real API call** — its key is rejected by its own
  gateway. `--check` works and is in use; generation does not.
- The age-band curation (`data/curation.json`) is a **keyword heuristic**, not editorial
  judgement. Treat it as a proposal.
- The `_draft` review flag was cleared on all 70 entries but **records nothing** — see
  `WORKLOG.md` §Open items.

## 11. Honest summary

**Solid:** the corpus is complete and packaged for a pipeline, with provenance and
licensing recorded. Page numbering matches the book's own table of contents, and two
direct reads of the physical scans hold. The adaptive engine selects on ability and its
self-check passes; 82 stories carry tags and question banks at 100% coverage.

**Weaker than it looked until 1 October 2026. Three things were certified that were not —**
**the first two are now corrected (2026-10-13→14):**

- The adapted tellings were **not all faithful.** PT010's 4-9 telling invented a death that appears
  nowhere in Ryder; the validator measures sentence length, not plot. **Corrected:** a census, then a
  certification, then a re-certification read tellings against the source — 23, then 42, then 6
  defects found, every one fixed and re-read. **54 edits across 47 files.** See §10.
- The per-story files are **not all complete**, and stay that way by design: PT010 and others end on
  a teller's hand-off, the parent's resolution living in `panchatantra_complete.txt`. That is the
  partition, not damage — but `check_corpus.py` does not check for it, and `corpus/README.md` had
  written the hand-off ending down as *expected, not damage*, the belief that hid the bug. The
  **adapted** side is now resolved against the complete text.
- The review flag is **not evidence.** It was cleared on all 70 entries while recording no
  reviewer and no date. A second read of the 18 served stories then found 7 defects in 15
  of them.

**Untested:** the generation pipeline has never made a live API call.

**Blocked on a decision:** which readability target is the spec (the brief and the code
disagree — §7), and whether adaptation is done by a model or a human.

**The lesson worth carrying forward:** every automated check in this project has failed at
least once, and each failure was a check that reported success *without looking at the
thing that mattered* — a keyword screen that read the frame instead of the fable, a
truncation check that accepted a clean cut, a validator that measured sentence length and
not plot, a review flag that recorded nothing. Reading the actual text is the only check
here that has never been wrong.

---

## 12. Where to start

Read in this order: this file → `WORKLOG.md` §RESUME HERE → `corpus/README.md`'s hand-off
note → `ADAPTATION_BRIEF.md` §1a if you are adapting anything.

```bash
python3 -m engine.demo                        # engine self-check
python3 scripts/check_corpus.py               # corpus integrity — PASSES, but read §9
python3 scripts/build_story_tags.py --check   # 82 tag records
python3 scripts/build_story_items.py --check  # 250 + 495 items
python3 scripts/adapt.py --band 4-9 --check   # readability, per band
python3 scripts/review.py --flag              # remaining flagged rows
```

**The things to do first, in order:**

1. ~~**Fix the 42 certification defects** (§10).~~ **DONE 2026-10-13.** 4 fan-outs (draft+verify ×2;
   re-certification ×2), **54 edits across 47 files**, every edit re-read against Ryder and certified.
   Fixed: the 42 certification defects, the 3 never-audited tellings (PT028 faithful; PT029/PT030
   fixed), and 6 defects the re-certification itself caught (2 caused by first-pass edits). Tools:
   `scripts/apply_triple_fixes.py`; undo `data/apply_triple_fixes_backup.json` +
   `data/apply_recertfix_backup.json`. Full write-up: `WORKLOG.md` §2026-10-13 (later).
2. ~~`git init`~~ — done, then removed at the user's request, then re-initialised by the user;
   **commits again declined 2026-10-13**. Nothing here is versioned by choice; `WORKLOG.md` is the
   only record and the two `*_backup.json` files are the only undo.
3. ~~Fix PT010~~ — **done 2026-10-13**, along with PT003, PT017, PT059, PT022, PT084, PT060,
   PT013, PT047; PT090 removed.

**What is left:** the app/player (unowned; blocks telemetry, co-read, dashboard), the engine
prototype port, and video generation (team-mate's half). A full third-pass certification of all 142
tellings has not been run — see §10.

**Ownership:** Omkar owns the adaptive engine — story parameter tagging, skill/age
mapping, story selection. The team-mate owns video generation, consuming the `video_brief`
block. **`STORY_TAGGING_SCHEMA.md` is the handoff contract between them:** `video_brief`
is the video half; `skills` / `age_map` / `attention_load` / `calibration` are the engine
half; the shared spine is `story_id` / `title` / `band` / `moral` / `themes` /
`characters`.
