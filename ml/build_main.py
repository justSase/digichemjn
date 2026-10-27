import json

import sys as _sys; _sys.path.insert(0, "../toolkit"); _sys.dont_write_bytecode = True
# 2026-09-28 (S) — the toolkit is assembled from chapter_template.py + css/ + js/
# by the Ladeteil; the text is the same one file it always was.
from assemble import template as _template
TEMPLATE    = _template()
import re as _re
# 2026-09-25 — THE VERSION GOES IN THE NAME, HERE TOO.
# Complex and Sets have carried it since 1.1 because the file name is the ONE
# place JupyterLite shows cold — before a kernel runs, a tooltip and the ⚙
# drawer show nothing. These three were the last without it, which meant a
# reader could not tell which build they had open until they ran it.
# Read from the toolkit, never typed: one source for the number.
NBV = _re.search(r'NB_VERSION = "([^"]+)"', TEMPLATE).group(1)
OUT = "Machine_Learning_LLMs_AI_Step_by_Step_v" + NBV + ".ipynb"

PROFILES    = open("../toolkit/profiles.py").read()
SETUP_EXTRA = open("chapters/_setup_extra.py").read()

# Both cells are locked: a stray double-click on the title used to un-render it
# into raw HTML, and there is no reason for a reader to edit or delete either one.
# (The panel script re-renders it as well, in case a front end ignores this.)
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

# ---- centred title banner (matches the blue chapter pills) ----
TITLE = (
  '<div style="text-align:center;margin:20px 0 6px">'
  '<div style="display:inline-block;background:linear-gradient(90deg,#33475a,#527189);color:#fff;'
  'padding:20px 48px;border-radius:16px;box-shadow:0 6px 18px rgba(51,71,90,.30)">'
  '<div style="font-size:1.95em;font-weight:800;letter-spacing:.4px">Machine Learning, LLMs &amp; AI</div>'
  '<div style="font-size:1.05em;font-weight:600;opacity:.92;margin-top:4px;letter-spacing:.5px">Explained Step by Step</div>'
  '</div>'
  '<div style="color:#5b6b7b;max-width:720px;margin:14px auto 0;font-style:italic;font-size:1.05em">'
  'From a single line to attention, building the intuition by editing code yourself</div>'
  '<div style="color:#33475b;max-width:720px;margin:12px auto 0;font-size:1.0em">'
  '<b>To start:</b> run the whole notebook once with the <b>Run all cells</b> button.</div>'
  '</div>')

# Package install — MUST stay a bare %pip magic so JupyterLite/Pyodide awaits it
# and the packages are ready before the imports below. It is the (collapsed) Setup
# cell; the friendly comment on line 1 is all that shows in the collapsed preview,
# so the pip command itself is no longer visible.
INSTALL = (
    "# DigiChemJN · Setup, installs packages, loads the toolkit, data & quiz, applies the style. "
    "Run this cell first; it stays collapsed.\n"
        '# The installer says nothing. pip prints a "Note: you may need to restart the\n# kernel" line (and, on some machines, a warning about the user it is running\n# as) straight into the cell\'s output — which lands directly under the title\n# page, above the document, and reads to a first-time reader as something\n# having gone wrong. It is captured; a real failure still speaks up.\ntry:\n    from IPython import get_ipython as _gi\n    from IPython.utils.capture import capture_output as _cap\n    with _cap():\n        _gi().run_line_magic(\n            "pip", "install -q --disable-pip-version-check "\n                   "numpy matplotlib ipywidgets jupyterquiz")\nexcept Exception:\n    try:\n        _gi().run_line_magic(\n            "pip", "install -q numpy matplotlib ipywidgets jupyterquiz")\n    except Exception as _e:\n        print("Could not install the packages automatically:", _e)\n'
)

# ---- order of the rendered sections (all render from the single hidden cell below) ----
# The table of contents (overview) stands on its own, then the chapters are
# organised into three collapsible GROUPS.
OVERVIEW    = "overview.py"
FOUNDATIONAL = ["setup.py", "howto.py", "teaches.py", "roadmap.py"]   # Grundlegend
# ch06.py (the standalone chemistry example) was removed; application examples now
# live in the interpretation boxes, and the hands-on chemistry case is the BYOD chapter.
CONTENT      = ["ch02.py", "ch03.py", "ch04.py", "ch05.py", "ch07.py", "ch08.py",
                "ch09.py", "ch10.py", "ch11.py", "ch12.py", "ch13.py", "ch14.py", "ch15.py"]
# "Remarks" (ch_limits, the red caveats box) is the first Resources item, then Summary, Glossary, …
ADVANCED     = ["ch_limits.py", "ch16.py", "glossary.py", "ch17.py", "ch18.py", "byod.py"]

def _src(fname):
    return "# ---- %s ----\n%s" % (fname, open("chapters/%s" % fname).read())

parts = [INSTALL, TEMPLATE, PROFILES, SETUP_EXTRA,
         "\n# ===== sections (all rendered from this one collapsed cell) ====="]

# the table of contents stands on its own, above the three groups
# (the "run all cells" button now lives in its own first cell)
parts.append(_src(OVERVIEW))

# GROUP 1 · Introduction (setup · how · what) — grey line header, collapsed by default
parts.append("group_start()")
for f in FOUNDATIONAL: parts.append(_src(f))
parts.append('group_end("Introduction", icon="👋", top_color="#8894a0", open_=False, anchor="grp_intro")')

# GROUP 2 · Content (the numbered chapters) — blue line header, open by default
parts.append("group_start()")
for f in CONTENT: parts.append(_src(f))
parts.append('group_end("Content", icon="📚", top_color="#2c6e91", anchor="grp_content")')

# GROUP 3 · Appendix (summary · glossary · references · quiz · byod) — grey, collapsed by default
parts.append("group_start()")
for f in ADVANCED: parts.append(_src(f))
parts.append('group_end("Appendix", icon="📑", top_color="#8894a0", open_=False, anchor="grp_appendix")')

MEGA = "\n\n".join(parts)

# 2026-09-24x — no third cell. The reader asked for it gone: a
# notebook of ours is the title and the machine, nothing else.
cells = [md(TITLE), code(MEGA, hide=True)]

nb = {"cells": cells,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python", "version": "3.8"}},
      "nbformat": 4, "nbformat_minor": 4}
json.dump(nb, open(OUT, "w"), ensure_ascii=False, indent=1)
print("built notebook with", len(cells), "cells")
