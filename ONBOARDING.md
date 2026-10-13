# Onboarding — for whoever builds the app

Short. Deeper detail lives in `HANDOVER.md`.

## What this is
An AI tutoring app that serves Panchatantra stories to children (ages 4-9 and 9+) and
adapts to each child's ability. **The corpus and the selection engine are done. The app
shell does not exist yet — that is the job.**

## State of play
| | |
|---|---|
| Corpus | ✅ 145 age-adapted tellings (63 × 4-9, 82 × 9+), readability-validated, source-certified |
| Tags + questions | ✅ 82 story records; 250 auto-scored MCQ + 495 discussion prompts |
| Engine | ✅ v0 prototype — story selection + mastery update (`engine/`) |
| **App shell** | ❌ **yours** — persistence, serving, telemetry, UI |
| Video | ❌ Member 3's half (consumes the `video_brief` block) |

## Read first
1. `HANDOVER.md` — the map of the whole project.
2. `STORY_TAGGING_SCHEMA.md` — the data contract.
3. `PROJECT_CONTEXT.md` §2–3, §10 — vision, features, stack.
4. `uxpilot-export-09-17-26.pdf` — the UI design.

## The integration surface
The engine is a **pure Python module**. The app owns persistence, serving and telemetry —
`engine/__init__.py` says so explicitly. Don't rewrite the selection logic.

```python
from engine import ChildState, load_corpus, select_next, apply_story, all_skills

stories, items = load_corpus()
state  = ChildState.new(child_id, age, all_skills(stories))
lesson = select_next(state, stories, items, co_read=False)
# serve  lesson["story"]  +  lesson["measurement"]   (MCQ, auto-scored)
# serve  lesson["discussion"]                        (open, adult-facilitated)
apply_story(state, lesson["story"], items_by_id, {"PT005-C2-m1": True})
```

## Build order
1. **Shell** — React + FastAPI + PostgreSQL. Persist `ChildState`; serve one lesson.
2. **Telemetry** — time-on-task, drop-off, replays. Feeds the attention ramp and is the
   **only** way `calibration` is ever written (it is empty by design).
3. **Co-read mode** — unlocks the `requires_adult` discussion prompts; the only path to M4/M5.
4. **Dashboard** — trends + uncertainty, and **never** the word "improvement"
   (`PRODUCT_RESEARCH.md` is explicit about what is honest to claim).
5. **Video** (Member 3) — consume the `video_brief` block in each tag record.

## Don't
- Don't re-adapt the corpus — it is adapted, validated and certified.
- Don't re-run `scripts/export_json.py` — the data is settled.

## Know this — it will surprise you otherwise
- **Moral reasoning is deliberately never scored.** It lives in the discussion bank and is
  shown to the parent as raw text; only comprehension (MCQ) is measured. See schema §3.
- Exploration is weak, cold-start is a binary, and `calibration` is empty — all three are
  **telemetry-dependent, not bugs**. Step 2 is where they get fixed.
- Nothing here needs a trained model. The app calls pre-trained LLMs/embeddings over API;
  the repo is the data + the selection algorithm.
