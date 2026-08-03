---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, or when verified code changes need Git disposition before committing, pushing, merging, creating a PR, or deleting a branch
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

Fresh verification establishes whether changes are ready; it does not authorize a Git workflow. After successful verification, inspect the current branch, working tree, and remotes, then determine whether the user already specified how to handle the finished changes.

### 1. Honor an existing choice

If the user already gave explicit instructions for the current changes—such as leaving them uncommitted, committing only, pushing, opening a PR, or integrating and cleaning up a topic branch—follow that choice without asking the general wrap-up question again. Ask only for details required to execute it safely, such as a missing target branch or whether to push after integration.

**Complete when:** the user's existing choice and every still-missing execution detail are identified, or the workflow has established that no choice was provided.

### 2. Ask when no choice was provided

Use a structured user-question tool when available; otherwise ask directly. Present only options valid for the current repository state. Include the applicable choices among:

- Leave changes uncommitted
- Commit only
- Commit and push
- Commit, merge into a target branch, delete the topic branch, and choose whether to push
- User-specified handling

Do not silently choose a conservative default and stop. Reporting “left uncommitted because committing was not requested” does not complete this decision—the user must be offered the choice. Do not commit, push, merge, create a PR, or delete a branch before the user selects that action.

**Complete when:** the user has explicitly selected how the finished changes should be handled.

### 3. Execute only the selected path

Obtain any missing details for the selected path one decision at a time, then perform exactly that Git workflow. Load `git-commits` before composing any commit message. For topic-branch integration, confirm the target branch and whether the resulting target branch should be pushed before merging or deleting the topic branch.

**Complete when:** the selected operations have been executed and verified, or the changes remain uncommitted because that was the user's explicit selection; no unselected Git operation has occurred.

If verification fails, stop before this decision. Report the actual failure and return to diagnosis or ask the user how to proceed; unverified changes are not ready for Git wrap-up.

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
