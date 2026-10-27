_intro = (
  "Addition and subtraction need nothing new. Real parts go with real parts, imaginary parts "
  "with imaginary parts, and the two never mix" + cite(1) + ". The reason: here i is treated as an "
  "ordinary factor, and no " + imath("i^2") + " ever appears. So the defining rule of i is not even "
  "needed yet. In the picture this is plain vector addition (adding arrows tip to tail). That is why "
  "the figure below shows a parallelogram and nothing exotic.")

info = concept_box(_intro,
    r"$z_1 \pm z_2 = (a_1 \pm a_2) + i\,(b_1 \pm b_2)$",
    variables=[("z₁ = a₁ + ib₁", "first number"),
               ("z₂ = a₂ + ib₂", "second number"),
               ("a₁ ± a₂", "real part of the result"),
               ("b₁ ± b₂", "imaginary part of the result")])

def _render_c03(a1=2.0, b1=4.0, a2=1.0, b2=3.0, op="z₁ + z₂"):
    # FIXED frame: each component slider runs to ±6, so a sum can reach ±12.
    # The frame is ±13 and stays there whatever the sliders do.
    z1 = complex(a1, b1); z2 = complex(a2, b2)
    plus = "+" in op
    z = z1 + z2 if plus else z1 - z2
    fig, ax = fixed_canvas(figsize=(5.8, 5.8), left=.12, right=.97, top=.97, bottom=.10)
    argand_axes(ax, lim=13)
    def arrow(zz, col, lw=2.4, ls="-"):
        ax.plot([0, zz.real], [0, zz.imag], color=col, lw=lw, ls=ls, zorder=3)
        ax.plot([zz.real], [zz.imag], "o", color=col, ms=8, zorder=4)
    arrow(z1, PAL["z"])
    if plus:
        arrow(z2, PAL["z2"])
        ax.plot([z1.real, z.real], [z1.imag, z.imag], color=PAL["z2"], lw=1.6, ls="--", alpha=.85)
        ax.plot([z2.real, z.real], [z2.imag, z.imag], color=PAL["z"], lw=1.6, ls="--", alpha=.85)
    else:
        arrow(-z2, PAL["z2"], ls="--")
        ax.plot([z1.real, z.real], [z1.imag, z.imag], color=PAL["z2"], lw=1.6, ls="--", alpha=.85)
    arrow(z, PAL["sum"], lw=3.0)
    return fig

def _read_c03(a1=2.0, b1=4.0, a2=1.0, b2=3.0, op="z₁ + z₂"):
    z1 = complex(a1, b1); z2 = complex(a2, b2); plus = "+" in op
    z = z1 + z2 if plus else z1 - z2; sg = "+" if plus else "−"
    return (readout([("z₁", zs(z1, 1)), ("z₂", zs(z2, 1)), (op, zs(z, 1))])
            + readout([("real", "%.1f %s %.1f = %.1f" % (a1, sg, a2, z.real)),
                       ("imag", "%.1f %s %.1f = %.1f" % (b1, sg, b2, z.imag))]))

viz = [viz_intro_box("",
    "Switch between <b>z₁ + z₂</b> and <b>z₁ − z₂</b> and watch how the construction changes. For the "
    "sum, the dashed lines close a parallelogram: move z₂ so that it starts at the tip of z₁, and it "
    "ends exactly on the result. For the difference, z₂ is first flipped through the origin, and then "
    "the same construction is used. Subtracting means adding the reversed arrow. The line under the sliders shows the "
    "two component sums separately. You will notice that they never influence each other.")]
viz += slider_plot(_render_c03, {
    "a1": FloatSlider(value=2.0, min=-6, max=6, step=0.5, description="a₁"),
    "b1": FloatSlider(value=4.0, min=-6, max=6, step=0.5, description="b₁"),
    "a2": FloatSlider(value=1.0, min=-6, max=6, step=0.5, description="a₂"),
    "b2": FloatSlider(value=3.0, min=-6, max=6, step=0.5, description="b₂"),
    "op": Dropdown(options=["z₁ + z₂", "z₁ − z₂"], value="z₁ + z₂", description="operation")},
                   readout_fn=_read_c03)

_z1, _z2 = TV["z1"], TV["z2"]
_SUM, _DIF = _z1 + _z2, _z1 - _z2

@on_reseed
def _tv_c03():                                   # R2 · 13: new seed, in place
    global _z1, _z2, _SUM, _DIF
    _z1, _z2 = TV["z1"], TV["z2"]
    _SUM, _DIF = _z1 + _z2, _z1 - _z2

def _ans_t3(v):
    got_s = complex(v["sre"], v["sim"]); got_d = complex(v["dre"], v["dim"])
    if abs(got_s - _SUM) > tol():
        if abs(got_s - _DIF) < tol():
            return False, "You have swapped them. The first pair of boxes is the sum."
        return False, ("The sum is not right yet: add the real parts (%g + %g) and the imaginary "
                       "parts (%g + %g) separately." % (_z1.real, _z2.real, _z1.imag, _z2.imag))
    if abs(got_d - _DIF) > tol():
        return False, ("The sum is right, the difference is not. Watch the sign on the imaginary "
                       "part: %g − (%g) = %g." % (_z1.imag, _z2.imag, _DIF.imag))
    return True, "Both correct. Note that the two components never influenced each other."

practice = [
  personal(lambda: exercise_box("", taskline("<b>Compute the sum and the difference of your two numbers.</b>")
      + formula_line(r"$z_1 \pm z_2 = (a_1 \pm a_2) + i\,(b_1 \pm b_2)$")
      + "<div>Your personal pair is <b>z₁ = " + zs(_z1) + "</b> and <b>z₂ = " + zs(_z2) + "</b>. "
        "Combine real parts with real parts and imaginary parts with imaginary parts. You need no calculator. "
        "Type the four numbers below.</div>")),
  numeric_answer([("sre", "Re(z₁+z₂) ="), ("sim", "Im(z₁+z₂) ="),
                  ("dre", "Re(z₁−z₂) ="), ("dim", "Im(z₁−z₂) =")], _ans_t3, task="t3",
                 answer=lambda: {"sre": _SUM.real, "sim": _SUM.imag, "dre": _DIF.real, "dim": _DIF.imag}),
  # 2026-09-27 (Inhalt), eingebaut R2 · 15 — hints: the idea, then the working.
  hint_steps("t3", lambda: [
    "Adding complex numbers means adding arrows, and an arrow has two independent components. Real "
    "parts go with real parts, imaginary parts with imaginary parts. Treat i like a unit, as in "
    "3 m + 2 m: the two kinds never mix. For the difference, subtract z₂ as a whole, so both of its "
    "parts change sign.",
    "Sum: real part %s + %s, imaginary part %s + %s. Difference: real part %s − %s, imaginary "
    "part %s − %s. Where a minus meets a negative number, the two minus signs make a plus."
    % tuple(_pn(x) for x in (_z1.real, _z2.real, _z1.imag, _z2.imag,
                            _z1.real, _z2.real, _z1.imag, _z2.imag)),
  ], forbid=lambda: (_SUM.real, _SUM.imag, _DIF.real, _DIF.imag)),
  code_fold("def add_sub(a1, b1, a2, b2):\n"
            "    s = complex(..., ...)\n"
            "    d = complex(..., ...)\n"
            "    return (s, d)\n",
            lambda g: _check_t3(g), task="t3", locked_by="t2",
            task_text=('Write <code>add_sub(a1, b1, a2, b2)</code> that adds and subtracts z₁ = a1 + i·b1 and z₂ = a2 + i·b2. '
                       'It takes the four real components and returns the tuple (z₁ + z₂, z₁ − z₂) as two complex numbers. '
                       'Example: <code>add_sub(2, 4, 1, 3)</code> → <code>((3+7j), (1+1j))</code>.'),
            solution="def add_sub(a1, b1, a2, b2):\n"
                     "    s = complex(a1 + a2, b1 + b2)\n"
                     "    d = complex(a1 - a2, b1 - b2)\n"
                     "    return (s, d)\n"),
]

def _check_t3(g):
    f = g.get("add_sub")
    if not callable(f):
        return False, "Define a function called add_sub(a1, b1, a2, b2)."
    for (p, q) in [(_z1, _z2), (complex(2, 4), complex(1, 3)), (complex(19, 0), complex(0, 15)),
                   (complex(-2, -5), complex(-3, 8))]:
        try:
            out = f(p.real, p.imag, q.real, q.imag)
        except Exception as e:
            return False, "add_sub raised %r." % (e,)
        if not isinstance(out, (tuple, list)) or len(out) != 2:
            return False, "Return exactly two values: (sum, difference)."
        s, d = complex(out[0]), complex(out[1])
        if abs(s - (p + q)) > 1e-9:
            if abs(s - (p - q)) < 1e-9:
                return False, "Sum and difference are the other way round."
            return False, ("For z₁ = %s and z₂ = %s the sum is %s." % (zs(p), zs(q), zs(p + q)))
        if abs(d - (p - q)) > 1e-9:
            return False, ("The difference is wrong: for z₁ = %s, z₂ = %s it is %s."
                           % (zs(p), zs(q), zs(p - q)))
    return True, "Correct: both operations, with every component sign right."

interp = interpretation_box(
  "Addition keeps the two components strictly apart. That is why it is <b>vector addition</b>: "
  "here ℂ behaves exactly like ℝ², the ordinary plane of vectors. Everything really new about complex "
  "numbers is hidden in the <i>multiplication</i>. That is where we go next.")

build_chapter(3, "Addition and subtraction", figure='Parallelogram rule', info=info, viz=viz, practice=practice, interp=interp,
              locked_by="t2", task="t3")
