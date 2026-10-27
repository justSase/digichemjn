"""E21 · test_regress — the Python workshop's part (points 6, 7, 11, 13, 14),
in a real JupyterLab under Playwright. Complex AND Modeling.

    python3 tests/regress/py_e21.py <complex.ipynb> <modeling.ipynb> [--only R6,R7] [--old]

Every check names its owner — the workshop that has to make it green — and
what the reader saw when it was red. Run first against v1.60/v1.61: where the
reader saw a fault, the check MUST be red (otherwise it checks the wrong
thing); the table of that first run is in the chronicle of 2026-10-02.

  R7   version line: after Run All, in each window of the drawer, VISIBLE
       elements whose text holds "build 20xx": ⚙ exactly 1, 👤 📚 ⌨ 0; no element
       anywhere with a title "build 20xx" (cold cover and running document).
       Owner: Python (markup), CSS if a stylesheet shows it again; the one
       line is small: font-size ≤ 12 px (CSS — v1.61 head 17 px, py-E21.7 in
       the ⚙ cell 15 px from a drawer rule).
  R14  crest: no `svg.nborn-crest` (the three dots under the title pill),
       visible or not. Owner: Python.
  R13  appendix: the panel's Appendix holds "Conclusion" and no "Summary" or
       "Glossary"; no mark "Setup and how the numbers are drawn" (panel, cover
       before Play); the roadmap chapter ends with a mailto:samuel.wiese@gmx.de.
       Owner: Python.
  R11  restart cards under "End of the guide": every `.nbend-mode` carries the
       cover card's parts (.nbmode-ic/-l/-d) and the cards follow the cover's
       order (Python); the cover's first card is "plain" (JS, MODE_OPT).
  R6   the mode, kernel side (Python) and page side (JS):
       R6f  a mode file beside the notebook (<folder>/.digichemjn/<id>.mode —
            what the page can write before a restart, Jupyter contents API),
            newer than ~/.digichemjn/<id>.mode: Restart + Run All builds it in
            the FIRST run. Owner: Python.
       R6i  the inbox: "<other id>:code" changes nothing; "<own id>:code" stores
            it (~ file), answers data-ok=1, and ⚙ "Content" shows it. Python.
       R6c  the reader's way (Video 3/4): Complex ran once and was saved, is
            opened again (fresh kernel, cover alive from the saved outputs);
            ONE click on "Pen & paper" → aria-checked and stored under
            `digichemjn.mode.<id>` (JS); Play → exactly one run, built calc
            (JS + Python: the page writes the file of R6f or the inbox of R6i
            BEFORE the restart). v1.61: stored nothing (→ __pending), runs
            both, then calc — "gilt erst beim nächsten Neustart".
       R6x  two notebooks in one window, both run: in Complex, "Start again
            with … Pen & paper" → Complex rebuilds as calc in ONE run;
            Modeling's file and `digichemjn.mode.modeling` unchanged, Modeling
            still built "both". Owner: JS (which notebook it tells) + Python
            (the kernel takes only its own id). NOTE: green on v1.61 in this
            sequence — it does not yet reproduce the reader's "one notebook
            changes the other"; kept as a guard, the sequence that shows it is
            still to be found (--old: a v1.54 `__pending` without a title is
            adopted by whichever notebook first has an id).
--old  the same with a browser store from an older version preloaded (v1.54
       keys, written by hand: mode/zoom/theme/skin/orient/pending); the
       Hauptwerkstatt's scaffold carries the real v1.54 store.
exit 0 = REGRESS-PY OK."""
import sys, os, re, json, time, shutil, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from lab_keys import CHROME, ensure_lab, kill_sessions, open_nb, restart_run_all
from playwright.sync_api import sync_playwright
sys.path.insert(0, HERE)
from _py_page import page_whole      # E24 Stufe 2 Rest 2: the page whole first


rows, fails = [], []
def check(tag, owner, ok, got, want):
    rows.append("%-5s %-6s %-4s got %s · want %s" % (tag, owner, "ok" if ok else "RED", got, want))
    if not ok:
        fails.append("%s (%s): got %s, want %s" % (tag, owner, got, want))
def tap(el):
    """a real click; when JupyterLab's toasts lie over it, the element's own click()"""
    try:
        el.click(timeout=5000)
    except Exception:
        el.evaluate("e => e.click()")

def want(t):
    return ONLY is None or t in ONLY

OLD_STORE = {   # keys an older browser holds (v1.54 era), the reader's "used" store
    "digichemjn.mode.__pending": "code\n", "digichemjn.zoom.v1": "130",
    "digichemjn.theme.v1": "light", "digichemjn.skin.v1": "minimal",
    "digichemjn.orient.v1": "vert", "digichemjn.readline.v1": "220"}

def nb_name(src, tag):
    name = "rg_%s_%s" % (tag, os.path.basename(src))
    shutil.copy(src, os.path.join(LAB, name))
    return name

def clean_store():
    for f in glob.glob(os.path.join(KHOME, ".digichemjn", "*")) + glob.glob(os.path.join(LAB, ".digichemjn", "*")):
        try: os.remove(f)
        except Exception: pass

def preload(ctx):
    if OLD:
        ctx.add_init_script("(function(s){try{if(!sessionStorage.getItem('rg-old')){for(var k in s)localStorage.setItem(k,s[k]);"
                            "sessionStorage.setItem('rg-old','1');}}catch(e){}})(%s)" % json.dumps(OLD_STORE))

def wait_idle(pg, secs=90):
    for _ in range(secs):
        pg.wait_for_timeout(1000)
        st = pg.evaluate("() => (document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator, .jp-Notebook-ExecutionIndicator')||{getAttribute:()=>null}).getAttribute('data-status')")
        if st == "idle": return True
    return False

FEED = """() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var f = P && P.querySelectorAll('.nbfeed[data-progress]'); f = f && f.length ? f[f.length-1] : null;
  return f ? {run: f.getAttribute('data-nbid'), mode: f.getAttribute('data-nbmode')} : null; }"""

def runs_after(pg, secs, old=None):
    """distinct run ids (and modes) of the visible notebook over `secs`
    seconds, the run `old` (the one before the restart) left out"""
    seen = []
    for _ in range(secs * 2):
        pg.wait_for_timeout(500)
        f = pg.evaluate(FEED)
        if f and f["run"] != old and (not seen or seen[-1][0] != f["run"]): seen.append((f["run"], f["mode"]))
    return seen

def open_nb_ctx(b, name, w=1400, h=900):
    """open_nb with the --old store preloaded; one retry on a fresh copy when
    the palette misfired (open_nb refuses a notebook that is not 2 cells)"""
    try:
        return _open_nb_ctx(b, name, w, h)
    except RuntimeError as e:
        rows.append("(retry %s: %s)" % (name, e))
        kill_sessions(BASE)
        src = [s for s in (CX, MOD) if s.endswith(name.split("_", 2)[2])][0]
        shutil.copy(src, os.path.join(LAB, name))
        return _open_nb_ctx(b, name, w, h)

def _open_nb_ctx(b, name, w=1400, h=900):
    """open_nb with the --old store preloaded (open_nb makes its own context)"""
    if not OLD:
        return open_nb(b, BASE, name, w, h)
    orig = b.new_context
    def nc(**kw):
        c = orig(**kw); preload(c); return c
    b.new_context = nc
    try:
        return open_nb(b, BASE, name, w, h)
    finally:
        b.new_context = orig

VIS = r"""(sel) => [].filter.call(document.querySelectorAll(sel), function(e){
  for (var p = e; p && p !== document.body; p = p.parentElement){ var q = getComputedStyle(p);
    if (q.display === 'none' || q.visibility === 'hidden' || +q.opacity === 0) return false; }
  var r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; }).length"""
# E21 Rest (2026-10-03, Hauptwerkstatt-Tor „pair“): the notebook IN FRONT. With two
# notebooks open in one window, `document` holds both; every check below reads
# only the visible panel (P) and the shared host #nbpanel-root (H), which shows
# and borrows the controls of the notebook in front. BEHAUPTETE BISHER: R11 over
# `document` saw the end cards of both notebooks (calc, code, calc, code) and
# was red although each notebook was right; R13/R14/R6i/the R7 tooltips read
# `document` too and were green only because both notebooks were the same build.
FRONT = r"""var P = (function(){ var ps = document.querySelectorAll('.jp-NotebookPanel');
    for (var i = 0; i < ps.length; i++) if (!ps[i].classList.contains('lm-mod-hidden') && ps[i].getBoundingClientRect().width > 0) return ps[i];
    return null; })(), H = document.getElementById('nbpanel-root');
  var inP = function(sel){ return P ? [].slice.call(P.querySelectorAll(sel)) : []; };
  var inPH = function(sel){ return (H ? [].slice.call(H.querySelectorAll(sel)) : []).concat(inP(sel)); };"""
VER = r"""() => { var re = /build 20\d\d/, n = 0, t = 0; """ + FRONT + r"""
  function vis(e){ for (var p = e; p && p !== document.body; p = p.parentElement){ var q = getComputedStyle(p);
    if (q.display === 'none' || q.visibility === 'hidden' || +q.opacity === 0) return false; }
    var r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; }
  var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) { var x = w.currentNode, e = x.parentElement;
    if (e && re.test(x.nodeValue) && !/^(SCRIPT|STYLE)$/.test(e.tagName) && !e.closest('.jp-InputArea') && vis(e)) n++; }
  inPH('[title]').forEach(function(e){ if (re.test(e.getAttribute('title'))) t++; });
  return {vis: n, titles: t}; }"""


# ======================================================================
# THE RUNNER'S WAY (Vertrag PATCH-hw-E21.0): one function per check,
# fn(pg, ctx) -> (ok, detail), on the page after Run All of one matrix row.
# The checks that need two notebooks, a restart or the kernel's files (R6f,
# R6c, R6x, and R7 on the cold cover) stay in the standalone run below.
# The inbox check (R6i) changes the stored mode: it is the last one.
# ======================================================================
def _ver_in(pg, btn):
    try:
        tap(pg.wait_for_selector("#nbpanel-root .nbbtn.%s" % btn, state="attached", timeout=8000))
        pg.wait_for_timeout(900)
        v = pg.evaluate(VER)
        fs = pg.evaluate("""() => { var e = [].filter.call(document.querySelectorAll('#nbpanel-root .nbbuild'),
            function(x){ return x.getBoundingClientRect().height > 0; })[0];
            return e ? parseFloat(getComputedStyle(e).fontSize) : null; }""")
    finally:
        pg.keyboard.press("Escape"); pg.wait_for_timeout(500)
    return v, fs

def t_r7(pg, ctx):
    """R7 (Python): the version line once, in ⚙ only; no title stamp."""
    try:
        doc = pg.evaluate(VER)
        got = {b: _ver_in(pg, b)[0]["vis"] for b in ("nbgear", "nbprofile", "nbseries", "nbkeys")}
    except Exception as e:
        return False, "BAD %s" % str(e)[:80]
    ok = doc["titles"] == 0 and got == {"nbgear": 1, "nbprofile": 0, "nbseries": 0, "nbkeys": 0}
    return ok, "titles %d · visible per window %s (want ⚙ 1, others 0)" % (doc["titles"], got)

def t_r7_small(pg, ctx):
    """R7 (CSS): the one line is small (≤ 12 px)."""
    try:
        v, fs = _ver_in(pg, "nbgear")
    except Exception as e:
        return False, "BAD %s" % str(e)[:80]
    return (fs is not None and fs <= 12), "⚙ version line %s px (want ≤ 12)" % fs

def t_r14(pg, ctx):
    """R14 (Python): no crest under the title pill."""
    n = pg.evaluate("() => { " + FRONT + " return inP('svg.nborn-crest').length; }")
    t = pg.evaluate("() => { " + FRONT + " return inP('.nbtitle-doc').length; }")
    if not t:
        return False, "BAD no title card in the document"
    return n == 0, "%d crest(s)" % n

def t_r13(pg, ctx):
    """R13 (Python): Conclusion instead of Summary + Glossary, no Setup, contact at the end of the roadmap."""
    ok0, s0 = page_whole(pg)
    if not ok0: return False, s0
    r = pg.evaluate(r"""() => { """ + FRONT + r"""
      var names = [].map.call(document.querySelectorAll('#nbpanel-root .nbmap-node'), function(a){
          return (a.getAttribute('title') || a.textContent || '').trim(); });
      var a = inP('a[href="mailto:samuel.wiese@gmx.de"]')[0], box = a && a.closest('.nbbox');
      var t = box ? box.textContent.trim() : '';
      return {n: names.length,
              conc: names.filter(function(n){ return /^Conclusion\b/.test(n); }).length,
              summ: names.filter(function(n){ return /^(Summary|Glossary)\b/.test(n); }).length,
              setup: /Setup and how the numbers are drawn/.test((P && P.textContent) || '') ? 1 : 0,
              tail: t.slice(-40)}; }""")
    if not r["n"]:
        return False, "BAD no panel marks"
    ok = r["conc"] >= 1 and r["summ"] == 0 and r["setup"] == 0 and r["tail"].endswith("samuel.wiese@gmx.de.")
    return ok, "Conclusion %d · Summary/Glossary %d · Setup %d · roadmap ends %r" % (r["conc"], r["summ"], r["setup"], r["tail"])

def _cards(pg):
    return pg.evaluate(r"""() => { """ + FRONT + r""" return {
      end: inP('.nbend-go .nbend-mode').map(function(b){
        return [b.getAttribute('data-mode'), !!(b.querySelector('.nbmode-ic') && b.querySelector('.nbmode-l') && b.querySelector('.nbmode-d'))]; }),
      cov: inP('.nbcover .nbmode .nbmode-opt').map(function(b){ return b.getAttribute('data-mode'); })}; }""")

def t_r11(pg, ctx):
    """R11 (Python): the restart cards carry the cover card's parts, in the cover's order."""
    ok0, s0 = page_whole(pg)
    if not ok0: return False, s0
    r = _cards(pg)
    order = ["plain", "calc", "code", "both"]
    em = [m for m, _ in r["end"]]
    if not em:
        return False, "BAD no restart cards under the end"
    ok = all(x for _, x in r["end"]) and em == sorted(em, key=order.index)
    return ok, "end cards %s, parts %s" % (em, [x for _, x in r["end"]])

def t_r11_cover(pg, ctx):
    """R11 (JS): plain is the first card on the cover."""
    c = _cards(pg)["cov"]
    if not c:
        return False, "BAD no mode cards on the cover"
    return c[0] == "plain", "cover cards %s (want plain first)" % c

def t_r6i(pg, ctx):
    """R6i (Python): the inbox takes only this notebook's id; ⚙ Content follows."""
    me = ctx.get("id") or ""
    # E24 Stufe 2 (2026-10-07): in the v1.67 gate R6i said "no inbox" in 6 of 12
    # rows (never in pair rows), green alone and in shorter sequences; not
    # reproduced here in 4 full rows + 8 short ones. The inbox is the LAST
    # output of a run (finalizers, before the panel), so a run still going —
    # a rebuild an earlier test of the row left behind — is the likeliest
    # reader of "none". Precondition now: the notebook in front idle, no
    # loading view (≤ 90 s; how long it took is in the detail). Still none →
    # red, with what the page holds (document-wide, the attic, the tab, the run).
    PAGE = """() => { """ + FRONT + """ var f = inP('.nbfeed[data-nbid]'), ind = P && P.querySelector('.jp-Notebook-ExecutionIndicator');
        var tab = document.querySelector('.lm-DockPanel .lm-TabBar-tab.lm-mod-current .lm-TabBar-tabLabel');
        return {inbox: inPH('.nbctl-modein input').length, doc: document.querySelectorAll('.nbctl-modein input').length,
                attic: document.querySelectorAll('#nbctl-attic .nbctl-modein').length,
                panels: document.querySelectorAll('.jp-NotebookPanel').length, tab: tab ? tab.textContent.trim() : null,
                run: f.length ? f[f.length - 1].getAttribute('data-nbid') : null, mode: f.length ? f[f.length - 1].getAttribute('data-nbmode') : null,
                busy: ind ? ind.getAttribute('data-status') : null, load: !!document.querySelector('#nbload:not(.nbload-out)'),
                outs: inP('.jp-OutputArea-output').length, cover: inP('.nbcover-out[data-nbcov]').length}; }"""
    s0 = pg.evaluate(PAGE); t0 = time.time(); s = s0
    while (s["busy"] not in (None, "idle") or s["load"]) and time.time() - t0 < 90:
        pg.wait_for_timeout(1000); s = pg.evaluate(PAGE)
    waited = round(time.time() - t0)
    pre = "" if not waited else "waited %d s for the notebook (busy %s, loading %s, run %s → %s) · " % (
        waited, s0["busy"], s0["load"], s0["run"], s["run"])
    if s["busy"] not in (None, "idle") or s["load"]:
        return False, "BAD the notebook in front is not idle after 90 s · page: %s" % s
    # E24 Stufe 2 Rest 2: in the v1.67 gate the inbox was gone because the page
    # had lost widget models on a reload before (J23.pe), not because of the inbox
    ok0, s1 = page_whole(pg)
    if not ok0: return False, pre + s1
    if not s["inbox"]:
        return False, pre + "no inbox .nbctl-modein (v1.61: none) · page: %s · before: %s" % (s, s0)
    def inbox(text):
        pg.evaluate("""(t) => { """ + FRONT + """ inPH('.nbctl-modein input').forEach(function(i){
            i.value = t; i.dispatchEvent(new Event('input', {bubbles: true})); i.dispatchEvent(new Event('change', {bubbles: true})); }); }""", text)
        pg.wait_for_timeout(1500)
        return pg.evaluate("""() => { """ + FRONT + """ var r = inPH('.nbctl-modein-res'); r = r[r.length-1];
            return r ? [r.getAttribute('data-ok'), r.getAttribute('data-why')] : null; }""")
    r1 = inbox("some-other-notebook:calc")
    r2 = inbox(me + ":calc")
    dd = pg.evaluate("""() => { """ + FRONT + """ var s = null, x = inPH('.nbctl-difficulty select').filter(function(x){
          return [].some.call(x.options, function(o){ return /Only\\s+calculating/.test(o.textContent); }); })[0];
      if (x) [].forEach.call(x.options, function(o){ if (/Only\\s+calculating/.test(o.textContent) && x.selectedIndex === o.index) s = 'calc'; }); return s; }""")
    ok = r1 == ["0", "other"] and r2 == ["1", "stored"] and dd == "calc"
    return ok, pre + "foreign %s · own %s · ⚙ Content %s" % (r1, r2, dd)

TESTS = [("PY-R7 version line once, in ⚙ only", t_r7),
         ("PY-R7b version line small (CSS)", t_r7_small),
         ("PY-R14 no crest under the title pill", t_r14),
         ("PY-R13 Conclusion, no Setup, contact", t_r13),
         ("PY-R11 restart cards = cover cards", t_r11),
         ("PY-R11c plain first on the cover (JS)", t_r11_cover),
         ("PY-R6i mode inbox: own id only", t_r6i)]


def main():
    global CX, MOD, ONLY, OLD, BASE, LAB, KHOME, IDS
    ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
    CX, MOD = ARGS[0], ARGS[1]
    ONLY = None
    for a in sys.argv[1:]:
        if a.startswith("--only"):
            ONLY = set(sys.argv[sys.argv.index(a) + 1].split(",")) if a == "--only" else set(a.split("=", 1)[1].split(","))
    OLD = "--old" in sys.argv
    BASE, LAB = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899"))
    KHOME = os.environ.get("DIGICHEM_KERNEL_HOME") or os.path.expanduser("~")
    IDS = {CX: "complex-numbers", MOD: "intro-modeling"}
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for src, nbk in ((CX, "C"), (MOD, "M")):
            nid = IDS[src]
            # ---------------------------------------------------------------- R7/R14/R13/R11 (one run)
            if want("R7") or want("R14") or want("R13") or want("R11"):
                kill_sessions(BASE); clean_store()
                name = nb_name(src, "a")
                # cold cover first (no run): no build stamp in a title
                ctx0 = b.new_context(viewport={"width": 1400, "height": 900}); preload(ctx0)
                pg0 = ctx0.new_page(); pg0.goto(BASE + "/lab/tree/" + name + "?reset")
                pg0.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=60000)
                pg0.wait_for_timeout(2500)
                if pg0.query_selector(".jp-Dialog"): pg0.keyboard.press("Escape")
                cold = pg0.evaluate(VER)
                cold_setup = pg0.evaluate("() => [].filter.call(document.querySelectorAll('.nbcover .nbtl-nm, .nbcover [title]'), function(e){ return /Setup and how/.test(e.textContent + ' ' + (e.getAttribute('title')||'')); }).length")
                ctx0.close(); kill_sessions(BASE)
                ctx, pg, errs = open_nb_ctx(b, name)
                doc = pg.evaluate(VER)
                if want("R7"):
                    check("R7", "Py", cold["titles"] == 0, "%s: %d title(s) on the cold cover" % (nbk, cold["titles"]), "0")
                    check("R7", "Py", doc["titles"] == 0, "%s: %d title(s) after Run All" % (nbk, doc["titles"]), "0")
                    for btn, n in (("nbgear", 1), ("nbprofile", 0), ("nbseries", 0), ("nbkeys", 0)):
                        try:
                            wait_idle(pg, 60)                          # a rebuild (old store) runs first
                            tap(pg.wait_for_selector("#nbpanel-root .nbbtn.%s" % btn, state="attached", timeout=8000))
                            pg.wait_for_timeout(900)
                            v = pg.evaluate(VER)["vis"]
                            if btn == "nbgear":       # "klein": the one line is small (CSS: no rule may blow it up)
                                fs = pg.evaluate("""() => { var e = [].filter.call(document.querySelectorAll('#nbpanel-root .nbbuild'),
                                    function(x){ return x.getBoundingClientRect().height > 0; })[0];
                                    return e ? parseFloat(getComputedStyle(e).fontSize) : null; }""")
                                check("R7", "CSS", fs is not None and fs <= 12, "%s: ⚙ version line %s px" % (nbk, fs), "≤ 12 px")
                            pg.keyboard.press("Escape"); pg.wait_for_timeout(500)
                        except Exception as e:
                            v = "no button (%s)" % str(e)[:40]
                        check("R7", "Py", v == n, "%s: %s window shows the version %s×" % (nbk, btn, v), n)
                if want("R14"):
                    c = pg.evaluate("() => document.querySelectorAll('svg.nborn-crest').length")
                    check("R14", "Py", c == 0, "%s: %d crest(s) under the title pill" % (nbk, c), "0")
                if want("R13"):
                    r = pg.evaluate(r"""() => {
                      var names = [].map.call(document.querySelectorAll('#nbpanel-root .nbmap-node'), function(a){
                          return (a.getAttribute('title') || a.textContent || '').trim(); });
                      var txt = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)').textContent;
                      var mail = [].slice.call(document.querySelectorAll('a[href^="mailto:"]')).map(function(a){ return a.getAttribute('href'); });
                      return {conc: names.filter(function(n){ return /^Conclusion\b/.test(n); }).length,
                              summ: names.filter(function(n){ return /^(Summary|Glossary)\b/.test(n); }).length,
                              setup: names.filter(function(n){ return /^Setup and how/.test(n); }).length,
                              setupTxt: /Setup and how the numbers are drawn/.test(txt), mail: mail}; }""")
                    check("R13", "Py", r["conc"] >= 1 and r["summ"] == 0,
                          "%s: panel marks Conclusion %d · Summary/Glossary %d" % (nbk, r["conc"], r["summ"]), "≥ 1 · 0")
                    check("R13", "Py", r["setup"] == 0 and not r["setupTxt"] and cold_setup == 0,
                          "%s: Setup mark %d · in the text %s · on the cold cover %d" % (nbk, r["setup"], r["setupTxt"], cold_setup), "0 · False · 0")
                    check("R13", "Py", "mailto:samuel.wiese@gmx.de" in r["mail"],
                          "%s: mailto links %s" % (nbk, r["mail"]), "mailto:samuel.wiese@gmx.de")
                    last = pg.evaluate("""() => { var a = document.querySelector('a[href="mailto:samuel.wiese@gmx.de"]');
                        var box = a && a.closest('.nbbox'); if (!box) return null;
                        var t = box.textContent.trim(); return t.slice(t.length - 40); }""")
                    check("R13", "Py", bool(last) and last.endswith("samuel.wiese@gmx.de."),
                          "%s: roadmap box ends with %r" % (nbk, last), "… samuel.wiese@gmx.de.")
                if want("R11"):
                    r = pg.evaluate(r"""() => {
                      var end = [].map.call(document.querySelectorAll('.nbend-go .nbend-mode'), function(b){
                        return {m: b.getAttribute('data-mode'), parts: !!(b.querySelector('.nbmode-ic') && b.querySelector('.nbmode-l') && b.querySelector('.nbmode-d'))}; });
                      var cov = [].map.call(document.querySelectorAll('.nbcover .nbmode .nbmode-opt'), function(b){ return b.getAttribute('data-mode'); });
                      return {end: end, cov: cov}; }""")
                    order = ["plain", "calc", "code", "both"]
                    em = [x["m"] for x in r["end"]]
                    check("R11", "Py", bool(em) and all(x["parts"] for x in r["end"]) and em == sorted(em, key=order.index),
                          "%s: end cards %s, cover parts %s" % (nbk, em, [x["parts"] for x in r["end"]]), "cover order, all with ic/l/d")
                    check("R11", "JS", bool(r["cov"]) and r["cov"][0] == "plain",
                          "%s: cover cards %s" % (nbk, r["cov"]), "plain first")
                if errs:
                    pe = [e for e in errs if e.startswith("pageerror")]
                    check("err", "all", not pe, "%s: page errors %s" % (nbk, pe[:2]), "none")
                ctx.close()
            # ---------------------------------------------------------------- R6f
            if want("R6"):
                kill_sessions(BASE); clean_store()
                name = nb_name(src, "f")
                ctx, pg, errs = open_nb_ctx(b, name)          # first run: both
                os.makedirs(os.path.join(KHOME, ".digichemjn"), exist_ok=True)
                os.makedirs(os.path.join(LAB, ".digichemjn"), exist_ok=True)
                open(os.path.join(KHOME, ".digichemjn", nid + ".mode"), "w").write("both")
                time.sleep(1.2)
                open(os.path.join(LAB, ".digichemjn", nid + ".mode"), "w").write("code")   # as the page would PUT it
                old = (pg.evaluate(FEED) or {}).get("run")
                t = restart_run_all(pg)
                seen = runs_after(pg, 45, old)
                first = seen[0][1] if seen else None
                check("R6f", "Py", first == "code",
                      "%s: file beside the notebook 'code' (newer) → runs %s" % (nbk, [s[1] for s in seen]), "first run code")
                # ------------------------------------------------------------ R6i
                ok_inbox = pg.evaluate("() => document.querySelectorAll('.nbctl-modein input').length")
                def inbox(text):
                    pg.evaluate("""(t) => [].forEach.call(document.querySelectorAll('.nbctl-modein input'), function(i){
                        i.value = t; i.dispatchEvent(new Event('input', {bubbles: true})); i.dispatchEvent(new Event('change', {bubbles: true})); })""", text)
                    pg.wait_for_timeout(1500)
                    return pg.evaluate("""() => { var r = document.querySelectorAll('.nbctl-modein-res');
                        return r.length ? {ok: r[r.length-1].getAttribute('data-ok'), why: r[r.length-1].getAttribute('data-why')} : null; }""")
                fh = os.path.join(KHOME, ".digichemjn", nid + ".mode")
                before = open(fh).read() if os.path.exists(fh) else None
                r1 = inbox(("intro-modeling" if nbk == "C" else "complex-numbers") + ":calc")
                after1 = open(fh).read() if os.path.exists(fh) else None
                check("R6i", "Py", ok_inbox >= 1 and r1 and r1["ok"] == "0" and after1 == before,
                      "%s: inboxes %d · foreign id → %s · file %r → %r" % (nbk, ok_inbox, r1, before, after1), "≥ 1 · ok 0 · unchanged")
                r2 = inbox(nid + ":calc")
                after2 = open(fh).read() if os.path.exists(fh) else None
                dd = pg.evaluate("""() => { var s = null; document.querySelectorAll('.nbctl-difficulty select').forEach(function(x){
                      [].forEach.call(x.options, function(o){ if (/Only\\s+calculating/.test(o.textContent) && x.selectedIndex === o.index) s = 'calc'; }); }); return s; }""")
                check("R6i", "Py", r2 and r2["ok"] == "1" and after2 == "calc" and dd == "calc",
                      "%s: own id → %s · file %r · ⚙ Content %s" % (nbk, r2, after2, dd), "ok 1 · 'calc' · calc")
                ctx.close()
            # ---------------------------------------------------------------- R6c
            if want("R6"):
                # the reader's way (Video 3/4): a notebook that ran once and was
                # saved is opened again — kernel fresh, the cover alive from the
                # saved outputs. ONE click on a card, then Play.
                kill_sessions(BASE); clean_store()
                name = nb_name(src, "c")
                ctx, pg, errs = open_nb_ctx(b, name)
                pg.keyboard.press("Control+s"); pg.wait_for_timeout(3000)
                old = (pg.evaluate(FEED) or {}).get("run")
                kill_sessions(BASE); pg.wait_for_timeout(1500)
                pg.goto(BASE + "/lab/tree/" + name); pg.wait_for_timeout(8000)
                if pg.query_selector(".jp-Dialog"): pg.keyboard.press("Enter"); pg.wait_for_timeout(2000)
                card = pg.query_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .nbcover .nbmode-opt[data-mode='calc']")
                if card:
                    card.scroll_into_view_if_needed(); tap(card); pg.wait_for_timeout(700)
                st = pg.evaluate("""(k) => { var c = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .nbcover .nbmode-opt[data-mode="calc"]');
                    return {checked: c && c.getAttribute('aria-checked'), ls: localStorage.getItem(k)}; }""", "digichemjn.mode." + nid)
                check("R6c", "JS", bool(card) and st["checked"] == "true" and st["ls"] == "calc",
                      "%s: one click on Pen & paper → aria-checked %s, stored %r" % (nbk, st["checked"], st["ls"]), "true · 'calc'")
                play = pg.query_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .nbcover-play")
                if play:
                    play.scroll_into_view_if_needed(); tap(play)
                    if pg.query_selector(".jp-Dialog"): pg.keyboard.press("Enter")
                seen = runs_after(pg, 90, old) if play else []
                check("R6c", "JS+Py", [x[1] for x in seen] == ["calc"],
                      "%s: Play after the click → runs %s" % (nbk, [x[1] for x in seen]), "['calc'] (one run)")
                ctx.close()
        # -------------------------------------------------------------------- R6x
        if want("R6"):
            kill_sessions(BASE); clean_store()
            nc, nm = nb_name(CX, "x"), nb_name(MOD, "x")
            ctx, pg, errs = open_nb_ctx(b, nm)                  # Modeling first, then Complex in the same window
            # the second notebook from the file browser, in the same window (a reader's way)
            it = pg.wait_for_selector(".jp-DirListing-item[title*='%s']" % nc, timeout=15000)
            it.dblclick(); pg.wait_for_timeout(5000)
            if pg.query_selector(".jp-Dialog"): pg.keyboard.press("Enter"); pg.wait_for_timeout(1500)
            title = restart_run_all(pg)
            for _ in range(240):                       # until Complex has a run of its own
                pg.wait_for_timeout(500)
                if pg.evaluate(FEED): break
            wait_idle(pg, 120); pg.wait_for_timeout(3000)
            f0 = pg.evaluate(FEED)
            lsm0 = pg.evaluate("() => localStorage.getItem('digichemjn.mode.intro-modeling')")
            fm = os.path.join(KHOME, ".digichemjn", "intro-modeling.mode")
            fm0 = open(fm).read() if os.path.exists(fm) else None
            btn = pg.query_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .nbend-go .nbend-mode[data-mode='calc']")
            if btn:
                btn.scroll_into_view_if_needed(); tap(btn)
                seen = runs_after(pg, 60, f0 and f0["run"])
            else:
                seen = []
            lsm1 = pg.evaluate("() => localStorage.getItem('digichemjn.mode.intro-modeling')")
            fm1 = open(fm).read() if os.path.exists(fm) else None
            fc = os.path.join(KHOME, ".digichemjn", "complex-numbers.mode")
            fc1 = open(fc).read() if os.path.exists(fc) else None
            check("R6x", "JS+Py", bool(btn) and [s[1] for s in seen] == ["calc"] and fc1 == "calc",
                  "Complex in front (feed %s): calc card → runs %s, complex file %r" % (f0 and f0["mode"], [s[1] for s in seen], fc1),
                  "one run, calc; file 'calc'")
            check("R6x", "JS+Py", lsm1 == lsm0 and fm1 == fm0,
                  "Modeling store %r → %r · file %r → %r" % (lsm0, lsm1, fm0, fm1), "unchanged")
            # Modeling's own run is untouched: bring it to the front and read its feed
            pg.click(".lm-DockPanel .lm-TabBar-tab:has-text('%s')" % nm[:20]); pg.wait_for_timeout(2500)
            f2 = pg.evaluate(FEED)
            check("R6x", "JS+Py", bool(f2) and f2["mode"] == "both", "Modeling feed after it %s" % f2, "both")
            ctx.close()
        b.close()
    kill_sessions(BASE)
    print("\n".join(rows))
    print("\n" + ("REGRESS-PY OK" if not fails else "RED (%d):\n- " % len(fails) + "\n- ".join(fails)))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
