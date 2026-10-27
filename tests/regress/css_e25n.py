"""test_regress — Werkstatt CSS, Eilauftrag E25.n (2026-10-08), umgeschrieben
mit E29 P5 (2026-10-12). Real JupyterLab under Playwright; read off the page
(getComputedStyle, getBoundingClientRect), nothing from our stylesheet.

    python3 tests/regress/css_e25n.py <notebook.ipynb> [lab|lite] [fresh|old]
    (also a module of tests/regress/run.py: TESTS at the end)

  C25.n  the feedback cell in the ⚙ drawer (.nbcell.pg-fb.nbfb; set into the
         drawer by the test when the notebook does not carry one) is VISIBLE
         when ⚙ is open and hidden on 👤 (one place); E29 P5: it is a small
         text, no button — its heading and text <= 12.5 px, nothing in it
         with a border and a pill radius.
  Behauptete bisher (E25.n): the link is a pill button (border, radius ≥ 8,
  ≥ 28 px high) in ⚙ and in the preview. E29 P5 (Nutzer 12.10.): "kein
  Formular, kein mailto — nur ein Text"; the preview's part is C29.P5.
Gegenprobe v1.67 (a6d3648c): chronicle 08.10., Werkstatt CSS (E25).
Gegenprobe v1.75 (96f71b52), E29 part: chronicle 12.10., Werkstatt CSS (E29)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import css_e21 as C

FRONT = "var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');"
UP = "(on) => !!(window.__nbCoverShow && window.__nbCoverShow(on))"
CELL = ('<div class="nbcell pg-fb nbfb" data-c25n="1"><div class="nbcell-h">Feedback</div>'
        '<span class="nbfb-text">Feedback, errors and contact: by e-mail to <span class="nbfb-to">contact@example.org</span></span></div>')
PUT = """(html) => { var h = document.getElementById('nbpanel-root'), g = h && h.querySelector('.nbdrawer .nbdrawer-grid, .nbdrawer');
  if (!g) return 'BAD keine Schublade'; if (h.querySelector('.nbdrawer .nbfb')) return 'own';
  var t = document.createElement('div'); t.innerHTML = html; g.appendChild(t.firstChild); return 'test'; }"""
TAKE = "() => document.querySelectorAll('[data-c25n]').forEach(function(e){ e.remove(); })"
PAGE = """(p) => { var h = document.getElementById('nbpanel-root'); var b = h && h.querySelector('.nbcorner ' + p);
  if (!b) return null; var r = b.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }"""
READ = """(sel) => { var e = document.querySelector(sel); if (!e) return null;
  var r = e.getBoundingClientRect(), cs = getComputedStyle(e);
  var bgOf = function(x){ for (; x; x = x.parentElement) { var b = getComputedStyle(x).backgroundColor, m = b.match(/[\\d.]+/g);
      if (m && (m.length < 4 || parseFloat(m[3]) > 0.5)) return b; } return 'rgb(255, 255, 255)'; };
  var vis = r.width > 2 && r.height > 2 && cs.visibility !== 'hidden' && !!e.offsetParent;
  return {vis: vis, h: r.height, cx: r.left + r.width / 2, bw: parseFloat(cs.borderTopWidth), rad: parseFloat(cs.borderTopLeftRadius),
          cur: cs.cursor, deco: cs.textDecorationLine, fg: cs.color, bg: bgOf(e)}; }"""
COVER = """(html) => { """ + FRONT + """ var c = P && P.querySelector('.nbcover-out'); if (!c) return null;
  var a = c.querySelector('.nbfb-link'); if (!a) { var t = document.createElement('div'); t.innerHTML = html;
    a = t.firstChild; a.setAttribute('data-c25n', '1'); (c.querySelector('.nbcover') || c).appendChild(a); }
  a.scrollIntoView({block: 'center'}); var r = c.querySelector('.nbtitle-card').getBoundingClientRect(); return r.left + r.width / 2; }"""

def _rgb(s):
    import re
    return tuple(int(round(float(x))) for x in re.findall(r"[\d.]+", s)[:3])

def _btn(d, minh, who):
    bad = []
    if not d or not d["vis"]: return ["%s: Knopf nicht sichtbar" % who]
    cr = C.contrast(_rgb(d["fg"]), _rgb(d["bg"]))
    if d["bw"] < 1: bad.append("%s: kein Rand" % who)
    if d["rad"] < 8: bad.append("%s: keine Pille (Radius %.0f)" % (who, d["rad"]))
    if d["h"] < minh: bad.append("%s: %.0f px hoch" % (who, d["h"]))
    if d["cur"] != "pointer": bad.append("%s: Zeiger %s" % (who, d["cur"]))
    if "underline" in (d["deco"] or ""): bad.append("%s: unterstrichen (Textlink)" % who)
    if cr < 4.5: bad.append("%s: Kontrast %.2f:1" % (who, cr))
    return bad

SMALL = """() => { var c = document.querySelector('#nbpanel-root .nbdrawer .nbcell.pg-fb'); if (!c) return null;
  var big = [], pill = [];
  [c].concat([].slice.call(c.querySelectorAll('*'))).forEach(function(e){ var cs = getComputedStyle(e), r = e.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0)) return;
    var own = [].some.call(e.childNodes, function(n){ return n.nodeType === 3 && n.textContent.trim(); });
    if (own && parseFloat(cs.fontSize) > 12.5) big.push(String(e.className).split(' ')[0] + ' ' + cs.fontSize);
    if (e !== c && parseFloat(cs.borderTopWidth) >= 1 && parseFloat(cs.borderTopLeftRadius) >= 8) pill.push(e.tagName + '.' + String(e.className).split(' ')[0]); });
  return {big: big, pill: pill}; }"""

def cn(pg, ctx):
    bad, got = [], []
    try:
        how = pg.evaluate(PUT, CELL)
        if how.startswith("BAD"): return False, how
        for page, sel in (("diff", ".nbbtn.nbgear"), ("code", ".nbbtn.nbprofile")):
            xy = pg.evaluate(PAGE, sel)
            if not xy: bad.append("BAD kein Knopf %s" % sel); continue
            pg.mouse.click(*xy); pg.wait_for_timeout(1200)
            pg.evaluate("() => { var a = document.querySelector('#nbpanel-root .nbdrawer .nbcell.pg-fb'); if (a) a.scrollIntoView({block: 'center'}); }")
            pg.wait_for_timeout(300)
            d = pg.evaluate(READ, "#nbpanel-root .nbdrawer .nbcell.pg-fb")
            pgx = pg.evaluate("() => document.getElementById('nbpanel-root').dataset.page")
            got.append("%s(%s): %s" % (page, pgx, json.dumps({k: d[k] for k in ("vis", "h")} if d else None)))
            if page == "diff":
                if not d or not d["vis"]: bad.append("⚙: Feedback nicht sichtbar")
                else:
                    sm = pg.evaluate(SMALL)
                    if sm["big"]: bad.append("⚙: Text größer als 12,5 px: %s" % sm["big"][:3])
                    if sm["pill"]: bad.append("⚙: Knopf statt Text: %s" % sm["pill"][:3])
            elif d and d["vis"]: bad.append("auch auf 👤 sichtbar")
            pg.keyboard.press("Escape"); pg.wait_for_timeout(500)
            if pg.evaluate("() => document.getElementById('nbpanel-root').classList.contains('open')"):
                pg.mouse.click(*xy); pg.wait_for_timeout(600)
    finally:
        pg.evaluate(TAKE); pg.wait_for_timeout(300)
    return (not bad), ("; ".join(bad[:5]) + " · " if bad else "") + " | ".join(got) + " · (as=%s)" % how

TESTS = [
    ("C25.n E25.n/E29 Feedback im ⚙ sichtbar, klein, kein Knopf", cn),
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
        for s, t in (("minimal", "light"), ("cyber", "dark")):
            pg.evaluate(C.SET, [s, t]); pg.wait_for_timeout(800)
            for name, fn in TESTS:
                ok, d = fn(pg, {"skin": s, "theme": t, "nb": nb})
                red += not ok
                print("%-4s %s %s/%s · %s" % ("ok" if ok else "RED", name.split()[0], s, t, d[:900]), flush=True)
        if errs: red += 1; print("RED Seitenfehler", errs[:3])
        b.close()
    print("css_e25n: %d rot" % red); sys.exit(1 if red else 0)

if __name__ == "__main__":
    main()
