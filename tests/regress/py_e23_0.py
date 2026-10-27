"""E23.0 / E23.16 · test_regress — the Python workshop's part of E23.0 and 16a/b.

In the matrix (TESTS, every row, real JupyterLab after Run All):
  PY-E23.0  THE ONE-CELL STRUCTURE SURVIVES A SLIP, AND SAYS WHAT TO DO.
            del   a control cell is inserted (palette "Insert Cell Below"), then
                  "Select All Cells" + "Delete Cells": the control cell (and
                  every own cell) is gone — the delete ran — and the two cells
                  of the notebook stay, title (md) and mega-cell (code)
            gone  palette "Clear Outputs of All Cells" (the reader's slip, or a
                  copy saved without outputs): no feed left (precondition);
                  in the notebook area, what is VISIBLE (box > 0, inside the
                  window, opacity > 0) says what to do in both languages —
                  "Play" and "Run All", and the German "Dokument"
            back  Run All again: the document is back, and the progress
                  (answered / coding / skipped counts of the feed), the mode
                  and the language are what they were before the slip (E23.16b:
                  no state lives only in the output)
            v1.63: after Clear All Outputs the only visible line was
            "#@title DigiChemJN · Setup, installs packages, …" (the title cell
            stays out of the flow) → "gone" red. Owner: Python (cell text,
            metadata, kernel state); bringing the cover back is JS/CSS.
            Changes the notebook (clears and reruns it): the last test of its
            module; py_e23_9 after it waits for nothing (the run is complete).
exit: run through tests/regress/run.py."""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))

FRONT = "var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');"
STATE_JS = """() => { """ + FRONT + """
  if (!P) return null;
  var f = P.querySelectorAll('.nbfeed[data-progress]'), last = f.length ? f[f.length - 1] : null, pr = {};
  try { pr = JSON.parse(last.getAttribute('data-progress')); } catch (e) {}
  var cs = P.querySelectorAll('.jp-Notebook .jp-Cell');
  return {cells: cs.length, kinds: [].map.call(cs, function(c){ return c.classList.contains('jp-MarkdownCell') ? 'md' : 'code'; }).join(','), feeds: f.length,
          a: pr.a || null, c: pr.c || null, s: pr.s || null, mode: last && last.getAttribute('data-nbmode'),
          lang: last && last.getAttribute('data-nblang')}; }"""
SEEN_JS = """() => { """ + FRONT + """
  if (!P) return '';
  var nb = P.querySelector('.jp-Notebook') || P, W = innerWidth, H = innerHeight, out = [];
  var tw = document.createTreeWalker(nb, NodeFilter.SHOW_TEXT, null), n;
  while ((n = tw.nextNode())) {
    var t = n.nodeValue.trim(); if (!t) continue;
    var e = n.parentElement, r = document.createRange(); r.selectNodeContents(n);
    var b = r.getBoundingClientRect();
    if (b.width < 1 || b.height < 1 || b.bottom < 0 || b.top > H || b.right < 0 || b.left > W) continue;
    var cs = getComputedStyle(e); if (cs.visibility === 'hidden' || +cs.opacity === 0) continue;
    out.push(t); }
  return out.join(' '); }"""

def t_e23_0(pg, ctx):
    import run as R
    s0 = pg.evaluate(STATE_JS)
    if not s0 or not s0["feeds"]: return False, "BAD no document before the slip"
    det = []
    # del: both cells are locked. A control cell of the reader's kind is put in
    # first (palette "Insert Cell Below"): Delete must take it — and every other
    # cell of one's own an earlier test made — so a delete that never ran
    # cannot pass as "protected".
    pg.click(".lm-DockPanel .lm-TabBar-tab.lm-mod-current"); pg.keyboard.press("Escape")
    ins = R.palette(pg, "Insert Cell Below"); pg.wait_for_timeout(800)
    sA = pg.evaluate(STATE_JS)
    ok1 = R.palette(pg, "Select All Cells"); pg.wait_for_timeout(400)
    pg.keyboard.press("Control+Shift+C")                      # not through palette(): its click on the tab drops the selection
    ok2 = False
    try:
        pg.wait_for_function("() => { var i = document.activeElement; return !!(i && i.classList && i.classList.contains('lm-CommandPalette-input')); }", timeout=8000)
        pg.keyboard.type("Delete Cell")
        pg.wait_for_function("() => { var a = document.querySelector('.lm-CommandPalette-item.lm-mod-active .lm-CommandPalette-itemLabel'); return !!(a && /^Delete Cells?$/.test(a.textContent.trim())); }", timeout=8000)
        pg.keyboard.press("Enter"); ok2 = True
    except Exception:
        pg.keyboard.press("Escape")
    pg.wait_for_timeout(1500)
    if pg.query_selector(".jp-Dialog"):
        pg.keyboard.press("Escape"); pg.wait_for_timeout(500)
    s1 = pg.evaluate(STATE_JS)
    det.append("delete (insert %s: %d cells, select all %s, Delete %s): %d → %d cells %s" % (
        ins, sA["cells"], ok1, ok2, sA["cells"], s1["cells"], s1["kinds"]))
    # gone: Clear Outputs of All Cells
    if not R.palette(pg, "Clear Outputs of All Cells"): return False, "BAD palette: Clear Outputs of All Cells"
    pg.wait_for_timeout(2500)
    pg.evaluate("() => { " + FRONT + " var o = P && P.querySelector('.jp-WindowedPanel-outer'); if (o) o.scrollTop = 0; }")
    pg.wait_for_timeout(1500)
    s2 = pg.evaluate(STATE_JS)
    seen = pg.evaluate(SEEN_JS)
    says = all(w in seen for w in ("Play", "Run All", "Dokument"))
    det.append("cleared: %d feeds, visible %r" % (s2["feeds"], seen[:110]))
    # back: Run All, as the line says
    t = R.run_front(pg, ctx["id"])
    s3 = None
    for _ in range(20):
        s3 = pg.evaluate(STATE_JS)
        if s3 and s3["feeds"]: break
        pg.wait_for_timeout(1000)
    same = s3 and all(s3[k] == s0[k] for k in ("a", "c", "s", "mode", "lang"))
    det.append("rerun %.0f s: progress a%s c%s s%s %s/%s → a%s c%s s%s %s/%s" % (
        t, s0["a"], s0["c"], s0["s"], s0["mode"], s0["lang"],
        s3 and s3["a"], s3 and s3["c"], s3 and s3["s"], s3 and s3["mode"], s3 and s3["lang"]))
    ok = (ins and ok2 and sA["cells"] > 2 and s1["cells"] == 2 and s1["kinds"] == "md,code"
          and s2["feeds"] == 0 and says and bool(same))
    return ok, " · ".join(det)

TESTS = [("PY-E23.0 one cell survives Delete/Clear, says Play", t_e23_0)]
