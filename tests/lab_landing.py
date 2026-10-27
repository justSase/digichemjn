"""Real-JupyterLab measurement for STRUKTUR §4b/§4c — Eilauftrag 2, 2026-09-27f.

NOT a suite: it needs a running `jupyter lab` (see lab_keys.py). Real mouse,
getBoundingClientRect / class reads only. The LINE is the reading line: top of
the rail's window + railY0 (where the cursor stands).

  M  MARKER — over 21 scroll positions the middle of the marker that lights
     the marks up (.nbmap-here) is on the line (<= 2 px), and the lit mark
     (.here) is the last drawn mark whose middle has reached the line (+2 px);
     a mark within 3 px of the line may go either way (E10 Teil 4, 01.10.:
     BEHAUPTETE BISHER 2 px in floating point — 17-marker lights by
     offsetTop <= Math.round(line) + 2, both WHOLE pixels, so a mark 2.015 px
     below the line was lit and the script said no; 2 px + 1 px rounding).
  O  ONSET — each chapter mark: with its middle 3 px below the line it is not
     lit; on the line and 3 px above it, it is (the ±2 px of the criterion).
  L  LANDING — a click on a mark (chapter, exercise, coding, figure, end)
     brings that mark's middle onto the line (<= 2 px), it is the lit one, and
     the marker is on the line.
  T  TOGGLE — click / click / click on chapter 1: open / folded / open; the
     first and third land on the line.
  E  ENDS (E12.2, 01.10.) — no air: at scrollTop 0 the lit mark is the title
     and its middle is on the line, at the bottom the lit mark is "Your own
     cell" and its middle is on the line (<= 2 px). Until v1.45 the script
     only knew E9.2's air, where st 0 lit nothing (`lit []` was right then).

    python3 tests/lab_landing.py <notebook> <out.json> [skin,...] [pct,...]
Exit 1 if a criterion fails."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import fresh, CHROME
from playwright.sync_api import sync_playwright
BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
ROOT = os.environ.get("DIGICHEM_LAB_ROOT", "/home/claude/lab/root")
nb, out = sys.argv[1], sys.argv[2]
skins = sys.argv[3].split(",") if len(sys.argv) > 3 and sys.argv[3] else [None]
pcts = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else [100, 0]
SC = "document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer')"
LIB = r"""
window.__ld = {
  MK: '.nbsect,.nbsubdot,.nbchapdot,.nbvizmark,.nbrail-dot,.nbcodemark,.nbendmark,.nbcellmark',
  sc: function(){ return %s; },
  nodes: function(){ return [].slice.call(document.querySelectorAll('#nbpanel-root .nbmap-node')); },
  mid: function(e){ if (!e) return null; var r = e.getBoundingClientRect(); return r.height > 0 ? r.top + r.height/2 : null; },
  mk: function(n){ return n ? this.mid(n.querySelector(this.MK)) : null; },
  line: function(){ var h = document.getElementById('nbpanel-root'), map = h.querySelector('.nbmap');
    return map.getBoundingClientRect().top + (parseInt(h.dataset.railY0 || '0', 10) || 0); },
  kind: function(n){ var c = n.classList; return c.contains('chap') ? 'chap' : c.contains('codetask') ? 'code'
    : c.contains('task') ? 'task' : c.contains('title') ? 'title' : c.contains('end') ? 'end'
    : c.contains('cell') ? 'cell' : c.contains('sect') ? 'sect' : n.querySelector('.nbvizmark') ? 'viz' : 'sub'; },
  state: function(){ var self = this, L = this.line(), ns = this.nodes(), vis = [], lit = [];
    ns.forEach(function(n, i){ if (n.classList.contains('nbgone')) { if (n.classList.contains('here')) lit.push(i); return; }
      var y = self.mk(n); if (y !== null) vis.push([i, y]); if (n.classList.contains('here')) lit.push(i); });
    var exp = -1, ey = -1e9, amb = [];
    vis.forEach(function(v){ if (v[1] <= L + 2 && v[1] >= ey) { ey = v[1]; exp = v[0]; }
                             if (Math.abs(v[1] - L) <= 3) amb.push(v[0]); });   // 2 px + 1 px whole-pixel rounding (17-marker: offsetTop, Math.round)
    var m = document.querySelector('#nbpanel-root .nbmap-here');
    return {line: L, st: this.sc().scrollTop, marker: this.mid(m), lit: lit, expect: exp, amb: amb}; },
  acc: function(id){ var s = document.getElementById(id); if (!s) return null;
    var host = s; while (host.parentElement && !(host.parentElement.classList.contains('widget-vbox') ||
           host.parentElement.classList.contains('jupyter-widget-vbox'))) host = host.parentElement;
    var sib = host.nextElementSibling, k = 0;
    while (sib && k++ < 8){ var c = sib.classList.contains('jupyter-widget-Collapse') ? sib
             : sib.querySelector('.jupyter-widget-Collapse'); if (c) return c; sib = sib.nextElementSibling; }
    return null; },
  // a group bar's anchor stands before the group's own accordion (.acc-group)
  grp: function(id){ var s = document.getElementById(id), host = s, hops = 0;
    while (host && host !== document.body && hops++ < 8){ var sib = host.nextElementSibling, k = 0;
      while (sib && k++ < 6){ var g = sib.classList.contains('acc-group') ? sib : sib.querySelector('.acc-group');
        if (g) return g.classList.contains('jupyter-widget-Collapse') ? g : g.querySelector('.jupyter-widget-Collapse');
        sib = sib.nextElementSibling; }
      host = host.parentElement; }
    return null; },
  open: function(id){ var c = /^grp_/.test(id || '') ? this.grp(id) : this.acc(id);
    return c ? c.classList.contains('jupyter-widget-Collapse-open') : null; },
  // K2.9 — does the mark SHOW that it is lit: its computed ring/fill/edge
  // with `.here` differ from the same mark without it (read, then put back)
  glow: function(i){ var n = this.nodes()[i], m = n && n.querySelector(this.MK); if (!m) return null;
    var had = n.classList.contains('here'), k = ['boxShadow','backgroundColor','borderTopColor','filter','outlineStyle'];
    var rd = function(){ var c = getComputedStyle(m); return k.map(function(x){ return c[x]; }).join('|'); };
    n.classList.add('here'); var on = rd(); n.classList.remove('here'); var off = rd();
    if (had) n.classList.add('here');
    return on !== off; }
};
""" % SC
res = {}; fails = []

def st(pg): return pg.evaluate("()=>window.__ld.state()")

def bring(pg, i):
    """scroll the document so mark i is in the middle of the rail's window"""
    for _ in range(3):
        y = pg.evaluate("(i)=>window.__ld.mk(window.__ld.nodes()[i])", i)
        vh = pg.evaluate("()=>window.innerHeight")
        # "in view" = a click there reaches the mark; under the toolbar
        # (y < ~150) it hits the dock — a fixed 120 px bound let that through
        hit = y is not None and pg.evaluate("(i)=>{var n=window.__ld.nodes()[i], m=n.querySelector(window.__ld.MK), r=m.getBoundingClientRect(), e=document.elementFromPoint(r.left+r.width/2, r.top+r.height/2); return !!(e && e.closest('.nbmap-node')===n);}", i)
        if hit and 120 < y < vh - 80: return y
        if y is None: return None
        pg.evaluate("(d)=>{window.__ld.sc().scrollTop += d;}", y - vh / 2); pg.wait_for_timeout(900)
    return pg.evaluate("(i)=>window.__ld.mk(window.__ld.nodes()[i])", i)

def click(pg, i):
    if bring(pg, i) is None: return None
    xy = pg.evaluate("(i)=>{var n=window.__ld.nodes()[i], m=n.querySelector(window.__ld.MK), r=m.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];}", i)
    pg.mouse.click(xy[0], xy[1]); pg.wait_for_timeout(2400)
    s = st(pg); s["mk"] = pg.evaluate("(i)=>window.__ld.mk(window.__ld.nodes()[i])", i)
    s["off"] = None if s["mk"] is None else round(s["mk"] - s["line"], 1)
    return s

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    ctx, errs = None, []
    for sk in skins:
      for pct in pcts:
        # a fresh copy for every case: a chapter chosen or opened in one case
        # would fold on the first click of the next (the toggle)
        ctx, pg, e1 = fresh(b, BASE, nb, ROOT, ctx)
        # window height from DIGICHEM_H (default 900), as lab_readline
        pg.set_viewport_size({"width": 1400, "height": int(os.environ.get("DIGICHEM_H", "900"))})
        pg.wait_for_timeout(1500)
        try: pg.click(".jp-toast-buttonBar button:has-text('No')", timeout=1500)
        except Exception: pass
        pg.add_script_tag(content=LIB)
        if sk:
            pg.evaluate("(s)=>{ window.__nbStore.set('digichemjn.skin.v1', s); window.__nbApplySkin && window.__nbApplySkin(); }", sk)
            pg.wait_for_timeout(1500)
        if True:
            key = "%s/%d" % (sk, pct)
            pg.evaluate("(p)=>window.__nbSetGui(p)", pct); pg.wait_for_timeout(1500)
            pg.evaluate("()=>{window.__ld.sc().scrollTop=0;}"); pg.wait_for_timeout(1200)
            # ---- M: 21 positions ------------------------------------------
            mx = pg.evaluate("()=>{var s=window.__ld.sc(); return s.scrollHeight-s.clientHeight;}")
            M = []
            for k in range(21):
                pg.evaluate("(y)=>{window.__ld.sc().scrollTop=y;}", round(mx * k / 20)); pg.wait_for_timeout(700)
                M.append(st(pg))
            res[key + "/M"] = M
            for s in M:
                if s["marker"] is None or abs(s["marker"] - s["line"]) > 2:
                    fails.append("%s M st %d: marker %s, line %.1f" % (key, s["st"], s["marker"], s["line"])); break
            for s in M:
                ok = (s["lit"] == [s["expect"]]) or (len(s["lit"]) == 1 and s["lit"][0] in s["amb"])
                if not ok:
                    fails.append("%s M st %d: lit %s, last mark on the line is %s" % (key, s["st"], s["lit"], s["expect"])); break
            # ---- E: the two ends (E12.2) -----------------------------------
            ends = {}
            for tag, kd, k in (("top", "title", 0), ("bottom", "cell", 20)):
                s0 = M[k]
                ti = pg.evaluate("(kd)=>window.__ld.nodes().findIndex(function(n){return window.__ld.kind(n)===kd && !n.classList.contains('nbgone');})", kd)
                pg.evaluate("(y)=>{window.__ld.sc().scrollTop=y;}", s0["st"]); pg.wait_for_timeout(700)
                s1 = st(pg); y = pg.evaluate("(i)=>window.__ld.mk(window.__ld.nodes()[i])", ti) if ti >= 0 else None
                ends[tag] = {"i": ti, "st": s1["st"], "lit": s1["lit"], "off": None if y is None else round(y - s1["line"], 1)}
                if ti < 0: fails.append("%s E %s: no %s mark" % (key, tag, kd)); continue
                if s1["lit"] != [ti]: fails.append("%s E %s: lit %s, want the %s mark %d" % (key, tag, s1["lit"], kd, ti))
                if ends[tag]["off"] is None or abs(ends[tag]["off"]) > 2:
                    fails.append("%s E %s: %s mark %s px from the line (air?)" % (key, tag, kd, ends[tag]["off"]))
            if ends.get("top", {}).get("st") != 0: fails.append("%s E top: scrollTop %s" % (key, ends.get("top", {}).get("st")))
            res[key + "/E"] = ends
            # ---- O: onset — every chapter mark, and (K2.9, 28b) the first
            # visible mark of every other kind: figure, exercise, coding,
            # group, title, end, your own cell ------------------------------
            chs = pg.evaluate("()=>window.__ld.nodes().map(function(n,i){return window.__ld.kind(n)==='chap' && !n.classList.contains('nbgone') ? i : -1;}).filter(function(i){return i>=0;})")
            oth = pg.evaluate("()=>{var o={}; window.__ld.nodes().forEach(function(n,i){var k=window.__ld.kind(n); if(k==='chap'||n.classList.contains('nbgone')||k in o) return; o[k]=i;}); return o;}")
            O = []
            for i in chs + sorted(oth.values()):
                row = {"i": i, "kind": pg.evaluate("(i)=>window.__ld.kind(window.__ld.nodes()[i])", i)}
                for dd in (3, 0, -3):
                    for _ in range(4):
                        y = pg.evaluate("(i)=>window.__ld.mk(window.__ld.nodes()[i])", i); L = pg.evaluate("()=>window.__ld.line()")
                        if y is None: break
                        d = (y - L) - dd
                        if abs(d) < 0.6: break
                        pg.evaluate("(d)=>{window.__ld.sc().scrollTop += d;}", d); pg.wait_for_timeout(700)
                    s = st(pg); y = pg.evaluate("(i)=>window.__ld.mk(window.__ld.nodes()[i])", i)
                    row[str(dd)] = {"off": None if y is None else round(y - s["line"], 1), "lit": i in s["lit"],
                                    "glow": pg.evaluate("(i)=>window.__ld.glow(i)", i)}
                O.append(row)
                for dd, want in (("3", False), ("0", True), ("-3", True)):
                    r = row.get(dd)
                    if not r or r["off"] is None: continue
                    if want and r["off"] <= 0.5 and not r["lit"]:
                        fails.append("%s O %s %d not lit %.1f px from the line" % (key, row["kind"], i, r["off"]))
                    if want and r["lit"] and not r["glow"]:
                        fails.append("%s O %s %d lit, but the mark shows nothing of it" % (key, row["kind"], i))
                    if not want and r["off"] > 2 and r["lit"]:
                        fails.append("%s O %s %d lit %.1f px BEFORE reaching the line" % (key, row["kind"], i, r["off"]))
            res[key + "/O"] = O
            # ---- L: landing, one click per mark kind ---------------------
            pg.evaluate("()=>{window.__ld.sc().scrollTop=0;}"); pg.wait_for_timeout(1200)
            kinds = pg.evaluate("()=>window.__ld.nodes().map(function(n,i){return [i, window.__ld.kind(n), n.classList.contains('locked'), n.classList.contains('nbgone')];})")
            pick, seen = [], {}
            for i, kd, locked, gone in kinds:
                if gone or kd in ("title", "cell", "sect", "sub"): continue
                if locked: kd = kd + "-locked"
                if seen.get(kd, 0) >= (3 if kd in ("chap", "task", "code") else 1): continue
                seen[kd] = seen.get(kd, 0) + 1; pick.append((i, kd))
            L = []
            for i, kd in pick:
                s = click(pg, i)
                if s is None: continue
                s["i"] = i; s["kind"] = kd; L.append(s)
                if s["off"] is None or abs(s["off"]) > 2:
                    fails.append("%s L %s %d: mark %s px from the line after the click" % (key, kd, i, s["off"]))
                elif i not in s["lit"]:
                    fails.append("%s L %s %d: landed but lit is %s" % (key, kd, i, s["lit"]))
                if s["marker"] is None or abs(s["marker"] - s["line"]) > 2:
                    fails.append("%s L %s %d: marker %s, line %.1f" % (key, kd, i, s["marker"], s["line"]))
                pg.keyboard.press("Escape")
            res[key + "/L"] = L
            # ---- T: toggle — click / click / click = open / folded / open,
            # chosen / not / chosen, the mark on the line each time. Chapter 1
            # (27f/27g) and, since K2.10 (28b), every mark that has something
            # to fold: figure, exercise, coding (chapter 1's), a group (the
            # Appendix), a section in it, and the quiz's exercise mark.
            TK = {}
            def toggle3(i, tag):
                tid = pg.evaluate("(i)=>window.__ld.nodes()[i].getAttribute('data-target')", i)
                click(pg, 0)                       # start from another mark: the title
                T = []
                for k in range(3):
                    s = click(pg, i)
                    if s is None: T.append({"off": None, "open": None, "sel": None}); continue
                    s["open"] = pg.evaluate("(i)=>window.__ld.open(i)", tid)
                    s["sel"] = pg.evaluate("(i)=>window.__ld.nodes()[i].classList.contains('nbsel')", i); T.append(s)
                TK[tag] = T
                if [t["open"] for t in T] != [True, False, True]:
                    fails.append("%s T %s: open after clicks 1/2/3 = %s" % (key, tag, [t["open"] for t in T]))
                for k in (0, 1, 2):
                    if T[k]["off"] is None or abs(T[k]["off"]) > 2:
                        fails.append("%s T %s click %d: mark %s px from the line" % (key, tag, k + 1, T[k]["off"]))
                if [t["sel"] for t in T] != [True, False, True]:
                    fails.append("%s T %s: chosen after clicks 1/2/3 = %s" % (key, tag, [t["sel"] for t in T]))
            def first(js):
                return pg.evaluate("()=>{var n=window.__ld.nodes(); for(var i=0;i<n.length;i++){var x=n[i]; if(x.classList.contains('nbgone')) continue; if(" + js + ") return i;} return null;}")
            c1 = chs[0] if chs else None
            if c1 is not None: toggle3(c1, "chap")
            for tag, js in (("viz", "window.__ld.kind(x)==='viz'"),
                            ("task", "window.__ld.kind(x)==='task'"),
                            ("code", "window.__ld.kind(x)==='code'")):
                # chapter 1 open again, so its figure, exercise and coding are drawn
                i = first(js)
                if i is None: fails.append("%s T %s: no such mark on the rail" % (key, tag)); continue
                toggle3(i, tag)
            ga = first("window.__ld.kind(x)==='sect' && /Appendix/.test(x.textContent)")
            if ga is None: fails.append("%s T group: no Appendix mark" % key)
            else:
                toggle3(ga, "group")
                # E25.l: no quiz mark any more (behauptete bisher: the quiz's mark toggles)
                for tag, js in (("sub", "window.__ld.kind(x)==='sub'"),):
                    i = first(js)
                    if i is None: fails.append("%s T %s: no such mark on the rail" % (key, tag)); continue
                    toggle3(i, tag)
            res[key + "/T"] = TK
            # ---- K: the other kinds — title, group, your own cell ------------
            K = []
            kk = pg.evaluate("()=>{var n=window.__ld.nodes(), o={}; n.forEach(function(x,i){var k=window.__ld.kind(x); if(x.classList.contains('nbgone')) return; if((k==='title'||k==='sect'||k==='cell') && !(k in o)) o[k]=i; if(k==='sect') o.sectLast=i;}); return o;}")
            for kd in ("sect", "sectLast", "cell", "title"):
                i = kk.get(kd)
                if i is None: continue
                s = click(pg, i)
                if s is None: continue
                s["i"] = i; s["kind"] = kd; K.append(s)
                if s["off"] is None or abs(s["off"]) > 2:
                    fails.append("%s K %s %d: mark %s px from the line after the click" % (key, kd, i, s["off"]))
            res[key + "/K"] = K
        errs += e1
    res["errs"] = errs
    if errs: fails.append("console: %s" % errs[:3])
    ctx.close(); b.close()

res["fails"] = fails
json.dump(res, open(out, "w"), indent=1)
for k, v in res.items():
    if k.endswith("/M"):
        print("%-14s marker-line %s | lit==expected %d/%d" % (k, "%.1f..%.1f" % (min(s["marker"] - s["line"] for s in v if s["marker"] is not None), max(s["marker"] - s["line"] for s in v if s["marker"] is not None)) if any(s["marker"] is not None for s in v) else "none",
              sum(1 for s in v if s["lit"] == [s["expect"]] or (len(s["lit"]) == 1 and s["lit"][0] in s["amb"])), len(v)))
    if k.endswith("/O"):
        print("%-14s onset lit at +3/0/-3 px: %d/%d/%d of %d, glowing on the line %d (kinds %s; offsets hit %s)" % (k, *[sum(1 for r in v if r.get(d, {}).get("lit")) for d in ("3", "0", "-3")], len(v),
              sum(1 for r in v if r.get("0", {}).get("glow")), ",".join(sorted(set(r["kind"] for r in v))),
              sorted(set(r.get(d, {}).get("off") for r in v for d in ("3", "0", "-3")))))
    if k.endswith("/L"):
        print("%-14s landing offsets: %s" % (k, ", ".join("%s %s" % (s["kind"], s["off"]) for s in v)))
    if k.endswith("/T"):
        for tag, T in v.items():
            print("%-14s toggle %-5s open %s, chosen %s, offsets %s" % (k, tag, [t["open"] for t in T], [t.get("sel") for t in T], [t["off"] for t in T]))
    if k.endswith("/E"):
        print("%-14s ends: %s" % (k, ", ".join("%s st %s lit %s off %s" % (t, e["st"], e["lit"], e["off"]) for t, e in v.items())))
    if k.endswith("/K"):
        print("%-14s other kinds: %s" % (k, ", ".join("%s %s" % (s["kind"], s["off"]) for s in v)))
for f in fails: print("FAIL", f)
print("LANDING OK" if not fails else "LANDING: %d failures" % len(fails))
sys.exit(1 if fails else 0)
