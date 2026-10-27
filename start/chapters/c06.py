_intro = note_box(
  "Your answers are recorded. Nothing is sent anywhere. Those two sentences are not in tension, "
  "and this chapter explains the mechanism that makes both true at once — and what to do when "
  "you want your progress on a different machine.")

info = note_box(
  "<b>Where it lives.</b> Every time you settle an exercise, the notebook writes a small record "
  "into this browser's own local storage: which exercises were answered, which were skipped, "
  "which were given up, and the notebook's id. It is the same place a website keeps the fact "
  "that you dismissed its cookie banner. No request is made, because there is nobody to make it "
  "to.<br><br>"
  "<b>What follows from that.</b> The record belongs to <i>this browser on this machine</i>. A "
  "different browser, a private window, a different laptop or a cleared cache all start from "
  "zero. That is the honest cost of having no server, and it is the reason for the next "
  "paragraph.<br><br>"
  "<b>The progress code.</b> The 👤 chip in the middle of the toolbar opens a short block of "
  "text that encodes your record. Copy it, paste it into the same box on another machine, and "
  "your progress is there. It is not a login: nothing is checked, nothing expires, and anyone "
  "you hand it to gets your progress, which is a good reason not to treat it as a credential and "
  "an excellent reason for nobody to grade with it.<br><br>"
  "<b>The statistics badge.</b> Beside the chip sit three numbers — ✓ solved, ⤼ skipped, "
  "✗ given up — summed across every notebook of this series that this browser has seen, over "
  "the total number of exercises those notebooks contain. It is a note to yourself about where "
  "to go back to, and it keeps the three outcomes apart on purpose: a single percentage would "
  "quietly turn eleven skipped exercises into the same thing as eleven solved ones.")

def _render_c06(week=4):
    weeks = np.arange(0, 9)
    solved = np.clip(np.round(np.linspace(0, 26, 9)), 0, None)
    skipped = np.clip(np.round(np.linspace(0, 7, 9) * (weeks % 3 != 0)), 0, None)
    failed = np.clip(np.round(np.linspace(0, 3, 9)), 0, None)
    fig, ax = fixed_canvas(figsize=(7.4, 3.6), left=.10, right=.97, top=.92, bottom=.18)
    theme_axes(ax)
    ax.set_xlim(-.6, 8.6); ax.set_ylim(0, 34)
    k = int(week)
    # matplotlib takes ONE alpha per call, not one per bar — so the faded term is
    # drawn first and the selected week is drawn again on top at full strength
    ax.bar(weeks, solved, color=PAL["sum"], width=.62, label="solved", alpha=.32)
    ax.bar(weeks, skipped, bottom=solved, color=PAL["warn"], width=.62,
           label="skipped", alpha=.32)
    ax.bar(weeks, failed, bottom=solved + skipped, color=PAL["z"], width=.62,
           label="given up", alpha=.32)
    ax.bar([k], [solved[k]], color=PAL["sum"], width=.62)
    ax.bar([k], [skipped[k]], bottom=[solved[k]], color=PAL["warn"], width=.62)
    ax.bar([k], [failed[k]], bottom=[solved[k] + skipped[k]], color=PAL["z"], width=.62)
    ax.set_xlabel("week of the course"); ax.set_ylabel("exercises")
    theme_legend(ax, loc="upper left", fontsize=8)
    return fig

def _read_c06(week=4):
    k = int(week)
    solved = int(round(np.linspace(0, 26, 9)[k]))
    skipped = int(round(np.linspace(0, 7, 9)[k])) if k % 3 != 0 else 0
    failed = int(round(np.linspace(0, 3, 9)[k]))
    return readout([("week", "%d" % k), ("✓ solved", "%d" % solved),
                    ("⤼ skipped", "%d" % skipped), ("✗ given up", "%d" % failed)])

viz = [viz_intro_box("",
    "A simulated term seen through the badge. <b>The three numbers are kept apart on purpose.</b> "
    "Collapse them into one percentage and the amber band vanishes — along with the only "
    "information in the picture that tells you what to revisit. These bars are invented, not "
    "measured; your own three numbers are in the toolbar.")]
viz += slider_plot(_render_c06, {"week": IntSlider(value=4, min=0, max=8, step=1,
                                                   description="week")},
                   readout_fn=_read_c06)

def _ans_c06(idx, label):
    if idx == 2:
        return True, ("Correct. It is a copyable record, nothing more — which is why it can be "
                      "carried, and why it must never be used to grade anyone.")
    if idx == 0:
        return False, ("There is no account anywhere in this system, so there is nothing to log "
                       "into and nothing to lose.")
    if idx == 1:
        return False, ("Nothing is transmitted. Open the browser's network tab while you answer "
                       "an exercise and watch nothing happen.")
    return False, ("The notebook file is never written to by your answers; it is the same file "
                   "for everyone.")

practice = [
  exercise_box("", taskline(
    "<b>Open the 👤 chip in the toolbar</b> and look at what it shows you. Then answer: what is "
    "that block of text?")),
  choice_answer("The progress code is …",
    ["… a login that identifies me to the course.",
     "… a link that uploads my results when I click it.",
     "… a copyable record of my answers, which I move between browsers by hand.",
     "… stored inside the notebook file, so it travels with the document."],
    _ans_c06, task="t6"),
]

interp = interpretation_box(
  "No server means no account, no data protection paperwork, no outage and no way for anything "
  "you type to be used against you — and, unavoidably, no synchronisation either. The progress "
  "code is the smallest possible bridge across that gap: a piece of text you carry yourself, "
  "which is also the only kind of transfer that leaves you in charge of it.")

build_chapter(6, "Where your progress lives", info=info, intro=_intro, viz=viz,
              practice=practice, interp=interp, task="t6", locked_by="t5")
