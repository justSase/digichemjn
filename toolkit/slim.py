"""Build-time helper (E10.8, 2026-09-30): the mega-cell without its workshop notes.

The sources keep every comment and docstring — they are the project's memory.
The reader's cell does not need them: they were ~100 000 of its 853 000
characters (E10.8, criterion "mega-cell ≤ 700 KB"). slim() drops

  • comments, except the section markers at column 0 (`# ---- c01.py ----`,
    `# ===== sections …`) that show where each file begins, and the cell's
    leading comment lines (what the collapsed cell shows);
  • docstrings and other lone strings (an emptied block keeps `pass`);
  • indentation beyond one space per block level, the indentation of
    continuation lines, and blank lines.

Nothing inside a string is touched — CSS, JS, HTML and code the reader edits
are string literals. The proof is structural: the AST of the result equals the
AST of the input with the docstrings taken out (asserted on every build).

    from slim import slim
    small = slim(mega_source)
"""
import ast, io, re, tokenize

_KEEP = re.compile(r"# (----|=====) ")


def _lit(st):
    return isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant) \
        and isinstance(st.value.value, str)


def _blocks(tree):
    for n in ast.walk(tree):
        for f in ("body", "orelse", "finalbody"):
            b = getattr(n, f, None)
            if isinstance(b, list) and b and isinstance(b[0], ast.stmt):
                yield n, f, b


def _docstrings(tree):
    """(first row, last row, pass here) of every docstring and every other
    string standing alone as a statement."""
    out = []
    for n, f, b in _blocks(tree):
        only = all(_lit(st) for st in b)
        for i, st in enumerate(b):
            if _lit(st):
                out.append((st.lineno, st.end_lineno, only and i == 0))
    return out


def _strip_doc(tree):
    for n, f, b in list(_blocks(tree)):
        setattr(n, f, [st for st in b if not _lit(st)] or [ast.Pass()])
    return tree


_LIT = re.compile(r"(?is)([rbu]*)('|\")(.*)\2")


def _join(src):
    """'abc' 'def' on neighbouring lines -> 'abcdef': one literal, as Python
    reads it anyway. Only single-line literals with the same prefix and quote."""
    starts = [0]
    for line in src.split("\n"):
        starts.append(starts[-1] + len(line) + 1)
    off = lambda rc: starts[rc[0] - 1] + rc[1]
    edits, run = [], []
    def flush():
        if len(run) > 1:
            m0 = _LIT.fullmatch(run[0].string)
            edits.append((off(run[0].start), off(run[-1].end), m0.group(1) + m0.group(2)
                          + "".join(_LIT.fullmatch(t.string).group(3) for t in run) + m0.group(2)))
        run.clear()
    for t in tokenize.generate_tokens(io.StringIO(src).readline):
        if t.type == tokenize.NL:
            continue
        m = _LIT.fullmatch(t.string) if t.type == tokenize.STRING and t.start[0] == t.end[0] else None
        if m and len(m.group(2)) == 1 and not m.group(3).endswith("\\") \
                and run and _LIT.fullmatch(run[-1].string).group(1, 2) == m.group(1, 2):
            run.append(t)
            continue
        flush()
        if m:
            run.append(t)
    flush()
    for a, b, lit in reversed(edits):
        src = src[:a] + lit + src[b:]
    return src


def slim(src):
    lines = src.split("\n")
    head = 0                                   # the leading comment block stays
    while head < len(lines) and lines[head].startswith("#"):
        head += 1
    toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    inside = set()                             # rows that begin inside a token (a string)
    cut = {}                                   # row -> column where a comment starts
    first = {}                                 # row -> block depth, first row of a logical line
    depth, at_start = 0, True
    for t in toks:
        (r0, c0), (r1, c1) = t.start, t.end
        if r1 > r0:
            inside.update(range(r0 + 1, r1 + 1))
        if t.type == tokenize.INDENT:
            depth += 1
            continue
        if t.type == tokenize.DEDENT:
            depth -= 1
            continue
        if t.type == tokenize.COMMENT:
            if not (c0 == 0 and _KEEP.match(t.string)) and r0 > head:
                cut[r0] = c0
            continue
        if t.type in (tokenize.NL, tokenize.ENCODING, tokenize.ENDMARKER):
            continue
        if t.type == tokenize.NEWLINE:
            at_start = True
            continue
        if at_start:
            first[r0] = depth
            at_start = False
    drop, sole = set(), {}
    for a, b, only in _docstrings(ast.parse(src)):
        if lines[a - 1][:len(lines[a - 1]) - len(lines[a - 1].lstrip())].strip() == "" \
                and a in first:
            drop.update(range(a, b + 1))
            if only:
                sole[a] = first[a]
    out = []
    for i, line in enumerate(lines, 1):
        if i <= head:
            out.append(line)
            continue
        if i in drop:
            if i in sole:
                out.append(" " * sole[i] + "pass")
            continue
        if i in inside:                        # a string's own text: as it is
            if i in cut:
                line = line[:cut[i]].rstrip()
            out.append(line)
            continue
        if i in cut:
            line = line[:cut[i]]
        line = line.strip()
        if not line:
            continue
        out.append((" " * first[i] if i in first else "") + line)
    res = _join("\n".join(out))
    want = ast.dump(_strip_doc(ast.parse(src)))
    assert ast.dump(ast.parse(res)) == want, "slim changed the program"
    return res
