_intro = note_box(
  "An exercise here answers back in at most three lines, and one of them is a hint that points "
  "at the step you missed without ever handing you the result. This chapter explains what those "
  "lines can and cannot say — and then makes you use them.")

info = note_box(
  "Press a check button and you get, in this order:<br><br>"
  "<b>A status line</b> — green <i>correct</i> or amber <i>not there yet</i>. Never red for a "
  "wrong answer: red is reserved for something having actually gone wrong, such as code that "
  "raised an exception.<br><br>"
  "<b>A hint</b> — written for the specific thing you entered. If you gave <i>q</i> where "
  "<i>√q</i> was asked, the hint says so. If you rounded to a whole number where the answer is "
  "irrational, the hint says that instead. A hint that merely repeated the question would be "
  "decoration; a hint that gave the answer would end the exercise. The interesting hints are the "
  "ones for the mistakes an author expects, which is why writing them is most of the work of "
  "writing a chapter" + cite(9) + ".<br><br>"
  "<b>An error line</b> — only in the optional code fold, and only if what you wrote raised.<br><br>"
  "<b>The difficulty setting</b>, top left in the toolbar, changes two things and nothing else: "
  "how close a number has to be before it counts (2 % on <i>Gentle</i>, 0.5 % on <i>Standard</i>, "
  "0.1 % on <i>Strict</i>), and whether the tailored hints appear at all — <i>Strict</i> gives "
  "you the status line and leaves the diagnosis to you. It never changes which exercises exist "
  "or what they ask.<br><br>"
  "<b>Two ways out.</b> <i>Skip</i> records that you passed over this one and unlocks what comes "
  "next; the circle on the rail keeps an amber ring and a ⤼ so you can find it again. "
  "<i>Give up</i> shows the worked solution and marks the exercise as such. Both count as having "
  "settled the exercise, neither counts as having solved it, and neither is hidden from you as a "
  "punishment — an exercise you cannot leave is a trap, not a checkpoint.")

def _render_c03(answer=7.0):
    true = float(TV["chapters"])
    fig, ax = fixed_canvas(figsize=(7.4, 3.4), left=.08, right=.97, top=.93, bottom=.22)
    theme_axes(ax, grid=False)
    lo, hi = true * 0.90, true * 1.10
    ax.set_xlim(lo, hi); ax.set_ylim(0, 3.4)
    bands = [("Gentle", 2e-2, PAL["sum"], 2.6), ("Standard", 5e-3, PAL["z2"], 1.7),
             ("Strict", 1e-3, PAL["warn"], 0.8)]
    for name, t, col, y in bands:
        w = true * t
        ax.add_patch(plt.Rectangle((true - w, y - .28), 2 * w, .56, facecolor=col,
                                   alpha=.55, edgecolor=col, lw=1.4, zorder=2))
        ax.text(lo + (hi - lo) * .02, y, name, fontsize=9.5, va="center",
                color=col, fontweight="bold", zorder=4)
    ax.axvline(true, color=PLOT_INK, lw=1.2, ls=":", zorder=3)
    ax.axvline(answer, color=PAL["z"], lw=2.4, zorder=5)
    ax.text(true, 3.15, "the true value", fontsize=8.6, ha="center", color=PLOT_INK)
    ax.set_yticks([]); ax.set_xlabel("what you enter")
    return fig

def _read_c03(answer=7.0):
    true = float(TV["chapters"])
    rel = abs(answer - true) / true if true else 0
    passes = [n for n, t in (("Gentle", 2e-2), ("Standard", 5e-3), ("Strict", 1e-3)) if rel <= t]
    return readout([("your entry", "%.3f" % answer), ("true value", "%g" % true),
                    ("relative error", "%.2f %%" % (100 * rel)),
                    ("accepted by", ", ".join(passes) if passes else "none of the three")])

viz = [viz_intro_box("",
    "The three difficulty levels drawn as what they are: three widths around the same true "
    "value. Slide <b>answer</b> and watch which bands still contain it. Note how little "
    "<i>Strict</i> forgives — and that changing the setting has moved no band's centre.")]
viz += slider_plot(_render_c03,
    {"answer": FloatSlider(value=float(TV["chapters"]) * 0.97,
                           min=float(TV["chapters"]) * 0.90,
                           max=float(TV["chapters"]) * 1.10,
                           step=float(TV["chapters"]) * 0.002, description="answer")},
    readout_fn=_read_c03)

_C, _S, _K, _F = TV["chapters"], TV["solved"], TV["skipped"], TV["failed"]

def _ans_c03(v):
    want_open = _C - _S - _K - _F
    want_pct = 100.0 * _S / _C
    if abs(v["open"] - want_open) > 0.5:
        if abs(v["open"] - (_C - _S)) < 0.5:
            return False, ("You subtracted only the solved ones. Skipped and given-up exercises "
                           "are settled too — they are no longer open.")
        return False, ("Not yet. Of %d exercises, %d are solved, %d skipped and %d given up; "
                       "everything else is still open." % (_C, _S, _K, _F))
    if abs(v["pct"] - want_pct) > 100 * tol() * 2:
        if abs(v["pct"] - 100.0 * (_S + _K) / _C) < 0.6:
            return False, ("You counted the skipped ones as passed. The badge keeps them apart "
                           "on purpose — that is the whole reason it has three numbers.")
        return False, ("The pass rate is solved ÷ total, as a percentage: %d ÷ %d. You entered "
                       "%.2f %%." % (_S, _C, v["pct"]))
    return True, ("Correct: %d still open, and a pass rate of %.2f %%. Notice that the pass rate "
                  "says nothing about the %d you skipped — which is exactly the point of "
                  "chapter 4." % (want_open, want_pct, _K))

practice = [
  exercise_box("", taskline(
    "<b>Your imagined course has " + str(_C) + " exercises.</b> You have solved <b>" + str(_S) +
    "</b>, skipped <b>" + str(_K) + "</b> and given up on <b>" + str(_F) + "</b>.")
    + "<div>Give the number still <b>open</b>, and your <b>pass rate</b> in percent (solved "
      "divided by the total). Enter the percentage as a decimal with at least two places — and "
      "before you press check, set the difficulty to <i>Gentle</i> and then to <i>Strict</i> and "
      "watch the hint change.</div>"),
  numeric_answer([("open", "still open ="), ("pct", "pass rate [%] =")], _ans_c03, task="t3"),
  code_fold(
    "# Return (open, pass_rate_percent) for a notebook with these tallies.\n"
    "\n"
    "def tally(total, solved, skipped, failed):\n"
    "    still_open = ...\n"
    "    pass_rate  = ...\n"
    "    return (still_open, pass_rate)\n",
    lambda g: _check_c03(g), task="t3", locked_by="t1",
    solution="def tally(total, solved, skipped, failed):\n"
             "    still_open = total - solved - skipped - failed\n"
             "    pass_rate  = 100.0 * solved / total\n"
             "    return (still_open, pass_rate)\n"),
]

def _check_c03(g):
    f = g.get("tally")
    if not callable(f):
        return False, "Define a function called tally(total, solved, skipped, failed)."
    for args in ((10, 4, 2, 1), (_C, _S, _K, _F), (8, 8, 0, 0)):
        try:
            out = f(*args)
        except Exception as e:
            return False, "tally%r raised %r." % (args, e)
        if not isinstance(out, (tuple, list)) or len(out) != 2:
            return False, "Return exactly two values: (still_open, pass_rate)."
        t, s, k, x = args
        if out[0] != t - s - k - x:
            return False, ("For %r the open count should be %d." % (args, t - s - k - x))
        if abs(out[1] - 100.0 * s / t) > 1e-6:
            return False, "The pass rate is a percentage: 100 · solved / total."
    return True, "Both values, and the skipped ones correctly excluded from the pass rate."

interp = interpretation_box(
  "A check that only says <i>wrong</i> teaches nothing, and a check that says <i>the answer is "
  "4.7</i> ends the exercise. Everything in this chapter sits between those two, and so does the "
  "difficulty setting: it moves the width of the band, never the centre. Set it where the "
  "feedback is useful to you rather than where it flatters you — nobody else ever sees it.")

build_chapter(3, "How an exercise answers back", info=info, intro=_intro, viz=viz,
              practice=practice, interp=interp, task="t3", locked_by="t2")
