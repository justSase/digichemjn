_intro = (
  "<b>Key idea and link to the previous chapters.</b> Now the conceptual model becomes concrete. Take a "
  "single dose into a vein. The drug spreads into one well-mixed space (a compartment), and the body "
  "removes it at a rate proportional to its concentration. Then the concentration falls "
  "<b>exponentially</b> with time. This one-compartment, first-order model is the basis of clinical "
  "pharmacokinetics" + cite(4) +
  " and of the cefazolin dosing analysis later on" + cite(5) + ".")

info = concept_box(_intro, r"$C(t) = C_0\,e^{-k\,t}$",
    variables=[("C(t)", "drug concentration at time t (mg/L)"),
               ("C&#8320;", "initial concentration just after the dose (mg/L)"),
               ("k", "first-order elimination rate constant (1/h)"),
               ("t", "time since the dose (h)")])

_m04t = np.linspace(0, 12, 200)

def _render_m04(C0=100.0, k=0.35):
    # FIXED frame: 0 … 12 h, 0 … 160 mg/L (the C0 slider ends at 150)
    fig, ax = fixed_canvas(figsize=(6.6, 3.9), left=.12, right=.97, top=.95, bottom=.15)
    theme_axes(ax)
    ax.set_xlim(0, 12); ax.set_ylim(0, 160)
    ax.scatter(t_obs, c_obs, color=PAL["ghost"], s=26, zorder=3, label="data (simulated)")
    ax.plot(_m04t, pk(_m04t, C0, k), color=PAL["z"], lw=2.5, label="model")
    th = np.log(2) / k
    if th <= 12:
        ax.plot([th, th], [0, C0 / 2], ls=":", color=PAL["z2"], lw=1.4)
        ax.plot([0, th], [C0 / 2, C0 / 2], ls=":", color=PAL["z2"], lw=1.4)
    ax.set_xlabel("time (h)"); ax.set_ylabel("concentration (mg/L)")
    theme_legend(ax, loc="upper right")
    return fig

def _read_m04(C0=100.0, k=0.35):
    return readout([("C₀", "%.0f mg/L" % C0), ("k", "%.2f /h" % k),
                    ("half-life", "%.2f h" % (np.log(2) / k)), ("AUC = C₀/k", "%.0f mg·h/L" % (C0 / k))])

viz = [viz_intro_box("",
        "The curve is the model and the pale points are the simulated measurements. The initial "
        "concentration sets where the curve starts. The elimination rate constant sets how fast it falls. "
        "The half-life (dotted), the time until half the drug is gone, is ln(2) divided by that rate. Try a "
        "small rate near 0.15 for a drug the body clears slowly, and a large rate near 0.7 for one it clears "
        "fast. Then adjust the initial concentration until the red curve runs through the points. Finding "
        "those two numbers by eye is the calibration problem of the next chapter.")]
viz += slider_plot(_render_m04, {"C0": FloatSlider(value=100.0, min=50, max=150, step=1, description="C0"),
                                 "k":  FloatSlider(value=0.35, min=0.1, max=0.8, step=0.01,
                                                   readout_format=".2f", description="k")},
                   readout_fn=_read_m04)

# 2026-09-27 (Inhalt, ML/Mod-Aufgaben; eingebaut E10 Teil 4) — the standard pair.
def _tv_m04():
    global _q4C0, _q4k, _q4t, _Q4h, _Q4c
    _q4C0, _q4k, _q4t = TV["pk_C0"], TV["pk_k"], TV["pk_t"]
    _Q4h = float(np.log(2) / _q4k)
    _Q4c = float(_q4C0 * np.exp(-_q4k * _q4t))
_tv_m04()
on_reseed(_tv_m04)

def _check_t4(ns):
    f = ns.get("pk_numbers")
    if not callable(f): return False, "Define a function called pk_numbers(C0, k, t)."
    # k = 0.5, NOT ln 2: with k = ln 2 the swapped fraction k/ln 2 also gives 1
    # and the check could not tell them apart (found by test_checks, 27.09.)
    h, c = f(100.0, 0.5, 2.0)                        # half-life 1.386 h, C(2) = 36.79
    H, C = np.log(2) / 0.5, 100.0 * np.exp(-1.0)
    if np.isclose(h, H) and np.isclose(c, C):
        return True, "Half-life and remaining concentration both right."
    if np.isclose(c, 100.0 * np.exp(1.0)): return False, "The concentration must fall: e^(−k·t)."
    if np.isclose(h, 0.5 / np.log(2)) or np.isclose(h, 0.5 * np.log(2)): return False, "Half-life = ln 2 <b>divided</b> by k."
    return False, "For C0=100, k=0.5, t=2: half-life %s and C %s; got %s and %s." % (fnum(H), fnum(C), fnum(h), fnum(c))

def _ans_t4(v):
    h, c = v["h"], v["c"]
    if not _near(h, _Q4h):
        if _near(h, float(np.log10(2) / _q4k)):
            return False, "Natural log: t½ = ln 2 / k (ln 2 ≈ 0.693)."
        if _near(h, _q4k / np.log(2)) or _near(h, 1 / _q4k):
            return False, "t½ = ln 2 / k: ln 2 on top, k below."
        return False, "Set C(t½) = C0/2 in C0·e<sup>−k·t</sup>: that gives t½ = ln 2 / k."
    if _near(c, _Q4c):
        return True, ("Right: t½ = %s h, and after %d h %s mg/L are left. That is %s half-lives, so a fraction "
                      "(1/2)<sup>%s</sup>." % (fnum(_Q4h), _q4t, fnum(_Q4c), fnum(_q4t / _Q4h), fnum(_q4t / _Q4h)))
    if _near(c, float(_q4C0 * np.exp(_q4k * _q4t))):
        return False, "The exponent is negative: C0·e<sup>−k·t</sup>."
    if _near(c, _q4C0 * (1 - _q4k * _q4t)):
        return False, "That is a straight-line decrease. First-order elimination is exponential: C0·e<sup>−k·t</sup>."
    return False, "C(t) = C0·e<sup>−k·t</sup> with your three numbers."

practice = [
  personal(lambda: exercise_box("",
      taskline("<b>Two numbers every pharmacist asks for.</b>")
      + formula_line(r"$t_{1/2}=\dfrac{\ln 2}{k},\qquad C(t)=C_0\,e^{-k\,t}$")
      + "<div>After an intravenous dose the concentration starts at <b>C₀ = %g mg/L</b> and is "
        "eliminated with <b>k = %g h⁻¹</b>. What is the half-life, and what concentration is left "
        "after <b>%d h</b>? The sliders above let you check the curve.</div>" % (_q4C0, _q4k, _q4t))),
  numeric_answer([("h", "t½ [h] ="), ("c", "C [mg/L] =")], _ans_t4, task="t4"),
  hint_steps("t4", lambda: [
    "The half-life is the time after which the concentration has fallen to half of C₀. Put that into "
    "the model: C₀·e<sup>−k·t½</sup> = C₀/2, so e<sup>−k·t½</sup> = 1/2. Take the natural log: "
    "t½ = ln 2 / k. For the concentration left, put your time into C(t) = C₀·e<sup>−k·t</sup>.",
    "With your numbers: t½ = ln 2 / %g, with ln 2 ≈ 0.693. The exponent for the second box is "
    "k · t = %g · %d; the concentration is %g times e to the power of minus that."
    % (_q4k, _q4k, _q4t, _q4C0),
  ], forbid=lambda: (_Q4h, _Q4c)),
  code_fold("import numpy as np\n\n"
            "def pk_numbers(C0, k, t):\n"
            "    # return (half-life, concentration at time t)\n"
            "    return 0.0, 0.0\n",
            lambda g: _check_t4(g), task="t4", locked_by="t3",
            task_text=('Write <code>pk_numbers(C0, k, t)</code> that returns, for first-order elimination '
                       'C(t) = C0·e<sup>−kt</sup>, the half-life and the concentration left at time t, as '
                       'a pair. '
                       'Example: <code>pk_numbers(100, 0.5, 2)</code> → <code>(1.386…, 36.79…)</code>.'),
            solution="import numpy as np\n\n"
                     "def pk_numbers(C0, k, t):\n"
                     "    return float(np.log(2) / k), float(C0 * np.exp(-k * t))\n"),
]

interp = interpretation_box(
    "Two parameters fix this model completely: the starting concentration and the elimination rate. Every "
    "pharmacokinetic quantity you need follows from them. The half-life is ln(2) over the rate. The area "
    "under the curve measures the total drug exposure; it is the initial concentration divided by the "
    "rate. In a good conceptual model, a few parameters carry a real, interpretable meaning.")

build_chapter(4, "The conceptual model: First-order elimination", figure="The elimination curve",
              info=info, viz=viz, practice=practice, interp=interp, task="t4", locked_by="t3")
