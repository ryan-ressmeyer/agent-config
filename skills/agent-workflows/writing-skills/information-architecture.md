# Information Architecture

Read this reference for every new skill or structural edit.

## Two skill types

| Type | Purpose | Invocation |
|---|---|---|
| **Workflow** | Directs actions or decisions. Routers are simple workflows. May load references or call scripts. | Often user-invoked for deliberate commands; model-invoked when it must start autonomously. |
| **Reference** | Supplies facts, concepts, conventions, or usage guidance when relevant. Need not contain steps. | Always model-invoked so the agent can retrieve it when useful. |

Scripts and pi extensions are executable resources, not additional skill types. A workflow that includes descriptive context remains a workflow.

## Invocation

A model-invoked skill contributes its description to context on every turn. A user-invoked skill saves that context but requires the user to remember and explicitly run it.

Use user invocation for workflows that represent deliberate commands and do not need autonomous discovery. In pi, set `disable-model-invocation: true`; confirm support in every target harness. Keep a workflow model-invoked when safety, diagnosis, or another process depends on it starting autonomously.

Keep every reference model-invoked. Its value depends on the agent recognizing when the context is relevant without the user naming the skill.

In this repository, use `disable-model-invocation: true` only for user-invoked workflows. Omit it from references and workflows that require autonomous discovery; keep `writing-skills` model-invoked.

## Frontmatter and descriptions

Use a lowercase, hyphenated name of at most 64 characters. Keep the description specific, third-person, and within 1024 characters.

For a model-invoked workflow, describe the situations that should start it. For a reference, describe the questions, concepts, artifacts, and terminology that should retrieve it. Do not summarize a workflow in the description: agents may execute the summary instead of loading the body. Collapse synonyms that describe the same trigger.

A user-invoked workflow still needs a valid description for harness validation, but it can be a concise human-facing summary.

## Workflow architecture

Match the degree of freedom to the cost of deviation:

- **High freedom:** prose heuristics when several approaches are safe.
- **Medium freedom:** templates, pseudocode, or parameterized scripts when a preferred pattern allows variation.
- **Low freedom:** exact commands and strict sequences when deviation is fragile or expensive.

Keep ordered actions, decisions, recovery paths, and stopping conditions on the execution path. End every procedural step with an observable and exhaustive completion criterion.

A router is a workflow whose action is selecting another skill or reference. Its completion criterion identifies the selected target and the evidence supporting that choice.

## Reference architecture

Organize a reference around retrieval rather than sequence:

- questions and situations that should load it;
- stable terminology and lookup keys;
- definitions, facts, conventions, and usage guidance;
- examples that clarify application;
- explicit limits and unknowns.

A reference may be entirely flat material in `SKILL.md`. It does not need steps, branches, or completion criteria. Add procedure only when the skill truly directs an action; if action becomes its primary purpose, classify it as a workflow.

Move large or condition-specific material to a directly linked file. The pointer must state when the agent needs that file. Evaluate whether relevant context is retrieved without loading unrelated material.

## Shared information hierarchy

Place information according to when the agent needs it:

1. **Main skill:** type, invocation, navigation, and material needed on most uses.
2. **External reference:** conditional or extensive context loaded through a direct pointer.
3. **Executable resource:** deterministic behavior the workflow should run rather than regenerate.

Keep references one level deep from `SKILL.md` and give long references a contents list. Co-locate each concept's definition, rules, limits, and examples. One meaning should have one authoritative home.

## When to split

Split only when the boundary changes what context a run carries:

- **By invocation:** a distinct trigger must independently reach a model-invoked skill, or a deliberate workflow should carry no persistent context.
- **By retrieval domain:** reference material serves distinct questions that should not load together.
- **By workflow branch:** different paths need substantially different instructions.
- **By sequence:** later workflow steps cause observed premature completion of the current step.

Do not split merely to shorten a file if every use still needs both halves.

## Pruning

Review each sentence:

1. Does it change action or supply context the model lacks?
2. Is this meaning already stated elsewhere?
3. Is it relevant to a live workflow path or retrieval question?
4. Could a stable term express it without losing requirements?

Delete no-ops, duplication, and stale guidance. Move live conditional detail behind a pointer. Do not compress several independent requirements into an evocative word unless evaluations show that it preserves them.

## Common structural failures

- **Manufactured workflow:** a reference is burdened with unnecessary steps or completion gates.
- **Hidden context:** a reference is user-only and cannot be retrieved when relevant.
- **Premature completion:** sharpen the current workflow step's criterion before splitting its sequence.
- **Duplication:** choose one authoritative location and point to it.
- **Sprawl:** move conditional reference out of the main path or split genuine retrieval domains.
- **Over-templating:** require sections only when evaluations demonstrate their value.
