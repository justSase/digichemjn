_txt = (
  "A script is a working document, and its author says so himself" + cite(1) + ": “There is no "
  "guarantee that the content of this script is complete or correct. If you figure out any further "
  "errors or other issues, please contact me.” Taking that seriously is a skill in its own right — "
  "and it applies to this notebook too, and to anything an AI hands you.<br><br>"
  "Section 1.2 contains three small inconsistencies. None of them breaks the mathematics, and two "
  "are pure transcription slips, but each one will cost you time if you copy it without checking. "
  "Go and look at these three places:"
  "<ul style='max-width:720px;margin:10px auto;text-align:left'>"
  "<li><b>p. 35, solution to exercise 1.8 d)</b>, " + imath("z=-2-4i") + ": the angle is given both in "
  "radians and in degrees. Convert one into the other and see whether they agree. Exercise 1.8 b) is "
  "a useful control — there the two do agree.</li>"
  "<li><b>p. 27, figure 1.2</b>: compare the axis <i>names</i> in the figure with the sentence above "
  "it, and with figure 1.3 on p. 33.</li>"
  "<li><b>p. 29, solution to exercise 1.3 b)</b>: compare the value of " + imath("z_2") + " as the "
  "exercise states it with the way the solution repeats it, then check which of the two the printed "
  "results actually belong to.</li></ul>")

info = note_box(_txt, grey=True)

_PHI_TRUE = np.arctan2(-4.0, -2.0) % (2*np.pi)      # 4.2487 rad = 243.4 deg

def _ans_t8(v):
    phi = float(v["phi"]) % (2*np.pi)
    if abs(phi - _PHI_TRUE) < tol():
        return True, ("Correct: φ = %.4f rad, and that is %.1f°. So the script's 243.4° is right "
                      "while the 2.678 rad printed next to it is not — 2.678 rad would be %.1f°."
                      % (_PHI_TRUE, np.degrees(_PHI_TRUE), np.degrees(2.678)))
    if abs(phi - 2.678) < tol():
        return False, ("That is the value printed in the script — the one you are checking. "
                       "Convert it to degrees and compare it with the 243.4° beside it.")
    if abs(((phi - _PHI_TRUE) % (2*np.pi)) - np.pi) < tol():
        return False, "Off by π: Re(z) = −2 is negative, so arctan(b/a) still needs the + π."
    if abs(phi - 243.4) < 1.0 or abs(v["phi"] - 243.4) < 1.0:
        return False, "That is the degree value — the box asks for radians."
    return False, ("Not yet. Compute arctan(−4 / −2) = arctan(2), then add π because Re(z) < 0.")

_AXOPTS = ["the horizontal axis", "the vertical axis",
           "both figures agree, there is nothing wrong"]

def _ans_axis(idx, label):
    if idx == 0:
        return True, ("Right. The text says “we define the x-axis as the real axis”, and figure 1.3 "
                      "on p. 33 draws it that way — figure 1.2 has its two axis names swapped.")
    if idx == 1:
        return False, ("That is what figure 1.2 claims, but read the sentence just above it, and "
                       "compare with figure 1.3 on p. 33.")
    return False, "Compare the axis labels of figure 1.2 with those of figure 1.3 — they disagree."

practice = [
  exercise_box("", taskline("<b>Report the angle you computed.</b>")
      + "<div>For " + imath("z=-2-4i") + ", give the <i>correct</i> angle <b>in radians</b>, on "
        + imath("[0,2\\pi)") + ". Then compare it with both numbers the script prints in the "
        "solution to exercise 1.8 d) — one of the two is right, the other is not.</div>"),
  numeric_answer([("phi", "φ [rad] =")], _ans_t8, task="t8", columns=1),
  choice_answer("In the convention the text defines, which axis carries the real part?",
                _AXOPTS, _ans_axis),
  code_fold("import numpy as np\n\n"
            "def verify_script():\n"
            "    return {\n"
            "        'phi_rad':   ...,\n"
            "        'deg_ok':    ...,\n"
            "        'real_axis': ...,\n"
            "    }\n",
            lambda g: _check_t8(g), task="t8",
            solution="import numpy as np\n\n"
                     "def verify_script():\n"
                     "    a, b = -2.0, -4.0\n"
                     "    phi = np.arctan(b/a) + np.pi      # a < 0 -> quadrant III, so + pi\n"
                     "    # 4.2487 rad = 243.4 deg -> the DEGREE value in the script is right,\n"
                     "    # the printed 2.678 rad is not (that would be 153.4 deg).\n"
                     "    return {\n"
                     "        'phi_rad':   phi % (2*np.pi),\n"
                     "        'deg_ok':    True,\n"
                     "        'real_axis': 'horizontal',\n"
                     "    }\n"),
]

def _check_t8(g):
    f = g.get("verify_script")
    if not callable(f):
        return False, "Define a function called verify_script() returning a dictionary."
    try:
        d = f()
    except Exception as e:
        return False, "verify_script raised %r." % (e,)
    if not isinstance(d, dict):
        return False, "Return a dictionary with the keys phi_rad, deg_ok and real_axis."
    miss = [k for k in ("phi_rad", "deg_ok", "real_axis") if k not in d]
    if miss:
        return False, "Missing key(s): %s." % ", ".join(miss)
    want = np.arctan2(-4.0, -2.0) % (2*np.pi)      # 4.2487 rad
    try:
        phi = float(d["phi_rad"]) % (2*np.pi)
    except Exception:
        return False, "phi_rad must be a number in radians."
    if abs(phi - want) > tol():
        if abs(phi - 2.678) < tol():
            return False, ("That is the value printed in the script — the one you are asked to check. "
                           "Convert it to degrees and compare with the 243.4° next to it.")
        if abs(phi - (want - np.pi) % (2*np.pi)) < tol():
            return False, "Off by π: for a < 0 the arctan result still needs the + π correction."
        return False, ("Not yet: the correct angle is near %.4f rad, you returned %.4f rad "
                       "(= %.1f°)." % (want, phi, np.degrees(phi)))
    if d["deg_ok"] is not True:
        return False, ("Check the degree value on its own: %.4f rad converts to %.1f°. Is the "
                       "script's 243.4° right or wrong?" % (want, np.degrees(want)))
    ax = str(d["real_axis"]).strip().lower()
    if not ax.startswith("h"):
        return False, ("Re-read the sentence above figure 1.2: “We define the x-axis as the real axis” "
                       "— so which axis is that, horizontal or vertical? Figure 1.3 does it right; "
                       "figure 1.2 does not.")
    return True, ("Exactly right. The degree value 243.4° is correct while the printed 2.678 rad is "
                  "not (that would be 153.4°), and figure 1.2 has its axis names swapped. Worth "
                  "sending to the lecturer — that is how a script gets better.")

build_chapter(None, "Verify the script", icon="🔍", chapter_open=False, anchor="verify",
              info=info, practice=practice, task="t8")
