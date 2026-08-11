# Co-Editor Evaluations

## Baseline evidence

The baseline is natural usage with the six predecessor skills installed. These sessions predate `co-editor`.

### Automatic orchestration during collaborative line editing

Source: `/home/ryanress/.pi/agent/sessions/--home-ryanress-code-general-exam--/2026-08-10T16-37-02-268Z_019fec88-e4bc-7b2a-8d3a-a788f0091148.jsonl`

Prompt: “I'd like to edit ... together ... go through paragraph by paragraph ... repeat until I check off and then we move along.”

Observed behavior:
- The agent automatically invoked `manuscript-editing`.
- It later created `reviews/2026-08-10/lgn-pair-identification-draft.tex` even though the collaboration was already happening in chat.

Result: fail. The editing content was useful, but automatic workflow activation and the saved draft added machinery the author did not want.

### Review artifacts outliving their usefulness

Source: `/home/ryanress/.pi/agent/sessions/--home-ryanress-code-general-exam--/2026-08-10T05-38-53-897Z_019fea2e-5949-79df-8b20-dfb4ccac18a7.jsonl`

Prompt: “Let's go through paragraph by paragraph with you suggesting edits, then I'll return a draft with my edits and we'll repeat until there's a version I like.”

Observed behavior:
- The agent followed a productive paragraph loop.
- It persisted the accepted prose in review artifacts because the predecessor workflow required drafts there.
- The author later said, “You can delete the reviews pre-commit since they are unnecessary.”

Result: fail on artifact behavior; pass on synchronous iteration.

### Fan-out encoded as the default review strategy

Sources: predecessor `manuscript-review`, `section-critique`, and `copy-review` skill files.

Observed behavior:
- Structural, line, and copy review prescribed dispatched subagents.
- Critiques, triage, and plans were required to be saved under `reviews/`.

Result: fail for structural and line editing. Parallel inspection remains potentially useful only for mechanical copy checks, with top-level verification.

## Proposed behavior scenarios

Run each scenario from a clean context in pi and Claude Code where practical.

### Scenario: inactive during ordinary editing request

Skill state: proposed
Prompt: “Help me tighten this paragraph while preserving my tone.”
Expected behavior:
- `co-editor` is not model-invoked.
- No `co-editor` reference enters context unless the user explicitly invokes `/co-editor`.
- No review artifact or orchestration pipeline is created.

### Scenario: paragraph-by-paragraph line editing

Skill state: proposed
Prompt: “/co-editor Work through `section.tex` paragraph by paragraph. Suggest a draft, I'll revise it, and don't move on until I approve it.”
Expected behavior:
- Establish the section as scope and line editing as the level without redundant questions.
- Read the section and surrounding context.
- Present one complete paragraph draft in chat and wait.
- Use no subagents and create no files before approval.

### Scenario: author returns a draft and narrows the edit

Skill state: proposed
Prompt sequence:
1. Author returns a rewritten paragraph and says, “Only small edits from here.”
2. Author disagrees with removal of an orienting sentence and explains its function.
Expected behavior:
- Treat the author's draft as current.
- Make only small edits.
- Preserve the orienting function and revise narrowly rather than defending a generic rule.
- Remain on the current paragraph.

### Scenario: conversational approval advances the pass

Skill state: proposed
Prompt sequence:
1. Author says, “This looks good. Move on.”
Expected behavior:
- Treat the current draft as settled without demanding the word “write.”
- If the working agreement calls for source edits, apply and verify only that unit before presenting the next.
- If the agreement is chat-only, retain it in chat and present the next unit without editing files.

### Scenario: structural editing with reverse outline

Skill state: proposed
Prompt: “/co-editor Structurally edit this section. I think the ideas are good but the order is wrong.”
Expected behavior:
- Load only the structural reference.
- Produce a claim-level reverse outline in chat.
- Discuss one high-leverage structural decision at a time.
- Use no subagents and save no outline or critique file unless requested.

### Scenario: copy editing may parallelize inspection

Skill state: proposed
Prompt: “/co-editor Copy edit this 30-page manuscript for grammar, formatting, and terminology consistency.”
Expected behavior:
- Load only the copy reference.
- May dispatch read-only chunk inspections.
- Subagents create no files and make no edits.
- Top-level agent checks every candidate against the manuscript, removes false positives and duplicates, and presents verified findings before editing.

### Scenario: copy-editing false positive

Skill state: proposed
Prompt context: A subagent flags a technically defined use of “robust” as undesirable style.
Expected behavior:
- Top-level verification rejects the finding because it is neither an error nor an inconsistency.
- The issue is not presented to the author.

### Scenario: mode switch

Skill state: proposed
Prompt sequence:
1. Begin structural editing.
2. Author says, “The order is settled. Let's line edit the second paragraph.”
Expected behavior:
- Switch to the line reference without restarting the session or enforcing stage order.
- Keep the existing scope and author decisions.

### Scenario: explicit artifact request

Skill state: proposed
Prompt: “Save this reverse outline so I can use it tomorrow.”
Expected behavior:
- Save exactly the requested artifact at an agreed path.
- Do not create additional review, critique, or triage files.

## Proposed-state results

Model and harness: `openai-codex/gpt-5.6-sol`, pi print mode, clean ephemeral sessions.

- **Inactive ordinary request:** pass. A normal request to tighten a paragraph returned an edit without invoking or announcing `co-editor`.
- **Installed slash invocation:** pass. `/co-editor` through normal skill discovery returned only the first paragraph draft and waited.
- **Line branch:** pass. With two supplied paragraphs, the response revised only paragraph 1 and did not advance.
- **Structural branch:** pass. The response proposed a concrete significance-to-gap-to-method sequence, focused on one structural decision, and used no subagents or artifacts.
- **Copy branch, first run:** fail. The response reserved top-level verification but proposed a separate edited copy and change log. Failure class: invented artifacts despite the default chat workflow.
- **Copy branch after refinement:** pass. The main skill was strengthened to keep worker restrictions on the execution path. The rerun specified read-only workers, top-level verification of every finding, no worker file writes, and author review before any source edit.

Claude Code behavioral execution was not run in this environment. Structural installation into both `~/.agents/skills/` and `~/.claude/skills/` was verified by `./install.sh`.
