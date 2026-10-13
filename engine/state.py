"""Child profile + per-skill rating state, persisted as JSON.

Rating scale (shared with `engine/update.py`):

    BASE   1200  == the difficulty of an item with prior 2
    STEP    100  rating points per step of the 0-3 prior scale
    TARGET 1350  == mastered (reliably clears prior-3.5 items)

Authored tags are *priors*; these numbers are where the engine starts, not what
it believes (schema §1). Every constant below is a cold-start knob — a straight
line, not a fitted curve. Tune once real response data exists.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

BASE = 1200.0
STEP = 100.0
K = 32.0
TARGET = BASE + 1.5 * STEP

PRIOR_AT_AGE_4 = 0.5
PRIOR_PER_YEAR = 0.2
CAPACITY_AT_AGE_4 = 120.0   # seconds of story a 4-year-old is assumed to sustain
CAPACITY_PER_YEAR = 45.0
RAMP = 1.2                  # stretch above current capacity when serving
CAPACITY_GROWTH = 0.05      # per completed story

MIN_AGE, MAX_AGE = 3, 15


def band_for_age(age: int) -> str:
    """Storage band. The corpus is built in these two."""
    return "4-9" if age <= 9 else "9+"


def sub_band_for_age(age: int) -> str:
    """Serving band — schema §5. 4-9 spans five years; precision is free."""
    return "4-6" if age <= 6 else "7-9" if age <= 9 else "10+"


def rating_for_age(age: int) -> float:
    prior = min(max(PRIOR_AT_AGE_4 + PRIOR_PER_YEAR * (age - 4), 0.0), 3.0)
    return BASE + (prior - 2.0) * STEP


def capacity_for_age(age: int) -> float:
    return CAPACITY_AT_AGE_4 + CAPACITY_PER_YEAR * (age - 4)


@dataclass
class ChildState:
    """One child. `ratings` is one Elo per skill; cold start is per-skill flat."""

    child_id: str
    age: int
    ratings: dict[str, float]
    attention_capacity_sec: float
    recent: list[str] = field(default_factory=list)
    served: int = 0

    @classmethod
    def new(cls, child_id: str, age: int, skills) -> "ChildState":
        # Age arrives from the app — a trust boundary, so it gets a guard.
        if not isinstance(age, int) or not MIN_AGE <= age <= MAX_AGE:
            raise ValueError(f"age must be an int in {MIN_AGE}..{MAX_AGE}, got {age!r}")
        return cls(
            child_id=str(child_id),
            age=age,
            ratings={s: rating_for_age(age) for s in skills},
            attention_capacity_sec=capacity_for_age(age),
        )

    @property
    def band(self) -> str:
        return band_for_age(self.age)

    @property
    def sub_band(self) -> str:
        return sub_band_for_age(self.age)

    def rating(self, skill: str) -> float:
        return self.ratings.get(skill, rating_for_age(self.age))

    def save(self, path) -> None:
        Path(path).write_text(json.dumps(asdict(self), indent=2))

    @classmethod
    def load(cls, path) -> "ChildState":
        return cls(**json.loads(Path(path).read_text()))
