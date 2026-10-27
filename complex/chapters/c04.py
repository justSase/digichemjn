_intro = (
  "With multiplication, a complex number becomes more than two separate columns of numbers. Multiply out "
  + imath("(a_1+ib_1)(a_2+ib_2)") + " as usual. One term then contains " + imath("i^2") + ", which by "
  "definition equals " + imath("-1") + ". This one sign change mixes the two "
  "components and gives ℂ its own arithmetic" + cite(1) + ". The chapter also introduces the <b>conjugate</b> "
  + imath("\\bar{z}=a-ib") + ". It is the mirror image of z across the real axis, and you will use it "
  "constantly in the next chapter.")

info = concept_box(_intro,
    r"$z_1 z_2 = (a_1a_2 - b_1b_2) + i\,(a_1b_2 + a_2b_1)$",
    variables=[("a₁a₂ − b₁b₂", "real part; the minus sign comes from i² = −1"),
               ("a₁b₂ + a₂b₁", "imaginary part: the two cross terms"),
               ("z̄ = a − ib", "the conjugate: same real part, opposite imaginary part")],
    extra_html=("<div style='max-width:800px;margin:14px auto 0;text-align:justify;line-height:1.6'>"
                "The minus sign in the real part is the most common mistake in this topic. "
                "If a result looks wrong, check this sign first.</div>"))

# --- i-powers carousel: four pre-rendered frames --------------------------
def _ipow_frame(k):
    fig, ax = fixed_canvas(figsize=(4.4, 4.4), left=.14, right=.96, top=.90, bottom=.12)
    argand_axes(ax, lim=1.6)
    th = np.linspace(0, 2*np.pi, 300)
    ax.plot(np.cos(th), np.sin(th), color=PLOT_INK, lw=1.0, alpha=.45)
    vals = [1 + 0j, 1j, -1 + 0j, -1j]
    for j, v in enumerate(vals):
        on = (j == (k % 4))
        col = PAL["z"] if on else PAL["ghost"]
        ax.plot([0, v.real], [0, v.imag], color=col, lw=2.6 if on else 1.2,
                alpha=1.0 if on else .5, zorder=3)
        ax.plot([v.real], [v.imag], "o", color=col, ms=9 if on else 5,
                alpha=1.0 if on else .5, zorder=4)
    ax.set_xticks([-1, 0, 1]); ax.set_yticks([-1, 0, 1])
    return fig

# Paket 21b — drawn when the chapter opens, not at start (frame_player takes the function)
_ipow_frames = lambda k: fig_to_html(_ipow_frame(k), dpi=84, tight=False)
_ipow_labels = ["<div style='text-align:center'><b class='nbaccent'>%s</b> &nbsp;·&nbsp; %s</div>" % t
                for t in [("i⁰ = 1",  "start on the real axis at 1"),
                          ("i¹ = i",  "one factor of i: a quarter turn anticlockwise"),
                          ("i² = −1", "two factors: half a turn. This <i>is</i> the definition"),
                          ("i³ = −i", "three factors: three quarters of a turn"),
                          ("i⁴ = 1",  "full circle, back to 1. The powers of i repeat with period 4")]]

def _render_conj(a=3.0, b=2.0):
    # FIXED frame ±6; the sliders run to ±5.
    z = complex(a, b); zb = z.conjugate()
    fig, ax = fixed_canvas(figsize=(5.4, 5.4), left=.13, right=.97, top=.97, bottom=.10)
    argand_axes(ax, lim=6)
    ax.plot([0, z.real], [0, z.imag], color=PAL["z"], lw=2.6, zorder=3)
    ax.plot([z.real], [z.imag], "o", color=PAL["z"], ms=9, zorder=4)
    ax.plot([0, zb.real], [0, zb.imag], color=PAL["z2"], lw=2.6, ls="--", zorder=3)
    ax.plot([zb.real], [zb.imag], "o", color=PAL["z2"], ms=9, zorder=4)
    ax.plot([z.real, zb.real], [z.imag, zb.imag], color=PAL["ghost"], lw=1.2, ls=":")
    return fig

def _read_conj(a=3.0, b=2.0):
    z = complex(a, b)
    return readout([("z", zs(z, 1)), ("z̄", zs(z.conjugate(), 1)),
                    ("z·z̄", "%.2f" % (abs(z)**2)), ("|z|", "%.3f" % abs(z))])

viz = [viz_intro_box("",
    "<b>Top:</b> step through the powers of i. Each factor of i turns the arrow by a quarter circle, "
    "so after four steps you are back at the start. This repetition makes i² = −1 look "
    "natural rather than arbitrary.<br><br>"
    "<b>Bottom:</b> drag z and watch its conjugate z̄, the mirror image across the horizontal axis. Watch "
    "the title: the product " + imath("z\\bar{z}") + " stays real and non-negative wherever "
    "you put z, because the imaginary parts cancel exactly. The absolute value in the next chapter "
    "rests on this fact.")]
viz += frame_player(_ipow_frames, _ipow_labels, description="power of i", n=5)
viz += slider_plot(_render_conj, {"a": FloatSlider(value=3.0, min=-5, max=5, step=0.5, description="a"),
                                  "b": FloatSlider(value=2.0, min=-5, max=5, step=0.5, description="b")},
                   readout_fn=_read_conj)

_PROD = TV["z1"] * TV["z2"]
on_reseed(lambda: globals().update(_PROD=TV["z1"] * TV["z2"]))   # R2 · 13

def _ans_t4(v):
    got = complex(v["re"], v["im"])
    if abs(got - _PROD) < tol():
        return True, ("Correct: %s · %s = %s. The minus sign in the real part comes from i²."
                      % (zs(TV["z1"]), zs(TV["z2"]), zs(_PROD)))
    wrong_sign = complex(_PROD.real + 2*TV["z1"].imag*TV["z2"].imag, _PROD.imag)
    if abs(got - wrong_sign) < tol():
        return False, ("Sign error: you used a₁a₂ <b>+</b> b₁b₂ for the real part. It must be "
                       "a₁a₂ <b>−</b> b₁b₂, because i·i = −1.")
    if abs(got - complex(_PROD.imag, _PROD.real)) < tol():
        return False, "You swapped the real and imaginary parts."
    return False, ("Not yet. Real part: a₁a₂ − b₁b₂ = %g·%g − %g·%g. Imaginary part: a₁b₂ + a₂b₁."
                   % (TV["z1"].real, TV["z2"].real, TV["z1"].imag, TV["z2"].imag))

practice = [
  personal(lambda: exercise_box("", taskline("<b>Multiply your two numbers.</b>")
      + formula_line(r"$z_1 z_2 = (a_1a_2 - b_1b_2) + i\,(a_1b_2 + a_2b_1)$")
      + "<div>Your pair is <b>z₁ = " + zs(TV["z1"]) + "</b> and <b>z₂ = " + zs(TV["z2"]) + "</b>. "
        "You need two products for the real part and two for the imaginary part. One minus sign "
        "decides whether the answer is right.</div>")),
  numeric_answer([("re", "Re(z₁·z₂) ="), ("im", "Im(z₁·z₂) =")], _ans_t4, task="t4",
                 answer=lambda: {"re": _PROD.real, "im": _PROD.imag}),
  # 2026-09-27 (Inhalt), eingebaut R2 · 15 — hints: the idea, then the working.
  hint_steps("t4", lambda: [
    "Multiply out the brackets as in school algebra: (a₁ + ib₁)(a₂ + ib₂) gives four products. "
    "Three of them are straightforward. One contains i·i, and i·i is −1. So that product loses its i "
    "and moves into the real part with its sign flipped. Then sort the terms: everything without i is the "
    "real part, everything with one i is the imaginary part.",
    "With your numbers the four products are %s·%s, %s·%s, %s·%s and %s·%s. The last one is "
    "%s·%s·i²; replace i² by −1. <b>Real part:</b> the first product plus the last one after that "
    "replacement. <b>Imaginary part:</b> the two middle products, added."
    % (_pn(TV["z1"].real), _pn(TV["z2"].real), _pn(TV["z1"].real), _pni(TV["z2"].imag),
       _pni(TV["z1"].imag), _pn(TV["z2"].real), _pni(TV["z1"].imag), _pni(TV["z2"].imag),
       _pn(TV["z1"].imag), _pn(TV["z2"].imag)),
  ], forbid=lambda: (_PROD.real, _PROD.imag)),
  code_fold("def mul(a1, b1, a2, b2):\n"
            "    re = ...        # watch the minus sign\n"
            "    im = ...\n"
            "    return complex(re, im)\n",
            lambda g: _check_t4(g), task="t4", locked_by="t3",
            task_text=('Write <code>mul(a1, b1, a2, b2)</code> that multiplies z₁ = a1 + i·b1 by z₂ = a2 + i·b2, working with the four components. '
                       'It returns the product as one complex number. Mind the minus sign that i·i = −1 puts into the real part. '
                       'Example: <code>mul(0, 1, 0, 1)</code> → <code>(-1+0j)</code>.'),
            solution="def mul(a1, b1, a2, b2):\n"
                     "    re = a1*a2 - b1*b2      # i² = −1 produces this minus\n"
                     "    im = a1*b2 + a2*b1\n"
                     "    return complex(re, im)\n"),
]

def _check_t4(g):
    f = g.get("mul")
    if not callable(f):
        return False, "Define a function called mul(a1, b1, a2, b2)."
    for (p, q) in [(complex(4, 3), complex(-5, 6)), (TV["z1"], TV["z2"]),
                   (complex(0, 1), complex(0, 1)), (complex(2, 0), complex(0, -3))]:
        try:
            out = complex(f(p.real, p.imag, q.real, q.imag))
        except Exception as e:
            return False, "mul raised %r." % (e,)
        want = p * q
        if abs(out - want) > 1e-9:
            if abs(out - complex(want.real + 2*p.imag*q.imag, want.imag)) < 1e-9:
                return False, ("Sign error: the real part must be a₁a₂ <b>−</b> b₁b₂, "
                               "because i·i = −1.")
            return False, ("For z₁ = %s and z₂ = %s the product is %s." % (zs(p), zs(q), zs(want)))
    return True, "Correct, including the sign from i·i = −1."

interp = interpretation_box(
  "Multiplication mixes the components, but not at random: the powers of i show that it is a "
  "<b>rotation</b>. Multiplying by i turns an arrow by 90°; multiplying by i² = −1 turns it by 180°. Chapter 6 "
  "extends this to any angle. After that, you will rarely need to write out the component "
  "formula above.")

build_chapter(4, "Multiplication and conjugation", figure='Powers of i, conjugate', info=info, viz=viz, practice=practice,
              interp=interp, locked_by="t3", task="t4")
