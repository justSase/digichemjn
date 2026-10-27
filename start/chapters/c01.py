_intro = note_box(
  "Open this notebook's file in a text editor and you will find <b>two cells</b>. One is a "
  "markdown cell holding the title card. The other is a single collapsed code cell holding "
  "everything else — the toolkit, every chapter, every exercise, the panel. That is not "
  "laziness; it is the only shape that makes the rest of the format possible.")

info = note_box(
  "A classical teaching notebook is a long ladder of small cells, and the reader is expected to "
  "run them in order. It fails in three ordinary situations: somebody runs cell 12 before cell 7 "
  "and gets an error that has nothing to do with the subject; somebody edits a cell by accident "
  "and cannot get it back; somebody closes the tab and returns to a document whose state is "
  "scattered over forty cells, half of which now have to be re-run in the right order.<br><br>"
  "<b>Two cells remove all three at once.</b> There is no order to get wrong, because there is "
  "one cell. There is nothing to edit by accident, because the cell is collapsed and marked "
  "non-editable. And <i>Run All Cells</i> is a complete, unambiguous recovery instruction that "
  "works from any state the notebook can be in.<br><br>"
  "What it costs is the thing readers expect from notebooks — typing into cells — and that is "
  "given back deliberately in two places: the optional code fold under each exercise, and the "
  "empty cell at the very bottom, which is yours (chapter 7).<br><br>"
  "The price of the design is paid by the author, not the reader: the chapters live in separate "
  "Python files and a build script concatenates them into the one cell. The reader never sees "
  "that seam, which is the point.")

def _render_c01(step=4):
    stages = [
      ("the .ipynb file", "two cells on disk:\ntitle card + one code cell"),
      ("Run All Cells", "the browser starts Pyodide\nand hands it the cell"),
      ("the toolkit runs", "boxes, folds, checks,\nstylesheet, panel script"),
      ("the chapters run", "each build_chapter() call\nregisters itself and draws"),
      ("the panel appears", "the structure is complete,\nso the timeline is complete"),
    ]
    fig, ax = fixed_canvas(figsize=(7.2, 4.4), left=.02, right=.98, top=.95, bottom=.04)
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    y = 8.6
    for i, (head, body) in enumerate(stages):
        on = i <= step
        face = PAL["z"] if on else "#d9dee3"
        ink = "#ffffff" if on else "#8b98a5"
        ax.add_patch(plt.Rectangle((1.1, y - 1.25), 7.8, 1.35, facecolor=face,
                                   edgecolor="none", zorder=2,
                                   alpha=1.0 if on else .55))
        ax.text(1.45, y - .40, "%d. %s" % (i + 1, head), color=ink, fontsize=11,
                fontweight="bold", va="center", zorder=3)
        ax.text(5.3, y - .62, body, color=ink, fontsize=8.4, va="center", zorder=3,
                linespacing=1.45)
        if i < len(stages) - 1:
            ax.annotate("", xy=(5.0, y - 1.45), xytext=(5.0, y - 1.25),
                        arrowprops=dict(arrowstyle="-|>", color="#b6bfc8", lw=1.6))
        y -= 1.72
    return fig

def _read_c01(step=4):
    left = 4 - step
    return readout([("step", "%d of 5" % (step + 1)),
                    ("still to come", "%d" % left),
                    ("cells involved", "1"),
                    ("state on disk", "unchanged")])

viz = [viz_intro_box("",
    "Drag <b>step</b> through what happens when you press <i>Run All Cells</i>. Note that the "
    "file on disk never changes: the entire document you are reading is produced anew each "
    "time, from the same two cells. That is why the recovery instruction is so short — there "
    "is no accumulated state to repair.")]
viz += slider_plot(_render_c01, {"step": IntSlider(value=4, min=0, max=4, step=1,
                                                   description="step")},
                   readout_fn=_read_c01)

def _ans_c01(idx, label):
    if idx == 0:
        return True, ("Correct. The widgets are handles to objects in a Python process that "
                      "ended with the tab; your answers were never in that process.")
    if idx == 1:
        return False, ("The saved output is there, but a widget without its kernel is an empty "
                       "frame. Look again at what survives and what does not.")
    if idx == 2:
        return False, ("Nothing is lost: the file is untouched and your answers are in the "
                       "browser's storage, not in the kernel.")
    return False, ("The seed is redrawn on a fresh run, but that is not what the question asks "
                   "about — it asks what you must DO.")

practice = [
  exercise_box("", taskline(
    "<b>Try it for real before you answer.</b> Reload this page (F5). The interactive parts "
    "come back as placeholders. Run all cells again, then come back here and say what happened "
    "to your progress.")
    + "<div>If you would rather not reload right now, reason it through: which of the two — the "
      "live widgets, or your recorded answers — lives in the Python kernel?</div>"),
  choice_answer("After a reload and a fresh <i>Run All Cells</i>:",
    ["My answers are still recorded; only the widgets had to be rebuilt.",
     "Everything was restored from the saved output; nothing had to run again.",
     "My answers were lost together with the widgets.",
     "Only the exercise numbers were lost."],
    _ans_c01, task="t1"),
  code_fold(
    "# The notebook keeps its record under one key per notebook.\n"
    "# Write a function that returns the number of cells this document has.\n"
    "\n"
    "def cell_count():\n"
    "    return ...\n",
    lambda g: _check_c01(g), task="t1",
    solution="def cell_count():\n"
             "    return 2      # a markdown title card and one collapsed code cell\n"),
]

def _check_c01(g):
    f = g.get("cell_count")
    if not callable(f):
        return False, "Define a function called cell_count() that takes no arguments."
    try:
        v = f()
    except Exception as e:
        return False, "cell_count() raised %r." % (e,)
    if v == 2:
        return True, "Two: the markdown title card and the one collapsed code cell."
    if isinstance(v, int) and v > 2:
        return False, ("You are counting the chapters, not the cells. Everything below the "
                       "title is produced by a single cell.")
    return False, "Not quite — count what is in the .ipynb file, not what is on the screen."

interp = interpretation_box(
  "The document you are reading is <b>rendered, not stored</b>. That one decision is what makes "
  "<i>Run All Cells</i> a complete repair instruction, what makes the notebook safe to hand to "
  "someone who has never seen Jupyter, and what lets the timeline in chapter 5 know the whole "
  "structure — because by the time it is drawn, every chapter has already announced itself.")

build_chapter(1, "Two cells, and why", info=info, intro=_intro, viz=viz,
              practice=practice, interp=interp, task="t1")
