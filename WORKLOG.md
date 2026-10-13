# Worklog — build log & resume point

Running log of build sessions on the Panchatantra AI project, plus everything a new
session needs to pick up cold.

**Last updated:** 2026-10-13

---

## ⏭ RESUME HERE

**Where we are (2026-10-13):** The 2026-10-01 held defects are **fixed and applied**. All checks
green: `engine.demo` 82 stories / 250 measurement / 495 discussion at 82/82 coverage,
`check_corpus.py` PASS, both builders OK, `adapt.py --check` clean for both bands.

> **Version control (updated at end of 2026-10-13).** A repo was initialised, then removed at the
> user's request, then **re-initialised by the user**. `.gitignore` exists (excludes
> `source/fullbook/`, `source/rendered/`, `.playwright-mcp/`, `__pycache__/`). **There are still
> ZERO commits** as of this writing — everything from 2026-10-13 is on disk only. The baseline
> `bba22f9` was in the *removed* repo and is **gone**; any reference to it below is historical and
> unresolvable. **`data/apply_content_fixes_backup.json` is the only undo for the band files.**
> `GIT_CHEATSHEET.md` has the copy-paste commands.

**What changed on 2026-10-13, in order:** the 2026-10-01 held defects were fixed (PT010 both bands
— fabricated fish-bone death *and* unresolved ending both replaced with the golden-chain device;
PT003, PT017 9+, PT059 both bands, PT022 9+ 157→512 words, PT013/PT047 9+ new tellings plus their
tags and items; PT090 removed from the adapted side only). Then the judgement calls (PT084 `C4`
3→2; PT060 child-marriage line; PT062 9+ verse + "Pot-baking Hell"; PT077 both bands' verse moral;
PT089 4-9 heart-eating). Then **the census**: 142 tellings audited, 23 flagged, all fixed in 24
edits across 22 files. Then **certification**, which found 42 more — see below.

**Immediately next:**
> **The 42 are fixed (2026-10-13).** All 42 certification defects fixed and re-certified, plus the 3
> tellings neither prior pass had read (PT028/PT029/PT030 9+). **54 edits across 47 files**, every one
> re-read against the source. See the later 2026-10-13 entry. **Not provably clean** — a full third-pass
> certification of all 142 tellings has *not* been run, and every prior pass found more.

1. ~~Fix the 42 certification defects~~ — **DONE 2026-10-13.** 4 fan-outs (draft+verify ×2; re-cert
   ×2), 54 edits across 47 files, all certified faithful against the source. See WORKLOG §2026-10-13 (later).
2. ~~Commit something.~~ **In progress 2026-10-13** — the user is making the first commit
   (`GIT_CHEATSHEET.md` §1). Until it lands, `WORKLOG.md` is the only record and
   `data/apply_triple_fixes_backup.json` + `data/apply_recertfix_backup.json` the granular undo for
   the content fixes; once committed, git is the undo.
3. **The app/player** — unowned, and it blocks telemetry, co-read and the dashboard together.
4. ~~3 tellings were never audited by EITHER pass~~ — **DONE 2026-10-13.** PT028 9+ audited faithful;
   PT029 9+ and PT030 9+ had real defects, now fixed and certified.

> **The 9+ word-count question is CLOSED (2026-10-13) — not a defect, no work needed.** It was
> never a real spec: **reading complexity separates the bands, not length.** 4-9 median 197 words
> at FK 3.17 / 10.24 w-s; 9+ median 283 words at FK 6.33 / 15.36 w-s. FK nearly doubles and
> sentence length rises 50%, both enforced by `adapt.py` and both passing. 9+ is also genuinely
> longer than 4-9 (283 vs 197) and only **8 of 82** nine-plus stories fall below the 4-9 median.
> **Correction to an earlier claim in this entry:** the brief's 500-word row is *not* a typo. The
> brief says so itself, two lines under the table — *"This table is the spec; the code is the
> floor. Treat the numbers here as what you are aiming for, and flag any file that only satisfies
> `--check`."* So it is a deliberate aspiration, and the corpus sits at roughly **half** of it on
> length (283 vs a 500 floor) while **meeting** it on complexity. The user has decided that is
> acceptable. **Closed by decision, not by defect — and do not "fix" the brief.**

> **Hindi is out of scope (user decision, 2026-10-13).** Not deferred-with-a-trigger — removed
> from the plan. Nothing in the remaining work waits on it and it no longer gates anything.
> `corpus/age/4-9-hi/` and `9+-hi/` stay empty. The superseded reason it was urgent — "finish the
> census first or the invented endings get translated too" — no longer applies, and the census is
> now run anyway.

**Resolved this session, do not re-open:** PT084 `C4` 3→2 · PT060 9+ child-marriage line softened
(**the one deliberate departure from Ryder**, revert is one string) · PT003 441 words (no change,
above the band median) · PT062 9+ verse + "Pot-baking Hell" (both replaced) · PT077 4-9 and 9+
verse morals (replaced with **authored prose** — do not read those as source text) · PT089 4-9
heart-eating (softened, plot intact). Details and evidence in the earlier 2026-10-13 entry.

**Four writes this session "succeeded" while being wrong**, all the same species — a rewrite that
hides or misreports the real change: `adapt.py --check` measuring a stale manifest; the apply script
silently rewriting CRLF as LF; a shell loop that printed `ALL CHECKS GREEN` while executing nothing;
and a JSON rewrite at the wrong indent that turned a one-record deletion into a 3,000-line diff.
All four are written up in the earlier 2026-10-13 entry and all four are fixed. **Assume any check or
write here may be lying until you have seen it fail, and read every diff before trusting it.**

---

## ⏭ RESUME HERE (2026-10-01, superseded)

**Where we are:** Steps 0–2 done — tags 10 → 80, items 10 → 80 (242 measurement + 485
discussion), coverage 100%, engine selects on ability. The human review was **marked
complete** on 2026-10-01 (`_draft` cleared on all 70 — note `--approve` records the
assertion, not the evidence). A follow-up **second-pass read of all 18 served stories**
then found **7 confirmed defects the first pass missed**; a 23-agent fan-out fixed 7
stories (14 edits) and held 5. **Of 18 served stories, 5 still carry an open defect.**

**Next action — 5 items are held, each needing a decision rather than a patch:**
1. **PT010 first — it is a corpus bug, not a story bug.** The 4-9 telling's fish-bone death
   is fabricated; the source's real ending is the golden-chain device
   (`panchatantra_complete.txt:2768-2774`), lost to the partition bug HANDOVER records as
   #7. Fixing it means aligning **both** bands and the tags, and it invalidates HANDOVER
   §9's "no story truncated mid-sentence" claim — `corpus/stories/PT010-*.txt` ends
   mid-sentence. The open question is larger than PT010: **how many other tellings invented
   their resolution?** Answerable by checking each adapted ending against the source
   *continuation* — the check the fan-out got wrong by reading only the truncated chapter
   record. Do not trust a scan for this; the PT010 agent's failure was reading the wrong file.
2. **PT003** — its verifier hallucinated; needs a human read. Ending may name the wrong jackal.
3. **PT059** — band-agreement mechanism unconfirmed against source.
4. **PT084** — verifier rejected; also needs `build_story_tags.py` rerun.
5. **PT017** — its draft agent died on an API error; never ran.
6. **Then** the residual judgement calls: PT025 (done, `C5`→1) · **PT060 9+ child-marriage
   line** · **PT022's 9+ telling is 157 words** vs the 500–1500 target.

**Applied and verified:** PT027, PT031, PT086, PT082, PT004, PT023, PT025 (14 edits). All
four project checks green. See the session log.

**Do not trust a mechanical scan for the truncation class.** A fourth detector was built
and failed (recall 1/6 on known cases) — see the session log. Reading is the detector.

**Resolved:** PT034 `@5` — confirmed to stand. No death, no violence; the only content is
the caged parrot's shouted threat, which sits below both the fable-death tier (`@6`) and
the graphic-violence tier (`@7`).

**Not reachable:** Step 3 telemetry and Step 4 co-read — both on an app/player nobody owns.
**Also open:** selection is a binary at cold start; PT090 to delete; see §Open items.
**Corrected earlier:** `HANDOVER.md` §7's readability targets disagreed with `adapt.py`'s
`BANDS` — the table now matches the code that actually gates a band.



**Verify current state is intact:**
```bash
cd /Users/omkarpujeri/Desktop/Projects/panchatantra story
python3 -m engine.demo                          # engine self-check, prints coverage
python3 scripts/build_story_tags.py --check     # 80 records
python3 scripts/build_story_items.py --check    # 242 measurement + 485 discussion
python3 scripts/check_corpus.py                 # original corpus integrity
python3 scripts/review.py --list                # review progress, served-first
python3 scripts/review.py --flag                # flagged rows left
```

---

## Who owns what

| | owns |
|---|---|
| **Omkar** | the adaptive engine — story parameter tagging, skill/age mapping, story selection |
| **Team-mate** | video generation — consumes the `video_brief` block |

**The tagging schema is the handoff contract.** `video_brief` is the team-mate's half;
`skills` / `age_map` / `attention_load` / `calibration` are the engine's half; the shared
spine is `story_id` / `title` / `band` / `moral` / `themes` / `characters`.

---

## DONE

### Steps 0–1 (this session)

| # | step | artifacts |
|---|---|---|
| 0 | Tag 10 pilot stories | `corpus/story_tags.json`, `scripts/build_story_tags.py` |
| 1 | Question banks (measurement + discussion) | `corpus/story_items.json`, `scripts/build_story_items.py` |
| 2 | **Engine v0** (Elo, cold-start off priors) | `engine/` — `state.py`, `select.py`, `update.py`, `demo.py` |
| 6 | **Scale tagging 10 → 80** | `data/story_tags_authored.json` (new), rewritten `scripts/build_story_tags.py` |

**Step 0 — `story_tags.json` (10 records).** Per story: `age_map` (bands + sub-age +
rationale), per-band `readability`, `moral`, `themes`, `characters`, `skills` (M1–M5,
C1–C6 as ordinal 0–3 priors), `attention_load`, `video_brief`, empty `calibration`.

**Step 1 — `story_items.json`.** **Two collections with opposite band rules:**
- `measurement[]` — 32 mcq, auto-scored, **band-invariant**. Difficulty is per-item
  (`difficulty_prior` → calibrated `difficulty_b`); `suitable_from_age` is a *hint*,
  never a filter.
- `discussion[]` — 42 open prompts (20 need an adult), **band-specific**, never scored.

**Step 2 — `engine/` (v0).** Elo, one rating per `(child, skill)`. Reads the corpus,
writes child state; **does not write `story_tags.json`** — calibration stays a later
step.

| module | what |
|---|---|
| `state.py` | `ChildState` (age → band/sub-band, per-skill ratings, capacity), JSON save/load |
| `select.py` | schema §4 steps 1–5, in order |
| `update.py` | Elo update from answered items; folds a finished story back in |
| `demo.py` | runnable self-check + the usage example (`python3 -m engine.demo`) |

Selection: **filter** on `min_age`/`max_age` (real age) → **pace** on
`duration_sec <= capacity × 1.2` → **novelty** (hard-exclude the last 3 story ids,
fall back if that would starve the pool) → **score** by largest gap to mastery among
the skills the story actually exercises → argmax.

Two things worth knowing:
- **Novelty is an exclusion, not a penalty.** A mastery gap is ~250 rating points; no
  penalty small enough to be safe outbids that. A soft theme/character penalty still
  runs on top, for a *different* story about the same jackal.
- **The self-check caught a real bug in its own author.** The first `capacity`
  assertion used 120s; a 6-year-old actually gets 120 + 45×2 = 210s. Fixed the test.

**Step 6 — tags scaled 10 → 80.** Two structural changes before any authoring:

1. **The authored table moved out of the script into `data/story_tags_authored.json`.**
   This step is *reviewing model-authored proposals*, and a JSON drafts file is
   reviewable in a way a Python literal is not. The 10 existing entries were extracted
   by executing the module, not retyped — a rebuild of those 10 produces byte-identical
   records, which is how the refactor was checked.
2. **The pilot lock came off, and completeness replaced it.** The old `validate()`
   asserted `len(stories) == len(PILOT)`. It now asserts every story **with adapted
   text** has an entry and names the ones that don't. That gate was verified by
   watching it fail with exactly 70 missing before authoring.

**The real count is 80, not 145.** 145 is band-files; 90 is story records; 81 have
adapted text; 1 (PT090) is a duplicate. The plan and two earlier messages said "135" —
that was wrong.

Authoring was fanned out across 9 parallel agents, each reading its own stories'
adapted text and returning tags. Result:

| | |
|---|---|
| pool at age 4 | 2 → **9** |
| pool at age 5 | 2 → **21** |
| pool at age 6 | 3 → **40** |
| pool at age 9 | 9 → **77** |
| forced repeats in 8 draws | **none at any age 4–11** |
| divergence, strong vs weak child | ❌ **still identical** — see below |

**What Step 6 did and did not fix.** The pool problem is solved; the criterion that
strong and weak children get different sequences is **not** met, and the cause is
measurement coverage, not selection: only 10 of 80 stories carry questions, so a served
story usually yields no mastery signal and the ratings barely move (a 39-point gap
between a child who answers everything right and one who answers everything wrong).
Tags were the approved scope; items are the follow-on.

### Earlier: corpus intake (this session)
Team-mate returned `~/Downloads/corpus` + `~/Downloads/panchatantra_adapted_package`.
Verified, then merged:

| check | result |
|---|---|
| Adapted, not copied | ✅ spot-read PT016; faithful, real simplification |
| Readability (project's own `readability.py`) | ✅ 4-9 median FK 3.1 / 10.1 wps — on target |
| Excluded stories absent | ✅ none of the 6 `EXCLUDE` stories adapted |
| Truncation | ✅ every file ends on sentence punctuation |
| Coverage | 64 (4-9) + 81 (9+) English; **Hindi 0 files** |

**Merged:** `corpus/age/{4-9,9+}/` (+ manifests), `corpus/panchatantra_adapted.json`,
rewritten `scripts/adapt.py`, `data/adapt_config.json`, `data/prompts/`.
**Not merged:** `_rejected/` (quarantine folder — still in `~/Downloads/corpus/`).

### Also done

- `PRODUCT_RESEARCH.md` — verified feasibility review (5 angles, 23 sources, 25 claims
  adversarially checked, 24 survived).
- `STORY_TAGGING_SCHEMA.md` — the parameter spec the engine selects on.

---

## TODO — earlier plan, superseded

> **Superseded.** This is the pre-2026-10-13 plan; the live resume point is the
> **⏭ RESUME HERE** at the top of this file and the newest session entry at the bottom.
> Kept for the reasoning. Steps 3–5 and 7 below are still accurate (all blocked on the app).

| # | step | notes |
|---|---|---|
| ~~2~~ | ~~Engine v0~~ | ✅ done earlier this session — `engine/`, Elo, cold-start off priors |
| ~~6~~ | ~~Scale tagging 10 → 145~~ | ✅ done. **Correction: 80 stories, not 145** — 145 is band-files, 90 is story records, 81 have text |
| ~~6b~~ | ~~Items for the other 70 stories~~ | ✅ done — `data/story_items_authored.json`. 10 → 82 stories, **250 measurement + 495 discussion** (grew from the 242+485 first written) |
| ~~6c~~ | ~~Two engine selection bugs~~ | ✅ done — `engine/select.py` `reading_band` and `_score`. **Selection had been a no-op.** |
| 3 | Telemetry | time-on-task, drop-off, replays — feeds the attention *demand* ramp. **Blocked on an app** |
| 4 | **Co-read mode** | the evidence-aligned differentiator; unlocks the `requires_adult` prompts and is the only path to M4/M5 |
| 5 | Dashboard | trends + uncertainty, **never** "improvement" |
| 6d | **Review the drafts** | 17 served stories read (model pass; **all fixes applied**). **53 drafts still unread + the whole human review.** `_draft: true` on 70/70 |
| 7 | **The app / player** | **nobody owns this.** Blocks steps 3, 4 and 5 |

**Unscheduled but worth doing:**
- The pipeline's 9+ targets are looser than the brief (FK to 8.5 not 6.5, wps to 18.5
  not 16) — **needs a decision**, not a cleanup.

### Cleanup — done (same session)

| item | resolution |
|---|---|
| `HANDOVER.md` §10 stale ("no story has been rewritten yet") | ✅ rewritten; §10 now lists what is *actually* outstanding |
| `PT004` manifest metric counted a leaked line | ✅ recomputed — 207 → **175 words**, FK 4.9 → 4.6 |
| `The moral:` format deviation | ✅ 3 files normalised to `Moral:` (PT077 4-9, PT077 9+, PT038 9+) |
| `_rejected/` audit trail not copied in | ✅ 5 files → `corpus/age/9+/_rejected/` |
| "9 files have no `Moral:` line" | **not a defect — left as-is.** See below |

**On the remaining 6 files with no `Moral:` line** (PT004, PT007, PT020, PT025,
PT048, PT076, all `scoped_to_fable=false`): their source is an **unscoped frame
chapter**, and the fable's moral lives in a **verse** — which the brief says to drop.
So they legitimately have no moral. Adding one would violate the brief's "do not add a
moral explanation" rule, so they stay as-is by design, not by omission.

---

## Artifacts

| file | what |
|---|---|
| `PRODUCT_RESEARCH.md` | feasibility verdict + 10 cited sources. **Read before designing anything parent-facing.** |
| `STORY_TAGGING_SCHEMA.md` | the parameter spec (§3 = the two question banks) |
| `WORKLOG.md` | this file |
| `corpus/story_tags.json` | **82** tagged stories (schema v1.0) — was 10, then 80 |
| `corpus/story_items.json` | 250 measurement items + 495 discussion prompts (schema v2.0) |
| `data/story_tags_authored.json` | **the review artifact** — authored judgment for all 82 stories; `_draft: true` = model-drafted, unreviewed |
| `data/story_items_authored.json` | **the review artifact, questions** — 82 stories of mcq + discussion rows; same `_draft` flag |
| `data/census_2026-10-13_findings.md` | **the resolution census** — 142 tellings audited, 16 defect stories found and fixed |
| `data/apply_content_fixes_backup.json` | **the only undo** — previous contents of every band file any script rewrote (no git) |
| `engine/` | **the adaptive engine v0** — `python3 -m engine.demo` runs the self-check |
| `scripts/build_story_tags.py` | tag builder + validator (`--check`) |
| `scripts/build_story_items.py` | item-bank builder + validator (`--check`) |
| `scripts/shuffle_options.py` | de-bias MCQ answer position (idempotent; drafts only) |
| `scripts/fix_length_tell.py` | rewrite options so the correct answer isn't the longest (served items) |
| `scripts/fix_pt022_graft.py` | trim PT022's 9+ telling back to the fish fable |
| `scripts/review.py` | review the drafts — `--list`, `--flag`, `<ID>`, `--approve` |
| `corpus/age/{4-9,9+}/` | 145 adapted English stories + manifests |
| `corpus/panchatantra_adapted.json` | consolidated adapted corpus |
| `scripts/adapt.py` | the (rewritten) generation pipeline + `--check` validator |

**Pilot stories** (`adapt.py` `PILOT_STORIES`): PT005, PT008, PT012, PT015, PT016,
PT021, PT033, PT045, PT062, PT065.

---

## Decisions (do not re-litigate)

1. **Hindi is OUT OF SCOPE — removed, not deferred.** User decision 2026-10-13. English is the
   whole scope. (`4-9-hi/` and `9+-hi/` stay empty.) This supersedes the earlier "deferred, not
   cancelled" entry — do not re-open it as a pending decision.
2. **`video_brief` is the handoff contract** to the video workstream.
3. **Sub-band precision** (`min_age`/`max_age`) because 4-9 spans five years. Storage
   bands stay `4-9`/`9+`; serving is graded (4-6 / 7-9 / 10+).
4. **Measurement is band-invariant; discussion is band-specific.** Opposite rules on
   purpose — comparability is the point of one, depth is the point of the other.
5. **Difficulty is never a band exclusion.** A young child answering a hard item wrongly
   is *signal*, not breakage.
6. **Open moral responses are never auto-scored.** MCQ only.
7. **Attention is a story *demand* parameter, not a mastered skill.**
8. **Authored tags are priors; the engine calibrates from response data.**
9. **The engine lives in `engine/` here as a prototype, to port into the app later**
   (locked with the user this session). Runnable against the pilot data now, and it
   defines the contract the app shell consumes. `engine/__init__.py` is that contract.
10. **Elo first, not BKT** (locked this session). Cold-starts trivially off the priors;
    BKT needs response volume per skill and this is 32 items. Swap once there's volume.
11. **The engine requires the child's real age**, not just the band (locked this
    session) — otherwise `min_age`/`max_age` and the whole sub-band split is dead code.
    `ChildState.new` rejects a non-int age outside 3..15.

---

## Open items / caveats

- **Selection was a no-op until this session, and the fix is only partial.** `_score`
  computed `max((gap, prior))` and then *returned only the gap*, discarding the prior —
  and since all 80 stories exercise all six C skills (every one is `prior > 0`), the max
  gap was identical everywhere. Measured spread across 59 eligible stories at age 8:
  **0.00**. Which story a child saw was decided by story order and the novelty rotation,
  at 10 stories as much as at 80. Weighted by centrality the spread is now 73.33 and the
  acceptance test passes — but ties are still common, because most stories have *some*
  skill at prior 3 matching any weakness. The signal is coarse; do not read a served
  sequence as a tight fit to a child's ability.
- **Selection still does not respond to absolute level.** Add +400 to every rating of a
  child and they get the identical sequence. The score is built on gaps *between* skills,
  and a uniform shift moves them all together. Matching story difficulty to a level needs
  a difficulty term — a separate change, not a bug fix.
- **The review flag is cleared, and that does NOT mean the entries are good.**
  `_draft` was popped from all 70 entries on 2026-10-01 at the user's instruction.
  `review.py --approve` records **nothing** — no reviewer, no date, no note — so the
  cleared flag is an assertion with no evidence behind it, and it now distinguishes
  nothing. A second pass over the 18 served stories then found 7 defects the "complete"
  review had missed. **Treat `_draft` as decorative until it records who read what.**
  The other 52 stories the engine does not reach remain unread.
- **The item drafts carried a gameable answer-position bias — 65% of answer keys sat at
  position A** (`{0:136, 1:62, 2:10, 3:2}` over 210 draft rows): pick the first option,
  score 65% without reading. **Fixed** mechanically by `scripts/shuffle_options.py`
  (`{0:35, 1:66, 2:59, 3:50}` after), drafts only — the human-authored pilot rows had no
  such bias (`{0:4, 1:22, 2:6}`). The shuffle is idempotent and content-seeded, so the
  authored file is exactly what gets served.
- **The item drafts carried a length tell — the correct option was the only longest in
  156/210 draft rows (74%)**: pick the longest option, score 74% without reading.
  **Fixed for the 35 items in served stories** (`scripts/fix_length_tell.py` rewrites
  the options so the correct answer is strictly shorter than the longest, index
  unchanged). **121 remain**, all in stories no child reaches yet — left flagged by
  `review.py --flag` rather than rewritten blind. Unlike position, length is authoring,
  not a transform: matching a distractor's length means rewriting its text, and padding
  options to equal length makes them worse.
- **`suitable_from_age` disagrees with the story's `min_age` on 45 draft rows.**
  (`review.py --flag`.) Either the hint is miscalibrated or the items are pitched above
  their story's youngest reader. Not a defect on its own — measurement is band-invariant
  by design — but it wants a decision.
- **All six C skills are `prior > 0` on every one of the 80 stories.** That is what made
  the scoring degenerate, and it is also a tagging-quality signal: "prior > 0" carries
  almost no information for C skills, only for M skills (which range 0–5 per story).
- **Selection rotates through ~4 stories per child, whatever the pool size.** Measured
  at every age from 4 to 11: 4 distinct stories in 8 draws. Not a repeat (the novelty
  window holds) but a lack of exploration — the top few stories by mastery gap are the
  same for every cold-started child, so novelty just cycles them. Worth revisiting when
  there is real response data to spread the gaps.
- **The one live age judgement call from the review: PT034 at 5 — RESOLVED.** Second
  read confirmed it stands. Its 4-9 text contains the caged parrot shouting "Bind the
  king! Kill him!", but no death and no violence; that sits below the fable-death tier
  (`@6`) and well below the graphic-violence tier (`@7`). Moving it to 6 remains a
  one-word edit if you read it otherwise.
- **All 80 entries use a flat `skills` block, but two-band stories have two tellings.**
  A 4-year-old gets the softened 4-9 text while the priors were judged largely from the
  9+ text. The schema allows a per-band dict and nothing uses it. Fold this into the
  items step.
- **PT090 is a duplicate of PT002 and is deliberately NOT tagged.** Same "three
  blockhead sons" frame, same king and city, only the sons' names differ and those are
  borrowed from other stories. Titled "front matter". It sits in `_skipped` in
  `data/story_tags_authored.json` with that reason — confirm and delete it from the
  corpus rather than tagging it.
- **`apply_story` only ramps capacity upward.** A drop-off leaves it unchanged rather
  than shrinking it, because shrinking needs the *point* of drop-off — which is Step 3
  telemetry, not a guess. Until then a child who abandons every story still ramps.
- **The engine never writes `calibration` back to `story_tags.json`.** Schema §4
  forbids calibrating from a single response; that needs `n_observations` across many
  children. `difficulty_b` stays null and the priors stay authoritative for v0.
- **PT016's `age_map` overrules curation** — set to serve both bands against a
  `NINE_PLUS` verdict, on `HANDOVER.md` §5 grounds (the screen blamed the fable for the
  frame's verse). One line in `build_story_tags.py` if the user disagrees.
- **`skills` priors and `age_map` are proposals for human review**, same caveat the
  corpus README applies to curation.
- **PT013 and PT047 are not missing — they failed validation** and sit in
  `_rejected/`. Both are long frame/chain narratives that blew the 9+ words-per-sentence
  target. The real 9+ gap is 2 stories, not 3.
- **`_rejected/` is now in the project** at `corpus/age/9+/_rejected/` (6 files) — the
  audit trail for the PT013/PT047 failures, three earlier drafts that were later
  regenerated successfully, and **PT022's contaminated 9+ telling** (see the session log).

---

## Key constraints from the research (why the design is shaped this way)

Violating any of these means shipping a claim the evidence does not support:

- **Attention training does not improve attention** (CI includes zero) — so model demand,
  never claim improvement.
- **A child's session-to-session score change is mostly noise** (K-CPT test-retest
  r=.57) — report trends over many sessions, never single deltas.
- **Rater bias inflates apparent gains ~3.4×** (unblinded d=0.48 vs objective d=0.14).
- **The active ingredient in the moral-reasoning literature is adult-led discussion** —
  which a solo app removes. Hence the co-read mode.
- **Do not let an LLM "judge" a child's morality** and surface it to parents — LLM
  inference of deep psychological states from brief interaction is biased and unreliable.
- **Dashboard numbers come from comprehension (measured); moral reasoning appears as
  discussion (visible, unscored).**

---

## Session log

### 2026-10-01

Corpus intake + verification and merge → feasibility research → tagging schema →
Step 0 (pilot tags) → Step 1 (question banks, restructured same day to two collections).

**Validator catches recorded (all fixed):**
1. Over-tagged **M5** on 5 consequence stories → fixed the *tags*, not the rule.
2. `dialogue_lines` read only the richer band's text → now max across bands.
3. First item bank had 9 items band-excluded → restructured to two collections.
4. Validator's own "every M skill needs both bands" rule was too broad (M5 is 9+-only)
   → fixed the *rule*, not the data.

**Step 2 — engine v0 (same session).** Both v0 decisions put to the user and locked
(9–11 below), then built:

```
python3 -m engine.demo
corpus: 10 stories, 32 measurement, 42 discussion

strong-6   age  6  masteries   1125  capacity   281s  served ['PT005','PT012','PT045','PT005','PT005','PT012']
weak-6     age  6  masteries   1068  capacity   281s  served ['PT005','PT012','PT045','PT005','PT005','PT012']
strong-10  age 10  masteries   1198  capacity   523s  served ['PT008','PT012','PT015','PT062','PT008','PT012']

OK — engine v0 self-check passed
```

Correct answers beat wrong ones (1125 vs 1068), older children start higher and ramp
further (523s vs 281s), and the corpus is untouched.

**What the self-check caught, in order:**
1. **Its own author's arithmetic** — asserted a 6-year-old's capacity was 120s; the
   formula gives 120 + 45×2 = 210s. Fixed the assertion, not the formula.
2. **Novelty as a soft penalty does not work** — a 50-point nudge loses badly to a
   ~250-point mastery gap, and `PT005` was served 3× in 6 draws. Changed to a hard
   exclusion on the last 3 story ids, with a fallback so a small pool can't starve.
3. **Then confirmed the remaining repeat is not a bug** — age 6 has exactly 3 eligible
   stories, so the fallback firing is correct behaviour on a thin pilot pool.

**Step 6 — scaling the tags (same session).** Step 2's thin pool made the schema
unvalidatable, and the original gate ("scale only after the engine validates the schema")
turned out to be circular: validating selection needs a pool, and a pool needs scaling.
So this step unblocks the validation rather than the other way round.

The adaptation model was gone — `ollama` is not installed and `localhost:11434` is dead —
so there was no local drafter. `ANTHROPIC_*` is set in the env and `adapt.py` has an
`anthropic` provider branch, but the plan's chosen path was to author the drafts
directly, and that is what happened: 9 parallel agents, one batch each.

**Findings that changed the work:**
1. **The count was wrong everywhere, including in the approved plan.** "145" is
   band-files, not stories. 90 records, 81 with text, 1 a duplicate → **80 to tag, 70 to
   author**. Corrected in the plan's own text.
2. **PT090 ("front matter") is a duplicate of PT002** — same frame, same king and city,
   sons renamed after characters from other stories. Added a `_skipped` mechanism with a
   reason rather than silently dropping or blindly tagging it.
3. **The demo's own assertions were pilot-shaped and broke on a real corpus**: one
   demanded every story carry measurement items, another compared against the globally
   shortest story instead of the shortest *eligible* one, a third hardcoded age 14 as
   out-of-range (the new tags reach 14). All three were test bugs, all three surfaced by
   growth — which is the argument for scaling.
4. **Step 6 met one of its two criteria.** No forced repeats at any age 4–11 ✅. Strong
   and weak children still get identical sequences ❌ — 10/80 stories carry questions
   (12% coverage), so ratings barely separate (39 points). Items are now the top gap.

**Step 6 — the review pass (same session).** 15 entries pulled across bands, ages and
verdicts, shown with their youngest band's text so the age call could be checked.

**Two audits of my own were wrong before the third was right**, both worth recording
because both are easy to repeat:
1. **Checked `curation.reason` instead of the adapted text.** Curation describes the
   SOURCE story, before adaptation softens it. It flagged 8 stories as violent at
   min_age ≤ 5; almost all of that content is not in the 4-9 text a young child gets.
2. **Then flagged rationales that correctly explain the band difference** — PT049's
   rationale cites the 9+ killing *in order to say the 4-9 telling softens it*. Matching
   the word without reading the sentence marked correct reasoning as a defect.
3. The third check — harm in the band the child is actually served — showed the floors
   are right: every genuine death (PT010, PT017, PT022, PT025, PT030, PT038, PT052,
   PT072, PT080, PT083) is already floored at 6, and the other "hits" are
   *"pretend to be dead"*, *"was not dead"*, *"a dead calf"*.

**Outcome: no age changes made.** The drafts held up. One live judgement call is
recorded below.

**The one imprecision the review did confirm:** all 80 entries use a flat `skills`
block, but a two-band story has two tellings. A 4-year-old is served the softened 4-9
text while the priors were judged largely from the richer 9+ text. The schema allows
`skills` to be a per-band dict (`build_story_tags.py` says so in `meta.notes`) and
nothing uses it. Real, but it belongs with the items step, not here.

**Items step — questions for the other 70 stories (same session).** Same shape as the
tags: `MEASUREMENT`/`DISCUSSION` extracted out of `build_story_items.py` into
`data/story_items_authored.json` (verified byte-identical for the original 10), then 10
parallel agents authored the rest. Result: **242 measurement + 485 discussion, 80/80
stories, coverage 12% → 100%.**

The authoring rule that made it work: **write each measurement item answerable from the
*younger* band's text.** Measurement is band-invariant by design, so an item a 6-year-old
can answer from the softened telling is automatically answerable by the 10-year-old
reading the richer one. That is what removes the need for per-band skills.

Two validation failures, both predicted and both correct to reject: `PT042` and `PT066`
had M5 prompts in the 4-9 band. M5 is 9+-only by definition. Dropped the two rows.

**Two engine bugs the item work exposed — both pre-existing, neither visible before.**

1. **A 9-year-old served a 9+-only story got zero discussion prompts.**
   `serve_discussion` matched prompts on the child's *storage* band, and a 9-year-old's
   storage band is `4-9` while the story only had `9+` prompts. The band has to follow
   the text the child actually reads, not just their age. Added `reading_band()`; 17
   stories affected. This also let the validator rule be relaxed: a story now needs
   prompts for the bands a child could *reach*, not blanket "both bands" — 24 stories
   need one band, 46 need both.

2. **Story selection had never discriminated between stories at all.** `_score`
   computed `max((gap, prior))` and returned only the gap, discarding the prior; and
   because every story exercises all six C skills, the max gap was the *same number*
   for every story. Measured spread across 59 eligible stories: **0.00**. Story order
   and the novelty rotation were silently making the choice. Now weighted by centrality
   (spread 73.33).

   Worth recording how this surfaced: it looked like "Step 6's criterion 2 still fails,
   because only 12% of stories carry questions." That diagnosis was wrong — measurement
   coverage was never the cause. The cause was that the scoring function could not tell
   two stories apart, and a thin pool had hidden it since the beginning.

**Acceptance:**
```
                          before items   after
measurement coverage      10/80 (12%)    80/80 (100%)
strong vs weak, age 6     identical      DIFFER (4/8 shared)
mastery gap               39 points      67 points
```
`DIFFER` holds at every age 4–11, sharing 3–5 of 8 stories. The 9+-only discussion fix
returns 4 prompts where it returned 0.

**Review tooling + the MCQ bias audit (same session).** Before any human read, a
mechanical sweep of the item drafts — the same move that caught the two engine bugs.

**A third gameable defect, which no validator had watched for: answer *position*.**
`correct` is an index, so position is directly exploitable. Across the draft rows:

| | before | after |
|---|---|---|
| answer position (210 draft rows) | `{0:136, 1:62, 2:10, 3:2}` — 65% at A | `{0:35, 1:66, 2:59, 3:50}` |
| correct option is the only longest | 183/242 (75%) | **unchanged — see below** |

`scripts/shuffle_options.py` sorts each item's options into a canonical order, then
permutes them with a seed derived from the prompt. That makes it **idempotent** — a
second run is a no-op, verified — and independent of the order it finds, so what the
reviewer reads is exactly what gets served. No item uses an order-dependent option
("all of the above"), so the shuffle is safe. Only `_draft` entries are touched; the
32 human-authored pilot rows showed no position bias.

**The length tell is NOT mechanically fixable and was left alone.** Rewriting a
distractor to match the correct option's length is authoring, and padding options to
equal length makes them worse, not better — so it is surfaced for the human rather than
faked.

**`scripts/review.py`** does the three jobs of a review pass:

| command | job |
|---|---|
| `--list` | drafts left, `★` marks the 17 the engine actually reaches (review first) |
| `--flag` | mechanically-suspicious: 156 length-tell, 46 age-hint, 7 harm@≤6 |
| `<STORY_ID>` | tag draft + items + the served band text(s) on one screen |
| `<STORY_ID> --approve` | clear `_draft` (only after reading) |

It encodes the worklog's two hard-won rules: read the *adapted* text, never
`curation.reason`; and judge an age floor on harm in the band *actually served*, not
whether the word appears anywhere.

**Flags are candidates, not verdicts.** The harm scan's first run flagged PT084 for
"stable" (the `stab` prefix) and had a typo in the pattern — both fixed; it now returns
7. The age-floor review already judged genuine deaths floored at 6 to be correct, so the
scan only narrows the read.

**State after:** `_draft` is still `true` on 70/70 — the shuffle de-biases, it does not
review. Coverage unchanged (80/80), all four checks green, engine demo passes.

**The length tell — fixed for the served set, left flagged for the rest.** Where
position was a pure transform, length is authoring: the correct option carried a full
cause/effect clause while distractors stayed terse, so the fix is rewriting text.
`scripts/fix_length_tell.py` holds a hand-written patch for the **35 items in served
stories**, shortening the over-worded correct option (or lengthening a terse distractor)
so the answer is strictly *shorter* than the longest option — the answer key's index is
untouched, so correctness cannot break by construction. Applied as a set: idempotent.

Two caught by the script's own assertion, not by eye: PT017/C2 and PT020/C2 came out of
the first pass with the correct option *as* the max, and PT010/C2 came out a tie. The
assertion `len(correct) < max(len)` — stricter than the flag, which only catches a
*unique* longest — is what surfaced them. Worth keeping: a first draft of a rewrite pass
is not evidence the rewrite worked.

Remaining length-tell: **121 items, all in stories no child reaches**, still flagged by
`review.py --flag`. They will be reached once the difficulty term lands, so they are
deferred, not dismissed.

**State (final):** all four checks green; length-tell in served stories **35 → 0**;
position bias gone; `_draft` still `true` on 70/70.

**First-pass review of the 17 served stories (same session).** A *model* first pass — not
the human review the drafts still need. Four reviewers read each story's adapted band
text(s) and checked the measurement answer keys, discussion band-fit, age floor and tags;
I then independently re-checked every load-bearing finding against the text, because the
worklog's own rule is that two audits were wrong before the third was right.

**Verdict: 15 of 17 have issues. Only PT003 and PT086 are clean.**

**Defects in the ADAPTED TEXT — served content, so worse than any draft defect:**

| story | defect |
|---|---|
| **PT022** | ✅ **FIXED** (see below) — the 9+ telling grafted PT020's plover/ocean plot onto the fish fable and blended both morals; also carried "I'll burn myself" |
| **PT004** | ✅ **FIXED** — the 9+ telling killed the monkey ("the monkey was crushed") then had him found and interviewed; now "the monkey was hurt", and the rationale no longer says "crushed to death" |
| **PT020** | the 9+ telling is truncated — no resolution, no moral (204 words vs the 500–1500 target); `max_age 8` so never served |

**Age floors — resolved into two clean tiers:**
- **fable deaths at 6** — PT010, PT012, PT017, PT022, PT025 (already reviewed; stand).
- **graphic violence at 7** — PT023 (blinding) and PT027 (burning) stand; **PT035** ✅
  **FIXED** — was @5, raised to **7** (user call) to join them. Its own rationale already
  said the mutilation "keeps this out of the youngest tier", yet 5 sat inside the 4–6 tier.

**9+ discussion prompts that quote 4-9-only content** (verified against both tellings):
**✅ FIXED** — PT007 (M1), PT010 (M2, M3), PT017 (M1, M4). Each referenced a detail that
exists only in the 4-9 telling — "said he was a foolish man", "what really happened" to a
snake the 9+ telling never kills, "thought it would be boring", the caravan leader
"ordering" a shot the 9+ archer fires on his own. All five rewritten against the 9+ text.

**Schema conflicts — ✅ RESOLVED** (user call: make the doc describe reality):
- schema §3 scoped the measurement bank to `C1–C3, C6`, but **27 items use C4/C5**
  (24 `C5_inference`, 3 `C4_vocabulary`). The step-6b plan allowed any `C*`. → **§3 now
  reads `C1`–`C6`.** Separately flagged, *not* fixed: most of the 24 `C5` items test
  recall rather than inference — the schema now permits the label; it does not make it
  true.
- schema §6 said "every story has 4–6 items"; every story has 3. → **§6 now says 3**, and
  the validator's floor was raised **2 → 3** so doc, code and corpus agree.

**Tag defects:** ✅ PT082 theme `bad-advice` → `ignoring-good-advice` (the advice was
*good* and ignored); ✅ PT023's gnat and PT035's village chief added to `characters` —
both omitted. **Still open:** PT025 `C5` prior 3 and PT084 `C4` prior 3 look overstated,
and the Elephant-as-"victim" / Thief-as-"trickster" roles are arguable — judgement calls
left for the human.

> *(Historical entry — both of those closed later: PT025 `C5` → 1 on 2026-10-01, PT084
> `C4` → 2 on 2026-10-13. See the earlier 2026-10-13 entry.)*

**Small review fixes applied (same pass):**
- PT007 measurement item 2 — distractor A ("Godly always carried the treasure into the
  temple") echoed the true line *"He kept it under his arm always"*; replaced with a
  plainly-false option.
- PT059 M2 4-9 — a bare yes/no ("Did his plan work?") rewritten open.
- PT020 M3 4-9 — asked what happened *because* Sprawl didn't listen, but the 4-9 telling
  resolves harmlessly (*"the waves came and went, but they didn't hurt the plover's
  home"*); rewritten as a hypothetical consequence.

**`harm@≤6` resolved to known states** (the flag is candidates, not verdicts): real deaths
at the floor-6 tier — PT010, PT012, PT017, PT022, PT025 — stand. PT003 ("was not dead";
"Lively died" is a lie) and PT024 ("pretend to be dead") are the known false positives.
**PT034 @5 is still the one open call** — the caged parrot shouting "Bind the king! Kill
him!" — exactly as the earlier review recorded. It only *appeared* in the flag now because
raising PT035 to 7 shifted the served set.

**Refuted — do not act:** the reviewers flagged PT020 / PT031 / PT035 as "missing 9+
prompts". They are not — `required_bands` is `['4-9']` for all three (max_age ≤ 9, so
every reader is storage-band 4-9). The validator is right and the reviewers conflated
`max_age 9` with "served at 9+".

**`_draft` stays `true` on all 17 — nothing reviewed here is approvable as-is.**

**PT022's 9+ telling fixed — the worst finding of the review (same session).**

Root cause was *not* an adaptation slip. PT022's SOURCE chapter is the fish fable with
the plover tale woven on as a tail (*"'My dear,' said the plover, 'why do you think me
like Fatalist?'"*) — the nested-frame structure again, and the plover tale also stands
alone as PT020. The 4-9 adapter trimmed to the fable; the 9+ adapter adapted the whole
chapter, so the served 9+ text was two stories with a blended moral.

`scripts/fix_pt022_graft.py` trims the 9+ telling to the fable alone (384 → 157 words),
matching the 4-9 scope, with the fable's moral. The original is kept in
`corpus/age/9+/_rejected/`. Synced: the band file, `panchatantra_adapted.json`, the 9+
manifest, and PT022's tag `rationale` (which still cited the removed frame). The script
is guarded — a second run asserts and refuses rather than silently no-op'ing.

It still meets the 9+ readability targets (wps 11.2, FK 5.4). **But it is 157 words
against the 500–1500 target, and the untrimmed one was 384 — also under.** So the length
gap is pre-existing and wants a real 9+ re-adaptation of the fable; this trim only
removes the wrong story. All four checks green after.

**Served set shifted — two unreviewed drafts are now reachable.** Raising PT035's floor
to 7 changed which stories the engine reaches at ages 4–11: **PT035 dropped out**, and
**PT034 and PT060 entered**. Both are drafts the review did not cover (PT034 is also the
flagged @5 harm call). The served-draft count went **17 → 18**. **Read PT034 and PT060
before calling the served set clean** — this is the cheapest next read.

**Could the contamination be elsewhere? No reliable automated detector found.** Three
tried; all failed, and the failures are worth keeping:

1. **Cross-story character-name scan** — false negative on the known-bad text. The graft
   says "a plover", never naming PT020's Sprawl or Constance, so nothing matched.
2. **Source shingle-containment scan** (does chapter A contain story B's fable?) — 125
   hit pairs, but the Panchatantra *nests* stories, so chapters legitimately share text.
   Pure noise; cannot separate nesting from error.
3. **9+/4-9 length ratio** — this one *did* discriminate: PT022 was 2.4× while the median
   is 1.35×, because it held two stories. But after the fix the new top outlier, **PT054
   (2.34×, 112→262w)**, may just be a legitimately richer telling.

**Conclusion: contamination here can only be found by reading — which is the review
itself.** PT054, the one lead those scans produced, was then read and is **CLEAN** — its
9+ telling is a legitimately richer version of the same swan story (112→262w), not a
graft. No other lead remains. Do not treat the scans themselves as a clean bill of health.

---

**PT034 + PT060 read — the two stories the served set gained (next session).** The review
above moved the served-draft count 17 → 18 by raising PT035's floor. **PT034** and
**PT060** were the two that entered, and neither had been read. This is that read. Both
had a defect.

**PT034, both tellings — the kind parrot was made to describe itself as the cruel one.**
The hermitage parrot is the kindly one, raised by holy men. Both adapted tellings handed
it the *hunter-raised* chick's explanation:

| | adapted (before) | source |
|---|---|---|
| 4-9 | the parrot explained, *"I was once like that parrot. I was taught to be cruel."* | the parrot *relates the course of its own life* — the good one — and lets the contrast with the hunter-raised chick carry the moral |
| 9+ | *"It had learned to mimic the voices of its surroundings and had been taught to deceive."* | same |

This is not a slip of emphasis — it deletes the story's mechanism. The fable works only
because the two parrots differ *by education*; naming the wrong parrot as the cruel one
leaves the moral ("Education shows its true results") with nothing to attach to.

Only the 4-9 telling is served — PT034's `max_age` is 9, so no child ever lands in storage
band 9+ and its 9+ telling is **unreachable**. The 9+ telling was still fixed: one word
from being served, and free to fix while the file is open.

It also makes the item bank strictly better. The `C3` item asks *why the caged parrot
shouted "Kill him!"*, keyed "It had been taught to be cruel" — before the fix those words
belonged to the wrong bird. No item text changed.

**PT060, 9+ — the moon is invented.** The 9+ telling lists the suitors as "the sun, the
moon, the wind, or the mountain". Ryder's chain is sun → cloud → wind → mountain → mouse,
and the 4-9 telling has the cloud; the moon occurs in the source *only* inside the
child-marriage verse the adaptation drops. It is a suitor named once and never summoned.
One word: moon → cloud.

The tag got this right — PT060's own `rationale` already said "the sun, cloud, wind and
mountain". That is the useful part: the tag was correct and the *adapted text* was what
had drifted.

**PT034 `@5` — the one open age call — resolved: it stands.** The served 4-9 text has no
death and no violence. The only candidate is the caged parrot shouting "Bind the king!
Kill him!" — immediately framed as mimicry and never carried out. That sits below the
fable-death tier (`@6`: PT010, PT012, PT017, PT022, PT025) and well below the
graphic-violence tier (`@7`: PT023 blinding, PT027 burning, PT035 mutilation). A
5-year-old being given gentler content than the death tier is consistent; the floor holds.

**Two judgement calls it produced — surfaced, not fixed:**

- **PT060 9+ carries the child-marriage line.** "Yajnavalkya agreed, saying that a girl
  should be married before she developed womanhood." It is faithful (it compresses Ryder's
  verse) and 9+ only, so no 4-9 child sees it — but it is precisely the niti-shastra
  content this project's curation exists to catch, and it is served to 10- and
  11-year-olds. It is a *plot* point (it is why she marries at twelve), so removing it
  needs a replacement sentence, not a deletion. Not a mechanical fix.
- **Minor, PT060 9+:** the chain has a gap. The girl rejects the sun, the cloud and the
  wind, but the mountain is never offered to her — the holy man asks the mountain whether
  it is superior and it names the mouse. Wrong for "Finally", harmless in practice.

**A guard caught its own author — and that is how a doc drift surfaced.** The fix script
asserts the edited telling stays inside its readability target. The first draft of the
PT034 9+ replacement (one longer clause) came out at fk 7.14 / wps 16.31 and the assert
refused to write. Two things fell out of that:

1. Rewritten as three short sentences, the replacement now reads *better* than what it
   replaced (fk 6.65 → 6.60, wps 15.62 → 15.06).
2. **The targets the script was checking were the wrong ones.** `HANDOVER.md` §7 published
   4-9 as fk 1.0–4.0 / wps 5–10 and 9+ as fk 3.5–6.5 / wps 9–16. `adapt.py`'s own `BANDS`
   — the thing that actually gates a band — uses **1.0–4.8 / 5.0–13.0** and
   **3.5–8.5 / 8.0–18.5**, plus a syllables/word ceiling the doc omits. Under the published
   numbers PT034's 9+ telling was already 0.15 over *before* any edit and PT060's 4-9 is
   over on words/sentence (10.65 vs 10); under the real numbers both are in band, which is
   what `adapt.py --band <b> --check` reports. **§7 is now corrected**, and the script
   imports `BANDS` rather than restating it so it cannot drift again. This is the same
   shape as the schema §3/§6 drift already recorded — the second time a doc described a
   corpus it no longer matched.

**Fixed with:** `scripts/fix_pt034_pt060_prose.py` — guarded (asserts the text to fix is
present, so a second run refuses rather than no-op'ing), idempotent, `--dry-run`, and it
syncs the band `.txt`, `panchatantra_adapted.json` and the band manifest together.

**`_draft` stays `true` on all 18 served stories.** A model pass with its findings applied
is still not the human review the flag exists for.

**State after:** all four project checks green (`engine.demo`, `check_corpus.py`,
`build_story_tags --check`, `build_story_items --check`), `adapt.py --check` green for both
bands, served-draft count unchanged at 18, and no served telling carries a known defect.

---

**Second pass over all 18 served stories — and the served set is NOT clean (next session).**

The human review was marked complete (`_draft` cleared on all 70). A second, independent
read of the 18 served stories then found **7 confirmed defects the first pass missed.**
The two passes disagree, so record the disagreement rather than the conclusion: a review
that returns "nothing needed changing" on 18 stories, when a later read finds 7 defects in
15 of them, was not reading for whether each **moral is earned by the telling**.

**Method, for the record.** Four parallel readers covered the 16 stories PT034/PT060 had
not. Every finding below was then re-checked by me against the raw text before being
recorded — the agents' unverified claims are listed separately and are *not* counted.

**Confirmed by reading the served text (7):**

| story | class | evidence |
|---|---|---|
| **PT003** both bands | truncation — moral unearned | 4-9 ends `"…planned to get rid of Lively"` → `"Moral: Lying and being jealous can lead to loss of friends."` Nothing shows a loss |
| **PT010** 9+ | truncation — 4-9 resolves, 9+ does not | 9+ ends `"The snake will take care of itself."` + a moral about a `downfall` never shown. 4-9: `"The snake died."` |
| **PT027** 9+ | truncation — 4-9 resolves, 9+ does not | 9+ ends at `"Strong had the monk's body burned."` 4-9 adds `"The monk didn't come back. He was just pretending."` |
| **PT031** 4-9 | set-up with no payoff | trial convened, `"Bring the goddess tomorrow."`, then the father's warning and the moral. No verdict |
| **PT086** 9+ | mis-assigned actor — nonsense sentence | `"The thief … decided to drop the thief from a high spot to save his own life."` PT086 is 9+-only, so this is its only telling |
| **PT059** both bands | the two tellings give *different plots* | 4-9: embracing another man makes the husband live 100 years. 9+: the husband's bad luck transfers to the lover |
| **PT082** 9+ prompt | quotes the *other* band's text | prompt: "stayed to **watch for farmers**"; 9+ text: "stay **by the hedge**" — the farmers line is in 4-9 only |

**Served status checked for each:** all reach a child except PT031's 9+ (`max_age` 9) and
PT020's 9+ (`max_age` 8). PT086 is 9+-only.

**Agent-reported, NOT verified by me — read before acting:** PT017 (9+ invents a "threat"
motive where 4-9 and the source use the omen) · PT023 (9+ moral unearned; elephant labelled
`victim` though it is the aggressor) · PT025 (9+ garbled causal beat; `C5` prior 3 holds up
as overstated) · PT004 (item keys "hungry" where the text says "curious") · PT084 (`C4`
prior 3 overstated). PT022 and PT024 came back **clean**, matching this log.

**The root cause is structural, and it explains PT020 too.** Every source *chapter* ends on
a hand-off — `"And the jackal told the story of…"`, `"And his father told the story of…"`.
The nested-frame partition means the chapter genuinely does not contain the fable's own
ending. So each adapter had to **author** an ending to make a standalone story, and the 4-9
adapter usually did while the 9+ adapter often stopped at the hand-off. That is why the
class is concentrated in 9+. It is the same partition that produced PT022's graft.

**A fourth automated detector was built and failed — do not build a fifth.**
The hypothesis was testable: if a telling stops at the hand-off, its moral should name an
outcome its body never shows. Implemented and scored against the six known cases:
**recall 1/6.** It found PT020 (by a "no moral at all" route) and missed every real one.
The signal does not live in the moral's wording or the telling's length — it lives in
whether the *plot resolves*, and no regex reads a plot. This matches the three failed
detectors already recorded above. **Reading is the detector**, and the served set is 18
stories, which is small enough that reading it is the right cost.

**Fixing the truncations is authoring, not a transform.** A resolving beat has to be
written. The guide is already on the page: for PT010 and PT027 the **4-9 telling shows
exactly what the 9+ one is missing**, so the fix is to bring the 9+ ending up to the 4-9
resolution rather than invent anything. PT003 and PT031 have no resolving sibling and need
a real ending. That is why this needs a human sign-off rather than a script.

---

## ✅ DONE — the fan-out, and what it actually produced

Ran 2026-10-01 on the user's instruction ("complete all the fixes by fanning out multiple
sub agents"): 23 agents, 12 draft → 12 verify, ~948k subagent tokens. Raw output kept at
`data/review_2026-10-01_workflow.json` so every proposal is auditable.

**Applied — 7 stories, 14 edits**, via `scripts/apply_review_fixes.py` (guarded, idempotent,
`--dry-run`; reads its edits from the workflow JSON so no string is ever retyped):

| story | what changed |
|---|---|
| **PT027** 9+ | added the payoff: the monk never came back, he had been pretending |
| **PT031** 4-9 | added the trial outcome — father hiding in the tree, trick exposed |
| **PT086** 9+ | `"decided to drop the thief"` → the thief drops himself, per source line 13771; dropped the unearned "just like the fiend" |
| **PT082** 9+ | M1 prompt reworded to match the 9+ text ("stayed by the hedge") not the 4-9 one |
| **PT004** | text/option/stem/moral: monkey is curious, not hungry; "hurt" not "crushed" |
| **PT023** | 9+ moral now earned by the text; Elephant role `victim` → `antagonist` |
| **PT025** | the garbled causal beat now matches the 4-9 logic; `C5` prior 3 → 1 |

All checks green after: `engine.demo`, `check_corpus.py`, both `--check` validators,
`adapt.py --check` for both bands. Derived artifacts rebuilt (`adapt.py --export-json`,
`build_story_tags.py`, `build_story_items.py`).

**Held — 5, deliberately, and each needs a decision not a patch:**

- **PT010 — the find of the session.** The 4-9 telling's *fish-bone death is fabricated*:
  the word `bone` appears nowhere in PT010's source chapter, and the real ending is the
  **golden-chain device** (`panchatantra_complete.txt:2768-2774`) — the crow-hen steals a
  gold chain, drops it in the snake's hole, the king's men club the snake. The divergence
  came from the same heading-partition that HANDOVER documents as bug #7. This is why the
  copy-up strategy is not sound in general: **sibling agreement is evidence, not authority.**
- **HANDOVER §9 needs correcting.** It claims *"No story truncated mid-sentence | clean"*.
  `corpus/stories/PT010-*.txt` ends mid-sentence at `"And the jackal told the story of"`.
  That check must be re-run against the corpus, not trusted.
- **PT003** — its verifier hallucinated (it cited `"The bull lay dead"` in the 9+ band;
  I printed that whole file and the line does not exist). Its other point may hold: the
  draft ending names Cheek where the source names Victor. Needs a human read, not a re-run.
- **PT059** — the band-agreement mechanism could not be confirmed against the source.
- **PT084** — verifier rejected it outright; also needs the `build_story_tags.py` rerun.
- **PT017** — its draft agent died on an API error and never ran. Zero work done.

**Three own-goals in the apply script, all caught by its own guards, worth recording:**
1. The `characters` tag branch unpacked the *index* (`2`) instead of the role, writing
   `["Elephant","elephant",2]` into PT023. Caught by re-reading the file, repaired, and the
   re-run's idempotence check is what surfaced it — a write that "succeeded" was still wrong.
2. Append-style edits (`new` contains `old`) were not idempotent: the "old present" check
   re-fired forever and would have duplicated PT031's ending on a second run. Fixed by
   testing for `new` **first**.
3. The dry-run's summary line counted JSON/tag applies as "no-ops", reading as *nothing to
   do* when it meant the opposite.

None of these reached the corpus undetected, but all three are the same species: a guard
that reports success without checking. The project keeps relearning this.

---

## ⏳ SUPERSEDED — the fan-out as planned

Started on the user's instruction ("complete all the fixes by fanning out multiple sub
agents"). **Scope is exactly these 12 stories and nothing else.** No agent may touch a
story not on this list, may not rewrite a telling beyond the defect named, and may not
edit files — agents return edits as data and one guarded script applies them all, because
parallel writers to the same band file would clobber each other.

Each item gets a **draft** agent that verifies the claim and proposes exact `old` → `new`
strings, then an **adversarial verify** agent that tries to refute it (checks the `old`
string is verbatim, that `new` resolves the defect, that it invents nothing absent from
the source, and that it stays inside the band's readability targets). Refuting is an
accepted good outcome — 5 of the 12 are unverified claims that may be wrong.

| # | story | class | what the agent is asked to do |
|---|---|---|---|
| 1 | **PT010** 9+ | copy-up | bring the 9+ ending up to the snake's death, which the 4-9 telling and source already have |
| 2 | **PT027** 9+ | copy-up | add the 4-9 telling's payoff ("The monk didn't come back") |
| 3 | **PT003** both | AUTHOR | write a resolving ending for each band; no sibling to copy |
| 4 | **PT031** 4-9 | AUTHOR | pay off the abandoned trial, non-violent, ages 5-9 (9+ not served) |
| 5 | **PT059** both | CHOICE | pick the source-faithful mechanism for the wife's excuse; align both bands and the 4-9 moral |
| 6 | **PT086** 9+ | mechanical | fix the mis-assigned actor and the unearned "just like the fiend" |
| 7 | **PT082** 9+ | mechanical | reword the M1 prompt so it matches the 9+ text, not the 4-9 one |
| 8 | **PT017** | verify→fix | claimed 9+ invented motive; **not yet independently confirmed** |
| 9 | **PT023** | verify→fix | claimed unearned 9+ moral + elephant labelled `victim`; **not confirmed** |
| 10 | **PT025** | verify→fix | claimed garbled 9+ causal beat + overstated `C5` prior; **not confirmed** |
| 11 | **PT004** | verify→fix | claimed item keys "hungry" where the text says "curious"; **not confirmed** |
| 12 | **PT084** | verify→fix | claimed `C4` prior 3 overstated; **not confirmed** |

Items 1–7 were confirmed by me reading the raw text. Items 8–12 are the parallel readers'
claims, so the first job of those agents is to falsify them.

**On completion:** apply every surviving edit through one guarded, idempotent script
(asserts each `old` is present, `--dry-run` first), sync the band `.txt` files,
`panchatantra_adapted.json` and the band manifests, rebuild `story_tags.json` /
`story_items.json` if tags or items changed, then re-run the full check suite plus
`adapt.py --check` for both bands. Anything the verify stage rejected, or that I disagree
with on re-reading, gets recorded as **refuted** rather than quietly dropped.

---

### 2026-10-13 — content fixes, fan-out round 2

**Started from:** the 5 held defects + the residual judgement calls. Instruction: *"fix all
the pt issues, fan out subagents"*, and *"keep updating the log so nothing is lost"*.

**First: a temporary git repo, now removed.** `git init` + a `.gitignore`
(`source/fullbook/`, `source/rendered/`, `.playwright-mcp/`, `__pycache__/`) + baseline
commit `bba22f9`, 307 files tracked — created **only** so the fan-out below had an undo, and
deleted the same day at the user's request. It is not there now. Recorded here because the
entries below refer to it and to reverting files with it, and a later reader would otherwise
look for a repo that does not exist.

> **Doc path was wrong — fixed 2026-10-13.** Every command block in `WORKLOG.md` and
> `HANDOVER.md` used to say `cd /Users/omkarpujeri/Desktop/Projects/story`; the real
> directory is `.../Projects/panchatantra story`. Anyone pasting the documented commands
> got a no-such-directory. Both files now carry the correct path.

**Ground truth re-established by my own reading — not from the previous log's summary.**
Confirmed, with the evidence I actually printed:

| story | confirmed how |
|---|---|
| **PT010** | `grep -c bone corpus/stories/PT010-*.txt` → **0**. The 4-9 "fish-bone" death is invented. The source ending is the **golden-chain device** at `panchatantra_complete.txt:2760-2772`: jackal advises → crow-hen steals a king's gold chain → drops it in the snake's hole → king's men club the snake → *"Thereafter the crow and his wife lived in peace."* The 9+ band stops at *"The snake will take care of itself."* with a moral about a `downfall` never shown. **Both bands wrong, in different ways** |
| **PT017** | 9+ really does say *"the archer, thinking the swan was a threat, shot and killed him"* — but the swan is **asleep**, so the motive is incoherent. 4-9 has the omen (source-faithful). The claim holds |
| **PT059** | 4-9: *"make my husband live a hundred years by embracing another man."* 9+: *"the bad luck that threatened her husband would transfer to him."* Two different plots, confirmed by printing both files |
| **PT003** | Both bands end at *"planned to get rid of Lively"* then assert a moral about a loss never shown. The 9+ additionally ends on a **hand-off** (*"Remember the story of the monkey who extracted a wedge"*) — the partition bug, visible |
| **PT022** | `wc -w` → **157** against a 500–1500 target. Confirmed |
| **PT013 / PT047** | No 9+ file at all; failed attempts sit in `corpus/age/9+/_rejected/` |
| **PT090** | *"front matter"* 715 words vs PT002 *"Introduction"* 718 words — a near-exact duplicate. It is **absent from `story_tags.json` and `story_items.json`** (80 records each) but **present in the age manifests and `panchatantra_adapted.json`**. So "delete PT090" is a cascade, not an `rm` |
| **PT084** | The prose of both bands reads coherently. The open claim is about the **C4 tag**, not the text — so it is not a text edit at all |

**Fan-out round 2 — design, and why it differs from round 1.** Workflow `wf_f244e866`, 9
stories, draft → adversarial verify, ~18 agents. The rules encode every failure this project
has already had:

1. **The defect description is passed to each agent as a hypothesis to falsify**, not a fact.
   Returning `needs_change=false` with a reason is an accepted outcome (PT084 and PT060 are
   both expected to land there).
2. **Every `old` string is grep-verified verbatim before return** — the guard against
   PT003's hallucinated quote.
3. **Agents are told the chapter file is often truncated and the real ending lives in the
   *continuation* in `panchatantra_complete.txt`** — the exact mistake two earlier agents made.
4. **No agent writes a file.** They return edits as data; one guarded script applies them.
   Parallel writers to the same band file is how round 1 nearly clobbered PT031.
5. **The verifier defaults to REFUTED** and must check (a) `old` is present, (b) the source
   quote is real, (c) nothing is invented, (d) the band's readability targets hold,
   (e) the edit is the minimal one.

**Not in this fan-out, deliberately:** PT090's cascade delete, and the tag edits (PT084's C4,
PT004's already-applied set) — mechanical, and safer done by hand than by an agent.

#### The fan-out result: 11 edits confirmed, **0 refuted**

PT084 and PT060 both came back `needs_change=false` — correctly. PT084's prose is fine and its
only real issue is the **C4 tag**, and PT060 is a human curation call. The design's falsification
branch therefore worked; what did **not** fire is the adversarial check: eleven edits and not one
refutation is a warning sign, not a clean bill. I treated it as such and read every changed file
myself rather than trusting the verdicts.

**Applied, 8 files, 44 insertions / 20 deletions:**

| story | what changed |
|---|---|
| **PT010** both bands | the fabricated fish-bone death (4-9) **and** the unresolved "snake will take care of itself" (9+) both replaced with the source's **golden-chain device**. The heron-and-crab story is kept in both — it is genuine, and is the jackal's illustration, not the resolution |
| **PT003** both bands | each telling now runs to the frame's real ending: Victor's two mutual lies, the fight, Lively's death, Rusty's repentance (*"Lively was my second life. In killing him, I have only hurt myself."* — source line 6267). The 4-9 band also stopped calling *both* jackals plotters; the source makes Victor the sole schemer |
| **PT017** 9+ | the nonsense motive (*"the archer, thinking the swan was a threat"* — the swan is asleep) replaced with the source's omen: the owl's hoot disturbs the leader's spirit, so he has the sleeping swan shot |
| **PT059** both bands | both bands now carry the source's **single** mechanism: the goddess says the husband will die soon and the death passes to whoever embraces her — so the husband lives a hundred years. The 4-9 moral was aligned to the 9+ one |
| **PT022** 9+ | 157 words → **512**. A whole telling, not a trim |
| **PT013** 9+ | **new file, 1,467 words** — the complete weaver/Garuda story, resolving on the discus and Vishnu's own intervention |
| **PT047** 9+ | **new file, 695 words** — the complete crows-and-owls frame, resolving on the burning of the cave |

All eight pass `adapt.py --check` for their band. `readability.py` FK/wps confirmed per file.

#### Two more "the check passed without looking" bugs, found by reading the diff

**1. The applier silently rewrote line endings.** The first apply produced a diff where *every
line* was changed. Cause: 125 of the 147 corpus files are **CRLF**, and `Path.write_text()`
rewrites them as LF. The content edit was correct and the diff was unreadable — a write that
"succeeded" and was still wrong, which is this project's signature failure. Fixed in
`apply_content_fixes.py` (read bytes, detect the file's own newline, restore it on write); the
seven files were reverted with `git checkout` and re-applied. New files are written CRLF to match
the corpus. Second diff: **44 insertions, 20 deletions** — the real change, nothing else.

**2. `adapt.py --check` was reporting on a stale manifest.** After adding the two new 9+ files it
still said **81 stories** while 83 sat on disk, because `report()` rebuilds `manifest.json` *only
if the file is missing*. The two new files were never measured and "All adapted stories satisfy
target readability metrics!" was not true of them — it was true of the 81 it had already seen.
Fixed at the shared function (always rebuild; the directory is the source of truth and the
manifest is derived). It now reports **83**, then **82** after PT090 came out.

#### PT090 — the "duplicate" claim did not survive checking

HANDOVER says *"PT090 is a duplicate of PT002 and should be deleted"*. `corpus/story_tags.json`
already carried a prior note: *"Confirm and delete from the corpus rather than tag."* Checked:
the **source** texts overlap only **35%** — PT090 is the book's **front matter** (the
Vishnusharman dedication verse), PT002 is the Introduction. So they are not source duplicates;
the duplication is at the **adapted** level, where both retell the same three-blockhead-sons
frame. Confirming evidence: `data/curation.json` scored PT090's bands off the keyword `murder ×2`,
and the evidence example is *"61 the weaver's wife 62 how the crow-hen killed the black snake"* —
a **table of contents**. The heuristic was reading the contents page as a story.

**Decision (user, this session): remove the adapted side only.** Deleted the two tellings, dropped
PT090 from `panchatantra_adapted.json` (90 → 89), both `bands/band-*.json` (63→62, 84→83) and
`curation.json`; kept `corpus/stories/PT090-front-matter.txt` and its `panchatantra.json` record
so `check_corpus.py`'s text-coverage test stays valid. PT090 was never in the 80 tag records, so
nothing served changed.

#### The fix created one honest new failure

`build_story_tags.py --check` now fails: *"2 stories have adapted text but no authored tags:
PT013, PT047."* That is the corpus invariant working correctly — a story with a telling must have
tags and items, or the engine cannot select it. Both were quarantined in `_rejected/` before, so
they were never tagged. **A third fan-out is authoring those records now**; the alternative was to
leave them untagged and ship a corpus whose own validator fails, which is not a fixed state.

#### Fan-out round 3 — tagging the two new tellings

Two agents, one per story, told to read `STORY_TAGGING_SCHEMA.md`, both validators, and the
neighbouring records before writing anything. Both returned records **and** reported that they had
simulated the validators in memory rather than assuming. Merged via a script: `_draft` stripped
from both to match the 70/80 majority that omit it.

- **PT013** — 9+, `min_age 9 max_age 13`, moral *"The gods befriend the man who climbs the height
  of determination."* (courage). 4 measurement (C1/C2/C3/C6) + 5 discussion (M1–M5).
- **PT047** — 9+, `min_age 9 max_age 12`, moral *"Never trust an enemy, however friendly they may
  seem."* (prudence). 4 measurement + 5 discussion.

Both agents independently reached the same structural conclusion: for a 9+-only story, discussion
prompts are **9+ only**, because a 4-9 prompt is unreachable when there is no 4-9 telling — matching
the 21 existing 9+-only records. That is the documented exception to "give both bands", and both
found it by reading the neighbours rather than from the prompt.

`build_story_tags.py` already had a `_skipped` mechanism naming PT090 — so the PT090 removal above
is consistent with how the builder already treated it.

#### Final state, all checks green

```
engine.demo                        82 stories, 250 measurement, 495 discussion, 82/82 coverage
check_corpus.py                    PASS — 90 stories, 96,541 words
build_story_tags.py   --check      OK: 82 records
build_story_items.py  --check      OK: 250 measurement | 495 discussion (125 need an adult)
adapt.py --band 4-9   --check      All satisfied — median FK 3.17, 10.24 w/s
adapt.py --band 9+    --check      All satisfied — median FK 6.33, 15.36 w/s
```

**A note on how that was verified.** The first attempt at running that suite was a shell loop that
expanded each command as a single word, so nothing ran — and it printed `ALL CHECKS GREEN`
anyway. Caught because the output showed absent. It is the same species as everything else in this
entry: **a check that reports success without executing the thing it claims to check.** Rewritten
with the commands as arguments, and re-run.

**3. The PT090 removal reformatted its host files.** The first pass rewrote `corpus/bands/*.json`
and `data/curation.json` with `json.dumps(indent=2)`; the originals use **indent=1**, so deleting
one record diffed as **2,824 / 3,712 / 3,272 lines**. Reverted to baseline and re-applied at the
original indent — the diff is now the PT090 record and nothing else (24 / 24 / 34 lines). Third
instance of the same species in one session: *a rewrite that makes the real change unreadable.*
The lesson generalises past newlines — **before rewriting a generated file, match how it was
generated.**

#### The three residual content calls — resolved

These were left for a human. The user asked for them to be handled directly, so they were, with
the evidence recorded here so each one can be checked or reversed.

**1. PT084 `C4_vocabulary`: 3 → 2. Applied.** `C4` is word-meaning-in-context. The distribution
over 82 stories settled it: `C4=2` is the norm at 51 stories, and `C4=3` is the top tier shared by
only **four** — PT014, PT018, PT026, PT079. PT084 is *The Brahman's Dream*, a short dream-sequence
whose entire vocabulary demand is `barley-meal`, `famine`, `mares`, `inner court`, `dowry`; it was
sitting in the top tier beside four longer, denser stories. Now reads `{1: 27, 2: 51, 3: 4}`.

**2. PT060 9+ child-marriage line. Applied — this is a deliberate departure from Ryder.**
`corpus/age/9+/PT060-mouse-maid-made-mouse.txt` line 7 read:

> Yajnavalkya agreed, saying that **a girl should be married before she developed womanhood.**

and now reads:

> Yajnavalkya agreed, saying that **the time had come for her to be married.**

The plot is untouched — he still resolves to find her a husband, so the suitor search that follows
still has its motive — but the *justification* for marrying a child is gone. **This is the one edit
in the whole session that knowingly departs from the source**, and it is recorded as such because
the project's curation exists precisely to catch this content. Revert is one string if the call is
ever reversed.

> **PT003's 441 words — no change, and the question turned out to be malformed.** It was framed as
> "441 against a 500–1,500 target", but the target is not real. Measured across the band:
> **76 of 82 nine-plus stories (92%) are under 500 words, median 284.** The brief's own line 126
> already concedes the point — *"`--check` will therefore pass files that miss the targets on this
> page"* — while the table on line 121 still prints 500–1,500. So the enforced spec is the code's
> `70–1500`, the brief's floor is aspirational, and PT003 at 441 is **above median**. Nothing to fix
> in the story.
>
> **But this is bigger than PT003 and is now an open item in its own right:** if the brief's
> 500-word floor for 9+ *is* the product intent, then the 9+ corpus is systematically short and that
> is a large re-adaptation job, not a tidy-up. If it is not, the brief's table should stop saying
> so. That is a spec decision, and it is not mine to make silently.

#### The census — run 2026-10-13, and the answer is not the one we expected

**Full findings: `data/census_2026-10-13_findings.md`.** Raw output: `data/census_2026-10-13.json`.

28 read-only agents over **82 stories / 142 tellings**. Every claim was then re-checked by me
against the raw text before being recorded — necessary, because two agents in this run cited
**table-of-contents line numbers** as source evidence, and this project has previously had agents
cite the wrong file twice and hallucinate a quote once.

```
142 tellings audited -> 119 resolve, 23 flagged -> 17 stories, 1 of them a false positive
```

**~16 stories carry a real defect — about 15% of the corpus.** The estimate going in was "a
handful". It is a systemic property of how the corpus was built, not a tail.

**The mechanism is confirmed, and it is the partition bug.** 16 of the 17 flagged stories have a
source chapter ending on a hand-off (`"How was that?" asked X. And Y told the story of`). In the
Panchatantra a chapter holds the fable's **setup**; the resolution comes after the nested tale. An
adapter given only the chapter either **invented** an ending or **stopped at the hand-off**.

Verified by reading the source myself (the full table is in the findings file):

- **INVENTED** — PT004 9+, PT019 9+, PT020 4-9, PT048 4-9, PT076 9+, **PT085 9+** (the telling
  eats the king; source line 13718 has him *"hasten home, grief-stricken"* and survive),
  PT089 both bands (the source has **no treasure** at all).
- **TRUNCATED** — PT020 9+, PT028 4-9, PT031 9+, PT040 both, PT048 9+, PT049 9+, PT062 4-9,
  PT063 9+, PT071 9+.
- **FALSE POSITIVE** — **PT039** both bands. Its source continuation at 7321+ is a *new nested
  tale*, not the resolution; both tellings do resolve. The agent read "the source keeps going" as
  "the telling stopped short". Recorded here so nobody re-fixes it later.
- **PT043 and PT079** were flagged with specific claims I only partially verified. Probably real;
  read before fixing.

**Two things this settles.** First, **PT003 and PT010 came back clean** — the two found by hand
and fixed today. A census that failed to clear them would have been the one making things up.
Second, **reading was the detector, again.** Four automated detectors have failed on this project;
this pass worked because readers read and a human checked every claim.

#### Still open after this session

- ~~**The 16 census defects above**~~ — **all fixed later the same day**, 24 edits across 22 files.
  The "copy-up" cases (PT049, PT062, PT063) and the "author" cases (PT020, PT028, PT031, PT040,
  PT048, PT071) were drafted, adversarially verified, applied and read. Three agents found *more*
  than the census listed. See §"The census fixes — applied 2026-10-13".
- ~~The brief-vs-code 9+ word-count question~~ — **CLOSED 2026-10-13, not a defect** (see the closure note above: complexity separates the bands, not length).
- `corpus/age/9+/_rejected/` still holds 6 files: the superseded PT013/PT047 attempts, PT022,
  PT029, PT032, PT059. Their live replacements all exist (PT029/PT032 were never broken) — the
  rejected ones are dead weight, but they are the audit trail for *why*, so leave them.
- **Formatting note:** `data/story_tags_authored.json` and `data/story_items_authored.json` are
  `indent=2`; `corpus/bands/*.json` and `data/curation.json` are `indent=1`. Match whichever file
  you are editing or the diff becomes unreadable — see the §3 note above.

#### The census fixes — applied 2026-10-13

Workflow `wf_65c7a531`: 16 stories, draft -> adversarial verify, 32 agents, 2.22M subagent tokens.
Raw output `data/review_2026-10-13_censusfix_workflow.json`.

**24 edits confirmed, 1 refuted, 22 files.** Every edit was then read against the before-state via
`data/apply_content_fixes_backup.json` (the only undo — there is no git) before anything was
accepted. Same rules as before: agents returned edits as DATA, never wrote a file, and the
verifier had to grep the `old` string verbatim, check the cited source line really says what is
claimed, and re-run `readability.py` on the patched text.

| story | band(s) | what changed |
|---|---|---|
| PT004 | 9+ | the invented king/Victor-errand/**counselor promotion** block deleted; resolves on the source's actual fate — the log snaps shut on the monkey — plus the source's own moral |
| PT019 | 9+ | invented "they became good friends" replaced with the source ending: the carpenter stays up the tree and will not come down |
| PT020 | 4-9 + 9+ | both had only the *setup*. Now the theft, the vow, the birds, Garuda, and the restoration |
| PT028 | 4-9 + 9+ | 9+ was found broken too, beyond the census list. Now the serpent's true form and the burnt snakeskin |
| PT031 | 9+ | the mimosa-tree ordeal, the voice from the hole, the burning |
| PT040 | 4-9 + 9+ | the sesame bargain — the wife hulling grain, the trade, the *"Mother Shandilee…"* verse |
| PT043 | 4-9 + 9+ | **claim was unverified going in; confirmed.** 4-9 stopped at the hand-off, 9+ invented a grant. Now the Penny-Hide / Penny-Fling test |
| PT048 | 4-9 + 9+ | 4-9 said *"The owl was very happy"* — the **inverse**. Now the crow argues the birds out of the anointing, the owl is left un-crowned and furious: the origin of the crow-owl feud |
| PT049 | 9+ | *"I shall never return here." And with these words he went to his own place* |
| PT062 | 4-9 | the woodpile at the gate and the burning of the cave |
| PT063 | 9+ | the frogs eaten — *"not even one tiny frog was left"* |
| PT071 | 9+ | the invented nested monkey story replaced with the source's silence verse (*complete.txt* 12459/12465) |
| PT076 | 9+ | the garbled invented ending **deleted outright** (256 → 173 words); ends on the source's moral |
| PT079 | 9+ | the wheel-bearer's reply and the farewell |
| PT085 | 9+ | **the king now survives and goes home**, per source 13718. The telling had eaten him |
| PT089 | 4-9 + 9+ | **both bands were wholly fabricated** — a "Numskull and Red-Face" fruit story and a "treasure hunt". Rewritten as the real monkey-and-crocodile fable |

**One refutation, and it was correct:** PT071 4-9 — the census had that band as RESOLVES and the
findings scope was 9+ only. The verifier refused an out-of-scope edit. That is the adversarial
pass working.

**Three agents found MORE than the census had flagged** (PT028 9+, PT020 9+, and PT062's sibling).
The census was a floor, not a ceiling.

**All checks green after:** 4-9 total words 13,516 → 14,244; 9+ 25,568 → 26,953; `engine.demo` 82
stories / 250 items / 495 prompts; `check_corpus.py` PASS; both builders OK; `adapt.py --check`
clean for both bands with the medians essentially unmoved (4-9 FK 3.17 → 3.09, 9+ 6.33 → 6.22).

#### Two things the fixes surfaced that nobody had looked at

1. **PT062 9+ is untouched by this work and ends on a verse** — *"Cause your friends no bitter
   woes; do not fraternize with foes…"* — and narrates the owls as *"suffering the torments of
   Pot-baking Hell."* The brief says **drop all verse**, and that is strong imagery for a 9+ band
   that is served to children. This is pre-existing, it is not a census defect (the telling does
   resolve), and no check looks for either thing. **Worth a decision.**
2. **PT089 is curated BOTH bands and the corrected 4-9 telling now contains *"Bring me his heart.
   I want to eat it."*** The old 4-9 telling was so wrong that it never raised this. The curation
   passed the *source*, which contains the same plot; the telling is faithful. **A band-eligibility
   question for a human, not a bug.**

#### The two follow-up judgement calls — closed 2026-10-13

Both were resolved by editing, on the user's instruction.

**PT062 9+** had two problems in one telling, neither of them a census defect (it resolved fine):
the body narrated the owls *"suffering the torments of Pot-baking Hell"*, and the Moral line was a
copied source verse (*complete.txt* 11252-11254). Hell line replaced with *"The owls, trapped
inside, could not find their way out of the flames."*; moral replaced with prose.

**PT077** turned out to be **both bands**, not just 9+ — the 4-9 moral was the same source verse
truncated (*"Deeds ill-known, ill-recognized, ill-accomplished, ill-advised."* ← 12852). Both
replaced with prose.

**PT089 4-9** carried *"Bring me his heart. I want to eat it."* The plot is untouched — the wife
still covets the heart, which is the fable and what makes the monkey's *"I left my heart at home"*
trick work — and only the eating clause is gone.

**These replacement morals are authored prose, not source text.** That is the correct move under
the brief's *"drop all verse"*, but it means sentences were written that are not in Ryder. Recorded
here so nobody later diffs the corpus against the source and concludes they were invented errors.

**A note on the scan that found this.** A quick regex over the 9+ band flagged **11** tellings as
ending on a "verse-style moral". Reading them showed most were ordinary prose morals that happened
to contain commas. Only PT062 and PT077 were real. That is the fifth time in this project that a
mechanical detector over-fired — the flags were useful as a shortlist and useless as an answer.
Also checked: the ` . . . . ` verse-elision marker the brief bans appears in **0** files.

#### Certification pass — run 2026-10-13, and it did NOT pass

Full findings: `data/certification_2026-10-13_findings.md`. Raw: `data/certification_2026-10-13.json`.

The 23 tellings census 1 flagged were all verified by me. The **119 it cleared were not.** This pass
re-audited those, adversarially, asking the opposite question. 30 agents, batches of 4.

**Result: 45 refutations across 42 story-band pairs.** The corpus **could not be certified clean.**

**This is a signal, not noise.** The agents were told to *default to flagging when uncertain*, which
biases toward false positives — so I spot-verified the three sharpest claims first, and **all three
held**:

- **PT002 9+** puts *"It will take twelve years"* in **Keen's** mouth as his own clever idea. The
  source gives that to the advisors collectively (line 40) and gives Keen the **opposite** proposal
  (line 42) — rejecting the long timeline is his whole role. The 4-9 band has it right.
- **PT005 4-9** — *"the drum was quiet when the wind blew."* Source: it made the sound *when* the
  grass tips swaying in the wind struck it. Inverted.
- **PT006 9+** — *"Bull was overjoyed and apologized."* Source line 156: Bull, the wrongdoer, says
  *"Friend merchant, I forgive you."* Reversed.

**Census 1 was not wrong — it was narrow.** It asked "does the telling resolve?" and answered that
correctly. It never asked "is the telling's *plot* right?" A telling can resolve perfectly and still
invert who did what to whom. That is why 42 more turned up on the second question.

**Status of the 42: unfixed, and only 3 of them verified by me.** The other 39 are agent claims
carrying a flag-biased prompt. Expect some false positives among them. Fixing them needs a third
fan-out with draft + adversarial verify, the same shape as the census fixes.

> **Resolved 2026-10-13** — all 42 fixed and re-certified; see the entry immediately below.

---

### 2026-10-13 (later) — the 42 certification defects

**IN PROGRESS.** Third fan-out, workflow `wf_55dcf5cd-248` (watch with `/workflows`): **45 draft
agents**, one per story-band file — the 42 flagged pairs plus the 3 tellings neither pass ever read
(`PT028 9+`, `PT029 9+`, `PT030 9+`; census 1 reported only their 4-9 band, so they fell through the
coverage gap). Each draft is followed by an **adversarial verifier** that must refute by default.

Same rules as the census fixes, deliberately:

- agents return edits as **DATA** (`old`→`new`), never write a corpus file;
- the verifier must confirm the `old` is an exact substring, read the cited source line itself, and
  re-run `readability.py` on the patched text;
- a guarded script, `scripts/apply_triple_fixes.py`, applies survivors with a CRLF-preserving
  backup — **no git** (user declined commits 2026-10-13).

Work list `data/triplefix_items.json` · raw result `data/review_2026-10-13_certfix_raw.json` ·
apply input `data/review_2026-10-13_certfix_workflow.json` · undo
`data/apply_triple_fixes_backup.json`.

**Result — 101 agents, 5.6M subagent tokens, 13.6 min.**

```
45 draft agents -> 56 edits drafted CONFIRMED
   -> 48 APPLIED (verified faithful + readability ok)
   ->  7 refuted by the adversarial verifier (NOT applied)
   ->  1 verified but readability-flagged (NOT applied — human read)
   2 false positives (agent judged the telling faithful): PT050 4-9 and 9+
```

Applied **48 edits across 48 files**: `python3 scripts/apply_triple_fixes.py` (backup written).
All green after: `check_corpus.py` PASS · `adapt.py --check` clean for 4-9 and 9+ · `engine.demo`
untouched. **Every edit was read against its before-state in the backup** (the diffs are in the
session, not summarised away).

The verifier earned its place — it refuted 7, each for a real reason: PT006 9+ (edit deleted an
accusation the next sentence depends on), PT035 9+ (premise wrong), PT055 9+ (×2, dove gender
already contradicts the file), PT065 9+ (left the file incoherent), PT068 9+ (invented moral),
PT030 9+ (moral edit incoherent against unchanged line 9 — but PT030's *other* claim did apply).

**A bug in my own tooling, caught before it wrote wrong.** The first `--dry-run` reported
`PT083:4-9` as **"already applied"**. It was not: PT083's edit is a *deletion* (`new` "Slow died."
is a substring of `old`), and the guard — copied from `apply_content_fixes.py`, where edits are
*append*-style — tested `new in body` first. A skip that looked like success, on an un-applied
edit. Fixed by testing `old` first, with the reasoning recorded in the script. **This is the fifth
"check that lies" this corpus has produced** (HANDOVER §11).

**Two audit-only items scored.** PT030 9+ had a real invented 'the other monkeys learned a lesson'
ending — now the source's own "an unfit mind cannot be taught". PT028 9+ and PT029 9+ audited:
PT029 9+ carried 2 edits (god/Yama/Death reassignment); PT028 was faithful.

**Left for a human read (deliberately not auto-applied):**
- **PT055 9+** — the surviving edit adds *"The dove kindled a fire for him."* Verifier: source-
  faithful, but band readability flagged, and the file already contradicts itself on the dove's
  gender (lines 12-13 "devoted wife" vs source's male dove). Needs one human pass.
- **PT073 4-9 / 9+, PT037 9+, PT068 4-9** — these *append a resolution* to a telling that stopped
  on the chapter hand-off. Verified, but they are authored endings: read before shipping.
- **PT052 9+, PT084 4-9** — deletions of an invented closing beat; confirm the cut is the source's.

#### Re-certification, and the 6 defects it caught

41 edited files re-read against the source (workflow `wf_c9a00f2f-8ca`, 47 agents). **35 faithful, 6
real defects** — every one confirmed by a second reader. Two were *caused by the first-pass edits*:

- **PT007 9+** — the edit that fixed the distrust actor ("Godly still did not trust him") left the
  next sentence's `He` pointing at Godly, so it read *"Godly thought of killing Godly."* A pronoun
  antecedent the first-pass verifier did not catch. **This is why draft+verify is not enough and the
  re-certification exists.**
- **PT065 9+** — the heart-reveal sentence was fixed but its companion clause *"telling him about his
  wife's demands"* survived, half-fixing the scene.

Four were adjacent defects the read surfaced: **PT015 9+** (moral ran opposite the source's *"With no
stranger share your house"*), **PT056 9+** (spared party was the guest, not the thief), **PT062 9+**
(the rejoicing was at *Red-Eye's*, not Curd-Face's, departure — the telling even contradicted itself
one sentence later), **PT068 9+** (appended moral inverted the source's *"No elephants are slain in
your family"*).

**All 6 fixed and re-certified** (workflows `wf_6d11c736-cff` draft+verify → `wf_c971a75d-d54`
certify). 6 edits applied via `scripts/apply_triple_fixes.py --workflow
data/review_2026-10-13_recertfix_workflow.json` (undo `data/apply_recertfix_backup.json`); **6/6
FAITHFUL**. `check_corpus.py` PASS and both bands clean again after.

**Final state of this pass:** the 42 certification defects are fixed (48 edits), the 3 unaudited
tellings were audited (PT028 faithful; PT029/PT030 fixed), the 6 follow-ups from re-certification are
fixed, and **every file this session touched has been re-read against the source and certified
faithful**. 54 edits total across 47 files, 4 fan-outs, ~9.3M subagent tokens.

**Not claimed:** that the whole 142-telling corpus is provably clean. Each successive pass has found
more (census: 23; certification: 42; this pass's re-certification: 6) — the honest bar is a full
third-pass certification of all 142, which has *not* been run. What *is* true: no file we changed is
unverified, and the two sharpest spot-checks held.

#### Follow-on — PT016 "The Blue Jackal": a stale curation verdict (2026-10-13)

Spotted while prepping the handover: `story_tags.json` already carried PT016 as `age_map.bands =
["4-9","9+"]` with the rationale *"CURATION OVERRULE: … NINE_PLUS on the frame's misogynist verse, not
the fable (HANDOVER §5)"*, and a 4-9 telling existed — but `data/curation.json` still said
`NINE_PLUS`, so `band-4-9.json` excluded it. **The docs and the tags were right; curation was the
stale artifact.** Fixed: PT016 `verdict → BOTH`, `bands → ["4-9","9+"]`, screen reason kept as the
record. Derived files updated surgically.

> **`scripts/export_json.py` had two side effects not in its contract — both FIXED 2026-10-13.**
> They were caught by diffing a re-run against a pre-edit copy and reverted, then fixed:
>
> 1. a story with **no `curation` entry** (PT090) fell back into **both** band files, re-adding it.
>    **Fix:** no-curation stories now get `bands: []` — excluded, never defaulted to both.
> 2. `META.band_targets` were built from **`adapt.BANDS`** (the *enforced floor*), so a re-run
>    silently rewrote the shipped spec numbers (FK 4.0→4.8, syllables 1.38→1.42, word floor 200→70) —
>    i.e. it *decided* the unresolved §7 question. **Fix:** the shipped numbers are pinned in a
>    `BAND_TARGETS` constant with a comment naming §7; `adapt.BANDS` is no longer imported here.
>
> **Re-running is now idempotent — proven by running it twice and diffing (run 2 byte-identical to
> run 1).** PT090 now carries `bands: []` in `panchatantra.json` too, so the hand-removal is no longer
> fragile. When §7 is decided, align `BAND_TARGETS`, `ADAPTATION_BRIEF.md` §2 and `adapt.BANDS` together.

**Now consistent:** `band-4-9` = 63 = the 63 four-to-nine tellings; curation BOTH 63 / NINE_PLUS 20 /
EXCLUDE 6. **Left open:** `band-9+` is 83 against 82 nine-plus tellings — the extra is **PT001
"Translator's Introduction"** (front matter, book 0, no telling, no tags), the same class as PT090
(which was removed from curation). Recommend mirroring PT090; **not changed — an editorial call,
flagged to the user.**

