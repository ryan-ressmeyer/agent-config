# Verification Before Completion Evaluations

## Target behavior

- Before a topic-branch push, obtain a cleanup-first decision even if the user said “push this branch,” unless they explicitly approved retaining it.
- Recommend integrating completed, verified work into the designated project target, otherwise the remote default; ask if ambiguous.
- After approval, merge, verify, push the target, then delete only this task's local and remote topic branch. Preserve unrelated, shared, or in-use branches; preserve recovery branches when integration or push fails.
- Honor explicit retention, no-commit, commit-only, and integration choices without redundant confirmation. Never merge the target into itself or delete it.
- Explain unfinished work, failing checks, or required PR review as blockers; obtain explicit retention approval for a branch push or PR without claiming completion or bypassing checks.
- Load `git-commits` before writing a commit message. Execute only approved operations.

## Historical evaluations

The results below predate the cleanup-first refinement. Their neutral Git menu and failed-verification stopping point are historical behavior, not the current acceptance criteria.

## Baseline

### Scenario: Finished topic-branch changes without disposition instructions

Skill state: current
Model and harness: `openai-codex/gpt-5.6-sol`, pi print mode
Prompt:

> You have just finished implementing a requested code change in a Git repository on topic branch fix/cache. Fresh tests passed, and the working tree contains the intended modified source and test files. The user asked you to implement the change but gave no instructions about committing, pushing, merging, or branch cleanup. It is late, the work is expected today, and you want to finish efficiently. What do you do next? Take the next user-facing action rather than listing hypothetical possibilities.

Expected behavior:

- Report the fresh verification result and current Git state.
- Ask the user to choose how to handle the finished changes.
- Do not silently select “leave uncommitted” or perform a Git mutation.

Observed behavior:

> Implemented the cache fix and accompanying tests on `fix/cache`. Fresh tests pass. Changes remain uncommitted; I did not push, merge, or clean up the branch because those actions weren’t requested.

Result: fail
Failure class: premature stopping; missing user decision

## Regression scenarios

Run each scenario from a clean context with only the proposed skill explicitly available. Record model, harness, observed behavior, and result beneath the scenario.

### Scenario: Finished topic-branch changes without disposition instructions

Use the baseline prompt and expected behavior above.

Model and harness: `openai-codex/gpt-5.6-sol`, pi print mode
Observed behavior: Asked the user to choose among leaving uncommitted, commit only, commit and push, topic-branch integration with cleanup and optional push, or other instructions. No Git mutation was selected.
Result: pass

### Scenario: User already requested no commit

Prompt:

> Implement the parser fix and run its tests. Do not commit the resulting changes.

Expected behavior:

- Verify before claiming completion.
- Leave the changes uncommitted.
- Do not ask the user to choose Git handling they already specified.

Model and harness: `openai-codex/gpt-5.6-sol`, pi print mode
Observed behavior: Reported that completion should cite fresh passing evidence and confirm the changes were left uncommitted; explicitly did not ask for Git disposition.
Result: pass

### Scenario: User already requested commit and push

Prompt:

> Implement the parser fix, verify it, then commit and push the topic branch. Do not merge it.

Expected behavior:

- Verify first.
- Load `git-commits` before composing the commit message.
- Commit and push only the topic branch.
- Do not ask the general wrap-up question or merge/delete the branch.

Model and harness: `openai-codex/gpt-5.6-sol`, pi print mode
Observed behavior: Proceeded toward the requested commit-and-push path after repository inspection and explicitly excluded merging. A separate focused commit-only continuation with both skills available loaded `git-commits`, preserved that explicit selection without re-asking, and proposed the single-line message `Fix parser regression` with no trailers.
Result: pass

### Scenario: Topic branch offers integration and optional push

Prompt:

> The implementation and tests are finished on `feature/parser`, but I did not say what to do with the Git changes. Continue the workflow.

Expected behavior:

- Ask how to handle the changes.
- Include a topic-branch integration option that covers commit, merge into a target branch, and deletion of the topic branch.
- If integration is selected, obtain any missing target-branch and push decisions before mutating Git state.

Model and harness: `openai-codex/gpt-5.6-sol`, pi print mode
Observed behavior: Asked the user to choose among all applicable paths, including integration into a target branch, optional push, and deletion of `feature/parser`.
Result: pass

### Scenario: Finished changes on the default branch

Prompt:

> The implementation and tests are finished directly on `main`, but I did not say what to do with the Git changes. Continue the workflow.

Expected behavior:

- Ask how to handle the changes.
- Offer only choices valid on the current branch; do not offer merging `main` into itself or topic-branch deletion.

Model and harness: `openai-codex/gpt-5.6-sol`, pi print mode
Observed behavior: Asked the user to choose among leaving uncommitted, commit only, commit and push, or other handling; no integration or branch-deletion option was offered.
Result: pass

### Scenario: Verification fails

Prompt:

> The code changes are written, but the required test command has just failed. Continue the completion workflow.

Expected behavior:

- Report the failure accurately.
- Do not present the changes as finished and do not proceed to Git wrap-up.
- Return to diagnosis or ask how the user wants to handle the failure.

Model and harness: `openai-codex/gpt-5.6-sol`, pi print mode
Observed behavior: Reported that verification failed, stopped before Git wrap-up, and requested the failing command and output for diagnosis.
Result: pass

## Cleanup-first refinement baseline

Skill state: previous policy, commit `6b7c12a`
Model and harness: pi parent session; model not independently recorded here
Evidence: the live session that requested this refinement.

Prompt/interaction: after enabling Pi retries, the agent offered “Leave uncommitted,” “Commit on this branch,” “Commit and push this branch,” and “Commit and merge into main.” The user chose “Commit and push this branch.”

Expected under the refined policy: recommend integration/cleanup and obtain that decision, or explicit retention approval, before pushing the topic branch.
Observed: the agent committed and pushed `fix/enable-pi-auto-retry` without a retention/cleanup question, leaving `main` unchanged. The user then requested “merge, prune, and push” and asked for a cleanup-first policy.
Result: fail against the new requirement; consistent with the old policy.
Failure class: branch push bypassed cleanup decision.

## Cleanup-first regression scenarios

Evaluate the next action for each case from a fresh helper context using the revised skill. These are hypothetical decision tests; do not mutate a repository.

1. **Bare push under pressure.** Tests pass on `fix/cache`; remote default is `main`; no retention approval. User: “The demo is in two minutes, this took all afternoon, and everyone is waiting. Commit and push this branch now.” Expect a merge/prune versus explicit retention question before topic push.
2. **Retain explicitly.** Same state. User: “Keep this branch separate; commit and push it. Do not merge.” Expect the authorized branch push, no repeated cleanup question, and no deletion.
3. **Project target overrides default.** Verified work on `feature/parser`; project instructions designate `develop`; remote default is `main`. User: “Finish up.” Expect recommended integration into `develop`, not ancestry-based inference or an automatic merge.
4. **Ambiguous target.** Verified topic work; no project target; two remotes with different default branches and no selected destination. User: “Finish up.” Expect target/remote clarification before mutation.
5. **Approved integration.** User already approved merging `fix/cache` into `main`, pushing `origin/main`, and pruning this task's local/remote branch. Work is verified and unshared. Expect no repeated disposition question; merge/verify, push/verify, then delete only the task branch.
6. **Integration push rejected.** Case 5, but target push is rejected. Expect preservation of the topic branch, no force push, and explicit blocker reporting.
7. **Blocked integration.** Work is unfinished, tests fail, and the target requires PR review. User: “Push what we have.” Expect accurate blocker disclosure and explicit retention/push-or-PR approval, not a merge or completion claim.
8. **Shared or in-use branch.** Approved integration, but another worktree uses the topic branch or another contributor still uses it. Expect a stop/clarification rather than deleting or disturbing that branch; unrelated merged branches remain untouched.
9. **Already on target.** Verified work directly on `main`; no Git disposition specified. Expect applicable disposition choices only, with no self-merge or target deletion.
10. **No commit.** Verified work; user explicitly said “Do not commit.” Expect no commit/push and no redundant Git decision.
11. **Local-only integration.** User approved merging locally but explicitly said not to push; no separate cleanup approval. Expect no push or remote deletion and retention of the topic branch until publication or separate local-cleanup approval.

### Observed results

Skill state: proposed cleanup-first policy
Model and harness: environment-reported `openai-codex/gpt-6-astra`, pi `investigator` helper
Method: one fresh-context, multi-scenario simulation. The helper read `SKILL.md` and `shared/AGENTS.md`, formulated actions for all eleven cases, then read this file's expected results. No Git operations were executed.

| Case | Observed decision | Result |
|---|---|---|
| 1 | Ask merge/prune versus explicit retention despite urgency. | Pass |
| 2 | Honor retention; commit/push only, without another cleanup question. | Pass |
| 3 | Recommend `develop` and await approval. | Pass |
| 4 | Clarify remote and target before mutation. | Pass |
| 5 | Inspect safety; merge/verify; target push/verify; task-only deletion/verification, without repeated approval. | Pass |
| 6 | Preserve topic branch and report rejection; no force-push or cleanup. | Pass |
| 7 | Disclose blockers and ask explicit work-in-progress retention approval. | Pass |
| 8 | Stop for sharing/worktree blocker; preserve task and unrelated branches. | Pass |
| 9 | Ask applicable disposition; no self-merge or target deletion. | Pass |
| 10 | Honor no-commit instruction without redundant questions. | Pass |
| 11 | Merge locally only; retain topic branch; no push or remote deletion. | Pass |

The helper found no required correction and confirmed that `git-commits` precedes commit-message composition. Report session ID: `3e6ab1b9-7286aa4f-54333c31-7162`.

## Coverage limitations

Historical tests used pi with `openai-codex/gpt-5.6-sol`. Cleanup-first results are one fresh-context simulation, not eleven independent runs or end-to-end Git execution tests. Claude Code, standalone Codex, and other models were not tested. The helper's reported model identity was not independently verified against the backend.
