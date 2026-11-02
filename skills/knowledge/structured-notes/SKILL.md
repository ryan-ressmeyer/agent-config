---
name: structured-notes
description: Use when the user asks to leave, take, write, or save a note, or to record or write down a fact, decision, or conversation for later; and when reading, creating, or editing a markdown file whose header contains a `format: structured-notes` line.
---

# Structured Notes

A structured note is a markdown file that records knowledge (research, decisions, transcripts, facts) in sections that agents can read in parts. The line `format: structured-notes` under the title marks a conforming file. Treat markdown without that line as plain text, and do not add the marker to an existing file unless the user asks to convert it.

## Layout

```markdown
# <Title>
format: structured-notes
date: YYYY-MM-DD
source: <url | file path | conversation (who, which session)>

## Summary
At most 6 lines. Enough to decide whether to read further.

## <Body sections, any number, any names>

## Sources
- [1] ...
```

- The three header lines follow the H1 directly, in this order. `date` is the creation date; git records later edits, so add no other header lines.
- `## Summary` is the first H2 and `## Sources` is the last. A short note may have no body sections.
- Use H2 (`## `) only for sections. Use H3 and below inside sections.
- Verbatim material such as a transcript, email, or quoted answers goes unedited in its own body section. The Summary says that it is verbatim.
- Sources are a numbered list. Mark a URL you did not open as cited but not checked.

## Leaving a note

When the user asks for a note, write a new file at `notes/<kebab-case-topic>.md` in the repository root, and create `notes/` if it is absent. Do not append to a README or another existing file. Use today's date. When the note records something from the conversation, `source` is `conversation` with enough detail to identify it.

## Editing a note

Keep `date` unchanged. When a body change alters a conclusion, rewrite the Summary to match, and add a Sources entry for the new information.

## Reading notes in parts

```bash
awk 'FNR==1{print "==> " FILENAME} /^## /{p=($0=="## Summary")} p' notes/*.md   # every summary
sed -n '/^## Summary/,/^## /p' notes/<file>.md | sed '$d'                      # one section (swap the heading)
grep '^## ' notes/<file>.md                                                     # table of contents
grep -L '^format: structured-notes' notes/*.md                                  # files that are not marked
```

Read the summaries first and open a full note only when its Summary shows it is relevant.
