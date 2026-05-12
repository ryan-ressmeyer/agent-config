---
name: theme-synthesize
description: Use when creating or updating a cross-paper thematic synthesis in ansa. A theme is a `collection` of `kind=theme` whose members are the papers; the synthesis itself is a `note` attached to that collection. Use when the user asks to synthesize across papers, find themes, or update an existing theme as new papers arrive.
---

# Theme Synthesize

## Overview

Create or update a thematic synthesis across multiple papers in the ansa graph. The model:

- A **theme** is a `collection` with `properties.kind = "theme"`.
- Member papers are connected via `in_collection` edges.
- The **synthesis text** is a single `note` attached to the collection via `note_of` (collection → note).

There is one synthesis note per theme. Updating a theme means PUTting a new body to the same note — not appending a second note.

The synthesis is an **objective report** of what each study found and how findings relate — not an editorial narrative, not a list of summaries, not a claim about field consensus.

## When to use

- User asks to synthesize across a specific list of papers.
- User asks about patterns or themes in the graph and 3+ papers share a topic without an existing theme.
- A new paper is added that materially changes an existing theme.
- User explicitly asks to update theme `<name>`.

## Inputs

You need:

1. **Theme name** (short, kebab-case if the user hasn't specified).
2. **A set of paper UUIDs**, supplied as:
   - An explicit list from the user, **or**
   - A search query (`ansa search "..."`) that yields candidates the user confirms, **or**
   - An existing theme collection whose members to re-synthesize.

Resolve everything to UUIDs before mutating.

## Workflow

### Step 1 — Find or create the theme collection

```bash
# Look for an existing theme by name
ansa collection ls --kind theme
```

If a collection with the requested name exists, reuse its UUID. Otherwise create one:

```bash
ansa collection add \
  --name "<theme-name>" \
  --kind theme \
  --description "<one-sentence scope of the theme>"
```

Capture the returned `id` — that's the theme UUID.

### Step 2 — Attach member papers

For each paper UUID that should belong to the theme:

```bash
ansa collection add-member <theme-uuid> <paper-uuid>
```

`in_collection` is idempotent at the (member, collection) level — re-adding a paper is a no-op. To remove a stale member:

```bash
ansa collection rm-member <theme-uuid> <paper-uuid>
```

Confirm the full member set:

```bash
ansa collection members <theme-uuid>
```

### Step 3 — Read each member's scratchpad

For each member, pull the QLMRI summary out of its scratchpad:

```bash
ansa paper scratchpad <paper-uuid>
```

If a paper's scratchpad is just the auto-stub (`# <citekey> — <title>` and nothing else), stop and tell the user that paper needs summarization first — delegate to `paper-summarize` before continuing. A synthesis built on unread papers is fiction.

Focus on:

- Questions asked
- Methods (species, preparation, stimuli, model architecture)
- Results — effect sizes, sample sizes, specific numbers
- Inferences **as stated by the authors** (not your interpretation)

### Step 4 — Check for an existing synthesis note

Find the note attached to this collection, if any:

```bash
ansa node neighbors <theme-uuid> | jq '.[] | select(.type=="note")'
```

(Equivalently: `GET /api/nodes/<theme-uuid>/notes` returns the same list.)

If a note exists, read its body and present it to the user before overwriting — synthesis updates are common and a full overwrite without review loses prior careful wording.

### Step 5 — Draft the synthesis

Render this markdown. Keep section order and headings.

```markdown
# <Theme Title> — <descriptive subtitle>

## Scope
N papers in this synthesis. Note which perspectives, subfields, methods, or
species are NOT represented. Be honest about the limited view.

## Overview
2-3 sentences framing the core question the theme addresses.
Do not claim consensus. Do not say "it is now understood." Just frame.

## Findings by Study
One paragraph per paper, attributed to the authors.
Use "AuthorName et al. (Year) found/measured/concluded..."
Cite by citekey: `[vaswani2017attention]`.

## Points of Contact Across Studies
Organize by sub-question or claim, not by paper.
Always attribute: "Study A found X [citekeyA]; Study B found Y in a different
preparation [citekeyB]."
Note:
- Where results are consistent (species/method matched)
- Where results differ or create tension
- Methodological differences that may explain discrepancies

## Open Questions
Questions that arise from the papers in this theme.
Do not speculate about answers — identify the gaps.

## Suggested Papers to Add
Specific paper types (or specific titles/DOIs if you can name them) that would
broaden the theme or address the open questions above.
```

No `Papers in This Theme` section at the bottom — the collection's `in_collection` edges are the source of truth. The web UI shows the member list automatically.

No figure embeds — figures live in attachments on individual papers, not in the synthesis. Reference them by paper citekey + figure number in prose if needed.

### Step 6 — Write the note

**If no synthesis note exists yet**, create one attached to the collection:

```bash
# Write the body to a tempfile first
cat > /tmp/theme-<name>.md <<'MD'
<full rendered synthesis from Step 5>
MD

ansa note add \
  --target <theme-uuid> \
  --title "Synthesis: <theme-name>" \
  --body-file /tmp/theme-<name>.md
```

`--target` creates the `note_of` edge from the new note → the theme collection.

**If a synthesis note already exists** (from Step 4), update its body:

```bash
ansa note edit <note-uuid>
```

`note edit` opens `$EDITOR` on the current body. For an agent-driven overwrite, use Python:

```bash
uv run --with ansa-cli python - <<'PY'
from ansa_cli.client import Client
c = Client.over_http("http://kamaji:7327")
body = open("/tmp/theme-<name>.md").read()
c.update_note("<note-uuid>", body=body)
print("ok")
PY
```

### Step 7 — Present for review

Show the rendered synthesis. Ask:

- "Does this accurately capture the relationships across these papers?"
- "Are members missing from this theme? Should any be removed?"
- "Are there candidate papers (in your suggested list) you want to add now?"

## Objectivity directives (mandatory)

The synthesis is a small subset of a larger literature. Stay within what the member papers actually say.

1. **Report findings, don't narrate history.** Don't claim a paper "began the modern understanding" or was "the first to show X" unless the paper itself says so.
2. **Attribute every claim.** "Burr et al. (1994) found X [burr1994motion]; Reppas et al. (2002) found Y [reppas2002visual]." No floating "converging evidence shows."
3. **Don't synthesize consensus that may not exist.** Avoid "it is now understood," "the definitive evidence," "has progressively narrowed."
4. **Flag blind spots.** State N papers in the Scope section. Note which perspectives are absent.
5. **Distinguish authors' claims from inferences.** Use "the authors concluded" when reporting their stance.
6. **Avoid superlatives.** No "definitive," "critical," "striking," "key," "crucial."
7. **Limitations only when they bear on interpretation.** Don't catalog every caveat for every paper.
8. **End with suggested papers to add**, not your own speculation about answers.

## Common mistakes

| Mistake | Fix |
|---|---|
| Synthesizing without reading scratchpads | Step 3 is non-negotiable — stop and `paper-summarize` empty scratchpads first |
| Creating a second note for the same theme | One note per theme; update the existing note instead |
| Editorializing across the literature | Attribute every claim by citekey; the synthesis is a report, not an essay |
| Claiming historical firsts | You're reading a sample, not the whole literature |
| Forgetting to attach members | Without `in_collection` edges the theme is just a name; add members before drafting |
| Listing papers in a "Papers in This Theme" section | The collection's edges are the source of truth — don't duplicate in prose |
| Embedding figures in the note | Figures are attachments on the paper nodes; reference by citekey + figure number |
