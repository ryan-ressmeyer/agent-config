---
name: exploratory-notebook
description: >-
  Use when a task calls for exploratory or explanatory data analysis — building
  intuition step by step, a walkthrough or demonstration, an "analysis I can
  learn from", or explaining what an analysis actually does — rather than
  reusable infrastructure or a run-once compute script. Also use when about to
  reach for a batch script to walk someone through an analysis.
---

# Exploratory Notebook

## Overview

The analysis **is** the deliverable, and you prove and explain it by running it
in a shared live marimo kernel the user watches — so their understanding is a
byproduct of the workflow, not an act of faith.

This exists to defeat one specific trap: **"the output looks right, so I trust
code I never read."** A clean figure is produced by correct code *and* by
several silent bugs (unit errors, pooling/pseudoreplication, a categorical
x-axis that reorders points). Looking right ≠ being right. The defense is not
you verifying harder — it is the user engaging with real, rendered output as it
is built.

**REQUIRED SUB-SKILL:** Use `marimo-pair` for all kernel mechanics (connect,
scratchpad vs. committed cells, `cm` code-mode). This skill is the *policy*
layer on top of it. **REQUIRED:** `python-environment` (marimo runs via uv).

## When to use — the script taxonomy

| Kind | What it is | Tool |
|---|---|---|
| 1. Module | reusable infrastructure: functions, classes | plain `.py` module + TDD |
| 2. Heavy script | run-once compute: train, cache, render figure | `uv run` script + TDD |
| **3. Exploratory** | **walkthrough / intuition / demonstration / "learn from it"** | **this skill → marimo notebook** |

Use this skill for **type 3**. If the ask is really type 1 or 2, do that
instead. When a type-3 exploration crystallizes into reusable infra or heavy
compute, **graduate** it: extract the code into a module/script and apply
`test-driven-development`. The notebook stays the explanation; the extracted
code gets tests.

## Start of session (before writing any cell)

**1. Negotiate the mode.** Ask how they want to work — do not assume:

- **Shared walkthrough** (default): you build cells in the live notebook,
  pausing at checkpoints for them to read and react.
- **Human-driven**: you propose cells; they run the load-bearing ones
  themselves.
- **Show-don't-tell only**: you build with real rendered outputs and narration,
  no hard gates.

Also offer: a **walkthrough-after** (build first, then narrate) is available if
they ask for it.

**2. Launch marimo.** Local:

```bash
marimo edit notebook.py --sandbox   # --sandbox: PEP 723 inline deps
```

**Remote (SSH tunnel — the safe path):**

```bash
# on the remote machine:
marimo edit notebook.py --headless --no-token --sandbox
# on your laptop:
ssh -L 2718:localhost:2718 you@remote
# then open http://localhost:2718 locally BEFORE driving cells —
# the session is not active until a browser connects.
```

`--no-token` is safe **only** because marimo stays on loopback and only the
authenticated tunnel reaches it. **Never** `--host 0.0.0.0 --no-token` (that is
an open kernel = remote code execution). For a tailnet, bind `0.0.0.0` **with**
a token instead. See `marimo-pair` for connection/auth detail.

## The discipline (the heart)

- **Checkpoint gates (default backbone).** Build 1–3 cells, then **STOP**. Do
  not continue until the user responds. Never batch a whole analysis top to
  bottom.
- **Show, don't tell.** Render results in the notebook (plots, `mo.ui.table`,
  `mo.md`). **Never substitute a chat prose summary for an output the notebook
  can show.** Typing "p ≈ 1.8e-12" into chat instead of a rendered cell is
  contraband.
- **Explanation lives in the notebook**, as `mo.md` markdown cells — not the
  chat transcript. The committed `.py` must read top-to-bottom as the
  walkthrough on its own.
- **Human-runs-key-cells.** For load-bearing steps, hand the cell to the user
  to run themselves so engagement is hands-on.

## Done means reproducible

marimo's reactive DAG prevents most hidden-state rot, but before you call it
done: **restart the runtime and run all cells clean.** Use single-definition
naming (`clean = df.dropna()`, never `df = df.dropna()` — marimo rejects
redefinition; see `marimo-pair` gotchas).

## Rationalizations — STOP

| Excuse | Reality |
|---|---|
| "They're short on time — skip the gates" | Time pressure downgrades the *pacing*, never the discipline. Offer show-don't-tell mode, not zero engagement. If they truly want only a number, that is a type-2 script — say so, don't smuggle a hollow walkthrough. |
| "It's just scratchpad / read-only, no need to pause" | The goal is their understanding, not file safety. Read-only does not make skipped engagement OK. |
| "I'll just summarize the result in chat, it's faster" | A chat summary is the un-auditable claim they asked to escape. Render it in a cell. |
| "A run-once script explains it fine" | A batch script executed straight through is type-2 in disguise — they can't watch intuition build. Use the live notebook. |
| "The figure looks right, so the code is right" | Right-looking output is produced by silent bugs too. Looking right ≠ being right. |
| "I verified it myself, so we're done" | Agent-side verification is not the goal — the human learning is. Move the check into the surface they read. |

## Red flags

- About to write a full analysis before the user has seen a single cell
- About to type a numeric result or conclusion into chat instead of a cell
- Skipping the mode question because the task "seems obvious"
- Reaching for `uv run script.py` to walk someone through an analysis
- Saying "looks good, done" without a fresh restart-and-run-all

## Common mistakes

- **Editing the `.py` file directly during a live session** — marimo overwrites
  it from kernel state. Use `cm` (`marimo-pair`), not `Edit`/`Write`.
- **Reassigning a public name** (`df = df.dropna()`) — multiply-defined error.
- **Forgetting `--sandbox`** with a PEP 723 header — marimo ignores inline deps.
