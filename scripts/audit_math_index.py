#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Audit staged GitHub math blobs against the Obsidian working tree."""

from pathlib import Path
import re
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parent.parent
CHAPTER_DIR = REPO_ROOT / "chinese"
CLEAN_SCRIPT = REPO_ROOT / "scripts" / "ghmath_clean.py"
SMUDGE_SCRIPT = REPO_ROOT / "scripts" / "ghmath_smudge.py"
BLOCK_RE = re.compile(r"(?m)^\$\$\n(.*?)\n\$\$$", re.S)
TAG_RE = re.compile(r"\\tag\{[^{}\n]+\}")
GITHUB_LABEL_RE = re.compile(r"\\qquad\\text\{\([^{}\n]+\)\}")
BACKSLASH_RUN_RE = re.compile(r"\\{2,}")


def run_filter(script: Path, data: bytes) -> bytes:
    return subprocess.run(
        [sys.executable, str(script)],
        cwd=REPO_ROOT,
        input=data,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout


def staged_blob(relative_path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f":{relative_path}"],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout


def normalized(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def main() -> int:
    errors: list[str] = []
    chapter_files = sorted(CHAPTER_DIR.glob("*.md"))
    total_blocks = 0
    total_local_tags = 0
    total_github_labels = 0

    for path in chapter_files:
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        worktree = path.read_bytes()
        blob = staged_blob(relative_path)
        blob_text = blob.decode("utf-8-sig")
        worktree_text = worktree.decode("utf-8-sig")
        blocks = BLOCK_RE.findall(blob_text)
        total_blocks += len(blocks)

        local_tags = len(TAG_RE.findall(worktree_text))
        github_labels = len(GITHUB_LABEL_RE.findall(blob_text))
        total_local_tags += local_tags
        total_github_labels += github_labels

        if TAG_RE.search(blob_text):
            errors.append(f"{path.name}: staged blob still contains '\\tag'")
        if local_tags != github_labels:
            errors.append(
                f"{path.name}: local tags ({local_tags}) != "
                f"GitHub labels ({github_labels})"
            )

        for body in blocks:
            for match in BACKSLASH_RUN_RE.finditer(body):
                if len(match.group(0)) not in (4, 5):
                    errors.append(
                        f"{path.name}: staged backslash run has length "
                        f"{len(match.group(0))}, expected 4 or 5"
                    )

        if normalized(run_filter(SMUDGE_SCRIPT, blob)) != normalized(worktree):
            errors.append(f"{path.name}: staged blob does not smudge to worktree")
        if run_filter(CLEAN_SCRIPT, blob) != blob:
            errors.append(f"{path.name}: clean filter is not idempotent")

    if errors:
        print("Staged GitHub math audit failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"OK: {len(chapter_files)} staged files, {total_blocks} blocks, "
        f"{total_local_tags} local tags <-> "
        f"{total_github_labels} GitHub-safe labels"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
