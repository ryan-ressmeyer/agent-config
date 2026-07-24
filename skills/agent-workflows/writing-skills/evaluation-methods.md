# Evaluation Methods

Read this reference before changing skill behavior.

## Evaluation cycle

1. **Define expected behavior:** Write observable outcomes for each relevant workflow path or retrieval situation.
2. **Run a baseline:** Test without the proposed skill or change and preserve the output.
3. **Classify failures:** Identify wrong action, premature stopping, missed retrieval, incorrect application, invented context, or deliberate shortcutting.
4. **Make the minimum change:** Add only instructions or context justified by the evidence.
5. **Run the same evaluations:** Compare changed behavior directly with baseline behavior.
6. **Add variations:** Test nearby prompts, missing information, edge cases, and intended models.
7. **Regress:** Preserve scenarios that exposed real failures and rerun them after later edits.

If the baseline already succeeds, make the scenario less leading or reconsider whether new content is needed.

## Choose the evaluation type

| Skill type | Primary evaluation | Evidence of success |
|---|---|---|
| **Workflow** | Execution, decision, branch, recovery, and completion scenarios | Correct actions in the correct order with valid stopping conditions |
| **Reference** | Invocation, retrieval, application, and gap scenarios | Relevant context loaded and applied accurately without invented or irrelevant material |

A router uses workflow evaluations. A workflow that calls a script also tests the script with fixtures and output validation. A workflow containing rules agents may evade adds realistic pressure scenarios.

## Workflow evaluations

Test:

- whether explicit commands or autonomous triggers start the workflow as intended;
- correct action and decision order;
- important branches and recovery paths;
- behavior when required information is missing;
- observable and exhaustive completion criteria;
- exclusions that should not start the workflow.

For user-invoked workflows, verify the explicit command works and the workflow does not consume model context when inactive. For model-invoked workflows, test trigger and false-activation prompts.

## Reference evaluations

Test:

- whether relevant questions and artifacts invoke the reference autonomously;
- whether the agent retrieves the correct fact or concept;
- whether it applies that context accurately;
- whether adjacent but irrelevant questions avoid unnecessary retrieval;
- whether missing information is recognized rather than invented;
- whether large references load only the relevant material.

Do not test a reference as though it were a workflow. It needs no artificial sequence or completion criteria.

## Scenario record

For each scenario record:

```markdown
### Scenario: [name]
Skill state: absent | current | proposed
Model and harness: [identifier]
Prompt: [exact prompt]
Expected behavior:
- [observable action or retrieval outcome]
Observed behavior:
- [decision, output, and files loaded]
Result: pass | fail
Failure class: [if failed]
```

Keep prompts realistic and avoid naming the behavior being tested unless normal users would do so. A prompt that explicitly requests a reference-only structure cannot establish that the skill prevents manufactured workflow under natural prompting.

## Pressure scenarios

Use pressure only for workflow rules agents have an incentive to evade. Combine realistic incentives such as time, authority, sunk cost, exhaustion, or social friction. Require a concrete decision or action and capture rationalizations verbatim.

Read [discipline-workflows.md](discipline-workflows.md) directly from `SKILL.md` when pressure testing applies.

## Mechanical changes

A behavioral baseline is unnecessary only when all of these are true:

- the change is mechanical;
- trigger language and retrieval terms are unaffected;
- meaning and execution are unchanged;
- navigation and file structure are unchanged;
- focused structural checks can prove the correction.

Record those checks and inspect the diff. If any condition is uncertain, run a narrow behavioral regression.

## Models and clean contexts

Test every model and harness intended to use the skill when practical. At minimum, test the least capable supported model and the primary production model. Use fresh contexts so conversation history does not supply missing instructions.

When access to a model or harness is unavailable, report the limitation rather than generalizing from another model.

## Completion standard

Evaluation is complete when:

- every required workflow path or retrieval situation has a recorded result;
- original failures pass with the changed skill;
- important variations and exclusions pass;
- observed regressions remain in the evaluation set;
- intended models pass or untested models are explicitly reported;
- each use loads no irrelevant reference material.
