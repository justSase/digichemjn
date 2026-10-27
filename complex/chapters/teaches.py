# The goals are declared in _setup_cx.py (register_goals) — one source for
# this table, the OER record and the title card (R2 · 15, Inhalt A).
_rows = goals_table_html()

build_chapter(None, "What you will be able to do", icon="🎯", chapter_open=False,
    info=note_box(
      "After working through this notebook, you can:"
      "<table style='border-collapse:collapse;margin:12px auto 0'>%s</table>"
      "<div style='margin-top:14px;font-size:.93em'>Each objective belongs to an exercise below. "
      "So you can check every one of them yourself.<br><br>"
      "<b>No programming is required.</b> This is a <i>%s</i> notebook. In this standard, the "
      "objectives are the concepts, the physics and the critical check, not the implementation. "
      "You solve every exercise by entering numbers, choosing an option or moving sliders. Each "
      "exercise also has a clearly marked <i>optional</i> code fold, closed at first, for anyone who "
      "wants to write the formula in Python. It unlocks the same step, and you never need it to get "
      "through.</div>" % (_rows, PROFILE["label"]),
      grey=True))
