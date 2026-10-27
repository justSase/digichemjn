# the quiz renders into an Output that becomes the chapter body, so it folds with the card
_quiz_out = Output(layout=Layout(width="100%"))
with _quiz_out:
    show_quiz()
build_chapter(None, "Multiple-choice quiz", icon="❓", chapter_open=False, anchor="quiz",
  body=[_quiz_out, completion_button("q1", "I have worked through the quiz")], task="q1")
