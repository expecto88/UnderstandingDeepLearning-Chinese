#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Git clean filter for GitHub/Obsidian display-math compatibility.

Inside standalone ``$$`` blocks, blank lines are removed and local row
separators are encoded reversibly for GitHub Markdown: a run of two
backslashes becomes four, while three (a row separator immediately followed
by a command slash) becomes five. Everything outside those blocks is kept.
"""
import re
import sys


def _clean_backslash_run(match):
    """Encode a local row separator without losing an adjacent command slash."""
    run = match.group(0)
    if len(run) in (2, 3):
        return "\\" * (len(run) + 2)
    return run


def _transform_block(match):
    body = match.group(1)
    body = re.sub(r"\n[ \t]*\n", "\n", body)
    body = re.sub(r"^[ \t]*\n", "", body)
    body = re.sub(r"\n[ \t]*$", "", body)
    body = re.sub(r"\\{2,}", _clean_backslash_run, body)
    return "$$\n" + body + "\n$$"


_BLOCK_RE = re.compile(r"\$\$\n(.*?)\n\$\$", re.S)


def main():
    raw = sys.stdin.buffer.read()
    crlf = raw.count(b"\r\n")
    bare_lf = raw.count(b"\n") - crlf
    use_crlf = crlf > bare_lf
    data = raw.decode("utf-8").replace("\r\n", "\n")
    out = _BLOCK_RE.sub(_transform_block, data)
    if use_crlf:
        out = out.replace("\n", "\r\n")
    sys.stdout.buffer.write(out.encode("utf-8"))


if __name__ == "__main__":
    main()
