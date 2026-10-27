"""E38 P3 (2026-10-27, Python) — WHAT THE NOTEBOOK'S CELL RUNS: THE PACKAGE, NOT A NEW BUILD.

This file is not imported. The build (toolkit/paketzelle.py) puts it into the cell's package (_NBP, zlib +
base64), after the data of the build (_NBP_DATA), and the cell runs it in its own globals. Python 3.8+, the
standard library and IPython only — no numpy, no matplotlib, no ipywidgets: Run All shows the document as
soon as the kernel answers (Dirigent 27.10.: "Run All → Deckblatt 6,1–6,4 s" in Lab, lesen.html 0,6 s).

  _nbp_main(g)       DIGICHEM_LAB=1 → the Lab document as before (the cargo _NBZ, built in the kernel: the build
                     itself, py_e36 R1, the suites of the Lab). Otherwise: the language (DIGICHEM_LANG, the stored
                     choice ~/.digichemjn/<id>.lang and beside the notebook — the newer wins, as notebook_lang();
                     else the build's), ONE output = the reading version of the build in that language, put back
                     together from its skeleton and the hull blocks (<style>/<script> of the kernel's output, the
                     same for both languages) — character for character what the kernel of the build showed —
                     with the package data as its first child (<script type=application/json data-nbrw-daten>,
                     daten.json — claude/VERTRAG-E38-js.md), then the fonts of the hull (@font-face, data: URLs)
                     and, on a notebook page, the frame.
  pruefe(key, *fns)  the check of a coding exercise in the kernel, from the package (daten code[].pruef / pruef_code
                     — the same text the window runs in Pyodide); the result goes to the window as in the Lab
                     (localStorage digichemjn.<id>.reader.code.<key>).
  show(id, lang)     the document once more (the package of THIS notebook; B: import digichemjn; show(id)).
  _nbp_live(nr, **values) the picture of slider nr at any value (daten regler[].live, E38 P4), where the package has it.
The trust model stays: the saved file carries the still preview only; the script comes with the run."""


def _nbp_lang(d):
    import os
    v = (os.environ.get("DIGICHEM_LANG") or "").strip().lower()
    if v in ("en", "de"):
        return v
    i = d.get("id") or ""
    have = []
    try:
        import sys
        pyo = "pyodide" in sys.modules or sys.platform == "emscripten"
    except Exception:
        pyo = False
    if pyo:
        try:
            import js
            s = str(js.localStorage.getItem("digichemjn.lang." + i) or "").strip().lower()
            if s in ("en", "de"):
                return s
        except Exception:
            pass
    for q in (os.path.join(os.path.expanduser("~"), ".digichemjn", i + ".lang"),
              os.path.join(os.getcwd(), ".digichemjn", i + ".lang")):
        try:
            if os.path.isfile(q):
                have.append((os.path.getmtime(q), open(q).read().strip().lower()))
        except Exception:
            pass
    have = [x for x in have if x[1] in ("en", "de")]
    if have:
        return max(have)[1]
    return d.get("lang") or "en"


def _nbp_html(d, lang):
    import json, re
    sk = d["doc"].get(lang) or d["doc"]["en"]
    blocks = d["blocks"]
    doc = re.sub("\x00(\\d+)\x00", lambda m: blocks[int(m.group(1))], sk)
    # the output STARTS with the reading version, as the kernel's did (viewers and suites look for it there); the
    # package data go INSIDE it, first child (claude/VERTRAG-E38-js.md: the reader reads
    # .nbreading > script[type=application/json][data-nbrw-daten] where no loader gave window.DIGICHEMJN.daten);
    # the fonts follow it
    if d.get("daten") is not None:
        js = json.dumps(d["daten"], ensure_ascii=False, separators=(",", ":"))
        js = js.replace("</", "<\\/")
        i = doc.find(">", doc.find("<div class='nbreading'")) + 1
        doc = doc[:i] + "<script type='application/json' data-nbrw-daten='%s'>%s</script>" % (d["id"], js) + doc[i:]
    tail = "<style data-digichemjn-fonts>%s</style>" % d["fonts_css"] if d.get("fonts_css") else ""
    return doc + tail + _NBP_RAHMEN


# On a notebook page (JupyterLab, Notebook 7, Lite: the output sits in .jp-NotebookPanel; classic: #notebook — not
# nbconvert's static page, whose .jp-Notebook keeps the plain reading version as before) 20-reader.js does not
# start (hosted(): there the Lab document was the interface). The package has no Lab document: this stand-in puts
# the same output into a page of its own (iframe srcdoc, same origin: the same localStorage, pruefe() reaches it)
# — where VS Code, PyCharm, Colab put every output anyway — and the reader starts there as in lesen.html. The
# frame is as tall as its page. Without a run (saved file, not trusted) nothing of this runs: the reading version
# stands as plain HTML, as before. (For JS: once the reader starts by itself next to a package output — e.g.
# .nbreading[data-nbrw-paket] — this goes.)
_NBP_RAHMEN = (
    "<script data-digichemjn-rahmen>(function(){var me=document.currentScript;if(!me)return;var box=me.parentNode;"
    "if(!box||!box.closest||!box.closest('.jp-NotebookPanel,#notebook'))return;"
    "var rd=box.querySelector('.nbreading');if(!rd||rd.getAttribute('data-nbrw')||box.querySelector('iframe[data-digichemjn-rahmen]'))return;"
    "var c=box.cloneNode(true),s=c.querySelectorAll('script[data-digichemjn-rahmen]');"
    "for(var i=0;i<s.length;i++)s[i].parentNode.removeChild(s[i]);"
    "var f=document.createElement('iframe');f.setAttribute('data-digichemjn-rahmen','1');f.setAttribute('title','DigiChemJN');"
    "var h0=0;try{h0=(screen.availHeight||screen.height||900)-200}catch(e){h0=700}"
    "f.style.cssText='display:block;width:100%;border:0;margin:0;padding:0;background:transparent;height:'+Math.max(400,h0)+'px';"
    "f.srcdoc='<!doctype html><html><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
    "</head><body style=\"margin:0\">'+c.innerHTML+'</body></html>';"
    "rd.style.display='none';box.appendChild(f);"
    "function fit(){try{var d=f.contentDocument;if(!d||!d.documentElement)return;var h=d.documentElement.scrollHeight;"
    "if(h>40&&Math.abs(h-f.offsetHeight)>1)f.style.height=h+'px'}catch(e){}}"
    "f.addEventListener('load',function(){fit();try{new f.contentWindow.ResizeObserver(fit).observe(f.contentDocument.documentElement)}"
    "catch(e){setInterval(fit,400)}setTimeout(fit,300);setTimeout(fit,1500)})})();</script>")


_NBP_STATE = {"lang": "en", "live": {}}


def _nbp_say(ok, txt, key=None):
    from IPython.display import display
    import html as _h, re
    mark = "ℹ" if ok is None else ("✓" if ok else "✗")
    msg = "%s %s" % (mark, txt)
    st = {True: "solved", False: "wrong"}.get(ok)
    js = ("<script>try{localStorage.setItem('digichemjn.%s.reader.code.%s','%s')}catch(e){}</script>"
          % (re.sub(r"[^\w.-]", "", str(_NBP_DATA.get("id") or "nb")), re.sub(r"\W", "", str(key)), st)) if st and key else ""
    cls = {True: "nbok", False: "nbwarn"}.get(ok, "nbink")
    try:
        display({"text/plain": msg, "text/html": "<div class='%s' style='font-weight:600'>%s</div>%s"
                 % (cls, _h.escape(msg, quote=False), js)}, raw=True)
    except Exception:
        print(msg)


def _nbp_t(en, de):
    return de if _NBP_STATE["lang"] == "de" else en


def pruefe(key, *fns):
    """Check a coding exercise from a cell of your own: the same check as the window (and the Lab box).
        pruefe("t1")              # your function, defined in this notebook
        pruefe("t1", roots_of)    # or handed over"""
    key = str(key)
    d = _NBP_DATA.get("daten") or {}
    c = next((x for x in d.get("code") or () if x.get("task") == key), None)
    if c is None:
        _nbp_say(None, _nbp_t("There is no coding exercise %s in this notebook." % key,
                              "In diesem Notebook gibt es keine Programmieraufgabe %s." % key))
        return None
    src = (c.get("pruef") or {}).get(_NBP_STATE["lang"]) or c.get("pruef_code")
    if not src:
        _nbp_say(None, _nbp_t("Exercise %s has no check in this version: run it in the window (Run)." % key,
                              "Aufgabe %s hat in dieser Fassung keine Prüfung: im Fenster ausführen." % key))
        return None
    try:
        g = get_ipython().user_ns          # noqa: F821 — the reader's own names
    except Exception:
        g = globals()
    ns = dict(g)
    for f in fns:
        nm = getattr(f, "__name__", None)
        if nm:
            ns[nm] = f
    if c.get("cname") and len(fns) == 1 and callable(fns[0]):
        ns[c["cname"]] = fns[0]
    try:
        prog = {"__name__": "_nbrw_check"}
        exec(compile(src, "<check %s>" % key, "exec"), prog)
        ok, tip = prog["_nbrw_check"](ns)
    except Exception as e:
        ok, tip = False, _nbp_t("Your function ran but crashed on the test inputs: %r" % (e,),
                                "Ihre Funktion lief, brach aber bei den Testwerten ab: %r" % (e,))
    if ok:
        _nbp_say(True, _nbp_t("correct, well done!", "richtig, gut gemacht!") + (" " + str(tip) if tip else ""), key)
    else:
        _nbp_say(False, _nbp_t("Not there yet, keep going.", "Noch nicht, weiter so.") + (" " + str(tip) if tip else ""), key)
    return None


def show(id=None, lang=None):
    """The document of this notebook once more (its package, built with the notebook)."""
    from IPython.display import display
    if id is not None and str(id) != _NBP_DATA.get("id"):
        _nbp_say(None, "This notebook carries %r, not %r." % (_NBP_DATA.get("id"), id))
        return None
    if lang in ("en", "de"):
        _NBP_STATE["lang"] = lang
    display({"text/html": _nbp_html(_NBP_DATA, _NBP_STATE["lang"]),
             "text/plain": "DigiChemJN — %s (reading window; run this cell in JupyterLab, Notebook 7, "
                           "VS Code or PyCharm)" % (_NBP_DATA.get("title") or {}).get(_NBP_STATE["lang"], "")}, raw=True)
    return None


def _nbp_live(nr, **values):
    """The picture of slider `nr` (0, 1, …) at any value, as HTML (the program of the package, E38 P4)."""
    p = _NBP_STATE["live"].get(nr)
    if p is None:
        rg = ((_NBP_DATA.get("daten") or {}).get("regler") or [])
        lv = rg[nr].get("live") if nr < len(rg) else None
        src = (lv.get("code") or lv.get("py")) if isinstance(lv, dict) else None
        if not src:
            raise LookupError("slider %r has no live program in this package" % (nr,))
        p = {"__name__": "_nbrw_live"}
        exec(compile(src, "<slider %d>" % nr, "exec"), p)
        _NBP_STATE["live"][nr] = p
    return p["_nbrw_render"](**values)


def _nbp_main(g):
    import os
    if os.environ.get("DIGICHEM_LAB") == "1":
        return g["_nbz_run"](g["_NBZ"], g)
    _NBP_STATE["lang"] = _nbp_lang(_NBP_DATA)
    show()
    return None
