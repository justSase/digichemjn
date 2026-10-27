_intro = (
  "The binomial coefficient answers one question: <b>how many ways can k things be chosen from "
  "n, when the order of choosing does not matter?</b>" + cite(1) + " It is the last piece of "
  "notation in this section and the one that does the most work later, because almost every "
  "counting argument in statistics reduces to it.")

info = concept_box(_intro,
    r"$\binom{n}{k}=\frac{n!}{(n-k)!\,k!}\qquad (a+b)^n=\sum_{j=0}^{n}\binom{n}{j}a^j b^{n-j}$",
    variables=[("n", "how many there are to choose from"),
               ("k", "how many are chosen"),
               ("n!/(n−k)!", "the ordered count — n · (n−1) · … · (n−k+1)"),
               ("k!", "the number of orders of the k chosen things — divided out")],
    extra_html=(
      "<div style='max-width:800px;margin:14px auto 0;text-align:justify;line-height:1.6'>"
      "The script's lottery example is the clearest way in. Six numbers from 49: there are 49 "
      "choices for the first, 48 for the second, and so on down to 44 — "
      + imath(r"49\cdot48\cdot47\cdot46\cdot45\cdot44") + ". But a ticket does not care in "
      "which order you wrote them, and those same six numbers could have been written in "
      + imath("6! = 720") + " orders. So divide:<br><br>"
      + imath(r"\binom{49}{6}=\frac{49\cdot48\cdot47\cdot46\cdot45\cdot44}{6\cdot5\cdot4\cdot3\cdot2\cdot1}=13\,983\,816")
      + "<br><br>That division by k! <i>is</i> the difference between this chapter and chapter 3. "
      "A Cartesian product is ordered and multiplies; a choice is unordered and therefore "
      "divides by the number of orders. Everything else follows.<br><br>"
      "The second formula is the same coefficient wearing different clothes. Expanding "
      + imath("(a+b)^n") + " means picking, from each of the n brackets, either a or b; the "
      "term " + imath("a^j b^{n-j}") + " appears exactly as often as there are ways of choosing "
      "which j brackets contributed the a — which is " + imath(r"\binom{n}{j}") + ".</div>"))


def _render_c07(n=6, k=3):
    """Pascal's triangle: the coefficients, with the chosen one marked."""
    from math import comb
    n, k = int(n), int(k)
    k = min(k, n)
    fig, ax = fixed_canvas(figsize=(6.8, 4.1), left=.03, right=.99, top=.97, bottom=.03)
    N = 10
    ax.set_xlim(-0.7, N + 0.2); ax.set_ylim(-0.7, N + 0.2)
    ax.set_xticks([]); ax.set_yticks([]); ax.invert_yaxis()
    for sp in ax.spines.values():
        sp.set_visible(False)
    for r in range(N + 1):
        for c in range(r + 1):
            x = c - r / 2.0 + N / 2.0
            y = r
            v = comb(r, c)
            on = (r == n and c == k)
            row = (r == n)
            ax.text(x, y, str(v), ha="center", va="center",
                    fontsize=9.5 if not on else 11.5,
                    color=("white" if on else (PLOT_INK if not row else PAL["z2"])),
                    fontweight=("bold" if on or row else "normal"),
                    zorder=4,
                    bbox=(dict(boxstyle="circle,pad=0.28", fc=PAL["sum"], ec="none")
                          if on else None))
    return fig


def _read_c07(n=6, k=3):
    from math import comb, factorial
    n, k = int(n), int(k)
    k = min(k, n)
    return readout([("n choose k", "C(%d, %d)" % (n, k)),
                    ("ordered first", "%d!/(%d−%d)! = %d"
                     % (n, n, k, factorial(n) // factorial(n - k))),
                    ("orders of k", "%d! = %d" % (k, factorial(k))),
                    ("result", str(comb(n, k)))])


viz = [viz_intro_box("",
    "Every number here is a binomial coefficient, and the row you pick is the row of "
    + imath("(a+b)^n") + ". Two things are worth seeing. The triangle is <b>symmetric</b> — "
    "choosing k to keep is the same as choosing n−k to leave. And each entry is the sum of the "
    "two above it, which is the whole of Pascal's rule: either the new element is in your "
    "choice, or it is not.")]
viz += slider_plot(_render_c07,
                   {"n": IntSlider(value=6, min=0, max=10, step=1, description="n"),
                    "k": IntSlider(value=3, min=0, max=10, step=1, description="k")},
                   readout_fn=_read_c07)

_n, _k = TV["n_ch"], TV["k_ch"]
from math import comb as _comb, factorial as _fact
_want_ch = _comb(_n, _k)
_want_ord = _fact(_n) // _fact(_n - _k)

practice = [
  exercise_box("", taskline("<b>You choose " + str(_k) + " items out of " + str(_n)
               + ".</b>")
      + "<div>Give two numbers. First the <b>ordered</b> count — how many ways if it matters "
        "which you picked first: " + imath(r"%d\cdot%d\cdot\ldots" % (_n, _n - 1))
      + ", with " + str(_k) + " factors. Then the <b>unordered</b> count "
      + imath(r"\binom{%d}{%d}" % (_n, _k)) + ", where only the set of chosen items "
        "matters.</div>"
      + "<div style='margin-top:10px'>The second is the first divided by " + str(_k)
      + "! — and checking that your two numbers really stand in that ratio is the fastest way "
        "to catch a slip.</div>"),
  numeric_answer([("ordered", "ordered ="), ("choose", "C(%d, %d) =" % (_n, _k))],
                 lambda v: _ans_t7(v), task="t7"),
  code_fold("def choose(n, k):\n"
            "    # return (ordered count, unordered count) — do NOT use math.comb here\n"
            "    return (..., ...)\n",
            lambda g: _check_t7(g), task="t7", locked_by="t6",
            solution="def choose(n, k):\n"
                     "    ordered = 1\n"
                     "    for j in range(n, n - k, -1):   # k factors: n, n-1, ...\n"
                     "        ordered *= j\n"
                     "    orders = 1\n"
                     "    for j in range(1, k + 1):       # k!\n"
                     "        orders *= j\n"
                     "    return (ordered, ordered // orders)\n"),
]


def _ans_t7(v):
    if abs(v["ordered"] - _want_ord) > tol() * max(1, _want_ord):
        if abs(v["ordered"] - _n ** _k) < 0.5:
            return False, ("That is %d^%d — which would allow the same item to be chosen "
                           "twice. Here each pick removes one, so the factors fall: %d · %d · …"
                           % (_n, _k, _n, _n - 1))
        if abs(v["ordered"] - _want_ch) < 0.5:
            return False, "That is already the unordered count — this box wants the ordered one."
        return False, ("Multiply %d factors, starting at %d and counting down: %s."
                       % (_k, _n, " · ".join(str(j) for j in range(_n, _n - _k, -1))))
    if abs(v["choose"] - _want_ch) > tol() * max(1, _want_ch):
        if abs(v["choose"] - _want_ord) < 0.5:
            return False, ("You gave the ordered count again. Divide it by %d! = %d, the number "
                           "of orders the same %d items could have been picked in."
                           % (_k, _fact(_k), _k))
        return False, ("C(%d,%d) = ordered / %d! = %d / %d."
                       % (_n, _k, _k, _want_ord, _fact(_k)))
    return True, ("Correct: %d ordered, and %d / %d! = %d unordered."
                  % (_want_ord, _want_ord, _k, _want_ch))


def _check_t7(g):
    f = g.get("choose")
    if not callable(f):
        return False, "Define a function called choose(n, k)."
    for n, k in ((_n, _k), (49, 6), (5, 3), (4, 0), (4, 4)):
        try:
            out = f(n, k)
        except Exception as e:
            return False, "choose(%d, %d) raised %r." % (n, k, e)
        if not isinstance(out, (tuple, list)) or len(out) != 2:
            return False, "Return exactly two values."
        want = (_fact(n) // _fact(n - k), _comb(n, k))
        if (int(out[0]), int(out[1])) != want:
            return False, ("For n=%d, k=%d the answer is %r — check k = 0 and k = n too."
                           % (n, k, want))
    return True, "Correct, including 49 choose 6 and both edge cases."


interp = interpretation_box(
  "One division separates this chapter from chapter 3, and it is the division by <b>k!</b> — "
  "the number of orders you decided not to care about. Almost every counting mistake in "
  "statistics is that factor: present when it should not be, or absent when it should. The "
  "habit worth taking from here is to ask, before counting anything, <i>does the order of "
  "these count as a different outcome?</i> The lottery says no, so 14 million and not 10 "
  "billion; a peptide sequence says yes, so 20ⁿ and no division at all.")

build_chapter(7, "Choosing without order: the binomial coefficient",
              info=info, viz=viz, practice=practice, interp=interp, locked_by="t6", task="t7")
