      // A double-click on the title turns the markdown cell back into raw HTML and
      // it stays that way until someone runs it again. The cell metadata says
      // editable:false, but not every front end honours that for the render
      // toggle, so this puts it back. Only OUR title is touched, and at most once
      // every few seconds, so a reader editing their own markdown is left alone.
      // 2026-09-24bg — THE TITLE PAGE IS NOT AN EDITOR.
      // MEASURED from the reader's recording: one click into the title cell
      // left six hundred characters of raw HTML standing where the title page
      // had been, and it stayed there. `editable: false` in the cell's metadata
      // stops TYPING and nothing else — un-rendering a markdown cell is not an
      // edit, so JupyterLab allows it.
      // The repair below (render-all-markdown) was the only defence and it is a
      // repair: it needs the application object, it runs on the next sweep, and
      // in that recording it never arrived. So the gestures are refused first.
      // There are exactly two of them — double-click on the cell, and Enter on
      // it in command mode — and both are caught in the capture phase, before
      // the front end's own handlers see them. Everything else about the cell
      // is untouched: it can still be selected, copied and scrolled past.
      function nbTitleCell(el){
        var c = el && el.closest ? el.closest('.jp-MarkdownCell') : null;
        if (!c) return null;
        return (c.textContent || '').indexOf('nbtitle') > -1 ? c : null;
      }
      // 2026-09-27a — …BUT ENTER IN THE COMMAND PALETTE IS NOT ENTER ON THE TITLE.
      // Measured (night 26.09., Complex/Sets/Start, RTC on and off): a TRUSTED
      // notebook opened cold runs its saved outputs, this guard among them, and
      // leaves the title cell active. Ctrl+Shift+C → "Run All Cells" → Enter was
      // then swallowed here — the palette stayed open, nothing ran. The key only
      // counts when it comes from inside a notebook (the palette's input is
      // not), and never while the palette is on screen. Versioned like the
      // other handlers, so a newer build replaces an older guard it installed;
      // a guard from a build before 27a has no handle and stays (it only ever
      // lives in a page that ran such an old notebook).
      function onTitleDbl(ev){
        if (!nbTitleCell(ev.target)) return;
        ev.preventDefault();
        ev.stopPropagation();
      }
      function onTitleEnter(ev){
        if (ev.key !== 'Enter' || ev.ctrlKey || ev.shiftKey || ev.altKey ||
            ev.metaKey) return;
        var tg = ev.target;
        if (!tg || !tg.closest || !tg.closest('.jp-Notebook')) return;
        var pal = document.querySelector('.jp-ModalCommandPalette');
        if (pal && !pal.classList.contains('lm-mod-hidden') && pal.offsetParent !== null) return;
        // only in COMMAND mode: in edit mode Enter is a newline, and in any
        // other cell it is none of our business
        var nb = tg.closest('.jp-Notebook.jp-mod-commandMode');
        if (!nb) return;
        var act = nb.querySelector('.jp-Cell.jp-mod-active');
        if (!act || !act.classList.contains('jp-MarkdownCell')) return;
        if ((act.textContent || '').indexOf('nbtitle') < 0) return;
        ev.preventDefault();
        ev.stopPropagation();
      }
      if (!window.__nbTitleGuardV || vkey(window.__nbTitleGuardV) <= vkey(NBRAIL_VERSION)) {
        if (window.__nbTitleGuardH) {
          document.removeEventListener('dblclick', window.__nbTitleGuardH[0], true);
          document.removeEventListener('keydown', window.__nbTitleGuardH[1], true);
        }
        window.__nbTitleGuard = true;
        window.__nbTitleGuardV = NBRAIL_VERSION;
        window.__nbTitleGuardH = [onTitleDbl, onTitleEnter];
        document.addEventListener('dblclick', onTitleDbl, true);
        document.addEventListener('keydown', onTitleEnter, true);
      }

      // 2026-09-24bh — ...AND ONCE IT HAS RUN, IT IS NOT A CELL ANY MORE.
      // The reader asked for the heading to be simply part of the big document
      // cell after Play. The markdown cell is what the COLD page needs — it is
      // the only thing a notebook with no outputs can show — so it stays, and
      // is taken out of the flow the moment the document below it exists. The
      // class goes on the cell; the stylesheet hides it inside a notebook that
      // carries a live feed, so a second notebook open beside it is untouched.
      function markTitleCell(src){
        var nb = src && src.closest ? (src.closest('.jp-NotebookPanel')
                                    || src.closest('.jp-Notebook')) : null;
        if (!nb) return;
        var cells = allCls(nb, 'jp-MarkdownCell');               // E22.1b
        for (var i = 0; i < cells.length; i++) {
          if ((cells[i].textContent || '').indexOf('nbtitle') > -1 ||
              cells[i].querySelector('.nbtitle')) {
            if (!cells[i].classList.contains('nbtitle-cell'))
              cells[i].classList.add('nbtitle-cell');
          }
        }
      }

      function keepTitleRendered(src){
        var nb = src.closest('.jp-NotebookPanel') || src.closest('.jp-Notebook');
        if (!nb) return;
        var raw = allCls(nb, 'jp-MarkdownCell').filter(function(c){ return !c.classList.contains('jp-mod-rendered'); });   // E22.1b
        var mine = false;
        for (var i = 0; i < raw.length; i++)
          if ((raw[i].textContent || '').indexOf('nbtitle') > -1) { mine = true; break; }
        if (!mine) { window.__nbrailReRender = 0; return; }
        if (Date.now() - (window.__nbrailReRender || 0) < 700) return;
        window.__nbrailReRender = Date.now();
        var app = window.jupyterapp || window.jupyterlab || null;
        if (app && app.commands && app.commands.execute) {
          try { app.commands.execute('notebook:render-all-markdown'); } catch (e) {}
        }
      }

      // 2026-09-24bg — THE CURSOR FOLLOWS THE MARKER, BY MEASUREMENT.
      // It lives in the RAIL, the marker lives in the scrolling inner, so the
      // two have different coordinate systems and the only honest way to line
      // them up is to read both boxes. Cheap, and it cannot drift: whatever
      // moved the marker — a snap, a drag, a jump, a resize — moved the cursor
      // in the same pass.
      function placeCursor(host){
        var rail = host && railOf(host);
        var cur = host && host.querySelector('.nbmap-cursor');
        var grip = host && host.querySelector('.nbgrip');
        if (!rail) return;
        var rr = rail.getBoundingClientRect();
        // 2026-09-24bi — THE GRIP HANGS ON THE OUTSIDE.
        // Both of these are siblings of the rail now, in a fixed full-window
        // layer, so they are positioned in window coordinates — which is the
        // only way anything can sit OUTSIDE a box that clips its children.
        if (grip) {
          if (!vertOn()) { grip.style.visibility = 'hidden'; }
          else {
            var gw = grip.offsetWidth || 13, gh = grip.offsetHeight || 58;
            // FLUSH, not floating. A 3px gap made it a separate little
            // object parked next to the panel; hard against the edge it reads
            // as the panel's own handle (2026-09-25).
            var gl = Math.round(rr.left - gw);
            var gt = Math.round(rr.top + rr.height / 2 - gh / 2);
            // E9.1: ON THE READING HEIGHT, level with cursor and marker
            var GT = nbL('drag up or down to move the reading height, left or right to widen or narrow the timeline',
                         'nach oben oder unten ziehen: Lesehöhe verschieben; nach links oder rechts: Zeitleiste breiter oder schmaler');
            if (grip.title !== GT) grip.title = GT;
            var mapG = host.querySelector('.nbmap');
            var y0g = parseInt(host.dataset.railY0 || '0', 10) || 0;
            if (mapG && y0g > 0)
              gt = Math.round(Math.max(rr.top, Math.min(rr.bottom - gh,
                     mapG.getBoundingClientRect().top + y0g - gh / 2)));
            if (grip.style.left !== gl + 'px') grip.style.left = gl + 'px';
            if (grip.style.top !== gt + 'px') grip.style.top = gt + 'px';
            if (grip.style.visibility) grip.style.visibility = '';
          }
        }
        if (!cur) return;
        if (!vertOn()) { cur.style.visibility = 'hidden'; return; }
        var mark = host.querySelector('.nbmap-here');
        if (!mark) return;
        var mr = mark.getBoundingClientRect();
        if (!(mr.height > 0) || !(rr.height > 0)) return;
        // 2026-09-25 — THE BAR RIDES WITH THE MARKER, NOT BESIDE IT.
        // 24bi let it follow the TRUE reading position while the marker snapped
        // to the nearest mark, on the argument that the pair would then say
        // "this mark, and this far past it". The reader wants one statement,
        // not two: the bar sticks to the nearest symbol, level with its centre.
        // markCentre() puts the marker's centre exactly on that symbol's
        // centre, so the marker's own centre IS the answer — nothing to
        // compute, and the two can never disagree.
        var cy = mr.top + mr.height / 2;
        // 2026-09-27d — THE CURSOR IS A FIXED POINT. It no longer rides with
        // the marker: on the rail, which scrolls 1:1 with the document, the
        // snapped marker hopped up and down the screen (measured 125 → 317 →
        // 290 → 532 → 846 px over one scroll). The bar now stands on ONE
        // screen line — the line the title mark has when the notebook opens
        // (railY0 below the top of the rail's window), the same line a click
        // on a mark lands its pill on (landGap) and the line markCentre()
        // reads the position from. The marks travel past it; the marker
        // steps onto whichever is nearest.
        var map1 = host.querySelector('.nbmap');
        var y0c = parseInt(host.dataset.railY0 || '0', 10) || 0;
        if (map1 && y0c > 0) cy = map1.getBoundingClientRect().top + y0c;
        // 2026-09-25d — THE BAR HANGS ON THE PANEL'S EDGE, NOT ON THE LANE.
        // It sat a fixed 34px to the left of the lane, and the lane is the
        // panel's middle — so the gap between the timeline and the bar was 34px
        // at every width, and no amount of widening ever opened a column for
        // the names. Pinned to the left edge instead, widening pushes the bar
        // outwards and the space between it and the lane IS the name column.
        // One rule produces both halves of what was asked for: pull the panel
        // in and the column closes by itself.
        var cw = cur.offsetWidth || 30;
        var axis = parseFloat(getComputedStyle(document.documentElement)
                     .getPropertyValue('--nbvert-axis')) || 30;
        // E6.7 — plus the air the name column was measured with (14-grip)
        var cx = Math.round(rr.left + 6 + (window.__nbCurAir || 0));
        // ...but it never crosses the lane or the marks on it. In a panel too
        // narrow to hold both, the marks win and the bar steps aside.
        var keep = Math.round(rr.left + axis - 24 - cw);
        if (cx > keep) cx = keep;
        var tooNarrow = (axis - 24 - cw) < 4;
        // 2026-09-29e (E7.5, Struktur) — SHUT, THE THUMB STEPS OUTSIDE. In a
        // panel too narrow for it the cursor used to vanish; now it hangs a
        // few pixels left of the panel's edge, still level with the reading
        // line and still a handle to pull.
        if (tooNarrow) cx = Math.round(rr.left - cw - 6);
        // 2026-09-30 (E9.1, Struktur) — AT THE PANEL'S RIGHT EDGE, INSIDE,
        // shut or open, like a scroll bar (applyGui reserves the room)
        // 2026-09-30 (E11.6, Struktur) — NOW OUTSIDE: in the scroll bar's own
        // column right of the panel (vertPlace leaves SBW px for it), in the
        // middle of it; the track `.nbsb` runs the rail's height there. The
        // panel's own track (`.nbrail::after`) is switched off by
        // `#nbpanel-root.nbsb-out` (04-timeline). Zooming moves neither.
        // 2026-10-01 (E12.3, Struktur + Applikation) — A PLAIN SCROLL BAR,
        // ON THE LEFT, BETWEEN THE TOOLS (user, E12.3 — replaces E9.1's
        // "cursor on the reading height" and E11.6's "right of the panel").
        // The track `.nbsb` runs in the tool column from under the top-left
        // corner (⛶ ◐ ○) to above the bottom-left one (⌨ ⚙ 👤 📚); the thumb
        // (`.nbmap-cursor`) is at its top with "Title" on the reading height
        // (scrollTop __nbTopAt) and at its bottom with "Your own cell" on it
        // (the end of the range), in proportion between. The reading height
        // is the grip, the marker and `.nbreadfix` alone.
        tooNarrow = false;
        host.classList.add('nbsb-out');
        var sb = host.querySelector(':scope > .nbsb');
        if (!sb) {
          sb = document.createElement('div');
          sb.className = 'nbsb'; sb.setAttribute('aria-hidden', 'true');
          host.insertBefore(sb, cur);
        }
        var cTL = host.querySelector('.nbcorner-tl'), cBL = host.querySelector('.nbcorner-bl');
        var scB = scroller(host), sbw = 10, tTop = 0, tH = 0, sbl = 0;
        if (cTL && cBL && scB) {
          var qa = cTL.getBoundingClientRect(), qb = cBL.getBoundingClientRect();
          var bt = cTL.querySelector('.nbbtn'), btr = bt ? bt.getBoundingClientRect() : qa;
          var colX = btr.left + btr.width / 2;
          sbl = Math.round(colX - sbw / 2);
          tTop = Math.round(qa.bottom + 12); tH = Math.max(0, Math.round(qb.top - 12) - tTop);
          cx = Math.round(colX - cw / 2);
        }
        // 2026-10-06 (E23.18, Struktur) — THE THUMB IS THE SHARE OF THE
        // DOCUMENT IN VIEW. Its length = track × (visible height of the
        // document ÷ the document from the title card to the end of the YOC
        // strip), read from the page in this pass: lens out → long, lens in →
        // short; accordions shut → longer, open → shorter. The track is the
        // tool column (corners), so the panel's width changes neither. Never
        // under 24 px (a thumb the mouse can still take; CSS min-height as
        // well), never over the track. Written as `--nbsb-th` on the thumb
        // (04-timeline reads it); the drag (__nbSbTrav) runs with this length.
        var chH = cur.offsetHeight || 48, SBMIN = 24, sbOn = tH > SBMIN + 8;
        if (scB && tH > 0) {
          var tnS = host.querySelector('.nbmap-node.title'), cardS = tnS ? targetEl(tnS) : null;
          var footS = byCls(scB, 'jp-Notebook-footer') || byCls(scB, 'jp-WindowedPanel-footer');
          var crS = cardS && cardS.getBoundingClientRect(), frS = footS && footS.getBoundingClientRect();
          var docH = (crS && frS && crS.height > 0 && frS.height > 0) ? frS.bottom - crS.top : 0;
          var viewH = scB.clientHeight;
          if (docH > 0 && viewH > 0) {
            var thS = Math.max(SBMIN, Math.min(tH, Math.round(tH * Math.min(1, viewH / docH))));
            var thV = thS + 'px';
            if (cur.style.getPropertyValue('--nbsb-th') !== thV) cur.style.setProperty('--nbsb-th', thV);
            chH = thS;
            host.__nbSbShare = viewH / docH;
          }
        }
        sb.style.cssText = 'position:fixed;pointer-events:none;box-sizing:border-box;'
          + 'left:' + sbl + 'px;top:' + tTop + 'px;width:' + sbw + 'px;'
          + 'height:' + tH + 'px;border-radius:5px;' + (sbOn ? '' : 'visibility:hidden;')
          + 'background:color-mix(in srgb,var(--nbskin-line,#c3ced8) 45%%,transparent);'
          + 'box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--nbskin-line,#c3ced8) 60%%,transparent);';
        var sMin = Math.max(0, window.__nbTopAt || 0);
        var sSpan = scB ? Math.max(1, scB.scrollHeight - scB.clientHeight - sMin) : 1;
        var sFr = scB ? Math.max(0, Math.min(1, (scB.scrollTop - sMin) / sSpan)) : 0;
        host.__nbSbTrav = Math.max(1, tH - chH);
        var ct = Math.round(tTop + sFr * (tH - chH));
        var vis = sbOn;
        cur.classList.toggle('nbcur-out', tooNarrow);
        if (cur.style.left !== cx + 'px') cur.style.left = cx + 'px';
        if (cur.style.top !== ct + 'px') cur.style.top = ct + 'px';
        var want = vis ? '' : 'hidden';
        if (cur.style.visibility !== want) cur.style.visibility = want;
        // E9.1 — THE FIXED POINT IN THE DOCUMENT (CSS contract `.nbreadfix`:
        // fixed, height 0, JS sets top/left/width): the reading height drawn
        // across the document, from the scroller's left edge to the panel
        var fix = host.querySelector(':scope > .nbreadfix');
        if (!fix) {
          fix = document.createElement('div');
          fix.className = 'nbreadfix';
          fix.setAttribute('aria-hidden', 'true');
          fix.style.cssText = 'position:fixed;height:0;pointer-events:none;';
          host.appendChild(fix);
        }
        var scF = scroller(host), sr = scF ? scF.getBoundingClientRect() : null;
        if (sr && sr.width > 0) {
          var fl = Math.round(sr.left), fw = Math.max(0, Math.round(rr.left - sr.left));
          var ft = Math.round(cy);
          if (fix.style.top !== ft + 'px') fix.style.top = ft + 'px';
          if (fix.style.left !== fl + 'px') fix.style.left = fl + 'px';
          if (fix.style.width !== fw + 'px') fix.style.width = fw + 'px';
        }
        var wantF = (cy > rr.top + 2 && cy < rr.bottom - 2) ? '' : 'hidden';
        if (fix.style.visibility !== wantF) fix.style.visibility = wantF;
      }
      window.__nbPlaceCursor = placeCursor;

      // ======================================================================
      // 2026-09-28 (R3 · Paket 18, Applikation + Struktur) — THE CHOICE BEFORE
      // PLAY: only calculating · only coding · both. Python 18 builds the run
      // for MODE, read once at its start (DIGICHEM_MODE > stored > both); this
      // is the page's half:
      //   1. THE FIELD. `.nbmode` (CSS 18 contract: .nbmode-t, .nbmode-row,
      //      .nbmode-opt[data-mode] with aria-checked, .nbmode-ic/-l/-d) is put
      //      on the cover above Play whenever our script is alive there (after a
      //      run, or a trusted notebook reopened with its outputs). A plain
      //      inline look of its own, which the stylesheet dresses. Before the
      //      very first run no script runs at all, so a cold first open shows no
      //      field — the ⚙ "Content" field (Python 18) is the way there.
      //   2. THE STORE. The choice goes to localStorage under Python's key
      //      `digichemjn.mode.<notebook id>` — JupyterLite's kernel reads it
      //      there directly.
      //   3. THE KERNEL. A server kernel reads ~/.digichemjn/<id>.mode, which
      //      only Python can write: the choice is handed to the ⚙ "Content"
      //      dropdown (its observer calls set_mode) BEFORE Play restarts the
      //      kernel. After a run whose `.nbfeed[data-nbmode]` is not the choice
      //      (the kernel could not be told in time: a cold start), the dropdown
      //      is set and its ▶ pressed once — under the loading view. Guarded:
      //      once per 90 s, so a store that fails cannot loop.
      // E16.11: the fourth, "plain" — text and figures, no exercises (Python
      // builds it; ⚙ "Content" says "Plain — text and figures only")
      var MODE_TXT = {calc: 'Only calculating', code: 'Only coding', both: 'Both — calculate and code',
                      plain: 'Plain — text and figures only'};
      // 2026-10-02 (E21.11, Struktur) — plain first: the cards read from
      // "just read it" to "do everything" (Nutzer: plain ganz links)
      var MODE_OPT = [
        ['plain', '¶', 'Plain', 'text and figures only'],
        ['calc', '✎', 'Pen & paper', 'only the calculating exercises'],
        ['code', '⌨', 'Code', 'only the coding exercises'],
        ['both', '✎⌨', 'Both', 'calculate and code']];
      // 2026-10-02 (E21.6, Applikation) — WHOSE MODE IT IS. Every helper here
      // took "the notebook in front" or the FIRST ⚙ of the window. A cover
      // shown before Play has no feed, so its choice went to the notebook that
      // had run (stored under ITS id, and Play pressed ITS ⚙ dropdown): one
      // notebook changed the other's mode, the cover's card did not take the
      // click (the paint read the other key), and the run built the old mode.
      // Now each helper may be given an element; its notebook panel decides.
      // A cover knows its id by the class `nbid-<id>` on `.nbcover` (Python
      // markup; the sanitizer keeps classes), else from the title it showed
      // when that notebook last ran here (`digichemjn.ids.v1`).
      // E25.f: no JupyterLab around us (PyCharm, VS Code, Colab: one notebook
      // per view) → the page is the notebook; it was null, so a card had no
      // id to be stored under (`mode.__pending` with an empty title) and fell back
      function modePanel(el){
        return (el && el.closest && el.closest('.jp-NotebookPanel')) || visiblePanel()
               || (document.querySelector('.jp-NotebookPanel') ? null : document.body);
      }
      var IDS_KEY = 'digichemjn.ids.v1';
      function modeFeed(el){
        // E22.1: one look per pass for the notebook in front (memo, 10-rail-host)
        var vp0 = modePanel(el);
        if (window.__nbMemo && vp0 && vp0 === visiblePanel()) return memo('feed', function(){ return modeFeed0(el); });
        return modeFeed0(el);
      }
      function modeFeed0(el){
        // E16.1: the notebook in front, not the last feed of the window (two
        // open notebooks read each other's mode and id)
        var vp = modePanel(el), fs = feedsP(vp || document);           // E22.1b
        if (!fs.length && !vp) fs = feedsP(document);
        return fs.length ? fs[fs.length - 1] : null;
      }
      function modeT(el){ var vp = modePanel(el), h = vp && vp.querySelector('.nbtitle-h'); return h ? h.textContent.trim() : ''; }
      function modeNbId(el){
        var vp = modePanel(el), cov = vp && byCls(vp, 'nbcover'), m;
        var id = (vp && modeFeed(el) && nbId(vp)) || '';
        if (id) return id;
        m = cov && /\bnbid-([a-z0-9-]+)/.exec(cov.className || '');
        if (m) return m[1];
        try { var map = JSON.parse(localStorage.getItem(IDS_KEY) || '{}') || {}, t = modeT(el); if (t && map[t]) return map[t]; } catch (e) {}
        return el ? null : (nbId() || null);
      }
      function modeLearn(){
        var vp = visiblePanel(), id = vp && modeFeed() && nbId(vp), t = modeT();
        if (!id || !t) return;
        try { var map = JSON.parse(localStorage.getItem(IDS_KEY) || '{}') || {};
              if (map[t] !== id) { map[t] = id; localStorage.setItem(IDS_KEY, JSON.stringify(map)); } } catch (e) {}
      }
      function modeKey(el){ var id = modeNbId(el); return id ? 'digichemjn.mode.' + id : null; }
      function modeWanted(el){
        var v = null, k = modeKey(el);
        try {
          // E8.16: a choice made before the notebook had an id (the cover
          // after a reload) becomes this notebook's choice as soon as it has
          // one — and is not read again after that
          // E16.10: … but only the notebook whose title the cover showed
          // (the pending choice carries it: "<mode>\n<title>")
          var pend = (localStorage.getItem('digichemjn.mode.__pending') || '').split('\n'),
              mine = MODE_TXT[pend[0]] && pend[1] && pend[1] === modeT(el) ? pend[0] : null;
          if (k && mine) { localStorage.setItem(k, mine); localStorage.removeItem('digichemjn.mode.__pending'); }
          v = (k && localStorage.getItem(k)) || mine;
          // E17.3: no choice for this notebook → the favourite content
          if (!MODE_TXT[v] && window.__nbStore) v = window.__nbStore.get('digichemjn.defmode.v1');   // E25.o: this notebook's
        } catch (e) {}
        return MODE_TXT[v] ? v : null;
      }
      function modeBuilt(el){ var f = modeFeed(el); return f ? f.getAttribute('data-nbmode') || 'both' : null; }
      function modeStore(v, el){
        try {
          var k = modeKey(el);
          if (k) { localStorage.setItem(k, v); localStorage.removeItem('digichemjn.mode.__pending'); }
          else localStorage.setItem('digichemjn.mode.__pending', v + '\n' + modeT(el));
        } catch (e) {}
      }
      // the ⚙ dropdown of Python 18 (inside .nbctl-difficulty): set by LABEL,
      // the only thing of the option the page can read
      // ipywidgets writes the labels with no-break spaces: compare words only
      function modeNorm(t){ return String(t || '').replace(/\s+/g, ' ').trim(); }
      // the drawer BORROWS the front notebook's controls (18): while a notebook
      // is in front its ⚙ lives in our host, not in its panel
      function modeQ(el, sel){
        var P = modePanel(el), h = document.getElementById(HOST_ID), x = null;
        if (P && P === visiblePanel() && h) x = h.querySelector(sel);
        return x || (P || document).querySelector(sel);
      }
      // E17.1 (rebase 03.10.): a German run writes the labels in German
      // (py-E17.1 de.txt) and marks the dropdown `.nbctl-mode`, options in
      // the order of MODES — so a label is read in both languages, and an
      // unknown one by its place in the marked dropdown
      var MODE_TXT_DE = {calc: 'Nur rechnen', code: 'Nur programmieren', both: 'Beides: rechnen und programmieren',
                         plain: 'Nur lesen: Text und Abbildungen'};
      var MODE_ORDER = ['both', 'calc', 'code', 'plain'];
      function modeOf(sel, j){
        var t = modeNorm((sel.options[j] || {}).textContent);
        for (var m in MODE_TXT) if (MODE_TXT[m] === t || MODE_TXT_DE[m] === t) return m;
        return sel.closest && sel.closest('.nbctl-mode') ? MODE_ORDER[j] || null : null;
      }
      function modeDropdown(el){
        var box = modeQ(el, '.nbctl-difficulty');
        if (!box) return null;
        var mk = box.querySelector('.nbctl-mode select');
        if (mk) return mk;
        var sels = box.querySelectorAll('select');
        for (var i = 0; i < sels.length; i++)
          for (var j = 0; j < sels[i].options.length; j++)
            if (modeOf(sels[i], j) === 'code') return sels[i];
        return null;
      }
      // E21.6: py-E21.6's own entrance, if the build has it: "<id>:<mode>"
      // into `.nbctl-modein input` of THIS notebook (the kernel checks the id)
      function modeIn(v, el){
        var inp = modeQ(el, '.nbctl-modein input'), id = modeNbId(el);
        if (!inp || !id || !v) return false;
        var s = id + ':' + v;
        if (inp.value === s) return false;
        inp.value = s;
        modeSelf = true;
        try { inp.dispatchEvent(new Event('input', {bubbles: true}));
              inp.dispatchEvent(new Event('change', {bubbles: true}));
              inp.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', keyCode: 13, bubbles: true})); }
        finally { modeSelf = false; }
        return true;
      }
      function modeToKernel(v, el){
        if (modeIn(v, el)) return true;
        var sel = modeDropdown(el);
        if (!sel || !v) return false;
        for (var j = 0; j < sel.options.length; j++) {
          if (modeOf(sel, j) !== v) continue;
          if (sel.selectedIndex === j) return false;          // already told
          sel.selectedIndex = j;
          modeSelf = true;
          try { sel.dispatchEvent(new Event('change', {bubbles: true})); } finally { modeSelf = false; }
          return true;
        }
        return false;
      }
      // E21.6: a cold kernel cannot be told — the file it reads at its first
      // run can be written now, beside the notebook (py-E21.6 reads
      // `<folder>/.digichemjn/<id>.mode`, the newer of it and ~ wins), through
      // the server's Contents API. JupyterLab only (a server behind the page);
      // the tab of the panel names the notebook's path.
      function modeFile(v, el){
        try {
          var P = modePanel(el), id = modeNbId(el), cfg = document.getElementById('jupyter-config-data');
          if (!P || !id || !v || !cfg || !window.fetch) return null;
          var c = JSON.parse(cfg.textContent || '{}'), base = String(c.baseUrl || '/').replace(/\/?$/, '/');
          if (c.appName && /lite/i.test(c.appName)) return null;
          var tab = document.querySelector('.lm-TabBar-tab[data-id="' + P.id + '"]'), tt = tab ? (tab.title || '') : '';
          var m = /Path:\s*([^\n]+)/.exec(tt); if (!m) return null;
          var dir = m[1].trim().replace(/[^\/]*$/, ''), enc = function(p){ return p.split('/').map(encodeURIComponent).join('/'); };
          var xs = /(?:^|;\s*)_xsrf=([^;]+)/.exec(document.cookie), hd = {'Content-Type': 'application/json'};
          if (xs) hd['X-XSRFToken'] = decodeURIComponent(xs[1]);
          var url = base + 'api/contents/' + enc(dir + '.digichemjn');
          return fetch(url, {method: 'PUT', headers: hd, credentials: 'same-origin', body: JSON.stringify({type: 'directory'})})
            .catch(function(){}).then(function(){
              return fetch(url + '/' + encodeURIComponent(id + '.mode'), {method: 'PUT', headers: hd, credentials: 'same-origin',
                           body: JSON.stringify({type: 'file', format: 'text', content: v})}); })
            .catch(function(){});
        } catch (e) { return null; }
      }
      window.__nbModeToKernel = function(el){
        var v = modeWanted(el), told = modeToKernel(v, el), f = told ? null : modeFile(v, el);
        return told || f;                       // true, a promise (file under way), or nothing
      };
      // 2026-09-29 (E8.16, Applikation) — THE LAST CHOICE WINS, WHEREVER IT
      // WAS MADE. The page kept its own copy of the mode (localStorage, set on
      // the cover) and, after every run, forced the run back to it when the
      // kernel had built another one (modeAfterRun). A reader who then chose
      // in ⚙ "Content" (Python stores it for the kernel) and ran again got
      // the OLD cover choice back: the page's copy was never told. Now a
      // change of that dropdown by the reader is the page's choice too.
      var modeSelf = false;
      function modeFromSelect(ev){
        var sel = ev.target;
        if (modeSelf || !sel || sel.tagName !== 'SELECT' || !sel.closest || !sel.closest('.nbctl-difficulty')) return;
        if (modeDropdown(sel) !== sel) return;
        var m = modeOf(sel, sel.selectedIndex);
        if (MODE_TXT[m]) {
          modeStore(m, sel);                   // E21.6: the notebook of THIS ⚙
          [].forEach.call(document.querySelectorAll('.nbmode'), modePaint);
          coverPaint();                        // E9.11
          return;
        }
      }
      function modePaint(box){
        var w = modeWanted(box) || modeBuilt(box) || 'both';     // E21.6: the cover's own notebook
        [].forEach.call(box.querySelectorAll('.nbmode-opt'), function(o){
          var on = o.getAttribute('data-mode') === w;
          if (o.getAttribute('aria-checked') !== String(on)) o.setAttribute('aria-checked', String(on));
          o.classList.toggle('on', on);
          o.style.borderColor = on ? '#3fa877' : '#c3ced8';
          o.style.boxShadow = on ? '0 0 0 3px rgba(63,168,119,.22)' : 'none';
        });
      }
      // E17.1: the cards in the reader's language
      var MODE_OPT_DE = {calc: ['Stift & Papier', 'nur die Rechenaufgaben'], code: ['Code', 'nur die Programmieraufgaben'],
                         both: ['Beides', 'rechnen und programmieren'], plain: ['Nur lesen', 'nur Text und Abbildungen']};
      function modeField(){
        var covs = allCls(document, 'nbcover'), lg = langOf();     // E22.1b
        [].forEach.call(covs, function(cov){
          var play = cov.querySelector('.nbcover-play');
          if (!play) return;
          var box = cov.querySelector('.nbmode');
          if (box && (box.getAttribute('data-lang') || 'en') !== lg) { box.remove(); box = null; }   // E17.1
          if (!box) {
            box = document.createElement('div');
            box.className = 'nbmode';
            box.setAttribute('data-lang', lg);
            box.setAttribute('role', 'radiogroup');
            box.setAttribute('aria-label', lg === 'de' ? 'was dieses Notebook Ihnen zeigt' : 'what this notebook shows you');
            box.style.cssText = 'max-width:680px;margin:0 auto 20px;text-align:center;';
            box.innerHTML = '<div class="nbmode-t" style="font-size:.78em;font-weight:800;'
              + 'letter-spacing:2px;text-transform:uppercase;color:#8b98a5;margin-bottom:9px">'
              + (lg === 'de' ? 'Was möchten Sie üben?' : 'What do you want to practise?')
              + '</div><div class="nbmode-row" style="display:flex;'
              + 'justify-content:center;gap:10px;flex-wrap:wrap">'
              + MODE_OPT.map(function(m){
                  if (lg === 'de') m = [m[0], m[1]].concat(MODE_OPT_DE[m[0]]);
                  return '<button type="button" class="nbmode-opt" role="radio" data-mode="' + m[0]
                    + '" aria-checked="false" style="display:flex;flex-direction:column;align-items:center;'
                    + 'gap:2px;width:150px;padding:10px 10px 9px;border-radius:12px;cursor:pointer;'
                    + 'background:#fff;color:#55636f;border:1.5px solid #c3ced8;font:inherit">'
                    + '<span class="nbmode-ic" style="font-size:20px;line-height:1.2">' + m[1] + '</span>'
                    + '<span class="nbmode-l" style="font-weight:800;font-size:.9em">' + m[2] + '</span>'
                    + '<span class="nbmode-d" style="font-size:.74em;line-height:1.3">' + m[3] + '</span></button>';
                }).join('') + '</div>';
            play.parentNode.insertBefore(box, play);
          }
          modePaint(box);
          langRow(cov, box);                                            // E17.1
        });
      }
      window.__nbModeField = modeField;
      // 2026-10-02 (E17.1, Applikation) — ENGLISH OR GERMAN, IN THE SAME
      // NOTEBOOK. The choice is the profile's (`digichemjn.lang.v1`, shared,
      // a favourite of the account) and works like the content: on the cover
      // two buttons beside the cards (`.nblang > .nblang-opt[data-lang]`,
      // radio group) — chosen before Play, the kernel learns it before the
      // run; in the 👤 settings it is stored and the notebook rebuilt at once.
      // The texts the KERNEL writes come from Python; the page tells it
      // through the toolkit's own field, the way the content is told: a ⚙
      // dropdown whose options read "English" / "Deutsch" (contract with
      // Python), and reads what was built from `.nbfeed[data-nblang]`
      // (absent = English). Without that field nothing is rebuilt — the
      // page's own words (cover, windows, panel) follow at once anyway.
      function langOf(){ return window.__nbAcct ? window.__nbAcct.lang() : 'en'; }
      function langRow(cov, box){
        // E25.k: the row may live in the title card's slot, beside the cover
        var lg = langOf(), root = cov.closest('.nbtitle') || cov, row = root.querySelector('.nblang');
        if (row && row.getAttribute('data-lang') !== lg) { row.remove(); row = null; }
        if (!row) {
          row = document.createElement('div');
          row.className = 'nblang';
          row.setAttribute('data-lang', lg);
          row.setAttribute('role', 'radiogroup');
          row.setAttribute('aria-label', lg === 'de' ? 'Sprache' : 'language');
          row.style.cssText = 'max-width:680px;margin:0 auto 14px;text-align:center;display:flex;'
            + 'justify-content:center;align-items:center;gap:8px;flex-wrap:wrap';
          row.innerHTML = '<span class="nblang-t" style="font-size:.78em;font-weight:800;letter-spacing:2px;'
            + 'text-transform:uppercase;color:#8b98a5">' + (lg === 'de' ? 'Sprache' : 'Language') + '</span>'
            + [['en', 'English'], ['de', 'Deutsch']].map(function(o){
                var on = o[0] === lg;
                return '<button type="button" class="nblang-opt' + (on ? ' on' : '') + '" role="radio" data-lang="' + o[0]
                  + '" aria-checked="' + on + '" style="padding:5px 14px;border-radius:999px;cursor:pointer;font:inherit;'
                  + 'font-size:.86em;font-weight:700;background:#fff;color:#55636f;border:1.5px solid '
                  + (on ? '#3fa877;box-shadow:0 0 0 3px rgba(63,168,119,.22)' : '#c3ced8') + '">' + o[1] + '</button>';
              }).join('');
          box.parentNode.insertBefore(row, box);
        }
        // E25.k: py-E25.k gives the language its place — small, top right in
        // the title card (`.nbcover-lang-slot`); the row goes there, without
        // the word "Language" (the two buttons say it)
        var slot = root.querySelector('.nbcover-lang-slot');
        if (slot && row.parentNode !== slot) {
          slot.appendChild(row);
          row.style.cssText = 'display:flex;gap:4px;justify-content:flex-end;align-items:center;margin:0';
          var lt = row.querySelector('.nblang-t'); if (lt) lt.style.display = 'none';
          [].forEach.call(row.querySelectorAll('.nblang-opt'), function(b){ b.style.padding = '2px 9px'; b.style.fontSize = '.78em'; });
        }
        try { coverDe(cov); } catch (e) {}                              // py-E17.1 .nbcover-de
        try { coverLang(cov); } catch (e) {}                            // E29 P1
      }
      // 2026-10-12 (E29 P1, JavaScript) — EN | DE CHANGES ALL OF THE PREVIEW.
      // Reader 12.10.: after the switch the title card, the lead, the
      // timeline (names, hover boxes, tooltips), Play, the account, the series
      // and the feedback stood half in the other language. py-E29 puts both
      // languages into the cover (claude/VERTRAG-E29-py.md): texts as
      // `span[data-nbl="en|de"]`, shown by the cover's own stylesheet on the
      // EN|DE row this page writes (`.nblang[data-lang]`) — nothing to do here;
      // attributes as `data-nbl-en` / `data-nbl-de` = JSON {attr: value}
      // (title, data-desc, aria-label, placeholder, alt) — applied here, for
      // the language CHOSEN on the preview (langOf), whatever the run was
      // built in. A title the hover has moved (`data-nm`, 17-rail tlShow) or
      // the bubble holds (`data-nbtip`, 01-jump) is set there; a pinned hover
      // box says its text again. The cover root carries `lang` and
      // `data-nbcov-lang` (for the stylesheet), and coverDe (E17.1) only works
      // where a build still has its map (Complex, Modeling: not caught up).
      function clSet(e, k, v){
        var cur = k;
        if (k === 'title' && !e.hasAttribute('title')) {
          if (e.hasAttribute('data-nm')) cur = 'data-nm'; else if (e.hasAttribute('data-nbtip')) cur = 'data-nbtip';
        }
        if (v == null) { if (e.hasAttribute(cur)) e.removeAttribute(cur); }
        else if (e.getAttribute(cur) !== v) e.setAttribute(cur, v);
      }
      function coverLang(cov){
        var lg = langOf() === 'de' ? 'de' : 'en', root = cov.closest('.nbtitle') || cov;
        if (root.getAttribute('lang') !== lg) root.setAttribute('lang', lg);
        if (root.getAttribute('data-nbcov-lang') !== lg) root.setAttribute('data-nbcov-lang', lg);
        if (cov.__nbLangShown === lg) return;
        [].forEach.call(root.querySelectorAll('[data-nbl-' + lg + ']'), function(e){
          var m = null;
          try { m = JSON.parse(e.getAttribute('data-nbl-' + lg)); } catch (x) { m = null; }
          if (m) Object.keys(m).forEach(function(k){ clSet(e, k, m[k]); });
        });
        cov.__nbLangShown = lg;
        [].forEach.call(root.querySelectorAll('.nbcover-tl'), function(tl){
          var pin = tl.querySelector('.nbtl-row.nbtl-pin');
          if (window.__nbTlShow) window.__nbTlShow(tl, pin || null);
        });
      }
      window.__nbCoverLang = coverLang;
      // 2026-10-08 (E25.k, JavaScript) — THE SERIES ON THE PREVIEW.
      // py-E25.k: `.nbcover-series[data-series]` = {series, name, me, items:
      // [{id, name: [en, de], file, lite}]} and a plain list (`li.nbser-it`,
      // this one `.nbser-me`). Here: the names in the reader's language, each
      // notebook's progress beside it (solved / exercises), a link where the
      // Lite page has an address (else the file's name as a hint), and one
      // line: this notebook · the series · all notebooks. The source is what
      // this browser knows (`progress.v1`, folded in from an account code on
      // a log-in) — the line says so; without a server there is no more.
      function seriesCover(){
        allCls(document, 'nbcover-series').forEach(function(box){
          var d = null; try { d = JSON.parse(box.getAttribute('data-series') || ''); } catch (e) {}
          if (!d || !d.items) return;
          var de = langOf() === 'de', all = {};
          try { all = JSON.parse(localStorage.getItem('digichemjn.progress.v1') || '{}') || {}; } catch (e) {}
          var ab = function(id){ var r = all[id], a = r && r.a; return a && a.length === 2 ? [+a[0] || 0, +a[1] || 0] : null; };
          var sum = function(ids){ var s = [0, 0]; ids.forEach(function(i){ var a = ab(i); if (a) { s[0] += a[0]; s[1] += a[1]; } }); return s; };
          var sig = [de, JSON.stringify(d.items.map(function(it){ return ab(it.id); })), JSON.stringify(sum(Object.keys(all)))].join('|');
          if (box.__nbSerSig === sig) return;
          box.__nbSerSig = sig;
          d.items.forEach(function(it){
            var li = box.querySelector('li.nbser-it[data-nbid="' + it.id + '"]');
            if (!li) return;
            if (!li.__nbEn) li.__nbEn = li.innerHTML;
            var nm = (it.name && it.name[de ? 1 : 0]) || it.id, a = ab(it.id), me = it.id === d.me;
            var tx = document.createElement('span'); tx.className = 'nbser-nm'; tx.textContent = nm;
            var el = tx;
            if (!me && it.lite) { el = document.createElement('a'); el.className = 'nbser-nm'; el.href = it.lite; el.textContent = nm; }
            else if (!me && it.file) li.title = (de ? 'Datei: ' : 'file: ') + it.file + '_v….ipynb';
            li.innerHTML = '';
            li.appendChild(el);
            if (me) { var h = document.createElement('span'); h.className = 'nbser-here'; h.style.cssText = 'opacity:.7;font-weight:400';
                      h.textContent = de ? ' (dieses Notebook)' : ' (this notebook)'; li.appendChild(h); }
            var p = document.createElement('span'); p.className = 'nbser-p'; p.style.cssText = 'margin-left:5px;opacity:.75;font-variant-numeric:tabular-nums';
            p.textContent = a ? a[0] + '/' + a[1] : '\u2013';
            li.appendChild(p);
            // css-E25.k draws a bar from this share (0 … 1)
            li.style.setProperty('--nbser-p', a && a[1] ? String(Math.round(1000 * a[0] / a[1]) / 1000) : '0');
          });
          var me = ab(d.me) || [0, 0], se = sum(d.items.map(function(it){ return it.id; })), tot = sum(Object.keys(all));
          var ln = box.querySelector('.nbser-sum');
          if (!ln) { ln = document.createElement('div'); ln.className = 'nbser-sum'; ln.style.cssText = 'margin-top:6px'; box.appendChild(ln); }
          ln.textContent = (de ? 'Gelöst: dieses Notebook ' : 'Solved: this notebook ') + me[0] + '/' + me[1]
            + (de ? ' · die Reihe ' : ' · the series ') + se[0] + '/' + se[1]
            + (de ? ' · alle Notebooks ' : ' · all notebooks ') + tot[0] + '/' + tot[1]
            + (de ? ' — so weit dieser Browser es kennt' : ' — as far as this browser knows');
        });
      }
      // 2026-10-04 (E17.1, rebase) — THE COLD COVER IN GERMAN. The cover is
      // the markdown cell: English before Play, and the sanitiser strips
      // data-* from it. A German run of py-E17.1 puts what the page needs into
      // its document instead, hidden: `.nbcover-de[data-map]` = {rows:
      // [[name, card], …] in the order of the cover timeline, facts: the
      // title card's facts block, play, hint, tl}. Applied to the cover of
      // the SAME notebook panel while its feed says `data-nblang="de"`; the
      // English is kept on the elements and comes back with an English run.
      // (`tl`: the heading is coverPaint's, counted per content.)
      function coverDe(cov){
        var P = cov.closest('.jp-NotebookPanel') || document;
        // E22.1b: by class, the first one carrying the attribute
        var mk = allCls(P, 'nbcover-de').filter(function(e){ return e.hasAttribute('data-map'); })[0] || null;
        var fd = allCls(P, 'nbfeed').filter(function(e){ return e.hasAttribute('data-nblang'); })[0] || null;
        // E29 P1: the language chosen on the preview, not the one the run was built in
        var want = mk && langOf() === 'de' ? mk.getAttribute('data-map') || '' : '';
        void fd;
        if (cov.__nbDeSig === want) return;
        var m = null;
        try { m = want ? JSON.parse(want) : null; } catch (e) { m = null; }
        cov.__nbDeSig = want;
        var keep = function(el, k, get, set, v){
          if (!el) return;
          if (!el.__nbEn) el.__nbEn = {};
          if (!(k in el.__nbEn)) el.__nbEn[k] = get();
          var nv = v == null ? el.__nbEn[k] : v;
          if (get() !== nv) set(nv);
        };
        [].forEach.call(cov.querySelectorAll('.nbtl-row'), function(r, i){
          var tt = r.title, ti = tt.indexOf('\n');                      // as coverPaint (py-E15.4)
          if (ti > -1) { r.setAttribute('data-desc', tt.slice(ti + 1)); r.title = tt.slice(0, ti); }
          var x = m && m.rows && m.rows[i], nm = r.querySelector('.nbtl-nm');
          keep(nm, 'nm', function(){ return nm.textContent; }, function(v){ nm.textContent = v; }, x ? x[0] : null);
          keep(r, 'title', function(){ return r.title; }, function(v){ r.title = v; }, x ? x[0] : null);
          keep(r, 'desc', function(){ return r.getAttribute('data-desc') || ''; },
               function(v){ if (v) r.setAttribute('data-desc', v); else r.removeAttribute('data-desc'); }, x && x[1] ? x[1] : null);
        });
        // the facts block stands beside the cover in the title cell, not in it
        var fa = (cov.closest('.nbtitle') || cov.parentNode || cov).querySelector('.nbtitle-facts'), nf = null;
        if (m && m.facts) { var tmp = document.createElement('div'); tmp.innerHTML = m.facts; nf = tmp.querySelector('.nbtitle-facts'); }
        keep(fa, 'facts', function(){ return fa.innerHTML; }, function(v){ fa.innerHTML = v; }, nf ? nf.innerHTML : null);
        var pl = cov.querySelector('.nbcover-play-lab'), hi = cov.querySelector('.nbcover-hint');
        keep(pl, 'play', function(){ return pl.textContent; }, function(v){ pl.textContent = v; }, m && m.play ? m.play : null);
        keep(hi, 'hint', function(){ return hi.innerHTML; }, function(v){ hi.innerHTML = v; }, m && m.hint ? m.hint : null);
      }
      window.__nbCoverDe = coverDe;
      function langNorm(t){ return String(t || '').replace(/\s+/g, ' ').trim(); }
      function langDropdown(){
        // the KERNEL's field (a widget), never the page's own 👤 setting
        var sels = document.querySelectorAll('.nbctl-stash select, #' + HOST_ID + ' .nbslot select, .nbctl-lang select');
        for (var i = 0; i < sels.length; i++) {
          if (sels[i].classList.contains('nbpref')) continue;
          var t = [].map.call(sels[i].options, function(o){ return langNorm(o.textContent); });
          if (t.indexOf('Deutsch') > -1 && t.indexOf('English') > -1) return sels[i];
        }
        return null;
      }
      function langToKernel(v){
        var sel = langDropdown();
        if (!sel) return false;
        for (var j = 0; j < sel.options.length; j++) {
          if (langNorm(sel.options[j].textContent) !== (v === 'de' ? 'Deutsch' : 'English')) continue;
          if (sel.selectedIndex === j) return false;
          sel.selectedIndex = j;
          sel.dispatchEvent(new Event('change', {bubbles: true}));
          return true;
        }
        return false;
      }
      function langBuilt(){ var f = modeFeed(); return f ? (f.getAttribute('data-nblang') || 'en') : null; }
      function langRebuild(go0){
        var go = null, box = document.querySelector('.nbctl-difficulty'), LV = window.__nbLoading;
        if (box) [].forEach.call(box.querySelectorAll('.nbrunall, .nbrunall button'), function(x){ go = go || x; });
        if (!go) return false;
        if (LV) { try { LV.show(go0 || go, false); } catch (e) {} }
        setTimeout(function(){ go.click(); }, 700);
        return true;
      }
      // a choice: stored (profile + account), the page's words at once, the kernel told
      window.__nbLangGo = function(v, now){
        v = v === 'de' ? 'de' : 'en';
        if (window.__nbAcct) window.__nbAcct.setFav('lang', v);
        else if (window.__nbStore) window.__nbStore.set('digichemjn.lang.v1', v);                  // E25.o
        var told = langToKernel(v);
        try { modeField(); coverPaint(); } catch (e) {}
        if (window.__nbAcctAll) window.__nbAcctAll();
        var b = langBuilt();
        if (now !== false && b && b !== v && (told || langDropdown())) return langRebuild();
        return told;
      };
      // after a run: built ≠ wanted and the kernel can be told → once, like the content
      // rebase 03.10.: only right after a run of THIS notebook (a new run id
      // on its feed). The language is a profile value: chosen in another
      // notebook, it reaches this one's page words at once (storage, E17.5)
      // but never rebuilds it — that waits for this notebook's next run
      // (E17.5a: the other notebook follows with 0 runs). Measured with
      // py-E17.5: Deutsch in Complex rebuilt the open Modeling as well.
      function langAfterRun(){
        var w = langOf(), b = langBuilt(), f = modeFeed(), run = f ? f.getAttribute('data-nbid') || '' : '';
        if (!b) return;
        var seen = window.__nbLangSeen || (window.__nbLangSeen = {}), nid = modeNbId() || 'nb';
        if (seen[nid] === run) return;
        var vp = visiblePanel();
        var st = ((vp || document).querySelector('.jp-Notebook-ExecutionIndicator') || {getAttribute: function(){ return 'idle'; }})
                 .getAttribute('data-status');
        if (st && st !== 'idle') return;
        seen[nid] = run;
        if (w === b || !langDropdown()) return;
        var rk = 'digichemjn.lang.retry.' + nid, pair = w + '>' + b, last = '';
        try { last = sessionStorage.getItem(rk) || ''; } catch (e) { return; }
        if (last === pair) return;
        try { sessionStorage.setItem(rk, pair); } catch (e) { return; }
        langToKernel(w);
        langRebuild();
      }
      function langClick(ev){
        var o = ev.target && ev.target.closest ? ev.target.closest('.nblang .nblang-opt') : null;
        if (!o) return false;
        ev.preventDefault(); ev.stopPropagation();
        window.__nbLangGo(o.getAttribute('data-lang'), false);     // the cover: Play builds it
        return true;
      }
      // 2026-09-30 (E9.11, Struktur + Applikation) — THE COVER'S TIMELINE
      // FOLLOWS THE MODE AND SHOWS WHERE YOU ARE. Python's flat timeline on
      // the cover (py-E8.21: `.nbtl-row`, `.nbtl-calc` / `.nbtl-code`,
      // `.nbtl-k-<task>`) was the same for every reader. Now:
      //   * the mode chosen (cover or ⚙, else the one built) hides the other
      //     route's columns — calc hides `.nbtl-code`, code hides `.nbtl-calc`
      //     — and the summary line counts what is left;
      //   * every exercise column carries the reader's state as `data-st`
      //     (the pip words: solved · wrong · skipped · open · locked), read
      //     from the panel's marks while the notebook runs and kept in
      //     `digichemjn.cover.v1` (per notebook, with its title), so a cover
      //     shown later still has it. The mark gets a colour inline (no
      //     stylesheet on a cold page); CSS can take over on `data-st`.
      var COVER_KEY = 'digichemjn.cover.v1';
      var COVER_ST = {'st-ans': 'solved', 'st-fail': 'wrong', 'st-skip': 'skipped', 'st-open': 'open', 'st-lock': 'locked',
                      'cd-done': 'solved', 'cd-fail': 'wrong', 'cd-skip': 'skipped', 'cd-open': 'open', 'cd-lock': 'locked'};
      var COVER_COL = {solved: '#3fa877', wrong: '#d05050', skipped: '#d9a520', locked: '#aab4be'};
      var COVER_FREE = '#8a96a3';      // E23.3: unlocked, not the highest — no lane colour
      function coverWord(el){
        if (!el) return null;
        for (var c in COVER_ST) if (el.classList.contains(c)) return COVER_ST[c];
        return null;
      }
      function coverRead(){
        var all = {};
        try { all = JSON.parse(localStorage.getItem(COVER_KEY) || '{}') || {}; } catch (e) { all = {}; }
        var id = modeNbId(), h = document.getElementById(HOST_ID);
        if (id && h) {
          // E17.5: an order number, not a time (concept §4)
          var rec = {t: 0, title: '', k: {}}, f = modeFeed(), n = 0;
          try { rec.title = JSON.parse(f.getAttribute('data-progress')).title || ''; } catch (e) {}
          [].forEach.call(h.querySelectorAll('.nbmap-node.task[data-task], .nbmap-node.codetask[data-task]'), function(a){
            var k = String(a.getAttribute('data-task') || '').toLowerCase().replace(/[^a-z0-9]/g, '');
            var code = a.classList.contains('codetask');
            var mk = a.querySelector(code ? '.nbcodemark' : '.nbrail-dot'), w = coverWord(mk);
            // E18.2: "open" is the panel's CURRENT one (is-current, cd-current);
            // other unlocked ones that are not done are "free"
            if (w === 'open' && !(code ? mk.classList.contains('cd-current') : a.classList.contains('is-current'))) w = 'free';
            if (!k || !w) return;
            rec.k[k] = rec.k[k] || {};
            rec.k[k][code ? 'code' : 'calc'] = w; n++;
          });
          // E18.3: and the chapters' locks, in their order
          rec.c = [].map.call(h.querySelectorAll('.nbmap-node.chap'), function(a){ return a.classList.contains('locked') ? 'locked' : 'open'; });
          if (n) {
            var old = all[id] ? JSON.stringify([all[id].k, all[id].c]) : '';
            if (old !== JSON.stringify([rec.k, rec.c])) {
              for (var q in all) if (all[q] && all[q].t > 1e9) all[q].t = 0;      // times written before E17.5
              for (q in all) if (all[q] && +all[q].t >= rec.t) rec.t = +all[q].t + 1;
              all[id] = rec;
              try { localStorage.setItem(COVER_KEY, JSON.stringify(all)); } catch (e) {}
            }
          }
        }
        return all;
      }
      function coverRec(all, cov){
        var id = modeNbId();
        if (id && all[id]) return all[id];
        // a cold cover has no feed: the record whose title the cover shows
        var txt = (cov.textContent || ''), hit = null;
        for (var k in all) if (all[k] && all[k].title && txt.indexOf(all[k].title) > -1 &&
                               (!hit || all[k].t > hit.t)) hit = all[k];
        return hit;
      }
      function coverPaint(){
        try { compatCover(); } catch (e) {}                  // E25.v: every pass that paints the cover
        var tls = allCls(document, 'nbcover-tl');            // E22.1b
        if (!tls.length) return;
        var w = modeWanted() || modeBuilt() || 'both';
        var all = coverRead();
        [].forEach.call(tls, function(tl){
          var cov = tl.closest('.nbcover') || tl.parentNode || tl;
          var rec = coverRec(all, cov);
          var sig = w + '|' + langOf() + '|' + (rec ? JSON.stringify([rec.k, rec.c]) : '');   // E17.1: + language
          if (tl.__nbCoverSig === sig) { coverLane(tl); return; }    // E13
          tl.__nbCoverSig = sig;
          // E18.1–4 (Applikation): the states are the panel's, kept per
          // notebook (exercises: solved/wrong/skipped, "open" = the current
          // one per lane, "free", "locked"; chapters: open/locked). Without a
          // record: per lane the first exercise open, the rest locked, and the
          // chapters after the gating lane's open one (calc; "code": coding) locked
          var nC = 0, nT = 0, nK = 0, seen = [0, 0], gate = 0, gl = w === 'code' ? 1 : 0, chSt = null, lane = [];
          [].forEach.call(tl.querySelectorAll('.nbtl-row'), function(r){
            // py-E15.4: a mark's short line comes as its title's 2nd line
            // (the sanitiser strips data-*) -> `data-desc`; `title` = name
            var tt = r.title, ti = tt.indexOf('\n');
            if (ti > -1) { r.setAttribute('data-desc', tt.slice(ti + 1)); r.title = tt.slice(0, ti); }
            var calc = r.classList.contains('nbtl-calc'), code = r.classList.contains('nbtl-code');
            // py-E23.5: the quiz and own data are built in every mode, so their marks stay
            var free = /\bnbtl-(?:quiz|byod)\b/.test(r.className);
            var hide = !free && ((w === 'code' && calc) || (w === 'calc' && code) || (w === 'plain' && (calc || code)));
            // !important: the cover's stylesheet sets the rows' display so
            if (hide) r.style.setProperty('display', 'none', 'important');
            else if (r.style.getPropertyPriority('display')) r.style.setProperty('display', 'flex');
            if (r.classList.contains('nbtl-chapter')) { nC++; chSt = rec && rec.c ? rec.c[nC - 1] || 'open' : gate ? 'locked' : 'open'; r.setAttribute('data-st', chSt); }
            else if (/\bnbtl-(title|group|end|cell)\b/.test(r.className)) chSt = null;
            // E23.7: a figure of a locked chapter is locked with it (pale, E18.3)
            if (r.classList.contains('nbtl-figure')) {
              if (chSt === 'locked') { if (r.getAttribute('data-st') !== 'locked') r.setAttribute('data-st', 'locked'); }
              else if (r.hasAttribute('data-st')) r.removeAttribute('data-st');
            }
            if (hide) return;
            if (calc) nT++;
            if (code) nK++;
            if (!calc && !code) return;
            var m = /\bnbtl-k-([a-z0-9]+)/.exec(r.className);
            var st = (m && rec && rec.k[m[1]] && rec.k[m[1]][code ? 'code' : 'calc']) || 'open';
            var ln = code ? 1 : 0, ex = /\bnbtl-(task|coding)\b/.test(r.className);
            // E23.7: quiz and BYOD are no step of a lane's gate (free, E18.4)
            if (!rec && st === 'open') {
              if (!ex) st = 'free';
              else { st = seen[ln] ? 'locked' : 'open'; seen[ln] = 1; if (ln === gl) gate = 1; }
            }
            lane.push([r, st, ln, ex]);
          });
          // 2026-10-06 (E23.3, Applikation) — ONE MARK PER LANE IS "OPEN": THE
          // HIGHEST UNLOCKED ONE. Of the exercises (and of the coding
          // exercises) that are unlocked and not yet done — the record's
          // "open" (the panel's current) and "free" — only the LAST in the
          // lane's order is "open" (green / purple, open lock); the others
          // are "free" and drawn neutral. A record from before E18.2 (used
          // browser storage) kept "open" on every unlocked one and the cover
          // showed several purple marks. Quiz and BYOD keep their own colour.
          var top = [-1, -1];
          lane.forEach(function(x, i){ if (x[3] && (x[1] === 'open' || x[1] === 'free')) top[x[2]] = i; });
          lane.forEach(function(x, i){
            var r = x[0], st = x[1];
            if (x[3] && (st === 'open' || st === 'free')) st = i === top[x[2]] ? 'open' : 'free';
            if (r.getAttribute('data-st') !== st) r.setAttribute('data-st', st);
            var mk = r.querySelector('.nbtl-mk');
            if (mk) {
              if (mk.__nbCol === undefined) mk.__nbCol = mk.style.color;
              mk.style.color = (x[3] && st === 'free' ? COVER_FREE : COVER_COL[st]) || mk.__nbCol;
            }
          });
          // E16.5: rows folded by a title/group mark of the cover stay hidden
          [].forEach.call(tl.querySelectorAll('.nbtl-row'), function(r){ if (r.__nbFold) r.style.setProperty('display', 'none', 'important'); });
          var hd = tl.querySelector('.nbcover-tl-h');
          if (hd) {
            var de = langOf() === 'de';                                  // E17.1
            var t = (de ? 'Zeitleiste \u00b7 ' + nC + ' Kapitel' : 'Timeline \u00b7 ' + nC + ' chapters')
                  + (nT ? ' \u00b7 ' + nT + (de ? ' Aufgaben' : ' exercises') : '')
                  + (nK ? ' \u00b7 ' + nK + (de ? ' Code' : ' coding') : '');   // E24 Stufe 2: „Code“ as de.txt
            if (hd.textContent !== t) hd.textContent = t;
          }
          coverLane(tl);                       // E13
        });
      }
      window.__nbCoverPaint = coverPaint;
      // 2026-10-01 (E13, Struktur + Applikation) — THE COVER'S LANE SCROLLS
      // SIDEWAYS. One row in natural size (CSS); where it is wider than its
      // box, JS says on which side marks are still out of sight —
      // `data-fade` on `.nbtl-lane`: 'l', 'r', 'lr' or '' (CSS fades there) —
      // and keeps a scroll bar under it: track `.nbtl-sb`, thumb
      // `.nbtl-sb-th`, thumb length = visible share (`--nbtl-th`, px, as
      // `--nbsb-th`), its left = scroll share (`--nbtl-tx`, px), `.nbdragging`
      // on the thumb while it is dragged; CSS draws both and hides the bar at
      // data-fade="" (contract in 02-dark.css, css-E13). The thumb drags, a click in the
      // track moves a page towards it, Shift+wheel and the trackpad scroll the
      // lane natively (docWheel leaves both alone). The first time the lane
      // is seen it shows the reader's place: the first exercise mark still
      // open, in the middle. Fits it: no fade, no bar.
      function coverLane(tl){
        var L = tl.querySelector('.nbtl-lane');
        if (!L) return;
        var sb = L.nextElementSibling;
        if (!sb || sb.className !== 'nbtl-sb') {
          sb = document.createElement('div');
          sb.className = 'nbtl-sb';
          sb.innerHTML = '<div class="nbtl-sb-th"></div>';
          L.after(sb);
          sb.onpointerdown = function(ev){
            var th = sb.firstChild, o = L.scrollWidth - L.clientWidth;
            ev.preventDefault(); ev.stopPropagation();
            if (ev.target !== th) {          // the track: a page towards the click
              L.scrollLeft += (ev.clientX < th.getBoundingClientRect().left ? -.9 : .9) * L.clientWidth;
              return;
            }
            var x0 = ev.clientX, s0 = L.scrollLeft, run = Math.max(1, sb.clientWidth - th.offsetWidth);
            sb.setPointerCapture(ev.pointerId);
            th.classList.add('nbdragging');
            sb.onpointermove = function(e){ L.scrollLeft = s0 + (e.clientX - x0) * o / run; };
            sb.onpointerup = sb.onpointercancel = function(){ sb.onpointermove = null; th.classList.remove('nbdragging'); };
          };
          L.onscroll = function(){ laneSet(L, sb); };
        }
        laneSet(L, sb);
        // the reader's place, once the lane can be measured
        if (!L.__nbStart && L.clientWidth > 0) {
          L.__nbStart = 1;
          var at = [].filter.call(L.querySelectorAll('.nbtl-calc,.nbtl-code'), function(r){
            return r.offsetWidth > 0 && (r.getAttribute('data-st') || 'open') === 'open'; })[0];
          if (at) {
            var lr = L.getBoundingClientRect(), ar = at.getBoundingClientRect();
            L.scrollLeft += ar.left + ar.width / 2 - lr.left - L.clientWidth / 2;
          }
        }
      }
      // 2026-10-12 (E29 P5, JavaScript) — FEEDBACK IS A LINE OF TEXT. Reader
      // 12.10.: a small widget, no form, no mailto, no error ring — only the
      // sentence (en/de) with the contact address from the metadata; Python
      // writes it, nothing here builds or fills a link. What E25.n added is
      // taken back: the tick, the link at the foot of the preview, the click
      // that rewrote the mailto (an older build's listener is switched off).
      if (window.__nbFbOff) { try { window.__nbFbOff(); } catch (e) {} window.__nbFbOff = null; }
      function fbClean(){
        [].forEach.call(document.querySelectorAll('.nbfb-cover, .nbfb-tick'), function(e){ e.remove(); });
      }
      // 2026-10-02 (E17.3, Applikation + Struktur) — LOG IN ON THE COVER.
      // Above Play, where the reader decides how to start: the same form as
      // in 👤 (12-rail-series-role, E19.5) — code + password + "Log in",
      // "New account", "Load file"; logged in it names the person id and
      // offers "Log out". A log-in brings the favourites at once: the cards
      // (content, language) stand on them, the cover's timeline wears the
      // style. Before the first Play nothing of ours runs (the cover is the
      // markdown cell alone), so the form appears once the page knows us —
      // the cover beside a run notebook, a reload after a run, or any cover
      // of a notebook opened after one ran. Contract: `.nbacct[data-where=
      // "cover"]` with its heading `.nbacct-t` (py-E17.3, 13-stats.css).
      function acctCover(){
        if (!window.__nbAcctForm) return;
        [].forEach.call(allCls(document, 'nbcover'), function(cov){      // E22.1b
          var play = cov.querySelector('.nbcover-play');
          if (!play) return;
          // rebase 03.10.: py-E17.3 puts THE block in the cover (`.nbacct`,
          // inline display:none, its data-* stripped by the sanitiser) — it
          // is adopted, no second one; a build without it gets one from here
          var w = cov.querySelector('.nbacct');
          if (!w) {
            w = document.createElement('div');
            w.className = 'nbacct';
            w.style.cssText = 'max-width:640px;margin:0 auto 18px';
          }
          if (w.getAttribute('data-where') !== 'cover') w.setAttribute('data-where', 'cover');
          // right above Play, under the language and the cards (they are put
          // before Play as well); never moved while the reader types in it
          var ae = document.activeElement;
          // E25.k: in its fold ("Sign in ▸", py-E25.k `details.nbacct-fold`) it stays
          if (!w.closest('.nbacct-fold') && w.nextElementSibling !== play && !(ae && w.contains(ae))) play.parentNode.insertBefore(w, play);
          window.__nbAcctForm(w);
        });
      }
      // 2026-10-06 (E24.3, JavaScript) — THE COVER IS THE FIRST OUTPUT THE
      // READER SEES. py-E24.3: the markdown cell is one start line, the cover
      // (card, goals, content, language, login, Play, timeline) is the LAST
      // output of the mega-cell, `.nbtitle.nbcover-out`, hidden by the
      // stylesheet in a notebook of ours (06-marks). It exists only where our
      // script runs, so here everything on it works at once (the forms above
      // fill every `.nbcover`). What this adds is WHEN it shows:
      //   * after a run, in a notebook panel where Play has not been pressed
      //     yet (the reader's own Run All / ▶ at the cell): the cover, laid over the notebook
      //     area, scrolling by itself; the timeline panel steps aside. "A
      //     run" = one that ran in this page (02-loading saw it running and
      //     noted it on the panel): outputs that only came with the file — a
      //     trusted notebook reopened, a page reloaded — open on the
      //     document, as before;
      //   * Play on it: the document, on the title (goTop) — no second run,
      //     unless the cover's content or language is not the one this run
      //     built: then Play restarts and runs as it always did, and the run
      //     that follows comes up as the document.
      // The choice is the panel's (a property of its node): after a reload,
      // or the tab closed and opened, the next run starts at the cover again;
      // ⚙ rebuilds, the
      // language and "start again with …" never bring it back.
      // Laid over, not laid out: the document under it stays in place and
      // measured (timeline, reading line, loading view all as before). The
      // cover stays where Python put it (inside the cell's output, so
      // `.jp-CodeCell .jp-OutputArea .nbcover-out` still finds it) and is
      // positioned `fixed`; JupyterLab's widgets carry `contain: strict`, so
      // "fixed" means "relative to the nearest of them" — the offset is
      // measured, not assumed, and corrected in one write.
      // 2026-10-08 (E25.v, JavaScript) — TOO OLD SAYS SO, WITH THE WAY.
      // Nutzer 08.10. ("kann eine zu alte Version auch woanders vorkommen?"):
      // what the page needs and a too-old front end lacks is looked at once
      // per page — the browser (CSS :has, structuredClone; WebCrypto and
      // CompressionStream only for the account), the Jupyter front end
      // (JupyterLab ≥ 4, Notebook ≥ 7; the classic Notebook 6 has `Jupyter.notebook`)
      // — and named on the preview in one line each, with what to do (en/de),
      // instead of failing silently. The kernel side (Python, ipywidgets) is
      // the bootstrap's (py-E25.v). Minimums: Chrome/Edge 105, Firefox 121,
      // Safari 15.4 (`:has`), JupyterLab 4, Notebook 7.
      function compatIssues(){
        if (window.__nbCompat) return window.__nbCompat;
        var out = [], has = false;
        try { has = !!(window.CSS && CSS.supports && CSS.supports('selector(:has(*))')); } catch (e) {}
        if (!has || typeof window.structuredClone !== 'function')
          out.push(['browser', 'This browser is too old for this notebook. Please update it (Chrome or Edge 105+, Firefox 121+, Safari 15.4+).',
                    'Dieser Browser ist für dieses Notebook zu alt. Bitte aktualisieren Sie ihn (Chrome oder Edge ab 105, Firefox ab 121, Safari ab 15.4).']);
        else if (!(window.crypto && crypto.subtle) || !window.CompressionStream)
          out.push(['account', 'This browser cannot keep an account here (no WebCrypto or CompressionStream): everything else works.',
                    'Dieser Browser kann hier kein Konto führen (kein WebCrypto oder CompressionStream): alles andere geht.']);
        var cfg = {}, el = document.getElementById('jupyter-config-data');
        try { if (el) cfg = JSON.parse(el.textContent || '{}') || {}; } catch (e) {}
        var app = String(cfg.appName || ''), ver = parseInt(String(cfg.appVersion || '').split('.')[0], 10);
        if (/JupyterLab/i.test(app) && ver > 0 && ver < 4)
          out.push(['lab', 'JupyterLab ' + cfg.appVersion + ' is too old: please run  pip install -U "jupyterlab>=4"  and start it again.',
                    'JupyterLab ' + cfg.appVersion + ' ist zu alt: bitte  pip install -U "jupyterlab>=4"  ausführen und neu starten.']);
        if ((/Jupyter Notebook/i.test(app) && ver > 0 && ver < 7) || (window.Jupyter && window.Jupyter.notebook && !document.querySelector('.jp-NotebookPanel')))
          out.push(['nb6', 'The classic Jupyter Notebook (6) is too old: please run  pip install -U "notebook>=7"  or open the file in JupyterLab.',
                    'Das klassische Jupyter Notebook (6) ist zu alt: bitte  pip install -U "notebook>=7"  ausführen oder die Datei in JupyterLab öffnen.']);
        return (window.__nbCompat = out);
      }
      window.__nbCompatIssues = compatIssues;
      function compatCover(){
        var is = compatIssues(), de = langOf() === 'de';
        allCls(document, 'nbcover').forEach(function(cov){
          var play = cov.querySelector('.nbcover-play');
          if (!play) return;
          var box = cov.querySelector('.nbcompat');
          if (!is.length) { if (box) box.remove(); return; }
          var txt = is.map(function(x){ return de ? x[2] : x[1]; }).join('\n');
          if (!box) {
            box = document.createElement('div'); box.className = 'nbcompat'; box.setAttribute('role', 'alert');
            box.style.cssText = 'max-width:640px;margin:10px auto;padding:8px 12px;border:1px solid #c9a227;border-radius:8px;'
              + 'font-size:.85em;text-align:left;white-space:pre-line';
            cov.insertBefore(box, cov.firstChild);
          }
          if (box.textContent !== txt) box.textContent = txt;
        });
      }
      function covOf(P){ return P ? byCls(P, 'nbcover-out') : null; }
      function covOn(P){
        return !!(P && P.__nbRan && !P.__nbDoc && P.getAttribute('data-digichem') === '1' && covOf(P)
                  && !/^(pycharm|vscode|colab)$/.test((function(){ try { return nbEnv().env; } catch (e) { return ''; } })()));
      }
      window.__nbCoverOn = function(el){ return covOn(el && el.closest ? el.closest('.jp-NotebookPanel') : visiblePanel()); };
      function covLay(c, P){
        var s = c.style;
        if (!c.hasAttribute('data-nbcov')) {
          c.__nbSt0 = c.getAttribute('style');
          c.setAttribute('data-nbcov', '1');
          s.setProperty('display', 'block', 'important');
          s.setProperty('position', 'fixed', 'important');
          s.setProperty('margin', '0', 'important');
          s.setProperty('z-index', '10040', 'important');
          s.setProperty('overflow', 'auto', 'important');
          s.setProperty('overscroll-behavior', 'contain');
          s.setProperty('box-sizing', 'border-box', 'important');
          // room under the last line (the old cover had its 1400-px room): a fold
          // on the cover's timeline, which shortens it, never scrolls the page
          s.setProperty('padding', '26px 16px 45vh', 'important');
          s.setProperty('background', 'var(--jp-layout-color0, #fff)', 'important');
          s.left = '0px'; s.top = '0px';
          // the stylesheet hides `.nbcover` in a notebook that has run (the
          // old cold cover, 06-marks `.nbrail-own .nbcover`); over the cover
          // it is the point
          var inn = byCls(c, 'nbcover');
          if (inn) { inn.__nbSt0 = inn.getAttribute('style'); inn.style.setProperty('display', 'block', 'important'); }
          // … and the document's scroller fades its top and bottom 84 px
          // (mask-image) — over the cover that faded the title card
          var sc = byCls(P, 'jp-WindowedPanel-outer');
          // (and its clip-path, css-E23.10: the lens strip's cut-out notched the card)
          if (sc) { c.__nbSc = sc; sc.style.setProperty('-webkit-mask-image', 'none', 'important'); sc.style.setProperty('mask-image', 'none', 'important');
                    sc.style.setProperty('clip-path', 'none', 'important'); }
          // … and the cover lives in the mega-cell: JupyterLab paints (and
          // hit-tests) a cell only while it is near the view (windowing,
          // `content-visibility`) — with the page scrolled down to a cell of
          // the reader's own, the cover was laid out but not drawn (measured:
          // a click on its title mark went to the scroller). The cell is
          // drawn while the cover is up, and should the page stand below its
          // end, the page is moved up until a strip of it is in view (after a
          // run it is: the title on the line; Play puts it there anyway,
          // without Play the old place comes back).
          c.__nbCell = c.closest('.jp-Cell');
          if (sc) c.__nbScTop = sc.scrollTop;
        }
        // every pass: a fold on the cover folds the document under it too, and
        // the page can end up below the cell (measured with a cell of the
        // reader's own: the mega-cell 243 px high, 160 px above the view)
        var cl = c.__nbCell, sk = c.__nbSc;
        if (cl) {
          if (cl.style.getPropertyValue('content-visibility') !== 'visible') cl.style.setProperty('content-visibility', 'visible', 'important');
          if (sk) {
            var sr = sk.getBoundingClientRect(), cr = cl.getBoundingClientRect();
            if (cr.bottom < sr.top + 40) sk.scrollTop -= sr.top + 40 - cr.bottom + sr.height / 2;
            else if (cr.top > sr.bottom - 40) sk.scrollTop += cr.top - sr.bottom + 40 + sr.height / 2;
          }
        }
        // 2026-10-07 (E24 Stufe 2 Rest, J24.3a) — THE COVER TAKES THE LENS
        // OFF ITSELF. The lens zooms every child of a cell (14-rail
        // zoomTargets, CSS `zoom`), the mega-cell's output with the cover in
        // it: with a lens of 130 % left by an earlier step the cover stood
        // 1391 × 1013 over a notebook of 1070 × 779 (Tor 07.10.), and what
        // was on it (names, beam) had another size than at 100 % (C23.2/C23.8
        // red after other tests). The cover is not the document: zoom = 1 /
        // the lens above it, so its box is the notebook area and its content
        // the same at every lens. Read every pass (the lens can change).
        var k = 1;
        for (var za = c.parentElement; za && za !== P; za = za.parentElement) {
          var zv = parseFloat(getComputedStyle(za).zoom);
          if (zv > 0) k *= zv;
        }
        var zw = Math.abs(k - 1) < 0.001 ? '' : String(1 / k);
        if (s.zoom !== zw) s.zoom = zw;
        var nb = P.querySelector('.jp-Notebook') || P, t = nb.getBoundingClientRect(), r = c.getBoundingClientRect();
        if (t.width < 2 || t.height < 2) return;
        var L = (parseFloat(s.left) || 0) + t.left - r.left, T = (parseFloat(s.top) || 0) + t.top - r.top;
        if (Math.abs(r.left - t.left) > 0.5) s.left = L + 'px';
        if (Math.abs(r.top - t.top) > 0.5) s.top = T + 'px';
        if (Math.abs(r.width - t.width) > 0.5) s.width = t.width + 'px';
        if (Math.abs(r.height - t.height) > 0.5) s.height = t.height + 'px';
      }
      function covOff(c, keepTop){
        if (!c.hasAttribute('data-nbcov')) return;
        c.removeAttribute('data-nbcov');
        if (c.__nbSt0 != null) c.setAttribute('style', c.__nbSt0); else c.removeAttribute('style');
        var inn = byCls(c, 'nbcover');
        if (inn && '__nbSt0' in inn) { if (inn.__nbSt0 != null) inn.setAttribute('style', inn.__nbSt0); else inn.removeAttribute('style'); }
        if (c.__nbSc) { c.__nbSc.style.removeProperty('-webkit-mask-image'); c.__nbSc.style.removeProperty('mask-image'); c.__nbSc.style.removeProperty('clip-path');
                        if (!keepTop && c.__nbScTop != null) c.__nbSc.scrollTop = c.__nbScTop; c.__nbSc = null; }
        if (c.__nbCell) { c.__nbCell.style.removeProperty('content-visibility'); c.__nbCell = null; }
      }
      // 2026-10-08 (E25.e, JavaScript) — THE PREVIEW IN A FOREIGN FRONT END.
      // PyCharm/DataSpell, VS Code and Colab draw the outputs without a
      // JupyterLab around them (no `.jp-NotebookPanel`): covOn() is false
      // there, so nothing was laid over and the cover stood as the LAST
      // output under the document (still copy or widgets) — two title
      // cards, and Play named a menu path instead of opening the document
      // that was already there (Nutzer 08.10., PyCharm: "Play tut nichts").
      // Here the cover is the preview the same way: the outputs of the
      // mega-cell before it (ours: the document, the feed, the still copy,
      // widgets; empty script outputs) are hidden while it is up, and so is
      // the floating tool column (E25.b/g: it hovered over the editor);
      // Play hides the cover and shows the document on its title — no
      // second run (one run built it). The level is found, not assumed:
      // from the cover up to the first ancestor whose earlier children hold
      // something of ours — the cell's output list in every front end
      // (each output its own wrapper or not). Other cells are never touched:
      // no such level below <body> → nothing is hidden.
      var FR_OURS = '.nbtitle-doc,.nbfeed,.nbstatic-note,.nbctl-stash,.nbwidget-hint,.nbrail,.jupyter-widgets,.widget-box';
      function frEnv(){
        try { return nbEnv().ui === 'frame' && !document.querySelector('.jp-NotebookPanel'); } catch (e) { return false; }
      }
      function frOurs(s){ return !!(s && s.matches && (s.matches(FR_OURS) || s.querySelector(FR_OURS))); }
      function frDoc(c){
        var x = c, out = [], s;
        while (x.parentElement && x.parentElement !== document.body) {
          var hit = false;
          for (s = x.previousElementSibling; s && !hit; s = s.previousElementSibling) hit = frOurs(s);
          if (hit) break;
          x = x.parentElement;
        }
        // at that level every earlier sibling is an earlier output of the
        // mega-cell (a quiz drawn by its own library carries no class of ours)
        if (x.parentElement === document.body) return out;
        for (s = x.previousElementSibling; s; s = s.previousElementSibling) out.push(s);
        return out;
      }
      function frHide(e, on){
        if (on) { if (!('__nbFrSt' in e)) { e.__nbFrSt = e.getAttribute('style'); e.style.setProperty('display', 'none', 'important'); } }
        else if ('__nbFrSt' in e) { if (e.__nbFrSt != null) e.setAttribute('style', e.__nbFrSt); else e.removeAttribute('style'); delete e.__nbFrSt; }
      }
      function frSync(){
        var cs = allCls(document, 'nbcover-out'), up = false, h = document.getElementById(HOST_ID);
        cs.forEach(function(c, i){
          // only the newest cover is a preview; an older one (a rerun left it) goes
          var mine = i === cs.length - 1 && !c.__nbFrDoc;
          if (mine) { up = true; (c.__nbFrList = frDoc(c)).forEach(function(e){ frHide(e, true); }); }
          else { (c.__nbFrList || []).forEach(function(e){ frHide(e, false); }); c.__nbFrList = null;
                 if (i < cs.length - 1 || c.__nbFrDoc) frHide(c, true); }
        });
        var R = document.documentElement;
        if (up !== R.hasAttribute('data-nbcovup')) { if (up) R.setAttribute('data-nbcovup', 'frame'); else R.removeAttribute('data-nbcovup'); }
        // the tool column floats over the editor in such a front end (E25.b):
        // not shown there at all; the cover carries content, language, login
        if (h && h.style.getPropertyValue('display') !== 'none') h.style.setProperty('display', 'none', 'important');
      }
      // Play on the preview there: true = done (the document shown, or a rebuild asked for)
      function frPlay(ra){
        var c = ra.closest && ra.closest('.nbcover-out');
        if (!c || !frEnv()) return false;
        var w = modeWanted(ra), b = modeBuilt(ra), lb = langBuilt();
        if ((w && b && w !== b) || (lb && langOf() !== lb)) {
          // another content or language than this run built: the kernel can
          // only be told through live widgets (⚙ "Rebuild now"); a still copy
          // has none — then the document as built, and the cover says why
          var go = null, box = document.querySelector('.nbctl-difficulty');
          if (box) [].forEach.call(box.querySelectorAll('.nbrunall, .nbrunall button'), function(x){ if (!go && !x.disabled) go = x; });
          if (go) {
            if (w) modeToKernel(w, ra);
            try { langToKernel(langOf()); } catch (e) {}
            var LV = window.__nbLoading;
            if (LV) { try { LV.show(ra, false); } catch (e) {} }
            setTimeout(function(){ go.click(); }, 700);
            return true;
          }
        }
        c.__nbFrDoc = Date.now();
        frSync();
        // py-E25.a writes the document's card hidden where the still copy is
        // on (`nbstatic-hide`): the preview was the one title; now it is this
        [].forEach.call(document.querySelectorAll('.nbtitle-doc.nbstatic-hide'), function(x){ x.style.removeProperty('display'); });
        var t = document.querySelector('.nbtitle-doc') || document.querySelector('.nbstatic-note');
        if (t && t.scrollIntoView) { try { t.scrollIntoView({block: 'start'}); } catch (e) { t.scrollIntoView(); } }
        return true;
      }
      window.__nbFramePlay = frPlay;
      function covSync(){
        if (frEnv()) { frSync(); return; }                              // E25.e
        allCls(document, 'nbcover-out').forEach(function(c){
          var P = c.closest('.jp-NotebookPanel');
          // outputs that came with the file (no run seen here): the document
          // is what this panel shows, and a later run (⚙ rebuild, a stored
          // mode) keeps it so (measured: test_regress, a page reloaded, then
          // a rebuild brought the cover up over the document)
          if (P && !P.__nbRan && !P.__nbDoc) P.__nbDoc = 1;
          if (P && covOn(P) && !P.classList.contains('lm-mod-hidden')) covLay(c, P); else covOff(c);
        });
      }
      window.__nbCoverSync = covSync;
      // 2026-10-08 (E25.h, JavaScript) — "NOT RUNNING YET" IS FOR A DEAD
      // PREVIEW. py-E25.h writes the line `.nbcover-stale` into the cover:
      // a saved output (Lite and PyCharm keep it, a reopened file shows it)
      // where nothing of ours runs and every button is dead. Where this
      // script runs, the preview is alive — the line goes, every pass (a
      // rebuilt cover brings a new one).
      function staleOff(){
        allCls(document, 'nbcover-stale').forEach(function(x){
          if (x.style.getPropertyValue('display') !== 'none') x.style.setProperty('display', 'none', 'important'); });
      }
      // the cover of a notebook again, or the document again (true/false), in
      // the panel of `el` or the one in front — what Play undoes; for the
      // measuring scripts, which read the cover of the notebook they ran
      // instead of running a second copy. Returns whether the cover is on.
      window.__nbCoverShow = function(on, el){
        var P = (el && el.closest && el.closest('.jp-NotebookPanel')) || visiblePanel();
        if (!P || !covOf(P)) return false;
        if (on) { P.__nbDoc = 0; P.__nbRan = P.__nbRan || Date.now(); } else P.__nbDoc = Date.now();
        try { dcMark(); covSync(); } catch (e) {}
        if (!on) { try { sync(); } catch (e) {} }
        return covOn(P);
      };
      // Play on the output cover: true = done here (the document shown)
      function covPlay(ra){
        var c = ra.closest && ra.closest('.nbcover-out'), P = c && c.closest('.jp-NotebookPanel');
        if (!P || !covOn(P)) return false;   // a cover that is not up: Play as before
        P.__nbDoc = Date.now();
        var w = modeWanted(ra), b = modeBuilt(ra), lb = langBuilt();
        if ((w && b && w !== b) || (lb && langOf() !== lb)) {
          // a rebuild — the kernel is running: told, then ⚙ "Rebuild now"
          // under the loading view, as "start again with …" does (no kernel
          // restart: measured, Play's restart of a live kernel left two page
          // errors of JupyterLab's, "Canceled future for kernel_info_request");
          // no ⚙ to press → Play as before (restart and run all)
          var go = null, box = modeQ(ra, '.nbctl-difficulty'), LV = window.__nbLoading;
          if (box) [].forEach.call(box.querySelectorAll('.nbrunall, .nbrunall button'), function(x){ go = go || x; });
          if (!go) return false;
          if (w) modeToKernel(w, ra);
          try { langToKernel(langOf()); } catch (e) {}
          if (LV) { try { LV.show(ra, false); } catch (e) {} }
          setTimeout(function(){ go.click(); }, 700);
          return true;
        }
        covOff(c, true);
        try { dcMark(); } catch (e) {}
        try { sync(); } catch (e) {}
        window.requestAnimationFrame(function(){ try { window.__nbGoTop && window.__nbGoTop(); } catch (e) {} });
        return true;
      }
      function laneSet(L, sb){
        var cw = L.clientWidth, o = L.scrollWidth - cw, sl = L.scrollLeft, on = cw > 0 && o > 1;
        L.setAttribute('data-fade', on ? (sl > 1 ? 'l' : '') + (sl < o - 1 ? 'r' : '') : '');
        if (!on) return;
        var T = sb.clientWidth, tw = Math.max(24, Math.round(T * cw / L.scrollWidth)), st = sb.firstChild.style;
        st.setProperty('--nbtl-th', tw + 'px');
        st.setProperty('--nbtl-tx', Math.round((T - tw) * Math.min(1, sl / o)) + 'px');
      }
      function modeClick(ev){
        if (endClick(ev)) return;                                       // E16.12
        if (langClick(ev)) return;                                      // E17.1
        var o = ev.target && ev.target.closest ? ev.target.closest('.nbmode .nbmode-opt') : null;
        if (!o) return;
        ev.preventDefault(); ev.stopPropagation();
        var v = o.getAttribute('data-mode');
        if (!MODE_TXT[v]) return;
        // E21.6: ONE click — stored for the cover's own notebook, painted at
        // once, told to its kernel if it runs, else written where its first
        // run reads it
        modeStore(v, o);
        if (!modeToKernel(v, o) && !modeFile(v, o) && !modeChan(o)) modeNote(o, v);    // E25.f
        [].forEach.call(document.querySelectorAll('.nbmode'), modePaint);
        coverPaint();                          // E9.11
      }
      // 2026-10-08 (E25.f, JavaScript) — A CHOICE THAT CANNOT ARRIVE SAYS SO.
      // Where nothing reaches the kernel — no live widget field (a window
      // that shows the still copy, PyCharm 08.10.) and no server to write
      // the file its run reads — the card is still chosen and stored for
      // this notebook, and one line under the cards says that this run
      // stays as built and where the content can be changed. It goes again
      // when the choice is the built one.
      function modeChan(o){
        var i = modeQ(o, '.nbctl-modein input'), d = modeDropdown(o);
        return !!((i && !i.disabled) || (d && !d.disabled));
      }
      function modeNote(o, v){
        var cov = o.closest && o.closest('.nbcover'), box = o.closest && o.closest('.nbmode');
        if (!cov || !box) return;
        var n = cov.querySelector('.nbmode-note'), b = modeBuilt(o), de = langOf() === 'de';
        if (b && v === b) { if (n) n.remove(); return; }
        if (!n) {
          n = document.createElement('div'); n.className = 'nbmode-note'; n.setAttribute('role', 'status');
          n.style.cssText = 'margin:8px auto 0;max-width:560px;font-size:.82em;text-align:center;opacity:.85';
        }
        if (box.nextSibling !== n) box.parentNode.insertBefore(n, box.nextSibling);
        n.textContent = de
          ? 'Gespeichert. Diese Ansicht erreicht den laufenden Kernel nicht (sie zeichnet keine Widgets): das Notebook bleibt, wie es gebaut ist. Den Inhalt wechseln können Sie in JupyterLab, Jupyter Notebook, JupyterLite, VS Code oder Colab.'
          : 'Saved. This view cannot reach the running kernel (it draws no widgets): the notebook stays as it was built. You can change the content in JupyterLab, Jupyter Notebook, JupyterLite, VS Code or Colab.';
      }
      function modeKeys(ev){
        // a radio group: ← → move the choice (and the focus), Space/Enter pick
        var o = ev.target && ev.target.closest ? ev.target.closest('.nbmode .nbmode-opt') : null;
        if (!o || (ev.key !== 'ArrowLeft' && ev.key !== 'ArrowRight')) return;
        var os = [].slice.call(o.parentNode.querySelectorAll('.nbmode-opt'));
        var j = (os.indexOf(o) + (ev.key === 'ArrowRight' ? 1 : os.length - 1)) % os.length;
        ev.preventDefault(); ev.stopPropagation();
        os[j].focus(); os[j].click();
      }
      // 2026-10-02 (E16.12, Applikation) — UNDER "END OF THE GUIDE" (Python's
      // `.nbend-go`): `.nbend-top` puts Title back on the reading line (goTop,
      // as after a start); `.nbend-mode[data-mode]` starts again with that
      // content — stored, told to the kernel, and the ⚙ "Rebuild now"
      // pressed under the loading view, as a choice in ⚙ does.
      function endClick(ev){
        var b = ev.target && ev.target.closest ? ev.target.closest('.nbend-btn') : null, v;
        if (!b || ev.button) return false;
        ev.preventDefault(); ev.stopPropagation();
        if (b.classList.contains('nbend-top')) { if (window.__nbGoTop) window.__nbGoTop(); return true; }
        v = b.getAttribute('data-mode');
        if (!MODE_TXT[v]) return true;
        modeStore(v, b); modeToKernel(v, b);
        var go = null, box = modeQ(b, '.nbctl-difficulty'), LV = window.__nbLoading;
        if (box) [].forEach.call(box.querySelectorAll('.nbrunall, .nbrunall button'), function(x){ go = go || x; });
        if (LV) { try { LV.show(go || b, false); } catch (e) {} }
        setTimeout(function(){ if (go) go.click(); else if (LV) { try { LV.hide(); } catch (e) {} } }, 700);
        return true;
      }
      if (window.__nbModeOff) { try { window.__nbModeOff(); } catch (e) {} }
      document.addEventListener('click', modeClick, true);
      document.addEventListener('change', modeFromSelect, true);
      window.addEventListener('keydown', modeKeys, true);
      window.__nbModeOff = function(){
        document.removeEventListener('click', modeClick, true);
        document.removeEventListener('change', modeFromSelect, true);
        window.removeEventListener('keydown', modeKeys, true);
      };
      // after a run: built ≠ wanted → tell the kernel and run again, once
      // 2026-10-02 (E16.1, Applikation) — ONCE MEANS ONCE. The guard was a
      // clock (one retry per 90 s), so a kernel that cannot take the wish
      // was asked again and again. MEASURED in a real JupyterLite: its kernel
      // lives in a web worker without localStorage, never reads the stored
      // mode and builds "both" every time — with "calc" stored, Modeling
      // restarted under the loading view every ≈ 90 s, endlessly. Now one
      // retry per notebook, wish and built mode in a tab; then the run stays
      // as it was built.
      function modeAfterRun(){
        modeLearn();                            // E21.6: this title is this id
        try { langAfterRun(); } catch (e) {}                            // E17.1
        var w = modeWanted(), b = modeBuilt();
        if (!w || !b || w === b) return;
        // E24.3: while the cover is up the choice waits for Play (which
        // rebuilds it, covPlay) — a card is a choice, not a start
        if (covOn(visiblePanel())) return;
        var rk = 'digichemjn.mode.retry.' + (modeNbId() || 'nb'), pair = w + '>' + b, last = '';
        try { last = sessionStorage.getItem(rk) || ''; } catch (e) { return; }
        if (last === pair) return;
        var vp = visiblePanel();
        var st = ((vp || document).querySelector('.jp-Notebook-ExecutionIndicator') || {getAttribute: function(){ return 'idle'; }})
                 .getAttribute('data-status');
        if (st && st !== 'idle') return;
        if (!modeToKernel(w)) return;
        try { sessionStorage.setItem(rk, pair); } catch (e) { return; }
        setTimeout(function(){
          var go = null, box = modeQ(null, '.nbctl-difficulty');
          if (box) [].forEach.call(box.querySelectorAll('.nbrunall, .nbrunall button'), function(b){ go = go || b; });
          var LV = window.__nbLoading;
          if (LV) { try { LV.show(go || document.body, false); } catch (e) {} }
          if (go) go.click(); else if (LV) { try { LV.hide(); } catch (e) {} }
        }, 700);
      }

      // 2026-09-29 (E8.23, Applikation) — OURS, AND ONLY OURS. Our stylesheet
      // and our handlers reached into every notebook of the window (the
      // reader's EIS_Battery_Analysis in the next tab lost its prompts). The
      // contract with CSS: every notebook panel of ours carries
      // `data-digichem="1"` (it has our feed, our cover or our panel), and the
      // body carries `nb-dc-active` exactly while such a panel is the one in
      // front; CSS lets global rules act only under those two. Our timeline
      // panel steps out of the way (display:none) while another notebook is
      // in front, and Ctrl +/−/0 and Ctrl+wheel are ours only over our panel.
      function dcOurs(p){
        return !!(p && (p.classList.contains('nbrail-own') ||
                        p.querySelector('.nbfeed, .nbcover, .nbtitle-h')));
      }
      window.__nbDcOurs = function(el){
        var p = el && el.closest ? el.closest('.jp-NotebookPanel') : null;
        if (p) return p.getAttribute('data-digichem') === '1' || dcOurs(p);
        return !byCls(document, 'jp-NotebookPanel');   // no Lab around: one page, ours (E22.1b)
      };
      function dcMark(){
        // 2026-10-06 (E23.11/E23.18 Nach-Runde, Applikation) — THE PAGE
        // FOLLOWS THE KERNEL'S WORD BACK. nbEnv() writes data-nbenv/data-nbui
        // on <html> only when someone asks it (the script's start, Play, a
        // message that names the menu path). A word that changed back — the
        // feed said "pycharm" for a moment, then the kernel's own again (a
        // rerun elsewhere; test_regress J22.3 clicks Play under "pycharm" and
        // puts the word back) — left <html> on data-nbui="frame": the
        // stylesheet's fall-back look stayed on in JupyterLab, rail, grip,
        // scroll bar and marker hidden (display none), the panel undocked.
        // Measured v1.65 + js-E23.11/E23.18, tor rows after J22.3: the panel
        // 826 px over the axis (J23.11), the thumb 0 px (J23.18). Now every
        // pass asks once: one look at the feed's word, cached per word —
        // nothing is laid out, nothing is written while it stays the same.
        try { nbEnv(); } catch (e) {}
        var ps = allCls(document, 'jp-NotebookPanel');       // E22.1b
        for (var i = 0; i < ps.length; i++) {
          var mine = dcOurs(ps[i]);
          if (mine && ps[i].getAttribute('data-digichem') !== '1') ps[i].setAttribute('data-digichem', '1');
          // py-E23.1: the run's language on our panel — the hook for words the stylesheet writes
          // (the YOC strip, "Locked"); one look at the first feed (all of a run say the same)
          if (mine) {
            var fl = ps[i].querySelector('.nbfeed[data-nblang]'), lg = fl ? fl.getAttribute('data-nblang') : null;
            if (lg && ps[i].getAttribute('data-nblang') !== lg) ps[i].setAttribute('data-nblang', lg);
          }
          else if (!mine && ps[i].hasAttribute('data-digichem')) ps[i].removeAttribute('data-digichem');
        }
        var vp = visiblePanel();
        var on = vp ? vp.getAttribute('data-digichem') === '1'
                    : (!ps.length && !!byCls(document, 'nbfeed'));
        if (document.body.classList.contains('nb-dc-active') !== on)
          document.body.classList.toggle('nb-dc-active', on);
        var h = document.getElementById(HOST_ID);
        if (h) { var d = on && !covOn(vp) ? '' : 'none'; if (h.style.display !== d) h.style.display = d; }   // E24.3: not over the cover
        var hw = byCls(document, 'nbhelp');
        if (hw && !on && hw.classList.contains('on')) hw.classList.remove('on');
        return on;
      }
      // 2026-10-12 (E29 D7, JavaScript) — THE FONT SIZE IS ITS OWN SETTING.
      // Reader 12.10.: at a lens of 100 %% the text is too small, and the lens
      // is the wrong tool for it (it scales everything, the marks' places
      // too). py-E29 gives the place in the ⚙ drawer — `.nbcell.pg-diff.
      // nbfontcell` (display:none) > `.nbfont-slot[data-min data-max data-step
      // data-std]` — and its words; here the control: A− · value · A+
      // (`.nbbtn`, `output.nbfs-val`; a double click on the value = standard),
      // the cell shown, the value kept per notebook (`digichemjn.fontsize.v1.
      // <id>`, level C like the lens and the panel's width), independent of
      // the lens. The stylesheet reads `--nbfs` (css-E29: a number, 1 = 100 %%)
      // on <html> and on the notebook's panel (the one in front decides <html>;
      // its panel keeps its own). A build without the cell gets the same one
      // from here (the words of the contract, claude/VERTRAG-E29-py.md).
      var FS_KEY = 'digichemjn.fontsize.v1';
      function fsKey(){ var id = ''; try { id = nbId(); } catch (e) {} return id ? FS_KEY + '.' + id : null; }
      function fsRange(){
        var sl = document.querySelector('#' + HOST_ID + ' .nbfont-slot'), n = function(a, d){ var v = sl ? parseFloat(sl.getAttribute(a)) : NaN; return v > 0 ? v : d; };
        return {min: n('data-min', 90), max: n('data-max', 150), step: n('data-step', 10), std: n('data-std', 100)};
      }
      function fsLevel(){
        var R = fsRange(), v = NaN, k = fsKey();
        try { if (k) v = parseFloat(localStorage.getItem(k)); } catch (e) {}
        return v >= R.min && v <= R.max ? v : R.std;
      }
      function fsSet(v){
        var R = fsRange();
        v = Math.max(R.min, Math.min(R.max, Math.round(v / R.step) * R.step));
        var k = fsKey();
        try { if (k) { if (v === R.std) localStorage.removeItem(k); else localStorage.setItem(k, String(v)); } } catch (e) {}
        fsApply(); fsField();
        return v;
      }
      window.__nbFontSize = function(v){ return v === undefined ? fsLevel() : fsSet(v); };   // for the tests
      function fsApply(){
        var P = visiblePanel();
        if (!P || P.getAttribute('data-digichem') !== '1') return;
        var v = fsLevel(), f = String(Math.round(v) / 100), R = document.documentElement;
        [R, P].forEach(function(e){ if (e.style.getPropertyValue('--nbfs') !== f) e.style.setProperty('--nbfs', f); });
        if (P.getAttribute('data-nbfs') !== String(v)) P.setAttribute('data-nbfs', String(v));
      }
      function fsField(){
        var h = document.getElementById(HOST_ID), g = h && h.querySelector('.nbdrawer-grid');
        if (!g) return;
        var de = !!(window.__nbDe && window.__nbDe()), L = function(en, d){ return de ? d : en; };
        var c = g.querySelector('.nbfontcell');
        if (!c) {
          c = document.createElement('div'); c.className = 'nbcell pg-diff nbfontcell';
          c.innerHTML = '<div class="nbcell-h"></div><div class="nbfont-slot" data-min="90" data-max="150" data-step="10" data-std="100"></div>';
          c.firstChild.textContent = L('Font size', 'Schriftgr\u00f6\u00dfe');
          g.insertBefore(c, g.firstChild);
        }
        if (c.style.getPropertyValue('display') === 'none') c.style.removeProperty('display');
        var sl = c.querySelector('.nbfont-slot');
        if (!sl) return;
        if (!sl.querySelector('.nbfs-val')) {
          sl.innerHTML = '<button type="button" class="nbbtn nbfs-minus">A\u2212</button><output class="nbfs-val"></output>'
                       + '<button type="button" class="nbbtn nbfs-plus">A+</button>';
          var step = function(d){ return function(ev){ ev.preventDefault(); ev.stopPropagation(); fsSet(fsLevel() + d * fsRange().step); }; };
          sl.querySelector('.nbfs-minus').addEventListener('click', step(-1));
          sl.querySelector('.nbfs-plus').addEventListener('click', step(1));
          sl.querySelector('.nbfs-val').addEventListener('dblclick', function(ev){ ev.preventDefault(); fsSet(fsRange().std); });
        }
        var v = fsLevel(), o = sl.querySelector('.nbfs-val'), t = v + ' %';
        if (o.textContent !== t) o.textContent = t;
        var tip = L('Text size of the document, independent of the zoom (stored per notebook)',
                    'Schriftgr\u00f6\u00dfe des Dokuments, unabh\u00e4ngig von der Lupe (je Notebook gemerkt)');
        if (sl.title !== tip) sl.title = tip;
        o.title = L('Reset to standard (100 %)', 'Auf Standard zur\u00fcck (100 %)');
        sl.querySelector('.nbfs-minus').setAttribute('aria-label', L('Smaller text', 'Kleinere Schrift'));
        sl.querySelector('.nbfs-plus').setAttribute('aria-label', L('Larger text', 'Gr\u00f6\u00dfere Schrift'));
      }
      // E31 G1 (2026-10-12, Werkstatt JS; claude/VERTRAG-E31-js.md) — THE SIZE OF THE CONTROLS, a setting of
      // its own beside the text size (D7) and the lens: tools, panel, marks, pips, names, marker, grip (Lab:
      // every size the panel draws × --nbk carries it — 14-grip-zoom applyGui; the tool column × --nbgs: CSS).
      // ⚙ cell `.nbcell.pg-diff.nbguicell` > `.nbgui-slot` (⊖ · value · ⊕, double click = 100 %%), the value
      // kept per notebook (`digichemjn.guiscale.v1.<id>`, level C), --nbgs on <html>, the panel and the host.
      var GS_KEY = 'digichemjn.guiscale.v1', GSR = {min: 80, max: 150, step: 10, std: 100};
      function gsKey(){ var id = ''; try { id = nbId(); } catch (e) {} return id ? GS_KEY + '.' + id : null; }
      function gsLevel(){
        var v = NaN, k = gsKey();
        try { if (k) v = parseFloat(localStorage.getItem(k)); } catch (e) {}
        return v >= GSR.min && v <= GSR.max ? v : GSR.std;
      }
      window.__nbGsF = function(){ return gsLevel() / 100; };
      function gsSet(v){
        v = Math.max(GSR.min, Math.min(GSR.max, Math.round(v / GSR.step) * GSR.step));
        var k = gsKey();
        try { if (k) { if (v === GSR.std) localStorage.removeItem(k); else localStorage.setItem(k, String(v)); } } catch (e) {}
        gsApply(); gsField();
        try { applyGui(document.getElementById(HOST_ID)); } catch (e) {}
        return v;
      }
      window.__nbGuiSize = function(v){ return v === undefined ? gsLevel() : gsSet(v); };   // for the tests
      function gsApply(){
        var P = visiblePanel();
        if (!P || P.getAttribute('data-digichem') !== '1') return;
        var v = gsLevel(), f = String(Math.round(v) / 100), R = document.documentElement, H = document.getElementById(HOST_ID);
        [R, P, H].forEach(function(e){ if (e && e.style.getPropertyValue('--nbgs') !== f) e.style.setProperty('--nbgs', f); });
        if (P.getAttribute('data-nbgs') !== String(v)) P.setAttribute('data-nbgs', String(v));
      }
      function gsField(){
        var h = document.getElementById(HOST_ID), g = h && h.querySelector('.nbdrawer-grid');
        if (!g) return;
        var de = !!(window.__nbDe && window.__nbDe()), L = function(en, d){ return de ? d : en; };
        var c = g.querySelector('.nbguicell');
        if (!c) {
          c = document.createElement('div'); c.className = 'nbcell pg-diff nbguicell';
          c.innerHTML = '<div class="nbcell-h"></div><div class="nbgui-slot"></div>';
          var fc = g.querySelector('.nbfontcell');
          g.insertBefore(c, fc ? fc.nextSibling : g.firstChild);
        }
        var hd = c.querySelector('.nbcell-h'), ht = L('Interface size', 'Größe der Bedienelemente');
        if (hd && hd.textContent !== ht) hd.textContent = ht;
        var sl = c.querySelector('.nbgui-slot');
        if (!sl) return;
        if (!sl.querySelector('.nbgs-val')) {
          sl.innerHTML = '<button type="button" class="nbbtn nbgs-minus">⊖</button><output class="nbgs-val"></output>'
                       + '<button type="button" class="nbbtn nbgs-plus">⊕</button>';
          var step = function(d){ return function(ev){ ev.preventDefault(); ev.stopPropagation(); gsSet(gsLevel() + d * GSR.step); }; };
          sl.querySelector('.nbgs-minus').addEventListener('click', step(-1));
          sl.querySelector('.nbgs-plus').addEventListener('click', step(1));
          sl.querySelector('.nbgs-val').addEventListener('dblclick', function(ev){ ev.preventDefault(); gsSet(GSR.std); });
        }
        var v = gsLevel(), o = sl.querySelector('.nbgs-val'), t = v + ' %';
        if (o.textContent !== t) o.textContent = t;
        var tip = L('Size of the tools, the panel and its marks, independent of the zoom and the text size (stored per notebook)',
                    'Größe der Werkzeuge, des Panels und seiner Marken, unabhängig von Lupe und Schrift (je Notebook gemerkt)');
        if (sl.title !== tip) sl.title = tip;
        o.title = L('Reset to standard (100 %)', 'Auf Standard zurück (100 %)');
        sl.querySelector('.nbgs-minus').setAttribute('aria-label', L('Smaller controls', 'Kleinere Bedienelemente'));
        sl.querySelector('.nbgs-plus').setAttribute('aria-label', L('Larger controls', 'Größere Bedienelemente'));
      }
      // E22.1/E22.9: one look per pass for the source and the notebook id
      // (memo, 10-rail-host) — a full pass asked for them some forty times
      function sync(){
        var own = !window.__nbMemo;
        if (own) window.__nbMemo = {};
        try { return sync0.apply(this, arguments); } finally { if (own) window.__nbMemo = null; }
      }
      function sync0(){
        window.__nbrailBeat = Date.now();      // proof that this instance is alive
        window.__nbrailFullAt = Date.now();    // E21.5: when the last full pass ran …
        if (!window.__nbrailBeating) window.__nbrailEventAt = window.__nbrailFullAt;   // … and the last one an event asked for
        try { dcMark(); } catch (e) {}          // E8.23
        try { staleOff(); } catch (e) {}       // E25.h
        try { covSync(); } catch (e) {}         // E24.3
        try { modeField(); modeAfterRun(); } catch (e) {}   // R3 · 18
        try { coverPaint(); } catch (e) {}                  // E9.11
        try { seriesCover(); } catch (e) {}                 // E25.k
        try { acctCover(); } catch (e) {}                   // E17.3
        var host0 = document.getElementById(HOST_ID);
        sweep(host0);
        try { fbClean(); } catch (e) {}                     // E29 P5 (was E25.n)
        try { fsField(); fsApply(); } catch (e) {}          // E29 D7
        try { gsField(); gsApply(); } catch (e) {}          // E31 G1
        var host = document.getElementById(HOST_ID);
        var vp = visiblePanel();
        var key = panelKey(vp);

        // Switched notebook? Then the panel on screen belongs to the notebook you
        // just left. Empty it at once, so the notebook you switched TO either shows
        // its own panel or none — never the previous one's numbers.
        if (key !== window.__nbrailKey) {
          window.__nbrailKey  = key;
          window.__nbrailLast = null;
          window.__nbrailMiss = 0;
          if (host) {
            host.classList.remove('ready');
            host.removeAttribute('data-sig');
            host.removeAttribute('data-follow');
            // park the borrowed widgets before the panel is emptied — they belong
            // to the notebook we are leaving and must survive for its next visit
            var park = host.querySelectorAll('.nbslot > *');
            for (var pi = 0; pi < park.length; pi++) attic().appendChild(park[pi]);
            host.innerHTML = '';
          }
        }

        var src = activeSrc();
        if (!src) {
          // No source in the notebook on screen. Either its setup cell has not run
          // (→ no panel at all) or a cell is re-rendering right now, which empties
          // the DOM for a moment; a short grace period bridges the latter without
          // ever showing another notebook's panel.
          if (!window.__nbrailMiss) {
            window.__nbrailMiss = Date.now();
            // make the end of the grace period a real event: without this the
            // panel could stay on screen until the next tick happens to arrive
            clearTimeout(window.__nbrailGrace);
            window.__nbrailGrace = setTimeout(sync, 650);
          }
          if (host && (!window.__nbrailLast ||
                       Date.now() - window.__nbrailMiss > 600))
            host.classList.remove('ready');
          return;
        }
        window.__nbrailMiss = 0;
        if (!host) {
          host = document.createElement('div');
          host.id = HOST_ID; host.className = 'nbpanel-host';
          document.body.appendChild(host);
        }
        mountHost(host);
        if (frEnv() && host.style.getPropertyValue('display') !== 'none') host.style.setProperty('display', 'none', 'important');   // E25.b
        // the drawer needs a page before anything is clicked, or both of them
        // would be visible at once
        if (!host.dataset.page) host.dataset.page = 'code';
        var html = src.querySelector('.nbrail') ? src.innerHTML : '';
        if (html) window.__nbrailLast = html;
        if (host.getAttribute('data-sig') !== html) {
          patch(host, html);
          host.setAttribute('data-sig', html);
        }
        goNext(host, src);      // 27e — a right answer moves the reader on
        series(host, src);
        adopt(host, src);
        seriesList(host);
        gauge(host);
        // where you are READING wins over where the next exercise is; the wheel
        // over the timeline still parks it (data-manual) until the next scroll
        if (railLeads()) { pad(host); markCentre(host); }     // E22.9
        else followDoc(host);
        place(host, src);
        applyZoom(host, src);
        applyGui(host);
        applyTheme();           // follow the front end, unless the reader said otherwise
        applySkin();            // ...and the skin is the reader's alone
        applyRole();            // ...and so is what they are shown of the series
        unlockCell(src);        // and keep the output out of a fold JupyterLab offers
        ownCells(host, src);    // R2 · H3 — a mark for each cell of the reader's
        if (vertOn()) vertGauge(host, vertLayout(host, src));
        footAir(host);          // 27d — room under your own cell, every pass
        // LAST, after place() has given the rail its height: the marker is a
        // scrollbar thumb now, and its length is a share of that height. Drawn
        // before the rail was sized, it came out as long as the whole document.
        markCentre(host);
        keepTitleRendered(src);
        markTitleCell(src);
        placeCursor(host);
        // the notebook this panel belongs to — the one whose cover has done its
        // job. Marked here rather than on the body, so a second notebook open
        // beside it keeps its own Play button (2026-09-24bh).
        var own = src.closest ? (src.closest('.jp-NotebookPanel')
                              || src.closest('.jp-Notebook')) : null;
        if (own && !own.classList.contains('nbrail-own'))
          own.classList.add('nbrail-own');
        host.classList.add('ready');
        reserve(host, src);
        // reserve() changes the document's box, and the toolbar spans its width —
        // so the toolbar is placed once more, after the change...
        placeDock(host, src);
        // ...and then the rail once more after THAT, because the rail starts
        // under the toolbar and cannot know where that is until it is placed.
        // Two cheap passes beat one pass with a guess in it.
        place(host, src);
        markCentre(host);
        // 2026-09-24az — LAST of all. sync() re-runs the layout after
        // followDoc(), so a correction applied there is written over a moment
        // later — measured, the foot mark stayed 34px off in full screen
        // however often followDoc ran. It belongs at the end of the pass,
        // when nothing else is going to move it.
        footAlign(host);
      }

      // A newer panel already running in this page wins — do not take over.
      // This is the case the reader hits by opening an OLD copy of a notebook in
      // another tab: its kernel runs an older script, which used to tear down the
      // current one and put its own (stale) panel on screen.
      var liveV = String(window.__nbrailVersion || '');
      var liveB = window.__nbrailBeat || 0;
      if (liveV && vkey(liveV) >= vkey(NBRAIL_VERSION) && Date.now() - liveB < 6000) {
        try { window.__nbrailSync && window.__nbrailSync(); } catch (e) {}
        if (window.console) console.log('[DigiChemJN] panel ' + liveV +
            ' already running — this notebook (' + NBRAIL_VERSION + ') just feeds it');
        return;
      }

      window.__nbrailSync = sync;
      window.__nbrailFollow = follow;
      window.__nbrailGauge = gauge;
      window.__nbrailMeasure = measure;
      sync();
      function arm(){
      // ALWAYS re-arm. A previous run of an older version leaves its own observer
      // and interval behind, and those keep calling THEIR closure — so guarding
      // with a flag means a fixed version never takes over until the whole page is
      // reloaded. Tear the old one down first, then install this one.
      if (window.__nbrailTeardown) { try { window.__nbrailTeardown(); } catch (e) {} }
      window.__nbrailSync = sync;
      window.__nbrailFollow = follow;
      window.__nbrailGauge = gauge;
      window.__nbrailVersion = NBRAIL_VERSION;
      {
        var t = null;
        var kick = function(){ clearTimeout(t); t = setTimeout(sync, 60); };
        // 2026-10-03 (E21.5, Applikation) — OUR OWN BOOKKEEPING WAKES NO SYNC.
        // Two things the panel adds and takes away by itself were answered by
        // this observer with a second full sync 60 ms later: the invisible
        // probe of the mark floor (14, `.nbprobe`, appended and removed inside
        // a sync) and the 🔖 of the reading place (17, `.nbbm-ic`, set 2 s
        // after a scroll comes to rest). Measured v1.61 + E21, one CPU, after a
        // wheel scroll: 4 full syncs and 4 long tasks in the 3 s the reader
        // looks at a still panel (J5) — two of them answers to ourselves.
        // A change that only adds or removes such nodes is let through
        // without a sync; every other change kicks as before.
        var ownNode = function(n){ return n && n.nodeType === 1 && n.classList
          && (n.classList.contains('nbprobe') || n.classList.contains('nbbm-ic')); };
        // … and an accordion that opens or shuts (the title pill, a chapter,
        // a group) asks for a sync itself: ipywidgets only switches the
        // class `jupyter-widget-Collapse-open`, no node comes or goes, so the
        // childList watch never saw it, and the marks under a title opened
        // again waited for the 1.5-s beat (measured with the leaner beat
        // below: J1 "marks below 16 -> 0 -> 0" in 3 of 24 runner rows).
        var hostEl = null;
        // 2026-10-03 (E21.5c, Applikation) — ONLY OUR NOTEBOOK WAKES A SYNC.
        // The observer watches the whole page, and JupyterLab's own chrome
        // changes all the time: the file browser rewrites "x seconds ago" and
        // its rows' classes on every poll, a notebook BEHIND the front one runs
        // its kernel and redraws its toolbar. Measured in the gate's pair rows
        // (two notebooks open, 1 CPU, test J5): one file-browser poll (itself a
        // 234-ms long task of the Lab's) woke a full sync, which opened the
        // beat's 3.2-s window for two more — 4 long tasks in the 3 s the
        // reader looks at a still panel. None of it changes the panel. Now a
        // change counts if it is inside the notebook in front (or a notebook
        // panel that is not hidden), inside our host, or if it adds or takes
        // away a notebook panel; a page without any notebook panel (another
        // front end) keeps the old rule: every change counts.
        var pnlHid = function(n){ var p = n && n.closest ? n.closest('.jp-NotebookPanel') : null;
          return p ? (p.classList.contains('lm-mod-hidden') ? 2 : 1) : 0; };
        var hasPanel = function(ns){ for (var q = 0; q < ns.length; q++) { var x = ns[q];
            if (x.nodeType === 1 && (x.classList.contains('jp-NotebookPanel') || (x.querySelector && x.querySelector('.jp-NotebookPanel')))) return true; }
          return false; };
        var counts = function(r){
          var t = r.target.nodeType === 1 ? r.target : r.target.parentElement, w = pnlHid(t);
          if (w === 1) return true;                       // a notebook on screen
          if (w === 2) return false;                      // a notebook behind the front one
          if (!(hostEl && hostEl.isConnected)) hostEl = document.getElementById(HOST_ID);
          if (hostEl && hostEl.contains(t)) return true;  // our panel (borrowed controls)
          if (r.type === 'childList' && (hasPanel(r.addedNodes) || hasPanel(r.removedNodes))) return true;
          return !document.querySelector('.jp-NotebookPanel');   // no Lab around: as before
        };
        var mo = new MutationObserver(function(rs){
          for (var i = 0; i < rs.length; i++) {
            var r = rs[i], j, mine;
            if (!counts(r)) continue;                     // E21.5c
            if (r.type === 'attributes') {
              var tg = r.target;
              if (!(tg.classList && tg.classList.contains('jupyter-widget-Collapse'))) continue;
              // only a real open ↔ shut, never a class rewritten to itself
              // (that would let a sync wake the next one)
              if (/\bjupyter-widget-Collapse-open\b/.test(r.oldValue || '')
                  === tg.classList.contains('jupyter-widget-Collapse-open')) continue;
              if (!(hostEl && hostEl.isConnected)) hostEl = document.getElementById(HOST_ID);
              if (hostEl && hostEl.contains(tg)) continue;
              kick(); return;
            }
            mine = r.addedNodes.length + r.removedNodes.length > 0;
            for (j = 0; mine && j < r.addedNodes.length; j++) mine = ownNode(r.addedNodes[j]);
            for (j = 0; mine && j < r.removedNodes.length; j++) mine = ownNode(r.removedNodes[j]);
            if (!mine) { kick(); return; }
          }
        });
        mo.observe(document.body, {childList:true, subtree:true, attributes:true, attributeOldValue:true, attributeFilter:['class']});
        // 2026-10-03 (E21.1c, Applikation) — AN ACCORDION GETS TWO MORE LOOKS.
        // The sync 60 ms after an accordion opens can come before what is in
        // it has a box (Modeling, cyber dark, one CPU): its marks stay off the
        // rail. Until E21.5b the 1.5-s beat caught that; since then only a
        // beat inside the 3.2-s window does, 0–1.5 s later depending on its
        // phase — the gate's J1 looked 1.4 s after the click and saw marks
        // "16 -> 0 -> 0" in 2 of 24 rows. A real open or shut of an accordion
        // in a notebook on screen now also asks for a sync at 0.45 s and at
        // 1 s, whatever the beat's phase (the observer above gives the first).
        var tA = null, tB = null;
        // 2026-10-07 (E24 Stufe 2 Rest 2, JavaScript) — … AND THE BOX ITSELF
        // IS WATCHED UNTIL IT IS THERE. The looks at 0.06/0.45/1 s are guesses
        // at when the opened accordion has its box; in a loaded page (Tor
        // 07.10., pair row: two notebooks and their kernels, J1 "marks 17 → 0
        // → 0" with the title body back at 4085 px 1.4 s after the click) the
        // box came after the last look, and the marks waited for a beat. The
        // contents of the accordion that opened (or shut) are watched for 4 s
        // with a ResizeObserver: the moment their box changes, a sync in the
        // next task — on a timer of its own, not kick(): kick waits for 60 ms
        // of quiet, and the opened contents keep the page busy while they
        // draw (measured: the box at +67 ms, kick's sync only at +410 ms). Its
        // first answer (the size at observe) costs one sync more.
        var roAcc = null, roEnd = 0, roT = null, roS = null;
        var accLate = function(tg){
          if (!window.ResizeObserver) return;
          var ct = tg.querySelector(':scope > .jupyter-widget-Collapse-contents, :scope > .lm-Collapse-contents');
          if (!ct) return;
          if (!roAcc) roAcc = new ResizeObserver(function(){ if (Date.now() < roEnd && !roS) roS = setTimeout(function(){ roS = null; sync(); }, 0); });
          roEnd = Date.now() + 4000;
          try { roAcc.observe(ct); } catch (e) { return; }
          clearTimeout(roT);
          roT = setTimeout(function(){ try { roAcc.disconnect(); } catch (e) {} }, 4100);
        };
        var moAcc = new MutationObserver(function(rs){
          for (var i = 0; i < rs.length; i++) {
            var tg = rs[i].target;
            if (!(tg.classList && tg.classList.contains('jupyter-widget-Collapse'))) continue;
            if (/\bjupyter-widget-Collapse-open\b/.test(rs[i].oldValue || '')
                === tg.classList.contains('jupyter-widget-Collapse-open')) continue;
            var pn = tg.closest('.jp-NotebookPanel');
            if (!pn || pn.classList.contains('lm-mod-hidden')) continue;
            clearTimeout(tA); tA = setTimeout(sync, 450);
            clearTimeout(tB); tB = setTimeout(sync, 1000);
            accLate(tg);
            return;
          }
        });
        moAcc.observe(document.body, {subtree:true, attributes:true, attributeOldValue:true, attributeFilter:['class']});
        // a sidebar opening or the browser zooming changes the axis without any
        // DOM change and without a window resize event — watch the box itself
        // A width change has to be answered in the SAME frame, or the toolbar
        // hangs at its old size until the next sync — which is what it looked
        // like when the file browser was toggled. So the cheap placement runs
        // immediately and the full sync follows behind it.
        var refit = function(){
          var h = document.getElementById(HOST_ID), sx = activeSrc();
          if (h && sx && h.classList.contains('ready')) {
            // K4: half the notebook moved with the window — re-apply the width
            var hw0 = window.__nbWhalf;
            try { if (window.__nbApplyGui && (wHalf(h) !== hw0)) window.__nbApplyGui(h); } catch (e) {}
            try { placeDock(h, sx); place(h, sx); reserve(h, sx); markCentre(h); } catch (e) {}
          }
          kick();
        };
        var ro = null;
        if (window.ResizeObserver) {
          ro = new ResizeObserver(refit);
          document.querySelectorAll('.jp-NotebookPanel,.jp-Notebook,'
                                  + '.jp-WindowedPanel-outer,#main').forEach(function(el){
            try { ro.observe(el); } catch (e) {}
          });
          try { ro.observe(document.documentElement); } catch (e) {}
        }
        window.addEventListener('resize', refit, true);
        // The front end's theme can change without us: the Settings menu, a
        // system preference, another extension.
        //
        // 2026-09-25 — AND IT DOES NOT REACH INTO THE DOCUMENT ANY MORE.
        // This observer used to answer a front-end theme change with
        // `setThemePref('')` — it DELETED the reader's own choice, and
        // applyTheme() then fell back to whatever JupyterLab had just decided.
        // That is the whole of "the Jupyter theme still interferes with the
        // design settings": every switch in the Settings menu silently wiped
        // the notebook's own brightness. The line is gone. What stays is the
        // re-run of applyTheme(), because `nbforce-dark` / `nbforce-light` are
        // computed AGAINST the front end — they are how our choice paints over
        // JupyterLab's chrome, so they have to be recomputed when that chrome
        // changes. Our brightness is ours; the override that keeps the rest of
        // the window agreeing with it is what follows.
        var tmo = new MutationObserver(function(){
          if (document.body.getAttribute('data-jp-theme-light') !== window.__nbrailLight) {
            window.__nbrailLight = document.body.getAttribute('data-jp-theme-light');
            themeFade();
            applyTheme();
          }
        });
        window.__nbrailLight = document.body.getAttribute('data-jp-theme-light');
        tmo.observe(document.body, {attributes: true,
                    attributeFilter: ['data-jp-theme-light', 'data-jp-theme-name']});
        // Scrolling must NOT run sync(): sync re-diffs the whole panel, re-adopts
        // the widgets and re-measures the box — tens of milliseconds, every wheel
        // notch. That is what made the timeline lurch instead of glide: most
        // scroll events never got drawn. So a scroll does only the cheap part
        // (follow the reading position, redraw the marker), once per frame, and
        // the heavy sync is left to a trailing pause of 220 ms.
        var raf = 0, slow = null;
        var lightScroll = function(){
          if (raf) return;
          var run = function(){
            raf = 0;
            var h = document.getElementById(HOST_ID);
            if (!h || !h.classList.contains('ready')) return;
            if (railLeads()) { markCentre(h); return; }       // E22.9: only when the rail leads
            if (followedAlready(h)) return;                   // E22.6: done in the frame that moved it
            followDoc(h);
          };
          // NOT (window.requestAnimationFrame || setTimeout)(run): calling rAF
          // detached from window throws "Illegal invocation" in Chromium, and the
          // thrown error is swallowed by the scroll handler — the timeline simply
          // stops following.
          raf = window.requestAnimationFrame ? window.requestAnimationFrame(run)
                                             : setTimeout(run, 16);
        };
        // 2026-10-02 (E21.5, Applikation) — JUPYTERLAB'S SCROLL EVENTS THAT
        // MOVED NOTHING ASK FOR NO SYNC. The windowed notebook fires `scroll`
        // on its scroller at an unchanged scrollTop whenever a sync changed a
        // height in it (measured v1.61 at rest: 8 in 3 s, no setter called);
        // each one scheduled the next full sync 220 ms later, for ever. Such an
        // event still re-places the marker (cheap).
        var scrollAt = window.WeakMap ? new WeakMap() : null;
        var onScroll = function(ev){
          var t = ev && ev.target;
          var inMap = t && t.classList && t.classList.contains('nbmap');
          if (inMap) return;
          var still = false;
          if (scrollAt && t && t.classList && t.classList.contains('jp-WindowedPanel-outer')) {
            var pos = t.scrollTop + ',' + t.scrollLeft;
            still = scrollAt.get(t) === pos;
            scrollAt.set(t, pos);
          }
          var h = document.getElementById(HOST_ID);
          if (h) h.removeAttribute('data-manual');
          lightScroll();
          // while the timeline is driving, only the marker follows — pulling the
          // window back at the same time would make the two fight each other
          if (Date.now() - (window.__nbrailDriving || 0) < 500) return;
          if (still) return;                     // E21.5
          // E22.1: the pass after a scroll is the safety net of a scroll, not
          // an event that changed the panel — it does not open the beat's
          // 3.2-s window (two more full passes, 50–64 ms each on one CPU,
          // measured v1.63, in the seconds a reader has just stopped to
          // read). It stays one pass: things lay themselves out late after a
          // scroll (test_js: names at a new width, K4; a turn of the panel),
          // and with one look per follow (memo, 10-rail-host) it is shorter.
          clearTimeout(slow); slow = setTimeout(function(){
            window.__nbrailBeating = true;
            try { sync(); } finally { window.__nbrailBeating = false; }
          }, 220);
        };
        var onFull = function(){ sync(); setTimeout(sync, 80); setTimeout(sync, 400); };
        window.addEventListener('resize', kick);
        window.addEventListener('scroll', onScroll, true);
        document.addEventListener('fullscreenchange', onFull);
        document.addEventListener('webkitfullscreenchange', onFull);
        // 2026-10-03 (E21.5, Applikation) — THE HEARTBEAT LOOKS BEFORE IT
        // WORKS. Every 1.5 s a full sync ran whether anything had changed or
        // not; at rest it is the panel's whole load: measured v1.61 + E21 in
        // the container (one CPU), 50–67 ms each — two long tasks in every 3 s
        // a reader looks at a still panel, and one more from any event made it
        // four (J5 red in 2 of 12 runner rows). Every change of ours already
        // asks for its own sync (DOM, scroll, size, fullscreen, zoom, storage,
        // the Lab's theme); the beat is the safety net. It now still says
        // "alive" every 1.5 s (`__nbrailBeat`, the takeover check needs it
        // under 6 s) and runs the full pass only when the notebook in front or
        // its timeline source changed, the panel is not ready, the last full
        // pass is ≥ 6 s old — or an event asked for a sync in the last 3.2 s:
        // what that event set going (an accordion that opens, a widget that
        // draws late, a glide) settles over a second or two without telling
        // us, and the old beat used to catch it. So after every event the
        // beat works twice as before, and at rest it only looks.
        var beat = function(){
          window.__nbrailBeat = Date.now();
          var due = Date.now() - (window.__nbrailFullAt || 0) >= 5900
                 || Date.now() - (window.__nbrailEventAt || 0) < 3200;
          if (!due) {
            try {
              var h = document.getElementById(HOST_ID), vp = visiblePanel(), sx = activeSrc();
              var sig = sx && sx.querySelector('.nbrail') ? sx.innerHTML : '';
              due = !h || !sx || !h.classList.contains('ready') || panelKey(vp) !== window.__nbrailKey
                    || h.getAttribute('data-sig') !== sig;
            } catch (e) { due = true; }
          }
          if (due) { window.__nbrailBeating = true; try { sync(); } finally { window.__nbrailBeating = false; } }
        };
        var iv = setInterval(beat, 1500);
        // E8.23: a tab switch is a click or a key — the marks follow at once,
        // not on the next 1.5-s tick
        var dcKick = function(){ setTimeout(function(){ try { dcMark(); } catch (e) {} }, 30); };
        document.addEventListener('pointerup', dcKick, true);
        document.addEventListener('keyup', dcKick, true);
        window.__nbrailTeardown = function(){
          document.removeEventListener('pointerup', dcKick, true);
          document.removeEventListener('keyup', dcKick, true);
          mo.disconnect(); if (ro) ro.disconnect(); if (tmo) tmo.disconnect();
          clearInterval(iv); clearTimeout(t);
          clearTimeout(slow);
          moAcc.disconnect(); clearTimeout(tA); clearTimeout(tB);     // E21.1c
          window.removeEventListener('resize', kick);
          window.removeEventListener('resize', refit, true);
          window.removeEventListener('scroll', onScroll, true);
          document.removeEventListener('fullscreenchange', onFull);
          document.removeEventListener('webkitfullscreenchange', onFull);
          if (window.__nbrailClick)
            document.removeEventListener('click', window.__nbrailClick, true);
          if (window.__nbrailZoomDown)
            document.removeEventListener('pointerdown', window.__nbrailZoomDown, true);
        };
        // ---- the panel's controls -------------------------------------
        var FONTS = ['', 'nbfont-l', 'nbfont-xl'];
        window.__nbrailClick = function(ev){
          // Clicking a node in the timeline makes its lift STICK, so the chapter you
          // jumped to keeps its name raised and enlarged after the pointer leaves.
          // No preventDefault here — the jump handler still gets the same click.
          var nd = ev.target.closest && ev.target.closest('.nbmap-node');
          if (nd) {
            var hp = document.getElementById(HOST_ID);
            // 2026-09-24at — A CLICK NO LONGER FREEZES THE HOVER.
            // `nbpop` was the hover state made permanent: the mark a reader had
            // clicked kept the 45° turn and the marker's colour for as long as
            // nothing else was clicked. With the names off the rail (24al) the
            // lift has nothing left to reveal, and a mark stuck mid-rotation in
            // the pick colour reads as a state the notebook does not have. What
            // a click leaves behind is `nbsel` alone — the magenta fill, which
            // is the selection the unlock gesture needs and nothing more.
            if (hp) {
              var on = hp.querySelectorAll('.nbmap-node.nbpop');
              for (var z = 0; z < on.length; z++) on[z].classList.remove('nbpop');
            }
            if (hp) {
              window.__nbrailHerePin = Date.now();
              centreOn(hp, nd.offsetLeft + nd.offsetWidth / 2);
              markCentre(hp);
            }
          }
          // ▶ Run all cells lives on the COVER, not on the toolbar, so it has to
          // be matched before the .nbbtn gate below sends everything else away.
          var ra = ev.target.closest && ev.target.closest('.nbrunall');
          // 2026-10-05 (E22.3, Applikation) — PLAY IN A FOREIGN FRONT END SAYS
          // THE WAY. In PyCharm/DataSpell, VS Code and Colab our script sits in
          // an output frame: no JupyterLab app, no command to restart and run
          // (runAllCells finds none). Play then showed the loading view for a
          // blink and said "needs the notebook to have been started once" —
          // which it had been: that is how this script got here. Now it
          // shows no loading view and names the front end's own way at once
          // (nbRunPath, E19.4). Before the first run nothing of ours runs
          // there at all — that part is the cover's text (Python, E22.3).
          var envFr = false;
          try { envFr = /^(pycharm|vscode|colab)$/.test(nbEnv().env); } catch (e0) {}
          if (ra && envFr) {
            ev.preventDefault();
            if (frPlay(ra)) return;                                     // E25.e: the document
            var noteF = ra.parentNode ? ra.parentNode.querySelector('.nbrunall-msg') : null;
            if (!noteF && ra.parentNode) {
              noteF = document.createElement('div'); noteF.className = 'nbrunall-msg';
              noteF.style.cssText = 'margin:10px auto 0;max-width:560px;font-size:.85em;text-align:center';
              ra.parentNode.insertBefore(noteF, ra.nextSibling);
            }
            var deF = false; try { deF = langOf() === 'de'; } catch (e1) {}
            var nmF = {pycharm: 'PyCharm', vscode: 'VS Code', colab: 'Colab'}[nbEnv().env] || '';
            if (noteF) {
              noteF.textContent = deF
                ? 'In ' + nmF + ' kann dieser Knopf das Notebook nicht starten. So geht es: ' + nbRunPath(true) + '.'
                : 'In ' + nmF + ' this button cannot start the notebook. Do this instead: ' + nbRunPath() + '.';
              noteF.style.opacity = '1';
            }
            ra.setAttribute('data-nbplay', 'path');
            return;
          }
          // E24.3: Play on the output cover shows the document (no second run)
          if (ra && covPlay(ra)) { ev.preventDefault(); return; }
          if (ra) {
            ev.preventDefault();
            // E5.1: the loading view, the instant Play is pressed — BEFORE the
            // run, so JupyterLab's jump to the running cell happens under it
            var LV = window.__nbLoading;
            if (LV) { try { LV.show(ra, false); } catch (e) {} }
            // R3 · 18: the choice before Play reaches a live kernel first
            // (the ⚙ dropdown stores it); the restart waits for that
            // E21.6: … THIS cover's notebook (not the first ⚙ of the window);
            // a cold one gets the file its first run reads, and Play waits
            // for it (≤ 1.5 s)
            var told = false;
            try { told = window.__nbModeToKernel ? window.__nbModeToKernel(ra) : false; } catch (e) {}
            var later = function(){ if (!runAllCells() && LV) { try { LV.hide(); } catch (e) {} } };
            var ok = true;
            if (told && told.then) { var once = 0, go1 = function(){ if (!once++) later(); };
                                     told.then(go1, go1); setTimeout(go1, 1500); }
            else if (told) setTimeout(later, 700);
            else ok = runAllCells();
            if (!ok && LV) { try { LV.hide(); } catch (e) {} }
            var note = ra.parentNode
                     ? ra.parentNode.querySelector('.nbrunall-msg') : null;
            if (note) {
              note.textContent = ok
                ? 'Restarting the kernel and running every cell \u2014 this takes '
                  + 'a few seconds.'
                : 'This button needs the notebook to have been started once. '
                  + 'Use the menu: ' + nbRunPath() + '.';                  // E19.4
              note.style.opacity = '1';
              // AND IT SAYS SO IF NOTHING HAPPENS (2026-09-24s).
              // A button that reports success and then does nothing is worse
              // than one that does nothing: the reader waits. If the panel has
              // not come back in half a minute, the message stops claiming it
              // is working and names the menu path instead.
              if (ok) {
                clearTimeout(window.__nbrunWatch);
                window.__nbrunWatch = setTimeout(function(){
                  if (document.querySelector('#nbpanel-root .nbrail')) return;
                  note.textContent = 'That did not start it. Use the menu: '
                    + nbRunPath() + '.';                                       // E19.4
                }, 30000);
              }
            }
            return;
          }
          var t = ev.target.closest && ev.target.closest('.nbbtn');
          if (!t) return;
          ev.preventDefault();
          if (t.classList.contains('nbfull')) {           // ⛶ full screen
            if (document.fullscreenElement) { document.exitFullscreen(); return; }
            var src = activeSrc();
            var el = (src && src.closest('.jp-NotebookPanel')) || document.documentElement;
            if (el.requestFullscreen) el.requestFullscreen();
            return;
          }
          if (t.classList.contains('nbprofile')) {        // 👤 your progress code
            var hp2 = document.getElementById(HOST_ID);
            if (hp2) {
              var was2 = hp2.classList.contains('open') && hp2.dataset.page === 'code';
              hp2.dataset.page = 'code';
              hp2.classList.toggle('open', !was2);
              try { placeDock(hp2, activeSrc()); } catch (e) {}   // R3 · 17b: drawer at its widget now
              adopt(hp2, activeSrc()); seriesList(hp2);
              setTimeout(function(){
                var box = hp2.querySelector('.nbctl-code');
                if (box && box.scrollIntoView) box.scrollIntoView({block: 'nearest'});
                measure(hp2); gauge(hp2);
                reserve(hp2, activeSrc() || document.querySelector('.nbfeed'));
              }, 380);
            }
            return;
          }
          if (t.classList.contains('nbseries')) {         // 📚 the whole series
            var hp3 = document.getElementById(HOST_ID);
            if (hp3) {
              var wasS = hp3.classList.contains('open') && hp3.dataset.page === 'stats';
              hp3.dataset.page = 'stats';
              hp3.classList.toggle('open', !wasS);
              try { placeDock(hp3, activeSrc()); } catch (e) {}   // R3 · 17b: drawer at its widget now
              adopt(hp3, activeSrc()); seriesList(hp3);
              setTimeout(function(){ measure(hp3); gauge(hp3); }, 380);
            }
            return;
          }
          if (t.classList.contains('nbkeys')) {          // ⌨ the help window (R3 · 19)
            helpWin();
            return;
          }
          if (t.classList.contains('nbgear')) {           // ⚙ difficulty
            var host = document.getElementById(HOST_ID);
            if (host) {
              var wasD = host.classList.contains('open') && host.dataset.page === 'diff';
              host.dataset.page = 'diff';
              host.classList.toggle('open', !wasD);
              try { placeDock(host, activeSrc()); } catch (e) {}   // R3 · 17b: drawer at its widget now
              adopt(host, activeSrc()); seriesList(host);
              setTimeout(function(){ measure(host); gauge(host); reserve(host, activeSrc() ||
                         document.querySelector('.nbfeed')); }, 380);
            }
            return;
          }
          if (t.classList.contains('nbskin')) {           // 🎨 the style
            themeFade();
            nextSkin();
            return;
          }
          if (t.classList.contains('nbtheme')) {          // ◐ light / dark
            // 2026-09-24au — THE SWITCH READS THE DOCUMENT, NOT THE FRONT END.
            // `|| labDark()` made the button one-way under a dark JupyterLab:
            // the reader's light choice clears `nbdark`, but labDark() stays
            // true, so the next press computed "we are dark" and asked for
            // light again — measured, the document sat on nbforce-light and
            // never came back. `applyTheme()` writes `nbdark` for the effective
            // state, front end or reader whichever decided it, so that class
            // alone is the truth here.
            var dark = document.body.classList.contains('nbdark');
            // One switch for the whole window, one duration: the fade is armed
            // BEFORE anything changes, so the front end's surfaces and ours move
            // together instead of ours snapping while JupyterLab's glides.
            themeFade();
            var want = dark ? 'light' : 'dark';
            // The reader's choice is recorded first, so the document changes in
            // this frame whatever the front end does about it.
            setThemePref(want);
            applyTheme();
            // ...then ask the front end to come along. `commands.execute`
            // returns a PROMISE: it does not throw when the command is missing,
            // so silence must never be read as success. A moment later we LOOK:
            // if the front end moved, its theme is the truth and our override is
            // dropped again, so a later change from the Settings menu is not
            // fighting a stale class. That is exactly how the light mode was
            // lost — a class nothing ever took off.
            window.__nbthemeSelf = Date.now();   // this mutation is ours
            var app = window.jupyterapp || window.jupyterlab || null;
            if (app && app.commands && app.commands.execute) {
              var name = want === 'dark' ? 'JupyterLab Dark' : 'JupyterLab Light';
              try { app.commands.execute('apply-theme:' + name); } catch (e) {}
              // JupyterLab 4 takes the theme as an ARGUMENT, not as part of the id
              try { app.commands.execute('apply-theme', {theme: name}); } catch (e) {}
            }
            // No "look again in 420 ms". The reader's choice stands until the
            // reader changes it somewhere else; the front end coming along
            // afterwards lands on the colours that are already on screen, so
            // nothing moves twice.
            return;
          }
        };

        // The two sliders. One control each: drag it, wheel over it, or
        // double-click to put it back to 100%.
        if (window.__nbrailSlide)
          document.removeEventListener('input', window.__nbrailSlide, true);
        window.__nbrailSlide = function(ev){
          var t = ev.target;
          if (!t || !t.classList || !t.classList.contains('nbslider')) return;
          var host = document.getElementById(HOST_ID);
          if (!host || !host.contains(t)) return;
          if (t.classList.contains('nbgui-lab')) setGui(guiFlip(parseInt(t.value, 10)));
          else setZoom(zoomStore(parseInt(t.value, 10)));
        };
        document.addEventListener('input', window.__nbrailSlide, true);
        if (window.__nbrailSlideReset)
          document.removeEventListener('dblclick', window.__nbrailSlideReset, true);
        window.__nbrailSlideReset = function(ev){
          var t = ev.target;
          if (!t || !t.classList || !t.classList.contains('nbslider')) return;
          ev.preventDefault();
          if (t.classList.contains('nbgui-lab')) setGui(0); else setZoom(100);
          // 2026-09-28b — …and the thumb goes there too. slider() leaves a
          // focused thumb alone (it is being dragged), and a double click
          // leaves it focused: the lens read 100 %% with its thumb still at
          // the floor, and the next arrow key stepped from there (60 → 67 %%).
          t.value = String(t.classList.contains('nbgui-lab') ? guiFlip(0) : zoomSlide(100));
        };
        document.addEventListener('dblclick', window.__nbrailSlideReset, true);
        document.addEventListener('click', window.__nbrailClick, true);

        // 2026-09-28 (Paket 10, Applikation) — THE WHEEL FOLLOWS THE LENS.
        // With the document lens at 60 %% a notch of the wheel still moved the
        // scroller by the browser's ~100 screen pixels — which, at 60 %%, is
        // 166 pixels of the document: zoomed out, the text raced past; zoomed
        // in, it crawled. The reader asked for the opposite: zoomed out
        // slower, zoomed in faster. So over the document the wheel is taken
        // over whenever the lens is not at 100 %% and scaled by z² on screen,
        // which is z × the notch in DOCUMENT pixels (60 %% → 0.6 ×, 150 %%
        // → 1.5 ×). At 100 %% nothing changes, and anything under the pointer
        // that scrolls by itself in that direction (an editor, an output
        // area, a list) keeps its wheel, as do Ctrl, Shift and sideways.
        // 2026-09-28 (Eilauftrag E4.2, Applikation) — THE WHEEL GLIDES.
        // A notch used to be applied in one frame (or, at 100 %%, left to the
        // browser): the page jumped by a hundred pixels and stood still —
        // ruckig, in the reader's video. Dragging the cursor on the timeline
        // moves the document a little every frame, and that is the feel that
        // was asked for. So the wheel over the document is always taken over
        // now, also at 100 %%: each notch adds to a TARGET, and every frame the
        // scroller goes a fixed share of the way there (about 0.2 s to settle).
        // The tempo per lens stays (Paket 10): z² on screen, i.e. z × the notch
        // in document pixels. Anything that scrolls by itself under the pointer
        // keeps its wheel, as do Ctrl, Shift and sideways; a scroll that is not
        // ours (a jump, a landing, the scrollbar) drops what is left.
        // 2026-09-30 (E11.3, Applikation) — SMOOTHER, AND SLOWER ZOOMED IN.
        // Measured in the real JupyterLab (v1.39, one notch = 100): the glide
        // took a fixed 24 %% of what was left each frame, so the first frame
        // of a notch moved 24 px at 100 %%, 54 at 150 %%, 96 at 200 %% — and
        // five quick notches 35 / 72 / 144 px in ONE frame: the jerk in the
        // reader's video. And zoomed in the page went FASTER (z × the notch
        // in document pixels, Paket 10); the reader asked for the opposite.
        //  · tempo: a notch is d / z^1.5 DOCUMENT pixels (60 %% → 215,
        //    100 %% → 100, 150 %% → 54, 200 %% → 35), i.e. d / √z on screen
        //  · glide: time-based (τ = 110 ms, the same feel at any frame rate)
        //    and never more than GLIDE_MAX = 18 screen pixels in one frame;
        //    a long flick simply glides a little longer.
        var GLIDE_TAU = 110, GLIDE_MAX = 18, WHEEL_EXP = 1.5;
        function glide(t){
          var g = window.__nbGlide;
          window.__nbDocWheelRaf = 0;
          if (!g || !g.sc || !g.sc.isConnected) { window.__nbGlide = null; return; }
          var sc = g.sc;
          if (Math.abs(sc.scrollTop - g.set) > 2) { window.__nbGlide = null; return; }
          var max = Math.max(0, sc.scrollHeight - sc.clientHeight);
          g.to = Math.max(0, Math.min(g.to, max));
          var left = g.to - g.pos;
          if (Math.abs(left) < 0.5) {
            g.pos = g.to; sc.scrollTop = g.to; g.set = sc.scrollTop;
            window.__nbGlide = null;
            window.__nbFollowNow();                                // E22.6
            return;
          }
          var now = typeof t === 'number' ? t : performance.now();
          var dt = Math.max(4, Math.min(50, now - (g.t || now - 16)));
          g.t = now;
          var step = left * (1 - Math.exp(-dt / GLIDE_TAU));
          if (Math.abs(step) > GLIDE_MAX) step = left < 0 ? -GLIDE_MAX : GLIDE_MAX;
          if (Math.abs(step) < 0.5) step = left < 0 ? -0.5 : 0.5;
          if (Math.abs(step) > Math.abs(left)) step = left;
          g.pos += step;
          sc.scrollTop = g.pos;
          g.set = sc.scrollTop;
          window.__nbFollowNow();                                  // E22.6
          window.__nbDocWheelRaf = window.requestAnimationFrame(glide);
        }
        // 2026-10-12 (E29 D9, JavaScript) — THE WHEEL SPEEDS UP WITH THE HAND.
        // Reader 12.10.: turned slowly the wheel should stay as slow as it is,
        // turned fast it should go further per notch — above all zoomed in,
        // where one notch is a few lines ("man braucht Jahre"). A notch of a
        // wheel (lines, or a whole pixel step of ≥ 50) counts; the notches of
        // the last 0.35 s say how fast the hand turns: one alone → ×1, each
        // more adds 0.45 (× (1 + lens − 1) above 100 %), at most ×3.5 (×5 at
        // the lens ceiling). A touchpad sends small steps: never accelerated,
        // it glides as before. One direction only — a turn starts again at ×1.
        function wheelAcc(ev, d, z, zc){
          var notch = ev.deltaMode !== 0 || (Math.abs(ev.deltaY) >= 50 && Math.abs(ev.deltaY - Math.round(ev.deltaY)) < 0.01);
          var W = window.__nbWheelHand || (window.__nbWheelHand = {ts: [], dir: 0});
          if (!notch) { W.ts = []; return 1; }
          var now = window.performance ? performance.now() : Date.now(), dir = d > 0 ? 1 : -1;
          if (dir !== W.dir) { W.ts = []; W.dir = dir; }
          W.ts = W.ts.filter(function(t){ return now - t < 350; });
          W.ts.push(now);
          var up = Math.max(0, z - 1) / Math.max(0.01, zc - 1);           // 0 at 100 %%, 1 at the ceiling
          var k = 0.45 * (1 + Math.max(0, z - 1)), cap = 3.5 + 1.5 * Math.min(1, up);
          var a = Math.min(cap, 1 + k * (W.ts.length - 1));
          window.__nbWheelLast = a;                                      // for the test
          return a;
        }
        function docWheel(ev){
          if (ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.defaultPrevented) return;
          if (!ev.deltaY || Math.abs(ev.deltaX) > Math.abs(ev.deltaY)) return;
          var pct = zoomLevel();
          var t = ev.target;
          if (t && t.closest && t.closest('.nbcover-out[data-nbcov]')) return;   // E24.3: the cover scrolls itself
          var sc = t && t.closest ? t.closest('.jp-WindowedPanel-outer') : null;
          if (!sc || !sc.querySelector('.nbfeed')) return;
          var down = ev.deltaY > 0;
          for (var e = t; e && e !== sc; e = e.parentElement) {
            if (e.scrollHeight > e.clientHeight + 1) {
              var oy = getComputedStyle(e).overflowY;
              if ((oy === 'auto' || oy === 'scroll') &&
                  (down ? e.scrollTop + e.clientHeight < e.scrollHeight - 1
                        : e.scrollTop > 0)) return;
            }
          }
          var d = ev.deltaY;
          if (ev.deltaMode === 1) d *= 40;               // lines, not pixels
          else if (ev.deltaMode === 2) d *= sc.clientHeight;
          var z = pct / 100;
          ev.preventDefault();
          var g = window.__nbGlide;
          if (!g || g.sc !== sc || Math.abs(sc.scrollTop - g.set) > 2)
            g = window.__nbGlide = {sc: sc, pos: sc.scrollTop, to: sc.scrollTop,
                                    set: sc.scrollTop, t: 0};
          // a turn of direction starts from where the page IS, not from where
          // the last notch was still heading
          if ((d > 0) !== (g.to - g.pos > 0) && Math.abs(g.to - g.pos) > 0.5) g.to = g.pos;
          // E19.2 (Applikation): a little faster at both ends — ×1.25 at the
          // lens floor (60 %%), ×1.3 at its ceiling, 1 at 100 %%, linear in
          // between; more lens still means fewer document pixels per notch
          var zc = (window.__nbZCeil || 200) / 100,
              f = z < 1 ? 1 + 0.25 * Math.min(1, (1 - z) / 0.4) : 1 + 0.3 * Math.min(1, (z - 1) / Math.max(0.01, zc - 1));
          g.to += wheelAcc(ev, d, z, zc) * f * d / Math.pow(z, WHEEL_EXP - 1);   // E11.3: d / z^1.5 document px; E29 D9
          if (!window.__nbDocWheelRaf)
            window.__nbDocWheelRaf = window.requestAnimationFrame(glide);
        }
        // E29 P6: a cover laid over the notebook under the pointer (or the one in front)
        function covUpNow(t){
          var P = (t && t.closest ? t.closest('.jp-NotebookPanel') : null) || visiblePanel();
          if (t && t.closest && t.closest('.nbcover-out[data-nbcov]')) return true;
          return !!(P && P.querySelector('.nbcover-out[data-nbcov]'));
        }
        // inside the panel the wheel moves the timeline: down/right, up/left
        if (window.__nbrailWheel)
          document.removeEventListener('wheel', window.__nbrailWheel, {capture:true});
        window.__nbrailWheel = function(ev){
          // 2026-09-24t — CTRL+WHEEL IS NOT THE ZOOM HERE.
          // The browser's own page zoom scales the whole application including
          // the panel, fights the Doc control, and leaves the two disagreeing
          // about how big the document is. There is a control for this, it is
          // on the toolbar, and it is the one the notebook is measured against.
          // 2026-10-12 (E29 P6, JavaScript) — ON THE PREVIEW NO LENS AT ALL.
          // Ctrl+wheel over the cover set the document's lens under it (and
          // the cover took it off itself again, J24.3a): the reader saw the
          // page "buggen" (12.10.). While a cover is laid over the notebook in
          // front, the wheel and Ctrl +/−/0 are the browser's own — no
          // preventDefault, no setZoom, no glide (docWheel stays out as well).
          if (covUpNow(ev.target)) return;
          if (ev.ctrlKey || ev.metaKey) {
            var nbp = ev.target.closest
                    ? ev.target.closest('.jp-NotebookPanel') : null;
            if (nbp && nbp.getAttribute('data-digichem') !== '1') nbp = null;   // E8.23
            var hst = document.getElementById(HOST_ID);
            if (nbp || (hst && hst.contains(ev.target))) {
              ev.preventDefault();
              // …and it does the sensible thing instead
              setZoom(zoomLevel() + (ev.deltaY < 0 ? 5 : -5));
              return;
            }
          }
          var host = document.getElementById(HOST_ID);
          if (!host || !host.contains(ev.target)) { docWheel(ev); return; }
          // only over the timeline — over the buttons or the open drawer the wheel
          // belongs to the page (or to the control under the pointer)
          var grp = ev.target.closest ? ev.target.closest('.nbzoomgrp') : null;
          if (grp) {
            var dz = (ev.deltaY < 0 ? 5 : -5);
            ev.preventDefault();
            if (grp.classList.contains('nbz-gui')) setGui(guiLevel() - dz);
            else setZoom(zoomLevel() + dz);
            return;
          }
          var map = ev.target.closest ? ev.target.closest('.nbmap') : null;
          if (!map || !host.contains(map)) return;
          var d = Math.abs(ev.deltaY) > Math.abs(ev.deltaX) ? ev.deltaY : ev.deltaX;
          if (ev.deltaMode === 1) d *= 16;          // lines, not pixels
          else if (ev.deltaMode === 2) d *= map.clientWidth;
          if (!d) return;
          ev.preventDefault();
          if (vertOn()) {
            var scw = scroller(host);
            if (window.__nbLandStop) { try { window.__nbLandStop(); } catch (e) {} }   // E8.5
            // (no moving() here: the reader scrolls the rail to bring a mark
            // under the pointer and clicks it — the marks keep the pointer)
            if (scw) { window.__nbrailDriving = Date.now(); scw.scrollTop += d; }
            return;
          }
          // Apply the wheel ONCE PER FRAME, not once per event: a trackpad
          // sends a dozen small deltas per frame, and setting scrollLeft on
          // each one made the rail stutter instead of glide. The document is
          // pulled along afterwards, on a longer pause, so a flick moves the
          // timeline immediately and the page only once the flick is over.
          window.__nbrailWheelAcc = (window.__nbrailWheelAcc || 0) + d;
          if (!window.__nbrailWheelRaf) {
            window.__nbrailWheelRaf = window.requestAnimationFrame(function(){
              window.__nbrailWheelRaf = 0;
              var acc = window.__nbrailWheelAcc || 0;
              window.__nbrailWheelAcc = 0;
              if (!acc) return;
              window.__nbrailSelfScroll = true;
              window.__nbrailSelfAt = Date.now();
              map.scrollLeft += acc;
              // the map's own scroll handler is skipped (this scroll is ours),
              // so the two things it would have done are done here
              host.setAttribute('data-manual', '1');
              markCentre(host);
            });
          }
          clearTimeout(window.__nbrailScrubT);
          window.__nbrailScrubT = setTimeout(function(){ scrubTo(host); }, 110);
        };
        document.addEventListener('wheel', window.__nbrailWheel, {capture:true, passive:false});
        // Ctrl/Cmd + plus / minus / zero is the same page zoom by another route.
        // Chrome lets the page refuse it; the browser's own menu cannot be
        // refused, and is not worth pretending otherwise about.
        if (window.__nbrailZoomKeys)
          document.removeEventListener('keydown', window.__nbrailZoomKeys, true);
        window.__nbrailZoomKeys = function(ev){
          if (!(ev.ctrlKey || ev.metaKey) || ev.altKey) return;
          var k = ev.key;
          if (k !== '+' && k !== '-' && k !== '=' && k !== '0'
              && k !== 'Add' && k !== 'Subtract') return;
          var nbp = ev.target && ev.target.closest
                  ? ev.target.closest('.jp-NotebookPanel') : null;
          // E8.23: only in our notebook — anywhere else Ctrl +/−/0 is the browser's
          var cur0 = nbp || (window.__nbFront && window.__nbFront());   // E21.1
          if (!cur0 || cur0.getAttribute('data-digichem') !== '1') return;
          if (covUpNow(ev.target)) return;                                // E29 P6
          ev.preventDefault();
          if (k === '0') setZoom(100);
          else setZoom(zoomLevel() + (k === '-' || k === 'Subtract' ? -5 : 5));
        };
        document.addEventListener('keydown', window.__nbrailZoomKeys, true);

        // Dragging the reading marker scrolls the document — it replaced the
        // rail's scrollbar, so it has to do a scrollbar's work. The rail is 1:1
        // with the document, so a pixel moved here is a pixel scrolled there.
        if (window.__nbrailMarkDown)
          document.removeEventListener('pointerdown', window.__nbrailMarkDown, true);
        window.__nbrailMarkDown = function(ev){
          var t = ev.target;
          // 2026-09-24bg — the cursor beside the lane grabs the same way the
          // marker does. One handler, because it is one gesture: whichever of
          // the two the reader took hold of, the document scrolls by the same
          // thumb arithmetic.
          if (!t || !t.classList ||
              !(t.classList.contains('nbmap-here') ||
                t.classList.contains('nbmap-cursor'))) return;
          if (!vertOn() || ev.button) return;
          var host = document.getElementById(HOST_ID);
          var sc = host && scroller(host);
          if (!sc) return;
          ev.preventDefault();
          // E8.5: the hand takes over — no landing or glide pulls against it
          if (window.__nbLandStop) { try { window.__nbLandStop(); } catch (e) {} }
          document.body.classList.add('nbscrubbing');
          var y0 = ev.clientY, top0 = sc.scrollTop, z = pageZoom();
          // A thumb's travel is the TRACK's, not the document's. One pixel of
          // mouse for one pixel of document meant dragging six thousand pixels
          // to cross a six-thousand-pixel notebook — the rail is 1:1 with the
          // document, but only eight hundred pixels of it are on screen. The
          // ratio below is the usual scrollbar one: the length of the thumb's
          // run maps onto the whole of the document's.
          var map0 = host.querySelector('.nbmap');
          var mk0 = host.querySelector('.nbmap-here');
          var trav = map0 && mk0
                   ? Math.max(1, map0.clientHeight - mk0.offsetHeight) : 1;
          // E12.3: the thumb runs its own track (placeCursor), a plain bar
          if (t.classList.contains('nbmap-cursor') && host.__nbSbTrav) trav = host.__nbSbTrav;
          var span = Math.max(1, sc.scrollHeight - sc.clientHeight);
          if (t.classList.contains('nbmap-cursor') && host.__nbSbTrav)
            span = Math.max(1, span - Math.max(0, window.__nbTopAt || 0));
          var ratio = span / trav;
          t.classList.add('dragging');
          t.classList.add('nbdragging');
          try { t.setPointerCapture(ev.pointerId); } catch (e) {}
          // One scroll per FRAME, not per pointer event: a trackpad or a
          // high-rate mouse sends several moves per frame, and setting scrollTop
          // on each of them made the drag stutter exactly like the wheel used to.
          var pend = null, raf = 0;
          var apply = function(){
            raf = 0;
            if (pend === null) return;
            window.__nbrailDriving = Date.now();
            moving();                                         // E22.9
            window.__nbGlide = null; window.__nbLandMove = null;
            sc.scrollTop = Math.max(0, Math.min(span,
                                top0 + ((pend - y0) / z) * ratio));
            pend = null;
            // E22.9: this runs IN a frame callback — the page's scroll event
            // comes a frame later, so the rail is put to the page here, or
            // every frame the thumb moved drew the marks one step behind
            // (measured: 37 px off their pills in one frame of three)
            window.__nbFollowNow();
          };
          var move = function(e){
            pend = e.clientY;
            if (!raf) raf = window.requestAnimationFrame ?
                window.requestAnimationFrame(apply) : setTimeout(apply, 16);
          };
          var up = function(){
            if (raf && window.cancelAnimationFrame) cancelAnimationFrame(raf);
            raf = 0; apply();
            t.removeEventListener('pointermove', move);
            t.removeEventListener('pointerup', up);
            t.removeEventListener('pointercancel', up);
            t.classList.remove('dragging');
            t.classList.remove('nbdragging');
            document.body.classList.remove('nbscrubbing');
            try { t.releasePointerCapture(ev.pointerId); } catch (e) {}
          };
          t.addEventListener('pointermove', move);
          t.addEventListener('pointerup', up);
          t.addEventListener('pointercancel', up);
        };
        document.addEventListener('pointerdown', window.__nbrailMarkDown, true);

        // A range input handles its own dragging, so the hand-rolled pointer
        // capture that used to move the old label is gone; only the teardown of
        // an older build's listener is kept.
        if (window.__nbrailZoomDown) {
          document.removeEventListener('pointerdown', window.__nbrailZoomDown, true);
          window.__nbrailZoomDown = null;
        }

        // dragging the scrollbar, a swipe or the keyboard: same rule as the wheel
        if (window.__nbrailMapScroll)
          document.removeEventListener('scroll', window.__nbrailMapScroll, {capture:true});
        window.__nbrailMapScroll = function(ev){
          var t = ev.target;
          if (!t || !t.classList || !t.classList.contains('nbmap')) return;
          var host = document.getElementById(HOST_ID);
          if (!host) return;
          markCentre(host);                         // welded to the window centre
          if (window.__nbrailSelfScroll &&
              Date.now() - (window.__nbrailSelfAt || 0) < 200) return;   // ours
          window.__nbrailSelfScroll = false;
          window.__nbMapLeadAt = Date.now();        // E22.9: the reader moved the rail itself
          // the timeline IS a scrubber: moving it moves the document, which moves
          // the window back — one position, reachable from either side
          clearTimeout(window.__nbrailScrubT);
          window.__nbrailScrubT = setTimeout(function(){ scrubTo(host); }, 40);
        };
        document.addEventListener('scroll', window.__nbrailMapScroll, {capture:true});
      }
      sync();
      }

      arm();
      // The watchdog is deliberately NOT part of the teardown: an older script from
      // another tab tears everything else down, and this is what brings the current
      // panel back a moment later. It retires by itself as soon as a newer version
      // announces one.
      window.__nbrailGuardV = NBRAIL_VERSION;
      if (!window.__nbrailGuard) {
        window.__nbrailGuard = setInterval(function(){
          if (vkey(window.__nbrailGuardV || '') > vkey(NBRAIL_VERSION)) {
            clearInterval(window.__nbrailGuard); window.__nbrailGuard = 0; return;
          }
          var v = String(window.__nbrailVersion || '');
          var beat = window.__nbrailBeat || 0;
          if (vkey(v) < vkey(NBRAIL_VERSION) || Date.now() - beat > 4000) arm();
        }, 2000);
      }
      document.body.classList.add('nbrail-live');
      if (window.console) console.log('[DigiChemJN] progress panel ' + NBRAIL_VERSION + ' armed');
    })();
    // 2026-10-13 (E33 C1, Werkstatt JS) — LAB TAKES THE WINDOW'S TWO LINES (Nutzer: „finde ich gut“). The
    // reading window (20-reader) has the progress bar at the TOP of its panel and the current chapter's name at
    // its FOOT; Lab/Lite get the same: `.nbp-xp` (> `.nbp-xp-t` „Progress s / n“ + `.nbp-xp-bar` >
    // `.nbp-xp-fill`) as the first child of `.nbrail`, `.nbp-cur` (the chapter the reading height stands
    // in, else its part or the title) as the last. Counted from the panel's own pips (`i.ps[data-kind][data-st]`
    // of the chapter marks) and the mode of the run (`.nbfeed[data-nbmode]`): what the mode leaves out does not
    // count. Look: CSS (inline here only what keeps them on the panel's edges).
    (function nbRailC1(){
      if (!document.querySelector('.jp-NotebookPanel, .jp-Notebook, #notebook')) return;
      if (window.__nbC1T) clearInterval(window.__nbC1T);
      function c1(){
        var h = document.getElementById('nbpanel-root'), rail = h && h.querySelector('.nbrail');
        if (!rail) return;
        var xp = rail.querySelector(':scope>.nbp-xp'), cur = rail.querySelector(':scope>.nbp-cur');
        if (!xp) {
          xp = document.createElement('div'); xp.className = 'nbp-xp'; xp.setAttribute('aria-hidden', 'true');
          xp.innerHTML = '<span class="nbp-xp-t"></span><span class="nbp-xp-bar"><span class="nbp-xp-fill"></span></span>';
          xp.style.cssText = 'position:absolute;left:8px;right:8px;top:2px;z-index:6;pointer-events:none;display:flex;flex-direction:column;gap:2px;font:600 11px/1.2 system-ui,sans-serif';
          xp.lastChild.style.cssText = 'display:block;height:5px;border-radius:3px;overflow:hidden;background:rgba(120,132,145,.3)';
          xp.lastChild.firstChild.style.cssText = 'display:block;height:100%;width:0;background:#2f8f5f';
          rail.insertBefore(xp, rail.firstChild);
        }
        if (!cur) {
          cur = document.createElement('div'); cur.className = 'nbp-cur'; cur.setAttribute('role', 'status');
          cur.style.cssText = 'position:absolute;left:6px;right:6px;bottom:2px;z-index:6;pointer-events:none;text-align:center;overflow:hidden;'
            + 'text-overflow:ellipsis;white-space:nowrap;font:700 11px/1.3 system-ui,sans-serif';
          rail.appendChild(cur);
        }
        var de = window.__nbAcct ? window.__nbAcct.lang() === 'de' : /^de/.test(document.documentElement.lang || '');
        var P = rail.closest('.jp-NotebookPanel') || document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)') || document;
        var fd = P.querySelector('.nbfeed[data-nbmode]') || document.querySelector('.nbfeed[data-nbmode]');
        var md = (fd && fd.getAttribute('data-nbmode')) || 'both', n = 0, s = 0;
        [].forEach.call(rail.querySelectorAll('.nbmap-node.chap i.ps[data-kind]'), function(p){
          var k = p.getAttribute('data-kind');
          if (md === 'plain' || (md === 'calc' && k === 'code') || (md === 'code' && k === 'calc')) return;
          n++; if (p.getAttribute('data-st') === 'solved') s++;
        });
        var t = (de ? 'Fortschritt ' : 'Progress ') + s + ' / ' + n;
        if (xp.firstChild.textContent !== t) xp.firstChild.textContent = t;
        xp.lastChild.firstChild.style.width = (n ? (100 * s / n).toFixed(1) : '0') + '%%';
        xp.style.display = n ? 'flex' : 'none';
        xp.setAttribute('data-n', String(n)); xp.setAttribute('data-solved', String(s));
        var ns = [].slice.call(rail.querySelectorAll('.nbmap-node')), i = ns.indexOf(rail.querySelector('.nbmap-node.here')), nm = '';
        for (var j = i; j >= 0 && !nm; j--) {
          var x = ns[j];
          if (x.classList.contains('nbgone') && !x.classList.contains('chap')) continue;
          if (x.classList.contains('chap') || x.classList.contains('sect') || x.classList.contains('title')) {
            var l = x.querySelector('.nbmap-lab'); nm = ((l && l.textContent) || x.getAttribute('title') || x.textContent || '').replace(/\s+/g, ' ').trim();
          }
        }
        if (!nm) nm = de ? 'Anfang' : 'Start';
        if (cur.textContent !== nm) { cur.textContent = nm; cur.title = nm; }
        // shut (the line alone) the bar stays, the words go (as the window's shut panel)
        var nar = rail.clientWidth < 90;
        xp.firstChild.style.display = nar ? 'none' : ''; cur.style.display = nar ? 'none' : '';
        rail.setAttribute('data-nbc1', nar ? 'shut' : 'open');
      }
      window.__nbC1 = c1;
      window.__nbC1T = setInterval(function(){ try { c1(); } catch (e) {} }, 400);
      try { c1(); } catch (e) {}
    })();
