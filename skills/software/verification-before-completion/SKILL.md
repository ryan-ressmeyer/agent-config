---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, or when deciding Git disposition, committing, pushing, merging, creating a PR, or deleting a branch
---

# Verification Before Completion

## Overview

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim
6. HAND OFF: If code changes are finished, follow the Git wrap-up decision below

Skip any step = lying, not verifying
```

## Git Wrap-Up Decision

Fresh verification establishes whether changes are ready; it does not authorize a Git workflow. Use this decision both at task completion and before a topic-branch push, including a requested work-in-progress push.

### 1. Establish the target and readiness

Inspect the current branch, working tree, remotes, and worktrees. Use the user's named or project-documented integration branch; otherwise use the remote's default branch. Ask if the target or remote is ambiguous. Do not infer the target from branch ancestry or assume it is named `main`.

Recommend integration only for completed, verified work. If work is unfinished, checks fail, or branch protection or required PR review blocks direct integration, explain the blocker and ask whether to retain the branch for a push or PR instead. Do not bypass checks or review requirements, or describe an approved work-in-progress push as verified completion.

**Complete when:** the integration target and remote are established or flagged for clarification, and readiness or the specific integration blocker is known.

### 2. Obtain a cleanup-first decision

For a finished topic branch, recommend **commit if needed → merge into the named integration branch → push that target → delete this task's local and remote topic branch**. Ask using a structured user-question tool when available. Alternatives may include leaving changes uncommitted, committing only, or explicitly retaining the topic branch for a push or PR. On the integration branch itself, offer only applicable choices; never propose merging it into itself or deleting it.

A request to “push” or “commit and push this branch” alone still requires the merge-and-prune question before a topic-branch push. Skip that question only when the user has explicitly approved retaining the branch, such as “keep this branch,” “do not merge,” or a confirmed PR workflow. Ask for retention approval before treating a new PR request as permission to skip the cleanup decision.

Honor explicit choices to leave uncommitted, commit only, retain the branch, or integrate and prune. One approval covers the specified workflow; ask only for missing details or new blockers, not the same decision again. Do not silently leave changes uncommitted as a substitute for asking when no disposition was specified.

**Complete when:** the user has selected a valid disposition, including explicit branch retention for a topic-branch push or approval of the named integration/cleanup workflow, and any missing target or push details are resolved.

### 3. Execute and verify the selected path

Load `git-commits` before composing a commit message. Perform only the approved operations. For integration and cleanup:

1. Verify that the topic branch contains only the intended work and is not shared or in use by another worktree. Stop and ask if either condition prevents safe integration or deletion; preserve unrelated branches.
2. Merge into the approved target and verify the integrated result. Stop on conflicts or failed verification rather than forcing integration.
3. Push the target and verify the remote contains the integrated commits. If the push fails, preserve the topic branch for recovery; do not force-push to bypass rejection.
4. Only after successful integration and target push, delete this task's local and remote topic branch if they exist. Verify their removal and report any incomplete cleanup. Never use this approval to prune unrelated branches.

An explicitly approved local-only merge does not authorize a push or remote deletion; retain the topic branch until the target is published unless the user separately approves local-only cleanup.

**Complete when:** all approved operations and their verification are accounted for, any failed or blocked operation is reported with recoverable work preserved, and no unselected operation or unrelated branch cleanup has occurred.

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!", etc.)
- About to commit/push/PR without verification
- Trusting agent success reports
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (TDD Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## Why This Matters

From 24 failure memories:
- your human partner said "I don't believe you" - trust broken
- Undefined functions shipped - would crash
- Missing requirements shipped - incomplete features
- Time wasted on false completion → redirect → rework
- Violates: "Honesty is a core value. If you lie, you'll be replaced."

## When To Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction
- ANY positive statement about work state
- Committing, PR creation, task completion
- Moving to next task
- Delegating to agents

**Rule applies to:**
- Exact phrases
- Paraphrases and synonyms
- Implications of success
- ANY communication suggesting completion/correctness

## The Bottom Line

**No shortcuts for verification.**

Run the command. Read the output. THEN claim the result.

This is non-negotiable.
