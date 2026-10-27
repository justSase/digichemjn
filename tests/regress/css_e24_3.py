"""test_regress — Werkstatt CSS, Eilauftrag E24 (2026-10-06; rewritten 2026-10-07,
E24 Stufe 2 Rest). Real JupyterLab under Playwright; read off the page (classes,
getComputedStyle, getBoundingClientRect, pixels), nothing from our stylesheet.

    python3 tests/regress/css_e24_3.py <notebook.ipynb> [lab] [fresh|old]
    (also a module of tests/regress/run.py: TESTS at the end)

  C24.3  the cover needs no inline style: the cover as the reader sees it after
         a run — the last output of the mega-cell, `.nbtitle.nbcover-out`, up
         over the notebook (window.__nbCoverShow, js-E24.3) — looks the same
         when every declaration Python wrote into a `style` attribute is taken
         away and the E14 fallback drawing (`.nbtl-ln`) is removed: every
         remaining element's box ±1 px and its colour, background, border,
         font size/weight, letter spacing, text transform, opacity and display
         equal, and the card and the timeline equal in pixels. Only Python's
         declarations go, only on the elements Python built (style attribute =
         one written in the cover's HTML in the notebook file, or the one the
         script kept when it laid the cover); what the page script set (with
         priority, the layer's own place and size, its forms) stays. Restored afterwards, the
         document put back. (Python can then drop the inline look, E24.3.)
Behauptete bisher (06.10.): the same on the COLD cover in the markdown cell of a
fresh copy opened beside the notebook — that cell is one start line since
py-E24.3, so C24.3 compared the start line with itself stripped (red 12/12 in
the v1.67 gate, "DIV.nbtitle textAlign center→start"). Gegenprobe: see the
chronicle 07.10., Werkstatt CSS (E24 Stufe 2 Rest)."""
import sys, os, json, warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import css_e21 as C
import css_e23 as C23

# ------------------------------------------------------------------ C24.3
import re, itertools
_N = itertools.count()
PROPS = ["color", "backgroundColor", "borderTopWidth", "borderTopStyle", "borderTopColor", "borderLeftWidth",
         "borderRadius", "fontSize", "fontWeight", "fontStyle", "letterSpacing", "textTransform", "opacity",
         "display", "textAlign", "lineHeight", "listStyleType", "boxShadow"]
CV = ".jp-NotebookPanel:not(.lm-mod-hidden) .nbcover-out[data-nbcov]"
SNAP = """(props) => { var P = document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden)'); P = P[P.length - 1];
  var t = P && P.querySelector('.nbcover-out[data-nbcov]'); if (!t) return null;
  t.scrollTop = 0; var lane = t.querySelector('.nbtl-lane'); if (lane) lane.scrollLeft = 0;
  var o0 = t.getBoundingClientRect(), out = [], all = [t].concat([].slice.call(t.querySelectorAll('*')));
  for (var i = 0; i < all.length; i++) { var e = all[i];
    if (e.closest('.nbtl-ln')) continue;
    var r = e.getBoundingClientRect(), cs = getComputedStyle(e),
        o = {k: e.tagName + '.' + String(e.getAttribute('class') || '').split(' ')[0] + (e.getAttribute('class') && /nbtl-row/.test(e.getAttribute('class')) ? '.' + e.getAttribute('class').split(' ')[1] : ''),
             x: r.left - o0.left, y: r.top - o0.top, w: r.width, h: r.height};
    // a display:contents box draws nothing: only what its children inherit counts
    var inh = /^(color|font|letterSpacing|textTransform|textAlign|lineHeight|listStyle)/;
    props.forEach(function(p){ o[p] = (cs.display === 'contents' && !inh.test(p)) ? '-' : cs[p]; }); out.push(o); }
  return out; }"""

# Python's declarations (from the notebook file) → browser spelling; then on the
# cover every inline declaration without priority that Python wrote is taken
# away (the layer's own left/top/width/height are the script's), `.nbtl-ln` out
STRIP = """(py) => { var P = document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden)'); P = P[P.length - 1];
  var c = P && P.querySelector('.nbcover-out[data-nbcov]'); if (!c) return null;
  var tmp = document.createElement('div'), dec = {}, raw = {};
  py.forEach(function(s){ raw[s] = 1; tmp.setAttribute('style', s); for (var i = 0; i < tmp.style.length; i++) { var p = tmp.style[i]; dec[p + ':' + tmp.style.getPropertyValue(p)] = 1; } });
  var saved = [], n = 0, own = {left: 1, top: 1, width: 1, height: 1};
  [c].concat([].slice.call(c.querySelectorAll('[style]'))).forEach(function(e){
    if (e.closest('.nbtl-ln')) return;
    // only elements Python built: their attribute as written, or as the script
    // kept it before laying the cover (__nbSt0) — the forms the script draws
    // (language, content, login) carry inline styles of their own
    if (!raw[e.getAttribute('style')] && !(e.__nbSt0 != null && raw[e.__nbSt0])) return;
    var drop = [];
    for (var i = 0; i < e.style.length; i++) { var p = e.style[i];
      if (e.style.getPropertyPriority(p) || (e === c && own[p])) continue;
      if (dec[p + ':' + e.style.getPropertyValue(p)]) drop.push(p); }
    if (!drop.length) return;
    saved.push([e, e.getAttribute('style')]); drop.forEach(function(p){ e.style.removeProperty(p); n++; }); });
  var ln = [].slice.call(c.querySelectorAll('.nbtl-ln')).filter(function(e){ return !e.parentElement.closest('.nbtl-ln'); })
             .map(function(e){ return [e, e.parentNode, e.nextSibling]; });
  ln.forEach(function(x){ x[0].remove(); });
  window.__c24s = {saved: saved, ln: ln}; return {decl: n, els: saved.length, ln: ln.length}; }"""
UNSTRIP = """() => { var s = window.__c24s; if (!s) return; window.__c24s = null;
  s.ln.reverse().forEach(function(x){ try { x[1].insertBefore(x[0], x[2] && x[2].parentNode === x[1] ? x[2] : null); } catch (e) {} });
  s.saved.forEach(function(x){ x[0].setAttribute('style', x[1]); }); }"""

def _drop_ln(src):
    """remove every element whose class is nbtl-ln (with what is inside it) — for the byte count"""
    out, i = [], 0
    while True:
        m = re.compile(r"<(span|img)\s+class=(['\"])nbtl-ln\2").search(src, i)
        if not m: out.append(src[i:]); break
        out.append(src[i:m.start()])
        if m.group(1) == "img":
            i = src.index(">", m.end()) + 1; continue
        depth, j = 0, m.start()
        for t in re.finditer(r"<(/?)span\b[^>]*>", src[m.start():]):
            depth += -1 if t.group(1) else 1
            if depth == 0: j = m.start() + t.end(); break
        i = j
    return "".join(out)

def _py_styles(pg):
    """the style attributes Python wrote into the cover (notebook file), and their bytes"""
    import ast
    src = C23._front_name(pg)
    path = os.path.join(C23._root(), src or "")
    if not src or not os.path.exists(path): return None, 0
    nb = json.load(open(path, encoding="utf-8"))
    code = __import__("megasrc").expand("".join(max((c for c in nb["cells"] if c.get("cell_type") == "code"), key=lambda c: len("".join(c["source"])))["source"]))
    # E24 Stufe 2 (py-E24.3de): the cover rides in `_nbcv = '…'` (German words put in at run time)
    m = (re.search(r"^_nbcv = (.*nbcover-out.*)$", code, re.M)
         or re.search(r"^display\(IHTML\((.*nbcover-out.*)\)\)$", code, re.M))
    if not m: return None, 0
    h = ast.literal_eval(m.group(1))
    st = re.findall(r"\sstyle=\"([^\"]*)\"", h) + re.findall(r"\sstyle='([^']*)'", h)
    n = sum(len(x) + 9 for x in st) + (len(h.encode()) - len(_drop_ln(h).encode()))
    return sorted(set(st)), n

def _diff(a, b):
    out = []
    if len(a) != len(b): return ["count %d vs %d" % (len(a), len(b))]
    for x, y in zip(a, b):
        if x["k"] != y["k"]: out.append("order %s/%s" % (x["k"], y["k"])); break
        for g in ("x", "y", "w", "h"):
            if abs(x[g] - y[g]) > 1: out.append("%s %s %.1f→%.1f" % (x["k"], g, x[g], y[g])); break
        for p in PROPS:
            if x[p] != y[p]: out.append("%s %s %s→%s" % (x["k"], p, x[p], y[p]))
    return out

# 2026-10-07 (E24 Stufe 2 Rest 2, CSS) — THE LANE AT ITS START, AND THE SCRIPT'S
# ANSWER TO IT. The cover opens its lane on the reader's place (19-rail
# coverLane: the first exercise still open, in the middle); the thumb of the
# lane's scroll bar is placed by the script in the lane's `scroll` event
# (laneSet → --nbtl-tx), and that event comes a frame AFTER `scrollLeft = 0`.
# SNAP set the lane to 0 and read at once: with progress in the browser (the
# "old" storage of the gate: t1 solved → lane at 372 px) the first read caught
# the thumb where it had stood (x 430), the second, 1.3 s later, where it
# belongs (x 225) — red in all old rows (gate 07.10., "DIV.nbtl-sb-th x
# 430.0→225.0"), a stale read, not a style that went missing (the thumb carries
# no style of Python's). Now: lane to 0, two frames, then read — both reads.
REST = """async () => { var c = document.querySelector('%s'); if (!c) return false;
  c.scrollTop = 0; var l = c.querySelector('.nbtl-lane'); if (l) l.scrollLeft = 0;
  await new Promise(function(r){ requestAnimationFrame(function(){ requestAnimationFrame(r); }); }); return true; }""" % CV

FREEZE = """(on) => { document.getAnimations().forEach(function(a){ try { if (on) { a.pause(); a.currentTime = 0; } else a.play(); } catch (e) {} }); }"""

def _pix(pg):
    """the cover as drawn: title card and timeline, two screens (animations held at 0)"""
    from PIL import Image
    import io
    shots = []
    for sel in ('.nbtitle-card', '.nbcover-tl'):
        pg.evaluate("(s) => { var c = document.querySelector('%s'); var e = c && c.querySelector(s); if (e) e.scrollIntoView({block: 'start'}); var l = c && c.querySelector('.nbtl-lane'); if (l) l.scrollLeft = 0; }" % CV, sel)
        pg.mouse.move(5, 450); pg.wait_for_timeout(500)
        pg.evaluate(FREEZE, True); pg.wait_for_timeout(100)
        shots.append(Image.open(io.BytesIO(pg.screenshot())).convert("RGB"))
        pg.evaluate(FREEZE, False)
    return shots

def _pixdiff(A, B):
    n = bad = 0
    for a, b in zip(A, B):
        pa, pb = a.load(), b.load(); w, h = a.size
        for y in range(70, h - 30, 2):           # the notebook, not the tab names and the status bar
            for x in range(300, w - 70, 2):      # nor the file browser and the scroll bar
                n += 1
                if max(abs(i - j) for i, j in zip(pa[x, y], pb[x, y])) > 24: bad += 1
    return bad / max(n, 1)

def c3(pg, ctx):
    py, nbytes = _py_styles(pg)
    if not py: return False, "BAD no cover output (display(IHTML(… nbcover-out …))) in the notebook file"
    if not C23.cover_open(pg): return False, "BAD kein Cover (Ausgabe .nbcover-out, __nbCoverShow)"
    try:
        pg.mouse.move(5, 450); pg.wait_for_timeout(600)
        # Play breathes (scale): the boxes are read with every animation held at 0
        # the lane at its start and the script's answer to that scroll on the page
        # BEFORE the first read (REST); see REST for what this was without it
        pg.evaluate(REST); pg.wait_for_timeout(250)
        pg.evaluate(FREEZE, True); a = pg.evaluate(SNAP, PROPS); pa = _pix(pg)
        st = pg.evaluate(STRIP, py)
        pg.wait_for_timeout(700)
        pg.evaluate(REST); pg.wait_for_timeout(250)
        pg.evaluate(FREEZE, True); b = pg.evaluate(SNAP, PROPS); pb = _pix(pg)
    finally:
        try: pg.evaluate(UNSTRIP); pg.evaluate(FREEZE, False)
        except Exception: pass
        C23.cover_close(pg)
    if not a or not b: return False, "BAD no cover to measure (%s/%s)" % (bool(a), bool(b))
    if not st or not st["decl"]: return False, "BAD nothing taken away (%s) — not a measurement" % st
    d = _diff(a, b)
    px = _pixdiff(pa, pb)
    if px > 0.001: d.append("pixels differ %.2f %%" % (100 * px))
    return (not d), ("%d elements, %d declarations on %d elements + %d drawings taken away (%d B inline look in the file) · "
                     % (len(a), st["decl"], st["els"], st["ln"], nbytes)) + (
                     "; ".join(d[:14]) + (" … (%d)" % len(d) if len(d) > 14 else "") if d else "equal")

TESTS = [
    ("C24.3 E24.3 Cover ohne Inline-Stil gleich", c3),
]

def main():
    nb = sys.argv[1]; C.NB = nb
    C.ENV = sys.argv[2] if len(sys.argv) > 2 else "lab"
    C.STORE = sys.argv[3] if len(sys.argv) > 3 else "fresh"
    only = sys.argv[4].split(",") if len(sys.argv) > 4 and sys.argv[4] else None
    styles = (os.environ.get("C24_STYLES") or "minimal/light").split(",")
    from playwright.sync_api import sync_playwright
    red = 0
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=C.CHROME)
        ctx, pg, errs = C.open_nb(b)
        for st in styles:
            s, t = st.split("/")
            pg.evaluate(C.SET, [s, t]); pg.wait_for_timeout(800)
            for name, fn in TESTS:
                key = name.split()[0]
                if only and key not in only: continue
                try: ok, d = fn(pg, {"skin": s, "theme": t, "nb": nb})
                except Exception as e: ok, d = False, "BAD exception %s" % str(e)[:300]
                red += not ok
                print("%-4s %s %s/%s · %s" % ("ok" if ok else "RED", key, s, t, d[:900])); sys.stdout.flush()
        if errs: red += 1; print("RED Seitenfehler", errs[:3])
        b.close()
    print("css_e24_3: %d rot" % red); sys.exit(1 if red else 0)

if __name__ == "__main__":
    main()
