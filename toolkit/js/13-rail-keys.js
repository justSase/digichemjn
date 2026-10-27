      // ====================================================================
      // 2026-09-25f — THE KEYBOARD.
      // 2026-09-25h — REPLACED BY A MODE. The Alt chords of 25f are gone.
      //
      // Why a mode and not chords: every chord is one more question "is this
      // taken?" — asked again for every browser, every OS, every layout and
      // every JupyterLab release. On macOS the question was already lost:
      // Option+J is a character there, ev.key reads '∆', and none of the 25f
      // chords reached the table. A mode asks the question ONCE, for the chord
      // that enters it.
      //
      // THE MODE IS FOCUS. The panel host is a focusable element that lives on
      // <body>, outside every notebook. JupyterLab's command-mode keys are
      // bound to selectors inside `.jp-Notebook`, so while the host has the
      // focus they cannot match — the collision disappears by construction,
      // not key by key. Only JupyterLab's GLOBAL bindings (selector `body`)
      // still see the keys we do not take, and those carry a modifier.
      //
      // ENTRY: Alt+. from anywhere (command mode, edit mode, an answer field),
      // matched on ev.code, so Option+. on a Mac ('…') is the same key.
      // MEASURED in JupyterLab 4.6.4 / Chromium / Linux, command mode, an
      // answer field and a code cell in edit mode: Alt+., Ctrl+Alt+P and F2
      // all had no effect before we took one; the first of the three wins.
      // A click into the panel enters as well — the host has tabindex -1, so a
      // click anywhere on it moves the focus there.
      // LEAVE: Esc, or Alt+. again. The focus goes back where it came from.
      //
      // ONE TABLE. The handler dispatches FROM it and the list is rendered
      // FROM it, so a key cannot work without being listed or be listed
      // without working. `g` is the group for the list: move · do · view.
      // 2026-09-29 (E6.1 + E6.4, Applikation) — EVERY KEY, SHORT WORDS.
      // The list holds every key the notebook answers to, also the ones
      // outside the document (corners, drawer, lens, help window), so the
      // Controls window (⌨ / ?) is complete. Rows without `key` are listed
      // only — their handlers live elsewhere (zoom, wheel, corners, fields).
      // Texts: a few words each (E6.4, "weniger Text").
      // group `g`: enter = anywhere · corner = corners and windows ·
      // move / do / view = in keyboard mode (Alt+.)
      var KEYS = [
        {k: 'Alt+.',     g: 'enter', t: 'keyboard mode',   d: 'on / off'},
        {k: 'Ctrl + / \u2212', g: 'enter', t: 'zoom',      d: 'Ctrl+0: 100 %'},
        {k: 'Ctrl+wheel', g: 'enter', t: 'zoom'},
        {k: 'Wheel',     g: 'enter', t: 'scroll'},
        {k: 'Enter',     g: 'enter', t: 'send', d: 'in an answer field'},
        {k: 'Tab',       g: 'corner', t: 'next corner sign'},
        {k: '\u2191 \u2193', g: 'corner', t: 'step through a corner'},
        {k: 'Home / End', g: 'corner', t: 'first / last widget'},
        {k: 'Enter / Space', g: 'corner', t: 'open the widget'},
        {k: '\u2190 \u2192', g: 'corner', t: 'lens smaller / bigger'},
        {k: 'Esc',       g: 'corner', t: 'close the window'},
        {k: 'J',         g: 'move',  t: 'next mark',            key: 'j',  a: 'next'},
        {k: 'K',         g: 'move',  t: 'mark before',          key: 'k',  a: 'prev'},
        // 2026-09-27e — the arrows as the same two steps (C2). Only in the
        // panel's own mode: outside it they are JupyterLab's and the page's.
        {k: '\u2193',    g: 'move',  t: 'next mark',            key: 'ArrowDown', a: 'next'},
        {k: '\u2191',    g: 'move',  t: 'mark before',          key: 'ArrowUp',   a: 'prev'},
        {k: '1 \u2013 9', g: 'move', t: 'chapter 1 \u2013 9', key: '#', a: 'chap'},
        {k: 'G',         g: 'move',  t: 'next open exercise',   key: 'g', a: 'open'},
        // R3 · 20 — the bookmark: where you stopped reading (🔖 on the timeline)
        {k: 'B',         g: 'move',  t: 'bookmark',             d: 'where you stopped', key: 'b', a: 'bookmark'},
        {k: 'Enter',     g: 'do',    t: 'go in',                d: 'into the answer field', key: 'Enter', a: 'go'},
        {k: 'A',         g: 'do',    t: 'send the answer',      key: 'a', a: 'send'},
        // R3 · 19 (C) — H: the next step of the hint of the exercise the
        // keyboard is on (the `.nbhint-btn` of the Inhalt patches, v1.19)
        {k: 'H',         g: 'do',    t: 'hint',                 d: 'next step', key: 'h', a: 'hint'},
        {k: 'Esc',       g: 'do',    t: 'leave keyboard mode',  key: 'Escape', a: 'leave'},
        {k: 'D',         g: 'view',  t: 'light / dark',         key: 'd', a: 'theme'},
        {k: 'S',         g: 'view',  t: 'next style',           key: 's', a: 'skin'},
        {k: 'P',         g: 'view',  t: 'panel wide / narrow',  key: 'p', a: 'panel'},
        {k: 'F',         g: 'view',  t: 'full screen',          key: 'f', a: 'full'},
        {k: '?',         g: 'view',  t: 'this window',          d: 'open / close', key: '?', a: 'help'}
      ];
      window.__nbKeys = KEYS;
      function keyRows(){
        return '<div class="nbkeylist">' + KEYS.map(function(r){
          return '<div class="nbkeyrow" data-g="' + (r.g || '') + '"><kbd>' + r.k + '</kbd>'
               + '<span class="kt">' + r.t + '</span>'
               + '<span class="kd">' + (r.d || '') + '</span></div>';
        }).join('') + '</div>';
      }
      window.__nbKeyRows = keyRows;
      // the marks the reader can actually travel between, in rail order
      function navNodes(){
        var h = document.getElementById(HOST_ID);
        if (!h) return [];
        return [].filter.call(h.querySelectorAll('.nbmap-node'), function(n){
          return !n.classList.contains('nbgone');
        });
      }
      // MEASURED: stepping from `.here` works going forward and fails going
      // back. `.here` is the READING position — it snaps to whichever mark the
      // document is nearest — so after a hop to mark 1, two marks that sit
      // close together in the document leave `.here` on mark 2, and the next
      // Alt+K computes "one before 2" and lands on 2 again. The reader presses
      // a key twice and nothing moves.
      // So the keyboard keeps its own place. It starts from the reading
      // position, and after that each press steps from where the LAST press
      // went — which is what a keyboard is expected to do. Clicking a mark, or
      // scrolling to somewhere else entirely, hands the place back to `.here`.
      function keyAt(ns){
        var j;
        if (window.__nbKeyAt != null && ns[window.__nbKeyAt]) return window.__nbKeyAt;
        for (j = 0; j < ns.length; j++)
          if (ns[j].classList.contains('here')) return j;
        for (j = 0; j < ns.length; j++)
          if (ns[j].classList.contains('nbsel')) return j;
        return -1;
      }
      // the keyboard's own click, marked as such so onJump does not read it as
      // the reader taking over and drop the place we just set
      function goTo(node, at){
        window.__nbKeyAt = at;
        window.__nbKeyNav = true;
        try { node.click(); } finally { window.__nbKeyNav = false; }
      }
      function hop(dir){
        var ns = navNodes();
        if (!ns.length) return;
        var i = keyAt(ns);
        var want = Math.max(0, Math.min(ns.length - 1, (i < 0 ? 0 : i + dir)));
        goTo(ns[want], want);
      }
      function hopOpen(){
        // the next EXERCISE that is neither answered nor given up, from where
        // the reader is now — the one question "what is left for me" asks
        var ns = navNodes(), i = keyAt(ns), j;
        for (j = i + 1; j < ns.length; j++) {
          var d = ns[j].querySelector('.nbrail-dot.st-open, .nbcodemark.cd-open');
          if (d) { goTo(ns[j], j); return; }
        }
        for (j = 0; j <= i && j < ns.length; j++) {   // wrap round
          var d2 = ns[j].querySelector('.nbrail-dot.st-open, .nbcodemark.cd-open');
          if (d2) { goTo(ns[j], j); return; }
        }
      }
      function hopChapter(dir){
        var all = navNodes();
        var ns = all.filter(function(n){ return n.classList.contains('chap'); });
        if (!ns.length) return;
        var i = keyAt(all), j, best = null, bestAt = -1;
        for (j = 0; j < ns.length; j++) {
          var at = all.indexOf(ns[j]);
          if (dir < 0 ? at < i : at > i) {
            best = ns[j]; bestAt = at;
            if (dir > 0) break;          // forwards: the FIRST one past here
          }                              // backwards: keep the LAST one before
        }
        if (best) goTo(best, bestAt);
      }
      function keysPage(){
        var h = document.getElementById(HOST_ID);
        if (!h) return;
        var was = h.classList.contains('open') && h.dataset.page === 'keys';
        h.dataset.page = 'keys';
        h.classList.toggle('open', !was);
        var slot = h.querySelector('.nbkeys-slot');
        if (slot && !was) slot.innerHTML = keyRows();
        try { placeDock(h, activeSrc()); } catch (e) {}   // R3 · 17b: drawer at its widget
        setTimeout(function(){ measure(h); gauge(h); }, 380);
      }
      window.__nbKeysPage = keysPage;
      var press = function(sel){
        var h = document.getElementById(HOST_ID);
        var b = h && h.querySelector(sel);
        if (b) b.click();
      };
      // the Check (or Run & check) button that belongs to a field: the nearest
      // ancestor that holds one. 25f looked for the nearest `.widget-box` and
      // stopped there — a number field sits in an HBox of its own, the button
      // one level further out, so the search ended before it got there.
      function checkBtnFor(f){
        var e = f && f.parentElement, n = 0;
        while (e && n < 12 && !(e.classList && e.classList.contains('jp-OutputArea'))) {
          var b = e.querySelector('button.sc-btn');
          if (b) return b;
          e = e.parentElement; n++;
        }
        return null;
      }
      if (!window.__nbKeysArmed) {
        window.__nbKeysArmed = true;
        document.addEventListener('keydown', function(ev){
          // ENTER IN AN ANSWER FIELD SENDS IT. No modifier, no global binding:
          // the key never leaves the input, so the front end cannot be robbed
          // of anything. (Alt+Enter would have been the obvious spelling and
          // is exactly the one that is taken.)
          if (ev.key === 'Enter' && !ev.altKey && !ev.ctrlKey && !ev.metaKey) {
            var f = ev.target;
            if (!f || !f.tagName) return;
            var tag = f.tagName.toLowerCase();
            if (tag !== 'input') return;
            // only the fields an answer is typed or picked in — a slider is not
            // an answer, and the nearest Check button to a slider may belong to
            // the exercise next to it
            var ty = (f.type || '').toLowerCase();
            if (ty !== 'number' && ty !== 'text' && ty !== 'radio') return;
            if (!f.closest('.jp-OutputArea')) return;
            var fn = window.__nbCheckBtnFor || checkBtnFor;
            var btn = fn(f);
            if (!btn) return;
            ev.preventDefault(); ev.stopPropagation();
            btn.click();
          }
        }, true);
      }
      window.__nbCheckBtnFor = checkBtnFor;

      // ---- the keyboard mode ------------------------------------------------
      function kbdHost(){
        var h = document.getElementById(HOST_ID);
        return (h && h.classList.contains('ready')) ? h : null;
      }
      function kbdOn(h){ h = h || kbdHost(); return !!(h && h.contains(document.activeElement)); }
      function kbdEnter(){
        var h = kbdHost();
        if (!h) return false;
        var ae = document.activeElement;
        if (ae && ae !== document.body && !h.contains(ae)) window.__nbKbdPrev = ae;
        h.setAttribute('tabindex', '-1');
        h.focus({preventScroll: true});
        return h.contains(document.activeElement);
      }
      function kbdLeave(){
        var h = document.getElementById(HOST_ID);
        var prev = window.__nbKbdPrev;
        window.__nbKbdPrev = null;
        if (prev && prev.isConnected && !(h && h.contains(prev))) {
          try { prev.focus({preventScroll: true}); } catch (e) {}
        }
        if (h && h.contains(document.activeElement)) {
          // nothing to go back to: the notebook on screen, in command mode
          var nb = document.querySelector('.jp-NotebookPanel.jp-mod-current .jp-Notebook')
                || document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook');
          if (nb) nb.focus({preventScroll: true});
          else if (document.activeElement && document.activeElement.blur) document.activeElement.blur();
        }
      }
      window.__nbKbdEnter = kbdEnter;
      window.__nbKbdLeave = kbdLeave;
      // the mark the keyboard is on, and the field / button after its anchor
      function kbdNode(){
        var ns = navNodes(), i = keyAt(ns);
        return i < 0 ? null : ns[i];
      }
      function anchorOf(node){
        var id = node && node.getAttribute('data-target');
        return id ? document.getElementById(id) : null;
      }
      function isTask(node){
        return !!(node && node.classList &&
                  (node.classList.contains('task') || node.classList.contains('codetask')));
      }
      function fieldAfter(node){
        var sp = anchorOf(node);
        if (!sp) return null;
        var scope = sp.closest('.jp-OutputArea') || sp.closest('.jp-Notebook') || document;
        // an ANSWER field: typed numbers or text, a picked option, a code box.
        // Not a slider — the mirrored panel's own zoom slider sits in the
        // document too, and was the first input after Start's anchors.
        var fs = scope.querySelectorAll('input[type=number], input[type=text], input[type=radio], textarea');
        for (var i = 0; i < fs.length; i++) {
          if (!(sp.compareDocumentPosition(fs[i]) & Node.DOCUMENT_POSITION_FOLLOWING)) continue;
          if (fs[i].closest('.Quiz, .nbrail, .nbfeed, #nbpanel-root')) continue;
          return fs[i];
        }
        return null;
      }
      function goIn(){
        var node = kbdNode();
        if (!node) return;
        var ns = navNodes();
        goTo(node, ns.indexOf(node));
        if (!isTask(node)) return;        // a heading: stay on the rail
        // 2026-09-28a (K1.2) — a task that waits has no field to go into: its
        // fold did not open, and the next field down belongs to another task
        if (node.querySelector('.cd-lock, .st-lock')) return;
        // the accordion opens and animates; the field is focusable once it is
        // laid out, so try a few times, and give up quietly
        var tries = [420, 800, 1300, 2000];
        tries.forEach(function(ms){
          setTimeout(function(){
            if (window.__nbKbdWentIn === node) return;
            var f = fieldAfter(node);
            if (!f) return;
            var r = f.getBoundingClientRect();
            if (!r.width || !r.height) return;
            window.__nbKbdWentIn = node;
            f.focus({preventScroll: true});
          }, ms);
        });
        window.__nbKbdWentIn = null;
      }
      // A sends only what the reader has TOUCHED. Measured in 25h: A on an
      // untouched number field sent its 0.0 and booked a wrong attempt — one
      // stray key changed the record, which is invariant 3 of D. A field counts
      // as touched once an input event came from it (typing, picking, pasting).
      function touched(f){
        var box = f && (f.closest('.widget-vbox') || f.parentElement);
        return !!(box && (f.hasAttribute('data-nbtouched') ||
                          box.querySelector('[data-nbtouched]')));
      }
      function sendIt(){
        var node = kbdNode();
        if (!isTask(node)) return;
        var f = fieldAfter(node);
        if (!f || !touched(f)) return;
        var b = checkBtnFor(f);
        if (b) b.click();
      }
      if (!window.__nbTouchArmed) {
        window.__nbTouchArmed = true;
        document.addEventListener('input', function(ev){
          var t = ev.target;
          if (t && t.closest && t.closest('.jp-OutputArea') &&
              /^(INPUT|TEXTAREA)$/.test(t.tagName)) t.setAttribute('data-nbtouched', '1');
        }, true);
      }
      // chapter n — ALL chapter marks, not only the ones drawn at this panel
      // size: a narrow horizontal rail hides them (nbgone) and 1 must still
      // mean chapter 1. A hidden mark cannot hold the keyboard's place, so the
      // place falls back to where the document lands (-1 -> .here).
      function chapN(n){
        var h = document.getElementById(HOST_ID);
        var cs = h ? h.querySelectorAll('.nbmap-node.chap') : [];
        if (n >= 1 && n <= cs.length) goTo(cs[n - 1], navNodes().indexOf(cs[n - 1]));
      }
      function panelToggle(){
        var v = guiLevel();
        if (v > 0) { window.__nbKbdGui = v; setGui(0); }
        else setGui(window.__nbKbdGui || 60);
      }
      // ---- R3 · 19 (C) — THE HELP WINDOW ---------------------------------
      // One window over the notebook (CSS 19 contract: .nbhelp-back + .nbhelp,
      // `.on` while open; .nbhelp-h/.nbhelp-t/.nbhelp-x, .nbhelp-body of
      // .nbhelp-sec, key lists ul.nbhelp-keys > li > kbd, .nbhelp-f). Opened by
      // ⌨ in the corner and by ? in keyboard mode; Esc, ? or × closes it and the
      // focus goes back where it was. The key list is rendered from KEYS, the
      // one table the handler dispatches from, so it cannot drift.
      // E6.4 — the corner signs in one or two words each
      var HELP_CORNER = [
        ['\u26f6', 'full screen'], ['\u25d0', 'light / dark'], ['\ud83c\udfa8', 'style'],
        ['\ud83d\udd0d', 'text size'], ['\ud83d\udcda', 'your statistics'],
        ['\ud83d\udc64', 'progress code'], ['\u2699', 'difficulty'], ['\u2328', 'this window']];
      function helpEsc(t){ return String(t).replace(/[&<>]/g, function(c){ return {'&': '&amp;', '<': '&lt;', '>': '&gt;'}[c]; }); }
      // py-E23.1 (Inhalt) — the window in the reader's language: every word of
      // KEYS and HELP_CORNER, the headings and the foot, by their English text
      var HELP_DE = {
        'keyboard mode': 'Tastaturmodus', 'on / off': 'an / aus', 'zoom': 'Lupe', 'Ctrl+0: 100 %': 'Strg+0: 100 %',
        'scroll': 'blättern', 'send': 'abschicken', 'in an answer field': 'in einem Antwortfeld',
        'next corner sign': 'nächstes Eckzeichen', 'step through a corner': 'durch eine Ecke gehen',
        'first / last widget': 'erstes / letztes Element', 'open the widget': 'Element öffnen',
        'lens smaller / bigger': 'Lupe kleiner / größer', 'close the window': 'Fenster schließen',
        'next mark': 'nächste Marke', 'mark before': 'Marke davor', 'chapter 1 \u2013 9': 'Kapitel 1 \u2013 9',
        'next open exercise': 'nächste offene Aufgabe', 'bookmark': 'Lesezeichen', 'where you stopped': 'wo Sie aufgehört haben',
        'go in': 'hinein', 'into the answer field': 'ins Antwortfeld', 'send the answer': 'Antwort abschicken',
        'hint': 'Hinweis', 'next step': 'nächster Schritt', 'leave keyboard mode': 'Tastaturmodus verlassen',
        'light / dark': 'hell / dunkel', 'next style': 'nächster Stil', 'panel wide / narrow': 'Panel breit / schmal',
        'full screen': 'Vollbild', 'this window': 'dieses Fenster', 'open / close': 'öffnen / schließen',
        'style': 'Stil', 'text size': 'Textgröße', 'your statistics': 'Ihre Statistik', 'progress code': 'Fortschrittscode',
        'difficulty': 'Schwierigkeit', 'Controls': 'Bedienung', 'close': 'schließen', 'close (Esc)': 'schließen (Esc)',
        'Corner signs': 'Eckzeichen', 'Timeline': 'Zeitleiste', 'Anywhere': 'Überall', 'Corners and windows': 'Ecken und Fenster',
        'Keyboard mode (Alt+.)': 'Tastaturmodus (Alt+.)', 'Esc, ? or \u00d7 closes': 'Esc, ? oder \u00d7 schließt',
        'Ctrl + / \u2212': 'Strg + / \u2212', 'Ctrl+wheel': 'Strg+Rad', 'Wheel': 'Rad', 'Enter': 'Eingabe',
        'Enter / Space': 'Eingabe / Leertaste', 'Home / End': 'Pos1 / Ende',
        '<p>Click a mark: go there. Click again: fold.<br>Marker = where you read. \ud83d\udd12 = do the exercise before.</p>':
          '<p>Ein Klick auf eine Marke: dorthin. Noch einmal: zuklappen.<br>Marker = wo Sie lesen. \ud83d\udd12 = erst die Aufgabe davor.</p>'};
      function helpHtml(){
        var deH = !!(window.__nbDe && window.__nbDe()), T = function(t){ return deH && HELP_DE[t] || t; };
        var title = '';
        try { title = (document.querySelector('#nbpanel-root .nbmap-node.title .nbmap-lab') || {}).textContent || ''; } catch (e) {}
        var li = function(k, t){ return '<li><kbd>' + helpEsc(T(k)) + '</kbd><span>' + helpEsc(t) + '</span></li>'; };
        var grp = function(g){ return KEYS.filter(function(r){ return r.g === g; })
                  .map(function(r){ return li(r.k, T(r.t) + (r.d ? ' \u00b7 ' + T(r.d) : '')); }).join(''); };
        var sec = function(h, body){ return '<div class="nbhelp-sec"><h4>' + T(h) + '</h4>' + body + '</div>'; };
        return '<div class="nbhelp-h"><span class="nbhelp-t" id="nbhelp-t">' + T('Controls') + (title ? ' \u00b7 ' + helpEsc(title) : '') + '</span>'
             + '<button class="nbhelp-x" type="button" aria-label="' + T('close') + '" title="' + T('close (Esc)') + '">\u00d7</button></div>'
             + '<div class="nbhelp-body">'
             + sec('Corner signs', '<ul class="nbhelp-keys">' + HELP_CORNER.map(function(c){ return li(c[0], T(c[1])); }).join('') + '</ul>')
             + sec('Timeline', T('<p>Click a mark: go there. Click again: fold.<br>Marker = where you read. \ud83d\udd12 = do the exercise before.</p>'))
             + sec('Anywhere', '<ul class="nbhelp-keys">' + grp('enter') + '</ul>')
             + sec('Corners and windows', '<ul class="nbhelp-keys">' + grp('corner') + '</ul>')
             + sec('Keyboard mode (Alt+.)', '<ul class="nbhelp-keys">' + grp('move') + grp('do') + grp('view') + '</ul>')
             + '</div>'
             + '<div class="nbhelp-f">' + T('Esc, ? or \u00d7 closes') + '</div>';
      }
      function helpOpen(){ var w = byCls(document, 'nbhelp'); return !!(w && w.classList.contains('on')); }   // E22.1b
      // 2026-09-29 (E6.5, Struktur + Applikation) — ONE WINDOW AT A TIME, AT
      // THE LEFT EDGE, VERTICALLY IN THE MIDDLE. Every widget window (this
      // one and the drawer of ⚙ 👤 📚) opens right beside the corner signs,
      // its middle on the middle of the notebook panel. Opening one closes
      // the other. Only WHERE is set here; the stylesheet's centring
      // transform (-50 %, -50 %) stays, so left/top name the window's middle.
      function helpPlace(){
        var w = document.querySelector('.nbhelp');
        if (!w) return;
        // E11.7 (replaces E9.10): beside the corner signs, its middle on
        // the middle of the corner column, like the drawer (11-layout); the
        // window is centred on its left/top by the stylesheet's translate.
        // One size: the panel's factor is pinned to 1 on the window.
        w.style.setProperty('--nbk', '1');
        var ww = w.offsetWidth || 620, wh = w.offsetHeight || 400;
        var hs = document.getElementById(HOST_ID);
        var bl = hs && hs.querySelector('.nbcorner-bl');
        var tl = hs && hs.querySelector('.nbcorner-tl');
        var br = bl ? bl.getBoundingClientRect() : null, tr = tl ? tl.getBoundingClientRect() : null;
        var ax = br && br.width ? br.right + 12 + ww / 2 : window.innerWidth / 2;
        var ay = (br && tr && br.height && tr.height) ? (tr.top + br.bottom) / 2 : window.innerHeight / 2;
        var L = Math.round(Math.max(ww / 2 + 8, Math.min(ax, window.innerWidth - ww / 2 - 8))) + 'px';
        var T = Math.round(Math.max(wh / 2 + 8, Math.min(ay, window.innerHeight - wh / 2 - 8))) + 'px';
        if (w.style.left !== L) w.style.left = L;
        if (w.style.top !== T) w.style.top = T;
      }
      window.__nbHelpPlace = helpPlace;
      function helpWin(force){
        var want = force === undefined ? !helpOpen() : !!force;
        if (want) {                                  // E6.5: the drawer shuts first
          var hd = document.getElementById(HOST_ID);
          if (hd && hd.classList.contains('open')) {
            hd.classList.remove('open');
            try { placeDock(hd, activeSrc()); } catch (e) {}
          }
        }
        var root = document.fullscreenElement || document.body;
        var back = document.querySelector('.nbhelp-back'), w = document.querySelector('.nbhelp');
        if (!want) {
          if (w) w.classList.remove('on');
          if (back) back.classList.remove('on');
          var pv = window.__nbHelpPrev; window.__nbHelpPrev = null;
          if (pv && pv.isConnected) { try { pv.focus({preventScroll: true}); } catch (e) {} }
          return false;
        }
        if (!back) { back = document.createElement('div'); back.className = 'nbhelp-back'; }
        if (!w) {
          w = document.createElement('div'); w.className = 'nbhelp';
          w.setAttribute('role', 'dialog'); w.setAttribute('aria-modal', 'true');
          w.setAttribute('aria-labelledby', 'nbhelp-t'); w.tabIndex = -1;
        }
        if (back.parentNode !== root) root.appendChild(back);
        if (w.parentNode !== root) root.appendChild(w);
        w.innerHTML = helpHtml();                   // fresh each time: title, keys
        helpPlace();                                // E6.5: beside the corners, middle
        var ae = document.activeElement;
        if (ae && ae !== document.body && !w.contains(ae)) window.__nbHelpPrev = ae;
        // two frames: the transition needs the element laid out without `.on`
        requestAnimationFrame(function(){ requestAnimationFrame(function(){
          back.classList.add('on'); w.classList.add('on');
          var x = w.querySelector('.nbhelp-x'); if (x) x.focus({preventScroll: true});
        }); });
        return true;
      }
      window.__nbHelp = helpWin;
      // 2026-09-30 (E11.7, Applikation) — EVERY TOOL WINDOW SHUTS THE SAME
      // WAY: ×, Esc, or a click outside. The drawer (⚙ 👤 📚) shut on Esc only
      // while the focus was in it or on its sign, had no ×, and a click
      // outside left it open (measured v1.39). The Controls window already
      // shut by ×, Esc and its backdrop. A click on a corner sign is left
      // to the sign (it toggles or switches the page itself).
      function drawerShut(){
        var h = document.getElementById(HOST_ID);
        if (!h || !h.classList.contains('open')) return false;
        h.classList.remove('open');
        try { placeDock(h, activeSrc()); } catch (e) {}
        return true;
      }
      window.__nbDrawerShut = drawerShut;
      if (window.__nbDrawerOff) { try { window.__nbDrawerOff(); } catch (e) {} }
      function drawerDown(ev){
        var h = document.getElementById(HOST_ID);
        if (!h || !h.classList.contains('open') || ev.button) return;
        var t = ev.target;
        if (!t || !t.closest) return;
        if (t.closest('.nbdrawer-x')) { ev.preventDefault(); drawerShut(); return; }
        if (t.closest('.nbdrawer') || t.closest('.nbcorner') || t.closest('.jp-Dialog')
            || t.closest('.nbhelp') || t.closest('.lm-Menu')) return;
        drawerShut();
      }
      function drawerKey(ev){
        if (ev.key !== 'Escape' || helpOpen()) return;
        if (drawerShut()) { ev.preventDefault(); ev.stopPropagation(); }
      }
      document.addEventListener('pointerdown', drawerDown, true);
      document.addEventListener('keydown', drawerKey, true);
      window.__nbDrawerOff = function(){
        document.removeEventListener('pointerdown', drawerDown, true);
        document.removeEventListener('keydown', drawerKey, true);
      };
      if (window.__nbHelpOff) { try { window.__nbHelpOff(); } catch (e) {} }
      function helpClick(ev){
        var t = ev.target;
        if (!t || !t.closest) return;
        if (t.closest('.nbhelp-x') || t.classList.contains('nbhelp-back')) {
          ev.preventDefault(); helpWin(false);
          // 2026-09-30 (E11.7, Applikation) — A CORNER SIGN UNDER THE
          // BACKDROP STILL ANSWERS. With the Controls window open, a click
          // on 📚 ⚙ 👤 hit the backdrop, shut the window and opened nothing
          // (measured v1.39: 3 of 3 switches from ⌨ failed — "📚 does not
          // always open"). The sign under the pointer is pressed after.
          if (t.classList.contains('nbhelp-back') && document.elementsFromPoint) {
            var under = document.elementsFromPoint(ev.clientX, ev.clientY).filter(function(e){
              return e.closest && e.closest('#' + HOST_ID + ' .nbcorner') && e.closest('.nbbtn'); })[0];
            var bt = under && under.closest('.nbbtn');
            if (bt && !bt.classList.contains('nbkeys')) setTimeout(function(){ bt.click(); }, 0);
          }
        }
      }
      function helpKey(ev){
        if (!helpOpen()) return;
        if (ev.key === 'Escape' || (ev.key === '?' && !(ev.target && /^(INPUT|TEXTAREA)$/.test(ev.target.tagName)))) {
          ev.preventDefault(); ev.stopPropagation(); helpWin(false); return;
        }
        // the focus stays in the window while it is open (Tab cycles)
        if (ev.key === 'Tab') {
          var w = document.querySelector('.nbhelp');
          var fs = [].filter.call(w.querySelectorAll('button, [href], [tabindex]:not([tabindex="-1"])'),
                                  function(e){ return e.offsetParent !== null; });
          if (!fs.length) return;
          var i = fs.indexOf(document.activeElement);
          var j = ev.shiftKey ? (i <= 0 ? fs.length - 1 : i - 1) : (i >= fs.length - 1 ? 0 : i + 1);
          ev.preventDefault(); fs[j].focus();
        }
      }
      document.addEventListener('click', helpClick, true);
      window.addEventListener('keydown', helpKey, true);     // before Lumino's own Esc
      window.__nbHelpOff = function(){
        document.removeEventListener('click', helpClick, true);
        window.removeEventListener('keydown', helpKey, true);
      };
      // ---- R3 · 19 — H: the hint of the exercise the keyboard is on --------
      function hintBtnAfter(node){
        var sp = anchorOf(node);
        if (!sp) return null;
        var scope = sp.closest('.jp-OutputArea') || sp.closest('.jp-Notebook') || document;
        var bs = scope.querySelectorAll('.nbhint-btn');
        for (var i = 0; i < bs.length; i++) {
          if (!(sp.compareDocumentPosition(bs[i]) & Node.DOCUMENT_POSITION_FOLLOWING)) continue;
          var b = bs[i].tagName === 'BUTTON' ? bs[i] : bs[i].querySelector('button') || bs[i];
          return b;
        }
        return null;
      }
      function hintIt(){
        var node = kbdNode();
        if (!isTask(node) || node.querySelector('.cd-lock, .st-lock')) return;
        var push = function(){
          var b = hintBtnAfter(node);
          if (!b) return false;
          var r = b.getBoundingClientRect();
          if (!r.width || !r.height || b.disabled) return false;
          b.click();
          return true;
        };
        if (push()) return;
        goIn();                                      // the fold opens first
        [500, 1100, 1900].forEach(function(ms){
          setTimeout(function(){ if (!node.__nbHinted) node.__nbHinted = push(); }, ms);
        });
        setTimeout(function(){ node.__nbHinted = false; }, 2000);
      }
      var KBD_ACT = {
        next: function(){ hop(1); },  prev: function(){ hop(-1); },
        open: hopOpen,                go: goIn,
        send: sendIt,                 leave: kbdLeave,
        theme: function(){ press('.nbbtn.nbtheme'); },
        skin:  function(){ press('.nbbtn.nbskin'); },
        panel: panelToggle,
        full:  function(){ press('.nbbtn.nbfull'); },
        help:  function(){ helpWin(); },            // R3 · 19: the window, not the drawer
        hint:  hintIt
      };
      var KBD_MAP = {};
      KEYS.forEach(function(r){ if (r.key && r.a && r.key !== '#') KBD_MAP[r.key] = r.a; });
      window.__nbKbdMap = KBD_MAP;
      function isEntry(ev){
        return ev.code === 'Period' && ev.altKey && !ev.ctrlKey && !ev.metaKey && !ev.shiftKey;
      }
      function editable(el){
        if (!el || !el.tagName) return false;
        var t = el.tagName.toLowerCase();
        return t === 'input' || t === 'textarea' || t === 'select' || el.isContentEditable;
      }
      function onKbd(ev){
        if (ev.defaultPrevented) return;
        if (isEntry(ev)) {
          var h0 = kbdHost();
          if (!h0) return;                       // no panel on screen: not ours
          ev.preventDefault(); ev.stopPropagation();
          if (kbdOn(h0)) kbdLeave(); else kbdEnter();
          return;
        }
        var h = kbdHost();
        if (!h || !kbdOn(h)) return;
        var ae = document.activeElement;
        // typing in the panel's own fields (the progress code, the role) is
        // typing; only Esc still leaves
        if (editable(ae)) {
          if (ev.key === 'Escape') { ev.preventDefault(); ev.stopPropagation(); kbdLeave(); }
          return;
        }
        if (ev.ctrlKey || ev.metaKey || ev.altKey) return;   // JupyterLab's globals pass
        var k = ev.key || '';
        // a focused button or mark keeps what Enter and Space do to it
        var tag = ae && ae.tagName ? ae.tagName.toLowerCase() : '';
        if ((tag === 'button' || tag === 'a') && ae !== h && (k === 'Enter' || k === ' ')) return;
        var act = null;
        if (/^[1-9]$/.test(k)) { ev.preventDefault(); ev.stopPropagation(); chapN(+k); return; }
        act = KBD_MAP[k] || KBD_MAP[k.toLowerCase()];
        if (act && KBD_ACT[act]) {
          ev.preventDefault(); ev.stopPropagation();
          KBD_ACT[act]();
          return;
        }
        // Everything else that would TYPE something is swallowed as well:
        // the mode is a closed room. (Firefox opens its quick find on '/' and
        // "'" when nothing editable has the focus.) Tab and F-keys pass; ↑ ↓ are J K (27e), ← → pass.
        if (k.length === 1) { ev.preventDefault(); ev.stopPropagation(); }
      }
      // ---- the two cells are kept (D) -----------------------------------------
      // MEASURED by the key fuzz (tests/test_fuzz_keys.py): in JupyterLab's
      // command mode these keys change the notebook's CELLS — insert one above
      // or below, run-and-insert — and a DigiChemJN
      // notebook is two cells by construction (`deletable: false` stops delete
      // and cut, but nothing stops insert). They are held back in
      // OUR notebooks only; every other notebook in the window keeps them.
      // One table, found by the fuzz, not guessed. Keys are written as
      // [Ctrl+][Alt+][Shift+][Meta+]key, key as ev.key in lower case.
      var CELL_KEEP = {
        'a': 'insert a cell above',            'b': 'insert a cell below',
        'shift+a': 'insert a cell above',      'shift+b': 'insert a cell below',
        'shift+enter': 'run, and insert a cell after the last',
        'alt+enter': 'run and insert a cell below'
        // Ctrl+Backspace (merge above) was on this list for an hour: the first
        // fuzz blamed it for a change that the Ctrl+Enter pressed just before
        // it had made, a run still under way. Measured on its own it does
        // nothing to our cells — so it is not held back. Only what is measured.
      };
      // Off the Mac, JupyterLab reads these keys with the Meta (Windows) key
      // held exactly as without it — measured: Meta+A and Shift+Meta+Enter
      // inserted a cell. So there Meta is dropped before the lookup; on the Mac
      // it is Cmd, JupyterLab's Accel, and means something else.
      var KEEP_MAC = /Mac|iPhone|iPad/.test(navigator.platform || '');
      window.__nbCellKeep = CELL_KEEP;
      function keyName(ev){
        var k = (ev.key || '').toLowerCase();
        return (ev.ctrlKey ? 'ctrl+' : '') + (ev.altKey ? 'alt+' : '') +
               (ev.shiftKey ? 'shift+' : '') + (ev.metaKey ? 'meta+' : '') + k;
      }
      function ourNotebook(el){
        var nb = el && el.closest ? el.closest('.jp-Notebook') : null;
        var panel = nb && nb.closest('.jp-NotebookPanel');
        // ours = it carries our feed, i.e. it has run; a cold notebook has no
        // script of ours to hold anything back with anyway
        return (panel && panel.querySelector('.nbfeed')) ? nb : null;
      }
      function onCellKeep(ev){
        if (ev.defaultPrevented) return;
        var nb = ourNotebook(ev.target);
        if (!nb) return;
        var name = keyName(ev);
        if (!KEEP_MAC) name = name.replace('meta+', '');
        if (!CELL_KEEP[name]) return;
        var editing = nb.classList.contains('jp-mod-editMode');
        // in edit mode only the two RUN keys matter; typing 'a' is typing
        if (editing && name !== 'shift+enter' && name !== 'alt+enter') return;
        if (!editing && editable(ev.target)) return;      // our own answer fields
        ev.preventDefault(); ev.stopPropagation();
        if (window.console) console.log('[DigiChemJN] held back: ' + name + ' (' +
            CELL_KEEP[name] + ') — this notebook keeps its two cells');
      }
      if (!window.__nbKeepV || vkey(window.__nbKeepV) <= vkey(NBRAIL_VERSION)) {
        if (window.__nbKeepHandler) window.removeEventListener('keydown', window.__nbKeepHandler, true);
        window.__nbKeepHandler = onCellKeep;
        window.__nbKeepV = NBRAIL_VERSION;
        window.addEventListener('keydown', onCellKeep, true);
      }
      // 2026-09-30 (E10.6, Applikation) — K STOPS AT THE TITLE, NOT ABOVE IT.
      // In command mode JupyterLab's K (select the cell above) on the
      // document cell makes the hidden title cell active and scrolls it into
      // view: scrollTop 0, i.e. up through the air over the title (E9.2),
      // measured in v1.35 from 201 and from 1500. The key stays JupyterLab's
      // — nothing is prevented, the active cell changes as before; only the
      // scroll it causes is held at `__nbTopAt` (the title on the reading
      // line). If the page already stood higher, it stays there. The hold
      // lives 1.5 s after the key, in our notebook only; the wheel, the
      // scroll bar and our own landings are not touched. One list of keys.
      // 2026-09-30 (E10.M-up, Applikation, Nutzer) — ↑ IS THE SAME KEY. In
      // command mode JupyterLab binds ↑ and K to the same command (select the
      // cell above), so ↑ jumped through the head air to 0 exactly like K
      // did; it is held the same way. Still nothing is prevented.
      var KHOLD = {k: 1, ArrowUp: 1};
      function onKHold(ev){
        if (ev.ctrlKey || ev.altKey || ev.metaKey || ev.shiftKey) return;
        if (!KHOLD[ev.key]) return;
        var nb = ourNotebook(ev.target);
        if (!nb || nb.classList.contains('jp-mod-editMode') || editable(ev.target)) return;
        var sc = nb.querySelector('.jp-WindowedPanel-outer') || nb;
        var top = Math.max(0, Math.round(window.__nbTopAt || 0));
        if (!top) return;
        var st = sc.scrollTop;
        window.__nbKHold = {sc: sc, floor: st >= top - 1 ? top : st, until: Date.now() + 1500};
      }
      function onKHoldScroll(ev){
        var g = window.__nbKHold;
        if (!g || ev.target !== g.sc) return;
        if (Date.now() > g.until || !g.sc.isConnected) { window.__nbKHold = null; return; }
        if (g.sc.scrollTop < g.floor - 1) g.sc.scrollTop = g.floor;
      }
      if (!window.__nbKHoldV || vkey(window.__nbKHoldV) <= vkey(NBRAIL_VERSION)) {
        if (window.__nbKHoldHandler) {
          window.removeEventListener('keydown', window.__nbKHoldHandler[0], true);
          window.removeEventListener('scroll', window.__nbKHoldHandler[1], true);
        }
        window.__nbKHoldHandler = [onKHold, onKHoldScroll];
        window.__nbKHoldV = NBRAIL_VERSION;
        window.addEventListener('keydown', onKHold, true);
        window.addEventListener('scroll', onKHoldScroll, true);
      }
      // A newer build replaces an older handler; an older one never replaces a
      // newer. Compared with vkey(), like the rest of the version handshake.
      if (!window.__nbKbdV || vkey(window.__nbKbdV) <= vkey(NBRAIL_VERSION)) {
        if (window.__nbKbdHandler) window.removeEventListener('keydown', window.__nbKbdHandler, true);
        window.__nbKbdHandler = onKbd;
        window.__nbKbdV = NBRAIL_VERSION;
        // window, capture: before JupyterLab's own listener on the document
        window.addEventListener('keydown', onKbd, true);
      }
      // the host shows the mode as a class, for the key caps and the ring
      if (!window.__nbKbdFocusArmed) {
        window.__nbKbdFocusArmed = true;
        var kbdSync = function(){
          var h = document.getElementById('nbpanel-root');
          if (h) h.classList.toggle('nbkbd', h.contains(document.activeElement));
        };
        document.addEventListener('focusin', kbdSync, true);
        document.addEventListener('focusout', function(){ setTimeout(kbdSync, 0); }, true);
        // a click on the panel moves the focus there: tabindex before the focus
        document.addEventListener('pointerdown', function(ev){
          var h = document.getElementById('nbpanel-root');
          if (h && ev.target && h.contains(ev.target) && !h.hasAttribute('tabindex'))
            h.setAttribute('tabindex', '-1');
        }, true);
      }
