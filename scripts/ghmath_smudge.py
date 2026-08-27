#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ghmath_smudge.py - git smudge filter (inverse of ghmath_clean.py)
=================================================================
Runs on checkout: converts the committed GitHub-correct form (\\\\ inside
display-math blocks) back to the canonical Obsidian-friendly form (\\).

Scope: display math blocks delimited by a line containing only "$$".
Nothing outside those blocks is touched.

Reads from stdin, writes to stdout.
"""
import re
import sys


def _transform_block(m):
    body = m.group(1)
    # remove blank lines inside block (mirror of clean)
    body = re.sub(r'\n[ \t]*\n', '\n', body)
    body = re.sub(r'^[ \t]*\n', '', body)
    body = re.sub(r'\n[ \t]*$', '', body)
    # collapse every run of 2+ backslashes to exactly two (\\)
    body = re.sub(r'\\{2,}', r'\\\\', body)
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
