"""E28 (2026-10-12, Python) — DIE VORLAGE ENTHÄLT JEDEN BAUSTEIN.
    python3 tests/test_vorlage_cover.py            (from the bundle root or tests/)

Dauerregel (Nutzer 12.10.): developed, built and gated is the TEMPLATE; what the
template does not contain counts as untested. So this suite is red when a
public building block of the toolkit is missing from vorlage/ — and it finds a
new one by itself: every public top-level function (no leading _) of the code
that goes into the notebook cell (toolkit/chapter_template.py,
toolkit/profiles.py) must stand in exactly ONE table of vorlage/ANLEITUNG.md:

  ## Bausteine …               an author places it in a chapter
  ## Setup und Fundament …     it sits in _setup.py, controls.py, refs.py, … or the build
  ## Infrastruktur …           the toolkit calls it itself / the reader calls it (pruefe)
  ## Ruhend …                  public, but in no notebook for now (E25.l)

Rows (exit 1 = red, each with its reason):
  T1  every public function is in one table, none in two, no table row names
      a function the toolkit does not have (a stale row)
  T2  Bausteine + Setup/Fundament: called in vorlage/ (comments do not count),
      in the file the row names first (`k03.py`, `build_vorlage.py` …)
  T3  honesty: Infrastruktur/Ruhend is called by NO built file of Complex or
      Modeling (build script, setup, the chapters the build lists) — what a
      real notebook uses is a block, and a block must be in the template
  T4  the features the order names (STOP E28): slider_plot with 1, 2 and 3
      sliders and with a menu (Dropdown) · numeric_answer with an angle
      (answer = (value, tolerance, period)) · gating locked_by on a chapter
      and on a coding fold · cite + BIB · roadmap.py and refs.py built ·
      notebook_end (the end card) in the build · the cover's series bar (an
      entry "vorlage" in toolkit/card_facts.py SERIES)
Base v1.74 (two chapters): red (T1 no tables, T2 choice_answer, target_exercise …).
Owner: Python. exit 0 = VORLAGE COVER OK."""
import ast, io, os, re, sys, tokenize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOR = os.path.join(ROOT, "vorlage")
CELL_CODE = ("toolkit/chapter_template.py", "toolkit/profiles.py")
TABLES = (("bau", "## Bausteine"), ("fund", "## Setup und Fundament"),
          ("infra", "## Infrastruktur"), ("ruht", "## Ruhend"))
fails, rows = [], []

def row(name, ok, detail):
    rows.append(name)
    print("%-3s %s  %s" % (name, "ok " if ok else "BAD", detail))
    if not ok:
        fails.append(name)

def read(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()

def nocomment(s):
    """The source without its comments (a name in a comment is no call); strings stay —
    the build's cell code (title_card(%r), group_start()) is real code in a string."""
    lines = s.split("\n")
    try:
        for t in tokenize.generate_tokens(io.StringIO(s).readline):
            if t.type == tokenize.COMMENT:
                r, c = t.start
                lines[r - 1] = lines[r - 1][:c]
    except (tokenize.TokenError, IndentationError):
        pass
    return "\n".join(lines)

def calls(src, name):
    return len(re.findall(r"(?<![\w.])%s\(" % re.escape(name), src))

def built_files(d, build):
    """build script + setup + every chapter file the build lists"""
    b = read("%s/%s" % (d, build))
    files = set()
    for v in ("FOUNDATIONAL", "CONTENT", "APPENDIX"):
        m = re.search(v + r"\s*=\s*\[([^\]]*)\]", b)
        files |= set(re.findall(r'"([^"]+\.py)"', m.group(1))) if m else set()
    for pat in (r'PROGRESS\s*=\s*"([^"]+)"', r'SETUP\s*=\s*open\("chapters/([^"]+)"'):
        m = re.search(pat, b)
        if m:
            files.add(m.group(1))
    out = {build: nocomment(b)}
    for f in sorted(files):
        out[f] = nocomment(read("%s/chapters/%s" % (d, f)))
    return out, files

# the public functions of the cell code
pub = []
for f in CELL_CODE:
    t = ast.parse(read(f))
    pub += [n.name for n in t.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")]
pub_set = set(pub)

# the tables of ANLEITUNG.md
anl = read("vorlage/ANLEITUNG.md") if os.path.exists(os.path.join(VOR, "ANLEITUNG.md")) else ""
tab, where = {}, {}
for key, head in TABLES:
    i = anl.find("\n" + head)
    seg = anl[i + 1:] if i >= 0 else ""
    j = seg.find("\n## ", 1)
    seg = seg[:j] if j > 0 else seg
    tab[key] = []
    for m in re.finditer(r"^\|\s*`([A-Za-z_]\w*)`\s*\|([^|]*)\|", seg, re.M):
        tab[key].append(m.group(1))
        where[(key, m.group(1))] = re.findall(r"`([\w.]+\.py)`", m.group(2))
listed = [n for k in tab for n in tab[k]]
dup = sorted(n for n in set(listed) if listed.count(n) > 1)
missing = [n for n in pub if n not in set(listed)]
stale = sorted(n for n in set(listed) if n not in pub_set)
row("T1", not dup and not missing and not stale and all(tab.values()),
    "%d public functions · tables %s · unlisted %s · in two tables %s · stale rows %s"
    % (len(pub), {k: len(v) for k, v in tab.items()}, missing[:12] or "none", dup or "none", stale or "none"))

# T2 — in the template, in the named file
V, vfiles = built_files("vorlage", "build_vorlage.py")
vsrc = "\n".join(V.values())
absent, wrong_place = [], []
for key in ("bau", "fund"):
    for n in tab[key]:
        if n not in pub_set:
            continue
        if not calls(vsrc, n):
            absent.append(n); continue
        w = where.get((key, n)) or []
        if not w or not calls(V.get(w[0], ""), n):
            wrong_place.append("%s→%s" % (n, w[0] if w else "?"))
row("T2", not absent and not wrong_place,
    "%d blocks + %d setup/foundation · not in the template: %s · not in the named file: %s"
    % (len(tab["bau"]), len(tab["fund"]), absent or "none", wrong_place or "none"))

# T3 — what Complex/Modeling use is in the template
used = {}
for d, b in (("complex", "build_complex.py"), ("modeling", "build_modeling.py")):
    src, _ = built_files(d, b)
    for f, s in src.items():
        for n in tab["infra"] + tab["ruht"] + missing:
            if n in pub_set and calls(s, n):
                used.setdefault(n, set()).add("%s/%s" % (d, f))
row("T3", not used, "infrastructure/dormant called by a real notebook: %s"
    % ({k: sorted(v)[:2] for k, v in used.items()} or "none"))

# T4 — the features the order names
feats, bad = {}, []
sliders, menu = set(), False
period = gate_ch = gate_code = False
for f, s in V.items():
    if not f.startswith("k"):
        continue
    for node in ast.walk(ast.parse(s)):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        fn, kw = node.func.id, {k.arg: k.value for k in node.keywords}
        if fn in ("slider_plot", "target_exercise") and len(node.args) > 1 and isinstance(node.args[1], ast.Dict):
            d = node.args[1]
            dd = [isinstance(v, ast.Call) and getattr(v.func, "id", "") == "Dropdown" for v in d.values]
            if fn == "slider_plot":                  # sliders = the controls that are no menu
                sliders.add(len(dd) - sum(dd))
            menu |= any(dd)
        if fn == "numeric_answer" and "answer" in kw:
            period |= any(isinstance(t, ast.Tuple) and len(t.elts) == 3 for t in ast.walk(kw["answer"]))
        if fn == "build_chapter" and "locked_by" in kw:
            gate_ch = True
        if fn == "code_fold" and "locked_by" in kw:
            gate_code = True
setup = V.get("_setup.py", "")
b = V["build_vorlage.py"]
feats = {"slider_plot 1/2/3": sorted(sliders), "menu": menu, "angle period": period,
         "locked_by chapter/code": (gate_ch, gate_code),
         "cite + BIB": bool(calls(vsrc, "cite")) and bool(re.search(r"^BIB\s*=\s*\{\s*\n\s*1:", setup, re.M)),
         "roadmap/refs built": "roadmap.py" in vfiles and "refs.py" in vfiles,
         "end card": bool(calls(b, "notebook_end")),
         "series bar": bool(re.search(r'^\s*"vorlage":\s*\{', read("toolkit/card_facts.py"), re.M))}
ok = ({1, 2, 3} <= sliders and menu and period and gate_ch and gate_code and feats["cite + BIB"]
      and feats["roadmap/refs built"] and feats["end card"] and feats["series bar"])
row("T4", ok, " · ".join("%s %s" % kv for kv in feats.items()))

print("VORLAGE COVER OK" if not fails else "VORLAGE COVER RED " + " ".join(fails))
sys.exit(1 if fails else 0)
