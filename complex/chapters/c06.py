_intro = (
  "You can describe a point in the plane by its coordinates or by its <b>distance and direction</b>. "
  "For complex numbers the second description is the natural one. With " + imath("a=|z|\\cos\\varphi")
  + " and " + imath("b=|z|\\sin\\varphi") + " we get " + imath("z=|z|(\\cos\\varphi+i\\sin\\varphi)") +
  ". The bracket is exactly the series expansion of " + imath("e^{i\\varphi}") + cite(1, 4) + ". "
  "This identity is the key to the whole topic. At " + imath("\\varphi=\\pi") + " it reads "
  + imath("e^{i\\pi}=-1") + ".")

info = concept_box(_intro,
    r"$z = |z|\,(\cos\varphi + i\sin\varphi) = |z|\,e^{i\varphi}$",
    variables=[("|z| = √(a²+b²)", "modulus: the distance from the origin"),
               ("φ", "argument: the angle measured from the positive real axis, in radians (not degrees)"),
               ("φ(rad)/φ(deg)", "= π/180°, the conversion between the two")],
    extra_html=("<div style='max-width:800px;margin:14px auto 0;text-align:justify;line-height:1.6'>"
                "The angle is defined on " + imath("[0,2\\pi]") + ". The obvious formula "
                + imath(r"\varphi=\arctan(b/a)") + " only works for " + imath("a>0") + ", that is, "
                "in quadrants I and IV. For " + imath("a<0") + " you must add π. The second "
                "visualisation below shows exactly this trap."
                + "</div>"))   # E26.3: the box closed (an open <div> swallowed the rest of the reading copy, JS 11.10.)

# ---- Euler unfolding: pre-rendered frames --------------------------------
_NFR = 25
def _euler_frame(k):
    phi = 2*np.pi*k/(_NFR-1)
    fig, ax = fixed_canvas(figsize=(4.9, 4.9), left=.14, right=.96, top=.96, bottom=.12)
    argand_axes(ax, lim=1.55)
    th = np.linspace(0, 2*np.pi, 300)
    ax.plot(np.cos(th), np.sin(th), color=PLOT_INK, lw=1.0, alpha=.4)
    tt = np.linspace(0, phi, max(2, int(60*phi/(2*np.pi)) + 2))
    ax.plot(np.cos(tt), np.sin(tt), color=PAL["aux"], lw=2.4, alpha=.9)
    c, s = np.cos(phi), np.sin(phi)
    ax.plot([0, c], [0, s], color=PAL["z"], lw=2.8, zorder=3)
    ax.plot([c], [s], "o", color=PAL["z"], ms=9, zorder=4)
    ax.plot([c, c], [0, s], color=PAL["sum"], lw=2.0, ls="--")
    ax.plot([0, c], [0, 0], color=PAL["z2"], lw=2.0, ls="--")
    ax.plot([c], [0], "o", color=PAL["z2"], ms=6)
    ax.plot([0], [s], "o", color=PAL["sum"], ms=6)
    ax.plot([0, 0], [0, s], color=PAL["sum"], lw=2.0, ls=":", alpha=.7)
    ax.set_xticks([-1, 0, 1]); ax.set_yticks([-1, 0, 1])
    return fig

# Paket 21b — drawn when the chapter opens, not at start (frame_player takes the function)
_euler_frames = lambda k: fig_to_html(_euler_frame(k), dpi=82, tight=False)
_euler_labels = []
for k in range(_NFR):
    phi = 2*np.pi*k/(_NFR-1)
    note = ""
    if abs(phi - np.pi) < np.pi/(_NFR-1):
        note = ("&nbsp;&nbsp;<b class='nbaccent'>half a turn: e<sup>iπ</sup> = −1</b>"
                ": Euler's relation, read straight off the picture")
    elif abs(phi - np.pi/2) < np.pi/(_NFR-1):
        note = "&nbsp;&nbsp;<b class='nbaccent'>a quarter turn: e<sup>iπ/2</sup> = i</b>"
    _euler_labels.append(
        readout([("φ", "%.3f rad" % phi), ("", "%.1f°" % np.degrees(phi)),
                 ("cos φ", "%+.3f" % np.cos(phi)), ("sin φ", "%+.3f" % np.sin(phi))])
        + ("<div style='text-align:center;font-size:.92em'>%s</div>" % note if note else ""))

# ---- the arctan trap -----------------------------------------------------
def _render_trap(a=-2.0, b=-4.0):
    # FIXED frame ±6; sliders run to ±5. Numbers go to the readout, not the title.
    z = complex(a, b)
    naive = np.arctan(b/a) if abs(a) > 1e-12 else np.sign(b)*np.pi/2
    fig, ax = fixed_canvas(figsize=(5.6, 5.6), left=.12, right=.97, top=.97, bottom=.10)
    argand_axes(ax, lim=6)
    r = max(abs(z), 1e-9)
    ax.plot([0, r*np.cos(naive)], [0, r*np.sin(naive)], color=PAL["warn"], lw=2.4,
            ls="--", zorder=3)
    ax.plot([0, z.real], [0, z.imag], color=PAL["z"], lw=2.8, zorder=3)
    ax.plot([z.real], [z.imag], "o", color=PAL["z"], ms=9, zorder=4)
    return fig

def _read_trap(a=-2.0, b=-4.0):
    z = complex(a, b)
    naive = np.arctan(b/a) if abs(a) > 1e-12 else np.sign(b)*np.pi/2
    true = np.arctan2(b, a) % (2*np.pi)
    ok = abs(((naive - true + np.pi) % (2*np.pi)) - np.pi) < 1e-9
    verdict = ("<span class='nbok'>arctan is correct here (a &gt; 0)</span>" if ok else
               "<span class='nbwarn'>arctan is off by π: add π</span>")
    return (readout([("z", zs(z, 1)),
                     ("arctan(b/a)", "%.3f rad" % naive), ("", "%.1f°" % np.degrees(naive)),
                     ("true φ", "%.3f rad" % true), ("", "%.1f°" % np.degrees(true))])
            + "<div style='text-align:center;font-weight:700;margin-top:2px'>%s</div>" % verdict)

viz = [viz_intro_box("",
    "<b>Top: the unfolding.</b> Step φ from 0 to 2π. The arrow rides around the unit circle (the "
    "circle of radius one). Its shadow on the horizontal axis traces cos φ (blue), its shadow on the "
    "vertical axis traces sin φ (green). Stop at step 12: the arrow points at −1. That is Euler's "
    "relation, with nothing left to prove. The frames are pre-rendered, so stepping is instant.<br><br>"
    "<b>Bottom: the trap.</b> The red arrow is the true z. The dashed orange arrow is what the plain "
    "formula " + imath(r"\arctan(b/a)") + " gives you. Keep <b>a</b> positive and the two coincide. "
    "Make <b>a</b> negative (quadrant II or III) and they differ by exactly π. The reason: arctan "
    "only returns values between −π/2 and +π/2, so it cannot tell those quadrants apart.")]
viz += frame_player(_euler_frames, _euler_labels, description="φ step", n=_NFR)
viz += slider_plot(_render_trap, {"a": FloatSlider(value=-2.0, min=-5, max=5, step=0.5, description="a"),
                                  "b": FloatSlider(value=-4.0, min=-5, max=5, step=0.5, description="b")},
                   readout_fn=_read_trap)

_zq = TV["zq"]
_RQ  = abs(_zq)
_PHQ = np.angle(_zq) % (2*np.pi)

@on_reseed
def _tv_c06():                                   # R2 · 13: new seed, in place
    global _zq, _RQ, _PHQ
    _zq = TV["zq"]
    _RQ  = abs(_zq)
    _PHQ = np.angle(_zq) % (2*np.pi)

def _ans_t6(v):
    if abs(v["r"] - _RQ) > tol():
        return False, ("The modulus is not right: |z| = √(a² + b²) = √(%g² + %g²) = %.4f."
                       % (_zq.real, _zq.imag, _RQ))
    phi = v["phi"] % (2*np.pi)
    if abs(((phi - _PHQ + np.pi) % (2*np.pi)) - np.pi) < tol():
        return True, ("Correct: |z| = %.4f and φ = %.4f rad = %.1f°. Your z is in the third "
                      "quadrant, so the + π was needed." % (_RQ, _PHQ, np.degrees(_PHQ)))
    if abs(((phi - _PHQ) % (2*np.pi)) - np.pi) < tol():
        return False, ("Off by exactly π. That is the trap: Re(z) = %g is negative, so the plain "
                       "arctan(b/a) lands in the wrong half of the plane. You need to add π."
                       % _zq.real)
    if abs(phi - np.degrees(_PHQ)) < 0.5:
        return False, "That looks like degrees. Enter the angle in radians."
    return False, ("The modulus is right, but the angle is not. Start from arctan(b/a) = arctan(%g/%g). "
                   "Then check the sign of Re(z): it decides whether you have to add π."
                   % (_zq.imag, _zq.real))

practice = [
  personal(lambda: exercise_box("", taskline("<b>Write your number in polar form.</b>")
      + formula_line(r"$|z| = \sqrt{a^2+b^2}, \qquad \varphi = \arctan\left(\frac{b}{a}\right)"
                     r"\;\;(+\,\pi \;\; \mathrm{for}\;\; a<0)$")
      + "<div>Your personal number is <b>z = " + zs(_zq) + "</b>. Give the modulus and the angle "
        "<b>in radians</b>, on the interval " + imath("[0,2\\pi)") + ". "
        # 12b: gentle is −k − ki (no calculator), standard/strict a Pythagorean point
        + (("Here b/a = 1, so " + imath("\\arctan(b/a) = \\pi/4") + " follows without a calculator")
           if abs(_zq.real) == abs(_zq.imag) else
           ("Here |z| is a whole number. For the angle, use your calculator's arctan (in radians)"))
        + ". But check the sign of the "
        "real part before you trust the result. The second visualisation above shows what goes "
        "wrong otherwise. Enter decimals (" + imath("\\pi \\approx 3.1416")
        + (", " + imath("\\sqrt{2} \\approx 1.4142") if abs(_zq.real) == abs(_zq.imag) else "")
        + ").</div>")),
  numeric_answer([("r", "|z| ="), ("phi", "φ [rad] =")], _ans_t6, task="t6",
                 answer=lambda: {"r": _RQ, "phi": (_PHQ, None, 2*np.pi)}),
  # 2026-09-27 (Inhalt), eingebaut R2 · 15 — hints: the idea, then the working
  # with the reader's own number (always −k − ki since R1 · 12).
  hint_steps("t6", lambda: [
    "Two boxes, two questions. <b>|z|</b> is the length of the arrow from 0 to z; you get it with "
    "Pythagoras from the two components. <b>φ</b> is the angle measured anticlockwise from the "
    "positive real axis. Before you compute anything, sketch z = " + zs(_zq) + ". Which quadrant is "
    "it in? The quadrant fixes the range for φ (I: 0 to π/2, II: π/2 to π, III: π to 3π/2, "
    "IV: 3π/2 to 2π).",
    ("|z| is √(a² + b²), with a and b both %s. For the angle, start from arctan(b/a). Here b/a is 1, "
     "and arctan 1 is π/4. But that angle belongs to an arrow pointing to the <i>right</i>. Your a is "
     "negative, so your arrow points to the left: add π. Check that the result lies between π and "
     "3π/2, and enter it in radians." % _pn(_zq.real)) if abs(_zq.real) == abs(_zq.imag) else
    # 12b: a Pythagorean point (standard/strict): |z| is whole, the angle needs a calculator
    ("|z| is √(a² + b²) with a = %s and b = %s. Square both, add them and take the root; the "
     "result is a whole number. For the angle, type arctan(b/a) into a calculator set to radians. "
     "It returns an angle between −π/2 and π/2, which belongs to an arrow pointing to the "
     "<i>right</i>. Your a is negative, "
     "so your arrow points to the left: add π. Check that the result lies between π and 3π/2."
     % (_pn(_zq.real), _pn(_zq.imag))),
  ], forbid=lambda: (_RQ, _PHQ, np.degrees(_PHQ))),
  code_fold("import numpy as np\n\n"
            "def to_polar(a, b):\n"
            "    r = ...\n"
            "    phi = ...          # correct in ALL four quadrants, in [0, 2*pi)\n"
            "    return (r, phi)\n",
            lambda g: _check_t6(g), task="t6", locked_by="t5",
            task_text=('Write a function <code>to_polar(a, b)</code> that converts z = a + ib into polar form. '
                       'It returns the tuple (r, phi): the modulus r = |z| and the angle phi in radians. The angle must be correct in all four quadrants and lie in [0, 2π). '
                       'Example: <code>to_polar(-3, 4)</code> → <code>(5.0, 2.214…)</code>.'),
            solution="import numpy as np\n\n"
                     "def to_polar(a, b):\n"
                     "    r = np.hypot(a, b)                  # = sqrt(a**2 + b**2)\n"
                     "    phi = np.arctan2(b, a) % (2*np.pi)  # arctan2 picks the right quadrant\n"
                     "    return (r, phi)\n"),
]

def _check_t6(g):
    f = g.get("to_polar")
    if not callable(f):
        return False, "Define a function called to_polar(a, b)."
    for z in [complex(4, 3), complex(-3, 4), complex(10, 0), complex(-2, -4), _zq, complex(0, -5)]:
        try:
            out = f(z.real, z.imag)
        except Exception as e:
            return False, "to_polar raised %r." % (e,)
        if not isinstance(out, (tuple, list)) or len(out) != 2:
            return False, "Return exactly two values: (r, phi)."
        r, phi = float(out[0]), float(out[1])
        if abs(r - abs(z)) > 1e-8:
            return False, "For z = %s the modulus is %.4f." % (zs(z), abs(z))
        want = np.angle(z) % (2*np.pi)
        if abs(((phi - want + np.pi) % (2*np.pi)) - np.pi) > 1e-7:
            if abs(((phi - want) % (2*np.pi)) - np.pi) < 1e-6:
                return False, ("Off by exactly π for z = %s. For a < 0 the angle needs + π "
                               "(or use np.arctan2)." % zs(z))
            return False, "For z = %s the angle is %.4f rad." % (zs(z), want)
        if not (-1e-9 <= phi < 2*np.pi + 1e-9):
            return False, "The angle is right but outside [0, 2π)."
    return True, "Correct in all four quadrants."

interp = interpretation_box(
  "Polar form does not add information. It <b>re-sorts</b> it: the same number is now described by a "
  "length and a direction. The next chapter shows why this pays off. In polar form, multiplying is "
  "almost no work at all. The price is the caveat above: the angle needs a quadrant check that "
  "the textbook formula quietly leaves out.")

# E19.8 — from "Remarks and limits": the pitfall of this chapter, in red
warn = warn_box(
  "<b>The angle is only defined up to 2π</b>, and a number on the negative real axis sits exactly at the "
  "seam. Libraries choose different intervals: <b>np.angle</b> returns "
  "(−π, π], while this notebook wraps to [0, 2π). Neither is more correct, but mixing them unnoticed is a "
  "reliable source of sign errors.")

build_chapter(6, "Polar form and Euler's relation", figure='Euler and the arctan trap', info=info, viz=viz, practice=practice,
              interp=interp, body=[warn], locked_by="t5", task="t6")
