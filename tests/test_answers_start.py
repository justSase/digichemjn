"""Every no-code answer in notebook 0 must accept the right answer and reject a wrong one."""
import json, io, contextlib, sys, re
import matplotlib; matplotlib.use("Agg")
import IPython.display as ipd; ipd.display=lambda *a,**k: None
p = sys.argv[1] if len(sys.argv)>1 else "Start_Here_How_These_Notebooks_Work.ipynb"
src="\n".join(l for l in __import__("megasrc").expand("".join(max(json.load(open(p))["cells"], key=lambda c: len("".join(c["source"])))["source"])).splitlines()
              if not l.strip().startswith("%pip"))
G={"__name__":"__main__","display":lambda *a,**k:None}
with contextlib.redirect_stdout(io.StringIO()): exec(compile(src,"m","exec"),G)
TV=G["TV"]; fails=[]
C,S,K,F = TV["chapters"],TV["solved"],TV["skipped"],TV["failed"]
CASES=[
 ("_ans_c01","choice",0,[1,2,3]),
 ("_ans_c02","choice",2,[0,1,3]),
 ("_ans_c04","choice",1,[0,2,3]),
 ("_ans_c06","choice",2,[0,1,3]),
 ("_ans_c07","choice",1,[0,2,3]),
 ("_ans_c03","num",{"open":C-S-K-F,"pct":100.0*S/C},
              [{"open":C-S,"pct":100.0*S/C},{"open":C-S-K-F,"pct":100.0*(S+K)/C}]),
 ("_ans_c05","num",{"text":80,"dots":35},
              [{"text":85,"dots":35},{"text":80,"dots":50}]),
]
for name,kind,good,bads in CASES:
    fn=G.get(name)
    if fn is None: fails.append("%s missing" % name); continue
    ok,tip = fn(good,"") if kind=="choice" else fn(good)
    print("%-10s right -> %-5s %s" % (name, ok, "" if ok else "TIP: "+re.sub("<[^>]+>","",str(tip))[:80]))
    if not ok: fails.append("%s rejects the correct answer: %s" % (name,tip))
    for b in bads:
        ok2,tip2 = fn(b,"") if kind=="choice" else fn(b)
        if ok2: fails.append("%s accepted a wrong answer %r" % (name,b))
        else:   print("%-10s wrong -> hint: %s" % (name, re.sub("<[^>]+>","",str(tip2))[:88]))
print("\n"+("START ANSWERS OK" if not fails else "FAILURES:\n- "+"\n- ".join(fails)))
sys.exit(1 if fails else 0)
