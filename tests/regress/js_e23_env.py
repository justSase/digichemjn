"""E23.11/E23.18 Nach-Runde — the JS workshop's regress test (2026-10-06;
Kategorie Applikation, Prüfwerkzeug). Module of tests/regress/run.py
(TESTS = [(name, fn)], fn(pg, ctx) -> (ok, detail)). Real JupyterLab, measured
in the browser (getComputedStyle, getBoundingClientRect).

  J23.env  the page follows the kernel's word back: the feed says "pycharm"
           (the front end's word, `.nbfeed[data-nbenv]`) and the page asks for
           it once (Play's way-message does, E22.3) — <html> data-nbui="frame";
           then the word is the kernel's own again (as after a rerun elsewhere).
           Without anyone asking, within 3 s: <html> data-nbenv/data-nbui say
           lab, and the panel is docked again: rail, grip and scroll bar drawn
           (display not none, box > 0). The cache of nbEnv is NOT cleared by the
           test (the reader's page does not do that either).
           v1.65 + js-E23.11/E23.18: <html> stayed on "frame", rail hidden — and
           the tor rows J23.11 (826 px) and J23.18 (thumb 0 px) after J22.3 red.

A test that cannot reach its precondition returns False ("BAD …"), never True."""

ST = r"""() => { var R = document.documentElement, h = document.getElementById('nbpanel-root');
  var d = function(s){ var e = h && h.querySelector(s); if (!e) return null; var c = getComputedStyle(e), r = e.getBoundingClientRect();
    return c.display !== 'none' && r.width > 0 && r.height > 0; };
  return {env: R.getAttribute('data-nbenv'), ui: R.getAttribute('data-nbui'), rail: d('.nbrail'), grip: d('.nbgrip'), sb: d('.nbsb')}; }"""

def env_back(pg, ctx):
    s0 = pg.evaluate(ST)
    if s0["ui"] != "lab" or not s0["rail"]: return False, "BAD not docked before: %s" % s0
    w = pg.evaluate("""() => { var f = document.querySelectorAll('.nbfeed[data-nbenv]'); if (!f.length) return null;
      var w0 = f[0].getAttribute('data-nbenv'); window.__j23env = w0;
      f.forEach(function(x){ x.setAttribute('data-nbenv', 'pycharm'); });
      var v = window.__nbEnv ? window.__nbEnv() : null; return [w0, v && v.env, v && v.ui]; }""")
    if not w: return False, "BAD no .nbfeed[data-nbenv]"
    s1 = pg.evaluate(ST)
    if s1["ui"] != "frame":
        pg.evaluate("() => { document.querySelectorAll('.nbfeed[data-nbenv]').forEach(function(x){ x.setAttribute('data-nbenv', window.__j23env); }); }")
        return False, "BAD the page did not take the word pycharm (%s · %s)" % (w, s1)
    pg.evaluate("() => { document.querySelectorAll('.nbfeed[data-nbenv]').forEach(function(x){ x.setAttribute('data-nbenv', window.__j23env); }); }")
    seq = []
    for _ in range(6):
        pg.wait_for_timeout(500); seq.append(pg.evaluate(ST))
    s2 = seq[-1]
    ok = s2["env"] == s0["env"] and s2["ui"] == "lab" and s2["rail"] and s2["grip"] and s2["sb"]
    t = next((i for i, s in enumerate(seq) if s["ui"] == "lab"), None)
    if not ok:     # leave the page as it was for the tests after this one
        pg.evaluate("() => { window.__nbEnvV = null; window.__nbEnv && window.__nbEnv(); }"); pg.wait_for_timeout(800)
    return ok, "word %s → pycharm (%s/%s) → %s: after %s ms %s" % (w[0], s1["env"], s1["ui"], w[0],
        (t + 1) * 500 if t is not None else ">3000", {k: s2[k] for k in ("env", "ui", "rail", "grip", "sb")})

TESTS = [("J23.env page follows the kernel's word back", env_back)]
