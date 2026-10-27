"""test_regress — Werkstatt CSS, Eilauftrag E25.k (2026-10-08). Real JupyterLab
under Playwright; read off the page (getComputedStyle, getBoundingClientRect),
nothing from our stylesheet. Needs the markup of py-E25.k (else BAD).

    python3 tests/regress/css_e25k.py <notebook.ipynb> [lab|lite] [fresh|old]
    (also a module of tests/regress/run.py: TESTS at the end)

  C25.k  the tidied preview LOOKS tidy (the cover of a run, brought up again
         with window.__nbCoverShow, as the reader sees it after a run):
    fold  "What you will learn" / "Sign in" (details > summary): one quiet
          line — no list marker of the browser (display ≠ list-item), no
          triangle at all (E30 A2; until v1.76 our own ▸ that turned), hand cursor, ≥ 11 px, text
          ≥ 4,5 : 1 against the cover;
    lang  the language field set into the slot of the title card (JS does
          that, E25.k Verhalten; here moved in by the test): it sits in the
          card's top right corner (right and top edge 4…24 px inside), one
          line ≤ 26 px high, no name label, each choice ≤ 40 px wide;
    serie the series as one bar: items in one row, each a pill (border
          ≥ 1 px, radius ≥ 8 px), joined by a line (::before), this notebook
          in another border colour, text ≥ 4,5 : 1.
Gegenprobe: v1.67 + py-E25.k markup without this CSS — chronicle 08.10.,
Werkstatt CSS (E25)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import css_e21 as C

FRONT = "var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');"
UP = "(on) => !!(window.__nbCoverShow && window.__nbCoverShow(on))"
READ = """() => { """ + FRONT + """
  var c = P && P.querySelector('.nbcover-out'); if (!c) return null;
  var bgOf = function(e){ for (; e; e = e.parentElement) { var b = getComputedStyle(e).backgroundColor;
      if (b && b !== 'transparent' && !/rgba\\(.*,\\s*0\\)$/.test(b)) return b; } return 'rgb(255, 255, 255)'; };
  var R = function(e){ var r = e.getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; };
  var out = {fold: [], ser: null, lang: null};
  c.querySelectorAll('details.nbcover-learn, details.nbacct-fold').forEach(function(d){
    var s = d.querySelector(':scope > summary'); if (!s) return;
    var cs = getComputedStyle(s), a = getComputedStyle(s, '::after'), was = d.open;
    d.open = false; var t0 = getComputedStyle(s, '::after').transform;
    d.open = true; var t1 = getComputedStyle(s, '::after').transform; d.open = was;
    out.fold.push({k: d.className, disp: cs.display, cursor: cs.cursor, fs: parseFloat(cs.fontSize), color: cs.color,
                   bg: bgOf(s), after: a.content, t0: t0, t1: t1}); });
  var S = c.querySelector('.nbcover-series');
  if (S) { var it = [].slice.call(S.querySelectorAll('.nbser-it'));
    out.ser = it.map(function(e){ var cs = getComputedStyle(e), b = getComputedStyle(e, '::before');
      return {me: e.classList.contains('nbser-me'), r: R(e), bw: parseFloat(cs.borderTopWidth), rad: parseFloat(cs.borderTopLeftRadius),
              bc: cs.borderTopColor, color: cs.color, bg: bgOf(e), before: b.content, bwid: parseFloat(b.width) || 0}; }); }
  return out; }"""
# the language field into the slot, as JS will (E25.k): measured, then put back
LANG = """(put) => { """ + FRONT + """
  var c = P && P.querySelector('.nbcover-out'); if (!c) return null;
  var slot = c.querySelector('.nbcover-lang-slot'), row = c.querySelector('.nblang');
  if (!slot || !row) return {slot: !!slot, row: !!row};
  if (!put) { if (window.__c25k) { window.__c25k[1].insertBefore(row, window.__c25k[2]); window.__c25k = null; } return true; }
  if (row.parentNode !== slot) { window.__c25k = [row, row.parentNode, row.nextSibling]; slot.appendChild(row); }
  var card = c.querySelector('.nbtitle-card').getBoundingClientRect(), r = row.getBoundingClientRect();
  var lab = row.querySelector('.nblang-t');
  return {slot: true, row: true, card: [card.left, card.top, card.right], r: [r.left, r.top, r.right, r.height],
          lab: lab ? lab.getBoundingClientRect().width : 0,
          opts: [].map.call(row.querySelectorAll('.nblang-opt'), function(o){ return o.getBoundingClientRect().width; })}; }"""

def _rgb(s):
    import re
    v = [float(x) for x in re.findall(r"[\d.]+", s)[:3]]
    return tuple(int(round(x)) for x in v)

def ck(pg, ctx):
    bad, got = [], []
    if not pg.evaluate(UP, True): return False, "BAD kein Cover (__nbCoverShow)"
    pg.wait_for_timeout(1500)
    try:
        d = pg.evaluate(READ)
        if not d: return False, "BAD kein Cover"
        if len(d["fold"]) < 2: bad.append("BAD Faltzeilen fehlen (%d, Markup py-E25.k?)" % len(d["fold"]))
        for f in d["fold"]:
            k = f["k"].split()[0]
            cr = C.contrast(_rgb(f["color"]), _rgb(f["bg"]))
            got.append("%s %.1fpx %.1f:1 %s" % (k, f["fs"], cr, f["after"]))
            if f["disp"] == "list-item": bad.append("%s: Browser-Dreieck (list-item)" % k)
            # E30 A2 (Werkstatt CSS, 12.10., Nutzer: die Dreiecke der Akkordeons bleiben versteckt — überall):
            # behauptete bisher: ein eigenes ▸ (::after), das sich beim Öffnen dreht (E25.k) — jetzt KEIN Dreieck
            if any(t in (f["after"] or "") for t in "▸▾▶◂"): bad.append("%s: Dreieck %s (E30 A2: versteckt)" % (k, f["after"]))
            if f["cursor"] != "pointer": bad.append("%s: Zeiger %s" % (k, f["cursor"]))
            if f["fs"] < 11: bad.append("%s: Schrift %.1f px" % (k, f["fs"]))
            if cr < 4.5: bad.append("%s: Kontrast %.2f:1" % (k, cr))
        L = pg.evaluate(LANG, True); pg.wait_for_timeout(300)
        L = pg.evaluate(LANG, True)
        if not L or not L.get("slot") or not L.get("row"): bad.append("BAD Sprach-Platz/-Feld fehlt %s" % L)
        else:
            dr, dt = L["card"][2] - L["r"][2], L["r"][1] - L["card"][1]
            got.append("Sprache rechts %.0f oben %.0f h %.0f Name %.0f Wahl %s" % (dr, dt, L["r"][3], L["lab"], [round(w) for w in L["opts"]]))
            if not (4 <= dr <= 24 and 4 <= dt <= 24): bad.append("Sprache nicht rechts oben in der Karte (%.0f/%.0f px)" % (dr, dt))
            if L["r"][3] > 26: bad.append("Sprache %.0f px hoch" % L["r"][3])
            if L["lab"] > 0: bad.append("Sprache mit Namen (%.0f px)" % L["lab"])
            if any(w > 40 for w in L["opts"]): bad.append("Sprachwahl breit %s" % [round(w) for w in L["opts"]])
        S = d["ser"]
        if not S: bad.append("BAD keine Reihe (Markup py-E25.k?)")
        else:
            tops = [s["r"][1] for s in S]
            got.append("Reihe %d, Rand %s, Radius %s" % (len(S), [s["bw"] for s in S], [s["rad"] for s in S]))
            if max(tops) - min(tops) > 2: bad.append("Reihe nicht in einer Zeile %s" % tops)
            for s in S:
                if s["bw"] < 1 or s["rad"] < 8: bad.append("keine Pille (Rand %s, Radius %s)" % (s["bw"], s["rad"]))
                cr = C.contrast(_rgb(s["color"]), _rgb(s["bg"]))
                if cr < 4.5: bad.append("Reihe Kontrast %.2f:1" % cr)
            for s in S[1:]:
                if s["before"] in (None, "none", "normal") or s["bwid"] < 4: bad.append("keine Verbindungslinie")
            me = [s for s in S if s["me"]]; ot = [s for s in S if not s["me"]]
            if len(me) != 1: bad.append("dieses Notebook %d× markiert" % len(me))
            elif ot and all(o["bc"] == me[0]["bc"] for o in ot): bad.append("dieses Notebook nicht hervorgehoben")
    finally:
        pg.evaluate(LANG, False); pg.evaluate(UP, False); pg.wait_for_timeout(800)
    return (not bad), ("; ".join(bad[:5]) + " · " if bad else "") + " | ".join(got)

TESTS = [
    ("C25.k E25.k Vorschau aufgeräumt: Faltzeilen, Sprache rechts oben, Reihe", ck),
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
        for s, t in (("minimal", "light"), ("minimal", "dark")):
            pg.evaluate(C.SET, [s, t]); pg.wait_for_timeout(800)
            for name, fn in TESTS:
                ok, d = fn(pg, {"skin": s, "theme": t, "nb": nb})
                red += not ok
                print("%-4s %s %s/%s · %s" % ("ok" if ok else "RED", name.split()[0], s, t, d[:900]), flush=True)
        if errs: red += 1; print("RED Seitenfehler", errs[:3])
        b.close()
    print("css_e25k: %d rot" % red); sys.exit(1 if red else 0)

if __name__ == "__main__":
    main()
