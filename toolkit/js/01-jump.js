(function(){
  // 2026-10-06 (Nach-Runde v1.65, Applikation) — THE QUIZ'S MATHJAX CHECK,
  // ALSO WHEN MATHJAX COMES LATE. The page error "Cannot read properties of
  // undefined (reading '0')" (test_regress, tor rows after a reload; Werkstatt
  // CSS: 2 of ~12 first runs) is not ours and not patch(): measured with the
  // debugger (Runtime.exceptionThrown → Debugger.getScriptSource), v1.65,
  // cyber dark, save + reload, 4 of 4: jupyterquiz's script, line 783 —
  // `if (version[0] == "2")` 500 ms after a quiz is drawn, `version` =
  // `MathJax.version`. The guard of 2026-09-24be (chapter_template.py) gives
  // JupyterLab's MathJax loader the no-op `typeset` (and a version) the quiz
  // judges it by — but only if `window.MathJax` is there when that output
  // runs. On a reload (and on a cold first run) it is not yet: JupyterLab sets
  // it up a moment later, the first quiz finds no `typeset`, replaces
  // `window.MathJax` with a bare config object (no version), and the next
  // quiz reads `version[0]` of undefined. Now the same guard looks again
  // every 50 ms for the first 60 s after this script runs (no layout, one
  // property read): whenever `window.MathJax` is there without `typeset` or
  // without `version`, it gets them — before any quiz's 500-ms check.
  // MathJax itself, once loaded, sets its real `typeset` over ours.
  (function(){
    var t0 = Date.now();
    var mj = function(){
      var M = window.MathJax;
      if (M && (typeof M.typeset !== 'function' || !M.version)) {
        try { if (typeof M.typeset !== 'function') M.typeset = function(){}; if (!M.version) M.version = '3.0.0'; } catch (e) {}
      }
      if (Date.now() - t0 < 60000) setTimeout(mj, 50);
    };
    mj();
  })();
  // py-E23.1 (2026-10-06, Inhalt) — THE PAGE'S OWN WORDS IN THE READER'S
  // LANGUAGE. German when the run in front was built German (its feed says
  // data-nblang), else as the reader chose it (digichemjn.lang.v1); looked up
  // at most every 500 ms (the rail asks in its passes). The rail's L(en, de)
  // helpers (nbL, 11-rail-layout) ask this.
  var deC = {t: 0, v: false};
  window.__nbDe = function(){
    var t = Date.now();
    if (t - deC.t < 500) return deC.v;
    var v = null;
    try {
      var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)') || document;
      var f = P.querySelector('.nbfeed[data-nblang]');
      if (f) v = f.getAttribute('data-nblang') === 'de';
    } catch (e) {}
    if (v === null) { try { v = !!window.__nbStore && window.__nbStore.get('digichemjn.lang.v1') === 'de'; } catch (e) { v = false; } }   // E25.o
    deC.t = t; deC.v = v;
    return v;
  };
  // The jump handler is installed on the DOCUMENT, so the first notebook to run
  // used to install it for the whole page — for good. With several notebooks
  // open in one JupyterLab, that meant the OLDEST script decided how clicking a
  // timeline node behaves, and a fix in a newer notebook never took effect
  // until the page was reloaded. Same rule as the panel's: the newest version
  // wins, and it tears the previous listener down first.
  var JUMP_VERSION = '__JUMPV__';
  // 2026-09-27a — VERSIONS ARE COMPARED AS VERSIONS (D-b). As plain strings
  // '2026-09-24z' > '2026-09-24bi', so from the 27th build of a day on the
  // OLDER script won every handshake. The letters are a number (a=1 … z=26,
  // aa=27, bi=61), padded, so a string compare of the key is right.
  var vkey = window.__nbVKey = function(v){
    v = String(v || '');
    var m = /^(.*?)([a-z]+)$/.exec(v);
    if (!m) return v;
    var n = 0;
    for (var i = 0; i < m[2].length; i++) n = n * 26 + (m[2].charCodeAt(i) - 96);
    return m[1] + '#' + ('000000' + n).slice(-6);
  };
  if (vkey(window.__nbjumpVersion || '') > vkey(JUMP_VERSION)) return;
  if (window.__nbjumpTeardown) { try { window.__nbjumpTeardown(); } catch (e) {} }
  window.__nbjumpVersion = JUMP_VERSION;
  window.__nbjumpInstalled = true;
  var HDR = '.jupyter-widget-Collapse-header,.lm-Collapse-header,.p-Collapse-header';
  var COL = '.jupyter-widget-Collapse,.lm-Collapse,.p-Collapse';
  function isCol(el){return el.classList&&(el.classList.contains('jupyter-widget-Collapse')||el.classList.contains('lm-Collapse')||el.classList.contains('p-Collapse'));}
  function isVbox(el){return el.classList&&(el.classList.contains('widget-vbox')||el.classList.contains('jupyter-widget-vbox'));}
  function isOpen(el){
    if(!el) return true;
    if(el.classList.contains('jupyter-widget-Collapse-open')||el.classList.contains('lm-Collapse-open')||el.classList.contains('p-Collapse-open')) return true;
    var c=el.querySelector('.jupyter-widget-Collapse-contents,.lm-Collapse-contents,.p-Collapse-contents');
    return !!(c && c.offsetHeight>0);
  }
  function expand(el){ if(el && !isOpen(el)){ var h=el.querySelector(HDR); if(h) h.click(); } }

  // Every collapsed accordion between the page and this element, OUTERMOST
  // first. Order matters: the header of a chapter inside a closed group is not
  // laid out, so clicking it is a no-op — the group has to open first.
  function ancestorCols(el){
    var out = [], n = el.parentElement;
    while(n && n !== document.body){ if(isCol(n)) out.push(n); n = n.parentElement; }
    return out.reverse();
  }
  // The accordion an anchor announces. The anchor is NOT followed directly by
  // its chapter — a zero-height progress mirror sits between them — so the walk
  // goes forward until it finds one.
  function chapterAfter(span){
    var host = span;
    while(host.parentElement && !isVbox(host.parentElement)) host = host.parentElement;
    var sib = host ? host.nextElementSibling : null, hops = 0;
    while(sib && hops++ < 8){
      var c = isCol(sib) ? sib : sib.querySelector(COL);
      if(c) return c;
      sib = sib.nextElementSibling;
    }
    return null;
  }
  // A SECTION BAR OPENS ITS SECTION (2026-09-24u).
  // Introduction / Content / Appendix are announced by an anchor that sits
  // BEFORE the group's accordion, not inside it — so ancestorCols() found
  // nothing to open and a click on the bar only scrolled to a closed lid.
  function groupAfter(span){
    var host = span, hops = 0;
    while(host && host !== document.body && hops++ < 8){
      var sib = host.nextElementSibling, k = 0;
      while(sib && k++ < 6){
        var g = (sib.classList && sib.classList.contains('acc-group'))
              ? sib : (sib.querySelector ? sib.querySelector('.acc-group') : null);
        if(g) return isCol(g) ? g : g.querySelector(COL);
        sib = sib.nextElementSibling;
      }
      host = host.parentElement;
    }
    return null;
  }
  // 2026-09-27e — FOLDING, the other half (Applikation F). One helper for
  // both uses: a second click on a chosen chapter folds it (rule a), and a
  // right answer folds the exercise it was given in (rule b). It closes the
  // accordion an anchor announces through its own header — the widget's
  // model follows the click, so the kernel and the page agree.
  function foldAfter(id){
    var span = id && document.getElementById(id);
    var c = span && chapterAfter(span);
    if (c && isOpen(c)) { var h = c.querySelector(HDR); if (h) { h.click(); return true; } }
    return false;
  }
  window.__nbFoldAfter = foldAfter;
  // …and a group bar folds the group it opened (K2.10)
  function foldGroup(id){
    var span = id && document.getElementById(id);
    var g = span && groupAfter(span);
    if (g && isOpen(g)) { var h = g.querySelector(HDR); if (h) { h.click(); return true; } }
    return false;
  }
  // 2026-09-29 (E8.19, Applikation) — THE TITLE FOLDS THE BOOK. A click on
  // the title's mark or on the title card itself shuts everything under it:
  // every chapter (so a group opened again shows its chapters shut), then
  // Introduction, Content and Appendix. Your own cells and "Your own cell"
  // are not folds of the notebook and stay as they are.
  function foldAll(){
    var h = document.getElementById('nbpanel-root');
    if (!h) return 0;
    var n = 0;
    [].forEach.call(h.querySelectorAll('.nbmap-node.chap[data-target]'), function(c){
      if (foldAfter(c.getAttribute('data-target'))) n++; });
    [].forEach.call(h.querySelectorAll('.nbmap-node.sect[data-target]'), function(g){
      if (g.classList.contains('title') || g.classList.contains('end') ||
          g.classList.contains('cell') || g.classList.contains('own')) return;
      if (foldGroup(g.getAttribute('data-target'))) n++; });
    if (window.__nbArmLock) window.__nbArmLock(null);
    return n;
  }
  window.__nbFoldAll = foldAll;
  // 2026-09-30 (E9.5, Struktur + Applikation) — THE TITLE IS AN ACCORDION.
  // Python puts everything between the title card and "Your own cell" into
  // one root accordion (`.acc-title.acc-root`). A click on the title's mark
  // or on the card now shuts THAT, through its own header (the widget's
  // model follows), and the next click opens it again. The chapters inside
  // are not touched, so they come back as they were (E9.6); "Your own cell"
  // (`.acc-yoc`) and the reader's own cells are outside it. A notebook built
  // before E9.5 has no root: the old fold of every chapter (E8.19) remains.
  // 2026-10-02 (E21.1/E21.3, Applikation) — THE NOTEBOOK IN FRONT, NOT THE
  // FIRST ONE. JupyterLab 4.6 marks no `.jp-NotebookPanel` `jp-mod-current`
  // (measured: none of two open), so `current || first in the DOM` took the
  // notebook opened FIRST — with Complex and Modeling open, a click on the
  // title of the one in front shut the title of the one behind it, and the
  // YOC mark made its cell there (reader's video 1; Hauptwerkstatt pair run).
  // With one notebook the first IS the one in front: every suite was green.
  function frontPanel(){
    var ps = document.querySelectorAll('.jp-NotebookPanel'), i;
    var shown = function(p){ return !p.classList.contains('lm-mod-hidden') && !p.classList.contains('p-mod-hidden')
                                    && p.getBoundingClientRect().width > 0; };
    for (i = 0; i < ps.length; i++) if (ps[i].classList.contains('jp-mod-current') && shown(ps[i])) return ps[i];
    for (i = 0; i < ps.length; i++) if (shown(ps[i])) return ps[i];
    return null;
  }
  window.__nbFront = frontPanel;
  function rootAcc(kind, panel){
    var p = panel || frontPanel() || document;
    var r = p.querySelector('.acc-' + kind + '.acc-root');
    return r ? (isCol(r) ? r : r.querySelector(COL)) : null;
  }
  window.__nbRootAcc = rootAcc;
  function titleToggle(open, panel){
    var c = rootAcc('title', panel);
    if (!c) { if (open !== true) foldAll(); return null; }
    var was = isOpen(c);
    if (open === undefined || open !== was) {
      var h = c.querySelector(HDR);
      if (h) h.click();
    }
    if (window.__nbArmLock) window.__nbArmLock(null);
    return !was;
  }
  window.__nbTitleToggle = titleToggle;
  function onTitleCard(ev){
    if (ev.button) return;
    var h = document.getElementById('nbpanel-root');
    var tn = h && h.querySelector('.nbmap-node.title');
    var sel = tn && tn.getAttribute('data-sel');
    if (!sel || !ev.target || !ev.target.closest || ev.target.closest('#nbpanel-root')) return;
    var hit = null;
    sel.split(/\s+/).forEach(function(c){ if (c && !hit) hit = ev.target.closest('.' + c); });
    if (!hit || !hit.closest('.jp-OutputArea')) return;   // the document's card, not the cold cover cell
    if (ev.target.closest('a,button,input,select,textarea,.nbmode')) return;
    titleToggle(undefined, hit.closest('.jp-NotebookPanel'));   // E9.5; E21.1: the card's own notebook
  }
  if (window.__nbTitleFoldOff) { try { window.__nbTitleFoldOff(); } catch (e) {} }
  document.addEventListener('click', onTitleCard, true);
  window.__nbTitleFoldOff = function(){ document.removeEventListener('click', onTitleCard, true); };
  // 2026-10-02 (E21.10, Applikation) — THE HEADING OF A LOCKED CHAPTER OPENS
  // ITS LOCK BOX. Since 24ah the pill of a locked chapter is
  // `pointer-events:none` (05-document: "the door is somewhere else"), so a
  // click on it fell through to the accordion and nothing happened — the
  // reader saw a chapter that answers no click. Now one click inside the
  // pill's box opens the chapter, which while locked holds only the padlock
  // notice ("This chapter is locked …", Python `_lock_shell`), and the next
  // click shuts it. Nothing is unlocked: the notice is all there is behind it.
  function onLockedHead(ev){
    if (ev.button || !ev.target || !ev.target.closest || ev.target.closest('#nbpanel-root')) return;
    var acc = ev.target.closest('.acc-locked');
    if (!acc) return;
    var cs = acc.querySelectorAll(':scope > .jupyter-widget-Collapse, :scope > .lm-Collapse');
    for (var i = 0; i < cs.length; i++) {
      var hd = cs[i].querySelector(':scope > .jupyter-widget-Collapse-header, :scope > .lm-Collapse-header');
      var r = hd && hd.getBoundingClientRect();
      if (r && ev.clientX >= r.left && ev.clientX <= r.right && ev.clientY >= r.top && ev.clientY <= r.bottom) {
        ev.preventDefault(); ev.stopPropagation();
        hd.click();                         // the widget's own toggle; its model follows
        return;
      }
    }
  }
  if (window.__nbLockHeadOff) { try { window.__nbLockHeadOff(); } catch (e) {} }
  document.addEventListener('click', onLockedHead, true);
  window.__nbLockHeadOff = function(){ document.removeEventListener('click', onLockedHead, true); };
  // (not `nbown-…`: ownCells() strips every other class of that prefix)
  function ownFold(cell, shut){
    var inp = cell.querySelector('.jp-Cell-inputWrapper');
    var out = cell.querySelector('.jp-Cell-outputWrapper');
    cell.classList.toggle('nbownshut', shut);
    if (inp) {
      if (shut) { inp.style.setProperty('max-height', '2.3em', 'important');
                  inp.style.setProperty('overflow', 'hidden', 'important'); }
      else { inp.style.removeProperty('max-height'); inp.style.removeProperty('overflow'); }
    }
    if (out) { if (shut) out.style.setProperty('display', 'none', 'important'); else out.style.removeProperty('display'); }
  }
  window.__nbOwnFold = ownFold;
  function openPath(span, isSection){
    ancestorCols(span).forEach(expand);
    if(isSection){
      var g = groupAfter(span);
      if(g) { expand(g); return g; }
    }
    var c = chapterAfter(span);
    if(c) expand(c);
    return c;
  }

  // Where the page scrolls: the notebook's own scroller, not the window.
  function scrollerOf(el){
    var n = el.parentElement;
    while(n && n !== document.body){
      var st = getComputedStyle(n);
      if((st.overflowY === 'auto' || st.overflowY === 'scroll') &&
         n.scrollHeight > n.clientHeight + 4) return n;
      n = n.parentElement;
    }
    return null;
  }
  // The panel floats over the top of the page, so a target that lands at the top
  // of the viewport lands UNDER the panel. Everything is placed just below it.
  function panelBottom(){
    var h = document.getElementById('nbpanel-root');
    if(!h || !h.classList.contains('ready')) return 8;
    // the rail, not the layer: the layer covers the whole window now
    var rail = h.querySelector('.nbrail');
    if(!rail || h.classList.contains('vert')) return 8;
    var r = rail.getBoundingClientRect();
    return (r.height ? r.bottom : 8) + 14;
  }
  // 2026-09-24at — A LANDING THE READER CAN INTERRUPT.
  // A click schedules five landing passes over 1.4 s, because opening an
  // accordion animates and ipywidgets renders a moment later. Every pass wrote
  // scrollTop, so for those 1.4 s the document was pulled back from wherever
  // the reader had scrolled it to: the click left the page stuck.
  //
  // Fewer passes is not the answer — the late ones are what make a click on a
  // deep chapter land at all. What is needed is a pass that knows it is no
  // longer wanted, and the honest signal for that is an INPUT EVENT. Comparing
  // scroll positions between passes looks simpler and is wrong: opening an
  // accordion moves the scroller by itself, so a legitimate landing abandons
  // itself half-way (measured: the target came to rest 72px below the line it
  // was aimed at). A wheel, a drag or a Page-Down key happens only when the
  // reader acts, and nothing in a relayout produces one.
  function landArm(){
    window.__nbLandOff = false;
    if (window.__nbLandArmed) return;
    window.__nbLandArmed = true;
    var stop = function(ev){
      // the click that STARTS a landing must not also end it, and neither must
      // operating the panel itself — the rail is a control, not the document
      if (ev.target && ev.target.closest && ev.target.closest('#nbpanel-root'))
        return;
      if (ev.type === 'keydown' &&
          !/^(Arrow|Page|Home|End|Space| )/.test(ev.key || '')) return;
      window.__nbLandOff = true;
    };
    ['wheel', 'touchmove', 'keydown', 'pointerdown'].forEach(function(t){
      document.addEventListener(t, stop, {capture: true, passive: true});
    });
  }
  // 2026-09-29 (E6.3, Applikation) — ONE KEY, ONE MOVEMENT, ONE TARGET.
  // A jump used to schedule its reopen and landing passes (40 … 1400 ms) and
  // leave them running. K and then J a moment later ran BOTH sets: K's late
  // passes pulled the page back to K's heading, J's pulled it to J's figure —
  // the reader's video showed three changes of direction in two seconds.
  // Every jump now takes a new GENERATION; a pass of an older one does
  // nothing. And a pass no longer sets scrollTop in one go: it hands its
  // target to one glide (the same feel as the wheel, E4.2), which the next
  // jump re-aims instead of starting a second movement next to it.
  var landGen = 0;
  function landNew(){
    landGen = window.__nbLandGen = (window.__nbLandGen || 0) + 1;
    window.__nbGlide = null;                 // the wheel's glide gives way
    return landGen;
  }
  function landLive(g){ return g === window.__nbLandGen; }
  // 2026-10-03 (E21 Rest Stufe 2, Applikation) — THE GLIDE RUNS ON THE
  // CLOCK, NOT ON THE FRAMES. Each frame moved a fifth of what was left
  // (LGLIDE 0.2): 0.4 s at 60 frames a second, but a busy page paints 8–12
  // (the gate's one CPU; Modeling dark on the reader's machine), and the same
  // 184 px took 2.2–3.2 s — measured v1.62 probe, Complex, lab_landing: the
  // mark still 3–94 px off the line 2.4 s after the click, the jump after an
  // answer (lab_flow B) 1.3 s. FINAL 11: nothing longer than 1.5 s. Now the
  // share of a step follows the time since the last one, 1 − e^(−dt/τ), with
  // τ = 75 ms = what 0.2 per frame was at 60 frames a second: the same glide
  // on a fast machine, and on a slow one fewer, larger steps in the same time.
  var LTAU = 75;
  function landTo(sc, to){
    to = Math.max(0, Math.min(Math.round(to), Math.max(0, sc.scrollHeight - sc.clientHeight)));
    var m = window.__nbLandMove;
    if (m && m.sc === sc) { m.to = to; m.gen = window.__nbLandGen; return; }
    m = window.__nbLandMove = {sc: sc, to: to, pos: sc.scrollTop, set: sc.scrollTop,
                               gen: window.__nbLandGen, t: 0};
    var step = function(){
      var mv = window.__nbLandMove;
      if (mv !== m) return;
      if (window.__nbLandOff || !m.sc.isConnected) { window.__nbLandMove = null; return; }
      // someone else moved the page (the scrollbar, a script): the movement
      // is theirs now — like the wheel's glide, this one steps aside
      if (Math.abs(m.sc.scrollTop - m.set) > 2) { window.__nbLandMove = null; return; }
      var left = m.to - m.pos;
      if (Math.abs(left) < 0.75) {
        m.sc.scrollTop = m.to; window.__nbLandMove = null;
        if (window.__nbFollowNow) window.__nbFollowNow();     // E22.6
        return;
      }
      var now = window.performance ? performance.now() : Date.now();
      var dt = m.t ? now - m.t : 16.7;          // the first step: one frame's worth
      m.t = now;
      var d = left * (1 - Math.exp(-dt / LTAU));
      if (Math.abs(d) < 0.75) d = left < 0 ? -0.75 : 0.75;
      m.pos += d;
      m.sc.scrollTop = m.pos;
      m.set = m.sc.scrollTop;
      // E22.6: set inside a frame callback, the page's scroll event comes a
      // frame later — the rail goes with the page in this one
      if (window.__nbFollowNow) window.__nbFollowNow();
      window.requestAnimationFrame(step);
    };
    window.requestAnimationFrame(step);
  }
  window.__nbLandTo = landTo;
  // 2026-09-29 (E8.5, Applikation) — THE READER'S HAND ENDS EVERY LANDING.
  // A click on a mark schedules its landing passes (60 … 1400 ms). landArm()
  // stops them on input OUTSIDE the panel only — so a click on chapter 7 and
  // then a grab of the cursor (or the wheel over the timeline) left the
  // passes running: every pass re-aimed the page at chapter 7 while the hand
  // dragged it elsewhere, and the document jumped back (video V3). The
  // cursor, the lane and the wheel over the panel call this: a new generation
  // (older passes are void), no landing glide, no wheel glide. One target —
  // the hand's.
  window.__nbLandStop = function(){
    landNew();
    window.__nbLandMove = null;
  };
  // the reading line on screen: the line `.nbreadfix` draws (E9.1), else the
  // rail's top plus railY0; null before the panel has one
  function readLineY(){
    var hh = document.getElementById('nbpanel-root');
    if (!hh || !document.body.classList.contains('nbvert')) return null;
    var fx = hh.querySelector(':scope > .nbreadfix');
    var y = fx ? parseFloat(fx.style.top) : NaN;
    if (!(y > 0)) {
      var mp = hh.querySelector('.nbmap'), y0 = parseInt(hh.dataset.railY0 || '0', 10) || 0;
      if (mp && y0 > 0) y = mp.getBoundingClientRect().top + y0;
    }
    return y > 0 ? y : null;
  }
  // 2026-10-06 (E23.15, Struktur + Applikation) — THE CHOSEN MARK STAYS ON THE
  // READING LINE. A click lands its pill on the line (E22.4) — and then let it
  // go: an accordion shut above it, a plot or widget drawn late, a hint opened,
  // the lens or the panel's width changed, and the pill (with its mark) went
  // 40–250 px off the line (reader's video, Complex, chapter 2's exercise
  // chosen; measured v1.64 probe, dir_e23 D23.15: up to 749 px after the
  // Introduction opened above it). Now the chosen mark is an ANCHOR: a
  // ResizeObserver on the document's column (viewport + cells) answers every
  // change of size after layout and before paint, and in that same frame sets
  // scrollTop so that pill − line = 0 (the point land() aims at, __nbAim).
  // The anchor holds until the READER scrolls on his own — wheel (not
  // Ctrl+wheel: the lens), a scroll key outside an editor, the scroll bar,
  // the thumb, the marker — and comes back with the next click on a mark.
  // Our own moves (this correction, the lens's fix point, the landing) are
  // no input events and never loosen it. While a landing glides, or in its
  // first 1.5 s (its passes aim at the same point), the anchor waits.
  var pin = null;
  function pinY(p){
    var aim = p.node.__nbAim;
    var ae = aim && aim[0] && aim[0].isConnected ? aim[0] : null;
    var ar = ae ? ae.getBoundingClientRect() : null;
    if (ar && ar.height > 0) return aim[1] ? ar.top + ar.height / 2 : ar.top + 56;
    var el = p.el;
    if (!el || !el.isConnected) return null;
    var hd = el.querySelector ? el.querySelector(HDR) : null;
    var r = (hd && hd.getBoundingClientRect().height > 2 ? hd : el).getBoundingClientRect();
    if (r.height > 0) return r.top + r.height / 2;
    // E29 D4: folded by its pill, neither the aim nor the land box has a box
    // any more — the pill the reader sees is the header of the nearest drawn
    // fold around the mark's anchor (measured Vorlage v1.75: ch1 folded by its
    // pill, pinY null, the chapter stood 98 px above the line, its mark unlit)
    var sp = p.node.getAttribute ? document.getElementById(p.node.getAttribute('data-target') || '') : null;
    for (var c = sp; c && c !== p.sc; c = c.parentElement) {
      if (!c.classList || !(c.classList.contains('jupyter-widget-Collapse') || c.classList.contains('lm-Collapse'))) continue;
      var h2 = c.querySelector(':scope > .jupyter-widget-Collapse-header, :scope > .lm-Collapse-header, :scope > .p-Collapse-header');
      var q = h2 && h2.getBoundingClientRect();
      if (q && q.height > 2) return q.top + q.height / 2;
    }
    return null;
  }
  function pinFix(){
    var p = pin;
    if (!p) return;
    if (!p.sc.isConnected || !p.node.isConnected) { pinOff(); return; }
    if (Date.now() < p.from) return;
    var mv = window.__nbLandMove;
    if (mv && mv.sc === p.sc) return;                  // a landing glides there itself
    var line = readLineY(), y = line === null ? null : pinY(p);
    if (y === null) return;
    var sc = p.sc, d = y - line;
    if (Math.abs(d) < 0.5) return;
    var to = Math.max(0, Math.min(sc.scrollTop + d, sc.scrollHeight - sc.clientHeight));
    if (Math.abs(to - sc.scrollTop) < 0.5) return;
    sc.scrollTop = to;
    p.set = sc.scrollTop;                              // ours (pinScroll)
    if (window.__nbFollowNow) { try { window.__nbFollowNow(); } catch (e) {} }   // the rail in this frame (E22.6)
  }
  window.__nbPinFix = pinFix;
  // 2026-10-12 (E29 D4, JavaScript) — THE PILL'S CLICK AND THE MARK'S CLICK
  // AGREE. A click on a fold's pill in the document (its header) changes the
  // layout over the next frames (the widget's own toggle, then its content);
  // the anchor of the chosen mark (E23.15) answered only through the
  // ResizeObserver and lost the last step now and then (re-opened: 6 px off).
  // A pill click of the reader inside our notebook counts as a change of size
  // (the scroll that follows is not the reader's) and the anchor is put on the
  // line again over the next 0.8 s.
  function pinPill(ev){
    if (!pin || ev.button) return;
    var t = ev.target, hd = t && t.closest ? t.closest(HDR) : null;
    if (!hd || !pin.sc.contains(hd)) return;
    var now = function(){ return window.performance ? performance.now() : Date.now(); };
    pin.lay = now(); pin.from = Math.min(pin.from, Date.now());
    [0, 60, 160, 320, 520, 800].forEach(function(ms){
      setTimeout(function(){ if (!pin) return; pin.lay = now(); pinFix(); }, ms);
    });
  }
  if (window.__nbPinPillOff) { try { window.__nbPinPillOff(); } catch (e) {} }
  document.addEventListener('click', pinPill, false);
  window.__nbPinPillOff = function(){ document.removeEventListener('click', pinPill, false); };
  window.__nbPinState = function(){ return pin ? {y: pinY(pin), line: readLineY(), el: pin.el ? String(pin.el.className) : null, from: pin.from - Date.now()} : null; };   // for the tests (E29 D4)
  // 2026-10-06 (E23.15 Nach-Runde, Applikation) — A SCRIPT THAT SCROLLS THE
  // PAGE AWAY ALSO LOOSENS THE ANCHOR. Only the reader's input events did
  // (pinFree). But the page can be carried off without one: JupyterLab
  // scrolls a cell into view, a find, a test's scrollIntoView. The anchor then
  // held a pill that was no longer on screen, and the next change of size
  // anywhere (a lock box opened down there) pulled the page back up to it —
  // measured v1.65 + js-E23.15, test_regress J10 after J11 (a click on a
  // mark): the heading of the locked chapter jumped away under the mouse and
  // the second click missed it, the box stayed open. Now every scroll of the
  // anchored page is looked at: our own (the correction, a landing's glide)
  // and one that follows a change of size (the browser's scroll anchoring,
  // the lens — the ResizeObserver saw it, at most 150 ms before) are kept;
  // a pure scroll that leaves the pill off the line (> 2 px) is someone
  // else's — the anchor lets go, as for the wheel.
  function pinScroll(){
    var p = pin;
    if (!p) return;
    var sc = p.sc, mv = window.__nbLandMove;
    if ((mv && mv.sc === sc && Math.abs(sc.scrollTop - mv.set) <= 2) || Math.abs(sc.scrollTop - p.set) < 1) { p.set = sc.scrollTop; return; }
    var now = window.performance ? performance.now() : Date.now();
    if (now - p.lay < 150) { p.set = sc.scrollTop; return; }
    var line = readLineY(), y = line === null ? null : pinY(p);
    if (y === null || Math.abs(y - line) <= 2) { p.set = sc.scrollTop; return; }
    pinOff();
  }
  function pinWatch(p){
    if (window.__nbPinRO) { try { window.__nbPinRO.disconnect(); } catch (e) {} }
    if (!window.ResizeObserver) return;
    var first = true;
    var ro = window.__nbPinRO = new ResizeObserver(function(){
      if (pin !== p) return;
      // a change of size (not the first call, which only reports the boxes)
      if (!first) p.lay = window.performance ? performance.now() : Date.now();
      first = false;
      pinFix();
    });
    // the column, not the airs above and below it (footAir sizes those in the
    // follow this correction calls — observing them would loop)
    var col = p.sc.querySelector('.jp-WindowedPanel-viewport') || p.sc.querySelector('.jp-Notebook') || p.sc;
    ro.observe(col);
    [].forEach.call(col.children, function(c){ if (c.classList && c.classList.contains('jp-Cell')) ro.observe(c); });
  }
  function pinOff(){
    if (pin) { try { pin.sc.removeEventListener('scroll', pinScroll); } catch (e) {} }
    pin = null;
    if (window.__nbPinRO) { try { window.__nbPinRO.disconnect(); } catch (e) {} window.__nbPinRO = null; }
  }
  function pinSet(node, el, sc){
    pinOff();
    if (!node || !sc) return;
    pin = {node: node, el: el, sc: sc, from: Date.now() + 1500, set: sc.scrollTop, lay: -1e9};
    pinWatch(pin);
    sc.addEventListener('scroll', pinScroll, {passive: true});
    setTimeout(function(){ if (pin && pin.node === node) pinFix(); }, 1600);
  }
  window.__nbPinOff = pinOff;
  // the notebook's scroller: the one of the panel the element is in
  function pinScroller(el){
    var P = (el && el.closest && el.closest('.jp-NotebookPanel')) || frontPanel();
    return (P && (P.querySelector('.jp-WindowedPanel-outer') || P.querySelector('.jp-Notebook'))) || scrollerOf(el);
  }
  window.__nbPinned = function(){ return pin ? pin.node : null; };
  // the reader's own scrolling loosens the anchor
  function pinFree(ev){
    if (!pin) return;
    var t = ev.target;
    if (ev.type === 'wheel') {
      if (ev.ctrlKey || ev.metaKey) return;            // the lens
    } else if (ev.type === 'keydown') {
      if (!/^(ArrowUp|ArrowDown|PageUp|PageDown|Home|End| |Spacebar)$/.test(ev.key || '')) return;
      if (t && t.closest && t.closest('input,textarea,select,[contenteditable="true"],.cm-editor,.CodeMirror')) return;
    } else if (ev.type === 'pointerdown') {
      if (!t || !(t === pin.sc || (t.closest && t.closest('#nbpanel-root .nbmap-cursor,#nbpanel-root .nbmap-here,#nbpanel-root .nbsb'))))
        return;
    }
    pinOff();
  }
  ['wheel', 'touchmove', 'keydown', 'pointerdown'].forEach(function(t){
    document.addEventListener(t, pinFree, {capture: true, passive: true});
  });
  function land(el, node, gen){
    if(!el) return;
    if (window.__nbLandOff) return;          // the reader has the wheel
    if (gen !== undefined && !landLive(gen)) return;   // E6.3: a later jump owns the page
    // an anchor span has no height and sits 56px above what it marks — land on
    // the thing itself, not on the marker
    if(el.getBoundingClientRect().height === 0){
      var nx = el.nextElementSibling;
      while(nx && nx.getBoundingClientRect().height === 0) nx = nx.nextElementSibling;
      if(nx) el = nx;
    }
    // Land on the PILL, not on the box around it. The rail's node is measured
    // against the accordion header — so if the scroll stops at the top of the
    // widget, the pill ends up some eighty pixels lower than the marker that
    // just pointed at it. Aiming at the same header the rail aimed at puts the
    // two on one line, which is what the reader is promised when they click.
    var head = null;
    if (el.querySelector)
      head = el.querySelector('.jupyter-widget-Collapse-header,'
                            + '.lm-Collapse-header,.p-Collapse-header');
    if (head && head.getBoundingClientRect().height > 2) el = head;
    var top = panelBottom();
    var sc = scrollerOf(el);
    var r = el.getBoundingClientRect();
    if(sc){
      var sr = sc.getBoundingClientRect();
      // ON THE MARKER (2026-09-24t).
      // The rail's marks and the reading marker are the same instrument: a
      // click on a mark should leave that mark standing on the marker, not
      // somewhere below it. The marker's own middle is read off the DOM, so the
      // two cannot drift apart however the panel is sized.
      // UNDER THE TOOLBAR, AND NOWHERE ELSE (2026-09-24z).
      // Two earlier versions aimed at the marker: first where it was pinned,
      // then where it starts. Both read something that the click itself then
      // changes — the marker moves, the rail re-measures, railY0 comes back
      // slightly different — so the five passes that follow an expanding
      // accordion each aimed at a different line. That is the wobble.
      // The target is now a line nothing on the rail can move: just under the
      // toolbar, which is where the reader's eye is anyway and where the
      // marker stands when the document is opened.
      var want = Math.max(sr.top, top) + 6;
      var hostP = document.getElementById('nbpanel-root');
      // 2026-10-05 (E22.4, Struktur) — THE LINE IS WHERE THE READER PUT IT.
      // landGap below is the distance toolbar → title mark, measured ONCE
      // (24ai) — the reading height of the opening. Since the reading height
      // can be dragged (E9.1/E11.4) that was the wrong line: with the knob
      // pulled to the middle of the window a click landed its chapter 192 px
      // above the marker, at 70 % 345 px (measured v1.63, Modeling, real Lab).
      // The target is the reading line as it is drawn now (`.nbreadfix`, else
      // rail top + railY0), read on every pass: railY0 is the title mark's
      // height plus the reader's offset, it does not move with the rail's
      // scroll, and a pixel of relayout is within what a landing forgives.
      var lineNow = readLineY();
      var rowP = hostP && hostP.querySelector('.nbdock .nbctrl');
      var mapP = hostP && hostP.querySelector('.nbmap');
      if (document.body.classList.contains('nbvert') && rowP) {
        var rrP = rowP.getBoundingClientRect();
        if (rrP.height > 4) {
          // 2026-09-24ai — THE SAME GAP THE TITLE MARK HAS ON OPENING.
          // A click used to land the mark ten pixels under the toolbar, which
          // is tighter than anything else in the panel; the reader asked for
          // the gap they see when the notebook opens, which is the distance
          // from the toolbar down to the title diamond.
          // That distance is MEASURED ONCE and kept: railY0 shifts by a pixel
          // or two on every relayout, and reading it fresh on each of the five
          // passes that follow an expanding accordion is what made the document
          // shake in the first place (see 24z).
          var gap = parseInt(hostP.dataset.landGap || '0', 10) || 0;
          if (!gap && mapP) {
            var lo0 = parseInt(hostP.dataset.railY0 || '0', 10) || 0;
            if (lo0 > 0) {
              // NOT minus scrollTop. railY0 is the title mark's place INSIDE
              // the rail and does not move when the rail scrolls; subtracting
              // the scroll turned the gap negative the moment the reader was
              // anywhere but the top, so it never got cached and every click
              // fell back to the 10px default.
              var g = Math.round(mapP.getBoundingClientRect().top
                                 + lo0 - rrP.bottom);
              if (g > 8 && g < 400) { gap = g; hostP.dataset.landGap = String(g); }
            }
          }
          want = Math.max(want, rrP.bottom + (gap || 10));
          if (lineNow !== null) want = lineNow;          // E22.4
        } else if (mapP) {
          // 2026-09-28 (R2 · 17) — NO TOOLBAR ROW. The line is where the title
          // mark was when the notebook opened: its distance from the
          // scroller's top, measured once and kept (the same reason as above).
          var gapC = parseInt(hostP.dataset.landGapC || '0', 10) || 0;
          if (!gapC) {
            var y0c = parseInt(hostP.dataset.railY0 || '0', 10) || 0;
            if (y0c > 0) {
              var gc = Math.round(mapP.getBoundingClientRect().top + y0c - sr.top);
              if (gc > 0 && gc < 600) { gapC = gc; hostP.dataset.landGapC = String(gc); }
            }
          }
          if (gapC) want = sr.top + gapC;
          if (lineNow !== null) want = lineNow;          // E22.4
        }
      }
      // ...and a pass that has nothing to correct does not scroll at all. An
      // unconditional assignment re-ran the browser's smooth scrolling on every
      // one of the five passes, which is the visible shake even when the target
      // had not moved.
      var d = Math.round(r.top - want);
      // 2026-09-27f — THE MARK, NOT THE PILL'S TOP EDGE, LANDS ON THE LINE
      // (Eilauftrag 2). The rail puts a mark on the MIDDLE of its pill (or
      // on the point vertLayout chose for it, kept as __nbAim), and the
      // cursor and the marker stand on the reading line — so landing the
      // pill's top edge there left the clicked mark 24 px (chapter) to
      // 152 px (end) below the cursor, measured in 27d. The same point the
      // rail measures is brought onto the line; 1 px is the step, because
      // the marker counts a mark as reached within 2.
      if (document.body.classList.contains('nbvert')) {
        var aim = node && node.__nbAim;
        var ae = aim && aim[0] && aim[0].isConnected ? aim[0] : null;
        var ar = ae ? ae.getBoundingClientRect() : null;
        if (ar && (ar.height > 0 || ar.top)) {
          d = Math.round((aim[1] ? ar.top + ar.height / 2 : ar.top + 56) - want);
        } else {
          d = Math.round(r.top + r.height / 2 - want);
        }
        // E6.3: the target is where the page will be, not where it is
        var mv0 = window.__nbLandMove;
        if (Math.abs(d) > 1 || (mv0 && mv0.sc === sc)) landTo(sc, sc.scrollTop + d);
        return;
      }
      if (Math.abs(d) > 3) landTo(sc, sc.scrollTop + d);
    } else {
      window.scrollTo({top: Math.max(0, (window.scrollY || 0) + r.top - top),
                       behavior: 'smooth'});
    }
  }
  // 2026-09-24an — SELECT FIRST, THEN DOUBLE-CLICK.
  // 24aj's arm fired on any two clicks inside four seconds, and two clicks on a
  // mark is how a reader navigates — chapters opened by accident, which is the
  // one thing a lock must not do. The gesture is now in two deliberate parts: a
  // single click SELECTS the mark (the magenta fill), and only a real
  // double-click on an already-selected lock opens it. A reader who is
  // navigating never produces that pair.
  //
  // What it opens is the CHAPTER and nothing inside it: the exercises stay
  // folded, and the skipped one goes amber until it is answered properly. The
  // click reaches Python through the chapter's own hidden button — the same
  // widget the gear drawer borrows, pressed from here.
  // 2026-09-24az — THE LOCK IS ARMED ON THE RAIL AND TURNED IN THE DOCUMENT.
  // The double-click gesture is gone. Clicking a locked mark now ARMS that one
  // chapter: its padlock, on the rail and in the box down in the document,
  // becomes an open one. Nothing has been unlocked yet — the open padlock in
  // the BOX is the thing you press, and pressing it is the deliberate act the
  // whole gesture exists to require. Clicking any other mark disarms it again,
  // so there is never more than one chapter standing open-lock at a time.
  // 2026-09-28a (K1, Applikation) — NO WAY PAST A LOCK ON THE TIMELINE.
  // 24az armed a locked chapter's mark (its padlock became a key, here and in
  // the box), 25f added a window at the top of the panel with that key, and
  // the key pressed the chapter's hidden "open chapter only" button. The user
  // decided (27.09.): a skip happens only at the exercise, by "Skip for now".
  // Arming is gone; `__nbArmLock` stays as a name (older callers, and a build
  // from before 28a in the same window) and only clears what one may have set.
  function armLock(key){
    var was = document.querySelectorAll('.nbmap-node.nbkeyed, .nblocked-note.nbkeyed');
    for (var i = 0; i < was.length; i++) was[i].classList.remove('nbkeyed');
  }
  window.__nbArmLock = armLock;
  window.__nbLockWindow = function(){};
  // K1.2 — A TASK THAT WAITS DOES NOT UNFOLD. Python marks the fold
  // `acc-tasklock` while the task before it is unanswered and removes the
  // class when it opens. Every way to unfold a fold is a click on its header —
  // the reader's, the timeline's (`expand`), the keyboard's (Enter goes through
  // the same click) — so the click is refused here, in the capture phase,
  // before ipywidgets sees it. Enter/Space on a focused header likewise. The
  // kernel folds it back as well, should anything get past (`_task_lock`).
  function taskLockedHdr(t){
    var hd = t && t.closest ? t.closest(HDR) : null;
    return !!(hd && hd.closest('.acc-tasklock'));
  }
  window.__nbTaskLocked = function(el){
    return !!(el && el.closest && el.closest('.acc-tasklock'));
  };
  if (!window.__nbTaskLockArmed) {
    window.__nbTaskLockArmed = true;
    document.addEventListener('click', function(ev){
      if (!taskLockedHdr(ev.target)) return;
      ev.preventDefault(); ev.stopPropagation();
      if (ev.stopImmediatePropagation) ev.stopImmediatePropagation();
    }, true);
    document.addEventListener('keydown', function(ev){
      if ((ev.key === 'Enter' || ev.key === ' ') && taskLockedHdr(ev.target)) {
        ev.preventDefault(); ev.stopPropagation();
      }
    }, true);
  }
  // 2026-09-25 — A DOUBLE CLICK ON A MARK OPENS NOTHING.
  // Picking a mark ARMS its lock, and an armed lock is one press away from
  // open. Two quick presses anywhere along that path — on the mark, or on the
  // mark and then the padlock that has just appeared under the pointer — were
  // enough to walk a chapter open without the reader ever deciding to. The
  // gesture is refused at both ends: the second click of a double click never
  // reaches the rail, and never turns a key.
  document.addEventListener('dblclick', function(ev){
    var n = ev.target.closest ? ev.target.closest('#nbpanel-root .nbmap-node') : null;
    if (!n) return;
    ev.preventDefault();
    ev.stopPropagation();
  }, true);
  // 2026-09-29 (E8.18, Applikation) — A PIP IS A WAY TO ITS EXERCISE. The
  // two pips beside a chapter mark ("Exercises" / "Coding") and their words
  // were part of the chapter mark, so a click on them landed on the
  // chapter. Now it lands on that chapter's exercise or coding exercise,
  // as a click on the exercise's own mark would — unless the chapter or the
  // pip is locked: then it is a click on the chapter, as before.
  function pipTarget(t, a){
    var row = t && t.closest ? t.closest('.nbpip-row') : null;
    if (!row || !a || !a.classList || !a.classList.contains('chap') || !a.contains(row)) return null;
    if (a.classList.contains('locked')) return null;
    var pip = row.querySelector('[data-st]');
    if (pip && pip.getAttribute('data-st') === 'locked') return null;
    var want = row.getAttribute('data-kind') === 'code' ? 'codetask' : 'task';
    for (var n = a.nextElementSibling; n; n = n.nextElementSibling) {
      if (!n.classList || !n.classList.contains('nbmap-node')) continue;
      if (n.classList.contains('chap') || n.classList.contains('sect')) break;
      if (n.classList.contains(want)) return n;
    }
    return null;
  }
  // 2026-10-12 (E29 D3, JavaScript) — A LOCKED CHAPTER IS NOT A PLACE TO GO.
  // Reader 12.10.: a click on a pip (or the mark) of a locked chapter tried
  // to jump there and to open it ("a locked chapter's mark still jumps to
  // it", since 28a) — and landed on a lock card, or nowhere. Now a reader's
  // click on such a mark does nothing to the page (no jump, no fold, no
  // choice) and says why, as the lock card in the document does: its head
  // and its sentence (the card of THIS lock, `.nblocked-<key>`, in the
  // notebook in front; Python's words, in the language it was built in),
  // as a small box beside the mark, gone after 4 s or on the next click.
  // The keyboard's walk (Alt+J/K) and the script's own moves are not clicks
  // of the reader and still land.
  function lockedMark(a, t){
    if (!a || !a.classList || !a.classList.contains('nbmap-node')) return false;
    if (a.classList.contains('locked') || a.classList.contains('st-lock') || a.classList.contains('cd-lock')) return true;
    var row = t && t.closest ? t.closest('.nbpip-row') : null, pip = row && a.contains(row) ? row.querySelector('[data-st]') : null;
    if (pip && pip.getAttribute('data-st') === 'locked') return true;
    if (a.classList.contains('chap') || a.classList.contains('sect')) return false;
    // an exercise, a coding exercise or a figure: locked with its chapter
    for (var n = a.previousElementSibling; n; n = n.previousElementSibling) {
      if (!n.classList || !n.classList.contains('nbmap-node')) continue;
      if (n.classList.contains('sect')) return false;
      if (n.classList.contains('chap')) return n.classList.contains('locked');
    }
    return false;
  }
  function lockHint(a){
    var key = a.getAttribute('data-lock') || '', chap = a;
    if (!key) for (var n = a.previousElementSibling; n; n = n.previousElementSibling)
      if (n.classList && n.classList.contains('chap')) { chap = n; key = n.getAttribute('data-lock') || ''; break; }
    var P = frontPanel() || document, card = key ? P.querySelector('.nblocked-note.nblocked-' + key.replace(/[^\w-]/g, '')) : null;
    var de = !!(window.__nbDe && window.__nbDe());
    var hd = card && card.querySelector('.nblocked-head'), sy = card && card.querySelector('.nblocked-say');
    var head = '\uD83D\uDD12 ' + ((hd && hd.textContent.trim()) || (de ? 'Noch gesperrt' : 'Still locked'));
    var say = (sy && sy.textContent.trim()) || (de ? 'Es öffnet sich, sobald die Aufgabe davor beantwortet ist.' : 'It opens once the exercise before it is answered.');
    var host = document.getElementById('nbpanel-root') || document.body, b = host.querySelector(':scope>.nblockhint');
    if (!b) {
      b = document.createElement('div'); b.className = 'nblockhint'; b.setAttribute('role', 'status');
      b.innerHTML = '<b></b><span></span>';
      // E31 G1: a box of the panel — × the controls' size (--nbgs), not the text size
      b.style.cssText = 'position:fixed;z-index:10060;max-width:calc(260px * var(--nbgs,1));padding:8px 11px;border-radius:10px;font-size:calc(12px * var(--nbgs,1));line-height:1.4;'
        + 'background:var(--jp-layout-color1,#fff);color:var(--jp-ui-font-color1,#33414e);border:1px solid var(--jp-border-color1,#c3ced8);'
        + 'box-shadow:0 4px 14px rgba(0,0,0,.18);pointer-events:none;display:flex;flex-direction:column;gap:3px;text-align:left';
      host.appendChild(b);
    }
    b.firstChild.textContent = head; b.lastChild.textContent = say;
    var f = a, r = f.getBoundingClientRect();
    if (!(r.width > 0 && r.height > 0)) { var d = a.querySelectorAll('*');
      for (var i = 0; i < d.length; i++) { var q = d[i].getBoundingClientRect(); if (q.width > 0 && q.height > 0) { r = q; break; } } }
    b.style.display = 'flex';
    var bw = b.offsetWidth || 240, bh = b.offsetHeight || 60;
    var x = r.left - bw - 10; if (x < 4) x = Math.min(window.innerWidth - bw - 4, r.right + 10);
    var y = Math.max(4, Math.min(window.innerHeight - bh - 4, r.top + r.height / 2 - bh / 2));
    b.style.left = Math.round(x) + 'px'; b.style.top = Math.round(y) + 'px';
    b.setAttribute('data-lock', key);
    clearTimeout(window.__nbLockHintT);
    window.__nbLockHintT = setTimeout(function(){ b.style.display = 'none'; }, 4000);
    var off = function(ev){ if (ev.target && ev.target.closest && ev.target.closest('.nbmap-node') === a) return;
      b.style.display = 'none'; document.removeEventListener('pointerdown', off, true); };
    document.addEventListener('pointerdown', off, true);
  }
  var onJump = function(ev){
    // ---- table-of-contents jump links (also used by the group "back to top" pills) ----
    var a = ev.target.closest ? ev.target.closest('a.nbjump') : null;
    if(!a) return;
    ev.preventDefault();
    // E29 D3: a locked chapter (its mark, its pips, its exercises) is not a place to go
    if (!window.__nbKeyNav && !window.__nbGoing && lockedMark(a, ev.target)) {
      ev.stopPropagation(); lockHint(a); return;
    }
    var pt = pipTarget(ev.target, a);
    if (pt) { ev.stopPropagation(); pt.click(); return; }
    // a locked chapter's mark still jumps to it; it no longer opens it
    // …and the mark that was clicked stays filled until another one is
    // (2026-09-24ak) — the rail's own answer to "where did I last go?"
    // 2026-09-27e — A CHOSEN, OPEN CHAPTER FOLDS ON THE NEXT CLICK (F, rule a).
    // "Chosen" is `nbsel` from the click before; a click that is the tail of a
    // double click (detail > 1) is not a second choice, and a click the
    // script makes itself (the move after a right answer) never folds.
    // 2026-09-28b (K2.10) — EVERY MARK THAT HAS SOMETHING TO FOLD, not only
    // a chapter: an exercise folds its practice fold, a coding mark its code
    // fold, a figure its visualisation, a group (Introduction, Content,
    // Appendix) itself and with it all its chapters, a sub-section (the quiz,
    // own data, glossary …) its section. Title, end and your own cell have
    // nothing to fold: a second click there only lands again. A waiting
    // exercise never unfolds (K1), so it has nothing to fold either.
    if (a.classList && a.classList.contains('nbmap-node') &&
        a.classList.contains('nbsel') &&
        !a.classList.contains('title') && !a.classList.contains('end') &&
        !a.classList.contains('cell') && !a.classList.contains('own') &&
        ev.detail === 1 && !window.__nbGoing) {
      if (a.classList.contains('sect') ? foldGroup(a.getAttribute('data-target'))
                                       : foldAfter(a.getAttribute('data-target'))) {
        if (window.__nbArmLock) window.__nbArmLock(null);
        // 2026-09-27g — …and it is no longer the chosen one (Eilauftrag 2,
        // criterion 2). It stays where it is — on the reading line — and
        // stays lit; only the choice is taken back, so the next click is a
        // first click again and opens it.
        a.classList.remove('nbsel');
        return;
      }
    }
    var wasSel = !!(a.classList && a.classList.contains('nbsel'));   // E8.11
    pinOff();                                // E23.15: a new choice; the anchor follows below
    if (a.classList && a.classList.contains('nbmap-node')) {
      var sel = document.querySelectorAll('#nbpanel-root .nbmap-node.nbsel');
      for (var sj = 0; sj < sel.length; sj++) sel[sj].classList.remove('nbsel');
      a.classList.add('nbsel');
      // a click is the reader taking over: the keyboard's own place is dropped
      // and the next Alt+J/K starts from where the document actually is.
      if (!window.__nbKeyNav) window.__nbKeyAt = null;
      // …and picking a mark arms its lock, or disarms whatever was armed.
      // 2026-09-25: only a click that stands alone arms anything. The second
      // press of a double click leaves the selection where it is and arms
      // nothing new — see the dblclick guard above.
      if (window.__nbArmLock && !(ev.detail > 1))
        window.__nbArmLock(a.getAttribute('data-lock') || null);
    }
    if(a.getAttribute('data-bottom')){        // the cell bar: down to the end
      landNew();                             // E6.3: older landings stop here
      var cur2 = frontPanel();                   // E21.1/E21.3
      // E9.7: "Your own cell" is an accordion now; a shut one opens first
      var yo = cur2 && cur2.querySelector('.acc-yoc.acc-root');
      yo = yo && (isCol(yo) ? yo : yo.querySelector(COL));
      if (yo) expand(yo);
      var bot = cur2 && (cur2.querySelector('.jp-WindowedPanel-outer') ||
                         cur2.querySelector('.jp-Notebook'));
      // 2026-09-28 (Paket 6, Applikation) — "YOUR OWN CELL" MAKES ONE.
      // The mark used to scroll to the strip JupyterLab leaves at the foot
      // ("Click to add a cell.") and stop there: the reader then had to find
      // and click the strip. A click of the READER now clicks that strip for
      // them, so every click is one new cell, in edit mode, at the end.
      // The keyboard's walk along the marks (Alt+J/K) and the script's own
      // moves only land — stepping past the last mark must not litter the
      // notebook with empty cells. No strip (JupyterLite, Colab, a static
      // page): the old landing, nothing else.
      var foot = (!window.__nbKeyNav && !window.__nbGoing && cur2)
               ? cur2.querySelector('.jp-Notebook-footer') : null;
      // 2026-09-29 (E6.8, Applikation) — EVERY CLICK, ONE NEW CELL. The strip's
      // click was sent once and trusted; when the front end was busy (a run,
      // a re-render of the strip) it came to nothing. The cells are counted
      // before, and if none came, the strip is looked up again and clicked
      // again, up to three times.
      var nCells = function(){ return cur2 ? cur2.querySelectorAll('.jp-Notebook .jp-Cell').length : 0; };
      var n0 = nCells();
      if(foot && foot.click) {
        try { foot.click(); } catch(e) {}
        [250, 600, 1000].forEach(function(ms){
          setTimeout(function(){
            if (nCells() > n0) return;
            var f2 = cur2.querySelector('.jp-Notebook-footer');
            if (f2 && f2.click) { try { f2.click(); } catch(e) {} }
          }, ms);
        });
      }
      // 2026-10-01 (E10.M-yoc, Struktur) — THE MARK'S NEW CELL STANDS ON THE
      // READING HEIGHT TOO. Since E11.1 the mark is the only way to make one,
      // and it still went to the very end (scrollHeight): the new cell's
      // middle stood at y 10, 256 px above the line (lab_landing, v1.42).
      // The same landing as the old button (E10.5), and the editor focused.
      if (foot) { cellToLine(cur2, bot, n0); return; }
      if(bot) bot.scrollTop = bot.scrollHeight;
      return;
    }
    if(a.getAttribute('data-top')){           // the title bar: back to the start
      // E9.5: the first click lands on the title and leaves the book as it
      // is; a click on the chosen title mark shuts (or opens) the title's
      // accordion, like a chapter mark folds its chapter
      if (wasSel && ev.detail === 1 && !window.__nbKeyNav && !window.__nbGoing) titleToggle();
      else if (rootAcc('title')) titleToggle(true);                 // a first click opens
      else foldAll();                                               // E8.19, old builds
      var cur = frontPanel();                   // E21.1/E21.3
      var top = cur && (cur.querySelector('.jp-WindowedPanel-outer') ||
                        cur.querySelector('.jp-Notebook'));
      landNew(); landArm();                  // E6.3: glide up, and nothing older pulls
      if(top) landTo(top, Math.max(0, window.__nbTopAt || 0));   // E9.2: title on the line
      else window.scrollTo({top: 0, behavior: 'smooth'});
      return;
    }
    // R2 · H3 — a mark of the reader's own cell: land that cell on the line
    if(a.classList && a.classList.contains('own')){
      var cp = frontPanel() || document;                            // E21.1
      var oc = cp.querySelector('.' + a.getAttribute('data-sel'));
      // 2026-09-29 (E8.11, Applikation) — AN OWN CELL FOLDS TO ONE LINE. As
      // with a chapter: the first click chooses and lands, a click on the
      // chosen mark folds the cell to its first line (output hidden), the
      // next one opens it again.
      if (oc && wasSel && ev.detail === 1 && !window.__nbKeyNav && !window.__nbGoing) {
        ownFold(oc, !oc.classList.contains('nbownshut'));
        a.classList.toggle('nbownshut', oc.classList.contains('nbownshut'));
        return;
      }
      if(oc){ var go = landNew(); landArm(); [0, 200, 600].forEach(function(ms){ setTimeout(function(){ land(oc, a, go); }, ms); });
              pinSet(a, oc, pinScroller(oc)); }                      // E23.15
      return;
    }
    var id = a.getAttribute('data-target'); if(!id) return;
    var span = document.getElementById(id); if(!span) return;
    // 1) + 2) OPEN THE WHOLE PATH, outermost first.
    //
    // Two things used to make a click on an Introduction sub-point do nothing.
    // First, the ancestors were opened from the inside out: clicking the header
    // of a chapter that is still inside a CLOSED group does nothing, because
    // that header is not laid out yet — the outer lid has to come off first.
    // Second, the chapter accordion was located exactly once, at click time; if
    // the group was shut, the walk found nothing and the retries kept expanding
    // a null. Both are resolved on every pass now.
    var isSect = !!(a.classList && a.classList.contains('sect'));
    var chap = openPath(span, isSect);
    // 3) scroll once the expansions have rendered; briefly highlight a
    //    References entry so the reader sees which source was meant
    // 3) scroll so the PILL sits directly under the panel, not in the middle of
    //    the screen. Several passes, because opening an accordion animates and
    //    moves everything below it.
    var landEl = (chap && chap.nodeType === 1) ? chap : span;
    if (landEl.classList) landEl.classList.add('nbjump-land');
    // Opening an accordion is animated and ipywidgets may render the panel a
    // moment later, so ONE expand often lands on a widget that is not there yet.
    // Repeat it a few times — expand() is a no-op once the thing is already open.
    var gen = landNew();   // E6.3: from here on, older passes are void
    // E23.15: a mark of the timeline is the anchor from now on
    if (a.classList && a.classList.contains('nbmap-node')) pinSet(a, landEl, pinScroller(span));
    function reopen(){
      if (!landLive(gen)) return;
      var c = openPath(span, isSect);
      if(c && !chap){ chap = c; landEl = c;
        if(c.classList) c.classList.add('nbjump-land');
        if (pin && pin.node === a) pin.el = c; }
    }
    landArm();          // a fresh click starts a fresh, interruptible landing
    [40, 160, 340, 620, 1000].forEach(function(ms){ setTimeout(reopen, ms); });
    [60, 260, 600, 1000, 1400].forEach(function(ms){ setTimeout(function(){ land(landEl, a, gen); }, ms); });
    setTimeout(function(){
      if(id.indexOf('ref')===0){ span.classList.remove('ref-flash'); void span.offsetWidth; span.classList.add('ref-flash'); }
    }, 400);
  };
  document.addEventListener('click', onJump, true);
  // 2026-09-30 (E9.7, Applikation) — "＋ YOUR OWN CELL" MAKES ONE. Python's
  // `.acc-yoc.acc-root` holds the button `.nbyoc-add`; a click on it is the
  // same as a click of the reader on the "Your own cell" mark: one new code
  // cell at the end of the notebook, in edit mode, on screen. Counted and
  // retried like the mark (E6.8), because the front end can be busy. No
  // strip (JupyterLite, Colab, a static page): the button says so instead.
  // E16.7: the cover timeline's "Your own cell" mark (`.nbtl-cell`) is
  // such a button too — it made no cell, its card stayed empty
  function yocAdd(ev){
    var b = ev.target && ev.target.closest ? ev.target.closest('.nbyoc-add,.nbcover-tl .nbtl-row.nbtl-cell') : null;
    if (!b || ev.button) return;
    ev.preventDefault(); ev.stopPropagation();
    var cur2 = b.closest('.jp-NotebookPanel') || frontPanel();      // E21.3
    var foot = cur2 && cur2.querySelector('.jp-Notebook-footer');
    if (!foot || !foot.click) {
      b.setAttribute('title', window.__nbDe() ? 'Diese Oberfläche hat keinen Streifen zum Anlegen einer Zelle; nehmen Sie ihr eigenes „+“'
                                              : 'this front end has no strip to add a cell with — use its own "+"');
      return;
    }
    var bot = cur2.querySelector('.jp-WindowedPanel-outer') || cur2.querySelector('.jp-Notebook');
    var nCells = function(){ return cur2.querySelectorAll('.jp-Notebook .jp-Cell').length; };
    var n0 = nCells();
    landNew();
    try { foot.click(); } catch(e) {}
    [250, 600, 1000].forEach(function(ms){
      setTimeout(function(){
        if (nCells() > n0) return;
        var f2 = cur2.querySelector('.jp-Notebook-footer');
        if (f2 && f2.click) { try { f2.click(); } catch(e) {} }
      }, ms);
    });
    cellToLine(cur2, bot, n0);
  }
  function cellToLine(cur2, bot, n0){
    // 2026-09-30 (E10.5, Struktur) — THE NEW CELL STANDS ON THE READING
    // HEIGHT. Until v1.35 the page went to its very end (scrollTop =
    // scrollHeight): the new cell ended up at the top, under the toolbar,
    // and only foot air below it. Now its middle is brought onto the reading
    // height — the line `.nbreadfix` draws (E9.1), the same point a click on
    // its "Own cell N" mark lands on. Re-aimed while the editor grows in.
    // Each pass takes a new landing generation: a lens hold (applyZoom's
    // zoomBack, K2.5) that a new cell's wrappers set off belongs to an older
    // one and yields; a click elsewhere takes a newer one and ends these.
    var gAdd = landNew();
    var lineY = function(){
      var hh = document.getElementById('nbpanel-root');
      var fx = hh && hh.querySelector(':scope > .nbreadfix');
      var y = fx ? parseFloat(fx.style.top) : NaN;
      if (!(y > 0) && hh) {
        var mp = hh.querySelector('.nbmap'), y0 = parseInt(hh.dataset.railY0 || '0', 10) || 0;
        if (mp && y0 > 0) y = mp.getBoundingClientRect().top + y0;
      }
      return y > 0 ? y : null;
    };
    var toLine = function(){
      if (!bot || !landLive(gAdd)) return;
      gAdd = landNew();
      var cs = cur2.querySelectorAll('.jp-Notebook .jp-Cell');
      if (cs.length <= n0) { bot.scrollTop = bot.scrollHeight; return; }
      var c = cs[cs.length - 1], r = c.getBoundingClientRect(), y = lineY();
      if (y === null || !(r.height > 0)) { bot.scrollTop = bot.scrollHeight; return; }
      var d = Math.round(r.top + r.height / 2 - y);
      if (Math.abs(d) > 1) landTo(bot, bot.scrollTop + d);
    };
    [80, 260, 600, 1000, 1500].forEach(function(ms){ setTimeout(toLine, ms); });
    [320, 1150].forEach(function(ms){ setTimeout(function(){
      var cs = cur2.querySelectorAll('.jp-Cell');
      var ed = cs.length > n0 ? cs[cs.length - 1].querySelector('.cm-content') : null;
      if (ed && ed.focus && document.activeElement !== ed) { try { ed.focus(); } catch(e) {} }
    }, ms); });
  }
  document.addEventListener('click', yocAdd, true);
  // 2026-10-02 (E16.8, Applikation) — A SLIDER'S NUMBER FIELD TAKES WHAT IS
  // TYPED. ipywidgets 8 commits its readout (`.widget-readout`, editable) on
  // Enter and on a delegated "blur" — which never bubbles, so leaving the
  // field kept the old value (measured, py-E16.8). Leaving it now commits
  // (focusout → the field's own Enter), and a valid number commits while
  // typing (60 ms after the last key); "-" or "1." wait for more. The
  // commit writes the formatted number: what was typed and the caret come
  // back while the field still has the focus.
  function roEnter(el){
    el.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true, cancelable: true}));
  }
  function roOut(ev){
    var el = ev.target;
    if (el && el.classList && el.classList.contains('widget-readout') && el.isContentEditable) roEnter(el);
  }
  function roIn(ev){
    var el = ev.target;
    if (!el || !el.classList || !el.classList.contains('widget-readout')) return;
    clearTimeout(el.__nbRoT);
    el.__nbRoT = setTimeout(function(){
      var t = (el.textContent || '').trim(), sel = window.getSelection();
      if (!/^-?(\d+(\.\d+)?|\.\d+)$/.test(t) || document.activeElement !== el) return;
      var off = sel && sel.rangeCount ? sel.getRangeAt(0).startOffset : t.length;
      roEnter(el);
      if (document.activeElement === el && el.textContent !== t) {
        el.textContent = t;
        try { var r = document.createRange(); r.setStart(el.firstChild || el, Math.min(off, t.length)); r.collapse(true);
              sel.removeAllRanges(); sel.addRange(r); } catch (e) {}
      }
    }, 60);
  }
  document.addEventListener('focusout', roOut, true);
  document.addEventListener('input', roIn, true);
  window.__nbjumpTeardown = function(){
    pinOff();                                                         // E23.15
    ['wheel', 'touchmove', 'keydown', 'pointerdown'].forEach(function(t){
      document.removeEventListener(t, pinFree, {capture: true, passive: true}); });
    document.removeEventListener('focusout', roOut, true);
    document.removeEventListener('input', roIn, true);
    document.removeEventListener('click', onJump, true);
    document.removeEventListener('click', yocAdd, true);
  };

  // 2026-09-28 (R2 · offen aus Paket 7, Oberfläche + Applikation) — TOOLTIPS IN
  // THE STYLE. A native `title` is drawn by the browser and no stylesheet can
  // reach it. Inside our own UI (the panel, the corners, our outputs) the
  // text moves to `data-nbtip` while the pointer is on the element, the
  // browser has nothing to show, and one bubble `.nbtip` shows it in the
  // skin's surface, ink, line and font. On leaving, `title` comes back, so
  // everything that reads or syncs titles (patch(), tests) sees them as
  // before. The look here is a sketch in the skin variables; the CSS
  // workshop can take `.nbtip` over (the !important-free inline style yields
  // to any rule with !important).
  if (window.__nbTipTeardown) { try { window.__nbTipTeardown(); } catch (e) {} }
  // 2026-10-03 (E21.3, Applikation) — ONE BUBBLE IN THE PAGE. Every run of
  // the notebook (Restart Kernel and Run All, ▶ in ⚙, a second notebook)
  // runs this script again; the teardown only took the listeners away and
  // the old `.nbtip` stayed in <body>, never shown again. The page then held
  // two bubbles, and whatever reads "the" bubble read the dead one — the
  // regress test saw the YOC box empty after a rerun although it was drawn
  // (J3, runner row Modeling cyber dark). Bubbles of earlier runs go now.
  [].forEach.call(document.querySelectorAll('.nbtip'), function(e){ if (e.parentNode) e.parentNode.removeChild(e); });
  var tipEl = null, tipOn = null, tipT = null;
  var tipScope = '#nbpanel-root, .jp-OutputArea-output, .nbtitle';
  // E16.7: in full screen (⛶) only the full-screen panel is drawn; a
  // bubble made before in <body> stayed there, unseen — the YOC mark "had
  // no box". It moves to whatever is on screen now.
  function tipBubble(){
    var fsP = document.fullscreenElement || document.body;
    if (tipEl && tipEl.isConnected && tipEl.parentNode !== fsP) fsP.appendChild(tipEl);
    if (!tipEl || !tipEl.isConnected) {
      tipEl = document.createElement('div');
      tipEl.className = 'nbtip';
      tipEl.setAttribute('role', 'tooltip');
      // R3 · 17 Teil 2: only WHERE it is is the script's; how it looks is
      // the stylesheet's `.nbtip` / `.nbtip.on` (R2 finding: the inline look
      // beat every rule without !important)
      tipEl.style.cssText = 'position:fixed;z-index:3000;pointer-events:none;';
      (document.fullscreenElement || document.body).appendChild(tipEl);
    }
    return tipEl;
  }
  function tipShow(el){
    if (tipOn !== el || !el.isConnected) return;
    var b = tipBubble();
    b.textContent = el.getAttribute('data-nbtip') || '';
    var r = el.getBoundingClientRect(), bw = b.offsetWidth, bh = b.offsetHeight;
    var x = Math.round(r.left + r.width / 2 - bw / 2);
    x = Math.max(6, Math.min(x, window.innerWidth - bw - 6));
    var y = Math.round(r.bottom + 8);
    if (y + bh > window.innerHeight - 6) y = Math.round(r.top - bh - 8);
    b.style.left = x + 'px'; b.style.top = Math.max(6, y) + 'px';
    b.classList.add('on');        // the CSS workshop's hook (R2 · 17)
  }
  function tipOut(){
    clearTimeout(tipT);
    if (tipEl) tipEl.classList.remove('on');
    if (tipOn && tipOn.__nbTipBack && !tipOn.getAttribute('title'))
      tipOn.setAttribute('title', tipOn.getAttribute('data-nbtip') || '');
    tipOn = null;
  }
  function tipOver(ev){
    var el = ev.target && ev.target.closest ? ev.target.closest('[title],[data-nbtip]') : null;
    if (el === tipOn) return;
    tipOut();
    if (!el || !el.closest(tipScope)) return;
    var t = el.getAttribute('title');
    if (t) { el.setAttribute('data-nbtip', t); el.removeAttribute('title'); el.__nbTipBack = true; }
    // 2026-10-01 (E12.4, Struktur) — THE YOC MARK SAYS WHAT A CLICK DOES:
    // its hover box reads "＋ Add your cell" (a click makes one, on the line)
    if (el.matches('#nbpanel-root .nbmap-node.cell[data-acc="yoc"]'))
      el.setAttribute('data-nbtip', window.__nbDe() ? '\uFF0B Eigene Zelle anlegen' : '\uFF0B Add your cell');   // py-E23.1
    if (!el.getAttribute('data-nbtip')) return;
    tipOn = el;
    tipT = setTimeout(function(){ tipShow(el); }, 350);
  }
  document.addEventListener('mouseover', tipOver, true);
  document.addEventListener('pointerdown', tipOut, true);
  document.addEventListener('wheel', tipOut, {capture: true, passive: true});
  // 2026-10-05 (E22.7, Struktur) — THE YOC MARK SHOWS THE BOX IN THE
  // DOCUMENT. Hovering the strip under the document (JupyterLab's
  // `.jp-Notebook-footer`, styled "＋ Add your own coding cell", 05-document)
  // shows it; hovering the YOC mark on the timeline only showed the small
  // tooltip at the mark (video 4, Modeling dark, title shut). The mark stands
  // at the strip's height (the rail is 1:1 with the page), so the strip is in
  // view whenever the mark is: hovering the mark now gives the strip
  // `nbyoc-hot`, the same look as its own hover (05-document), until the
  // pointer leaves the mark. The tooltip at the mark stays (E12.4).
  var yocHot = null;
  function yocHotOff(){ if (yocHot) { yocHot.classList.remove('nbyoc-hot'); yocHot = null; } }
  function yocHover(ev){
    var t = ev.target;
    var m = t && t.closest ? t.closest('#nbpanel-root .nbmap-node.cell[data-acc="yoc"]') : null;
    var P = m ? frontPanel() : null;
    var f = P ? P.querySelector('.jp-Notebook-footer') : null;
    if (yocHot && yocHot !== f) yocHotOff();
    if (f && !f.classList.contains('nbyoc-hot')) { f.classList.add('nbyoc-hot'); yocHot = f; }
  }
  function yocLeave(ev){ if (!ev.relatedTarget) yocHotOff(); }
  document.addEventListener('mouseover', yocHover, true);
  document.addEventListener('mouseout', yocLeave, true);
  window.__nbTipTeardown = function(){
    yocHotOff();
    document.removeEventListener('mouseover', yocHover, true);
    document.removeEventListener('mouseout', yocLeave, true);
    tipOut();
    if (tipEl && tipEl.parentNode) tipEl.parentNode.removeChild(tipEl);   // E21.3
    document.removeEventListener('mouseover', tipOver, true);
    document.removeEventListener('pointerdown', tipOut, true);
    document.removeEventListener('wheel', tipOut, {capture: true, passive: true});
  };
})();
