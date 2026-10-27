"""E35 · CSS — Werkstatt CSS, 19.10. (Nutzer: „Die Vorschau soll auch den digi-Stil haben, es soll alles bündig aussehen
… auch bei unterschiedlichen Stilen, hell/dunkel sollen alle Flächen entsprechend eingefärbt werden … die Textur soll wie
auf der Webseite aussehen (Sterne), nicht die Punkte und der goldene Schein oben“; Auftrag plan/AUFTRAG.md C1–C3).
Im echten JupyterLab, 1400 × 900, frisches Profil je Zeile, Run All (+ Play):

    python3 tests/regress/css_e35.py [notebook.ipynb] [--rows C1,C2,C3] [--skins digi,minimal,cyber,fairy]
                                     [--themes dark,light] [--shots DIR] [--json out.json] [--js]

  C1   digi dunkel/hell: der Grund des Dokuments (Scroller) ist #04050b / #f6f7fb, sein Bild ist GENAU EINE SVG-Kachel
       (data:, 420 × 420) — kein Verlauf (kein Punktraster, kein Gold-Schein); die Kachel enthält die 68 Sterne der
       Webseite (stars() unten: Park-Miller Seed 7 — Ort, Radius 0,35–1,65, Deckkraft dunkel 0,20–0,65 in #cfd6ff,
       hell ≤ 0,15 in #3a4060), Stern für Stern gleich, gemalt in Originalgröße (background-size 420px 420px).
  C1s  ruhig beim Scrollen: background-attachment ist weder fixed noch local, und ein Streifen Grund neben dem Text
       ist nach 300 px Scrollen pixelgleich.
  C2   je Stil × hell/dunkel: jede sichtbare Fläche (Hintergrundfarbe, jeder Verlaufsstopp, ::before/::after) UND jeder
       Ring/Hof (box-shadow) ist eine Farbe der Palette dieses Stils ± 2 je Kanal (Transparenz erlaubt; Weiß nur bis
       Alpha 0,2; dunkle Schlagschatten erlaubt: alle Kanäle ≤ 45, Alpha ≤ 0,8) — auf dem Cover (nur .nbcover-out: es liegt über
       allem), im Dokument von oben
       bis unten (Schritte zu 800 px) und in den Einstellungen ⚙. Plots sind Bilder des Kernels (nicht gezählt).
  C2k  dabei Kontrast ≥ 4,5 : 1 für jeden sichtbaren Text (Dokument oben, ⚙) — wie css_e34 R4. Auf dem Cover nur berichtet
       (C2c, INFO): dort zählt R4 auch die eingeklappten Ziele und die absichtlich blassen gesperrten Kapitelnamen, in jedem
       Stil, auch minimal (gemessen v1.80) — offen, eigener Punkt.
  C3   kein Aufblitzen (Lab dunkel, frisches Profil): ein Bild je Malvorgang (CDP-Screencast) ab dem Moment, in dem der
       Lauf die gespeicherte Vorschau (.nbstill, Python) ersetzt (+ 0,2 s Malverzug), bis 3 s nach body.nbskin-digi: in keinem Bild eine Fläche
       (Block 24 × 24 px, ≥ 90 % seiner Pixel) heller als #2a2f4a im Panel. Die Bilder davor (gespeicherte Vorschau =
       Python P1) nur berichtet: C3s (INFO). C3a = derselbe Maßstab für die Bilder, bevor das Skript body.nb-dc-active
       setzt — das ist der Teil, den CSS allein trägt. Gemessen v1.80: das Skript setzt nb-dc-active ~3 s VOR Stil und
       hell/dunkel (15-rail-theme); in dieser Lücke gelten die Werte von minimal hell (weiße Ladeansicht). Sie schließt J1
       (JS) — darum zählt C3 (alle Bilder) erst mit --js.
  C3d  das erste Bild mit unserem Inhalt ist schon digi (Grund ∈ #04050b/#05060c/#0b0e1c ± 3) — braucht die JS-Hälfte
       (J1: Ladeansicht/Klassen vor dem ersten Malen); ohne --js nur berichtet (INFO), mit --js gezählt.
Gegenprobe v1.80 (cecc1c32): Chronik. exit 0 = REGRESS-CSS-E35 OK."""
import sys, os, json, time, shutil, tempfile, base64, io, re, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from playwright.sync_api import sync_playwright
import css_e34 as E

A = sys.argv[1:]
def opt(k, d=None):
    return A[A.index(k) + 1] if k in A else d
ROWS = opt("--rows", "C1,C2,C3").split(",")
SKINS = opt("--skins", "digi,minimal,cyber,fairy").split(",")
THEMES = opt("--themes", "dark,light").split(",")
SHOTS, JOUT, JS = opt("--shots"), opt("--json"), "--js" in A
W, H = 1400, 900

def stars(amin, amax, W=420, seed=7):
    """Der Sternenhimmel der digi-Webseite: 1 Stern je 2 600 px², je Stern x, y, Radius, Deckkraft aus Park-Miller."""
    s = [seed]
    def rnd():
        s[0] = s[0] * 16807 % 2147483647; return s[0] / 2147483647
    n = round(W * W / 2600)
    return [(rnd() * W, rnd() * W, 0.35 + rnd() * 1.30, amin + rnd() * (amax - amin)) for _ in range(n)]

def tile(fill, amin, amax, W=420):
    """Die SVG-Kachel, wie sie in 07-skins.css steht (url-kodiert: # → %23)."""
    f = lambda v: ("%.2f" % v).lstrip("0") if v < 1 else ("%.2f" % v).rstrip("0").rstrip(".")
    c = "".join("<circle cx='%d' cy='%d' r='%s' fill-opacity='%s'/>" % (round(x), round(y), f(r), f(a)) for x, y, r, a in stars(amin, amax, W))
    return "<svg xmlns='http://www.w3.org/2000/svg' width='%d' height='%d'><g fill='%s'>%s</g></svg>" % (W, W, fill, c)

STAR = {"dark": ("#cfd6ff", .20, .65, "#04050b"), "light": ("#3a4060", .05, .15, "#f6f7fb")}

# Die Palette je Stil × hell/dunkel: die Werte der Stile (07-skins, 09, 10, 12-k3, 14-e7 --dg-*); minimal = das Dunkel-/
# Hell-Thema des Toolkits selbst (gemessen v1.80, die Referenz, gegen die die anderen Stile abgegrenzt werden).
PAL = {
 ("digi", "dark"): "#04050b #05060c #0b0e1c #10142a #1d2342 #2a3050 #e9ecf6 #c3c9de #8a91aa #3a4166 #ffd36b #ffb84a #7fb4ff #ff7bd5 #6be3a0 #ff6b7a",
 ("digi", "light"): "#f6f7fb #f5f6fa #ffffff #f7f8fc #dde1ec #e3e6ef #d5d9e6 #b5bbcc #141826 #454b63 #5b6178 #9a6b00 #f2b426 #e8a817 #d9a21c "
                    "#ffd36b #ffb84a #2a5bc8 #7fb4ff #c2338f #d23aa0 #ff7bd5 #1a7a4c #b3263a",
 ("cyber", "dark"): "#0c1020 #0e142a #12162a #141a2e #1b1330 #0f1324 #2b2154 #3a2a6b #241a52 #d8e6ff #8fa8d8 #00e5ff #ff2fd0 #ff4fd8 #3dffb0 #ff6b93 #ffe066 #c9f7ff #9ff4ff",
 ("cyber", "light"): "#f3f1fb #f2eeff #eef2ff #fbeeff #ffffff #d9cdf5 #9b7fe0 #7c5cd6 #3a2a6b #241a52 #231a3d #54437e #00647f #006d8a #0096be #00e5ff "
                     "#a3128c #ff2fd0 #ff4fd8 #086643 #a8183f #8a5b00 #783cc8",
 ("fairy", "dark"): "#1c1629 #241828 #191a2e #1b2033 #7b32c2 #a8306f #1b1426 #241c33 #1f1830 #3a2d52 #4a3a63 #e6d9f7 #b3a2c8 #c79cff #b06cff #e6a0ff #ff8fc4 #ff9fd0 #e3649f #82e3b8 #ff94b4 #ffd38a #f0dcff #fff7fb",
 ("fairy", "light"): "#fbf6ff #fdf0f7 #f3efff #fdf8ff #fbf3ff #f2f7ff #fbf5ff #ffffff #ead9fa #e2cdf5 #c9a8e8 #a48fc4 #4a3a63 #655377 #7b32c2 #8a3fd1 #b06cff "
                     "#c85aaa #a8306f #ff8fc4 #e3649f #1d6645 #a3264f #8a5b00",
 ("minimal", "dark"): "#111111 #111820 #171c22 #1b222b #1d2228 #1f252c #222a33 #242b32 #243637 #262c33 #2a323a #39424d #39444e #3b444d #3b4652 #4b5763 "
                      "#5d6f82 #6c7885 #8a96a3 #9fb0bd #b9c4cf #dbe2e9 #8fc7e8 #7fb8dc #4fd39b #4cc38a #3fa877 #1e7a4c #6b3fd1 #c7a8ff #b896ff #a783e8 #3d3119 #e0a500 #3d1f1b #e05a48 #f2837a #ffffff #c07a12 #7b4fb3 #6fb6de #29343d",
 ("minimal", "light"): "#ffffff #f8fafb #f6f8fa #eceff2 #ecf6f1 #dfe6ec #d7dfe7 #d3dde6 #cbd5de #c3ced8 #9aaabb #8a96a3 #8a94a0 #8894a0 #767f8a #55636f #4d5964 "
                       "#46535f #33475b #1f2933 #0d63e0 #1d5c8a #2c6e91 #3fa877 #18693f #1e7a4c #6b3fd1 #8b4ff2 #fdf0d8 #8a5b00 #fbe0dd #a5291b #b42318 #d9a53a #c07a12 #7b4fb3 #2f8f63 #7b3fe4 #ebf0f4",
}

COLLECT = r"""([pal, only]) => {""" + E.COLOR_LIB + r"""
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), root = document.getElementById('nbpanel-root');
  var allow = pal.map(norm), bad = {}, n = 0;
  var inPal = function(c){ return allow.some(function(a){ return Math.abs(a[0]-c[0]) <= 2 && Math.abs(a[1]-c[1]) <= 2 && Math.abs(a[2]-c[2]) <= 2; }); };
  var ok = function(c, shadow){ if (!c || c[3] < .01) return true;
    if (c[0] > 252 && c[1] > 252 && c[2] > 252 && c[3] <= .2) return true;             // white: only as a line
    if (shadow && Math.max(c[0], c[1], c[2]) <= 45 && c[3] <= .8) return true;           // a dark drop shadow
    return inPal(c); };
  var els = [];
  (only ? [].slice.call(document.querySelectorAll(only)) : [P, root].concat([].slice.call(document.querySelectorAll('.nbhelp,.nbtip,#nbload'))))
    .forEach(function(sc){ if (sc) els = els.concat([sc], [].slice.call(sc.querySelectorAll('*'))); });
  var shc = function(v){ return v && v !== 'none' ? stops(v).map(norm) : []; };
  els.forEach(function(e){ if (e.closest('svg,mjx-container,.jp-InputArea,.cm-editor,.jp-Toolbar,.jp-NotebookPanel-toolbar,.jp-RenderedImage')) return;
    var r = e.getBoundingClientRect(); if (r.width < 2 || r.height < 2 || r.bottom < 0 || r.top > innerHeight || r.right < 0 || r.left > innerWidth) return;
    var s = getComputedStyle(e); if (s.visibility === 'hidden' || s.display === 'none' || parseFloat(s.opacity) === 0) return;
    var cs = [[norm(s.backgroundColor), 0]].concat(s.backgroundImage !== 'none' ? stops(s.backgroundImage).map(function(c){ return [norm(c), 0]; }) : [])
             .concat(shc(s.boxShadow).map(function(c){ return [c, 1]; }));
    ['::before', '::after'].forEach(function(ps){ var q = getComputedStyle(e, ps); if (q.content === 'none' || q.display === 'none') return;
      cs.push([norm(q.backgroundColor), 0]); if (q.backgroundImage !== 'none') stops(q.backgroundImage).forEach(function(c){ cs.push([norm(c), 0]); });
      shc(q.boxShadow).forEach(function(c){ cs.push([c, 1]); }); });
    cs.forEach(function(p){ var c = p[0]; n++; if (ok(c, p[1])) return;
      var k = e.tagName + '.' + String(e.className).split(' ').filter(Boolean).slice(0, 2).join('.') + (p[1] ? ' ring ' : ' ') + hex(c) + (c[3] < 1 ? '/' + Math.round(c[3]*100) / 100 : '');
      bad[k] = (bad[k] || 0) + 1; }); });
  var list = Object.keys(bad).map(function(k){ return [k, bad[k]]; }).sort(function(a, b){ return b[1] - a[1]; });
  return {n: n, bad: list.length, list: list.slice(0, 16)}; }"""

TEX = r"""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), sc = P && P.querySelector('.jp-WindowedPanel-outer');
  if (!sc) return null; var s = getComputedStyle(sc), gr = [];
  // every gradient on the way from the scroller to the panel (the gold light sat on the scroller)
  for (var a = sc; a && a !== P.parentElement; a = a.parentElement) { var b = getComputedStyle(a).backgroundImage; if (/gradient/.test(b)) gr.push(a.className.split(' ')[0] + ': ' + b.slice(0, 60)); }
  return {bg: s.backgroundColor, img: s.backgroundImage, size: s.backgroundSize, att: s.backgroundAttachment, grads: gr,
          r: sc.getBoundingClientRect().toJSON(), top: sc.scrollTop, h: sc.scrollHeight}; }"""

def judge_tile(img, theme):
    fill, amin, amax, _ = STAR[theme]
    urls = re.findall(r'url\("?(data:image/svg\+xml[^")]*)"?\)', img)
    if len(urls) != 1 or "gradient" in img: return False, "image %r" % img[:90]
    d = urls[0].split(",", 1)[1]
    svg = base64.b64decode(d).decode() if ";base64" in urls[0] else urllib.parse.unquote(d)
    cs = re.findall(r"<circle cx='([\d.]+)' cy='([\d.]+)' r='([\d.]+)' fill-opacity='([\d.]+)'", svg)
    want = stars(amin, amax)
    size = re.search(r"width='(\d+)' height='(\d+)'", svg)
    same = len(cs) == len(want) and all(abs(float(a) - x) <= .5 and abs(float(b) - y) <= .5 and abs(float(r) - rr) <= .006 and abs(float(o) - oo) <= .006
                                        for (a, b, r, o), (x, y, rr, oo) in zip(cs, want))
    rs = [float(c[2]) for c in cs]; os_ = [float(c[3]) for c in cs]
    ok = (same and ("fill='%s'" % fill) in svg and size and size.groups() == ("420", "420")
          and min(rs) >= .35 - .006 and max(rs) <= 1.65 + .006 and min(os_) >= amin - .006 and max(os_) <= amax + .006)
    return ok, "%d stars (want %d, same as stars(): %s) · fill %s · r %.2f–%.2f · alpha %.2f–%.2f · tile %s" % (
        len(cs), len(want), same, fill if ("fill='%s'" % fill) in svg else "OTHER", min(rs or [0]), max(rs or [0]),
        min(os_ or [0]), max(os_ or [0]), size.groups() if size else None)

def open_lab(b, base, items, theme):
    ctx = b.new_context(viewport={"width": W, "height": H}, color_scheme=theme)
    if items:
        ctx.add_init_script("try{if(!sessionStorage.getItem('__e35')){var o=%s;for(var k in o)localStorage.setItem(k,o[k]);"
                            "sessionStorage.setItem('__e35','1');}}catch(e){}" % json.dumps(items))
    pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
    pg.goto(base + "/lab/tree/v.ipynb?reset")
    pg.wait_for_selector(".jp-NotebookPanel .jp-Cell", state="attached", timeout=180000)
    pg.wait_for_timeout(3000)
    return ctx, pg, errs

def scroll_to(pg, y):
    return pg.evaluate("""(y) => { var sc = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer');
      if (!sc) return -1; sc.scrollTop = y; return sc.scrollTop; }""", y)

def lum(c):
    f = lambda v: v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(c[0] / 255) + .7152 * f(c[1] / 255) + .0722 * f(c[2] / 255)

def flash_frames(pg, cdp, box, until_s=30.0):
    """Every painted frame from now (CDP screencast) until 3 s after body.nbskin-digi (at most until_s)."""
    import numpy as np
    from PIL import Image
    frames = []
    # the body's classes over time, in the page's own clock (Date.now), to know which frames came before the script
    pg.evaluate("""() => { window.__e35c = [[Date.now() / 1000, document.body.className]];
      new MutationObserver(function(){ window.__e35c.push([Date.now() / 1000, document.body.className]); })
        .observe(document.body, {attributes: true, attributeFilter: ['class']}); }""")
    def on(ev):
        frames.append((ev.get("metadata", {}).get("timestamp") or time.time(), ev["data"]))
        try: cdp.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]})
        except Exception: pass
    cdp.on("Page.screencastFrame", on)
    cdp.send("Page.startScreencast", {"format": "png", "everyNthFrame": 1})
    t0 = pg.evaluate("() => Date.now() / 1000"); E.palette(pg, "Run All Cells"); seen = gone = None; tw = time.time() - t0
    while time.time() - tw - t0 < until_s:
        pg.wait_for_timeout(50)
        st = pg.evaluate("() => [document.body.classList.contains('nbskin-digi'), !!document.querySelector('.jp-NotebookPanel .nbstill')]")
        now = time.time() - tw
        if gone is None and not st[1]: gone = now                         # the stored preview (Python) is replaced by the run
        if seen is None and st[0]: seen = now
        if seen and now - seen > 3: break
    cdp.send("Page.stopScreencast")
    cl = pg.evaluate("() => window.__e35c")
    def cls_at(t):
        c = cl[0][1]
        for tt, cc in cl:
            if tt <= t: c = cc
        return c
    thr = lum((0x2a, 0x2f, 0x4a)); out = []
    x0, y0, x1, y1 = [int(v) for v in box]
    for t, data in frames:
        im = Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB")
        if im.size != (W, H): im = im.resize((W, H))
        a = np.asarray(im.crop((x0, y0, x1, y1))).astype(float) / 255
        f = np.where(a <= .03928, a / 12.92, ((a + .055) / 1.055) ** 2.4)
        L = .2126 * f[..., 0] + .7152 * f[..., 1] + .0722 * f[..., 2]
        hb = (L.shape[0] // 24) * 24; wb = (L.shape[1] // 24) * 24
        bl = (L[:hb, :wb] > thr).reshape(hb // 24, 24, wb // 24, 24).mean(axis=(1, 3))
        px = np.asarray(im.crop((x0, y0, x1, y1))).reshape(-1, 3)
        vals, cnt = np.unique(px // 1, axis=0, return_counts=True)
        dom = vals[cnt.argmax()]
        out.append({"t": round(t - t0, 2), "bright": int((bl >= .9).sum()), "dom": "#%02x%02x%02x" % tuple(int(v) for v in dom), "img": im,
                    "active": "nb-dc-active" in cls_at(t).split()})
    return out, (round(seen - t0, 2) if seen else None), (round(gone - t0, 2) if gone else None)

def main():
    import nbpick
    src = os.path.abspath(nbpick.from_argv(sys.argv))
    nid = (json.load(open(src, encoding="utf-8")).get("metadata", {}).get("digichemjn", {}) or {}).get("id") or "vorlage"
    rows = []
    def row(name, ok, detail="", info=False):
        rows.append((name, bool(ok) or info, detail)); print("%s  %-44s %s" % ("INFO" if info else ("PASS" if ok else "FAIL"), name, detail), flush=True)
    def shot(pg, name):
        if SHOTS: os.makedirs(SHOTS, exist_ok=True); pg.screenshot(path=os.path.join(SHOTS, name))
    with sync_playwright() as P:
        b = P.chromium.launch(executable_path=E.CHROME)
        for theme in THEMES:
            tmp = tempfile.mkdtemp(prefix="e35nb_"); shutil.copy(src, os.path.join(tmp, "v.ipynb"))
            srv, base = E.start_server("lab", tmp, theme)
            try:
                for sk in SKINS:
                    tag = "%s %s" % (sk, theme)
                    want_c1 = "C1" in ROWS and sk == "digi"
                    if not ("C2" in ROWS or want_c1): continue
                    items = {"digichemjn.theme.v1." + nid: theme, "digichemjn.skin.v1." + nid: sk}
                    ctx, pg, errs = open_lab(b, base, items, theme)
                    st = E.run_and_play(pg)
                    cls = pg.evaluate("() => document.body.className")
                    want_cls = ("nbskin-" + sk) if sk != "minimal" else None
                    have = (want_cls in cls.split()) if want_cls else not re.search(r"\bnbskin-", cls)
                    if st != "ok" or not have or (("nbdark" in cls.split()) != (theme == "dark")):
                        row("C2 surfaces in the palette · " + tag, False, "BAD %s · body %s · errors %s" % (st, cls, errs[:2])); ctx.close(); continue
                    pal = PAL[(sk, theme)].split()
                    views = []
                    if "C2" in ROWS:
                        views.append(("cover", pg.evaluate(COLLECT, [pal, ".nbcover-out"])))
                        shot(pg, "E35-%s-%s-cover.png" % (sk, theme))
                        k0 = pg.evaluate(E.MEASURE, ".nbcover-out")["r4"]
                    pl = E.play(pg); pg.wait_for_timeout(1200)
                    if pl != "play":
                        row("C2 surfaces in the palette · " + tag, False, "BAD Play: %s" % pl); ctx.close(); continue
                    shot(pg, "E35-%s-%s.png" % (sk, theme))
                    if want_c1:
                        tx = pg.evaluate(TEX); fill, amin, amax, ground = STAR[theme]
                        gok = tx and max(abs(a - b_) for a, b_ in zip(E_rgb(tx["bg"]), hexrgb(ground))) <= 1
                        tok, tdet = judge_tile(tx["img"] if tx else "", theme)
                        row("C1 starry sky, no dots, no gold light · " + tag, bool(gok and tok and not tx["grads"] and tx["size"] == "420px 420px"),
                            "ground %s (want %s) · %s · gradients %s · size %s" % (tx and tx["bg"], ground, tdet, tx and tx["grads"], tx and tx["size"]))
                        # steady while scrolling: a strip of ground beside the text, before and after 300 px
                        y = scroll_to(pg, 300); pg.wait_for_timeout(700)
                        clip = strip(pg); why = clip.get("bad") if clip else "no scroller"
                        if why: clip = None
                        a1 = pg.screenshot(clip=clip) if clip else None
                        scroll_to(pg, y + 300); pg.wait_for_timeout(900)
                        a2 = pg.screenshot(clip=clip) if clip else None
                        c2 = strip(pg)
                        if clip and c2 != clip: why, clip = "strip not clear after scrolling: %s" % (c2,), None
                        att = tx["att"] if tx else "?"
                        row("C1s steady while scrolling · " + tag, bool(clip) and a1 == a2 and att not in ("fixed", "local"),
                            "attachment %s · strip %s · pixel-equal after 300 px: %s" % (att, clip and {k: int(v) for k, v in clip.items()} or ("BAD no clear strip: %s" % (why,)), a1 == a2))
                        scroll_to(pg, 0); pg.wait_for_timeout(600)
                    if "C2" in ROWS:
                        k1 = pg.evaluate(E.MEASURE, None)["r4"]
                        views.append(("top", pg.evaluate(COLLECT, [pal, None])))
                        h = pg.evaluate("() => { var sc = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden) .jp-WindowedPanel-outer'); return sc ? sc.scrollHeight : 0; }")
                        y = 800
                        while y < h:
                            scroll_to(pg, y); pg.wait_for_timeout(700)
                            views.append(("y%d" % y, pg.evaluate(COLLECT, [pal, None]))); y += 800
                        shot(pg, "E35-%s-%s-end.png" % (sk, theme))
                        g = pg.evaluate("() => { var g = document.querySelector('#nbpanel-root .nbbtn.nbgear'); if (!g) return false; g.click(); return true; }")
                        pg.wait_for_timeout(1400)
                        views.append(("gear", pg.evaluate(COLLECT, [pal, "#nbpanel-root .nbdrawer"]) if g else {"n": 0, "bad": 1, "list": [["BAD no ⚙", 1]]}))
                        k2 = pg.evaluate(E.MEASURE, "#nbpanel-root .nbdrawer")["r4"]
                        shot(pg, "E35-%s-%s-gear.png" % (sk, theme))
                        badl = []
                        for nm, v in views:
                            badl += ["%s: %s ×%d" % (nm, k, c) for k, c in v["list"]]
                        n = sum(v["n"] for _, v in views)
                        row("C2 surfaces in the palette · " + tag, n > 200 and not badl,
                            "%d colours in %d views (cover, top, every 800 px to %d, ⚙); outside: %d %s" % (n, len(views), h, len(badl), badl[:12]))
                        low = k0["worst"] + k1["worst"] + k2["worst"]
                        row("C2k contrast ≥ 4.5 (document, ⚙) · " + tag, k1["low"] + k2["low"] == 0 and k1["n"] > 10 and k2["n"] > 5,
                            "top %d/%d · ⚙ %d/%d under 4.5 %s" % (k1["low"], k1["n"], k2["low"], k2["n"], (k1["worst"] + k2["worst"])[:6]))
                        row("C2c contrast on the cover · " + tag, k0["low"] == 0,
                            "%d/%d under 4.5 %s" % (k0["low"], k0["n"], k0["worst"][:5]), info=True)
                    ctx.close()
                if "C3" in ROWS and theme == "dark":
                    ctx, pg, errs = open_lab(b, base, None, theme)
                    box = pg.evaluate("""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), r = P.getBoundingClientRect();
                      var t = P.querySelector('.jp-NotebookPanel-toolbar'), top = t ? t.getBoundingClientRect().bottom : r.top;
                      return [r.left + 2, top + 2, r.right - 2, r.bottom - 2]; }""")
                    cdp = ctx.new_cdp_session(pg)
                    allf, seen, gone = flash_frames(pg, cdp, box)
                    # a frame painted up to 0.2 s after the poll saw the preview gone can still show it (compositor lag)
                    pre = [f for f in allf if gone is None or f["t"] < gone + .2]
                    fr = [f for f in allf if gone is not None and f["t"] >= gone + .2]
                    pw = max(pre, key=lambda f: f["bright"]) if pre else None
                    row("C3s stored preview before the run (Python P1) · digi dark (fresh)", pw is not None and pw["bright"] == 0,
                        "%d frames before the run replaced it (t < %ss): brightest %s blocks, ground %s" % (len(pre), gone, pw and pw["bright"], pw and pw["dom"]), info=True)
                    worst = max(fr, key=lambda f: f["bright"]) if fr else None
                    if SHOTS and worst: worst["img"].save(os.path.join(SHOTS, "E35-C3-brightest-frame.png"))
                    fa = [f for f in fr if not f["active"]]
                    wa = max(fa, key=lambda f: f["bright"]) if fa else None
                    act = next((f["t"] for f in fr if f["active"]), None)
                    row("C3a no flash before the script (CSS) · digi dark (fresh)", bool(fa) and wa["bright"] == 0,
                        "%d frames from the run until body.nb-dc-active (%ss): brightest t=%ss %s blocks (dominant %s)"
                        % (len(fa), act, wa and wa["t"], wa and wa["bright"], wa and wa["dom"]))
                    ours = [f for f in fr if f["dom"] not in ("#111111",)]          # Lab's own dark ground before our first paint
                    first = ours[0] if ours else None
                    row("C3 no flash after Run All · digi dark (fresh)", bool(fr) and seen is not None and worst["bright"] == 0, info=not JS, detail=
                        ("" if JS else "[needs J1: the script sets nb-dc-active before skin/theme — counted with --js] ") +
                        "%d frames from the run (stored preview gone at %ss), digi set at %ss · brightest frame t=%ss: %s blocks brighter than #2a2f4a (dominant %s) · grounds seen %s"
                        % (len(fr), gone, seen, worst and worst["t"], worst and worst["bright"], worst and worst["dom"],
                           sorted(set(f["dom"] for f in fr))[:8]))
                    okd = bool(first) and max(abs(a - b_) for a, b_ in zip(hexrgb(first["dom"]), (4, 5, 11))) <= 3 or \
                          bool(first) and any(max(abs(a - b_) for a, b_ in zip(hexrgb(first["dom"]), hexrgb(g))) <= 3 for g in ("#05060c", "#0b0e1c"))
                    row("C3d first frame already digi · digi dark (fresh)", okd,
                        "first frame of ours t=%ss: ground %s (want #04050b/#05060c/#0b0e1c)%s" % (first and first["t"], first and first["dom"],
                        "" if JS else " — needs J1 (JS); counted with --js"), info=not JS)
                    ctx.close()
            finally:
                srv.terminate()
        b.close()
    red = [r for r in rows if not r[1]]
    if JOUT: json.dump(rows, open(JOUT, "w"), indent=1)
    print("\n%d rows, %d red" % (len(rows), len(red)))
    print("REGRESS-CSS-E35 OK" if not red else "REGRESS-CSS-E35 RED")
    sys.exit(1 if red else 0)

def hexrgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def E_rgb(s):
    m = re.findall(r"[\d.]+", s or ""); return tuple(round(float(v)) for v in m[:3]) if len(m) >= 3 else (999, 999, 999)

def strip(pg):
    """A strip of the scroller's ground beside the text column: inside the scroller, right of our dock and the lens,
    every sampled point hits the scroller or a layer over it that paints nothing (transparent, no image, no text)."""
    return pg.evaluate("""() => { var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), sc = P && P.querySelector('.jp-WindowedPanel-outer');
      if (!sc) return null; var r = sc.getBoundingClientRect(), x0 = r.left + 4;
      [].forEach.call(document.querySelectorAll('.nbdock, .nbmap-cursor, .nbsb, .nbz-lens'), function(d){ var q = d.getBoundingClientRect();
        if (q.width > 0 && q.width < 200 && q.right > x0 && q.left < r.left + 120) x0 = Math.max(x0, q.right + 6); });
      var x1 = x0 + 36, y0 = r.top + 140, y1 = Math.min(r.bottom - 20, r.top + 440);
      var clear = function(e){ if (!e) return false; if (e === sc) return true; if (!sc.contains(e)) return false;
        var s = getComputedStyle(e), m = /rgba?\\(([^)]+)\\)/.exec(s.backgroundColor), al = m ? (m[1].split(',')[3] === undefined ? 1 : parseFloat(m[1].split(',')[3])) : 0;
        return al === 0 && s.backgroundImage === 'none' && !(e.firstChild && e.firstChild.nodeType === 3 && e.firstChild.nodeValue.trim()); };
      for (var x = x0; x <= x1; x += 9) for (var y = y0; y <= y1; y += 25) { var e = document.elementFromPoint(x, y);
        if (!clear(e)) return {bad: [Math.round(x), Math.round(y), e ? e.tagName + '.' + String(e.className).slice(0, 50) : null]}; }
      return {x: x0, y: y0, width: x1 - x0, height: y1 - y0}; }""")

if __name__ == "__main__":
    main()
