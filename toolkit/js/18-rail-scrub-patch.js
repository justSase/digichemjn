      // 2026-10-05 (E22.9 + E22.6, Struktur + Applikation) — THE RAIL FOLLOWS
      // IN THE SAME FRAME, ALSO WHILE A HAND DRIVES THE PAGE. Every gesture that
      // moves the document from our side (thumb, reading-height knob, the
      // wheel over the rail) stamps __nbrailDriving, and for 500 ms after it
      // the scroll handler moved only the marker, never the rail: so the rail
      // was not "pulled back against the hand". But in the vertical layout the
      // rail never pulls the page — it is 1:1 with the document — so the marks
      // simply stood still while the pills ran away (measured v1.63, real Lab,
      // cyber dark, post-rAF probe: thumb drag 150 px → marks up to 746 px off
      // their pills; knob drag 100 px → 95–102 px; and after the thumb was
      // let go the rail stayed 112 px off until the next sync, which nothing
      // asked for). The rail only LEADS when the reader scrolled the rail itself
      // (its own scroll, not ours: __nbMapLeadAt, set in __nbrailMapScroll);
      // then the document follows it (scrubTo) and the rail is left alone.
      // In the horizontal banner the old rule stays (the rail is parked there).
      function railLeads(){
        if (Date.now() - (window.__nbrailDriving || 0) >= 500) return false;
        if (!vertOn()) return true;
        return Date.now() - (window.__nbMapLeadAt || 0) < 400;
      }
      // E22.9 — NO HOVER GROWTH WHILE THINGS MOVE. A mark under the pointer
      // grows (hover) and shrinks again; when the zoom or a drag slides the
      // marks under a resting pointer, one after another grows for a moment
      // (the reader's video: "the title diamond is big for a moment"; measured
      // Ctrl+wheel on the rail: the mark under the pointer 11.3 → 23.8 px →
      // 12.3 px within the gesture). While a gesture runs and 300 ms after it
      // the marks take no pointer (so :hover cannot match) and the host says
      // so: `#nbpanel-root[data-nbmoving]` (+ class `nbmoving`) — the hook
      // CSS asked for (chronicle 05.10.): no arrival pulse `nbm-glow`, no
      // hover growth while it stands.
      // (On the NODES, inline: 06-marks gives every shown node
      // `pointer-events:auto`, which a `none` on their parent does not beat.)
      function nodesTakePointer(h, yes){
        var ns = h ? h.querySelectorAll('.nbmap-node') : [];
        for (var i = 0; i < ns.length; i++) {
          var want = yes ? '' : 'none';
          if (ns[i].style.pointerEvents !== want) ns[i].style.pointerEvents = want;
        }
      }
      function moving(ms){
        var h = document.getElementById(HOST_ID);
        if (!h) return;
        clearTimeout(window.__nbMovT);
        if (!h.classList.contains('nbmoving')) { h.classList.add('nbmoving'); h.setAttribute('data-nbmoving', '1'); nodesTakePointer(h, false); }
        else if (!window.__nbMovLock) nodesTakePointer(h, false);
        window.__nbMovLock = true;
        // the marks take the pointer again as soon as the HAND moves (not
        // after a timer: a pointer resting where the zoom left it would make
        // the mark that slid under it grow 300 ms later, unasked). A move with
        // a button held is a drag of ours (pointer capture), not a hand going
        // to a mark.
        if (!window.__nbMovFree) {
          var free = function(e){
            if (e && e.buttons) return;
            if (e && !(e.movementX || e.movementY)) return;
            window.removeEventListener('pointermove', free, true);
            if (window.__nbMovFree === free) window.__nbMovFree = null;
            window.__nbMovLock = false;
            nodesTakePointer(document.getElementById(HOST_ID), true);
          };
          window.__nbMovFree = free;
          window.addEventListener('pointermove', free, true);
        }
        window.__nbMovT = setTimeout(function(){
          var h2 = document.getElementById(HOST_ID);
          if (h2) {
            h2.classList.remove('nbmoving'); h2.removeAttribute('data-nbmoving');
            // the glyphs' own transitions back (11-rail-layout glyphZoom held them at 0 s)
            [].forEach.call(h2.querySelectorAll('.nbmap-node [style*="transition-duration"]'), function(g){
              g.style.removeProperty('transition-duration'); });
          }
        }, ms || 300);
      }
      window.__nbMoving = moving;
      // E22.6 — the same for a page moved INSIDE a frame callback (the wheel's
      // glide, a landing): its scroll event comes one frame later, so without
      // this every frame of the glide drew the rail one step behind the page
      // (stamped: the scroll event of that very move, a frame later, then
      // finds the rail already there and does not lay it out a second time —
      // two layouts a frame cost the wheel 8–10 ms a frame on one CPU)
      window.__nbFollowNow = function(){
        if (!vertOn()) return;
        var h = document.getElementById(HOST_ID);
        if (!h || !h.classList.contains('ready')) return;
        // 2026-10-05 (E22.1b) — a frame that did not move the page asks for
        // nothing: the glide's last frames step under a pixel and the page
        // stands (scrollTop unchanged), its final frame lands where the page
        // already is — each of them was a whole follow (profile v1.64 probe:
        // `glide` → followDoc, a 63–77-ms task at the very moment the page
        // came to rest). Followed at this scrollTop within 250 ms: done.
        if (followedAlready(h, 250)) return;
        try { followDoc(h); } catch (e) {}
        var sc = scroller(h);
        window.__nbFollowed = sc ? sc.scrollTop : null;
        window.__nbFollowedAt = performance.now();
      };
      function followedAlready(h, ms){
        if (window.__nbFollowed === null || window.__nbFollowed === undefined) return false;
        if (performance.now() - (window.__nbFollowedAt || 0) > (ms || 60)) return false;
        var sc = scroller(h);
        return !!sc && sc.scrollTop === window.__nbFollowed;
      }

      // ---- the timeline as a scrubber -------------------------------------
      // Dragging or wheeling the timeline scrolls the DOCUMENT to the matching
      // place, which in turn moves the marker: one position, two ways to set it.
      function scrubTo(host){
        var map = host.querySelector('.nbmap');
        var inner = host.querySelector('.nbmap-inner');
        if (!map || !inner) return;
        if (vertOn()) {
          // one to one: the rail's scroll IS the document's scroll
          var sc0 = scroller(host);
          if (!sc0) return;
          window.__nbrailDriving = Date.now();
          sc0.scrollTop = Math.round(map.scrollTop / pageZoom());
          return;
        }
        var x = map.scrollLeft + map.clientWidth / 2;
        var nodes = inner.querySelectorAll('.nbmap-node[data-target],.nbmap-node[data-sel]');
        var mid = function(n){ return n.offsetLeft + n.offsetWidth / 2; };
        var prev = null, next = null;
        for (var i = 0; i < nodes.length; i++) {
          if (!targetEl(nodes[i])) continue;
          if (mid(nodes[i]) <= x) prev = nodes[i];
          else { next = nodes[i]; break; }
        }
        var el0 = prev && targetEl(prev);
        var el1 = next && targetEl(next);
        var sc = scroller(host);
        if (!sc) return;
        var yOf = function(el){
          var r = el.getBoundingClientRect(), b = sc.getBoundingClientRect();
          return sc.scrollTop + (r.top - b.top);
        };
        var y;
        if (el0 && el1) {
          var t = (x - mid(prev)) / Math.max(1, mid(next) - mid(prev));
          y = yOf(el0) + Math.max(0, Math.min(1, t)) * (yOf(el1) - yOf(el0));
        } else if (el0) { y = yOf(el0); }
        else if (el1) { y = yOf(el1); }
        else return;
        y -= ((railOf(host) || host).getBoundingClientRect().height + 24);
        window.__nbrailDriving = Date.now();
        sc.scrollTop = Math.max(0, Math.round(y));
        markCentre(host);
      }
      function scroller(host){
        var src = activeSrc();
        var p = src && (src.closest('.jp-NotebookPanel') || src.closest('.jp-Notebook'));
        if (!p) return null;
        return p.querySelector('.jp-WindowedPanel-outer') ||
               p.querySelector('.jp-Notebook') || p;
      }

      function follow(host, force){
        if (vertOn()) return;              // the rail already stands where the document does
        var map = host.querySelector('.nbmap');
        if (!map) return;
        var cur = map.querySelector('.nbmap-node.is-current')
               || map.querySelector('.nbmap-node.task');
        if (!cur) return;
        var key = cur.getAttribute('data-task') || '';
        var same = host.getAttribute('data-follow') === key;
        if (!force && same) return;
        if (same && host.getAttribute('data-manual') === '1') return;
        host.setAttribute('data-follow', key);
        host.removeAttribute('data-manual');       // a new exercise takes over again
        window.__nbrailSelfScroll = true;
        window.__nbrailSelfAt = Date.now() + 500;   // the smooth scroll below runs on
        setTimeout(function(){ window.__nbrailSelfScroll = false; }, 700);
        var want = cur.offsetLeft - map.clientWidth / 2 + cur.offsetWidth / 2;
        want = Math.max(0, Math.min(want, map.scrollWidth - map.clientWidth));
        // smooth only here; the track itself scrolls instantly, otherwise the
        // wheel keeps fighting a running animation and the bar feels stuck
        if (map.scrollTo) map.scrollTo({left: want, behavior: 'smooth'});
        else map.scrollLeft = want;
      }

      // The timeline IS the progress bar: the green line runs over its whole
      // width, filled to the share of exercises answered correctly, and every
      // chapter or section dot it has passed turns green with it. Full width means
      // every exercise done — a skipped or bypassed one does not move it.
      // How far you have come is a POSITION on the timeline: the green line runs
      // to the chapter you have reached — the last one unlocked — and stops there.
      // The exercise you are on sits just beyond it, marked by the green ring.
      // How far a track has come, as a NODE on the timeline:
      //   · every exercise solved so far is passed;
      //   · the exercise you are on is reached — the line ends on its circle;
      //   · but if the one before it was skipped or given up, the chapter opened
      //     without a solution, so the line stops at that chapter's dot and the
      //     circle stays outside it.
      // Null means the whole track is finished, and the line covers everything.
      // Returns where the lane ends AND why. When an exercise was skipped or given
      // up, the stretch from that circle to the chapter it opened is not progress
      // you made — it is a door you walked past, so it is drawn in the colour of
      // that circle's ring (amber for skipped, red for given up) instead of green.
      // The lane always runs UP TO the circle you are standing at — the one with
      // the open padlock. How the last stretch is coloured says how you got there:
      // green if the exercise before it was answered, amber if it was skipped, red
      // if it was given up, purple if only its coding route was solved.
      // WHERE THE GREEN ENDS.
      //
      // At the circle with the open padlock — the one you are standing at — and
      // nowhere else. How you got there does not change it: a skipped or given-up
      // exercise opened the next chapter, so the next chapter IS open, and a
      // progress bar that says otherwise contradicts the padlock right next to
      // it. The circle keeps its amber or red ring, which is where that belongs:
      // on the exercise, not on the road.
      // (Not `.is-current`: that marks the ANSWER route's open padlock, and the
      // purple lane needs the same question asked about the coding route. The
      // walk below answers it for whichever route it is given.)
      function reachedNode(inner, isSolved){
        var nodes = inner.querySelectorAll('.nbmap-node'), last = null;
        for (var i = 0; i < nodes.length; i++) {
          var n = nodes[i];
          if (!n.classList.contains('task')) continue;
          var d = n.querySelector('.nbrail-dot');
          if (!d) continue;
          last = n;
          if (isSolved(d) || d.classList.contains('st-skip') ||
              d.classList.contains('st-fail') || d.classList.contains('st-code')) continue;
          return {node: n, via: null, kind: ''};
        }
        return {node: null, via: null, kind: ''};
      }

      // Where the line begins and where it ends. Not the box: the MARKERS. The
      // track starts on the first section bar and stops on the last chapter dot
      // or exercise circle, and the gap in front of every further section bar
      // reaches back exactly to the previous marker — so Introduction, Content and
      // Appendix each read as one block of line with nothing sticking out.
      function extent(inner){
        var nodes = inner.querySelectorAll('.nbmap-node');
        if (!nodes.length) return null;
        var mid = function(n){ return n.offsetLeft + n.offsetWidth / 2; };
        var x0 = Math.round(mid(nodes[0]));
        var x1 = Math.round(mid(nodes[nodes.length - 1]));
        var sx0 = x0 + 'px', sw = Math.max(0, x1 - x0) + 'px';
        if (inner.style.getPropertyValue('--rail-x0') !== sx0)
          inner.style.setProperty('--rail-x0', sx0);
        if (inner.style.getPropertyValue('--rail-w') !== sw)
          inner.style.setProperty('--rail-w', sw);
        // The grey track runs through everything, but PROGRESS only starts where
        // there is something to solve: at the section bar of the block that holds
        // the first exercise. Introduction has no exercises, so its line stays grey
        // instead of being filled by a progress nobody made there.
        var f0 = x0, first = -1, j;
        for (j = 0; j < nodes.length; j++)
          if (nodes[j].classList.contains('task')) { first = j; break; }
        if (first > -1) {
          for (j = first; j >= 0; j--)
            if (nodes[j].classList.contains('sect')) { f0 = Math.round(mid(nodes[j])); break; }
        }
        var sf0 = f0 + 'px';
        if (inner.style.getPropertyValue('--fill-x0') !== sf0)
          inner.style.setProperty('--fill-x0', sf0);
        // The dark "you have not been here yet" ink belongs to the block that holds
        // the exercises. Introduction and Appendix are not progress territory, so
        // their stretch of line keeps the light grey.
        var f1 = x1;
        if (first > -1) {
          var seen = false;
          for (j = 0; j < nodes.length; j++) {
            if (nodes[j].classList.contains('sect')) {
              if (seen) { break; }                     // the next block starts here
              if (Math.round(mid(nodes[j])) === f0) seen = true;
              continue;
            }
            if (seen) f1 = Math.round(mid(nodes[j]));
          }
        }
        var ahead = inner.querySelector('.nbmap-ahead');
        if (ahead) {
          var al = f0 + 'px', aw = Math.max(0, f1 - f0) + 'px';
          if (ahead.style.left !== al) ahead.style.left = al;
          if (ahead.style.width !== aw) ahead.style.width = aw;
        }
        // Where the line is interrupted: from the CENTRE of the last marker of one
        // block to the CENTRE of the next section's bar. The first section opens no
        // gap — there is no line in front of it.
        var want = [], prev = null;
        // the banner's line is continuous too — see vertGauge()
        var bars = inner.querySelectorAll('.nbmap-gap');
        var fills = inner.querySelectorAll('.nbmap-fill');
        var anchor = fills.length ? fills[fills.length - 1] : null;
        for (var k = 0; k < want.length; k++) {
          var bar = bars[k];
          if (!bar) {
            bar = document.createElement('span');
            bar.className = 'nbmap-gap';
            // right behind the fills: above them in paint order, below the nodes
            if (anchor && anchor.nextSibling) inner.insertBefore(bar, anchor.nextSibling);
            else inner.appendChild(bar);
          }
          if (bar.style.top)    bar.style.top = '';      // a vertical leftover
          if (bar.style.height) bar.style.height = '';
          var L = want[k][0] + 'px', W = Math.max(0, want[k][1] - want[k][0]) + 'px';
          if (bar.style.left !== L) bar.style.left = L;
          if (bar.style.width !== W) bar.style.width = W;
        }
        for (var m = want.length; m < bars.length; m++) bars[m].remove();
        return {x0: x0, x1: x1, f0: f0, f1: f1};
      }

      function gauge(host){
        if (vertOn()) return;              // the vertical lanes are drawn by vertGauge
        var inner = host.querySelector('.nbmap-inner');
        if (inner) inner.querySelectorAll('.nbmap-fill').forEach(function(e){
          if (e.style.height) e.style.height = '';
          if (e.style.top)    e.style.top    = '';
        });
        var fill  = host.querySelector('.nbmap-fill:not(.code)');
        var code  = host.querySelector('.nbmap-fill.code');
        if (!inner || !fill) return;
        var nodes = inner.querySelectorAll('.nbmap-node');
        var ext = extent(inner);
        // Appendix and Introduction are not progress territory: the lanes live
        // between the first and the last marker of the block that holds the
        // exercises, and nothing outside it is ever filled.
        var x0 = ext ? ext.f0 : 0, span = ext ? ext.f1 : 0;
        function endOf(node){
          return node ? Math.round(node.offsetLeft + node.offsetWidth / 2) : span;
        }
        var gRes = reachedNode(inner, function(d){
          return d.classList.contains('st-ans') || d.classList.contains('st-both'); });
        var pRes = reachedNode(inner, function(d){
          return d.classList.contains('st-code') || d.classList.contains('st-both'); });
        var green = gRes.node, purple = pRes.node;
        // The amber/red stripe is gone. A skip or a give-up is a fact about
        // that ONE exercise, and its circle already says so with an amber or a
        // red ring. Painting the road behind it as well said the opposite of the
        // open padlock two circles along: the chapter IS open, so the bar that
        // leads to it is green like any other.
        var tail = host.querySelector('.nbmap-fill.tail');
        if (tail && tail.style.opacity !== '0') {
          tail.style.width = '0px'; tail.style.height = '0px'; tail.style.opacity = '0';
        }
        var w = Math.min(endOf(green), span), cw = Math.min(endOf(purple), span);
        // The green lane ends ON its marker. The purple one ends AROUND its marker:
        // it runs past the centre by the marker's own radius, and that marker gets
        // the same glow, so the lane closes around the dot instead of stopping in
        // the middle of it.
        var pm = purple && purple.querySelector(
                   '.nbrail-dot,.nbchapdot,.nbsubdot,.nbsect');
        var cwEnd = cw + (pm ? pm.offsetWidth / 2 + 3 : 0);
        // the fills start where the track starts, so their width is the distance
        // travelled along it — not the distance from the edge of the box
        var fw = Math.max(0, w - x0) + 'px', cwp = Math.max(0, cwEnd - x0) + 'px';
        if (fill.style.width !== fw) fill.style.width = fw;
        if (code && code.style.width !== cwp) code.style.width = cwp;
        // every marker takes the colour of the lanes that have reached it
        for (var j = 0; j < nodes.length; j++) {
          var c = nodes[j].offsetLeft + nodes[j].offsetWidth / 2;
          // a section bar says WHERE you are, never HOW FAR you got, so it keeps
          // its own colour; and nothing before the start of the lanes counts
          var sect = nodes[j].classList.contains('sect');
          var on  = !sect && c >= x0 - 1 && c <= Math.min(w, span) + 1;
          var onc = !sect && c >= x0 - 1 && c <= Math.min(cw, span) + 1;
          if (nodes[j].classList.contains('passed') !== on)
            nodes[j].classList.toggle('passed', on);
          if (nodes[j].classList.contains('passed-code') !== onc)
            nodes[j].classList.toggle('passed-code', onc);
        }
        for (var q = 0; q < nodes.length; q++)
          nodes[q].classList.toggle('via-code',
              nodes[q] === green && gRes.kind === 'code');
        for (var q2 = 0; q2 < nodes.length; q2++)
          nodes[q2].classList.toggle('code-end',
              nodes[q2] === purple && !nodes[q2].classList.contains('sect'));
        if (green && !green.classList.contains('sect')) green.classList.add('passed');
        if (purple && !purple.classList.contains('sect')) purple.classList.add('passed-code');
      }

      // Kept for a panel whose nodes carry no width of their own (an older build):
      // the timeline's spacing normally comes from the content and is fixed, so
      // this is NOT called on every sync any more — opening a chapter must not
      // change the length of the timeline.
      function measure(host){
        var inner = host.querySelector('.nbmap-inner');
        var map = host.querySelector('.nbmap');
        if (!inner || !map) return;
        var nodes = [].slice.call(inner.querySelectorAll('.nbmap-node'));
        if (nodes.length < 2) return;
        var pos = nodes.map(function(n){
          var t = n.getAttribute('data-target');
          var el = t ? document.getElementById(t) : null;
          if (!el) return null;
          var r = el.getBoundingClientRect();
          if (!r.height && !r.width && !r.top) return null;
          return r.top + (window.scrollY || 0);
        });
        var first = null, last = null, k;
        for (k = 0; k < pos.length; k++)
          if (pos[k] !== null) { if (first === null) first = k; last = k; }
        if (first === null || last === first) return;
        for (k = 0; k < first; k++) pos[k] = pos[first];
        for (k = last + 1; k < pos.length; k++) pos[k] = pos[last];
        for (k = first + 1; k < last; k++) {
          if (pos[k] !== null) continue;
          var a = k - 1, b = k;
          while (pos[b] === null) b++;
          var stp = (pos[b] - pos[a]) / (b - a);
          for (var m = a + 1; m < b; m++) pos[m] = pos[a] + stp * (m - a);
        }
        var gaps = [], total = 0;
        for (k = 0; k < pos.length - 1; k++) {
          var g = Math.max(0, pos[k+1] - pos[k]);
          gaps.push(g); total += g;
        }
        if (total <= 0) return;
        var target = Math.max(760, Math.min(2600, (map.clientWidth || 480) * 2.4));
        var scale = target / total;
        for (k = 0; k < nodes.length; k++) {
          var wpx = k < gaps.length ? Math.round(gaps[k] * scale) : 34;
          var mn = nodes[k].classList.contains('task') ? 34
                 : nodes[k].classList.contains('sect') ? 80 : 18;
          wpx = Math.max(mn, Math.min(220, wpx));
          if (nodes[k].style.width !== wpx + 'px') nodes[k].style.width = wpx + 'px';
        }
      }

      // The drawer does NOT rebuild the notebook's controls — it borrows them.
      // Each slot adopts the matching widget node from the notebook (the same DOM
      // element, so it keeps its model and its kernel connection) and leaves a
      // note where it stood. Re-run on every sync, because JupyterLab may render
      // a fresh copy of an output at any time.
      // A borrowed widget is never thrown away. While the panel is being rebuilt
      // the widgets wait here — a box outside the panel, so innerHTML cannot reach
      // them, and outside the notebook, so a re-rendering output cannot either.
      function attic(){
        var a = document.getElementById('nbctl-attic');
        if (!a) {
          a = document.createElement('div');
          a.id = 'nbctl-attic'; a.className = 'nbctl-stash';
          document.body.appendChild(a);
        }
        return a;
      }
      // which notebook the panel currently belongs to — the attic keeps one set of
      // widgets per notebook, so switching tabs can never hand notebook B the
      // difficulty dropdown that belongs to notebook A (nor an old copy's)
      function nbTag(){ return panelKey(visiblePanel()) || NOWID() || 'nb'; }

      function adopt(host, feed){
        var slots = host.querySelectorAll('.nbslot');
        var tag = nbTag();
        // only ever borrow from the notebook on screen
        var scope = (feed && (feed.closest('.jp-NotebookPanel') ||
                              feed.closest('.jp-Notebook'))) || document;
        var park = document.getElementById('nbctl-attic');
        for (var i = 0; i < slots.length; i++) {
          var slot = slots[i], cls = slot.getAttribute('data-slot'), j;
          if (slot.firstElementChild && slot.firstElementChild.isConnected) continue;
          // whatever waits in the attic is the live widget — it wins over a freshly
          // rendered copy in the notebook, which would have lost its state
          var src = null;
          if (park) {
            var kept = park.querySelectorAll('.' + cls);
            for (j = 0; j < kept.length; j++)
              if (kept[j].getAttribute('data-nb') === tag) { src = kept[j]; break; }
          }
          if (!src) {
            var all = scope.querySelectorAll('.' + cls);
            for (j = 0; j < all.length; j++)
              if (!host.contains(all[j])) { src = all[j]; break; }
          }
          if (!src) continue;
          src.setAttribute('data-nb', tag);
          // a note is only worth leaving where a reader would look for the control;
          // the stash and the attic are invisible parking spaces
          if (src.parentNode && src.parentNode.id !== 'nbctl-attic' &&
              !src.closest('.nbctl-stash')) {
            var mark = document.createElement('div');
            mark.className = 'nbctl-moved';
            mark.setAttribute('data-for', cls);
            mark.textContent = nbL('This control now sits in the panel at the top of the window (⚙).',
                                   'Diese Einstellung sitzt jetzt im Panel oben im Fenster (⚙).');
            src.parentNode.insertBefore(mark, src);
          }
          slot.appendChild(src);
        }
      }

      // 2026-09-28 (Paket 5, Applikation + Struktur) — A PIP IN THE 📚 WINDOW
      // GOES WHERE ITS MARK GOES. The window's chapter rows copy the pips of
      // the rail's chapter marks; a click on one closes the window and clicks
      // the mark on the rail that the pip stands for — the chapter's exercise
      // mark (◆) or its coding mark (■), the chapter mark if there is none.
      // The SAME click, the same handler: a locked or waiting place shows
      // exactly what the rail shows for it, and there is no second way to
      // land to keep in step. (A script click has detail 0, so it never folds
      // a mark that happens to be chosen already.)
      if (window.__nbStatJump)
        document.removeEventListener('click', window.__nbStatJump, true);
      window.__nbStatJump = function(ev){
        var pip = ev.target && ev.target.closest
                ? ev.target.closest('.nbseries-chap .ps') : null;
        var host = document.getElementById(HOST_ID);
        if (!pip || !host || !host.contains(pip)) return;
        var row = pip.closest('.nbseries-chap');
        var ci = parseInt((row && row.getAttribute('data-ci')) || '-1', 10);
        var chaps = host.querySelectorAll('.nbmap-node.chap');
        var cn = chaps[ci];
        if (!cn) return;
        ev.preventDefault();
        ev.stopPropagation();
        var want = pip.classList.contains('c') ? 'codetask' : 'task';
        var ns = [].slice.call(host.querySelectorAll('.nbmap-node'));
        var to = null;
        for (var k = ns.indexOf(cn) + 1; k < ns.length; k++) {
          if (ns[k].classList.contains('chap') || ns[k].classList.contains('sect')) break;
          if (ns[k].classList.contains(want)) { to = ns[k]; break; }
        }
        host.classList.remove('open');
        setTimeout(function(){
          measure(host); gauge(host);
          reserve(host, activeSrc() || document.querySelector('.nbfeed'));
        }, 380);
        (to || cn).click();
      };
      document.addEventListener('click', window.__nbStatJump, true);

      // the series list is read from the same record the 📚 badge counts
      function seriesList(host){
        try { acctPanel(host); } catch (e) {}                         // E17.2
        var el = host.querySelector('.nbserieslist');
        if (!el) return;
        var all = {};
        try { all = JSON.parse(localStorage.getItem(STORE) || '{}'); } catch (e) {}
        var tot = seriesTotals(all);
        // E17.2: the 👤 window shows the progress per notebook and the sum to
        // EVERY reader — it is their own (the 📚 view of 25f is gone with 📚)
        var isAdmin = true;
        var de = window.__nbAcct && window.__nbAcct.lang() === 'de', L = function(en, dd){ return de ? dd : en; };
        var soloNote = tot.ids.length ? '' : '<div class="nbstat-row">' + L('Only this '
                     + 'notebook so far.', 'Bisher nur dieses Notebook.') + '</div>';
        var now = NOWID() || '';
        var cell = function(cls, ch, n){
          return '<span class="nbstat ' + cls + '">' + ch + ' ' + n + '</span>';
        };
        // the difficulty a pass was earned at, in one compact group
        var lv = function(g){
          g = g || [0, 0, 0];
          if (!(g[0] + g[1] + g[2])) return '';
          var bit = function(cls, ch, n){
            return n ? '<span class="nblevel ' + cls + '" title="' + ch + '">'
                     + ch.charAt(0) + ' ' + n + '</span>' : '';
          };
          return '<span class="nblevels">' + bit('lv-g', 'Gentle', g[0])
               + bit('lv-s', 'Standard', g[1]) + bit('lv-t', 'Strict', g[2])
               + '</span>';
        };
        var rows = (!isAdmin ? [] : (soloNote ? [soloNote] : [])).concat(
                   !isAdmin ? [] : tot.rows.map(function(r){
          var st = r.st || [0, 0, 0], ra = r.a || [0, 0];
          return '<div class="nbstat-row">' + (r.id === now ? '▸ ' : '&nbsp;&nbsp;')
               + '<b>' + (r.title || r.id || '—') + '</b> '
               + cell('ok', '\u2713', st[0] || 0) + cell('skip', '\u293c', st[1] || 0)
               + cell('fail', '\u2717', st[2] || 0)
               + '<span class="nbstat of">/ ' + (ra[1] || 0) + '</span>'
               + lv(r.g) + '</div>';
        }));
        if (isAdmin && tot.rows.length > 1) {
          rows.push('<div class="nbstat-sum nbstat-row"><b>' + L('all notebooks', 'alle Notebooks') + '</b> '
               + cell('ok', '\u2713', tot.p) + cell('skip', '\u293c', tot.s)
               + cell('fail', '\u2717', tot.f)
               + '<span class="nbstat of">/ ' + tot.at + '</span>'
               + lv(tot.g) + '</div>');
        }
        // 2026-09-25d \u2014 AND THIS NOTEBOOK, CHAPTER BY CHAPTER.
        // Built by READING THE RAIL, not by counting the store a second time.
        // The rail already holds every chapter's two states, drawn from the
        // same helper; taking them from the DOM means the window and the rail
        // cannot drift apart, and there is no second place to fix when the
        // states change. (The alternative \u2014 recount from `_TASKS` in Python
        // and ship a second table \u2014 is exactly how the rail's marks and the
        // box's padlock once disagreed for a whole build.)
        var chaps = host.querySelectorAll('.nbmap-node.chap');
        if (chaps.length) {
          var crows = ['<div class="nbseries-head">' + L('This notebook, chapter by '
                     + 'chapter', 'Dieses Notebook, Kapitel für Kapitel') + '</div>'];
          for (var ci = 0; ci < chaps.length; ci++) {
            var cn = chaps[ci];
            var ttl = (cn.getAttribute('title') || '').split(' \u2014 ')[0];
            var pips = cn.querySelector('.nbchapstat');
            // 2026-09-28 (Paket 5) — each pip is a way there: `data-ci` says
            // which chapter mark the row copies, the click handler below
            // clicks that chapter's exercise (or coding) mark on the rail
            var pz = pips ? pips.cloneNode(true) : null;
            if (pz) [].forEach.call(pz.querySelectorAll('.ps'), function(p){
              p.setAttribute('role', 'button');
              p.style.cursor = 'pointer';
              p.title = (p.title || '') + nbL(' \u2014 click to go there', '; ein Klick führt dorthin');
            });
            crows.push('<div class="nbseries-chap" data-ci="' + ci + '"><span class="nm">'
                     + (ttl || '\u2014') + '</span>'
                     + (pz ? pz.innerHTML : '') + '</div>');
          }
          crows.push('<div class="nbseries-key">'
            + '<span><i class="ps a done"></i> ' + L('exercise', 'Aufgabe') + '</span>'
            + '<span><i class="ps c done"></i> ' + L('coding', 'Programmieren') + '</span>'
            + '<span><i class="ps a done"></i> ' + L('solved', 'gelöst') + '</span>'
            + '<span><i class="ps a skip"></i> ' + L('skipped', 'übersprungen') + '</span>'
            + '<span><i class="ps a fail"></i> ' + L('given up', 'aufgegeben') + '</span>'
            + '<span><i class="ps a open"></i> ' + L('still open', 'noch offen') + '</span></div>');
          rows.push(crows.join(''));
        }
        if (!isAdmin) {
          rows.push('<div class="nbstat-note">This is your progress in <b>this '
               + 'notebook</b>, chapter by chapter.</div>');
        }
        rows.push('<div class="nbstat-note">' + L(
               '<b>\u2713</b> answered &nbsp; <b>\u293c</b> skipped, come back '
             + '&nbsp; <b>\u2717</b> given up &nbsp; <b>/ n</b> exercises in total'
             + '<br><b>G</b> Gentle &nbsp; <b>S</b> Standard &nbsp; <b>T</b> Strict '
             + '\u2014 the tolerance the exercise was answered under, recorded at '
             + 'the moment it was settled and never rewritten afterwards.'
             + '<br>These numbers live in this browser. Your account code carries '
             + 'them to another machine.',
               '<b>\u2713</b> gelöst &nbsp; <b>\u293c</b> übersprungen, später zurück '
             + '&nbsp; <b>\u2717</b> aufgegeben &nbsp; <b>/ n</b> Aufgaben insgesamt'
             + '<br><b>G</b> Gentle &nbsp; <b>S</b> Standard &nbsp; <b>T</b> Strict '
             + '\u2014 die Toleranz, unter der die Aufgabe gelöst wurde, festgehalten im '
             + 'Moment der Lösung und danach nie geändert.'
             + '<br>Diese Zahlen liegen in diesem Browser. Ihr Konto-Code trägt '
             + 'sie auf einen anderen Rechner.') + '</div>');
        var _sh = rows.join('');                 // E21.5: only when it changed (16-rail-flow)
        if (el.__nbHtml !== _sh) { el.innerHTML = _sh; el.__nbHtml = _sh; }
      }
      // 2026-10-02 (E17.2, Applikation + Struktur) — ONE WINDOW FOR THE PERSON.
      // 👤 opens it (page "code"); 📚 is gone from the corner (11-rail-layout)
      // and its statistics are part of it. From the top: the ACCOUNT (person
      // id or "not logged in", log in/out, code, QR, file — E19.5 form) ·
      // SETTINGS (favourite style, light/dark, language, role, default
      // content) · PROGRESS (per notebook and the sum, difficulty) · start
      // over. The toolkit's single-notebook code box stays in the page but
      // out of sight: the account field takes those codes and hands them to
      // it. Rebuilt panels lose the cells; every sync puts them back.
      // Contract for the stylesheet: `.nbcell.nbacct-cell > .nbacct`,
      // `.nbcell.nbprefs-cell` with `.nbpref-row > label + select.nbpref[data-k]`.
      var PREF_OPT = {
        skin: [['digi', 'digi', 'digi'], ['minimal', 'minimal', 'minimal'], ['cyber', 'cyber', 'cyber'], ['fairy', 'fairy', 'fairy']],   // E34
        theme: [['auto', 'as JupyterLab', 'wie JupyterLab'], ['light', 'light', 'hell'], ['dark', 'dark', 'dunkel']],
        lang: [['en', 'English', 'English'], ['de', 'Deutsch', 'Deutsch']],
        mode: [['', 'ask on the cover', 'auf dem Cover fragen'], ['both', 'calculate and code', 'rechnen und programmieren'],
               ['calc', 'only calculating', 'nur rechnen'], ['code', 'only coding', 'nur programmieren'],
               ['plain', 'text and figures', 'Text und Abbildungen']]};
      var PREF_LAB = {skin: ['Favourite style', 'Lieblingsstil'], theme: ['Light / dark', 'Hell / dunkel'],
                      lang: ['Language', 'Sprache'], mode: ['Default content', 'Standardinhalt']};
      function acctPanel(host){
        var A = window.__nbAcct, grid = host.querySelector('.nbdrawer-grid');
        if (!A || !grid) return;
        var de = A.lang() === 'de', ix = de ? 2 : 1, L = function(en, dd){ return de ? dd : en; };
        var st = grid.querySelector('.nbcell.pg-stats');
        // rebase 03.10.: the cells by the stylesheet's contract (css-E17.2):
        // pg-acct (1) · pg-code, the old single-notebook code (2) · pg-set (3)
        // · pg-stats (4) · pg-code with the reset slot (5); the order is the
        // stylesheet's, the DOM follows it as well
        var acc = grid.querySelector(':scope > .nbcell.pg-acct'), pr = grid.querySelector(':scope > .nbcell.pg-set');
        var oc = null;
        [].forEach.call(grid.querySelectorAll(':scope > .nbcell.pg-code'), function(c){
          if (!oc && c.querySelector('[data-slot="nbctl-code"]')) oc = c; });
        if (!acc) {
          acc = document.createElement('div'); acc.className = 'nbcell pg-acct';
          acc.innerHTML = '<div class="nbcell-h"></div><div class="nbacct" data-where="panel"></div>';
          grid.insertBefore(acc, grid.firstChild);
        }
        if (!pr) {
          pr = document.createElement('div'); pr.className = 'nbcell pg-set';
          pr.innerHTML = '<div class="nbcell-h"></div><div class="nbprefs"></div>';
          grid.insertBefore(pr, oc ? oc.nextSibling : acc.nextSibling);
          if (st) grid.insertBefore(st, pr.nextSibling);
        }
        // the role is a setting now (pg-set); its old row and the line about
        // 📚 (gone, E17.2) leave the code cell
        if (oc) [].forEach.call(oc.querySelectorAll(':scope > .nbrolerow, :scope > .nbcell-n'), function(e){
          if (e.style.display !== 'none') e.style.setProperty('display', 'none', 'important'); });
        var hs = [[acc, L('Account', 'Konto')], [pr, L('Settings', 'Einstellungen')], [st, L('Progress', 'Fortschritt')]];
        hs.forEach(function(x){ var hh = x[0] && x[0].querySelector('.nbcell-h'); if (hh && hh.textContent !== x[1]) hh.textContent = x[1]; });
        var sn = st && st.querySelector('.nbcell-n');
        if (sn) { var t0 = L('Stays in this browser. No grade.', 'Bleibt in diesem Browser. Keine Note.'); if (sn.textContent !== t0) sn.textContent = t0; }
        if (window.__nbAcctForm) window.__nbAcctForm(acc.querySelector('.nbacct'));
        var box = pr.querySelector('.nbprefs'), f = A.fav();
        var sig = de + JSON.stringify(f);
        if (box.__nbSig === sig || (document.activeElement && box.contains(document.activeElement))) return;
        box.__nbSig = sig;
        box.innerHTML = ['skin', 'theme', 'lang', 'mode'].map(function(k){      // E38a J3: no role
          return '<div class="nbset-row" style="display:flex;justify-content:space-between;align-items:center;gap:10px;margin:4px 0"><label>' + PREF_LAB[k][de ? 1 : 0] + '</label><select class="nbpref'
               + '" data-k="' + k + '">' + PREF_OPT[k].map(function(o){
                 return '<option value="' + o[0] + '"' + (String(f[k] || '') === o[0] ? ' selected' : '') + '>' + o[ix] + '</option>';
               }).join('') + '</select></div>';
        }).join('') + '<div class="nbcell-n">' + L('Logged in, these follow you to every notebook and machine.',
                    'Angemeldet folgen sie Ihnen in jedes Notebook und auf jeden Rechner.') + '</div>';
      }
      window.__nbAcctPanel = acctPanel;                 // the 👤 window is here (test_js E17.2)
      if (window.__nbPrefOff) { try { window.__nbPrefOff(); } catch (e) {} }
      var prefChange = function(ev){
        var t = ev.target;
        if (!t || !t.classList || !t.classList.contains('nbpref') || !window.__nbAcct) return;
        var k = t.getAttribute('data-k'), v = t.value, A = window.__nbAcct;
        A.setFav(k, v);
        if (k === 'skin' && window.__nbApplySkin) { try { themeFade(); } catch (e) {} window.__nbApplySkin(); }
        if (k === 'theme') {
          // "as JupyterLab": the front end's state is the choice again (E15.3)
          if (v === 'auto' && window.__nbStore) window.__nbStore.set('digichemjn.theme.v1',            // E25.o
              document.body.getAttribute('data-jp-theme-light') === 'false' ? 'dark' : 'light');
          if (window.__nbApplyTheme) window.__nbApplyTheme();
        }
        if (k === 'lang' && window.__nbLangGo) window.__nbLangGo(v);                 // E17.1
        if (window.__nbCoverPaint) { try { window.__nbCoverPaint(); } catch (e) {} }
        var h = document.getElementById(HOST_ID);
        if (h) { var b = h.querySelector('.nbprefs'); if (b) b.__nbSig = null; seriesList(h); }
      };
      document.addEventListener('change', prefChange, true);
      window.__nbPrefOff = function(){ document.removeEventListener('change', prefChange, true); };
      function NOWID(){
        var src = activeSrc();
        if (!src) return '';
        try { return JSON.parse(src.getAttribute('data-progress') || '{}').id || ''; }
        catch (e) { return ''; }
      }

      function patch(host, html){
        var keepMap = host.querySelector('.nbmap');
        var keepLeft = keepMap ? keepMap.scrollLeft : 0;
        // 2026-09-24at — what survives a rebuild is the SELECTION, not the pop.
        // `nbpop` is gone (a click no longer freezes the hover), and `nbsel` was
        // never carried across — so a panel rebuild silently dropped the pick
        // the unlock gesture requires, and the reader's double-click did
        // nothing until they clicked the mark again.
        var popped = host.querySelector('.nbmap-node.nbsel');
        var popKey = popped ? (popped.getAttribute('data-target') || '') : '';
        var restore = function(){
          var m = host.querySelector('.nbmap');
          if (m && keepLeft && m.scrollLeft !== keepLeft) m.scrollLeft = keepLeft;
        };
        setTimeout(restore, 0);
        var tmp = document.createElement('div');
        tmp.innerHTML = html;
        var oldDots = host.querySelectorAll('.nbrail-dot');
        var newDots = tmp.querySelectorAll('.nbrail-dot');
        // Whether the panel is rebuilt or patched in place used to hang on the
        // NUMBER of circles alone. That was wrong the moment the panel's own
        // shape changed: moving the controls out of the rail and into a dock
        // leaves the circle count untouched, so a host built by the previous
        // version was patched in place for ever — same circles, and no dock.
        // The controls simply never appeared again. So the SHAPE is compared
        // too: if the new panel has a part the mounted one does not, rebuild.
        var shape = function(root){
          return ['.nbrail', '.nbdock', '.nbctrl', '.nbdrawer', '.nbmap-fill',
                  '.nbmap-here', '.nbslider', '.nbgear', '.nbcell.pg-diff',
                  // 2026-09-24bf — the grip is a PART, so a host mounted by a
                  // build that had none is rebuilt rather than patched. Without
                  // this line the circle count and the shape both matched and
                  // the new edge simply never appeared.
                  '.nbgrip', '.nbmap-cursor', '.nbbtn.nbskin',
                  '.nbcell.pg-stats', 'button.nbseries']
                 .map(function(sel){ return root.querySelector(sel) ? 1 : 0; }).join('');
        };
        // 2026-09-27a — …and when the NUMBER OF MARKS differs. Measured (D
        // merge, Complex, real Lab): solve coding 1, Run All or restart + Run
        // All — in about one run of three the panel kept 43 marks while the
        // source had 46 (the partial structure of a mirror, taken while the
        // document re-rendered). The circles and the shape matched, so this
        // went in place; the loop below syncs the marks' classes only when the
        // counts agree, skipped them, and data-sig was set anyway — chapter 2
        // stayed padlocked on the panel for good while the document and the
        // kernel had it open. A different mark count is a structure change.
        var markCount = function(root){
          // R2 · H3: the reader's own-cell marks are the page's, not the
          // kernel's — they are not structure, and do not force a rebuild
          return root.querySelectorAll('.nbmap-node:not(.own)').length + '/' +
                 root.querySelectorAll('.nbcodemark').length;
        };
        // 2026-10-04 (E21 Nachtrag R1, Struktur + Applikation) — …and when the
        // RUN changed. Every anchor id carries the run's token (`_aid`,
        // chapter_template: "ch2__<token>"), so after Restart + Run All the
        // marks of a panel patched in place pointed at the PREVIOUS run's
        // anchors: measured v1.62, 39 of 39 `data-target`s without an element
        // 30 s after the rerun — a click on a mark found nothing to jump to
        // (01-jump: getElementById → null, return). The in-place path below
        // copies classes, padlocks, pips and states, never the targets. A new
        // token is a new document: rebuild, once per run.
        var runOf = function(root){
          var n = root.querySelector('.nbmap-node[data-target]'), t = n ? n.getAttribute('data-target') || '' : '';
          var m = /__([0-9a-f]{8})$/.exec(t);
          return m ? m[1] : '';
        };
        var runOld = runOf(host), runNew = runOf(tmp);
        if (oldDots.length !== newDots.length || shape(host) !== shape(tmp) ||
            markCount(host) !== markCount(tmp) ||
            (runOld && runNew && runOld !== runNew) ||
            !host.querySelector('.nbmap-fill')) {
          // hand the borrowed widgets back before the panel is rebuilt, otherwise
          // innerHTML would destroy live widget nodes
          // into the attic, never into the void: the old code removed a widget
          // outright whenever it could not find the note it had left behind, and a
          // removed widget never comes back — that is how the ⚙ drawer ended up
          // with empty slots after a re-render.
          var keep = host.querySelectorAll('.nbslot > *');
          for (var q = 0; q < keep.length; q++) attic().appendChild(keep[q]);
          host.innerHTML = html;                      // structure changed → rebuild
          var fills = host.querySelectorAll('.nbmap-fill');
          var want = [];
          fills.forEach(function(f){ want.push(f.style.width); f.style.width = '0px'; });
          if (popKey) {
            var again = host.querySelector('.nbmap-node[data-target="' + popKey + '"]');
            if (again) again.classList.add('nbsel');
          }
          requestAnimationFrame(function(){
            fills.forEach(function(f, i){ f.style.width = want[i]; });
            gauge(host);
          });
          return;
        }
        // The nodes themselves carry state too — the padlock in a chapter dot and
        // the 'locked' class. Only the circles used to be synced here, so a chapter
        // that had just been opened by a skip kept its padlock until something
        // else forced a full rebuild.
        var oldN = host.querySelectorAll('.nbmap-node:not(.own)');
        var newN = tmp.querySelectorAll('.nbmap-node');
        if (oldN.length === newN.length) {
          for (var k = 0; k < oldN.length; k++) {
            ['locked', 'unlocked', 'is-current'].forEach(function(c){
              oldN[k].classList.toggle(c, newN[k].classList.contains(c));
            });
            var od = oldN[k].querySelector('.nbchapdot'),
                nd2 = newN[k].querySelector('.nbchapdot');
            if (od && nd2 && od.textContent !== nd2.textContent)
              od.textContent = nd2.textContent;
            // 2026-09-27c — AND THE TWO PIPS under the chapter's name. They
            // were never synced in place: a solved, skipped or given-up task
            // left its chapter's pips 'open' until something forced a full
            // rebuild (measured: t1 done, pips of chapter 1 still open).
            var os3 = oldN[k].querySelector('.nbchapstat'),
                ns3 = newN[k].querySelector('.nbchapstat');
            if (os3 && ns3 && os3.innerHTML !== ns3.innerHTML)
              os3.innerHTML = ns3.innerHTML;
            var ot2 = oldN[k].getAttribute('title'), nt2 = newN[k].getAttribute('title');
            if (nt2 && ot2 !== nt2) oldN[k].setAttribute('title', nt2);
            // 2026-09-24ar — and the LOCK ATTRIBUTE, which was never synced.
            // `data-lock` is what makes a mark a double-click target. The
            // classes and the padlock glyph were copied here, so an opened
            // chapter looked open — and still answered the unlock gesture,
            // because the attribute behind it had never been taken off.
            // Measured: unlock t3, and the rail still carried data-lock="t3".
            var ol2 = oldN[k].getAttribute('data-lock'),
                nl2 = newN[k].getAttribute('data-lock');
            if (ol2 !== nl2) {
              if (nl2 === null) oldN[k].removeAttribute('data-lock');
              else oldN[k].setAttribute('data-lock', nl2);
            }
            // 2026-09-27e — and the two STATES (F): data-state / data-cstate,
            // the written and the coding route, for styles to select on.
            ['data-state', 'data-cstate'].forEach(function(at){
              var o3 = oldN[k].getAttribute(at), n3 = newN[k].getAttribute(at);
              if (o3 !== n3) {
                if (n3 === null) oldN[k].removeAttribute(at);
                else oldN[k].setAttribute(at, n3);
              }
            });
          }
        }
        for (var i = 0; i < oldDots.length; i++) {          // in-place → transitions run
          if (oldDots[i].className !== newDots[i].className)
            oldDots[i].className = newDots[i].className;
          // 2026-09-27c — innerHTML, NOT textContent (OBERFLAECHE §3, G1).
          // The sign sits in <i class="nbdotg">, and that wrapper is what turns
          // it back level inside the 45° mark. Copying the TEXT threw the
          // wrapper away: after the first answer the tick stood bare in the
          // mark and leaned 45° with it — measured in the real Lab (tick,
          // skip arrow and cross at 45°; the open padlock of the current task
          // gone). The purple marks below always copied innerHTML.
          if (oldDots[i].innerHTML !== newDots[i].innerHTML)
            oldDots[i].innerHTML = newDots[i].innerHTML;
          var oi = oldDots[i].closest('.nbrail-item'), ni = newDots[i].closest('.nbrail-item');
          if (oi && ni && oi.title !== ni.title) oi.title = ni.title;
        }
        // 2026-09-25h — AND THE PURPLE MARKS. Only the circles were synced here,
        // so a solved CODING exercise stayed `cd-open` on the panel while every
        // copy in the document said `cd-done` — found by the code fuzz (D), which
        // asks after every hostile payload whether the panel still shows a solve.
        // It never had, in place; only a full rebuild ever did. (25g the same.)
        var oldC = host.querySelectorAll('.nbcodemark');
        var newC = tmp.querySelectorAll('.nbcodemark');
        if (oldC.length === newC.length) {
          for (var c2 = 0; c2 < oldC.length; c2++) {
            if (oldC[c2].className !== newC[c2].className)
              oldC[c2].className = newC[c2].className;
            if (oldC[c2].innerHTML !== newC[c2].innerHTML)
              oldC[c2].innerHTML = newC[c2].innerHTML;
          }
        }
        var ot = host.querySelector('.nbmap-fill'), nt = tmp.querySelector('.nbmap-fill');
        if (ot && nt && ot.title !== nt.title) ot.title = nt.title;
        gauge(host);
      }

      // Older builds of this notebook (an old copy opened in another tab, with its
      // own kernel) pin their own panel to <body>. Those hosts are dead weight and
      // they overlay ours, so they go. Only body-level hosts are touched — never
      // anything inside a notebook, where our own feed lives.
      // 2026-10-05 (E22.1b, Applikation) — the same two sweeps, over the
      // page's top level only. `body > …` as a selector walked the whole page
      // (the browser matches right to left: every element is asked whether its
      // parent is <body>) — 16 of every 100 samples of a full pass (profile
      // v1.64 probe, two notebooks). What is swept lies directly under <body>
      // (or one div down): that is where it is looked for now, in page order.
      var SWEEP_TOP = /^(nbrail-host|nbprog-host)$/;
      function sweep(host){
        var b = document.body;
        if (!b) return;
        var top = [].slice.call(b.children), i, j, e, k;
        for (i = 0; i < top.length; i++) {
          e = top[i];
          if (e !== host && (SWEEP_TOP.test(e.id) || e.classList.contains('nbrail-host')
              || e.classList.contains('nbprog-host') || e.classList.contains('nbrail-fixed'))) { e.remove(); continue; }
          if (e.tagName !== 'DIV' || e === host || e.id === HOST_ID) continue;
          for (j = 0, k = e.children; j < k.length; j++)
            if (k[j].classList.contains('nbrail') || k[j].classList.contains('nbprog')) { e.remove(); break; }
        }
      }

