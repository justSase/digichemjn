"""test_regress — Werkstatt CSS, Eilauftrag E22.6 (2026-10-04). Real JupyterLab
under Playwright; read off the page (getComputedStyle, document.getAnimations()).

    python3 tests/regress/css_e22_6.py <notebook.ipynb> [lab|lite] [fresh|old]
    (also a module of tests/regress/run.py: TESTS at the end)

  C22.6  no transition on position while the page is dragged/scrolled: on
         everything in the panel that follows the document (marker, thumb,
         grip, fix point, rail, dock, lane, map, panel host) no transform/
         translate/scale/rotate/top/left/inset with a duration > 0
         (computed), and during 1,5 s scroll per frame, 15 wheel notches and a
         30-step thumb drag no such transition runs.
Gegenprobe v1.62: red in every row (computed: .nbmap-here 0,2 s, .nbgrip
0,15 s); running during the moves: none — the lag of Video 2 is not a CSS
transition (JS, E22.6)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import css_e21 as C

CARRIERS = """['#nbpanel-root', '#nbpanel-root .nbrail', '#nbpanel-root .nbdock', '#nbpanel-root .nbmap',
  '#nbpanel-root .nbmap-inner', '#nbpanel-root .nbmap-cursor', '#nbpanel-root .nbgrip', '#nbpanel-root .nbsb',
  '#nbpanel-root .nbmap-here', '.nbreadfix']"""
POS = "['transform','translate','scale','rotate','top','left','right','bottom','inset','all']"
COMPUTED = """() => { var C = %s, P = %s, bad = [];
  C.forEach(function(s){ var e = document.querySelector(s); if (!e) return; var c = getComputedStyle(e);
    var tp = c.transitionProperty.split(',').map(function(x){ return x.trim(); }), td = c.transitionDuration.split(',');
    tp.forEach(function(p, i){ var d = parseFloat(td[i %% td.length]) || 0;
      if (d > 0 && P.indexOf(p) > -1) bad.push(s + ' ' + p + ' ' + d + 's'); }); });
  return bad; }""" % (CARRIERS, POS)
REC = """() => { window.__c6 = {}; window.__c6n = 0; window.__c6on = true; var C = %s, P = %s;
  (function f(){ if (!window.__c6on) return; window.__c6n++;
    var els = []; C.forEach(function(s){ document.querySelectorAll(s).forEach(function(e){ els.push([s, e]); }); });
    document.getAnimations().forEach(function(a){ var t = a.effect && a.effect.target; if (!t || a.effect.pseudoElement) return;
      var p = a.transitionProperty || ('@' + a.animationName);
      els.forEach(function(se){ if (se[1] === t && (P.indexOf(p) > -1 || p.charAt(0) === '@')) {
        var k = se[0] + ' ' + p; window.__c6[k] = (window.__c6[k] || 0) + 1; } }); });
    requestAnimationFrame(f); })(); }""" % (CARRIERS, POS)
STOP = "() => { window.__c6on = false; return {frames: window.__c6n, running: window.__c6}; }"

def c6(pg, ctx):
    comp = pg.evaluate(COMPUTED)
    pg.evaluate(C.TOP); pg.wait_for_timeout(1500)
    pg.evaluate(REC); pg.evaluate(C.SCROLL, [10, 1500]); pg.wait_for_timeout(1700)
    sc = pg.evaluate(STOP)
    pg.evaluate(C.TOP); pg.wait_for_timeout(1200)
    r = pg.evaluate("() => { var e = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer') || document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook'); var b = e.getBoundingClientRect(); return [b.left + b.width / 2, b.top + b.height / 2]; }")
    pg.mouse.move(r[0], r[1]); pg.evaluate(REC)
    for _ in range(15): pg.mouse.wheel(0, 120); pg.wait_for_timeout(60)
    pg.wait_for_timeout(300); wh = pg.evaluate(STOP)
    pg.evaluate(C.TOP); pg.wait_for_timeout(1200)
    th = pg.evaluate("() => { var c = document.querySelector('#nbpanel-root .nbmap-cursor'); if (!c) return null; var r = c.getBoundingClientRect(); return r.width > 0 ? [r.left + r.width / 2, r.top + r.height / 2] : null; }")
    dr = None
    if th:
        pg.mouse.move(th[0], th[1]); pg.mouse.down(); pg.evaluate(REC)
        for i in range(30): pg.mouse.move(th[0], th[1] + 6 * (i + 1)); pg.wait_for_timeout(40)
        dr = pg.evaluate(STOP); pg.mouse.up()
    pg.evaluate(C.TOP); pg.wait_for_timeout(800)
    got = {"computed": comp, "scroll": sc, "wheel": wh, "drag": dr}
    bad = []
    if comp: bad.append("Lage-Übergang im Stil: " + ", ".join(comp[:6]))
    for k, v in (("scroll", sc), ("wheel", wh), ("drag", dr)):
        if v is None: bad.append("BAD %s: kein Daumen" % k); continue
        if v["frames"] < 3: bad.append("BAD %s: %d Bilder" % (k, v["frames"]))
        if v["running"]: bad.append("%s: läuft %s" % (k, v["running"]))
    return (not bad), ("; ".join(bad) + " " if bad else "") + json.dumps(got, ensure_ascii=False)[:400]

TESTS = [
    ("C22.6 E22.6 keine Lage-Transition beim Ziehen/Scrollen", c6),
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
                if s not in ("minimal", "cyber"): continue
                pg.evaluate(C.SET, [s, t]); pg.wait_for_timeout(800)
                for name, fn in TESTS:
                    ok, d = fn(pg, {"skin": s, "theme": t, "nb": nb})
                    red += not ok
                    print("%-4s %s %s/%s · %s" % ("ok" if ok else "RED", name.split()[0], s, t, d[:300]))
        if errs: red += 1; print("RED Seitenfehler", errs[:3])
        b.close()
    print("css_e22_6: %d rot" % red); sys.exit(1 if red else 0)

if __name__ == "__main__":
    main()
