#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ghmath_clean.py - git clean filter for math compatibility
==========================================================
Transforms a markdown file's DISPLAY MATH blocks ($$ ... $$) so that the
version committed to git / shown on GitHub renders correctly, while the
local working-tree copy stays Obsidian-friendly (canonical \\).

Rules (applied ONLY inside $$...$$ blocks, nothing else touched):
  1. Remove blank lines inside the block      (GitHub treats blank line as block end)
  2. Normalize any run of 2+ backslashes to a single \\  (row separator)
  3. Double every \\  ->  \\\\   (GitHub markdown eats one backslash layer)

Reads from stdin, writes to stdout. Scope: display math delimited by a line
containing only "$$". Single-line $$...$$ blocks and inline $...$ math are
left untouched.

Usage (via .gitattributes + git config):
  git config filter.ghmath.clean   "python scripts/ghmath_clean.py"
  git config filter.ghmath.smudge  "python scripts/ghmath_smudge.py"
"""
import re
import sys


def _transform_block(m):
    body = m.group(1)
    # 1. remove blank lines inside block
    body = re.sub(r'\n[ \t]*\n', '\n', body)
    # trim leading/trailing whitespace-only lines
    body = re.sub(r'^[ \t]*\n', '', body)
    body = re.sub(r'\n[ \t]*$', '', body)
    # 2. normalize any run of 2+ backslashes to exactly two (\\)
    body = re.sub(r'\\{2,}', r'\\\\', body)
    # 3. double every \\ -> \\\\
    body = body.replace('\\\\', '\\\\\\\\')
    return '$$\n' + body + '\n$$'


_BLOCK_RE = re.compile(r'\$\$\n(.*?)\n\$\$', re.S)


def main():
    raw = sys.stdin.buffer.read()
    # normalize line endings to LF for processing, restore at the end.
    # CRLF file: every \n is preceded by \r, so bare-LF count == 0.
    crlf = raw.count(b'\r\n')
    bare_lf = raw.count(b'\n') - crlf
    use_crlf = crlf > bare_lf
    data = raw.decode('utf-8').replace('\r\n', '\n')
    out = _BLOCK_RE.sub(_transform_block, data)
    if use_crlf:
        out = out.replace('\n', '\r\n')
    sys.stdout.buffer.write(out.encode('utf-8'))


if __name__ == '__main__':
    main()
