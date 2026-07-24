# Stage 1: Frame — Elicitation Guide

Stage 1 produces `frame.md`. It is a short interview, not a dialog. Ask the four questions below, in order. Record the answers verbatim where possible. Write the file at the end. Do not start Stage 2 until the user has signed off on the file.

---

## The four questions

### Q1. Who specifically is in the room?

Not "the neurobiology faculty." Specifically:

- Which **subfields** are represented? (molecular neuro, systems neuro, computational, developmental, clinical…)
- Which audience members are **expert in the speaker's specific topic**? Which are **generalists** for this topic?
- Who are the 2–3 **most important individuals** in the room? (Committee members, target collaborators, hiring decision-makers.)
- What is the **size** of the audience?

Why this level of detail: a talk designed for "faculty" is designed for no one. A talk designed for *"15 faculty, of whom 3 work on early visual processing and 12 do not; the most important listeners are my two committee members plus the department chair"* has concrete constraints.

### Q2. What does the speaker want this talk to accomplish?

Concrete, not "communicate my research." Examples:

- "Get my committee to sign off on proposing my dissertation."
- "Recruit one collaborator for the behavioral extension."
- "Signal that I'm ready for the job market."
- "Land the core result hard enough that it gets mentioned at lunch."

Multiple goals are allowed but must be ranked. The goal shapes what the core message is and how boldly it is stated.

### Q3. What is the one sentence every audience member should remember?

Ask for one sentence, written down, in the user's voice. Push back on:

- Sentences that are actually two sentences ("we built X and showed Y").
- Sentences that are topics not claims ("the role of LGN in active vision").
- Sentences that are hedged into meaninglessness ("LGN may play a role in active vision").

A good core message is a definite claim the user is willing to defend. (Internally you should be able to recognize one when you see it — e.g., a construction like *"X is actively reshaped by Y, which means Z is not a passive relay"* is a well-formed claim. Do **not** offer an example sentence to the user. Offering a starter, even when flagged as "rewrite in your own words," anchors the user to your phrasing and obscures whether the speaker has actually settled the message. Make them generate the sentence; only react after they do.)

If the user cannot state the sentence, the talk is not ready. Iterate on this question — it often uncovers that the speaker has not yet decided what the talk is actually about. Do not paper over this by writing a sentence for them and asking them to approve it.

### Q4. What is the prerequisite-knowledge map?

List every concept, term, technique, or piece of context the core message *relies on*. For each, classify:

- **Shared** — the audience already has this. Use freely.
- **Build** — the audience does not have this. The talk must earn it before use.
- **Skip** — the audience does not have this, but it is not essential to the core message. Avoid mentioning it.

The **Build list** is the most important output of Stage 1. It becomes the list of stepping stones the Storyline must weave into the forward narrative.

Do not let the build list blow up. If it exceeds ~6 items, the core message is probably too ambitious for the audience; revisit Q3.

---

## What frame.md looks like

```markdown
# Frame — [Talk Title]

## Audience
- Occasion: [seminar / defense / conference / faculty talk]
- Size: [~N]
- Subfields represented: [...]
- Experts in this specific topic: [names or roles, count]
- Generalists: [count]
- Most important listeners: [2–3 names/roles]

## Goal
[One sentence, concrete.]

## Core message
> [One sentence in the speaker's voice.]

## Prerequisite knowledge map

### Shared (audience already has)
- [concept]
- [concept]

### Build (talk must earn these before using)
- [concept] — [one-line note on how / where to earn it]
- [concept] — [...]

### Skip (not essential — avoid)
- [concept]
```

---

## Signals the Frame is not done

- User cannot state the core message in one sentence.
- User has not specified which individuals matter most.
- Build list is empty (implausible) or larger than ~6 (scope too broad).
- Goal is "communicate my research" or similarly generic.

When any of these are true, stay in Stage 1. Do not advance.
