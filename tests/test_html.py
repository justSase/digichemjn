"""Open the HTML edition in a real browser and drive it: figures draw, the gate
holds, a right answer fills the timeline, the panel follows."""
import sys, json
from playwright.sync_api import sync_playwright
PATH = "file:///home/claude/work/html/Complex_Numbers.html"
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.on("console", lambda m: errs.append("console.%s: %s" % (m.type, m.text)) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("pageerror: %s" % e))
    pg.goto(PATH); pg.wait_for_timeout(900)

    info = pg.evaluate("""() => ({
        figs: document.querySelectorAll('.nbfig').length,
        canvases: [].slice.call(document.querySelectorAll('.nbcanvas-wrap.js')).length,
        answers: document.querySelectorAll('.nbans').length,
        locks: document.querySelectorAll('.nblock').length,
        panel: !!document.querySelector('#nbpanel-root .nbmap'),
        dots: document.querySelectorAll('#nbpanel-root .nbrail-dot').length,
        fill: document.querySelector('.nbmap-fill').style.width,
        details: document.querySelectorAll('details').length,
        imgs: document.querySelectorAll('img').length
    })""")
    print("page:", info)
    if info["figs"] < 10: errs.append("only %d figures" % info["figs"])
    if info["dots"] < 8: errs.append("panel has %d dots" % info["dots"])
    if info["locks"] < 6: errs.append("only %d exercises are locked at the start" % info["locks"])

    # the canvas must actually be painted, not blank
    painted = pg.evaluate("""() => {
        var out = [];
        document.querySelectorAll('.nbcanvas-wrap.js canvas').forEach(function(c){
            var g = c.getContext('2d');
            var d = g.getImageData(0, 0, c.width, c.height).data;
            var n = 0;
            for (var i = 3; i < d.length; i += 4000) if (d[i] > 0) n++;
            out.push(n);
        });
        return out;
    }""")
    print("painted samples per canvas:", painted)
    if any(n < 5 for n in painted): errs.append("a canvas figure is blank: %s" % painted)

    # answer exercise 1 correctly: q is in NBDATA
    q = pg.evaluate("() => window.NBDATA.tv.q")
    import math
    root = math.sqrt(q)
    pg.evaluate("""(r) => {
        var box = document.querySelector(".nbans[data-task='t1']");
        var ins = box.querySelectorAll('input[type=number]');
        ins[0].value = '0'; ins[1].value = String(r);
        box.querySelector('[data-check]').click();
    }""", round(root, 6))
    pg.wait_for_timeout(400)
    after = pg.evaluate("""() => ({
        msg: (document.querySelector(".nbans[data-task='t1'] .nbmsg") || {}).className,
        text: (document.querySelector(".nbans[data-task='t1'] .nbmsg") || {}).textContent,
        dot1: document.querySelector("#nbpanel-root .nbmap-node.task .nbrail-dot").className,
        fill: document.querySelector('.nbmap-fill').style.width,
        locks: document.querySelectorAll('.nblock').length,
        stored: localStorage.getItem('digichemjn.progress.v1')
    })""")
    print("after answering exercise 1:", {k: (v[:90] if isinstance(v, str) else v) for k, v in after.items()})
    if "ok" not in (after["msg"] or ""): errs.append("a correct answer was not accepted")
    if "st-ans" not in (after["dot1"] or ""): errs.append("the panel did not mark exercise 1")
    if after["locks"] >= info["locks"]: errs.append("exercise 2 did not unlock")
    if not after["stored"] or '"a":[1,' not in after["stored"].replace(" ", ""):
        errs.append("the series record was not written: %s" % after["stored"])

    # a wrong answer must be rejected and must not fill anything
    pg.evaluate("""() => {
        var box = document.querySelector(".nbans[data-task='t3']");
        if (!box) return;
        box.querySelectorAll('input[type=number]').forEach(function(i){ i.value = '1'; });
        box.querySelector('[data-check]').click();
    }""")
    pg.wait_for_timeout(300)
    wrong = pg.evaluate("""() => (document.querySelector(".nbans[data-task='t3'] .nbmsg")||{}).className""")
    print("wrong answer:", wrong)
    if wrong and "no" not in wrong: errs.append("a wrong answer was accepted")

    pg.screenshot(path="/home/claude/work/html/shot_top.png", clip={"x":0,"y":0,"width":1280,"height":900})
    pg.evaluate("""() => { document.querySelectorAll('details.acc-chapter').forEach(function(d,i){ if(i===0) d.open = true; });
        var el = document.getElementById('ch2'); if (el) el.scrollIntoView(); }""")
    pg.wait_for_timeout(600)
    pg.screenshot(path="/home/claude/work/html/shot_ch.png")
    b.close()
for e in errs[:12]: print("  !!", e)
print("\n" + ("HTML EDITION OK" if not errs else "FAILURES: %d" % len(errs)))
sys.exit(1 if errs else 0)
