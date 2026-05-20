# Stages 3–5: Slide Authoring in Marp

> **Where the spoken frame lives.** During slide construction (Stages 3 and 4), the spoken frame lives **inline on each slide** as a `<!-- SPEAKER NOTES … TRANSITION IN/OUT -->` comment block. This is the canonical source during construction — keeping the spoken frame visible next to the slide it belongs to is the whole point. At Stage 5, after visuals have settled, the verbatim script is written in `script.md` as `## @<selector>` blocks and the inline scaffolding is deleted. From Stage 5 onward, `script.md` is the source of truth and `tools/compile.py` strips any leftover inline blocks with a warning. See the **Build system** section in `SKILL.md`.

Stage 3 produces a no-image `slides.md` skeleton: titles, `FIGURE:` description comments, inline scaffolding notes. Stage 4 layers visuals — image tags pointing into the deck's `assets/` directory, progressive reveals, polish — while continuing to revise slide order, titles, and inline notes as visuals reveal what works. Stage 5 writes `script.md` once the deck is visually settled.

The skeleton-first sequencing exists because the talk is a spoken performance. Drafting figures before titles and a spoken frame lets the visuals colonize the iteration: the user tweaks the picture instead of the argument. Once a skeleton exists, visuals and flow co-iterate productively in Stage 4 — the structure is no longer hostage to whichever figure was drawn first.

---

## Per-slide unit

Every slide is one unit of argument, with three parts:

1. **Title** — a short directive clause stating what the slide is about.
2. **Evidence** — one visual that proves the claim. In Stage 3 this is a `FIGURE:` description comment; in Stage 4 it becomes a placeholder image tag pointing into `assets/`.
3. **Spoken frame** — what the speaker says on approach and on departure, plus the moment-of-delivery notes they need. Lives inline as `<!-- SPEAKER NOTES / TRANSITION IN / TRANSITION OUT -->` comment blocks during Stages 3–4; migrates into `script.md` blocks at Stage 5.

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

In the second pass, replace the `FIGURE:` description with a placeholder tag pointing into the deck's `assets/` directory, keeping the description directly below it so the user knows what to produce:

```markdown
![width:700px](assets/TODO-rf-anisotropy-scatter.png)

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
- **Never stretch images.** Aspect ratio must be preserved. On `<img>` tags, do not combine `width: X%` with `max-height: Ypx` — when the natural height at that width exceeds the max, the browser clamps height while leaving width fixed and the image is squished. Use `max-width` + `max-height` (with `width: auto; height: auto`) so both bounds preserve intrinsic aspect ratio. Canonical sizing for an inline image:

  ```html
  <img src="..." alt="..."
       style="max-width: 80%; max-height: 468px; width: auto; height: auto; display: block; margin: 0 auto;">
  ```

  Only one constrained dimension (`width: 80%` alone, or `height: 432px` alone) is also safe. Two constrained dimensions on `<img>` is the failure mode. Videos behave the same way in principle, but typically render at their intrinsic aspect ratio inside the box; still prefer `max-width` + `max-height` if a video aspect mismatch ever appears.

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

The skill ships `assets/themes/flexoki-dark.css`, `assets/themes/flexoki-light.css`, bundled Inter woff2 files, and a `marprc.yml.template`. These are **not** authoring decisions — they are copied verbatim into every new presentation at the start of Stage 3:

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

![width:700px](assets/TODO-descriptive-name.png)   <!-- Stage 4 onward -->

<!--
FIGURE: [what this figure should contain, axes, annotations, what the audience looks at first]

SPEAKER NOTES
- [specific number / pacing cue / skeptic pre-empt]
- [...]

TRANSITION IN: [one sentence spoken before this slide]
TRANSITION OUT: [one sentence spoken moving to the next slide]
-->
```

In Stage 3 the `![width:...](...)` line is omitted; only the `FIGURE:` comment appears. The inline `SPEAKER NOTES` / `TRANSITION IN/OUT` block is the canonical spoken frame throughout Stages 3–4. In Stage 4 the image tag is added above the FIGURE comment. At Stage 5 the inline `SPEAKER NOTES` / `TRANSITION` block is removed from the slide and rewritten as a `## @<selector>` block in `script.md`.

---

## Progressive reveals (builds) — Stage 4

Marp's support for progressive reveals is weaker than Keynote/PowerPoint, but three patterns work.

### Pattern A — one-reveal-per-slide (simplest, always works)

Duplicate the slide, adding one element at a time.

```markdown
---

## Anisotropy time course

![width:700px](assets/TODO-anisotropy-timecourse-panel1.png)

<!-- BUILD: panel 1 — raw time course only -->

---

## Anisotropy time course

![width:700px](assets/TODO-anisotropy-timecourse-panel2.png)

<!-- BUILD: panel 2 — add shaded 95% CI -->
```

### Pattern B — CSS fragments

```markdown
![width:700px](assets/TODO-anisotropy-timecourse.png)

<!-- BUILD: reveal panel 2 (shaded CI) on advance -->
<!-- BUILD: reveal annotation arrows on next advance -->
```

`BUILD:` comments are informational markers at Stage 4; they become real fragments when the theme is wired for it or when the user swaps to Pattern A.

### Pattern C — pre-rendered animated figure

```markdown
![width:700px](assets/TODO-eye-trace-animation.mp4)
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
       style="width: 80%; max-height: 468px; display: block; margin: 0 auto;"></video>

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

Inline `style="width: ...; max-height: ...; display: block; margin: 0 auto;"` is the canonical layout for `<video>` (videos render at intrinsic aspect ratio inside that box). For `<img>`, use `max-width` + `max-height` with `width: auto; height: auto;` instead — see "Never stretch images" in the Visual rules section above. The width and max-height keep the element sized correctly even if the resource is briefly unloaded.

### Sizing units — never use `vh`/`vw`

Marp's slide `<section>` is a fixed-size canvas (default **1280×720 px**, 16:9). The HTML renderer scales the whole slide as a unit to fit the browser. But `vh`/`vw` resolve against the **browser viewport**, not the slide — so an element styled `height: 65vh` re-sizes when the deck is opened on a different display while the slide canvas around it is scaled differently. The result: layout drifts between machines/resolutions.

Always size figures, videos, and other inline media with **px values matched to the 720 px slide height** (or `%` of an explicitly-sized parent). Reference conversions for the default 1280×720 canvas:

| viewport intent | px on 720-tall slide |
|---|---|
| 65vh | 468px |
| 60vh | 432px |
| 55vh | 396px |
| 50vh | 360px |
| 40vh | 288px |

If the deck overrides the canvas size via `theme` CSS (`@page { size: ... }` or a `section { width/height: ... }` rule), recompute against the overridden height. Percent widths (e.g. `width: 80%`) are fine — they resolve against the slide, not the viewport.

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

Create an `assets/` subdirectory next to `slides.md` and place all figure and video files there. `tools/slide_summary.py` lists every `TODO-*` filename across the deck — enough of a checklist that no separate `README.md` is required. (The skill's own `assets/` directory — where these templates live — is unrelated; only the deck-local `assets/` matters at render time.)

---

## Figure legibility — matching render to display

Declared font sizes in a matplotlib figure only land at their nominal size on the slide if the SVG renders at **1.0× scale** — i.e., the figure's native size in inches equals its on-slide display size. When that ratio drifts, fonts shrink or grow per panel and the deck looks inconsistent even though every script sets the same `fontsize`.

**Rule.** Pick a slide-width fraction for each panel and size both ends to match.

- Marp's default canvas is 1280 × 720 px = **13.333 × 7.5 inches at 96 dpi**.
- In the figure script: `figsize = (13.333 × width_frac, 13.333 × width_frac / aspect)`. Provide one helper (e.g. `slide_figsize(width_frac, aspect)`) and call it everywhere; do not hand-tune figsizes per panel.
- In `slides.md`: display the image with `style="width: <width_frac × 100>%; height: auto"`. Drop `max-height` on these panels — combining a width fraction with a pixel height clamp re-scales the SVG and undoes the alignment.
- Multi-panel layouts: set the flex/grid column width to the desired fraction and let the image be `width: 100%` of its column.

**Center font sizes in one place.** A shared style helper (e.g. `_slide_style.apply_dark_style()` invoked at the top of every render script) sets `rcParams['font.size']`, `axes.labelsize`, `xtick.labelsize`, etc. Default range that survives projector and lecture hall: **16 pt body, 18 pt axis labels, 15 pt ticks/legend.** Remove per-script `fontsize=` overrides so all panels inherit; only override locally for inset annotations.

**Pure-SVG scripts** (hand-written SVG, not matplotlib) follow the same idea: set the SVG `viewBox` width to `width_frac × 1280` and size text in those user units. These panels are the place where `width: %` + `max-height: Npx` *is* warranted (the SVG has a fixed aspect that may overflow the slide vertically) — leave the height clamp on them.

**Axis units stay consistent across the deck.** If most time axes are in milliseconds, every time axis is in milliseconds — converting one panel to seconds for a smaller number range creates a unit mismatch the audience has to translate mid-talk.

---

## Per-slide self-check (Stages 3–4)

Before declaring a slide done:

- [ ] Title is a short directive clause, one line on the rendered slide.
- [ ] One claim per slide (no "and" joining two distinct takeaways).
- [ ] Visual described precisely enough that the user can tell whether their existing figure fits or a new one is needed.
- [ ] Every axis/label/panel on the visual has a sentence the speaker will say about it. Otherwise, the element is cut or the slide is built progressively.
- [ ] Inline `TRANSITION IN:` and `TRANSITION OUT:` are one sentence each.
- [ ] Inline `SPEAKER NOTES` contain at least one of: a specific number, a skeptic pre-empt, or a pacing cue.
- [ ] The slide is a step in the Storyline arc — trace it back to a beat or dive.

### Stage 4 only

- [ ] Every `FIGURE:` comment now has a `![](assets/TODO-*.png)` tag above it.
- [ ] Progressive-reveal points are marked (duplicated slides or `BUILD:` comments).
- [ ] Summary and acknowledgments slides present.
- [ ] Figure script's `figsize` matches the slide-width fraction the image is displayed at (see "Figure legibility"). Image style is `width: <pct>%; height: auto` — no `max-height` clamp on a figure also sized by width.
- [ ] `uv run tools/slide_summary.py slides.md` lists every `TODO-*` filename without surprises.

### Stage 5 only

- [ ] Every slide id is covered by a `## @<selector>` block in `script.md`.
- [ ] Inline `SPEAKER NOTES` / `TRANSITION IN/OUT` blocks have been removed from `slides.md`.
- [ ] `./build.sh` runs clean (no warnings about stripped inline comments).
- [ ] The prose reads like speech, not like writing. See "Writing spoken prose" below.

---

## Writing spoken prose (Stage 5)

`script.md` is what the speaker says out loud while standing in front of a slide. It is **not** written prose dressed up with `(→)` markers. The rhythms that work on a page often fail at a podium, and vice versa.

### Spoken prose is longer and more expanded than written prose

Readers control their own pace and can re-read. Audiences cannot. The same idea that takes one tight sentence in a paper usually needs two or three sentences when spoken — a setup, the claim, and a moment to land — so the audience has time to absorb it before the next idea arrives.

When the slide has a figure, walk through what is on it explicitly: name the panels, the axes, the colors, what the audience should look at first. "On the slide here is the basic setup. At the top is X. Below that is Y" reads as padding on the page; live, it is the audience's lifeline.

A good heuristic: if a `script.md` block could be lifted unchanged into a methods paragraph, it is probably too compressed for speech.

### Em dashes and colons read; they don't speak

Em dashes and colons work in written prose because the reader's eye absorbs the structural break visually. Spoken aloud, both collapse into the same pause, and stacking them makes delivery choppy and breathless. A paragraph with three em dashes and two colons reads cleanly on the page and trips the speaker on every clause.

In `script.md`, prefer commas, periods, and clause-restructured sentences. An em dash that genuinely marks a strong rhetorical break is fine occasionally; a colon introducing a single short list item is fine; the failure mode is using them as a default joinery for every dependent clause.

**Before (written rhythm):**

> The key measurement we can now make is the probability of transmission. Almost every spike in the LGN relay cell is preceded by a spike from its driving RGC — that's what the tight CCG peak we saw earlier tells us. But the reverse isn't true: not every RGC spike evokes a spike in the LGN. So we can ask: of the spikes coming in, what fraction get through?

**After (spoken rhythm):**

> The idea is simple. Almost every spike in the LGN relay cell is preceded by a spike from its driving RGC. That's what the tight CCG peak we saw earlier tells us. But the reverse isn't true, since not every RGC spike evokes a spike in the LGN. So we can ask, of the spikes coming in from the retina, what fraction get through to drive a spike in the LGN.

Same content, but the dashes and colons have been replaced with periods, commas, and a restructured "since" clause. The speaker can breathe.

### When the user asks for "more detail" or "go slower," expand, don't compress

A common failure mode: when asked to slow down or add detail, an LLM adds qualifying adjectives and parenthetical clauses, which is *more written-prose density*, not more spoken pacing. The right move is to **add sentences** — explicit walkthroughs of what is on the slide, restatement of the claim in plain words, an extra beat between setup and payoff. Length comes from more clauses spoken slowly, not from more information per clause.

---

## Slide-count sanity check

Rough rule: **60–90 seconds per slide** for a technical talk, including transitions and pauses. A 30-minute talk is therefore ~20–30 slides, not 50.

If the deck is producing more slides than the time budget allows, the talk either has too many dives or individual dives are over-built. Revisit Storyline and prune.

---

## Rendering the deck

The deck should be renderable at any point during Stages 3–5 — rendering is the fastest way to catch title overflow, figure sizing, and layout bugs. Render whenever it helps verify the work; don't wait until a stage is "done."

```
./build.sh           # compile slides.md + script.md, render PDF + HTML
./build.sh -o name   # override the output basename
```

`build.sh` invokes `tools/compile.py` to splice `script.md` into `slides.md` (a no-op if `script.md` does not yet exist or is empty — which is the normal state during Stages 3–4), then runs marp-cli for HTML and PDF. **Do not** call `npx @marp-team/marp-cli slides.md --pdf` directly: at Stage 5 onward that renders the raw, unspliced `slides.md` and the deck ships with no speaker notes. marp-cli auto-discovers `.marprc.yml`, so theme registration and `allowLocalFiles` are picked up automatically.

**When to render:**
- After writing an initial batch of Stage 3 slides, to confirm titles don't wrap and inline scaffolding comments aren't leaking onto the slide face.
- After Stage 4 figure placeholders are added, to confirm sizing directives work.
- After Stage 5 migration, to confirm `script.md` is the source and no inline-comment warnings appear.
- Any time the user reports something looks wrong — render, open the PDF, and verify directly rather than guessing.

---

## Post-Stage-5 rehearsal suggestion

After Stage 5, close with a **suggestion** (not a requirement):

> The skeleton is ready. The next productive step is to rehearse the talk aloud once, with the deck visible, speaking the transitions from the notes rather than reading them. Time it. Note any slide where you stumbled, any transition that felt forced, any moment where you wanted a slide you don't have. Capture the notes in `rehearsal-notes.md` and bring them back to iterate.

Do not block progress on rehearsal — the user will decide when they're ready.
