import sys as _sys, nbpick as _nbpick; _nbpick.argv_fix(_sys.argv)   # E28: ohne Angabe die Vorlage (--nb complex auf Zuruf)
"""E17.5 — merging an account's progress never lowers a state.
    python3 tests/test_merge.py <notebook.ipynb>
Builds two states in the kernel (exec), merges the code of one into the
other and checks every exercise: solved > skipped > wrong > open."""
import json, sys, io, contextlib
import matplotlib; matplotlib.use("Agg")
import IPython.display as ipd; ipd.display = lambda *a, **k: None
nb = json.load(open(sys.argv[1]))
src = __import__("megasrc").expand("".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"]))
g = {"__name__": "__main__", "display": lambda *a, **k: None}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src, "m", "exec"), g)
T, order = g["_TASKS"], g["_TASKS"]["order"]
R = {"open": 0, "fail": 1, "skip": 2, "done": 3}
cyc = ["open", "fail", "skip", "done"]
fails = []
def setall(sa, sc):
    for n, k in enumerate(order):
        T["state"][k] = sa[n]; T["code"][k] = sc[n]
A = ([cyc[n % 4] for n in range(len(order))], [cyc[(n + 1) % 4] for n in range(len(order))])
B = ([cyc[(n + 2) % 4] for n in range(len(order))], [cyc[(3 * n) % 4] for n in range(len(order))])
setall(*B); code_b = g["progress_code"]()
setall(*A)
ok, msg = g["merge_progress_code"](code_b)
if not ok: fails.append("merge refused: " + msg)
for n, k in enumerate(order):
    for route, a, b in (("state", A[0][n], B[0][n]), ("code", A[1][n], B[1][n])):
        want = a if R[a] >= R[b] else b
        if T[route][k] != want:
            fails.append("%s %s: %s + %s → %s, want %s" % (k, route, a, b, T[route][k], want))
before = dict(T["state"])
ok2, msg2 = g["merge_progress_code"]("not-a-code")
if ok2 or dict(T["state"]) != before: fails.append("a broken code changed the state")
print("%d exercises × 2 routes merged; broken code: %s" % (len(order), msg2))
print("MERGE OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
sys.exit(1 if fails else 0)
