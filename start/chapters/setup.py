_seed_html = (
  "<div style='text-align:center;margin-top:12px;font-weight:700'>"
  "Your personal task seed: <span class='nbaccent'>%d</span></div>"
  "<div style='text-align:center;font-size:.92em;margin-top:2px'>"
  "Every notebook in this catalogue draws its exercise values from a seed like this one, "
  "so the numbers on your screen are yours. Running the notebook again draws a fresh set."
  "</div>" % ST_SEED)

build_chapter(None, "What is actually running here", icon="⚙️", chapter_open=False,
    info=note_box(
      "Nothing is installed and nothing is signed into. This page is a <b>Jupyter notebook</b>"
      + cite(1) + " executed by <b>JupyterLite</b>" + cite(2) + ", which means the Python "
      "interpreter itself — <b>Pyodide</b>, a build of CPython compiled to WebAssembly"
      + cite(3) + " — is running inside your browser tab. There is no server doing the work "
      "for you, which has three consequences worth knowing from the start:<br><br>"
      "<b>Nothing you type leaves your machine.</b> Your answers, your seed and your progress "
      "stay in this browser's own storage. That is a privacy property, and it is also the "
      "reason there is no login.<br><br>"
      "<b>The first run is the slow one.</b> The interpreter and the libraries have to be "
      "fetched once; afterwards the browser caches them.<br><br>"
      "<b>Closing the tab ends the Python.</b> The notebook file is untouched and your answers "
      "survive, but the live widgets do not — run all cells again and they come back. "
      "Chapter 1 shows exactly why."
      + _seed_html, grey=True))
