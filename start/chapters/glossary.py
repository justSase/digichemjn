_g = [
 ("notebook", "a .ipynb file of cells; here always exactly two of them"),
 ("cell", "one unit of a notebook — markdown or code; ours is collapsed and locked"),
 ("kernel", "the Python process behind the page; it ends when the tab closes"),
 ("JupyterLite", "a Jupyter that runs entirely in the browser, with no server"),
 ("Pyodide", "CPython compiled to WebAssembly — the Python inside the browser"),
 ("widget", "an interactive control drawn by the kernel; empty without one"),
 ("toolkit", "chapter_template.py — the shared code every notebook is built from"),
 ("profile", "the subject standard: what the objectives are, whether code is required"),
 ("chapter", "one build_chapter() call: message, content, visualisation, practice"),
 ("fold", "a closed accordion — 📊 visualisation, 📝 practice, 💻 optional code"),
 ("task", "the identifier of one exercise; what a lock refers to"),
 ("lock", "a chapter waiting on a task, with an 'open anyway' button"),
 ("seed", "the number your exercise values are drawn from; printed in Setup"),
 ("tolerance", "how close a numeric answer must be; set by the difficulty"),
 ("rail / timeline", "the column on the right: contents, scrollbar and progress in one"),
 ("marker", "the bright bar on the rail — your position, and draggable"),
 ("detail ladder", "the fixed order in which the rail drops detail as it narrows"),
 ("progress code", "a copyable text record of your answers; not a login"),
 ("BYOD", "'bring your own data' — the editable section at the end of every notebook"),
 ("CC BY-SA", "the licence: reuse and change freely, credit, and stay open"),
]
_html = "".join(
  "<tr><td style='padding:4px 16px 4px 0;vertical-align:top;white-space:nowrap'><b>%s</b></td>"
  "<td style='padding:4px 0'>%s</td></tr>" % r for r in _g)
build_chapter(None, "Glossary", icon="📖", chapter_open=False, anchor="glossary",
  info=note_box("<table style='border-collapse:collapse;margin:4px auto 0'>%s</table>" % _html))
