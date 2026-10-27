"""E31 · JS — „WIE IN LAB“ IN THE READING WINDOW, G1 IN LAB, W1 (Werkstatt JS, 2026-10-12).
    python3 tests/regress/js_e31.py [<notebook.ipynb>] [--only T2,S1] [--shots DIR] [--no-lab]

The reader's three pictures and two videos of v1.77 (PyCharm, Vorlage; Lite cyber), STOP.md „E31 — GILT JETZT“,
the JS points. The reading window as env_reader/js_e30 build it: the notebook's cell in a real kernel, every
output in an iframe of its own, no widget manager (PyCharm / JCEF), the host page taller than the viewport,
1400 × 900 (T1 also 1000), served over http. The template (`--nb vorlage`) unless a notebook is named.
Rows:
  T2 tools      the tool column floats: no border, no surface, no shadow of its own; every tool a button with its
                own border; the column left of the text column (no overlap)
  S1 scroll bar the window's scroll bar stands in the tool column on the LEFT (.nbrw-sb, left of the text): the
                thumb = track × visible share (±2 px); dragged to the bottom = the end (±2 px); a click high on the
                track goes up there
  P1 panel      the grip (.nbrw-grip) on the panel's left edge (±1 px): dragged 120 px left → the panel 120 px
                wider (±2), kept after reload; dragged far left → never past the window's middle; dragged far
                right → shut (the rail, 44 px × gs); a click on the grip opens it again
  L1 reading ht the grip dragged 60 px down → the reading line 60 px lower (±2), the grip on it (±1); kept
                after reload
  M1 marker     the marker stands on the rail at the reading height (±1 px, rail ±2 px); a chapter brought to the
                line → the marker takes its kind (chap); while the document runs it carries .is-moving, 0.4 s
                after it does not
  Z1 axis       |title card middle − window middle| ≤ 1 px: preview, document with the panel standard, shut, wide
                (400 px) and at controls 130 %
  G1 controls   ⊕ ×3 → --nbgs 1.3 on the window, a tool button 34 → 44.2 px (±1, Lab's 34 px); since E33 B5 the shut panel
                (44), the grip (28) and a mark's dot unchanged (±1 px / ±8 %), the text size and the lens unchanged;
                kept after reload; a double click on the value → 100 %
  T1 preview    the cover's timeline is ONE row: every dot on one line (±1 px), every name one line, two names
                of one side never touch; 1400 and 1000 px wide
  W1 re-run     PyCharm's second run, rebuilt: ALL outputs of the cell in ONE page (class "output", our widgets
                drawn there from the kernel's models, the JS outputs run), the cell run five times in the same
                page: after each run (5 s) exactly one visible reading window with its reading version, no Lab
                panel (#nbpanel-root) over the page
  G1L Lab       (real JupyterLab, skipped with --no-lab) ⚙ „Interface size“ (.nbguicell) present; 130 % →
                --nbgs 1.3 on <html>, --nbk ≥ 1.3, the grip and the marker ×1.3 (±8 %), the document's text
                unchanged; kept after reload (per notebook)
  F1 (CSS)      information only, CSS owns it: in the window A 100 → 150 %, the code field, its output, the ▶
                button and the check button against the running text (ratio ±3 %)
v1.77 (`859cf890`): red T2, S1, P1, L1, M1, G1, T1, W1, G1L; Z1 green at the standard panel (the rows that
need a dragged or scaled panel cannot be reached there). Owner: JS. exit 0 = REGRESS-JS-E31 OK."""
import sys, os, re, json, tempfile, time, shutil, html as _h
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
if __name__ != "__main__":
    raise ImportError("js_e31 is a stand-alone script")
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
LINE = """() => { var w = document.querySelector('.nbrw-win'), R = window.__nbReader; return w.getBoundingClientRect().top + (R && R.line ? R.line() : NaN); }"""
CARD = """() => { var w = document.querySelector('.nbrw'), v = w.getAttribute('data-nbrw-view');
  var c = v === 'cover' ? w.querySelector('.nbrw-cover [class*="nbtitle-card"]') : w.querySelector('.nbrw-doc [class*="nbtitle-card"]');
  if (!c || !c.getClientRects().length) return null; var r = c.getBoundingClientRect(), W = w.getBoundingClientRect();
  return (r.left + r.width / 2) - (W.left + W.width / 2); }"""

ROWS, FAILS = [], []
def row(k, ok, det, count=True):
    ROWS.append((k, ok, det)); print("%-4s %s  %s" % (k, "ok " if ok else ("RED" if count else "red (info)"), det)); sys.stdout.flush()
    if not ok and count: FAILS.append(k)

def frame(pg):
    fi = pg.evaluate(FR)
    if fi < 0: return None, None
    return [f for f in pg.frames if f != pg.main_frame][fi], pg.query_selector_all("iframe.out")[fi]

# ---------------------------------------------------------------- W1: one page, five runs
W1_PAGE = """<!doctype html><meta charset=utf-8><body style='margin:0;padding:8px 16px;background:#fff'>
<div class='cell'><div class='output' id='out'></div></div><div style='height:1600px'></div>
<script>
var OUTS = %s;
function inject(o) {
  var box = document.getElementById('out'), d = document.createElement('div'); d.className = 'output_subarea';
  box.appendChild(d);
  if (o.js != null) { window.element = d; var s = document.createElement('script'); s.textContent = o.js; d.appendChild(s); return; }
  d.innerHTML = o.html;
  [].slice.call(d.querySelectorAll('script')).forEach(function (old) {     // a renderer runs the scripts of an HTML output
    var s = document.createElement('script'); s.textContent = old.textContent; old.parentNode.replaceChild(s, old); });
}
window.RUN = function () {
  var box = document.getElementById('out'); box.innerHTML = '';
  OUTS.forEach(function (o, i) { setTimeout(function () { inject(o); }, 40 * i); });
};
window.RUN();
</script>"""
W1_STATE = """() => { var ws = [].filter.call(document.querySelectorAll('.nbrw'), function (w) { var r = w.getBoundingClientRect(); return r.width > 100 && r.height > 100 && getComputedStyle(w).visibility !== 'hidden'; });
  var p = document.getElementById('nbpanel-root'), pv = !!(p && p.getClientRects().length && getComputedStyle(p).display !== 'none' && p.getBoundingClientRect().width > 0);
  return {wins: ws.length, reading: ws.length ? !!ws[0].querySelector('.nbreading') : false, raw: document.querySelectorAll('.nbreading').length,
          live: document.querySelectorAll('.nb-live').length, panel: pv, acc: document.querySelectorAll('.acc-root').length}; }"""

def w1(b, base, tmpd, outs):
    oo = []
    for o in outs:
        d = o["data"]
        if "application/javascript" in d: oo.append({"js": d["application/javascript"]})
        else:
            h = frame_doc(d, o.get("models"))
            if h: oo.append({"html": h})
    open(os.path.join(tmpd, "w1.html"), "w", encoding="utf-8").write(W1_PAGE % json.dumps(oo).replace("</", "<\\/"))
    ctx = b.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
    pg.goto(base + "w1.html"); st = []
    for k in range(5):
        if k: pg.evaluate("() => window.RUN()")
        pg.wait_for_timeout(5000); st.append(pg.evaluate(W1_STATE))
    if shots: pg.screenshot(path=os.path.join(shots, "E31-js-W1-fuenf-laeufe.png"))
    ctx.close()
    acc = st[0]["acc"]
    ok = all(s["wins"] == 1 and s["reading"] and not s["panel"] for s in st)
    row("W1", ok, "five runs in one page (widgets drawn: %d .acc-root): windows %s · reading version in it %s · Lab panel %s"
        % (acc, [s["wins"] for s in st], [s["reading"] for s in st], [s["panel"] for s in st]))
    if acc == 0: row("W1", False, "the rebuilt page drew no widget of ours — the case is not rebuilt")

# ---------------------------------------------------------------- the window
def window_rows(b, base):
    ctx = b.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
    pg.goto(base + "light.html"); pg.wait_for_timeout(3000)
    fr, fe = frame(pg)
    if not fr: row("W0", False, "no reading window"); return
    S = lambda js, a=None: fr.evaluate(js, a)
    def onscreen():
        pg.evaluate("y => window.scrollTo(0, y)", int(fe.bounding_box()["y"] + pg.evaluate("window.scrollY") - 10)); pg.wait_for_timeout(150)
    def P(x, y): bx = fe.bounding_box(); return bx["x"] + x, bx["y"] + y
    def drag(sel, dx, dy, steps=10):
        bb = S(BOX, sel)
        if not bb: return False
        x, y = P(bb["cx"], bb["cy"]); pg.mouse.move(x, y); pg.mouse.down()
        pg.mouse.move(x + dx * 0.3, y + dy * 0.3, steps=steps); pg.mouse.move(x + dx, y + dy, steps=steps); pg.mouse.up(); pg.wait_for_timeout(350)
        return True
    def reload():
        nonlocal fr, fe, S
        pg.reload(); pg.wait_for_timeout(3000); fr, fe = frame(pg); S = lambda js, a=None: fr.evaluate(js, a)
        S(PLAY); pg.wait_for_timeout(600); onscreen()
    onscreen()
    # T1 on the preview first
    if want("T1"): t1(pg, S, "1400")
    if want("Z1"):
        z0 = S(CARD); row("Z1", z0 is not None and abs(z0) <= 1, "preview: title card %s px from the window's middle" % (None if z0 is None else round(z0, 1)))
    S(PLAY); pg.wait_for_timeout(700); onscreen()
    # ---- T2
    if want("T2"):
        t = S("""() => { var t = document.querySelector('.nbrw-tools'), w = document.querySelector('.nbreading'); if (!t) return null; var s = getComputedStyle(t);
          var bs = ['Top', 'Right', 'Bottom', 'Left'].map(function (k) { return parseFloat(s['border' + k + 'Width']) || 0; });
          var bg = s.backgroundColor, a = /rgba\\([^)]*,\\s*([\\d.]+)\\)/.exec(bg); var alpha = bg === 'transparent' ? 0 : a ? +a[1] : 1;
          var bt = [].filter.call(t.querySelectorAll('.nbrw-btn'), function (b) { return b.getClientRects().length; });
          var own = bt.filter(function (b) { return parseFloat(getComputedStyle(b).borderTopWidth) > 0; }).length;
          var tr = t.getBoundingClientRect(), cr = w.getBoundingClientRect(), txt = [].filter.call(w.querySelectorAll('p'), function (p) { return p.getClientRects().length; })[0];
          var pr = txt ? txt.getBoundingClientRect() : cr;
          return {border: bs, alpha: alpha, shadow: s.boxShadow, btns: bt.length, own: own, right: tr.right, text: pr.left}; }""")
        ok = bool(t) and max(t["border"]) == 0 and t["alpha"] == 0 and t["shadow"] == "none" and t["btns"] >= 8 and t["own"] == t["btns"] and t["right"] <= t["text"]
        row("T2", ok, "tool column: border %s, surface alpha %s, shadow %s, %s/%s buttons with their own border, column right %s ≤ text left %s"
            % (t and t["border"], t and t["alpha"], t and t["shadow"][:20], t and t["own"], t and t["btns"], t and round(t["right"]), t and round(t["text"])))
    # ---- S1
    if want("S1"):
        S("() => { document.querySelector('.nbrw-win').scrollTop = 0; }"); pg.wait_for_timeout(200)
        s = S("""() => { var sb = document.querySelector('.nbrw-sb'), th = document.querySelector('.nbrw-thumb'), w = document.querySelector('.nbrw-win'), rd = document.querySelector('.nbreading');
          if (!sb || !th) return null; var r = sb.getBoundingClientRect(), t = th.getBoundingClientRect(), W = w.getBoundingClientRect();
          var txt = [].filter.call(rd.querySelectorAll('p'), function (p) { return p.getClientRects().length; })[0], tl = txt ? txt.getBoundingClientRect().left : rd.getBoundingClientRect().left;
          return {inside: th.parentElement === sb, x: r.left + r.width / 2, mid: W.left + W.width / 2, text: tl, want: Math.max(24, r.height * w.clientHeight / w.scrollHeight), got: t.height, tools: !!sb.closest('.nbrw-tools')}; }""")
        ok = bool(s) and s["inside"] and s["tools"] and s["x"] < s["text"] and abs(s["want"] - s["got"]) <= 2
        det = "no scroll bar in the tool column" if not s else "bar at x %d (text from %d, window middle %d), thumb %.1f / %.1f px" % (s["x"], s["text"], s["mid"], s["got"], s["want"])
        if s:
            bb = S(BOX, ".nbrw-thumb"); x, y = P(bb["cx"], bb["cy"]); pg.mouse.move(x, y); pg.mouse.down()
            pg.mouse.move(x, y + 300, steps=8); pg.mouse.move(x, y + 1200, steps=8); pg.mouse.up(); pg.wait_for_timeout(250)
            e = S("() => { var w = document.querySelector('.nbrw-win'); return w.scrollHeight - w.clientHeight - w.scrollTop; }")
            sbb = S(BOX, ".nbrw-sb"); pg.mouse.click(*P(sbb["cx"], sbb["t"] + 6)); pg.wait_for_timeout(250)
            top = S("() => document.querySelector('.nbrw-win').scrollTop"), S("() => { var w = document.querySelector('.nbrw-win'); return w.scrollHeight - w.clientHeight; }")
            det += " · dragged to the bottom: %.1f px short · click high on the track: %d / %d px" % (e, top[0], top[1])
            ok = ok and e <= 2 and top[0] <= 0.05 * top[1]
        row("S1", ok, det)
    # ---- P1 / L1 / M1
    if want("P1"):
        g = S(BOX, ".nbrw-grip"); p0 = S(BOX, ".nbrw-panel")
        if not g: row("P1", False, "no grip (.nbrw-grip)")
        else:
            edge = g["cx"] - p0["l"]
            drag(".nbrw-grip", -120, 0); p1 = S(BOX, ".nbrw-panel")
            reload(); p2 = S(BOX, ".nbrw-panel")
            drag(".nbrw-grip", -2000, 0); p3 = S(BOX, ".nbrw-panel"); W = S(BOX, ".nbrw")
            drag(".nbrw-grip", 2000, 0); p4 = S(BOX, ".nbrw-panel"); st4 = S("() => document.querySelector('.nbrw').getAttribute('data-nbrw-panel')")
            gb = S(BOX, ".nbrw-grip"); pg.mouse.click(*P(gb["cx"], gb["cy"])); pg.wait_for_timeout(400)
            st5 = S("() => document.querySelector('.nbrw').getAttribute('data-nbrw-panel')"); p5 = S(BOX, ".nbrw-panel")
            ok = abs(edge) <= 1 and abs(p1["w"] - p0["w"] - 120) <= 2 and abs(p2["w"] - p1["w"]) <= 1 and p3["l"] >= W["cx"] - 1 \
                and st4 == "closed" and abs(p4["w"] - 44) <= 1 and st5 == "open" and p5["w"] > 100
            row("P1", ok, "grip %.1f px from the panel's edge · 120 px left: %d → %d px · after reload %d · far left: panel left %d, middle %d · far right: %s %d px · click: %s %d px"
                % (edge, p0["w"], p1["w"], p2["w"], p3["l"], W["cx"], st4, p4["w"], st5, p5["w"]))
            S("() => window.__nbReader.pw(168)"); pg.wait_for_timeout(300)
    if want("L1"):
        g = S(BOX, ".nbrw-grip")
        if not g: row("L1", False, "no grip")
        else:
            l0 = S(LINE); drag(".nbrw-grip", 0, 60); l1 = S(LINE); g1 = S(BOX, ".nbrw-grip")
            reload(); l2 = S(LINE)
            ok = abs(l1 - l0 - 60) <= 2 and abs(g1["cy"] - l1) <= 1 and abs(l2 - l1) <= 1
            row("L1", ok, "grip dragged 60 px down: line %.1f → %.1f (grip %.1f) · after reload %.1f" % (l0, l1, g1["cy"], l2))
            drag(".nbrw-grip", 0, -60)
    if want("M1"):
        m = S("""() => { var m = document.querySelector('.nbrw-marker'), t = document.querySelector('.nbrw-track'); if (!m || !m.getClientRects().length) return null;
          var r = m.getBoundingClientRect(), tr = t.getBoundingClientRect(), bl = parseFloat(getComputedStyle(t).borderLeftWidth) || 0;
          return {cy: r.top + r.height / 2, cx: r.left + r.width / 2, rail: tr.left + bl / 2}; }""")
        if not m: row("M1", False, "no marker (.nbrw-marker) on the rail")
        else:
            ln = S(LINE)
            S("() => document.querySelectorAll('ol.nbread-toc a')[0].click()"); pg.wait_for_timeout(700)
            k = S("() => document.querySelector('.nbrw-marker').getAttribute('data-kind')")
            bx = S(BOX, ".nbrw-win"); pg.mouse.move(*P(bx["cx"], bx["cy"]))
            pg.mouse.wheel(0, 120); pg.wait_for_timeout(40); mv1 = S("() => document.querySelector('.nbrw-marker').classList.contains('is-moving')")
            pg.wait_for_timeout(450); mv2 = S("() => document.querySelector('.nbrw-marker').classList.contains('is-moving')")
            ok = abs(m["cy"] - ln) <= 1 and abs(m["cx"] - m["rail"]) <= 2 and k == "chap" and mv1 and not mv2
            row("M1", ok, "marker %.1f px from the line, %.1f px from the rail · chapter 1 on the line → %s · running %s, 0.45 s later %s"
                % (m["cy"] - ln, m["cx"] - m["rail"], k, mv1, mv2))
    # ---- Z1 + G1
    if want("Z1"):
        zz = []
        for what, js in (("standard", "() => window.__nbReader.pw(168)"), ("shut", "() => { if (document.querySelector('.nbrw').getAttribute('data-nbrw-panel') === 'open') document.querySelector('.nbrw-btn[data-act=panel]').click(); }"),
                         ("wide 400", "() => { if (!window.__nbReader.pw) throw 'no pw'; window.__nbReader.pw(400); }"), ("controls 130 %", "() => { if (!window.__nbReader.gs) throw 'no gs'; window.__nbReader.gs(130); }")):
            try: S(js); pg.wait_for_timeout(400); zz.append((what, S(CARD)))
            except Exception as e: zz.append((what, "n/a"))
        S("() => { try { window.__nbReader.gs(100); window.__nbReader.pw(168); } catch (e) {} }"); pg.wait_for_timeout(300)
        ok = all(isinstance(v, (int, float)) and abs(v) <= 1 for _, v in zz)
        row("Z1", ok, "title card − window middle: " + " · ".join("%s %s" % (w, round(v, 1) if isinstance(v, (int, float)) else v) for w, v in zz))
    if want("G1"):
        S("() => { document.querySelectorAll('ol.nbread-toc a')[0].click(); }"); pg.wait_for_timeout(500)
        def meas():
            return S("""() => { var q = function (s) { var e = document.querySelector(s); return e && e.getClientRects().length ? e.getBoundingClientRect() : null; };
              var b = q('.nbrw-tools .nbrw-btn[data-act="a+"]'), g = q('.nbrw-grip'), m = [].filter.call(document.querySelectorAll('.nbrw-mark[data-kind=chap]'), function (x) { return x.getClientRects().length && getComputedStyle(x).display !== 'none'; })[0];
              var p = [].filter.call(document.querySelectorAll('.nbreading p'), function (x) { return x.getClientRects().length; })[0];
              return {gs: getComputedStyle(document.querySelector('.nbrw')).getPropertyValue('--nbgs').trim(), btn: b && b.height, grip: g && g.width,
                      mark: m ? m.getBoundingClientRect().height : null, text: p ? parseFloat(getComputedStyle(p).fontSize) : null, zoom: window.__nbReader.zoom(),
                      val: (document.querySelector('.nbgs-val') || {}).textContent}; }""")
        g0 = meas()
        for _ in range(3):
            try: fr.click(".nbrw-btn[data-act=\"g+\"]", timeout=2000)
            except Exception: break
            pg.wait_for_timeout(250)
        g1 = meas()
        S("() => { if (document.querySelector('.nbrw').getAttribute('data-nbrw-panel') === 'open') document.querySelector('.nbrw-btn[data-act=panel]').click(); }"); pg.wait_for_timeout(350)
        shut = S(BOX, ".nbrw-panel")
        reload(); g2 = meas()
        try: fr.dblclick(".nbgs-val", timeout=2000); pg.wait_for_timeout(300)
        except Exception: pass
        g3 = meas()
        S("() => { if (document.querySelector('.nbrw').getAttribute('data-nbrw-panel') === 'closed') document.querySelector('.nbrw-btn[data-act=panel]').click(); }"); pg.wait_for_timeout(300)
        # E33 B5 (Werkstatt JS, 13.10.): the controls' size acts on the TOOL COLUMN only — grip, marks and the shut panel
        # keep their size (they follow the panel's width and the lens, js_e33 B5). Behauptete bisher: grip 28 → 36.4,
        # a mark ×1.3, the shut panel 44 → 57.2 at 130 %
        ok = (g1["gs"] == "1.3" and g1["btn"] and abs(g1["btn"] - 34 * 1.3) <= 1 and g1["grip"] and abs(g1["grip"] - 28) <= 1
              and g0["mark"] and g1["mark"] and abs(g1["mark"] / g0["mark"] - 1) <= 0.08 and shut and abs(shut["w"] - 44) <= 1
              and g1["text"] and abs(g1["text"] - g0["text"]) <= 0.05 and g1["zoom"] == g0["zoom"] and g2["gs"] == "1.3" and g3["gs"] == "1")
        row("G1", ok, "⊕×3: --nbgs %s, button %s → %s px, grip %s → %s, mark %s → %s, shut panel %s, text %s → %s px, lens %s → %s · reload %s · double click %s"
            % (g1["gs"], g0["btn"], g1["btn"] and round(g1["btn"], 1), g0["grip"], g1["grip"] and round(g1["grip"], 1), g0["mark"] and round(g0["mark"], 1),
               g1["mark"] and round(g1["mark"], 1), shut and round(shut["w"], 1), g0["text"], g1["text"], g0["zoom"], g1["zoom"], g2["gs"], g3["gs"]))
    # ---- F1 (CSS, info)
    if want("F1"):
        def kinds():
            return S("""() => { var f = function (s) { var e = [].filter.call(document.querySelectorAll(s), function (x) { return x.getClientRects().length || x.closest('details'); })[0]; return e ? parseFloat(getComputedStyle(e).fontSize) : null; };
              return {text: f('.nbreading p'), code: f('.nbrw-code .nbrw-ta, .nbrw-code textarea'), out: f('.nbrw-out'), run: f('.nbrw-run'), check: f('.nbrw-check')}; }""")
        S("() => window.__nbReader.fs(100)"); pg.wait_for_timeout(300); k0 = kinds()
        S("() => window.__nbReader.fs(150)"); pg.wait_for_timeout(300); k1 = kinds()
        S("() => window.__nbReader.fs(100)"); pg.wait_for_timeout(200)
        bad = []
        for k in ("code", "out", "run", "check"):
            if k0.get(k) and k1.get(k) and k0["text"] and k1["text"]:
                r = (k1[k] / k1["text"]) / (k0[k] / k0["text"])
                if abs(r - 1) > 0.03: bad.append("%s %.2f" % (k, r))
        row("F1", not bad, "window A 100 → 150 %%: text %s → %s px; ratio drift %s" % (k0["text"], k1["text"], bad or "none"), count=False)
    if shots:
        S("() => { document.querySelectorAll('ol.nbread-toc a')[0].click(); }"); pg.wait_for_timeout(600); onscreen()
        pg.screenshot(path=os.path.join(shots, "E31-js-fenster-dokument-hell.png"), clip={"x": 0, "y": 0, "width": 1400, "height": 900})
        S("() => window.__nbReader.gs(130)"); S("() => window.__nbReader.pw(380)"); pg.wait_for_timeout(500)
        pg.screenshot(path=os.path.join(shots, "E31-js-fenster-gui130-breit-hell.png"), clip={"x": 0, "y": 0, "width": 1400, "height": 900})
        S("() => { window.__nbReader.gs(100); window.__nbReader.pw(168); }")
    if errs: row("ERR", False, "page errors: %s" % errs[:2])
    ctx.close()
    # T1 at 1000 px
    if want("T1"):
        ctx = b.new_context(viewport={"width": 1000, "height": 900}); pg = ctx.new_page(); pg.goto(base + "light.html"); pg.wait_for_timeout(3000)
        fr, fe = frame(pg); t1(pg, lambda js, a=None: fr.evaluate(js, a), "1000"); ctx.close()

def t1(pg, S, tag):
    r = S("""() => { var tl = document.querySelector('.nbrw-cover .nbrw-cv-tl'); if (!tl) return null;
      var ds = [].filter.call(tl.querySelectorAll('.nbrw-cv-dot'), function (d) { return d.getClientRects().length; });
      var ys = ds.map(function (d) { var c = getComputedStyle(d, '::before'), r = d.getBoundingClientRect(); return r.top + (r.height ? r.height / 2 : 0); });
      var labs = [].filter.call(tl.querySelectorAll('.nbrw-cv-lab'), function (l) { return l.getClientRects().length; }).map(function (l) {
        var r = l.getBoundingClientRect(), s = getComputedStyle(l), lh = parseFloat(s.lineHeight) || parseFloat(s.fontSize) * 1.25;
        var d = l.closest('.nbrw-cv-dot'), dr = d.getBoundingClientRect();
        return {l: r.left, r: r.right, top: r.top, h: r.height, lh: lh, up: r.bottom <= dr.top + dr.height / 2 + 1, t: l.textContent}; });
      var two = labs.filter(function (x) { return x.h > x.lh * 1.5; }).map(function (x) { return x.t; });
      var touch = [];
      [true, false].forEach(function (u) { var s = labs.filter(function (x) { return x.up === u; }).sort(function (a, b) { return a.l - b.l; });
        for (var i = 1; i < s.length; i++) if (s[i].l < s[i - 1].r + 2) touch.push(s[i - 1].t + ' | ' + s[i].t); });
      var rows = {}; ds.forEach(function (d, i) { rows[Math.round(ys[i])] = 1; });
      var sc = tl.querySelector('.nbrw-cv-scroll') || tl, out = labs.filter(function (x) { var b = sc.getBoundingClientRect(); return x.l < b.left - 1 && sc.scrollWidth <= sc.clientWidth; }).length;
      return {dots: ds.length, ys: Object.keys(rows).length, spread: Math.max.apply(null, ys) - Math.min.apply(null, ys), labs: labs.length, two: two, touch: touch, out: out}; }""")
    if not r: row("T1", False, "%s: no timeline on the preview" % tag); return
    ok = r["dots"] >= 5 and r["spread"] <= 1 and not r["two"] and not r["touch"] and not r["out"]
    row("T1", ok, "%s: %d dots, rows apart %.1f px, %d names, on two lines %s, touching %s, cut %d" % (tag, r["dots"], r["spread"], r["labs"], r["two"][:2], r["touch"][:2], r["out"]))

# ---------------------------------------------------------------- G1 in Lab
def lab_rows(src):
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
        name = "e31_%d_%s" % (int(time.time() * 1000) % 1000000, os.path.basename(src)); shutil.copy(src, os.path.join(ROOT, name))
        pg.goto(BASE + "/lab/tree/" + name + "?reset")
        pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000); pg.wait_for_timeout(1500)
        R.run_front(pg, nid); pg.wait_for_timeout(1500)
        M = """() => { var h = document.getElementById('nbpanel-root'), q = function (s) { var e = h && h.querySelector(s); return e && e.getClientRects().length ? e.getBoundingClientRect() : null; };
          var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), p = [].filter.call(P.querySelectorAll('.jp-OutputArea p, .jp-OutputArea .nbbox-concept'), function (x) { return x.getClientRects().length && x.textContent.trim().length > 20; })[0];
          // Hauptwerkstatt 12.10. (E31 merge): the template's Lab document has no visible <p> (its text lives in HTML widgets) —
          // the concept box as the text probe, as css_e31 does (behauptete bisher: a visible <p> > 20 characters in the output area)
          var cs = getComputedStyle(document.documentElement);
          return {fn: typeof window.__nbGuiSize, gs: cs.getPropertyValue('--nbgs').trim(), nbk: parseFloat(cs.getPropertyValue('--nbk')) || null, cell: !!(h && h.querySelector('.nbguicell .nbgui-slot .nbgs-val')),
                  grip: q('.nbgrip') && q('.nbgrip').width, here: q('.nbmap-here') && q('.nbmap-here').height, text: p ? parseFloat(getComputedStyle(p).fontSize) : null}; }"""
        a = pg.evaluate(M)
        if a["fn"] != "function": row("G1L", False, "Lab: no control of the controls' size (window.__nbGuiSize %s, ⚙ cell %s)" % (a["fn"], a["cell"])); return
        pg.evaluate("() => window.__nbGuiSize(130)"); pg.wait_for_timeout(2500); c = pg.evaluate(M)
        pg.reload(); pg.wait_for_selector(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell", state="attached", timeout=120000); pg.wait_for_timeout(1500)
        R.run_front(pg, nid); pg.wait_for_timeout(1500); d = pg.evaluate(M)
        if shots: pg.screenshot(path=os.path.join(shots, "E31-js-G1-lab-130-hell.png"))
        pg.evaluate("() => window.__nbGuiSize(100)"); pg.wait_for_timeout(1500); e = pg.evaluate(M)
        r = lambda x, y: (y / x) if (x and y) else 0
        ok = (a["cell"] and c["gs"] == "1.3" and (c["nbk"] or 0) >= 1.29 and abs(r(a["grip"], c["grip"]) - 1.3) <= 0.08 and abs(r(a["here"], c["here"]) - 1.3) <= 0.1
              and a["text"] and c["text"] == a["text"] and d["gs"] == "1.3" and e["gs"] == "1")
        row("G1L", ok, "Lab ⚙ cell %s · 130 %%: --nbgs %s, --nbk %s, grip %s → %s px, marker %s → %s px, text %s → %s px · after reload %s · back %s"
            % (a["cell"], c["gs"], c["nbk"], a["grip"], c["grip"], a["here"], c["here"], a["text"], c["text"], d["gs"], e["gs"]))
        ctx.close()
    finally:
        b.close(); p.stop()

def main():
    import nbpick
    src = nbpick.from_argv(sys.argv)
    print("notebook:", src)
    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    tmpd = tempfile.mkdtemp(prefix="jse31_"); srv = serve(tmpd)
    base = "http://127.0.0.1:%d/" % srv.server_address[1]
    outs, errs, chapters = run_cell(src, {})
    if errs: row("RUN", False, "the run raised: %s" % errs[:1])
    h = host_page(outs, False).replace("</iframe><script>", "</iframe><div style='height:2400px'></div><script>", 1)
    open(os.path.join(tmpd, "light.html"), "w", encoding="utf-8").write(h)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        try:
            window_rows(b, base)
            if want("W1"): w1(b, base, tmpd, outs)
        finally:
            b.close()
    if want("G1L") and not NOLAB: lab_rows(src)
    print("\n".join("%s %s %s" % (k, "ok" if o else "RED", d) for k, o, d in ROWS) if "--json" in args else "")
    print("REGRESS-JS-E31 %s (%d rows, red: %s)" % ("OK" if not FAILS else "FAIL", len(ROWS), ", ".join(FAILS) or "none"))
    sys.exit(1 if FAILS else 0)

main()
