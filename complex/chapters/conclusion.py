# E21.13 (2026-10-02, Inhalt + Struktur) — ONE CHAPTER "CONCLUSION" (Nutzer:
# "Summary + Glossary → ein Kapitel Conclusion; Setup entfällt"). It holds
# what summary.py, glossary.py and the setup chapter said that a reader still
# needs: the rules on one screen, the terms, the source of the content, and
# the two red notes — the locks are no assessment (Konzept §4, E19.8: in the
# Appendix, red) and the numbers are drawn from your own seed (was Setup).
# The seed itself is in the ⚙ drawer; the old line "runs entirely in your
# browser (JupyterLite / Pyodide)" is gone with Setup: it was not true in
# JupyterLab on a server.
_rules = [
 ("i² = −1", "the one definition that everything else follows from"),
 ("z = a + ib", "a pair of real numbers: Re(z) = a and Im(z) = b, so Im(z) is real too"),
 ("point / arrow", "Re horizontal, Im vertical: algebra becomes geometry"),
 ("z₁ ± z₂", "component by component, like adding vectors; real and imaginary parts never mix"),
 ("z₁·z₂", "(a₁a₂ − b₁b₂) + i(a₁b₂ + a₂b₁); the minus sign comes from i²"),
 ("z̄ = a − ib", "the mirror image across the real axis; z·z̄ = |z|² is real"),
 ("|z| = √(a²+b²)", "the length of the arrow; the only quantity in ℂ you can order"),
 ("z₁/z₂", "multiply by the conjugate of the denominator, then divide by a real number"),
 ("z = |z|e^{iφ}", "polar form (length and angle); e^{iπ} = −1"),
 ("φ = arctan(b/a)", "valid only for a > 0; add π when a < 0"),
 ("z₁z₂ polar", "moduli multiply, angles add: rotation plus stretch"),
]
_terms = [
 ("imaginary unit i", "the number with i² = −1"),
 ("complex number", "z = a + ib with a, b ∈ ℝ"),
 ("real part Re(z)", "a, a real number"),
 ("imaginary part Im(z)", "b, also a real number: the factor in front of i"),
 ("Argand plane", "the plane with Re on the horizontal axis and Im on the vertical axis; z is a point in it"),
 ("conjugate z̄", "a − ib; the mirror image of z across the real axis"),
 ("modulus |z|", "√(a²+b²) = √(z z̄); the distance from the origin"),
 ("argument φ", "the angle of z, measured from the positive real axis, in radians"),
 ("polar form", "z = |z|(cos φ + i sin φ) = |z| e^{iφ}"),
 ("Euler's relation", "e^{iπ} = −1, the case φ = π of the polar form"),
 ("quadrant correction", "the extra + π that arctan(b/a) needs whenever Re(z) < 0"),
]
def _table(rows, pad):
    return ("<table style='border-collapse:collapse;margin:12px auto 0'>%s</table>" % "".join(
        "<tr><td style='padding:%s 16px %s 0;vertical-align:top;white-space:nowrap'><b>%s</b></td>"
        "<td style='padding:%s 0'>%s</td></tr>" % (pad, pad, a, pad, b) for a, b in rows))
build_chapter(None, "Conclusion", icon="📋", chapter_open=False, anchor="conclusion",
  info=note_box("Everything on one screen:" + _table(_rules, "5px")
                + "<div style='margin-top:12px'>All content follows section 1.2 of the lecture "
                  "script" + cite(1) + ".</div>"),
  body=[note_box("<b>Glossary</b>" + _table(_terms, "4px")),
        warn_box(
    "<b>The locks in this notebook set your pace; they are not an assessment.</b> Everything runs in "
    "your browser, the check functions sit in the same cell as the exercises, and the "
    "<b>Skip for now</b> button is there on purpose. Treat the timeline as a note to yourself about "
    "what to revisit."),
        warn_box(
    "<b>Your numbers are not your neighbour's.</b> The exercise values are drawn from your seed. "
    "This makes copying pointless. It also means that your numbers differ from those on your "
    "neighbour's screen, so quote the seed when you ask someone about a result" + cite(7) + ".")])
