"""E33 · Python workshop (STOP.md Block „E33 — GILT JETZT“, Nutzer 13.10., v1.78 in PyCharm, VS Code, Lab, Lite).
    python3 tests/regress/py_e33.py [<notebook.ipynb> | --nb vorlage] [--lite] [--vscode] [--shots DIR] [--json out.json]

A SAVED FILE MUST OPEN CLEAN. The notebook is built (the argument) and run once (nbclient, a real kernel) and
saved with its outputs — what Lab, Lite and PyCharm keep. Then, measured in real pages (Chromium):
  A1  saved run, opened NOT trusted (fresh HOME/JUPYTER dirs): JupyterLab light + dark, JupyterLite light + dark
      (--lite: a site built here with jupyterlite-core, no kernel needed to show saved outputs), PyCharm rebuilt:
      every output in an iframe of its own, its HTML through a sanitizer like JupyterLab's (allowed tags and
      attributes, no <style>/<script>/<svg>/<template>, no data-*, no empty attribute, no var() declaration),
      the IDE's text colour on its background, light + dark. In the outputs:
        other language   texts of the OTHER language (the kernel's own pairs, ≥ 10 characters, two words) visible  want 0
        contrast         every visible text element against its painted background                            min ≥ 4.5
        buttons          visible <button>/<input> in the outputs (dead without script)                          want 0
  R1  where our script runs, the reading version is rebuilt to the v1.78 markup ELEMENT FOR ELEMENT: the kernel's
      _nbread_html() with the old markup (_NBRW_ENC = False) against the new one after the page's rebuild
      (_NBRW_REHYD, run alone in a page) — the normalized DOM is equal (the window, EN|DE, CSS see what they saw).
  A2  the BUILT file (not run) carries one saved output: the still preview (text/html, no button/script/style/
      var()/svg), opened in Lab not trusted light + dark, (--lite) Lite, nbconvert HTML: title + "Run this cell to
      start" visible, 0 buttons, contrast ≥ 4.5; the first run replaces it (no .nbstill among the run's outputs).
  A3  Python 3.9 (the kernel's install part run with a sys whose version_info is 3.9): no output in the notebook
      (v1.78: the box "Python 3.9 is out of support"), exactly one line on the kernel's console (sys.__stderr__).
  B3  the window's preview (_nbrw_cover) holds the account container as in Lab: details.nbrw-acct >
      .nbacct[data-where=reader] (JS fills it), summary in both languages.
  D   the start line (markdown) has no HTML entity (VS Code's outline showed "&#9654;&ensp;…" raw); no output of
      the run is an empty text/plain alone (VS Code draws each as a 33-px "…" row: v1.78 had 8); every widget
      output carries an empty text/html. --vscode (DIGICHEM_CODE_SERVER): in code-server the outline text and the
      output rows with height > 0 and no text under the window (want 0).
v1.78: red (A1 both languages + grey on grey in Lab dark; A2 no output; A3 box; B3 no container; D entities, 8 rows).
Owner: Python. exit 0 = REGRESS-PY-E33 OK."""
import sys, os, re, json, html as _h, shutil, socket, subprocess, tempfile, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "toolkit"))
from html.parser import HTMLParser

A = sys.argv[1:]
LITE, VSCODE = "--lite" in A, "--vscode" in A
SHOTS = A[A.index("--shots") + 1] if "--shots" in A else None
JOUT = A[A.index("--json") + 1] if "--json" in A else None
WMIME = "application/vnd.jupyter.widget-view+json"

PROBE = r'''
import json as _j33, html as _h33, re as _r33
def _t33(v):
    return " ".join(_r33.sub(r"<[^>]+>", " ", _h33.unescape(str(v))).split())
_pp33 = _nbrw_pairs()
_run33 = set(_t33(k) for k in _pp33 if k is not None)
_oth33 = set(_t33(v) for k, v in _pp33.items() if k is not None)
_tt33 = globals().get("_NBRW_TITLES") or {}
_ol33 = "de" if LANG["value"] == "en" else "en"
_oth33 |= set(_t33(x) for x in (_tt33.get(_ol33) or ()))
_run33 |= set(_t33(x) for x in (_tt33.get(LANG["value"]) or ()))
_oth33 = sorted(x for x in _oth33 if len(x) >= 10 and " " in x and x not in _run33)
_NBREAD["buf"] = _NBREAD.get("kept") or []
_new33 = _nbread_html()
_NBRW_ENC = False
_old33 = _nbread_html()
_NBRW_ENC = True
_cv33 = _nbrw_cover()
_NBREAD["buf"] = []
print("@@E33@@" + _j33.dumps({"other": _oth33, "new": _new33, "old": _old33, "cover": _cv33, "lang": LANG["value"],
                              "rehyd": globals().get("_NBRW_REHYD", "")}))
'''

def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

def probe(src):
    """A kernel of its own runs the cell and, in the SAME execution (the kept outputs are cleared when the next
    one begins), the probe: the other language's texts, the reading markup new and old, the window's cover."""
    from jupyter_client.manager import start_new_kernel
    nb = json.load(open(src))
    code = "".join(max((c for c in nb["cells"] if c["cell_type"] == "code"), key=lambda c: len("".join(c["source"])))["source"])
    env = {k: v for k, v in os.environ.items() if not k.startswith("DIGICHEM_")}
    km, kc = start_new_kernel(kernel_name="python3", env=env, cwd=os.path.dirname(src))
    try:
        mid = kc.execute(code + "\n" + PROBE); txt, err = [], []
        while True:
            m = kc.get_iopub_msg(timeout=900)
            if m["parent_header"].get("msg_id") != mid: continue
            t, c = m["msg_type"], m["content"]
            if t == "stream": txt.append(c["text"])
            elif t == "error": err.append(c["ename"] + ": " + c["evalue"])
            elif t == "status" and c["execution_state"] == "idle": break
    finally:
        km.shutdown_kernel(now=True)
    s = "".join(txt)
    if "@@E33@@" not in s:
        raise RuntimeError("probe: no answer %s" % err[:1])
    return json.loads(s.split("@@E33@@", 1)[1].strip().splitlines()[0])

def run_saved(src, dst):
    """Run the built file once and save it with its outputs (what a front end keeps)."""
    import nbformat
    from nbclient import NotebookClient
    nb = nbformat.read(src, as_version=4)
    keep = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("DIGICHEM_")}
    try:
        NotebookClient(nb, timeout=900, kernel_name="python3", resources={"metadata": {"path": os.path.dirname(dst)}}).execute()
    finally:
        os.environ.update(keep)
    info = probe(src)
    for c in nb.cells:
        if c.cell_type == "code":
            c.metadata["collapsed"] = False
            c.metadata.setdefault("jupyter", {})["outputs_hidden"] = False
    nbformat.write(nb, dst)
    return nb, info

# ---- a sanitizer like JupyterLab's (sanitize-html with Lab's lists, measured in jlab_core 4.6) ----------------
ALLOWED_TAGS = set("a abbr acronym address area article aside audio b bdi bdo big blockquote br button canvas caption "
                   "center cite code col colgroup colspan command data datalist dd del details dfn dir div dl dt em "
                   "fieldset figcaption figure font footer form h1 h2 h3 h4 h5 h6 header hgroup hr i img input ins kbd "
                   "label legend li map mark menu meter nav nobr ol optgroup option output p pre progress q rowspan s "
                   "samp section select small source span strike strong sub summary sup table tbody td textarea tfoot "
                   "th thead time tr track tt u ul var video wbr".split())
ALL_ATTR = set("class dir draggable hidden id inert itemprop itemref itemscope lang spellcheck style title translate".split())
TAG_ATTR = {"a": {"href", "name", "target", "rel"}, "img": {"src", "alt", "width", "height"}, "details": {"open"},
            "ol": {"start", "type", "reversed"}, "td": {"colspan", "rowspan"}, "th": {"colspan", "rowspan"},
            "input": {"type", "value", "placeholder", "disabled", "checked"}, "button": {"type", "disabled", "value"}}
DROP_WITH_TEXT = {"script", "style", "textarea", "option", "noscript"}
VOID = {"br", "hr", "img", "input", "wbr", "col", "area", "source", "track", "meta", "link"}

class _San(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False); self.out = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if self.skip or tag in DROP_WITH_TEXT:
            if tag not in VOID: self.skip += 1
            return
        if tag not in ALLOWED_TAGS: return
        keep = []
        for k, v in attrs:
            if v is None or v == "": continue                       # an empty attribute goes (hidden, open="")
            if k not in ALL_ATTR and k not in TAG_ATTR.get(tag, ()): continue
            if k == "style":
                v = ";".join(d for d in v.split(";") if d.strip() and "var(" not in d)
                if not v: continue
            keep.append('%s="%s"' % (k, _h.escape(v, quote=True)))
        self.out.append("<%s%s>" % (tag, "".join(" " + a for a in keep)))
    def handle_endtag(self, tag):
        if self.skip:
            if tag in DROP_WITH_TEXT or tag not in VOID: self.skip -= 1
            return
        if tag in ALLOWED_TAGS and tag not in VOID: self.out.append("</%s>" % tag)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
    def handle_data(self, d):
        if not self.skip: self.out.append(_h.escape(d, quote=False))
    def handle_entityref(self, n):
        if not self.skip: self.out.append("&%s;" % n)
    def handle_charref(self, n):
        if not self.skip: self.out.append("&#%s;" % n)

def sanitize(h):
    s = _San(); s.feed(h); s.close(); return "".join(s.out)

# ---- measurement in the page ----------------------------------------------------------------------------------
MEASURE = r"""([other, hostBg, rootSel, wants]) => {
  var lum = function(c){ var f = function(v){ v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
  var rgba = function(s){ var m = /rgba?\(([^)]+)\)/.exec(s || ''); if (!m) return [0,0,0,0];
    var p = m[1].split(/[ ,\/]+/).filter(Boolean).map(parseFloat); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
  var over = function(t, b){ var a = t[3]; return [t[0]*a + b[0]*(1-a), t[1]*a + b[1]*(1-a), t[2]*a + b[2]*(1-a), 1]; };
  var vis = function(e){ var w = e.ownerDocument.defaultView, b = e.getBoundingClientRect(), s = w.getComputedStyle(e);
    if (!(b.width > 0 && b.height > 0) || s.visibility === 'hidden' || +s.opacity === 0) return false;
    for (var x = e; x; x = x.parentElement) { var cs = w.getComputedStyle(x); if (cs.display === 'none' || +cs.opacity === 0) return false; }
    return true; };
  var host = rgba(hostBg);
  var bgOf = function(e){ var L = [];
    for (var x = e; x; x = x.parentElement) { var cs = x.ownerDocument.defaultView.getComputedStyle(x), c = rgba(cs.backgroundColor);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') { var m = /rgba?\([^)]+\)|#[0-9a-f]{3,8}/i.exec(cs.backgroundImage);
        if (m) { var t = document.createElement('i'); t.style.color = m[0]; document.body.appendChild(t);
                 c = rgba(getComputedStyle(t).color); t.remove(); } }
      if (c[3] > 0) L.push(c); if (c[3] >= 1) break; }
    var b = (L.length && L[L.length - 1][3] >= 1) ? L.pop() : host; while (L.length) b = over(L.pop(), b); return b; };
  var docs = [document].concat([].slice.call(document.querySelectorAll('iframe.out')).map(function(f){ return f.contentDocument; }).filter(Boolean));
  var R = {low: 0, minC: 99, lowEx: [], buttons: 0, text: '', n: 0};
  docs.forEach(function(d, di){
    if (!d.body || (di === 0 && docs.length > 1)) return;
    var roots = rootSel ? [].slice.call(d.querySelectorAll(rootSel)) : [d.body];
    roots.forEach(function(r){
      [].forEach.call(r.querySelectorAll('*'), function(e){
        if (/^(SCRIPT|STYLE)$/.test(e.tagName)) return;
        if (/^(BUTTON|INPUT|SELECT|TEXTAREA)$/.test(e.tagName) && vis(e)) R.buttons++;
        var own = [].filter.call(e.childNodes, function(n){ return n.nodeType === 3 && n.textContent.trim(); }).map(function(n){ return n.textContent; }).join(' ').trim();
        if (!own || !vis(e)) return;
        R.n++;
        var s = e.ownerDocument.defaultView.getComputedStyle(e), bg = bgOf(e), fg = over(rgba(s.color), bg);
        var c = (Math.max(lum(fg), lum(bg)) + 0.05) / (Math.min(lum(fg), lum(bg)) + 0.05);
        if (c < R.minC) R.minC = c;
        if (c < 4.5) { R.low++; if (R.lowEx.length < 4) R.lowEx.push(own.slice(0, 28) + ' ' + c.toFixed(2)); }
      });
      R.text += ' ' + (r.innerText || '');
    });
  });
  R.text = R.text.replace(/\s+/g, ' ');
  R.hits = other.filter(function(t){ return R.text.indexOf(t) >= 0; });
  var miss = (wants || []).filter(function(t){ return t && R.text.indexOf(t) < 0; });
  R.minC = Math.round(R.minC * 100) / 100;
  return {low: R.low, minC: R.minC, lowEx: R.lowEx, buttons: R.buttons, n: R.n, hits: R.hits.slice(0, 5), nhits: R.hits.length,
          chars: R.text.length, head: R.text.slice(0, 160), miss: miss}; }"""

def start_lab(root, theme):
    home = tempfile.mkdtemp(prefix="e33lab_")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("JUPYTER", "DIGICHEM"))}
    env.update(HOME=home, JUPYTER_DATA_DIR=home + "/data", JUPYTER_CONFIG_DIR=home + "/cfg",
               JUPYTER_RUNTIME_DIR=home + "/rt", IPYTHONDIR=home + "/ip")
    sd = home + "/cfg/lab/user-settings/@jupyterlab/apputils-extension"; os.makedirs(sd)
    json.dump({"theme": "JupyterLab Dark" if theme == "dark" else "JupyterLab Light"}, open(sd + "/themes.jupyterlab-settings", "w"))
    nd = home + "/cfg/lab/user-settings/@jupyterlab/apputils-extension"
    json.dump({"fetchNews": "false", "checkForUpdates": False}, open(nd + "/notification.jupyterlab-settings", "w"))
    port = free_port()
    p = subprocess.Popen([sys.executable, "-m", "jupyterlab", "--no-browser", "--port=%d" % port, "--ServerApp.token=",
                          "--ServerApp.password=", "--ServerApp.root_dir=" + root, "--allow-root"],
                         env=env, stdout=open(home + "/log", "w"), stderr=subprocess.STDOUT)
    base = "http://127.0.0.1:%d" % port
    for _ in range(240):
        try:
            urllib.request.urlopen(base + "/api/status", timeout=2); return p, base
        except Exception:
            time.sleep(0.5)
    p.terminate(); raise RuntimeError("lab did not start")

def open_nb(pg, url, reset=True):
    pg.goto(url + (("&" if "?" in url else "?") + "reset" if reset else ""))
    pg.wait_for_selector(".jp-NotebookPanel .jp-Cell", state="attached", timeout=120000)
    pg.wait_for_timeout(5000)
    trusted = pg.evaluate("() => document.querySelectorAll('.jp-OutputArea-output.jp-mod-trusted').length")
    return trusted

def shot(pg, name):
    if SHOTS:
        os.makedirs(SHOTS, exist_ok=True); pg.screenshot(path=os.path.join(SHOTS, name))

LAB_BG = {"light": "rgb(255,255,255)", "dark": "rgb(17,17,17)"}

def main():
    import nbpick
    src = os.path.abspath(nbpick.from_argv(sys.argv))
    rows, fails = [], []
    def row(name, ok, detail):
        rows.append((name, bool(ok), detail)); print("%-34s %s  %s" % (name, "ok " if ok else "RED", detail))
        if not ok: fails.append("%s: %s" % (name, detail))
    tmp = tempfile.mkdtemp(prefix="e33_")
    built = os.path.join(tmp, "built.ipynb"); saved = os.path.join(tmp, "saved.ipynb")
    shutil.copy(src, built)
    bnb = json.load(open(built))
    t0 = time.time()
    snb, info = run_saved(built, saved)
    print("run + probe %.1f s · run language %s · %d texts of the other language" % (time.time() - t0, info["lang"], len(info["other"])))
    other = info["other"]
    if len(other) < 20:
        row("PRE other-language texts", False, "BAD only %d texts of the other language from the kernel" % len(other))

    # ---- D (file + run) ---------------------------------------------------------------------------------------
    md = "".join(bnb["cells"][0]["source"])
    ents = re.findall(r"&#?\w+;", md)
    row("D1 start line without entities", not ents, "%d entities %s" % (len(ents), ents[:4]))
    outs = [o for c in snb.cells if c.cell_type == "code" for o in c.outputs if o.get("output_type") in ("display_data", "execute_result")]
    def nonempty(d, k):
        v = d.get(k); v = "".join(v) if isinstance(v, list) else v
        return v not in (None, "")
    plain_only = [i for i, o in enumerate(outs) if "text/plain" in o.get("data", {}) and
                  not any(k != "text/plain" for k in o["data"]) and not nonempty(o["data"], "text/plain")]
    w = [o for o in outs if WMIME in o.get("data", {})]
    wh = [o for o in w if "text/html" in o["data"] and not nonempty(o["data"], "text/html")]
    row("D2 no empty text/plain alone", not plain_only and w and len(wh) == len(w),
        "%d outputs · empty text/plain alone at %s · widget outputs %d, with empty text/html %d" % (len(outs), plain_only, len(w), len(wh)))

    # ---- A2 (file) -------------------------------------------------------------------------------------------
    co = [c for c in bnb["cells"] if c["cell_type"] == "code"]
    bo = co[0].get("outputs", []) if co else []
    sh = "".join((bo[0].get("data", {}) or {}).get("text/html", "")) if len(bo) == 1 else ""
    bad = [x for x in ("<button", "<script", "<style", "var(", "<svg", "<input") if x in sh]
    row("A2a file: one saved preview", len(bo) == 1 and "nbstill" in sh and "Run this cell to start" in sh and not bad,
        "%d outputs · %d chars · forbidden %s" % (len(bo), len(sh), bad))
    # Hauptwerkstatt E33 (merge): the element, not the word — css-E33's comment in 15-reader.css names ".nbstill" and
    # ships inside the reading output (behauptete bisher: the word "nbstill" only stands in the preview)
    still_after = sum('class="nbstill"' in "".join(o.get("data", {}).get("text/html", "")) for o in outs)
    row("A2b the run replaces it", still_after == 0 and len(outs) > 5, "preview among the run's outputs: %d of %d" % (still_after, len(outs)))
    title = re.sub(r"<[^>]+>", "", (bnb["metadata"].get("digichemjn") or {}).get("title") or "")

    # ---- A3 (kernel) ------------------------------------------------------------------------------------------
    try:
        row(*a3(snb))
    except Exception as e:
        row("A3 Python 3.9: no box, one line", False, "BAD %s" % str(e)[:160])

    # ---- B3 ---------------------------------------------------------------------------------------------------
    cv = info["cover"]
    m = re.search(r"<details class='nbrw-acct'>(.*?)</details>", cv, re.S)
    acc = m.group(1) if m else ""
    row("B3 account container in the window", bool(re.search(r"class='nbacct'[^>]*data-where='reader'", acc))
        and "data-nbrw-l='en'" in acc and "data-nbrw-l='de'" in acc,
        "details.nbrw-acct %s · .nbacct[data-where=reader] %s" % (bool(m), "data-where='reader'" in acc))

    from lab_keys import CHROME
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        # ---- R1 rebuild = v1.78 markup ----------------------------------------------------------------------
        pg = b.new_page()
        pg.set_content("<!doctype html><meta charset=utf-8><body><div id=o></div><div id=n></div></body>")
        r1 = pg.evaluate("""([o, n, js]) => {
            document.getElementById('o').innerHTML = o;
            var N = document.getElementById('n'); N.innerHTML = n;
            var s = document.createElement('script'); s.textContent = js.replace("document.currentScript", "window.__me");
            window.__me = (function(){ var x = document.createElement('i'); N.appendChild(x); return x; })();
            document.body.appendChild(s);
            var A = document.querySelector('#o .nbreading'), B = document.querySelector('#n .nbreading');
            if (!A || !B) return {bad: 'no .nbreading'};
            var rh = B.getAttribute('data-nbrw-rh'); B.removeAttribute('data-nbrw-rh');
            var a = A.outerHTML, bb = B.outerHTML, i = 0; while (i < a.length && a[i] === bb[i]) i++;
            return {rh: rh, same: a === bb, la: a.length, lb: bb.length, at: i, ctxA: a.slice(Math.max(0, i - 60), i + 80), ctxB: bb.slice(Math.max(0, i - 60), i + 80),
                    pairs: B.querySelectorAll('[data-nbrw-l][hidden]').length, cover: !!B.querySelector('.nbrw-cover'), rail: !!B.querySelector('template.nbrw-rail')}; }""",
            [info["old"], info["new"], info["rehyd"]])
        row("R1 rebuilt markup = v1.78 markup", r1.get("same") and r1.get("rh") == "1" and r1.get("pairs", 0) > 20,
            "equal %s · %d / %d chars · hidden pairs %s · cover %s · rail %s%s" % (r1.get("same"), r1.get("la", 0), r1.get("lb", 0),
            r1.get("pairs"), r1.get("cover"), r1.get("rail"), "" if r1.get("same") else " · first difference at %s: %r ≠ %r" % (r1.get("at"), r1.get("ctxA"), r1.get("ctxB"))))
        pg.close()

        # ---- A1 / A2 in JupyterLab, not trusted ------------------------------------------------------------
        root = os.path.join(tmp, "root"); os.makedirs(root)
        shutil.copy(saved, os.path.join(root, "saved.ipynb")); shutil.copy(built, os.path.join(root, "built.ipynb"))
        for theme in ("light", "dark"):
            proc, base = start_lab(root, theme)
            try:
                ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme=theme); pg = ctx.new_page()
                tr = open_nb(pg, base + "/lab/tree/saved.ipynb")
                r = pg.evaluate(MEASURE, [other, LAB_BG[theme], ".jp-NotebookPanel:not(.lm-mod-hidden) .jp-OutputArea-output", [title]])
                shot(pg, "E33-A1-lab-%s.png" % theme)
                judge("A1 Lab %s saved run" % theme, r, tr, row, want_text=title)
                pg.close(); pg = ctx.new_page()
                tr = open_nb(pg, base + "/lab/tree/built.ipynb")
                r = pg.evaluate(MEASURE, [[], LAB_BG[theme], ".jp-NotebookPanel:not(.lm-mod-hidden) .jp-OutputArea-output", [title, "Run this cell to start"]])
                shot(pg, "E33-A2-lab-%s.png" % theme)
                judge("A2 Lab %s built file" % theme, r, tr, row, want_text="Run this cell to start", title=title)
                ctx.close()
            finally:
                proc.terminate()

        # ---- A1 / A2 in JupyterLite (saved outputs need no kernel) -------------------------------------------
        if LITE:
            lite(b, tmp, saved, built, other, title, row)
        else:
            print("A1/A2 Lite: not asked (--lite)")

        # ---- A1 PyCharm rebuilt with a sanitizer --------------------------------------------------------------
        for theme in ("light", "dark"):
            bg, ink = ("#2b2d30", "#dfe1e5") if theme == "dark" else ("#ffffff", "#1f2328")
            fr = []
            for o in outs:
                d = o.get("data", {})
                hh = "".join(d.get("text/html", "")) if "text/html" in d else ""
                if not hh and "text/plain" in d:
                    t = "".join(d["text/plain"]); hh = "<pre>%s</pre>" % _h.escape(t) if t else ""
                doc = ("<!doctype html><meta charset=utf-8><body style='margin:0;background:%s;color:%s;font:13px sans-serif'>%s"
                       % (bg, ink, sanitize(hh)))
                fr.append("<iframe class='out' style='display:block;width:100%%;border:0;height:40px' srcdoc=\"%s\"></iframe>"
                          % _h.escape(doc, quote=True))
            page = ("<!doctype html><meta charset=utf-8><body style='margin:0;padding:8px 16px;background:%s'>%s</body>" % (bg, "".join(fr)))
            ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme=theme); pg = ctx.new_page()
            pg.set_content(page); pg.wait_for_timeout(1500)
            pg.evaluate("() => document.querySelectorAll('iframe.out').forEach(function(f){ var d = f.contentDocument; if (d && d.documentElement) f.style.height = Math.max(1, d.documentElement.scrollHeight) + 'px'; })")
            pg.wait_for_timeout(500)
            r = pg.evaluate(MEASURE, [other, "rgb(%d,%d,%d)" % tuple(int(bg[i:i + 2], 16) for i in (1, 3, 5)), None, [title]])
            shot(pg, "E33-A1-pycharm-sanitized-%s.png" % theme)
            judge("A1 PyCharm+sanitizer %s" % theme, r, 0, row, want_text=title)
            ctx.close()

        # ---- A2 nbconvert (GitHub / nbviewer preview) --------------------------------------------------------
        out = os.path.join(tmp, "built.html")
        subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "html", built, "--output", out], capture_output=True)
        ctx = b.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page()
        pg.route("**/*", lambda rt: rt.abort() if rt.request.resource_type == "script" else rt.continue_())
        pg.goto("file://" + out); pg.wait_for_timeout(800)
        r = pg.evaluate(MEASURE, [[], "rgb(255,255,255)", ".jp-OutputArea-output, .output_area", [title, "Run this cell to start"]])
        shot(pg, "E33-A2-nbconvert.png")
        judge("A2 nbconvert built file", r, 0, row, want_text="Run this cell to start", title=title)
        ctx.close()

        if VSCODE:
            vscode(b, built, saved, row)
        b.close()

    print("\n".join("%-34s %s  %s" % (n, "ok " if ok else "RED", d) for n, ok, d in rows))
    if JOUT: json.dump([{"row": n, "ok": ok, "detail": d} for n, ok, d in rows], open(JOUT, "w"), ensure_ascii=False, indent=1)
    print("REGRESS-PY-E33 OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
    sys.exit(1 if fails else 0)

def judge(name, r, trusted, row, want_text=None, title=None):
    """Not trusted (no trusted output), 0 texts of the other language, contrast ≥ 4.5, 0 buttons, the wanted texts seen."""
    ok = r["nhits"] == 0 and r["low"] == 0 and r["buttons"] == 0 and r["n"] > 0 and not r["miss"]
    row(name, ok and not trusted, "trusted outputs %d · other language %d %s · contrast min %.2f (%d below 4.5 %s) · buttons %d · "
        "%d text elements · missing %s · %r" % (trusted, r["nhits"], r["hits"][:3], r["minC"], r["low"], r["lowEx"][:3],
                                               r["buttons"], r["n"], r["miss"], r["head"][:90]))

def a3(snb):
    """The kernel's install part with sys.version_info = 3.9: outputs and console lines."""
    from shortcell import expand
    from jupyter_client.manager import start_new_kernel
    code = expand("".join(max((c for c in snb.cells if c.cell_type == "code"), key=lambda c: len(c.source)).source))
    i, j = code.find("def _nb_say("), code.find("_NB_MISSING = [")
    if i < 0 or j < 0:
        return ("A3 Python 3.9: no box, one line", False, "BAD install part not found (def _nb_say … _NB_MISSING)")
    part = code[i:j]
    k0 = code.find("_NB_MIN_PY, _NB_OK_PY")
    head = code[k0:code.find("\n", k0)] if k0 >= 0 else "_NB_MIN_PY, _NB_OK_PY = (3, 9), (3, 10)"
    pre = ("import io as _io33, types as _ty33, sys as _sys33\n"
           "_fs33 = _ty33.SimpleNamespace(version_info=(3, 9, 18, 'final', 0), __stderr__=_io33.StringIO(), modules=_sys33.modules)\n"
           "def _nb_stop(): raise SystemExit\n")
    part = part.replace('__import__("sys")', "_fs33")
    km, kc = start_new_kernel(kernel_name="python3")
    try:
        mid = kc.execute(pre + head + "\n" + part + "\nprint('@@A3@@' + repr(_fs33.__stderr__.getvalue()))")
        disp, txt, err = [], [], []
        while True:
            m = kc.get_iopub_msg(timeout=120)
            if m["parent_header"].get("msg_id") != mid: continue
            t, c = m["msg_type"], m["content"]
            if t in ("display_data", "execute_result"): disp.append(c["data"].get("text/html") or c["data"].get("text/plain") or "")
            elif t == "stream": txt.append(c["text"])
            elif t == "error": err.append(c["ename"] + ": " + c["evalue"])
            elif t == "status" and c["execution_state"] == "idle": break
    finally:
        km.shutdown_kernel(now=True)
    s = "".join(txt); con = eval(s.split("@@A3@@", 1)[1].strip()) if "@@A3@@" in s else ""
    lines = [l for l in con.splitlines() if l.strip()]
    ok = not disp and not err and len(lines) == 1 and "3.9" in lines[0]
    return ("A3 Python 3.9: no box, one line", ok, "outputs in the notebook %d %r · console lines %d %r · errors %s"
            % (len(disp), re.sub(r"<[^>]+>", " ", disp[0])[:80] if disp else "", len(lines), lines[:1], err[:1]))

def lite(b, tmp, saved, built, other, title, row):
    """A JupyterLite site per theme (jupyterlite-core, overrides.json sets the theme), the two files in its contents;
    saved outputs show without a kernel (Pyodide is not reachable here — not needed to open a file)."""
    files = os.path.join(tmp, "litefiles"); os.makedirs(files)
    shutil.copy(saved, os.path.join(files, "saved.ipynb")); shutil.copy(built, os.path.join(files, "built.ipynb"))
    for theme in ("light", "dark"):
        lroot = os.path.join(tmp, "lite-" + theme); site = os.path.join(lroot, "site"); os.makedirs(lroot)
        json.dump({"@jupyterlab/apputils-extension:themes": {"theme": "JupyterLab Dark" if theme == "dark" else "JupyterLab Light"},
                   "@jupyterlab/apputils-extension:notification": {"fetchNews": "false", "checkForUpdates": False}},
                  open(os.path.join(lroot, "overrides.json"), "w"))
        r = subprocess.run([sys.executable, "-m", "jupyter", "lite", "build", "--contents", files, "--output-dir", site],
                           capture_output=True, text=True, cwd=lroot, timeout=600)
        if r.returncode or not os.path.exists(os.path.join(site, "lab", "index.html")):
            row("A1 Lite %s" % theme, False, "BAD no Lite site (jupyterlite-core): %s" % (r.stderr or r.stdout)[-200:]); continue
        port = free_port()
        srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1", "--directory", site],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.5)
        try:
            for f, oth, want in (("saved.ipynb", other, title), ("built.ipynb", [], "Run this cell to start")):
                ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme=theme); pg = ctx.new_page()
                tr = open_nb(pg, "http://127.0.0.1:%d/lab/index.html?path=%s" % (port, f), reset=False)
                if pg.query_selector(".jp-Dialog"): pg.keyboard.press("Escape"); pg.wait_for_timeout(800)
                th = pg.evaluate("() => document.body.getAttribute('data-jp-theme-name')")
                r = pg.evaluate(MEASURE, [oth, LAB_BG[theme], ".jp-NotebookPanel:not(.lm-mod-hidden) .jp-OutputArea-output", [title, want]])
                tag = "A1" if f == "saved.ipynb" else "A2"
                shot(pg, "E33-%s-lite-%s.png" % (tag, theme))
                judge("%s Lite %s (%s)" % (tag, theme, th), r, tr, row)
                ctx.close()
        finally:
            srv.terminate()

def vscode(b, built, saved, row):
    cs = os.environ.get("DIGICHEM_CODE_SERVER") or shutil.which("code-server")
    if not cs:
        row("D VS Code", False, "BAD no code-server (DIGICHEM_CODE_SERVER)"); return
    from env_vscode import open_file
    root = tempfile.mkdtemp(prefix="e33vsc_"); ws = os.path.join(root, "ws"); os.makedirs(ws)
    shutil.copy(saved, os.path.join(ws, "saved.ipynb")); shutil.copy(built, os.path.join(ws, "built.ipynb"))
    ud, ext = os.path.join(root, "ud"), os.path.join(root, "ext"); os.makedirs(os.path.join(ud, "User"))
    json.dump({"security.workspace.trust.enabled": False, "workbench.startupEditor": "none", "workbench.colorTheme": "Default Light Modern",
               "update.mode": "none", "telemetry.telemetryLevel": "off", "chat.disableAIFeatures": True}, open(os.path.join(ud, "User", "settings.json"), "w"))
    port = free_port(); url = "http://127.0.0.1:%d/?folder=%s" % (port, ws)
    srv = subprocess.Popen([cs, "--auth", "none", "--bind-addr", "127.0.0.1:%d" % port, "--user-data-dir", ud, "--extensions-dir", ext,
                            "--disable-telemetry", "--disable-update-check", "--disable-workspace-trust", ws],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(4)
    try:
        for f in ("saved.ipynb", "built.ipynb"):
            ctx = b.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page()
            open_file(pg, url, f); pg.wait_for_timeout(9000)
            bc = pg.evaluate("() => { var e = document.querySelector('.breadcrumbs-control'); return e ? e.innerText : '' }") or ""
            for _ in range(60):
                pg.mouse.move(700, 600); pg.mouse.wheel(0, 3000); pg.wait_for_timeout(100)
            pg.wait_for_timeout(1500)
            info = None
            for fr in pg.frames:
                try:
                    if fr.evaluate("() => !!document.querySelector('.output_container')"):
                        info = fr.evaluate("""() => { var o = [...document.querySelectorAll('.output_container')];
                          return {n: o.length, empty: o.filter(e => e.getBoundingClientRect().height > 0 && !(e.innerText || '').trim()).length,
                                  run: (document.body.innerText || '').indexOf('Run this cell to start') >= 0,
                                  text: (document.body.innerText || '').replace(/\\s+/g, ' ').slice(0, 200)}; }""")
                except Exception:
                    pass
            shot(pg, "E33-D-vscode-%s.png" % f.split(".")[0])
            if f == "saved.ipynb":
                row("D VS Code outline + rows", info and info["empty"] == 0 and "&#" not in bc and "&ensp;" not in bc,
                    "outline %r · outputs %s · empty rows %s" % (bc.replace("\n", " ")[:70], info and info["n"], info and info["empty"]))
            else:
                row("A2 VS Code built file", bool(info) and info.get("run"),
                    "outputs %s · %r" % (info and info["n"], (info or {}).get("text", "")[:100]))
            ctx.close()
    finally:
        srv.terminate()

if __name__ == "__main__":
    main()
