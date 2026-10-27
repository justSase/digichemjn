import json

import sys as _sys; _sys.path.insert(0, "../toolkit"); _sys.dont_write_bytecode = True
# 2026-09-28 (S) — the toolkit is assembled from chapter_template.py + css/ + js/
# by the Ladeteil; the text is the same one file it always was.
from assemble import template as _template
TEMPLATE = _template()
import re as _re
# 2026-09-25 — THE VERSION GOES IN THE NAME, HERE TOO.
# Complex and Sets have carried it since 1.1 because the file name is the ONE
# place JupyterLite shows cold — before a kernel runs, a tooltip and the ⚙
# drawer show nothing. These three were the last without it, which meant a
# reader could not tell which build they had open until they ran it.
# Read from the toolkit, never typed: one source for the number.
NBV = _re.search(r'NB_VERSION = "([^"]+)"', TEMPLATE).group(1)
OUT = "Start_Here_How_These_Notebooks_Work_v" + NBV + ".ipynb"

PROFILES = open("../toolkit/profiles.py").read()
SETUP    = open("chapters/_setup_00.py").read()

_LOCKED = {"editable": False, "deletable": False}

def code(src, hide=True):
    meta = dict(_LOCKED)
    if hide:
        meta.update({"jupyter": {"source_hidden": True}, "collapsed": True})
    return {"cell_type": "code", "execution_count": None, "metadata": meta,
            "outputs": [], "source": src.splitlines(keepends=True)}
def md(src):
    return {"cell_type": "markdown", "metadata": dict(_LOCKED),
            "source": src.splitlines(keepends=True)}

TITLE = (
  # A FULL PAGE, and a button that is there from the very first render.
  #
  # JupyterLab sanitises a markdown cell before it renders it: `script`,
  # `style`, `onclick` and every data- attribute are removed and `id` is
  # rewritten. `class` and inline `style` survive — so the button can carry its
  # shape and its place here, and the panel script gives it its function as soon
  # as the notebook has run once. Until then it stands next to the menu path it
  # names, which is the one instruction a first-time reader needs.
  '<div class="nbtitle nbcover" style="text-align:center;'
  'min-height:calc(100vh - 190px);display:flex;flex-direction:column;'
  'align-items:center;justify-content:center;gap:4px;padding:18px 0 40px">'
  '<div class="nbtitle-card" style="display:block;background:#f8fafb;'
  'border:1px solid #dde5ec;border-radius:16px;padding:40px 62px;width:96%;'
  'max-width:1100px;margin:0 auto;box-sizing:border-box">'
  '<div class="nbtitle-h" style="font-size:2.6em;font-weight:800;color:#33475b;'
  'line-height:1.12;letter-spacing:.2px">Start here</div>'
  '<div class="nbtitle-rule" style="width:62px;height:2px;border-radius:2px;'
  'background:#cbd5de;margin:15px auto 12px"></div>'
  '<div class="nbtitle-sub" style="color:#7a8794;font-size:.8em;font-weight:700;'
  'letter-spacing:2.4px;text-transform:uppercase;line-height:1.5">'
  'DigiChemJN &mdash; notebook 0 of the catalogue</div>'
  '</div>'
  '<div class="nbtitle-lead" style="color:#5b6b7b;max-width:860px;margin:22px auto 0;'
  'font-style:italic;font-size:1.1em">How these notebooks work &mdash; explained on '
  'the one page where every part of the machinery is switched on and in front of '
  'you</div>'
  '<div style="margin:30px auto 0">'
  '<span class="nbrunall" style="display:inline-flex;align-items:center;gap:12px;'
  'background:linear-gradient(180deg,#3aa76d,#2c8f66);color:#fff;font-weight:800;'
  'font-size:1.15em;letter-spacing:.3px;padding:16px 38px;border-radius:999px;'
  'cursor:pointer;box-shadow:0 6px 18px rgba(44,143,102,.34);'
  'border:1px solid #2c8f66">&#9654;&emsp;Run all cells</span>'
  '<div class="nbrunall-msg" style="color:#5b6b7b;font-size:.92em;'
  'margin-top:12px;min-height:1.2em"></div>'
  '</div>'
  '<div class="nbtitle-note" style="color:#33475b;max-width:720px;margin:10px auto 0">'
  'The button runs once the notebook has been started. The first time, use the '
  'menu: <b>Run &#9656; Run All Cells</b>. That is the only instruction you need; '
  'the rest of this notebook explains why.</div>'
  '<div class="nbtitle-fine" style="color:#8b98a5;max-width:720px;margin:14px auto 0;'
  'font-size:.9em">Reopened this notebook and see only <i>Loading widget&hellip;</i>? '
  'That is expected, and chapter 1 is about exactly that. Run all cells again and '
  'everything comes back, including your progress.'
  '</div></div>')

INSTALL = (
    "# DigiChemJN · Setup, installs packages, loads the toolkit, data & quiz, applies the style. "
    "Run this cell first; it stays collapsed.\n"
        '# The installer says nothing. pip prints a "Note: you may need to restart the\n# kernel" line (and, on some machines, a warning about the user it is running\n# as) straight into the cell\'s output — which lands directly under the title\n# page, above the document, and reads to a first-time reader as something\n# having gone wrong. It is captured; a real failure still speaks up.\ntry:\n    from IPython import get_ipython as _gi\n    from IPython.utils.capture import capture_output as _cap\n    with _cap():\n        _gi().run_line_magic(\n            "pip", "install -q --disable-pip-version-check "\n                   "numpy matplotlib ipywidgets jupyterquiz")\nexcept Exception:\n    try:\n        _gi().run_line_magic(\n            "pip", "install -q numpy matplotlib ipywidgets jupyterquiz")\n    except Exception as _e:\n        print("Could not install the packages automatically:", _e)\n'
)

PROGRESS     = "progress.py"
FOUNDATIONAL = ["setup.py", "controls.py", "howto.py", "teaches.py", "roadmap.py"]
CONTENT      = ["c01.py", "c02.py", "c03.py", "c04.py", "c05.py", "c06.py", "c07.py"]
APPENDIX     = ["summary.py", "glossary.py", "remarks.py", "refs.py", "quiz.py", "byod.py"]

def _src(fname):
    return "# ---- %s ----\n%s" % (fname, open("chapters/%s" % fname).read())

parts = [INSTALL, TEMPLATE, PROFILES, SETUP,
         "\n# ===== sections (all rendered from this one collapsed cell) ====="]
parts.append("group_start()")
for f in FOUNDATIONAL: parts.append(_src(f))
parts.append('group_end("Introduction", icon="👋", top_color="#8894a0", open_=True, anchor="grp_intro")')

parts.append("group_start()")
for f in CONTENT: parts.append(_src(f))
parts.append('group_end("Content", icon="📚", top_color="#2c6e91", anchor="grp_content")')

parts.append("group_start()")
for f in APPENDIX: parts.append(_src(f))
parts.append('group_end("Appendix", icon="📑", top_color="#8894a0", anchor="grp_appendix")')

parts.append("notebook_end()")
parts.append(_src(PROGRESS))

MEGA = "\n\n".join(parts)
# 2026-09-24x — no third cell. The reader asked for it gone: a
# notebook of ours is the title and the machine, nothing else.
cells = [md(TITLE), code(MEGA, hide=True)]
nb = {"cells": cells,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python", "version": "3.8"}},
      "nbformat": 4, "nbformat_minor": 4}
json.dump(nb, open(OUT, "w"),
          ensure_ascii=False, indent=1)
print("built start notebook with", len(cells), "cells;", len(MEGA), "chars in the mega-cell")
