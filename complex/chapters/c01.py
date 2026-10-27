_intro = (
  "Each number system in mathematics was invented because the previous one ran out of answers. "
  "The real numbers run out at a surprisingly simple equation: " + imath("x^2+1=0") + ". The square "
  "of a real number is never negative, so this polynomial has no real root (no real x solves it)" + cite(1) + ". "
  "The fix is a single definition, <b>i² = −1</b>. The rest of this notebook follows from it.")

info = concept_box(_intro, r"$i = \sqrt{-1} \;\Leftrightarrow\; i^2 = -1$",
    variables=[("i", "the imaginary unit"),
               ("z", "a complex number, written z = a + ib"),
               ("a = Re(z)", "the real part of z"),
               ("b = Im(z)", "the imaginary part of z: a real number, the factor in front of i")],
    extra_html=("<div style='max-width:800px;margin:14px auto 0;text-align:justify;line-height:1.6'>"
                "Look closely at <b>Im(z)</b>. For " + imath("z = 4+5i") + " the imaginary part is the "
                "real number 5, not 5i. So a complex number is not a strange new kind of number. "
                "It is a <i>pair</i> of real numbers with one extra rule for multiplication.</div>"))

def _render_c01(q=4.0):
    # FIXED frame: x from the linspace, y from the slider range (q in [-6,10]),
    # so nothing rescales while q moves.
    x = np.linspace(-4, 4, 400)
    fig, ax = fixed_canvas(figsize=(6.6, 3.9), left=.12, right=.97, top=.95, bottom=.16)
    theme_axes(ax)
    ax.set_xlim(-4, 4); ax.set_ylim(-8, 26)
    ax.plot(x, x**2 + q, color=PAL["z2"], lw=2.4)
    ax.axhline(0, color=PLOT_INK, lw=1.1)
    if q < 0:
        r = np.sqrt(-q)
        ax.plot([-r, r], [0, 0], "o", color=PAL["sum"], ms=8)
    else:
        ax.plot([0], [q], "o", color=PAL["warn"], ms=8)
    ax.set_xlabel("x"); ax.set_ylabel("f(x)")
    return fig

def _read_c01(q=4.0):
    if q < 0:
        r = np.sqrt(-q)
        return readout([("q", "%.1f" % q), ("real roots", "2"),
                        ("x", "±%.3f" % r), ("lowest point", "%.1f" % q)])
    return readout([("q", "%.1f" % q), ("real roots", "0"),
                    ("x", "none on this line"), ("lowest point", "%.1f" % q)])

viz = [viz_intro_box("",
    "The parabola " + imath("f(x)=x^2+q") + " crosses the horizontal axis exactly where "
    + imath("x^2+q=0") + " has a real solution (a root). Pull <b>q</b> below zero and two crossings "
    "appear. Raise it above zero and the curve lifts off the axis: there is nothing left to find "
    "<i>on this line</i>. The roots have not vanished. The number line is just the wrong place to "
    "look for them. Chapter 2 gives them the plane they live in.")]
viz += slider_plot(_render_c01, {"q": FloatSlider(value=4.0, min=-6, max=10, step=0.5,
                                                  description="q")}, readout_fn=_read_c01)

_q = TV["q"]
on_reseed(lambda: globals().update(_q=TV["q"]))   # R2 · 13: new seed, in place

def _ans_t1(v):
    r = np.sqrt(_q)
    if abs(v["re"]) > 1e-6:
        return False, ("Both roots are purely imaginary, so the real part is 0. You entered %g."
                       % v["re"])
    if abs(abs(v["im"]) - r) > tol():
        if abs(abs(v["im"]) - _q) < 1e-9:
            return False, ("You entered q itself. The imaginary part is the square <i>root</i> of q."
                           )
        return False, ("Not yet. Take the square root of q = %d and put an i in front: the two roots "
                       "are ±i·√%d. Your imaginary part was %g." % (_q, _q, v["im"]))
    if v["im"] <= 0:
        return False, "That is the root with the negative imaginary part. Enter the one with the positive part."
    return True, ("Correct: √%d = %d, so the roots are ±%d i." % (_q, round(r), round(r)))

practice = [
  personal(lambda: exercise_box("", taskline("<b>Give the root of " + imath("z^2 + q = 0")
               + " that has a positive imaginary part.</b>")
      + formula_line(r"$z^2 + q = 0 \;\Rightarrow\; z_{1,2} = \pm\, i\sqrt{q}$")
      + "<div>Your personal value is <b>q = " + str(_q) + "</b>, so the imaginary part you "
        "need is " + imath(r"\sqrt{%d}" % _q) + ". It is a whole number, so you need no calculator. "
        "The real part is the easy one: both roots are purely imaginary (a real number times i).</div>")),
  numeric_answer([("re", "Re(z) ="), ("im", "Im(z) =")], _ans_t1, task="t1",
                 answer=lambda: {"re": 0.0, "im": float(np.sqrt(_q))}),   # E26 Teil 2: reading window
  # 2026-09-27 (Inhalt), eingebaut R2 · 15, Zahlen seit R1 · 12 — hints: idea, then working.
  hint_steps("t1", lambda: [
    "You need a number whose <i>square</i> is −q. No real number can do that: every real square is "
    "0 or more. This is exactly why the parabola above never reaches the axis. The number i was "
    "made for this case, since i² is −1. So try z = i·y with a real y. Then z² = i²·y² = −y², and "
    "the question becomes: which real y has y² equal to q?",
    "With your q = %d: y² must be %d, so y is ±√%d and the two roots are ±i·√%d. Which whole "
    "number, multiplied by itself, gives %d? The root you are asked for has the plus sign. Its "
    "real part is the easy box: i·y has no real part at all." % (_q, _q, _q, _q, _q),
  ], forbid=lambda: (np.sqrt(_q),)),
  code_fold("import numpy as np\n\n"
            "def roots_of(q):\n"
            "    # return the two roots of z**2 + q = 0 for q > 0, as a tuple\n"
            "    r = ...\n"
            "    return (..., ...)\n",
            lambda g: _check_t1(g), task="t1",
            task_text=('Write <code>roots_of(q)</code> that returns the two solutions of z² + q = 0 for a positive real number q. '
                       'It takes q &gt; 0 and returns a tuple of two complex numbers, +i·√q and −i·√q. '
                       'Example: <code>roots_of(4)</code> → <code>(2j, -2j)</code>.'),
            solution="import numpy as np\n\n"
                     "def roots_of(q):\n"
                     "    r = np.sqrt(q)          # real square root of q\n"
                     "    return (1j*r, -1j*r)    # ± i·sqrt(q)\n"),
]

def _check_t1(g):
    f = g.get("roots_of")
    if not callable(f):
        return False, "Define a function called roots_of(q) that returns a tuple."
    for q in (1.0, 4.0, float(_q), 7.0):
        try:
            out = f(q)
        except Exception as e:
            return False, "roots_of(%g) raised %r." % (q, e)
        if not isinstance(out, (tuple, list)) or len(out) != 2:
            return False, "Return exactly two values, e.g. (z1, z2)."
        if any(abs(complex(v).real) > 1e-9 for v in out):
            return False, "Both roots are purely imaginary, so Re(z) must be 0."
        got = sorted(complex(v).imag for v in out)
        if not np.allclose(got, sorted([np.sqrt(q), -np.sqrt(q)]), atol=1e-8):
            return False, ("For q = %g the roots should be ±i·%.4f." % (q, np.sqrt(q)))
    return True, "Correct: two purely imaginary roots with opposite signs."

interp = interpretation_box(
  "One definition, " + imath("i^2=-1") + ", turns a dead end into a solvable equation. It breaks "
  "none of the old arithmetic. Every real number is still a complex number, namely one with "
  "<b>Im(z) = 0</b>. This pattern is worth remembering: the real numbers are not replaced, they "
  "become part of something larger.")

# the first chapter is the one the reader is meant to be standing in when the
# notebook finishes loading, so it is the one chapter that opens by itself
build_chapter(1, "Why complex numbers?", figure='Where the real roots end', info=info, viz=viz, practice=practice, interp=interp,
              task="t1", chapter_open=True)
