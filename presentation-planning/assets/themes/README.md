# Flexoki + Inter — locked-in visual style

This directory ships with every new presentation created via the
`presentation-planning` skill. It defines the house visual style:

- **Color scheme:** [Flexoki](https://stephango.com/flexoki) by Steph Ango
  (`kepano/flexoki`). Full palette — base ramp plus 8 accent ramps in
  50–950 — exposed as CSS custom properties. Canonical values verified
  against `kepano/flexoki/css/flexoki.css`.
- **Typeface:** [Inter](https://rsms.me/inter/) by Rasmus Andersson.
  Variable font bundled as `fonts/InterVariable.woff2` (Regular) and
  `fonts/InterVariable-Italic.woff2` (Italic), loaded via `@font-face`
  so rendering is reproducible on any machine with marp-cli + Chromium.

## Files

```
themes/
├── flexoki-dark.css    # @theme flexoki-dark   — paper-black bg, 400 accents
├── flexoki-light.css   # @theme flexoki-light  — paper bg, 600 accents
└── fonts/
    ├── InterVariable.woff2
    └── InterVariable-Italic.woff2
```

## Usage in slides.md

```yaml
---
marp: true
theme: flexoki-dark     # or: flexoki-light
paginate: true
math: katex
---
```

The companion `.marprc.yml` at the presentation root registers this
directory and enables `allowLocalFiles` so the bundled font loads.

## Why not Google Fonts or system Inter

- System Inter is not guaranteed to exist on every rendering machine
  (e.g. conference laptops, CI, PDF export from a Docker container).
- Google Fonts `@import` requires internet at render time.

Bundling the woff2 file locally with `@font-face` is the only approach
that survives an offline laptop + a fresh Docker image + a machine
without Inter pre-installed. The two woff2 files are ~740 KB combined —
small enough to live in every deck repo.

## Semantic handles

Beyond the raw palette, each theme defines a set of semantic variables
that decks actually consume:

| Variable | Dark (400 series) | Light (600 series) | Meaning |
|----------|-------------------|--------------------|---------|
| `--bg` | `--base-black` | `--paper` | Slide canvas |
| `--bg-elev` | `--base-950` | `--base-50` | Elevated surfaces (quotes, code) |
| `--text` | `--base-200` | `--base-900` | Body copy |
| `--text-strong` | `--base-100` | `--base-black` | Headings, `<strong>` |
| `--text-mute` | `--base-500` | `--base-600` | Captions, pagination |
| `--rule` | `--base-800` | `--base-200` | Heading underlines, hr |
| `--link` | `--blue-400` | `--blue-600` | Hyperlinks |
| `--accent` | `--orange-400` | `--orange-600` | Emphasis, blockquote bar, `<em>` |

Decks are encouraged to define per-talk paper-palette handles
(e.g. `--rgc`, `--lgn`, `--transmit` in the LGN talk) on top of these.

## Editing

Do not hand-edit color values. If the canonical Flexoki palette is
updated upstream, re-pull from `kepano/flexoki/css/flexoki.css` and
re-verify all hex codes against it before committing.

The structural CSS (typography, layout, component styling) is
intentionally duplicated between dark and light — it's ~180 lines and
easier to maintain as two self-contained themes than as a shared
import with Marp's theme bundler.
