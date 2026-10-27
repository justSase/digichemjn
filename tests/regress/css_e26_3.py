"""E26 Teil 3 · CSS — DAS LESEFENSTER WIE LAB (toolkit/css/15-reader.css). Werkstatt CSS, 11.10.
    python3 tests/regress/css_e26_3.py <notebook.ipynb> [--shots DIR]

Real kernel (env_iframe.run_cell); the reading output in a page of its own (PyCharm:
every output its own page), 1366 px wide, the window 600 px. The real 20-reader.js
builds the window; a stand-in adds what JS and Python bring in E26 Teil 3 after
claude/VERTRAG-nbrw-E26.3.md (data-nbrw-view/lang/mode/panel, --nbrw-pw/--nbrw-side,
.nbrw-cover with title card, language and mode buttons, play, cover timeline dots;
[data-nbrw-l], [data-nbrw-only], .nbrw-lockmsg, .nbrw-code overlay, .nbrw-xp).
The Lab values (LAB) were measured in JupyterLab 4.6 with v1.73, 11.10., 1366 px,
getComputedStyle, per style x light/dark (Werkstatt CSS; Chronik 11.10.).
Rows per style minimal/cyber/fairy x light/dark:
  L1 font      reading base 14.3 px (Lab 100 % after E29 D7); box text 14.3/22.88; chapter 19.76/800;
               section 10.14 caps; fold pill 9.88; title 31.57 (Lab, ±0.3) — E30; v1.73–v1.76: 13 / 28.7
  L2 colours   title card border, title, chapter ink, box ink, key line (not cyber),
               field surface, section ink = Lab's (±6 per channel); title card surface
               = Lab's colour or its gradient's first colour
  L3 column    a prose box: width ≤ min(94 %, 70rem) of the column, centred ±1 px
  L4 axis      --nbrw-side = panel width: |centre title card − centre window| ≤ 1 px,
               panel open (168) and closed (44), zoom 0.6 / 1 / 1.5
  L5 cover     view=cover: cover shown, document headings and panel hidden (Lab: no tools
               on the cover, E25.g); view=doc: back;
               lang de/en hides the other [data-nbrw-l]; without window only the
               run's language; mode plain/calc/code hides task/copy/[data-nbrw-only];
               chosen mode card and play ring in the 'go' colour, play 84 x 84 round
               (go = Lab's green darkened to 4.5 : 1 — Lab's #3fa877 on white is 2.97)
  L6 fields    lock card dashed + text ≥ 4.5; locked chapter mark shows a padlock;
               check button: field surface, field line, ink ≥ 4.5; input on field surface
  L7 code      overlay: textarea and highlight layer same box (±0.5), same font and
               line height; textarea glyphs transparent; keyword colour = Lab's token
  L8 contrast  every text of cover, lock card, task, code output, xp ≥ 4.5
v1.73: red (base 15 px, no tokens, no cover/lock/code/xp rules). exit 0 = REGRESS-CSS-E26-3 OK."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from env_iframe import run_cell

# Lab, measured 11.10. (v1.73, JupyterLab 4.6, 1366 px): rgb triples
LAB = {
 ("minimal", "light"): dict(card=(248,250,251), cardln=(221,229,236), title=(51,71,91), chap=(18,50,74), ink=(31,41,51),
                            key=(24,105,63), fld=(255,255,255), sec=(85,99,111), kw=(29,92,138)),
 ("minimal", "dark"):  dict(card=(29,34,40), cardln=(51,65,79), title=(219,228,236), chap=(220,230,238), ink=(219,226,233),
                            key=(76,195,138), fld=(31,37,44), sec=(159,176,189), kw=(143,199,232)),
 ("cyber", "light"):   dict(card=(238,242,255), cardln=(155,127,224), title=(0,100,127), chap=(201,247,255), ink=(35,26,61),
                            key=None, fld=(242,238,255), sec=(84,67,126), kw=(0,100,127)),
 ("cyber", "dark"):    dict(card=(20,26,46), cardln=(58,42,107), title=(0,229,255), chap=(201,247,255), ink=(216,230,255),
                            key=None, fld=(20,26,46), sec=(143,168,216), kw=(0,229,255)),
 ("fairy", "light"):   dict(card=(251,243,255), cardln=(226,205,245), title=(123,50,194), chap=(255,247,251), ink=(74,58,99),
                            key=(29,102,69), fld=(253,248,255), sec=(101,83,119), kw=(123,50,194)),
 ("fairy", "dark"):    dict(card=(36,28,51), cardln=(74,58,99), title=(199,156,255), chap=(255,247,251), ink=(230,217,247),
                            key=(130,227,184), fld=None, sec=(179,162,200), kw=(199,156,255)),
}

STANDIN = r"""([skin, theme]) => {
  var rw = document.querySelector('.nbrw'); if (!rw) return 'no window';
  // E26.3 (Hauptwerkstatt, Zusammenführen): the real 20-reader.js opens on the preview → Play first, so the
  // document (.nbrw-doc) and the panel are there; behauptete bisher: the window opens on the document
  var play = rw.querySelector('.nbrw-cover [data-nbrw-act=play]'); if (play && rw.getAttribute('data-nbrw-view') === 'cover') play.click();
  var rd = rw.querySelector('.nbreading'), pn = rw.querySelector('.nbrw-panel');
  rw.setAttribute('data-nbrw-skin', skin); if (theme) rw.setAttribute('data-nbrw-theme', theme);
  rw.setAttribute('data-nbrw-view', 'doc'); rw.setAttribute('data-nbrw-lang', 'en');
  rw.setAttribute('data-nbrw-mode', 'both'); rw.setAttribute('data-nbrw-panel', 'open');
  rw.style.setProperty('--nbrw-pw', '168px'); rw.style.setProperty('--nbrw-side', '168px');
  var card = rd.querySelector('.nbr-nbtitle-card');
  var cv = document.createElement('div'); cv.className = 'nbrw-cover'; cv.style.display = 'none';
  cv.innerHTML = "<div class='nbrw-lang'><button data-lang='en'>EN</button><button data-lang='de'>DE</button></div>"
    + "<div style='text-align:center' class='cvcard'></div>"
    + "<p><span data-nbrw-l='en'>From one equation to rotation</span><span data-nbrw-l='de'>Von einer Gleichung zur Drehung</span></p>"
    + "<h4 class='nbrw-cv-h'><span data-nbrw-l='en'>Timeline</span><span data-nbrw-l='de'>Zeitleiste</span></h4>"
    + "<div class='nbrw-cv-tl'>" + [['chap','solved','1 Why'],['calc','solved',''],['code','open',''],['chap','open','2 Plane'],['viz','open',''],['chap','locked','3 Addition']]
        .map(function(d){ return "<span class='nbrw-cv-dot' data-kind='" + d[0] + "' data-st='" + d[1] + "'>" + (d[2] ? "<span class='nbrw-cv-lab'>" + d[2] + "</span>" : "") + "</span>"; }).join('') + "</div>"
    + "<div class='nbrw-modes'>" + ['plain','calc','code','both'].map(function(m){ return "<button class='nbrw-mode-opt' data-mode='" + m + "'><b>" + m + "</b><small>what it does</small></button>"; }).join('') + "</div>"
    + "<button data-nbrw-act='play'>&#9654;</button><span class='nbrw-play-lab'>Play</span>"
    + "<div class='nbrw-acct'>Sign in &#9656;</div>";
  rd.insertBefore(cv, rd.firstChild);
  if (card) cv.querySelector('.cvcard').appendChild(card.cloneNode(true));
  var h3 = rd.querySelectorAll('h3.nbread-h')[3];
  var ex = document.createElement('div');
  ex.innerHTML = "<div class='nbrw-lockmsg'>&#128274; <b>This chapter is locked.</b> It opens once 1 · roots is answered.</div>"
    + "<div class='nbrw-task' id='sti-task'><input class='nbrw-input' value='2'><button class='nbrw-check'>&#128269; Check answer</button><button class='nbrw-hint'>&#128172; Hint 1 of 2</button><span class='nbrw-fb' data-ok='1'>right</span></div>"
    + "<div class='nbrw-copy' data-kind='code' id='sti-copy'><div class='nbrw-code'><pre class='nbrw-hl'><span class='nbrw-hl-k'>def</span> f(q):\n    <span class='nbrw-hl-k'>return</span> <span class='nbrw-hl-n'>2</span> <span class='nbrw-hl-c'># note</span> <span class='nbrw-hl-s'>'s'</span></pre>"
    + "<textarea class='nbrw-ta' spellcheck='false'>def f(q):\n    return 2 # note 's'</textarea></div><button class='nbrw-run'>&#9654; Run in the window</button>"
    + "<span class='nbrw-runst'>Python is loading, once ~10 s</span><pre class='nbrw-out' data-err='1'>NameError: x</pre></div>"
    + "<div data-nbrw-only='code' id='sti-only'>code only</div>"
    + "<p><span data-nbrw-l='en' id='sti-en'>English</span><span data-nbrw-l='de' id='sti-de'>Deutsch</span></p>";
  h3.after(ex);
  var xp = document.createElement('div'); xp.className = 'nbrw-xp';
  xp.innerHTML = "<div class='nbrw-xp-bar'><div class='nbrw-xp-fill' style='width:40%'></div></div><span class='nbrw-xp-t'>3 / 14</span>";
  pn.insertBefore(xp, pn.querySelector('.nbrw-track'));
  var mk = document.createElement('a'); mk.className = 'nbrw-mark'; mk.id = 'sti-mark'; mk.setAttribute('data-kind', 'chap');
  mk.setAttribute('data-st', 'locked'); mk.style.top = '200px'; mk.innerHTML = "<span class='nbrw-lab'>3 Addition</span>";
  rw.querySelector('.nbrw-track').appendChild(mk);
  return 'ok';
}"""

MEASURE = r"""() => {
  var lum = function(c){ var f = function(v){ v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
  var rgba = function(s){ var m = /rgba?\(([^)]+)\)/.exec(s || ''); if (!m) return [0,0,0,0];
    var p = m[1].split(/[ ,\/]+/).filter(Boolean).map(parseFloat); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
  var over = function(t, b){ var a = t[3]; return [t[0]*a + b[0]*(1-a), t[1]*a + b[1]*(1-a), t[2]*a + b[2]*(1-a), 1]; };
  var host = rgba(getComputedStyle(document.body).backgroundColor);
  var bgOf = function(e){ var L = []; for (var x = e; x; x = x.parentElement) { var cs = getComputedStyle(x), c = rgba(cs.backgroundColor);
      if (c[3] === 0 && cs.backgroundImage.indexOf('gradient') >= 0) { var g = /rgba?\([^)]+\)/.exec(cs.backgroundImage); if (g) c = rgba(g[0]); }
      if (c[3] > 0) L.push(c); if (c[3] >= 1) break; }
    var b = (L.length && L[L.length - 1][3] >= 1) ? L.pop() : host; while (L.length) b = over(L.pop(), b); return b; };
  var con = function(e){ var bg = bgOf(e), fg = over(rgba(getComputedStyle(e).color), bg), a = lum(fg), b = lum(bg);
    return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05); };
  var vis = function(e){ var r = e.getBoundingClientRect(); if (!(r.width > 0 && r.height > 0)) return false;
    for (var x = e; x; x = x.parentElement) if (getComputedStyle(x).display === 'none') return false; return true; };
  var q = function(s){ return document.querySelector(s); }, R = function(e){ return e.getBoundingClientRect(); };
  var C = function(e, p){ return rgba(getComputedStyle(e)[p]).slice(0, 3).map(Math.round); };
  var rw = q('.nbrw'), win = q('.nbrw-win'), rd = q('.nbrw .nbreading'), o = {};
  var fs = function(e){ return e ? Math.round(parseFloat(getComputedStyle(e).fontSize) * 100) / 100 : -1; };
  var box = rd.querySelector('.nbr-nbbox-concept') || rd.querySelector('.nbr-nbbox');
  var h3s = rd.querySelectorAll('h3.nbread-h'), chap = h3s[3], sec = rd.querySelector('h2.nbread-h'), fold = rd.querySelector('h4.nbread-h');
  // E26.3 (Zusammenführen): the document's card is in .nbrw-doc (JS); the cover's copy comes first in the DOM — behauptete bisher: the first card is the document's
  var card = rd.querySelector(':scope > .nbrw-doc > div > .nbr-nbtitle-card') || rd.querySelector(':scope > div > .nbr-nbtitle-card') || rd.querySelector('.nbr-nbtitle-card'), th = card && card.querySelector('.nbr-nbtitle-h');
  var key = rd.querySelector('.nbr-nbbox-interp');
  o.font = {base: fs(rd), box: fs(box), lh: box ? parseFloat(getComputedStyle(box).lineHeight) : -1, chap: fs(chap),
            chapW: chap ? getComputedStyle(chap).fontWeight : '', sec: fs(sec), fold: fs(fold), title: fs(th)};
  var cs = card ? getComputedStyle(card) : null;
  var g = cs && /rgba?\([^)]+\)/.exec(cs.backgroundImage);
  o.col = {card: cs ? (rgba(cs.backgroundColor)[3] > 0 ? C(card, 'backgroundColor') : (g ? rgba(g[0]).slice(0,3).map(Math.round) : null)) : null,
           cardln: card ? C(card, 'borderTopColor') : null, title: th ? C(th, 'color') : null, chap: chap ? C(chap, 'color') : null,
           ink: box ? C(box.querySelector('p,div,span') || box, 'color') : null, key: key ? C(key, 'borderLeftColor') : null,
           fld: C(q('.nbrw .nbrw-input'), 'backgroundColor'), sec: sec ? C(sec, 'color') : null,
           kw: C(q('.nbrw .nbrw-hl-k'), 'color')};
  // L3: the column = the window's content box
  var wr = R(win), wcs = getComputedStyle(win), cl = wr.left + parseFloat(wcs.paddingLeft), cr = wr.right - parseFloat(wcs.paddingRight) - (win.offsetWidth - win.clientWidth);
  var br = R(box); o.colm = {w: br.width, cap: Math.min(0.94 * (cr - cl), 70 * parseFloat(getComputedStyle(document.documentElement).fontSize)),
           off: (br.left + br.right) / 2 - (cl + cr) / 2, colW: cr - cl};
  // L5 language / mode / view
  var shown = function(s){ var e = q(s); return !!(e && vis(e)); };
  o.lang = {en: shown('#sti-en'), de: shown('#sti-de')};
  o.mode = {task: shown('#sti-task'), copy: shown('#sti-copy'), only: shown('#sti-only')};
  o.view = {cover: shown('.nbrw-cover'), doc: !!(chap && vis(chap)), panel: shown('.nbrw-panel')};
  var mo = q('.nbrw .nbrw-mode-opt[data-mode=both]'), pl = q('.nbrw [data-nbrw-act=play]');
  o.cover = {modeLn: mo ? C(mo, 'borderTopColor') : null, playLn: pl ? C(pl, 'borderTopColor') : null,
             play: pl && vis(pl) ? [Math.round(R(pl).width), Math.round(R(pl).height), getComputedStyle(pl).borderRadius] : null};
  // L6
  var lk = q('.nbrw .nbrw-lockmsg'), ck = q('.nbrw .nbrw-check'), mk = q('#sti-mark');
  o.lock = {style: lk ? getComputedStyle(lk).borderTopStyle : '', con: lk && vis(lk) ? con(lk.querySelector('b')) : 0,
            mark: mk ? getComputedStyle(mk, '::before').content : 'none'};
  o.check = {bg: ck ? C(ck, 'backgroundColor') : null, ln: ck ? C(ck, 'borderTopColor') : null, con: ck ? con(ck) : 0};
  // L7
  var ta = q('.nbrw .nbrw-ta'), hl = q('.nbrw .nbrw-hl');
  if (ta && hl) { var a = R(ta), b = R(hl), A = getComputedStyle(ta), B = getComputedStyle(hl);
    o.code = {dx: Math.max(Math.abs(a.left - b.left), Math.abs(a.top - b.top)), font: A.fontFamily === B.fontFamily && A.fontSize === B.fontSize && A.lineHeight === B.lineHeight,
              pad: A.paddingLeft === B.paddingLeft && A.paddingTop === B.paddingTop, glyph: rgba(A.color)[3], fill: A.webkitTextFillColor}; }
  // L8
  var low = [];
  document.querySelectorAll('.nbrw .nbrw-cover *, .nbrw .nbrw-lockmsg, .nbrw .nbrw-lockmsg *, .nbrw .nbrw-task *, .nbrw .nbrw-runst, .nbrw .nbrw-out, .nbrw .nbrw-xp-t, .nbrw .nbrw-run')
    .forEach(function(e){ var own = [].some.call(e.childNodes, function(n){ return n.nodeType === 3 && n.textContent.trim(); });
      if (!own || !vis(e)) return; var c = con(e); if (c < 4.5) low.push((e.className || e.tagName) + ' "' + e.textContent.trim().slice(0, 14) + '" ' + c.toFixed(2)); });
  o.low = low;
  return o;
}"""

AXIS = r"""([pw, z]) => { var rw = document.querySelector('.nbrw'), win = rw.querySelector('.nbrw-win');
  rw.style.setProperty('--nbrw-pw', pw + 'px'); rw.style.setProperty('--nbrw-side', pw + 'px');
  rw.setAttribute('data-nbrw-panel', pw > 60 ? 'open' : 'closed'); rw.style.setProperty('--nbrw-zoom', z);
  // E26.3: the document sits in .nbrw-doc (JS) — behauptete bisher: the card directly under .nbreading
  var c = rw.querySelector('.nbreading > .nbrw-doc > div > .nbr-nbtitle-card') || rw.querySelector('.nbreading > div > .nbr-nbtitle-card'); win.scrollTop = 0;
  var r = c.getBoundingClientRect(), w = win.getBoundingClientRect();
  return (r.left + r.right) / 2 - (w.left + w.right) / 2; }"""

def page(html, dark):
    bg = "#2b2d30" if dark else "#ffffff"
    return ("<!doctype html><meta charset=utf-8><body style='margin:0;padding:0;background:%s;color:%s'>%s"
            % (bg, "#dfe1e5" if dark else "#1f2328", html))

def near(a, b, tol=6):
    return a is not None and b is not None and all(abs(x - y) <= tol for x, y in zip(a, b))

def main():
    import nbpick
    nb = nbpick.from_argv(sys.argv)               # E28: no notebook → the template
    shots = sys.argv[sys.argv.index("--shots") + 1] if "--shots" in sys.argv else None
    outs, errs, _ = run_cell(nb, {})
    if errs: print("kernel errors:", errs[:3])
    rd = [o for o in outs if "nbreading" in (o["data"].get("text/html") or "")]
    if not rd:
        print("FAIL no reading output"); print("REGRESS-CSS-E26-3 RED"); return 1
    html = rd[0]["data"]["text/html"]
    outs_de, _, _ = run_cell(nb, {"DIGICHEM_LANG": "de"})
    html_de = [o for o in outs_de if "nbreading" in (o["data"].get("text/html") or "")][0]["data"]["text/html"]
    from playwright.sync_api import sync_playwright
    from lab_keys import CHROME
    rows, fails = [], []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for (skin, theme), ref in LAB.items():
            dark = theme == "dark"
            ctx = b.new_context(viewport={"width": 1366, "height": 760}, color_scheme="dark" if dark else "light")
            pg = ctx.new_page(); pg.set_content(page(html, dark)); pg.wait_for_timeout(600)
            tag = "%s %s" % (skin, theme); f = []
            st = pg.evaluate(STANDIN, [skin, theme])
            if st != "ok":
                fails.append("%s BAD stand-in: %s" % (tag, st)); ctx.close(); continue
            pg.wait_for_timeout(150)
            o = pg.evaluate(MEASURE)
            F = o["font"]
            # E30 (Werkstatt CSS, 12.10.): Lab after E29 D7 — text 14.3 (line 1.6 = 22.88), title 31.57; chapter,
            # section and fold stayed 19.76 / 10.14 / 9.88 in Lab (measured, Vorlage v1.76) — behauptete bisher: 13 = Lab (v1.73)
            want = dict(base=14.3, box=14.3, lh=22.88, chap=19.76, sec=10.14, fold=9.88, title=31.57)
            bad = [k for k, v in want.items() if abs(F[k] - v) > 0.3]
            if bad or F["chapW"] != "800": f.append("L1 font %s (want %s, chapter 800)" % ({k: F[k] for k in want}, want))
            c = o["col"]
            for k in ("card", "cardln", "title", "chap", "ink", "key", "fld", "sec", "kw"):
                if ref.get(k) is not None and not near(c.get(k), ref[k]): f.append("L2 %s %s, Lab %s" % (k, c.get(k), ref[k]))
            m = o["colm"]
            if not (m["w"] <= m["cap"] + 1 and abs(m["off"]) <= 1): f.append("L3 box %.0f (cap %.0f) off %.1f" % (m["w"], m["cap"], m["off"]))
            ax = []
            for pw in (168, 44):
                for z in (0.6, 1, 1.5):
                    d = pg.evaluate(AXIS, [pw, z]); ax.append(d)
                    if abs(d) > 1: f.append("L4 axis panel %d zoom %s: %.1f px" % (pw, z, d))
            pg.evaluate(AXIS, [168, 1])
            # L5 language, mode, view
            S = lambda js: pg.evaluate(js)
            if not (o["lang"]["en"] and not o["lang"]["de"]): f.append("L5 lang en: %s" % o["lang"])
            # E26.3 (Zusammenführen): the real JS sets the language on .nbrw AND on .nbreading (lang, the rule without window) — behauptete bisher: only data-nbrw-lang
            LNG = "(l) => { document.querySelector('.nbrw').setAttribute('data-nbrw-lang', l); document.querySelector('.nbrw .nbreading').setAttribute('lang', l); }"
            pg.evaluate(LNG, "de")
            l2 = S("() => [!!document.querySelector('#sti-en').offsetParent, !!document.querySelector('#sti-de').offsetParent]")
            if l2 != [False, True]: f.append("L5 lang de: en/de shown %s" % l2)
            pg.evaluate(LNG, "en")
            for mode, want_m in (("both", [True, True, True]), ("plain", [False, False, False]), ("calc", [True, False, False]), ("code", [False, True, True])):
                pg.evaluate("(m) => document.querySelector('.nbrw').setAttribute('data-nbrw-mode', m)", mode)
                got = S("() => ['#sti-task', '#sti-copy', '#sti-only'].map(function(s){ return !!document.querySelector(s).offsetParent; })")
                if got != want_m: f.append("L5 mode %s: task/copy/only %s, want %s" % (mode, got, want_m))
            S("() => document.querySelector('.nbrw').setAttribute('data-nbrw-mode', 'both')")
            if o["view"] != {"cover": False, "doc": True, "panel": True}: f.append("L5 view doc %s" % o["view"])
            # E26.3 (Zusammenführen): the view through the real JS (it also sets the inline display of cover/document) — behauptete bisher: the attribute alone
            VIEW = "(v) => { var w = document.querySelector('.nbrw'); if (window.__nbReader && window.__nbReader.show) window.__nbReader.show(v); w.setAttribute('data-nbrw-view', v); w.querySelector('.nbrw-win').scrollTop = 0; }"
            pg.evaluate(VIEW, "cover")
            pg.wait_for_timeout(100)
            oc = pg.evaluate(MEASURE)
            if oc["view"] != {"cover": True, "doc": False, "panel": False}: f.append("L5 view cover %s" % oc["view"])
            cv = oc["cover"]
            go = cv["playLn"]
            if not (cv["play"] and cv["play"][:2] == [84, 84] and cv["play"][2] == "50%"): f.append("L5 play %s" % cv["play"])
            if not (go and cv["modeLn"] == go and go != oc["col"]["ink"]): f.append("L5 chosen mode line %s, play %s" % (cv["modeLn"], go))
            if oc["low"]: f.append("L8 cover contrast %s" % oc["low"][:4])
            if shots:
                os.makedirs(shots, exist_ok=True); pg.screenshot(path=os.path.join(shots, "e26_3-cover-%s-%s.png" % (skin, theme)))
            pg.evaluate(VIEW, "doc")
            # L6 / L7 / L8 (document)
            L = o["lock"]
            if not (L["style"] == "dashed" and L["con"] >= 4.5 and "\U0001F512" in (L["mark"] or "")): f.append("L6 lock %s" % L)
            K = o["check"]
            if not (near(K["bg"], ref["fld"] or K["bg"]) and K["con"] >= 4.5 and K["bg"] != K["ln"]): f.append("L6 check %s" % K)
            cd = o.get("code")
            if not (cd and cd["dx"] <= 0.5 and cd["font"] and cd["pad"] and (cd["glyph"] == 0 or cd["fill"] in ("transparent", "rgba(0, 0, 0, 0)"))):
                f.append("L7 code overlay %s" % cd)
            if o["low"]: f.append("L8 contrast %s" % o["low"][:4])
            if shots:
                pg.evaluate("() => { var w = document.querySelector('.nbrw-win'), e = document.querySelectorAll('h3.nbread-h')[3]; w.scrollTop += e.getBoundingClientRect().top - w.getBoundingClientRect().top - 10; }")
                pg.wait_for_timeout(100); pg.screenshot(path=os.path.join(shots, "e26_3-doc-%s-%s.png" % (skin, theme)))
            rows.append("%-14s font %s/%s ch %s · card %s · title %s · chap %s · box %.0f/%.0f off %.1f · axis max %.1f · play %s · lock %s · low %d  %s"
                        % (tag, F["base"], F["box"], F["chap"], c["card"], c["title"], c["chap"], m["w"], m["cap"], m["off"],
                           max(abs(x) for x in ax), cv["play"], L["style"], len(o["low"]) + len(oc["low"]), "OK" if not f else "RED"))
            fails += ["%s: %s" % (tag, x) for x in f]
            ctx.close()
        # without a window (nbconvert / no script): only the run's language
        for lang, h in (("en", html), ("de", html_de)):
            ctx = b.new_context(viewport={"width": 1366, "height": 760})
            pg = ctx.new_page()
            pg.route("**/*", lambda r: r.abort())
            pg.set_content(page(h.replace("<script>", "<script type='text/plain'>"), False))
            got = pg.evaluate("""() => { var rd = document.querySelector('.nbreading'); var s = document.createElement('p');
              s.innerHTML = "<span data-nbrw-l='en' id='x-en'>E</span><span data-nbrw-l='de' id='x-de'>D</span>"; rd.appendChild(s);
              return [getComputedStyle(document.querySelector('#x-en')).display !== 'none', getComputedStyle(document.querySelector('#x-de')).display !== 'none', document.querySelectorAll('.nbrw').length]; }""")
            want = [lang == "en", lang == "de", 0]
            rows.append("no window, run %s: en/de shown %s, windows %d" % (lang, got[:2], got[2]))
            if got != want: fails.append("L5 no window, run %s: en/de/windows %s, want %s" % (lang, got, want))
            ctx.close()
        b.close()
    print("\n".join(rows))
    for x in fails: print("FAIL", x)
    print("REGRESS-CSS-E26-3", "OK" if not fails else "RED")
    return 0 if not fails else 1

if __name__ == "__main__":
    sys.exit(main())
