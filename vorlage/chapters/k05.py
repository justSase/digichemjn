# Kapitel 5 (Platzhalter) — BAUKASTEN III (E28): Ziel treffen, Code im Kasten, feste Abbildung.
# Bausteine hier: target_exercise (Regler-Ziel; im Lesefenster zwei Felder) · plot_html
# (Abbildung ohne Regler) · math_img · dmath · highlight_code · editable_exercise (Code-Feld
# ohne Wertung, task=None) · editable_runner (Code-Feld mit Ausgabe) · solution_box ·
# center · hint_steps · code_fold (locked_by)
info = note_box(
  "Placeholder: a chapter without a single formula box, with a fixed picture and code to run."
  + dmath(r"$d = |z - z_{\mathrm{target}}|$"))

def _static_k05():
    fig, ax = fixed_canvas(figsize=(5.0, 3.2), left=.12, right=.97, top=.95, bottom=.18)
    theme_axes(ax)
    ax.bar(["A", "B", "C"], [3, 5, 2], color=PAL["z2"])
    ax.set_ylabel("value (placeholder)")
    return fig

body_k5 = [plot_html(_static_k05()),
           center(HTML(value="<div style='text-align:center'>" + math_img(r"$r \cdot e^{i\varphi}$", fs=22, height=40)
                              + "</div>")),
           center(HTML(value="<div style='max-width:640px'>" + highlight_code("def y_von(a, x):\n    return a * x\n")
                              + "</div>")),
           editable_runner("import numpy as np\nprint(np.round(np.linspace(0, 1, 5), 2))\n", height="120px"),
           editable_exercise("def doppelt(x):\n    return ...\n",
                             lambda g: (callable(g.get("doppelt")) and g["doppelt"](3) == 6, "doppelt(3) should be 6.")),
           solution_box("Placeholder: one worked solution.", "def doppelt(x):\n    return 2 * x\n")]

_TGT5 = (1.0 + TV["b"] * 0.2, 1.0)            # personal target (x, y)
on_reseed(lambda: globals().update(_TGT5=(1.0 + TV["b"] * 0.2, 1.0)))
_TTOL5 = 0.3

def _render_target_k05(x=0.0, y=0.0):
    fig, ax = fixed_canvas(figsize=(5.0, 5.0), left=.13, right=.97, top=.97, bottom=.10)
    argand_axes(ax, lim=3.2)
    ax.set_xticks([-3, 0, 3]); ax.set_yticks([-3, 0, 3])
    ax.add_patch(plt.Circle(_TGT5, _TTOL5, color=PAL["warn"], alpha=.35))
    ax.plot([0, x], [0, y], color=PAL["sum"], lw=2.6)
    ax.plot([x], [y], "o", color=PAL["sum"], ms=8)
    return fig

def _ans_t5(v):
    d = np.hypot(v["x"] - _TGT5[0], v["y"] - _TGT5[1])
    if d < _TTOL5:
        return True, "On target (placeholder)."
    return False, "Off by %.2f. Move x first, then y (placeholder)." % d

practice = [
  exercise_box("", taskline("<b>Steer the point into the circle.</b>")
      + "<div>Placeholder: what to move and why. Then press the button.</div>"),
]
practice += target_exercise(_render_target_k05, {
    "x": FloatSlider(value=0.0, min=-3, max=3, step=0.1, description="x"),
    "y": FloatSlider(value=0.0, min=-3, max=3, step=0.1, description="y")},
    _ans_t5, task="t5",
    answer=lambda: {"x": (_TGT5[0], _TTOL5 / 3), "y": (_TGT5[1], _TTOL5 / 3)})
practice += [
  hint_steps("t5", ["Idea: x and y move the point independently (placeholder).",
                    "Working: set x to the circle's centre first (placeholder)."]),
  code_fold("def abstand(x, y, tx, ty):\n    # Abstand zum Ziel\n    return ...\n",
            lambda g: _check_t5(g), task="t5", locked_by="t4",
            task_text="Write <code>abstand(x, y, tx, ty)</code> that returns the distance to the target.",
            solution="import numpy as np\ndef abstand(x, y, tx, ty):\n    return np.hypot(x - tx, y - ty)\n"),
]

def _check_t5(g):
    f = g.get("abstand")
    if not callable(f):
        return False, "Define a function abstand(x, y, tx, ty)."
    for c in ((0, 0, 3, 4), (1, 1, 1, 1), (-1, 2, 2, -2)):
        try:
            w = float(np.hypot(c[0] - c[2], c[1] - c[3]))
            if abs(f(*c) - w) > 1e-6:
                return False, "abstand%s should be %.3f." % (c, w)
        except Exception as e:
            return False, "abstand%s raised %r." % (c, e)
    return True, "Correct."

interp = interpretation_box("Placeholder: what hitting the target shows.")

build_chapter(5, "Fifth chapter title (placeholder)", figure="Fifth figure name (placeholder)",
              info=info, body=body_k5, viz=None,
              practice=practice, interp=interp, task="t5", locked_by="t4")
