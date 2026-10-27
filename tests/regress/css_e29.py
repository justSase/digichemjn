"""test_regress — Werkstatt CSS, Eilauftrag E29 (2026-10-12, Rückmeldung Nutzer
zu v1.75). Real JupyterLab under Playwright; everything read off the page
(getBoundingClientRect, getComputedStyle, Range, screenshot pixels).

    python3 tests/regress/css_e29.py <vorlage.ipynb> [lab] [fresh|old]
    (also a module of tests/regress/run.py: TESTS at the end)

  C29.P2  cover, "What you will learn" open: the headings ("You will be able
          to", "Chapters") AND their blocks (goal list, chapter list) on the
          main axis — |centre − title card centre| <= 1 px each.
  C29.P3  cover timeline: hovering a chapter mark shows its info box and
          moves what is below the timeline by 0 px (<= 0.5); the box sits
          under the XP bar and above the mode question (short text).
  C29.P4  the info box: the head (symbol name, `b`) alone in line 1 and its
          ink centred on the box (<= 1 px), the text below it.
  C29.P5  feedback in the preview (`.nbfb-note`, py-E29 — set in as Python
          writes it when the notebook does not carry it yet): small
          text, no button — font <= 12.5 px, no border, no ground, <= 2 lines
          high, as wide as its text (+ 12 px), on the axis (<= 1 px), ink
          >= 4.5 : 1.
  C29.D5  full screen (⛶): the title card, the YOC strip and the own cells
          on one axis (<= 1 px); the cells' viewport no wider than its box.
  C29.D6  lens 60/100/200: the YOC strip scales like the document — its
          font : document text constant (±3 %), its height ∝ lens (±2 px).
  C29.D7  document font: standard one step up (14.3 px at lens 100); with
          --nbfs 1.3 (the font widget's contract) 18.6 px, at lens 150 too
          (× 1.5, independent), preview/panel/YOC unchanged.
  C29.D8  the moving marker at lens 60/100/150/200: one round object — a
          covering core wider than the lane, in the marker colour (ΔE2000 <= 5 — the marker is drawn at .95
          beside the lane, halfway to 0.42 × the light's radius; the grip's
          "=" and the marks hidden).
  C29.D10 cyber dark + light: inside a plot no texture (an empty patch
          spreads <= 3 levels), outside it the texture stays (> 3).
Gegenprobe v1.75 (96f71b52, Vorlage): chronicle 12.10., Werkstatt CSS (E29)."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import css_e21 as C
import css_e22_8 as E8

FRONT = "var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');"
UP = "(on) => !!(window.__nbCoverShow && window.__nbCoverShow(on))"
SC = "document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer')"

def _cover(pg):
    if not pg.evaluate(UP, True): return False
    pg.wait_for_timeout(1500); return True

def _uncover(pg):
    pg.mouse.move(5, 450); pg.evaluate(UP, False); pg.wait_for_timeout(800)

P2 = """() => { """ + FRONT + """ var c = P && P.querySelector('.nbcover-out'); if (!c) return null;
  var d = c.querySelector('details.nbcover-learn'); if (!d) return {nofold: true};
  d.open = true; d.scrollIntoView({block: 'start'});
  var t = c.querySelector('.nbtitle-card').getBoundingClientRect(), mid = t.left + t.width / 2;
  // a block: its box centre AND how tightly the box holds its text (ink of
  // the items; a bullet list keeps its bullet room on the left)
  var m = function(e){ var r = e.getBoundingClientRect(), pl = parseFloat(getComputedStyle(e).paddingLeft) || 0;
      var l = 1e9, rr = -1e9, w = document.createTreeWalker(e, NodeFilter.SHOW_TEXT), n;
      while ((n = w.nextNode())) { if (!n.textContent.trim()) continue; var g = document.createRange(); g.selectNodeContents(n);
        var rs = g.getClientRects(); for (var i = 0; i < rs.length; i++) if (rs[i].width > 0) { l = Math.min(l, rs[i].left); rr = Math.max(rr, rs[i].right); } }
      var bul = getComputedStyle(e).listStyleType !== 'none' ? pl : 0;
      return {dx: Math.round((r.left + r.width / 2 - mid) * 10) / 10, gapL: Math.round((l - r.left - bul) * 10) / 10, gapR: Math.round((r.right - rr) * 10) / 10}; };
  var ink = function(e){ var g = document.createRange(); g.selectNodeContents(e); var rs = g.getClientRects(), l = 1e9, r = -1e9;
      for (var i = 0; i < rs.length; i++) if (rs[i].width > 0) { l = Math.min(l, rs[i].left); r = Math.max(r, rs[i].right); }
      return Math.round(((l + r) / 2 - mid) * 10) / 10; };
  return {heads: [].map.call(c.querySelectorAll('.nbtitle-facts-h'), function(h){ return [h.textContent.trim(), ink(h)]; }),
          goals: [].map.call(c.querySelectorAll('.nbtitle-goals'), m), chaps: [].map.call(c.querySelectorAll('.nbtitle-chaps'), m)}; }"""

def p2(pg, ctx):
    if not _cover(pg): return False, "BAD kein Cover"
    try:
        d = pg.evaluate(P2)
    finally:
        _uncover(pg)
    if not d or d.get("nofold"): return False, "BAD kein Faltblock 'What you will learn' (%s)" % d
    bad = []
    if len(d["heads"]) < 2 or not d["goals"] or not d["chaps"]: return False, "BAD Köpfe/Blöcke fehlen %s" % d
    for nm, dx in d["heads"]:
        if abs(dx) > 1: bad.append("Kopf %s %+.1f px" % (nm, dx))
    for nm in ("goals", "chaps"):
        for b in d[nm]:
            if abs(b["dx"]) > 1: bad.append("Block %s %+.1f px neben der Achse" % (nm, b["dx"]))
            if b["gapL"] > 8 or b["gapR"] > 8: bad.append("Block %s nicht auf der Achse: Text links %.0f / rechts %.0f px vom Rand" % (nm, b["gapL"], b["gapR"]))
    return (not bad), ("; ".join(bad) + " · " if bad else "") + json.dumps(d, ensure_ascii=False)

TL = """() => { """ + FRONT + """ var c = P && P.querySelector('.nbcover-out'); if (!c) return null;
  var tl = c.querySelector('details.nbcover-tl'); if (!tl) return {notl: true}; tl.open = true;
  var mk = [].filter.call(tl.querySelectorAll('.nbtl-chapter .nbtl-mk'), function(e){ return e.getBoundingClientRect().width > 0; });
  if (mk.length < 2) return {nomk: mk.length};
  tl.scrollIntoView({block: 'center'}); var r = mk[1].getBoundingClientRect();
  return {xy: [r.left + r.width / 2, r.top + r.height / 2]}; }"""
GEO = """() => { """ + FRONT + """ var c = P.querySelector('.nbcover-out'), tl = c.querySelector('details.nbcover-tl');
  var nx = c.querySelector('.nbmode');
  var d = tl.querySelector(':scope > .nbtl-desc'), vis = !!(d && !d.hidden && d.getBoundingClientRect().height > 0);
  var o = {below: nx ? nx.getBoundingClientRect().top : null, belowCls: nx ? String(nx.className).split(' ')[0] : null, vis: vis};
  var bars = [].filter.call(tl.querySelectorAll('*'), function(e){ var r = e.getBoundingClientRect(); return r.width > 300 && r.height > 3 && r.height < 16 && !e.closest('.nbtl-desc'); });
  o.barB = bars.length ? Math.max.apply(null, bars.map(function(e){ return e.getBoundingClientRect().bottom; })) : null;
  if (vis) {
    var dr = d.getBoundingClientRect(), b = d.querySelector('b'), s = d.querySelector('span');
    var g = document.createRange(); g.selectNodeContents(b); var rs = [].filter.call(g.getClientRects(), function(x){ return x.width > 0; });
    var l = Math.min.apply(null, rs.map(function(x){ return x.left; })), rr = Math.max.apply(null, rs.map(function(x){ return x.right; }));
    var sr = s ? s.getBoundingClientRect() : null;
    o.desc = {top: dr.top, bottom: dr.bottom, mid: dr.left + dr.width / 2, bInk: (l + rr) / 2, bTop: rs[0].top, bBot: Math.max.apply(null, rs.map(function(x){ return x.bottom; })),
              sTop: sr ? sr.top : null, sText: s ? s.textContent.length : 0, bLines: new Set(rs.map(function(x){ return Math.round(x.top); })).size};
  }
  return o; }"""

def _hover(pg):
    if not _cover(pg): return None, "BAD kein Cover"
    t = pg.evaluate(TL)
    if not t or not t.get("xy"): _uncover(pg); return None, "BAD keine Kapitelmarke in der Cover-Timeline %s" % t
    pg.mouse.move(5, 5); pg.wait_for_timeout(600)
    a = pg.evaluate(GEO)
    pg.mouse.move(*t["xy"], steps=3); pg.wait_for_timeout(900)
    b = pg.evaluate(GEO)
    return (a, b), None

def p3(pg, ctx):
    ab, err = _hover(pg)
    if err: return False, err
    try:
        a, b = ab
        bad = []
        if not b["vis"]: return False, "BAD Hover zeigt keine Infobox %s" % b
        if a["below"] is None: return False, "BAD nichts unter der Timeline"
        dy = b["below"] - a["below"]
        if abs(dy) > 0.5: bad.append("darunter (%s) %+.1f px verschoben" % (a["belowCls"], dy))
        d = b["desc"]
        if b["barB"] is not None and d["top"] < b["barB"] - 0.5: bad.append("Box über der XP-Leiste (%.1f < %.1f)" % (d["top"], b["barB"]))
        if d["bottom"] > b["below"] + 0.5: bad.append("Box ragt in den Block darunter (%.1f > %.1f)" % (d["bottom"], b["below"]))
        return (not bad), ("; ".join(bad) + " · " if bad else "") + "Δ %+.1f px unter (%s), Box %.0f…%.0f, XP-Leiste bis %s" % (
            dy, a["belowCls"], d["top"], d["bottom"], b["barB"] and round(b["barB"], 1))
    finally:
        _uncover(pg)

def p4(pg, ctx):
    ab, err = _hover(pg)
    if err: return False, err
    try:
        b = ab[1]
        if not b["vis"]: return False, "BAD keine Infobox"
        d, bad = b["desc"], []
        if d["bLines"] != 1: bad.append("Kopf über %d Zeilen" % d["bLines"])
        if d["sText"] and d["sTop"] is not None and d["sTop"] < d["bBot"] - 1: bad.append("Text in Zeile 1 neben dem Kopf (Text oben %.1f, Kopf unten %.1f)" % (d["sTop"], d["bBot"]))
        if abs(d["bInk"] - d["mid"]) > 1: bad.append("Kopf %+.1f px neben der Mitte" % (d["bInk"] - d["mid"]))
        return (not bad), ("; ".join(bad) + " · " if bad else "") + "Kopf %+.1f px, Text oben %s / Kopf unten %.1f" % (d["bInk"] - d["mid"], d["sTop"] and round(d["sTop"], 1), d["bBot"])
    finally:
        _uncover(pg)

# py-E29 P5 (claude/VERTRAG-E29-py.md): the cover's feedback line — set in by the
# test, as Python writes it (inline look included), when the notebook does not carry it yet
NOTE = ('<div class="nbfb nbfb-note" data-c29="1" style="max-width:640px;margin:16px auto 0;text-align:center;'
        'font-size:.8em;color:#8b98a5"><span class="nbfb-text">Feedback, errors and contact: by e-mail to '
        '<span class="nbfb-to">contact@example.org</span></span></div>')
FB = """(html) => { """ + FRONT + """ var c = P && P.querySelector('.nbcover-out'); if (!c) return null;
  var a = c.querySelector('.nbfb-note'), how = 'own';
  if (!a) { var t = document.createElement('div'); t.innerHTML = html; a = t.firstChild; (c.querySelector('.nbcover') || c).appendChild(a); how = 'test'; }
  a.scrollIntoView({block: 'center'});
  var r = a.getBoundingClientRect(), cs = getComputedStyle(a), t = c.querySelector('.nbtitle-card').getBoundingClientRect();
  var l = 1e9, rr = -1e9, w = document.createTreeWalker(a, NodeFilter.SHOW_TEXT), n;
  while ((n = w.nextNode())) { if (!n.textContent.trim()) continue; var g = document.createRange(); g.selectNodeContents(n);
    [].forEach.call(g.getClientRects(), function(x){ if (x.width > 0) { l = Math.min(l, x.left); rr = Math.max(rr, x.right); } }); }
  var bgOf = function(x){ for (; x; x = x.parentElement) { var b = getComputedStyle(x).backgroundColor, m = b.match(/[\\d.]+/g);
      if (m && (m.length < 4 || parseFloat(m[3]) > 0.5)) return b; } return 'rgb(255, 255, 255)'; };
  var own = cs.backgroundColor.match(/[\\d.]+/g);
  var o = {how: how, w: r.width, ink: rr - l, h: r.height, dx: r.left + r.width / 2 - (t.left + t.width / 2), fs: parseFloat(cs.fontSize), lh: parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.45,
          bw: parseFloat(cs.borderTopWidth) + parseFloat(cs.borderLeftWidth), ground: !!(own && (own.length < 4 || parseFloat(own[3]) > 0.05)) || cs.backgroundImage !== 'none',
          fg: cs.color, bg: bgOf(a.parentElement), tag: a.tagName, card: t.width};
  [].forEach.call(document.querySelectorAll('[data-c29]'), function(e){ e.remove(); });
  return o; }"""

def p5(pg, ctx):
    if not _cover(pg): return False, "BAD kein Cover"
    try:
        d = pg.evaluate(FB, NOTE)
    finally:
        _uncover(pg)
    if not d or d.get("none"): return False, "BAD kein Feedback (.nbfb-note/.nbfb-cover) in der Vorschau"
    import re
    rgb = lambda s: tuple(int(round(float(x))) for x in re.findall(r"[\d.]+", s)[:3])
    cr = C.contrast(rgb(d["fg"]), rgb(d["bg"]))
    bad = []
    if d["fs"] > 12.5: bad.append("Schrift %.1f px" % d["fs"])
    if d["bw"] > 0: bad.append("Rand %.1f px (Knopf)" % d["bw"])
    if d["ground"]: bad.append("eigene Fläche")
    if d["h"] > 2 * d["lh"] + 2: bad.append("%.0f px hoch (> 2 Zeilen)" % d["h"])
    if d["w"] > d["ink"] + 12 or d["w"] >= d["card"]: bad.append("%.0f px breit für %.0f px Text (Karte %.0f)" % (d["w"], d["ink"], d["card"]))
    if abs(d["dx"]) > 1: bad.append("%+.1f px neben der Achse" % d["dx"])
    if cr < 4.5: bad.append("Kontrast %.2f:1" % cr)
    return (not bad), ("; ".join(bad) + " · " if bad else "") + "%s (%s) %.0f×%.0f px, Text %.0f px, %.1f px Schrift, Rand %.0f, Kontrast %.2f" % (d["tag"], d["how"], d["w"], d["h"], d["ink"], d["fs"], d["bw"], cr)

AX = """() => { """ + FRONT + """ var R = function(e){ var r = e.getBoundingClientRect(); return r.width > 0 ? r : null; };
  var t = P.querySelector('.nbtitle-card'), f = P.querySelector('.jp-Notebook-footer'), v = P.querySelector('.jp-WindowedPanel-viewport'), i = P.querySelector('.jp-WindowedPanel-inner');
  var mid = function(r){ return r ? Math.round((r.left + r.width / 2) * 10) / 10 : null; };
  var own = [].filter.call(P.querySelectorAll('.jp-Cell[class*="nbown-"]'), function(c){ return c.getBoundingClientRect().height > 4; }).map(function(c){ return mid(R(c)); });
  var cells = [].filter.call(P.querySelectorAll('.jp-Cell'), function(c){ return c.getBoundingClientRect().height > 4; }).map(function(c){ return mid(R(c)); });
  return {fs: !!document.fullscreenElement, card: t ? mid(R(t)) : null, foot: f ? mid(R(f)) : null, own: own, cells: cells,
          vR: v ? v.getBoundingClientRect().right : null, iR: i ? i.getBoundingClientRect().right : null}; }"""
FULL = "() => { var b = document.querySelector('#nbpanel-root .nbbtn.nbfull'); if (!b) return null; var r = b.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }"

def d5(pg, ctx):
    import js_e23_10 as J                    # one own cell at the end (made here: an own cell
    J._make_own(pg); pg.keyboard.press("Escape"); pg.mouse.move(700, 450)   # changes the page — last test)
    xy = pg.evaluate(FULL)
    if not xy: return False, "BAD kein ⛶"
    pg.mouse.click(*xy); pg.wait_for_timeout(2500)
    try:
        if not pg.evaluate("() => !!document.fullscreenElement"): return False, "BAD Vollbild ging nicht an"
        pg.evaluate("() => { var n = %s; if (n) n.scrollTop = 0; }" % SC); pg.wait_for_timeout(1200)
        a = pg.evaluate(AX)
        pg.evaluate("() => { var n = %s; if (n) n.scrollTop = n.scrollHeight; }" % SC); pg.wait_for_timeout(1500)
        b = pg.evaluate(AX)
    finally:
        if pg.evaluate("() => !!document.fullscreenElement"):
            pg.evaluate("() => document.exitFullscreen()"); pg.wait_for_timeout(2000)
    if a["card"] is None or b["foot"] is None: return False, "BAD Titelkarte/YOC nicht gemessen %s %s" % (a, b)
    bad, ax = [], a["card"]
    if abs(b["foot"] - ax) > 1: bad.append("YOC %+.1f px neben der Titelkarte" % (b["foot"] - ax))
    for o in b["own"]:
        if abs(o - ax) > 1: bad.append("eigene Zelle %+.1f px" % (o - ax))
    for c in a["cells"]:
        if abs(c - ax) > 1: bad.append("Zelle %+.1f px" % (c - ax)); break
    if a["vR"] is not None and a["iR"] is not None and a["vR"] > a["iR"] + 0.5: bad.append("Viewport %.0f px breiter als sein Behälter" % (a["vR"] - a["iR"]))
    return (not bad), ("; ".join(bad) + " · " if bad else "") + "Achse %.1f · YOC %.1f · eigene %s" % (ax, b["foot"], b["own"])

TXT = """() => { """ + FRONT + """ var Z = function(e){ var z = 1; for (var x = e; x; x = x.parentElement) z *= parseFloat(getComputedStyle(x).zoom) || 1; return z; };
  var t = [].filter.call(P.querySelectorAll('.nbbox-concept'), function(e){ return e.getBoundingClientRect().height > 0; })[0] || P.querySelector('.nbbox-concept');
  var f = P.querySelector('.jp-Notebook-footer'), fr = f ? f.getBoundingClientRect() : null;
  var cv = P.querySelector('.nbcover-out .nbtitle-lead'), pl = document.querySelector('#nbpanel-root .nbmap-lab');
  return {text: t ? parseFloat(getComputedStyle(t).fontSize) * Z(t) : null, zf: parseFloat(getComputedStyle(document.body).getPropertyValue('--nbzf')) || 1,
          yoc: f ? parseFloat(getComputedStyle(f, '::before').fontSize) : null, yocH: fr ? fr.height : null,
          cover: cv ? parseFloat(getComputedStyle(cv).fontSize) : null, panel: pl ? parseFloat(getComputedStyle(pl).fontSize) : null}; }"""

def _lens(pg, z):
    pg.evaluate(E8.ZOOM, z); pg.wait_for_timeout(1500)

def d6(pg, ctx):
    got, bad = {}, []
    try:
        for z in (100, 60, 200):
            _lens(pg, z); got[z] = pg.evaluate(TXT)
    finally:
        _lens(pg, 100)
    if any(not got[z]["text"] or not got[z]["yoc"] for z in got): return False, "BAD nicht gemessen %s" % got
    r0 = got[100]["yoc"] / got[100]["text"]
    for z in (60, 200):
        r = got[z]["yoc"] / got[z]["text"]
        if abs(r / r0 - 1) > 0.03: bad.append("Lupe %d: YOC : Text %.2f statt %.2f" % (z, r, r0))
        h = got[100]["yocH"] * got[z]["zf"]
        if abs(got[z]["yocH"] - h) > 2: bad.append("Lupe %d: YOC %.0f px hoch statt %.0f" % (z, got[z]["yocH"], h))
    return (not bad), ("; ".join(bad) + " · " if bad else "") + " | ".join("%d: Text %.2f YOC %.1f/%.0f px" % (z, got[z]["text"], got[z]["yoc"], got[z]["yocH"]) for z in (60, 100, 200))

# Hauptwerkstatt 12.10. (Zusammenführen E29): behauptete bisher, --nbfs auf <html> allein entscheide. js-E29 setzt
# es (Vertrag D7) auf <html> UND das Notebook-Panel (das Panel behält seinen Wert) — der Test setzt es wie JS.
# Die Seite stellt --nbfs alle 1,5 s aus dem gemerkten Wert nach (fsApply) → über window.__nbFontSize (js-E29), sonst von Hand.
FS = """(v) => { if (window.__nbFontSize) { window.__nbFontSize(v === null ? 100 : Math.round(v * 100)); return; }
  [document.documentElement].concat([].slice.call(document.querySelectorAll('.jp-NotebookPanel[data-digichem]'))).forEach(function(e){
  if (v === null) e.style.removeProperty('--nbfs'); else e.style.setProperty('--nbfs', String(v)); }); }"""

def d7(pg, ctx):
    bad, got = [], []
    try:
        _lens(pg, 100); pg.evaluate(FS, None); pg.wait_for_timeout(600)
        a = pg.evaluate(TXT)
        pg.evaluate(FS, 1.3); pg.wait_for_timeout(800)
        b = pg.evaluate(TXT)
        _lens(pg, 150); c = pg.evaluate(TXT)
    finally:
        pg.evaluate(FS, None); _lens(pg, 100)
    if not a["text"]: return False, "BAD kein Dokumenttext"
    if abs(a["text"] - 14.3) > 0.15: bad.append("Standard %.2f px (soll 14,3 = 13 + 1 Stufe)" % a["text"])
    if abs(b["text"] - 14.3 * 1.3) > 0.2: bad.append("--nbfs 1.3: %.2f px (soll %.2f)" % (b["text"], 14.3 * 1.3))
    if abs(c["text"] - 14.3 * 1.3 * c["zf"]) > 0.3: bad.append("--nbfs 1.3 × Lupe %.2f: %.2f px (soll %.2f)" % (c["zf"], c["text"], 14.3 * 1.3 * c["zf"]))
    for k in ("cover", "panel", "yoc"):
        if a[k] is not None and b[k] is not None and abs(a[k] - b[k]) > 0.01: bad.append("%s wächst mit (%.2f → %.2f)" % (k, a[k], b[k]))
    return (not bad), ("; ".join(bad) + " · " if bad else "") + "Text 100 %%: %.2f · 130 %%: %.2f · 130 %% × Lupe %.2f: %.2f · Vorschau %s · Panel %s · YOC %s" % (
        a["text"], b["text"], c["zf"], c["text"], a["cover"], a["panel"], a["yoc"])

# the grip's "=" (::before) out of the way: what is read is the core under it
NOEQ = """(on) => { var id = '__nbc29_noeq', s = document.getElementById(id);
  if (!on) { if (s) s.remove(); return; }
  if (!s) { s = document.createElement('style'); s.id = id; document.head.appendChild(s); }
  s.textContent = '#nbpanel-root .nbmap-here::before{visibility:hidden!important}'; }"""
NBMC = "() => { var m = document.querySelector('#nbpanel-root .nbmap-here'); return m ? getComputedStyle(m).getPropertyValue('--nbm-c').trim() : null; }"

def _hex(s):
    import re
    s = s.strip()
    if s.startswith("#"):
        s = s[1:]
        if len(s) == 3: s = "".join(c * 2 for c in s)
        return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(int(round(float(x))) for x in re.findall(r"[\d.]+", s)[:3])

def d8(pg, ctx):
    bad, got = [], []
    try:
        for z in (60, 100, 150, 200):
            _lens(pg, z); pg.evaluate(C.TOP); pg.wait_for_timeout(1500)
            pg.evaluate(C.BARE, True); pg.evaluate(NOEQ, True); pg.wait_for_timeout(300)
            m = pg.evaluate(C.MARK); col = pg.evaluate(NBMC)
            g = pg.evaluate("() => { var h = document.querySelector('#nbpanel-root .nbmap-here'); return h ? h.getBoundingClientRect().width : null; }")
            if not m or not col or not g: bad.append("BAD Lupe %d: kein Marker" % z); continue
            k = g / 11.0                         # marker box = 11 px × lens (11-k4-scale)
            gr = pg.evaluate("() => { var h = document.querySelector('#nbpanel-root .nbmap-here'); return parseFloat(getComputedStyle(h, '::after').width) / 2; }")
            lane = 4 * k                         # half the lane (8 px × lens)
            rho = (lane + 0.42 * gr) / 2.0       # beside the lane, inside a core of 0.42 × the light
            if rho < lane + 1: rho = lane + 1
            clip = {"x": max(0, int(m["x"] - gr - 4)), "y": max(0, int(m["y"] - gr - 4)), "width": int(2 * gr) + 8, "height": int(2 * gr) + 8}
            im = C.shot(pg, clip)
            px = [im.getpixel((int(round(m["x"] + s * rho - clip["x"])), int(round(m["y"] - clip["y"])))) for s in (-1, 1)]
            want = _hex(col)
            de = max(C.de2000(p, want) for p in px)
            got.append("%d: Kern ΔE %.1f bei %.1f px (Strich ±%.1f, Leuchten %.1f)" % (z, de, rho, lane, gr))
            if de > 5: bad.append("Lupe %d: kein deckender runder Kern neben dem Strich (ΔE %.1f, %s statt %s)" % (z, de, px, want))
    finally:
        pg.evaluate(C.BARE, False); pg.evaluate(NOEQ, False); _lens(pg, 100)
    return (not bad), ("; ".join(bad[:4]) + " · " if bad else "") + " | ".join(got)

PLOT = """() => { """ + FRONT + """
  var vis = function(){ return [].filter.call(P.querySelectorAll('svg.nbplot, img.nbplot'), function(e){ var r = e.getBoundingClientRect(); return r.width > 200 && r.height > 120 && getComputedStyle(e).visibility !== 'hidden'; }); };
  if (!vis().length) { var hs = [].filter.call(P.querySelectorAll('.jupyter-widget-Collapse-header'), function(h){ return /VISUAL|ABBILD|VERANSCHAUL/i.test(h.textContent); });
    for (var i = 0; i < hs.length && !vis().length; i++) if (!hs[i].parentElement.classList.contains('jupyter-widget-Collapse-open')) hs[i].click(); }
  return vis().length; }"""
PLOTR = """() => { """ + FRONT + """ var e = [].filter.call(P.querySelectorAll('svg.nbplot, img.nbplot'), function(e){ var r = e.getBoundingClientRect(); return r.width > 200 && r.height > 120 && getComputedStyle(e).visibility !== 'hidden'; })[0];
  if (!e) return null; e.scrollIntoView({block: 'center'}); var r = e.getBoundingClientRect(), o = P.querySelector('.jp-WindowedPanel-outer').getBoundingClientRect();
  return {x: r.left, y: r.top, w: r.width, h: r.height, ol: o.left}; }"""

def _spread(im):
    px = list(im.convert('RGB').getdata()) if not hasattr(im, 'get_flattened_data') else list(im.get_flattened_data()); ls = [0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2] for p in px]
    return max(ls) - min(ls)

def d10(pg, ctx):
    bad, got = [], []
    s0, t0 = ctx.get("skin", "minimal"), ctx.get("theme", "light")
    try:
        for t in ("dark", "light"):
            pg.evaluate(C.SET, ["cyber", t]); pg.wait_for_timeout(1200)
            for _ in range(3):
                if pg.evaluate(PLOT): break
                pg.wait_for_timeout(1500)
            pg.wait_for_timeout(1200)
            r = pg.evaluate(PLOTR)
            if not r: bad.append("BAD %s: kein Plot sichtbar" % t); continue
            pg.mouse.move(5, 450); pg.wait_for_timeout(1500)
            # empty patch: top right inside the axes (the curve and the grid lie low / in the middle)
            ins = C.shot(pg, {"x": int(r["x"] + 0.80 * r["w"]), "y": int(r["y"] + 0.10 * r["h"]), "width": 40, "height": 40})
            # outside: the page margin left of the plot, at the same height
            ox = int(max(r["ol"] + 60, r["x"] - 140))
            outs = C.shot(pg, {"x": ox, "y": int(r["y"] + 0.10 * r["h"]), "width": 40, "height": 40})
            a, b = _spread(ins), _spread(outs)
            got.append("%s: innen %.1f · außen %.1f" % (t, a, b))
            if a > 3: bad.append("%s: Textur in der Plotfläche (Spreizung %.1f)" % (t, a))
            if b <= 3: bad.append("%s: außen keine Textur (%.1f) — Messung ungültig?" % (t, b))
    finally:
        pg.evaluate(C.SET, [s0, t0]); pg.wait_for_timeout(800)
    return (not bad), ("; ".join(bad) + " · " if bad else "") + " | ".join(got)

TESTS = [
    ("C29.P2 E29 Ziele/Kapitel: Kopf + Block auf der Achse", p2),
    ("C29.P3 E29 Hover-Info verschiebt nichts (0 px)", p3),
    ("C29.P4 E29 Infobox: Kopf allein, mittig, Text darunter", p4),
    ("C29.P5 E29 Feedback klein, kein Knopf", p5),
    ("C29.D6 E29 YOC skaliert mit der Lupe", d6),
    ("C29.D7 E29 Schrift: Standard +1 Stufe, --nbfs, unabhängig von der Lupe", d7),
    ("C29.D8 E29 Marker reingezoomt ein runder Kern", d8),
    ("C29.D10 E29 Plots ohne Textur", d10),
    ("C29.D5 E29 Vollbild: YOC/eigene Zellen auf der Achse", d5),
]

def main():
    nb = sys.argv[1]; C.NB = nb
    C.ENV = sys.argv[2] if len(sys.argv) > 2 else "lab"
    C.STORE = sys.argv[3] if len(sys.argv) > 3 else "fresh"
    only = os.environ.get("C29_ONLY", "")
    from playwright.sync_api import sync_playwright
    red = 0
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=C.CHROME)
        ctx, pg, errs = C.open_nb(b)
        # the last test (D5) makes an own cell, which changes the page: it runs
        # for both themes after the others
        last = TESTS[-1:]
        for part in (TESTS[:-1], last):
            for s, t in (("minimal", "light"), ("minimal", "dark")):
                pg.evaluate(C.SET, [s, t]); pg.wait_for_timeout(800)
                for name, fn in part:
                    if only and not any(o in name for o in only.split(",")): continue
                    ok, d = fn(pg, {"skin": s, "theme": t, "nb": nb})
                    red += not ok
                    print("%-4s %s %s/%s · %s" % ("ok" if ok else "RED", name.split()[0], s, t, d[:900]), flush=True)
        if errs: red += 1; print("RED Seitenfehler", errs[:3])
        b.close()
    print("css_e29: %d rot" % red); sys.exit(1 if red else 0)

if __name__ == "__main__":
    main()
