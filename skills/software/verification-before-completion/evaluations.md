# Verification Before Completion Evaluations

## Target behavior

After fresh verification establishes the actual state of completed code changes:

- If the user has not specified Git handling, ask them to choose before committing, pushing, merging, or deleting branches.
- Offer choices appropriate to the repository state, including leaving changes uncommitted, commit only, commit and push, topic-branch integration and cleanup, and user-specified handling.
- Ask only for missing details after the user selects a path; do not repeat a choice already made explicitly.
- Execute only the selected path. Load `git-commits` before writing a commit message.
- Verification and its evidence must precede the wrap-up decision.

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

## Coverage limitations

The baseline was run only on pi with `openai-codex/gpt-5.6-sol`. Run proposed-skill regressions on additional supported models and Claude Code when practical; report unavailable harness/model coverage rather than generalizing.
