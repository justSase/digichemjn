_intro = (
  "Two sets can be combined in four ways, and each one is a different question about "
  "membership" + cite(1) + ". The <b>intersection</b> asks <i>in both?</i>, the <b>union</b> asks "
  "<i>in either?</i>, the <b>difference</b> asks <i>in A but not in B?</i>, and the "
  "<b>complement</b> asks <i>not in A?</i> — which only makes sense once you have said what the "
  "surrounding set is.")

info = concept_box(_intro,
    r"$A \cap B = \{x \mid x \in A \wedge x \in B\} \qquad "
    r"A \cup B = \{x \mid x \in A \vee x \in B\}$",
    variables=[("A ∩ B", "intersection — the elements in both"),
               ("A ∪ B", "union — the elements in at least one"),
               ("M \\ A", "relative complement — in M but not in A"),
               ("Aᶜ", "absolute complement, Aᶜ = {x | x ∉ A} — everything outside A"),
               ("A ∩ B = ∅", "A and B are called disjoint")],
    extra_html=(
      "<div style='max-width:800px;margin:14px auto 0;text-align:justify;line-height:1.6'>"
      "The two logical operators in the formula are the whole definition: <b>∧</b> is "
      "<i>and</i>, <b>∨</b> is <i>or</i>. That is worth noticing rather than skipping, because "
      "it is the reason every rule in chapter 4 can be <i>proved</i> instead of memorised — a "
      "statement about sets is a statement about and/or, and those you already know.<br><br>"
      "One caution about ∨: in mathematics it is the <b>inclusive</b> or. "
      + imath(r"x \in A \vee x \in B") + " is true when x is in both, which is why "
      + imath(r"A \cap B") + " is part of " + imath(r"A \cup B") + " and not somehow excluded "
      "from it. Everyday German <i>oder</i> and English <i>or</i> often mean the exclusive one; "
      "the symbol never does.</div>"))


def _render_c02(shift=0.55, op=0):
    """Two discs; the answer to the chosen question is filled in."""
    fig, ax = fixed_canvas(figsize=(6.6, 3.7), left=.03, right=.99, top=.96, bottom=.03)
    ax.set_xlim(-1.9, 1.9); ax.set_ylim(-1.05, 1.05)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
    for sp in ax.spines.values():
        sp.set_visible(False)
    import matplotlib.path as mpath
    import matplotlib.patches as mpatches
    d = float(shift)
    r = 0.72
    op = int(op)
    # the surrounding set M
    ax.add_patch(mpatches.Rectangle((-1.82, -0.98), 3.64, 1.96, fill=False,
                                    ec=PLOT_INK, lw=1.2, ls=(0, (5, 4))))
    ax.text(-1.76, 0.86, "M", fontsize=12, color=PLOT_INK, fontweight="bold")
    th = np.linspace(0, 2 * np.pi, 400)
    ax_ = -d, 0.0
    bx_ = d, 0.0
    # what gets filled, drawn by clipping one disc against the other
    cA = mpatches.Circle(ax_, r, transform=ax.transData)
    cB = mpatches.Circle(bx_, r, transform=ax.transData)
    fillc = PAL["sum"]
    if op == 0:                                   # A ∩ B
        p = mpatches.Circle(ax_, r, color=fillc, alpha=.55, lw=0)
        ax.add_patch(p); p.set_clip_path(cB)
    elif op == 1:                                 # A ∪ B
        for c in (ax_, bx_):
            ax.add_patch(mpatches.Circle(c, r, color=fillc, alpha=.45, lw=0))
    elif op == 2:                                 # A \ B
        p = mpatches.Circle(ax_, r, color=fillc, alpha=.55, lw=0)
        ax.add_patch(p)
        ax.add_patch(mpatches.Circle(bx_, r, color="white", alpha=1.0, lw=0, zorder=2))
    else:                                         # Aᶜ  (inside M, outside A)
        ax.add_patch(mpatches.Rectangle((-1.82, -0.98), 3.64, 1.96,
                                        color=fillc, alpha=.35, lw=0))
        ax.add_patch(mpatches.Circle(ax_, r, color="white", alpha=1.0, lw=0, zorder=2))
    # the outlines always on top, so the two sets stay readable whatever is filled
    ax.plot(ax_[0] + r * np.cos(th), r * np.sin(th), color=PAL["z2"], lw=2.0, zorder=3)
    ax.plot(bx_[0] + r * np.cos(th), r * np.sin(th), color=PAL["z"], lw=2.0, zorder=3)
    ax.text(ax_[0] - 0.42, 0.52, "A", fontsize=13, color=PAL["z2"], fontweight="bold", zorder=4)
    ax.text(bx_[0] + 0.30, 0.52, "B", fontsize=13, color=PAL["z"], fontweight="bold", zorder=4)
    return fig


_OPNAME = ["A ∩ B", "A ∪ B", "A \\ B", "Aᶜ"]
_OPSAY = ["in both", "in at least one", "in A but not in B", "everything in M outside A"]


def _read_c02(shift=0.55, op=0):
    op = int(op)
    d = float(shift)
    disj = "yes — A ∩ B = ∅" if d >= 0.72 else "no"
    return readout([("filled", _OPNAME[op]),
                    ("means", _OPSAY[op]),
                    ("disjoint?", disj),
                    ("overlap", "%.0f %%" % (max(0.0, 1 - d / 0.72) * 100))])


viz = [viz_intro_box("",
    "Pick the operation, then pull the two sets apart. Two things are worth watching. The "
    "<b>union</b> never loses the overlap — that is the inclusive <i>or</i> from the box above. "
    "And once the discs separate completely the intersection is <b>∅</b>, which is the definition "
    "of <i>disjoint</i>: not 'barely touching', but sharing nothing at all.")]
viz += slider_plot(_render_c02,
                   {"op": IntSlider(value=0, min=0, max=3, step=1, description="operation"),
                    "shift": FloatSlider(value=0.55, min=0.0, max=0.95, step=0.05,
                                         description="apart")},
                   readout_fn=_read_c02)

_A, _B, _M = TV["A"], TV["B"], TV["M"]
_inter = sorted(set(_A) & set(_B))
_union = sorted(set(_A) | set(_B))
_diff = sorted(set(_A) - set(_B))

practice = [
  exercise_box("", taskline("<b>Your personal sets are A = " + setstr(_A)
               + " and B = " + setstr(_B) + ", inside M = " + setstr(_M) + ".</b>")
      + "<div>Work out three counts — not the sets themselves, just how many elements each one "
        "has:</div>"
      + "<div style='margin-top:8px'><b>#(A ∩ B)</b>, <b>#(A ∪ B)</b> and <b>#(A \\ B)</b>.</div>"
      + "<div style='margin-top:10px'>A check worth doing before you press the button: "
        + imath(r"\#\,(A\cup B) = \# A + \# B - \#\,(A\cap B)") + ". The subtraction is there because "
        "the shared elements would otherwise be counted twice — a set has each element once, "
        "however many of the original sets it came from.</div>"),
  numeric_answer([("inter", "#(A ∩ B) ="), ("union", "#(A ∪ B) ="), ("diff", "#(A \\ B) =")],
                 lambda v: _ans_t2(v), task="t2", columns=3),
  code_fold("def counts(A, B):\n"
            "    # return (#(A and B), #(A or B), #(A without B)) for the two lists\n"
            "    return (..., ..., ...)\n",
            lambda g: _check_t2(g), task="t2", locked_by="t1",
            solution="def counts(A, B):\n"
                     "    A, B = set(A), set(B)\n"
                     "    return (len(A & B), len(A | B), len(A - B))\n"),
]


def _ans_t2(v):
    want = {"inter": len(_inter), "union": len(_union), "diff": len(_diff)}
    for k, lab in (("inter", "#(A ∩ B)"), ("union", "#(A ∪ B)"), ("diff", "#(A \\ B)")):
        if abs(v[k] - want[k]) > tol() * max(1, want[k]):
            if k == "union" and abs(v[k] - (len(_A) + len(_B))) < 0.5:
                return False, ("That is #A + #B, which counts the %d shared element(s) twice. "
                               "Subtract #(A ∩ B) once." % len(_inter))
            if k == "diff" and abs(v[k] - len(set(_B) - set(_A))) < 0.5:
                return False, "That is B \\ A. The order matters: A \\ B keeps A's own elements."
            if k == "inter":
                return False, "Go through A element by element and keep only those also in B."
            return False, "%s is not right yet — count the elements one at a time." % lab
    return True, ("Correct: %d in both, %d in the union, %d in A alone — and %d + %d − %d = %d "
                  "checks out." % (len(_inter), len(_union), len(_diff),
                                   len(_A), len(_B), len(_inter), len(_union)))


def _check_t2(g):
    f = g.get("counts")
    if not callable(f):
        return False, "Define a function called counts(A, B) that returns a tuple."
    trials = [(_A, _B), ([1, 2, 3], [3, 4]), ([1, 2], [1, 2]), ([1, 2], [5, 6]), ([], [1])]
    for A, B in trials:
        try:
            out = f(list(A), list(B))
        except Exception as e:
            return False, "counts(%r, %r) raised %r." % (A, B, e)
        if not isinstance(out, (tuple, list)) or len(out) != 3:
            return False, "Return exactly three values."
        sA, sB = set(A), set(B)
        want = (len(sA & sB), len(sA | sB), len(sA - sB))
        if tuple(int(x) for x in out) != want:
            return False, ("For A=%r, B=%r the answer is %r — check the disjoint and the "
                           "identical case too." % (A, B, want))
    return True, "Correct on the overlapping, identical, disjoint and empty cases."


interp = interpretation_box(
  "The subtraction in " + imath(r"\#\,(A\cup B)=\# A+\# B-\#\,(A\cap B)") + " is the first appearance "
  "of a habit that runs through the whole of the statistics later in this course: <b>count, then "
  "remove what you counted twice</b>. It is the same correction that turns 'probability of A or "
  "B' into " + imath("P(A)+P(B)-P(A\\cap B)") + ", and the reason the naive sum is right only "
  "when the two things cannot happen together — when they are disjoint.")

build_chapter(2, "Intersection, union, difference, complement",
              info=info, viz=viz, practice=practice, interp=interp, locked_by="t1", task="t2")
