_intro = (
  "<b>Key idea and link to the previous chapter.</b> In the last chapter you adjusted the two parameters by "
  "eye. That is calibration by hand. To calibrate objectively, we need one number that says how badly the "
  "model misses the data. This number is the <b>objective function</b>. The usual choice is the <b>sum of "
  "squared errors</b> (SSE) between the observed and the predicted concentrations. Calibration then means "
  "finding the parameters that make this sum as small as possible" + cite(2) + ".")

info = concept_box(_intro, r"$F(\theta)=\sum_i \left(C_i-\hat{C}(t_i)\right)^2$",
    variables=[("F(&#952;)", "objective (sum of squared errors) for parameters &#952;"),
               ("C&#7522;", "observed concentration at time t&#7522; (mg/L)"),
               ("&#264;(t&#7522;)", "concentration predicted by the model at t&#7522;"),
               ("&#952;", "the parameters being calibrated, here C&#8320; and k")])

_m05t = np.linspace(0, 12, 200)

def _render_m05(C0=80.0, k=0.5):
    # FIXED frame: 0 … 12 h, 0 … 160 mg/L
    fig, ax = fixed_canvas(figsize=(6.6, 3.9), left=.12, right=.97, top=.95, bottom=.15)
    theme_axes(ax)
    ax.set_xlim(0, 12.5); ax.set_ylim(0, 160)
    pred_obs = pk(t_obs, C0, k)
    for ti, ci, pi in zip(t_obs, c_obs, pred_obs):          # residuals as vertical sticks
        ax.plot([ti, ti], [ci, pi], color=PAL["warn"], lw=1.4, alpha=.9)
    ax.scatter(t_obs, c_obs, color=PAL["z2"], s=28, zorder=3, label="data")
    ax.plot(_m05t, pk(_m05t, C0, k), color=PAL["z"], lw=2.5, label="model")
    ax.set_xlabel("time (h)"); ax.set_ylabel("concentration (mg/L)")
    theme_legend(ax, loc="upper right")
    return fig

def _read_m05(C0=80.0, k=0.5):
    return readout([("C₀", "%.0f mg/L" % C0), ("k", "%.2f /h" % k),
                    ("SSE", "%.1f" % sse(c_obs, pk(t_obs, C0, k))), ("", "smaller = better fit")])

viz = [viz_intro_box("",
        "Each amber stick is one residual: the gap between a measurement and the model at that time. The "
        "objective adds up the squares of all residuals. Move the two sliders and try to make the SSE below "
        "them smaller. You will notice that a better fit at one end often means a worse fit at the other. "
        "The best fit is a compromise that balances all residuals together. Because of the squaring, large "
        "misses count far more than small ones. That is why the curve is pulled towards the outlying points.")]
viz += slider_plot(_render_m05, {"C0": FloatSlider(value=80.0, min=50, max=150, step=1, description="C0"),
                                 "k":  FloatSlider(value=0.5, min=0.1, max=0.8, step=0.01,
                                                   readout_format=".2f", description="k")},
                   readout_fn=_read_m05)

def _check_t5(ns):
    f = ns.get("my_sse")
    if not callable(f): return False, "Define a function called my_sse(y_true, y_pred)."
    a = float(f([1, 2, 3], [1, 2, 3]))     # identical → 0
    b = float(f([0, 0], [1, 2]))           # 1 + 4 = 5
    if np.isclose(a, 0.0) and np.isclose(b, 5.0):
        return True, "Zero for a perfect fit, and the squares add up."
    if a == 0.0 and b == 0.0:
        return False, "You are still returning the placeholder; combine y_true and y_pred."
    if not np.isclose(a, 0.0):
        return False, "Identical inputs must give 0: subtract y_pred from y_true first."
    if np.isclose(b, 3.0):
        return False, "That looks like the sum of absolute errors. Square each difference, do not take its size."
    return False, "Expected 0 and 5; got %s and %s. Square each difference, then sum." % (fnum(a), fnum(b))

# 2026-09-27 (Inhalt, nachziehen; eingebaut E10 Teil 4) — a number first, code optional.
def _tv_m05():
    global _t5o, _t5p, _t5r, _T5
    _t5o, _t5p = TV["sse_obs"], TV["sse_pred"]
    _t5r = [o - p for o, p in zip(_t5o, _t5p)]
    _T5 = float(np.sum(np.square(_t5r)))
_tv_m05()
on_reseed(_tv_m05)

def _ans_t5(v):
    x = v["F"]
    if _near(x, _T5):
        return True, ("Right: the residuals are %s, and their squares add up to %s. Calibration "
                      "searches for the C₀ and k that make this number as small as possible."
                      % (", ".join("%d" % r for r in _t5r), fnum(_T5)))
    if _near(x, _T5 / 3):
        return False, ("That is the <b>mean</b> of the squares. The objective here is their "
                       "<b>sum</b>, so do not divide by n.")
    if _near(x, float(np.sum(np.abs(_t5r)))):
        return False, "That is the sum of the absolute residuals. Square each residual, then add."
    if _near(x, float(np.sum(_t5r))) or _near(x, float(np.sum(_t5r)) ** 2):
        return False, ("You added the residuals before squaring, so their signs cancel. Square each "
                       "residual on its own, then add.")
    return False, "For each point, residual = observed − predicted. Square the three residuals and add them."

practice = [
  personal(lambda: exercise_box("",
      taskline("<b>Compute the objective for one guess of the parameters.</b>")
      + formula_line(r"$F=\sum_i (y_i-\hat{y}_i)^2$")
      + "<div>At three time points the assay measured <b>y = %s mg/L</b>; the model with the "
        "current guess of C₀ and k predicts <b>ŷ = %s mg/L</b>. What is F?</div>"
      % (", ".join(map(str, _t5o)), ", ".join(map(str, _t5p))))),
  numeric_answer([("F", "F =")], _ans_t5, task="t5", columns=1),
  hint_steps("t5", lambda: [
    "The objective collects every miss in one number. For each time point, take the residual (observed "
    "minus predicted) and square it. Squaring makes misses up and down both count, and big misses count "
    "more. Then add the squares. Do not divide: this objective is a <i>sum</i>.",
    "Your three residuals y − ŷ are %s. Square each of them and add the three squares."
    % ", ".join(("%d" % r).replace("-", "−") for r in _t5r),
  ], forbid=lambda: (_T5,)),
  code_fold("def my_sse(y_true, y_pred):\n"
            "    y_true = np.asarray(y_true, float); y_pred = np.asarray(y_pred, float)\n"
            "    return 0.0\n",
            lambda g: _check_t5(g), task="t5", locked_by="t4",
            task_text=('Write <code>my_sse(y_true, y_pred)</code> that returns the objective used for '
                       'calibration: the sum of the squared differences between observed and predicted '
                       'values. '
                       'Example: <code>my_sse([0, 0], [1, 2])</code> → <code>5.0</code>.'),
            solution="def my_sse(y_true, y_pred):\n"
                     "    y_true = np.asarray(y_true, float); y_pred = np.asarray(y_pred, float)\n"
                     "    return float(np.sum((y_true - y_pred)**2))\n"),
]

interp = interpretation_box(
    "Calibration is now a precise task: choose the parameters that make the objective as small as possible. "
    "By hand, this works for two parameters, but it quickly becomes hopeless for many. So the next chapter "
    "hands the search to an algorithm. The objective you just computed is exactly the quantity that this "
    "algorithm will push downhill.")

# E19.8 — from "Remarks": the pitfall of the objective, in red
warn = warn_box(
  "<b>Goodhart's law:</b> when a measure becomes a target, it stops being a good measure" + cite(10) + ". "
  "Optimising a single metric too hard can quietly damage the real goal.")

build_chapter(5, "Calibration: The objective function", figure="Residuals and the objective",
              info=info, viz=viz, practice=practice, interp=interp, body=[warn], task="t5", locked_by="t4")
