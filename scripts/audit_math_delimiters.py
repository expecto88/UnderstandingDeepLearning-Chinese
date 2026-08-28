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


def audit_file(path: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    inside_block = False
    opening_line = 0
    block_count = 0
    raw_superscript_stars = 0

    lines = path.read_text(encoding="utf-8-sig").splitlines()
    for line_number, line in enumerate(lines, start=1):
        if "$$" not in line:
            if inside_block:
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
            if raw_superscript_stars >= 2:
                errors.append(
                    f"{path.name}:{opening_line}: multiple raw superscript '*' "
                    "tokens can be consumed as Markdown; use '\\ast'"
                )
            inside_block = False
            block_count += 1
            raw_superscript_stars = 0
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
