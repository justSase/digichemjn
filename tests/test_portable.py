NBFILE=1
"""The progress code must survive a full round trip, and the panel must carry the
machine-readable snapshot the browser needs for the series view."""
import json, io, contextlib, re, sys
import matplotlib; matplotlib.use("Agg")
import IPython.display as ipd; ipd.display=lambda *a,**k: None
src="\n".join(l for l in __import__("megasrc").expand("".join(max(json.load(open(__import__("sys").argv[1] if len(__import__("sys").argv)>1 else "Complex_Numbers_Step_by_Step.ipynb"))
              ["cells"], key=lambda c: len("".join(c["source"])))["source"])).splitlines() if not l.strip().startswith("%pip"))
def fresh():
    G={"__name__":"__main__","display":lambda *a,**k:None}
    with contextlib.redirect_stdout(io.StringIO()): exec(compile(src,"m","exec"),G)
    return G
fails=[]
A=fresh()
print("notebook id:", A["NOTEBOOK"])
if A["NOTEBOOK"]["id"] == "unnamed": fails.append("the notebook has no identity")

# build a mixed state and export it
A["task_solved"]("t1"); A["task_code_solved"]("t1"); A["task_code_solved"]("t2")
A["task_skipped"]("t3"); A["task_solution_opened"]("t4"); A["task_solved"]("t5")
before = (dict(A["_TASKS"]["state"]), dict(A["_TASKS"]["code"]), A["_prog_counts"]())
code = A["progress_code"]()
print("progress code: %d chars — %s…" % (len(code), code[:44]))

# a second, untouched notebook restores it
B=fresh()
ok, msg = B["apply_progress_code"](code)
print("restore:", ok, "|", msg)
if not ok: fails.append("the code did not restore: %s" % msg)
after = (dict(B["_TASKS"]["state"]), dict(B["_TASKS"]["code"]), B["_prog_counts"]())
if before != after:
    fails.append("state after restore differs:\n  %s\n  %s" % (before, after))
else:
    print("state round-trips exactly:", before[2])
# locks that were settled must be open again
closed=[k for k in B["_TASKS"]["order"][:5]
        if B["_LOCKS"].get(("practice",k)) and not B["_LOCKS"][("practice",k)]["open"]]
print("locks still closed after restore:", closed)
if "t1" in closed or "t3" in closed: fails.append("restore did not re-open settled locks")

# garbage and foreign codes must be refused, not crash
for bad in ("hello", "", "!!!!", A["base64"].urlsafe_b64encode(b'{"n":"other","s":{},"c":{}}').decode()):
    ok2, m2 = B["apply_progress_code"](bad)
    if ok2: fails.append("a bad code was accepted: %r" % bad)
print("bad codes refused:", 4)

# the panel must carry the snapshot the browser reads
ph = B["_prog_html"]()
m = re.search(r"data-progress='([^']+)'", ph)
if not m: fails.append("the panel carries no data-progress snapshot")
else:
    snap = json.loads(m.group(1))
    print("snapshot:", snap)
    if snap["id"] != B["NOTEBOOK"]["id"]: fails.append("snapshot has the wrong notebook id")
    if snap["a"][1] != len(B["_TASKS"]["order"]): fails.append("snapshot totals are wrong")
if "nbseries" not in ph: fails.append("no series slot in the panel")

print("\n"+("PORTABLE PROGRESS OK" if not fails else "FAILURES:\n- "+"\n- ".join(fails)))
sys.exit(1 if fails else 0)
