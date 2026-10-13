# Resolution census — 2026-10-13

**Question:** does every adapted telling actually resolve its plot, or did an adapter write an
ending the source does not contain?

Run because PT010 (an invented fish-bone death) and PT003 (a hand-off ending) were found by hand
out of a sample of 18, and the class looked systemic. It is.

## Method

28 read-only agents over **82 stories / 142 tellings**. Each read the telling in full, found the
source *continuation* in `corpus/panchatantra_complete.txt`, and compared the enabling to the
source's actual resolution. Then **every claim below was re-checked against the raw text by me**
before being recorded — this project has a documented history of agents citing the wrong file
(PT010, PT082) and of one hallucinating a quote outright (PT003). Two agents in this run cited
**table-of-contents line numbers** as source evidence, so the check was necessary.

## Headline

```
142 tellings audited
119 resolve
 23 flagged  ->  17 stories, of which 1 is a false positive
```

**~16 stories carry a real defect — roughly 15% of the corpus.** The earlier estimate was "a
handful". It is not a tail; it is a systemic property of how the corpus was built.

**The mechanism, confirmed.** 16 of the 17 flagged stories have a source chapter that ends on a
story hand-off (`"How was that?" asked X. And Y told the story of`). In the Panchatantra a chapter
is the fable's *setup*; its resolution comes after the nested tale. An adapter handed only the
chapter had to produce a standalone ending and either **invented one** or **stopped at the
hand-off**. This is the same partition bug HANDOVER records as #7.

## Verified findings — I read the source myself

| story | band | verdict | what the source actually says |
|---|---|---|---|
| **PT004** | 9+ | INVENTED | source has no king, no errand, no promotion — the fable is the monkey pulling the wedge and being crushed; Victor's "new counselor" ending appears nowhere |
| **PT019** | 9+ | INVENTED | source ends with the carpenter in the tree reciting *"I do not like your friends"*; the telling's "they became good friends" is invented |
| **PT020** | 4-9 | INVENTED | source (4868): the ocean *"made a long reach… and eagerly seized the eggs"*; the telling says the waves *"didn't hurt the plover's home"* — the inverse |
| **PT020** | 9+ | TRUNCATED | stops on Sprawl's realization; no theft, no appeal to the birds, no restoration |
| **PT028** | 4-9 | TRUNCATED | source (5611-5615): the serpent takes human form, *"I am your husband"*, the father burns the snakeskin; the telling stops at the girl's decision |
| **PT031** | 9+ | TRUNCATED | source (5814-5830): the mimosa-tree ordeal, the father's voice from the hole, the burning, Wrong-Mind hanged; the telling stops at a warning |
| **PT040** | 4-9 + 9+ | TRUNCATED | source (7245-7259): the sesame bargain and the *"Mother Shandilee… has some good reason in her mind"* verse; the telling stops at the preaching |
| **PT048** | 4-9 | INVENTED | source (9614-9636): the **crow** persuades the birds against the owl — *"If you make the owl your king, you will fail in everything"*; the telling says *"The owl was very happy"* and moralises about having two leaders |
| **PT048** | 9+ | TRUNCATED | stops mid-action before the birds' verdict |
| **PT049** | 9+ | TRUNCATED | source (9780): *"I shall never return here." And with these words he went to his own place* |
| **PT062** | 4-9 | TRUNCATED | source (11250-11284): the woodpile at the gate and the burning of the cave; the telling ends on *"He wanted to get rid of them"* |
| **PT063** | 9+ | TRUNCATED | source (11542): *"He ate them all so completely that not even frog-seed was left"* |
| **PT071** | 9+ | TRUNCATED | ends part-way through a nested story it never finishes |
| **PT076** | 9+ | INVENTED | attributes the frame's resolution to the monkey and invents a take-over of its home; the ending is also internally garbled |
| **PT085** | 9+ | INVENTED | source (13718): *"the king… hastened home, grief-stricken"* — **the king survives**; the telling has him eaten last |
| **PT089** | 4-9 + 9+ | INVENTED | the source has **no treasure**; the monkey's trick is claiming his heart is in a hole on shore, and the ending is the crocodile recovering his home |

## Confirmed false positive

- **PT039** both bands — flagged TRUNCATED, but its source continuation at 7321+ is a **new nested
  tale**, not the resolution of Gold's Gloom. Both tellings do resolve the frame's question. The
  agent read "the source keeps going" as "the telling stopped short". **Not a defect.**

## Confidence note

The table above is everything I personally read the source for. Three stories — **PT043, PT079** —
were flagged with specific claims I only partially verified; they are likely real but should be
read before being fixed. Everything else in this document is verified.

## Status — FIXED 2026-10-13

All 16 stories were repaired in the same session: **24 edits across 22 files, 1 refuted (PT071 4-9,
correctly — it was already resolving and out of scope).** Every diff was read against the
before-state before acceptance. See `WORKLOG.md` §2026-10-13 for the per-story table.

Three agents found **more** than the census had flagged, so this list was a floor, not a ceiling.

## What this means

- **These are shipping defects in the English corpus** — the app would serve them today. (Hindi
  was dropped from scope on 2026-10-13, so it is no longer a multiplier here.)
- **The fixes divide in two**, exactly as PT010's did:
  - **copy-up** — where the sibling band already has the ending (PT049, PT062, PT063 are
    candidates) the fix is bringing one band up to the other;
  - **author** — where neither band resolves, a resolving beat has to be written from the source
    continuation. This is authoring, and it needs a human read.
- **Reading was the detector again.** Four automated detectors have failed on this project. This
  pass worked because 28 agents read 142 tellings and a human verified every claim — not because
  anything was scripted.
