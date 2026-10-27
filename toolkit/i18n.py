"""E17.1 (2026-10-02, Inhalt + Applikation) — ONE NOTEBOOK, TWO LANGUAGES.

The reader chooses English or Deutsch (cover, 👤, ⚙); the next run builds the
document in that language. Nothing in the chapters is written twice: the
German lives in a table next to them (`chapters/de.txt`, the toolkit's own in
`toolkit/de.txt`), and the BUILD wraps every string literal the table knows
in a call that picks the language when the cell runs:

    "Not yet. Take the square root of q = %d"          (chapter source)
    _nbL("Not yet. Take the square root of q = %d",     (mega-cell)
         "Noch nicht. Zieh die Wurzel aus q = %d")

A literal is the unit, exactly as Python sees it: adjacent pieces that Python
joins ("a " "b") are one literal; f-strings are never touched. A literal the
table does not know stays as it is, so code, keys, CSS and formulas cannot be
translated by accident. Numbers, %-placeholders, {}-fields and HTML tags must
be the same in both languages — the build checks it (check()) and stops.

Table format, one entry per pair of lines, blank lines and `#` lines free:
    en: <the English literal, \\n for a line break>
    de: <its German>
"""
import io, re, tokenize, ast

def load(path):
    """{english: german} from a table file. Missing file → {}."""
    try:
        txt = open(path, encoding="utf-8").read()
    except OSError:
        return {}
    out, en = {}, None
    for n, line in enumerate(txt.split("\n"), 1):
        if line.startswith("en: "):
            if en is not None:
                raise ValueError("%s:%d: 'en:' without 'de:'" % (path, n))
            en = _unesc(line[4:])
        elif line.startswith("de: "):
            if en is None:
                raise ValueError("%s:%d: 'de:' without 'en:'" % (path, n))
            if en in out and out[en] != _unesc(line[4:]):
                raise ValueError("%s:%d: two translations of %r" % (path, n, en[:60]))
            out[en] = _unesc(line[4:]); en = None
        elif line.strip() and not line.startswith("#"):
            raise ValueError("%s:%d: neither en: nor de:" % (path, n))
    if en is not None:
        raise ValueError("%s: last 'en:' without 'de:'" % path)
    return out

# A blank at either end of a literal is written ⎵, so that no editor, patch
# tool or text store can strip it unseen (\n is a line break).
def _unesc(s):
    s = s.replace("\\n", "\n")
    core = s.strip("⎵")
    lead, trail = len(s) - len(s.lstrip("⎵")), len(s) - len(s.rstrip("⎵"))
    return " " * lead + core + " " * trail if core else s.replace("⎵", " ")

def _esc(s):
    s = s.replace("\n", "\\n")
    core = s.strip(" ")
    lead, trail = len(s) - len(s.lstrip(" ")), len(s) - len(s.rstrip(" "))
    return "⎵" * lead + core + "⎵" * trail if core else s

def groups(src):
    """Every string literal of `src` as (start, end, value): character offsets
    of the whole implicit concatenation, and its value. f-strings and bytes
    break a group and are never returned."""
    lines = src.splitlines(keepends=True)
    starts = [0]
    for l in lines:
        starts.append(starts[-1] + len(l))
    off = lambda rc: starts[rc[0] - 1] + rc[1]
    out, cur, bad, depth = [], [], False, 0
    def flush():
        nonlocal cur, bad
        if cur and not bad:
            s0, e0 = cur[0][0], cur[-1][1]
            try:
                v = ast.literal_eval("(" + " ".join(t for _, _, t in cur) + ")")
                if isinstance(v, str):
                    out.append((s0, e0, v))
            except Exception:
                pass
        cur, bad = [], False
    FS = {getattr(tokenize, n) for n in ("FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END")
          if hasattr(tokenize, n)}
    infs = 0
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type in FS:
            if tok.type == getattr(tokenize, "FSTRING_START", -1):
                infs += 1
            elif tok.type == getattr(tokenize, "FSTRING_END", -1):
                infs -= 1
                if not infs:       # an f-string joins its neighbours: the whole group stays
                    cur.append((0, 0, '""')); bad = True
            continue
        if infs:
            continue
        if tok.type == tokenize.STRING:
            t = tok.string
            p = re.match(r"[A-Za-z]*", t).group(0).lower()
            if "b" in p or "f" in p:
                cur.append((0, 0, '""')); bad = True
                continue
            cur.append((off(tok.start), off(tok.end), t))
        elif tok.type in (tokenize.NL, tokenize.COMMENT):
            continue
        else:
            flush()
    flush()
    return out

def apply(src, table, fn="_nbL"):
    """`src` with every literal the table knows wrapped in fn(english, german).
    Returns (new_src, used_keys)."""
    used, pieces, last = set(), [], 0
    for s0, e0, v in groups(src):
        if v in table:
            used.add(v)
            pieces.append(src[last:s0])
            pieces.append("%s(%s, %r)" % (fn, src[s0:e0], table[v]))
            last = e0
    pieces.append(src[last:])
    return "".join(pieces), used

_TAG = re.compile(r"</?([a-zA-Z][a-zA-Z0-9]*)")
_PCT = re.compile(r"%(?:\([^)]*\))?[-+ #0]*\d*(?:\.\d+)?[sdifgexXrc%]")
_FMT = re.compile(r"\{[^{}]*\}")
_NUM = re.compile(r"\d+(?:[.,]\d+)?")
_ENT = re.compile(r"&[a-zA-Z#0-9]+;")

def check(en, de):
    """[] if `de` keeps everything of `en` the program depends on: the same
    %-placeholders in order, the same {}-fields, the same HTML tags (multiset),
    the same numbers (multiset; 1,5 counts as 1.5)."""
    bad = []
    if _PCT.findall(en) != _PCT.findall(de):
        bad.append("placeholders %s ≠ %s" % (_PCT.findall(en), _PCT.findall(de)))
    if sorted(_FMT.findall(en)) != sorted(_FMT.findall(de)):
        bad.append("{} fields")
    if sorted(t.lower() for t in _TAG.findall(en)) != sorted(t.lower() for t in _TAG.findall(de)):
        bad.append("tags %s ≠ %s" % (sorted(_TAG.findall(en)), sorted(_TAG.findall(de))))
    ne = sorted(n.replace(",", ".") for n in _NUM.findall(_TAG.sub("", _strip_attrs(en))))
    nd = sorted(n.replace(",", ".") for n in _NUM.findall(_TAG.sub("", _strip_attrs(de))))
    if ne != nd:
        bad.append("numbers %s ≠ %s" % (ne, nd))
    if en[:1].isspace() != de[:1].isspace() or en[-1:].isspace() != de[-1:].isspace():
        bad.append("leading/trailing space")
    return bad

def _strip_attrs(s):
    # numbers inside tags (style='margin:14px') are part of the tag, compared
    # as tags; numbers in the text must stay the same
    return re.sub(r"<[^>]*>", "<>", _ENT.sub("", s))

def translate(src, *tables, where="?"):
    """apply() with every table, after checking each entry it uses. Raises on
    a broken entry; returns (src, used)."""
    table = {}
    for t in tables:
        table.update(t)
    out, used = apply(src, table)
    errs = ["%s: %r → %s" % (where, k[:70], "; ".join(check(k, table[k])))
            for k in sorted(used) if check(k, table[k])]
    if errs:
        raise ValueError("translation table:\n  " + "\n  ".join(errs))
    return out, used

def prose(v):
    """Is this literal reader-facing text? (for the extraction list only)"""
    t = re.sub(r"<[^>]*>", " ", v)
    t = re.sub(r"&[a-zA-Z#0-9]+;", " ", t)
    words = re.findall(r"[A-Za-z]{2,}", t)
    if not words:
        return False
    if re.fullmatch(r"[a-z_][a-z0-9_.\-]*", v.strip()):      # identifiers, keys
        return False
    if re.search(r"[{};]\s*$|^\s*[.#@]?[a-z\-]+\s*[{:]", v) and " " not in t.strip():
        return False
    return True

def candidates(src):
    """Reader-facing literals for the translator's list: groups that are not
    docstrings, not CSS/regex/identifiers. (Build-time help only.)"""
    toks = [t for t in tokenize.generate_tokens(io.StringIO(src).readline)
            if t.type not in (tokenize.NL, tokenize.COMMENT)]
    lines = src.splitlines(keepends=True)
    starts = [0]
    for l in lines:
        starts.append(starts[-1] + len(l))
    stmt_start = set()
    prev = None
    for t in toks:
        if t.type == tokenize.STRING and (prev is None or prev.type in (
                tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT)):
            stmt_start.add(starts[t.start[0] - 1] + t.start[1])
        prev = t
    out = []
    for s0, e0, v in groups(src):
        if s0 in stmt_start or not prose(v):
            continue
        t = re.sub(r"<[^>]*>", " ", v)
        if re.search(r"\d(px|em|%)|var\(|#[0-9a-fA-F]{3}\b|gradient\(|\\[dsSwW(]|^\s*[\w\-]+\s*:\s*[^ ]+;", t):
            if len(re.findall(r"[A-Za-z]{3,} [A-Za-z]{3,}", t)) < 2:
                continue
        out.append((s0, e0, v))
    return out

# A build whose toolkit has no language of its own (E17.5 not merged) still
# gets a working _nbL: German only when DIGICHEM_LANG says so.
FALLBACK = ('_nbL = lambda en, de: de if __import__("os").environ.get("DIGICHEM_LANG", "")'
            '.strip().lower() == "de" else en\n')

def title_de(card, table):
    """The warm title card in German: every phrase of the table found in it
    (longer than eight characters, longest first) replaced."""
    for en in sorted((k for k in table if len(k) > 8 and k in card), key=len, reverse=True):
        card = card.replace(en, table[en])
    return card

def cover_map(rows_en, rows_de, desc_key, cards_de, facts_de_html, extra):
    """What the page needs to put the cold cover into German after Play (the
    cell before Play cannot carry it: the sanitiser strips data-*): the rows of
    the cover timeline IN ORDER (the German run builds the same rows), each as
    [name, card], the facts block, and a few single texts. One hidden element
    in the German title card: <div class="nbcover-de" data-map='…'>."""
    import json, html
    rows_en = [tuple(r) + ("",) * (3 - len(r)) for r in rows_en]
    rows_de = [tuple(r) + ("",) * (3 - len(r)) for r in rows_de]
    assert [r[0] for r in rows_en] == [r[0] for r in rows_de], "the German run built other rows"
    rows = []
    for e, d in zip(rows_en, rows_de):
        k = desc_key(*e)
        rows.append([d[1], cards_de.get(k, "") if k else ""])
    m = dict(extra, rows=rows, facts=facts_de_html)
    return ("<div class=\"nbcover-de\" style=\"display:none\" data-map='%s'></div>"
            % html.escape(json.dumps(m, ensure_ascii=False, separators=(",", ":")), quote=True))

def cover_map_call(div):
    """The mega-cell line that puts the map into the document, German runs
    only: a zero-height widget like the anchors (works with either _nbL)."""
    return ('if _nbL(0, 1):\n    _show(HTML(value=%r, layout=Layout(height="0px", margin="0px")))'
            % div)
