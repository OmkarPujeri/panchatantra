"""Apply the certification-defect fixes that survived adversarial verification.

Reads data/review_2026-10-13_certfix_workflow.json -> doc["confirmedEdits"].
Each edit: {story, file, old, new, rationale, source_quote, authored_not_sourced?}

Same guards as apply_content_fixes.py, which this deliberately mirrors:

  * the target is the DECLARED file, resolved exactly — not globbed by story,
    because these edits already know their exact path;
  * "already applied" is tested FIRST (append-style edits have `new` containing
    `old`; testing `old` first would re-fire forever);
  * every `old` must be present or the run refuses to write anything;
  * CRLF is preserved — 125 of the 147 corpus files are CRLF and Path.write_text()
    would silently rewrite them all as LF, making every line look changed.

    python3 scripts/apply_triple_fixes.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / "data" / "review_2026-10-13_certfix_workflow.json"
BACKUP = ROOT / "data" / "apply_triple_fixes_backup.json"


def plan(edit: dict):
    """Return (status, path, why). status in write|skip|fail."""
    old, new = edit["old"], edit["new"]
    path = ROOT / edit["file"]

    if old == "":  # whole-file replacement
        if path.exists() and path.read_text(encoding="utf-8") == new:
            return ("skip", path, "already applied")
        return ("write", path, None)

    if not path.exists():
        return ("fail", None, f"file missing: {edit['file']}")

    body = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
    # Test `old` FIRST. The census-fix script tested `new` first because its edits
    # were append-style (`new` contains `old`); here one edit (PT083) is a DELETION
    # (`new` is a substring of `old`), so testing `new` first would report the
    # un-applied edit as "already applied" — a skip that looks like success.
    # ponytail: PT037 is append-style, so a *re-run* would re-apply it; this runs once.
    if old in body:
        return ("write", path, None)
    if new in body:
        return ("skip", path, "already applied")
    return ("fail", None, f"`old` not found in {edit['file']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--workflow", default=str(WORKFLOW), help="JSON with confirmedEdits[]")
    ap.add_argument("--backup", default=str(BACKUP), help="where to save the before-state")
    args = ap.parse_args()
    workflow, backup_path = Path(args.workflow), Path(args.backup)

    doc = json.loads(workflow.read_text())
    edits = doc["confirmedEdits"]

    planned, failures = [], []
    for e in edits:
        r = plan(e)
        (failures if r[0] == "fail" else planned).append((e, r))

    for e, (status, _path, why) in planned:
        tag = "SKIP   " if status == "skip" else ("AUTHORS" if e.get("authored_not_sourced") else "APPLY  ")
        print(f"  {tag} {e.get('story', ''):7} {e['file']:60} {why or ''}")
    for e, r in failures:
        print(f"  FAIL   {e.get('story', ''):7} {e['file']:60} {r[2]}")

    if failures:
        print(f"\n{len(failures)} edit(s) could not be placed — refusing to write anything.")
        return 1

    writes = [(e, r) for e, r in planned if r[0] == "write"]
    if args.dry_run:
        print(f"\ndry run: {len(writes)} write(s), {len(planned) - len(writes)} already "
              f"applied — nothing written")
        return 0

    backup = []
    for e, (_status, path, _why) in writes:
        raw = path.read_bytes()
        before = raw.decode("utf-8").replace("\r\n", "\n")
        backup.append({"file": str(path.relative_to(ROOT)), "before": before})
        after = e["new"] if e["old"] == "" else before.replace(e["old"], e["new"], 1)
        nl = "\r\n" if raw and b"\r\n" in raw else "\n"
        path.write_bytes(after.replace("\n", nl).encode("utf-8"))

    backup_path.write_text(json.dumps(backup, indent=2, ensure_ascii=False) + "\n")
    print(f"\napplied {len(writes)} edit(s); previous contents saved to "
          f"{backup_path.resolve().relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
