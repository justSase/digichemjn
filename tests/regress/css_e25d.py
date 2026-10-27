"""test_regress — Werkstatt CSS, Eilauftrag E25.d (2026-10-08). Real JupyterLab
under Playwright; read off the page (getComputedStyle), nothing from our
stylesheet.

    python3 tests/regress/css_e25d.py <notebook.ipynb> [lab|lite] [fresh|old]
    (also a module of tests/regress/run.py: TESTS at the end)

  C25.d  dark outside JupyterLab: the preview follows a dark host (Nutzer
         08.10., PyCharm: light cards on a dark theme). PyCharm, VS Code and
         Colab have no JupyterLab theme (no body[data-jp-theme-light], no
         --jp-* colours); JS marks the page `html[data-nbenv]` (E19.4). Built
         here in the real Lab: the cover of the run brought up again,
         html[data-nbenv] set and body[data-jp-theme-light] taken away, then
           pycharm + body.nbdark (JS says dark)           → dark
           pycharm + prefers-color-scheme: dark (media)    → dark
           vscode  + body.vscode-dark (VS Code's class)    → dark
           pycharm, light media, no class                  → light
         "dark" = cover ground, title card and the account card darker than
         luminance 0,1, the title, the lead, the goals and the mode cards' text ≥ 4,5 : 1
         on their ground; "light" = card ground lighter than 0,7. Restored
         afterwards. Not measured: real PyCharm/VS Code/Colab (Lesart: their
         webview reports prefers-color-scheme from the IDE/OS; JS's body.nbdark
         is the sure way — JS E25.d/b).
Gegenprobe v1.67 (a6d3648c): chronicle 08.10., Werkstatt CSS (E25)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import css_e21 as C

FRONT = "var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');"
UP = "(on) => !!(window.__nbCoverShow && window.__nbCoverShow(on))"
SETENV = """([env, cls]) => { var h = document.documentElement, b = document.body;
  if (window.__c25d === undefined) window.__c25d = [h.getAttribute('data-nbenv'), b.getAttribute('data-jp-theme-light'), b.className];
  // hw-E25.int (08.10.): our page script re-sets body.nbdark from the row's
  // stored light/dark (cyber dark pair: red 2 of 2 — the stored pick, not the
  // host); while a case runs the body keeps exactly the classes it names
  // (behauptete bisher: two writes 400/200 ms apart hold them)
  if (window.__c25dMo) { window.__c25dMo.disconnect(); window.__c25dMo = null; }
  if (env === null) { var s = window.__c25d; window.__c25d = undefined;
    if (s[0] === null) h.removeAttribute('data-nbenv'); else h.setAttribute('data-nbenv', s[0]);
    if (s[1] !== null) b.setAttribute('data-jp-theme-light', s[1]); b.className = s[2]; return true; }
  h.setAttribute('data-nbenv', env); b.removeAttribute('data-jp-theme-light');
  ['nbdark', 'nbforce-dark', 'nbforce-light', 'vscode-dark', 'vscode-light'].forEach(function(c){ b.classList.remove(c); });
  (cls || []).forEach(function(c){ b.classList.add(c); });
  var keep = function(){ ['nbdark', 'nbforce-dark', 'nbforce-light', 'vscode-dark', 'vscode-light'].forEach(function(c){
      var want = (cls || []).indexOf(c) > -1; if (b.classList.contains(c) !== want) b.classList.toggle(c, want); });
    if (b.hasAttribute('data-jp-theme-light')) b.removeAttribute('data-jp-theme-light');
    if (h.getAttribute('data-nbenv') !== env) h.setAttribute('data-nbenv', env); };
  window.__c25dMo = new MutationObserver(keep);
  window.__c25dMo.observe(b, {attributes: true, attributeFilter: ['class', 'data-jp-theme-light']});
  window.__c25dMo.observe(h, {attributes: true, attributeFilter: ['data-nbenv']});
  return true; }"""
READ = """() => { """ + FRONT + """
  var c = P && P.querySelector('.nbcover-out'); if (!c) return null;
  var lum = function(s){ var m = s.match(/[\\d.]+/g); if (!m) return null; var a = m.length > 3 ? parseFloat(m[3]) : 1;
    var f = function(v){ v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return {l: 0.2126 * f(+m[0]) + 0.7152 * f(+m[1]) + 0.0722 * f(+m[2]), a: a}; };
  var bgOf = function(e){ for (; e; e = e.parentElement) { var b = getComputedStyle(e).backgroundColor, L = lum(b);
      if (L && L.a > 0.5) return b; } return 'rgb(255, 255, 255)'; };
  var one = function(sel){ var e = c.querySelector(sel); if (!e || !e.getBoundingClientRect().height) return null;
    var cs = getComputedStyle(e), bg = bgOf(e); return {bg: bg, bgl: lum(bg).l, fg: cs.color}; };
  return {cover: one('.nbcover'), card: one('.nbtitle-card'), h: one('.nbtitle-h'), lead: one('.nbtitle-lead'),
          mode: one('.nbmode-opt'), facts: one('.nbtitle-facts li'), acct: one('.nbacct'), out: lum(bgOf(c)).l}; }"""

def _rgb(s):
    import re
    return tuple(int(round(float(x))) for x in re.findall(r"[\d.]+", s)[:3])

CASES = [("pycharm + body.nbdark", "pycharm", ["nbdark"], "dark", "dark"),
         ("pycharm + media dark", "pycharm", [], "dark", "dark"),
         ("vscode + body.vscode-dark", "vscode", ["vscode-dark"], "light", "dark"),
         ("pycharm, light", "pycharm", [], "light", "light")]

def cd(pg, ctx):
    bad, got = [], []
    if not pg.evaluate(UP, True): return False, "BAD kein Cover (__nbCoverShow)"
    pg.wait_for_timeout(1500)
    try:
        for name, env, cls, media, want in CASES:
            pg.emulate_media(color_scheme=media)
            pg.evaluate(SETENV, [env, cls]); pg.wait_for_timeout(400)
            pg.evaluate(SETENV, [env, cls]); pg.wait_for_timeout(200)     # JS may have re-set its classes
            d = pg.evaluate(READ)
            if not d or not d["card"] or not d["h"]: bad.append("BAD %s: Cover nicht gelesen" % name); continue
            row = []
            if want == "dark":
                for k in ("card", "acct"):
                    if d[k] and d[k]["bgl"] > 0.1: row.append("%s-Grund hell (%.2f)" % (k, d[k]["bgl"]))
                if d["out"] > 0.1: row.append("Cover-Grund hell (%.2f)" % d["out"])
                for k in ("h", "lead", "mode", "facts"):
                    if d[k]:
                        cr = C.contrast(_rgb(d[k]["fg"]), _rgb(d[k]["bg"]))
                        if cr < 4.5: row.append("%s Kontrast %.2f:1" % (k, cr))
            else:
                if d["card"]["bgl"] < 0.7: row.append("Karte dunkel (%.2f)" % d["card"]["bgl"])
            got.append("%s: Karte %.2f, Cover %.2f" % (name, d["card"]["bgl"], d["out"]))
            bad += ["%s: %s" % (name, r) for r in row]
    finally:
        pg.evaluate(SETENV, [None, None]); pg.emulate_media(color_scheme="light")
        pg.evaluate(UP, False); pg.wait_for_timeout(800)
    return (not bad), ("; ".join(bad[:6]) + " · " if bad else "") + " | ".join(got)

TESTS = [
    ("C25.d E25.d Vorschau dunkel außerhalb von JupyterLab", cd),
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
        pg.evaluate(C.SET, ["minimal", "light"]); pg.wait_for_timeout(800)
        for name, fn in TESTS:
            ok, d = fn(pg, {"skin": "minimal", "theme": "light", "nb": nb})
            red += not ok
            print("%-4s %s · %s" % ("ok" if ok else "RED", name.split()[0], d[:1200]), flush=True)
        if errs: red += 1; print("RED Seitenfehler", errs[:3])
        b.close()
    print("css_e25d: %d rot" % red); sys.exit(1 if red else 0)

if __name__ == "__main__":
    main()
