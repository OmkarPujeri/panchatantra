# Story Tagging Schema

The structured parameter set that the **adaptive engine** selects on and the **age
mapper** grades by. This is the missing layer identified in `HANDOVER.md` §10: the
stories carry morals in prose, but nothing structured.

Read `PRODUCT_RESEARCH.md` §3 and §5 first — two decisions here follow directly from it:

1. **Attention is a story *demand* parameter, not a mastered skill.** Attention training
   does not work (research §2), so we do not pretend to "teach" it. We model how much
   attention a story demands and let the engine ramp it up gradually.
2. **Authored tags are *priors*; the engine calibrates real difficulty from response
   data.** Never treat a hand-assigned 1–3 as measured.

Output artifact: `corpus/story_tags.json` — one record per story, extends the existing
record rather than duplicating it.

---

## 1. Skill taxonomy

Two constructs are *mastered* (tagged, tracked, adapted on). The third is *demanded*.

### M — Moral reasoning (the dialogic layer)

| id | skill | observable question form |
|---|---|---|
| `M1_perspective_taking` | what a character thinks / feels / knows | "What did Fierce-Howl think the animals would do?" |
| `M2_intention_vs_outcome` | did they *mean* harm, or was it accident? | "Was the jackal lying on purpose, or did he just fall in?" |
| `M3_consequence_reasoning` | if→then on actions | "What would have happened if the animals had checked first?" |
| `M4_justification_quality` | *why* something is right/wrong (reasoning depth) | "Why was it wrong to trick them?" |
| `M5_moral_conflict` | competing goods in tension — **9+ only** | "What should X do when two things both matter?" |

`M4` is the closest thing to the outcome the literature actually moved (justification
frequency, RR=1.67) — **and it is the one that requires an adult.** Score it from the
co-read mode, not solo play.

### C — Cognitive / comprehension (the solo-testable layer)

| id | skill | observable question form |
|---|---|---|
| `C1_sequence` | order of events | "What happened first?" |
| `C2_cause_effect` | why an event happened | "Why did the dogs run away?" |
| `C3_character_motive` | infer a motive from behaviour | "Why did the animals bow to him?" |
| `C4_vocabulary` | word meaning in context | "'Dyer' means —" |
| `C5_inference` | read between the lines / predict | "What will happen next?" |
| `C6_theme` | main idea / moral extraction | "What is this story really about?" |

Comprehension (`C*`) is where in-app assessment is honest and well-validated. This is
the backbone of the solo experience.

### A — Attention (demand parameter, **not** a skill)

Not tagged per-skill. Each story carries an **attention load** that the engine increases
as the child's session length and completion rate grow:

```
attention_load: { duration_sec, pace: slow|medium|fast, scene_density, dialogue_lines }
```

Telemetry (time-on-task, drop-off point, replays) is recorded against it. It is reported
as **engagement**, never as "attention improved".

---

## 2. Record schema

```jsonc
{
  "story_id": "PT016",
  "title": "The Blue Jackal",
  "source_file": "PT016-the-blue-jackal.txt",

  // ---- age mapping (drives which band(s) this story may be served in) ----
  "age_map": {
    "bands": ["9+"],          // from curation.verdict; overrule with a note if you disagree
    "min_age": 6,             // sub-band precision — see §5
    "max_age": 10,
    "rationale": "deception + a character is torn apart; fine 9+, too harsh 4-6"
  },

  // ---- readability (measured from the ADAPTED text, not the source) ----
  "readability": { "fk_grade": 3.1, "words_per_sentence": 10.1, "words": 178 },

  // ---- content parameters ----
  "moral": {
    "text": "A clever trick can fool everyone for a while, but not forever.",
    "domain": "prudence"             // prudence|honesty|loyalty|greed|friendship|courage|...
  },
  "themes": ["deception", "identity", "consequence"],
  "characters": [
    { "name": "Fierce-Howl", "species": "jackal", "role": "trickster" }
  ],

  // ---- skill priors: how much this story exercises each skill, 0-3 ----
  // 0 = absent, 1 = incidental, 2 = present, 3 = central/teachable
  "skills": {
    "M1_perspective_taking": 2,
    "M2_intention_vs_outcome": 1,
    "M3_consequence_reasoning": 2,
    "M4_justification_quality": 2,
    "M5_moral_conflict": 0,
    "C1_sequence": 2,
    "C2_cause_effect": 3,
    "C3_character_motive": 3,
    "C4_vocabulary": 1,
    "C5_inference": 2,
    "C6_theme": 2
  },

  // ---- engine state: EMPTY on authoring, filled by the engine over time ----
  "calibration": {
    "M1_perspective_taking": { "difficulty_b": null, "n_observations": 0 },
    "C2_cause_effect":       { "difficulty_b": null, "n_observations": 0 }
    // one entry per skill with prior > 0
  },

  // ---- attention demand (drives pacing ramp, not mastery) ----
  "attention_load": {
    "duration_sec": 180, "pace": "medium", "scene_density": 2, "dialogue_lines": 12
  },

  // ---- brief handed to the video pipeline (NOT the engine's concern) ----
  "video_brief": {
    "scenes": 8, "visual_complexity": 2, "tone": "warm",
    "characters_to_design": ["Fierce-Howl"], "key_beat": "the dye vat"
  }
}
```

### Field rules

- **Authoring fills everything except `calibration`.** That block is engine-written.
- `age_map.bands` copies `curation.verdict` unless overruled — an overrule **must** carry
  a `rationale` (this is the PT016 lesson from `HANDOVER.md` §5).
- `readability` is measured from the **adapted** text, per band. A story served in two
  bands has two readability profiles — store per-band if it differs.
- `skills` priors are **ordinal, not cardinal**. `3` does not mean "three units"; it
  means "central". The engine never sums them.

---

## 3. The two question banks — `corpus/story_items.json`

The questions serve **two purposes that pull in opposite directions**, so they are two
collections with **opposite band rules**. One flat list with a `band` field cannot do
both — that was the ambiguity this split removes.

| | `measurement[]` | `discussion[]` |
|---|---|---|
| Purpose | track a child over time, compare children | develop moral reasoning |
| Format | mcq, auto-scored | open, adult-facilitated, **never scored** |
| Skills | `C1`–`C6` | `M1`–`M5` |
| **Band rule** | **band-invariant** — identical item in every band | **band-specific** — a variant per band |
| Difficulty | per-item `difficulty_prior` → calibrated `difficulty_b` | n/a |

**Why measurement must be band-invariant:** comparability *is* the measurement. If a
5-year-old and an 11-year-old answer different questions, their scores aren't
comparable and one child can't be tracked as they move from 4-9 into 9+.

**Difficulty is never a band exclusion.** A hard item stays available to a young child;
getting it wrong is *signal*, not breakage. `suitable_from_age` is a **selection hint**,
not a filter. Comparability across different item subsets comes from the calibrated
difficulty scale in `story_tags.json` → `calibration`, not from forcing identical items.

**Why discussion must be band-specific:** nothing is measured there, so divergence in
depth is free — and necessary. A 4-9 prompt asks about feelings and choices; a 9+ prompt
asks for justification or presents the dilemma.

```jsonc
// measurement[] — no band field
{
  "item_id": "PT016-C2-m1",
  "story_id": "PT016",
  "skill": "C2_cause_effect",
  "prompt": "Why did the animals run away from Fierce-Howl?",
  "options": ["He was bigger than them",
              "He was blue and they did not know what he was",   // correct
              "He shouted at them"],
  "correct": 1,
  "difficulty_prior": 1,          // 0-3, calibrated later
  "suitable_from_age": 6,         // SELECTION HINT, not a filter
  "scored": true
}

// discussion[] — one per band per skill
{
  "prompt_id": "PT016-M2-9p-d2",
  "story_id": "PT016",
  "skill": "M2_intention_vs_outcome",
  "band": "9+",
  "prompt": "Fierce-Howl said Indra chose him. Was he lying on purpose, or did the animals just believe him?",
  "requires_adult": false,
  "scored": false
}
```

### Scoring policy (from research §2)

- **Auto-score `measurement`.** These are the valid, low-noise signal.
- **Never auto-score `discussion`.** LLMs inferring deep psychological states from brief
  text show systematic bias. Collect responses, show them to the **parent** as raw text,
  never convert into a "morality score".
- `requires_adult` is **derived, not authored**: any `M4`/`M5` prompt needs the co-read
  mode, because the evidence says adult-facilitated discussion is the active ingredient.
  A solo "morality question" cannot be shipped by accident.
- `M5` is the one prompt with **no younger variant** — it is 9+ by definition.

**Honest dashboard consequence:** reliable numbers come from *comprehension*
(`measurement`). Moral reasoning appears as *discussion* — visible to the parent, not
scored.

---

## 4. How the engine consumes it

```
child state: per-skill mastery (BKT or Elo) + engagement telemetry + attention capacity

select next story:
  1. filter  → age_map.bands contains child's band; content OK for child's age
  2. score   → prefer stories whose skills show the largest mastery gap
               (prior > 0 for a skill the child is weak on)
  3. pace    → attention_load within child's current capacity (+ small ramp)
  4. novelty → avoid characters_themes seen recently; prefer variety
  5. pick argmax, serve

after each story:
  - score items → update per-skill mastery (BKT posterior / Elo rating)
  - log telemetry → update attention capacity (ramp duration slowly)
  - never write to calibration from a single response — need n_observations > few
```

**Cold start:** with no calibration, difficulty_b is null → fall back to
`skills` priors and `readability` band midpoint. Elo-style is simpler to cold-start than
BKT; either is fine, Elo first is the lazy path.

**Forgetting:** BKT normally ignores decay. At multi-week gaps (a child's usage pattern),
add a decay term or the mastery estimate drifts stale. Flagged, not solved.

---

## 5. Age mapping — split the 4-9 band

**4-9 is a five-year span. A 4-year-old and a 9-year-old are not the same reader,
listener, or reasoner.** The research instruments themselves split at ~7 (K-CPT 2 stops
at 7; DCCS correlations change at 8).

Recommendation: keep `4-9` / `9+` as the *storage* bands (the corpus is already built for
them), but add **sub-band precision** in `age_map`:

| sub-band | serves | M-depth | C-depth |
|---|---|---|---|
| `4-6` | read-aloud, co-view only | M1–M3 | C1–C2 |
| `7-9` | early solo | M1–M4 | C1–C5 |
| `10+` | solo, dilemma-capable | M1–M5 | C1–C6 |

The engine filters on `min_age`/`max_age`, so sub-band precision costs nothing at
runtime and buys a much better fit.

---

## 6. Authoring workflow

1. Load `corpus/panchatantra_adapted.json` + `corpus/curation.json`.
2. For each story, fill the block above. Mechanical fields (`readability`, `moral.text`
   seed, `characters`) can be auto-drafted; `skills` priors, `themes`, and `age_map`
   judgment should be **human-reviewed**.
3. Auto-draft with an LLM where possible, but treat `skills` priors as **proposals** —
   the same caveat the corpus README already applies to curation.
4. Validate: every story has 3 measurement items (a couple carry 4); every item's
   `skill` has prior > 0; no `M5` or `requires_adult` item outside the `10+`/co-read path.

**Start with the 10 pilot stories** (same advice as `ADAPTATION_BRIEF.md` §6). Tag 10,
build the engine against them, correct the schema, *then* scale.

> **Done — 2026-10-13.** Scaled to **82** tagged stories (the "145" here was always band-files,
> not stories: 90 source records, 82 with adapted text), carrying 250 measurement items and 495
> discussion prompts at 100% coverage. Both builders validate.

---

## 7. Worked example — PT016 in two bands

Same story, two records (or one record with per-band `readability` + a band-split
`skills` block):

| field | `4-9` / sub-band `7-9` | `9+` / sub-band `10+` |
|---|---|---|
| `age_map.bands` | `["9+"]` → **overruled to `7-9`**, rationale: no blood shown in adapted text; the dye-vat trick is classic children's material | `["9+"]` |
| `skills.M2_intention_vs_outcome` | 1 | 2 |
| `skills.M5_moral_conflict` | 0 | 1 |
| `skills.C2_cause_effect` | 2 | 3 |
| `requires_adult` items | M4 only | M4, M5 |

The overrule on `4-9` is exactly the kind of call `HANDOVER.md` §5 says the automated
screen gets wrong — the Blue Jackal was excluded on its *frame's* misogynist verse, not
the fable.
