# Kapitel 3 (Platzhalter) — BAUKASTEN I (E28): Auswahl, Tabelle, zwei Regler mit Menü.
# Jeder Baustein des Toolkits steht mindestens einmal in der Vorlage (Tabelle in
# ANLEITUNG.md, Test tests/test_vorlage_cover.py). Hier:
#   intro=note_box (Kurzsatz vor dem Kasten) · concept_box mit constants · info_box (ältere
#   Formelkarte) · warn_box · make_table · fnum · readout · slider_plot mit 2 Reglern + Menü
#   (Dropdown) + readout_fn · theme_legend · choice_answer · hint_steps · code_fold (locked_by)
#   · interpretation_box mit Titel · Literatur cite(2)
intro_k3 = note_box("Placeholder: one sentence that links this chapter to the previous one.")
info = concept_box(
  "Placeholder: the idea of this chapter, now with a constant" + cite(2) + ".",
  r"$y = a \cdot x + b_0$",
  variables=[("a", "slope (placeholder)"), ("x", "input"), ("y", "output")],
  constants=[("<b><i>b</i><sub>0</sub></b> = 1", "fixed offset (placeholder)")])
body_k3 = [info_box(r"$y(0) = b_0$", [("b₀", "value at x = 0 (placeholder)")]),
           warn_box("<b>Placeholder limit:</b> where this simple model stops being right.")]

def _render_k03(a=2.0, b=1.0, form="line"):
    x = np.linspace(0, 10, 120)
    fig, ax = fixed_canvas(figsize=(6.6, 3.9), left=.12, right=.97, top=.95, bottom=.16)
    theme_axes(ax)
    ax.set_xlim(0, 10); ax.set_ylim(0, 110)
    ax.set_xticks([0, 5, 10]); ax.set_yticks([0, 50, 100])
    y = a * x + b if form == "line" else a * x ** 2 / 10 + b
    ax.plot(x, y, color=PAL["z2"], lw=2.4, label=form)
    ax.plot([0], [b], "o", color=PAL["z"], ms=7, label="y(0)")
    theme_legend(ax, loc="upper left")
    ax.set_xlabel("x"); ax.set_ylabel("y")
    return fig

def _read_k03(a=2.0, b=1.0, form="line"):
    y5 = a * 5 + b if form == "line" else a * 2.5 + b
    return readout([("a", fnum(a)), ("b", fnum(b)), ("y(5)", fnum(y5))])

viz = [viz_intro_box("", "Placeholder: two sliders and a menu. The table lists what each control does.",
                     make_table(["control", "what it changes"],
                                [["a", "slope (placeholder)"], ["b", "offset (placeholder)"],
                                 ["menu", "line or curve (placeholder)"]]))]
viz += slider_plot(_render_k03, {
    "a": FloatSlider(value=2.0, min=0, max=10, step=0.5, description="a"),
    "b": FloatSlider(value=1.0, min=0, max=20, step=1.0, description="b"),
    "form": Dropdown(options=["line", "curve"], value="line", description="form")},
    readout_fn=_read_k03)

_QOPTS_K3 = ["y grows with x (placeholder)", "y stays constant (placeholder)", "y falls with x (placeholder)"]
_QTRUE_K3 = 0

def _ans_t3(i, label):
    if i == _QTRUE_K3:
        return True, "Correct: a positive slope makes y grow (placeholder)."
    return False, "Not yet. Look at the sign of a in the figure (placeholder)."

practice = [
  exercise_box("", taskline("<b>Pick the right statement.</b>")
      + "<div>Placeholder: what the reader should decide, in one or two sentences.</div>"),
  choice_answer("For a &gt; 0, what does y do?", _QOPTS_K3, _ans_t3, task="t3", answer=lambda: _QTRUE_K3),
  hint_steps("t3", [
    "Idea: the slope says how y changes when x grows (placeholder).",
    "Working: a &gt; 0, so each step in x adds a to y (placeholder).",
  ]),
  code_fold("def zunahme(a):\n    # True, wenn y mit x wächst\n    return ...\n",
            lambda g: _check_t3(g), task="t3", locked_by="t2",
            task_text="Write <code>zunahme(a)</code> that returns <code>True</code> when y grows with x.",
            solution="def zunahme(a):\n    return a > 0\n"),
]

def _check_t3(g):
    f = g.get("zunahme")
    if not callable(f):
        return False, "Define a function zunahme(a)."
    for a in (2, 0, -1):
        try:
            if bool(f(a)) != (a > 0):
                return False, "zunahme(%g) should be %s." % (a, a > 0)
        except Exception as e:
            return False, "zunahme(%g) raised %r." % (a, e)
    return True, "Correct."

interp = interpretation_box("Placeholder: the one statement to take away from this chapter.",
                            title="Key message (placeholder)")

build_chapter(3, "Third chapter title (placeholder)", figure="Third figure name (placeholder)",
              intro=intro_k3, info=info, body=body_k3, viz=viz,
              practice=practice, interp=interp, task="t3", locked_by="t2")
