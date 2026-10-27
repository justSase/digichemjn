"""test_regress — Werkstatt CSS, Eilauftrag E25 (2026-10-08). Real JupyterLab
under Playwright; read off the page (pixels, getBoundingClientRect), nothing
from our stylesheet.

    python3 tests/regress/css_e25p.py <notebook.ipynb> [lab|lite] [fresh|old]
    (also a module of tests/regress/run.py: TESTS at the end)

  C25.p  the scroll bar keeps ONE width: thumb (.nbmap-cursor and its
         drawing) and track (.nbsb) as wide as with the panel shut at
         lens 100, whatever the panel width (shut, pulled to its far end at
         1920 × 1080, where --nbk > 1) and the lens (60/100/top), ±0,5 px.
Gegenprobe v1.67 (a6d3648c): chronicle 08.10., Werkstatt CSS (E25)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import css_e21 as C
import css_e22_8 as E8

HIDE = """(on) => { var id = '__nbc25_hide', s = document.getElementById(id);
  if (!on) { if (s) s.remove(); return; }
  if (!s) { s = document.createElement('style'); s.id = id; document.head.appendChild(s); }
  s.textContent = '#nbpanel-root .nbmap-here{visibility:hidden!important}'; }"""
GEO = """() => { var m = document.querySelector('#nbpanel-root .nbmap'), h = document.querySelector('#nbpanel-root .nbmap-here');
  if (!m || !h) return null; var r = m.getBoundingClientRect();
  var kz = parseFloat(getComputedStyle(document.getElementById('nbpanel-root')).getPropertyValue('--nbkz')) || 0;
  var k = h.getBoundingClientRect().width / 11;            // marker box = 11 px × lens (11-k4-scale)
  return {l: r.left, r: r.right, t: r.top, b: r.bottom, k: k, ceil: window.__nbZCeil || 200}; }"""
GRIP = "() => { var g = document.querySelector('#nbpanel-root .nbgrip'); if (!g) return null; var r = g.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }"
T = 10

def _pull(pg, dx):
    g = pg.evaluate(GRIP)
    if not g: return False
    x, y = g
    pg.mouse.move(x, y); pg.mouse.down()
    pg.mouse.move(x + dx / 2, y, steps=8); pg.mouse.move(x + dx, y, steps=8); pg.mouse.up()
    pg.wait_for_timeout(1500); pg.mouse.move(5, 450); pg.wait_for_timeout(300)
    return True

SB = """() => { var c = document.querySelector('#nbpanel-root .nbmap-cursor'), s = document.querySelector('#nbpanel-root .nbsb');
  if (!c || !s) return null; var r = c.getBoundingClientRect(), q = s.getBoundingClientRect();
  var kk = parseFloat(getComputedStyle(document.getElementById('nbpanel-root')).getPropertyValue('--nbk')) || 1;
  return {cur: Math.round(r.width * 10) / 10, draw: parseFloat(getComputedStyle(c, '::before').width) || r.width,
          sb: Math.round(q.width * 10) / 10, k: kk, map: Math.round(document.querySelector('#nbpanel-root .nbmap').getBoundingClientRect().width)}; }"""
def cp(pg, ctx):
    bad, got = [], []
    vp = pg.viewport_size
    try:
        pg.set_viewport_size({"width": 1920, "height": 1080}); pg.wait_for_timeout(1500)
        _pull(pg, 900)
        pg.evaluate(E8.ZOOM, 100); pg.wait_for_timeout(1200)
        ref = pg.evaluate(SB)
        if not ref: return False, "BAD keine Scrollleiste"
        g = pg.evaluate(GEO)
        for wide in (0, 1):
            if wide: _pull(pg, -1400)
            for z in (60, 100, g["ceil"] if g else 200):
                pg.evaluate(E8.ZOOM, z); pg.wait_for_timeout(1200)
                d = pg.evaluate(SB)
                got.append("%s/%s: Daumen %.1f (%.1f) Rinne %.1f K %.2f Panel %d" % ("offen" if wide else "zu", z, d["cur"], d["draw"], d["sb"], d["k"], d["map"]))
                for n in ("cur", "draw", "sb"):
                    if abs(d[n] - ref[n]) > 0.5: bad.append("%s Lupe %s: %s %.1f statt %.1f px" % ("offen" if wide else "zu", z, n, d[n], ref[n]))
                if abs(d["cur"] - d["sb"]) > 0.5: bad.append("%s Lupe %s: Daumen %.1f ≠ Rinne %.1f" % ("offen" if wide else "zu", z, d["cur"], d["sb"]))
        if not any("K 1.00" not in x for x in got): bad.append("BAD Panel nie über die Standardbreite gezogen (K = 1)")
    finally:
        pg.evaluate(E8.ZOOM, 100); _pull(pg, 1400)
        pg.set_viewport_size(vp); pg.wait_for_timeout(1500)
    return (not bad), ("; ".join(bad[:4]) + " · " if bad else "") + " | ".join(got)

TESTS = [
    ("C25.p E25.p Scrollleiste konstant dünn", cp),
]

def main():
    nb = sys.argv[1]; C.NB = nb
    C.ENV = sys.argv[2] if len(sys.argv) > 2 else "lab"
    C.STORE = sys.argv[3] if len(sys.argv) > 3 else "fresh"
    only = sys.argv[4].split(",") if len(sys.argv) > 4 else None
    from playwright.sync_api import sync_playwright
    red = 0
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=C.CHROME)
        ctx, pg, errs = C.open_nb(b)
        for s, t in (("minimal", "light"), ("minimal", "dark"), ("cyber", "dark"), ("fairy", "light")):
            pg.evaluate(C.SET, [s, t]); pg.wait_for_timeout(800)
            for name, fn in TESTS:
                if only and name.split()[0] not in only: continue
                ok, d = fn(pg, {"skin": s, "theme": t, "nb": nb})
                red += not ok
                print("%-4s %s %s/%s · %s" % ("ok" if ok else "RED", name.split()[0], s, t, d[:1200]), flush=True)
        if errs: red += 1; print("RED Seitenfehler", errs[:3])
        b.close()
    print("css_e25p: %d rot" % red); sys.exit(1 if red else 0)

if __name__ == "__main__":
    main()
