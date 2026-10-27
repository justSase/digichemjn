"""Real-JupyterLab measurement for APPLIKATION §8a — F, coding exercises are
exercises, and a right answer moves the reader on. 2026-09-27e.

NOT a suite: it needs a running `jupyter lab` (see lab_keys.py). A fresh copy
of the notebook, the reader's own hands (mouse and keyboard, no kernel calls
for the answers), and with getBoundingClientRect / class / attribute reads:

  A  TOGGLE — a click on a chapter mark chooses it and opens the chapter; a
     second single click on the chosen, open chapter folds it; a third opens
     it again. A double click folds nothing.
  B  CODE ROUTE — coding 1 typed and checked in its own fold: the fold closes,
     the coding mark is cd-done (data-cstate=done), chapter 2 is open, the
     purple door (cd-current) stands on coding 2, the chosen mark is chapter 2
     and the reading marker is on it: |marker - choice| <= 1 px.
  C  ANSWER ROUTE — exercise 1 typed and checked: its fold closes, the chosen
     mark is the next open place (chapter 2) and the marker is on it (<= 1 px).
  D  STATES — coding 2 skipped, coding 3 wrong (kernel, after the two real
     answers): cd-skip / cd-fail, data-cstate skip / fail, no chapter opened.
  E  RUN ALL = SPAWN ON THE TITLE (E12.2, 01.10.) — Run All again: the
     progress comes back, the document stands at __nbTopAt (0 since E12.2:
     no air), the lit mark is the title, its middle and the marker are on the
     reading line (<= 2 px), and nothing is chosen or scrolled by the panel in
     the 4 s after (the run is not an answer). Until v1.45 this part claimed
     "a run does not scroll"; with E9.2's air the run landed at 191.

  2026-10-03 (E21 Rest Stufe 2, JS) — B and C BEHAUPTETEN BISHER that the
  move is over 3.5 s after the click on "Check". The click starts the
  kernel's grading (1.8–2.4 s on the gate's one CPU), then the jump: landing
  passes at 60 … 1400 ms (01-jump) and the glide. Measured v1.62 probe,
  Complex: chapter 2 chosen at 2.40 s, the marker on it at 3.71 s — at 3.5 s
  the glide was 9 px short and the lit mark still coding 1, 100 px above
  (gate 03.10.: "Marker 100 px neben der gewählten Marke", the same since
  v1.54). The jump itself was right. Now B and C wait for it: from the
  moment the choice moves (the kernel has answered) the marker must be on
  the choice within the jump time, 1.4 s of landing passes + 1.5 s of glide
  (FINAL 4 "nach der Sprungzeit", 11 "nichts > 1,5 s"); both times are
  reported (`t_choice`, `t_land`).
  The same day: MODELING too. The script typed Complex's answers (`_q`,
  roots_of) and broke on Modeling (`name '_q' is not defined`, gate
  03.10.). Each notebook now gets its own right answers for exercise 1
  and coding 1 (Modeling: orders = log10(slow / fast), `_Q1`).

    python3 tests/lab_flow.py <notebook> <out.json> [skin]
Exit 1 if a criterion fails."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import fresh, CHROME
from lab_marks import kexec
from playwright.sync_api import sync_playwright
BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
ROOT = os.environ.get("DIGICHEM_LAB_ROOT", "/home/claude/lab/root")
nb, out = sys.argv[1], sys.argv[2]
skin = sys.argv[3] if len(sys.argv) > 3 else None
MK = '.nbsect,.nbsubdot,.nbchapdot,.nbvizmark,.nbrail-dot,.nbcodemark'
LIB = r"""
window.__fl = {
  acc: function(id){ var s = document.getElementById(id); if (!s) return null;
    var host = s; while (host.parentElement && !(host.parentElement.classList.contains('widget-vbox') ||
           host.parentElement.classList.contains('jupyter-widget-vbox'))) host = host.parentElement;
    var sib = host.nextElementSibling, k = 0;
    while (sib && k++ < 8){ var c = sib.classList.contains('jupyter-widget-Collapse') ? sib
             : sib.querySelector('.jupyter-widget-Collapse'); if (c) return c; sib = sib.nextElementSibling; }
    return null; },
  open: function(id){ var c = this.acc(id); return c ? c.classList.contains('jupyter-widget-Collapse-open') : null; },
  nodes: function(){ return [].slice.call(document.querySelectorAll('#nbpanel-root .nbmap-node')); },
  idx: function(sel, task){ var n = this.nodes();
    for (var i = 0; i < n.length; i++) if (n[i].matches(sel) && (!task || n[i].getAttribute('data-task') === task)) return i;
    return -1; },
  mid: function(n){ var m = n && n.querySelector('%MK%'); if (!m) return null;
    var r = m.getBoundingClientRect(); return r.height > 0 ? [r.left + r.width/2, r.top + r.height/2] : null; },
  state: function(){ var n = this.nodes(), self = this;
    var here = n.findIndex(function(x){ return x.classList.contains('here'); }),
        sel = n.findIndex(function(x){ return x.classList.contains('nbsel'); });
    var hm = here >= 0 ? self.mid(n[here]) : null, sm = sel >= 0 ? self.mid(n[sel]) : null;
    var sc = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer');
    var cur = [].slice.call(document.querySelectorAll('#nbpanel-root .nbcodemark.cd-current'))
                .map(function(c){ return c.closest('.nbmap-node').getAttribute('data-task'); });
    return {here: here, sel: sel, hereMid: hm, selMid: sm,
            gap: (hm && sm) ? Math.abs(hm[1] - sm[1]) : null,
            st: sc ? Math.round(sc.scrollTop) : null, cdCurrent: cur,
            selTarget: sel >= 0 ? n[sel].getAttribute('data-target') : null}; },
  node: function(i){ var n = this.nodes()[i]; return {cls: n.className, target: n.getAttribute('data-target'),
      task: n.getAttribute('data-task'), ds: n.getAttribute('data-state'), dc: n.getAttribute('data-cstate'),
      mark: (n.querySelector('.nbcodemark,.nbrail-dot') || {}).className || ''}; },
  tag: function(id, sel, name){ var c = this.acc(id); if (!c) return 0;
    var els = c.querySelectorAll(sel); for (var i = 0; i < els.length; i++) els[i].setAttribute('data-fl', name + i);
    return els.length; }
};
""".replace("%MK%", MK)
res = {}; fails = []

HIT = ("([i,x,y])=>{var e=document.elementFromPoint(x,y);"
       " return !!(e && e.closest('.nbmap-node')===window.__fl.nodes()[i]);}")

def click_mark(pg, i, count=1):
    # 2026-09-27g — "on screen" is not "clickable": since 27f a click lands the
    # mark on the reading line, and a mark near the top can sit UNDER the
    # toolbar (y 142, the click hit .nbdock). Ask the page what the pointer
    # would hit; if it is not this mark, scroll it to the middle first.
    xy = pg.evaluate("(i)=>window.__fl.mid(window.__fl.nodes()[i])", i)
    vh = pg.evaluate("()=>window.innerHeight")
    hit = bool(xy) and pg.evaluate(HIT, [i, xy[0], xy[1]])
    if not hit or xy[1] < 80 or xy[1] > vh - 60:   # the rail scrolls with the page: bring it into view
        pg.evaluate("(d)=>{var s=document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer'); s.scrollTop+=d;}", xy[1] - vh / 2)
        pg.wait_for_timeout(900)
        xy = pg.evaluate("(i)=>window.__fl.mid(window.__fl.nodes()[i])", i)
    pg.mouse.click(xy[0], xy[1], click_count=count)
    return xy

import time as _time
JUMP = 1.4 + 1.5        # landing passes (01-jump) + glide (FINAL 11)
def settle(pg, want, t_click, limit=14.0):
    """after a check: wait until the choice is `want` and the marker sits on
    it (gap <= 1 px, three reads in a row); returns (state, t_choice, t_land)
    in seconds after the click (None where it never came)"""
    t_choice = t_land = None; ok = 0; st = None
    while _time.time() - t_click < limit:
        st = pg.evaluate("()=>window.__fl.state()")
        if st["sel"] == want and t_choice is None: t_choice = _time.time() - t_click
        if st["sel"] == want and st["gap"] is not None and st["gap"] <= 1 and st["here"] == want:
            ok += 1
            if ok == 1: t_land = _time.time() - t_click
            if ok >= 3: break
        else:
            ok = 0; t_land = None
        pg.wait_for_timeout(100)
    return st, t_choice, t_land

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    ctx, pg, errs = fresh(b, BASE, nb, ROOT)
    MOD = kexec("print('_Q1' in globals())").strip() == "True"      # Modeling's exercise 1
    # E28 (2026-10-12): the template's exercise 1 is y = a·3, coding 1 y_von(a, x)
    # (behauptete bisher: Complex or Modeling — on the Vorlage "name '_q' is not defined")
    VOR = kexec("print('y_von' in str(_TASKS.get('order')) or ('_a' in globals() and '_q' not in globals() and '_Q1' not in globals()))").strip() == "True"
    pg.add_script_tag(content=LIB)
    if skin:
        pg.evaluate("(s)=>{try{window.__nbStore.set('digichemjn.skin.v1', s);}catch(e){} window.__nbApplySkin && window.__nbApplySkin();}", skin)
        pg.wait_for_timeout(2500)
    res["skin"] = pg.evaluate("()=>(document.body.className.match(/nbskin-[a-z]+/)||['nbskin-(none)'])[0]")
    ch1 = pg.evaluate("()=>window.__fl.idx('.chap')")
    ch2 = pg.evaluate("()=>{var n=window.__fl.nodes(), k=0; for (var i=0;i<n.length;i++) if (n[i].classList.contains('chap') && ++k===2) return i; return -1;}")
    t1 = pg.evaluate("()=>window.__fl.idx('.task','t1')")
    c1 = pg.evaluate("()=>window.__fl.idx('.codetask','t1')")
    ids = pg.evaluate("()=>window.__fl.nodes().map(function(n){return n.getAttribute('data-target');})")

    # ---- A: toggle ------------------------------------------------------
    A = []
    for step in range(3):
        click_mark(pg, ch1); pg.wait_for_timeout(1800)
        A.append({"open": pg.evaluate("(i)=>window.__fl.open(i)", ids[ch1]), **pg.evaluate("()=>window.__fl.state()")})
    click_mark(pg, ch1, 2); pg.wait_for_timeout(1500)
    A.append({"dbl": True, "open": pg.evaluate("(i)=>window.__fl.open(i)", ids[ch1])})
    res["A"] = A
    if [a["open"] for a in A[:3]] != [True, False, True]:
        fails.append("A toggle: chapter 1 open after clicks 1/2/3 = %s, want True/False/True" % [a["open"] for a in A[:3]])
    if A[0]["sel"] != ch1: fails.append("A: the first click did not choose chapter 1")
    if A[3]["open"] is not True: fails.append("A: a double click folded the chapter")

    # ---- B: code route, real hands ---------------------------------------
    click_mark(pg, c1); pg.wait_for_timeout(1800)
    b0 = {"codeOpen": pg.evaluate("(i)=>window.__fl.open(i)", ids[c1]), "ch1Open": pg.evaluate("(i)=>window.__fl.open(i)", ids[ch1])}
    n = pg.evaluate("(i)=>window.__fl.tag(i,'.codearea textarea','ta')", ids[c1])
    pg.evaluate("(i)=>window.__fl.tag(i,'button','bt')", ids[c1])
    btn = pg.evaluate("(i)=>{var c=window.__fl.acc(i); var bs=c.querySelectorAll('button'); for (var k=0;k<bs.length;k++) if (/Check input/.test(bs[k].textContent)) return bs[k].getAttribute('data-fl'); return null;}", ids[c1])
    pg.fill('[data-fl="ta0"]', ("import numpy as np\n\ndef orders(t_fast_ms, t_slow_h):\n"
                                 "    return float(np.log10(t_slow_h * 3600 * 1000 / t_fast_ms))\n") if MOD else
                                "def y_von(a, x):\n    return a * x\n" if VOR else
                                "import numpy as np\n\ndef roots_of(q):\n    r = np.sqrt(q)\n    return (1j*r, -1j*r)\n")
    pg.click('[data-fl="%s"]' % btn); tb = _time.time()
    sb, tbc, tbl = settle(pg, ch2, tb)
    pg.wait_for_timeout(300)
    B = dict(b0, codeFoldAfter=pg.evaluate("(i)=>window.__fl.open(i)", ids[c1]),
             ch2Open=pg.evaluate("(i)=>window.__fl.open(i)", ids[ch2]),
             mark=pg.evaluate("(i)=>window.__fl.node(i)", c1), t_choice=tbc and round(tbc, 2), t_land=tbl and round(tbl, 2),
             **pg.evaluate("()=>window.__fl.state()"))
    res["B"] = B
    if not b0["codeOpen"]: fails.append("B: coding 1 did not open for the reader")
    if "cd-done" not in B["mark"]["mark"] or B["mark"]["dc"] != "done":
        fails.append("B: coding 1 not drawn solved (%s, data-cstate=%s)" % (B["mark"]["mark"], B["mark"]["dc"]))
    if B["codeFoldAfter"]: fails.append("B: the solved coding fold stayed open")
    if not B["ch2Open"]: fails.append("B: chapter 2 did not open")
    if B["cdCurrent"] != ["t2"]: fails.append("B: the purple door is on %s, want t2" % B["cdCurrent"])
    if B["sel"] != ch2: fails.append("B: the move went to mark %s, want chapter 2 (%s)" % (B["sel"], ch2))
    if B["gap"] is None or B["gap"] > 1: fails.append("B: |marker - choice| = %s px" % B["gap"])
    if tbc is None or tbl is None or tbl - tbc > JUMP:
        fails.append("B: the jump took %s s from the choice (%s) to the landing (%s), want <= %.1f s" % (
            tbl and tbc and round(tbl - tbc, 2), B["t_choice"], B["t_land"], JUMP))

    # ---- C: answer route, real hands --------------------------------------
    q = kexec("print(_Q1)" if MOD else "print(3 * _a)" if VOR else "print(_q)").strip()
    click_mark(pg, t1); pg.wait_for_timeout(1800)
    c0 = {"pracOpen": pg.evaluate("(i)=>window.__fl.open(i)", ids[t1]),
          "selBefore": pg.evaluate("()=>window.__fl.state().sel")}
    pg.evaluate("(i)=>window.__fl.tag(i,'.widget-text input','in')", ids[t1])
    if MOD or VOR:
        pg.fill('[data-fl="in0"]', "%.4f" % float(q))
    else:
        pg.fill('[data-fl="in0"]', "0"); pg.fill('[data-fl="in1"]', "%.6f" % (float(q) ** 0.5))
    pg.keyboard.press("Tab")
    btn = pg.evaluate("(i)=>{var c=window.__fl.acc(i); var bs=c.querySelectorAll('button'); for (var k=0;k<bs.length;k++) if (/Check answer/.test(bs[k].textContent)) { bs[k].setAttribute('data-fl','chk'); return 'chk'; } return null;}", ids[t1])
    pg.click('[data-fl="chk"]'); tc = _time.time()
    sc_, tcc, tcl = settle(pg, ch2, tc)
    pg.wait_for_timeout(300)
    C = dict(c0, pracAfter=pg.evaluate("(i)=>window.__fl.open(i)", ids[t1]), t_choice=tcc and round(tcc, 2), t_land=tcl and round(tcl, 2),
             mark=pg.evaluate("(i)=>window.__fl.node(i)", t1),
             kernel=kexec("print(_TASKS['state']['t1'], _TASKS['code']['t1'])").strip(),
             **pg.evaluate("()=>window.__fl.state()"))
    res["C"] = C
    if not c0["pracOpen"]: fails.append("C: exercise 1 did not open for the reader")
    if C["mark"]["ds"] != "done": fails.append("C: exercise 1 data-state=%s (kernel %s)" % (C["mark"]["ds"], C["kernel"]))
    if C["pracAfter"]: fails.append("C: the answered exercise stayed open")
    if C["selBefore"] != t1: fails.append("C: clicking exercise 1 did not choose it (%s)" % C["selBefore"])
    if C["sel"] != ch2: fails.append("C: the move went to mark %s, want chapter 2 (%s)" % (C["sel"], ch2))
    if C["gap"] is None or C["gap"] > 1: fails.append("C: |marker - choice| = %s px" % C["gap"])
    if tcc is None or tcl is None or tcl - tcc > JUMP:
        fails.append("C: the jump took %s s from the choice (%s) to the landing (%s), want <= %.1f s" % (
            tcl and tcc and round(tcl - tcc, 2), C["t_choice"], C["t_land"], JUMP))

    # ---- D: the other two states on the purple lane -----------------------
    c2 = pg.evaluate("()=>window.__fl.idx('.codetask','t2')"); c3 = pg.evaluate("()=>window.__fl.idx('.codetask','t3')")
    lk3 = kexec("print(_LOCKS[('chapter','t2')]['open'])").strip()
    # 2026-10-04 (E21 Rest Stufe 2, JS — Prüfwerkzeug) — BEHAUPTETE BISHER: both
    # states are drawn 2.5 s after the kernel call. The page learns them from the
    # kernel's feed (a display update) and draws them on its next sync; in the
    # gate (stage 2 after a full stage 1, one CPU) "coding 3 wrong not drawn" at
    # 2.5 s on Complex AND Modeling (Hauptwerkstatt 04.10.), green alone. Now
    # read until both are drawn, at most 8 s, and report the time (`t_D`); a
    # state that never comes is still red.
    import time as _t
    kexec("task_code_skipped('t2'); task_wrong('t3','code')"); _t0 = _t.time()
    for _ in range(80):
        pg.wait_for_timeout(100)
        _a = pg.evaluate("(i)=>window.__fl.node(i)", c2); _b = pg.evaluate("(i)=>window.__fl.node(i)", c3)
        if "cd-skip" in _a["mark"] and _a["dc"] == "skip" and "cd-fail" in _b["mark"] and _b["dc"] == "fail": break
    t_D = round(_t.time() - _t0, 2)
    pg.wait_for_timeout(500)
    D = {"c2": pg.evaluate("(i)=>window.__fl.node(i)", c2), "c3": pg.evaluate("(i)=>window.__fl.node(i)", c3),
         "ch3lockBefore": lk3, "ch3lockAfter": kexec("print(_LOCKS[('chapter','t2')]['open'])").strip(), "t_D": t_D}
    res["D"] = D
    if "cd-skip" not in D["c2"]["mark"] or D["c2"]["dc"] != "skip": fails.append("D: coding 2 skip not drawn (%s)" % D["c2"])
    if "cd-fail" not in D["c3"]["mark"] or D["c3"]["dc"] != "fail": fails.append("D: coding 3 wrong not drawn (%s)" % D["c3"])
    if D["ch3lockAfter"] != D["ch3lockBefore"]: fails.append("D: skipping code opened chapter 3")

    # ---- E: a run is not an answer ----------------------------------------
    s0 = pg.evaluate("()=>window.__fl.state()")
    pg.evaluate("()=>{var s=document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer'); s.scrollTop=0;}")
    pg.click(".lm-DockPanel .lm-TabBar-tab.lm-mod-current"); pg.keyboard.press("Escape")
    pg.keyboard.press("Control+Shift+C")
    pg.wait_for_function("() => { var i = document.activeElement; return !!(i && i.classList && i.classList.contains('lm-CommandPalette-input')); }", timeout=8000)
    pg.keyboard.type("Run All Cells")
    pg.wait_for_function("() => { var a = document.querySelector('.lm-CommandPalette-item.lm-mod-active .lm-CommandPalette-itemLabel'); return !!(a && a.textContent.trim() === 'Run All Cells'); }", timeout=8000)
    pg.keyboard.press("Enter")
    for _ in range(90):
        pg.wait_for_timeout(1000)
        st = pg.evaluate("() => (document.querySelector('.jp-Notebook-ExecutionIndicator')||{getAttribute:()=>null}).getAttribute('data-status')")
        if st == "idle": break
    pg.wait_for_timeout(1500)
    e0 = pg.evaluate("()=>window.__fl.state()")
    pg.wait_for_timeout(4000)
    e1 = pg.evaluate("()=>window.__fl.state()")
    E = {"before": s0, "afterRun": e0, "later": e1,
         "restored": pg.evaluate("(i)=>window.__fl.node(i)", c1),
         "kernel": kexec("print(_TASKS['state']['t1'], _TASKS['code']['t1'])").strip()}
    res["E"] = E
    if E["kernel"] != "done done": fails.append("E: progress not back after the run (%s)" % E["kernel"])
    if e1["st"] != e0["st"] or e1["sel"] != e0["sel"]: fails.append("E: the panel moved after the run (%s -> %s)" % (e0, e1))
    sp = pg.evaluate("""()=>{var h=document.getElementById('nbpanel-root'), map=h.querySelector('.nbmap'),
        line=map.getBoundingClientRect().top+(parseInt(h.dataset.railY0||'0',10)||0),
        n=[].slice.call(h.querySelectorAll('.nbmap-node')), ti=n.findIndex(function(x){return x.classList.contains('title');}),
        m=ti>=0?n[ti].querySelector('.nbsect,.nbsubdot,.nbchapdot,.nbvizmark,.nbrail-dot,.nbcodemark,.nbendmark,.nbcellmark'):null, r=m?m.getBoundingClientRect():null,
        hm=h.querySelector('.nbmap-here'), hr=hm?hm.getBoundingClientRect():null;
      return {title: ti, topAt: Math.round(window.__nbTopAt||0), line: line,
              titleOff: r ? Math.round((r.top+r.height/2-line)*10)/10 : null,
              markerOff: hr ? Math.round((hr.top+hr.height/2-line)*10)/10 : null};}""")
    E["spawn"] = sp
    if e0["st"] != sp["topAt"]: fails.append("E: after the run the document is at %s, the spawn (title) is %s" % (e0["st"], sp["topAt"]))
    if sp["topAt"] != 0 or e0["st"] != 0: fails.append("E: spawn at scrollTop %s / __nbTopAt %s — E12.2: no air, the title at 0" % (e0["st"], sp["topAt"]))
    if e0["here"] != sp["title"]: fails.append("E: after the run the lit mark is %s, not the title %s" % (e0["here"], sp["title"]))
    if sp["titleOff"] is None or abs(sp["titleOff"]) > 2: fails.append("E: title mark %s px from the line" % sp["titleOff"])
    if sp["markerOff"] is None or abs(sp["markerOff"]) > 2: fails.append("E: marker %s px from the line" % sp["markerOff"])
    res["errors"] = errs
    if errs: fails.append("console: %s" % errs[:3])
    ctx.close(); b.close()

res["fails"] = fails
json.dump(res, open(out, "w"), indent=1)
print("skin:", res.get("skin"))
for k in "ABCDE":
    print(k, json.dumps(res.get(k))[:600])
print("FLOW OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
sys.exit(1 if fails else 0)
