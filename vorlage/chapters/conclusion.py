# E30 A1 (2026-10-12) — THE CONCLUSION IS A TEXT, as at the end of a paper
# (Nutzer 12.10.): what the chapters established, where it stands, an outlook —
# in paragraphs, no list (toolkit: conclusion()). Replace the three sample
# paragraphs; keep the order. The glossary is its own box below (optional).
_terms = [("term 1", "explanation (placeholder)")]
def _table(rows, pad):
    return ("<table style='border-collapse:collapse;margin:12px auto 0'>%s</table>" % "".join(
        "<tr><td style='padding:%s 16px %s 0;vertical-align:top;white-space:nowrap'><b>%s</b></td>"
        "<td style='padding:%s 0'>%s</td></tr>" % (pad, pad, a, pad, b) for a, b in rows))
build_chapter(None, "Conclusion", icon="📋", chapter_open=False, anchor="conclusion",
  info=conclusion(
    ["Summary (placeholder). In full sentences, what the chapters established and how they build on each other: "
     "the first chapter introduced the idea and its formula, the second applied it to a picture, and the "
     "exercises practised the step that matters. Write it as one line of argument, not as a list of topics."],
    context="Context (placeholder). Where the result stands: what it means for the lecture, the lab or a "
            "neighbouring field, which assumption it rests on, and what it does not cover.",
    outlook="Outlook (placeholder). What comes next: the question this notebook leaves open, the notebook "
            "that follows in the series, and one thing to try on your own with the code of the exercises."),
  body=[note_box("<b>Glossary</b>" + _table(_terms, "4px"))])
