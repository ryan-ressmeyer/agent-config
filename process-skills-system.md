# Process & Code Skills — Design Document

## Goal

A set of discipline-enforcing and workflow skills that govern how the agent approaches software engineering tasks: planning, implementing, debugging, testing, and verifying work. These skills apply across all projects and domains — they are not specific to scientific research.

## Skill Overview

```
Planning Pipeline (sequential):
  designing-plans → writing-plans → executing-plans

Code Quality (invoked as needed):
  test-driven-development
  systematic-debugging
  verification-before-completion

Infrastructure:
  python-environment
  dispatching-parallel-agents
  skills-prelude
  writing-skills
```

---

## Planning Pipeline

These three skills form a sequential pipeline: design the solution, write the implementation plan, execute the plan. Each phase gates the next — no skipping ahead.

### `designing-plans`

**Purpose:** Turn ideas into fully formed designs through collaborative dialogue before any implementation.

**When:** Before any open-ended request — creating features, building components, adding functionality, modifying behavior. Every project, regardless of perceived simplicity.

**Process:**
1. Explore project context (files, docs, recent commits)
2. Ask clarifying questions one at a time (prefer multiple choice)
3. Propose 2-3 approaches with trade-offs and a recommendation
4. Present design in sections, get user approval after each
5. Save design to `plans/YYYY-MM-DD-<topic>-design.md`
6. Hand off to `writing-plans`

**Key principles:** One question at a time. YAGNI ruthlessly. Explore alternatives before settling. No implementation until design is approved.

---

### `writing-plans`

**Purpose:** Convert an approved design into a detailed implementation plan with bite-sized tasks.

**When:** After a design/spec has been approved, before touching code.

**Process:** Write a comprehensive plan assuming the implementer has zero codebase context. Each task specifies: which files to touch, what code to write, how to test it. Plans follow DRY, YAGNI, and TDD principles.

---

### `executing-plans`

**Purpose:** Execute a written implementation plan with review checkpoints.

**When:** A written plan exists and needs to be implemented in a session.

**Process:** Load plan, review critically, execute tasks in batches, report for review between batches. Includes code review at stage gates.

---

## Code Quality Skills

These skills are invoked as needed during any implementation work. They enforce discipline that prevents common failure modes.

### `test-driven-development`

**Purpose:** Write the test first. Watch it fail. Write minimal code to pass.

**When:** Implementing any feature or bugfix, before writing implementation code.

**The iron law:** No code without a failing test first. Write code before the test? Delete it. Start over. No exceptions.

**Cycle:** RED (write failing test) → GREEN (minimal code to pass) → REFACTOR (clean up while tests stay green).

---

### `systematic-debugging`

**Purpose:** Diagnose bugs through structured investigation, not random fixes.

**When:** Encountering any bug, test failure, or unexpected behavior, before proposing fixes.

**Key insight:** Random fixes waste time and create new bugs. Quick patches mask underlying issues. Systematic debugging means: reproduce, isolate, understand root cause, then fix.

---

### `verification-before-completion`

**Purpose:** Run verification commands and confirm output before claiming work is done.

**When:** About to claim work is complete, fixed, or passing. Before committing or creating PRs.

**The rule:** Evidence before assertions. Run the tests. Read the output. Confirm it passes. Then — and only then — claim success.

---

## Infrastructure Skills

These skills support the others and manage the agent's environment and capabilities.

### `python-environment`

**Purpose:** Ensure all Python execution goes through `uv`, never bare `python`.

**When:** Before ANY Python script or command execution, including when invoked as part of another skill.

**The iron law:** NEVER use bare `python`, `python3`, or `pip`. ALL Python execution goes through `uv run`. Scripts use PEP 723 inline metadata for self-contained dependency management.

---

### `dispatching-parallel-agents`

**Purpose:** Run independent tasks in parallel using subagents.

**When:** Facing 2+ independent tasks with no shared state or sequential dependencies.

---

### `skills-prelude`

**Purpose:** Bootstrap skill discovery at conversation start.

**When:** Starting any conversation. Ensures relevant skills are invoked before any response.

**The rule:** If there is even a 1% chance a skill applies, invoke it.

---

### `writing-skills`

**Purpose:** Create, test, and deploy new skills using TDD methodology.

**When:** Creating new skills, editing existing skills, or verifying skills work before deployment.

**Key insight:** Writing skills IS TDD applied to process documentation. Same cycle: baseline test (RED) → write skill (GREEN) → close loopholes (REFACTOR).

---

## Dependency Graph

```
skills-prelude
└── (triggers all other skills as needed)

designing-plans
└── writing-plans
    └── executing-plans
        ├── test-driven-development
        ├── systematic-debugging
        ├── verification-before-completion
        ├── python-environment
        └── dispatching-parallel-agents

writing-skills
└── test-driven-development (required background)
```

## How These Connect to the Research System

The process skills are domain-agnostic — they apply to any engineering work. But they are especially important in the research system:

- **`manuscript-planning`** uses `python-environment`, `systematic-debugging`, and `test-driven-development` when writing and running analysis scripts
- **`designing-plans`** is the model for `manuscript-planning`'s collaborative dialogue pattern (one question at a time, explore before committing)
- **`verification-before-completion`** applies when running analyses — verify results before interpreting them
- **`writing-plans` / `executing-plans`** apply when building analysis pipelines that require multiple scripts or complex data processing

See `research-system.md` for the research-specific skill documentation.
