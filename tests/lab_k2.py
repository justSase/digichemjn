"""Real-JupyterLab measurement for the K2 corrections (STRUKTUR, 2026-09-28b).

NOT a suite: it needs a running `jupyter lab` (see lab_keys.py). A fresh copy
of the notebook per skin, the reader's own mouse and keyboard, reads from
getBoundingClientRect / getComputedStyle / classes only. The LINE is the
reading line (top of the rail's window + railY0, where the cursor stands).
The other K2 points are measured elsewhere: K2.4 in lab_center.py, K2.9 and
K2.10 in lab_landing.py; K2.6 came with K1 (lab_skip.py).

  E  K2.2  END OF GUIDE — the heading "End of the guided part" scrolled onto
           the line: its mark's middle − the heading's middle <= 2 px.
  Q  K2.3  ONE MARK PER EXERCISE — the panel carries as many marks as its
           source. E25.l: the quiz (q1) and own data (b1) have NO mark (out
           for now; behauptete bisher: one mark each, none pointing where
           theirs does).
  N  K2.8  NAMES — every numbered mark reads "Chapter|Figure|Exercise|Coding
           n: …", and the middle of what its name shows is the middle
           between the column's start — the panel's inner edge + (5 + 8·K)
           px, where the cursor stood until E9.1 — and the lane (the marks'
           axis), <= 1 px; panel at 100 %, 75 % and 50 %, lens 100 %.
           Until v1.45 it claimed "between the cursor's end and the lane"; the
           cursor left the column in E9.1 and the panel in E11.6/E12.3 (it is
           the scrollbar thumb in the tool column now, x ≈ 312–322).
  T  K2.11 TITLE — the top mark reads what the title card's heading reads;
           a name too long for the column ends in an ellipsis; at scroll 0
           the mark stands on the card's middle (<= 2 px).
  S  K2.7  STATISTICS — (E17.2, 04.10.: BEHAUPTETE BISHER „📚 is in the
           toolbar and opens a window of its own“; 📚 is part of 👤 now) 📚
           is not drawn; a click on 👤 opens the one window, which shows the
           statistics among account, code, settings (css-E17.2); it lists the chapters of this notebook
           (as many rows as chapter marks on the rail — until 01.10. a fixed
           7, Complex's count; Modeling has 9)
           with their states (t1 solved through the kernel: chapter 1's
           exercise pip "done", the badge counts it).
  Z  K2.5  ZOOM — chapter 2 clicked (it lands on the line), then the lens
           100 → 60 → 100 → 150 % with Ctrl+minus / Ctrl+plus (60 is the
           lens's floor): after each step the reading line and the knob
           (.nbgrip) keep their height (<= 1 px), chapter 2's PILL (the point of
           the document on the line, E11.5) stays on the line (<= 2 px) and its
           mark on the middle of the pill (<= 2 px, the Zoom criterion). Until
           v1.45 it held the CURSOR's height: since E12.3 the cursor is the
           scrollbar thumb, it follows the scroll share, and the lens changes
           that share. Until 01.10. (E10 Teil 4) it BEHAUPTETE "the MARK on the
           line (<= 2 px)" — the sum of both tolerances: in Modeling the pill
           drifts 0.4–0.9 px per lens step (whole-pixel scrollTop), 1.8 px
           after three steps, the mark 0.2 px under the pill → 2.02 px, red,
           while each criterion held. The drift is reported (`drift`).
  F  K2.1  FULL SCREEN — at 1920 × 1080: exercise box, key message,
           interpretation, figure and lock box widths, each over the text
           column (the chapter's key-message box), before and after ⛶ with
           the mouse: equal within 2 %; nothing wider than the text column
           × 1.02 in full screen.

    python3 tests/lab_k2.py <notebook> <out.json> [skin,...]
Exit 1 if a criterion fails."""
import sys, json, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import fresh, CHROME
from lab_marks import kexec
from playwright.sync_api import sync_playwright
BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
ROOT = os.environ.get("DIGICHEM_LAB_ROOT", "/home/claude/lab/root")
nb, out = sys.argv[1], sys.argv[2]
skins = sys.argv[3].split(",") if len(sys.argv) > 3 and sys.argv[3] else [None]
SC = "document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer')"
LIB = r"""
window.__k2 = {
  MK: '.nbsect,.nbsubdot,.nbchapdot,.nbvizmark,.nbrail-dot,.nbcodemark',
  sc: function(){ return %s; },
  host: function(){ return document.getElementById('nbpanel-root'); },
  nodes: function(){ return [].slice.call(document.querySelectorAll('#nbpanel-root .nbmap-node')); },
  line: function(){ var h = this.host(), map = h.querySelector('.nbmap');
    return map.getBoundingClientRect().top + (parseInt(h.dataset.railY0 || '0', 10) || 0); },
  mark: function(n){ var m = n && n.querySelector(this.MK); if (!m) return null; var r = m.getBoundingClientRect();
    return r.height > 0 ? {x: r.left + r.width / 2, y: r.top + r.height / 2} : null; },
  cursor: function(){ var c = this.host().querySelector('.nbmap-cursor'); if (!c) return null;
    var r = c.getBoundingClientRect(); return r.width > 0 ? {right: r.right, y: r.top + r.height / 2} : null; },
  // where the name column starts (E9.1): the rail's inner edge + (5 + 8·K)
  colStart: function(){ var h = this.host(), rl = h.querySelector('.nbrail'); if (!rl) return null;
    var k = parseFloat(getComputedStyle(h).getPropertyValue('--nbk')) || parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nbk')) || 1;
    return rl.getBoundingClientRect().left + 1 + 5 + Math.round(8 * k); },
  grip: function(){ var g = this.host().querySelector('.nbgrip'); if (!g) return null; var r = g.getBoundingClientRect();
    return r.height > 0 ? r.top + r.height / 2 : null; },
  // the part of a name the reader sees: its text, clipped to its box
  shown: function(lab){ var b = lab.getBoundingClientRect(); if (b.width <= 0) return null;
    var rg = document.createRange(); rg.selectNodeContents(lab);
    var L = 1e9, R = -1e9; [].forEach.call(rg.getClientRects(), function(q){ if (q.width > 0) { L = Math.min(L, q.left); R = Math.max(R, q.right); } });
    if (R < L) return null;
    // an inline ::before ("＋ " on Your own cell, CSS) is ink the Range does not
    // see: measure it as a span of the same text and font, put it before L
    var bf = getComputedStyle(lab, '::before'), bc = bf.content;
    if (bc && bc !== 'none' && bc !== 'normal' && bf.display.indexOf('inline') === 0 && bf.position === 'static') {
      var sp = document.createElement('span'); sp.textContent = bc.replace(/^["']|["']$/g, '');
      sp.style.cssText = 'font:' + bf.font + ';letter-spacing:' + bf.letterSpacing + ';text-transform:' + bf.textTransform + ';white-space:pre;';
      lab.insertBefore(sp, lab.firstChild); var pw = sp.getBoundingClientRect().width; sp.remove();
      L -= pw; }
    L = Math.max(L, b.left); R = Math.min(R, b.right);
    var cs = getComputedStyle(lab);
    return {mid: (L + R) / 2, cut: lab.scrollWidth > lab.clientWidth + 1, ell: cs.textOverflow, ws: cs.whiteSpace}; },
  vis: function(e){ if (!e) return false; var r = e.getBoundingClientRect(); var c = getComputedStyle(e);
    return r.width > 0 && r.height > 0 && c.visibility === 'visible' && c.display !== 'none'; }
};
""" % SC
res = {}; fails = []

def bring_line(pg, js_el, tries=5):
    """scroll so the middle of the element js_el returns sits on the line"""
    for _ in range(tries):
        d = pg.evaluate("()=>{var e=(" + js_el + ")(); if(!e) return null; var r=e.getBoundingClientRect(); return r.top+r.height/2-window.__k2.line();}")
        if d is None: return None
        if abs(d) < 0.6: return d
        pg.evaluate("(d)=>{window.__k2.sc().scrollTop += d;}", d); pg.wait_for_timeout(900)
    return pg.evaluate("()=>{var e=(" + js_el + ")(); var r=e.getBoundingClientRect(); return r.top+r.height/2-window.__k2.line();}")

def click_node(pg, i):
    for _ in range(4):
        xy = pg.evaluate("(i)=>{var n=window.__k2.nodes()[i], m=window.__k2.mark(n); if(!m) return null; var e=document.elementFromPoint(m.x,m.y); return [m.x,m.y,!!(e&&e.closest('.nbmap-node')===n)];}", i)
        if xy is None: return False
        vh = pg.evaluate("()=>window.innerHeight")
        if xy[2] and 150 < xy[1] < vh - 80:
            pg.mouse.click(xy[0], xy[1]); pg.wait_for_timeout(2600); return True
        pg.evaluate("(d)=>{window.__k2.sc().scrollTop += d;}", xy[1] - vh / 2); pg.wait_for_timeout(900)
    return False

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    ctx = None; errs = []
    for sk in skins:
        key = sk or "default"
        ctx, pg, e1 = fresh(b, BASE, nb, ROOT, ctx)
        pg.set_viewport_size({"width": 1400, "height": 900}); pg.wait_for_timeout(1500)
        try: pg.click(".jp-toast-buttonBar button:has-text('No')", timeout=1500)
        except Exception: pass
        pg.add_script_tag(content=LIB)
        if sk:
            pg.evaluate("(s)=>{ window.__nbStore.set('digichemjn.skin.v1', s); window.__nbApplySkin && window.__nbApplySkin(); }", sk)
            pg.wait_for_timeout(1500)
        R = res[key] = {}
        # ---- T: the title mark ------------------------------------------
        pg.evaluate("()=>window.__nbSetGui(100)"); pg.wait_for_timeout(1500)
        pg.evaluate("()=>{window.__k2.sc().scrollTop=0;}"); pg.wait_for_timeout(1500)
        t = pg.evaluate("""()=>{var n=window.__k2.nodes()[0], lab=n.querySelector('.nbmap-lab');
            var card=[].filter.call(document.querySelectorAll('.nbtitle-card'),function(c){return c.getBoundingClientRect().height>0;})[0];
            var h=card&&card.querySelector('.nbtitle-h'); var cr=card.getBoundingClientRect(); var m=window.__k2.mark(n);
            var cs=getComputedStyle(lab);
            return {lab:lab.textContent, head:h?h.textContent.replace(/\\s+/g,' ').trim():null, title:n.classList.contains('title'),
                    mark:m?m.y:null, card:cr.top+cr.height/2, ell:cs.textOverflow, ws:cs.whiteSpace, ov:cs.overflow,
                    clamp:cs.webkitLineClamp, long:(function(){ var o=lab.textContent; lab.textContent=Array(40).join('Complex Numbers ');
                      var lh=parseFloat(cs.lineHeight)||parseFloat(cs.fontSize)*1.2, r={cut:lab.scrollHeight>lab.clientHeight+1||lab.scrollWidth>lab.clientWidth+1,
                      lines:Math.round(lab.clientHeight/lh)}; lab.textContent=o; return r; })()};}""")
        R["T"] = t
        if not t["title"] or t["lab"].strip() != (t["head"] or "") or not t["head"]:
            fails.append("%s T: top mark reads %r, the card's heading %r" % (key, t["lab"], t["head"]))
        # 2026-09-28c — UNTIL 28b this asserted one line (white-space:nowrap) and
        # an ellipsis. Since the user's variant (a) (28.09. 03:1x) every name,
        # the title's too, breaks into a second line first; the ellipsis comes
        # when two are not enough. Measured now with a real long title put in
        # the label: clipped, at most two lines, and the ellipsis is set.
        one = t["ws"] == "nowrap"
        two = t["ws"] == "normal" and str(t.get("clamp")) == "2"
        lg = t.get("long") or {}
        if t["ell"] != "ellipsis" or not (one or two) or not lg.get("cut") or lg.get("lines", 9) > 2:
            fails.append("%s T: a long title would not end in an ellipsis within two lines (%s / %s / clamp %s / %s)"
                         % (key, t["ell"], t["ws"], t.get("clamp"), lg))
        if t["mark"] is None or abs(t["mark"] - t["card"]) > 2:
            fails.append("%s T: title mark %s, card middle %.1f" % (key, t["mark"], t["card"]))
        # ---- Q: one mark per exercise -----------------------------------
        q = pg.evaluate("""()=>{var ns=window.__k2.nodes(), o={};
            ['q1','b1'].forEach(function(k){ var own=ns.filter(function(n){return n.getAttribute('data-task')===k && n.classList.contains('task');});
              var tg=own.length?own[0].getAttribute('data-target'):null;
              o[k]={marks:own.length, sameTarget:ns.filter(function(n){return tg && n.getAttribute('data-target')===tg;}).length,
                    name:own.length?(own[0].querySelector('.nbtasklab')||{}).textContent:null}; });
            var src=[].filter.call(document.querySelectorAll('.nbfeed[data-final]'),function(f){return f.isConnected && f.querySelector('.nbrail');})[0];
            o.panel=ns.length; o.source=src?src.querySelectorAll('.nbmap-node').length:null; return o;}""")
        R["Q"] = q
        for k in ("q1", "b1"):                 # E25.l: out for now
            if q[k]["marks"] != 0:
                fails.append("%s Q %s: %d mark(s), want 0 (E25.l)" % (key, k, q[k]["marks"]))
        if q["panel"] != q["source"]:
            fails.append("%s Q: panel %s marks, source %s" % (key, q["panel"], q["source"]))
        # ---- N: names, 100 % and 50 % ------------------------------------
        R["N"] = {}
        for pct in (100, 75, 50):
            pg.evaluate("(p)=>window.__nbSetGui(p)", pct); pg.wait_for_timeout(1800)
            nn = pg.evaluate("""()=>{var cu=window.__k2.cursor(), c0=window.__k2.colStart(), out=[];
                window.__k2.nodes().forEach(function(n,i){ if(n.classList.contains('nbgone')) return;
                  var num=n.classList.contains('chap')||n.classList.contains('viztask')||n.classList.contains('task')||n.classList.contains('codetask');
                  var lab=n.classList.contains('task')?n.querySelector('.nbtasklab'):n.querySelector('.nbmap-lab');
                  if(!lab) return; var sh=window.__k2.shown(lab), m=window.__k2.mark(n);
                  out.push({i:i, num:num, text:lab.textContent, mid:sh?sh.mid:null, cut:sh?sh.cut:null,
                            lane:m?m.x:null, want:(c0!==null&&m)?(c0+m.x)/2:null}); });
                return {names:document.getElementById('nbpanel-root').classList.contains('nbnames'), cursor:cu, colStart:c0, rows:out};}""")
            R["N"][pct] = nn
            if not nn["names"]:
                # below ~55 %% the column between the cursor and the widest
                # mark is under 72 px and the names are dropped (a rule since
                # 25d); 50 %% is recorded, not required
                if pct != 50: fails.append("%s N %d%%: the names are not shown" % (key, pct))
                continue
            for r in nn["rows"]:
                if r["num"] and not re.match(r"^(Chapter|Figure|Exercise|Coding) \d+: .+", r["text"] or ""):
                    fails.append("%s N %d%% node %d: name %r" % (key, pct, r["i"], r["text"]))
                if r["mid"] is None or r["want"] is None or abs(r["mid"] - r["want"]) > 1:
                    fails.append("%s N %d%% node %d %r: name middle %s, cursor–lane middle %s" % (key, pct, r["i"], (r["text"] or "")[:24], r["mid"], r["want"]))
        pg.evaluate("()=>window.__nbSetGui(100)"); pg.wait_for_timeout(1500)
        # ---- E: end of guide ---------------------------------------------
        hd = "function(){return [].filter.call(document.querySelectorAll('.nbend-h'),function(e){return e.getBoundingClientRect().height>0;})[0];}"
        d0 = bring_line(pg, hd)
        e = pg.evaluate("""()=>{var h=[].filter.call(document.querySelectorAll('.nbend-h'),function(e){return e.getBoundingClientRect().height>0;})[0];
            var r=h.getBoundingClientRect(); var n=document.querySelector('#nbpanel-root .nbmap-node.end'); var m=window.__k2.mark(n);
            return {text:r.top+r.height/2, mark:m?m.y:null, line:window.__k2.line(), lit:n.classList.contains('here')};}""")
        R["E"] = e
        if e["mark"] is None or abs(e["mark"] - e["text"]) > 2:
            fails.append("%s E: end mark %s, heading middle %.1f (line %.1f)" % (key, e["mark"], e["text"], e["line"]))
        # ---- S: statistics ----------------------------------------------
        kexec("task_solved('t1')\n"); pg.wait_for_timeout(3500)
        s0 = pg.evaluate("""()=>{var b=document.querySelector('#nbpanel-root .nbdock .nbseries'), p=document.querySelector('#nbpanel-root .nbcorner .nbbtn.nbprofile');
            var r=p?p.getBoundingClientRect():{left:0,width:0,top:0,height:0};
            return {series:!!(b&&window.__k2.vis(b)), vis:!!(p&&window.__k2.vis(p)), x:r.left+r.width/2, y:r.top+r.height/2,
                    role:window.__nbRole?window.__nbRole():null};}""")
        S = {"button": s0}
        if s0["series"]:
            fails.append("%s S: 📚 is drawn (E17.2: only 👤) (%s)" % (key, s0))
        if not s0["vis"] or s0["role"] != "reader":
            fails.append("%s S: 👤 not in the corner for a reader (%s)" % (key, s0))
        else:
            pg.mouse.click(s0["x"], s0["y"]); pg.wait_for_timeout(1500)
            S["window"] = pg.evaluate("""()=>{var h=window.__k2.host();
                var cells=[].filter.call(h.querySelectorAll('.nbdrawer .nbcell'),window.__k2.vis).map(function(c){return (c.className.match(/pg-\\w+/)||['?'])[0];});
                var rows=[].slice.call(h.querySelectorAll('.nbserieslist .nbseries-chap')).map(function(r){return {nm:r.querySelector('.nm').textContent, ps:[].map.call(r.querySelectorAll('.ps'),function(p){return p.className;})};});
                var lst=h.querySelector('.nbserieslist');
                return {open:h.classList.contains('open'), page:h.dataset.page, cells:cells, rows:rows, list:window.__k2.vis(lst)};}""")
            w = S["window"]
            if not w["open"] or w["page"] != "code" or not w["list"]:
                fails.append("%s S: the click on 👤 did not show the statistics (%s)" % (key, w))
            if not set(w["cells"]) <= {"pg-acct", "pg-code", "pg-set", "pg-stats"} or "pg-stats" not in w["cells"]:
                fails.append("%s S: the 👤 window shows %s (E17.2: account, code, settings, statistics)" % (key, w["cells"]))
            nch = pg.evaluate("()=>window.__k2.nodes().filter(function(n){return n.classList.contains('chap');}).length")
            if len(w["rows"]) != nch:
                fails.append("%s S: %d chapter rows, %d wanted (chapter marks)" % (key, len(w["rows"]), nch))
            elif "done" not in " ".join(w["rows"][0]["ps"]):
                fails.append("%s S: chapter 1 after t1 solved: %s" % (key, w["rows"][0]["ps"]))
            pg.keyboard.press("Escape"); pg.wait_for_timeout(900)
        R["S"] = S
        # ---- Z: zoom -----------------------------------------------------
        c2 = pg.evaluate("()=>window.__k2.nodes().findIndex(function(n){return n.classList.contains('chap') && /Chapter 2\\b/.test(n.textContent);})")
        Z = []
        # the answer to t1 above moved the reader on to chapter 2 (F) and
        # chose it: a click on it now would be a second click and fold it.
        # Start from another mark — the title — so the click is a first one.
        click_node(pg, 0)
        if c2 < 0 or not click_node(pg, c2):
            fails.append("%s Z: chapter 2 could not be clicked" % key)
        else:
            def zs(tag):
                pg.wait_for_timeout(2600)
                s = pg.evaluate("""(i)=>{var n=window.__k2.nodes()[i], m=window.__k2.mark(n), c=window.__k2.cursor();
                    var z=null; try{z=localStorage.getItem(window.__nbZKey ? window.__nbZKey() : 'digichemjn.zoom.v1');}catch(e){}
                    var A=document.getElementById(n.getAttribute('data-target')), hs=A?[].filter.call(document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jupyter-widget-Collapse-header'),function(x){return !!(A.compareDocumentPosition(x)&4);}):[], hr=hs[0]?hs[0].getBoundingClientRect():null;
                    return {zoom:z, line:window.__k2.line(), grip:window.__k2.grip(), cursor:c?c.y:null, mark:m?m.y:null, pill:hr?hr.top+hr.height/2:null, sel:n.classList.contains('nbsel')};}""", c2)
                s["tag"] = tag; Z.append(s); return s
            base = zs("clicked")
            # THE LENS in the notebook's toolbar, with the reader's own hand:
            # the mouse puts the focus on its thumb; Home takes it to its floor
            # (60 %% — 50 is below the lens's range); a double click on it puts
            # it back to 100 %% (its own reset); then ArrowRight, one step of
            # the slider (5 = 7 %%) a press, 7 presses → 149.6 ≈ 150 %%. Every
            # key is an input event on the slider, as a drag is.
            THJ = "()=>{var s=document.querySelector('#nbpanel-root .nbz-doc .nbslider'); var r=s.getBoundingClientRect(); var v=+s.value, mx=+(s.max||100); return [r.left+8+(r.width-16)*v/mx, r.top+r.height/2];}"
            th = pg.evaluate(THJ)
            pg.mouse.click(th[0], th[1]); pg.wait_for_timeout(600)
            pg.keyboard.press("Home"); zs("60")
            th = pg.evaluate(THJ); pg.mouse.dblclick(th[0], th[1]); zs("100")
            # hw-E25.int (08.10.): since js-E25.o the bar's middle is 100 %% and
            # its upper half runs to the window's ceiling — a step is no longer
            # 7 %% everywhere (behauptete bisher: 7 presses → 150 %%). Pressed
            # until the lens reads ≥ 148 %%, at most 15 presses.
            ZR = "()=>{try{return +localStorage.getItem(window.__nbZKey ? window.__nbZKey() : 'digichemjn.zoom.v1')||100;}catch(e){return 100;}}"
            for _ in range(15):
                pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(120)
                if pg.evaluate(ZR) >= 148: break
            zs("150")
            for s in Z:
                if not s["sel"]:
                    fails.append("%s Z %s: chapter 2 is not the chosen mark" % (key, s["tag"]))
                if abs(s["line"] - base["line"]) > 1:
                    fails.append("%s Z %s: reading line %s, before %s" % (key, s["tag"], s["line"], base["line"]))
                if s["grip"] is None or base["grip"] is None or abs(s["grip"] - base["grip"]) > 1:
                    fails.append("%s Z %s: knob %s, before %s" % (key, s["tag"], s["grip"], base["grip"]))
                if s["pill"] is None or abs(s["pill"] - s["line"]) > 2:
                    fails.append("%s Z %s: chapter 2's pill %s, line %.1f (the document point, E11.5)" % (key, s["tag"], s["pill"], s["line"]))
                if s["mark"] is None or s["pill"] is None or abs(s["mark"] - s["pill"]) > 2:
                    fails.append("%s Z %s: chapter 2's mark %s, its pill %s" % (key, s["tag"], s["mark"], s["pill"]))
            zz = [int(s["zoom"] or 0) for s in Z[1:]]
            if not (zz[0] == 60 and abs(zz[1] - 100) <= 1 and 148 <= zz[2] <= 165):
                fails.append("%s Z: the lens went %s" % (key, [s["zoom"] for s in Z]))
            # back to 100 for what follows (a double click on the lens)
            th = pg.evaluate(THJ); pg.mouse.dblclick(th[0], th[1]); pg.wait_for_timeout(1500)
        R["Z"] = Z
        # ---- F: full screen ----------------------------------------------
        pg.set_viewport_size({"width": 1920, "height": 1080}); pg.wait_for_timeout(2000)
        # chapter 2 open (lock box), chapter 1's figure and exercise open
        pg.evaluate("""()=>{[].forEach.call(document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .acc-chapter > .jupyter-widget-Collapse, .jp-NotebookPanel:not(.lm-mod-hidden) .acc-viz > .jupyter-widget-Collapse, .jp-NotebookPanel:not(.lm-mod-hidden) .acc-practice > .jupyter-widget-Collapse'),
            function(c){ if(!c.classList.contains('jupyter-widget-Collapse-open') && !c.closest('.acc-tasklock')){ var h=c.querySelector('.jupyter-widget-Collapse-header'); if(h && h.getBoundingClientRect().height>2) h.click(); } });}""")
        pg.wait_for_timeout(4000)
        WJS = """()=>{var sc=window.__k2.sc(); var K={task:'.nbbox-ex', key:'.nbbox-concept', interp:'.nbbox-interp', figure:'.nbplot', lock:'.nblocked-note'};
            var o={screen:window.innerWidth, fs:!!document.fullscreenElement, col:null, w:{}};
            Object.keys(K).forEach(function(k){ var ws=[].filter.call(sc.querySelectorAll(K[k]),function(e){return !e.closest('#nbpanel-root') && e.getBoundingClientRect().width>0;}).map(function(e){return e.getBoundingClientRect().width;});
              o.w[k]=ws.length?Math.max.apply(null,ws):null; });
            o.col=o.w.key; return o;}"""
        f0 = pg.evaluate(WJS)
        xy = pg.evaluate("()=>{var b=document.querySelector('#nbpanel-root .nbdock .nbfull'); var r=b.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];}")
        pg.mouse.click(xy[0], xy[1]); pg.wait_for_timeout(3000)
        f1 = pg.evaluate(WJS)
        R["F"] = {"normal": f0, "full": f1}
        if not f1["fs"]:
            fails.append("%s F: ⛶ did not enter full screen" % key)
        for k, w0 in f0["w"].items():
            w1 = f1["w"].get(k)
            if w0 is None or w1 is None:
                fails.append("%s F %s: not measured (%s → %s)" % (key, k, w0, w1)); continue
            r0, r1 = w0 / f0["col"], w1 / f1["col"]
            if abs(r1 - r0) > 0.02 * r0:
                fails.append("%s F %s: %.0f/%.0f = %.3f normal, %.0f/%.0f = %.3f full screen" % (key, k, w0, f0["col"], r0, w1, f1["col"], r1))
            if w1 > f0["col"] * 1.02:
                fails.append("%s F %s: %.0f px in full screen, text column %.0f" % (key, k, w1, f0["col"]))
        try: pg.evaluate("()=>document.exitFullscreen()")
        except Exception: pass
        pg.wait_for_timeout(1000)
        errs += e1
    res["errs"] = errs
    if errs: fails.append("console: %s" % errs[:3])
    ctx.close(); b.close()
res["fails"] = fails
json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
for k, v in res.items():
    if not isinstance(v, dict) or "T" not in v: continue
    print("%-7s T title %r = card %r, mark−card %.1f" % (k, v["T"]["lab"], v["T"]["head"], (v["T"]["mark"] or 0) - v["T"]["card"]))
    print("%-7s Q q1 %s b1 %s, panel %s = source %s" % (k, v["Q"]["q1"], v["Q"]["b1"], v["Q"]["panel"], v["Q"]["source"]))
    for pct, nn in v["N"].items():
        ds = [r["mid"] - r["want"] for r in nn.get("rows", []) if r["mid"] is not None and r["want"] is not None]
        print("%-7s N %s%% names %d, middle − (column start+lane)/2 %s, cut %d" % (k, pct, len(nn.get("rows", [])),
              ("%.1f..%.1f" % (min(ds), max(ds))) if ds else "-", sum(1 for r in nn.get("rows", []) if r["cut"])))
    print("%-7s E end mark − heading %.1f" % (k, (v["E"]["mark"] or 0) - v["E"]["text"]))
    print("%-7s S %s" % (k, {kk: vv for kk, vv in v["S"].items() if kk != "window"} | ({"rows": len(v["S"]["window"]["rows"]), "cells": v["S"]["window"]["cells"]} if "window" in v["S"] else {})))
    print("%-7s Z %s" % (k, ["%s: line %.1f knob %.1f cursor %.1f pill−line %.2f mark−pill %.2f mark−line %.2f" % (s["tag"], s["line"], s.get("grip") or -1, s["cursor"] or -1, (s.get("pill") or 0) - s["line"], (s["mark"] or 0) - (s.get("pill") or 0), (s["mark"] or 0) - s["line"]) for s in v["Z"]]))
    zp = [s.get("pill") for s in v["Z"] if s.get("pill") is not None]
    if len(zp) > 1: print("%-7s Z drift of the pill per lens step %s px" % (k, ["%.2f" % (zp[i + 1] - zp[i]) for i in range(len(zp) - 1)]))
    print("%-7s F normal %s | full %s" % (k, {kk: round(vv) if vv else vv for kk, vv in v["F"]["normal"]["w"].items()}, {kk: round(vv) if vv else vv for kk, vv in v["F"]["full"]["w"].items()}))
for f in fails: print("FAIL", f)
print("K2 OK" if not fails else "K2: %d failures" % len(fails))
sys.exit(1 if fails else 0)
