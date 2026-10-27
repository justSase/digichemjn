_intro = (
  "<b>Key idea and link to the previous chapter.</b> With the objective, calibration becomes a search for "
  "its lowest point. <b>Gradient descent</b> does this search automatically. Again and again, it moves each "
  "parameter a small step against the slope (gradient) of the objective, until the objective stops "
  "falling" + cite(7) + ". Here it calibrates the elimination rate k of the pharmacokinetic model. At every "
  "step, the best initial concentration is solved for as well.")

info = concept_box(_intro, r"$\theta \leftarrow \theta - \eta\,\frac{\partial F}{\partial \theta}$",
    variables=[("&#952;", "the parameter being updated (here the rate k)"),
               ("&#951; (eta)", "learning rate, the step size"),
               ("&#8706;F/&#8706;&#952;", "gradient: slope of the objective F")])

# Taking the logarithm makes the first-order model LINEAR in its parameters
# (ln C = ln C0 - k·t), so gradient descent on the two parameters is well behaved.
# Time is standardised (the usual trick) so one learning rate works cleanly.
_ylog = np.log(c_obs)
_tm, _ts = float(t_obs.mean()), float(t_obs.std() + 1e-9)
_tz = (t_obs - _tm) / _ts
_m06t = np.linspace(0, 12, 200)

def _gd_m06(learning_rate, epochs):
    w = b = 0.0; hist = []                              # model: ln C ≈ w·z + b  (z = standardised time)
    n = t_obs.size
    for _ in range(int(epochs)):
        err = w*_tz + b - _ylog
        w -= learning_rate*(2/n)*np.sum(err*_tz)
        b -= learning_rate*(2/n)*np.sum(err)
        hist.append(float(np.mean((w*_tz + b - _ylog)**2)))
    return -w/_ts, float(np.exp(b - w*_tm/_ts)), hist   # back to k, C0

def _render_m06(learning_rate=0.1, epochs=100):
    # FIXED frames: left 0 … 12 h × 0 … 160 mg/L; right 0 … 400 steps (the slider's
    # end) × objective 10⁻³ … 30 on a log axis
    k, C0, hist = _gd_m06(learning_rate, epochs)
    fig, ax = fixed_canvas(figsize=(9.6, 3.8), left=.08, right=.98, top=.95, bottom=.15, ncols=2)
    theme_axes(ax[0]); theme_axes(ax[1])
    ax[0].set_xlim(0, 12.5); ax[0].set_ylim(0, 160)
    ax[0].scatter(t_obs, c_obs, color=PAL["z2"], s=24, zorder=3)
    ax[0].plot(_m06t, np.clip(pk(_m06t, C0, k), -1, 1e3), color=PAL["z"], lw=2.5)
    ax[0].set_xlabel("time (h)"); ax[0].set_ylabel("conc. (mg/L)")
    ax[1].set_yscale("log"); ax[1].set_xlim(0, 400); ax[1].set_ylim(1e-3, 30)
    ax[1].plot(np.arange(1, len(hist) + 1), np.clip(hist, 1e-3, 30), color=PAL["sum"], lw=2)
    ax[1].set_xlabel("step"); ax[1].set_ylabel("objective (MSE of ln C)")
    return fig

def _read_m06(learning_rate=0.1, epochs=100):
    k, C0, hist = _gd_m06(learning_rate, epochs)
    return readout([("lr", "%.2f" % learning_rate), ("steps", "%d" % int(epochs)),
                    ("fitted k", "%.3f /h" % k), ("fitted C₀", "%.1f mg/L" % C0),
                    ("final objective", "%.4f" % hist[-1])])

viz = [viz_intro_box("",
        "Training starts from a flat line and steps downhill on the objective. The left panel shows how the "
        "fitted curve settles onto the data. The right panel shows how the objective falls with every step. "
        "The learning rate (the step size) matters most. With a tiny value near 0.01, the search crawls. "
        "With a moderate 0.1, it converges smoothly onto the true rate. With a large value near 0.5, the "
        "steps are so big that the search overshoots before it settles.")]
viz += slider_plot(_render_m06, {
    "learning_rate": FloatSlider(value=0.1, min=0.01, max=0.6, step=0.01, readout_format=".2f", description="lr"),
    "epochs": IntSlider(value=100, min=10, max=400, step=10, description="epochs")},
    readout_fn=_read_m06, plot_w="900px")

def _check_t6(ns):
    f = ns.get("gd_step")
    if not callable(f): return False, "Define a function called gd_step(p, g, lr)."
    r1 = float(f(5.0, 2.0, 0.1)); r2 = float(f(0.0, -1.0, 0.5))
    if np.isclose(r1, 4.8) and np.isclose(r2, 0.5):
        return True, "One step against the gradient, scaled by the learning rate."
    if np.isclose(r1, 5.0):  return False, "You return p unchanged. Take one step away from it."
    if np.isclose(r1, 5.2):  return False, "Wrong direction: move against the gradient, not with it."
    if np.isclose(r1, 3.0):  return False, "The step size is missing. Scale the gradient by lr."
    return False, "For p=5, g=2, lr=0.1 the answer is 4.8; you got %s. Return p - lr*g." % fnum(r1)

# 2026-09-27 (Inhalt, nachziehen; eingebaut E10 Teil 4) — a number first, code optional.
def _tv_m06():
    global _t6k, _t6g, _t6lr, _T6
    _t6k, _t6g, _t6lr = TV["gd_k"], TV["gd_g"], TV["gd_lr"]
    _T6 = _t6k - _t6lr * _t6g
_tv_m06()
on_reseed(_tv_m06)

def _ans_t6(v):
    x = v["k"]
    if _near(x, _T6):
        # E17.1 — whole sentences, so each language can order its own words
        return True, (("Right: %g − %g·(%g) = %s per hour. The objective falls with smaller k, "
                       "so the step goes down." if _t6g > 0 else
                       "Right: %g − %g·(%g) = %s per hour. The objective falls with larger k, "
                       "so the step goes up.") % (_t6k, _t6lr, _t6g, fnum(_T6)))
    if _near(x, _t6k + _t6lr * _t6g):
        return False, ("Wrong direction: that step goes <i>uphill</i> on the objective. "
                       "Subtract the gradient, don't add it.")
    if _near(x, _t6k - _t6g):
        return False, "The learning rate is missing: scale the gradient by lr before subtracting."
    if _near(x, _t6lr * _t6g) or _near(x, -_t6lr * _t6g):
        return False, "That is the step alone. The new k is the old k minus that step."
    return False, "New k = old k − lr · g. Mind the sign of g."

practice = [
  personal(lambda: exercise_box("",
      taskline("<b>Take one step of the search by hand.</b>")
      + formula_line(r"$k \leftarrow k - \mathrm{lr}\cdot \dfrac{\partial F}{\partial k}$")
      + "<div>The current guess is <b>k = %g h⁻¹</b>. At that k the objective has the slope "
        "<b>∂F/∂k = %g</b>, and the learning rate is <b>lr = %g</b>. Where does one step put k?</div>"
      % (_t6k, _t6g, _t6lr))),
  numeric_answer([("k", "new k =")], _ans_t6, task="t6", columns=1),
  hint_steps("t6", lambda: [
    "The slope ∂F/∂k points <i>uphill</i>, towards larger values of the objective. Gradient descent "
    "wants to go down. So it moves k the other way, by a small step equal to the learning rate times the "
    "slope. New k = old k − lr · slope.",
    ("Your step is lr · slope = %s · (%s). Subtract it from k = %s. Mind the sign: with a positive "
     "slope, subtracting the step makes k smaller." if _t6g > 0 else
     "Your step is lr · slope = %s · (%s). Subtract it from k = %s. Mind the sign: with a negative "
     "slope, subtracting the step makes k larger.") % (_g3(_t6lr), _g3(_t6g), _g3(_t6k)),
  ], forbid=lambda: (_T6,)),
  code_fold("def gd_step(p, g, lr):\n    # one update of a single parameter\n    return p\n",
            lambda g: _check_t6(g), task="t6", locked_by="t5",
            task_text=('Write <code>gd_step(p, g, lr)</code> that performs one gradient-descent update of '
                       'a single parameter p, given the gradient g of the objective at p and the learning '
                       'rate lr, and returns the new value. '
                       'Example: <code>gd_step(5, 2, 0.1)</code> → <code>4.8</code>.'),
            solution="def gd_step(p, g, lr):\n    return p - lr * g\n"),
]

interp = interpretation_box(
    "The same rule that fits this two-parameter model also trains models with millions of parameters. Only "
    "the number of parameters changes, not the idea. Watch the objective curve: it should fall smoothly to "
    "a plateau. A learning rate that is too small wastes steps. One that is too large makes the search "
    "unstable. So the step size is itself a modelling decision that you have to tune.")

build_chapter(6, "Optimization: Searching the objective", figure="Gradient descent on the rate",
              info=info, viz=viz, practice=practice, interp=interp, task="t6", locked_by="t5")
