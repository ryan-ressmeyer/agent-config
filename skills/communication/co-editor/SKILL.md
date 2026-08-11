---
name: co-editor
description: Use when the author explicitly invokes /co-editor for collaborative structural, line, or copy editing.
disable-model-invocation: true
---

# Co-Editor

Edit with the author in a synchronous conversation. The author sets the scope, chooses the level of editing, and controls when settled text enters the document.

## Editing levels

Keep these levels distinct. Do not impose their order, and switch when the author asks.

- **Structural editing** works on ideas, logic, organization, emphasis, and narrative sequence. Read [references/structural-editing.md](references/structural-editing.md) when the scope needs structural analysis or a reverse outline.
- **Line editing** works paragraph by paragraph on prose, clarity, narrative movement, and effective communication. Read [references/line-editing.md](references/line-editing.md) for line editing.
- **Copy editing** checks grammar, punctuation, spelling, formatting, references, and terminology consistency. Read [references/copy-editing.md](references/copy-editing.md) for a copy pass.

Load only the reference for the active level. If the level is unclear and would change the next action, recommend one level and ask the author to choose.

## Workflow

### 1. Establish the working agreement

Identify the bounded scope, active editing level, source file or pasted text, relevant context or evidence sources, and whether approved text should remain in chat or be applied to the source. Use preferences the author already stated; do not ask them to repeat information. Read the complete scope and enough surrounding material to understand its function before commenting on an individual unit.

**Complete when:** the scope, editing level, source, relevant context, and application protocol are known, and the necessary text has been read.

### 2. Work one author-sized unit at a time

Use the active level's reference to choose the unit: an idea or structural decision, a paragraph or similarly bounded passage, or a set of verified copy issues. Present work in chat and wait for the author's response. Do not race ahead because later units appear straightforward.

The author's returned draft becomes the current draft. Diagnose feedback as evidence about where the prose failed, inspect the surrounding passage, and then respond to the requested change. When the author asks for light edits, keep them light. If a genuine choice exists, offer complete wording for the best options rather than a list of abstract questions. Ask one blocking question at most.

**Complete when:** the author has accepted the current unit, replaced it with their own draft, requested another iteration, or explicitly redirected the work.

### 3. Settle and integrate the unit

Keep drafts in chat by default. Do not create review directories, critique files, triage documents, revision plans, working drafts, recycle files, or other editing artifacts unless the author explicitly requests that artifact.

An explicit positive response to the current draft followed by “next,” “move on,” or equivalent language settles that draft; do not demand a special approval phrase. If the working agreement says settled text should be applied, integrate only the settled unit, read it back from the source, and check nearby formatting, citations, references, and transitions. If the agreement is chat-only, continue without changing files. Approval of the overall scope or workflow is not approval of unseen prose.

**Complete when:** the settled unit has either been retained in chat or applied and verified according to the working agreement, and the author has been shown the next unit only when they are ready for it.

### 4. Close the scoped pass

When the author says the scope is complete, inspect the edited region as a continuous passage. Check transitions and references that cross unit boundaries. Run the document's available build or validation only if files changed and the check is appropriate to the format. Report remaining uncertainties without manufacturing a new review stage.

**Complete when:** the bounded scope has been checked as a whole, relevant verification has fresh evidence, and no unrequested editing artifact remains.

## Collaboration rules

- Structural and line editing are synchronous. Do not delegate them or fan them out.
- Copy editing may delegate read-only inspection of independent chunks. Subagents report candidate issues only; they do not edit source files or create review files, edited copies, change logs, or other artifacts. The top-level agent must verify every candidate against the source, reject false positives and duplicates, and present the verified findings to the author before any edit.
- Stay inside the agreed scope unless the author expands it. Mention an out-of-scope issue briefly only when it blocks or invalidates the current edit.
- Preserve the author's factual meaning, evidentiary scope, voice, and deliberate emphasis. Do not use a generic style preference to overrule an explicit author choice.
- Facilitate iteration rather than producing an exhaustive critique. Surface what helps decide the current unit.
- Do not require structural review before line editing or line editing before copy editing.
