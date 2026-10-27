      // 2026-09-24bf — THE GRIP'S GESTURE.
      // Delegated from the document, because the panel is rebuilt out of its
      // own HTML on every progress change and a handler bound to the element
      // would be thrown away with it.
      // The arithmetic is the inverse of applyGui, and it has to STAY the
      // inverse: the edge follows the pointer exactly — drag it 60px to the
      // left and the panel is 60px wider. No acceleration, nothing to learn.
      // 2026-09-25d: the range is 16px to 560px now, so one percent is 5.44px.
      // Derived from the same two numbers applyGui uses, not typed twice.
      // 2026-09-27b — the narrow end is no longer a typed 16: the marks set it
      // (markFloor), so one percent is measured against that same number.
      function GPX(){ return (560 - (window.__nbWmin || 16)) / 100; }
      // 2026-09-30 (E9.1, Struktur + Applikation) — THE READING HEIGHT AS ONE
      // UNIT. Marker, scroll-bar cursor, fold knob (.nbgrip) and the fixed
      // point in the document stand on one line. The line is the title
      // mark's height (railY0n, 11-layout) plus RLKEY, the offset the reader
      // dragged the knob by — stored, so it survives a reload. rlLine keeps
      // it inside the rail's window.
      var RLKEY = 'digichemjn.readline.v1';
      // E16.10 (Struktur): the reading height is the notebook's own — its key
      // carries the id (`.<id>`); the old shared value is taken over once
      function rlKey(){ return idKey(RLKEY); }
      function rlOff(){
        var v = 0;
        try { v = parseInt(localStorage.getItem(rlKey()) || '0', 10) || 0; } catch (e) {}
        return v;
      }
      function rlLine(host, y){
        var map = host && host.querySelector('.nbmap');
        var ch = map ? map.clientHeight : 0;
        // E15.6: not below 70 %% of the rail's window. Lower, the knob sat
        // under JupyterLab's toasts (bottom right, z-index 9999, measured
        // 1400 × 900: 777–887 px) and could not be taken hold of again.
        if (ch > 80) y = Math.max(24, Math.min(Math.round(ch * .7), y));
        return Math.round(y);
      }
      window.__nbRlOff = rlOff;
      // 2026-09-30 (E11.4, Struktur + Applikation) — DRAGGING THE READING
      // HEIGHT WORKS IN EVERY WINDOW, AND THE DOCUMENT GOES WITH IT.
      // Two faults, both measured in the real JupyterLab:
      //  1. The gesture was armed ONCE per window (`__nbGripArmed`), with the
      //     closure of whichever notebook ran first. A window in which an
      //     older build had run (before E9.1: sideways only) kept that
      //     handler for good — up and down did nothing. It is now handed over
      //     like every other handler (version compare with vkey, newer or
      //     equal replaces), and it listens on WINDOW in the capture phase:
      //     it runs before any old, unremovable handler on the document and
      //     stops the event there, so an old build cannot answer it too.
      //  2. The document did not stay with the line. The move set
      //     `scrollTop = st0 − dy`, but the air over the title follows the
      //     line (headAir: the title must reach it), and headAir scrolled
      //     the page by the air's growth afterwards — measured +50 px per
      //     25-px step, the page jumped back and forth (1475 ↔ 1525) and
      //     ended 24–50 px off. Now the POINT of the document on the line
      //     when the drag starts (without the air) is held: the air is
      //     brought up to date first, then scrollTop = point + air − line.
      //     The rail's answering scroll is marked as ours, so the scrubber
      //     does not pull the page back.
      function onGripDown(ev){
          var g = ev.target && ev.target.closest
                ? ev.target.closest('.nbgrip') : null;
          if (!g || ev.button) return;
          ev.preventDefault(); ev.stopPropagation();
          var x0 = ev.clientX, p0 = guiLevel(), moved = 0;
          // E9.1: the first 4 px decide the axis — sideways is the panel's
          // width (as before), up and down is the reading height
          // E15.6: o0 is the offset ON SCREEN (line − title height), not the
          // stored one: a stored offset past the rail's window (smaller
          // window, other title height) was clamped on screen but not here,
          // so the first few hundred px of a drag moved nothing — the line
          // "sat fast" until the pointer had made up the difference.
          var y0 = ev.clientY, axis = null;
          var hostG = document.getElementById(HOST_ID);
          var scG = hostG ? scroller(hostG) : null, st0 = scG ? scG.scrollTop : 0;
          var n0 = hostG ? (parseInt(hostG.dataset.railY0n || '0', 10) || 0) : 0;
          var o0 = hostG && hostG.dataset.railY0 ? parseInt(hostG.dataset.railY0, 10) - n0 : rlOff();
          var airOf = function(){
            var a = scG && scG.querySelector(':scope > .nbhead-air');
            return a ? (parseFloat(a.style.height) || 0) : 0;
          };
          var lineOf = function(L){
            var mp = hostG.querySelector('.nbmap');
            return (mp ? mp.getBoundingClientRect().top : 0) + L
                 - (scG ? scG.getBoundingClientRect().top : 0);
          };
          // the document point on the line, in pixels of the content
          var P0 = (scG && hostG) ? st0 - airOf() + lineOf(n0 + o0) : 0;
          var raf = 0;
          g.classList.add('nbdragging');
          // E15.6: the drag ends however the button comes up — over an
          // iframe, outside the window, on a lost capture, on blur. Before,
          // only a pointerup that reached this document ended it.
          try { g.setPointerCapture(ev.pointerId); } catch (e) {}
          var lineTo = function(L){
            L = rlLine(hostG, L);
            try { localStorage.setItem(rlKey(), String(L - n0)); } catch (e2) {}
            hostG.dataset.railY0 = String(L);
            if (scG) {
              window.__nbrailSelfScroll = true;
              window.__nbrailSelfAt = Date.now();
              window.__nbrailDriving = Date.now();
              if (window.__nbLandStop) { try { window.__nbLandStop(); } catch (e4) {} }
              try { headAir(hostG); } catch (e5) {}
              scG.scrollTop = Math.max(0, Math.round(P0 + airOf() - lineOf(L)));
            }
            if (!raf) raf = requestAnimationFrame(function(){
              raf = 0;
              try { markCentre(hostG); } catch (e3) {}
            });
          };
          var move = function(e){
            if (!e.buttons) return up();
            var dx = x0 - e.clientX;                 // to the LEFT is bigger
            var dy = e.clientY - y0;
            if (Math.max(Math.abs(dx), Math.abs(dy)) > moved)
              moved = Math.max(Math.abs(dx), Math.abs(dy));
            if (!axis && moved > 4) {
              axis = Math.abs(dy) > Math.abs(dx) ? 'y' : 'x';
              if (axis === 'y' && hostG) hostG.classList.add('nbread-drag');
            }
            if (axis) moving();                      // E22.9
            if (axis === 'x') setGui(Math.round(p0 + dx / GPX()));
            // the line follows the pointer; what stood on it goes with it
            else if (axis === 'y' && hostG && n0 > 0) lineTo(n0 + o0 + dy);
          };
          var done = 0;
          var up = function(){
            if (done++) return;
            document.removeEventListener('pointermove', move, true);
            document.removeEventListener('pointerup', up, true);
            document.removeEventListener('pointercancel', up, true);
            g.removeEventListener('lostpointercapture', up);
            window.removeEventListener('blur', up);
            g.classList.remove('nbdragging');
            if (hostG) hostG.classList.remove('nbread-drag');
            // A CLICK IS NOT A DEAD BUTTON. It looks like one thing to press,
            // so pressing it does the obvious thing: jump to the other end.
            // E15.6: it waits 260 ms for a second click — a DOUBLE click puts
            // the reading height back to its start (the title mark's height)
            // and leaves the panel alone. (Toggling at once moved the knob
            // away from under the pointer before the second click came.)
            if (moved < 3) {
              if (window.__nbGripT) {
                clearTimeout(window.__nbGripT); window.__nbGripT = 0;
                if (hostG && n0 > 0) lineTo(n0);
              } else window.__nbGripT = setTimeout(function(){
                window.__nbGripT = 0; setGui(guiLevel() > 50 ? 0 : 100);
              }, 260);
            }
            else if (axis === 'y' && hostG && window.__nbrailSync) {
              window.__nbrailSelfScroll = true;
              window.__nbrailSelfAt = Date.now();
              window.__nbrailSync();
            }
          };
          document.addEventListener('pointermove', move, true);
          document.addEventListener('pointerup', up, true);
          document.addEventListener('pointercancel', up, true);
          g.addEventListener('lostpointercapture', up);
          window.addEventListener('blur', up);
      }
      if (!window.__nbGripV || vkey(window.__nbGripV) <= vkey(NBRAIL_VERSION)) {
        if (window.__nbGripHandler)
          window.removeEventListener('pointerdown', window.__nbGripHandler, true);
        window.__nbGripHandler = onGripDown;
        window.__nbGripV = NBRAIL_VERSION;
        window.__nbGripArmed = true;       // an older build then arms nothing
        window.addEventListener('pointerdown', onGripDown, true);
      }
      // The ladder. Each step is a threshold on the same number, so the control
      // has one meaning in both orientations: how much panel there is.
      var DETAIL = [['det-text', .85], ['det-emoji', .70], ['det-circle', .58],
                    ['det-bar', .46], ['det-dot', .36]];
      // 2026-09-24r — THE CONTROL'S RANGE.
      // Everything below half was a rail nobody used: at a third of the size
      // the marks are smaller than the line they sit on. So what used to be 50 %
      // is the new 0 %, and the control runs from there to full size.
      var GFLOOR = 0.5;
      function guiT(pct){ return GFLOOR + (1 - GFLOOR) * (pct / 100); }
      // 2026-09-24x — THE MARKS ARE NOT THE PANEL.
      // One number used to set both: at 0 %% the panel was half as wide AND the
      // marks were half as big, which put them three rungs down the ladder —
      // names gone, emoji gone, exercise circles gone. A narrow panel is a
      // request for less WIDTH, not for a rail you cannot read. The marks now
      // have their own floor and stay nearly full size at every setting; only
      // the names, which genuinely do not fit in 150 px, still go.
      var MFLOOR = 0.82;
      function markT(pct){ return MFLOOR + (1 - MFLOOR) * (pct / 100); }
      // 2026-09-27b — THE MARK SETS THE PANEL'S NARROW END, NOT THE OTHER WAY
      // ROUND (STRUKTUR §4a, Vorhaben E). Shut, the panel was 16px and the marks
      // were scaled to fit it: 0.148 of full size, 4px squares, and the detail
      // ladder faded 14 of 15 of them out — "practically gone" (measured 27a,
      // and in the reader's video). Now the smallest mark is at least
      // MARK_MIN_PX, and the panel is as wide as the widest mark at that scale
      // needs, plus 2px. Both numbers are MEASURED from the marks this notebook
      // really draws in the skin that is really on: one clone of each kind of
      // node, laid out invisibly at a given --nbthick, read, and removed. No
      // mark size is typed here, so a skin that changes a shape changes the
      // floor with it.
      var MARK_MIN_PX = 10;
      var MARK_SEL = '.nbsect,.nbchapdot,.nbsubdot,.nbrail-dot,.nbvizmark,.nbcodemark';
      function markProbe(host, t){
        var inner = host.querySelector('.nbmap-inner');
        if (!inner) return null;
        var box = document.createElement('div');
        box.className = 'nbprobe';
        box.setAttribute('aria-hidden', 'true');
        box.style.cssText = 'position:absolute;left:0;top:0;width:100%;height:0;'
                          + 'visibility:hidden;pointer-events:none;--nbthick:' + t;
        var seen = {};
        inner.querySelectorAll(':scope > .nbmap-node').forEach(function(n){
          if (n.classList.contains('nbgone')) return;
          if (seen[n.className]) return;
          seen[n.className] = 1;
          var c = n.cloneNode(true);
          c.removeAttribute('id');
          c.querySelectorAll('[id]').forEach(function(e){ e.removeAttribute('id'); });
          c.style.top = '0px';
          box.appendChild(c);
        });
        inner.appendChild(box);
        var mn = 1e9, ext = 0;
        box.querySelectorAll(MARK_SEL).forEach(function(m){
          var cs = getComputedStyle(m);
          if (cs.display === 'none') return;
          // the laid-out size, before the 45-degree turn; offsetWidth rounds,
          // and a 9.6px mark must not pass as 10
          var w = parseFloat(cs.width) || 0, h = parseFloat(cs.height) || 0;
          if (cs.boxSizing !== 'border-box') {
            var pb = function(a, b){ return (parseFloat(cs[a]) || 0) + (parseFloat(cs[b]) || 0); };
            w += pb('paddingLeft', 'paddingRight') + pb('borderLeftWidth', 'borderRightWidth');
            h += pb('paddingTop', 'paddingBottom') + pb('borderTopWidth', 'borderBottomWidth');
          }
          if (w < 0.5 || h < 0.5) return;
          mn = Math.min(mn, w, h);
          // ...and what it takes ACROSS the panel, after the turn
          ext = Math.max(ext, m.getBoundingClientRect().width);
        });
        box.remove();
        return mn === 1e9 ? null : {min: mn, ext: ext};
      }
      function markFloor(host){
        var cs = getComputedStyle(host), kinds = {};
        host.querySelectorAll('.nbmap-inner > .nbmap-node').forEach(function(n){
          if (n.classList.contains('nbgone')) return;
          // E21.5 (2026-10-03): `nbbm` (the 🔖 of the reading place, 17) is a
          // state, not a shape — with it in the key every new bookmark re-ran
          // the probe (≈ 350 ms on one CPU, 2–3 s after each scroll)
          kinds[n.className.replace(/\b(here|nbsel|nbpop|nbfolded|nbspan|nbbm)\b/g, '')
                           .replace(/\s+/g, ' ').trim()] = 1;
        });
        var key = document.body.className.split(/\s+/).filter(function(c){
                    return c.indexOf('nbskin-') === 0; }).join(',')
                + '|' + cs.getPropertyValue('--nbsym') + '|' + cs.getPropertyValue('--nbcirc')
                + '|' + Object.keys(kinds).sort().join(';');
        var C = window.__nbFloorCache;
        if (C && C.key === key) return C.f;
        var p1 = markProbe(host, 1);
        if (!p1) return null;
        // the smallest mark is linear in --nbthick (measured: 26px at 1, 3.8px at
        // 0.148); a mark with a fixed ring is not, so the guess is checked and
        // corrected against the probe itself
        var t = MARK_MIN_PX / p1.min, ext = p1.ext * t, p = null;
        for (var i = 0; i < 4; i++) {
          p = markProbe(host, t);
          if (!p) break;
          ext = p.ext;
          if (p.min >= MARK_MIN_PX - 0.01) break;
          t = t * MARK_MIN_PX / p.min;
        }
        var f = {t: Math.min(1, t), w: Math.max(16, Math.ceil(ext + 2)),
                 e0: ext, e1: p1.ext,
                 min: p ? Math.round(p.min * 100) / 100 : null};
        window.__nbFloorCache = {key: key, f: f};
        return f;
      }
      window.__nbMarkFloor = markFloor;
      // 2026-09-28c (K4): the standard width, the cap on the scale, and half
      // the notebook area the panel belongs to (0 when it cannot be measured).
      var WSTD = 560, KCAP = 3;
      function wHalf(host){
        var P = (host && host.closest && host.closest('.jp-NotebookPanel'))
              || allCls(document, 'jp-NotebookPanel').filter(function(p){ return !p.classList.contains('lm-mod-hidden'); })[0];
        var pr = P ? P.getBoundingClientRect() : null;
        var nw = pr ? pr.width : 0;
        var hw = nw > 0 ? Math.round(nw / 2) : 0;
        // 2026-09-29e (E7.2, Applikation) — TO THE MIDDLE OF THE PAGE, IN LAB
        // AS IN LITE. Measured in real JupyterLab 4.6 (v1.28, 1400 × 900): the
        // grip did reach half the notebook panel (536 px, left edge at 825 =
        // the panel's middle) — but JupyterLab opens with the file browser
        // (250 px) on the left, so the notebook panel is 1072 px, not 1324,
        // and its middle is 125 px right of the page's. Without that side bar
        // (Lite as the reader uses it) both middles coincide. The far end is
        // now the page's middle: the panel's left edge reaches innerWidth / 2
        // (1400: 662 px with or without the side bar), never less than half
        // the notebook and never more than the notebook less 40 px.
        // 2026-10-02 (E19.1, Struktur) — HALF THE DOCUMENT, NOT THE PAGE: the
        // user takes E7.2 back. The far end is half the notebook area (the
        // main area without side bars), with the file browser open or shut.
        // 2026-10-06 (E23.11, Struktur) — TO THE DOCUMENT'S MAIN AXIS, MEASURED.
        // The far end is where the document's middle is: the middle of the
        // title card (or, folded away, of the first pill) on the page — the
        // axis every block stands on (E22.8). The panel's left edge reaches it
        // and never passes it (user, video 7: the panel lay over the text).
        // Half the notebook stays the fallback where no axis can be read (a
        // cold page, a front end without our blocks). Read here, every pass:
        // the lens, a side bar or the window move the axis.
        if (P && hw > 0) {
          var ax = null, cds = allCls(P, 'nbtitle-card'), q, i;
          for (i = 0; i < cds.length && ax === null; i++) {
            q = cds[i].getBoundingClientRect();
            if (q.height > 4 && q.width > 4) ax = q.left + q.width / 2;
          }
          if (ax === null) {
            var hs = allCls(P, 'jupyter-widget-Collapse-header');
            for (i = 0; i < hs.length && ax === null; i++) {
              q = hs[i].getBoundingClientRect();
              if (q.height > 4 && q.width > 4) ax = q.left + q.width / 2;
            }
          }
          var rl = host && host.querySelector ? host.querySelector('.nbrail') : null;
          var rR = rl ? rl.getBoundingClientRect().right : 0;
          if (!(rR > 0)) rR = pr.right - 1;
          if (ax !== null && rR - ax > 8 && ax > pr.left) hw = Math.floor(rR - ax);
        }
        window.__nbWhalf = hw;
        return hw;
      }
      // the far end of the control in percent: 100 is the standard width,
      // beyond it the grip reaches half the notebook
      // (E19.1: also BELOW the standard width — a notebook narrower than
      // 2 × 560 px stops the grip at its half; floor, never past it)
      function gMax(){
        var wm = window.__nbWmin || 16, hw = window.__nbWhalf || 0;
        if (!(hw > wm)) return GMAX;
        // E23.11: rounded up — the step that crosses the far end is cut to it
        // (applyGui: w = min(w, WHALF)), so the panel reaches the axis exactly
        return Math.max(GMIN + 1, Math.ceil((hw - wm) / ((WSTD - wm) / 100)));
      }
      window.__nbGMax = gMax;
      function applyGui(host){
        if (!host) return;
        var pct = guiLevel(), t = guiT(pct), tm = markT(pct);
        var rail = host.querySelector('.nbrail');
        if (rail && rail.style.zoom) rail.style.zoom = '';   // an older build's way
        var root = document.documentElement.style;
        if (vertOn()) {
          // Vertical: the height belongs to the document, so the control zooms
          // everything ELSE — width, markers, names — in one proportion. That is
          // what Ctrl+wheel does to a page, applied to the rail alone.
          //
          // This is safe here only because in vertical every marker is pinned to
          // `top:0` of its node and centred with translate(-50%,-50%): --nbthick
          // changes sizes and never positions, so a fatter rail still has its
          // circles on the same screen line as their headings.
          // 2026-09-25d — THE CONTROL RUNS FROM "THE LINE ALONE" TO "WITH
          // NAMES". It ran from 150px to 300px, which is neither end: at 0 %%
          // the panel was still a wide empty column, and at 100 %% there was
          // never room for a word. The new ends are the two things a reader
          // actually wants — everything out of the way, or the structure
          // written out.
          var FL = markFloor(host) || {t: 0, w: 16};
          // E9.1: the scroll-bar cursor stands INSIDE the panel at its right
          // edge, shut or open — its width and a gap are reserved there
          // 2026-09-30 (E11.6, Struktur) — THE SCROLL BAR LEFT THE PANEL.
          // Cursor and track stand in a column of their own RIGHT of the
          // panel (SBW, vertPlace/placeCursor), so nothing is reserved for
          // them inside any more: the lane is the panel's middle, shut too.
          var CUR_R = 0, SB_PAD = 6;
          // 2026-09-30 (E10.M-wmin, Struktur) — SHUT, THE PANEL IS AS WIDE
          // AS THE LENS DRAWS ITS MARKS. The floor's width (markFloor, probed
          // WITHOUT the lens since css-E10.3) and the cursor's room are what
          // the panel needs at 100 %%; the stylesheet draws the marks × lens
          // (--nbkz), so shut at 150 %% 12–13 of 16 marks hung up to 11 px
          // over the rail (CSS, 30.09.). The marks' part of the narrow end is
          // now × lens; the cursor is a tool and keeps its size (measured:
          // 10 px wide at every lens), so its room CUR_R does not scale with
          // the lens — here, in the fit and for the lane (_cr). The standard
          // width WSTD stays the reader's.
          // E31 G1 (2026-10-12, JS): the controls' size (⚙ „Interface size“, --nbgs, 19-title-sync) is one
          // more factor of the PANEL — never of the document: the marks' part of the narrow end and the
          // panel's own factor (--nbk, everything the stylesheet draws × --nbk, and window.__nbK) carry it
          var GSF = window.__nbGsF ? window.__nbGsF() : 1;
          var ZL = zoomLevel() / 100 * GSF;
          var WMIN = Math.round(FL.w * ZL) + CUR_R + SB_PAD, WMAX = WSTD;
          window.__nbWmin = WMIN;
          // 2026-09-28c (K4) — THE PANEL PULLS OUT TO HALF THE NOTEBOOK.
          // 0-100 %% is the old travel, the line alone to the standard width
          // (WSTD, where every mark is at full size and the names are shown).
          // The grip drags further: past 100 %% the panel keeps widening until
          // it is half as wide as the notebook area, and from the standard
          // width on EVERYTHING on it grows in proportion — marks, pips, lane,
          // names, marker and cursor all carry --nbk = width / WSTD. Below the
          // standard width nothing changed (28b). The far end is measured on
          // the notebook panel every pass, so a resize moves it.
          var WHALF = wHalf(host);
          var w = Math.round(WMIN + (WSTD - WMIN) * (pct / 100));
          // E23.14 Nach-Runde: the width this share drew before, in pixels —
          // a narrow end measured a few pixels off does not move it
          var gpx = pct > 0 ? guiPx() : 0;
          if (gpx > 0) w = Math.max(WMIN, Math.round(gpx));
          var w0 = w;
          if (WHALF) w = Math.min(w, Math.max(WMIN, WHALF));
          // the taper keeps reading the control where the width is not cut
          // short, so below the standard width every size is 28b's exactly
          var pEff = w === w0 ? Math.min(1, pct / 100)
                   : Math.max(0, Math.min(1, (w - WMIN) / Math.max(1, WSTD - WMIN)));
          // 2026-09-30 (E9.3, Struktur) — THE PANEL SCALES WITH THE LENS.
          // Zoomed out, the document's pills came closer together while the
          // names, pips and labels kept their size and ran into each other
          // (the reader's video). The stylesheet multiplies every size on the
          // panel by the lens (--nbk × --nbzf, CSS-E9.3); --nbk itself stays
          // the panel's own factor. Everything THIS function and its helpers
          // compute from sizes — name column, lane room, pip room, marker,
          // bookmark — uses the product, window.__nbK, so it agrees with what
          // the stylesheet draws. The panel's WIDTH stays the reader's.
          var nbkP = Math.min(KCAP, Math.max(1, w / WSTD) * GSF);
          var nbk = nbkP * zoomLevel() / 100;
          window.__nbK = nbk; window.__nbW = w;
          root.setProperty('--nbk', nbkP.toFixed(4));
          root.setProperty('--nbvert-w', w + 'px');
          // THE MARKS ARE AS BIG AS THE PANEL CAN HOLD, NEVER BIGGER THAN FULL
          // SIZE. Not a ladder of five steps and not a taper that shrinks them
          // while there is still room: one rule, from the geometry. The widest
          // mark is a square of 24·sym·circ turned 45°, so what has to fit
          // across the panel is its DIAGONAL. Solve that for the scale and the
          // marks shrink exactly when, and only when, they stop fitting — which
          // is what "smaller and smaller until only the timeline is left"
          // means, without a single magic number.
          var _cs = getComputedStyle(host);
          var _S = parseFloat(_cs.getPropertyValue('--nbsym')) || 2.9;
          var _C = parseFloat(_cs.getPropertyValue('--nbcirc')) || 0.55;
          var _ext = 24 * _S * _C * 1.4142;
          var _fit = Math.max(0, Math.min(1, (w - 8) / _ext));
          // MEASURED, and this is the second half of the rule. The fit alone
          // was a cliff: the marks were full size from 70px of panel upwards
          // and collapsed to nothing in the last eight percent of the control,
          // so pulling the panel in did nothing at all until it suddenly did
          // everything. A gentle taper runs underneath it, so the marks get
          // smaller the whole way in — and the fit still overrides it at the
          // narrow end, which is what makes "until only the timeline is left"
          // true rather than merely likely.
          // 2026-09-27b — and never below the floor: the smallest mark stays
          // MARK_MIN_PX wide, the panel is widened to carry it (markFloor).
          // The fit is the MEASURED extent now, not 24·sym·circ·√2: the open
          // exercise wears a ring that does not scale, so it is 65px across at
          // full size where the formula said 54, and at the narrow end it hung
          // out of the panel (measured 27b: 32.5px in 32). Two probes give its
          // extent at the floor and at full size; in between it is linear.
          // 2026-09-30 (E10, Struktur) — THE MARKS FIT LEFT OF THE CURSOR.
          // Since E9.1 the panel is the floor's width PLUS the cursor's room
          // (CUR_R), and the fit still read the whole width: shut, the marks
          // came out at 0.52 instead of the floor's 0.38 and hung ~2 px into
          // the cursor's column (test_js, v1.34/35). The fit takes the room
          // the marks actually have, w − CUR_R·K.
          // E10.M-wmin: the fit is read WITHOUT the lens (_ext and the
          // floor's extents are unlensed; the stylesheet multiplies tm by it)
          var wFit = (w - Math.round(CUR_R * nbkP) - SB_PAD) / ZL;   // E11.6: the pad is air, not room
          _fit = Math.max(0, Math.min(1, (wFit - 8) / _ext));
          if (FL.e1 > FL.e0 + 0.5 && FL.t < 1)
            _fit = FL.t + (wFit - 2 - FL.e0) * (1 - FL.t) / (FL.e1 - FL.e0);
          // 2026-10-05 (E22.9, Struktur) — SHUT IS THE FLOOR, AT EVERY LENS. The
          // shut width is round(FL.w × lens) + pad; read back through the
          // lens, the rounding left _fit 0–1.6 %% above or below the floor
          // from one lens step to the next (measured v1.63: --nbthick 0.3966
          // → 0.4031 → 0.3935 → 0.3996 … at 100/105/110/115 %%): every mark
          // grew and shrank by ~0.5 px on each Ctrl+wheel notch. At the narrow
          // end the marks are the floor's size, exactly.
          if (w <= WMIN) _fit = FL.t;
          tm = Math.max(FL.t, Math.min(_fit, 0.52 + 0.48 * pEff)) * nbkP;
          root.setProperty('--nbthick', String(tm));
          // THE COLUMN FOR THE NAMES. It is what is left between the cursor,
          // which hangs at the panel's left edge, and the widest mark on the
          // lane. It is a number, not a guess, and it is what decides whether
          // the names are shown at all.
          // E9.3: as DRAWN, with the lens (--nbsym × --nbzf; the probes
          // below are measured in the lensed .nbmap already)
          var _half = (_ext * tm) / 2 * (nbk / nbkP);
          // 2026-09-28b (K2.8) — THE NAMES STAND IN THE MIDDLE BETWEEN THE
          // CURSOR AND THE LANE (user, 27.09.). Until 28a the column ran from
          // 44 px to the widest mark and the names were right-aligned against
          // the lane. Now the column is centred on the point half way between
          // the cursor's end and the lane, as wide as it can be without
          // reaching the widest mark: every name — short or cut off with an
          // ellipsis — has its middle on that point. The widest mark is the
          // MEASURED one where there is a measurement (the open exercise's
          // ring does not scale, 27b), else the formula.
          if (FL.e1 > FL.e0 + 0.5 && FL.t < 1)
            _half = Math.max(_half, (FL.e0 + (FL.e1 - FL.e0) * (tm - FL.t) / (1 - FL.t)) / 2);
          // the cursor's end, in the node's own coordinates: the cursor hangs
          // 6 px inside the panel (placeCursor) and is 30 px long (its rule),
          // a node starts at the rail's inner edge, 1 px in — so 35
          // 2026-09-29 (E6.7, Struktur) — MORE AIR LEFT OF THE CURSOR: it
          // hangs CUR_AIR further in (placeCursor reads the same number), and
          // the name column's middle moves with its end
          var _air = Math.round(18 * nbk);
          window.__nbCurAir = _air;
          // E7.5 — the cursor is a scroll thumb now, 14 px × K wide, not the
          // 30-px bar: its end is 16·K in (thumb + 2 px)
          // E9.1: the cursor left the name column's left end (it is at the
          // right edge now); the lane is the middle of what is left of it
          var _cr = Math.round(CUR_R * nbkP);        // E10.M-wmin: a tool, no lens
          var _crN = 5 + Math.round(8 * nbk);
          var _lane = Math.max(6, Math.round((w - _cr) / 2));
          var _mid = (_crN + _lane) / 2;
          var _hw = Math.max(0, (_lane - _half - 2 * nbk) - _mid);
          var _labW = Math.max(0, Math.floor(2 * _hw));
          // 2026-09-29e (E7.1, Struktur) — THE PIPS STAND RIGHT OF THE LANE
          // (17-marker pipPlace measures what they need, in units of K). When
          // the names — and with them the pips — are shown and the right half
          // is too narrow for them, the lane moves left by the difference and
          // the name column is measured again from the new lane. Where the
          // moved lane leaves no room for a name, the names stay off and the
          // lane stays in the middle.
          var _pn = (window.__nbPipNeedK || 0) * nbk;
          if (_pn > 0 && _labW >= 72 * nbk && _lane + _pn > w - 2 - _cr) {
            var _l2 = Math.max(6, Math.floor(w - 2 - _cr - _pn));
            var _m2 = (_crN + _l2) / 2;
            var _w2 = Math.max(0, Math.floor(2 * Math.max(0, (_l2 - _half - 2 * nbk) - _m2)));
            if (_w2 >= 72 * nbk) { _lane = _l2; _mid = _m2; _labW = _w2; }
          }
          window.__nbLane = _lane;
          // E7.4 — THE TEXT GOES FIRST, THE PIPS LAST. `nbnames` now says "the
          // chapter tallies are shown", `nbnotext` "…but the words are not":
          // the pips' circles need only their own room right of the lane
          // (pipPlace measures it, __nbPipCircK), so while the panel is pulled
          // in the names and the pip labels fade out first and the circles
          // stay until even they no longer fit.
          var _txt = _labW >= 72 * nbk;
          var _pc = (window.__nbPipCircK || 40) * nbk;
          var _pips = _txt || (_lane + _pc <= w - 2 - _cr && w >= 120);
          root.setProperty('--nbvert-lab', _labW + 'px');
          root.setProperty('--nbvert-labx', (_mid - _labW / 2).toFixed(1) + 'px');
          // 72px is "Coding 12" at this size with room to spare, measured —
          // the threshold is what a name NEEDS, not a round number.
          host.classList.toggle('nbnames', _pips);
          host.classList.toggle('nbnotext', _pips && !_txt);
          // THE LINE KEEPS ITS PLACE. The axis used to jump to the middle of the
          // column the moment the names were dropped — a hundred pixels sideways
          // in one step of the control, which is what made the timeline lurch
          // while the panel was being resized. One formula for every size: the
          // line keeps its distance from the panel's left edge, in proportion
          // with everything else on it.
          // 30px left the exercise circles (38px across) all but touching the
          // panel's edge. The lane is moved in far enough that the largest
          // marker, and its ring, clear it at every size.
          // AT 0 % THE LINE IS CENTRED. The reader asked for the same gap on
          // both sides of the rail when it is at its narrowest; at full size it
          // keeps the old place, close to the left edge, so the names have room.
          // 2026-09-25 — THE LANE IS THE PANEL'S MIDDLE. FULL STOP.
          // It has been three things in three builds: a share that slid with
          // the control (24x), a fixed distance from the left edge, then a
          // fixed distance from the right (24bi). All three meant the timeline
          // moved when something else did. One rule that cannot be argued
          // with: dead centre of the panel, at every width, in every skin.
          // A skin changes what a mark LOOKS like, never where the line is.
          // the floor is 6, not 20: at the narrowest setting a floor of 20 held
          // the lane 12px right of the middle of a 16px panel — the one width
          // where the centring is most obvious (measured: lane+12).
          root.setProperty('--nbvert-axis', _lane + 'px');
        } else {
          // Horizontal: the width belongs to the document, so the control sets the
          // THICKNESS — how far the panel reaches down the page.
          root.setProperty('--nbvert-w', '300px');
          root.setProperty('--nbvert-axis', '30px');
          // HORIZONTAL keeps the old number. There the control's meaning is the
          // thickness itself — how far the banner reaches down the page — so it
          // has to keep its full travel. Only the vertical rail, where the
          // control means width, gets the raised floor for the marks.
          root.setProperty('--nbthick', String(t));
        }
        // the ladder follows the MARKS, not the panel: a rung is about whether
        // a shape is still legible, and the shapes are sized by whatever
        // --nbthick ended up being in this orientation
        var tk = vertOn() ? tm : t;
        // 2026-09-27b — standing, only the words go (names, then the glyphs in
        // the marks). The marks themselves stay: the floor above keeps every
        // one of them at least MARK_MIN_PX, and fading them out as well was
        // what left the shut panel empty.
        var nLad = vertOn() ? 2 : DETAIL.length;
        for (var i = 0; i < DETAIL.length; i++)
          host.classList.toggle(DETAIL[i][0], i < nLad && tk < DETAIL[i][1]);
        // 2026-10-01 (E12.1, Struktur) — THE GRIP'S ARROW TURNS WHERE THE
        // TEXT GOES. `data-names` says whether any name in the timeline can be
        // read: shown (`nbnames`) and with words (not `nbnotext`) — the ladder's
        // `det-text` fades the others but leaves the lit and chosen names (the
        // last text there is). The stylesheet turns the arrow on it.
        var cl = host.classList;
        host.setAttribute('data-names', vertOn() && cl.contains('nbnames') &&
          !cl.contains('nbnotext') ? '1' : '0');
        slider(host, '.nbz-gui', Math.min(GMAX, pct), 'Panel ');
      }
      window.__nbApplyGui = applyGui;
      // Which way the timeline runs. Horizontal is a banner across the top of the
      // document; vertical hangs it down the right-hand edge, where every node
      // sits at the height of the chapter it points at.
      // For now there is one orientation: the rail runs down the right-hand edge
      // of the document. The horizontal banner is not deleted — every rule and
      // every measurement for it is still here — it is parked, because two
      // layouts were two places for the same bug to hide while the panel was
      // still settling. Flipping comes back when it is worth testing again.
      function orient(){
        var v = 'v';
        try { v = localStorage.getItem(idKey(OKEY)) === 'h' ? 'h' : 'v'; } catch (e) {}
        return v;
      }
      function setOrient(v){
        try { localStorage.setItem(idKey(OKEY), v === 'v' ? 'v' : 'h'); } catch (e) {}
        var host = document.getElementById(HOST_ID), src = activeSrc();
        if (host && src) {
          // leave no trace of the other orientation behind: the reserved strip and
          // every inline position belong to one layout only
          var nb = src.closest('.jp-Notebook') || src.closest('.jp-NotebookPanel');
          if (nb) { nb.style.paddingTop = ''; delete nb.dataset.nbpad; }
          var sc = scroller(host);
          if (sc) { sc.style.paddingRight = ''; delete sc.dataset.nbpadr; }
          var inner = host.querySelector('.nbmap-inner');
          if (inner) { inner.style.height = ''; inner.style.paddingLeft = '';
                       inner.style.paddingRight = ''; }
          host.querySelectorAll('.nbmap-node').forEach(function(n){ n.style.top = ''; });
          host.style.height = ''; host.style.width = ''; host.style.right = '';
          if (window.__nbrailSync) window.__nbrailSync();
        }
      }
      // 2026-09-24r — THE DOCUMENT CONTROL'S RANGE.
      // Stored as the real scale, shown as 0-100: what used to be 50 % is 0 and
      // what used to be 150 % is 100. Above 150 the boxes were wider than the
      // window and nobody went there; below 50 the text was unreadable.
      // 2026-09-24w — the floor was too far out: at 50 %% the text was smaller
      // than anything anyone reads. The document never gets SMALLER than its
      // natural size now; the control only makes it bigger.
      // 2026-09-24bi — THE MAGNIFIER READS AS A MAGNIFIER.
      // Two things were wrong and they compounded. The readout showed the
      // SLIDER's position (0-100) and not the zoom, so "0%%" meant 100%% and
      // "25%%" meant 125%% — a control whose number means nothing is worse than
      // no number. And the range only ever went UP: a reader who wanted more of
      // the document on screen at once had nowhere to go. It runs from 60%% to
      // 200%% now, with 100%% inside it, and the readout is the zoom itself.
      var ZFLOOR = 60, ZCEIL = 200;
      var ZSPAN = (ZCEIL - ZFLOOR) / 100;                      // 1.5 % per step
      // 2026-09-30 (E9.4, Struktur) — THE LENS GOES ON UNTIL THE READING
      // COLUMN FILLS THE WINDOW. 200 %% was a typed end: on a wide screen the
      // column (--nbcolw, 720 px) was still a strip in the middle there. The
      // ceiling is now the zoom at which the column is as wide as the
      // document's room (the scroller less the panel's reserve), rounded up
      // to 5 %%, never below 200 and never above 400. Measured at most every
      // half second; the slider's scale (ZSPAN) follows it.
      var zCeilAt = 0;
      function zCeilNow(){
        if (Date.now() - zCeilAt < 500) return ZCEIL;
        zCeilAt = Date.now();
        var sc = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer')
              || document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Notebook');
        if (!sc || !(sc.clientWidth > 200)) return ZCEIL;
        var cw = parseFloat(getComputedStyle(sc).getPropertyValue('--nbcolw')) || 720;
        var room = sc.clientWidth - (parseFloat(sc.style.paddingRight) || 0) - 48;
        var c = Math.ceil(100 * room / cw / 5) * 5;
        c = Math.max(200, Math.min(400, c));
        if (c !== ZCEIL) { ZCEIL = c; ZSPAN = (ZCEIL - ZFLOOR) / 100; }
        window.__nbZCeil = ZCEIL;
        return ZCEIL;
      }
      // 2026-10-08 (E25.o, JavaScript) — THE MIDDLE OF THE BAR IS 100 %%.
      // Nutzer 08.10.: the standard lens is the middle of the bar and that
      // value is called 100 %% (double click sets it). The bar (0 … 100) is
      // two halves now: 0 … 50 = ZFLOOR … 100 %%, 50 … 100 = 100 %% … ZCEIL,
      // each even; the middle stays 100 %% whatever ZCEIL the window allows.
      function zoomSlide(pct){
        zCeilNow();
        return Math.round(pct <= 100 ? 50 * (pct - ZFLOOR) / (100 - ZFLOOR) : 50 + 50 * (pct - 100) / (ZCEIL - 100));
      }
      function zoomStore(v){
        zCeilNow();
        return Math.round(v <= 50 ? ZFLOOR + (100 - ZFLOOR) * v / 50 : 100 + (ZCEIL - 100) * (v - 50) / 50);
      }
      // 2026-10-02 (E15.7, Struktur) — THE LENS IS PER NOTEBOOK. One key
      // for every notebook (ZKEY) meant Complex at 150 %% opened Modeling at
      // 150 %% too. The key now carries the notebook's id (as progress and
      // mode do); the old shared value is taken over ONCE as the start value
      // of a notebook that has none yet, and is not written any more.
      // One notebook's id, as every per-notebook key spells it: the last
      // feed with a record in `root` (default the page). E15.7 made this one
      // helper of the four copies (own cells, mode, bookmark, lens).
      // E16.10: without a root, the id of the notebook IN FRONT — not the
      // last feed of the window (with two notebooks open, the other one's id
      // kept its bookmark, own cells and mode); a notebook in front that has
      // not run has no id. idKey: a key of this notebook, `<key>.<id>`, the
      // old shared value taken over once (as the lens, E15.7).
      function nbId(root){
        if (root === undefined || (window.__nbMemo && root === visiblePanel()))   // E22.9: one look per follow
          return memo('id', function(){ return nbId0(visiblePanel()); });
        return nbId0(root);
      }
      // `.nbfeed[data-progress]` under root, in page order (E22.1b: by class)
      function feedsP(root){
        return allCls(root, 'nbfeed').filter(function(f){ return f.hasAttribute('data-progress'); });
      }
      function nbId0(root){
        var fs = feedsP(root || document), id = '';            // E22.1b
        try { id = JSON.parse(fs[fs.length - 1].getAttribute('data-progress')).id || ''; } catch (e) {}
        return String(id).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
      }
      function idKey(k){
        var id = nbId(), ik = id ? k + '.' + id : k;
        try { if (id && localStorage.getItem(ik) === null && localStorage.getItem(k) !== null) localStorage.setItem(ik, localStorage.getItem(k)); } catch (e) {}
        return ik;
      }
      window.__nbOKey = function(){ return idKey(OKEY); };
      function zKey(){ var id = nbId(visiblePanel()); return id ? ZKEY + '.' + id : ZKEY; }
      window.__nbZKey = zKey;
      function zoomLevel(){
        zCeilNow();
        var v = null, k = zKey();
        // E25.o: this notebook's own or the standard 100 %% — the old shared
        // value (and with no id the shared key) is not read
        try { v = k !== ZKEY ? localStorage.getItem(k) : null; } catch (e) {}
        v = parseInt(v, 10) || 100;
        return Math.max(ZFLOOR, Math.min(ZCEIL, v));
      }
      // The zoom control does exactly what Ctrl+wheel does — it zooms the PAGE.
      // An earlier attempt zoomed only the notebook's inner window and widened it
      // by 1/zoom to compensate; that works in theory and drifts in practice,
      // because the inner window's containing block is not the scroller in every
      // front end. Zooming the page keeps document, panel and scrollbar in one
      // coordinate system, which is why Ctrl+wheel never lost the alignment.
      // The document zoom scales the READING MATTER, never the application.
      //
      // The earlier build put `zoom` on <body>, which is what a browser's own
      // Ctrl+wheel does — and that is exactly the grey block: at 50% the whole
      // shell shrinks into a corner of the window and what is left over is bare
      // background. It also dragged the two panels along, so every length they
      // wrote had to be divided by the zoom again, and any value read in the
      // same pass was read at the wrong scale.
      //
      // So the zoom goes on the scroller's CONTENT instead. The scroller keeps
      // its full size, the window stays full, the panels live outside the
      // zoomed box and are therefore immune by construction — no counter-scale,
      // no unit conversion, nothing to get out of step.
      // NEVER the windowed container. JupyterLab's virtual scroller writes each
      // cell's `top` and the inner's `height` in ITS pixels; scaling that element
      // puts the browser's rendering and the front end's arithmetic a factor
      // apart, and the reader is left staring at an empty document because the
      // list believes the cells are somewhere they are not.
      //
      // The cell's own WRAPPERS are safe: scaling them makes the cell shorter,
      // which is the same thing that happens every time an accordion closes —
      // a case the windowed list handles on every interaction.
      function zoomTargets(src){
        var p = src && src.closest('.jp-NotebookPanel');
        if (!p) return [];
        var cells = allCls(p, 'jp-Cell'), out = [], i, k;          // E22.1b
        for (i = 0; i < cells.length; i++) {
          var kids = cells[i].children;
          for (k = 0; k < kids.length; k++)
            if (kids[k].nodeType === 1) out.push(kids[k]);
        }
        if (out.length) return out;
        // the mock, and any front end without .jp-Cell: the scroller's children
        var sc = byCls(p, 'jp-Notebook') || byCls(p, 'jp-WindowedPanel-outer');
        if (!sc) return [];
        return Array.prototype.filter.call(sc.children, function(c){
          return c.nodeType === 1 && !c.classList.contains('nbpanel-host')
              && !c.classList.contains('jp-WindowedPanel-inner');
        });
      }
      // Everything the panel measures is now a screen pixel. The function stays
      // so that the arithmetic below reads the same as before.
      function pageZoom(){ return 1; }

