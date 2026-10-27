"""Real-JupyterLab measurement for K4 (panel out to half the notebook, content
scales with it) and the trail behind the movement. 2026-09-28c.

DIGICHEM_SIDEBAR_SHUT=1: JupyterLab's left side bar shut first (wider notebook).

NOT a suite: it needs a running `jupyter lab` (see lab_keys.py).

    python3 tests/lab_k4.py <notebook> <out.json> [skin,...] [width,...] [part,...]

parts: W  width, scale, names, overlaps, document boxes, retract (per skin x theme)
       G  the real grip, dragged with the mouse to its far end and back
       T  no trail (E16.3): real wheel down / up / turn round, sampled every 100 ms
Everything read with getBoundingClientRect / getComputedStyle. Exit 1 on a failed
criterion. Screenshots of the widest panel go next to <out.json>.

Rewritten 2026-10-01 (E10 Schritt C, v1.45) — four claims were older than the
rules they measured:
  * far end: claimed "half the notebook"; since E7.2 it is the PAGE's middle —
    max(notebook/2, min(notebook.right − innerWidth/2, notebook − 40)), 662 px
    at 1400 with the file browser open;
  * name vs. pips: claimed "the pips stand BELOW the name" (pips.top −
    name.bottom >= 0); since E7.1 they stand right of the lane, beside it —
    now: the two boxes do not intersect;
  * the marker's light: claimed "never ahead of the marker"; since E11.8 and
    E12.5 the light is centred on the marker (only the TRAIL is behind) —
    now: light middle − marker middle <= 2 px;
  * catch-up time: claimed 1000 ms for every style; since R3 it is the style's
    --nbm-trail-ms (minimal 1000, cyber 450, retro 1300, fairy 1400), ±10 %,
    sampled every 100 ms for up to 2.2 s."""
import sys, json, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import fresh, CHROME
from playwright.sync_api import sync_playwright
BASE = os.environ.get("DIGICHEM_LAB_URL", "http://127.0.0.1:8899")
ROOT = os.environ.get("DIGICHEM_LAB_ROOT", "/home/claude/lab/root")
nb, out = sys.argv[1], sys.argv[2]
skins = sys.argv[3].split(",") if len(sys.argv) > 3 and sys.argv[3] else ["minimal", "cyber", "retro", "fairy"]
widths = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 and sys.argv[4] else [1400, 1920]
parts = sys.argv[5].split(",") if len(sys.argv) > 5 and sys.argv[5] else ["W", "G", "T"]
themes = ["light", "dark"]
WSTD = 560.0
SET = """([s,t]) => { window.__nbStore.set('digichemjn.skin.v1', s); window.__nbStore.set('digichemjn.theme.v1', t);
  window.__nbApplySkin(); window.__nbApplyTheme(); }"""
M = r"""() => {
  function R(e){ if(!e) return null; var r=e.getBoundingClientRect(); return [r.left,r.top,r.width,r.height]; }
  var h=document.getElementById('nbpanel-root'), P=document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var cell=P.querySelectorAll('.jp-Cell')[1];
  var boxes=[].slice.call(cell.querySelectorAll('.nbbox')).filter(function(b){return b.getBoundingClientRect().width>0;});
  var rail=h.querySelector('.nbrail'), inner=h.querySelector('.nbmap-inner');
  var first=function(sel){ var a=h.querySelectorAll(sel); for(var i=0;i<a.length;i++){ var n=a[i].closest('.nbmap-node'); if(n&&n.classList.contains('nbgone')) continue; if(a[i].offsetWidth>0) return a[i]; } return null; };
  var size={};
  ['.nbsect','.nbsubdot','.nbchapdot','.nbvizmark','.nbrail-dot','.nbcodemark','.nbendmark','.nbcellmark'].forEach(function(s){ var e=first(s); size[s]=e?e.offsetWidth:null; });
  var ps=first('.nbchapstat .ps'); size.pip=ps?ps.offsetWidth:null;
  var cl=first('.nbmap-node.chap .nbmap-lab'), sl=first('.nbmap-node.sect .nbmap-lab'), tl=first('.nbtasklab');
  size.fontChap=cl?parseFloat(getComputedStyle(cl).fontSize):null;
  size.fontSect=sl?parseFloat(getComputedStyle(sl).fontSize):null;
  size.fontTask=tl?parseFloat(getComputedStyle(tl).fontSize):null;
  size.lane=parseFloat(getComputedStyle(inner,'::before').width);
  var mk=h.querySelector('.nbmap-here'), mkr=mk.getBoundingClientRect(); size.markerW=mkr.width; size.markerH=mkr.height;
  size.markerBand=parseFloat(getComputedStyle(mk,'::before').width);
  var cu=h.querySelector('.nbmap-cursor'); size.cursor=cu?cu.offsetWidth:null;
  // names: every visible one, how many are cut, where their middle is
  var names=[], items=[];
  var labx=parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nbvert-labx'))||0;
  var labw=parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nbvert-lab'))||0;
  var rr=rail.getBoundingClientRect();
  h.querySelectorAll('.nbmap-node').forEach(function(n,i){
    if(n.classList.contains('nbgone')) return;
    n.querySelectorAll('.nbmap-lab,.nbtasklab').forEach(function(l){
      var cs=getComputedStyle(l); if(cs.display==='none'||cs.visibility==='hidden'||l.offsetWidth===0) return;
      var r=l.getBoundingClientRect(), lh=parseFloat(cs.lineHeight)||parseFloat(cs.fontSize)*1.2;
      // the text's own width, in a probe that does not clamp
      var pr=document.createElement('span'); pr.textContent=l.textContent; pr.style.cssText='position:absolute;visibility:hidden;white-space:nowrap;font:'+cs.font+';letter-spacing:'+cs.letterSpacing+';text-transform:'+cs.textTransform;
      document.body.appendChild(pr); var tw=pr.getBoundingClientRect().width; pr.remove();
      var cut=(l.scrollHeight>l.clientHeight+1)||(l.scrollWidth>l.clientWidth+1);
      names.push({i:i,t:l.textContent,cut:cut,lines:Math.round(r.height/lh),w:r.width,tw:Math.round(tw),
        mid:Math.round((r.left+r.width/2-(rr.left+1+labx+labw/2))*10)/10});
      items.push({i:i,k:'lab',bb:[r.left,r.top,r.width,r.height]});
    });
    var cs2=n.querySelector('.nbchapstat'); if(cs2&&cs2.offsetWidth>0){ var q=cs2.getBoundingClientRect();
      // the pips themselves, not the flex row across the column
      var ps2=cs2.querySelectorAll('.ps'); if(ps2.length){ var a=ps2[0].getBoundingClientRect(), b=ps2[ps2.length-1].getBoundingClientRect();
        items.push({i:i,k:'pips',bb:[a.left,Math.min(a.top,b.top),b.right-a.left,Math.max(a.bottom,b.bottom)-Math.min(a.top,b.top)]}); } }
    var m=n.querySelector('.nbsect,.nbsubdot,.nbchapdot,.nbvizmark,.nbrail-dot,.nbcodemark,.nbendmark,.nbcellmark');
    if(m&&m.offsetWidth>0){ var r2=m.getBoundingClientRect(); items.push({i:i,k:'mark',bb:[r2.left,r2.top,r2.width,r2.height]}); }
  });
  var ov=[];
  for(var a=0;a<items.length;a++) for(var b=a+1;b<items.length;b++){ if(items[a].i===items[b].i) continue;
    var A=items[a].bb,B=items[b].bb;
    if(A[0]<B[0]+B[2]-0.5&&B[0]<A[0]+A[2]-0.5&&A[1]<B[1]+B[3]-0.5&&B[1]<A[1]+A[3]-0.5) ov.push([items[a].i+items[a].k,items[b].i+items[b].k]); }
  // own node: the name against its own pips (two lines must push the pips down)
  var own=[]; h.querySelectorAll('.nbmap-node.chap').forEach(function(n,i){ var l=n.querySelector('.nbmap-lab'), c=n.querySelector('.nbchapstat .ps');
    if(!l||!c||l.offsetWidth===0||c.offsetWidth===0) return; var a=l.getBoundingClientRect(), b=c.getBoundingClientRect();
    // E7.1: the pips stand beside the name (right of the lane); the gap is the
    // larger of the horizontal and vertical clearances — < 0 only if they meet
    own.push(Math.round(Math.max(b.left-a.right, b.top-a.bottom, a.left-c.getBoundingClientRect().right)*10)/10); });
  var PR=P.getBoundingClientRect();
  return {nbW:PR.width, nbR:PR.right, vw:window.innerWidth, farEnd:Math.round(PR.width/2), half:window.__nbWhalf, rail:rr.width, k:window.__nbK, W:window.__nbW, gui:window.__nbGui,
    gmax:window.__nbGMax?window.__nbGMax():null, names_on:h.classList.contains('nbnames'),
    cell:R(cell), box0:R(boxes[0]), box1:R(boxes[1]), size:size, names:names, overlaps:ov, pipGap:own};
}"""
# ---- trail -------------------------------------------------------------
TR = r"""() => { var h=document.getElementById('nbpanel-root'), t=h.querySelector('.nbmap-trail'), m=h.querySelector('.nbmap-here');
  var map=h.querySelector('.nbmap'); var line=map.getBoundingClientRect().top+(parseInt(h.dataset.railY0||'0',10)||0);
  var mr=m.getBoundingClientRect(), tr=t?t.getBoundingClientRect():null;
  var sc=document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer');
  var b=t?getComputedStyle(t,'::before'):null, g=t?getComputedStyle(t,'::after'):null, ma=getComputedStyle(m,'::after');
  return {now:performance.now(), t0:h.__nbTr?h.__nbTr.t0:null, st:sc.scrollTop, line:line,
    mTop:mr.top, mBot:mr.bottom, mMid:mr.top+mr.height/2, mdir:m.getAttribute('data-dir'),
    side:t?t.getAttribute('data-side'):null, tTop:tr?tr.top:null, tBot:tr?tr.bottom:null, tH:tr?tr.height:0,
    op:t?getComputedStyle(t).opacity:null, bandMask:b?b.webkitMaskImage:null, glowMask:g?g.webkitMaskImage:null,
    mGlowTop:parseFloat(ma.top), mGlowH:parseFloat(ma.height), mGlowMask:ma.webkitMaskImage,
    trMs:parseFloat(getComputedStyle(document.body).getPropertyValue('--nbm-trail-ms'))}; }"""

res = {}; fails = []
def F(msg): fails.append(msg); print("FAIL", msg, flush=True)

def pct_for(pg, w):
    return pg.evaluate("(w)=>{ var wm=window.__nbWmin||16; return Math.round((w-wm)/((560-wm)/100)); }", w)

def setw(pg, pct, wait=1600):
    pg.evaluate("(p)=>window.__nbSetGui(p)", pct); pg.wait_for_timeout(wait)
    return pg.evaluate(M)

def part_w(pg, W, sk, th, shot_dir):
    key = "%d/%s/%s" % (W, sk, th)
    r0 = setw(pg, 0)
    std = setw(pg, 100)
    mx = setw(pg, 99999)
    half = mx["nbW"] / 2
    mid_w = (min(WSTD, half) + half) / 2 if half > WSTD else None
    q25 = setw(pg, pct_for(pg, round(0.25 * mx["nbW"])))
    mid = setw(pg, pct_for(pg, round(mid_w))) if mid_w else None
    # 2026-09-28c (Hauptwerkstatt): the same at the FOOT of the document, widest
    # panel. footAlign (24az) pulls "your own cell" onto the footer only while the
    # footer is on screen — at the top it never runs, so the check above could not
    # see it pull the mark onto "End" (measured: 14 px apart, 43-px marks, K 1.65)
    setw(pg, 99999, 800)
    st0 = pg.evaluate("()=>document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer').scrollTop")
    pg.evaluate("()=>{var s=document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer'); s.scrollTop=s.scrollHeight; s.dispatchEvent(new Event('scroll'));}")
    pg.wait_for_timeout(2600)
    foot = pg.evaluate(M)
    pg.evaluate("(y)=>{var s=document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer'); s.scrollTop=y; s.dispatchEvent(new Event('scroll'));}", st0)
    pg.wait_for_timeout(1600)
    back = setw(pg, 100)
    res[key] = {"0": r0, "std": std, "max": mx, "q25": q25, "mid": mid, "back": back, "foot": foot}
    if foot["overlaps"]: F("%s foot: %d overlaps at the end of the document %s" % (key, len(foot["overlaps"]), foot["overlaps"][:6]))
    if W == widths[-1] and sk in ("minimal", "retro"):
        setw(pg, 99999, 1800); pg.evaluate("()=>{var s=document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer'); s.scrollTop=900; s.dispatchEvent(new Event('scroll'));}")
        pg.wait_for_timeout(1800)
        pg.screenshot(path=os.path.join(shot_dir, "k4_%d_%s_%s_max.png" % (W, sk, th)))
        setw(pg, 100)
    # 1) the far end is the page's middle (E7.2), never less than half the notebook
    # E19.1 — THIS BEHAUPTETE BISHER (E7.2) "the far end is the page's middle";
    # the user took it back: at most half the notebook area, reached to 6 px
    if not (mx["farEnd"] - 6 <= mx["rail"] <= mx["farEnd"] + 1): F("%s: widest panel %.1f, far end (half the notebook) %.1f" % (key, mx["rail"], mx["farEnd"]))
    # 2) the document does not move
    for nm, r in (("std", std), ("max", mx), ("q25", q25), ("back", back)):
        for b in ("cell", "box0", "box1"):
            if r[b] != r0[b]: F("%s: %s %s moved %s -> %s" % (key, nm, b, r0[b], r[b]))
    # 3) scale above the standard width: size = standard x (width / 560) +-5 %
    base = std if std["rail"] >= WSTD - 0.5 else None
    for nm, r in (("mid", mid), ("max", mx)):
        if not r or not base or r["rail"] <= WSTD + 0.5: continue
        kk = r["rail"] / WSTD
        for q, v0 in base["size"].items():
            v = r["size"].get(q)
            if not v0 or v is None: continue
            want = min(3.0, kk)
            if abs(v / v0 - want) > 0.05 * want:
                F("%s %s (w %.0f, k %.3f): %s %.2f -> %.2f = x%.3f" % (key, nm, r["rail"], kk, q, v0, v, v / v0))
    # 4) names: none cut at the widest, none overlapping, all centred
    for nm, r in (("std", std), ("max", mx), ("mid", mid)):
        if not r: continue
        cut = [n["t"] for n in r["names"] if n["cut"]]
        off = [n for n in r["names"] if abs(n["mid"]) > 2]
        if nm in ("max", "mid") and cut: F("%s %s: %d names cut %s" % (key, nm, len(cut), cut))
        if r["overlaps"]: F("%s %s: %d overlaps %s" % (key, nm, len(r["overlaps"]), r["overlaps"][:6]))
        if off: F("%s %s: %d names off the column's middle %s" % (key, nm, len(off), [(n["t"], n["mid"]) for n in off][:4]))
        if any(g < 0 for g in r["pipGap"]): F("%s %s: a chapter name runs into its pips %s" % (key, nm, r["pipGap"]))
    # 5) pulled back to the standard width, every measure is what it was
    for q in ("rail", "size", "k"):
        if back[q] != std[q]: F("%s: back at 100 %% %s %s != %s" % (key, q, back[q], std[q]))
    if [n["t"] for n in back["names"]] != [n["t"] for n in std["names"]]: F("%s: back at 100 %%, other names" % key)
    print(key, "half %.0f | std w %.0f k %s | max w %.1f k %.3f | mid %s | q25 w %.0f k %s | names on std/max %s/%s cut std %d max %d | ov %d/%d" % (
        half, std["rail"], std["k"], mx["rail"], mx["k"] or 0, mid and ("%.0f/%.3f" % (mid["rail"], mid["k"] or 0)), q25["rail"], q25["k"],
        std["names_on"], mx["names_on"], sum(n["cut"] for n in std["names"]), sum(n["cut"] for n in mx["names"]),
        len(std["overlaps"]), len(mx["overlaps"])), flush=True)

def part_g(pg, W):
    """the real grip: press, drag left past the far end, release; then back"""
    key = "%d/grip" % W
    setw(pg, 100)
    r0 = pg.evaluate(M)
    g = pg.evaluate("()=>{var g=document.querySelector('#nbpanel-root .nbgrip'); var r=g.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];}")
    pg.mouse.move(g[0], g[1]); pg.mouse.down()
    for x in range(0, 1400, 40):
        pg.mouse.move(g[0] - x, g[1]); pg.wait_for_timeout(15)
    pg.mouse.up(); pg.wait_for_timeout(1800)
    r1 = pg.evaluate(M)
    g2 = pg.evaluate("()=>{var g=document.querySelector('#nbpanel-root .nbgrip'); var r=g.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];}")
    d = r1["rail"] - r0["rail"]
    if d < 3:       # already at the far end (1400: half < 560) — a press would be a click
        res[key] = {"before": r0, "dragged": r1, "back": r1}
        half = r1["nbW"] / 2
        print(key, "grip: %.1f -> %.1f (half %.1f), nothing to drag back" % (r0["rail"], r1["rail"], half), flush=True)
        if not (r1["farEnd"] - 6 <= r1["rail"] <= r1["farEnd"] + 1): F("%s: dragged to the end %.1f, far end %.1f" % (key, r1["rail"], r1["farEnd"]))
        return
    pg.mouse.move(g2[0], g2[1]); pg.mouse.down()
    for x in range(0, int(d) + 1, 20):
        pg.mouse.move(g2[0] + x, g2[1]); pg.wait_for_timeout(15)
    pg.mouse.move(g2[0] + d, g2[1]); pg.mouse.up(); pg.wait_for_timeout(1800)
    r2 = pg.evaluate(M)
    res[key] = {"before": r0, "dragged": r1, "back": r2}
    half = r1["nbW"] / 2
    print(key, "grip: %.1f -> %.1f (half %.1f) -> back %.1f" % (r0["rail"], r1["rail"], half, r2["rail"]), flush=True)
    if not (r1["farEnd"] - 6 <= r1["rail"] <= r1["farEnd"] + 1): F("%s: dragged to the end %.1f, far end %.1f" % (key, r1["rail"], r1["farEnd"]))
    for b in ("cell", "box0", "box1"):
        if r1[b] != r0[b]: F("%s: %s moved %s -> %s" % (key, b, r0[b], r1[b]))
    if abs(r2["rail"] - r0["rail"]) > 6: F("%s: dragged back %.1f, was %.1f" % (key, r2["rail"], r0["rail"]))

def samples(pg, n=22, dt=100):
    out = []
    for _ in range(n):
        out.append(pg.evaluate(TR)); pg.wait_for_timeout(dt)
    return out

def check_run(key, what, moving, seq, want_side):
    """moving = sample right after the last wheel; seq = 100 ms samples after.
    2026-10-02 (E16.3) — THIS BEHAUPTETE BISHER (28c/E12.5): "the trail lies
    behind the movement and catches up within --nbm-trail-ms". The user
    replaced the trail with one round light behind the marker (E16.3): now
    no trail is drawn, moving or after the stop, the marker's light stays
    centred on it and the marker on the line. `want_side` is kept for the
    callers (which way the wheel went)."""
    ok = True
    allS = [moving] + list(seq)
    tmax = max(s["tH"] for s in allS)
    if tmax > 0.5:
        F("%s %s: a trail is still drawn (%.1f px)" % (key, what, tmax)); ok = False
    gm = moving["mGlowTop"] + moving["mGlowH"] / 2 - (moving["mBot"] - moving["mTop"]) / 2
    if not (abs(gm) <= 2):
        F("%s %s: the marker's light is %.1f px off the marker's middle (top %.1f h %.1f)" % (key, what, gm, moving["mGlowTop"], moving["mGlowH"])); ok = False
    if abs(moving["mMid"] - moving["line"]) > 2:
        F("%s %s: marker %.1f px off the line" % (key, what, moving["mMid"] - moving["line"])); ok = False
    return {"moving": {k: moving[k] for k in ("mMid", "line", "mGlowTop", "mGlowH")}, "trailMax": tmax, "ok": ok}

def turned(pg, dy):
    """wheel the other way at once, and sample the moment the DOCUMENT has
    really turned round (smooth scrolling may still carry the old way for a
    few frames): the first 20-ms poll at which scrollTop has moved against
    the last direction by more than 2 px from its extreme"""
    ext = pg.evaluate(TR)["st"]
    pg.mouse.wheel(0, dy)
    for _ in range(40):
        pg.wait_for_timeout(20)
        s = pg.evaluate(TR)
        if dy > 0: ext = min(ext, s["st"])
        else: ext = max(ext, s["st"])
        if (dy > 0 and s["st"] > ext + 2) or (dy < 0 and s["st"] < ext - 2):
            pg.wait_for_timeout(20)
            return pg.evaluate(TR)
    return pg.evaluate(TR)

def part_t(pg, W, sk, th):
    key = "%d/%s/%s/trail" % (W, sk, th)
    setw(pg, 100, 1200)
    box = pg.evaluate("()=>{var c=document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer').getBoundingClientRect(); return [c.left+c.width*0.3, c.top+c.height*0.5];}")
    pg.evaluate("()=>{var s=document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer'); s.scrollTop=600;}")
    pg.wait_for_timeout(1600)
    pg.mouse.move(box[0], box[1])
    out = {}
    # down
    for _ in range(3): pg.mouse.wheel(0, 100); pg.wait_for_timeout(60)
    pg.wait_for_timeout(120)
    mv = pg.evaluate(TR); seq = samples(pg)
    out["down"] = check_run(key, "down", mv, seq, "above")
    pg.wait_for_timeout(500)
    # up
    for _ in range(3): pg.mouse.wheel(0, -100); pg.wait_for_timeout(60)
    pg.wait_for_timeout(120)
    mv = pg.evaluate(TR); seq = samples(pg)
    out["up"] = check_run(key, "up", mv, seq, "below")
    pg.wait_for_timeout(500)
    # turn round at once: down, then up with no pause
    for _ in range(3): pg.mouse.wheel(0, 100); pg.wait_for_timeout(60)
    pg.wait_for_timeout(120)
    mv = turned(pg, -100); seq = samples(pg)
    out["turn"] = check_run(key, "turn down->up", mv, seq, "below")
    pg.wait_for_timeout(500)
    for _ in range(3): pg.mouse.wheel(0, -100); pg.wait_for_timeout(60)
    pg.wait_for_timeout(120)
    mv = turned(pg, 100); seq = samples(pg)
    out["turn2"] = check_run(key, "turn up->down", mv, seq, "above")
    res[key] = out
    print(key, {k: (round(v["trailMax"], 1), v["ok"]) for k, v in out.items()}, flush=True)

shot_dir = os.path.dirname(os.path.abspath(out))
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    for W in widths:
        ctx, pg, errs = fresh(b, BASE, nb, ROOT)
        pg.set_viewport_size({"width": W, "height": 900}); pg.wait_for_timeout(2500)
        # 2026-09-28c (Hauptwerkstatt): DIGICHEM_SIDEBAR_SHUT=1 shuts JupyterLab's
        # left side bar first (Ctrl+B) — the notebook is wider, so is its half
        # and K (1920: 0.5 x 1842 = 921, K 1.64 instead of 1.42)
        if os.environ.get("DIGICHEM_SIDEBAR_SHUT") == "1":
            pg.keyboard.press("Control+b"); pg.wait_for_timeout(1500)
        for sk in skins:
            for th in themes:
                pg.evaluate(SET, [sk, th]); pg.wait_for_timeout(1200)
                if "W" in parts: part_w(pg, W, sk, th, shot_dir)
                if "T" in parts: part_t(pg, W, sk, th)
        if "G" in parts:
            pg.evaluate(SET, ["minimal", "light"]); pg.wait_for_timeout(1000)
            part_g(pg, W)
        res["%d/errs" % W] = errs
        if errs: F("%d: console %s" % (W, errs[:3]))
        ctx.close()
json.dump(res, open(out, "w"), indent=1, default=str)
print("K4 OK" if not fails else "K4: %d failures" % len(fails))
sys.exit(1 if fails else 0)
