"""E23.10 — the JS workshop's regress test (2026-10-06; Kategorie Applikation,
Prüfwerkzeug). Module of tests/regress/run.py (TESTS = [(name, fn)]). Real
JupyterLab, measured in the browser (getBoundingClientRect, elementFromPoint).
Belongs with css-E23.10 (the document keeps the corner free; the cell is a 720-px
column): the JS half takes its own margin (E21.3c/E22.8) away.

  J23.10  a cell of one's own, made through the YOC mark (hover, click), stands on
          the main axis: |middle − middle of the title card| ≤ 1 px, and is as wide
          as the other blocks: |width − YOC strip| ≤ 1 px, at lens 100 also = the title
          card (720 px; above ~135 % the card keeps its own cap); no inline margin
          of ours on it; lens 60/100/150 %. And the tool corner (signs, lens) lies
          over none of its points (grid 16 × 6, top/middle/end of the page and the
          cell scrolled up under the lens). Changes the notebook: last.
          Nach-Runde 06.10.: a point counts where the cell is DRAWN (inside the
          scroller and its clip-path — css-E23.10 cuts the lens strip out).
          Behauptete bisher: every point of the cell's box — red at lens 151 with
          two own cells at the page's end (tor C23.10, row 1), where the cell is
          cut away under the strip. A corner over a drawn cell stays red.

A test that cannot reach its precondition returns False ("BAD …"), never True."""
import json

FRONT = ".jp-NotebookPanel:not(.lm-mod-hidden)"
YOC = """() => { var m = document.querySelector('#nbpanel-root .nbmap-node.cell[data-acc="yoc"]');
  var t = m && (m.querySelector('.nbsect') || m), r = t ? t.getBoundingClientRect() : null;
  return {xy: r && r.width ? [r.left + r.width / 2, r.top + r.height / 2] : null}; }"""
OWN = """() => { var P = document.querySelector('%s');
  var card = [].filter.call(P.querySelectorAll('.jp-OutputArea .nbtitle-card'), function(x){ return x.getBoundingClientRect().height > 4; })[0];
  var own = [].slice.call(P.querySelectorAll('.jp-Cell[class*="nbown-"]')).filter(function(c){ return c.getBoundingClientRect().height > 4; });
  var cr = card && card.getBoundingClientRect(), f = P.querySelector('.jp-Notebook-footer'), fr = f && f.getBoundingClientRect();
  return {card: cr ? [cr.left + cr.width / 2, cr.width] : null, foot: fr && fr.width ? fr.width : null,
          own: own.map(function(c){ var q = c.getBoundingClientRect(); return [q.left + q.width / 2, q.width, c.style.marginLeft || '', c.style.marginRight || '']; })}; }""" % FRONT
CORNER = r"""() => { var P = document.querySelector('%s'), h = document.getElementById('nbpanel-root');
  var skip = [].map.call(h ? h.querySelectorAll('.nbrail, .nbgrip, .nbsb') : [], function(e){ return e.getBoundingClientRect(); })
               .filter(function(r){ return r.width > 0 && r.height > 0; });
  // E23.10 Nach-Runde: a point counts only where the cell is DRAWN — inside the
  // scroller's box and inside its clip-path (css-E23.10 cuts the lens strip out:
  // what scrolls under it is not painted there and takes no click there)
  var so = P.querySelector('.jp-WindowedPanel-outer'), sr = so.getBoundingClientRect();
  var cpv = getComputedStyle(so).clipPath || 'none', poly = null, pm = /^polygon\((.*)\)$/.exec(cpv);
  if (pm) poly = pm[1].split(',').map(function(p){ var v = p.trim().split(/\s+/);
    var f = function(s, L){ return /%%$/.test(s) ? parseFloat(s) / 100 * L : parseFloat(s); };
    return [sr.left + f(v[0], sr.width), sr.top + f(v[1], sr.height)]; });
  var drawn = function(x, y){
    if (x < sr.left || x > sr.right || y < sr.top || y > sr.bottom) return false;
    if (!poly) return true;
    var inside = false;
    for (var a = 0, b = poly.length - 1; a < poly.length; b = a++) {
      var xa = poly[a][0], ya = poly[a][1], xb = poly[b][0], yb = poly[b][1];
      if ((ya > y) !== (yb > y) && x < (xb - xa) * (y - ya) / (yb - ya) + xa) inside = !inside; }
    return inside; };
  var vh = window.innerHeight, bad = [], n = 0;
  P.querySelectorAll('.jp-Cell[class*="nbown-"]').forEach(function(c){
    var r = c.getBoundingClientRect(), t = Math.max(r.top, 60), b = Math.min(r.bottom, vh - 30);
    if (b - t < 6 || r.width < 6) return;
    for (var i = 0; i < 16; i++) for (var j = 0; j < 6; j++) {
      var x = r.left + 2 + (r.width - 4) * i / 15, y = t + 2 + (b - t - 4) * j / 5;
      if (skip.some(function(q){ return x >= q.left - 2 && x <= q.right + 2 && y >= q.top - 2 && y <= q.bottom + 2; })) continue;
      if (!drawn(x, y)) continue;
      n++; var e = document.elementFromPoint(x, y);
      if (e && e.closest('#nbpanel-root')) bad.push(e.tagName + '.' + String(e.className).split(' ')[0] + ' (' + Math.round(x) + ',' + Math.round(y) + ')'); } });
  return {n: n, bad: bad}; }""" % FRONT
SC = "document.querySelector('%s .jp-WindowedPanel-outer')" % FRONT

def _lens(pg, n):
    pg.mouse.move(700, 450); pg.keyboard.press("Control+0"); pg.wait_for_timeout(400)
    if n:
        pg.keyboard.down("Control")
        for _ in range(abs(n)): pg.mouse.wheel(0, -100 if n > 0 else 100); pg.wait_for_timeout(90)
        pg.keyboard.up("Control")
    pg.wait_for_timeout(1600)

def _make_own(pg):
    for _ in range(3):
        if pg.evaluate(OWN)["own"]: return True
        pg.keyboard.press("Escape")
        pg.evaluate("() => { var n = %s; if (n) n.scrollTop = n.scrollHeight; }" % SC); pg.wait_for_timeout(1500)
        y = pg.evaluate(YOC)
        if y["xy"]:
            pg.mouse.move(y["xy"][0] - 40, y["xy"][1] - 40); pg.wait_for_timeout(300)
            y = pg.evaluate(YOC); pg.mouse.move(*y["xy"], steps=4); pg.wait_for_timeout(600)
            pg.mouse.click(*y["xy"]); pg.wait_for_timeout(2500); pg.keyboard.press("Escape"); pg.mouse.move(700, 450)
    return bool(pg.evaluate(OWN)["own"])

def own_axis(pg, ctx):
    if not _make_own(pg): return False, "BAD no own cell made"
    bad, got = [], []
    try:
        for tag, n in (("100", 0), ("60", -8), ("150", 10)):
            _lens(pg, n)
            pg.evaluate("() => { var n = %s; if (n) n.scrollTop = n.scrollHeight; }" % SC); pg.wait_for_timeout(1200)
            d = pg.evaluate(OWN)
            for _ in range(10):                # settled: two reads 400 ms apart agree
                pg.wait_for_timeout(400); d2 = pg.evaluate(OWN)
                same = json.dumps(d2) == json.dumps(d); d = d2
                if same: break
            if not d["card"] or not d["own"]: bad.append("BAD lens %s not measured %s" % (tag, d)); continue
            for o in d["own"]:
                dm, dw = o[0] - d["card"][0], o[1] - (d["foot"] or 0)
                got.append("lens %s: middle %+.1f, width %.0f/%s" % (tag, dm, o[1], d["foot"]))
                if abs(dm) > 1: bad.append("lens %s: middle %+.1f px off the axis" % (tag, dm))
                if abs(dw) > 1: bad.append("lens %s: width %.0f, the YOC strip %s" % (tag, o[1], d["foot"]))
                # the column of every block: 720 px × lens, at most the cells' column (the title
                # card keeps its own cap at a high lens and is not the measure there)
                if tag == "100" and abs(o[1] - d["card"][1]) > 1: bad.append("lens 100: width %.0f, the title card %.0f" % (o[1], d["card"][1]))
                if o[2] or o[3]: bad.append("lens %s: inline margin %s/%s" % (tag, o[2], o[3]))
            for frac in (0.0, 0.5, 1.0):
                pg.evaluate("(f) => { var o = %s; o.scrollTop = f * (o.scrollHeight - o.clientHeight); }" % SC, frac)
                pg.wait_for_timeout(900)
                c = pg.evaluate(CORNER)
                if c["bad"]: bad.append("lens %s, at %.1f: corner over the cell %s" % (tag, frac, c["bad"][:2]))
            pg.evaluate("() => { var P = document.querySelector('%s'), o = P.querySelector('.jp-WindowedPanel-outer'), c = P.querySelector('.jp-Cell[class*=\\\"nbown-\\\"]');"
                        " var g = document.querySelector('#nbpanel-root .nbcorner .nbzoomgrp, #nbpanel-root .nbcorner .nbbtn'); var gy = g ? g.getBoundingClientRect().top + 6 : 110;"
                        " o.scrollTop += c.getBoundingClientRect().top - gy; }" % FRONT)
            pg.wait_for_timeout(900)
            c = pg.evaluate(CORNER)
            if c["bad"]: bad.append("lens %s, under the corner: %s" % (tag, c["bad"][:2]))
    finally:
        _lens(pg, 0)
    return (not bad), ("; ".join(bad[:5]) + " | " if bad else "") + " · ".join(got)

TESTS = [("J23.10 own cell on the main axis", own_axis)]
