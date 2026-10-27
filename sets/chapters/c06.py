_intro = (
  "Σ and Π are not operations — they are <b>abbreviations</b>" + cite(1) + ". Each one says: "
  "take the index j, run it from the bottom number to the top number, and add (or multiply) "
  "whatever stands to the right. Everything you will meet later that looks intimidating in Σ "
  "notation is a long sum someone did not want to write out.")

info = concept_box(_intro,
    r"$\sum_{j=m}^{n} a_j = a_m + a_{m+1} + \dots + a_n \qquad "
    r"\prod_{j=m}^{n} a_j = a_m \cdot a_{m+1} \cdot \dots \cdot a_n$",
    variables=[("j", "the index — a name, not a quantity; it disappears in the answer"),
               ("m", "where the index starts (inclusive)"),
               ("n", "where it stops (inclusive)"),
               ("aⱼ", "the term — anything at all that depends on j")],
    extra_html=(
      "<div style='max-width:800px;margin:14px auto 0;text-align:justify;line-height:1.6'>"
      "Both limits are <b>inclusive</b>, which is the single most common slip: "
      + imath(r"\sum_{j=3}^{7} j^2 = 9+16+25+36+49 = 135") + " has five terms, not four. "
      "(Python's <code>range(3, 8)</code> is where that bites — the stop value is excluded "
      "there, so the translation always costs a +1.)<br><br>"
      "The <b>factorial</b> is a product with nothing extra in it: "
      + imath(r"n! = \prod_{j=1}^{n} j = n\cdot(n-1)\cdot\ldots\cdot2\cdot1") + ", so "
      + imath("5! = 120") + ". By convention " + imath("0! = 1") + " — the empty product, the "
      "same way an empty sum is 0.</div>"))


def _render_c06(n=6, m=1, mode=0):
    """The terms as bars, and the running total drawn on top of them."""
    n, m, mode = int(n), int(m), int(mode)
    if m > n:
        m = n
    js = np.arange(m, n + 1)
    terms = js.astype(float) ** 2 if mode == 0 else js.astype(float)
    fig, ax = fixed_canvas(figsize=(6.8, 3.8), left=.12, right=.88, top=.93, bottom=.17)
    ax.set_xlim(0.3, 9.7)
    ax.set_xticks(range(1, 10))
    theme_axes(ax, grid=True)
    ax.set_ylim(0, 92 if mode == 0 else 11)
    ax.bar(js, terms, width=.62, color=PAL["z2"], alpha=.75, zorder=3)
    for j, t in zip(js, terms):
        ax.text(j, t + (2.5 if mode == 0 else .3), "%d" % t, ha="center",
                fontsize=8.5, color=PLOT_INK, zorder=4)
    ax.set_xlabel("j", color=PLOT_INK, fontsize=11)
    ax.set_ylabel("aⱼ = j²" if mode == 0 else "aⱼ = j", color=PLOT_INK, fontsize=11)
    # the accumulation on its own axis: a sum grows, a product runs away
    ax2 = ax.twinx()
    run = np.cumsum(terms) if mode == 0 else np.cumprod(terms)
    ax2.plot(js, run, "o-", color=PAL["sum"], lw=2.0, ms=6, zorder=5)
    ax2.tick_params(colors=PAL["sum"], labelcolor=PAL["sum"], labelsize=9)
    for sp in ax2.spines.values():
        sp.set_color(PLOT_INK); sp.set_linewidth(1.0)
    ax2.set_ylabel("running Σ" if mode == 0 else "running Π", color=PAL["sum"], fontsize=11)
    ax2.set_ylim(0, max(220.0, float(run[-1]) * 1.12) if mode == 0
                 else max(10.0, float(run[-1]) * 1.12))
    return fig


def _read_c06(n=6, m=1, mode=0):
    n, m, mode = int(n), int(m), int(mode)
    if m > n:
        m = n
    js = np.arange(m, n + 1)
    terms = js.astype(float) ** 2 if mode == 0 else js.astype(float)
    total = float(terms.sum()) if mode == 0 else float(np.prod(terms))
    return readout([("terms", "j = %d … %d" % (m, n)),
                    ("how many", str(len(js))),
                    ("written out", " %s " % ("+" if mode == 0 else "·")
                     .join("%d" % t for t in terms)),
                    ("total", "%d" % total)])


viz = [viz_intro_box("",
    "The bars are the individual terms; the green line is the running total. Move the lower "
    "limit and count the bars — <b>both limits are included</b>, so j from 3 to 7 is five terms. "
    "Then switch <b>mode</b> to the product and watch the right-hand axis: the same numbers, "
    "multiplied instead of added, leave the picture almost at once. That is the factorial's "
    "temperament, and the reason chapter 7 needs a way to cancel most of it.")]
viz += slider_plot(_render_c06,
                   {"mode": IntSlider(value=0, min=0, max=1, step=1, description="Σ / Π"),
                    "m": IntSlider(value=1, min=1, max=9, step=1, description="from j ="),
                    "n": IntSlider(value=6, min=1, max=9, step=1, description="to j =")},
                   readout_fn=_read_c06)

_m, _n, _f = TV["m_sum"], TV["n_sum"], TV["fact"]
_sum_want = sum(j * j for j in range(_m, _n + 1))
_fact_want = 1
for _j in range(1, _f + 1):
    _fact_want *= _j

practice = [
  exercise_box("", taskline("<b>Two values, both written out by hand.</b>")
      + formula_line(r"$\sum_{j=%d}^{%d} j^2 \qquad\text{and}\qquad %d!$" % (_m, _n, _f))
      + "<div>Write the first one out term by term before adding — the point of the exercise is "
        "the number of terms, not the arithmetic. Remember that <b>both</b> limits belong to "
        "the sum.</div>"),
  numeric_answer([("s", "Σ j² ="), ("f", "%d! =" % _f)],
                 lambda v: _ans_t6(v), task="t6"),
  code_fold("def sigma_pi(m, n, k):\n"
            "    # return (sum of j*j for j from m to n inclusive, k factorial)\n"
            "    return (..., ...)\n",
            lambda g: _check_t6(g), task="t6", locked_by="t5",
            solution="def sigma_pi(m, n, k):\n"
                     "    # range(m, n + 1): the +1 is the inclusive upper limit\n"
                     "    s = sum(j * j for j in range(m, n + 1))\n"
                     "    f = 1\n"
                     "    for j in range(1, k + 1):\n"
                     "        f *= j\n"
                     "    return (s, f)\n"),
]


def _ans_t6(v):
    if abs(v["s"] - _sum_want) > tol() * max(1, _sum_want):
        short = sum(j * j for j in range(_m, _n))
        if abs(v["s"] - short) < 0.5:
            return False, ("You stopped one term early — j = %d belongs to the sum as well."
                           % _n)
        if abs(v["s"] - sum(range(_m, _n + 1))) < 0.5:
            return False, "You added the j, not the j². Each term is squared first."
        return False, ("Write it out: %s. There are %d terms."
                       % (" + ".join("%d²" % j for j in range(_m, _n + 1)), _n - _m + 1))
    if abs(v["f"] - _fact_want) > tol() * max(1, _fact_want):
        if abs(v["f"] - sum(range(1, _f + 1))) < 0.5:
            return False, "That is the sum 1+2+…+n. A factorial multiplies."
        return False, ("%d! = %s." % (_f, " · ".join(str(j) for j in range(_f, 0, -1))))
    return True, ("Correct: %d terms giving %d, and %d! = %d."
                  % (_n - _m + 1, _sum_want, _f, _fact_want))


def _check_t6(g):
    f = g.get("sigma_pi")
    if not callable(f):
        return False, "Define a function called sigma_pi(m, n, k)."
    import math
    for m, n, k in ((_m, _n, _f), (3, 7, 5), (1, 1, 1), (2, 4, 0)):
        try:
            out = f(m, n, k)
        except Exception as e:
            return False, "sigma_pi(%d, %d, %d) raised %r." % (m, n, k, e)
        if not isinstance(out, (tuple, list)) or len(out) != 2:
            return False, "Return exactly two values."
        want = (sum(j * j for j in range(m, n + 1)), math.factorial(k))
        if (int(out[0]), int(out[1])) != want:
            return False, ("For m=%d, n=%d, k=%d the answer is %r — note 0! = 1."
                           % (m, n, k, want))
    return True, "Correct, including the single-term sum and 0! = 1."


interp = interpretation_box(
  "Σ is the notation nearly every formula in the rest of the course is written in — a mean, a "
  "variance, a least-squares residual, a Fourier series are all one Σ with a different term "
  "inside. Getting fluent here costs an hour and saves the whole term. The one thing to carry "
  "forward: <b>read off the limits first and count the terms</b>, before looking at what is "
  "being summed. Most Σ mistakes are off-by-one, not algebra.")

build_chapter(6, "Σ, Π and the factorial",
              info=info, viz=viz, practice=practice, interp=interp, locked_by="t5", task="t6")
