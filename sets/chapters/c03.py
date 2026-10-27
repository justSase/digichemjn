_intro = (
  "The <b>cardinality</b> #A is simply the number of elements of A — finite or ∞" + cite(1) + ". "
  "The interesting operation is the <b>Cartesian product</b> " + imath(r"M_1\times M_2")
  + ", which does not combine two sets into a bigger collection of the same kind of thing: it "
  "builds the set of all <b>ordered pairs</b>, one entry from each. That is what a pair of dice, "
  "a die and a coin, or a position and a time is.")

info = concept_box(_intro,
    r"$M = M_1\times M_2 = \{(a,b)\mid a\in M_1 \wedge b\in M_2\}"
    r"\qquad \# M = \# M_1\cdot \# M_2$",
    variables=[("#A", "cardinality — the number of elements of A (also written |A|)"),
               ("M₁ × M₂", "the set of all ordered pairs (a, b)"),
               ("Mⁿ", "the product of n identical copies, M × M × … × M"),
               ("#M", "for finite sets: the product m₁ · m₂ · … · mₙ")],
    extra_html=(
      "<div style='max-width:800px;margin:14px auto 0;text-align:justify;line-height:1.6'>"
      "<b>Ordered</b> is the load-bearing word. (heads, 3) and (3, heads) are different elements "
      "of different products, and inside " + imath(r"M\times M") + " the pairs (2,5) and (5,2) "
      "are two elements, not one. That is exactly the opposite of a set, where order never "
      "counts — and the difference is what chapter 7 is about.<br><br>"
      "The counts multiply for the reason you would guess: every one of the "
      + imath(r"\# M_1") + " first entries can be followed by any of the " + imath(r"\# M_2")
      + " second ones, and none of those combinations coincide.</div>"))


def _render_c03(m1=6, m2=2):
    """The product as a grid — the picture that makes m1·m2 obvious."""
    m1, m2 = int(m1), int(m2)
    fig, ax = fixed_canvas(figsize=(6.6, 3.9), left=.11, right=.97, top=.93, bottom=.15)
    ax.set_xlim(-0.6, 8.6); ax.set_ylim(-0.6, 4.6)
    ax.set_xticks(range(0, 9)); ax.set_yticks(range(0, 5))
    ax.set_xticklabels([str(i + 1) for i in range(9)])
    ax.set_yticklabels([str(i + 1) for i in range(5)])
    theme_axes(ax, grid=True)
    xs, ys = np.meshgrid(np.arange(m1), np.arange(m2))
    ax.plot(xs.ravel(), ys.ravel(), "o", color=PAL["sum"], ms=9, zorder=3)
    # the two factors drawn along their axes
    ax.plot(np.arange(m1), np.full(m1, -0.38), "s", color=PAL["z2"], ms=7, zorder=3)
    ax.plot(np.full(m2, -0.42), np.arange(m2), "s", color=PAL["z"], ms=7, zorder=3)
    ax.set_xlabel("M₁", color=PAL["z2"], fontsize=11)
    ax.set_ylabel("M₂", color=PAL["z"], fontsize=11)
    return fig


def _read_c03(m1=6, m2=2):
    m1, m2 = int(m1), int(m2)
    return readout([("#M₁", str(m1)), ("#M₂", str(m2)),
                    ("#(M₁ × M₂)", "%d · %d = %d" % (m1, m2, m1 * m2)),
                    ("#(M₁ × M₁)", "%d² = %d" % (m1, m1 * m1))])


viz = [viz_intro_box("",
    "Each dot is one <b>pair</b>, and the grid is the whole product. Change either factor and "
    "the dots do not grow by that amount, they grow by that <i>multiple</i> — one new column is "
    "a whole column of new pairs. The two rows of squares along the axes are the original sets, "
    "which is the comparison worth making: adding one element to M₁ adds #M₂ elements to the "
    "product.")]
viz += slider_plot(_render_c03,
                   {"m1": IntSlider(value=6, min=1, max=9, step=1, description="#M₁"),
                    "m2": IntSlider(value=2, min=1, max=5, step=1, description="#M₂")},
                   readout_fn=_read_c03)

_d, _c = TV["dice"], TV["coin"]

practice = [
  exercise_box("", taskline("<b>You roll a die with " + str(_d) + " faces and, independently, "
               "spin a marker with " + str(_c) + " sides.</b>")
      + "<div>The set of outcomes is the Cartesian product " + imath(r"M = M_1 \times M_2")
      + " with " + imath(r"\# M_1 = %d" % _d) + " and " + imath(r"\# M_2 = %d" % _c) + ".</div>"
      + "<div style='margin-top:8px'>Give <b>#M</b>, and then <b>#(M₁ × M₁)</b> — the outcomes "
        "of rolling that same die <i>twice</i>, where (2,5) and (5,2) count separately.</div>"),
  numeric_answer([("prod", "#M ="), ("sq", "#(M₁ × M₁) =")],
                 lambda v: _ans_t3(v), task="t3"),
  code_fold("import itertools\n\n"
            "def product_size(m1, m2):\n"
            "    # return (number of pairs from m1 and m2, number of pairs from m1 with itself)\n"
            "    return (..., ...)\n",
            lambda g: _check_t3(g), task="t3", locked_by="t2",
            solution="import itertools\n\n"
                     "def product_size(m1, m2):\n"
                     "    # built out, to show the pairs really are what is counted\n"
                     "    mixed = list(itertools.product(range(m1), range(m2)))\n"
                     "    same  = list(itertools.product(range(m1), repeat=2))\n"
                     "    return (len(mixed), len(same))\n"),
]


def _ans_t3(v):
    w1, w2 = _d * _c, _d * _d
    if abs(v["prod"] - w1) > tol() * max(1, w1):
        if abs(v["prod"] - (_d + _c)) < 0.5:
            return False, ("You added. Each of the %d faces can be paired with each of the %d "
                           "sides, so the counts multiply." % (_d, _c))
        return False, "#M = #M₁ · #M₂ — multiply the two counts."
    if abs(v["sq"] - w2) > tol() * max(1, w2):
        n_unord = _d * (_d + 1) // 2
        if abs(v["sq"] - n_unord) < 0.5:
            return False, ("That is the count with the order ignored. A product is ordered: "
                           "(2,5) and (5,2) are two different pairs.")
        if abs(v["sq"] - _d * (_d - 1)) < 0.5:
            return False, ("Close — but nothing forbids rolling the same face twice, so the "
                           "pairs (k,k) count as well.")
        return False, "Rolling the same die twice gives #M₁ · #M₁ pairs."
    return True, ("Correct: %d · %d = %d, and %d² = %d." % (_d, _c, w1, _d, w2))


def _check_t3(g):
    f = g.get("product_size")
    if not callable(f):
        return False, "Define a function called product_size(m1, m2)."
    for a, b in ((_d, _c), (1, 1), (3, 5), (6, 2)):
        try:
            out = f(a, b)
        except Exception as e:
            return False, "product_size(%d, %d) raised %r." % (a, b, e)
        if not isinstance(out, (tuple, list)) or len(out) != 2:
            return False, "Return exactly two values."
        if (int(out[0]), int(out[1])) != (a * b, a * a):
            return False, "For m1=%d, m2=%d the answer is (%d, %d)." % (a, b, a * b, a * a)
    return True, "Correct, including the one-element case."


interp = interpretation_box(
  "The product is where combinatorial explosion starts, and it is worth feeling it once: a "
  "peptide of length 5 built from the 20 amino acids lives in " + imath("20^5")
  + " = 3 200 000 possibilities" + cite(4) + ", and length 10 gives " + imath("20^{10}")
  + " ≈ 10¹³. No experiment enumerates that. Every method you will meet for searching sequence "
  "or parameter space exists because the Cartesian product is too large to write down — which "
  "makes this the most practically important line in the section.")

build_chapter(3, "Counting: cardinality and the Cartesian product",
              info=info, viz=viz, practice=practice, interp=interp, locked_by="t2", task="t3")
