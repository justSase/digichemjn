_obj = [
 ("K3", "basic", "state what a set is and decide whether a given set is finite, "
                 "countably infinite or uncountable"),
 ("K3", "basic", "read and write the symbols ∈, ∉, ⊂, ∩, ∪, \\, ᶜ, ∅ and # correctly"),
 ("K4", "intermediate", "compute intersection, union, difference and complement of "
                        "concrete sets and say which of them are disjoint"),
 ("K4", "intermediate", "count the elements of a Cartesian product and explain why the "
                        "counts multiply"),
 ("K5", "intermediate", "apply the commutative, associative, distributive and De Morgan "
                        "rules, and verify one of them on an example rather than trusting it"),
 ("K3", "advanced", "place a number in ℕ ⊂ ℤ ⊂ ℚ ⊂ ℝ and name what each step adds, "
                    "and write an interval as a set with the right kind of bracket"),
 ("K4", "advanced", "evaluate Σ, Π, n! and the binomial coefficient, and explain why "
                    "'6 from 49' divides by 6! — that is, when order does not count"),
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
      "<div style='margin-top:14px;font-size:.93em'>Each objective is coupled to an exercise below "
      "and to the quiz in the appendix, so you can check every one of them yourself.<br><br>"
      "<b>No programming is required.</b> This is a <i>%s</i> notebook, and in that standard the "
      "objectives are the concepts and the critical check — not the implementation. Every exercise "
      "is solved by entering numbers, choosing an option or moving sliders. Each one additionally "
      "offers a closed, clearly marked <i>optional</i> code fold for anyone who wants to write it "
      "out in Python; it unlocks the same step and is never needed to get through.</div>"
      % (_rows, PROFILE["label"]),
      grey=True))
