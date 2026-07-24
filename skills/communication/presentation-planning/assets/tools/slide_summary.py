#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Emit a low-token overview of slides.md: one line per slide with id, title, alt text.

Intended as the agent-friendly index for the deck (replaces hand-maintained
slides-manifest.md).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parser import parse_slides  # noqa: E402


VIDEO_SRC_RE = re.compile(r"<video[^>]*\bsrc\s*=\s*\"([^\"]+)\"", re.IGNORECASE)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slides", type=Path, nargs="?", default=Path("slides.md"))
    args = ap.parse_args(argv)

    text = args.slides.read_text()
    doc, warnings = parse_slides(text)
    for w in warnings:
        print(f"# warning: {w}", file=sys.stderr)

    print(f"# {args.slides} — {len(doc.slides)} slides")
    for s in doc.slides:
        title = s.title or "(untitled)"
        line = f"{s.index:>3}. {s.id}  —  {title}"
        body = "\n".join(s.body_lines)
        videos = [Path(m.group(1)).name for m in VIDEO_SRC_RE.finditer(body)]
        bits: list[str] = []
        if s.image_alts:
            bits.extend(f"alt: {a}" for a in s.image_alts)
        if videos:
            bits.extend(f"video: {v}" for v in videos)
        if "_class:" in body:
            for m in re.finditer(r"<!--\s*(_class\s*:\s*[^-]+?)\s*-->", body):
                bits.append(m.group(1).strip())
        print(line)
        for b in bits:
            print(f"      · {b}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
