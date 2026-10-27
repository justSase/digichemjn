info = note_box(
  "<b>Key idea and link to the previous chapters.</b> A model that fits its calibration data perfectly is "
  "not necessarily good. What matters is <b>generalisation</b>: how well it predicts new data. This depends "
  "on the balance between <b>model complexity</b> and <b>data availability</b>" + cite(6) + ". A model that "
  "is too simple <b>underfits</b> and shows a systematic error (<b>bias</b>). A model that is too complex "
  "<b>overfits</b>: it follows the noise, and its predictions scatter strongly (high <b>variance</b>). A "
  "single fit can mislead. So generalisation is estimated on independent data, with a <b>train&ndash;test "
  "split</b>, or more robustly with <b>cross-validation</b> and <b>bootstrap</b> resampling. The "
  "visualisation fits polynomials of growing degree. It compares the error on the training half with the "
  "error on a held-out test half.")

_m07xx = np.linspace(0, 1, 200)
_m07xt, _m07yt = _xp[::2], _yp[::2]        # train (held-in)
_m07xv, _m07yv = _xp[1::2], _yp[1::2]      # test  (held-out)

def _fit_m07(degree):
    return np.poly1d(np.polyfit(_m07xt, _m07yt, int(degree)))

def _render_m07(degree=3):
    # FIXED frame: x 0 … 1, y −2 … 2, whatever the degree
    fig, ax = fixed_canvas(figsize=(6.6, 3.9), left=.11, right=.97, top=.95, bottom=.15)
    theme_axes(ax)
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-2, 2)
    ax.scatter(_m07xt, _m07yt, color=PAL["z2"], s=26, zorder=3, label="train")
    ax.scatter(_m07xv, _m07yv, color=PAL["z"], s=26, zorder=3, label="test")
    ax.plot(_m07xx, _fit_m07(degree)(_m07xx), color=PAL["sum"], lw=2, label="polynomial")
    ax.plot(_m07xx, _truth(_m07xx), color=PAL["ghost"], ls=":", lw=1.5, label="true process")
    ax.set_xlabel("input x"); ax.set_ylabel("response")
    theme_legend(ax, loc="upper right", ncol=2, fontsize=8)
    return fig

def _read_m07(degree=3):
    fit = _fit_m07(degree)
    trn = float(np.mean((_m07yt - fit(_m07xt))**2)); tst = float(np.mean((_m07yv - fit(_m07xv))**2))
    return readout([("degree", "%d" % int(degree)), ("train MSE", "%.3f" % trn),
                    ("test MSE", "%.3f" % tst), ("gap", "%.3f" % (tst - trn))])

viz = [viz_intro_box("",
        "Blue points are the training half, red points the held-out test half. The green curve is a "
        "polynomial of the degree you choose, and the dotted line is the true process. Watch the two error "
        "numbers together. At degree 1 both are high: the model is too simple and biased (underfitting). "
        "Around degree 3 both are low and close to each other. This is the sweet spot. Push the degree "
        "towards 12, and the green curve wriggles through every training point. The training error collapses, "
        "but the test error climbs steeply. This is the typical sign of overfitting and high variance.")]
viz += slider_plot(_render_m07, {"degree": IntSlider(value=3, min=1, max=12, step=1, description="degree")},
                   readout_fn=_read_m07)

# 2026-09-27 (Inhalt, ML/Mod-Aufgaben; eingebaut E10 Teil 4) — the standard pair.
def _tv_m07():
    global _q7y, _q7p, _q7tr, _q7e, _Q7, _Q7g
    _q7y, _q7p, _q7tr = np.array(TV["ov_y"]), np.array(TV["ov_p"]), TV["ov_tr"]
    _q7e = [round(float(e), 1) for e in _q7y - _q7p]
    _Q7 = float(np.mean((_q7y - _q7p) ** 2))
    _Q7g = _Q7 - _q7tr
_tv_m07()
on_reseed(_tv_m07)

def _check_t7(ns):
    f = ns.get("test_mse")
    if not callable(f): return False, "Define a function called test_mse(y, yhat)."
    a = float(f([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])); b = float(f([0.0, 0.0, 0.0], [1.0, 1.0, 2.0]))
    if np.isclose(a, 0.0) and np.isclose(b, 2.0):
        return True, "The mean of the squared errors, nothing else."
    if np.isclose(b, 6.0): return False, "That is the sum. The MSE is the <b>mean</b> of the squared errors."
    if np.isclose(b, np.sqrt(2.0)): return False, "No square root: MSE, not RMSE."
    return False, "Expected 0 and 2; got %s and %s." % (fnum(a), fnum(b))

def _ans_t7(v):
    m, g = v["m"], v["g"]
    if not _near(m, _Q7):
        if _near(m, 3 * _Q7):
            return False, "That is the sum of the squared errors. Divide by the number of test points, 3."
        if _near(m, float(np.sqrt(_Q7))):
            return False, "That is the square root of the MSE. Leave the root off."
        return False, "For each test point, error = observed − predicted. Square, add, and divide by 3."
    if _near(g, _Q7g):
        return True, ("Right: test MSE %s against %s on the training half, a gap of %s. %s"
                      % (fnum(_Q7), fnum(_q7tr), fnum(_Q7g),
                         "A gap this large shows that the model memorised the training noise." if _Q7g > 2 * _q7tr
                         else "A small gap: the model generalises about as well as it fits."))
    if _near(g, -_Q7g):
        return False, "The gap is test MSE <b>minus</b> training MSE."
    return False, "Gap = your test MSE − the training MSE %g." % _q7tr

practice = [
  personal(lambda: exercise_box("",
      taskline("<b>Judge a calibrated model on data it has not seen.</b>")
      + formula_line(r"$\mathrm{MSE}_{\mathrm{test}}=\frac{1}{n}\sum (y_i-\hat y_i)^2,\qquad \mathrm{gap}=\mathrm{MSE}_{\mathrm{test}}-\mathrm{MSE}_{\mathrm{train}}$")
      + "<div>A polynomial reached <b>MSE = %g</b> on its training half. On three held-out points "
        "(simulated) it predicts <b>ŷ = %s</b>, where the observations were <b>y = %s</b>. Compute the "
        "test MSE and the gap.</div>" % (_q7tr, ", ".join("%g" % x for x in _q7p), ", ".join("%g" % x for x in _q7y)))),
  numeric_answer([("m", "test MSE ="), ("g", "gap =")], _ans_t7, task="t7"),
  hint_steps("t7", lambda: [
    "The test MSE is the <i>mean</i> of the squared errors on the held-out points. For each point, error "
    "= observed − predicted. Square each error, add, and divide by the number of points. The gap is test "
    "MSE minus training MSE. If the gap is large compared with the training error, the model has learned "
    "noise that does not come back on new data.",
    "Your three test errors y − ŷ are %s. Square each, add the three squares and divide by 3. Then "
    "subtract the training MSE given in the exercise."
    % ", ".join(("%.1f" % e).replace("-", "−") for e in _q7e),
  ], forbid=lambda: (_Q7, _Q7g)),
  code_fold("def test_mse(y, yhat):\n"
            "    return 0.0\n",
            lambda g: _check_t7(g), task="t7", locked_by="t6",
            task_text=('Write <code>test_mse(y, yhat)</code> that returns the mean squared error between '
                       'observed values y and predicted values yhat (two lists of the same length). '
                       'Example: <code>test_mse([0, 0, 0], [1, 1, 2])</code> → <code>2.0</code>.'),
            solution="def test_mse(y, yhat):\n"
                     "    return sum((a - b) ** 2 for a, b in zip(y, yhat)) / len(y)\n"),
]

interp = interpretation_box(
    "In practice, the gap between training and test error reveals overfitting. When the gap opens up, the "
    "model memorises noise instead of learning the process. The best model is the simplest one whose test "
    "error is still low. This is why a model is always judged on data it did not see. Cross-validation goes "
    "one step further: it rotates which part of the data is held out (the fold), and so gives a more stable "
    "estimate than a single split.")

# E19.8 — from "Remarks": the overfitting warning, in red
warn = warn_box(
  "<b>A low calibration error does not guarantee good predictions.</b> Judge a model on held-out data "
  "that it did not see during calibration.")

build_chapter(7, "Evaluation: Under- and overfitting", figure="Train and test error",
              info=info, viz=viz, practice=practice, interp=interp, body=[warn], task="t7", locked_by="t6")
