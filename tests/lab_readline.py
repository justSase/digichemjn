"""Real-JupyterLab measurement for STRUKTUR §4b — the reading line. 2026-09-27d;
rewritten 2026-09-30 (E11 Schritt B) to the rule since E9.2; rewritten again
2026-10-01 (E10 Teil 4, JS) to E12.2 + E12.3:

  THIS SCRIPT BEHAUPTETE BISHER (E9.1/E11 B) "the scroll-bar cursor stands on
  the reading line and never moves, dragging it moves it off the line and it
  comes back" and "air above the title (__nbTopAt) and below the last cell".
  Since E12.3 the cursor is the THUMB of a plain scroll bar in the tool column:
  it runs with the scroll share. The reading height is the grip (.nbgrip), the
  marker (.nbmap-here) and the fixed point (.nbreadfix) alone. Since E12.2
  there is no air: scrollTop 0 = the title on the line, the end = "Your own
  cell" on it.

NOT a suite: it needs a running `jupyter lab` (see lab_keys.py). Measures, with
getBoundingClientRect only:
  * UNIT — over a sweep of the whole scroll: grip middle, marker middle and the
    .nbreadfix line stand on the reading line (<= 1 px) and do not move (<= 1 px)
  * TOP — scrollTop 0 (= __nbTopAt = 0): the title mark on the line and on the
    middle of the title card that is ON the page (<= 1 px), the title lit
  * END — at the furthest scroll: the own-cell mark on the line (<= 2 px) and
    JupyterLab's add-a-cell strip level with it (<= 2 px), that mark lit
  * LIT — the lit mark is the last one whose middle reached the line (+2 px; a
    mark within 2 px + 1 px whole-pixel rounding of the line may go either way:
    17-marker reads offsetTop and Math.round(line), both integers)
  * THUMB — the thumb (.nbmap-cursor) lies inside its track (.nbsb), and its
    share (top − track top)/(track − thumb) = the scroll share ±0.01
  * the rail scrolls 1:1 with the document
  * the same after the reader adds a cell and after it is deleted
  * THUMB DRAG +/-120 px: the thumb moves 120 px (±2), the document by
    120 × span / run (±3 %), the reading unit stays on the line
  * GRIP DRAG +/-80 px (E11.4): grip, marker and .nbreadfix move together by
    80 px (±2), the document point on the line goes with it (±2); back again
  * window height from DIGICHEM_H (default 900; measured at 900 and 1100)

    python3 tests/lab_readline.py <notebook> <out.json> [skin,...] [pct,...]

Exit 1 if a criterion fails."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab_keys import fresh, CHROME, to_command
from playwright.sync_api import sync_playwright
BASE=os.environ.get("DIGICHEM_LAB_URL","http://127.0.0.1:8899"); ROOT=os.environ.get("DIGICHEM_LAB_ROOT","/home/claude/lab/root")
nb=sys.argv[1]; out=sys.argv[2]
skins=sys.argv[3].split(",") if len(sys.argv)>3 and sys.argv[3] else [None]
pcts=[int(x) for x in sys.argv[4].split(",")] if len(sys.argv)>4 else [0,25,50,100]
SC="document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer')"
AMB=3   # 2 px of the criterion + 1 px whole-pixel rounding (offsetTop, Math.round(line))
M=r"""() => {
  var h=document.getElementById('nbpanel-root'), map=h.querySelector('.nbmap');
  var sc=%s;
  var mid=function(e){ if(!e) return null; var r=e.getBoundingClientRect(); return r.height>0 ? r.top+r.height/2 : null; };
  var MK='.nbsect,.nbsubdot,.nbchapdot,.nbvizmark,.nbrail-dot,.nbcodemark,.nbendmark,.nbcellmark';
  var nodes=[].slice.call(h.querySelectorAll('.nbmap-node'));
  var y0=parseInt(h.dataset.railY0||'0',10)||0, line=map.getBoundingClientRect().top+y0;
  var vis=nodes.filter(function(n){return !n.classList.contains('nbgone');});
  // 27f: the lit mark is the LAST one whose middle has reached the line (+2 px), not the nearest
  var best=null, by=-1e9; vis.forEach(function(n){ var c=mid(n.querySelector(MK)); if(c!==null && c<=line+2 && c>=by){by=c; best=n;} });
  var hm=h.querySelector('.nbmap-here'), markerMid=mid(hm);
  var here=vis.filter(function(n){return n.classList.contains('here');})[0]||null;
  var cards=[].slice.call(document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .nbtitle-card')).filter(function(c){return c.getBoundingClientRect().height>4;});
  var cur=h.querySelector('.nbmap-cursor'), cv=cur && cur.style.visibility!=='hidden' && getComputedStyle(cur).display!=='none';
  var sb=h.querySelector(':scope > .nbsb'), sbr=sb?sb.getBoundingClientRect():null, cr=cv?cur.getBoundingClientRect():null;
  var g=h.querySelector('.nbgrip'), gv=g && g.style.visibility!=='hidden' && getComputedStyle(g).display!=='none';
  var fx=h.querySelector(':scope > .nbreadfix'), fxv=fx && fx.style.visibility!=='hidden';
  var foot=sc.querySelector('.jp-Notebook-footer');
  var t=nodes[0], c=nodes[nodes.length-1];
  var hereMk=here?mid(here.querySelector(MK)):null, bestMk=best?mid(best.querySelector(MK)):null;
  var topAt=Math.max(0, window.__nbTopAt||0), span=Math.max(1, sc.scrollHeight-sc.clientHeight-topAt);
  return {st:sc.scrollTop, max:sc.scrollHeight-sc.clientHeight, mapTop:map.scrollTop, line:line, y0:y0,
    grip: gv?mid(g):null, fix: fxv?fx.getBoundingClientRect().top:null,
    thumbTop: cr?cr.top:null, thumbH: cr?cr.height:null, thumbL: cr?cr.left:null, thumbR: cr?cr.right:null,
    sbTop: sbr?sbr.top:null, sbH: sbr?sbr.height:null, sbL: sbr?sbr.left:null, sbR: sbr?sbr.right:null,
    thumbShare: (cr && sbr && sbr.height-cr.height>0) ? (cr.top-sbr.top)/(sbr.height-cr.height) : null,
    scrollShare: Math.max(0, Math.min(1, (sc.scrollTop-topAt)/span)),
    titleMark: mid(t.querySelector('.nbsect')), titleCls:t.className,
    card: cards.length?mid(cards[0]):null, ncards:cards.length,
    cellMark: mid(c.querySelector('.nbsect')), cellCls:c.className, foot: mid(foot),
    here: here?nodes.indexOf(here):null, best: best?nodes.indexOf(best):null, hereOff: hereMk===null?null:hereMk-line, bestOff: bestMk===null?null:bestMk-line,
    last: nodes.indexOf(c), marker: markerMid===null?null:markerMid-line,
    cells: document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell').length,
    topAt: window.__nbTopAt == null ? null : window.__nbTopAt};
}""" % SC
# the document point on the reading line: the element under it and its offset
PT=r"""() => {
  var h=document.getElementById('nbpanel-root'), map=h.querySelector('.nbmap'), sc=%s;
  var line=map.getBoundingClientRect().top+(parseInt(h.dataset.railY0||'0',10)||0);
  var r=sc.getBoundingClientRect(), x=r.left+r.width/2;
  var e=document.elementFromPoint(x, line);
  if(!e || !sc.contains(e)) return null;
  var a=e; while(a.parentElement && a.getBoundingClientRect().height<8) a=a.parentElement;
  window.__rlPt=a; return a.getBoundingClientRect().top-line;
}""" % SC
PT2=r"""() => { var h=document.getElementById('nbpanel-root'), map=h.querySelector('.nbmap');
  var line=map.getBoundingClientRect().top+(parseInt(h.dataset.railY0||'0',10)||0);
  return window.__rlPt ? window.__rlPt.getBoundingClientRect().top-line : null; }"""
res={}; fails=[]
def unit(key, s, tag):
    for nm in ("grip","marker","fix"):
        v=s[nm]
        if v is None: fails.append("%s %s: %s missing (hidden?)"%(key,tag,nm)); return
        d=v if nm=="marker" else v-s["line"]
        if abs(d)>1 + (1 if nm=="marker" else 0): fails.append("%s %s: %s %.1f px from the line %.1f"%(key,tag,nm,d,s["line"]))
def sweep(pg, key, n=21):
    pg.evaluate("()=>{var s=%s; s.scrollTop=0;}"%SC); pg.wait_for_timeout(900)
    mx=pg.evaluate("()=>{var s=%s; return s.scrollHeight-s.clientHeight;}"%SC)
    seq=[]
    for k in range(n):
        y=round(mx*k/(n-1))
        pg.evaluate("(y)=>{var s=%s; s.scrollTop=y;}"%SC, y); pg.wait_for_timeout(700)
        seq.append(pg.evaluate(M))
    pg.wait_for_timeout(1200); pg.evaluate("()=>{var s=%s; s.scrollTop=s.scrollHeight;}"%SC); pg.wait_for_timeout(1200)
    seq.append(pg.evaluate(M))
    res[key]=seq
    s0=seq[0]; sN=seq[-1]
    # TOP (E12.2): no air, scrollTop 0 is the title on the line
    if s0["topAt"] not in (0, None): fails.append("%s: __nbTopAt %s, want 0 (E12.2: no air)"%(key,s0["topAt"]))
    if s0["st"]!=0: fails.append("%s: top scrollTop %s"%(key,s0["st"]))
    if s0["titleMark"] is None or abs(s0["titleMark"]-s0["line"])>1: fails.append("%s: at 0 the title mark is %s, line %.1f"%(key,s0["titleMark"],s0["line"]))
    if s0["card"] is None or s0["titleMark"] is None or abs(s0["titleMark"]-s0["card"])>1: fails.append("%s: at 0 title mark %s, card middle %s"%(key,s0["titleMark"],s0["card"]))
    if s0["here"]!=0: fails.append("%s: at 0 lit %s, want the title 0"%(key,s0["here"]))
    # END (E12.2): your own cell on the line, the add-a-cell strip level with it
    if sN["cellMark"] is None or abs(sN["cellMark"]-sN["line"])>2: fails.append("%s: own-cell mark %s, line %.1f at the end"%(key,sN["cellMark"],sN["line"]))
    if sN["foot"] is None or sN["cellMark"] is None or abs(sN["foot"]-sN["cellMark"])>2: fails.append("%s: add-a-cell strip %s, own-cell mark %s at the end"%(key,sN["foot"],sN["cellMark"]))
    if sN["here"]!=sN["last"]: fails.append("%s: at the end lit %s, want your own cell %s"%(key,sN["here"],sN["last"]))
    # UNIT: grip, marker, fixed point on the line, never moving
    for s in seq: unit(key, s, "st %.0f"%s["st"])
    for nm in ("grip","fix"):
        v=[s[nm] for s in seq if s[nm] is not None]
        if v and max(v)-min(v)>1: fails.append("%s: %s moved %.1f..%.1f"%(key,nm,min(v),max(v)))
    for s in seq:
        if abs(s["mapTop"]-s["st"])>1: fails.append("%s: rail %.0f vs document %.0f"%(key,s["mapTop"],s["st"])); break
    # LIT
    for s in seq:
        if s["here"]!=s["best"] and not (s["hereOff"] is not None and abs(s["hereOff"])<=AMB):
            fails.append("%s st %.0f: lit %s (%s), last mark on the line is %s (%s)"%(key,s["st"],s["here"],s["hereOff"],s["best"],s["bestOff"])); break
    # THUMB (E12.3)
    for s in seq:
        if s["thumbShare"] is None: fails.append("%s st %.0f: no thumb / track"%(key,s["st"])); break
        if s["thumbTop"] < s["sbTop"]-1 or s["thumbTop"]+s["thumbH"] > s["sbTop"]+s["sbH"]+1 or s["thumbL"] < s["sbL"]-12 or s["thumbR"] > s["sbR"]+12:
            fails.append("%s st %.0f: thumb %.0f+%.0f outside its track %.0f+%.0f"%(key,s["st"],s["thumbTop"],s["thumbH"],s["sbTop"],s["sbH"])); break
        if abs(s["thumbShare"]-s["scrollShare"])>0.01:
            fails.append("%s st %.0f: thumb share %.4f, scroll share %.4f"%(key,s["st"],s["thumbShare"],s["scrollShare"])); break
    res[key+"#dev"]=max([abs(x["marker"]) for x in seq if x.get("marker") is not None] or [0])
    res[key+"#share"]=max([abs(x["thumbShare"]-x["scrollShare"]) for x in seq if x.get("thumbShare") is not None] or [9])
    return seq
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME)
    ctx,pg,errs=fresh(b,BASE,nb,ROOT)
    pg.set_viewport_size({"width": 1400, "height": int(os.environ.get("DIGICHEM_H", "900"))}); pg.wait_for_timeout(1500)
    try: pg.click(".jp-toast-buttonBar button:has-text('No')", timeout=1500)
    except Exception: pass
    pg.evaluate("()=>{try{localStorage.removeItem('digichemjn.readline.v1');}catch(e){}}")
    for sk in skins:
        if sk:
            pg.evaluate("(s)=>{ window.__nbStore.set('digichemjn.skin.v1', s); window.__nbApplySkin && window.__nbApplySkin(); }", sk)
            pg.wait_for_timeout(1500)
        for pct in pcts:
            pg.evaluate("(p)=>window.__nbSetGui(p)", pct); pg.wait_for_timeout(1500)
            sweep(pg, "%s/%d"%(sk,pct))
    # THUMB DRAG: a real mouse, both directions, from the middle of the scroll
    pg.evaluate("(p)=>window.__nbSetGui(p)", 50); pg.wait_for_timeout(1200)
    res["drag"]=[]
    for dy in (120, -120):
        pg.evaluate("()=>{var s=%s; s.scrollTop=Math.round((s.scrollHeight-s.clientHeight)/2);}"%SC); pg.wait_for_timeout(1200)
        b0=pg.evaluate(M)
        c=[(b0["thumbL"]+b0["thumbR"])/2, b0["thumbTop"]+b0["thumbH"]/2]
        pg.mouse.move(c[0],c[1]); pg.mouse.down()
        for k in range(1,9): pg.mouse.move(c[0], c[1]+dy*k/8); pg.wait_for_timeout(30)
        pg.mouse.up(); pg.wait_for_timeout(1200)
        a=pg.evaluate(M)
        run=b0["sbH"]-b0["thumbH"]; span=b0["max"]-(b0["topAt"] or 0)
        want=dy*span/run if run>0 else None
        d={"dy":dy,"before":b0["st"],"after":a["st"],"want":want,"thumb":a["thumbTop"]-b0["thumbTop"]}
        res["drag"].append(d)
        if want is None or abs((a["st"]-b0["st"])-want)>abs(want)*0.03+2: fails.append("thumb drag %+d: document %d -> %d, want %+.0f"%(dy,b0["st"],a["st"],want or 0))
        if abs(d["thumb"]-dy)>2: fails.append("thumb drag %+d: thumb moved %.1f"%(dy,d["thumb"]))
        unit("thumb drag %+d"%dy, a, "after release")
    # GRIP DRAG (E11.4): the reading height moves, the document point goes with it
    res["grip"]=[]
    pg.evaluate("()=>{var s=%s; s.scrollTop=Math.round((s.scrollHeight-s.clientHeight)/3);}"%SC); pg.wait_for_timeout(1200)
    for dy in (80, -80):
        b0=pg.evaluate(M); p0=pg.evaluate(PT)
        gx=pg.evaluate("()=>{var r=document.querySelector('#nbpanel-root .nbgrip').getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2];}")
        pg.mouse.move(gx[0],gx[1]); pg.mouse.down()
        for k in range(1,11): pg.mouse.move(gx[0], gx[1]+dy*k/10); pg.wait_for_timeout(40)
        pg.mouse.up(); pg.wait_for_timeout(1500)
        a=pg.evaluate(M); p1=pg.evaluate(PT2)
        d={"dy":dy,"line":a["line"]-b0["line"],"grip":(a["grip"] or 0)-(b0["grip"] or 0),"fix":(a["fix"] or 0)-(b0["fix"] or 0),
           "marker":a["marker"],"pt":[p0,p1]}
        res["grip"].append(d)
        for nm in ("line","grip","fix"):
            if abs(d[nm]-dy)>2: fails.append("grip drag %+d: %s moved %.1f"%(dy,nm,d[nm]))
        unit("grip drag %+d"%dy, a, "after release")
        if p0 is None or p1 is None or abs(p1-p0)>2: fails.append("grip drag %+d: document point on the line %s -> %s"%(dy,p0,p1))
    pg.evaluate("()=>{try{localStorage.removeItem('digichemjn.readline.v1');}catch(e){}}")
    # the reader adds a cell of their own, then deletes it
    pg.evaluate("(p)=>window.__nbSetGui(p)", 50); pg.wait_for_timeout(1200)
    # through JupyterLab's own toolbar button — command-mode `B` is held back
    # by the toolkit (D) until the reader has typed, so it would add nothing
    pg.click(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Toolbar [data-command='notebook:insert-cell-below']")
    pg.wait_for_timeout(1500); pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
    sweep(pg, "added", 9)
    if res["added"][-1]["cells"]!=3: fails.append("added: %d cells, expected 3"%res["added"][-1]["cells"])
    pg.screenshot(path=out.replace(".json","_added.png"))
    pg.evaluate("()=>{ var c=document.querySelectorAll('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-Cell'); c[c.length-1].focus(); }")
    pg.click(".jp-NotebookPanel:not(.lm-mod-hidden) .jp-Toolbar [data-command='notebook:cut-cell']"); pg.wait_for_timeout(1500)
    sweep(pg, "deleted", 9)
    if res["deleted"][-1]["cells"]!=2: fails.append("deleted: %d cells, expected 2"%res["deleted"][-1]["cells"])
    res["errs"]=errs
    if errs: fails.append("console: %s"%errs[:3])
json.dump(res,open(out,"w"),indent=1)
print("thumb drag", res.get("drag")); print("grip drag", res.get("grip"))
for k,v in res.items():
    if k in ("errs","drag","grip") or "#" in k: continue
    s0=v[0]; sN=v[-1]
    print("%-12s line %.1f | top: title %.1f card %.1f | end: max %d own-cell %.1f foot %.1f | cells %d | marker-line max %.1f | thumb-scroll share max %.4f"%(k,s0["line"],s0["titleMark"] or -1,s0["card"] or -1,
          sN["max"],sN["cellMark"] or -1,sN["foot"] or -1,sN["cells"],res[k+"#dev"],res[k+"#share"]))
for f in fails: print("FAIL", f)
print("READLINE OK" if not fails else "READLINE: %d failures"%len(fails))
sys.exit(1 if fails else 0)
