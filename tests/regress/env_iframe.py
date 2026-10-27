"""E26.1 · Pflichttest (STOP.md, E26 Teil 1) — Python workshop.
    python3 tests/regress/env_iframe.py <notebook.ipynb> [--shots DIR] [--json out.json]

EVERY OUTPUT IN A PAGE OF ITS OWN (PyCharm 2025.2 / JCEF 122, VS Code): our
script reaches only its own output. js_e25 rebuilt the opposite (all outputs in
one page) and was green BECAUSE of the error (6th time). Here the notebook's
cell runs in a real kernel (jupyter_client, every iopub message, display
updates applied by display id as a front end does) and every output is put
into an iframe of its own, as such a viewer does: Javascript runs in its frame
(`element` = null), text/html is drawn, a widget output without a widget
manager shows its text/html, else its text/plain; no widget manager anywhere.
The host page is light (#ffffff) or dark (#2b2d30, PyCharm Darcula) with the
browser's colour scheme set to match. Chromium: the one Playwright has (the
oldest available here, 1194 ≈ Chrome 141 — no Chromium 122 in this container).
Counted over ALL frames, visible elements only:
  title cards        elements whose own text is the notebook title, ≥ 24 px   want 1
  widget hints       "(widgets) cannot be drawn" / ".nbwidget-hint"             want 0
  tool buttons       button, [role=button], input, select, #nbpanel-root       want 0
  chapters 1–7       each chapter title of the run (the kernel's _STRUCT) in
                     the visible text                                           want 7/7
  contrast           every visible text element against its painted
                     background (alpha blended up to the host)                  min ≥ 4.5
  one language       en run: no German marker; de run: no English marker       want 0
Rows: en light, en dark, en with PYCHARM_HOSTED=1 (dark), de light; then the
nbconvert HTML of the executed file (GitHub / nbviewer preview) with scripts
off and on, light and dark — measured in the output areas only (the start
line is markdown, en + de by design, and the source is the template's).
v1.69: red (two title cards, Play and the tools drawn, chapters not in the
visible text). Owner: Python. exit 0 = REGRESS-ENV-IFRAME OK."""
import sys, os, re, json, html as _h, subprocess, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

WMIME = "application/vnd.jupyter.widget-view+json"
DE_MARK = ("Führen Sie", "Lesefassung", "Kapitel ", "Aufgabe", "Zeitleiste")
EN_MARK = ("Run the cell", "Reading version", "Chapter ", "exercise", "timeline")

def run_cell(src, extra):
    """Every output of the mega-cell as a front end keeps it, + chapter titles."""
    from jupyter_client.manager import start_new_kernel
    nb = json.load(open(src))
    code = "".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"])
    env = {k: v for k, v in os.environ.items()
           if k not in ("PYCHARM_HOSTED", "DIGICHEM_STATIC_HTML", "DIGICHEM_LANG", "VSCODE_PID")}
    env.update(extra)
    km, kc = start_new_kernel(kernel_name="python3", env=env, cwd=os.path.dirname(os.path.abspath(src)))
    try:
        models = {}
        def drain(msg_id):
            outs, errs, text = [], [], []
            while True:
                m = kc.get_iopub_msg(timeout=600)
                if m["parent_header"].get("msg_id") != msg_id: continue
                t, c = m["msg_type"], m["content"]
                did = (c.get("transient") or {}).get("display_id")
                if t == "comm_open":
                    models[c["comm_id"]] = dict((c.get("data") or {}).get("state") or {})
                elif t == "comm_msg" and (c.get("data") or {}).get("method") == "update":
                    models.setdefault(c["comm_id"], {}).update(c["data"].get("state") or {})
                if t in ("display_data", "execute_result"):
                    outs.append({"data": c["data"], "id": did, "raw": c["data"]})
                elif t == "update_display_data":
                    for o in outs:
                        if did and o["id"] == did: o["data"] = c["data"]
                elif t == "stream": text.append(c["text"])
                elif t == "error": errs.append(c["ename"] + ": " + c["evalue"])
                elif t == "status" and c["execution_state"] == "idle": break
            return outs, errs, "".join(text)
        outs, errs, _ = drain(kc.execute(code))
        # E38 P3 (Python): the cell of the Vorlage shows the PACKAGE (toolkit/paketzelle.py) — no toolkit in the kernel,
        # no _STRUCT; the chapter titles of the run are the package's (daten.json kapitel_titel, the run's language).
        # Behauptete bisher: every run has _STRUCT (the toolkit built the document in the kernel).
        _, e2, txt = drain(kc.execute(
            "import json as _j\n"
            "try:\n    _t = [e['title'] for e in _STRUCT if e.get('kind') == 'chapter']\n"
            "except NameError:\n"
            "    _t = ((_NBP_DATA.get('daten') or {}).get('kapitel_titel') or {}).get(_NBP_STATE['lang']) or []\n"
            "print(_j.dumps(_t))"))
        chapters = json.loads(txt.strip().splitlines()[-1]) if txt.strip() else []
        for o in outs: o["models"] = models
        return outs, errs + e2, chapters
    finally:
        km.shutdown_kernel(now=True)

# E26.1b — A FRONT END THAT DRAWS WIDGETS ITSELF, ONE PAGE PER OUTPUT (PyCharm
# 2025.2.3, 11.10., v1.70: the panel's HBox came out as a white "Your progress"
# card under the reading version; the iframe rows above showed a widget output
# as its empty text/plain and saw nothing). Generic ipywidgets semantics from
# the kernel's own model states (comm messages): the layout's inline styles
# (display, visibility, height, width, overflow), HTML values, boxes,
# accordions/tabs (selected child open), buttons, fields, choices, Output
# widgets' outputs — and none of our stylesheet or scripts.
def _ref(x):
    return x[10:] if isinstance(x, str) and x.startswith("IPY_MODEL_") else None

def widget_html(models, mid, depth=0):
    m = models.get(mid) or {}
    if depth > 60: return ""
    lay = models.get(_ref(m.get("layout")) or "", {}) or {}
    st = []
    for k, css in (("display", "display"), ("visibility", "visibility"), ("height", "height"), ("width", "width"),
                   ("max_width", "max-width"), ("overflow", "overflow"), ("margin", "margin")):
        v = lay.get(k)
        if v not in (None, ""): st.append("%s:%s" % (css, v))
    sty = ";".join(st)
    cls = " ".join(m.get("_dom_classes") or [])
    name = m.get("_model_name") or ""
    kids = lambda: "".join(widget_html(models, _ref(c), depth + 1) for c in (m.get("children") or []))
    if name in ("HTMLModel", "HTMLMathModel"):
        return "<div class='w-html %s' style='%s'>%s</div>" % (cls, sty, m.get("value") or "")
    if name == "LabelModel":
        return "<div class='%s' style='%s'>%s</div>" % (cls, sty, _h.escape(m.get("value") or ""))
    if name in ("AccordionModel", "TabModel", "StackModel"):
        tl, sel, out = list(m.get("titles") or []), m.get("selected_index"), []
        for i, c in enumerate(m.get("children") or []):
            t = tl[i] if i < len(tl) else ""
            out.append("<div><div class='w-acc-h'>%s</div><div style='display:%s'>%s</div></div>"
                       % (_h.escape(t or ""), "block" if sel == i else "none", widget_html(models, _ref(c), depth + 1)))
        return "<div class='%s' style='%s'>%s</div>" % (cls, sty, "".join(out))
    if name.endswith("BoxModel"):
        fl = "display:flex;flex-direction:%s;" % ("row" if name == "HBoxModel" else "column")
        return "<div class='%s' style='%s%s'>%s</div>" % (cls, fl, sty, kids())
    if name in ("ButtonModel", "ToggleButtonModel"):
        return "<button class='%s' style='%s'>%s</button>" % (cls, sty, _h.escape(m.get("description") or ""))
    if name in ("DropdownModel", "SelectModel", "RadioButtonsModel", "ToggleButtonsModel", "SelectionSliderModel"):
        return "<select class='%s' style='%s'>%s</select>" % (cls, sty, "".join(
            "<option>%s</option>" % _h.escape(str(o)) for o in (m.get("_options_labels") or [])))
    if name == "TextareaModel":
        return "<textarea class='%s' style='%s'>%s</textarea>" % (cls, sty, _h.escape(str(m.get("value") or "")))
    if name.endswith(("TextModel", "SliderModel", "CheckboxModel", "PasswordModel")) or name in ("BoundedIntTextModel", "BoundedFloatTextModel"):
        return "<input class='%s' style='%s' value='%s'>" % (cls, sty, _h.escape(str(m.get("value", "")), quote=True))
    if name == "OutputModel":
        return "<div class='%s' style='%s'>%s</div>" % (cls, sty, "".join(frame_doc(o.get("data") or {})
                                                                        for o in (m.get("outputs") or [])
                                                                        if o.get("output_type") in ("display_data", "execute_result")))
    if name in ("ImageModel",):
        return "<div class='%s' style='%s'>[image]</div>" % (cls, sty)
    return "<div class='%s' style='%s'>%s</div>" % (cls, sty, kids())

def frame_doc(d, models=None):
    if "application/javascript" in d:
        js = d["application/javascript"]
        return "<script>var element = null;\n%s\n</script>" % js.replace("</script", "<\\/script")
    if models is not None and WMIME in d:
        return widget_html(models, (d[WMIME] or {}).get("model_id"))
    if "text/html" in d: return d["text/html"]
    for k in ("image/svg+xml",):
        if k in d: return d[k]
    if "image/png" in d: return "<img src='data:image/png;base64,%s'>" % d["image/png"]
    t = d.get("text/plain") or ""
    return "<pre>%s</pre>" % _h.escape(t) if t else ""

def host_page(outs, dark, widgets=False, raw=False):
    bg = "#2b2d30" if dark else "#ffffff"
    fr = []
    for o in outs:
        doc = "<!doctype html><meta charset=utf-8><body style='margin:0'>" + frame_doc(
            o["raw"] if raw else o["data"], o.get("models") if widgets else None)
        fr.append("<iframe class='out' style='display:block;width:100%%;border:0;height:40px' srcdoc=\"%s\"></iframe>"
                  % _h.escape(doc, quote=True))
    return ("<!doctype html><meta charset=utf-8><body style='margin:0;padding:8px 16px;background:%s;color:%s'>%s"
            "<script>function fit(){document.querySelectorAll('iframe.out').forEach(function(f){try{"
            "var d=f.contentDocument;if(d&&d.documentElement){f.style.height=Math.max(1,d.documentElement.scrollHeight)+'px';}}catch(e){}});}"
            "setInterval(fit,150);</script>" % (bg, "#dfe1e5" if dark else "#1f2328", "".join(fr)))

MEASURE = r"""([title, chapters, hostBg, rootSel]) => {
  var lum = function(c){ var f = function(v){ v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
  var rgba = function(s){ var m = /rgba?\(([^)]+)\)/.exec(s || ''); if (!m) return [0,0,0,0];
    var p = m[1].split(/[ ,\/]+/).filter(Boolean).map(parseFloat); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
  var over = function(top, bot){ var a = top[3]; return [top[0]*a + bot[0]*(1-a), top[1]*a + bot[1]*(1-a), top[2]*a + bot[2]*(1-a), 1]; };
  var vis = function(e){ var w = e.ownerDocument.defaultView, b = e.getBoundingClientRect(), s = w.getComputedStyle(e);
    if (!(b.width > 0 && b.height > 0) || s.visibility === 'hidden' || +s.opacity === 0) return false;
    for (var x = e; x; x = x.parentElement) if (w.getComputedStyle(x).display === 'none') return false;
    var fe = w.frameElement; if (fe) { var fb = fe.getBoundingClientRect(); if (!(fb.width > 0 && fb.height > 0)) return false; }
    return true; };
  var host = rgba(hostBg);
  var bgOf = function(e){ var layers = [];
    for (var x = e; x; x = x.parentElement) { var c = rgba(x.ownerDocument.defaultView.getComputedStyle(x).backgroundColor); if (c[3] > 0) layers.push(c); if (c[3] >= 1) break; }
    var b = (layers.length && layers[layers.length - 1][3] >= 1) ? layers.pop() : host;
    while (layers.length) b = over(layers.pop(), b);
    return b; };
  var docs = [document].concat([].slice.call(document.querySelectorAll('iframe.out')).map(function(f){ return f.contentDocument; }).filter(Boolean));
  var R = {cards: 0, hints: 0, tools: 0, toolList: [], text: '', low: 0, minC: 99, lowEx: [], frames: docs.length - 1, visFrames: 0,
           outside: 0, outsideEx: [], blank: 0};
  docs.forEach(function(d, di){
    if (!d.body) return;
    var any = false;
    var all = rootSel ? [].concat.apply([], [].map.call(d.querySelectorAll(rootSel), function(r){ return [].slice.call(r.querySelectorAll('*')); }))
                      : [].slice.call(d.body.querySelectorAll('*'));
    all.forEach(function(e){
      if (e.tagName === 'SCRIPT' || e.tagName === 'STYLE' || e.tagName === 'IFRAME') return;
      var own = [].filter.call(e.childNodes, function(n){ return n.nodeType === 3 && n.textContent.trim(); }).map(function(n){ return n.textContent; }).join(' ').trim();
      var isTool = (/^(BUTTON|INPUT|SELECT|TEXTAREA)$/.test(e.tagName) || e.getAttribute('role') === 'button' || e.id === 'nbpanel-root') && !e.closest('.nbrw-panel,.nbrw-task,.nbrw-copy,.nbrw-slider,.nbrw-cover');  // E26.2: the reading window's own panel (env_reader.py) and its exercise fields (py_e26_2.py) are not tools; E26.3: nor its preview (Play, EN|DE, mode cards — behauptete bisher: the window opens on the document)
      var isHint = (e.classList && e.classList.contains('nbwidget-hint')) || /\(widgets\) (cannot be drawn|können)/.test(own);
      if (!own && !isTool && !isHint) return;
      if (!vis(e)) return;
      if (di > 0) any = true;
      if (di > 0 && !d.querySelector('.nbreading')) { R.outside++; if (R.outsideEx.length < 4) R.outsideEx.push((own || e.tagName).slice(0, 40)); }
      if (isTool) { R.tools++; if (R.toolList.length < 6) R.toolList.push(e.tagName + ':' + (e.textContent || e.value || '').trim().slice(0, 20)); }
      if (isHint) R.hints++;
      if (!own) return;
      var s = e.ownerDocument.defaultView.getComputedStyle(e);
      if (own.replace(/\s+/g, ' ') === title && parseFloat(s.fontSize) >= 24) R.cards++;
      var fg = rgba(s.color), bg = bgOf(e); fg = over(fg, bg);
      var L1 = lum(fg), L2 = lum(bg), c = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
      if (c < R.minC) R.minC = c;
      if (c < 4.5) { R.low++; if (R.lowEx.length < 4) R.lowEx.push(own.slice(0, 30) + ' ' + c.toFixed(2)); }
    });
    if (any) R.visFrames++;
    // E26.1b: height the frames after the reading version take (held widgets
    // with content overflowing a 0-px box still make a frame tall: empty space)
    // (the content's height, as a front end sizes an output to it: the body's)
    if (di > 0 && !d.querySelector('.nbreading')) R.blank += Math.max(d.body.scrollHeight, d.body.getBoundingClientRect().height);
    try { R.text += ' ' + (rootSel ? [].map.call(d.querySelectorAll(rootSel), function(r){ return r.innerText || ''; }).join(' ')
                                   : (d.body.innerText || '')); } catch (e) {}
  });
  R.chapters = chapters.filter(function(t){ return R.text.indexOf(t) >= 0; }).length;
  R.minC = Math.round(R.minC * 100) / 100;
  R.text = R.text.replace(/\s+/g, ' ');
  return R; }"""

# nbconvert: the outputs only — the start line (markdown, en + de by design, E24.3)
# and the cell's source are not the output and are drawn by the template
OUTS = ".jp-OutputArea, .output_area"

def judge(tag, r, nch, lang, rows, fails):
    other = [m for m in (DE_MARK if lang == "en" else EN_MARK) if m in r["text"]]
    rows.append(("%-34s " + ("outside %d · blank %d px · " % (r.get("outside", 0), r.get("blank", 0)) if r.get("strictOutside") else "") + "cards %d · hints %d · tools %d%s · chapters %d/%d · contrast min %.2f (%d below 4.5) · other language %s · frames %d (visible %d)")
                % (tag, r["cards"], r["hints"], r["tools"], (" " + str(r["toolList"])) if r["tools"] else "",
                   r["chapters"], nch, r["minC"], r["low"], other or "none", r["frames"], r["visFrames"]))
    if r.get("strictOutside") and r["blank"] > 80:
        fails.append("%s outputs after the reading version take %d px of empty height, want ≤ 80" % (tag, r["blank"]))
    if r.get("strictOutside") and r["outside"]:
        fails.append("%s %d visible elements in outputs after the reading version, want 0: %s"
                     % (tag, r["outside"], r["outsideEx"]))
    if nch < NCH_WANT: fails.append("%s BAD the run named %d chapters (want ≥ %d)" % (tag, nch, NCH_WANT))
    if r["cards"] != 1: fails.append("%s %d visible title cards, want 1" % (tag, r["cards"]))
    if r["hints"]: fails.append("%s %d widget hints visible, want 0" % (tag, r["hints"]))
    if r["tools"]: fails.append("%s %d tool buttons/fields visible, want 0: %s" % (tag, r["tools"], r["toolList"]))
    if r["chapters"] < nch: fails.append("%s chapters in the visible text %d/%d" % (tag, r["chapters"], nch))
    if r["low"]: fails.append("%s %d text elements below contrast 4.5 (min %.2f): %s" % (tag, r["low"], r["minC"], r["lowEx"]))
    if other: fails.append("%s two languages: %s" % (tag, other))
    # E26.1b: the reading version's end card names no JupyterLab cell and offers
    # no buttons; its top line gives no pip advice where nothing is recognised
    for bad in ("leaves you an empty cell", "Start again with", "Neu beginnen mit", "pip install", "leere Zelle"):
        if bad in r["text"]: fails.append("%s visible text has %r" % (tag, bad))

NCH_WANT = 7

def want_chapters(src):
    """E28 (2026-10-12): the numbered chapters of THIS notebook, from the cell's pieces
    (c01…c07, k01…k05) — behauptete bisher: fest ≥ 7 (Complex)."""
    import json as _j
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "toolkit"))
    import megasrc, shortcell
    nb = _j.load(open(src, encoding="utf-8"))
    full = megasrc.expand("".join(max(nb["cells"], key=lambda c: len("".join(c["source"])))["source"]))
    return max(1, sum(1 for n, _ in shortcell.pieces(full) if re.match(r"<digichemjn:[a-z]\d\d\.py>$", n)))

def main():
    global NCH_WANT
    import nbpick
    args = [a for a in sys.argv[1:]]
    nbpick.argv_fix(sys.argv)                     # E28: no notebook → the template
    src = sys.argv[1]
    NCH_WANT = want_chapters(src)
    shots = args[args.index("--shots") + 1] if "--shots" in args else None
    jout = args[args.index("--json") + 1] if "--json" in args else None
    nbsrc = open(src, encoding="utf-8").read()
    m = re.search(r'class=\\"nbtitle-h\\"[^>]*>([A-Za-z][^<]{2,})<', nbsrc)
    title = _h.unescape(m.group(1)).strip() if m else ""
    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    rows, fails = [], []
    if not title: fails.append("BAD no notebook title found in the file")
    tmpd = tempfile.mkdtemp(prefix="envif_")
    # E26.1b: "w" = widgets drawn per output by the front end itself (PyCharm),
    # "w-raw" = the same, display updates NOT applied (outputs as first sent)
    runs = [("en", {}, [(False, ""), (True, ""), (False, "w")]),
            ("en PYCHARM_HOSTED=1", {"PYCHARM_HOSTED": "1"}, [(True, ""), (True, "w"), (True, "w-raw")]),
            ("de", {"DIGICHEM_LANG": "de"}, [(False, ""), (False, "w")])]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        try:
            for tag, env, themes in runs:
                outs, errs, chapters = run_cell(src, env)
                lang = "de" if "DIGICHEM_LANG" in env else "en"
                ttl = title
                if lang == "de":
                    # E28: the German title from the notebook's metadata (title_de, since E26.3) —
                    # behauptete bisher: only Complex/Modeling ("Komplexe Zahlen" …), else the English one
                    tde = (json.loads(nbsrc).get("metadata", {}).get("digichemjn", {}) or {}).get("title_de")
                    mm = re.search(r"Komplexe Zahlen|Einführung in die Modellierung", nbsrc)
                    ttl = tde or (mm.group(0) if mm else title)
                if errs: fails.append("%s the run raised: %s" % (tag, errs[:1]))
                rows.append("%s: %d outputs, first: %s" % (tag, len(outs), sorted(outs[0]["data"]) if outs else None))
                for dark, wmode in themes:
                    t2 = "%s %s%s" % (tag, "dark" if dark else "light", (" " + wmode) if wmode else "")
                    f = os.path.join(tmpd, "host_%s.html" % re.sub(r"\W+", "_", t2))
                    open(f, "w", encoding="utf-8").write(host_page(outs, dark, widgets=bool(wmode), raw=wmode == "w-raw"))
                    ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme="dark" if dark else "light")
                    pg = ctx.new_page(); pg.goto("file://" + f); pg.wait_for_timeout(2500)
                    r = pg.evaluate(MEASURE, [ttl, chapters, "rgb(43,45,48)" if dark else "rgb(255,255,255)", None])
                    r["strictOutside"] = True
                    judge("iframe " + t2, r, len(chapters), lang, rows, fails)
                    if shots: pg.screenshot(path=os.path.join(shots, "env_iframe_%s.png" % re.sub(r"\W+", "_", t2)))
                    ctx.close()
            # GitHub / nbviewer: the nbconvert HTML of the executed file
            ex = os.path.join(tmpd, "nb.ipynb"); shutil.copy(src, ex)
            subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", ex],
                           check=True, capture_output=True, cwd=tmpd)
            subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "html", ex], check=True,
                           capture_output=True, cwd=tmpd)
            hf = ex[:-6] + ".html"
            _, _, chapters = run_cell(src, {})
            for js in (False, True):
                for dark in (False, True):
                    t2 = "nbconvert js %s %s" % ("on" if js else "off", "dark" if dark else "light")
                    ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme="dark" if dark else "light",
                                        java_script_enabled=js)
                    pg = ctx.new_page(); pg.goto("file://" + hf); pg.wait_for_timeout(3000 if js else 800)
                    if not js:   # the measuring script itself needs JS: measure in a twin with JS, scripts removed
                        ctx2 = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme="dark" if dark else "light")
                        pg2 = ctx2.new_page()
                        noscript = re.sub(r"<script\b.*?</script>", "", open(hf, encoding="utf-8").read(), flags=re.S | re.I)
                        nf = os.path.join(tmpd, "noscript.html"); open(nf, "w", encoding="utf-8").write(noscript)
                        pg2.goto("file://" + nf); pg2.wait_for_timeout(800)
                        r = pg2.evaluate(MEASURE, [title, chapters, "rgb(255,255,255)", OUTS])
                        if shots: pg2.screenshot(path=os.path.join(shots, "env_iframe_%s.png" % re.sub(r"\W+", "_", t2)))
                        ctx2.close()
                    else:
                        r = pg.evaluate(MEASURE, [title, chapters, "rgb(255,255,255)", OUTS])
                        if shots: pg.screenshot(path=os.path.join(shots, "env_iframe_%s.png" % re.sub(r"\W+", "_", t2)))
                    judge(t2, r, len(chapters), "en", rows, fails)
                    ctx.close()
        except Exception as e:
            fails.append("BAD %s" % str(e)[:300])
        b.close()
    shutil.rmtree(tmpd, ignore_errors=True)
    print("\n".join(rows))
    if jout: json.dump({"rows": rows, "fails": fails}, open(jout, "w"), indent=1, ensure_ascii=False)
    print("REGRESS-ENV-IFRAME OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
