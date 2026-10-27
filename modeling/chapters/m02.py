info = note_box(
  "<b>Key idea and link to the previous chapter.</b> Reality exists whether we look or not. What we know "
  "of it comes from <b>observations</b>, and these are incomplete and noisy. So the true relationship "
  "between a system's inputs and outputs stays hidden. A model is a <b>parameterised abstraction</b>: a "
  "simplified description with a few adjustable numbers, its parameters. It approximates the hidden "
  "relationship from quantities we can observe. We set the parameters by comparing what the model "
  "simulates with what we observe" + cite(2) + ". In the visualisation you are the modeller. A hidden "
  "process produces noisy observations, and you adjust a model to match them.")

_m02x = np.linspace(0, 1, 60)
_m02xo = np.linspace(0.05, 0.95, 12)
_m02obs = 4.0 + 3.0*np.sin(2*np.pi*_m02xo) + np.random.default_rng(1).normal(0, 0.8, _m02xo.size)

def _render_m02(model_slope=6.0):
    # FIXED frame: x 0 … 1, y from the slider range (slope −6 … 12 → −2 … 10)
    fig, ax = fixed_canvas(figsize=(6.6, 3.9), left=.11, right=.97, top=.95, bottom=.15)
    theme_axes(ax)
    ax.set_xlim(0, 1); ax.set_ylim(-2.5, 10.5)
    ax.plot(_m02x, 4.0 + 3.0*np.sin(2*np.pi*_m02x), color=PAL["ghost"], lw=2, ls=":",
            label="true process (hidden)")
    ax.scatter(_m02xo, _m02obs, color=PAL["z2"], s=28, zorder=3, label="observations (noisy)")
    ax.plot(_m02x, 4.0 + model_slope*(_m02x - 0.5), color=PAL["z"], lw=2.5, label="your model")
    ax.set_xlabel("observed input"); ax.set_ylabel("response")
    theme_legend(ax, loc="upper right")
    return fig

def _read_m02(model_slope=6.0):
    resid = (4.0 + model_slope*(_m02xo - 0.5)) - _m02obs
    return readout([("slope", "%.1f" % model_slope), ("SSE", "%.2f" % float(np.sum(resid**2)))])

viz = [viz_intro_box("",
        "A hidden true process (dotted) produces a handful of noisy observations (points). Your model "
        "(red line) is kept simple on purpose: it has one adjustable parameter, its slope. Drag the "
        "slider and watch the readout below it. SSE is the sum of squared errors, the squared gaps between "
        "line and points added up. You can lay the line through the middle of the cloud, but a straight "
        "line can never follow the curve. That is the point: every model gives up detail to stay "
        "simple.")]
viz += slider_plot(_render_m02, {"model_slope": FloatSlider(value=6.0, min=-6, max=12, step=0.5,
                                                            description="slope")}, readout_fn=_read_m02)

# 2026-09-27 (Inhalt, ML/Mod-Aufgaben; eingebaut E10 Teil 4) — the standard pair.
def _tv_m02():
    global _q2y, _Q2m, _Q2s
    _q2y = np.array(TV["ob_y"], float)
    _Q2m = float(_q2y.mean())
    _Q2s = float(_q2y.std(ddof=1))
_tv_m02()
on_reseed(_tv_m02)

def _check_t2(ns):
    f = ns.get("mean_sd")
    if not callable(f): return False, "Define a function called mean_sd(obs)."
    m, s = f([2.0, 4.0, 4.0, 6.0])                  # 4, sqrt(8/3)
    if np.isclose(m, 4.0) and np.isclose(s, np.sqrt(8 / 3)):
        return True, "Mean and sample standard deviation (n − 1) both right."
    if np.isclose(m, 4.0) and np.isclose(s, np.sqrt(2.0)): return False, "Divide by n − 1, not n: the sample SD (ddof=1)."
    if np.isclose(m, 4.0) and np.isclose(s, 8 / 3): return False, "That is the variance; take its square root."
    return False, "For 2, 4, 4, 6 the mean is 4 and the SD 1.633; got %s and %s." % (fnum(m), fnum(s))

def _ans_t2(v):
    m, s = v["m"], v["s"]
    if not _near(m, _Q2m):
        return False, "The mean is the sum of the four readings divided by 4."
    if _near(s, _Q2s):
        return True, ("Right: %s ± %s. The true value is hidden; four readings pin it down only this "
                      "well. Every model is calibrated against numbers like these." % (fnum(_Q2m), fnum(_Q2s)))
    if _near(s, float(_q2y.std(ddof=0))):
        return False, "You divided by n. For a sample, divide the sum of squares by n − 1."
    if _near(s, _Q2s ** 2):
        return False, "That is the variance. The standard deviation is its square root."
    return False, "SD = √( Σ(yᵢ − mean)² / (n − 1) )."

practice = [
  personal(lambda: exercise_box("",
      taskline("<b>What do four noisy observations tell you?</b>")
      + formula_line(r"$\bar y=\frac{1}{n}\sum y_i,\qquad s=\sqrt{\frac{1}{n-1}\sum (y_i-\bar y)^2}$")
      + "<div>The same plasma sample was assayed four times (simulated readings): <b>%s mg/L</b>. "
        "Compute the mean and the sample standard deviation.</div>" % ", ".join("%d" % y for y in _q2y))),
  numeric_answer([("m", "mean ="), ("s", "SD =")], _ans_t2, task="t2"),
  hint_steps("t2", lambda: [
    "The mean is the centre of the readings: add them and divide by how many there are. The standard "
    "deviation says how far a single reading typically sits from that centre: take each reading's "
    "distance from the mean and square it. Add the squares, divide by <b>n − 1</b> (one less than the "
    "number of readings, because the mean came from the same four) and take the square root.",
    "Your four readings add up to %d, and there are 4 of them. Once you have the mean, subtract it from "
    "each of %s, square the four differences, add them, divide by 3 and take the square root."
    % (int(round(_q2y.sum())), ", ".join("%d" % y for y in _q2y)),
  ], forbid=lambda: (_Q2m, _Q2s)),
  code_fold("import numpy as np\n\n"
            "def mean_sd(obs):\n"
            "    return 0.0, 0.0\n",
            lambda g: _check_t2(g), task="t2", locked_by="t1",
            task_text=('Write <code>mean_sd(obs)</code> that takes a list of repeated readings and returns '
                       'their mean and their sample standard deviation (divided by n − 1) as a pair. '
                       'Example: <code>mean_sd([2, 4, 4, 6])</code> → <code>(4.0, 1.633…)</code>.'),
            solution="import numpy as np\n\n"
                     "def mean_sd(obs):\n"
                     "    y = np.asarray(obs, float)\n"
                     "    return float(y.mean()), float(y.std(ddof=1))\n"),
]

interp = interpretation_box(
    "You never see the true process, only the points. You shape the model by making its disagreement with "
    "them smaller. That is what a parameterised abstraction means: the parameters hold our best compromise "
    "with incomplete, uncertain data. Choosing a straight line here is a modelling decision. The error "
    "that remains is the price of that simplicity.")

# E19.8 — from "Remarks": the limits of simplification and measurement, in red
warn = warn_box(
  "<b>Simplification has a range.</b> A model keeps only the processes judged to matter. It is valid only "
  "within its assumptions and the range of data behind it, and extrapolation beyond that range is risky. "
  "<b>A model is no better than its measurements.</b> It can be no more valid than its data are accurate, "
  "and transferring a model across biological scales often breaks its predictive structure.")

build_chapter(2, "Reality, observation and the role of models", figure="Model against noisy observations",
              info=info, viz=viz, practice=practice, interp=interp, body=[warn], task="t2", locked_by="t1")
