"""E26.3 · Pflichttest (STOP.md, E26 Teil 3, Punkt 4 + Daten für 1/3) — Python workshop.
    python3 tests/regress/py_e26_short.py <notebook.ipynb> [--base <older.ipynb>] [--json out.json]

THE CELL IS SHORT, AND RUNS THE SAME. PyCharm ignores `source_hidden` and
showed all ~2 900 lines of the code cell (v1.70–v1.73). Since E26.3 the cell
is a few lines and one line of cargo (toolkit/shortcell.py). Rows:
  L1  the cell: ≤ 15 lines (E31 C1: + the lines of shortcell.NOTE_BLOCK where the cell
      carries it, the Vorlage: 23); line 1/2 = the head lines (E23.0, E26.1b); a run
      line en/de; the editor-fold pair (collapsed); cargo on ONE line (or the
      Variant-B lines, NB_CELL_CHUNK); Lab/Colab metadata kept (source_hidden,
      cellView form, not editable/deletable)
  L2  the cargo unpacks (shortcell.expand) to a cell that compiles, piece by
      piece under the chapter files' names
  L3  an error keeps its chapter: a probe raised in c03.py comes back with
      <digichemjn:c03.py>, its line in that piece and the line's text
  L4  a real kernel runs it: no error; the outputs (number, mime types, order)
      are those of --base; the run is not slower than --base +10 % (median of 3)
  L5  nbconvert (GitHub / nbviewer preview) renders the file; the cargo line
      is there once, the fold comment too
  D1  the cover for the window (claude/VERTRAG-nbrw-E26.3.md): .nbrw-cover
      hidden inline; title card, lead and "what you will learn" in a
      [data-nbrw-l=en] and a [data-nbrw-l=de] block ("Complex Numbers" /
      "Komplexe Zahlen", German card texts); .nbrw-lang EN|DE; an empty
      .nbrw-cv-tl; 4 button.nbrw-mode-opt[data-mode] with <b>; ▶
      [data-nbrw-act=play] + .nbrw-play-lab; details.nbrw-acct; no
      "Not running yet"
  D2  gating/mode data: .nbreading[data-nbrw-mode] = the run's; chapter 2's
      content in [data-nbrw-gate="calc:t1"] … chapter 7's "calc:t6", chapter 1
      without; data-rw-gate decodes (anchors are ids, order, cguard, states);
      the contents list in both languages ([data-nbrw-l], 7 + 7)
  D3  folds: <details class="nbrw-acc …" open data-acc=<unique id>> with
      data-kind/data-open (Lab's open chapter 1 = 1), practice folds
      data-nbrw-only=calc, coding folds =code; every <div>/<details> of the
      reading copy closed (v1.73: three concept boxes left a <div> open — JS)
  P1  the check as text (data-check, base64 UTF-8 defining _nbrw_check(ns);
      data-pkgs numpy; data-cname): every coding exercise has one; run in a
      FRESH Python (-I, only numpy — as Pyodide would) on the solution →
      ok, on the stub → not ok, and the same (ok, tip) as the kernel's own
      check (_PRUEFE) for both, en and de
v1.73: red (L1 5 000 lines, D1–D3, P1). Owner: Python. exit 0 = REGRESS-PY-E26-SHORT OK.

E28.1 (2026-10-12, Python) — ANY NOTEBOOK, THE TEMPLATE FIRST (Dauerregel 12.10.:
"nur die Vorlage"). What the rows expect is read from the notebook, not typed
for Complex: the titles from its metadata (digichemjn.title / title_de), the
chapters from the cell's pieces (<letter><nn>.py: c01…c07, k01…, m01…), the
probe chapter = the third of them (c03 for Complex, as before), gates t1…t(N−1),
contents N + N, one coding check per code_fold. Behauptete bisher: Complex's
names and counts (7, t6, "Why complex numbers?") — the same rows for Complex.
Without a notebook: --nb vorlage (tests/nbpick.py). Vorlage v1.74: red (L1–L3,
D1–D3: long cell, no window cover)."""
import sys, os, re, json, time, base64, zlib, subprocess, tempfile, statistics, argparse, traceback, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "toolkit"))
import megasrc                                  # noqa: E402
import shortcell                                # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("nb", nargs="?", default=None)
ap.add_argument("--nb", dest="nbname", default="vorlage", help="vorlage | complex | modeling | <file> (when no notebook is given)")
ap.add_argument("--base", default=None)
ap.add_argument("--json", default=None)
ap.add_argument("--runs", type=int, default=3)
A = ap.parse_args()
import nbpick                                   # noqa: E402
A.nb = nbpick.resolve(A.nb or A.nbname)
rows, bad = [], []

def row(name, ok, detail):
    rows.append({"row": name, "ok": bool(ok), "detail": detail})
    print("%-4s %s  %s" % (name, "ok " if ok else "BAD", detail))
    if not ok:
        bad.append(name)

def cell_of(path):
    nb = json.load(open(path, encoding="utf-8"))
    c = max(nb["cells"], key=lambda c: len("".join(c["source"])))
    return nb, c, "".join(c["source"])

nb, cell, src = cell_of(A.nb)
_M = nb.get("metadata", {}).get("digichemjn", {})
T_EN, T_DE = _M.get("title") or "?title?", _M.get("title_de") or "?Titel?"
lines = src.rstrip("\n").split("\n")
meta = cell.get("metadata", {})
full = megasrc.expand(src)
chunked = bool(re.search(r"^_NBZ = \($", src, re.M))
cargo = [l for l in lines if l.startswith("_NBZ = ")]
# E31 C1 (12.10., Nutzer zu v1.77: "darf auch die erste Seite ausfüllen"): a cell that
# carries shortcell.NOTE_BLOCK (one sentence per line, en + de) may have its lines on
# top — behauptete bisher: ≤ 15 lines and line 2 "# Output:" in every notebook
_block = all(l in lines for l in getattr(shortcell, "NOTE_BLOCK", ("\0",)))
lim = (15 + (len(shortcell.NOTE_BLOCK) - 3 if _block else 0)
       + (0 if not chunked else sum(1 for l in lines if re.match(r'^ "[A-Za-z0-9+/=]*"$', l))))
ok = (len(lines) <= lim and lines[0].startswith("#@title DigiChemJN") and (lines[1].startswith("# Output:") or _block)
      # E29 P8 (12.10.): the Vorlage's run line is the warning, en + de (shortcell.NOTE_LINES)
      and (shortcell.RUN_LINE in lines or _block or all(l in lines for l in getattr(shortcell, "NOTE_LINES", ("\0",))))
      and shortcell.FOLD_OPEN in lines and shortcell.FOLD_CLOSE in lines
      and lines.index(shortcell.FOLD_OPEN) < lines.index(shortcell.FOLD_CLOSE) and len(cargo) == 1
      and meta.get("jupyter", {}).get("source_hidden") and meta.get("cellView") == "form"
      and meta.get("editable") is False and meta.get("deletable") is False)
row("L1", ok, "%d lines (want ≤ %d)%s, cargo %d chars on %s, fold %s, metadata %s" % (
    len(lines), lim, "" if lines[:1] and lines[0].startswith("#@title DigiChemJN") else " FIRST LINE " + lines[0][:40],
    len(src) - sum(len(l) + 1 for l in lines if not l.startswith(("_NBZ", ' "'))),
    "Variant B lines" if chunked else "one line", shortcell.FOLD_OPEN in lines,
    {k: meta.get(k) for k in ("editable", "deletable", "cellView")}))

# the notebook's chapters, from the cell's pieces (c01.py, k01.py, m01.py …)
_ALL = [n for n, _ in shortcell.pieces(full)]
CHAPS = [n for n in _ALL if re.match(r"(<digichemjn:)?[a-z]\d\d\.py>?$", n)]
N = len(CHAPS)
PROBE_F = re.sub(r"^<digichemjn:|>$", "", CHAPS[2] if N >= 3 else (CHAPS[-1] if CHAPS else "c03.py"))
PROBE = "<digichemjn:%s>" % PROBE_F
_PCS = dict(shortcell.pieces(full))
NCODE = sum(len(re.findall(r"\bcode_fold\(", _PCS.get(c, ""))) for c in CHAPS)
print("     notebook %s · %r / %r · %d chapters %s · probe %s · %d code folds"
      % (os.path.basename(A.nb), T_EN, T_DE, N, " ".join(re.sub(r"^<digichemjn:|>$", "", c) for c in CHAPS), PROBE_F, NCODE))
try:
    names = []
    for n, p in shortcell.pieces(full):
        compile(p, n, "exec"); names.append(n)
    ok = full != src and len(names) >= 8 and PROBE in names and full.startswith("#@title DigiChemJN")
    row("L2", ok, "%d chars unpacked, %d pieces: %s" % (len(full), len(names), " ".join(x[12:-1] for x in names)))
except Exception as e:
    row("L2", False, "does not compile: %r" % (e,))

# L3 — a probe in c03.py, run like the suites run the cell (plain Python, display stubbed)
try:
    probe = full.replace("# ---- %s ----\n" % PROBE_F, "# ---- %s ----\nraise RuntimeError('probe E26.3')\n" % PROBE_F, 1)
    pcell = shortcell.short(probe, probe.split("\n")[:2]) if probe != full else None
    import matplotlib; matplotlib.use("Agg")
    import IPython.display as ipd
    ipd.display = lambda *a, **k: None
    g = {"__name__": "__main__", "display": lambda *a, **k: None}
    tb = ""
    cwd = os.getcwd(); os.chdir(os.path.dirname(os.path.abspath(A.nb)))
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(pcell, "cell", "exec"), g)
    except RuntimeError:
        tb = traceback.format_exc()
    finally:
        os.chdir(cwd)
    ok = pcell is not None and 'File "%s", line 2' % PROBE in tb and "raise RuntimeError('probe E26.3')" in tb
    row("L3", ok, "traceback: %s" % (" | ".join(l.strip() for l in tb.strip().splitlines()[-3:]) or "none"))
except Exception as e:
    row("L3", False, repr(e))

# L4 — a real kernel
from jupyter_client.manager import start_new_kernel   # noqa: E402

POST = r'''
import json as _j
_res = {}
for _lg in ("en", "de"):
    LANG["value"] = _lg
    for _r in [v for v in _NBRW.values() if v.get("kind") == "code"]:
        _k = _r["task"]
        _NBRW_PY.pop(_k, None)
        _prog = _nbrw_pysrc(_k)
        for _which in ("solution", "stub"):
            _g = {}
            try:
                exec(_r.get(_which) or "", _g)
                _ok, _tip = _PRUEFE[_k](_g)
            except Exception as _e:
                _ok, _tip = None, repr(_e)
            _res["%s|%s|%s" % (_lg, _k, _which)] = {"ok": _ok, "tip": str(_tip), "code": _r.get(_which) or "", "prog": _prog,
                                                   "bad": _NBRW_PY.get(("bad", _k))}
LANG["value"] = "en"
print("@@" + _j.dumps(_res))
'''

def kernel_run(path, post=None):
    _, _, code = cell_of(path)
    home = tempfile.mkdtemp(prefix="e26s_")
    env = {k: v for k, v in os.environ.items() if not k.startswith("DIGICHEM_") and k not in ("PYCHARM_HOSTED", "VSCODE_PID")}
    env["HOME"] = home
    km, kc = start_new_kernel(kernel_name="python3", env=env, cwd=os.path.dirname(os.path.abspath(path)))
    try:
        def drain(mid):
            outs, err, txt = [], None, ""
            while True:
                m = kc.get_iopub_msg(timeout=900)
                if m["parent_header"].get("msg_id") != mid:
                    continue
                t, c = m["msg_type"], m["content"]
                if t in ("display_data", "execute_result"):
                    outs.append(c["data"])
                elif t == "error":
                    err = "%s: %s" % (c["ename"], c["evalue"])
                elif t == "stream":
                    txt += c["text"]
                elif t == "status" and c["execution_state"] == "idle":
                    return outs, err, txt
        t0 = time.time()
        outs, err, _ = drain(kc.execute(code))
        dt = time.time() - t0
        res = None
        if post:
            _, e2, txt = drain(kc.execute(post))
            m = re.search(r"@@(.*)", txt)
            res = json.loads(m.group(1)) if m else {"_err": e2 or txt[-400:]}
        return outs, err, dt, res
    finally:
        km.shutdown_kernel(now=True)

def shape(outs):
    return [sorted(k for k in o if k != "text/plain") for o in outs]

new_t, base_t, outs_new, res = [], [], None, None
for i in range(max(1, A.runs)):
    o, err, dt, r = kernel_run(A.nb, POST if i == 0 else None)
    new_t.append(dt)
    if i == 0:
        outs_new, err_new, res = o, err, r
    if A.base:
        ob, errb, dtb, _ = kernel_run(A.base)
        base_t.append(dtb)
        if i == 0:
            outs_base = ob
if A.base:
    same = shape(outs_new) == shape(outs_base)
    mn, mb = statistics.median(new_t), statistics.median(base_t)
    # not slower than +10 % (faster is no fault: IPython no longer runs its input
    # transformers over ~620 000 characters — measured 11.10.: −9 … −11 %, +1.6 %)
    row("L4", err_new is None and same and mn <= 1.10 * mb,
        "error %s · outputs %d vs base %d (%s) · run %.2f s vs base %.2f s (%+.1f %%), runs %s / %s" % (
            err_new, len(outs_new), len(outs_base), "same kinds" if same else "DIFFERENT KINDS", mn, mb,
            100 * (mn - mb) / mb, [round(x, 2) for x in new_t], [round(x, 2) for x in base_t]))
else:
    row("L4", err_new is None, "error %s · %d outputs · run %.2f s (no --base: time not compared)"
        % (err_new, len(outs_new), statistics.median(new_t)))

# L5 — nbconvert
try:
    from nbconvert import HTMLExporter
    import nbformat
    body, _ = HTMLExporter().from_notebook_node(nbformat.read(A.nb, as_version=4))
    ok = body.count("_NBZ") >= 1 and "editor-fold" in body and len(body) > 10000
    row("L5", ok, "nbconvert HTML %d chars, cargo name %d×, fold comment %s" % (len(body), body.count("_NBZ"), "editor-fold" in body))
except Exception as e:
    row("L5", False, "nbconvert: %r" % (e,))

read = [o.get("text/html", "") for o in outs_new if "class='nbreading'" in o.get("text/html", "")]
h = read[0] if read else ""
# E33 A1: behauptete bisher "the run's HTML string holds the cover and both languages as markup"; the static
# copy now carries them encoded (data-nbrw-o, data-nbrw-put) and the page rebuilds the v1.78 markup (py_e33 R1)
from _nbrw_static import rebuild as _rebuild
h = _rebuild(h)
# D1 cover
m = re.search(r"<div class='nbrw-cover' style='display:none' data-kind='cover' data-lang='(\w+)'>", h)
if m:
    i = h.index(m.group(0)); seg = h[i:h.index("<div class='nbread-line'>", i)]
    blocks = re.findall(r"<div data-nbrw-l='(en|de)'><div style='text-align:center'><div class=\"nbr-nbtitle-card\"", seg)
    en = seg[seg.find("<div data-nbrw-l='en'>"):seg.find("<div data-nbrw-l='de'>")]
    de = seg[seg.find("<div data-nbrw-l='de'>"):seg.find("<div class='nbrw-cv-t")]
    modes = re.findall(r"<button type='button' class='nbrw-mode-opt' role='radio' data-mode='(\w+)' aria-checked='\w+'>"
                       r"<span class='nbrw-mode-ic'>[^<]*</span><b class='nbrw-mode-l'>", seg)
    ok = (blocks == ["en", "de"] and m.group(1) == "en" and T_EN in en and T_DE in de
          and "Was Sie lernen" in de and "What you will learn" in en and "Zeitleiste" in seg
          and modes == ["plain", "calc", "code", "both"] and "<div class='nbrw-lang' role='group'>" in seg
          and "<div class='nbrw-cv-tl'></div>" in seg and "data-nbrw-act='play'" in seg and "nbrw-play-lab" in seg
          and "<details class='nbrw-acct'>" in seg and "Not running yet" not in seg and "Noch nicht ausgef" not in seg
          and 'class="nbtitle-card"' not in seg)
    row("D1", ok, "cover: card blocks %s (en %s, de %s), lang switch %s, timeline slot %s, modes %s, Play %s, account %s, stale line %s, %d chars"
        % (blocks, T_EN in en, T_DE in de, "nbrw-lang" in seg, "nbrw-cv-tl" in seg, modes,
           "data-nbrw-act='play'" in seg, "nbrw-acct" in seg, "Not running yet" in seg, len(seg)))
else:
    row("D1", False, "no .nbrw-cover in the reading version")
# D2 gating
m = re.search(r"data-nbrw-mode='(\w+)' data-rw-gate='([^']+)'", h)
gates = re.findall(r"<div data-nbrw-gate='(\w+):(\w+)'>", h)
toc = re.search(r"<ol class='nbread-toc'>(.*?)</ol>", h, re.S)
tl = re.findall(r"data-nbrw-l='(en|de)'", toc.group(1)) if toc else []
if m:
    g = json.loads(base64.b64decode(m.group(2)))
    ids = set(re.findall(r"""\sid=["']([^"']+)["']""", h))
    miss = [c["a"] for c in g["chap"] if c["a"] not in ids]
    chs = [c for c in g["chap"] if c["n"]]
    ok = (N >= 2 and not miss and g["mode"] == m.group(1) == "both" and g["order"][:min(3, N)] == ["t%d" % k for k in range(1, min(3, N) + 1)]
          and gates == [("calc", "t%d" % k) for k in range(1, N)] and tl.count("en") == tl.count("de") == N
          and len(chs) == N and chs[1]["lock"] == "t1" and chs[1]["shut"] and not chs[0]["shut"]
          and g["cguard"].get("t2") == "t1" and set(g["st"].values()) == {"open"} and g["built"] == {"calc": True, "code": True})
    row("D2", ok, "gates %s · contents en %d / de %d · %d sections (%d chapters), anchors missing %s, order %s, ch2 lock %s shut %s, cguard %d, mode %s"
        % (" ".join("%s:%s" % x for x in gates), tl.count("en"), tl.count("de"), len(g["chap"]), len(chs), miss[:3], g["order"],
           chs[1]["lock"] if len(chs) > 1 else "-", chs[1]["shut"] if len(chs) > 1 else "-", len(g["cguard"]), g["mode"]))
else:
    row("D2", False, "no data-nbrw-mode/data-rw-gate on the reading version")
# D3 folds
det = re.findall(r"<details class='nbrw-acc nbread-acc' open data-acc='([\w-]+)' data-kind='([\w-]*)' data-open='(\d)'([^>]*)>", h)
ch1 = re.search(r"<details class='nbrw-acc nbread-acc' open data-acc='chapter-\d+' data-kind='chapter' data-open='1'[^>]*><summary class='nbread-sum'><h\d class='nbread-h'>", h)
ids = [d[0] for d in det]
onl = {}
for d in det:
    if d[1] in ("practice", "code"):
        onl.setdefault(d[1], set()).update(re.findall(r"data-nbrw-only='(\w+)'", d[3]))
from html.parser import HTMLParser
class _Bal(HTMLParser):
    def __init__(s): super().__init__(); s.st = []; s.bad = 0
    def handle_starttag(s, t, a):
        if t in ("div", "details"): s.st.append(t)
    def handle_endtag(s, t):
        if t in ("div", "details"):
            if s.st and s.st[-1] == t: s.st.pop()
            else: s.bad += 1
_b = _Bal(); _b.feed(re.sub(r"<script.*?</script>", "", h, flags=re.S))
row("D3", len(det) >= 2 * N + 4 and ch1 is not None and len(set(ids)) == len(ids) and onl.get("practice") == {"calc"}
    and onl.get("code") == {"code"} and not _b.st and not _b.bad,
    "%d folds (%s), ids unique %s, chapter 1 open in Lab %s, only %s · open tags left %s, mismatched %d"
    % (len(det), ", ".join(sorted(set(d[1] for d in det))), len(set(ids)) == len(ids), ch1 is not None,
       {k: sorted(v) for k, v in onl.items()}, _b.st[:4], _b.bad))
# P1 the check as text
if not res or "_err" in (res or {}):
    row("P1", False, "kernel post-run failed: %s" % ((res or {}).get("_err")))
else:
    # data-pkgs: what the check imports (Complex: numpy; the template's checks need nothing)
    progs = re.findall(r"data-check='([^']+)' data-pkgs='(?:numpy)?' data-cname='\w+'", h)
    fails, n = [], 0
    runner = ("import sys, json\nd = json.load(sys.stdin)\nout = {}\nfor k, v in d.items():\n"
              "    g = {}\n    ns = {}\n    try:\n        exec(v['code'], g)\n        exec(v['prog'], ns)\n"
              "        ok, tip = ns['_nbrw_check'](g)\n    except Exception as e:\n        ok, tip = None, repr(e)\n"
              "    out[k] = {'ok': ok, 'tip': str(tip)}\nprint(json.dumps(out))\n")
    feed = {k: {"code": v["code"], "prog": v["prog"] or ""} for k, v in res.items()}
    p = subprocess.run([sys.executable, "-I", "-c", runner], input=json.dumps(feed), capture_output=True, text=True,
                       cwd=tempfile.mkdtemp(prefix="e26py_"), timeout=300)
    try:
        got = json.loads(p.stdout)
    except Exception:
        got = {}
        fails.append("runner: " + p.stderr[-300:])
    for k, v in sorted(res.items()):
        lg, key, which = k.split("|")
        n += 1
        w = got.get(k, {})
        want_ok = which == "solution"
        if not v["prog"]:
            fails.append("%s: no program (unresolved %s)" % (k, v["bad"])); continue
        # a stub that crashes inside the check counts as wrong (pruefe: "ran but crashed")
        if v["ok"] is not want_ok and not (which == "stub" and v["ok"] is None):
            fails.append("%s: kernel says %s" % (k, v["ok"])); continue
        if w.get("ok") is not v["ok"] or w.get("tip") != v["tip"]:
            fails.append("%s: text %s %r vs kernel %s %r" % (k, w.get("ok"), w.get("tip", "")[:60], v["ok"], v["tip"][:60]))
    keys = sorted(set(k.split("|")[1] for k in res))
    sizes = [len(base64.b64decode(x)) for x in progs]
    defs = all("def _nbrw_check(ns):" in base64.b64decode(x).decode() for x in progs)
    row("P1", not fails and len(progs) == len(keys) == NCODE >= 1 and defs,
        "data-check %d/%d (%s chars, _nbrw_check %s), %d cases (solution ✓ · stub ✗/crash × en/de) in a fresh Python: %s"
        % (len(progs), len(keys), "–".join(str(x) for x in (min(sizes), max(sizes))) if sizes else "-", defs, n,
           "all as the kernel" if not fails else "; ".join(fails[:4])))

if A.json:
    json.dump(rows, open(A.json, "w"), indent=1, ensure_ascii=False)
print("REGRESS-PY-E26-SHORT", "OK" if not bad else "RED " + " ".join(bad))
sys.exit(0 if not bad else 1)
