---
name: paper-summarize
description: Use when a paper in ansa needs to be read and summarized using the QLMRI framework (Questions, Logic, Methods, Results, Inferences), or when re-summarizing a paper already in ansa.
---

# Paper Summarize

## Overview

Read a paper that lives in the ansa knowledge graph and write a structured QLMRI summary to its **scratchpad** (`PUT /api/papers/{id}/scratchpad`). One paper at a time, interactive — the user should be learning alongside the agent.

This skill no longer touches `references/<id>/`, `index.yaml`, `references.bib`, or any per-paper folder. The scratchpad markdown blob *is* the summary.

## When to Use

- User points at a paper UUID, citekey, or title and wants a QLMRI summary.
- User wants to re-summarize a paper already in ansa (e.g. after a verify/rekey).
- A paper exists in ansa but its scratchpad is empty or only contains the auto-stub.

## Remote

Default remote: `kamaji` (`http://kamaji:7327`), via the user's `remotes.yaml`. Override by passing `--remote NAME` to `ansa`, setting `ANSA_REMOTE=NAME`, or — for inline Python — passing the URL to `Client.over_http(...)`.

## Workflow

### Step 1 — Resolve the paper

You should arrive with one of: a UUID, a citekey, or a title fragment. Resolve to a UUID before doing anything else.

```bash
# UUID already known — confirm it exists:
uv run ansa --remote kamaji node get <UUID>

# Citekey known — query for it:
uv run ansa --remote kamaji query '{"type":"paper","where":{"citekey":"vaswani2017attention"}}'

# Free-text — search FTS:
uv run ansa --remote kamaji search "attention all you need"
```

Confirm the match with the user when the input was a citekey or title — duplicates and near-misses happen.

### Step 2 — Resolve the paper text

`properties.text` and `properties.pdf` are **`file_ref` dicts** (`{kind, path, managed_by_plugin}`), not raw content — they name a storage path. Fetch via the storage API. Try sources in this order:

1. **OCR/extracted text sidecar** — if `properties.text` is present, it points at `papers/ocr/<citekey>.txt`. Fetch with `Client.get_file("papers", "ocr", f"{citekey}.txt")` and decode as UTF-8. This is the preferred source — covers both OCR and PyMuPDF-extracted body. `properties.text_status` tells you which (`done` = OCR'd; `extracted-text` = born-digital).
2. **PDF** — if `properties.text` is absent, fall back to `properties.pdf` → `papers/pdfs/<citekey>.pdf` via `Client.get_file("papers", "pdfs", f"{citekey}.pdf")`. Read natively if you are Claude.

If neither is present, stop and tell the user — `pdf-retrieve` and `paper enrich --ocr` are the upstream fixes, not this skill's job.

Always read `properties.abstract`, `properties.title`, `properties.authors` (via `authored_by` edges if needed), `properties.year`, `properties.journal`, `properties.doi` as the citation skeleton — don't try to extract these from the body.

### Step 3 — Check the existing scratchpad

```bash
uv run ansa --remote kamaji paper scratchpad <UUID>
```

The route auto-stubs `# <citekey> — <title>\n\n` on first GET. If the body is just the stub (or empty after the stub), overwrite freely in Step 5. If it contains real content (prior summary, human notes), surface it to the user and ask before overwriting — the PUT is a full overwrite, not a merge.

### Step 4 — Draft the QLMRI summary

Render this markdown, filling each section from the paper text. Keep section order; don't rename headings. The first heading is `# <citekey> — <short title>` so it lines up with the auto-stub.

```markdown
# <citekey> — <short title>

## Citation
Full citation, APA-ish, with DOI.

## Subject / Preparation
Species (genus species if known), preparation, age/sex/strain if relevant.
Computational work: "Computational model" / "Simulation" + framework details.
Multiple subjects: list all.

## Questions
- What specific questions does this paper address?
- Frame as the authors frame them.

## Logic
- Reasoning structure / hypothesis.
- Predictions that follow.
- What would falsify it.

## Methods
- Key experimental/computational methods.
- Sample sizes, statistical approaches.
- Stimulus parameters, recording methods, model architecture — whatever is central.

## Results
- Key findings with effect sizes and statistics where reported.
- Distinguish primary findings from secondary/exploratory.
- Reference figure numbers for key results (e.g. "Fig. 3B").

## Inferences
- What do the authors conclude?
- Are the conclusions supported by the data?
- Note overclaims or caveats the authors acknowledge.

## Key Figures
Reference figures by number with one-line captions. (No filesystem embeds — the scratchpad is a single markdown blob; figure assets live elsewhere if they exist at all.)
```

### Step 5 — Write the scratchpad

PUT the rendered body. There is no CLI flag for this today (`ansa paper scratchpad --edit` opens `$EDITOR`, which doesn't fit an agent workflow). Use a short inline Python call:

```bash
uv run --with ansa-cli python - <<'PY'
from ansa_cli.client import Client
c = Client.over_http("http://kamaji:7327")
body = open("/tmp/qlmri-<UUID>.md").read()  # or pass a heredoc
c.put_scratchpad("<UUID>", body)
print("ok")
PY
```

Round-trip to confirm:

```bash
uv run ansa --remote kamaji paper scratchpad <UUID>
```

### Step 6 — Present and discuss

Show the rendered summary to the user. Ask:

- "Does this accurately capture the paper? Anything to correct or add?"
- If the user wants to tag/group this paper (status, topic, reading-list), that's a `collection` workflow — see the `ansa-literature-review` orchestrator. The scratchpad itself is just the QLMRI body.

### Step 7 — Surface related papers

The old `references.yaml` / `cited-by.yaml` / `related.yaml` files don't exist in ansa. Use `ansa similar` for semantic neighbors:

```bash
uv run ansa --remote kamaji paper similar <UUID>
```

For citation neighbors, walk `cites` edges via `node get <UUID>` + `ansa edge list --source <UUID> --type cites` — though as of Phase B importers don't yet build `cites` edges (Phase F).

## Rigor Requirements

- **Distinguish claims from evidence.** "Authors claim X" vs "Data show Y" when they diverge.
- **Note sample sizes.** N animals, n neurons/trials/subjects.
- **Report statistics.** p-values, effect sizes, confidence intervals when available.
- **Flag concerns.** Marginal significance, missing controls, overclaims, circular analyses.
- **Capture subject details.** Species, strain, age, sex, preparation.
- **For computational papers:** Note model assumptions, parameter choices, validation approach.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Summarizing the abstract instead of the full paper | Read all sections — results often diverge from abstract framing. |
| Missing subject/preparation details | Always check Methods for species, strain, preparation. |
| Accepting author conclusions uncritically | Compare Results to Inferences — note any gaps. |
| Skipping statistics | Include p-values, N, effect sizes where reported. |
| Overwriting a human-edited scratchpad without asking | GET first; only overwrite the auto-stub silently. |
| Trying to read `references/<id>/...` files | Those don't exist anymore. Everything is HTTP against the ansa remote. |
