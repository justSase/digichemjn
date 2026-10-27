r"""E26.3 (2026-10-11, Python) — THE CELL IS SHORT: A FEW LINES AND ONE LINE OF CARGO.

PyCharm ignores `source_hidden` and showed all ~2 900 lines of the mega-cell
above its output (measured 11.10., v1.70/v1.72). There is no second file and
no package (E20.2 stays the way for a server): the cell itself gets short.

    short(src, head, chunk=0) -> cell     (build time)
    expand(cell) -> src                   (the suites: the text the cell runs)

`src` is the finished mega-cell (after slim and packz) — exactly what the cell
held up to v1.73. `head` are its first comment lines (what a collapsed cell
shows: E23.0 line 1, E26.1b line 2). The new cell is

    <head lines>
    # ▶ run — the output appears below · ▶ ausführen — die Ausgabe erscheint darunter
    # <editor-fold desc="DigiChemJN — nicht bearbeiten" defaultstate="collapsed">
    _NBZ = "<zlib + base64 of src>"                 ← ONE line (chunk=0)
    def _nbz_run(z, g): …                            unpack, compile, run
    _nbz_run(_NBZ, globals())
    # </editor-fold>

— 14 lines with the two head lines. The editor-fold pair is an IntelliJ fold
region (collapsed when PyCharm opens the file, if it honours it in a notebook
cell — the Dirigent measures); for every other front end it is a comment.

chunk > 0 (Variant B, switch NB_CELL_CHUNK in chapter_template.py): the cargo
in lines of `chunk` characters inside one pair of brackets, for an editor that
cannot show a 350 000-character line. More lines, same value.

ERRORS KEEP THEIR CHAPTER. The cargo is split at the build's file markers
(`# ---- c03.py ----`, column 0, top level — slim keeps exactly these) and each
piece is compiled under its own name `<digichemjn:c03.py>` and put into
linecache: a traceback names the chapter file, its line in that piece and the
line itself — and inspect.getsource works on the notebook's functions (the
check logic for the reading window, py-E26.3). The pieces run one after the
other in the cell's own globals: the same statements in the same order as the
one cell before. short() proves it: expand(cell) == src, and every piece
compiles on its own."""
import base64, re, zlib

# E38a P3 (2026-10-26, Python; Befund zu v1.79) — WHAT A READER SEES OF THE CELL IS ASCII. VS Code drew
# ▶ ⚠ → — · in the cell's comments as boxes (its editor font has no such glyph, no fallback). Every line
# a front end shows — the #@title line (TITLE_ASCII), the comment block, the fold — is plain ASCII now;
# umlauts are written out (ae, oe, ue, ss). short(…, ascii=True) refuses anything else (the Vorlage;
# Complex/Modeling keep RUN_LINE until they are pulled along — only the fold line below is shared).
FOLD_OPEN = '# <editor-fold desc="DigiChemJN - nicht bearbeiten" defaultstate="collapsed">'
FOLD_CLOSE = "# </editor-fold>"
RUN_LINE = ("# ▶ run — the output appears below · "
            "▶ ausführen — die Ausgabe erscheint darunter")
# E29 P8 (2026-10-12, Python; Nutzer zu v1.75) — THE CELL SAYS: DO NOT CHANGE IT.
# short(…, note=NOTE_LINES): the run line in two lines, en and de, each with the
# warning — an edit breaks the notebook; reading is fine (to build notebooks of
# one's own, → the template); yes, one could hack into the solutions (cheating
# oneself). Same line count as RUN_LINE + 1: the cell stays at 15 lines.
# (The Vorlage only, by the Dauerregel; Complex/Modeling keep RUN_LINE.)
NOTE_LINES = (
    "# ▶ run — the output appears below. Do not edit this cell: any change breaks the notebook. Reading the "
    "code is fine: to build your own notebooks (→ Vorlage) — and yes, you could hack into the solutions that "
    "way (cheating yourself).",
    "# ▶ ausführen — die Ausgabe erscheint darunter. Nicht ändern: eine Änderung macht das Notebook "
    "unbenutzbar. Der Code darf gelesen werden: zum Bauen eigener Notebooks/Inhalte (→ Vorlage) — und ja, man "
    "könnte sich damit auch in die Lösungen hacken (Selbstbetrug).")
# E31 C1 (2026-10-12, Python; Nutzer zu v1.77: "darf auch die erste Seite
# ausfüllen") — THE COMMENT BLOCK, ONE SENTENCE PER LINE. The run line, the
# Output line and the warning of E29 P8 stood two and three sentences to a
# line (up to 190 characters, cut off in PyCharm's editor). Now a block in
# English, an empty comment line, the same in German — each sentence a line;
# with short(…, head=[#@title line], note=NOTE_BLOCK) it replaces the head's
# line 2 and NOTE_LINES (the Vorlage only, by the Dauerregel). 23 lines.
NOTE_BLOCK = (
    "# Run this cell: the output appears below it, at the very end (Ctrl+End).",
    "# If there is no output, run it again - your progress is kept.",
    "# Do not edit this cell: any change breaks the notebook.",
    "# Reading the code is fine: to build notebooks of your own (see Vorlage).",
    "# And yes, you could hack into the solutions that way - cheating yourself.",
    "#",
    "# Zelle ausfuehren: die Ausgabe erscheint darunter, ganz unten (Strg+Ende).",
    "# Erscheint keine Ausgabe, noch einmal ausfuehren - der Fortschritt bleibt erhalten.",
    "# Nicht aendern: eine Aenderung macht das Notebook unbenutzbar.",
    "# Der Code darf gelesen werden: zum Bauen eigener Notebooks/Inhalte (siehe Vorlage).",
    "# Und ja, man koennte sich damit auch in die Loesungen hacken (Selbstbetrug).")
# the #@title line of the Vorlage (Colab's form title; JupyterLab, VS Code show it when the cell is folded)
TITLE_ASCII = ("#@title DigiChemJN | No document? Play / Run All draws it | "
               "Kein Dokument? Play / Run All zeigt es an")
SPLIT = re.compile(r"\n(?=# ---- [^\n]+ ----\n)")
NAME = re.compile(r"# ---- ([^\n]+?) ----\n")
# the loader: plain Python 3.9+, no IPython, nothing outside the stdlib
LOADER = (
    "def _nbz_run(z, g):\n"
    "    import base64, linecache, re, zlib\n"
    "    for p in re.split(r\"\\n(?=# ---- [^\\n]+ ----\\n)\", zlib.decompress(base64.b64decode(z)).decode()):\n"
    "        m = re.match(r\"# ---- ([^\\n]+?) ----\\n\", p)\n"
    "        n = \"<digichemjn:%s>\" % (m.group(1).split()[0] if m else \"toolkit\")\n"
    "        linecache.cache[n] = (len(p), None, p.splitlines(True), n)\n"
    "        exec(compile(p, n, \"exec\"), g)\n"
    "_nbz_run(_NBZ, globals())\n")
_CARGO = re.compile(r'^_NBZ = (?:"([A-Za-z0-9+/=]+)"|\(\n((?: "[A-Za-z0-9+/=]*"\n)+)\))$', re.M)


def pieces(src):
    """The pieces the loader compiles, with their names (as the loader names them)."""
    out = []
    for p in SPLIT.split(src):
        m = NAME.match(p)
        out.append(("<digichemjn:%s>" % (m.group(1).split()[0] if m else "toolkit"), p))
    return out


def short(src, head, chunk=0, note=None, ascii=False):
    z = base64.b64encode(zlib.compress(src.encode("utf-8"), 9)).decode("ascii")
    if chunk and chunk > 0:
        cargo = "_NBZ = (\n%s)" % "".join(' "%s"\n' % z[i:i + chunk] for i in range(0, len(z), chunk))
    else:
        cargo = '_NBZ = "%s"' % z
    run = list(note) if note else [RUN_LINE]
    assert all((l.startswith("# ") or l == "#") and "\n" not in l for l in run), "shortcell: a note line is not one comment line"
    cell = "\n".join(list(head) + run + [FOLD_OPEN, cargo, LOADER.rstrip("\n"), FOLD_CLOSE]) + "\n"
    if ascii and not cell.isascii():                         # E38a P3
        bad = sorted({c for c in cell if ord(c) > 127})
        raise SystemExit("shortcell: the visible cell is not ASCII: %r" % "".join(bad))
    # the proof, on every build
    if expand(cell) != src:
        raise SystemExit("shortcell: the cargo does not unpack to the cell")
    if "\n".join(p for _, p in pieces(src)) != src:
        raise SystemExit("shortcell: the pieces do not add up to the cell")
    for n, p in pieces(src):
        compile(p, n, "exec")
    return cell


def expand(cell):
    """The text the short cell runs; any other cell comes back unchanged."""
    m = _CARGO.search(cell)
    if not m:
        return cell
    z = m.group(1) or "".join(re.findall(r'"([A-Za-z0-9+/=]*)"', m.group(2)))
    return zlib.decompress(base64.b64decode(z)).decode("utf-8")


def visible_lines(cell):
    return len(cell.rstrip("\n").split("\n"))
