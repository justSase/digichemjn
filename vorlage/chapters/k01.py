# Kapitel 1 (Platzhalter) — Aufbau jedes Kapitels:
#   info      Idee + Formel (concept_box)
#   viz       Abbildung mit Regler (slider_plot)
#   practice  Rechenaufgabe (numeric_answer) + Hinweise + optionale Coding-Aufgabe (code_fold)
#   interp    Kernaussage (interpretation_box)
info = concept_box(
  "Placeholder: the idea of this chapter in two to four sentences" + cite(1) + ".",
  r"$y = a \cdot x$",
  variables=[("a", "slope (placeholder)"), ("x", "input"), ("y", "output")])

def _render_k01(a=2.0):
    x = np.linspace(0, 10, 200)
    fig, ax = fixed_canvas(figsize=(6.6, 3.9), left=.12, right=.97, top=.95, bottom=.16)
    theme_axes(ax)
    ax.set_xlim(0, 10); ax.set_ylim(0, 100)
    ax.set_xticks([0, 5, 10]); ax.set_yticks([0, 50, 100])   # wenige Marken: schneller (Lesefenster-Bilder)
    ax.plot(x, a * x, color=PAL["z2"], lw=2.4)
    ax.set_xlabel("x"); ax.set_ylabel("y")
    return fig

viz = [viz_intro_box("", "Placeholder: what the slider shows and what to look for.")]
viz += slider_plot(_render_k01, {"a": FloatSlider(value=2.0, min=0, max=10, step=0.5, description="a")})

_a = TV["a"]
on_reseed(lambda: globals().update(_a=TV["a"]))

def _ans_t1(v):
    if abs(v["y"] - 3 * _a) > tol():
        return False, "Not yet. Put x = 3 into y = a·x. You entered %g." % v["y"]
    return True, "Correct: y = %d · 3 = %d." % (_a, 3 * _a)

practice = [
  personal(lambda: exercise_box("", taskline("<b>Compute y for x = 3.</b>")
      + "<div>Your personal value is <b>a = " + str(_a) + "</b>.</div>")),
  numeric_answer([("y", "y =")], _ans_t1, task="t1", answer=lambda: {"y": 3 * _a}),
  hint_steps("t1", lambda: [
    "Idea: y = a·x, so just substitute.",
    "Working: y = %d · 3." % _a,
  ], forbid=lambda: (3 * _a,)),
  code_fold("def y_von(a, x):\n    # return a·x\n    return ...\n",
            lambda g: _check_t1(g), task="t1",
            task_text="Write <code>y_von(a, x)</code> that returns a·x. Example: <code>y_von(2, 3)</code> → <code>6</code>.",
            solution="def y_von(a, x):\n    return a * x\n"),
]

def _check_t1(g):
    f = g.get("y_von")
    if not callable(f):
        return False, "Define a function y_von(a, x)."
    for a, x in ((2, 3), (0, 5), (_a, 7)):
        try:
            if abs(f(a, x) - a * x) > 1e-9:
                return False, "y_von(%g, %g) should be %g." % (a, x, a * x)
        except Exception as e:
            return False, "y_von(%g, %g) raised %r." % (a, x, e)
    return True, "Correct."

interp = interpretation_box("Placeholder: the one statement to take away from this chapter.")

build_chapter(1, "Chapter title (placeholder)", figure="Figure name (placeholder)", info=info, viz=viz,
              practice=practice, interp=interp, task="t1", chapter_open=True)
