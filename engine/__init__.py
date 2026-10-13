"""Adaptive story engine, v0 — Elo, cold-starting off the authored priors.

    from engine import ChildState, load_corpus, select_next, apply_story

    stories, items = load_corpus()
    state = ChildState.new("c1", 6, all_skills(stories))

    lesson = select_next(state, stories, items, co_read=False)
    ... serve lesson["story"], lesson["measurement"], lesson["discussion"] ...
    apply_story(state, lesson["story"], items_by_id, {"PT005-C2-m1": True})

See `engine/demo.py` for a runnable end-to-end pass. This module is the contract
the app shell consumes; the app owns persistence, serving and telemetry.
"""

from .select import all_skills, load_corpus, select_next, serve_discussion, serve_measurement
from .state import ChildState, band_for_age, rating_for_age, sub_band_for_age
from .update import apply_responses, apply_story, expected, item_rating

__all__ = [
    "ChildState", "all_skills", "apply_responses", "apply_story", "band_for_age",
    "expected", "item_rating", "load_corpus", "rating_for_age", "select_next",
    "serve_discussion", "serve_measurement", "sub_band_for_age",
]
