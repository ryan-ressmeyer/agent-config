---
name: writing-skills
description: Use when creating new skills, editing existing skills, or verifying skills before deployment
---

# Writing Skills

A skill makes either **action** or **retrieval** predictable. A workflow skill guides what the agent does; a reference skill supplies context the agent should find and apply on demand.

Develop skills from observed behavior. Establish a baseline, make the smallest justified change, and verify that the change improves the target behavior.

## Load the relevant guidance

- For every new skill or structural edit, read [information-architecture.md](information-architecture.md).
- Before any behavioral change, read [evaluation-methods.md](evaluation-methods.md) and define the evaluation before editing.
- When a workflow contains rules agents may resist, shortcut, or rationalize away, also read [discipline-workflows.md](discipline-workflows.md).
- When a workflow calls scripts, validators, or other executable resources, also read [executable-resources.md](executable-resources.md).

Read only the references that these conditions select. Each linked file is the direct, authoritative source for its concern.

## Choose the skill type

- **Workflow:** directs actions or decisions. A router is a simple workflow. Workflows are often user-invoked when they represent deliberate commands, but must be model-invoked when they should start autonomously.
- **Reference:** supplies facts, concepts, conventions, or usage guidance without directing a task. References are always model-invoked so the agent can retrieve them when relevant.

A workflow may load reference material or call a script without creating additional skill types.

## Authoring workflow

### 1. Define the target behavior

For a **workflow**, state its trigger or explicit command, ordered actions, decisions, branches, recovery paths, and required outcome.

For a **reference**, state the situations and questions that should retrieve it, the context it supplies, its limits, and how that context should be applied.

For either type, identify important exclusions and the models and harnesses that must support it.

**Complete when:** the selected type is explicit and every required trigger, command, branch, retrieval situation, outcome, limit, and exclusion relevant to that type is represented in an evaluation or marked out of scope.

### 2. Establish the baseline

Run representative evaluations without the proposed skill or change. Record the agent's decisions, outputs, navigation path, and relevant failures. Match the evaluation to the skill type; pressure scenarios apply only to workflow rules agents have an incentive to evade.

A strictly mechanical correction may use structural checks instead of a behavioral baseline only when the diff cannot alter discovery, meaning, navigation, or execution.

**Complete when:** each targeted behavior has baseline evidence showing either a relevant failure or a precisely bounded mechanical change that requires no behavioral instruction.

### 3. Design the information architecture

For a workflow, keep required actions and decisions on the execution path. For a reference, organize around the questions and terminology that retrieve the context; the skill may be entirely reference material with no procedural steps. Move large or conditional material behind direct context pointers. Use scripts or extensions for deterministic execution rather than inventing a tool skill category.

**Complete when:** every section has one authoritative location, every external file has a condition that says when to read or run it, and no required content is hidden more than one reference deep.

### 4. Write the minimum effective change

Address demonstrated failures rather than hypothetical ones.

For a **workflow**, give ordered work explicit steps. End every procedural step with a separate **Complete when:** criterion that names the exact artifact and exhaustively accounts for its required contents or conditions. State the desired action positively; add prohibitions for observed or high-cost failure paths and pair them with the required alternative.

For a **reference**, present definitions, facts, conventions, examples, and usage guidance for retrieval. Do not manufacture workflow steps, branches, or completion criteria merely to make the reference procedural.

For either type:

- Use consistent, established terminology.
- Put retrieval triggers in the description without summarizing a workflow the agent might execute instead of loading the skill.
- Keep examples only when they improve retrieval or application more efficiently than prose.
- Remove duplicated meanings, stale guidance, and instructions or context the model already supplies reliably.

**Complete when:** every new instruction or fact addresses baseline evidence, each meaning appears in one authoritative place, and the content follows only the structural requirements of its selected type.

### 5. Verify and refine

Run the original evaluations with the changed skill, then test important variations and intended models. Compare behavior with the baseline. If the agent chooses a wrong action, retrieves wrong context, invents unsupported context, or misses a reference, improve the instruction or context pointer and rerun the affected evaluations.

**Complete when:** every required behavior passes from a clean context on every intended model, every observed regression has a passing evaluation, and the agent loads only the material needed for the selected task or question.

### 6. Audit and deploy

Check frontmatter, links, terminology, file organization, invocation settings, and repository-specific installation steps. Review the final diff and run available validators.

**Complete when:** all references resolve, invocation matches the selected type, all evaluations and structural checks pass, generated or installed copies match the source, and no unresolved issue is omitted from the report.

## Release gate

- [ ] The skill is classified as workflow or reference.
- [ ] Invocation matches the type and retrieval needs.
- [ ] Baseline evidence predates the change.
- [ ] Workflow steps have checkable completion criteria; references contain no manufactured procedure.
- [ ] Conditional material has a direct context pointer.
- [ ] Meanings are not duplicated across files.
- [ ] Original and variation evaluations pass.
- [ ] Intended models and harnesses were checked or limitations reported.
- [ ] Links, frontmatter, installation, and diff were verified.
