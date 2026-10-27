_intro = note_box(
  "Every chapter in every notebook of this catalogue has the same four parts in the same order. "
  "Once you have seen them here you can skim the first screen of any other notebook and know "
  "where everything is.")

info = note_box(
  "<b>1 · The key message</b> — a short grey note at the top saying what this chapter is about "
  "and how it follows from the one before. It is the only part written to be readable out of "
  "context, and it is what you reread the night before an exam.<br><br>"
  "<b>2 · The content box</b> — the idea, the formula, and a named list of every symbol in it. "
  "Symbols are listed even when they look obvious; the ten seconds that costs the author saves "
  "the reader the ten minutes of deciding whether <i>b</i> means the same thing it meant two "
  "chapters ago.<br><br>"
  "<b>3 · The visualisation fold</b> — a picture with sliders. It is closed by default, because "
  "a picture you opened on purpose is looked at and a picture that was already open is scrolled "
  "past. The axes never rescale while you drag: if the frame moved with the data you would be "
  "unable to tell a change in the curve from a change in the view.<br><br>"
  "<b>4 · The practice fold</b> — exactly one exercise, with your own numbers, and underneath it "
  "a second closed fold offering the same exercise as a piece of Python. One exercise, not five: "
  "the exercise is the checkpoint that opens the next chapter, and a checkpoint made of five "
  "questions is a quiz, which is what the appendix is for.<br><br>"
  "Under all four sits a green <b>interpretation box</b>: one paragraph saying what the chapter "
  "was actually for. If you read nothing else in a chapter, read the grey note at the top and "
  "the green box at the bottom.")

_PARTS = ["key message", "content box", "visualisation", "practice", "interpretation"]

def _render_c02(part=1):
    heights = [.9, 2.3, 1.7, 2.0, 1.0]
    labels = ["key message (grey note)", "content box — idea, formula, symbols",
              "Visualisation  (closed fold)", "Practice  (closed fold) + optional code",
              "interpretation (green)"]
    colours = ["#8b98a5", PAL["z2"], PAL["aux"], PAL["warn"], PAL["sum"]]
    fig, ax = fixed_canvas(figsize=(7.2, 4.6), left=.02, right=.98, top=.96, bottom=.03)
    ax.set_xlim(0, 10); ax.set_ylim(0, 9.6); ax.axis("off")
    y = 9.2
    for i, h in enumerate(heights):
        on = (i == part)
        ax.add_patch(plt.Rectangle((1.0, y - h), 8.0, h - .16,
                                   facecolor=colours[i] if on else "#e6eaee",
                                   edgecolor=colours[i] if on else "#d4dae0",
                                   lw=2.0 if on else 1.0, zorder=2))
        ax.text(1.35, y - h / 2 - .08, labels[i], fontsize=10.2,
                fontweight="bold" if on else "normal",
                color="#ffffff" if on else "#7a8794", va="center", zorder=3)
        y -= h
    return fig

def _read_c02(part=1):
    what = ["read it first", "the reference part", "open it and drag",
            "one exercise, your numbers", "read it last"]
    return readout([("highlighted", _PARTS[part]), ("what to do", what[part]),
                    ("open by default", "yes" if part in (0, 1, 4) else "no"),
                    ("parts in total", "5")])

viz = [viz_intro_box("",
    "The anatomy of one chapter, top to bottom. Move <b>part</b> to highlight each in turn. "
    "The two folds in the middle are the ones that start closed — and the chapter you are "
    "reading right now is built out of exactly these five pieces.")]
viz += slider_plot(_render_c02, {"part": IntSlider(value=1, min=0, max=4, step=1,
                                                   description="part")},
                   readout_fn=_read_c02)

def _ans_c02(idx, label):
    if idx == 2:
        return True, ("Correct — and the reason is worth keeping: an axis that rescales while "
                      "you drag makes every change look the same.")
    if idx == 0:
        return False, ("Closed folds are about attention, not about size — the notebook is one "
                       "cell either way.")
    if idx == 1:
        return False, ("Nothing here is hidden from you. Every fold opens with one click and "
                       "nothing asks who you are.")
    return False, ("The plots are drawn by the kernel when the fold is opened, but that is a "
                   "side effect, not the reason.")

practice = [
  exercise_box("", taskline(
    "<b>Open the visualisation fold above, drag the slider to <i>practice</i>, and then answer:</b> "
    "why do the visualisation and practice folds start closed while the text boxes do not?")),
  choice_answer("The folds are closed because …",
    ["… a closed fold makes the file smaller.",
     "… the content is restricted until you have read the chapter.",
     "… something you opened on purpose gets looked at; something already open gets scrolled past.",
     "… the plots would otherwise slow the notebook down."],
    _ans_c02, task="t2"),
]

interp = interpretation_box(
  "The repetition is the feature. Four parts, always in the same order, always with the same "
  "icons, means that the structure costs you nothing to learn twice — and that a reader who "
  "arrives in the middle of a notebook still knows what they are looking at. When you write "
  "your own chapter in the appendix, keep the order even if you leave parts out.")

build_chapter(2, "The anatomy of a chapter", info=info, intro=_intro, viz=viz,
              practice=practice, interp=interp, task="t2", locked_by="t1")
