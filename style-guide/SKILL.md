---
name: style-guide
description: **MUST INVOKE** when **writing**, **drafting**, or **editing** any public-facing text (manuscripts, blogs, emails, grants) to enforce voice standards and eliminate AI writing patterns.
---

# Style Guide

## Overview

Enforce voice standards and eliminate AI writing patterns from public-facing prose. This skill fires independently via skills-prelude whenever the agent is about to produce or edit text intended for an audience. It does not apply to internal artifacts (plans, lab journals, commit messages, code comments, task descriptions).

## Context Inference

Infer the writing register from the conversation. Do not ask the user.

- **Manuscript** (default): `literature-writer` active, writing paper sections, scientific content
- **Blog**: user says "blog post", "blog", informal science communication
- **Email**: user says "email", "message to", correspondence
- **Grant**: user says "grant", "proposal", "specific aims"

If ambiguous, default to manuscript.

## Voice Principles

These are shared across all contexts.

1. **Calm, direct, information-dense.** No decorative sentences.
2. **Adjectives earn their place or get cut.** Every modifier must carry information the reader needs.
3. **Transitions mark real logical moves, not theatrical ones.** "However" is fine when there's a genuine contrast. "But here's the thing:" is theater.
4. **Let content carry its own weight.** Never announce importance — demonstrate it.
5. **Trust the reader.** No softening, hand-holding, or justification for why you're telling them something. State facts directly.
6. **Name the actor.** Prefer human subjects doing things over inanimate objects performing human actions. (Relaxed for manuscripts — "The model predicts..." is fine in scientific register.)
7. **Vary rhythm.** Mix sentence lengths. Don't stack short punchy fragments. Don't let every paragraph end the same way.
8. **Be specific.** No vague declaratives ("The implications are significant"). Name the specific thing.

## Context-Specific Adjustments

These document where each register relaxes or tightens the shared rules.

### Manuscript
- Passive voice is acceptable when the actor is irrelevant ("Stimuli were presented at 60 Hz") or convention demands it (Methods sections)
- Inanimate subjects performing domain verbs are fine ("The model predicts...", "These results suggest...", "The data indicate...")
- Precision hedging is expected — "approximately", "predominantly", "in most cases" are not filler, they're accuracy
- Em-dashes are acceptable
- No "you" address

### Blog
- Full shared rules apply — active voice, human subjects, no em-dashes
- "You" address encouraged
- Conversational tone is fine when it serves clarity, not when it's performative
- Humor and personality are acceptable; slop is not

### Email
- Brevity over style — short sentences, short paragraphs
- Shared blacklist still applies (no throat-clearing, no stacked intensifiers)
- Rhythm and structure rules relaxed — emails don't need varied paragraph endings
- Professional tone; skip the voice-principle policing beyond "be direct"

### Grant
- Follows manuscript rules with one addition: claims about significance and impact are expected, but must be specific ("This will enable X" not "This will be transformative")
- Active voice preferred over manuscript convention ("We will test..." not "It will be tested...")

## Blacklist

Organized by category. Severity marked per item: `CRITICAL` = never use, `HIGH` = almost never use, `MODERATE` = only with strong justification.

### Filler Phrases `CRITICAL`

Throat-clearing openers and emphasis crutches. Cut and state the point directly.

- "Here's the thing:"
- "Here's what/this/that [X]"
- "Here's why [X]"
- "The uncomfortable truth is..."
- "It turns out"
- "The real [X] is"
- "Let me be clear"
- "The truth is,"
- "I'll say it again:"
- "Can we talk about"
- "Here's what I find interesting"
- "Here's the problem though"
- "Full stop." / "Period."
- "Let that sink in."
- "This matters because"
- "Make no mistake"
- "Here's why that matters"
- "Now, more than ever..."
- "In today's [X]"
- "At its core"
- "At the end of the day"
- "When it comes to"
- "In a world where"
- "The reality is"

### Structures `CRITICAL`

Formulaic patterns that telegraph AI authorship.

| Pattern | Example |
|---------|---------|
| Binary contrast / false reframe | "It's not X, it's Y" / "Not about X — about Y" |
| Negative listing | "Not a X... Not a Y... A Z." |
| Corrective escalation | "It's not just X; it's Y" |
| Fragment pivot | "They ran it three times. The result? Nothing worked." |
| Weighty pivot | "But here's the thing:" / "And yet." / "But here's the catch:" |
| Rhetorical question as transition | "So what does this mean? Let's explore." |
| Enumerated profundity | "There are three things you need to understand about X" |
| Dramatic fragmentation | "[Noun]. That's it. That's the [thing]." |
| Symmetrical antithesis | "Not about X — about Y" |
| Rhetorical setup | "What if [reframe]?" / "Think about it:" |
| Epiphanic closing | "In the end, maybe the real X was the Y we made..." |

### Vocabulary `CRITICAL`

Words and phrases that signal AI-generated text.

| Category | Examples |
|----------|---------|
| Forced intensifiers | absolutely, literally, incredibly, utterly, truly, genuinely |
| Stacked intensifiers | "truly remarkable, genuinely unprecedented" |
| Hedged superlatives | "could be one of the most significant..." |
| Lexical gentrification | leverage, synergy, paradigm shift, unpack, scaffold |
| Hollow adjectives | novel, powerful, robust, challenging, non-trivial |
| Business jargon | navigate (challenges), lean into, game-changer, deep dive, double down, circle back, on the same page |
| Filler adverbs | really, just, literally, genuinely, honestly, simply, actually, deeply, truly, fundamentally, inherently, inevitably |

### Self-Reference & Meta-Commentary `CRITICAL`

Text that announces its own structure or importance.

- "In this section, we'll..."
- "As we'll see..."
- "Let me walk you through..."
- "The rest of this essay explains..."
- "This is where it gets interesting"
- "That's the real story"
- "What most people miss is..."
- "Why It Matters" (as a section header or standalone sentence)
- "Hint:" / "Plot twist:" / "Spoiler:"
- "But that's another post"
- "I want to explore..."

### Colons & Em-Dashes `HIGH`

LLMs overuse both as structural crutches. Neither is banned, but each must be justified. If the same meaning and style can be achieved with a period, comma, or restructured sentence, prefer that. Before delivering prose, check: could this colon or em-dash be replaced without losing clarity or rhythm? If yes, replace it.

Em-dashes are more acceptable in manuscript register where they're conventional. Still prefer alternatives when equivalent.

### Stacked Synonyms & Triplets `HIGH`

Redundant groupings that pad rather than clarify.

- "fundamental, foundational, and far-reaching"
- "Fast. Reliable. Scalable."
- Three-item lists where two would do

### Performative Hedging `HIGH`

False modesty or manufactured sincerity.

- "It's worth noting that..."
- "Importantly,..."
- "Interestingly,..."
- "Notably,..."
- "Of course, not everyone agrees. And that's okay."
- "This is genuinely hard"
- "I promise"

### Vague Declaratives `HIGH`

Sentences that announce importance without naming the specific thing.

- "The reasons are structural"
- "The implications are significant"
- "The stakes are high"
- "The consequences are real"
- "This is the deepest problem"

If a sentence says something is important without showing the specific thing, cut it or replace it with the specific thing.

### Nominalization Bloat `MODERATE`

Turning verbs into noun phrases. "the implementation of this methodology enables the facilitation of" — just say what was done.

### Cascading Relative Clauses `MODERATE`

Multiple nested "which/that" clauses. Break into separate sentences.

### Editorial Adverbs `MODERATE`

Interestingly, Notably, Remarkably, Crucially — only with strong justification in manuscript context. Never in blog or email.

### Closers `MODERATE`

- Paving-the-way: "This paves the way for future work."
- Epiphanic: "In the end, maybe the real X was the Y we made..."
- Self-congratulatory: "We believe this represents a significant contribution."
- Falsely modest: "While only a small step, this could be a paradigm shift."

## Quick Checks

Run this checklist before delivering any prose.

- Any filler phrases or throat-clearing? Cut to the point.
- Any binary contrasts or false reframes? State the positive claim directly.
- Any blacklisted vocabulary (intensifiers, hollow adjectives, business jargon)? Replace with specific language.
- Any self-referential meta-commentary? Delete.
- Any stacked synonyms or triplets? Reduce to one or two items.
- Any vague declaratives? Name the specific thing.
- Any unnecessary colons or em-dashes? Restructure the sentence.
- Any passive voice? (Manuscript: acceptable when conventional. Blog/email: find the actor.)
- Inanimate thing doing a human verb? (Manuscript: acceptable for domain conventions. Blog: name the person.)
- Three consecutive sentences match length? Break one.
- Any paragraph end with a punchy one-liner? Vary it.
- Does any sentence sound like a pull-quote? Rewrite it.
- Any adverbs? (Manuscript: keep precision hedges like "approximately". Cut filler like "interestingly".)
