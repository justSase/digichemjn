import sys as _sys, nbpick as _nbpick; _nbpick.argv_fix(_sys.argv)   # E28: ohne Angabe die Vorlage (--nb complex auf Zuruf)

# 2026-09-24aw — the rail's SHAPE, which is what it is now judged on.
# 2026-09-24az — the arm-then-turn lock gesture.
_LOCKFLOW_JS = """() => {
    var h = document.getElementById('nbpanel-root');
    var ls = h.querySelectorAll('a.nbjump[data-lock]');
    if (ls.length < 2) return {skipped: true};
    var k1 = ls[0].getAttribute('data-lock'), k2 = ls[1].getAttribute('data-lock');
    var hit = function(el){
        el.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true})); };
    hit(ls[0]);
    var dot = ls[0].querySelector('.nbchapdot');
    var box = document.querySelector('.nblocked-' + k1);
    var bl = box && box.querySelector('.nblocked-lock');
    // 2026-09-25c: the drawn lock, read off a LOCKED chapter mark — the
    // shackle is a bordered box, the body a filled one. Both are pseudo-
    // elements, so this is the only way to see them at all.
    var lockedDot = h.querySelector('.nbmap-node.locked .nbchapdot')
                 || h.querySelector('.nbrail-dot.st-lock .nbdotg');
    var sh = lockedDot ? getComputedStyle(lockedDot, '::before') : null;
    var bd = lockedDot ? getComputedStyle(lockedDot, '::after') : null;
    var out = {k1: k1, k2: k2,
               armedRail: h.querySelectorAll('.nbmap-node.nbkeyed').length,
               armedBox: document.querySelectorAll('.nblocked-note.nbkeyed').length,
               railGlyph: dot ? getComputedStyle(dot, '::after').content : null,
               hoverGlyph: dot ? getComputedStyle(dot, '::before').content : null,
               drawn: lockedDot ? {
                   shackle: sh.borderTopStyle !== 'none',
                   shackleBorder: parseFloat(sh.borderTopWidth) || 0,
                   shackleRadius: sh.borderTopLeftRadius,
                   bodyBg: bd.backgroundColor,
                   ink: getComputedStyle(lockedDot).color} : null,
               boxGlyph: bl ? getComputedStyle(bl, '::after').content : null};
    out.lockPage = h.dataset.page === 'lock' && h.classList.contains('open');
    hit(ls[1]);
    out.afterOther = h.querySelectorAll('.nbmap-node.nbkeyed').length;
    out.firstStillArmed = ls[0].classList.contains('nbkeyed');
    return out;
}"""

_RAIL_SHAPE_JS = """() => {
    var h = document.getElementById('nbpanel-root');
    var dY = h.__nbDocY, rY = h.__nbRailY, vI = h.__nbVis;
    if (!dY || !rY || !vI) return {noTables: true};
    var all = h.querySelectorAll('.nbmap-node');
    var moved = 0, worst = 0, kinds = [];
    vI.forEach(function(i){
        var d = Math.round(rY[i] - dY[i]);
        if (d !== 0) moved++;
        if (Math.abs(d) > Math.abs(worst)) worst = d;
        var m = all[i].className.match(
            /(^| )(title|sect|chap|sub|task|codetask|viz|end|cell)( |$)/);
        kinds.push(m ? m[2] : '?');
    });
    var ys = [];
    vI.forEach(function(i){
        var m = all[i].querySelector('.nbsect,.nbchapdot,.nbsubdot,.nbrail-dot,'
                                   + '.nbvizmark,.nbcodemark');
        if (!m) return;
        var c = getComputedStyle(m), w = parseFloat(c.width) || 10;
        ys.push({y: rY[i], e: c.transform.indexOf('0.707') >= 0 ? w * 1.4142 : w});
    });
    ys.sort(function(a, b){ return a.y - b.y; });
    var bad = 0, tight = 1e9, back = 0;
    for (var q = 1; q < ys.length; q++) {
        var sl = (ys[q].y - ys[q-1].y) - (ys[q].e + ys[q-1].e) / 2;
        if (sl < 0) bad++;
        if (sl < tight) tight = Math.round(sl);
        if (ys[q].y < ys[q-1].y) back++;
    }
    return {n: vI.length, exact: vI.length - moved, nudged: moved,
            biggestNudge: worst, overlaps: bad,
            tightest: (tight === 1e9 ? null : tight), back: back,
            kinds: kinds.join(' ')};
}"""
NBFILE=1
JS_HERE = """() => {
    var h = document.getElementById('nbpanel-root');
    var mark = h.querySelector('.nbmap-here');
    if (!mark) return {missing: true};
    var nb = document.querySelector('.jp-Notebook');
    var blocks = [];
    var nodes = [].slice.call(h.querySelectorAll('.nbmap-node[data-target]'));
    nodes.forEach(function(n){
      var id = n.getAttribute('data-target');
      if (document.getElementById(id)) return;
      var b = document.createElement('div');
      b.style.cssText = 'height:420px;position:relative';
      var sp = document.createElement('span');
      sp.id = id; sp.style.cssText = 'display:block;height:1px;position:relative';
      b.appendChild(sp); nb.appendChild(b); blocks.push(b);
    });
    nb.scrollTop = 0; window.__nbrailSync();
    var top = mark.style.left, on0 = mark.classList.contains('on');
    // The marker sits at the middle of the window, always. So "the timeline starts
    // on the Introduction bar" means: with the window scrolled fully left, its
    // middle falls on the first section bar.
    var map0 = h.querySelector('.nbmap');
    var f = h.querySelector('.nbmap-node');
    var fm = f.querySelector('.nbsect,.nbchapdot,.nbsubdot,.nbrail-dot');
    var firstX = f.offsetLeft + (fm ? fm.offsetLeft + fm.offsetWidth / 2 : 0);
    var atStart = Math.round(Math.abs(firstX - map0.clientWidth / 2));
    var width = Math.round(mark.getBoundingClientRect().width);
    var zMark = +getComputedStyle(mark).zIndex;
    var zNode = +getComputedStyle(h.querySelector('.nbmap-node')).zIndex;
    // whatever the marker covers turns white with it
    var painted = null, hit = h.querySelector('.nbmap-node.here');
    if (hit) {
      var m = hit.querySelector('.nbchapdot,.nbsubdot,.nbsect');
      var d = hit.querySelector('.nbrail-dot');
      painted = m ? getComputedStyle(m).backgroundColor
                  : (d ? getComputedStyle(d).borderTopColor : null);
    }
    nb.scrollTop = nb.scrollHeight; window.__nbrailSync();
    var bottom = mark.style.left;
    blocks.forEach(function(b){ b.remove(); });
    nb.scrollTop = 0;
    h.removeAttribute('data-doc');
    var map = h.querySelector('.nbmap'); if (map) map.scrollLeft = 0;
    window.__nbrailSync();
    return {top: top, bottom: bottom, on: on0, width: width, atStart: atStart,
            zMark: zMark, zNode: zNode, painted: painted};
}"""

"""Run the panel's REAL JavaScript against a mock JupyterLab DOM and check that
the host is created, filled and positioned. Console errors are fatal."""
import json, re, io, contextlib, re, sys, html as H
import matplotlib; matplotlib.use("Agg")
import IPython.display as ipd
CAP = {"js": [], "css": []}
class _Rec:
    def __init__(self, v, *a, **k): self.data = v
ipd.display = lambda *a, **k: None
src="\n".join(l for l in __import__("megasrc").expand("".join(max(json.load(open(__import__("sys").argv[1] if len(__import__("sys").argv)>1 else "Complex_Numbers_Step_by_Step.ipynb"))
              ["cells"], key=lambda c: len("".join(c["source"])))["source"])).splitlines() if not l.strip().startswith("%pip"))
G={"__name__":"__main__","display":lambda *a,**k:None}
with contextlib.redirect_stdout(io.StringIO()): exec(compile(src,"m","exec"),G)
# E28 (2026-10-12): the panel's dots = this notebook's exercises (Complex 7, the template 5)
# — behauptete bisher: fest ">= 7" (Complex)
_NDOTS = len(G["_TASKS"]["order"])

# capture what inject_style() actually emits: the CSS and the two scripts
class RH:
    def __init__(self,v): CAP["css"].append(v)
class RJ:
    def __init__(self,v): CAP["js"].append(v)
G["IHTML"]=RH; G["Javascript"]=RJ
G["inject_style"]()
css  = "".join(CAP["css"])
js   = "\n".join(CAP["js"])
print("captured: %d style block(s), %d script(s), %d chars of JS" % (len(CAP["css"]), len(CAP["js"]), len(js)))
if not js:
    print("NO JAVASCRIPT EMITTED"); sys.exit(1)

G["_PROG"]["final"] = True          # the panel that mounts is the finished one
# py-E26.1 (11.10.): the panel starts only next to OUR drawn widgets (10-rail
# gate, `.acc-root`) — the stand-in for JupyterLab carries the drawn root
# accordion (behauptete bisher: the panel starts in a page without any widget)
panel_html = G["_prog_html"]()
page = """<!doctype html><html><head><meta charset='utf-8'>%s</head>
<body data-jp-theme-light="false">
  <div class="jp-NotebookPanel jp-mod-current" style="width:100%%;height:800px">
    <div class="jp-Toolbar" style="height:40px">toolbar</div>
    <div class="jp-Notebook" style="height:700px;overflow:auto;width:100%%">
      <div class="jp-Cell"><div class="jp-OutputArea">%s<div class="jupyter-widgets widget-accordion acc-title acc-root"></div></div></div>
      <div style="height:2000px">filler</div>
    </div>
  </div>
</body></html>""" % (css, panel_html)
open("/tmp/jsmock.html","w").write(page)

from playwright.sync_api import sync_playwright
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg=b.new_page(viewport={"width":1200,"height":800}, device_scale_factor=2)
    pg.on("console", lambda m: errs.append("console.%s: %s" % (m.type, m.text)) if m.type=="error" else None)
    pg.on("pageerror", lambda e: errs.append("pageerror: %s" % e))
    # Vertical is the default now. The suite below measures the banner as well —
    # pad(), the reading marker, the centring — so it starts from the banner and
    # the vertical probes flip to the rail themselves.
    pg.goto("file:///tmp/jsmock.html"); pg.wait_for_timeout(50)
    pg.evaluate("() => { try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','h'); }"
                " catch(e){} }")
    pg.wait_for_timeout(150)
    print("orientation for this run:",
          pg.evaluate("() => { try { return localStorage.getItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1'); }"
                      " catch(e){ return 'BLOCKED'; } }"))
    # Reproduce the situation in a long-lived JupyterLite page: a PREVIOUS version
    # of this script is still running, with its old names and its own timers, and
    # it has no teardown hook. It hides any host it does not recognise and deletes
    # any .nbrail-host without its own marker — that was the flicker in the video.
    pg.evaluate("""() => {
        window.__nbrailWired = true;                       // the old guard flag
        window.__legacyTicks = 0;
        setInterval(function(){                            // old sync: finds nothing
            window.__legacyTicks++;
            var h = document.getElementById('nbrail-host');
            if (h) h.classList.remove('ready');
            document.querySelectorAll('.nbrail-host').forEach(function(x){
                if (!x.__src) x.remove();                  // destructive cleanup
            });
        }, 120);
    }""")
    res = pg.evaluate("(code) => { try { eval(code); return 'ok'; } catch (e) { return 'THREW: ' + e; } }", js)
    print("eval of the notebook's JS:", res)
    pg.wait_for_timeout(500)
    info = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var nb = document.querySelector('.jp-Notebook');
        return {host: !!h,
                ready: h ? h.classList.contains('ready') : null,
                dots: h ? h.querySelectorAll('.nbrail-dot').length : 0,
                fill: h ? h.querySelectorAll('.nbmap-fill').length : 0,
                top: h ? h.style.top : null, left: h ? h.style.left : null,
                parent: h ? h.parentElement.tagName : null,
                pad: nb ? nb.style.paddingTop : null,
                srcs: document.querySelectorAll('.nbfeed').length};
    }""")
    print("DOM after the script ran:", info)
    _armed = pg.evaluate("() => window.__nbrailVersion || null")
    print("version armed:", _armed)
    # 2026-09-25h — the panel's version was TYPED and stood at 25a through 25g;
    # a newer notebook then only fed an older panel. It comes from the toolkit now.
    if _armed != G["TOOLKIT_VERSION"]:
        errs.append("the panel arms as %r, the toolkit is %r — the handshake compares stale numbers"
                    % (_armed, G["TOOLKIT_VERSION"]))
    # let the legacy timers run and make sure they cannot touch the new panel
    pg.wait_for_timeout(1500)
    surv = pg.evaluate("""() => { var h=document.getElementById('nbpanel-root');
        return {ticks: window.__legacyTicks, host: !!h,
                ready: h ? h.classList.contains('ready') : false,
                dots: h ? h.querySelectorAll('.nbrail-dot').length : 0}; }""")
    print("after %d ticks of the OLD script:" % surv["ticks"], surv)
    # control: the legacy script IS destructive — a host with the old class dies
    pg.evaluate("""() => { var d=document.createElement('div');
        d.className='nbrail-host'; d.id='decoy'; document.body.appendChild(d); }""")
    pg.wait_for_timeout(500)
    decoy = pg.evaluate("() => !!document.getElementById('decoy')")
    print("control — a host with the OLD class survives the legacy script:", decoy)
    if decoy:
        errs.append("the legacy mock is not destructive, so the test proves nothing")
    if surv["ticks"] < 5: errs.append("the legacy script did not actually run")
    if not (surv["host"] and surv["ready"] and surv["dots"] >= _NDOTS):   # hw-E25.l: >= 7 (behauptete bisher >= 8: mit Quiz + eigene Daten)
        errs.append("the old script still interferes — panel would flicker")
    # the inline fallback must be visible until the script confirms it is alive
    vis = pg.evaluate("""(h) => {
        var d = document.createElement('div'); d.innerHTML = h;
        document.body.appendChild(d);
        var strip = d.querySelector('.nbprog');
        var before = getComputedStyle(strip).display;
        document.body.classList.remove('nbrail-live');
        var without = getComputedStyle(strip).display;
        document.body.classList.add('nbrail-live');
        d.remove();
        return {with_script: before, without_script: without};
    }""", panel_html)
    print("inline strip:", vis)

    # the timeline must SCROLL inside the panel, not be squeezed into it
    sc = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var m = h.querySelector('.nbmap');
        var st = getComputedStyle(m);
        return {overflowX: st.overflowX,
                clientW: Math.round(m.clientWidth),
                scrollW: Math.round(m.scrollWidth),
                scrollable: m.scrollWidth > m.clientWidth + 2,
                panelW: Math.round(h.getBoundingClientRect().width),
                scrollLeft: Math.round(m.scrollLeft)};
    }""")
    print("timeline window:", sc)
    if sc["overflowX"] not in ("auto", "scroll"):
        errs.append("the timeline does not scroll inside the panel (overflow-x=%s)" % sc["overflowX"])
    if not sc["scrollable"]:
        errs.append("the timeline fits entirely — the window cannot be demonstrated")

    # the window must travel to whichever exercise is current (smooth, so wait)
    pg.evaluate("""() => {
        var m = document.querySelector('#nbpanel-root .nbmap');
        m.scrollLeft = 0;
        var tasks = m.querySelectorAll('.nbmap-node.task');
        tasks.forEach(function(t){ t.classList.remove('is-current'); });
        tasks[tasks.length - 1].classList.add('is-current');
        window.__nbrailFollow(document.getElementById('nbpanel-root'), true);
    }""")
    pg.wait_for_timeout(700)
    atLast = pg.evaluate("() => Math.round(document.querySelector('#nbpanel-root .nbmap').scrollLeft)")
    pg.evaluate("""() => {
        var m = document.querySelector('#nbpanel-root .nbmap');
        var tasks = m.querySelectorAll('.nbmap-node.task');
        tasks.forEach(function(t){ t.classList.remove('is-current'); });
        tasks[0].classList.add('is-current');
        window.__nbrailFollow(document.getElementById('nbpanel-root'), true);
    }""")
    pg.wait_for_timeout(700)
    moved = pg.evaluate("""() => { var m = document.querySelector('#nbpanel-root .nbmap');
        return {atFirst: 0, atLast: %d, back: Math.round(m.scrollLeft),
                max: Math.round(m.scrollWidth - m.clientWidth)}; }""" % atLast)
    print("window travel:", moved)
    if moved["atLast"] <= moved["atFirst"]:
        errs.append("the window did not travel to the last exercise")
    if moved["back"] >= moved["atLast"]:
        errs.append("the window did not travel back to the first exercise")

    # a position the reader set by hand must survive the next sync
    pg.evaluate("""() => { var m=document.querySelector('#nbpanel-root .nbmap');
        m.style.scrollBehavior='auto'; m.scrollLeft = 0; }""")
    pg.evaluate("() => window.__nbrailSync && window.__nbrailSync()")
    pg.wait_for_timeout(300)
    stay = pg.evaluate("() => document.querySelector('#nbpanel-root .nbmap').scrollLeft")
    print("manual position after a sync:", round(stay))
    if stay > 5:
        errs.append("a manual scroll position is overwritten by the next sync")
    if vis["with_script"] != "none" or vis["without_script"] == "none":
        errs.append("the inline fallback does not appear when the script is absent")
    if not pg.evaluate("() => typeof window.__nbrailTeardown === 'function'"):
        errs.append("no teardown installed — a later version could not take over")

    # running the cell again must not leave two hosts or two observers behind
    pg.evaluate("(code) => { eval(code); }", js)
    pg.wait_for_timeout(300)
    hosts = pg.evaluate("() => document.querySelectorAll('.nbpanel-host').length")
    print("hosts after a second run:", hosts)
    if hosts != 1: errs.append("a second run produced %d hosts" % hosts)

    # the real order of events: the script is injected BEFORE the panel widget
    # exists, so it must pick the source up when it appears later
    pg.evaluate("""() => {
        document.getElementById('nbpanel-root').remove();
        document.querySelectorAll('.nbfeed').forEach(function(e){ e.remove(); });
    }""")
    pg.wait_for_timeout(200)
    pg.evaluate("(h) => { var d=document.createElement('div'); d.innerHTML=h;"
                "document.querySelector('.jp-OutputArea').appendChild(d); }", panel_html)
    pg.wait_for_timeout(700)
    late = pg.evaluate("""() => { var h=document.getElementById('nbpanel-root');
        return {host: !!h, ready: h ? h.classList.contains('ready') : false,
                dots: h ? h.querySelectorAll('.nbrail-dot').length : 0}; }""")
    print("source appearing AFTER the script:", late)
    if not (late["host"] and late["ready"] and late["dots"] >= _NDOTS):
        errs.append("the panel does not pick up a source that appears later")



    # ---- two tracks on one line: answers green, coding exercises purple -----
    fillinfo = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var inner = h.querySelector('.nbmap-inner');
        var fill  = h.querySelector('.nbmap-fill:not(.code)');
        var code  = h.querySelector('.nbmap-fill.code');
        var nodes = [].slice.call(inner.querySelectorAll('.nbmap-node'));
        var tasks = [].slice.call(inner.querySelectorAll('.nbmap-node.task'));
        function centre(n){ return Math.round(n.offsetLeft + n.offsetWidth / 2); }
        function chapBefore(node){
          var last = null;
          for (var i = 0; i < nodes.length; i++){
            if (nodes[i] === node) break;
            if (nodes[i].classList.contains('chap') || nodes[i].classList.contains('sect'))
              last = nodes[i];
          }
          return last;
        }
        function set(i, cls){ tasks[i].querySelector('.nbrail-dot').className = 'nbrail-dot ' + cls; }
        // the purple lane wraps its marker, so compare it on the CENTRE by taking
        // the wrap back off again
        function wrap(){
          var e = inner.querySelector('.nbmap-node.code-end');
          var m = e && e.querySelector('.nbrail-dot,.nbchapdot,.nbsubdot,.nbsect');
          return m ? m.offsetWidth / 2 + 3 : 0;
        }
        function widths(){ window.__nbrailGauge(h);
          return [Math.round(parseFloat(fill.style.width) || 0),
                  Math.round((parseFloat(code.style.width) || 0) - wrap())]; }

        tasks.forEach(function(t, i){ set(i, 'st-open'); });
        var fresh = widths();
        // answer 1 → green reaches exercise 2, purple stays on exercise 1
        set(0, 'st-ans');
        var afterAns = widths();
        // solve the coding route of 1 → purple follows to exercise 2
        set(0, 'st-both');
        var afterCode = widths();
        // skip exercise 2: the chapter opens, but the line stops at the chapter
        set(1, 'st-skip');
        var afterSkip = widths();
        var tl = h.querySelector('.nbmap-fill.tail');
        var tailShown = !!tl && parseFloat(tl.style.width || 0) > 4;
        var chap3 = chapBefore(tasks[2]);
        tasks.forEach(function(t, i){ set(i, 'st-both'); });
        var full = widths();
        tasks.forEach(function(t, i){ set(i, i === 0 ? 'st-ans' : 'st-open'); });
        window.__nbrailGauge(h);
        return {fresh: fresh, afterAns: afterAns, afterCode: afterCode,
                afterSkip: afterSkip, full: full,
                t1: centre(tasks[0]), t2: centre(tasks[1]), t3: centre(tasks[2]),
                chap1: centre(chapBefore(tasks[0])), chap3: centre(chap3),
                span: Math.round(inner.scrollWidth),
                x0: Math.round(parseFloat(getComputedStyle(inner).getPropertyValue('--rail-x0')) || 0),
                f0: Math.round(parseFloat(getComputedStyle(inner).getPropertyValue('--fill-x0')) || 0),
                f1: (function(){ var a = inner.querySelector('.nbmap-ahead');
                       return a ? Math.round(parseFloat(a.style.left) +
                                             parseFloat(a.style.width)) : 0; })(),
                fillLeft: getComputedStyle(fill).left,
                tailShown: tailShown,
                introPassed: !!inner.querySelector('.nbmap-node.passed'),
                sectPassed: !!inner.querySelector('.nbmap-node.sect.passed'),
                railW: Math.round(parseFloat(getComputedStyle(inner).getPropertyValue('--rail-w')) || 0),
                trackLeft: getComputedStyle(inner, '::before').left,
                firstMark: centre(nodes[0]), lastMark: centre(nodes[nodes.length - 1]),
                codeTop: getComputedStyle(code).top, greenTop: getComputedStyle(fill).top,
                codeBg: (getComputedStyle(code).backgroundColor + ' ' +
                         getComputedStyle(code).boxShadow).slice(0, 60)};
    }""")
    print("two tracks:", fillinfo)
    # the fills start where the TRACK starts, so a marker at x is reached when the
    # fill is x - x0 wide
    # the lanes start at the section bar of the block that holds the first exercise,
    # not at the very first marker — Introduction has nothing to solve
    X0 = fillinfo["f0"]
    for _k in ("t1", "t2", "t3", "chap1", "chap3"):
        fillinfo[_k] -= X0
    # a fresh notebook: exercise 1 is unlocked from the start, so both lines end
    # on its circle
    if abs(fillinfo["fresh"][0] - fillinfo["t1"]) > 3 or abs(fillinfo["fresh"][1] - fillinfo["t1"]) > 3:
        errs.append("a fresh notebook does not start both lines at exercise 1 (%s vs %d)"
                    % (fillinfo["fresh"], fillinfo["t1"]))
    if abs(fillinfo["afterAns"][0] - fillinfo["t2"]) > 3:
        errs.append("answering exercise 1 does not take the green line to exercise 2 (%d vs %d)"
                    % (fillinfo["afterAns"][0], fillinfo["t2"]))
    if fillinfo["afterAns"][1] >= fillinfo["afterAns"][0]:
        errs.append("the purple line ran ahead without a coding solution (%s)"
                    % fillinfo["afterAns"])
    if abs(fillinfo["afterCode"][1] - fillinfo["t2"]) > 3:
        errs.append("solving the coding route does not move the purple line (%d vs %d)"
                    % (fillinfo["afterCode"][1], fillinfo["t2"]))
    # after a skip the lane runs ON to the circle you are standing at — the colour
    # of the last stretch is what says it was skipped
    if abs(fillinfo["afterSkip"][0] - fillinfo["t3"]) > 3:
        errs.append("after a skip the line does not reach the exercise you are on (%d vs %d)"
                    % (fillinfo["afterSkip"][0], fillinfo["t3"]))
    # The stripe is gone on purpose: a skip is a fact about ONE exercise, and its
    # circle carries the amber ring that says so. The road behind it leads to a
    # chapter that IS open, so it is green like any other.
    if fillinfo["tailShown"]:
        errs.append("the skipped stretch is still painted onto the progress bar")
    # everything solved fills the EXERCISE BLOCK — Appendix and Introduction never
    _want = fillinfo["f1"] - fillinfo["f0"]
    if abs(fillinfo["full"][0] - _want) > 3 or abs(fillinfo["full"][1] - _want) > 3:
        errs.append("everything solved does not fill the rest of the timeline (%s of %d)"
                    % (fillinfo["full"], _want))
    if fillinfo["f0"] <= fillinfo["x0"]:
        errs.append("the lanes start at the very first marker, so Introduction is "
                    "filled by a progress made elsewhere (%d vs %d)"
                    % (fillinfo["f0"], fillinfo["x0"]))
    if fillinfo["fillLeft"] != str(fillinfo["f0"]) + "px":
        errs.append("the painted lane ignores its own start (%s vs %dpx)"
                    % (fillinfo["fillLeft"], fillinfo["f0"]))
    if fillinfo["sectPassed"]:
        errs.append("a section bar took the progress colour")
    # the track itself runs from the first marker to the last, and no further
    if abs(fillinfo["x0"] - fillinfo["firstMark"]) > 1:
        errs.append("the track does not start on the first marker (%d vs %d)"
                    % (fillinfo["x0"], fillinfo["firstMark"]))
    if abs(fillinfo["x0"] + fillinfo["railW"] - fillinfo["lastMark"]) > 1:
        errs.append("the track does not end on the last marker (%d vs %d)"
                    % (fillinfo["x0"] + fillinfo["railW"], fillinfo["lastMark"]))
    if fillinfo["trackLeft"] != str(fillinfo["x0"]) + "px":
        errs.append("the painted track ignores the measured start (%s vs %dpx)"
                    % (fillinfo["trackLeft"], fillinfo["x0"]))

    # ---- the gaps between the three blocks -----------------------------------
    # A gap runs from the CENTRE of the last marker of one block to the CENTRE of
    # the next section's bar, it covers both lanes including the glow, and it never
    # paints over a marker.
    gaps = pg.evaluate("""() => {
        var inner = document.querySelector('#nbpanel-root .nbmap-inner');
        var nodes = [].slice.call(inner.querySelectorAll('.nbmap-node'));
        function mid(n){ return Math.round(n.offsetLeft + n.offsetWidth / 2); }
        var want = [], prev = null;
        nodes.forEach(function(n){
          if (n.classList.contains('sect') && prev) want.push([mid(prev), mid(n)]);
          prev = n;
        });
        var bars = [].slice.call(inner.querySelectorAll('.nbmap-gap')).map(function(b){
          return [Math.round(parseFloat(b.style.left)),
                  Math.round(parseFloat(b.style.left) + parseFloat(b.style.width))];
        });
        var gz = bars.length ? +getComputedStyle(inner.querySelector('.nbmap-gap')).zIndex : 0;
        var nz = +getComputedStyle(nodes[0]).zIndex;
        var fz = +getComputedStyle(inner.querySelector('.nbmap-fill')).zIndex;
        var cz = +getComputedStyle(inner.querySelector('.nbmap-fill.code')).zIndex;
        return {want: want, bars: bars, gz: gz, nz: nz, fz: fz, cz: cz,
                glow: getComputedStyle(inner.querySelector('.nbmap-fill.code')).boxShadow};
    }""")
    print("gaps:", {k: v for k, v in gaps.items() if k != "glow"})
    # THE LINE IS ONE CONTINUOUS RUN NOW. The gaps used to cut it into three
    # blocks; the landmarks say where a block begins, and the line does not have
    # to be broken for that. So there must be NONE.
    if gaps["bars"]:
        errs.append("the line is cut into pieces again: %s" % (gaps["bars"],))
    if not (gaps["cz"] < gaps["fz"] < gaps["nz"]):
        errs.append("wrong stacking: glow %d, green %d, gap %d, node %d"
                    % (gaps["cz"], gaps["fz"], gaps["gz"], gaps["nz"]))
    # THE PANEL IS QUIET NOW. The coding lane used to carry a violet glow; the
    # document beside it has no glows at all, and an instrument that shouts next
    # to a page that does not is the thing that made the whole screen restless.
    # The lane is still there, still violet, still its own width — flat.
    if gaps["glow"] and gaps["glow"] != "none":
        errs.append("the coding lane is glowing again (%s)" % gaps["glow"])
    if fillinfo["greenTop"] == fillinfo["codeTop"]:
        errs.append("both lines sit at the same height — they would cover each other")
    # E34 (Hauptwerkstatt, 19.10.): digi is the standard now — its code colour is rosa
    # (#c2338f light, #ff7bd5 dark); behauptete bisher nur Violett (minimal/cyber/fairy)
    if not any(c in fillinfo["codeBg"] for c in
               ("123, 79, 189", "155, 124, 203", "170, 138, 219",
                "150, 92, 246", "139, 79, 242", "194, 51, 143", "255, 123, 213")):
        errs.append("the coding glow is not purple (%s)" % fillinfo["codeBg"])

    # ---- markers sit ON the axis, spacing follows the content ------------------
    geo = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var inner = h.querySelector('.nbmap-inner');
        var ir = inner.getBoundingClientRect();
        var axis = null, off = [], widths = {};
        inner.querySelectorAll('.nbmap-node').forEach(function(n){
            var m = n.querySelector('.nbrail-dot,.nbchapdot,.nbsubdot,.nbsect');
            if (!m) return;
            var r = m.getBoundingClientRect();
            var c = r.top + r.height / 2 - ir.top;
            if (axis === null) axis = c;
            off.push(Math.abs(c - axis));
            var k = n.className.indexOf('chap') >= 0 ? 'chap' : 'other';
            if (k === 'chap') widths[n.title] = Math.round(n.getBoundingClientRect().width);
        });
        var w = Object.keys(widths).map(function(k){ return widths[k]; });
        return {maxOffset: Math.round(Math.max.apply(null, off)),
                chapWidths: w, spread: Math.max.apply(null, w) - Math.min.apply(null, w)};
    }""")
    _STRUCT_W = [e.get("weight", 0) for e in G["_STRUCT"]
                 if e.get("kind") == "chapter"]
    print("markers on the axis:", geo, "| content weights:", _STRUCT_W)
    if geo["maxOffset"] > 1:
        errs.append("markers are %dpx off the axis" % geo["maxOffset"])
    # Spacing follows the CONTENT, so it can only spread when the chapters
    # differ in length. Notebook 0's seven chapters are deliberately the same
    # size; requiring a spread there would be requiring a lie.
    _wspread = (max(_STRUCT_W) - min(_STRUCT_W)) / max(1.0, float(max(_STRUCT_W))) \
               if _STRUCT_W else 0.0
    if _wspread > 0.25 and geo["spread"] < 10:
        errs.append("chapter spacing does not follow the content (widths %s, "
                    "content spread %.0f%%)" % (geo["chapWidths"], 100 * _wspread))

    # ---- one axis for the panel and the notebook body -------------------------
    # The panel hangs on the centre of the notebook's scroll viewport, and the
    # content column is centred in the same box — at any window width, and in
    # full screen. The blue cell gutter is what used to pull the content aside.
    def axis_check(width):
        pg.set_viewport_size({"width": width, "height": 800})
        pg.wait_for_timeout(400)
        return pg.evaluate("""() => {
            var h = document.getElementById('nbpanel-root');
            var nb = document.querySelector('.jp-Notebook');
            var r = nb.getBoundingClientRect();
            var hr = h.getBoundingClientRect();
            return {want: Math.round(r.left + nb.clientWidth / 2),
                    got: Math.round(hr.left + hr.width / 2),
                    left: h.style.left};
        }""")
    for w in (1200, 980, 1440):
        a = axis_check(w)
        print("axis at %dpx:" % w, a)
        if abs(a["want"] - a["got"]) > 2:
            errs.append("at %dpx the panel is %dpx off the notebook axis"
                        % (w, a["got"] - a["want"]))
    pg.set_viewport_size({"width": 1200, "height": 800})
    pg.wait_for_timeout(300)
    gutter = pg.evaluate("""() => {
        var c = document.querySelector('.jp-Cell');
        var pr = document.createElement('div'); pr.className = 'jp-InputPrompt'; c.appendChild(pr);
        var co = document.createElement('div'); co.className = 'jp-Collapser'; c.appendChild(co);
        var out = {prompt: getComputedStyle(pr).display,
                   collapser: getComputedStyle(co).width};
        pr.remove(); co.remove();
        return out;
    }""")
    print("cell gutter:", gutter)
    if gutter["prompt"] != "none":
        errs.append("the [ ]: prompt still takes the left gutter")
    if float(gutter["collapser"].replace("px", "")) > 6:
        errs.append("the blue cell bar is still %s wide" % gutter["collapser"])


    # ---- the timeline has a fixed length, set by the content -----------------
    spacing = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var inner = h.querySelector('.nbmap-inner');
        var nodes = [].slice.call(inner.querySelectorAll('.nbmap-node'));
        function widths(){ return nodes.map(function(n){
            return Math.round(n.getBoundingClientRect().width); }); }
        var before = widths(), total = inner.scrollWidth;
        // the document grows by 3000px — the timeline must not care
        var grow = document.createElement('div');
        grow.style.height = '3000px';
        document.querySelector('.jp-Notebook').appendChild(grow);
        window.__nbrailSync();
        var after = widths(), total2 = inner.scrollWidth;
        grow.remove();
        var chap = [];
        nodes.forEach(function(n, i){ if (n.classList.contains('chap')) chap.push(before[i]); });
        return {same: JSON.stringify(before) === JSON.stringify(after),
                total: total, total2: total2,
                chapMin: Math.min.apply(null, chap), chapMax: Math.max.apply(null, chap)};
    }""")
    print("timeline length:", spacing)
    if not spacing["same"] or spacing["total"] != spacing["total2"]:
        errs.append("the timeline changed when the document grew (%s)" % spacing)
    if spacing["chapMax"] - spacing["chapMin"] < 8:
        errs.append("chapter spacing does not follow the content (%d..%d)"
                    % (spacing["chapMin"], spacing["chapMax"]))

    wheel = pg.evaluate("""() => {
        var map = document.querySelector('#nbpanel-root .nbmap');
        map.style.scrollBehavior = 'auto';
        map.scrollLeft = 0;
        // the wheel is applied once per FRAME now, so each step has to be
        // given a frame before it is read
        map.dispatchEvent(new WheelEvent('wheel', {deltaY: 240, bubbles: true, cancelable: true}));
        return new Promise(function(res){ requestAnimationFrame(function(){
          requestAnimationFrame(function(){
            var down = map.scrollLeft;
            map.dispatchEvent(new WheelEvent('wheel',
                {deltaY: -240, bubbles: true, cancelable: true}));
            requestAnimationFrame(function(){ requestAnimationFrame(function(){
              res({down: Math.round(down), up: Math.round(map.scrollLeft),
                   bar: Math.round(map.offsetHeight - map.clientHeight)});
            }); });
          }); }); });
    }""")
    print("wheel over the panel:", wheel)
    if wheel["down"] <= 0:
        errs.append("the wheel does not move the timeline to the right")
    if wheel["up"] >= wheel["down"]:
        errs.append("the wheel does not move the timeline back to the left")
    # headless Chromium draws overlay scrollbars, so the bar takes no layout space
    # here — check the rule that makes it permanent instead
    if "scrollbar-width:auto" not in css.replace(" ", ""):
        errs.append("the timeline scrollbar is still set to 'thin'")
    import re as _re
    _m = _re.search(r"\.nbmap::-webkit-scrollbar\{height:(\d+)px", css.replace(" ", ""))
    if not _m or int(_m.group(1)) < 9:
        errs.append("the timeline scrollbar is thinner than its hover size")


    # ---- a jump lands under the panel, and opens what is collapsed -----------
    jump = pg.evaluate("""() => {
        var nb = document.querySelector('.jp-Notebook');
        var node = document.querySelector("#nbpanel-root .nbmap-node[data-target]");
        var id = node.getAttribute('data-target');
        // build a target far down the notebook: an anchor plus the pill it marks
        var old = document.getElementById(id); if (old) old.remove();
        var spacer = document.createElement('div'); spacer.style.height = '1200px';
        var span = document.createElement('span');
        span.id = id; span.style.cssText = 'display:block;height:0;position:relative;top:-56px';
        var pill = document.createElement('div');
        pill.id = 'jumptarget';
        pill.style.cssText = 'height:40px;background:#345;margin:0 auto;width:300px';
        nb.appendChild(spacer); nb.appendChild(span); nb.appendChild(pill);
        var tail = document.createElement('div'); tail.style.height = '1600px';
        nb.appendChild(tail);
        nb.scrollTop = 0;
        node.click();
        return {clicked: id};
    }""")
    pg.wait_for_timeout(900)
    landed = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var p = document.getElementById('jumptarget').getBoundingClientRect();
        // the RAIL is the panel now; the host is a transparent layer
        var hb = h.querySelector('.nbrail').getBoundingClientRect();
        return {targetTop: Math.round(p.top), panelBottom: Math.round(hb.bottom),
                delta: Math.round(p.top - hb.bottom)};
    }""")
    print("jump target position:", landed)
    if not (0 <= landed["delta"] <= 60):
        errs.append("a jump does not land the target under the panel (%dpx off)"
                    % landed["delta"])

    # 2026-09-24at — AND THE READER CAN LEAVE MID-LANDING.
    # A click schedules landing passes for 1.4s. They used to keep writing
    # scrollTop, so a reader who scrolled away in that window was dragged back
    # and the page felt stuck. One wheel event has to end the landing, and the
    # test scrolls at 300ms — while the passes are still due — and then watches
    # whether the document stays where it was put.
    interrupt = pg.evaluate("""() => {
        var sc = document.querySelector('.jp-WindowedPanel-outer')
              || document.querySelector('.jp-Notebook');
        var a = document.querySelector('#nbpanel-root a.nbjump.nbmap-node.chap');
        if (!a || !sc) return null;
        sc.scrollTop = 0;
        a.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
        window.__sc = sc;
        return true;
    }""")
    if interrupt:
        pg.wait_for_timeout(300)                     # mid-landing, on purpose
        pg.evaluate("""() => {
            var sc = window.__sc;
            // a real wheel over the document, which is what a reader does
            sc.dispatchEvent(new WheelEvent('wheel', {deltaY: 600, bubbles: true}));
            window.__mine = sc.scrollTop + 900;
            sc.scrollTop = window.__mine;
            sc.dispatchEvent(new Event('scroll', {bubbles: true}));
        }""")
        drift = []
        for _ in range(6):
            pg.wait_for_timeout(280)
            drift.append(pg.evaluate(
                "() => Math.round(window.__sc.scrollTop - window.__mine)"))
        print("scrolling away from a landing:", drift)
        # JupyterLab's own virtualisation nudges scrollTop by a few dozen px as
        # cells are realised; being pulled back to the landing is hundreds.
        if min(drift) < -200:
            errs.append("a click holds the document: it was pulled back %dpx "
                        "after the reader scrolled away" % -min(drift))

    # ---- the theme button darkens the whole surface, not only our boxes -----
    # The switch cross-fades over ~0.85s now, so every reading is taken once
    # the fade has finished — an immediate read catches the old colour.
    theme = pg.evaluate("""() => {
        // the button switches OUR override; start from a light front end, which is
        // what JupyterLite serves by default.
        // 2026-09-25 — AND THE START IS SET THROUGH THE PREFERENCE, NOT BY HAND.
        // This probe used to strip `nbdark` off the body and change the front
        // end's attribute, and it relied on the front-end change WIPING the
        // reader's stored choice to keep the class off. That wipe was the bug
        // ("the Jupyter theme interferes with the design settings"), so it is
        // gone, and a hand-removed class is now put straight back by the very
        // next applyTheme(). The honest way to start from light is to say light.
        try { window.__nbStore.set('digichemjn.theme.v1', 'light'); } catch (e) {}
        document.body.setAttribute('data-jp-theme-light', 'true');
        if (window.__nbApplyTheme) window.__nbApplyTheme();
        document.querySelector('.jp-Notebook').style.background = '';
        return getComputedStyle(document.querySelector('.jp-Notebook')).backgroundColor;
    }""")
    theme = {"before": theme}
    # 2026-09-24m: the switch is INSTANT. The colour is read in the SAME
    # evaluate as the click, with no frame in between — if a transition were
    # still armed, this would still be the light colour.
    theme.update(pg.evaluate("""() => {
        document.querySelector('#nbpanel-root .nbtheme').click();
        return {instant: getComputedStyle(document.querySelector('.jp-Notebook')).backgroundColor,
                fading: document.body.classList.contains('nbtheming')};
    }"""))
    pg.wait_for_timeout(300)
    theme.update(pg.evaluate("""() => ({
        cls: document.body.className,
        after: getComputedStyle(document.querySelector('.jp-Notebook')).backgroundColor,
        faded: !document.body.classList.contains('nbtheming')
    })"""))
    pg.evaluate("() => document.querySelector('#nbpanel-root .nbtheme').click()")
    pg.wait_for_timeout(300)
    theme.update(pg.evaluate("""() => {
        var back = getComputedStyle(document.querySelector('.jp-Notebook')).backgroundColor;
        document.body.setAttribute('data-jp-theme-light', 'false');
        return {back: back};
    }"""))
    print("theme button:", theme)
    if "nbdark" not in theme["cls"] or "nbforce-dark" not in theme["cls"]:
        errs.append("the theme button does not switch the surface (%s)" % theme["cls"])
    if theme["after"] == theme["before"]:
        errs.append("the notebook surface stayed %s when switching to dark" % theme["before"])
    if theme["instant"] == theme["before"]:
        errs.append("the theme switch is not instant — the surface was still %s "
                    "in the frame of the click" % theme["before"])
    # 2026-09-24y: `nbtheming` changed meaning. It used to ARM a cross-fade, so
    # the test wanted it absent. It now SUPPRESSES every transition for the
    # frame of the switch — which is what stops the boxes arriving a third of a
    # second after the rest of the window — so it has to be there at the click
    # and gone again shortly after.
    if not theme["fading"]:
        errs.append("the theme switch does not suppress transitions (no nbtheming)")
    if not theme["faded"]:
        errs.append("nbtheming was never taken off again")
    if theme["back"] != theme["before"]:
        errs.append("switching back did not restore the light surface")

    # ---- 2026-10-02 (E15.3): JupyterLab's theme switch WINS -----------------
    # THIS TEST BEHAUPTETE BISHER (2026-09-25 to v1.51) the opposite: "a
    # front-end switch must NOT change the stored choice". That was green
    # BECAUSE of the fault the user reported on 02.10.: once dark, a light
    # JupyterLab (Settings → Theme) stayed dark — measured in the real Lab,
    # both ways, also after a reload. New rule (user, E15.3): after every
    # switch of the front end our surfaces follow it, and the stored choice
    # becomes the front end's; ◐ still sets it while the front end stands.
    # The skin still has to survive the move. The old reasoning follows.
    # The reported symptom was "the Jupyter theme still interferes with the
    # design settings". The mechanism was one line in the theme observer:
    # `setThemePref('')` — a switch in JupyterLab's Settings menu DELETED the
    # notebook's own brightness, which then fell back to the front end's. So the
    # test is: choose dark, move the front end to light, and the document must
    # still be dark; choose light, move the front end to dark, still light. And
    # the skin has to survive the same move, because the skins' light halves
    # used to be keyed on the front-end attribute as well.
    indep = pg.evaluate("""() => {
        var read = function(){
            return {dark: document.body.classList.contains('nbdark'),
                    pref: (function(){ try {
                        return window.__nbStore.get('digichemjn.theme.v1'); }
                        catch (e) { return null; } })(),
                    skinLight: getComputedStyle(document.body)
                                 .getPropertyValue('--nbskin-surf').trim()};
        };
        try { window.__nbStore.set('digichemjn.skin.v1', 'fairy'); } catch (e) {}
        if (window.__nbApplySkin) window.__nbApplySkin();
        // the reader chooses DARK, the front end then goes LIGHT
        try { window.__nbStore.set('digichemjn.theme.v1', 'dark'); } catch (e) {}
        window.__nbApplyTheme();
        var chose = read();
        document.body.setAttribute('data-jp-theme-light', 'true');
        document.body.setAttribute('data-jp-theme-name', 'JupyterLab Light');
        return {chose: chose, later: null};
    }""")
    pg.wait_for_timeout(200)           # let the observer run
    indep["later"] = pg.evaluate("""() => ({
        dark: document.body.classList.contains('nbdark'),
        pref: (function(){ try {
            return window.__nbStore.get('digichemjn.theme.v1'); }
            catch (e) { return null; } })(),
        skinLight: getComputedStyle(document.body)
                     .getPropertyValue('--nbskin-surf').trim(),
        skin: document.body.className.indexOf('nbskin-fairy') > -1
    })""")
    # ...and the mirror image
    _mc = pg.evaluate("""() => {
        try { window.__nbStore.set('digichemjn.theme.v1', 'light'); } catch (e) {}
        window.__nbApplyTheme();
        return !document.body.classList.contains('nbdark');
    }""")
    pg.evaluate("""() => {
        document.body.setAttribute('data-jp-theme-light', 'false');
        document.body.setAttribute('data-jp-theme-name', 'JupyterLab Dark');
    }""")
    pg.wait_for_timeout(200)
    indep["mirror"] = pg.evaluate("""() => ({
        dark: document.body.classList.contains('nbdark'),
        pref: (function(){ try {
            return window.__nbStore.get('digichemjn.theme.v1'); }
            catch (e) { return null; } })()
    })""")
    indep["mirror"]["chose"] = _mc
    print("the front end's switch wins:", indep)
    if not indep["chose"]["dark"]:
        errs.append("choosing dark did not darken the document")
    if indep["later"]["dark"] or indep["later"]["pref"] != "light":
        errs.append("a LIGHT front end left the document dark "
                    "(dark %r, pref %r)" % (indep["later"]["dark"], indep["later"]["pref"]))
    if not indep["later"]["skin"]:
        errs.append("the skin was lost when the front end's theme changed")
    if indep["later"]["skinLight"] == indep["chose"]["skinLight"] == "":
        errs.append("the skin palette is empty — --nbskin-surf resolves to nothing")
    if not indep["mirror"]["chose"]:
        errs.append("◐ light under a light front end did not hold")
    if not indep["mirror"]["dark"] or indep["mirror"]["pref"] != "dark":
        errs.append("a DARK front end left the document light "
                    "(dark %r, pref %r)" % (indep["mirror"]["dark"], indep["mirror"]["pref"]))
    # leave the page as the rest of the suite expects it
    pg.evaluate("""() => {
        try { window.__nbStore.del('digichemjn.skin.v1');
              window.__nbStore.set('digichemjn.theme.v1', 'light'); } catch (e) {}
        document.body.removeAttribute('data-jp-theme-name');
        if (window.__nbApplySkin) window.__nbApplySkin();
        window.__nbApplyTheme();
    }""")
    pg.wait_for_timeout(120)


    # ---- the settings drawer borrows the notebook's real controls ------------
    drawer = pg.evaluate("""() => {
        // put the three control widgets into the mock notebook, as the real one does
        var out = document.querySelector('.jp-OutputArea');
        ['nbctl-difficulty', 'nbctl-code', 'nbctl-reset',
         'nbctl-seed', 'nbctl-unl'].forEach(function(c){
            if (document.querySelector('.' + c)) return;
            var d = document.createElement('div');
            d.className = c; d.id = 'src-' + c;
            d.innerHTML = '<select><option>standard</option></select>';
            out.appendChild(d);
        });
        var h = document.getElementById('nbpanel-root');
        var before = h.classList.contains('open');
        h.querySelector('.nbprofile').click();
        var slots = [].slice.call(h.querySelectorAll('.nbslot')).map(function(s){
            var k = s.firstElementChild;
            return k ? k.className : null;
        });
        return {wasOpen: before, open: h.classList.contains('open'), slots: slots,
                moved: document.querySelectorAll('.nbctl-moved').length,
                sameNode: document.getElementById('src-nbctl-code') ===
                          h.querySelector("[data-slot='nbctl-code']").firstElementChild,
                series: (h.querySelector('.nbserieslist') || {}).textContent};
    }""")
    print("settings drawer:", drawer)
    if not drawer["open"]:
        errs.append("the gear does not open the drawer")
    if drawer["slots"].count(None):
        errs.append("a drawer slot stayed empty: %s" % drawer["slots"])
    if not drawer["sameNode"]:
        errs.append("the drawer shows a copy, not the notebook's own control")
    if drawer["moved"] < 3:
        errs.append("the notebook does not say where its controls went (%d notes)"
                    % drawer["moved"])
    # 2026-09-28a (K1) — the gear drawer lent the chapter lock's "Skip it, open
    # this chapter" (slot nbctl-unl), and the panel had a lock window at the
    # top (pg-lock). Both were skip ways outside the exercise; both are gone.
    _k1 = pg.evaluate("""() => { var h = document.getElementById('nbpanel-root');
        return {unl: !!h.querySelector("[data-slot='nbctl-unl']"),
                lockPage: !!h.querySelector('.pg-lock, .nblock-slot')}; }""")
    if _k1["unl"]: errs.append("K1: the gear drawer still has a slot for the lock's skip button")
    if _k1["lockPage"]: errs.append("K1: the panel still has a lock window (pg-lock)")

    # the borrowed widgets must survive a panel rebuild
    pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        h.removeAttribute('data-sig');           // force patch() to rebuild
        window.__nbrailSync();
    }""")
    pg.wait_for_timeout(400)
    alive = pg.evaluate("""() => ({
        stillThere: !!document.getElementById('src-nbctl-code'),
        inPanel: !!document.querySelector("#nbpanel-root [data-slot='nbctl-code'] > *"),
        count: document.querySelectorAll('.nbctl-code').length })""")
    print("after a panel rebuild:", alive)
    if not alive["stillThere"]:
        errs.append("a rebuild destroyed the borrowed widget")
    if alive["count"] != 1:
        errs.append("the borrowed widget was duplicated (%d copies)" % alive["count"])


    # ---- the controls show their state, and the wheel stays on the timeline --
    states = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var map = h.querySelector('.nbmap');
        map.style.scrollBehavior = 'auto'; map.scrollLeft = 120;
        // over the drawer the wheel must NOT move the timeline
        h.classList.add('open');
        var dr = h.querySelector('.nbdrawer');
        dr.dispatchEvent(new WheelEvent('wheel', {deltaY: 240, bubbles: true, cancelable: true}));
        var afterDrawer = map.scrollLeft;
        h.querySelector('.nbprofile').dispatchEvent(
            new WheelEvent('wheel', {deltaY: 240, bubbles: true, cancelable: true}));
        var afterButton = map.scrollLeft;
        map.dispatchEvent(new WheelEvent('wheel', {deltaY: 240, bubbles: true, cancelable: true}));
        // the wheel lands on the next frame, so flush it by hand
        if (window.__nbrailWheelRaf) { cancelAnimationFrame(window.__nbrailWheelRaf);
          window.__nbrailWheelRaf = 0;
          map.scrollLeft += (window.__nbrailWheelAcc || 0);
          window.__nbrailWheelAcc = 0; }
        var afterMap = map.scrollLeft;
        // getComputedStyle returns a LIVE object — read the value out at once
        // R3 · 17 Teil 2: in a corner the chip's shadow is the chip's own;
        // an open drawer shows on its widget as aria-pressed (border, ink)
        var LOOK = function(e){ var c = getComputedStyle(e);
          return [c.boxShadow, c.borderTopColor, c.color, e.getAttribute('aria-pressed')].join(' | '); };
        var pg0 = h.dataset.page; h.dataset.page = 'code';
        window.__nbCornerPressed && window.__nbCornerPressed();
        var gearOn = LOOK(h.querySelector('.nbprofile'));
        h.classList.remove('open');
        window.__nbCornerPressed && window.__nbCornerPressed();
        var gearOff = LOOK(h.querySelector('.nbprofile'));
        if (pg0) h.dataset.page = pg0; else delete h.dataset.page;
        h.classList.add('fs');
        var fullOn = getComputedStyle(h.querySelector('.nbfull')).boxShadow;
        h.classList.remove('fs');
        // The theme button lights one side, and the side changes with the theme.
        // 2026-09-24ac: the reader's own choice outranks the front end's
        // attribute now, so an earlier check that left `nbforce-light` behind
        // would (correctly) suppress every dark rule here. The attribute is
        // only the front end's opinion — clear the reader's before reading it.
        // 2026-09-25: brightness is `nbdark` and nothing else. Toggling the
        // front end's attribute here used to change our colours; it no longer
        // does, which is the point — so the probe says which brightness it
        // wants instead of asking JupyterLab to say it for us.
        var wasDark = document.body.classList.contains('nbdark');
        document.body.classList.remove('nbdark', 'nbforce-light', 'nbforce-dark');
        window.__nbCornerPressed && window.__nbCornerPressed();
        var themeLight = LOOK(h.querySelector('.nbtheme'));
        document.body.classList.add('nbdark');
        window.__nbCornerPressed && window.__nbCornerPressed();
        var themeDark = LOOK(h.querySelector('.nbtheme'));
        document.body.classList.toggle('nbdark', wasDark);
        var track = getComputedStyle(h.querySelector('.nbmap-inner'), '::before').height;
        return {afterDrawer: Math.round(afterDrawer), afterButton: Math.round(afterButton),
                afterMap: Math.round(afterMap),
                gearOn: gearOn, gearOff: gearOff, fullOn: fullOn,
                themeLight: themeLight, themeDark: themeDark, track: track,
                lastBadge: !!h.querySelector('.nbdiff'),
                chapDot: Math.round(h.querySelector('.nbchapdot').getBoundingClientRect().width),
                subDot: Math.round(h.querySelector('.nbsubdot').getBoundingClientRect().width),
                circle: Math.round(h.querySelector('.nbrail-dot').getBoundingClientRect().width),
                series: getComputedStyle(h.querySelector('.nbserieslist')).color};
    }""")
    print("control states:", {k: (v[:46] if isinstance(v, str) else v) for k, v in states.items()})
    if states["afterDrawer"] != 120 or states["afterButton"] != 120:
        errs.append("the wheel scrolls the timeline from outside it (%s)" % states)
    if states["afterMap"] <= 120:
        errs.append("the wheel no longer scrolls the timeline itself")
    if states["gearOn"] == states["gearOff"] or "none" in states["gearOn"]:
        errs.append("the gear does not light up while the drawer is open")
    if "none" in states["fullOn"]:
        errs.append("the full screen button does not light up while full screen is on")
    if states["themeLight"] == states["themeDark"]:
        errs.append("the theme button lights the same side in both themes")
    _track = float(states["track"].replace("px", ""))
    if _track > 10:
        errs.append("the timeline line is %s thick" % states["track"])
    # 2026-09-24r: the control's floor is half size, so at 0 % the line is 4px
    # and the chapter dot 6.5 — the dot must still be clearly the wider mark,
    # which is a ratio, not a fixed number of pixels.
    if states["chapDot"] < _track * 1.4:
        errs.append("a chapter dot (%dpx) does not stand out from the line (%s)"
                    % (states["chapDot"], states["track"]))
    if states["chapDot"] <= states["subDot"]:
        errs.append("chapter dots are not bigger than the intro/appendix dots (%d vs %d)"
                    % (states["chapDot"], states["subDot"]))
    if states["lastBadge"]:
        errs.append("the rightmost badge is still there")

    # ---- the drawer opens INSIDE the panel, not on top of the document -------
    push = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var nb = document.querySelector('.jp-Notebook');
        function state(){ return {pad: nb.style.paddingTop,
                                  h: document.documentElement.style.getPropertyValue('--nbpanel-h')}; }
        var open0 = h.classList.contains('open');
        if (open0) h.querySelector('.nbprofile').click();
        window.__nbrailSync();
        var shut = state();
        h.querySelector('.nbprofile').click();
        window.__nbrailSync();
        var open = state();
        h.querySelector('.nbprofile').click(); window.__nbrailSync();
        return {shut: shut, open: open,
                drawerGrew: h.querySelector('.nbdrawer').getBoundingClientRect().height};
    }""")
    # leftovers from the wheel probes (a pending scrub, a parked timeline)
    # would otherwise yank the document in the middle of the next measurement
    pg.evaluate("""() => {
        clearTimeout(window.__nbrailScrubT);
        if (window.__nbrailWheelRaf) cancelAnimationFrame(window.__nbrailWheelRaf);
        window.__nbrailWheelRaf = 0; window.__nbrailWheelAcc = 0;
        window.__nbrailSelfScroll = false; window.__nbrailDriving = 0;
        window.__nbrailHerePin = 0;
        var h = document.getElementById('nbpanel-root');
        h.removeAttribute('data-manual'); h.removeAttribute('data-doc');
    }""")
    # ---- the timeline follows where you are READING --------------------------
    pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var map = h.querySelector('.nbmap');
        var nodes = [].slice.call(map.querySelectorAll('.nbmap-node[data-target]'));
        // give the mock notebook a body: one tall block per node, each carrying
        // that node's anchor, so there is something to scroll THROUGH
        var nb = document.querySelector('.jp-Notebook');
        window.__probe = [];
        nodes.forEach(function(n){
          var id = n.getAttribute('data-target');
          if (document.getElementById(id)) return;
          var block = document.createElement('div');
          block.style.cssText = 'height:420px;position:relative';
          var sp = document.createElement('span');
          sp.id = id; sp.style.cssText = 'display:block;height:1px;position:relative';
          block.appendChild(sp); nb.appendChild(block); window.__probe.push(block);
        });
        // a node far enough along that the window actually has to travel
        var tgt = null, el = null;
        for (var i = nodes.length - 1; i >= 0; i--) {
          var e = document.getElementById(nodes[i].getAttribute('data-target'));
          if (!e) continue;
          if (nodes[i].offsetLeft - map.clientWidth / 2 < 120) continue;
          tgt = nodes[i]; el = e; break;
        }
        window.__tgt = tgt;
        if (!tgt) return;
        h.removeAttribute('data-manual'); h.removeAttribute('data-doc');
        window.__before = Math.round(map.scrollLeft);
        // Scroll the DOCUMENT the way a reader does — a wheel, not scrollIntoView
        // and not a hand-set map.scrollLeft: setting the map by hand reads as
        // scrubbing, and scrubbing drags the document straight back.
        var sc = nb.closest ? nb : nb;
        var y = el.getBoundingClientRect().top - nb.getBoundingClientRect().top;
        nb.scrollTop += Math.round(y) - 200;
        nb.dispatchEvent(new Event('scroll', {bubbles: true}));
        window.__nbrailSync();
    }""")
    pg.wait_for_timeout(700)                     # the window travels smoothly
    track = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var map = h.querySelector('.nbmap');
        var mk = h.querySelector('.nbmap-here');
        var centre = map.scrollLeft + map.clientWidth / 2;
        var markCentre = mk ? parseFloat(mk.style.left || 0) + mk.offsetWidth / 2 : null;
        var out = window.__tgt ? {
            before: window.__before, after: Math.round(map.scrollLeft),
            offBy: markCentre === null ? null : Math.round(Math.abs(centre - markCentre)),
            target: window.__tgt.getAttribute('data-target')} : {skipped: true};
        // leave the mock as we found it — later checks measure this layout
        (window.__probe || []).forEach(function(b){ b.remove(); });
        h.removeAttribute('data-doc'); map.scrollLeft = 0;
        window.__nbrailSync();
        return out;
    }""")
    print("timeline follows the document:", track)
    # the white notch says WHERE in the document you are — it must move with the
    # scroll, and it must not sit on a circle
    here = pg.evaluate(JS_HERE)
    print("reading marker:", here)
    if here.get("missing"):
        errs.append("there is no reading marker on the bar")
    elif not here["on"]:
        errs.append("the reading marker never shows")
    elif here["top"] == here["bottom"]:
        errs.append("the reading marker does not move with the document (%s)" % here["top"])
    else:
        if here["atStart"] > 3:
            errs.append("at the start the marker is %dpx off the first section bar"
                        % here["atStart"])
        if here["width"] < 40:
            errs.append("the reading marker is only %dpx wide" % here["width"])
        if not (here["zMark"] < here["zNode"]):
            errs.append("the marker is not behind the dots (%s vs %s)"
                        % (here["zMark"], here["zNode"]))
        # The colour under the marker is checked properly further down, in
        # 'what the marker runs over' — with a settle, because the markers now
        # transition their colour and an immediate read catches the old one.
    if not track.get("skipped"):
        if track["after"] <= track["before"]:
            errs.append("scrolling the document does not move the timeline (%d -> %d)"
                        % (track["before"], track["after"]))
        # the window's centre IS the marker's centre — that is what makes the
        # scrollbar underneath travel with it
        if track["offBy"] is None or track["offBy"] > 8:
            errs.append("the window is not centred on the reading marker (off by %s)"
                        % track["offBy"])

    # ---- the scrollbar stops where the markers stop ---------------------------
    # The travel of the panel's scrollbar is the travel of the marker: from the
    # centre of the first section bar to the centre of the last marker, and not a
    # pixel past either. Padding to the EDGE of the last node's box overruns by
    # half a node, because the dot sits in the middle of a 106px box.
    stops = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var map = h.querySelector('.nbmap'), inner = h.querySelector('.nbmap-inner');
        var ns = inner.querySelectorAll('.nbmap-node');
        var mid = function(n){
          var m = n.querySelector('.nbsect,.nbchapdot,.nbsubdot,.nbrail-dot');
          return n.offsetLeft + (m ? m.offsetLeft + m.offsetWidth / 2 : n.offsetWidth / 2);
        };
        window.__nbrailHerePin = Date.now();
        map.scrollLeft = 0;
        var lo = Math.round(map.scrollLeft + map.clientWidth / 2 - mid(ns[0]));
        map.scrollLeft = map.scrollWidth;
        var hi = Math.round(map.scrollLeft + map.clientWidth / 2 - mid(ns[ns.length - 1]));
        map.scrollLeft = 0; window.__nbrailHerePin = 0;
        return {lo: lo, hi: hi, max: Math.round(map.scrollWidth - map.clientWidth)};
    }""")
    print("where the scrollbar stops:", stops)
    if abs(stops["lo"]) > 2:
        errs.append("at the left end the centre is %dpx off the first bar" % stops["lo"])
    if abs(stops["hi"]) > 2:
        errs.append("at the right end the centre is %dpx off the last marker" % stops["hi"])

    # leftovers from the wheel probes (a pending scrub, a parked timeline)
    # would otherwise yank the document in the middle of the next measurement
    pg.evaluate("""() => {
        clearTimeout(window.__nbrailScrubT);
        if (window.__nbrailWheelRaf) cancelAnimationFrame(window.__nbrailWheelRaf);
        window.__nbrailWheelRaf = 0; window.__nbrailWheelAcc = 0;
        window.__nbrailSelfScroll = false; window.__nbrailDriving = 0;
        window.__nbrailHerePin = 0;
        var h = document.getElementById('nbpanel-root');
        h.removeAttribute('data-manual'); h.removeAttribute('data-doc');
    }""")
    # ---- the track must GLIDE, not lurch --------------------------------------
    # A scroll used to run the whole sync — diffing the panel, re-adopting the
    # widgets, re-measuring the box — so most scroll events were never drawn and
    # the timeline arrived in jumps. Scrolling now does the cheap part only.
    pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var map = h.querySelector('.nbmap');
        var nodes = [].slice.call(map.querySelectorAll('.nbmap-node[data-target]'));
        var nb = document.querySelector('.jp-Notebook');
        window.__probe = [];
        nodes.forEach(function(n){
          var id = n.getAttribute('data-target');
          if (document.getElementById(id)) return;
          var block = document.createElement('div');
          block.style.cssText = 'height:420px;position:relative';
          var sp = document.createElement('span');
          sp.id = id; sp.style.cssText = 'display:block;height:1px;position:relative';
          block.appendChild(sp); nb.appendChild(block); window.__probe.push(block);
        });
        h.removeAttribute('data-manual'); h.removeAttribute('data-doc');
        // start where the anchored blocks start — everything above them is mock
        // scenery, and the timeline has nothing to say about it
        var first = document.getElementById(nodes[0].getAttribute('data-target'));
        if (first) first.scrollIntoView();
        map.scrollLeft = 0;
        window.__nbrailSync();
    }""")
    pg.wait_for_timeout(200)
    glide = []
    for _i in range(24):
        glide.append(pg.evaluate("""() => {
            var nb = document.querySelector('.jp-Notebook');
            nb.scrollTop += 90;
            nb.dispatchEvent(new Event('scroll', {bubbles: true}));
            return null;
        }""") or 0)
        pg.wait_for_timeout(45)
        glide[-1] = pg.evaluate(
            "() => Math.round(document.getElementById('nbpanel-root')"
            ".querySelector('.nbmap').scrollLeft)")
    pg.evaluate("""() => {
        (window.__probe || []).forEach(function(b){ b.remove(); });
        var nb = document.querySelector('.jp-Notebook'); nb.scrollTop = 0;
        var h = document.getElementById('nbpanel-root');
        h.removeAttribute('data-doc');
        h.querySelector('.nbmap').scrollLeft = 0;
        window.__nbrailSync();
    }""")
    _steps = [glide[i + 1] - glide[i] for i in range(len(glide) - 1)]
    _moved = [d for d in _steps if d > 0]
    _still = sum(1 for d in _steps if d == 0)
    print("gliding:", {"travel": glide[-1] - glide[0], "steps": len(_moved),
                       "still": _still, "biggest": max(_steps) if _steps else 0,
                       "typical": sorted(_moved)[len(_moved) // 2] if _moved else 0})
    # The threshold measures how far the glide has got by the time the last
    # sample is taken, so it is partly a measure of animation TIMING: across
    # runs of the same build it lands between 198 and 210. What the check is
    # actually for is a timeline that does not follow at all, which is an order
    # of magnitude away; the smoothness is checked by the step counts below.
    if glide[-1] - glide[0] < 180:
        errs.append("scrolling the document barely moves the timeline (%d px)"
                    % (glide[-1] - glide[0]))
    elif _still > len(_steps) / 3:
        errs.append("the timeline stands still through %d of %d scroll steps — it "
                    "lurches instead of gliding" % (_still, len(_steps)))
    elif max(_steps) > 0.35 * (glide[-1] - glide[0]):
        # Not measured against the MEDIAN: the mapping from document to timeline
        # is legitimately uneven — the title page is a screen tall and half a
        # bar wide — so a fast segment is not a stutter. What would be a stutter
        # is one step swallowing a third of the whole travel.
        errs.append("the timeline jumps %dpx in one step of a %dpx travel"
                    % (max(_steps), glide[-1] - glide[0]))

    # ---- pointing at a node ---------------------------------------------------
    # Hover is attention, not a state: the marker and its name take the colour of
    # the reading marker and grow, whatever state colour the node would otherwise
    # wear. A locked circle is the hard case — its border carries !important.
    hov = {}
    _digi = pg.evaluate("() => document.body.classList.contains('nbskin-digi')")
    for _theme in ("light", "dark"):
        pg.evaluate("""(dark) => {
            var h = document.getElementById('nbpanel-root');
            h.querySelectorAll('.nbmap-node.nbpop').forEach(function(n){
              n.classList.remove('nbpop'); });
            document.body.classList.toggle('nbdark', dark);
            document.body.classList.toggle('nbforce-dark', dark);
            (function(_d){ try { window.__nbStore.set('digichemjn.theme.v1', _d ? 'dark' : 'light'); } catch (e) {} if (window.__nbApplyTheme) window.__nbApplyTheme(); })(dark);   // 2026-09-25: brightness is the reader's setting, not the front end's
            var d = h.querySelector('.nbmap-node.task .nbrail-dot.st-lock');
            if (d) d.closest('.nbmap-node').classList.add('nbpop');
            return !!d;
        }""", _theme == "dark")
        # longer than the theme cross-fade (850ms + the 1s arming window), or the
        # colour read here is an intermediate one and means nothing
        pg.wait_for_timeout(1250)
        hov[_theme] = pg.evaluate("""() => {
            var h = document.getElementById('nbpanel-root');
            var d = h.querySelector('.nbmap-node.nbpop .nbrail-dot');
            if (!d) return null;
            var n = d.closest('.nbmap-node');
            var l = n.querySelector('.nbtasklab') || n.querySelector('.nbmap-lab');
            var cs = getComputedStyle(d);
            var m = cs.transform.match(/matrix\(([-\d.]+)/);
            return {ring: cs.borderTopColor, lab: l ? getComputedStyle(l).color : null,
                    grew: m ? parseFloat(m[1]) : null};
        }""")
    pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        h.querySelectorAll('.nbmap-node.nbpop').forEach(function(n){
          n.classList.remove('nbpop'); });
        (function(_d){ try { window.__nbStore.set('digichemjn.theme.v1', _d ? 'dark' : 'light'); } catch (e) {} if (window.__nbApplyTheme) window.__nbApplyTheme(); })(false); }""")
    print("pointing at a locked circle:", hov)
    for _theme, _got in hov.items():
        if not _got:
            errs.append("no locked circle to point at (%s)" % _theme)
            continue
        _w = (248, 248, 248) if _theme == "dark" else (13, 99, 224)
        # E34 (Hauptwerkstatt): in digi the reading marker is gold (--nbmark #f2b426 light,
        # #ffd36b dark), so hover is gold; behauptete bisher nur Blau/Weiß (minimal)
        if _digi: _w = (255, 211, 107) if _theme == "dark" else (242, 180, 38)
        for _what in ("ring", "lab"):
            if not _got[_what]:
                continue
            _m = [int(x) for x in re.findall(r"\d+", _got[_what])[:3]]
            _ok = (max(abs(_m[i] - _w[i]) for i in range(3)) <= 8 if _digi
                   else min(_m) >= 248 if _theme == "dark"
                   else max(abs(_m[i] - _w[i]) for i in range(3)) <= 8)
            if not _ok:
                errs.append("in %s, hovering does not colour the %s (%s, wanted %s)"
                            % (_theme, _what, _got[_what], _w))
        if not _got["grew"] or _got["grew"] < 1.15:
            errs.append("in %s, hovering does not make the circle grow (%s)"
                        % (_theme, _got["grew"]))

    # ---- the hidden feed must stay hidden -------------------------------------
    # The rail and the dock are absolutely positioned. Without a positioned,
    # clipping feed they escape its zero-height box, float over the notebook
    # and swallow every click meant for the text underneath.
    caged = pg.evaluate("""() => {
        var out = [];
        document.querySelectorAll('.nbfeed').forEach(function(f){
          var cs = getComputedStyle(f);
          var fb = f.getBoundingClientRect();
          // does anything belonging to this feed actually receive a click just
          // below where it sits?
          var hit = document.elementFromPoint(
              Math.round(fb.left + Math.min(fb.width, 400) / 2),
              Math.round(fb.top + 40));
          out.push({overflow: cs.overflow, position: cs.position,
                    height: Math.round(fb.height),
                    grabs: !!(hit && hit.closest && hit.closest('.nbfeed'))});
        });
        return out;
    }""")
    print("the hidden feed:", caged)
    for _c in caged:
        if _c["position"] == "static" or "hidden" not in _c["overflow"]:
            errs.append("the feed does not cage the panel (%s)" % _c)
        if _c["grabs"]:
            errs.append("the hidden feed swallows clicks meant for the document")

    # ---- the title page opens the timeline ------------------------------------
    # The first bar is the title card, not the Introduction: the marker has to
    # have somewhere to stand while the reader is still on the cover.
    title = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var first = h.querySelector('.nbmap-node');
        var card = document.createElement('div');
        card.className = 'nbtitle';
        card.style.cssText = 'height:180px';
        var nb = document.querySelector('.jp-Notebook');
        nb.insertBefore(card, nb.firstChild);
        window.__nbrailSync();
        var sel = first.getAttribute('data-sel');
        // 2026-09-24n: data-sel is a LIST, best first (.nbtitle-card, then .nbtitle)
        var found = false;
        (sel || '').split(/\s+/).forEach(function(c){
          if (c && document.querySelector('.' + c)) found = true; });
        nb.scrollTop = 400;
        first.click();
        return new Promise(function(res){ setTimeout(function(){
          res({cls: first.className.replace('nbjump nbmap-node ', ''),
               sel: sel, found: found,
               top: Math.round(nb.scrollTop)});
          card.remove(); window.__nbrailSync();
        }, 700); });
    }""")
    print("the title bar:", title)
    if "title" not in title["cls"]:
        errs.append("the timeline does not begin with the title page (%s)"
                    % title["cls"])
    if not title["found"]:
        errs.append("the title bar points at nothing (%s)" % title["sel"])
    if title["top"] != 0:
        errs.append("clicking the title bar does not go to the top (%s)"
                    % title["top"])

    # ---- the toolbar carries the tools it is meant to carry -------------------
    tools = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var where = function(sel){
          var e = h.querySelector(sel);
          if (!e) return null;
          // R3 · 17 Teil 2: no toolbar — two corners (was nbdock-l/-c/-r)
          if (e.closest('.nbcorner-tl')) return 'top-left';
          if (e.closest('.nbcorner-bl')) return 'bottom-left';
          if (e.closest('.nbdock-l')) return 'left';
          if (e.closest('.nbdock-c')) return 'centre';
          if (e.closest('.nbdock-r')) return 'right';
          return e.closest('.nbdrawer') ? 'drawer' : 'elsewhere';
        };
        var sc = document.querySelector('.jp-NotebookPanel')
              || document.querySelector('.jp-Notebook');
        var dk = h.querySelector('.nbdock');
        var r = sc.getBoundingClientRect(), db = dk.getBoundingClientRect();
        var order = function(sel){ var c = h.querySelector(sel); if (!c) return [];
          return [].slice.call(c.children).map(function(e){
            return {k: (e.className.match(/nb(full|theme|skin|zoomgrp|series|profile|gear|keys)\\b/) || [])[1] || '?',
                    y: Math.round(e.getBoundingClientRect().top),
                    w: Math.round(e.getBoundingClientRect().width)}; }); };
        return {tlOrder: order('.nbcorner-tl'), blOrder: order('.nbcorner-bl'),
                theme: where('.nbtheme'), gear: where('.nbgear'),
                doc: where('.nbz-doc'), gui: where('.nbz-gui'),
                stats: where('.nbseries'), profile: where('.nbprofile'),
                diff: where('[data-slot="nbctl-difficulty"]'),
                pid: (h.querySelector('.nbpid') || {}).textContent,
                statsW: h.querySelector('.nbseries') ? Math.round(h.querySelector('.nbseries').getBoundingClientRect().width) : 0,
                flush: Math.round(db.top - r.top),
                _rtop: Math.round(r.top), _dtop: Math.round(db.top),
                _dockStyleTop: dk.style.top,
                _nbScroll: Math.round((document.querySelector('.jp-Notebook')||{}).scrollTop||0)};
    }""")
    print("the toolbar:", tools)
    # 2026-09-24ao: the panel's own zoom control (.nbz-gui) left the toolbar.
    # 2026-09-28 (R3 · 17 Teil 2): the toolbar is gone (17 Teil 1, v1.19) —
    # top left: full screen, light/dark, style (top down); bottom left: zoom,
    # statistics, profile, settings, keys (bottom up). Until R3 this block
    # asserted the old bar's left/centre/right and was red since v1.19.
    # 2026-09-30 (E10) — THE LENS STANDS TOP LEFT, BESIDE FULL SCREEN (E6.6,
    # user, 29.09.: "Lupe oben neben ⛶"). Until E10 this asserted the lens in
    # the bottom corner (R3 · 17) and was red since v1.25 — the rule was the
    # old one, not the code. Top left: full, theme, skin in the column, the
    # lens group lying beside full screen; bottom left: statistics, profile,
    # settings, keys.
    # 2026-10-02 (E17.2) — 📚 IS PART OF 👤. This block asserted 📚 in the
    # bottom corner (R3 · 17) and the chip showing an id (the notebook's, a
    # placeholder since 24i). Now the statistics are a section of the 👤
    # window: 📚 keeps its place in the corner (hw_e21 B4 and css-E17.2 look
    # for it there) but is not drawn (width 0, display:none — K2.7), the
    # corner as DRAWN holds 👤 ⚙ ⌨, and the chip names the PERSON: "—" until
    # an account is on (the account block below checks the id after a log-in).
    _want = {"theme": "top-left", "gear": "bottom-left", "doc": "top-left",
             "stats": "bottom-left", "profile": "bottom-left", "diff": "drawer"}
    if tools.get("statsW"):
        errs.append("📚 is drawn (%s px wide) — E17.2: only 👤" % tools["statsW"])
    for _k, _v in _want.items():
        if tools[_k] != _v:
            errs.append("%s is %s, wanted %s" % (_k, tools[_k], _v))
    _tl = [x["k"] for x in tools["tlOrder"]]; _bl = [x["k"] for x in tools["blOrder"] if x.get("w")]
    if _tl != ["full", "theme", "skin", "zoomgrp"]:
        errs.append("the top-left corner holds %s, wanted full, theme, skin + the lens" % _tl)
    if _bl != ["profile", "gear", "keys"]:
        errs.append("the bottom-left corner draws %s, wanted profile, gear, keys (E17.2)" % _bl)
    _ys = [x["y"] for x in tools["blOrder"] if x.get("w")]
    if any(a <= b for a, b in zip(_ys, _ys[1:])) and all(y != 0 for y in _ys):
        errs.append("the bottom-left corner does not stack upwards (%s)" % tools["blOrder"])
    # 2026-09-24bb: the zoom bar is back on the right, beside the panel.
    if tools["gui"] is not None:
        errs.append("the panel zoom control is back in the toolbar (%s)" % tools["gui"])
    if tools["pid"] != "—":
        errs.append("the profile chip shows %r with nobody logged in (E17.2: —)" % tools["pid"])
    # The dock is pinned to the panel's top edge, but clamped into the window —
    # a toolbar scrolled off the screen is not a toolbar. So the check is: flush
    # when the panel's top is visible, clamped to the window's edge when it is not.
    if tools["_rtop"] >= 2:
        if abs(tools["flush"]) > 3:
            errs.append("the toolbar is %dpx off the document's top edge"
                        % tools["flush"])
    elif abs(tools["_dtop"] - 2) > 3:
        errs.append("the toolbar is not clamped to the window's top edge (%s)"
                    % tools["_dtop"])

    # ---- and the document has no scrollbar of its own left --------------------
    nobar = pg.evaluate("""() => {
        try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','v'); } catch(e){}
        window.__nbrailSync();
        var sc = document.querySelector('.jp-Notebook');
        var out = {vert: document.body.classList.contains('nbvert'),
                   width: getComputedStyle(sc).scrollbarWidth,
                   bar: sc.offsetWidth - sc.clientWidth};
        try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','h'); } catch(e){}
        window.__nbrailSync();
        out.backAgain = getComputedStyle(sc).scrollbarWidth;
        return out;
    }""")
    print("the document's own scrollbar:", nobar)
    if nobar["width"] != "none":
        errs.append("the document still paints its own scrollbar next to the "
                    "marker (%s)" % nobar["width"])
    if nobar["backAgain"] == "none":
        errs.append("a notebook without the rail loses its scrollbar too")

    # ---- the document zoom leaves both panels alone ---------------------------
    # Ctrl+wheel and the Doc slider scale the DOCUMENT. The rail and the
    # toolbar are instruments, not content: they keep their size on screen,
    # and the rail keeps its right edge pinned to the document's.
    indep = pg.evaluate("""() => {
        try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','v'); } catch(e){}
        window.__nbrailSync();
        var h = document.getElementById('nbpanel-root');
        var rail = h.querySelector('.nbrail'), dock = h.querySelector('.nbdock');
        var sc = document.querySelector('.jp-Notebook');
        var doc = h.querySelector('.nbz-doc .nbslider');
        var snap = function(tag){
          var rb = rail.getBoundingClientRect(), db = dock.getBoundingClientRect();
          var sb = sc.getBoundingClientRect();
          var bar = sc.offsetWidth - sc.clientWidth;
          return {tag: tag, railW: Math.round(rb.width), railH: Math.round(rb.height),
                  dockH: Math.round(db.height),
                  pin: Math.round((sb.right - bar) - rb.right),
                  lens: +(localStorage.getItem(window.__nbZKey ? window.__nbZKey() : 'digichemjn.zoom.v1') || 100),
                  w: window.__nbW, wmin: window.__nbWmin};
        };
        var out = [snap('100%')];
        [70, 130, 100].forEach(function(p){
          doc.value = String(p);
          doc.dispatchEvent(new Event('input', {bubbles: true}));
          window.__nbrailSync();
          out.push(snap(p + '%'));
        });
        try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','h'); } catch(e){}
        window.__nbrailSync();
        return out;
    }""")
    print("panels against the document zoom:",
          ", ".join("%s rail %dx%d dock h%d pin %d"
                    % (d["tag"], d["railW"], d["railH"], d["dockH"], d["pin"])
                    for d in indep))
    _b = indep[0]
    _SBW = pg.evaluate("() => window.__nbSbw || 0")
    # 2026-09-30 (E10.M-wmin) — THIS BEHAUPTETE BISHER "the rail keeps its
    # width at every lens". Since E9.3 the marks are drawn × lens, and shut
    # the panel is exactly as wide as its marks need (WMIN), so shut it is
    # now round(floor · lens) + the cursor's 14 px. The rule: the rail is
    # WMIN of that lens when shut, the reader's width otherwise; the toolbar
    # and the pin stay as they were. At 100 % (the first snap, when shut)
    # WMIN is the floor + 14 — the old width.
    for _d in indep:
        _shut = _d["w"] is not None and _d["w"] == _d["wmin"]
        _want = _d["wmin"] if _shut else _b["railW"]
        if _want is None or abs(_d["railW"] - _want) > 4:
            errs.append("E10.M-wmin: the rail at lens %s is %d px wide, want %s (%s)"
                        % (_d["lens"], _d["railW"], _want, "shut: WMIN" if _shut else "the reader's width"))
    _sh = [d for d in indep if d["w"] == d["wmin"]]
    for _x in _sh:
        for _y in _sh:
            if _x["lens"] > _y["lens"] and _x["railW"] <= _y["railW"]:
                errs.append("E10.M-wmin: shut, the rail at lens %s (%d px) is not wider than at %s (%d px)"
                            % (_x["lens"], _x["railW"], _y["lens"], _y["railW"]))
    for _d in indep[1:]:
        if abs(_d["dockH"] - _b["dockH"]) > 4:
            errs.append("the document zoom resized the toolbar at %s (%d vs %d)"
                        % (_d["tag"], _d["dockH"], _b["dockH"]))
        # E11.6: THIS BEHAUPTETE BISHER "the rail's right edge IS the
        # document's". The scroll bar has a column of its own right of the
        # panel now (16 px, __nbSbw): the rail stands that far in.
        if abs(_d["pin"] - _SBW) > 4:
            errs.append("the rail is not the scroll-bar column (%d px) in from the document's right edge at %s (%dpx)"
                        % (_SBW, _d["tag"], _d["pin"]))

    # 2026-10-01 (E12.3) — THIS BEHAUPTETE BISHER (E11.6) "the scroll bar
    # stands in a column of its own RIGHT of the panel". The user moved it
    # (E12.3): on the LEFT, in the tools' column between the top-left and the
    # bottom-left corner, the thumb (cursor) in the track; the panel's own
    # groove (.nbrail::after) stays off (#nbpanel-root.nbsb-out).
    sbc = pg.evaluate("""() => {
        try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','v'); } catch(e){}
        window.__nbrailSync(); if (window.__nbPlaceCursor) window.__nbPlaceCursor(document.getElementById('nbpanel-root'));
        var h = document.getElementById('nbpanel-root');
        var rr = h.querySelector('.nbrail').getBoundingClientRect();
        var cr = h.querySelector('.nbmap-cursor').getBoundingClientRect();
        var sb = h.querySelector(':scope > .nbsb'), sr = sb ? sb.getBoundingClientRect() : null;
        var qa = h.querySelector('.nbcorner-tl'), qb = h.querySelector('.nbcorner-bl');
        qa = qa ? qa.getBoundingClientRect() : null; qb = qb ? qb.getBoundingClientRect() : null;
        var out = {railL: rr.left, railR: rr.right, curL: cr.left, curR: cr.right, curT: cr.top, curB: cr.bottom, sb: !!sb,
                   sbT: sr ? sr.top : null, sbB: sr ? sr.bottom : null,
                   tlB: qa ? qa.bottom : null, blT: qb ? qb.top : null, colL: qa ? qa.left : null, colR: qa ? qa.right : null,
                   sbL: sr ? sr.left : null, sbR: sr ? sr.right : null,
                   groove: getComputedStyle(h.querySelector('.nbrail'), '::after').display};
        try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','h'); } catch(e){}
        window.__nbrailSync();
        return out; }""")
    print("E12.3 scroll bar between the tools:", sbc)
    if (not sbc["sb"] or sbc["tlB"] is None or sbc["blT"] is None or sbc["sbR"] > sbc["railL"]
            or sbc["sbL"] < sbc["colL"] - 1 or sbc["sbR"] > sbc["colR"] + 1
            or sbc["sbT"] < sbc["tlB"] or sbc["sbB"] > sbc["blT"]
            or sbc["curL"] < sbc["sbL"] - 1 or sbc["curR"] > sbc["sbR"] + 1
            or sbc["curT"] < sbc["sbT"] - 1 or sbc["curB"] > sbc["sbB"] + 1):
        errs.append("E12.3: the scroll bar is not in the tools' column between the corners, thumb in its track (%s)" % sbc)
    if sbc["groove"] != "none":
        errs.append("E12.3: the panel still draws its own track (.nbrail::after %s)" % sbc["groove"])

    # ---- the marker does the scrollbar's job ----------------------------------
    # In the rail there is no scrollbar any more: the marker is the thumb. It
    # has to be as long as the visible share of the document, and dragging it
    # has to scroll the document.
    thumb = pg.evaluate("""() => {
        try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','v'); } catch(e){}
        window.__nbrailSync();
        var h = document.getElementById('nbpanel-root');
        var map = h.querySelector('.nbmap'), inner = h.querySelector('.nbmap-inner');
        var mk = h.querySelector('.nbmap-here');
        var sc = document.querySelector('.jp-Notebook');
        var share = sc.scrollHeight ? sc.clientHeight / sc.scrollHeight : 1;
        var out = {bar: map.offsetWidth - map.clientWidth,
                   h: Math.round(mk.offsetHeight),
                   want: Math.max(24, Math.min(map.clientHeight,
                         Math.round(map.clientHeight * Math.min(1, share)))),
                   topOff: Math.round(parseFloat(mk.style.top || 0)
                           - Math.max(map.scrollTop,
                                      parseInt(h.dataset.railY0 || '0', 10) || 0)),
                   grab: getComputedStyle(mk).cursor, K: window.__nbK || 1,
                   before: Math.round(sc.scrollTop)};
        var ev = function(t, y){ return new PointerEvent(t, {bubbles: true,
            cancelable: true, clientY: y, clientX: 10, pointerId: 7, button: 0}); };
        mk.dispatchEvent(ev('pointerdown', 100));
        mk.dispatchEvent(ev('pointermove', 260));
        mk.dispatchEvent(ev('pointerup',   260));
        out.after = Math.round(sc.scrollTop);
        sc.scrollTop = 0;
        try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','h'); } catch(e){}
        window.__nbrailSync();
        return out;
    }""")
    print("the marker as a thumb:", thumb)
    if thumb["bar"] > 1:
        errs.append("the rail still has a scrollbar next to the marker (%dpx)"
                    % thumb["bar"])
    # 2026-09-24n: the marker is no longer a window drawn to scale — it is a
    # ring barely larger than a marker circle (28px), so it points at one mark
    # instead of swallowing several. Its length is now a clamp, not a share.
    # 2026-09-24ab: short again, and final. The long thumb said how much of the
    # document was on screen and cost the marker its one job — standing level
    # with a single mark. The travel (24z) stays; the length is back to the
    # 32-38 clamp, so it is barely larger than an exercise mark.
    # 2026-09-24ag: back to half — 16-22. It fills what it stands on either way;
    # the length is what decides whether it reads as a position or as a band.
    # 2026-09-30 (E10) — × K. Since E9.3 the marker grows with the lens and
    # the panel (--nbkz, CSS-E9.3; K = window.__nbK). Until E10 this asserted
    # 14-26 px flat and was red at the lens an earlier probe leaves (200 %%:
    # 48 px = 24 × 2).
    _K = float(thumb.get("K") or 1)
    if not (14 * _K - 1 <= thumb["h"] <= 26 * _K + 1):
        errs.append("the marker is not the right length (%dpx; wanted 14-26 x K %.2f)"
                    % (thumb["h"], _K))
    if False:
        errs.append("the marker is not as long as the window it stands for "
                    "(%d vs %d)" % (thumb["h"], thumb["want"]))
    if "grab" not in thumb["grab"]:
        errs.append("the marker does not offer to be dragged (%s)" % thumb["grab"])
    if thumb["after"] - thumb["before"] < 120:
        errs.append("dragging the marker does not scroll the document (%d -> %d)"
                    % (thumb["before"], thumb["after"]))

    # ---- the dock keeps its size and its corner -------------------------------
    # It is the thing a reader reaches for when the timeline has become hard to
    # read, so it must not shrink with it — and it must not move when the panel
    # is turned on its side.
    dock = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var d = h.querySelector('.nbdock');
        var sc = document.querySelector('.jp-Notebook');
        // 2026-09-24ao: the panel's own size control is gone from the toolbar
        var gui = h.querySelector('.nbz-gui .nbslider');
        var doc = h.querySelector('.nbz-doc .nbslider');
        // 2026-09-24o: the PANEL slider runs the other way — right folds it
        // away — so a test that wants N%% of panel writes 100-N to the thumb.
        var set = function(i, v){
          if (!i) return;                       // the panel slider no longer exists
          var w = i.classList.contains('nbgui-lab') ? (100 - v) : v;
          i.value = String(w);
          i.dispatchEvent(new Event('input', {bubbles: true})); };
        // measured against the WINDOW: that is the corner the dock is pinned
        // to, and the point of pinning it there is that nothing else moves it
        var snap = function(tag){
          var b = d.getBoundingClientRect();
          return {tag: tag, w: Math.round(b.width), h: Math.round(b.height),
                  x: Math.round(b.left),
                  y: Math.round(window.innerHeight - b.bottom)};
        };
        var out = [snap('rest')];
        set(gui, 30);  out.push(snap('panel 30%'));
        set(gui, 100);
        set(doc, 70);  out.push(snap('doc 70%'));
        set(doc, 100);
        try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','v'); } catch(e){}
        window.__nbrailSync();
        return new Promise(function(res){ setTimeout(function(){
          out.push(snap('vertical'));
          try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','h'); } catch(e){}
        window.__nbrailSync();
          setTimeout(function(){ out.push(snap('back')); res(out); }, 500);
        }, 500); });
    }""")
    print("the dock:", ", ".join("%s %dx%d at %d/%d"
          % (d["tag"], d["w"], d["h"], d["x"], d["y"]) for d in dock))
    _r = dock[0]
    for _d in dock[1:]:
        # The HEIGHT is the dock's own and must never change. The width is the
        # document's — a toolbar that spans the top of the document is wider on
        # screen when the document is zoomed out, and that is the point.
        if abs(_d["h"] - _r["h"]) > 3:
            errs.append("the dock changed height at %s (%d vs %d)"
                        % (_d["tag"], _d["h"], _r["h"]))
        if abs(_d["x"] - _r["x"]) > 9 or abs(_d["y"] - _r["y"]) > 30:
            errs.append("the dock left its corner at %s (%d/%d vs %d/%d)"
                        % (_d["tag"], _d["x"], _d["y"], _r["x"], _r["y"]))

    # ---- the marker whitens a LOCKED circle too, and in the dark theme ---------
    # This is the one that kept regressing: the dark twins are
    # `body[data-jp-theme-light="false"] .nbrail-dot.st-lock` — an element plus
    # three classes — and outrank a plain `.nbmap-node.here .nbrail-dot`.
    PICK = {"lock": "var d=n.querySelector('.nbrail-dot');"
                    "return d&&d.classList.contains('st-lock');",
            "sect": "return !!n.querySelector('.nbsect');",
            "chap": "return !!n.querySelector('.nbchapdot');"}
    PARK = """(kind) => {
        var h = document.getElementById('nbpanel-root');
        var map = h.querySelector('.nbmap'), inner = h.querySelector('.nbmap-inner');
        var pick = new Function('n', kind);
        var ns = [].slice.call(inner.querySelectorAll('.nbmap-node')), n = null;
        for (var j = 0; j < ns.length; j++) {
          if (!pick(ns[j])) continue;
          var cj = Math.round(ns[j].offsetLeft + ns[j].offsetWidth / 2 - map.clientWidth / 2);
          if (cj >= 0 && cj <= map.scrollWidth - map.clientWidth) { n = ns[j]; break; }
        }
        if (!n) return false;
        map.scrollLeft = Math.round(n.offsetLeft + n.offsetWidth / 2 - map.clientWidth / 2);
        window.__nbrailHerePin = Date.now();   // or the sync pulls the track back
        window.__nbrailSync();
        window.__hereNode = n;
        return true;
    }"""
    READ = """() => {
        var n = window.__hereNode;
        var kid = n.querySelector('.nbrail-dot') || n.querySelector('.nbchapdot')
               || n.querySelector('.nbsubdot') || n.querySelector('.nbsect');
        var cs = getComputedStyle(kid);
        return {here: n.classList.contains('here'),
                ink: kid.classList.contains('nbrail-dot') ? cs.borderTopColor
                                                          : cs.backgroundColor};
    }"""
    over = {}
    for _theme in ("light", "dark"):
        if _theme == "dark":
            pg.evaluate("""() => { (function(_d){ try { window.__nbStore.set('digichemjn.theme.v1', _d ? 'dark' : 'light'); } catch (e) {} if (window.__nbApplyTheme) window.__nbApplyTheme(); })(true); }""")
        else:
            pg.evaluate("""() => { (function(_d){ try { window.__nbStore.set('digichemjn.theme.v1', _d ? 'dark' : 'light'); } catch (e) {} if (window.__nbApplyTheme) window.__nbApplyTheme(); })(false); }""")
        # the theme cross-fade is armed by the attribute change; wait it out, or
        # every colour read below is an intermediate one
        pg.wait_for_timeout(1250)
        over[_theme] = {}
        for _what, _js in PICK.items():
            if not pg.evaluate(PARK, _js):
                over[_theme][_what] = None
                continue
            pg.wait_for_timeout(400)      # the colour transitions — read it settled
            over[_theme][_what] = pg.evaluate(READ)
    pg.evaluate("""() => {
        (function(_d){ try { window.__nbStore.set('digichemjn.theme.v1', _d ? 'dark' : 'light'); } catch (e) {} if (window.__nbApplyTheme) window.__nbApplyTheme(); })(false);
        var h = document.getElementById('nbpanel-root');
        window.__nbrailHerePin = 0;
        h.querySelector('.nbmap').scrollLeft = 0; window.__nbrailSync();
    }""")
    print("what the marker runs over:", over)
    for _theme in ("light", "dark"):
        for _what in ("lock", "sect", "chap"):
            _got = over[_theme][_what]
            if not _got:
                continue
            _m = [int(x) for x in re.findall(r"\d+", _got["ink"])[:3]]
            # white on a dark page, the structural blue #2c6e91 on a light one
            _want = (248, 248, 248) if _theme == "dark" else (13, 99, 224)
            _ok = len(_m) >= 3 and (min(_m) >= 248 if _theme == "dark"
                                    else max(abs(_m[i] - _want[i]) for i in range(3)) <= 6)
            # 2026-09-24n: the marker no longer repaints what it passes. It is a
            # ring that runs BEHIND the marks, so a mark under it keeps its own
            # colour — the ring is what says "here", not a change of ink. What
            # is still checked is that the marker REACHES the node.
            if not _got["here"]:
                errs.append("the marker does not reach the %s node (%s)" % (_what, _theme))
            elif False:
                errs.append("in %s the marker does not colour the %s node (%s, wanted %s)"
                            % (_theme, _what, _got["ink"], _want))

    # ---- what an OPENED chapter looks like ------------------------------------
    pg.wait_for_timeout(400)          # let the marker's colours settle back
    opened = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var cur = h.querySelector('.nbmap-node.is-current .nbrail-dot');
        var un = h.querySelector('.nbmap-node.unlocked:not(.here) .nbchapdot');
        var lk = h.querySelector('.nbmap-node.locked .nbchapdot');
        var tail = h.querySelector('.nbmap-fill.tail');
        var fill = h.querySelector('.nbmap-fill:not(.tail):not(.code)');
        var g = cur && cur.querySelector('.nbdotg');
        return {digi: document.body.classList.contains('nbskin-digi'), cls: cur ? cur.className : null,
                glyph: g ? getComputedStyle(g, '::after').backgroundColor : null,
                ring: cur ? getComputedStyle(cur).borderTopColor : null,
                open_: un ? getComputedStyle(un).backgroundColor : null,
                shut: lk ? getComputedStyle(lk).backgroundColor : null,
                tailH: tail ? getComputedStyle(tail).height : null,
                greenH: fill ? getComputedStyle(fill).height : null};
    }""")
    print("an opened chapter:", opened)
    # E34 (Hauptwerkstatt): in digi the open circle is surface + line (C4) and the open
    # padlock itself is green (--dg-ok #1a7a4c light, #6be3a0 dark); behauptete bisher: grüner Ring
    if opened.get("digi"):
        if not (opened["glyph"] and any(c in opened["glyph"] for c in ("26, 122, 76", "107, 227, 160"))):
            errs.append("digi: the open padlock is not green (%s, ring %s)" % (opened["glyph"], opened["ring"]))
    elif opened["ring"] and "63, 168, 119" not in opened["ring"]:
        errs.append("the circle with the open padlock has no green ring (%s)" % opened["ring"])
    def _green(v):
        m = re.findall(r"\d+", v or "")
        if len(m) < 3: return False
        r, g, b = (int(x) for x in m[:3])
        return g > 140 and g > r + 40 and g > b + 30
    # 2026-09-24aj: a chapter mark is never coloured. Green on an unlocked
    # chapter said "passed", which is not a thing that happens to a chapter; it
    # only ever meant "not locked", and the absence of a padlock says that. So
    # the check is the opposite one now — it must NOT be green, and it must not
    # differ from a locked one's fill either.
    if opened["open_"] and _green(opened["open_"]):
        errs.append("an unlocked chapter dot is coloured (%s) — a chapter has no "
                    "state to show" % opened["open_"])
    # the skip/give-up stripe lies ON the green, thin enough that the XP reads through
    if opened["tailH"] and opened["greenH"]:
        _t = float(opened["tailH"][:-2]); _g = float(opened["greenH"][:-2])
        if _t > _g / 2:
            errs.append("the skip stripe covers the XP green (%s of %s)"
                        % (opened["tailH"], opened["greenH"]))

    print("drawer push:", push)
    if push["shut"]["pad"] != push["open"]["pad"]:
        errs.append("opening the drawer moves the document (%s -> %s)"
                    % (push["shut"]["pad"], push["open"]["pad"]))
    if push["shut"]["h"] != push["open"]["h"]:
        errs.append("opening the drawer changes the reserved strip (%s -> %s)"
                    % (push["shut"]["h"], push["open"]["h"]))

    # ---- the zoom control -----------------------------------------------------
    # It zooms the NOTEBOOK, never the panel, and the reserved strip is recomputed
    # in the notebook's own units so the first lines never slide under the panel.
    zoom = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var nb = document.querySelector('.jp-Notebook');
        // 2026-09-24r: both thumbs speak 0-100. The panel's runs the other way
        // (right folds it in); the document's is the real scale minus 50.
        function set(sel, v){
          var i = h.querySelector(sel + ' .nbslider');
          // the document thumb spans 50-200 % over 0-100 steps
          // 2026-09-24bi — the document slider runs 60-200%% now, and its
          // readout is the ZOOM and not the slider's own position. The thumb
          // is therefore (pct - 60) / 1.4, and the label is the percentage.
          // E25.o (2026-10-08) — behauptete bisher: the thumb is (pct − 60) / 1.4,
          // one even scale. Now the middle of the bar is 100 %%: two halves,
          // 60 … 100 %% on 0 … 50 and 100 %% … the ceiling on 50 … 100.
          var C = window.__nbZCeil || 200;
          i.value = String(sel === '.nbz-gui' ? (100 - v)
                           : Math.round(v <= 100 ? 50 * (v - 60) / 40 : 50 + 50 * (v - 100) / (C - 100)));
          i.dispatchEvent(new Event('input', {bubbles: true}));
        }
        function pageZoomForTest(){ return parseFloat(document.body.style.zoom) || 1; }
        function centres(){
          var pr = h.querySelector('.nbrail').getBoundingClientRect(),
              nr = nb.getBoundingClientRect();
          return {panel: Math.round(pr.left + pr.width / 2),
                  doc: Math.round(nr.left + nr.width / 2),
                  gap: Math.round(pr.left - nr.left), z: pageZoomForTest(),
                  width: Math.round(pr.width), nbw: Math.round(nr.width)};
        }
        var before = centres();
        // 2026-09-25: the readout says no number any more — the thumb is the
        // readout. So the oracle is the SETTING itself, which is a better one:
        // it measures what the control did rather than what it printed.
        var clean = function(){
            try { return localStorage.getItem(window.__nbZKey ? window.__nbZKey() : 'digichemjn.zoom.v1') || '100'; }
            catch (e) { return ''; } };
        set('.nbz-doc', 120);
        window.__nbrailSync();
        var zt = function(){
            var p = document.querySelector('.jp-NotebookPanel.jp-mod-current')
                 || document.querySelector('.jp-NotebookPanel');
            var c0 = p && p.querySelector('.jp-Cell');
            if (c0 && c0.children.length) return c0.children[0].style.zoom;
            var s2 = p && (p.querySelector('.jp-Notebook')
                        || p.querySelector('.jp-WindowedPanel-outer'));
            if (!s2) return '';
            var k = Array.prototype.filter.call(s2.children, function(c){
                return c.nodeType === 1 && !c.classList.contains('nbpanel-host')
                    && !c.classList.contains('jp-WindowedPanel-inner'); });
            return k.length ? k[0].style.zoom : '';
        };
        var out = {zoom: zt(), lab: clean(), bodyZoom: document.body.style.zoom || '(none)',
                   on: h.querySelector('.nbz-doc .nbslval').classList.contains('on'),
                   pad: nb.style.paddingTop,
                   at80: centres(), before: before};
        set('.nbz-doc', 140);
        out.back = clean();
        // dragging the slider is just its own input event
        set('.nbz-doc', 160);
        window.__nbrailSync();
        out.dragged = clean();
        // the wheel over the control does the same
        h.querySelector('.nbz-doc').dispatchEvent(new WheelEvent('wheel',
            {bubbles: true, cancelable: true, deltaY: -1}));
        out.wheeled = clean();
        // a double-click on the slider is the reset
        h.querySelector('.nbz-doc .nbslider').dispatchEvent(
            new MouseEvent('dblclick', {bubbles: true, cancelable: true}));
        window.__nbrailSync();
        out.reset = zt() || '(none)';
        out.resetLab = clean();
        out.resetThumb = h.querySelector('.nbz-doc .nbslider').value;     // E25.o: the middle
        out.at100 = centres();
        return out;
    }""")
    print("zoom control:", zoom)
    def _pc(v):
        """the readout, as a number. It says the zoom itself since 24bi."""
        try: return float(str(v).replace("%", "").strip())
        except Exception: return None
    if abs((_pc(zoom["lab"]) or 0) - 120) > 4 or abs(float(zoom["zoom"] or 1) - 1.2) > 0.04:
        errs.append("the document control did not reach 120%% (%s / %s)"
                    % (zoom["lab"], zoom["zoom"]))
    if zoom["bodyZoom"] != "(none)":
        errs.append("the zoom is on the page instead of the reading matter (%s)"
                    % zoom["bodyZoom"])
    if not zoom["on"]:
        errs.append("the zoom label does not light up while the document is enlarged")
    # ±4 %% throughout: the thumb is an integer 0-100 across a 140-point range,
    # so a percentage asked for cannot always be landed on exactly.
    if str(zoom.get("resetThumb")) != "50":
        errs.append("E25.o: 100%% is not the middle of the lens bar (thumb %s after the reset, want 50)" % zoom.get("resetThumb"))
    if abs((_pc(zoom["back"]) or 0) - 140) > 4:
        errs.append("zoom in does not step back (%s)" % zoom["back"])
    if abs((_pc(zoom["dragged"]) or 0) - 160) > 4:
        errs.append("dragging the zoom handle does not follow the pointer (%s, wanted 160%%)"
                    % zoom["dragged"])
    if (_pc(zoom["wheeled"]) or 0) <= (_pc(zoom["dragged"]) or 0):
        errs.append("the wheel over the zoom control does nothing (%s after %s)"
                    % (zoom["wheeled"], zoom["dragged"]))
    if zoom["reset"] != "(none)" or abs((_pc(zoom["resetLab"]) or 0) - 100) > 1:
        errs.append("clicking the zoom label does not reset it (%s / %s)"
                    % (zoom["reset"], zoom["resetLab"]))
    # The panel is as wide as the notebook it belongs to — at every zoom. Zooming
    # out does not shrink the panel on screen, because it does not shrink the
    # notebook on screen either: it puts MORE notebook in the same width.
    for _z in ("before", "at80"):
        if abs(zoom[_z]["width"] - zoom[_z]["nbw"]) > 26:
            errs.append("the panel is not as wide as the notebook at %s (%d vs %d)"
                        % (_z, zoom[_z]["width"], zoom[_z]["nbw"]))
    # and the one invariant that must never break: panel and document share a centre
    # The panel is pinned to the document's LEFT edge with a 10px gutter, at
    # every zoom — that is the whole point of pinning by the edge instead of
    # centring. Measured in device pixels, so the gutter scales with the zoom.
    for _name, _d in (("100%", zoom["before"]), ("80%", zoom["at80"]),
                      ("back at 100%", zoom["at100"])):
        if abs(_d["gap"] - 10 * _d["z"]) > 4:
            errs.append("at %s the panel sits %dpx from the document's edge, "
                        "wanted %d" % (_name, _d["gap"], round(10 * _d["z"])))

    # ---- hovering lifts the name instead of burying it ------------------------
    # A marker grows when you point at it. Its name has to stay readable: it must
    # sit above the grown marker, and it must move up with it, not stay behind.
    pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var node = h.querySelector('.nbmap-node.chap');
        window.__t = node;
        var lab = node.querySelector('.nbmap-lab'), dot = node.querySelector('.nbchapdot');
        function box(el){ var r = el.getBoundingClientRect();
                          return {top: Math.round(r.top), bottom: Math.round(r.bottom)}; }
        window.__rest = {lab: box(lab), dot: box(dot)};
        // :hover cannot be forced from script — the class carries the very same block
        node.classList.add('nbpop');
    }""")
    pg.wait_for_timeout(400)            # let the lift transition finish
    pop = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var node = window.__t;
        var lab = node.querySelector('.nbmap-lab'), dot = node.querySelector('.nbchapdot');
        function box(el){ var r = el.getBoundingClientRect();
                          return {top: Math.round(r.top), bottom: Math.round(r.bottom)}; }
        var popLab = box(lab), popDot = box(dot), grew = getComputedStyle(lab).transform;
        node.classList.remove('nbpop');
        // 2026-09-24at: a click must leave the SELECTION behind, and nothing of
        // the hover — no frozen rotation, no marker colour on a mark the
        // pointer left long ago.
        node.click();
        var m = node.querySelector('.nbchapdot');
        window.__clicked = node;
        return {restGap: window.__rest.dot.top - window.__rest.lab.bottom,
                popGap: popDot.top - popLab.bottom,
                lifted: window.__rest.lab.top - popLab.top, grew: grew,
                stuck: node.classList.contains('nbpop'),
                sel: node.classList.contains('nbsel'),
                sels: h.querySelectorAll('.nbmap-node.nbsel').length,
                clicked: m ? getComputedStyle(m).transform : null,
                others: h.querySelectorAll('.nbmap-node.nbpop').length};
    }""")
    # the pointer is wherever the last pg.click() left it, and :hover is a live
    # thing — park it in the corner before asking what the CLICK left behind
    pg.mouse.move(4, 4)
    pg.wait_for_timeout(350)
    pop["clicked"] = pg.evaluate("""() => {
        var n = window.__clicked, m = n && n.querySelector('.nbchapdot');
        return m ? getComputedStyle(m).transform : null;
    }""")
    print("hover lift:", pop)
    if pop["restGap"] < 4:
        errs.append("a chapter name sits on the line (%dpx clearance)" % pop["restGap"])
    if pop["popGap"] < 4:
        errs.append("the grown marker reaches into its own name (%dpx clearance)" % pop["popGap"])
    if pop["lifted"] < 3:
        errs.append("the name does not rise with the marker (%dpx)" % pop["lifted"])
    if "matrix" not in (pop["grew"] or ""):
        errs.append("the name is not scaled up on hover (%s)" % pop["grew"])
    if pop["stuck"] or pop["others"]:
        errs.append("a click still freezes the hover on the mark (%d popped)"
                    % pop["others"])
    if not pop["sel"]:
        errs.append("a click does not select the mark it landed on")
    if pop["sels"] != 1:
        errs.append("%d marks are selected at once, wanted exactly 1" % pop["sels"])
    # the selected mark must sit still: a transform that only translates is the
    # resting state; a rotate or a scale would be the hover left behind
    _m = (pop["clicked"] or "").replace("matrix(", "").split(",")
    if len(_m) >= 4:
        _a, _b, _c, _d = (float(x) for x in _m[:4])
        if abs(_a - 1) > .02 or abs(_d - 1) > .02 or abs(_b) > .02 or abs(_c) > .02:
            errs.append("the clicked mark keeps a turn or a stretch (%s)"
                        % pop["clicked"])


    # ---- what the reader scrolled to stays put -------------------------------
    manual = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var map = h.querySelector('.nbmap');
        map.style.scrollBehavior = 'auto';
        map.scrollLeft = 0;
        map.dispatchEvent(new WheelEvent('wheel', {deltaY: 300, bubbles: true, cancelable: true}));
        if (window.__nbrailWheelRaf) { cancelAnimationFrame(window.__nbrailWheelRaf);
          window.__nbrailWheelRaf = 0;
          map.scrollLeft += (window.__nbrailWheelAcc || 0);
          window.__nbrailWheelAcc = 0;
          h.setAttribute('data-manual', '1'); }
        var afterWheel = map.scrollLeft;
        window.__nbrailSync();                       // a plain sync must not reset it
        var afterSync = h.querySelector('.nbmap').scrollLeft;
        h.removeAttribute('data-sig');               // force a full rebuild
        window.__nbrailSync();
        return {afterWheel: Math.round(afterWheel), afterSync: Math.round(afterSync),
                manual: h.getAttribute('data-manual')};
    }""")
    pg.wait_for_timeout(400)
    manual["afterRebuild"] = pg.evaluate(
        "() => Math.round(document.querySelector('#nbpanel-root .nbmap').scrollLeft)")
    print("manual scroll position:", manual)
    if manual["afterWheel"] <= 0:
        errs.append("the wheel did not move the timeline")
    if manual["afterSync"] != manual["afterWheel"]:
        errs.append("a sync pulled the timeline back (%d -> %d)"
                    % (manual["afterWheel"], manual["afterSync"]))
    if abs(manual["afterRebuild"] - manual["afterWheel"]) > 2:
        errs.append("a rebuild threw the reader's scroll position away (%d -> %d)"
                    % (manual["afterWheel"], manual["afterRebuild"]))

    # ---- switching notebooks -------------------------------------------------
    # A second notebook is opened. Its panel must take over; the first notebook's
    # numbers must not stay on screen (that is what the user saw).
    pg.evaluate("""(h) => {
        var p = document.createElement('div');
        p.className = 'jp-NotebookPanel'; p.id = 'nb2';
        p.style.cssText = 'width:1200px;height:800px';
        p.innerHTML = '<div class="jp-Toolbar" style="height:40px">toolbar</div>' +
                      '<div class="jp-Notebook" style="height:700px"><div class="jp-Cell">' +
                      '<div class="jp-OutputArea" id="out2"></div></div></div>';
        document.body.appendChild(p);
        var d = document.createElement('div');
        d.innerHTML = h.replace('class="nbrail"', 'class="nbrail nb-second"')
                       .replace(/data-nbid="[^"]*"/, 'data-nbid="second00"');
        document.getElementById('out2').appendChild(d);
        document.querySelectorAll('.jp-NotebookPanel').forEach(function(x){
            x.classList.toggle('jp-mod-current', x.id === 'nb2');
        });
        document.querySelector('.jp-NotebookPanel:not(#nb2)').classList.add('lm-mod-hidden');
    }""", panel_html)
    pg.wait_for_timeout(700)
    sw = pg.evaluate("""() => { var h=document.getElementById('nbpanel-root');
        return {ready: h.classList.contains('ready'),
                second: !!h.querySelector('.nb-second'),
                dots: h.querySelectorAll('.nbrail-dot').length}; }""")
    print("after switching to the second notebook:", sw)
    if not (sw["ready"] and sw["second"]):
        errs.append("the panel does not follow the notebook switch")

    # a notebook whose setup cell has not run gets NO panel — not the other one's
    pg.evaluate("""() => {
        document.getElementById('out2').innerHTML = '';
        document.querySelectorAll('.jp-NotebookPanel').forEach(function(x){
            x.classList.toggle('jp-mod-current', x.id === 'nb2');
        });
    }""")
    pg.wait_for_timeout(1800)
    empty = pg.evaluate("""() => { var h=document.getElementById('nbpanel-root');
        var vp = document.querySelector('.jp-NotebookPanel.jp-mod-current');
        return {ready: h.classList.contains('ready'),
                dots: h.querySelectorAll('.nbrail-dot').length,
                miss: window.__nbrailMiss ? Math.round(Date.now()-window.__nbrailMiss) : 0,
                vp: vp ? vp.id : null,
                feeds: document.querySelectorAll('.nbfeed').length,
                inVp: vp ? vp.querySelectorAll('.nbfeed').length : -1}; }""")
    print("notebook without a panel of its own:", empty)
    if empty["ready"]:
        errs.append("a notebook without its own panel still shows the previous one")

    # back to the first notebook: its own panel returns
    pg.evaluate("""() => {
        document.getElementById('nb2').remove();
        var p = document.querySelector('.jp-NotebookPanel');
        p.classList.remove('lm-mod-hidden'); p.classList.add('jp-mod-current');
    }""")
    pg.wait_for_timeout(800)
    back = pg.evaluate("""() => { var h=document.getElementById('nbpanel-root');
        return {ready: h.classList.contains('ready'),
                second: !!h.querySelector('.nb-second'),
                dots: h.querySelectorAll('.nbrail-dot').length}; }""")
    print("back in the first notebook:", back)
    if not (back["ready"] and back["dots"] >= _NDOTS and not back["second"]):
        errs.append("the first notebook's own panel does not come back")

    # ---- full screen ---------------------------------------------------------
    # Everything outside the element that went full screen is not painted, so the
    # host has to move INSIDE it, and back out again afterwards.
    fs = pg.evaluate("""() => {
        var panel = document.querySelector('.jp-NotebookPanel');
        Object.defineProperty(document, 'fullscreenElement',
            {configurable: true, get: function(){ return panel; }});
        document.dispatchEvent(new Event('fullscreenchange'));
        var h = document.getElementById('nbpanel-root');
        return {parent: h.parentElement.className || h.parentElement.tagName,
                inside: panel.contains(h),
                ready: h.classList.contains('ready'),
                dots: h.querySelectorAll('.nbrail-dot').length,
                pos: getComputedStyle(h).position};
    }""")
    fs["bodyFs"] = pg.evaluate("() => document.body.classList.contains('nbfs')")
    fs["toolbar"] = pg.evaluate(
        "() => getComputedStyle(document.querySelector('.jp-Toolbar')).display")
    fs["nbWidth"] = pg.evaluate(
        "() => getComputedStyle(document.querySelector('.jp-Notebook')).maxWidth")
    # The panel's width is the DOCUMENT's — in full screen as anywhere else,
    # and at every setting of the thickness control.
    pg.wait_for_timeout(300)
    fs["widths"] = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var rail = h.querySelector('.nbrail');
        var nb = document.querySelector('.jp-Notebook');
        var inp = h.querySelector('.nbz-gui .nbslider');
        var out = [];
        if (!inp) return out;          // no panel size control any more
        [100, 60, 25].forEach(function(p){
          inp.value = String(100 - p);
          inp.dispatchEvent(new Event('input', {bubbles: true}));
          out.push({pct: p, rail: Math.round(rail.getBoundingClientRect().width),
                    nb: Math.round(nb.clientWidth)});
        });
        inp.value = '0'; inp.dispatchEvent(new Event('input', {bubbles: true}));
        return out;
    }""")
    # ...and in VERTICAL, full screen must keep it pinned to the right edge
    fs["vert"] = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','v'); } catch(e){}
        window.__nbrailSync();
        return null;
    }""")
    pg.wait_for_timeout(600)
    fs["vert"] = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var sc = document.querySelector('.jp-Notebook');
        var b = h.querySelector('.nbrail').getBoundingClientRect();
        // In full screen the WINDOW is the document: the rail pins to the
        // full-screen element's right edge, not to the scroller's, because the
        // scroller's box lags a frame behind the resize.
        var fsEl = document.fullscreenElement || document.webkitFullscreenElement;
        var r = (fsEl && fsEl !== document.documentElement && fsEl !== document.body)
              ? fsEl.getBoundingClientRect() : sc.getBoundingClientRect();
        var right = Math.max(r.right, window.innerWidth);
        var bar = sc.offsetWidth - sc.clientWidth;
        // 2026-09-24z: the rail starts at the toolbar's own TOP and runs up
        // behind it, so a mark scrolling up is swallowed by the bar instead of
        // stopping at a gap below it.
        var dk = h.querySelector('.nbdock');
        var want = dk ? dk.getBoundingClientRect().top : r.top;
        var out = {dx: Math.round(b.right - (right - bar)),
                   dy: Math.round(b.top - want),
                   dh: Math.round(b.bottom - window.innerHeight)};
        try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','h'); } catch(e){}
        window.__nbrailSync();
        return out;
    }""")
    pg.wait_for_timeout(600)
    print("in full screen:", fs)
    # E11.6: the panel stands the scroll-bar column (__nbSbw) in from the edge
    if abs(fs["vert"]["dx"] + pg.evaluate("() => window.__nbSbw || 0")) > 3 or abs(fs["vert"]["dy"]) > 3:
        errs.append("in full screen the vertical panel is %dpx/%dpx off the document's edge" % (fs["vert"]["dx"], fs["vert"]["dy"]))
    # The rail starts under the toolbar, so it is the document's height MINUS
    # the strip the toolbar takes — not the full height any more.
    if fs["vert"]["dh"] > 4 or fs["vert"]["dh"] < -140:
        errs.append("in full screen the vertical panel is not the document's full height (%dpx off)" % fs["vert"]["dh"])
    for _w in fs["widths"]:
        if abs(_w["rail"] - _w["nb"]) > 30:
            errs.append("in full screen at %d%% the panel is %dpx wide, the document %dpx"
                        % (_w["pct"], _w["rail"], _w["nb"]))
    if not fs["bodyFs"]:
        errs.append("full screen does not put the page into its full-width mode")
    if fs["toolbar"] != "none":
        errs.append("the notebook toolbar is still shown in full screen (%s)" % fs["toolbar"])
    if not (fs["inside"] and fs["ready"] and fs["dots"] >= _NDOTS):
        errs.append("the panel is not inside the full-screen element — it would vanish")
    if fs["pos"] != "fixed":
        errs.append("the panel lost position:fixed in full screen (%s)" % fs["pos"])
    out = pg.evaluate("""() => {
        Object.defineProperty(document, 'fullscreenElement',
            {configurable: true, get: function(){ return null; }});
        document.dispatchEvent(new Event('fullscreenchange'));
        var h = document.getElementById('nbpanel-root');
        return {parent: h.parentElement.tagName, ready: h.classList.contains('ready')};
    }""")
    print("after leaving full screen:", out)
    if out["parent"] != "BODY" or not out["ready"]:
        errs.append("the panel does not return to <body> after full screen")


    # ---- an OLD copy of the notebook in another tab ---------------------------
    # Its kernel runs an older script that tears the current panel down and pins
    # its own. The watchdog must bring this notebook's panel back.
    pg.evaluate("""() => {
        try { window.__nbrailTeardown(); } catch (e) {}
        var h = document.getElementById('nbpanel-root'); if (h) h.remove();
        var old = document.createElement('div');
        old.id = 'nbrail-host'; old.textContent = 'stale panel';
        document.body.appendChild(old);
        window.__nbrailVersion = '2026-01-01a';      // the older build announces itself
        window.__nbrailBeat = Date.now();
    }""")
    pg.wait_for_timeout(3500)
    rescue = pg.evaluate("""() => { var h = document.getElementById('nbpanel-root');
        return {version: window.__nbrailVersion,
                host: !!h, ready: h ? h.classList.contains('ready') : false,
                dots: h ? h.querySelectorAll('.nbrail-dot').length : 0,
                stale: !!document.getElementById('nbrail-host'),
                staleHidden: !!document.querySelector('body > #nbrail-host') ? 'present' : 'gone'}; }""")
    print("after an OLD build took over:", rescue)
    if rescue["version"] == "2026-01-01a":
        errs.append("an older script keeps the page — the watchdog did not re-arm")
    if not (rescue["host"] and rescue["ready"] and rescue["dots"] >= _NDOTS):
        errs.append("the panel did not come back after an older build took over")
    if rescue["stale"]:
        errs.append("the stale panel of the older build is still in the page")

    # ---- and the reverse: a NEWER panel is already running --------------------
    # Opening an old notebook must NOT downgrade a newer panel; the old one just
    # feeds it instead of taking over.
    taken = pg.evaluate("""(code) => {
        window.__nbrailVersion = '2999-01-01z';        // pretend a newer build runs
        window.__nbrailBeat = Date.now();
        window.__fedTheNewOne = false;
        window.__nbrailSync = function(){ window.__fedTheNewOne = true; };
        var tornDown = false;
        window.__nbrailTeardown = function(){ tornDown = true; };
        eval(code);
        return {version: window.__nbrailVersion, fed: window.__fedTheNewOne,
                tornDown: tornDown};
    }""", js)
    print("an older notebook against a newer panel:", taken)
    if taken["version"] != "2999-01-01z" or taken["tornDown"]:
        errs.append("an older notebook still takes over a newer panel")
    if not taken["fed"]:
        errs.append("the older notebook does not hand its progress to the newer panel")


    # ---- the panel waits for the finished structure --------------------------
    # (the real sync runs on its own interval — window.__nbrailSync is a spy from
    # the test above, so this waits instead of calling it)
    pg.evaluate("""(h) => {
        window.__nbrailFinal = false;                 // pretend a fresh page
        var host = document.getElementById('nbpanel-root'); if (host) host.remove();
        document.querySelectorAll('.nbfeed').forEach(function(e){ e.remove(); });
        var out = document.querySelector('.jp-OutputArea');
        var partial = document.createElement('div');
        partial.innerHTML = h.replace(' data-final="1"', '');    // a mirror, mid-render
        out.appendChild(partial);
    }""", panel_html)
    pg.wait_for_timeout(1800)
    mid = pg.evaluate("""() => { var h = document.getElementById('nbpanel-root');
        return !!(h && h.classList.contains('ready')); }""")
    pg.evaluate("""(h) => {
        var fin = document.createElement('div');
        fin.innerHTML = h;                                       // the finished panel
        document.querySelector('.jp-OutputArea').appendChild(fin);
    }""", panel_html)
    pg.wait_for_timeout(1800)
    done = pg.evaluate("""() => { var h = document.getElementById('nbpanel-root');
        return {ready: !!(h && h.classList.contains('ready')),
                dots: h ? h.querySelectorAll('.nbrail-dot').length : 0}; }""")
    print("panel while rendering:", mid, "| when finished:", done)
    if mid:
        errs.append("the panel shows a half-built timeline while the notebook renders")
    if not done["ready"] or done["dots"] < _NDOTS:
        errs.append("the panel does not appear once the notebook is finished (%s)" % done)

    # ---- the vertical panel ---------------------------------------------------
    # Turned onto the document's axis, a node must sit at the HEIGHT of the
    # heading it points at, the rail must scroll in lockstep with the document,
    # and the room must be taken beside the text instead of above it.
    pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var map = h.querySelector('.nbmap');
        var nodes = [].slice.call(map.querySelectorAll('.nbmap-node[data-target]'));
        var nb = document.querySelector('.jp-Notebook');
        window.__vprobe = [];
        nodes.forEach(function(n){
          var id = n.getAttribute('data-target');
          if (document.getElementById(id)) return;
          var block = document.createElement('div');
          block.style.cssText = 'height:300px;position:relative';
          // the anchor is a zero-height span sitting 56px ABOVE what it points
          // at, exactly as the real one is — and the pill it announces comes
          // further down still. Lining up on the anchor is what put every
          // circle a hundred pixels above its heading.
          var sp = document.createElement('span');
          sp.id = id;
          sp.style.cssText = 'display:block;height:0;position:relative;top:-56px';
          var pill = document.createElement('div');
          pill.className = 'lm-Collapse-header';
          pill.style.cssText = 'margin-top:90px;height:44px;background:#eee';
          block.appendChild(sp); block.appendChild(pill);
          nb.appendChild(block); window.__vprobe.push(block);
        });
        nb.scrollTop = 0;
        try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','v'); } catch(e){}
        window.__nbrailSync();
    }""")
    pg.wait_for_timeout(700)
    vert = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var map = h.querySelector('.nbmap'), inner = h.querySelector('.nbmap-inner');
        var sc = document.querySelector('.jp-Notebook');
        var ns = [].slice.call(inner.querySelectorAll('.nbmap-node[data-target]'));
        var off = [];
        ns.forEach(function(n){
          var el = document.getElementById(n.getAttribute('data-target'));
          if (!el) return;
          // only the blocks THIS probe built: an anchor left behind by an
          // earlier probe has no pill of its own, and asking its parent for
          // one hands back the next block's — which is the mock lying, not
          // the panel misplacing anything
          if ((window.__vprobe || []).indexOf(el.parentElement) < 0) return;
          var pill = el.parentElement.querySelector('.lm-Collapse-header');
          var r = (pill || el).getBoundingClientRect();
          off.push(Math.round(n.getBoundingClientRect().top - (r.top + r.height / 2)));
        });
        var hb = h.querySelector('.nbrail').getBoundingClientRect(),
            cb = h.querySelector('.nbdock').getBoundingClientRect(),
            nbb = sc.getBoundingClientRect();
        var sb = h.querySelector('.nbmap-inner');
        return {vert: h.classList.contains('vert'),
                worst: off.length ? Math.max.apply(null, off.map(Math.abs)) : null,
                seen: off.length,
                innerH: parseInt(sb.style.height || '0', 10), docH: sc.scrollHeight,
                lock: Math.round(map.scrollTop - sc.scrollTop),
                padT: sc.style.paddingTop || '',
                padR: getComputedStyle(document.documentElement)
                          .getPropertyValue('--nbvert-pad').trim(),
                dock: {inDoc: cb.left >= -2 && cb.right <= window.innerWidth + 2,
                       onScreen: cb.bottom <= window.innerHeight + 2 && cb.top >= -2,
                       w: Math.round(cb.width), h: Math.round(cb.height),
                       corner: Math.round(cb.left) + '/'
                             + Math.round(window.innerHeight - cb.bottom)},
                bar: map.offsetWidth - map.clientWidth,
                docBar: sc.offsetWidth - sc.clientWidth,
                scrollable: map.scrollHeight - map.clientHeight,
                hereOn: h.querySelector('.nbmap-here').classList.contains('on'),
                hereTop: h.querySelector('.nbmap-here').style.top,
                hereCentre: (function(){
                  // the marker's UPPER EDGE is the reading position: the rail is
                  // 1:1 with the document and scrolls with it, so the top of the
                  // visible rail is where the reader is
                  // the marker cannot go above the title bar, which sits 8px in
                  var m = h.querySelector('.nbmap-here'), mp = h.querySelector('.nbmap');
                  var lo = parseInt(h.dataset.railY0 || '0', 10) || 0;
                  return Math.round(parseFloat(m.style.top || 0)
                                    - Math.max(mp.scrollTop, lo));})()};
    }""")
    # and again after scrolling: the lockstep is the whole point
    pg.evaluate("""() => { var sc = document.querySelector('.jp-Notebook');
        sc.scrollTop = 1400; sc.dispatchEvent(new Event('scroll', {bubbles: true})); }""")
    pg.wait_for_timeout(300)
    vert["afterScroll"] = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var map = h.querySelector('.nbmap'), sc = document.querySelector('.jp-Notebook');
        var ns = [].slice.call(h.querySelectorAll('.nbmap-node[data-target]'));
        var off = [];
        ns.forEach(function(n){
          var el = document.getElementById(n.getAttribute('data-target'));
          if (!el) return;
          // only the blocks THIS probe built: an anchor left behind by an
          // earlier probe has no pill of its own, and asking its parent for
          // one hands back the next block's — which is the mock lying, not
          // the panel misplacing anything
          if ((window.__vprobe || []).indexOf(el.parentElement) < 0) return;
          var pill = el.parentElement.querySelector('.lm-Collapse-header');
          var r = (pill || el).getBoundingClientRect();
          off.push(Math.round(n.getBoundingClientRect().top - (r.top + r.height / 2)));
        });
        return {lock: Math.round(map.scrollTop - sc.scrollTop),
                worst: off.length ? Math.max.apply(null, off.map(Math.abs)) : null};
    }""")
    print("vertical panel:", vert)
    if not vert["vert"]:
        errs.append("the ⇅ button did not turn the panel vertical")
    else:
        if vert["seen"] < 5:
            errs.append("only %s anchored nodes measured in vertical mode" % vert["seen"])
        # 2026-09-24aw — THE RAIL IS A DIAGRAM, NOT A SCALE MODEL.
        # Until now this asserted that every mark sits at its pill's position
        # in the DOCUMENT. That contract is gone on purpose: the document is
        # not evenly distributed (one open chapter is a thousand pixels, six
        # folded ones fifty each), so the marks piled up and were hidden —
        # measured on Sets, five Appendix marks inside two pixels. The rail is
        # now spaced by what each mark IS. What has to hold instead is the
        # ORDER, a floor under the spacing, and the marker (checked separately
        # below) still tracking the scroll.
        if abs(vert["lock"]) > 2 or abs(vert["afterScroll"]["lock"]) > 2:
            errs.append("the rail is not locked to the document (%s / %s)"
                        % (vert["lock"], vert["afterScroll"]["lock"]))
        # the rail's own length is no longer the document's length either: it
        # reserves the title's gap below the last mark (24av).
        shape = pg.evaluate(_RAIL_SHAPE_JS)
        print("marks against their pills:",
              {k: v for k, v in shape.items() if k != "kinds"})
        print("   order:", shape["kinds"])
        # 2026-09-24bd — A MARK STANDS LEVEL WITH ITS PILL.
        # 24aw spaced the rail evenly instead and lost that; it was an
        # over-correction (the marks that piled up were already hidden). What
        # is asserted now is the contract the rail is FOR: every visible mark
        # is drawn exactly where its pill was measured, except where two would
        # really overlap — and there it moves by the least that separates them.
        if shape.get("noTables"):
            errs.append("the rail keeps no position tables — alignment cannot hold")
        if shape["back"]:
            errs.append("%d marks run backwards on the rail" % shape["back"])
        if shape["overlaps"]:
            errs.append("%d pairs of marks overlap on the rail" % shape["overlaps"])
        if shape["nudged"] and abs(shape["biggestNudge"]) > 80:
            errs.append("a mark is %dpx from its pill — that is not alignment"
                        % shape["biggestNudge"])
        if shape["n"] and shape["exact"] < shape["n"] * 0.6:
            errs.append("only %d of %d marks sit exactly on their pill"
                        % (shape["exact"], shape["n"]))
        _k = shape["kinds"].split()
        if _k and _k[0] not in ("title", "sect"):
            errs.append("the rail does not start at the title (%s)" % _k[0])
        if len(_k) > 2 and _k[-1] not in ("cell", "sect"):
            errs.append("the rail does not end on your own cell (%s)" % _k[-1])
        # 2026-09-28a (K1) — REVERSED. From 24az to 27h this block asserted
        # the gesture itself: clicking a locked mark ARMS it (its padlock
        # becomes a key on the rail and in the box, a window opens at the top)
        # and the key opens the chapter — the timeline's way past a lock, i.e.
        # a skip that does not happen at the exercise. The user decided on
        # 27.09.: skipping only by "Skip for now" at the exercise, no skip way
        # on the timeline. So now: a click on a locked mark arms nothing,
        # opens no lock window, and the mark still carries its DRAWN lock.
        lockflow = pg.evaluate(_LOCKFLOW_JS)
        print("the lock gesture:", lockflow)
        if lockflow.get("skipped"):
            print("   (no locked chapter in this mock — not checked)")
        else:
            if lockflow["armedRail"] != 0:
                errs.append("K1: a click on a locked mark still arms %s marks "
                            "(the timeline's skip way is back)" % lockflow["armedRail"])
            if lockflow["armedBox"] != 0:
                errs.append("K1: a click on a locked mark still arms %s boxes"
                            % lockflow["armedBox"])
            if lockflow.get("lockPage"):
                errs.append("K1: a click on a locked mark opened the lock window "
                            "at the top of the panel")
            if lockflow["afterOther"] != 0:
                errs.append("K1: %d marks armed after picking another" % lockflow["afterOther"])
            def _isopenlock(v):
                v = (v or "")
                return ("\U0001F513" in v) or ("1F513" in v.upper().replace(" ", ""))
            if _isopenlock(lockflow["railGlyph"]):
                errs.append("a locked mark shows the open-padlock emoji (%s)"
                            % lockflow["railGlyph"])
            if _isopenlock(lockflow["hoverGlyph"]):
                errs.append("hovering a locked mark still shows the open-padlock "
                            "emoji (%s)" % lockflow["hoverGlyph"])
            # the drawn lock: a shackle with a real border, and a filled body
            dl = lockflow.get("drawn") or {}
            if not dl.get("shackle") or float(dl.get("shackleBorder") or 0) <= 0:
                errs.append("a locked chapter mark carries no drawn shackle (%s)" % dl)
            if not dl.get("bodyBg") or "rgba(0, 0, 0, 0)" in str(dl.get("bodyBg")):
                errs.append("a locked chapter mark carries no drawn lock body (%s)" % dl)
        # K1.2 — a task fold that waits (acc-tasklock) refuses the click on its
        # header (the reader's, the timeline's expand(), the keyboard's) and
        # Enter/Space on it; an ordinary fold still takes the click.
        tlock = pg.evaluate("""() => {
            var mk = function(locked){
                var acc = document.createElement('div');
                acc.className = 'jupyter-widget-Accordion' + (locked ? ' acc-tasklock' : '');
                var col = document.createElement('div'); col.className = 'jupyter-widget-Collapse';
                var hd = document.createElement('div'); hd.className = 'jupyter-widget-Collapse-header';
                hd.tabIndex = 0; hd.textContent = locked ? 'locked' : 'free';
                var got = {click: 0, key: 0};
                hd.addEventListener('click', function(){ got.click++; });
                hd.addEventListener('keydown', function(){ got.key++; });
                col.appendChild(hd); acc.appendChild(col);
                document.querySelector('.jp-OutputArea').appendChild(acc);
                return {hd: hd, got: got, acc: acc};
            };
            var L = mk(true), F = mk(false);
            L.hd.click(); F.hd.click();
            L.hd.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true, cancelable: true}));
            F.hd.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', bubbles: true, cancelable: true}));
            L.acc.classList.remove('acc-tasklock');      // the lock comes off
            L.hd.click();
            var out = {lockedClick: L.got.click, lockedKey: L.got.key,
                       freeClick: F.got.click, freeKey: F.got.key,
                       fn: typeof window.__nbTaskLocked};
            L.acc.remove(); F.acc.remove();
            return out;
        }""")
        print("K1 task lock:", tlock)
        if tlock["fn"] != "function":
            errs.append("K1: the page has no task-lock guard (__nbTaskLocked)")
        if tlock["lockedClick"] != 1:
            errs.append("K1: a waiting task fold took %d clicks while locked "
                        "(want 0, then 1 once open)" % tlock["lockedClick"])
        if tlock["lockedKey"] != 0:
            errs.append("K1: Enter reached a waiting task fold's header")
        if tlock["freeClick"] != 1 or tlock["freeKey"] != 1:
            errs.append("K1: an ordinary fold lost its click or key (%s)" % tlock)
        if not vert["padT"]:
            errs.append("vertical reserves no room for the toolbar above the document")
        # 2026-09-27b — REVERSED. Until 27a this asserted that the vertical
        # panel took a strip off the document (--nbvert-pad) — the very thing
        # the reader filmed: opening the panel pushed the text, the zoom and
        # the profile chip to the left. The panel is an overlay now (STRUKTUR
        # §4); a reserve coming back is the regression.
        if vert["padR"] not in ("", "0px"):
            errs.append("vertical reserves room beside the document again "
                        "(--nbvert-pad %r) — the panel is an overlay" % vert["padR"])
        # The reason the dock exists: in the vertical rail the controls were
        # pushed off the bottom of the column and could not be reached at all.
        if not vert["dock"]["onScreen"]:
            errs.append("the controls are off screen in vertical mode (%s)"
                        % vert["dock"])
        if not vert["dock"]["inDoc"]:
            errs.append("the controls are not inside the window (%s)"
                        % vert["dock"])
        # A headless Chromium draws overlay scrollbars (zero width) — so the test
        # is that the rail scrolls and that its bar is as wide as the document's,
        # whatever this platform makes that.
        if vert["scrollable"] < 100:
            errs.append("the rail does not scroll with the document (%s)" % vert["scrollable"])
        if vert["bar"] != vert["docBar"]:
            errs.append("the rail's scrollbar (%dpx) does not match the document's (%dpx)"
                        % (vert["bar"], vert["docBar"]))
        if not vert["hereOn"]:
            errs.append("the reading marker is gone once the panel is flipped")
        # 2026-09-24o: the marker is centred ON the title mark's line, so its
        # top edge sits half its own height above it — by design.
        elif not (-26 <= vert["hereCentre"] <= 2):
            errs.append("the flipped marker is %dpx off the title mark's line"
                        % vert["hereCentre"])

    # In VERTICAL the panel control sets the WIDTH: the height belongs to the
    # document, and the thickness of the line must not change or the nodes would
    # leave the heights of their headings.
    gui = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var sc = document.querySelector('.jp-Notebook');
        var box = function(){ var b = h.querySelector('.nbrail').getBoundingClientRect();
          return {w: Math.round(b.width), h: Math.round(b.height)}; };
        var b0 = box();
        var inp = h.querySelector('.nbz-gui .nbslider');
        if (!inp) return {skipped: true};
        inp.value = '20'; inp.dispatchEvent(new Event('input', {bubbles: true}));
        // (thumb 20 -> 80 % of panel; the readout mirrors the thumb)
        var out = {lab: h.querySelector('.nbz-gui .nbslval').textContent,
                   docZoom: document.body.style.zoom || '(none)',
                   railZoom: h.querySelector('.nbrail').style.zoom || '(none)',
                   thick: document.documentElement.style.getPropertyValue('--nbthick'),
                   b0: b0, b1: box(), scH: sc.clientHeight};
        inp.dispatchEvent(new MouseEvent('dblclick', {bubbles: true, cancelable: true}));
        window.__nbrailSync();
        out.back = box();
        return out;
    }""")
    print("the panel control, vertical:", gui)
    if gui.get("skipped"):
        pass                     # nothing to drive; see the note in the mock
    elif "80" not in gui["lab"]:  # noqa
        errs.append("two clicks on the panel control did not reach 80%% (%s)" % gui["lab"])
    if not gui.get("skipped") and gui["docZoom"] != "(none)":
        errs.append("the panel control moved the DOCUMENT too (%s)" % gui["docZoom"])
    if not gui.get("skipped") and gui["railZoom"] != "(none)":
        errs.append("the panel control still zooms the rail (%s)" % gui["railZoom"])
    # The Panel control is a proportional zoom of the rail now: width AND the
    # markers AND the names, all by the same factor — what Ctrl+wheel does to a
    # page, applied to the rail alone.
    # 2026-09-24x: the control's 0-100 maps onto 0.5-1.0 of the panel's WIDTH
    # but onto 0.82-1.0 of the marker size — a narrow panel must still be a
    # readable rail. So 80 % on the control is 0.82 + 0.18*0.8 = 0.964.
    if not gui.get("skipped") and abs(float(gui["thick"] or 1) - 0.964) > 1e-6:
        errs.append("the panel control did not scale the markers (thick %s, wanted 0.964)"
                    % gui["thick"])
    if not gui.get("skipped") and not (gui["b1"]["w"] < gui["b0"]["w"]):
        errs.append("the panel control did not narrow the rail (%s -> %s)"
                    % (gui["b0"]["w"], gui["b1"]["w"]))
    if not gui.get("skipped") and not (gui["b1"]["w"] < gui["b0"]["w"] - 20):
        errs.append("vertical: the panel did not get narrower (%d -> %d)"
                    % (gui["b0"]["w"], gui["b1"]["w"]))
    if not gui.get("skipped") and abs(gui["b1"]["h"] - gui["b0"]["h"]) > 4:
        errs.append("vertical: the panel changed height (%d -> %d)"
                    % (gui["b0"]["h"], gui["b1"]["h"]))
    # 2026-09-24r: the reset goes back to the DEFAULT, and the default is the
    # narrow rail (0 %), not full size.
    if not gui.get("skipped") and gui["back"]["w"] >= gui["b0"]["w"]:
        errs.append("clicking the panel label does not reset to the narrow rail (%s)"
                    % gui["back"])

    # 2026-09-24ar — THE TWO LANES LIGHT UP, AND THE MARKER FADES.
    # The green lane and the purple coding lane each carry a halo, in both
    # themes; the marker's trail is a band whose brightness runs out away from
    # the mark the marker sits on, so the light points back at the reader's
    # position. The trail only exists while the reading position is BETWEEN two
    # marks, so the scroller is walked until one appears — and the direction
    # must flip as the travel changes sign.
    lanes = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var pick = function(sel, ps){
            var e = h.querySelector(sel); if (!e) return null;
            var s = getComputedStyle(e), o = {};
            ps.forEach(function(p){ o[p] = s.getPropertyValue(p); }); return o; };
        var read = function(){
            return {green: pick('.nbmap-fill:not(.tail):not(.code)',
                                ['background-color', 'box-shadow']),
                    code: pick('.nbmap-fill.code', ['box-shadow'])}; };
        // 2026-09-25: `nbdark` is the brightness, so the probe sets THAT.
        var was = document.body.classList.contains('nbdark');
        document.body.classList.remove('nbdark', 'nbforce-light');
        var light = read();
        document.body.classList.add('nbdark');
        var dark = read();
        document.body.classList.toggle('nbdark', was);
        return {light: light, dark: dark};
    }""")
    print("the lanes' halo:", lanes)
    for _th in ("light", "dark"):
        for _lane in ("green", "code"):
            _v = lanes[_th][_lane]
            if not _v or "none" in _v["box-shadow"]:
                errs.append("the %s lane has no halo in the %s theme (%s)"
                            % (_lane, _th, _v))
    if lanes["light"]["green"]["background-color"] == \
       lanes["dark"]["green"]["background-color"]:
        errs.append("the green lane is the same ink in both themes (%s)"
                    % lanes["light"]["green"]["background-color"])
    # 2026-10-02 (E16.3, CSS) — THIS BEHAUPTETE BISHER (E12.5 / E11.8t,
    # 24ar, 28c) "the marker leaves a trail: one band BEHIND it, fading,
    # blurred, gone 1.4 s after it stops". The user took the trail back
    # (E16.3, 02.10.): the marker's light is ONE CIRCLE in the layer under
    # it — round (width = height ±1 px), centred on the marker's head ±1 px
    # (= the reading height), no band, no trail at rest or in motion.
    # 2026-10-02 (E21.8, JS) — AND THIS BEHAUPTETE BISHER "no trail": it looked
    # for the element `.nbmap-trail`, which E16.3 deleted — blind, green with a
    # trail on screen. E21.8 brings the trail back, drawn by CSS from the
    # marker's `--nbm-y` (css-E21.8 measures the trail in pixels, C8). What this
    # suite holds JS to is the contract: `--nbm-y` = the marker's `top`, at
    # rest and in every step of a move.
    def _to(y):
        pg.evaluate("""(y) => {
            if (window.__nbLandStop) window.__nbLandStop();
            var s = document.querySelector('.jp-WindowedPanel-outer')
                 || document.querySelector('.jp-Notebook');
            s.scrollTop = y; s.dispatchEvent(new Event('scroll', {bubbles: true}));
        }""", y)
    def _lt():
        return pg.evaluate("""() => {
            var m = document.querySelector('#nbpanel-root .nbmap-here');
            if (!m) return null;
            var mr = m.getBoundingClientRect(), a = getComputedStyle(m, '::after'),
                b = getComputedStyle(m, '::before');
            var w = parseFloat(a.width) || 0, h = parseFloat(a.height) || 0;
            var cy = mr.top + m.clientTop + (parseFloat(a.top) || 0) + (parseFloat(a.marginTop) || 0) + h / 2;
            var hy = mr.top + m.clientTop + (parseFloat(b.top) || 0) + (parseFloat(b.marginTop) || 0) + (parseFloat(b.height) || 0) / 2;
            return {w: w, h: h, cy: cy, hy: hy, z: a.zIndex,
                    lit: a.content !== 'none' && a.display !== 'none',
                    top: m.style.top, y: m.style.getPropertyValue('--nbm-y')};
        }""")
    _seen = []
    _to(300); pg.wait_for_timeout(1400); _seen.append(("rest", _lt()))
    for _k, _y in enumerate((360, 420, 380, 900, 600)):
        _to(_y); pg.wait_for_timeout(40); _seen.append(("moving %d" % _k, _lt()))
    print("the marker's light:", [(n, s and (round(s["w"], 1), round(s["h"], 1), round(s["cy"] - s["hy"], 1), s["z"], s["top"], s["y"])) for n, s in _seen])
    for _nm, _s in _seen:
        if not _s or not _s["lit"]:
            errs.append("%s, the marker has no light (%s)" % (_nm, _s)); continue
        if not _s["top"] or _s["y"] != _s["top"]:
            errs.append("%s, the marker's --nbm-y (%r) is not its top (%r) — no trail for CSS (E21.8)" % (_nm, _s["y"], _s["top"]))
        if abs(_s["w"] - _s["h"]) > 1:
            errs.append("%s, the marker's light is not round (%.1f x %.1f)" % (_nm, _s["w"], _s["h"]))
        if abs(_s["cy"] - _s["hy"]) > 1:
            errs.append("%s, the marker's light is not centred on it (%.1f vs %.1f)" % (_nm, _s["cy"], _s["hy"]))
        if _s["z"] != "-1":
            errs.append("%s, the marker's light is not under the marker (z-index %s)" % (_nm, _s["z"]))

    # 2026-09-24as — THE MARKS FIT ON THE RAIL, AND THE OPEN DOORS GLOW.
    # A diamond is a square turned 45°, so what has to fit between two
    # neighbours is its DIAGONAL, not its width — that was the whole bug: 42px
    # boxes reading as 60px of vertical space against gaps of 51px and 55px.
    # This measures the same way the rail lays out: every visible mark's extent
    # along the column against the distance to its neighbour.
    fit = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var out = [];
        h.querySelectorAll('.nbmap-node').forEach(function(n){
            if (n.classList.contains('nbgone')) return;
            var m = n.querySelector('.nbsect,.nbchapdot,.nbsubdot,.nbrail-dot,'
                                  + '.nbvizmark,.nbcodemark');
            if (!m) return;
            var c = getComputedStyle(m), w = parseFloat(c.width);
            out.push({y: n.offsetTop, mark: m.className.split(' ')[0],
                      extent: Math.round(c.transform.indexOf('0.707') >= 0
                                         ? w * Math.SQRT2 : w)});
        });
        out.sort(function(a, b){ return a.y - b.y; });
        var worst = null, pairs = 0;
        for (var i = 1; i < out.length; i++) {
            var slack = (out[i].y - out[i-1].y)
                      - (out[i].extent + out[i-1].extent) / 2;
            pairs++;
            if (worst === null || slack < worst.slack)
                worst = {slack: Math.round(slack), a: out[i-1].mark,
                         b: out[i].mark, dy: out[i].y - out[i-1].y};
        }
        var big = {};
        out.forEach(function(m){
            if (!big[m.mark] || m.extent > big[m.mark]) big[m.mark] = m.extent; });
        return {pairs: pairs, worst: worst, extent: big};
    }""")
    print("marks against their neighbours:", fit)
    if fit["worst"] and fit["worst"]["slack"] < 0:
        errs.append("marks overlap on the rail: %s and %s are %dpx apart and "
                    "need %dpx" % (fit["worst"]["a"], fit["worst"]["b"],
                                   fit["worst"]["dy"],
                                   fit["worst"]["dy"] - fit["worst"]["slack"]))
    _ex = fit["extent"].get("nbrail-dot", 0)
    _ch = fit["extent"].get("nbchapdot", 0)
    if _ex and _ch and _ex > _ch * 1.6:
        errs.append("the exercise mark is %dpx against a %dpx chapter — too big"
                    % (_ex, _ch))
    doors = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var read = function(){
            var g = h.querySelector('.nbmap-node.is-current .nbrail-dot');
            var p = h.querySelector('.nbcodemark.cd-current');
            var st = function(e){ if (!e) return null; var c = getComputedStyle(e);
                return {bg: c.backgroundColor, sh: c.boxShadow}; };
            return {green: st(g), purple: st(p),
                    railbg: getComputedStyle(h.querySelector('.nbrail'))
                              .getPropertyValue('--nbrail-bg').trim()}; };
        // 2026-09-25: `nbdark` is the brightness, so the probe sets THAT.
        var was = document.body.classList.contains('nbdark');
        document.body.classList.remove('nbdark', 'nbforce-light');
        var light = read();
        document.body.classList.add('nbdark');
        var dark = read();
        document.body.classList.toggle('nbdark', was);
        return {light: light, dark: dark};
    }""")
    print("the two open doors:", {t: {k: (v and v["sh"][:52]) for k, v in d.items()
                                      if k != "railbg"} for t, d in doors.items()})
    for _th in ("light", "dark"):
        for _which in ("green", "purple"):
            _m = doors[_th][_which]
            if not _m:
                errs.append("no %s open door on the rail (%s theme)" % (_which, _th))
                continue
            # a glow is a BLURRED shadow; the flat 0-blur ring is the cut-out
            _blurred = [s for s in _m["sh"].split("px,")
                        if "0px 0px 0px" not in s and "0px 0px" in s]
            if not _blurred:
                errs.append("the %s open door has no glow in the %s theme (%s)"
                            % (_which, _th, _m["sh"]))
            if "rgba(0, 0, 0, 0)" == _m["bg"]:
                errs.append("the %s open door has no tinted fill (%s theme)"
                            % (_which, _th))
        # the cut-out ring must be the rail's OWN background, or a light ring
        # appears around every mark on a dark rail (the 24am bug)
        _want = doors[_th]["railbg"].lstrip("#").lower()
        _rgb = tuple(int(_want[i:i+2], 16) for i in (0, 2, 4)) if len(_want) == 6 else None
        if _rgb and doors[_th]["green"]:
            _first = doors[_th]["green"]["sh"].split(",")[0:3]
            if "rgb(%d, %d, %d)" % _rgb not in ",".join(_first):
                errs.append("the %s cut-out ring is not the rail's background "
                            "(%s vs %s)" % (_th, _first, _rgb))

    # and back: horizontal must come back clean
    pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','h'); } catch(e){}
        window.__nbrailSync();
    }""")
    pg.wait_for_timeout(600)
    back = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var sc = document.querySelector('.jp-Notebook');
        var n = h.querySelector('.nbmap-node');
        (window.__vprobe || []).forEach(function(b){ b.remove(); });
        sc.scrollTop = 0;
        return {vert: h.classList.contains('vert'),
                padR: getComputedStyle(document.documentElement)
                          .getPropertyValue('--nbvert-pad').trim(),
                padT: sc.style.paddingTop || '', nodeTop: n.style.top || '',
                h: h.style.height || '', pos: getComputedStyle(n).position};
    }""")
    print("back to horizontal:", back)
    # In HORIZONTAL the control sets the THICKNESS: the width stays the
    # document's, the panel reaches less far down the page, and detail falls
    # away in order — names, glyphs, circles, bars, dots.
    thick = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var rail = h.querySelector('.nbrail');
        var steps = [100, 80, 65, 50, 40, 30];
        var out = [];
        var det = ['det-text','det-emoji','det-circle','det-bar','det-dot'];
        var inp = h.querySelector('.nbz-gui .nbslider');
        // 2026-09-24ao: the panel's own size control is gone from the toolbar,
        // so these measurements have nothing to drive.
        if (!inp) return {skipped: true, nbw: Math.round(
          document.querySelector('.jp-Notebook').clientWidth)};
        steps.forEach(function(p){
          inp.value = String(100 - p);
          inp.dispatchEvent(new Event('input', {bubbles: true}));
          var b = rail.getBoundingClientRect();
          out.push({pct: p, w: Math.round(b.width), h: Math.round(b.height),
                    thick: document.documentElement.style.getPropertyValue('--nbthick'),
                    off: det.filter(function(c){ return h.classList.contains(c); })});
        });
        inp.value = '0';
        inp.dispatchEvent(new Event('input', {bubbles: true}));
        var nbw = Math.round(document.querySelector('.jp-Notebook').clientWidth);
        return {steps: out, nbw: nbw};
    }""")
    # Distorting the panel must not knock the markers off the line: at every
    # thickness the middle of every marker is the middle of the track.
    centred = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var inp = h.querySelector('.nbz-gui .nbslider');
        if (!inp) return [];
        var inner = h.querySelector('.nbmap-inner');
        var out = [];
        [100, 75, 55, 40].forEach(function(p){
          inp.value = String(100 - p);
          inp.dispatchEvent(new Event('input', {bubbles: true}));
          var tr = getComputedStyle(inner, '::before');
          var mid = parseFloat(tr.top) + parseFloat(tr.height) / 2;
          var ib = inner.getBoundingClientRect();
          var worst = 0, what = '';
          ['.nbsect', '.nbchapdot', '.nbsubdot', '.nbrail-dot',
           '.nbmap-fill', '.nbmap-fill.code', '.nbmap-here'].forEach(function(sel){
            var e = inner.querySelector(sel);
            if (!e) return;
            var b = e.getBoundingClientRect();
            if (!b.height) return;
            var c = b.top + b.height / 2 - ib.top;
            if (Math.abs(c - mid) > Math.abs(worst)) { worst = c - mid; what = sel; }
          });
          out.push({pct: p, axis: Math.round(mid), off: Math.round(worst), what: what});
        });
        inp.value = '0'; inp.dispatchEvent(new Event('input', {bubbles: true}));
        return out;
    }""")
    print("centring while distorting:",
          ", ".join("%d%%: axis %d, worst %+d (%s)"
                    % (c["pct"], c["axis"], c["off"], c["what"]) for c in centred))
    for _c in centred:
        if abs(_c["off"]) > 2:
            errs.append("at %d%% the %s sits %+dpx off the line's middle"
                        % (_c["pct"], _c["what"], _c["off"]))

    # 2026-09-24ao: the panel's own zoom slider (.nbz-gui) is gone. Only the
    # document slider is left, and it stays flat in the corner of the toolbar.
    updown = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var g = h.querySelector('.nbz-gui .nbslider');
        var d = h.querySelector('.nbz-doc .nbslider');
        var box = function(e){ if (!e) return null;
          var b = e.getBoundingClientRect();
          return {w: Math.round(b.width), h: Math.round(b.height)}; };
        return {guiFlat: box(g), docFlat: box(d)};
    }""")

    # 2026-09-24bg — SKINS. Brightness and material are two axes: the skin
    # button must cycle all of them and repaint the document, and it must not
    # touch light/dark on the way round. E24.6 (06.10.): three styles — retro
    # is not offered any more; this asserted four until then. E34 (19.10.): four
    # again — „digi“ (the standard) + minimal, cyber, fairy; asserted three until then.
    skins = pg.evaluate("""async () => {
        const b = document.querySelector('#nbpanel-root .nbbtn.nbskin');
        if (!b) return {missing: true};
        const seen = [];
        for (let i = 0; i < 5; i++) {
          const box = document.querySelector('.nbbox') || document.querySelector('.nblock');
          const cs = box ? getComputedStyle(box) : null;
          seen.push({face: b.textContent,
                     skin: Array.prototype.filter.call(document.body.classList,
                             c => c.indexOf('nbskin-') === 0).join(',') || 'minimal',
                     dark: document.body.classList.contains('nbdark'),
                     paint: cs ? (cs.backgroundImage !== 'none'
                                  ? cs.backgroundImage.slice(0, 40)
                                  : cs.backgroundColor) : null});
          if (i < 4) { b.click(); await new Promise(r => setTimeout(r, 420)); }
        }
        return {seen: seen};
    }""")
    if skins.get("missing"):
        errs.append("the style button is missing from the toolbar")
    else:
        _s = skins["seen"]
        print("the style button:")
        for _x in _s: print("   ", _x)
        _names = [x["skin"] for x in _s]
        if len(set(_names[:4])) != 4 or any("retro" in n for n in _names) or _names[0] != "nbskin-digi":
            errs.append("the style button does not cycle the four styles from digi (%s)" % _names)
        if _names[0] != _names[4]:
            errs.append("the style button does not come back round (%s)" % _names)
        if len({x["dark"] for x in _s}) != 1:
            errs.append("changing the style changed light/dark as well")
        if all(x["paint"] is None for x in _s):
            # the JS suite drives a mock page with no prose boxes in it;
            # test_links checks the skins' rules from Python instead
            print("   (no document box in this mock — repaint not checked)")
        elif len({str(x["paint"]) for x in _s}) < 4:
            errs.append("the styles do not repaint the document (%s)"
                        % [x["paint"] for x in _s])
        if len({x["face"] for x in _s[:4]}) != 4:
            errs.append("the style button does not show which style is on (%s)"
                        % [x["face"] for x in _s])

    print("the document slider in the corner:", updown)
    if updown["guiFlat"] is not None:
        errs.append("the panel's own zoom slider is back (%s)" % updown["guiFlat"])
    if updown["docFlat"] is None:
        errs.append("the document zoom slider is missing from the toolbar")
    # R3 · 17 Teil 2: in its corner the document slider stood upright.
    # 2026-09-30 (E10) — E6.6 (user, 29.09.) put the lens top left beside
    # full screen, LYING DOWN (magnifier, then the slider, 96 × 16). Until
    # E10 this asserted upright and was red since v1.25.
    elif updown["docFlat"]["h"] >= updown["docFlat"]["w"]:
        errs.append("the document slider should lie beside full screen (%s)" % updown["docFlat"])

    # 2026-09-24ao: the detail ladder was driven by the panel's own zoom
    # control. With the names off the rail there was nothing in a wide panel
    # to look at, so the control went — and with it this ladder. The rail now
    # renders at one size; what is left to check is that it still does.
    if thick.get("skipped"):
        print("thickness and the detail ladder: skipped — the panel zoom is gone")
        _fixed = pg.evaluate("""() => {
            var h = document.getElementById('nbpanel-root');
            var r = h.querySelector('.nbrail').getBoundingClientRect();
            return {w: Math.round(r.width), h: Math.round(r.height),
                    thick: getComputedStyle(h).getPropertyValue('--nbthick').trim(),
                    off: Array.prototype.filter.call(h.classList, function(c){
                           return c.indexOf('det-') === 0; })};
        }""")
        print("   the rail at its one size:", _fixed)
        # 2026-09-24: the rail's fixed size is the old control's 0 %, i.e. half
        # thickness — the reader asked for that as the default before the
        # control went. The ladder must still agree with that thickness.
        _LADDER = [("det-text", .85), ("det-emoji", .70), ("det-circle", .58),
                   ("det-bar", .46), ("det-dot", .36)]
        _t = float(_fixed["thick"] or 1)
        _want_i = [c for c, thr in _LADDER if _t < thr]
        if _fixed["off"] != _want_i:
            errs.append("at thickness %s the detail ladder is %s, wanted %s"
                        % (_fixed["thick"], _fixed["off"], _want_i))
        if abs(_t - 0.5) > 1e-6:
            errs.append("the rail's fixed thickness is %s, wanted 0.5" % _fixed["thick"])

        # 2026-09-24bf — THE GRIP IS THE SIZE CONTROL NOW.
        # A short bar on the rail's left flank, half way down. Dragging it left
        # widens the panel by exactly as far as the pointer travelled; dragging
        # it right folds it back. A click with no drag jumps to the other end.
        # Measured through real pointer events, not by calling setGui: what is
        # in doubt is the gesture, not the arithmetic behind it.
        # the grip belongs to the VERTICAL panel, and by this point the suite
        # has put the rail back across the top — so it is turned on for this
        # probe and off again after it.
        pg.evaluate("() => { try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','v'); }"
                    " catch(e){} window.__nbrailSync(); }")
        pg.wait_for_timeout(700)
        grip = pg.evaluate("""() => {
            var h = document.getElementById('nbpanel-root');
            var g = h.querySelector('.nbgrip');
            if (!g) return {missing: true};
            var gr = g.getBoundingClientRect();
            var rr = h.querySelector('.nbrail').getBoundingClientRect();
            var cs = getComputedStyle(g);
            var mp = h.querySelector('.nbmap');
            var y0g = parseInt(h.dataset.railY0 || '0', 10) || 0;
            return {x: Math.round(gr.left + gr.width / 2),
                    y: Math.round(gr.top + gr.height / 2),
                    offLine: mp && y0g > 0 ? Math.round(gr.top + gr.height / 2
                             - (mp.getBoundingClientRect().top + y0g)) : null,
                    fromLeft: Math.round(gr.left - rr.left),
                    offCentre: Math.round((gr.top + gr.height / 2)
                                          - (rr.top + rr.height / 2)),
                    w: Math.round(gr.width), h: Math.round(gr.height),
                    shown: cs.display !== 'none' && cs.visibility !== 'hidden',
                    cursor: cs.cursor, railW: Math.round(rr.width)};
        }""")
        print("the grip:", grip)
        if grip.get("missing"):
            errs.append("the panel has no grip — the size control is gone again")
        else:
            if not grip["shown"]:
                errs.append("the grip is not visible in the vertical panel")
            if grip["fromLeft"] > 24:
                errs.append("the grip is %dpx from the panel's left edge, not on it"
                            % grip["fromLeft"])
            # 2026-09-30 (E10) — E9.1 (user): the knob stands ON THE READING
            # HEIGHT (with marker, cursor and .nbreadfix) and is dragged both
            # ways — sideways the width, up and down the line; its cursor is
            # `grab` (CSS-E9.1). Until E10 this asserted "half way down the
            # panel ±30" and `ew-resize`, the knob of 24bf.
            if grip["offLine"] is None or abs(grip["offLine"]) > 1:
                errs.append("the grip is %spx off the reading height" % grip["offLine"])
            if grip["cursor"] != "grab":
                errs.append("the grip does not offer to be dragged (%s, wanted grab)" % grip["cursor"])
            def _railw():
                return pg.evaluate("() => Math.round(document.getElementById('nbpanel-root')"
                                   ".querySelector('.nbrail').getBoundingClientRect().width)")
            def _drag(dx):
                g = pg.evaluate("""() => {
                    var r = document.querySelector('#nbpanel-root .nbgrip')
                              .getBoundingClientRect();
                    return [Math.round(r.left + r.width/2), Math.round(r.top + r.height/2)];
                }""")
                pg.mouse.move(g[0], g[1]); pg.mouse.down()
                for _i in range(1, 7):
                    pg.mouse.move(g[0] + dx * _i / 6.0, g[1])
                pg.mouse.up(); pg.wait_for_timeout(350)
            _w0 = _railw()
            _drag(-110)                       # to the LEFT: wider
            _w1 = _railw()
            _drag(110)                        # and back to the right: narrower
            _w2 = _railw()
            print("   dragging it: %d -> %d -> %d px" % (_w0, _w1, _w2))
            if _w1 - _w0 < 60:
                errs.append("dragging the grip 110px left widened the panel by %d px"
                            % (_w1 - _w0))
            if _w1 - _w2 < 60:
                errs.append("dragging the grip back right narrowed the panel by %d px"
                            % (_w1 - _w2))
            _w3 = _railw()
            pg.evaluate("""() => {
                var g = document.querySelector('#nbpanel-root .nbgrip');
                var r = g.getBoundingClientRect();
                var at = {clientX: r.left + r.width/2, clientY: r.top + r.height/2,
                          bubbles: true, cancelable: true, button: 0};
                g.dispatchEvent(new PointerEvent('pointerdown', at));
                document.dispatchEvent(new PointerEvent('pointerup', at));
            }""")
            pg.wait_for_timeout(350)
            _w4 = _railw()
            print("   a click with no drag: %d -> %d px" % (_w3, _w4))
            if abs(_w4 - _w3) < 60:
                errs.append("a click on the grip does nothing (%d -> %d)" % (_w3, _w4))

    # ---- 2026-09-25d: THE CONTROL'S TWO ENDS, AND EVERYTHING BETWEEN -------
    # The panel has to close to the line alone and open to a column with the
    # structure written in it. Both ends, and the fact that nothing overlaps
    # anywhere in between, are measurements — and the measurement is the only
    # way to catch the shape of the failure this replaced: marks that stayed
    # full size until the very last step of the control and then vanished.
    _range = []
    for _pct in (0, 10, 25, 50, 75, 100):
        pg.evaluate("(p) => { if (window.__nbSetGui) window.__nbSetGui(p); }", _pct)
        pg.wait_for_timeout(260)
        _range.append(pg.evaluate("""() => {
            var h = document.getElementById('nbpanel-root');
            var cs = getComputedStyle(document.documentElement);
            var ys = [];
            h.querySelectorAll('.nbmap-node').forEach(function(n){
              if (n.classList.contains('nbgone')) return;
              var m = n.querySelector('.nbsect,.nbchapdot,.nbsubdot,.nbrail-dot,'
                                    + '.nbvizmark,.nbcodemark');
              if (!m) return;
              var r = m.getBoundingClientRect();
              if (r.height < 0.6) return;
              var c = getComputedStyle(m);
              var side = parseFloat(c.height) || r.height;
              ys.push({y: r.top + r.height / 2,
                       e: c.transform.indexOf('0.707') >= 0 ? side * 1.4142 : side});
            });
            ys.sort(function(a, b){ return a.y - b.y; });
            var over = 0, tight = 1e9;
            for (var q = 1; q < ys.length; q++) {
              var g = (ys[q].y - ys[q-1].y) - (ys[q].e + ys[q-1].e) / 2;
              if (g < 0) over++;
              if (g < tight) tight = g;
            }
            var w = Math.round(h.querySelector('.nbrail').getBoundingClientRect().width);
            var axis = parseFloat(cs.getPropertyValue('--nbvert-axis')) || 0;
            // 2026-09-27b — the smallest mark as LAID OUT (before the turn), and
            // whether any rung of the ladder that fades marks is on
            var side = 1e9;
            h.querySelectorAll('.nbmap-node:not(.nbgone)').forEach(function(n){
              var m = n.querySelector('.nbsect,.nbchapdot,.nbsubdot,.nbrail-dot,'
                                    + '.nbvizmark,.nbcodemark');
              if (!m) return;
              var c = getComputedStyle(m);
              if (c.display === 'none') return;
              var sw = parseFloat(c.width) || 0, sh = parseFloat(c.height) || 0;
              if (sw > 0.5 && sh > 0.5) side = Math.min(side, sw, sh);
            });
            var fl = window.__nbFloorCache && window.__nbFloorCache.f;
            return {w: w, axis: Math.round(axis),
                    wmin: window.__nbWmin || null,
                    floor: fl ? Math.round(fl.t * 1000) / 1000 : null,
                    side: side === 1e9 ? null : Math.round(side * 10) / 10,
                    fade: Array.prototype.filter.call(h.classList, function(c){
                      return c === 'det-circle' || c === 'det-bar' || c === 'det-dot'; }),
                    // E10: the lane is the middle of the room LEFT of the
                    // scroll-bar cursor (E9.1 reserves 14·K at the right)
                    // E11.6: THIS BEHAUPTETE BISHER "the middle of the room
                    // left of the cursor". The cursor left the panel (its own
                    // column right of it), nothing is reserved: the lane is
                    // the panel's middle again, shut and open.
                    off: Math.round(axis - w / 2),
                    // E7.1: where the pips do not fit right of the middle,
                    // the lane stands left of it by exactly their room
                    pipLane: (window.__nbPipNeedK || 0) > 0 ? Math.floor(w - 2
                             - (window.__nbPipNeedK || 0) * (window.__nbK || 1)) : null,
                    thick: Math.round((parseFloat(cs.getPropertyValue('--nbthick')) || 0) * 1000) / 1000,
                    lab: Math.round(parseFloat(cs.getPropertyValue('--nbvert-lab')) || 0),
                    names: h.classList.contains('nbnames'),
                    overlaps: over,
                    tight: tight === 1e9 ? null : Math.round(tight * 10) / 10};
        }"""))
    print("the control's range:", _range)
    _lo, _hi = _range[0], _range[-1]
    # 2026-09-27b — THE NARROW END IS SET BY THE MARKS (STRUKTUR §4a).
    # Until 27a this asserted "collapsed <= 24px" and "marks <= 0.30 of full
    # size": the rule that shrank every mark to 4px and faded 14 of 15 out —
    # green BECAUSE of the defect the reader filmed. Now: shut, the panel is
    # exactly as wide as the marks' floor asks (__nbWmin), the smallest mark is
    # at least 10px, and no rung of the ladder fades a mark.
    if _lo["wmin"] is None or abs(_lo["w"] - _lo["wmin"]) > 1:
        errs.append("collapsed, the panel is %spx, the marks' floor asks for %s"
                    % (_lo["w"], _lo["wmin"]))
    if _lo["wmin"] is not None and _lo["wmin"] > 48:
        errs.append("collapsed, the panel is still %dpx wide — the floor is the "
                    "widest mark plus 2px, not a column" % _lo["wmin"])
    if _lo["side"] is None or _lo["side"] < 10 - 0.01:
        errs.append("collapsed, the smallest mark is %s px — it has to stay >= 10"
                    % _lo["side"])
    for _st in _range:
        if _st["fade"]:
            errs.append("at panel width %dpx the ladder fades the marks (%s)"
                        % (_st["w"], ",".join(_st["fade"])))
            break
    if _hi["w"] < 500:
        errs.append("opened, the panel reaches only %dpx — too narrow for a "
                    "name column" % _hi["w"])
    # at or just above the floor: the panel is the floor's width rounded UP to
    # a whole pixel, and the fit uses that pixel — never below it
    if _lo["floor"] is None or not (_lo["floor"] - 0.002 <= _lo["thick"] <= _lo["floor"] + 0.03):
        errs.append("collapsed, the marks are at %.3f, the floor is %s"
                    % (_lo["thick"], _lo["floor"]))
    if _hi["thick"] < 0.98:
        errs.append("opened, the marks are only at %.2f of full size" % _hi["thick"])
    # …and the shrink is CONTINUOUS: every step in must be smaller than the one
    # before it. A cliff passes both end checks and is still the wrong shape.
    for _i in range(1, len(_range)):
        if _range[_i]["thick"] <= _range[_i - 1]["thick"]:
            errs.append("the marks do not shrink between %d%% and %d%% "
                        "(%.3f -> %.3f)"
                        % (_i * 0, _i, _range[_i - 1]["thick"], _range[_i]["thick"]))
            break
    if _hi["lab"] < 150 or not _hi["names"]:
        errs.append("opened, there is no name column (%spx, names=%s)"
                    % (_hi["lab"], _hi["names"]))
    if _lo["names"]:
        errs.append("collapsed, the names are still on")
    for _st in _range:
        if _st["overlaps"]:
            errs.append("%d marks overlap at panel width %dpx"
                        % (_st["overlaps"], _st["w"]))
            break
        # 2026-09-30 (E10) — until E10: "the lane is the panel's middle".
        # Since E9.1 the cursor stands inside the panel at its right edge and
        # applyGui reserves its room (14·K); the lane is the middle of what is
        # left, so the marks stand centred in the free part of the panel.
        # …or, with the names on and the pips short of room, E7.1's place:
        # the lane moved left until the pips fit (±1 px)
        _pl = _st.get("pipLane")
        if abs(_st["off"]) > 2 and not (_st["off"] < 0 and _st["names"] and _pl is not None
                                        and abs(_st["axis"] - _pl) <= 1):
            errs.append("the lane is %dpx off the middle of the panel left of the cursor at width %dpx"
                        % (_st["off"], _st["w"]))
            break
    # the names themselves, and the per-chapter tally under them
    pg.evaluate("(p) => { if (window.__nbSetGui) window.__nbSetGui(p); }", 100)
    pg.wait_for_timeout(320)
    _names = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var ch = h.querySelector('.nbmap-node.chap');
        var lab = ch && ch.querySelector('.nbmap-lab');
        var pip = ch && ch.querySelector('.nbchapstat');
        var task = h.querySelector('.nbmap-node.task .nbtasklab');
        var code = h.querySelector('.nbmap-node.codetask .nbmap-lab');
        return {chap: lab ? (lab.textContent || '').trim() : null,
                chapShown: !!(lab && lab.getBoundingClientRect().width > 2),
                align: lab ? getComputedStyle(lab).textAlign : null,
                // K2.8 (28b) — the column's middle, in the node's coordinates,
                // and where it should be: half way from the cursor's end (35)
                // to the lane (--nbvert-axis)
                colMid: lab ? parseFloat(getComputedStyle(lab).left) + lab.getBoundingClientRect().width / 2 : null,
                axis: parseFloat(getComputedStyle(h).getPropertyValue('--nbvert-axis')) || null,
                K: window.__nbK || 1,
                task: task ? (task.textContent || '').trim() : null,
                code: code ? (code.textContent || '').trim() : null,
                pips: pip ? pip.querySelectorAll('.ps').length : 0,
                pipShown: pip ? getComputedStyle(pip).display !== 'none' : false};
    }""")
    print("the names:", _names)
    import re as _reN
    # 2026-09-28b (K2.8) — the names are "Chapter 1: Why complex numbers?",
    # "Exercise 1: …", "Coding 1: roots_of()", and they stand in the MIDDLE
    # between the cursor and the lane. Until 28a this asserted the rule the
    # user replaced: 'Chapter N' alone, right-aligned against the lane.
    if not _names["chapShown"] or not _reN.match(r"^Chapter \d+: .+", _names["chap"] or ""):
        errs.append("a chapter's name is not 'Chapter N: title' (%r, shown=%s)"
                    % (_names["chap"], _names["chapShown"]))
    if _names["align"] != "center":
        errs.append("the names are not centred in their column (%s)" % _names["align"])
    # 2026-09-30 (E10) — until E10: half way from the cursor's end (35) to
    # the lane. E9.1 moved the cursor to the panel's RIGHT edge; the column
    # now starts at the panel's left margin, 5 + 8·K (applyGui `_crN`), and
    # its middle is half way from there to the lane.
    _lm = None if _names["axis"] is None else 5 + round(8 * float(_names["K"]))
    if _names["colMid"] is None or _names["axis"] is None or \
       abs(_names["colMid"] - (_lm + _names["axis"]) / 2) > 1:
        errs.append("the name column's middle is %s, half way from the left margin (%s) "
                    "to the lane (%s) is %s" % (_names["colMid"], _lm, _names["axis"],
                    None if _names["axis"] is None else (_lm + _names["axis"]) / 2))
    if _names["task"] and not _reN.match(r"^Exercise \d+: .+", _names["task"]):
        errs.append("an exercise's name is not 'Exercise N: name' (%r)" % _names["task"])
    if _names["code"] and not _reN.match(r"^Coding \d+: \w+\(\)$", _names["code"]):
        errs.append("a coding exercise's name is not 'Coding N: function()' (%r)" % _names["code"])
    if _names["pips"] != 2 or not _names["pipShown"]:
        errs.append("a chapter carries %d tally pips, wanted 2 (shown=%s)"
                    % (_names["pips"], _names["pipShown"]))
    # the name the reader is ON lights up with the marker, and the others do not
    _lit = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root');
        var n = h.querySelector('.nbmap-node.here');
        if (!n) { n = h.querySelector('.nbmap-node.chap'); n.classList.add('here'); }
        var l = n.querySelector('.nbmap-lab') || n.querySelector('.nbtasklab');
        var o = h.querySelector('.nbmap-node:not(.here) .nbmap-lab');
        if (!l) return null;
        var cs = getComputedStyle(l);
        return {lit: cs.color, shadow: cs.textShadow,
                weight: cs.fontWeight,
                plain: o ? getComputedStyle(o).color : null,
                mark: getComputedStyle(document.body)
                        .getPropertyValue('--nbmark').trim()};
    }""")
    print("the lit name:", _lit)
    if not _lit:
        errs.append("no name to light up")
    else:
        if _lit["plain"] and _lit["lit"] == _lit["plain"]:
            errs.append("the name under the marker is the same ink as the rest (%s)"
                        % _lit["lit"])
        if "none" in (_lit["shadow"] or "none"):
            errs.append("the name under the marker does not light up (no glow)")
    # 2026-09-28c (K4) — the grip pulls the panel out to HALF the notebook,
    # and past the standard width (560) everything on it grows with it; the
    # names break into a second line instead of an ellipsis (K3.1a).
    _K4 = """() => { var h = document.getElementById('nbpanel-root');
        var d = h.querySelector('.nbmap-node.chap .nbchapdot'), l = h.querySelector('.nbmap-node.chap .nbmap-lab');
        var cs = l ? getComputedStyle(l) : null;
        return {W: window.__nbW, half: window.__nbWhalf, k: window.__nbK,
                vw: parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nbvert-w')),
                nbk: parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nbk')),
                dot: d ? d.getBoundingClientRect().width : null,
                font: cs ? parseFloat(cs.fontSize) : null,
                clamp: cs ? cs.webkitLineClamp : null, ws: cs ? cs.whiteSpace : null}; }"""
    pg.evaluate("(p) => { if (window.__nbSetGui) window.__nbSetGui(p); }", 100); pg.wait_for_timeout(320)
    _k4a = pg.evaluate(_K4)
    pg.evaluate("(p) => { if (window.__nbSetGui) window.__nbSetGui(p); }", 99999); pg.wait_for_timeout(320)
    _k4b = pg.evaluate(_K4)
    pg.evaluate("(p) => { if (window.__nbSetGui) window.__nbSetGui(p); }", 100); pg.wait_for_timeout(320)
    _k4c = pg.evaluate(_K4)
    print("K4 panel out to half the notebook:", {"std": _k4a, "max": _k4b, "back": _k4c})
    if not _k4b["half"] or abs(_k4b["vw"] - _k4b["half"]) > 2:
        errs.append("K4: at the far end the panel is %s px, half the notebook is %s" % (_k4b["vw"], _k4b["half"]))
    _kk = max(1.0, min(3.0, (_k4b["vw"] or 0) / 560.0))
    if abs((_k4b["nbk"] or 0) - _kk) > 0.01:
        errs.append("K4: --nbk is %s at %s px, want %.3f" % (_k4b["nbk"], _k4b["vw"], _kk))
    if _k4a["dot"] and _k4b["dot"] and abs(_k4b["dot"] / _k4a["dot"] - _kk) > 0.05 * _kk:
        errs.append("K4: a chapter mark grew x%.3f, the panel x%.3f" % (_k4b["dot"] / _k4a["dot"], _kk))
    if _k4a["font"] and _k4b["font"] and abs(_k4b["font"] / _k4a["font"] - _kk) > 0.05 * _kk:
        errs.append("K4: a chapter name grew x%.3f, the panel x%.3f" % (_k4b["font"] / _k4a["font"], _kk))
    if _k4c != _k4a:
        errs.append("K4: back at the standard width, not what it was (%s != %s)" % (_k4c, _k4a))
    if _k4a["clamp"] != "2" or _k4a["ws"] != "normal":
        errs.append("K3.1a: a name does not break into a second line (line-clamp %s, white-space %s)" % (_k4a["clamp"], _k4a["ws"]))
    pg.evaluate("(p) => { if (window.__nbSetGui) window.__nbSetGui(p); }", 0)
    pg.wait_for_timeout(260)

    # the cursor checks below were written inside the `thick.get("skipped")`
    # branch; the block above splits it, so the same condition re-opens it.
    # (That they only run in that branch is odd and older than this change —
    # noted, not touched, because changing it here would mix two things.)
    if thick.get("skipped"):
        # 2026-09-24bg — THE CURSOR BESIDE THE LANE.
        # A handle for the reading marker, level with it, clear of the marks and
        # — the part that took two goes — actually hit-testable: drawn as a bare
        # CSS triangle it was a zero-size box, and elementFromPoint at its own
        # centre returned the lane behind it, so a real mouse went through it.
        # the marker has to be somewhere in the middle of the rail, or the
        # cursor is legitimately hidden (it never points at nothing)
        pg.evaluate("""() => {
            let sc = null;
            ['.jp-WindowedPanel-outer','.jp-Notebook','#nb1'].forEach(function(s){
              const e = document.querySelector(s);
              if (!sc && e && e.scrollHeight - e.clientHeight > 40) sc = e; });
            if (sc) sc.scrollTop = Math.round((sc.scrollHeight - sc.clientHeight) * 0.4);
        }""")
        pg.wait_for_timeout(900)
        cur = pg.evaluate("""() => {
            const h = document.getElementById('nbpanel-root');
            const c = h.querySelector('.nbmap-cursor'), m = h.querySelector('.nbmap-here');
            if (!c || !m) return {missing: true};
            const cr = c.getBoundingClientRect(), mr = m.getBoundingClientRect();
            const cs = getComputedStyle(c);
            const x = Math.round(cr.left + cr.width/2), y = Math.round(cr.top + cr.height/2);
            // only the marks on the cursor's OWN line can overlap it; one
            // three hundred pixels up the rail says nothing about clearance
            // NOT .nbsect: a section bar spans the whole panel by design, so
            // the bar beside the lane is always "over" one. The marks that can
            // really collide with it are the ones ON the lane (2026-09-25).
            const marks = h.querySelectorAll('.nbmap-node .nbrail-dot,'
                        + '.nbmap-node .nbcodemark, .nbmap-node .nbvizmark,'
                        + '.nbmap-node .nbchapdot, .nbmap-node .nbsubdot');
            let nearest = 1e9;
            marks.forEach(function(d){ const r = d.getBoundingClientRect();
              if (!(r.width > 0)) return;
              if (Math.abs((r.top + r.height/2) - y) > 26) return;
              nearest = Math.min(nearest, r.left - cr.right); });
            return {level: Math.round((cr.top+cr.height/2) - (mr.top+mr.height/2)),
                    leftOfLane: Math.round(mr.left - cr.right),
                    clear: nearest === 1e9 ? null : Math.round(nearest),
                    hit: (document.elementFromPoint(x, y) || {}).className || '',
                    w: Math.round(cr.width), h: Math.round(cr.height),
                    cursor: cs.cursor, vis: cs.visibility};
        }""")
        print("the cursor beside the lane:", cur)
        if cur.get("missing"):
            errs.append("the marker has no cursor beside the lane")
        else:
            # 2026-09-24bi — the bar follows the TRUE reading position while
            # the marker snaps to the nearest mark, so they are level only when
            # the reader is standing on one. The slip is clamped to 90px.
            # 2026-10-01 (E12.3) — THIS BEHAUPTETE BISHER "the cursor is level
            # with the marker". The cursor is a plain scroll bar's thumb now
            # (left, between the tools); the reading height is grip + marker +
            # .nbreadfix. Its place is checked under "the reading line".
            pass
            # A HANDLE HAS TO HAVE A BOX. This is the regression that cost a
            # build: drawn as a bare CSS triangle the cursor was a zero-size
            # element with borders, and the pointer went straight through it.
            # Geometry-independent, so it holds in the mock as well as in a
            # real notebook.
            if cur["w"] < 8 or cur["h"] < 8:
                errs.append("the cursor has no box to grab (%dx%d)"
                            % (cur["w"], cur["h"]))
            if cur["cursor"] not in ("grab", "grabbing"):
                errs.append("the cursor does not offer a drag (%s)" % cur["cursor"])
            if cur["vis"] == "hidden":
                # it hides itself when the marker is off the visible rail, which
                # this mock's geometry can produce; the checks below need it on
                print("   (the cursor is parked off the rail in this mock)")
            else:
                if "nbmap-cursor" not in (cur["hit"] or ""):
                    errs.append("the cursor cannot be hit by a pointer (%r is on top)"
                                % cur["hit"])
                if cur["clear"] is not None and cur["clear"] < -2:
                    errs.append("the cursor overlaps a mark by %dpx" % -cur["clear"])
            # and it drags the document
            drag = pg.evaluate("""async () => {
                const c = document.querySelector('#nbpanel-root .nbmap-cursor');
                const r = c.getBoundingClientRect();
                let sc = null;
                ['.jp-WindowedPanel-outer','.jp-Notebook','#nb1'].forEach(function(s){
                  const e = document.querySelector(s);
                  if (!sc && e && e.scrollHeight - e.clientHeight > 40) sc = e; });
                if (!sc) return {skipped: true};
                const x = Math.round(r.left + r.width/2), y = Math.round(r.top + r.height/2);
                const before = Math.round(sc.scrollTop);
                const mk = (t, cy) => new PointerEvent(t, {clientX:x, clientY:cy,
                     bubbles:true, cancelable:true, button:0, pointerId:1, isPrimary:true});
                c.dispatchEvent(mk('pointerdown', y));
                for (let i=1;i<=8;i++) c.dispatchEvent(mk('pointermove', y + 130*i/8));
                await new Promise(z => setTimeout(z, 260));
                c.dispatchEvent(mk('pointerup', y + 130));
                await new Promise(z => setTimeout(z, 320));
                return {before: before, after: Math.round(sc.scrollTop)};
            }""")
            print("   dragging it:", drag)
            if not drag.get("skipped") and drag["after"] - drag["before"] < 30:
                errs.append("dragging the cursor moved the document by %d px"
                            % (drag["after"] - drag["before"]))

        # 2026-09-24bg — THE MARKER DOES NOT PUT THE LIGHT OUT.
        # The marks carry a background TRANSITION, so a colour read in the same
        # tick as the class change is the one it is coming FROM — that trap cost
        # three probes. The class is held on for longer than the transition,
        # against the panel's own sweep, and read at the end.
        rings = pg.evaluate("""async () => {
            const h = document.getElementById('nbpanel-root');
            const n = h.querySelector('.nbmap-node.is-current');
            const cm = h.querySelector('.nbcodemark.cd-current');
            const pn = cm && cm.closest('.nbmap-node');
            if (!n && !cm) return {skipped: true};
            const t = setInterval(function(){ if (n) n.classList.add('here');
                                              if (pn) pn.classList.add('here'); }, 30);
            await new Promise(r => setTimeout(r, 700));
            const d = n && n.querySelector('.nbrail-dot');
            const gs = d ? getComputedStyle(d) : null, ps = cm ? getComputedStyle(cm) : null;
            const out = {mark: gs ? gs.getPropertyValue('--nbmark').trim() : null,
                         greenFill: gs && gs.backgroundColor,
                         greenRing: gs && gs.borderTopColor,
                         purpleFill: ps && ps.backgroundColor,
                         purpleRing: ps && ps.borderTopColor};
            clearInterval(t);
            if (n) n.classList.remove('here'); if (pn) pn.classList.remove('here');
            return out;
        }""")
        print("the marker over the open doors:", rings)
        if not rings.get("skipped"):
            def _rgb(v):
                import re as _re
                m = _re.findall(r"\\d+", v or "")
                return tuple(int(x) for x in m[:3]) if len(m) >= 3 else None
            for _name, _fill, _ring in (("green", rings["greenFill"], rings["greenRing"]),
                                        ("purple", rings["purpleFill"], rings["purpleRing"])):
                if _fill is None:
                    continue
                f, r = _rgb(_fill), _rgb(_ring)
                if f and r and max(abs(f[i] - r[i]) for i in range(3)) < 40:
                    errs.append("under the marker the %s mark's ring is the same "
                                "colour as its fill (%s / %s)" % (_name, _fill, _ring))
                if r and max(r) - min(r) < 25:
                    errs.append("under the marker the %s mark lost its colour (%s)"
                                % (_name, _ring))

        # the "click to add cell" strip stops at the panel
        foot = pg.evaluate("""() => {
            const f = document.querySelector('.jp-Notebook-footer')
                   || document.querySelector('.jp-WindowedPanel-footer');
            const rail = document.querySelector('#nbpanel-root .nbrail');
            if (!f || !rail) return {skipped: true};
            const fr = f.getBoundingClientRect(), rr = rail.getBoundingClientRect();
            if (!(fr.width > 10)) return {skipped: true};
            return {over: Math.round(fr.right - rr.left), w: Math.round(fr.width)};
        }""")
        print("the add-cell strip:", foot)
        if not foot.get("skipped") and foot["over"] > 0:
            errs.append("the add-cell strip runs %dpx under the timeline" % foot["over"])
        pg.evaluate("() => { try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','h'); }"
                    " catch(e){} window.__nbrailSync(); }")
        pg.wait_for_timeout(500)
    else:
        print("thickness and the detail ladder:")
        for _s in thick.get("steps", []):
            print("   %3d%%  width %4d  height %3d  thick %-5s  gone: %s"
                  % (_s["pct"], _s["w"], _s["h"], _s["thick"], ",".join(_s["off"]) or "—"))
        _w = [x["w"] for x in thick.get("steps", [])] or [0]
        _h = [x["h"] for x in thick.get("steps", [])] or [0]
        if max(_w) - min(_w) > 4:
            errs.append("horizontal: the panel width changes with the control (%s)" % _w)
        if abs(_w[0] - thick["nbw"]) > 30:
            errs.append("horizontal: the panel is not the document's width (%d vs %d)"
                        % (_w[0], thick["nbw"]))
        if not all(_h[i] >= _h[i + 1] for i in range(len(_h) - 1)) or _h[0] - _h[-1] < 20:
            errs.append("horizontal: the panel does not get thinner (%s)" % _h)
        _LADDER = [("det-text", .85), ("det-emoji", .70), ("det-circle", .58),
                   ("det-bar", .46), ("det-dot", .36)]
        for _i, _s in enumerate(thick["steps"]):
            _t = float(_s["thick"] or 1)
            _want_i = [c for c, thr in _LADDER if _t < thr]
            if _s["off"] != _want_i:
                errs.append("at %d%% the detail ladder is %s, wanted %s"
                            % (_s["pct"], _s["off"], _want_i))
                break
    if back["vert"]:
        errs.append("the ⇅ button does not turn the panel back")
    if back["padR"] not in ("", "0px"):
        errs.append("horizontal still reserves room beside the document (%s)" % back["padR"])
    if not back["padT"]:
        errs.append("horizontal reserves no strip above the document")
    if back["nodeTop"]:
        errs.append("a node kept its vertical position (%s)" % back["nodeTop"])
    if back["h"]:
        errs.append("the panel kept its vertical height (%s)" % back["h"])

    # ------------------------------------------------------------------
    # 2026-09-25h — THE KEYBOARD MODE. Alt+. puts the focus on the panel host;
    # while it is there the panel's keys act and NOTHING reaches the document
    # (a listener on the document is the stand-in for JupyterLab's own). Keys
    # with a modifier pass. Esc goes back to where the focus came from.
    kb = pg.evaluate("""() => {
        var out = {}, h = document.getElementById('nbpanel-root');
        var K = window.__nbKeys || [], M = window.__nbKbdMap || {};
        out.undocumented = Object.keys(M).filter(function(k){
            return !K.some(function(r){ return r.key === k && r.a === M[k]; }); });
        out.unbound = K.filter(function(r){ return r.a && r.key !== '#' && M[r.key] !== r.a; })
                       .map(function(r){ return r.k; });
        var rows = window.__nbKeyRows ? window.__nbKeyRows() : '';
        out.unlisted = K.filter(function(r){ return rows.indexOf('<kbd>' + r.k + '</kbd>') < 0; })
                        .map(function(r){ return r.k; });
        window.__reached = [];
        document.addEventListener('keydown', function(e){ window.__reached.push(e.key); }, false);
        var inp = document.createElement('input'); inp.id = '__kbdprobe';
        document.querySelector('.jp-Notebook').appendChild(inp);
        inp.focus();
        out.start = document.activeElement === inp;
        return out; }""")
    pg.keyboard.press("Alt+Period"); pg.wait_for_timeout(80)
    kb["entered"] = pg.evaluate("() => { var h = document.getElementById('nbpanel-root'); "
                                "return {focus: document.activeElement === h, cls: h.classList.contains('nbkbd')}; }")
    kb["theme0"] = pg.evaluate("() => { window.__reached = []; try { return window.__nbStore.get('digichemjn.theme.v1'); } catch(e) { return 'X'; } }")
    for key in ["j", "j", "d", "x", "Space", "1"]:
        pg.keyboard.press(key); pg.wait_for_timeout(120)
    kb["after"] = pg.evaluate("""() => ({
        at: window.__nbKeyAt, reached: window.__reached.slice(),
        focus: document.activeElement === document.getElementById('nbpanel-root'),
        chap: (function(){ var c = document.querySelector('#nbpanel-root .nbmap-node.chap');
                 return !!(c && c.classList.contains('nbsel')); })(),
        theme: (function(){ try { return window.__nbStore.get('digichemjn.theme.v1'); } catch(e) { return 'X'; } })() })""")
    # 2026-09-27e — the arrows are J and K in the mode (C2)
    pg.keyboard.press("ArrowDown"); pg.wait_for_timeout(120)
    kb["a0"] = pg.evaluate("() => window.__nbKeyAt")
    pg.keyboard.press("ArrowDown"); pg.wait_for_timeout(120)
    kb["a1"] = pg.evaluate("() => window.__nbKeyAt")
    pg.keyboard.press("ArrowUp"); pg.wait_for_timeout(120)
    kb["a2"] = pg.evaluate("() => ({at: window.__nbKeyAt, reached: window.__reached.slice()})")
    pg.keyboard.press("Shift+Slash"); pg.wait_for_timeout(120)
    # R3 · 19 (C): ? opens the help WINDOW (it opened the ⌨ drawer page until
    # v1.21); it lists every key of the one table, and ? again closes it
    kb["help"] = pg.evaluate("() => { var w = document.querySelector('.nbhelp.on'); if (!w) return false; "
                             "var n = w.querySelectorAll('.nbhelp-keys kbd').length; "
                             "return n >= (window.__nbKeys || []).length; }")
    pg.keyboard.press("Shift+Slash"); pg.wait_for_timeout(120)
    kb["helpShut"] = pg.evaluate("() => !document.querySelector('.nbhelp.on')")
    pg.keyboard.press("Control+Shift+KeyY"); pg.wait_for_timeout(80)
    kb["modpass"] = pg.evaluate("() => window.__reached.indexOf('Y') > -1 || window.__reached.indexOf('y') > -1")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(80)
    kb["left"] = pg.evaluate("() => ({back: document.activeElement && document.activeElement.id === '__kbdprobe', "
                             "cls: document.getElementById('nbpanel-root').classList.contains('nbkbd')})")
    pg.keyboard.press("j"); pg.wait_for_timeout(60)
    kb["typing"] = pg.evaluate("() => document.getElementById('__kbdprobe').value")
    print("keyboard mode:", kb)
    for f in ("undocumented", "unbound", "unlisted"):
        if kb[f]: errs.append("keyboard: %s keys %s — the table and the handler disagree" % (f, kb[f]))
    if not kb["start"]: errs.append("keyboard: the probe field could not take the focus")
    if not (kb["entered"]["focus"] and kb["entered"]["cls"]):
        errs.append("keyboard: Alt+. did not put the focus on the panel (%s)" % kb["entered"])
    if kb["after"]["reached"]:
        errs.append("keyboard: keys leaked to the document in the mode: %s" % kb["after"]["reached"])
    if not kb["after"]["focus"]: errs.append("keyboard: the mode lost the focus while keys were pressed")
    if kb["after"]["theme"] == kb["theme0"]: errs.append("keyboard: D did not switch light/dark")
    if not kb["after"]["chap"]: errs.append("keyboard: 1 did not land on a chapter mark")
    if not kb["help"]: errs.append("keyboard: ? did not open the help window with every key")
    if not kb.get("helpShut"): errs.append("keyboard: ? again did not close the help window")
    if not kb["modpass"]: errs.append("keyboard: a key WITH a modifier was swallowed — JupyterLab's globals must pass")
    if not kb["left"]["back"] or kb["left"]["cls"]:
        errs.append("keyboard: Esc did not give the focus back to the field (%s)" % kb["left"])
    if kb["typing"] != "j": errs.append("keyboard: after Esc, typing does not type (%r)" % kb["typing"])
    if kb["a0"] is None or kb["a1"] != kb["a0"] + 1 or kb["a2"]["at"] != kb["a0"]:
        errs.append("keyboard: \u2193/\u2191 are not J/K in the mode (%s, %s, %s)" % (kb["a0"], kb["a1"], kb["a2"]))
    if kb["a2"]["reached"]:
        errs.append("keyboard: the arrows leaked to the document in the mode: %s" % kb["a2"]["reached"])

    # 2026-09-27e — F: A RIGHT ANSWER MOVES THE READER ON. The feed carries
    # run:seq:route:key; the panel notes a run it sees for the first time and
    # only moves on a HIGHER number of a run it already knows. The next open
    # place is the next chapter mark after the exercise, if that chapter is
    # open; a locked one means nowhere.
    gt = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root'), out = {};
        out.fn = typeof window.__nbNextOpen === 'function';
        if (!out.fn) return out;
        var feed = document.querySelector('.nbfeed');
        var g = (feed.getAttribute('data-goto') || '').split(':');
        out.attr = g.length >= 4;
        var seen = window.__nbGotoSeen || {};
        out.firstSeen = Object.keys(seen).filter(function(k){ return k.slice(-g[0].length - 1) === '/' + g[0]; })
                          .map(function(k){ return seen[k]; });
        var r = window.__nbNextOpen(h, 'a', 't1');
        out.lockedIsNowhere = !!r.from && r.to === null;
        var ns = [].slice.call(h.querySelectorAll('.nbmap-node')), i = ns.indexOf(r.from), c = null;
        for (var j = i + 1; j < ns.length; j++) if (ns[j].classList.contains('chap')) { c = ns[j]; break; }
        if (c) { c.classList.remove('locked'); out.toChapter = window.__nbNextOpen(h, 'a', 't1').to === c; c.classList.add('locked'); }
        var rc = window.__nbNextOpen(h, 'c', 't1');
        out.codeFrom = !!(rc.from && rc.from.classList.contains('codetask'));
        window.__gtT0 = window.__nbGotoT;
        // every feed on the page (the suite mounts a mirror as well): the one
        // the panel reads is whichever is active
        [].forEach.call(document.querySelectorAll('.nbfeed'), function(f){
            f.setAttribute('data-goto', g[0] + ':' + (parseInt(g[1], 10) + 5) + ':a:t1'); });
        return out; }""")
    pg.wait_for_timeout(1800)          # the sync runs every 1.5 s (and on a DOM change)
    gt["moved"] = pg.evaluate("() => window.__nbGotoT !== window.__gtT0")
    pg.evaluate("""() => { window.__gtT1 = window.__nbGotoT;
        [].forEach.call(document.querySelectorAll('.nbfeed'), function(f){
            f.setAttribute('data-goto', 'newrun:3:a:t1'); }); }""")
    pg.wait_for_timeout(1800)
    gt["newRunQuiet"] = pg.evaluate("() => window.__nbGotoT === window.__gtT1")
    print("move after a right answer:", gt)
    if not gt.get("fn"): errs.append("F: the panel has no __nbNextOpen — a right answer cannot move the reader on")
    else:
        if not gt["attr"]: errs.append("F: the feed carries no data-goto")
        if gt["firstSeen"] != [0]: errs.append("F: the first sight of a run was not noted as seq 0 (%s)" % gt["firstSeen"])
        if not gt["lockedIsNowhere"]: errs.append("F: a locked next chapter should mean no move")
        if not gt.get("toChapter"): errs.append("F: the move does not go to the next open chapter")
        if not gt["codeFrom"]: errs.append("F: the code route does not start from the coding mark")
        if not gt["moved"]: errs.append("F: a higher number in a known run did not schedule a move")
        if not gt["newRunQuiet"]: errs.append("F: a NEW run moved the reader — a run is not an answer")

    # 2026-09-27a — D-b: versions compared as versions, not as strings.
    vk = pg.evaluate("""() => { var k = window.__nbVKey; if (!k) return null;
        return {zbi: k('2026-09-24z') < k('2026-09-24bi'), az: k('2026-09-24a') < k('2026-09-24z'),
                zaa: k('2026-09-24z') < k('2026-09-24aa'), day: k('2026-09-24bi') < k('2026-09-25a'),
                same: k('2026-09-27a') === k('2026-09-27a'), empty: k('') < k('2026-09-24a')}; }""")
    print("version keys:", vk)
    if not vk: errs.append("versions: window.__nbVKey is missing")
    else:
        for _n, _ok in vk.items():
            if not _ok: errs.append("versions: %s compares wrong (24z vs 24bi is the case that broke)" % _n)
    for _m in re.finditer(r"[^\n]*(NBRAIL_VERSION|JUMP_VERSION|best)[^\n]*", js):
        _l = _m.group(0)
        if re.search(r"(<|>)=?\s*(NBRAIL_VERSION|JUMP_VERSION|best)\b|\b(NBRAIL_VERSION|JUMP_VERSION|best)\s*(<|>)", _l) and "vkey(" not in _l:
            errs.append("versions: a raw string compare is left: %s" % _l.strip()[:120])
    # 2026-09-27a — the title guard lets the command palette through (night
    # 26.09., finding 2), and still holds Enter on the title cell itself.
    tg = pg.evaluate("""() => {
        var nb = document.createElement('div'); nb.className = 'jp-Notebook jp-mod-commandMode'; nb.tabIndex = 0;
        var c = document.createElement('div'); c.className = 'jp-Cell jp-MarkdownCell jp-mod-active';
        c.innerHTML = '<div class="nbtitle">nbtitle</div>'; nb.appendChild(c); document.body.appendChild(nb);
        var pal = document.createElement('div'); pal.className = 'jp-ModalCommandPalette';
        var inp = document.createElement('input'); pal.appendChild(inp); document.body.appendChild(pal);
        var fire = function(el){ var e = new KeyboardEvent('keydown', {key: 'Enter', bubbles: true, cancelable: true});
                                 el.dispatchEvent(e); return e.defaultPrevented; };
        var r = {palette: fire(inp), title: null};
        pal.remove();
        r.title = fire(nb);
        nb.remove();
        return r; }""")
    print("title guard:", tg)
    if tg["palette"]: errs.append("title guard: Enter in the command palette was swallowed")
    if not tg["title"]: errs.append("title guard: Enter on the title cell in command mode is no longer held")
    # 2026-09-27a — dark prints light, and comes back dark.
    pr = pg.evaluate("""() => { var bc = document.body.classList, K = 'digichemjn.theme.v1', was = null;
        was = window.__nbStore.get(K); window.__nbStore.set(K, 'dark');   // E25.o: this notebook's key
        window.__nbApplyTheme(); var before = bc.contains('nbdark');
        window.dispatchEvent(new Event('beforeprint')); var inPrint = bc.contains('nbdark');
        try { window.__nbrailSync(); } catch(e) {}            // the tick that used to undo it
        window.__nbApplyTheme(); var afterTick = bc.contains('nbdark');
        window.dispatchEvent(new Event('afterprint')); var after = bc.contains('nbdark');
        if (was === null) window.__nbStore.del(K); else window.__nbStore.set(K, was);
        window.__nbApplyTheme();
        return {before: before, inPrint: inPrint, afterTick: afterTick, after: after}; }""")
    print("print light:", pr)
    if not pr["before"]: errs.append("print: the probe could not make the document dark")
    if pr["inPrint"]: errs.append("print: the dark document stays dark in print")
    if pr["afterTick"]: errs.append("print: a sync tick during the print made the document dark again")
    if not pr["after"]: errs.append("print: after printing the document is not dark again")

    # 2026-09-27c — THE IN-PLACE SYNC KEEPS WHAT IT SYNCS (OBERFLAECHE §3, G1).
    # A state change with the same marks is patched in place. It copied a
    # dot's TEXT, which threw away the <i class="nbdotg"> that turns the sign
    # level inside the turned mark (the tick leaned 45° after the first
    # answer, real Lab), and it never copied the pips under a chapter's name
    # (they stayed 'open'). Feed the panel a new source with t1 solved and t2
    # skipped, same marks, and read the panel.
    if "t1" in G.get("_TASKS", {}).get("state", {}) and "t2" in G["_TASKS"]["state"]:
        G["task_solved"]("t1"); G["task_skipped"]("t2")
        _new = G["_prog_html"]()
        pg.evaluate("(h) => { var o = document.querySelector('.jp-OutputArea'); o.innerHTML = h; }", _new)
        pg.wait_for_timeout(1800)
        try: pg.evaluate("() => { try { window.__nbrailSync(); } catch(e) {} }")
        except Exception: pass
        pg.wait_for_timeout(400)
        ip = pg.evaluate("""() => { var h = document.getElementById('nbpanel-root'); if (!h) return null;
            function dot(k){ var n = h.querySelector('.nbmap-node[data-task="' + k + '"]'); var d = n && n.querySelector('.nbrail-dot');
              return d ? {cls: d.className, g: !!d.querySelector('.nbdotg'), txt: d.textContent} : null; }
            var ch = [].slice.call(h.querySelectorAll('.nbmap-node.chap'));
            var pips = ch.slice(0, 2).map(function(c){ return [].map.call(c.querySelectorAll('.nbchapstat .ps'), function(p){ return p.className; }).join(','); });
            return {t1: dot('t1'), t2: dot('t2'), pips: pips}; }""")
        print("in-place sync:", ip)
        if not ip or not ip["t1"] or not ip["t2"]:
            errs.append("in-place sync: no exercise marks on the panel")
        else:
            if "st-ans" not in ip["t1"]["cls"] or "st-skip" not in ip["t2"]["cls"]:
                errs.append("in-place sync: the state did not reach the marks (%s / %s)" % (ip["t1"]["cls"], ip["t2"]["cls"]))
            if not ip["t1"]["g"] or not ip["t2"]["g"]:
                errs.append("in-place sync: the sign lost its level wrapper (.nbdotg) — it turns with the mark")
            if not ip["pips"] or "done" not in ip["pips"][0] or "skip" not in ip["pips"][1]:
                errs.append("in-place sync: the pips under the chapter names did not follow (%s)" % ip["pips"])

    # ---- 2026-09-27d — THE READING LINE (STRUKTUR §4b) ------------------------
    # Three claims of the Eilauftrag, in the mock: (1) with the markdown cell's
    # hidden title card FIRST in the page, the title mark stands on the middle
    # of the card that is on screen — querySelector alone took the hidden one;
    # (2) the cursor is a fixed point: the same screen line at every scroll,
    # the title mark's opening line; (3) under the add-a-cell strip there is
    # room enough that the furthest scroll brings it onto that line. Until 27c
    # the cursor rode with the snapped marker and nothing asserted where it was.
    # Late in this run __nbrailSync() is not the live instance any more, so the
    # probe waits for the panel's own timer instead of calling it.
    pg.evaluate("""() => {
        try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','v'); } catch(e){}
        var sc = document.querySelector('.jp-Notebook');
        var out0 = sc.querySelector('.jp-OutputArea');
        var hid = document.createElement('div'); hid.className = 'nbtitle-card nbrl-probe';
        hid.style.display = 'none'; hid.textContent = 'hidden copy';
        var vis = document.createElement('div'); vis.className = 'nbtitle-card nbrl-probe nbrl-vis';
        vis.style.cssText = 'height:140px;margin:260px 0 30px;'; vis.textContent = 'Title';
        // as in JupyterLab: the hidden copy lives in a cell of its OWN (the
        // markdown cell, display:none) — not a sibling the anchor walk could
        // step over to the visible card
        var hc = document.createElement('div'); hc.className = 'jp-Cell nbrl-probe'; hc.style.display = 'none';
        hc.appendChild(hid); sc.insertBefore(hc, sc.firstChild);
        out0.insertBefore(vis, out0.firstChild);
        var foot = document.createElement('button'); foot.className = 'jp-Notebook-footer nbrl-probe';
        foot.style.cssText = 'display:block;height:27px;width:100%;'; sc.appendChild(foot);
        sc.scrollTop = 0; }""")
    pg.wait_for_timeout(1800)
    RLM = """() => {
        var sc = document.querySelector('.jp-Notebook');
        var h = document.getElementById('nbpanel-root'), map = h.querySelector('.nbmap');
        var mid = function(e){ if (!e) return null; var r = e.getBoundingClientRect(); return r.top + r.height / 2; };
        var y0 = parseInt(h.dataset.railY0 || '0', 10) || 0, cur = h.querySelector('.nbmap-cursor');
        var air = sc.querySelector(':scope > .nbfoot-air');
        return {vert: document.body.classList.contains('nbvert'), y0: y0,
                line: map.getBoundingClientRect().top + y0, st: sc.scrollTop, max: sc.scrollHeight - sc.clientHeight,
                title: mid(h.querySelector('.nbmap-node.title .nbsect')), card: mid(document.querySelector('.nbrl-vis')),
                cursor: cur ? (parseFloat(cur.style.top) || 0) + (cur.offsetHeight || 14) / 2 : null,
                foot: mid(document.querySelector('.jp-Notebook-footer.nbrl-probe')),
                air: air ? air.getBoundingClientRect().height : null,
                yoc: mid(h.querySelector('.nbmap-node.cell .nbsect')), airx: window.__nbAirX || 0,
                // 27f: the marker that lights the marks, and which mark is lit
                marker: mid(h.querySelector('.nbmap-here')),
                lit: (function(){ var ns = [].slice.call(h.querySelectorAll('.nbmap-node')), L = map.getBoundingClientRect().top + y0,
                        MK = '.nbsect,.nbsubdot,.nbchapdot,.nbvizmark,.nbrail-dot,.nbcodemark', exp = -1, ey = -1e9, lit = [], near = [];
                        ns.forEach(function(n, i){ if (n.classList.contains('nbgone')) return; var m = n.querySelector(MK);
                          if (!m) return; var r = m.getBoundingClientRect(); if (!(r.height > 0)) return; var c = r.top + r.height / 2;
                          if (c <= L + 2 && c >= ey) { ey = c; exp = i; } if (Math.abs(c - L) <= 2) near.push(i);
                          if (n.classList.contains('here')) lit.push(i); });
                        return {lit: lit, expect: exp, near: near}; })()}; }"""
    rl = {"at": []}
    for _f in (0, 0.3, 0.7, 1.0, 1.0):
        pg.evaluate("(f) => { var sc = document.querySelector('.jp-Notebook'); sc.scrollTop = Math.round((sc.scrollHeight - sc.clientHeight) * f); }", _f)
        pg.wait_for_timeout(900)
        rl["at"].append(pg.evaluate(RLM))
    pg.evaluate("""() => { document.querySelectorAll('.nbrl-probe, .nbfoot-air').forEach(function(e){ e.remove(); });
        try { localStorage.setItem(window.__nbOKey ? window.__nbOKey() : 'digichemjn.orient.v1','h'); } catch(e){}
        document.querySelector('.jp-Notebook').scrollTop = 0; }""")
    pg.wait_for_timeout(900)
    _r0, _rN = rl["at"][0], rl["at"][-1]
    rl.update({"y0": _r0["y0"], "line": _r0["line"], "title": _r0["title"], "card": _r0["card"],
               "cursors": [a["cursor"] for a in rl["at"]], "foot": _rN["foot"], "lineEnd": _rN["line"],
               "air": _rN["air"], "vert": _r0["vert"], "yoc": _rN["yoc"], "airx": _rN["airx"]})
    print("the reading line:", {k: v for k, v in rl.items() if k != "at"})
    if not rl["vert"] or rl["y0"] <= 0:
        errs.append("reading line: the rail did not come up vertical (vert %r, railY0 %r)" % (rl["vert"], rl["y0"]))
    if abs(rl["title"] - rl["card"]) > 1:
        errs.append("reading line: the title mark stands at %.1f, the visible card's middle at %.1f"
                    " (the hidden copy was measured)" % (rl["title"], rl["card"]))
    # 2026-10-01 (E12.3) — THIS BEHAUPTETE BISHER (27d/E9.1) "the cursor is a
    # fixed point on the title mark's line". It is a plain scroll bar's thumb
    # now: it moves down with the scroll (0 → 0.3 → 0.7 → 1), and not at all
    # once the end is reached.
    _c = rl["cursors"]
    if not (_c[0] < _c[1] < _c[2] < _c[3]) or abs(_c[3] - _c[4]) > 1:
        errs.append("reading line: the scroll bar's thumb does not run down with the scroll (%s)"
                    % ["%.1f" % c for c in _c])
    # 2026-09-27f — THE MARKER RUNS ON THE LINE (Eilauftrag 2). Until 27e it
    # snapped to the nearest mark and nothing here said where it stood; the
    # lit mark (.here) is now the last one whose middle reached the line.
    for _a in rl["at"]:
        if _a["marker"] is None or abs(_a["marker"] - _a["line"]) > 2:
            errs.append("reading line: at scroll %d the marker is at %s, the line at %.1f — it does not run on the line"
                        % (_a["st"], _a["marker"], _a["line"])); break
    # 2026-09-30 (E10) — E9.2: at scroll 0 the page stands in the air ABOVE
    # the title; no mark has reached the line and nothing is lit. Until E10
    # this demanded one lit mark everywhere and read "expect -1" as a mark.
    for _a in rl["at"]:
        _l = _a["lit"]
        if _l["expect"] == -1 and not _l["near"]:
            if _l["lit"]:
                errs.append("reading line: at scroll %d (air above the title) %s is lit" % (_a["st"], _l["lit"])); break
            continue
        if not (_l["lit"] == [_l["expect"]] or (len(_l["lit"]) == 1 and _l["lit"][0] in _l["near"])):
            errs.append("reading line: at scroll %d the lit mark is %s, the last mark that reached the line is %s"
                        % (_a["st"], _l["lit"], _l["expect"])); break
    # 2026-09-30 (E10) — until E10: at the furthest scroll the add-a-cell
    # strip stands ON the line. E8.6 ended the range on the "Your own cell"
    # mark, E9.2 added the same air as above the title (AIRX, __nbAirX) past
    # it: at the end the YOC mark stands AIRX above the line, the strip above
    # the line too.
    if rl["air"] is None or rl["yoc"] is None or abs(rl["lineEnd"] - rl["yoc"] - rl["airx"]) > 1 \
       or rl["foot"] > rl["lineEnd"] + 1:
        errs.append("reading line: at the end the YOC mark is at %s, the strip at %.1f, the line at %.1f,"
                    " air past it %s (room under it: %s)" % (rl["yoc"], rl["foot"], rl["lineEnd"], rl["airx"], rl["air"]))

    # ---- 2026-10-02 (E19.4) — WHERE ARE WE ------------------------------------
    # one stand-in page per front end; the answer and the class of interface
    env = pg.evaluate("""() => {
        var E = window.__nbEnv, out = {here: E ? E() : null, cases: {}};
        if (!E) return out;
        var C = {
          lab:    {cfg: {appName: 'JupyterLab'}, host: '127.0.0.1', path: '/lab/tree/x.ipynb', proto: 'http:', ua: 'Chrome', body: ''},
          nb7:    {cfg: {appName: 'Jupyter Notebook'}, host: 'localhost', path: '/notebooks/x.ipynb', proto: 'http:', ua: 'Chrome', body: ''},
          lite:   {cfg: {appName: 'JupyterLite'}, lite: true, host: 'example.org', path: '/lab/index.html', proto: 'https:', ua: 'Chrome', body: ''},
          binder: {cfg: {appName: 'JupyterLab', hubPrefix: '/hub/'}, host: 'hub.2i2c.mybinder.org', path: '/user/x-y/lab', proto: 'https:', ua: 'Chrome', body: ''},
          hub:    {cfg: {appName: 'JupyterLab', hubPrefix: '/hub/', hubUser: 'u'}, host: 'jupyter.uni-freiburg.de', path: '/user/u/lab', proto: 'https:', ua: 'Chrome', body: ''},
          colab:  {cfg: {}, host: 'abc-0-colab.googleusercontent.com', path: '/outputframe.html', proto: 'https:', ua: 'Chrome', body: ''},
          vscode: {cfg: {}, host: 'x', path: '/index.html', proto: 'vscode-webview:', ua: 'Chrome Code', body: 'vscode-light'},
          pycharm:{cfg: {}, host: 'localhost', path: '/', proto: 'http:', ua: 'Mozilla/5.0 JetBrains JCEF', body: ''},
          page:   {cfg: {}, host: 'nbviewer.org', path: '/x', proto: 'https:', ua: 'Chrome', body: ''},
          // the kernel's word (py-E19.4 data-nbenv) wins for what the page cannot see
          colab_k:{cfg: {appName: 'JupyterLab'}, host: 'localhost', path: '/lab', proto: 'http:', ua: 'Chrome', body: '', kernel: 'colab'},
          lab_k:  {cfg: {appName: 'JupyterLab'}, host: 'localhost', path: '/lab', proto: 'http:', ua: 'Chrome', body: '', kernel: 'server'}};
        for (var k in C) out.cases[k] = E(C[k]);
        out.attr = [document.documentElement.getAttribute('data-nbenv'), document.documentElement.getAttribute('data-nbui')];
        out.path = window.__nbRunPath ? window.__nbRunPath() : null;
        return out; }""")
    print("E19.4 environments:", env)
    _ui = {"lab": "lab", "nb7": "lab", "lite": "lab", "binder": "lab", "hub": "lab",
           "colab": "frame", "vscode": "frame", "pycharm": "frame", "page": "page",
           "colab_k": "frame", "lab_k": "lab"}
    if not env["here"]:
        errs.append("E19.4: no window.__nbEnv on the page")
    else:
        for _k, _u in _ui.items():
            _got = (env["cases"] or {}).get(_k) or {}
            if _got.get("env") != _k.split("_")[0] or _got.get("ui") != _u:
                errs.append("E19.4: the %s page reads as %s" % (_k, _got))
        if not env["attr"][0] or env["attr"][0] != env["here"].get("env"):
            errs.append("E19.4: <html data-nbenv> is %s, the reading %s" % (env["attr"], env["here"]))

    # ---- 2026-09-28b — K2.7 and K2.1 --------------------------------------
    # K2.7: 📚 is there for a READER (25f hid it unless the role was
    # "administrator"), and the page a tile opens shows its own cells only
    # (the drawer's four page rules had lost their display:none and every
    # tile opened the whole drawer).
    # K2.1: full screen gives a box no other width (the body.nbfs rules made
    # the key message 850 → 1466 px at 1920).
    # 2026-10-02 (E17.2, with css-E17.2) — K2.7 BEHAUPTETE BISHER "📚 for every
    # reader, and every page shows only its own cells" (K2, 28b). E17.2 folds
    # 📚 into the one 👤 window: the 📚 sign is gone from the corner, and the
    # page `code` (👤) shows the account, the old progress code, the settings
    # and the progress — `pg-acct|pg-code|pg-set|pg-stats`, at least `pg-code`
    # and `pg-stats`; `stats`, `diff` and `keys` show only their own. Apply
    # together with PATCH-css-E17.2(-df74628b).
    k2 = pg.evaluate("""() => {
        var h = document.getElementById('nbpanel-root'); var out = {};
        try { window.__nbStore.del('digichemjn.role.v1'); } catch (e) {}
        if (window.__nbApplyRole) window.__nbApplyRole();
        var b = h.querySelector('.nbdock .nbseries');
        out.admin = document.body.classList.contains('nbadmin');
        out.btn = b ? getComputedStyle(b).display : null;
        var was = [h.dataset.page, h.classList.contains('open')];
        out.pages = {};
        ['stats', 'diff', 'code', 'keys'].forEach(function(pgn){
          h.dataset.page = pgn; h.classList.add('open');
          out.pages[pgn] = [].filter.call(h.querySelectorAll('.nbdrawer .nbcell'), function(c){
              return getComputedStyle(c).display !== 'none'; }).map(function(c){
              return (c.className.match(/pg-\w+/) || ['?'])[0]; });
        });
        if (was[0]) h.dataset.page = was[0]; else delete h.dataset.page;
        h.classList.toggle('open', was[1]);
        var nb = document.querySelector('.jp-Notebook');
        var box = document.createElement('div'); box.className = 'acc-practice';
        box.innerHTML = '<div class="nbbox nbbox-ex" style="width:100%">x</div>'
                      + '<div class="nbbox nbbox-concept">y</div>';
        nb.insertBefore(box, nb.firstChild);
        var wd = function(){ return [].map.call(box.querySelectorAll('.nbbox'), function(e){ return Math.round(e.getBoundingClientRect().width); }); };
        out.normal = wd(); document.body.classList.add('nbfs'); out.full = wd();
        document.body.classList.remove('nbfs'); box.remove();
        return out; }""")
    print("K2.7 / K2.1:", k2)
    if k2["admin"] or k2["btn"] not in (None, "none"):
        errs.append("K2.7 (E17.2): the 📚 sign is still in the corner (display %s)" % k2["btn"])
    # rebase 04.10. (css-E17.2-df74628b): only the page `code` (👤) gathers
    # account, old code, settings and progress; `stats` (old calls — 📚 opens
    # 👤 now) shows only its own again, like `diff` and `keys`
    for _pn, _cells in k2["pages"].items():
        if _pn == "code":
            if (not set(_cells) <= {"pg-acct", "pg-code", "pg-set", "pg-stats"}
                    or not {"pg-code", "pg-stats"} <= set(_cells)):
                errs.append("K2.7 (E17.2): the page %r shows %s" % (_pn, _cells))
        # hw-E25.int (08.10.): the page `diff` (⚙) also shows the feedback cell
        # `pg-fb` of py-E25.n/css-E25.n (behauptete bisher: `diff` shows only
        # pg-diff); every other page still shows only its own
        elif not _cells or any(c != "pg-" + _pn and not (_pn == "diff" and c == "pg-fb") for c in _cells) \
                or (_pn == "diff" and "pg-diff" not in _cells):
            errs.append("K2.7: the page %r shows %s" % (_pn, _cells))
    if k2["normal"] != k2["full"]:
        errs.append("K2.1: in full screen the boxes are %s px, outside %s px" % (k2["full"], k2["normal"]))

    # 2026-09-30 (E10.M-up) — K AND ↑ IN COMMAND MODE STOP AT THE TITLE.
    # Both are JupyterLab's "select the cell above"; the scroll they cause is
    # held on __nbTopAt for 1.5 s, the key itself is not prevented. ↓ is not
    # held (control). The mock notebook is the scroller.
    kh = pg.evaluate("""async () => {
        var nb = document.querySelector('.jp-Notebook'), out = {};
        var top0 = window.__nbTopAt; window.__nbTopAt = 191;
        nb.classList.add('jp-mod-commandMode');
        var one = async function(key){
            window.__nbKHold = null; nb.scrollTop = 400;
            await new Promise(function(r){ setTimeout(r, 60); });
            var ev = new KeyboardEvent('keydown', {key: key, bubbles: true, cancelable: true});
            nb.dispatchEvent(ev);
            nb.scrollTop = 0;
            await new Promise(function(r){ setTimeout(r, 120); });
            return {st: nb.scrollTop, prevented: ev.defaultPrevented};
        };
        out.k = await one('k'); out.up = await one('ArrowUp'); out.down = await one('ArrowDown');
        window.__nbKHold = null; nb.classList.remove('jp-mod-commandMode'); window.__nbTopAt = top0; nb.scrollTop = 0;
        return out; }""")
    print("E10.M-up K/↑ hold:", kh)
    for _k in ("k", "up"):
        if abs(kh[_k]["st"] - 191) > 1 or kh[_k]["prevented"]:
            errs.append("E10.M-up: %s in command mode left scrollTop %s (want __nbTopAt 191), prevented %s" % (_k, kh[_k]["st"], kh[_k]["prevented"]))
    if kh["down"]["st"] != 0:
        errs.append("E10.M-up: ArrowDown was held too (scrollTop %s)" % kh["down"]["st"])

    # ---- 2026-10-02 (E17.4 + E19.5) — THE ACCOUNT -----------------------
    # (window.__nbrailSync is a spy since the version test above: the real
    # sync runs on its 1.5-s interval, so each step waits for it)
    _A = lambda js: pg.evaluate("async () => { var A = window.__nbAcct, h = document.getElementById('nbpanel-root'); " + js + " }")
    acct = {}
    if not pg.evaluate("() => !!window.__nbAcct"):
        acct = {"missing": True}
    else:
        acct.update(_A("""
        ['digichemjn.account.v1', 'digichemjn.acct.push'].forEach(function(k){ localStorage.removeItem(k); });
        window.__pr0 = localStorage.getItem('digichemjn.progress.v1');
        localStorage.setItem('digichemjn.progress.v1', JSON.stringify({'complex-numbers': {title: 'Complex Numbers', a: [1, 9],
            p: {both: 'dsfoooooo|doooooooo|gt-------'}}}));
        var out = {ready: A.ready(), short: (await A.create('kurz')).ok};
        var c = await A.create('geheim123'); out.created = c.ok; out.id = c.id;
        return out;"""))
        pg.wait_for_timeout(1800)
        acct.update(_A("""
        var out = {};
        out.wrong = (await A.code('falsch999')).ok;
        var k = await A.code('geheim123'); out.code = k.code || '';
        out.qr = /<svg[^>]*nbacct-qr/.test(A.qr(out.code));
        A.logout(); return out;"""))
        pg.wait_for_timeout(1800)
        acct.update(_A("""
        var out = {}, code = %s;
        localStorage.setItem('digichemjn.progress.v1', JSON.stringify({'complex-numbers': {title: 'Complex Numbers',
            p: {both: 'oodoooood|ooooooood|--s-----t'}}}));
        var bad = code.slice(0, 30) + (code[30] === 'A' ? 'B' : 'A') + code.slice(31);
        out.typo = (await A.login(bad, 'geheim123')).why;
        out.pw = (await A.login(code, 'geheim999')).why;
        var r = await A.login(code, 'geheim123'); out.login = r.ok; out.on = A.on();
        out.merged = JSON.parse(localStorage.getItem('digichemjn.progress.v1'))['complex-numbers'].p.both;
        out.push = localStorage.getItem('digichemjn.acct.push');
        out.store = ['digichemjn.account.v1', 'digichemjn.progress.v1'].map(function(k){ return localStorage.getItem(k); }).join(' ');
        return out;""" % json.dumps(acct.get("code", ""))))
        acct.update(_A("""
        var out = {};
        A.logout(); localStorage.removeItem('digichemjn.account.v1'); localStorage.removeItem('digichemjn.acct.push');
        if (window.__pr0 === null) localStorage.removeItem('digichemjn.progress.v1'); else localStorage.setItem('digichemjn.progress.v1', window.__pr0);
        return out;"""))
    print("E17.4/E19.5 account:", {k: (v[:60] + "…" if isinstance(v, str) and len(v) > 60 else v) for k, v in acct.items()})
    if acct.get("missing"):
        errs.append("E17.4: no window.__nbAcct")
    else:
        if not acct["ready"]: errs.append("E19.5: WebCrypto not ready on the test page")
        if acct["short"]: errs.append("E19.5: a 4-character password was taken")
        if not acct["created"] or not re.match(r"^DCJ(-[0-9A-HJKMNP-TV-Z]{4}){3}$", acct["id"] or ""):
            errs.append("E17.4: the person id is %r" % acct["id"])
        if acct["wrong"]: errs.append("E19.5: a wrong password made a code")
        if not re.match(r"^DCJ1\.[A-Za-z0-9_-]+\.[0-9A-Z]{2}$", acct["code"]) or len(acct["code"]) > 300:
            errs.append("E17.4: the code is %d characters: %r" % (len(acct["code"]), acct["code"][:40]))
        if not acct["qr"]: errs.append("E17.4: no QR")
        if acct["typo"] != "typo": errs.append("E17.4: a changed character reads as %r, not a typo" % acct["typo"])
        if acct["pw"] != "password": errs.append("E19.5: a wrong password reads as %r" % acct["pw"])
        if not acct["login"] or not acct["on"]: errs.append("E17.4: the log-in failed")
        # code: d s f o… / d o… / g t -…   here: o o d … d / o … d / - - s … t  → never back
        if acct["merged"] != "dsdoooood|doooooood|gts-----t":
            errs.append("E17.5c: the merge gave %r (wanted dsdoooood|doooooood|gts-----t)" % acct["merged"])
        if '"complex-numbers":1' not in (acct["push"] or ""):
            errs.append("E17.5: the merged progress does not wait for the kernel (%r)" % acct["push"])
        if re.search(r"geheim|\b1[6-9]\d{11}\b", acct["store"]):
            errs.append("E17.5d: the store holds a password or a time: %r" % acct["store"][:200])


    # 2026-10-02 (E17.2) — the 👤 window: account, settings, progress, start
    # over; the chip names the person once an account is on, "—" after it
    # is off. Needs the account (E17.4) and the window (E17.2, 18:
    # window.__nbAcctPanel); without either the block says so.
    if pg.evaluate("() => !!(window.__nbAcct && window.__nbAcctPanel)"):
        pg.evaluate("async () => { localStorage.removeItem('digichemjn.account.v1'); await window.__nbAcct.create('geheim123'); var h = document.getElementById('nbpanel-root'); h.dataset.page = 'code'; h.classList.add('open'); }")
        pg.wait_for_timeout(1800)        # the real sync, on its interval (see the version test)
        w172 = pg.evaluate("""() => { var h = document.getElementById('nbpanel-root'), A = window.__nbAcct, out = {id: A.get().id};
            out.chip = (h.querySelector('.nbpid') || {}).textContent;
            // rebase 03.10.: the cells by the stylesheet's contract (css-E17.2),
            // in the order they are DRAWN (grid order, read from the boxes)
            var vis = [].filter.call(h.querySelectorAll('.nbdrawer .nbcell'), function(e){ return getComputedStyle(e).display !== 'none'; });
            vis.sort(function(p, q){ return p.getBoundingClientRect().top - q.getBoundingClientRect().top; });
            out.cells = vis.map(function(e){ var m = (e.className.match(/pg-\\w+/) || ['?'])[0];
                                             return e.querySelector('[data-slot="nbctl-reset"]') ? 'reset' : m; });
            var f = h.querySelector('.nbacct[data-where="panel"]'); out.form = f ? f.getAttribute('data-in') : null;
            out.prefs = [].map.call(h.querySelectorAll('select.nbpref'), function(e){ return e.getAttribute('data-k'); });
            out.heads = [].map.call(h.querySelectorAll('.pg-acct .nbcell-h, .pg-set .nbcell-h'), function(e){ return e.textContent; });
            A.logout(); h.classList.remove('open'); return out; }""")
        pg.wait_for_timeout(1800)
        w172["chipOut"] = pg.evaluate("() => { var t = (document.querySelector('#nbpanel-root .nbpid') || {}).textContent; localStorage.removeItem('digichemjn.account.v1'); return t; }")
        print("E17.2 the 👤 window:", w172)
        if w172["chip"] != w172["id"]: errs.append("E17.2: logged in, the chip shows %r" % w172["chip"])
        if w172["chipOut"] != "—": errs.append("E17.2: logged out, the chip shows %r" % w172["chipOut"])
        if w172["form"] != "1": errs.append("E17.2: logged in, the 👤 form says data-in=%r" % w172["form"])
        if w172["cells"] != ["pg-acct", "pg-code", "pg-set", "pg-stats", "reset"]:
            errs.append("E17.2: the 👤 window shows %s" % w172["cells"])
        # E38a J3 (Nutzer 14.10.): BEHAUPTETE BISHER skin, theme, lang, ROLE, mode — die Rolle ist ersatzlos weg
        if w172["prefs"] != ["skin", "theme", "lang", "mode"]:
            errs.append("E17.2: the settings are %s" % w172["prefs"])
    else:
        print("E17.2 the 👤 window: no account (E17.4) or no 👤 window (E17.2) here — skipped")

    pg.screenshot(path="/home/claude/jsmock.png", full_page=False)
    pg.close(); b.close()
for e in errs: print("  !!", e)
bad=[]
if res!="ok": bad.append(res)
if not info["host"]: bad.append("no #nbpanel-host was created")
elif not info["ready"]: bad.append("the host is not marked ready (stays invisible)")
elif info["dots"]<_NDOTS: bad.append("the host has only %d dots" % info["dots"])   # hw-E25.l: 7 Aufgaben, MCQ/BYOD raus (behauptete bisher: >= 8 = 7 + Quiz + Daten)
if info["parent"] not in (None,"BODY"): bad.append("host is not on <body> but in %s" % info["parent"])
if errs: bad += errs
print("\n"+("PANEL SCRIPT OK" if not bad else "FAILURES:\n- "+"\n- ".join(map(str,bad))))
sys.exit(1 if bad else 0)
