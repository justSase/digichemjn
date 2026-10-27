_intro = (
  "<b>Key idea and link to the previous chapters.</b> Once a model is calibrated, we ask which parameters "
  "really matter. <b>Sensitivity analysis</b> measures how much the output changes when an input changes. "
  "The simplest form is <b>one-factor-at-a-time</b> (OFAT). You vary a single parameter around a baseline "
  "(its reference value) and hold the others fixed. A central difference, a slope taken from one point on "
  "each side, then estimates the local sensitivity. Here the model output is the total drug exposure, the "
  "area under the curve (AUC = C&#8320;/k). The varied parameter is the elimination rate k.")

info = concept_box(_intro, r"$S \approx \dfrac{F(\mu_0+\delta)-F(\mu_0-\delta)}{2\,\delta}$",
    variables=[("S", "local sensitivity of the output to the parameter"),
               ("F", "the model output as a function of the parameter"),
               ("&#956;&#8320;", "baseline value of the parameter"),
               ("&#948;", "small perturbation around the baseline")])

_C0 = 100.0
def _auc(k):   # total exposure of the one-compartment model
    return _C0 / k
_m08ks = np.linspace(0.1, 0.8, 200)

def _slope_m08(k, delta=0.02):
    return (_auc(k + delta) - _auc(k - delta)) / (2 * delta)

def _render_m08(k=0.35):
    # FIXED frame: k 0.08 … 0.82 (slider 0.1 … 0.8), AUC 0 … 1100
    S = _slope_m08(k)
    fig, ax = fixed_canvas(figsize=(6.6, 3.9), left=.13, right=.97, top=.95, bottom=.15)
    theme_axes(ax)
    ax.set_xlim(0.08, 0.82); ax.set_ylim(0, 1100)
    ax.plot(_m08ks, _auc(_m08ks), color=PAL["z2"], lw=2.5, label="AUC(k) = C0/k")
    ax.scatter([k], [_auc(k)], color=PAL["z"], s=60, zorder=3, label="baseline")
    sec = np.array([k - 0.06, k + 0.06])
    ax.plot(sec, _auc(k) + S*(sec - k), color=PAL["warn"], lw=2, ls="--", label="local slope (sensitivity)")
    ax.set_xlabel("elimination rate k (1/h)"); ax.set_ylabel("AUC (mg·h/L)")
    theme_legend(ax, loc="upper right")
    return fig

def _read_m08(k=0.35):
    return readout([("k", "%.2f /h" % k), ("AUC", "%.0f mg·h/L" % _auc(k)),
                    ("sensitivity dAUC/dk", "%.0f" % _slope_m08(k))])

viz = [viz_intro_box("",
        "The blue curve is the model output (the total exposure) as a function of the elimination rate. The "
        "red point is the current baseline. The dashed line is the central-difference slope at that point: "
        "the local sensitivity. Move the rate and watch the slope. At small rates the curve is steep. The "
        "exposure then reacts strongly to k, and a small error in k badly distorts the prediction. At large "
        "rates the curve flattens, and the same absolute error in k barely matters. So sensitivity is local: "
        "it depends on where you stand.")]
viz += slider_plot(_render_m08, {"k": FloatSlider(value=0.35, min=0.1, max=0.8, step=0.01,
                                                  readout_format=".2f", description="k")},
                   readout_fn=_read_m08)

def _check_t8(ns):
    f = ns.get("sensitivity")
    if not callable(f): return False, "Define a function called sensitivity(F, mu0, delta)."
    s1 = float(f(lambda x: x**2, 3.0, 1e-3))     # derivative 2x = 6
    s2 = float(f(lambda x: 5.0*x, 2.0, 1e-3))    # derivative 5
    if np.isclose(s1, 6.0, atol=1e-2) and np.isclose(s2, 5.0, atol=1e-2):
        return True, "A two-sided difference, divided by the full distance 2·delta."
    if np.isclose(s1, 0.0):
        return False, "You returned 0. Evaluate F at mu0+delta and at mu0-delta, and take the difference."
    # 2026-09-27 (Inhalt): dividing by delta instead of 2·delta DOUBLES the slope
    # (12 and 10 here); the old branch looked for half of it and never fired.
    if np.isclose(s1, 12.0, atol=2e-2) or np.isclose(s2, 10.0, atol=2e-2):
        return False, "You divided by delta, not by 2·delta. This is a central (two-sided) difference."
    if np.isclose(s1, 3.0, atol=1e-2) or np.isclose(s2, 2.5, atol=1e-2):
        return False, "That is half the slope: divide by 2·delta once, not twice."
    return False, "For F(x)=x^2 at mu0=3 the answer is ~6; you got %s. Use (F(mu0+d)-F(mu0-d))/(2*d)." % fnum(s1)

# 2026-09-27 (Inhalt, nachziehen; eingebaut E10 Teil 4) — a number first, code optional.
def _F8(x): return _t8a * x * x
def _tv_m08():
    global _t8a, _t8m, _t8d, _T8
    _t8a, _t8m, _t8d = TV["sn_a"], TV["sn_mu"], TV["sn_d"]
    _T8 = (_F8(_t8m + _t8d) - _F8(_t8m - _t8d)) / (2 * _t8d)
_tv_m08()
on_reseed(_tv_m08)

def _ans_t8(v):
    x = v["S"]
    if _near(x, _T8):
        return True, ("Right: S = %s. For F = a·μ² the central difference is exact: it equals "
                      "the derivative 2aμ₀. That is why it is preferred over a one-sided one."
                      % fnum(_T8))
    if _near(x, 2 * _T8):
        return False, "You divided by δ, not by 2δ: the two points are 2δ apart."
    if _near(x, (_F8(_t8m + _t8d) - _F8(_t8m)) / _t8d):
        return False, ("That is the one-sided (forward) difference. Use both sides: "
                       "F(μ₀+δ) and F(μ₀−δ).")
    if _near(x, _F8(_t8m + _t8d) - _F8(_t8m - _t8d)):
        return False, "That is the difference of the two values. Divide it by 2δ to get a slope."
    return False, "Evaluate F at μ₀+δ and μ₀−δ, subtract, and divide by 2δ."

practice = [
  personal(lambda: exercise_box("",
      taskline("<b>Estimate a sensitivity by a central difference.</b>")
      + formula_line(r"$S=\dfrac{F(\mu_0+\delta)-F(\mu_0-\delta)}{2\,\delta}$")
      + "<div>A model output depends on a parameter as <b>F(μ) = %g·μ²</b>. At the baseline "
        "<b>μ₀ = %g</b> and with <b>δ = %g</b>, what is S?</div>" % (_t8a, _t8m, _t8d))),
  numeric_answer([("S", "S =")], _ans_t8, task="t8", columns=1),
  hint_steps("t8", lambda: [
    "A central difference measures a slope from two points placed symmetrically around the baseline. "
    "Evaluate F a little above (μ₀ + δ) and a little below (μ₀ − δ). Subtract the lower value from the "
    "upper one. Then divide by the distance between the two points, which is 2δ.",
    "Your two points are μ₀ + δ = %s and μ₀ − δ = %s. Evaluate %s·μ² at both, subtract, and divide by "
    "2 · %s." % (_g3(_t8m + _t8d), _g3(_t8m - _t8d), _g3(_t8a), _g3(_t8d)),
  ], forbid=lambda: (_T8,)),
  code_fold("def sensitivity(F, mu0, delta):\n    return 0.0\n",
            lambda g: _check_t8(g), task="t8", locked_by="t7",
            task_text=('Write <code>sensitivity(F, mu0, delta)</code> that estimates the local slope of a '
                       'function F at mu0 by a central difference with step delta. F is a function you can '
                       'call. '
                       'Example: <code>sensitivity(lambda x: x**2, 3, 0.001)</code> → <code>6.0…</code>.'),
            solution="def sensitivity(F, mu0, delta):\n"
                     "    return (F(mu0 + delta) - F(mu0 - delta)) / (2 * delta)\n"),
]

interp = interpretation_box(
    "OFAT is cheap and easy to interpret, so it is a natural first step. Its limitation: it is local and "
    "one-dimensional. It probes one parameter near one baseline. It therefore misses interactions between "
    "parameters and non-linear behaviour across the whole range. When several parameters matter at once, "
    "you need a global method that samples the whole parameter space, such as Monte-Carlo.")

# E19.8 — from "Remarks": the limit of OFAT, in red
warn = warn_box(
  "<b>Local sensitivity is local.</b> A one-factor-at-a-time analysis probes one point in parameter "
  "space. It misses interactions between parameters and global non-linear behaviour.")

build_chapter(8, "Sensitivity analysis: One factor at a time", figure="Local sensitivity of the exposure",
              info=info, viz=viz, practice=practice, interp=interp, body=[warn], task="t8", locked_by="t7")
