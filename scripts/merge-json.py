#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.10"
# ///
"""Idempotent JSON fragment merger.

Merges a fragment file into a target JSON file:
- Dicts merge recursively (keys in fragment override target)
- Lists union (fragment items appended if not already present)
- Scalars override

In a list, a string item prefixed with "!" removes its match from the merged
result instead of being appended -- this is how a per-machine fragment opts out
of something the base fragment adds. Items are processed in order, so within a
single fragment ["a", "!a"] nets to absent. Write "\\!" to mean a literal "!".

Usage:
    merge-json.py <fragment> <target>

Creates <target> with {} if it doesn't exist. Writes with 2-space indent + trailing newline.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _unescape(value: str) -> str:
    r"""Turn a leading ``\!`` back into a literal ``!``."""
    return value[1:] if value.startswith("\\!") else value


def merge(target: Any, fragment: Any) -> Any:
    if isinstance(target, dict) and isinstance(fragment, dict):
        result = dict(target)
        for k, v in fragment.items():
            if k in result:
                result[k] = merge(result[k], v)
            else:
                result[k] = v
        return result
    if isinstance(target, list) and isinstance(fragment, list):
        result = list(target)
        for item in fragment:
            if isinstance(item, str):
                if item.startswith("!"):
                    excluded = _unescape(item[1:])
                    result = [existing for existing in result if existing != excluded]
                    continue
                item = _unescape(item)
            if item not in result:
                result.append(item)
        return result
    # fragment wins for scalars or type mismatches
    return fragment


def main() -> int:
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <fragment> <target>", file=sys.stderr)
        return 2

    fragment_path = Path(sys.argv[1])
    target_path = Path(sys.argv[2])

    if not fragment_path.exists():
        print(f"fragment not found: {fragment_path}", file=sys.stderr)
        return 1

    fragment_text = fragment_path.read_text().strip()
    if not fragment_text:
        # empty fragment file — nothing to do
        return 0
    fragment = json.loads(fragment_text)

    # Empty dict fragment is a no-op
    if fragment == {}:
        return 0

    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists():
        existing_text = target_path.read_text().strip()
        target = json.loads(existing_text) if existing_text else {}
    else:
        target = {}

    merged = merge(target, fragment)

    if merged == target:
        print(f"  no changes: {target_path}")
        return 0

    target_path.write_text(json.dumps(merged, indent=2) + "\n")
    print(f"  merged {fragment_path.name} → {target_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
