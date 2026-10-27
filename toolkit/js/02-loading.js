// 2026-09-28 (Eilauftrag E5.1, Applikation + Oberfläche) — THE START IS ONE
// PICTURE, NOT A BUILD YOU WATCH.
// After Play the document used to assemble itself in front of the reader:
// JupyterLab follows the running cell to the bottom, every chapter pops in,
// then goTop pulls the page back up (video of the user, 28.09.). Now the very
// first thing the notebook's cell shows is a loading view laid over its own
// notebook panel: the title, a bar that fills and a row of the marks of the
// timeline that light up one by one. It lifts — softly — only when the run is
// over, the panel is there and the page has stood still at the top (title mark
// on the reading line) for a moment. The Play button calls it too, the instant
// it is clicked. Nothing here moves the document; it only hides the moving.
(function(el){
  var W = window, D = document, V = '__NBLOADV__';
  var IDE = '__NBIDEARLY__';         // E35 J1: the notebook's id (build: build_*.py), unreplaced = none
  function panelOf(node){
    return node && node.closest ? node.closest('.jp-NotebookPanel') : null;
  }
  // 2026-10-19 (E35 J1, JavaScript) — THE LOOK BEFORE THE FIRST PICTURE. Nutzer 19.10.: after Run a
  // light minimal card stood on black, then the page turned digi. Measured v1.80 (Lab light, fresh):
  // for the whole run (≈ 12 s of installer + build) the body carried no style class and no `nbdark` —
  // applySkin/applyTheme (15-rail-theme) run only in the panel's sync, and the panel is the cell's LAST
  // output; the loading view drew in minimal's light colours over the notebook. This script is the
  // cell's FIRST output, so it now sets what the panel will set, the moment it runs: the style class,
  // light/dark (`nbdark`, `nbforce-*`), and our mark on the panel (`data-digichem`, `nb-dc-active`,
  // the contract with CSS). It reads the same keys with the same rules and writes nothing — the
  // panel's applySkin/applyTheme stay the only writers, and come to the same answer.
  // Only for the notebook in front, only for a panel of ours (cover, title or feed in it).
  function early(node){
    try {
      var p = panelOf(node) || D.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
      if (!p || p.classList.contains('lm-mod-hidden')) return false;
      // the panel of this script's own output is ours by construction (only our cell emits it)
      if (!(panelOf(node) || p.getAttribute('data-digichem') === '1' || p.querySelector('.nbfeed, .nbcover, .nbtitle-h, .nbstart'))) return false;
      // the notebook's id as the panel will read it: the last feed (nbId0), else the cover's class
      var id = '', fs = p.querySelectorAll('.nbfeed[data-progress]'), m;
      try { id = JSON.parse(fs[fs.length - 1].getAttribute('data-progress')).id || ''; } catch (e) {}
      id = String(id).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
      // … else the id the build wrote into this script (the cold cell holds only the start line), else the cover's class
      if (!id && !/^__NB/.test(IDE)) id = IDE;
      if (!id) { var cv = p.querySelector('.nbcover'); m = cv && /\bnbid-([a-z0-9-]+)/.exec(cv.className || ''); id = m ? m[1] : ''; }
      var get = function(k){ if (!id) return null; try { return localStorage.getItem('digichemjn.' + k + '.v1.' + id); } catch (e) { return null; } };
      var DEF = W.__nbDEF || {skin: 'digi', theme: 'dark'};       // = NB_DEF (12-rail-series-role)
      var SK = ['digi', 'cyber', 'fairy'], sk = get('skin');     // skinPref(): nothing stored → the standard
      sk = sk == null || sk === '' ? DEF.skin : (sk === 'retro' ? 'minimal' : sk);
      var b = D.body, i;
      for (i = 0; i < SK.length; i++) b.classList.toggle('nbskin-' + SK[i], SK[i] === sk);
      b.classList.remove('nbskin-retro');
      // applyTheme(): the front end's state is news only if it differs from the one this notebook saw
      var lab = b.getAttribute('data-jp-theme-light');
      var labDark = lab === 'false' || /Dark/.test(b.getAttribute('data-jp-theme-name') || '');
      var pref = get('theme'), seen = get('themeseen');
      if (pref !== 'dark' && pref !== 'light') pref = '';
      if (lab !== null) {
        if (seen == null && !pref) pref = '';
        else if (seen == null ? lab !== W.__nbThemeSeen : lab !== seen) pref = labDark ? 'dark' : 'light';
      }
      if (!pref) pref = DEF.theme === 'light' || DEF.theme === 'dark' ? DEF.theme : (labDark ? 'dark' : 'light');
      var dark = pref === 'dark' && !W.__nbPrintSaved;
      b.classList.toggle('nbdark', dark);
      b.classList.toggle('nbforce-dark', dark && !labDark);
      b.classList.toggle('nbforce-light', !dark && labDark);
      if (p.getAttribute('data-digichem') !== '1') p.setAttribute('data-digichem', '1');
      b.classList.add('nb-dc-active');
      return true;
    } catch (e) { return false; }
  }
  W.__nbEarlyLook = early;
  if (el) early(el);                // E35 J1: at once (the notebook in front, if the output is not attached yet)
  var earlyEl = false;
  if (!W.__nbLoading || W.__nbLoading.v !== V) {
    var L = W.__nbLoading = {v: V, box: null, panel: null, t0: 0, busy: false,
                             timer: null, calm: 0, names: []};
    L.css = function(){
      // E35 J1: an older build's sheet (other version) is rewritten, not kept
      var s = D.getElementById('nbload-css');
      if (s && s.getAttribute('data-v') === V) return;
      if (!s) { s = D.createElement('style'); s.id = 'nbload-css'; }
      s.setAttribute('data-v', V);
      s.textContent =
        '#nbload{position:fixed;z-index:10050;display:flex;flex-direction:column;' +
        'align-items:center;justify-content:center;gap:18px;' +
        'background:var(--nbskin-surf,#f8fafb);color:var(--nbskin-ink,#33475b);' +
        'font-family:var(--nbskin-font,inherit);opacity:1;transition:opacity .55s ease;}' +
        'body.nbdark #nbload,body[data-jp-theme-light="false"] #nbload{' +
        'background:var(--nbskin-surf,#1f252c);color:var(--nbskin-ink,#dbe2e9);}' +
        '#nbload.nbload-out{opacity:0;pointer-events:none;}' +
        '#nbload .nbload-t{font-size:30px;font-weight:800;letter-spacing:.3px;}' +
        '#nbload .nbload-track{position:relative;width:min(360px,70%);height:8px;border-radius:8px;' +
        'background:color-mix(in srgb,currentColor 12%,transparent);overflow:visible;}' +
        '#nbload .nbload-fill{position:absolute;left:0;top:0;bottom:0;width:0;border-radius:8px;' +
        'background:linear-gradient(90deg,var(--nbskin-acc,#2c6e91),var(--nbskin-acc2,#3fa877));' +
        'transition:width .35s ease;}' +
        '#nbload .nbload-spark{position:absolute;top:50%;right:-7px;width:14px;height:14px;' +
        'margin-top:-7px;border-radius:50%;background:var(--nbskin-acc2,#3fa877);' +
        'box-shadow:0 0 12px 3px color-mix(in srgb,var(--nbskin-acc2,#3fa877) 60%,transparent);' +
        'animation:nbload-hop .9s ease-in-out infinite;}' +
        '@keyframes nbload-hop{0%,100%{transform:translateY(0) scale(1);}' +
        '50%{transform:translateY(-9px) scale(.8);}}' +
        '#nbload .nbload-marks{display:flex;gap:9px;align-items:center;height:18px;}' +
        '#nbload .nbload-mk{width:10px;height:10px;border-radius:3px;opacity:.22;' +
        'background:currentColor;transition:opacity .3s ease,transform .3s ease,background .3s ease;}' +
        '#nbload .nbload-mk.x{transform:rotate(45deg) scale(.85);}' +
        '#nbload .nbload-mk.on{opacity:1;background:var(--nbskin-acc,#2c6e91);transform:scale(1.35);}' +
        '#nbload .nbload-mk.x.on{transform:rotate(45deg) scale(1.2);}' +
        '#nbload .nbload-say{font-size:13px;letter-spacing:.4px;opacity:.72;min-height:1.3em;}' +
        '@media (prefers-reduced-motion:reduce){#nbload .nbload-spark{animation:none;}}' +
        // E35 J1: the view runs ≈ 12 s before the stylesheet exists, so under digi its own
        // fall-backs are digi's (07-skins: surf/ink/acc/acc2); once the sheet is there, its tokens win
        'body.nbskin-digi:not(.nbdark) #nbload{background:var(--nbskin-surf,#ffffff);color:var(--nbskin-ink,#141826);}' +
        'body.nbdark.nbskin-digi #nbload{background:var(--nbskin-surf,#0b0e1c);color:var(--nbskin-ink,#e9ecf6);}' +
        'body.nbskin-digi #nbload .nbload-fill{background:linear-gradient(90deg,var(--nbskin-acc,#ffd36b),var(--nbskin-acc2,#7fb4ff));}' +
        'body.nbskin-digi #nbload .nbload-spark{background:var(--nbskin-acc2,#7fb4ff);' +
        'box-shadow:0 0 12px 3px color-mix(in srgb,var(--nbskin-acc2,#7fb4ff) 60%,transparent);}' +
        'body.nbskin-digi #nbload .nbload-mk.on{background:var(--nbskin-acc,#ffd36b);}' +
        'body.nbskin-digi:not(.nbdark) #nbload .nbload-fill{background:linear-gradient(90deg,var(--nbskin-acc,#9a6b00),var(--nbskin-acc2,#2a5bc8));}' +
        'body.nbskin-digi:not(.nbdark) #nbload .nbload-mk.on{background:var(--nbskin-acc,#9a6b00);}';
      if (!s.parentNode) D.head.appendChild(s);
    };
    // the reader's own panel: cover the notebook area under JupyterLab's
    // toolbar, follow the window, step aside when another tab is in front
    L.place = function(){
      var b = L.box, p = L.panel;
      if (!b) return;
      if (!p || !p.isConnected || p.classList.contains('lm-mod-hidden')) {
        b.style.display = 'none'; return;
      }
      var r = p.getBoundingClientRect(), tb = p.querySelector('.jp-NotebookPanel-toolbar');
      var top = tb ? tb.getBoundingClientRect().bottom : r.top;
      if (r.width < 2 || r.height < 2) { b.style.display = 'none'; return; }
      b.style.display = 'flex';
      b.style.left = r.left + 'px'; b.style.top = top + 'px';
      b.style.width = r.width + 'px'; b.style.height = Math.max(0, r.bottom - top) + 'px';
    };
    L.show = function(node, running){
      var p = panelOf(node) || L.panel;
      if (!p) return;
      L.css();
      if (!L.box || !L.box.isConnected) {
        var b = L.box = D.createElement('div'); b.id = 'nbload';
        b.setAttribute('role', 'status'); b.setAttribute('aria-live', 'polite');
        var h = p.querySelector('.nbtitle-h');
        // py-E23.1: in the reader's language (the run's feed, else the stored choice)
        var deL = false;
        try { var fL = D.querySelector('.nbfeed[data-nblang]');
              deL = fL ? fL.getAttribute('data-nblang') === 'de' : !!W.__nbStore && W.__nbStore.get('digichemjn.lang.v1') === 'de'; } catch (e) {}   // E25.o
        // E29 P1: the language chosen on the preview first (Play builds it), and a
        // text of the two-language cover (py-E29: span[data-nbl]) in that language only
        try { if (W.__nbAcct) deL = W.__nbAcct.lang() === 'de'; } catch (e) {}
        var one = function(e){ var x = e && e.querySelector('[data-nbl="' + (deL ? 'de' : 'en') + '"]'); return (x || e).textContent; };
        var tl = [].slice.call(p.querySelectorAll('.nbcover-tl .nbtl-row'));
        L.names = tl.filter(function(r){ return /nbtl-(chapter|task|coding|figure)/.test(r.className); })
                    .map(function(r){ var m = r.querySelector('.nbtl-nm'); return m ? one(m) : ''; });
        var marks = tl.length ? tl.filter(function(r){ return /nbtl-(chapter|task)/.test(r.className); }) : [];
        var mk = marks.length ? marks.map(function(r){
                   return '<i class="nbload-mk' + (/nbtl-task/.test(r.className) ? ' x' : '') + '"></i>'; }).join('')
                 : new Array(9).join('<i class="nbload-mk"></i>');
        b.innerHTML = '<div class="nbload-t"></div>' +
          '<div class="nbload-track"><div class="nbload-fill"><i class="nbload-spark"></i></div></div>' +
          '<div class="nbload-marks">' + mk + '</div><div class="nbload-say"></div>';
        b.querySelector('.nbload-say').textContent = deL ? 'Das Notebook wird aufgebaut …' : 'Building the notebook…';
        b.querySelector('.nbload-t').textContent = h ? one(h) : (deL ? 'Laden' : 'Loading');
        D.body.appendChild(b);
        L.t0 = Date.now(); L.calm = 0; L.idle = 0; L.asked = false; L.seen = false;
        W.__nbTopStarted = false;
      }
      L.box.classList.remove('nbload-out');
      L.panel = p;
      // a run we know is running (the cell itself called us) counts as seen busy
      L.busy = !!running || L.busy;
      L.place();
      if (!L.timer) L.timer = setInterval(L.tick, 200);
    };
    L.running = function(){
      var p = L.panel; if (!p) return false;
      var ind = p.querySelector('.jp-Notebook-ExecutionIndicator');
      var st = ind && ind.getAttribute('data-status');
      if (st) return st !== 'idle';
      return !!p.querySelector('.jp-Cell.jp-mod-running, .jp-InputPrompt:not(:empty)') &&
             /\*/.test((p.querySelector('.jp-CodeCell .jp-InputPrompt') || {}).textContent || '');
    };
    L.tick = function(){
      var b = L.box; if (!b) { clearInterval(L.timer); L.timer = null; return; }
      L.place();
      var t = (Date.now() - L.t0) / 1000;
      var run = L.running(); if (run) { L.busy = true; L.seen = true; }
      // E8.15: a view that has never seen the kernel work in 6 s is not
      // covering a run — it is the saved picture of an old one. It goes.
      if (!L.seen && t > 6) { L.hide(); return; }
      // E26.1: the run is over, the reading version is there and no widget of
      // ours is drawn (no widget component here): nothing to wait for
      if (t > 4 && !run && L.panel && L.panel.querySelector('.nbreading') && !L.panel.querySelector('.acc-root')) { L.hide(); return; }
      var p = L.panel, host = D.getElementById('nbpanel-root');
      var ready = L.busy && !run && !!(host && host.querySelector('.nbmap'));
      if (!ready) L.idle = 0; else L.idle = (L.idle || 0) + 200;
      // goTop (E4.3) puts the reader on the title mark after a start; should
      // it not have come within 2.5 s of the end, ask for it once
      if (ready && !W.__nbTopStarted && L.idle >= 2500 && !L.asked) {
        L.asked = true; try { W.__nbGoTop && W.__nbGoTop(); } catch (e) {}
      }
      var sc = p && p.querySelector('.jp-WindowedPanel-outer');
      // E9.2: "the top" is the title on the line, under the air (__nbTopAt)
      if (ready && sc && Math.abs(sc.scrollTop - (W.__nbTopAt || 0)) <= 1
          && (W.__nbTopStarted || L.asked)) L.calm += 200;
      else L.calm = 0;
      // the bar: fills towards 90 % while it waits, the rest when it is done
      var done = L.calm >= 800 || t > 120;
      var f = done ? 100 : Math.min(90, 90 * (1 - Math.exp(-t / 7)));
      var fill = b.querySelector('.nbload-fill'); if (fill) fill.style.width = f + '%';
      var mks = b.querySelectorAll('.nbload-mk'), n = mks.length;
      var lit = done ? n : Math.floor(t * 3) % (n + 3);
      for (var i = 0; i < n; i++) mks[i].classList.toggle('on', i < lit);
      var say = b.querySelector('.nbload-say');
      if (say && L.names.length && !done)
        say.textContent = L.names[Math.floor(t * 1.4) % L.names.length] + ' …';
      if (done) L.hide();
    };
    L.hide = function(){
      var b = L.box; if (!b) return;
      clearInterval(L.timer); L.timer = null; L.box = null; L.busy = false;
      var say = b.querySelector('.nbload-say'); if (say) say.textContent = 'Ready';
      setTimeout(function(){ b.classList.add('nbload-out'); }, 250);
      setTimeout(function(){ if (b.parentNode) b.parentNode.removeChild(b); }, 900);
    };
    W.addEventListener('resize', function(){ if (L.box) L.place(); });
  }
  // the output is not in the page yet when this runs: wait for it (≤ 3 s),
  // then fall back to the notebook in front
  // 2026-09-29 (E8.15, Applikation) — ONLY OVER A RUN THAT IS RUNNING.
  // This script is an OUTPUT of the notebook's cell, so it is saved with the
  // file and runs again whenever the saved notebook is opened — with no run
  // behind it. Measured in the real JupyterLab (saved with outputs, kernels
  // shut, page reloaded): the kernel came back idle, the panel never came
  // (no widgets without a run), and the view waited for its 120-s fallback
  // (the reader's "≈ 3 minutes"), hiding the cover and its Play button. It
  // now shows only when its own cell is executing ("[*]") or the kernel is
  // busy; otherwise the cover stays until Play (which shows it itself).
  function live(node){
    var c = node && node.closest ? node.closest('.jp-Cell') : null;
    var pr = c && c.querySelector('.jp-InputPrompt');
    if (pr && /\*/.test(pr.textContent || '')) return true;
    // Complex hides its prompts: the kernel's own state is the signal. While
    // the page is still loading it is "initializing", "connecting" or
    // "unknown" — busy only while it runs code.
    var p = panelOf(node);
    var ind = p && p.querySelector('.jp-Notebook-ExecutionIndicator');
    return !!(ind && ind.getAttribute('data-status') === 'busy');
  }
  // 2026-10-06 (E24.3, JavaScript) — and it notes on the panel that a run
  // RAN here: the cover output comes up first after such a run (19-rail
  // covOn), never over outputs that were only opened with the file.
  function ran(node){ var p = panelOf(node); if (p) p.__nbRan = Date.now(); }
  if (el) (function wait(n){
    if (el.isConnected && panelOf(el)) {
      if (!earlyEl) { earlyEl = true; early(el); }                    // E35 J1: and on its own panel
      return live(el) ? (ran(el), W.__nbLoading.show(el, true)) : null;
    }
    if (n > 60) { var nb0 = D.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook');
                  return nb0 && live(nb0) ? (ran(nb0), W.__nbLoading.show(nb0, true)) : null; }
    // E35 J1: the first looks before the next paint (the output is attached right after this script),
    // so the loading view stands in the same picture as the output; then every 50 ms as before
    if (n < 6 && W.requestAnimationFrame) { if (n === 0) Promise.resolve().then(function(){ wait(1); }); else W.requestAnimationFrame(function(){ wait(n + 1); }); return; }
    setTimeout(function(){ wait(n + 1); }, 50);
  })(0);
})(typeof element !== 'undefined' ? (element && element.jquery ? element[0] : element) : null);
