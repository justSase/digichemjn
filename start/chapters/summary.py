_rows = [
 ("Run All Cells", "the complete operating manual, and the complete repair instruction"),
 ("two cells", "a title card and one collapsed cell; the document is rendered, not stored"),
 ("five parts", "key message · content box · 📊 visualisation · 📝 practice · interpretation"),
 ("one exercise", "per chapter, with your own numbers, drawn from your seed"),
 ("status + hint", "green or amber, then a hint aimed at what you actually entered"),
 ("difficulty", "changes the tolerance and whether hints appear — never what is asked"),
 ("skip / give up", "both settle an exercise and open the next chapter; neither is hidden"),
 ("locks", "pacing, not grading: the text is never locked and every lock has a button"),
 ("the rail", "table of contents, scrollbar and progress display in one column"),
 ("the marker", "where you are — drag it; the front end's own scrollbar is hidden"),
 ("Doc / Panel", "document size · rail width; double-click either to return to 100 %"),
 ("detail ladder", "labels 80 % · emoji 70 % · circles 58 % · bars 46 % · dots 35 %"),
 ("👤 progress code", "a copyable record; carry it by hand, never grade with it"),
 ("✓ ⤼ ✗", "solved · skipped · given up, kept apart on purpose, across the series"),
 ("CC BY-SA 4.0", "reuse it, change it, teach from it — credit it and keep it open"),
 ("the empty cell", "the guided part ends there; the notebook does not"),
]
_html = "".join(
  "<tr><td style='padding:5px 16px 5px 0;vertical-align:top;white-space:nowrap'><b>%s</b></td>"
  "<td style='padding:5px 0'>%s</td></tr>" % r for r in _rows)
build_chapter(None, "Summary", icon="📋", chapter_open=False, anchor="summary",
  info=note_box("The whole format in one screen:"
                "<table style='border-collapse:collapse;margin:12px auto 0'>%s</table>" % _html))
