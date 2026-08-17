#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Compile slides.md + script.md into the final Marp .md (with speaker notes).

Behaviour:
- Pre-Stage-5 mode (script.md is missing or contains no `## @<selector>` blocks):
  slides.md is passed through verbatim. Inline HTML comments — including
  SPEAKER NOTES / TRANSITION IN / TRANSITION OUT scaffolding — are preserved,
  because they are the canonical spoken frame during Stages 3 and 4. Marp
  renders HTML comments as presenter notes, so the deck is delivery-usable.
- Stage 5+ mode (script.md has blocks): the script becomes the source of truth.
  - Front-matter is preserved verbatim.
  - Each slide is emitted with its original body, then HTML comments are filtered:
      * Marp directives (`<!-- _foo: ... -->`) are kept where they appeared.
      * `<!-- _id: ... -->` directives are consumed (their content is metadata).
      * `<!-- @ ... -->` author comments are silently stripped.
      * Any other HTML comment is stripped; if it had non-trivial content, a warning
        is emitted because it likely contained Stage-3/4 inline scaffolding that
        script.md is now superseding.
  - A single speaker-note HTML comment block is appended to each slide, containing
    the prose from the script.md block whose selector covers that slide.
  - Slides not covered by any script block get an empty notes block and a warning.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# When invoked as a script via `uv run`, __package__ is unset; ensure tools/ is importable.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from parser import COMMENT_RE, SlidesDoc, parse_script, parse_slides, route  # noqa: E402

# Placeholder for a stripped comment; see strip_slide_comments. Never survives output.
SENTINEL = "\x00"


def strip_slide_comments(body: str, slide_id: str) -> tuple[str, list[str]]:
    """Strip non-directive comments from a slide body. Returns (new_body, warnings).

    Stripped comments are replaced with SENTINEL rather than "", and any line left
    holding nothing but sentinels is then deleted outright. Replacing a whole-line
    comment with "" would leave a BLANK LINE behind, and a blank line inside a run
    of HTML ends the HTML block (CommonMark). The next line then re-enters as
    markdown, and a nested <div> indented four spaces reads as an indented code
    block — so the slide renders its own markup as visible text.

    This bites any deck whose layout comments sit INSIDE the HTML scaffolding,
    between e.g. `    </div>` and `    <div ...>` with no blank line on either
    side. It only appears at Stage 5, when script.md turns stripping on, so it
    presents as figures breaking rather than as a compiler bug. Deleting the
    whole line is the only edit that preserves the HTML block.
    """
    warnings: list[str] = []

    def repl(m: re.Match[str]) -> str:
        inner = m.group(1)
        stripped = inner.strip()
        if not stripped:
            return SENTINEL  # empty comment
        first_line = stripped.splitlines()[0]
        # Marp directive: keep
        from parser import (
            AUTHOR_COMMENT_RE,
            ID_DIRECTIVE_RE,
            MARP_DIRECTIVE_RE,
        )
        if "\n" not in stripped:
            if ID_DIRECTIVE_RE.match(stripped):
                return SENTINEL  # consumed
            if MARP_DIRECTIVE_RE.match(stripped):
                return m.group(0)
        if AUTHOR_COMMENT_RE.match(first_line):
            return SENTINEL  # silently stripped
        # Anything else: stripped with warning if non-trivial.
        word_count = len(stripped.split())
        if word_count >= 3:
            preview = " ".join(stripped.split()[:8])
            warnings.append(
                f"slide {slide_id!r}: stripped non-directive comment "
                f"({word_count} words; \"{preview}...\") — script.md is the source of truth"
            )
        return SENTINEL

    marked = COMMENT_RE.sub(repl, body)
    kept: list[str] = []
    for line in marked.split("\n"):
        if SENTINEL in line:
            if not line.replace(SENTINEL, "").strip():
                continue  # the comment was the whole line; drop the line
            line = line.replace(SENTINEL, "")  # inline comment; keep the rest
        kept.append(line)
    return "\n".join(kept), warnings


def render(slides: SlidesDoc, notes: dict[str, str]) -> tuple[str, list[str]]:
    warnings: list[str] = []
    chunks: list[str] = []

    if slides.front_matter:
        # Front-matter is its own fenced block; emit verbatim with a trailing newline.
        chunks.append("\n".join(slides.front_matter) + "\n")

    rendered_slides: list[str] = []
    for slide in slides.slides:
        body = "\n".join(slide.body_lines)
        cleaned, warn = strip_slide_comments(body, slide.id)
        warnings.extend(warn)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip("\n")

        note_text = notes.get(slide.id, "").strip()
        note_block = f"<!--\n{note_text}\n-->" if note_text else "<!--\n-->"

        rendered_slides.append(f"\n{cleaned}\n\n{note_block}\n")

    chunks.append("\n---\n".join(rendered_slides))
    return "".join(chunks).rstrip() + "\n", warnings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--slides", type=Path, default=Path("slides.md"))
    ap.add_argument("--script", type=Path, default=Path("script.md"))
    ap.add_argument("--output", "-o", type=Path, required=True,
                    help="Path to write the compiled Marp .md")
    args = ap.parse_args(argv)

    slides_text = args.slides.read_text()
    script_text = args.script.read_text() if args.script.exists() else ""

    slides_doc, sw = parse_slides(slides_text)
    script_doc, scw = parse_script(script_text)

    # Pre-Stage-5 mode: no script blocks → pass slides through verbatim so that
    # inline SPEAKER NOTES / TRANSITION scaffolding survives as Marp presenter notes.
    if not script_doc.blocks:
        for w in sw + scw:
            print(f"warning: {w}", file=sys.stderr)
        args.output.write_text(slides_text)
        print(
            f"wrote {args.output} ({len(slides_doc.slides)} slides, "
            f"pre-Stage-5 passthrough — no script.md blocks)",
            file=sys.stderr,
        )
        return 0

    notes, rw = route(slides_doc, script_doc)
    rendered, render_warnings = render(slides_doc, notes)

    for w in sw + scw + rw + render_warnings:
        print(f"warning: {w}", file=sys.stderr)

    args.output.write_text(rendered)
    print(f"wrote {args.output} ({len(slides_doc.slides)} slides)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
