info = note_box(
  "<b>Key idea and link to the previous chapter.</b> Models differ in how much mechanism they contain. An "
  "<b>event-driven</b> (white-box) model is built from known processes and clear causes and effects. It "
  "explains <i>why</i> an outcome occurs. A <b>data-driven</b> (black-box) model learns a mapping from the "
  "observed data alone, without knowing the mechanism. It captures <i>what</i> tends to occur. Most real "
  "models are <b>grey boxes</b> somewhere in between."
  "<div style='margin:14px 0'>" + make_table(
      ["aspect", "event-driven (white box)", "data-driven (black box)"],
      [["built from", "physical / chemical laws", "observed data"],
       ["direction", "bottom-up (mechanism)", "top-down (empirical)"],
       ["answers", "why it happens", "what tends to happen"],
       ["extrapolates", "often well, within its assumptions", "poorly, outside the training range"]],
      scheme="info") + "</div>"
  "The visualisation fits both kinds to the same simulated drug concentrations. The white box is an "
  "exponential decay from first-order kinetics (the rate is proportional to the amount left). The black "
  "box is a polynomial that just follows the points.")

_m03xx = np.linspace(0, 13, 200)
_m03b1, _m03b0 = np.polyfit(t_obs[c_obs > 0], np.log(c_obs[c_obs > 0]), 1)   # white box, log-linear LSQ

def _render_m03(poly_degree=6):
    # FIXED frame: time 0 … 13 h, concentration −20 … 120 mg/L, whatever the degree
    fig, ax = fixed_canvas(figsize=(6.6, 3.9), left=.12, right=.97, top=.95, bottom=.15)
    theme_axes(ax)
    ax.set_xlim(0, 13); ax.set_ylim(-20, 120)
    black = np.poly1d(np.polyfit(t_obs, c_obs, int(poly_degree)))(_m03xx)
    ax.scatter(t_obs, c_obs, color=PAL["z2"], s=28, zorder=3, label="data (simulated)")
    ax.plot(_m03xx, np.exp(_m03b0) * np.exp(_m03b1 * _m03xx), color=PAL["sum"], lw=2.5,
            label="white box: exponential")
    ax.plot(_m03xx, black, color=PAL["z"], lw=2, ls="--", label="black box: polynomial")
    ax.set_xlabel("time (h)"); ax.set_ylabel("concentration (mg/L)")
    theme_legend(ax, loc="upper right")
    return fig

def _read_m03(poly_degree=6):
    black = np.poly1d(np.polyfit(t_obs, c_obs, int(poly_degree)))
    return readout([("degree", "%d" % int(poly_degree)),
                    ("white box at 13 h", "%.1f mg/L" % float(np.exp(_m03b0 + _m03b1 * 13))),
                    ("black box at 13 h", "%.1f mg/L" % float(black(13.0)))])

viz = [viz_intro_box("",
        "The same simulated concentration&ndash;time data is described in two ways. The green curve is a "
        "white-box first-order exponential; its single rate constant comes from the assumed mechanism. The "
        "red dashed curve is a black-box polynomial whose degree you control. Raise the degree, and the "
        "polynomial fits the points ever more closely inside the measured window. Just beyond the last "
        "point, though, it swings off wildly, while the mechanistic curve keeps decaying sensibly. This is "
        "the classic trade-off. Mechanism gives you predictions you can trust outside the data (extrapolation); "
        "flexibility gives you a close fit inside it.")]
viz += slider_plot(_render_m03, {"poly_degree": IntSlider(value=6, min=1, max=12, step=1, description="degree")},
                   readout_fn=_read_m03)

# 2026-09-27 (Inhalt, ML/Mod-Aufgaben; eingebaut E10 Teil 4) — the standard pair.
def _tv_m03():
    global _q3C0, _q3C2, _q3T, _Q3k, _Q3w, _Q3b
    _q3C0, _q3C2, _q3T = TV["wb_C0"], TV["wb_C2"], TV["wb_T"]
    _Q3k = float(np.log(_q3C0 / _q3C2) / 2)
    _Q3w = float(_q3C0 * np.exp(-_Q3k * _q3T))
    _Q3b = float(_q3C0 + (_q3C2 - _q3C0) / 2 * _q3T)
_tv_m03()
on_reseed(_tv_m03)

def _check_t3(ns):
    f = ns.get("predict_both")
    if not callable(f): return False, "Define a function called predict_both(C0, C2, T)."
    w, b = f(100.0, 50.0, 4)                         # k = ln2/2 -> 25 ; line -> 0
    if np.isclose(w, 25.0) and np.isclose(b, 0.0):
        return True, "Both predictions right: the mechanism halves twice, the line runs out of concentration."
    if np.isclose(b, 0.0) and np.isclose(w, 400.0): return False, "The exponential must decay: e^(−k·T)."
    if np.isclose(w, 25.0): return False, "The white box is right; the line runs through (0, C0) and (2, C2), so its slope is (C2 − C0)/2."
    return False, "For C0=100, C2=50, T=4: white box 25, black box 0; got %s and %s." % (fnum(w), fnum(b))

def _ans_t3(v):
    w, b = v["w"], v["b"]
    if not _near(w, _Q3w):
        if _near(w, float(_q3C0 * np.exp(_Q3k * _q3T))):
            return False, "Your exponential grows. Elimination makes it decay: C0·e<sup>−k·T</sup>."
        if _near(w, float(_q3C0 * np.exp(-np.log10(_q3C0 / _q3C2) / 2 * _q3T))):
            return False, "k comes from the natural log: k = ln(C(0)/C(2)) / 2."
        return False, "First k = ln(C(0)/C(2)) / 2, then C(T) = C(0)·e<sup>−k·T</sup>."
    if _near(b, _Q3b):
        return True, ("Right: the mechanism predicts %s mg/L, the straight line %s mg/L%s. Both agree on "
                      "the two measured points; only the mechanism survives outside them."
                      % (fnum(_Q3w), fnum(_Q3b), " (a negative concentration)" if _Q3b < 0 else ""))
    if _near(b, float(_q3C0 - (_q3C2 - _q3C0) / 2 * _q3T)):
        return False, "The line falls: its slope is (C(2) − C(0)) / 2, which is negative."
    return False, "The line through (0, C(0)) and (2, C(2)) is C(0) + slope·T with slope (C(2) − C(0)) / 2."

practice = [
  personal(lambda: exercise_box("",
      taskline("<b>Extrapolate with both kinds of model.</b>")
      + formula_line(r"$\mathrm{white:}\ C_0e^{-kT},\ k=\frac{1}{2}\ln\frac{C(0)}{C(2)}\qquad \mathrm{black:}\ C(0)+\frac{C(2)-C(0)}{2}\,T$")
      + "<div>Two measurements are all you have (simulated): <b>C(0) = %g mg/L</b> and "
        "<b>C(2 h) = %g mg/L</b>. A white-box model assumes first-order elimination; a black-box model "
        "draws the straight line through the two points. What does each predict at <b>t = %d h</b>?</div>"
      % (_q3C0, _q3C2, _q3T))),
  numeric_answer([("w", "white box ="), ("b", "black box =")], _ans_t3, task="t3"),
  hint_steps("t3", lambda: [
    "Both models have to pass through your two measured points, and in each model the points "
    "fix one number. The white box, C(t) = C(0)·e<sup>−kt</sup>, gets its rate k from how much of the drug is left "
    "after 2 h. The black box, a straight line, gets its slope from the same two points. Then read each "
    "model off at the later time.",
    "White box: k = ln(%g / %g) / 2 (natural log), then evaluate %g · e<sup>−k·%d</sup>. Black box: the "
    "slope is (%g − %g) / 2 mg/L per hour (negative), and the line at t = %d h is %g + slope · %d."
    % (_q3C0, _q3C2, _q3C0, _q3T, _q3C2, _q3C0, _q3T, _q3C0, _q3T),
  ], forbid=lambda: (_Q3w, _Q3b)),
  code_fold("import numpy as np\n\n"
            "def predict_both(C0, C2, T):\n"
            "    # return (white-box prediction, black-box prediction) at time T\n"
            "    return 0.0, 0.0\n",
            lambda g: _check_t3(g), task="t3", locked_by="t2",
            task_text=('Write <code>predict_both(C0, C2, T)</code> that takes the concentrations measured at '
                       '0 h and 2 h and returns the two predictions at time T: first the white box '
                       '(first-order elimination through both points), then the black box (the straight '
                       'line through both points). '
                       'Example: <code>predict_both(100, 50, 4)</code> → <code>(25.0, 0.0)</code>.'),
            solution="import numpy as np\n\n"
                     "def predict_both(C0, C2, T):\n"
                     "    k = np.log(C0 / C2) / 2\n"
                     "    return float(C0 * np.exp(-k * T)), float(C0 + (C2 - C0) / 2 * T)\n"),
]

interp = interpretation_box(
    "Neither box is better in every case. The white-box model contains a pharmacological assumption and "
    "extrapolates well, which matters for dosing. The black-box model makes no such assumption and can fit "
    "more complex shapes. But you can trust it only within the range of data it saw. In practice the usual "
    "choice is a grey box: mechanism where it is known, data where it is not.")

# E19.8 — from "Remarks": the pitfall of the black box, in red
warn = warn_box(
  "<b>Correlation is not causation.</b> A data-driven fit describes an association, not a mechanism. "
  "Be sceptical of linear correlations and oversimplified patterns.")

build_chapter(3, "Data-driven vs event-driven models", figure="White box against black box",
              info=info, viz=viz, practice=practice, interp=interp, body=[warn], task="t3", locked_by="t2")
