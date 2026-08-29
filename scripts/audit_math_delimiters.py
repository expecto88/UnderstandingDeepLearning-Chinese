#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Audit display-math delimiters in every translated chapter.

The ghmath clean/smudge filter intentionally handles only display-math blocks
whose opening and closing ``$$`` delimiters are each at column zero on a line
by themselves. GitHub also needs these blocks separated from surrounding prose.
This audit keeps the source syntax aligned with both requirements.
"""

from pathlib import Path
import re
import sys


REPO_ROOT = Path(__file__).resolve().parent.parent
CHAPTER_DIR = REPO_ROOT / "chinese"
GITHUB_TAG_RE = re.compile(r"\\qquad\\text\{\([^{}\n]+\)\}")
MATH_STRUCTURE_RE = re.compile(
    r"\\(?P<boundary>begin|end)\{"
    r"(?P<environment>aligned|alignedat|array|matrix|bmatrix|pmatrix|"
    r"vmatrix|Vmatrix|cases|gathered|split)\*?\}"
    r"|(?P<tag>\\tag\{[^{}\n]+\})"
    r"|(?P<separator>(?<!\\)\\{2,3}(?!\\))"
)
FORBIDDEN_ALIGN_RE = re.compile(r"\\(?:begin|end)\{align\*?\}")


def audit_math_structure(body: str) -> tuple[bool, bool]:
    """Return whether a row separator is outside an environment or a tag inside."""
    environment_stack: list[str] = []
    separator_outside = False
    tag_inside = False

    for match in MATH_STRUCTURE_RE.finditer(body):
        boundary = match.group("boundary")
        if boundary == "begin":
            environment_stack.append(match.group("environment"))
        elif boundary == "end":
            environment = match.group("environment")
            if environment_stack and environment_stack[-1] == environment:
                environment_stack.pop()
        elif match.group("separator") and not environment_stack:
            separator_outside = True
        elif match.group("tag") and environment_stack:
            tag_inside = True

    return separator_outside, tag_inside


def audit_file(path: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    inside_block = False
    opening_line = 0
    block_count = 0
    raw_superscript_stars = 0
    block_lines: list[str] = []

    lines = path.read_text(encoding="utf-8-sig").splitlines()
    for line_number, line in enumerate(lines, start=1):
        if "$$" not in line:
            if inside_block:
                block_lines.append(line)
                if not line.strip():
                    errors.append(
                        f"{path.name}:{line_number}: blank line inside display math"
                    )
                for match in re.finditer(r"\\{4,}", line):
                    errors.append(
                        f"{path.name}:{line_number}: noncanonical local "
                        f"backslash run of length {len(match.group(0))}"
                    )
                raw_superscript_stars += len(
                    re.findall(r"\^(?:\{\*\}|\*)", line)
                )
            continue

        if line != "$$":
            errors.append(
                f"{path.name}:{line_number}: '$$' must be alone at column zero"
            )
            continue

        if inside_block:
            body = "\n".join(block_lines)
            if raw_superscript_stars >= 2:
                errors.append(
                    f"{path.name}:{opening_line}: multiple raw superscript '*' "
                    "tokens can be consumed as Markdown; use '\\ast'"
                )
            if GITHUB_TAG_RE.search(body):
                errors.append(
                    f"{path.name}:{opening_line}: GitHub-only equation label "
                    "must not appear in the Obsidian working tree"
                )
            if FORBIDDEN_ALIGN_RE.search(body):
                errors.append(
                    f"{path.name}:{opening_line}: use 'aligned' instead of "
                    "'align' inside a '$$' block"
                )
            separator_outside, tag_inside = audit_math_structure(body)
            if separator_outside:
                errors.append(
                    f"{path.name}:{opening_line}: row separator outside an "
                    "explicit multiline math environment"
                )
            if tag_inside:
                errors.append(
                    f"{path.name}:{opening_line}: '\\tag' must be placed "
                    "after the multiline environment"
                )
            inside_block = False
            block_count += 1
            raw_superscript_stars = 0
            block_lines = []
            if line_number < len(lines) and lines[line_number].strip():
                errors.append(
                    f"{path.name}:{line_number}: blank line required after block"
                )
        else:
            if line_number > 1 and lines[line_number - 2].strip():
                errors.append(
                    f"{path.name}:{line_number}: blank line required before block"
                )
            inside_block = True
            opening_line = line_number
            raw_superscript_stars = 0
            block_lines = []

    if inside_block:
        errors.append(
            f"{path.name}:{opening_line}: display-math block is not closed"
        )

    return errors, block_count


def main() -> int:
    chapter_files = sorted(CHAPTER_DIR.glob("*.md"))
    if not chapter_files:
        print(f"ERROR: no Markdown chapters found in {CHAPTER_DIR}", file=sys.stderr)
        return 2

    all_errors: list[str] = []
    total_blocks = 0
    for path in chapter_files:
        errors, block_count = audit_file(path)
        all_errors.extend(errors)
        total_blocks += block_count

    if all_errors:
        print("Display-math delimiter audit failed:", file=sys.stderr)
        for error in all_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"OK: {len(chapter_files)} Markdown files, "
        f"{total_blocks} canonical display-math blocks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
