_intro = (
  "<b>Key idea and link to the previous chapter.</b> Some quantities cannot be worked out exactly, for "
  "example when many parameters vary at once. Then we estimate them by <b>repeated random sampling</b>. "
  "This is the Monte-Carlo method. It is the basis of global sensitivity analysis and of uncertainty "
  "quantification (stating how uncertain a prediction is). The classic example estimates &#960; from the "
  "fraction of random points that land inside a quarter circle. That fraction approximates &#960;/4, "
  "because the quarter circle fills exactly &#960;/4 of the unit square.")

info = concept_box(_intro, r"$\pi \approx \dfrac{4\,r}{n}$",
    variables=[("&#960;", "the quantity being estimated"),
               ("r", "number of random points inside the quarter circle"),
               ("n", "total number of random points sampled")])

_m09th = np.linspace(0, np.pi/2, 100)

def _pts_m09(n):
    rr = np.random.default_rng(0)
    x = rr.random(int(n)); y = rr.random(int(n))
    return x, y, x*x + y*y <= 1.0

def _render_m09(n=500):
    # FIXED frame: the unit square
    x, y, inside = _pts_m09(n)
    fig, ax = fixed_canvas(figsize=(5.0, 5.0), left=.12, right=.96, top=.96, bottom=.11)
    theme_axes(ax, equal=True)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.scatter(x[inside], y[inside], s=6, color=PAL["z2"], alpha=.7)
    ax.scatter(x[~inside], y[~inside], s=6, color=PAL["z"], alpha=.7)
    ax.plot(np.cos(_m09th), np.sin(_m09th), color=PLOT_INK, lw=1.5)
    return fig

def _read_m09(n=500):
    x, y, inside = _pts_m09(n)
    est = 4.0 * float(np.mean(inside))
    return readout([("n", "%d" % int(n)), ("inside", "%d" % int(inside.sum())),
                    ("π ≈", "%.4f" % est), ("error", "%.4f" % abs(est - np.pi))])

viz = [viz_intro_box("",
        "Each dot is a random point in the unit square. It is blue if it falls inside the quarter circle and "
        "red if it falls outside. Four times the blue fraction estimates &#960;. With only 50 points the "
        "estimate jumps around. As you raise the count towards several thousand, it settles close to the "
        "true value. The error shrinks only slowly, roughly like one over the square root of the number of "
        "samples. This slow convergence is the typical price of Monte-Carlo methods.")]
viz += slider_plot(_render_m09, {"n": IntSlider(value=500, min=50, max=5000, step=50, description="n points")},
                   readout_fn=_read_m09)

def _check_t9(ns):
    f = ns.get("estimate_pi")
    if not callable(f): return False, "Define a function called estimate_pi(x, y)."
    r = np.random.default_rng(3); N = 40000
    x = r.random(N); y = r.random(N); val = float(f(x, y))
    if np.isclose(val, np.pi, atol=0.05):
        return True, "Four times the inside fraction: %s for 40 000 points." % fnum(val)
    if np.isclose(val, np.pi/4, atol=0.02):
        return False, "That is the fraction itself (π/4). Multiply by 4 to estimate π."
    if 0.9 < val < 1.1:
        return False, "You seem to have returned the mean of the inside mask. Multiply this fraction by 4."
    return False, "Expected roughly π (3.14); got %s. Count x²+y² ≤ 1, take the mean, multiply by 4." % fnum(val)

# 2026-09-27 (Inhalt, nachziehen; eingebaut E10 Teil 4) — a number first, code optional.
def _tv_m09():
    global _t9n, _t9r, _T9
    _t9n, _t9r = TV["mc_n"], TV["mc_r"]
    _T9 = 4.0 * _t9r / _t9n
_tv_m09()
on_reseed(_tv_m09)

def _ans_t9(v):
    x = v["pi"]
    if _near(x, _T9):
        return True, ("Right: 4 · %d / %d = %s, which differs from π by %s. With four times as many "
                      "points, the typical error would only halve." % (_t9r, _t9n, fnum(_T9), fnum(abs(_T9 - np.pi))))
    if _near(x, _t9r / _t9n):
        return False, "That is the inside fraction, which estimates π/4. Multiply by 4."
    if _near(x, 4.0 * _t9n / _t9r) or _near(x, _t9n / _t9r):
        return False, "The fraction is upside down: points inside divided by points thrown."
    if _near(x, np.pi):
        return False, ("That is π itself, not what <i>your</i> sample estimates. The exercise asks "
                       "what these %d points say." % _t9n)
    return False, "π ≈ 4 · (points inside) / (points thrown)."

practice = [
  personal(lambda: exercise_box("",
      taskline("<b>Estimate π from a sample.</b>")
      + formula_line(r"$\pi \approx 4\cdot\dfrac{r}{n}$")
      + "<div>Of <b>n = %d</b> random points in the unit square, <b>r = %d</b> fell inside the "
        "quarter circle. What does this sample estimate for π?</div>" % (_t9n, _t9r))),
  numeric_answer([("pi", "π ≈")], _ans_t9, task="t9", columns=1),
  hint_steps("t9", lambda: [
    "The quarter circle covers the fraction π/4 of the unit square. So the fraction of your points that "
    "fell inside it estimates π/4, and four times that fraction estimates π. The answer here is what your "
    "sample says, not the π you know.",
    "Your fraction is r / n = %d / %d: points inside divided by points thrown. Multiply it by 4." % (_t9r, _t9n),
  ], forbid=lambda: (_T9,)),
  code_fold("def estimate_pi(x, y):\n    x = np.asarray(x, float); y = np.asarray(y, float)\n"
            "    return 0.0\n",
            lambda g: _check_t9(g), task="t9", locked_by="t8",
            task_text=('Write <code>estimate_pi(x, y)</code> that takes the coordinates of random points in '
                       'the unit square (two arrays of the same length) and returns the Monte-Carlo '
                       'estimate of π: four times the fraction with x² + y² ≤ 1. '
                       'Example: 40 000 random points → about <code>3.14</code>.'),
            solution="def estimate_pi(x, y):\n    x = np.asarray(x, float); y = np.asarray(y, float)\n"
                     "    inside = x**2 + y**2 <= 1.0\n    return 4.0 * float(np.mean(inside))\n"),
]

interp = interpretation_box(
    "Monte-Carlo turns a hard integral into simple counting. It also works for problems with many uncertain "
    "parameters, where exact formulas are out of reach. Its weakness is the slow convergence: to halve the "
    "error, you need roughly four times as many samples. Used well, it lets you pass parameter uncertainty "
    "through a model. You can then report a prediction together with a credible range around it.")

build_chapter(9, "Monte-Carlo estimation", figure="π from random points",
              info=info, viz=viz, practice=practice, interp=interp, task="t9", locked_by="t8")
