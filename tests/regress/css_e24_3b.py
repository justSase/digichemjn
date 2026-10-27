"""test_regress — Werkstatt CSS, E24 Stufe 2 Rest (2026-10-07). Real JupyterLab
under Playwright; read off the page (getComputedStyle), nothing from our sources.

    python3 tests/regress/css_e24_3b.py <notebook.ipynb> [lab] [fresh|old]
    (also a module of tests/regress/run.py: TESTS at the end)

  C24.3b the cover over the notebook belongs to the stylesheet (hint from the
         js-E24.3 run): with the output cover up (`.nbcover-out[data-nbcov]`,
         brought back by window.__nbCoverShow) and the script's inline
         `display` taken off the cover and off its inner `.nbcover`, and its
         inline `background` taken off the cover, both still show (display
         block, inner box > 0 px high) and the cover's ground is the
         notebook's ground in this light/dark (`--jp-layout-color0`, not
         transparent). The inline values are put back, the document too.
Gegenprobe (Teststand without the CSS rule): red — the inner `.nbcover` is
display:none (06-marks `.nbrail-own .nbcover`), the cover transparent; see the
chronicle 07.10., Werkstatt CSS."""
import sys, os, json, warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import css_e21 as C
import css_e23 as C23

FREE = """() => { var P = document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden)'); P = P[P.length - 1];
  var c = P && P.querySelector('.nbcover-out[data-nbcov]'), inn = c && c.querySelector('.nbcover');
  if (!c || !inn) return null;
  var keep = [[c, 'display'], [c, 'background'], [c, 'background-color'], [inn, 'display']].map(function(x){
    return [x[0], x[1], x[0].style.getPropertyValue(x[1]), x[0].style.getPropertyPriority(x[1])]; });
  keep.forEach(function(x){ x[0].style.removeProperty(x[1]); });
  var pr = document.createElement('div'); pr.style.background = 'var(--jp-layout-color0, #fff)'; c.parentNode.appendChild(pr);
  var want = getComputedStyle(pr).backgroundColor; pr.remove();
  var cs = getComputedStyle(c), ci = getComputedStyle(inn), r = inn.getBoundingClientRect();
  var out = {disp: cs.display, inner: ci.display, innerH: Math.round(r.height), bg: cs.backgroundColor, want: want};
  keep.forEach(function(x){ if (x[2]) x[0].style.setProperty(x[1], x[2], x[3]); });
  return out; }"""

def c3b(pg, ctx):
    if not C23.cover_open(pg): return False, "BAD kein Cover (Ausgabe .nbcover-out, __nbCoverShow)"
    try:
        pg.wait_for_timeout(400)
        d = pg.evaluate(FREE)
    finally:
        C23.cover_close(pg)
    if not d: return False, "BAD no cover / no inner .nbcover"
    bad = []
    if d["disp"] != "block": bad.append("cover display %s" % d["disp"])
    if d["inner"] != "block" or d["innerH"] < 50: bad.append("inner .nbcover display %s, %d px" % (d["inner"], d["innerH"]))
    tr = d["bg"] in ("transparent", "rgba(0, 0, 0, 0)")
    if tr or d["bg"] != d["want"]: bad.append("ground %s, want %s" % (d["bg"], d["want"]))
    return (not bad), ("; ".join(bad) + " · " if bad else "") + "without inline: cover %s, inner %s %d px, ground %s (notebook %s)" % (
        d["disp"], d["inner"], d["innerH"], d["bg"], d["want"])

TESTS = [
    ("C24.3b E24.3 Cover über dem Notebook ohne Inline-Anzeige/-Fläche", c3b),
]

def main():
    nb = sys.argv[1]; C.NB = nb
    C.ENV = sys.argv[2] if len(sys.argv) > 2 else "lab"
    C.STORE = sys.argv[3] if len(sys.argv) > 3 else "fresh"
    only = sys.argv[4].split(",") if len(sys.argv) > 4 and sys.argv[4] else None
    styles = (os.environ.get("C24_STYLES") or "minimal/light,cyber/dark").split(",")
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
    print("css_e24_3b: %d rot" % red); sys.exit(1 if red else 0)

if __name__ == "__main__":
    main()
