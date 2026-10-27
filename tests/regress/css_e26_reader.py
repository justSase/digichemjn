"""E26 Teil 2 · CSS — das Lesefenster (toolkit/css/15-reader.css). Werkstatt CSS.
    python3 tests/regress/css_e26_reader.py <notebook.ipynb> [--shots DIR]

The cell runs in a real kernel (env_iframe.run_cell); its reading output
(`.nbreading`, with its own <style>) is drawn in a page of its own, as PyCharm
does. A stand-in for 20-reader.js builds the reading window after the class
contract (claude/VERTRAG-nbrw.md): .nbrw > .nbrw-win (the reading version) +
.nbrw-panel (buttons, current chapter, track, thumb, marks) and one
calculation field, one copy line and one slider INSIDE the reading version
(where its !important reset would win). Rows: skins minimal/cyber/fairy ×
theme light/dark by attribute, plus no attribute under prefers dark/light.
  R1 window       height = --nbrw-h (E33: screen − 240 px, was 600) ±1, scrolls in itself (overflow auto, content taller)
  R2 own bar      hidden: offsetWidth − clientWidth = 0
  R3 panel        absolute at the right edge, width 168 ±1, does not cover the window (overlap ≤ 1 px)
  R4 thumb        ≥ 4 px wide, ≥ 24 px tall, painted (alpha > 0, opacity > 0)
  R5 contrast     buttons, current chapter, mark names (not locked), field, check button, feedback ≥ 4.5
  R6 fields       input/check/task paint their own background inside .nbreading (not transparent)
  R7 theme        dark rows: panel background luminance < 0.2; light rows > 0.6
  R8 skins        the three skins paint three different panels per theme
v1.70 (no 15-reader.css): red (R1 height = content, R3 panel static, R6 transparent).
exit 0 = REGRESS-CSS-E26-READER OK."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from env_iframe import run_cell

STANDIN = r"""([skin, theme]) => {
  var rd = document.querySelector('.nbreading');
  // E26.2 merge (Hauptwerkstatt): since 20-reader.js travels in the same output it has
  // already built the real window -> measure THAT one (stand-in fields/marks added);
  // behauptete bisher: the reading output carries no script (nested windows, R3 red).
  var real = document.querySelector('.nbrw');
  if (real) {
    // E26.3 (JS): the window opens on the preview; the panel is there in the document
    var play = real.querySelector('[data-nbrw-act=play]'); if (play && real.getAttribute('data-nbrw-view') === 'cover') play.click();
    real.setAttribute('data-nbrw-skin', skin);
    if (theme) real.setAttribute('data-nbrw-theme', theme); else real.removeAttribute('data-nbrw-theme');
    real.style.color = ''; real.style.backgroundColor = '';
    var h0 = rd.querySelector('h2.nbread-h') || rd.querySelector('.nbread-h');
    var t0 = document.createElement('div'); t0.className = 'nbrw-task';
    t0.innerHTML = "<input class='nbrw-input' value='3.14'><button class='nbrw-check'>Check</button><span class='nbrw-fb' data-ok='0'>Not yet</span>";
    var c0 = document.createElement('div'); c0.className = 'nbrw-copy';
    c0.innerHTML = "<code>pruefe(\"t1\", z)</code><button class='nbrw-copybtn'>Copy</button>";
    var s0 = document.createElement('div'); s0.className = 'nbrw-slider';
    s0.innerHTML = "<input type='range' class='nbrw-range' min='0' max='4' value='2'><output class='nbrw-val'>2.0</output>";
    h0.after(t0, c0, s0);
    var tr0 = real.querySelector('.nbrw-track'), k0 = ['calc','code','viz'], s0t = ['solved','wrong','open','locked'];
    for (var j = 0; j < 4; j++) { var m0 = document.createElement('a'); m0.className = 'nbrw-mark';
      m0.setAttribute('data-kind', k0[j % 3]); m0.setAttribute('data-st', s0t[j]); m0.style.top = (300 + j * 30) + 'px';
      m0.innerHTML = "<span class='nbrw-lab'>Task " + (j + 1) + "</span>"; tr0.appendChild(m0); }
    return -1;
  }
  var rw = document.createElement('div'); rw.className = 'nbrw';
  rw.setAttribute('data-nbrw-skin', skin); if (theme) rw.setAttribute('data-nbrw-theme', theme);
  rw.style.setProperty('--nbrw-h', '600px');
  rd.parentNode.insertBefore(rw, rd);
  var win = document.createElement('div'); win.className = 'nbrw-win'; win.appendChild(rd); rw.appendChild(win);
  var h1 = rd.querySelector('h2.nbread-h') || rd.querySelector('.nbread-h');
  var task = document.createElement('div'); task.className = 'nbrw-task';
  task.innerHTML = "<input class='nbrw-input' value='3.14'><button class='nbrw-check'>Check</button><span class='nbrw-fb' data-ok='0'>Not yet</span>";
  var cp = document.createElement('div'); cp.className = 'nbrw-copy';
  cp.innerHTML = "<code>pruefe(\"t1\", z)</code><button class='nbrw-copybtn'>Copy</button>";
  var sl = document.createElement('div'); sl.className = 'nbrw-slider';
  sl.innerHTML = "<input type='range' class='nbrw-range' min='0' max='4' value='2'><output class='nbrw-val'>2.0</output><div class='nbrw-fig'><svg width='200' height='60'><rect width='200' height='60' fill='#888'/></svg></div>";
  h1.after(task, cp, sl);
  var p = document.createElement('div'); p.className = 'nbrw-panel';
  var bar = "<div class='nbrw-bar'>" + ["h+","h-","a+","a-","theme","skin"].map(function(a, i){
    return "<button class='nbrw-btn" + (i == 4 ? " is-on" : "") + "' data-act='" + a + "'>" + {"h+":"↕+","h-":"↕−","a+":"A+","a-":"A−","theme":"◐","skin":"✿"}[a] + "</button>"; }).join('') + "</div>";
  p.innerHTML = bar + "<div class='nbrw-cur'>1 · Chapter</div><div class='nbrw-track'><div class='nbrw-thumb' style='top:0;height:60px'></div></div>";
  rw.appendChild(p);
  var tr = p.querySelector('.nbrw-track'), hs = rd.querySelectorAll('h2.nbread-h'), n = Math.min(hs.length, 7);
  var kinds = ['chap','calc','code','viz'], sts = ['solved','wrong','open','locked'];
  for (var i = 0; i < n; i++) { var m = document.createElement('a'); m.className = 'nbrw-mark' + (i == 1 ? ' is-active' : '');
    m.setAttribute('data-kind', i % 2 ? kinds[1 + (i % 3)] : 'chap'); m.setAttribute('data-st', sts[i % 4]);
    m.style.top = (10 + i * 40) + 'px'; m.innerHTML = "<span class='nbrw-lab'>" + hs[i].textContent.slice(0, 30) + "</span>"; tr.appendChild(m); }
  return n;
}"""

MEASURE = r"""() => {
  var lum = function(c){ var f = function(v){ v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
  var rgba = function(s){ var m = /rgba?\(([^)]+)\)/.exec(s || ''); if (!m) return [0,0,0,0];
    var p = m[1].split(/[ ,\/]+/).filter(Boolean).map(parseFloat); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; };
  var over = function(t, b){ var a = t[3]; return [t[0]*a + b[0]*(1-a), t[1]*a + b[1]*(1-a), t[2]*a + b[2]*(1-a), 1]; };
  var host = rgba(getComputedStyle(document.body).backgroundColor);
  var bgOf = function(e){ var L = []; for (var x = e; x; x = x.parentElement) { var c = rgba(getComputedStyle(x).backgroundColor);
      if (c[3] > 0) L.push(c); if (c[3] >= 1) break; }
    var b = (L.length && L[L.length - 1][3] >= 1) ? L.pop() : host; while (L.length) b = over(L.pop(), b); return b; };
  var con = function(e){ var bg = bgOf(e), fg = over(rgba(getComputedStyle(e).color), bg), a = lum(fg), b = lum(bg);
    return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05); };
  var q = function(s){ return document.querySelector(s); }, R = function(e){ return e.getBoundingClientRect(); };
  var rw = q('.nbrw'), win = q('.nbrw-win'), pn = q('.nbrw-panel'), th = q('.nbrw-thumb');
  var o = {};
  o.winH = R(win).height; o.winOv = getComputedStyle(win).overflowY; o.winScroll = win.scrollHeight - win.clientHeight;
  o.hVar = parseFloat(getComputedStyle(win.closest('.nbrw')).getPropertyValue('--nbrw-h')) || 600;   // E33 B1b: the screen's height, not 600
  o.bar = win.offsetWidth - win.clientWidth;
  o.pnPos = getComputedStyle(pn).position; o.pnW = R(pn).width; o.pnRight = R(rw).right - R(pn).right;
  // E26.3 (JS): the window runs under the panel (axis = window middle), the COLUMN stays clear of it;
  // behauptete bisher: the window itself ends at the panel
  o.overlap = Math.max(0, R(q('.nbreading')).right - R(pn).left);
  var ts = getComputedStyle(th); o.thW = R(th).width; o.thH = R(th).height; o.thA = rgba(ts.backgroundColor)[3] * (+ts.opacity);
  var low = [];
  document.querySelectorAll('.nbrw-btn,.nbrw-cur,.nbrw-mark:not([data-st=locked]) .nbrw-lab,.nbrw-input,.nbrw-check,.nbrw-copybtn,.nbrw-fb,.nbrw-val')
    .forEach(function(e){ var c = con(e); if (c < 4.5) low.push(e.className + ' ' + c.toFixed(2)); });
  o.low = low;
  o.fieldBg = ['.nbrw-input','.nbrw-check','.nbrw-task'].map(function(s){ return rgba(getComputedStyle(q(s)).backgroundColor)[3]; });
  var pb = bgOf(pn); o.pnLum = lum(pb); o.pnBg = pb.slice(0, 3).map(Math.round).join(',');
  return o;
}"""

def page(html, dark):
    bg = "#2b2d30" if dark else "#ffffff"
    return ("<!doctype html><meta charset=utf-8><body style='margin:0;padding:8px;background:%s;color:%s'>%s"
            % (bg, "#dfe1e5" if dark else "#1f2328", html))

def main():
    sys.path.insert(0, os.path.dirname(HERE)); import nbpick
    nb = nbpick.from_argv(sys.argv)               # E28: no notebook → the template
    shots = sys.argv[sys.argv.index("--shots") + 1] if "--shots" in sys.argv else None
    outs, errs, _ = run_cell(nb, {})
    if errs:
        print("kernel errors:", errs[:3])
    rd = [o for o in outs if "nbreading" in (o["data"].get("text/html") or "")]
    if not rd:
        print("FAIL no reading output"); print("REGRESS-CSS-E26-READER RED"); return 1
    html = rd[0]["data"]["text/html"]
    from playwright.sync_api import sync_playwright
    rows, fails, bgs = [], [], {}
    cases = [(s, t, t == "dark") for s in ("minimal", "cyber", "fairy") for t in ("light", "dark")]
    cases += [("minimal", None, True), ("minimal", None, False)]
    with sync_playwright() as p:
        b = p.chromium.launch()
        for skin, theme, dark in cases:
            ctx = b.new_context(viewport={"width": 1400, "height": 900}, color_scheme="dark" if dark else "light")
            pg = ctx.new_page()
            pg.set_content(page(html, dark))
            pg.evaluate(STANDIN, [skin, theme])
            pg.wait_for_timeout(150)
            o = pg.evaluate(MEASURE)
            tag = "%s %s" % (skin, theme or ("prefers-" + ("dark" if dark else "light")))
            f = []
            # E33 B1b (Werkstatt JS): the real window's height is the screen's less 240 (behauptete bisher: 600 px fix)
            if not (abs(o["winH"] - o["hVar"]) <= 1 and o["winOv"] in ("auto", "scroll") and o["winScroll"] > 0):
                f.append("R1 window h %.0f overflow %s scroll %d" % (o["winH"], o["winOv"], o["winScroll"]))
            if o["bar"] != 0: f.append("R2 own bar %d px" % o["bar"])
            if not (o["pnPos"] == "absolute" and abs(o["pnW"] - 168) <= 1 and abs(o["pnRight"] - 1) <= 1 and o["overlap"] <= 1):
                f.append("R3 panel %s w %.0f right %.1f overlap %.0f" % (o["pnPos"], o["pnW"], o["pnRight"], o["overlap"]))
            if not (o["thW"] >= 4 and o["thH"] >= 24 and o["thA"] > 0): f.append("R4 thumb %.0f×%.0f a %.2f" % (o["thW"], o["thH"], o["thA"]))
            if o["low"]: f.append("R5 contrast %s" % o["low"][:4])
            if min(o["fieldBg"]) <= 0: f.append("R6 field background alpha %s" % o["fieldBg"])
            if dark and not o["pnLum"] < 0.2: f.append("R7 dark panel lum %.2f" % o["pnLum"])
            if not dark and not o["pnLum"] > 0.6: f.append("R7 light panel lum %.2f" % o["pnLum"])
            if theme: bgs.setdefault(theme, set()).add(o["pnBg"])
            rows.append("%-22s win %.0f/%s bar %d · panel %s %.0f · thumb %.0f×%.0f · low %d · fields %s · lum %.2f  %s"
                        % (tag, o["winH"], o["winOv"], o["bar"], o["pnPos"], o["pnW"], o["thW"], o["thH"], len(o["low"]),
                           o["fieldBg"], o["pnLum"], "OK" if not f else "RED"))
            fails += ["%s: %s" % (tag, x) for x in f]
            if shots:
                os.makedirs(shots, exist_ok=True)
                pg.screenshot(path=os.path.join(shots, "reader-%s-%s.png" % (skin, theme or ("pref-dark" if dark else "pref-light"))))
            ctx.close()
        b.close()
    for t, s in bgs.items():
        if len(s) != 3: fails.append("R8 %s: %d different panels for 3 skins" % (t, len(s)))
    print("\n".join(rows))
    for x in fails: print("FAIL", x)
    print("REGRESS-CSS-E26-READER", "OK" if not fails else "RED")
    return 0 if not fails else 1

if __name__ == "__main__":
    sys.exit(main())
