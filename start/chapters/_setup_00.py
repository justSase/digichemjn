# ---------------------------------------------------------------------------
# DigiChemJN · Notebook 0 — "Start here" — domain setup
# The notebook whose subject is the notebooks themselves. Everything a reader
# learns here is demonstrated on the page they are reading: the boxes, the
# folds, the exercises, the locks and the panel are not screenshots, they are
# the live objects.
# ---------------------------------------------------------------------------

use_profile("biophysics")
use_style("quiet")
set_notebook("start-here", "Start here")

set_metadata(
    thema="start.start-here",                # E39a: Katalog-Schlüssel (vorläufig, Nutzer entscheidet)
    kurse=[],
    title="Start here",
    subtitle="How a DigiChemJN notebook works — the first notebook of the catalogue",
    authors=["… Autor:innen bitte eintragen …"],
    institution="Fakultät für Chemie und Pharmazie, Albert-Ludwigs-Universität Freiburg",
    licence="CC BY-SA 4.0",
    licence_url="https://creativecommons.org/licenses/by-sa/4.0/",
    version="0.9 (pre-release)",
    date="2026-09",
    doi="",
    repo="",
    audience="Everyone opening a DigiChemJN notebook for the first time — "
             "students and teaching staff alike",
    prerequisites="None. No mathematics, no programming, no account.",
    duration="25–40 minutes",
    keywords=["OER", "Jupyter", "JupyterLite", "Pyodide", "ipywidgets",
              "self-assessment", "flipped classroom", "DigiChemJN", "onboarding"],
    source="DigiChemJN toolkit, chapter_template.py (TOOLKIT_VERSION %s)" % TOOLKIT_VERSION,
)
inject_style()

# --- personal task values --------------------------------------------------
# Same mechanism as every other notebook in the catalogue, and for the same
# reason: the reader should SEE that the numbers are theirs, here, on the one
# page where the mechanism itself is the subject.
ST_SEED = int(_NBID, 16) % 100000
_rng = np.random.default_rng(ST_SEED)

TV = dict(
    cells    = 2,                                     # every notebook has two
    chapters = int(_rng.integers(6, 13)),             # an imagined course
    solved   = int(_rng.integers(2, 6)),
    skipped  = int(_rng.integers(1, 4)),
)
TV["failed"] = int(_rng.integers(1, 3))
TV["open"]   = TV["chapters"] - TV["solved"] - TV["skipped"] - TV["failed"]
if TV["open"] < 1:                                    # keep the arithmetic sane
    TV["chapters"] = TV["solved"] + TV["skipped"] + TV["failed"] + 1
    TV["open"] = 1

# --- the tasks, declared up front so the progress strip is complete --------
# (key, label, anchor of the chapter the exercise lives in)
register_tasks([
    ("t1", "1 · two cells",        "ch1"),
    ("t2", "2 · anatomy",          "ch2"),
    ("t3", "3 · checking",         "ch3"),
    ("t4", "4 · locks",            "ch4"),
    ("t5", "5 · the rail",         "ch5"),
    ("t6", "6 · progress code",    "ch6"),
    ("t7", "7 · making it yours",  "ch7"),
    ("q1", "8 · multiple choice",  "quiz"),
    ("b1", "9 · your own chapter", "byod"),
])

# --- quiz ------------------------------------------------------------------
QUIZ = [
 {"question": "You close the browser tab and open the notebook again the next day. "
              "What do you see, and what do you do?",
  "type": "multiple_choice",
  "answers": [
    {"answer": "Placeholders instead of the widgets — run all cells again; the progress comes back.",
     "correct": True,
     "feedback": "Correct. The widgets live in the Python kernel, which ends with the tab. "
                 "The answers do not: they are in the browser's own storage."},
    {"answer": "Everything exactly as I left it, because notebooks save their output.",
     "correct": False,
     "feedback": "The output is saved, but a widget is only a handle to a living kernel. "
                 "Without the kernel it is an empty frame."},
    {"answer": "Nothing at all — the notebook has to be downloaded again.",
     "correct": False,
     "feedback": "No. The file is unchanged; only the kernel has to be restarted."},
    {"answer": "My progress is gone and I start from chapter 1.",
     "correct": False,
     "feedback": "Progress survives: it is stored per notebook in this browser, not in the kernel."}]},
 {"question": "What does a chapter's lock actually do?",
  "type": "multiple_choice",
  "answers": [
    {"answer": "It paces the reading and can always be opened anyway.", "correct": True,
     "feedback": "Exactly. It is a suggestion with a button, not a grade."},
    {"answer": "It reports to the lecturer who is behind.", "correct": False,
     "feedback": "Nothing is reported anywhere. There is no server."},
    {"answer": "It hides the chapter's text until the exercise is solved.", "correct": False,
     "feedback": "The text is never locked — only the interactive parts wait."},
    {"answer": "It prevents the notebook from being edited.", "correct": False,
     "feedback": "The notebook is CC BY-SA: editing it is the point."}]},
 {"question": "The reading marker on the right-hand rail is …",
  "type": "multiple_choice",
  "answers": [
    {"answer": "the notebook's scrollbar and its position indicator in one.",
     "correct": True,
     "feedback": "Correct — the front end's own scrollbar is hidden, because two bars "
                 "saying the same thing is one too many."},
    {"answer": "a decoration that follows the mouse.", "correct": False,
     "feedback": "Drag it: the document moves."},
    {"answer": "a progress bar for the exercises.", "correct": False,
     "feedback": "That is the green fill along the rail. The marker is about WHERE you are."},
    {"answer": "a loading indicator.", "correct": False,
     "feedback": "No — it is there for as long as the notebook is."}]},
 {"question": "Your progress code is best described as …",
  "type": "multiple_choice",
  "answers": [
    {"answer": "a short text that carries your answers to another browser.",
     "correct": True,
     "feedback": "Correct. You copy it out, you paste it in; nothing travels on its own."},
    {"answer": "a login.", "correct": False,
     "feedback": "There is no account and no password — and therefore nothing to lose."},
    {"answer": "a licence key that unlocks the notebook.", "correct": False,
     "feedback": "Everything is open already; the licence is CC BY-SA."},
    {"answer": "a link to a server that stores your results.", "correct": False,
     "feedback": "No server is involved at any point."}]},
 {"question": "Which of these is NOT required to run a DigiChemJN notebook?",
  "type": "multiple_choice",
  "answers": [
    {"answer": "A Python installation on your computer.", "correct": True,
     "feedback": "Correct — in JupyterLite the Python runs inside the browser itself."},
    {"answer": "A browser.", "correct": False, "feedback": "That one you do need."},
    {"answer": "The notebook file.", "correct": False, "feedback": "That one too."},
    {"answer": "Running the cells once.", "correct": False,
     "feedback": "Without that the notebook is an empty page."}]},
]

# --- bibliography ----------------------------------------------------------
BIB = {
 1: 'Project Jupyter, <i>JupyterLab Documentation</i>. '
    '<a href="https://jupyterlab.readthedocs.io/" target="_blank">jupyterlab.readthedocs.io</a>',
 2: 'Project Jupyter, <i>JupyterLite — Wasm powered Jupyter running in the browser</i>. '
    '<a href="https://jupyterlite.readthedocs.io/" target="_blank">jupyterlite.readthedocs.io</a>',
 3: 'Pyodide contributors, <i>Pyodide: Python distribution for the browser and Node.js '
    'based on WebAssembly</i>. '
    '<a href="https://pyodide.org/" target="_blank">pyodide.org</a>',
 4: 'Jupyter Widgets contributors, <i>ipywidgets: Interactive HTML Widgets</i>. '
    '<a href="https://ipywidgets.readthedocs.io/" target="_blank">ipywidgets.readthedocs.io</a>',
 5: 'J. Bergmann, A. Sams, <i>Flip Your Classroom: Reach Every Student in Every Class '
    'Every Day</i>, ISTE/ASCD, 2012. ISBN 978-1-56484-315-9.',
 6: 'M. D. Wilkinson et al., “The FAIR Guiding Principles for scientific data management '
    'and stewardship”, <i>Sci. Data</i> <b>3</b>, 160018 (2016). '
    'DOI: <a href="https://doi.org/10.1038/sdata.2016.18" target="_blank">10.1038/sdata.2016.18</a>',
 7: 'UNESCO, <i>Recommendation on Open Educational Resources (OER)</i>, Paris, 2019. '
    '<a href="https://www.unesco.org/en/legal-affairs/recommendation-open-educational-resources-oer" '
    'target="_blank">unesco.org</a>',
 8: 'Creative Commons, <i>Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)</i>. '
    '<a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank">creativecommons.org</a>',
 9: 'P. Black, D. Wiliam, “Assessment and Classroom Learning”, <i>Assessment in Education</i> '
    '<b>5</b>(1), 7–74 (1998). '
    'DOI: <a href="https://doi.org/10.1080/0969595980050102" target="_blank">10.1080/0969595980050102</a>',
10: 'H. F. Ebel, C. Bliefert, <i>Vortragen in Naturwissenschaft, Technik und Medizin</i>, '
    '3. Aufl., Wiley-VCH, 2008. ISBN 978-3-527-31225-6.',
}

notebook_start()
