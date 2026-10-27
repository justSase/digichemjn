      // ---- ▶ run all cells ---------------------------------------------
      // A markdown cell is sanitised before it is rendered: `id` is rewritten,
      // `script`, `style`, `onclick` and every data- attribute are stripped.
      // `class` survives — so the title page can carry the button's SHAPE from
      // the first render, and this handler gives it its FUNCTION as soon as the
      // notebook has run once.
      //
      // There is no public handle on the application in a stock JupyterLab, so
      // the command is reached the way a reader would: through the menu. By its
      // COMMAND ID, never by the label, because the label is translated.
      function runAllCells(){
        // RESTART and run all, in that order of preference. A fresh kernel is
        // how this notebook is meant to be started: the mega-cell defines every
        // name it uses, so a second run on a dirty kernel can inherit state from
        // the first one. Restarting removes the question.
        var CMDS = ['runmenu:restart-and-run-all', 'notebook:restart-run-all',
                    'runmenu:run-all', 'notebook:run-all-cells'];
        var app = window.jupyterapp || window.jupyterlab || null;
        // 2026-09-24s — THE COMMAND, NOT THE KERNEL.
        // 24n restarted the kernel through `session.kernel.restart()` because
        // that API does not put up a dialog. It also does not tell JupyterLab
        // that anything happened: the promise resolves while the front end is
        // still reconnecting, so the `run-all` fired on the next line ran
        // against a session that was not ready and quietly did nothing. The
        // kernel came back empty, the document did not, and the reader had to
        // restart it a second time by hand. Exactly what was reported.
        //
        // So the command is used again — the same one the menu item uses — and
        // the dialog it raises is hidden and accepted (armDialog). Commands are
        // chosen by `hasCommand`, because `execute` returns a PROMISE: it does
        // not throw for a command that does not exist, so the old loop always
        // stopped at the first name whether or not it was there.
        if (app && app.commands && app.commands.execute) {
          var pick = null, ci;
          for (ci = 0; ci < CMDS.length; ci++) {
            var has = true;
            try { if (app.commands.hasCommand) has = app.commands.hasCommand(CMDS[ci]); }
            catch (e) { has = true; }
            if (has) { pick = CMDS[ci]; break; }
          }
          if (pick) {
            armDialog();
            try {
              var pr = app.commands.execute(pick);
              if (pr && pr.catch) pr.catch(function(){
                // the chosen command refused — fall back to plain run-all
                try { app.commands.execute('notebook:run-all-cells'); } catch (e2) {}
              });
              return true;
            } catch (e) {}
          }
        }
        // No public handle in a stock JupyterLab, so the command is reached the
        // way a reader reaches it: through the menu bar. Two things had to be
        // learned the hard way — Lumino opens a menu on POINTERDOWN, not on
        // mousedown, and the command is called `runmenu:run-all`, not
        // `notebook:run-all-cells`. Matched by id, never by label, because the
        // label is translated.
        var fire = function(el, type, extra){
          var r = el.getBoundingClientRect();
          var o = {bubbles: true, cancelable: true, button: 0,
                   clientX: r.left + 6, clientY: r.top + 6};
          for (var k in (extra || {})) o[k] = extra[k];
          var C = type.indexOf('pointer') === 0 ? PointerEvent : MouseEvent;
          try { el.dispatchEvent(new C(type, o)); } catch (e) {}
        };
        var open = function(el){
          fire(el, 'pointerdown', {pointerId: 1, isPrimary: true});
          fire(el, 'mousedown');
        };
        var pick = function(){
          for (var j = 0; j < CMDS.length; j++) {
            var it = document.querySelector('.lm-Menu-item[data-command="' + CMDS[j]
                   + '"],.p-Menu-item[data-command="' + CMDS[j] + '"]');
            if (it && it.className.indexOf('mod-disabled') < 0) return it;
          }
          return null;
        };
        var bar = document.querySelectorAll('.lm-MenuBar-item,.p-MenuBar-item');
        for (var i = 0; i < bar.length; i++) {
          open(bar[i]);
          var hit = pick();
          if (hit) {
            // The same sequence a pointing device produces, in the same order.
            // Lumino sets the active item from a POINTERMOVE/MOUSEMOVE hit test
            // and triggers it on mouseup; a mousedown/mouseup pair on its own
            // finds no active item and does nothing at all.
            var r2 = hit.getBoundingClientRect();
            var cx = r2.left + r2.width / 2, cy = r2.top + r2.height / 2;
            var base = {bubbles: true, cancelable: true, button: 0, buttons: 1,
                        clientX: cx, clientY: cy, view: window};
            var seq = [['pointerover', 1], ['pointerenter', 1], ['mouseover', 0],
                       ['mouseenter', 0], ['pointermove', 1], ['mousemove', 0],
                       ['pointerdown', 1], ['mousedown', 0],
                       ['pointerup', 1], ['mouseup', 0], ['click', 0]];
            for (var q = 0; q < seq.length; q++) {
              var o2 = {}; for (var kk in base) o2[kk] = base[kk];
              if (seq[q][1]) { o2.pointerId = 1; o2.isPrimary = true;
                               o2.pointerType = 'mouse'; }
              if (seq[q][0] === 'pointerup' || seq[q][0] === 'mouseup'
                  || seq[q][0] === 'click') o2.buttons = 0;
              try {
                hit.dispatchEvent(new (seq[q][1] ? PointerEvent : MouseEvent)(
                    seq[q][0], o2));
              } catch (e) {}
            }
            armDialog();
            return true;
          }
          open(bar[i]);                 // toggle it shut and try the next one
        }
        return false;
      }
      // The fallback path still goes through a command that asks. The reader
      // already answered that question by pressing ▶, so the dialog is not shown
      // to them at all: `body.nbnodlg` hides it (a class, because CSS cannot
      // match text) and it is accepted on the next tick. The window is short —
      // 2.5 s from the click — and inside it the only dialog that can appear is
      // the one the button caused. Outside it, dialogs behave normally.
      function armDialog(){
        document.body.classList.add('nbnodlg');
        clearTimeout(window.__nbdlgOff);
        window.__nbdlgOff = setTimeout(function(){
          document.body.classList.remove('nbnodlg');
        }, 6000);
        var tries = 0;
        clearInterval(window.__nbdlgTick);
        window.__nbdlgTick = setInterval(function(){
          if (++tries > 240) {
            clearInterval(window.__nbdlgTick);
            document.body.classList.remove('nbnodlg');
            return;
          }
          var dlg = document.querySelector('.jp-Dialog');
          if (!dlg) return;
          var txt = (dlg.textContent || '').toLowerCase();
          if (txt.indexOf('restart') < 0) {
            // not ours — stop hiding at once and leave it alone
            clearInterval(window.__nbdlgTick);
            document.body.classList.remove('nbnodlg');
            return;
          }
          var ok = dlg.querySelector('.jp-mod-accept,.jp-Dialog-button.jp-mod-accept,'
                   + 'button.jp-mod-accept,.jp-Dialog-footer button:last-child');
          if (ok) {
            clearInterval(window.__nbdlgTick);
            ok.click();
            setTimeout(function(){
              document.body.classList.remove('nbnodlg');
            }, 120);
          }
        }, 25);
      }

      // JupyterLab offers to collapse and to "scroll" a cell's output: a click on
      // the blue gutter beside it folds the whole document into a small box with
      // a drag handle. There is exactly one output here and it IS the document,
      // so there is nothing to gain and a notebook to lose. The controls are
      // made inert in the stylesheet; this takes the state back off if a click
      // got through anyway, or if it arrived with the file.
      function unlockCell(src){
        var p = src && src.closest('.jp-NotebookPanel');
        if (!p) return;
        // 2026-09-24p — NO SCROLLING PAST THE END.
        // JupyterLab's "scroll past end" hangs a whole blank screen under the
        // last cell (measured: scrollHeight 3793 against 3006 of real content).
        // There is one cell here and it IS the document, so that blank is not
        // room to write in — it is a screen of nothing after the notebook has
        // said it is finished, and it is what let the reader scroll past the end
        // bar. The class is taken off; the notebook now stops where it stops.
        // E22.1b: the same three sets, looked up by class (static copies:
        // taking the class off changes a live list while it is walked)
        var inCell = function(e){ var pp = e.parentElement; return !!(pp && pp.closest('.jp-Cell')); };
        var nbs = allCls(p, 'jp-mod-scrollPastEnd').filter(function(e){ return e.classList.contains('jp-Notebook'); });
        for (var q = 0; q < nbs.length; q++)
          nbs[q].classList.remove('jp-mod-scrollPastEnd');
        var cells = allCls(p, 'jp-mod-outputsScrolled').filter(function(e){ return e.classList.contains('jp-Cell'); })
          .concat(allCls(p, 'jp-OutputArea-scrolled').filter(function(e){ return e.classList.contains('jp-OutputArea') && inCell(e); }));
        for (var i = 0; i < cells.length; i++) {
          cells[i].classList.remove('jp-mod-outputsScrolled');
          cells[i].classList.remove('jp-OutputArea-scrolled');
        }
        var hid = allCls(p, 'jp-mod-hidden').filter(function(e){
          return (e.classList.contains('jp-Cell-outputWrapper') || e.classList.contains('jp-OutputArea')) && inCell(e); });
        for (var j = 0; j < hid.length; j++) hid[j].classList.remove('jp-mod-hidden');
      }

      // ---- the theme ---------------------------------------------------
      // The notebook's palette FOLLOWS the front end's. Anything else and a
      // reader who switches JupyterLab to light is left with a dark document
      // inside a light application — which is exactly what happened: the ◐
      // button used to set a class that nothing ever took off again.
      function labDark(){
        return document.body.getAttribute('data-jp-theme-light') === 'false'
            || /Dark/.test(document.body.getAttribute('data-jp-theme-name') || '');
      }
      function themePref(){
        var v = (window.__nbStore ? window.__nbStore.get(TKEY) : '') || '';     // E25.o: this notebook's
        return v === 'dark' || v === 'light' ? v : '';
      }
      function setThemePref(v){
        if (window.__nbStore) { if (v) window.__nbStore.set(TKEY, v); else window.__nbStore.del(TKEY); }
      }
      // 2026-09-24bg — SKINS: what the notebook is made of, not how bright it
      // is. Light/dark and skin are two independent axes on purpose, so every
      // skin has a light half and a dark half and neither button undoes the
      // other. "minimal" is the absence of a skin class, not a copy of the
      // default rules — the one spelling that cannot drift from them.
      // 2026-10-06 (E24.6) — retro is no longer offered (nutzer): not in the
      // cycle, not in the 👤 choice; a saved "retro" is written back as
      // minimal once. Its rules stay in the stylesheet sources.
      // E34: „digi“ first — the standard (NB_DEF, 12-rail-series-role) and the cycle's start
      var SKINS = ['digi', 'minimal', 'cyber', 'fairy'];
      var SKINFACE = {digi: '\u25C9', minimal: '\u25CB', cyber: '\u25C6', fairy: '\u2726'};
      var SKEY = 'digichemjn.skin.v1';
      function skinPref(){
        var S = window.__nbStore, v = S ? S.get(SKEY) : null;                   // E25.o: this notebook's
        if (v === 'retro') { S.set(SKEY, 'minimal'); v = 'minimal'; }
        // E34: nothing stored = the standard (digi); an unknown stored word (an older build's) = minimal,
        // as before — a reader who had chosen is never moved to the new standard
        if (v == null || v === '') return NB_DEF.skin;
        return SKINS.indexOf(v) > -1 ? v : 'minimal';
      }
      function applySkin(){
        var sk = skinPref(), i;
        for (i = 0; i < SKINS.length; i++)
          document.body.classList.toggle('nbskin-' + SKINS[i],
                                         SKINS[i] !== 'minimal' && SKINS[i] === sk);
        document.body.classList.remove('nbskin-retro');   // E24.6: an older tab's class
        var host = document.getElementById(HOST_ID);
        var b = host && host.querySelector('.nbbtn.nbskin');
        if (b) {
          // the button wears the skin it is ON, not the one it would go to:
          // a control that shows its own state is readable standing still.
          if (b.textContent !== SKINFACE[sk]) b.textContent = SKINFACE[sk];
          b.title = nbL('style: ', 'Stil: ') + sk + nbL(' \u2014 click for ', '; ein Klick wechselt zu ')
                  + SKINS[(SKINS.indexOf(sk) + 1) % SKINS.length]
                  + nbL('. It works with light and dark, not instead of them.', '. Er gilt in hell und dunkel, nicht statt ihrer.');
        }
        return sk;
      }
      function nextSkin(){
        var sk = SKINS[(SKINS.indexOf(skinPref()) + 1) % SKINS.length];
        if (window.__nbStore) window.__nbStore.set(SKEY, sk);
        applySkin();
        return sk;
      }
      window.__nbApplySkin = applySkin;

      function applyTheme(){
        // 2026-09-25 — THE FRONT END IS A SEED, NOT A SOURCE.
        // `pref ? … : labDark()` meant that with no stored choice the document
        // re-read JupyterLab's theme on every call, so a switch in the Settings
        // menu moved the notebook for ever after. The front end is now read
        // ONCE, on the first run, and written down as the reader's own
        // preference — a friendly starting point that cannot come back later
        // and overrule them.
        // E15.3 — THE FRONT END'S SWITCH WINS. Seeded once, the stored
        // choice outlived every later Settings → Theme: one dark, and a light
        // JupyterLab stayed dark under nbforce-dark (measured v1.49, both
        // ways, also after a reload). Now each time the front end's state is
        // new to this page (first call, Settings, reload) it is written down
        // as the choice; ◐ still overrides until the front end moves again.
        // E34 — THE STANDARD IS DARK, AND IT LASTS. This notebook holds no light/dark and has never
        // seen the front end → the standard (NB_DEF.theme), whatever the Lab is; the Lab's state is
        // written down as SEEN, not as the choice. What it saw is kept per notebook (`themeseen`), so
        // a reload is not news any more; Settings → Theme (a state other than the one seen) still wins,
        // also while the notebook was closed. A notebook that holds a choice but no `seen` (a build
        // before E34) takes the front end's state once, as before — nobody is moved.
        var lab = document.body.getAttribute('data-jp-theme-light'), S = window.__nbStore;
        var SEEN = 'digichemjn.themeseen.v1';
        if (lab !== null) {
          var seen = S ? S.get(SEEN) : null;
          if (seen == null && !themePref() && S && S.set(SEEN, lab)) {
            setThemePref(NB_DEF.theme === 'light' || NB_DEF.theme === 'dark' ? NB_DEF.theme : (labDark() ? 'dark' : 'light'));
          } else if (seen == null ? lab !== window.__nbThemeSeen : lab !== seen) {
            if (S) S.set(SEEN, lab);
            setThemePref(labDark() ? 'dark' : 'light');
          }
          window.__nbThemeSeen = lab;
        }
        var pref = themePref();
        // no id yet (nothing stored) → the standard
        if (!pref) { pref = NB_DEF.theme === 'light' || NB_DEF.theme === 'dark' ? NB_DEF.theme : (labDark() ? 'dark' : 'light'); setThemePref(pref); }
        // 2026-09-27a — while the page prints, it is light (see printLight).
        var dark = pref === 'dark' && !window.__nbPrintSaved;
        window.__nbDark = dark;      // the one place anything may read it from
        document.body.classList.toggle('nbdark', dark);
        // The hand-made palette is only for the case where the front end did
        // NOT move — otherwise it would paint over a theme that is already right
        // and the two would drift apart at every edge.
        document.body.classList.toggle('nbforce-dark', dark && !labDark());
        // ...and the mirror image: a light choice while the front end is still
        // dark. Both overrides are dropped the moment the front end agrees, and
        // because they are the colours already on screen, that drop is invisible.
        document.body.classList.toggle('nbforce-light', !dark && labDark());
        var host = document.getElementById(HOST_ID);
        if (host) {
          var b = host.querySelector('.nbtheme');
          if (b) b.title = dark ? nbL('switch this notebook to light', 'dieses Notebook hell schalten')
                                : nbL('switch this notebook to dark', 'dieses Notebook dunkel schalten');
        }
        return dark;
      }
      // One duration for everything on screen: armed before the switch, taken
      // off after it, so the transition costs nothing for the rest of the time.
      window.__nbApplyTheme = applyTheme;
      // E16.10 (Applikation) — THE PROFILE IS SHARED: a style, light/dark or
      // text size chosen in another tab of this browser applies here as well
      // (storage event); nothing is rebuilt, nothing of the notebook moves
      if (window.__nbProfOff) window.__nbProfOff();
      // E17.5: … and the language, the role, the account and the default
      // content; their words and forms are redrawn by one sync, now (≤ 1 s)
      var profEv = function(e){
        // E23.14: the panel's width (guizoom) is the notebook's own now, not the profile's
        // E25.o: … and so are style, light/dark, language, role, content —
        // `<key>.<id>`, never matched here: another notebook moves nothing of
        // this one. What is left is the account record (password check,
        // favourites; logged in or not is per notebook) — a full key only
        if (e.key && !/^digichemjn\.(skin|theme|lang|role|account|defmode)\.v1$/.test(e.key)) return;
        try { applySkin(); applyTheme(); applyGui(document.getElementById(HOST_ID)); } catch (x) {}
        if (e.key && /(lang|role|account|defmode)\.v1$/.test(e.key)) {
          try { applyRole(); } catch (x) {}
          try { if (window.__nbAcctAll) window.__nbAcctAll(); } catch (x) {}
          try { if (window.__nbrailSync) window.__nbrailSync(); } catch (x) {}
        }
      };
      window.addEventListener('storage', profEv);
      window.__nbProfOff = function(){ window.removeEventListener('storage', profEv); };
      // 2026-09-27a — DARK PRINTS LIGHT. The print stylesheet (night 27.09.)
      // makes a handout, but every colour hangs on body.nbdark and CSS cannot
      // take a class away: retro dark printed dark pages. So for the print, and
      // only for it, applyTheme() computes the light half of the same skin; the
      // reader's stored choice is not touched. It is a FLAG read by
      // applyTheme(), not a class taken off once: measured, sync() calls
      // applyTheme() on every tick and put nbdark back within 1.5 s of
      // beforeprint — while a print dialog would still be open.
      function printLight(){
        if (window.__nbPrintSaved) return;
        window.__nbPrintSaved = true;
        applyTheme();
      }
      function printBack(){
        if (!window.__nbPrintSaved) return;
        window.__nbPrintSaved = false;
        applyTheme();
      }
      if (!window.__nbPrintV || vkey(window.__nbPrintV) <= vkey(NBRAIL_VERSION)) {
        if (window.__nbPrintH) {
          window.removeEventListener('beforeprint', window.__nbPrintH[0]);
          window.removeEventListener('afterprint', window.__nbPrintH[1]);
        }
        window.__nbPrintV = NBRAIL_VERSION;
        window.__nbPrintH = [printLight, printBack];
        window.addEventListener('beforeprint', printLight);
        window.addEventListener('afterprint', printBack);
      }
      function themeFade(){
        // 2026-09-24n: there is no fade any more. The switch is one frame for
        // every surface, ours and the front end's, because a duration is
        // exactly what let the two halves of the window disagree.
        // 2026-09-24y: and `nbtheming` is what ENFORCES that. It was left as a
        // no-op that only ever removed the class, so the boxes kept their own
        // `transition:background .3s` and arrived a third of a second after the
        // rest of the window — the lag the reader still saw inside the boxes.
        // The class now goes ON for the frame of the switch and off again
        // afterwards; every surface named in the rule paints at once.
        document.body.classList.add('nbtheming');
        clearTimeout(window.__nbrailFadeT);
        window.__nbrailFadeT = setTimeout(function(){
          document.body.classList.remove('nbtheming');
        }, 260);
      }
      // K2.5 — the point to keep through a zoom, and putting it back.
      // A CHOSEN MARK is kept by the MARK: at 60 %% the marks of a chapter
      // crowd and the rail moves a later one down to make room (§5), so its
      // pill and its mark are no longer level — measured: chapter 2's pill
      // on the line, its mark 59 px under it. The rail runs 1 : 1 with the
      // document, so scrolling the document by the mark's distance puts the
      // mark there. Without a choice, the point of the document the line
      // crosses is kept.
      var ZOOM_MARK = false;             // E11.5
      var ZMK = '.nbsect,.nbsubdot,.nbchapdot,.nbvizmark,.nbrail-dot,.nbcodemark';
      function zoomLine(host){
        var m = host && host.querySelector('.nbmap');
        if (!m) return null;
        var y0 = parseInt(host.dataset.railY0 || '0', 10) || 0;
        return y0 > 0 ? m.getBoundingClientRect().top + y0 : null;
      }
      function zoomMark(host, tgt){
        var n = host.querySelector('.nbmap-node.nbsel');
        if (!n || (tgt && n.getAttribute('data-target') !== tgt)) return null;
        var m = n.querySelector(ZMK), r = m && m.getBoundingClientRect();
        return r && r.height > 0 ? r.top + r.height / 2 : null;
      }
      function zoomKeep(host, sc){
        if (!host || !sc || !vertOn()) return null;
        var L = zoomLine(host);
        if (L === null) return null;
        // 2026-09-30 (E11.5, Struktur) — THE DOCUMENT POINT, ALWAYS. With a
        // chosen mark (the state after every click on the timeline) the mark
        // was kept, not the page: the mark is re-laid only on the next pass,
        // so between the steps of a zoom the page was pulled to a stale mark
        // and back — measured in the real JupyterLab with Ctrl+wheel 100 →
        // 130 → 60 → 100 %: the point on the reading height swung 104 /
        // 1152 / 131 px before it settled (without a chosen mark ≤ 0.4 px).
        // The reader asked for the other rule: what stands on the reading
        // height — wherever it has been dragged — stays there. The mark
        // branch is kept for nobody; ZOOM_MARK stays false.
        var sel = ZOOM_MARK ? host.querySelector('.nbmap-node.nbsel') : null;
        if (sel && !sel.classList.contains('nbgone')) {
          var tgt = sel.getAttribute('data-target') || '';
          var y = zoomMark(host, tgt);
          if (y !== null) return {host: host, tgt: tgt, d: y - L, el: sel, gen: window.__nbLandGen};
        }
        var sr = sc.getBoundingClientRect();
        // E11.5: the DOCUMENT on the line, not the panel lying over it (open,
        // the panel covers the middle of the scroller), and the SMALLEST
        // thing there: a big box (a cell, the list's viewport) also holds
        // the unscaled air, so a point kept as a fraction of it drifts.
        // Five places across the column; the lowest box of at least 8 px wins.
        var e = null, eh = 1e9, xs = [0.5, 0.35, 0.65, 0.2, 0.8];
        for (var xi = 0; xi < xs.length; xi++) {
          var hits = document.elementsFromPoint
                   ? document.elementsFromPoint(sr.left + sr.width * xs[xi], L)
                   : [document.elementFromPoint(sr.left + sr.width * xs[xi], L)];
          for (var hi = 0; hi < hits.length; hi++) {
            var c = hits[hi];
            if (!c || c === sc || !sc.contains(c)) continue;
            if (c.closest && c.closest('.nbfeed, .nbrail, .nbpanel-host')) continue;   // our own markup
            while (c && c !== sc && c.getBoundingClientRect().height < 8) c = c.parentElement;
            if (c && c !== sc) {
              var chh = c.getBoundingClientRect().height;
              if (chh < eh) { e = c; eh = chh; }
            }
            break;
          }
        }
        while (e && e !== sc && e.getBoundingClientRect().height < 8) e = e.parentElement;
        if (!e || e === sc || !sc.contains(e)) return null;
        var r = e.getBoundingClientRect();
        return {host: host, el: e, frac: (L - r.top) / (r.height || 1), d: 0,
                gen: window.__nbLandGen};
      }
      // 2026-10-12 (E29 D2, JavaScript) — THE READER'S OWN SCROLL ENDS THE
      // HOLD. After a change of the lens the page was put back on the kept
      // point for 2.2 s (60 … 2200 ms below) — and every wheel notch in that
      // time was undone: the page stood still or jumped back (reader 12.10.:
      // "nach Zoomwechsel hängt das Scrollen"; measured v1.75: 4 notches after
      // Ctrl+wheel, the page back on its start 4 times). A wheel without Ctrl,
      // a key that scrolls or a touch move stamps the time; a hold older than
      // that stamp lets go, and the next lens step takes a new point.
      if (!window.__nbUserMoveOn) {
        window.__nbUserMoveOn = 1;
        var userMove = function(ev){
          if (ev.type === 'wheel' && (ev.ctrlKey || ev.metaKey)) return;
          if (ev.type === 'keydown' && !/^(Arrow(Up|Down)|Page(Up|Down)|Home|End| )$/.test(ev.key)) return;
          window.__nbUserMoveAt = Date.now();
        };
        ['wheel', 'touchmove', 'keydown'].forEach(function(t){
          document.addEventListener(t, userMove, {capture: true, passive: true});
        });
      }
      function userMovedSince(t){ return (window.__nbUserMoveAt || 0) >= (t || 0); }
      function zoomBack(k, sc){
        if (userMovedSince(k.at)) return;                         // E29 D2
        // 2026-09-30 (E10.5, Struktur) — A LANDING STARTED SINCE OWNS THE
        // PAGE. The lens is applied to every new cell's wrappers too, and
        // the hold that follows (up to 2.2 s) pulled the page back to where
        // the line had been — at 60 % and 150 % the new own cell stood
        // 170–320 px off the reading height (v1.35 + E10.5 alone, measured).
        if (k.gen !== window.__nbLandGen) return;
        // E11.5: the hold is the vertical rail's; switched to the banner the
        // line means something else (test_js flips orientation within 2 s)
        if (!vertOn()) return;
        var L = zoomLine(k.host);
        if (L === null) return;
        var y;
        if (k.tgt !== undefined) y = zoomMark(k.host, k.tgt);
        else if (k.el.isConnected) {
          var r = k.el.getBoundingClientRect(); y = r.top + k.frac * r.height;
        }
        if (y === null || y === undefined) return;
        var d = Math.round(y - L - k.d);
        if (Math.abs(d) >= 1) sc.scrollTop = Math.max(0, sc.scrollTop + d);
      }
      function applyZoom(host, src){
        var pct = zoomLevel(), want = pct === 100 ? '' : String(pct / 100);
        // an older build zoomed the page itself — take it back off
        if (document.body.style.zoom) document.body.style.zoom = '';
        // ...and 2026-09-24b zoomed the windowed container, which is what made
        // the document come back empty. Undo it wherever it is still set.
        var p0 = src && src.closest('.jp-NotebookPanel');
        if (p0) {
          var zs = function(e){ return /zoom/.test(e.getAttribute('style') || ''); };   // E22.1b
          var bad = allCls(p0, 'jp-WindowedPanel-inner').concat(allCls(p0, 'jp-Notebook')).filter(zs);
          for (var b = 0; b < bad.length; b++) bad[b].style.zoom = '';
        }
        var tg = zoomTargets(src), i;
        // 2026-09-28c (K3.5) — the page's texture keeps pace with the lens
        // (the tokens are resolved on <body>, so the factor lives there)
        var tz = String(pct / 100);
        if (document.body.style.getPropertyValue('--nbtexz') !== tz)
          document.body.style.setProperty('--nbtexz', tz);
        // 2026-09-30 (E9.3, Struktur) — THE LENS FACTOR FOR THE STYLESHEET
        // (contract of 07-skins / 10-names / CSS-E9.3, open since E8.2):
        // on <body> and on <html>, the same number. The stylesheet scales the
        // panel's sizes with it (--nbk × --nbzf); applyGui scales its
        // geometry with the same factor (window.__nbK).
        if (document.body.style.getPropertyValue('--nbzf') !== tz)
          document.body.style.setProperty('--nbzf', tz);
        if (document.documentElement.style.getPropertyValue('--nbzf') !== tz)
          document.documentElement.style.setProperty('--nbzf', tz);
        // KEEP THE READING POSITION. Scaling the content changes the document's
        // whole length, so a scrollTop left untouched lands the reader somewhere
        // else entirely — usually a chapter or two away from the one they were
        // reading. The zoom is uniform, so the same content is at the same
        // FRACTION of the document before and after: measure it, apply the zoom,
        // put it back. Done here rather than in the caller, because only here is
        // it certain that nothing else moved in between.
        var sc1 = src && (src.closest('.jp-WindowedPanel-outer')
                       || src.closest('.jp-Notebook'));
        var h0 = sc1 ? sc1.scrollHeight : 0, t0 = sc1 ? sc1.scrollTop : 0;
        // 2026-09-28b (K2.5) — THE READING LINE KEEPS WHAT IS ON IT.
        // The fraction rule below put back the same share of the document,
        // which is not the same chapter: after 100 → 150 %% the chosen chapter
        // stood tens of pixels off the cursor (measured 28a). What is kept now
        // is a POINT: the chosen mark's own point (the one a click lands,
        // __nbAim) if a mark is chosen, else whatever the reading line crosses
        // — at the same height as before, after every relayout pass.
        // several steps in a row (a drag, Ctrl+plus held down) keep the point
        // taken BEFORE the first one — re-reading it mid-relayout would carry
        // each step's error into the next
        // (only a call that CHANGES the zoom renews it: the sync calls this
        // every 1.5 s, and renewing there kept a point from long before alive)
        var kk = window.__nbZoomKeep;
        var keep = (kk && Date.now() - kk.t < 1600 && kk.k.host === host && !userMovedSince(kk.k.at)) ? kk.k : null;   // E29 D2
        var changed = false;
        for (i = 0; i < tg.length; i++) {
          if (tg[i].style.zoom !== want) {
            if (!changed && !keep) { keep = zoomKeep(host, sc1); if (keep) keep.at = Date.now() + 1; }   // E29 D2
            tg[i].style.zoom = want; changed = true;
          }
          if (tg[i].style.width) tg[i].style.width = '';
        }
        if (changed && keep) window.__nbZoomKeep = {k: keep, t: Date.now()};
        if (changed && sc1 && keep) {
          // E4.4: the head air first, so the title has room to stay on the line
          var back = function(){ if (host) headAir(host); zoomBack(keep, sc1); };
          back();
          [60, 260, 600, 1000, 1500, 2200].forEach(function(ms){ setTimeout(back, ms); });
        } else if (changed && sc1 && h0 > 0 && t0 > 0) {
          var rAt = Date.now() + 1;
          var restore = function(){
            if (userMovedSince(rAt)) return;                     // E29 D2
            var h1 = sc1.scrollHeight;
            if (h1 > 0 && Math.abs(h1 - h0) > 1) {
              var want2 = Math.round(t0 * h1 / h0);
              want2 = Math.max(0, Math.min(want2, h1 - sc1.clientHeight));
              if (Math.abs(sc1.scrollTop - want2) > 1) sc1.scrollTop = want2;
            }
          };
          restore();
          // ...and once more after the front end has re-laid the cells out,
          // because the height it reports in this pass is the old one
          setTimeout(restore, 60);
          setTimeout(restore, 260);
        }
        // The front end's virtual scroller sizes itself from what it measured
        // last; a cell that just changed height has to be noticed. A scroll event
        // is the cheapest way to ask it to look again, and it is harmless when
        // there is no virtual scroller at all.
        var sc0 = src && (src.closest('.jp-WindowedPanel-outer')
                       || src.closest('.jp-Notebook'));
        if (sc0) { try { sc0.dispatchEvent(new Event('scroll')); } catch (e) {} }
        if (!host) return;
        if (host.style.transform !== 'none') host.style.transform = 'none';
        slider(host, '.nbz-doc', pct, '\ud83d\udd0d ');   // 2026-09-24at: a lens, not a word
      }
