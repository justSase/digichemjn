# The goals are declared in _setup_mod.py (register_goals) — one source for
# this table, the OER record and the title card.
_rows = goals_table_html()

build_chapter(None, "What you will be able to do", icon="🎯", chapter_open=False, anchor="teaches",
    info=note_box(
      "This notebook turns the lecture <b>Introduction to Modeling</b> into an interactive module. "
      "You build intuition by moving sliders and checking numbers on a small, realistic "
      "<b>pharmacokinetic</b> model (how a drug's concentration in the body changes over time). "
      "It leads from first perception to calibration, validation and "
      "sensitivity analysis. After working through it, you can:"
      "<table style='border-collapse:collapse;margin:12px auto 0'>%s</table>"
      "<div style='margin-top:14px;font-size:.93em'>Each objective belongs to an exercise below. "
      "This way you can check every one of them yourself.<br><br>"
      "<b>No programming is required.</b> This is a <i>%s</i> notebook: you solve every exercise by "
      "entering numbers. Each exercise also has a closed, clearly marked <i>optional</i> code "
      "fold if you want to write it out in Python. It unlocks the same step, and you never "
      "need it to get through.</div>" % (_rows, PROFILE["label"]),
      grey=True))
