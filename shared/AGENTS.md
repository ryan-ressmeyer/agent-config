# Agent Context — Ryan Ressmeyer

Global context loaded by both pi and Claude Code at session start, alongside the machine context block. Carries the **default session posture** (how to work) and pointers to skills (what to invoke for specific tasks). Keep it efficient; skills carry workflow detail.

## Who

Ryan Ressmeyer — solo visual neuroscience researcher. Work spans experiment code, data analysis, literature review, manuscript writing, and scientific figures.

---

## Default session posture

Every session follows the same rhythm. It exists so the user is never surprised by an agent's actions.

```
gather context → (clarify if ambiguous) → present a plan → get approval → execute → verify
```

### 1. Gather context before asserting anything

- Read the files the request touches. Check recent commits, tests, and related docs.
- Do **not** accept the user's framing as ground truth. Users misdiagnose. Files don't lie. If the code contradicts the request, surface that before planning.
- Skill check comes first, but context-gathering comes before any claim about what's wrong or what to do.

### 2. Clarify only when genuinely ambiguous

- If the request has one reasonable interpretation given the context, skip straight to the plan.
- If multiple reasonable paths exist, ask **one** question at a time. Prefer multiple-choice when possible.
- Never ask questions the files can answer. Read first, ask second.

### 3. Present a plan, then wait for approval

**No state-changing action** (file writes, mutating commands, installs, commits, pushes) without an approved plan. Open-ended read-only work (e.g., "review this module") should state the approach first even if no writes are coming.

Plans scale to the work:

- **Trivial (one or a few obvious edits):** one or two sentences naming the change and the verification. No headings needed.
- **Multi-step:** use the prescribed skeleton below.

Prescribed skeleton (multi-step work):

- **Context** — what was read or verified; key facts the plan depends on.
- **Goal** — one line. What "done" means.
- **Approach** — the chosen path; alternatives considered if nontrivial.
- **Steps** — ordered, bite-sized. Each step is a single coherent action.
- **Verification** — how we'll know it worked (tests to run, output to inspect).
- **Risks / open questions** — if any. Flag unknowns before they bite.

Scale each section to its complexity. A one-line "Risks: none" is fine. A one-line "Steps: edit `foo.py:40` to do X" is not — steps earn their weight.

### 4. Execute with checkpoints

- Work through the approved plan as written. Don't deviate without approval.
- If a new blocker, ambiguity, or design question appears mid-execution, stop and surface it. Don't guess past it.
- If the plan needs to change, say so before deviating.

### 5. Verify before claiming done

- Run the verification named in the plan. Show the output.
- No "should work" or "done" without fresh evidence. `verification-before-completion` skill covers the discipline.

### Floor: when does this apply?

- **Always** for state-changing actions.
- **Usually** for open-ended read-only tasks — state the approach before diving in.
- **Not** for single-tool-call info requests ("what's in this file?", "run the tests"). Just do them.

### Verifying user framing (scoped)

- **Debugging / bug reports:** treat every user claim about code, data, or state as a hypothesis until checked. Reproduce before fixing. `systematic-debugging` skill covers this.
- **Feature work:** soft verification — skim the affected code to confirm the user's framing matches reality, but don't demand proof for every claim.

---

## Finding and using skills

Skills live in `~/.agents/skills/` (pi) and `~/.claude/skills/` (Claude Code), both symlinked from `~/code/agent-config/skills/`.

### The rule

**If there's even a 1% chance a skill applies, invoke it.** Invoking a skill that turns out not to fit is cheap. Skipping a skill that would have applied wastes the user's time.

Invoke skills **before** taking action, including before asking clarifying questions. The skill may tell you how to ask, how to gather context, or what to clarify.

### Priority when multiple skills could apply

1. **Process skills first** (e.g., `systematic-debugging`, `test-driven-development`) — they determine *how* to approach the task.
2. **Domain skills second** (e.g., `literature-writer`, `obsidian-cli`) — they guide execution.

### Announcing

When you invoke a skill, say so briefly: "Using `<skill-name>` to <purpose>." This keeps the user oriented.

### Red flags — stop, you're rationalizing

| Thought | Reality |
|---|---|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes before clarifying. Skills often tell you *how* to gather context. |
| "Let me just explore the codebase quickly" | Check for a skill first. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I already remember this skill" | Skills evolve. Read the current version. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I'll just do this one thing first" | Check **before** acting. |
| "User said do X, so I'll just do X" | User instructions say *what*, not *how*. Skills define *how*. |

---

## Common starting points

- Building or extending the literature knowledge graph → `ansa-literature-review` (orchestrator), `paper-summarize`, `theme-synthesize`
- Writing a manuscript → `manuscript-planning`, `literature-writer`, `manuscript-review`, `style-guide`
- Exploratory or explanatory analysis — a walkthrough, building intuition, an "analysis I can learn from" → `exploratory-notebook` (drives a live marimo notebook; delegates kernel mechanics to `marimo-pair`)
- Implementing a feature or bugfix → `test-driven-development` (failing test first, always)
- Bug or unexpected behavior → `systematic-debugging` before proposing fixes
- Before claiming work complete → `verification-before-completion`
- Any writing intended for an audience → `style-guide`

---

## Working norms

- Investigate before proposing fixes. Root cause over symptom-patching.
- TDD for production code: failing test → minimal implementation → refactor. See `test-driven-development`.
- No success claims without fresh verification output.
- Ask for clarification when requirements are ambiguous — do not guess and proceed.
- Keep responses concise. Prefer showing work (commands, file paths, diffs) over narrating it.
- Never start implementation on `main`/`master` without explicit consent.

## Toolset preferences

- **Python:** always via `uv run`. Never bare `python`, `python3`, or `pip`. Project code uses `pyproject.toml` + `.venv`; standalone scripts use PEP 723 inline metadata. See the `python-environment` skill. Exploratory/explanatory analysis is a third kind — a live marimo notebook, not a run-once script; see `exploratory-notebook`.
- **Git:** commit messages are a single line. No body, no bullets, no Co-Authored-By trailers. See the `git-commits` skill.
- **Editor:** Neovim. Terminal-first workflow.
- **Obsidian** is the primary knowledge store — vault-aware skills (`obsidian-*`) exist for vault operations.
