# ---------------------------------------------------------------------------
# DigiChemJN · Complex numbers — domain setup
# Source of the content: L. Heidinger, "Principles of Biophysics" &
# "Computational methods", Univ. Freiburg, WS 2025/26, section 1.2 (pp. 26-38).
# ---------------------------------------------------------------------------

# Subject standard first (it may override DESIGN), then the stylesheet.
use_profile("biophysics")
# the document speaks the panel's language: one quiet surface, colour only for state
use_style("quiet")
set_notebook("complex-numbers", "Complex Numbers")
# --- OER record (FCI proposal: open licence, metadata, DOI, versioning) -----
set_metadata(
    thema="math.complex-numbers",                # E39a: Katalog-Schlüssel bereich.thema (eindeutig)
    kurse=[("ALU · Einführung in die Biophysik", "1.2")],
    title="Complex Numbers",
    subtitle="Principles of Biophysics & Computational methods, section 1.2",
    authors=["… Autor:innen bitte eintragen …"],
    institution="Fakultät für Chemie und Pharmazie, Albert-Ludwigs-Universität Freiburg",
    licence="CC BY-SA 4.0",
    licence_url="https://creativecommons.org/licenses/by-sa/4.0/",
    version=NB_VERSION,
    date="2026-09",
    doi="",                     # reserved on the Zenodo deposit
    repo="",                    # GitHub URL once the module is published
    audience="Master Chemie, Biochemie & Biophysik, Pharmazeutische Wissenschaften, "
             "Sustainable Materials — from the 7th semester",
    prerequisites="School algebra and trigonometry; no programming knowledge required",
    # duration: not typed — time_budget() counts it (refs.py writes it in)
    keywords=["complex numbers", "Argand plane", "Euler's relation", "polar form",
              "impedance", "biophysics", "OER", "Jupyter", "DigiChemJN"],
    source="L. Heidinger, Principles of Biophysics & Computational methods, "
           "Univ. Freiburg, WS 2025/26, section 1.2 (pp. 26–38)",
)
inject_style()

# --- personal task values -------------------------------------------------
# Seeded from the per-run notebook id, so two students almost never get the
# same numbers and a copied answer is worthless. The seed is printed in the
# Setup box, so any result stays reproducible: same seed -> same numbers.
# 2026-09-24ac — the reader can pin this. notebook_seed() hands back the seed
# they stored in the toolbar's gear drawer, and only falls back to the per-run
# id when they have not. Same seed -> same numbers, on any machine.
CX_SEED = notebook_seed(int(_NBID, 16) % 100000)
# R3 · 18 — which content this run builds (calc / code / both), read once,
# before the first chapter: DIGICHEM_MODE, else the stored choice, else both
CX_MODE = notebook_mode()
_rng = np.random.default_rng(CX_SEED)

# 2026-09-28 (R1 · Paket 12, Inhalt + Applikation) — SOLVABLE WITHOUT A COMPUTER.
# Every personal number is drawn so that the answer can be worked out with pen
# and paper, and every number the exercise asks the reader to SET on a slider
# lies on that slider (range and step):
#   q   a perfect square 4 … 144, so √q is a whole number (was 2 … 12: √q
#       irrational, "work it out on a calculator")
#   z1, z2  components in ±5 — the sliders of chapters 2 and 4 run ±5 in steps
#       of 0.5; ±6 could not be set there
#   n5 / d5  chapter 5 divides the reader's own pair, built backwards from a
#       quotient with whole components, so the result is whole; the numerator
#       stays within ±7, the sliders of chapter 5 (was the fixed lecture pair
#       (4+3i)/(−5+6i) = −2/61 − 39/61 i, which needs long division by 61)
#   zq  = −k − ki: arctan(b/a) = arctan 1 = π/4 by hand, φ = 5π/4, |z| = k√2.
#       Any other integer point in quadrant III needs a calculator's arctan.
# `_draw_tv` is a function so a seed sweep can call it without the notebook.
# 2026-09-28 (Paket 12b, Inhalt + Applikation) — THE EASIEST LEVEL NEEDS NO
# CALCULATOR, AND THE NUMBERS NOW DEPEND ON THE LEVEL. In gentle every input
# and every result is whole or .5, a modulus is whole or k√2, an angle a
# multiple of π/4 or π/6 — which the draw above already gives. Standard and
# strict may need a calculator: exercise 6 is a Pythagorean point in quadrant
# III there (|z| whole, arctan(b/a) not a known value) instead of −k − ki.
# The same number of draws on every level, so a seed keeps all other numbers
# when only the level changes. reseed() (Paket 13) calls this without a level,
# so it follows the level that is set.
_T6_PYTH = ((-3, -4), (-4, -3), (-6, -8), (-8, -6), (-5, -12))

def _draw_tv(rng, level=None):
    level = level or DIFFICULTY["level"]
    def nz(lo, hi):
        v = 0
        while v == 0:
            v = int(rng.integers(lo, hi + 1))
        return v
    k = int(rng.integers(2, 13))
    z1 = complex(nz(-5, 5), nz(-5, 5))
    z2 = complex(nz(-5, 5), nz(-5, 5))
    while True:
        w = complex(nz(-3, 3), nz(-3, 3))                # the quotient, whole
        d5 = complex(nz(-4, 4), nz(-4, 4))
        n5 = w * d5
        if max(abs(n5.real), abs(n5.imag)) <= 7:
            break
    kq = int(rng.integers(1, 6))
    return dict(
        q    = k * k,                                    # z^2 + q = 0
        z1   = z1,
        z2   = z2,
        n5   = n5,                                       # chapter 5: n5 / d5
        d5   = d5,
        zq   = (complex(-kq, -kq) if level == "gentle"     # 3rd quadrant, for the arctan trap
                else complex(*_T6_PYTH[kq - 1])),
        phi  = float(np.round(rng.uniform(0.3, 2.6), 3)),
    )

def _nz(lo, hi):
    """A non-zero integer in [lo, hi]."""
    v = 0
    while v == 0:
        v = int(_rng.integers(lo, hi + 1))
    return v

TV = _draw_tv(_rng)

# 2026-09-28 (R2 · Paket 13) — the ⚙ seed buttons draw again IN PLACE: TV is
# refilled (same dict, so every reader of TV sees the new numbers), and the
# chapters' on_reseed hooks recompute what they derived from it.
personal_draw(lambda seed: TV.update(_draw_tv(np.random.default_rng(seed))))

def zs(z, prec=0):
    """Format a complex number the way the script writes it: a + ib."""
    a, b = z.real, z.imag
    fa = ("%%.%df" % prec) % a if prec else "%d" % int(round(a))
    fb = ("%%.%df" % prec) % abs(b) if prec else "%d" % int(round(abs(b)))
    if abs(b) < 1e-12:
        return fa
    sign = "+" if b > 0 else "-"
    fb = "" if fb == "1" else fb
    return "%s %s %si" % (fa, sign, fb)

def _pn(x):
    """A whole number for a worked line: 3, or (−3) in brackets when negative
    (Inhalt 2026-09-27 — the hints write out the working with the reader's numbers)."""
    x = int(round(x))
    return "%d" % x if x >= 0 else "(−%d)" % -x

def _pni(x):
    """The same for an imaginary part: 3i, i, (−i), (−3i)."""
    x = int(round(x))
    m = "i" if abs(x) == 1 else "%di" % abs(x)
    return m if x >= 0 else "(−%s)" % m

# --- learning goals: declared ONCE, read by the Introduction, the OER record
# and the title card (Inhalt A, eingebaut R2 · 15). K-tag · level · what the
# reader can do. In the biophysics standard K2 ("implement it in Python") is
# deliberately absent: every exercise can be solved without code.
register_goals([
 ("K3", "basic", "state the definition i² = −1 and split any z ∈ ℂ into its real part Re(z) and imaginary part Im(z)"),
 ("K3", "basic", "locate a complex number in the Argand plane (the complex plane) and name its quadrant"),
 ("K4", "intermediate", "add, multiply and divide complex numbers, and describe what each operation does "
                        "to the arrow in the plane"),
 ("K3", "intermediate", "convert between z = a + ib and z = |z|e^{iφ}, including the quadrant "
                        "correction that plain arctan does not make"),
 ("K5", "advanced", "check a published worked solution against your own calculation and say "
                    "exactly where and why it differs"),
 ("K4", "advanced", "explain why an RC membrane model uses a complex impedance, and what "
                    "the modulus and the argument of that number mean physically"),
])

# --- the tasks, declared up front so the progress strip is complete --------
# (key, label, anchor of the chapter the exercise lives in — the panel at the top
#  links each node to it)
# The fourth field is the exercise's name on the timeline ("Exercise 3: Sum and
# difference" — Inhalt's list of 27.09. 15:55; K2.8, 2026-09-28b).
register_tasks([
    ("t1", "1 · roots",             "ch1",  "Imaginary roots"),
    ("t2", "2 · quadrant",          "ch2",  "Find the quadrant"),
    ("t3", "3 · add / subtract",    "ch3",  "Sum and difference"),
    ("t4", "4 · multiply",          "ch4",  "Multiply"),
    ("t5", "5 · divide",            "ch5",  "Divide via the conjugate"),
    ("t6", "6 · polar form",        "ch6",  "Polar form"),
    ("t7", "7 · rotate",            "ch7",  "Hit the target"),
    # E25.l (08.10.): q1 "8 · multiple choice" (quiz) and b1 "9 · own data"
    # (byod) are out for now; quiz.py / byod.py stay as sources
])

# --- quiz (jupyterquiz) ---------------------------------------------------
QUIZ = [
 {"question": "What is i² ?",
  "type": "multiple_choice",
  "answers": [
    {"answer": "−1", "correct": True,  "feedback": "Correct. This one definition generates everything else."},
    {"answer": "1",  "correct": False, "feedback": "That is i⁴."},
    {"answer": "i",  "correct": False, "feedback": "That is i¹."},
    {"answer": "0",  "correct": False, "feedback": "No, i is not zero."}]},
 {"question": "Where does the conjugate z̄ sit relative to z in the complex plane?",
  "type": "multiple_choice",
  "answers": [
    {"answer": "Mirrored across the real axis", "correct": True,
     "feedback": "Yes. a + ib becomes a − ib, so only the sign of the imaginary part flips."},
    {"answer": "Mirrored across the imaginary axis", "correct": False,
     "feedback": "That would be −a + ib, which is −z̄."},
    {"answer": "Rotated by 90°", "correct": False, "feedback": "Rotation by 90° is multiplication by i."},
    {"answer": "At the same place", "correct": False, "feedback": "Only when z is real."}]},
 {"question": "Multiplying two complex numbers in polar form means …",
  "type": "multiple_choice",
  "answers": [
    {"answer": "multiply the moduli, add the angles", "correct": True,
     "feedback": "Correct: |z₁||z₂| e^{i(φ₁+φ₂)}."},
    {"answer": "add the moduli, multiply the angles", "correct": False,
     "feedback": "The exponents add, so the angles add; the moduli multiply."},
    {"answer": "multiply both", "correct": False, "feedback": "Only the moduli multiply."},
    {"answer": "add both", "correct": False, "feedback": "Only the angles add."}]},
 {"question": "For z = −2 − 4i, plain arctan(b/a) gives an angle in which quadrant?",
  "type": "multiple_choice",
  "answers": [
    {"answer": "The first; it is off by π", "correct": True,
     "feedback": "Right. arctan only returns angles in (−π/2, π/2), so quadrants II and III need +π."},
    {"answer": "The third; it is already correct", "correct": False,
     "feedback": "No: b/a = 2 > 0, so arctan returns a first-quadrant angle."},
    {"answer": "The second", "correct": False, "feedback": "arctan never returns an angle beyond ±π/2."},
    {"answer": "The fourth", "correct": False, "feedback": "arctan(2) is positive, so not the fourth."}]},
 {"question": "Is there an order relation (z₁ < z₂) on ℂ?",
  "type": "multiple_choice",
  "answers": [
    {"answer": "No", "correct": True,
     "feedback": "Correct. Only the moduli |z₁| and |z₂| can be compared, not the numbers themselves."},
    {"answer": "Yes, by real part", "correct": False, "feedback": "That ignores the imaginary part entirely."},
    {"answer": "Yes, by modulus", "correct": False,
     "feedback": "|z| can be compared, but that compares two real numbers; it is not an order on ℂ."},
    {"answer": "Only for purely imaginary numbers", "correct": False, "feedback": "No order exists on ℂ at all."}]},
]

# --- bibliography ---------------------------------------------------------
BIB = {
 1: 'L. Heidinger, <i>Principles of Biophysics &amp; Computational methods</i>, '
    'Albert-Ludwigs-Universität Freiburg, WS 2025/26, section 1.2 “Complex numbers”, pp. 26–38.',
 2: 'T. Needham, <i>Visual Complex Analysis</i>, Oxford University Press, 1997. ISBN 978-0-19-853446-4.',
 3: 'L. V. Ahlfors, <i>Complex Analysis</i>, 3rd ed., McGraw-Hill, 1979. ISBN 978-0-07-000657-7.',
 4: 'K. F. Riley, M. P. Hobson, S. J. Bence, <i>Mathematical Methods for Physics and Engineering</i>, '
    '3rd ed., Cambridge University Press, 2006.',
 5: 'A. L. Hodgkin, A. F. Huxley, “A quantitative description of membrane current …”, '
    '<i>J. Physiol.</i> <b>117</b>, 500–544 (1952). '
    'DOI: <a href="https://doi.org/10.1113/jphysiol.1952.sp004764" target="_blank">10.1113/jphysiol.1952.sp004764</a>',
 6: 'L. J. Gentet, G. J. Stuart, J. D. Clements, “Direct measurement of specific membrane capacitance '
    'in neurons”, <i>Biophys. J.</i> <b>79</b>, 314–320 (2000). '
    'DOI: <a href="https://doi.org/10.1016/S0006-3495(00)76293-X" target="_blank">10.1016/S0006-3495(00)76293-X</a>',
 7: 'M. D. Wilkinson et al., “The FAIR Guiding Principles for scientific data management and stewardship”, '
    '<i>Sci. Data</i> <b>3</b>, 160018 (2016). '
    'DOI: <a href="https://doi.org/10.1038/sdata.2016.18" target="_blank">10.1038/sdata.2016.18</a>',
}

# the title page is the first bar on the timeline: the marker and the
# scrollbar start there, not a screen further down at the Introduction
notebook_start()
