_intro = (
  "The set operations obey rules that look like the rules of arithmetic, and one pair that does "
  "not" + cite(1) + ". ∩ and ∪ are both <b>commutative</b> and <b>associative</b>, like + and ·. "
  "They are also <b>distributive</b> — but unlike arithmetic, in <i>both</i> directions. The "
  "pair worth learning properly is <b>De Morgan</b>: a complement turns ∪ into ∩ and back.")

info = concept_box(_intro,
    r"$(A\cup B)^C = A^C \cap B^C \qquad (A\cap B)^C = A^C \cup B^C$",
    variables=[("commutative", "A ∪ B = B ∪ A,  A ∩ B = B ∩ A"),
               ("associative", "(A ∪ B) ∪ C = A ∪ (B ∪ C)"),
               ("distributive", "A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C)"),
               ("De Morgan", "a complement swaps ∪ and ∩")],
    extra_html=(
      "<div style='max-width:800px;margin:14px auto 0;text-align:justify;line-height:1.6'>"
      "Read De Morgan in words and it stops being a formula to memorise: <i>not (in A or in B)</i> "
      "means <i>not in A, and also not in B</i>. Said aloud it is obvious; written in symbols it "
      "is the rule that people most often get backwards, because they carry the complement "
      "inwards and leave the ∪ alone.<br><br>"
      "A few more that fall out immediately: " + imath(r"A\cap M = A") + ", "
      + imath(r"A\cup\emptyset = A") + ", " + imath(r"A\cup A^C = M") + " and "
      + imath(r"A\cap A^C = \emptyset") + ". Each of them is worth reading as a sentence rather "
      "than a formula.<br><br>"
      "And the reason all of this can be <i>proved</i> rather than believed: "
      + imath(r"A\cap B=\{x\mid x\in A \wedge x\in B\}") + ". A statement about sets is a "
      "statement about <b>and</b>/<b>or</b>, so the rules above are the rules of logic wearing "
      "different symbols.</div>"))


def _render_c04(which=0, step=0):
    """De Morgan, left side against right side, filled the same way."""
    import matplotlib.patches as mpatches
    which, step = int(which), int(step)
    fig, ax = fixed_canvas(figsize=(6.8, 3.7), left=.02, right=.99, top=.99, bottom=.02)
    ax.set_xlim(-1.95, 1.95); ax.set_ylim(-1.1, 1.1)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
    for sp in ax.spines.values():
        sp.set_visible(False)
    r, d = 0.70, 0.46
    A, B = (-d, 0.0), (d, 0.0)
    th = np.linspace(0, 2 * np.pi, 400)
    ax.add_patch(mpatches.Rectangle((-1.88, -1.02), 3.76, 2.04, fill=False,
                                    ec=PLOT_INK, lw=1.2, ls=(0, (5, 4))))
    ax.text(-1.82, 0.90, "M", fontsize=12, color=PLOT_INK, fontweight="bold")
    fillc = PAL["sum"]
    cA = mpatches.Circle(A, r, transform=ax.transData)
    cB = mpatches.Circle(B, r, transform=ax.transData)
    if which == 0:      # (A ∪ B)ᶜ  built in two steps
        if step == 0:                       # A ∪ B
            for c in (A, B):
                ax.add_patch(mpatches.Circle(c, r, color=PAL["aux"], alpha=.45, lw=0))
        else:                               # its complement
            ax.add_patch(mpatches.Rectangle((-1.88, -1.02), 3.76, 2.04,
                                            color=fillc, alpha=.38, lw=0))
            for c in (A, B):
                ax.add_patch(mpatches.Circle(c, r, color="white", alpha=1.0, lw=0, zorder=2))
    else:               # Aᶜ ∩ Bᶜ  built in two steps
        if step == 0:                       # Aᶜ
            ax.add_patch(mpatches.Rectangle((-1.88, -1.02), 3.76, 2.04,
                                            color=PAL["aux"], alpha=.38, lw=0))
            ax.add_patch(mpatches.Circle(A, r, color="white", alpha=1.0, lw=0, zorder=2))
        else:                               # Aᶜ ∩ Bᶜ
            ax.add_patch(mpatches.Rectangle((-1.88, -1.02), 3.76, 2.04,
                                            color=fillc, alpha=.38, lw=0))
            for c in (A, B):
                ax.add_patch(mpatches.Circle(c, r, color="white", alpha=1.0, lw=0, zorder=2))
    ax.plot(A[0] + r * np.cos(th), r * np.sin(th), color=PAL["z2"], lw=2.0, zorder=3)
    ax.plot(B[0] + r * np.cos(th), r * np.sin(th), color=PAL["z"], lw=2.0, zorder=3)
    ax.text(A[0] - 0.44, 0.50, "A", fontsize=13, color=PAL["z2"], fontweight="bold", zorder=4)
    ax.text(B[0] + 0.32, 0.50, "B", fontsize=13, color=PAL["z"], fontweight="bold", zorder=4)
    return fig


_SIDE = [["A ∪ B", "(A ∪ B)ᶜ"], ["Aᶜ", "Aᶜ ∩ Bᶜ"]]


def _read_c04(which=0, step=0):
    which, step = int(which), int(step)
    same = "yes — the same region" if step == 1 else "keep going"
    return readout([("side", "left" if which == 0 else "right"),
                    ("showing", _SIDE[which][step]),
                    ("final region", "(A ∪ B)ᶜ" if which == 0 else "Aᶜ ∩ Bᶜ"),
                    ("equal?", same)])


viz = [viz_intro_box("",
    "De Morgan in two moves per side. Set <b>side</b> to the left and step through: first "
    + imath(r"A\cup B") + ", then everything outside it. Now switch to the right side and step "
    "through " + imath("A^C") + " and then " + imath(r"A^C\cap B^C") + ". At step 1 both sides "
    "fill <b>exactly the same region</b> — that is the proof, and it is worth doing with your "
    "own eyes rather than taking the formula on trust.")]
viz += slider_plot(_render_c04,
                   {"which": IntSlider(value=0, min=0, max=1, step=1, description="side"),
                    "step": IntSlider(value=0, min=0, max=1, step=1, description="step")},
                   readout_fn=_read_c04)

_A, _B, _M = TV["A"], TV["B"], TV["M"]
_lhs = sorted(set(_M) - (set(_A) | set(_B)))
_wrong = sorted(set(_M) - (set(_A) & set(_B)))

practice = [
  exercise_box("", taskline("<b>With M = " + setstr(_M) + ", A = " + setstr(_A)
               + " and B = " + setstr(_B) + ", how many elements are in "
               + imath(r"(A\cup B)^C") + "?</b>")
      + "<div>You can work it out either way round — that is the point of the rule. Build "
        + imath(r"A\cup B") + " and count what is left over in M, or build "
        + imath("A^C") + " and " + imath("B^C") + " separately and intersect them. Both must "
        "give the same number.</div>"
      + "<div style='margin-top:10px'>Then answer the second question: is "
        + imath(r"(A\cap B)^C") + " the same set? Enter <b>1</b> for yes, <b>0</b> for no.</div>"),
  numeric_answer([("n", "#(A ∪ B)ᶜ ="), ("same", "is (A ∩ B)ᶜ the same set? 1 / 0 =")],
                 lambda v: _ans_t4(v), task="t4"),
  code_fold("def de_morgan(M, A, B):\n"
            "    # return (#(A or B)^C, True/False: is (A and B)^C the same set?)\n"
            "    return (..., ...)\n",
            lambda g: _check_t4(g), task="t4", locked_by="t3",
            solution="def de_morgan(M, A, B):\n"
                     "    M, A, B = set(M), set(A), set(B)\n"
                     "    left  = M - (A | B)          # (A u B)^C\n"
                     "    other = M - (A & B)          # (A n B)^C = A^C u B^C\n"
                     "    return (len(left), left == other)\n"),
]


def _ans_t4(v):
    want = len(_lhs)
    if abs(v["n"] - want) > tol() * max(1, want):
        if abs(v["n"] - len(_wrong)) < 0.5:
            return False, ("That is #(A ∩ B)ᶜ. The complement swaps the operator: (A ∪ B)ᶜ is "
                           "Aᶜ ∩ Bᶜ — outside <i>both</i>.")
        if abs(v["n"] - len(set(_A) | set(_B))) < 0.5:
            return False, "That is #(A ∪ B) itself. The complement is what is left in M."
        return False, ("Count the elements of M that are in neither A nor B. There are %d "
                       "elements in M altogether." % len(_M))
    same = (set(_lhs) == set(_wrong))
    if abs(v["same"] - (1.0 if same else 0.0)) > 0.4:
        return False, ("Compare the two sets element by element — De Morgan says (A ∩ B)ᶜ is "
                       "Aᶜ ∪ Bᶜ, which is a <i>larger</i> region whenever A ∩ B ≠ ∅.")
    return True, ("Correct: #(A ∪ B)ᶜ = %d, and the two complements %s."
                  % (want, "do coincide here" if same else "are different sets"))


def _check_t4(g):
    f = g.get("de_morgan")
    if not callable(f):
        return False, "Define a function called de_morgan(M, A, B)."
    trials = [(_M, _A, _B), (range(1, 7), [1, 2], [2, 3]), (range(1, 5), [1], [1]),
              (range(1, 5), [1, 2], [3, 4])]
    for M, A, B in trials:
        try:
            out = f(list(M), list(A), list(B))
        except Exception as e:
            return False, "de_morgan raised %r." % (e,)
        if not isinstance(out, (tuple, list)) or len(out) != 2:
            return False, "Return exactly two values: (count, same?)."
        sM, sA, sB = set(M), set(A), set(B)
        left, other = sM - (sA | sB), sM - (sA & sB)
        if int(out[0]) != len(left) or bool(out[1]) != (left == other):
            return False, ("For M=%r, A=%r, B=%r the answer is (%d, %s)."
                           % (list(M), A, B, len(left), left == other))
    return True, "Correct, including the disjoint case and A = B."


interp = interpretation_box(
  "De Morgan is the rule you will use without noticing, every time a condition is negated. "
  "A filter that keeps everything <i>except</i> the samples that are noisy <b>or</b> unlabelled "
  "keeps the samples that are clean <b>and</b> labelled — one <i>or</i> became an <i>and</i>, and "
  "getting that backwards is one of the most common silent bugs in data selection. The picture "
  "above is worth keeping: it is the same region, reached from two sides.")

build_chapter(4, "The rules, and De Morgan",
              info=info, viz=viz, practice=practice, interp=interp, locked_by="t3", task="t4")
