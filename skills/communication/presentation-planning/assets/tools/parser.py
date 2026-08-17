"""Shared parsing for slides.md and script.md.

Slides.md model:
- Optional YAML front-matter delimited by `---` at the top of the file.
- Slides separated by lines that are exactly `---`.
- HTML comments inside a slide are classified:
    * Marp per-slide directive `<!-- _foo: ... -->` (single line) -> kept verbatim.
    * Our slide-id directive `<!-- _id: slug -->` -> consumed; not emitted.
    * Author-only comment `<!-- @ ... -->` -> silently stripped.
    * Anything else -> stripped, warning emitted (likely a pre-existing speaker note).
- Default slide ID = slugified text of first heading (`#`+ ). Duplicates of an auto-derived
  ID get `-2`, `-3`, ... appended in document order. Explicit `_id:` overrides must be unique.

Script.md model:
- Sequence of blocks. Each block begins with a `## @<selector>[, @<selector>...]` header.
- Selector is `@slug` or `@slug-a..slug-b` (inclusive range using slides.md document order).
- Block body extends to the next `## @` header or EOF. `<!-- @ ... -->` author comments
  inside a block body are stripped; everything else is preserved verbatim.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


SLIDE_SEP_RE = re.compile(r"^---\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
COMMENT_RE = re.compile(r"<!--(.*?)-->", re.DOTALL)
ID_DIRECTIVE_RE = re.compile(r"^\s*_id\s*:\s*([A-Za-z0-9][A-Za-z0-9_-]*)\s*$")
# Only a comment naming an ACTUAL Marp directive counts as one; a directive is kept
# verbatim in the compiled deck, and Marp renders every comment it finds as a presenter
# note. The old pattern was `_?[A-Za-z][A-Za-z0-9]*\s*:`, which matches any `Word:`
# shape — so authoring comments like `<!-- FIGURE: recycled as-is. Build 1 of 3. -->`
# were treated as directives and surfaced in the speaker notes. Names are Marp's own
# (case-sensitive), optionally `_`-prefixed for the spot/local form, plus this
# workflow's own `_id`.
_MARP_DIRECTIVE_NAMES = (
    "marp theme style headingDivider paginate header footer class color size "
    "backgroundColor backgroundImage backgroundPosition backgroundRepeat "
    "backgroundSize transition math lang"
).split()
MARP_DIRECTIVE_RE = re.compile(
    r"^\s*(?:_id|_?(?:" + "|".join(_MARP_DIRECTIVE_NAMES) + r"))\s*:"
)
AUTHOR_COMMENT_RE = re.compile(r"^\s*@(?:\s|$)")
BLOCK_HEADER_RE = re.compile(r"^##\s+(@.+?)\s*$")
SELECTOR_RE = re.compile(r"^@([A-Za-z0-9][A-Za-z0-9_-]*)(?:\.\.([A-Za-z0-9][A-Za-z0-9_-]*))?$")


def slugify(text: str) -> str:
    """Lowercase, alphanumerics + hyphens. Collapses runs and trims edges."""
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return text or "slide"


@dataclass
class Comment:
    """An HTML comment found inside a slide body."""
    raw: str             # full text between `<!--` and `-->`
    kind: str            # 'marp' | 'id' | 'author' | 'other'
    line_offset: int     # 0-based line index within the slide where the comment starts


@dataclass
class Slide:
    """One slide parsed from slides.md."""
    index: int                              # 0-based, matches document order (excluding front-matter)
    id: str                                 # resolved slide id
    id_override: bool                       # True if `_id:` directive was present
    title: str | None                       # text of first heading, if any
    body_lines: list[str]                   # raw lines of the slide as written
    comments: list[Comment]                 # all HTML comments found in the body
    image_alts: list[str] = field(default_factory=list)


@dataclass
class SlidesDoc:
    front_matter: list[str]                 # raw lines including the `---` delimiters; empty if none
    slides: list[Slide]

    def by_id(self) -> dict[str, Slide]:
        return {s.id: s for s in self.slides}


@dataclass
class Selector:
    start: str
    end: str | None                         # None for single, else the upper bound slug

    def expand(self, slides: SlidesDoc) -> list[str]:
        ids = [s.id for s in slides.slides]
        try:
            i = ids.index(self.start)
        except ValueError:
            raise KeyError(f"unknown slide id {self.start!r}")
        if self.end is None:
            return [self.start]
        try:
            j = ids.index(self.end)
        except ValueError:
            raise KeyError(f"unknown slide id {self.end!r}")
        if j < i:
            raise ValueError(f"range {self.start}..{self.end} runs backwards")
        return ids[i : j + 1]


@dataclass
class ScriptBlock:
    selectors: list[Selector]
    body: str                               # block prose, author-comments stripped
    header_line: int                        # 1-based line in script.md


@dataclass
class ScriptDoc:
    blocks: list[ScriptBlock]


# ---------------------------------------------------------------------------
# slides.md
# ---------------------------------------------------------------------------


def split_slides(text: str) -> tuple[list[str], list[list[str]]]:
    """Return (front_matter_lines, list_of_slide_line_lists).

    Front-matter is the first `---`-fenced block iff the file starts with `---`.
    Slides are split on lines matching `^---\\s*$`.
    """
    lines = text.splitlines()
    i = 0
    front_matter: list[str] = []
    if lines and SLIDE_SEP_RE.match(lines[0]):
        # find closing fence
        for j in range(1, len(lines)):
            if SLIDE_SEP_RE.match(lines[j]):
                front_matter = lines[: j + 1]
                i = j + 1
                break
        # no closing fence -> treat as no front-matter
        if not front_matter:
            i = 0

    # Split on `---` lines, but ignore separators inside an HTML comment.
    slides: list[list[str]] = []
    current: list[str] = []
    in_comment = False
    for line in lines[i:]:
        # Track HTML-comment state line-by-line. We assume a comment is opened
        # by the last `<!--` on a line with no matching `-->` after it, and
        # closed when a `-->` appears.
        if not in_comment and SLIDE_SEP_RE.match(line):
            slides.append(current)
            current = []
            continue
        current.append(line)
        # Update comment state based on this line's content.
        scan = line
        while scan:
            if not in_comment:
                idx = scan.find("<!--")
                if idx < 0:
                    break
                close = scan.find("-->", idx + 4)
                if close < 0:
                    in_comment = True
                    break
                scan = scan[close + 3 :]
            else:
                close = scan.find("-->")
                if close < 0:
                    break
                in_comment = False
                scan = scan[close + 3 :]
    slides.append(current)

    # If the body began with `---`, the first slide will be empty; drop it.
    if slides and not any(s.strip() for s in slides[0]):
        slides = slides[1:]
    # Drop a trailing empty slide (file ended with `---\n`).
    if slides and not any(s.strip() for s in slides[-1]):
        slides = slides[:-1]

    return front_matter, slides


def _classify_comment(inner: str) -> str:
    """Return one of 'marp', 'id', 'author', 'other'."""
    stripped = inner.strip()
    if "\n" not in stripped:
        if ID_DIRECTIVE_RE.match(stripped):
            return "id"
        if MARP_DIRECTIVE_RE.match(stripped):
            return "marp"
    if AUTHOR_COMMENT_RE.match(stripped.splitlines()[0] if stripped else ""):
        return "author"
    return "other"


def _scan_comments(body: str) -> list[Comment]:
    out: list[Comment] = []
    for m in COMMENT_RE.finditer(body):
        inner = m.group(1)
        kind = _classify_comment(inner)
        # line offset = number of newlines before the match start
        line_offset = body[: m.start()].count("\n")
        out.append(Comment(raw=inner, kind=kind, line_offset=line_offset))
    return out


def _extract_image_alts(body: str) -> list[str]:
    alts: list[str] = []
    # Markdown ![alt](src)
    for m in re.finditer(r"!\[([^\]]*)\]\(", body):
        if m.group(1):
            alts.append(m.group(1))
    # <img ... alt="...">
    for m in re.finditer(r"<img[^>]*\balt\s*=\s*\"([^\"]*)\"", body, re.IGNORECASE):
        if m.group(1):
            alts.append(m.group(1))
    # <video ... > -> no alt; record src basename as a hint instead
    return alts


def parse_slides(text: str) -> tuple[SlidesDoc, list[str]]:
    """Parse slides.md content. Returns (doc, warnings)."""
    warnings: list[str] = []
    front_matter, raw_slides = split_slides(text)

    # First pass: title, comments, explicit IDs.
    parsed: list[Slide] = []
    for idx, raw in enumerate(raw_slides):
        body = "\n".join(raw)
        comments = _scan_comments(body)

        # title from first heading
        title: str | None = None
        for line in raw:
            mh = HEADING_RE.match(line)
            if mh:
                title = mh.group(2).strip()
                break

        # explicit _id override?
        id_override = False
        resolved_id = ""
        for c in comments:
            if c.kind == "id":
                m = ID_DIRECTIVE_RE.match(c.raw.strip())
                if m:
                    if id_override:
                        warnings.append(
                            f"slide {idx}: multiple `_id` directives; using the first"
                        )
                    else:
                        resolved_id = m.group(1)
                        id_override = True

        parsed.append(
            Slide(
                index=idx,
                id=resolved_id,           # filled below
                id_override=id_override,
                title=title,
                body_lines=raw,
                comments=comments,
                image_alts=_extract_image_alts(body),
            )
        )

    # Resolve auto-IDs with collision numbering. Detect override collisions.
    override_seen: dict[str, int] = {}
    auto_groups: dict[str, list[int]] = {}
    for s in parsed:
        if s.id_override:
            override_seen.setdefault(s.id, 0)
            override_seen[s.id] += 1
        else:
            base = slugify(s.title) if s.title else f"slide-{s.index}"
            auto_groups.setdefault(base, []).append(s.index)

    for sid, count in override_seen.items():
        if count > 1:
            raise ValueError(f"duplicate explicit slide id {sid!r}: appears {count} times")

    # Reserve override IDs so auto-numbering can't collide with them.
    reserved = set(override_seen.keys())

    for base, indices in auto_groups.items():
        n = 1
        for idx in indices:
            candidate = base if n == 1 else f"{base}-{n}"
            while candidate in reserved:
                n += 1
                candidate = f"{base}-{n}"
            parsed[idx].id = candidate
            reserved.add(candidate)
            n += 1

    return SlidesDoc(front_matter=front_matter, slides=parsed), warnings


# ---------------------------------------------------------------------------
# script.md
# ---------------------------------------------------------------------------


def parse_script(text: str) -> tuple[ScriptDoc, list[str]]:
    """Parse script.md. Returns (doc, warnings)."""
    warnings: list[str] = []
    lines = text.splitlines()
    blocks: list[tuple[int, list[Selector], list[str]]] = []

    current_header_line: int | None = None
    current_selectors: list[Selector] = []
    current_body: list[str] = []
    preamble: list[str] = []
    saw_header = False
    in_comment = False

    def flush() -> None:
        nonlocal current_header_line, current_selectors, current_body
        if current_header_line is not None:
            blocks.append((current_header_line, current_selectors, current_body))
        current_header_line = None
        current_selectors = []
        current_body = []

    for lineno, line in enumerate(lines, start=1):
        m = BLOCK_HEADER_RE.match(line)
        if not in_comment and m and m.group(1).lstrip().startswith("@"):
            saw_header = True
            flush()
            current_header_line = lineno
            current_selectors = _parse_selectors(m.group(1), lineno)
        else:
            if saw_header:
                current_body.append(line)
            else:
                preamble.append(line)
        # Track HTML-comment state line-by-line (same logic as split_slides).
        scan = line
        while scan:
            if not in_comment:
                idx = scan.find("<!--")
                if idx < 0:
                    break
                close = scan.find("-->", idx + 4)
                if close < 0:
                    in_comment = True
                    break
                scan = scan[close + 3 :]
            else:
                close = scan.find("-->")
                if close < 0:
                    break
                in_comment = False
                scan = scan[close + 3 :]
    flush()

    if any(s.strip() for s in preamble):
        warnings.append(
            "script.md: content before the first `## @<selector>` block is ignored"
        )

    doc_blocks: list[ScriptBlock] = []
    for header_line, selectors, body in blocks:
        body_text = _strip_author_comments("\n".join(body)).strip("\n")
        doc_blocks.append(ScriptBlock(selectors=selectors, body=body_text, header_line=header_line))

    return ScriptDoc(blocks=doc_blocks), warnings


def _parse_selectors(header_text: str, lineno: int) -> list[Selector]:
    out: list[Selector] = []
    for part in (p.strip() for p in header_text.split(",")):
        m = SELECTOR_RE.match(part)
        if not m:
            raise ValueError(f"script.md line {lineno}: bad selector {part!r}")
        out.append(Selector(start=m.group(1), end=m.group(2)))
    if not out:
        raise ValueError(f"script.md line {lineno}: empty selector list")
    return out


def _strip_author_comments(text: str) -> str:
    def repl(m: re.Match[str]) -> str:
        inner = m.group(1)
        if _classify_comment(inner) == "author":
            return ""
        return m.group(0)
    return COMMENT_RE.sub(repl, text)


# ---------------------------------------------------------------------------
# routing
# ---------------------------------------------------------------------------


def route(
    slides: SlidesDoc, script: ScriptDoc
) -> tuple[dict[str, str], list[str]]:
    """Expand script blocks into a slide_id -> notes_text mapping. Returns (mapping, warnings).

    Errors are raised; warnings are returned for uncovered slides.
    """
    warnings: list[str] = []
    mapping: dict[str, str] = {}
    coverage_block: dict[str, int] = {}  # slide_id -> header_line that first covered it

    valid_ids = {s.id for s in slides.slides}

    for block in script.blocks:
        # expand selectors
        covered: list[str] = []
        for sel in block.selectors:
            try:
                covered.extend(sel.expand(slides))
            except (KeyError, ValueError) as e:
                raise ValueError(
                    f"script.md line {block.header_line}: {e}"
                ) from None

        # detect duplicates
        for sid in covered:
            if sid in coverage_block:
                raise ValueError(
                    f"slide {sid!r} covered by multiple blocks "
                    f"(lines {coverage_block[sid]} and {block.header_line})"
                )
            if sid not in valid_ids:
                raise ValueError(f"unknown slide id {sid!r}")
            coverage_block[sid] = block.header_line
            mapping[sid] = block.body

    for s in slides.slides:
        if s.id not in mapping:
            warnings.append(f"slide {s.id!r} has no script block")

    return mapping, warnings
