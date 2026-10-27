_intro = (
  "A <b>set</b> is an amount of elements — nothing more" + cite(1) + ". What makes the idea "
  "useful is that it says nothing about what the elements <i>are</i>: the six faces of a die, "
  "the twenty natural amino acids, the names of everyone in a city and the real numbers are all "
  "sets, and every rule in this notebook applies to all of them equally. The only question a set "
  "answers is <b>is this thing in it, yes or no</b>.")

info = concept_box(_intro, r"$M = \{\,\text{the elements of } M\,\} \qquad x \in M \;\text{ or }\; x \notin M$",
    variables=[("M", "a set"),
               ("x ∈ M", "x is an element (a member) of M"),
               ("x ∉ M", "x is not an element of M"),
               ("∅", "the empty set — the set with no elements at all")],
    extra_html=(
      "<div style='max-width:800px;margin:14px auto 0;text-align:justify;line-height:1.6'>"
      "Sets come in three sizes, and the difference matters later in the course:<br><br>"
      "<b>Finite</b> — you can count the elements and stop. The faces of a die, "
      + imath(r"M=\{1,2,3,4,5,6\}") + ".<br>"
      "<b>Infinite and countable</b> — you cannot stop, but you can put the elements in a list "
      "so that every one of them is reached eventually. The natural numbers, "
      + imath(r"\mathbb{N}=\{1,2,3,4,\dots\}") + ".<br>"
      "<b>Infinite and uncountable</b> — no such list exists, however clever. The real numbers "
      + imath(r"\mathbb{R}") + ".<br><br>"
      "Note the third one is a genuinely stronger statement than the second, not just a bigger "
      "number: between any two real numbers there are more reals than there are natural numbers "
      "altogether.</div>"))


def _render_c01(n=6):
    """A set as a bag of dots: the picture that says 'membership, nothing else'."""
    fig, ax = fixed_canvas(figsize=(6.4, 3.6), left=.04, right=.98, top=.95, bottom=.06)
    ax.set_xlim(-1.35, 1.35); ax.set_ylim(-0.85, 0.85)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
    for sp in ax.spines.values():
        sp.set_visible(False)
    th = np.linspace(0, 2 * np.pi, 220)
    ax.plot(0.95 * np.cos(th) - 0.15, 0.62 * np.sin(th), color=PAL["z2"], lw=2.0)
    n = int(n)
    # elements inside, on a ring so they never collide however many there are
    ang = np.linspace(0.2, 2 * np.pi + 0.2, n, endpoint=False)
    rr = 0.44 if n > 3 else 0.0
    ax.plot(rr * np.cos(ang) - 0.15, 0.30 * np.sin(ang), "o",
            color=PAL["sum"], ms=11, zorder=3)
    for i, (x, y) in enumerate(zip(rr * np.cos(ang) - 0.15, 0.30 * np.sin(ang))):
        ax.text(x, y, str(i + 1), ha="center", va="center", fontsize=8,
                color="white", zorder=4, fontweight="bold")
    # one element that is NOT in the set
    ax.plot([1.08], [0.42], "o", color=PAL["z"], ms=11, zorder=3)
    ax.text(1.08, 0.42, "x", ha="center", va="center", fontsize=8,
            color="white", zorder=4, fontweight="bold")
    ax.text(1.08, 0.62, "x ∉ M", ha="center", va="bottom", fontsize=10, color=PLOT_INK)
    ax.text(-0.15, 0.66, "M", ha="center", va="bottom", fontsize=13, color=PAL["z2"],
            fontweight="bold")
    return fig


def _read_c01(n=6):
    n = int(n)
    return readout([("# M", str(n)),
                    ("kind", "finite"),
                    ("is x in M?", "no — x ∉ M"),
                    ("subsets of M", str(2 ** n))])


viz = [viz_intro_box("",
    "A set is a <b>boundary</b> and nothing else: the dots inside are its elements, the red dot "
    "outside is not. Drag the number of elements and watch what the picture does <i>not</i> "
    "change — the order of the dots, their spacing, what they stand for. None of that is part of "
    "the set. The readout counts the subsets, which is the number that grows alarmingly fast.")]
viz += slider_plot(_render_c01,
                   {"n": IntSlider(value=6, min=1, max=12, step=1, description="# M")},
                   readout_fn=_read_c01)

_A = TV["A"]
practice = [
  exercise_box("", taskline("<b>Your personal set is A = " + setstr(_A) + ".</b>")
      + "<div>Answer two questions about it. <b>How many elements</b> does A have — that is "
        "written <b>#A</b> (some books write |A|). And <b>how many different subsets</b> does A "
        "have, counting the empty set ∅ and A itself?</div>"
      + "<div style='margin-top:10px'>The second one is the interesting question. A subset is "
        "made by going through the elements one at a time and deciding, for each one "
        "independently, in or out.</div>"),
  numeric_answer([("card", "#A ="), ("subs", "number of subsets =")],
                 lambda v: _ans_t1(v), task="t1"),
  code_fold("def about(A):\n"
            "    # return (number of elements, number of subsets) for the list A\n"
            "    n = ...\n"
            "    return (..., ...)\n",
            lambda g: _check_t1(g), task="t1",
            solution="def about(A):\n"
                     "    n = len(set(A))     # a set has no repeats\n"
                     "    return (n, 2 ** n)  # two choices, in or out, per element\n"),
]


def _ans_t1(v):
    n = len(_A)
    if abs(v["card"] - n) > tol() * max(1, n):
        return False, ("#A is the number of elements you can count in " + setstr(_A) + ".")
    want = 2.0 ** n
    if abs(v["subs"] - want) > tol() * max(1, want):
        if abs(v["subs"] - (2 ** n - 1)) < 0.5:
            return False, ("Close — but ∅ counts as a subset too, so nothing is subtracted.")
        if abs(v["subs"] - n) < 0.5:
            return False, ("That is the number of elements, not of subsets. Each element is "
                           "decided independently: in or out.")
        return False, ("Each of the %d elements is independently in or out, so the count is a "
                       "power of two." % n)
    return True, "Correct: #A = %d and 2^%d = %d subsets." % (n, n, 2 ** n)


def _check_t1(g):
    f = g.get("about")
    if not callable(f):
        return False, "Define a function called about(A) that returns a tuple."
    for trial in ([1, 2, 3], _A, [5, 5, 7], []):
        try:
            out = f(list(trial))
        except Exception as e:
            return False, "about(%r) raised %r." % (trial, e)
        if not isinstance(out, (tuple, list)) or len(out) != 2:
            return False, "Return exactly two values: (count, subsets)."
        n = len(set(trial))
        if int(out[0]) != n:
            return False, ("For %r the count should be %d — a set has no repeated elements."
                           % (trial, n))
        if int(out[1]) != 2 ** n:
            return False, "The number of subsets of an n-element set is 2ⁿ."
    return True, "Correct, including the repeated element and the empty list."


interp = interpretation_box(
  "Everything in this notebook rests on the one question a set answers: <b>in, or not in</b>. "
  "That is why the same rules serve for dice faces, amino acids and the real numbers — none of "
  "the rules ever look at what the elements are. The subset count is the first sign of how fast "
  "this gets big: twenty amino acids give 2²⁰ ≈ a million possible subsets, which is why "
  "counting arguments, not lists, are what you will reach for later in the course.")

build_chapter(1, "What a set is", info=info, viz=viz, practice=practice, interp=interp,
              task="t1", chapter_open=True)
