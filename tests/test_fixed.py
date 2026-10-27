import sys as _sys, nbpick as _nbpick; _nbpick.argv_fix(_sys.argv)   # E28: ohne Angabe die Vorlage (--nb complex auf Zuruf)
NBFILE=1
"""Assert that every interactive plot keeps EXACTLY the same pixel size and the
same axis limits across the whole slider range — that is what stops the picture
from shifting while a slider moves."""
import json, io, base64, contextlib, re, struct, sys
import matplotlib; matplotlib.use("Agg")
import IPython.display as ipd
ipd.display = lambda *a, **k: None
nb=json.load(open(__import__("sys").argv[1] if len(__import__("sys").argv)>1 else "Complex_Numbers_Step_by_Step.ipynb"))
src=__import__("megasrc").expand("".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"]))
src="\n".join(l for l in src.splitlines() if not l.strip().startswith("%pip"))
G={"__name__":"__main__","display":lambda *a,**k:None}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src,"m","exec"),G)
np=G["np"]; f2h=G["fig_to_html"]

def png_size(html):
    # 2026-09-28 (R2 · 16): the plots are inline SVG now — same claim, the size
    # is read off the <svg> element (px, set from figsize × dpi)
    m=re.search(r'<svg[^>]*?width="([\d.]+)px" height="([\d.]+)px"', html)
    if m:
        return (int(float(m.group(1))), int(float(m.group(2))))
    b64=re.search(r'base64,([^"\']+)', html).group(1)
    raw=base64.b64decode(b64)
    w,h=struct.unpack(">II", raw[16:24])
    return (w,h)

# 2026-09-30 (E10 Teil 4) — Modeling: every slider plot on fixed_canvas, the
# slider ends as cases (the frame must not move between them); no frame players
_MOD = "Modeling" in (sys.argv[1] if len(sys.argv) > 1 else "")
MOD_CASES = {} if not _MOD else {
 "m01 scales":        (G["_render_m01"], [dict(log_dt=-4, log_T=6), dict(log_dt=6, log_T=-4), dict(log_dt=0, log_T=0)]),
 "m02 observations":  (G["_render_m02"], [dict(model_slope=-6), dict(model_slope=12), dict(model_slope=0)]),
 "m03 white/black":   (G["_render_m03"], [dict(poly_degree=1), dict(poly_degree=12), dict(poly_degree=6)]),
 "m04 elimination":   (G["_render_m04"], [dict(C0=50, k=0.1), dict(C0=150, k=0.8), dict(C0=100, k=0.35)]),
 "m05 objective":     (G["_render_m05"], [dict(C0=50, k=0.1), dict(C0=150, k=0.8), dict(C0=80, k=0.5)]),
 "m06 descent":       (G["_render_m06"], [dict(learning_rate=0.01, epochs=10), dict(learning_rate=0.6, epochs=400),
                                          dict(learning_rate=0.1, epochs=100)]),
 "m07 train/test":    (G["_render_m07"], [dict(degree=1), dict(degree=12), dict(degree=3)]),
 "m08 sensitivity":   (G["_render_m08"], [dict(k=0.1), dict(k=0.8), dict(k=0.35)]),
 "m09 monte-carlo":   (G["_render_m09"], [dict(n=50), dict(n=5000), dict(n=500)]),
}
# E28 (2026-10-12) — the template: every slider plot at its slider ends, the menu
# both ways; the frame player of k04
_VOR = "Vorlage" in (sys.argv[1] if len(sys.argv) > 1 else "")
VOR_CASES = {} if not _VOR else {
 "k01 one slider":    (G["_render_k01"], [dict(a=0), dict(a=10), dict(a=2)]),
 "k03 two + menu":    (G["_render_k03"], [dict(a=0, b=0, form="line"), dict(a=10, b=20, form="curve"),
                                          dict(a=2, b=1, form="line")]),
 "k04 three":         (G["_render_k04"], [dict(r=0.5, phi=0, n=1), dict(r=3, phi=6.28, n=4), dict(r=1, phi=0.5, n=2)]),
 "k05 target":        (G["_render_target_k05"], [dict(x=-3, y=-3), dict(x=3, y=3), dict(x=0, y=0)]),
}
if _VOR:
    MOD_CASES, _MOD = VOR_CASES, True       # the same path as Modeling: own cases, players below
CASES = MOD_CASES if _MOD else {
 "c01 parabola":      (G["_render_c01"], [dict(q=-6), dict(q=0), dict(q=10)]),
 "c02 argand":        (G["_render_c02"], [dict(a=-5,b=-5), dict(a=0,b=0), dict(a=5,b=5)]),
 "c03 add/sub":       (G["_render_c03"], [dict(a1=-6,b1=-6,a2=-6,b2=-6,op="z₁ + z₂"),
                                          dict(a1=6,b1=6,a2=-6,b2=-6,op="z₁ − z₂"),
                                          dict(a1=0,b1=0,a2=0,b2=0,op="z₁ + z₂")]),
 "c04 conjugate":     (G["_render_conj"], [dict(a=-5,b=-5), dict(a=5,b=5), dict(a=0,b=0)]),
 "c05 modulus/div":   (G["_render_c05"], [dict(a1=-7,b1=-7,a2=-7,b2=-7), dict(a1=7,b1=7,a2=0.5,b2=0),
                                          dict(a1=0,b1=0,a2=7,b2=7), dict(a1=4,b1=3,a2=0,b2=0)]),
 "c06 arctan trap":   (G["_render_trap"], [dict(a=-5,b=-5), dict(a=5,b=5), dict(a=0,b=3)]),
 "c07 product/quot":  (G["_render_c07"], [dict(r1=0.5,p1=0,r2=0.5,p2=0,op="z₁ · z₂"),
                                          dict(r1=2.5,p1=6.28,r2=2.5,p2=6.28,op="z₁ · z₂"),
                                          dict(r1=2.5,p1=1,r2=0.5,p2=5,op="z₁ / z₂")]),
}
bad=[]
for name,(fn,cases) in CASES.items():
    sizes=set(); lims=set()
    for kw in cases:
        fig=fn(**kw)
        for ax in fig.axes:
            lims.add((tuple(np.round(ax.get_xlim(),6)), tuple(np.round(ax.get_ylim(),6))))
        sizes.add(png_size(f2h(fig, tight=False)))
    ok = len(sizes)==1
    # one entry per axes object, so a 2-panel figure legitimately has 2 limit pairs
    n_ax = len(cases and fn(**cases[0]).axes)
    ok_lim = len(lims)==n_ax
    print("%-18s  size %-14s %s   limits %s"
          % (name, str(sizes.pop() if ok else sorted(sizes)),
             "OK " if ok else "VARIES", "OK" if ok_lim else "VARY: %s" % sorted(lims)))
    if not ok: bad.append(name+" (png size varies)")
    if not ok_lim: bad.append(name+" (axis limits vary)")

# frame players must also be uniform
# Paket 21b (2026-09-29): the players take a frame FUNCTION now (drawn when the
# chapter opens) — the test draws every frame itself
for key, n in ((("_k04_frames", 3),) if _VOR else () if _MOD else (("_euler_frames", G["_NFR"]), ("_ipow_frames", 5))):
    fr = G[key]
    fr = [fr(k) for k in range(n)] if callable(fr) else fr
    s={png_size(h) for h in fr}
    print("%-18s  %d frames, sizes %s  %s" % (key, len(fr), s, "OK" if len(s)==1 else "VARIES"))
    if len(s)!=1: bad.append(key)

print("\n"+("ALL PLOTS FIXED" if not bad else "PROBLEMS:\n- "+"\n- ".join(bad)))
sys.exit(1 if bad else 0)
