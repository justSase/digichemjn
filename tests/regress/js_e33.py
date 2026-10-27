"""E33 · JS — PYCHARM + VS CODE (LESEFENSTER), LAB/LITE C1 (Werkstatt JS, 2026-10-13).
    python3 tests/regress/js_e33.py [<notebook.ipynb>] [--only B4,B5] [--shots DIR] [--no-lab]

The reader's 11 pictures + 2 videos of v1.78 (PyCharm, VS Code, Lab, Lite), STOP.md „E33 — GILT JETZT“, the JS
points. The reading window as env_reader/js_e31 build it: the notebook's cell in a real kernel, every output in an
iframe of its own (= PyCharm), no widget manager, a host page with 1500 px of „cells“ above the outputs, 1400 × 900,
served over http (a secure page: localhost). The template (`--nb vorlage`) unless a notebook is named.
Rows:
  B1a after the run    the window's top at the top of what one sees (±4 px of the host's viewport): the host scrolled
  B1b height           fresh: the window = screen.availHeight − 240 (clamped 300 … 2400), not 600; ↕+ → +100
  B1c wheel at the ends the window at its bottom / top: 3 notches on → the page moves 0 px
  B2  preview timeline hover over a chapter mark → the description line under the row says its name (and the mode
                       heading below moves 0 px); a click on Title folds the row to Title + end, again → all back; a
                       click on a part folds up to the next part
  B3  account          👤 → the drawer; New account (name, password twice) → logged in (digichemjn.acct.on.<id> = 1);
                       log out; name + password → in; a wrong password → an error line; „Show my code“ → DCJ1.….XX;
                       out, then that code + password → in; the cover's „Account“ holds the same form
  B4  document         wheel: 4 notches quickly ≥ ×1.4 of 4 slowly, a touchpad (40 × 10 px) unchanged ±5 %; the rail in
                       the panel's middle (±2 px, open and shut); no fold button in the panel, one in the tool column;
                       a click on Title and on „End of the guided part“ → each on the reading height (±2 px)
  B5  GUI size         ⊕ to 130 %: a tool button ×1.3 (±1 px); the panel's width, the grip, the marker and the window
                       unchanged (±1 px); the lens 150 %: grip and marker ×1.5 (±8 %); the panel at 2 × its standard
                       width: a mark's dot ×2 (±8 %)
  B6  tools            ⌨ ⚙ ✎ 👤 ✉ in the tool column (data-act kbd|gear|mode|acct|fb), each opens its drawer; ✎: four
                       modes (a click sets it); ⚙: EN|DE + feedback; ✉: one line with an address (…@…); ⌨: ≥ 6 keys; Esc closes
  D   VS Code theme    the frames' <body class="vscode-dark"> under a light OS scheme → the window dark (its surface
                       luminance < 0.2); vscode-light under a dark OS scheme → light (> 0.6)
  C1  Lab              (real JupyterLab, skipped with --no-lab) the panel opened: `.nbp-xp` at its top („Progress
                       s / n“, n = the exercises of the mode), `.nbp-cur` at its foot with the chapter's name
A1 (the other language encoded) is Python's part, rebuilt by its own script before 20-reader (VERTRAG-E33-py; py_e33).
v1.78 (`b9350b0c`): red B1a, B1b, B1c, B2, B3, B4, B5, B6, D, C1. Owner: JS. exit 0 = REGRESS-JS-E33 OK."""
import sys, os, re, json, tempfile, time, shutil, html as _h
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
if __name__ != "__main__":
    raise ImportError("js_e33 is a stand-alone script")
from env_iframe import run_cell, host_page, frame_doc
from env_reader import serve

ONLY = None
args = sys.argv[1:]
if "--only" in args: ONLY = args[args.index("--only") + 1].split(",")
want = lambda k: not ONLY or any(k.startswith(x) for x in ONLY)
shots = args[args.index("--shots") + 1] if "--shots" in args else None
NOLAB = "--no-lab" in args

FR = """() => [].findIndex.call(document.querySelectorAll('iframe.out'), function (f) { try { return !!f.contentDocument.querySelector('.nbrw'); } catch (e) { return false; } })"""
PLAY = """() => { var w = document.querySelector('.nbrw'), p = w && w.querySelector('[data-nbrw-act=play]');
  if (w && w.getAttribute('data-nbrw-view') === 'cover' && p) p.click(); return w ? w.getAttribute('data-nbrw-view') : null; }"""
BOX = """(s) => { var e = (typeof s === 'string') ? document.querySelector(s) : null; if (!e || !e.getClientRects().length) return null;
  var r = e.getBoundingClientRect(); return {l: r.left, t: r.top, w: r.width, h: r.height, r: r.right, b: r.bottom, cx: r.left + r.width / 2, cy: r.top + r.height / 2}; }"""

ROWS, FAILS = [], []
def row(k, ok, det, count=True):
    ROWS.append((k, ok, det)); print("%-4s %s  %s" % (k, "ok " if ok else ("RED" if count else "red (info)"), det)); sys.stdout.flush()
    if not ok and count: FAILS.append(k)

def frame(pg):
    fi = pg.evaluate(FR)
    if fi < 0: return None, None
    return [f for f in pg.frames if f != pg.main_frame][fi], pg.query_selector_all("iframe.out")[fi]

def host(outs, dark=False, body_cls=""):
    h = host_page(outs, dark)
    if body_cls: h = h.replace("&lt;body style=&#x27;margin:0&#x27;&gt;", "&lt;body class=&#x27;%s&#x27; style=&#x27;margin:0&#x27;&gt;" % body_cls)
    h = h.replace("<iframe class='out'", "<div class='cells' style='height:1500px;border:1px dashed #aaa'>cells above the outputs</div><iframe class='out'", 1)
    return h.replace("</iframe><script>", "</iframe><div style='height:2400px'></div><script>", 1)

def guard(k, fn):
    try: fn()
    except Exception as e: row(k, False, "BAD %s" % str(e).splitlines()[0][:160])

def window_rows(b, base):
    ctx = b.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
    pg.goto(base + "light.html"); pg.wait_for_timeout(3000)
    fr, fe = frame(pg)
    if not fr: row("W0", False, "no reading window"); return
    S = lambda js, a=None: fr.evaluate(js, a)
    def P(x, y): bx = fe.bounding_box(); return bx["x"] + x, bx["y"] + y
    def onscreen():
        pg.evaluate("y => window.scrollTo(0, y)", int(fe.bounding_box()["y"] + pg.evaluate("window.scrollY"))); pg.wait_for_timeout(150)
    def wy(): return pg.evaluate("window.scrollY")
    # ---- B1a: the host scrolled to the window (before we touch anything)
    def _B1a():
        nonlocal pg
        t = S("() => { var w = document.querySelector('.nbrw'); return w.getBoundingClientRect().top; }") + fe.bounding_box()["y"]
        row("B1a", abs(t) <= 4, "after the run the window's top stands %.0f px from the top of the host's view (page scrolled %d px)" % (t, wy()))
    if want("B1a"): guard("B1a", _B1a)
    onscreen()
    # ---- B1b: the height
    def _B1b():
        nonlocal pg
        g = S("() => ({h: document.querySelector('.nbrw-win').getBoundingClientRect().height, s: screen.availHeight})")
        want_h = max(300, min(2400, round((g["s"] - 240) / 10) * 10))
        S("() => document.querySelector('.nbrw-btn[data-act=\"h+\"]').click()"); pg.wait_for_timeout(300)
        g2 = S("() => document.querySelector('.nbrw-win').getBoundingClientRect().height")
        S("() => document.querySelector('.nbrw-btn[data-act=\"h-\"]').click()"); pg.wait_for_timeout(300)
        row("B1b", abs(g["h"] - want_h) <= 1 and abs(g2 - g["h"] - 100) <= 1,
            "fresh window %.0f px (screen.availHeight %d → want %d, not 600) · ↕+ %.0f" % (g["h"], g["s"], want_h, g2))
    if want("B1b"): guard("B1b", _B1b)
    # ---- B2: the preview's timeline
    def _B2():
        nonlocal pg
        r = S("""() => { var c = document.querySelector('.nbrw-cover'), d = c.querySelector('.nbrw-cv-dot[data-kind=chap]'), m = c.querySelector('.nbrw-modes');
          if (!d || !m) return null; var y0 = m.getBoundingClientRect().top;
          d.dispatchEvent(new PointerEvent('pointerover', {bubbles: true}));
          var ds = c.querySelector('.nbrw-cv-desc'), y1 = m.getBoundingClientRect().top, dtx = ds ? ds.innerText.replace(/\\s+/g, ' ').trim() : null;
          var vis = function () { return [].filter.call(c.querySelectorAll('.nbrw-cv-dot'), function (x) { return x.getClientRects().length && getComputedStyle(x).display !== 'none'; }).length; };
          var n0 = vis(), t = c.querySelector('.nbrw-cv-dot[data-kind=title]'), g = [].slice.call(c.querySelectorAll('.nbrw-cv-dot[data-kind=group]'));
          t && t.click(); var n1 = vis(); t && t.click(); var n2 = vis();
          var cg = g[1]; cg && cg.click(); var n3 = vis(); cg && cg.click();
          return {name: (d.querySelector('.nbrw-cv-lab') || {}).textContent || '', desc: dtx, dy: y1 - y0, n0: n0, n1: n1, n2: n2, n3: n3, vis: vis()}; }""")
        ok = bool(r and r["desc"] and r["name"] and r["name"] in r["desc"] and abs(r["dy"]) < 0.5 and r["n1"] <= 2 and r["n2"] == r["n0"] and r["n0"] > r["n3"] > r["n1"] and r["vis"] == r["n0"])
        row("B2", ok, "hover chapter → line %r (name %r), mode heading moved %s px · dots %s, Title folded %s, unfolded %s, Content folded %s"
            % (r and r["desc"], r and r["name"], r and round(r["dy"], 1), r and r["n0"], r and r["n1"], r and r["n2"], r and r["n3"]))
        if shots: S("() => { var d = document.querySelector('.nbrw-cover .nbrw-cv-dot[data-kind=chap]'); d && d.dispatchEvent(new PointerEvent('pointerover', {bubbles: true})); }"); pg.wait_for_timeout(200); pg.screenshot(path=os.path.join(shots, "E33-js-B2-vorschau-hover.png"))
    if want("B2"): guard("B2", _B2)
    # ---- B3 on the cover: the form is there
    cov_form = S("() => !!document.querySelector('.nbrw-cover details.nbrw-acct .nbrw-acct-form')")
    nonl = None
    S(PLAY); pg.wait_for_timeout(700); onscreen()
    # ---- B1c: the wheel at the ends
    def _B1c():
        nonlocal pg
        cx, cy = P(*[S("() => { var r = document.querySelector('.nbrw-win').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }")][0])
        S("() => { var w = document.querySelector('.nbrw-win'); w.scrollTop = w.scrollHeight; }"); pg.wait_for_timeout(200)
        pg.mouse.move(cx, cy); y0 = wy()
        for _ in range(3): pg.mouse.wheel(0, 200); pg.wait_for_timeout(80)
        pg.wait_for_timeout(300); y1 = wy()
        S("() => { document.querySelector('.nbrw-win').scrollTop = 0; }"); pg.wait_for_timeout(200)
        pg.evaluate("y => window.scrollTo(0, y)", y1); pg.wait_for_timeout(100); y2 = wy()
        for _ in range(3): pg.mouse.wheel(0, -200); pg.wait_for_timeout(80)
        pg.wait_for_timeout(300); y3 = wy()
        row("B1c", y1 == y0 and y3 == y2, "window at its bottom: 3 notches down → page %+d px · at its top: 3 notches up → page %+d px" % (y1 - y0, y3 - y2))
        onscreen()
    if want("B1c"): guard("B1c", _B1c)
    # ---- B4
    def _B4():
        nonlocal pg
        def notches(n, gap, dy=100):
            S("() => { var w = document.querySelector('.nbrw-win'); w.scrollTop = Math.round(w.scrollHeight / 3); }"); pg.wait_for_timeout(500)
            cx, cy = P(*S("() => { var r = document.querySelector('.nbrw-win').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }"))
            pg.mouse.move(cx, cy); t0 = S("() => document.querySelector('.nbrw-win').scrollTop")
            for _ in range(n): pg.mouse.wheel(0, dy); pg.wait_for_timeout(gap)
            pg.wait_for_timeout(200); return S("() => document.querySelector('.nbrw-win').scrollTop") - t0
        slow, fast, pad = notches(4, 420), notches(4, 30), notches(40, 15, 10)
        row("B4w", slow > 0 and fast / slow >= 1.4 and abs(pad - 400) <= 20,
            "wheel: 4 slow notches %d px, 4 quick %d px (×%.2f) · touchpad 40 × 10 px → %d px" % (slow, fast, fast / max(1, slow), pad))
        c = []
        for st in ("open", "closed"):
            if S("() => document.querySelector('.nbrw').getAttribute('data-nbrw-panel')") != st: S("() => document.querySelector('.nbrw-btn[data-act=panel]').click()"); pg.wait_for_timeout(400)
            c.append(S("""() => { var p = document.querySelector('.nbrw-panel').getBoundingClientRect(), t = document.querySelector('.nbrw-track'), r = t.getBoundingClientRect(),
              bl = parseFloat(getComputedStyle(t).borderLeftWidth) || 0; return (r.left + bl / 2) - (p.left + p.width / 2); }"""))
        btn = S("() => [document.querySelectorAll('.nbrw-panel [data-act=panel]').length, document.querySelectorAll('.nbrw-tools [data-act=panel]').length]")
        row("B4c", all(abs(x) <= 2 for x in c) and btn == [0, 1], "rail − panel middle: open %.1f, shut %.1f px · fold buttons in the panel %d, in the tools %d" % (c[0], c[1], btn[0], btn[1]))
        def on_line(kind):
            S("k => { var m = document.querySelector('.nbrw-mark[data-kind=' + k + ']'); if (m) m.click(); }", kind); pg.wait_for_timeout(900)
            return S("""(k) => { var w = document.querySelector('.nbrw-win'), R = window.__nbReader, e = k === 'title' ? document.querySelector('.nbrw-doc [class*="nbtitle-card"]') : document.querySelector('.nbrw-doc .nbread-end');
              if (!e) return null; var r = e.getBoundingClientRect(); return r.top + r.height / 2 - (w.getBoundingClientRect().top + R.line()); }""", kind)
        S("() => { var w = document.querySelector('.nbrw-win'); w.scrollTop = Math.round(w.scrollHeight / 2); }"); pg.wait_for_timeout(300)
        dt = on_line("title"); de_ = on_line("end")
        row("B4r", dt is not None and de_ is not None and abs(dt) <= 2 and abs(de_) <= 2, "Title on the reading height %s px · End of the guided part %s px" % (dt and round(dt, 1), de_ and round(de_, 1)))
    if want("B4"): guard("B4", _B4)
    # ---- B5
    def _B5():
        nonlocal pg
        M = """() => { var q = function (s) { var e = document.querySelector(s); return e && e.getClientRects().length ? e.getBoundingClientRect() : null; };
          var m = [].filter.call(document.querySelectorAll('.nbrw-mark'), function (x) { return x.getClientRects().length; })[0];
          return {btn: q('.nbrw-tools .nbrw-btn[data-act="a+"]').height, pan: q('.nbrw-panel').width, grip: q('.nbrw-grip') && q('.nbrw-grip').width,
                  mk: q('.nbrw-marker') && q('.nbrw-marker').width, win: q('.nbrw-win').height, dot: m ? m.getBoundingClientRect().height : null}; }"""
        if S("() => document.querySelector('.nbrw').getAttribute('data-nbrw-panel')") != "open": S("() => document.querySelector('.nbrw-btn[data-act=panel]').click()")
        S("() => { window.__nbReader.pw(168); window.__nbReader.gs(100); }"); pg.wait_for_timeout(400)
        S("() => { var m = document.querySelector('.nbrw-mark[data-kind=title]'); m && m.click(); }"); pg.wait_for_timeout(600)
        a = S(M); S("() => window.__nbReader.gs(130)"); pg.wait_for_timeout(500); g = S(M); S("() => window.__nbReader.gs(100)"); pg.wait_for_timeout(300)
        ok1 = abs(g["btn"] - a["btn"] * 1.3) <= 1 and abs(g["pan"] - a["pan"]) <= 1 and abs(g["grip"] - a["grip"]) <= 1 and abs(g["mk"] - a["mk"]) <= 1 and abs(g["win"] - a["win"]) <= 1
        for _ in range(5): S("() => document.querySelector('.nbrw-btn[data-act=\"a+\"]').click()")
        pg.wait_for_timeout(600); z = S(M)
        for _ in range(5): S("() => document.querySelector('.nbrw-btn[data-act=\"a-\"]').click()")
        pg.wait_for_timeout(400)
        S("() => window.__nbReader.pw(336)"); pg.wait_for_timeout(600); w2 = S(M); S("() => window.__nbReader.pw(168)"); pg.wait_for_timeout(400)
        r = lambda x, y: (y / x) if (x and y) else 0
        ok2 = abs(r(a["grip"], z["grip"]) - 1.5) <= 0.12 and abs(r(a["mk"], z["mk"]) - 1.5) <= 0.12
        ok3 = abs(r(a["dot"], w2["dot"]) - 2) <= 0.16
        row("B5", ok1 and ok2 and ok3, "GUI 130 %%: button %.0f → %.1f, panel %.0f → %.0f, grip %.0f → %.0f, marker %.0f → %.0f, window %.0f → %.0f · lens 150 %%: grip ×%.2f, marker ×%.2f · panel 336: dot ×%.2f"
            % (a["btn"], g["btn"], a["pan"], g["pan"], a["grip"], g["grip"], a["mk"], g["mk"], a["win"], g["win"], r(a["grip"], z["grip"]), r(a["mk"], z["mk"]), r(a["dot"], w2["dot"])))
    if want("B5"): guard("B5", _B5)
    # ---- B6
    def _B6():
        nonlocal pg
        r = S("""() => { var out = {}, w = document.querySelector('.nbrw');
          ['kbd', 'gear', 'mode', 'acct', 'fb'].forEach(function (k) { var b = w.querySelector('.nbrw-tools [data-act=' + k + ']'); if (!b || !b.getClientRects().length) { out[k] = null; return; }
            b.click(); var d = w.querySelector('.nbrw-drawer'), on = d && d.getClientRects().length && d.getAttribute('data-kind') === k;
            out[k] = {on: !!on, keys: d ? d.querySelectorAll('.nbrw-keys tr').length : 0, modes: d ? d.querySelectorAll('[data-mode]').length : 0,
                      langs: d ? d.querySelectorAll('.nbrw-dr-lang').length : 0, fb: d ? ((d.querySelector('.nbrw-fb') || {}).textContent || '') : ''};
            if (k === 'mode') { var c = d.querySelector('[data-mode=calc]'); c && c.click(); out.md = window.__nbReader.mode(); var b2 = w.querySelector('.nbrw-drawer [data-mode=both]'); b2 && b2.click(); }
            d.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true})); out[k].esc = !d.getClientRects().length; });
          out.back = window.__nbReader.mode(); return out; }""")
        K = ("kbd", "gear", "mode", "acct", "fb")
        ok = all(r.get(k) and r[k]["on"] and r[k]["esc"] for k in K) and r["kbd"]["keys"] >= 6 and r["mode"]["modes"] == 4 \
            and r["md"] == "calc" and r["back"] == "both" and "@" in r["fb"]["fb"] and "@" in r["gear"]["fb"]
        row("B6", ok, "drawers %s · keys %s · modes %s (calc → %s, back %s) · languages %s · feedback %r"
            % ({k: bool(r.get(k) and r[k]["on"] and r[k]["esc"]) for k in K}, r.get("kbd") and r["kbd"]["keys"],
               r.get("mode") and r["mode"]["modes"], r.get("md"), r.get("back"), r.get("gear") and r["gear"]["langs"], r.get("fb") and r["fb"]["fb"][:60]))
        if shots:
            S("() => document.querySelector('.nbrw-tools [data-act=mode]').click()"); pg.wait_for_timeout(200); pg.screenshot(path=os.path.join(shots, "E33-js-B6-modus.png"))
            S("() => window.__nbReader.drawer('')")
    if want("B6"): guard("B6", _B6)
    # ---- B3
    def _B3():
        nonlocal pg
        def acct_do(js, wait=2500):
            S(js); pg.wait_for_timeout(wait)
            return S("""() => { var d = document.querySelector('.nbrw-drawer'), m = d && d.querySelector('.nbrw-acct-msg'), c = d && d.querySelector('.nbrw-acct-code code');
              return {a: window.__nbReader.acct(), step: d && d.querySelector('form') ? d.querySelector('form').getAttribute('data-step') : null,
                      msg: m ? m.textContent : '', kind: m ? m.getAttribute('data-kind') : '', code: c ? c.textContent : '', on: localStorage.getItem('digichemjn.acct.on.' + window.__nbReader.id)}; }""")
        fill = lambda pairs, do: "() => { var d = document.querySelector('.nbrw-drawer'); " + " ".join(
            "d.querySelector('.%s').value = %s;" % (c, json.dumps(v)) for c, v in pairs) + " d.querySelector('[data-do=%s]').click(); }" % do
        S("() => { localStorage.removeItem('digichemjn.account.v1'); document.querySelector('.nbrw-tools [data-act=acct]').click(); }"); pg.wait_for_timeout(300)
        s0 = acct_do("() => {}", 100)
        s1 = acct_do("() => document.querySelector('.nbrw-drawer [data-do=new]').click()", 300)
        s2 = acct_do(fill([("nbrw-acct-name", "Ada"), ("nbrw-acct-pw1", "geheim123"), ("nbrw-acct-pw2", "geheim123")], "mk"))
        s3 = acct_do("() => document.querySelector('.nbrw-drawer [data-do=out]').click()", 300)
        s4 = acct_do(fill([("nbrw-acct-name", "Ada"), ("nbrw-acct-pw", "falsch999")], "in"))
        s5 = acct_do(fill([("nbrw-acct-name", "Ada"), ("nbrw-acct-pw", "geheim123")], "in"))
        s6 = acct_do(fill([("nbrw-acct-pw", "geheim123")], "code"), 3500)
        code = s6["code"]
        S("() => document.querySelector('.nbrw-drawer [data-do=out]').click()"); pg.wait_for_timeout(300)
        S("() => localStorage.removeItem('digichemjn.account.v1')"); pg.wait_for_timeout(100)
        S("() => { window.__nbReader.drawer(''); window.__nbReader.drawer('acct'); }"); pg.wait_for_timeout(200)
        s7 = acct_do(fill([("nbrw-acct-name", "Bea"), ("nbrw-acct-pw", "geheim123"), ("nbrw-acct-code", code)], "in"), 4000)
        if shots: pg.screenshot(path=os.path.join(shots, "E33-js-B3-konto.png"))
        S("() => { var a = JSON.parse(localStorage.getItem('digichemjn.account.v1') || 'null'); localStorage.removeItem('digichemjn.account.v1'); localStorage.removeItem('digichemjn.acct.on.' + window.__nbReader.id); window.__nbReader.drawer(''); }")
        ok = (s0["step"] == "out" and s1["step"] == "new" and s2["a"] and s2["a"]["on"] and s2["on"] == "1" and s2["a"]["name"] == "Ada"
              and s3["a"] and not s3["a"]["on"] and s3["on"] is None and s4["kind"] == "err" and not s4["a"]["on"] and s5["a"]["on"]
              and re.match(r"^DCJ1\.[A-Za-z0-9_-]+\.[0-9A-Z]{2}$", code or "") and s7["a"] and s7["a"]["on"] and s7["a"]["id"] == s2["a"]["id"] and cov_form)
        row("B3", bool(ok), "steps %s · new → in %s (%s) · out %s · wrong password %s %r · name+password → %s · code %s… · code+password on a fresh browser → %s, same id %s · cover form %s"
            % ([s0["step"], s1["step"]], s2["a"] and s2["a"]["on"], s2["on"], s3["a"] and s3["a"]["on"], s4["kind"], s4["msg"][:40], s5["a"] and s5["a"]["on"],
               (code or "")[:12], s7["a"] and s7["a"]["on"], bool(s7["a"] and s2["a"] and s7["a"]["id"] == s2["a"]["id"]), cov_form))
    if want("B3"): guard("B3", _B3)
    if shots:
        S("() => { var w = document.querySelector('.nbrw-win'); w.scrollTop = window.__nbReader ? 0 : 0; }"); onscreen()
        S("() => { var m = document.querySelector('.nbrw-mark[data-kind=title]'); m && m.click(); }"); pg.wait_for_timeout(700)
        pg.screenshot(path=os.path.join(shots, "E33-js-fenster-dokument-hell.png"))
    if errs: row("ERR", False, "page errors: %s" % errs[:2])
    ctx.close()

def d_rows(b, base):
    LUM = """() => { var w = document.querySelector('.nbrw'), c = getComputedStyle(w).backgroundColor, m = /rgba?\\(([^)]+)\\)/.exec(c) || [0, '255,255,255'];
      var p = m[1].split(/[ ,\\/]+/).filter(Boolean).map(parseFloat), f = function (v) { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
      return {theme: w.getAttribute('data-nbrw-theme'), host: w.getAttribute('data-nbrw-host'), bg: c, lum: 0.2126 * f(p[0]) + 0.7152 * f(p[1]) + 0.0722 * f(p[2])}; }"""
    res = {}
    for nm, sch in (("vsdark.html", "light"), ("vslight.html", "dark")):
        ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme=sch); pg = ctx.new_page()
        pg.goto(base + nm); pg.wait_for_timeout(3000); fr, fe = frame(pg)
        res[nm] = fr.evaluate(LUM) if fr else None
        if shots and nm == "vsdark.html":
            fr.evaluate(PLAY); pg.wait_for_timeout(600); pg.evaluate("y => window.scrollTo(0, y)", int(fe.bounding_box()["y"] + pg.evaluate("window.scrollY")))
            pg.screenshot(path=os.path.join(shots, "E33-js-D-vscode-dunkel.png"))
        ctx.close()
    a, c = res["vsdark.html"], res["vslight.html"]
    row("D", bool(a and c and a["theme"] == "dark" and a["lum"] < 0.2 and c["theme"] == "light" and c["lum"] > 0.6),
        "body.vscode-dark under a light OS: %s · body.vscode-light under a dark OS: %s" % (a, c))

def c1_lab(src):
    from lab_keys import ensure_lab, kill_sessions, CHROME
    from playwright.sync_api import sync_playwright
    sys.argv = [sys.argv[0]]
    import run as R
    BASE, ROOT = ensure_lab(os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:1"))
    nid = R.nb_id(src)
    p = sync_playwright().start(); b = p.chromium.launch(executable_path=CHROME)
    try:
        ctx = b.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page()
        kill_sessions(BASE); R.set_lab_theme(BASE, "light")
        name = "e33_%d_%s" % (int(time.time() * 1000) % 1000000, os.path.basename(src)); shutil.copy(src, os.path.join(ROOT, name))
        pg.goto(BASE + "/lab/tree/" + name + "?reset")
        pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000); pg.wait_for_timeout(1500)
        R.run_front(pg, nid); pg.wait_for_timeout(1500)
        g = pg.query_selector("#nbpanel-root .nbgrip")
        if g:
            bb = g.bounding_box(); pg.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); pg.mouse.down()
            pg.mouse.move(bb["x"] - 200, bb["y"] + bb["height"] / 2, steps=8); pg.mouse.up(); pg.wait_for_timeout(1500)
        M = """() => { var r = document.querySelector('#nbpanel-root .nbrail'); if (!r) return null; var x = r.querySelector('.nbp-xp'), c = r.querySelector('.nbp-cur'), R = r.getBoundingClientRect();
          var b = function (e) { if (!e || !e.getClientRects().length) return null; var q = e.getBoundingClientRect(); return {t: q.top - R.top, b: R.bottom - q.bottom, w: q.width}; };
          return {w: R.width, xp: b(x), xpt: x ? x.textContent : '', n: x ? +x.getAttribute('data-n') : null, cur: b(c), curt: c ? c.textContent : ''}; }"""
        a = pg.evaluate(M)
        if shots: pg.screenshot(path=os.path.join(shots, "E33-js-C1-lab-panel.png"))
        ctx.close()
        ok = bool(a and a["xp"] and a["xp"]["t"] <= 20 and re.match(r"^(Progress|Fortschritt) \d+ / \d+$", a["xpt"]) and a["n"] and a["cur"] and a["cur"]["b"] <= 20 and a["curt"])
        row("C1", ok, "Lab panel %s px: progress at its top %s %r · chapter at its foot %s %r" % (a and round(a["w"]), a and a["xp"], a and a["xpt"], a and a["cur"], a and a["curt"]))
    finally:
        b.close(); p.stop()

def main():
    import nbpick
    src = nbpick.from_argv(sys.argv)
    print("notebook:", src)
    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    tmpd = tempfile.mkdtemp(prefix="jse33_"); srv = serve(tmpd)
    base = "http://127.0.0.1:%d/" % srv.server_address[1]
    outs, errs, chapters = run_cell(src, {})
    if errs: row("RUN", False, "the run raised: %s" % errs[:1])
    open(os.path.join(tmpd, "light.html"), "w", encoding="utf-8").write(host(outs))
    open(os.path.join(tmpd, "vsdark.html"), "w", encoding="utf-8").write(host(outs, False, "vscode-dark"))
    open(os.path.join(tmpd, "vslight.html"), "w", encoding="utf-8").write(host(outs, True, "vscode-light"))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        try:
            window_rows(b, base)
            if want("D"): d_rows(b, base)
        finally:
            b.close()
    if want("C1") and not NOLAB: c1_lab(src)
    print("REGRESS-JS-E33 %s (%d rows, red: %s)" % ("OK" if not FAILS else "FAIL", len(ROWS), ", ".join(FAILS) or "none"))
    sys.exit(1 if FAILS else 0)

main()
