#!/usr/bin/env python3
"""Age-adapt the Panchatantra corpus into two children's reading bands (4-9 and 9+).

Reads corpus/panchatantra.json, extracts clean fable texts, sends each fable through
an LLM (Ollama, OpenAI, or Anthropic) with band-calibrated prompts, validates the
result against readability metrics (Flesch-Kincaid grade, words per sentence),
retries with self-correcting feedback upon misses, and writes the output files to
corpus/age/<band>/.

Usage:
    # Pilot run on 10 classic fables
    python scripts/adapt.py --band 4-9 --pilot
    python scripts/adapt.py --band 9+ --pilot

    # Single story test
    python scripts/adapt.py --band 4-9 --story PT005

    # Full batch run
    python scripts/adapt.py --band 4-9 --all
    python scripts/adapt.py --band 9+ --all

    # Inspect metrics of generated texts
    python scripts/adapt.py --band 4-9 --check
    python scripts/adapt.py --band 9+ --check
"""
import argparse
import glob
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
CORPUS = os.path.join(ROOT, "corpus")
DATA = os.path.join(ROOT, "data")
CONFIG_PATH = os.path.join(DATA, "adapt_config.json")
CURATION = os.path.join(DATA, "curation.json")
MASTER_JSON = os.path.join(CORPUS, "panchatantra.json")

sys.path.insert(0, HERE)
from readability import check_target, metrics  # noqa: E402

PROMPT_VERSION = "v2"

# 10 well-known fables spanning diverse animals and themes for pilot validation
PILOT_STORIES = [
    "PT005",  # The Jackal and the War-Drum
    "PT008",  # The Jackal at the Ram-Fight
    "PT012",  # Numskull and the Rabbit
    "PT015",  # Leap and Creep
    "PT016",  # The Blue Jackal
    "PT021",  # Shell-Neck, Slim, and Grim (The Tortoise and the Geese)
    "PT033",  # The Mice That Ate Iron
    "PT045",  # The Mice That Set Elephants Free
    "PT062",  # The Cave That Talked
    "PT065",  # The Monkey and the Crocodile
]

DEFAULT_CONFIG = {
    "provider": "openai",
    "base_url": "http://localhost:11434/v1",
    "model": "llama3.1:latest",
    "api_key_env": "ADAPT_API_KEY",
    "api_key": "ollama",
    "temperature": 0.35,
    "max_tokens": 2500,
    "timeout": 180,
    "max_retries": 2,
}

BANDS = {
    "4-9": {
        "label": "children aged 4 to 9",
        "description": "Early reader / bedtime read-aloud",
        "fk_grade": (1.0, 4.8),
        "words_per_sentence": (5.0, 13.0),
        "max_syllables_per_word": 1.42,
        "word_count": (70, 700),
    },
    "9+": {
        "label": "children aged 9 and older",
        "description": "Independent reader (9 to 12+)",
        "fk_grade": (3.5, 8.5),
        "words_per_sentence": (8.0, 18.5),
        "max_syllables_per_word": 1.55,
        "word_count": (70, 1500),
    },
}

SYSTEM_PROMPTS = {
    "4-9": """\
You are adapting a classic Indian fable from the Panchatantra for children aged 4 to 9.

Rules:
1. Tell the SAME story. Keep the same characters, same sequence of events, and same ending.
2. Very short sentences (aim for 5 to 10 words per sentence). Use simple, everyday words that a 6-year-old understands. Keep the tone warm, clear, and gentle like a bedtime story.
3. Completely remove every poem, verse, and rhyming passage from the original. NEVER quote proverbs or sayings (do not say "as the proverb says"). Completely omit all proverbs.
4. Do not invent new events, characters, or lessons.
5. Keep character names as given (e.g. Red-Face, Ugly-Mug, Fierce-Howl, Numskull).
6. Format strictly as follows:
Line 1: Story Title
Line 2: [Blank]
Line 3+: The story in short, clear paragraphs
Last line: Moral: <one simple, memorable sentence>
""",
    "9+": """\
You are adapting a classic Indian fable from the Panchatantra for young readers aged 9 and older.

Rules:
1. Tell the SAME story. Keep the same characters, same sequence of events, and same ending.
2. Keep sentences brisk and lively (aim for 10 to 14 words per sentence). Natural, engaging prose for a 9 to 12 year old. Not babyish, but avoid overly long or rambling sentences.
3. Completely remove every poem, verse, and rhyming stanza. NEVER quote poetry, proverbs, or sayings. Describe character thoughts and morals in natural prose.
4. Do not invent new characters or events. Keep character names as given.
5. Format strictly as follows:
Line 1: Story Title
Line 2: [Blank]
Line 3+: The story in paragraphs
Last line: Moral: <one insightful sentence>
"""
}


def load_config():
    os.makedirs(DATA, exist_ok=True)
    cfg = dict(DEFAULT_CONFIG)
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg.update(json.load(f))
        except Exception:
            pass
    else:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)

    for key, env in (("api_key", "ADAPT_API_KEY"), ("base_url", "ADAPT_BASE_URL"),
                     ("model", "ADAPT_MODEL")):
        if os.environ.get(env):
            cfg[key] = os.environ[env]
    cfg.setdefault("api_key", os.environ.get(cfg["api_key_env"], "ollama"))
    return cfg


def load_corpus():
    """Load stories directly from corpus/panchatantra.json with clean fable texts."""
    if not os.path.exists(MASTER_JSON):
        raise FileNotFoundError(f"Missing master corpus: {MASTER_JSON}")
    with open(MASTER_JSON, "r", encoding="utf-8") as f:
        doc = json.load(f)
    return {s["story_id"]: s for s in doc["stories"]}


def get_clean_source_fable(story):
    """Isolate clean fable text, stripping chapter headers and frame leftovers."""
    if story.get("scoped_to_fable") and story.get("fable_text"):
        raw = story["fable_text"]
    else:
        raw = story.get("text", "")

    # Strip repeated all-caps title header
    raw = re.sub(r"\A\s*[A-Z][A-Z\s,'\-]{3,}\n+", "", raw.strip())
    # Strip opening lines like "And so-and-so told the story of..."
    raw = re.sub(r"\A(?:[^\n]+\btold the story of[^\n]*\n+)", "", raw, flags=re.I)
    return raw.strip()


def build_prompt(story, band):
    source = get_clean_source_fable(story)
    system = SYSTEM_PROMPTS[band]
    user = f"Title: {story['title']}\n\nAdapt this Panchatantra fable for {BANDS[band]['label']}:\n\n---\n{source}\n---"
    return system, user, source


def call_model(cfg, system, user, feedback=""):
    if feedback:
        user = (
            f"{user}\n\n---\n"
            f"IMPORTANT FIX REQUIRED: Your previous output had the following issues:\n{feedback}\n"
            f"Please rewrite the story carefully to correct this while keeping all other rules."
        )

    if cfg["provider"] == "anthropic":
        url = cfg["base_url"].rstrip("/") + "/messages"
        payload = {
            "model": cfg["model"],
            "max_tokens": cfg["max_tokens"],
            "temperature": cfg["temperature"],
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        headers = {
            "x-api-key": cfg["api_key"],
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
    else:
        url = cfg["base_url"].rstrip("/") + "/chat/completions"
        payload = {
            "model": cfg["model"],
            "max_tokens": cfg["max_tokens"],
            "temperature": cfg["temperature"],
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        headers = {
            "Authorization": f"Bearer {cfg['api_key']}",
            "content-type": "application/json",
        }

    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=cfg.get("timeout", 180)) as r:
        d = json.loads(r.read().decode("utf-8"))

    if cfg["provider"] == "anthropic":
        return "".join(b.get("text", "") for b in d.get("content", []))
    return d["choices"][0]["message"]["content"]


def clean_output(text, title=""):
    """Strip markdown code fences, model conversational chatter, and fix title header."""
    t = text.strip()
    t = re.sub(r"^```[a-z]*\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    t = re.sub(r"^(Here is|Here's)[^\n]*\n+", "", t, flags=re.I)
    t = re.sub(r"\n+(I hope|Let me know|Would you like|Hope this helps)[^\n]*$", "", t, flags=re.I)
    t = re.sub(r"^(Title|Story)\s*:\s*", "", t, flags=re.I | re.M)
    # Strip any model self-reported metadata lines at the end
    t = re.sub(r"\n+(?:Word Count|Words per sentence|FK Grade|Grade Level|Readability)[^\n]*", "", t, flags=re.I)

    # Ensure title is at the top
    lines = t.strip().splitlines()
    if lines and not lines[0].strip().lower().startswith(title.lower()[:15]):
        # If model forgot the title line, prepend it
        if title:
            t = f"{title}\n\n{t}"

    return re.sub(r"\n{3,}", "\n\n", t).strip()


def adapt_one(cfg, story, band, dry_run=False):
    system, user, source = build_prompt(story, band)
    if dry_run:
        return {"dry_run": True, "system": system, "user": user, "source": source}

    spec = dict(BANDS[band])
    # Adjust minimum word count if source fable is short
    source_words = len(source.split())
    if source_words < spec["word_count"][0]:
        spec["word_count"] = (max(50, int(source_words * 0.5)), spec["word_count"][1])

    feedback, last = "", None
    for attempt in range(cfg["max_retries"] + 1):
        raw = call_model(cfg, system, user, feedback)
        text = clean_output(raw, title=story.get("title", ""))
        m = metrics(text)
        fails = check_target(m, spec)
        last = {"text": text, "metrics": m, "fails": fails, "attempts": attempt + 1}
        if not fails:
            return last
        feedback = "; ".join(fails)

    return last


def write_manifest(out_dir, band, spec, cfg):
    rows = []
    for f in sorted(os.listdir(out_dir)):
        if not f.endswith(".txt") or f.startswith("_"):
            continue
        filepath = os.path.join(out_dir, f)
        with open(filepath, "r", encoding="utf-8") as fp:
            content = fp.read()
        m = metrics(content)
        if m:
            rows.append({"file": f, "story_id": f.split("-")[0], **m})

    manifest_data = {
        "band": band,
        "model": cfg["model"],
        "prompt_version": PROMPT_VERSION,
        "target": {k: v for k, v in spec.items() if k != "description"},
        "story_count": len(rows),
        "stories": rows,
    }
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)


def report(out_dir, band, spec):
    if not os.path.isdir(out_dir):
        print(f"nothing at {out_dir} yet")
        return 1
    man = os.path.join(out_dir, "manifest.json")
    # Rebuild every time. The directory is the source of truth and the manifest is derived;
    # the old "rebuild only if missing" reported 81 stories while 83 sat on disk, so files
    # added since the last run were never measured — the exact failure this project keeps
    # hitting, a check that reports success without looking at the thing that matters.
    write_manifest(out_dir, band, spec, load_config())
    with open(man, "r", encoding="utf-8") as f:
        d = json.load(f)
    rows = d.get("stories", [])
    if not rows:
        print(f"no adapted stories found in {out_dir}")
        return 1

    import statistics
    print(f"\n==========================================")
    print(f"BAND {band} QUALITY REPORT ({len(rows)} stories)")
    print(f"==========================================")
    print(f"Total Words           : {sum(r['words'] for r in rows):,}")
    print(f"Median FK Grade       : {statistics.median(r['fk_grade'] for r in rows):.2f} (Target: {spec['fk_grade'][0]}-{spec['fk_grade'][1]})")
    print(f"Median Words/Sentence : {statistics.median(r['words_per_sentence'] for r in rows):.2f} (Target: {spec['words_per_sentence'][0]}-{spec['words_per_sentence'][1]})")
    print(f"Median Syllables/Word : {statistics.median(r['syllables_per_word'] for r in rows):.3f} (Max: {spec['max_syllables_per_word']})")

    bad = []
    for r in rows:
        f = check_target({k: r[k] for k in ("fk_grade", "words_per_sentence", "words", "syllables_per_word")}, spec)
        if f:
            bad.append((r["story_id"], r["file"], f))

    if bad:
        print(f"\nStories outside target spec ({len(bad)}):")
        for sid, fname, fails in bad[:10]:
            print(f"  - {sid} ({fname}): {', '.join(fails)}")
    else:
        print("\nAll adapted stories satisfy target readability metrics!")

    rej = os.path.join(out_dir, "_rejected")
    if os.path.isdir(rej):
        n = len([x for x in os.listdir(rej) if x.endswith(".txt")])
        if n:
            print(f"Rejected / quarantined files in _rejected/: {n}")
    return 0


def export_unified_json():
    """Generates corpus/panchatantra_adapted.json combining original + both adapted bands."""
    corpus_dict = load_corpus()
    unified = []

    dir_4_9 = os.path.join(CORPUS, "age", "4-9")
    dir_9_plus = os.path.join(CORPUS, "age", "9+")

    for sid, s in corpus_dict.items():
        rec = {
            "story_id": sid,
            "title": s["title"],
            "book": s["book"],
            "book_name": s["book_name"],
            "source_file": s["source_file"],
            "curation": s["curation"],
            "original_fable": s.get("fable_text", ""),
            "adapted": {}
        }

        # Check 4-9
        path_4_9 = os.path.join(dir_4_9, s["source_file"])
        if os.path.exists(path_4_9):
            with open(path_4_9, "r", encoding="utf-8") as f:
                content = f.read()
            rec["adapted"]["4-9"] = {
                "text": content,
                "metrics": metrics(content)
            }

        # Check 9+
        path_9_plus = os.path.join(dir_9_plus, s["source_file"])
        if os.path.exists(path_9_plus):
            with open(path_9_plus, "r", encoding="utf-8") as f:
                content = f.read()
            rec["adapted"]["9+"] = {
                "text": content,
                "metrics": metrics(content)
            }

        unified.append(rec)

    out_file = os.path.join(CORPUS, "panchatantra_adapted.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"stories": unified}, f, indent=2, ensure_ascii=False)
    print(f"\nWrote unified dataset to {out_file}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--band", choices=sorted(BANDS), help="Age band (4-9 or 9+)")
    ap.add_argument("--story", action="append", default=[], help="Specific story ID (e.g. PT005)")
    ap.add_argument("--pilot", action="store_true", help="Run on 10 curated pilot stories")
    ap.add_argument("--all", action="store_true", help="Run on all eligible stories for this band")
    ap.add_argument("--dry-run", action="store_true", help="Write prompts without calling model")
    ap.add_argument("--check", action="store_true", help="Generate quality and readability report")
    ap.add_argument("--force", action="store_true", help="Overwrite existing files")
    ap.add_argument("--export-json", action="store_true", help="Build unified panchatantra_adapted.json")
    ap.add_argument("--model", help="Override LLM model name")
    ap.add_argument("--base-url", help="Override API base URL")
    args = ap.parse_args()

    if args.export_json:
        export_unified_json()
        return 0

    if not args.band and not args.check:
        print("Please specify --band 4-9 or --band 9+ (or --check / --export-json)")
        return 1

    cfg = load_config()
    if args.model:
        cfg["model"] = args.model
    if args.base_url:
        cfg["base_url"] = args.base_url

    out_dir = os.path.join(CORPUS, "age", args.band)
    rej_dir = os.path.join(out_dir, "_rejected")
    spec = BANDS[args.band]

    if args.check:
        return report(out_dir, args.band, spec)

    corpus_stories = load_corpus()

    # Determine story list
    if args.pilot:
        selected_ids = PILOT_STORIES
    elif args.all:
        selected_ids = sorted(corpus_stories.keys())
    elif args.story:
        selected_ids = args.story
    else:
        print("Nothing selected. Use --pilot, --all, or --story PT005")
        return 1

    os.makedirs(out_dir, exist_ok=True)
    print(f"=== Panchatantra Adaptation Pipeline ===")
    print(f"Band      : {args.band} ({spec['description']})")
    print(f"Model     : {cfg['model']} via {cfg['base_url']}")
    print(f"Target    : FK Grade {spec['fk_grade'][0]}-{spec['fk_grade'][1]}, "
          f"{spec['words_per_sentence'][0]}-{spec['words_per_sentence'][1]} w/s, "
          f"{spec['word_count'][0]}-{spec['word_count'][1]} words\n")

    done = skipped = rejected = 0

    for sid in selected_ids:
        if sid not in corpus_stories:
            print(f"  ??   {sid} not found in corpus")
            continue

        story = corpus_stories[sid]
        curation = story.get("curation", {})
        verdict = curation.get("verdict", "")
        bands = curation.get("bands", [])

        # Skip non-fable introductory matter
        if sid in ("PT001", "PT090"):
            print(f"  --   {sid} ({story['title']}) skipped: front matter / academic essay")
            skipped += 1
            continue

        # Content filtering: exclude stories flagged EXCLUDE or not meant for this band
        if verdict == "EXCLUDE":
            print(f"  --   {sid} ({story['title']}) skipped: content flagged as EXCLUDE")
            skipped += 1
            continue

        # In pilot mode or force, allow testing fables like PT016 (The Blue Jackal) even if heuristic tagged it 9+
        if not args.pilot and bands and args.band not in bands:
            print(f"  --   {sid} ({story['title']}) skipped: curated only for {bands}")
            skipped += 1
            continue

        fname = story["source_file"]
        dest = os.path.join(out_dir, fname)

        if os.path.exists(dest) and not args.force and not args.dry_run:
            print(f"  ok   {sid} already exists (use --force to overwrite)")
            skipped += 1
            continue

        if args.dry_run:
            p = adapt_one(cfg, story, args.band, dry_run=True)
            prompts_dir = os.path.join(DATA, "prompts")
            os.makedirs(prompts_dir, exist_ok=True)
            with open(os.path.join(prompts_dir, f"{sid}-{args.band}.txt"), "w", encoding="utf-8") as f:
                f.write(f"=== SYSTEM ===\n{p['system']}\n\n=== USER ===\n{p['user']}\n")
            print(f"  -->  {sid} ({story['title']}) prompt saved to data/prompts/")
            continue

        print(f"  >>   Adapting {sid}: {story['title']}...", end="", flush=True)
        t0 = time.time()
        try:
            r = adapt_one(cfg, story, args.band)
        except Exception as e:
            print(f" ERROR: {type(e).__name__}: {e}")
            continue

        elapsed = time.time() - t0
        m = r.get("metrics") or {}
        fails = r.get("fails", [])

        if fails:
            os.makedirs(rej_dir, exist_ok=True)
            with open(os.path.join(rej_dir, fname), "w", encoding="utf-8") as f:
                f.write(r["text"])
            print(f" REJECTED in {elapsed:.1f}s after {r['attempts']} attempts: {fails}")
            rejected += 1
            continue

        with open(dest, "w", encoding="utf-8") as f:
            f.write(r["text"] + "\n")

        print(f" DONE in {elapsed:.1f}s | Grade {m['fk_grade']:.1f} | {m['words_per_sentence']:.1f} w/s | {m['words']}w ({r['attempts']} attempt{'s' if r['attempts'] > 1 else ''})")
        done += 1

    if not args.dry_run:
        write_manifest(out_dir, args.band, spec, cfg)
        print(f"\nSummary for band {args.band}: {done} written, {skipped} skipped, {rejected} rejected")
        if rejected:
            print(f"Quarantined rejected outputs saved in: {rej_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
