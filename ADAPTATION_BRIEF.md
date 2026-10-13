# Panchatantra Adaptation Brief

Work package for adapting the Panchatantra corpus into children's reading versions.

**What this is:** a set of 87 public-domain fables rewritten into simpler English at two
reading levels. The output feeds an AI tutoring app for Indian Knowledge Systems.

> **Status 2026-10-13.** The English adaptation is **done and audited** — 63 files at 4-9 and 82 at
> 9+ in `corpus/age/`, all passing readability validation. Resolution defects (16 stories, census)
> and content defects (42 certification + 6 re-certification + 3 never-audited tellings) are all
> repaired; every edited file was re-read against the source. **Not provably clean** — a full
> third-pass certification of all 142 tellings has not been run (see `HANDOVER.md` §10).
> **Hindi is out of scope** (user decision); §8 is retained for reference only.

---

## 1. What you are starting from

**Use the JSON, not the text files.** `corpus/panchatantra.json` has all 90 records
with metadata, the curation verdict, and the story text. Pre-filtered versions sit in
`corpus/bands/`.

```
corpus/panchatantra.json        90 stories, full metadata + text
corpus/panchatantra.jsonl       same, one story per line (for streaming)
corpus/bands/band-4-9.json      63 stories curated as suitable for 4-9
corpus/bands/band-9+.json       83 stories curated as suitable for 9+
```

Each story record:

```json
{
  "story_id": "PT016",
  "title": "The Blue Jackal",
  "book": 1,
  "book_name": "Mitra-bheda (The Loss of Friends)",
  "source_file": "PT016-the-blue-jackal.txt",
  "printed_page": 122,
  "word_count": 1271,
  "fable_word_count": 494,
  "scoped_to_fable": true,
  "curation": { "verdict": "NINE_PLUS", "bands": ["9+"], "reason": "...",
                "scoped_to_fable": true },
  "text": "THE BLUE JACKAL\n\nThere was once a jackal...",
  "fable_text": "THE BLUE JACKAL\n\nThere was once a jackal..."
}
```

Minimal consuming pipeline:

```python
import json

doc = json.load(open("corpus/panchatantra.json"))
BANDS = doc["band_targets"]          # the readability targets, so you don't hardcode them

for story in doc["stories"]:
    for band in story["curation"]["bands"]:
        source = story["fable_text"] if story["scoped_to_fable"] else story["text"]
        # ... send `source` and BANDS[band] to your model, write the result
```

**Read §7 before trusting `fable_text`.** It is the fable trimmed out of its enclosing
chapter, and it is right — but only 47 of 90 records have it. For the rest,
`scoped_to_fable` is `false`, `fable_text` equals `text`, and the whole chapter is
being handed to you, frame narrative and all.

### The underlying text files

`corpus/stories/` — 90 plain-text files, if you would rather work from those. 87 are
fables; the other three are the translator's introduction, the book's frame story, and
front matter.

Source: Arthur W. Ryder's 1925 translation, *The Panchatantra*, Purnabhadra's recension,
University of Chicago Press. Public domain. Full provenance in `corpus/README.md`.

**Important, and the one thing most likely to trip you up:** these files are **book
chapters, not clean stories.** Panchatantra is a frame narrative — a story is told
inside another story, which is told inside another. So a file typically contains:

1. the fable you want, introduced by its own heading in capitals,
2. **before** it, the tail end of the parent story that was still talking,
3. **after** it, the parent story resuming, often with court intrigue and a
   "women are fickle" verse that belongs to a completely different tale.

Example — `PT016` is 1,271 words as a chapter but only 494 as a fable. The rest is the
lion-and-bull frame story. **Adapt only the part under the capitalised heading that
matches the filename, up to the line "and the rest of it." Everything else is not
your story.** This is exactly what `fable_text` does for you where it can.

## 1a. The trap that has already bitten us — read before writing any ending

**Most files stop mid-story, on a teller's hand-off line** — `"How was that?" asked the
crow. And the jackal told the story of`. That is the frame introducing the story nested
*inside* it, which lives in the next file. The current story's own resolution comes
*after* that nested story, so **the file you are handed usually does not contain the
ending of the story you are adapting.**

This has already produced a fabrication in this project. `PT010` ("How the Crow-Hen
Killed the Black Snake") stops on a hand-off; the 4-9 adapter, needing an ending,
invented one — the snake chokes on a fish bone. **The word "bone" appears nowhere in
Ryder.** The real ending is the crow-hen stealing a golden chain and dropping it in the
snake's hole so the king's men club the snake (`panchatantra_complete.txt`, lines
2768-2774). That invented death shipped to children.

**So, before writing an ending:**

1. Search `corpus/panchatantra_complete.txt` for the story and read past the hand-off.
   The resolution is almost always there, a paragraph or two later — after the nested
   story has finished.
2. Use **that** ending. It is the plot rule 1 requires and rule 3 protects.
3. If the resolution genuinely is not in the complete text, **do not invent one** —
   leave the file and say so. A missing adaptation is a known gap; a fabricated ending
   is a silent error that survives every validator we have.

None of the automated checks catch this. They check sentence length, not whether the
plot resolves.

## 2. The two bands

| | Ages 4–9 | Ages 9+ |
|---|---|---|
| Who | A grown-up reads it aloud, or the child reads with help | Reads alone, can follow a twist |
| Sentence length | 5–10 words | 9–16 words |
| Flesch-Kincaid grade | 1.0–4.0 | 3.5–6.5 |
| Length | 200–700 words | 500–1,500 words |
| Words | Only words a six-year-old knows | Richer vocabulary is fine |
| Feel | Warm, clear, bedtime-story | Clear but not babyish |

> **Note — these do not match `scripts/adapt.py`.** The validator's `BANDS` are looser
> (4-9: grade 1.0–4.8, 5.0–13.0 w/s, 70–700 words; 9+: 3.5–8.5, 8.0–18.5 w/s, 70–1,500
> words). `--check` will therefore pass files that miss the targets **on this page** —
> notably on length. This table is the spec; the code is the floor. Treat the numbers
> here as what you are aiming for, and flag any file that only satisfies `--check`.

The source text measures at **grade 7.9 with 19.9 words per sentence** — so 4–9 is
roughly a halving of sentence length, not a light trim.

## 3. Rules

1. **Tell the same story.** Same characters, same events in the same order, same
   ending, same moral. You are simplifying the telling, never the plot.
2. **Drop every poem and verse.** Ryder's verse interludes do not survive
   simplification. Leave them out; do not replace them with new rhymes.
3. **Do not invent** events, characters, dialogue topics, or lessons.
4. **Do not add** an introduction, a moral explanation, or a closing note. **But you
   must resolve the plot — and the source file usually stops before it does.** Read the
   warning in §1a below before you write a single ending. "End where the original ends"
   ends the story mid-scene, and inventing a resolution to compensate is worse.
5. **Make it stand alone.** Cut lines like "And the chamberlain told the story of".
6. **Keep the animal characters and their names** (Fierce-Howl, Numskull, Rusty).
7. **Do not soften the point.** If the moral is uncomfortable, keep it. "Intelligence
   beats strength" stays; do not turn it into "be kind to everyone".
8. **When no rule reaches, prefer the source.** The rules here are shortcuts for
   judgment you already have. `corpus/panchatantra_complete.txt` is the authority.

## 4. Content guidance — read this before you start

Ryder's Panchatantra is a *niti-shastra*, a political manual for training princes. It
is **not** a children's book, and the modern children's Panchatantra everyone
remembers is a sanitised retelling that came much later.

So there is content here that should never reach a six-year-old, and your judgment on
that matters more than any rule above.

`data/curation.json` has a per-story recommendation with the evidence behind it:

- **63 stories — fine for both bands**
- **20 stories — 9+ only** (mostly ordinary fable deaths, which are fine for older
  children and standard in the genre)
- **6 stories — not suitable for children at all:**

| ID | Title | Why |
|---|---|---|
| PT009 | The Weaver's Wife | adultery, a body dismembered |
| PT011 | The Heron That Liked Crab-Meat | graphic killing, misogynist verse |
| PT057 | The Brahman, the Thief, and the Ghost | cannibalism |
| PT064 | The Butter-blinded Brahman | adultery, dismemberment |
| PT074 | The Pert Hen-Sparrow | adultery as the plot |
| PT088 | The Three-breasted Princess | infanticide threat, adultery, murder |

**Treat that file as a proposal, not an authority.** It is an automated screen and it
has known blind spots — see §7. If you read a story and disagree, you are almost
certainly right. Overrule it and note why; that note is useful to us.

## 5. Output format

One file per story per language per band. **Keep the source filename exactly.**
A consistent filename means the app can load the adapted version as a drop-in
replacement with no mapping table.

```
corpus/age/
  4-9/        English, ages 4-9        PT016-the-blue-jackal.txt
  9+/         English, ages 9+        PT016-the-blue-jackal.txt
  4-9-hi/     OUT OF SCOPE — empty, stays empty (see §8)
  9+-hi/      OUT OF SCOPE — empty, stays empty (see §8)
```

Each file:

```
The Blue Jackal

Once a jackal named Fierce-Howl lived in a cave near a city. One night he
was very hungry. He crept into the city looking for food.
...

Moral: A clever trick can fool everyone for a while, but not forever.
```

Title, blank line, story, blank line, `Moral:` and one line. Nothing else — no
headers, no notes, no numbering.

## 6. Scope advice

> **Historical — superseded 2026-10-13.** The English adaptation is complete. Kept because the
> reasoning still applies to any future language, and the pilot-first rule is still good advice.

87 stories × 2 bands × 2 languages = **348 texts**. That is a very large job.

**Start with 10 stories, not 87.** Pick from the "both bands" list, do the English
for both bands, and stop. Send those back so the register and format can be checked
before you spend weeks on the rest. It is much cheaper to correct the style at 10
texts than at 348.

## 7. Known limitations — so you know what to check

- The automated curation **only scoped 47 of 90 files to the fable**. For the other
  43 it scanned the whole chapter, so a verdict may reflect the *frame's* content
  rather than the fable's. `data/curation.json` records `scoped_to_fable` per story;
  where it is `false`, read the story yourself before trusting the verdict.
- The screen flags any death. Deaths are normal in fables and mostly harmless for
  older children — that is why so many stories landed in "9+ only".
- It cannot detect tone. A story can score zero and still be bleak.
- Names: Ryder uses English translations of the Sanskrit names. Keep them as-is
  unless told otherwise; consistency matters more than which convention we pick.

## 8. Hindi — OUT OF SCOPE

> **User decision, 2026-10-13: Hindi is removed from the plan, not deferred.** `corpus/age/4-9-hi/`
> and `9+-hi/` stay empty. This section is retained only so the rules are on record if that ever
> changes — do not treat it as pending work.

Same rules, same filenames, same structure. Translate the *adapted* text, not the
original — the Hindi should match the reading level of the English it sits beside.

Two requests:
- Keep proper nouns and animal names recognisable.
- Where a moral depends on an idiom, translate the sense rather than the words.

Please agree terms in writing before starting — an adaptation and a translation are
new copyrightable works, and we would like the rights assigned so the app can use
them. A short email is enough.

## 9. If you want to check your own work

A validator is included. Once your files are in place:

```bash
python3 scripts/adapt.py --band 4-9 --check     # readability vs target
python3 scripts/readability.py "corpus/age/4-9/*.txt" -v
```

It reports Flesch-Kincaid grade and words per sentence per file, so you can see
which ones missed the band before sending them.
