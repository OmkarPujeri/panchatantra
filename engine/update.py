"""Elo updates. One rating per (child, skill); item difficulty comes from its prior.

Deliberately *not* here: writing story-level `calibration.difficulty_b` back to
`story_tags.json`. Schema §4 — never calibrate from a single response; that needs
n_observations across many children and is a later step, not v0.
"""

from __future__ import annotations

from .state import BASE, CAPACITY_GROWTH, K, STEP

RECENT_WINDOW = 5


def item_rating(difficulty_prior: float) -> float:
    return BASE + (difficulty_prior - 2.0) * STEP


def expected(r_child: float, r_item: float) -> float:
    """Logistic Elo. P(child rates this item correct)."""
    return 1.0 / (1.0 + 10 ** ((r_item - r_child) / 400.0))


def apply_responses(state, items_by_id, responses) -> dict:
    """responses: {item_id: bool}. Mutates `state.ratings` in place.

    Returns {skill: {"before": r, "after": r}} for the skills that moved.
    """
    moved: dict[str, dict] = {}
    for item_id, correct in responses.items():
        item = items_by_id[item_id]
        skill = item["skill"]
        before = state.rating(skill)
        after = before + K * (float(bool(correct)) - expected(before, item_rating(item["difficulty_prior"])))
        state.ratings[skill] = after
        moved.setdefault(skill, {"before": before, "after": after})["after"] = after
    return moved


def apply_story(state, story, items_by_id, responses, completed: bool = True) -> dict:
    """Fold one finished story back into the child's state.

    Growth only — a drop-off leaves capacity unchanged. Shrinking needs the
    *point* of drop-off, which is telemetry (step 3), not a guess.
    """
    deltas = apply_responses(state, items_by_id, responses)
    state.recent.append(story["story_id"])
    state.recent = state.recent[-RECENT_WINDOW:]
    state.served += 1
    if completed:
        state.attention_capacity_sec *= 1.0 + CAPACITY_GROWTH
    return deltas
