import sys as _sys, nbpick as _nbpick; _nbpick.argv_fix(_sys.argv)   # E28: ohne Angabe die Vorlage (--nb complex auf Zuruf)
"""E16.11 (2026-10-02) — WHAT EACH CONTENT BUILDS, headless.

    python3 tests/test_modes.py <notebook>

Runs the mega-cell once per mode (DIGICHEM_MODE) and checks the registries:
  plain  no exercise registered, no lock, no coding, the timeline has only
         title, groups, sections, chapters, figures, end and own cell, the
         time line says "text and figures"; every chapter of "both" is there
  E25.l  no mode has a quiz or own-data mark or exercise (MCQ and BYOD out,
         Nutzer 08.10.; behauptete bisher, E23.5: every mode has the quiz and
         own-data marks of "both")
  calc   no coding mark; code: no written exercise mark of a chapter
  both   unchanged: every exercise and coding mark
exit 0 = MODES OK."""
import json, sys, io, os, contextlib, subprocess
if len(sys.argv) > 2:                                  # child: one mode
    import matplotlib; matplotlib.use("Agg")
    import IPython.display as ipd; ipd.display = lambda *a, **k: None
    nb = json.load(open(sys.argv[1]))
    src = __import__("megasrc").expand("".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"]))
    src = "\n".join(l for l in src.splitlines() if not l.strip().startswith("%pip"))
    g = {"__name__": "__main__", "display": lambda *a, **k: None}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(src, "m", "exec"), g)
    print(json.dumps({"mode": g["MODE"]["value"], "tasks": g["_TASKS"]["order"],
                      "locks": len(g["_LOCKS"]), "code": sorted(g["_TASKS"]["has_code"]),
                      "kinds": [r[0] for r in g["card_timeline"]()],
                      "rows": [list(r[:3]) for r in g["card_timeline"]()],
                      "chapters": [r[1] for r in g["card_timeline"]() if r[0] == "chapter"],
                      "time": g["time_budget_text"]()}))
    sys.exit(0)
R = {}
for m in ("both", "calc", "code", "plain"):
    out = subprocess.run([sys.executable, __file__, sys.argv[1], m], capture_output=True, text=True,
                         env=dict(os.environ, DIGICHEM_MODE=m))
    R[m] = json.loads(out.stdout.strip().splitlines()[-1])
fails = []
def need(c, msg):
    if not c: fails.append(msg)
p, b = R["plain"], R["both"]
need(p["mode"] == "plain", "plain: built %s" % p["mode"])
need(p["tasks"] == [], "plain: exercises registered %s (want none)" % (p["tasks"],))
for m in ("both", "calc", "code", "plain"):
    qb = [r[1] for r in R[m]["rows"] if r[0] in ("quiz", "byod")]
    need(not qb, "E25.l %s: quiz/own-data marks %s (want none)" % (m, qb))
    need(not [t for t in R[m]["tasks"] if t in ("q1", "b1")], "E25.l %s: quiz/own-data exercises registered" % m)
need(p["locks"] == 0, "plain: %d locks" % p["locks"])
need(p["code"] == [], "plain: coding %s" % p["code"])
bad = sorted(set(p["kinds"]) - {"title", "group", "sub", "chapter", "figure", "end", "cell"})
need(not bad, "plain: timeline marks %s" % bad)
need(p["chapters"] == b["chapters"], "plain: chapters differ from both")
need(p["kinds"].count("figure") == b["kinds"].count("figure"), "plain: figures lost")
# E17.1 (02.10.): the line is in the run's language
need(("Text und Abbildungen" if __import__("os").environ.get("DIGICHEM_LANG") == "de"
      else "text and figures") in p["time"], "plain: time line %r" % p["time"])
need("coding" not in R["calc"]["kinds"], "calc: coding marks")
need("task" not in R["code"]["kinds"], "code: written exercise marks")
need(b["kinds"].count("task") >= 1 and b["kinds"].count("coding") >= 1 and b["locks"] > 0, "both: lost its exercises")
for m in R:
    print("%-5s exercises %2d · locks %2d · coding %2d · marks %2d · %s"
          % (m, len(R[m]["tasks"]), R[m]["locks"], len(R[m]["code"]), len(R[m]["kinds"]), R[m]["time"]))
print("MODES OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
sys.exit(1 if fails else 0)
