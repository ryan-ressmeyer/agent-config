#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Reformat script.md to match slides.md order and insert TODOs for gaps.

Always-on behaviour:
- Validates every selector resolves to a real slide id.
- Reorders blocks to match slides.md document order, using each block's lowest-indexed
  slide as the sort key.
- Inserts a `## @<id>` placeholder block with `TODO:` body for any slide not covered.

Modes:
- default: rewrite the file in place.
- --dry-run: print the reformatted output to stdout; do not modify the file.
- --init: write a fresh script.md scaffold from slides.md (refuses if the target is
  non-empty unless --force is given).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parser import (  # noqa: E402
    ScriptBlock,
    ScriptDoc,
    Selector,
    SlidesDoc,
    parse_script,
    parse_slides,
)


def render_block(block: ScriptBlock) -> str:
    header = "## " + ", ".join(_render_selector(s) for s in block.selectors)
    body = block.body.strip("\n")
    return f"{header}\n\n{body}\n" if body else f"{header}\n\nTODO:\n"


def _render_selector(s: Selector) -> str:
    return f"@{s.start}" if s.end is None else f"@{s.start}..{s.end}"


def reformat(slides: SlidesDoc, script: ScriptDoc) -> str:
    ids = [s.id for s in slides.slides]
    id_index = {sid: i for i, sid in enumerate(ids)}

    # Map each block to the slide indices it covers; track coverage.
    block_min_idx: dict[int, int] = {}
    covered: set[str] = set()
    for bi, block in enumerate(script.blocks):
        block_ids: list[str] = []
        for sel in block.selectors:
            block_ids.extend(sel.expand(slides))
        for sid in block_ids:
            if sid in covered:
                raise ValueError(f"slide {sid!r} covered by multiple script blocks")
            covered.add(sid)
        block_min_idx[bi] = min(id_index[s] for s in block_ids)

    # Sort blocks by their min-index slide; gather uncovered slides as TODOs.
    sorted_blocks = sorted(enumerate(script.blocks), key=lambda kv: block_min_idx[kv[0]])
    todo_ids = [sid for sid in ids if sid not in covered]
    todo_blocks = [
        ScriptBlock(selectors=[Selector(start=sid, end=None)], body="TODO:", header_line=0)
        for sid in todo_ids
    ]

    # Merge: interleave existing blocks (in id order) with TODOs at the right positions.
    all_blocks = [(block_min_idx[bi], block) for bi, block in sorted_blocks]
    for sid in todo_ids:
        all_blocks.append((id_index[sid], ScriptBlock(
            selectors=[Selector(start=sid, end=None)], body="TODO:", header_line=0
        )))
    all_blocks.sort(key=lambda kv: kv[0])

    out = "\n".join(render_block(b) for _, b in all_blocks)
    return out.strip("\n") + "\n"


def init_scaffold(slides: SlidesDoc) -> str:
    blocks = [
        ScriptBlock(selectors=[Selector(start=s.id, end=None)], body="TODO:", header_line=0)
        for s in slides.slides
    ]
    return "\n".join(render_block(b) for b in blocks).strip("\n") + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--slides", type=Path, default=Path("slides.md"))
    ap.add_argument("--script", type=Path, default=Path("script.md"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--init", action="store_true",
                    help="write a fresh skeleton (refuses if --script exists and is non-empty)")
    ap.add_argument("--force", action="store_true",
                    help="with --init: overwrite an existing non-empty script")
    args = ap.parse_args(argv)

    slides_text = args.slides.read_text()
    slides_doc, sw = parse_slides(slides_text)
    for w in sw:
        print(f"warning: {w}", file=sys.stderr)

    if args.init:
        if args.script.exists() and args.script.read_text().strip() and not args.force:
            print(f"refuse: {args.script} is non-empty (use --force to overwrite)",
                  file=sys.stderr)
            return 2
        content = init_scaffold(slides_doc)
    else:
        script_text = args.script.read_text() if args.script.exists() else ""
        script_doc, scw = parse_script(script_text)
        for w in scw:
            print(f"warning: {w}", file=sys.stderr)
        content = reformat(slides_doc, script_doc)

    if args.dry_run:
        sys.stdout.write(content)
    else:
        args.script.write_text(content)
        print(f"wrote {args.script}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
