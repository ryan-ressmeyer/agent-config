# Stages 3 and 4: Slide Authoring in Marp

Stages 3 and 4 produce and refine a single `slides.md` file. Stage 3 fixes the spoken structure of the talk — titles, speaker notes, and transitions — with **no figures**. Stage 4 layers figure placeholders, progressive reveals, and visual polish on top of that structure.

This two-pass workflow exists because the talk is a spoken performance. If visuals are drafted at the same time as spoken flow, the visuals colonize the iteration: the user tweaks the picture instead of the argument. Decoupling them keeps the argument first.

---

## Per-slide unit

Every slide is one unit of argument, with three parts:

1. **Title** — a short directive clause stating what the slide is about.
2. **Evidence** — one visual that proves the claim. In Stage 3 this is a `FIGURE:` description comment; in Stage 4 it becomes a placeholder image tag.
3. **Spoken frame** — what the speaker says on approach and on departure, plus the moment-of-delivery notes they need. Lives in HTML comments.

If any of the three is missing, the slide isn't done. If the evidence supports two distinct claims, the slide is two slides.

---

## The title

**A short, direct clause.** Typically a noun phrase or compact sentence fragment, 3–8 words, one line on the rendered slide. Non-colloquial. The *full declarative claim* belongs in the speaker's mouth (transitions and notes), not on the slide.

### Good

- *"Perisaccadic RF anisotropy"*
- *"Gene Y repression by Protein X"*
- *"Vulkan pipeline latency"*
- *"Why classical models fail here"*

### Bad (topical — fails the "what is this slide about" test)

- *"Results"*
- *"Regulation"*
- *"Benchmarks"*

### Bad (full declarative sentence — wraps to two lines, crowds the figure)

- *"LGN receptive fields elongate along the saccade axis during free viewing."*
- *"Protein X represses Gene Y in postmitotic neurons, as shown by qPCR and ChIP-seq."*

### Bad (hedged or colloquial)

- *"RFs may kind of be affected sometimes"*
- *"A really cool thing about LGN"*

### The rare exception

For a deliberate rhetorical landing slide (often the hook or the closing claim), a full declarative sentence as title can work — the sentence *is* the slide. Use this once or twice in a talk, never as the default.

---

## The visual

**One image per slide, chosen to prove exactly the claim named in the title.**

### Stage 3: figure description only

In the first pass, every slide has a `FIGURE:` HTML comment instead of an image tag:

```markdown
---

## Perisaccadic RF anisotropy

<!--
FIGURE: scatter of along-axis vs. orthogonal RF extent for all 347 units.
Unity line dashed. Marginal histograms on both axes. Color by animal.
Audience should notice in ~2 s that most points lie above the unity line.
-->

<!--
SPEAKER NOTES
- [notes]

TRANSITION IN: [...]
TRANSITION OUT: [...]
-->
```

This keeps the user's attention on the argument. No image work happens until Stage 4.

### Stage 4: placeholder image tag

In the second pass, replace the `FIGURE:` description with a placeholder tag, keeping the description directly below it so the user knows what to produce:

```markdown
![width:700px](figures/TODO-rf-anisotropy-scatter.png)

<!--
FIGURE: scatter of along-axis vs. orthogonal RF extent for all 347 units.
Unity line dashed. Marginal histograms on both axes. Color by animal.
Audience should notice in ~2 s that most points lie above the unity line.
-->
```

### Visual rules (both passes)

- **If you will not explain it, delete it.** Every axis, label, and legend entry must correspond to something the speaker will say.
- **Never paste a published figure untouched.** Crop, relabel, recolor. The published figure was optimized for a reader with infinite time; the talk figure is optimized for a 60-second glance.
- **Build up complex figures** via progressive reveals (see below).
- **No red-green pairs. No 3D chart effects. No gridlines unless they carry meaning.**
- **Never invent figure content.** Every figure in `slides.md` is a placeholder the user fills in.

---

## The spoken frame

Lives entirely in HTML comments on the slide. Marp renders HTML comments as presenter notes in presenter mode.

### Structure

```markdown
<!--
SPEAKER NOTES
- Specific numbers: n = 347 units across 3 monkeys.
- Pause after the title. Let the scatter land.
- If asked "is this just retinal motion?" forward-reference the passive-replay control.

TRANSITION IN: So under passive fixation, the RFs look classical. What happens when the monkey is freely viewing?
TRANSITION OUT: The anisotropy is clear in the population. Is it present in single units, trial by trial?
-->
```

### Transition in

One sentence the speaker says **before** revealing this slide. A question or setup that the current slide answers — the bridge from the previous slide.

### Transition out

One sentence the speaker says **while moving to** the next slide. Both lands this slide's claim and sets up the next.

**Transitions are spoken, not read.** They never appear on the slide surface. Putting them on the slide duplicates what the speaker says and violates the "slide is not a teleprompter" rule.

### Speaker notes

2–4 bullets of *what the speaker needs in the moment but wouldn't want to say by rote*:

- Specific numbers that are easy to misremember.
- Pre-empts for the skeptic question the speaker expects here.
- Pacing cues ("pause after 'is not a passive relay'").
- Phrasing for a hard-to-explain concept.

Notes are **not** a script. They are what the speaker glances at while speaking.

---

## Marp basics

A Marp file is a markdown document with YAML frontmatter that enables Marp rendering. Slides are separated by horizontal rules (`---`). Marp supports directives (front-matter and per-slide), HTML comments as speaker notes, and standard markdown with a slide-aware CSS layer.

### Minimal frontmatter

```markdown
---
marp: true
theme: flexoki-dark
paginate: true
math: katex
---
```

| Directive | Purpose |
|-----------|---------|
| `marp: true` | Required — enables Marp rendering. |
| `theme: flexoki-dark` | Locked-in house theme. Alternative: `flexoki-light`. Do not use `default`. |
| `paginate: true` | Page numbers. |
| `math: katex` | Enables KaTeX math rendering (for equations). |

### Locked-in visual style

The skill ships `assets/themes/flexoki-dark.css`, `assets/themes/flexoki-light.css`, bundled Inter woff2 files, and a `marprc.yml.template`. These are **not** Stage 3 or 4 authoring decisions — they are copied verbatim into every new presentation at the start of Stage 3:

```
cp -r <skill>/assets/themes  <presentation>/themes
cp    <skill>/assets/marprc.yml.template  <presentation>/.marprc.yml
```

The presentation then has:

```
<presentation>/
├── themes/
│   ├── flexoki-dark.css
│   ├── flexoki-light.css
│   └── fonts/
│       ├── InterVariable.woff2
│       └── InterVariable-Italic.woff2
├── .marprc.yml          # registers themes/, enables allowLocalFiles
└── slides.md            # frontmatter picks flexoki-dark or flexoki-light
```

**Critical:** `.marprc.yml` must set `allowLocalFiles: true`. Without it, Chromium blocks the local woff2 URL during rendering and the deck falls back to a system sans-serif silently.

### Picking a theme

- `flexoki-dark` — default. Paper-black background, base-200 text, 400-series accents. Best for projected talks in darkened rooms. Kinder to photographic figures and fluorescence microscopy.
- `flexoki-light` — paper (#FFFCF0) background, base-900 text, 600-series accents. Best for bright rooms and decks that will also be printed or shared as PDFs.

Swap themes by editing one line in frontmatter. Do not hand-edit palette values or author a per-talk theme. If the talk needs more semantic handles (e.g. `--rgc`, `--lgn`), define them in the slides.md `<style>` block using existing `var(--*)` references.

### Per-slide directives

```markdown
---
<!-- _class: dark -->
<!-- _backgroundColor: #000 -->

# Fluorescence image slide
```

Use sparingly. Apply classes only where the slide's content actually requires it (e.g., a dark background for a microscopy slide).

---

## Slide template

```markdown
---

## [Short directive title — 3–8 words]

![width:700px](figures/TODO-descriptive-name.png)   <!-- Stage 4 only -->

<!--
FIGURE: [what this figure should contain, axes, annotations, what the audience looks at first]

SPEAKER NOTES
- [specific number / pacing cue / skeptic pre-empt]
- [...]

TRANSITION IN: [one sentence spoken before this slide]
TRANSITION OUT: [one sentence spoken moving to the next slide]
-->
```

In Stage 3 the `![width:...](...)` line is omitted; only the `FIGURE:` comment appears. In Stage 4 the image tag is added above the comment.

---

## Progressive reveals (builds) — Stage 4

Marp's support for progressive reveals is weaker than Keynote/PowerPoint, but three patterns work.

### Pattern A — one-reveal-per-slide (simplest, always works)

Duplicate the slide, adding one element at a time.

```markdown
---

## Anisotropy time course

![width:700px](figures/TODO-anisotropy-timecourse-panel1.png)

<!-- BUILD: panel 1 — raw time course only -->

---

## Anisotropy time course

![width:700px](figures/TODO-anisotropy-timecourse-panel2.png)

<!-- BUILD: panel 2 — add shaded 95% CI -->
```

### Pattern B — CSS fragments

```markdown
![width:700px](figures/TODO-anisotropy-timecourse.png)

<!-- BUILD: reveal panel 2 (shaded CI) on advance -->
<!-- BUILD: reveal annotation arrows on next advance -->
```

`BUILD:` comments are informational markers at Stage 4; they become real fragments when the theme is wired for it or when the user swaps to Pattern A.

### Pattern C — pre-rendered animated figure

```markdown
![width:700px](figures/TODO-eye-trace-animation.mp4)
```

Flag Pattern C to the user so they know they need to pre-render.

### Which to use

- Default to Pattern A.
- Mark Pattern B sites with `BUILD:` comments for later CSS-driven builds.
- Flag Pattern C figures to the user.

---

## Animated figures (videos) — Stage 4

For videos that should *play under speaker control* (not start automatically the moment the slide appears), the deck ships a small JS controller — `marp-video-controls.js` — copied alongside `themes/` and `.marprc.yml` at Stage 3. The slides template loads it via a `<script src="./marp-video-controls.js"></script>` tag at the bottom of `slides.md`, which passes through to the rendered HTML thanks to `options.html: true` in `.marprc.yml` and the `--html` flag in `build.sh`. It enables two HTML attributes on `<video>` tags:

| Attribute | Behavior |
|-----------|----------|
| `data-play-from-start` | Autoplay from frame 0 each time the slide becomes active. Pause + rewind when the slide goes inactive. Use when the speaker wants the video already running on arrival. |
| `data-play-then-advance` | Show frame 0 on entry. The next advance keypress on this slide *plays the video* (and is consumed — does not advance). The press after that advances normally. Going back resets the played flag. Use when the speaker wants to land on a still frame, deliver a setup line, then trigger playback at a deliberate moment. |

**Prefer `data-play-then-advance`** for any video the speaker introduces verbally. It collapses what would otherwise be two duplicate slides (one paused, one autoplay) into one slide. The previous duplicate-slide pattern is now a code smell — replace it.

### Markup

```markdown
---

## The eye jumps ~3 times a second

<video src="assets/free-viewing-eye.webm" data-play-then-advance loop muted playsinline
       style="width: 80%; max-height: 65vh; display: block; margin: 0 auto;"></video>

<!--
SPEAKER NOTES
- Land on the still frame and deliver the transition-in line.
- Press advance once to start the video — let it run silently for ~3 s.
- ...

TRANSITION IN: "..."
TRANSITION OUT: "..."
-->
```

Required attributes on the `<video>` tag:

- `muted` — required for programmatic playback under browser autoplay policy.
- `playsinline` — keeps the video inline rather than going fullscreen on some browsers.
- `loop` — usually wanted; the video keeps looping while the slide is shown.
- One of `data-play-from-start` or `data-play-then-advance`.

Inline `style="width: ...; max-height: ...; display: block; margin: 0 auto;"` is the canonical layout. The width and max-height keep the element sized correctly even if the resource is briefly unloaded.

### Build wiring

The deck root must contain three files (all copied at Stage 3 from the skill's `assets/`):

```
<presentation>/
├── themes/                    # locked-in visual style
├── .marprc.yml                # registers themes/, allowLocalFiles, html: true
├── marp-video-controls.js     # video controller — loaded by <script src> in slides.md
└── build.sh                   # marp-cli driver
```

`slides.md` ends with `<script src="./marp-video-controls.js"></script>`. Because `.marprc.yml` sets `options.html: true` and `build.sh` passes `--html`, marp-cli emits the `<script>` tag verbatim into `slides.html`, which loads the controller at runtime. The script is inert during PDF rendering. Editing `marp-video-controls.js` takes effect on the next deck reload — no rebuild step required.

### Common pitfalls

- **Selector by class only, never by element.** Marp wraps each slide in `<svg><foreignObject><section>…</section></foreignObject></svg>`, and bespoke applies `bespoke-marp-active` / `bespoke-marp-slide` to the `<svg>`, not the `<section>`. Selecting `section.bespoke-marp-active` matches nothing. The shipped controller already gets this right; do not "simplify" it.
- **Do not call `v.load()` before `v.play()`.** `load()` unloads the current resource, drops the element's intrinsic aspect ratio for one frame, and produces a visible layout reflow (video collapses to the HTML5 default 300×150, surrounding content shifts). `currentTime = 0` is sufficient.
- **The keydown listener uses capture phase.** Bespoke binds advance keys at the bubble phase on `document`. The controller registers with `{ capture: true }` and calls `stopImmediatePropagation()` to consume the press. Capture is required — bubble would arrive too late.
- **PDF export does not animate.** Videos play in `slides.html` only. The PDF shows the first frame.

---

## Figure directory convention

Create a `figures/` subdirectory next to `slides.md`. At the end of Stage 4, place a `figures/README.md` listing each `TODO-*.png` filename and what the figure should be — this becomes the user's checklist of figures to produce.

---

## Per-slide self-check (both stages)

Before declaring a slide done:

- [ ] Title is a short directive clause, one line on the rendered slide.
- [ ] One claim per slide (no "and" joining two distinct takeaways).
- [ ] Visual described precisely enough that the user can tell whether their existing figure fits or a new one is needed.
- [ ] Every axis/label/panel on the visual has a sentence the speaker will say about it. Otherwise, the element is cut or the slide is built progressively.
- [ ] Transition-in and transition-out are one sentence each.
- [ ] Speaker notes contain at least one of: a specific number, a skeptic pre-empt, or a pacing cue.
- [ ] The slide is a step in the Storyline arc — trace it back to a beat or dive.

### Stage 4 only

- [ ] Every `FIGURE:` comment now has a `![](figures/TODO-*.png)` tag above it.
- [ ] Progressive-reveal points are marked (duplicated slides or `BUILD:` comments).
- [ ] Summary and acknowledgments slides present.
- [ ] `figures/README.md` lists every `TODO-*` filename.

---

## Slide-count sanity check

Rough rule: **60–90 seconds per slide** for a technical talk, including transitions and pauses. A 30-minute talk is therefore ~20–30 slides, not 50.

If the deck is producing more slides than the time budget allows, the talk either has too many dives or individual dives are over-built. Revisit Storyline and prune.

---

## Rendering the deck

The deck should be renderable at any point during Stages 3 and 4 — rendering is the fastest way to catch title overflow, figure sizing, and layout bugs. Render whenever it helps verify the work; don't wait until Stage 4 is "done."

```
npx @marp-team/marp-cli slides.md --pdf    # visual-hygiene pass
npx @marp-team/marp-cli slides.md --html   # delivery format; preserves fragments/transitions
```

marp-cli auto-discovers `.marprc.yml` in the current directory, so theme registration and `allowLocalFiles` are picked up automatically. Do not invent additional CLI flags.

**When to render:**
- After writing an initial batch of Stage 3 slides, to confirm titles don't wrap and speaker-note comments aren't leaking onto the slide face.
- After Stage 4 figure placeholders are added, to confirm sizing directives work.
- Any time the user reports something looks wrong — render, open the PDF, and verify directly rather than guessing.

---

## Post-Stage-4 rehearsal suggestion

After Stage 4, close with a **suggestion** (not a requirement):

> The skeleton is ready. The next productive step is to rehearse the talk aloud once, with the deck visible, speaking the transitions from the notes rather than reading them. Time it. Note any slide where you stumbled, any transition that felt forced, any moment where you wanted a slide you don't have.
>
> When you come back, use `presentation-editing` with your rehearsal notes in hand.

Do not block progress on rehearsal — the user will decide when they're ready.
