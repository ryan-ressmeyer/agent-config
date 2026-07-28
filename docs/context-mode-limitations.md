# Context-mode in Pi: Benefits, Limitations, and a Path Toward Selective Routing

## Purpose

This document evaluates how context-mode affects work in Pi and identifies changes that could make its routing selective rather than universal. It is based on direct observation during a manuscript-editing session on July 27, 2026, inspection of context-mode 1.0.169, and comparison with Pi's built-in tools.

The central conclusion is that context-mode is useful when the task is fundamentally one of **data reduction**. It is less useful, and can be counterproductive, when the task requires **semantic understanding of a bounded text**. A good configuration should preserve both modes instead of treating every read as a potential context flood.

This is a design analysis, not a final configuration. Its purpose is to support later experiments and deliberate changes to `agent-config`.

## Executive summary

Context-mode provides three distinct capabilities:

1. **Sandboxed derivation**: commands or files can be processed without placing all source bytes in the model context.
2. **Persistent indexing and retrieval**: large outputs can be stored and queried later through focused searches.
3. **Routing guidance and memory hooks**: the Pi extension injects instructions that encourage the model to prefer `ctx_*` tools and records session events for later retrieval.

The first capability is valuable for logs, test output, structured data, repository-wide aggregation, and commands with unknown output size. The second is valuable for large reference collections that will be queried repeatedly. The third may help continuity across long sessions.

The problem is routing. The bundled guidance treats normal reading as exceptional:

> context-mode active. Hierarchy: ctx_batch_execute > ctx_execute > ctx_execute_file > ctx_search. Read/edit files → ctx_execute_file.

The context-mode skill is more aggressive still. It says to default to context-mode for all commands, reserves Bash for a small whitelist, and treats any MCP output that may exceed 20 lines as a trigger. This policy conflates output length with task type. Twenty lines of a manuscript, function, or configuration file may be essential evidence rather than noise.

During the manuscript task, context-mode kept large PDF extractions out of the visible conversation, but it also:

- converted straightforward reading into repeated extraction, indexing, and search operations;
- obscured document structure and nearby context;
- mixed snippets from multiple similarly labeled sources;
- made two-column PDF reconstruction more difficult;
- introduced search throttling and additional failure modes;
- reported no measured token savings despite substantial use.

The preferred strategy is a **balanced hybrid**:

- read bounded prose and source files directly when understanding, editing, or exact context matters;
- use context-mode when deriving an answer from large or unknown data;
- use search to locate relevant sections in large documents, then read those sections in full;
- use dedicated format-aware tools, such as a PDF reader, before using a generic indexing layer.

## What context-mode currently does in Pi

### Tool layer

The extension exposes tools for four broad operations:

- execution and derivation: `ctx_execute`, `ctx_execute_file`, and `ctx_batch_execute`;
- storage and retrieval: `ctx_index` and `ctx_search`;
- web acquisition: `ctx_fetch_and_index`;
- diagnostics and management: `ctx_stats`, `ctx_doctor`, `ctx_upgrade`, `ctx_purge`, and `ctx_insight`.

The execution tools are built around a sound idea: code should process the source data and print only the derived result. If the task is to count failures in a 50 MB log, the model should write the counting program rather than read the log.

### Prompt-level routing

The Pi adapter injects a lightweight routing anchor during `before_agent_start`. In version 1.0.169, that anchor explicitly directs file reads toward `ctx_execute_file`, multi-command research toward `ctx_batch_execute`, and web pages toward fetch-and-index followed by search.

This is guidance rather than a general tool prohibition. Inspection of the Pi adapter showed that its `tool_call` hook only hard-blocks unsafe inline HTTP clients in Bash, including language-level HTTP calls and `curl` or `wget` commands that would write to stdout. It does not programmatically block Pi's normal `read` tool or ordinary inspection commands. Therefore, a more selective policy can be imposed through higher-priority project or user instructions without first replacing the extension.

### Skill-level routing

The bundled context-mode skill goes beyond the extension's short routing anchor. It declares context-mode mandatory for nearly all commands and uses a very narrow Bash whitelist. It also routes file analysis through `ctx_execute_file` even when a direct read would be bounded and semantically useful.

This distinction matters when tuning the system:

- the extension supplies tools, persistence, session hooks, and a short routing nudge;
- the skill supplies the most aggressive behavioral policy;
- local `AGENTS.md` instructions can refine the model's choices because most routing is not hard enforcement.

## What helped during the manuscript task

### Large PDF extraction did not flood the conversation

The two PDFs contained 30 and 11 pages. Poppler's `pdftotext` generated outputs large enough to consume substantial context if returned in full. Running extraction inside `ctx_execute` allowed small programs to search for headings and terms such as `Methods`, `PEDOT`, `fixation`, and `Electrophysiology` while keeping most bytes out of the conversation.

This was a legitimate use of sandboxed derivation. The task initially required locating relevant material in documents of uncertain structure, and context-mode reduced the cost of broad reconnaissance.

### Repository and remote-pipeline inspection benefited from batch execution

When the monkey A spike-sorting pipeline had to be checked on `solo`, `ctx_batch_execute` combined directory discovery, documentation inspection, and repository-wide searches. The raw command output was much larger than the few lines needed to establish that non-Logan subjects were sorted with Kilosort 4 and passed through pipeline quality control.

This is close to context-mode's ideal use case:

- several related commands;
- potentially large, repetitive output;
- a narrow factual question;
- no need to preserve the prose or exact structure of every source file.

A later targeted read of the relevant source lines then supplied exact evidence. The hybrid worked well.

### Context-mode supported targeted recall

Once outputs were indexed, `ctx_search` could recover specific passages without rerunning every extraction. This helped retrieve the existing manuscript's Methods fragments and the prior paper's descriptions of eye tracking, surgery, stimulus presentation, and electrophysiology.

Persistent retrieval could be more valuable in longer projects where the same documentation or output is consulted repeatedly. The benefit was smaller in this short task because most indexed material was used only once.

## Limitations observed during the task

### 1. Semantic reading was treated as data reduction

The manuscript task required understanding complete Methods sections, not merely finding isolated facts. Prose has local structure:

- qualifications may follow a claim;
- a subsection heading changes the interpretation of subsequent sentences;
- omitted information can be as important as matched information;
- terminology and level of detail must be judged across paragraphs;
- authorial voice is visible only in sustained context.

Search snippets are an incomplete representation of this evidence. They answer the query that was asked, but they are poorly suited to discovering unanticipated relationships or absences. This creates a form of retrieval-induced confirmation bias: the model sees passages related to its current hypothesis and may miss nearby text that would change the conclusion.

For manuscript editing, a bounded full-section read is often the efficient choice even if it consumes more immediate context.

### 2. Tool-call multiplication

A direct read is one operation. The context-mode path often became:

1. run extraction;
2. allow the output to be indexed;
3. inspect the indexing summary;
4. formulate retrieval queries;
5. search the index;
6. rerun extraction when the snippets lack context;
7. perform a targeted direct read anyway.

Each step adds latency and another opportunity for a poor query, source collision, timeout, or truncation. Context-mode can save context while increasing wall-clock time and cognitive overhead.

The manuscript session demonstrated this clearly. Several broad PDF extractions were indexed, followed by multiple searches and narrower extraction passes. A format-aware PDF tool plus direct reading of the relevant pages would likely have been faster and more reliable.

### 3. Loss of document structure and provenance

The PDFs were two-column scientific articles. `pdftotext -layout` preserved approximate page layout but interleaved columns in some searches. `pdftotext -raw` produced cleaner paragraphs but weakened page and section provenance. Once indexed, snippets did not consistently retain dependable page numbers or neighboring headings.

This is not solely a context-mode defect; Poppler extraction caused much of the problem. Context-mode nevertheless made the structural loss harder to notice because retrieval returned plausible fragments without a full-page view.

For scientific documents, useful provenance includes:

- PDF page number and printed page number;
- section and subsection heading;
- paragraph boundaries;
- figure or table association;
- column order;
- extraction mode;
- source-file identity and hash.

A generic text index cannot substitute for a PDF-aware reader that preserves these features.

### 4. Source-label collisions

Several `ctx_execute` calls were indexed under generic labels such as `execute:javascript`. Searches could return passages from the current manuscript, the Nature Communications paper, or unrelated command output. Queries had to include distinctive terms such as `PEDOT` or `Monkey A` to disambiguate them.

This weakens confidence and increases query complexity. Every indexed operation should have a stable, explicit source label derived from the file path and operation, for example:

- `pdf:FEM_V1_Fovea-1:methods`;
- `pdf:yates2023detailed:methods`;
- `repo:data-yates-v1:pipeline`.

Retrieval should make source scoping the default rather than an optional refinement.

### 5. Retrieval throttling became part of the workflow

Repeated searches triggered context-mode's rolling search throttle. The tool advised batching queries and progressively limited results. Batching is often good practice, but a throttle introduces a constraint unrelated to the scientific task. A weak first query becomes more costly because exploratory refinement is rationed.

This can encourage over-broad batched searches before the evidence landscape is understood. It also makes performance depend on earlier activity in the session rather than only on the current request.

### 6. Sandboxing blocked legitimate reads outside the project root

When Pi documentation under the global package installation was inspected, `ctx_execute_file` rejected the path because it resolved outside `/home/ryanress`, the active project root. Pi's normal `read` tool could access the same explicitly authorized documentation. The fallback was to read a 2,912-line Markdown file in bounded chunks.

The sandbox is an important security boundary, but the routing instruction did not account for this difference in capability. A hierarchy that always prefers `ctx_execute_file` can choose a tool that is categorically unable to access a valid source.

Routing should consider path accessibility before selecting a tool.

### 7. Exact-text editing remains dependent on direct reads

Pi's `edit` tool requires exact source text. Context-mode is designed to derive information without exposing all source bytes, which is the opposite requirement. Any file that will be edited must eventually be read with sufficient exact context to construct and verify the replacement.

The bundled instruction `Read/edit files → ctx_execute_file` is therefore too broad. Context-mode can help analyze a large file before editing, but it cannot replace the exact read needed for a safe edit.

### 8. Metrics did not demonstrate a benefit in this session

At the end of the manuscript and PDF work, `ctx_stats` reported:

```text
context-mode  1h 41m  23 calls

91.6 KB entered context  |  0 tokens saved
```

This does not prove that context-mode provided no value. Full PDF extractions were kept out of the visible conversation, and the reported metric may not capture the counterfactual cost of commands that would otherwise have been narrowed manually. It does show that the available telemetry did not substantiate a token-saving claim for this task.

A useful metric must explain:

- which calls avoided how many source bytes;
- what baseline operation is assumed;
- how much indexed retrieval later re-entered context;
- the added number of calls and elapsed time;
- whether the final answer was more or less accurate.

Without a credible counterfactual, a single "tokens saved" number is difficult to interpret.

### 9. Automatic indexing can preserve low-value material

Failed extraction attempts, broad regex windows, and malformed section boundaries were indexed alongside useful passages. One extraction failed to find its intended endpoint and captured much more of the manuscript than intended. This material remained searchable even though it was an intermediate error.

Automatic capture is convenient, but persistent stores need quality controls:

- do not index failed commands by default;
- allow the caller to mark an output as ephemeral;
- associate outputs with success criteria;
- support deletion of one source without purging an entire project;
- expire low-value command artifacts sooner than curated documentation.

### 10. Context savings are not equivalent to task performance

Context-mode optimizes the number of source bytes entering the model. That is only one component of performance. For research and writing tasks, other outcomes can matter more:

- factual completeness;
- preservation of qualifications and uncertainty;
- detection of contradictions and omissions;
- faithful representation of source structure;
- time to a usable draft;
- number of corrective interactions required.

A routing policy that minimizes context while degrading any of these outcomes is not efficient in the broader sense.

## When full-text reads are the right tool

Full reads are appropriate when the source is bounded and the model must understand it as a whole. Examples include:

- a manuscript section being revised;
- a source file that will be edited;
- a skill or instruction file whose complete rules must be followed;
- a configuration file where interactions among fields matter;
- a design document whose argument develops across sections;
- a short paper section where omissions and transitions are evidence;
- code review of one manageable module;
- exact API documentation needed for implementation.

A full read should not be considered a failure to optimize context. It is the acquisition of primary evidence. The appropriate question is whether the evidence is bounded and relevant, not whether it exceeds an arbitrary line count.

Pi's built-in read limit of 50 KB or 2,000 lines already provides a natural guardrail. A file below that limit is not automatically safe or useful, but direct reading it should remain a normal option.

## When context-mode is the right tool

Context-mode is strongest when the task asks for a transformation, filter, aggregate, or search over data larger than the desired answer. Examples include:

- identify failures in a long test log;
- summarize a large JSON response;
- calculate counts or distributions across a dataset;
- inspect repository-wide dependency or symbol patterns;
- compare Git histories or large diffs;
- query multiple remote services;
- search a large documentation collection repeatedly;
- process many files to produce a small inventory;
- inspect commands whose output size is unknown and potentially unbounded.

The defining property is not "more than 20 lines." It is a large ratio between source volume and required answer volume.

## A balanced routing model

### Four operation modes

A useful Pi configuration should distinguish four modes.

#### 1. Direct reading

Use `read` when:

- one bounded text source is central to the task;
- exact wording or surrounding context matters;
- the file will be edited;
- document structure or argumentative flow matters;
- the expected output is within Pi's normal read bounds.

#### 2. Sandboxed derivation

Use `ctx_execute` or `ctx_execute_file` when:

- the answer must be computed from the source;
- the source is structured data, logs, or command output;
- only a small subset or aggregate is required;
- raw output size is unknown or large.

#### 3. Persistent indexing

Use `ctx_index` and `ctx_search` when:

- the same large source will support multiple later questions;
- a documentation corpus or session history merits durable retrieval;
- source labels and provenance can be made explicit;
- the cost of indexing is likely to be amortized.

#### 4. Hybrid locate-then-read

Use search or derivation to locate relevant regions, then read those regions directly when:

- a large document contains a small number of semantically rich sections;
- exact interpretation matters after broad discovery;
- format-aware extraction can preserve page or section boundaries.

The manuscript task belonged primarily in the fourth mode.

### Proposed decision procedure

Before choosing a tool, evaluate the task in this order:

1. **Will the file be edited?** If yes, use direct read for the affected region.
2. **Is exact wording, adjacency, or document structure evidence?** If yes, prefer direct read.
3. **Is the source bounded to approximately 30–50 KB or a known section?** If yes, direct read is acceptable.
4. **Is the requested answer an aggregate, filter, count, parse, or transformation?** If yes, use sandboxed derivation.
5. **Are three or more sources being compared or inventoried?** If yes, consider batch execution or indexing.
6. **Will the source be queried repeatedly?** If yes, index it with an explicit source label.
7. **Is output size unknown and potentially large?** If yes, capture it through context-mode.
8. **Is the format specialized?** Use a format-aware tool first, then choose direct or indexed consumption.

This procedure makes task semantics primary and source size secondary.

## Proposed Ryan-specific policy

A first policy for `shared/AGENTS.md` could eventually state:

> Prefer direct `read` for bounded text files, manuscript sections, source files being edited, complete instruction files, and tasks requiring exact surrounding context. Use context-mode for unknown or large outputs, structured or tabular data, aggregation across multiple files, repository-wide searches, and outputs expected to exceed 50 KB. For large prose documents, use context-mode or a format-aware reader to locate relevant sections, then read those sections in full. Do not route by line count alone.

This policy should be tested before being installed globally. It may need narrower variants for different task classes:

- scientific writing and literature review;
- software implementation and debugging;
- exploratory data analysis;
- infrastructure and server administration.

## Available tuning surfaces

### 1. Repository instructions

Because normal `read` calls are not hard-blocked, `shared/AGENTS.md` can override the aggressive default with a balanced rule. This is the lowest-cost intervention and can be reverted easily.

The risk is instruction conflict. Context-mode injects its routing anchor on every turn, while `AGENTS.md` is loaded as standing project context. The wording must explicitly state that it refines the context-mode hierarchy rather than merely offering another preference.

### 2. Package resource filtering

Pi packages can filter extensions and skills independently. The bundled context-mode skill could be disabled while keeping the package extension enabled. This would remove the strongest "default for all commands" guidance but retain the extension's tools, hooks, and lighter routing anchor.

This option needs a controlled test because package-filter behavior and generated settings must remain compatible with `install.sh` and the existing settings merge strategy.

### 3. A local policy extension

A small Pi extension could inject a replacement routing policy after context-mode loads. This would centralize the behavior and allow future controls such as:

- `/context-mode manual`;
- `/context-mode balanced`;
- `/context-mode aggressive`;
- a per-turn `context-mode: off` escape hatch;
- status-bar display of the active routing profile.

A prompt-only extension would be easy to build but could still conflict with context-mode's own injection order.

### 4. A context-mode fork or upstream contribution

The cleanest technical solution is native configuration in context-mode. Useful options would include:

```json
{
  "routing": {
    "profile": "balanced",
    "directReadMaxBytes": 50000,
    "multiSourceThreshold": 3,
    "routeByTaskType": true,
    "indexCommandOutputs": "successful-only",
    "requireExplicitSourceLabels": true,
    "allowDirectReadForEditing": true
  }
}
```

Profiles could be defined as:

- `manual`: tools available, no routing prompt;
- `balanced`: semantic direct reads allowed, large-data operations routed;
- `aggressive`: current behavior;
- `custom`: user-defined thresholds and exceptions.

The current Pi adapter does not expose a documented configuration of this kind.

## Improvements context-mode itself could make

### Task-aware routing

Routing should classify the requested operation, not just the potential output size. "Read this Methods section" and "count errors in this log" are different tasks even if both sources contain 500 lines.

### Preview before indexing

For uncertain outputs, the tool could capture data in the sandbox, estimate its size and structure, and then choose among:

- return directly if small;
- return a derived summary;
- index if large and likely reusable;
- save to a temporary file if large but ephemeral.

This avoids indexing every intermediate command.

### Explicit ephemeral mode

Execution tools should allow outputs to be marked `ephemeral`, preventing low-value or failed attempts from entering persistent retrieval.

### Better provenance

Every indexed chunk should retain file path, content hash, command, page or line range, extraction mode, timestamp, and a caller-supplied source label. Search results should display this provenance prominently.

### Promote search results to direct reads

A search result should be able to return a precise file range that Pi's normal `read` tool can open. The intended loop would be:

```text
locate broadly → identify exact range → read exact range → reason from full local context
```

### Honest comparative telemetry

Stats should report more than inferred token savings. A useful per-task report would include:

- source bytes captured;
- bytes returned to the model;
- indexing and retrieval calls;
- wall-clock duration;
- retrieval retries;
- direct-read counterfactual size;
- whether the final source was later read directly anyway.

## Evaluation plan

Changes should be evaluated with repeated real tasks rather than intuition alone.

### Task classes

Use representative tasks from Ryan's work:

1. **Manuscript editing**: revise a Methods section using two papers.
2. **Literature review**: extract QLMRI evidence from one paper.
3. **Code editing**: modify one module after understanding its local design.
4. **Repository analysis**: identify an architectural pattern across many files.
5. **Debugging**: diagnose a failing test suite from logs and source.
6. **Data inspection**: summarize a large CSV or JSON result.
7. **Documentation lookup**: implement against a long API reference.
8. **Server operations**: inspect logs, services, or deployment state.

### Conditions

Run each task under three policies:

- direct-tool baseline;
- current aggressive context-mode routing;
- proposed balanced routing.

Where practical, use the same model and fresh sessions. Record the initial prompt, source files, and expected answer criteria.

### Metrics

#### Quality

- factual errors;
- missed qualifications or contradictions;
- unsupported claims;
- edit correctness;
- independent reviewer score;
- number of user corrections.

#### Efficiency

- elapsed time;
- number of tool calls;
- number of retrieval refinements;
- bytes and estimated tokens entering context;
- duplicate source acquisition;
- number of failed or blocked calls.

#### Usability

- whether the user can follow the evidence trail;
- whether exact source provenance is available;
- whether the workflow feels interruptive;
- whether the final answer arrives in a useful form.

### Success criteria for balanced routing

Balanced routing should:

- match or improve answer quality relative to direct reading;
- reduce context use materially on large-data tasks;
- avoid increasing tool calls substantially on bounded-text tasks;
- preserve exact source access for edits;
- reduce retrieval retries and source collisions;
- make its routing decisions understandable from the transcript.

## Implications for a PDF extension

A PDF extension and context-mode solve different problems.

A PDF extension should preserve document semantics:

- page ranges;
- section boundaries;
- columns;
- figures and tables;
- OCR when needed;
- stable page provenance.

Context-mode should decide how much of the extracted material enters context and whether it merits persistent indexing. The PDF extension should therefore sit before context-mode in the pipeline:

```text
PDF → format-aware extraction → locate relevant pages → direct section read
                                      └→ optional indexing for repeated queries
```

Installing a PDF extension would not eliminate the need to tune context-mode. It would remove one source of extraction noise and make hybrid routing more reliable.

## Recommended next steps

1. Install or inspect a PDF-reading extension separately; do not treat it as the routing solution.
2. Add a temporary balanced-routing override in a branch or controlled experiment.
3. Disable the bundled context-mode skill while retaining the extension, if package filtering behaves as expected.
4. Run a small A/B comparison across one manuscript task, one code task, and one log-analysis task.
5. Review transcripts for quality, latency, and unnecessary tool multiplication.
6. Decide whether an `AGENTS.md` rule is sufficient or a local Pi extension is warranted.
7. Consider proposing configurable routing profiles upstream if the balanced policy generalizes.

## Conclusion

Context-mode addresses a real problem: large tool outputs can consume context without improving reasoning. Its sandboxed derivation tools are valuable when the source is much larger than the answer, and its indexing tools can support repeated retrieval from large collections.

The current routing policy overgeneralizes that insight. Reading a bounded source is sometimes the reasoning task itself. Manuscripts, instruction files, code modules, and design documents contain structure that cannot be reduced safely to keyword-matched snippets. In those cases, full context is not waste; it is evidence.

Pi should choose between direct reading, derivation, indexing, and hybrid locate-then-read workflows based on the semantics of the task. A balanced configuration would preserve context-mode's advantages while avoiding the latency, retrieval bias, and structural loss observed in this session.
