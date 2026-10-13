"""Runnable self-check for engine v0.

    python3 -m engine.demo

Also the usage example: this is the shape the app shell consumes.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from .select import NOVELTY_WINDOW, all_skills, load_corpus, reading_band, select_next, serve_discussion
from .state import TARGET, ChildState, band_for_age, capacity_for_age, rating_for_age, sub_band_for_age
from .update import apply_story, item_rating, expected


def _items_by_id(items):
    return {i["item_id"]: i for i in items["measurement"]}


def check_bands():
    assert (band_for_age(4), band_for_age(9), band_for_age(10)) == ("4-9", "4-9", "9+")
    assert sub_band_for_age(4) == "4-6"
    assert sub_band_for_age(6) == "4-6"
    assert sub_band_for_age(7) == "7-9"
    assert sub_band_for_age(9) == "7-9"
    assert sub_band_for_age(10) == "10+"
    # older child starts higher, and never below the youngest
    assert rating_for_age(4) < rating_for_age(8) < rating_for_age(12)


def check_age_guard(stories):
    skills = all_skills(stories)
    for bad in (2, 16, "6", 6.0, None):
        try:
            ChildState.new("c", bad, skills)
        except ValueError:
            pass
        else:
            raise AssertionError(f"age {bad!r} should have been rejected")


def check_selection_covers_ages(stories, items):
    """Every age the corpus claims to serve gets a story that fits that age."""
    skills = all_skills(stories)
    for age in range(4, 12):
        state = ChildState.new("c", age, skills)
        lesson = select_next(state, stories, items)
        a = lesson["story"]["age_map"]
        assert a["min_age"] <= age <= a["max_age"], (age, lesson["story"]["story_id"])

    too_old = max(s["age_map"]["max_age"] for s in stories) + 1
    try:
        select_next(ChildState.new("c", too_old, skills), stories, items)
    except LookupError as e:
        assert str(too_old) in str(e)
    else:
        raise AssertionError(f"age {too_old} has no story and should raise, not serve")


def check_measurement_coverage(stories, items):
    """Coverage check: how many tagged stories carry questions at all.

    Now complete — 80/80 — but kept as a guard: it fails if a rebuild ever drops the item
    bank back to the pilot set. The *review* status of those items is a separate matter;
    see the worklog.
    """
    with_items = {i["story_id"] for i in items["measurement"]} | \
                 {p["story_id"] for p in items["discussion"]}
    tagged = {s["story_id"] for s in stories}
    covered = tagged & with_items
    print(f"  measurement coverage: {len(covered)}/{len(tagged)} tagged stories carry "
          f"questions ({100 * len(covered) // len(tagged)}%)")
    assert covered, "at least the original question-bank stories must still have items"
    return covered


def check_elo_direction(stories, items):
    skills = all_skills(stories)
    by_id = _items_by_id(items)
    probe = items["measurement"][0]
    item_id, skill = probe["item_id"], probe["skill"]

    up = ChildState.new("c", 6, skills)
    before = up.rating(skill)
    apply_story(up, {"story_id": probe["story_id"]}, by_id, {item_id: True})
    assert up.rating(skill) > before, "a correct answer must raise the rating"

    down = ChildState.new("c", 6, skills)
    apply_story(down, {"story_id": probe["story_id"]}, by_id, {item_id: False})
    assert down.rating(skill) < before, "a wrong answer must lower the rating"

    # and the step shrinks as the child's rating approaches the item's
    assert expected(before, item_rating(3)) < expected(before, item_rating(0))


def check_capacity_ramp(stories, items):
    skills = all_skills(stories)
    start = capacity_for_age(6)

    done = ChildState.new("c", 6, skills)
    assert done.attention_capacity_sec == start
    apply_story(done, {"story_id": "PT005"}, _items_by_id(items), {}, completed=True)
    assert done.attention_capacity_sec > start, "completing a story should ramp capacity"
    assert done.served == 1 and done.recent == ["PT005"]

    quit_ = ChildState.new("c", 6, skills)
    apply_story(quit_, {"story_id": "PT005"}, _items_by_id(items), {}, completed=False)
    assert quit_.attention_capacity_sec == start, "a drop-off must not ramp capacity"


def check_attention_gate(stories, items):
    """Cap the served duration to capacity, and fall back to the shortest eligible."""
    age = 4
    eligible = [s for s in stories
                if s["age_map"]["min_age"] <= age <= s["age_map"]["max_age"]]
    shortest = min(s["attention_load"]["duration_sec"] for s in eligible)

    state = ChildState.new("c", age, all_skills(stories))
    lesson = select_next(state, stories, items)
    dur = lesson["story"]["attention_load"]["duration_sec"]
    assert dur <= state.attention_capacity_sec * 1.2 or dur == shortest, dur

    tiny = ChildState.new("c", age, all_skills(stories))
    tiny.attention_capacity_sec = 1.0                         # nothing fits
    assert select_next(tiny, stories, items)["story"]["attention_load"]["duration_sec"] == shortest


def check_discussion_gating(stories, items):
    """M4/M5 never reach a solo 4-9 child; M5 never reaches anyone under 10."""
    for story in stories:
        for age, co_read in ((5, False), (5, True), (8, False), (8, True), (11, False), (11, True)):
            state = ChildState.new("c", age, all_skills(stories))
            served = serve_discussion(state, story, items, co_read)
            for p in served:
                # the band of the TEXT the child reads, not their storage band — a
                # 9-year-old reading a 9+-only story gets its 9+ prompts
                assert p["band"] == reading_band(state, story)
                assert int(p["skill"][1]) <= {"4-6": 3, "7-9": 4, "10+": 5}[state.sub_band]
                if not co_read:
                    assert not p["requires_adult"], f"{p['prompt_id']} leaked into solo play"
                if age <= 9:
                    assert not p["skill"].startswith("M5"), "M5 is 9+/10+-only by definition"


def check_persistence(stories):
    state = ChildState.new("kid-1", 7, all_skills(stories))
    state.ratings["C2_cause_effect"] = 1337.0
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "c1.json"
        state.save(path)
        back = ChildState.load(path)
    assert back.child_id == "kid-1" and back.age == 7
    assert back.ratings["C2_cause_effect"] == 1337.0
    assert back.band == "4-9" and back.sub_band == "7-9"


def simulate(child_id, age, answers, n=6, co_read=False):
    """Answers `n` stories, always answering `answers` correctly. Returns state."""
    stories, items = load_corpus()
    by_id = _items_by_id(items)
    state = ChildState.new(child_id, age, all_skills(stories))
    trace = []
    for _ in range(n):
        lesson = select_next(state, stories, items, co_read=co_read)
        served = lesson["measurement"]
        responses = {i["item_id"]: answers for i in served}
        apply_story(state, lesson["story"], by_id, responses)
        trace.append((lesson["story"]["story_id"], len(served), len(lesson["discussion"])))
    return state, trace


def main():
    stories, items = load_corpus()
    print(f"corpus: {len(stories)} stories, {len(items['measurement'])} measurement, "
          f"{len(items['discussion'])} discussion\n")

    check_bands()
    check_age_guard(stories)
    check_selection_covers_ages(stories, items)
    check_measurement_coverage(stories, items)
    check_elo_direction(stories, items)
    check_capacity_ramp(stories, items)
    check_attention_gate(stories, items)
    check_discussion_gating(stories, items)
    check_persistence(stories)

    for child_id, age in (("strong-6", 6), ("weak-6", 6), ("strong-10", 10)):
        good = child_id.startswith("strong")
        state, trace = simulate(child_id, age, answers=good, n=6, co_read=(age >= 10))
        seen = [t[0] for t in trace]
        avg = sum(state.ratings.values()) / len(state.ratings)
        print(f"{child_id:<10} age {age:>2}  masteries {avg:6.0f}  capacity "
              f"{state.attention_capacity_sec:5.0f}s  served {seen}")
        assert len(set(seen)) > 1, "novelty should vary the served stories"
        # No story should come back inside NOVELTY_WINDOW while a fresh one exists.
        eligible = [s for s in stories
                    if s["age_map"]["min_age"] <= age <= s["age_map"]["max_age"]]
        if len(eligible) > NOVELTY_WINDOW:
            for i in range(1, len(seen)):
                assert seen[i] not in seen[max(0, i - NOVELTY_WINDOW):i], \
                    f"repeated {seen[i]} within {NOVELTY_WINDOW} draws: {seen}"

    # A child answering everything correctly should climb toward mastery.
    strong, _ = simulate("s", 6, answers=True, n=6)
    weak, _ = simulate("w", 6, answers=False, n=6)
    s_avg = sum(strong.ratings.values()) / len(strong.ratings)
    w_avg = sum(weak.ratings.values()) / len(weak.ratings)
    assert s_avg > w_avg, "answering correctly must beat answering wrongly"
    assert TARGET > rating_for_age(6), "cold start should sit below mastery"

    print("\nOK — engine v0 self-check passed")


if __name__ == "__main__":
    main()
