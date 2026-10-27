import json, re

import sys as _sys; _sys.path.insert(0, "../toolkit"); _sys.dont_write_bytecode = True
# 2026-09-28 (S) — the toolkit is assembled from chapter_template.py + css/ + js/
# by the Ladeteil; the text is the same one file it always was.
from assemble import template as _template
TEMPLATE = _template()
PROFILES = open("../toolkit/profiles.py").read()
SETUP    = open("chapters/_setup_sets.py").read()

# 2026-09-24bc — THE BUILD STAMP GOES ON THE COLD PAGE TOO.
# The ⚙ drawer shows it, but the drawer only exists once the notebook has run.
# Reloading a notebook from disk is exactly the moment you want to know which
# build you are holding, and at that moment nothing has run — so the markdown
# title cell carries it as well. Taken from the toolkit itself, so it can
# never disagree with what was actually built in.
VERSION = re.search(r'TOOLKIT_VERSION = "([^"]+)"', TEMPLATE).group(1)
# 2026-09-25 — THE VERSION IS IN THE FILE'S NAME.
# "Which one am I looking at?" had no answer before the notebook had run: the
# build lived in a tooltip and in the gear drawer, and JupyterLite shows
# neither until the kernel is up. A name is visible in the file browser, in
# the tab and in the window title, cold, on every platform. Read from the
# toolkit so the name, the OER record and the drawer cannot disagree.
NBV = re.search(r'NB_VERSION = "([^"]+)"', TEMPLATE).group(1)

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

TITLE = (
  '<div class="nbtitle" style="text-align:center;margin:26px 0 8px">'
  # 2026-09-24an — the card is the width of the page BEFORE the notebook has
  # run too. Until the mega-cell injects the stylesheet, only these inline
  # styles exist, and `display:inline-block; max-width:92%` drew the narrow
  # centred box the reader saw on a cold open.
  # the box is the width of its title, on a cold open too (2026-09-24ap)
  '<div class="nbtitle-card" title="build ' + VERSION + '" style="display:inline-block;background:#f8fafb;'
  'border:1px solid #dde5ec;border-radius:16px;padding:32px 56px;'
  'max-width:94%;box-sizing:border-box">'
  '<div class="nbtitle-h" style="font-size:2.05em;font-weight:800;color:#33475b;'
  'line-height:1.15;letter-spacing:.2px">Sets</div>'
  '<div class="nbtitle-rule" style="width:62px;height:2px;border-radius:2px;'
  'background:#cbd5de;margin:13px auto 11px"></div>'
  '<div class="nbtitle-sub" style="color:#7a8794;font-size:.78em;font-weight:700;'
  'letter-spacing:2.4px;text-transform:uppercase;line-height:1.5">'
  'Principles of Biophysics &amp; Computational methods &mdash; section 1.1</div>'
  '</div>'
  '<div class="nbtitle-lead" style="color:#5b6b7b;max-width:720px;margin:18px auto 0;'
  'font-style:italic;font-size:1.06em">From “is it in, or is it not” to counting '
  'what is far too large to write down</div>'
  # NO BUTTON HERE, AND THE REASON IS MEASURED (2026-09-24an).
  # A <button onclick="…"> in a markdown cell renders, but JupyterLab's
  # sanitiser strips the handler: measured `onclick: false`, `handler: object`,
  # and clicking it started nothing. Markdown cannot carry behaviour, so a
  # button drawn here would be a control that does not control anything —
  # worse than none. The green ▶ belongs to the panel, which exists once the
  # notebook has run; until then the menu is the whole instruction.
    # 2026-09-24av — THE COLD PAGE IS A PREVIEW OF THE WARM ONE.
  # What the reader meets before the kernel has run used to be a title and two
  # paragraphs of apology. It is now a picture of the notebook they are about
  # to get: the three section bars, collapsed, in the same quiet style the
  # running document uses, and the closing line under them.
  #
  # The play button is a real button element with the class the panel's click
  # handler listens for. MEASURED (2026-09-24av): JupyterLab's markdown
  # sanitiser rewrites `id` to `data-jupyter-id` and strips `onclick`,
  # `onerror` and `javascript:` hrefs outright — so this markup can carry no
  # handler of its own. It carries a CLASS instead, and the class survives.
  # The button therefore comes alive exactly when our script is alive: after
  # the first run, and on a cold open of a TRUSTED notebook, where JupyterLab
  # re-executes the saved `application/javascript` output with no kernel at
  # all (measured: it does). Until then it is an instruction, and the line
  # under it says what to press.
  '<div class="nbcover" style="max-width:560px;margin:26px auto 0">'
  '<button class="nbbtn nbrunall nbcover-play" title="run the whole notebook" style="display:block;margin:0 auto;width:74px;height:74px;border-radius:50%;border:2px solid #8b98a5;background:transparent;color:#8b98a5;cursor:pointer;font-size:26px;line-height:1;padding:0 0 0 6px">&#9654;</button>'
  '<div class="nbcover-play-lab" style="margin-top:10px;font-size:.82em;font-weight:800;letter-spacing:2.4px;text-transform:uppercase;color:#8b98a5">Play</div>'
  '<div class="nbcover-hint" style="color:#8b98a5;font-size:.86em;margin-top:9px">'
  'runs every cell &mdash; or the menu <i>Run &#9656; Run All Cells</i></div>'
  '<div class="nbcover-map" style="margin:26px auto 0;text-align:center">'
  + "".join(
      '<div class="nbcover-bar" style="display:flex;align-items:center;gap:14px;'
      'justify-content:center;margin:20px auto;color:#8b98a5;font-size:1.02em;'
      'font-weight:800;letter-spacing:2px;text-transform:uppercase;'
      'width:520px;max-width:88%%">'
      '<span style="flex:0 1 120px;border-top:1px solid currentColor;opacity:.5"></span>'
      '<span>%s&ensp;%s</span>'
      '<span style="flex:0 1 120px;border-top:1px solid currentColor;opacity:.5"></span>'
      '</div>' % (ic, nm)
      for ic, nm in (("&#128075;", "Introduction"),
                     ("&#128218;", "Content"),
                     ("&#128209;", "Appendix")))
  + '</div>'
  '</div>'
  '</div>')

# 2026-09-24bh — THE HEADING IS PART OF THE DOCUMENT ONCE THE NOTEBOOK RUNS.
# The markdown cell above is what a COLD notebook shows — with no outputs it is
# the only thing there is — so it keeps the whole title page, cover and all.
# The mega-cell emits the card and its one line again at the top of its own
# output, and the panel then takes the markdown cell out of the flow: one
# title, in the document, with none of JupyterLab's cell furniture round it.
# Derived from TITLE rather than written twice, so the two can never disagree.
_cut = TITLE.index('<div class="nbcover"')
TITLE_CARD = TITLE[TITLE.index('>') + 1:_cut]

INSTALL = open("../toolkit/install_cell.py").read()

PROGRESS     = "progress.py"
FOUNDATIONAL = ["setup.py", "controls.py", "howto.py", "teaches.py", "roadmap.py"]
CONTENT      = ["c01.py", "c02.py", "c03.py", "c04.py", "c05.py", "c06.py", "c07.py"]
# The Appendix ends with the two sections the reader DOES something in — the quiz
# and their own data — so the two circles sit at the very end of the timeline.
# refs.py can therefore no longer be last in the build: its list is written by a
# finalizer once every chapter has run (see chapters/refs.py), which is what kept
# it last before.
# 'Remarks and limits' belongs next to the sources it qualifies, not in front of
# the summary: what a model cannot do reads as a footnote to the references.
APPENDIX     = ["summary.py", "glossary.py", "remarks.py", "refs.py",
                "quiz.py", "byod.py"]

def _src(fname):
    return "# ---- %s ----\n%s" % (fname, open("chapters/%s" % fname).read())

parts = [INSTALL, TEMPLATE, PROFILES, SETUP,
         # the heading, first thing in the document cell (2026-09-24bh)
         "title_card(%r)" % TITLE_CARD,
         "\n# ===== sections (all rendered from this one collapsed cell) ====="]
# The Contents chapter is gone: the pinned panel IS the table of contents now, and
# two of them could only drift apart.
parts.append("group_start()")
for f in FOUNDATIONAL: parts.append(_src(f))
parts.append('group_end("Introduction", icon="👋", top_color="#8894a0", open_=False, anchor="grp_intro")')

parts.append("group_start()")
for f in CONTENT: parts.append(_src(f))
parts.append('group_end("Content", icon="📚", top_color="#2c6e91", anchor="grp_content")')

parts.append("group_start()")
for f in APPENDIX: parts.append(_src(f))
# 2026-09-24aa — only Content is open when the notebook is opened. Introduction
# and Appendix are reference material; a reader who wants them opens them.
parts.append('group_end("Appendix", icon="📑", top_color="#8894a0", open_=False, anchor="grp_appendix")')

# the notebook's own end: a footer the reader can see and a bar that closes the
# timeline, so the last circle is no longer mistaken for "not reached yet"
parts.append("notebook_end()")

# the panel goes last: by now every chapter is registered, so it renders complete
parts.append(_src(PROGRESS))

MEGA = "\n\n".join(parts)
# 2026-09-24x — no third cell. The reader asked for it gone: a
# notebook of ours is the title and the machine, nothing else.
cells = [md(TITLE), code(MEGA, hide=True)]
nb = {"cells": cells,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python", "version": "3.8"}},
      "nbformat": 4, "nbformat_minor": 4}
OUT = "Sets_Step_by_Step_v" + NBV + ".ipynb"
json.dump(nb, open(OUT, "w"), ensure_ascii=False, indent=1)
print("built", OUT, "with", len(cells), "cells;", len(MEGA), "chars in the mega-cell")
