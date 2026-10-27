      // ---- progress across the whole series -------------------------------
      // Each notebook writes its own record; the panel adds them up. This lives in
      // the browser (localStorage), so it is per browser and per device and it goes
      // when the site data goes — which is why every notebook can also print a
      // portable code. Nothing leaves the machine.
      var STORE = 'digichemjn.progress.v1';
      // ---- zoom -----------------------------------------------------------
      // Ctrl+wheel zooms the whole page, panel included, and on a wide screen it
      // left the content column off centre. This zooms the NOTEBOOK only: the
      // panel keeps its size and its axis, and the column stays centred because
      // the caps above carry auto margins.
      var ZKEY = 'digichemjn.zoom.v1';
      // The panel has a size of its own, separate from the document's. One bar
      // scales what you READ, the other scales the instrument you read it with;
      // mixing the two into a single control was what made the old 'A' button
      // useless — it scaled neither properly.
      var GKEY = 'digichemjn.guizoom.v1', GPXKEY = 'digichemjn.guipx.v1';
      var OKEY = 'digichemjn.orient.v1';
      // '' (or absent) = follow the front end; 'dark' / 'light' = the reader
      // decided, and that decision outlives a reload until they change the
      // front end's own theme, which is a louder statement than the ◐ button.
      var TKEY = 'digichemjn.theme.v1';
      // 25 % is "one line and nothing else"; 160 % is the panel at its most
      // generous. The whole range is reachable, because the far end of it is the
      // point: a reader who wants the text and not the instrument can wind the
      // panel down to a hairline instead of hiding it.
      var GMIN = 0, GMAX = 100;
      // Keep a slider and its readout in step with the stored value — without
      // writing to the input while the reader is dragging it, which would fight
      // the drag.
      // 2026-09-24o — THE PANEL CONTROL RUNS THE OTHER WAY.
      // Dragging the thumb towards the panel folds it away; dragging it back
      // towards the document opens it out. The stored number is unchanged
      // (0 = the line alone, 100 = everything), so only the thumb is mirrored —
      // the readout still says how much panel there is.
      function guiFlip(v){ return GMAX + GMIN - v; }
      function slider(host, grp, pct, name){
        var g = host.querySelector(grp);
        if (!g) return;
        var inp = g.querySelector('.nbslider'), out = g.querySelector('.nbslval');
        var shown = grp === '.nbz-gui' ? guiFlip(pct)
                  : grp === '.nbz-doc' ? zoomSlide(pct) : pct;
        if (inp && document.activeElement !== inp && +inp.value !== shown)
          inp.value = String(shown);
        if (out) {
          // The PANEL readout says how much panel there is (the thumb is
          // mirrored, the number is not); the DOCUMENT readout says where the
          // thumb stands, because that is the scale the reader set.
          // both readouts say the STORED value: how much panel there is, and
          // what the document is zoomed to. The thumb may be mirrored or
          // rescaled; the number never is (2026-09-24bi).
          // 2026-09-25 — NO NUMBER BESIDE THE BAR.
          // The percentage was a readout of a control the reader is already
          // holding: the thumb says where it stands, and the number only told
          // them again, in the busiest corner of the toolbar. The lens stays —
          // it is what says WHAT the bar does — and it lights up while the
          // setting is away from its default, which is the one thing the thumb
          // alone does not say at a glance.
          var lbl = pct;
          var txt = name.replace(/\s+$/, '');
          if (out.textContent !== txt) out.textContent = txt;
          out.classList.toggle('on', lbl !== (grp === '.nbz-doc' ? 100 : 0));
        }
      }
      function guiLevel(){
        // `|| 100` would turn a stored 0 back into 100 — and 0 is a setting now:
        // the line and the marker, and nothing else.
        // 2026-09-24r: the notebook opens at 0 % — the narrow rail — and the
        // reader opens it out if they want the names.
        // 2026-09-24al — THE STORED VALUE IS NOT READ BACK ANY MORE.
        // With the names gone there is nothing in a wide panel to look at, so
        // opening one out is a thing you do for a moment, not a setting you
        // carry between sessions. The control still works; every open starts at
        // 0 again. (The write is kept — an older panel in another tab reads it.)
        // 2026-10-06 (E23.14, Applikation) — THE PANEL'S WIDTH IS THE
        // NOTEBOOK'S OWN. It was one number for the whole page (window.__nbGui):
        // Complex and Modeling open side by side in one JupyterLab shared it —
        // the panel opened out in one notebook stood open in the other (reader,
        // 06.10., „dringend“). Now each notebook keeps its own, in memory and
        // under `digichemjn.guizoom.v1.<id>` (level C, like the lens and the
        // mode; never in the profile or the account), and it is read back on
        // the next open. Nothing is taken over from the old shared key (no
        // earlier readers, reader 06.10.: no backward compatibility) — an old
        // `digichemjn.guizoom.v1` is simply never read. No storage event moves
        // it: the profile's listener (15-rail-theme) knows only `….v1` keys.
        // A notebook without an id yet (not run) keeps the page's value.
        var k = gKey(), v;
        if (k) {
          var by = window.__nbGuiBy || (window.__nbGuiBy = {});
          if (!(k in by)) {
            var s = null;
            try { s = localStorage.getItem(k); } catch (e) {}
            by[k] = s === null ? 0 : parseFloat(s);
          }
          v = by[k];
          window.__nbGui = v;            // what the measuring scripts read
        } else v = window.__nbGui;
        if (v === undefined || v === null || isNaN(v)) v = 0;
        return Math.max(GMIN, Math.min(gMax(), v));
      }
      function gKey(){ var id = nbId(); return id ? GKEY + '.' + id : null; }
      // 2026-10-06 (E23.14 Nach-Runde, Applikation) — THE WIDTH COMES BACK IN
      // PIXELS. The control is a share (0 = the line alone, 100 = the standard
      // width) of the travel from the narrow end WMIN — and WMIN is not a
      // constant: it is the widest mark × lens (markFloor), measured anew when
      // the page shows the notebook again, and it came out a few pixels
      // different after a tab switch or a reload (the shut panel read 32 or
      // 38 px). The same share then drew another width: measured v1.65 +
      // js-E23.14, tor row pair, D23.14: opened to 201 px, after a tab switch
      // 193. The panel is the reader's width, not a share of it: the width it
      // drew is kept beside the share (`digichemjn.guipx.v1.<id>`, level C as
      // the share) and drawn again as long as the share is the same —
      // applyGui (14) reads it; a new drag or the ⚙ control stores a new one.
      function guiPx(){
        var k = gKey(); if (!k) return 0;
        var PB = window.__nbGuiPx || (window.__nbGuiPx = {});
        if (!(k in PB)) {
          var s = null;
          try { s = localStorage.getItem(GPXKEY + '.' + k.slice(GKEY.length + 1)); } catch (e) {}
          PB[k] = s === null ? 0 : parseFloat(s) || 0;
        }
        return PB[k] || 0;
      }
      function setGui(pct){
        wHalf(document.getElementById(HOST_ID));
        pct = Math.max(GMIN, Math.min(gMax(), pct));
        window.__nbGui = pct;            // the session's value; see guiLevel()
        var k = gKey();                  // E23.14: the notebook's own, not GKEY
        if (k) {
          (window.__nbGuiBy || (window.__nbGuiBy = {}))[k] = pct;
          try { localStorage.setItem(k, String(pct)); } catch (e) {}
        }
        var host = document.getElementById(HOST_ID);
        if (k) (window.__nbGuiPx || (window.__nbGuiPx = {}))[k] = 0;   // a new share: drawn from the share
        applyGui(host);
        // E23.14 Nach-Runde: … and the width this drew, in pixels (below)
        if (k) {
          var px = pct > 0 ? Math.round(window.__nbW || 0) : 0, PB = window.__nbGuiPx || (window.__nbGuiPx = {});
          if (px > 0) { PB[k] = px; try { localStorage.setItem(GPXKEY + '.' + k.slice(GKEY.length + 1), String(px)); } catch (e) {} }
          else { delete PB[k]; try { localStorage.removeItem(GPXKEY + '.' + k.slice(GKEY.length + 1)); } catch (e) {} }
        }
        // the node boxes changed height (or the column changed width), so the
        // whole geometry has to be measured again — not just repositioned
        if (window.__nbrailSync) window.__nbrailSync();
      }
      window.__nbSetGui = setGui;   // the suites drive the real control

      // ====================================================================
      // 2026-09-25f — WHO IS LOOKING.
      //
      // The 📚 badge counts every notebook of the series this browser has
      // seen. For the person teaching the course that is the point; for a
      // student it is a number about themselves that nobody asked them to
      // keep, sitting in the toolbar of every notebook they open.
      //
      // (25f: a role `reader` | `administrator` decided whether the series
      // was shown — a view, never a permission.)
      // E38a J3 (2026-10-26, Werkstatt JS; Nutzer 14.10.: Reihen- und
      // Gesamtstatistik sehen alle) — THE ROLE IS GONE, without a substitute.
      // Everyone sees the series rows and the totals; no choice, no class
      // `nbadmin`, nothing stored. An old `digichemjn.role.v1` (this
      // notebook's store or the profile) is removed once, so nothing is left
      // that once meant something. `__nbRole()` stays as a constant 'reader'
      // and `__nbApplyRole()` as the clean-up — callers (15-rail-theme,
      // 19-rail-title-sync, the suites) need not change.
      var ROLEKEY = 'digichemjn.role.v1';
      function roleOf(){ return 'reader'; }
      function applyRole(){
        document.body.classList.remove('nbadmin');
        try { if (window.__nbStore && window.__nbStore.get(ROLEKEY)) window.__nbStore.del(ROLEKEY); } catch (e) {}
        return 'reader';
      }
      window.__nbRole = roleOf;
      window.__nbApplyRole = applyRole;

      // ====================================================================
      // 2026-10-02 (E17.4, Applikation) — A QR CODE WITHOUT A LIBRARY.
      // QR code, byte mode, error correction L, versions 1–40, own code (no
      // library): returns the module matrix (true = dark). After the
      // reference design (ISO/IEC 18004, the "Project Nayuki" layout).
      function qrMatrix(text){
        var data = [], i, j, k;
        var u = unescape(encodeURIComponent(text));          // UTF-8 bytes
        for (i = 0; i < u.length; i++) data.push(u.charCodeAt(i));
        var ECL = [7, 10, 15, 20, 26, 18, 20, 24, 30, 18, 20, 24, 26, 30, 22, 24, 28, 30, 28, 28, 28, 28, 30,
                   30, 26, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30];
        var NB = [1, 1, 1, 1, 1, 2, 2, 2, 2, 4, 4, 4, 4, 4, 6, 6, 6, 6, 7, 8, 8, 9, 9, 10, 12, 12, 12,
                  13, 14, 15, 16, 17, 18, 19, 19, 20, 21, 22, 24, 25];
        function rawMods(v){
          var r = (16 * v + 128) * v + 64;
          if (v >= 2) { var na = Math.floor(v / 7) + 2; r -= (25 * na - 10) * na - 55; if (v >= 7) r -= 36; }
          return r;
        }
        function dataCw(v){ return Math.floor(rawMods(v) / 8) - ECL[v - 1] * NB[v - 1]; }
        var ver = 0;
        for (var v = 1; v <= 40; v++) {
          var bits = 4 + (v < 10 ? 8 : 16) + 8 * data.length;
          if (bits <= dataCw(v) * 8) { ver = v; break; }
        }
        if (!ver) return null;
        var bb = [];
        function put(val, len){ for (var q = len - 1; q >= 0; q--) bb.push((val >>> q) & 1); }
        put(4, 4); put(data.length, ver < 10 ? 8 : 16);
        data.forEach(function(b){ put(b, 8); });
        var cap = dataCw(ver) * 8;
        put(0, Math.min(4, cap - bb.length));
        put(0, (8 - bb.length % 8) % 8);
        for (var pad = 0xEC; bb.length < cap; pad ^= 0xEC ^ 0x11) put(pad, 8);
        var cw = [];
        for (i = 0; i < bb.length; i += 8) { var x = 0; for (j = 0; j < 8; j++) x = (x << 1) | bb[i + j]; cw.push(x); }
        // Reed–Solomon over GF(256), polynomial 0x11D
        function mul(a, b){ var z = 0; for (var t = 7; t >= 0; t--) { z = (z << 1) ^ ((z >>> 7) * 0x11D); z ^= ((b >>> t) & 1) * a; } return z; }
        var deg = ECL[ver - 1], div = [], root = 1;
        for (i = 0; i < deg - 1; i++) div.push(0);
        div.push(1);
        for (i = 0; i < deg; i++) {
          for (j = 0; j < div.length; j++) { div[j] = mul(div[j], root); if (j + 1 < div.length) div[j] ^= div[j + 1]; }
          root = mul(root, 0x02);
        }
        function rem(d){
          var r = div.map(function(){ return 0; });
          d.forEach(function(b){
            var f = b ^ r.shift(); r.push(0);
            div.forEach(function(c, n){ r[n] ^= mul(c, f); });
          });
          return r;
        }
        var nb = NB[ver - 1], raw = Math.floor(rawMods(ver) / 8), nShort = nb - raw % nb,
            shortLen = Math.floor(raw / nb), blocks = [], off = 0;
        for (i = 0; i < nb; i++) {
          var dl = shortLen - deg + (i < nShort ? 0 : 1), dat = cw.slice(off, off + dl);
          off += dl;
          var ec = rem(dat);
          if (i < nShort) dat.push(0);
          blocks.push(dat.concat(ec));
        }
        var all = [];
        for (i = 0; i < blocks[0].length; i++)
          for (j = 0; j < blocks.length; j++)
            if (i !== shortLen - deg || j >= nShort) all.push(blocks[j][i]);
        // the matrix
        var S = ver * 4 + 17, M = [], F = [];
        for (i = 0; i < S; i++) { M.push(new Array(S).fill(false)); F.push(new Array(S).fill(false)); }
        function set(x, y, d){ M[y][x] = d; F[y][x] = true; }
        for (i = 0; i < S; i++) { set(6, i, i % 2 === 0); set(i, 6, i % 2 === 0); }
        function finder(cx, cy){
          for (var dy = -4; dy <= 4; dy++) for (var dx = -4; dx <= 4; dx++) {
            var d = Math.max(Math.abs(dx), Math.abs(dy)), xx = cx + dx, yy = cy + dy;
            if (xx >= 0 && xx < S && yy >= 0 && yy < S) set(xx, yy, d !== 2 && d !== 4);
          }
        }
        finder(3, 3); finder(S - 4, 3); finder(3, S - 4);
        var al = [];
        if (ver > 1) {
          var na2 = Math.floor(ver / 7) + 2, step = ver === 32 ? 26 : Math.ceil((ver * 4 + 4) / (na2 * 2 - 2)) * 2;
          al = [6]; for (var pos = S - 7; al.length < na2; pos -= step) al.splice(1, 0, pos);
        }
        al.forEach(function(ax, ai){ al.forEach(function(ay, aj){
          if ((ai === 0 && aj === 0) || (ai === 0 && aj === al.length - 1) || (ai === al.length - 1 && aj === 0)) return;
          for (var dy = -2; dy <= 2; dy++) for (var dx = -2; dx <= 2; dx++)
            set(ax + dx, ay + dy, Math.max(Math.abs(dx), Math.abs(dy)) !== 1);
        }); });
        function format(mask){
          var d = (1 << 3) | mask, r = d;                        // ECC L = 01
          for (var t = 0; t < 10; t++) r = (r << 1) ^ ((r >>> 9) * 0x537);
          var b = ((d << 10) | r) ^ 0x5412;
          for (t = 0; t <= 5; t++) set(8, t, ((b >>> t) & 1) !== 0);
          set(8, 7, ((b >>> 6) & 1) !== 0); set(8, 8, ((b >>> 7) & 1) !== 0); set(7, 8, ((b >>> 8) & 1) !== 0);
          for (t = 9; t < 15; t++) set(14 - t, 8, ((b >>> t) & 1) !== 0);
          for (t = 0; t < 8; t++) set(S - 1 - t, 8, ((b >>> t) & 1) !== 0);
          for (t = 8; t < 15; t++) set(8, S - 15 + t, ((b >>> t) & 1) !== 0);
          set(8, S - 8, true);
        }
        format(0);
        if (ver >= 7) {
          var r2 = ver;
          for (i = 0; i < 12; i++) r2 = (r2 << 1) ^ ((r2 >>> 11) * 0x1F25);
          var vb = (ver << 12) | r2;
          for (i = 0; i < 18; i++) {
            var bt = ((vb >>> i) & 1) !== 0, a = S - 11 + i % 3, c = Math.floor(i / 3);
            set(a, c, bt); set(c, a, bt);
          }
        }
        // the data, in the zigzag
        var bi = 0;
        for (var right = S - 1; right >= 1; right -= 2) {
          if (right === 6) right = 5;
          for (var vert = 0; vert < S; vert++) for (j = 0; j < 2; j++) {
            var xx = right - j, up = ((right + 1) & 2) === 0, yy = up ? S - 1 - vert : vert;
            if (!F[yy][xx] && bi < all.length * 8) { M[yy][xx] = ((all[bi >>> 3] >>> (7 - (bi & 7))) & 1) !== 0; bi++; }
          }
        }
        function applyMask(m){
          for (var y = 0; y < S; y++) for (var x = 0; x < S; x++) {
            if (F[y][x]) continue;
            var inv = [(x + y) % 2 === 0, y % 2 === 0, x % 3 === 0, (x + y) % 3 === 0,
                       (Math.floor(x / 3) + Math.floor(y / 2)) % 2 === 0, x * y % 2 + x * y % 3 === 0,
                       (x * y % 2 + x * y % 3) % 2 === 0, ((x + y) % 2 + x * y % 3) % 2 === 0][m];
            if (inv) M[y][x] = !M[y][x];
          }
        }
        function penalty(){
          // rules 1, 2 and 4 of the standard (runs, 2×2 blocks, balance);
          // any mask is a valid code, this only picks a well readable one
          var p = 0, x, y, dark = 0;
          for (var a = 0; a < S; a++) for (var o = 0; o < 2; o++) {
            var n = 1;
            for (var b = 1; b <= S; b++) {
              var same = b < S && (o ? M[b][a] === M[b - 1][a] : M[a][b] === M[a][b - 1]);
              if (same) { n++; continue; }
              if (n >= 5) p += n - 2;
              n = 1;
            }
          }
          for (y = 0; y < S - 1; y++) for (x = 0; x < S - 1; x++) {
            var c3 = M[y][x];
            if (c3 === M[y][x + 1] && c3 === M[y + 1][x] && c3 === M[y + 1][x + 1]) p += 3;
            if (c3) dark++;
          }
          return p + Math.floor(Math.abs(dark * 20 - S * S * 10) / (S * S)) * 10;
        }
        var best = 0, bestP = 1e9;
        for (k = 0; k < 8; k++) {
          applyMask(k); format(k);
          var pk = penalty();
          if (pk < bestP) { bestP = pk; best = k; }
          applyMask(k);
        }
        applyMask(best); format(best);
        return M;
      }
      // the matrix as one SVG path (quiet zone 4 modules), drawn in currentColor
      function qrSvg(text, px){
        var M = qrMatrix(text);
        if (!M) return '';
        var S = M.length, d = '';
        for (var y = 0; y < S; y++) for (var x = 0; x < S; x++)
          if (M[y][x]) d += 'M' + (x + 4) + ' ' + (y + 4) + 'h1v1h-1z';
        var n = S + 8;
        return '<svg class="nbacct-qr" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + n + ' ' + n
             + '" width="' + (px || 4 * n) + '" height="' + (px || 4 * n) + '" shape-rendering="crispEdges"'
             + ' role="img" aria-label="QR code of your account code">'
             + '<rect width="' + n + '" height="' + n + '" fill="#fff"/><path fill="#000" d="' + d + '"/></svg>';
      }

      // ====================================================================
      // 2026-10-02 (E17.4 + E19.5, Applikation) — THE ACCOUNT, WITHOUT A SERVER.
      //
      // Three levels (E17): A the ACCOUNT `digichemjn.account.v1` (person id,
      // favourites, logged in or not) · B the PROFILE, shared by every
      // notebook of this browser (style, light/dark, language, role, panel
      // size, `progress.v1` per notebook) · C the NOTEBOOK (lens, reading
      // height, own cells, …) — C never goes into the account.
      //
      // Between browsers, machines and front ends (Lab, Lite, Colab, Binder
      // keep separate stores) the only bridge is the ACCOUNT CODE:
      //   DCJ1.<base64url>.<2 check characters>
      //   base64url = version byte · salt (16) · iv (12) · AES-GCM( deflate( text ) )
      //   text      = 1~<person id>~<5 favourites>~<notebook>[.<mode>]=<states>|<codes>|<difficulties>~…
      // The key comes from the reader's PASSWORD (PBKDF2-SHA-256, 300 000
      // rounds) in this browser; no server ever sees either. Without the
      // password the code opens for nobody — there is no reset, and the
      // window says so. The check characters catch a typo before the
      // password is blamed. What is in it: states and difficulties per
      // exercise, the favourites, the person id. What is never in it or in
      // the store (concept §4): answers, cell contents, timestamps.
      //
      // One door to the store (`window.__nbStore`, backend "local"). A server
      // ("which codes were handed out") needs a decision of the user — server
      // and legal basis, APPLIKATION-server-und-recht.md — so `remote` is the
      // prepared interface only: it refuses, with the reason.
      var ACCT_KEY = 'digichemjn.account.v1', LANG_KEY = 'digichemjn.lang.v1',
          DEFMODE_KEY = 'digichemjn.defmode.v1';
      // 2026-10-08 (E25.o, JavaScript) — STANDARD FIRST, THEN PERSONAL — PER
      // NOTEBOOK. Nutzer 08.10.: a notebook opened for the first time is the
      // standard (minimal, light/dark as Jupyter, English, both, lens 100 %%);
      // not logged in, every notebook keeps ITS OWN settings and takes over
      // nothing from another one; logged in (in this notebook) the account's
      // favourites hold for this notebook only. Replaces the shared profile
      // of E16.10/E17 (level B). So the profile's keys are the notebook's:
      // `<key>.<notebook id>` — read and written through this door (`pk`),
      // the old shared value is never read (no old users, E23.17). No id yet
      // (nothing of the notebook has run) → nothing stored, the standard. The
      // account record itself (person id, favourites, password check) stays
      // one per browser; whether it is ON is the notebook's (`acct.on.<id>`).
      // E34 (2026-10-19, JavaScript) — THE STANDARD IS „digi“, DARK. Nutzer 19.10.: the notebooks
      // look like the digi web page and app from the first opening („Standardstil“). Only where this
      // notebook holds NO choice: a stored skin or light/dark is the reader's and stays (no reader is
      // moved). Same values as Python's NB_DEFAULTS (py-E34 P1/P2). `themeseen` = the front end's
      // light/dark last seen by this notebook, so the standard survives a reload under a light Lab and
      // a switch in Settings → Theme still wins (E15.3) — before, every reload was „new“.
      var NB_DEF = window.__nbDEF = {skin: 'digi', theme: 'dark'};
      var PROF_RE = /^digichemjn\.(skin|theme|themepick|themeseen|lang|role|defmode)\.v1$/;
      // The language is spelled as py-E25.o reads it in Lite (the kernel
      // learns it there from `digichemjn.lang.<id>`): one key for both sides.
      function pk(k){
        if (!PROF_RE.test(k)) return k;
        var id = ''; try { id = nbId(); } catch (e) {}
        if (!id) return null;
        return k === 'digichemjn.lang.v1' ? 'digichemjn.lang.' + id : k + '.' + id;
      }
      window.__nbPK = pk;
      var nbStore = window.__nbStore = {
        backend: 'local',
        get: function(k){ k = pk(k); if (!k) return null; try { return localStorage.getItem(k); } catch (e) { return null; } },
        set: function(k, v){ k = pk(k); if (!k) return false; try { localStorage.setItem(k, v); return true; } catch (e) { return false; } },
        del: function(k){ k = pk(k); if (!k) return false; try { localStorage.removeItem(k); return true; } catch (e) { return false; } },
        json: function(k, d){
          k = pk(k); if (!k) return d;
          try { var v = JSON.parse(localStorage.getItem(k)); return v == null ? d : v; } catch (e) { return d; }
        },
        put: function(k, o){ return nbStore.set(k, JSON.stringify(o)); },
        remote: {
          ready: false,
          why: 'no server: where codes are kept and on which legal basis is the user\'s decision '
             + '(APPLIKATION-server-und-recht.md)',
          push: function(){ return Promise.reject(new Error(nbStore.remote.why)); },
          pull: function(){ return Promise.reject(new Error(nbStore.remote.why)); }
        }
      };
      var B32 = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';          // Crockford: no I L O U
      function acRnd(n){ var a = new Uint8Array(n); crypto.getRandomValues(a); return a; }
      // 60 random bits, read aloud in groups of four: DCJ-7QK4-M2PX-9RTF
      function acNewId(){
        var b = acRnd(12), s = '';
        for (var i = 0; i < 12; i++) s += B32[b[i] & 31] + (i === 3 || i === 7 ? '-' : '');
        return 'DCJ-' + s;
      }
      function acUtf8(s){ return new TextEncoder().encode(s); }
      function acB64(u){
        var s = ''; for (var i = 0; i < u.length; i++) s += String.fromCharCode(u[i]);
        return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
      }
      function acUnB64(s){
        s = s.replace(/-/g, '+').replace(/_/g, '/');
        var r = atob(s + '==='.slice((s.length + 3) % 4)), u = new Uint8Array(r.length);
        for (var i = 0; i < r.length; i++) u[i] = r.charCodeAt(i);
        return u;
      }
      // two check characters (10 bits of FNV-1a over what precedes them)
      function acCheck(s){
        var h = 0x811c9dc5;
        for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
        return B32[(h >>> 5) & 31] + B32[h & 31];
      }
      function acZip(u, back){
        if (!window.CompressionStream) return Promise.reject(new Error('nozip'));
        var S = back ? new DecompressionStream('deflate-raw') : new CompressionStream('deflate-raw');
        return new Response(new Blob([u]).stream().pipeThrough(S)).arrayBuffer()
          .then(function(b){ return new Uint8Array(b); });
      }
      var AC_ITER = 300000;
      function acKey(pw, salt, bits){
        var C = crypto.subtle;
        return C.importKey('raw', acUtf8(pw), 'PBKDF2', false, ['deriveKey', 'deriveBits']).then(function(k){
          var p = {name: 'PBKDF2', salt: salt, iterations: AC_ITER, hash: 'SHA-256'};
          return bits ? C.deriveBits(p, k, 256)
                      : C.deriveKey(p, k, {name: 'AES-GCM', length: 256}, false, ['encrypt', 'decrypt']);
        });
      }
      // the password is checked against a hash kept with the account
      // (its own salt), never stored itself
      function acVerifier(pw, vs){
        return acKey(pw, vs, true).then(function(b){ return crypto.subtle.digest('SHA-256', b); })
          .then(function(h){ return acB64(new Uint8Array(h)); });
      }
      function acReady(){
        // WebCrypto lives only on a secure page (https, localhost)
        return !!(window.crypto && crypto.subtle && window.isSecureContext !== false);
      }

      // ---- the account record ------------------------------------------
      // E25.o: logged in = in THIS notebook (`digichemjn.acct.on.<id>`); the
      // record's own `on` is not read (a record of an older build carried it)
      function acOnKey(){ var id = ''; try { id = nbId(); } catch (e) {} return id ? 'digichemjn.acct.on.' + id : null; }
      function acGet(){
        var a = nbStore.json(ACCT_KEY, null);
        if (!a || !a.id) return null;
        var k = acOnKey(); a.on = !!(k && nbStore.get(k) === '1');
        return a;
      }
      function acOn(){ var a = acGet(); return !!(a && a.on); }
      function acSave(a){
        var r = {}, k = acOnKey();
        for (var x in a) if (x !== 'on') r[x] = a[x];
        nbStore.put(ACCT_KEY, r);
        if (k && 'on' in a) { if (a.on) nbStore.set(k, '1'); else nbStore.del(k); }
      }
      var FAV = {skin: {digi: 'd', minimal: 'm', cyber: 'c', retro: 'r', fairy: 'f', anime: 'a'},
                 theme: {auto: 'a', light: 'l', dark: 'd'},
                 lang: {en: 'e', de: 'd'},
                 role: {reader: 'r'},          // E38a J3: an old 'a' reads as nothing
                 mode: {both: 'b', calc: 'c', code: 'k', plain: 'p'}};
      var FAV_ORDER = ['skin', 'theme', 'lang', 'role', 'mode'];
      function favPack(f){
        return FAV_ORDER.map(function(k){ return FAV[k][f[k]] || '-'; }).join('');
      }
      function favUnpack(s){
        var f = {};
        FAV_ORDER.forEach(function(k, i){
          f[k] = '';
          for (var w in FAV[k]) if (FAV[k][w] === s.charAt(i)) f[k] = w;
        });
        return f;
      }
      function langNow(){ return nbStore.get(LANG_KEY) === 'de' ? 'de' : 'en'; }
      // the profile as it stands = the favourites a new account starts with
      function favNow(){
        var a = acGet(), f = (a && a.fav) || {};
        return {skin: nbStore.get('digichemjn.skin.v1') || NB_DEF.skin,             // E34
                // light/dark is always stored (E15.3 writes the front end's);
                // the FAVOURITE is what was picked in 👤 (auto = as the front end)
                theme: nbStore.get('digichemjn.themepick.v1') || f.theme || 'auto',
                lang: langNow(),
                role: 'reader',            // E38a J3: no role any more (the code keeps its place)
                mode: nbStore.get(DEFMODE_KEY) || f.mode || ''};
      }

      // ---- progress, per notebook and content ---------------------------
      // the kernel's own words (progress_code() of the toolkit): one
      // character per exercise — o open · f wrong · s skipped · d solved —
      // for the written and the coding route, and the difficulty it was
      // settled at (g s t, '-'). Kept in `progress.v1[<id>].p[<mode>]`.
      var AC_RANK = {o: 0, f: 1, s: 2, d: 3};
      function acMerge(a, b){
        // the further state wins, per exercise and route; never back
        if (!a) return b; if (!b) return a;
        var A = a.split('|'), Bv = b.split('|');
        if (A[0].length !== Bv[0].length || A[1].length !== Bv[1].length) return b;   // other version: keep ours
        var st = '', cd = '', df = '', i, da = A[2] || '', db = Bv[2] || '';
        for (i = 0; i < A[0].length; i++) {
          var ra = AC_RANK[A[0][i]] || 0, rb = AC_RANK[Bv[0][i]] || 0;
          st += ra > rb ? A[0][i] : Bv[0][i];
          // the difficulty goes with the state that wins; on a tie the one known
          df += (ra > rb ? da[i] : ra < rb ? db[i] : (db[i] && db[i] !== '-' ? db[i] : da[i])) || '-';
        }
        for (i = 0; i < A[1].length; i++)
          cd += (AC_RANK[A[1][i]] || 0) > (AC_RANK[Bv[1][i]] || 0) ? A[1][i] : Bv[1][i];
        return st + '|' + cd + '|' + df;
      }
      function acCounts(body){
        var p = body.split('|'), st = p[0] || '', cd = p[1] || '', df = p[2] || '';
        var n = function(s, ch){ return s.split(ch).length - 1; };
        var g = [0, 0, 0];
        for (var i = 0; i < st.length; i++)
          if (st[i] === 'd') g[df[i] === 'g' ? 0 : df[i] === 't' ? 2 : 1]++;
        return {a: [n(st, 'd'), st.length], c: [n(cd, 'd'), cd.length],
                s: [n(st, 'd'), n(st, 's'), n(st, 'f')], g: g};
      }
      function acProgAll(){ return nbStore.json('digichemjn.progress.v1', {}) || {}; }
      // fold a code's progress into this browser's records, never back
      function acTakeProgress(map){
        var all = acProgAll(), n = 0;
        Object.keys(map).forEach(function(key){
          var dot = key.indexOf('.'), id = dot > -1 ? key.slice(0, dot) : key, md = dot > -1 ? key.slice(dot + 1) : 'both';
          var r = all[id] || {title: id};
          r.p = r.p || {};
          var m = acMerge(map[key], r.p[md]);
          if (m !== r.p[md]) n++;
          r.p[md] = m;
          if (!r.a || md === 'both') { var c = acCounts(m); r.a = c.a; r.s = c.s; r.g = c.g; if (!r.c) r.c = c.c; }
          all[id] = r;
        });
        nbStore.put('digichemjn.progress.v1', all);
        // the kernels hear of it when their notebook runs next (E17.5)
        var pend = nbStore.json('digichemjn.acct.push', {}) || {};
        Object.keys(map).forEach(function(k){ pend[k] = 1; });
        nbStore.put('digichemjn.acct.push', pend);
        return n;
      }
      function acProgMap(){
        var all = acProgAll(), out = {};
        Object.keys(all).sort().forEach(function(id){
          var p = all[id] && all[id].p;
          if (!p || /[~=]/.test(id)) return;
          Object.keys(p).sort().forEach(function(md){
            if (/^[odsf]*\|[odsf]*\|[gst-]*$/.test(p[md] || ''))
              out[id + (md === 'both' ? '' : '.' + md)] = p[md];
          });
        });
        return out;
      }

      // ---- the code -----------------------------------------------------
      function acText(a){
        var map = acProgMap();
        return ['1', a.id.replace(/^DCJ-|-/g, ''), favPack(a.fav || {})]
          .concat(Object.keys(map).map(function(k){ return k + '=' + map[k]; })).join('~');
      }
      function acParseText(t){
        var p = t.split('~');
        if (p[0] !== '1' || !/^[0-9A-Z]{12}$/.test(p[1] || '')) throw new Error('form');
        var id = 'DCJ-' + p[1].slice(0, 4) + '-' + p[1].slice(4, 8) + '-' + p[1].slice(8);
        var map = {};
        p.slice(3).forEach(function(e){
          var q = e.indexOf('=');
          if (q > 0 && /^[odsf]*\|[odsf]*\|[gst-]*$/.test(e.slice(q + 1))) map[e.slice(0, q)] = e.slice(q + 1);
        });
        return {id: id, fav: favUnpack(p[2] || ''), map: map};
      }
      function acSeal(text, pw){
        var salt = acRnd(16), iv = acRnd(12), plain = acUtf8(text), flag = 0x11;
        return acZip(plain).catch(function(){ flag = 0x10; return plain; }).then(function(z){
          return acKey(pw, salt).then(function(k){
            return crypto.subtle.encrypt({name: 'AES-GCM', iv: iv}, k, z);
          }).then(function(ct){
            ct = new Uint8Array(ct);
            var all = new Uint8Array(29 + ct.length);
            all[0] = flag; all.set(salt, 1); all.set(iv, 17); all.set(ct, 29);
            var head = 'DCJ1.' + acB64(all);
            return head + '.' + acCheck(head);
          });
        });
      }
      function acOpen(code, pw){
        var c = String(code || '').replace(/\s+/g, '');
        var m = /^(DCJ1\.[A-Za-z0-9_-]+)\.([0-9A-Z]{2})$/.exec(c);
        if (!m) return Promise.reject(new Error(/^DCJ/i.test(c) ? 'typo' : 'old'));
        if (acCheck(m[1]) !== m[2]) return Promise.reject(new Error('typo'));
        var all;
        try { all = acUnB64(m[1].slice(5)); } catch (e) { return Promise.reject(new Error('typo')); }
        if (all.length < 45 || (all[0] !== 0x11 && all[0] !== 0x10)) return Promise.reject(new Error('typo'));
        return acKey(pw, all.slice(1, 17)).then(function(k){
          return crypto.subtle.decrypt({name: 'AES-GCM', iv: all.slice(17, 29)}, k, all.slice(29));
        }).then(function(z){
          z = new Uint8Array(z);
          return all[0] === 0x11 ? acZip(z, true) : z;
        }, function(){ throw new Error('password'); }).then(function(u){
          return acParseText(new TextDecoder().decode(u));
        });
      }

      // ---- what the window and the cover call --------------------------
      var AC_MSG = {
        typo:     ['This code has a typo: a character is missing or changed.',
                   'Dieser Code hat einen Tippfehler: ein Zeichen fehlt oder ist anders.'],
        password: ['This password does not open this code.',
                   'Dieses Passwort öffnet diesen Code nicht.'],
        form:     ['This code is from a newer version of the notebooks.',
                   'Dieser Code stammt aus einer neueren Version der Notebooks.'],
        insecure: ['Accounts need a secure page (https or localhost); this page is not one.',
                   'Konten brauchen eine sichere Seite (https oder localhost); diese ist keine.'],
        short:    ['The password needs at least 8 characters.',
                   'Das Passwort braucht mindestens 8 Zeichen.'],
        nomatch:  ['The two passwords are not the same.',
                   'Die beiden Passwörter sind nicht gleich.'],
        wrongpw:  ['That is not the password of this account.',
                   'Das ist nicht das Passwort dieses Kontos.']
      };
      function acSay(k){ var m = AC_MSG[k]; return m ? m[langNow() === 'de' ? 1 : 0] : String(k); }
      function acErr(e){ var k = e && e.message; return {ok: false, why: k, msg: acSay(AC_MSG[k] ? k : 'typo')}; }
      // favourites → profile, once per page (and at once on a log-in)
      function acApplyFav(force){
        var a = acGet();
        if (!a || !a.on || !a.fav) return false;
        var fd = a.id + '/' + (acOnKey() || '');                // E25.o: once per notebook
        if (window.__nbFavDone === fd && !force) return false;
        window.__nbFavDone = fd;
        var f = a.fav;
        if (f.skin === 'retro') { f.skin = 'minimal'; acSave(a); }   // E24.6: retro is not offered any more
        if (f.skin && nbStore.get('digichemjn.skin.v1') !== f.skin) nbStore.set('digichemjn.skin.v1', f.skin);
        if (f.lang) nbStore.set(LANG_KEY, f.lang);
        if (f.mode) nbStore.set(DEFMODE_KEY, f.mode);
        if (f.theme) nbStore.set('digichemjn.themepick.v1', f.theme);
        if (f.theme === 'light' || f.theme === 'dark') {
          nbStore.set('digichemjn.theme.v1', f.theme);
          // the front end's present state is not news (E15.3): the favourite stands until it moves
          window.__nbThemeSeen = document.body.getAttribute('data-jp-theme-light');
          if (window.__nbThemeSeen !== null) nbStore.set('digichemjn.themeseen.v1', window.__nbThemeSeen);   // E34
        }
        try { window.__nbApplySkin && window.__nbApplySkin(); } catch (e) {}
        try { window.__nbApplyTheme && window.__nbApplyTheme(); } catch (e) {}
        try { window.__nbApplyRole && window.__nbApplyRole(); } catch (e) {}
        return true;
      }
      // a setting changed in the window: the profile, and the account if one is on
      function acSetFav(k, v){
        if (k === 'skin') nbStore.set('digichemjn.skin.v1', v);
        if (k === 'lang') nbStore.set(LANG_KEY, v === 'de' ? 'de' : 'en');
        if (k === 'mode') { if (v) nbStore.set(DEFMODE_KEY, v); else nbStore.del(DEFMODE_KEY); }
        if (k === 'theme') { nbStore.set('digichemjn.themepick.v1', v); if (v === 'light' || v === 'dark') nbStore.set('digichemjn.theme.v1', v); }
        var a = acGet();
        if (a && a.on) { a.fav = a.fav || {}; a.fav[k] = v; acSave(a); }
      }
      window.__nbAcct = {
        ready: acReady, get: acGet, on: acOn, onKey: acOnKey, lang: langNow, say: acSay,
        fav: favNow, setFav: acSetFav, applyFav: acApplyFav, merge: acMerge,
        progress: acProgMap, take: acTakeProgress, qr: function(t, px){ return qrSvg(t, px); },
        // a new account: a person id from chance, the password's hash
        create: function(pw){
          if (!acReady()) return Promise.resolve({ok: false, why: 'insecure', msg: acSay('insecure')});
          if (String(pw || '').length < 8) return Promise.resolve({ok: false, why: 'short', msg: acSay('short')});
          var vs = acRnd(16), f = favNow();
          return acVerifier(pw, vs).then(function(vh){
            var a = {v: 1, id: acNewId(), on: true, fav: f, vs: acB64(vs), vh: vh};
            acSave(a);
            window.__nbFavDone = a.id + '/' + (acOnKey() || '');
            return {ok: true, id: a.id};
          });
        },
        // the code of now: favourites and every notebook's progress
        code: function(pw){
          var a = acGet();
          if (!a) return Promise.resolve({ok: false, msg: ''});
          if (!acReady()) return Promise.resolve({ok: false, why: 'insecure', msg: acSay('insecure')});
          return acVerifier(pw, acUnB64(a.vs)).then(function(vh){
            if (vh !== a.vh) return {ok: false, why: 'wrongpw', msg: acSay('wrongpw')};
            a.fav = favNow(); acSave(a);
            return acSeal(acText(a), pw).then(function(c){ return {ok: true, code: c}; });
          });
        },
        // log in: account and favourites from the code, progress folded in
        login: function(code, pw){
          if (!acReady()) return Promise.resolve({ok: false, why: 'insecure', msg: acSay('insecure')});
          return acOpen(code, pw).then(function(d){
            var vs = acRnd(16);
            return acVerifier(pw, vs).then(function(vh){
              var a = {v: 1, id: d.id, on: true, fav: d.fav, vs: acB64(vs), vh: vh};
              acSave(a);
              var n = acTakeProgress(d.map);
              acApplyFav(true);
              return {ok: true, id: d.id, notebooks: Object.keys(d.map).length, changed: n};
            });
          }, function(e){ return e && e.message === 'old' ? {ok: false, old: true} : acErr(e); });
        },
        logout: function(){ var a = acGet(); if (a) { a.on = false; acSave(a); } window.__nbFavDone = null; },
        // the file: the same sealed code, nothing in clear
        file: function(code){
          var blob = new Blob([JSON.stringify({format: 'digichemjn-konto', v: 1, code: code}, null, 1)],
                              {type: 'application/json'});
          var u = URL.createObjectURL(blob), ln = document.createElement('a');
          ln.href = u; ln.download = 'digichemjn-konto.json';
          document.body.appendChild(ln); ln.click(); ln.remove();
          setTimeout(function(){ URL.revokeObjectURL(u); }, 4000);
        },
        unfile: function(text){
          try { var o = JSON.parse(text); return o && o.format === 'digichemjn-konto' ? String(o.code || '') : ''; }
          catch (e) { return ''; }
        }
      };

      // ---- the log-in, wherever it is shown (E19.5) ----------------------
      // One form, two places: the 👤 window (E17.2) and the cover (E17.3).
      // A container `.nbacct[data-where]` is filled here and answers its own
      // clicks. 2026-10-03 (rebase on v1.62): the markup is the stylesheet's
      // contract of E19.5 (13-stats.css) and py-E17.3's cover block, no own
      // one any more —
      //   .nbacct[data-in="0|1"][data-where][data-step="out|new|in"]
      //     .nbacct-t                    heading (cover; in 👤 the cell's .nbcell-h)
      //     .nbacct-me                   .nbacct-id (person id, or "not logged in")
      //                                  + logged in: password + "Show my code" + Log out
      //     .nbacct-form                 logged out: code, password, Log in, New account, file
      //                                  · new: password twice, Create, Cancel
      //       input.nbacct-code · .nbacct-pwbox > input.nbacct-pw + button.nbacct-eye[aria-pressed]
      //       button.nbacct-btn[data-do] (.nbprimary main · .nbdanger log out)
      //     .nbacct-codebox > code.nbacct-codetext + buttons + .nbacct-qr > svg
      //     .nbacct-msg[data-kind="ok|err|info"] · .nbacct-note
      // [hidden] and [aria-invalid] as the stylesheet reads them. Inline only
      // what the layout needs (a code that breaks anywhere).
      function acEsc(s){ return String(s).replace(/[&<>"]/g, function(c){ return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }
      // The state of a form (message, step, code shown, what was typed) is
      // kept per place, not on the box: the panel is rebuilt whole when its
      // shape or its marks change (18, adopt), and a rebuilt 👤 window shows
      // the same answer and the same typed text (measured lab_acct c: a
      // rebuild right after the run took the code, the click and the answer
      // with it). Page memory only — nothing of it goes to the store.
      var AC_UI = window.__nbAcUi = window.__nbAcUi || {};
      function acState(where){ return AC_UI[where] || (AC_UI[where] = {vals: {}}); }
      function acForm(box){
        var a = acGet(), de = langNow() === 'de';
        var L = function(en, dd){ return de ? dd : en; };
        var where = box.getAttribute('data-where') || '';
        var ui = acState(where);
        var st = a && a.on ? 'in' : (ui.mk ? 'new' : 'out');
        var sig = [st, a ? a.id : '', de, ui.code || '', ui.qr ? 1 : 0, where, ui.msg || '', ui.kind || '', ui.bad || ''].join('|');
        if (box.__nbSig === sig && !box.__nbForce) return;
        // a tick never re-draws under the reader's typing; an answer does,
        // and what was typed stays
        var ae = document.activeElement, same = box.__nbSig && box.__nbSig.split('|')[0] === st;
        if (!box.__nbForce && ae && box.contains(ae) && ae.tagName === 'INPUT' && same) return;
        box.__nbForce = false;
        if (ui.step !== st) { ui.vals = {}; ui.step = st; }             // another step: nothing typed carries over
        var kept = ui.vals;
        if (same) [].forEach.call(box.querySelectorAll('input'), function(i){ if (i.value) kept[i.className] = i.value; });
        box.__nbSig = sig;
        box.setAttribute('data-in', st === 'in' ? '1' : '0');
        box.setAttribute('data-step', st);
        if (box.style.display === 'none') box.style.removeProperty('display');      // py-E17.3: hidden before Play
        var btn = function(d, t, cls){ return '<button type="button" class="nbacct-btn' + (cls ? ' ' + cls : '') + '" data-do="' + d + '">' + t + '</button>'; };
        var badPw = ui.bad === 'pw', badCode = ui.bad === 'code';
        var pw = function(ph, cls, nw){
          return '<span class="nbacct-pwbox"><input type="password" class="nbacct-pw' + (cls ? ' ' + cls : '') + '" autocomplete="'
               + (nw ? 'new-password' : 'current-password') + '" placeholder="' + ph + '" aria-label="' + ph + '"'
               + (badPw ? ' aria-invalid="true"' : '') + '><button type="button" class="nbacct-eye" aria-pressed="false" title="'
               + L('show or hide the password', 'Passwort zeigen oder verbergen') + '">&#128065;</button></span>';
        };
        var h = where === 'cover' ? '<div class="nbacct-t">' + L('Your account', 'Ihr Konto') + '</div>' : '';
        if (st === 'in') {
          h += '<div class="nbacct-me"><b class="nbacct-id" title="' + L('your person id: random, no name in it', 'Ihre Personen-Id: zufällig, kein Name darin')
             + '">' + acEsc(a.id) + '</b>' + pw(L('password', 'Passwort')) + btn('code', L('Show my code', 'Meinen Code zeigen'), 'nbprimary')
             + btn('out', L('Log out', 'Abmelden'), 'nbacct-logout nbdanger') + '</div>';
          if (ui.code) {
            h += '<div class="nbacct-codebox"><code class="nbacct-codetext" style="display:block;word-break:break-all;white-space:normal;margin:8px 0">'
               + acEsc(ui.code) + '</code><div class="nbacct-form">' + btn('copy', L('Copy', 'Kopieren')) + btn('qr', 'QR')
               + btn('file', L('Save as file', 'Als Datei')) + '</div>'
               + (ui.qr ? '<div class="nbacct-qr">' + qrSvg(ui.code, 232) + '</div>' : '') + '</div>';
          }
        } else if (st === 'new') {
          h += '<div class="nbacct-me"><b class="nbacct-id">' + L('New account', 'Neues Konto') + '</b></div>'
             + '<div class="nbacct-form">' + pw(L('password (8 or more)', 'Passwort (8 oder mehr)'), 'nbacct-pw1', 1)
             + pw(L('password again', 'Passwort noch einmal'), 'nbacct-pw2', 1)
             + btn('create', L('Create account', 'Konto anlegen'), 'nbprimary') + btn('cancel', L('Cancel', 'Abbrechen')) + '</div>';
        } else {
          h += '<div class="nbacct-me"><b class="nbacct-id">' + L('Not logged in', 'Nicht angemeldet') + '</b></div>'
             + '<div class="nbacct-form"><input type="text" class="nbacct-code" spellcheck="false" autocomplete="username" placeholder="'
             + L('account code DCJ1.… (or an older progress code)', 'Konto-Code DCJ1.… (oder ein älterer Fortschritts-Code)')
             + '" aria-label="' + L('account code', 'Konto-Code') + '"' + (badCode ? ' aria-invalid="true"' : '') + '>' + pw(L('password', 'Passwort'))
             + btn('in', L('Log in', 'Anmelden'), 'nbacct-login nbprimary') + btn('new', L('New account', 'Neues Konto'), 'nbacct-new')
             + btn('load', L('Load file', 'Datei laden')) + '</div>';
        }
        h += '<div class="nbacct-msg" role="status" aria-live="polite" data-kind="' + (ui.kind || 'info') + '">' + acEsc(ui.msg || '') + '</div>';
        h += '<div class="nbacct-note">' + L('The code carries your settings and progress, never answers or cells. '
             + '<b>There is no password reset:</b> without the password nobody can open the code, not even we.',
             'Der Code trägt Einstellungen und Fortschritt, nie Antworten oder Zellen. <b>Ein Passwort lässt sich nicht '
             + 'zurücksetzen:</b> ohne Passwort kann niemand den Code öffnen, auch wir nicht.') + '</div>';
        box.innerHTML = h;
        [].forEach.call(box.querySelectorAll('input'), function(i){ if (kept[i.className]) i.value = kept[i.className]; });
      }
      // o: {msg, tone: ok|bad|'' (→ data-kind ok|err|info), bad: pw|code|'', code, qr, mk}
      function acUi(box, o){
        o = Object.assign({}, o);
        if ('tone' in o) { o.kind = o.tone === 'ok' ? 'ok' : o.tone === 'bad' ? 'err' : 'info'; delete o.tone; if (!('bad' in o)) o.bad = ''; }
        var where = box.getAttribute('data-where') || '', ui = acState(where);
        // the box may have been rebuilt since the click: its typed values first
        if (box.isConnected) [].forEach.call(box.querySelectorAll('input'), function(i){ if (i.value) ui.vals[i.className] = i.value; });
        if (o.clearPw) { Object.keys(ui.vals).forEach(function(k){ if (/nbacct-pw/.test(k)) delete ui.vals[k]; }); delete o.clearPw; }
        Object.assign(ui, o);
        [].forEach.call(document.querySelectorAll('.nbacct[data-where="' + where + '"]'), function(b){ b.__nbForce = true; acForm(b); });
        acAll();
      }
      // what is typed is kept for its place (see AC_UI)
      function acInput(ev){
        var i = ev.target, bx = i && i.closest ? i.closest('.nbacct[data-where]') : null;
        if (!bx || i.tagName !== 'INPUT') return;
        acState(bx.getAttribute('data-where')).vals[i.className] = i.value;
      }
      // every form on the page shows the same account
      function acAll(){ [].forEach.call(document.querySelectorAll('.nbacct[data-where]'), acForm); }
      window.__nbAcctForm = acForm;
      window.__nbAcctAll = acAll;
      // an older single-notebook code goes to the kernel of the notebook in
      // front: through py-E17.5's merge field (`.nbctl-merge`, the kernel
      // merges, never lowers) when the build has it, else the toolkit's own
      // "Restore from code" (it checks the code either way)
      function acOldCode(code){
        var vp = visiblePanel(), h = document.getElementById(HOST_ID);
        var box = (h && h.querySelector('.nbctl-code')) || (vp || document).querySelector('.nbctl-code');
        if (!box) return false;
        var mi = box.querySelector('.nbctl-merge input, input.nbctl-merge');
        var inp = box.querySelector('input'), go = null;
        [].forEach.call(box.querySelectorAll('button'), function(b){ if (/Restore|Wiederherstellen/.test(b.textContent)) go = b; });
        if (!mi && (!inp || !go)) return false;
        window.__nbKpHold = Date.now() + 8000;          // E17.5: no read of the kernel meanwhile
        var t = mi || inp;
        t.value = code;
        t.dispatchEvent(new Event('input', {bubbles: true}));
        t.dispatchEvent(new Event('change', {bubbles: true}));
        if (!mi) setTimeout(function(){ go.click(); }, 120);
        return box;
      }
      // which field an answer blames (the stylesheet marks it, aria-invalid)
      function acBad(r){
        var w = r && (r.why || '');
        if (w === 'password' || w === 'wrongpw' || w === 'short' || w === 'nomatch') return 'pw';
        if (w === 'typo' || w === 'form') return 'code';
        return '';
      }
      function acClick(ev){
        var eye = ev.target && ev.target.closest ? ev.target.closest('.nbacct .nbacct-eye') : null;
        if (eye) {                                         // show / hide the password
          ev.preventDefault(); ev.stopPropagation();
          var pi = eye.parentNode && eye.parentNode.querySelector('input.nbacct-pw');
          var on = eye.getAttribute('aria-pressed') !== 'true';
          eye.setAttribute('aria-pressed', on ? 'true' : 'false');
          if (pi) { pi.type = on ? 'text' : 'password'; pi.focus(); }
          return;
        }
        var b = ev.target && ev.target.closest ? ev.target.closest('.nbacct .nbacct-btn') : null;
        if (!b) return;
        var box = b.closest('.nbacct'), d = b.getAttribute('data-do'), A = window.__nbAcct;
        ev.preventDefault(); ev.stopPropagation();
        var val = function(sel){ var i = box.querySelector(sel); return i ? i.value : ''; };
        var busy = function(t){ acUi(box, {msg: t, tone: ''}); };
        var de = langNow() === 'de', L = function(en, dd){ return de ? dd : en; };
        var showCode = function(c, extra){ acUi(box, {code: c, qr: false, mk: false, clearPw: true, msg: extra || L(
          'This is your account code. Keep it, with your password, outside this browser.',
          'Das ist Ihr Konto-Code. Bewahren Sie ihn mit Ihrem Passwort außerhalb dieses Browsers auf.'), tone: 'ok'}); };
        if (d === 'new') return acUi(box, {mk: true, msg: '', code: ''});
        if (d === 'cancel') return acUi(box, {mk: false, msg: ''});
        if (d === 'out') { A.logout(); return acUi(box, {code: '', qr: false, clearPw: true, msg: L('Logged out. Your progress stays in this browser.',
                                       'Abgemeldet. Ihr Fortschritt bleibt in diesem Browser.'), tone: 'ok'}); }
        if (d === 'qr') return acUi(box, {qr: !acState(box.getAttribute('data-where') || '').qr});
        if (d === 'copy') {
          var c = acState(box.getAttribute('data-where') || '').code || '';
          var done = function(){ acUi(box, {msg: L('Copied.', 'Kopiert.'), tone: 'ok'}); };
          if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(c).then(done, function(){});
          else { var t = box.querySelector('.nbacct-codetext'); if (t) { var r = document.createRange(); r.selectNodeContents(t);
                 var s = getSelection(); s.removeAllRanges(); s.addRange(r); try { document.execCommand('copy'); done(); } catch (e) {} } }
          return;
        }
        if (d === 'file') return A.file(acState(box.getAttribute('data-where') || '').code || '');
        if (d === 'load') {
          var f = document.createElement('input'); f.type = 'file'; f.accept = '.json,application/json';
          f.onchange = function(){
            var fl = f.files && f.files[0]; if (!fl) return;
            fl.text().then(function(t){
              var c2 = A.unfile(t), ci = box.querySelector('.nbacct-code');
              if (c2 && ci) { ci.value = c2; acUi(box, {msg: L('Code loaded from the file. Now the password.',
                                                                 'Code aus der Datei geladen. Jetzt das Passwort.'), tone: 'ok'}); }
              else acUi(box, {msg: L('This is not an account file.', 'Das ist keine Konto-Datei.'), tone: 'bad'});
            });
          };
          f.click();
          return;
        }
        if (d === 'create') {
          var p1 = val('.nbacct-pw1'), p2 = val('.nbacct-pw2');
          if (p1 !== p2) return acUi(box, {msg: acSay('nomatch'), tone: 'bad', bad: 'pw'});
          busy(L('Creating …', 'Wird angelegt …'));
          var kc0 = window.__nbKernelProgress;
          return A.create(p1).then(function(r){
            if (!r.ok) return acUi(box, {msg: r.msg, tone: 'bad', bad: acBad(r)});
            return Promise.resolve(kc0 ? kc0() : 0).catch(function(){}).then(function(){ return A.code(p1); }).then(function(c3){ showCode(c3.code, L('Account created. This is your code: keep it, with your password, outside this browser.',
                                                                    'Konto angelegt. Das ist Ihr Code: Bewahren Sie ihn mit Ihrem Passwort außerhalb dieses Browsers auf.')); });
          });
        }
        if (d === 'code') {
          busy(L('Sealing …', 'Wird versiegelt …'));
          var kc = window.__nbKernelProgress;
          return Promise.resolve(kc ? kc() : 0).catch(function(){}).then(function(){ return A.code(val('.nbacct-pw')); })
            .then(function(r){ if (r.ok) showCode(r.code); else acUi(box, {msg: r.msg, tone: 'bad', bad: acBad(r)}); });
        }
        if (d === 'in') {
          var code = val('.nbacct-code').trim(), p = val('.nbacct-pw');
          if (!code) return;
          busy(L('Opening …', 'Wird geöffnet …'));
          return A.login(code, p).then(function(r){
            if (r.old) {
              var ob = acOldCode(code);
              if (!ob) return acUi(box, {msg: L('An older progress code needs this notebook to have run once.',
                                               'Ein älterer Fortschritts-Code braucht ein Notebook, das einmal gelaufen ist.'), tone: 'bad'});
              acUi(box, {msg: L('An older progress code: handed to this notebook …', 'Ein älterer Fortschritts-Code: an dieses Notebook übergeben …'), tone: ''});
              var t0 = Date.now();
              (function wait(){
                var o = ob.querySelector('.nbctl-merge-res') || ob.querySelector('.widget-html, .jupyter-widget-HTML, .widget-html-content');
                var t = o ? o.textContent.replace(/\s+/g, ' ').trim() : '';
                var done = /Restored|does not|belongs|covers|contains|look like/.test(t);
                if (!done && Date.now() - t0 < 6000) return setTimeout(wait, 200);
                acUi(box, {msg: done ? t : L('Sent to the kernel.', 'An den Kernel geschickt.'), tone: /Restored/.test(t) ? 'ok' : (done ? 'bad' : '')});
              })();
              return;
            }
            if (!r.ok) return acUi(box, {msg: r.msg, tone: 'bad', bad: acBad(r)});
            try { window.__nbKernelPush && window.__nbKernelPush(); } catch (e) {}
            // the favourites may have brought another language: say it in that one
            var de2 = langNow() === 'de', L2 = function(en, dd){ return de2 ? dd : en; };
            acUi(box, {code: '', clearPw: true, msg: L2('Logged in. Settings applied; progress of ', 'Angemeldet. Einstellungen übernommen; Fortschritt aus ')
                       + r.notebooks + L2(' notebook(s) merged (nothing goes back).', ' Notebook(s) zusammengeführt (nichts wird zurückgestuft).'), tone: 'ok'});
          });
        }
      }
      if (window.__nbAcctOff) { try { window.__nbAcctOff(); } catch (e) {} }
      document.addEventListener('click', acClick, true);
      document.addEventListener('input', acInput, true);
      // Enter in a field of the form presses its first button
      var acKeyH = function(ev){
        var i = ev.target;
        if (ev.key !== 'Enter' || !i || !i.closest || !i.closest('.nbacct') || i.tagName !== 'INPUT') return;
        var b = i.closest('.nbacct').querySelector('.nbacct-btn[data-do="in"], .nbacct-btn[data-do="create"], .nbacct-btn[data-do="code"]');
        if (b) { ev.preventDefault(); ev.stopPropagation(); b.click(); }
      };
      document.addEventListener('keydown', acKeyH, true);
      window.__nbAcctOff = function(){
        document.removeEventListener('click', acClick, true);
        document.removeEventListener('keydown', acKeyH, true);
        document.removeEventListener('input', acInput, true);
      };
      // logged in: the favourites hold in every notebook opened (once per page)
      try { acApplyFav(); } catch (e) {}
