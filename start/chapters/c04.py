_intro = note_box(
  "Chapters unlock as you go. This is the feature most often mistaken for grading, and the "
  "misunderstanding matters, because what you believe a lock is changes how you behave in front "
  "of it.")

info = note_box(
  "<b>What a lock does.</b> A chapter whose exercise has not been settled waits behind a small "
  "panel with a sentence saying what opens it — and a button labelled <i>Open anyway</i>. "
  "The chapter's <b>text is never locked</b>: you can read every word of every chapter from the "
  "first minute. Only the interactive parts wait.<br><br>"
  "<b>What a lock is not.</b> It is not assessment. Nothing is submitted, nothing is reported, "
  "no one is told. The check functions live in the same cell as the exercises — a reader who "
  "wants the answers has them, and that is fine, because the lock exists to stop you from "
  "arriving at chapter 6 without chapter 3, not to find out whether you did.<br><br>"
  "<b>Why bother at all, then?</b> Because a notebook is a document with no natural resistance. "
  "You can scroll to the end of anything. Where every idea is built on the one before, a "
  "checkpoint every few screens is the cheapest way of telling you — not your lecturer — that "
  "something did not land. That it can be waved past with one click is not a weakness of the "
  "design; it is what keeps it honest.<br><br>"
  "<b>The lock lives in your browser.</b> Clear the site data and every chapter is shut again; "
  "open the notebook in a second browser and it starts from the beginning. If that annoys you, "
  "chapter 6 has the answer.")

def _render_c04(solved=3):
    n = 8
    fig, ax = fixed_canvas(figsize=(7.4, 3.6), left=.03, right=.97, top=.92, bottom=.10)
    ax.set_xlim(0, n + 1); ax.set_ylim(0, 4); ax.axis("off")
    for i in range(1, n + 1):
        if i <= solved:
            face, ring, glyph = PAL["sum"], PAL["sum"], "✓"
        elif i == solved + 1:
            face, ring, glyph = "#ffffff", PAL["sum"], "○"
        else:
            face, ring, glyph = "#eef1f4", "#c7ced5", "·"
        ax.add_patch(plt.Circle((i, 2.2), .34, facecolor=face, edgecolor=ring, lw=2.6, zorder=3))
        ax.text(i, 2.2, glyph, fontsize=11, ha="center", va="center", zorder=4,
                color="#ffffff" if i <= solved else "#7a8794")
        ax.text(i, 1.45, "ch %d" % i, fontsize=8.6, ha="center", color="#8b98a5")
    ax.plot([1, n], [2.2, 2.2], color="#d6dce2", lw=3, zorder=1)
    if solved >= 1:
        ax.plot([1, min(solved + 1, n)], [2.2, 2.2], color=PAL["sum"], lw=3.4, zorder=2)
    ax.text((n + 1) / 2, 3.35, "the timeline, with %d of %d settled" % (solved, n),
            fontsize=10, ha="center", color=PLOT_INK)
    return fig

def _read_c04(solved=3):
    return readout([("settled", "%d" % solved),
                    ("open now", "%d" % min(solved + 1, 8)),
                    ("still shut", "%d" % max(0, 8 - solved - 1)),
                    ("readable", "8 — the text is never locked")])

viz = [viz_intro_box("",
    "Eight chapters and one moving frontier. Drag <b>solved</b> and watch the green fill follow, "
    "the open padlock sit one step ahead of it, and everything behind it stay unlocked for good. "
    "This is the same picture the rail on the right draws for the notebook you are actually in — "
    "including the rule that whatever is <i>behind</i> the open padlock is open, whether you "
    "solved it, skipped it or gave up on it.")]
viz += slider_plot(_render_c04, {"solved": IntSlider(value=3, min=0, max=8, step=1,
                                                     description="solved")},
                   readout_fn=_read_c04)

def _ans_c04(idx, label):
    if idx == 1:
        return True, ("Correct. Skipping settles the exercise, so the next chapter opens — and "
                      "the circle keeps an amber ring and a ⤼ so you can find it again later.")
    if idx == 0:
        return False, ("No — an exercise you cannot leave is a trap. Look for the second button "
                       "next to the check.")
    if idx == 2:
        return False, ("Nothing is reported to anybody. There is no server in this system at all.")
    return False, ("The green progress fill counts what you solved. Skipping does not colour it "
                   "green, but it does open the next chapter.")

practice = [
  exercise_box("", taskline(
    "<b>Find the two buttons.</b> Scroll back to the practice fold of chapter 3 and look at what "
    "sits beside the check button. Then answer: what happens to the chapters after an exercise "
    "you press <i>Skip</i> on?")),
  choice_answer("After skipping an exercise …",
    ["… nothing; the next chapter stays shut until I solve it.",
     "… the next chapter opens, and the skipped one is marked on the rail so I can return to it.",
     "… the skip is recorded and reported as a gap.",
     "… the progress bar turns green as if I had solved it."],
    _ans_c04, task="t4"),
]

interp = interpretation_box(
  "A lock you can always open is a <b>pace</b>, not a gate. Read it as a message from the "
  "notebook to you — <i>this next part assumes the last one</i> — and the feature does what it "
  "was built for. Read it as a grade and it will only make you resent a document that has no "
  "opinion about you whatsoever.")

build_chapter(4, "Locks: pacing, not grading", info=info, intro=_intro, viz=viz,
              practice=practice, interp=interp, task="t4", locked_by="t3")
