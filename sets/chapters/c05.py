_intro = (
  "Four sets carry the whole course, and each one exists because the previous one ran out of "
  "answers" + cite(1) + ". ℕ counts. ℤ adds subtraction — every element gets an inverse, so "
  "3 + (−3) = 0. ℚ adds division, so 2 · ½ = 1. And ℝ closes the gaps ℚ still leaves: "
  + imath(r"\sqrt{2}") + ", e and π are not fractions.")

info = concept_box(_intro,
    r"$\mathbb{N}\subset\mathbb{Z}\subset\mathbb{Q}\subset\mathbb{R}$",
    variables=[("ℕ", "natural numbers {1, 2, 3, …}; ℕ₀ includes 0"),
               ("ℤ", "integers {…, −2, −1, 0, 1, 2, …} — addition has inverses"),
               ("ℚ", "rationals {p/q | p, q ∈ ℤ} — multiplication has inverses"),
               ("ℝ", "reals — every Cauchy sequence converges; no gaps left")],
    extra_html=(
      "<div style='max-width:800px;margin:14px auto 0;text-align:justify;line-height:1.6'>"
      "All four have an <b>order relation</b>: given two of them you can always say which is "
      "smaller. What each step adds is an <i>operation</i>, not more numbers for their own sake. "
      "The script's word for the last step is worth keeping: ℝ is defined so that every Cauchy "
      "sequence converges — the gaps where a sequence obviously heads somewhere but that "
      "somewhere is not in the set are filled in.<br><br>"
      "<b>Intervals are sets too</b>, and the bracket is the entire difference:<br>"
      + imath(r"(a,b)=\{x\in\mathbb{R}\mid a<x<b\}") + " open — neither end belongs<br>"
      + imath(r"[a,b)=\{x\in\mathbb{R}\mid a\leq x<b\}") + " half-open<br>"
      + imath(r"(a,b]=\{x\in\mathbb{R}\mid a<x\leq b\}") + " half-open<br>"
      + imath(r"[a,b]=\{x\in\mathbb{R}\mid a\leq x\leq b\}") + " compact — both ends belong<br><br>"
      "Restrictions are written the same way: " + imath(r"\mathbb{R}^+=\{x\in\mathbb{R}\mid x\geq0\}")
      + ". A concentration lives in " + imath(r"\mathbb{R}^+") + ", not in " + imath(r"\mathbb{R}")
      + ", and saying so is a modelling decision, not pedantry.</div>"))


def _render_c05(zoom=1.0, kind=0):
    """The number line, and what each set actually occupies on it."""
    kind = int(kind)
    fig, ax = fixed_canvas(figsize=(6.8, 3.3), left=.06, right=.97, top=.94, bottom=.20)
    ax.set_xlim(-4.4, 4.4); ax.set_ylim(-1.15, 1.15)
    ax.set_yticks([]); ax.set_xticks(range(-4, 5))
    theme_axes(ax, grid=False)
    ax.axhline(0, color=PLOT_INK, lw=1.2)
    z = float(zoom)
    if kind == 0:                       # N
        pts = np.arange(1, 5)
        ax.plot(pts, np.zeros_like(pts, dtype=float), "o", color=PAL["sum"], ms=10, zorder=3)
        lab = "ℕ = {1, 2, 3, …}"
    elif kind == 1:                     # Z
        pts = np.arange(-4, 5)
        ax.plot(pts, np.zeros_like(pts, dtype=float), "o", color=PAL["sum"], ms=10, zorder=3)
        lab = "ℤ — the negatives arrive"
    elif kind == 2:                     # Q, denser as you zoom
        n = int(4 + 34 * z)
        pts = np.unique(np.concatenate([np.arange(-4, 5)] +
                                       [np.arange(-4 * k, 4 * k + 1) / k
                                        for k in range(1, n)]))
        ax.plot(pts, np.zeros_like(pts), "o", color=PAL["sum"], ms=4.5, alpha=.85, zorder=3)
        lab = "ℚ — dense, but still full of holes"
    else:                               # R
        ax.plot([-4.3, 4.3], [0, 0], "-", color=PAL["sum"], lw=7, alpha=.65,
                solid_capstyle="butt", zorder=2)
        lab = "ℝ — no gaps left"
    # √2 and π are the witnesses: in R, never in Q
    for x, nm in ((np.sqrt(2), "√2"), (np.pi, "π")):
        ax.plot([x], [0], "v", color=PAL["z"], ms=9, zorder=4)
        ax.text(x, 0.16, nm, ha="center", fontsize=10, color=PAL["z"])
    ax.text(0, -0.72, lab, ha="center", fontsize=12, color=PLOT_INK, fontweight="bold")
    return fig


def _read_c05(zoom=1.0, kind=0):
    kind = int(kind)
    rows = [("showing", ["ℕ", "ℤ", "ℚ", "ℝ"][kind]),
            ("adds", ["counting", "subtraction", "division", "no gaps"][kind]),
            ("is √2 in it?", "yes" if kind == 3 else "no"),
            ("countable?", "yes" if kind < 3 else "no — uncountable")]
    return readout(rows)


viz = [viz_intro_box("",
    "Step through the four sets. ℚ is the one to linger on: turn the <b>zoom</b> up and the "
    "points crowd together until the line looks solid — yet <b>√2 and π are never among them</b>, "
    "however far you go. That is the difference between <i>dense</i> and <i>complete</i>, and it "
    "is precisely the gap ℝ is defined to fill.")]
viz += slider_plot(_render_c05,
                   {"kind": IntSlider(value=0, min=0, max=3, step=1, description="set"),
                    "zoom": FloatSlider(value=1.0, min=0.0, max=1.0, step=0.05,
                                        description="density")},
                   readout_fn=_read_c05)

_CH = [
  ("−7",              "Z"),
  ("3/4",             "Q"),
  ("√2",              "R"),
  ("0",               "Z"),
  ("π",               "R"),
  ("12",              "N"),
]
_pick_i = int(_rng.integers(0, len(_CH)))
_val, _home = _CH[_pick_i]
_OPTS = ["ℕ — the natural numbers",
         "ℤ but not ℕ — an integer that does not count things",
         "ℚ but not ℤ — a genuine fraction",
         "ℝ but not ℚ — irrational"]
_WANT = {"N": 0, "Z": 1, "Q": 2, "R": 3}[_home]

practice = [
  exercise_box("", taskline("<b>Where does " + imath(_val.replace("√2", r"\sqrt{2}")
               .replace("π", r"\pi")) + " first appear?</b>")
      + "<div>Every one of these numbers is in ℝ — the question is the <i>smallest</i> of the "
        "four sets that already contains it. Pick the step at which it arrives.</div>"),
  choice_answer("", _OPTS, lambda i, lab: _ans_t5(i, lab), task="t5"),
  code_fold("from fractions import Fraction\n\n"
            "def smallest_home(x):\n"
            "    # x is a Fraction or a float; return one of 'N', 'Z', 'Q', 'R'\n"
            "    return ...\n",
            lambda g: _check_t5(g), task="t5", locked_by="t4",
            solution="from fractions import Fraction\n\n"
                     "def smallest_home(x):\n"
                     "    if isinstance(x, Fraction):\n"
                     "        if x.denominator != 1:\n"
                     "            return 'Q'\n"
                     "        return 'N' if x.numerator >= 1 else 'Z'\n"
                     "    # a float that is not a whole number cannot be told from a\n"
                     "    # rational by inspection, so the irrationals come in as floats\n"
                     "    return 'R' if x != int(x) else ('N' if x >= 1 else 'Z')\n"),
]


def _ans_t5(i, lab):
    if i == _WANT:
        why = {"N": "it counts, so ℕ already has it",
               "Z": "ℕ has no negatives and (by the script's convention) no 0",
               "Q": "it is a ratio of integers but not a whole number",
               "R": "it is not a ratio of integers at all"}[_home]
        return True, "Correct — %s." % why
    if _home == "R" and i == 2:
        return False, ("Not quite: it is not a fraction. No pair of integers p, q gives it, "
                       "which is exactly what makes it irrational.")
    if _home == "Z" and i == 0:
        return False, ("ℕ = {1, 2, 3, …} in this script — no negatives, and 0 only in ℕ₀.")
    if _home == "Q" and i == 1:
        return False, "ℤ holds whole numbers only; this one has a denominator."
    return False, "Work up from ℕ and stop at the first set that already contains it."


def _check_t5(g):
    f = g.get("smallest_home")
    if not callable(f):
        return False, "Define a function called smallest_home(x)."
    from fractions import Fraction as _F
    cases = [(_F(12), "N"), (_F(-7), "Z"), (_F(3, 4), "Q"),
             (float(np.sqrt(2)), "R"), (float(np.pi), "R"), (_F(0), "Z")]
    for x, want in cases:
        try:
            got = f(x)
        except Exception as e:
            return False, "smallest_home(%r) raised %r." % (x, e)
        if str(got).upper() != want:
            return False, "smallest_home(%r) should be %r, got %r." % (x, want, got)
    return True, "Correct on all six, including 0 and the two irrationals."


interp = interpretation_box(
  "Naming the set a quantity lives in is a modelling statement, and it is the cheapest error "
  "check you have. A particle count is in ℕ, so a fitted value of 3.4 means the model is wrong "
  "or the fit is. A concentration is in " + imath(r"\mathbb{R}^+") + ", so a negative result is "
  "not a small number, it is a signal. And the bracket in an interval decides whether an "
  "endpoint is allowed at all — which is the difference between a constraint you can reach and "
  "one you can only approach.")

build_chapter(5, "ℕ, ℤ, ℚ, ℝ — and intervals",
              info=info, viz=viz, practice=practice, interp=interp, locked_by="t4", task="t5")
