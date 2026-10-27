"""E26 Teil 2 · JS — THE READING WINDOW (Werkstatt JS, 2026-10-11).
    python3 tests/regress/env_reader.py <notebook.ipynb> [--shots DIR] [--json out.json]

Same viewer as env_iframe.py (real kernel, every output in an iframe of its own,
no widget manager — PyCharm / JCEF), served over http (localStorage like a real
viewer), the host page made taller than the viewport so that it CAN scroll —
the wheel test means nothing otherwise. Rows (en light; en dark; de light):
  W1 one window          one .nbrw in the reading frame, window screen − 240 px (E33; fresh
                         storage), panel with chapter marks = chapters (7; py-E26.2: the
                         exercise marks data-kind=calc|code come on top, py_e26_2.py), no
                         requestFullscreen in any output
  W2 wheel moves window  wheel over the window and over the panel: the window
                         scrolls (≥ 80 % of the delta), the PAGE does not move
  W3 wheel at the end    window at its end: the next wheel moves the page 0 px (E33 B1c; was: moves it)
  W4 marks jump          click on mark k → chapter k's heading on the reading
                         height ±2 px (or the window at its end); a locked
                         chapter's mark leaves the window where it is (E30,
                         Lab E29 D3); the page stays
  W5 contents link       a link of the contents list → same, the page stays
  W6 height kept         ↕+ ×2 = standard + 200 px, A+ = 16.5 px; reload → both kept;
                         ↕− ×2, A− → standard / 15
  W10 theme, style kept  fresh: data-nbrw-skin=digi (E34, the standard); ◐ → data-nbrw-theme=dark,
                         ✿ ✿ → cyber (digi → minimal → cyber), kept after reload; round trip → none / digi
                         (behauptete bisher: fresh minimal, one ✿ → cyber, round trip → minimal; E34 JS)
  W7 thumb               thumb = track × visible share ±2 px (min 24); drag to
                         the bottom → window at its end ±2 px
  W8 current chapter     after a jump the panel names that chapter
  W9 not in a notebook   nbconvert page (scripts on): 0 windows (the page
     front end           scrolls there; Lab/Lite: cold.py, lab_flow)
E26 Teil 3 (Werkstatt JS, 11.10.) — "Lesefenster wie Lab". The W rows press
▶ Play first (the window opens on the preview now). New rows on the en-light
run; where Python's markup of E26.3 is not there yet (gates, both languages,
accordions, the check as text) a STAND-IN after claude/VERTRAG-nbrw-E26.3.md
is put into the reading output (row "py-markup: stand-in|real"):
  C1 preview first       view=cover: one title card, ▶ Play, timeline with the
                         chapter names, 4 mode cards, panel hidden, document
                         hidden · Play → document + panel · ◂ Vorschau → cover
                         · Play → the document where it was (±2 px)
  C2 language            DE on the cover → the cover German at once; the
                         document view in ONE language (E30 B2: a document
                         built English keeps contents + panel English, one
                         line says why; a bilingual one goes German); kept
                         after reload; EN back
  A1 axis                |middle of the visible title card − middle of the
                         window| ≤ 1 px: cover, document with panel open and
                         closed, lens 60/100/150 %; the panel never past the
                         middle; column width reported
  G1 gating              chapter 2 locked: its content hidden, a 🔒 line, mark
                         data-st=locked with 🔒 · t1 answered wrong → open
  X1 XP                  "0 / n" → t1 right → "1 / n", bar wider
  M1 mode                plain: 0 exercises, 0 exercise marks, no XP · calc:
                         calc only · code: code only · both; kept after reload
  D1 accordions          <details data-acc> closed → kept after reload; a jump
                         to a target inside opens it
  R1 ▶ in the window     Pyodide routed to a local copy (jsDelivr is not
                         reachable here): DIGICHEM_PYODIDE_DIR, else `npm pack
                         pyodide@0.27.7` once into ~/.cache (else red): status "Loading Python",
                         wrong code → ✗ wrong, error → output data-err, nothing
                         counted, right → ✓ solved, XP +1, kept after reload
  R2 no network          the CDN refused: the honest sentence with
                         pruefe("t1", …), "Copy to clipboard" there, the
                         clipboard gets the field + the pruefe line
v1.73: red (C1: no preview). Owner: JS. exit 0 = REGRESS-ENV-READER OK."""
import sys, os, re, json, tempfile, shutil, subprocess, threading, functools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from env_iframe import run_cell, host_page

FR = """() => { var f = [].slice.call(document.querySelectorAll('iframe.out')).filter(function(x){
  try { return !!x.contentDocument.querySelector('.nbreading'); } catch (e) { return false; } })[0];
  return f ? [].indexOf.call(document.querySelectorAll('iframe.out'), f) : -1; }"""

def serve(d):
    import http.server, socketserver
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    h = functools.partial(Q, directory=d)
    s = socketserver.TCPServer(("127.0.0.1", 0), h)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s

PLAY = """() => { var w = document.querySelector('.nbrw'), p = w && w.querySelector('[data-nbrw-act=play]');
  if (w && w.getAttribute('data-nbrw-view') === 'cover' && p) p.click(); return w ? w.getAttribute('data-nbrw-view') : null; }"""

def check(pg, tag, nch, lang, fails, rows, shots):
    def bad(m): fails.append("%s %s" % (tag, m))
    fi = pg.evaluate(FR)
    if fi < 0: bad("W1 no frame with the reading version"); return
    fr = [f for f in pg.frames if f != pg.main_frame][fi]
    fe = pg.query_selector_all("iframe.out")[fi]
    S = lambda js, a=None: fr.evaluate(js, a)
    n = S("() => document.querySelectorAll('.nbrw').length")
    if n != 1: bad("W1 %d reading windows, want 1" % n); return
    v = S(PLAY)        # E26.3: the window opens on the preview; the W rows read the document
    if v != "doc": bad("W1 Play → view %r, want 'doc'" % v)
    pg.wait_for_timeout(400)
    g = S("""() => { var w = document.querySelector('.nbrw'), win = w.querySelector('.nbrw-win');
      return {h: Math.round(win.getBoundingClientRect().height), marks: w.querySelectorAll('.nbrw-mark[data-kind=chap]').length,
              sh: win.scrollHeight, ch: win.clientHeight, cur: w.querySelector('.nbrw-cur').textContent,
              hin: w.querySelector('.nbrw-btn[data-act="h+"]').title, scr: screen.availHeight}; }""")
    rows.append("%s: window %d px, marks %d, content %d / %d px, panel '%s'" % (tag, g["h"], g["marks"], g["sh"], g["ch"], g["hin"]))
    # E33 B1b (Werkstatt JS): fresh = the screen's height less the IDE's bars (behauptete bisher: 600 px)
    if g["h"] != H0(g["scr"]): bad("W1 window height %d, want %d (screen.availHeight %d − 240)" % (g["h"], H0(g["scr"]), g["scr"]))
    if g["marks"] != nch: bad("W1 %d marks, want %d" % (g["marks"], nch))
    if lang == "de" and g["hin"] != "Fenster höher": bad("W1 panel not German: %r" % g["hin"])
    if lang == "en" and g["hin"] != "Taller window": bad("W1 panel not English: %r" % g["hin"])
    box = fe.bounding_box()
    wb = S("() => { var r = document.querySelector('.nbrw-win').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }")
    pb = S("() => { var r = document.querySelector('.nbrw-panel').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }")
    # scroll the page so the window is fully on screen
    pg.evaluate("y => window.scrollTo(0, y)", int(box["y"] + pg.evaluate("window.scrollY") - 20))
    pg.wait_for_timeout(200)
    def at(b):
        bx = fe.bounding_box(); return bx["x"] + b[0] + b[2] / 2, bx["y"] + b[1] + min(b[3] / 2, 200)
    win_top = lambda: S("() => document.querySelector('.nbrw-win').scrollTop")
    # W2
    for where, b in (("window", wb), ("panel", pb)):
        S("() => { document.querySelector('.nbrw-win').scrollTop = 0; }"); pg.wait_for_timeout(100)
        y0 = pg.evaluate("window.scrollY"); x, y = at(b); pg.mouse.move(x, y)
        for _ in range(3): pg.mouse.wheel(0, 200); pg.wait_for_timeout(60)
        pg.wait_for_timeout(300)
        t, y1 = win_top(), pg.evaluate("window.scrollY")
        rows.append("%s W2 wheel over the %s: window %d px, page %+d px" % (tag, where, t, y1 - y0))
        if t < 480: bad("W2 wheel over the %s moved the window %d px of 600" % (where, t))
        if abs(y1 - y0) > 1: bad("W2 wheel over the %s moved the PAGE %d px" % (where, y1 - y0))
    # W3
    S("() => { var w = document.querySelector('.nbrw-win'); w.scrollTop = w.scrollHeight; }"); pg.wait_for_timeout(150)
    y0 = pg.evaluate("window.scrollY"); x, y = at(wb); pg.mouse.move(x, y)
    pg.mouse.wheel(0, 300); pg.wait_for_timeout(400)
    y1 = pg.evaluate("window.scrollY")
    rows.append("%s W3 wheel at the end: page %+d px" % (tag, y1 - y0))
    # E33 B1c (Nutzer, Video 2): the wheel stays in the window at its ends too — out over the IDE's scroll bar
    # (behauptete bisher: at the end the next wheel moves the page ≥ 50 px)
    if abs(y1 - y0) > 1: bad("W3 window at its end, the wheel moved the page %d px, want 0" % (y1 - y0))
    pg.evaluate("y => window.scrollTo(0, y)", int(y0)); pg.wait_for_timeout(150)
    # W4 + W8 — E30 (JS): a mark puts its chapter's HEADING on the reading height (Lab), not the anchor at the
    # window top (behauptete bisher: anchor ±2 px at the top); a locked chapter's mark does not move the window
    # (E29 D3 in the window; behauptete bisher: every mark jumps)
    worst, names, locked = 0, 0, 0
    for k in range(g["marks"]):
        y0 = pg.evaluate("window.scrollY"); t0 = win_top()
        lk = S("k => document.querySelectorAll('.nbrw-mark[data-kind=chap]')[k].getAttribute('data-st') === 'locked'", k)
        S("k => document.querySelectorAll('.nbrw-mark[data-kind=chap]')[k].click()", k); pg.wait_for_timeout(250)
        r = S("""k => { var w = document.querySelector('.nbrw-win'), a = document.querySelectorAll('ol.nbread-toc a')[k];
          var t = document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1))), d = t.parentElement.nextElementSibling;
          var h = d && d.tagName === 'DETAILS' ? d.querySelector(':scope>summary .nbread-h') : t, b = h.getBoundingClientRect();
          var line = w.getBoundingClientRect().top + (window.__nbReader.line ? window.__nbReader.line() : 0);
          return {d: b.top + b.height / 2 - line, end: w.scrollTop >= w.scrollHeight - w.clientHeight - 1,
                  cur: document.querySelector('.nbrw-cur').textContent.trim(), want: (a.innerText || a.textContent).replace(/\\s+/g, ' ').trim()}; }""", k)
        if lk:
            locked += 1
            if abs(win_top() - t0) > 1: bad("W4 locked mark %d moved the window %+d px" % (k + 1, win_top() - t0))
        else:
            if not r["end"]: worst = max(worst, abs(r["d"]))
            if not r["end"] and abs(r["d"]) > 2: bad("W4 mark %d: chapter heading %.1f px from the reading height" % (k + 1, r["d"]))
            if r["cur"] == r["want"]: names += 1
            elif not r["end"]: bad("W8 mark %d: panel names %r, want %r" % (k + 1, r["cur"], r["want"]))
        if abs(pg.evaluate("window.scrollY") - y0) > 1: bad("W4 mark %d moved the page" % (k + 1))
    rows.append("%s W4 marks: worst %.1f px from the reading height (%d locked: stayed) · W8 named %d/%d" % (tag, worst, locked, names, g["marks"] - locked))
    # W5
    S("() => { document.querySelector('.nbrw-win').scrollTop = 0; }"); pg.wait_for_timeout(100)
    y0 = pg.evaluate("window.scrollY")
    # E30: the contents link goes like the mark — the chapter's heading on the reading height (behauptete bisher: anchor at the top)
    S("""() => { var a = document.querySelectorAll('ol.nbread-toc a'), k = Math.min(3, a.length - 1); a[k].click(); }""")
    pg.wait_for_timeout(300)
    r = S("""() => { var a = document.querySelectorAll('ol.nbread-toc a'), k = Math.min(3, a.length - 1), w = document.querySelector('.nbrw-win');
      var t = document.getElementById(decodeURIComponent(a[k].getAttribute('href').slice(1))), d = t.parentElement.nextElementSibling;
      var h = d && d.tagName === 'DETAILS' ? d.querySelector(':scope>summary .nbread-h') : t, b = h.getBoundingClientRect();
      if (w.scrollTop >= w.scrollHeight - w.clientHeight - 1) return 0;
      return b.top + b.height / 2 - w.getBoundingClientRect().top - (window.__nbReader.line ? window.__nbReader.line() : 0); }""")
    rows.append("%s W5 contents link: %.1f px from the reading height, page %+d" % (tag, r, pg.evaluate("window.scrollY") - y0))
    if abs(r) > 2: bad("W5 contents link: chapter heading %.1f px from the reading height" % r)
    if abs(pg.evaluate("window.scrollY") - y0) > 1: bad("W5 the contents link moved the page")
    # W7
    S("() => { document.querySelector('.nbrw-win').scrollTop = 0; }"); pg.wait_for_timeout(150)
    # E31 S1 (JS): the thumb runs in the scroll bar of the tool column on the left (.nbrw-sb) — its track is the
    # thumb's parent (behauptete bisher: the panel's track .nbrw-track)
    t = S("""() => { var w = document.querySelector('.nbrw-win'), th = document.querySelector('.nbrw-thumb'), tr = th.parentElement;
      return {want: Math.max(24, tr.clientHeight * w.clientHeight / w.scrollHeight), got: th.getBoundingClientRect().height}; }""")
    if abs(t["want"] - t["got"]) > 2: bad("W7 thumb %.1f px, want %.1f" % (t["got"], t["want"]))
    tb = S("() => { var r = document.querySelector('.nbrw-thumb').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; }")
    bx = fe.bounding_box(); x, y = bx["x"] + tb[0] + tb[2] / 2, bx["y"] + tb[1] + tb[3] / 2
    pg.mouse.move(x, y); pg.mouse.down(); pg.mouse.move(x, y + 300, steps=8); pg.mouse.move(x, y + 900, steps=8); pg.mouse.up()
    pg.wait_for_timeout(150)
    e = S("() => { var w = document.querySelector('.nbrw-win'); return w.scrollHeight - w.clientHeight - w.scrollTop; }")
    rows.append("%s W7 thumb %.1f/%.1f px, dragged to the bottom: %.1f px left" % (tag, t["got"], t["want"], e))
    if e > 2: bad("W7 thumb dragged to the bottom: %.1f px short of the end" % e)
    if shots:
        S("() => { document.querySelectorAll('.nbrw-mark[data-kind=chap]')[1].click(); }"); pg.wait_for_timeout(150)
        pg.evaluate("y => window.scrollTo(0, y)", int(fe.bounding_box()["y"] + pg.evaluate("window.scrollY") - 10))
        pg.wait_for_timeout(200)
        pg.screenshot(path=os.path.join(shots, "env_reader_%s.png" % re.sub(r"\W+", "_", tag)))

def H0(scr):        # E33 B1b: 20-reader hDef() — screen.availHeight − 240, 300 … 2400, in tens
    return max(300, min(2400, int(round((scr - 240) / 10.0)) * 10)) if scr else 600

def kept(pg, tag, fails, rows):
    def fr():
        fi = pg.evaluate(FR); return [f for f in pg.frames if f != pg.main_frame][fi]
    S = lambda js: fr().evaluate(js)
    G = "() => [Math.round(document.querySelector('.nbrw-win').getBoundingClientRect().height), parseFloat(getComputedStyle(document.querySelector('.nbreading')).fontSize)]"
    # E26.3: the base size is the stylesheet's (CSS E26.3: Lab's 13 px; before 15) — A+ is one lens step, ×1.1
    h0 = H0(fr().evaluate("() => screen.availHeight"))       # E33 B1b (was 600)
    f0 = S(G)[1]; w1 = [h0 + 200, round(f0 * 1.1, 1)]
    S("() => { var c = function(s){ document.querySelector(s).click(); }; c('.nbrw-btn[data-act=\"h+\"]'); c('.nbrw-btn[data-act=\"h+\"]'); c('.nbrw-btn[data-act=\"a+\"]'); }")
    pg.wait_for_timeout(200)
    T = "() => [document.querySelector('.nbrw').getAttribute('data-nbrw-theme'), document.querySelector('.nbrw').getAttribute('data-nbrw-skin')]"
    t0 = S(T)
    if t0[1] != "digi": fails.append("%s W10 fresh skin %s, want digi (E34)" % (tag, t0[1]))
    S("() => { var c = function(s){ document.querySelector(s).click(); }; c('.nbrw-btn[data-act=\"theme\"]'); c('.nbrw-btn[data-act=\"skin\"]'); c('.nbrw-btn[data-act=\"skin\"]'); }")
    pg.wait_for_timeout(100)
    t1 = S(T)
    a = S(G); pg.reload(); pg.wait_for_timeout(3000); S(PLAY); pg.wait_for_timeout(200); b = S(G); t2 = S(T)
    rows.append("%s W10 ◐ ✿: %s · after reload %s" % (tag, t1, t2))
    if t1 != ["dark", "cyber"] or t2 != t1: fails.append("%s W10 theme/skin %s, after reload %s, want ['dark', 'cyber'] both" % (tag, t1, t2))
    S("() => { var c = function(s){ document.querySelector(s).click(); }; c('.nbrw-btn[data-act=\"theme\"]'); c('.nbrw-btn[data-act=\"theme\"]'); c('.nbrw-btn[data-act=\"skin\"]'); c('.nbrw-btn[data-act=\"skin\"]'); }")
    t3 = S(T)
    if t3 != [None, "digi"]: fails.append("%s W10 theme/skin round trip %s, want [None, 'digi']" % (tag, t3))
    S("() => { var c = function(s){ document.querySelector(s).click(); }; c('.nbrw-btn[data-act=\"h-\"]'); c('.nbrw-btn[data-act=\"h-\"]'); c('.nbrw-btn[data-act=\"a-\"]'); }")
    pg.wait_for_timeout(200); c = S(G)
    rows.append("%s W6 ↕+×2 A+: %s · after reload %s · back %s" % (tag, a, b, c))
    r1 = lambda v: [v[0], round(v[1], 1)]
    if r1(a) != w1: fails.append("%s W6 after ↕+ ×2, A+: %s, want %s" % (tag, a, w1))
    if r1(b) != w1: fails.append("%s W6 not kept after reload: %s, want %s" % (tag, b, w1))
    if r1(c) != [h0, round(f0, 1)]: fails.append("%s W6 back: %s, want [%d, %s]" % (tag, c, h0, f0))

# ---- E26 Teil 3 (Werkstatt JS) ---------------------------------------------
CHECK_T1 = """def _nbrw_check(ns):
    f = ns.get("roots_of")
    if not callable(f):
        return False, "roots_of?"
    try:
        r = sorted((complex(x) for x in f(4)), key=lambda z: z.imag)
    except Exception as e:
        return False, repr(e)
    ok = len(r) == 2 and abs(r[0] + 2j) < 1e-9 and abs(r[1] - 2j) < 1e-9
    return ok, ""
"""
RIGHT = "import cmath\ndef roots_of(q):\n    r = cmath.sqrt(q)\n    return (1j*r, -1j*r)\n"
WRONG = "def roots_of(q):\n    return (1j*q, -1j*q)\n"
BROKEN = "def roots_of(q)\n    return 1\n"
FNAME = "roots_of"
# E28 (2026-10-12): coding t1 of the notebook under test — behauptete bisher: only
# Complex's roots_of (the template's t1 is y_von)
CODE_T1 = {"vorlage": ("def y_von(a, x):\n    return a * x\n", "def y_von(a, x):\n    return a + x\n",
                       "def y_von(a, x)\n    return 1\n", "y_von")}
PYV = "0.27.7"

def standin(h, de_titles):
    """Python's E26.3 markup after the contract, where it is not there yet."""
    import base64
    used = []
    if "<script" in h:      # only the markup counts: the reader script itself names these attributes
        i = h.find("<script"); m, tail = standin(h[:i], de_titles); return m + h[i:], tail
    ids = re.findall(r"<li><a href='#(nbr-ch\d+__\w+)'>", h)
    def sect(k):      # the top-level siblings after chapter k's heading, up to chapter k+1's anchor
        a = h.find('id="%s"' % ids[k]); a = h.find("</h3>", a) + 5
        b = h.rfind("<div class='nbread-b'>", 0, h.find('id="%s"' % ids[k + 1]))
        return a, b
    if "data-nbrw-gate" not in h and len(ids) > 3:
        a, b = sect(1); h = h[:a] + "<div data-nbrw-gate='calc:t1'>" + h[a:b] + "</div>" + h[b:]; used.append("gate")
    if "data-acc=" not in h and len(ids) > 3:
        a, b = sect(2); h = h[:a] + "<details class='nbrw-acc' data-acc='ch3' open><summary>Details</summary>" + h[a:b] + "</details>" + h[b:]
        used.append("details")
    if "data-nbrw-l=" not in h and de_titles:
        toc = re.findall(r"(<li><a href='#nbr-ch\d+__\w+'>)(.*?)(</a></li>)", h)
        for (o, t, c), dt in zip(toc, de_titles):
            h = h.replace(o + t + c, o + "<span data-nbrw-l='en'>%s</span><span data-nbrw-l='de'>%s</span>" % (t, dt) + c, 1)
        h = h.replace("</style>", ".nbrw[data-nbrw-lang=de] [data-nbrw-l=en],.nbrw[data-nbrw-lang=en] [data-nbrw-l=de],"
                      ".nbreading:not([data-nbrw]) [data-nbrw-l=de]{display:none!important}</style>", 1)
        used.append("lang")
    if "data-check=" not in h:
        h = h.replace("data-task='t1' data-st='open' data-guard=''", "data-task='t1' data-st='open' data-guard='' data-check='%s'"
                      % base64.b64encode(CHECK_T1.encode()).decode(), 1)
        used.append("check")
    return h, used

def py_dir():
    """A local Pyodide (the CDN's files): DIGICHEM_PYODIDE_DIR, else `npm pack pyodide@<PYV>` once into ~/.cache."""
    d = os.environ.get("DIGICHEM_PYODIDE_DIR", "")
    if d: return d
    c = os.path.join(os.path.expanduser("~"), ".cache", "digichemjn", "pyodide-" + PYV)
    if not os.path.isfile(os.path.join(c, "package", "pyodide.js")):
        try:
            os.makedirs(c, exist_ok=True)
            subprocess.run(["npm", "pack", "pyodide@" + PYV], cwd=c, check=True, capture_output=True, timeout=300)
            subprocess.run(["tar", "xzf", "pyodide-%s.tgz" % PYV], cwd=c, check=True, capture_output=True, timeout=120)
        except Exception:
            return ""
    return os.path.join(c, "package")

def py_route(ctx, mode):
    """jsDelivr is not reachable here: Pyodide from a local copy, or refused.
    E38a (Hauptwerkstatt, 26.10.): BEHAUPTETE BISHER, Pyodide komme immer von jsDelivr. Seit P2+J2 nimmt lesen.html
    manifest.pyodide = "/pyodide/<PYV>/" (eigener Server) — dieselbe lokale Kopie auch unter dieser Adresse."""
    pre = "https://cdn.jsdelivr.net/pyodide/v%s/full/" % PYV
    own = re.compile(r"^https?://[^/]+/pyodide/%s/" % re.escape(PYV))
    d = py_dir() if mode != "off" else ""
    def h(route):
        if mode == "off" or not d: return route.abort()
        u = route.request.url
        m = own.match(u)
        f = os.path.join(d, (u[m.end():] if m else u[len(pre):]).split("?")[0])
        if not os.path.isfile(f): return route.fulfill(status=404, body="")
        ct = {".js": "text/javascript", ".mjs": "text/javascript", ".wasm": "application/wasm", ".json": "application/json",
              ".zip": "application/zip"}.get(os.path.splitext(f)[1], "application/octet-stream")
        route.fulfill(status=200, body=open(f, "rb").read(), headers={"content-type": ct, "access-control-allow-origin": "*"})
    ctx.route(pre + "**", h)
    ctx.route(re.compile(own.pattern + ".*"), h)
    return bool(d and os.path.isfile(os.path.join(d, "pyodide.js")))

def frame(pg):
    fi = pg.evaluate(FR); return [f for f in pg.frames if f != pg.main_frame][fi], pg.query_selector_all("iframe.out")[fi]

AX = """() => { var w = document.querySelector('.nbrw'), r = w.getBoundingClientRect(), v = w.getAttribute('data-nbrw-view');
  var box = v === 'cover' ? w.querySelector('.nbrw-cover') : w.querySelector('.nbrw-doc');
  var c = [].filter.call(box.querySelectorAll('[class*="nbtitle-card"]'), function (e) { return e.getClientRects().length; })[0];
  var cr = c && c.getBoundingClientRect(), col = w.querySelector('.nbreading').getBoundingClientRect(), p = w.querySelector('.nbrw-panel').getBoundingClientRect();
  return {mid: r.left + r.width / 2, card: cr ? cr.left + cr.width / 2 : null, col: col.width, pl: p.width ? p.left : null, pw: p.width, ww: r.width}; }"""

def check3(b, base, name, tag, fails, rows, shots, used, de_titles):
    def bad(m): fails.append("%s %s" % (tag, m))
    ctx = b.new_context(viewport={"width": 1400, "height": 900})
    try: ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=base.rstrip("/"))
    except Exception: pass
    have = py_route(ctx, "on")
    pg = ctx.new_page(); pg.goto(base + name); pg.wait_for_timeout(3000)
    fr, fe = frame(pg); S = lambda js, a=None: fr.evaluate(js, a)
    pg.evaluate("y => window.scrollTo(0, y)", int(fe.bounding_box()["y"] + pg.evaluate("window.scrollY") - 10))
    rows.append("%s py-markup: %s" % (tag, ("stand-in " + "+".join(used)) if used else "real"))
    # C1
    c = S("""() => { var w = document.querySelector('.nbrw'), cv = w.querySelector('.nbrw-cover'), d = w.querySelector('.nbrw-doc');
      var vis = function (e) { return !!(e && e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden'); };
      return {view: w.getAttribute('data-nbrw-view'), cover: vis(cv), doc: vis(d), panel: vis(w.querySelector('.nbrw-panel')),
        cards: [].filter.call(w.querySelectorAll('[class*="nbtitle-card"]'), vis).length, play: vis(cv && cv.querySelector('[data-nbrw-act=play]')),
        modes: cv ? [].filter.call(cv.querySelectorAll('.nbrw-mode-opt[data-mode]'), vis).length : 0,
        tl: cv ? [].filter.call(cv.querySelectorAll('.nbrw-cv-dot[data-kind=chap]'), vis).map(function (e) { return e.innerText.trim(); }) : []}; }""")
    rows.append("%s C1 start: view %s, cover %s, document %s, panel %s, cards %d, Play %s, modes %d, timeline %d" % (
        tag, c["view"], c["cover"], c["doc"], c["panel"], c["cards"], c["play"], c["modes"], len(c["tl"])))
    if c["view"] != "cover" or not c["cover"] or c["doc"] or c["panel"]: bad("C1 not on the preview: %s" % {k: c[k] for k in ("view", "cover", "doc", "panel")}); ctx.close(); return
    if c["cards"] != 1 or not c["play"] or c["modes"] != 4 or len(c["tl"]) < 3: bad("C1 preview incomplete: %s" % c)
    if shots: pg.screenshot(path=os.path.join(shots, "E26.3-cover-en-hell.png"))
    # C2
    LG = """() => { var w = document.querySelector('.nbrw'), vis = function (e) { return !!e.getClientRects().length; };
      return {lang: w.getAttribute('data-nbrw-lang'), sw: !!w.querySelector('.nbrw-cover [data-lang="de"]'),
        cv: [].map.call(w.querySelectorAll('.nbrw-cover .nbrw-cv-t'), function (e) { return e.innerText; }).join(' | '),
        tl: [].filter.call(w.querySelectorAll('.nbrw-cv-dot[data-kind=chap]'), vis).map(function (e) { return e.innerText.trim(); }),
        toc: [].map.call(w.querySelectorAll('ol.nbread-toc a'), function (a) { return a.innerText.trim(); }),
        hin: w.querySelector('.nbrw-btn[data-act="h+"]').title, back: w.querySelector('.nbrw-btn[data-act=cover]').textContent}; }"""
    if not S("() => !!document.querySelector('.nbrw-cover [data-lang=\"de\"]')"): bad("C2 no language switch on the preview")
    else:
        fr.click('.nbrw-cover [data-lang="de"]'); pg.wait_for_timeout(250); l1 = S(LG)
        # E30 B2 (JS): the document view shows ONE language — a document built in one language keeps the contents
        # list and the panel in ITS language with one line why (behauptete bisher: contents German beside an English
        # document, the mix of the reader's PyCharm pictures); a bilingual document follows DE (js_e30 L2)
        fr.click("[data-nbrw-act=play]"); pg.wait_for_timeout(250); l1d = S(LG)
        bil = S("() => !!document.querySelector('details[data-acc] [data-nbrw-l]')")
        note = S("() => { var n = document.querySelector('.nbrw-langnote'); return n && n.getClientRects().length ? n.textContent : ''; }")
        rows.append("%s C2 document view after DE: %s document, shown %s, contents %r, panel %r, line %r" % (
            tag, "bilingual" if bil else "one-language", l1d["lang"], l1d["toc"][:1], l1d["hin"], note[:60]))
        if bil:
            if l1d["lang"] != "de" or (de_titles and l1d["toc"][:len(de_titles)] != de_titles) or note: bad("C2 bilingual document not German: %s" % l1d)
        elif l1d["lang"] != "en" or l1d["hin"] != "Taller window" or (c["tl"] and l1d["toc"][:1] != [re.sub("^\U0001F512\\s*", "", c["tl"][0])]) or "Englisch" not in note:
            bad("C2 English document with DE chosen is not one language: %s, line %r" % (l1d, note))
        l1["toc"] = de_titles[:] if not bil else l1d["toc"]       # the contents list is checked above
        pg.reload(); pg.wait_for_timeout(3000); fr, fe = frame(pg); S = lambda js, a=None: fr.evaluate(js, a); l2 = S(LG)
        fr.click('.nbrw-cover [data-lang="en"]'); pg.wait_for_timeout(250); l3 = S(LG)
        rows.append("%s C2 DE: %s · timeline %r · contents %r · panel %r %r · after reload %s · EN back %s %r" % (
            tag, l1["lang"], l1["tl"][:1], l1["toc"][:1], l1["hin"], l1["back"], l2["lang"], l3["lang"], l3["tl"][:1]))
        nolock = lambda xs: [re.sub("^\U0001F512\\s*", "", x) for x in xs]
        en_t = nolock(c["tl"]); l1["tl"], l3["tl"] = nolock(l1["tl"]), nolock(l3["tl"])
        if l1["lang"] != "de" or l1["hin"] != "Fenster höher" or "Vorschau" not in l1["back"] or "was möchten" not in l1["cv"].lower(): bad("C2 panel/cover not German: %s" % l1)
        if de_titles and (l1["tl"][:len(de_titles)] != de_titles or l1["toc"][:len(de_titles)] != de_titles): bad("C2 chapter names not German: %s / %s" % (l1["tl"][:2], l1["toc"][:2]))
        if l2["lang"] != "de": bad("C2 language not kept after reload: %s" % l2["lang"])
        if l3["lang"] != "en" or l3["tl"] != en_t: bad("C2 EN back: %s %s" % (l3["lang"], l3["tl"][:2]))
    ax = [("cover", S(AX))]
    fr.click("[data-nbrw-act=play]"); pg.wait_for_timeout(400)
    v = S("() => [document.querySelector('.nbrw').getAttribute('data-nbrw-view'), !!document.querySelector('.nbrw-doc').getClientRects().length, !!document.querySelector('.nbrw-panel').getClientRects().length]")
    if v != ["doc", True, True]: bad("C1 Play → %s, want doc, document + panel shown" % v)
    S("() => { var w = document.querySelector('.nbrw-win'); w.scrollTop = 0; }"); pg.wait_for_timeout(150)
    ax.append(("doc open", S(AX)))
    fr.click(".nbrw-btn[data-act=panel]"); pg.wait_for_timeout(250); ax.append(("doc closed", S(AX)))
    fr.click(".nbrw-btn[data-act=panel]"); pg.wait_for_timeout(250)
    for k, n in (("a-", 4), ("a+", 9)):
        for _ in range(n): S("k => document.querySelector('.nbrw-btn[data-act=\"' + k + '\"]').click()", k)
        pg.wait_for_timeout(250); S("() => { document.querySelector('.nbrw-win').scrollTop = 0; }"); pg.wait_for_timeout(150)
        ax.append(("lens %d %%" % round(100 * S("() => window.__nbReader.zoom()")), S(AX)))
    for _ in range(5): S("() => document.querySelector('.nbrw-btn[data-act=\"a-\"]').click()")
    pg.wait_for_timeout(200)
    worst = 0
    for nm, a in ax:
        if a["card"] is None: bad("A1 %s: no title card visible" % nm); continue
        d = abs(a["card"] - a["mid"]); worst = max(worst, d)
        if d > 1: bad("A1 %s: title card middle %.1f px off the window middle" % (nm, d))
        if a["pl"] is not None and a["pl"] < a["mid"] - 0.5: bad("A1 %s: the panel reaches %.1f px past the middle" % (nm, a["mid"] - a["pl"]))
    rows.append("%s A1 axis: worst %.2f px over %s · column %s px · window %d px, panel %s px" % (
        tag, worst, "/".join(n for n, _ in ax), "/".join(str(round(a["col"])) for _, a in ax), ax[1][1]["ww"], ax[1][1]["pw"]))
    # C1 back and forth
    S("() => { var w = document.querySelector('.nbrw-win'); w.scrollTop = 3000; }"); pg.wait_for_timeout(150)
    t0 = S("() => document.querySelector('.nbrw-win').scrollTop")
    fr.click(".nbrw-btn[data-act=cover]"); pg.wait_for_timeout(250)
    v1 = S("() => document.querySelector('.nbrw').getAttribute('data-nbrw-view')")
    fr.click("[data-nbrw-act=play]"); pg.wait_for_timeout(250)
    t1 = S("() => document.querySelector('.nbrw-win').scrollTop")
    rows.append("%s C1 ◂ Vorschau → %s · Play → back at %d px (was %d)" % (tag, v1, t1, t0))
    if v1 != "cover": bad("C1 ◂ Vorschau → view %r" % v1)
    if abs(t1 - t0) > 2: bad("C1 back in the document at %d px, was %d" % (t1, t0))
    # G1 + X1
    G = """() => { var g = document.querySelector('[data-nbrw-gate]'); if (!g) return null;
      var m = document.querySelectorAll('.nbrw-mark[data-kind=chap]')[1], l = g.previousElementSibling;
      return {st: g.getAttribute('data-st'), hidden: !g.getClientRects().length, msg: !!(l && l.classList.contains('nbrw-lockmsg') && l.getClientRects().length),
              mark: m && m.getAttribute('data-st'), lab: m && (m.title + ' ' + getComputedStyle(m, '::before').content), xp: document.querySelector('.nbrw-xp-t').textContent,
              fill: document.querySelector('.nbrw-xp-fill').getBoundingClientRect().width}; }"""
    g0 = S(G)
    def answer(val):
        S("() => { var t = document.querySelector('.nbrw-task[data-task=t1]'); t.scrollIntoView({block: 'center'}); }"); pg.wait_for_timeout(100)
        a = S("() => JSON.parse(atob(document.querySelector('.nbrw-task[data-task=t1]').getAttribute('data-a')))")
        for x in a.get("f", []):
            fr.fill('.nbrw-task[data-task=t1] .nbrw-input[data-f="%s"]' % x[0], str(x[1] + (0 if val else 3 * x[2] + 1)))
        fr.click(".nbrw-task[data-task=t1] .nbrw-check"); pg.wait_for_timeout(250)
    answer(False); g1 = S(G); answer(True); g2 = S(G)
    if g0:
        rows.append("%s G1 gate: %s/%s, 🔒 line %s, mark %s %r → t1 wrong: %s, hidden %s, mark %s" % (
            tag, g0["st"], "hidden" if g0["hidden"] else "SHOWN", g0["msg"], g0["mark"], g0["lab"][:14], g1["st"], g1["hidden"], g1["mark"]))
        if g0["st"] != "locked" or not g0["hidden"] or not g0["msg"] or g0["mark"] != "locked" or "\U0001F512" not in (g0["lab"] or ""):
            bad("G1 chapter 2 not locked like Lab: %s" % g0)
        if g1["st"] != "open" or g1["hidden"] or g1["mark"] != "open": bad("G1 t1 answered, chapter 2 still locked: %s" % g1)
        rows.append("%s X1 XP: %r (%.0f px) → t1 right: %r (%.0f px)" % (tag, g0["xp"], g0["fill"], g2["xp"], g2["fill"]))
        if not re.search(r"\b0 / \d+", g0["xp"]) or not re.search(r"\b1 / \d+", g2["xp"]) or not g2["fill"] > g0["fill"]:
            bad("X1 XP %r → %r, fill %.0f → %.0f" % (g0["xp"], g2["xp"], g0["fill"], g2["fill"]))
    else: bad("G1 no gate in the reading version")
    # M1
    M = """() => { var vis = function (e) { return !!e.getClientRects().length; };
      return [[].filter.call(document.querySelectorAll('.nbrw-task[data-kind=calc]'), vis).length,
              [].filter.call(document.querySelectorAll('.nbrw-copy[data-kind=code]'), vis).length,
              document.querySelectorAll('.nbrw-mark[data-kind=calc]').length, document.querySelectorAll('.nbrw-mark[data-kind=code]').length,
              vis(document.querySelector('.nbrw-xp')), document.querySelector('.nbrw').getAttribute('data-nbrw-mode')]; }"""
    res = {}
    for m in ("plain", "calc", "code", "both"):
        fr.click(".nbrw-btn[data-act=cover]"); pg.wait_for_timeout(150)
        fr.click('.nbrw-mode-opt[data-mode="%s"]' % m); fr.click("[data-nbrw-act=play]"); pg.wait_for_timeout(350)
        res[m] = S(M)
        if m == "calc":
            pg.reload(); pg.wait_for_timeout(3000); fr, fe = frame(pg); S = lambda js, a=None: fr.evaluate(js, a)
            S(PLAY); pg.wait_for_timeout(350); res["calc kept"] = S(M)
    rows.append("%s M1 modes [calc, code shown, marks calc, code, XP, mode]: %s" % (tag, " · ".join("%s %s" % kv for kv in res.items())))
    pm, cm, bm = res["plain"], res["calc"], res["both"]
    if pm[:5] != [0, 0, 0, 0, False]: bad("M1 plain shows %s" % pm)
    if not (cm[0] > 0 and cm[1] == 0 and cm[3] == 0): bad("M1 calc shows %s" % cm)
    if not (res["code"][0] == 0 and res["code"][1] > 0 and res["code"][2] == 0): bad("M1 code shows %s" % res["code"])
    if not (bm[0] > 0 and bm[1] > 0): bad("M1 both shows %s" % bm)
    if res["calc kept"][5] != "calc": bad("M1 mode not kept after reload: %s" % res["calc kept"])
    # D1
    dd = S("() => { var d = document.querySelector('details[data-acc]'); if (!d) return null; d.open = false; return d.open; }")
    if dd is None: bad("D1 no accordion")
    else:
        pg.wait_for_timeout(200); pg.reload(); pg.wait_for_timeout(3000); fr, fe = frame(pg); S = lambda js, a=None: fr.evaluate(js, a)
        S(PLAY); pg.wait_for_timeout(300)
        k1 = S("() => document.querySelector('details[data-acc]').open")
        S("""() => { var d = document.querySelector('details[data-acc]'), t = d.querySelector('[id]');
          if (!t) { t = document.createElement('span'); t.id = 'nbr-d1-probe'; d.appendChild(t); }
          var a = document.createElement('a'); a.href = '#' + t.id; a.textContent = 'probe'; a.id = 'nbr-d1-link';
          document.querySelector('.nbrw-doc').insertBefore(a, document.querySelector('.nbrw-doc').firstChild); a.click(); }""")
        pg.wait_for_timeout(250); k2 = S("() => document.querySelector('details[data-acc]').open")
        rows.append("%s D1 accordion closed → after reload open=%s · jump inside → open=%s" % (tag, k1, k2))
        if k1 is not False: bad("D1 accordion state not kept (open after reload)")
        if k2 is not True: bad("D1 a jump into a closed accordion did not open it")
        S("() => { var a = document.getElementById('nbr-d1-link'); if (a) a.remove(); }")
    # R1
    R = """() => { var c = document.querySelector('.nbrw-copy[data-task=t1]'), o = c.querySelector('.nbrw-out');
      return {st: c.getAttribute('data-st'), ok: c.querySelector('.nbrw-fb').getAttribute('data-ok'), fb: c.querySelector('.nbrw-fb').textContent,
              run: c.querySelector('.nbrw-runst').textContent, off: c.querySelector('.nbrw-runst').getAttribute('data-off'),
              err: o.getAttribute('data-err'), out: o.textContent.slice(-160), xp: document.querySelector('.nbrw-xp-t').textContent,
              hl: c.querySelectorAll('.nbrw-hl .nbrw-hl-k').length}; }"""
    def put(code):
        S("c => { var t = document.querySelector('.nbrw-copy[data-task=t1] .nbrw-ta'); t.scrollIntoView({block: 'center'}); t.value = c; t.dispatchEvent(new Event('input')); }", code)
    def runwait(ms=120000):
        fr.click(".nbrw-copy[data-task=t1] .nbrw-run"); pg.wait_for_timeout(300)
        first = S(R)["run"]
        fr.wait_for_function("() => !document.querySelector('.nbrw-copy[data-task=t1] .nbrw-run').disabled", timeout=ms)
        return first, S(R)
    hl = S(R)["hl"]
    if hl < 2: bad("R1 the code field is not coloured (%d keywords marked)" % hl)
    if not have:      # README rule 2: a test that cannot reach its precondition is red, never skipped
        bad("R1 BAD no local Pyodide %s (npm pack failed; set DIGICHEM_PYODIDE_DIR to an unpacked `npm pack pyodide@%s`)" % (PYV, PYV))
    else:
        put(WRONG); f0, r0 = runwait()
        put(BROKEN); _, r1 = runwait(30000)
        put(RIGHT); _, r2 = runwait(30000)
        rows.append("%s R1 ▶: status %r · wrong → %s/%s · broken → err %s, %r, st %s · right → %s/%s, %s · keywords %d" % (
            tag, f0[:40], r0["st"], r0["ok"], r1["err"], r1["out"].strip().splitlines()[-1][:50] if r1["out"].strip() else "", r1["st"],
            r2["st"], r2["ok"], r2["xp"], hl))
        if not re.search("Loading Python|Python wird geladen", f0): bad("R1 no loading status: %r" % f0)
        if r0["st"] != "wrong" or r0["ok"] != "0": bad("R1 wrong code: %s" % r0)
        if r1["err"] != "1" or "SyntaxError" not in r1["out"] or r1["st"] != "wrong": bad("R1 broken code: %s" % r1)
        if r2["st"] != "solved" or r2["ok"] != "1" or not re.search(r"\b2 / \d+", r2["xp"]): bad("R1 right code: %s" % r2)
        if shots: S("() => document.querySelector('.nbrw-copy[data-task=t1]').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(200); pg.screenshot(path=os.path.join(shots, "E26.3-run-en-hell.png"))
        pg.reload(); pg.wait_for_timeout(3000); fr, fe = frame(pg); S = lambda js, a=None: fr.evaluate(js, a); S(PLAY); pg.wait_for_timeout(300)
        k = S("() => document.querySelector('.nbrw-copy[data-task=t1]').getAttribute('data-st')")
        if k != "solved": bad("R1 coding t1 not kept after reload: %s" % k)
    ctx.close()
    # R2: the CDN refused
    ctx = b.new_context(viewport={"width": 1400, "height": 900})
    try: ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=base.rstrip("/"))
    except Exception: pass
    py_route(ctx, "off")
    pg = ctx.new_page(); pg.goto(base + name); pg.wait_for_timeout(3000)
    fr, fe = frame(pg); S = lambda js, a=None: fr.evaluate(js, a); S(PLAY); pg.wait_for_timeout(300)
    put(WRONG); _, r = runwait(30000)
    cb = S("() => { var b = document.querySelector('.nbrw-copy[data-task=t1] .nbrw-copybtn'); return b ? [b.textContent, !!b.getClientRects().length] : null; }")
    fr.click(".nbrw-copy[data-task=t1] .nbrw-copybtn"); pg.wait_for_timeout(300)
    try: clip = pg.evaluate("() => navigator.clipboard.readText()")
    except Exception as e: clip = "?" + str(e)[:60]
    rows.append("%s R2 no network: off=%s %r · button %s · clipboard %r" % (tag, r["off"], r["run"][:70], cb, clip[-40:]))
    if r["off"] != "1" or 'pruefe("t1", …)' not in r["run"]: bad("R2 no honest sentence with pruefe: %r" % r["run"])
    if not cb or not cb[1] or not re.search("clipboard|Zwischenablage", cb[0]): bad("R2 no visible copy button: %s" % cb)
    if not clip.startswith("?") and (FNAME not in clip or 'pruefe("t1")' not in clip): bad("R2 clipboard %r" % clip)
    ctx.close()

def main():
    global RIGHT, WRONG, BROKEN, FNAME
    import nbpick
    args = sys.argv[1:]
    src = nbpick.from_argv(sys.argv)              # E28: no notebook → the template
    _id = (json.load(open(src, encoding="utf-8")).get("metadata", {}).get("digichemjn", {}) or {}).get("id")
    if _id in CODE_T1:
        RIGHT, WRONG, BROKEN, FNAME = CODE_T1[_id]
    shots = args[args.index("--shots") + 1] if "--shots" in args else None
    jout = args[args.index("--json") + 1] if "--json" in args else None
    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    rows, fails = [], []
    tmpd = tempfile.mkdtemp(prefix="envrd_"); srv = serve(tmpd); runs = {}
    base = "http://127.0.0.1:%d/" % srv.server_address[1]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        try:
            for tag, env, dark in (("en light", {}, False), ("en dark", {"PYCHARM_HOSTED": "1"}, True),
                                   ("de light", {"DIGICHEM_LANG": "de"}, False)):
                outs, errs, chapters = run_cell(src, env)
                runs[tag] = (outs, chapters)
                if errs: fails.append("%s the run raised: %s" % (tag, errs[:1]))
                if any("requestFullscreen" in (o["data"].get("text/html") or "") for o in outs if "nbreading" in (o["data"].get("text/html") or "")):
                    fails.append("%s W1 the reading output calls requestFullscreen" % tag)
                name = re.sub(r"\W+", "_", tag) + ".html"
                h = host_page(outs, dark).replace("</iframe><script>", "</iframe><div style='height:2400px'></div><script>", 1)
                if "height:2400px" not in h:
                    h = h.replace("<script>function fit", "<div style='height:2400px'></div><script>function fit", 1)
                open(os.path.join(tmpd, name), "w", encoding="utf-8").write(h)
                ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme="dark" if dark else "light")
                pg = ctx.new_page(); pg.goto(base + name); pg.wait_for_timeout(3000)
                lang = "de" if "DIGICHEM_LANG" in env else "en"
                check(pg, tag, len(chapters), lang, fails, rows, shots)
                if tag == "en light" and not any(f.startswith(tag + " W1") for f in fails): kept(pg, tag, fails, rows)
                ctx.close()
            # E26 Teil 3: preview, axis, gating, XP, mode, accordions, ▶ in the window
            outs = [dict(o, data=dict(o["data"])) for o in runs["en light"][0]]
            used = []
            for o in outs:
                hh = o["data"].get("text/html") or ""
                if hh.startswith("<div class='nbreading'"):
                    o["data"]["text/html"], used = standin(hh, runs["de light"][1])
            open(os.path.join(tmpd, "e263.html"), "w", encoding="utf-8").write(
                host_page(outs, False).replace("</iframe><script>", "</iframe><div style='height:2400px'></div><script>", 1))
            check3(b, base, "e263.html", "en light", fails, rows, shots, used, runs["de light"][1])
            # W9 nbconvert page: a notebook front end's page — no window
            ex = os.path.join(tmpd, "nb.ipynb"); shutil.copy(src, ex)
            subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", ex],
                           check=True, capture_output=True, cwd=tmpd)
            subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "html", ex], check=True, capture_output=True, cwd=tmpd)
            ctx = b.new_context(viewport={"width": 1400, "height": 900})
            pg = ctx.new_page(); pg.goto(base + "nb.html"); pg.wait_for_timeout(3000)
            n = pg.evaluate("() => [document.querySelectorAll('.nbrw').length, document.querySelectorAll('.nbreading').length]")
            rows.append("W9 nbconvert (scripts on): windows %d, reading versions %d" % tuple(n))
            if n[0] != 0: fails.append("W9 nbconvert page: %d reading windows, want 0" % n[0])
            if n[1] < 1: fails.append("W9 nbconvert page: no reading version")
            ctx.close()
        except Exception as e:
            fails.append("BAD %s" % str(e)[:300])
        b.close()
    srv.shutdown(); shutil.rmtree(tmpd, ignore_errors=True)
    print("\n".join(rows))
    if jout: json.dump({"rows": rows, "fails": fails}, open(jout, "w"), indent=1, ensure_ascii=False)
    print("REGRESS-ENV-READER OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
