"""Shared by the Python workshop's regress tests (py_e21, py_e22): IS THE PAGE WHOLE?
(2026-10-07, E24 Stufe 2 Rest 2, Python; not a test module — run.py skips files
starting with "_".)

Measured in the v1.67 gate and here: after a page reload the front end restores
the widget models from the live kernel, and now and then it does not get them
all — the outputs then say "Error displaying widget: model not found" (the
kernel still holds every model: probed with a second client). In the gate the
reloads come from J23.pe (save, reload ×2, Run All when the panel is late), and
PY-R6i/R11/R13/E22.2a then read a document without its inbox, its end cards,
its exercise 1. The same happens with a notebook of plain ipywidgets and none
of our code (2 of 30 reloads), so it is the environment, not the notebook — and
not the subject of these tests. They now look first: a page that is not whole
is a precondition not reached (BAD), with what is missing and why, never a
plain "no inbox"."""

WHOLE = r"""() => { var ps = document.querySelectorAll('.jp-NotebookPanel'), P = null;
  for (var i = 0; i < ps.length; i++) if (!ps[i].classList.contains('lm-mod-hidden') && ps[i].getBoundingClientRect().width > 0) P = ps[i];
  if (!P) return {panelOfNb: false};
  var H = document.getElementById('nbpanel-root'), f = P.querySelectorAll('.nbfeed[data-nbid]');
  var err = [].filter.call(P.querySelectorAll('.jupyter-widgets'), function(e){
      return /^\s*Error displaying widget/.test(e.textContent || '') && !e.querySelector('.jupyter-widgets'); }).length;
  // a widget output is the one output node without a data-mime-type (JupyterLab
  // names every other kind); drawn, it holds the widget's view (.jupyter-widgets)
  var lost = [].filter.call(P.querySelectorAll('.jp-OutputArea-output'), function(o){
      return !o.hasAttribute('data-mime-type') && !o.querySelector('.jupyter-widgets') && !o.classList.contains('jupyter-widgets'); }).length;
  var inbox = P.querySelectorAll('.nbctl-modein input').length + (H ? H.querySelectorAll('.nbctl-modein input').length : 0);
  return {panelOfNb: true, err: err, lost: lost, inbox: inbox, panel: !!(H && H.querySelector('.nbmap')),
          ends: P.querySelectorAll('.nbend-mode').length, widgets: P.querySelectorAll('.jupyter-widgets').length,
          run: f.length ? f[f.length - 1].getAttribute('data-nbid') : null}; }"""

def page_whole(pg):
    """(True, state) when no widget output of the notebook in front lost its model;
    else (False, "BAD …") naming what is missing."""
    s = pg.evaluate(WHOLE)
    if s.get("panelOfNb") and (s["err"] or s["lost"]):
        # a view may still be on its way (a re-render): look again once
        pg.wait_for_timeout(2500); s = pg.evaluate(WHOLE)
    if not s.get("panelOfNb"):
        return False, "BAD no notebook in front"
    if s["err"] or s["lost"]:
        return False, ("BAD the page is not whole before this test: %d widget outputs without their view, "
                       "%d saying 'Error displaying widget: model not found' — the front end lost widget "
                       "models on a page reload (restore from the kernel; an earlier test reloads: J23.pe), "
                       "not this test's subject · inbox %d, panel %s, end cards %d, widgets %d, run %s"
                       % (s["lost"], s["err"], s["inbox"], s["panel"], s["ends"], s["widgets"], s["run"]))
    return True, s
