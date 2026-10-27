      // ======================================================================
      // THE VERTICAL LAYOUT
      // Turned on its side the panel needs no mapping at all: the document's own
      // axis IS the timeline's axis. The rail is exactly as tall as the document
      // is long, it scrolls in lockstep with it, and every node sits at the
      // offset of the heading it points at — so a circle and its accordion pill
      // are at the same height on screen, and the two scrollbars run side by side
      // at the same length and the same position.
      // What that costs: with the notebook fully open the timeline is as long as
      // the notebook, so you no longer see all nine exercises at once. Closed, it
      // is short and you do — which is the right way round.
      function vertOn(){ return orient() === 'v'; }
      // py-E23.1 — a word of the page in the reader's language (01-jump __nbDe)
      function nbL(en, de){ return window.__nbDe && window.__nbDe() ? de : en; }

      // 2026-09-28 (R2 · Paket 15 / H3, Struktur + Applikation) — THE READER'S
      // OWN CELLS ARE MARKS. Every cell after the two of the notebook (title,
      // document) gets a mark "Own cell n" on the rail, just above "Your own
      // cell". The cell is tagged `nbown-n` and the mark points at that class
      // (data-sel), so vertLayout measures it like every other mark and a click
      // lands it on the reading line. THE CELL OBSERVER is the page's own
      // MutationObserver (arm(): body, childList, subtree): a cell added or
      // deleted is a childList change, sync() runs, and this puts the marks
      // right — added, removed, renumbered. It writes only when something is
      // different, so it does not feed the observer that called it.
      function ownCells(host, src){
        var inner = host && host.querySelector('.nbmap-inner');
        var p = src && src.closest ? (src.closest('.jp-NotebookPanel') || src.closest('.jp-Notebook')) : null;
        var nb = p && (p.classList.contains('jp-Notebook') ? p : p.querySelector('.jp-Notebook'));
        if (!inner || !nb) return;
        var cells = allCls(nb, 'jp-Cell').filter(function(c){       // E22.1b
          return !(c.parentElement && c.parentElement.closest('.jp-Cell'));
        });
        // 2026-10-03 (E21.3c, Struktur + Applikation) — OWN = NOT OURS, WHEREVER
        // IT STANDS. "Every cell after the first two" took a cell the reader
        // put ABOVE the title (A on the title cell; the gate's row Complex
        // cyber dark old, from a palette typed into command mode: the saved
        // file had an empty code cell at 0) for the title, and the mega cell
        // for the reader's — the new cell got no mark and no margin and lay
        // under ⛶ (J3: BUTTON.nbbtn over its .cm-content). Ours are the title
        // cell (markdown with the title card) and the cell that holds this
        // panel's source; every other cell is the reader's, in page order.
        // Without a source cell (another front end) the old rule stays.
        var mega = src.closest ? src.closest('.jp-Cell') : null, mine = [], k, n = 0;
        var isTitle = function(c){ return c.classList.contains('nbtitle-cell') || (c.classList.contains('jp-MarkdownCell')
          && (!!c.querySelector('.nbtitle') || (c.textContent || '').indexOf('nbtitle') > -1)); };
        if (mega && cells.indexOf(mega) >= 0) {
          mine = cells.filter(function(c){ return c !== mega && !isTitle(c); });
        } else mine = cells.slice(2);
        for (k = 0; k < cells.length; k++) {
          var want = mine.indexOf(cells[k]) >= 0 ? 'nbown-' + (++n) : null;
          [].slice.call(cells[k].classList).forEach(function(c){
            if (c.indexOf('nbown-') === 0 && c !== want) cells[k].classList.remove(c);
          });
          if (want && !cells[k].classList.contains(want)) cells[k].classList.add(want);
        }
        // 2026-10-02 (E21.3, Struktur) — AN OWN CELL STARTS RIGHT OF THE
        // CORNER. The corner's signs (⛶ ◐ … ⌨ ⚙ 👤 📚) stand in a column at the
        // notebook's left edge, over the margin of our own cells — and over
        // the prompt and the left of every cell of the reader's own (Befund
        // Dirigent a: ⛶ took the click meant for the last cell). Those cells
        // move right of that column; ours (title, mega cell) are untouched.
        // 2026-10-03 (E21.3c, Struktur) — … AND RIGHT OF THE LENS. The lens
        // (`.nbzoomgrp`, E6.6: lying, right of ⛶ in the top corner) reaches
        // ~150 px further into the page than the signs; an own cell scrolled
        // up under it lost its clicks there (gate 03.10., J3: SPAN.nbzoomgrp /
        // INPUT.nbslider over cell 2). The cell scrolls, the lens stays, so
        // the cell starts right of the whole corner. While the corner cannot
        // be measured (panel hidden behind another notebook, rebuilt during a
        // run) a cell keeps the margin it has instead of losing it.
        // 2026-10-06 (E23.10, Struktur) — NO MARGIN OF OURS ANY MORE: ON THE
        // AXIS, AS WIDE AS THE OTHER BLOCKS. The margin (E21.3c left, E22.8
        // both sides) kept the corner off the cell by moving or narrowing
        // the cell: measured v1.63 + E22, 1400 × 900: own cell 409 px wide
        // (the blocks 720), and with E21.3c alone +95 px off the axis. Since
        // css-E23.10 the DOCUMENT keeps the corner free (the scroller's 52-px
        // sides, the lens strip cut out) and the cell is a column like the
        // others (720 px × lens, margin auto). A margin this script set before
        // (a cell restored or kept from an older run) is taken away; one the
        // reader's own front end set is not ours to judge — only what carries
        // our mark (both sides equal, !important) goes.
        mine.forEach(function(c){
          var st = c.style;
          if (st.getPropertyPriority('margin-left') === 'important' && st.marginLeft === st.marginRight) {
            st.removeProperty('margin-left'); st.removeProperty('margin-right');
          } else if (st.getPropertyPriority('margin-left') === 'important' && !st.marginRight) {
            st.removeProperty('margin-left');                 // E21.3c: left only
          }
        });
        var have = [].slice.call(inner.querySelectorAll(':scope > .nbmap-node.own'));
        var foot = inner.querySelector(':scope > .nbmap-node.cell');
        for (k = mine.length; k < have.length; k++) have[k].remove();
        for (k = have.length; k < mine.length; k++) {
          var a = document.createElement('a');
          a.className = 'nbjump nbmap-node sect own';
          a.href = '#';
          a.innerHTML = '<span class="nbmap-lab"></span><span class="nbsect"></span>';
          if (foot) inner.insertBefore(a, foot); else inner.appendChild(a);
          have.push(a);
        }
        for (k = 0; k < mine.length; k++) {
          var n = have[k], nm = nbL('Own cell ', 'Eigene Zelle ') + (k + 1);
          if (n.getAttribute('data-sel') !== 'nbown-' + (k + 1)) n.setAttribute('data-sel', 'nbown-' + (k + 1));
          var lab = n.querySelector('.nbmap-lab');
          if (lab && lab.textContent !== nm) lab.textContent = nm;
          var tt = nm + nbL(' \u2014 a cell you added; click to go there', ' \u2014 eine Zelle, die Sie angelegt haben; ein Klick führt dorthin');
          if (n.getAttribute('title') !== tt) n.setAttribute('title', tt);
        }
        try { ownKeep(nb, mine); } catch (e) {}      // E9.13
      }

      // 2026-09-30 (E9.13, Applikation) — YOUR OWN CELLS OUTLIVE THE VERSION.
      // A new version of the notebook is a new file, and the cells the
      // reader added to the old one stayed behind in it. Their code is now
      // kept in this browser (`digichemjn.owncells.v1`, per notebook id,
      // with the build it came from) on every sync that changes it. A build
      // that opens with none of its own and finds cells kept by ANOTHER
      // build offers them in "Your own cell" (Python's `.nbyoc-list`):
      // "Restore your N own cells?" — Restore makes them again, one by one,
      // through JupyterLab's own add-a-cell strip; "No" is remembered for
      // this build. Code cells only (a rendered Markdown cell has no source
      // in the page). Nothing leaves the machine.
      var OWN_KEY = 'digichemjn.owncells.v1';
      function ownId(){
        return nbId() || null;
      }
      function ownSrc(c){
        var ls = c.querySelectorAll('.jp-Cell-inputWrapper .cm-content .cm-line');
        return [].map.call(ls, function(l){ return l.textContent; }).join('\n').replace(/\u200b/g, '');
      }
      function ownKeep(nb, mine){
        var id = ownId();
        if (!id) return;
        var all = {};
        try { all = JSON.parse(localStorage.getItem(OWN_KEY) || '{}') || {}; } catch (e) { all = {}; }
        var rec = all[id] || null;
        var code = mine.filter(function(c){ return c.classList.contains('jp-CodeCell'); })
                       .map(ownSrc).filter(function(t){ return t.trim(); });
        var put = function(r){ all[id] = r; try { localStorage.setItem(OWN_KEY, JSON.stringify(all)); } catch (e) {} };
        if (code.length) {
          window.__nbOwnSeen = id;
          if (!rec || rec.v !== NBRAIL_VERSION || JSON.stringify(rec.cells) !== JSON.stringify(code))
            put({v: NBRAIL_VERSION, t: Date.now(), cells: code});
        } else if (window.__nbOwnSeen === id && rec && rec.v === NBRAIL_VERSION && rec.cells.length) {
          put({v: NBRAIL_VERSION, t: Date.now(), cells: []});   // the reader deleted them here
        }
        ownOffer(nb, id, (!code.length && rec && rec.v !== NBRAIL_VERSION &&
                          rec.no !== NBRAIL_VERSION && rec.cells && rec.cells.length) ? rec : null);
      }
      function ownOffer(nb, id, rec){
        var p = nb.closest('.jp-NotebookPanel') || nb;
        var lists = allCls(p, 'nbyoc-list');                   // E22.1b: by class, one under .acc-yoc first
        var list = lists.filter(function(e){ return !!(e.parentElement && e.parentElement.closest('.acc-yoc')); })[0] || lists[0] || null;
        if (!list) return;
        var box = list.querySelector('.nbyoc-restore');
        if (!rec || window.__nbOwnBusy) { if (box && !window.__nbOwnBusy) box.remove(); return; }
        var n = rec.cells.length;
        var txt = nbL('Restore your ' + n + ' own cell' + (n === 1 ? '' : 's') + '?',
                      (n === 1 ? 'Ihre eigene Zelle' : 'Ihre ' + n + ' eigenen Zellen') + ' wiederherstellen?');
        if (box && box.getAttribute('data-n') === String(n)) return;
        if (!box) { box = document.createElement('div'); box.className = 'nbyoc-restore'; list.appendChild(box); }
        box.setAttribute('data-n', String(n));
        box.style.cssText = 'margin:10px auto 0;display:flex;gap:10px;align-items:center;justify-content:center;flex-wrap:wrap';
        box.innerHTML = '<span class="nbyoc-restore-t"></span>'
          + '<button type="button" class="nbyoc-restore-yes">' + nbL('Restore', 'Wiederherstellen') + '</button>'
          + '<button type="button" class="nbyoc-restore-no">' + nbL('No', 'Nein') + '</button>';
        box.querySelector('.nbyoc-restore-t').textContent = txt;
        box.title = nbL('code you added to an earlier version of this notebook (kept in this browser)',
                        'Code, den Sie einer früheren Version dieses Notebooks hinzugefügt haben (in diesem Browser aufbewahrt)');
        box.querySelector('.nbyoc-restore-no').onclick = function(ev){
          ev.preventDefault(); ev.stopPropagation();
          var all = {};
          try { all = JSON.parse(localStorage.getItem(OWN_KEY) || '{}') || {}; } catch (e) {}
          if (all[id]) { all[id].no = NBRAIL_VERSION; try { localStorage.setItem(OWN_KEY, JSON.stringify(all)); } catch (e) {} }
          box.remove();
        };
        box.querySelector('.nbyoc-restore-yes').onclick = function(ev){
          ev.preventDefault(); ev.stopPropagation();
          box.remove();
          ownRestore(p, rec.cells.slice());
        };
      }
      // one cell after the other: the strip makes it, its editor gets the text
      function ownRestore(p, cells){
        window.__nbOwnBusy = true;
        var nCells = function(){ return p.querySelectorAll('.jp-Notebook .jp-Cell').length; };
        var step = function(){
          if (!cells.length) { window.__nbOwnBusy = false; return; }
          var foot = p.querySelector('.jp-Notebook-footer');
          if (!foot) { window.__nbOwnBusy = false; return; }
          var n0 = nCells(), tries = 0;
          try { foot.click(); } catch (e) {}
          var wait = function(){
            if (nCells() <= n0) {
              if (++tries > 12) { window.__nbOwnBusy = false; return; }
              if (tries % 4 === 0) { try { foot.click(); } catch (e) {} }
              return setTimeout(wait, 150);
            }
            var cs = p.querySelectorAll('.jp-Notebook .jp-Cell');
            var ed = cs[cs.length - 1].querySelector('.cm-content');
            if (ed) {
              try { ed.focus(); document.execCommand('insertText', false, cells.shift()); } catch (e) { cells.shift(); }
            } else cells.shift();
            setTimeout(step, 250);
          };
          setTimeout(wait, 150);
        };
        step();
      }

      // E10.7 — how far the title card's middle moves when the lens is
      // lifted (content pixels), or null. One read, nothing painted between.
      function titleAt100(host){
        var tn = host.querySelector('.nbmap-node.title');
        var aim = tn && tn.__nbAim, card = aim && aim[0];
        if (!card || !card.isConnected) return null;
        var sc = scroller(host), p = card.closest('.jp-NotebookPanel');
        if (!sc || !p) return null;
        var zs = [].filter.call(p.querySelectorAll('.jp-Cell > *'), function(e){
          return !!e.style.zoom; });
        if (!zs.length) return null;
        var mid = function(){ var r = card.getBoundingClientRect();
          return r.height > 4 ? r.top + r.height / 2 + sc.scrollTop : null; };
        var st = sc.scrollTop, a = mid(), was = zs.map(function(e){ return e.style.zoom; });
        zs.forEach(function(e){ e.style.zoom = ''; });
        var b = mid();
        zs.forEach(function(e, i){ e.style.zoom = was[i]; });
        if (sc.scrollTop !== st) sc.scrollTop = st;
        return (a === null || b === null) ? null : b - a;
      }
      // What a timeline node points at: an anchor id, or — for the title bar,
      // which cannot carry one — a class looked up inside the notebook this
      // panel is currently serving.
      function targetEl(node){
        // 2026-09-24p — `data-mark` names the element a bar BELONGS ON, ahead of
        // its jump anchor. The end-of-the-guided-part anchor is a zero-height
        // span sitting above the note it marks, so measuring from it put the bar
        // seventy pixels over the pill. Naming the note itself ends the guessing.
        var mk = node.getAttribute('data-mark');
        if (mk) {
          var ml = mk.split(/\s+/), mi, mh;
          for (mi = 0; mi < ml.length; mi++) {
            if (!ml[mi]) continue;
            mh = byCls(document, ml[mi]);                 // E22.1b
            if (mh && mh.getBoundingClientRect().height > 4) return mh;
          }
        }
        var id = node.getAttribute('data-target');
        if (id) { var e = document.getElementById(id); if (e) return e; }
        var sel = node.getAttribute('data-sel');
        if (!sel) return null;
        var src = activeSrc();
        var p = src && (src.closest('.jp-NotebookPanel') || src.closest('.jp-Notebook'));
        // several class names, best first: the title bar points at the CARD, and
        // falls back to the whole cover for a notebook built before the card had
        // a class of its own. Aiming at the cover put the mark on the middle of a
        // full-screen-tall section instead of on the card it names.
        // 2026-09-27d — THE CARD THAT IS ON THE PAGE, not the first in the file.
        // Once the notebook has run there are TWO title cards: the markdown
        // cell's (display:none, 0 × 0) and the document's own. querySelector
        // returned the hidden one, its box measured nothing, and the title
        // mark was parked by the "hole" rule instead — measured 93 px above the
        // middle of the card it names. The first match with a real box wins;
        // a cold page, where only the hidden kind exists, still gets one.
        var list = sel.split(/\s+/), k, hit, all, a0, first = null;
        for (k = 0; k < list.length; k++) {
          if (!list[k]) continue;
          all = allCls(p || document, list[k]);          // E22.1b
          for (a0 = 0; a0 < all.length; a0++) {
            if (all[a0].getBoundingClientRect().height > 4) return all[a0];
            if (!first) first = all[a0];
          }
        }
        return first;
      }

      // Where an element sits in the SCROLLER's own content, in page pixels.
      // In SCREEN pixels: getBoundingClientRect already reports those, and the
      // scroll offset is a page length, so only that one is scaled.
      function offIn(sc, el, scRect, z, mid){
        var r = el.getBoundingClientRect();
        if (!r.height && !r.width && !r.top) return null;
        var y = r.top + (mid ? r.height / 2 : 0);
        return Math.round(sc.scrollTop * z + (y - scRect.top));
      }

      // An anchor is a zero-height span carrying `top:-56px`, sitting somewhere
      // above the thing it announces. Lining a circle up with THAT puts it a
      // hundred pixels above the pill a reader actually sees. So each node is
      // lined up with the accordion header that follows its anchor — its vertical
      // MIDDLE, which is what the eye reads as the row.
      var HDR = '.jupyter-widget-Collapse-header,.p-Collapse-header,.lm-Collapse-header';
      // Anchors and headers are both in document order, so one pointer walks
      // both lists — no O(n·m) search per frame.
      function pillFinder(sc){
        // E22.1b: by class — JupyterLab 4 has only the first of the three names;
        // where another one is there too, the selector keeps the page order
        var h1 = allCls(sc, 'jupyter-widget-Collapse-header');
        var heads = (byCls(sc, 'p-Collapse-header') || byCls(sc, 'lm-Collapse-header'))
                  ? [].slice.call(sc.querySelectorAll(HDR)) : h1;
        var i = 0;
        // `next` is the FOLLOWING anchor, and it bounds the search: a header
        // that lies beyond it belongs to the next chapter, not to this one.
        // Without that bound, a section that has no accordion of its own — a
        // plain box — borrowed the next chapter's pill, and several such
        // sections piled up on the same one. That is the stack in the panel.
        return function(el, next){
          while (i < heads.length &&
                 !(el.compareDocumentPosition(heads[i]) & 4 /* FOLLOWING */)) i++;
          if (i >= heads.length) return null;
          if (next && (next.compareDocumentPosition(heads[i]) & 4)) return null;
          return heads[i];
        };
      }

      function vertLayout(host, src){
        var map = host.querySelector('.nbmap');
        var inner = host.querySelector('.nbmap-inner');
        var sc = scroller(host);
        if (!map || !inner || !sc) return null;
        var z = pageZoom();
        var scRect = sc.getBoundingClientRect();
        // The map does not begin at the scroller's top — the rail has padding, a
        // border, a rounded card. That inset is a constant, and subtracting it
        // from every node is what puts a circle on the same screen line as its
        // heading instead of nine pixels under it.
        var inset = Math.round(map.getBoundingClientRect().top - scRect.top);
        // The rail is scaled back against the document zoom, so its own pixels
        // are SCREEN pixels: the document's rendered length is scrollHeight × z,
        // and that is what the rail has to be as long as.
        var H = Math.round(sc.scrollHeight * z);
        // 2026-09-24p — the two windows are not the same height. The rail runs
        // from under the toolbar to the bottom of the window; the document's
        // scroller stops above the status bar. So the document could still
        // scroll when the rail had already run out, and the last marks — the end
        // bar above all — stayed a few dozen pixels below their pills. The rail
        // is given that difference as extra length, so the two reach their ends
        // together.
        var extra = Math.round(map.clientHeight - sc.clientHeight * z);
        if (extra > 0) H += extra;
        if (inner.style.height !== H + 'px') inner.style.height = H + 'px';
        var nodes = inner.querySelectorAll('.nbmap-node');
        var nextPill = pillFinder(sc);
        var els = [], i;
        for (i = 0; i < nodes.length; i++) els.push(targetEl(nodes[i]));
        var ys = [], hasPill = [], onPage = [];
        for (i = 0; i < nodes.length; i++) {
          var el = els[i], y = null;
          hasPill.push(false);
          // 2026-09-24x — IS THE THING IT POINTS AT ON THE PAGE AT ALL?
          // hasPill alone was not enough. The pill search is bounded by the
          // NEXT node's anchor, and for the last marks inside a shut chapter —
          // the visualisation square and the practice circle — that bound falls
          // past the next chapter's pill. They borrowed it and stayed on the
          // rail at its height, which is why folding a chapter never quite
          // emptied it. An anchor inside a collapsed accordion has no layout
          // box at all, and that is the honest test.
          onPage.push(!!(el && (el.offsetParent
                                || (el.getClientRects
                                    && el.getClientRects().length))));
          if (el) {
            // the next anchor that is a DIFFERENT element: a chapter and its
            // exercise share one anchor when the exercise has none of its own,
            // and bounding the search by the element itself excluded every
            // header, which sent the node back to the anchor's own position
            var nx = null;
            for (var q = i + 1; q < els.length; q++)
              if (els[q] && els[q] !== el) { nx = els[q]; break; }
            // 2026-09-30 (E9 Hinweis, Struktur) — THE TITLE MARK STANDS ON
            // THE CARD. Since py-E9.5 the first header after the card is the
            // title's own accordion (`.acc-title`, the whole book), and the
            // title mark borrowed it: ~110 px under the card when the notebook
            // opens (Hauptwerkstatt, v1.34). The card is the title's place.
            var pill = nodes[i].classList.contains('title') ? null : nextPill(el, nx);
            // no pill of its own: fall back to the anchor, undoing the -56px it
            // carries so that it lands where it actually sits in the text
            // No pill of its own — the title card, a plain box. If the thing
            // it points at has a height, its middle is the honest place; only a
            // zero-height anchor needs the -56px it carries undone.
            // An anchor span has no height and sits 56px above what it marks.
            // Rather than adding that 56 back as a guess, walk to the first
            // sibling that IS on the page — the end-of-the-notebook footer, the
            // title card — and use its middle. That is where the reader sees the
            // thing, so that is where its mark belongs.
            if (!pill && el.getBoundingClientRect().height <= 4) {
              var nx2 = el.nextElementSibling, guard = 0;
              while (nx2 && guard++ < 6
                     && nx2.getBoundingClientRect().height <= 4)
                nx2 = nx2.nextElementSibling;
              if (nx2 && nx2.getBoundingClientRect().height > 4) el = nx2;
            }
            var solid = el.getBoundingClientRect().height > 4;
            hasPill[i] = !!pill;
            y = pill ? offIn(sc, pill, scRect, z, true)
                     : (solid ? offIn(sc, el, scRect, z, true)
                              : offIn(sc, el, scRect, z, false) + 56 * z);
            // 2026-09-27f — the element the mark stands for, and which point
            // of it: kept on the node, so a click LANDS that same point on the
            // reading line (land(), Eilauftrag 2) — one measure, not two.
            nodes[i].__nbAim = pill ? [pill, 1] : (solid ? [el, 1] : [el, 0]);
          } else nodes[i].__nbAim = null;
          ys.push(y === null ? null : y - inset);
        }
        // A COLLAPSED CHAPTER TAKES ITS POINTS WITH IT.
        // When a group or a chapter is shut, the pills inside it are not in the
        // document at all — so every node under it falls back to its anchor,
        // and a dozen anchors a few pixels apart become a dozen circles on top
        // of one another. They are not information in that state; they are a
        // pile. So a node whose pill is gone is taken off the rail until its
        // chapter is open again. The bars — title, the group headers, the end —
        // never have a pill of their own and always stay.
        // 2026-09-30 (E11.2, Struktur) — THE TITLE SHUT TAKES THE BARS TOO.
        // Folding the title pill (card or mark) shuts the whole book, but the
        // bars — Introduction, Content, Appendix, End — stayed on the rail
        // (measured: 6 marks left, 5 of them for things no longer on the
        // page). With the title's root accordion shut, every node whose
        // anchor lies inside it goes; the title mark, the own-cell mark and
        // the reader's own cells live outside it and stay. Shut = none of the
        // anchors inside the root has a box; open again, all come back.
        var tRoot = allCls(sc, 'acc-title').filter(function(e){ return e.classList.contains('acc-root'); })[0] || null,   // E22.1b
            inRoot = [], nIn = 0, nOn = 0;
        for (i = 0; i < nodes.length; i++) {
          var ir = !!(tRoot && els[i] && tRoot.contains(els[i])
                      && !nodes[i].classList.contains('title'));
          inRoot.push(ir);
          if (ir) { nIn++; if (onPage[i]) nOn++; }
        }
        var tShut = nIn > 0 && nOn === 0;
        // E16.2 (Struktur) — the state for CSS: `data-tshut` on the host while
        // the title is shut; the rail then shows the title mark alone, and a
        // beam only from YOC to the reader's own cells (no trail above YOC)
        if (host.hasAttribute('data-tshut') !== tShut) host.toggleAttribute('data-tshut', tShut);
        for (i = 0; i < nodes.length; i++) {
          var keep = (hasPill[i] && onPage[i])
                  || (nodes[i].classList.contains('sect') && !(tShut && inRoot[i]));
          nodes[i].classList.toggle('nbgone', !keep);
        }
        // An anchor that has not rendered yet (a collapsed widget, a cell the
        // front end is still building) leaves a hole. Rather than dropping the
        // node — which would make the line jump about while the page settles — it
        // is parked halfway between the neighbours that DID measure.
        var lastY = 0;
        for (i = 0; i < ys.length; i++) {
          if (ys[i] === null) {
            var nxt = null;
            for (var j = i + 1; j < ys.length; j++) if (ys[j] !== null) { nxt = ys[j]; break; }
            ys[i] = nxt === null ? lastY : Math.round((lastY + nxt) / 2);
          }
          if (i && ys[i] < lastY) ys[i] = lastY;   // never run backwards
          lastY = ys[i];
        }
        // 2026-09-24av — one number for both ends of the rail, so the title
        // mark's gap at the top and the add-a-cell mark's gap at the bottom
        // are the same gap.
        var NB_INSET = 18;
        // The two covers are not measured, they are the ends: the title bar sits
        // at the very top of the rail and the cell bar at the very bottom, so
        // the line spans exactly the document and nothing sticks out past it.
        for (i = 0; i < nodes.length; i++) {
          // just inside the ends, not ON them: the markers are centred on their
          // position, so a bar at exactly 0 loses its upper half to the clip
          // 2026-09-24n — the title's mark is MEASURED, like every other mark.
          // It used to be welded to y = 8, which put it against the rail's top
          // edge and a long way above the card it names. It now sits on the
          // vertical middle of the title card, with a minimum gap so it never
          // touches the panel's edge.
          if (nodes[i].classList.contains('title'))
            ys[i] = Math.max(NB_INSET, ys[i] === null ? NB_INSET : ys[i]);
          else if (nodes[i].classList.contains('end')) {
            // 2026-09-24av — ON THE LAST LINE OF TEXT, not on the box.
            // The end bar's anchor resolves to the whole closing block, whose
            // middle sits well above the sentence the reader actually stops
            // at. The mark belongs level with that last line.
            var endEl = els[i];
            if (endEl && endEl.getBoundingClientRect().height <= 4)
              endEl = endEl.nextElementSibling;
            var lastLine = null;
            // 2026-09-28b (K2.2) — ON THE HEADING "End of the guided part".
            // 24av put the mark on the last line of the closing block, which
            // is the small note under the heading: with the heading on the
            // reading line the mark stood 39 px below it (measured, 28a). The
            // heading is what the mark is named after and what the eye stops
            // at; the note is its footnote. The last line stays the fallback
            // for a closing block without a heading.
            var endH = endEl && endEl.querySelector ? endEl.querySelector('.nbend-h') : null;
            if (endH && endH.getBoundingClientRect().height > 4) lastLine = endH;
            if (!lastLine && endEl && endEl.querySelectorAll) {
              var kids = endEl.querySelectorAll('div,p');
              for (var q3 = kids.length - 1; q3 >= 0; q3--) {
                var kr = kids[q3].getBoundingClientRect();
                if (kr.height > 4 && (kids[q3].textContent || '').trim()) {
                  lastLine = kids[q3]; break;
                }
              }
            }
            if (lastLine) {
              ys[i] = offIn(sc, lastLine, scRect, z, true) - inset;
              nodes[i].__nbAim = [lastLine, 1];
            }
          }
          else if (nodes[i].classList.contains('cell')) {
            // 2026-09-24au — MEASURED, like every other mark.
            // "end + 54px" was a guess at where the strip you click to add a
            // cell sits, and a guess cannot line up with it: the reader hovers
            // the bar at the foot of the notebook and its mark is somewhere
            // else. JupyterLab's footer is a real element, so it is measured
            // with the same mapping every other mark uses. The old offset
            // stays as the fallback for front ends that have no footer
            // (JupyterLite, Colab, a plain nbconvert page).
            var foot = sc ? (byCls(sc, 'jp-Notebook-footer')
                          || byCls(sc, 'jp-WindowedPanel-footer')) : null;          // E22.1b
            var yF = null;
            if (foot && foot.getBoundingClientRect().height > 2)
              yF = offIn(sc, foot, scRect, z, true) - inset;
            if (yF === null) {
              var yE = null, q2;
              for (q2 = 0; q2 < nodes.length; q2++)
                if (nodes[q2].classList.contains('end')) yE = ys[q2];
              yF = yE !== null ? yE + 54 : Math.max(ys[i], H - NB_INSET);
            }
            // 2026-09-24av — AND IT KEEPS THE TITLE'S OWN MARGIN.
            // The reader asked for the mark at the foot of the rail to stand
            // as far from the bottom edge as the title mark does from the top.
            // That distance is not the 18px floor — the title mark is MEASURED
            // on its card and lands wherever the card is (149px in the build
            // this was written against). So the title's own y is what gets
            // mirrored, and the constant is only the fallback.
            // …and the margin belongs to the RAIL, not to the mark. Pinning
            // the mark to H - 149 pulled it ABOVE the end-of-the-guided-part
            // mark, which sits lower in the document — measured, cell at 2151
            // against end at 2230. So the mark stays where the footer is, and
            // the rail is told to leave the title's own gap below it.
            ys[i] = yF;
            var yT = null, q4;
            for (q4 = 0; q4 < nodes.length; q4++)
              if (nodes[q4].classList.contains('title')) yT = ys[q4];
            host.dataset.railFoot = String(Math.round(
                yF + (yT === null ? NB_INSET : yT)));
          }
        }
        // ==================================================================
        // ==================================================================
        // 2026-09-24bd — A MARK STANDS LEVEL WITH ITS PILL. AGAIN.
        //
        // 24aw replaced that with even, structural spacing, and it was an
        // over-correction of my own making. The evidence I acted on was five
        // Appendix marks landing within two pixels of one another — but those
        // marks were ALREADY hidden, because their section was folded. The
        // marks actually on screen were 51..96px apart: tight against a 44px
        // mark, never overlapping. I traded the one property the rail is for
        // against a problem that was not on the screen.
        //
        // So the document's position is the position again, and the pile is
        // handled where it actually occurs: a pass that pushes apart only the
        // pairs that would really collide, by only as much as they need, and
        // never out of order. Everywhere else — which is nearly everywhere —
        // a mark is exactly level with its pill.
        var docY = ys.slice();
        var vis = [];
        for (i = 0; i < nodes.length; i++)
          if (!nodes[i].classList.contains('nbgone')) vis.push(i);
        // how much room one mark needs along the column, from its own size
        var needOf = function(nd){
          var m = nd.querySelector('.nbsect,.nbchapdot,.nbsubdot,.nbrail-dot,'
                                 + '.nbvizmark,.nbcodemark');
          if (!m) return 10;
          var c = getComputedStyle(m), w = parseFloat(c.width) || 10;
          // a diamond is a square turned 45°: what has to fit is its diagonal
          return (c.transform.indexOf('0.707') >= 0 ? w * 1.4142 : w);
        };
        // 2026-09-25c — THE AIR BETWEEN TWO MARKS IS A SHARE OF THEIR SIZE.
        // It was a flat 3px, whatever the marks. Measured with every chapter
        // open and the document zoomed all the way out, that produced a
        // tightest gap of 2.6px between two 50px section diamonds — no overlap,
        // the rule did its job, but two marks 2.6px apart read as one blob, and
        // each of them carries a glow that is wider than the gap. "No overlap"
        // was true and still looked wrong.
        // A tenth of the two marks' own extent is 7-8px for the big ones and
        // 4-5px for the small: enough to read as two things, small enough that
        // a mark stays level with its pill, which is the property this whole
        // pass nearly cost once before (see the note above).
        var airFor = function(a, b){ return 3 + (a + b) * 0.05; };
        // 2026-09-29 (E8.1 + E8.28, Struktur) — THE MARKS SHRINK, THEY DO NOT
        // STEP ASIDE. Zoomed out, the pills of the document come closer
        // together than the marks are tall, and the pass below pushed the marks
        // apart — off their pills: measured at 60 %% with the panel wide, "Own
        // cell 1–6" stood well below their cells. Now one scale for all marks
        // is taken first, the largest at which every pair still fits between
        // its own two pills (never below 0.4); the push below is then left
        // with nothing — or next to nothing — to do. The scale is written as
        // `--nbmkz` on the host (for the stylesheet) and applied as `scale`
        // on each mark's glyph — not `zoom`, which scales the glyph's offsets
        // too and pushed the marks off the lane (first sketch).
        var mkz = 1, n0 = [], v0;
        var MKSEL = '.nbsect,.nbchapdot,.nbsubdot,.nbrail-dot,.nbvizmark,.nbcodemark';
        // (needOf reads the laid-out width, which `scale` does not touch: the
        // zoom of the last pass stays on — E21 Rest, see glyphZoom below)
        for (v0 = 0; v0 < vis.length; v0++) n0.push(needOf(nodes[vis[v0]]));
        if (vis.length > 1) {
          for (v0 = 1; v0 < vis.length; v0++) {
            var gap0 = docY[vis[v0]] - docY[vis[v0 - 1]];
            if (!(gap0 > 2)) continue;          // one pill, two marks: the push decides
            var req0 = (n0[v0] + n0[v0 - 1]) / 2 + airFor(n0[v0], n0[v0 - 1]);
            if (gap0 < req0) mkz = Math.min(mkz, gap0 / req0);
          }
          mkz = Math.max(0.4, Math.round(mkz * 50) / 50);
        }
        if (Math.abs((host.__nbMkz || 1) - mkz) > 0.001) {
          host.__nbMkz = mkz;
          host.style.setProperty('--nbmkz', String(mkz));
        }
        // 2026-10-03 (E21 Rest, Struktur) — THE SCALED MARK STAYS ON ITS PILL.
        // A mark is scaled about its own centre: `scale` turns about the
        // glyph's transform-origin, and the glyph's `transform` (translate
        // −50 %, the turn of a diamond) lies between the two, so the centre
        // moves by (1 − s) × q, q = the centre's place after `transform`,
        // seen from the origin; `translate` gives that back. This was read
        // off the page: centre before, `scale` set, centre after. Since
        // E18.6 (01-base) `scale` and `translate` are TRANSITIONED, so the
        // read right after setting `scale` still saw the old value: before ==
        // after, nothing given back, and once the transition had run the mark
        // stood (1 − s) × 12.7 px below its pill — measured v1.62 probe at
        // GUI 100 % (s 0.86): title mark 267.8 vs reading line 266.0
        // (lab_readline), names 1.3–1.7 px above their marks, T +1.8 px
        // (lab_k2 N/T); with s ≈ 0.75 2.4–3.6 px (lab_k2 Z). And every pass
        // took the zoom off first and read the centre while the transition
        // back had not even begun. Now q is computed from the computed
        // `transform` matrix and `transform-origin` (no layout read of a
        // moving box), the pair is written only when it changes, and because
        // `scale` and `translate` share one transition, the centre stays put
        // during it as well: (s(t) − 1)·q + (1 − s)·q·e(t) = 0.
        var glyphZoom = function(g, s){
          var want = s < 1 ? String(s) : '', tr = '';
          if (want) {
            var cs = getComputedStyle(g), o = String(cs.transformOrigin || '').split(' ').map(parseFloat);
            var mt = String(cs.transform || ''), v = null, a = 1, b = 0, c = 0, d = 1, e = 0, f = 0;
            if ((v = /^matrix\(([^)]*)\)/.exec(mt))) {
              v = v[1].split(',').map(parseFloat); a = v[0]; b = v[1]; c = v[2]; d = v[3]; e = v[4]; f = v[5];
            } else if ((v = /^matrix3d\(([^)]*)\)/.exec(mt))) {
              v = v[1].split(',').map(parseFloat); a = v[0]; b = v[1]; c = v[4]; d = v[5]; e = v[12]; f = v[13];
            }
            var x = g.offsetWidth / 2 - (o[0] || 0), y = g.offsetHeight / 2 - (o[1] || 0);
            var dx = (1 - s) * (a * x + c * y + e), dy = (1 - s) * (b * x + d * y + f);
            if (Math.abs(dx) > 0.05 || Math.abs(dy) > 0.05) tr = dx.toFixed(2) + 'px ' + dy.toFixed(2) + 'px';
          }
          // 2026-10-05 (E22.9, Struktur) — WHILE THE LENS OR A HAND MOVES, THE
          // SCALE IS SET, NOT SLID. `scale`/`translate` are transitioned
          // (E18.6, 0.2 s); a new crowding scale per lens step then slid
          // after the lens size that changes at once — measured v1.63 +
          // E22.9, two notebooks open, Complex in front, Ctrl+wheel ±5: a
          // mark 29.9 → 31.4 → 29.4 → 30.7 … px, steps of 1.4 px against
          // the zoom's direction. During a gesture (`data-nbmoving`, 18) the
          // glyph takes it in the same frame; afterwards the transition is
          // its own again (moving() clears it).
          if ((g.style.scale !== want || g.style.translate !== tr) && host.hasAttribute('data-nbmoving')
              && g.style.getPropertyValue('transition-duration') !== '0s')
            g.style.setProperty('transition-duration', '0s', 'important');
          if (g.style.scale !== want) g.style.scale = want;
          if (g.style.translate !== tr) g.style.translate = tr;
        };
        for (i = 0; i < nodes.length; i++) {
          var gm = nodes[i].querySelector(MKSEL);
          if (gm) glyphZoom(gm, mkz);
        }
        if (vis.length > 1) {
          var need = [], vi;
          for (vi = 0; vi < vis.length; vi++) need.push(n0[vi] * mkz);
          // forwards: nobody may sit closer to the one above than half the two
          // marks together, plus the air
          for (vi = 1; vi < vis.length; vi++) {
            var floor = ys[vis[vi - 1]] + (need[vi] + need[vi - 1]) / 2
                      + airFor(need[vi], need[vi - 1]);
            if (ys[vis[vi]] < floor) ys[vis[vi]] = Math.round(floor);
          }
          // …and if that pushed the last one past the end of the rail, take the
          // whole thing back up again, still in order
          var lastV = vis[vis.length - 1];
          var over = ys[lastV] - docY[lastV];
          if (over > 0) {
            for (vi = vis.length - 1; vi > 0; vi--) {
              var ceil = ys[vis[vi]] - (need[vi] + need[vi - 1]) / 2
                       - airFor(need[vi], need[vi - 1]);
              if (ys[vis[vi - 1]] > ceil) ys[vis[vi - 1]] = Math.round(ceil);
            }
          }
        }
        // the marker needs both tables: where a mark IS in the document, and
        // where it is drawn on the rail. They are the same nearly everywhere
        // now, so the mapping below is the identity except across a collision.
        host.__nbDocY  = docY;
        host.__nbRailY = ys.slice();
        host.__nbVis   = vis;
        for (i = 0; i < nodes.length; i++) {
          var t = ys[i] + 'px';
          if (nodes[i].style.top !== t) nodes[i].style.top = t;
        }
        // A PILE IS NOT A LIST (2026-09-24t).
        // With every chapter folded shut the headings are some forty pixels
        // apart in the document, and forty pixels of document is forty pixels of
        // rail — at a narrow panel that is less than a line of text, so seven
        // chapter names printed one over the other. A name that cannot be read
        // is not a name: the ones that would collide are taken off, the mark
        // stays, and hovering brings the name back.
        var thickNow = parseFloat(getComputedStyle(document.documentElement)
                         .getPropertyValue('--nbthick')) || 1;
        // the label's OWN height, not a guess from the thickness: the two do
        // not always scale together, and a guess is what let them overlap
        // the marks are half again as big on the vertical rail, so two of them
        // need half again as much room before one has to give way
        var needDot = Math.max(6, Math.round(11 * thickNow));
        var lastLab = -1e9, lastDot = -1e9;
        for (i = 0; i < nodes.length; i++) {
          var nd = nodes[i];
          if (nd.classList.contains('nbgone')) continue;
          // a low-rank mark landing ON the one above it is a pile too
          var minor = nd.classList.contains('sub') || nd.classList.contains('task')
                   || nd.classList.contains('codetask');
          if (minor && ys[i] - lastDot < needDot) { nd.classList.add('nbgone'); continue; }
          lastDot = ys[i];
          var lb = nd.querySelector('.nbmap-lab');
          if (!lb || !(lb.textContent || '').trim()) continue;
          var lh = Math.round(lb.getBoundingClientRect().height) || 14;
          if (ys[i] - lastLab < lh + 3) nd.classList.add('nblabgone');
          else { nd.classList.remove('nblabgone'); lastLab = ys[i]; }
        }
        // NO MERGING. A circle carrying "4" was a fourth kind of mark that meant
        // something different from the other three, and it appeared exactly when
        // the rail was already hard to read. Collapsing a chapter now takes its
        // points off the rail altogether (see nbgone above), which is what the
        // merge was standing in for.
        inner.querySelectorAll('.nbmap-merge').forEach(function(e){ e.remove(); });
        inner.querySelectorAll('.nbmap-node.nbfolded').forEach(function(n){
          n.classList.remove('nbfolded'); });
        // lock the rail to the document — this is what makes them parallel
        var want = Math.round(sc.scrollTop * z);
        // 2026-09-24o — THE RAIL STOPS WHERE THE NOTEBOOK STOPS.
        // JupyterLab's "scroll past end" adds a whole blank screen under the
        // last cell, and the rail is as long as the document INCLUDING it. So
        // scrolling to the bottom showed a screenful of empty rail and the end
        // bar was somewhere above, off the top. The rail now refuses to scroll
        // past the point where the end bar is still in view.
        var y1 = parseInt(host.dataset.railY1 || '0', 10) || 0;
        if (y1 > 0) {
          // generous: with scroll-past-end gone (see unlockCell) the rail is
          // 1:1 with real content and this never bites. It is the guard for a
          // front end that puts the blank tail back before our sync has run.
          var maxTop = Math.max(0, y1 + 160 - map.clientHeight);
          // 2026-09-27d — …but it may always run until the LAST mark (your
          // own cell) stands on the reading line, which is what the room
          // footAir() hangs under the document is for. Clamped at the end bar
          // the rail stopped short of the document and the two came apart.
          var y0g = parseInt(host.dataset.railY0 || '0', 10) || 0;
          var yLast = ys.length ? ys[ys.length - 1] : 0;
          if (y0g > 0 && yLast > y0g) maxTop = Math.max(maxTop, yLast - y0g + (window.__nbAirX || 0));
          if (want > maxTop) want = maxTop;
        }
        if (Math.abs(map.scrollTop - want) > 1) {
          window.__nbrailSelfScroll = true;
          window.__nbrailSelfAt = Date.now();
          map.scrollTop = want;
        }
        return {ys: ys, nodes: nodes, H: H};
      }

      // ---- dots that have collapsed onto each other ------------------------
      // Fold a section shut and the sections inside it lose their height: their
      // dots pile up into one grey smudge that says nothing. So a run of dots
      // that has closed up is replaced by ONE dot carrying the count — the
      // detail disappears with the sections it describes, and what is left
      // still says how much is in there. Open the section again and the dots
      // come back, because nothing was removed, only hidden.
      var MERGE_GAP = 26;
      function mergeDots(inner, nodes, ys){
        var runs = [], run = [], i;
        var flush = function(){ if (run.length > 1) runs.push(run); run = []; };
        for (i = 0; i < nodes.length; i++) {
          var n = nodes[i];
          // section bars are landmarks and exercise circles carry state: only
          // the plain dots are ever folded together
          if (n.classList.contains('sect') || n.classList.contains('task')) { flush(); continue; }
          // a node whose chapter is shut is not on the rail at all, so it has
          // nothing to be merged with
          if (n.classList.contains('nbgone')) { flush(); continue; }
          if (run.length && ys[i] - ys[run[run.length - 1]] > MERGE_GAP) flush();
          run.push(i);
        }
        flush();
        var hidden = {};
        runs.forEach(function(r){ r.forEach(function(k){ hidden[k] = true; }); });
        for (i = 0; i < nodes.length; i++)
          nodes[i].classList.toggle('nbfolded', !!hidden[i]);
        var pills = inner.querySelectorAll('.nbmap-merge');
        for (i = 0; i < runs.length; i++) {
          var r = runs[i];
          var pill = pills[i];
          if (!pill) {
            pill = document.createElement('a');
            pill.className = 'nbjump nbmap-merge';
            inner.appendChild(pill);
          }
          var first = nodes[r[0]];
          var tgt = first.getAttribute('data-target') || '';
          if (pill.getAttribute('data-target') !== tgt) {
            pill.setAttribute('data-target', tgt);
            pill.setAttribute('href', '#' + tgt);
          }
          var mid = Math.round((ys[r[0]] + ys[r[r.length - 1]]) / 2);
          if (pill.style.top !== mid + 'px') pill.style.top = mid + 'px';
          var txt = String(r.length);
          if (pill.textContent !== txt) pill.textContent = txt;
          pill.title = r.length + nbL(' sections in here — click to open them', ' Abschnitte hier; ein Klick öffnet sie');
        }
        for (var m = runs.length; m < pills.length; m++) pills[m].remove();
      }

      // The same three lanes as across the top, drawn downwards: the track from
      // the first marker to the last, the green XP from the first exercise to the
      // one you are standing on, the purple glow behind it, and the amber or red
      // stripe over the stretch a skip or a give-up opened.
      function vertGauge(host, lay){
        var inner = host.querySelector('.nbmap-inner');
        if (!inner || !lay) return;
        var nodes = lay.nodes, ys = lay.ys;
        if (!nodes.length) return;
        var isSolved = function(d){
          return d.classList.contains('st-ans') || d.classList.contains('st-both');
        };
        var yOf = function(n){
          for (var i = 0; i < nodes.length; i++) if (nodes[i] === n) return ys[i];
          return null;
        };
        var y0 = ys[0], y1 = ys[ys.length - 1];
        // Progress belongs to the ONE block that holds exercises, exactly as it
        // does across the top: the lane starts on that block's section bar and
        // stops on its last marker. Introduction carries none, and neither does
        // the Appendix — the quiz and 'bring your own data' are exercises, but
        // they are not the route through the notebook, so the green must stop at
        // the last chapter instead of running on into them.
        var f0 = y0, f1 = y1, first = -1, i, k;
        for (i = 0; i < nodes.length; i++)
          if (nodes[i].classList.contains('task')) { first = i; break; }
        if (first > -1) {
          for (k = first; k >= 0; k--)
            if (nodes[k].classList.contains('sect')) { f0 = ys[k]; break; }
          var seen = false;
          for (i = 0; i < nodes.length; i++) {
            if (nodes[i].classList.contains('sect')) {
              if (seen) break;                       // the next block starts here
              if (ys[i] === f0) seen = true;
              continue;
            }
            if (seen) f1 = ys[i];
          }
        }
        // THE LINE RUNS FROM THE TITLE TO THE END OF THE NOTEBOOK.
        // The last marker on the rail is the empty cell JupyterLab leaves under
        // the document — past the end of what was written. The line, and with it
        // the marker's travel, stops one bar earlier, on "end of the guided
        // part": that is where the notebook ends and where the reader is told it
        // ends. The cell's bar stays, outside the line, because it is still a
        // place you can jump to.
        var yEnd = y1;
        for (i = nodes.length - 1; i >= 0; i--)
          if (nodes[i].classList.contains('end')) { yEnd = ys[i]; break; }
        inner.style.setProperty('--rail-y0', y0 + 'px');
        inner.style.setProperty('--rail-h', Math.max(0, yEnd - y0) + 'px');
        // 2026-09-24av — the column is at least as tall as the last mark plus
        // the gap the title mark has at the top, so the two ends of the rail
        // are framed alike.
        var wantFoot = parseInt(host.dataset.railFoot || '0', 10) || 0;
        if (wantFoot > 0) {
          var nowH = parseFloat(getComputedStyle(inner).height) || 0;
          if (wantFoot > nowH) inner.style.minHeight = wantFoot + 'px';
          else if (inner.style.minHeight) inner.style.minHeight = '';
        }
        // markCentre() cannot measure the nodes, so the two ends are left here
        var hostEl = inner.closest ? inner.closest('.nbpanel-host') : null;
        if (hostEl) {
          // E9.2: the title's height WITHOUT the air above it (headAir)
          var scA = scroller(hostEl), airA = scA && scA.querySelector(':scope > .nbhead-air');
          // E15.6: the margin too — a line ABOVE the title (dragged up, or
          // a lens > 100 %%) pulls the page up by a negative margin; left in,
          // the title's height followed the line and the line ran away
          // from the pointer (measured: 80 px drag → 223 px)
          if (airA) y0 -= (parseFloat(airA.style.height) || 0) + (parseFloat(airA.style.marginTop) || 0);
          // 2026-09-28b (K2.5) — THE CURSOR DOES NOT MOVE WITH THE MAGNIFIER.
          // The line is the title mark's height when the notebook opens
          // (§4b). The magnifier scales the title card too, and the line used
          // to follow it: the cursor jumped with every step of the lens. The
          // line is taken at the zoom it was measured at and kept while the
          // zoom is different; back at that zoom it is measured again.
          var zNow = (typeof zoomLevel === 'function') ? zoomLevel() : 100;
          var zAt = parseInt(hostEl.dataset.railZ || '0', 10) || 0;
          var liftZ = parseInt(hostEl.dataset.railLiftZ || '0', 10) || 0;
          var moved = liftZ === zNow
                   && Math.abs(y0 - (parseFloat(hostEl.dataset.railY0z) || 0)) > 1;
          if (!zAt || zAt === zNow || !hostEl.dataset.railY0n || moved) {
            // 2026-09-30 (E10.7, Struktur) — THE LINE IS TAKEN AT 100 %,
            // WHATEVER LENS THE NOTEBOOK OPENS WITH. Measured at the stored
            // lens, the line followed it: 209 px at 60 %, 349 at 150 %, 266
            // at 100 % (v1.35, 1400 × 900). The title card is now read as it
            // stands at 100 %: the lens (CSS zoom on the cell wrappers) is
            // lifted for one synchronous read and put back before anything
            // is painted; the scroll is restored with it. The line then
            // counts as measured at 100 % (railZ), so it is kept at every
            // other lens (K2.5) and re-measured only back at 100 %.
            // While the lens stays the one it was lifted at, the line is
            // lifted again only when the card has moved there (the page is
            // still settling), not on every pass.
            var y0m = Math.round(y0), zm = zNow;
            delete hostEl.dataset.railLiftZ;
            if (zNow !== 100) {
              var dl = titleAt100(hostEl);
              if (dl !== null) {
                y0m = Math.round(y0 + dl); zm = 100;
                hostEl.dataset.railLiftZ = String(zNow);
                hostEl.dataset.railY0z = String(Math.round(y0));
              }
            }
            hostEl.dataset.railY0n = String(y0m);
            hostEl.dataset.railZ = String(zm);
          }
          // 2026-09-30 (E9.1, Struktur + Applikation) — THE READING HEIGHT IS
          // THE READER'S. railY0n is the title mark's height (as before);
          // the line is that plus what the reader dragged the fold knob by
          // (rlOff, 14-grip), kept inside the rail's window.
          // E15.6: and a stored offset the window cannot show is clamped
          // where it is kept — once, when the panel first stands (ready):
          // a window made small for a moment does not move it for good.
          var nY = parseInt(hostEl.dataset.railY0n, 10) || Math.round(y0), oY = rlOff();
          var LY = rlLine(hostEl, nY + oY);
          hostEl.dataset.railY0 = String(LY);
          if (!window.__nbRlChk && hostEl.classList.contains('ready')) {
            window.__nbRlChk = 1;
            if (LY - nY !== oY) try { localStorage.setItem(rlKey(), String(LY - nY)); } catch (e) {}
          }
          hostEl.dataset.railY1 = String(Math.round(yEnd));
        }
        inner.style.setProperty('--fill-y0', f0 + 'px');
        var r = reachedNode(inner, isSolved);
        var end = r.node ? yOf(r.node) : f1;
        if (end === null) end = f1;
        end = Math.max(f0, Math.min(end, f1));
        var fill = inner.querySelector('.nbmap-fill:not(.tail):not(.code)');
        var tail = inner.querySelector('.nbmap-fill.tail');
        var code = inner.querySelector('.nbmap-fill.code');
        // the horizontal gauge writes inline WIDTHS; left behind they turn the
        // vertical lanes into giant lozenges the moment the radius rounds them
        [fill, tail, code].forEach(function(e){
          if (!e) return;
          if (e.style.width) e.style.width = '';
          if (e.style.left)  e.style.left  = '';
        });
        // THE LANE IS MADE OF SEGMENTS (2026-09-24q).
        // One per settled exercise, from the previous circle to its own: green
        // where it was answered, amber where it was skipped, red where a wrong
        // answer was entered. Answer a skipped or wrong one correctly and its
        // own stretch turns green — the bar is a record of the route, not a
        // single frontier.
        var segHost = inner.querySelector('.nbmap-segs');
        if (!segHost) {
          segHost = document.createElement('span');
          segHost.className = 'nbmap-segs';
          inner.appendChild(segHost);
        }
        // 2026-09-24y — THE RUN STARTS AT THE CHAPTER, NOT AT THE LAST MARK.
        // It used to run from whatever mark came before, which for the first
        // exercise of a chapter meant the section bar above it: skipping one
        // question painted a stretch of rail belonging to two chapters. A
        // colour on this lane says something about ONE chapter, so it begins at
        // that chapter's own point — and that point takes the colour with it.
        // 2026-09-24ad — ONE EXERCISE, ONE SHORT STRETCH.
        // The run used to reach from the chapter's own point all the way down
        // to the exercise — 755px measured, most of it rail that belongs to the
        // chapter's text, not to the question. A colour on this lane now covers
        // exactly what it is about: from the exercise's own mark to the NEXT
        // mark on the rail, which for an exercise that has a coding twin is
        // that twin's mark. The chapter's point still takes the colour (that is
        // what says "something happened in this chapter" at a glance), but the
        // band no longer pretends the whole chapter was answered.
        // 2026-09-24ae — BOTH KINDS OF EXERCISE PAINT, AND NOTHING ELSE DOES.
        // A stretch of colour belongs to the exercise it came from and reaches
        // to the next mark on the rail. The coding exercise is an exercise, so
        // it gets exactly the same treatment from its own circle. The chapter's
        // point is no longer tinted along with it: a chapter is not a thing
        // that can be passed, skipped or given up, and colouring it said it was.
        var segs = [], ti, tj, dt, st2;
        for (ti = 0; ti < nodes.length; ti++) {
          var isTask = nodes[ti].classList.contains('task');
          var isCode = nodes[ti].classList.contains('codetask');
          if (!isTask && !isCode) continue;
          st2 = '';
          if (isTask) {
            dt = nodes[ti].querySelector('.nbrail-dot');
            if (dt) {
              if (dt.classList.contains('st-ans') || dt.classList.contains('st-both'))
                st2 = 'done';
              else if (dt.classList.contains('st-skip')) st2 = 'skip';
              else if (dt.classList.contains('st-fail')) st2 = 'fail';
            }
          } else {
            dt = nodes[ti].querySelector('.nbcodemark');
            if (dt) {
              // 2026-09-24au — the coding route paints in ITS colour. A solved
              // coding exercise used to tint the lane green, which is the other
              // route's colour and said the wrong thing about which ladder the
              // reader had climbed.
              if (dt.classList.contains('cd-done')) st2 = 'code';
              else if (dt.classList.contains('cd-skip')) st2 = 'skip';
              else if (dt.classList.contains('cd-fail')) st2 = 'fail';
            }
          }
          if (!st2) continue;
          // the next mark that is actually ON the rail. A mark inside a folded
          // chapter is not, so the band must not end at one: it would stop in
          // the middle of nothing.
          var endY = null;
          for (tj = ti + 1; tj < nodes.length; tj++) {
            if (nodes[tj].classList.contains('nbgone')) continue;
            if (ys[tj] === null) continue;
            endY = ys[tj];
            break;
          }
          if (endY === null) endY = f1;
          if (endY > ys[ti]) segs.push([ys[ti], endY, st2]);
        }
        // 2026-09-29 (E6.8, Struktur) — THE SECOND BAR: the reader's own
        // cells. From "Own cell 1" down to "Your own cell", a stretch of its
        // own (data-s="own"); its colour is the style's: --nbxp2, else the
        // skin's second accent. Only while there is an own cell.
        var yOwn1 = null, yCellM = null;
        for (ti = 0; ti < nodes.length; ti++) {
          if (nodes[ti].classList.contains('nbgone') || ys[ti] === null) continue;
          if (yOwn1 === null && nodes[ti].classList.contains('own')) yOwn1 = ys[ti];
          if (nodes[ti].classList.contains('cell')) yCellM = ys[ti];
        }
        if (yOwn1 !== null && yCellM !== null && yCellM > yOwn1) segs.push([yOwn1, yCellM, 'own']);
        // and whatever an older pass tinted on a chapter point comes back off
        for (ti = 0; ti < nodes.length; ti++)
          nodes[ti].classList.remove('ch-done', 'ch-skip', 'ch-fail');
        while (segHost.children.length > segs.length)
          segHost.removeChild(segHost.lastChild);
        while (segHost.children.length < segs.length) {
          var sp = document.createElement('span');
          sp.className = 'nbseg';
          segHost.appendChild(sp);
        }
        for (ti = 0; ti < segs.length; ti++) {
          var sg = segHost.children[ti];
          if (sg.getAttribute('data-s') !== segs[ti][2])
            sg.setAttribute('data-s', segs[ti][2]);
          var sTop = segs[ti][0] + 'px';
          var sH = Math.max(0, segs[ti][1] - segs[ti][0]) + 'px';
          if (sg.style.top !== sTop) sg.style.top = sTop;
          if (sg.style.height !== sH) sg.style.height = sH;
          var bgO = segs[ti][2] === 'own' ? 'var(--nbxp2, var(--nbskin-acc2, #2c6e91))' : '';
          if (sg.style.background !== bgO && (bgO || sg.style.background)) sg.style.background = bgO;
        }
        // Standing on its side the segments ARE the lane, so the one-piece green
        // bar underneath them is turned off — two bars saying different things
        // about the same stretch is how a reader stops trusting either.
        if (fill) fill.style.height = vertOn() ? '0px' : (end - f0) + 'px';
        if (tail && tail.style.opacity !== '0') {
          tail.style.height = '0px'; tail.style.width = '0px'; tail.style.opacity = '0';
        }
        if (code) {
          // 2026-09-24u — THE PURPLE LANE IS GONE.
          // Two lanes on one line asked the reader to hold two progressions in
          // their head at once. The coding route keeps its own MARK on the rail
          // — a circle of its own, green when it is solved — which says the same
          // thing in the place where it belongs.
          code.style.height = '0px';
          code.style.opacity = '0';
        }
        // The interruption in front of every further section bar, turned on its
        // side: the line stops at the last marker of one block and starts again
        // on the next block's bar, so Content, Introduction and the Appendix each
        // read as one piece of line with nothing sticking out.
        // ONE CONTINUOUS LINE. The gaps used to paint over the track between a
        // block's last marker and the next block's landmark, so that the three
        // groups read as three pieces. They also broke the one thing the rail is
        // for: showing that a notebook is a single run from the title to the
        // end. The landmarks say where the blocks begin; the line does not have
        // to be cut for that.
        var want = [];
        var bars = inner.querySelectorAll('.nbmap-gap');
        var fl = inner.querySelectorAll('.nbmap-fill');
        var anch = fl.length ? fl[fl.length - 1] : null;
        for (var b = 0; b < want.length; b++) {
          var bar = bars[b];
          if (!bar) {
            bar = document.createElement('span');
            bar.className = 'nbmap-gap';
            if (anch && anch.nextSibling) inner.insertBefore(bar, anch.nextSibling);
            else inner.appendChild(bar);
          }
          if (bar.style.left)  bar.style.left = '';
          if (bar.style.width) bar.style.width = '';
          var T = want[b][0] + 'px';
          var H = Math.max(0, want[b][1] - want[b][0]) + 'px';
          if (bar.style.top !== T) bar.style.top = T;
          if (bar.style.height !== H) bar.style.height = H;
        }
        for (var m2 = want.length; m2 < bars.length; m2++) bars[m2].remove();
      }

      // Vertical needs room beside the document, not above it. The strip is taken
      // off the SCROLLER, so the content column re-centres inside what is left
      // instead of sliding out from under the panel.
      function vertReserve(host, src){
        var sc = scroller(host);
        if (!sc) return;
        var z = pageZoom();
        // the toolbar floats over the top of the document, so the document is
        // pushed down by exactly its height — the same rule the banner had
        var nb = src.closest('.jp-Notebook') || src.closest('.jp-NotebookPanel');
        var dk = dockOf(host);
        // The strip belongs to the TOOLBAR, never to the drawer. Measuring the
        // whole dock meant that opening a widget pushed the document down and
        // dragged the rail with it — the reader lost their place to a settings
        // panel. The drawer opens OVER the page instead, on top of everything.
        var row = dk && dk.querySelector('.nbctrl');
        if (nb && dk) {
          var dh = Math.ceil(((row || dk).getBoundingClientRect().height + 18) / z / 4) * 4;
          // R2 · 17 — no toolbar: the document starts right under JupyterLab's
          // bar, with the same small strip at every size
          if (NB_CORNERS) dh = 16;
          var cur0 = parseInt(nb.dataset.nbpad || '0', 10);
          if (dh >= 16 && Math.abs(cur0 - dh) > 3) {
            nb.style.paddingTop = dh + 'px';
            nb.dataset.nbpad = String(dh);
          }
        }
        // 2026-09-27b — NOTHING IS RESERVED BESIDE THE DOCUMENT ANY MORE.
        // The panel lies over it (STRUKTUR §4). A value an older build wrote
        // into this window is taken back, so no stale strip survives.
        var root2 = document.documentElement.style;
        ['--nbvert-pad', '--nbdock-cut', '--nbfoot-w'].forEach(function(k){
          if (root2.getPropertyValue(k)) root2.removeProperty(k);
        });
        // an older build padded the scroller itself — undo it
        if (sc.style.paddingRight) { sc.style.paddingRight = ''; }
        if (sc.dataset.nbpadr) { delete sc.dataset.nbpadr; }
      }

      function vertPlace(host, src){
        var sc = scroller(host);
        var rail = railOf(host);
        if (!sc || !rail) return;
        var z = pageZoom();
        var r = sc.getBoundingClientRect();
        // IN FULL SCREEN THE WINDOW IS THE DOCUMENT. The scroller's box can lag
        // a frame or two behind the resize — and the rail, pinned to its right
        // edge, then stops a few hundred pixels short of the screen and stays
        // there. The full-screen element IS the page, so its own box is the
        // honest one to pin to.
        var fsEl = document.fullscreenElement || document.webkitFullscreenElement || null;
        if (fsEl && fsEl !== document.documentElement && fsEl !== document.body) {
          var fr = fsEl.getBoundingClientRect();
          if (fr.width > 200) {
            r = {left: fr.left, right: Math.max(fr.right, window.innerWidth),
                 top: r.top, bottom: Math.max(fr.bottom, window.innerHeight),
                 width: fr.width, height: fr.height};
          }
        }
        // sit to the LEFT of the front end's own scrollbar, so the two run side
        // by side instead of one covering the other
        var barW = Math.max(0, sc.offsetWidth - sc.clientWidth);
        // Read the width from the STYLE, not from the box. Measuring the host
        // right after the .vert class goes on can still return the horizontal
        // width — the panel is then placed a thousand pixels too far left, which
        // is what buried the timeline against the edge of the document.
        var w = parseInt(getComputedStyle(document.documentElement)
                  .getPropertyValue('--nbvert-w'), 10);
        if (!w || w < 1) w = 300;
        // The toolbar floats over the top of the document, so the rail starts
        // UNDER it — otherwise the first bar, the title page, is hidden behind
        // the very controls the reader would use to find it.
        // Derived from the toolbar's HEIGHT, not from where it was measured to
        // be: the toolbar is pinned 8px under the document's top edge, so its
        // bottom is r.top + 8 + height and nothing has to be read back. A rect
        // read in the same pass the toolbar was placed in is a race; an
        // offsetHeight is not.
        // The rail begins where the TOOLBAR ends — measured from the toolbar's
        // own box, because the toolbar is pinned to the notebook PANEL and the
        // scroller starts lower down. And it runs to the bottom of the window,
        // not to the bottom of the scroller: the reader asked for the full
        // height, and the scroller's box stops short of it.
        var dk = dockOf(host);
        // the CONTROL ROW's bottom, not the dock's: an open drawer must not move
        // the rail either
        var row0 = dk && dk.querySelector('.nbctrl');
        var dr = (row0 || dk) ? (row0 || dk).getBoundingClientRect() : null;
        // 2026-09-24z — THE TOOLBAR SWALLOWS IT.
        // The rail used to BEGIN under the toolbar, so nothing ever went in:
        // a mark scrolled up to the gap and then simply stopped existing. It
        // now starts at the toolbar's own top edge and runs up behind it — the
        // bar is opaque and in front, so a mark travelling up slides under it
        // and disappears there, the way the document does.
        var dkR = dk ? dk.getBoundingClientRect() : null;
        var y0 = dkR && dkR.height > 4 ? dkR.top
               : (dr && dr.height > 4 ? dr.bottom + 6
                  : (dk ? r.top + dk.offsetHeight + 8 : r.top));
        // what the reader actually sees begins below the bar; the strip above
        // is reserved so the marks have somewhere to disappear to
        var hide = dr && dr.height > 4 ? Math.max(0, Math.round(dr.bottom - y0)) : 0;
        document.documentElement.style.setProperty('--nbrail-hide', hide + 'px');
        // The document zoom must not touch the panel. The rail sits inside the
        // zoomed page, so it is scaled back by exactly the same factor, with the
        // origin at its TOP RIGHT — the corner it is pinned to. After that, a
        // length written here is a length on SCREEN: no conversion, and the
        // reader can shrink the document without the instrument shrinking too.
        var undo = z === 1 ? '' : 'scale(' + (1 / z) + ')';
        if (rail.style.transform !== undo) rail.style.transform = undo;
        var top = Math.round(y0 / z);
        // ...and never past the bottom of the document OR of the window,
        // whichever comes first: in the recording the rail hung out under the
        // notebook because the scroller's box reached past the screen.
        // 2026-09-24z — FLUSH WITH THE DOCUMENT, not with the window. The
        // window's bottom is below JupyterLab's status bar, so a rail measured
        // against it hung a status bar's worth past the end of the notebook.
        var endY = Math.min(window.innerHeight, r.bottom || window.innerHeight);
        var h = Math.round(endY - y0);
        // 2026-09-30 (E11.6, Struktur) — THE SCROLL BAR'S COLUMN. Cursor and
        // track are no longer part of the panel: they stand in a column of
        // SBW px right of it (placeCursor), between the panel and the front
        // end's own scroll bar. The panel moves left by that column; the
        // column is a tool and does not scale with the lens or the panel.
        // E12.3: the bar moved to the tools on the left — no column any more
        var SBW = window.__nbSbw = 0;
        var left = Math.round((r.right - barW) / z) - w - SBW;
        // 2026-09-24bi — THE PANEL'S RIGHT EDGE IS THE WINDOW'S RIGHT EDGE.
        // 24bh pulled the rail left until it stood beside the text; the reader
        // asked for it back against the edge, and for widening to grow the
        // panel INTO the page rather than move it. So the anchor is the right
        // edge again, and the lane keeps its place while the panel grows —
        // see applyGui(), where the axis is measured from that same edge.
        // A panel that has left the window cannot be turned back, because the
        // control that turns it lives on it. So both ends are clamped: whatever
        // the document's box says, the rail stays inside the window.
        var vw = Math.round(window.innerWidth / z), vh = Math.round(window.innerHeight / z);
        left = Math.max(2, Math.min(left, vw - w - SBW - 2));
        top  = Math.max(0, Math.min(top, vh - 60));
        h    = Math.max(60, Math.min(h, endY - Math.round(top * z)));
        // 2026-09-27b — the toolbar is no longer cut at the rail, and JupyterLab's
        // "click to add cell" strip keeps its own width: the panel lies over
        // both, the toolbar stands in front of it (§4, Vorhaben E).
        if (rail.style.top !== top + 'px') rail.style.top = top + 'px';
        if (rail.style.left !== left + 'px') rail.style.left = left + 'px';
        if (rail.style.height !== h + 'px') rail.style.height = h + 'px';
        if (rail.style.right !== 'auto') rail.style.right = 'auto';
        if (rail.style.bottom !== 'auto') rail.style.bottom = 'auto';
        // A fixed element is laid out against the VIEWPORT — except when an
        // ancestor establishes a containing block, which is exactly what full
        // screen does: the host is moved inside the notebook panel, and its
        // left/top are then measured from that box instead. Rather than guess
        // which ancestor it is, place it, look at where it actually landed, and
        // correct the difference. One pass, no oscillation: the correction is
        // only applied when it is more than a pixel.
        var got = rail.getBoundingClientRect();
        // 2026-09-24bh — AND IT CORRECTS TOWARDS THE LEFT WE CHOSE.
        // This aimed at the scroller's right edge, which is the same thing as
        // the rail's old anchor — so the moment the rail was asked to stand
        // beside the text instead, this line pulled it straight back to the
        // window's edge. Measured: left set to 1445, rail found at 1711.
        // The correction is for a containing block that is not the viewport
        // (full screen moves the host inside the notebook panel); it has to be
        // the difference between where we PUT it and where it landed.
        var dx = Math.round(((left * z) - got.left) / z);
        // ...against y0, not against the document's top edge. The rail starts
        // UNDER the toolbar now, and a correction that still aimed at the top
        // edge dragged it straight back up behind it — which is why the title
        // bar kept disappearing under the controls.
        var dy = Math.round((y0 - got.top) / z);
        if (Math.abs(dx) > 1) rail.style.left = (left + dx) + 'px';
        if (Math.abs(dy) > 1) rail.style.top  = (top + dy) + 'px';
        placeDock(host, src);
      }

      // Each orientation reserves room in a different direction, and a strip left
      // over from the other one is not cosmetic: the vertical layout measures the
      // scroller's clientHeight, and a stale paddingTop makes it 156px too tall —
      // so the panel hangs below the window and its controls go with it.
      function clearOther(host, src, vert){
        var nb = src.closest('.jp-Notebook') || src.closest('.jp-NotebookPanel');
        var sc = scroller(host);
        if (vert) {
          // the strip at the top belongs to the toolbar now, in BOTH
          // orientations — vertReserve() owns it, so it is not cleared here
        } else {
          if (sc && sc.style.paddingRight) { sc.style.paddingRight = ''; delete sc.dataset.nbpadr; }
          var rl = railOf(host);
          if (rl) { rl.style.height = ''; rl.style.width = ''; }
          // every trace of the rail: the inline heights and tops the vertical
          // layout wrote are meaningless across the top, and a leftover one
          // parks a node a whole document away from where it belongs
          var inr = host.querySelector('.nbmap-inner');
          if (inr && inr.style.height) inr.style.height = '';
          host.querySelectorAll('.nbmap-node').forEach(function(n){
            if (n.style.top) n.style.top = '';
            n.classList.remove('nbfolded');
          });
          host.querySelectorAll('.nbmap-merge').forEach(function(e){ e.remove(); });
        }
      }

      // The host is a transparent layer; the PANEL is the rail inside it. Every
      // measurement that used to be taken from the host belongs to the rail.
      function railOf(host){ return host && host.querySelector('.nbrail'); }
      function dockOf(host){ return host && host.querySelector('.nbdock'); }

      // ======================================================================
      // 2026-09-28 (R2 · Paket 17, Teil 1 — Struktur + Applikation)
      // THE TOOLBAR IS GONE; THE WIDGETS STAND FREE IN TWO CORNERS.
      // The dock stays as an invisible layer over the notebook panel (from
      // under JupyterLab's own bar to the panel's bottom edge) so that every
      // rule written for `.nbdock .nbbtn` still finds its buttons, and the
      // re-render in patch() still finds them where it left them. Inside it:
      //   top left, top to bottom:     full screen · light/dark · style
      //   bottom left, bottom to top:  zoom · statistics · profile · settings · keys
      // The order is written HERE and nowhere else. The row the buttons came
      // from is hidden; a re-render puts them back into it, and the next pass
      // moves them out again. The drawer opens beside the lower corner and grows
      // upwards. Look (colour, frame) is the CSS workshop's (R2 · 17 Widget-
      // Stil); what is set here is position and flow, inline and !important,
      // because the old toolbar rules are !important too.
      // Teil 2 (R3): drawers open away from their widget, keyboard.
      var NB_CORNERS = true;
      // 2026-09-29 (E6.6, Struktur) — THE LENS GOES UP, right beside ⛶ in the
      // top corner (last in the list, placed out of the column below); the
      // lower corner closes up without it.
      var NB_CORNER_TL = ['.nbbtn.nbfull', '.nbbtn.nbtheme', '.nbbtn.nbskin', '.nbzoomgrp'];
      // E17.2 (2026-10-02): 📚 is part of the 👤 window now. It keeps its
      // place in the corner (the re-render's shape check counts it, and the
      // stylesheet's contract hides `.nbcorner .nbbtn.nbseries`, css-E17.2)
      // but is never drawn: display:none, set below (rebase 04.10.)
      var NB_CORNER_BL = ['.nbbtn.nbseries', '.nbbtn.nbprofile',
                          '.nbbtn.nbgear', '.nbbtn.nbkeys'];
      function impSet(el, map){
        if (!el) return;
        for (var k in map)
          if (el.style.getPropertyValue(k) !== map[k] ||
              el.style.getPropertyPriority(k) !== 'important')
            el.style.setProperty(k, map[k], 'important');
      }
      function cornerBox(dock, cls){
        var c = dock.querySelector(':scope > .' + cls);
        if (!c) {
          c = document.createElement('div');
          c.className = 'nbcorner ' + cls;
          dock.appendChild(c);
        }
        return c;
      }
      function cornerFill(box, sels, dock){
        var want = [];
        sels.forEach(function(s){ var e = dock.querySelector(s); if (e) want.push(e); });
        for (var i = 0; i < want.length; i++)
          if (box.children[i] !== want[i]) box.insertBefore(want[i], box.children[i] || null);
      }
      function cornerDock(host, dock, left, top, w, bottom){
        var h = Math.max(160, Math.round(bottom - top));
        impSet(dock, {left: Math.round(left) + 'px', top: Math.round(top) + 'px',
                      width: Math.round(w) + 'px', height: h + 'px',
                      padding: '0', margin: '0', display: 'block',
                      background: 'transparent', 'background-image': 'none',
                      border: '0', 'border-radius': '0', 'box-shadow': 'none',
                      'backdrop-filter': 'none', '-webkit-backdrop-filter': 'none',
                      transform: 'none', 'pointer-events': 'none'});
        impSet(dock.querySelector(':scope > .nbctrl'), {display: 'none'});
        var tl = cornerBox(dock, 'nbcorner-tl'), bl = cornerBox(dock, 'nbcorner-bl');
        var col = {position: 'absolute', left: '10px', display: 'flex',
                   'align-items': 'flex-start', gap: '6px', 'pointer-events': 'auto',
                   margin: '0', padding: '0'};
        impSet(tl, col); impSet(tl, {top: '10px', 'flex-direction': 'column'});
        impSet(bl, col); impSet(bl, {bottom: '10px', 'flex-direction': 'column-reverse'});
        cornerFill(tl, NB_CORNER_TL, dock);
        cornerFill(bl, NB_CORNER_BL, dock);
        // E17.2: 📚 is not drawn anywhere (its row is hidden, the button too:
        // its own display said "flex" inside the hidden row — K2.7)
        [].forEach.call(dock.querySelectorAll('.nbbtn.nbseries'), function(e){ impSet(e, {display: 'none'}); });
        // flush against the left edge (the old bar centred every control)
        [].forEach.call(tl.children, function(e){ impSet(e, {'align-self': 'flex-start', margin: '0'}); });
        [].forEach.call(bl.children, function(e){ impSet(e, {'align-self': 'flex-start', margin: '0'}); });
        // the document size stands upright in its corner: slider on its side,
        // the magnifier under it
        // R3 · 17 Teil 2: the chip grows with its slider (the CSS chip is
        // 34 px high, which squashed the group and pushed the slider under
        // the window's edge — R2 finding), and the slider is shorter when the
        // corner is short.
        var hBox = Math.max(160, Math.round(bottom - top));
        // E6.6 — the lens stands in the TOP corner, to the right of full
        // screen, lying down: the magnifier, then its slider (the look before
        // R3; colour and frame are the stylesheet's). Out of the column's
        // flow, so ◐ and 🎨 stay where they were under ⛶.
        var zg = tl.querySelector('.nbzoomgrp');
        if (zg) {
          var fb = tl.querySelector('.nbbtn.nbfull');
          var fw = fb ? (fb.offsetWidth || 34) : 34, fh = fb ? (fb.offsetHeight || 34) : 34;
          impSet(zg, {position: 'absolute', left: (fw + 6) + 'px', top: '0px',
                      display: 'flex', 'flex-direction': 'row-reverse', 'align-items': 'center',
                      gap: '6px', margin: '0', height: fh + 'px', width: 'auto',
                      'min-width': '0', padding: '0 10px', 'box-sizing': 'border-box'});
          impSet(zg.querySelector('.nbslider'), {'writing-mode': 'horizontal-tb',
                      direction: 'ltr', width: '96px', height: '16px', margin: '0'});
          impSet(zg.querySelector('.nbslval'), {position: 'static', margin: '0',
                      transform: 'none', left: 'auto', top: 'auto', 'line-height': '1',
                      width: 'auto', 'min-width': '0', padding: '0'});
        }
        cornerSlim(dock);
        cornerPressed(host, dock);
        // the drawer: beside the lower corner, and FROM ITS WIDGET (Teil 2):
        // its lower edge stands level with the lower edge of the chip that
        // opened it and it grows upwards from there; only if it would run
        // over the top of the corner does it slide down (never below 10 px).
        var dr = dock.querySelector(':scope > .nbdrawer');
        if (dr) {
          var br = bl.getBoundingClientRect();
          var dl = Math.round(br.right - left + 12);
          var open = host.classList.contains('open');
          var opener = open ? cornerOpener(host, dock) : null;
          var bot = 10, maxH = hBox - 20;
          // 2026-09-29 (E6.5) — ONE WINDOW AT A TIME: an open drawer shuts the
          // help window. And the drawer stands in the MIDDLE of the panel's
          // height, beside the corners, not level with the chip that opened it.
          if (open && typeof helpOpen === 'function' && helpOpen()) {
            try { helpWin(false); } catch (e) {}
          }
          // 2026-09-30 (E11.7, Struktur) — BACK AT THE LEFT EDGE, IN THE
          // MIDDLE, AND ONE SIZE. (Replaces E9.10 "middle of the screen".)
          // The window stands right beside the corner signs (their right
          // edge + 12 px), its middle on the middle of the corner column —
          // the notebook panel's height. Its width is fixed (640 px, less on
          // a narrow window) and it no longer scales with the panel: the
          // panel's factor --nbk is pinned to 1 on the window itself
          // (measured v1.39: fonts 15 → 17.7 px with the panel pulled wide).
          var vwD = window.innerWidth;
          var dw = Math.max(300, Math.min(640, vwD - Math.round(br.right) - 24));
          // rebase 04.10. (E17.2) — A SHUT WINDOW IS NOT LAID OUT EITHER. The
          // 👤 page holds five cells now (account, code, settings, progress,
          // start over); shut, they were still laid out under opacity 0, and
          // every answer of the kernel re-laid them (measured lab_inputs A
          // with css-E17.2: 0,46 → 0,52–0,62 s). `content-visibility:hidden`
          // keeps them in the DOM (scripts read and click them) but skips
          // their rendering until the window opens. Set before the height
          // below is read (hidden, its scrollHeight is 0).
          impSet(dr, {'content-visibility': open ? 'visible' : 'hidden'});
          if (open) {
            var dh = Math.min(dr.scrollHeight || 0, maxH);
            bot = Math.round(hBox / 2 - dh / 2);
            bot = Math.max(10, Math.min(bot, hBox - dh - 10));
          }
          dr.style.setProperty('--nbk', '1');
          // E11.7: a close button of its own (the Controls window has one)
          var dx = dr.querySelector(':scope > .nbdrawer-x');
          if (!dx) {
            dx = document.createElement('button');
            dx.type = 'button'; dx.className = 'nbdrawer-x nbhelp-x';
            dx.setAttribute('aria-label', 'close'); dx.title = 'close (Esc)';
            dx.textContent = '\u00d7';
            dr.insertBefore(dx, dr.firstChild);
          }
          impSet(dx, {position: 'sticky', top: '0', float: 'right', 'z-index': '2',
                      display: open ? '' : 'none', cursor: 'pointer'});
          impSet(dr, {position: 'absolute', left: dl + 'px', bottom: bot + 'px',
                      'max-height': maxH + 'px', 'overflow-y': 'auto',
                      width: dw + 'px',
                      'pointer-events': open ? 'auto' : 'none', 'box-sizing': 'border-box',
                      'border-radius': '12px', background: 'var(--nbskin-surf, #ffffff)',
                      'box-shadow': open ? '0 6px 22px rgba(0,0,0,.22)' : 'none',
                      padding: open ? '10px 14px' : '0 14px',
                      border: open ? '1px solid var(--nbskin-line, #d6e2ec)' : '0'});
          // 2026-10-02 (E21.3/E21.10, Applikation) — A SHUT WINDOW TAKES NO
          // CLICK. Shut, the drawer is only transparent (opacity 0) and keeps
          // its box beside the corner, in the middle of the page; its own
          // `pointer-events:none` does not reach the borrowed widgets inside
          // (theirs is `auto`). Measured v1.61: the progress code's field and
          // button and the ⚙ dropdowns took clicks meant for the document
          // (a locked chapter's heading at y 600, the text around it). Shut =
          // inert: no hit, no focus, for everything in it.
          if (dr.inert !== !open) dr.inert = !open;
          if (typeof helpOpen === 'function' && helpOpen() && window.__nbHelpPlace) window.__nbHelpPlace();
          if (opener) dr.setAttribute('data-from', opener.className.replace(/.*\bnb(gear|profile|series|keys)\b.*/, '$1'));
          else dr.removeAttribute('data-from');
        }
      }
      // R3 · 17 Teil 2 — WHICH WIDGET A DRAWER PAGE BELONGS TO. One place.
      var NB_PAGE_OPENER = {diff: '.nbbtn.nbgear', code: '.nbbtn.nbprofile',
                            stats: '.nbbtn.nbprofile', keys: '.nbbtn.nbkeys'};      // E17.2: 📚 is in 👤
      function cornerOpener(host, dock){
        var s = NB_PAGE_OPENER[host.dataset.page || ''];
        return s ? dock.querySelector('.nbcorner ' + s) : null;
      }
      // the chip of an open drawer says so (aria-pressed; the CSS workshop's
      // `.nbcorner > [aria-pressed=true]` rule draws it), and so does ◐
      // (pressed = dark) and ⛶ (pressed = full screen)
      function cornerPressed(host, dock){
        var open = host.classList.contains('open'), op = open ? cornerOpener(host, dock) : null;
        [].forEach.call(dock.querySelectorAll('.nbcorner .nbbtn'), function(b){
          var on = b === op;
          if (b.classList.contains('nbtheme')) on = document.body.classList.contains('nbdark');
          if (b.classList.contains('nbfull')) on = !!document.fullscreenElement;
          var v = on ? 'true' : 'false';
          if (b.getAttribute('aria-pressed') !== v) b.setAttribute('aria-pressed', v);
        });
      }
      window.__nbCornerPressed = function(){
        var h = document.getElementById('nbpanel-root'), d = h && dockOf(h);
        if (d) cornerPressed(h, d);
      };
      // R3 · 17 Teil 2 — ONLY THE SIGN IN THE CORNER (R2 proposal, sketch).
      // 👤 and 📚 were 119 and 204 px wide and stood over the text; now they
      // are one sign each, and what they said is in their tooltip. The spans
      // stay (the panel's re-render and the tests read them); they are only
      // not drawn.
      function cornerSlim(dock){
        var pf = dock.querySelector('.nbcorner .nbbtn.nbprofile');
        if (pf) {
          var pid = pf.querySelector('.nbpid');
          if (pid) {
            impSet(pid, {display: 'none'});
            // E17.2: the account, its settings and the progress
            var deP = window.__nbAcct && window.__nbAcct.lang() === 'de', pt = pid.textContent.trim();
            cornerTip(pf, deP ? 'Konto, Einstellungen und Fortschritt' + (pt.length > 3 ? ' \u2014 ' + pt : ' \u2014 nicht angemeldet')
                              : 'account, settings and progress' + (pt.length > 3 ? ' \u2014 ' + pt : ' \u2014 not logged in'));
          }
        }
        var se = dock.querySelector('.nbcorner .nbbtn.nbseries');
        if (se) {
          var ic = se.querySelector(':scope > .nbcorner-ic');
          if (!ic) {
            ic = document.createElement('span'); ic.className = 'nbcorner-ic';
            ic.textContent = '\uD83D\uDCDA'; ic.setAttribute('aria-hidden', 'true');
            se.insertBefore(ic, se.firstChild);
          }
          var parts = [];
          [].forEach.call(se.querySelectorAll('.nbstat'), function(s){
            impSet(s, {display: 'none'}); parts.push(s.textContent.trim());
          });
          // a stray text node ("📚 —" before the first render) is not drawn either
          [].forEach.call(se.childNodes, function(n){
            if (n.nodeType === 3 && n.textContent.trim()) n.textContent = '';
          });
          cornerTip(se, nbL('this notebook: ', 'dieses Notebook: ') + (parts.length ? parts.join(' · ') : '—')
                        + nbL(' — click for the statistics', '; ein Klick zeigt die Statistik'));
        }
      }
      function cornerTip(el, t){
        // while the bubble shows it, the text lives in data-nbtip (01-jump.js)
        var a = el.hasAttribute('data-nbtip') && !el.hasAttribute('title') ? 'data-nbtip' : 'title';
        if (el.getAttribute(a) !== t) el.setAttribute(a, t);
        if (el.getAttribute('aria-label') !== t) el.setAttribute('aria-label', t);
      }
      // R3 · 17 Teil 2 — THE CORNERS BY KEYBOARD. Every chip is a button, so
      // Tab reaches it; inside a corner ↑/↓ go to the next chip (in the order
      // it stands on the screen), Home/End to the ends. Esc in an open drawer
      // closes it and gives the focus back to the chip that opened it; a
      // drawer opened with the keyboard takes the focus onto its first field.
      if (window.__nbCornerKeysOff) { try { window.__nbCornerKeysOff(); } catch (e) {} }
      function cornerKeys(ev){
        var host = document.getElementById('nbpanel-root');
        if (!host) return;
        var a = document.activeElement;
        var dr = a && a.closest ? a.closest('.nbdrawer') : null;
        if (ev.key === 'Escape' && host.classList.contains('open') &&
            (dr || (a && a.closest && a.closest('.nbcorner')))) {
          var dk = dockOf(host), op = dk ? cornerOpener(host, dk) : null;
          host.classList.remove('open');
          if (op) op.focus();
          ev.preventDefault(); ev.stopPropagation();
          return;
        }
        var c = a && a.closest ? a.closest('.nbcorner') : null;
        if (!c) return;
        var k = ev.key;
        if (k !== 'ArrowUp' && k !== 'ArrowDown' && k !== 'Home' && k !== 'End') return;
        // E10.M-home (Applikation): on a slider all four keys are the slider's
        // own (Home/End = its ends); they took the focus to the first/last chip
        if (a.matches && a.matches('input[type=range]')) return;
        var items = [].slice.call(c.querySelectorAll('.nbbtn, input.nbslider'))
          .filter(function(e){ return e.getBoundingClientRect().height > 0; })
          .sort(function(p, q){ return p.getBoundingClientRect().top - q.getBoundingClientRect().top; });
        var i = items.indexOf(a.closest('.nbbtn, input.nbslider'));
        var j = k === 'Home' ? 0 : k === 'End' ? items.length - 1
              : Math.max(0, Math.min(items.length - 1, i + (k === 'ArrowDown' ? 1 : -1)));
        if (items[j]) { items[j].focus(); ev.preventDefault(); ev.stopPropagation(); }
      }
      function cornerKeyOpen(ev){
        if (ev.detail !== 0) return;                 // a mouse click, not Enter/Space
        var b = ev.target && ev.target.closest ? ev.target.closest('.nbcorner .nbbtn') : null;
        if (!b || !/\bnb(gear|profile|series|keys)\b/.test(b.className)) return;
        setTimeout(function(){
          var host = document.getElementById('nbpanel-root');
          if (!host || !host.classList.contains('open')) return;
          var pg = host.querySelector('.nbdrawer .pg-' + host.dataset.page);
          var f = pg && pg.querySelector('input, select, button, textarea, [tabindex]');
          if (f) f.focus();
        }, 420);
      }
      window.addEventListener('keydown', cornerKeys, true);     // before Lumino's document listener
      document.addEventListener('click', cornerKeyOpen, false);
      window.__nbCornerKeysOff = function(){
        window.removeEventListener('keydown', cornerKeys, true);
        document.removeEventListener('click', cornerKeyOpen, false);
      };

      // The dock sits in the bottom-left corner of the document and does not
      // change size, ever. The page zoom is undone on it so that Ctrl+wheel and
      // the document slider leave it alone as well.
      // The dock is pinned to the WINDOW's bottom-left corner, by CSS alone.
      // Nothing is computed, so nothing can be computed wrong: wherever the
      // document is, however the panel is turned, whatever either zoom is doing,
      // the controls are in the same corner of the screen. The only thing the
      // script does here is undo the page zoom, so they keep one size.
      function placeDock(host, src){
        var dock = dockOf(host);
        if (!dock) return;
        var z = pageZoom();
        // The counter-scale is a TRANSFORM, not `zoom`: a transform does not
        // touch layout, so the centring below stays exact at any page zoom. The
        // origin is the top centre, which is the point being pinned.
        var want = z === 1 ? '' : 'scale(' + (1 / z) + ')';
        if (dock.style.transform !== want) dock.style.transform = want;
        var sc = scroller(host);
        var vw = window.innerWidth, vh = window.innerHeight;
        var left = 10, top = 48, w = Math.max(320, vw - 20);
        // Pinned to the DOCUMENT's own top edge and its whole width — the panel,
        // not the scroller. The scroller starts below the notebook's toolbar,
        // which left a band of empty page above the bar; the panel does not.
        var nbp = (src && src.closest('.jp-NotebookPanel'))
               || (window.__nbFront && window.__nbFront())     // E21.1: in front, not first
               || null;
        var box = nbp || sc;
        if (box) {
          var r = box.getBoundingClientRect();
          left = r.left;
          top  = r.top;                            // flush with the top edge
          w    = Math.max(320, r.width);           // the WHOLE width, edge to edge
        }
        // 2026-09-24z — NOT ON TOP OF JUPYTERLAB'S OWN TOOLBAR.
        // Pinned to the notebook panel's top edge, our bar sat exactly over the
        // front end's: the restart-kernel button, the cell-type box and the
        // kernel indicator were all underneath it and unreachable. We are a
        // second toolbar, so we go under the first one.
        var jtb = nbp && (nbp.querySelector('.jp-Toolbar')
                       || nbp.querySelector('.jp-NotebookPanel-toolbar'));
        if (jtb) {
          var jr = jtb.getBoundingClientRect();
          if (jr.height > 4 && jr.bottom > top) top = jr.bottom;
        }
        // R2 · 17 — no toolbar: two corners (cornerDock), nothing to centre
        if (NB_CORNERS) {
          var bot = box ? Math.min(box.getBoundingClientRect().bottom, vh) : vh;
          cornerDock(host, dock, Math.max(0, left), Math.max(0, top), Math.min(w, vw - left), bot);
          return;
        }
        // clamped into the window: a toolbar you cannot reach is not a toolbar
        left = Math.max(2, Math.min(left, vw - 60));
        top  = Math.max(2, Math.min(top, vh - 40));
        w    = Math.min(w, vw - left - 4);
        // left/top are positions in the zoomed page; the width is a length in
        // the dock's own, counter-scaled pixels — which are screen pixels
        var L = Math.round(left / z) + 'px', T = Math.round(top / z) + 'px',
            W = Math.round(w) + 'px';
        if (dock.style.left !== L) dock.style.left = L;
        if (dock.style.top !== T) dock.style.top = T;
        if (dock.style.width !== W) dock.style.width = W;
        // THE DOCUMENT HOLDS THE AXIS. The reading column is bound to the rail on
        // its right, so its centre is half the reserved strip left of the bar's
        // own centre. The middle group — the progress chip and the statistics —
        // is moved onto it, so that what is on the toolbar stands over what it
        // refers to. The document is rendered before the toolbar exists; the
        // toolbar comes to it, not the other way round.
        // THE MIDDLE OF THE BAR. The strip is taken off both sides of the
        // document, so the reading column's centre IS the bar's centre — one
        // axis for the chip, the statistics and every accordion under them.
        // Measured in .nbctrl's own coordinates, so the dock's padding does not
        // creep into the answer.
        var padL = parseFloat(getComputedStyle(dock).paddingLeft) || 0;
        var padR2 = parseFloat(getComputedStyle(dock).paddingRight) || 0;
        var inner2 = Math.max(80, w - padL - padR2);
        // 2026-09-24n — the reading column is no longer centred in the cell: the
        // strip is taken off the RIGHT only, so the column runs from the left
        // edge to where the rail begins. Its middle is therefore half of what is
        // left, and that is where the chip belongs. Reading the reserve from the
        // custom property keeps the two in step at every panel size.
        // 2026-09-27b — nothing is reserved any more (the panel is an overlay),
        // so the column's middle is the bar's middle at every panel size.
        var ax = Math.round(inner2 / 2);
        // and the offset that puts the PROFILE chip on that axis rather than
        // the middle of the group it sits in
        var cgrp = dock.querySelector('.nbdock-c');
        var chip = cgrp && cgrp.querySelector('.nbprofile');
        if (cgrp && chip) {
          var gr0 = cgrp.getBoundingClientRect(), cr0 = chip.getBoundingClientRect();
          if (gr0.width > 4 && cr0.width > 4) {
            var cdx = Math.round((gr0.left + gr0.width / 2)
                                 - (cr0.left + cr0.width / 2));
            if (cgrp.style.getPropertyValue('--nbdock-cdx') !== cdx + 'px')
              cgrp.style.setProperty('--nbdock-cdx', cdx + 'px');
          }
        }
        var curA = dock.style.getPropertyValue('--nbaxis-x');
        if (curA !== ax + 'px') dock.style.setProperty('--nbaxis-x', ax + 'px');
      }

      function place(host, src){
        var v = vertOn();
        host.classList.toggle('vert', v);
        document.body.classList.toggle('nbvert', v);
        clearOther(host, src, v);
        if (v) { vertPlace(host, src); return; }
        var a = axis(src);
        // getBoundingClientRect reports DEVICE pixels, but a fixed element's own
        // left/top are read in the page's (zoomed) pixels — so the axis has to be
        // divided by the zoom before it is written back.
        var z = pageZoom();
        var rail = railOf(host);
        if (!rail) return;
        var hh = Math.ceil((shutHeight(host) + 16) / z);
        if (hh > 20) document.documentElement.style.setProperty('--nbpanel-h', hh + 'px');
        // Pinned by the LEFT edge, not by the centre. The rail is exactly as
        // wide as the document, so "centre it and pull it back by half its own
        // width" is an arithmetic detour with two chances to drift — and drift
        // it did. Left edge to left edge cannot drift: there is nothing to
        // compute.
        var top = Math.round(a.top / z), lx = Math.round(a.left / z);
        if (rail.style.top  !== top + 'px') rail.style.top  = top + 'px';
        if (rail.style.left !== lx  + 'px') rail.style.left = lx  + 'px';
        if (rail.style.right !== 'auto') rail.style.right = 'auto';
        if (rail.style.bottom !== 'auto') rail.style.bottom = 'auto';
        // ...and the same check the vertical placement makes: full screen moves
        // the host inside the notebook panel, and a fixed layer is then laid
        // out against THAT box. Place it, see where it landed, correct once.
        var got = rail.getBoundingClientRect();
        var dx = Math.round((a.left - got.left) / z);
        var dy = Math.round((a.top  - got.top)  / z);
        if (Math.abs(dx) > 1) rail.style.left = (lx + dx) + 'px';
        if (Math.abs(dy) > 1) rail.style.top  = (top + dy) + 'px';
        placeDock(host, src);
      }

