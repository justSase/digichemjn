# render the quiz into an Output that becomes the chapter body, so it lives INSIDE
# the "Multiple-choice quiz" accordion and folds away with it
_quiz_out = Output(layout=Layout(width="100%"))
with _quiz_out:
    show_quiz()
build_chapter(None, "Multiple-choice quiz", info=_quiz_out, icon="❓", anchor="quiz",
              chapter_open=False)
