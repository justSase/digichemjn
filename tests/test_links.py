"""1) no SyntaxWarning may reach the student (it renders as a red block at the top)
   2) every number in the progress bar must link to an anchor that really exists"""
import json, io, contextlib, warnings, re, sys, gc
import matplotlib; matplotlib.use("Agg")
import IPython.display as ipd
SHOWN=[]
def _rec_display(*a, **k):
    for o in a:
        v = getattr(o, "data", None) or getattr(o, "value", None)
        if isinstance(v, str): SHOWN.append(v)
ipd.display = _rec_display          # the mega-cell imports display FROM this module
# 2026-09-25 — THE LIST IS FOUND, NOT TYPED.
# It was five hard-coded paths with the version written into two of them, so
# every version bump silently pointed the suite at a file that no longer
# existed — and a FileNotFoundError is not a test result, it is a test that
# stopped running. The version comes from the toolkit, the same single source
# the builders read, and a missing file is now a FAILURE with a name.
import re as _reV
_NBV = _reV.search(r'NB_VERSION = "([^"]+)"',
                   open("toolkit/chapter_template.py", encoding="utf-8").read()).group(1)
NBS = ["start/Start_Here_How_These_Notebooks_Work_v%s.ipynb" % _NBV,
       "complex/Complex_Numbers_Step_by_Step_v%s.ipynb" % _NBV,
       "sets/Sets_Step_by_Step_v%s.ipynb" % _NBV,
       "ml/Machine_Learning_LLMs_AI_Step_by_Step_v%s.ipynb" % _NBV,
       "modeling/Introduction_to_Modeling_v%s.ipynb" % _NBV]
import os as _osV
_missing = [p for p in NBS if not _osV.path.exists(p)]
fails=[]
for _m in _missing:
    fails.append("%s was never built — build all five before this suite runs" % _m)
NBS = [p for p in NBS if p not in _missing]
def _css_of(G):
    grab={}
    class R:
        def __init__(self,v): grab["css"]=v
    oi,oj=G["IHTML"],G["inject_jump"]; G["IHTML"]=R; G["inject_jump"]=lambda: None
    ok=G.get("nbrail_js"); G["nbrail_js"]=lambda: None
    G["inject_style"](); G["IHTML"],G["inject_jump"],G["nbrail_js"]=oi,oj,ok
    return grab.get("css","")
for path in NBS:
    src="\n".join(l for l in __import__("megasrc").expand("".join(max(json.load(open(path))["cells"], key=lambda c: len("".join(c["source"])))["source"])).splitlines()
                  if not l.strip().startswith("%pip"))
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        code = compile(src, "<mega>", "exec")
        sw = [x for x in w if issubclass(x.category, SyntaxWarning)]
    name = path.split("/")[-1]
    print("%-46s SyntaxWarnings: %d" % (name, len(sw)))
    for x in sw:
        line = src.splitlines()[x.lineno-1].strip()[:90]
        print("    line %s: %s\n      >>> %s" % (x.lineno, x.message, line))
        fails.append("%s: SyntaxWarning at line %s (%s)" % (name, x.lineno, x.message))
    SHOWN.clear()
    G={"__name__":"__main__","display":_rec_display}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(code, G)
    if "complex" not in path:
        continue
    # collect every HTML widget this notebook built, and look for the anchor ids
    import ipywidgets as W
    # anchors are emitted both as ipywidgets HTML and via IPython display(HTML(...))
    html = "".join(o.value for o in gc.get_objects()
                   if isinstance(o, W.HTML) and isinstance(getattr(o, "value", None), str))
    html += "".join(SHOWN)
    rail = G["_prog_html"]()
    targets = re.findall(r'data-target="([^"]+)"', rail)
    ids = set(re.findall(r'id="([^"]+)"', html)) | set(re.findall(r"id='([^']+)'", html))
    print("    progress bar: %d numbers, %d of them are jump links" %
          (len(G["_TASKS"]["order"]), len(targets)))
    ST = G["structure"]()
    kinds = {}
    for e in ST: kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    print("    timeline from the accordions: %s" % kinds)
    if kinds.get("group", 0) < 3:   fails.append("sections missing from the timeline")
    if kinds.get("chapter", 0) < 5: fails.append("chapters missing from the timeline")
    if kinds.get("sub", 0) < 5:     fails.append("sub-sections missing from the timeline")
    mapped = {e["task"] for e in ST if e.get("task")}
    if mapped != set(G["_TASKS"]["order"]):
        fails.append("timeline and task list disagree: %s vs %s"
                     % (sorted(mapped), G["_TASKS"]["order"]))
    # 2026-09-24aa — ONE SECTION AND ONE CHAPTER ARE OPEN, AND NOTHING ELSE.
    # The Appendix used to open too, on the argument that a reader looking for
    # the glossary should not have to guess. The cost was a notebook that
    # presents itself half-unpacked; the rail is the table of contents now, so
    # nothing behind a closed lid is hidden. What opens is Content, because that
    # is where the reader starts, and chapter 1 inside it.
    _seen = {}
    _chaps = []
    for e in ST:
        if e["kind"] == "group":
            _seen[e["title"]] = e["open"]
            if e["title"] != "Content" and e["open"]:
                fails.append("section %r is expanded on open" % e["title"])
        if e["kind"] == "sub" and e["open"]:
            fails.append("sub-section %r is expanded on open" % e["title"])
        if e["kind"] == "chapter":
            _chaps.append(e)
    if _seen.get("Content") is False:
        fails.append("the Content section is closed on open")
    if not _chaps or not _chaps[0]["open"]:
        fails.append("the first chapter is not open on open")
    for e in _chaps[1:]:
        if e["open"]:
            fails.append("chapter %r is expanded on open" % e["title"])
    opened = [e["title"] for e in ST if e["kind"] == "group" and e["open"]]
    print("    sections expanded on open: %s" % (opened or "none"))
    # the panel must be fully opaque and reserve its own height
    _c = _css_of(G)
    if "rgba(246,248,250,.9" in _c or "rgba(29,34,40,.9" in _c:
        fails.append("the panel background is still translucent")
    if "reserve(" not in "".join(l for l in src.splitlines() if "reserve" in l):
        fails.append("the panel does not reserve space, content will hide under it")
    # 2026-09-24bf — A CSS ESCAPE IS NOT A PYTHON ESCAPE.
    # The stylesheet is an ordinary Python string, so `content:"\01F512"` was
    # read as chr(1) + "F512" before CSS ever saw it: the lock box drew a tofu
    # and the letters F512 where the padlock belongs. Nothing in the markup
    # could show it — the glyph is the stylesheet's — so it went unseen until
    # the box was screenshotted in a real browser.
    if "\x01" in _c or "\x02" in _c:
        fails.append("a control character is in the stylesheet — a CSS escape "
                     "was swallowed by Python (write \\\\ in the source)")
    # 2026-09-25c — THE PADLOCK IS DRAWN NOW, SO IT MUST NOT BE TYPED.
    # Until this build the check was the other way round: the escapes had to be
    # PRESENT. They are gone on purpose — an emoji cannot take the skin's
    # colour, cannot be centred inside a mark that is a square turned 45°, and
    # is a different picture on every platform. What has to be true instead is
    # that no padlock is typed anywhere, in either spelling, and that the
    # drawing that replaced it is there.
    for _g in ("\\01F512", "\\01F513", "\U0001F512", "\U0001F513"):
        if _g in _c:
            fails.append("a padlock glyph %r is still typed into the stylesheet "
                         "— the lock is drawn from the class now" % _g)
    # The stylesheet check above covers the CSS. Here the MARKUP is checked —
    # but only outside comments: this file's own notes talk about the emoji
    # that was removed, and a note is not a glyph on anybody's screen.
    _nocom = "\n".join(l for l in src.splitlines()
                       if not l.lstrip().startswith("#"))
    if "\U0001F512" in _nocom or "\U0001F513" in _nocom:
        fails.append("a padlock emoji is still written into the MARKUP")
    for _probe in ("--nbskin-lock", ".nbmap-node.locked .nbchapdot::before",
                   ".nbcodemark.cd-current .nbdotg::before"):
        if _probe not in _c:
            fails.append("the drawn lock is missing from the stylesheet (%r)" % _probe)
    # difficulty must reach the numeric tolerance
    t0 = G["tol"](); G["set_difficulty"]("strict"); t1 = G["tol"]()
    G["set_difficulty"]("gentle"); t2 = G["tol"](); G["set_difficulty"]("standard")
    print("    tolerance  gentle %.0e > standard %.0e > strict %.0e" % (t2, t0, t1))
    if not (t2 > t0 > t1): fails.append("difficulty does not change the tolerance")
    # the controls must be in the panel
    # 2026-09-24ao: `nbgui-lab` (the panel's own size control) is gone — with
    # the names off the rail there was nothing in a wide panel to look at.
    for c in ("nbfull", "nbtheme", "nbprofile", "nbzoom-lab"):
        if c not in G["_prog_html"](): fails.append("control %r missing from the panel" % c)
    if "nbgui-lab" in G["_prog_html"]():
        fails.append("the panel size control is back in the toolbar")
    if "body.nbdark" not in _css_of(G): fails.append("the ◐ override has no CSS")
    # 2026-09-24ar — UNLOCKING IS AN EVENT YOU CAN SEE.
    # Three things had to be true and only the first was: the chapter's lock
    # comes off, its mark stops being a lock on the rail, and the accordion is
    # actually unfolded. The rail kept `data-lock` forever (so the mark stayed
    # a double-click target), the open padlock was tested against the GUARDING
    # task rather than the guarded one and so never appeared, and the accordion
    # was only unfolded when it had never been touched.
    _rail0 = G["_prog_html"]()
    _locks0 = sorted(set(re.findall(r'data-lock="([^"]+)"', _rail0)))
    _key = _locks0[2] if len(_locks0) > 2 else _locks0[0]
    _acc = G["_TASKS"]["acc"]
    _guarded = next((t for t, g in G["_TASKS"]["guard"].items() if g == _key), None)
    if _guarded and _acc.get(_guarded) is not None:
        _acc[_guarded].selected_index = 0      # the reader has been here before
    G["unlock_chapter_only"](_key)
    _rail1 = G["_prog_html"]()
    _locks1 = sorted(set(re.findall(r'data-lock="([^"]+)"', _rail1)))
    print("    unlocking %s: rail locks %d -> %d, padlocks left %d"
          % (_key, len(_locks0), len(_locks1), _rail1.count("\U0001f512")))
    if _key in _locks1:
        fails.append("the rail still calls %r a lock after it was opened" % _key)
    # 2026-09-24az — AND IT CARRIES NOTHING ONCE IT IS OPEN.
    # The open padlock used to stay on the mark. It is now the state BETWEEN
    # picking the chapter on the rail and turning the key in its box, so a
    # chapter that is simply open must show no glyph at all — one that did
    # would claim a lock that is not there any more.
    if "\U0001f513" in _rail1:
        fails.append("an open padlock is left on the rail after %r was opened" % _key)
    # (the panel's HTML carries other padlocks too — the coding ladder's
    # cd-lock marks and the tooltips — so counting them all says nothing.)
    if _guarded and _acc.get(_guarded) is not None \
       and _acc[_guarded].selected_index != 0:
        fails.append("the chapter guarded by %r stayed folded after unlocking" % _key)
    # 2026-09-24az — the locked box shows a PADLOCK, and names its own key so
    # the rail can find it. The open state is a CSS class, so all that can be
    # checked from Python is that the markup carries what the stylesheet needs.
    _shell = G["_LOCKS"][("chapter", _locks0[0])]["closed"]
    _parts = []
    def _collect(w):
        v = getattr(w, "value", None)
        if isinstance(v, str):
            _parts.append(v)
        for c in getattr(w, "children", ()) or ():
            _collect(c)
    for _w in _shell:
        _collect(_w)
    # only the NOTE: the hidden box the gear drawer borrows carries the older,
    # longer lock panel, and that one is allowed its own padlock.
    _note = "".join(v for v in _parts if "nblocked-note" in v)
    print("    the locked box: padlock %s, keyed class %s, two hints %s"
          % ("\U0001f512" in _note,
             ("nblocked-%s" % _locks0[0]) in _note,
             ("nblocked-shut" in _note and "nblocked-open" in _note)))
    if "\U0001f512" in _note or "\U0001f513" in _note:
        fails.append("the lock box writes its padlock into the markup — it has "
                     "to come from the stylesheet, or the two sides can drift")
    if ("nblocked-%s" % _locks0[0]) not in _note:
        fails.append("the lock box does not name its key, so the rail cannot arm it")
    if "nblocked-shut" not in _note or "nblocked-open" not in _note:
        fails.append("the lock box has no armed/disarmed wording")
    if "nblocked-lock" not in _note:
        fails.append("the lock box has no padlock element")
    # and the ordinary route does the same: answering opens the next chapter AND
    # unfolds it, even one the reader had already closed once.
    _nxt = G["_TASKS"]["order"][0]
    _g2 = next((t for t, g in G["_TASKS"]["guard"].items() if g == _nxt), None)
    if _g2 and _acc.get(_g2) is not None:
        _acc[_g2].selected_index = None
        G["task_solved"](_nxt)
        if _acc[_g2].selected_index != 0:
            fails.append("answering %r did not unfold the chapter it opens" % _nxt)
    G["reset_progress"]() if "reset_progress" in G else None
    # 2026-09-24bf — OPENING THE CHAPTER DOES NOT HAND OVER ITS EXERCISES.
    # The box (and the rail's key) buy the chapter's TEXT. The written exercise
    # inside it keeps a lock of its own on the same key, and only a correct
    # answer — on either route — takes it off. Without this the lock chain was
    # decorative: a reader could reach the last chapter with every exercise open
    # and none of them answered.
    _L = G["_LOCKS"]
    # the box again, from a clean slate (the checks above ended with a reset)
    G["unlock_chapter_only"](_key)
    _pl = _L.get(("practice", _key))
    print("    after the box: chapter %s, its exercise %s"
          % ("open" if _L[("chapter", _key)]["open"] else "shut",
             "open" if (_pl and _pl["open"]) else "shut"))
    if _pl is None:
        fails.append("chapter exercises carry no lock of their own")
    elif _pl["open"]:
        fails.append("the box opened the exercises of %r as well as the chapter" % _key)
    for _route, _fn in (("skip", "task_skipped"), ("give up", "task_bypassed")):
        _k2 = next((t for t in G["_TASKS"]["order"]
                    if ("practice", t) in _L and not _L[("practice", t)]["open"]), None)
        if _k2:
            G[_fn](_k2)
            if _L[("practice", _k2)]["open"]:
                fails.append("%r opened the exercises of %r" % (_route, _k2))
            if not _L[("chapter", _k2)]["open"]:
                fails.append("%r did not open the chapter of %r" % (_route, _k2))
    _k3 = next((t for t in G["_TASKS"]["order"]
                if ("practice", t) in _L and not _L[("practice", t)]["open"]), None)
    if _k3:
        G["task_solved"](_k3)
        if not _L[("practice", _k3)]["open"]:
            fails.append("answering %r correctly did not open the exercises it guards" % _k3)
    _k4 = next((t for t in G["_TASKS"]["order"]
                if ("practice", t) in _L and not _L[("practice", t)]["open"]), None)
    if _k4:
        G["task_code_solved"](_k4)
        if not _L[("practice", _k4)]["open"]:
            fails.append("solving %r in code did not open the exercises it guards" % _k4)
    G["reset_progress"]()
    if any(e["open"] for (k, _t), e in _L.items() if k == "practice"):
        fails.append("a reset left an exercise lock open")
    # the panel's size control is back, and it is part of the rail's own markup
    if 'class="nbgrip"' not in G["_prog_html"]():
        fails.append("the grip (the panel size control) is missing from the rail")
    # 2026-09-24bg — the marker's handle and the style button are part of the
    # rail's own markup, so they survive a panel rebuild the way the marks do.
    _r = G["_prog_html"]()
    for _c, _what in (('class="nbmap-cursor"', "the marker's cursor"),
                      ('nbbtn nbskin', "the style button")):
        if _c not in _r:
            fails.append("%s is missing from the panel" % _what)
    # ...and each style is a complete palette, not three boxes. The JS suite
    # drives a mock page with no prose in it, so the rules are checked here.
    _c2 = _css_of(G)
    for _sk in ("cyber", "retro", "fairy"):
        _n = _c2.count("body.nbskin-%s" % _sk)
        if _n < 8:
            fails.append("the %r style has only %d rules — it cannot repaint "
                         "the whole instrument" % (_sk, _n))
        for _part in (".nbbox", "#nbpanel-root .nbrail", ".nbtitle-card"):
            if ("body.nbskin-%s %s" % (_sk, _part)) not in _c2 and \
               ("body.nbskin-%s %s," % (_sk, _part)) not in _c2:
                fails.append("the %r style does not reach %s" % (_sk, _part))
    # the native windows the browser draws for us have to be told which way
    # round the page is, or a forced dark theme leaves white-on-white dropdowns
    for _cs in ("body.nbforce-dark{color-scheme:dark;}",
                "body.nbforce-light{color-scheme:light;}"):
        if _cs not in _c2.replace("\n", "").replace("  ", ""):
            fails.append("missing colour-scheme instruction: %s" % _cs)
    missing_anchor = [k for k in G["_TASKS"]["order"] if not G["_TASKS"]["anchor"].get(k)]
    if missing_anchor:
        fails.append("tasks without an anchor: %s" % missing_anchor)
    dead = [t for t in targets if t not in ids]
    print("    link targets resolved: %d/%d" % (len(targets)-len(dead), len(targets)))
    if dead:
        fails.append("dead jump targets in the progress bar: %s" % dead)
    if "nbjump" not in rail:
        fails.append("progress bar numbers are not jump links")
    if "position:fixed" not in G["inject_style"].__doc__ if G["inject_style"].__doc__ else False:
        pass
print("\n"+("LINKS AND WARNINGS OK" if not fails else "FAILURES:\n- "+"\n- ".join(fails)))
sys.exit(1 if fails else 0)
