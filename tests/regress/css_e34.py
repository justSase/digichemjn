"""E34 · CSS — Werkstatt CSS, 19.10. (Nutzer: die Notebooks sollen zur digi-Webseite und zur digi App passen,
„Standardstil“; Auftrag plan/AUFTRAG.md C1–C3). Der Stil „digi“ im echten Browser, nach Run All und Play:

    python3 tests/regress/css_e34.py [notebook.ipynb] [--env lab,nb7,lite] [--themes light,dark] [--lite-site DIR]
                                     [--shots DIR] [--strict] [--json out.json]

Lite: ohne --lite-site (oder DIGICHEM_LITE_SITE, deren files/v.ipynb dann das geprüfte Notebook sein muss) baut der
Test seine Seite selbst — ohne Netz zur Laufzeit: Pyodide 314.0.6 aus einem lokalen Tarball (DIGICHEM_PYODIDE, sonst
einmal von den GitHub-Releases nach ~/.cache/digichemjn/), ipywidgets/jupyterquiz als lokale Wheels.

Je Umgebung (JupyterLab · Notebook 7 · JupyterLite) × hell/dunkel, 1400 × 900, frisches Profil:
  S0   der Stil ist digi: body.nbskin-digi (Profil frisch, nur hell/dunkel als Wahl des Lesers gesetzt). Ohne die JS-Hälfte (J1: Erststart → digi) setzt der Test die Klasse als
       Stand-in (die Zeile sagt es); mit --strict ist ein Stand-in rot (nach dem Zusammenführen).
  R1   Akzent der Rail = Gold: --nbmark am Panel und Fläche + Leuchten der Marke, an der der Leser steht (.here), sind Gold
       (Farbton 36–52°, Sättigung ≥ 0,6, Helligkeit 0,45–0,85).
  R2   Formen: Titelkarte des Dokuments und des Covers Radius 14 px mit 1-px-Linie; Kapitel-Pille Radius ≥ 999 px.
  R3   Überschriften: font-family von Titel und Kapitel-Pille beginnt mit Unbounded; eine FontFace „Unbounded“
       ist geladen (status loaded) und zeichnet anders als der Ersatz (Canvas-Breite) — document.fonts.check
       allein ist wahr auch ohne jede Schrift dieses Namens und zählt darum nicht.
  R4   Kontrast: jeder sichtbare Text auf dem Schirm (Notebook mit Panel; R4b weiter unten, R4c Einstellungen ⚙ offen) ≥ 4,5 : 1 gegen seinen Grund — der ungünstigste Punkt von
       Farbe und Verläufen des ersten deckenden Vorfahren (Textur der Seite eingeschlossen), Deckkraft eingerechnet.
  R6   (Korrektur E34) dunkel: jede sichtbare Fläche — Hintergrundfarbe und jeder Verlaufsstopp, auch ::before/::after —
       ist eine Farbe der Palette ± 2 je Kanal (Transparenz erlaubt; Weiß nur als Linie bis Alpha 0,2); auf dem Cover
       (R6v), oben und weiter unten im Dokument (R6) und in den Einstellungen (R6c).
  R5   0 Netzanfragen für Schriften (resource type font, außer data: und den Schriften, die das Frontend selbst
       mitbringt, z. B. Font Awesome unter /static/) und 0 Anfragen an fremde Hosts.
Gegenprobe v1.79 (e5c61dbb, Vorlage, mit Stand-in): rot in R1, R2, R3 (Chronik). exit 0 = REGRESS-CSS-E34 OK."""
import sys, os, json, time, shutil, tempfile, subprocess, socket, urllib.request, urllib.parse, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from playwright.sync_api import sync_playwright

CHROME = os.environ.get("DIGICHEM_CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
A = sys.argv[1:]
def opt(k, d=None):
    return A[A.index(k) + 1] if k in A else d
SHOTS, JOUT, STRICT = opt("--shots"), opt("--json"), "--strict" in A
ENVS = opt("--env", "lab,nb7,lite").split(",")
THEMES = opt("--themes", "light,dark").split(",")
LITE = opt("--lite-site") or os.environ.get("DIGICHEM_LITE_SITE")
PYV = "314.0.6"                       # the Pyodide jupyterlite-pyodide-kernel 0.8.6 expects (constants.PYODIDE_VERSION)

def build_lite(src, tmp):
    """A JupyterLite site that runs WITHOUT the network: Pyodide from a local tarball (DIGICHEM_PYODIDE = path, else
    ~/.cache/digichemjn/pyodide-<v>.tar.bz2, fetched once from the GitHub release), the notebook's own pip packages
    as local wheels (piplite), the front end's extensions from wherever pip put them (sys.prefix may be /usr while
    they live in /usr/local). Returns the site directory or raises."""
    tb = os.environ.get("DIGICHEM_PYODIDE") or os.path.join(os.path.expanduser("~"), ".cache", "digichemjn", "pyodide-%s.tar.bz2" % PYV)
    if not os.path.isfile(tb):
        os.makedirs(os.path.dirname(tb), exist_ok=True)
        url = "https://github.com/pyodide/pyodide/releases/download/%s/pyodide-%s.tar.bz2" % (PYV, PYV)
        subprocess.run(["curl", "-sSfL", "-o", tb + ".part", url], check=True, timeout=1200); os.rename(tb + ".part", tb)
    lite = os.path.join(tmp, "lite"); files = os.path.join(lite, "files"); wh = os.path.join(lite, "wheels")
    os.makedirs(files); os.makedirs(wh); shutil.copy(src, os.path.join(files, "v.ipynb"))
    subprocess.run([sys.executable, "-m", "pip", "download", "--no-deps", "-q", "-d", wh, "ipywidgets", "jupyterquiz", "comm",
                    "widgetsnbextension", "jupyterlab_widgets"], check=True, timeout=600)
    import jupyter_core.paths as jp
    ext = [d for d in jp.jupyter_path("labextensions") if os.path.isdir(d)]
    json.dump({"FederatedExtensionAddon": {"extra_labextensions_path": ext}}, open(os.path.join(lite, "jupyter_lite_config.json"), "w"))
    cmd = [sys.executable, "-m", "jupyter", "lite", "build", "--contents", files, "--output-dir", os.path.join(lite, "site"), "--pyodide", tb]
    for w in sorted(os.listdir(wh)): cmd += ["--piplite-wheels", os.path.join(wh, w)]
    r = subprocess.run(cmd, cwd=lite, capture_output=True, text=True, timeout=1500)
    site = os.path.join(lite, "site")
    if r.returncode or not os.path.isfile(os.path.join(site, "lab", "index.html")):
        raise RuntimeError("jupyter lite build: %s" % (r.stderr or r.stdout)[-300:])
    cfg = json.load(open(os.path.join(site, "jupyter-lite.json")))["jupyter-config-data"]
    if not any("pyodide-kernel" in e["name"] for e in cfg.get("federated_extensions", [])):
        raise RuntimeError("the Lite site has no Pyodide kernel (federated extensions %s)" % ext)
    return site
W, H = 1400, 900

def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p

def start_server(kind, root, theme):
    """JupyterLab or Notebook 7 with its own HOME; the front end's theme is the reader's (E15.3)."""
    home = tempfile.mkdtemp(prefix="e34_%s_" % kind)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("JUPYTER", "DIGICHEM"))}
    env.update(HOME=home, JUPYTER_DATA_DIR=home + "/data", JUPYTER_CONFIG_DIR=home + "/cfg",
               JUPYTER_RUNTIME_DIR=home + "/rt", IPYTHONDIR=home + "/ip")
    sd = home + "/cfg/lab/user-settings/@jupyterlab/apputils-extension"; os.makedirs(sd)
    json.dump({"theme": "JupyterLab Dark" if theme == "dark" else "JupyterLab Light"}, open(sd + "/themes.jupyterlab-settings", "w"))
    json.dump({"fetchNews": "false", "checkForUpdates": False}, open(sd + "/notification.jupyterlab-settings", "w"))
    port = free_port()
    mod = "jupyterlab" if kind == "lab" else "notebook"
    p = subprocess.Popen([sys.executable, "-m", mod, "--no-browser", "--port=%d" % port, "--ServerApp.token=",
                          "--ServerApp.password=", "--ServerApp.root_dir=" + root, "--allow-root"],
                         env=env, stdout=open(home + "/log", "w"), stderr=subprocess.STDOUT)
    base = "http://127.0.0.1:%d" % port
    for _ in range(240):
        try:
            urllib.request.urlopen(base + "/api/status", timeout=2); return p, base
        except Exception:
            time.sleep(0.5)
    p.terminate(); raise RuntimeError("%s did not start" % kind)

def palette(pg, label):
    """A command by its palette label (Lab, NB7 and Lite all have Ctrl+Shift+C). Never types into the notebook."""
    if pg.query_selector(".jp-Dialog"):
        pg.keyboard.press("Escape"); pg.wait_for_timeout(600)
    try:
        pg.click(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-NotebookPanel-toolbar", position={"x": 5, "y": 5}, timeout=3000)
    except Exception:
        pass
    pg.keyboard.press("Escape"); pg.keyboard.press("Control+Shift+C")
    try:
        pg.wait_for_function("() => { var i = document.activeElement; return !!(i && i.classList && i.classList.contains('lm-CommandPalette-input')); }", timeout=8000)
        pg.fill(".lm-CommandPalette-input", label)
        pg.wait_for_function("(l) => { var a = document.querySelector('.lm-CommandPalette-item.lm-mod-active .lm-CommandPalette-itemLabel'); return !!(a && a.textContent.trim() === l); }", arg=label, timeout=8000)
    except Exception:
        pg.keyboard.press("Escape"); return False
    pg.keyboard.press("Enter"); return True

COVER_UP = """() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var c = P && P.querySelector('.nbcover-out[data-nbcov]'), p = c && c.querySelector('.nbcover-play');
  return !!(p && p.getBoundingClientRect().width > 2); }"""

def run_and_play(pg, lite=False):
    for attempt in range(3):
        palette(pg, "Run All Cells")
        try:
            pg.wait_for_selector("#nbpanel-root .nbmap", state="attached", timeout=600000 if lite else 90000); break
        except Exception:
            if attempt == 2: return "BAD no panel after Run All"
    for _ in range(int(240 if lite else 90)):
        pg.wait_for_timeout(1000)
        st = pg.evaluate("() => (document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook-ExecutionIndicator, .jp-Notebook-ExecutionIndicator')||{getAttribute:()=>null}).getAttribute('data-status')")
        if st in ("idle", None): break
    pg.wait_for_timeout(2500)
    for _ in range(12):
        if pg.evaluate(COVER_UP): break
        pg.wait_for_timeout(250)
    return "ok"

def play(pg):
    if not pg.evaluate(COVER_UP): return "none"
    xy = pg.evaluate("""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
      var p = P.querySelector('.nbcover-out[data-nbcov] .nbcover-play'); p.scrollIntoView({block: 'center'});
      var r = p.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }""")
    pg.wait_for_timeout(200); pg.mouse.click(*xy)
    for _ in range(40):
        pg.wait_for_timeout(250)
        if not pg.evaluate(COVER_UP) and not pg.evaluate("() => !!document.querySelector('#nbload:not(.nbload-out)')"): break
    pg.wait_for_timeout(1500)
    return "play" if not pg.evaluate(COVER_UP) else "BAD the cover stayed after Play"

STAND = """(strict) => { var b = document.body, had = b.classList.contains('nbskin-digi');
  if (!had && !strict) { b.classList.add('nbskin-digi'); window.__e34stand = true; }
  return {had: had, cls: b.className, theme: b.getAttribute('data-jp-theme-light'), dark: b.classList.contains('nbdark')}; }"""
# a stand-in survives a re-apply of the skin by the script (it only toggles the skins it knows)
KEEP = """() => { if (window.__e34stand && !document.body.classList.contains('nbskin-digi')) document.body.classList.add('nbskin-digi'); }"""

COLOR_LIB = r"""
  var cv = document.createElement('canvas').getContext('2d');
  function rgba(s){ var m = /rgba?\(([^)]+)\)/.exec(s || ''); if (!m) return null;
    var p = m[1].split(/[ ,\/]+/).filter(Boolean).map(parseFloat); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
  function norm(c){ var m = /^color\(srgb ([^)]+)\)/.exec(c);
    if (m) { var q = m[1].split(/[ \/]+/).filter(Boolean).map(parseFloat); return [q[0]*255, q[1]*255, q[2]*255, q.length > 3 ? q[3] : 1]; }
    if (/^rgba?\(/.test(c || '')) return rgba(c);
    if (!c || c === 'transparent') return [0, 0, 0, 0];
    cv.fillStyle = '#000'; cv.fillStyle = c; var v = cv.fillStyle;   // canvas → #rrggbb or rgba()
    if (v[0] === '#') return [parseInt(v.slice(1,3),16), parseInt(v.slice(3,5),16), parseInt(v.slice(5,7),16), 1];
    return rgba(v); }
  function over(t, b){ var a = t[3]; return [t[0]*a + b[0]*(1-a), t[1]*a + b[1]*(1-a), t[2]*a + b[2]*(1-a), 1]; }
  function lum(c){ var f = function(v){ v /= 255; return v <= .03928 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); };
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2]); }
  function ratio(a, b){ var x = lum(a), y = lum(b); return (Math.max(x, y) + .05) / (Math.min(x, y) + .05); }
  function hsl(c){ var r = c[0]/255, g = c[1]/255, b = c[2]/255, mx = Math.max(r,g,b), mn = Math.min(r,g,b), l = (mx+mn)/2, h = 0, s = 0;
    if (mx !== mn) { var d = mx - mn; s = l > .5 ? d / (2 - mx - mn) : d / (mx + mn);
      h = mx === r ? (g - b) / d + (g < b ? 6 : 0) : mx === g ? (b - r) / d + 2 : (r - g) / d + 4; h *= 60; }
    return [Math.round(h), Math.round(s * 100) / 100, Math.round(l * 100) / 100]; }
  function stops(img){ return (img || '').match(/rgba?\([^)]+\)|color\(srgb[^)]+\)|#[0-9a-fA-F]{3,8}\b/g) || []; }
  function gold(c){ var q = hsl(c); return q[0] >= 36 && q[0] <= 52 && q[1] >= .6 && q[2] >= .45 && q[2] <= .85; }
  function hex(c){ return '#' + c.slice(0,3).map(function(v){ return ('0' + Math.round(v).toString(16)).slice(-2); }).join(''); }
"""

MEASURE = r"""(only) => {""" + COLOR_LIB + r"""
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), R = {};
  var root = document.getElementById('nbpanel-root');
  // R1 — the rail's accent
  var mk = root ? getComputedStyle(root).getPropertyValue('--nbmark').trim() : '';
  // the mark the reader is at (.here): its face and its glow are the accent
  var here = root && root.querySelector('.nbmap-node.here :is(.nbsect,.nbrail-dot,.nbchapdot,.nbsubdot,.nbvizmark,.nbcodemark)');
  var hs = here ? getComputedStyle(here) : null;
  var curImg = hs ? hs.backgroundColor + ' ' + hs.boxShadow : '';
  var cs = stops(curImg).map(norm).filter(function(c){ return c && c[3] > .3; });
  R.r1 = {mark: mk, markHsl: mk ? hsl(norm(mk)) : null, markGold: !!mk && gold(norm(mk)),
          here: here ? here.className.split(' ')[0] : null, cursor: cs.map(hex), img: curImg.slice(0, 120), cursorGold: cs.length > 0 && cs.every(gold)};
  // R2 — shapes
  var px = function(e, k){ return e ? parseFloat(getComputedStyle(e)[k]) : null; };
  var card = P.querySelector('.nbtitle:not(:has(>.nbcover)) .nbtitle-card') || P.querySelector('.nbtitle-card');
  var pill = P.querySelector('.acc-chapter>.jupyter-widget-Collapse>.jupyter-widget-Collapse-header, .acc-chapter>.lm-Collapse>.lm-Collapse-header');
  R.r2 = {card: card ? [px(card, 'borderTopLeftRadius'), px(card, 'borderTopWidth'), getComputedStyle(card).borderTopStyle] : null,
          pill: pill ? px(pill, 'borderTopLeftRadius') : null};
  // R3 — the heading face
  var fam = function(e){ return e ? getComputedStyle(e).fontFamily : ''; };
  var t = P.querySelector('.nbtitle:not(:has(>.nbcover)) .nbtitle-h') || P.querySelector('.nbtitle-h');
  var pt = pill ? (pill.querySelector('.jupyter-widget-Collapse-header-text, span, div') || pill) : null;
  var faces = []; document.fonts.forEach(function(f){ faces.push([f.family.replace(/["']/g, ''), f.weight, f.status]); });
  var unb = faces.filter(function(f){ return f[0] === 'Unbounded'; });
  cv.font = '400 40px Unbounded, monospace'; var w1 = cv.measureText('Notebook title Äß').width;
  cv.font = '400 40px monospace'; var w0 = cv.measureText('Notebook title Äß').width;
  R.r3 = {title: fam(t).slice(0, 60), pill: fam(pt).slice(0, 60), faces: unb,
          loaded: unb.some(function(f){ return f[2] === 'loaded'; }), check: document.fonts.check('400 20px Unbounded'),
          drawn: Math.abs(w1 - w0) > 2, w: [Math.round(w1), Math.round(w0)]};
  // R4 — every visible text against the worst point of its ground
  var vis = function(e){ var r = e.getBoundingClientRect(); if (r.width < 1 || r.height < 1) return false;
    if (r.right < 0 || r.bottom < 0 || r.left > innerWidth || r.top > innerHeight) return false;   // on the screen
    var s = getComputedStyle(e); return s.visibility !== 'hidden' && s.display !== 'none'; };
  var ground = function(e){ var stack = [], op = 1;
    for (var a = e; a && a.nodeType === 1; a = a.parentElement) {
      var s = getComputedStyle(a); op *= parseFloat(s.opacity) || 1;
      var bc = norm(s.backgroundColor), img = s.backgroundImage !== 'none' ? stops(s.backgroundImage).map(norm).filter(Boolean) : [];
      if ((bc && bc[3] > 0) || img.length) stack.push({bc: bc, img: img, el: a});
      if (bc && bc[3] >= .99) break; }
    var base = [255, 255, 255, 1], c = [base];
    for (var i = stack.length - 1; i >= 0; i--) {
      var L = stack[i], nc = [];
      // a gradient whose every stop is opaque covers what lies under it: only its stops are ground
      var cover = L.img.length && L.img.every(function(g){ return g[3] >= .99; });
      c.forEach(function(b){ var b2 = L.bc && L.bc[3] > 0 ? over(L.bc, b) : b; if (!cover) nc.push(b2);
        L.img.forEach(function(g){ nc.push(over(g, b2)); }); });
      c = nc.slice(0, 64); }
    return {cands: c, op: op}; };
  // what the reader sees of the notebook: its panel, our panel (rail, dock, drawer), our pop-ups — not the Lab around it;
  // with a window open (only = '.nbdrawer') just that window: the rest lies under its veil
  var out = [], seen = 0, els = [];
  (only ? [].slice.call(document.querySelectorAll(only)) : [P, root].concat([].slice.call(document.querySelectorAll('.nbhelp,.nbtip'))))
    .forEach(function(sc){ if (sc) els = els.concat([].slice.call(sc.querySelectorAll('*'))); });
  els = els.filter(function(e, i){ return els.indexOf(e) === i; });
  for (var i = 0; i < els.length; i++) {
    var e = els[i]; if (/^(SCRIPT|STYLE|SVG|PATH|CANVAS|IMG|INPUT|TEXTAREA|SELECT|OPTION|MJX-CONTAINER)$/i.test(e.tagName)) continue;
    if (e.closest('svg,mjx-container,.MathJax,.jp-InputArea,.cm-editor,[aria-hidden=true]')) continue;
    var own = ''; for (var n = e.firstChild; n; n = n.nextSibling) if (n.nodeType === 3) own += n.nodeValue;
    if (!/[A-Za-zÄÖÜäöüß0-9]/.test(own) || !vis(e)) continue;
    var s = getComputedStyle(e), fg = norm(s.color); if (!fg || fg[3] < .05) continue;   // no ink at all: not text anyone reads
    var g = ground(e), worst = 99, wb = null;
    g.cands.forEach(function(b){ var f = over([fg[0], fg[1], fg[2], fg[3] * g.op], b), r = ratio(f, b); if (r < worst) { worst = r; wb = b; } });
    seen++;
    if (worst < 4.5) out.push({t: own.trim().slice(0, 40), c: Math.round(worst * 100) / 100, fg: hex(fg), bg: wb ? hex(wb) : null,
                               el: e.tagName + '.' + String(e.className).split(' ').slice(0, 2).join('.')}); }
  out.sort(function(a, b){ return a.c - b.c; });
  var uniq = {}, u = []; out.forEach(function(o){ var k = o.el + o.fg + o.bg; if (!uniq[k]) { uniq[k] = 1; u.push(o); } });
  R.r4 = {n: seen, low: out.length, worst: u.slice(0, 10)};
  return R; }"""

# R6 (Korrektur E34, Nutzer 19.10.: „alle Felder passend eingefärbt“) — dunkel: jede sichtbare Fläche (Hintergrundfarbe
# und jeder Stopp eines Verlaufs) ist eine Farbe der Palette (± 2 je Kanal); Transparenz ist erlaubt (Alpha 0, oder
# eine Palettenfarbe mit Alpha); Weiß nur durchscheinend bis Alpha 0,2 (die Linie #ffffff1c).
PALETTE = ["#05060c", "#0b0e1c", "#10142a", "#e9ecf6", "#c3c9de", "#8a91aa",
           "#ffd36b", "#7fb4ff", "#ff7bd5", "#6be3a0", "#ff6b7a"]
PAL = r"""([pal, only]) => {""" + COLOR_LIB + r"""
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), root = document.getElementById('nbpanel-root');
  var allow = pal.map(norm), bad = {}, n = 0;
  var ok = function(c){ if (!c || c[3] < .01) return true;
    if (c[0] > 252 && c[1] > 252 && c[2] > 252) return c[3] <= .2;          // white: only as the line
    return allow.some(function(a){ return Math.abs(a[0]-c[0]) <= 2 && Math.abs(a[1]-c[1]) <= 2 && Math.abs(a[2]-c[2]) <= 2; }); };
  var els = [];
  (only ? [].slice.call(document.querySelectorAll(only)) : [P, root].concat([].slice.call(document.querySelectorAll('.nbhelp,.nbtip'))))
    .forEach(function(sc){ if (sc) els = els.concat([sc], [].slice.call(sc.querySelectorAll('*'))); });
  els.forEach(function(e){ if (e.closest('svg,mjx-container,.jp-InputArea,.cm-editor,.jp-Toolbar,.jp-NotebookPanel-toolbar')) return;
    var r = e.getBoundingClientRect(); if (r.width < 2 || r.height < 2 || r.bottom < 0 || r.top > innerHeight || r.right < 0 || r.left > innerWidth) return;
    var s = getComputedStyle(e); if (s.visibility === 'hidden' || s.display === 'none' || parseFloat(s.opacity) === 0) return;
    var cs = [norm(s.backgroundColor)].concat(s.backgroundImage !== 'none' ? stops(s.backgroundImage).map(norm) : []);
    ['::before', '::after'].forEach(function(ps){ var q = getComputedStyle(e, ps); if (q.content === 'none' || q.display === 'none') return;
      cs.push(norm(q.backgroundColor)); if (q.backgroundImage !== 'none') cs = cs.concat(stops(q.backgroundImage).map(norm)); });
    cs.forEach(function(c){ n++; if (ok(c)) return;
      var k = e.tagName + '.' + String(e.className).split(' ').filter(Boolean).slice(0, 2).join('.') + ' ' + hex(c) + (c[3] < 1 ? '/' + Math.round(c[3]*100) / 100 : '');
      bad[k] = (bad[k] || 0) + 1; }); });
  var list = Object.keys(bad).map(function(k){ return [k, bad[k]]; }).sort(function(a, b){ return b[1] - a[1]; });
  return {n: n, bad: list.length, list: list.slice(0, 14)}; }"""

def judge(row, env, theme, r, stand):
    tag = "%s %s" % (env, theme)
    s = " (stand-in body.nbskin-digi)" if stand else ""
    m = r["r1"]
    row("R1 rail accent gold · " + tag, m["markGold"] and m["cursorGold"],
        "--nbmark %s hsl %s · mark at .here (%s) face+glow %s%s" % (m["mark"], m["markHsl"], m["here"], m["cursor"] or m.get("img"), s))
    c, p = r["r2"]["card"], r["r2"]["pill"]
    row("R2 card 14px + 1px line, pill 999px · " + tag,
        bool(c) and abs(c[0] - 14) < .5 and abs(c[1] - 1) < .3 and c[2] != "none" and p is not None and p >= 999,
        "card radius/line %s · pill radius %s%s" % (c, p, s))
    f = r["r3"]
    first = lambda x: x.split(",")[0].strip().strip('"\'')
    row("R3 headings Unbounded, loaded · " + tag,
        first(f["title"]) == "Unbounded" and first(f["pill"]) == "Unbounded" and f["loaded"] and f["drawn"],
        "title %r · pill %r · faces %s · drawn %s %s · (check() %s, not counted)%s"
        % (f["title"][:30], f["pill"][:30], f["faces"], f["drawn"], f["w"], f["check"], s))
    q = r["r4"]
    row("R4 contrast ≥ 4.5 · " + tag, q["n"] > 20 and q["low"] == 0,
        "%d texts, %d under 4.5 %s%s" % (q["n"], q["low"], q["worst"][:8], s))

def lite_theme(pg, theme):
    want = "JupyterLab Dark" if theme == "dark" else "JupyterLab Light"
    if pg.evaluate("() => document.body.getAttribute('data-jp-theme-name')") == want: return True
    ok = palette(pg, "Use Theme: " + want)
    pg.wait_for_timeout(2500)
    return ok and pg.evaluate("() => document.body.getAttribute('data-jp-theme-name')") == want

def main():
    import nbpick
    src = os.path.abspath(nbpick.from_argv(sys.argv))
    nid = (json.load(open(src, encoding="utf-8")).get("metadata", {}).get("digichemjn", {}) or {}).get("id") or "vorlage"
    rows, LITE_BUILT = [], [None]
    def row(name, ok, detail):
        rows.append((name, bool(ok), detail)); print("%s  %-46s %s" % ("PASS" if ok else "FAIL", name, detail), flush=True)
    def shot(pg, name):
        if SHOTS:
            os.makedirs(SHOTS, exist_ok=True); pg.screenshot(path=os.path.join(SHOTS, name))
    with sync_playwright() as P:
        b = P.chromium.launch(executable_path=CHROME)
        for env in ENVS:
            for theme in THEMES:
                tag = "%s %s" % (env, theme)
                srv = None; tmp = tempfile.mkdtemp(prefix="e34nb_")
                try:
                    if env in ("lab", "nb7"):
                        shutil.copy(src, os.path.join(tmp, "v.ipynb"))
                        srv, base = start_server(env, tmp, theme)
                        url = base + ("/lab/tree/v.ipynb?reset" if env == "lab" else "/notebooks/v.ipynb")
                    else:
                        if not LITE or not os.path.isdir(LITE):
                            try:
                                LITE_BUILT[0] = LITE_BUILT[0] or build_lite(src, tempfile.mkdtemp(prefix="e34lite_"))
                            except Exception as e:
                                row("S0 the style is digi · " + tag, False, "BAD no Lite site: %s" % str(e)[:200]); continue
                        site = LITE if LITE and os.path.isdir(LITE) else LITE_BUILT[0]
                        port = free_port()
                        srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1", "--directory", site],
                                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        time.sleep(1.5); base = "http://127.0.0.1:%d" % port
                        url = base + "/lab/index.html?path=v.ipynb"
                    ctx = b.new_context(viewport={"width": W, "height": H}, color_scheme=theme)
                    # the brightness is the reader's choice, stated as a reader states it (◐ → this notebook's key,
                    # as run.py does); the STYLE is left unset: a first start, so the notebook's default decides (J1)
                    ctx.add_init_script("try{if(!sessionStorage.getItem('__e34')){localStorage.setItem(%s,%s);"
                                        "sessionStorage.setItem('__e34','1');}}catch(e){}" % (json.dumps("digichemjn.theme.v1." + nid), json.dumps(theme)))
                    reqs, fe = [], []
                    def onreq(rq):
                        u = rq.url
                        if u.startswith("data:") or u.startswith("blob:"): return
                        host = urllib.parse.urlparse(u).hostname or ""
                        local = host in ("127.0.0.1", "localhost")
                        own = local and re.search(r"/(static|build|extensions|lab/extensions)/", urllib.parse.urlparse(u).path)
                        if not local or (rq.resource_type == "font" and not own):
                            reqs.append((rq.resource_type, u[:90]))
                        elif rq.resource_type == "font":
                            fe.append(u.rsplit("/", 1)[-1][:40])
                    ctx.on("request", onreq)
                    pg = ctx.new_page(); errs = []
                    pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
                    pg.goto(url)
                    pg.wait_for_selector(".jp-NotebookPanel .jp-Cell", state="attached", timeout=180000)
                    pg.wait_for_timeout(3000)
                    if env == "lite" and not lite_theme(pg, theme):
                        row("S0 the style is digi · " + tag, False, "BAD Lite theme not set to %s" % theme); ctx.close(); continue
                    st = run_and_play(pg, env == "lite")
                    if st != "ok":
                        row("S0 the style is digi · " + tag, False, st + " · errors %s" % errs[:2]); ctx.close(); continue
                    sv = pg.evaluate(STAND, STRICT)
                    stand = not sv["had"]
                    pg.wait_for_timeout(1200); shot(pg, "E34-%s-%s-cover.png" % (env, theme))
                    pv = pg.evaluate(PAL, [PALETTE, None]) if theme == "dark" else None
                    pl = play(pg); pg.evaluate(KEEP); pg.wait_for_timeout(1500)
                    dark_ok = sv["dark"] == (theme == "dark")
                    row("S0 the style is digi · " + tag, (sv["had"] or not STRICT) and pl == "play" and dark_ok,
                        "body.nbskin-digi %s · nbdark %s · Play %s" % ("by the notebook" if sv["had"] else ("MISSING (strict)" if STRICT else "stand-in"),
                                                                       sv["dark"], pl))
                    if pv is not None:
                        row("R6v dark: the cover in the palette · " + tag, pv["n"] > 20 and pv["bad"] == 0,
                            "%d colours; outside: %s" % (pv["n"], pv["list"][:10]))
                    shot(pg, "E34-%s-%s.png" % (env, theme))
                    r = pg.evaluate(MEASURE, None)
                    judge(row, env, theme, r, stand)
                    p0 = pg.evaluate(PAL, [PALETTE, None]) if theme == "dark" else None
                    # open the first chapter's practice and figure, measure contrast again further down
                    pg.evaluate("""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
                      var sc = P.querySelector('.jp-WindowedPanel-outer'); if (sc) sc.scrollTop = 700; }""")
                    pg.wait_for_timeout(1200); shot(pg, "E34-%s-%s-2.png" % (env, theme))
                    r2 = pg.evaluate(MEASURE, None)["r4"]
                    row("R4b contrast ≥ 4.5 (scrolled) · " + tag, r2["n"] > 20 and r2["low"] == 0,
                        "%d texts, %d under 4.5 %s" % (r2["n"], r2["low"], r2["worst"][:4]))
                    if theme == "dark":
                        p1 = pg.evaluate(PAL, [PALETTE, None])
                        row("R6 dark: every surface in the palette · " + tag, p0["bad"] == 0 and p1["bad"] == 0,
                            "%d colours at the top, %d further down; outside: %s" % (p0["n"], p1["n"], (p0["list"] + p1["list"])[:12]))
                    gear = pg.evaluate("""() => { var g = document.querySelector('#nbpanel-root .nbbtn.nbgear');
                      if (!g) return false; g.click(); return true; }""")
                    pg.wait_for_timeout(1500); shot(pg, "E34-%s-%s-gear.png" % (env, theme))
                    r3 = pg.evaluate(MEASURE, "#nbpanel-root .nbdrawer")["r4"]
                    if theme == "dark":
                        p2 = pg.evaluate(PAL, [PALETTE, "#nbpanel-root .nbdrawer"])
                        row("R6c dark: settings ⚙ in the palette · " + tag, gear and p2["bad"] == 0,
                            "%d colours; outside: %s" % (p2["n"], p2["list"][:10]))
                    row("R4c contrast ≥ 4.5 (settings ⚙ open) · " + tag, gear and r3["n"] > 10 and r3["low"] == 0,
                        "⚙ %s · %d texts, %d under 4.5 %s" % ("opened" if gear else "BAD no ⚙ button", r3["n"], r3["low"], r3["worst"][:6]))
                    if gear: pg.evaluate("() => document.querySelector('#nbpanel-root .nbbtn.nbgear').click()")
                    fonts = [x for x in reqs if x[0] == "font"]
                    row("R5 no font from the network · " + tag, not fonts and not reqs,
                        "font requests %d %s · foreign hosts %d %s · the front end's own packaged fonts (not counted) %s"
                        % (len(fonts), fonts[:2], len(reqs), reqs[:2], fe[:3]))
                    ctx.close()
                finally:
                    if srv: srv.terminate()
        b.close()
    red = [r for r in rows if not r[1]]
    if JOUT: json.dump(rows, open(JOUT, "w"), indent=1)
    print("\n%d rows, %d red" % (len(rows), len(red)))
    print("REGRESS-CSS-E34 OK" if not red else "REGRESS-CSS-E34 RED")
    sys.exit(1 if red else 0)

if __name__ == "__main__":
    main()
