---
name: marp-presentation-reference
description: Use when a task needs facts or usage guidance about Ryan's Marp presentation format, including slides.md, script.md, slide identifiers, speaker-note routing, figures, videos, progressive reveals, themes, build tools, rendering, or editing an existing deck.
---

# Marp Presentation Reference

Ryan's presentation format separates slide content from the spoken script and compiles both into a rendered Marp deck. Use this reference for authoring, editing, repairing, or rendering an existing presentation. Use `presentation-planning` when the task is to develop a talk collaboratively from framing through storyline and slides.

Read [marp-conventions.md](marp-conventions.md) for detailed slide, figure, video, visual-style, and spoken-prose conventions.

## Canonical artifacts

- `slides.md` contains slide content, Marp directives, stable slide identifiers, and visual references.
- During early construction, inline `SPEAKER NOTES` and `TRANSITION IN/OUT` comments are the spoken-frame source.
- Once `script.md` exists, it is the canonical spoken script. Inline scaffolding should then be removed from `slides.md`.
- `script.md` routes prose with `## @<selector>` blocks. A selector may identify one slide, an inclusive range, or comma-separated selections.
- The generated output deck is not an authoring source. Edit `slides.md` or `script.md`, then rebuild.

## Slide identifiers and script routing

A slide receives an identifier from its first heading. Use `<!-- _id: explicit-slug -->` when titles repeat, when an automatic slug is awkward, or when a stable external selector is needed.

A script block has the form:

```markdown
## @slide-id

Spoken prose for this slide.
```

Continuous build sequences can share one block through an inclusive selector such as `## @first..last`. `(→)` and `(play)` are presenter cues preserved in the script but ignored by the compiler.

After structural slide changes, validate and normalize script coverage:

```bash
uv run tools/script_format.py --dry-run
uv run tools/script_format.py
```

`--init` creates a new script scaffold from current slide identifiers.

## Build system

A presentation directory normally contains:

- `build.sh` — compile and render driver;
- `tools/compile.py` — combines slides and script;
- `tools/slide_summary.py` — low-token slide index;
- `tools/script_format.py` — selector validation and ordering;
- `.marprc.yml` — Marp configuration;
- `themes/` — Flexoki themes and bundled Inter fonts;
- `marp-video-controls.js` — controlled video playback.

Render through the project driver:

```bash
./build.sh
./build.sh -o alternate-name
```

Do not render `slides.md` directly with Marp after `script.md` exists; doing so omits the compiled speaker notes. Run `tools/slide_summary.py slides.md` before reading a large existing deck when a concise structural overview is sufficient.

## Visual identity

The house style is Flexoki with bundled Inter variable fonts:

- `flexoki-dark` is the default for projected talks and photographic or fluorescence imagery.
- `flexoki-light` is available for bright rooms and print-oriented output.

Keep `.marprc.yml` configured with local-file access so Chromium can load bundled fonts. Reuse palette variables instead of creating a per-talk theme. Presentation-specific semantic colors may map new names to existing theme variables.

## Figures

- One argumentative unit and one primary visual per slide.
- Preserve image aspect ratio. Prefer one constrained dimension or `max-width` plus `max-height` with automatic width/height.
- Do not use `vh` or `vw`; Marp uses a fixed slide canvas that is scaled into the browser viewport.
- Keep axis units and figure typography consistent across the deck.
- Match a generated figure's native dimensions to its intended slide-width fraction so text renders consistently.
- Put presentation-local figures and videos in the deck's `assets/` directory.

The detailed sizing rules and matplotlib/SVG conventions are in `marp-conventions.md`.

## Progressive reveals and video

Prefer duplicated slides for the simplest reliable progressive reveal. `BUILD:` comments can mark future fragment behavior. Pre-rendered animations are appropriate when the visual itself changes continuously.

For controlled videos, use the shipped controller and the documented `data-play-from-start` or `data-play-then-advance` attributes. Video playback is available in HTML; PDF output shows a static frame.

## Spoken prose

`script.md` is speech, not manuscript prose. Use short breathable sentences, explicit visual walkthroughs, and enough repetition for an audience that cannot reread. When asked to slow down, add sentences and explanatory beats rather than packing more qualifications into existing clauses.

## Verification after edits

When an edit changes a figure-generating script, regenerate the asset. When it changes slide structure, validate script selectors. When it changes slides, script, or embedded assets, run `./build.sh` and inspect the relevant rendered output. A source diff alone does not verify a presentation edit.

## Resource ownership

New-deck templates, themes, build tools, and other executable resources remain owned by the `presentation-planning` workflow under its `assets/` directory. A deck created by that workflow carries its own copies, so later editing relies on the deck-local resources rather than the installed skill.
