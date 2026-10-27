"""
DigiChemJN — Accordion Chapter Template  (JupyterLite / Pyodide-safe)
====================================================================
ONE place to control the look of every chapter. Change a value in DESIGN
below (or a builder) and every chapter in the notebook updates.

Why it is built this way (hard-won, JupyterLite/Pyodide facts):
  • HTML widgets honour a fixed/`fit-content` width and can be centred.
  • HTMLMath and Output widgets IGNORE width and drift left  → so formulas
    and plots are rendered to PNG images and shown inside HTML widgets.
  • Centring that actually works here = a full-width HBox with
    justify_content:center  →  center(widget).
  • Formulas are typeset with matplotlib mathtext, fontset 'cm' (classic TeX
    look, ~ MathJax) and embedded as crisp transparent PNGs.

Public builders:
  inject_style()                              – run once in setup
  info_box(tex, variables, constants, function, accent='blue')
  viz_intro_box(title, subtitle, table_html)  – pink intro card
  make_table(headers, rows)                   – styled table (column + header rules)
  slider_plot(render_fn, sliders)             – returns centred [sliders..., plot]
  exercise_box(title, prompt)                 – red exercise card
  editable_exercise(stub, check_fn, hint)     – textarea + Run&self-check + output
  solution_box(intro, code)                   – collapsible green solution
  interpretation_box(html)                    – light-green justified takeaway (the key message)
  warn_box(html)                              – red box: a warning, a limit, a pitfall
  build_chapter(num, title, info=None, viz=None, practice=None, interp=None,
                viz_title=..., practice_title=...)   – assembles + displays
"""
import io, base64, tokenize as _tok, keyword as _kw, builtins as _bi
import warnings as _warnings
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as _pe   # used to render formulas in bold
from ipywidgets import (HTML, VBox, HBox, Output, Button, Textarea, Layout,
                        FloatSlider, IntSlider, Dropdown, Accordion,
                        FloatText, IntText, RadioButtons, Text)
from IPython.display import display, HTML as IHTML, Javascript
# E22.3 — in PyCharm (no widget manager, see _static_fallback) the first
# Javascript outputs come before the toolkit is defined: no placeholder text
# E26.1: everywhere, not only where the kernel says PyCharm — a viewer that runs
# no script must not show "<IPython.core.display.Javascript object>"
Javascript.__repr__ = lambda self: ""

plt.rcParams['mathtext.fontset'] = 'cm'   # classic TeX look for rendered formulas

# E24.2 (2026-10-06, Applikation) — NEVER SILENTLY EMPTY WITHOUT THE WIDGET
# FRONT END. The whole document is ipywidgets; a page without the widget
# manager (measured: tests/regress/cold.py "bare" — the run installs
# ipywidgets, but the front end that comes with it can only load with the
# NEXT page load) drew 7 × "VBox(children=…)" text under a loading view that
# never lifted. Every widget output now carries an empty text/plain, and the
# first one of the run a text/html: a box (en/de) that says what is missing
# and the way — reload the page and Run All when this run has just installed
# it, else the widget component for the environment JupyterLab runs in. A
# front end with the manager prefers widget-view and shows none of it; the
# box also lifts the loading view (its own <style>, present only when the box
# is drawn). Where this run installed ipywidgets the still copy of E22.3
# (_static_fallback) is switched on as well: text, formulas and figures stay
# readable until the reload.
_NB_WFRESH = "ipywidgets" in (globals().get("_NB_FRESH") or ())
_nb_whinted = []


def _nb_widget_hint():
    from ipywidgets import Widget
    if getattr(Widget, "_nb_hint", False):
        return
    orig = Widget._repr_mimebundle_

    def _mb(self, **kw):
        d = orig(self, **kw)
        if not d:
            return d
        d = dict(d)
        # E26.1 — no hint box any more: the reading version (first output)
        # says what is missing, in the flow, where no widget is drawn
        # E33 D (2026-10-13, Python; VS Code K2: ~7 empty "…" rows under the
        # window). VS Code without a widget renderer draws an empty text/plain
        # as a 33-px "…" row, an empty text/html as nothing (measured, code-server
        # 1.104). So an empty text/html joins the empty text/plain (which stays:
        # without it IPython fills in the repr): a widget manager still prefers
        # widget-view; a viewer without one picks the HTML and draws nothing.
        d["text/plain"] = ""
        d["text/html"] = ""
        return d
    Widget._repr_mimebundle_ = _mb
    Widget._nb_hint = True


try:
    _nb_widget_hint()
except Exception:
    pass

# ======================================================================
# E26.1 (2026-10-11, Python) — THE READING VERSION COMES FIRST.
# PyCharm (JCEF 122, Video 08.10., v1.68), like VS Code, draws EVERY output in
# a page of its own: our script reaches only its own output, so cover, widget
# hint and document mixed (two title cards in two languages, "Your progress",
# the tool column). Principle now: the cell's FIRST and, without widgets, only
# visible output is the reading version (`.nbreading`) — card + document as
# finished HTML, in the language of the run, chapters as anchors, formulas and
# figures as inline SVG, light/dark by prefers-color-scheme (or the front
# end's theme variables), readable without any script. Everything else is
# what v1.69 output, published AFTER it: while the cell builds, the toolkit
# keeps its outputs (display_pub) and lets them go at the end
# (_nbread_end, safety net post_execute). The title card and the cover go out
# wrapped in `.nbwarm` (hidden inline): only our page script unwraps them, and
# only where it sees our widgets drawn in the SAME page (JupyterLab, Lite) —
# there the stylesheet hides the reading version (`.nb-live`). No kernel
# detection decides any of this; kernel_env only words the line on top.
# Displays inside an Output widget's context are never kept (the front end
# routes them by time). A display update of a kept output changes the kept one.
# ======================================================================
_NBREAD = {"on": False, "buf": [], "orig": None, "outd": [0], "done": False, "load": None}

def _nbread_begin():
    try:
        ip = get_ipython()                    # noqa: F821 — only in IPython
    except NameError:
        return False
    pub = getattr(ip, "display_pub", None)
    if pub is None or _NBREAD["on"]:
        return False
    orig = pub.publish
    if getattr(orig, "_nbread", False):
        orig = orig._nbread
    def publish(*a, **kw):
        if not _NBREAD["on"] or _NBREAD["outd"][0] > 0:
            return orig(*a, **kw)
        did = (kw.get("transient") or {}).get("display_id")
        if kw.get("update"):
            for e in _NBREAD["buf"]:
                if did and (e[1].get("transient") or {}).get("display_id") == did:
                    e[0] = (a[0] if a else kw.get("data"),) + tuple(a[1:])
                    if not a: e[1]["data"] = kw.get("data")
                    if "metadata" in kw: e[1]["metadata"] = kw["metadata"]
                    return None
            return orig(*a, **kw)
        _NBREAD["buf"].append([tuple(a), dict(kw)])
    publish._nbread = orig
    pub.publish = publish
    _NBREAD.update(on=True, buf=[], orig=orig, done=False, pub=pub, ip=ip)
    try:
        from ipywidgets import Output as _O
        if not getattr(_O, "_nbread", False):
            _oe, _ox = _O.__enter__, _O.__exit__
            def _enter(self, *a):
                _NBREAD["outd"][0] += 1
                return _oe(self, *a)
            def _exit(self, *a):
                try: return _ox(self, *a)
                finally: _NBREAD["outd"][0] = max(0, _NBREAD["outd"][0] - 1)
            _O.__enter__, _O.__exit__, _O._nbread = _enter, _exit, True
    except Exception:
        pass
    try:
        ip.events.register("post_execute", _nbread_end)
    except Exception:
        pass
    return True

def _nbread_data(e):
    a, kw = e
    return (a[0] if a else kw.get("data")) or {}

def _nbread_widget(mid):
    try:
        from ipywidgets.widgets import widget as _wm
        return getattr(_wm, "_instances", None).get(mid)
    except Exception:
        try:
            from ipywidgets import Widget
            return Widget.widgets.get(mid)
        except Exception:
            return None

_NBREAD_SKIP = ('class="nbrail', "class='nbrail", 'class="nbfeed', "class='nbfeed", "nbyoc-list",
                'class="nbcell', 'nbctl-', 'class="nbprog')

def _nbread_w(w, lvl, out):
    """One widget of the document as reading HTML (appended to `out`)."""
    from ipywidgets import Widget, Box, Accordion, Tab
    if not isinstance(w, Widget):
        return
    lay = getattr(w, "layout", None)
    if lay is not None and getattr(lay, "display", None) == "none":
        return
    for ent in _LOCKS.values():               # a lock shows its content, not its notice
        if ent.get("shell") is w and not ent.get("open"):
            _nbread_w(ent["real"], lvl, out)
            return
    r = _NBRW.get(getattr(w, "_model_id", None) or None)
    if r is not None:                         # E26 Teil 2: exercises and sliders for the reading window
        if r["kind"] != "skip":
            try:
                h = _nbrw_html(r)
            except Exception:
                h = ""
            if h:
                out.append(h)
            else:
                for fw in r.get("fallback") or ():
                    v = getattr(fw, "value", "") or ""
                    if v.strip():
                        out.append("<div class='nbread-b'>%s</div>" % _nbread_ids(v))
        return
    cls = tuple(getattr(w, "_dom_classes", ()) or ())
    if any(c.startswith(("nbctl", "nbstash")) for c in cls):     # the ⚙ drawer's controls
        return
    if isinstance(w, (Accordion, Tab)):
        # E26.3 (Teil 3, 4): a fold is a <details class="nbrw-acc" data-acc=<id>>
        # (claude/VERTRAG-nbrw-E26.3.md; folds without script too), OPEN in the
        # markup — readable everywhere as before; the window's script keeps the
        # reader's state per notebook. data-open = how Lab starts it (its
        # selected index), data-kind = which fold, data-lock = a chapter still
        # shut, data-nbrw-only = what the mode leaves out (practice → calc,
        # coding → code). A chapter that waits for an exercise wraps its content
        # in [data-nbrw-gate="calc:t1"] (code:… where the run builds no written
        # answer, mode code). The heading stays the h2–h5 .nbread-h of E26.1.
        tl = tuple(getattr(w, "titles", ()) or ())
        sel = getattr(w, "selected_index", None)
        kind = next((c[4:] for c in cls if c.startswith("acc-") and c not in ("acc-root", "acc-locked", "acc-plain",
                                                                                  "acc-exsec")), "")
        only = {"practice": "calc", "code": "code"}.get(kind, "")
        gate = ""
        if kind == "chapter":
            tk = _NBREAD.get("acc_task", {}).get(id(w))
            g = _TASKS["guard"].get(tk, "") if tk else ""
            if g:
                gate = "%s:%s" % ("code" if g in _TASKS["noanswer"] else "calc", g)
        for i, c in enumerate(w.children):
            t = tl[i] if i < len(tl) and tl[i] else ""
            if t and "acc-root" not in cls:
                h = min(lvl, 5)
                n = _NBREAD.setdefault("acc_n", {})
                n[kind or "acc"] = n.get(kind or "acc", 0) + 1
                out.append("<details class='nbrw-acc nbread-acc' open data-acc='%s-%d' data-kind='%s' data-open='%d'%s%s>"
                           "<summary class='nbread-sum'><h%d class='nbread-h'>%s</h%d></summary>"
                           % (_nbrw_attr(kind or "acc"), n[kind or "acc"], _nbrw_attr(kind), 1 if sel == i else 0,
                              " data-lock='1'" if "acc-locked" in cls else "",
                              (" data-nbrw-only='%s'" % only) if only else "", h, _esc_txt(t.strip()), h))
                if gate:
                    out.append("<div data-nbrw-gate='%s'>" % gate)
                _nbread_w(c, lvl + 1, out)
                if gate:
                    out.append("</div>")
                out.append("</details>")
            else:
                _nbread_w(c, lvl if "acc-root" in cls else lvl + 1, out)
        return
    if isinstance(w, Box):
        for c in w.children:
            _nbread_w(c, lvl, out)
        return
    name = type(w).__name__
    if name in ("HTML", "HTMLMath"):
        v = w.value or ""
        if any(k in v[:400] for k in _NBREAD_SKIP) or "<script" in v:
            return
        if '<div class="nbprog"' in v:
            v = v[:v.find('<div class="nbprog"')]
        if "class='nbend'" in v[:300]:
            # E26.1b: the end card speaks of JupyterLab's empty cell and offers
            # buttons ("Start again with"); in the reading copy only its heading
            m = _re.search(r"<div class='nbend-h'>(.*?)</div>", v, _re.S)
            if m:
                out.append("<hr><p class='nbread-end' style='text-align:center;font-weight:700'>%s</p>"
                           % m.group(1))
            return
        # controls do nothing in a reading copy: no button, field or choice
        v = _re.sub(r"<(button|select|textarea)\b.*?</\1>|<input\b[^>]*>", "", v, flags=_re.S | _re.I)
        if v.strip():
            out.append("<div class='nbread-b'>%s</div>" % _nbread_ids(v))

# ======================================================================
# E26 Teil 2 (2026-10-11, Python) — THE READING WINDOW GETS ITS EXERCISES.
# Where no widget is drawn but our script runs (PyCharm: every output a page
# of its own), 20-reader.js shows the reading version in a window. Its
# exercises come from here, as finished markup with the data of THIS run
# (the reader's seed): nothing in the page can ask the kernel.
#   calc    numeric_answer / choice_answer / target_exercise with `answer=`
#           → .nbrw-task[data-kind=calc] > span.nbrw-flab + input.nbrw-input
#           (or label.nbrw-opt > input[type=radio]) + button.nbrw-check +
#           .nbrw-fb. data-a = the answers and tolerances (base64 JSON:
#           {"f": [[field, value, tolerance, period]]} or {"c": index}).
#           JS checks; the state is kept per notebook in localStorage.
#   viz     slider_plot → .nbrw-slider > (input.nbrw-range + output.nbrw-val)
#           per control + .nbrw-fig. The pictures are drawn now, along each
#           control with the others at their start value (5 values each,
#           a menu: its options), and travel deflated (data-z, base64 zlib of
#           JSON; DecompressionStream in the page) — SVGs share almost all
#           their bytes. Without script: the start picture, as before.
#   code    code_fold → .nbrw-copy[data-kind=code] > code (the stub + the line
#           pruefe("t1")) + button.nbrw-copybtn: the reader runs it in a cell
#           of their own, pruefe() checks in the KERNEL like the Lab box does
#           (same check, same clock, same progress file ~/.digichemjn).
# Gating like Lab: a task waits until the one before it is answered (right,
# wrong or skipped); the code chain waits for its own guard (cguard). The
# first state comes from the kernel's progress (data-st), then the page's.
# Every interactive part is hidden inline (display:none) and shown only under
# .nbrw (15-reader.css !important, 20-reader.js): without script, in
# nbconvert/GitHub and in Lab nothing of it is visible.
# ======================================================================
_NBRW = {}
# values per slider (plus its start value): 5 with one or two sliders, 3 with
# more; and a time budget for all pictures of the run (measured 11.10.: ~45 ms
# a picture, Complex 68 pictures ≈ 3 s) — past it a figure keeps its start
# picture only (a slow machine gets fewer sliders, never a longer wait)
_NBRW_CFG = {"n": 5, "n_many": 3, "budget": float(__import__("os").environ.get("DIGICHEM_NBRW_BUDGET") or 4.0),
             "t0": None}

def _nbrw_reg(w, kind, **kw):
    try:
        _NBRW[w._model_id] = dict(kw, kind=kind)
    except Exception:
        pass
    return w

def _nbrw_b64(obj, z=False):
    import json as _json, zlib as _zlib
    b = _json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.b64encode(_zlib.compress(b, 9) if z else b).decode("ascii")

_NBRW_ST = {"done": "solved", "fail": "wrong", "skip": "skipped"}

def _nbrw_state(key, route="answer"):
    if not key:
        return "open"
    st = (_TASKS["code"] if route == "code" else _TASKS["state"]).get(key, "open")
    if st in _NBRW_ST:
        return _NBRW_ST[st]
    if route == "code":
        return "locked" if _is_locked_code(key) else "open"
    return "locked" if _is_locked(key) else "open"

def _nbrw_attr(s):
    return _esc_txt(str(s)).replace("'", "&#39;").replace('"', "&quot;")

def _nbrw_head(kind, key, st, extra=""):
    return ("<div class='nbrw-task' style='display:none' data-kind='%s' data-task='%s' data-st='%s'"
            " id='nbr-rw-%s-%s'%s>" % (kind, _nbrw_attr(key or ""), st, kind, _nbrw_attr(key or "x"), extra))

def _nbrw_tail():
    return ("<button type='button' class='nbrw-check'>%s</button><span class='nbrw-fb' role='status'></span></div>"
            % _nbL("Check", "Prüfen"))

def _nbrw_calc(r):
    ans = r["answer"]() if callable(r["answer"]) else r["answer"]
    rows = []
    for k, lab in r["fields"]:
        a = ans.get(k)
        if a is None:
            return ""
        a = tuple(a) if isinstance(a, (tuple, list)) else (a,)
        t = a[1] if len(a) > 1 and a[1] is not None else tol()
        rows.append([k, round(float(a[0]), 9), float(t), float(a[2]) if len(a) > 2 else 0.0, str(lab)])
    key = r.get("task")
    h = _nbrw_head("calc", key, _nbrw_state(key), " data-a='%s'" % _nbrw_b64({"f": [x[:4] for x in rows]}))
    for k, v, t, p, lab in rows:
        h += ("<span class='nbrw-flab'>%s</span><input class='nbrw-input' data-f='%s' inputmode='decimal'"
              " autocomplete='off' spellcheck='false' aria-label='%s'>" % (_esc_txt(lab), _nbrw_attr(k), _nbrw_attr(lab)))
    return h + _nbrw_tail()

def _nbrw_choice(r):
    c = r["answer"]() if callable(r["answer"]) else r["answer"]
    if c is None:
        return ""
    key = r.get("task")
    nm = "nbrw-%s-%x" % (key or "c", abs(hash(tuple(r["options"]))) % 65536)
    h = _nbrw_head("calc", key, _nbrw_state(key), " data-a='%s'" % _nbrw_b64({"c": int(c)}))
    for i, o in enumerate(r["options"]):
        h += ("<label class='nbrw-opt'><input type='radio' name='%s' value='%d'> %s</label>"
              % (nm, i, _esc_txt(str(o))))
    return h + _nbrw_tail()

def _nbrw_values(w, n=5):
    """The values a precomputed slider offers, and the index of its start value."""
    if isinstance(w, Dropdown):
        opts = [o[1] if isinstance(o, tuple) else o for o in w.options]
        labs = [str(o[0] if isinstance(o, tuple) else o) for o in w.options]
        return opts, labs, max(0, opts.index(w.value)) if w.value in opts else 0
    lo, hi, st, v0 = float(w.min), float(w.max), float(w.step or 1), float(w.value)
    vals = {v0}
    for i in range(n):
        x = lo + (hi - lo) * i / (n - 1)
        vals.add(round(lo + round((x - lo) / st) * st, 9))
    vals = sorted(v for v in vals if lo - 1e-9 <= v <= hi + 1e-9)
    if isinstance(w, IntSlider):
        vals = sorted({int(round(v)) for v in vals})
        v0 = int(round(v0))
    dec = max(0, len(("%g" % st).split(".")[1]) if "." in ("%g" % st) else 0)
    labs = [_de_num(("%." + str(dec) + "f") % v) if dec else _de_num("%d" % int(round(v))) for v in vals]
    return vals, labs, vals.index(v0) if v0 in vals else 0

def _nbrw_slider(r):
    sl, render, rd, dpi = r["sliders"], r["render"], r.get("readout"), r.get("dpi", 100)
    names = [k for k, w in sl.items() if isinstance(w, (FloatSlider, IntSlider, Dropdown))]
    base = {k: w.value for k, w in sl.items()}
    def frame(vals):
        try:
            h = fig_to_html(render(**vals), dpi=dpi, tight=False)
        except Exception:
            return None
        if rd is not None:
            try: h = rd(**vals) + h
            except Exception: pass
        # rounded coordinates: the same picture, a third fewer bytes
        h = _re.sub(r'(\d\.\d\d)\d+', r'\1', h)
        return _nbread_ids(h)
    f0 = frame(base)
    if f0 is None:
        return ""
    if _NBRW_CFG["t0"] is None:
        _NBRW_CFG["t0"] = _time.monotonic()
    if _time.monotonic() - _NBRW_CFG["t0"] > _NBRW_CFG["budget"]:
        names = []                            # over the budget: the start picture only
    nv = _NBRW_CFG["n"] if sum(1 for k in names if not isinstance(sl[k], Dropdown)) <= 2 else _NBRW_CFG["n_many"]
    frames, ctl, rows = [f0], [], ""
    for k in names:
        vals, labs, d = _nbrw_values(sl[k], nv)
        idx = []
        for j, v in enumerate(vals):
            if j == d:
                idx.append(0); continue
            f = frame(dict(base, **{k: v}))
            if f is None:
                idx.append(0); continue
            frames.append(f); idx.append(len(frames) - 1)
        desc = str(getattr(sl[k], "description", "") or k)
        ctl.append({"i": idx, "l": labs, "d": d})
        rows += ("<input type='range' class='nbrw-range' style='display:none' min='0' max='%d' step='1' value='%d'"
                 " data-s='%d' aria-label='%s'><output class='nbrw-val' style='display:none' data-desc='%s'>%s = %s</output>"
                 % (len(vals) - 1, d, len(ctl) - 1, _nbrw_attr(desc), _nbrw_attr(desc), _esc_txt(desc), _esc_txt(labs[d])))
    data = _nbrw_b64({"c": ctl, "f": frames}, z=True) if len(frames) > 1 else ""
    return ("<div class='nbrw-slider' data-kind='viz'%s>%s<div class='nbrw-fig'>%s</div></div>"
            % ((" data-z='%s'" % data) if data else "", rows if data else "", f0))

def _nbrw_code(r):
    key = r.get("task")
    if not key:
        return ""
    line = "%s\n\npruefe(\"%s\")\n" % ((r.get("stub") or "").rstrip("\n"), key)
    g = _TASKS["cguard"].get(key) or ""
    py = _nbrw_pysrc(key)                    # E26.3: the check as text, for Pyodide in the window
    return (("<div class='nbrw-copy' style='display:none' data-kind='code' data-task='%s' data-st='%s' data-guard='%s'"
             + ((" data-check='%s' data-pkgs='%s' data-cname='%s'"
                 % (base64.b64encode(py.encode("utf-8")).decode("ascii"), _nbrw_attr(",".join(_NBRW_PY.get(("pkgs", key)) or ())),
                    _nbrw_attr(_TASKS["cname"].get(key) or ""))) if py else "")
             + " id='nbr-rw-code-%s'><span class='nbrw-copytxt'>%s</span><code>%s</code>"
             "<button type='button' class='nbrw-copybtn'>%s</button><span class='nbrw-fb' role='status'></span></div>")
            % (_nbrw_attr(key), _nbrw_state(key, "code"), _nbrw_attr(g), _nbrw_attr(key),
               _nbL("Copy into a new cell below, fill in, run it: <code>pruefe()</code> checks it in the kernel "
                    "and keeps your progress.",
                    "In eine neue Zelle darunter kopieren, ausfüllen, ausführen: <code>pruefe()</code> prüft im "
                    "Kernel und speichert Ihren Fortschritt."),
               _esc_txt(line), _nbL("Copy", "Kopieren")))

# ======================================================================
# E26.3 (2026-10-11, Python) — THE CHECK TRAVELS AS TEXT (Pyodide in the window).
# "▶ Ausführen im Fenster": the page runs the reader's code in Pyodide and
# checks it with THE SAME check as the Lab box and pruefe() — so the check goes
# into the output as Python text (data-check on .nbrw-copy: base64 of UTF-8,
# with data-pkgs and data-cname — claude/VERTRAG-nbrw-E26.3.md, JS). It is cut
# out of the notebook itself: the short cell puts every
# piece into linecache (toolkit/shortcell.py), so inspect finds the source of
# the check and of everything it calls. _nbrw_pysrc(key) follows the names the
# check reads (AST Name loads that are globals), recursively:
#   module            → import numpy as np
#   our function      → its source (a lambda: the lambda's own expression)
#   our class         → its source (the ClassDef, from the same piece)
#   plain value       → name = repr  (numbers, text, tuples/lists/dicts of
#                        them, numpy numbers/arrays → float / np.array)
#   a builtin          → nothing
# Anything else (a widget, a file, an open object) and the text is NOT made:
# the window keeps the copy line (pruefe in a cell, E26 Teil 2). The program
# ends with  def _nbrw_check(ns): return _nbcheck(ns);  the page runs it in the
# namespace of the reader's code — as pruefe() does. The values
# are those of THIS run (the reader's seed, the run's language).
# ======================================================================
_NBRW_PY = {}

def _nbrw_lit(v, depth=0):
    """repr that evaluates back to v (with numpy as np), or None."""
    if depth > 6:
        return None
    if v is None or isinstance(v, (bool, int, str)):
        return repr(v)
    if isinstance(v, float):
        return repr(v) if v == v and v not in (float("inf"), float("-inf")) else "float(%r)" % repr(v)
    if isinstance(v, complex):
        return "complex(%s, %s)" % (_nbrw_lit(v.real), _nbrw_lit(v.imag))
    if isinstance(v, np.generic):
        return _nbrw_lit(v.item(), depth + 1)
    if isinstance(v, _re.Pattern):
        return "__import__('re').compile(%r, %d)" % (v.pattern, v.flags)
    if isinstance(v, np.ndarray):
        return "np.array(%r)" % (v.tolist(),) if v.size <= 4096 else None
    if isinstance(v, (tuple, list, set, frozenset)):
        items = [_nbrw_lit(x, depth + 1) for x in v]
        if any(x is None for x in items):
            return None
        if isinstance(v, tuple):
            return "(%s%s)" % (", ".join(items), "," if len(items) == 1 else "")
        if isinstance(v, list):
            return "[%s]" % ", ".join(items)
        return "%s([%s])" % (type(v).__name__, ", ".join(items))
    if type(v) is dict:
        out = []
        for k, x in v.items():
            a, b = _nbrw_lit(k, depth + 1), _nbrw_lit(x, depth + 1)
            if a is None or b is None:
                return None
            out.append("%s: %s" % (a, b))
        return "{%s}" % ", ".join(out)
    return None

def _nbrw_lines(code):
    """The lines of the piece a code object was compiled from (shortcell → linecache)."""
    import linecache as _lc
    fn = getattr(code, "co_filename", "")
    return _lc.getlines(fn) if fn.startswith("<digichemjn:") else []

def _nbrw_node_src(code, want):
    """The source of the def (or the lambda) starting at code.co_firstlineno.
    Cut from the piece's lines (inspect.getblock), never by parsing the whole
    piece: the toolkit's piece is ~5 000 lines (measured: 1.8 s for 7 checks)."""
    import ast as _ast, inspect as _ins
    lines = _nbrw_lines(code)
    i = code.co_firstlineno - 1
    if not lines or not 0 <= i < len(lines):
        return None
    if want is _ast.Lambda:
        args = list(code.co_varnames[:code.co_argcount])
        line = lines[i].rstrip("\n")
        for m in _re.finditer(r"\blambda\b", line):
            tail = line[m.start():]
            for end in range(len(tail), 6, -1):
                try:
                    node = _ast.parse(tail[:end].strip(), mode="eval").body
                except SyntaxError:
                    continue
                if isinstance(node, _ast.Lambda) and [x.arg for x in node.args.args] == args:
                    return tail[:end].strip()
        return None
    if lines[i].lstrip().startswith("@"):
        return None
    try:
        return "".join(_ins.getblock(lines[i:]))
    except Exception:
        return None

def _nbrw_class_src(cls):
    import inspect as _ins
    for v in vars(cls).values():
        c = getattr(v, "__code__", None) or getattr(getattr(v, "__func__", None), "__code__", None)
        if c is None:
            continue
        lines = _nbrw_lines(c)
        for i in range(min(c.co_firstlineno - 1, len(lines) - 1), -1, -1):
            if _re.match(r"\s*class\s+%s\b" % _re.escape(cls.__name__), lines[i]):
                try:
                    return "".join(_ins.getblock(lines[i:]))
                except Exception:
                    return None
        return None
    return None

def _nbrw_names(src, code_objs):
    """Global names a piece of source reads: Name loads that are in co_names."""
    import ast as _ast
    try:
        tree = _ast.parse(_dedent_src(src))
    except SyntaxError:
        return None
    loads = {n.id for n in _ast.walk(tree) if isinstance(n, _ast.Name) and isinstance(n.ctx, _ast.Load)}
    cn = set()
    todo = list(code_objs)
    while todo:
        c = todo.pop()
        cn.update(c.co_names)
        todo.extend(x for x in c.co_consts if hasattr(x, "co_names"))
    return sorted(loads & cn)

def _dedent_src(src):
    import textwrap as _tw
    s = _tw.dedent(src)
    return s if not s[:1].isspace() else s.strip()

def _nbrw_pysrc(key):
    """The check of coding exercise `key` as a stand-alone Python text, or None."""
    if key in _NBRW_PY:
        return _NBRW_PY[key]
    import types as _ty
    chk = _PRUEFE.get(key)
    _NBRW_PY[key] = None
    if not isinstance(chk, _ty.FunctionType):
        return None
    imports, values, defs, seen, bad = [], [], [], set(), []
    def need(fn_obj):
        code = fn_obj.__code__
        lam = code.co_name == "<lambda>"
        src = _nbrw_node_src(code, _ast_kinds()[0] if lam else _ast_kinds()[1])
        if not src:
            bad.append(getattr(fn_obj, "__name__", "?"))
            return None
        for i, nm in enumerate(code.co_freevars):
            try:
                cv = fn_obj.__closure__[i].cell_contents
            except Exception:
                bad.append(nm); continue
            take(nm, cv, fn_obj.__globals__)
        for nm in _nbrw_names(src, [code]) or ():
            if nm in code.co_freevars:
                continue
            if nm in fn_obj.__globals__:
                take(nm, fn_obj.__globals__[nm], fn_obj.__globals__)
            elif not hasattr(_bi, nm):
                bad.append(nm)
        return src
    def take(nm, v, glb):
        if nm in seen:
            return
        seen.add(nm)
        if isinstance(v, _ty.ModuleType):
            imports.append("import %s" % v.__name__ if v.__name__ == nm else "import %s as %s" % (v.__name__, nm))
            return
        if isinstance(v, _ty.FunctionType):
            src = need(v)
            if src is None:
                return
            if v.__code__.co_name == "<lambda>" or v.__name__ != nm:
                defs.append("%s = %s" % (nm, src) if v.__code__.co_name == "<lambda>" else "%s\n%s = %s" % (_dedent_src(src), nm, v.__name__))
            else:
                defs.append(_dedent_src(src))
            return
        if isinstance(v, type):
            src = _nbrw_class_src(v)
            if not src:
                bad.append(nm); return
            for base in v.__mro__[1:]:
                if base.__module__ == "builtins":
                    continue
                if base.__name__ in glb:
                    take(base.__name__, base, glb)
            code_objs = [getattr(x, "__code__", None) or getattr(getattr(x, "__func__", None), "__code__", None)
                         for x in vars(v).values()]
            for n2 in _nbrw_names(src, [c for c in code_objs if c is not None]) or ():
                if n2 in glb and n2 != nm:
                    take(n2, glb[n2], glb)
            defs.append(_dedent_src(src))
            return
        if isinstance(v, (_ty.BuiltinFunctionType, np.ufunc)):
            mod = getattr(v, "__module__", None) or ("numpy" if isinstance(v, np.ufunc) else None)
            if mod and getattr(__import__(mod.split(".")[0]), v.__name__, None) is v:
                imports.append("from %s import %s as %s" % (mod.split(".")[0], v.__name__, nm)); return
            bad.append(nm); return
        lit = _nbrw_lit(v)
        if lit is None:
            bad.append(nm); return
        values.append("%s = %s" % (nm, lit))
    top = need(chk)
    if top is None or bad:
        _NBRW_PY[("bad", key)] = sorted(set(bad))
        return None
    lam = chk.__code__.co_name == "<lambda>"
    imports = sorted(set(imports)) + (["import numpy as np"] if "np" not in seen and "np.array(" in "".join(values) else [])
    prog = "\n".join(["# DigiChemJN %s · check of coding exercise %s (%s, seed %s) · run: ok, tip = _nbrw_check(ns)"
                      % (NB_VERSION, key, LANG["value"], SEED.get("value"))]
                     + imports + values + defs
                     + ["_nbcheck = %s" % (top if lam else chk.__name__),
                        "def _nbrw_check(ns):", "    return _nbcheck(ns)"]) + "\n"
    # what Pyodide must load first (claude/VERTRAG-nbrw-E26.3.md: data-pkgs) — the
    # imports that are not the standard library's
    _NBRW_PY[("pkgs", key)] = sorted({m for m in _re.findall(r"^(?:import|from) (\w+)", "\n".join(imports), _re.M)
                                      if m in ("numpy", "matplotlib", "scipy", "pandas", "sympy")})
    try:
        compile(prog, "<check %s>" % key, "exec")
    except SyntaxError:
        _NBRW_PY[("bad", key)] = ["SyntaxError"]
        return None
    _NBRW_PY[key] = prog
    return prog

def _ast_kinds():
    import ast as _ast
    return (_ast.Lambda, (_ast.FunctionDef,))

# E26.3 — GATING AND MODE FOR THE WINDOW, as data on the reading version
# (data-rw-gate, base64 JSON; data-rw-mode). Nothing new is decided here: it is
# the run's own registry. chap: every section in order — a = its anchor id in
# the reading copy (nbr-…), t = title, n = number (null = unnumbered), task =
# its exercise, lock = the exercise that holds it shut (answer chain, Lab:
# guard; "" = never shut), shut = shut at the end of this run, open = folded
# open in Lab at the start, code = anchor of its coding fold. order = the
# answer chain, corder = the code chain, cguard = which coding exercise waits
# for which, st/cst = the states (solved|wrong|skipped|open), built = what this
# mode built (the window hides what the reader's mode does not show:
# plain → no exercise, calc → no coding, code → no written answer).
def _nbrw_gate():
    chap = []
    for ent in _STRUCT:
        if ent.get("kind") not in ("chapter", "sub") or not ent.get("anchor"):
            continue
        t = ent.get("task") or ""
        g = _TASKS["guard"].get(t, "") if t else ""
        chap.append({"a": "nbr-" + _aid(ent["anchor"]), "t": str(ent.get("title") or ""),
                     "n": ent.get("num"), "task": t, "lock": g,
                     "shut": bool(t and _is_locked(t)), "open": bool(ent.get("open")),
                     "code": ("nbr-" + _aid(ent["code_anchor"])) if ent.get("code_anchor") else ""})
    corder = [k for k in _TASKS["order"] if _TASKS["has_code"].get(k)]
    return {"mode": MODE["value"], "built": {"calc": builds_answer(), "code": builds_code()},
            "chap": chap, "order": _answer_order(), "corder": corder,
            "cguard": {k: v for k, v in _TASKS["cguard"].items() if v},
            "st": {k: _NBRW_ST.get(_TASKS["state"].get(k, "open"), "open") for k in _TASKS["order"]},
            "cst": {k: _NBRW_ST.get(_TASKS["code"].get(k, "open"), "open") for k in corder},
            "lang": LANG["value"]}

# E26.3 — THE COVER IN THE WINDOW (E26 Teil 3, 1; claude/VERTRAG-nbrw-E26.3.md).
# The window's first view is the cover as in Lab. Its parts come from the build
# in both languages (_NBRW_COVER = {en: …, de: …}, card_facts.cover_parts):
# title card, lead, "what you will learn", the timeline's heading, the series
# bar — each language in a [data-nbrw-l] block (CSS hides the other one; the
# window switches, without script the run's language shows). The controls are
# written here once: .nbrw-lang (EN|DE), an empty .nbrw-cv-tl (the window draws
# the dots from the document: mode and progress), .nbrw-modes >
# button.nbrw-mode-opt[data-mode] with the name in <b>, ▶ button[data-nbrw-act=
# play] + .nbrw-play-lab, details.nbrw-acct. Hidden inline (shown by the window
# only); ids/classes of the parts with the nbr- prefix like the whole copy.
# (f-strings: the build's German table must not turn the English half into _nbL)
# E33 B3 (2026-10-13, Python markup; Nutzer: "Login im Fenster … sehr wichtig"):
# details.nbrw-acct holds an EMPTY .nbacct[data-where=reader] as in Lab (JS fills
# it with 12-rail's account logic: name + password, new account, log out; store
# per notebook, E25 o) and one line under it. claude/VERTRAG-E33-py.md.
_NBRW_MODES = (("plain", "¶", (f"Plain", "Nur lesen"), (f"text and figures only", "nur Text und Abbildungen")),
               ("calc", "✎", (f"Pen & paper", "Stift & Papier"),
                (f"only the calculating exercises", "nur die Rechenaufgaben")),
               ("code", "⌨", (f"Code", "Code"), (f"only the coding exercises", "nur die Programmieraufgaben")),
               ("both", "✎⌨", (f"Both", "Beides"), (f"calculate and code", "rechnen und programmieren")))
_NBRW_CV = {"mode": (f"What do you want to practise?", "Was möchten Sie üben?"),
            "play": (f"Play", "Start"),
            "acct": (f"Sign in · new account", "Anmelden · neues Konto"),
            "acctT": (f"Your progress stays in this browser, per notebook — with or without an account.",
                      "Ihr Fortschritt bleibt in diesem Browser, je Notebook — mit oder ohne Konto.")}

def _nbrw_two(pair):
    return "".join("<span data-nbrw-l='%s'>%s</span>" % (l, _esc_txt(str(pair[k]))) for k, l in ((0, "en"), (1, "de")))

def _nbrw_cover():
    cov = globals().get("_NBRW_COVER")
    if not isinstance(cov, dict) or not cov.get("en") or not cov.get("de"):
        return ""
    head = "".join("<div data-nbrw-l='%s'><div style='text-align:center'>%s</div>%s%s</div>"
                   % (l, _nbread_ids(cov[l].get("card") or ""), _nbread_ids(cov[l].get("lead") or ""),
                      _nbread_ids(cov[l].get("learn") or "")) for l in ("en", "de"))
    tlh = "".join("<span data-nbrw-l='%s'>%s</span>" % (l, cov[l].get("tl") or "") for l in ("en", "de"))
    series = "".join("<div data-nbrw-l='%s'>%s</div>" % (l, _nbread_ids(cov[l].get("series") or ""))
                     for l in ("en", "de") if cov[l].get("series"))
    modes = "".join("<button type='button' class='nbrw-mode-opt' role='radio' data-mode='%s' aria-checked='%s'>"
                    "<span class='nbrw-mode-ic'>%s</span><b class='nbrw-mode-l'>%s</b><span class='nbrw-mode-d'>%s</span></button>"
                    % (m, "true" if m == MODE["value"] else "false", ic, _nbrw_two(l), _nbrw_two(d))
                    for m, ic, l, d in _NBRW_MODES)
    return ("<div class='nbrw-cover' style='display:none' data-kind='cover' data-lang='%s'>"
            "<div class='nbrw-lang' role='group'><button type='button' data-lang='en'>EN</button>"
            "<button type='button' data-lang='de'>DE</button></div>%s"
            "<div class='nbrw-cv-t nbrw-cv-h'>%s</div><div class='nbrw-cv-tl'></div>"
            "<div class='nbrw-cv-t nbrw-cv-h'>%s</div><div class='nbrw-modes' role='radiogroup'>%s</div>"
            "<div class='nbrw-cv-row'><button type='button' class='nbrw-play' data-nbrw-act='play'>▶</button>"
            "<span class='nbrw-play-lab'>%s</span></div>"
            "<details class='nbrw-acct'><summary>%s</summary><div><div class='nbacct' data-where='reader' data-in='0' "
            "data-step='in'></div><div class='nbrw-acct-note'>%s</div></div></details>%s</div>"
            % (LANG["value"], head, tlh, _nbrw_two(_NBRW_CV["mode"]), modes, _nbrw_two(_NBRW_CV["play"]),
               _nbrw_two(_NBRW_CV["acct"]), _nbrw_two(_NBRW_CV["acctT"]), series))

def _nbrw_html(r):
    return {"calc": _nbrw_calc, "choice": _nbrw_choice, "slider": _nbrw_slider,
            "code": _nbrw_code}.get(r["kind"], lambda _r: "")(r)

_PRUEFE = {}

def pruefe(key, *fns):
    """Check a coding exercise from a cell of your own (the reading window,
    PyCharm): the same check as the box in JupyterLab, the same progress.
        pruefe("t1")              # your function, defined in this notebook
        pruefe("t1", roots_of)    # or handed over"""
    key = str(key)
    def say(ok, txt):
        if ok is None:
            mark = "ℹ"
        else:
            mark = "✓" if ok else "✗"
        msg = "%s %s" % (mark, txt)
        st = {True: "solved", False: "wrong"}.get(ok)
        js = ("<script>try{localStorage.setItem('digichemjn.%s.reader.code.%s','%s')}catch(e){}</script>"
              % (_re.sub(r"[^\w.-]", "", str(NOTEBOOK.get("id") or "nb")), _re.sub(r"\W", "", key), st)) if st else ""
        cls = {True: "nbok", False: "nbwarn"}.get(ok, "nbink")
        try:
            display({"text/plain": msg, "text/html": "<div class='%s' style='font-weight:600'>%s</div>%s"
                     % (cls, _esc_txt(msg), js)}, raw=True)
        except Exception:
            print(msg)
    chk = _PRUEFE.get(key)
    if chk is None:
        say(None, _nbL("There is no coding exercise %s in this run (mode or name?)." % key,
                       "In diesem Lauf gibt es keine Programmieraufgabe %s (Modus oder Name?)." % key))
        return None
    g0 = _TASKS["cguard"].get(key)
    if g0 and _TASKS["code"].get(g0, "open") == "open":
        say(None, _nbL("Coding %s opens once coding %s is answered: right, wrong or skipped." % (key, g0),
                       "Programmieraufgabe %s öffnet sich, sobald %s beantwortet ist: richtig, falsch oder "
                       "übersprungen." % (key, g0)))
        return None
    g = _user_globals()
    for f in fns:
        nm = getattr(f, "__name__", None)
        if nm:
            g[nm] = f
    cn = _TASKS["cname"].get(key)
    if cn and len(fns) == 1 and callable(fns[0]):
        g[cn] = fns[0]
    try:
        ok, tip = _clocked(chk, g)
    except Exception as e:
        ok, tip = False, _nbL("Your function ran but crashed on the test inputs: %r" % (e,),
                              "Ihre Funktion lief, brach aber bei den Testwerten ab: %r" % (e,))
    if ok:
        task_code_solved(key)
        say(True, _nbL("correct, well done!", "richtig, gut gemacht!") + (" " + str(tip) if tip else ""))
    else:
        task_wrong(key, "code")
        say(False, _nbL("Not there yet, keep going.", "Noch nicht, weiter so.") + (" " + str(tip) if tip else ""))
    return None

def _nbread_line():
    # E38a P1 (2026-10-26, Python) — THE LINE FITS THE PAGE IT IS ON. The package
    # for lesen.html (toolkit/paket.py, Ausgang A) is made by a kernel run, and the
    # line said "run the cell in JupyterLab" on a page that has no cell. The build
    # sets DIGICHEM_READ_PAGE=1 for that run: the line says what works THERE —
    # exercises are checked in the page, a coding exercise starts Python (Pyodide)
    # at its first Run. A notebook run never has the variable (paket strips DIGICHEM*).
    import os as _os38
    if _os38.environ.get("DIGICHEM_READ_PAGE") == "1":
        return _nbL("Web version: exercises are checked right here; a coding exercise starts Python in this "
                    "browser at its first <b>&#9654; Run</b>.",
                    "Webfassung: Aufgaben werden hier gepr&uuml;ft; eine Code-Aufgabe startet Python in diesem "
                    "Browser beim ersten <b>&#9654; Ausf&uuml;hren</b>.")
    env = kernel_env()
    if env in ("pycharm", "vscode", "colab"):
        return _nbL("Reading version. <b>Interactive</b> (exercises, checks, timeline): open this notebook in "
                    "JupyterLab or on the Lite page.",
                    "Lesefassung. <b>Interaktiv</b> (Aufgaben, Pr&uuml;fen, Zeitleiste): dieses Notebook in "
                    "JupyterLab bzw. auf der Lite-Seite &ouml;ffnen.")
    if _NB_WFRESH:
        return _nbL("Reading version. This run has just installed the widgets: <b>reload the browser page</b> "
                    "(F5 / &#8984;R), then <i>Run &#9656; Run All Cells</i> &mdash; the interactive notebook replaces it.",
                    "Lesefassung. Dieser Lauf hat die Widgets gerade installiert: <b>Browserseite neu laden</b> "
                    "(F5 / &#8984;R), dann <i>Run &#9656; Run All Cells</i> &mdash; das interaktive Notebook ersetzt sie.")
    # E26.1b (PyCharm 11.10.: not recognised, the pip advice was wrong there):
    # without a recognised front end the line is NEUTRAL. The pip advice is
    # written hidden (inline) and only our page script shows it — it runs
    # next to this output only where the whole notebook is one page
    # (JupyterLab, Notebook 7, Lite) and it sees no widget of ours drawn.
    # (a saved copy opened in JupyterLab shows this too: it says to run the cell, E25.h)
    return (_nbL("Reading version. <b>Interactive</b> (exercises, checks, timeline): run the cell in "
                 "JupyterLab, or open the notebook on the Lite page.",
                 "Lesefassung. <b>Interaktiv</b> (Aufgaben, Pr&uuml;fen, Zeitleiste): die Zelle in JupyterLab "
                 "ausf&uuml;hren bzw. das Notebook auf der Lite-Seite &ouml;ffnen.")
            + "<span class='nbread-pip' style='display:none'> "
            + _nbL("Here the widget component is missing: <code>pip install ipywidgets</code> where JupyterLab "
                   "runs, restart, reload the page.",
                   "Hier fehlt die Widget-Komponente: <code>pip install ipywidgets</code> dort, wo JupyterLab "
                   "l&auml;uft, neu starten, Seite neu laden.") + "</span>")

_NBREAD_CSS = (
    "<style>"
    ".nbreading{--nbr-fg:var(--jp-content-font-color1,var(--vscode-editor-foreground,#1d2731));"
    "--nbr-bg:var(--jp-layout-color0,var(--vscode-editor-background,#ffffff));"
    "--nbr-q:var(--jp-content-font-color2,#46525e);--nbr-ln:rgba(120,132,145,.45);"
    "color:var(--nbr-fg);background:var(--nbr-bg);"
    "--nbskin-ink:var(--nbr-fg);--nbskin-acc:#2f78b5;--nbskin-font:inherit;"
    "max-width:860px;margin:0 auto;padding:18px 22px 28px;box-sizing:border-box;"
    "font:15px/1.6 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;text-align:left}"
    "@media (prefers-color-scheme:dark){.nbreading{"
    "--nbr-fg:var(--jp-content-font-color1,var(--vscode-editor-foreground,#e3e8ed));"
    "--nbr-bg:var(--jp-layout-color0,var(--vscode-editor-background,#1e2329));"
    "--nbr-q:var(--jp-content-font-color2,#b9c3cc);--nbskin-acc:#6fb3e6}}"
    ".nbreading *:not(svg):not(svg *){color:inherit!important;background-color:transparent!important;"
    "background-image:none!important;box-shadow:none!important;position:static!important;opacity:1!important;"
    "max-width:100%!important;float:none!important}"
    ".nbreading svg{max-width:100%;height:auto}"
    ".nbreading .nbread-line{border:1px solid var(--nbr-ln);border-radius:8px;padding:7px 12px;"
    "margin:0 0 16px;font-size:.92em}"
    ".nbreading .nbread-toc{margin:10px 0 18px;padding-left:1.4em}"
    ".nbreading a{color:inherit!important;text-decoration:underline}"
    ".nbreading .nbread-h{margin:1.3em 0 .4em;line-height:1.3;border-bottom:1px solid var(--nbr-ln);padding-bottom:3px}"
    ".nbreading h2.nbread-h{font-size:1.45em}.nbreading h3.nbread-h{font-size:1.22em}"
    ".nbreading h4.nbread-h,.nbreading h5.nbread-h{font-size:1.05em;border-bottom:0}"
    ".nbreading .nbread-b{margin:6px 0}"
    ".nbreading table{border-collapse:collapse;margin:8px auto}"
    ".nbreading td,.nbreading th{border:1px solid var(--nbr-ln);padding:3px 8px}"
    ".nbreading [class*='box'],.nbreading [class*='card']{border-color:var(--nbr-ln)!important}"
    # E26.3 — the folds (<details>): the heading is the summary's line, a small ▾/▸ before it
    # (only without the window: there 15-reader.css draws the folds like Lab)
    ".nbreading summary.nbread-sum{cursor:pointer;list-style:none}"
    ".nbreading summary.nbread-sum::-webkit-details-marker{display:none}"
    ".nbreading:not(.nbrw *) summary.nbread-sum{display:flex;align-items:baseline;gap:.45em}"
    ".nbreading:not(.nbrw *) summary.nbread-sum::before{content:'\\25BE';font-size:.85em;opacity:.65}"
    ".nbreading:not(.nbrw *) details:not([open])>summary.nbread-sum::before{content:'\\25B8'}"
    ".nbreading summary.nbread-sum>.nbread-h{flex:1 1 auto;min-width:0}"
    # E26.3 — both languages in the markup ([data-nbrw-l]), one shown: the
    # language of .nbreading (the run's; the window sets the reader's choice)
    ".nbreading[lang=en] [data-nbrw-l=de],.nbreading[lang=de] [data-nbrw-l=en]{display:none!important}"
    # E30 B2: a piece of the document in both languages: the chosen one shows (inline,
    # like the text it stands for; `hidden` keeps the other out without a stylesheet)
    ".nbreading[lang=en] [data-nbrw-t][data-nbrw-l=en],.nbreading[lang=de] [data-nbrw-t][data-nbrw-l=de]{display:inline!important}"
    "</style>")
# E26.2 (CSS) — THE READING WINDOW. Where no widget is drawn but our script
# runs (PyCharm: every output a page of its own), 20-reader.js puts the
# reading version into a window of fixed height (.nbrw-win, own scrollbar
# hidden) with a panel on the right (.nbrw-panel: buttons, current chapter,
# track, thumb, marks) and fields/sliders in the text. Its look travels INSIDE
# the reading output — inject_style() never reaches a page of its own. Plain
# text (no % DESIGN, not minified); everything hangs on .nbrw, which only the
# script sets, so without script nothing changes. .nbreading resets every
# descendant with !important (0,1,2); 15-reader's rules are (0,2,0) and carry
# !important where that reset would win. Light/dark: [data-nbrw-theme], else
# prefers-color-scheme; skins [data-nbrw-skin] minimal|cyber|fairy (07-skins).
_NBREAD_CSS = _NBREAD_CSS[:-len("</style>")] + r"""
/*@include css/15-reader.css*/
""" + "</style>"

def _nbread_ids(h):
    # the reading copy shares the page with the live document in JupyterLab:
    # none of its ids, classes or data-nb* marks may be one the document, the
    # panel, the stylesheet or a test looks up (`.nbtitle-card` first in the
    # output = the document's card, 19-rail) — all get the prefix nbr-
    h = _re.sub(r"""(\sid=)(["'])""", r"\1\2nbr-", h)
    h = _re.sub(r"""((?:xlink:)?href=)(["'])#""", r"\1\2#nbr-", h)
    h = _re.sub(r"""(\sclass=)(["'])([^"']*)\2""",
                lambda m: "%s%s%s%s" % (m.group(1), m.group(2),
                                        " ".join("nbr-" + c for c in m.group(3).split()), m.group(2)), h)
    h = _re.sub(r"""\sdata-nb[\w-]*=(?:"[^"]*"|'[^']*')""", "", h)
    return h.replace("url(#", "url(#nbr-")

# E30 B2 (2026-10-12, Python) — BOTH LANGUAGES IN THE READING DOCUMENT (STOP
# E30 B2: title/document English, contents + panel German in the window). The
# text of the run stays where it is; each piece the run took from a pair
# (_NBL_SEEN, whole literals — no %-templates, nothing in a tag, a script, a
# style, an svg, code or a form field, whole words only, balanced tags) becomes
#   <span data-nbrw-l=run data-nbrw-t>…</span><span data-nbrw-l=other data-nbrw-t hidden>…</span>
# .nbreading[lang] shows one (the window sets lang from EN|DE), inline like the
# text it stands for; without a stylesheet `hidden` keeps the other language
# out (nbviewer/GitHub).
import re as _re30
_NBRW_TAG = _re30.compile(r"""<!--.*?-->|<(?:[^>"']|"[^"]*"|'[^']*')*>""", _re30.S)
_NBRW_SKIP = _re30.compile(r"<(script|style|svg|code|pre|textarea|select)\b.*?</\1\s*>", _re30.S | _re30.I)
_NBRW_INLINE = r"</?(?:b|i|em|strong|u|s|sub|sup|small|mark)\s*>"
_NBRW_VOID = ("br", "hr", "img", "input", "wbr", "meta", "link", "source", "col", "area", "embed", "param")

def _nbrw_balanced(s):
    st = []
    for m in _NBRW_TAG.finditer(s):
        t = m.group(0)
        if t.startswith("<!--"):
            return False
        mm = _re30.match(r"<\s*(/?)\s*([a-zA-Z][\w-]*)", t)
        if not mm:
            return False
        nm = mm.group(2).lower()
        if nm in _NBRW_VOID or t.endswith("/>"):
            continue
        if mm.group(1):
            if not st or st.pop() != nm:
                return False
        else:
            st.append(nm)
    return not st and "<" not in _NBRW_TAG.sub("", s) and ">" not in _NBRW_TAG.sub("", s)

def _nbrw_markup(s):
    """A piece with real markup (a tag with attributes: a node, a box) is no
    text: doubling it would double the element (a timeline node twice)."""
    return any(not _re30.fullmatch(r"</?[a-zA-Z][a-zA-Z0-9]*\s*/?>", t) for t in _NBRW_TAG.findall(s))

def _nbrw_pairs():
    import html as _h
    run = LANG["value"]
    out = {}
    seen = list(_NBL_SEEN.items())
    # a long piece of markup (the title card) is split before it is shown: its
    # texts between the tags pair up one by one where both have the same tags
    for en, de in list(seen):
        if "<" not in en:
            continue
        te, td = _NBRW_TAG.findall(en), _NBRW_TAG.findall(de)
        nm = lambda ts: [_re30.sub(r"[\s/]", "", t.split(None, 1)[0]).lower() for t in ts]
        if len(te) < 2 or nm(te) != nm(td):
            continue
        for x, y in zip(_NBRW_TAG.split(en), _NBRW_TAG.split(de)):
            x, y = x.strip(), y.strip()
            if x != y and len(x) >= 8 and (" " in x or len(x) >= 12):
                seen.append((x, y))
        # …and so do their tooltips (title="%s · visualisation for this chapter")
        ax = r"""\s(%s)=(?:"([^"]*)"|'([^']*)')""" % "|".join(_NBRW_ATTRS)
        for x, y in zip(te, td):
            vx = {m.group(1): m.group(2) if m.group(2) is not None else m.group(3) for m in _re30.finditer(ax, x)}
            vy = {m.group(1): m.group(2) if m.group(2) is not None else m.group(3) for m in _re30.finditer(ax, y)}
            for k in vx:
                if k in vy and vx[k] != vy[k] and len(vx[k]) >= 8:
                    seen.append((vx[k], vy[k]))
    tpl = []
    for en, de in seen:
        a, b = (de, en) if run == "de" else (en, de)
        if (_DE_PH.search(a) and "%(" not in a and not _re30.search(r"%[^sdgfiu%]", _DE_PH.sub("", a))
                and len(_re30.findall(r"[A-Za-zÄÖÜäöüß]", _DE_PH.sub("", a))) >= 6 and _nbrw_balanced(a)
                and len(_DE_PH.findall(a)) == len(_DE_PH.findall(b)) and not _nbrw_markup(a)):
            tpl.append((a, b))
            continue
        for x, y in ((a, b), (_h.escape(a, quote=False), _h.escape(b, quote=False))):
            if (len(x.strip()) < 3 or not _re30.search(r"[A-Za-zÄÖÜäöüß]{2}", x) or _DE_PH.search(x)
                    or x in out or not _nbrw_balanced(x) or _nbrw_markup(x)):
                continue
            out[x] = y
    out[None] = tpl                         # %-templates: (run's, other's)
    return out

def _nbrw_tpl_rx(a):
    ms = list(_DE_PH.finditer(a))
    parts, pos = [], 0
    for n, m in enumerate(ms):
        parts.append(_re30.escape(a[pos:m.start()]))
        if m.group(3) == "%":
            parts.append("%")
        elif m.group(3) in "diu":
            parts.append(r"([−+-]?\d+)")
        elif m.group(3) in "eEfFgG":
            parts.append(r"([−+-]?\d+(?:[.,]\d+)?(?:[eE][−+-]?\d+)?)")
        elif n == 0 and m.start() == 0:
            parts.append(r"(?:^|(?<=>))([^<>]{1,80}?)")   # first: from the start of its text
        elif m.end() == len(a):
            parts.append(r"([^<>]{1,80})")            # last: up to the next tag
        else:
            parts.append(r"([^<>]{1,80}?)")
        pos = m.end()
    parts.append(_re30.escape(a[pos:]))
    return _re30.compile("".join(parts))

def _nbrw_fill(b, vals, pairs, run):
    out, pos, i = [], 0, 0
    for m in _DE_PH.finditer(b):
        out.append(b[pos:m.start()]); pos = m.end()
        if m.group(3) == "%":
            out.append("%"); continue
        v = vals[i] if i < len(vals) else ""; i += 1
        if v in pairs:
            v = pairs[v]
        elif _re30.search(r"[A-Za-zÄÖÜäöüß]{3}", v or "") and len(v) < 200:
            v = _nbrw_other(v, pairs, whole=True)            # a value made from a pair itself
        if _re30.fullmatch(r"[−\-+]?\d+(?:[.,]\d+)?", v or ""):
            v = v.replace(",", ".") if run == "de" else _de_dec(v)
        out.append(v)
    out.append(b[pos:])
    return "".join(out)

def _nbrw_bi(h, pairs=None, enc=False):
    import bisect
    pairs = _nbrw_pairs() if pairs is None else pairs
    if not h or not pairs:
        return h
    run = LANG["value"]
    oth = "de" if run == "en" else "en"
    lists = []
    for rx in (_NBRW_TAG, _NBRW_SKIP):      # each: sorted, without overlaps
        iv = [(m.start(), m.end()) for m in rx.finditer(h)]
        lists.append(([x[0] for x in iv], iv))
    def inside(p):                          # strictly inside a tag or a skipped block
        for st, iv in lists:
            j = bisect.bisect_left(st, p) - 1
            if j >= 0 and iv[j][1] > p:
                return True
        return False
    def wordy(c):
        return c.isalnum() or c == "_"
    cand = []
    for k in sorted((k for k in pairs if k is not None), key=len, reverse=True):
        i = h.find(k)
        while i >= 0:
            e = i + len(k)
            if not ((wordy(k[0]) and i > 0 and wordy(h[i - 1])) or (wordy(k[-1]) and e < len(h) and wordy(h[e]))):
                cand.append((i, e, k))
            i = h.find(k, e)
    other = {}
    for a, b in pairs.get(None) or ():
        try:
            rx = _nbrw_tpl_rx(a)
        except Exception:
            continue
        for m in rx.finditer(h):
            i, e = m.span()
            k = m.group(0)
            if k in pairs or i == e:
                continue
            other[(i, e)] = _nbrw_fill(b, m.groups(), pairs, run)
            cand.append((i, e, k))
    cand.sort(key=lambda c: c[0] - c[1])     # longest first
    took, starts = [], []
    for i, e, k in cand:                    # longest first; a piece never overlaps another
        j = bisect.bisect_left(starts, i)
        if (j < len(took) and took[j][0] < e) or (j > 0 and took[j - 1][1] > i):
            continue
        if inside(i) or inside(e):
            continue
        took.insert(j, (i, e, k)); starts.insert(j, i)
    # no sentence in two languages: where a piece would leave words of the run's
    # language in the same run of text (between two tags other than <b>/<i>/…),
    # a single word there (Check, exercise) stays as it is; a phrase (a title,
    # a goal: ≥ 2 words, ≥ 10 characters) is a text of its own and turns
    brk = [m.span() for m in _NBRW_TAG.finditer(h) if not _re30.fullmatch(_NBRW_INLINE, m.group(0))]
    bst = [x[0] for x in brk]
    def unit(p):
        j = bisect.bisect_right(bst, p) - 1
        return (brk[j][1] if j >= 0 else 0), (brk[j + 1][0] if j + 1 < len(brk) else len(h))
    groups = {}
    for t in took:
        u0, u1 = unit(t[0])
        while True:
            groups.setdefault((u0, u1), []).append(t)
            if u1 >= t[1] or u1 >= len(h):
                break
            u0, u1 = unit(u1 + 1)
    drop = set()
    for (u0, u1), ts in groups.items():
        seg = list(h[u0:u1])
        for i, e, k in ts:
            for q in range(max(i, u0), min(e, u1)):
                seg[q - u0] = " "
        rest = _NBRW_TAG.sub(" ", _NBRW_SKIP.sub(" ", "".join(seg)))
        if _re30.search(r"[A-Za-zÄÖÜäöüß]{2}", __import__("html").unescape(rest)):
            # …a single word (Check, exercise) goes; a phrase (a title, a goal) is a text of its own
            drop.update(t for t in ts if len(_NBRW_TAG.sub("", t[2]).strip().split()) < 2
                        or len(_NBRW_TAG.sub("", t[2]).strip()) < 10)
    took = [t for t in took if t not in drop]
    out, pos = [], 0
    for i, e, k in took:
        o = other.get((i, e)) if (i, e) in other else pairs[k]
        if enc:                             # E33 A1: the other language only in an attribute (_nbrw_static)
            out += [h[pos:i], "<span data-nbrw-l='%s' data-nbrw-t data-nbrw-o='%s'>%s</span>"
                    % (run, __import__("html").escape(o, quote=True), k)]
        else:
            out += [h[pos:i], "<span data-nbrw-l='%s' data-nbrw-t>%s</span><span data-nbrw-l='%s' data-nbrw-t hidden>%s</span>"
                    % (run, k, oth, o)]
        pos = e
    out.append(h[pos:])
    return "".join(out)

def _nbrw_other(t, pairs, whole=False):
    """`t` (plain text, the run's language) in the other language, piece by
    piece as _nbrw_bi finds them; what it does not know stays. whole=True: only
    when no word of `t` is left untranslated (else `t`)."""
    h = _nbrw_bi(t, pairs)
    if h == t:
        return t
    if whole and _re30.search(r"[A-Za-zÄÖÜäöüß]{2}", _re30.sub(
            r"<span data-nbrw-l='\w\w' data-nbrw-t>.*?</span><span data-nbrw-l='\w\w' data-nbrw-t hidden>.*?</span>", "", h,
            flags=_re30.S)):
        return t
    h = _re30.sub(r"<span data-nbrw-l='\w\w' data-nbrw-t>.*?</span><span data-nbrw-l='\w\w' data-nbrw-t hidden>(.*?)</span>",
                  lambda m: m.group(1), h, flags=_re30.S)
    return h

_NBRW_ATTRS = ("title", "aria-label", "placeholder", "alt", "data-desc")

def _nbrw_attrs(h, pairs):
    """Every title / aria-label / placeholder / alt / data-desc that has words of
    a pair gets both languages as on the cover (claude/VERTRAG-E29-py.md):
    the run's value stays, data-nbl-en / data-nbl-de = JSON {attr: value}."""
    import html as _h, json as _json
    run = LANG["value"]
    oth = "de" if run == "en" else "en"
    js = lambda d: _h.escape(_json.dumps(d, ensure_ascii=False, separators=(",", ":")), quote=True)
    def one(m):
        t = m.group(0)
        if t.startswith("<!--") or t.startswith("</") or "data-nbl-" in t:
            return t
        a, b = {}, {}
        for am in _re30.finditer(r"""\s(%s)=(?:"([^"]*)"|'([^']*)')""" % "|".join(_NBRW_ATTRS), t):
            v = _h.unescape(am.group(2) if am.group(2) is not None else am.group(3))
            o = _nbrw_other(_h.escape(v, quote=False), pairs, whole=True)
            o = _h.unescape(o)
            if o != v:
                a[am.group(1)], b[am.group(1)] = v, o
        if not a:
            return t
        cut = len(t) - (2 if t.endswith("/>") else 1)
        return t[:cut] + " data-nbl-%s='%s' data-nbl-%s='%s'" % (run, js(a), oth, js(b)) + t[cut:]
    return _NBRW_TAG.sub(one, h)

# E30 B6 (2026-10-12, Python) — THE TIMELINE OF LAB IN THE WINDOW (one panel logic
# for two hosts, STOP E30 B6). The reading copy carries the panel's own markup
# (_prog_html: nodes, pips with their states, locks, XP bars, the here-mark) in a
# <template class="nbrw-rail"> — inert, so JupyterLab's page never finds a second
# panel in it (lab_same) and nothing shows without script. Targets point into
# the reading copy (href="#nbr-…", data-target="nbr-…"); visible labels carry
# both languages ([data-nbrw-l], as the document), title / aria-label carry
# data-nbl-en / -de (as the cover). The window's script clones template.content.
def _nbrw_rail(pairs):
    h = _prog_html()
    if '<div class="nbprog"' in h:          # the still strip repeats the map: not needed
        h = h[:h.find('<div class="nbprog"')]
    h = _re30.sub(r"""(\shref=)(["'])#(?!nbr-)(?=[^"'])""", r"\1\2#nbr-", h)
    h = _re30.sub(r"""(\sdata-target=)(["'])(?!nbr-)""", r"\1\2nbr-", h)
    h = _nbrw_attrs(_nbrw_bi(h, pairs), pairs)
    return "<template class='nbrw-rail' data-lang='%s'>%s</template>" % (LANG["value"], h)

def _nbread_html():
    # the pictures of locked chapters wait for their lock (Paket 21b); where the
    # reading version is all a reader gets (front ends that draw every output
    # in a frame of its own) they are drawn now — ~1 s, never in Lab or Lite
    if kernel_env() in ("pycharm", "colab") or __import__("os").environ.get("DIGICHEM_READ_ALL") == "1":
        for ent in list(_LOCKS.values()):
            _lazy_run(ent.pop("lazy", ()))
    body = []
    _NBREAD["acc_task"] = {id(a): k for k, a in _TASKS["acc"].items()}     # chapter fold → its exercise (gates)
    _NBREAD["acc_n"] = {}
    for e in _NBREAD["buf"]:
        d = _nbread_data(e)
        wv = d.get("application/vnd.jupyter.widget-view+json")
        if wv:
            w = _nbread_widget((wv or {}).get("model_id"))
            if w is not None:
                _nbread_w(w, 2, body)
    toc = []
    # E26.3: the chapters' names in both languages (build: _NBRW_TITLES) — the
    # window switches language at once; without script the run's one shows
    tt = globals().get("_NBRW_TITLES") or {}
    nch = [e for e in _STRUCT if e.get("kind") == "chapter" and e.get("anchor")]
    two = bool(nch) and all(len(tt.get(l) or ()) == len(nch) for l in ("en", "de"))
    for i, ent in enumerate(nch):
        if two and not _NBRW_ENC:
            name = "".join("<span data-nbrw-l='%s'>%s</span>" % (l, _esc_txt(str(tt[l][i]))) for l in ("en", "de"))
        elif two:                           # E33 A1: the run's name, the other one in data-nbrw-o
            _o = "de" if LANG["value"] == "en" else "en"
            name = "<span data-nbrw-l='%s' data-nbrw-o='%s'>%s</span>" % (
                LANG["value"], __import__("html").escape(_esc_txt(str(tt[_o][i])), quote=True),
                _esc_txt(str(tt[LANG["value"]][i])))
        else:
            name = _esc_txt(str(ent.get("title") or ""))
        toc.append("<li><a href='#nbr-%s'>%s</a></li>" % (_aid(ent["anchor"]), name))
    card = _nbread_ids(_NB_TITLE.get("html") or "")
    try:                                    # E30 B2: both languages in the document
        _pp = _nbrw_pairs()
        card, body = _nbrw_bi(card, _pp, enc=_NBRW_ENC), [_nbrw_bi("".join(body), _pp, enc=_NBRW_ENC)]
    except Exception:
        _pp = {}
    try:                                    # E30 B6: Lab's timeline for the window's panel
        rail = _nbrw_rail(_pp)
    except Exception:
        rail = ""
    if card:
        card = "<div style='text-align:center;margin:0 0 8px'>%s</div>" % card
    try:
        gate = " data-nbrw-mode='%s' data-rw-gate='%s'" % (_nbrw_attr(MODE["value"]), _nbrw_b64(_nbrw_gate()))
    except Exception:
        gate = ""
    try:
        cover = _nbrw_cover()
    except Exception:
        cover = ""
    toc = "<ol class='nbread-toc'>%s</ol>" % "".join(toc) if toc else ""
    card, toc, body = _nbrw_inl(card), _nbrw_inl(toc), [_nbrw_inl("".join(body))]
    if _NBRW_ENC:                           # E33 A1: readable without the stylesheet (restored by _NBRW_REHYD)
        card, toc, body = _nbrw_cols(card), _nbrw_cols(toc), [_nbrw_cols(body[0])]
        gate += " style='%s' data-nbrw-s=''" % _NBRW_PAGE
    return ("<div class='nbreading' lang='%s' data-nbread='1'%s>%s%s<div class='nbread-line'>%s</div>%s%s%s%s</div>"
            % (LANG["value"], gate, _NBREAD_CSS, _nbrw_put(cover), _nbread_line(), card,
               toc, "".join(body), _nbrw_put(rail)))

# E33 A1 (2026-10-13, Python; Nutzer 13.10.: a saved output opened in Lab, Lite,
# PyCharm "not trusted" showed the reading version IN BOTH LANGUAGES — "Notebook
# titleTitel des Notebooks" — and its boxes grey on grey in Lab dark). MEASURED
# (JupyterLab 4.6, not trusted, tests/regress/py_e33.py): the sanitizer drops
# <style>, <script>, <svg>, <template> (keeping its TEXT), every data-* and an
# EMPTY attribute (`hidden`), and a style declaration whose value is var(…). The
# E30 markup hid the other language with exactly those. Now the STATIC reading
# version holds the run's language only: the other one of a pair lives in the
# attribute data-nbrw-o of the run's element (_nbrw_bi enc), the preview and
# Lab's timeline (shown by script only) in <script type=application/json
# data-nbrw-put> at their old places — nothing of either is text without a
# script. Where our script runs, _NBRW_REHYD (first, in the same <script> as
# 20-reader.js) builds the v1.78 markup back, element for element, so the
# window, its EN|DE and CSS see what they saw (claude/VERTRAG-E33-py.md).
# Colours: a declaration prop:var(--x, v) gets prop:v in front of it — the same
# picture where the variable exists, readable where the sanitizer drops it.
_NBRW_ENC = True                            # False: the v1.78 markup (tests/regress/py_e33.py R1 compares)

def _nbrw_put(h):
    if not h or not _NBRW_ENC:
        return h
    import json as _json
    return "<script type='application/json' data-nbrw-put>%s</script>" % _json.dumps(
        h, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e")

_NBRW_VARDECL = _re30.compile(r"(^|;)(\s*)([a-z-]+)\s*:\s*var\(\s*--[\w-]+\s*,\s*((?:[^();]|\([^()]*\))+?)\s*\)\s*(?=;|$)")

def _nbrw_inl(h):
    def sty(m):
        q, v = m.group(1), m.group(2)
        def one(d):
            pre = v[:d.start()]
            if _re30.search(r"(^|;)\s*%s\s*:" % _re30.escape(d.group(3)), pre):
                return d.group(0)
            return "%s%s%s:%s;%s" % (d.group(1), d.group(2), d.group(3), d.group(4).strip(), d.group(0)[len(d.group(1)):])
        return " style=%s%s%s" % (q, _NBRW_VARDECL.sub(one, v), q)
    return _re30.sub(r"""\sstyle=(["'])(.*?)\1""", sty, h)

# …and its own page: the static copy is a light page with dark ink of its own
# (inline: a front end's dark theme gave its text light ink on our light boxes),
# links and the light greys of the card darkened to ≥ 4.5 : 1 — each changed
# element keeps its original style in data-nbrw-s ('' = had none), put back by
# _NBRW_REHYD: where our script runs, the window and Lab see the v1.78 colours.
_NBRW_PAGE = "background:#ffffff;color:#1f2328;padding:14px 18px;border-radius:12px"
_NBRW_INK = {"#7a8794": "#56616c", "#8b98a5": "#56616c", "#9aa5b1": "#56616c", "#5b6b7b": "#4e5c6a"}

def _nbrw_cols(h):
    import html as _hh
    def tag(m):
        t, name = m.group(0), m.group(1).lower()
        sm = _re30.search(r"""\sstyle=(["'])(.*?)\1""", t)
        st = _hh.unescape(sm.group(2)) if sm else ""
        new = st
        for a_, b_ in _NBRW_INK.items():
            new = _re30.sub(r"(?i)(color\s*:\s*)%s\b" % a_, r"\g<1>" + b_, new)
        if name == "a" and not _re30.search(r"(^|;)\s*color\s*:", new):
            new = (new.rstrip("; ") + ";" if new.strip() else "") + "color:#0b57d0"
        if name == "tr" and not _re30.search(r"(^|;)\s*background", new):     # Lab dark paints table rows dark
            new = (new.rstrip("; ") + ";" if new.strip() else "") + "background:transparent"
        if name in ("table", "th", "td") and not _re30.search(r"(^|;)\s*color\s*:", new):   # …and inks them light
            new = (new.rstrip("; ") + ";" if new.strip() else "") + "color:#1f2328"
        if new == st:
            return t
        keep = " data-nbrw-s='%s'" % _hh.escape(st, quote=True)
        if sm:
            return t[:sm.start()] + " style='%s'" % _hh.escape(new, quote=True) + t[sm.end():-1].rstrip("/") + keep + ">"
        return t[:-1].rstrip("/") + " style='%s'%s>" % (_hh.escape(new, quote=True), keep)
    return _re30.sub(r"<([a-zA-Z][a-zA-Z0-9]*)\b[^<>]*>", tag, h)

_NBRW_REHYD = r"""(function(){var me=document.currentScript,r=null;
if(me){var p=me.previousElementSibling;if(p&&p.classList&&p.classList.contains('nbreading'))r=p;}
if(!r&&me&&me.closest)r=me.closest('.nbreading');
if(!r){var a=document.querySelectorAll('.nbreading:not([data-nbrw])');r=a.length?a[a.length-1]:null;}
if(!r||r.getAttribute('data-nbrw-rh'))return;r.setAttribute('data-nbrw-rh','1');
[].forEach.call(r.querySelectorAll('[data-nbrw-s]'),function(e){var v=e.getAttribute('data-nbrw-s');
if(v)e.setAttribute('style',v);else e.removeAttribute('style');e.removeAttribute('data-nbrw-s');});
if(r.hasAttribute('data-nbrw-s')){r.removeAttribute('style');r.removeAttribute('data-nbrw-s');}
[].forEach.call(r.querySelectorAll('script[data-nbrw-put]'),function(s){try{var t=document.createElement('template');
t.innerHTML=JSON.parse(s.textContent);s.parentNode.replaceChild(t.content,s);}catch(e){}});
[].forEach.call(r.querySelectorAll('[data-nbrw-o]'),function(e){var o=e.getAttribute('data-nbrw-o'),
l=e.getAttribute('data-nbrw-l')==='de'?'en':'de',t=e.hasAttribute('data-nbrw-t'),n=e.cloneNode(false);
e.removeAttribute('data-nbrw-o');n.removeAttribute('data-nbrw-o');n.setAttribute('data-nbrw-l',l);
if(t)n.setAttribute('hidden','');n.innerHTML=o;e.parentNode.insertBefore(n,(!t&&l==='en')?e:e.nextSibling);});})();
"""

def _nbread_js():
    """E26 Teil 2 (JS): the reading window — shipped INSIDE the reading
    version's output (a viewer that draws every output in a page of its own
    runs only the script of that output). It starts only where no notebook
    front end hosts the page and no widget of ours is drawn (20-reader.js)."""
    js = r"""
//@include js/20-reader.js
"""
    return "<script>%s</script>" % (_NBRW_REHYD + js).replace("__NBREADV__", TOOLKIT_VERSION).replace(
        "__NBREADID__", str(NOTEBOOK.get("id") or "nb")).replace("</", "<\\/")

_NBREAD_WARM = ("nbtitle-doc", "nbcover-out")

# E26.1b (PyCharm 2025.2.3, 11.10., v1.70) — WIDGET OUTPUTS ARE HELD TOO.
# PyCharm draws ipywidgets itself, each output in a page of its own, without
# our stylesheet: the panel's HBox (progress_panel) came out under the
# reading version as a white "Your progress" card with an unstyled timeline.
# `.nbwarm` only wrapped text/html outputs; a widget output has no HTML to
# wrap. So every top-level widget output gets a held layout (height 0,
# overflow hidden, visibility hidden — inline, from the layout model, in any
# widget renderer: no text and no empty height under the reading version) and
# the class `nbhold`. Where our widgets are drawn in the same page the
# stylesheet lifts height and visibility at once (`.nb-live`, `:has(.acc-root)`,
# 01-base) and the page script takes the three inline values off (10-rail-host,
# so the widgets' own overflow rules apply again) — the page of v1.70.
def _nbread_hold(d):
    wv = d.get("application/vnd.jupyter.widget-view+json")
    if not wv:
        return
    w = _nbread_widget((wv or {}).get("model_id"))
    lay = getattr(w, "layout", None)
    if lay is None or lay.display == "none" or (lay.height or "") in ("0", "0px"):
        return
    lay.visibility, lay.height, lay.overflow = "hidden", "0px", "hidden"
    w.add_class("nbhold")

def _nbread_end(*_a):
    """Let the kept outputs go: the reading version first, then all of them."""
    if not _NBREAD["on"] or _NBREAD["done"]:
        return
    _NBREAD["on"] = False
    _NBREAD["done"] = True
    try:
        _NBREAD["ip"].events.unregister("post_execute", _nbread_end)
    except Exception:
        pass
    pub, orig = _NBREAD["pub"], _NBREAD["orig"]
    pub.publish = orig
    try:
        h = _nbread_html() + _nbread_js()
    except Exception as ex:
        h = "<div class='nbreading' data-nbread='1'><!-- %s --></div>" % _esc_txt(repr(ex))[:200]
    # E31 W1 (2026-10-12, Python; PyCharm Video 1 zu v1.77: after a re-run the
    # output came and went — [3] cover, [4] empty). NOTHING CHANGES AN OUTPUT
    # AFTER THE WINDOW: the loading view is emptied BEFORE the reading version
    # goes out (it was right after it — the one display update of the run
    # came after the window). A viewer that drops or rebuilds a cell's
    # outputs on update_display_data can now only touch the loading view;
    # after the reading version the cell only appends. JupyterLab: the same
    # two outputs in the same state, a few µs apart (the loading view lives
    # on its own box, 02-loading). tests/regress/py_e31.py W1b/W1c.
    ld = globals().get("_NBLOADID")
    if ld:
        try:
            orig({"text/html": ""}, metadata={}, transient={"display_id": ld}, update=True)   # E33 D: no "…" row
        except Exception:
            pass
    try:
        orig({"text/html": h, "text/plain": ""}, metadata={})
    except Exception:
        pass
    for e in _NBREAD["buf"]:
        try:
            _nbread_hold(_nbread_data(e))
        except Exception:
            pass
        try:
            d = _nbread_data(e)
            hh = d.get("text/html")
            if (isinstance(hh, str) and "application/vnd.jupyter.widget-view+json" not in d
                    and any(k in hh[:600] for k in _NBREAD_WARM)):
                d = dict(d)
                d["text/html"] = "<div class='nbwarm' style='display:none'>%s</div>" % hh
                a, kw = e
                if a:
                    a = (d,) + tuple(a[1:])
                else:
                    kw = dict(kw, data=d)
                e = [a, kw]
            orig(*e[0], **e[1])
        except Exception:
            pass
    _NBREAD["kept"] = _NBREAD["buf"]        # E33: the run's outputs, for a later _nbread_html (py_e33 R1)
    _NBREAD["buf"] = []

_nbread_begin()

# ======================================================================
# E17.5 (2026-10-02, Applikation) — THE LANGUAGE OF THIS RUN: en | de.
# Decided ONCE, here, before any text of the toolkit or a chapter exists:
# every reader-facing literal the build knows a German for reaches the cell
# as _nbL("English", "Deutsch") (toolkit/i18n.py), evaluated as the cell runs.
# Where the choice comes from, first hit wins:
#   1. DIGICHEM_LANG (tests, a course server)
#   2. the stored choice of THIS notebook (E25.o, see _LANG_NS below; until
#      E25 a profile value shared by all notebooks, "digichemjn.lang.v1")
#   3. "en"
# As with the mode, the stored choice is read only in a real kernel: the build
# and the suites exec the notebook in plain Python (en unless DIGICHEM_LANG).
# The page hands a choice to a server kernel through the ⚙ "Language"
# dropdown (controls: lang_store), exactly like the mode; the feed says what
# this run built (data-nblang).
# ======================================================================
LANGS = ("en", "de")
LANG = {"value": "en", "source": "default"}

def _lang_pyo():
    import sys
    return "pyodide" in sys.modules or sys.platform == "emscripten"

# E25.o (2026-10-08, Python) — THE LANGUAGE IS THIS NOTEBOOK'S, NOT THE
# BROWSER'S. Not logged in, a notebook keeps its own settings and takes
# nothing from another one (Nutzer 08.10.; replaces E16.10/E17 "profile
# shared" for the language). The stored choice is now per notebook, named
# like the mode: localStorage "digichemjn.lang.<id>" under JupyterLite,
# .digichemjn/<id>.lang in ~ and beside the notebook on a server kernel (the
# newer file wins). The old shared "digichemjn.lang.v1" / ".digichemjn/lang"
# is not read any more (no old users, E23.17: unknown keys are ignored). The
# id has to be known before the first text: the build writes it at the top
# of the cell (_NB_ID_EARLY); without it the run is English.
_LANG_NS = "digichemjn.lang."
# E34 P1/P2 (2026-10-19, Python) — THE STANDARD IS digi, DARK (Nutzer 19.10.:
# the notebooks look like the digi web site and the digi app, „Standardstil“).
# Only the start for a reader with nothing stored: a stored style or light/
# dark wins (JS, J1); light, „like the system“ and the other styles stay.
NB_DEFAULTS = {"skin": "digi", "theme": "dark", "lang": "en", "mode": "both",
               "zoom": 100, "panel": "default", "readline": "default"}

def _lang_id():
    i = globals().get("_NB_ID_EARLY") or (globals().get("NOTEBOOK") or {}).get("id")
    return i if i and i != "unnamed" else None

def _lang_paths():
    import os
    i = _lang_id()
    if not i:
        return []
    here = os.path.join(os.getcwd(), ".digichemjn", i + ".lang")
    if _lang_pyo():
        return [here]
    home = os.path.join(os.path.expanduser("~"), ".digichemjn", i + ".lang")
    return [home] if os.path.abspath(home) == os.path.abspath(here) else [home, here]

def _lang_real():
    if _lang_pyo():
        return True
    try:
        return get_ipython().__class__.__name__ == "ZMQInteractiveShell"   # noqa: F821
    except Exception:
        return False

def _lang_ls():
    if not _lang_pyo():
        return None
    try:
        import js
        return js.localStorage
    except Exception:
        return None

def lang_stored():
    """The stored language, or None. Never raises."""
    if not _lang_real():
        return None
    i = _lang_id()
    if not i:
        return None
    try:
        ls = _lang_ls()
        if ls is not None:
            v = ls.getItem(_LANG_NS + i)
        else:
            import os
            have = [q for q in _lang_paths() if os.path.isfile(q)]
            if not have:
                return None
            v = open(max(have, key=os.path.getmtime)).read()
        v = str(v).strip().lower()
        return v if v in LANGS else None
    except Exception:
        return None

def lang_store(value):
    """Remember `value` for the next run of THIS notebook (E25.o). True when written."""
    v = str(value).strip().lower()
    i = _lang_id()
    if v not in LANGS or not i:
        return False
    try:
        ls = _lang_ls()
        if ls is not None:
            ls.setItem(_LANG_NS + i, v)
            return True
        import os
        ok = False
        for q in _lang_paths():
            try:
                os.makedirs(os.path.dirname(q), exist_ok=True)
                with open(q, "w") as fh:
                    fh.write(v)
                ok = True
            except Exception:
                pass
        return ok
    except Exception:
        return False

def lang_page_js(value):
    """The page learns a choice made in Python (as mode_page_js)."""
    v = str(value).strip().lower()
    i = _lang_id()
    if v not in LANGS or not i:
        return ""
    import json as _json
    return "try{localStorage.setItem(%s,%s);}catch(e){}" % (_json.dumps(_LANG_NS + i), _json.dumps(v))

def notebook_lang():
    """Decide this run's language (called once, below)."""
    import os
    env = (os.environ.get("DIGICHEM_LANG") or "").strip().lower()
    if env in LANGS:
        LANG.update(value=env, source="env")
    else:
        st = lang_stored()
        LANG.update(value=st or "en", source="stored" if st else "default")
    return LANG["value"]

# E30 B2 (2026-10-12, Python) — THE READING COPY KEEPS BOTH WORDS. Every pair
# the run asks for is noted (_NBL_SEEN, English → German); the reading copy
# writes both where the run's text stands (_nbrw_bi), so EN|DE in the window
# turns the document too, not only the contents list and the panel.
_NBL_SEEN = {}

def _nbL(en, de):
    """The reader's language: `de` when this run is German, else `en`."""
    # by name in a string: the check shipped as text to the window (_nbrw_pysrc)
    # follows the names it calls and must not carry this table along
    seen = globals().get("_NBL_SEEN")
    if seen is not None and en != de and type(en) is str and isinstance(de, str) and len(seen) < 20000:
        seen[en] = str(de)
    return _De(de) if LANG["value"] == "de" else en

# E22.2 (2026-10-04, Inhalt + Applikation) — GERMAN NUMBERS HAVE A COMMA. The
# German tables write 2,5 in the text; what the program fills in at run time
# (%g, %.4f, a number made by fnum) must follow, or a German sentence says
# "Ihr Imaginärteil war 1.5". A German literal is a _De: `_De % args` formats
# every placeholder on its own and gives a decimal comma to the numbers it
# put there — never to the template (that is the table's job), never inside
# <code>…</code> or a call written out, "roots_of(%g)" (Python keeps its
# point), never to %r (a Python repr) and to a %s only when the value is a
# number or a string that is nothing but a number ("2.5 − 1.2i"); a %s that
# carries HTML or a tuple stays as it is. Anything unusual falls back to str %.
import re as _re22
_DE_PH = _re22.compile(r"%(?:\(([^)]*)\))?([-+ #0]*\d*(?:\.\d+)?)([sdiouxXeEfFgGcr%])")
_DE_NUMSTR = _re22.compile(r"^[\s\d.,+\-−±·×/eEijπ°]*\d[\s\d.,+\-−±·×/eEijπ°]*$")
_DE_CALL = _re22.compile(r"\w\([^()]*$")

def _de_dec(s):
    return _re22.sub(r"(?<=\d)\.(?=\d)", ",", s)

class _De(str):
    """A German literal: its %-formatting writes numbers with a decimal comma."""
    __slots__ = ()
    def __mod__(self, args):
        try:
            return self._fmt(args)
        except Exception:
            return str.__mod__(str(self), args)
    def _fmt(self, args):
        tpl = str(self)
        ms = list(_DE_PH.finditer(tpl))
        named = any(m.group(1) is not None for m in ms)
        seq = None if named else (args if isinstance(args, tuple) else (args,))
        out, pos, i = [], 0, 0
        for m in ms:
            out.append(tpl[pos:m.start()]); pos = m.end()
            name, flags, conv = m.groups()
            if conv == "%":
                out.append("%"); continue
            if named:
                v = args[name]
            else:
                v = seq[i]; i += 1
            piece = ("%" + flags + conv) % (v,)
            before = tpl[:m.start()]
            code = before.count("<code") > before.count("</code") or _DE_CALL.search(before)
            num = conv in "eEfFgG" or (conv == "s" and (
                (isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, bool))
                or (isinstance(v, str) and "<" not in v and _DE_NUMSTR.match(v))))
            out.append(_de_dec(piece) if num and not code else piece)
        if seq is not None and i != len(seq):
            raise TypeError("not all arguments converted")
        out.append(tpl[pos:])
        return "".join(out)

def _de_num(v):
    """A readout value in the reader's language (E22.2): in a German run its
    numbers get a decimal comma ("0.35 /h" → "0,35 /h"; markup is left alone)."""
    if LANG["value"] != "de":
        return v
    if isinstance(v, (float, np.floating)):
        v = "%g" % v
    if isinstance(v, str) and "<" not in v:
        return _de_dec(v)
    return v

def _parse_num(s):
    """A number as a reader types it: 2.5 or 2,5 (E22.2), −2,5, 1 234,5 or
    1.234,5 / 1,234.5 (the last separator is the decimal one). None when it
    is no number (yet): "", "-", "1,", "√2"."""
    t = str(s).strip().replace("−", "-").replace("\u2212", "-")
    for sp in (" ", "\u00a0", "\u202f", "'"):
        t = t.replace(sp, "")
    if "," in t and "." in t:
        if t.rfind(",") > t.rfind("."):
            t = t.replace(".", "").replace(",", ".")
        else:
            t = t.replace(",", "")
    else:
        t = t.replace(",", ".")
    try:
        v = float(t)
    except ValueError:
        return None
    return v if np.isfinite(v) else None

notebook_lang()

# 2026-09-24be — NOTHING MATPLOTLIB SAYS TO ITSELF REACHES THE READER.
# MEASURED in a real JupyterLite (Pyodide ships matplotlib 3.10): every picture
# drawn through `_png` emitted eight MatplotlibDeprecationWarnings — "The width
# parameter as float was deprecated" and its siblings — straight into the
# output, so the Introduction opened with a red block forty lines long. They
# come from inside Agg, from figsize x dpi not being a whole number after
# bbox_inches="tight"; there is nothing the reader, or this file, can do about
# them, and a warning nobody can act on is noise. The same filter also covers
# the older JupyterLab installs, where matplotlib is quieter only by accident
# of version. Real errors still raise, and our own warnings are untouched.
try:
    from matplotlib import MatplotlibDeprecationWarning as _mplDW
    _warnings.filterwarnings("ignore", category=_mplDW)
except Exception:
    pass
_warnings.filterwarnings("ignore", category=DeprecationWarning, module="matplotlib")
_warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"mpl_toolkits.*")

# ======================================================================
# DESIGN TOKENS  — edit here to restyle the whole notebook
# ======================================================================
DESIGN = dict(
    box_maxw   = "880px",
    text_w     = "700px",                       # width used for justified prose
    radius     = "14px",
    formula = dict(bg="linear-gradient(180deg,#eef4fb,#f6faff)", border="4px solid #7fb0cd",
                   ink="#243b53", label="#5b6b7b"),
    viz     = dict(bg="linear-gradient(90deg,#fdeef5,#fff8fb)", border="1px solid #f3cfe0",
                   head="#8a3b63", ink="#6b4a5e", accent="#b64a86", rule="#ecc9dc",
                   hrule="#d9b3c8"),
    ex      = dict(bg="linear-gradient(90deg,#fdecec,#fff6f6)", border="1px solid #f2caca",
                   head="#922b21", ink="#7a4a4a"),
    sol     = dict(bg="linear-gradient(90deg,#e7f4ec,#f5fbf7)", border="1px solid #bfe0cd",
                   head="#155e43", ink="#1e5f43"),
    interp  = dict(bg="linear-gradient(180deg,#ecf9f2,#f6fdfa)", border="4px solid #7fc9a8",
                   head="#2f8f6f", ink="#33475b"),
    warn    = dict(bg="linear-gradient(90deg,#fdecec,#fff7f6)", border="1px solid #e3a59d"),
    # accordion title-pill gradients
    pill_chapter = "linear-gradient(90deg,#245f80,#3f8fb5)",
    pill_viz     = "linear-gradient(90deg,#c85fa0,#e2a0c6)",
    pill_practice= "linear-gradient(90deg,#c0392b,#d9695c)",
    pill_group   = "linear-gradient(90deg,#33475a,#527189)",   # top level: overview + section groups
)
_BOXCSS = "margin:12px auto;border-radius:%s;padding:16px 24px;" % DESIGN["radius"]

# ======================================================================
# core helpers
# ======================================================================
def fnum(x):
    """Compact number for on-screen display (≤3 dp normal, else 1-dp exponential)."""
    x = float(x)
    if not np.isfinite(x): return "∞" if x > 0 else ("-∞" if x < 0 else "nan")
    a = abs(x)
    return f"{x:.3f}" if (a == 0 or 1e-3 <= a < 1e4) else f"{x:.1e}"

def center(w):
    """The one centring method that works in JupyterLite: full-width HBox, justify centre."""
    return HBox([w], layout=Layout(width="100%", justify_content="center"))

# --- citation registry: numbers follow the ORDER sources first appear in the text ---
# cite() takes STABLE source ids (the fixed keys 1..N used in the chapters and in the
# bibliography); the registry maps each stable id to a DISPLAY number the first time it
# is cited, so the printed [n] run 1, 2, 3, … in reading order and a reused source keeps
# its first number. The References chapter reads the same registry to list the entries
# in that order with matching id="ref{n}" anchors.
_CITEREG = {"order": [], "num": {}}

# Every jump anchor id and every link target is suffixed with this per-run token.
# JupyterLab keeps ALL open notebooks in ONE shared DOM, so if an older version of
# this notebook is open in another tab the plain ids (ref1, ch2, grptop1 …) would be
# duplicated and getElementById would resolve to the wrong notebook — breaking the
# links. A unique token per run makes every id globally unique, so the table of
# contents, the [n] citation links and the "back to …" lines always resolve to THIS
# notebook's own anchors, no matter what else is open.
import random as _random
import re as _re
_NBID = format(_random.getrandbits(32), "08x")
def _aid(base):
    """Anchor/link id for `base`, made unique to this notebook run."""
    return "%s__%s" % (base, _NBID)

def _cite_num(sid):
    if sid not in _CITEREG["num"]:
        _CITEREG["order"].append(sid)
        _CITEREG["num"][sid] = len(_CITEREG["order"])
    return _CITEREG["num"][sid]

def cite(*sids):
    """In-text source marker written on the baseline (normal size, not superscript):
    "[n]" or "[n, m]". Numbers are assigned in first-appearance order via the registry
    above and link to the matching References entry id="ref{n}". A leading space keeps
    the marker off the preceding word."""
    nums = sorted({_cite_num(s) for s in sids})   # register in argument order, show sorted
    links = ", ".join(
        "<a class='nbjump cite-link' data-target='%s' href='#%s'>%d</a>" % (_aid("ref%d" % n), _aid("ref%d" % n), n)
        for n in nums)
    return " [%s]" % links

def _w(maxw=None):
    return Layout(width="fit-content", max_width=maxw or DESIGN["box_maxw"])

MATH_INK = "#1a1a1a"   # every rendered formula / value is typeset in black
_MATH_EM_BASE = 14.3   # px of the document text at 100 % (E29 D7) — a formula given in px is that many / 14.3 em
_MATH_BOLD = 0.5       # stroke width (px) that renders every formula in bold
def math_img(tex, fs=26, color=None, height=52, valign="middle"):
    """Render a LaTeX string to a centred, crisp transparent PNG <img> tag (bold)."""
    color = MATH_INK
    fig = plt.figure(figsize=(0.01, 0.01))
    t = fig.text(0, 0, tex, fontsize=fs, color=color)
    t.set_path_effects([_pe.withStroke(linewidth=_MATH_BOLD, foreground=color)])
    fig.canvas.draw()
    bb = t.get_window_extent()
    fig.set_size_inches(bb.width/fig.dpi + 0.3, bb.height/fig.dpi + 0.3)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, transparent=True, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    b64 = base64.b64encode(buf.getvalue()).decode()
    # E31 F1 (2026-10-12, Python; Nutzer zu v1.77: "A± skaliert ALLES") — the
    # height in em, not px: `height` stays the px the call meant at the
    # document's text size (_MATH_EM_BASE), so 100 % looks as before and the
    # picture follows the text size (--nbfs) and every container's font
    return ('<img class="nbmath" src="data:image/png;base64,%s" style="height:%.4gem;vertical-align:%s">'
            % (b64, height / _MATH_EM_BASE, valign))

def _render_math_png(tex, fs, color):
    """Render a mathtext string to a transparent PNG (bold); return (base64, height_px).
    Kept for PLOT_FORMAT "png"-era callers; imath/dmath use _math_svg (Paket 21a)."""
    fig = plt.figure(figsize=(0.01, 0.01))
    t = fig.text(0, 0, tex, fontsize=fs, color=color)
    t.set_path_effects([_pe.withStroke(linewidth=_MATH_BOLD, foreground=color)])
    fig.canvas.draw()
    bb = t.get_window_extent()
    fig.set_size_inches(bb.width/fig.dpi + 0.05, bb.height/fig.dpi + 0.05)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, transparent=True, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode(), bb.height

# 2026-09-29 (Paket 21a, Applikation + Oberfläche) — FORMULAS ARE SVG, AND THE
# BUILD HAS ALREADY DRAWN THEM.
# COUNTED FIRST (v1.29, in-process profile): 68 mathtext PNGs took 3.7 of 7.4 s
# of the mega-cell; the same 61 distinct formulas as SVG take 0.8 s — the bold
# path effect and the 200-dpi PNG were the cost, not the typesetting. And a PNG
# is one ink: dark mode could only invert it (02-dark.css), the four styles
# could not reach it at all (E6.13 rest). Now:
#   • a formula is an inline <svg>, glyphs as paths, fill and stroke
#     `currentColor`, colour var(--nbskin-ink) → it takes the style's ink in
#     every style, light and dark, with no kernel;
#   • bold is the same 0.5 pt stroke as before, now an SVG stroke (the width is
#     given per <use> in the glyph's own units, so it is 0.5 pt at any size);
#   • the build runs the notebook for three fixed seeds, keeps the formulas all
#     three runs drew (the ones that do not depend on the seed), and writes them
#     into the cell (_MATH_PRE, glyphs once in _MATH_GLYPHS). At run time those
#     are a dict lookup; only a formula the build did not see (a seed-dependent
#     one, e.g. √q in exercise 1) is typeset here, by the same _math_svg.
# The glyph ids are made unique per formula at run time, so no <use> ever
# points into another (perhaps hidden) formula.
_MATH_PRE = {}      # "fs|tex" -> (h, W, H, "glyph ids", body) — filled by the build
_MATH_GLYPHS = {}   # glyph id -> path data — filled by the build
_MATH_REC = None    # the build sets a list here to see which formulas are drawn
_MATH_N = [0]
_SVG_NUM = _re.compile(r"(-?\d+\.\d+)")
# E10.8 (2026-09-30, Applikation): positions with one decimal. Inside a glyph
# group one unit is 0.16 px (0.2 at fs 20), so rounding moves a glyph by
# < 0.01 px; the group's own offset is in px and moves by < 0.05 px. About
# 1 400 numbers, each a character or more shorter.
# Glyph outlines come from matplotlib in 1/64 units; the cell keeps them in
# 1/8 (whole numbers, a digit shorter): 4 old units at most = 0.01 px at fs 16.
_GLS = 0.125
def _n1(v):
    v = ("%.1f" % float(v)).rstrip("0").rstrip(".")
    return "0" if v in ("-0", "") else v

def _math_svg(tex, fs):
    """Typeset `tex` at `fs` as SVG; return the compact form (h, W, H, ids, body)
    that _MATH_PRE stores. h is the text height in px at the figure dpi — the
    same number the PNG path used for its em sizing."""
    fig = plt.figure(figsize=(0.01, 0.01))
    t = fig.text(0, 0, tex, fontsize=fs, color="#000000")
    fig.canvas.draw()
    bb = t.get_window_extent()
    fig.set_size_inches(bb.width/fig.dpi + 0.05, bb.height/fig.dpi + 0.05)
    buf = io.StringIO()
    with plt.rc_context({"svg.fonttype": "path", "svg.hashsalt": "digichemjn"}):
        fig.savefig(buf, format="svg", transparent=True, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    svg = buf.getvalue()
    W, H = _re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups()
    for gid, d in _re.findall(r'<path id="([^"]+)" d="([^"]*)" transform="scale\(0\.015625\)"/>', svg):
        _MATH_GLYPHS.setdefault(gid, _re.sub(r"-?\d+(?:\.\d+)?", lambda m: str(round(float(m.group()) / 8)),
                                             _re.sub(r"\s*([MLQCz])\s*", r"\1", d).strip()))
    body = []
    for grp in _re.finditer(r'<g transform="translate\(([^)]*)\) scale\(([\d.]+) -[\d.]+\)">(.*?)</g>', svg, _re.S):
        tr, sg, inner = grp.group(1), float(grp.group(2)), grp.group(3)
        body.append('<g transform="translate(%s) scale(%s -%s)" stroke-width="%.4g">'
                    % (_SVG_NUM.sub(lambda m: _n1(m.group(1)), tr), grp.group(2), grp.group(2),
                       _MATH_BOLD / (sg * _GLS)))
        for u in _re.finditer(r'<use xlink:href="#([^"]+)"([^>]*?)/>', inner):
            gid, rest = u.groups()
            at = dict(_re.findall(r'(\w+)="([^"]*)"', rest))
            assert set(at) <= {"x", "y", "transform"}, at
            utr = at.get("transform", "")
            su = _re.search(r"scale\(([\d.]+)\)", utr)
            su = float(su.group(1)) if su else 1.0
            utr = _SVG_NUM.sub(lambda m: _n1(m.group(1)), utr)
            ex = "".join(' %s="%s"' % (n, at[n]) for n in ("x", "y") if n in at)
            # E10.8 (2026-09-30): a bare translate is written as x/y — half
            # the characters, the same place (no scale, so nothing multiplies)
            tm = _re.fullmatch(r"translate\((\S+) (\S+)\)", utr)
            if tm and not ex:
                ex = "".join(' %s="%s"' % (n, v) for n, v in zip("xy", tm.groups()) if v != "0")
            elif utr:
                ex += ' transform="%s"' % utr
            if su != 1.0:
                ex += ' stroke-width="%.4g"' % (_MATH_BOLD / (sg * su * _GLS))
            body.append('<use href="#@%s"%s/>' % (gid, ex))
        for d in _re.findall(r'<path d="([^"]*)"\s*/>', inner):
            d = _re.sub(r"\s*([MLQCz])\s*", r"\1", d).strip()
            d = _SVG_NUM.sub(lambda m: _n1(m.group(1)), d)
            body.append('<path d="%s" stroke-width="%.4g"/>' % (d, _MATH_BOLD / sg))
        body.append("</g>")
    ids = " ".join(sorted(set(_re.findall(r'href="#@([^"]+)"', "".join(body)))))
    return (bb.height, float(W), float(H), ids, "".join(body))

def _math_get(tex, fs):
    """The compact SVG of one formula: from the build's _MATH_PRE, else typeset now."""
    k = "%d|%s" % (fs, tex)
    if _MATH_REC is not None:
        _MATH_REC.append(k)
    v = _MATH_PRE.get(k)
    if v is None:
        v = _MATH_PRE[k] = _math_svg(tex, fs)
    return v

def _math_tag(v, cls, em, style=""):
    """The inline <svg> for a compact formula, `em` high, in the style's ink."""
    h, W, H, ids, body = v
    _MATH_N[0] += 1
    p = "m%d-" % _MATH_N[0]
    defs = "".join('<path id="%s%s" d="%s" transform="scale(%s)"/>'
                   % (p, g, _MATH_GLYPHS[g], _GLS) for g in ids.split())
    return ('<svg class="%s" viewBox="0 0 %s %s" fill="currentColor" stroke="currentColor" '
            'style="height:%sem;width:%sem;color:var(--nbskin-ink,%s);overflow:visible;%s">'
            '<defs>%s</defs>%s</svg>'
            % (cls, W, H, em, round(em * W / H, 3), MATH_INK, style, defs, body.replace("#@", "#" + p)))

_IMATH_REF = {}   # cache of the single-line reference height per font size
def imath(tex, color="#33475b", fs=16):
    """Inline math for prose: an SVG formula for an equation or value written inside
    the running text (for example w=b=0 or σ(0)=0.5), typeset like the formula boxes
    instead of plain text. The formula is sized in em RELATIVE to a one-line reference,
    so a single-line expression matches the surrounding prose and a fraction is given
    proportionally more height; it is centred on the line with vertical-align:middle.
    `tex` is a mathtext string WITHOUT the surrounding $…$ (they are added here)."""
    if fs not in _IMATH_REF:
        _IMATH_REF[fs] = _math_get(r"$0$", fs)[0]
    v = _math_get(r"$%s$" % tex, fs)
    # size in em relative to one text line; cap so an inline snippet never blows the
    # line height (feed compact, single-line expressions for inline use)
    em = round(min(1.9, max(1.0, v[0] / _IMATH_REF[fs]) * 1.15), 2)
    # E31 F1: the side margin in em too (2 px at 14.3 px)
    return _math_tag(v, "imath", em, "display:inline-block;vertical-align:middle;margin:0 .14em")

_DISPLAY_FS = 20      # one font size for EVERY display formula, so they look uniform
_DISPLAY_SCALE = 1.3  # base-glyph height in em (kept moderate — "not overly large")
def dmath(tex, color=None, fs=None):
    """A display formula on its own centred line. Every formula is rendered at the SAME
    font size, so short and tall formulas show glyphs of one uniform size; the formula
    only grows taller for multi-line content (a fraction or a sum). `tex` includes the
    $…$ delimiters, like math_img."""
    fs = fs or _DISPLAY_FS
    if fs not in _IMATH_REF:
        _IMATH_REF[fs] = _math_get(r"$0$", fs)[0]
    v = _math_get(tex, fs)
    em = round(v[0] / _IMATH_REF[fs] * _DISPLAY_SCALE, 2)
    return ("<div style='text-align:center;margin:14px 0'>%s</div>"
            % _math_tag(v, "dmath", em, "vertical-align:middle"))

# 2026-09-28 (R2 · Paket 16, G2 — Oberfläche + Applikation) — PLOTS IN THE STYLE.
# A PNG is painted once, in the kernel, in one ink that has to read on every
# page; a style switch in the browser could not reach it. The plots are now
# SVG, written into the page, and their colours are CSS variables: the axes
# ink is var(--nbskin-ink), the main curve var(--nbskin-acc), the lettering
# var(--nbskin-font). The body carries those per style and per light/dark, so
# switching style or theme recolours every plot at once, with no kernel.
# COUNTED FIRST (the card's rule): over the 38 figures Complex draws, the SVGs
# are 0.92 × the PNGs (562 against 609 KB) — and one set serves 4 styles ×
# light/dark, where PNGs would need eight.
#   PLOT_FORMAT = "png" brings the old picture back (one line, for a front end
#   that cannot show inline SVG).
PLOT_FORMAT = "svg"
# which drawn colour becomes which style variable; the old colour stays as the
# fallback, so a page without our stylesheet shows exactly the old plot
_PLOT_VARS = (("#8a94a0", "--nbskin-ink"),      # PLOT_INK: axes, ticks, labels, grid
              ("#3f93d1", "--nbskin-acc"))      # PAL["z2"]: the main curve
_SVG_FONT = _re.compile(r"font-family: [^;\"]*")

def _svg_html(fig, tight, dpi=100):
    buf = io.StringIO()
    with plt.rc_context({"svg.fonttype": "none", "svg.hashsalt": "digichemjn"}), \
         _warnings.catch_warnings():
        _warnings.filterwarnings("ignore", category=DeprecationWarning)
        fig.savefig(buf, format="svg", transparent=True,
                    **({"bbox_inches": "tight"} if tight else {}))
    svg = buf.getvalue()
    svg = svg[svg.index("<svg"):]
    svg = _re.sub(r"<metadata>.*?</metadata>\s*", "", svg, flags=_re.S)
    # matplotlib's <style>*{…}</style> would be a rule for the WHOLE page once
    # the svg is inline — its two properties go onto the svg itself instead
    svg = _re.sub(r"<style type=\"text/css\">.*?</style>\s*", "", svg, flags=_re.S)
    # the same pixel size the PNG had at this dpi (matplotlib writes pt)
    svg = _re.sub(r'(<svg[^>]*?)width="([\d.]+)pt" height="([\d.]+)pt"',
                  lambda m: '%swidth="%.0fpx" height="%.0fpx"' % (
                      m.group(1), float(m.group(2)) * dpi / 72, float(m.group(3)) * dpi / 72),
                  svg, count=1)
    for hexc, var in _PLOT_VARS:
        svg = svg.replace(hexc, "var(%s, %s)" % (var, hexc))
    svg = _SVG_FONT.sub("font-family: var(--nbskin-font, 'DejaVu Sans', sans-serif)", svg)
    svg = svg.replace("<svg ", '<svg class="nbplot nbplot-svg" style="max-width:100%;'
                      'height:auto;stroke-linejoin:round;stroke-linecap:butt" ', 1)
    return '<div style="text-align:center">%s</div>' % svg

def fig_to_html(fig, dpi=100, tight=True):
    """Serialise a matplotlib figure to a centred piece of HTML — an inline SVG
    in the style's colours (PLOT_FORMAT "svg", 2026-09-28) or an <img> PNG.

    tight=False keeps the output EXACTLY figsize*dpi pixels. Interactive plots must
    use it: with bbox_inches="tight" the picture is cropped to its content, so every
    slider move that changes a label length also changes the image size and the
    whole plot appears to jump."""
    for _ax in fig.axes:
        if not getattr(_ax, "_nb_themed", False):
            theme_axes(_ax, grid=False)
    if PLOT_FORMAT == "svg":
        try:
            return _svg_html(fig, tight, dpi)
        finally:
            plt.close(fig)
    buf = io.BytesIO()
    # transparent, so the SAME png sits correctly on the light and the dark page
    # (see theme_axes(): axes/labels are drawn in a neutral ink that carries on both)
    #
    # The warning filter is not carelessness. Matplotlib 3.10 deprecates float
    # pixel coordinates INSIDE its own PNG writer; with bbox_inches="tight" the
    # cropped canvas is fractional and the warning fires from library code we do
    # not call directly and cannot round. In JupyterLite it lands in the cell's
    # stderr, which the front end paints as a red block above the chapter — a
    # reader is told their notebook is broken because a library is planning a
    # change. Scoped to this one call, and to deprecation warnings only, so a
    # real error still comes through.
    with _warnings.catch_warnings():
        _warnings.filterwarnings("ignore", category=DeprecationWarning)
        _warnings.filterwarnings("ignore", category=FutureWarning)
        _warnings.filterwarnings("ignore", message=".*parameter as float.*")
        fig.savefig(buf, format="png", dpi=int(round(dpi)), transparent=True,
                    **({"bbox_inches": "tight"} if tight else {}))
    plt.close(fig)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return ('<div style="text-align:center">'
            '<img class="nbplot" src="data:image/png;base64,%s" style="max-width:100%%;height:auto"></div>' % b64)

# ======================================================================
# CSS injected once (accordion title pills + minimal centring aids)
# ======================================================================
# 2026-09-25 — TWO NUMBERS, AND THEY ANSWER DIFFERENT QUESTIONS.
# NB_VERSION is what the READER holds: it is in the file's name, in the OER
# record and on the title card, and it goes up when a notebook changes in a way
# a reader would notice. TOOLKIT_VERSION is the build — a date and a letter —
# and it only matters when two notebooks from different days meet in one
# JupyterLab window and their stylesheets have to agree which is newer.
NB_VERSION = "1.84"
TOOLKIT_VERSION = "2026-10-27a"
# E26.3 — the short cell (toolkit/shortcell.py): 0 = the cargo on ONE line;
# > 0 = Variant B, the cargo in lines of that many characters (~4 000) for an
# editor that cannot show one long line (PyCharm, to be measured). Read by the build.
NB_CELL_CHUNK = 0

_STYLE = {"quiet": False}

def use_style(name="default"):
    """Pick the document's look. "quiet" drops the coloured pills and the five
    card palettes and gives the document the panel's own language — one light
    surface, one hairline border, no gradients, no shadows — so colour is left to
    mean progress. Call it BEFORE inject_style()."""
    _STYLE["quiet"] = (name == "quiet")

def inject_style():
    css = """
/*@include css/01-base.css*/
/*@include css/02-dark.css*/
/*@include css/03-panel.css*/
/*@include css/04-timeline.css*/
/*@include css/05-document.css*/
/*@include css/06-marks.css*/
/*@include css/07-skins.css*/
/*@include css/08-print.css*/
/*@include css/09-skin-controls.css*/
/*@include css/10-names.css*/
/*@include css/11-k4-scale.css*/
/*@include css/12-k3.css*/
/*@include css/13-stats.css*/
/*@include css/14-e7.css*/
</style>""" % DESIGN
    # 2026-09-25 — ONE SOURCE OF BRIGHTNESS, AND IT IS OURS.
    #
    # The history: every dark rule was WRITTEN keyed on JupyterLab's own body
    # attribute (`data-jp-theme-light="false"` / `data-jp-theme-name*="Dark"`),
    # and a post-processor bolted a `body.nbdark` twin onto each one so the ◐
    # button could force dark on a light front end. Then 24ac had to bolt a
    # `:not(.nbforce-light)` guard onto the attribute half so the front end's
    # opinion would stand down when the reader disagreed. Two bolts on a wrong
    # foundation, and they still leaked: the SKIN rules carry their own light
    # guards spelled `body:not([data-jp-theme-light="false"]):not(.nbdark)`,
    # which the `:not()` bolt never matched (it looks for `body[`, not
    # `body:not([`). Under a dark JupyterLab with the reader asking for light,
    # every skin's light half simply did not apply.
    #
    # So the foundation is replaced instead of bolted to. `body.nbdark` is the
    # ONE thing that says this document is dark; applyTheme() is the only writer
    # of it, and it writes the reader's choice. The front-end attribute is
    # translated away here, for every rule at once — which is the only way to be
    # sure none was missed — and after this line the stylesheet does not mention
    # JupyterLab's theme at all. What still reads it is `nbforce-dark` /
    # `nbforce-light`, and those are the opposite direction: our choice painting
    # over the front end's chrome so the window agrees with the document.
    #
    # Order matters: the composite light guard contains the positive form as a
    # substring, so it is rewritten first.
    _rules, _out = css.split("}"), []
    for _r in _rules:
        if ('data-jp-theme-light' in _r) or ('data-jp-theme-name' in _r):
            _r = (_r
                  .replace('body:not([data-jp-theme-light="false"]):not(.nbdark)',
                           'body:not(.nbdark)')
                  .replace('body:not([data-jp-theme-light="false"])',
                           'body:not(.nbdark)')
                  .replace('body[data-jp-theme-light="false"]', 'body.nbdark')
                  .replace('body[data-jp-theme-name*="Dark"]', 'body.nbdark'))
        _out.append(_r)
    css = "}".join(_out).replace("__NBSTYLE__", TOOLKIT_VERSION)
    # A rule that listed both front-end spellings now lists `body.nbdark` twice.
    # That is legal and harmless, but it doubles the size of a few selector
    # lists, so the exact duplicates are dropped.
    # 2026-09-30 (E10.M1) — split at TOP-LEVEL commas only. `_sel.split(",")`
    # also cut inside `:where([data-digichem],.nbrail-own)`, took the second
    # `:where([data-digichem]` for a duplicate and dropped it: five dark rules
    # (quiz cards, dark formulas, quiet headers) became invalid and the browser
    # threw each away whole. Measured by lab_contrast --overlay: quiz question
    # 1.0 : 1 in dark.
    def _parts(_sel):
        _o, _d, _a = [], 0, 0
        for _i, _ch in enumerate(_sel):
            if _ch in "([": _d += 1
            elif _ch in ")]": _d -= 1
            elif _ch == "," and _d == 0:
                _o.append(_sel[_a:_i]); _a = _i + 1
        _o.append(_sel[_a:])
        return _o
    def _dedupe(_sel):
        _seen, _keep = set(), []
        for _p in _parts(_sel):
            _k = " ".join(_p.split())
            if _k and _k not in _seen:
                _seen.add(_k)
                _keep.append(_p)
        return ",".join(_keep)
    _out2, _chunks = [], css.split("}")
    for _c in _chunks:
        if "{" in _c and "body.nbdark" in _c.split("{")[0]:
            _h, _b = _c.split("{", 1)
            _c = _dedupe(_h) + "{" + _b
        _out2.append(_c)
    css = "}".join(_out2)
    display(IHTML(css))
    # An old copy of a notebook, opened in another JupyterLab tab, injects the
    # stylesheet of ITS toolkit version into the same page — and whichever tag
    # happens to come last in the DOM wins. So the stylesheets arbitrate the same
    # way the panel script does: the newest version is moved to the end of <head>
    # and every older one is dropped. A notebook whose style was dropped gets it
    # back the moment it runs its own setup cell again.
    display(Javascript("""
    (function(){
      var V = '%s';
      // 2026-09-27a — VERSIONS ARE COMPARED AS VERSIONS (D-b). As plain strings
      // '2026-09-24z' > '2026-09-24bi', so from the 27th build of a day on the
      // OLDER script won every handshake. The letters are a number (a=1 … z=26,
      // aa=27, bi=61), padded, so a string compare of the key is right.
      var vkey = window.__nbVKey = function(v){
        v = String(v || '');
        var m = /^(.*?)([a-z]+)$/.exec(v);
        if (!m) return v;
        var n = 0;
        for (var i = 0; i < m[2].length; i++) n = n * 26 + (m[2].charCodeAt(i) - 96);
        return m[1] + '#' + ('000000' + n).slice(-6);
      };
      var all = [].slice.call(document.querySelectorAll('style[data-nbstyle]'));
      var best = V;
      all.forEach(function(s){
        var v = s.getAttribute('data-nbstyle') || '';
        if (vkey(v) > vkey(best)) best = v;
      });
      all.forEach(function(s){
        if (vkey(s.getAttribute('data-nbstyle') || '') < vkey(best)) s.remove();
      });
      if (best === V) {
        var mine = document.querySelector('style[data-nbstyle="%s"]');
        if (mine && mine.parentNode !== document.head) document.head.appendChild(mine);
      }
    })();
    """ % (TOOLKIT_VERSION, TOOLKIT_VERSION)))
    display(Javascript("document.body.classList.%s('nbquiet');"
                       % ("add" if _STYLE["quiet"] else "remove")))
    # 2026-09-24be — THE ONE CONSOLE ERROR WE COULD NEVER PLACE WAS NOT OURS.
    # `Cannot read properties of undefined (reading '0')` has been in the console
    # since the quiz was added. TRACED (JupyterLite, real run): it is line 783 of
    # jupyterquiz's own bundled script — `if (version[0] == "2")`, where
    # `version` is `MathJax.version`.
    # What happens, measured: JupyterLab 4 exposes `window.MathJax` as the
    # component LOADER — {version, _, config, loader} — with NO `typeset`
    # function. jupyterquiz sees version "3" but no `typeset`, decides MathJax
    # is not loaded, REPLACES `window.MathJax` with a bare config object (which
    # throws `version` away) and appends a MathJax script tag from a CDN. That
    # request is the 404/ERR_FAILED in the console, and offline it simply never
    # arrives. The next read of `MathJax.version` is then undefined, and `[0]`
    # on undefined is the error.
    # The fix is to give the loader the `typeset` it is being judged on. Our
    # quiz text carries no LaTeX — the questions are written in unicode — so the
    # honest implementation is a no-op: jupyterquiz takes its "MathJax is here"
    # branch, calls it, and leaves the page alone. JupyterLab's own maths does
    # not go through `window.MathJax.typeset`, so nothing else changes.
    display(Javascript("""
    (function(){
      var M = window.MathJax;
      if (!M || typeof M.typeset === 'function') return;
      try {
        M.typeset = function(){};
        if (!M.version) M.version = '3.0.0';
      } catch (e) {}
    })();
    """))
    inject_jump()
    nbrail_js()

# ----------------------------------------------------------------------
# make the Chapter-overview links work even when accordions are collapsed:
# a single delegated click handler expands the target's parent group and the
# target chapter, then scrolls to it.  Links keep a plain href="#id" so they
# still jump natively if this script is not executed by the environment.
# ----------------------------------------------------------------------
def inject_jump():
    js = r"""
//@include js/01-jump.js
""".replace("__JUMPV__", TOOLKIT_VERSION)
    try:
        display(Javascript(js))
    except Exception:
        pass

def loading_screen():
    """E5.1 (2026-09-28, Applikation + Oberfläche): the loading view over the
    notebook panel while the document builds itself. Called as the FIRST
    output of the mega-cell; it lifts itself once the run is over and the
    reader stands at the top."""
    try:
        display(Javascript(r"""
//@include js/02-loading.js
""".replace("__NBLOADV__", TOOLKIT_VERSION)))
    except Exception:
        pass

def nbrail_js():
    """Host the progress panel on <body>, keep it below JupyterLab's toolbar, and
    update it in place so the CSS transitions can actually run.

    Three problems this solves, all seen in practice:
      * position:fixed inside the output area is captured by a transformed or
        virtualised ancestor, so the panel drifts off after a while;
      * several open notebooks each produced their own host, and the copies
        overlapped at the same coordinates (the flicker in the recording);
      * replacing the whole panel on every update restarts the element, so the
        bars jumped instead of growing. Now only the changed attributes are
        patched, and width/colour animate.
    """
    display(Javascript(r"""
//@include js/10-rail-host.js
//@include js/11-rail-layout.js
//@include js/12-rail-series-role.js
//@include js/13-rail-keys.js
//@include js/14-rail-grip-zoom.js
//@include js/15-rail-theme.js
//@include js/16-rail-flow.js
//@include js/17-rail-marker.js
//@include js/18-rail-scrub-patch.js
//@include js/19-rail-title-sync.js
    """.replace("__NBRAILV__", TOOLKIT_VERSION)))

def run_all_button():
    """A green button that runs every cell in the notebook, centred on the same
    axis as everything else (a real Button in a centred HBox). It works once the
    setup cell has run (it needs the injected click handler); on first open,
    students run this cell once via Run ▸ Run All Cells, after which the button
    re-runs everything."""
    btn = Button(description="▶  Run all cells", layout=Layout(width="auto", height="46px"))
    btn.add_class("nb-runall")
    msg = HTML(value='<div class="nb-runall-msg" style="color:var(--nbskin-quiet,#5b6b7b);font-size:.9em;'
                     'text-align:center;margin-top:6px"></div>')
    display(VBox([center(btn), center(msg)], layout=Layout(width="100%")))

# ======================================================================
# box builders
# ======================================================================
_VAR_LABEL_COLOR = "var(--nbskin-quiet,#5b6b7b)"   # E6.13: the style's quiet ink
def _var_section(label, items, colon=True):
    """A two-column grid: symbols in the left column, meanings flush in the right, under
    a small uppercase label. Used for the variables / constants listing in the concept box."""
    h = ('<div style="color:%s;font-size:.82em;text-transform:uppercase;letter-spacing:1.6px;'
         'margin:16px 0 8px">%s</div>' % (_VAR_LABEL_COLOR, label))
    def _cap(s):
        return s[0].upper() + s[1:] if s and s[0].isalpha() else s
    sep = ":" if colon else ""
    rows = "".join(
        '<div style="text-align:left"><b><i>%s</i></b>%s</div>'
        '<div style="text-align:left">%s</div>' % (sym, sep, _cap(mean)) for sym, mean in items)
    h += ('<div style="display:inline-grid;grid-template-columns:max-content auto;'
          'gap:5px 14px;text-align:left">%s</div>' % rows)
    return h

def info_box(tex, variables, constants=None, function=None, accent="blue", extra_html=""):
    """Kept for compatibility. A formula card in the content-box style (light, thin
    border), with the formula at a uniform display size. New chapters use concept_box."""
    return concept_box("", tex, variables=variables, constants=constants,
                       function=function, extra_html=extra_html)

def concept_box(intro, tex=None, variables=None, constants=None, function=None,
                grey=False, extra_html=""):
    """ONE box per chapter (in the content-box style): the key-message intro text
    (justified) at the top, then — if given — the formula on its own centred line at the
    uniform display size, then a single ALIGNED listing of the variables followed by the
    constants (no section labels, no separate function line). `variables` are (symbol,
    meaning) pairs; `constants` are (left, right) pairs already formatted (e.g.
    ("<b><i>e</i></b> ≈ 2.71828", "Euler's number" + cite(...))) so the value lines up
    under the variable symbols and the name under the variable meanings."""
    d = (dict(bg="linear-gradient(180deg,#eef0f2,#f8fafb)", border="4px solid #b8c1c9", ink="var(--nbskin-ink,#1a1a1a)")
         if grey else dict(bg="linear-gradient(180deg,#f7fafc,#fdfeff)",
                           border="1px solid #d6e2ec", ink="var(--nbskin-ink,#1a1a1a)"))
    def _cap(s):
        return s[0].upper() + s[1:] if s and s[0].isalpha() else s
    inner = ""
    if intro:
        inner += ('<div style="max-width:800px;margin:0 auto;text-align:justify;line-height:1.6">%s</div>'
                  % intro)
    if tex:
        inner += dmath(tex)
    rows = ""
    for sym, mean in (variables or []):
        rows += ('<div style="text-align:left"><b><i>%s</i></b>:</div>'
                 '<div style="text-align:left">%s</div>' % (sym, _cap(mean)))
    for left, right in (constants or []):
        rows += ('<div style="text-align:left">%s</div>'
                 '<div style="text-align:left">%s</div>' % (left, right))
    if rows:
        inner += ('<div style="text-align:center;margin-top:14px"><div style="display:inline-grid;'
                  'grid-template-columns:max-content auto;gap:5px 14px;text-align:left">%s</div></div>' % rows)
    inner += extra_html
    return HTML(layout=_w(), value=(
        '<div class="nbbox %s" style="background:%s;border:%s;text-align:center;%scolor:%s">%s</div>'
        % ("nbbox-grey" if grey else "nbbox-concept",
           d["bg"], d["border"], _BOXCSS, d["ink"], inner)))

def note_box(html, grey=False):
    """Concept box for prose-only chapters (no formula). Content left-aligned.
    grey=True → the neutral grey palette used for the meta sections;
    otherwise a light, thin-framed box (no heavy fill) like the solution box."""
    d = (dict(bg="linear-gradient(180deg,#eef0f2,#f8fafb)", border="4px solid #b8c1c9", ink="var(--nbskin-ink,#1a1a1a)")
         if grey else dict(bg="linear-gradient(180deg,#f7fafc,#fdfeff)",
                           border="1px solid #d6e2ec", ink="var(--nbskin-ink,#1a1a1a)"))
    return HTML(layout=_w(), value=(
        '<div class="nbbox %s" style="background:%s;border:%s;%scolor:%s">'
        '<div style="max-width:800px;margin:0 auto;text-align:justify;line-height:1.6">%s</div></div>'
        % ("nbbox-grey" if grey else "nbbox-concept",
           d["bg"], d["border"], _BOXCSS, d["ink"], html)))

# E30 A1 (2026-10-12, Python; Nutzer 12.10.: "Conclusion = ein zusammenhängender,
# zusammenfassender Text wie in Publikationen … keine Stichpunkt-Liste") —
# THE CONCLUSION IS PROSE. Paragraphs, in this order: what the chapters
# established (summary), where it stands (context), and an Outlook under a
# small heading. No table, no list: the rules on one screen of E21.13 are gone
# from the template; a glossary, where a notebook keeps one, is its own box.
# Markup for CSS (claude/VERTRAG-E30-py.md): .nbbox.nbbox-concept.nbconcl >
# div > p.nbconcl-p (+ .nbconcl-ctx / .nbconcl-out), div.nbconcl-h (Outlook).
def conclusion(summary, context=(), outlook=()):
    """The closing text of a notebook, written like the conclusion of a paper.
        conclusion(["The chapters showed …", "…"],      # summary, 1–3 paragraphs
                   context="This places …",              # where it stands (optional)
                   outlook="Next, …")                    # under "Outlook" (optional)
    Each argument is one paragraph (a string) or several (a list); HTML inside
    a paragraph is fine (<b>, <i>, cite(n)), lists are not what this is for."""
    one = lambda x: [x] if isinstance(x, str) else [p for p in (x or ()) if p]
    paras = lambda xs, cls: "".join("<p class='nbconcl-p%s' style='margin:0 0 .85em'>%s</p>" % (cls, p) for p in xs)
    out = one(outlook)
    h = (paras(one(summary), "") + paras(one(context), " nbconcl-ctx")
         + (("<div class='nbconcl-h' style='font-weight:700;margin:1.2em 0 .45em'>%s</div>" % "Outlook"
             + paras(out, " nbconcl-out")) if out else ""))
    w = note_box(h)
    w.value = w.value.replace('class="nbbox nbbox-concept"', 'class="nbbox nbbox-concept nbconcl"', 1)
    return w

def intro_box(html):
    """A small, light, thin-framed card placed at the very top of a chapter (before
    the formula box). It states the chapter's key message and its connection to the
    previous chapter, mirroring the plain concept box of Chapter 1. No heading line
    and no heavy border, so it stays visually quiet above the coloured formula box."""
    return HTML(layout=_w(), value=(
        '<div class="nbbox nbbox-concept" style="background:linear-gradient(180deg,#f7fafc,#fdfeff);'
        'border:1px solid #d6e2ec;%scolor:var(--nbskin-ink,#1a1a1a)">'
        '<div style="max-width:800px;margin:0 auto;text-align:justify;line-height:1.6">%s</div>'
        '</div>' % (_BOXCSS, html)))

def formula_line(tex, color=None):
    """A display formula on its own centred line, for use inside a prose box (exercise,
    note, …). Uniform size via dmath. `tex` includes the $…$ delimiters."""
    return dmath(tex, color=color)

def taskline(html):
    """The centred first line of an exercise box: the one-sentence task statement,
    shown above the (centred) formula and the justified how-to text."""
    return "<div style='text-align:center;margin-bottom:2px'>%s</div>" % html

def plot_html(fig):
    """Wrap a static (non-interactive) matplotlib figure as a centred image widget."""
    return center(HTML(layout=_w(), value=fig_to_html(fig)))

# table colour schemes — pick the one matching the box the table sits in
TABLE_SCHEMES = {
    "viz":  dict(head="#8a3b63", accent="#b64a86", rule="#ecc9dc", hrule="#d9b3c8", ink="#6b4a5e"),
    "info": dict(head="#245f80", accent="#2c6e91", rule="#cfe0ea", hrule="#9cc2d6", ink="#3a5468"),
    "ex":   dict(head="#922b21", accent="#c0392b", rule="#f0cbcb", hrule="#e0a49c", ink="#7a4a4a"),
}
def make_table(headers, rows, scheme="viz"):
    """Styled table: no cell background, header underline, vertical column rules.
    `scheme` colours the table to match its container box ('viz' pink / 'info' blue / 'ex' red)."""
    d = TABLE_SCHEMES.get(scheme, TABLE_SCHEMES["viz"])
    n = len(headers)
    def _al(k):   # every cell left-aligned (the whole table is centred via margin:auto)
        return "left"
    th = "".join(
        '<th style="padding:4px 16px 6px;color:var(--nbskin-ink,#1a1a1a);text-align:%s;border-bottom:2px solid %s%s">%s</th>'
        % (_al(k), d["hrule"], ("" if k == 0 else ";border-left:1px solid %s" % d["rule"]), h)
        for k, h in enumerate(headers))
    body = ""
    for r in rows:
        tds = ""
        for k, cell in enumerate(r):
            fw  = "font-weight:700;" if k == 1 else ""
            bl  = "" if k == 0 else ";border-left:1px solid %s" % d["rule"]
            tds += '<td style="padding:2px 16px;color:var(--nbskin-ink,#1a1a1a);text-align:%s;%s%s">%s</td>' % (_al(k), fw, bl, cell)
        body += "<tr>%s</tr>" % tds
    return ('<table style="border-collapse:collapse;font-size:0.96em;margin:0 auto">'
            '<tr>%s</tr>%s</table>' % (th, body))

def viz_intro_box(title, subtitle, table_html=""):
    """Pink description card at the top of an Interactive fold. `title` is optional
    (pass "" to show only the description); `table_html` is optional and normally
    omitted now — the visualisation is explained in prose in `subtitle` instead."""
    d = DESIGN["viz"]
    title_html = ('<div style="font-weight:800;color:%s;font-size:1.14em;margin-bottom:12px">%s</div>'
                  % (d["head"], title)) if title else ""
    return HTML(layout=_w(), value=(
        '<div class="nbbox nbbox-viz" style="background:%s;border:%s;text-align:center;%scolor:%s">'
        '%s<div style="color:var(--nbskin-ink,#1a1a1a);margin:0 auto;max-width:640px;text-align:justify;line-height:1.55">%s</div>%s</div>'
        % (d["bg"], d["border"], _BOXCSS, d["ink"], title_html, subtitle,
           ("<div style='margin-top:12px'>%s</div>" % table_html if table_html else ""))))

def exercise_box(title, prompt):
    # `title` is accepted for compatibility but no longer shown: the boxes carry no
    # heading of their own (the Practice pill already names the section). The detailed
    # task text is left-aligned for easy reading.
    d = DESIGN["ex"]
    return HTML(layout=_w(), value=(
        '<div class="nbbox nbbox-ex" style="background:%s;border:%s;%scolor:%s">'
        '<div style="width:%s;max-width:100%%;margin:0 auto;text-align:justify;line-height:1.6;color:var(--nbskin-ink,#1a1a1a)">%s</div></div>'
        % (d["bg"], d["border"], _BOXCSS, d["ink"], DESIGN["text_w"], prompt)))

# ---- theme-aware syntax highlighting (stdlib tokenizer, no dependency) --------
_BUILTINS = set(dir(_bi))
# JupyterLab exposes its editor token colours as CSS variables, so colouring with
# them makes the highlighting follow whatever Jupyter theme the user selected.
_TOKCOL = {
    "kw":  "var(--jp-mirror-editor-keyword-color,#008000)",
    "str": "var(--jp-mirror-editor-string-color,#b5482e)",
    "com": "var(--jp-mirror-editor-comment-color,#5c6370)",
    "num": "var(--jp-mirror-editor-number-color,#2aa198)",
    "def": "var(--jp-mirror-editor-def-color,#1750eb)",
    "blt": "var(--jp-mirror-editor-builtin-color,#308080)",
    "op":  "var(--jp-mirror-editor-operator-color,#a626a4)",
}
def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def highlight_code(code):
    """`code` → theme-aware, syntax-highlighted HTML using only the standard-library
    tokenizer. Falls back to plain escaped text if the snippet cannot be tokenised."""
    skip = {_tok.ENCODING, _tok.ENDMARKER, _tok.NEWLINE, _tok.NL, _tok.INDENT, _tok.DEDENT}
    try:
        toks = list(_tok.generate_tokens(io.StringIO(code).readline))
    except Exception:
        return _esc(code)
    out, row, col, prev = [], 1, 0, ""
    for ttype, tstr, (srow, scol), (erow, ecol), _ in toks:
        if ttype in skip:
            continue
        if srow > row:                       # reproduce blank lines / line breaks
            out.append("\n" * (srow - row)); col = 0
        if scol > col:                        # reproduce spaces / indentation
            out.append(" " * (scol - col))
        cls = None
        if   ttype == _tok.COMMENT: cls = "com"
        elif ttype == _tok.STRING:  cls = "str"
        elif ttype == _tok.NUMBER:  cls = "num"
        elif ttype == _tok.OP:      cls = "op"
        elif ttype == _tok.NAME:
            if   _kw.iskeyword(tstr):     cls = "kw"
            elif prev in ("def", "class"): cls = "def"
            elif tstr in _BUILTINS:        cls = "blt"
        out.append('<span style="color:%s">%s</span>' % (_TOKCOL[cls], _esc(tstr)) if cls else _esc(tstr))
        if tstr.strip():
            prev = tstr
        row, col = erow, ecol
    return "".join(out)

# a monospace <pre> that adopts the selected Jupyter theme's editor colours
# 2026-09-24ag — IT LINES UP WITH THE BOXES.
# `display:inline-block` with `margin:auto` does not centre anything: an
# inline-block is placed by the text alignment of whatever contains it, and in a
# left-aligned widget that means hard against the left edge — which is exactly
# where the solution listing sat, while every box above it was centred. As a
# BLOCK with `width:fit-content` and auto margins it centres itself, and the
# width ladder is the one the boxes use (24w), so it comes out the same width as
# the box it belongs to instead of a width of its own.
_CODE_PRE = ('display:block;text-align:left;box-sizing:border-box;'
             # ONE per cent sign, not two: this constant is an ARGUMENT to a
             # %-format, never a format string itself, so nothing un-doubles it
             'width:fit-content;max-width:min(94%,70rem);'
             'background:var(--jp-cell-editor-background,#f6f8fa);'
             'color:var(--jp-content-font-color1,#24292e);'
             'border:1px solid var(--jp-cell-editor-border-color,#e1e4e8);'
             'border-radius:8px;padding:10px 14px;margin:8px auto 0;overflow:auto;'
             'font-family:var(--jp-code-font-family,monospace);'
             'font-size:var(--jp-code-font-size,.9em);line-height:1.5')

def solution_box(intro, code, task=None, route="answer"):
    """The worked solution, behind a green pill in the same family as the yellow
    check button. With `task` set, revealing it records that the reader did not
    get there themselves — unless the exercise is already settled, which is left
    alone. That is why this is a Button and no longer a <details>: only Python
    can update the state.

    `route` says WHICH of the two progressions this solution belongs to
    (2026-09-24ae). On the answer route, revealing it is a skip — amber — because
    red is reserved for an answer that was actually entered and was wrong. On the
    CODE route there is no wrong answer to enter, so revealing the solution is
    the give-up case and is red. Before this, a coding solution marked the
    ANSWER route, which is a different exercise entirely."""
    body = HTML(layout=_w(), value="")
    # E17.1 — whole sentences, so each language can order its own words
    warn = ("<div class='nbink' style='text-align:center;font-size:.86em;opacity:.85;"
            "margin-top:4px'>%s</div>"
            % ("Revealing the solution marks this coding exercise as given up (✗) "
               "in the progress panel." if route == "code" else
               "Revealing the solution marks this exercise as come back to later (⤳) "
               "in the progress panel.")) if task else ""
    hint = HTML(layout=_w(), value=warn)
    btn  = Button(description="💡  Solution", layout=Layout(width="220px", height="42px"))
    try: btn.style.button_color = "#3fa877"; btn.style.text_color = "#ffffff"; btn.style.font_weight = "800"
    except Exception: pass
    btn.add_class("sol-btn")
    state = {"open": False}
    def _toggle(_b):
        state["open"] = not state["open"]
        if state["open"]:
            body.value = ('<pre style="%s;margin:12px auto 0;text-align:left"><code>%s</code></pre>'
                          % (_CODE_PRE, highlight_code(code)))
            btn.description = "💡  Hide solution"
            hint.value = ""
            if task:
                (task_code_bypassed if route == "code"
                 else task_solution_opened)(task)
        else:
            body.value = ""
            btn.description = "💡  Solution"
            hint.value = warn
    btn.on_click(_toggle)
    return VBox([center(btn), center(hint), center(body)], layout=Layout(width="100%"))

# ======================================================================
# 2026-09-27 (Inhalt), eingebaut R2 · Paket 15 (2026-09-28) — HINTS BEFORE THE
# SOLUTION: two steps, on request. Step 1 names the idea, step 2 lays out the
# working with the reader's own numbers — and neither states the answer. That
# rule is CODE: `forbid` takes the correct results, and a step that spells one
# out stops the build. A hint changes NO progress state; _HINTS only counts how
# far each reader looked. `.nbhint-btn` is the handle for key H and the look.
# R2 · 15: `steps` and `forbid` may be functions — then a reseed (Paket 13, if
# it is in the build) writes the hints again with the new numbers.
# ======================================================================
_HINTS = {}          # key -> highest step opened
_HINT_WIDGETS = {}   # key -> (button, body, steps), for the tests
_HINT_SRC = {}       # key -> function giving the checked steps (for a seed sweep)

def hints_seen():
    """{task key: highest hint step the reader opened}."""
    return dict(_HINTS)

def _hint_leaks(text, forbid):
    """The forbidden results that `text` spells out.
    A decimal leaks when it appears to 2, 3 or 4 places. A whole number leaks
    only when it stands right after '=' ('= -7', '= (−7)') — a bare '5' is in
    too many sentences to mean anything. A string (the right option of a
    choice) leaks when it appears as whole words, any case."""
    plain = _re.sub(r"<[^>]+>", "", str(text)).replace("−", "-")
    plain = _re.sub(r"(?<=\d),(?=\d)", ".", plain)      # E22.2: a German 1,414 leaks like 1.414
    out = []
    for v in forbid:
        if isinstance(v, str):
            if _re.search(r"(?<!\w)" + _re.escape(v) + r"(?!\w)", plain, _re.I):
                out.append(repr(v))
            continue
        v = float(v)
        if abs(v - round(v)) < 1e-9:
            m = _re.search(r"=\s*\(?\s*-?\s*%d\s*\)?(?!\d|[.,]\d)" % abs(int(round(v))), plain)
            if m:
                out.append(m.group(0).strip())
            continue
        for p in (2, 3, 4):
            sv = "%.*f" % (p, abs(v))
            if sv in plain:
                out.append(sv); break
    return out

def _hint_check(key, steps, forbid):
    steps = [str(x) for x in steps]
    if not steps:
        raise ValueError("hint_steps(%r): no steps" % (key,))
    for i, x in enumerate(steps, 1):
        leak = _hint_leaks(x, forbid)
        if leak:
            raise ValueError("hint %d of %r gives the answer away (%s)" % (i, key, ", ".join(leak)))
    return steps

def hint_steps(key, steps, forbid=()):
    """Hints on request, one step per click, before any solution.

    key    : the task this belongs to (only for hints_seen()).
    steps  : [html, …] or a function returning it — the standard is two:
             1) the idea, 2) the working with the reader's numbers, stopping
             before the final number.
    forbid : the correct results (or a function returning them) — numbers, or
             for a choice the right option's text. A step that states one of
             them is an error."""
    _get = (lambda: _hint_check(key, steps() if callable(steps) else steps,
                                forbid() if callable(forbid) else forbid))
    _HINT_SRC[key] = _get
    st = {"seen": 0, "open": False, "steps": _get()}
    body = HTML(layout=_w(), value="")
    btn = Button(description="💬  Hint 1 of %d" % len(st["steps"]),
                 layout=Layout(width="220px", height="42px"))
    btn.add_class("sol-btn"); btn.add_class("nbhint-btn")
    def _show():
        n = len(st["steps"])
        body.value = "".join(
            "<div class='nbhint nbink' style='max-width:640px;margin:10px auto 0;"
            "text-align:left;line-height:1.5'><b>Hint %d.</b> %s</div>" % (i + 1, x)
            for i, x in enumerate(st["steps"][:st["seen"]])) if st["open"] else ""
        if st["open"] and st["seen"] < n:
            btn.description = "💬  Hint %d of %d" % (st["seen"] + 1, n)
        elif st["open"]:
            btn.description = "💬  Hide hints"
        else:
            btn.description = "💬  Show hints" if st["seen"] else "💬  Hint 1 of %d" % n
    def _click(_b):
        if not st["open"]:
            st["open"] = True
            if st["seen"] == 0:
                st["seen"] = 1
        elif st["seen"] < len(st["steps"]):
            st["seen"] += 1
        else:
            st["open"] = False
        _HINTS[key] = max(_HINTS.get(key, 0), st["seen"])
        _show()
    btn.on_click(_click)
    _HINT_WIDGETS[key] = (btn, body, st["steps"])
    if callable(steps) and isinstance(globals().get("_RESEED"), dict):
        def _renew():                    # new numbers: new hints, folded shut
            st["steps"] = _get(); st["open"] = False; st["seen"] = 0
            _HINT_WIDGETS[key] = (btn, body, st["steps"]); _show()
        _RESEED["clear"].append(_renew)
    return VBox([center(btn), center(body)], layout=Layout(width="100%"))

def interpretation_box(html, title=None):
    # `title` is accepted for compatibility but no longer shown: the box carries no
    # heading of its own; its green colour marks it as the take-away. It now uses the
    # lighter thin-bordered green that used to belong to the solution box (styles swapped).
    d = DESIGN["sol"]
    return HTML(layout=_w(), value=(
        '<div class="nbbox nbbox-interp nbkey" style="background:%s;border:%s;%sline-height:1.6;">'
        '<div style="width:%s;max-width:100%%;margin:0 auto;color:var(--nbskin-ink,#1a1a1a);'
        'text-align:justify">%s</div></div>'
        % (d["bg"], d["border"], _BOXCSS, DESIGN["text_w"], html)))

# E19.8 (2026-10-02, Inhalt + Struktur; Python = Markup) — GREEN IS THE KEY
# MESSAGE, RED IS THE WARNING. The interpretation box above is the chapter's
# key message and the only green box (`.nbbox-interp.nbkey`). What stood in
# the "Remarks and limits" section — a limit, a pitfall, a warning — now sits
# in the chapter it belongs to, in this red box (`.nbbox-warn`, passed to
# build_chapter as body=[…], so it follows the key message). The section and
# its mark on the timeline are gone. Colours per style: CSS (≥ 4.5 : 1).
def warn_box(html):
    d = DESIGN["warn"]
    return HTML(layout=_w(), value=(
        '<div class="nbbox nbbox-warn" role="note" style="background:%s;border:%s;%sline-height:1.6;">'
        '<div style="width:%s;max-width:100%%;margin:0 auto;color:var(--nbskin-ink,#1a1a1a);'
        'text-align:justify">%s</div></div>'
        % (d["bg"], d["border"], _BOXCSS, DESIGN["text_w"], html)))

# ======================================================================
# interactive helpers
# ======================================================================
# 2026-09-29 (Paket 21b, Applikation) — A LOCKED CHAPTER IS DRAWN WHEN IT OPENS.
# COUNTED FIRST (v1.29, in-process profile): of 7.4 s, 1.4 s went into the 38
# figures fig_to_html wrote at start — 8 slider plots and 30 pre-rendered
# frames (i^k, Euler) — and all but one slider plot sit in chapters 2–7,
# which are locked when the notebook starts. Nobody can see them then.
# Now the drawing is a job (_defer): while a group is being built, slider_plot
# and frame_player register their first picture instead of drawing it;
# build_chapter hands the jobs to the chapter's lock, and _open_lock runs them
# the moment the chapter opens — by an answer, a skip, or a restored progress
# code. A chapter that is not locked draws at once, as before. Outside a group
# (the reader's own cell, a test) nothing is deferred.
_LAZY = {"on": False, "jobs": []}

def _defer(job):
    """Run `job` now, or — while a group is built — when its chapter opens."""
    if _LAZY["on"]:
        _LAZY["jobs"].append(job)
    else:
        job()

def _lazy_take():
    jobs, _LAZY["jobs"] = _LAZY["jobs"], []
    return jobs

def _lazy_run(jobs):
    for job in jobs:
        try: job()
        except Exception: pass   # a picture that cannot be drawn must not keep a chapter shut

def slider_plot(render_fn, sliders, readout_fn=None, dpi=100, plot_w="640px", frames=True):
    """
    sliders    : dict name -> widget (already constructed, e.g. FloatSlider(...)).
    render_fn  : render_fn(**values) must RETURN a matplotlib Figure built with
                 fixed_canvas() and FIXED axis limits.
    readout_fn : optional readout_fn(**values) -> html. All the numbers that change
                 with the sliders belong HERE, not in the plot title: text inside the
                 figure changes the layout and makes the picture shift on every move.

    Returns centred widgets: [sliders…, readout, plot].
    """
    _ELEMENTS["figure"] += 1          # counted for the time budget (Inhalt A, 2026-09-26)
    plot = HTML(layout=_w())
    read = HTML(layout=_w()) if readout_fn else None
    def _update(*_):
        vals = {k: w.value for k, w in sliders.items()}
        try:
            plot.value = fig_to_html(render_fn(**vals), dpi=dpi, tight=False)
            if read is not None:
                read.value = readout_fn(**vals)
        except Exception as e:   # a plot error must never blank the rest of the notebook
            plot.value = ('<div class="nberr" style="text-align:center;color:var(--nbskin-bad,#a3352b);font-weight:600">'
                          '⚠ this plot could not be drawn: %r</div>' % (e,))
    for w in sliders.values():
        w.layout = Layout(width="440px")
        w.observe(_update, "value")
    _defer(_update)          # Paket 21b: drawn when its chapter opens
    # E26 Teil 2: the reading window gets this figure with its pictures drawn
    # in advance (_nbrw_slider); frames=False: the start picture only
    if frames:
        _nbrw_reg(plot, "slider", sliders=sliders, render=render_fn, readout=readout_fn, dpi=dpi,
                  fallback=([read] if read is not None else []) + [plot])
        if read is not None:
            _nbrw_reg(read, "skip")
    out = list(sliders.values())
    if read is not None:
        out.append(read)
    return out + [plot]

def readout(pairs):
    """One-line HTML readout: [(label, value), …] rendered as fixed-width chips, so
    the line itself never reflows while the numbers change."""
    cells = "".join(
        "<span style='display:inline-block;min-width:118px;margin:2px 6px;text-align:center'>"
        "<span class='nbread-k'>%s</span>&nbsp;<b>%s</b></span>" % (k, _de_num(v)) for k, v in pairs)
    return ("<div class='nbread' style='text-align:center;font-variant-numeric:tabular-nums;"
            "font-size:.95em;margin:4px auto 2px'>%s</div>" % cells)

# 2026-09-25h — THE READER'S CODE RUNS IN A ROOM OF ITS OWN.
# Both code boxes used to exec() straight into the toolkit's globals, so one line
# in "your own cell" — `task_solved = lambda *a: None`, `del _refresh_progress`
# — silently switched off the progress for the rest of the session. Now every
# run gets a COPY of the globals plus what the reader defined before; what the
# run defines or rebinds is kept for the reader's next run, and never written
# back. The toolkit keeps calling its own functions. Shared OBJECTS are still
# shared (a dict is not copied) — the room keeps names apart, it is not a jail.
_USER_NS = {}
_ROOM_MISSING = object()

def _user_globals():
    g = dict(globals())
    g.update(_USER_NS)
    return g

# 2026-09-25h — AND IT STOPS BY ITSELF. Measured (D, JupyterLab 4.6.4,
# ipykernel 7.3): `while True: pass` in a code box cannot be interrupted — the
# server logs "Kernel interrupted" and the kernel stays busy, because the box's
# code runs inside a widget callback. The only way out was a restart, which
# loses the widgets. So the reader's code runs under a clock: only frames of
# THEIR code are traced (not numpy's, not matplotlib's), and after
# _USER_SECONDS the run ends with an error the box shows like any other.
import sys as _sys, time as _time
_USER_SECONDS = 20
_USER_FILE = "<your code>"

class RanTooLong(Exception):
    pass

def _clocked(fn, *args):
    """Run fn(*args) with the reader's own frames on the clock. The CHECK runs
    under it too: it calls the reader's function, and a function that never
    returns hangs the kernel just the same."""
    deadline = _time.monotonic() + _USER_SECONDS
    def _line(frame, event, arg):
        if _time.monotonic() > deadline:
            raise RanTooLong("stopped after %d seconds — is there a loop that never ends?"
                             % _USER_SECONDS)
        return _line
    def _call(frame, event, arg):
        return _line if frame.f_code.co_filename == _USER_FILE else None
    before = _sys.gettrace()
    _sys.settrace(_call)
    try:
        return fn(*args)
    finally:
        _sys.settrace(before)

def _exec_user(code, g):
    _clocked(exec, compile(code, _USER_FILE, "exec"), g)

def _keep_user(g):
    base = globals()
    for k, v in g.items():
        if k.startswith("__") and k.endswith("__"):
            continue
        if base.get(k, _ROOM_MISSING) is v and k not in _USER_NS:
            continue                       # an untouched toolkit name
        _USER_NS[k] = v
    for k in list(_USER_NS):               # deleted in the room: gone from it
        if k not in g:
            _USER_NS.pop(k, None)

def editable_exercise(stub, check_fn, task=None, route="answer"):
    """
    Editable code cell + one-click Run & self-check.
    Output is always up to three lines:
      1) STATUS  — green "correct" or amber "not there yet"
      2) TIP     — a black, context-specific hint that never gives the full answer
      3) ERROR   — a red line, only if the entered code raised
    check_fn(globals_dict) -> (ok: bool, tip: str). It reads the just-defined
    function from the namespace and returns a hint tailored to what was entered.
    """
    ta  = Textarea(value=stub, layout=Layout(width="96%", max_width="780px", height="150px"))
    ta.add_class("codearea")
    out = Output(layout=Layout(width="96%", max_width="780px"))
    _LINECLS = {"#0f5c41": "nbok", "#b06f00": "nbwarn", "#a3352b": "nberr", "#222": "nbink"}
    def line(txt, color, weight="400", size="1em"):
        display(IHTML('<div class="%s" style="text-align:center;color:%s;font-weight:%s;'
                      'font-size:%s;margin:3px 0">%s</div>'
                      % (_LINECLS.get(color, "nbink"), color, weight, size, txt)))
    def run(_):
        out.clear_output(wait=True)
        with out:
            g = _user_globals()
            run_err = None
            try:
                _exec_user(ta.value, g)
            except Exception as e:
                run_err = e
            _keep_user(g)
            if run_err is not None:                       # code did not even run
                line("Not there yet, keep going.", "#b06f00", "700", "1.1em")   # amber status
                line("Fix the error shown below, then run again.", "#222")        # black tip
                line("⚠ your code raised: %r" % (run_err,), "#a3352b", "600")     # red error
                return
            chk_err = None
            try:
                ok, tip = _clocked(check_fn, g)
            except Exception as e:                        # ran, but crashed on the test inputs
                ok, tip, chk_err = False, "Your function ran but crashed on the test inputs.", e
            if not ok and task:
                task_wrong(task, route)
            if ok:
                if task:
                    (task_code_solved if route == "code" else task_solved)(task)
                line("✓ correct, well done!", "#0f5c41", "700", "1.14em")        # green status
                line(tip or "The Solution button shows a worked version.", "#222") # black tip
            else:
                line("Not there yet, keep going.", "#b06f00", "700", "1.1em")    # amber status
                line(tip or "Compare your output with what the exercise asks for.", "#222")  # black tip
                if chk_err is not None:
                    line("⚠ %r" % (chk_err,), "#a3352b", "600")                   # red error
    btn = Button(description="🔍  Check input", layout=Layout(width="240px", height="42px"))
    try: btn.style.button_color = "#e6b52a"; btn.style.text_color = "#ffffff"; btn.style.font_weight = "800"
    except Exception: pass
    btn.add_class("sc-btn")
    btn.on_click(run)
    return VBox([center(ta), center(btn), center(out)], layout=Layout(width="100%"))

def editable_runner(code, run_label="Run ▶", height="220px"):
    """An editable code cell + Run button whose output (plots/prints) shows inside
    the same box — used for the 'bring your own data' section so it lives in the
    accordion and folds with it."""
    ta  = Textarea(value=code, layout=Layout(width="96%", max_width="780px", height=height))
    ta.add_class("codearea")
    out = Output(layout=Layout(width="96%", max_width="780px"))
    def run(_):
        out.clear_output(wait=True)
        with out:
            g = _user_globals()
            try:
                _exec_user(ta.value, g)
            except Exception as e:
                _keep_user(g)
                display(IHTML('<div class="nberr" style="text-align:center;color:var(--nbskin-bad,#a3352b);font-weight:600">⚠ %r</div>' % (e,)))
                return
            _keep_user(g)
            for num in plt.get_fignums():            # render any figures the code made, centred
                display(IHTML(fig_to_html(plt.figure(num))))
    btn = Button(description=run_label, layout=Layout(width="200px", height="42px"))
    btn.add_class("sc-btn"); btn.on_click(run)
    return VBox([center(ta), center(btn), center(out)], layout=Layout(width="100%"))

# ======================================================================
# chapter assembler
# ======================================================================
# When a group is "open", build_chapter buffers its accordions instead of
# displaying them, so group_end() can wrap them in one outer accordion.
_GROUP = {"on": False, "buf": []}

def _anchor_html(anchor):
    return ('<span id="%s" style="display:block;height:0;position:relative;top:-56px"></span>'
            % _aid(anchor))

def _emit(anchor, outer):
    """Either display a chapter now, or buffer it for the current group."""
    if _GROUP["on"]:
        _GROUP["buf"].append((anchor, outer))
    else:
        if anchor:
            _show(HTML(value=_anchor_html(anchor), layout=Layout(height="0px", margin="0px")))
        _show(progress_mirror())
        _show(outer)

# ======================================================================
# E9.5 (2026-09-30, Struktur + Applikation, Skizze) — THE TITLE AND "YOUR OWN
# CELL" ARE THE TWO TOP ACCORDIONS.
# Everything the document shows between the title card and "Your own cell" —
# the subtitle (the card's italic line), Introduction, Content, Appendix and
# the end of the guided part — is ONE accordion, `.acc-title.acc-root`. Shut
# it and all of it goes, and because the chapters inside keep their own
# state, opening it again shows them as they were (E9.6 for free). The card
# itself stays outside, on screen when everything is shut: it is what the
# title's mark stands on, and it is the pill a click folds from (JS). After it
# comes the second root accordion, `.acc-yoc.acc-root`: "Your own cell", with
# the "＋ Your own cell" button (`.nbyoc-add`, JS makes the cell) — outside the
# title's fold, like the reader's own cells under it.
# Markup contract for JS/CSS:
#   .nbtitle.nbtitle-doc            the card (unchanged, outside)
#   .acc-title.acc-root             root accordion 1, open; header = title text
#     .nbtitle-leadbox > .nbtitle-lead   the subtitle, first thing inside
#     anchor #nbtitle_acc           zero-height span BEFORE the accordion
#   .nbyoc > .nbyoc-list            E11.1: no accordion, no header, no button;
#     anchor #nbyoc                 zero-height span before it (outside the title)
#   panel: .nbmap-node.title[data-acc="title"], .nbmap-node.cell[data-acc="yoc"]
# ======================================================================
_ROOT = {"on": False, "buf": [], "lead": None}

def _show(w):
    """Display now, or keep for the title's accordion while it is being filled."""
    if _ROOT["on"]:
        _ROOT["buf"].append(w)
    else:
        display(w)

def _root_start(lead_html):
    _ROOT["on"] = True
    _ROOT["buf"] = []
    _ROOT["lead"] = None
    if lead_html:
        _ROOT["lead"] = HTML(value='<div class="nbtitle nbtitle-leadbox" '
                                   'style="text-align:center;margin:0 0 6px">%s</div>' % lead_html,
                             layout=Layout(width="100%"))
        _ROOT["lead"].add_class("nbtitle-leadw")

def _root_end():
    """Put everything kept since the title card into the title's accordion."""
    if not _ROOT["on"]:
        return
    _ROOT["on"] = False
    kids = ([_ROOT["lead"]] if _ROOT["lead"] is not None else []) + list(_ROOT["buf"])
    _ROOT["buf"] = []
    acc = Accordion(children=[VBox(kids, layout=Layout(width="100%"))],
                    layout=Layout(width="100%"))
    _set_acc_title(acc, _NB_TITLE.get("text") or "Title")
    acc.selected_index = 0
    acc.add_class("acc-title"); acc.add_class("acc-root")
    display(HTML(value=_anchor_html("nbtitle_acc"), layout=Layout(height="0px", margin="0px")))
    display(acc)

# E11.1 (2026-09-30, Struktur + Applikation) — "YOUR OWN CELL" IS NO ACCORDION.
# The user took the pill "Your own cell", its sentence and the "＋ Your own
# cell" button out of the document: nothing down here folds, and a cell of
# one's own is made from the YOC mark in the timeline (JS). What is left is
# the zero-height anchor #nbyoc and the empty `.nbyoc-list`, where JS offers
# "Restore your N own cells?" (E9.13) — both outside the title's accordion.
# (replaces E9.5/E9.7 for YOC: `.acc-yoc`, `.nbyoc-note`, `.nbyoc-add` are gone)
def _yoc_mark():
    display(HTML(value=_anchor_html("nbyoc"), layout=Layout(height="0px", margin="0px")))
    display(HTML(value="<div class='nbyoc'><div class='nbyoc-list'></div></div>",
                 layout=Layout(width="100%", margin="0px")))

def group_start():
    """Begin collecting the chapters built after this call into one group."""
    _GROUP["on"] = True
    _GROUP["buf"] = []
    _GROUP["mark"] = len(_STRUCT)      # where this section starts in the timeline
    _LAZY["on"] = True                 # Paket 21b: pictures wait for build_chapter

def group_end(title, icon="📦", open_=True, top_color=None, anchor=None):
    """Wrap every chapter built since group_start() into one outer 'group' accordion
    (Foundational / Content / Advanced). Jump anchors are embedded at each chapter
    so the table-of-contents links still reach chapters nested inside the group.
    `anchor` is a stable id at the top of the group, so the Chapter-overview can link to
    the section header itself (the click expands the section and scrolls to it)."""
    items = _GROUP["buf"]
    _GROUP["on"] = False
    _GROUP["buf"] = []
    _LAZY["on"] = False
    _lazy_run(_lazy_take())            # Paket 21b: nothing is left undrawn outside a chapter
    _GROUP["gid"] = _GROUP.get("gid", 0) + 1
    top_id = anchor or ("grptop%d" % _GROUP["gid"])
    # anchor at the very top of the group, so the bottom button can jump back to it
    kids = []
    for anchor, outer in items:
        if anchor:
            kids.append(HTML(value=_anchor_html(anchor),
                             layout=Layout(height="0px", margin="0px")))
        kids.append(progress_mirror())
        kids.append(outer)
    _STRUCT.insert(_GROUP.get("mark", len(_STRUCT)),
                   {"kind": "group", "title": title, "icon": icon, "anchor": top_id,
                    "open": bool(open_)})
    inner = VBox(kids, layout=Layout(width="100%"))
    acc = Accordion(children=[inner], layout=Layout(width="100%"))
    try: acc.set_title(0, "%s  %s" % (icon, title))
    except Exception: acc.titles = ("%s  %s" % (icon, title),)
    acc.selected_index = 0 if open_ else None
    acc.add_class("acc-group")
    # The anchor sits BEFORE the accordion, not inside it: jumping to a section
    # has to leave its header on screen, and an anchor inside the body scrolls the
    # header off the top.
    _show(HTML(value=_anchor_html(top_id), layout=Layout(height="0px", margin="0px")))
    _show(acc)

def notebook_start(title="Title page", anchor="nbtop"):
    """Put the title page on the timeline as its first bar.

    The timeline used to begin at the Introduction, which is not where the
    notebook begins — so the reading marker had nowhere to stand while the
    reader was still on the title page, and the scrollbar started a screen too
    late. The bar is registered here and anchored to the title card, which the
    first cell carries; nothing is displayed, because the card is already there.
    """
    _STRUCT.insert(0, {"kind": "title", "title": title, "icon": "\u25A0",
                       "anchor": anchor, "open": True})

# E16.12 (2026-10-02, Struktur; Python = Markup) — UNDER THE END: BACK TO THE
# START, OR AGAIN IN ANOTHER CONTENT. Markup only; JS does it, CSS draws it.
#   .nbend-go               the block under the end note
#   button.nbend-btn.nbend-top  ↑ back to the start (JS: Title on the reading line)
#   button.nbend-btn.nbend-mode[data-mode=<m>]  start again in content <m> (JS: set the
#                           mode and rebuild, as ⚙ "Content" + ▶ does)
# Offered: the PLAYABLE contents other than this run's — both ("Normal"),
# calc, code; after "plain" all three (E16.12, Lesart Dirigent).
# E21.11 (2026-10-02, Struktur; Python = Markup) — THE RESTART CHOICES ARE
# THE COVER'S CARDS. Same four contents in the same order as the cover —
# plain first, on the left — and the same inside: sign, name, one line
# (`.nbmode-ic` / `.nbmode-l` / `.nbmode-d`, the cover's contract), in a row
# `.nbmode-row.nbend-modes`. Each card is still a `button.nbend-btn.nbend-mode
# [data-mode]` (JS E16.12 does it) and carries `.nbmode-opt` so CSS can draw
# it like a cover card; it is NOT inside a `.nbmode` box, so the cover's
# script (modePaint, modeClick) never touches it. Offered as in E16.12: the
# PLAYABLE contents other than this run's (plain is not offered here; after
# plain all three), in the cover's order — plain would stand on the left.
_END_MODES = (("plain", "\u00b6", "Plain", "text and figures only"),
              ("calc", "\u270e", "Pen & paper", "only the calculating exercises"),
              ("code", "\u2328", "Code", "only the coding exercises"),
              ("both", "\u270e\u2328", "Both", "calculate and code"))

def _end_go():
    import html as _h
    card = ("<button class='nbend-btn nbend-mode nbmode-opt' data-mode='%s' "
            "title='start again: %s'><span class='nbmode-ic'>%s</span>"
            "<span class='nbmode-l'>%s</span><span class='nbmode-d'>%s</span></button>")
    return ("<div class='nbend-go'><button class='nbend-btn nbend-top'>↑ Back to the start</button>"
            "<div class='nbend-again'>Start again with</div><div class='nbmode-row nbend-modes'>"
            + "".join(card % (k, _h.escape(l + " — " + d), ic, _h.escape(l), _h.escape(d))
                      for k, ic, l, d in _END_MODES if k not in ("plain", MODE["value"])) + "</div></div>")

def notebook_end(title="End of the guided part",
                 note="Below this line JupyterLab leaves you an empty cell of your "
                      "own. That is not a mistake and it is not the end: carry the "
                      "notebook on from there, or rewrite what is above it. It is "
                      "yours — the licence says so, and so does the empty cell."):
    """Close the guided part with a centred footer AND a bar on the timeline.

    It deliberately does NOT claim to be the end of the document. JupyterLab
    always offers one more cell underneath, and a line that says 'end of this
    notebook' directly above an invitation to write is simply wrong. The bar in
    the timeline says the same thing: the guided route stops here, the notebook
    does not have to."""
    _struct_add({"kind": "end", "title": title, "icon": "\u25A0",
                 "anchor": "nbend", "open": True})
    # ...and the empty cell under it, which belongs to JupyterLab and has no
    # anchor of its own. It gets the last bar on the timeline, so the line ends
    # where the document ends instead of where our text stops.
    _struct_add({"kind": "cell", "title": "Your own cell", "icon": "\u25A0",
                 "anchor": None, "open": True, "acc": "yoc"})
    _show(HTML(value=_anchor_html("nbend"),
               layout=Layout(height="0px", margin="0px")))
    _show(center(HTML(value=(
        "<div class='nbend'>"
        + ornament("rule") +      # E19.9: the ornament is the rule now (was .nbend-rule)
        "<div class='nbend-h'>%s</div>"
        "<div class='nbend-note'>%s</div>%s</div>") % (title, note, _end_go()),
        layout=Layout(width="100%", max_width="720px"))))
    # E9.5 — the title's accordion closes here; E11.1 — "Your own cell" is
    # no accordion any more, only its anchor and the restore list follow
    _root_end()
    _yoc_mark()

def _set_acc_title(acc, title):
    """ipywidgets moved from set_title() to the `titles` tuple; support both."""
    try:
        acc.set_title(0, title)
    except Exception:
        try: acc.titles = (title,)
        except Exception: pass

def _acc(children, title, cls, open_=False):
    # centre EVERY child on the one shared axis (idempotent: re-centring a
    # center() HBox is harmless), so no box can be left un-centred.
    kids = [center(c) for c in children]
    a = Accordion(children=[VBox(kids, layout=Layout(width="100%"))], layout=Layout(width="100%"))
    try: a.set_title(0, title)
    except Exception: a.titles = (title,)
    a.selected_index = 0 if open_ else None
    a.add_class(cls)
    return a

def build_chapter(num, title, info=None, viz=None, practice=None, interp=None,
                  viz_title="📊  Visualisation for this chapter",
                  practice_title="📝  Practice for this chapter",
                  chapter_open=False, icon="📖", anchor=None, body=None,
                  outer_class="acc-chapter", intro=None, locked_by=None, task=None,
                  figure=None):
    """
    num       : chapter number, or None for an unnumbered section
    figure    : the visualisation's name on the timeline ("Figure 3: <figure>",
                2026-09-28b, K2.8); None leaves "Figure 3"
    intro     : a small key-message note_box shown FIRST (before the formula box),
                stating this chapter's core idea and its link to the previous one
    info      : an info_box / note_box widget (or None)
    body      : list of extra widgets placed (centred) directly in the chapter, after info
    viz       : list of widgets (intro box, sliders, plot) or None
    practice  : list of widgets (exercise box, editable_exercise, solution) or None
    interp    : an interpretation_box widget (or list) — sits OUTSIDE the accordions
    anchor    : jump-target id; defaults to 'ch{num}' for numbered chapters
    icon      : leading emoji for the chapter pill
    """
    # E16.11 — mode "plain": a chapter keeps its text and figure, loses its
    # practice and its lock, and has no exercise of its own; a section that IS
    # an exercise (quiz, own data) is built as in every mode (E23.5)
    if plain():
        if task and num is None:              # E23.5: built, open, marked by hand
            if task in _PLAIN_ROWS:
                _register_row(_PLAIN_ROWS.pop(task))
            practice, locked_by = None, None
        else:
            practice, locked_by, task = None, None, None
    # R3 · 18 — a fold the mode does not build is None in the practice list
    # (code_fold on "calc"); drop it here, once
    if practice:
        practice = [w for w in practice if w is not None]
    # …and an answer lock on an exercise whose written part is not built
    # ("code") is turned by its coding exercise instead (E8.7, 29.09.: the
    # chapter stays locked until the task before it is answered — right,
    # wrong or skipped — in every mode; R3 · 18 left it simply readable).
    # Only a lock that nothing could ever open is dropped.
    if (locked_by and locked_by in _TASKS["noanswer"]
            and not _TASKS["has_code"].get(locked_by)):
        locked_by = None
    kids = []
    if intro is not None: kids.append(center(intro))
    if info is not None: kids.append(center(info))
    # the green interpretation box states the chapter's message; it belongs
    # directly under the concept box, not at the far end of the chapter
    if interp is not None:
        for w in (interp if isinstance(interp, (list, tuple)) else [interp]):
            kids.append(center(w))
    if body:
        for w in body: kids.append(center(w))
    viz_anchor = None
    if viz:
        # A MARK OF ITS OWN (2026-09-24v). The visualisation fold gets an anchor
        # immediately before it, so the rail finds the fold's pill and puts a
        # small square on its line — and loses it again with the chapter.
        viz_anchor = "viz_%s" % (anchor or ("ch%s" % num) or (title or "x")[:8])
        kids.append(HTML(layout=_w(), value=_anchor_html(viz_anchor)))
        kids.append(_acc(viz, viz_title, "acc-viz"))
    prac_anchor = None
    if practice:
        # 2026-09-24aj — THE CODING FOLD IS NOT PART OF THE PRACTICE FOLD.
        # It was written into the practice list, so it opened inside it: a fold
        # in a fold, and the second progression buried in the first. It is a
        # step of its own — its own mark on the rail, its own chain of locks —
        # so it sits at chapter level, after the practice fold it belongs to.
        _code_kids = [w for w in practice
                      if "nbcodefold" in tuple(getattr(w, "_dom_classes", ()))]
        _prac_kids = [w for w in practice if w not in _code_kids]
    if practice and _code_kids and not builds_answer():
        # R3 · 18, mode "code": the written practice fold is not built at all;
        # the exercise keeps its coding fold and its code chain
        if task:
            _TASKS["noanswer"].add(task)
        for _cw in _code_kids:
            kids.append(_cw)
    elif practice:
        prac_anchor = "prac_%s" % (anchor or ("ch%s" % num) or title[:8])
        kids.append(HTML(layout=_w(), value=_anchor_html(prac_anchor)))
        # 2026-09-28a (K1) — "Skip for now" lives in the exercise it skips
        if task and task in _TASKS["state"] and _prac_kids:
            _prac_kids = list(_prac_kids) + [skip_button(task)]
        _pacc = _acc(_prac_kids or practice, practice_title, "acc-practice")
        if task:
            _TASKS["pacc"][task] = _pacc
        # 2026-09-24bf — OPENING A CHAPTER IS NOT ANSWERING THE ONE BEFORE IT.
        # The lock box hands the reader the chapter: the text, the formula, the
        # visualisation. It used to hand over the exercises with them, and that
        # emptied the lock of its meaning — you could reach the end of the
        # notebook, every exercise open, without answering a single one.
        # The written exercise now carries a lock of its own, on the same key,
        # and only a CORRECT answer (on either route) opens it. The chapter
        # stays readable throughout, which was always the point: what is gated
        # is the practice, never the prose.
        # The coding exercise needs nothing here — it already waits on
        # ("code", locked_by), and neither the box nor the rail's key touches
        # that chain.
        if locked_by:
            kids.append(_exercise_lock_shell(locked_by, _pacc))
        else:
            kids.append(_pacc)
        for _cw in _code_kids:
            kids.append(_cw)
    chapter = VBox(kids, layout=Layout(width="100%"))
    # Paket 21b — the pictures this chapter registered are drawn when its
    # lock opens, or now if it has none
    _jobs = _lazy_take()
    # the whole chapter waits for the previous chapter's exercise
    if locked_by:
        chapter = _lock_shell("chapter", locked_by, chapter, title)
        _lent = _LOCKS.get(("chapter", locked_by))
        if _lent is not None and not _lent.get("open"):
            _lent.setdefault("lazy", []).extend(_jobs)
            _jobs = []
        if task:
            # remember WHICH exercise holds this one shut, so the panel can show
            # a lock on the circle for as long as it is shut
            _TASKS["guard"][task] = locked_by
    _lazy_run(_jobs)
    # NOTE: the chapter TEXT is never locked — everything can be read at any time.
    # Only the exercise of a chapter waits for the previous one (see above).
    # em-space after the number gives a clear gap between "N." and the title
    # (matching the marker gap in the References list)
    # 2026-09-24ah — A NUMBERED CHAPTER'S PILL IS ITS NAME.
    # The book glyph sat on every one of them, so it distinguished nothing,
    # and the number said what the rail already says by position. Both are
    # gone. The unnumbered meta sections keep their icon, because there the
    # icon IS the distinction (setup, how to, quiz, glossary, …).
    label = title if num is not None else "%s  %s" % (icon, title)
    outer = _acc([chapter], label, outer_class, open_=chapter_open)
    if task: _TASKS["acc"][task] = outer
    # A SHUT CHAPTER STILL SAYS IT IS SHUT (2026-09-24n).
    # Every chapter now starts folded, so the lock panel inside it is not on
    # screen — the padlock has to be on the pill itself, or a locked chapter is
    # indistinguishable from one that is merely closed.
    if locked_by:
        _ent = _LOCKS.get(("chapter", locked_by))
        if _ent is not None and not _ent.get("open"):
            _ent["pill"] = (outer, label)
            # no padlock on the pill any more (2026-09-24ah): the lock, and
            # the way past it, belong to the timeline. The pill only goes quiet.
            try: outer.add_class("acc-locked")
            except Exception: pass
    if num is None and outer_class == "acc-chapter":
        outer.add_class("acc-plain")   # unnumbered meta section → grey pill
        # a section that IS an exercise (quiz, own data) is centred like one
        # (K2.4, 2026-09-28b)
        if task:
            outer.add_class("acc-exsec")
    # emit a jump anchor so the Chapter-overview links reach this chapter even
    # when all chapters render from a single cell
    if anchor is None:
        # EVERY chapter gets one, numbered or not. Without an anchor the panel
        # has nothing to measure an unnumbered section against, so its node falls
        # into the interpolate-between-neighbours path and drifts a long way from
        # its pill — which is what the Introduction sub-points were doing.
        if num is not None:
            anchor = "ch%s" % num
        else:
            _slug = _re.sub(r"[^a-z0-9]+", "_", (title or "sec").lower()).strip("_")[:28]
            anchor = "sec_%s" % (_slug or "x")
            _n = 2
            while anchor in _ANCHORS_USED:
                anchor = "sec_%s_%d" % (_slug or "x", _n); _n += 1
    _ANCHORS_USED.add(anchor)
    _struct_add({"kind": "chapter" if num is not None else "sub",
                 "num": num, "title": title, "icon": icon, "anchor": anchor,
                 "task": task, "open": bool(chapter_open),
                 "task_anchor": prac_anchor,
                 "code_anchor": ("code_%s" % task
                                 if task and _TASKS["has_code"].get(task) else None),
                 "viz_anchor": viz_anchor, "figure": figure,
                 "weight": _content_weight(kids),
                 "has_viz": bool(viz), "has_practice": bool(practice)})
    _emit(anchor, outer)
    _refresh_progress()
    # NOTE: return nothing — returning the widget would make Jupyter auto-display
    # it a second time (the cell's trailing expression), duplicating the chapter.


# ======================================================================
# NEW in the Complex-numbers notebook
#   (1) theme-neutral plots      (2) soft lock + progress      (3) frame player
# ======================================================================

# ---------- (1) plots that read on a light AND a dark page -------------
# The PNG is rendered ONCE in Python, but the page theme is only decided in the
# browser. So instead of rendering twice, every axis element is drawn in one
# neutral ink with enough contrast against white and against near-black, and the
# figure background stays transparent (see fig_to_html).
PLOT_INK = "#8a94a0"

def fixed_canvas(figsize=(5.6, 5.6), left=.13, right=.97, top=.97, bottom=.11, ncols=1):
    """A figure whose axes box is nailed down in figure coordinates.

    Everything interactive must be built on this: the axes never move, the png is
    always the same size, and therefore only the drawn content changes when a
    slider moves. Use together with fig_to_html(..., tight=False) and with axis
    limits taken from the SLIDER RANGE, never from the current data."""
    fig, axs = plt.subplots(1, ncols, figsize=figsize)
    fig.subplots_adjust(left=left, right=right, top=top, bottom=bottom, wspace=.28)
    return fig, axs
PAL = dict(z="#e0563f", z2="#3f93d1", sum="#37a06a", aux="#b06fd0", warn="#d99b2b",
           ghost="#9aa4ae")

def theme_axes(ax, grid=True, equal=False):
    """Style one axes object in the neutral ink. Call it for every plot."""
    for sp in ax.spines.values():
        sp.set_color(PLOT_INK); sp.set_linewidth(1.0)
    ax.tick_params(colors=PLOT_INK, labelcolor=PLOT_INK, labelsize=9)
    ax.xaxis.label.set_color(PLOT_INK); ax.yaxis.label.set_color(PLOT_INK)
    ax.title.set_color(PLOT_INK)
    ax.set_facecolor("none")
    if grid:
        ax.grid(True, color=PLOT_INK, alpha=0.22, linewidth=0.7)
        ax.set_axisbelow(True)
    if equal:
        ax.set_aspect("equal", adjustable="box")
    ax._nb_themed = True
    return ax

def argand_axes(ax, lim=6, lim_y=None):
    """A complex plane: Re horizontal, Im vertical, axes through the origin."""
    ly = lim_y or lim
    theme_axes(ax, grid=True, equal=True)
    ax.set_xlim(-lim, lim); ax.set_ylim(-ly, ly)
    ax.axhline(0, color=PLOT_INK, lw=1.2, zorder=1)
    ax.axvline(0, color=PLOT_INK, lw=1.2, zorder=1)
    ax.set_xlabel("Re", color=PLOT_INK, fontsize=11)
    ax.set_ylabel("Im", color=PLOT_INK, fontsize=11)
    for sp in ax.spines.values():
        sp.set_visible(False)
    return ax

def theme_legend(ax, **kw):
    # the caller may override either default; passing them positionally as well
    # is what raised "got multiple values for keyword argument 'fontsize'"
    kw.setdefault("frameon", False)
    kw.setdefault("fontsize", 9)
    lg = ax.legend(**kw)
    for t in lg.get_texts():
        t.set_color(PLOT_INK)
    return lg

# ---------- (2) soft lock + progress ----------------------------------
# A locked chapter is NOT sealed: it shows a lock panel with an "open anyway"
# button. The progress strip marks every task as open / solved / skipped, so
# skipping stays visible without shutting anybody out. This is a motivational
# device, not an assessment control — everything runs client-side.
# state: open -> the exercise is still untouched
#        done -> answered correctly (the ONLY state that fills the green bar)
#        skip -> content of the next chapter opened without answering  (⤼)
#        fail -> the next chapter's EXERCISE was opened anyway          (✗)
# code:  a second, independent track for the optional coding route (purple bar)
_TASKS = {"order": [], "label": {}, "state": {}, "anchor": {},
          # 2026-09-28b (K2.8) — the NAME a timeline mark reads after its
          # number ("Exercise 3: Sum and difference"), and the function a
          # coding exercise asks for ("Coding 3: add_sub()"). Separate from
          # `label`, which the lock boxes print and which Inhalt owns.
          "name": {}, "cname": {},
          "code": {}, "has_code": {}, "guard": {},
          # 2026-09-24n — TWO CHAINS, NOT ONE.
          # `guard` is the ANSWER chain: which exercise holds a chapter shut.
          # `cguard` is the CODE chain, which runs beside it and unlocks only
          # the next coding exercise — a reader who never writes a line of
          # Python still gets through the notebook, and a reader who does gets
          # a second progression of their own.
          "cguard": {}, "cacc": {},
          # 2026-09-24ak — and the PRACTICE fold of each chapter, so a right
          # answer can put the next one in front of the reader instead of
          # leaving it folded inside a chapter that did open.
          "pacc": {},
          # 2026-09-24an — which chapters the reader opened by skipping the
          # exercise in front of them. The rail shows an OPEN padlock on
          # those: not a warning, a record of the route they took.
          "skipped_open": set(),
          # R3 · 18 — exercises whose WRITTEN part this run does not build
          # (mode "code"); they keep their coding exercise and their code state
          "noanswer": set(),
          # WHICH DIFFICULTY the exercise was settled at. A pass on Gentle and a
          # pass on Strict are not the same result, and a statistic that cannot
          # tell them apart is one number pretending to be two.
          "diff": {},
          # the chapter accordion each exercise lives in, so that settling one
          # can open the chapter it unlocks instead of leaving the reader to
          # find it
          "acc": {}}

# ---------------------------------------------------------------------------
# The timeline in the panel is DERIVED from the accordion structure while the
# notebook is built — group_start/group_end and build_chapter record themselves
# here. Nothing is declared twice, so the overview can never drift from the
# notebook it describes.
#   kind "group"   — a section (Introduction / Content / Appendix)
#   kind "chapter" — a numbered chapter; carries its exercise
#   kind "sub"     — an unnumbered section (setup, glossary, quiz, …): a tiny dot
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Difficulty — one setting, read by the exercise checks. "gentle" is forgiving in
# both the numeric tolerance and the hints; "strict" tightens the tolerance and
# reduces the hint to the bare fact that it is not right yet.
# ---------------------------------------------------------------------------
# Which notebook this is. The panel uses it to keep one record per notebook in
# the browser, so a student sees their progress across the whole series.
NOTEBOOK = {"id": "unnamed", "title": "Notebook"}

# ======================================================================
# OER metadata — the FCI proposal requires an open licence (CC BY-SA), full
# metadata, a persistent identifier (DOI) and versioning for every module.
# Filled per notebook with set_metadata(); rendered by metadata_box() in the
# appendix, next to the references.
# ======================================================================
META = {
    "title": "", "subtitle": "", "authors": [], "institution": "",
    "licence": "CC BY-SA 4.0",
    "licence_url": "https://creativecommons.org/licenses/by-sa/4.0/",
    "version": "", "date": "", "doi": "", "repo": "", "keywords": [],
    "audience": "", "prerequisites": "", "duration": "", "source": "",
    "objectives": [],
    # E39a K1 — the catalogue: thema = "bereich.thema" (one per notebook, no duplicates),
    # kurse = [("<HS> · <Vorlesung>", "<platz>"), …] (toolkit/katalog.py reads them from the source)
    "thema": "", "kurse": [],
}

def set_metadata(**fields):
    """Declare the OER metadata of this notebook (see META for the fields)."""
    unknown = [k for k in fields if k not in META]
    if unknown:
        raise KeyError("unknown metadata field(s): %s" % ", ".join(sorted(unknown)))
    import re as _re39
    if "thema" in fields and not _re39.match(r"^[a-z0-9]+(-[a-z0-9]+)*\.[a-z0-9]+(-[a-z0-9]+)*$", str(fields["thema"])):
        raise ValueError("thema must look like 'bereich.thema': %r" % (fields["thema"],))
    if "kurse" in fields:
        fields["kurse"] = [{"kurs": k, "platz": p} for k, p in fields["kurse"]]
        for e in fields["kurse"]:
            if " · " not in e["kurs"] or not _re39.match(r"^\d+(\.\d+)*$", e["platz"]):
                raise ValueError("kurse: (\"<HS> · <Vorlesung>\", \"<platz>\") expected: %r" % (e,))
    META.update(fields)

def _meta_row(label, value):
    return ("<div style='display:table-row'>"
            "<div style='display:table-cell;padding:3px 16px 3px 0;white-space:nowrap;"
            "color:%s;font-size:.86em;text-transform:uppercase;letter-spacing:1.2px;"
            "vertical-align:top'>%s</div>"
            "<div style='display:table-cell;padding:3px 0;vertical-align:top'>%s</div>"
            "</div>" % (_VAR_LABEL_COLOR, label, value))

def metadata_box():
    """The notebook's OER record: who made it, under which licence, which
    version, how to cite it and where it lives. Everything a repository (Zenodo,
    ILIAS, an OER portal) needs, and everything a reader needs to reuse it."""
    m = META
    authors = ", ".join(m["authors"]) if m["authors"] else "—"
    lic = ("<a href='%s' target='_blank'><b>%s</b></a>" % (m["licence_url"], m["licence"])
           if m["licence_url"] else "<b>%s</b>" % m["licence"])
    doi = ("<a href='https://doi.org/%s' target='_blank'>%s</a>" % (m["doi"], m["doi"])
           if m["doi"] else "<i>reserved on publication (Zenodo)</i>")
    repo = ("<a href='%s' target='_blank'>%s</a>" % (m["repo"], m["repo"])
            if m["repo"] else "<i>not published yet</i>")
    rows = [_meta_row("Title", "<b>%s</b>%s" % (m["title"] or NOTEBOOK["title"],
                      (" — " + m["subtitle"]) if m["subtitle"] else "")),
            _meta_row("Authors", authors)]
    if m["institution"]: rows.append(_meta_row("Institution", m["institution"]))
    rows += [_meta_row("Licence", lic),
             _meta_row("Version", "%s%s" % (m["version"] or "—",
                       (" · " + m["date"]) if m["date"] else "")),
             _meta_row("DOI", doi),
             _meta_row("Repository", repo),
             _meta_row("Notebook id", "<code>%s</code>" % NOTEBOOK["id"])]
    if m["audience"]:      rows.append(_meta_row("Audience", m["audience"]))
    if m["prerequisites"]: rows.append(_meta_row("Prerequisites", m["prerequisites"]))
    if m["duration"]:      rows.append(_meta_row("Working time", m["duration"]))
    if m["keywords"]:      rows.append(_meta_row("Keywords", ", ".join(m["keywords"])))
    if m["source"]:        rows.append(_meta_row("Content source", m["source"]))
    if m["objectives"]:
        rows.append(_meta_row("Learning objectives",
                    "<ul style='margin:0;padding-left:18px'>%s</ul>"
                    % "".join("<li style='margin:2px 0'>%s</li>" % o for o in m["objectives"])))
    cite = ("%s: <i>%s</i>%s. %s%s. %s%s"
            % (authors, m["title"] or NOTEBOOK["title"],
               (" — " + m["subtitle"]) if m["subtitle"] else "",
               m["institution"] + ", " if m["institution"] else "",
               m["date"] or "", m["licence"],
               (". DOI: " + m["doi"]) if m["doi"] else ""))
    rows.append(_meta_row("Cite as",
                "<div style='font-size:.94em;line-height:1.5'>%s</div>" % cite))
    body = ("<div style='display:table;margin:0 auto;text-align:left;max-width:820px'>%s</div>"
            "<div style='max-width:820px;margin:14px auto 0;text-align:center;font-size:.9em;"
            "opacity:.85'>This notebook is an Open Educational Resource. You may share and "
            "adapt it, including commercially, as long as you credit the authors and pass it "
            "on under the same licence.</div>" % "".join(rows))
    return note_box(body)

def set_notebook(nb_id, title):
    NOTEBOOK["id"], NOTEBOOK["title"] = nb_id, title

# ---------------------------------------------------------------------------
# THE SEED (2026-09-24ac)
# The exercise values are drawn once, at import, and the questions are built
# from them — so a seed the reader CHANGES cannot take effect until the next
# run. That is the whole design: the widget stores a number, and the next
# "Run all cells" picks it up. Nothing has to be re-rendered, and the same seed
# on another machine reproduces the same numbers, which is what makes a result
# comparable at all.
#
# Where a number is stored depends on where the kernel lives, and the two cases
# have nothing in common:
#   * Pyodide / JupyterLite — the kernel IS the page, so `js.localStorage` is
#     readable straight from Python, and it is the only thing that survives a
#     reload. The virtual filesystem does not.
#   * a server kernel (JupyterLab, Colab, Binder) — there is no browser to ask,
#     but there is a real home directory. One small text file per notebook.
# Both are best-effort: a failure means "no stored seed", never an error in the
# reader's face.
_SEED_NS = "digichemjn.seed."

def _seed_key(nb_id=None):
    return _SEED_NS + _re.sub(r"[^a-z0-9]+", "-",
                              (nb_id or NOTEBOOK.get("id") or "nb").lower()).strip("-")

# E16.1-Rest (2026-10-02, Applikation) — JUPYTERLITE HAS NO localStorage IN
# THE KERNEL. Its Pyodide kernel runs in a Web Worker (measured, JS E16.1:
# hasattr(js, "localStorage") is False), so mode, seed and progress were never
# stored there and every run built "both". _ls() is the page's storage only
# where the kernel can reach it; otherwise Pyodide keeps the small text files
# beside the notebook, in ./.digichemjn/ — the browser drive JupyterLite keeps
# across reloads (measured), not ~ (memory only).
def _ls():
    if not _in_pyodide():
        return None
    try:
        import js
        return js.localStorage
    except Exception:
        return None

def _seed_path(nb_id=None):
    import os
    return os.path.join(os.getcwd() if _in_pyodide() else os.path.expanduser("~"), ".digichemjn",
                        _seed_key(nb_id).replace(_SEED_NS, "") + ".seed")

def _in_pyodide():
    import sys
    return "pyodide" in sys.modules or sys.platform == "emscripten"

# E19.4 (2026-10-02, Applikation) — WHERE THE KERNEL RUNS. The page finds
# out in which front end it sits (JS); the kernel knows things the page
# cannot see — Colab's own module, the variables an editor sets for the
# kernels it starts. Said once per run on the feed (`data-nbenv`), so the page
# need not guess where it is told. Order: the surest sign first.
#   lite     Pyodide (JupyterLite)        colab   google.colab is loaded
#   vscode   VS Code started the kernel   pycharm PyCharm / DataSpell
#   binder   a Binder pod                 hub     a JupyterHub server
#   server   any other kernel on a machine (JupyterLab, Notebook 7)
# Colab, VS Code and PyCharm are not measured here (no account / no desktop
# application in the container): the variables are their documented ones.
_PARENT_IS = {}

def _parent_is(word, depth=6):
    """Is a process up the kernel's parent chain named like `word`? psutil if
    there, else /proc (Linux); never raises, never waits. Asked once."""
    if word not in _PARENT_IS:
        _PARENT_IS[word] = _parent_walk(word, depth)
    return _PARENT_IS[word]

def _parent_walk(word, depth):
    try:
        import psutil
        p = psutil.Process()
        for _ in range(depth):
            p = p.parent()
            if p is None:
                return False
            if word in (p.name() or "").lower():
                return True
    except Exception:
        pass
    try:
        import os
        pid = os.getppid()
        for _ in range(depth):
            if pid <= 1:
                return False
            with open("/proc/%d/stat" % pid) as f:
                st = f.read()
            if word in st[st.find("(") + 1:st.rfind(")")].lower():
                return True
            pid = int(st[st.rfind(")") + 2:].split()[1])
    except Exception:
        pass
    return False

def kernel_env():
    import os, sys
    if _in_pyodide():
        return "lite"
    if "google.colab" in sys.modules:
        return "colab"
    e = os.environ
    if e.get("VSCODE_PID") or e.get("VSCODE_CWD") or e.get("VSCODE_IPC_HOOK_CLI"):
        return "vscode"
    if e.get("PYCHARM_HOSTED") or "JetBrains" in e.get("TERMINAL_EMULATOR", ""):
        return "pycharm"
    # E26.1b: PyCharm 2025.2 starts its own Jupyter server and PYCHARM_HOSTED
    # did not reach the kernel (11.10.). Cheap extra signs; nothing depends on
    # them (they only word the reading version's top line).
    if any(k.startswith(("PYCHARM", "JETBRAINS", "IDEA_INITIAL")) for k in e):
        return "pycharm"
    if _parent_is("pycharm"):
        return "pycharm"
    if e.get("BINDER_LAUNCH_HOST") or e.get("BINDER_REPO_URL") or e.get("BINDER_REQUEST"):
        return "binder"
    if e.get("JUPYTERHUB_USER"):
        return "hub"
    return "server"

# E22.3/E25.a (still copy per widget output, PyCharm only) — replaced by the
# reading version of E26.1 (_nbread_*), which needs no kernel detection.

def _fput(path, text):
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)

def seed_stored(nb_id=None):
    """The seed the reader chose, or None. Never raises."""
    ls = _ls()
    if ls is not None:
        try:
            v = ls.getItem(_seed_key(nb_id))
            return int(str(v)) if v not in (None, "", "null") else None
        except Exception:
            return None
    try:
        with open(_seed_path(nb_id)) as fh:
            return int(fh.read().strip())
    except Exception:
        return None

def seed_store(value, nb_id=None):
    """Remember `value` for the next run. Returns True when it was written."""
    try:
        v = int(value)
    except Exception:
        return False
    ls = _ls()
    try:
        if ls is not None:
            ls.setItem(_seed_key(nb_id), str(v))
        else:
            _fput(_seed_path(nb_id), str(v))
        return True
    except Exception:
        return False

def seed_forget(nb_id=None):
    """Back to a fresh random seed on every run."""
    ls = _ls()
    try:
        if ls is not None:
            ls.removeItem(_seed_key(nb_id))
        else:
            import os
            os.remove(_seed_path(nb_id))
        return True
    except Exception:
        return False

def notebook_seed(default, nb_id=None):
    """The seed this run must use: the stored one if there is one, else
    `default` (which the caller derives from the per-run id, so an untouched
    notebook still draws fresh numbers every time). Recorded in SEED so the
    widget can say which of the two it is."""
    st = seed_stored(nb_id)
    SEED["fixed"] = st is not None
    SEED["value"] = int(st if st is not None else default)
    SEED["random"] = int(default)
    return SEED["value"]

# ======================================================================
# 2026-09-28 (R2 · Paket 13, Applikation) — A NEW SEED WITHOUT A NEW RUN.
# Until 28f the ⚙ seed buttons stored the number and pressed Run All: every
# cell ran again, the page was rebuilt, and what the reader had open or typed
# was gone. Now the kernel draws the personal numbers again and puts them
# where they are, in place:
#   personal_draw(fn)  the notebook says HOW to draw: fn(seed) refills TV
#   on_reseed(fn)      a chapter recomputes what it derived from TV (_q, _QD …),
#                      so its checks accept the new answers and refuse the old
#   personal(make)     a widget whose text carries personal numbers: make() is
#                      called now and again after each reseed, its .value swapped
#   _RESEED["clear"]   the answer widgets empty their boxes and their feedback,
#                      so a "✓ correct" does not stand next to numbers it was not
#                      given for
# Progress is NOT touched: an exercise answered stays answered (Nutzer, 13).
# ======================================================================
_RESEED = {"draw": None, "hooks": [], "views": [], "clear": []}

def personal_draw(fn):
    """fn(seed) draws the personal numbers for `seed` (in place)."""
    _RESEED["draw"] = fn
    return fn

def on_reseed(fn):
    """Call fn() after every reseed. Returns fn, so it works as a decorator."""
    _RESEED["hooks"].append(fn)
    return fn

def personal(make):
    """make() -> an HTML widget whose text uses personal numbers. The widget is
    shown once; a reseed calls make() again and copies the new text into it."""
    w = make()
    _RESEED["views"].append((w, make))
    return w

def reseed(seed, fixed=None):
    """Draw every personal number again from `seed`, in place, no Run All.
    Returns the number of texts that were redrawn."""
    if _RESEED["draw"] is None:
        raise RuntimeError("this notebook has no personal numbers (personal_draw)")
    seed = int(seed)
    _RESEED["draw"](seed)
    SEED["value"] = seed
    if fixed is not None:
        SEED["fixed"] = bool(fixed)
    for fn in _RESEED["hooks"]:
        fn()
    n = 0
    for w, make in _RESEED["views"]:
        try:
            w.value = make().value; n += 1
        except Exception:
            pass
    for fn in _RESEED["clear"]:
        try: fn()
        except Exception: pass
    return n


# 2026-09-25h — PROGRESS SURVIVES A RUN (D). Measured: solve a coding exercise
# (record c: 1/7), run the document cell again — Ctrl+Enter, Play, or the Run All
# the reader needs after a kernel restart — and the record is c: 0/7. The kernel
# starts empty and the panel wrote the empty state over the stored one, so every
# new session began at zero and "a new version inherits the progress"
# (APPLIKATION §8) never held. Now the signed progress code is kept exactly
# where the seed is kept — the page's localStorage under JupyterLite, one small
# file in ~/.digichemjn on a server kernel — and restored at the end of every
# run, through apply_progress_code, checksum and all. Only in a real kernel:
# the suites exec the notebook in plain Python and must not see each other.
_CODE_NS = "digichemjn.code."

def _persist_ok():
    if _in_pyodide():
        return True
    try:
        return get_ipython().__class__.__name__ == "ZMQInteractiveShell"   # noqa: F821
    except Exception:
        return False

def _mode_tag():
    # R3 · 18 — one progress record per mode; "both" keeps the old name, so
    # progress kept before 18 is still found
    m = globals().get("MODE", {}).get("value", "both")
    return "" if m == "both" else "." + m

def _code_key(nb_id=None):
    return _seed_key(nb_id).replace(_SEED_NS, _CODE_NS) + _mode_tag()

def _code_path(nb_id=None):
    return _seed_path(nb_id)[:-len(".seed")] + _mode_tag() + ".progress"

def progress_store(nb_id=None):
    """Keep this notebook's progress code for the next run. Never raises."""
    if not _persist_ok():
        return False
    try:
        code = progress_code()
        ls = _ls()
        if ls is not None:
            ls.setItem(_code_key(nb_id), code)
        else:
            _fput(_code_path(nb_id), code)
        return True
    except Exception:
        return False

def progress_stored(nb_id=None):
    """The kept progress code, or None."""
    if not _persist_ok():
        return None
    try:
        ls = _ls()
        if ls is not None:
            v = ls.getItem(_code_key(nb_id))
            return str(v) if v not in (None, "", "null") else None
        with open(_code_path(nb_id)) as fh:
            return fh.read().strip() or None
    except Exception:
        return None

def progress_forget(nb_id=None):
    """Start over: the next run begins with every exercise open."""
    try:
        ls = _ls()
        if ls is not None:
            ls.removeItem(_code_key(nb_id))
        else:
            import os
            os.remove(_code_path(nb_id))
        return True
    except Exception:
        return False

def _progress_resume():
    """End of the run: bring back what was kept — only into an untouched state,
    and only through the checksum. From here on every change is kept."""
    try:
        code = progress_stored()
        fresh = all(_TASKS["state"].get(k) == "open" and _TASKS["code"].get(k, "open") == "open"
                    for k in _TASKS["order"])
        if code and fresh:
            ok, msg = apply_progress_code(code)
            _PROG["resumed"] = msg if ok else "not restored: " + msg
    finally:
        _PROG["persist"] = True

# ======================================================================
# 2026-09-28 (R3 · Paket 18, Applikation + Struktur) — WHAT THIS RUN BUILDS.
# Three contents, chosen before Play: "both" (default) · "calc" (only the
# written exercises) · "code" (only the coding exercises). The choice is read
# ONCE, at the start of the run, and the notebook is built for it: a fold the
# mode does not want is not built at all — not hidden — so the panel's marks,
# the lock chains, 📚 and XP count exactly what is on the page.
#   calc  code_fold() returns None; no purple lane, no code chain.
#   code  build_chapter() leaves out the written practice fold of a chapter
#         that has a coding fold (_TASKS["noanswer"]), and an answer lock on an
#         exercise that is not built is dropped — the chapters are readable,
#         the coding exercises keep their own chain (cguard). Quiz and own data
#         are neither and stay.
# Where the choice comes from, first hit wins:
#   1. the environment variable DIGICHEM_MODE (tests, a course server)
#   2. the stored choice — the same two places the seed uses: localStorage
#      "digichemjn.mode.<id>" under JupyterLite, ~/.digichemjn/<id>.mode on a
#      server kernel. Plain text: calc | code | both. The page (JS 18, the
#      field before Play) writes it there; set_mode() writes it from Python.
#   3. "both"
# The stored choice is only read in a real kernel (_persist_ok): the build and
# the suites exec the notebook in plain Python and always get "both".
# Progress is kept per mode (_code_key): a run on "code" does not overwrite
# what "both" had reached.
# ======================================================================
# E16.11 (2026-10-02, Applikation + Struktur) — A FOURTH CONTENT: "plain".
# Only text and visualisations: no exercise of any kind is built — no answer
# box, no coding fold, no hint, no skip, no quiz, no own-data section — and
# so nothing is registered (register_tasks keeps the list empty: no pips, no
# XP, no lock chain) and no chapter waits for one (every lock is dropped).
# The figures stay; they belong to the text. Chosen like the other three
# (cover card, ⚙ "Content", DIGICHEM_MODE=plain); its progress record is its
# own (".plain"), which stays empty.
MODES = ("both", "calc", "code", "plain")
MODE = {"value": "both", "source": "default"}
_MODE_NS = "digichemjn.mode."

def _mode_key(nb_id=None):
    return _seed_key(nb_id).replace(_SEED_NS, _MODE_NS)

def _mode_path(nb_id=None):
    return _seed_path(nb_id)[:-len(".seed")] + ".mode"

# E21.6 (2026-10-02, Applikation) — THE MODE OF THIS NOTEBOOK, ON THE KERNEL'S
# SIDE. Measured on v1.60/v1.61: a choice made on the cover reached a server
# kernel only through the ⚙ dropdown of a LIVE run — on a cold Play the
# kernel built the old mode and the page had to run it a second time — and the
# page set the first dropdown in the window, so one notebook's click could be
# stored by another notebook's kernel. The kernel side now has two doors that
# name the notebook:
#   1. A FILE BESIDE THE NOTEBOOK: <notebook folder>/.digichemjn/<id>.mode —
#      the kernel's working folder, which the page can write before a restart
#      without any kernel (Jupyter contents API; JupyterLite: its drive, where
#      it was already the only place). A server kernel reads it AND
#      ~/.digichemjn/<id>.mode; the newer file wins (mtime, a tie goes to the
#      one beside the notebook). mode_store keeps both in step.
#   2. THE INBOX (mode_inbox): a hidden field `.nbctl-modein input`; the page
#      writes "<notebook id>:<mode>". Only the kernel whose notebook carries
#      that id takes it — written into every inbox of the window, it changes
#      exactly one notebook. The answer is `.nbctl-modein-res` (data-ok,
#      data-why, data-nb, data-mode, data-built, data-src); the ⚙ dropdown
#      follows, so the reader sees the choice there too.
# The id is the notebook's (NOTEBOOK["id"], slug as in the file names), never
# the run's: two notebooks never share a mode, one notebook keeps its own
# across runs.
def _mode_paths(nb_id=None):
    """Where a stored mode can be: [~, beside the notebook] on a server kernel,
    [beside the notebook] under Pyodide (both are the same folder there)."""
    import os
    name = _seed_key(nb_id).replace(_SEED_NS, "") + ".mode"
    here = os.path.join(os.getcwd(), ".digichemjn", name)
    if _in_pyodide():
        return [here]
    home = os.path.join(os.path.expanduser("~"), ".digichemjn", name)
    return [home] if os.path.abspath(home) == os.path.abspath(here) else [home, here]

def mode_stored(nb_id=None):
    """The stored choice, or None. Never raises."""
    if not _persist_ok():
        return None
    try:
        ls = _ls()
        if ls is not None:
            v = str(ls.getItem(_mode_key(nb_id))).strip().lower()
            return v if v in MODES else None
        import os
        best = None
        for n, p in enumerate(_mode_paths(nb_id)):
            try:
                with open(p) as fh:
                    v = fh.read().strip().lower()
                t = os.path.getmtime(p)
            except Exception:
                continue
            if v in MODES and (best is None or (t, n) >= best[:2]):
                best = (t, n, v)
        return best[2] if best else None
    except Exception:
        return None

def mode_store(value, nb_id=None):
    """Remember `value` for the next run. True when it was written."""
    v = str(value).strip().lower()
    if v not in MODES:
        return False
    ls = _ls()
    try:
        if ls is not None:
            ls.setItem(_mode_key(nb_id), v)
            return True
        import os
        ps = _mode_paths(nb_id)
        _fput(ps[0], v)
        for p in ps[1:]:                 # beside the notebook: only if the page made one
            if os.path.exists(p):
                _fput(p, v)
        return True
    except Exception:
        return False

def mode_inbox(text):
    """E21.6 — the page hands a mode to THIS notebook: "<notebook id>:<mode>".
    Returns (ok, why, mode); why is stored | other (another notebook's id,
    nothing changes) | mode (not a mode) | write (could not store)."""
    nb, _, v = str(text or "").strip().rpartition(":")
    nb, v = nb.strip().lower(), v.strip().lower()
    if nb != _seed_key().replace(_SEED_NS, ""):
        return False, "other", v
    if v not in MODES:
        return False, "mode", v
    if not mode_store(v):
        return False, "write", v
    return True, "stored", v

def _mode_inbox_res(ok, why, v):
    import html as _h
    return ("<div class='nbctl-modein-res' data-ok='%d' data-why='%s' data-nb='%s' data-mode='%s' "
            "data-built='%s' data-src='%s'></div>" % (ok, why, _h.escape(_seed_key().replace(_SEED_NS, "")),
                                                      _h.escape(v), MODE["value"], MODE["source"]))

def _mode_inbox_show():
    """The hidden door (shown once, with the last chapters, before the panel)."""
    box_in = Text(value="", layout=Layout(display="none"))
    box_in.add_class("nbctl-modein")
    res = HTML(value=_mode_inbox_res(False, "", ""), layout=Layout(display="none"))
    def _take(ch):
        if not ch["new"]:
            return
        ok, why, v = mode_inbox(ch["new"])
        res.value = _mode_inbox_res(ok, why, v)
        box_in.value = ""
        dd = globals().get("_mode")              # the ⚙ "Content" dropdown (controls)
        if ok and dd is not None and getattr(dd, "value", None) != v:
            try:
                dd.value = v
            except Exception:
                pass
    box_in.observe(_take, "value")
    try:
        display(VBox([box_in, res], layout=Layout(display="none")))
    except Exception:
        pass

def notebook_mode(nb_id=None):
    """Decide this run's mode. Call once, after set_notebook and BEFORE the
    first chapter is built — a later change needs a new run."""
    import os
    env = (os.environ.get("DIGICHEM_MODE") or "").strip().lower()
    if env in MODES:
        MODE.update(value=env, source="env")
    else:
        st = mode_stored(nb_id)
        MODE.update(value=st or "both", source="stored" if st else "default")
    return MODE["value"]

def set_mode(value, nb_id=None):
    """Store a new mode for the NEXT run. Returns True when stored; the page
    then needs Run All (the fold that is not built cannot appear in place)."""
    return mode_store(value, nb_id)

def mode_page_js(value, nb_id=None):
    """E8.16 (2026-09-29, Applikation) — THE PAGE LEARNS THE KERNEL'S CHOICE.

    Measured in JupyterLab 4 (v1.30): once the cover field had written a choice
    to localStorage (`digichemjn.mode.<id>`), a later choice in the ⚙ "Content"
    dropdown only reached ~/.digichemjn/<id>.mode. The run built the new mode,
    the page saw built ≠ its stored choice and put the dropdown BACK and ran
    again (`modeAfterRun`) — the mode never changed. The two stores must say
    the same: a choice made in Python is written to the browser too. This is
    the script that does it; the caller displays it in a live output."""
    v = str(value).strip().lower()
    if v not in MODES:
        return ""
    import json as _json
    k = _mode_key(nb_id)
    return ("try{localStorage.setItem(%s,%s);"
            "localStorage.removeItem('digichemjn.mode.__pending');}catch(e){}"
            % (_json.dumps(k), _json.dumps(v)))

def builds_answer():
    return MODE["value"] in ("both", "calc")

def builds_code():
    return MODE["value"] in ("both", "code")

def plain():
    return MODE["value"] == "plain"

def _answer_order():
    """The exercises that have a WRITTEN part in this run, in order. Equal to
    _TASKS["order"] unless the mode is "code"."""
    na = _TASKS["noanswer"]
    return [k for k in _TASKS["order"] if k not in na]

def _answer_num(task):
    """The number an exercise mark reads: its place among the built ones."""
    o = _answer_order()
    return o.index(task) + 1 if task in o else "•"

SEED = {"value": 0, "fixed": False, "random": 0}

DIFFICULTY = {"level": "standard"}
_DIFF = {"gentle":   dict(tol=2e-2, hints=True,  label="Gentle"),
         "standard": dict(tol=5e-3, hints=True,  label="Standard"),
         "strict":   dict(tol=1e-3, hints=False, label="Strict")}

def set_difficulty(level):
    if level in _DIFF:
        DIFFICULTY["level"] = level
        _refresh_progress()
    return DIFFICULTY["level"]

def tol():
    """The numeric tolerance the current difficulty allows."""
    return _DIFF[DIFFICULTY["level"]]["tol"]

def hints_on():
    return _DIFF[DIFFICULTY["level"]]["hints"]

_STRUCT = []

def _content_weight(obj, depth=0):
    """Roughly how much there is to read in a widget (tree), in characters.

    This drives the spacing on the timeline: a long chapter gets a long stretch of
    line, a two-line meta section a short one. Text counts as its visible length,
    a formula image as a short word, a plot or any other widget as a block — so a
    chapter that is mostly pictures is not counted as empty."""
    if obj is None or depth > 8:
        return 0
    if isinstance(obj, (list, tuple)):
        return sum(_content_weight(o, depth + 1) for o in obj)
    v = getattr(obj, "value", None)
    if isinstance(v, str):
        n = len(_re.sub(r"<[^>]+>", "", v))          # visible characters
        n += 40  * v.count('class="dmath"')          # inline formula
        n += 900 * (v.count("<img") - v.count('class="dmath"'))  # a plot
        return max(n, 0)
    kids = getattr(obj, "children", None)
    if kids:
        return sum(_content_weight(k, depth + 1) for k in kids)
    return 150                                       # slider, button, dropdown …

def _struct_add(entry):
    _STRUCT.append(entry)

def structure():
    """The recorded structure — read it if you want to build your own overview."""
    return list(_STRUCT)
_LOCKS = {}
_ANCHORS_USED = set()
_PROG  = {"w": None, "mirrors": [], "final": False}

def register_tasks(rows):
    """rows: [(key, short label, anchor), …] — declared once, before the chapters.
    `anchor` is the jump target of the chapter the exercise lives in, so clicking
    the number in the progress bar scrolls there (and expands the folds on the way)."""
    if plain():                    # E16.11: no exercise in this run …
        # E23.5 — … except the sections that ARE one (quiz, own data): their
        # row waits here and is registered when build_chapter builds them
        for row in rows:
            _PLAIN_ROWS[row[0]] = row
        return
    for row in rows:
        _register_row(row)

# E23.5 (2026-10-06, Applikation — Bau/Gating) — MULTIPLE CHOICE AND OWN DATA
# IN EVERY CONTENT. "plain" (E16.11) dropped every section that is an exercise,
# so the quiz and "bring your own data" were gone with the calculations; the
# reader wants them in plain and coding too (E23.5). They grade nothing in
# Python (the reader marks them done), so they stand outside both routes:
# built in every mode, never locked in plain.
_PLAIN_ROWS = {}

def _register_row(row):
    k, lab = row[0], row[1]
    anchor = row[2] if len(row) > 2 else None
    # an optional fourth field: the exercise's name on the timeline (K2.8)
    if len(row) > 3 and row[3]:
        _TASKS["name"][k] = row[3]
    if k not in _TASKS["state"]:
        _TASKS["order"].append(k)
    _TASKS["label"][k] = lab
    _TASKS["anchor"][k] = anchor
    _TASKS["state"][k] = "open"
    _TASKS["code"][k] = "open"

# The circles carry no number any more — the chapter's NAME stands above the line,
# and the exercise number is in the tooltip. Only a state that needs saying shows:
# skipped and given-up.
_MARK = {"skip": "⤼", "fail": "✗"}

def _is_locked(k):
    """True while the chapter this exercise lives in is still shut.

    Everything BEFORE the exercise you are on counts as open, whatever the lock
    registry says: you have already been there, so a padlock on it would be a lie."""
    g = _TASKS["guard"].get(k)
    if not g:
        return False
    order = _TASKS["order"]
    # E8.7 — in mode "code" the reader's place is on the code route
    st = _TASKS["state"] if builds_answer() else _TASKS["code"]
    cur = next((t for t in order if st.get(t, "open") == "open"), None)
    if cur is not None and k in order and cur in order and order.index(k) <= order.index(cur):
        return False
    ent = _LOCKS.get(("chapter", g)) or _LOCKS.get(("practice", g))
    return bool(ent) and not ent.get("open")

def _is_locked_code(k):
    """True while the coding exercise before this one has not been settled.

    The code chain never blocks a chapter — only the next coding exercise."""
    g = _TASKS["cguard"].get(k)
    if not g:
        return False
    ent = _LOCKS.get(("code", g))
    return bool(ent) and not ent.get("open")

_TICK_A = '<span class="ck ok">\u2713</span>'     # the answer route
_TICK_C = '<span class="ck co">\u2713</span>'     # the coding route

def _dot_mark(k, cls, current=False):
    """What stands IN the circle. One green tick for the answer, a second purple
    one when the coding route is solved too — the same language as the ✗ for a
    given-up exercise, instead of a filled disc that says only 'something happened
    here'."""
    if cls == "st-lock":
        # 2026-09-25c — the padlock is DRAWN from the class, not written here.
        # A colour emoji cannot take the skin's colour, cannot be centred
        # reliably inside a mark that is a square turned 45°, and renders as a
        # different picture on every platform. The element stays (it is what
        # the drawing hangs on); it is simply empty.
        return ""
    if current:
        # 2026-09-24ai — no open padlock. The circle in front of the reader is
        # already the one with the green ring round it, and a second sign saying
        # the same thing is one more glyph to decode. The CLOSED padlock stays:
        # that one says something the ring cannot.
        return ""
    # 2026-09-24u: one circle, one route. The coding exercise has a mark of its
    # own on the rail now, so a second tick inside this one only asked the
    # reader to decode a circle.
    if cls in ("st-ans", "st-both"):
        return _TICK_A
    return _MARK.get(_TASKS["state"].get(k, "open"), "")

def _code_class(k):
    """The state of the CODING route, as its own mark on the rail (2026-09-24q).

    It is deliberately separate from _dot_class: the two progressions are counted
    and unlocked separately, so they are also drawn separately."""
    if _is_locked_code(k):
        return "cd-lock"
    st = _TASKS["code"].get(k, "open")
    return {"done": "cd-done", "skip": "cd-skip", "fail": "cd-fail"}.get(st, "cd-open")

_CODE_NOTE = {"cd-open cd-current": "the coding exercise in front of you",
              "cd-done": "coding exercise solved",
              "cd-skip": "coding exercise skipped",
              "cd-fail": "coding exercise answered wrongly",
              "cd-lock": "the coding exercise before this one is still open",
              "cd-open": "coding exercise, still open"}

def _dot_class(k):
    """How full the circle is: lower half = answered correctly,
    upper half = the optional coding exercise solved, both = full."""
    st = _TASKS["state"].get(k, "open")
    if st == "skip": return "st-skip"
    if st == "fail": return "st-fail"
    if st == "open" and _is_locked(k): return "st-lock"
    # the circle is the ANSWER route only (2026-09-24u)
    return "st-ans" if st == "done" else "st-open"

_PIPNAME = {"done": _nbL("solved", "gelöst"), "skip": _nbL("skipped", "übersprungen"),
            "fail": _nbL("given up", "aufgegeben"), "open": _nbL("still open", "noch offen")}
# E6 contract: the state words the stylesheet selects on
_PIPST = {"done": "solved", "fail": "wrong", "skip": "skipped", "open": "open"}

def _chap_pips(key):
    """The chapter's own tally: one pip per route, four states each.

    The rail already says all of this — but it says it strung out along the
    line, one mark per exercise, and a reader looking at a CHAPTER wants the
    chapter's answer. Two pips under its name is that answer, in the colours
    the rail is already using, so nothing new has to be learned.

    Shapes follow the rail too: the written route is a diamond, the coding one
    a square. A reader who knows the rail can read this without a key."""
    if not key:
        return ""
    a = _TASKS["state"].get(key, "open")
    c = _TASKS["code"].get(key, "open")
    # E6.12 (2026-09-29) — a locked exercise says so: data-st="locked". The
    # class stays "open" as before, so the old rules still draw it.
    la = key in _TASKS["state"] and _is_locked(key)
    lc = _TASKS["has_code"].get(key) and _is_locked_code(key)
    if la:
        a = "open"
    # E6.11 (2026-09-29) — ONE ROW PER KIND, EACH WITH ITS LABEL. The contract
    # of E6: every pip carries data-kind="calc|code" and
    # data-st="solved|wrong|skipped|open|locked"; each row a .nbpip-lab.
    # CSS styles by these attributes only, JS only places. The 📚 window
    # clones this span, so its dots carry the same attributes.
    def _row(kind, cls, lab, st, locked, title):
        dst = "locked" if locked else _PIPST.get(st, "open")
        return ('<span class="nbpip-row" data-kind="%s"><span class="nbpip-lab">%s</span>'
                '<i class="ps %s %s" data-kind="%s" data-st="%s" title="%s: %s"></i></span>'
                % (kind, lab, cls, st, kind, dst, title,
                   _nbL("locked", "gesperrt") if locked else _PIPNAME.get(st, st)))
    # R3 · 18 — a pip only for a route this run built
    pa = ('' if key in _TASKS["noanswer"] else
          _row("calc", "a", "Exercises", a, la, _nbL("exercise", "Aufgabe")))
    pc = (_row("code", "c", "Coding", c, lc, "coding exercise")
          if MODE["value"] == "both" or _TASKS["has_code"].get(key) else '')
    return '<span class="nbchapstat">%s%s</span>' % (pa, pc)

def _state_attrs(key):
    """The two states of an exercise as attributes of its marks (F, 27e):
    `data-state` the written route, `data-cstate` the coding route — each one
    of open / done / skip / fail, exactly the four the pips draw. A locked
    exercise is `open` here as it is on the pips. Styles may select on them;
    the panel copies them in place like the classes."""
    if not key or key not in _TASKS["state"]:
        return ""
    a = _TASKS["state"].get(key, "open")
    if _is_locked(key):
        a = "open"
    return ' data-state="%s" data-cstate="%s"' % (a, _TASKS["code"].get(key, "open"))

_SCHAR = {"open": "o", "done": "d", "skip": "s", "fail": "f"}
# the code route has the same four states now that it has its own chain
_CCHAR = {"open": "o", "done": "d", "skip": "s", "fail": "f"}
_SBACK = {v: k for k, v in _SCHAR.items()}
_CBACK = {v: k for k, v in _CCHAR.items()}
# one char per exercise for the difficulty it was settled at; '-' = still open
_DCHAR = {"gentle": "g", "standard": "s", "strict": "t"}
_DBACK = {v: k for k, v in _DCHAR.items()}

def _mark_diff(key):
    """Record the difficulty this exercise was settled at, once.

    Set at the moment it is settled and never overwritten by a later change of
    the control: the number is about the attempt, not about where the dropdown
    happens to stand when someone looks at the statistics."""
    if key and key not in _TASKS["diff"]:
        _TASKS["diff"][key] = DIFFICULTY["level"]

# 2026-09-25h — THE CODE CARRIES A CHECKSUM. An HMAC over the whole body —
# notebook id and every state — with a key that lives HERE, in the toolkit.
# Honestly: the key ships inside every notebook, so a reader with a console can
# find it and sign any code. This stops a code typed or edited by hand; it does
# not stop someone who means it. Tamper-EVIDENT, not tamper-PROOF — a statistic
# that must hold needs a server (APPLIKATION-server-und-recht.md).
import hmac as _hmac, hashlib as _hashlib
_CODE_KEY = b"digichemjn/progress-code/2026-09"

def _code_tag(body):
    return _hmac.new(_CODE_KEY, body.encode(), _hashlib.sha256).hexdigest()[:8]

def progress_code():
    """This notebook's state as one short, copy-pasteable code.

    Format before encoding: "<notebook id>|<one char per exercise>|<one per code
    exercise>|<difficulty per exercise>|<checksum>" — so the code stays short
    enough to type. Browser storage is per browser and goes with the site data;
    this code is the part the student owns.
    """
    body = "%s|%s|%s|%s" % (NOTEBOOK["id"],
                         "".join(_SCHAR[_TASKS["state"][k]] for k in _TASKS["order"]),
                         "".join(_CCHAR[_TASKS["code"][k]] for k in _TASKS["order"]),
                         "".join(_DCHAR.get(_TASKS["diff"].get(k), "-")
                                 for k in _TASKS["order"]))
    body += "|" + _code_tag(body)
    return base64.urlsafe_b64encode(body.encode()).decode().rstrip("=")

def apply_progress_code(code):
    """Restore a state from progress_code(). Returns (ok, message)."""
    try:
        raw = code.strip()
        signed = base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)).decode()
        body, tag = signed.rsplit("|", 1)
        parts = body.split("|")
        nb_id, states, codes = parts[0], parts[1], parts[2]
        diffs = parts[3] if len(parts) > 3 else ""
    except Exception:
        return False, "That does not look like a progress code."
    if not _hmac.compare_digest(tag, _code_tag(body)):
        # a code from before 25h has no checksum; it cannot be told apart from
        # an edited one, so it is refused the same way — with the reason
        return False, ("This code does not check out — it was changed by hand, or "
                       "it is from an older version without a checksum.")
    if nb_id != NOTEBOOK["id"]:
        return False, ("This code belongs to %r, not to this notebook (%r)."
                       % (nb_id, NOTEBOOK["id"]))
    order = _TASKS["order"]
    if len(states) != len(order) or len(codes) != len(order):
        return False, ("The code covers %d exercises, this notebook has %d — it is "
                       "probably from an older version." % (len(states), len(order)))
    if any(ch not in _SBACK for ch in states) or any(ch not in _CBACK for ch in codes):
        return False, "The code contains a state this notebook does not know."
    if diffs and len(diffs) != len(order):
        diffs = ""                       # a mismatched tail is simply dropped
    for n, (k, a, c) in enumerate(zip(order, states, codes)):
        _TASKS["state"][k] = _SBACK[a]
        _TASKS["code"][k]  = _CBACK[c]
        d = diffs[n] if diffs else "-"
        if d in _DBACK: _TASKS["diff"][k] = _DBACK[d]
        else: _TASKS["diff"].pop(k, None)
    for k in order:                               # re-open what is already settled
        if _TASKS["state"][k] in ("done", "skip", "fail"):
            _unlock_next(k, refresh=False)
        # …and the code chain separately, because it unlocks different things
        if _TASKS["code"][k] in ("done", "skip", "fail"):
            _code_opens_chapter(k, unfold=False)      # E8.7: mode "code"
            _unlock_next_code(k, refresh=False)
        # 2026-09-26a — a coding exercise SOLVED opens the next chapter and its
        # written exercise too (task_code_solved, since 24ak/24bf). The restore
        # only reopened the next coding exercise, so a reader who got there in
        # code found chapter 2 locked again after every run. Measured by D:
        # solve code 1, run again → chapter 2 and exercise 2 locked.
        if _TASKS["code"][k] == "done":
            _open_lock("chapter", k)
            _open_lock("practice", k)
    _refresh_progress()
    d, t, c, ct = _prog_counts()
    return True, "Restored: %d of %d answered, %d of %d coding exercises." % (d, t, c, ct)

# E17.5 (2026-10-02, Applikation) — LOGGING IN NEVER UNDOES WORK. An account
# brings the progress of another browser or machine (E17 model, "über
# Geräte"); restoring it as it stands would put back an exercise this kernel
# has solved since. Merged instead, per exercise and per route: the further
# state wins — solved > skipped > wrong > open — and a state is never lowered.
# The difficulty goes with the state that won. The page hands a code in
# through the hidden `.nbctl-merge` field (controls); a broken code changes
# nothing (apply_progress_code checks it first).
_RANK = {"open": 0, "fail": 1, "skip": 2, "done": 3}

def merge_progress_code(code):
    """Merge a progress code into this notebook's state, never lowering one.
    Returns (ok, message)."""
    try:
        raw = code.strip()
        body, tag = base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)).decode().rsplit("|", 1)
        parts = body.split("|")
        nb_id, states, codes = parts[0], parts[1], parts[2]
        diffs = parts[3] if len(parts) > 3 else ""
        order = _TASKS["order"]
        ok = (_hmac.compare_digest(tag, _code_tag(body)) and nb_id == NOTEBOOK["id"]
              and len(states) == len(order) == len(codes)
              and all(ch in _SBACK for ch in states) and all(ch in _CBACK for ch in codes))
    except Exception:
        ok = False
    if not ok:
        return apply_progress_code(code)          # says why, changes nothing
    if len(diffs) != len(order):
        diffs = "-" * len(order)
    st, cd, df = [], [], []
    for n, k in enumerate(order):
        a_in, c_in = _SBACK[states[n]], _CBACK[codes[n]]
        a_now, c_now = _TASKS["state"].get(k, "open"), _TASKS["code"].get(k, "open")
        a_win = a_in if _RANK[a_in] > _RANK[a_now] else a_now
        st.append(_SCHAR[a_win]); cd.append(_CCHAR[c_in if _RANK[c_in] > _RANK[c_now] else c_now])
        df.append(diffs[n] if a_win is a_in and a_in != a_now else _DCHAR.get(_TASKS["diff"].get(k), "-"))
    merged = "%s|%s|%s|%s" % (NOTEBOOK["id"], "".join(st), "".join(cd), "".join(df))
    merged += "|" + _code_tag(merged)
    return apply_progress_code(base64.urlsafe_b64encode(merged.encode()).decode().rstrip("="))

def _prog_counts():
    order = _answer_order()                      # R3 · 18: only what is built
    done  = sum(1 for k in order if _TASKS["state"].get(k) == "done")
    ctot  = [k for k in _TASKS["order"] if _TASKS["has_code"].get(k)]
    cdone = sum(1 for k in ctot if _TASKS["code"].get(k) == "done")
    return done, len(order), cdone, len(ctot)

def _prog_states():
    """How the exercises ended, as three numbers the panel can show:
    passed, skipped, given up. The rest are simply still open, which is not a
    result and therefore not counted — the total is in _prog_counts()."""
    st = _TASKS["state"]
    order = _answer_order()
    passed  = sum(1 for k in order if st.get(k) == "done")
    skipped = sum(1 for k in order if st.get(k) == "skip")
    failed  = sum(1 for k in order if st.get(k) == "fail")
    return passed, skipped, failed

def _prog_diffs():
    """How many exercises were PASSED at each difficulty, in the fixed order
    gentle / standard / strict. Only passes are counted: a skip says nothing
    about the tolerance it was skipped under."""
    st, dd = _TASKS["state"], _TASKS["diff"]
    out = [0, 0, 0]
    for k in _answer_order():
        if st.get(k) != "done":
            continue
        lv = dd.get(k)
        if   lv == "gentle":   out[0] += 1
        elif lv == "standard": out[1] += 1
        elif lv == "strict":   out[2] += 1
        else:                  out[1] += 1      # recorded before this was kept
    return out

def _esc_txt(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _esc_attr(s):
    return _esc_txt(s).replace('"', "&quot;")

def _map_html(nodes, done, tot, cdone=0, ctot=0, wide=False):
    """The timeline carries both progressions on one line: its upper half is green
    for the exercises, its lower half purple for the optional coding exercises.
    Both run to the point you have reached, so the second one simply travels with
    the first instead of needing a bar of its own.

    The percentages here are only the fallback a browser sees before the script
    runs; afterwards both ends sit exactly on a circle or a chapter dot."""
    pct  = int(round(100.0 * done / (tot or 1)))
    cpct = int(round(100.0 * cdone / (ctot or 1)))
    return ('<div class="nbmap"%s><div class="nbmap-inner">'
            '<span class="nbmap-fill" style="width:%d%%" '
            'title="exercises answered correctly: %d of %d"></span>'
            '<span class="nbmap-fill code" style="width:%d%%" '
            'title="coding exercises solved: %d of %d"></span>'
            '<span class="nbmap-fill tail" style="width:0" '
            'title="opened by skipping or giving up"></span>'
            '<span class="nbmap-ahead"></span>'
            '<span class="nbmap-here" title="where you are in the document"></span>'
            '%s</div></div>'
            % (' style="margin:10px 0"' if wide else "", pct, done, tot,
               cpct, cdone, ctot, nodes))

# E29 P5 (2026-10-12, Python: Text; Nutzer zu v1.75) — FEEDBACK IS ONE LINE OF TEXT.
# Replaces E25.n (the prefilled mailto: link, the tick for the page's error
# list and its JSON for the page's button): no form, no mailto:, nothing sent
# from the page — only a short text, en and de: feedback, errors and contact
# by e-mail to the contact address (E21.13). The address is plain text (the
# reader copies it). In the ⚙ drawer this cell; on the cover the same words
# (card_facts.feedback_note, build time, both languages).
#   FEEDBACK                  the address, the heading and the line, en and de
#   .nbfb > .nbfb-text > .nbfb-to     contract for CSS (small) and JS (nothing to wire)
FEEDBACK = {
    "to": "samuel.wiese@gmx.de",
    "label": {"en": "Feedback", "de": "Feedback"},
    "text": {"en": "Feedback, errors and contact: by e-mail to {to}",
             "de": "Feedback, Fehler und Kontakt: per E-Mail an {to}"},
}

# E29 D7 (2026-10-12, Python: Texte) — THE FONT SIZE, A CONTROL OF ITS OWN.
# Nutzer zu v1.75: "bei 100 % noch zu klein"; the size of the document's text,
# independent of the zoom (🔍), kept per notebook. Python gives the place in the
# ⚙ drawer and the words; the control is the page's (JS fills .nbfont-slot with
# the data-* range and takes the cell's inline display:none off), the look CSS's.
#   .nbcell.pg-diff.nbfontcell (display:none) > .nbcell-h · .nbfont-slot[data-min
#   data-max data-step data-std] · .nbcell-n         (claude/VERTRAG-E29-py.md)
FONT_SIZE = {"min": 90, "max": 150, "step": 10, "std": 100}

def _font_cell():
    return ('<div class="nbcell pg-diff nbfontcell" style="display:none"><div class="nbcell-h">%s</div>'
            '<div class="nbfont-slot" data-min="%d" data-max="%d" data-step="%d" data-std="%d" '
            'aria-label="%s"></div><div class="nbcell-n">%s</div></div>'
            % (_nbL("Font size", "Schriftgr\u00f6\u00dfe"), FONT_SIZE["min"], FONT_SIZE["max"], FONT_SIZE["step"],
               FONT_SIZE["std"], _nbL("font size of the document", "Schriftgr\u00f6\u00dfe des Dokuments"),
               _nbL("The size of the text, independent of the zoom (\U0001f50d). Kept for this notebook.",
                    "Die Gr\u00f6\u00dfe der Schrift, unabh\u00e4ngig von der Lupe (\U0001f50d). F\u00fcr dieses "
                    "Notebook gemerkt.")))

def _feedback_cell():
    import html as _h
    lg = LANG["value"] if LANG["value"] in ("en", "de") else "en"
    to = "<span class=\"nbfb-to\">%s</span>" % _h.escape(FEEDBACK["to"])
    return ('<div class="nbcell pg-fb nbfb"><div class="nbcell-h">%s</div>'
            '<div class="nbfb-text">%s</div></div>'
            % (_h.escape(FEEDBACK["label"][lg]), _h.escape(FEEDBACK["text"][lg]).replace("{to}", to)))

def _prog_html():
    """The control panel: the notebook's own accordion structure as a timeline,
    the two hairline bars, and the controls.

    Node sizes follow the hierarchy — a section gets a labelled marker, a numbered
    chapter a small solid dot with its name, an unnumbered section (setup, glossary,
    quiz, …) a tiny dot, and every exercise the big fillable circle."""
    done, tot, cdone, ctot = _prog_counts()
    NOTE = {"st-open": "not answered yet", "st-ans": "answered correctly",
            "st-code": "coding exercise solved", "st-both": "answer and code solved",
            "st-skip": "skipped — exercise still open",
            "st-lock": "locked — it opens with the exercise before it",
            "st-fail": "not answered (bypassed or solution revealed)"}
    cur = next((k for k in _answer_order() if _TASKS["state"].get(k) == "open"), None)
    # …and the same for the CODING chain (2026-09-24ag). The two ladders are
    # separate, so each needs its own "this is the one in front of you": the
    # first coding exercise that is neither settled nor waiting for the one
    # before it. Without it the code route had no open door to point at.
    # 2026-09-27e — …among the exercises that HAVE a coding exercise. Every
    # task carries a code state ("open" by default), so in a notebook where
    # only some chapters have code (Start: t1 and t3) the door went to t2,
    # which has no purple mark — and after coding 1 the rail showed no open
    # door at all. Complex has code everywhere, which is why it never showed.
    ccur = next((k for k in _TASKS["order"]
                 if _TASKS["has_code"].get(k)
                 and _TASKS["code"].get(k, "open") == "open" and not _is_locked_code(k)),
                None)

    # Spacing follows the content: the stretch of line a section occupies is
    # proportional to how much there is to read in it, with a floor so a two-line
    # meta section is still clickable and a ceiling so one long chapter does not
    # push everything else out of the window.
    # The spacing is measured from the CONTENT, not from the current layout: the
    # amount of material in a section is what its length would be in a fully
    # expanded document, and unlike a layout measurement it does not change when a
    # reader opens or closes an accordion. The timeline therefore has a fixed
    # length for a given notebook. Kept deliberately tight so the dots stay close.
    _nz = sorted(e.get("weight") or 0 for e in _STRUCT if (e.get("weight") or 0) > 0)
    _lo = (_nz[0] if _nz else 0) ** 0.5
    _hi = (_nz[-1] if _nz else 0) ** 0.5
    # A named chapter needs room for its name, so the scale for chapters starts
    # where two lines of title fit and grows from there with the content; the small
    # meta sections and the exercise circles keep the tight old scale.
    def _span(e):
        w = e.get("weight") or 0
        if not w or _hi <= _lo:
            return None
        f = (w ** 0.5 - _lo) / (_hi - _lo)
        if e["kind"] == "chapter":
            return int(round(166 + 58.0 * f))
        return int(round(24 + 44.0 * f))

    parts = []
    _chap_i = 0
    for e in _STRUCT:
        _px = _span(e)
        _sty = ' style="width:%dpx"' % _px if _px else ""
        aid = _aid(e["anchor"]) if e.get("anchor") else ""
        href = ' data-target="%s" href="#%s"' % (aid, aid) if aid else ""
        if e["kind"] == "title":
            # The title card lives in the notebook's FIRST cell, which is written
            # at build time and cannot know this run's anchor id. So this one bar
            # points at a class instead, resolved inside the notebook the panel
            # is currently serving — and a click on it goes to the very top.
            # 2026-09-28b (K2.11): named after the card's own heading.
            _tt = _NB_TITLE["text"] or e["title"]
            parts.append('<a class="nbjump nbmap-node sect title" '
                         'data-sel="nbtitle-card nbtitle" data-acc="title" '
                         'data-top="1" href="#" title="%s">'
                         '<span class="nbmap-lab">%s</span><span class="nbsect"></span></a>'
                         % (_esc_attr(_tt), _esc_txt(_tt)))
        elif e["kind"] == "cell":
            parts.append('<a class="nbjump nbmap-node sect cell" data-bottom="1" data-acc="yoc" '
                         'href="#" title="%s — the empty cell JupyterLab leaves you '
                         'at the end; click to go there">'
                         '<span class="nbmap-lab">%s</span><span class="nbsect"></span></a>'
                         % (e["title"], e["title"]))
        elif e["kind"] == "end":
            # the same bar a section header gets, and it carries the 'end' class
            # so the track, the lanes and the gaps all stop on it
            parts.append('<a class="nbjump nbmap-node sect end" data-mark="nbend"%s '
                         'title="%s — and not the end of the notebook: there is an '
                         'empty cell under it, carry on there or rewrite what is '
                         'above">'
                         '<span class="nbmap-lab">%s</span><span class="nbsect"></span></a>'
                         % (href, e["title"], e["title"]))
        elif e["kind"] == "group":
            # the FIRST section starts flush with the left edge of the window, so
            # the line and the scrollbar under it begin at the same place
            _first = not any(p.startswith('<a class="nbjump nbmap-node sect') for p in parts)
            parts.append('<a class="nbjump nbmap-node sect%s"%s title="%s %s">'
                         '<span class="nbmap-lab">%s</span><span class="nbsect"></span></a>'
                         % (" first" if _first else "", href, e["icon"],
                            e["title"], e["title"]))
        elif e["kind"] == "chapter":
            # the name, not the number. All names sit on ONE row — the chapter
            # nodes are wide enough that two long titles never meet.
            _chap_i += 1
            # a chapter that is still shut says so, in the name and on its dot
            _shut = bool(e.get("task")) and _is_locked(e["task"])
            _open = bool(e.get("task")) and not _shut
            parts.append('<a class="nbjump nbmap-node chap%s"%s%s title="%s · %s%s">'
                         '<span class="nbmap-lab">%s</span>%s'
                         '<span class="nbchapdot">%s</span></a>'
                         % (" locked" if _shut else (" unlocked" if _open else ""),
                            href + (' data-lock="%s"' % _TASKS["guard"].get(e["task"], "")
                                    if _shut else "") + _state_attrs(e.get("task")),
                            _sty, e["num"], e["title"],
                            # 2026-09-25c — AND THE TOOLTIP SAID THE WRONG
                            # THING. It offered a double click, which is the
                            # gesture that was taken away yesterday precisely
                            # because it opened chapters by accident. A tooltip
                            # that teaches a gesture the build refuses is worse
                            # than none.
                            # E30 (2026-10-12) — and since D3 (E29) a click on a shut
                            # chapter does nothing but show its lock card: the tooltip
                            # says what the card says, not a gesture that is gone
                            ((" — locked: it opens once %s is answered"
                              % ("Exercise %s" % _answer_num(_TASKS["guard"].get(e["task"], ""))))
                             if _shut else ""),
                            # 2026-09-25d — THE NAME SAYS WHAT THIS IS, NOT
                            # WHAT IT IS CALLED. The column is one line high
                            # and the reader is looking for structure: where am
                            # I, what comes next. "Chapter 3" answers that at a
                            # glance; the title needs reading, and it is one
                            # hover away in the tooltip where it always was.
                            # 2026-09-28b (K2.8) — …and the title after it
                            # (user, 27.09.): "Chapter 1: Why complex
                            # numbers?". The column ends in an ellipsis where
                            # the title is long; the tooltip keeps all of it.
                            _esc_txt("Chapter %s: %s" % (e["num"], e["title"])),
                            _chap_pips(e.get("task")),
                            # the padlock is DRAWN from the `locked` class now
                            # (see the stylesheet). Written here it was a colour
                            # emoji no skin could reach, sitting inside a mark
                            # whose font-size is zero — invisible, and still in
                            # the DOM for a screen reader to announce.
                            ""  if _shut
                            # 2026-09-24ar — the open padlock goes on the chapter
                            # that was OPENED, not on the one whose exercise was
                            # skipped to open it. `skipped_open` holds the
                            # GUARDING task; this node carries the guarded one,
                            # so the two never matched and 🔓 never appeared once.
                            # 2026-09-24az — and once it IS open, the mark
                            # carries nothing. The open padlock is the state
                            # BETWEEN picking the chapter and turning the key;
                            # a chapter that is simply open is not a lock any
                            # more, and a glyph saying otherwise is noise.
                            else ""))
        elif e.get("task") and not e.get("task_anchor"):
            # 2026-09-28b (K2.3) — ONE MARK FOR ONE EXERCISE. A section that IS
            # an exercise (the quiz, "bring your own data") had two marks on
            # the same spot: its own dot and the exercise circle, both pointing
            # at the same anchor. The circle below stands for both.
            pass
        else:
            parts.append('<a class="nbjump nbmap-node sub"%s%s title="%s">'
                         '<span class="nbmap-lab">%s</span><span class="nbsubdot"></span></a>'
                         % (href, _sty, e["title"], e["title"]))
        if e.get("viz_anchor"):
            vaid = _aid(e["viz_anchor"])
            parts.append('<a class="nbjump nbmap-node viztask" '
                         'data-target="%s" href="#%s" '
                         'title="%s \u00b7 visualisation for this chapter">'
                         '<span class="nbmap-lab">%s</span>'
                         '<span class="nbvizmark"></span></a>'
                         % (vaid, vaid, e["title"],
                            _esc_txt(("Figure %s: %s" % (e["num"], e["figure"]))
                                     if e.get("figure") else "Figure %s" % e["num"])))
        task = e.get("task")
        if task:
            cls = _dot_class(task)
            st  = _TASKS["state"].get(task, "open")
            num = _answer_num(task)                  # R3 · 18
            cnum = _TASKS["order"].index(task) + 1 if task in _TASKS["order"] else "•"
            taid = _aid(e["task_anchor"]) if e.get("task_anchor") else aid
            thref = ' data-target="%s" href="#%s"' % (taid, taid) if taid else href
            # the label reads "3 · add / subtract" — the number is already in the
            # tooltip, so only the name goes under the circle
            _tl = _TASKS["label"].get(task, "")
            _short = _tl.split("\u00b7")[-1].strip() if "\u00b7" in _tl else _tl
            # R3 · 18 — mode "code": no written part, no circle; the purple
            # mark below stands alone
            if task not in _TASKS["noanswer"]:
              parts.append('<a class="nbjump nbmap-node task%s"%s data-task="%s"%s '
                         'title="%s · exercise %s — %s">'
                         '<span class="nbmap-lab"></span>'
                         '<span class="nbrail-dot %s"><i class="nbdotg">%s</i></span>'
                         '<span class="nbtasklab">%s</span></a>'
                         % (" is-current" if task == cur else "", thref, task,
                            _state_attrs(task),
                            e["title"], num, NOTE[cls], cls,
                            _dot_mark(task, cls, task == cur),
                            _esc_txt(("Exercise %s: %s" % (num, _TASKS["name"][task]))
                                     if _TASKS["name"].get(task) else "Exercise %s" % num)))
            # ...and, where there is a coding exercise, its own mark right after
            # the circle: a purple rounded square, so the second progression is
            # readable on the rail and not only in the ticks inside the circle.
            if e.get("code_anchor"):
                ccls = _code_class(task)
                if task == ccur and ccls == "cd-open":
                    ccls = "cd-open cd-current"
                caid = _aid(e["code_anchor"])
                parts.append('<a class="nbjump nbmap-node codetask" '
                             'data-target="%s" href="#%s" data-task="%s"%s '
                             'title="%s · exercise %s — %s">'
                             '<span class="nbmap-lab">%s</span>'
                             '<span class="nbcodemark %s"><i class="nbdotg">%s</i>'
                             '</span></a>'
                             % (caid, caid, task, _state_attrs(task), e["title"], cnum,
                                _CODE_NOTE[ccls],
                                _esc_txt(("Coding %s: %s()" % (cnum, _TASKS["cname"][task]))
                                         if _TASKS["cname"].get(task) else "Coding %s" % cnum),
                                ccls,
                                {"cd-done": "✓", "cd-skip": "⤳",
                                 "cd-fail": "✗",
                                 # drawn from the class — see _dot_mark
                                 "cd-lock": "",
                                 "cd-open cd-current": ""}.get(ccls, "")))
    if parts:
        parts[-1] = parts[-1].replace('class="nbjump nbmap-node', 'class="nbjump nbmap-node last', 1)
    nodes = "".join(parts)
    ctrl = ('<span class="nbctrl">'
            '<span class="nbdock-l">'
            '<button class="nbbtn nbgear" title="difficulty — how close an answer '
            'has to be, and how much a hint says">\u2699</button>'
            '<button class="nbbtn nbfull"  title="full screen">⛶</button>'
            '<button class="nbbtn nbtheme" title="switch this notebook between light and dark">◐</button>'
            # 2026-09-24bg — light/dark is BRIGHTNESS; this is MATERIAL. Two
            # buttons side by side, because they are two independent choices:
            # every skin works on a light page and on a dark one.
            '<button class="nbbtn nbskin" title="the notebook\'s style — '
            'digi, minimal, cyberpunk, retro or fairy. It works with light and dark, '
            'not instead of them.">\U0001F3A8</button>'
            # 2026-09-25f — the keyboard. A list of shortcuts nobody can find
            # is a list nobody uses, so it gets a key of its own.
            # 2026-09-25h: Alt+. enters the keyboard mode, ? opens this list.
            '<button class="nbbtn nbkeys" title="keyboard \u2014 Alt+. '
            'to steer the panel, then ? for the keys">\u2328</button>'
            '</span>'
            '<span class="nbdock-c">'
            '<button class="nbbtn nbprofile" title="your progress code — the part '
            'of this that is yours. Click to open it.">\U0001F464 <span '
            'class="nbpid">—</span></button>'
            '<button class="nbbtn nbseries" title="progress across the whole '
            'series — click for the notebook-by-notebook list">📚 —</button>'
            '</span>'
            '<span class="nbdock-r">'
            # 2026-09-24bb — back on the right, where it started. It moved left
            # in 24au because the rail was painted over that corner; since 24ax
            # the toolbar is cut at the rail's left edge instead, so the corner
            # is free again and the control sits where the eye looks for it —
            # at the right end of the bar, immediately beside the panel.
            '<span class="nbzoomgrp nbz-doc" title="the size of the DOCUMENT — '
            'drag, turn the wheel over it, or double-click to go back to 100%">'
            '<input type="range" class="nbslider nbzoom-lab" min="0" max="100" '
            'step="5" value="100" aria-label="document size">'
            '<span class="nbslval">\U0001f50d</span></span>'
            # 2026-09-24ao — the panel's own size control is gone. With the
            # names off the rail there is nothing in a wide panel to look at,
            # and the control was the widest thing in a toolbar that is meant to
            # be quiet. The rail is one column of marks at one size now.
            ''
            '</span>'
            '</span>')
    # One drawer, two pages. The gear opens the difficulty page, the profile
    # chip opens the progress page; the host carries data-page and the CSS shows
    # one of them. Two tiles, two little windows, one mechanism.
    # 2026-09-24bb — THE BUILD STAMP, WHERE A READER CAN SEE IT.
    # "How do I know I have the new version?" had no answer on screen: the
    # version lived in a JS variable and in the file's name, neither of which
    # the reader looks at. It is one line in the gear drawer now, so the
    # question is a glance.
    # E21.7 (2026-10-02, Struktur) — ONCE, SMALL, IN ⚙ ONLY. The line was the
    # drawer's head, so every window of the drawer (⚙, 👤, 📚) carried it, and
    # the title card had it as a hover stamp (measured v1.61: 3 visible places
    # + the card's title). It is now the last line of the ⚙ cell, small, with
    # its own inline size (no stylesheet needed); nowhere else.
    drawer = ('<div class="nbdrawer">'
              '<div class="nbdrawer-grid">'
              # E9.9 (2026-09-30, Inhalt, Skizze) — the ⚙ "Content" field (py-18)
              # sits in this cell, under a heading that only said "Difficulty":
              # it was there and it worked, but nothing on the page said that the
              # mode can be changed here. The heading and the note now say both.
              '<div class="nbcell pg-diff"><div class="nbcell-h">Difficulty \u00b7 Content</div>'
              '<div class="nbslot" data-slot="nbctl-difficulty"></div>'
              '<div class="nbcell-n">Difficulty: how close an answer must be, and how much a hint '
              'says. The question stays the same.<br>Content: calculate, code or both.</div>'
              '<div class="nbbuild" title="the version of this notebook, and the toolkit build '
              'it came from" style="margin-top:10px;text-align:center;font-size:.72em;'
              'letter-spacing:.3px;opacity:.6">v' + NB_VERSION
              + ' \u00b7 build ' + TOOLKIT_VERSION + '</div></div>'
              '<div class="nbcell pg-code"><div class="nbcell-h">Carry your progress</div>'
              '<div class="nbslot" data-slot="nbctl-code"></div></div>'
              # E38a P6 (2026-10-26, Python; Nutzer 14.10.: Reihen- und Gesamtstatistik sehen alle) — the role
              # "administrator" is gone without replacement: no "You are" row, no line about teaching (JS: J3)
              '<div class="nbcell pg-keys"><div class="nbcell-h">Keyboard</div>'
              '<div class="nbkeys-slot"></div>'
              '<div class="nbcell-n">Every key is tested in JupyterLab. '
              'Send an answer with Enter in its field.</div></div>'
              '<div class="nbcell pg-stats"><div class="nbcell-h">This notebook, in this browser</div>'
              '<div class="nbserieslist">—</div>'
              '<div class="nbcell-n">Stays in this browser. No grade.</div></div>'
              '<div class="nbcell pg-diff"><div class="nbcell-h">Your seed</div>'
              '<div class="nbslot" data-slot="nbctl-seed"></div>'
              '<div class="nbcell-n">The exercise numbers come from this seed. '
              'Same seed, same exercises \u2014 for anyone.</div></div>'
              '<div class="nbcell pg-code"><div class="nbcell-h">Start over</div>'
              '<div class="nbslot" data-slot="nbctl-reset"></div></div>'
              + _font_cell() + _feedback_cell() +       # E29 D7 · E29 P5
              '</div></div>')
    # Two separate things now: the RAIL is only the timeline, and the DOCK holds
    # every control. The dock is pinned to one corner of the document at a fixed
    # size, so nothing the reader does to the timeline — thickness, orientation,
    # either zoom — moves or rescales the buttons they need to undo it with.
    # 2026-09-24bf — THE GRIP. The panel's size control is back, and it is the
    # panel's own edge: a short bar on the rail's left flank, half way down.
    # Drag it left and the timeline grows into the page; drag it right and it
    # folds back to the bare line. That is the whole of it — no slider, no
    # readout, no drawer to open first, and it sits where the thing it resizes
    # is. A click without a drag jumps between the two ends, so the button is
    # not dead to anyone who does not think to pull it.
    # It is written into the rail's own markup rather than added by script, so
    # it survives every panel rebuild the way the marks do.
    # 2026-09-24bi — the grip and the cursor are SIBLINGS of the rail, not
    # children of it. The rail is overflow:hidden (it has to be — the marks
    # scroll inside it), so anything hanging off its edge was cut off. Both are
    # placed by the panel script in window coordinates instead, which is also
    # what lets the grip hang OUTSIDE the panel, on its left flank, where the
    # reader reaches for it.
    rail = ('<button class="nbgrip" type="button" tabindex="-1" '
            # 2026-09-30 (E10.9, Oberfläche): the knob moves the reading
            # height since E9.1 — same words as 19-rail-title-sync.js (GT), so
            # the tooltip is right before the script runs and it has nothing to swap.
            'title="drag up or down to move the reading height, left or right '
            'to widen or narrow the timeline">'
            '<span></span></button>'
            '<div class="nbmap-cursor" title="drag to move through the '
            'notebook"></div>'
            '<div class="nbrail">'
            '<div class="nbrail-row">%s</div></div>'
            '<div class="nbdock">%s%s</div>'
            % (_map_html(nodes, done, tot, cdone, ctot), ctrl, drawer))
    strip = ('<div class="nbprog"><div style="font-weight:800;font-size:.95em">Your progress</div>'
             '%s</div>' % _map_html(nodes, done, tot, cdone, ctot, wide=True))
    import json as _json
    # 's' is the new field: passed / skipped / given up. An older panel script
    # ignores it, and a newer one treats a record without it as all-zero — so a
    # browser that already holds records from earlier notebooks keeps working.
    _p, _s, _f = _prog_states()
    # 'g' is the difficulty breakdown of the passes, gentle / standard / strict.
    # Added the same way 's' was: an older panel ignores it, a newer one treats a
    # record without it as "all at standard", which is what those runs were.
    snap = _json.dumps({"id": NOTEBOOK["id"], "title": NOTEBOOK["title"],
                        "a": [done, tot], "c": [cdone, ctot], "s": [_p, _s, _f],
                        "g": _prog_diffs(), "m": MODE["value"]},
                       separators=(",", ":"))
    # position:relative AND a transform. The rail is absolutely positioned and the
    # dock is FIXED — and a fixed element ignores overflow:hidden entirely unless
    # an ancestor establishes a containing block for it. Without the transform the
    # hidden feed's copy of the toolbar floated over the page next to the real
    # one: two toolbars, one of them dead.
    # E19.4: data-nbenv, where the kernel runs (kept out of the format below)
    return ('<div class="nbfeed" data-nbenv="' + kernel_env() + '" '
            'data-nbdefaults=\'' + _json.dumps(NB_DEFAULTS, separators=(",", ":")) + '\' '   # E25.o
            'data-nbid="%s"%s data-progress=\'%s\' '
            'data-nbmode="%s" '                   # R3 · 18: the mode this run built
            'data-nblang="%s" '                   # E17.5: the language this run built
            'data-goto="%s:%d:%s:%s" '
            'style="height:0;overflow:hidden;position:relative;transform:translateZ(0)">'
            '%s</div>%s'
            % (_NBID, ' data-final="1"' if _PROG.get("final") else "",
               snap.replace("'", "&#39;"), MODE["value"], LANG["value"],
               _GOTO["run"], _GOTO["seq"], _GOTO["route"], _GOTO["key"],
               rail, strip))

def _refresh_progress():
    html = _prog_html()
    if _PROG["w"] is not None:
        _PROG["w"].value = html
    # the mirrors carry the same panel; the script picks whichever one is mounted,
    # so scrolling or a re-render can never leave the panel without a source
    for m in _PROG["mirrors"]:
        m.value = _mirror_html(html)
    if _PROG.get("persist"):
        progress_store()

def _mirror_html(html):
    """Only the pinned part — a mirror never shows the inline strip."""
    i = html.find('</div>', html.find('nbfeed'))
    return html[:html.find('<div class="nbprog"')] if '<div class="nbprog"' in html else html

_FINALIZERS = []

def on_notebook_built(fn):
    """Register work that can only be done once EVERY chapter has rendered — the
    reference list above all: its numbers follow the order the sources first
    appear in the text, so it cannot be written while chapters are still to come.
    The callbacks run just before the panel, which is the last thing built."""
    _FINALIZERS.append(fn)

def _run_finalizers():
    for fn in _FINALIZERS + globals().get("_FINALIZERS_EARLY", []):
        try:
            fn()
        except Exception as e:
            print("finalizer failed: %r" % (e,))

# E19.9 (2026-10-02, Oberfläche; Python = SVG-Markup) — ORNAMENTS OF OUR OWN,
# ONE SET PER STYLE. Two motifs, drawn here (own shapes, no known work):
#   crest   64 × 24  under the title card — REMOVED in E21.14
#   rule   240 × 16  at the end of the guided part
# (the boxes inside the chapters carry the CSS ornament of css-E19.9; these
# two are the places it does not reach)
# The drawings travel ONCE, as <symbol>s in a hidden sprite under the title
# card; each place is a tiny <svg><use href="#nbo-…"/></svg>. A symbol holds
# one <g class="nbo-<style>"> per style; minimal shows without any stylesheet,
# the other three carry display="none" (a presentation attribute). The sprite
# brings the four rules that pick the group for body.nbskin-<s> itself (its
# own classes only), so it is right in every style before CSS knows it; CSS
# may move them into its files. .nborn / .nborn-rule are the
# handles to place and colour them (ink = currentColor, accent = --nbmark).
# Rules from the document reach into <use> (SVG 2, measured in Chromium).
_ORN_ACC = 'style="fill:var(--nbmark,currentColor)"'
_ORN_LINE = 'fill="none" stroke="currentColor"'
_ORN = {
  "rule": ("0 0 240 16", {
    "minimal": '<path d="M24 8H108M132 8H216" %s stroke-width="1" opacity=".55"/>'
               '<path d="M120 3l5 5-5 5-5-5z" %s/>' % (_ORN_LINE, _ORN_ACC),
    "cyber":   '<path d="M6 8H64l6-5h30M140 3h30l6 5h58" fill="none" '
               'style="stroke:var(--nbmark,currentColor)" stroke-width="1.4"/>'
               '<path d="M110 8l4-6h12l4 6-4 6h-12z" %s stroke-width="1.4"/>'
               '<circle cx="6" cy="8" r="2" %s/><circle cx="234" cy="8" r="2" %s/>'
               '<circle cx="120" cy="8" r="2" %s/>' % (_ORN_LINE, _ORN_ACC, _ORN_ACC, _ORN_ACC),
    "fairy":   '<path d="M14 8c14-7 26 7 40 0s26 7 40 0M146 8c14-7 26 7 40 0s26 7 40 0" '
               '%s stroke-width="1.2" opacity=".7"/>'
               '<path d="M120 0l2 6 6 2-6 2-2 6-2-6-6-2 6-2z" %s/>'
               '<circle cx="102" cy="8" r="1.6" %s/><circle cx="138" cy="8" r="1.6" %s/>'
               % (_ORN_LINE, _ORN_ACC, _ORN_ACC, _ORN_ACC),
    "retro":   '<path d="M12 6H100M12 10H100M140 6H228M140 10H228" %s stroke-width="1" opacity=".7"/>'
               '<path d="M106 13a14 14 0 0 1 28 0z" %s/>'
               '<path d="M120 13V2M120 13l-8-8M120 13l8-8" %s stroke-width="1"/>'
               % (_ORN_LINE, _ORN_ACC, _ORN_LINE),
    # E34 P1: digi — a hairline, the gold pill of the web site and the app in the
    # middle (radius = half the height), two small dots beside it
    "digi":    '<path d="M18 8H98M142 8H222" %s stroke-width="1" opacity=".45"/>'
               '<rect x="106" y="4" width="28" height="8" rx="4" %s/>'
               '<circle cx="101" cy="8" r="1.4" %s/><circle cx="139" cy="8" r="1.4" %s/>'
               % (_ORN_LINE, _ORN_ACC, _ORN_ACC, _ORN_ACC)}),
}
# E34 P1: digi is the fifth style (and the standard, NB_DEFAULTS); minimal stays
# first — it is the one group shown without any stylesheet
_ORN_SKINS = ("minimal", "cyber", "retro", "fairy", "digi")

def ornament_sprite():
    """The hidden sprite: one <symbol> per motif, one group per style."""
    out = []
    for kind, (vb, art) in _ORN.items():
        out.append('<symbol id="nbo-%s" viewBox="%s">%s</symbol>' % (kind, vb, "".join(
            '<g class="nbo-%s"%s>%s</g>' % (k, "" if k == "minimal" else ' display="none"', art[k])
            for k in _ORN_SKINS)))
    pick = ",".join("body.nbskin-%s .nbo-%s" % (k, k) for k in _ORN_SKINS[1:])
    hide = ",".join("body.nbskin-%s .nbo-minimal" % k for k in _ORN_SKINS[1:])
    return ('<svg class="nbo-sprite" aria-hidden="true" width="0" height="0" '
            'style="position:absolute;width:0;height:0;overflow:hidden">'
            '<style>%s{display:inline}%s{display:none}</style>%s</svg>' % (pick, hide, "".join(out)))

def ornament(kind):
    """One ornament in place (needs the sprite on the page)."""
    vb = _ORN[kind][0].split()
    return ('<svg class="nborn nborn-%s" aria-hidden="true" width="%s" height="%s" viewBox="%s" '
            'style="display:block;margin:6px auto;color:#8b98a5;overflow:visible">'
            '<use href="#nbo-%s"/></svg>' % (kind, vb[2], vb[3], _ORN[kind][0], kind))

def title_card(html):
    """The notebook's heading, INSIDE the document cell (2026-09-24bh).

    The markdown cell above carries the same card, and that one is what a cold
    notebook shows — a notebook with no outputs has nothing else. The moment
    this runs, the document has a heading of its own and the panel hides the
    cell, so the reader sees one title, in the flow, with no cell furniture
    around it.

    It is handed the markup rather than building it, because the title belongs
    to the notebook and not to the toolkit — the build script writes it once
    and both copies come from that one string."""
    # the outer <div class="nbtitle"> of the markdown cell carried the
    # centring as an inline style (it has to: on a cold page there is no
    # stylesheet yet), and the split above drops that wrapper — so it is
    # restated here. Without it the card sat hard against the left edge of the
    # cell while the whole document below it was centred.
    # E9.5 — the italic line under the card (the subtitle) goes INTO the
    # title's accordion; the card stays outside, as the pill it folds from
    _lead = ""
    _m = _re.search(r'<div class="nbtitle-lead".*\Z', html, _re.S)
    if _m:
        _lead = _m.group(0)
        html = html[:_m.start()]
    # E21.14 (2026-10-02, Oberfläche) — no crest under the title pill any more
    # (the three dots of E19.9, Nutzer: "entfernen"); the sprite stays for the
    # end rule
    html += ornament_sprite()      # E19.9
    # E25.a (2026-10-08, Python) — ONE PREVIEW WHERE NO WIDGET IS DRAWN.
    # PyCharm (Video 08.10.) showed this card, the panel's "Your progress"
    # strip of the still copy, and the cover with its own card: two title
    # cards. Where the still copy is on (_static_on) the cover — the last
    # output, the one place with Play, mode, language, login — is the only
    # preview: this card is written hidden (class nbstatic-hide; the page
    # script may show it once Play has opened the document), the strip is
    # left out of the still copy (_static_html). JupyterLab, Lite, Colab and
    # VS Code are unchanged.
    # E26.1: where no widget is drawn the card stays out by itself (.nbwarm, _nbread_end)
    _card = IHTML('<div class="nbtitle nbtitle-doc" '
                  'style="text-align:center;margin:8px 0 6px">%s</div>' % html)
    try:
        _NB_TITLE["handle"] = display(_card, display_id=True)
    except TypeError:
        display(_card)
    _NB_TITLE["html"] = html
    _root_start(_lead)
    # 2026-09-28b (K2.11) — THE TOP MARK CARRIES THE NOTEBOOK'S NAME.
    # The first mark on the timeline said "Title page" in every notebook. It
    # now reads the heading of this very card — the same string the build
    # script wrote once for both copies of the card — so it cannot disagree
    # with the title the reader sees, and nobody types it a second time.
    t = _title_text(html)
    if t:
        _NB_TITLE["text"] = t

_NB_TITLE = {"text": None}

def _title_mode_line():
    """R3 · 18 — the build wrote the card for "both". On another mode the time
    line under it is written again once every chapter is built, from the same
    counts the panel uses."""
    if MODE["value"] == "both" or not _NB_TITLE.get("handle") or not _NB_TITLE.get("html"):
        return
    import html as _h
    new = _re.sub(r"(<div class='nbtitle-time'[^>]*>)(.*?)(</div>)",
                  lambda m: m.group(1) + _h.escape(time_budget_text()) + m.group(3),
                  _NB_TITLE["html"], count=1, flags=_re.S)
    try:
        _NB_TITLE["handle"].update(IHTML('<div class="nbtitle nbtitle-doc" '
                                         'style="text-align:center;margin:8px 0 6px">%s</div>' % new))
    except Exception:
        pass
_FINALIZERS_EARLY = [_title_mode_line, _mode_inbox_show]      # E21.6: the inbox

def _title_text(html):
    """The text of the card's `.nbtitle-h` — tags dropped, entities read."""
    import html as _h
    m = _re.search(r'class="nbtitle-h"[^>]*>(.*?)</div>', html or "", _re.S)
    if not m:
        return None
    t = _h.unescape(_re.sub(r"<[^>]+>", "", m.group(1))).strip()
    return " ".join(t.split()) or None


def progress_panel():
    """The notebook's own panel source. It is emitted LAST, once every chapter has
    been built, so the panel that appears is the finished one — the mirrors above
    it only keep it alive when a cell re-renders."""
    """The progress panel — display it once, above the chapters."""
    _root_end()        # E9.5: a notebook without notebook_end() still shows its chapters
    _run_finalizers()
    _progress_resume()
    _PROG["w"] = HTML(layout=_w(), value=_prog_html())
    return _PROG["w"]

def progress_mirror():
    """A zero-height twin of the panel, emitted between chapters. Cheap insurance:
    whatever JupyterLab decides to keep mounted, at least one source is on screen."""
    m = HTML(layout=Layout(height="0px", margin="0px", width="100%"),
             value=_mirror_html(_prog_html()))
    _PROG["mirrors"].append(m)
    return m

def _open_lock(kind, key, unfold=True):
    ent = _LOCKS.get((kind, key))
    if ent is not None and not ent["open"]:
        # Paket 21b — the chapter's pictures, drawn now that it can be seen
        _lazy_run(ent.pop("lazy", ()))
        ent["shell"].children = (ent["real"],)
        ent["open"] = True
        # 2026-09-28a (K1) — a task fold that waited for this one may open now
        for _ta in ent.get("taccs", ()):
            try: _ta.remove_class("acc-tasklock")
            except Exception: pass
        pill = ent.get("pill")
        if pill and not unfold:
            acc, label = pill
            _set_acc_title(acc, label)
            try: acc.remove_class("acc-locked")
            except Exception: pass
        elif pill:
            acc, label = pill
            _set_acc_title(acc, label)
            try: acc.remove_class("acc-locked")
            except Exception: pass
            # 2026-09-24ar — AND IT UNFOLDS, ALWAYS.
            # This used to be `if selected_index is None`, which meant "only if
            # the reader has never touched it". An accordion that was opened and
            # closed again reports 0, so for any chapter the reader had looked
            # at once, the lock came off invisibly and the chapter stayed shut —
            # nothing on screen said anything had happened. Unlocking a chapter
            # IS putting it in front of the reader; there is no version of this
            # event where the chapter should stay folded.
            try: acc.selected_index = 0
            except Exception: pass

def _unlock_next(key, exercises=True, fold=None, unfold=True, refresh=True):
    """The ANSWER chain: the next chapter and its exercise.

    2026-09-24bf — `exercises` separated the two: a skip opened the chapter and
    left its exercise shut until the skipped one was answered correctly.
    2026-09-28a (K1, Applikation) — overturned. A task is locked until the one
    before it is ANSWERED — right, wrong or skipped — and then it opens. That
    is the rule the restore (apply_progress_code) always applied, so live and
    restored now agree. `fold` says whether the next exercise is unfolded for
    the reader (only after a right answer); `unfold=False` opens the locks and
    moves nothing on screen (a wrong answer, a revealed solution).

    2026-09-28 (R1 · Paket 1, Applikation) — `refresh`: the panel follows. The
    night fuzz found that code in the reader's own cell calling `_unlock_next`
    directly opened chapters in the document while the panel kept them locked.
    A caller that refreshes itself right after may pass `refresh=False`
    (task_solved, the restore …); a direct call (the default) refreshes here.
    task_skipped / task_code_skipped / task_wrong still refresh twice — they
    were reserved by the JS workshop in R1; the second refresh is harmless."""
    _open_lock("chapter", key, unfold=unfold)   # the next chapter opens with it
    if exercises:
        _open_lock("practice", key)
    if unfold:
        _open_following(key, fold=exercises if fold is None else fold)
    if refresh:
        _refresh_progress()

def _task_lock(ent_key, acc):
    """A TASK FOLD THAT WAITS DOES NOT OPEN (2026-09-28a, K1.2).

    Until 27h a locked coding fold unfolded onto a note and a skip button. Now
    it does not unfold at all — not by a click on its pill, not from the
    timeline, not by a key. Three layers, one state: the class `acc-tasklock`
    (the page refuses the click, see the panel script), and this observer,
    which folds it straight back if anything opens it anyway (a script, a
    widget message). `_open_lock` removes the class when the lock comes off."""
    ent = _LOCKS.get(ent_key)
    if ent is None:
        return
    ent.setdefault("taccs", []).append(acc)
    if not ent.get("open"):
        try: acc.add_class("acc-tasklock")
        except Exception: pass
    def _shut(ch, _e=ent, _a=acc):
        if ch.get("new") is not None and not _e.get("open"):
            try: _a.selected_index = None
            except Exception: pass
    try: acc.observe(_shut, "selected_index")
    except Exception: pass

def _unlock_next_code(key, refresh=True):
    """The CODE chain, and nothing else.

    Settling a coding exercise — solved, skipped or given up — opens the NEXT
    coding exercise. It deliberately does not open a chapter: the two
    progressions are separate, which is the whole point of having two of them.
    A reader who writes no Python is never held up, and a reader who does is
    never forced to answer the numbers first."""
    _open_lock("code", key)
    _open_following_code(key)
    if refresh:                          # R1 · Paket 1: as _unlock_next
        _refresh_progress()

def _open_following_code(key):
    """Open the next coding fold, the way _open_following opens the next chapter."""
    order = _TASKS["order"]
    try:
        i = order.index(key)
    except ValueError:
        return
    for nxt in order[i + 1:]:
        acc = _TASKS["cacc"].get(nxt)
        if acc is None:
            continue
        try:
            if getattr(acc, "selected_index", 0) is None:
                acc.selected_index = 0
        except Exception:
            pass
        return

def _open_following(key, fold=True):
    """Settling an exercise opens the chapter it unlocks.

    `fold` says whether the chapter's own PRACTICE fold is opened with it. It is
    False when the reader came along the code route: they get the chapter and
    their own next coding exercise, and the written one stays shut until they
    ask for it (2026-09-24ak).

    The lock coming off is not the same thing as the chapter being in front of
    the reader: it was still folded shut, three screens down, and had to be
    hunted for. Opening it is the other half of the same event. The chapter just
    finished is left exactly as it is — nothing is taken away from a reader who
    wants to read it again."""
    order = _TASKS["order"]
    try:
        i = order.index(key)
    except ValueError:
        return
    for nxt in order[i + 1:]:
        acc = _TASKS["acc"].get(nxt)
        if acc is None:
            continue
        # 2026-09-24ar — unconditionally, for the reason in `_open_lock`: a
        # chapter the reader had already opened once reports 0 rather than None
        # and was therefore left folded at the exact moment it was unlocked.
        try:
            acc.selected_index = 0
        except Exception:
            pass
        if fold:
            # …and the exercise inside it, on the route the reader is using
            pacc = _TASKS["pacc"].get(nxt)
            if pacc is not None:
                try:
                    if getattr(pacc, "selected_index", 0) is None:
                        pacc.selected_index = 0
                except Exception:
                    pass
        return

def completion_button(task, label="I have worked through this"):
    """Some chapters cannot be graded automatically — the quiz reports nothing back
    to Python, and 'bring your own data' has no right answer. There the reader says
    when they are through, and the circle on the timeline fills. Clicking again
    reopens it, so it is a marker, not a claim."""
    btn = Button(description="\u2713  " + label, layout=Layout(width="auto", height="38px"))
    btn.add_class("nbunlock")
    out = HTML(layout=_w(), value="")
    def _toggle(_b):
        if _TASKS["state"].get(task) == "done":
            _TASKS["state"][task] = "open"
            btn.description = "\u2713  " + label
            out.value = ("<div class='nbink' style='text-align:center;font-size:.9em'>"
                         "Marked as open again.</div>")
            _refresh_progress()
        else:
            task_solved(task)
            btn.description = "\u21ba  Mark as not done"
            out.value = ("<div class='nbok' style='text-align:center;font-size:.9em'>"
                         "Done \u2014 the circle for this section is filled.</div>")
    btn.on_click(_toggle)
    return VBox([center(btn), center(out)], layout=Layout(width="100%"))

# ======================================================================
# 2026-09-26 (Inhalt A), eingebaut R2 · Paket 15 — LEARNING GOALS, TIME
# BUDGET AND CHAPTER LIST: ONE SOURCE EACH, READ BY THE TITLE CARD.
#   * goals are declared ONCE, in _setup_*.py, with register_goals(); the
#     Introduction, the OER record and the title card all read them here;
#   * the minutes are never typed: TIME_RULE × what the registries count;
#   * the chapters on the card are the panel's chapters (_STRUCT), so the
#     card's miniature cannot disagree with the timeline.
# The build runs the notebook once headless (toolkit/card_facts.py) and asks
# card_facts(), so the cold markdown card carries the SAME facts the running
# notebook computes.
# ======================================================================
_GOALS = []
_GOAL_TAGS = ("K1", "K2", "K3", "K4", "K5", "K6")
_GOAL_LEVELS = ("basic", "intermediate", "advanced")

def register_goals(rows):
    """rows: [(K-tag, level, text), …] — the 3–7 things a reader can do
    afterwards. Declared once, in _setup_*.py, before the chapters."""
    del _GOALS[:]
    for tag, level, text in rows:
        if tag not in _GOAL_TAGS:
            raise ValueError("goal tag %r is not one of K1–K6" % (tag,))
        if level not in _GOAL_LEVELS:
            raise ValueError("goal level %r is not one of %s" % (level, ", ".join(_GOAL_LEVELS)))
        if not str(text).strip():
            raise ValueError("a goal without text")
        _GOALS.append((tag, level, str(text)))

def goals():
    return list(_GOALS)

def goal_strings():
    """The goals as the OER record lists them: 'text (K3, basic)'."""
    return ["%s (%s, %s)" % (t, g, l) for g, l, t in _GOALS]

def goals_table_html():
    """The goals as the Introduction shows them — tag · level · text."""
    return "".join(
        "<tr><td style='padding:5px 14px 5px 0;vertical-align:top'><b class='nbaccent'>%s</b></td>"
        "<td style='padding:5px 14px 5px 0;vertical-align:top;white-space:nowrap'><i>%s</i></td>"
        "<td style='padding:5px 0'>%s</td></tr>" % (g, l, t) for g, l, t in _GOALS)

# Minutes one element costs a reader on the DEFAULT route (numbers, not code).
# Coding is optional, so its minutes stand beside the budget, never inside it.
TIME_RULE = {"chapter": 3, "task": 5, "figure": 2, "coding": 10}
_ELEMENTS = {"figure": 0}

def set_time_rule(**minutes):
    """Minutes per element for THIS notebook. An unknown element is an error."""
    unknown = sorted(k for k in minutes if k not in TIME_RULE)
    if unknown:
        raise KeyError("unknown time-rule element(s): %s" % ", ".join(unknown))
    TIME_RULE.update({k: int(v) for k, v in minutes.items()})

def element_counts():
    """What there is in this notebook, counted from the registries."""
    return {"chapter": sum(1 for e in _STRUCT if e.get("kind") == "chapter"),
            "task": len(_answer_order()),        # R3 · 18
            "coding": sum(1 for k in _TASKS["order"] if _TASKS["has_code"].get(k)),
            "figure": _ELEMENTS["figure"]}

def time_budget():
    """(minutes on the default route, extra minutes for the optional code)."""
    c = element_counts()
    base = sum(TIME_RULE[k] * c[k] for k in ("chapter", "task", "figure"))
    return base, TIME_RULE["coding"] * c["coding"]

def time_budget_text():
    """'≈ 80 min · 9 exercises · 7 coding (+70 min)' — always with ≈."""
    c = element_counts(); base, extra = time_budget()
    if MODE["value"] == "code":                 # R3 · 18: coding IS the route
        base, extra = base + extra, 0
    if plain():                                 # E16.11
        return "≈ %d min · text and figures" % base
    s = ("≈ %d min · %d exercise" if c["task"] == 1 else "≈ %d min · %d exercises") % (base, c["task"])
    if c["coding"] and MODE["value"] == "code":
        s += " · %d coding" % c["coding"]
    elif c["coding"]:
        s += " · %d coding (+%d min)" % (c["coding"], extra)
    return s

def card_chapters():
    """[(number, title)] of the numbered chapters, in timeline order."""
    return [(e["num"], e["title"]) for e in _STRUCT if e.get("kind") == "chapter"]

def card_facts():
    """Everything the title card needs from the content, as plain data."""
    base, extra = time_budget()
    return {"goals": goals(), "counts": element_counts(), "chapters": card_chapters(),
            "minutes": base, "coding_minutes": extra, "line": time_budget_text(),
            "timeline": card_timeline()}

def card_facts_html(facts=None):
    """Goals, chapter list and time line for the title card. Inline-styled,
    because on a cold page there is no stylesheet yet. WHAT it says is Inhalt;
    WHERE (Struktur) and HOW (Oberfläche) it looks may change."""
    import html as _h
    f = facts or card_facts()
    items = "".join(
        # no data-k: the markdown sanitiser strips it from <li> (measured 26.09.)
        "<li class='nbtitle-goal' style='margin:3px 0'>%s "
        "<span class='nbtitle-k' style='font-size:.8em;font-weight:700;opacity:.75'>%s</span></li>"
        % (_h.escape(t), g) for g, l, t in f["goals"])
    goals_html = ("<div class='nbtitle-facts-h' style='font-size:.74em;font-weight:800;"
                  "letter-spacing:2px;text-transform:uppercase;margin:0 0 6px'>You will be able to</div>"
                  "<ul class='nbtitle-goals' style='text-align:left;margin:0 auto;"
                  "padding-left:20px;max-width:620px;line-height:1.45'>%s</ul>" % items
                  if items else "")
    chaps = "".join(
        "<li class='nbtitle-chap' style='margin:2px 0'><b>%d</b>&ensp;%s</li>"
        % (n, _h.escape(t)) for n, t in f.get("chapters", ()))
    chap_html = ("<div class='nbtitle-facts-h' style='font-size:.74em;font-weight:800;"
                 "letter-spacing:2px;text-transform:uppercase;margin:16px 0 6px'>Chapters</div>"
                 "<ol class='nbtitle-chaps' style='list-style:none;text-align:left;margin:0 auto;"
                 "padding:0;max-width:420px;line-height:1.45;columns:2;column-gap:28px'>%s</ol>" % chaps
                 if chaps else "")
    return ("<div class='nbtitle-facts' style='max-width:640px;margin:20px auto 0;"
            "color:#5b6b7b;font-size:.95em'>%s%s"
            "<div class='nbtitle-time' style='margin-top:14px;font-weight:700;"
            "letter-spacing:.3px'>%s</div></div>" % (goals_html, chap_html, _h.escape(f["line"])))

def card_timeline():
    """E5.3 (2026-09-28, Struktur + Inhalt) — the whole timeline as plain data,
    walked in the SAME order and named with the SAME words as the panel's
    marks (_STRUCT + _TASKS): [(kind, name, task), …]; `task` is the exercise
    key for task/coding/quiz/byod rows, else "" (E8.21: the page's script
    reads it off the class to paint the reader's own progress). The cold
    cover draws its miniature from this, so the two cannot disagree."""
    rows = []
    for e in _STRUCT:
        k = e.get("kind")
        if k == "title":
            rows.append(("title", _NB_TITLE["text"] or e["title"], ""))
        elif k in ("group", "end", "cell"):
            rows.append((k, e["title"], ""))
        elif k == "chapter":
            rows.append(("chapter", "Chapter %s: %s" % (e["num"], e["title"]), ""))
        elif e.get("task") and not e.get("task_anchor"):
            pass                                   # K2.3: the task mark stands for it
        else:
            rows.append(("sub", e["title"], ""))
        if e.get("viz_anchor"):
            rows.append(("figure", ("Figure %s: %s" % (e["num"], e["figure"]))
                                   if e.get("figure") else "Figure %s" % e["num"], ""))
        t = e.get("task")
        if t:
            n = _answer_num(t)                                   # R3 · 18
            cn = _TASKS["order"].index(t) + 1 if t in _TASKS["order"] else "•"
            kind = {"q1": "quiz", "b1": "byod"}.get(t, "task") if not e.get("task_anchor") else "task"
            if t not in _TASKS["noanswer"]:
                rows.append((kind, ("Exercise %s: %s" % (n, _TASKS["name"][t]))
                                   if _TASKS["name"].get(t) else "Exercise %s" % n, t))
            if e.get("code_anchor"):
                rows.append(("coding", ("Coding %s: %s()" % (cn, _TASKS["cname"][t]))
                                       if _TASKS["cname"].get(t) else "Coding %s" % cn, t))
    return rows

# E14 (2026-10-02): the cover's miniature (card_timeline_html, _TL_MARK, _TL_W)
# moved to toolkit/card_facts.py — it only runs at build time, from the rows
# card_timeline() gives above. Contract and sanitiser notes live there.

def reset_progress():
    """Start over: every exercise open again, every chapter locked again.

    The browser record follows on the next panel refresh, so the series total and
    the timeline agree with what is on screen."""
    for k in _TASKS["order"]:
        _TASKS["state"][k] = "open"
        _TASKS["code"][k]  = "open"
        _TASKS["diff"].pop(k, None)
    _TASKS["skipped_open"].clear()
    for key, ent in _LOCKS.items():
        if ent.get("open") and ent.get("closed"):
            ent["shell"].children = ent["closed"]
            ent["open"] = False
            for _ta in ent.get("taccs", ()):      # K1: the fold waits again
                try: _ta.add_class("acc-tasklock")
                except Exception: pass
            pill = ent.get("pill")
            if pill:
                acc, label = pill
                try: acc.add_class("acc-locked")
                except Exception: pass
    # starting over means starting over: every chapter folded shut again —
    # and every PRACTICE fold with them (2026-09-24au). `pacc` was missing from
    # this list, so after a reset the written exercise of every chapter was
    # still standing open, which also made the code route look as if it opened
    # the written one.
    for acc in (list(_TASKS["acc"].values()) + list(_TASKS["cacc"].values())
                + list(_TASKS["pacc"].values())):
        try: acc.selected_index = None
        except Exception: pass
    # E4.3 (2026-09-28, Applikation + Struktur): after a reset the reader
    # stands at the top again — the panel reads route "top" off the feed
    _goto_next("", "top")
    _refresh_progress()
    return len(_TASKS["order"])

def _is_settled(key):
    """Has this exercise been answered correctly on EITHER route?"""
    return _TASKS["state"].get(key) == "done" or _TASKS["code"].get(key) == "done"

# 2026-09-27e — A RIGHT ANSWER MOVES THE READER ON (Applikation F, rule b).
# The exercise folds and the document goes to the next open place — by the
# SAME function a click on the timeline uses: the panel script clicks that
# mark. The kernel only says "this one was just solved, on this route"; which
# mark is next is read off the rail, where the reader sees it. `run` changes
# with every kernel run, so a panel that meets a feed for the first time (a
# new run, a restore, a reload) records the number and does not jump.
_GOTO = {"run": "%08x" % _random.getrandbits(32), "seq": 0, "key": "", "route": ""}

def _goto_next(key, route):
    _GOTO["seq"] += 1
    _GOTO["key"] = key or ""
    _GOTO["route"] = route

def task_solved(key):
    """Correct on the ANSWER route: fills the green bar and the lower half of the circle."""
    if key in _TASKS["state"]:
        _TASKS["state"][key] = "done"
    _mark_diff(key)
    _unlock_next(key, refresh=False)
    _goto_next(key, "a")
    _refresh_progress()

def task_code_solved(key):
    """Correct on the CODE route.

    2026-09-24ak — a right answer moves the reader on, whichever route it came
    from. It opens the next CHAPTER (that was the half this route used not to
    do, so a reader who works in code was left standing in front of a locked
    chapter they had earned) and the next CODING exercise. It deliberately does
    NOT open the next chapter's written exercise: the reader has chosen a route,
    and the other one is still there to be opened by hand."""
    _TASKS["code"][key] = "done"
    _mark_diff(key)
    _open_lock("chapter", key)          # the chapter this one was holding shut
    # 2026-09-24bf — a right answer is a right answer, whichever route it came
    # from, so the written exercise of that chapter is unlocked too. It is not
    # UNFOLDED (fold=False below): the reader chose the code route and keeps it.
    _open_lock("practice", key)
    _open_following(key, fold=False)    # …and put it in front of the reader
    _unlock_next_code(key, refresh=False)
    _goto_next(key, "c")
    _refresh_progress()

def _code_opens_chapter(key, unfold=True):
    """E8.7 (29.09., Applikation) — in mode "code" the written exercise is not
    built, so the CODING exercise holds the next chapter shut: answered right,
    wrong or skipped, it opens it (the answer route does this in _unlock_next).
    In the other modes the chapter waits for the written exercise as before."""
    if not builds_answer():
        _open_lock("chapter", key, unfold=unfold)

def task_code_skipped(key):
    """Come back to the code later: the next coding exercise opens, ⤼ is recorded."""
    moved = _TASKS["code"].get(key, "open") == "open"
    if moved:
        _TASKS["code"][key] = "skip"
    _mark_diff(key)
    _code_opens_chapter(key)
    _unlock_next_code(key)
    if moved:
        _goto_next(key, "c")           # 2026-09-28 (Paket 4): skip moves on
    _refresh_progress()

def task_code_bypassed(key):
    """Given up on the code: the next coding exercise opens, ✗ is recorded."""
    if _TASKS["code"].get(key, "open") in ("open", "skip"):
        _TASKS["code"][key] = "fail"
    _mark_diff(key)
    _code_opens_chapter(key, unfold=False)
    _unlock_next_code(key, refresh=False)
    _refresh_progress()

def task_wrong(key, route="answer"):
    """A WRONGLY ENTERED answer — the only thing that counts as giving up now
    (2026-09-24q).

    It marks the step red on the timeline and leaves it open: answer it correctly
    later and the same stretch turns green.

    2026-09-28a (K1) — and it OPENS the next task. Until 27h a wrong answer
    unlocked nothing ("not a way forward, the skip button is"); the rule now is
    that a task waits until the one before it is answered — right, wrong or
    skipped. Nothing is unfolded here; since Paket 4 (28.09.) the page moves
    on after the same pause as after a right answer (`_goto_next`).
    The restore always did this (it reopens after every settled state)."""
    if route == "code" and _TASKS["code"].get(key, "open") in ("open", "skip"):
        _code_opens_chapter(key, unfold=False)       # E8.7: mode "code"
    if route == "code":
        if _TASKS["code"].get(key, "open") in ("open", "skip"):
            _TASKS["code"][key] = "fail"
            _mark_diff(key)
            _open_lock("code", key)        # the next coding fold may open now
            # E8.3 — a wrong answer does NOT move on (replaces Paket 4)
            _refresh_progress()
        return
    if _TASKS["state"].get(key) in ("open", "skip"):
        _TASKS["state"][key] = "fail"
        _mark_diff(key)
        _unlock_next(key, unfold=False)
        # 2026-09-29 (E8.3, Applikation) — A WRONG ANSWER STAYS PUT again
        # (replaces Paket 4 "moves on too"): the reader reads the verdict and
        # tries again. Right answers and skips still move (`_goto_next`).
        _refresh_progress()

# 2026-09-28a (K1) — `unlock_chapter_only` is gone: it was the timeline's way
# past a lock (arm the mark, turn the key in the box, or the gear drawer). The
# only skip left is "Skip for now" at the exercise itself (`skip_button`).

def task_skipped(key):
    """Come back later: the next chapter and its exercise open, this one keeps ⤼.

    2026-09-28a (K1) — the only way to skip is the "Skip for now" button at the
    exercise itself (`skip_button`). A skip is an answer in the sense of the
    lock: the next task opens (24bf kept its exercise shut). It is still no
    credit: amber, not green (since Paket 4 it moves on, see below)."""
    moved = _TASKS["state"].get(key) == "open" and not _is_settled(key)
    if moved:
        _TASKS["state"][key] = "skip"
    _mark_diff(key)
    _unlock_next(key, fold=False)
    # 2026-09-28 (Paket 4, Applikation) — …and a skip moves on like a right
    # answer (replaces K1 "skip does not move"). A revealed solution is a skip
    # by another name but does NOT move: the reader is reading it.
    if moved:
        _goto_next(key, "a")
    _refresh_progress()

def task_bypassed(key):
    """Given up: the next CHAPTER opens and this one is marked ✗.

    2026-09-24bf — as with ⤼, the exercises inside stay locked until this one is
    answered correctly."""
    if _TASKS["state"].get(key) in ("open", "skip") and not _is_settled(key):
        _TASKS["state"][key] = "fail"
    _mark_diff(key)
    _unlock_next(key, fold=False, refresh=False)
    _refresh_progress()

def task_solution_opened(key):
    """Revealing the worked solution is a SKIP, not a wrong answer (2026-09-24q).
    Red is reserved for an answer that was actually entered and was wrong; reading
    the solution is coming back later by another name. An exercise that is already
    correct, or already marked wrong, is left alone."""
    if not _is_settled(key) and _TASKS["state"].get(key) == "open":
        _TASKS["state"][key] = "skip"
        _mark_diff(key)
        # 2026-09-28a (K1) — ⤼ is answered: the next task opens, nothing moves
        _unlock_next(key, unfold=False, refresh=False)
        _refresh_progress()

def _exercise_lock_shell(key, real):
    """The written exercise of a chapter, behind a lock of its own (2026-09-24bf).

    Deliberately NOT `_lock_shell`: that one stashes a second copy of the
    chapter's controls for the panel to borrow, and two boxes claiming the class
    `nbctl-unl-<key>` would leave the rail's key gesture pressing whichever it
    found first. This is a notice and nothing else — there is no way past it but
    the one it names, and that is the point of it. It carries no
    `nblocked-<key>` class either, so the rail never turns this padlock into a
    key.

    `("practice", key)` is the registry entry `_open_lock` already knows; only a
    correct answer to `key`, on either route, calls it."""
    lab = _TASKS["label"].get(key, key)
    note = HTML(layout=_w(), value=(
        '<div class="nblock nblocked-note nbexlock">'
        '<div class="nblocked-lock"></div>'
        '<div class="nblocked-head">The exercise is still locked</div>'
        '<div class="nblocked-say">It opens as soon as <b>%s</b> is answered '
        '— right, wrong or skipped with <b>Skip for now</b>.</div></div>' % lab))
    shell = VBox([center(note)], layout=Layout(width="100%"))
    _LOCKS[("practice", key)] = {"shell": shell, "real": real, "open": False,
                                 "closed": tuple(shell.children)}
    return shell

def _lock_shell(kind, key, real, title):
    """A chapter waits for the previous chapter's exercise.

    2026-09-28a (K1, Applikation) — THE LOCK HAS NO WAY PAST IT ANY MORE.
    Until 27h it carried two: "Skip it, open this chapter" (lent to the gear
    drawer and to a window at the top of the panel) and a hidden "open chapter
    only" that the timeline pressed when the reader armed the mark and turned
    the key in this box. The user decided (27.09.): skipping happens only at
    the exercise itself, by its "Skip for now" button. What is left here is the
    notice — what holds the chapter shut and how it opens."""
    lab = _TASKS["label"].get(key, key)
    what = "This chapter is locked" if kind == "chapter" else "This exercise is locked"
    note = HTML(layout=_w(), value=(
        '<div class="nblock nblocked-note nblocked-%s">'
        '<div class="nblocked-lock"></div>'
        '<div class="nblocked-head">%s</div>'
        '<div class="nblocked-say">It opens once <b>%s</b> is answered — right, '
        'wrong, or skipped with <b>Skip for now</b> at that exercise.</div></div>'
        % (key, what, lab)))
    shell = VBox([center(note)], layout=Layout(width="100%"))
    _LOCKS[(kind, key)] = {"shell": shell, "real": real, "open": False,
                           "closed": tuple(shell.children)}
    return shell

def skip_button(key, route="answer"):
    """SKIP FOR NOW — the one way to skip, at the exercise itself (2026-09-28a, K1).

    On the answer route it is `task_skipped`: amber on the timeline, and the
    next chapter and its exercise open. On the code route it is
    `task_code_skipped`: the next coding exercise opens. A settled exercise is
    left alone (both functions only turn an OPEN one amber)."""
    b = Button(description="\u293c  Skip for now",
               layout=Layout(width="auto", height="38px"))
    b.add_class("nbunlock")
    b.add_class("nbskipnow")
    out = HTML(layout=_w(), value="")
    def _go(_b, k=key):
        if route == "code":
            task_code_skipped(k)
            st = _TASKS["code"].get(k)
        else:
            task_skipped(k)
            st = _TASKS["state"].get(k)
        # E17.1 — whole sentences, so each language can order its own words
        if st == "skip" and route == "code":
            say = ("Skipped \u2014 the next coding exercise is open. This one stays amber "
                   "until you come back and get it right.")
        elif st == "skip":
            say = ("Skipped \u2014 the next chapter and its exercise are open. This one "
                   "stays amber until you come back and get it right.")
        elif st == "fail" and route == "code":
            say = ("This one is marked wrong, and the next coding exercise is open "
                   "already. Get it right and it turns green.")
        elif st == "fail":
            say = ("This one is marked wrong, and the next chapter and its exercise are "
                   "open already. Get it right and it turns green.")
        else:
            say = "Already solved \u2014 nothing to skip."
        out.value = ("<div class='nbink' style='text-align:center;font-size:.88em'>%s</div>"
                     % say)
    b.on_click(_go)
    box = VBox([center(b), center(out)], layout=Layout(width="100%"))
    box.add_class("nbskipbox")
    return box

# ---------- (3) frame player ------------------------------------------
def frame_player(frames, labels=None, description="step", width="520px", n=None):
    """Step through PRE-RENDERED frames with a slider.

    Pyodide redraws a matplotlib figure far too slowly for a smooth animation,
    so the frames are rendered once and only swapped here. Returns a list of
    widgets, ready to hand to build_chapter(viz=[…]).

    Paket 21b (2026-09-29): `frames` may also be a function k -> html with `n`
    frames. Then all n are rendered in one go when the chapter opens (_defer),
    not at start — still before the first slide, so the player stays smooth."""
    if callable(frames):
        make, count, frames = frames, int(n), []
    else:
        make, count = None, len(frames)
    view = HTML(layout=_w(), value=(frames[0] if frames else ""))
    cap  = HTML(layout=_w(), value=(labels[0] if labels else ""))
    sl   = IntSlider(value=0, min=0, max=count - 1, step=1,
                     description=description, continuous_update=True,
                     layout=Layout(width=width))
    def _upd(*_):
        i = sl.value
        if i < len(frames):
            view.value = frames[i]
        if labels:
            cap.value = labels[i]
    if make is not None:
        def _draw():
            if not frames:
                frames.extend(make(k) for k in range(count))
            _upd()
        _defer(_draw)
    sl.observe(_upd, "value")
    return [sl, cap, view]


# ======================================================================
# ANSWER WIDGETS — solving an exercise must not require Python
#   numeric_answer  · choice_answer · target_exercise · code_fold
# Every one of them reports to the same task/lock system as
# editable_exercise, so a chapter unlocks whichever route was taken.
# ======================================================================
def _feedback(out, ok, tip, extra=None):
    """The three-line status block shared by every answer widget."""
    out.clear_output(wait=True)
    def line(txt, cls, weight="400", size="1em"):
        display(IHTML('<div class="%s" style="text-align:center;font-weight:%s;font-size:%s;'
                      'margin:3px 0">%s</div>' % (cls, weight, size, txt)))
    with out:
        if ok:
            line("✓ correct, well done!", "nbok", "700", "1.14em")
        else:
            line("Not there yet, keep going.", "nbwarn", "700", "1.1em")
        if tip and (ok or hints_on()):
            line(tip, "nbink")
        elif tip:
            line("Check the formula in the box above, then try again.", "nbink")
        if extra:
            line(extra, "nberr", "600")

def _check_button(label="🔍  Check answer", width="240px"):
    b = Button(description=label, layout=Layout(width=width, height="42px"))
    try: b.style.button_color = "#e6b52a"; b.style.text_color = "#ffffff"; b.style.font_weight = "800"
    except Exception: pass
    b.add_class("sc-btn")
    return b

# 2026-09-28 (R1 · Paket 12) — the Complex answers are whole numbers now, or
# need π and √2 at most; "a square root is almost never a whole number" said
# the opposite of what the exercise above it says.
_DEC_NOTE = ("Enter <b>decimals</b>, not fractions or roots (for example 1.414, not √2, and 0.5, "
             "not 1/2). The check allows a small tolerance.")

def numeric_answer(fields, check, task=None, columns=2, note=_DEC_NOTE, answer=None):
    """Type the numbers, no code.

    fields : [(key, label)] — one number box each, laid out in `columns` columns.
    check  : check({key: float, …}) -> (ok, tip). Compare with a tolerance; the
             students are working with a calculator, not with exact arithmetic.
    """
    boxes, rows, row = {}, [], []
    # E16.8 (2026-10-02, Applikation) — THE NUMBER IS TAKEN WHILE IT IS TYPED.
    # FloatText sends its value only on Enter or when it loses the focus
    # (continuous_update=False is its default); a Check pressed without either
    # — a script click, a key binding — judged the number before the one in
    # the box (measured, tests/lab_inputs.py C). Live, every keystroke that
    # makes a number is sent; "-", "1.", "" in between are skipped by the
    # front end (ipywidgets 8) and never reach check().
    # E22.2 (2026-10-04, Applikation) — A COMMA IS A DECIMAL POINT. FloatText is
    # an <input type=number>: Chromium drops the comma of "2,5" as it is typed
    # and the kernel gets 25 — in every locale, silently (measured, real Lab,
    # en-US and de-DE: "2,5" → 25.0, "-1,25" → -125.0). A German reader types
    # 2,5. The box is a text box now; the kernel reads it (_parse_num: 2.5 and
    # 2,5, a minus sign, blanks). What is no number yet ("", "-", "1,") is
    # never judged: Check says so instead of judging a number the reader did
    # not mean. Still sent on every keystroke (E16.8).
    for k, lab in fields:
        ft = Text(value="0", description=lab, layout=Layout(width="230px"),
                  style={"description_width": "initial"}, continuous_update=True)
        ft.add_class("nbnum")
        boxes[k] = ft
        row.append(ft)
        if len(row) == columns:
            rows.append(HBox(row, layout=Layout(justify_content="center"))); row = []
    if row:
        rows.append(HBox(row, layout=Layout(justify_content="center")))
    hint = HTML(layout=_w(), value=(
        "<div class='nbink' style='text-align:center;font-size:.90em;max-width:640px;"
        "margin:2px auto 8px;opacity:.9'>%s</div>" % note)) if note else None
    out = Output(layout=Layout(width="96%", max_width="780px"))
    btn = _check_button()
    def _run(_):
        vals = {k: _parse_num(w.value) for k, w in boxes.items()}
        if any(v is None for v in vals.values()):
            bad = [boxes[k].description.strip() for k, v in vals.items() if v is None]
            _feedback(out, False, "Enter a number in every box, for example 2.5 (%s)." % ", ".join(bad))
            return
        try:
            ok, tip = check(vals)
        except Exception as e:
            _feedback(out, False, "Could not check that input.", "⚠ %r" % (e,)); return
        if task:
            (task_solved if ok else task_wrong)(task)
        _feedback(out, ok, tip)
    btn.on_click(_run)
    def _clear(_b=boxes, _o=out):               # R2 · 13: new numbers, empty boxes
        for w in _b.values(): w.value = "0"
        _o.clear_output()
    _RESEED["clear"].append(_clear)
    kids = ([center(hint)] if hint else []) + [center(r) for r in rows]
    box = VBox(kids + [center(btn), center(out)], layout=Layout(width="100%"))
    # E26 Teil 2: answer = {field: value | (value, tolerance[, period])} or a
    # function returning it (asked at the end of the run, the reader's seed);
    # tolerance None = tol(). The reading window checks with it (_nbrw_calc).
    if answer is not None:
        _nbrw_reg(box, "calc", task=task, fields=list(fields), answer=answer, check=check)
    return box

def choice_answer(prompt, options, check, task=None, answer=None):
    """Pick one option, no code. check(index, label) -> (ok, tip).
    `prompt` may be a function: it is then asked again after a reseed (R2 · 13)."""
    _head = lambda: HTML(layout=_w(), value=(
        "<div style='text-align:center;font-weight:700;margin:2px 0 8px'>%s</div>"
        % (prompt() if callable(prompt) else prompt)))
    head = personal(_head) if callable(prompt) else _head()
    rb = RadioButtons(options=list(options), value=None, layout=Layout(width="560px"),
                      style={"description_width": "initial"})
    out = Output(layout=Layout(width="96%", max_width="780px"))
    btn = _check_button()
    def _run(_):
        if rb.value is None:
            _feedback(out, False, "Pick one of the options first."); return
        idx = list(options).index(rb.value)
        try:
            ok, tip = check(idx, rb.value)
        except Exception as e:
            _feedback(out, False, "Could not check that choice.", "⚠ %r" % (e,)); return
        if task:
            (task_solved if ok else task_wrong)(task)
        _feedback(out, ok, tip)
    btn.on_click(_run)
    def _clear(_r=rb, _o=out):
        _r.value = None; _o.clear_output()
    _RESEED["clear"].append(_clear)
    box = VBox([center(head), center(rb), center(btn), center(out)], layout=Layout(width="100%"))
    if answer is not None:                   # E26 Teil 2: the index of the right option
        _nbrw_reg(rb, "choice", task=task, options=list(options), answer=answer, check=check)
        _nbrw_reg(btn, "skip")
    return box

def target_exercise(render_fn, sliders, check, task=None, readout_fn=None,
                    dpi=100, label="🎯  Check position", answer=None):
    """Hit a target by moving the sliders — the picture IS the exercise.

    check({slider values}) -> (ok, tip). Nothing is typed and nothing is coded;
    what is assessed is the state the student steered the system into.
    """
    kids = slider_plot(render_fn, sliders, readout_fn=readout_fn, dpi=dpi, frames=False)
    out = Output(layout=Layout(width="96%", max_width="780px"))
    btn = _check_button(label, width="260px")
    # E26 Teil 2: in the reading window the target is typed: one field per
    # slider (answer = {slider: (value, tolerance[, period])})
    if answer is not None:
        _nbrw_reg(btn, "calc", task=task, answer=answer, check=check,
                  fields=[(k, (getattr(w, "description", "") or k) + " =") for k, w in sliders.items()])
    def _run(_):
        vals = {k: w.value for k, w in sliders.items()}
        try:
            ok, tip = check(vals)
        except Exception as e:
            _feedback(out, False, "Could not check that position.", "⚠ %r" % (e,)); return
        if task:
            (task_solved if ok else task_wrong)(task)
        _feedback(out, ok, tip)
    btn.on_click(_run)
    _RESEED["clear"].append(out.clear_output)
    return kids + [btn, out]

def code_fold(stub, check_fn, task=None, solution=None,
              title="💻  Optional: write it in code", locked_by=None, task_text=None):
    """The optional second route, and its own progression.

    `locked_by` names the CODING exercise this one waits for. That chain runs
    beside the chapter chain and never blocks it: a reader who writes no Python
    gets through the notebook untouched, and a reader who does has a second
    ladder of their own, drawn in purple on the timeline (2026-09-24n)."""
    if not builds_code():
        return None                          # R3 · 18, mode "calc": not built
    if MODE["value"] == "code" and title.startswith("💻  Optional: "):
        title = "💻  Write it in code"          # R3 · 18: not optional here
    if task:
        _TASKS["has_code"][task] = True      # this task counts in the purple lane
        # the function the reader writes names the mark: "Coding 3: add_sub()"
        # — read from the stub itself, so there is no second place to keep it
        _m = _re.search(r"^\s*def\s+([A-Za-z_]\w*)\s*\(", stub or "", _re.M)
        if _m:
            _TASKS["cname"][task] = _m.group(1)
        _refresh_progress()
    kids = [editable_exercise(stub, check_fn, task=task, route="code")]
    if task:                                 # E26 Teil 2: pruefe("t1") in a cell of your own
        _PRUEFE[task] = check_fn
        _nbrw_reg(kids[0], "code", task=task, stub=stub, solution=solution)
    # E8.22 (2026-09-29, Inhalt) — THE CODING EXERCISE SAYS WHAT TO WRITE.
    # Until now the fold opened on the stub alone, and the task had to be read
    # off a comment. `task_text` (2–3 sentences: what the function does, input
    # and output, one example) stands above the code, in the exercise box.
    if task_text:
        _tb = exercise_box("", task_text)
        _tb.add_class("nbcode-task")
        kids.insert(0, _tb)
    if task:
        kids.append(skip_button(task, route="code"))     # K1: skip HERE, nowhere else
    if solution:
        kids.append(solution_box("", solution, task=task, route="code"))
    body = VBox([center(c) for c in kids], layout=Layout(width="100%"))
    if locked_by:
        body = _code_lock_shell(locked_by, body)
        if task:
            _TASKS["cguard"][task] = locked_by
    acc = _acc([body], title, "acc-code", open_=False)
    if locked_by:
        _task_lock(("code", locked_by), acc)             # K1.2: does not unfold while locked
    if task:
        _TASKS["cacc"][task] = acc
        # A MARK OF ITS OWN ON THE TIMELINE (2026-09-24q).
        # The anchor sits immediately before the fold, so the rail finds the
        # fold's own pill and puts the purple mark on its line — the same
        # mechanism the chapters use, and it disappears with the chapter when
        # that is folded shut.
        _wrap = VBox([HTML(layout=Layout(height="0px", margin="0px"),
                           value=_anchor_html("code_%s" % task)),
                      acc], layout=Layout(width="100%"))
        # build_chapter looks for this to lift the fold out of the practice list
        _wrap.add_class("nbcodefold")
        return _wrap
    try: acc.add_class("nbcodefold")
    except Exception: pass
    return acc

def _code_lock_shell(key, real):
    """The code chain's own waiting room — the same two honest ways past it as the
    chapter lock, but wired to the code chain so nothing here touches a chapter."""
    lab = _TASKS["label"].get(key, key)
    panel = HTML(layout=_w(), value=(
        '<div class="nblock nblock-code">'
        # 2026-09-25c — the padlock is gone from here too. It said the same
        # thing as the heading right under it, and a colour emoji is the one
        # picture on the page that no skin can reach. The laptop stays: that
        # one says WHICH route is waiting, which the text does not.
        '<div style="font-size:1.4em;line-height:1">\U0001F4BB</div>'
        '<div style="font-weight:800;margin:8px 0 4px">The coding route is one step behind</div>'
        '<div style="max-width:560px;margin:0 auto;line-height:1.55">'
        'This one opens once the coding exercise in <b>%s</b> is answered — '
        'right, wrong, or skipped with <b>Skip for now</b>. '
        'It is a separate ladder: the chapters themselves are <b>not</b> waiting '
        'for it, so you can read on at any time.</div></div>' % lab))
    # 2026-09-28a (K1) — no skip button here any more: the fold this shell is in
    # does not even open while it waits (_task_lock), and skipping happens at
    # the coding exercise before, by its own "Skip for now".
    shell = VBox([center(panel)], layout=Layout(width="100%"))
    _LOCKS[("code", key)] = {"shell": shell, "real": real, "open": False,
                             "closed": tuple(shell.children)}
    return shell
