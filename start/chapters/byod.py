_txt = (
  "Every notebook in this catalogue ends with a section you are expected to <b>change</b> rather "
  "than answer. In the subject notebooks it holds real constants — a membrane resistance, a rate "
  "coefficient, a data file of yours. Here, where the subject is the format itself, the thing to "
  "bring is <b>your own material</b>.<br><br>"
  "The block below is a chapter. Not a picture of one: the same five parts, written out in the "
  "one function call chapter 7 described, with a check function of its own. Change the title, "
  "the text, the number and the hints, run it, and a new chapter appears at the bottom of this "
  "notebook with its own entry on the rail and its own circle for its exercise.<br><br>"
  "<b>Start by changing only <code>MY_TITLE</code> and <code>MY_ANSWER</code>.</b> Then rewrite "
  "the two hint strings, which is where the actual teaching lives — one hint for the mistake you "
  "expect, one for everything else. If something breaks, the error appears under the block and "
  "the rest of the notebook carries on; <i>Run All Cells</i> restores the original.")

_code = '''# ---- a chapter of your own ------------------------------------------
MY_TITLE  = "Something I know about"
MY_ANSWER = 42.0          # the number you want the reader to arrive at
MY_UNIT   = ""            # e.g. "kJ/mol" — or leave it empty

MY_TEXT = ("Replace this paragraph with the idea. One or two sentences on what "
           "it is, and one on why it follows from what came before.")

MY_TASK = ("State the value asked for above, to two decimal places.")

def my_check(v):
    x = v["val"]
    if abs(x - MY_ANSWER) <= max(0.01, abs(MY_ANSWER)*tol()):
        return True, "Correct."
    if abs(x - MY_ANSWER/2) < 1e-6:
        return False, "That is half of it — a hint for the mistake you expect."
    return False, "Not yet. Say here which STEP to look at, never the answer."
# ----------------------------------------------------------------------

build_chapter(None, MY_TITLE, icon="\\U0001F9EA", anchor="mine",
    intro=note_box("<b>Your chapter.</b> Everything below was produced by the "
                   "same function call every other chapter in this notebook uses."),
    info=note_box(MY_TEXT),
    practice=[exercise_box("", taskline("<b>" + MY_TASK + "</b>")),
              numeric_answer([("val", "value " + MY_UNIT + " =")], my_check)],
    interp=interpretation_box("And the green box at the end says what it was for."))
'''

build_chapter(None, "Bring your own material: write a chapter", icon="🧪", chapter_open=False,
  anchor="byod", info=note_box(_txt),
  body=[editable_runner(_code, run_label="Build my chapter ▶", height="470px"),
        note_box("<b>Things to try.</b> Give the exercise a wrong-but-plausible value and write "
                 "the hint for it — that is the part of authoring that cannot be automated. "
                 "Then set the difficulty to <i>Strict</i> and answer your own exercise: the "
                 "tolerance in <code>my_check</code> follows the setting, because it asks "
                 "<code>tol()</code> rather than hard-coding a number. Finally, note what you "
                 "did <i>not</i> have to write: no styling, no accordion, no lock, no entry on "
                 "the rail. That is what the toolkit is for."),
        completion_button("b1", "I have built a chapter of my own")], task="b1")
