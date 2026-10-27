_qout = Output()
with _qout:
    try:
        from jupyterquiz import display_quiz
        display_quiz(QUIZ)
    except Exception as _e:
        display(IHTML("<div style='text-align:center'>Quiz unavailable: %r</div>" % (_e,)))
build_chapter(None, "Multiple choice quiz", icon="❓", chapter_open=False, anchor="quiz",
  body=[_qout, completion_button("q1", "I have worked through the quiz")], task="q1")
