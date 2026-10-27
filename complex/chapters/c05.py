_intro = (
  "The conjugate now proves useful in two ways. First, " + imath("z\\bar{z}") + " is always a real, "
  "non-negative number. Its square root therefore gives the <b>length</b> of z, called the absolute value "
  + imath("|z|") + ". Second, the same product makes division possible: multiply "
  "numerator and denominator by " + imath("\\bar{z}_2") + ", and the denominator becomes real. You "
  "already know how to divide by a real number" + cite(1, 4) + ".")

info = concept_box(_intro,
    r"$|z| = \sqrt{z\bar{z}} = \sqrt{a^2+b^2}, \qquad "
    r"\frac{z_1}{z_2} = \frac{z_1\bar{z}_2}{z_2\bar{z}_2} = \frac{z_1\bar{z}_2}{a_2^2+b_2^2}$",
    variables=[("|z|", "modulus (absolute value): the distance from the origin to z"),
               ("z̄₂", "conjugate of the denominator"),
               ("a₂² + b₂²", "the real denominator you are left with, equal to |z₂|²")],
    extra_html=("<div style='max-width:800px;margin:14px auto 0;text-align:justify;line-height:1.6'>"
                "Written out in components, the quotient is "
                + imath(r"\frac{a_1a_2+b_1b_2}{a_2^2+b_2^2} + i\,\frac{a_2b_1-a_1b_2}{a_2^2+b_2^2}")
                + ". You do not need to memorise this expression. The two-step recipe is easier: "
                "<b>conjugate the denominator, then divide by a real number</b>."
                + "</div>"))   # E26.3: the box closed (an open <div> swallowed the rest of the reading copy, JS 11.10.)

def _render_c05(a1=4.0, b1=3.0, a2=-5.0, b2=6.0):
    # FIXED frames. Left: components run to ±7, so |z| <= 9.9 -> frame ±10.
    # Right: the quotient is unbounded as |z2| -> 0, so the frame is fixed at ±4
    # and an out-of-frame quotient is marked instead of rescaling the axes.
    z1 = complex(a1, b1); z2 = complex(a2, b2)
    fig, axs = fixed_canvas(figsize=(9.6, 5.0), left=.07, right=.98, top=.95, bottom=.10, ncols=2)
    ax, bx = axs
    argand_axes(ax, lim=10)
    th = np.linspace(0, 2*np.pi, 300)
    for zz, col in ((z1, PAL["z"]), (z2, PAL["z2"])):
        ax.plot(abs(zz)*np.cos(th), abs(zz)*np.sin(th), color=col, lw=1.1, alpha=.45)
        ax.plot([0, zz.real], [0, zz.imag], color=col, lw=2.5, zorder=3)
        ax.plot([zz.real], [zz.imag], "o", color=col, ms=8, zorder=4)
    argand_axes(bx, lim=4)
    if abs(z2) > 1e-12:
        q = z1/z2
        if abs(q.real) <= 4 and abs(q.imag) <= 4:
            bx.plot([0, q.real], [0, q.imag], color=PAL["sum"], lw=2.8, zorder=3)
            bx.plot([q.real], [q.imag], "o", color=PAL["sum"], ms=9, zorder=4)
        else:                       # keep the scale, show the direction only
            u = q/abs(q)*3.8
            bx.plot([0, u.real], [0, u.imag], color=PAL["warn"], lw=2.4, ls="--", zorder=3)
            bx.annotate("off frame", (u.real*.55, u.imag*.55), color=PAL["warn"],
                        fontsize=9, ha="center")
    return fig

def _read_c05(a1=4.0, b1=3.0, a2=-5.0, b2=6.0):
    z1 = complex(a1, b1); z2 = complex(a2, b2)
    if abs(z2) < 1e-12:
        return readout([("|z₁|", "%.3f" % abs(z1)), ("|z₂|", "0"),
                        ("z₁/z₂", "undefined: z₂ is zero")])
    q = z1/z2
    return (readout([("|z₁|", "%.3f" % abs(z1)), ("|z₂|", "%.3f" % abs(z2)),
                     ("z₁/z₂", zs(q, 3))])
            + readout([("|z₁|/|z₂|", "%.4f" % (abs(z1)/abs(z2))),
                       ("|z₁/z₂|", "%.4f" % abs(q)), ("", "identical, always")]))

viz = [viz_intro_box("",
    "On the left, each number sits on a circle whose radius is its modulus. Move a slider, and the "
    "circle grows or shrinks with the arrow. On the right is the quotient. Watch the two numbers in the "
    "right-hand title: the modulus of the quotient always equals the quotient of the moduli, however "
    "you move the points. This is a first glimpse of a rule that chapter 7 makes exact: under "
    "multiplication and division, <b>lengths and angles behave separately</b>.")]
viz += slider_plot(_render_c05, {
    "a1": FloatSlider(value=4.0, min=-7, max=7, step=0.5, description="a₁"),
    "b1": FloatSlider(value=3.0, min=-7, max=7, step=0.5, description="b₁"),
    "a2": FloatSlider(value=-5.0, min=-7, max=7, step=0.5, description="a₂"),
    "b2": FloatSlider(value=6.0, min=-7, max=7, step=0.5, description="b₂")},
                   readout_fn=_read_c05)

# 2026-09-28 (R1 · Paket 12) — the reader's own pair, whole quotient (see _setup_cx)
_N5, _D5 = TV["n5"], TV["d5"]
_QD = _N5 / _D5
_DEN5 = int(round(_D5.real**2 + _D5.imag**2))

@on_reseed
def _tv_c05():                                   # R2 · 13: new seed, in place
    global _N5, _D5, _QD, _DEN5
    _N5, _D5 = TV["n5"], TV["d5"]
    _QD = _N5 / _D5
    _DEN5 = int(round(_D5.real**2 + _D5.imag**2))

def _ans_t5(v):
    got = complex(v["re"], v["im"])
    if abs(got - _QD) < tol():
        return True, ("Correct: (%s)/(%s) = %s. The conjugate turned the denominator into the "
                      "real number %d." % (zs(_N5), zs(_D5), zs(_QD), _DEN5))
    if abs(got - (_D5/_N5)) < tol():
        return False, "You divided the other way round. It is z₁/z₂, not z₂/z₁."
    if abs(got - _QD.conjugate()) < tol():
        return False, ("Your answer is the conjugate of the right one. Check the sign in the "
                       "imaginary part of the numerator: it is a₂b₁ − a₁b₂.")
    return False, ("Not yet. Multiply top and bottom by z̄₂ = %s. The denominator becomes "
                   "(%d)² + (%d)² = %d. Then divide both components by %d."
                   % (zs(_D5.conjugate()), _D5.real, _D5.imag, _DEN5, _DEN5))

practice = [
  personal(lambda: exercise_box("", taskline("<b>Divide, using the conjugate of the denominator.</b>")
      + formula_line(r"$\frac{z_1}{z_2} = \frac{z_1\,\bar{z}_2}{a_2^{\,2}+b_2^{\,2}}$")
      + "<div>Your personal pair is <b>z₁ = " + zs(_N5) + "</b> and <b>z₂ = " + zs(_D5) + "</b>. "
        "Conjugate the denominator and multiply out the numerator with the rule from chapter 4. Then "
        "divide both components by the real number " + imath("a_2^2+b_2^2") + ". The numbers work out "
        "neatly, so you do not need a calculator.</div>")),
  numeric_answer([("re", "Re(z₁/z₂) ="), ("im", "Im(z₁/z₂) =")], _ans_t5, task="t5",
                 answer=lambda: {"re": _QD.real, "im": _QD.imag}),
  # 2026-09-27 (Inhalt), eingebaut R2 · 15 — hints: the idea, then the working.
  # Rewritten for the reader's own pair (R1 · 12); the old ones named (4+3i)/(−5+6i).
  hint_steps("t5", lambda: [
    "Dividing by a complex number is hard; dividing by a <i>real</i> number is easy. "
    "Which number can you multiply your z₂, " + zs(_D5) + ", by so that the product is real? Chapter 4 "
    "has the answer: z · z̄ gives |z|². Multiply the top <i>and</i> the bottom of the fraction by that "
    "number. This changes nothing, because it is a multiplication by 1.",
    "The bottom: (%s)(%s) gives %s² + %s², a real number. The top: expand (%s)(%s) term by term "
    "and replace i² by −1. Collect the real and the imaginary part, then divide <b>each</b> of "
    "them by the bottom." % (zs(_D5), zs(_D5.conjugate()), _pn(_D5.real), _pn(_D5.imag),
                            zs(_N5), zs(_D5.conjugate())),
  ], forbid=lambda: (_QD.real, _QD.imag)),
  code_fold("def divide(a1, b1, a2, b2):\n"
            "    den = ...                 # a2**2 + b2**2, a real number\n"
            "    if den == 0:\n"
            "        raise ZeroDivisionError('z2 is zero')\n"
            "    re = ...\n"
            "    im = ...\n"
            "    return complex(re/den, im/den)\n",
            lambda g: _check_t5(g), task="t5", locked_by="t4",
            task_text=('Write <code>divide(a1, b1, a2, b2)</code> that returns z₁ / z₂ for z₁ = a1 + i·b1 and z₂ = a2 + i·b2, by multiplying top and bottom by the conjugate of z₂. '
                       'It returns one complex number and raises <code>ZeroDivisionError</code> if z₂ = 0. '
                       'Example: <code>divide(1, 0, 0, 1)</code> → <code>-1j</code>.'),
            solution="def divide(a1, b1, a2, b2):\n"
                     "    den = a2**2 + b2**2            # = |z2|**2, real\n"
                     "    if den == 0:\n"
                     "        raise ZeroDivisionError('z2 is zero')\n"
                     "    re = a1*a2 + b1*b2             # numerator of z1 * conj(z2)\n"
                     "    im = a2*b1 - a1*b2\n"
                     "    return complex(re/den, im/den)\n"),
]

def _check_t5(g):
    f = g.get("divide")
    if not callable(f):
        return False, "Define a function called divide(a1, b1, a2, b2)."
    for (p, q) in [(complex(4, 3), complex(-5, 6)), (TV["z1"], TV["z2"]),
                   (complex(1, 0), complex(0, 1)), (complex(-2, -5), complex(3, -1))]:
        try:
            out = complex(f(p.real, p.imag, q.real, q.imag))
        except Exception as e:
            return False, "divide raised %r." % (e,)
        want = p / q
        if abs(out - want) > 1e-8:
            if abs(out - (q / p)) < 1e-8:
                return False, "You divided the other way round."
            if abs(out - want.conjugate()) < 1e-8:
                return False, "That is the conjugate. Check the sign of a₂b₁ − a₁b₂."
            return False, ("For z₁ = %s, z₂ = %s the quotient is %s." % (zs(p), zs(q), zs(want, 4)))
    try:
        f(1, 1, 0, 0)
        return False, "Dividing by zero should raise ZeroDivisionError."
    except ZeroDivisionError:
        pass
    except Exception as e:
        return False, "Dividing by zero raised %r; expected ZeroDivisionError." % (e,)
    return True, "Correct on all pairs, and the zero denominator is handled."

interp = interpretation_box(
  "Both results of this chapter come from one idea: <b>the conjugate removes the imaginary part of a "
  "product</b>. It gives a length, and it turns any denominator into a real number. Notice also what "
  "|z| does <i>not</i> give you: an order. You cannot call one complex number “smaller” or "
  "“larger” than another. Only their moduli can be compared, and those are ordinary real numbers" + cite(1) + ".")

# E19.8 — from "Remarks and limits": the limit of this chapter, in red
warn = warn_box(
  "<b>There is no order on ℂ.</b> For two complex numbers, " + imath("z_1<z_2") + " is not just "
  "unknown; it is undefined" + cite(1) + ". You can compare only the moduli, and those are real "
  "numbers. Code that sorts complex numbers really sorts something else, usually |z| or Re(z), "
  "and should say so.")

build_chapter(5, "Absolute value and division", figure='Moduli of a quotient', info=info, viz=viz, practice=practice,
              interp=interp, body=[warn], locked_by="t4", task="t5")
