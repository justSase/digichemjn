import json, re

import sys as _sys; _sys.path.insert(0, "../toolkit"); _sys.dont_write_bytecode = True
# 2026-09-28 (S) — the toolkit is assembled from chapter_template.py + css/ + js/
# by the Ladeteil; the text is the same one file it always was.
from assemble import template as _template
TEMPLATE = _template()
PROFILES = open("../toolkit/profiles.py").read()
SETUP    = open("chapters/_setup_cx.py").read()

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

# E19.4 (2026-10-02, Applikation) — NO CODE LINE ON OPENING, WHEREVER IT IS
# OPENED. JupyterLab, Notebook 7, JupyterLite and VS Code read
# `jupyter.source_hidden`; Colab hides the code of a cell only in its form
# view: `cellView: "form"` and a first line `#@title` (the title is what the
# folded cell shows there, as the first comment line is in JupyterLab).
def code(src, hide=True):
    meta = dict(_LOCKED)
    if hide:
        meta.update({"jupyter": {"source_hidden": True}, "collapsed": True, "cellView": "form"})
        if not src.startswith("#@title"):
            src = "#@title " + src[1:].lstrip() if src.startswith("#") else src
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
  # E21.7 — no build stamp on the card (it was its hover title); the version
  # is one small line in the ⚙ drawer, nowhere else
  '<div class="nbtitle-card" style="display:inline-block;background:#f8fafb;'
  'border:1px solid #dde5ec;border-radius:16px;padding:32px 56px;'
  'max-width:94%;box-sizing:border-box">'
  '<div class="nbtitle-h" style="font-size:2.05em;font-weight:800;color:#33475b;'
  'line-height:1.15;letter-spacing:.2px">Complex Numbers</div>'
  '<div class="nbtitle-rule" style="width:62px;height:2px;border-radius:2px;'
  'background:#cbd5de;margin:13px auto 11px"></div>'
  '<div class="nbtitle-sub" style="color:#7a8794;font-size:.78em;font-weight:700;'
  'letter-spacing:2.4px;text-transform:uppercase;line-height:1.5">'
  'Principles of Biophysics &amp; Computational methods &mdash; section 1.2</div>'
  '</div>'
  '<div class="nbtitle-lead" style="color:#5b6b7b;max-width:720px;margin:18px auto 0;'
  'font-style:italic;font-size:1.06em">From one impossible equation to rotation in '
  'the plane, built up by editing code yourself</div>'
  # 2026-09-28 (R2 · Paket 15, Inhalt A) — goals, chapters and time budget,
  # filled below from the notebook itself (card_facts), in BOTH cards
  '<!--NBFACTS-->'
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
  # 2026-09-28 (R2 · Paket 14, Struktur) — THE COVER REACHES THE BOTTOM.
  # Before Play nothing of ours runs: this cell is all there is, and under it
  # JupyterLab drew the first line of the hidden mega-cell ("# DigiChemJN ·
  # Setup…") in the middle of the page. The cover is therefore taller than
  # any window, so that line is below the fold. The sanitiser keeps
  # `min-height` only in px/em (no vh — measured in its allow-list), hence a
  # fixed 1400 px. Once the notebook runs, the stylesheet sets it back to 0
  # (`.jp-Cell .nbcover{min-height:0!important}`) and the cell is hidden.
  # E8.21 (2026-09-29, Struktur) — the cover is as wide as its flat timeline
  # (940 px); Play, its label and the hint are centred in it as before.
  # E21.6 (JS): the cover says whose it is — `nbid-<id>` (the sanitizer keeps classes)
  '<div class="nbcover nbid-complex-numbers" style="max-width:940px;margin:26px auto 0">'
  '<button class="nbbtn nbrunall nbcover-play" title="run the whole notebook" style="display:block;margin:0 auto;width:74px;height:74px;border-radius:50%;border:2px solid #8b98a5;background:transparent;color:#8b98a5;cursor:pointer;font-size:26px;line-height:1;padding:0 0 0 6px">&#9654;</button>'
  '<div class="nbcover-play-lab" style="margin-top:10px;font-size:.82em;font-weight:800;letter-spacing:2.4px;text-transform:uppercase;color:#8b98a5">Play</div>'
  '<div class="nbcover-hint" style="color:#8b98a5;font-size:.86em;margin-top:9px">'
  'runs every cell &mdash; or the menu <i>Run &#9656; Run All Cells</i></div>'
  # E23.0 / E23.16a — the "no document?" box went with the cold cover (E24.3):
  # the start line of the markdown cell says it now
  # E5.3 (2026-09-28, Struktur + Inhalt) — instead of the three section bars,
  # a foldable miniature of the WHOLE timeline, filled below from the same
  # run that fills the card (card_facts → card_timeline_html).
  '<div class="nbcover-map" style="margin:26px auto 0;text-align:center"><!--NBTIMELINE-->'
  # E5.2 — the 1400-px room under the cover is gone (E24.3): the cover is an
  # output now, and nothing below it has to be pushed out of sight
  + '</div>'
  '</div>'
  '</div>')

# E24.3 (2026-10-06, Python) — THE FIRST START IS AN ORDINARY NOTEBOOK.
# Nothing of ours runs before the first run on a stranger's machine (an
# untrusted notebook executes no saved script; markdown never does), so the
# cover drawn in the markdown cell offered a Play that could not play, a
# timeline nobody could click (office PC, 06.10.). The markdown cell is now ONE
# line that says the one thing that works, en and de; under it the code cell,
# collapsed to its first line. The cover — card, goals, Play, mode, language,
# login, timeline — is an OUTPUT of that cell (below, "<!--NBCOVER-->"):
# it exists only where our script runs, so everything on it works at once.
# Class `nbtitle` keeps the line the "title cell" the page script takes out of
# the flow once the document exists (19-rail markTitleCell).
# E25.c (2026-10-08, Python) — THE START LINE IS PLAIN MARKDOWN. In PyCharm
# (Video 08.10.) the line stood top right beside the tool bar instead of over
# the cell: its renderer laid out our HTML block (a <div> with inline style)
# on its own. Now a paragraph of ordinary Markdown — every front end puts it
# in the flow, over the cell — with one inline <span> that carries the classes
# the page and the tests know (.nbtitle: the title cell; .nbstart).
START_LINE = (
  '<span class="nbtitle nbstart">&#9654;&ensp;**Run the cell below** (or *Run &#9656; Run All Cells*)'
  '&ensp;&middot;&ensp;&#9654;&ensp;**F&uuml;hren Sie die Zelle darunter aus** (oder *Run &#9656; Run All Cells*)</span>')
COVER_MARK = 'display(IHTML("<!--NBCOVER-->"))'

# 2026-09-24bh — THE HEADING IS PART OF THE DOCUMENT ONCE THE NOTEBOOK RUNS.
# The markdown cell above is what a COLD notebook shows — with no outputs it is
# the only thing there is — so it keeps the whole title page, cover and all.
# The mega-cell emits the card and its one line again at the top of its own
# output, and the panel then takes the markdown cell out of the flow: one
# title, in the document, with none of JupyterLab's cell furniture round it.
# Derived from TITLE rather than written twice, so the two can never disagree.
_cut = TITLE.index('<div class="nbcover')
TITLE_CARD = TITLE[TITLE.index('>') + 1:_cut]

INSTALL = open("../toolkit/install_cell.py").read()
# E5.1 (2026-09-28, Applikation) — THE LOADING VIEW COMES FIRST. It is the
# toolkit's js/02-loading.js (the same text loading_screen() shows), but put
# in front of the installer: the installer imports numpy, matplotlib and
# ipywidgets, and until the first output the reader watched JupyterLab jump
# to the running cell. Only IPython is needed to show it. The installer's two
# comment lines stay first — they are what the collapsed cell reads.
_ih = INSTALL.split("\n", 2)
INSTALL_HEAD, INSTALL_REST = "\n".join(_ih[:2]), _ih[2]
_LOADJS = open("../toolkit/js/02-loading.js", encoding="utf-8").read().replace("__NBLOADV__", VERSION)
# E35 J1 (JavaScript): the notebook's id into the loading script — the cold cell carries none, and the
# script sets the reader's stored style/light-dark (keys `<key>.<id>`) before the first picture
_LOADJS = _LOADJS.replace("__NBIDEARLY__", re.search(r'nbid-([a-z0-9-]+)', TITLE).group(1))
assert '"""' not in _LOADJS
# E10.8 (2026-09-30, Applikation) — minified like the toolkit's other
# scripts (assemble), and in the cell ONCE: kept as _NBLOADJS, which the
# toolkit's loading_screen() shows too instead of its own copy (6.7 KB).
from assemble import _min_js
_LOADJS = _min_js(_LOADJS)
EARLY_LOAD = ('_NBLOADJS = r"""\n' + _LOADJS + '"""\n'
              'try:\n    from IPython.display import display as _nbd, Javascript as _nbJ\n'
              # E22.3 — empty text/plain: a front end without JS (PyCharm) shows no placeholder
              # E26.1 — with a display id: the reading version's end (_nbread_end) empties it,
              # so the cell's first visible output is the reading version
              '    _NBLOADID = "nbload-" + __import__("uuid").uuid4().hex\n'
              '    _nbd({"application/javascript": _NBLOADJS, "text/plain": ""}, raw=True, display_id=_NBLOADID)\nexcept Exception:\n    pass')
_LSJS = re.compile(r'r"""\n(?:(?!""").)*?"""\.replace\("__NBLOADV__", TOOLKIT_VERSION\)', re.S)
assert len(_LSJS.findall(TEMPLATE)) == 1
TEMPLATE = _LSJS.sub("_NBLOADJS", TEMPLATE)

# E17.1 (2026-10-02, Inhalt + Applikation) — ENGLISH AND GERMAN IN ONE CELL.
# Every reader-facing literal with an entry in toolkit/de.txt (toolkit) or
# chapters/de.txt (this notebook) becomes _nbL(english, german), chosen when
# the cell runs (LANG, toolkit). Each source is translated with its own
# tables only, so a short word cannot change code elsewhere. See i18n.py.
import i18n as _i18n
_DE_TK = _i18n.load("../toolkit/de.txt")
_DE_NB = _i18n.load("chapters/de.txt")
_USED = set()
def _tr(src, *tables, where="?"):
    out, used = _i18n.translate(src, *tables, where=where)
    _USED.update(used)
    return out
TEMPLATE = _tr(TEMPLATE, _DE_TK, where="toolkit")
if "def _nbL(" not in TEMPLATE:          # a toolkit without E17.5
    TEMPLATE = _i18n.FALLBACK + TEMPLATE
PROFILES = _tr(PROFILES, _DE_TK, where="profiles")
SETUP = _tr(SETUP, _DE_TK, _DE_NB, where="_setup_cx.py")

PROGRESS     = "progress.py"
# E21.13 — no Setup chapter any more (Nutzer); what it said that a reader
# still needs is in the Conclusion, the seed is in the ⚙ drawer
FOUNDATIONAL = ["controls.py", "howto.py", "teaches.py", "roadmap.py"]
CONTENT      = ["c01.py", "c02.py", "c03.py", "c04.py", "c05.py", "c06.py", "c07.py"]
# The Appendix ends with the two sections the reader DOES something in — the quiz
# and their own data — so the two circles sit at the very end of the timeline.
# refs.py can therefore no longer be last in the build: its list is written by a
# finalizer once every chapter has run (see chapters/refs.py), which is what kept
# it last before.
# E19.8 — no 'Remarks and limits' section any more: each remark sits, as a red
# box, in the chapter it qualifies (c05, c06, setup, summary).
# E21.13 — Summary + Glossary are one chapter, "Conclusion"
# E25.l (2026-10-08, Python) — MULTIPLE CHOICE AND OWN DATA OUT FOR NOW, in
# every mode (timeline, cover, document, gating, progress follow from what is
# built). The sources stay: own data becomes the base of the data café later.
# Replaces E23.5.
APPENDIX     = ["conclusion.py", "refs.py"]

def _src(fname):
    return "# ---- %s ----\n%s" % (fname, _tr(open("chapters/%s" % fname).read(),
                                            _DE_TK, _DE_NB, where=fname))

# E25.o — the notebook's id before the toolkit: the language is stored per notebook
_NB_ID_EARLY = re.search(r'nbid-([a-z0-9-]+)', TITLE).group(1)
parts = [INSTALL_HEAD, EARLY_LOAD, INSTALL_REST, "_NB_ID_EARLY = %r" % _NB_ID_EARLY, TEMPLATE, "#@NBMATHPRE", PROFILES, SETUP,
         # the heading, first thing in the document cell (2026-09-24bh)
         "title_card(%r)" % TITLE_CARD,
         "\n# ===== sections (all rendered from this one collapsed cell) ====="]
# The Contents chapter is gone: the pinned panel IS the table of contents now, and
# two of them could only drift apart.
parts.append("group_start()")
for f in FOUNDATIONAL: parts.append(_src(f))
parts.append(_tr('group_end("Introduction", icon="👋", top_color="#8894a0", open_=False, anchor="grp_intro")', _DE_TK, where='build'))

parts.append("group_start()")
for f in CONTENT: parts.append(_src(f))
parts.append(_tr('group_end("Content", icon="📚", top_color="#2c6e91", anchor="grp_content")', _DE_TK, where='build'))

parts.append("group_start()")
for f in APPENDIX: parts.append(_src(f))
# 2026-09-24aa — only Content is open when the notebook is opened. Introduction
# and Appendix are reference material; a reader who wants them opens them.
parts.append(_tr('group_end("Appendix", icon="📑", top_color="#8894a0", open_=False, anchor="grp_appendix")', _DE_TK, where='build'))

# the notebook's own end: a footer the reader can see and a bar that closes the
# timeline, so the last circle is no longer mistaken for "not reached yet"
parts.append("notebook_end()")

# the panel goes last: by now every chapter is registered, so it renders complete
parts.append(_src(PROGRESS))
# E24.3 — the cover (filled in below). LAST in the cell, not first: the page
# script and the gate take the first .nbtitle-card of the output for the
# document's title card (measured: B1/J1 "no card to click", C22.8 "title card
# not drawn" with the cover in front). Where and when it shows is the page's
# business (JS); in a running notebook the stylesheet keeps it out (06-marks).
parts.append(COVER_MARK)

MEGA = "\n\n".join(parts)

# 2026-09-29 (Paket 21a, Applikation) — THE FORMULAS ARE TYPESET HERE, NOT IN
# THE KERNEL. The build runs the cell for three fixed seeds and writes every
# formula that does not depend on the seed into the cell as SVG (see
# toolkit/math_pre.py). The marker is an inert comment until then.
from math_pre import math_pre_code
_MATHPRE, _n_pre, _n_rt = math_pre_code(MEGA)
assert MEGA.count("#@NBMATHPRE") == 1
MEGA = MEGA.replace("#@NBMATHPRE", _MATHPRE)

# 2026-09-28 (R2 · Paket 15, Inhalt A) — THE CARD SAYS WHAT IS INSIDE, AND THE
# NOTEBOOK SAYS IT. The build runs the mega-cell once headless (the marker is an
# inert comment), asks card_facts(), and writes the answer into BOTH cards — the
# markdown one and the one the mega-cell draws — so cold and warm cannot disagree.
from card_facts import facts_html
_FACTS_HTML, FACTS = facts_html(MEGA)
_old_call = "title_card(%r)" % TITLE_CARD
assert MEGA.count(_old_call) == 1
_TITLE_T = TITLE                     # E26.3: the template, for the German cover of the window
TITLE = TITLE.replace("<!--NBFACTS-->", _FACTS_HTML)
assert TITLE.count("<!--NBTIMELINE-->") == 1
TITLE = TITLE.replace("<!--NBTIMELINE-->", FACTS["timeline_html"])
# E8.17 (2026-09-29, Struktur) — AFTER PLAY ONLY THE SUBTITLE. In the running
# document the title pill is followed by its one italic line and then the
# Introduction: goals, chapters and time stay on the cold cover (and in the
# panel, which is the table of contents). The warm card drops the facts block.
TITLE_CARD = TITLE_CARD.replace("<!--NBFACTS-->", "")
# E17.1 — the warm card in German, and with it what the page needs to put the
# cold cover into German after Play (rows of the cover timeline, cards, facts):
# the build runs the cell a second time in German to ask it.
import os as _os
_os.environ["DIGICHEM_LANG"] = "de"
try:
    _FACTS_HTML_DE, FACTS_DE = facts_html(MEGA, quiet=True)
finally:
    del _os.environ["DIGICHEM_LANG"]
from card_facts import card_desc as _card_desc, desc_key as _desc_key
_COVER_DE = _i18n.cover_map(FACTS["timeline"], FACTS_DE["timeline"], _desc_key,
                            _card_desc("", "chapters/cards.de.txt"), _FACTS_HTML_DE,
                            {"tl": "Zeitleiste &middot; %d Kapitel &middot; %d Aufgaben &middot; %d Code"
                                   % (FACTS["timeline_html"].count("nbtl-row nbtl-chapter"),
                                      FACTS["timeline_html"].count(" nbtl-calc"),
                                      FACTS["timeline_html"].count(" nbtl-code")),
                             "play": "Start",
                             "hint": "führt alle Zellen aus &mdash; oder im Menü <i>Run &#9656; Run All Cells</i>"})
TITLE_CARD_DE = _i18n.title_de(TITLE_CARD, _DE_NB)
_USED.update(k for k in _DE_NB if len(k) > 8 and k in TITLE_CARD)
# the map for the page rides right under the card, in German runs only
MEGA = MEGA.replace(_old_call, "title_card(_nbL(%r, %r))\n%s" % (
    TITLE_CARD, TITLE_CARD_DE, _i18n.cover_map_call(_COVER_DE)))
_unused = sorted(k for k in _DE_NB if k not in _USED)
print("German: %d + %d table entries used%s" % (
    len(_USED & set(_DE_NB)), len(_USED & set(_DE_TK)),
    "" if not _unused else " — %d UNUSED in chapters/de.txt: %s" % (
        len(_unused), "; ".join(repr(k[:40]) for k in _unused[:8]))))
# E10.8 (2026-09-30, Applikation) — THE CELL WITHOUT THE WORKSHOP NOTES.
# Comments, docstrings and deep indentation go (toolkit/slim.py, which checks
# that the program is the same); the sources keep them.
# E24.3 — the cover as it was in the markdown cell (facts, timeline, account
# block above Play), now an output of the cell; `nbcover-out` names it for
# the page script and the stylesheet.
# E25.k — tidied: card (+ language slot) · lead · "What you will learn" folded ·
# timeline · (mode cards) · Play · "Sign in" folded · the series (card_facts.cover_order)
from card_facts import cover_neutral, cover_order, COVER_WORDS
COVER_OUT = cover_neutral(cover_order(TITLE)).replace('<div class="nbtitle"', '<div class="nbtitle nbcover-out"', 1)
assert MEGA.count(COVER_MARK) == 1 and "<!--NB" not in COVER_OUT
# E24 Stufe 2 (2026-10-07, Python) — THE COVER SPEAKS THE LANGUAGE OF THE RUN.
# The cover is the kernel's output now, so the kernel can write its words in
# German itself: the lead, Play's tooltip, its label and the hint (measured,
# py_e23_1 on the v1.67 probe: in a German run these stood English — the map
# for the page, .nbcover-de, carried only rows, facts, label and hint, and
# never the lead or the tooltip). Replaced at run time, pair by pair, so the
# cell carries the cover once (+ ~0.3 KB); rows and facts stay with the map.
_COV_DE = [(k, _DE_NB[k]) for k in sorted((k for k in _DE_NB if len(k) > 8 and k in TITLE_CARD), key=len, reverse=True)]
_COV_DE += [('title="run the whole notebook"', 'title="das ganze Notebook ausf\u00fchren"'),
            ('>Play</div>', '>Start</div>'),
            ('runs every cell &mdash; or the menu', 'f\u00fchrt alle Zellen aus &mdash; oder im Men\u00fc')]
_COV_DE += [('>%s</summary>' % a, '>%s</summary>' % b) for a, b in COVER_WORDS[:2]]          # E25.k
_COV_DE += [('>The series &middot; ', '>Die Reihe &middot; '), ('(this notebook)', '(dieses Notebook)'),
            ('Principles of Biophysics &amp; Computational methods</div>',
             'Grundlagen der Biophysik &amp; computergest\u00fctzte Methoden</div>'),
            ('>Sets</li>', '>Mengen</li>'), ('>Start here</li>', '>Hier beginnen</li>'),
            ('>Complex Numbers <span', '>Komplexe Zahlen <span')]
# hw-E25.int (08.10.): the "not running yet" line of py-E25.h in a German run
# only in German (the kernel knows the language; py_e23_1: 0 English segments)
_COV_DE += [('<b>Not running yet</b> &mdash; this is a saved preview, its buttons do nothing. '
             'Run the cell below (or <i>Run &#9656; Run All Cells</i>).<br>', '')]
_COV_DE = [(a, b) for a, b in _COV_DE if a in COVER_OUT]
# E26.3 (2026-10-11, Python) — THE WINDOW'S COVER IN BOTH LANGUAGES. Lab puts its
# cover into German from the page (.nbcover-de map, E17.1); the reading window
# (PyCharm) gets both as markup: the German cover is the same card built from
# the German run's facts and timeline (FACTS_DE), with the cover's own words
# (_COV_DE) put in; the window takes its parts (card_facts.cover_parts) —
# _NBRW_COVER = {en: parts, de: parts} → _nbrw_cover() at run time.
# the German timeline's rows are the English ones in the same order (cover_map
# asserts it): each row's tooltip gets its German card (cards.de.txt), the
# summary line its German words — as the page does in Lab (.nbcover-de)
_tl_de, _cards_de, _rows = FACTS_DE["timeline_html"], _card_desc("", "chapters/cards.de.txt"), []
_rows_en = [tuple(r) + ("",) * (3 - len(r)) for r in FACTS["timeline"]]
_hits = list(re.finditer(r"(<div class='nbtl-row [^']*' title=')([^']*)(')", _tl_de))
assert len(_hits) == len(_rows_en), (len(_hits), len(_rows_en))
_out, _last = [], 0
for _m, _r in zip(_hits, _rows_en):
    _k = _desc_key(*_r)
    _c = _cards_de.get(_k, "") if _k else ""
    _out += [_tl_de[_last:_m.end(2)], ("&#10;" + __import__("html").escape(_c, quote=True)) if _c and "&#10;" not in _m.group(2) else ""]
    _last = _m.end(2)
_tl_de = "".join(_out) + _tl_de[_last:]
_tl_de = re.sub(r">Timeline &middot; (\d+) chapters &middot; (\d+) exercises &middot; (\d+) coding<",
                r">Zeitleiste &middot; \1 Kapitel &middot; \2 Aufgaben &middot; \3 Code<", _tl_de)
_cdt = _TITLE_T.replace("<!--NBFACTS-->", _FACTS_HTML_DE).replace("<!--NBTIMELINE-->", _tl_de)
COVER_OUT_DE = cover_neutral(cover_order(_cdt)).replace('<div class="nbtitle"', '<div class="nbtitle nbcover-out"', 1)
for _a, _b in _COV_DE:
    COVER_OUT_DE = COVER_OUT_DE.replace(_a, _b)
assert "<!--NB" not in COVER_OUT_DE and "Komplexe Zahlen" in COVER_OUT_DE
from card_facts import cover_parts as _cover_parts
_NBRW_COVER = {"en": _cover_parts(COVER_OUT), "de": _cover_parts(COVER_OUT_DE)}
assert all(_NBRW_COVER[l]["card"] and _NBRW_COVER[l]["tl"] for l in ("en", "de")), _NBRW_COVER
# the chapters' names in both languages (the reading copy's contents list and the
# window's timeline switch language without a second run): the rows of the two runs
_NBRW_TITLES = {l: [r[1].split(": ", 1)[-1] for r in f["timeline"] if r[0] == "chapter"]
                for l, f in (("en", FACTS), ("de", FACTS_DE))}
assert len(_NBRW_TITLES["en"]) == len(_NBRW_TITLES["de"]) > 0, _NBRW_TITLES
assert len(_COV_DE) >= 4, _COV_DE
MEGA = MEGA.replace(COVER_MARK, "_nbcv = %r\n_NBRW_COVER = %r\n_NBRW_TITLES = %r\nif _nbL(0, 1):\n    for _a, _b in %r:\n        _nbcv = _nbcv.replace(_a, _b)\ndisplay(IHTML(_nbcv))\n_nbread_end()"
                    % (COVER_OUT, _NBRW_COVER, _NBRW_TITLES, _COV_DE))
from slim import slim
MEGA = slim(MEGA)
# E20.1 (2026-10-02, Applikation) — CSS AND JS TRAVEL PACKED: zlib + base64 in
# the cell, unpacked by the kernel when it runs; the page gets the same text
# (toolkit/packz.py checks it).
from packz import pack as _pack
MEGA, _PACKED = _pack(MEGA)
# 2026-09-24x — no third cell. The reader asked for it gone: a
# notebook of ours is the title and the machine, nothing else.
# E15.3-Rest — the cold card follows JupyterLab light/dark (card_facts.cover_neutral)
# E17.3 — the account block above Play: in COVER_OUT (E24.3)
# E26.3 (2026-10-11, Python) — THE SHORT CELL (toolkit/shortcell.py): the two
# head lines, a run line, an editor-fold, ONE line of cargo (zlib + base64 of
# the cell above) and its loader — PyCharm shows ~13 lines instead of ~2 900.
# NB_CELL_CHUNK (chapter_template.py) > 0 = Variant B, cargo in lines of that length.
from shortcell import short as _short, expand as _expand, visible_lines as _vis
_FULL = "#@title " + MEGA[1:].lstrip() if MEGA.startswith("#") and not MEGA.startswith("#@title") else MEGA
_CHUNK = int(re.search(r"NB_CELL_CHUNK = (\d+)", TEMPLATE).group(1))
CELL = _short(_FULL, _FULL.split("\n")[:2], chunk=_CHUNK)
assert _expand(CELL) == _FULL and _vis(CELL) <= (15 if not _CHUNK else 17 + -(-len(CELL) // _CHUNK))
cells = [md(START_LINE), code(CELL, hide=True)]
nb = {"cells": cells,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python", "version": "3.8"}},
      "nbformat": 4, "nbformat_minor": 4}
# E24.4 (2026-10-06, Python) — THE STANDARD KERNEL, NOTHING PINNED.
# `python3` / "Python 3 (ipykernel)" is what every ipykernel installs; a front
# end without it (JupyterLite: "python", "Python (Pyodide)") falls back to the
# one kernel whose language is python. language_info carried a Python version
# (3.8) the file never needed — it named an environment; now only what a
# fresh `ipykernel` writes itself, without the version.
nb["metadata"] = {"kernelspec": {"display_name": "Python 3 (ipykernel)", "language": "python", "name": "python3"},
                  "language_info": {"name": "python", "codemirror_mode": {"name": "ipython", "version": 3},
                                    "file_extension": ".py", "mimetype": "text/x-python",
                                    "nbconvert_exporter": "python", "pygments_lexer": "ipython3"}}
# E26.3 — the notebook's own name in its metadata (OER; and the anchor the suites
# look for: run.py nb_id, py_e25_o nbid-, env_iframe the card's title — the
# cell itself carries them only packed since the short cell)
_TT = re.search(r'class="nbtitle-h"[^>]*>([^<]+)<', TITLE).group(1)
nb["metadata"]["digichemjn"] = {"id": _NB_ID_EARLY, "class": "nbid-" + _NB_ID_EARLY, "title": _TT,
                                "card": '<div class="nbtitle-h">%s</div>' % _TT,
                                "title_de": re.search(r'class="nbtitle-h"[^>]*>([^<]+)<', TITLE_CARD_DE).group(1),
                                "version": NBV, "toolkit": VERSION,
                                "cell": "short cell (E26.3): the code is the _NBZ line, zlib + base64; "
                                        "toolkit/shortcell.py expand() gives it back"}
# E39a K1 — Katalog: thema + kurse aus chapters/_setup*.py (toolkit/katalog.py, eine Quelle)
from katalog import notebook as _kat
_KAT = _kat("chapters"); assert _KAT["id"] == _NB_ID_EARLY, "set_notebook-id ≠ Bau-id"
nb["metadata"]["digichemjn"].update(thema=_KAT["thema"], kurse=_KAT["kurse"])
OUT = "Complex_Numbers_Step_by_Step_v" + NBV + ".ipynb"
json.dump(nb, open(OUT, "w"), ensure_ascii=False, indent=1)
print("formulas: %d typeset by the build, %d at run time (seed-dependent)" % (_n_pre, _n_rt))
print("packed: %d blocks, %d -> %d bytes" % (len(_PACKED), sum(r[1] for r in _PACKED), sum(r[2] for r in _PACKED)))
print("short cell: %d lines, %d chars (cargo of %d chars)" % (_vis(CELL), len(CELL), len(MEGA)))
print("built", OUT, "with", len(cells), "cells;", len(MEGA), "chars in the mega-cell;", FACTS["line"])
# E36 P3 (2026-10-19, Python) — AUSGANG A NEBEN DER DATEI: die Hülle (dist/huelle/<TOOLKIT_VERSION>/,
# für alle Notebooks gleich) und das Inhaltspaket (dist/inhalt/<id>/<NB_VERSION>/: Lesefassung je
# Sprache ohne Hülle, daten.json, meta.json) — aus der eben geschriebenen .ipynb, die dafür einmal je
# Sprache in einem frischen Kernel läuft (toolkit/paket.py). Die .ipynb bleibt, wie sie ist.
# dist/ ist Bau-Ausgang, nie im Bündel (pack_bundle.py). DIGICHEM_DIST=0 lässt es weg.
from paket import ausgaenge as _ausgaenge
_ausgaenge(OUT, nb["metadata"]["digichemjn"])
