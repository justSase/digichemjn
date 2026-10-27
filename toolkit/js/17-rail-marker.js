      // Move the window so the exercise you are on is inside it. Done by setting
      // scrollLeft on the map itself — scrollIntoView() would drag the whole page
      // along. It only fires when the current node changes, so dragging the
      // scrollbar by hand is never fought.
      // The panel follows the current exercise only when that exercise CHANGES.
      // Anything the reader does — wheel, drag, keyboard — sets 'manual', and then
      // the panel keeps its hands off until the next exercise comes up. Without
      // that, every sync pulled the timeline back to where the panel wanted it.
      // Scrolling the document moves the timeline with it: the node whose section
      // is the last one above the fold is brought into the middle of the window.
      // Scrolling the document moves the timeline with it — the panel is a
      // position indicator, not a legend.

      // The marker is WELDED to the middle of the window: it is always drawn at
      // map.scrollLeft + clientWidth/2. Nothing else may move it, which is why it
      // can never drift away from the scrollbar underneath. The timeline slides
      // beneath it; the marker itself does not travel.
      // 2026-10-02 (E16.3, Applikation) — NO TRAIL. The light is one circle
      // behind the marker (CSS, `.nbmap-here`); the band that ran behind the
      // movement (E12.5, `.nbmap-trail`) is gone, and with it its script.
      function markCentre(host){
        var map = host.querySelector('.nbmap');
        var mark = host.querySelector('.nbmap-here');
        var inner = host.querySelector('.nbmap-inner');
        if (!map || !mark || !inner) return;
        var nodes = inner.querySelectorAll('.nbmap-node');
        var i;
        if (vertOn()) {
          // the same band, turned 90°: welded to the middle of the window, and
          // whatever it runs over takes its colour
          // As a scrollbar thumb it has to say how much of the document is on
          // screen, so its length is the visible share of the whole — with a
          // floor, or a long notebook would leave nothing to grab.
          // clamped to 1: between a flip and the next layout pass the inner is
          // still the height the banner gave it, and an unclamped ratio made the
          // thumb longer than the rail it lives in
          // The rail is 1:1 with the document and scrolls WITH it, so the
          // honest place for "the window you are looking at" is the TOP of the
          // visible rail — not its middle. Welded to the middle, clicking a
          // chapter put its pill at the top of the page and the marker half a
          // screen below it; welded to the top, the pill and the marker's upper
          // edge are the same line, which is what the reader is told to expect.
          var sc2 = scroller(host);
          var full = Math.max(map.clientHeight, inner.offsetHeight || 0,
                              map.scrollHeight || 0);
          // how much of the DOCUMENT is on screen, measured on the document
          var share = sc2 && sc2.scrollHeight
                    ? sc2.clientHeight / sc2.scrollHeight
                    : map.clientHeight / Math.max(1, full);
          // A thumb, not a window. The rail is 1:1 with the document, so the
          // visible range drawn to scale is nearly the whole rail — true, and
          // useless to look at. The share is drawn on the RAIL'S viewport
          // instead: short, proportional to how much of the document is on
          // screen, and its upper edge is the reading position.
          // 2026-09-24n — and SMALL. A thumb a hundred pixels long was the
          // loudest thing on the rail and swallowed several marks at once. It
          // is now barely larger than a marker circle (28px), so it reads as
          // "you are on this one" rather than as a second instrument. The
          // share still moves it between 32 and 44, so a short notebook still
          // gets a slightly longer thumb than a long one.
          // 2026-09-24ab — SHORT AGAIN, and that is the final answer. The long
          // thumb said how much of the document was on screen and cost the one
          // thing the marker is for: standing level with a single mark, so that
          // "where am I" has a one-line answer. The travel from 24z stays; only
          // the length goes back. The share still moves it between 32 and 38,
          // so a short notebook gets a slightly longer marker than a long one.
          // 2026-09-24ad — shorter still. At 36px it was as tall as an exercise
          // mark and read as a fifth kind of mark; at 18 it reads as a position
          // on the line, which is all it is. The share still moves it a little,
          // so a short notebook gets a slightly longer marker than a long one.
          var hv = Math.max(16, Math.min(22, Math.min(map.clientHeight,
                            Math.round(map.clientHeight * Math.min(1, share)))));
          // K4: the marker grows with the panel past its standard width
          hv = Math.round(hv * (window.__nbK || 1));
          // K4: border-box now (see the --nbk block) — the 1-px border each side is
          // part of the box, so the box is hv + 2, as it was when it was content-box
          var hbox = (hv + 2 * (window.__nbK || 1)).toFixed(2) + 'px';
          if (mark.style.height !== hbox) mark.style.height = hbox;
          // The marker's history — welded to the window (24o), a scrollbar
          // thumb (24x), read through the rail's own scale (24aw), snapped to
          // the nearest mark (24ak) with a trail for the hidden travel (24ao),
          // the reading position as title + scrolled distance (27d) — ends in
          // the rule below. railY0 is the title mark's place inside the rail.
          var lo = parseInt(host.dataset.railY0 || '0', 10) || 0;
          // 2026-09-27f — THE MARKER RUNS ON THE READING LINE (Eilauftrag 2).
          // Until 27e it was placed from the reading position and then SNAPPED
          // to the nearest mark, so a chapter lit up half a screen before its
          // mark reached the cursor and the marker hopped along the screen
          // (measured: up to ~140 px off the line). The reader asked for the
          // marker that lights the chapters up to stand where the cursor
          // stands: on the line the title mark has when the notebook opens
          // (railY0 below the top of the rail's window — see placeCursor). The
          // rail scrolls 1:1 with the document, so in the rail's own
          // coordinates the line is simply map.scrollTop + railY0; the marks
          // travel past it and the marker does not move on the screen.
          // A mark is PASSED from the scroll at which its middle reaches the
          // line, and the one that lights up is the last mark passed — so a
          // chapter lights exactly when its mark arrives on the line and stays
          // lit until the next one arrives. The trail (24ao) keeps its meaning,
          // "how far since the mark": it now runs from the lit mark down to
          // the marker, always upwards from it, bright at the marker's end.
          // K3.1a/K4: a chapter's pips hang under its name's last line
          var fk = (window.__nbW || 0) + '|' + host.classList.contains('nbnames');
          for (li = 0; li < nodes.length; li++) {
            var fn0 = nodes[li];
            if (fn0.__nbFit === fk || !fn0.querySelector('.nbchapstat')) continue;
            var lb0 = fn0.querySelector('.nbmap-lab');
            if (lb0 && lb0.offsetHeight > 0)
              fn0.style.setProperty('--nblabh', (lb0.offsetHeight / 2).toFixed(2) + 'px');
            fn0.__nbFit = fk;
          }
          var lineY = Math.round((map.scrollTop || 0) + lo);
          var top = Math.max(0, lineY - Math.round(hv / 2));
          var litI = -1, litY = -1e9, li;
          for (li = 0; li < nodes.length; li++) {
            if (nodes[li].classList.contains('nbgone')) continue;
            var ly = nodes[li].offsetTop;
            if (!(ly >= 0)) continue;
            // E10.M-lit: +2, the landing's own tolerance — a click landed a
            // mark 2 px low (rail 1 px behind the page + 1 px rounding) and
            // it stood on the line unlit (lab_landing, v1.42)
            if (ly <= lineY + 2 && ly >= litY) { litY = ly; litI = li; }
          }
          var lastLine = host.__nbLineY;
          var dy = lastLine === undefined ? 0 : lineY - lastLine;
          var dir = dy < 0 ? 'up' : dy > 0 ? 'down'
                  : (mark.getAttribute('data-dir') || 'down');
          host.__nbLineY = lineY;
          if (mark.getAttribute('data-dir') !== dir)
            mark.setAttribute('data-dir', dir);
          if (mark.style.top !== top + 'px') mark.style.top = top + 'px';
          // 2026-10-02 (E21.8, Applikation) — THE TRAIL AGAIN, DRAWN BY CSS.
          // Contract with css-E21.8: the marker carries its place as
          // `--nbm-y`; a registered property `--nbm-lag` follows it with a
          // 0.5-s transition and the gap between the two is the fading trail
          // (none at rest). Set in the same pass as `top`, never a frame late.
          if (mark.style.getPropertyValue('--nbm-y') !== top + 'px') mark.style.setProperty('--nbm-y', top + 'px');
          if (mark.style.left) mark.style.left = '';
          mark.classList.add('on');
          for (i = 0; i < nodes.length; i++) {
            var lit = i === litI;
            if (nodes[i].classList.contains('here') !== lit)
              nodes[i].classList.toggle('here', lit);
          }
          // the handle beside the lane is part of the marker, so it is placed
          // in the same pass — never a frame behind it
          placeCursor(host);
          return;
        }
        if (mark.style.top) mark.style.top = '';
        // the vertical marker sets its own height as a scrollbar thumb; across
        // the top that inline height would lift it off the line
        if (mark.style.height) mark.style.height = '';
        var w = mark.offsetWidth || 50;
        var left = Math.round(map.scrollLeft + map.clientWidth / 2 - w / 2);
        if (mark.style.left !== left + 'px') mark.style.left = left + 'px';
        mark.classList.add('on');
        var a = left, b = left + w;
        for (i = 0; i < nodes.length; i++) {
          var c = nodes[i].offsetLeft + nodes[i].offsetWidth / 2;
          nodes[i].classList.toggle('here', c >= a && c <= b);
        }
      }

      // Padding at both ends so every marker can reach the middle — and tuned so
      // that at scrollLeft 0 the middle sits exactly on the FIRST section bar.
      // The travel of the panel's scrollbar is the travel of the MARKER, and the
      // marker may go from the centre of the first section bar to the centre of
      // the last marker on the line — not one pixel further at either end. Both
      // paddings are therefore derived from a marker's centre, never from the
      // edge of a node's box: a node is 106px wide and its dot sits in the
      // middle, so padding to the box would overrun by half a node.
      function markX(n){
        var m = n.querySelector('.nbsect,.nbchapdot,.nbsubdot,.nbrail-dot');
        return n.offsetLeft + (m ? m.offsetLeft + m.offsetWidth / 2
                                 : n.offsetWidth / 2);
      }
      function pad(host){
        if (vertOn()) return;
        var map = host.querySelector('.nbmap');
        var inner = host.querySelector('.nbmap-inner');
        if (!map || !inner) return;
        var half = Math.round(map.clientWidth / 2);
        if (half < 40) return;
        var nodes = inner.querySelectorAll('.nbmap-node');
        if (!nodes.length) return;
        var first = nodes[0], last = nodes[nodes.length - 1];
        var cur = parseFloat(inner.style.paddingLeft) || 0;
        var want = Math.max(0, Math.round(cur + (half - markX(first))));
        if (Math.abs(want - cur) > 1) {
          inner.style.paddingLeft = want + 'px';
          cur = want;                       // the measurements below need it applied
        }
        // At the far end the window centre lands on
        //   paddingLeft + content + paddingRight - half,
        // and that has to be the centre of the last marker.
        var edge = last.offsetLeft + last.offsetWidth;   // end of the content box
        var pr = Math.max(0, Math.round(markX(last) + half - edge));
        if (inner.style.paddingRight !== pr + 'px') inner.style.paddingRight = pr + 'px';
      }

      // Where the reader is in the DOCUMENT, as a position on the line —
      // interpolated between the two anchored nodes on either side of the fold.
      function docPos(host){
        var inner = host.querySelector('.nbmap-inner');
        if (!inner) return null;
        var nodes = inner.querySelectorAll('.nbmap-node[data-target],.nbmap-node[data-sel]');
        var rail0 = railOf(host);
        var ref = (rail0 || host).getBoundingClientRect().bottom + 24;
        var mid = function(n){ return n.offsetLeft + n.offsetWidth / 2; };
        var prev = null, prevY = 0, next = null, nextY = 0;
        for (var i = 0; i < nodes.length; i++) {
          var el = targetEl(nodes[i]);
          if (!el) continue;
          var r = el.getBoundingClientRect();
          if (!r.height && !r.width && !r.top) continue;
          if (r.top <= ref) { prev = nodes[i]; prevY = r.top; }
          else { next = nodes[i]; nextY = r.top; break; }
        }
        if (prev && next && nextY > prevY) {
          var t = Math.max(0, Math.min(1, (ref - prevY) / (nextY - prevY)));
          return mid(prev) + t * (mid(next) - mid(prev));
        }
        if (prev) return mid(prev);
        if (next) return mid(next);
        return null;
      }

      function centreOn(host, x){
        var map = host.querySelector('.nbmap');
        if (!map) return;
        var want = Math.round(x - map.clientWidth / 2);
        want = Math.max(0, Math.min(want, map.scrollWidth - map.clientWidth));
        // one pixel is the smallest step the track can take; anything coarser
        // shows up as the stutter the reader sees while scrolling
        if (Math.abs(map.scrollLeft - want) < 1) return;
        // never smoothly: a smooth scroll keeps firing scroll events long after the
        // guard has expired, and each one reads as the reader scrubbing — panel and
        // document would chase each other across the notebook
        // a timestamp, not a timer: while the reader scrolls this runs once per
        // frame, and one setTimeout per frame is exactly the kind of litter that
        // makes a smooth scroll stutter
        window.__nbrailSelfScroll = true;
        window.__nbrailSelfAt = Date.now();
        map.scrollLeft = want;
      }

      // 2026-09-24az — THE FOOT MARK IS CORRECTED AGAINST THE SCREEN.
      // Mapping the footer through the layout is right in the ordinary view
      // (measured: 0px) and wrong in full screen (measured: 34px), because
      // full screen changes the frame the rail is measured in. Rather than
      // chase every frame of reference, the mark is checked where the reader
      // sees it: if the strip you click to add a cell is on screen, the mark
      // is nudged onto its middle. Self-correcting, so it holds in whatever
      // mode comes next too.
      function footAlign(host){
        if (!vertOn()) return;
        var cl = host.querySelector('.nbmap-node.cell');
        var foot = byCls(document, 'jp-Notebook-footer')
                || byCls(document, 'jp-WindowedPanel-footer');        // E22.1b
        if (!cl || !foot) return;
        var fr = foot.getBoundingClientRect();
        if (!(fr.height > 2)) return;
        var map = host.querySelector('.nbmap');
        if (!map) return;
        var mr = map.getBoundingClientRect();
        // only while the footer is actually in view — off screen its rect is
        // a projection, not a position
        if (fr.top > mr.bottom + 40 || fr.bottom < mr.top - 40) return;
        var cr = cl.getBoundingClientRect();
        var d = Math.round((fr.top + fr.height / 2) - (cr.top + cr.height / 2));
        if (Math.abs(d) < 2 || Math.abs(d) > 600) return;
        var now = parseFloat(cl.style.top || '0') || 0;
        var nt = Math.max(0, Math.round(now + d));
        // 2026-09-28c (K4) — …BUT NEVER ONTO THE MARK ABOVE IT. The nudge undid
        // the collision pass (24bd): with the panel at half the notebook the
        // marks are 1.6 × as big, and "your own cell" was pulled back 14 px
        // under the 43-px "End of the guided part" (measured, 1920 px window).
        // Level with the footer where there is room; otherwise as close as the
        // same rule as the pass allows (half of both marks plus the air).
        var vs = host.querySelectorAll('.nbmap-node:not(.nbgone)'), pv = null;
        for (var k = 0; k < vs.length; k++) { if (vs[k] === cl) break; pv = vs[k]; }
        if (pv) {
          var ext = function(nd){
            var m = nd.querySelector('.nbsect,.nbchapdot,.nbsubdot,.nbrail-dot,'
                                   + '.nbvizmark,.nbcodemark');
            if (!m) return 10;
            var c = getComputedStyle(m), w = parseFloat(c.width) || 10;
            return (c.transform.indexOf('0.707') >= 0 ? w * 1.4142 : w);
          };
          var a = ext(pv), b = ext(cl);
          var fl = (parseFloat(pv.style.top || '0') || 0) + (a + b) / 2 + 3 + (a + b) * 0.05;
          if (nt < fl) nt = Math.round(fl);
        }
        if (Math.abs(nt - now) >= 1) cl.style.top = nt + 'px';
      }
      // 2026-09-27d — ROOM UNDER YOUR OWN CELL.
      // The reading line is fixed (placeCursor), so the last mark — the strip
      // JupyterLab leaves you to add a cell, "your own cell" — can only become
      // the reading position if the document scrolls far enough to bring that
      // strip up onto the line. Without room under it the scroll ran out with
      // the strip at the bottom edge of the window (measured: mark at 846 of a
      // rail ending at 870, nothing below it). An empty block is hung after
      // the footer, INSIDE the scroller's content — not padding on the
      // scroller, which is the zoom rule of STRUKTUR §4 — sized so that the
      // furthest scroll puts the footer's middle exactly on the line. It is
      // re-measured every pass and only rewritten when it is off by > 1 px, so
      // it cannot feed back into the layout it is measured against.
      // 2026-09-28 (Paket 6, Struktur) — THE STRIP IS AS WIDE AS THE COLUMN.
      // JupyterLab indents "Click to add a cell." by the prompt's width, so
      // its hover box started 87 px right of the cells and stopped short of
      // them: a target that did not look like the column it adds to. It is
      // laid over the cell column exactly — left edge and width of the cells,
      // read off the page every pass (full screen, side bar, window size),
      // and only written when it is more than a pixel off.
      function footWide(sc){
        var foot = byCls(sc, 'jp-Notebook-footer');
        if (!foot) return;
        // E22.1b: the cells of the column = elements of class jp-Cell whose
        // parent is the notebook or the windowed viewport (as the selector)
        var cs = allCls(sc, 'jp-Cell').filter(function(c){ var pp = c.parentElement;
          return !!pp && (pp.classList.contains('jp-Notebook') || pp.classList.contains('jp-WindowedPanel-viewport')); });
        var cell = null;
        for (var i = cs.length - 1; i >= 0; i--)
          if (cs[i].getBoundingClientRect().width > 40) { cell = cs[i]; break; }
        if (!cell) return;
        var fr = foot.getBoundingClientRect(), cr = cell.getBoundingClientRect();
        if (!(fr.width > 0)) return;
        var ml = parseFloat(getComputedStyle(foot).marginLeft) || 0;
        var wantL = Math.round(ml + (cr.left - fr.left)), wantW = Math.round(cr.width);
        if (Math.abs(wantL - ml) > 1) foot.style.marginLeft = wantL + 'px';
        if (Math.abs(wantW - fr.width) > 1) {
          foot.style.boxSizing = 'border-box';
          foot.style.maxWidth = 'none';
          foot.style.width = wantW + 'px';
        }
      }
      function footAir(host){
        var sc = scroller(host);
        if (!sc) return;
        footWide(sc);
        var air = null;                                               // E22.1b: a child, not a walk
        for (var ai = 0; ai < sc.children.length; ai++)
          if (sc.children[ai].classList.contains('nbfoot-air')) { air = sc.children[ai]; break; }
        if (!vertOn()) { if (air && air.style.height !== '0px') air.style.height = '0px'; return; }
        var map = host.querySelector('.nbmap');
        var y0 = parseInt(host.dataset.railY0 || '0', 10) || 0;
        var foot = byCls(sc, 'jp-Notebook-footer')
                || byCls(sc, 'jp-WindowedPanel-footer');
        if (!map || !(y0 > 0) || !foot) return;
        var fr = foot.getBoundingClientRect();
        if (!(fr.height > 2)) return;
        var z = pageZoom(), scR = sc.getBoundingClientRect();
        var line = map.getBoundingClientRect().top + y0;
        var F = sc.scrollTop + (fr.top + fr.height / 2 - scR.top) / z;
        var needMax = F - (line - scR.top) / z;
        // 2026-09-29 (E8.6, Applikation + Struktur) — THE RANGE ENDS ON "YOUR
        // OWN CELL". The footer's middle was brought onto the line, but the
        // rail puts the YOC mark at least one mark's air below the last own
        // cell (vertLayout) — measured with an own cell and the panel wide:
        // at the furthest scroll "Own cell 1" was lit and the YOC mark stood
        // 40 px under the cursor, out of reach. The range now runs until the
        // YOC mark itself is on the line (rail = document, 1:1), and no
        // further: the air is sized to exactly that.
        var yocN = host.querySelector('.nbmap-node.last.cell') || host.querySelector('.nbmap-node.cell');
        if (yocN && yocN.offsetTop > y0) needMax = Math.max(needMax, (yocN.offsetTop - y0) / z);
        // E9.2: and on past it by the same air as above the title
        needMax += (window.__nbAirX || 0);
        if (!air) {
          air = document.createElement('div');
          air.className = 'nbfoot-air';
          air.setAttribute('aria-hidden', 'true');
          air.style.cssText = 'height:0px;margin:0;padding:0;border:0;'
                            + 'pointer-events:none;flex:none;';
          sc.appendChild(air);
        }
        if (air.nextElementSibling) sc.appendChild(air);   // always the last
        var cur = parseFloat(air.style.height) || 0;
        var want = Math.max(0, Math.round(cur + needMax
                                          - (sc.scrollHeight - sc.clientHeight)));
        if (Math.abs(want - cur) > 1) air.style.height = want + 'px';
      }
      // 2026-09-28 (Eilauftrag E4.4, Struktur) — ROOM ABOVE THE TITLE.
      // The reading line is the title mark's height, taken at the lens it was
      // measured at (K2.5). Zoomed OUT, the title card is smaller and sits
      // higher: at the very top of the document it stood above the line, and
      // the cursor could only land further down. The foot has its air
      // (.nbfoot-air); the head gets the same: a spacer before the document,
      // exactly as tall as the title card's middle is short of the line with
      // the page at the top. Zoomed in (or at the measuring lens) it is 0.
      function headAir(host){
        var sc = scroller(host);
        if (!sc) return;
        var air = sc.querySelector(':scope > .nbhead-air');
        var cur = air ? (parseFloat(air.style.height) || 0) + (parseFloat(air.style.marginTop) || 0) : 0;
        var need = 0;
        // only at a lens other than the one the line was measured at: there
        // the line is the title's height by definition (need 0), and the
        // line is re-measured WITH the air — measuring it there fed the air
        // back into the line and the two grew without end (mock, test_js)
        var zAt = parseInt(host.dataset.railZ || '0', 10) || 0;
        // 2026-09-30 (E9.2, Struktur + Applikation) — AIR ABOVE THE TITLE,
        // ALWAYS. The reader can scroll past the title upwards (and past
        // "Your own cell" downwards, footAir): AIRX more than the line needs.
        // The marker runs on into it; the lanes (track, XP) keep to title …
        // end, they are drawn from the marks. railY0n is measured WITHOUT
        // this air (vertGauge subtracts it), so it cannot feed back.
        // 2026-10-01 (E12.2, Struktur + Applikation) — NO AIR ANY MORE. The
        // range runs from "Title" on the reading height to "Your own cell" on
        // it (user, E12.2 — replaces E9.2); the title is where the marker
        // spawns (open, Play/Run All, Reset: __nbTopAt). AIRX stays as a name
        // for its readers (footAir, maxTop) and is 0.
        var AIRX = 0;
        window.__nbAirX = AIRX;
        var base = 0;
        if (vertOn() && zAt) {
          var map = host.querySelector('.nbmap');
          var y0 = parseInt(host.dataset.railY0 || '0', 10) || 0;
          var tn = host.querySelector('.nbmap-node.title');
          var card = tn ? targetEl(tn) : null;
          if (!map || !(y0 > 0) || !card) return;
          var cr = card.getBoundingClientRect();
          if (!(cr.height > 4)) return;
          var scR = sc.getBoundingClientRect();
          var line = map.getBoundingClientRect().top + y0 - scR.top;
          // the card's middle in document pixels, without the air
          var C = sc.scrollTop + (cr.top + cr.height / 2 - scR.top) - cur;
          // E10.7: the line is taken at 100 % — above it (a lens > 100 %)
          // the card stands BELOW the line at the top; then there is no
          // extra air, the page opens further down (over < 0)
          var over = Math.round(line - C);
          // E12.2: a lens > 100 % (over < 0) — the card stood below the line
          // at the top; the head now pulls the page UP by that much (negative
          // margin), so scrollTop 0 is the title on the line there too
          base = over;
          need = base + AIRX;
          window.__nbTopAt = 0;
        }
        if (!air) {
          if (!need) return;
          air = document.createElement('div');
          air.className = 'nbhead-air';
          air.setAttribute('aria-hidden', 'true');
          air.style.cssText = 'height:0px;margin:0;padding:0;border:0;'
                            + 'pointer-events:none;flex:none;';
          sc.insertBefore(air, sc.firstChild);
        }
        if (air.previousElementSibling) sc.insertBefore(air, sc.firstChild);  // always the first
        if (Math.abs(need - cur) > 1) {
          air.style.height = Math.max(0, need) + 'px';
          air.style.marginTop = Math.min(0, need) + 'px';
          // what stood on the line stays there: the page grows above it
          if (sc.scrollTop > 0) sc.scrollTop = Math.max(0, sc.scrollTop + need - cur);
          // E9.2: the first time, the page opens with the title on the line
          // (the new air is above it, reachable by scrolling up)
          else if (!cur) sc.scrollTop = window.__nbTopAt || 0;
        }
      }
      // 2026-09-29 (E6.11, Struktur) — THE PIPS BESIDE THE CHAPTER MARK.
      // A chapter's tally (`.nbchapstat`, rows `.nbpip-row` with their
      // `.nbpip-lab` — Python's markup, E6 contract) no longer hangs under the
      // chapter's name: it stands beside the chapter symbol, its middle level
      // with it. Only the place is set here (inline, !important, because the
      // old rules are); size and look are the stylesheet's.
      // 2026-09-29e (E7.1, Struktur) — ALWAYS ON THE RIGHT OF THE SYMBOL.
      // On the left (E6.11) the tally took the name's room ("Chapter 3:
      // Addition and…"). Now it stands a gap right of the symbol, and the
      // name has its whole column between the cursor and the lane again, as
      // before E6.11/11b (applyGui's --nbvert-labx/--nbvert-lab, untouched
      // here). What the tally needs to the right of the lane — in units of
      // K — goes to applyGui (window.__nbPipNeedK): where the right half of
      // the panel is too narrow, the lane moves left instead of the pips
      // being cut or pushed over the edge.
      function pipPlace(host){
        var K = window.__nbK || 1, need = 0, circ = 0;
        var axis = parseFloat(getComputedStyle(document.documentElement)
                              .getPropertyValue('--nbvert-axis')) || 0;
        [].forEach.call(host.querySelectorAll('.nbmap-node.chap'), function(n){
          if (n.classList.contains('nbgone')) return;
          var st = n.querySelector('.nbchapstat'), dot = n.querySelector('.nbchapdot');
          if (!st || !dot) return;
          var nr = n.getBoundingClientRect(), dr = dot.getBoundingClientRect();
          if (!(dr.width > 0) || !(st.offsetWidth > 0)) return;
          var gap = Math.round(10 * K);
          var L = Math.round(dr.right - nr.left + gap);
          var T = Math.round(dr.top + dr.height / 2 - nr.top);
          impSet(st, {left: L + 'px', top: T + 'px', width: 'auto', right: 'auto',
                      transform: 'translateY(-50%)', 'flex-direction': 'column',
                      'align-items': 'flex-start', 'justify-content': 'center',
                      'pointer-events': 'auto'});
          // E8.18: a pip and its word are a way to the exercise — they take the pointer
          [].forEach.call(st.querySelectorAll('.nbpip-row, .nbpip-row > *'), function(r){
            impSet(r, {'pointer-events': 'auto', cursor: 'pointer'});
          });
          // from the lane to the tally's far end, plus 4 px of air — with
          // its labels only while they are shown (E7.4: nbnotext hides them)
          var d0 = (dr.right - nr.left - axis) + gap + 4 * K;
          var ps = st.querySelector('.ps');
          var pw = ps ? ps.getBoundingClientRect().width * 1.42 : 26 * K;
          if (d0 + pw > circ) circ = d0 + pw;
          if (!host.classList.contains('nbnotext')) {
            var nd = d0 + st.offsetWidth;
            if (nd > need) need = nd;
          }
          // E6.11b's clamp on the name is undone: the column is applyGui's
          var lab = n.querySelector(':scope > .nbmap-lab');
          if (lab && lab.style.getPropertyValue('max-width')) {
            ['left', 'width', 'max-width'].forEach(function(k){ lab.style.removeProperty(k); });
          }
        });
        if (circ > 0) {
          var ck = Math.ceil(circ / K);
          if (Math.abs(ck - (window.__nbPipCircK || 0)) > 1) {
            window.__nbPipCircK = ck;
            try { if (window.__nbApplyGui) window.__nbApplyGui(host); } catch (e) {}
          }
        }
        if (need > 0) {
          var nk = Math.ceil(need / K);
          if (Math.abs(nk - (window.__nbPipNeedK || 0)) > 1) {
            window.__nbPipNeedK = nk;
            try { if (window.__nbApplyGui) window.__nbApplyGui(host); } catch (e) {}
          }
        }
      }
      function followDoc(host){
        var own = !window.__nbMemo;                 // E22.9: one look per follow (10-rail-host memo)
        if (own) window.__nbMemo = {};
        try { followDoc0(host); } finally { if (own) window.__nbMemo = null; }
      }
      function followDoc0(host){
        if (vertOn()) {
          var src0 = activeSrc();
          if (src0) { vertGauge(host, vertLayout(host, src0)); vertPlace(host, src0); }
          try { pipPlace(host); } catch (e) {}
          headAir(host);
          footAir(host);
          markCentre(host);
          footAlign(host);
          return;
        }
        pad(host);
        if (Date.now() - (window.__nbrailHerePin || 0) < 1400) { markCentre(host); return; }
        var x = docPos(host);
        if (x !== null) centreOn(host, x);
        markCentre(host);
      }


      // ======================================================================
      // 2026-09-28 (R3 · Paket 20, Struktur + Applikation) — THE TIMELINE AS A
      // BOOKMARK. Where the reader stood last (the mark lit on the reading
      // line, once they have scrolled away from the title and stayed there
      // two seconds) is kept in this browser per notebook
      // (`digichemjn.bookmark.<id>`) and carries a 🔖 on the timeline — also
      // after a new run, which starts at the top (E4.3). A click on that mark
      // goes there as on any mark; B in keyboard mode does the same.
      function bmKey(){
        var id = nbId();
        return id ? 'digichemjn.bookmark.' + id : null;
      }
      function bmGet(){ var k = bmKey(); try { return k ? localStorage.getItem(k) : null; } catch (e) { return null; } }
      // 2026-10-05 (E22.1, Applikation) — THE 🔖 COSTS NOTHING WHILE ONE
      // READS. The tick (1 s) wrote the place as soon as the lit mark had
      // stood two ticks, and on that tick it also walked every mark, read
      // two boxes and moved the 🔖: measured v1.63 (1 CPU) 9–14 ms on the
      // tick 2 s after every scroll stop, plus the localStorage write — and
      // it came while the panel's own passes after a scroll still ran. Now
      // the tick only REMEMBERS the candidate (one query, no layout, no
      // write). The place is written — and the 🔖 moved — when the browser is
      // idle (requestIdleCallback), at most every 5 s, and at once when the
      // page is hidden or left (visibilitychange, pagehide). What is
      // written is what it was: the lit mark after it stood ≥ 2 s.
      function bmCand(){
        var h = document.getElementById(HOST_ID);
        if (!h || !h.classList.contains('ready')) return null;
        var here = h.querySelector('.nbmap-node.here'), t = here && here.getAttribute('data-target');
        var busy = document.getElementById('nbload') && !document.getElementById('nbload').classList.contains('nbload-out');
        return (t && !here.classList.contains('title') && !busy) ? t : null;
      }
      function bmTick(){
        bmKeep();
        var t = bmCand();
        if (!t) return;
        if (window.__nbBmCand === t) {
          if (++window.__nbBmN === 2) bmSoon();
        } else { window.__nbBmCand = t; window.__nbBmN = 0; }
      }
      function bmSoon(){
        if (window.__nbBmIdle) return;
        var wait = Math.max(0, 5000 - (Date.now() - (window.__nbBmAt || 0)));
        var go = function(){
          window.__nbBmIdle = 0;
          if (window.requestIdleCallback) window.__nbBmIdle = window.requestIdleCallback(function(){ window.__nbBmIdle = 0; bmSave(); }, {timeout: 4000});
          else bmSave();
        };
        window.__nbBmIdle = -1;
        if (wait > 0) setTimeout(go, wait); else go();
      }
      function bmSave(){
        var k = bmKey(), t = window.__nbBmCand;
        if (!k || !t || window.__nbBmN < 2) return;
        window.__nbBmAt = Date.now();
        var at = bmGet();
        if (at !== t) { try { localStorage.setItem(k, t); } catch (e) {} }
        bmMark();
      }
      window.__nbBmSave = bmSave;
      // the 🔖 on the mark of the stored place — only where it is not yet
      // 2026-10-05 (E22.1b, Applikation) — READ FIRST, THEN WRITE, AND NO
      // MEASURING OF A SIGN THAT IS NOT DRAWN. The loop took the old 🔖 away
      // (a write) and then read two boxes for the new one: a forced layout of
      // the whole Lab in the reader's quiet seconds — profile v1.64 probe,
      // 1 CPU: 24–49 ms of getBoundingClientRect in bmSave, and with what the
      // change set going 35–112-ms tasks, 1–2 s after a scroll stopped (the
      // idle save). The sign itself is not drawn since E7.3 (14-e7:
      // `.nbbm-ic{display:none}`; the place is kept, B goes there). Now: all
      // reads first; the place of the sign is read only if it is drawn
      // (asked once per sign: bmDrawn); then the writes, only where a class or
      // a sign has to change. And once a sign was found not drawn, the page
      // keeps none (`__nbBmHidden`): adding and taking away a hidden sign and
      // its class cost a whole style pass of the Lab each time the place
      // moved (35–48 ms after the save, measured) and showed nothing.
      function bmDrawn(ic){
        if (ic.__nbDrawn === undefined) ic.__nbDrawn = getComputedStyle(ic).display !== 'none';
        if (!ic.__nbDrawn) window.__nbBmHidden = NBRAIL_VERSION;      // per build: a new one asks again
        return ic.__nbDrawn;
      }
      function bmClear(h){
        [].forEach.call(h.querySelectorAll('.nbbm-ic'), function(x){ x.remove(); });
        [].forEach.call(h.querySelectorAll('.nbmap-node.nbbm'), function(x){ x.classList.remove('nbbm'); });
      }
      function bmLeft(n){
        var mk = n.querySelector('.nbsect,.nbsubdot,.nbchapdot,.nbvizmark,.nbrail-dot,.nbcodemark');
        var nr = n.getBoundingClientRect(), mr = mk ? mk.getBoundingClientRect() : null;
        return mr && mr.width ? Math.round(mr.left - nr.left - 20 * (window.__nbK || 1)) + 'px' : '2px';
      }
      function bmMark(){
        var h = document.getElementById(HOST_ID);
        if (!h) return;
        if (window.__nbBmHidden === NBRAIL_VERSION) { if (h.querySelector('.nbbm-ic, .nbmap-node.nbbm')) bmClear(h); return; }
        var at = bmGet(), todo = [];
        // reads
        [].forEach.call(h.querySelectorAll('.nbmap-node'), function(n){
          var on = !!at && n.getAttribute('data-target') === at, ic = null;
          for (var k = 0; k < n.children.length; k++)
            if (n.children[k].classList.contains('nbbm-ic')) { ic = n.children[k]; break; }
          var L = (on && ic && bmDrawn(ic)) ? bmLeft(n) : null;
          if (on !== !!ic || on !== n.classList.contains('nbbm') || (L && ic.style.left !== L)) todo.push([n, on, ic, L]);
        });
        // writes
        todo.forEach(function(t){
          var n = t[0], on = t[1], ic = t[2];
          if (on && !ic) {
            ic = document.createElement('span'); ic.className = 'nbbm-ic';
            ic.textContent = '🔖'; ic.title = nbL('where you stopped reading — B in keyboard mode', 'wo Sie aufgehört haben zu lesen; B im Tastaturmodus');
            ic.style.cssText = 'position:absolute;left:2px;top:50%;transform:translateY(-50%);'
              + 'font-size:calc(12px * var(--nbk, 1));line-height:1;pointer-events:none;z-index:3;';
            n.appendChild(ic);                   // placed by the next tick (bmKeep), if it is drawn
          } else if (!on && ic) ic.remove();
          if (on && ic && t[3] && ic.style.left !== t[3]) ic.style.left = t[3];
          if (n.classList.contains('nbbm') !== on) n.classList.toggle('nbbm', on);
        });
      }
      // every tick, cheaply: the 🔖 is where the stored place is (a new run
      // rebuilds the marks) and stands left of its mark (lens and width move
      // it) — one query and, at rest, two boxes of a laid-out page
      function bmKeep(){
        var h = document.getElementById(HOST_ID);
        if (!h || !h.classList.contains('ready')) return;
        if (window.__nbBmHidden === NBRAIL_VERSION) { if (h.querySelector('.nbbm-ic, .nbmap-node.nbbm')) bmClear(h); return; }   // E22.1b
        var at = bmGet(), n = h.querySelector('.nbmap-node.nbbm'), ic = n && n.querySelector(':scope > .nbbm-ic');
        if (!at) { if (n) bmMark(); return; }
        if (!n || !ic || n.getAttribute('data-target') !== at || h.querySelectorAll('.nbbm-ic').length !== 1) { bmMark(); return; }
        if (!bmDrawn(ic)) return;                 // E22.1b: not drawn (E7.3) — nothing to place
        var L = bmLeft(n);
        if (ic.style.left !== L) ic.style.left = L;
      }
      // leaving: the place now, whatever the clock says
      var bmLeave = function(){
        if (document.visibilityState && document.visibilityState !== 'hidden' && arguments[0] && arguments[0].type === 'visibilitychange') return;
        var t = bmCand() || window.__nbBmCand, k = bmKey();
        if (t && k && window.__nbBmCand === t && window.__nbBmN >= 2) { try { localStorage.setItem(k, t); } catch (e) {} }
      };
      if (window.__nbBmLeave) {
        document.removeEventListener('visibilitychange', window.__nbBmLeave);
        window.removeEventListener('pagehide', window.__nbBmLeave);
      }
      window.__nbBmLeave = bmLeave;
      document.addEventListener('visibilitychange', bmLeave);
      window.addEventListener('pagehide', bmLeave);
      function bmGo(){
        var h = document.getElementById(HOST_ID), at = bmGet();
        if (!h || !at) return;
        var n = h.querySelector('.nbmap-node[data-target="' + at.replace(/"/g, '') + '"]');
        if (!n) return;
        var ns = [].filter.call(h.querySelectorAll('.nbmap-node'), function(x){ return !x.classList.contains('nbgone'); });
        window.__nbKeyAt = ns.indexOf(n);
        window.__nbKeyNav = true;
        try { n.click(); } finally { window.__nbKeyNav = false; }
      }
      window.__nbBookmarkGo = bmGo;
      if (typeof KBD_ACT !== 'undefined') KBD_ACT.bookmark = bmGo;
      if (window.__nbBmTimer) clearInterval(window.__nbBmTimer);
      window.__nbBmTimer = setInterval(bmTick, 1000);
      // 2026-10-02 (E15.4, Applikation) — THE COVER'S MARKS ANSWER. Hover
      // over a mark of the cover timeline: its row gets `nbtl-hov` (CSS
      // colours and turns it like a panel mark) and `.nbtl-desc`, the last
      // child of `.nbcover-tl`, says what it is: its `b` the name (the row's
      // title, kept as `data-nm` and taken off, so the browser's own tooltip
      // does not say it twice), its `span` Python's `data-desc`; `hidden`
      // while there is nothing to say. A click pins it (`nbtl-pin`: stays
      // when the pointer leaves, another hover shows its own and gives it
      // back); the same mark again lets go, another mark moves the pin.
      function tlShow(tl, r){
        var d = tl.querySelector(':scope>.nbtl-desc');
        if (!d) { d = document.createElement('div'); d.className = 'nbtl-desc'; d.innerHTML = '<b></b> <span></span>'; tl.appendChild(d); }
        if (r && r.title) { r.setAttribute('data-nm', r.title); r.title = ''; }
        d.hidden = !r;
        if (r) { d.firstChild.textContent = r.getAttribute('data-nm') || r.textContent;
                 // E29 P1: the cover's words in the language chosen on it
                 var deC = window.__nbAcct ? window.__nbAcct.lang() === 'de' : !!(window.__nbDe && window.__nbDe());
                 d.lastChild.textContent = r.getAttribute('data-desc') || (r.classList.contains('nbtl-cell') ? (deC ? '\uFF0B Eigene Zelle anlegen' : '\uFF0B Add your cell') : ''); }
      }
      window.__nbTlShow = tlShow;
      function tlEv(ev){
        var t = ev.target, r = t.closest && t.closest('.nbcover-tl .nbtl-row'), tl = r && r.closest('.nbcover-tl'), o = window.__nbTlH, p;
        if (ev.type === 'click' && r && TLF.test(r.className)) return tlFold(tl, r);        // E16.5
        if (ev.type === 'click') {
          if (!r || r.classList.contains('nbtl-cell')) return;    // E16.7: makes a cell (01-jump)
          p = tl.querySelector('.nbtl-pin');
          if (p) p.classList.remove('nbtl-pin');
          if (p !== r) r.classList.add('nbtl-pin');
          return tlShow(tl, p !== r && r);
        }
        if (ev.type === 'pointerout') { if (ev.relatedTarget) return; r = null; }
        if (o === r) return;
        window.__nbTlH = r;
        if (o) { o.classList.remove('nbtl-hov'); p = o.closest('.nbcover-tl'); if (p) tlShow(p, p.querySelector('.nbtl-pin')); }
        if (r) { r.classList.add('nbtl-hov'); tlShow(tl, TLF.test(r.className) ? null : r); }
      }
      if (window.__nbTlOff) window.__nbTlOff();
      window.__nbTlOff = function(a){ ['pointerover', 'pointerout', 'click'].forEach(function(e){ document[(a || 'remove') + 'EventListener'](e, tlEv, true); }); };
      window.__nbTlOff('add');
      // 2026-10-02 (E16.5, Applikation) — TITLE AND GROUPS FOLD THE COVER'S
      // TIMELINE, as their marks fold the document's, and show no card: a
      // click on a group (Introduction, Content, Appendix) hides the rows up
      // to the next group or the end and shows them again; a click on Title
      // hides all but Title and the own-cell mark. `nbtl-shut` on the clicked
      // row; the rows count their folds (`__nbFold`), coverPaint hides them.
      var TLF = /\bnbtl-(title|group)\b/;
      function tlFold(tl, r){
        var rows = [].slice.call(tl.querySelectorAll('.nbtl-row')), t = r.classList.contains('nbtl-title'),
            shut = !r.classList.contains('nbtl-shut'), j, x;
        r.classList.toggle('nbtl-shut', shut);
        for (j = rows.indexOf(r) + 1; j < rows.length; j++) {
          x = rows[j];
          if (x.classList.contains('nbtl-cell') || (!t && /\bnbtl-(group|end)\b/.test(x.className))) break;
          x.__nbFold = Math.max(0, (x.__nbFold || 0) + (shut ? 1 : -1));
        }
        tl.__nbCoverSig = '';
        if (window.__nbCoverPaint) window.__nbCoverPaint();
      }
