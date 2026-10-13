"""Story selection — schema §4, steps 1-5, in order.

    1. filter  -> age_map covers the child's real age
    2. score   -> largest mastery gap among skills the story actually exercises
    3. pace    -> attention_load within capacity * RAMP
    4. novelty -> penalise themes/characters seen in the last few stories
    5. argmax, serve
"""

from __future__ import annotations

import json
from pathlib import Path

from .state import RAMP, TARGET
from .update import item_rating

CORPUS = Path(__file__).resolve().parent.parent / "corpus"

NOVELTY_PENALTY = 50.0   # rating points per overlapping theme/character
NOVELTY_WINDOW = 3       # stories a child should not see again this soon

# Discussion depth by sub-band (schema §5). M4/M5 additionally need co-read.
MAX_M = {"4-6": 3, "7-9": 4, "10+": 5}


def load_corpus(corpus_dir=None):
    """Returns (stories, items). Pass a dir to point at a different corpus."""
    root = Path(corpus_dir) if corpus_dir else CORPUS
    stories = json.loads((root / "story_tags.json").read_text())["stories"]
    items = json.loads((root / "story_items.json").read_text())
    return stories, items


def all_skills(stories) -> list[str]:
    """Taxonomy straight from the corpus, so it can't drift from the tags."""
    return sorted({s for story in stories for s in story["skills"]})


def select_next(state, stories, items, co_read: bool = False) -> dict:
    """Pick the next story and the questions to serve with it."""
    eligible = [s for s in stories
                if s["age_map"]["min_age"] <= state.age <= s["age_map"]["max_age"]]
    if not eligible:
        raise LookupError(
            f"no story serves age {state.age} — pilot corpus covers "
            f"{min(s['age_map']['min_age'] for s in stories)}-"
            f"{max(s['age_map']['max_age'] for s in stories)}"
        )

    limit = state.attention_capacity_sec * RAMP
    paced = [s for s in eligible if s["attention_load"]["duration_sec"] <= limit]
    if not paced:
        # Nothing is under capacity yet; serve the shortest thing we have.
        paced = [min(eligible, key=lambda s: s["attention_load"]["duration_sec"])]

    # Novelty is an exclusion, not a nudge: a mastery gap of ~250 outbids any
    # penalty small enough to be safe. Falls back rather than starving a small pool.
    recent = set(state.recent[-NOVELTY_WINDOW:])
    fresh = [s for s in paced if s["story_id"] not in recent]
    pool = fresh or paced

    by_id = {s["story_id"]: s for s in stories}
    story = max(pool, key=lambda s: _score(state, s, by_id))

    return {
        "story": story,
        "measurement": serve_measurement(state, story, items),
        "discussion": serve_discussion(state, story, items, co_read),
    }


def _score(state, story, by_id) -> float:
    """Largest gap to mastery among the skills this story exercises, weighted by
    how central each skill is to the story.

    The weight is load-bearing. Every story exercises all six C skills (all have
    prior > 0), so an unweighted `max(gap)` is the SAME number for every story and
    the score discriminates nothing — which made selection a no-op that story order
    and the novelty rotation were silently deciding.

    `prior` is ordinal (3 = central, 1 = incidental) so it scales the gap rather
    than being summed into a practice score (schema §2).
    """
    gaps = [(TARGET - state.rating(skill)) * (prior / 3.0)
            for skill, prior in story["skills"].items() if prior > 0]
    if not gaps:
        return 0.0
    return max(gaps) - _novelty_penalty(state, story, by_id)


def _novelty_penalty(state, story, by_id) -> float:
    """Soft nudge against repeating *themes/characters* across different stories.

    Repeats of the same story_id are handled by exclusion in `select_next`; this
    covers the other half — a fresh fable about the same jackal.
    """
    recent = [by_id[i] for i in state.recent[-NOVELTY_WINDOW:] if i in by_id]
    overlap = 0
    for past in recent:
        overlap += len(set(story["themes"]) & set(past["themes"]))
        overlap += len({c["name"] for c in story["characters"]}
                       & {c["name"] for c in past["characters"]})
    return NOVELTY_PENALTY * overlap


def serve_measurement(state, story, items) -> list[dict]:
    """Band-invariant by design (schema §3) — identical items for every child.

    Ordered closest-to-the-child's-rating first, which is where the information
    is. `suitable_from_age` is a hint, never a filter.
    """
    mine = [i for i in items["measurement"] if i["story_id"] == story["story_id"]]
    return sorted(mine, key=lambda i: abs(item_rating(i["difficulty_prior"])
                                         - state.rating(i["skill"])))


def reading_band(state, story) -> str:
    """The band of the TEXT this child will actually read.

    Usually the child's storage band, but a story whose only band is '9+' is read in
    9+ by everyone who can reach it — including a 9-year-old, whose storage band is
    '4-9'. Matching discussion prompts on the storage band alone served those children
    zero prompts.
    """
    bands = story["age_map"]["bands"]
    return state.band if state.band in bands else bands[0]


def serve_discussion(state, story, items, co_read: bool) -> list[dict]:
    """Band-specific. Never scored — these go to the parent as raw text.

    Gated twice: sub-band depth caps the M level, and `requires_adult` (M4/M5,
    derived not authored) keeps a solo "morality question" from shipping by
    accident (schema §3).
    """
    cap = MAX_M[state.sub_band]
    band = reading_band(state, story)
    return [p for p in items["discussion"]
            if p["story_id"] == story["story_id"]
            and p["band"] == band
            and int(p["skill"][1]) <= cap
            and (co_read or not p["requires_adult"])]
