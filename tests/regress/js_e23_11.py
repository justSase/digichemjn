"""E23.11 — the JS workshop's regress test (2026-10-06; Kategorie Applikation,
Prüfwerkzeug). Module of tests/regress/run.py (TESTS = [(name, fn)]). Real
JupyterLab, measured in the browser (getBoundingClientRect).

  J23.11  the timeline panel opens at most to the document's main axis (the middle
          of the title card): pulled out as far as it goes, its left edge stands on
          the axis — never left of it (≥ axis − 0.5 px) and not short of it
          (≤ axis + 1 px); file browser open and shut, lens 60/100/150/max, window
          1400 and 1100 px wide. Back to shut at the end.

A test that cannot reach its precondition returns False ("BAD …"), never True."""

M = r"""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), h = document.getElementById('nbpanel-root');
  if (!P || !h) return null;
  var c = [].filter.call(P.querySelectorAll('.jp-OutputArea .nbtitle-card'), function(x){ return x.getBoundingClientRect().height > 4; })[0];
  var r = h.querySelector('.nbrail'); if (!c || !r) return null;
  var q = c.getBoundingClientRect(), rr = r.getBoundingClientRect();
  return {axis: q.left + q.width / 2, left: rr.left, w: rr.width, gui: window.__nbGui}; }"""

def _lens(pg, n):
    pg.mouse.move(500, 450); pg.keyboard.press("Control+0"); pg.wait_for_timeout(400)
    if n:
        pg.keyboard.down("Control")
        for _ in range(abs(n)): pg.mouse.wheel(0, -100 if n > 0 else 100); pg.wait_for_timeout(90)
        pg.keyboard.up("Control")
    pg.wait_for_timeout(1500)

def _far(pg, tag, rows, bad):
    pg.evaluate("() => { window.__nbSetGui && window.__nbSetGui(99999); }"); pg.wait_for_timeout(1200)
    m = pg.evaluate(M)
    if not m: bad.append("%s BAD not measured" % tag); return
    d = m["left"] - m["axis"]
    rows.append("%s %+.1f" % (tag, d))
    if d < -0.5: bad.append("%s: panel %.1f px past the axis" % (tag, -d))
    elif d > 1: bad.append("%s: panel stops %.1f px short of the axis" % (tag, d))

def axis_far(pg, ctx):
    rows, bad = [], []
    vs = pg.viewport_size
    try:
        for tag, n in (("100", 0), ("60", -8), ("150", 10), ("max", 40)):
            _lens(pg, n); _far(pg, "fb open · lens " + tag, rows, bad)
        _lens(pg, 0)
        pg.keyboard.press("Control+b"); pg.wait_for_timeout(1500)
        _far(pg, "fb shut · lens 100", rows, bad)
        _lens(pg, 10); _far(pg, "fb shut · lens 150", rows, bad)
        _lens(pg, 0)
        pg.keyboard.press("Control+b"); pg.wait_for_timeout(1500)
        pg.set_viewport_size({"width": 1100, "height": vs["height"]}); pg.wait_for_timeout(2000)
        _far(pg, "1100 px · lens 100", rows, bad)
    finally:
        pg.set_viewport_size(vs); pg.wait_for_timeout(1200)
        pg.evaluate("() => { window.__nbSetGui && window.__nbSetGui(0); }"); pg.wait_for_timeout(600)
        _lens(pg, 0)
    return (not bad), ("; ".join(bad) + " | " if bad else "") + "left edge − axis: " + " · ".join(rows)

TESTS = [("J23.11 panel opens to the main axis", axis_far)]
