_intro = (
  "A complex number carries two independent real numbers, " + imath("a") + " and " + imath("b") +
  ". A single line cannot hold it, but a plane can. Put <b>Re</b> (the real part) on the horizontal "
  "axis and <b>Im</b> (the imaginary part) on the vertical one. Then " + imath("z = a+ib") + " becomes "
  "the point with coordinates " + imath("(a,\\,b)") + ", or the arrow from the origin to that point" + cite(1, 2) +
  ". This plane is called the <i>Argand plane</i> or complex plane. From here on, almost every rule "
  "about complex numbers comes with a picture.")

info = concept_box(_intro, r"$z = a + ib \;\longleftrightarrow\; (a,\,b)$",
    variables=[("Re-axis", "horizontal, carries the real part a"),
               ("Im-axis", "vertical, carries the imaginary part b"),
               ("|z|", "the modulus: length of the arrow from the origin to z"),
               ("φ", "the argument: angle of that arrow, measured from the positive Re-axis")],
    extra_html=("<div style='max-width:800px;margin:14px auto 0;text-align:justify;line-height:1.6'>"
                "The axes divide the plane into four <b>quadrants</b>. They are numbered anticlockwise, "
                "starting with the one where both parts are positive. The quadrant matters more than it "
                "seems. Chapter 6 shows that the standard formula for the angle gives a wrong result in "
                "two of the four, without any warning.</div>"))

def _render_c02(a=3.0, b=2.0):
    # FIXED frame: the sliders run to ±5, the frame is ±6 and never moves.
    fig, ax = fixed_canvas(figsize=(5.6, 5.6), left=.12, right=.97, top=.97, bottom=.10)
    argand_axes(ax, lim=6)
    r = np.hypot(a, b); phi = np.arctan2(b, a)
    if r > 1e-9:
        th = np.linspace(0, phi, 80)
        ax.plot(0.9*np.cos(th), 0.9*np.sin(th), color=PAL["aux"], lw=1.6)
        ax.annotate("φ", (1.3*np.cos(phi/2), 1.3*np.sin(phi/2)), color=PAL["aux"],
                    fontsize=12, ha="center", va="center")
    ax.plot([0, a], [0, b], color=PAL["z"], lw=2.6, zorder=3)
    ax.plot([a], [b], "o", color=PAL["z"], ms=10, zorder=4)
    ax.plot([a, a], [0, b], ls=":", color=PAL["ghost"], lw=1.4)
    ax.plot([0, a], [b, b], ls=":", color=PAL["ghost"], lw=1.4)
    for q, (xx, yy) in {1: (4.8, 4.8), 2: (-4.8, 4.8), 3: (-4.8, -4.8), 4: (4.8, -4.8)}.items():
        ax.text(xx, yy, "(%s)" % ("I", "II", "III", "IV")[q-1], color=PLOT_INK,
                alpha=.6, fontsize=11, ha="center", va="center")
    return fig

def _read_c02(a=3.0, b=2.0):
    r = np.hypot(a, b); phi = np.arctan2(b, a) % (2*np.pi)
    quad = 0 if (abs(a) < 1e-9 or abs(b) < 1e-9) else (
        1 if (a > 0 and b > 0) else 2 if (a < 0 and b > 0) else 3 if (a < 0 and b < 0) else 4)
    return readout([("z", zs(complex(a, b), 1)), ("|z|", "%.3f" % r),
                    ("φ", "%.3f rad" % phi), ("", "%.1f°" % np.degrees(phi)),
                    ("quadrant", str(quad) if quad else "on an axis")])

viz = [viz_intro_box("",
    "Drag <b>a</b> and <b>b</b> and watch four things at once: the point, the arrow, its length "
    + imath("|z|") + " and its angle " + imath("\\varphi") + ". Start in the first quadrant. "
    "Then move the point anticlockwise through all four and watch the angle in the line under the sliders: it "
    "runs from 0 up towards 2π. Now set <b>b = 0</b>. The arrow collapses onto the horizontal axis, "
    "and you are back to an ordinary real number. This is what “the reals sit inside ℂ” means "
    "in the picture (ℂ is the set of all complex numbers).")]
viz += slider_plot(_render_c02, {"a": FloatSlider(value=3.0, min=-5, max=5, step=0.5, description="a = Re(z)"),
                                 "b": FloatSlider(value=2.0, min=-5, max=5, step=0.5, description="b = Im(z)")}, readout_fn=_read_c02)

_zc = TV["z1"]
_QOPTS = ["Quadrant I  (Re > 0, Im > 0)", "Quadrant II  (Re < 0, Im > 0)",
          "Quadrant III  (Re < 0, Im < 0)", "Quadrant IV  (Re > 0, Im < 0)",
          "on one of the axes"]
_QTRUE = (0 if (_zc.real > 0 and _zc.imag > 0) else 1 if (_zc.real < 0 and _zc.imag > 0)
          else 2 if (_zc.real < 0 and _zc.imag < 0) else 3)

@on_reseed
def _tv_c02():                                   # R2 · 13: new seed, in place
    global _zc, _QTRUE
    _zc = TV["z1"]
    _QTRUE = (0 if (_zc.real > 0 and _zc.imag > 0) else 1 if (_zc.real < 0 and _zc.imag > 0)
              else 2 if (_zc.real < 0 and _zc.imag < 0) else 3)

def _ans_t2(idx, label):
    if idx == _QTRUE:
        return True, ("Correct: Re(z) = %g and Im(z) = %g, so z sits in %s."
                      % (_zc.real, _zc.imag, _QOPTS[_QTRUE].split("(")[0].strip()))
    if idx == 4:
        return False, "Neither part is zero, so z is not on an axis."
    if idx in (1, 3) and _QTRUE in (1, 3):
        return False, ("Right half of the plane or left? Re(z) = %g decides that, and you picked "
                       "the other side." % _zc.real)
    return False, ("Not that one. Read off the two signs: Re(z) = %g and Im(z) = %g. Quadrants are "
                   "counted anticlockwise from the one where both are positive."
                   % (_zc.real, _zc.imag))

practice = [
  personal(lambda: exercise_box("", taskline("<b>Which quadrant does your number sit in?</b>")
      + "<div>Your personal number is <b>z = " + zs(_zc) + "</b>. Use the visualisation above if it "
        "helps: set the sliders to these values and look at where the arrow points.</div>")),
  choice_answer(lambda: "z = " + zs(_zc), _QOPTS, _ans_t2, task="t2", answer=lambda: _QTRUE),
  code_fold("def quadrant(a, b):\n"
            "    # 1: a>0,b>0   2: a<0,b>0   3: a<0,b<0   4: a>0,b<0   0: on an axis\n"
            "    ...\n",
            lambda g: _check_t2(g), task="t2", locked_by="t1",
            task_text=('Write <code>quadrant(a, b)</code> that says in which quadrant of the complex plane z = a + ib lies. '
                       'It takes the real part a and the imaginary part b and returns 1, 2, 3 or 4 (counted anticlockwise, starting top right), or 0 if z lies on an axis. '
                       'Example: <code>quadrant(-3, 2)</code> → <code>2</code>.'),
            solution="def quadrant(a, b):\n"
                     "    if a == 0 or b == 0:\n"
                     "        return 0\n"
                     "    if a > 0:\n"
                     "        return 1 if b > 0 else 4\n"
                     "    return 2 if b > 0 else 3\n"),
]
# 2026-09-27 (Inhalt), eingebaut R2 · 15 — hints: the idea, then the working;
# right after the choice (index 2), inserted here so the list above stays as it was.
practice.insert(2,
  # The right option is forbidden as TEXT: no step may name "Quadrant …" for z.
  hint_steps("t2", lambda: [
    "Only two signs decide the quadrant. Is the real part positive or negative, that is, right "
    "or left of the vertical axis? Is the imaginary part positive or negative, that is, above or "
    "below the horizontal axis? The size of the parts does not matter.",
    "Your z has Re(z) = %s and Im(z) = %s. Write down the two signs as a pair (sign of Re, sign "
    "of Im). The quadrants are counted anticlockwise, starting where both are positive: (+, +) "
    "is I, (−, +) is II, (−, −) is III, (+, −) is IV. A part that is exactly zero would put z on "
    "an axis." % tuple(("%d" % v).replace("-", "−") for v in (_zc.real, _zc.imag)),
  ], forbid=lambda: (_QOPTS[_QTRUE].split("(")[0].strip(),)))

def _check_t2(g):
    f = g.get("quadrant")
    if not callable(f):
        return False, "Define a function called quadrant(a, b)."
    cases = [(3, 2, 1), (-3, 2, 2), (-3, -2, 3), (3, -2, 4),
             (0, 5, 0), (5, 0, 0), (0, 0, 0), (-0.1, -7.5, 3), (2.5, -0.4, 4)]
    wrong = [(a, b, f(a, b), w) for a, b, w in cases if f(a, b) != w]
    if wrong:
        a, b, got, want = wrong[0]
        if want == 0:
            return False, ("Don't forget the axes: with a = %g, b = %g the answer is 0, but you "
                           "returned %r." % (a, b, got))
        return False, ("For a = %g, b = %g the point is in quadrant %d, but you returned %r."
                       % (a, b, want, got))
    return True, "Correct: all four quadrants and the axis cases are handled."

interp = interpretation_box(
  "Once a complex number is a point, every operation on it becomes a <b>movement</b> in the plane. "
  "This is the most useful idea in this notebook. Addition will turn out to be a shift, and "
  "conjugation (changing the sign of the imaginary part) a mirror image. Multiplication will be a "
  "rotation combined with a stretch. These three pictures are far easier to remember than three formulas.")

build_chapter(2, "The complex plane", figure='Point, length and angle', info=info, viz=viz, practice=practice, interp=interp,
              locked_by="t1", task="t2")
