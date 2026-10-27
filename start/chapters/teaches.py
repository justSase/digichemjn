_obj = [
 ("K1", "basic", "run a DigiChemJN notebook and get it back after closing the tab"),
 ("K1", "basic", "name the parts of a chapter — content box, visualisation, practice, "
                 "optional code — and say what each is for"),
 ("K3", "basic", "read the timeline rail: where you are, what is solved, skipped or still shut"),
 ("K4", "intermediate", "use the checking machinery deliberately: attempt, read the hint, "
                        "adjust the difficulty, skip or give up on purpose rather than by accident"),
 ("K5", "intermediate", "explain why the locks are pacing and not assessment, and what that "
                        "implies for how much a progress figure is worth"),
 ("K4", "intermediate", "carry your progress to another browser or device with the progress code"),
 ("K6", "advanced", "judge whether a given piece of teaching material fits this format, and "
                    "describe how you would restructure it if it did"),
]
OBJECTIVES = ["%s (%s, %s)" % (o[2], o[0], o[1]) for o in _obj]
_rows = "".join(
  "<tr><td style='padding:5px 14px 5px 0;vertical-align:top'><b class='nbaccent'>%s</b></td>"
  "<td style='padding:5px 14px 5px 0;vertical-align:top;white-space:nowrap'><i>%s</i></td>"
  "<td style='padding:5px 0'>%s</td></tr>" % o for o in _obj)

build_chapter(None, "What you will be able to do", icon="🎯", chapter_open=False,
    info=note_box(
      "After working through this notebook you can:"
      "<table style='border-collapse:collapse;margin:12px auto 0'>%s</table>"
      "<div style='margin-top:14px;font-size:.93em'>Every objective above is coupled to an "
      "exercise below and to the quiz in the appendix, so you can check each one yourself. "
      "That coupling is itself part of the format: in a <i>%s</i> notebook an objective that "
      "nothing tests does not get written down.<br><br>"
      "<b>No programming is required</b>, here or in any notebook of this standard. Exercises "
      "are solved by entering a number, choosing an option, or moving sliders until the picture "
      "says what was asked. Under each one sits a closed fold marked <i>optional: write it in "
      "code</i>, for anyone who would rather write the thing out in Python. It unlocks the same "
      "step, and skipping it costs nothing.</div>" % (_rows, PROFILE["label"]),
      grey=True))
