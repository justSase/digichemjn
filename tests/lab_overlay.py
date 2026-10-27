"""Real-JupyterLab measurement for STRUKTUR §4/§4a — the panel is an overlay. 2026-09-27b.

NOT a suite: it needs a running `jupyter lab` (see lab_keys.py). For each skin
and the panel control at 0/25/50/100 %% it reads, with getBoundingClientRect
and getComputedStyle:
  * the document cell, the first reading box, the zoom control, the profile
    chip and the toolbar  — must not move when the panel opens;
  * every visible mark: its laid-out size, its box across the panel after the
    turn, its opacity   — at 0 %% the smallest must be >= 10 px, none faded,
    none outside the panel, no two overlapping;
  * hit tests: a free point in the panel reaches the DOCUMENT; the centre of
    each mark reaches its node; the centre of the zoom control reaches it.

  2026-10-03 (E21 Rest Stufe 2, JS) — "none faded" BEHAUPTETE BISHER (27b)
  that no mark is dimmed. Since E18.3 (user, 02.10.) a LOCKED chapter or
  exercise is dimmed on purpose (dashed grey, opacity ≈ 0.45): measured
  v1.61 and the v1.62 probe, Complex 0/25/50/100 %, the 6 "faded" marks
  are exactly the 6 locked chapters at 0.45 (Befund Dirigent f: the lock
  look, not a fault). Now: a mark that is not locked must not be faded
  (< 0.5), a locked one must be dimmed but still there (0.3 … < 0.9).

    python3 tests/lab_overlay.py <notebook> <out.json> [skin,skin,...]

Exit 1 if a criterion fails."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import fresh, CHROME
from playwright.sync_api import sync_playwright
BASE=os.environ.get("DIGICHEM_LAB_URL","http://127.0.0.1:8899"); ROOT=os.environ.get("DIGICHEM_LAB_ROOT","/home/claude/lab/root")
nb=sys.argv[1]; out=sys.argv[2]
skins=sys.argv[3].split(",") if len(sys.argv)>3 else [None]
M = r"""() => {
  function R(e){ if(!e) return null; var r=e.getBoundingClientRect(); return [Math.round(r.left*10)/10,Math.round(r.top*10)/10,Math.round(r.width*10)/10,Math.round(r.height*10)/10]; }
  var P=document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)');
  var cells=P.querySelectorAll('.jp-Cell'); var cell=cells[1];
  var h=document.getElementById('nbpanel-root'); var rail=h.querySelector('.nbrail');
  var MK='.nbsect,.nbsubdot,.nbchapdot,.nbvizmark,.nbrail-dot,.nbcodemark,.nbendmark,.nbcellmark';
  var marks=[];
  h.querySelectorAll('.nbmap-node').forEach(function(n,i){
    if(n.classList.contains('nbgone')) return;
    var m=n.querySelector(MK); if(!m) { marks.push({i:i,cls:n.className,none:1}); return; }
    var cs=getComputedStyle(m); if(cs.display==='none'||cs.visibility==='hidden') { marks.push({i:i,cls:n.className,hidden:1}); return; }
    var r=m.getBoundingClientRect();
    var op=1; for(var a2=m;a2&&a2!==h;a2=a2.parentElement) op*= +getComputedStyle(a2).opacity;
    marks.push({i:i,cls:n.className.replace('nbjump nbmap-node ',''),mk:m.className,w:m.offsetWidth,h:m.offsetHeight,op:op,
      bb:[r.left,r.top,r.width,r.height]});
  });
  var rr=rail.getBoundingClientRect();
  // overlaps between neighbouring visible marks
  var vis=marks.filter(function(m){return m.bb && m.bb[2]>0;}), ov=[];
  // E18.3: locked marks are dimmed on purpose (≈ 0.45), the others never
  var lk=function(m){ return /(^|\s)locked(\s|$)/.test(m.cls) || /(^|\s)nblocked(\s|$)/.test(m.cls); };
  var faded=marks.filter(function(m){return m.bb && !lk(m) && m.op<0.5;}).length;
  var lockOff=marks.filter(function(m){return m.bb && lk(m) && !(m.op>=0.3 && m.op<0.9);}).map(function(m){return m.i+':'+Math.round(m.op*100)/100;});
  var nlocked=marks.filter(function(m){return m.bb && lk(m);}).length;
  for(var a=0;a<vis.length;a++) for(var b=a+1;b<vis.length;b++){ var A=vis[a].bb,B=vis[b].bb;
    if(A[0]<B[0]+B[2]-0.5&&B[0]<A[0]+A[2]-0.5&&A[1]<B[1]+B[3]-0.5&&B[1]<A[1]+A[3]-0.5) ov.push([vis[a].i,vis[b].i]); }
  // outside the rail?
  var outside=vis.filter(function(m){return m.bb[0]<rr.left-0.5||m.bb[0]+m.bb[2]>rr.right+0.5;}).map(function(m){return m.i;});
  // hit test: a free spot in the panel (between marks), 3px inside its left edge, mid-height
  var free=null;
  for (var y=rr.top+rr.height*0.5; y<rr.bottom-10; y+=7){
    var x=rr.left+Math.min(3, rr.width/4);
    var st=document.elementsFromPoint(x,y); var top=st[0];
    if (top && !top.closest('.nbmap-node') && !top.closest('.nbgrip')) { free={x:x,y:y,top:(top.className||top.tagName).toString().slice(0,60),inDoc:!!top.closest('.jp-NotebookPanel'),inPanel:!!top.closest('#nbpanel-root')}; break; }
  }
  var markHit=0, markMiss=[]; vis.forEach(function(m){ var x=m.bb[0]+m.bb[2]/2, y=m.bb[1]+m.bb[3]/2;
    if (y<rr.top+30||y>rr.bottom-5) return; var t=document.elementFromPoint(x,y);
    var node=h.querySelectorAll('.nbmap-node')[m.i]; if (t && node && node.contains(t)) markHit++; else markMiss.push(m.i+':'+(t?(t.className||t.tagName).toString().slice(0,30):'-')); });
  var zEl=h.querySelector('.nbz-doc'), zr=zEl.getBoundingClientRect(); var zt=document.elementFromPoint(zr.left+zr.width/2, zr.top+zr.height/2);
  var zoomHit=!!(zt && zEl.contains(zt));
  var grid={doc:0,panel:0,node:0}; for (var gx=rr.left+2; gx<rr.right-2; gx+=Math.max(4,rr.width/12)) for (var gy=rr.top+rr.height*0.2; gy<rr.bottom-10; gy+=37){
    var t2=document.elementFromPoint(gx,gy); if(!t2) continue; if (t2.closest('.nbmap-node')||t2.closest('.nbgrip')||t2.closest('.nbmap-here')||t2.closest('.nbmap-cursor')) grid.node++; else if (t2.closest('#nbpanel-root')) grid.panel++; else if (t2.closest('.jp-NotebookPanel')) grid.doc++; }
  var zi=[]; for(var e=rail;e&&e!==document.body;e=e.parentElement){var z=getComputedStyle(e).zIndex; zi.push((e.id||e.className.toString().split(' ')[0])+':'+z+':'+getComputedStyle(e).position+':pe='+getComputedStyle(e).pointerEvents);}
  var boxes=[].slice.call(cell.querySelectorAll('.nbbox')).filter(function(b){return b.getBoundingClientRect().width>0;});
  return {
    gui: window.__nbGui, w: getComputedStyle(document.documentElement).getPropertyValue('--nbvert-w'),
    pad: getComputedStyle(document.documentElement).getPropertyValue('--nbvert-pad'),
    cut: getComputedStyle(document.documentElement).getPropertyValue('--nbdock-cut'),
    thick: getComputedStyle(document.documentElement).getPropertyValue('--nbthick'),
    lab: getComputedStyle(document.documentElement).getPropertyValue('--nbvert-lab'),
    cell: R(cell), cellPadR: getComputedStyle(cell).paddingRight,
    out: R(cell.querySelector('.jp-OutputArea')), box0: R(boxes[0]),
    footer: R(document.querySelector('.jp-Notebook-footer')),
    dock: R(h.querySelector('.nbdock')), ctrl: R(h.querySelector('.nbctrl')),
    zoom: R(h.querySelector('.nbz-doc')), profile: R(h.querySelector('.nbprofile')),
    dockClip: getComputedStyle(h.querySelector('.nbdock')).clipPath,
    rail: R(rail), railZ: getComputedStyle(rail).zIndex, chain: zi,
    free: free, markHit: markHit, markMiss: markMiss, zoomHit: zoomHit, grid: grid, railBg: getComputedStyle(rail).backgroundColor, dockZ: getComputedStyle(h.querySelector('.nbdock')).zIndex, marks: marks, overlaps: ov, outside: outside,
    minMark: Math.min.apply(null, vis.map(function(m){return Math.min(m.w,m.h);})),
    maxBB: Math.max.apply(null, vis.map(function(m){return m.bb[2];})),
    nvis: vis.length, faded: faded, lockOff: lockOff, nlocked: nlocked, sym: getComputedStyle(h).getPropertyValue('--nbsym'), circ: getComputedStyle(h).getPropertyValue('--nbcirc'), hostCls: h.className, nhidden: marks.filter(function(m){return m.hidden||m.none;}).length,
    cursor: R(h.querySelector('.nbvcursor, .nbmap-cursor, .nbcursor'))
  };
}"""
res={}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME)
    ctx,pg,errs=fresh(b,BASE,nb,ROOT)
    for sk in skins:
        if sk:
            pg.evaluate("(s)=>{ window.__nbStore.set('digichemjn.skin.v1', s); window.__nbApplySkin && window.__nbApplySkin(); }", sk)
            pg.wait_for_timeout(1500)
        for pct in [0,25,50,100]:
            pg.evaluate("(p)=>window.__nbSetGui(p)", pct); pg.wait_for_timeout(1800)
            res["%s/%d"%(sk,pct)]=pg.evaluate(M)
    res["errs"]=errs
json.dump(res,open(out,"w"),indent=1)
fails=[]
KEYS=("cell","box0","zoom","profile","dock")
for sk in skins:
    r0=res["%s/0"%sk]
    for pct in (25,50,100):
        r=res["%s/%d"%(sk,pct)]
        for k in KEYS:
            if r[k]!=r0[k]: fails.append("%s %d%%: %s moved %s -> %s"%(sk,pct,k,r0[k],r[k]))
    for pct in (0,25,50,100):
        r=res["%s/%d"%(sk,pct)]
        if r["overlaps"]: fails.append("%s %d%%: %d marks overlap"%(sk,pct,len(r["overlaps"])))
        if r["outside"]: fails.append("%s %d%%: marks outside the panel %s"%(sk,pct,r["outside"]))
        if r["faded"]: fails.append("%s %d%%: %d marks faded out that are not locked"%(sk,pct,r["faded"]))
        if r["lockOff"]: fails.append("%s %d%%: locked marks not dimmed as E18.3 (0.3 … < 0.9): %s"%(sk,pct,r["lockOff"]))
        if r["nhidden"]: fails.append("%s %d%%: %d marks not drawn"%(sk,pct,r["nhidden"]))
        if not (r["free"] and r["free"]["inDoc"]): fails.append("%s %d%%: a free point in the panel does not reach the document (%s)"%(sk,pct,r["free"]))
        if r["markMiss"]: fails.append("%s %d%%: marks not clickable %s"%(sk,pct,r["markMiss"]))
        if not r["zoomHit"]: fails.append("%s %d%%: the zoom control is covered"%(sk,pct))
        if r["pad"].strip() not in ("","0px") or r["cut"].strip() not in ("","0px"): fails.append("%s %d%%: a reserve is back (pad %r cut %r)"%(sk,pct,r["pad"],r["cut"]))
    if res["%s/0"%sk]["minMark"] < 10: fails.append("%s 0%%: smallest mark %s px"%(sk,res["%s/0"%sk]["minMark"]))
if res["errs"]: fails.append("console: %s"%res["errs"][:3])
def s(r): return "hit %s zoomHit %s grid %s bg %s dockZ %s | cell %s padR %s | box0 %s | zoom %s | profile %s | dock %s clip %s | rail %s | min %s maxBB %s nvis %d faded %s locked %s hid %d ov %d outside %d | free %s"%(r['markHit'],r['zoomHit'],r['grid'],r['railBg'],r['dockZ'],r['cell'],r['cellPadR'],r['box0'],r['zoom'],r['profile'],r['dock'],r['dockClip'],r['rail'],r['minMark'],r['maxBB'],r['nvis'],r['faded'],r['nlocked'],r['nhidden'],len(r['overlaps']),len(r['outside']),r['free'])
for k,v in res.items():
    if k!="errs": print(k, s(v))
print("errs", res["errs"][:5])
for f in fails: print("FAIL", f)
print("OVERLAY OK" if not fails else "OVERLAY: %d failures" % len(fails))
sys.exit(1 if fails else 0)
