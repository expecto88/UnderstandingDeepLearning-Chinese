#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Git smudge filter, inverse of ``ghmath_clean.py``.

Inside standalone ``$$`` blocks, runs of four/five committed backslashes are
decoded to two/three local backslashes. This preserves both ordinary LaTeX
row separators and separators immediately followed by commands such as
``\\theta``. GitHub-safe text equation labels are restored to local
``\\tag{...}`` commands. Everything outside those blocks is kept.
"""
import re
import sys


_GITHUB_TAG_RE = re.compile(r"\\qquad\\text\{\(([^{}\n]+)\)\}")


def _smudge_backslash_run(match):
    """Decode a GitHub-safe row separator without losing command slashes."""
    run = match.group(0)
    if len(run) in (4, 5):
        return "\\" * (len(run) - 2)
    return run


def _transform_block(match):
    body = match.group(1)
    body = re.sub(r"\n[ \t]*\n", "\n", body)
    body = re.sub(r"^[ \t]*\n", "", body)
    body = re.sub(r"\n[ \t]*$", "", body)
    body = re.sub(r"\\{2,}", _smudge_backslash_run, body)
    body = _GITHUB_TAG_RE.sub(r"\\tag{\1}", body)
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
