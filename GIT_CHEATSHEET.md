# Git cheat sheet — Panchatantra

Copy-paste commands for this repo. A `.git` directory exists (re-initialised by the
user on 2026-10-13) but there are **zero commits** as of 2026-10-13. If `.git` is
already present, skip the `git init` line in §1 and go straight to `git add -A`.

> **The path has a space in it.** Every `cd` below is quoted for that reason. If you
> drop the quotes you get `no such file or directory`.

---

## 1. First-time setup — run once

`.git` already exists (re-initialised by the user) and `.gitignore` already exists
(§2), so there is no file to create and no `git init` to run. Just configure once:

```bash
cd "/Users/omkarpujeri/Desktop/Projects/panchatantra story"

git config core.autocrlf false      # keep the 125 CRLF corpus files as-is (§6a)

# identify yourself for these commits only (not global)
git config user.name "Omkar Pujeri"
git config user.email "your@email.com"
```

## 1a. The commit chain — copy-paste, in order

Five commits, grouped by subsystem so the history reads cleanly. Each `git add`
covers a different top-level group; together they add **every** file (verified —
317 of 317, nothing left over).

```bash
cd "/Users/omkarpujeri/Desktop/Projects/panchatantra story"

# 1 — project docs + config
git add .gitignore *.md *.pdf
git commit -m "docs: project context, handover, worklog, adaptation brief, tagging schema"

# 2 — the ingestion + build pipeline
git add scripts/ source/
git commit -m "feat(pipeline): Wikisource ingest -> corpus build -> integrity checks"

# 3 — the corpus: source records + adapted tellings
git add corpus/
git commit -m "feat(corpus): 90 source records, 145 adapted tellings (63x 4-9, 82x 9+), page-verified"

# 4 — the adaptive engine
git add engine/
git commit -m "feat(engine): adaptive storytelling engine v0 (select, state, update)"

# 5 — curation, authored sources, review artifacts
git add data/
git commit -m "chore(data): curation, authored tag/item sources, review fan-out artifacts"
```

Confirm a clean tree — only ignored files should remain:

```bash
git log --oneline      # 5 commits, newest first
git status             # clean — the scan, caches and aiml/ are ignored
```

> **Prefer one commit?** Skip the chain and run
> `git add -A && git commit -m "import: Panchatantra corpus, engine and docs"`.
> The chain is only for a readable history — nothing depends on the split.

---

## 2. The `.gitignore` — already in place

Already committed at the repo root, so nothing to create. It keeps out the render
caches, scratch/OS files, the 41MB scan and the `aiml/` submission material:

```gitignore
# render caches — safe to delete (HANDOVER §2)
source/fullbook/
source/rendered/

# scratch / OS / tooling
.DS_Store
.playwright-mcp/
__pycache__/
*.pyc

# college submission material — not part of the corpus product
aiml/

# the original Ryder 1925 scan — 41MB, read by NO script (the pipeline uses pages_raw.json,
# which is committed); public domain, re-fetchable from Wikimedia Commons
# (commons.wikimedia.org/wiki/File:Panchatantra.djvu). Kept out to keep the repo ~11MB.
source/Panchatantra_ryder_1925.djvu
```

---

## 3. Every day after that

```bash
cd "/Users/omkarpujeri/Desktop/Projects/panchatantra story"

git status                 # what changed
git diff                   # the actual changes, line by line
git add -A
git commit -m "what you did"
```

**Always run `git diff` before `git add -A`.** See §5 — three separate rewrites in
this project looked fine and were wrong; the diff is the only thing that catches them.

To commit only some files:

```bash
git add corpus/age/9+/PT010-how-the-crow-hen-killed-the-black-snake.txt
git commit -m "fix PT010 ending"
```

---

## 4. Pushing to GitHub (optional)

Create an empty repo on GitHub first — **do not** let it add a README or .gitignore,
that causes a conflict. Then:

```bash
cd "/Users/omkarpujeri/Desktop/Projects/panchatantra story"
git branch -M main
git remote add origin https://github.com/YOUR-USER/YOUR-REPO.git
git push -u origin main
```

The repo is now **~11MB** — `source/Panchatantra_ryder_1925.djvu` (41MB, the scan) and
`aiml/` (7.7MB, college-submission material) are both in `.gitignore`. The scan is read by
no script (the pipeline uses `source/pages_raw.json`, which is committed) and is public
domain from Wikimedia Commons, so leaving it out is safe. To include it anyway, delete the
`source/Panchatantra_ryder_1925.djvu` line from `.gitignore` before the first commit.

---

## 5. Undo commands

```bash
git checkout -- <file>        # throw away uncommitted changes to one file
git checkout -- .             # throw away ALL uncommitted changes  ⚠ permanent
git reset --soft HEAD~1       # undo last commit, keep the changes staged
git reset --hard HEAD~1       # undo last commit AND the changes  ⚠ permanent
git revert <commit>           # make a new commit that undoes an old one (safe)
```

`git revert` is the safe one — it does not rewrite history.

---

## 6. Three project-specific warnings

**a) Line endings.** 125 of the 147 files in `corpus/age/` use CRLF. `core.autocrlf
false` in §1 stops git touching them. If you ever see a diff where *every* line
changed but the content looks identical, that is this — stop and check before
committing.

**b) Do not reformat generated JSON.** `corpus/bands/*.json` and `data/curation.json`
are written with **1-space** indent; `panchatantra_adapted.json`, `story_tags.json`
and `story_items.json` come out of the project's own scripts. Rewriting any of them
with a different indent turns a one-line change into a 3,000-line diff. If you edit
one by hand or with a script, match its existing formatting.

**c) Read the diff.** Every automated check in this project has been wrong at least
once. In one session four separate writes reported success while being wrong — a
stale manifest, a CRLF-to-LF conversion, a shell loop that printed `ALL CHECKS GREEN`
without executing anything, and the indent reformat above. `git diff` is the check
that caught all of them.

---

## 7. Useful read-only commands

```bash
git log --oneline                 # commit list, newest first
git log --stat --oneline          # with the files each commit touched
git show <commit>                 # one commit in full
git diff <commit>                 # current state vs that commit
git diff --stat                   # just the file names and line counts
git ls-files                      # everything git is tracking
git status --short                # compact status
```

---

## 8. If something goes badly wrong

```bash
git reflog                        # every position HEAD has been at, last ~90 days
git reset --hard <hash>           # go back to one of them
```

`git reflog` is the safety net when you have committed something you should not
have. It only works for things git has actually seen — it cannot recover a file
that was never added.
