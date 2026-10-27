"""test_regress — Werkstatt CSS, Eilauftrag E22.5 (2026-10-04). Real JupyterLab
under Playwright; read off the page (pixels), nothing from our CSS.

    python3 tests/regress/css_e22.py <notebook.ipynb> [lab|lite] [fresh|old]
    (also a module of tests/regress/run.py: TESTS at the end)

  C22.5  the trail looks like v1.54: the colour of the style, never white on
         dark (trail and circle chroma ≥ 40/30); soft (no step > 50 % of its
         peak across it) and EQUALLY WIDE (width at 12 px and at 70 % of its
         length within 3 px, ≥ 12 px); densest at the marker (≥ 1,3 × the far
         end); nothing in front of the marker. Read with the trail held at a
         fixed length (--nbm-lag pinned 90 px behind --nbm-y, inline); marks,
         pips, XP pieces and the lane hidden; against the same column at rest.
         Timing (length follows speed, gone ≤ 0,7 s) stays C8 (css_e21 R8).
Gegenprobe v1.62 (chronicle 04.10., Werkstatt CSS, E22): red in all 8 rows
(4 styles × light/dark): hard edge (step 100 %), 11 px = the marker box;
minimal dark also white (trail chroma 5, circle 6)."""
import sys, os, json, colorsys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import css_e21 as C

PIN = """(gap) => { var m = document.querySelector('#nbpanel-root .nbmap-here');
  var y = parseFloat(m.style.top) || 0; m.style.setProperty('--nbm-y', y + 'px');
  m.style.setProperty('--nbm-lag', (y - gap) + 'px'); }"""
UNPIN = "() => { var m = document.querySelector('#nbpanel-root .nbmap-here'); if (m) m.style.removeProperty('--nbm-lag'); }"
GAP = 90
# the lane itself out of the way too: its hard edges are not the trail's
LANE = """(on) => { var id = '__nbc22_lane', s = document.getElementById(id);
  if (!on) { if (s) s.remove(); return; }
  if (!s) { s = document.createElement('style'); s.id = id; document.head.appendChild(s); }
  s.textContent = '#nbpanel-root .nbmap-inner::before{visibility:hidden!important}'; }"""

def _chroma(c):
    return max(c[:3]) - min(c[:3])

def _hue(c):
    h, s, v = colorsys.rgb_to_hsv(*[x / 255.0 for x in c[:3]])
    return h * 360

def c5(pg, ctx):
    dark = ctx.get("theme") == "dark"
    pg.evaluate(C.TOP); pg.wait_for_timeout(1500)
    pg.evaluate(C.BARE, True); pg.evaluate(LANE, True); pg.wait_for_timeout(300)
    try:
        m = pg.evaluate(C.MARK)
        if not m: return False, "BAD kein Marker"
        x0, y0 = int(round(m["x"])) - 30, int(round(m["y"])) - 140
        clip = {"x": x0, "y": y0, "width": 60, "height": 220}
        ref = C.shot(pg, clip)
        pg.evaluate(PIN, GAP); pg.wait_for_timeout(1300)
        im = C.shot(pg, clip)
        m2 = pg.evaluate(C.MARK)
        info = pg.evaluate("() => { var m = document.querySelector('#nbpanel-root .nbmap-here'); var b = m.getBoundingClientRect(); return {top: b.top, h: b.height}; }")
    finally:
        pg.evaluate(UNPIN); pg.evaluate(C.BARE, False); pg.evaluate(LANE, False)
    if abs(m2["y"] - m["y"]) > 1: return False, "BAD Marker bewegt (%s → %s)" % (m["y"], m2["y"])
    cx, cy = 30, int(round(m["y"])) - y0             # marker centre in the clip
    boxtop = int(round(info["top"])) - y0
    diff = lambda xx, yy: max(abs(a - b) for a, b in zip(im.getpixel((xx, yy)), ref.getpixel((xx, yy))))
    def row(yy):
        return [diff(xx, yy) for xx in range(60)]
    near, far = boxtop - 12, boxtop - int(GAP * 0.7)
    rn, rf = row(near), row(far)
    pk_n, pk_f = max(rn), max(rf)
    def width(r):
        p = max(r) or 1
        return sum(1 for v in r if v > 0.25 * p)
    def step(r):
        p = max(r) or 1
        return max(abs(r[i + 1] - r[i]) for i in range(len(r) - 1)) / p
    wn, wf = width(rn), width(rf)
    st = max(step(rn), step(rf))
    behind = max(diff(xx, yy) for xx in range(10, 50) for yy in range(cy + 26, min(cy + 70, 219)))
    tp = im.getpixel((cx, near)); gl = im.getpixel((cx - 10, cy))
    got = {"peak_near": pk_n, "peak_far": pk_f, "w_near": wn, "w_far": wf, "max_step": round(st, 2),
           "behind": behind, "trail_px": tp, "chroma": _chroma(tp), "glow_px": gl, "glow_chroma": _chroma(gl)}
    bad = []
    if pk_n < 40: bad.append("keine Spur am Marker (%d)" % pk_n)
    if dark and _chroma(tp) < 40: bad.append("Spur weiß/grau auf dunkel (Chroma %d)" % _chroma(tp))
    if dark and _chroma(gl) < 30: bad.append("Kreis weiß/grau auf dunkel (Chroma %d)" % _chroma(gl))
    if st > 0.5: bad.append("harte Kante (Sprung %.0f %% der Spitze)" % (st * 100))
    if abs(wn - wf) > 3: bad.append("nicht gleich breit (%d vs %d px)" % (wn, wf))
    if wn < 12: bad.append("schmaler als die Leiste + Rand (%d px)" % wn)
    if not pk_n >= 1.3 * max(pk_f, 1): bad.append("verläuft nicht vom Marker weg (%d vs %d)" % (pk_n, pk_f))
    if behind > 14: bad.append("Spur vor dem Marker (%d)" % behind)
    return (not bad), ("; ".join(bad) + " " if bad else "") + json.dumps(got)

TESTS = [
    ("C22.5 E22.5 Leuchtspur: Stilfarbe, weich, gleich breit, hinter dem Marker", c5),
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
        for s in ("minimal", "cyber", "fairy"):
            for t in ("light", "dark"):
                pg.evaluate(C.SET, [s, t]); pg.wait_for_timeout(800)
                for name, fn in TESTS:
                    ok, d = fn(pg, {"skin": s, "theme": t, "nb": nb})
                    red += not ok
                    print("%-4s %s %s/%s · %s" % ("ok" if ok else "RED", name.split()[0], s, t, d[:300]))
        if errs: red += 1; print("RED Seitenfehler", errs[:3])
        b.close()
    print("css_e22: %d rot" % red); sys.exit(1 if red else 0)

if __name__ == "__main__":
    main()
