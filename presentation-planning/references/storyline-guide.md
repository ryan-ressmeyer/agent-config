# Stage 2: Storyline — Narrative Craft Guide

Stage 2 produces `storyline.md`. It is the talk's skeleton — the order in which ideas arrive, the shape of the argument, and the places where prerequisite knowledge is earned along the way. No slides yet. Bullets, not prose.

---

## The ABT core statement

Before the arc, settle the one sentence the whole talk is making. Use Randy Olson's ABT pattern (via Crivellaro). **ABT is a structure of three roles, not a fill-in-the-blank with three fixed words.** The roles are what matters:

> **[Setup-what]** [shared context the audience already accepts] — **AND / SO** — **[Setup-why]** [why that context is important / what's at stake] — **BUT** [the conflict / gap / problem that makes this interesting] — **THEREFORE** [what the speaker did or concluded]

The Setup is two sub-clauses joined by an **explicit, audible conjunction** — never just a comma, never elision. The conjunction is what tells the audience "we are now moving from *what we're talking about* to *why it matters*," and that move is the load-bearing job of the Setup. Two conjunctions are admissible:

- **AND** — when the *why it matters* is an additional fact alongside the *what* (parallel relationship). This is the default.
- **SO** — when the *why it matters* is a consequence of the *what* (causal relationship). Use when SO reads more naturally than AND; do not weaken to a comma or a new sentence.

The Pivot should almost always be a literal **BUT** (or HOWEVER) — the audience needs an audible turn for the conflict to register. The Resolution should almost always be a literal **THEREFORE** (or SO, in its causal sense). Connectors are the audience's handrails through the sentence; do not file them off.

Example (from Crivellaro), canonical form:
> Bird egg shapes vary widely, AND this is thought to be driven by life-history adaptation, BUT we lack a global synthesis of how egg shape actually evolves, THEREFORE we analyzed 49,175 eggs across 1,400 species and found that flight capability is the primary driver of egg shape variation.

Same statement with a SO in the Setup, which can read more naturally when the "why it matters" clause is a *consequence* of the "what" rather than a parallel fact about it:
> Bird egg shapes vary widely, SO understanding what drives that variation tells us how life history shapes morphology, BUT we lack a global synthesis, THEREFORE we analyzed 49,175 eggs across 1,400 species and found that flight capability is the primary driver.

The Pivot is where the attention is. If removing the BUT leaves a sensible sentence ("Bird egg shapes vary widely, and this is driven by adaptation; we analyzed eggs"), the talk has no conflict and will not hold the audience.

A well-formed ABT should:
- Be utterable in ~30 seconds.
- Have exactly one Pivot (one BUT / one turn).
- Have a Setup that does *both* jobs: establish shared context *and* make the stakes legible. A Setup that only states the *what* without the *why it matters* is the most common ABT failure — the audience accepts the context but doesn't yet care about it, so the Pivot lands on no one.
- Restate the Frame's core message — but with the shared context, the stakes, and the conflict made explicit.

---

## The arc

A scientific talk is structured as a hero's journey where the **question** is the hero (Alon). Not the speaker, not the lab, not the method — the question.

### Four-beat arc (works for 20–40 minute talks)

| Beat | Content | Time share (rough) |
|------|---------|---------------------|
| 1. Hook | The fundamental question the audience already cares about (or can be made to care about in 60 seconds). Phrased as a problem, not a topic. | 10–15% |
| 2. Conflict | Why the question is hard. What's wrong with the field's current answer. What tool or idea has been missing. | 10–15% |
| 3. Resolution | The speaker's work, told as a sequence of "data dives" that together answer the core question. | 60–70% |
| 4. Meaning | What the world looks like now that the core message is true. Implications, open questions, a final restatement of the ABT. | 10–15% |

### The data dives

The Resolution decomposes into one or more **data dives**. A dive is a mini-argument with the same shape as the talk overall: it opens with a sub-question, shows one piece of evidence, lands a one-sentence result, and bridges to whatever comes next.

Each dive:

- Opens with a **sub-question** that is visibly a piece of the main question.
- Shows **one piece of evidence** (one key figure worth of data).
- Lands a **one-sentence result**.
- Closes with a **bridge** that sets up the next dive (or the Meaning beat, if it is the last).

**How many dives?** Let the *argument* decide, not a quota.

- A talk can be a single dive if the core message rests on one body of evidence that is best built up in layers (e.g., a methods-heavy talk whose entire weight is one centerpiece figure).
- A talk can have two dives if the core message decomposes into exactly two separable claims, with a fast pivot between them.
- A talk often has three or four dives when the core message has multiple distinguishable sub-claims (result → mechanism → control, or observation → manipulation → generalization).

What *actually* constrains the count:

- If a single dive takes longer than ~8–10 minutes to tell, the audience will need a recovery point inside it — subdivide.
- If the talk has more than ~5 dives, the audience will lose the through-line — this usually means the core message is too broad (revisit the Frame) or adjacent dives should be merged.
- If two "dives" collapse into the same result, they are one dive. If one "dive" has two results, it is two.

The 3–5 range is typical for 20–40 minute talks. It is a frequency observation, not a target.

### Between-dive recovery

At each transition between dives, the audience will have zoned out at least partially. Design a brief return to the big picture. Options (use the principle; don't fetishize the device):

- A single sentence that names where you are in the argument.
- A reused schematic, if the talk is long and has clearly separable sections.
- A return to the driving question on screen.

**Do not** insert a recurring "home slide" mechanically in a short or single-thread talk — it will feel templated. Judge by whether a zoned-out listener at this transition would actually need it.

---

## Stepping stones — earning the prerequisites

From the Frame's Build list, every concept must be introduced as **forward motion** in the narrative, not as a static Background slide.

### Pattern to avoid

> Slide 3: "Background: The visual hierarchy" — a schematic of LGN → V1 → V2 → MT, with bullet points about each area.

This is a foreign object. The audience does not yet know why they should care. The information will not stick.

### Pattern to use

Introduce the visual hierarchy *at the moment the talk needs it*, in the service of the question:

> Slide 3 (within Hook): "The standard story is that the retina hands a clean image to LGN, which relays it to V1 for real processing. I'll show you that story is wrong at the very first relay."

Now the audience has the hierarchy they need, framed as a claim the speaker is about to interrogate. The concept is earned.

### Writing the stepping-stone plan

For each concept on the Build list, specify:

- **Where** in the arc it gets earned (which beat, which dive).
- **How** it is framed as forward motion (what claim is being set up by introducing it).
- **Verbal form** — the sentence the speaker says when the concept enters.

If you cannot write a forward-motion framing for a prerequisite, it is a sign either (a) the concept isn't actually needed, (b) the core message is too ambitious for the audience, or (c) the narrative order needs to change to put a different concept first.

---

## Order check: anti-chronology

The lab-notebook order ("we did X, then Y failed, so we pivoted to Z, which gave us these results") is the default narrative shape an LLM or an inexperienced speaker will produce. It is the single most common failure mode in scientific talks.

### Checklist

- Does the talk open with a **question the audience cares about**, or with "the goal of this project was…"?
- Does the first result appear before the midpoint, or buried in the back half?
- Are the data dives ordered by **logical dependency** (each builds on the previous claim), or by **chronological order** (the order they were produced in the lab)?
- Does the talk end with **the implication of the core message**, or with "Future Directions"?

If any answer is wrong, the order needs rework. Kenny's framing: a speech is a film trailer, not a précis — it reveals the subject matter and mood, not the plot in order.

---

## What storyline.md looks like

```markdown
# Storyline — [Talk Title]

## ABT core statement
> AND [context], BUT [conflict], THEREFORE [resolution].

## Arc

### Hook (~3 min)
- [Opening claim / question]
- [Any prerequisite earned here: <concept> → <forward-motion framing>]
- Beat closes on: [one-sentence setup for the conflict]

### Conflict (~3 min)
- [What the field's current answer is, and why it is insufficient]
- [Any prerequisite earned here]
- Beat closes on: [one-sentence setup for the resolution]

### Resolution — dives

#### Dive 1: [sub-question]
- Prerequisites earned here: [...]
- Key evidence: [one-line description of the figure]
- Result: [one sentence]
- Bridge: [one sentence to next dive, or to the Meaning beat]

#### Dive 2 (if the argument has a second piece): [sub-question]
- [...same structure...]

#### Additional dives as the argument decomposes — no fixed count.

### Meaning (~3 min)
- [World-after-message claim 1]
- [World-after-message claim 2]
- Restate ABT.

## Stepping stones — prerequisite earning plan
| Prerequisite | Earned where | How it's framed as forward motion |
|--------------|--------------|------------------------------------|
| [concept] | Hook | [sentence] |
| [concept] | Dive 2 | [sentence] |
| [...] | | |

## Order check
- Question-first opening? [y/n]
- First result before midpoint? [y/n]
- Dives in logical (not chronological) order? [y/n]
- Closes on implications, not "future directions"? [y/n]
```

---

## Signals the Storyline is not done

- ABT has more than one BUT, or no BUT.
- Any prerequisite from the Frame's Build list has no home in the stepping-stones table.
- A dive is actually two dives (two sub-questions, two results).
- Dives are ordered chronologically.
- The Meaning beat is "Future Directions" with no restatement of the core message.

Until all of these are clear, stay in Stage 2.
