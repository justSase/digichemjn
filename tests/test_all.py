"""Cross-notebook check: one toolkit, three notebooks, the right profile each,
and no plot left with un-themed (invisible-on-dark) axes."""
import json, io, contextlib, sys, hashlib
import matplotlib; matplotlib.use("Agg")
import IPython.display as ipd; ipd.display=lambda *a,**k: None
NBS = [("ml/Machine_Learning_LLMs_AI_Step_by_Step.ipynb", "bioinformatics"),
       ("modeling/Introduction_to_Modeling.ipynb",        "biophysics"),
       ("complex/Complex_Numbers_Step_by_Step.ipynb",     "biophysics")]
sys.path.insert(0, "toolkit"); sys.dont_write_bytecode = True
from assemble import template
tpl = template()   # 2026-09-28 (S): chapter_template.py + css/ + js/
tpl_hash = hashlib.sha256(tpl.encode()).hexdigest()[:12]
fails=[]
for path, want in NBS:
    src="\n".join(l for l in __import__("megasrc").expand("".join(max(json.load(open(path))["cells"], key=lambda c: len("".join(c["source"])))["source"])).splitlines()
                  if not l.strip().startswith("%pip"))
    if tpl not in src:
        fails.append("%s does not embed the shared toolkit" % path)
    G={"__name__":"__main__","display":lambda *a,**k:None}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(src,"m","exec"),G)
    got = G["PROFILE"]["name"] if "name" in G["PROFILE"] else G["PROFILE"].get("label","?").lower()
    code = G["PROFILE"]["requires_code"]; objs = G["PROFILE"]["objectives"]
    d, t, c, ct = G["_prog_counts"]()
    print("%-46s profile=%-15s id=%-16s exercises=%d"
          % (path.split("/")[-1], G["PROFILE"]["label"], G["NOTEBOOK"]["id"], t))
    if G["NOTEBOOK"]["id"] == "unnamed":
        fails.append("%s has no notebook id — it cannot appear in the series view" % path)
    if t == 0:
        print("      NOTE: no registered exercises, so it contributes 0/0 to the series total")
    if G["PROFILE"]["label"].lower() != want:
        fails.append("%s: profile is %r, expected %r" % (path, G["PROFILE"]["label"], want))
    if want == "biophysics" and "K2" in objs:
        fails.append("%s: biophysics standard still lists K2" % path)
    if want == "bioinformatics" and "K2" not in objs:
        fails.append("%s: bioinformatics standard lost K2" % path)
    # every figure produced by this notebook must have themed axes
    import matplotlib.pyplot as plt
    f2h=G["fig_to_html"]; fig,ax=plt.subplots()
    ax.plot([0,1],[0,1]); f2h(fig)
    if not getattr(ax,"_nb_themed",False):
        fails.append("%s: fig_to_html did not theme an un-themed axes" % path)
print("\nshared toolkit sha256[:12] = %s, %d bytes, embedded in all %d notebooks"
      % (tpl_hash, len(tpl), len(NBS)))
print("\n"+("ONE TOOLKIT, PROFILES CORRECT" if not fails else "FAILURES:\n- "+"\n- ".join(fails)))
sys.exit(1 if fails else 0)
