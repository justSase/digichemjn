"""E23.18 — the JS workshop's regress test for E23.18 (2026-10-06; Kategorie
Applikation, Prüfwerkzeug). Module of tests/regress/run.py (TESTS = [(name, fn)],
fn(pg, ctx) -> (ok, detail)). Real JupyterLab, measured in the browser
(getBoundingClientRect, getComputedStyle).

  J23.18  scroll thumb = track × visible share of the document (Title … YOC)

A test that cannot reach its precondition returns False ("BAD …"), never True."""

FRONT = ".jp-NotebookPanel:not(.lm-mod-hidden)"
SC = "document.querySelector('%s .jp-WindowedPanel-outer')" % FRONT

# the document from the title card (the block the title mark lands on) to the end of the
# YOC strip (the notebook footer), on screen; the visible part = the scroller's box
SB_JS = r"""() => {
  var h = document.getElementById('nbpanel-root'); if (!h) return null;
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'); if (!P) return null;
  var sc = P.querySelector('.jp-WindowedPanel-outer'), sb = h.querySelector('.nbsb'), th = h.querySelector('.nbmap-cursor');
  var card = [].filter.call(P.querySelectorAll('.jp-OutputArea .nbtitle'), function(x){ return x.getBoundingClientRect().height > 4; })[0];
  var foot = P.querySelector('.jp-Notebook-footer');
  if (!sc || !sb || !th || !card || !foot) return {miss: [!!sc, !!sb, !!th, !!card, !!foot]};
  var a = card.getBoundingClientRect(), f = foot.getBoundingClientRect(), s = sb.getBoundingClientRect(), t = th.getBoundingClientRect();
  var doc = f.bottom - a.top, view = sc.getBoundingClientRect().height;
  return {track: s.height, thumb: t.height, doc: doc, view: view, share: Math.min(1, view / doc),
          vis: getComputedStyle(th).visibility, sbvis: getComputedStyle(sb).visibility,
          js: h.__nbSbShare, panel: h.querySelector('.nbrail') ? h.querySelector('.nbrail').getBoundingClientRect().width : null};
}"""

def _lens(pg, notches):
    pg.mouse.move(500, 450); pg.keyboard.press("Control+0"); pg.wait_for_timeout(500)
    if notches:
        pg.keyboard.down("Control")
        for _ in range(abs(notches)): pg.mouse.wheel(0, -100 if notches > 0 else 100); pg.wait_for_timeout(90)
        pg.keyboard.up("Control")
    pg.wait_for_timeout(1800)

TBODY = """() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var a = P && P.querySelector('.acc-title.acc-root .jupyter-widget-Collapse-contents');
  var t = document.querySelector('#nbpanel-root .nbmap-node[data-acc="title"]'); var r = t && t.getBoundingClientRect();
  return {body: a ? a.getBoundingClientRect().height : null, xy: r ? [r.left + r.width / 2, r.top + r.height / 2] : null}; }"""
def _title(pg, fold):
    """real clicks on the title mark (the first one may only choose it, E9.5) until the
    title body is folded (fold=True) or open"""
    tr = []
    pg.evaluate("()=>{var s=%s; s.scrollTop=0;}" % SC); pg.wait_for_timeout(1200)
    for _ in range(5):
        s = pg.evaluate(TBODY); tr.append((round(s["body"] or -1), s["xy"]))
        if s["body"] is None or not s["xy"]: return tr
        if (s["body"] <= 1) == fold: return True
        pg.mouse.click(*s["xy"]); pg.wait_for_timeout(2200)
    s = pg.evaluate(TBODY)
    return (s["body"] is not None and (s["body"] <= 1) == fold) or tr

def _row(pg, tag, rows, bad):
    m = pg.evaluate(SB_JS)
    if not m or "miss" in m:
        bad.append("%s BAD %s" % (tag, m)); return None
    want = max(24.0, min(m["track"], m["track"] * m["share"]))
    d = m["thumb"] - want
    rows.append("%s thumb %.0f want %.0f (track %.0f · share %.3f = %.0f/%.0f · js %s)" % (tag, m["thumb"], want, m["track"], m["share"], m["view"], m["doc"], m.get("js")))
    if abs(d) > 2: bad.append("%s thumb %.1f px ≠ track × share %.1f px" % (tag, m["thumb"], want))
    if m["vis"] != "visible": bad.append("%s thumb %s" % (tag, m["vis"]))
    return m

def thumb_share(pg, ctx):
    """E23.18: thumb length = track × (visible document height ÷ document from Title to the
    end of YOC), ±2 px (≥ 24 px): lens 60/100/150/max, Title open and folded, panel shut and
    wide; the panel width changes the thumb by 0 px; lens in → shorter, Title folded → longer."""
    pg.evaluate("()=>{var s=%s; s.scrollTop=Math.round((s.scrollHeight-s.clientHeight)*0.3);}" % SC)
    pg.wait_for_timeout(1200)
    rows, bad, th = [], [], {}
    for tag, n in (("60", -8), ("100", 0), ("150", 10), ("max", 40)):
        _lens(pg, n)
        m = _row(pg, "lens %s" % tag, rows, bad)
        if m: th[tag] = m["thumb"]
    if len(th) == 4 and not (th["60"] >= th["100"] >= th["150"] >= th["max"] and th["60"] > th["max"]):
        bad.append("thumb does not shrink with the lens %s" % th)
    _lens(pg, 0)
    m0 = _row(pg, "panel shut", rows, bad)
    pg.evaluate("()=>{ window.__nbSetGui && window.__nbSetGui(100); }"); pg.wait_for_timeout(1500)
    m1 = _row(pg, "panel wide", rows, bad)
    if m0 and m1:
        if not (m1["panel"] and m0["panel"] and m1["panel"] > m0["panel"] + 30):
            bad.append("BAD panel did not widen (%s → %s)" % (m0["panel"], m1["panel"]))
        if abs(m1["thumb"] - m0["thumb"]) > 0.5:
            bad.append("panel width moves the thumb %.1f → %.1f px" % (m0["thumb"], m1["thumb"]))
    pg.evaluate("()=>{ window.__nbSetGui && window.__nbSetGui(0); }"); pg.wait_for_timeout(1200)
    r = _title(pg, True)
    if r is not True: bad.append("BAD title does not fold %s" % (r,))
    pg.mouse.move(5, 450); pg.wait_for_timeout(600)
    m2 = _row(pg, "title folded", rows, bad)
    r = _title(pg, False)
    if r is not True: bad.append("BAD title does not open %s" % (r,))
    pg.mouse.move(5, 450); pg.wait_for_timeout(600)
    m3 = _row(pg, "title open", rows, bad)
    if m2 and m3 and not (m2["thumb"] > m3["thumb"] + 2 or m2["thumb"] >= m2["track"] - 2):
        bad.append("folding the title does not lengthen the thumb (%.0f vs %.0f)" % (m2["thumb"], m3["thumb"]))
    # E12.3: dragging stays proportional — thumb travel (track − thumb) maps onto the range
    _lens(pg, 0)
    pg.evaluate("()=>{var s=%s; s.scrollTop=Math.round((s.scrollHeight-s.clientHeight)*0.2);}" % SC); pg.wait_for_timeout(1500)
    d = pg.evaluate("""()=>{ var h=document.getElementById('nbpanel-root'), t=h.querySelector('.nbmap-cursor'), sb=h.querySelector('.nbsb'), r=t.getBoundingClientRect(), q=sb.getBoundingClientRect();
      var s=document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer');
      return {x: r.left + r.width / 2, y: r.top + r.height / 2, trav: q.height - r.height, span: s.scrollHeight - s.clientHeight - Math.max(0, window.__nbTopAt || 0), st: s.scrollTop}; }""")
    pg.mouse.move(d["x"], d["y"]); pg.mouse.down()
    for i in range(1, 11): pg.mouse.move(d["x"], d["y"] + 6 * i); pg.wait_for_timeout(30)
    pg.mouse.up(); pg.wait_for_timeout(900)
    st = pg.evaluate("()=>%s.scrollTop" % SC)
    want = 60.0 * d["span"] / max(1, d["trav"])
    rows.append("drag 60 px → %.0f px of page (want %.0f)" % (st - d["st"], want))
    if abs((st - d["st"]) - want) > max(4, 0.04 * want): bad.append("drag not proportional: %.0f vs %.0f px" % (st - d["st"], want))
    return (not bad), ("; ".join(bad) + " | " if bad else "") + " · ".join(rows)

TESTS = [("J23.18 scroll thumb = visible share", thumb_share)]
