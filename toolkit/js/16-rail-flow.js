      // 2026-09-27e — A RIGHT ANSWER MOVES THE READER ON (Applikation F, b).
      // The feed says `run:seq:route:key` — which exercise was just solved,
      // on which route. The first time this panel sees a run it only notes the
      // number: a new run, a restore or a reload is not an answer. After that,
      // a higher number is one: the exercise folds and the NEXT OPEN PLACE is
      // clicked — the same click, the same handler, as the reader's own on
      // the rail. Next open place = the next chapter mark after the exercise,
      // if it is open; otherwise the next exercise on the same route that is
      // still open. Nothing open after it: the exercise folds, nothing moves.
      function goNext(host, src){
        var g = (src.getAttribute('data-goto') || '').split(':');
        if (g.length < 4) return;
        var seen = window.__nbGotoSeen || (window.__nbGotoSeen = {});
        var sk = NOWID() + '/' + g[0], seq = parseInt(g[1], 10) || 0;
        // E4.3: a run this panel has not seen yet is a START (Play, Run All,
        // a restore) — the reader begins at the top, on the title mark
        if (!(sk in seen)) { seen[sk] = seq; goTop(host, true); return; }
        if (seq <= seen[sk]) return;
        seen[sk] = seq;
        var route = g[2], key = g.slice(3).join(':');
        if (route === 'top') { clearTimeout(window.__nbGotoT); goTop(host, false); return; }
        clearTimeout(window.__nbGotoT);
        window.__nbGotoT = setTimeout(function(){ goFrom(host, route, key); }, GOTO_MS);
      }
      var GOTO_MS = 1200;       // long enough to see the verdict turn green
      // 2026-09-28 (Eilauftrag E4.3, Applikation + Struktur) — START AT THE TOP.
      // After Play / Run All, and after "Reset this notebook", the reader
      // stands at the very top: document scrolled to 0, the cursor on the
      // title mark (the reading line IS the title's height at the top, and
      // the head air of E4.4 keeps it so at any lens). JupyterLab moves the
      // page by itself while a run renders (it follows the executing cell),
      // so the top is set again for a few seconds — a wheel, a drag, a key
      // or a click in the document ends that at once: the reader has it.
      function goTop(host, start){
        var off = false, fin = false;
        // E5.1: the loading view waits for this before it lifts
        if (start) setTimeout(function(){ window.__nbTopStarted = true; }, 350);
        // any input ends it, on the panel too: a click on a mark is a landing
        var stop = function(ev){
          if (ev.type === 'keydown' &&
              !/^(Arrow|Page|Home|End|Space| )/.test(ev.key || '')) return;
          // E8.6: closing the drawer the reset was pressed in (or any other
          // press on a button of the panel) is not the reader taking the page
          if (!start && ev.type === 'pointerdown' && ev.target && ev.target.closest &&
              ev.target.closest('#nbpanel-root') && !ev.target.closest('.nbmap-node,.nbmap-cursor,.nbmap-here'))
            return;
          off = true;
        };
        var evs = ['wheel', 'touchmove', 'keydown', 'pointerdown'];
        evs.forEach(function(t){
          document.addEventListener(t, stop, {capture: true, passive: true});
        });
        var once = function(){
          if (off || fin) return;
          var h = document.getElementById(HOST_ID) || host;
          if (!h) return;
          var sc = scroller(h);
          if (!sc) return;
          window.__nbGlide = null;
          if (typeof headAir === 'function') headAir(h);
          // E9.2: "the top" is the title on the line, under the air above it
          var t0 = Math.max(0, window.__nbTopAt || 0);
          if (Math.abs(sc.scrollTop - t0) > 1) sc.scrollTop = t0;
          h.removeAttribute('data-manual');
          try { markCentre(h); } catch (e) {}
        };
        var times = start ? [0, 300, 800, 1600, 2800, 4500] : [0, 200, 600, 1200, 2000];
        times.forEach(function(ms, i){
          setTimeout(function(){
            once();
            if (i === times.length - 1) {
              fin = true;
              evs.forEach(function(t){
                document.removeEventListener(t, stop, {capture: true, passive: true});
              });
            }
          }, ms);
        });
      }
      window.__nbGoTop = function(){ goTop(document.getElementById(HOST_ID), false); };
      function nextOpen(host, route, key){
        var sel = route === 'c' ? 'codetask' : 'task';
        var at = route === 'c' ? 'data-cstate' : 'data-state';
        var ns = [].slice.call(host.querySelectorAll('.nbmap-node'));
        var i = -1;
        for (var j = 0; j < ns.length; j++)
          if (ns[j].classList.contains(sel) && ns[j].getAttribute('data-task') === key) { i = j; break; }
        if (i < 0) return {from: null, to: null};
        for (var m = i + 1; m < ns.length; m++) {
          var n = ns[m];
          if (n.classList.contains('chap'))
            return {from: ns[i], to: n.classList.contains('locked') ? null : n};
          if (n.classList.contains(sel) && (n.getAttribute(at) || 'open') === 'open' &&
              !n.querySelector('.st-lock,.cd-lock'))
            return {from: ns[i], to: n};
        }
        return {from: ns[i], to: null};
      }
      window.__nbNextOpen = nextOpen;
      function goFrom(host, route, key){
        host = document.getElementById(HOST_ID) || host;
        var r = nextOpen(host, route, key);
        if (!r.from) return;
        if (window.__nbFoldAfter) window.__nbFoldAfter(r.from.getAttribute('data-target'));
        if (!r.to) return;
        window.__nbGoing = true;
        try { r.to.click(); } finally { window.__nbGoing = false; }
      }
      function setZoom(pct){
        pct = Math.max(ZFLOOR, Math.min(ZCEIL, pct));
        try { localStorage.setItem(zKey(), String(pct)); } catch (e) {}
        var host = document.getElementById(HOST_ID), src = activeSrc();
        moving();                            // E22.9: no hover growth while the lens moves
        applyZoom(host, src);
        if (host) applyGui(host);            // E9.3: the panel scales with the lens
        if (host && src) { place(host, src); reserve(host, src); placeDock(host, src); }
        // E22.9: the marks to their pills in THIS frame, not on the next scroll
        if (host && src && vertOn()) { try { followDoc(host); } catch (e) {} }
      }
      function series(host, src){
        var raw = src.getAttribute('data-progress');
        if (!raw) return;
        var rec; try { rec = JSON.parse(raw); } catch (e) { return; }
        var all = {};
        try { all = JSON.parse(localStorage.getItem(STORE) || '{}'); } catch (e) { all = {}; }
        // Records written by older builds are in this browser too, and they do
        // not all have every field. One malformed record used to throw here and
        // take the whole sync with it — which is a panel that never finishes.
        var _a = rec.a || [0, 0], _c = rec.c || [0, 0];
        var _s = rec.s || [_a[0] || 0, 0, 0];
        // a run from before the difficulty was recorded was a Standard run
        var _g = rec.g || [0, _s[0] || 0, 0];
        // E17.5: no timestamp in the store (concept §4 — the heartbeat `t`
        // was one, every 1.5 s); the kernel's states per content (`p`) stay
        var _old = all[rec.id] || {};
        all[rec.id] = {title: rec.title, a: _a, c: _c, s: _s, g: _g};
        if (_old.p) all[rec.id].p = _old.p;
        try { localStorage.setItem(STORE, JSON.stringify(all)); } catch (e) {}
        try { kpWatch(src, rec); } catch (e) {}                              // E17.5
        var tot = seriesTotals(all);
        var pid = host.querySelector('.nbpid');
        if (pid) {
          // short, stable, and yours: the first characters of this notebook's
          // own id. Enough to tell two people's codes apart at a glance without
          // putting a name on anything.
          var short = String(rec.id || '').replace(/[^a-z0-9]/gi, '').slice(0, 8) || '—';
          // E17.2: logged in, the chip says WHO (the person id), else nobody
          var acc = window.__nbAcct && window.__nbAcct.get();
          short = acc && acc.on ? acc.id : '\u2014';
          if (pid.textContent !== short) pid.textContent = short;
        }
        var el = host.querySelector('.nbseries');
        if (!el) return;
        // 2026-09-28b (K2.7): a reader saw only THIS notebook's numbers here,
        // the series was the administrator's. E38a J3 (Nutzer 14.10.): the
        // role is gone — everyone sees the series and its totals.
        // The badge is the statistics widget: how the exercises ENDED, across
        // every notebook of the series this browser has seen. Three numbers,
        // because there are three ways an exercise can end — answered, skipped,
        // given up. What is still open is the remainder and needs no glyph.
        // 2026-09-24bb — THE CODING ROUTE COUNTS TOO, AND IN ITS OWN COLOUR.
        // Its total has been in the tooltip since the badge existed, which is
        // to say nowhere: a reader following the purple ladder had no number
        // to follow. It gets a chip of its own, and the chip only appears when
        // the notebook actually has coding exercises.
        // 2026-10-02 (E21.5, Applikation) — WRITTEN ONLY WHEN IT CHANGED. Every
        // sync rewrote the badge (innerHTML), the corner put its sign back in,
        // and both are child-list changes the panel's own observer answers with
        // the next sync, 60 ms later — for ever. Measured at rest (v1.61, real
        // Lab, no input for 3 s): 8–13 full syncs, every mark's class rewritten
        // 32 times, 30–46 frames in 3 s — the panel that jitters in video 1.
        var _bh = '<span class="nbstat ok">\u2713 ' + tot.p + '</span>'
                     + '<span class="nbstat skip">\u293c ' + tot.s + '</span>'
                     + '<span class="nbstat fail">\u2717 ' + tot.f + '</span>'
                     + '<span class="nbstat of">/ ' + tot.at + '</span>'
                     + (tot.ct ? '<span class="nbstat code">\u2713 ' + tot.cd
                                 + '/' + tot.ct + '</span>' : '');
        if (el.__nbHtml !== _bh) { el.innerHTML = _bh; el.__nbHtml = _bh; }
        var _bt = nbL(
                   tot.ids.length + ' notebook(s) in this browser\n' + tot.lines.join('\n')
                 + '\n\ntotal: ' + tot.p + ' answered, ' + tot.s + ' skipped, '
                 + tot.f + ' given up, ' + (tot.at - tot.p - tot.s - tot.f)
                 + ' still open, of ' + tot.at
                 + '\ncoding exercises: ' + tot.cd + '/' + tot.ct,
                   tot.ids.length + ' Notebook(s) in diesem Browser\n' + tot.lines.join('\n')
                 + '\n\ninsgesamt: ' + tot.p + ' gelöst, ' + tot.s + ' übersprungen, '
                 + tot.f + ' aufgegeben, ' + (tot.at - tot.p - tot.s - tot.f)
                 + ' noch offen, von ' + tot.at
                 + '\nProgrammieraufgaben: ' + tot.cd + '/' + tot.ct);   // py-E23.1
        if (el.title !== _bt) el.title = _bt;
      }

      // 2026-10-02 (E17.5, Applikation) — THE KERNEL'S STATES, IN THE PROFILE,
      // AND BACK. The account code (12-rail-series-role) carries per notebook
      // the kernel's own record: one character per exercise and route plus
      // the difficulty, exactly what the toolkit's progress_code() signs. The
      // page reads it the way a reader would — the hidden "Show my progress
      // code" of the notebook in front — whenever the panel's numbers change,
      // and keeps it in `progress.v1[<id>].p[<content>]`. After a log-in with
      // a code (pending in `digichemjn.acct.push`) the next run of that
      // notebook gets the MERGE of code and kernel — the further state per
      // exercise, never back — through "Restore from code", signed with the
      // toolkit's checksum (its key ships in every notebook; the comment at
      // _CODE_KEY says what that protects). Nothing else is read or written:
      // no answers, no cell contents, no times.
      var KP = {sig: '', busy: 0, at: 0};
      function kpBox(){
        var h = document.getElementById(HOST_ID), vp = visiblePanel();
        return (h && h.querySelector('.nbctl-code')) || (vp || document).querySelector('.nbctl-code');
      }
      function kpParts(box){
        var o = {inp: box.querySelector('input')};
        [].forEach.call(box.querySelectorAll('button'), function(b){
          if (/Show my progress code|Fortschrittscode zeigen/.test(b.textContent)) o.show = b;
          if (/Restore|wiederherstellen/i.test(b.textContent)) o.load = b;
        });
        o.merge = box.querySelector('.nbctl-merge input, input.nbctl-merge');          // py-E17.5
        return o;
      }
      function kpDecode(code){
        try {
          var s = String(code).replace(/-/g, '+').replace(/_/g, '/');
          var p = decodeURIComponent(escape(atob(s + '==='.slice((s.length + 3) % 4)))).split('|');
          if (p.length < 4) return null;
          return {id: p[0], body: p[1] + '|' + p[2] + '|' + (p.length > 4 ? p[3] : '')};
        } catch (e) { return null; }
      }
      // the toolkit's checksum: HMAC-SHA-256 over "<id>|<states>|<codes>|<diffs>", 8 hex
      function kpSign(id, body){
        var t = id + '|' + body, E = new TextEncoder();
        return crypto.subtle.importKey('raw', E.encode('digichemjn/progress-code/2026-09'),
                                       {name: 'HMAC', hash: 'SHA-256'}, false, ['sign'])
          .then(function(k){ return crypto.subtle.sign('HMAC', k, E.encode(t)); })
          .then(function(sg){
            var h = [].map.call(new Uint8Array(sg).slice(0, 4), function(x){ return ('0' + x.toString(16)).slice(-2); }).join('');
            return btoa(unescape(encodeURIComponent(t + '|' + h))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
          });
      }
      // the answer is a new <pre> — or none, when the kernel's code is the
      // one already shown (an unchanged value is not drawn again)
      function kpWait(box, before, ms){
        return new Promise(function(res){
          var t0 = Date.now();
          (function poll(){
            var pre = box.querySelector('pre'), t = pre ? pre.textContent.trim() : '';
            if (t && t !== before) return res(t);
            if (Date.now() - t0 > ms) return res(t);
            setTimeout(poll, 120);
          })();
        });
      }
      // read the kernel's record of the notebook in front → progress.v1
      function kpCapture(){
        var box = kpBox(), src = activeSrc();
        if (!box || !src || KP.busy) return Promise.resolve(null);
        var P = kpParts(box);
        if (!P.show) return Promise.resolve(null);
        KP.busy = 1;
        var pre = box.querySelector('pre'), before = pre ? pre.textContent.trim() : '';
        P.show.click();
        return kpWait(box, before, before ? 1500 : 4000).then(function(code){
          KP.busy = 0;
          var d = code && kpDecode(code);
          if (!d) return null;
          var md = src.getAttribute('data-nbmode') || 'both', all = {}, pend = {};
          var key = d.id + (md === 'both' ? '' : '.' + md);
          try { all = JSON.parse(localStorage.getItem(STORE) || '{}') || {}; } catch (e) {}
          try { pend = JSON.parse(localStorage.getItem('digichemjn.acct.push') || '{}') || {}; } catch (e) {}
          var r = all[d.id] || {title: d.id};
          r.p = r.p || {};
          // the kernel is this browser's truth — except while a log-in's
          // progress waits to reach it: then the merge (never back)
          var want = pend[key] && window.__nbAcct ? window.__nbAcct.merge(r.p[md], d.body) : d.body;
          if (r.p[md] !== want) { r.p[md] = want; all[d.id] = r;
            try { localStorage.setItem(STORE, JSON.stringify(all)); } catch (e) {} }
          return {id: d.id, mode: md, key: key, body: d.body, want: want, pend: pend};
        }, function(){ KP.busy = 0; return null; });
      }
      // after a log-in: code ∪ kernel into the kernel, once per notebook and content
      function kpPush(n){
        if (!window.crypto || !crypto.subtle) return Promise.resolve(false);
        if (KP.busy) {                       // a read is under way: after it
          return (n || 0) > 12 ? Promise.resolve(false) : new Promise(function(res){
            setTimeout(function(){ res(kpPush((n || 0) + 1)); }, 700); });
        }
        return kpCapture().then(function(k){
          if (!k || !k.pend[k.key]) return false;
          var pend = k.pend, key = k.key, want = k.want;
          var done = function(){ delete pend[key]; try { localStorage.setItem('digichemjn.acct.push', JSON.stringify(pend)); } catch (e) {} };
          if (!want || want === k.body) { done(); return false; }
          var box = kpBox(), P = kpParts(box);
          if (!P.merge && (!P.inp || !P.load)) return false;
          return kpSign(k.id, want).then(function(code){
            // py-E17.5's merge field when the build has it (the kernel
            // merges again, never lowers), else "Restore from code"
            var t = P.merge || P.inp;
            t.value = code;
            t.dispatchEvent(new Event('input', {bubbles: true}));
            t.dispatchEvent(new Event('change', {bubbles: true}));
            if (!P.merge) setTimeout(function(){ P.load.click(); }, 150);
            done();
            setTimeout(kpCapture, 2500);
            return true;
          });
        });
      }
      window.__nbKernelProgress = kpCapture;
      window.__nbKernelPush = kpPush;
      // the panel's numbers changed (or a log-in waits): read again, idle kernel only
      function kpWatch(src, rec){
        var raw = src.getAttribute('data-progress') + '|' + (src.getAttribute('data-nbmode') || '');
        var pend = '';
        try { pend = localStorage.getItem('digichemjn.acct.push') || ''; } catch (e) {}
        // rebase 04.10.: only for an account that is on, or a log-in that
        // waits — without one nobody needs the kernel's record in the store
        // (the code is made on demand, `code`/`create` read it first), and
        // the read is a kernel call: measured lab_inputs A, the first read
        // after a run delayed the slider's answer 0,45 → 0,55–0,61 s
        var waits = pend.length > 2 && pend.indexOf('"' + rec.id) > -1;
        if (!waits && !(window.__nbAcct && window.__nbAcct.on())) return;
        var need = raw !== KP.sig || (waits && Date.now() - KP.at > 8000);
        if (!need || KP.busy || (window.__nbKpHold || 0) > Date.now()) return;
        var vp = visiblePanel();
        var st = ((vp || document).querySelector('.jp-Notebook-ExecutionIndicator') || {getAttribute: function(){ return 'idle'; }})
                 .getAttribute('data-status');
        if (st && st !== 'idle') return;
        KP.sig = raw; KP.at = Date.now();
        clearTimeout(KP.t);
        KP.t = setTimeout(function(){ (pend.indexOf('"' + rec.id) > -1 ? kpPush() : kpCapture()); }, 900);
      }

      // One place that adds the series up, used by the badge and by the drawer.
      // A record written by an older notebook has no 's' field; its answered
      // count stands in for "passed" and the other two are zero.
      function seriesTotals(all){
        var t = {p: 0, s: 0, f: 0, ad: 0, at: 0, cd: 0, ct: 0, lines: [],
                 g: [0, 0, 0],            // passes at gentle / standard / strict
                 rows: [], ids: Object.keys(all).sort()};
        t.ids.forEach(function(k){
          var r = all[k] || {};
          var ra = r.a || [0, 0], rc = r.c || [0, 0];
          var st = r.s || [ra[0] || 0, 0, 0];
          var rg = r.g || [0, st[0] || 0, 0];
          var num = function(v){ return typeof v === 'number' && isFinite(v) ? v : 0; };
          t.g[0] += num(rg[0]); t.g[1] += num(rg[1]); t.g[2] += num(rg[2]);
          t.p += num(st[0]); t.s += num(st[1]); t.f += num(st[2]);
          t.ad += num(ra[0]); t.at += num(ra[1]);
          t.cd += num(rc[0]); t.ct += num(rc[1]);
          t.rows.push({id: k, title: r.title || k, st: st, a: ra, c: rc, g: rg});
          t.lines.push((r.title || k) + ': \u2713' + num(st[0]) + ' \u293c' + num(st[1])
                       + ' \u2717' + num(st[2]) + ' of ' + num(ra[1]));
        });
        return t;
      }

      // How tall the panel is WITHOUT its settings drawer. Measured from the
      // timeline row rather than by subtracting the drawer, because the drawer
      // animates: right after a click its box is still the old one, and a strip
      // computed from it jumps. The row never changes, so this never jumps.
      function shutHeight(host){
        var rail = railOf(host);
        var row = host.querySelector('.nbrail-row');
        if (!row || !rail) return rail ? rail.getBoundingClientRect().height : 0;
        return Math.max(0, row.getBoundingClientRect().bottom -
                           rail.getBoundingClientRect().top) + 11;
      }

      // the panel floats above the document, so push the document down by exactly
      // its height — otherwise the first lines sit underneath it for good
      function reserve(host, src){
        if (vertOn()) { vertReserve(host, src); return; }
        var nb = src.closest('.jp-Notebook') || src.closest('.jp-NotebookPanel');
        if (!nb) return;
        // Measured in device pixels, written in page pixels — and quantised to 4px
        // steps. Without that, a one-pixel change in the panel's height changes the
        // padding, which reflows the notebook, which re-measures the panel: the
        // shimmy you see while the browser zoom is moving.
        var h = Math.ceil((shutHeight(host) + 14) / pageZoom() / 4) * 4;
        var cur = parseInt(nb.dataset.nbpad || '0', 10);
        if (Math.abs(cur - h) > 3) {
          nb.style.paddingTop = h + 'px';
          nb.dataset.nbpad = String(h);
        }
      }


      // ======================================================================
      // 2026-09-28 (R3 · Paket 20, Oberfläche + Applikation) — TYPED CODE IN
      // THE STYLE'S COLOURS. A code fold's answer field is a plain <textarea>:
      // it cannot colour a token. Over it lies a <pre class="nbedov-hl"> with
      // the same text, tokenised here the way highlight_code() does it in the
      // kernel (keyword · string · comment · number · def · builtin · operator,
      // `color:var(--jp-mirror-editor-…)`), re-drawn on every keystroke and
      // scrolled with the field. CSS 20 contract: `.codearea.nbedov` on the
      // widget, `.nbedov-hl` before the textarea, `.on` = live (the field's own
      // glyphs go transparent, the caret stays). The overlay switches itself on
      // ONLY where that stylesheet is present (the <pre> reads position
      // absolute); without it the field stays the plain field — never two
      // copies of the code on screen.
      var EDOV_KW = {}, EDOV_BLT = {};
      ('False None True and as assert async await break class continue def del elif else except '
       + 'finally for from global if import in is lambda nonlocal not or pass raise return try '
       + 'while with yield').split(' ').forEach(function(w){ EDOV_KW[w] = 1; });
      ('abs all any bin bool bytes callable chr complex dict dir divmod enumerate filter float '
       + 'format frozenset getattr hasattr hash hex id input int isinstance issubclass iter len '
       + 'list map max min next object oct open ord pow print range repr reversed round set '
       + 'setattr slice sorted str sum super tuple type vars zip').split(' ').forEach(function(w){ EDOV_BLT[w] = 1; });
      var EDOV_COL = {
        kw: 'var(--jp-mirror-editor-keyword-color,#008000)',
        str: 'var(--jp-mirror-editor-string-color,#b5482e)',
        com: 'var(--jp-mirror-editor-comment-color,#5c6370)',
        num: 'var(--jp-mirror-editor-number-color,#2aa198)',
        def: 'var(--jp-mirror-editor-def-color,#1750eb)',
        blt: 'var(--jp-mirror-editor-builtin-color,#308080)',
        op: 'var(--jp-mirror-editor-operator-color,#a626a4)'};
      var EDOV_RE = new RegExp([
        '(#[^\\n]*)',                                                      // 1 comment
        '((?:[rRbBuUfF]{0,2})(?:\'\'\'[\\s\\S]*?(?:\'\'\'|$)|"{3}[\\s\\S]*?(?:"{3}|$)|'
          + '\'(?:\\\\.|[^\'\\\\\\n])*\'?|"(?:\\\\.|[^"\\\\\\n])*"?))',  // 2 string
        '(\\b\\d[\\d_]*\\.?\\d*(?:[eE][+-]?\\d+)?[jJ]?\\b|\\.\\d+\\b)',      // 3 number
        '([A-Za-z_]\\w*)',                                                  // 4 name
        '([+\\-*/%=<>!&|^~@:.,;()\\[\\]{}])'                                 // 5 operator
      ].join('|'), 'g');
      function edovEsc(t){ return t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
      function edovHtml(code){
        var out = '', last = 0, prev = '', m;
        EDOV_RE.lastIndex = 0;
        while ((m = EDOV_RE.exec(code))) {
          if (m[0] === '') { EDOV_RE.lastIndex++; continue; }
          out += edovEsc(code.slice(last, m.index));
          var cls = m[1] ? 'com' : m[2] ? 'str' : m[3] ? 'num' : m[5] ? 'op'
                  : m[4] ? (EDOV_KW[m[4]] ? 'kw' : (prev === 'def' || prev === 'class') ? 'def'
                             : EDOV_BLT[m[4]] ? 'blt' : null) : null;
          out += cls ? '<span style="color:' + EDOV_COL[cls] + '">' + edovEsc(m[0]) + '</span>'
                     : edovEsc(m[0]);
          if (m[4] || m[5]) prev = m[0];
          last = EDOV_RE.lastIndex;
        }
        // a trailing newline needs a glyph after it, or the <pre> is one line short
        return out + edovEsc(code.slice(last)) + '​';
      }
      function edovPaint(ta){
        var box = ta.__nbEdov;
        if (!box) return;
        box.innerHTML = edovHtml(ta.value || '');
        box.scrollTop = ta.scrollTop; box.scrollLeft = ta.scrollLeft;
      }
      // 2026-09-29 (E8.4, Oberfläche + Applikation) — THE CODE IS ALWAYS SEEN.
      // Video V2: the code in a coding field vanished once the field lost
      // focus. Measured in the real JupyterLab: in cyber, retro and fairy the
      // skin paints the <textarea> itself (rgb(242,238,255) in cyber light),
      // and the textarea lies ABOVE the coloured <pre> (z 1 over z 0) while
      // its own glyphs are transparent — an empty box, in six of eight
      // style × brightness pairs. minimal leaves the field transparent, so it
      // never showed there. The <pre> now lies on top, and lets every pointer
      // through to the field under it: whatever a skin paints on the field is
      // background, the code is in front, the caret and the selection stay
      // the field's. And every scan checks it: an overlay that is not on
      // screen switches off, so the field's own glyphs come back.
      // 2026-10-06 (E23.12, Oberfläche + Applikation) — THE CODE STAYS
      // COLOURED WHEN THE FIELD IS LEFT. Since E8.4 the stylesheet hid the
      // coloured <pre> out of focus and gave the field its own glyphs in the
      // code ink — the safe way while the <pre> could lie under a painted
      // field. It cannot any more (edovLift: on top, z 2, no pointer), and the
      // reader saw the price: click outside and the code turned grey (video 8,
      // 06.10.). Now, while the overlay is live (`.on`), the <pre> is shown and
      // the field's glyphs stay transparent in and out of focus — inline, so
      // it outranks the E8.4 rules (the caret and the selection are still the
      // field's). The guard of E8.4 stays in edovSeen: an overlay that is not
      // drawn (no box, display none, opacity 0) switches off, edovOff gives
      // the field its own glyphs back — plain code, never none.
      function edovLift(pre){
        pre.style.setProperty('z-index', '2', 'important');
        pre.style.setProperty('pointer-events', 'none', 'important');
        pre.style.setProperty('visibility', 'visible', 'important');        // E23.12
        pre.style.setProperty('display', 'block', 'important');
        var ta = pre.nextElementSibling;
        if (ta && ta.tagName === 'TEXTAREA') {
          ta.style.setProperty('color', 'transparent', 'important');
          ta.style.setProperty('-webkit-text-fill-color', 'transparent', 'important');
        }
      }
      function edovOff(wrap, pre, ta){
        wrap.classList.remove('on');
        pre.style.removeProperty('visibility');
        pre.style.setProperty('display', 'none');
        ta.style.removeProperty('color');
        ta.style.removeProperty('-webkit-text-fill-color');
      }
      function edovSeen(ta){
        var pre = ta.__nbEdov, wrap = ta.closest('.codearea');
        if (!pre || !wrap || !wrap.classList.contains('on')) return;
        var cp = getComputedStyle(pre);
        // E19.3: out of focus the stylesheet hides the <pre> ON PURPOSE (E8.4:
        // the field shows its own ink then). Read as "broken", that switched
        // the overlay off for good at the first scan after the field was
        // left — the code never coloured again while typing.
        // E23.12: the <pre> is visible in and out of focus now (edovLift)
        if (cp.display === 'none' || cp.visibility === 'hidden' || +cp.opacity === 0 ||
            pre.getBoundingClientRect().height < 2 && ta.getBoundingClientRect().height > 2) {
          edovOff(wrap, pre, ta);
        }
      }
      function edovAttach(ta){
        var wrap = ta.closest('.codearea');
        if (!wrap || ta.__nbEdov) return;
        var pre = document.createElement('pre');
        pre.className = 'nbedov-hl'; pre.setAttribute('aria-hidden', 'true');
        wrap.classList.add('nbedov');
        ta.parentNode.insertBefore(pre, ta);
        ta.__nbEdov = pre;
        // only with the stylesheet's contract on the page (CSS 20)
        if (getComputedStyle(pre).position !== 'absolute') {
          pre.style.display = 'none';
          return;
        }
        wrap.classList.add('on');
        edovLift(pre);
        edovPaint(ta);
        ta.addEventListener('input', function(){ edovPaint(ta); });
        ta.addEventListener('scroll', function(){ pre.scrollTop = ta.scrollTop; pre.scrollLeft = ta.scrollLeft; });
      }
      function edovScan(){
        [].forEach.call(document.querySelectorAll('.jp-OutputArea .codearea textarea'), function(ta){
          if (!ta.__nbEdov) edovAttach(ta);
          else edovSeen(ta);
          if (!ta.__nbEdov) return;
          if (ta.__nbEdov.innerHTML.length && ta.__nbEdov.__v !== ta.value) { ta.__nbEdov.__v = ta.value; edovPaint(ta); }
        });
      }
      window.__nbEdovHtml = edovHtml;
      if (window.__nbEdovTick) clearInterval(window.__nbEdovTick);
      window.__nbEdovTick = setInterval(edovScan, 1500);
      // E23.12: coloured as soon as the fields are there (a load, a rebuild),
      // not only at the first tick
      [0, 300, 900].forEach(function(ms){ setTimeout(function(){ try { edovScan(); } catch (e) {} }, ms); });
