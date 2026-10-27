"""Nach-Runde v1.65 — the JS workshop's regress test for the page error
"Cannot read properties of undefined (reading '0')" (2026-10-06; Kategorie
Applikation, Prüfwerkzeug). Module of tests/regress/run.py (TESTS = [(name, fn)]).
Real JupyterLab; the page's own errors (pageerror) are read.

  J23.pe  the notebook saved and the page reloaded twice (the outputs' scripts run
          again, kernel alive — as the reader reopens a saved notebook): 0 page
          errors during the reloads, and the panel is back after each (by itself,
          else after Run All — only once the page has stopped restoring its
          widgets, see below). The error was jupyterquiz's `version[0]` on
          `MathJax.version` (line 783 of its script, found with the debugger),
          after the guard of 2026-09-24be had run before JupyterLab set MathJax
          up. v1.65 (cyber dark, fresh): 1 error per reload, 4 of 4.
          Reloads the page: the last test of its module, and after it the panel
          is the one the reload brought back (the row's page errors count on).

A test that cannot reach its precondition returns False ("BAD …"), never True."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 2026-10-07 (E24 Stufe 2 Rest 2, JS) — RUN ALL ONLY WHEN THE PAGE HAS STOPPED
# RESTORING. Behauptete bisher: no panel 20 s after the reload → Run All. After
# a reload JupyterLab restores every widget model from the kernel (each run in
# the same kernel adds ~1 950, the old ones are never closed — Python, Rest 2);
# late in a row (J2 reran, three runs: ~5 800 models, under load) that takes
# longer than 26 s, and the Run All came while the page was still restoring.
# Python found it (chronicle 07.10., Rest 2): right after J23.pe the mode inbox
# `.nbctl-modein` was gone (3 widget nodes missing, same run) — PY-R6i "no
# inbox" and R11/R13 "the document's end missing" in the Tor came from here,
# not from J24.3; reproduced by them as a race (reload → Run All during the
# restore) in 3 of 4. Now: wait for the panel up to 120 s; Run All only if it
# has not come AND the page's widget count has stood still for 5 s (the
# restore is over; 15 s when it stands at 0: no restore began, measured after
# J2's restart + save, the first reload restored nothing in 120 s) — what a
# reader does who sees an empty page. How long it took is in the detail.
# Measured here (JS, after three runs in one kernel): the restore can also
# STOP short — 274 of 277 widget nodes, the inbox's 3 missing, no panel; the
# Run All after it brings all back. A restore that stops short and still
# brings the panel back would leave the inbox missing: that is the kernel's
# side (Python: old widgets closed at each run), and PY-R6i says it.
WCOUNT = "() => ({w: document.querySelectorAll('.jupyter-widgets').length, panel: !!document.querySelector('#nbpanel-root .nbmap')})"

def _settle(pg, limit=120.0):
    """after a reload: (panel?, seconds, widget count) — waits for the panel, or for the
    widget count to stand still with no panel (restore over: 5 s; nothing restored: 15 s)"""
    t0 = time.time(); last = None; since = time.time(); s = {"w": 0, "panel": False}
    while time.time() - t0 < limit:
        try: s = pg.evaluate(WCOUNT)
        except Exception: s = {"w": -1, "panel": False}
        if s["panel"]: return True, time.time() - t0, s["w"]
        if s["w"] != last: last = s["w"]; since = time.time()
        elif time.time() - since >= (5 if s["w"] > 0 else 15): return False, time.time() - t0, s["w"]
        pg.wait_for_timeout(500)
    return False, time.time() - t0, s["w"]

def reload_clean(pg, ctx):
    import run as R
    errs = ctx.get("errs") if isinstance(ctx.get("errs"), list) else None
    if errs is None: return False, "BAD no page-error list in ctx"
    n0 = len(errs); log = []
    for k in range(2):
        pg.keyboard.press("Escape"); pg.keyboard.press("Control+s"); pg.wait_for_timeout(1500)
        pg.reload(); pg.wait_for_timeout(1500)
        ok, dt, nw = _settle(pg)
        if ok: log.append("reload %d: panel back after %.0f s" % (k + 1, dt + 1.5))
        else:
            t = R.run_front(pg, ctx["id"]); log.append("reload %d: no panel, restore stopped at %d widgets after %.0f s → Run All %.0f s" % (k + 1, nw, dt + 1.5, t))
        pg.wait_for_timeout(3000)
    new = [e for e in errs[n0:] if e.startswith("pageerror")]
    if not pg.evaluate("() => !!document.querySelector('#nbpanel-root .nbmap')"): return False, "BAD no panel after the reloads · " + " · ".join(log)
    return not new, " · ".join(log) + " · page errors %d %s" % (len(new), [e[:120] for e in new[:2]])

TESTS = [("J23.pe no page error on reload", reload_clean)]
