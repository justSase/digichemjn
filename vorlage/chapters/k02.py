# Kapitel 2 (Platzhalter) — Aufbau jedes Kapitels:
#   info      Idee + Formel (concept_box)
#   viz       feste Abbildung (plot_html; mit Regler: k01)
#   practice  Rechenaufgabe (numeric_answer) + Hinweise + optionale Coding-Aufgabe (code_fold)
#   interp    Kernaussage (interpretation_box)
info = concept_box(
  "Placeholder: the idea of this chapter in two to four sentences" + cite(1) + ".",
  r"$y = a \cdot x$",
  variables=[("a", "slope (placeholder)"), ("x", "input"), ("y", "output")])

def _render_k02(a=2.0):
    x = np.linspace(0, 10, 200)
    fig, ax = fixed_canvas(figsize=(6.6, 3.9), left=.12, right=.97, top=.95, bottom=.16)
    theme_axes(ax)
    ax.set_xlim(0, 10); ax.set_ylim(0, 100)
    ax.set_xticks([0, 5, 10]); ax.set_yticks([0, 50, 100])
    ax.plot(x, a * x, color=PAL["z2"], lw=2.4)
    ax.set_xlabel("x"); ax.set_ylabel("y")
    return fig

# E28: hier eine feste Abbildung ohne Regler (plot_html) — Regler zeigt k01; das spart dem
# Lesefenster fünf vorberechnete Bilder (Kernel-Lauf der Vorlage < ½ von Complex)
viz = [viz_intro_box("", "Placeholder: what the figure shows and what to look for.")]
viz += [plot_html(_render_k02())]

# eigener Name je Kapitel: alles läuft in EINEM Namensraum (k01 hat _a)
_a2 = TV["b"]
on_reseed(lambda: globals().update(_a2=TV["b"]))

def _ans_t2(v):
    if abs(v["y"] - 4 * _a2) > tol():
        return False, "Not yet. Put x = 4 into y = a·x. You entered %g." % v["y"]
    return True, "Correct: y = %d · 4 = %d." % (_a2, 4 * _a2)

practice = [
  personal(lambda: exercise_box("", taskline("<b>Compute y for x = 4.</b>")
      + "<div>Your personal value is <b>a = " + str(_a2) + "</b>.</div>")),
  numeric_answer([("y", "y =")], _ans_t2, task="t2", answer=lambda: {"y": 4 * _a2}),
  hint_steps("t2", lambda: [
    "Idea: y = a·x, so just substitute.",
    "Working: y = %d · 4." % _a2,
  ], forbid=lambda: (4 * _a2,)),
  code_fold("def y_von(a, x):\n    # return a·x\n    return ...\n",
            lambda g: _check_t2(g), task="t2", locked_by="t1",
            task_text="Write <code>y_von(a, x)</code> that returns a·x. Example: <code>y_von(2, 3)</code> → <code>6</code>.",
            solution="def y_von(a, x):\n    return a * x\n"),
]

def _check_t2(g):
    f = g.get("y_von")
    if not callable(f):
        return False, "Define a function y_von(a, x)."
    for a, x in ((2, 3), (0, 5), (_a2, 7)):
        try:
            if abs(f(a, x) - a * x) > 1e-9:
                return False, "y_von(%g, %g) should be %g." % (a, x, a * x)
        except Exception as e:
            return False, "y_von(%g, %g) raised %r." % (a, x, e)
    return True, "Correct."

interp = interpretation_box("Placeholder: the one statement to take away from this chapter.")

build_chapter(2, "Second chapter title (placeholder)", figure="Second figure name (placeholder)", info=info, viz=viz,
              practice=practice, interp=interp, task="t2", locked_by="t1")
