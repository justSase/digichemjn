_intro = note_box(
  "The last thing the format does is get out of the way. This chapter is about the parts of the "
  "notebook that are addressed to you as an author rather than as a reader.")

info = note_box(
  "<b>The licence.</b> Every notebook in this catalogue is <b>CC BY-SA 4.0</b>" + cite(8) + ": "
  "you may copy it, change it, translate it, cut it up and teach from the pieces, commercially "
  "or not, on two conditions — credit the source, and pass the result on under the same licence. "
  "That second condition is what keeps a teaching catalogue from being quietly enclosed, and it "
  "is the reason the full metadata record sits in the appendix of every notebook, ready to be "
  "cited" + cite(7) + ".<br><br>"
  "<b>The empty cell at the bottom.</b> Jupyter always leaves one more cell under the document. "
  "In this format it is not an oversight and the timeline gives it a bar of its own: it is where "
  "the guided part stops and yours begins. Import what the notebook already loaded, plot "
  "something the author did not think of, check a claim from the text against your own numbers.<br><br>"
  "<b>Bring your own data.</b> The last section of the appendix is always an editable block of "
  "real code with real constants in it. Replace them and re-run. The section exists so that "
  "there is one place in every notebook where the reader is expected to change something rather "
  "than answer something.<br><br>"
  "<b>Writing a chapter.</b> Authoring is one function call. <code>build_chapter(n, title, "
  "intro=…, info=…, viz=…, practice=…, interp=…)</code> takes the five parts of chapter 2 and "
  "produces a chapter that is indistinguishable from the ones here: the same boxes, the same "
  "folds, an entry on the rail, a circle for its exercise and a place in the lock chain. You "
  "supply the physics and the hints; the toolkit supplies everything else. Adding a chapter to "
  "a notebook is adding one file and one line to the build script.")

_code = '''# Your own cell, a chapter early. Everything the notebook loaded is here:
# numpy as np, matplotlib.pyplot as plt, and the toolkit's own helpers.

import numpy as np

# --- change these three lines ------------------------------------------
label   = "my first plot"
n       = 200
noise   = 0.25
# -----------------------------------------------------------------------

x = np.linspace(0, 4*np.pi, n)
y = np.sin(x) + noise*np.random.default_rng(ST_SEED).normal(size=n)

fig, ax = fixed_canvas(figsize=(7.2, 3.4))
theme_axes(ax)
ax.plot(x, y, lw=1.6, color=PAL["z2"], label=label)
ax.plot(x, np.sin(x), lw=2.2, color=PAL["z"], label="without the noise")
ax.set_xlabel("x"); ax.set_ylabel("y")
theme_legend(ax, loc="upper right", fontsize=9)

print("drew %d points with noise %.2f, seeded from THIS notebook (%d)"
      % (n, noise, ST_SEED))
'''

def _ans_c07(idx, label):
    if idx == 1:
        return True, ("Correct. BY is the attribution, SA is the obligation to pass your version "
                      "on under the same terms — that is what keeps the catalogue open.")
    if idx == 0:
        return False, ("Commercial use is explicitly allowed by CC BY-SA. The restriction you "
                       "are thinking of is the NC clause, which this licence does not have.")
    if idx == 2:
        return False, ("You may change it freely — that is the whole point of the empty cell and "
                       "of the build script being part of the material.")
    return False, ("Attribution is required, but it is not the only condition. Look at what the "
                   "second half of the licence name asks for.")

practice = [
  exercise_box("", taskline(
    "<b>Run the block above at least once, with one of the three values changed.</b> Then answer "
    "the question about the licence that lets you do this — and about what it asks in return.")),
  choice_answer("Under CC BY-SA 4.0 I may reuse this notebook provided that …",
    ["… I do not use it commercially.",
     "… I credit the source and license my version under the same terms.",
     "… I do not change it.",
     "… I credit the source; there is no other condition."],
    _ans_c07, task="t7"),
]

interp = interpretation_box(
  "A teaching notebook that cannot be taken apart is a video with extra steps. The two cells, "
  "the build script, the licence and the empty cell at the bottom all point the same way: this "
  "is <b>material</b>, not a product. The most useful thing you can do after finishing a "
  "notebook is to change one chapter of it and hand it to somebody else.")

build_chapter(7, "Making it yours", info=info, intro=_intro,
              body=[editable_runner(_code, run_label="Run ▶", height="430px")],
              practice=practice, interp=interp, task="t7", locked_by="t6")
