"""Rewrite options so the correct answer is no longer the *unique longest*.

The MCQ length tell: model-drafted items gave the correct option a full
cause/effect clause while distractors stayed terse, so the right answer was the
only longest option in 156/210 draft rows (74%) — pick the longest and score 74%
without reading. (Position was the same class of bug; that one *was* mechanical and
is fixed in `shuffle_options.py`. Length is not: it needs a rewrite.)

This patch covers the 35 such items in stories the engine actually serves at ages
4-11. Correct-option index is preserved; only option *text* changes. Applied as a
set, so re-running is a no-op.

    python3 scripts/fix_length_tell.py [--dry-run]

The remaining ~121 items live in stories no child reaches yet — left flagged by
`review.py --flag` rather than rewritten blind.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "story_items_authored.json"

# (story_id, skill) -> full replacement option list, same order and count.
PATCH = {
    ("PT003", "C3_character_motive"): [
        "They wanted Lively's food and water",
        "They were jealous of Lively",
        "They were afraid Lively would eat them"],
    ("PT003", "C2_cause_effect"): [
        "He stayed in the mud and never moved again",
        "He was caught and eaten by the lion Rusty",
        "He got up and grew healthy again"],
    ("PT007", "C2_cause_effect"): [
        "Godly always carried the treasure into the temple",
        "A guard stood watching the treasure day and night",
        "He could not break through the stone wall"],
    ("PT010", "C3_character_motive"): [
        "The snake stole the crow's food",
        "The snake wanted to take over the whole tree",
        "The snake ate the crow's chicks"],
    ("PT010", "C2_cause_effect"): [
        "She did not like the banyan tree",
        "She wanted to live near the jackal",
        "She wanted to protect her chicks"],
    ("PT010", "C5_inference"): [
        "The crow would have to fight the snake alone",
        "The snake would bring trouble on itself",
        "The snake would leave the tree on its own"],
    ("PT017", "C1_sequence"): [
        "Passion slept through the owl's hoot",
        "The archer shot the swan",
        "The owl visited Passion at the lake",
        "A caravan came to the lake"],
    ("PT017", "C2_cause_effect"): [
        "He forgot where Lotus Grove was",
        "The owl told him not to come",
        "He was too tired from playing",
        "He thought the owl was dull"],
    ("PT020", "C3_character_motive"): [
        "She wanted to lay her eggs safely",
        "She was afraid of the turtles",
        "She wanted a bigger home by the sea",
        "She wanted to move far away from Sprawl"],
    ("PT020", "C2_cause_effect"): [
        "He fell into the ocean",
        "He bragged a lot",
        "He caught a big fish",
        "He told her a funny joke"],
    ("PT022", "C3_character_motive"): [
        "He was tired of his friends",
        "Another fish had chased him away",
        "He heard fishermen were coming",
        "He wanted a bigger lake"],
    ("PT022", "C2_cause_effect"): [
        "The fishermen never came",
        "He was caught in the net",
        "He hid safely and escaped",
        "Forethought came back to save him"],
    ("PT023", "C2_cause_effect"): [
        "He was angry at the sparrows",
        "He wanted to eat the eggs inside",
        "He was feverish, hot and thirsty",
        "He wanted to build his own nest there"],
    ("PT023", "C5_inference"): [
        "To ask the elephant to say sorry",
        "To scare the elephant away with loud croaking",
        "To build a new nest for the sparrows",
        "To trick the elephant into a pit"],
    ("PT024", "C2_cause_effect"): [
        "It was taking food from the fig tree",
        "It was blocking the sunlight",
        "He feared someone could climb it",
        "It was too pretty to keep"],
    ("PT024", "C1_sequence"): [
        "The hunter used a long ladder",
        "They forgot to come home at night",
        "They flew away and got lost",
        "They ignored the old gander"],
    ("PT024", "C5_inference"): [
        "Call other birds to attack the hunter",
        "Pretend to be dead and then fly up",
        "Fly away quietly during the night",
        "Bite the hunter until he runs away"],
    ("PT025", "C2_cause_effect"): [
        "Because the ram charged at him first",
        "Because he thought the ram was weak",
        "Because the ram took his food",
        "Because the ram had big horns and thick fleece"],
    ("PT025", "C3_character_motive"): [
        "The ram was guarding a pile of meat",
        "The ram roared loudly at the lion",
        "His big horns made him look strong",
        "The ram was bigger than the lion"],
    ("PT025", "C6_theme"): [
        "Never leave your flock",
        "Don't judge by appearances",
        "Lions are afraid of all horns",
        "Always eat grass to stay healthy"],
    ("PT027", "C1_sequence"): [
        "He had been too sick to get up",
        "He had gone to heaven",
        "He had gone to the forest to find Vindhyaka",
        "He had been reading the stars all night"],
    ("PT027", "C3_character_motive"): [
        "The monk was his brother",
        "He was afraid of the monk",
        "Counselor Strong told him to",
        "He loved the monk's stories"],
    ("PT027", "C6_theme"): [
        "Don't believe everything you hear",
        "Always obey your counselor",
        "Kings should never leave their city",
        "Monks should never be trusted"],
    ("PT031", "C3_character_motive"): [
        "Because the magistrates told him to",
        "Because Right-Mind really stole it",
        "To blame his friend instead",
        "Because his father asked him to"],
    ("PT031", "C6_theme"): [
        "Always share your money",
        "Never trust a friend",
        "Think before you act",
        "Merchants should never travel"],
    ("PT035", "C5_inference"): [
        "The thief ran away with them",
        "He found no gem in the thief",
        "They gave him the gems",
        "The bird told him to let them go"],
    ("PT059", "C3_character_motive"): [
        "To hide from the lover",
        "To take a nap",
        "To scare his wife",
        "To test his wife"],
    ("PT059", "C2_cause_effect"): [
        "He sent his wife away",
        "He beat the lover",
        "He went back to the forest",
        "He carried the lover away"],
    ("PT059", "C1_sequence"): [
        "She invited her old lover",
        "She stubbed her toe",
        "She cleaned the whole house",
        "She locked the door"],
    ("PT082", "C6_theme"): [
        "Never eat cucumbers at night.",
        "Singing is always a bad idea.",
        "Jackals make dangerous friends.",
        "Listen to good advice."],
    ("PT084", "C2_cause_effect"): [
        "Seedy kicked it in his dream.",
        "His wife knocked it down.",
        "It fell off the peg by itself.",
        "His friends pushed it over."],
    ("PT084", "C6_theme"): [
        "Never keep food in a jar.",
        "Daydreaming always brings gold.",
        "Don't let daydreams fool you.",
        "Friends should never laugh at you."],
    ("PT086", "C3_character_motive"): [
        "To marry the princess in secret.",
        "To learn about his rival.",
        "To escape from the palace guards.",
        "To steal the best horse in the stable."],
    ("PT086", "C2_cause_effect"): [
        "It spoke to him in a human voice.",
        "It did not respond to the bit.",
        "It was standing inside a magic circle.",
        "It refused to eat any hay."],
    ("PT086", "C6_theme"): [
        "Horses should never be trusted.",
        "Princesses should not have friends.",
        "Even the cunning can be fooled.",
        "Thieves always win in the end."],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    doc = json.loads(PATH.read_text())
    items = doc["items"]
    for (sid, skill), new_opts in PATCH.items():
        rows = [r for r in items[sid]["measurement"] if r[0] == skill]
        assert len(rows) == 1, f"{sid}/{skill}: {len(rows)} matching rows"
        row = rows[0]
        assert len(row[2]) == len(new_opts), f"{sid}/{skill}: option count changed"
        old, correct = row[2], row[3]
        row[2] = new_opts
        lo = [len(o) for o in old]
        ln = [len(o) for o in new_opts]
        assert ln[correct] < max(ln), f"{sid}/{skill}: correct is still the longest"
        assert len(set(new_opts)) == len(new_opts), f"{sid}/{skill}: duplicate options"
        print(f"{sid}/{skill}: correct {lo[correct]}->{ln[correct]}ch  "
              f"max now at index {ln.index(max(ln))} (correct at {correct})")

    print(f"\npatched {len(PATCH)} items")
    if args.dry_run:
        print("dry run — nothing written")
        return
    PATH.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {PATH}")


if __name__ == "__main__":
    main()
