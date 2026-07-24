# Executable Resources

Read this reference when a skill includes scripts, validators, templates, or generated intermediate artifacts.

## Prefer execution for deterministic work

Use a bundled script when an operation must be repeated consistently, is error-prone to regenerate, or can be verified mechanically. Keep judgment and branch selection in instructions; put deterministic transformation and validation in code.

State intent explicitly:

- **Execute:** “Run `scripts/validate.py plan.json`; fix every reported error and rerun until exit status is zero.”
- **Read:** “Read `scripts/validate.py` only when modifying the validation algorithm.”

Most utility scripts should be executed without loading their source into context.

## Design scripts to finish the job

A resource should:

- validate inputs before mutation;
- handle expected errors with actionable messages;
- return meaningful exit statuses;
- avoid unexplained constants;
- preserve originals or provide rollback for destructive work;
- produce a documented, machine-checkable output;
- declare required runtimes and dependencies.

Do not punt predictable failures back to the agent with a raw stack trace or ambiguous output.

## Use verifiable intermediate artifacts

For complex or destructive operations, use:

```text
inspect → write structured plan → validate plan → execute → verify result
```

The plan artifact should enumerate every intended change and required precondition. The validator should reject missing targets, conflicts, unsafe combinations, and incomplete rollback information before execution.

Each stage needs a completion criterion. “Validation complete” means the named validator exits successfully against the exact artifact that will be executed.

## Keep resources discoverable

Place executable code under `scripts/` or another clearly named directory. Point to it directly from `SKILL.md`, state when to run it, show the minimal command, and describe expected output. Use forward-slash paths and resolve them relative to the skill directory.

Keep API documentation, examples, and executable resources separate so the agent does not load code merely to discover usage.

## Verify resources

Test scripts with:

- a normal fixture;
- invalid input;
- important boundary cases;
- interrupted or partial state where relevant;
- the documented command from the skill.

Completion requires fresh passing output, expected failure messages for invalid fixtures, and confirmation that the instructions match the executable interface.
