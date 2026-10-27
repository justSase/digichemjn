# Kapitel 4 (Platzhalter) — BAUKASTEN II (E28): Winkel mit Periode, Schritte, drei Regler.
# Bausteine hier: intro_box · imath · formula_line · argand_axes · frame_player (Bilder
# erst beim Öffnen) · fig_to_html · slider_plot mit 3 Reglern · numeric_answer mit Winkel
# (answer=(wert, toleranz, periode)) · personal + on_reseed · hint_steps mit forbid ·
# code_fold (locked_by)
intro_k4 = intro_box("Placeholder: the key message of this chapter and its link to chapter 3.")
info = concept_box(
  "Placeholder: an angle φ is only fixed up to full turns, " + imath(r"\varphi + 2\pi k") + ".",
  r"$z = r\,(\cos\varphi + i \sin\varphi)$",
  variables=[("r", "length (placeholder)"), ("φ", "angle in rad (placeholder)")])

def _k04_frame(k):
    fig, ax = fixed_canvas(figsize=(4.2, 4.2), left=.13, right=.97, top=.97, bottom=.10)
    argand_axes(ax, lim=1.4)
    ax.set_xticks([-1, 0, 1]); ax.set_yticks([-1, 0, 1])
    p = k * np.pi / 2
    ax.plot([0, np.cos(p)], [0, np.sin(p)], color=PAL["z"], lw=2.6)
    ax.plot([np.cos(p)], [np.sin(p)], "o", color=PAL["z"], ms=8)
    return fig

_k04_frames = lambda k: fig_to_html(_k04_frame(k), dpi=72, tight=False)
_k04_labels = ["<div style='text-align:center'>step %d of 3 (placeholder)</div>" % (k + 1) for k in range(3)]

def _render_k04(r=1.0, phi=0.5, n=1):
    fig, ax = fixed_canvas(figsize=(5.0, 5.0), left=.13, right=.97, top=.97, bottom=.10)
    argand_axes(ax, lim=3.2)
    ax.set_xticks([-3, 0, 3]); ax.set_yticks([-3, 0, 3])
    for j in range(int(n)):
        p = phi + 2 * np.pi * j / max(int(n), 1)
        ax.plot([0, r * np.cos(p)], [0, r * np.sin(p)], color=PAL["z2"], lw=2.2)
    return fig

viz = [viz_intro_box("", "Placeholder: <b>top</b> steps through prepared frames, <b>bottom</b> has three sliders.")]
viz += frame_player(_k04_frames, _k04_labels, description="step", n=3)
viz += slider_plot(_render_k04, {
    "r": FloatSlider(value=1.0, min=0.5, max=3.0, step=0.5, description="r"),
    "phi": FloatSlider(value=0.5, min=0, max=6.28, step=0.02, description="φ"),
    "n": IntSlider(value=1, min=1, max=4, step=1, description="n")})

_phi4 = 0.3 + TV["a"] * 0.1                     # personal angle (rad), from the seed
on_reseed(lambda: globals().update(_phi4=0.3 + TV["a"] * 0.1))

def _ans_t4(v):
    d = (v["phi"] - (_phi4 + np.pi)) % (2 * np.pi)
    if min(d, 2 * np.pi - d) > tol():
        return False, "Not yet. Turning by half a circle adds π (placeholder). You entered %g." % v["phi"]
    return True, "Correct: %.2f + π, any full turn more or less is the same angle." % _phi4

practice = [
  personal(lambda: exercise_box("", taskline("<b>Turn the arrow by half a circle.</b>")
      + "<div>Your angle is " + imath(r"\varphi = %.2f" % _phi4) + ". Enter the new angle in rad.</div>"
      + formula_line(r"$\varphi' = \varphi + \pi$"))),
  numeric_answer([("phi", "φ' =")], _ans_t4, task="t4",
                 answer=lambda: {"phi": (_phi4 + np.pi, None, 2 * np.pi)}),
  hint_steps("t4", lambda: [
    "Idea: half a circle is π (placeholder).",
    "Working: φ' = %.2f + 3.14 (placeholder)." % _phi4,
  ], forbid=lambda: (_phi4 + np.pi,)),
  code_fold("def halb(phi):\n    # Winkel um eine halbe Drehung weiter, in [0, 2π)\n    return ...\n",
            lambda g: _check_t4(g), task="t4", locked_by="t3",
            task_text="Write <code>halb(phi)</code> that returns φ + π in [0, 2π).",
            solution="import numpy as np\ndef halb(phi):\n    return (phi + np.pi) % (2 * np.pi)\n"),
]

def _check_t4(g):
    f = g.get("halb")
    if not callable(f):
        return False, "Define a function halb(phi)."
    for p in (0.0, 1.0, 4.0):
        try:
            w = (p + np.pi) % (2 * np.pi)
            if abs(f(p) - w) > 1e-6:
                return False, "halb(%g) should be %.4f." % (p, w)
        except Exception as e:
            return False, "halb(%g) raised %r." % (p, e)
    return True, "Correct."

interp = interpretation_box("Placeholder: an angle and the same angle plus 2π are one direction.")

build_chapter(4, "Fourth chapter title (placeholder)", figure="Fourth figure name (placeholder)",
              intro=intro_k4, info=info, viz=viz,
              practice=practice, interp=interp, task="t4", locked_by="t3")
