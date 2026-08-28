#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Audit display-math delimiters in every translated chapter.

The ghmath clean/smudge filter intentionally handles only display-math blocks
whose opening and closing ``$$`` delimiters are each on a line by themselves.
This audit prevents unsupported single-line or attached-delimiter forms from
silently bypassing the filter.
"""

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parent.parent
CHAPTER_DIR = REPO_ROOT / "chinese"


def audit_file(path: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    inside_block = False
    opening_line = 0
    block_count = 0

    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), start=1
    ):
        if "$$" not in line:
            continue

        if line.strip() != "$$":
            errors.append(
                f"{path.name}:{line_number}: '$$' must be on a line by itself"
            )
            continue

        if inside_block:
            inside_block = False
            block_count += 1
        else:
            inside_block = True
            opening_line = line_number

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
        f"OK: {len(chapter_files)} chapter files, "
        f"{total_blocks} canonical display-math blocks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
