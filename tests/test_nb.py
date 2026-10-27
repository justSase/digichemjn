import sys as _sys, nbpick as _nbpick; _nbpick.argv_fix(_sys.argv)   # E28: ohne Angabe die Vorlage (--nb complex auf Zuruf)
import json, sys, io, contextlib
import matplotlib; matplotlib.use("Agg")
import IPython.display as ipd
ipd.display = lambda *a, **k: None          # stub: no frontend here
path = sys.argv[1]
nb = json.load(open(path))
src = __import__("megasrc").expand("".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"]))
src = "\n".join(l for l in src.splitlines() if not l.strip().startswith("%pip"))
g = {"__name__": "__main__", "display": lambda *a, **k: None}
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    exec(compile(src, path, "exec"), g)
print("EXEC OK", path, "| cells:", len(nb["cells"]), "| mega-cell chars:", len(src))
