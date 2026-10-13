"""Apply the round-2 content fixes that survived adversarial verification.

Source of truth is data/review_2026-10-13_workflow.json — the raw output of the
wf_f244e866 fan-out, kept in the repo so this script never retypes a string (a
hand-copied `old` is how you corrupt a corpus).

Same guards as apply_review_fixes.py, which this deliberately mirrors:

  * the target file is found by searching the story's OWN band files for the exact
    `old` — the band label an agent supplied is not trusted;
  * "already applied" is tested FIRST, because an append-style edit has `new`
    containing `old` and testing `old` first would re-fire forever;
  * every `old` must be present or the run refuses to write anything.

One new case: `old == ""` means whole-file replacement, used for the stories that
have no telling yet (PT022 9+, PT013 9+, PT047 9+). Those are the ones most likely
to contain authored prose, so any edit with authored_not_sourced=true is printed
with a loud AUTHORS marker — it needs a human read before it ships, by design.

    python3 scripts/apply_content_fixes.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / "data" / "review_2026-10-13_workflow.json"
BACKUP = ROOT / "data" / "apply_content_fixes_backup.json"


def band_files(sid: str):
    return sorted((ROOT / "corpus" / "age").glob(f"*/{sid}-*.txt"))


def plan(sid: str, edit: dict):
    """Return (status, path, old, new, why). status in write|skip|fail."""
    old, new = edit["old"], edit["new"]
    declared = ROOT / edit["file"]

    if old == "":  # whole-file replacement
        if declared.exists() and declared.read_text(encoding="utf-8") == new:
            return ("skip", declared, old, new, "already applied")
        return ("write", declared, old, new, None)

    # already-applied test FIRST (append-style edits contain `old` inside `new`)
    for p in band_files(sid):
        if new in p.read_text(encoding="utf-8"):
            return ("skip", p, old, new, "already applied")
    for p in band_files(sid):
        if old in p.read_text(encoding="utf-8"):
            return ("write", p, old, new, None)
    # fall back to the declared path, in case it is a rejected/ file outside the glob
    if declared.exists() and old in declared.read_text(encoding="utf-8"):
        return ("write", declared, old, new, None)
    return ("fail", None, old, new, f"`old` not found in any band file for {sid}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    doc = json.loads(WORKFLOW.read_text())
    edits = doc["confirmedEdits"]

    planned, failures = [], []
    for e in edits:
        sid = e["story"]
        r = plan(sid, e)
        (failures if r[0] == "fail" else planned).append((sid, e, r))

    for sid, e, (status, path, old, new, why) in planned:
        marker = "AUTHORS" if e.get("authored_not_sourced") else "APPLY  "
        label = "SKIP   " if status == "skip" else marker
        rel = path.relative_to(ROOT) if path else e["file"]
        print(f"  {label} {sid:6} {str(rel):64} {why or ''}")
        if e.get("authored_not_sourced") and status != "skip":
            print(f"          ^ AUTHORED CONTENT — not from the source. Human read required.")
            print(f"            {e.get('rationale','')[:150]}")
    for sid, e, r in failures:
        print(f"  FAIL   {sid:6} {e['file']} — {r[5]}")

    if failures:
        print(f"\n{len(failures)} edit(s) could not be placed — refusing to write anything.")
        return 1

    writes = [p for p in planned if p[2][0] == "write"]
    if args.dry_run:
        authored = sum(1 for _, e, r in writes if e.get("authored_not_sourced"))
        print(f"\ndry run: {len(writes)} write(s) ({authored} containing authored prose), "
              f"{len(planned) - len(writes)} already applied — nothing written")
        return 0

    backup = []
    for sid, e, (status, path, old, new, _) in writes:
        # Preserve the file's line endings. 125 of the 147 corpus files are CRLF;
        # Path.write_text() would silently rewrite them all as LF and make every
        # line show as changed in a diff — a write that "succeeds" and is still wrong.
        raw = path.read_bytes() if path.exists() else b""
        before = raw.decode("utf-8").replace("\r\n", "\n")
        backup.append({"file": str(path.relative_to(ROOT)), "before": before})
        path.parent.mkdir(parents=True, exist_ok=True)
        after = (new if old == "" else before.replace(old, new, 1)).replace("\r\n", "\n")
        nl = "\n" if raw and b"\r\n" not in raw else "\r\n"  # new files match the corpus
        path.write_bytes(after.replace("\n", nl).encode("utf-8"))

    BACKUP.write_text(json.dumps(backup, indent=2, ensure_ascii=False) + "\n")
    print(f"\napplied {len(writes)} edit(s); previous contents saved to "
          f"{BACKUP.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
