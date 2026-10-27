"""E24.3 — the JS workshop's regress test for the cover as an OUTPUT (2026-10-06,
E24 Stufe 2). Module of tests/regress/run.py (TESTS = [(name, fn)], fn(pg, ctx) ->
(ok, detail)); also stand-alone:

    python3 tests/regress/js_e24_3.py <notebook.ipynb>

py-E24.3 made the markdown cell one start line and the cover the LAST output of
the mega-cell (`.nbtitle.nbcover-out`); js-E24.3 decides when it shows. Measured
like a stranger: a fresh copy of the notebook under test (outputs cleared) is
opened in a browser context of its own (since 07.10.: not beside it in the
row's page, see cover_output) and run from the palette (Run All):

  J24.3a  before the run: no cover, no Play; after it the cover is up OVER the
          notebook (its box = `.jp-Notebook` ±1 px), the timeline panel is not
          shown, Play, the content cards, the language and the login are on it
          and take the pointer (elementFromPoint at their middle hits them, the
          cover scrolled to them).
  J24.3b  one click on another content card: chosen at once (aria-checked, and
          stored under digichemjn.mode.<id>, ≤ 400 ms), no run of its own (the
          cover stays, 2.5 s); Play then rebuilds that
          content (a new run, `.nbfeed[data-nbmode]` = the card) and comes up as
          the DOCUMENT (no cover, the timeline panel there).
  J24.3c  the row's page saw nothing of it (no other panel, no storage event, no
          loading view) and its notebook has the same run and content after.
The copy is shut with its context; the kernel's folder is put back as it was
(the copy shares the notebook's id and the server).
A test that cannot reach its precondition returns False ("BAD …"), never True.
Gegenprobe v1.66 + py-E24.0–4 (cover output, no JS): J24.3a red (cover hidden,
no Play in the page) — see the chronicle 06.10. Werkstatt JS."""
import os, sys, json, time, itertools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FRONT = ".jp-NotebookPanel:not(.lm-mod-hidden)"
_N = itertools.count()

def _palette(pg, label):
    pg.keyboard.press("Escape"); pg.keyboard.press("Control+Shift+C")
    pg.wait_for_function("() => { var i = document.activeElement; return !!(i && i.classList && i.classList.contains('lm-CommandPalette-input')); }", timeout=10000)
    pg.fill(".lm-CommandPalette-input", label)
    pg.wait_for_function("(l) => { var a = document.querySelector('.lm-CommandPalette-item.lm-mod-active .lm-CommandPalette-itemLabel'); return !!(a && a.textContent.trim().indexOf(l) === 0); }", arg=label, timeout=10000)
    pg.keyboard.press("Enter")

def _front_name(pg):
    return pg.evaluate("() => { var t = document.querySelector('.lm-DockPanel .lm-TabBar-tab.lm-mod-current .lm-TabBar-tabLabel'); return t ? t.textContent.trim() : null; }")

STATE = r"""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var nb = P && P.querySelector('.jp-Notebook'), c = P && P.querySelector('.nbcover-out');
  var vis = function(e){ if (!e) return false; var r = e.getBoundingClientRect(), s = getComputedStyle(e); return r.width > 2 && r.height > 2 && s.display !== 'none' && s.visibility !== 'hidden'; };
  var host = document.getElementById('nbpanel-root'), f = P && P.querySelector('.nbfeed[data-nbid]');
  var ind = P && P.querySelector('.jp-Notebook-ExecutionIndicator');
  var a = nb ? nb.getBoundingClientRect() : null, r = c ? c.getBoundingClientRect() : null;
  return {cover: vis(c), box: r ? [r.left, r.top, r.width, r.height].map(Math.round) : null,
          area: a ? [a.left, a.top, a.width, a.height].map(Math.round) : null,
          play: vis(c && c.querySelector('.nbcover-play')),
          rail: !!(host && getComputedStyle(host).display !== 'none' && host.querySelector('.nbmap')),
          run: f ? f.getAttribute('data-nbid') : null, built: f ? (f.getAttribute('data-nbmode') || 'both') : null,
          busy: ind ? ind.getAttribute('data-status') : null, panels: document.querySelectorAll('.jp-NotebookPanel').length,
          load: !!document.querySelector('#nbload:not(.nbload-out)')}; }"""

# what takes the pointer at the middle of each control of the cover (scrolled to it)
HITS = r"""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), c = P && P.querySelector('.nbcover-out');
  if (!c) return null;
  var sel = {play: '.nbcover-play', card: '.nbmode .nbmode-opt', lang: '.nblang .nblang-opt', login: '.nbacct input, .nbacct button'}, out = {};
  // hw-E25.int (08.10.): since E25.k the login sits in the fold "Sign in"
  // (details.nbacct-fold, closed) — opened as the reader opens it, closed again
  // after (behauptete bisher: the login stands open on the cover)
  var fold = c.querySelector('details.nbacct-fold'), wasOpen = fold ? fold.open : null;
  Object.keys(sel).forEach(function(k){ var e = c.querySelector(sel[k]);
    if (!e) { out[k] = 'missing'; return; }
    if (k === 'login' && fold && fold.contains(e) && !fold.open) fold.open = true;
    e.scrollIntoView({block: 'center'});
    var r = e.getBoundingClientRect(), h = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    out[k] = h && (h === e || e.contains(h)) ? 'ok' : ('covered by ' + (h ? (h.className || h.tagName).toString().slice(0, 40) : 'nothing')); });
  if (fold && wasOpen === false) fold.open = false;
  c.scrollTop = 0; return out; }"""

# E24 Stufe 2 Rest: the page clocks the card (J24.3b)
WATCH = r"""(a) => { var want = a[0], nid = a[1], w = window.__j24w = {t0: null, t1: null, on: false, st: null};
  var ok = function(){ var o = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .nbcover-out .nbmode-opt[data-mode="' + want + '"]');
    w.on = !!(o && o.getAttribute('aria-checked') === 'true'); w.st = localStorage.getItem('digichemjn.mode.' + nid);
    return w.on && w.st === want; };
  var h = function(ev){ var o = ev.target && ev.target.closest && ev.target.closest('.nbcover-out .nbmode-opt');
    if (!o || o.getAttribute('data-mode') !== want || w.t0 !== null) return;
    w.t0 = performance.now(); document.removeEventListener('click', h, true);
    // our handler runs after this capture listener, in the same task: the
    // first look one tick later, then every frame for 2 s
    setTimeout(function(){ (function f(){ if (ok()) { w.t1 = performance.now(); return; }
                                           if (performance.now() - w.t0 < 2000) requestAnimationFrame(f); })(); }, 0); };
  document.addEventListener('click', h, true); }"""

def _click(pg, sel):
    """a real click; on failure what lies there instead (BAD detail, no exception)"""
    # a pointer click at the middle (Play pulses — CSS — and is never "stable"
    # for Playwright's own click; measured: 8 s timeout with Play itself hit)
    try:
        xy = pg.evaluate("(s) => { var e = document.querySelector(s); if (!e) return null; e.scrollIntoView({block: 'center'}); var r = e.getBoundingClientRect(); return r.width > 2 ? [r.left + r.width / 2, r.top + r.height / 2] : null; }", sel)
        if not xy: raise RuntimeError("not drawn")
        pg.wait_for_timeout(200); pg.mouse.click(*xy); return None
    except Exception as e:
        return "click %s failed (%s): %s" % (sel[-40:], str(e).splitlines()[0][:60], pg.evaluate("""(s) => { var e = document.querySelector(s); if (!e) return 'not in the page';
          var r = e.getBoundingClientRect(), h = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2), c = e.closest('.nbcover-out');
          return 'box ' + [r.left, r.top, r.width, r.height].map(Math.round) + ' · hit ' + (h ? (h.className || h.tagName).toString().slice(0, 50) : '-')
            + ' · cover ' + (c ? c.getAttribute('data-nbcov') + ' ' + getComputedStyle(c).display : '-'); }""", sel))

def _wait(pg, cond, ms):
    t = 0
    while t < ms:
        s = pg.evaluate(STATE)
        if cond(s): return s
        pg.wait_for_timeout(500); t += 500
    return pg.evaluate(STATE)

def _ran(s, run0=None):
    return s["run"] and s["run"] != run0 and s["busy"] == "idle" and not s["load"]

# The copy has the notebook's id: its run reads and writes what the notebook
# under test keeps — the kernel's folder (progress, mode, language, seed) and
# the page's storage (mode, language, the once-per-tab retry keys). All of it
# is put back as it was, so the tests after this one see their notebook's state
# (measured: without it PY-E23.0 found the progress reset and the mode changed).
def _dirs():
    kh = os.environ.get("DIGICHEM_KERNEL_HOME") or os.path.expanduser("~")
    root = os.environ.get("DIGICHEM_LAB_ROOT", "")
    return [os.path.join(d, ".digichemjn") for d in (kh, root) if d]

def _keep(dirs):
    out = {}
    for d in dirs:
        out[d] = None
        if os.path.isdir(d):
            out[d] = {}
            for b, _, fs in os.walk(d):
                for f in fs:
                    p = os.path.join(b, f)
                    try: out[d][os.path.relpath(p, d)] = open(p, "rb").read()
                    except Exception: pass
    return out

def _put_back(kept):
    import shutil
    for d, files in kept.items():
        try:
            if files is None:
                shutil.rmtree(d, ignore_errors=True); continue
            for b, _, fs in os.walk(d):
                for f in fs:
                    p = os.path.join(b, f)
                    if os.path.relpath(p, d) not in files: os.remove(p)
            for r, v in files.items():
                p = os.path.join(d, r); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "wb").write(v)
        except Exception:
            pass

def _close(pg, name):
    try:
        if name and _front_name(pg) == name:
            _palette(pg, "Close and Shut Down Notebook")
            pg.wait_for_timeout(800)
            if pg.query_selector(".jp-Dialog"):
                b = pg.query_selector(".jp-Dialog .jp-mod-accept") or pg.query_selector(".jp-Dialog button.jp-mod-warn")
                if b: b.click()
                else: pg.keyboard.press("Enter")
            pg.wait_for_timeout(2000)
    except Exception:
        pass

ST_KEEP = """() => { var o = {}; [['l', localStorage], ['s', sessionStorage]].forEach(function(p){ o[p[0]] = {};
  for (var i = 0; i < p[1].length; i++) { var k = p[1].key(i); if (k && k.indexOf('digichemjn.') === 0) o[p[0]][k] = p[1].getItem(k); } }); return o; }"""
ST_PUT = """(o) => { [['l', localStorage], ['s', sessionStorage]].forEach(function(p){ var st = p[1], want = o[p[0]], ks = [];
  for (var i = 0; i < st.length; i++) { var k = st.key(i); if (k && k.indexOf('digichemjn.') === 0) ks.push(k); }
  ks.forEach(function(k){ if (!(k in want)) st.removeItem(k); });
  Object.keys(want).forEach(function(k){ if (st.getItem(k) !== want[k]) st.setItem(k, want[k]); }); }); }"""

# 2026-10-07 (E24 Stufe 2 Rest 2, JS) — THE STRANGER'S COPY RUNS IN THE
# STRANGER'S OWN BROWSER. Behauptete bisher: the fresh copy is opened BESIDE
# the notebook under test, in the row's page (same window, same storage, same
# panel host, the copy with the same notebook id). Tor 07.10. (v1.67-Probe,
# 21 patches): J24.3 red in two pair rows (three notebooks in one page: "card
# calc 771 ms" — clocked in the page, the page itself busy; "BAD the copy did
# not run"), a page error "Cannot send" in a third (not reproduced here). And
# the copy touched the row's page every later test reads: measured with the
# old J24.3 (pair, minimal light) a third panel in the row's page and its
# loading view there for ~13 s (67 samples of 200 ms). (PY-R6i "no inbox" came
# from J23.pe, not from here — Python, Rest 2.) A stranger has no other
# notebook open and a fresh browser: the copy now opens in a NEW browser context (own storage,
# own page, its own JupyterLab workspace, the row's style and light/dark set
# as the row sets them), is run there and shut there. The row's page is only
# watched: J24.3c says it saw nothing — no other panel, no storage event, no
# loading view, the same run and content after. The kernel's folder is still
# shared (one server): kept and put back as before.
ROW_WATCH = r"""() => { if (window.__j24row) return; var w = window.__j24row = {panels: 0, store: [], load: 0};
  w.h = function(e){ if (e.key && e.key.indexOf('digichemjn.') === 0 && w.store.length < 20) w.store.push(e.key); };
  window.addEventListener('storage', w.h);
  w.iv = setInterval(function(){ w.panels = Math.max(w.panels, document.querySelectorAll('.jp-NotebookPanel').length);
    if (document.querySelector('#nbload:not(.nbload-out)')) w.load++; }, 200); }"""
ROW_READ = r"""() => { var w = window.__j24row; if (!w) return null; window.__j24row = null;
  clearInterval(w.iv); window.removeEventListener('storage', w.h); return {panels: w.panels, store: w.store, load: w.load}; }"""

def _lab_base(pg):
    u = pg.url
    return os.environ.get("DIGICHEM_LAB_URL") or u[:u.index("/lab")]

def _open_iso(pg, ctx):
    """the copy in a browser context of its own: (context, page, name, page errors) or None"""
    src = _front_name(pg); root = os.environ.get("DIGICHEM_LAB_ROOT", "")
    path = os.path.join(root, src or "")
    if not src or not os.path.exists(path): return None
    nb = json.load(open(path, encoding="utf-8"))
    for c in nb.get("cells", []):
        if c.get("cell_type") == "code": c["outputs"] = []; c["execution_count"] = None
    name = "j24cov_%03d_%d_%s" % (next(_N), os.getpid() % 1000, src)
    json.dump(nb, open(os.path.join(root, name), "w", encoding="utf-8"))
    vp = pg.viewport_size or {"width": 1400, "height": 900}
    c2 = pg.context.browser.new_context(viewport=vp)
    items = {"digichemjn.skin.v1": ctx.get("skin") or "minimal", "digichemjn.theme.v1": ctx.get("theme") or "light"}
    if ctx.get("id"):                                      # E25.o: the notebook's own keys
        items["digichemjn.skin.v1." + ctx["id"]] = items["digichemjn.skin.v1"]; items["digichemjn.theme.v1." + ctx["id"]] = items["digichemjn.theme.v1"]
    c2.add_init_script("(function(i){ try { if (sessionStorage.getItem('__j24init')) return; Object.keys(i).forEach(function(k){ localStorage.setItem(k, i[k]); }); sessionStorage.setItem('__j24init', '1'); } catch (e) {} })(%s);" % json.dumps(items))
    p2 = c2.new_page(); errs = []
    p2.on("pageerror", lambda e: errs.append("pageerror: %s" % str(e)[:200]))
    p2.goto("%s/lab/workspaces/j24iso%d/tree/%s?reset" % (_lab_base(pg), os.getpid(), name))
    p2.wait_for_selector(FRONT + " .jp-Cell", state="attached", timeout=120000)
    # the kernel first (a stranger's Run All waits for it too): idle, dialogs answered
    for _ in range(120):
        if p2.query_selector(".jp-Dialog"): p2.keyboard.press("Enter"); p2.wait_for_timeout(800)
        if p2.evaluate("() => { var e = document.querySelector('%s .jp-Notebook-ExecutionIndicator'); return !!(e && e.getAttribute('data-status') === 'idle'); }" % FRONT): break
        p2.wait_for_timeout(500)
    p2.wait_for_timeout(800)
    return c2, p2, name, errs

def _run_iso(p2):
    """Run All in the copy; once more if no run started within 25 s (counted)"""
    tries = 0
    for tries in range(1, 3):
        _palette(p2, "Run All Cells")
        s = _wait(p2, lambda s: bool(s["run"]) or s["busy"] == "busy", 25000)
        if s["run"] or s["busy"] == "busy": break
    return tries

def cover_output(pg, ctx):
    nid = ctx.get("id") or ""
    kept = _keep(_dirs())
    o0 = pg.evaluate(STATE)             # the notebook under test (c)
    pg.evaluate(ROW_WATCH)
    iso = None
    try:
        iso = _open_iso(pg, ctx)
    except Exception as e:
        pg.evaluate(ROW_READ)
        return False, "BAD could not open a fresh copy in its own browser (%s)" % str(e)[:120]
    if not iso:
        pg.evaluate(ROW_READ)
        return False, "BAD could not open a fresh copy"
    c2, cp, name, errs2 = iso
    bad, det = [], []
    try:
        s0 = cp.evaluate(STATE)
        if s0["cover"] or s0["play"]: bad.append("a: before the run cover %s, Play %s" % (s0["cover"], s0["play"]))
        tries = _run_iso(cp)
        s = _wait(cp, lambda s: _ran(s) and s["cover"], 150000)
        cp.wait_for_timeout(1500); s = cp.evaluate(STATE)
        if not s["run"]: return False, "BAD the copy did not run (Run All %dx; %s)" % (tries, s)
        if tries > 1: det.append("Run All twice (the first did not start)")
        if not s["cover"]: bad.append("a: no cover after the run")
        elif any(abs(x - y) > 1 for x, y in zip(s["box"], s["area"])): bad.append("a: cover %s ≠ notebook %s" % (s["box"], s["area"]))
        if s["rail"]: bad.append("a: the timeline panel over the cover")
        h = cp.evaluate(HITS) or {}
        bad += ["a: %s %s" % (k, v) for k, v in h.items() if v != "ok"]
        det.append("cover %s on %s, rail %s, hits %s" % (s["box"], s["area"], s["rail"], h))
        if not s["cover"]:
            return False, "; ".join(bad) + " | " + " · ".join(det)
        # b — one click on another card, then Play
        built = s["built"]; want = "calc" if built != "calc" else "plain"
        cp.evaluate("(m) => { var o = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .nbcover-out .nbmode-opt[data-mode=\"' + m + '\"]'); if (o) o.scrollIntoView({block: 'center'}); }", want)
        cp.wait_for_timeout(300)
        # E24 Stufe 2 Rest (07.10.): the time is the PAGE's — from the click
        # event on the card (capture listener, before our handler) to the first
        # moment card and storage both show the choice. Criterion: ≤ 400 ms.
        cp.evaluate(WATCH, [want, nid])
        err = _click(cp, "%s .nbcover-out .nbmode-opt[data-mode=\"%s\"]" % (FRONT, want))
        if err: return False, "BAD b: " + err + " | " + " · ".join(det)
        ch = None
        for _ in range(40):
            ch = cp.evaluate("() => window.__j24w || null")
            if ch and ch.get("t1") is not None: break
            cp.wait_for_timeout(50)
        dt = int(round(ch["t1"] - ch["t0"])) if ch and ch.get("t0") is not None and ch.get("t1") is not None else -1
        if not ch or ch.get("t0") is None: bad.append("b: BAD the click did not reach the card %s (%s)" % (want, ch))
        elif dt < 0: bad.append("b: card %s not chosen within 2 s of the click: %s" % (want, ch))
        elif dt > 400: bad.append("b: card %s chosen %d ms after the click (want ≤ 400)" % (want, dt))
        cp.wait_for_timeout(2500)          # a card is a choice, not a start: no rebuild before Play
        sb = cp.evaluate(STATE)
        if sb["load"] or sb["run"] != s["run"] or not sb["cover"]: bad.append("b: the card alone started a run (loading %s, run %s→%s, cover %s)" % (sb["load"], s["run"], sb["run"], sb["cover"]))
        run0 = s["run"]
        cp.evaluate("() => { var p = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .nbcover-out .nbcover-play'); if (p) p.scrollIntoView({block: 'center'}); }")
        cp.wait_for_timeout(300)
        err = _click(cp, "%s .nbcover-out .nbcover-play" % FRONT)
        if err: return False, "BAD b: " + err + " | " + " · ".join(det)
        s2 = _wait(cp, lambda x: _ran(x, run0) and x["rail"], 150000)
        cp.wait_for_timeout(3000); s2 = cp.evaluate(STATE)
        if s2["run"] == run0: bad.append("b: Play did not rebuild (run %s)" % run0)
        if s2["built"] != want: bad.append("b: built %s, chosen %s" % (s2["built"], want))
        if s2["cover"] or not s2["rail"]: bad.append("b: after the rebuild cover %s, timeline panel %s (want the document)" % (s2["cover"], s2["rail"]))
        det.append("card %s %d ms · Play → run %s→%s built %s, cover %s, rail %s" % (want, dt, run0, s2["run"], s2["built"], s2["cover"], s2["rail"]))
    finally:
        _close(cp, name)
        try: c2.close()
        except Exception: pass
        _put_back(kept)
        pe = [e for e in errs2 if e.startswith("pageerror")]
        if pe: bad.append("page errors in the copy's page: %s" % [e[:90] for e in pe[:2]])
        # c — the row's page saw nothing of the copy, and its notebook is as it was
        s9 = None
        for _ in range(8):
            pg.wait_for_timeout(500)
            s9 = pg.evaluate(STATE)
            if s9["load"] or s9["run"] != o0["run"]: break
        w = pg.evaluate(ROW_READ) or {}
        if w.get("panels", 0) > o0.get("panels", 0) or w.get("store") or w.get("load"):
            bad.append("c: the row's page saw the copy (panels %s → max %s, storage events %s, loading views %s)"
                       % (o0.get("panels"), w.get("panels"), w.get("store"), w.get("load")))
        if s9["load"] or s9["run"] != o0["run"] or s9["built"] != o0["built"]:
            bad.append("c: the notebook under test changed after the copy (run %s→%s, built %s→%s, loading %s)"
                       % (o0["run"], s9["run"], o0["built"], s9["built"], s9["load"]))
        det.append("row page: panels %s, storage events %d, loading %s" % (w.get("panels"), len(w.get("store") or []), w.get("load")))
    return (not bad), ("; ".join(bad) + " | " if bad else "") + " · ".join(det)

# ------------------------------------------------------------------ J24.3z
# 2026-10-07 (E24 Stufe 2 Rest, JS) — THE COVER AND THE LENS. The lens zooms
# every child of a cell (CSS zoom), the cover in the mega-cell's output with it:
# Tor 07.10. J24.3a once "cover 1391 × 1013 ≠ notebook 1070 × 779" (= 1.3 ×, the
# lens 130 % of the old-storage fixture), and the cover tests C23.2/C23.8 red
# in one order and green in another. On the notebook under test (no copy, no
# run): the cover brought up (__nbCoverShow) at lens 100 %, 130 %, 60 % —
#   box = `.jp-Notebook` ±1 px at every lens, and the cover's content the same
#   size (title heading and the first lane name: rendered width ±1 px of 100 %).
# Storage and the document are put back.
LENS = r"""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var c = P && P.querySelector('.nbcover-out[data-nbcov]'), nb = P && P.querySelector('.jp-Notebook');
  if (!c || !nb) return null; c.scrollTop = 0;
  var cell = P.querySelector('.jp-Cell > *'), r = c.getBoundingClientRect(), a = nb.getBoundingClientRect();
  var h = c.querySelector('.nbtitle-h'), n = c.querySelector('.nbcover-tl .nbtl-nm');
  var w = function(e){ return e ? Math.round(e.getBoundingClientRect().width * 10) / 10 : null; };
  return {lens: cell ? (cell.style.zoom || '1') : null, box: [r.left, r.top, r.width, r.height].map(Math.round),
          area: [a.left, a.top, a.width, a.height].map(Math.round), h: w(h), nm: w(n)}; }"""

def cover_lens(pg, ctx):
    st0 = pg.evaluate(ST_KEEP)
    key = pg.evaluate("() => window.__nbZKey ? window.__nbZKey() : null")
    if not key: return False, "BAD no lens key (__nbZKey)"
    out, bad = {}, []
    try:
        for z in ("100", "130", "60"):
            pg.evaluate("(a) => localStorage.setItem(a[0], a[1])", [key, z])
            want = "1" if z == "100" else str(int(z) / 100)
            for _ in range(24):            # the sync pass puts the lens on (every 1.5 s)
                pg.wait_for_timeout(250)
                if pg.evaluate("() => { var e = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell > *'); return e ? (e.style.zoom || '1') : null; }") == want: break
            if not pg.evaluate("() => !!(window.__nbCoverShow && window.__nbCoverShow(true))"):
                return False, "BAD the cover did not come up at lens %s %%" % z
            m = None
            for _ in range(12):
                pg.wait_for_timeout(250)
                m = pg.evaluate(LENS)
                if m and all(abs(x - y) <= 1 for x, y in zip(m["box"], m["area"])): break
            pg.wait_for_timeout(600); m = pg.evaluate(LENS)
            pg.evaluate("() => window.__nbCoverShow && window.__nbCoverShow(false)"); pg.wait_for_timeout(800)
            if not m: return False, "BAD no cover to measure at lens %s %%" % z
            if m["lens"] != want: bad.append("lens %s %%: the lens did not come on (%s)" % (z, m["lens"]))
            out[z] = m
            if any(abs(x - y) > 1 for x, y in zip(m["box"], m["area"])): bad.append("lens %s %%: cover %s ≠ notebook %s" % (z, m["box"], m["area"]))
        for z in ("130", "60"):
            for f in ("h", "nm"):
                if out["100"][f] is None or out[z][f] is None: bad.append("BAD no %s on the cover" % f)
                elif abs(out[z][f] - out["100"][f]) > 1: bad.append("lens %s %%: %s %.1f px, at 100 %% %.1f px" % (z, f, out[z][f], out["100"][f]))
    finally:
        pg.evaluate(ST_PUT, st0)
        try: pg.evaluate("() => window.__nbCoverShow && window.__nbCoverShow(false)")
        except Exception: pass
        pg.wait_for_timeout(2000)
    return (not bad), ("; ".join(bad) + " | " if bad else "") + " · ".join(
        "%s %%: cover %s, heading %s px, name %s px" % (z, out[z]["box"], out[z]["h"], out[z]["nm"]) for z in out)

TESTS = [("J24.3 cover output first, cards/Play work, Play → document", cover_output),
         ("J24.3z cover the same at every lens (box = notebook, content 100 %)", cover_lens)]

def main():
    import shutil
    from lab_keys import ensure_lab, open_nb, CHROME
    from playwright.sync_api import sync_playwright
    nb = sys.argv[1]
    base, root = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:1"))
    name = "j24main_%d_%s" % (os.getpid() % 1000, os.path.basename(nb))
    shutil.copy(nb, os.path.join(root, name))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        ctx, pg, errs = open_nb(b, base, name)
        txt = open(nb, encoding="utf-8").read()
        nid = next((i for i in ("complex-numbers", "intro-modeling") if '"%s' % i in txt or '\\"%s' % i in txt), "unnamed")
        only = sys.argv[2].split(",") if len(sys.argv) > 2 else None
        ok = True
        for tname, fn in TESTS:
            key = tname.split()[0]
            if only and key not in only: continue
            o, d = fn(pg, {"id": nid, "errs": errs})
            ok = ok and o
            print("%s %s · %s" % ("ok " if o else "RED", key, d)); sys.stdout.flush()
        if errs: print("page errors:", errs[:3])
        b.close()
    sys.exit(0 if ok and not [e for e in errs if e.startswith("pageerror")] else 1)

if __name__ == "__main__":
    main()
