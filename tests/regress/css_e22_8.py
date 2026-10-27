"""test_regress — Werkstatt CSS, Eilauftrag E22.8 (2026-10-04). Real JupyterLab
under Playwright; getBoundingClientRect only, nothing from our CSS.

    python3 tests/regress/css_e22_8.py <notebook.ipynb> [lab|lite] [fresh|old]
    (also a module of tests/regress/run.py: TESTS at the end)

  C22.8  everything on the main axis: the middle of every block of the
         document — accordions and their pills, boxes, the title block, the
         end card, locked notes, the YOC strip (.jp-Notebook-footer), the
         reader's own cells — is the middle of the title card in the
         document, |Δ| ≤ 1 px; Lupe 60/100/150 %, Title open and folded,
         at the top and at the end of the document.
  C22.8b the same with one cell of one's own (made through the YOC mark:
         hover, click): the cell and the YOC strip under it. Their place is
         set by JS (E21.3c: own cells start right of the corner and the lens;
         footWide: the strip follows the last cell) — red until JS decides.
Gegenprobe v1.62 (chronicle 04.10., Werkstatt CSS, E22): red in every row —
the title card is 10 px left of all 35 other blocks (JupyterLab's 20 px
right padding on the HTML output that holds it)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import css_e21 as C

TOL = 1.0
MEAS = r"""(own) => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var card = P && P.querySelector('.jp-OutputArea .nbtitle-card');
  if (!card) return {err: 'no title card'};
  var cr = card.getBoundingClientRect(); if (cr.width < 10) return {err: 'title card not drawn'};
  var cx = cr.left + cr.width / 2;
  var sel = ['.jupyter-widget-Collapse', '.jupyter-widget-Collapse-header', '.nbbox', '.nbend', '.jp-Notebook-footer',
             '.jp-Cell[class*="nbown-"] > .jp-Cell-inputWrapper', '.nblocked-note', '.nbtitle', '.jp-OutputArea-output > div > *'];
  // C22.8 measures the guided document only (cells of one's own, made by an
  // earlier test of the run, are C22.8b's); C22.8b all of it
  if (!own) sel = sel.filter(function(x){ return x.indexOf('nbown-') < 0; });
  var bad = [], n = 0, seen = new Set();
  sel.forEach(function(s){ P.querySelectorAll(s).forEach(function(e){ if (seen.has(e)) return; seen.add(e);
    if (e.closest('.nbcover') || e.closest('.jp-MarkdownCell')) return;
    var r = e.getBoundingClientRect();
    if (r.width < 60 || r.height < 4) return; if (getComputedStyle(e).visibility === 'hidden') return;
    n++; var d = r.left + r.width / 2 - cx;
    if (Math.abs(d) > %s) bad.push([s + ' ' + String(e.className).split(' ').slice(0, 3).join('.'), Math.round(d * 10) / 10, Math.round(r.width)]); }); });
  return {n: n, bad: bad, card: [Math.round(cr.left), Math.round(cr.width)]}; }""" % TOL
# 2026-10-08 (E25 Rest q, CSS): since js-E25.o the bar is two halves (0…50 =
# 60…100 %, 50…100 = 100 %…ceiling). Behauptete bisher: one even scale
# 60…ceiling — "Lupe 150" set 130 %, "Lupe 100" 83 % (C25.q pair 08.10.).
ZOOM = """(pct) => { var s = document.querySelector('#nbpanel-root input.nbslider.nbzoom-lab'); if (!s) return null;
  var ceil = window.__nbZCeil || 200;
  var v = Math.round(pct <= 100 ? 50 * (pct - 60) / 40 : 50 + 50 * (pct - 100) / Math.max(1, ceil - 100));
  s.value = String(Math.max(0, Math.min(100, v))); s.dispatchEvent(new Event('input', {bubbles: true}));
  var z = null; try { z = localStorage.getItem(window.__nbZKey ? window.__nbZKey() : 'digichemjn.zoom.v1'); } catch (e) {}
  return z; }"""
TITLE = """() => { var h = document.getElementById('nbpanel-root'); var t = h && h.querySelector('.nbmap-node[data-acc="title"]');
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var at = P && P.querySelector('.acc-title.acc-root .jupyter-widget-Collapse-contents');
  var r = t ? t.getBoundingClientRect() : null;
  if (r && r.height < 2 && t.querySelector('.nbsect')) r = t.querySelector('.nbsect').getBoundingClientRect();
  return {xy: r && r.width ? [r.left + r.width / 2, r.top + r.height / 2] : null,
          open: at ? at.getBoundingClientRect().height > 1 : null}; }"""
YOC = """() => { var m = document.querySelector('#nbpanel-root .nbmap-node.cell[data-acc="yoc"]');
  var t = m && (m.querySelector('.nbsect') || m), r = t ? t.getBoundingClientRect() : null;
  return {xy: r && r.width ? [r.left + r.width / 2, r.top + r.height / 2] : null,
          cells: document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell').length}; }"""

TOP0 = """() => { if (window.__nbLandStop) window.__nbLandStop();
  var n = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer'); if (n) { n.scrollTop = 0; n.dispatchEvent(new Event('scroll')); } }"""
def _title(pg, want_open):
    s = pg.evaluate(TITLE)
    if s["open"] == want_open: return True
    pg.keyboard.press("Escape"); pg.evaluate(TOP0); pg.wait_for_timeout(1200)
    s = pg.evaluate(TITLE)
    if not s["xy"]: _title.why = "no xy %s" % s; return False
    for _ in range(2):                    # a first click may only pick the mark
        pg.mouse.click(*s["xy"]); pg.wait_for_timeout(1500); pg.mouse.move(700, 450)
        s2 = pg.evaluate(TITLE); _title.why = "%s -> %s" % (s, s2)
        if s2["open"] == want_open: return True
        s = s2 if s2["xy"] else s
    return False

def _round(pg, tag, rows, own=False):
    m = pg.evaluate(MEAS, bool(own))
    if m.get("err"): rows.append((tag, False, "BAD " + m["err"])); return
    if m["n"] < 3: rows.append((tag, False, "BAD nur %d Blöcke gemessen" % m["n"])); return
    rows.append((tag, not m["bad"], "%d Blöcke, abseits: %s" % (m["n"], json.dumps(m["bad"][:4], ensure_ascii=False))))

def _rounds(pg, rows, own, end):
    for z in (100, 60, 150):
        got = pg.evaluate(ZOOM, z); pg.wait_for_timeout(1500)
        for op in (True, False):
            tag = "Lupe %s Title %s" % (got, "auf" if op else "zu") + (", %d eigene" % own if own else "")
            if not _title(pg, op): rows.append((tag, False, "BAD Title lässt sich nicht %s (%s)" % ("öffnen" if op else "zuklappen", getattr(_title, "why", "")))); continue
            if end:                          # the end of the document: YOC strip and own cell in view
                pg.evaluate("() => { var n = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer'); if (n) n.scrollTop = n.scrollHeight; }")
                pg.wait_for_timeout(900); _round(pg, tag + " (Ende)", rows, own)
            else:
                pg.evaluate(C.TOP); pg.wait_for_timeout(600); _round(pg, tag, rows, own)

def _verdict(rows):
    bad = [r for r in rows if not r[1]]
    return (not bad), " · ".join("%s %s: %s" % ("ok" if r[1] else "RED", r[0], r[2]) for r in (bad or rows))[:600]

def c8(pg, ctx):
    """the guided document, before any cell of one's own: top and end"""
    rows = []
    pg.keyboard.press("Escape"); pg.mouse.move(700, 450); pg.wait_for_timeout(300)
    try:
        _rounds(pg, rows, 0, False); _rounds(pg, rows, 0, True)
    finally:
        _title(pg, True); pg.evaluate(ZOOM, 100); pg.evaluate(C.TOP)
    return _verdict(rows)

def c8own(pg, ctx):
    """with one cell of one's own (made through the YOC mark: hover, click) —
    the cell and the YOC strip under it. Changes the notebook: last."""
    rows = []
    pg.keyboard.press("Escape"); pg.mouse.move(700, 450); pg.wait_for_timeout(300)
    pg.evaluate("() => { var n = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer'); if (n) n.scrollTop = n.scrollHeight; }")
    pg.wait_for_timeout(1500)
    y = pg.evaluate(YOC); own = 0
    if y["xy"]:
        pg.mouse.move(y["xy"][0] - 40, y["xy"][1] - 40); pg.wait_for_timeout(300)
        y = pg.evaluate(YOC); pg.mouse.move(*y["xy"], steps=4); pg.wait_for_timeout(600)
        pg.mouse.click(*y["xy"]); pg.wait_for_timeout(2500); pg.keyboard.press("Escape"); pg.mouse.move(700, 450)
        own = pg.evaluate("() => document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell[class*=\"nbown-\"]').length")
    if not own: return False, "BAD keine eigene Zelle angelegt"
    try:
        _rounds(pg, rows, own, True)
    finally:
        _title(pg, True); pg.evaluate(ZOOM, 100); pg.evaluate(C.TOP)
    return _verdict(rows)

TESTS = [
    ("C22.8 E22.8 alles auf der Hauptachse (Mitte = Titelkarte ±1 px)", c8),
    ("C22.8b E22.8 eigene Zelle + YOC-Streifen auf der Hauptachse (Lage JS: E21.3c, footWide)", c8own),
]

def main():
    nb = sys.argv[1]; C.NB = nb
    C.ENV = sys.argv[2] if len(sys.argv) > 2 else "lab"
    C.STORE = sys.argv[3] if len(sys.argv) > 3 else "fresh"
    from playwright.sync_api import sync_playwright
    red = 0
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=C.CHROME)
        ctx, pg, errs = C.open_nb(b)
        styles = [("minimal", "light"), ("cyber", "dark"), ("cyber", "light"), ("fairy", "dark")]
        for i, (s, t) in enumerate(styles):
            pg.evaluate(C.SET, [s, t]); pg.wait_for_timeout(800)
            for name, fn in TESTS:
                if fn is c8own and i < len(styles) - 1: continue      # changes the notebook: once, last
                ok, d = fn(pg, {"skin": s, "theme": t, "nb": nb})
                red += not ok
                print("%-4s %s %s/%s · %s" % ("ok" if ok else "RED", name.split()[0], s, t, d[:600]))
        if errs: red += 1; print("RED Seitenfehler", errs[:3])
        b.close()
    print("css_e22_8: %d rot" % red); sys.exit(1 if red else 0)

if __name__ == "__main__":
    main()
