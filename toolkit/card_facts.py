"""Build-time helper: ask the notebook itself what its title card must say.

2026-09-26 (Inhalt A), eingebaut R2 · Paket 15 (2026-09-28). The cold title
card is a markdown cell, written by the build before any kernel exists. The
goals, the chapter list and the time budget it shows must be the SAME ones the
running notebook computes — so the build runs the assembled mega-cell once,
headless (as tests/test_nb.py does), and asks the toolkit's card_facts().

    from card_facts import facts_html
    html, facts = facts_html(mega_source)
"""
import io, contextlib, re, html as _h
from urllib.parse import quote as _q


# E15.3-Rest (02.10., Oberfläche) — THE COLD CARD HAS NO SURFACE OF ITS OWN.
# Before Play only the markdown cell's inline styles exist, and JupyterLab's
# sanitiser drops var() and currentColor (measured, E14) — so the card's fixed
# light fill stayed light in a dark Lab. The markdown copy is therefore made
# theme-neutral: no fill, the heading in the cell's own colour (inherit), the
# border and rule as grey with alpha. The warm card in the mega-cell keeps its
# light look (CSS styles it after Play; the light theme relies on the inline
# fill), so only md(cover_neutral(TITLE)) uses this.
_NEUTRAL = (('background:#f8fafb;', 'background:transparent;'),
            ('border:1px solid #dde5ec;', 'border:1px solid rgba(127,140,153,.4);'),
            ('font-weight:800;color:#33475b;', 'font-weight:800;color:inherit;'),
            ('background:#cbd5de;margin:13px', 'background:rgba(127,140,153,.5);margin:13px'))


# E25.h (2026-10-08, Python: Text) — A SAVED PREVIEW SAYS IT IS NOT RUNNING.
# Lite (private window, 08.10.) showed the preview at once instead of the
# start line: the file had been run and saved WITH its outputs (Lab, PyCharm
# and Lite keep them). Such a preview is a picture — its buttons are dead. It
# now carries one line at its top, en and de, visible without any script;
# only our running page script hides it (JS E25.h: `.nbcover-stale`).
STALE_LINE = (
    '<div class="nbcover-stale" style="max-width:720px;margin:0 auto 14px;padding:8px 14px;'
    'border:1.5px solid #c9a227;border-radius:10px;background:rgba(201,162,39,.10);'
    'font-size:.92em;line-height:1.5;text-align:center">'
    '&#9654;&ensp;<b>Not running yet</b> &mdash; this is a saved preview, its buttons do nothing. '
    'Run the cell below (or <i>Run &#9656; Run All Cells</i>).'
    '<br><span lang="de"><b>Noch nicht ausgef&uuml;hrt</b> &mdash; eine gespeicherte Vorschau, ihre Kn&ouml;pfe '
    'tun nichts. F&uuml;hren Sie die Zelle aus (oder <i>Run &#9656; Run All Cells</i>).</span></div>')


def cover_neutral(title):
    """The markdown cell's card, made to follow JupyterLab light/dark; since
    E25.h with the "not running yet" line at the top of the cover."""
    for old, new in _NEUTRAL:
        assert title.count(old) == 1, old
        title = title.replace(old, new)
    i = title.index('>', title.index('<div class="nbtitle"')) + 1
    return title[:i] + STALE_LINE + title[i:]


def facts_html(mega_src, quiet=False):
    import matplotlib; matplotlib.use("Agg")
    import IPython.display as ipd
    ipd.display = lambda *a, **k: None          # no front end at build time
    src = "\n".join(l for l in mega_src.splitlines() if not l.strip().startswith("%pip"))
    g = {"__name__": "__main__", "display": lambda *a, **k: None}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(src, "<mega-cell>", "exec"), g)
    facts = g["card_facts"]()
    # E5.3 (2026-09-28): the cover's miniature timeline, from the same run
    desc = card_desc(mega_src)
    facts["timeline_html"] = card_timeline_html(facts["timeline"], desc)
    # E16.5 — say it at build time when a mark has no card
    facts["desc_missing"] = desc_missing(facts["timeline"], desc)
    n = sum(1 for r in facts["timeline"] if desc_key(*(tuple(r) + ("",) * (3 - len(r)))))
    if not quiet: print("cover cards: %d/%d marks%s" % (n - len(facts["desc_missing"]), n,
          "" if not facts["desc_missing"] else " — missing: " +
          ", ".join(k for k, _ in facts["desc_missing"])))
    return g["card_facts_html"](facts), facts


# ---------------------------------------------------------------------------
# E14 (2026-10-02, Struktur + Oberfläche vor Play; Python = Markup) — THE COLD
# COVER'S TIMELINE LOOKS LIKE THE WARM ONE ("minimal"), IN THE THEME'S COLOURS.
# Moved here from chapter_template.py: it only ever ran at build time, so it
# does not belong in the reader's cell (−≈4 KB there).
# Before Play nothing of ours has run: inline style only, and only what the
# markdown sanitiser keeps. MEASURED in JupyterLab 4.6 (allow-list, 02.10.):
# kept — flex, width, border (with or without colour), border-radius,
# box-shadow with hex/rgba, opacity, overflow-x, <img src="data:…svg">;
# stripped — var(), currentColor, position, transform, mask-image,
# scrollbar-color/-width, data-*. Hence:
#   * colours from the theme: the timeline sets no text colour, so it inherits
#     the cell's (JupyterLab: var(--jp-content-font-color1)); the beam pieces
#     and the grey marks are BORDERS WITHOUT A COLOUR = currentColor, softened
#     by opacity — light theme dark grey, dark theme light grey;
#   * one row in the warm column measure (CSS E13: 13.1 px, named ×3 = 39.3 px,
#     growing like CSS where there is room), the lane as wide as the text block
#     above it (.nbtitle-facts, 640 px), scrolling sideways with its native bar
#     right under it; no fade (mask-image is stripped, the edge would need JS);
#   * the beam is two pieces either side of each mark (no `position` for one
#     line behind them), from the middle of Title to the middle of YOC;
#   * the shapes of the warm marks: boxes and border triangles; the open task's
#     diamond outline (a rotated square there) is a small SVG <img>;
#   * names as warm: Title, groups, chapters, end and YOC, alternately under and
#     over the beam (even clusters over), Title left- and YOC right-aligned.
# Contract for JS/CSS after Play (unchanged): .nbcover-tl[open] · .nbtl-lane ·
# .nbtl-grp · .nbtl-row.nbtl-<kind> · .nbtl-calc/.nbtl-code · .nbtl-k-<task> ·
# .nbtl-mk (empty, inline display:none — CSS shows and draws it) · .nbtl-nm ·
# .nbtl-ln. Everything drawn only before Play carries `nbtl-ln`, which the warm
# stylesheet hides; the slot <div>s dissolve there (`.nbtl-row>div` contents).
# E16.6 (Python, cold half) — no beam between "End" and "Your own cell": End
# has no piece to its right, the YOC column none to its left (as after Play).
_TL_COL = {"title": "#0d63e0", "figure": "#3f8f6b", "task": "#c07a12", "quiz": "#c07a12",
           "byod": "#c07a12", "coding": "#7b4fb3"}
_TL_NAMED = ("title", "group", "chapter", "end", "cell")
_TL_U = 13.1                                   # CSS E13 --nbtl-u


def _rgba(hx, a):
    return "rgba(%d,%d,%d,%s)" % (int(hx[1:3], 16), int(hx[3:5], 16), int(hx[5:7], 16), a)


def _tl_shape(kind):
    """The mark as the warm stylesheet draws it (02-dark.css, minimal)."""
    c = _TL_COL.get(kind)
    glow = c and "box-shadow:0 0 7px 1px %s;" % _rgba(c, ".55")
    box = "<span class='nbtl-ln' style='display:block;flex:none;box-sizing:border-box;%s'></span>"
    if kind in ("group", "end"):               # 14 px square turned by 45° → 20 px
        tri = ("<span style='display:block;width:0;height:0;border-left:10px solid transparent;"
               "border-right:10px solid transparent;border-%s:10px solid'></span>")
        return ("<span class='nbtl-ln' style='display:flex;flex:none;flex-direction:column;"
                "opacity:.8'>%s%s</span>" % (tri % "bottom", tri % "top"))
    if kind == "task":                         # 12 px outline turned by 45° → 17 px
        svg = ("<svg xmlns='http://www.w3.org/2000/svg' width='27' height='27'><filter id='g'>"
               "<feGaussianBlur stdDeviation='2'/></filter><g fill='none' stroke='%s' "
               "stroke-width='2.5'><path d='M13.5 6.2 20.8 13.5 13.5 20.8 6.2 13.5Z' "
               "opacity='.55' filter='url(#g)'/><path d='M13.5 6.2 20.8 13.5 13.5 20.8 6.2 13.5Z'/>"
               "</g></svg>" % c)
        return ("<img class='nbtl-ln' alt='' width='27' height='27' src=\"data:image/svg+xml,%s\" "
                "style='display:block;flex:none;width:27px;height:27px;margin:0 -5px;max-width:none'>"
                % _q(svg, safe="/:=' "))
    return box % {
        "title":   "width:16px;height:16px;border:8px solid #0d63e0;border-radius:4px;"
                   "box-shadow:0 0 10px 3px rgba(13,99,224,.55)",
        "chapter": "width:18px;height:18px;border:9px solid;border-radius:3px;opacity:.8",
        "sub":     "width:10px;height:10px;border:2px solid;border-radius:50%;opacity:.8",
        "cell":    "width:14px;height:14px;border:2px dashed;border-radius:3px;opacity:.8",
        "figure":  "width:11px;height:9px;border:2px solid %s;border-radius:2px;%s" % (c, glow),
        "quiz":    "width:12px;height:12px;border:2.5px solid %s;border-radius:50%%;%s" % (c, glow),
        "byod":    "width:12px;height:12px;border:2.5px solid %s;border-radius:2px;%s" % (c, glow),
        "coding":  "width:12px;height:12px;border:2.5px solid %s;border-radius:4px;%s" % (c, glow),
    }.get(kind, "width:10px;height:10px;border:2px solid;border-radius:50%;opacity:.8")


# E15.4 (2026-10-02, Inhalt; Python = Markup) — A SHORT LINE PER MARK.
# E16.5 (2026-10-02, Inhalt) — A CARD FOR EVERY MARK, 2–3 SENTENCES: what the
# chapter or exercise contains and what it teaches, for students. All cards of
# a notebook stand in ONE file next to its chapters, `chapters/cards.txt`
# (`<key>: <text>` per line, `#` comments), read from the build's directory —
# one place to edit, review and later translate (E17), and not mixed into the
# chapter sources. A `#@desc <key>: <text>` comment in a source still works
# (E15.4) and wins. Neither reaches the reader's cell, so the cards cost the
# mega-cell nothing — they ride only in the cover (title cell).
# Keys:  ch<n> chapter · fig<n> its figure · <task> its exercise (t1, q1, b1 …)
#        · code_<task> its coding exercise · the slug of a section's name
#        (sub_how_to_use_this_notebook) · end · cell (defaults below).
# Title and the groups (Introduction, Content, Appendix) get NO card (E16.5):
# a click on them folds, as in the document's timeline (JS).
# The text rides in the mark's `title` after the name, on a line of its own —
# the cold tooltip; the sanitiser strips data-*, so after Play the script
# moves it to `data-desc` (contract: `title` = name, `data-desc` = text).
_DEFAULT_DESC = {
    "end": "Here the guided part of the notebook ends. Everything below it belongs to you: "
           "add cells of your own and carry on working.",
    "cell": "This is where your own cells go. Click the mark to add a new code cell below "
            "the guided part and try out ideas of your own.",
}
_NO_CARD = ("title", "group")


CARDS_FILE = "chapters/cards.txt"


def card_desc(src, cards=CARDS_FILE):
    """{key: text} from `chapters/cards.txt` and the `#@desc key: text`
    comments of the sources."""
    d = dict(_DEFAULT_DESC)
    try:
        with open(cards, encoding="utf-8") as fh:
            d.update(re.findall(r"^(\w+): *(.+?) *$", fh.read(), re.M))
    except OSError:
        pass
    d.update(re.findall(r"^#@desc (\w+): *(.+?) *$", src, re.M))
    return d


def _slug(name):
    return "sub_" + re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def desc_key(kind, name, task):
    """The `#@desc` key of a timeline row, or None for a mark without a card."""
    if kind in _NO_CARD:
        return None
    m = re.match(r"(?:Chapter|Figure) (\d+)", name)
    if kind == "chapter":
        return "ch" + m.group(1) if m else None
    if kind == "figure":
        return "fig" + m.group(1) if m else None
    if kind == "coding":
        return "code_" + task if task else None
    if kind in ("end", "cell"):
        return kind
    if task:
        return task
    return _slug(name)


def _desc(kind, name, task, desc):
    k = desc_key(kind, name, task)
    return desc.get(k, "") if k else ""


def desc_missing(rows, desc):
    """Marks that should carry a card and do not (E16.5: none may)."""
    rows = [tuple(r) + ("",) * (3 - len(r)) for r in rows]
    return [(desc_key(*r), r[1]) for r in rows
            if desc_key(*r) and not desc.get(desc_key(*r))]


def card_timeline_html(rows, desc=None):
    """The cover's miniature of the timeline (E5.3; flat since E8.21; one row in
    the warm look since E14). Static HTML, inline style only."""
    rows = [tuple(r) + ("",) * (3 - len(r)) for r in rows]
    n = {k: sum(1 for r in rows if r[0] in ((k, "quiz", "byod") if k == "task" else (k,)))
         for k in ("chapter", "task", "coding")}
    piece = ("<span class='nbtl-ln' style='flex:1 1 0;min-width:0;height:0;"
             "border-top:6px solid%s'></span>")
    beam, none = piece % ";opacity:.7", piece % ";border-top-color:transparent"
    groups, cur = [], []
    for kind, name, task in rows:
        if kind in _TL_NAMED and cur:
            groups.append(cur); cur = []
        cur.append((kind, name, task))
    if cur:
        groups.append(cur)
    out, last = [], len(groups) - 1
    for gi, grp in enumerate(groups):
        cols, grow = [], 0
        for ri, (kind, name, task) in enumerate(grp):
            first = ri == 0
            cls = "nbtl-row nbtl-%s" % kind
            if kind in ("task", "quiz", "byod"):
                cls += " nbtl-calc"
            elif kind == "coding":
                cls += " nbtl-code"
            if task:
                cls += " nbtl-k-%s" % re.sub(r"[^a-z0-9]", "", task.lower())
            if kind == "chapter":
                m = re.match(r"Chapter (\d+): (.*)", name)
                label = ("<b>%s</b>&ensp;%s" % (m.group(1), _h.escape(m.group(2)))
                         if m else _h.escape(name))
            else:
                label = _h.escape(name)
            f = 3 if first else 1
            grow += f
            shown = first and kind in _TL_NAMED
            big = kind in ("title", "group", "end", "cell")
            al = {"title": "flex-start", "cell": "flex-end"}.get(kind, "center")
            nm = ("<span class='nbtl-nm' style='display:block;max-width:110px;font-size:%s;"
                  "line-height:1.2;text-align:center;%s'>%s</span>"
                  % ("9px" if big else "10px",
                     "font-weight:800;letter-spacing:1.4px;text-transform:uppercase"
                     if big else "font-weight:700",
                     label) if shown else
                  "<span class='nbtl-nm' style='display:none'>%s</span>" % label)
            up = shown and gi % 2 == 1
            # the slots dissolve after Play (display:contents): their opacity
            # and width only ever act before it
            slot = ("<div style='display:flex;flex-direction:column;align-items:%s;align-self:%s;"
                    "justify-content:%s;width:110px;height:40px" + (";opacity:.75" if big else "")
                    + "'>%s</div>")
            cols.append(
                "<div class='%s' title='%s' style='flex:%d 0 %.1fpx;min-width:%.1fpx;"
                "display:flex;flex-direction:column;align-items:stretch'>%s"
                "<div style='display:flex;align-items:center;height:30px'>%s"
                "<span class='nbtl-mk' style='display:none%s'></span>%s%s</div>%s</div>"
                % (cls, _h.escape("\n".join(filter(None, (name, _desc(kind, name, task, desc or {})))),
                                  quote=True).replace("\n", "&#10;"), f, _TL_U * f, _TL_U * f,
                   slot % (al, al, "flex-end", nm if up else ""),
                   none if kind in ("title", "cell") else beam,
                   (";color:%s" % _TL_COL[kind]) if kind in ("task", "quiz", "byod", "coding", "figure") else "",
                   _tl_shape(kind), none if kind in ("end", "cell") else beam,
                   slot % (al, al, "flex-start", "" if up else nm)))
        out.append("<div class='nbtl-grp' style='display:flex;flex:%d 0 %.1fpx;min-width:%.1fpx'>%s</div>"
                   % (grow, _TL_U * grow, _TL_U * grow, "".join(cols)))
    head = ("Timeline &middot; %d chapters &middot; %d exercises &middot; %d coding"
            % (n["chapter"], n["task"], n["coding"]))
    return ("<details class='nbcover-tl' open style='max-width:640px;margin:30px auto 0;"
            "text-align:left'>"
            "<summary class='nbcover-tl-h' style='cursor:pointer;text-align:center;"
            "font-size:.8em;font-weight:800;letter-spacing:2px;text-transform:uppercase;"
            "color:#8b98a5;list-style-position:inside'>%s</summary>"
            "<div class='nbcover-tl-list nbtl-lane' style='display:flex;flex-wrap:nowrap;"
            "overflow-x:auto;overflow-y:hidden;margin:14px 0 0;padding:0 10px'>%s</div>"
            "</details>" % (head, "".join(out)))


# E17.3 (2026-10-02, Struktur: Markup) — THE ACCOUNT ON THE COVER. Logging in
# works where the mode choice works: on the cover, above Play. Python gives
# the place and the parts; the page gives the behaviour (JS: account, store,
# WebCrypto) and the look (CSS, contract of E19.5 in 13-stats.css / E17.3 in
# 06-marks.css). Before Play nothing of ours runs, so the block is hidden
# inline (a field that does nothing is worse than none, see Play in the
# build); JS adopts THIS block (no second one) and lifts the inline
# display:none once it is alive. Measured (JupyterLab 4.6 sanitiser): `hidden`,
# `aria-*` and every `data-*` attribute are stripped from the cell — JS sets
# data-in="0|1", aria-pressed and [hidden] itself.
#   .nbacct                       the block (inline display:none)
#     .nbacct-t                   its heading
#     .nbacct-me                  logged in: .nbacct-id + button.nbacct-logout
#     .nbacct-form                logged out:
#       input.nbacct-code         the profile code
#       .nbacct-pwbox > input.nbacct-pw[type=password] + button.nbacct-eye
#       button.nbacct-btn.nbacct-login.nbprimary · button.nbacct-btn.nbacct-new
#     .nbacct-msg                 one line of feedback
#     .nbacct-note                "no reset" (E19.5: say it, do not hide it)
# The words are English like the rest of the cell before Play; the page
# translates them with everything else once a language is chosen.
ACCOUNT_SLOT = (
    '<div class="nbacct" style="display:none;max-width:640px;margin:0 auto 18px;text-align:center">'
    '<div class="nbacct-t">Your account</div>'
    '<div class="nbacct-me" style="display:none"><b class="nbacct-id"></b> '
    '<button type="button" class="nbacct-btn nbacct-logout nbdanger">Log out</button></div>'
    '<div class="nbacct-form">'
    '<input class="nbacct-code" type="text" autocomplete="username" spellcheck="false" '
    'placeholder="Profile code"> '
    '<span class="nbacct-pwbox"><input class="nbacct-pw" type="password" '
    'autocomplete="current-password" placeholder="Password">'
    '<button type="button" class="nbacct-eye" title="show or hide the password">&#128065;</button></span> '
    '<button type="button" class="nbacct-btn nbacct-login nbprimary">Log in</button> '
    '<button type="button" class="nbacct-btn nbacct-new">New account</button></div>'
    '<div class="nbacct-msg"></div>'
    '<div class="nbacct-note">There is no password reset: without its password a profile '
    'code cannot be opened again.</div>'
    '</div>')

_PLAY = '<button class="nbbtn nbrunall nbcover-play"'

def account_slot(title):
    """The cover with the account block right above Play."""
    assert title.count(_PLAY) == 1, "the cover has no single Play button"
    return title.replace(_PLAY, ACCOUNT_SLOT + _PLAY)


# E25.k (2026-10-08, Python: Markup, Reihenfolge, Reihen-Daten) — THE PREVIEW,
# TIDIED (Nutzer 08.10.: "ordentlicher"; Lesart Dirigent, "hört sich gut an").
# From the top:
#   1 .nbtitle-card, with .nbcover-lang-slot inside (the page puts EN | DE
#     there, small, top right)
#   2 .nbtitle-lead — the one sentence; goals, chapters and time folded:
#     details.nbcover-learn > summary "What you will learn" > .nbtitle-facts
#   3 .nbcover-map — the timeline of this notebook (before the mode choice)
#   4 (the page inserts the mode cards .nbmode right before Play, as today)
#   5 Play, its label and hint
#   6 details.nbacct-fold > summary "Sign in" > .nbacct (the account block of
#     E17.3, unchanged inside; JS lifts its display:none as before)
#   7 .nbcover-series[data-series] — the notebooks of the series (before ·
#     this · after), a plain list that reads without script; data-series is
#     the JSON the page needs for progress per notebook and the links
# Python gives the markup and the data; behaviour (JS) and look (CSS) follow.
# SERIES is the catalogue (Lesart, order and names to be confirmed by the
# Nutzer): id, English and German name, file stem (the download carries
# "_v<version>.ipynb"), and the address on the Lite page once there is one.
SERIES = {
    # E29 P7 (2026-10-12, Python; Nutzer zu v1.75): Start Here is not part of the
    # biophysics series — it explains every notebook, so it is a series of its own
    "using": {
        "name": ("Using the notebooks", "Notebooks benutzen"),
        "items": [
            {"id": "start-here", "name": ["Start here", "Hier beginnen"],
             "file": "Start_Here_How_These_Notebooks_Work", "lite": ""},
        ]},
    "biophysics": {
        "name": ("Principles of Biophysics & Computational methods",
                 "Grundlagen der Biophysik & computergestützte Methoden"),
        "items": [
            {"id": "sets", "name": ["Sets", "Mengen"], "file": "Sets_Step_by_Step", "lite": ""},
            {"id": "complex-numbers", "name": ["Complex Numbers", "Komplexe Zahlen"],
             "file": "Complex_Numbers_Step_by_Step", "lite": ""},
        ]},
    "modeling": {
        "name": ("Introduction to Modeling", "Einführung in die Modellierung"),
        "items": [
            {"id": "intro-modeling", "name": ["Introduction to Modeling", "Einführung in die Modellierung"],
             "file": "Introduction_to_Modeling", "lite": ""},
        ]},
    # E28 (2026-10-12): the template is in a series of its own, so the cover's series
    # bar (E25.k) is a block the template shows — copy and rename for a new notebook
    "vorlage": {
        "name": ("Series name (placeholder)", "Name der Reihe (Platzhalter)"),
        "items": [
            {"id": "vorlage", "name": ["Notebook title", "Titel des Notebooks"], "file": "Vorlage", "lite": ""},
        ]},
}

COVER_WORDS = [("What you will learn", "Was Sie lernen"), ("Sign in", "Anmelden"),
               ("The series", "Die Reihe"), ("this notebook", "dieses Notebook")]


def series_of(nb_id):
    for sid, s in SERIES.items():
        if any(it["id"] == nb_id for it in s["items"]):
            return sid, s
    return None, None


def series_html(nb_id):
    """7 — the series bar: a plain ordered list (works without script) and the
    same as JSON for the page (data-series)."""
    import json as _json
    sid, s = series_of(nb_id)
    if not s:
        return ""
    lis = []
    for it in s["items"]:
        me = it["id"] == nb_id
        lis.append("<li class='nbser-it%s' data-nbid='%s' style='display:inline-block;margin:2px 8px;%s'>%s%s</li>"
                   % (" nbser-me" if me else "", it["id"], "font-weight:800" if me else "opacity:.8",
                      _h.escape(it["name"][0]),
                      " <span class='nbser-here' style='opacity:.7;font-weight:400'>(this notebook)</span>" if me else ""))
    data = {"series": sid, "name": list(s["name"]), "me": nb_id, "items": s["items"]}
    return ("<div class='nbcover-series' data-series='%s' style='max-width:640px;margin:22px auto 0;"
            "text-align:center;font-size:.86em;color:#8b98a5'>"
            "<div class='nbcover-series-h' style='font-weight:800;letter-spacing:2px;text-transform:uppercase;"
            "font-size:.9em;margin-bottom:6px'>The series &middot; %s</div>"
            "<ol class='nbser-list' style='list-style:none;margin:0;padding:0'>%s</ol></div>"
            % (_h.escape(_json.dumps(data, ensure_ascii=False, separators=(",", ":")), quote=True),
               _h.escape(s["name"][0]), "".join(lis)))


def cover_order(title):
    """The cover in the order of E25.k, with the account folded and the series
    bar (replaces account_slot for a notebook built by E25.k)."""
    m = re.search(r'nbid-([a-z0-9-]+)', title)
    nb_id = m.group(1) if m else ""
    # 1 the language slot, last child of the card
    i = title.index('<div class="nbtitle-lead"')
    j = title.rindex('</div>', 0, i)
    title = title[:j] + '<div class="nbcover-lang-slot"></div>' + title[j:]
    # 2 goals, chapters, time folded
    f0 = re.search(r'<div class=["\']nbtitle-facts["\']', title)
    f0 = f0.start() if f0 else -1
    c0 = re.search(r'<div class="nbcover[ "]', title).start()
    if f0 > -1:
        title = (title[:f0] + '<details class="nbcover-learn" style="max-width:640px;margin:14px auto 0">'
                 '<summary class="nbcover-learn-h" style="cursor:pointer;text-align:center;font-size:.8em;'
                 'font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#8b98a5">What you will learn'
                 '</summary>' + title[f0:c0] + '</details>' + title[c0:])
    # 3 · 5 the timeline before Play
    p0 = title.index(_PLAY)
    h0 = title.index('<div class="nbcover-hint"', p0)
    h1 = title.index('</div>', h0) + len('</div>')
    m0 = title.index('<div class="nbcover-map"')
    tail = '</div></div>'
    assert title.endswith(tail) and m0 >= h1, "cover: map is not the last child"
    play = title[p0:h1]
    mid = title[h1:m0]
    cmap = title[m0:len(title) - len(tail)]
    acct = ('<details class="nbacct-fold" style="max-width:640px;margin:22px auto 0;text-align:center">'
            '<summary class="nbacct-fold-h" style="cursor:pointer;font-size:.86em;font-weight:700;color:#8b98a5">'
            'Sign in</summary>' + ACCOUNT_SLOT + '</details>')
    return title[:p0] + cmap + play + mid + acct + series_html(nb_id) + tail


# E26.3 (2026-10-11, Python) — THE COVER'S PARTS, FOR THE READING WINDOW.
# The window (PyCharm) opens on a preview like Lab's cover; its markup is
# Python's (claude/VERTRAG-nbrw-E26.3.md): title card, lead, "what you will
# learn", the timeline's heading, the series bar — in BOTH languages — and
# the window's own controls (EN|DE, mode cards, ▶, account line), which the
# toolkit writes at run time (_nbrw_cover). The cover's timeline itself is
# not copied: the window draws its dots from the document (.nbrw-cv-tl), so
# they follow the mode and the progress. Taken from the finished cover
# (COVER_OUT, cover_order) by balanced tags, never by hand-written copies.
def _balanced(h, start):
    """The element starting at index `start` of `h`, up to its matching end tag."""
    tag = re.match(r"<(\w+)", h[start:]).group(1)
    pat = re.compile(r"<(/?)%s\b[^>]*>" % tag)
    depth = 0
    for m in pat.finditer(h, start):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return h[start:m.end()]
    raise ValueError("cover_parts: <%s> at %d is not closed" % (tag, start))


def cover_parts(cover):
    """{card, lead, learn, tl, series} of a finished cover (one language)."""
    def el(rx):
        m = re.search(rx, cover)
        return _balanced(cover, m.start()) if m else ""
    card = el(r"""<div class=["']nbtitle-card["']""")
    card = re.sub(r"""<div class=["']nbcover-lang-slot["']></div>""", "", card)
    tl = re.search(r"""<summary class=["']nbcover-tl-h["'][^>]*>(.*?)</summary>""", cover, re.S)
    return {"card": card, "lead": el(r"""<div class=["']nbtitle-lead["']"""),
            "learn": el(r"""<details class=["']nbcover-learn["']"""),
            "tl": tl.group(1).strip() if tl else "",
            "series": el(r"""<div class=["']nbcover-series["']""")}


# E29 P1 (2026-10-12, Python: Texte) — THE COVER IN BOTH LANGUAGES (Vorlage).
# Nutzer zu v1.75: "EN|DE ändert wirklich alles" — title card, subtitle, the
# timeline (names, hover boxes, tooltips), mode cards, Play, account, series,
# feedback. Up to v1.75 a click on DE changed only what the page writes itself
# (mode cards, the timeline's heading): the cover was the run's language, its
# German came only with a German run (.nbcover-de map). Now the cover carries
# BOTH (claude/VERTRAG-E29-P1.md):
#   * text   that differs: <span data-nbl="en">…</span><span data-nbl="de"
#            style="display:none">…</span> — the run's language visible inline
#            (no script, a saved preview: the sanitiser keeps the inline style);
#            a chunk only one language has: one such span (balanced HTML)
#   * attrs  title / placeholder / aria-label / alt that differ: the element
#            keeps the run's value and gets data-nbl-en / data-nbl-de = JSON
#            {attr: value}; a timeline row's "name\ncard" title comes split as
#            {"title": name, "data-desc": card} (the page's own split, 19-rail)
#   * the switch: COVER_LANG_CSS (in the cover output) shows the language of
#            the cover's EN|DE row (.nblang[data-lang], written by the page,
#            E17.1) and hides the other one — no rebuild, no reload. The
#            attributes are the page's (JS: apply data-nbl-<lang> on a switch).
# Built from the two finished one-language covers (same structure — asserted).
_TOK = re.compile(r"<[^>]+>|[^<]+")
_TATTR = re.compile(r"""\s(title|placeholder|aria-label|alt)=(?:"([^"]*)"|'([^']*)')""")
_KEEP_EN = re.compile(r"""\sdata-series='[^']*'""")      # JSON with both languages already


def _tkey(t):
    return _KEEP_EN.sub("", _TATTR.sub("", t)) if t.startswith("<") else "TEXT"


def _tattrs(t):
    out = {}
    for m in _TATTR.finditer(t):
        v = _h.unescape(m.group(2) if m.group(2) is not None else m.group(3))
        if m.group(1) == "title" and "\n" in v:
            v, d = v.split("\n", 1)
            out["data-desc"] = d
        out[m.group(1)] = v
    return out


def _nbl(lang, s, run="en"):
    return ('<span data-nbl="%s"%s>%s</span>' % (lang, "" if lang == run else ' style="display:none"', s)) if s else ""


def _balanced_ok(toks):
    st = []
    for t in toks:
        m = re.match(r"<(/?)(\w+)", t)
        if not m or t.endswith("/>") or m.group(2).lower() in ("br", "img", "input", "hr", "wbr"):
            continue
        if m.group(1):
            if not st or st.pop() != m.group(2):
                return False
        else:
            st.append(m.group(2))
    return not st


def cover_two(en, de):
    """One cover with both languages (English the run's), from the two covers."""
    import difflib, json as _json
    a, b = _TOK.findall(en), _TOK.findall(de)
    assert "".join(a) == en and "".join(b) == de
    sm = difflib.SequenceMatcher(None, [_tkey(t) for t in a], [_tkey(t) for t in b], autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for x, y in zip(a[i1:i2], b[j1:j2]):
                if not x.startswith("<"):
                    out.append(x if x == y else _nbl("en", x) + _nbl("de", y))
                    continue
                ea, da = _tattrs(x), _tattrs(y)
                if ea == da:
                    out.append(x)
                    continue
                js = lambda d: _h.escape(_json.dumps(d, ensure_ascii=False, separators=(",", ":")), quote=True)
                cut = len(x) - (2 if x.endswith("/>") else 1)
                out.append(x[:cut] + " data-nbl-en='%s' data-nbl-de='%s'" % (js(ea), js(da)) + x[cut:])
        else:
            xa, xb = a[i1:i2], b[j1:j2]
            assert _balanced_ok(xa) and _balanced_ok(xb), ("cover_two: unbalanced", "".join(xa)[:200], "".join(xb)[:200])
            assert "<span" not in "".join(xa + xb), ("cover_two: a chunk with a span", "".join(xa + xb)[:200])
            out.append(_nbl("en", "".join(xa)) + _nbl("de", "".join(xb)))
    return "".join(out)


def cover_one(two, lang):
    """The cover in one language (tests; the window takes its own one-language parts)."""
    other = "de" if lang == "en" else "en"
    h = re.sub(r'<span data-nbl="%s"(?: style="display:none")?>.*?</span>' % other, "", two, flags=re.S)
    h = re.sub(r'<span data-nbl="%s"(?: style="display:none")?>(.*?)</span>' % lang, r"\1", h, flags=re.S)
    return re.sub(r" data-nbl-(?:en|de)='[^']*'", "", h)


# E29 P5 — the cover's feedback line (the words of FEEDBACK in chapter_template.py,
# handed in by the build): at the foot of the cover, after the series
def feedback_note(fb, lang):
    to = '<span class="nbfb-to">%s</span>' % _h.escape(fb["to"])
    return ('<div class="nbfb nbfb-note" style="max-width:640px;margin:16px auto 0;text-align:center;'
            'font-size:.8em;color:#8b98a5"><span class="nbfb-text">%s</span></div>'
            % _h.escape(fb["text"][lang]).replace("{to}", to))


COVER_LANG_CSS = (
    "<style>.nbcover-out:has(.nblang[data-lang=de]) [data-nbl=en],"
    ".nbcover-out:has(.nblang[data-lang=en]) [data-nbl=de]{display:none!important}"
    ".nbcover-out:has(.nblang[data-lang=de]) [data-nbl=de],"
    ".nbcover-out:has(.nblang[data-lang=en]) [data-nbl=en]{display:inline!important}</style>")

# the run's language, at run time (a German run: German visible without script,
# and the German tooltips in place — the page swaps them on a switch, JS)
COVER_LANG_RT = r'''def _nbcv_de(h):
    import html as _hh, json as _jj, re as _rr
    h = h.replace(' data-nbl="en">', ' data-nbl="en" style="display:none">').replace(' data-nbl="de" style="display:none">', ' data-nbl="de">')
    def _a(m):
        t, d = m.group(0), _jj.loads(_hh.unescape(m.group(1)))
        if "data-desc" in d:
            d["title"] = d.get("title", "") + "\n" + d.pop("data-desc")
        for k, v in d.items():
            v = '"%s"' % _hh.escape(v, quote=True).replace("\n", "&#10;")
            t = _rr.sub(r"""(\s%s=)("[^"]*"|'[^']*')""" % k, lambda q: q.group(1) + v, t, count=1)
        return t
    return _rr.sub(r"<[^>]*\sdata-nbl-de='([^']*)'[^>]*>", _a, h)
if _nbL(0, 1):
    _nbcv = _nbcv_de(_nbcv)
'''


# E33 A2 (2026-10-13, Python; Nutzer 13.10.: "beim Öffnen direkt die Vorschau,
# wenn möglich auch beim allerersten Öffnen"). No Jupyter runs code on opening
# (Lab, PyCharm, VS Code, Colab: trust model) — so the FILE carries a saved, still
# preview as the code cell's one output: the cover's look (card, lead, goals,
# chapters, the timeline's count) in ONE language (EN, the default run), inline
# styles only with their own colours (readable on a light or dark front end, with
# or without a sanitizer: no <style>, no var(), no data-*, no svg), NO button and
# no script — instead, plainly, "▶ Run this cell to start" (+ one German line,
# like the start line above it). The first run replaces it (Jupyter clears a
# cell's outputs). Replaces E24.3 "no preview before the run" (Nutzer 13.10.).
# Class `nbstill` only (no class of the live cover: cold.py C2, lab_cover).
# E35 P1 (Nutzer 19.10.: "Die Vorschau soll auch den digi-Stil haben"): the
# colours of digi dark (07-skins.css, body.nbdark.nbskin-digi) — a dark card
# (its own background, so it reads the same on a white page — GitHub, nbviewer,
# Lab light — and on a dark one), gold kicker, the title in Unbounded where the
# reader has it, else the system stack (no font is loaded: no <style>, no net).
# Text on the card ≥ 4.5 (py_e35: ink 16.3, quiet 11.6, gold 13.5, pill ink on gold 12.4).
_STILL_INK, _STILL_SEC, _STILL_BG, _STILL_LINE = "#e9ecf6", "#c3c9de", "#0b0e1c", "#3a4166"
_STILL_GOLD, _STILL_PILL_INK = "#ffd36b", "#141826"
_STILL_FONT = ("font-family:'Instrument Sans',system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,"
               "'Noto Sans','DejaVu Sans',sans-serif")
_STILL_HEAD = ("font-family:Unbounded,'Instrument Sans',system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',"
               "Arial,'DejaVu Sans',sans-serif")


def _still_txt(h):
    import html as _h
    return _h.escape(_h.unescape(re.sub(r"<[^>]+>", " ", h or "")).split(" ")[-1].strip()
                     .replace("  ", " "), quote=False)


def still_preview(parts, chapters, count=""):
    """The saved preview (one text/html output of the built file)."""
    card = parts.get("card") or ""
    title = _still_txt((re.search(r"""class=["']nbtitle-h["'][^>]*>(.*?)</div>""", card, re.S) or [None, ""])[1])
    sub = _still_txt((re.search(r"""class=["']nbtitle-sub["'][^>]*>(.*?)</div>""", card, re.S) or [None, ""])[1])
    lead = _still_txt(parts.get("lead") or "")
    goals = [_still_txt(re.sub(r"<span class=.nbtitle-k.*?</span>", "", g, flags=re.S))
             for g in re.findall(r"<li class=.nbtitle-goal.[^>]*>(.*?)</li>", parts.get("learn") or "", re.S)]
    f = _STILL_FONT
    cap = ("font-size:12px;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:%s;margin:22px 0 6px"
           % _STILL_GOLD)
    h = ['<div class="nbstill" style="max-width:760px;margin:10px auto;padding:30px 26px 26px;box-sizing:border-box;'
         'background:%s;color:%s;border:1px solid %s;border-radius:14px;text-align:center;%s;font-size:15px;'
         'line-height:1.5">' % (_STILL_BG, _STILL_INK, _STILL_LINE, f),
         '<div style="%s;margin-top:0">Preview &middot; not running yet</div>' % cap,
         '<div style="%s;font-size:28px;font-weight:400;line-height:1.2;color:%s;margin-top:10px">%s</div>'
         % (_STILL_HEAD, _STILL_INK, title),
         '<div style="width:62px;height:2px;background:%s;margin:13px auto 11px"></div>' % _STILL_GOLD]
    if sub:
        h.append('<div style="font-size:12px;font-weight:700;letter-spacing:2.4px;text-transform:uppercase;color:%s">'
                 '%s</div>' % (_STILL_GOLD, sub))
    if lead:
        h.append('<div style="font-style:italic;font-size:16px;color:%s;max-width:620px;margin:16px auto 0">%s</div>'
                 % (_STILL_SEC, lead))
    if goals:
        h.append('<div style="%s">You will be able to</div><ul style="display:inline-block;text-align:left;margin:0;'
                 'padding-left:20px;color:%s">%s</ul>' % (cap, _STILL_INK, "".join(
                     '<li style="margin:2px 0">%s</li>' % g for g in goals)))
    if chapters:
        h.append('<div style="%s">Chapters</div><ol style="display:inline-block;text-align:left;margin:0;'
                 'padding-left:24px;color:%s">%s</ol>' % (cap, _STILL_INK, "".join(
                     '<li style="margin:2px 0">%s</li>' % _still_txt(c) for c in chapters)))
    if count:
        h.append('<div style="font-size:13px;color:%s;margin-top:14px">%s</div>' % (_STILL_SEC, _still_txt(count)))
    h.append('<div class="nbstill-run" style="display:inline-block;margin:24px auto 0;padding:12px 24px;border:2px solid '
             '%s;border-radius:999px;background:%s;color:%s;font-size:18px;font-weight:800">'
             '&#9654;&ensp;Run this cell to start</div>'
             '<div style="font-size:13px;color:%s;margin-top:8px">the &#9654; next to the cell, or <i>Run &#9656; Run All '
             'Cells</i> &middot; <span lang="de">&#9654; Zelle ausf&uuml;hren, um zu starten</span></div>' % (_STILL_GOLD, _STILL_GOLD, _STILL_PILL_INK, _STILL_SEC))
    h.append("</div>")
    return "".join(h)
