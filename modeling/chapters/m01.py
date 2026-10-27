info = note_box(
  "<b>Key idea.</b> A <b>model</b> is a simplified picture of a real system, built for one purpose. We "
  "use it to explain observations and to predict what has not been measured yet. You do not build it in "
  "one go: you work through stages and return to earlier ones as you learn" + cite(3) + "."
  "<div style='margin:14px 0'>" + make_table(
      ["stage", "question it answers", "output"],
      [["perceptual", "which processes matter?", "a mental picture of the system"],
       ["conceptual", "which equations link them?", "state variables and governing equations"],
       ["procedural", "how do we compute it?", "code and a numerical solver"]], scheme="info") + "</div>"
  "The <b>perceptual</b> model is what you understand about the system from observation, your own study, "
  "instruments and the literature. The <b>conceptual</b> model writes that understanding as equations "
  "between the system's states. The <b>procedural</b> model puts those equations into code so a computer "
  "can simulate them. Drug action spans many scales of time and size: from receptor binding in "
  "milliseconds to physiological change over days, from a single molecule to a whole body. So the central "
  "decision in modelling is what to keep and what to leave out" + cite(1) + "."
  "<br><br>One example runs through this whole notebook: a small <b>pharmacokinetic</b> model, which "
  "describes how the concentration of a drug given into a vein falls over time.")

# 2026-09-27 (Inhalt, ML/Mod-Figuren; eingebaut E10 Teil 4) — the figure: typical
# time scales of drug action on one logarithmic axis, and the window a model
# resolves (time step Δt to horizon T). ORDERS OF MAGNITUDE for illustration,
# not measured values.
_fm1 = [("receptor binding", 1e-3), ("signal transduction", 1.0), ("distribution", 6e2),
        ("elimination half-life", 1.4e4), ("physiological adaptation", 3e5)]

def _render_m01(log_dt=1.0, log_T=5.0):
    # FIXED frame: the sliders run −4 … 6, the frame is −4.5 … 6.5 and never moves
    fig, ax = fixed_canvas(figsize=(6.6, 3.4), left=.04, right=.97, top=.95, bottom=.22)
    theme_axes(ax, grid=False)
    ax.set_xlim(-4.5, 6.5); ax.set_ylim(-0.2, 1.25); ax.set_yticks([])
    lo, hi = min(log_dt, log_T), max(log_dt, log_T)
    ax.axvspan(lo, hi, color=PAL["z2"], alpha=.14, lw=0)
    ax.axvline(lo, color=PAL["z2"], lw=1.8); ax.axvline(hi, color=PAL["z2"], lw=1.8)
    for i, (name, t) in enumerate(_fm1):
        x = np.log10(t); inside = lo <= x <= hi
        yy = 0.18 + 0.2 * i
        col = PAL["sum"] if inside else PAL["ghost"]
        ax.plot([x], [yy], "o", ms=10, color=col, zorder=3)
        ax.text(x + (0.18 if x < 3.5 else -0.18), yy, name, color=col, fontsize=9, va="center",
                ha="left" if x < 3.5 else "right")
    ticks = [-3, 0, 1.778, 3.556, 4.936, 5.782]
    ax.set_xticks(ticks); ax.set_xticklabels(["1 ms", "1 s", "1 min", "1 h", "1 d", "1 wk"])
    ax.set_xlabel("time scale (logarithmic; typical orders of magnitude, illustrative)")
    return fig

def _read_m01(log_dt=1.0, log_T=5.0):
    lo, hi = min(log_dt, log_T), max(log_dt, log_T)
    kept = sum(1 for _, t in _fm1 if lo <= np.log10(t) <= hi)
    return readout([("Δt", "10^%.1f s" % lo), ("T", "10^%.1f s" % hi),
                    ("orders spanned", "%.1f" % (hi - lo)), ("steps T/Δt", "%.0e" % 10 ** (hi - lo)),
                    ("processes resolved", "%d of %d" % (kept, len(_fm1)))])

viz = [viz_intro_box("",
    "Five processes that decide how a drug acts, placed on one time axis by their typical order of "
    "magnitude (illustrative, not measured). The blue window is what one model resolves: from its time "
    "step <b>Δt</b> (left slider, as a power of ten in seconds) to its horizon <b>T</b> (right slider). "
    "Processes inside the window turn green. Try to catch receptor binding <i>and</i> physiological "
    "adaptation in one window, and read off how many time steps that would take. That number is the reason "
    "a modeller first chooses which scales to keep and treats the rest as instantaneous or as constant.")]
viz += slider_plot(_render_m01, {"log_dt": FloatSlider(value=1.0, min=-4.0, max=6.0, step=0.5,
                                                       description="log₁₀ Δt"),
                                 "log_T":  FloatSlider(value=5.0, min=-4.0, max=6.0, step=0.5,
                                                       description="log₁₀ T")}, readout_fn=_read_m01)

# 2026-09-27 (Inhalt, ML/Mod-Aufgaben; eingebaut E10 Teil 4) — the standard
# pair: a number first, code optional. Personal numbers follow a reseed in place.
def _tv_m01():
    global _q1f, _q1s, _Q1
    _q1f, _q1s = TV["sc_fast"], TV["sc_slow"]
    _Q1 = float(np.log10(_q1s * 3600 * 1000 / _q1f))
_tv_m01()
on_reseed(_tv_m01)

def _check_t1(ns):
    f = ns.get("orders")
    if not callable(f): return False, "Define a function called orders(t_fast_ms, t_slow_h)."
    a = float(f(1, 1)); b = float(f(10, 10))        # 1 h / 1 ms = 3.6e6
    if np.isclose(a, np.log10(3.6e6)) and np.isclose(b, np.log10(3.6e6)):
        return True, "Both conversions right: the units cancel only after hours become milliseconds."
    if np.isclose(a, 0.0): return False, "Convert first: hours to milliseconds (· 3600 · 1000), then compare."
    if np.isclose(a, np.log(3.6e6)): return False, "Orders of magnitude are counted with log10, not ln."
    return False, "1 h against 1 ms is log10(3 600 000) ≈ 6.56; you got %s." % fnum(a)

def _ans_t1(v):
    x = v["o"]
    if _near(x, _Q1):
        return True, ("Right: log10(%d h / %d ms) = %s. A single model cannot resolve both ends; "
                      "deciding which scale to keep is the first modelling decision." % (_q1s, _q1f, fnum(_Q1)))
    if _near(x, float(np.log10(_q1s / _q1f))):
        return False, "The units differ: convert the hours to milliseconds (1 h = 3 600 000 ms) before dividing."
    if _near(x, float(np.log10(_q1s * 3600 / _q1f))):
        return False, "You converted hours to seconds, but the fast time is in <b>milli</b>seconds: you need one more factor of 1000."
    if _near(x, float(np.log(_q1s * 3600 * 1000 / _q1f))):
        return False, "That is the natural log. Orders of magnitude are powers of ten: log10."
    if _near(x, _q1s * 3600 * 1000 / _q1f):
        return False, "That is the ratio itself. The question asks for its order of magnitude: log10 of it."
    return False, "Ratio = (slow time in ms) / (fast time in ms); orders of magnitude = log10 of that ratio."

practice = [
  personal(lambda: exercise_box("",
      taskline("<b>How far apart are the scales a drug model must span?</b>")
      + formula_line(r"$\mathrm{orders}=\log_{10}\dfrac{t_{\mathrm{slow}}}{t_{\mathrm{fast}}}$")
      + "<div>A receptor binding event takes about <b>%d ms</b>; the physiological change it triggers "
        "unfolds over about <b>%d h</b>. How many orders of magnitude lie between the two time scales? "
        "Two decimals are enough.</div>" % (_q1f, _q1s))),
  numeric_answer([("o", "orders =")], _ans_t1, task="t1", columns=1),
  hint_steps("t1", lambda: [
    "An order of magnitude is a factor of ten. First put both times in the <i>same unit</i> (an hour "
    "and a millisecond differ by a factor of 3 600 000). Then ask how many factors of ten lie between "
    "them. That count is log₁₀ of their ratio.",
    "Your slow time is %d h = %d × 3 600 000 ms = %s ms. Divide it by your fast time, %d ms, and "
    "take log₁₀ of the ratio (the <i>log</i> key of a calculator, not <i>ln</i>)."
    % (_q1s, _q1s, "{:,}".format(_q1s * 3600000).replace(",", " "), _q1f),
  ], forbid=lambda: (_Q1,)),
  code_fold("import numpy as np\n\n"
            "def orders(t_fast_ms, t_slow_h):\n"
            "    return 0.0\n",
            lambda g: _check_t1(g), task="t1",
            task_text=('Write <code>orders(t_fast_ms, t_slow_h)</code> that returns how many orders of '
                       'magnitude lie between a fast time in milliseconds and a slow time in hours: '
                       'log₁₀ of their ratio, after both are in the same unit. '
                       'Example: <code>orders(1, 1)</code> → <code>6.556…</code> (1 h = 3 600 000 ms).'),
            solution="import numpy as np\n\n"
                     "def orders(t_fast_ms, t_slow_h):\n"
                     "    return float(np.log10(t_slow_h * 3600 * 1000 / t_fast_ms))\n"),
]

interp = interpretation_box(
    "Six or seven orders of magnitude separate the fastest and the slowest process a drug model could "
    "include. No single model resolves all of them. It picks a window and treats anything faster as "
    "instantaneous and anything slower as constant. This choice comes before any equation is written. "
    "When a model fails, it is the first thing to question.")

# the first chapter is the one the reader stands in when the notebook finishes
# loading, so it is the one chapter that opens by itself (as in Complex)
# E19.8 — from "Remarks": the warning that holds throughout, in red
warn = warn_box(
  "<b>All models are wrong, but some are useful</b>" + cite(8) + ". Every model in this notebook is a "
  "deliberate simplification. Always check its output against measured data and domain knowledge. A "
  "model earns trust through calibration and validation, not through elegance. Treat any model as a fast "
  "but fallible assistant: state its assumptions, quantify its uncertainty, and check its claims against "
  "primary, measured sources.")

build_chapter(1, "What is a model?", figure="Time scales of drug action", info=info, viz=viz,
              practice=practice, interp=interp, body=[warn], task="t1", chapter_open=True)
