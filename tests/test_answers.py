import sys as _sys, nbpick as _nbpick; _nbpick.argv_fix(_sys.argv)   # E28: ohne Angabe die Vorlage (--nb complex auf Zuruf)
NBFILE=1
"""Every non-code answer route must accept the right answer and reject a targeted
wrong one with a specific hint — the same contract the code route already has."""
import json, io, contextlib, re, sys
import matplotlib; matplotlib.use("Agg")
import IPython.display as ipd; ipd.display = lambda *a, **k: None
nb=json.load(open(__import__("sys").argv[1] if len(__import__("sys").argv)>1 else "Complex_Numbers_Step_by_Step.ipynb"))
src="\n".join(l for l in __import__("megasrc").expand("".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"])).splitlines()
              if not l.strip().startswith("%pip"))
G={"__name__":"__main__","display":lambda *a,**k:None}
with contextlib.redirect_stdout(io.StringIO()): exec(compile(src,"m","exec"),G)
np=G["np"]; TV=G["TV"]
strip=lambda t: re.sub("<[^>]+>","",str(t))
fails=[]

# 2026-09-30 (E10 Teil 4) — MODELING: nine numeric routes. Each is checked with
# the right answer and a targeted wrong one, recomputed HERE from TV — for the
# seed of this run and for 40 more drawn in place (reseed), so the chapters'
# on_reseed hooks are exercised too: a check that kept the old numbers accepts
# the old answer and fails here.
# E28 (2026-10-12) — THE TEMPLATE: five routes of five kinds (number, number,
# choice, angle with period, slider target), right and targeted wrong, recomputed
# HERE from TV for this seed and 40 more drawn in place (the on_reseed hooks of
# k01/k02/k04/k05 are exercised: a hook that kept the old number fails here)
if "Vorlage" in (sys.argv[1] if len(sys.argv) > 1 else ""):
    def _vor_cases():
        a, b = TV["a"], TV["b"]
        p4 = 0.3 + 0.1 * a; tx, ty = 1.0 + 0.2 * b, 1.0
        return [
         ("t1 number",  "_ans_t1", (dict(y=3 * a),), (dict(y=3 * a + 3),)),
         ("t2 number",  "_ans_t2", (dict(y=4 * b),), (dict(y=4 * b + 3),)),
         ("t3 choice",  "_ans_t3", (0, ""), (1, "")),
         ("t4 angle",   "_ans_t4", (dict(phi=p4 + np.pi),), (dict(phi=p4),)),
         ("t4 +2π",     "_ans_t4", (dict(phi=p4 + 3 * np.pi),), (dict(phi=p4 + 2 * np.pi),)),
         ("t5 target",  "_ans_t5", (dict(x=tx, y=ty),), (dict(x=tx + 1.0, y=ty),)),
        ]
    import random as _rnd
    _seeds = [None] + _rnd.Random(7).sample(range(100000), 40)
    for _lv in ("gentle", "standard", "strict"):
        G["set_difficulty"](_lv)
        for _sd in _seeds:
            if _sd is not None:
                with contextlib.redirect_stdout(io.StringIO()):
                    G["reseed"](_sd)
            for _hk, _get in G.get("_HINT_SRC", {}).items():
                try:
                    _get()
                except ValueError as _e:
                    fails.append("hint %s (%s, seed %s): %s" % (_hk, _lv, _sd, _e))
            for name, fn, good, bad in _vor_cases():
                ok, tip = G[fn](*good); ok2, tip2 = G[fn](*bad)
                if _sd is None and _lv == "standard":
                    print("%-13s right->%-5s   wrong->%-5s  hint: %s" % (name, ok, ok2, strip(tip2)[:78]))
                if not ok:  fails.append("%s (%s, seed %s): the correct answer was rejected (%s)" % (name, _lv, _sd, strip(tip)))
                if ok2:     fails.append("%s (%s, seed %s): a wrong answer was accepted" % (name, _lv, _sd))
    print("%d seeds x 3 levels x 6 routes and their hints checked" % len(_seeds))
    T = G["_TASKS"]
    _WANT = {"t%d" % i for i in range(1, 6)}
    if set(T["order"]) != _WANT:
        fails.append("task list changed unexpectedly: %s" % sorted(set(T["order"]) ^ _WANT))
    print("\n"+("ALL ANSWER ROUTES PASSED" if not fails else "FAILURES:\n- "+"\n- ".join(fails[:20])))
    sys.exit(1 if fails else 0)

if "Modeling" in (sys.argv[1] if len(sys.argv) > 1 else ""):
    def _mod_cases():
        tv = TV; ln2 = np.log(2)
        q1 = float(np.log10(tv["sc_slow"] * 3.6e6 / tv["sc_fast"]))
        y2 = np.array(tv["ob_y"], float)
        k3 = np.log(tv["wb_C0"] / tv["wb_C2"]) / 2
        w3 = float(tv["wb_C0"] * np.exp(-k3 * tv["wb_T"]))
        b3 = float(tv["wb_C0"] + (tv["wb_C2"] - tv["wb_C0"]) / 2 * tv["wb_T"])
        h4 = float(ln2 / tv["pk_k"]); c4 = float(tv["pk_C0"] * np.exp(-tv["pk_k"] * tv["pk_t"]))
        f5 = float(sum((o - p) ** 2 for o, p in zip(tv["sse_obs"], tv["sse_pred"])))
        k6 = tv["gd_k"] - tv["gd_lr"] * tv["gd_g"]
        e7 = np.array(tv["ov_y"]) - np.array(tv["ov_p"]); m7 = float(np.mean(e7 ** 2))
        s8 = 2 * tv["sn_a"] * tv["sn_mu"]
        p9 = 4.0 * tv["mc_r"] / tv["mc_n"]
        return [
         ("t1 scales",   "_ans_t1", dict(o=q1), dict(o=float(np.log10(tv["sc_slow"] / tv["sc_fast"])))),
         ("t2 mean/SD",  "_ans_t2", dict(m=y2.mean(), s=y2.std(ddof=1)), dict(m=y2.mean(), s=y2.std(ddof=0))),
         ("t3 boxes",    "_ans_t3", dict(w=w3, b=b3), dict(w=w3, b=2 * tv["wb_C0"] - b3)),
         ("t4 half-life","_ans_t4", dict(h=h4, c=c4), dict(h=tv["pk_k"] / ln2, c=c4)),
         ("t5 SSE",      "_ans_t5", dict(F=f5), dict(F=f5 / 3)),
         ("t6 GD step",  "_ans_t6", dict(k=k6), dict(k=tv["gd_k"] + tv["gd_lr"] * tv["gd_g"])),
         ("t7 test MSE", "_ans_t7", dict(m=m7, g=m7 - tv["ov_tr"]), dict(m=m7, g=tv["ov_tr"] - m7)),
         ("t8 central",  "_ans_t8", dict(S=s8), dict(S=2 * s8)),
         ("t9 MC pi",    "_ans_t9", dict(pi=p9), dict(pi=tv["mc_r"] / tv["mc_n"])),
        ]
    import random as _rnd
    _seeds = [None] + _rnd.Random(7).sample(range(100000), 40)
    for _lv in ("gentle", "standard", "strict"):
        G["set_difficulty"](_lv)
        for _sd in _seeds:
            if _sd is not None:
                with contextlib.redirect_stdout(io.StringIO()):
                    G["reseed"](_sd)
            # the hints are rebuilt from the new numbers too; a step that would
            # state a result for this seed raises here (hint_steps' own guard)
            for _hk, _get in G.get("_HINT_SRC", {}).items():
                try:
                    _get()
                except ValueError as _e:
                    fails.append("hint %s (%s, seed %s): %s" % (_hk, _lv, _sd, _e))
            for name, fn, good, bad in _mod_cases():
                ok, tip = G[fn](good); ok2, tip2 = G[fn](bad)
                if _sd is None and _lv == "standard":
                    print("%-13s right->%-5s   wrong->%-5s  hint: %s" % (name, ok, ok2, strip(tip2)[:78]))
                if not ok:  fails.append("%s (%s, seed %s): the correct answer was rejected (%s)" % (name, _lv, _sd, strip(tip)))
                if ok2:     fails.append("%s (%s, seed %s): a wrong answer was accepted" % (name, _lv, _sd))
    print("%d seeds x 3 levels x 9 routes and their hints checked" % len(_seeds))
    T = G["_TASKS"]
    _WANT = {"t%d" % i for i in range(1, 10)}          # E25.l: no q1/b1 (behauptete bisher: + q1, b1)
    if set(T["order"]) != _WANT:
        fails.append("task list changed unexpectedly: %s" % sorted(set(T["order"]) ^ _WANT))
    print("\n"+("ALL ANSWER ROUTES PASSED" if not fails else "FAILURES:\n- "+"\n- ".join(fails[:20])))
    sys.exit(1 if fails else 0)

z1,z2,zq = TV["z1"],TV["z2"],TV["zq"]
prod = z1*z2; s_, d_ = z1+z2, z1-z2
# 2026-09-30 (E10): t5 divides the reader's seeded pair since py-12, not the old fixed
# (4+3i)/(-5+6i) — the test asserted the retired pair and rejected the right answer.
qd   = TV["n5"]/TV["d5"]
phiq = np.angle(zq)%(2*np.pi)
tz1  = G["_TZ1"]; tgt = G["_TGT"]

NUM = [
 ("t1 roots",   "_ans_t1", dict(re=0.0, im=np.sqrt(TV["q"])),      dict(re=np.sqrt(TV["q"]), im=0.0)),
 # the wrong variant must be wrong for EVERY seed -> shift, don't flip a sign
 # (a sign flip is a no-op when the component happens to be zero: flaky test)
 ("t3 add/sub", "_ans_t3", dict(sre=s_.real, sim=s_.imag, dre=d_.real, dim=d_.imag),
                            dict(sre=s_.real, sim=s_.imag, dre=d_.real, dim=d_.imag + 1.0)),
 ("t4 multiply","_ans_t4", dict(re=prod.real, im=prod.imag),
                            dict(re=prod.real+2*z1.imag*z2.imag, im=prod.imag)),
 ("t5 divide",  "_ans_t5", dict(re=qd.real, im=qd.imag),           dict(re=qd.real, im=qd.imag + 0.5)),
 ("t6 polar",   "_ans_t6", dict(r=abs(zq), phi=phiq),              dict(r=abs(zq), phi=(phiq+np.pi)%(2*np.pi))),
]
for name,fn,good,bad in NUM:
    f=G[fn]
    ok,tip=f(good); ok2,tip2=f(bad)
    print("%-13s right->%-5s   wrong->%-5s  hint: %s" % (name, ok, ok2, strip(tip2)[:78]))
    if not ok:  fails.append("%s: the correct answer was rejected (%s)" % (name, strip(tip)))
    if ok2:     fails.append("%s: a wrong answer was accepted" % name)

# choice routes
f=G["_ans_t2"]; true_idx=G["_QTRUE"]
ok,_=f(true_idx,""); ok2,tip2=f((true_idx+1)%4,"")
print("%-13s right->%-5s   wrong->%-5s  hint: %s" % ("t2 quadrant", ok, ok2, strip(tip2)[:78]))
if not ok: fails.append("t2: correct choice rejected")
if ok2:    fails.append("t2: wrong choice accepted")
# slider target
f=G["_ans_t7"]
r_ok, p_ok = abs(tgt)/abs(tz1), (np.angle(tgt)-np.angle(tz1))%(2*np.pi)
ok,_   = f(dict(r2=r_ok, p2=p_ok))
okL,tL = f(dict(r2=r_ok*0.6, p2=p_ok))          # right angle, wrong length
okA,tA = f(dict(r2=r_ok, p2=(p_ok+1.0)))        # right length, wrong angle
print("%-13s right->%-5s   short->%-5s  hint: %s" % ("t7 target", ok, okL, strip(tL)[:70]))
print("%-13s %19s wrongφ->%-5s hint: %s" % ("", "", okA, strip(tA)[:70]))
if not ok: fails.append("t7: the exact target position was rejected")
if okL or okA: fails.append("t7: an off-target position was accepted")
print("              exact solution: |z2| = %.2f, phi2 = %.3f" % (r_ok, p_ok))

# the task/lock wiring must cover every task
T=G["_TASKS"]; L=G["_LOCKS"]
print("\ntasks %s   locked chapters %s" % (T["order"], sorted(L)))
_WANT = {"t%d" % i for i in range(1, 8)}               # E25.l: no q1/b1 (behauptete bisher: + q1, b1)
if set(T["order"]) != _WANT:
    fails.append("task list changed unexpectedly: %s" % sorted(set(T["order"]) ^ _WANT))

print("\n"+("ALL ANSWER ROUTES PASSED" if not fails else "FAILURES:\n- "+"\n- ".join(fails)))
sys.exit(1 if fails else 0)
