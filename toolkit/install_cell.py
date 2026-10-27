# DigiChemJN · No document? ▶ Play / Run All draws it · Kein Dokument? ▶ Play / Run All zeigt es an
# Output: at the very end, below this code (Ctrl+End) · Ausgabe: ganz unten, unter diesem Code (Strg+Ende) · no output? run it again, progress is kept.
#
# E26.1b (2026-10-11, Python) — LINE 2 SAYS WHERE THE OUTPUT IS. PyCharm ignores
# `source_hidden` and shows all ~2 900 lines of this cell above its output
# (measured 11.10., v1.70). Until E20.2 (slim cell + package) the second line,
# the only other one the build keeps, points the reader down (en/de).
#
# E23.0 (2026-10-06, Applikation) — THE FIRST LINE IS THE LAST WORD. Where the
# output is gone (JupyterLab "Clear All Outputs", a copy saved without outputs,
# another front end) the reader sees exactly this line — JupyterLab, Notebook 7,
# JupyterLite and VS Code show a hidden cell's first line, Colab shows it as the
# form's title (#@title). It used to say what the cell does ("Setup, installs
# packages …"); it now says what to do, in both languages. Measured after
# Clear All Outputs (test_regress py_e23_0): the title cell stays out of the
# flow, this line is all that is left.
#
# 2026-09-24be — ONE FILE, EVERY KERNEL.
# Rule 1 of this project is that a single .ipynb runs in JupyterLab, in
# JupyterLite (jupyter.org/try-jupyter), in Colab and in Binder. It did not:
# the installer knew only `%pip`, and in JupyterLite that magic answers
# "Not available" — after which the first import of ipywidgets ended the
# notebook with a red traceback, three lines under the Play button. MEASURED
# there; a local JupyterLab never showed it, which is why it survived so long.
#
# Pyodide installs with `piplite`, and `piplite.install` is a COROUTINE: it
# needs a top-level `await`, which this file may not contain — a bare await
# makes it invalid ordinary Python, and every other kernel, and every test,
# stops compiling it. The way through is a nested cell: IPython compiles what
# it is handed with top-level await enabled, so the await lives inside a
# string and this file stays plain.
#
# One package at a time, on purpose. A single install call with four names
# fails as a whole if one wheel is missing from the Lite index, and the reader
# would lose numpy over jupyterquiz.
# E24.1 (2026-10-06, Applikation) — THE CELL BRINGS WHAT IT NEEDS, AND SAYS SO.
# Measured on a stranger's machine (tests/regress/cold.py, a venv with
# jupyterlab only): the install below worked, but in silence — the reader
# watched a loading view for ~90 s and then nothing. Now:
#  * a status line, en and de, fixed above the loading view while pip runs
#    ("Installing … once, about 30 s"), gone when it is done;
#  * after pip the import system is told about the new files (finder caches,
#    and a user site that did not exist when the kernel started — pip falls
#    back to `--user` where site-packages is not writable);
#  * pip gets one retry and a short timeout: without a network it says so in
#    seconds, not minutes;
#  * what still cannot be imported ends the run with one plain box (en/de:
#    what is missing, probably no internet, what to do) and NO traceback —
#    the cell stops through an exception IPython is told to keep quiet about.
# `subprocess` is not used: it does not exist in Pyodide, and %pip installs
# into the kernel's own environment wherever there is one (Lab, Notebook 7,
# VS Code, Colab). In JupyterLite the installs are coroutines (see above);
# when they have not finished inside this run, the box says: run it again.
_NB_NEED = ["numpy", "matplotlib", "ipywidgets", "jupyterquiz"]
_NB_SOFT = ["jupyterquiz"]          # nice to have; the quiz says so itself if absent
_NB_FRESH = []                      # what this run installed (E24.2 reads it)


def _nb_gone(names):
    try:
        import importlib as _il
        _il.invalidate_caches()
    except Exception:
        pass
    out = []
    for _m in names:
        try:
            __import__(_m)
        except Exception:
            out.append(_m)
    return out


_nb_st = []


def _nb_status(html):
    try:
        from IPython.display import display as _d, HTML as _H
        if _nb_st:
            _nb_st[0].update(_H(html))
        else:
            _nb_st.append(_d(_H(html), display_id=True))
    except Exception:
        pass


_NB_BOX = ('<div class="nbboot" style="position:fixed;left:50%%;bottom:30px;transform:translateX(-50%%);'
           'z-index:10070;max-width:min(680px,92vw);padding:10px 20px;border-radius:12px;'
           'background:%s;color:#fff;font:600 14px/1.5 system-ui,sans-serif;text-align:center;'
           'box-shadow:0 6px 24px rgba(0,0,0,.28)">%s</div>')


def _nb_bring(pkgs):
    miss = _nb_gone(pkgs)
    if not miss:
        return []
    _nb_status(_NB_BOX % ("#2c6e91",
        '&#9203; Installing %s &mdash; once, about 30 s<br>'
        '<span lang="de">Installiere %s &mdash; einmalig, ca. 30 s</span>' % (", ".join(miss), ", ".join(miss))))
    try:
        from IPython import get_ipython as _gi
        _ip = _gi()
    except Exception:
        _ip = None
    # --- JupyterLite / Pyodide ------------------------------------------
    try:
        import piplite                       # exists only in JupyterLite
        for _m in list(miss):
            try:
                if _ip is not None:
                    _ip.run_cell("import piplite\nawait piplite.install(%r)" % (_m,))
                else:
                    import asyncio
                    asyncio.get_event_loop().run_until_complete(piplite.install(_m))
            except Exception:
                pass
    except ImportError:
        pass
    except Exception:
        pass
    left = _nb_gone(miss)
    if left:
        # --- bare Pyodide, without JupyterLite's wrapper ------------------
        try:
            import micropip                  # noqa: F401
            if _ip is not None:
                for _m in list(left):
                    try:
                        _ip.run_cell("import micropip\nawait micropip.install(%r)" % (_m,))
                    except Exception:
                        pass
        except ImportError:
            pass
        except Exception:
            pass
        left = _nb_gone(left)
    if left and _ip is not None and "pyodide" not in __import__("sys").modules:
        # --- an ordinary kernel: %pip, quietly ----------------------------
        # pip's own chatter ("you may need to restart the kernel") is
        # captured; what it means for the reader is said below, in our words.
        _arg = "install -q --disable-pip-version-check --retries 1 --timeout 15 " + " ".join(left)
        try:
            from IPython.utils.capture import capture_output as _cap
            with _cap():
                _ip.run_line_magic("pip", _arg)
        except Exception:
            try:
                _ip.run_line_magic("pip", _arg)
            except Exception:
                pass
        try:
            import site as _site, sys as _sys
            _u = _site.getusersitepackages()
            if _site.ENABLE_USER_SITE and _u not in _sys.path and __import__("os").path.isdir(_u):
                _site.addsitedir(_u)
        except Exception:
            pass
        left = _nb_gone(left)
    _NB_FRESH.extend(m for m in miss if m not in left)
    _nb_status("")
    return left


class _NBStop(Exception):
    """Ends the cell after our own message; IPython prints nothing for it."""


def _nb_stop():
    try:
        from IPython import get_ipython as _gi
        _ip = _gi()
        if _ip is not None:
            _ip.set_custom_exc((_NBStop,), lambda *a, **k: [])
    except Exception:
        pass
    raise _NBStop()


# E25.v (2026-10-08, Python) — VERSIONS, CHECKED AND SAID. Nutzer 08.10.: an
# old venv (Python 3.9) could not even start the server; "kann eine zu alte
# Version auch woanders vorkommen?" The kernel side is checked here, before
# anything is installed, and said in our words (en/de) with the way — never a
# traceback, never silence. Measured (tests/regress/py_e25_v.py, kernels of
# their own): the cell runs on Python 3.9 and 3.10 with today's packages.
#   Python < 3.9            stop: not supported (untested; numpy/matplotlib of
#                           today need ≥ 3.9) — a new environment, the way
#   Python 3.9              a note, the run goes on: out of support since
#                           10/2025, newer packages need ≥ 3.10
#   ipywidgets < 8          a note, the run goes on: the document is built for
#                           ipywidgets 8 (JupyterLab 4 / Notebook 7), the way
# The front end (JupyterLab/Notebook version, the widget front end, the
# browser) is the page's to check (JS E25 Versionsprüfung). _NB_VERSIONS is
# what was found, for the feedback e-mail and the page.
_NB_MIN_PY, _NB_OK_PY = (3, 9), (3, 10)
_NB_VERSIONS = {"python": "%d.%d.%d" % tuple(__import__("sys").version_info[:3])}


def _nb_say(cls, colour, title_en, text_en, title_de, text_de, fixed=True):
    try:
        from IPython.display import display as _d, HTML as _H
        _d(_H('<div class="%s" style="%sz-index:10070;width:min(720px,92vw);box-sizing:border-box;'
              'padding:14px 22px;border:2px solid %s;border-radius:12px;text-align:center;background:#fffaf0;'
              'color:#33475b;font:14px/1.6 system-ui,sans-serif;box-shadow:0 8px 28px rgba(0,0,0,.18);margin:8px auto">'
              '%s<div style="font-weight:800">%s</div><div>%s</div>'
              '<div lang="de" style="margin-top:8px;font-weight:800">%s</div><div lang="de">%s</div></div>'
              % (cls, "position:fixed;left:50%;top:96px;transform:translateX(-50%);" if fixed else "",
                 colour, "<style>#nbload{display:none!important}</style>" if fixed else "",
                 title_en, text_en, title_de, text_de)))
    except Exception:
        print(title_en, "/", title_de)


_nb_pyv = tuple(__import__("sys").version_info[:2])
if _nb_pyv < _NB_MIN_PY:
    _nb_say("nbboot-old nbboot-fail", "#c0392b",
            "This notebook needs Python 3.10 or newer &mdash; this kernel runs Python %d.%d." % _nb_pyv,
            "Make a new environment with a current Python (3.12 is a good choice): "
            "<code>python3.12 -m venv dcj</code>, activate it, <code>pip install jupyterlab</code>, "
            "start <code>jupyter lab</code> from there and open the notebook again. Or open it in JupyterLite.",
            "Dieses Notebook braucht Python 3.10 oder neuer &mdash; dieser Kernel l&auml;uft mit Python %d.%d." % _nb_pyv,
            "Legen Sie eine neue Umgebung mit aktuellem Python an (3.12 ist eine gute Wahl): "
            "<code>python3.12 -m venv dcj</code>, aktivieren, <code>pip install jupyterlab</code>, "
            "von dort <code>jupyter lab</code> starten und das Notebook erneut &ouml;ffnen. Oder in JupyterLite &ouml;ffnen.")
    _nb_stop()
elif _nb_pyv < _NB_OK_PY:
    # E33 A3 (2026-10-13, Python; Nutzer 13.10.: the box "Python 3.9 is out of
    # support" stood in Lab 3.9 and in PyCharm, above the document). No box any
    # more: ONE line on the kernel's own console (the terminal that started
    # Jupyter / the IDE's log) — nothing in the notebook. tests/regress/py_e33.py A3.
    try:
        __import__("sys").__stderr__.write("DigiChemJN: Python %d.%d is out of support - the notebook runs; "
                                           "3.10 or newer recommended.\n" % _nb_pyv)
    except Exception:
        pass

_NB_MISSING = [m for m in _nb_bring(_NB_NEED) if m not in _NB_SOFT]
if _NB_MISSING:
    # Say it once, in our own words, and stop: a traceback under a title page
    # is the worst first impression this notebook can make.
    _nb_lite = "pyodide" in __import__("sys").modules
    _nb_m = ", ".join(_NB_MISSING)
    try:
        from IPython.display import display as _d, HTML as _H
        _d(_H('<div class="nbboot-fail" style="position:fixed;left:50%;top:96px;transform:translateX(-50%);'
              'z-index:10070;width:min(720px,92vw);box-sizing:border-box;padding:18px 24px;'
              'border:2px solid #c0392b;border-radius:12px;text-align:center;background:#fff8f6;color:#33475b;'
              'font:14px/1.6 system-ui,sans-serif;box-shadow:0 8px 28px rgba(0,0,0,.25)">'
              '<style>.jp-OutputArea-output[data-mime-type="application/vnd.jupyter.stderr"]:not(:has(*:not(:empty))):empty,'
              '.jp-OutputArea-child:has(>.jp-OutputArea-output[data-mime-type="application/vnd.jupyter.stderr"]>pre:empty){display:none!important}</style>'
              '<style>#nbload{display:none!important}</style>'
              '<div style="font-size:1.5em;line-height:1">&#9888;&#65039;</div>'
              + ('<div style="font-weight:800;margin:8px 0 6px">Still loading: ' + _nb_m + '</div>'
                 '<div>JupyterLite fetches packages in the background. Wait a few seconds, then run '
                 'it again: <i>Run &#9656; Run All Cells</i>.</div>'
                 '<div lang="de" style="margin-top:10px;font-weight:800">Wird noch geladen: ' + _nb_m + '</div>'
                 '<div lang="de">JupyterLite l&auml;dt Pakete im Hintergrund. Warten Sie einige Sekunden und '
                 'f&uuml;hren Sie dann erneut aus: <i>Run &#9656; Run All Cells</i>.</div>'
                 if _nb_lite else
                 '<div style="font-weight:800;margin:8px 0 6px">Could not install: ' + _nb_m + '</div>'
                 '<div>Most likely there is no internet connection (or pip is blocked here). Connect, then '
                 'run it again: <i>Run &#9656; Run All Cells</i> &mdash; it installs once. Or open the '
                 'notebook where these packages are already there.</div>'
                 '<div lang="de" style="margin-top:10px;font-weight:800">Konnte nicht installieren: ' + _nb_m + '</div>'
                 '<div lang="de">Wahrscheinlich besteht keine Internetverbindung (oder pip ist hier gesperrt). '
                 'Verbinden Sie sich und f&uuml;hren Sie erneut aus: <i>Run &#9656; Run All Cells</i> &mdash; '
                 'installiert wird nur einmal. Oder &ouml;ffnen Sie das Notebook dort, wo diese Pakete schon '
                 'vorhanden sind.</div>')
              + '</div>'))
    except Exception:
        print("Could not install / Konnte nicht installieren:", _nb_m)
    _nb_stop()

try:                                                    # E25.v
    import ipywidgets as _nb_w
    _NB_VERSIONS["ipywidgets"] = _nb_w.__version__
    if int(_nb_w.__version__.split(".")[0]) < 8:
        _nb_say("nbboot-old", "#c9a227",
                "ipywidgets %s is too old for this notebook (it is built for ipywidgets 8)." % _nb_w.__version__,
                "Run <code>%pip install -U \"ipywidgets>=8\"</code> in a cell, then <i>Kernel &#9656; Restart</i>, "
                "reload the page and <i>Run &#9656; Run All Cells</i>. Where JupyterLab itself runs, "
                "<code>pip install -U jupyterlab_widgets</code> as well.",
                "ipywidgets %s ist f&uuml;r dieses Notebook zu alt (es ist f&uuml;r ipywidgets 8 gebaut)." % _nb_w.__version__,
                "F&uuml;hren Sie in einer Zelle <code>%pip install -U \"ipywidgets>=8\"</code> aus, dann "
                "<i>Kernel &#9656; Restart</i>, die Seite neu laden und <i>Run &#9656; Run All Cells</i>. Dort, wo "
                "JupyterLab l&auml;uft, au&szlig;erdem <code>pip install -U jupyterlab_widgets</code>.", fixed=False)
except Exception:
    pass
