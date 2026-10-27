"""Real-JupyterLab measurement for the K3 corrections (OBERFLAECHE, 2026-09-28c).

NOT a suite: it needs a running `jupyter lab` (see lab_keys.py). One fresh copy
of the notebook per skin, progress set through the kernel (t1 and coding 1
solved, t2 skipped, t3 wrong: the lane carries all four fills, chapters 4–7
are locked and coding 3 waits for coding 2). Reads getComputedStyle /
getBoundingClientRect only; every contrast is WCAG over what is painted.

  N  K3.1  names in two lines (Variante a, 28c size), pips 12 × 12 (× --nbk):
           names cut at 100 / 75 / 60 % counted (0 at 100 %), no name, pip
           strip or mark over another node's, names on the column middle
           (<= 2 px), pips under their own name — at the top and the end of
           the document; markFloor reported.
  X  K3.2  every lane fill (done, skip, fail, code) against the marker's band
           (fill and edge) >= 3 : 1; every fill against the panel face (its
           colour at its share over the page) >= 1.5 : 1 — and, reported only,
           against the face over the worst ground the document paints.
  G  K3.3  pull tab = panel: same background, same backdrop filter, its edge
           colour = the panel's left border, no own shadow, gap 0 px — panel
           shut (0 %) and open (100 %).
  L  K3.4  every locked chapter pill and every waiting exercise fold: a drawn
           padlock (shackle + body) and "Locked", the name at 600, name,
           "Locked" and padlock >= 4.5 : 1 on the pill; a waiting fold shows
           not-allowed. Open chapter pills: fingerprint printed, compared
           against the previous build by the caller.
  T  K3.5  the lens 100 → 150 % (mouse on its thumb, double click = 100,
           seven ArrowRight = 150): the lens reads ≥ 145 (per-notebook key,
           E15.7) and the texture's tile stays (E8.2, ± 5 %).
  H  K3.6  a `.sol-btn.nbhint-btn` put next to Exercise 1's solution button
           (the real one arrives with A): its ink differs from the solution
           button's and reads >= 4.5 : 1 on the ground under it; marks in the
           dark >= 3 : 1 over the worst ground (lab_contrast's MARKS_JS).
  M        the marker's middle on the reading line (<= 2 px) at 12 scroll
           positions. (Until the 28b-based K3 build this part asserted K3.8
           "no tail" — the user replaced it; the trail is lab_k4's.)
  S  K3.4  "Skip for now" reads as a button: weight of the Check button,
           edge >= 3 : 1 on the ground, label >= 4.5 : 1, pointer, >= 32 px.

    python3 tests/lab_k3.py <notebook> <out.json> [skin,...] [--shots DIR]
Exit 1 if a criterion fails."""
import sys, json, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import fresh, CHROME
from lab_marks import kexec
from lab_contrast import GROUNDS_JS, MARKS_JS
from playwright.sync_api import sync_playwright
BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
ROOT = os.environ.get("DIGICHEM_LAB_ROOT", "/home/claude/lab/root")
args = [a for a in sys.argv[1:] if not a.startswith("--")]
nb, out = args[0], args[1]
skins = args[2].split(",") if len(args) > 2 and args[2] else ["minimal", "cyber", "fairy"]
SHOTS = sys.argv[sys.argv.index("--shots") + 1] if "--shots" in sys.argv else None
if SHOTS: os.makedirs(SHOTS, exist_ok=True)
SET = """([s,t]) => { window.__nbStore.set('digichemjn.skin.v1', s); window.__nbStore.set('digichemjn.theme.v1', t);
  window.__nbApplySkin(); window.__nbApplyTheme(); }"""
LIB = r"""
window.__k3 = {
  sc: function(){ return document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer'); },
  host: function(){ return document.getElementById('nbpanel-root'); },
  rgba: function(s){ if (!s) return null; var k = s.match(/color\(srgb ([^)]+)\)/); if (k) { var q = k[1].split(/[ \/]+/).filter(Boolean).map(parseFloat); return [q[0]*255, q[1]*255, q[2]*255, q.length > 3 ? q[3] : 1]; }
    var m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null; var p = m[1].split(/[ ,\/]+/).filter(Boolean).map(parseFloat); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; },
  over: function(f, b){ var a = f[3]; return [f[0]*a + b[0]*(1-a), f[1]*a + b[1]*(1-a), f[2]*a + b[2]*(1-a), 1]; },
  L: function(c){ var l = function(v){ v /= 255; return v <= .04045 ? v / 12.92 : Math.pow((v + .055) / 1.055, 2.4); }; return .2126*l(c[0]) + .7152*l(c[1]) + .0722*l(c[2]); },
  cr: function(a, b){ var x = this.L(a), y = this.L(b); return Math.round((Math.max(x, y) + .05) / (Math.min(x, y) + .05) * 100) / 100; },
  hex: function(c){ return c ? '#' + c.slice(0,3).map(function(v){ return ('0' + Math.round(v).toString(16)).slice(-2); }).join('') : null; },
  // the first opaque ground under an element in the document (ancestor walk; the document is not on the panel)
  ground: function(e){ var acc = null; for (var a = e; a; a = a.parentElement) { var c = this.rgba(getComputedStyle(a).backgroundColor);
      if (c && c[3] > 0) { acc = acc ? this.over(acc, c) : c; if (acc[3] >= 1 || c[3] >= 1) { if (acc[3] < 1) acc = this.over(acc, [255,255,255,1]); return acc; } } }
    return acc ? this.over(acc, [255,255,255,1]) : [255,255,255,1]; },
  vis: function(e){ if (!e) return false; var r = e.getBoundingClientRect(), c = getComputedStyle(e);
    return r.width > 0 && r.height > 0 && c.visibility === 'visible' && c.display !== 'none' && +c.opacity > 0; }
};
"""

NAMES_JS = r"""() => { var h=document.getElementById('nbpanel-root'), rail=h.querySelector('.nbrail'), rr=rail.getBoundingClientRect();
  var labx=parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nbvert-labx'))||0;
  var labw=parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nbvert-lab'))||0;
  var names=[], items=[], pip=null;
  h.querySelectorAll('.nbmap-node').forEach(function(n,i){
    if(n.classList.contains('nbgone')) return;
    n.querySelectorAll('.nbmap-lab,.nbtasklab').forEach(function(l){
      var cs=getComputedStyle(l); if(cs.display==='none'||cs.visibility==='hidden'||l.offsetWidth===0) return;
      var r=l.getBoundingClientRect();
      var cut=(l.scrollHeight>l.clientHeight+1)||(l.scrollWidth>l.clientWidth+1);
      names.push({i:i,t:l.textContent,cut:cut,h:Math.round(r.height*10)/10,fs:parseFloat(cs.fontSize),
        mid:Math.round((r.left+r.width/2-(rr.left+1+labx+labw/2))*10)/10});
      items.push({i:i,k:'lab',bb:[r.left,r.top,r.width,r.height]}); });
    var cs2=n.querySelector('.nbchapstat'); if(cs2&&cs2.offsetWidth>0){
      var ps2=cs2.querySelectorAll('.ps'); if(ps2.length){ if(pip===null) pip=ps2[0].offsetWidth; var a=ps2[0].getBoundingClientRect(), b=ps2[ps2.length-1].getBoundingClientRect();
        items.push({i:i,k:'pips',bb:[a.left,Math.min(a.top,b.top),b.right-a.left,Math.max(a.bottom,b.bottom)-Math.min(a.top,b.top)]}); } }
    var m=n.querySelector('.nbsect,.nbsubdot,.nbchapdot,.nbvizmark,.nbrail-dot,.nbcodemark,.nbendmark,.nbcellmark');
    if(m&&m.offsetWidth>0){ var r2=m.getBoundingClientRect(); items.push({i:i,k:'mark',bb:[r2.left,r2.top,r2.width,r2.height]}); } });
  var ov=[];
  for(var a=0;a<items.length;a++) for(var b=a+1;b<items.length;b++){ if(items[a].i===items[b].i) continue;
    var A=items[a].bb,B=items[b].bb;
    if(A[0]<B[0]+B[2]-0.5&&B[0]<A[0]+A[2]-0.5&&A[1]<B[1]+B[3]-0.5&&B[1]<A[1]+A[3]-0.5) ov.push([items[a].i+items[a].k,items[b].i+items[b].k]); }
  var own=[]; h.querySelectorAll('.nbmap-node.chap').forEach(function(n){ var l=n.querySelector('.nbmap-lab'), c=n.querySelector('.nbchapstat .ps');
    if(!l||!c||l.offsetWidth===0||c.offsetWidth===0) return; var a=l.getBoundingClientRect(), b=c.getBoundingClientRect();
    own.push(Math.round((b.top-a.bottom)*10)/10); });
  var FL=window.__nbMarkFloor?window.__nbMarkFloor(h):null;
  return {k:window.__nbK||1, W:rr.width, names_on:h.classList.contains('nbnames'), pip:pip, names:names, overlaps:ov, pipGap:own,
          floor:FL?{t:Math.round(FL.t*1000)/1000,w:FL.w,min:FL.min}:null};
}"""

def lens(pg, to):
    """The lens in the notebook's toolbar, by hand: double click on its thumb = 100 %,
    then ArrowRight (one step 7 %) for 150."""
    THJ = "()=>{var s=document.querySelector('#nbpanel-root .nbz-doc .nbslider'); var r=s.getBoundingClientRect(); var v=+s.value, mx=+(s.max||100); return [r.left+8+(r.width-16)*v/mx, r.top+r.height/2];}"
    th = pg.evaluate(THJ); pg.mouse.dblclick(th[0], th[1]); pg.wait_for_timeout(1800)
    if to == 150:
        for _ in range(7):
            pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(80)
        pg.wait_for_timeout(2200)
    try: return int(pg.evaluate("()=>localStorage.getItem(window.__nbZKey ? window.__nbZKey() : 'digichemjn.zoom.v1')") or 0)
    except Exception: return None

res = {}; fails = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    ctx = None
    for sk in skins:
        ctx, pg, errs = fresh(b, BASE, nb, ROOT, ctx)
        pg.set_viewport_size({"width": 1400, "height": 900}); pg.wait_for_timeout(1500)
        try: pg.click(".jp-toast-buttonBar button:has-text('No')", timeout=1500)
        except Exception: pass
        pg.add_script_tag(content=LIB)
        kexec("task_solved('t1'); task_code_solved('t1'); task_skipped('t2'); task_wrong('t3')")
        pg.wait_for_timeout(3500)
        for th in ("light", "dark"):
            key = "%s/%s" % (sk, th); R = res[key] = {}
            pg.evaluate(SET, [sk, th]); pg.wait_for_timeout(1500)
            pg.evaluate("()=>window.__nbSetGui(100)"); pg.wait_for_timeout(1800)
            # ---- X: the fills against the marker and the panel ------------
            grounds = pg.evaluate(GROUNDS_JS)
            X = pg.evaluate("""(grounds)=>{var K=window.__k3, h=K.host(), rail=h.querySelector('.nbrail');
                var face=K.rgba(getComputedStyle(rail,'::before').backgroundColor);
                var under=grounds.map(function(g){return face?K.over(face,g):g;});
                var mk=h.querySelector('.nbmap-here'), mb=getComputedStyle(mk,'::before');
                var band=K.rgba(mb.backgroundColor), edge=K.rgba(mb.borderTopColor);
                var o={band:K.hex(band), edge:K.hex(edge), fills:{}};
                ['done','skip','fail','code'].forEach(function(s){ var e=h.querySelector('.nbseg[data-s="'+s+'"]'); if(!e){o.fills[s]=null;return;}
                  var c=getComputedStyle(e), f=K.rgba(c.backgroundColor); var wp=1e9;
                  under.forEach(function(g){ var v=K.cr(f[3]<1?K.over(f,g):f,g); if(v<wp) wp=v; });
                  // the panel face as OBERFLAECHE §4a defines it: its colour at its share over the PAGE
                  // (under[0]); the worst document ground under it is reported beside it
                  o.fills[s]={fill:K.hex(f), alpha:f[3], vsBand:K.cr(f,band), vsEdge:K.cr(f,edge), vsPanel:K.cr(f,under[0]),
                              vsPanelWorst:Math.round(wp*100)/100,
                              shadow:c.boxShadow}; });
                return o;}""", grounds)
            R["X"] = X
            for s, f in X["fills"].items():
                if f is None: fails.append("%s X: no %s segment on the lane" % (key, s)); continue
                if min(f["vsBand"], f["vsEdge"]) < 3: fails.append("%s X %s: marker on fill %.2f / edge %.2f < 3" % (key, s, f["vsBand"], f["vsEdge"]))
                if f["vsPanel"] < 1.5: fails.append("%s X %s: fill on panel %.2f < 1.5" % (key, s, f["vsPanel"]))
            # ---- M: the marker on the line (the trail is lab_k4's) -------
            # 2026-09-28d — UNTIL the K3 build of 28b this part asserted "no
            # tail" (K3.8). The user replaced that with the trail BEHIND the
            # movement (28c, lab_k4 part T); here only: the marker still stands
            # on the reading line with the K3 band colour.
            M = []
            for y in (300, 900, 1500, 2100, 2700, 3300, 3900, 4500, 5100, 5700, 6300, 6900):
                pg.evaluate("(y)=>{window.__k3.sc().scrollTop=y;}", y); pg.wait_for_timeout(500)
                M.append(pg.evaluate("""()=>{var h=window.__k3.host(),mk=h.querySelector('.nbmap-here'),map=h.querySelector('.nbmap');
                    var r=mk.getBoundingClientRect(), line=map.getBoundingClientRect().top+(parseInt(h.dataset.railY0||'0',10)||0);
                    return {d:Math.round((r.top+r.height/2-line)*10)/10, on:mk.classList.contains('on')};}"""))
            R["M"] = M
            if any(abs(m["d"]) > 2 for m in M):
                fails.append("%s M: marker off the line %r" % (key, [m["d"] for m in M]))
            # ---- N: names (two lines, Variante a), pips, overlap -----------
            # 2026-09-28d — STOP.md, Namensspalte: how many of the names are cut
            # at 100, 75 and 60 % (0 at 100 %); names, pips and marks never
            # overlap the next node; names centred between cursor and lane
            # (<= 2 px); pips 12 px (× --nbk). At the top AND at the end of the
            # document (footAlign moves the last marks there, 28c).
            R["N"] = {}
            for pct in (100, 75, 60):
                pg.evaluate("(p)=>window.__nbSetGui(p)", pct); pg.wait_for_timeout(1800)
                for where in ("top", "end"):
                    if where == "top":
                        pg.evaluate("()=>{var s=window.__k3.sc(); s.scrollTop=0; s.dispatchEvent(new Event('scroll'));}")
                    else:
                        pg.evaluate("()=>{var s=window.__k3.sc(); s.scrollTop=s.scrollHeight; s.dispatchEvent(new Event('scroll'));}")
                    pg.wait_for_timeout(1300)
                    n = pg.evaluate(NAMES_JS)
                    kk = "%d/%s" % (pct, where); R["N"][kk] = n
                    cut = [x["t"] for x in n["names"] if x["cut"]]
                    n["ncut"] = len(cut); n["cut"] = cut
                    if pct == 100 and cut: fails.append("%s N %s: %d names cut %r" % (key, kk, len(cut), cut[:3]))
                    if n["overlaps"]: fails.append("%s N %s: %d overlaps %r" % (key, kk, len(n["overlaps"]), n["overlaps"][:3]))
                    off = [x for x in n["names"] if abs(x["mid"]) > 2]
                    if off: fails.append("%s N %s: %d names off the column middle %r" % (key, kk, len(off), [(x["t"][:20], x["mid"]) for x in off[:3]]))
                    if any(g < 0 for g in n["pipGap"]): fails.append("%s N %s: pips under their own name %r" % (key, kk, n["pipGap"]))
                    want = 12 * (n["k"] or 1)
                    if n["names_on"] and (n["pip"] is None or abs(n["pip"] - want) > .6):
                        fails.append("%s N %s: pip %r, want %.1f" % (key, kk, n["pip"], want))
            pg.evaluate("()=>window.__nbSetGui(100)"); pg.wait_for_timeout(1500)
            # ---- G: the pull tab ------------------------------------------
            R["G"] = {}
            for pct in (0, 100):
                pg.evaluate("(p)=>window.__nbSetGui(p)", pct); pg.wait_for_timeout(1800)
                g = pg.evaluate("""()=>{var h=window.__k3.host(), rail=h.querySelector('.nbrail'), gr=h.querySelector('.nbgrip');
                    var rb=getComputedStyle(rail,'::before'), rc=getComputedStyle(rail), gc=getComputedStyle(gr);
                    var a=gr.getBoundingClientRect(), r=rail.getBoundingClientRect();
                    return {grip:gc.backgroundColor, face:rb.backgroundColor, gripBlur:gc.backdropFilter, faceBlur:rb.backdropFilter,
                            gripEdge:[gc.borderTopColor,gc.borderLeftColor,gc.borderBottomColor], railEdge:rc.borderLeftColor,
                            railEdgeW:rc.borderLeftWidth, shadow:gc.boxShadow, gap:Math.round((r.left-a.right)*10)/10,
                            box:[a.left,a.top,a.width,a.height]};}""")
                R["G"][pct] = g
                if g["grip"] != g["face"] or g["gripBlur"] != g["faceBlur"]:
                    fails.append("%s G %d%%: tab %s/%s, panel %s/%s" % (key, pct, g["grip"], g["gripBlur"], g["face"], g["faceBlur"]))
                if any(c != g["railEdge"] for c in g["gripEdge"]) or g["shadow"] != "none" or abs(g["gap"]) > 0.5:
                    fails.append("%s G %d%%: edge %r vs %s, shadow %s, gap %s" % (key, pct, g["gripEdge"], g["railEdge"], g["shadow"], g["gap"]))
                if SHOTS:
                    bx = g["box"]; x0 = max(0, bx[0] - 40)
                    pg.screenshot(path=os.path.join(SHOTS, "k3_tab_%s_%s_%d.png" % (sk, th, pct)),
                                  clip={"x": x0, "y": max(0, bx[1] - 70), "width": min(260, 1400 - x0), "height": bx[3] + 140})
            pg.evaluate("()=>window.__nbSetGui(100)"); pg.wait_for_timeout(1500)
            if SHOTS:
                pg.evaluate("()=>{window.__k3.sc().scrollTop=1500;}"); pg.wait_for_timeout(1200)
                bx = pg.evaluate("()=>{var r=window.__k3.host().querySelector('.nbrail').getBoundingClientRect();return [r.left,r.top,r.width,r.height];}")
                pg.screenshot(path=os.path.join(SHOTS, "k3_panel_%s_%s.png" % (sk, th)),
                              clip={"x": max(0, bx[0] - 20), "y": 140, "width": 1400 - max(0, bx[0] - 20), "height": 740})
            # ---- L: locked pills and waiting folds ------------------------
            L = pg.evaluate("""()=>{var K=window.__k3, out={locked:[],waiting:[],open:[]};
                var hd=function(a){return a.querySelector(':scope>.jupyter-widget-Collapse>.jupyter-widget-Collapse-header,:scope>.lm-Collapse>.lm-Collapse-header');};
                var read=function(a){ var h=hd(a); if(!h) return null; var i=h.querySelector(':scope>i'), sp=h.querySelector(':scope>span');
                  var hc=getComputedStyle(h), ib=i?getComputedStyle(i,'::before'):null, ia=i?getComputedStyle(i,'::after'):null, ha=getComputedStyle(h,'::after');
                  var g=K.ground(h), ink=K.rgba(sp?getComputedStyle(sp).color:hc.color), lk=i?K.rgba(getComputedStyle(i).color):null, lt=K.rgba(ha.color);
                  return {name:sp?sp.textContent.trim().slice(0,40):null, weight:sp?getComputedStyle(sp).fontWeight:hc.fontWeight,
                    shackle:ib?(ib.content+'|'+ib.borderTopWidth+'|'+ib.borderTopStyle):null, body:ia?(ia.content+'|'+ia.backgroundColor):null,
                    locked:ha.content, cursor:hc.cursor, ground:K.hex(g), crName:K.cr(ink,g), crLock:lk?K.cr(lk,g):null,
                    crWord:ha.content!=='none'?K.cr(lt,g):null, shown:K.vis(h), color:hc.color, icon:ib?ib.content:null}; };
                document.querySelectorAll('.acc-locked').forEach(function(a){ var r=read(a); if(r) out.locked.push(r); });
                document.querySelectorAll('.acc-tasklock').forEach(function(a){ var r=read(a); if(r) out.waiting.push(r); });
                document.querySelectorAll('.acc-chapter:not(.acc-locked):not(.acc-plain)').forEach(function(a){ var r=read(a); if(r) out.open.push(r); });
                return out;}""")
            R["L"] = L
            if not L["locked"]: fails.append("%s L: no locked chapter pill found" % key)
            if not L["waiting"]: fails.append("%s L: no waiting fold found (coding 3 should wait)" % key)
            for kind in ("locked", "waiting"):
                for r in L[kind]:
                    if not r["shown"]: continue
                    ok_lock = r["shackle"] and r["shackle"].startswith('""') and not r["shackle"].endswith("none") and r["body"] and r["body"].startswith('""')
                    if not ok_lock or r["locked"] != '"Locked"':
                        fails.append("%s L %s %r: padlock %r / %r, word %r" % (key, kind, r["name"], r["shackle"], r["body"], r["locked"]))
                    if min(r["crName"], r["crLock"] or 0, r["crWord"] or 0) < 4.5:
                        fails.append("%s L %s %r: contrast name %.2f lock %s word %s" % (key, kind, r["name"], r["crName"], r["crLock"], r["crWord"]))
                    if kind == "waiting" and r["cursor"] != "not-allowed":
                        fails.append("%s L waiting %r: cursor %s" % (key, r["name"], r["cursor"]))
            if SHOTS:
                pg.evaluate("""()=>{var a=document.querySelector('.acc-locked'); var s=window.__k3.sc(); s.scrollTop += a.getBoundingClientRect().top-420;}""")
                pg.wait_for_timeout(1000)
                pg.screenshot(path=os.path.join(SHOTS, "k3_locked_%s_%s.png" % (sk, th)), clip={"x": 290, "y": 300, "width": 520, "height": 260})
            # ---- S: "Skip for now" is a button (K3.4, Befund K1) ----------
            # 2026-09-28d — it wore the skin's button coat but at weight 400,
            # next to its 700-weight siblings, behind a 1-px edge in the skin's
            # faint line (1.4–2 : 1): it read as a caption. Asserted: the weight
            # of the "Check" button next to it, an edge >= 3 : 1 against the
            # ground (WCAG 1.4.11), label >= 4.5 : 1 on its face, pointer, a
            # height a finger can hit (>= 32 px), and the Check button itself
            # unchanged (printed for the caller's comparison).
            # open the first fold that holds one and does not wait (a click on its head, as a reader would)
            pg.evaluate("""()=>{var bs=document.querySelectorAll('button.nbskipnow');
                for (var i=0;i<bs.length;i++){ var c=bs[i].closest('.jupyter-widget-Collapse,.lm-Collapse'); if(!c) continue;
                  var acc=c.parentElement; if(acc&&acc.classList.contains('acc-tasklock')) continue;
                  if(bs[i].getBoundingClientRect().width>0) return;
                  var hd=c.querySelector(':scope>.jupyter-widget-Collapse-header,:scope>.lm-Collapse-header'); if(hd){hd.click(); return;} } }""")
            pg.wait_for_timeout(1500)
            pg.evaluate("""()=>{var b=[].filter.call(document.querySelectorAll('button.nbskipnow'),function(x){return x.getBoundingClientRect().width>0;})[0];
                if(!b) return; var s=window.__k3.sc(); s.scrollTop += b.getBoundingClientRect().top-420;}""")
            pg.wait_for_timeout(900)
            Sx = pg.evaluate("""()=>{var K=window.__k3, out=[];
                document.querySelectorAll('button.nbskipnow').forEach(function(b){ if(!K.vis(b)) return;
                  var c=getComputedStyle(b), g=K.ground(b.parentElement), face=K.rgba(c.backgroundColor);
                  var under=face&&face[3]>0?K.over(face,g):g;
                  var box=b.closest('.jupyter-widget-Collapse-contents, .lm-Collapse-contents, .jp-OutputArea-output');
                  var ref=box?[].filter.call(box.querySelectorAll('button.sc-btn'),K.vis)[0]:null, rc=ref?getComputedStyle(ref):null;
                  out.push({weight:c.fontWeight, refWeight:rc?rc.fontWeight:null, ref:rc?[rc.color,rc.backgroundColor,rc.borderTopColor,rc.borderTopWidth,rc.fontWeight].join('|'):null,
                    crText:K.cr(K.rgba(c.color),under), crEdge:K.cr(K.rgba(c.borderTopColor),g), edgeW:c.borderTopWidth,
                    cursor:c.cursor, h:Math.round(b.getBoundingClientRect().height*10)/10, ink:c.color, edge:c.borderTopColor}); });
                return out;}""")
            R["S"] = Sx
            if not Sx: fails.append("%s S: no visible Skip-for-now button (exercise 1 open?)" % key)
            for r in Sx:
                if r["refWeight"] and r["weight"] != r["refWeight"]: fails.append("%s S: weight %s, the Check button %s" % (key, r["weight"], r["refWeight"]))
                if r["crEdge"] < 3: fails.append("%s S: edge %.2f < 3 : 1" % (key, r["crEdge"]))
                if r["crText"] < 4.5: fails.append("%s S: label %.2f < 4.5" % (key, r["crText"]))
                if r["cursor"] != "pointer" or r["h"] < 32: fails.append("%s S: cursor %s, height %s" % (key, r["cursor"], r["h"]))
            if SHOTS and Sx:
                pg.screenshot(path=os.path.join(SHOTS, "k3_skip_%s_%s.png" % (sk, th)), clip={"x": 290, "y": 330, "width": 560, "height": 200})
            # ---- H: the hint button, marks in the dark --------------------
            H = pg.evaluate("""()=>{var K=window.__k3, sb=[].filter.call(document.querySelectorAll('.sol-btn'),K.vis)[0];
                if(!sb) return {skipped:'no visible solution button'};
                var hb=document.createElement('button'); hb.className='lm-Widget jupyter-widgets jupyter-button widget-button sol-btn nbhint-btn';
                hb.textContent='Hint 1 of 2'; sb.parentElement.insertBefore(hb, sb);
                var hc=getComputedStyle(hb), sc=getComputedStyle(sb), g=K.ground(hb.parentElement);
                var ink=K.rgba(hc.color), bg=K.rgba(hc.backgroundColor); var under=bg&&bg[3]>0?K.over(bg,g):g;
                var o={hint:hc.color, hintBg:hc.backgroundColor, hintBorder:hc.borderTopColor, sol:sc.color, solBg:sc.backgroundImage.slice(0,40)||sc.backgroundColor,
                       cr:K.cr(ink,under), crEdge:K.cr(K.rgba(hc.borderTopColor),under)}; hb.remove(); return o;}""")
            R["H"] = H
            if not H.get("skipped"):
                if H["hint"] == H["sol"]: fails.append("%s H: hint ink = solution ink %s" % (key, H["hint"]))
                if H["cr"] < 4.5: fails.append("%s H: hint %.2f < 4.5" % (key, H["cr"]))
            pg.evaluate("()=>window.__nbSetGui(100)"); pg.wait_for_timeout(1500)
            mk = pg.evaluate(MARKS_JS, grounds)
            R["marks"] = {"n": len(mk), "min": min([m["cr"] for m in mk] or [0]), "under3": [m for m in mk if m["cr"] < 3]}
            if th == "dark" and R["marks"]["under3"]:
                fails.append("%s H: %d marks under 3 : 1 in the dark (%s)" % (key, len(R["marks"]["under3"]), R["marks"]["under3"][:2]))
        # ---- T: the texture and the lens (once per skin, light) ----------
        pg.evaluate(SET, [sk, "light"]); pg.wait_for_timeout(1500)
        T = {}
        for z in (100, 150):
            got = lens(pg, z)
            T[z] = pg.evaluate("""()=>{var s=window.__k3.sc(), c=getComputedStyle(s);
                return {zoom:null, size:c.backgroundSize, img:c.backgroundImage.slice(0,60), texz:getComputedStyle(document.body).getPropertyValue('--nbtexz').trim()};}""")
            T[z]["zoom"] = got
        lens(pg, 100)
        def px(sz):
            v = [float(x) for x in re.findall(r"([\d.]+)px", sz or "")]
            return v
        a, c = px(T[100]["size"]), px(T[150]["size"])
        T["ratio"] = [round(y / x, 3) for x, y in zip(a, c)] if a and len(a) == len(c) else None
        res[sk + "/T"] = T
        if T[100]["img"] == "none":
            T["note"] = "no texture in this skin"
        elif not a:
            T["note"] = "no tile (a wash across the page) — nothing to scale"
        # 2026-10-02 (CSS): K3.5 ("tile × 1.5 with the lens") is overruled since
        # E8.2 — the texture keeps its largest pitch (--nbtexz:2!important) and
        # the lens gives depth instead. Until E15.7 this check read the lens
        # from the shared key, which is no longer written (→ 0): it could not
        # tell a lens that did not move from a tile that did not grow.
        # Now: the lens DID move (≥ 145, read per notebook) and the tile stays.
        elif not (T[150]["zoom"] or 0) >= 145 or not T["ratio"] or any(abs(r - 1.0) > 0.05 for r in T["ratio"]):
            fails.append("%s T: tile %s → %s (lens %s → %s)" % (sk, T[100]["size"], T[150]["size"], T[100]["zoom"], T[150]["zoom"]))
        res[sk + "/errors"] = errs[:10]
        if errs: fails.append("%s: page errors %r" % (sk, errs[:3]))
    b.close()
json.dump({"res": res, "fails": fails}, open(out, "w"), indent=1, ensure_ascii=False)
for k, v in res.items():
    if k.endswith("/T"):
        print(k, v.get(100, {}).get("size"), "->", v.get(150, {}).get("size"), v.get("ratio"), v.get("note", ""))
    elif isinstance(v, dict) and "X" in v:
        x = v["X"]; print(k, "X band", x["band"], {s: (f["vsBand"], f["vsEdge"], f["vsPanel"]) if f else None for s, f in x["fills"].items()})
        print(k, "N", {p: (n["W"], round(n["k"], 3), n["names_on"], n["pip"], len(n["names"]), n["ncut"], len(n["overlaps"]),
                          max([abs(x["mid"]) for x in n["names"]] or [0]), min(n["pipGap"] or [0]), n["floor"]) for p, n in v["N"].items()})
        print(k, "S", [(r["weight"], r["refWeight"], r["crText"], r["crEdge"], r["cursor"], r["h"]) for r in v["S"][:1]])
        print(k, "G", {p: (g["grip"][:30], g["gap"], g["railEdge"]) for p, g in v["G"].items()})
        print(k, "L", len(v["L"]["locked"]), len(v["L"]["waiting"]), [(r["name"], r["crName"], r["crLock"], r["crWord"]) for r in (v["L"]["locked"][:1] + v["L"]["waiting"][:1])])
        print(k, "H", v["H"].get("cr"), v["H"].get("hint"), "marks min", v["marks"]["min"], "under3", len(v["marks"]["under3"]))
print("\n" + ("K3 OK" if not fails else "FAILURES (%d):\n- " % len(fails) + "\n- ".join(fails)))
sys.exit(1 if fails else 0)
