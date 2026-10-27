    (function nbRailMain(){
      // 2026-10-11 (E26.1, by the Python workshop, STOP.md) — INTERACTIVE ONLY
      // WHERE OUR WIDGETS ARE DRAWN IN THIS PAGE. The cell's first output is
      // the reading version (`.nbreading`, py-E26.1); the title card and the cover
      // come wrapped in `.nbwarm` (hidden inline). PyCharm and VS Code draw
      // every output in a page of its own: there this script sees no widget
      // and draws nothing — no panel, no tool buttons. Where the document's
      // widgets are drawn next to the reading version (JupyterLab, Lite) its
      // output area gets `nb-live` (the stylesheet hides `.nbreading` at once),
      // the reading copy is taken out of the page and the wrappers go, so the
      // page is the one of v1.69. Nothing reaches across
      // outputs: what is marked is always the output area that holds both.
      if (!window.__nbLiveObs) {
        var nbLiveF = 0;
        var nbLiveMark = function(){
          nbLiveF = 0;
          // E31 W1 (JS, PyCharm v1.77 video 1: a second run, the cover for a moment, then [4] empty): a host
          // that draws the cell's widget outputs into the SAME page as the reading version without being a
          // notebook front end (PyCharm, Colab) is no live document — taking the reading copy out left
          // nothing. Only on a real notebook page (JupyterLab, Notebook 7, classic) the live document takes
          // over (behauptete bisher: any .acc-root in the same output area)
          if (!document.querySelector('.jp-NotebookPanel, .jp-Notebook, #notebook')) return;
          var rs = document.querySelectorAll('.nbreading, .nbwarm');
          for (var i = 0; i < rs.length; i++) {
            var a = rs[i].closest ? rs[i].closest('.jp-OutputArea, .output') : null;
            if (!a || !a.querySelector('.acc-root')) continue;
            if (!a.classList.contains('nb-live')) a.classList.add('nb-live');
            var w = rs[i];
            if (!w.parentNode) continue;
            if (w.classList.contains('nbwarm')) {
              while (w.firstChild) w.parentNode.insertBefore(w.firstChild, w);
              w.parentNode.removeChild(w);
            } else {
              // the reading copy leaves the page (not only hidden): no query of
              // the document, the panel or a test may meet its text first
              var ch = w.closest('.jp-OutputArea-child');
              w.parentNode.removeChild(w);
              if (ch) ch.style.display = 'none';
            }
          }
          // E26.1b: the held widget outputs (py: layout height 0, overflow and
          // visibility hidden, class nbhold) get their own styles back in a live
          // output area — also after a re-render, which writes them again
          var hs = document.querySelectorAll('.nb-live .nbhold');
          for (var k = 0; k < hs.length; k++) {
            var hst = hs[k].style;
            if (hst.height === '0px') hst.removeProperty('height');
            if (hst.overflow === 'hidden') hst.removeProperty('overflow');
            if (hst.visibility === 'hidden') hst.removeProperty('visibility');
          }
        };
        window.__nbLiveMark = nbLiveMark;
        window.__nbLiveObs = new MutationObserver(function(){
          if (!nbLiveF) nbLiveF = (window.requestAnimationFrame || setTimeout)(nbLiveMark);
        });
        window.__nbLiveObs.observe(document.documentElement, {childList: true, subtree: true});
        nbLiveMark();
      }
      // the wrappers go BEFORE the panel looks for the title card and the cover
      if (window.__nbLiveMark) window.__nbLiveMark();
      // E26.1b — the reading version's pip advice (`.nbread-pip`, hidden inline)
      // is shown only here: this script runs next to the reading version only
      // where the notebook is ONE page (JupyterLab, Notebook 7, Lite: their
      // shell is in the page), and only when no widget of ours is drawn by then.
      // PyCharm / VS Code (a page per output) and a static HTML copy never show it.
      if (!window.__nbPipT) {
        window.__nbPipT = setTimeout(function(){
          if (document.querySelector('.acc-root')) return;
          if (!document.querySelector('.jp-LabShell, .jp-NotebookShell, #main-panel, .lm-DockPanel, .p-DockPanel')) return;
          var ps = document.querySelectorAll('.nbreading .nbread-pip');
          for (var i = 0; i < ps.length; i++) ps[i].style.display = 'inline';
        }, 6000);
      }
      // E31 W1: the live document and its panel only on a real notebook page — elsewhere (PyCharm, Colab: the
      // widgets drawn into the reading version's page) the reading window stays the notebook (STOP COLAB note:
      // Schicht B vorerst = C)
      if (!document.querySelector('.jp-NotebookPanel, .jp-Notebook, #notebook')) return;
      if (!document.querySelector('.acc-root')) {
        if (!window.__nbRailWait) {
          window.__nbRailWait = new MutationObserver(function(){
            if (!document.querySelector('.acc-root')) return;
            window.__nbRailWait.disconnect(); window.__nbRailWait = null; nbRailMain();
          });
          window.__nbRailWait.observe(document.documentElement, {childList: true, subtree: true});
        }
        return;
      }
      var HOST_ID = 'nbpanel-root';          // exactly ONE host, ever
      // 2026-09-25h — FROM THE TOOLKIT, NOT TYPED. It stood at "2026-09-25a"
      // through 25g, so a 25g notebook opened after a 25a one in the same
      // window read "a newer or equal panel is running" and only fed the old
      // one — measured, see APPLIKATION.md §2. One source: TOOLKIT_VERSION.
      var NBRAIL_VERSION = "__NBRAILV__";
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

      // 2026-10-02 (E19.4, Applikation) — ONE FILE FOR EVERY FRONT END: WHERE
      // ARE WE? Read once from what the page itself says — JupyterLab and
      // Notebook 7 name themselves in `#jupyter-config-data` (appName),
      // JupyterLite marks that script `data-jupyter-lite-root`, a JupyterHub
      // (and so Binder) adds `hubPrefix`/`hubUser`, Binder runs on a binder
      // host or under /binder/; Colab draws every output in a frame on
      // *.googleusercontent.com with `google.colab`, VS Code in a webview
      // (`vscode-webview:`, `acquireVsCodeApi`, body `vscode-*`), PyCharm /
      // DataSpell in JetBrains' browser (user agent — NOT measured here, no
      // such program in this container). The answer goes on <html>:
      //   data-nbenv = lab | nb7 | lite | binder | hub | colab | vscode | pycharm | page
      //   data-nbui  = lab   (a Jupyter app around us: panel docked as in Lab)
      //              | frame (our output sits in a frame of a foreign app: no
      //                       access to its menus or its other cells)
      //              | page  (a static page, no kernel)
      // for the stylesheet's fall-back look, and `window.__nbEnv()` for the
      // script (the menu path a message names, E19.4). `probe` = a test's
      // stand-in for the page.
      function nbEnv(probe){
        // rebase 03.10.: the kernel says where it runs (py-E19.4,
        // `.nbfeed[data-nbenv]`) — it sees what the page cannot (google.colab,
        // the variables VS Code and PyCharm set); for those three and Lite
        // its word wins. Read again on every call, cached per answer.
        var kf = probe ? null : document.querySelector('.nbfeed[data-nbenv]'),
            ke = probe ? (probe.kernel || '') : (kf ? kf.getAttribute('data-nbenv') || '' : '');
        if (!probe && window.__nbEnvV && window.__nbEnvV.k === ke) return window.__nbEnvV;
        var q = probe || {}, cfg = q.cfg, el = null;
        if (!cfg) {
          el = document.getElementById('jupyter-config-data'); cfg = {};
          try { if (el) cfg = JSON.parse(el.textContent || '{}') || {}; } catch (e) {}
        }
        var H = q.host !== undefined ? q.host : location.hostname || '',
            Pa = q.path !== undefined ? q.path : location.pathname || '',
            Pr = q.proto !== undefined ? q.proto : location.protocol || '',
            ua = q.ua !== undefined ? q.ua : navigator.userAgent || '',
            bc = q.body !== undefined ? q.body : (document.body ? document.body.className : ''),
            app = String(cfg.appName || ''),
            lite = q.lite !== undefined ? q.lite : !!(el && el.hasAttribute('data-jupyter-lite-root'));
        var env = Pr === 'vscode-webview:' || (!probe && typeof window.acquireVsCodeApi === 'function')
                  || /\bvscode-(light|dark|high-contrast)\b/.test(bc) ? 'vscode'
                : /(^|\.)googleusercontent\.com$/.test(H) || (!probe && window.google && window.google.colab) || q.colab ? 'colab'
                : /JetBrains|PyCharm|DataSpell|IntelliJ/i.test(ua) ? 'pycharm'
                : lite || /JupyterLite/i.test(app) ? 'lite'
                : /(^|\.)mybinder\.org$|binder/i.test(H) || /^\/binder\//.test(Pa) ? 'binder'
                : cfg.hubPrefix || cfg.hubUser ? 'hub'
                : /Jupyter Notebook/i.test(app) ? 'nb7'
                : /JupyterLab/i.test(app) || (!probe && document.querySelector('.jp-NotebookPanel')) ? 'lab'
                : 'page';
        if (/^(colab|vscode|pycharm|lite)$/.test(ke)) env = ke;
        var ui = /^(colab|vscode|pycharm)$/.test(env) ? 'frame' : env === 'page' ? 'page' : 'lab';
        var v = {env: env, ui: ui, k: ke};
        if (probe) return v;
        window.__nbEnvV = v;
        var R = document.documentElement;
        if (R.getAttribute('data-nbenv') !== env) R.setAttribute('data-nbenv', env);
        if (R.getAttribute('data-nbui') !== ui) R.setAttribute('data-nbui', ui);
        return v;
      }
      window.__nbEnv = nbEnv;
      // E25.n's ring of the page's last errors is gone (E29 P5, 12.10.: no
      // report is sent from the page any more — only a line of text, Python's).
      try { nbEnv(); } catch (e) {}
      // where "run everything" lives in each of them, for the messages that name it
      function nbRunPath(de){
        var e = nbEnv().env;
        if (e === 'colab') return de ? 'Laufzeit \u25b8 Sitzung neu starten und alle ausführen' : 'Runtime \u25b8 Restart session and run all';
        if (e === 'vscode') return de ? '\u201eNeu starten\u201c, dann \u201eAlle ausführen\u201c in der Leiste über dem Notebook'
                                     : '\u201cRestart\u201d, then \u201cRun All\u201d in the bar above the notebook';
        if (e === 'pycharm') return de ? 'Kernel neu starten, dann \u201eRun All\u201c (\u25b6\u25b6) über dem Notebook'
                                      : 'restart the kernel, then \u201cRun All\u201d (\u25b6\u25b6) above the notebook';
        return de ? 'Run \u25b8 Restart Kernel and Run All Cells' : 'Run \u25b8 Restart Kernel and Run All Cells';
      }
      window.__nbRunPath = nbRunPath;

      function shown(p){
        if (p.classList.contains('lm-mod-hidden') || p.classList.contains('p-mod-hidden'))
          return false;
        return p.getBoundingClientRect().width > 0;
      }
      // With several notebooks open, JupyterLab marks the one in front
      // .jp-mod-current; in a split view both are shown, and that mark is the only
      // thing that says which one the reader is actually in.
      function visiblePanel(){
        // E22.1/E22.9: one look per pass (memo, below) — each look reads a box,
        // and between our own writes in a pass that is a layout each time
        // (profile v1.63 + E22.9, two notebooks: 42 %% of a full pass)
        return window.__nbMemo ? memo('vp', visiblePanel0) : visiblePanel0();
      }
      function visiblePanel0(){
        var ps = document.getElementsByClassName('jp-NotebookPanel');     // E22.1b (byCls)
        for (var i = 0; i < ps.length; i++)
          if (ps[i].classList.contains('jp-mod-current') && shown(ps[i])) return ps[i];
        for (var j = 0; j < ps.length; j++)
          if (shown(ps[j])) return ps[j];
        return null;
      }

      // a stable handle for "which notebook is this", so a switch can be detected
      var SEQ = 0;
      function panelKey(p){
        if (!p) return '';
        if (!p.dataset.nbkey) p.dataset.nbkey = p.id || ('nb' + (++SEQ));
        return p.dataset.nbkey;
      }

      // The panel floats over the page, so in browser full screen it is only painted
      // when it lives INSIDE the element that went full screen — everything outside
      // that element is not rendered at all. That is why it vanished on ⛶.
      function mountHost(host){
        var fs = document.fullscreenElement || document.webkitFullscreenElement || null;
        host.classList.toggle('fs', !!fs);
        document.body.classList.toggle('nbfs', !!fs);
        var target = (fs && fs !== document.documentElement && fs !== document.body)
                   ? fs : document.body;
        if (host.parentNode !== target) target.appendChild(host);
      }

      // Find the progress source of the notebook that is on screen. The old version
      // additionally required the source node itself to have a non-zero box, which
      // made the whole panel disappear as soon as the only remaining notebook did
      // not satisfy that (with several tabs open, another tab's node had been
      // keeping it alive). Visibility is now decided by the NOTEBOOK PANEL, and a
      // source anywhere inside it counts — including the mirrors further down.
      // While the notebook is still rendering, the mirrors carry a PARTIAL
      // structure — the timeline would grow chapter by chapter in front of the
      // reader. So until the final panel (emitted after the last chapter) has been
      // seen once, only that one counts; afterwards any mirror may stand in, which
      // is what keeps the panel alive when a cell re-renders.
      function srcIn(root){
        var all = [].slice.call(root.getElementsByClassName('nbfeed')), i;   // E22.1b (byCls)
        for (i = 0; i < all.length; i++)
          if (all[i].isConnected && all[i].hasAttribute('data-final') &&
              all[i].querySelector('.nbrail')) {
            window.__nbrailFinal = true;
            return all[i];
          }
        if (!window.__nbrailFinal) return null;
        for (i = 0; i < all.length; i++)
          if (all[i].isConnected && all[i].querySelector('.nbrail')) return all[i];
        return null;
      }
      // Strictly the notebook on screen. Borrowing a source from another tab (the
      // old last-resort loop) meant notebook A's progress stayed on screen while
      // you were reading notebook B. The document-wide search is kept only for
      // interfaces that have no .jp-NotebookPanel at all (Notebook 7 / retro),
      // where there is exactly one notebook per page anyway.
      // 2026-10-05 (E22.9/E22.1, Applikation) — ONE LOOK PER FOLLOW. A follow
      // of the page (followDoc: vertLayout, headAir, footAir, markCentre …)
      // asks for the source and the notebook id a dozen times; each ask
      // searched the whole notebook (`.nbfeed`, 12 600 nodes) and parsed its
      // progress record again. Since the rail follows the page in every frame
      // (E22.6) that was the frame: profile v1.63 + E22.9, Modeling, two own
      // cells, one CPU: 50–85-ms frames, most of it in srcIn/nbId. Inside one
      // follow nothing of that changes, so the answers are kept for it
      // (`__nbMemo`, set and cleared by followDoc) — nowhere else.
      function memo(k, f){
        var m = window.__nbMemo;
        if (!m) return f();
        if (!(k in m)) m[k] = f();
        return m[k];
      }
      function activeSrc(){
        return memo('src', activeSrc0);
      }
      // 2026-10-05 (E22.1b, Applikation) — A LOOK BY CLASS IS A LOOK UP, NOT A
      // WALK. `querySelector('.x')` walks the page (JupyterLab with two of our
      // notebooks: some 25 000 elements) every time it is asked; a pass asked
      // some forty times. Profile of the gate rows that stayed red (J22.1,
      // v1.64 probe, 1 CPU): two thirds of a full pass (33 ms median, 60–84 ms
      // in a warm row) were these walks — sweep, helpOpen, dcMark,
      // visiblePanel, targetEl, the cover passes. getElementsByClassName
      // answers the same (the first / every element of that class, in page
      // order) from a list the browser keeps and only rebuilds after the page
      // changed: the second ask in a pass and every ask at rest costs nothing.
      // byCls = root.querySelector('.' + c); allCls = a static copy of
      // root.querySelectorAll('.' + c).
      function byCls(root, c){ return (root || document).getElementsByClassName(c)[0] || null; }
      function allCls(root, c){ return [].slice.call((root || document).getElementsByClassName(c)); }
      function activeSrc0(){
        var vp = visiblePanel();
        if (vp) return srcIn(vp);
        if (byCls(document, 'jp-NotebookPanel')) return null;
        return srcIn(document);
      }

      // The panel and the notebook body must share ONE vertical axis, whatever the
      // window does — sidebar open, browser zoom, full screen. The axis is the
      // centre of the notebook's own scroll viewport (clientWidth, so the
      // scrollbar does not pull it sideways); the content column is centred in
      // exactly that box by the stylesheet, so both land on the same line.
      function axis(src){
        var panel = src.closest('.jp-NotebookPanel') || src.closest('.jp-Notebook');
        var view = panel && (panel.querySelector('.jp-WindowedPanel-outer') ||
                             panel.querySelector('.jp-Notebook') || panel);
        if (!view) return {cx: Math.round(window.innerWidth / 2), left: 0, top: 8};
        var r = view.getBoundingClientRect();
        var w = view.clientWidth || r.width;
        var bar = panel && (panel.querySelector('.jp-Toolbar') ||
                            panel.querySelector('.jp-NotebookPanel-toolbar'));
        var top = 8;
        if (bar) {
          var b = bar.getBoundingClientRect();
          if (b.height > 0) top = Math.round(b.bottom + 8);
        }
        // the panel is as wide as the notebook it belongs to
        var rw = Math.max(380, Math.round(w - 20)) + 'px';
        if (document.documentElement.style.getPropertyValue('--nbrail-w') !== rw)
          document.documentElement.style.setProperty('--nbrail-w', rw);
        // the rail is `w - 20` wide, so a 10px gutter on each side of the
        // document's own content box puts it exactly over the text column
        return {cx: Math.round(r.left + w / 2), left: Math.round(r.left) + 10,
                top: top};
      }

