_intro = (
  "Write both factors in polar form and multiply: " + imath(r"|z_1|e^{i\varphi_1}\,|z_2|e^{i\varphi_2}"
  r"=|z_1||z_2|\,e^{i(\varphi_1+\varphi_2)}") + ". The exponents add, so <b>the moduli (the lengths) "
  "multiply and the angles add</b>" + cite(1) + ". Division reverses both. This one line replaces the "
  "component formula of chapter 4. It turns every complex multiplication into a picture: a rotation "
  "combined with a stretch.")

info = concept_box(_intro,
    r"$z_1 z_2 = |z_1||z_2|\,e^{i(\varphi_1+\varphi_2)}, \qquad "
    r"\frac{z_1}{z_2} = \frac{|z_1|}{|z_2|}\,e^{i(\varphi_1-\varphi_2)}$",
    variables=[("|z₁||z₂|", "the product stretches by the second modulus"),
               ("φ₁ + φ₂", "the product rotates by the second angle"),
               ("|z₁|/|z₂|", "the quotient shrinks by the second modulus"),
               ("φ₁ − φ₂", "the quotient rotates backwards")],
    extra_html=("<div style='max-width:800px;margin:14px auto 0;text-align:justify;line-height:1.6'>"
                "An important special case: if " + imath("|z_2|=1") + ", nothing is stretched, and the "
                "product is a <b>pure rotation</b> by φ₂. Multiplying by " + imath("e^{i\\pi/2}=i") +
                " is therefore the quarter turn you already met in chapter 4."
                + "</div>"))   # E26.3: the box closed (an open <div> swallowed the rest of the reading copy, JS 11.10.)

def _render_c07(r1=2.0, p1=0.5, r2=1.5, p2=1.0, op="z₁ · z₂"):
    # FIXED frame. The modulus sliders are deliberately limited to [0.5, 2.5]:
    # then the product reaches at most 6.25 and the quotient at most 5, so a frame
    # of ±6.5 always contains everything and the scale never changes.
    z1 = r1*np.exp(1j*p1); z2 = r2*np.exp(1j*p2)
    prod = "·" in op
    z = z1*z2 if prod else z1/z2
    fig, ax = fixed_canvas(figsize=(5.9, 5.9), left=.12, right=.97, top=.97, bottom=.10)
    argand_axes(ax, lim=6.5)
    for zz, col, lw in ((z1, PAL["z"], 2.5), (z2, PAL["z2"], 2.5), (z, PAL["sum"], 3.2)):
        ax.plot([0, zz.real], [0, zz.imag], color=col, lw=lw, zorder=3)
        ax.plot([zz.real], [zz.imag], "o", color=col, ms=8, zorder=4)
    th = np.linspace(np.angle(z1), np.angle(z), 90)
    rr = 0.55*min(abs(z1), abs(z))
    ax.plot(rr*np.cos(th), rr*np.sin(th), color=PAL["aux"], lw=2.0)
    return fig

def _read_c07(r1=2.0, p1=0.5, r2=1.5, p2=1.0, op="z₁ · z₂"):
    z1 = r1*np.exp(1j*p1); z2 = r2*np.exp(1j*p2)
    prod = "·" in op
    z = z1*z2 if prod else z1/z2
    return (readout([("|z₁|", "%.2f" % r1), ("φ₁", "%.2f" % (p1 % (2*np.pi))),
                     ("|z₂|", "%.2f" % r2), ("φ₂", "%.2f" % (p2 % (2*np.pi)))])
            + readout([("moduli", "%.2f %s %.2f = %.2f" % (r1, "×" if prod else "÷", r2, abs(z))),
                       ("angles", "%.2f %s %.2f = %.2f" % (p1 % (2*np.pi), "+" if prod else "−",
                                                           p2 % (2*np.pi), np.angle(z) % (2*np.pi)))])
            + readout([("result", zs(z, 3))]))

viz = [viz_intro_box("",
    "Here you steer the two numbers directly in polar form, each by a length and an angle. Switch "
    "between product and quotient and look at the line under the sliders: its two arithmetic lines are the whole "
    "rule. Try two experiments. First set <b>|z₂| = 1</b> and sweep <b>φ₂</b>. The result keeps the "
    "length of z₁ and only turns: a pure rotation. Then set <b>φ₂ = 0</b> and sweep "
    "<b>|z₂|</b>. Now the direction stays fixed and only the length changes. Every complex "
    "multiplication is a mixture of these two motions.")]
viz += slider_plot(_render_c07, {
    "r1": FloatSlider(value=2.0, min=0.5, max=2.5, step=0.1, description="|z₁|"),
    "p1": FloatSlider(value=0.5, min=0, max=6.28, step=0.05, description="φ₁"),
    "r2": FloatSlider(value=1.5, min=0.5, max=2.5, step=0.1, description="|z₂|"),
    "p2": FloatSlider(value=1.0, min=0, max=6.28, step=0.05, description="φ₂"),
    "op": Dropdown(options=["z₁ · z₂", "z₁ / z₂"], value="z₁ · z₂", description="operation")},
                   readout_fn=_read_c07)

_phi = TV["phi"]
on_reseed(lambda: globals().update(_phi=TV["phi"]))   # R2 · 13

# The target task: z1 is FIXED, the student steers z2 until the product lands on
# the marked target. Both sliders matter — one sets the length, one the angle.
_TZ1   = 2.0*np.exp(1j*0.6)                 # |z1| = 2, phi1 = 0.6
_TGT   = 3.0*np.exp(1j*(0.6 + np.pi/2))     # reachable with |z2| = 1.5, phi2 = pi/2
_TTOL  = 0.25

def _render_target(r2=1.0, p2=0.0):
    z2 = r2*np.exp(1j*p2); z = _TZ1*z2
    fig, ax = fixed_canvas(figsize=(5.6, 5.6), left=.12, right=.97, top=.97, bottom=.10)
    argand_axes(ax, lim=6.5)
    th = np.linspace(0, 2*np.pi, 200)
    ax.plot(_TGT.real + _TTOL*np.cos(th), _TGT.imag + _TTOL*np.sin(th),
            color=PAL["warn"], lw=2.0)
    ax.plot([_TGT.real], [_TGT.imag], "x", color=PAL["warn"], ms=11, mew=2.4)
    for zz, col, lw in ((_TZ1, PAL["z"], 2.4), (z2, PAL["z2"], 2.4), (z, PAL["sum"], 3.2)):
        ax.plot([0, zz.real], [0, zz.imag], color=col, lw=lw, zorder=3)
        ax.plot([zz.real], [zz.imag], "o", color=col, ms=8, zorder=4)
    return fig

def _read_target(r2=1.0, p2=0.0):
    z = _TZ1*r2*np.exp(1j*p2); d = abs(z - _TGT)
    state = ("<span class='nbok'>on target</span>" if d < _TTOL else
             "<span class='nbwarn'>distance to target: %.2f</span>" % d)
    # Say what is still off, and in WHICH of the two quantities — searching blindly
    # with two sliders is what made this exercise feel unsolvable.
    dr = abs(z) - abs(_TGT)
    dp = (np.angle(z) - np.angle(_TGT) + np.pi) % (2*np.pi) - np.pi
    hint = ("length %s &nbsp;·&nbsp; angle %s"
            % ("<b class='nbok'>right</b>" if abs(dr) < _TTOL/2 else
               (("<b>%+.2f too long</b>" if dr > 0 else "<b>%+.2f too short</b>") % dr),
               "<b class='nbok'>right</b>" if abs(dp) < _TTOL/6 else
               ("<b>%+.2f rad</b>" % dp)))
    return (readout([("|z₁|·|z₂|", "2.00 × %.2f = %.2f  (target %.2f)"
                                   % (r2, abs(z), abs(_TGT))),
                     ("φ₁+φ₂", "0.60 + %.2f = %.2f  (target %.2f)"
                               % (p2 % (2*np.pi), np.angle(z) % (2*np.pi),
                                  np.angle(_TGT) % (2*np.pi))),
                     ("product", zs(z, 2))])
            + "<div style='text-align:center;font-weight:700;margin-top:2px'>%s</div>" % state
            + "<div style='text-align:center;margin-top:2px;font-size:.92em'>%s</div>" % hint)

def _ans_t7(v):
    z = _TZ1*v["r2"]*np.exp(1j*v["p2"])
    d = abs(z - _TGT)
    if d < _TTOL:
        return True, ("On target. You needed |z₂| = %.2f, so that 2·|z₂| = %.1f, and φ₂ = %.2f, so "
                      "that 0.60 + φ₂ reaches %.2f. Length and angle can be set independently."
                      % (abs(_TGT)/2, abs(_TGT), np.pi/2, np.angle(_TGT) % (2*np.pi)))
    if abs(abs(z) - abs(_TGT)) > _TTOL:
        return False, ("The length is off: the product has |z| = %.2f, but the target sits at %.2f. "
                       "Remember that the moduli <i>multiply</i>, and |z₁| is fixed at 2."
                       % (abs(z), abs(_TGT)))
    return False, ("The length is right, the direction is not: your product points at %.2f rad, "
                   "the target at %.2f rad. The angles <i>add</i>, and φ₁ is fixed at 0.60."
                   % (np.angle(z) % (2*np.pi), np.angle(_TGT) % (2*np.pi)))

practice = [
  exercise_box("", taskline("<b>Steer the product onto the target.</b>")
      + "<div><b>z₁ is fixed</b> at " + imath("|z_1| = 2") + ", " + imath("\\varphi_1 = 0.60") +
        ". Move the two sliders for <b>z₂</b> until the green product arrow lands inside the orange "
        "target circle. Then press the button. You do not type or compute anything. But you will "
        "only find the target quickly if you use the rule: the moduli multiply, the angles add.</div>"),
]
practice += target_exercise(_render_target, {
    "r2": FloatSlider(value=1.0, min=0.5, max=3.0, step=0.05, description="|z₂|"),
    "p2": FloatSlider(value=0.0, min=0, max=6.28, step=0.02, description="φ₂")},
    _ans_t7, task="t7", readout_fn=_read_target,
    # E26 Teil 2: typed in the reading window; the two tolerances together stay inside _TTOL
    answer=lambda: {"r2": (abs(_TGT) / abs(_TZ1), _TTOL / (3 * abs(_TZ1))),
                    "p2": ((np.angle(_TGT) - np.angle(_TZ1)) % (2*np.pi), _TTOL / (3 * abs(_TGT)), 2*np.pi)})
# 2026-09-27 (Inhalt), eingebaut R2 · 15 — hints: the idea, then the working.
practice += [
  hint_steps("t7", [
    "Two sliders, two separate questions. Do not search with both at once. Multiplying "
    "<i>multiplies the lengths</i> and <i>adds the angles</i>. So the length of the product depends "
    "only on |z₂|, and its direction only on φ₂. Set one slider, then the other.",
    "Start with the length. The product is 2·|z₂| long, because |z₁| is 2. The readout shows the "
    "target's length: divide it by 2 and set |z₂| to the result. Then the angle. The product points "
    "at 0.60 + φ₂. The readout shows the target's angle: subtract 0.60 and set φ₂ to the result. The "
    "line under the readout tells you which of the two is still off.",
  ], forbid=(abs(_TGT) / 2, (np.angle(_TGT) - 0.6) % (2 * np.pi))),
]
practice += [
  code_fold("import numpy as np\n\n"
            "def rotate(a, b, phi):\n"
            "    # turn z = a + ib by phi, keeping |z| the same\n"
            "    ...\n",
            lambda g: _check_t7(g), task="t7", locked_by="t6",
            task_text=('Write a function <code>rotate(a, b, phi)</code> that turns z = a + ib anticlockwise about the origin by the angle phi (in radians). The length |z| must stay the same. '
                       'The function returns the rotated number z·e^(iφ) as a single complex number. '
                       'Example: <code>rotate(1, 0, np.pi/2)</code> → about <code>1j</code>.'),
            solution="import numpy as np\n\n"
                     "def rotate(a, b, phi):\n"
                     "    c, s = np.cos(phi), np.sin(phi)\n"
                     "    return complex(a*c - b*s, a*s + b*c)\n"),
]

def _check_t7(g):
    f = g.get("rotate")
    if not callable(f):
        return False, "Define a function called rotate(a, b, phi)."
    for z, ph in [(complex(1, 0), np.pi/2), (complex(3, 2), _phi), (complex(-2, -4), np.pi),
                  (TV["z1"], 0.0), (complex(0, 2), -np.pi/2)]:
        try:
            out = complex(f(z.real, z.imag, ph))
        except Exception as e:
            return False, "rotate raised %r." % (e,)
        want = z*np.exp(1j*ph)
        if abs(abs(out) - abs(z)) > 1e-7:
            return False, ("A rotation must not change the length: |z| = %.4f, but your result has "
                           "|w| = %.4f." % (abs(z), abs(out)))
        if abs(out - want) > 1e-7:
            if abs(out - z*np.exp(-1j*ph)) < 1e-7:
                return False, "You are rotating clockwise. Check the sign of the sine terms."
            return False, ("Rotating %s by %.3f rad gives %s." % (zs(z), ph, zs(want, 3)))
    return True, "Length preserved, direction correct, and the quarter turn lands on i."

interp = interpretation_box(
  "This is the payoff of the whole notebook. Complex multiplication is not an odd bookkeeping rule. "
  "It is a <b>rotation with a stretch</b>. That is why complex numbers appear wherever something "
  "oscillates or turns: alternating currents, waves, the Fourier transform of section 1.9 of the "
  "script, and the membrane impedance in the appendix" + cite(5) + ". A single number carries an "
  "amplitude (a size) and a phase (an angle) at the same time.")

build_chapter(7, "The geometry of multiplication", figure='Rotate and stretch', info=info, viz=viz, practice=practice,
              interp=interp, locked_by="t6", task="t7")
