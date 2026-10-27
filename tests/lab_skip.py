"""Real-JupyterLab measurement for K1 (APPLIKATION §8b) — skipping happens only
at the exercise, and a task that waits does not unfold. 2026-09-28a.

NOT a suite: it needs a running `jupyter lab` (see lab_keys.py). A fresh copy
of the notebook, the reader's own mouse and keyboard, and DOM / class /
getBoundingClientRect reads:

  S  NO SKIP OUTSIDE THE EXERCISE — every button or control in the page whose
     text says skip (or that is one of the old ways: the hidden "open chapter
     only", the key in the lock window, the gear drawer's lock slot) is
     counted, and where it sits: inside an exercise fold (.acc-practice /
     .acc-code) or not. Outside must be 0. A click on a locked chapter mark
     arms nothing and opens no lock window.
  K  "SKIP FOR NOW" IS THE SKIP — pressed with the mouse in exercise 1: the
     mark goes amber (data-state=skip, st-skip), chapter 2 is no longer
     locked, and exercise 2 opens from the timeline.
     (Marks are brought into view with the mouse wheel over the document, as
     a reader does — not with scrollTop, which a running landing undoes.)
  L  A WAITING TASK DOES NOT UNFOLD — coding 2 waits for coding 1: a mouse
     click on its pill in the document, a click on its mark on the timeline,
     and Enter on it in the panel's keyboard mode all leave it shut, sampled
     at 80/300/800/1500 ms (no flash), and Enter puts the focus in no field.
  M  …AND IT OPENS ONCE THE ONE BEFORE IS ANSWERED — coding 1 typed wrong and
     checked (red, cd-fail): now a click on coding 2's mark unfolds it.

    python3 tests/lab_skip.py <notebook> <out.json> [skin]
Exit 1 if a criterion fails."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import fresh, CHROME, to_panel
from lab_marks import kexec
from playwright.sync_api import sync_playwright
BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
ROOT = os.environ.get("DIGICHEM_LAB_ROOT", "/home/claude/lab/root")
nb, out = sys.argv[1], sys.argv[2]
skin = sys.argv[3] if len(sys.argv) > 3 else None
MK = '.nbsect,.nbsubdot,.nbchapdot,.nbvizmark,.nbrail-dot,.nbcodemark'
LIB = r"""
window.__sk = {
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
  node: function(i){ var n = this.nodes()[i]; return {cls: n.className, target: n.getAttribute('data-target'),
      task: n.getAttribute('data-task'), ds: n.getAttribute('data-state'), dc: n.getAttribute('data-cstate'),
      mark: (n.querySelector('.nbcodemark,.nbrail-dot') || {}).className || ''}; },
  skips: function(){
    // every control that is a way to skip, and where it lives
    var out = [], seen = new Set();
    var add = function(e, why){ if (seen.has(e)) return; seen.add(e);
      var r = e.getBoundingClientRect();
      var box = e.closest('.acc-practice, .acc-code');
      out.push({why: why, text: (e.textContent || '').trim().slice(0, 40),
                inTask: !!box, inPanel: !!e.closest('#nbpanel-root'),
                shown: r.width > 0 && r.height > 0}); };
    document.querySelectorAll('button, [role=button], .jupyter-button').forEach(function(e){
      if (/skip|open chapter only/i.test(e.textContent || '')) add(e, 'text'); });
    document.querySelectorAll('.nbunlock-chap, .nbwinkey, .nbctl-unl, [data-slot="nbctl-unl"], .nblock-slot, .pg-lock')
      .forEach(function(e){ add(e, 'old'); });
    return out; },
  armed: function(){ var h = document.getElementById('nbpanel-root');
    return {keyed: document.querySelectorAll('.nbkeyed').length,
            lockPage: !!(h && h.dataset.page === 'lock' && h.classList.contains('open'))}; },
  scrollTo: function(el){ var s = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer');
    var r = el.getBoundingClientRect(), sr = s.getBoundingClientRect();
    s.scrollTop += (r.top - sr.top) - sr.height / 2; }
};
""".replace("%MK%", MK)
res = {}; fails = []
HIT = ("([i,x,y])=>{var e=document.elementFromPoint(x,y);"
       " return !!(e && e.closest('.nbmap-node')===window.__sk.nodes()[i]);}")

def click_mark(pg, i, count=1):
    xy = pg.evaluate("(i)=>window.__sk.mid(window.__sk.nodes()[i])", i)
    vh = pg.evaluate("()=>window.innerHeight")
    hit = bool(xy) and pg.evaluate(HIT, [i, xy[0], xy[1]])
    # E10 Schritt C (01.10.): the READER's wheel brings the mark into view, over
    # the document. Until v1.45 a script set scrollTop: that is no input, so a
    # landing still running (the move-on after "Skip for now", passes up to
    # 1.4 s after the kernel answers) re-aimed the page back over it — by
    # design (01-jump landArm: only input ends a landing) — and the click hit
    # below the window (v1.45: 2 of 7 runs, "Aufgabe 2 öffnet nicht").
    for _ in range(3):
        if hit and 80 <= xy[1] <= vh - 60: break
        pg.mouse.move(700, vh / 2)
        pg.mouse.wheel(0, (xy[1] if xy else vh / 2) - vh / 2)
        last = None
        for _ in range(16):                 # until the glide has come to rest
            pg.wait_for_timeout(150)
            xy = pg.evaluate("(i)=>window.__sk.mid(window.__sk.nodes()[i])", i)
            if xy and last and abs(xy[1] - last[1]) < 0.5: break
            last = xy
        hit = bool(xy) and pg.evaluate(HIT, [i, xy[0], xy[1]])
    if not xy: return None
    pg.mouse.click(xy[0], xy[1], click_count=count)
    return xy

def samples(pg, tid):
    got = []
    for ms in (80, 220, 500, 700):          # cumulative: 80 / 300 / 800 / 1500 ms
        pg.wait_for_timeout(ms)
        got.append(pg.evaluate("(i)=>window.__sk.open(i)", tid))
    return got

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    ctx, pg, errs = fresh(b, BASE, nb, ROOT)
    pg.add_script_tag(content=LIB)
    if skin:
        pg.evaluate("(s)=>{try{window.__nbStore.set('digichemjn.skin.v1', s);}catch(e){} window.__nbApplySkin && window.__nbApplySkin();}", skin)
        pg.wait_for_timeout(2500)
    res["skin"] = pg.evaluate("()=>(document.body.className.match(/nbskin-[a-z]+/)||['nbskin-(none)'])[0]")
    ids = pg.evaluate("()=>window.__sk.nodes().map(function(n){return n.getAttribute('data-target');})")
    ch2 = pg.evaluate("()=>{var n=window.__sk.nodes(), k=0; for (var i=0;i<n.length;i++) if (n[i].classList.contains('chap') && ++k===2) return i; return -1;}")
    ch3 = pg.evaluate("()=>{var n=window.__sk.nodes(), k=0; for (var i=0;i<n.length;i++) if (n[i].classList.contains('chap') && ++k===3) return i; return -1;}")
    t1 = pg.evaluate("()=>window.__sk.idx('.task','t1')")
    t2 = pg.evaluate("()=>window.__sk.idx('.task','t2')")
    c1 = pg.evaluate("()=>window.__sk.idx('.codetask','t1')")
    c2 = pg.evaluate("()=>window.__sk.idx('.codetask','t2')")

    # ---- S: no skip outside the exercise ---------------------------------
    s0 = pg.evaluate("()=>window.__sk.skips()")
    click_mark(pg, ch3); pg.wait_for_timeout(1500)       # a LOCKED chapter mark
    arm = pg.evaluate("()=>window.__sk.armed()")
    note = pg.evaluate("""(i)=>{var c=window.__sk.acc(i); var n=c&&c.querySelector('.nblocked-note');
        return n ? (n.textContent||'').replace(/\\s+/g,' ').trim() : null;}""", ids[ch3])
    s1 = pg.evaluate("()=>window.__sk.skips()")
    click_mark(pg, t1); pg.wait_for_timeout(1800)         # exercise 1 open: its own button shows
    s2 = pg.evaluate("()=>window.__sk.skips()")
    S = {"fresh": s0, "afterLockedClick": s1, "exercise1Open": s2, "armed": arm, "ch3note": note}
    res["S"] = S
    for tag, lst in (("fresh", s0), ("after a click on a locked chapter", s1), ("with exercise 1 open", s2)):
        outside = [x for x in lst if not x["inTask"]]
        if outside: fails.append("S: %d skip controls outside an exercise (%s): %s" % (len(outside), tag, outside[:3]))
    if arm["keyed"] or arm["lockPage"]: fails.append("S: a click on a locked chapter armed a key / opened the lock window (%s)" % arm)
    shown = [x for x in s2 if x["inTask"] and x["shown"]]
    if len(shown) != 1 or "Skip for now" not in shown[0]["text"]:
        fails.append("S: exercise 1 open shows %d skip controls, want 1 'Skip for now' (%s)" % (len(shown), shown))

    # ---- K: the button is the skip ---------------------------------------
    kb = {"ch2Before": pg.evaluate("(i)=>window.__sk.node(i).cls", ch2),
          "kernelBefore": kexec("print(_TASKS['state']['t1'], _LOCKS[('chapter','t1')]['open'], _LOCKS[('practice','t1')]['open'])").strip()}
    has = pg.evaluate("""(i)=>{var c=window.__sk.acc(i); var bs=c.querySelectorAll('button');
        for (var k=0;k<bs.length;k++) if (/Skip for now/.test(bs[k].textContent)) { bs[k].setAttribute('data-sk','skip'); window.__sk.scrollTo(bs[k]); return true; } return false;}""", ids[t1])
    pg.wait_for_timeout(600)
    if has:
        pg.click('[data-sk="skip"]')                      # the reader's mouse
    else:
        # no button at the exercise (a build before 28a): record it, and set the
        # same state from the kernel so L and M still measure something
        fails.append("K: exercise 1 has no 'Skip for now' button")
        kexec("task_skipped('t1')")
    kb["button"] = has
    pg.wait_for_timeout(3000)
    K = dict(kb, mark=pg.evaluate("(i)=>window.__sk.node(i)", t1),
             ch2After=pg.evaluate("(i)=>window.__sk.node(i).cls", ch2),
             kernel=kexec("print(_TASKS['state']['t1'], _LOCKS[('chapter','t1')]['open'], _LOCKS[('practice','t1')]['open'])").strip())
    click_mark(pg, t2); pg.wait_for_timeout(1800)
    K["ex2Open"] = pg.evaluate("(i)=>window.__sk.open(i)", ids[t2])
    res["K"] = K
    if K["mark"]["ds"] != "skip" or "st-skip" not in K["mark"]["mark"]:
        fails.append("K: 'Skip for now' did not draw exercise 1 amber (%s)" % K["mark"])
    if K["kernel"] != "skip True True": fails.append("K: kernel after 'Skip for now': %s, want 'skip True True'" % K["kernel"])
    if " locked" in (" " + K["ch2After"] + " "): fails.append("K: chapter 2 still drawn locked (%s)" % K["ch2After"])
    if K["ex2Open"] is not True: fails.append("K: exercise 2 did not open from the timeline after the skip (%s)" % K["ex2Open"])

    # ---- L: a waiting task does not unfold --------------------------------
    L = {"c2": pg.evaluate("(i)=>window.__sk.node(i)", c2),
         "tasklock": pg.evaluate("(i)=>{var c=window.__sk.acc(i); return !!(c && c.closest('.acc-tasklock'));}", ids[c2]),
         "kernel": kexec("print(_TASKS['code']['t1'], _LOCKS[('code','t1')]['open'])").strip()}
    # (i) the reader clicks the pill in the document
    hd = pg.evaluate("""(i)=>{var c=window.__sk.acc(i); if(!c) return null; var h=c.querySelector('.jupyter-widget-Collapse-header');
        window.__sk.scrollTo(h); return true;}""", ids[c2])
    pg.wait_for_timeout(700)
    xy = pg.evaluate("""(i)=>{var h=window.__sk.acc(i).querySelector('.jupyter-widget-Collapse-header'); var r=h.getBoundingClientRect();
        return [r.left + Math.min(60, r.width/2), r.top + r.height/2];}""", ids[c2])
    hitHdr = pg.evaluate("""([i,x,y])=>{var e=document.elementFromPoint(x,y); var h=window.__sk.acc(i).querySelector('.jupyter-widget-Collapse-header');
        return !!(e && h.contains(e));}""", [ids[c2], xy[0], xy[1]])
    pg.mouse.click(xy[0], xy[1])
    L["docClick"] = {"hit": hitHdr, "open": samples(pg, ids[c2])}
    # (ii) the timeline
    click_mark(pg, c2)
    L["railClick"] = {"open": samples(pg, ids[c2]), "sel": pg.evaluate("(i)=>window.__sk.nodes()[i].classList.contains('nbsel')", c2)}
    # (iii) the keyboard: panel mode, walk to coding 2, Enter
    L["toPanel"] = to_panel(pg)
    walk = []
    for _ in range(70):
        at = pg.evaluate("()=>window.__nbKeyAt")
        tgt = pg.evaluate("(a)=>{var ns=[].slice.call(document.querySelectorAll('#nbpanel-root .nbmap-node')).filter(function(n){return !n.classList.contains('nbgone');}); return a!=null && ns[a] ? ns[a].getAttribute('data-target') : null;}", at)
        walk.append(tgt)
        if tgt == ids[c2]: break
        want = pg.evaluate("(t)=>[].slice.call(document.querySelectorAll('#nbpanel-root .nbmap-node')).filter(function(n){return !n.classList.contains('nbgone');}).map(function(n){return n.getAttribute('data-target');}).indexOf(t)", ids[c2])
        cur = at if at is not None else pg.evaluate("()=>{var ns=[].slice.call(document.querySelectorAll('#nbpanel-root .nbmap-node')).filter(function(n){return !n.classList.contains('nbgone');}); for (var j=0;j<ns.length;j++) if (ns[j].classList.contains('here')) return j; return -1;}")
        pg.keyboard.press("j" if cur < want else "k"); pg.wait_for_timeout(350)
    L["keyOn"] = walk[-1] == ids[c2]
    ae0 = pg.evaluate("()=>document.activeElement ? document.activeElement.tagName : null")
    pg.keyboard.press("Enter")
    L["enter"] = {"open": samples(pg, ids[c2]) + [pg.wait_for_timeout(700) or pg.evaluate("(i)=>window.__sk.open(i)", ids[c2])],
                  "focus": pg.evaluate("()=>{var a=document.activeElement; return a ? (a.tagName + (a.closest('#nbpanel-root') ? ' in panel' : ' in document')) : null;}"),
                  "before": ae0}
    pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
    L["kernelAfter"] = kexec("print(_TASKS['code']['t1'], _LOCKS[('code','t1')]['open'])").strip()
    res["L"] = L
    if not L["tasklock"]: fails.append("L: coding 2 waits for coding 1 but is not marked acc-tasklock")
    if L["kernel"] != "open False": fails.append("L: precondition — coding 1 is %s" % L["kernel"])
    if not L["docClick"]["hit"]: fails.append("L: the document click did not reach coding 2's pill")
    for way in ("docClick", "railClick", "enter"):
        if any(v is not False for v in L[way]["open"]):
            fails.append("L: %s unfolded the waiting coding 2 (%s)" % (way, L[way]["open"]))
    if not L["keyOn"]: fails.append("L: the keyboard never stood on coding 2 (%s)" % walk[-5:])
    if L["enter"]["focus"] and ("INPUT" in L["enter"]["focus"] or "TEXTAREA" in L["enter"]["focus"]):
        fails.append("L: Enter on the waiting coding 2 put the focus in a field (%s)" % L["enter"]["focus"])
    if L["kernelAfter"] != "open False": fails.append("L: coding 1 changed on the way (%s)" % L["kernelAfter"])

    # ---- M: it opens once the one before is answered (wrong, by hand) ------
    click_mark(pg, c1); pg.wait_for_timeout(1800)
    m0 = pg.evaluate("(i)=>window.__sk.open(i)", ids[c1])
    pg.evaluate("""(i)=>{var c=window.__sk.acc(i); var t=c.querySelector('.codearea textarea, textarea'); t.setAttribute('data-sk','ta');
        var bs=c.querySelectorAll('button'); for (var k=0;k<bs.length;k++) if (/Check input/.test(bs[k].textContent)) bs[k].setAttribute('data-sk','chk');}""", ids[c1])
    pg.fill('[data-sk="ta"]', "def roots_of(q):\n    return (q, -q)\n")
    # 2026-10-04 (E21 Rest Stufe 2, JS — Prüfwerkzeug) — BEHAUPTETE BISHER: 3.5 s
    # after "Check" the kernel has graded, the page has drawn coding 1 red and
    # lifted coding 2's wait (acc-tasklock). Grading takes 1.8–2.4 s on one CPU
    # (lab_flow), the page draws on its next sync; in the gate (stage 2 after a
    # full stage 1) M was red on Modeling, green alone 2 of 2 (Hauptwerkstatt
    # 04.10.) — and a click on coding 2 BEFORE the page knows the wait is over
    # is rightly refused. Now: until coding 1 is drawn red and coding 2 has no
    # wait, at most 10 s (reported as `t_M`); then the click as before.
    import time as _t
    pg.click('[data-sk="chk"]'); _t0 = _t.time()
    for _ in range(100):
        pg.wait_for_timeout(100)
        _n = pg.evaluate("(i)=>window.__sk.node(i)", c1)
        _w = pg.evaluate("(i)=>{var c=window.__sk.acc(i); return !!(c && c.closest('.acc-tasklock'));}", ids[c2])
        if "cd-fail" in _n["mark"] and not _w: break
    t_M = round(_t.time() - _t0, 2)
    pg.wait_for_timeout(300)
    M = {"t_M": t_M, "code1Open": m0, "c1": pg.evaluate("(i)=>window.__sk.node(i)", c1),
         "kernel": kexec("print(_TASKS['code']['t1'], _LOCKS[('code','t1')]['open'])").strip(),
         "tasklock": pg.evaluate("(i)=>{var c=window.__sk.acc(i); return !!(c && c.closest('.acc-tasklock'));}", ids[c2])}
    click_mark(pg, c2); pg.wait_for_timeout(1800)
    M["c2Open"] = pg.evaluate("(i)=>window.__sk.open(i)", ids[c2])
    res["M"] = M
    if M["kernel"] != "fail True": fails.append("M: coding 1 wrong -> kernel %s, want 'fail True'" % M["kernel"])
    if "cd-fail" not in M["c1"]["mark"]: fails.append("M: coding 1 not drawn red (%s)" % M["c1"])
    if M["tasklock"]: fails.append("M: coding 2 still marked acc-tasklock")
    if M["c2Open"] is not True: fails.append("M: coding 2 does not unfold after coding 1 was answered (%s)" % M["c2Open"])
    res["errors"] = errs
    if errs: fails.append("console: %s" % errs[:3])
    ctx.close(); b.close()

res["fails"] = fails
json.dump(res, open(out, "w"), indent=1)
print("skin:", res.get("skin"))
for k in "SKLM":
    print(k, json.dumps(res.get(k))[:700])
print("SKIP OK" if not fails else "FAILURES:\n- " + "\n- ".join(fails))
sys.exit(1 if fails else 0)
