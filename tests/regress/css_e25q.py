"""test_regress — Werkstatt CSS, Eilauftrag E25 (2026-10-08). Real JupyterLab
under Playwright; read off the page (pixels, getBoundingClientRect), nothing
from our stylesheet.

    python3 tests/regress/css_e25q.py <notebook.ipynb> [lab|lite] [fresh|old]
    (also a module of tests/regress/run.py: TESTS at the end)

  C25.q  marker + light + trail are ONE round object, never clipped (Video
         Nutzer 08.10.: the light a vertical band, cut hard left/right).
         Panel shut and pulled out, lens 60/100/150/top, the page's theme:
         the light (marker shown − marker hidden, marks/pips/XP pieces and the
         lane out, so the background is even)
         is as wide as it is tall (±2 px); its box stays inside the rail's
         clip (≥ 1 px from .nbmap's left and right edge, i.e. it fades out
         before any edge cuts it); there is light just outside the XP bar
         on both sides (bar edge + 2 px × lens); with the trail held at
         90 px (--nbm-lag pinned, as C22.5) the centre column is lit
         without a gap from the marker up the trail (one object, no pieces)
         and the trail is never wider than the light.
         Third, the NARROW rail (E25 Rest q 2, Tor 08.10.): pulled shut all
         the way or in a "pair" row the shut rail measured only 15–17 px at
         lens 60 (21 px at 100, 29 px at 150; JS: WMIN from markFloor) — in
         the gate C25.q ran after C25.p and was red only then. Not left to
         the order of the tests: the widths the gate measured are pinned
         (--nbvert-w / --nbvert-axis on :root, !important over the inline
         values JS sets) and the same checks run there.
Gegenprobe v1.67 (a6d3648c): chronicle 08.10., Werkstatt CSS (E25).
Gegenprobe v1.68 (517f893f): chronicle 08.10., Werkstatt CSS (E25 Rest q).
Gegenprobe css-E25.q-517f893f (narrow part): chronicle 08.10., CSS (E25 Rest q 2)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import css_e21 as C
import css_e22 as C22
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
NARROW = """(a) => { var s = document.getElementById('__nbc25_narrow'); if (!a) { if (s) s.remove(); return; }
  if (!s) { s = document.createElement('style'); s.id = '__nbc25_narrow'; document.head.appendChild(s); }
  s.textContent = 'html:root{--nbvert-w:' + a[0] + 'px!important;--nbvert-axis:' + a[1] + 'px!important}'; }"""
# (lens, rail width JS set) as measured in the gate 08.10. (pair / pulled shut)
NARROW_W = ((60, 15), (60, 17), (100, 21), (150, 29))

def _pull(pg, dx):
    g = pg.evaluate(GRIP)
    if not g: return False
    x, y = g
    pg.mouse.move(x, y); pg.mouse.down()
    pg.mouse.move(x + dx / 2, y, steps=8); pg.mouse.move(x + dx, y, steps=8); pg.mouse.up()
    pg.wait_for_timeout(1500); pg.mouse.move(5, 450); pg.wait_for_timeout(300)
    return True

def _diff(a, b, x, y):
    return max(abs(p - q) for p, q in zip(a.getpixel((x, y)), b.getpixel((x, y))))

def _one(pg, z):
    pg.evaluate(E8.ZOOM, z); pg.wait_for_timeout(1200)
    pg.evaluate(C.TOP); pg.wait_for_timeout(1500)
    m = pg.evaluate(C.MARK); g = pg.evaluate(GEO)
    if not m or not g: return None, "BAD kein Marker"
    R = 70
    x0, y0 = int(round(m["x"])) - R, int(round(m["y"])) - 150
    vw = pg.viewport_size["width"]
    clip = {"x": max(0, x0), "y": max(0, y0), "width": min(2 * R, vw - max(0, x0)), "height": 220}
    x0, y0 = clip["x"], clip["y"]
    pg.evaluate(C.BARE, True); pg.evaluate(C22.LANE, True); pg.wait_for_timeout(250)
    try:
        on = C.shot(pg, clip)
        pg.evaluate(HIDE, True); pg.wait_for_timeout(250)
        off = C.shot(pg, clip)
        pg.evaluate(HIDE, False)
        pg.evaluate(C22.PIN, 90); pg.wait_for_timeout(1300)
        mv = C.shot(pg, clip)
    finally:
        pg.evaluate(C22.UNPIN); pg.evaluate(HIDE, False); pg.evaluate(C.BARE, False); pg.evaluate(C22.LANE, False)
    cx, cy = int(round(m["x"])) - x0, int(round(m["y"])) - y0
    W, H = on.size
    lit = [(x, y) for y in range(H) for x in range(W) if _diff(on, off, x, y) > T]
    if not lit: return None, "BAD kein Leuchten (Lupe %s)" % z
    # the light alone: rows within the glow, not the 3 px stroke's white edges
    xs = [x for x, y in lit]; ys = [y for x, y in lit]
    bw = max(xs) - min(xs) + 1; bh = max(ys) - min(ys) + 1
    k = g["k"]; half = 4 * k + 2 * k
    lo = _diff(on, off, max(0, int(round(cx - half))), cy); hi = _diff(on, off, min(W - 1, int(round(cx + half))), cy)
    gl, gr = min(xs) + x0, max(xs) + x0
    # moving: centre column from the marker upwards, lit without a gap
    # read beside the stroke (± 6 px × lens: inside the trail, outside the
    # 8 px stroke and its light-theme white edges, which equal a white panel)
    xl, xr = max(0, int(round(cx - 6 * k))), min(W - 1, int(round(cx + 6 * k)))
    col = [max(_diff(mv, off, xl, y), _diff(mv, off, xr, y)) for y in range(H)]
    up = [y for y in range(cy, -1, -1)]
    run, gap = 0, False
    for y in up:
        if col[y] > T:
            if gap: break
            run += 1
        else:
            gap = True
    later = any(col[y] > T for y in up[run + 1:] if y < cy - run - 2)
    # trail width (rows above the light) never wider than the light
    tw = 0
    for y in range(max(0, min(ys) - 40), max(0, min(ys) - 6)):
        r = [x for x in range(W) if _diff(mv, off, x, y) > T]
        if r: tw = max(tw, max(r) - min(r) + 1)
    got = {"z": z, "box": [bw, bh], "glow_x": [round(gl - g["l"], 1), round(g["r"] - gr, 1)],
           "outside": [lo, hi], "trail_run": run, "trail_gap_then_lit": later, "trail_w": tw}
    bad = []
    if abs(bw - bh) > 2: bad.append("nicht rund %d×%d px" % (bw, bh))
    if gl - g["l"] < 1 or g["r"] - gr < 1: bad.append("an der Leistenkante abgeschnitten (%.1f / %.1f px)" % (gl - g["l"], g["r"] - gr))
    if lo <= T or hi <= T: bad.append("kein Leuchten neben der XP-Leiste (%d / %d)" % (lo, hi))
    if run < 30: bad.append("Spur nicht am Leuchten (%d px)" % run)
    if later: bad.append("Spur zerfällt (Lücke, dann wieder Licht)")
    if tw > bw: bad.append("Spur breiter als das Leuchten (%d > %d)" % (tw, bw))
    return bad, got

def cq(pg, ctx):
    bad, got = [], []
    g = pg.evaluate(GEO)
    if not g: return False, "BAD keine Leiste"
    zs = (60, 100, 150, g["ceil"])
    try:
        for wide in (0, 1):
            if wide and not _pull(pg, -260): return False, "BAD kein Griff"
            for z in zs:
                b, d = _one(pg, z)
                if b is None: return False, d
                got.append(("w" if wide else "s") + json.dumps(d))
                bad += ["%s Lupe %s: %s" % ("offen" if wide else "zu", z, x) for x in b]
        _pull(pg, 700)
        for z, w in NARROW_W:
            pg.evaluate(E8.ZOOM, z); pg.wait_for_timeout(800)
            pg.evaluate(NARROW, [w, (w - 1) / 2.0]); pg.wait_for_timeout(800)
            b, d = _one(pg, z)
            pg.evaluate(NARROW, None)
            if b is None: return False, d
            got.append("n%d%s" % (w, json.dumps(d)))
            bad += ["schmal %d px Lupe %s: %s" % (w, z, x) for x in b]
    finally:
        pg.evaluate(NARROW, None); pg.evaluate(E8.ZOOM, 100); _pull(pg, 700)
    return (not bad), ("; ".join(bad[:4]) + " · " if bad else "") + " ".join(got)[:1400]

TESTS = [
    ("C25.q E25.q Marker + Leuchten + Spur ein Objekt: rund, nicht geclippt", cq),
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
    print("css_e25q: %d rot" % red); sys.exit(1 if red else 0)

if __name__ == "__main__":
    main()
