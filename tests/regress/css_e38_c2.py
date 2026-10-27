"""E38 C1/C2 · CSS (css_e38_c1.py = css_e38_c2.py, Zeilen nach Dateiname) — Werkstatt CSS, 27.10. (Auftrag plan/AUFTRAG.md: „C1 Deckblatt im Leser = Lab (Groessen, Zeitleiste mit
Schloessern und Scrollbalken, Karten)“, „C2 Dokument: Kapitel-Pillen, gesperrt = zu + LOCKED, Einfuehrung geschlossen wie Lab;
Ueberschriften Unbounded (braucht P1)“). Lab ist die Vorlage: je Thema EIN echtes JupyterLab (Run All, Stil digi) und daneben
lesen.html aus dem Bau-Ausgang (dist/, E36), beide 1400 x 900, gleiche Datei, beide im echten Chromium (mit Scrollbalken):

    python3 tests/regress/css_e38_c1.py [notebook.ipynb] [--themes light,dark] [--shots DIR] [--json out.json]   (Zeilen C1)
    python3 tests/regress/css_e38_c2.py …                                                                         (Zeilen C2)

Deckblatt (vor Play), Lage relativ zur Oberkante der Titelkarte, Toleranz 4 px:
  C1a  Lage: Leitsatz, „What you will learn“ (Oberkante + Hoehe), Kopf der Zeitleiste, Strich der Marken, Leiste, Kopf der
       Moduskarten, Karten (Oberkante, Hoehe, Breite), ▶ (Oberkante, Groesse), „Play“ — je wie Lab
  C1b  Zeitleiste: Lane so breit wie Labs (± 2), rollt wie Labs (Inhalt breiter als die Lane), Leiste 10 px hoch und sichtbar,
       Daumen in Labs Farbe, Rand-Verlauf rechts (Anfang), links keiner — wie Labs data-fade="r"
  C1c  Marken: Titel/Teil/Kapitel/Abbildung/Rechnen/Code so gross wie Labs .nbtl-mk (± 1); gesperrtes Kapitel gestrichelt,
       Deckkraft wie Lab, Schloss darin (Breite wie Labs ::after ± 1); offene Rechenaufgabe mit Schloss
  C1d  Namen: Teile und Kapitel in Labs Groesse, Kapitel nummeriert, ein langer Kapitelname zweizeilig wie in Lab (± 3)
  C1e  Karten/▶: Moduskarte Radius wie Lab, ▶ rund, Dreieck so breit wie Labs (::before)
Dokument (nach Play):
  C2a  Falten starten wie Lab: jeder in Lab sichtbare Teil/Kapitel-Kopf (Einfuehrung, Inhalt, Kapitel 1, gesperrte Kapitel,
       Anhang) im Leser offen/zu wie in Lab (mindestens 8 gefunden); Abbildung/Uebung/Code bleiben im Leser offen (INFO)
  C2b  Kapitel-Pillen: Hoehe wie Lab (± 2), Farbe offen/zu wie Lab
  C2c  gesperrte Kapitel: Schloss vor dem Namen, Marke „Locked“ (Versalien, Rand) dahinter — wie Labs Kopf
  C2d  Teile: Striche links und rechts so lang wie Labs (± 2)
  C2e  Abbildung/Uebung/Code: Polster und Farbe wie Lab
  INFO Inhaltsverzeichnis (Lab hat keins; bleibt, env_reader springt darueber)
  INFO Unbounded geladen (kommt mit Python P1 in die Huelle; bis dahin Ersatzschrift — nur INFO)
Gegenprobe v1.84 (390392b): rot (Chronik). exit 0 = REGRESS-CSS-E38-C1 OK bzw. -C2 OK."""
import sys, os, re, json, shutil, tempfile, functools, threading, http.server, socketserver
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from playwright.sync_api import sync_playwright
import css_e34 as E

A = sys.argv[1:]
def opt(k, d=None):
    return A[A.index(k) + 1] if k in A else d
THEMES = opt("--themes", "light,dark").split(",")
# eine Datei je Paket (Patches einzeln anwendbar): css_e38_c1.py prueft C1, css_e38_c2.py C2 (--rows C1,C2 beide)
ONLY = (opt("--rows") or ("C2" if os.path.basename(__file__).endswith("_c2.py") else "C1")).split(",")
SHOTS, JOUT = opt("--shots"), opt("--json")
W, H = 1400, 900
rows = []
def row(name, ok, detail, info=False):
    if not any(name.startswith(k) for k in ONLY) and not (info and (("C1" in ONLY) == ("Unbounded" in name))): return
    rows.append({"row": name, "ok": bool(ok) or info, "info": info, "detail": detail})
    print("%s  %-26s %s" % ("INFO" if info else ("PASS" if ok else "FAIL"), name, detail), flush=True)

LIB = r"""
  var R = function (e) { if (!e) return null; var r = e.getBoundingClientRect(); return r.width || r.height ? r : null; };
  var cs = function (e, p) { return getComputedStyle(e, p || null); };
  var px = function (v) { return Math.round(parseFloat(v) * 10) / 10; };
  var rgb = function (v) { var d = document.createElement('i'); d.style.color = v; document.body.appendChild(d); var c = cs(d).color; d.remove(); return c; };
"""
LAB_COVER = r"""() => {""" + LIB + r"""
  var P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), c = P && P.querySelector('.nbcover-out');
  if (!c) return null; var card = R(c.querySelector('.nbtitle-card')); if (!card) return null; var o = card.top, g = {};
  var top = function (s) { var r = R(c.querySelector(s)); return r ? Math.round(r.top - o) : null; };
  var mk = function (s) { var e = c.querySelector(s + ' .nbtl-mk'); return e ? e.offsetWidth : null; };
  var t = c.querySelector('.nbtl-title .nbtl-mk'), tr = R(t), sb = c.querySelector('.nbtl-sb'), lane = c.querySelector('.nbtl-lane');
  var ch = c.querySelectorAll('.nbtl-chapter'), lk = ch[1], mo = c.querySelector('.nbmode-opt'), pl = c.querySelector('.nbcover-play');
  var learn = R(c.querySelector('.nbcover-learn-h')), mor = R(mo), plr = R(pl), sbr = R(sb);
  return {lead: top('.nbtitle-lead'), learn: Math.round(learn.top - o), learnH: Math.round(learn.height), tlh: top('.nbcover-tl-h'),
    line: tr ? Math.round(tr.top + tr.height / 2 - o) : null, sb: sbr ? Math.round(sbr.top - o) : null, sbH: sbr ? Math.round(sbr.height) : 0,
    modeT: top('.nbmode-t'), card: Math.round(mor.top - o), cardH: Math.round(mor.height), cardW: Math.round(mor.width),
    play: Math.round(plr.top - o), playW: Math.round(plr.width), playLab: top('.nbcover-play-lab'),
    laneW: lane.clientWidth, scrolls: lane.scrollWidth > lane.clientWidth + 2, fade: lane.getAttribute('data-fade'),
    thumb: sb && sb.querySelector('.nbtl-sb-th') ? cs(sb.querySelector('.nbtl-sb-th')).backgroundColor : null,
    mk: {title: mk('.nbtl-title'), group: mk('.nbtl-group'), chap: mk('.nbtl-chapter'), viz: mk('.nbtl-figure'), calc: mk('.nbtl-calc'), code: mk('.nbtl-code')},
    lock: lk ? {dash: cs(lk.querySelector('.nbtl-mk')).borderTopStyle, op: px(cs(lk.querySelector('.nbtl-mk')).opacity), w: px(cs(lk, '::after').width)} : null,
    calcLock: px(cs(c.querySelector('.nbtl-calc'), '::after').width) || 0,
    labG: px(cs(c.querySelector('.nbtl-group .nbtl-nm')).fontSize), labC: px(cs(ch[0].querySelector('.nbtl-nm')).fontSize),
    labNum: /^\s*\d/.test(ch[0].querySelector('.nbtl-nm').textContent), lab2H: Math.round(R(ch[1].querySelector('.nbtl-nm')).height),
    modeR: px(cs(mo).borderTopLeftRadius), playR: cs(pl).borderRadius, triW: px(cs(pl, '::before').width)}; }"""
LES_COVER = r"""() => {""" + LIB + r"""
  var c = document.querySelector('.nbrw-cover'); if (!c) return null; var card = R(c.querySelector('.nbr-nbtitle-card')); if (!card) return null;
  var o = card.top, top = function (e) { var r = R(typeof e === 'string' ? c.querySelector(e) : e); return r ? Math.round(r.top - o) : null; };
  var hs = [].slice.call(c.querySelectorAll('.nbrw-cv-h')), hT = hs.filter(function (h) { return h.nextElementSibling && h.nextElementSibling.classList.contains('nbrw-cv-tl'); })[0],
      hM = hs.filter(function (h) { return h.nextElementSibling && h.nextElementSibling.classList.contains('nbrw-modes'); })[0];
  var sc = c.querySelector('.nbrw-cv-scroll'), d = function (k, st) { return c.querySelector('.nbrw-cv-dot[data-kind=' + k + ']' + (st ? '[data-st=' + st + ']' : '')); };
  var mk = function (k, st) { var e = d(k, st); return e ? px(cs(e, '::before').width) : null; };
  var t = R(d('title')) || (d('title') && d('title').getBoundingClientRect()), scr = sc.getBoundingClientRect(), sbH = sc.offsetHeight - sc.clientHeight;
  var mo = c.querySelector('.nbrw-mode-opt'), mor = R(mo), pl = c.querySelector('[data-nbrw-act=play]'), plr = R(pl), learn = R(c.querySelector('summary.nbr-nbcover-learn-h'));
  var lk = d('chap', 'locked'), chs = c.querySelectorAll('.nbrw-cv-dot[data-kind=chap]'), l0 = chs[0] && chs[0].querySelector('.nbrw-cv-lab'), l1 = chs[1] && chs[1].querySelector('.nbrw-cv-lab');
  var sth = cs(sc).getPropertyValue('--rw-cv-sth').trim();
  return {lead: top('.nbr-nbtitle-lead'), learn: Math.round(learn.top - o), learnH: Math.round(learn.height), tlh: top(hT),
    line: t ? Math.round(t.top - o) : null, sb: sbH > 0 ? Math.round(scr.bottom - sbH - o) : null, sbH: sbH,
    modeT: top(hM), card: Math.round(mor.top - o), cardH: Math.round(mor.height), cardW: Math.round(mor.width),
    play: Math.round(plr.top - o), playW: Math.round(plr.width), playLab: top('.nbrw-play-lab'),
    laneW: sc.clientWidth, scrolls: sc.scrollWidth > sc.clientWidth + 2,
    fade: (px(cs(sc).getPropertyValue('--rw-cv-fl')) > 0 ? 'l' : '') + (px(cs(sc).getPropertyValue('--rw-cv-fr')) > 0 ? 'r' : ''),
    thumb: sth ? rgb(sth) : null,
    mk: {title: mk('title'), group: mk('group'), chap: mk('chap', 'open'), viz: mk('viz'), calc: mk('calc'), code: mk('code')},
    lock: lk ? {dash: cs(lk, '::before').borderTopStyle, op: px(cs(lk, '::before').opacity), w: px(cs(lk, '::after').width)} : null,
    calcLock: d('calc', 'open') ? (px(cs(d('calc', 'open'), '::after').width) || 0) : 0,
    labG: px(cs(d('group').querySelector('.nbrw-cv-lab')).fontSize), labC: l0 ? px(cs(l0).fontSize) : null,
    labNum: l0 ? /counter/.test(cs(l0, '::before').content) || /^\s*\d/.test(l0.textContent) : false, lab2H: l1 ? Math.round(R(l1).height) : null,
    modeR: px(cs(mo).borderTopLeftRadius), playR: cs(pl).borderRadius, triW: px(cs(pl, '::before').width),
    font: document.fonts ? document.fonts.check('20px Unbounded') && [].some.call(document.fonts, function (f) { return f.family.replace(/"/g, '') === 'Unbounded' && f.status === 'loaded'; }) : null}; }"""
NORM = r"""function (s) { return (s || '').replace(/[^A-Za-z0-9():,. -]/g, '').replace(/\s+/g, ' ').trim(); }"""
LAB_DOC = r"""() => {""" + LIB + r"""
  var N = """ + NORM + r""", P = document.querySelector('.jp-NotebookPanel:not(.lm-mod-hidden)'), out = [];
  [].forEach.call(P.querySelectorAll('.jupyter-widget-Collapse-header'), function (h) { var r = R(h); if (!r) return; var col = h.parentElement;
    var a = cs(h, '::after'), b = cs(h, '::before'), ic = h.querySelector('i'), icr = R(ic);
    out.push({t: N(h.textContent), open: col.classList.contains('jupyter-widget-Collapse-open'), h: Math.round(r.height), col: cs(h).color, pad: cs(h).padding,
      after: a.content, afterTT: a.textTransform, afterB: a.borderTopStyle, before: px(b.width) || 0, icon: !!(icr && icr.width > 4)}); });
  return out; }"""
LES_DOC = r"""() => {""" + LIB + r"""
  var N = """ + NORM + r""", out = [];
  [].forEach.call(document.querySelectorAll('.nbrw-doc details[data-acc]>summary>.nbread-h'), function (h) { var d = h.parentElement.parentElement;
    var en = h.querySelector('[data-nbrw-l=en]'), r = h.getBoundingClientRect(), a = cs(h, '::after'), b = cs(h, '::before');
    out.push({t: N(en ? en.textContent : h.textContent), acc: d.getAttribute('data-acc'), kind: d.getAttribute('data-kind'), open: d.open, h: Math.round(r.height), col: cs(h).color, pad: cs(h).padding,
      after: a.content, afterTT: a.textTransform, afterB: a.borderTopStyle, before: px(b.width) || 0,
      icon: b.content !== 'none' && b.content !== 'normal' && (px(b.width) || 0) > 4 && cs(h, '::before').maskImage !== 'none'}); });
  var toc = document.querySelector('.nbrw-doc ol.nbread-toc');
  return {heads: out, toc: !!(toc && R(toc))}; }"""

def find_dist(nbf):
    for d in (opt("--dist"), os.environ.get("DIGICHEM_DIST"), os.path.join(os.path.dirname(os.path.dirname(nbf)), "dist"), os.path.join(ROOT, "dist")):
        if d and os.path.isdir(os.path.join(d, "huelle")):
            return d

def near(a, b, t):
    return a is not None and b is not None and abs(a - b) <= t

def judge(th, L, R, LD, RD):
    if not L or not R:
        row("C1 %s" % th, False, "BAD kein Deckblatt (Lab %s, Leser %s)" % (bool(L), bool(R))); return
    keys = ["lead", "learn", "learnH", "tlh", "line", "sb", "sbH", "modeT", "card", "cardH", "cardW", "play", "playW", "playLab"]
    bad = ["%s %s≠%s" % (k, R[k], L[k]) for k in keys if not near(R[k], L[k], 4)]
    row("C1a %s Lage" % th, not bad, ("ab " + " · ".join(bad)) if bad else "alle %d wie Lab (± 4): %s" % (len(keys), " ".join("%s %s" % (k, R[k]) for k in keys)))
    ok = near(R["laneW"], L["laneW"], 2) and R["scrolls"] == L["scrolls"] and R["sbH"] == 10 and R["thumb"] == L["thumb"] and R["fade"] == (L["fade"] or "")
    row("C1b %s Zeitleiste" % th, ok, "Lane %s (Lab %s) · rollt %s (%s) · Leiste %s px · Daumen %s (%s) · Verlauf %r (%r)" % (
        R["laneW"], L["laneW"], R["scrolls"], L["scrolls"], R["sbH"], R["thumb"], L["thumb"], R["fade"], L["fade"]))
    bm = ["%s %s≠%s" % (k, R["mk"][k], L["mk"][k]) for k in L["mk"] if not near(R["mk"][k], L["mk"][k], 1)]
    lk, ll = R["lock"] or {}, L["lock"] or {}
    ok = not bm and lk.get("dash") == ll.get("dash") == "dashed" and near(lk.get("op"), ll.get("op"), .05) and near(lk.get("w"), ll.get("w"), 1) \
        and near(R["calcLock"], L["calcLock"], 1) and L["calcLock"] > 0
    row("C1c %s Marken" % th, ok, ("ab " + " · ".join(bm) + " · ") if bm else "Groessen wie Lab %s · " % R["mk"] +
        "gesperrt %s/%s Schloss %s (Lab %s/%s/%s) · offene Aufgabe Schloss %s (%s)" % (lk.get("dash"), lk.get("op"), lk.get("w"),
                                                                                     ll.get("dash"), ll.get("op"), ll.get("w"), R["calcLock"], L["calcLock"]))
    ok = near(R["labG"], L["labG"], .3) and near(R["labC"], L["labC"], .3) and R["labNum"] and L["labNum"] and near(R["lab2H"], L["lab2H"], 3)
    row("C1d %s Namen" % th, ok, "Teil %s px (%s) · Kapitel %s px (%s) · Nummer %s (%s) · Name 2 %s px hoch (%s)" % (
        R["labG"], L["labG"], R["labC"], L["labC"], R["labNum"], L["labNum"], R["lab2H"], L["lab2H"]))
    ok = near(R["modeR"], L["modeR"], .5) and R["playR"] == L["playR"] and near(R["triW"], L["triW"], 1)
    row("C1e %s Karten/Play" % th, ok, "Karte r %s (%s) · ▶ r %s (%s) · Dreieck %s (%s)" % (R["modeR"], L["modeR"], R["playR"], L["playR"], R["triW"], L["triW"]))
    row("INFO %s Unbounded" % th, True, "geladen: %s (Python P1 liefert die Schrift)" % R.get("font"), info=True)
    if "C2" not in ONLY: return
    if not LD or not RD:
        row("C2 %s" % th, False, "BAD kein Dokument"); return
    heads = RD["heads"]
    pairs = []
    for l in LD:
        m = [r for r in heads if r["t"] and l["t"] and (r["t"].startswith(l["t"]) or l["t"].startswith(r["t"]))]
        if m: pairs.append((l, m[0]))
    big = [(l, r) for l, r in pairs if r["kind"] in ("group", "chapter")]
    bad = ["%s %s≠%s" % (l["t"][:22], r["open"], l["open"]) for l, r in big if r["open"] != l["open"]]
    row("C2a %s Falten" % th, len(big) >= 8 and not bad, "Teile/Kapitel %d/%d gefunden · %s" % (len(big), len(pairs), ("ab " + " · ".join(bad)) if bad else "alle wie Lab"))
    sm = ["%s %s/%s" % (l["t"][:12], r["open"], l["open"]) for l, r in pairs if r["kind"] not in ("group", "chapter")]
    row("INFO %s Falten klein" % th, True, "Abbildung/Uebung/Code im Leser offen, in Lab zu (bewusst offen: Tests und Lesefluss; Auftrag nennt Teile/Kapitel): %s" % " · ".join(sm), info=True)
    ch = [(l, r) for l, r in pairs if l["h"] > 40]
    bad = ["%s h%s≠%s col %s≠%s" % (l["t"][:18], r["h"], l["h"], r["col"], l["col"]) for l, r in ch if not near(r["h"], l["h"], 2) or r["col"] != l["col"]]
    row("C2b %s Kapitel-Pillen" % th, len(ch) >= 5 and not bad, "%d Pillen · %s" % (len(ch), ("ab " + " · ".join(bad)) if bad else "Hoehe/Farbe wie Lab"))
    lk = [(l, r) for l, r in pairs if l["after"] not in ("none", "normal", '""') and l["h"] > 40]
    bad = ["%s %s/%s/%s/%s" % (l["t"][:18], r["after"], r["afterTT"], r["afterB"], r["icon"]) for l, r in lk
           if r["after"] != l["after"] or r["afterTT"] != l["afterTT"] or r["afterB"] != l["afterB"] or r["icon"] != l["icon"]]
    row("C2c %s gesperrt" % th, len(lk) >= 4 and not bad, "%d gesperrt (Lab %s, Schloss) · %s" % (len(lk), lk[0][0]["after"] if lk else "-", ("ab " + " · ".join(bad)) if bad else "wie Lab"))
    gr = [(l, r) for l, r in pairs if l["before"] > 0]
    bad = ["%s %s≠%s" % (l["t"][:14], r["before"], l["before"]) for l, r in gr if not near(r["before"], l["before"], 2)]
    row("C2d %s Teile" % th, len(gr) >= 3 and not bad, "%d Teile · %s" % (len(gr), ("ab " + " · ".join(bad)) if bad else "Striche wie Lab %s px" % gr[0][0]["before"]))
    sm = [(l, r) for l, r in pairs if 18 < l["h"] < 34]
    bad = ["%s %s/%s≠%s/%s" % (l["t"][:14], r["pad"], r["col"], l["pad"], l["col"]) for l, r in sm if r["pad"] != l["pad"] or r["col"] != l["col"]]
    row("C2e %s kleine Pillen" % th, len(sm) >= 3 and not bad, "%d · %s" % (len(sm), ("ab " + " · ".join(bad)) if bad else "Polster/Farbe wie Lab"))
    row("INFO %s Verzeichnis" % th, True, "Inhaltsverzeichnis im Fenster: %s (Lab: keins; bleibt — env_reader W8/C2 nutzen es)" % RD["toc"], info=True)

def main():
    import nbpick
    nbf = os.path.abspath(nbpick.from_argv(sys.argv))
    m = json.load(open(nbf, encoding="utf-8")).get("metadata", {}).get("digichemjn", {})
    nid, nbv, tv = m.get("id") or "vorlage", m.get("version") or "", m.get("toolkit") or ""
    dist = find_dist(nbf)
    if not dist:
        row("C0 Bau-Ausgang", False, "BAD kein dist/ mit huelle/ — erst bauen"); return
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Q, directory=dist))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = "http://127.0.0.1:%d/huelle/%s/lesen.html?nb=%s&v=%s" % (srv.server_address[1], tv, nid, nbv)
    with sync_playwright() as P:
        b = P.chromium.launch(executable_path=E.CHROME if os.path.exists(E.CHROME) else None, ignore_default_args=["--hide-scrollbars"])
        for th in THEMES:
            tmp = tempfile.mkdtemp(prefix="css_e38_"); shutil.copy(nbf, os.path.join(tmp, "nb.ipynb"))
            p, base = E.start_server("lab", tmp, th)
            L = LD = None
            try:
                c = b.new_context(viewport={"width": W, "height": H}, color_scheme=th)
                c.add_init_script("try{localStorage.clear();localStorage.setItem('digichemjn.theme.v1.%s','%s');localStorage.setItem('digichemjn.skin.v1.%s','digi')}catch(e){}" % (nid, th, nid))
                pg = c.new_page(); pg.goto(base + "/lab/tree/nb.ipynb"); pg.wait_for_selector(".jp-NotebookPanel", timeout=90000); pg.wait_for_timeout(3000)
                st = E.run_and_play(pg)
                if st == "ok":
                    L = pg.evaluate(LAB_COVER)
                    if SHOTS: os.makedirs(SHOTS, exist_ok=True); pg.screenshot(path=os.path.join(SHOTS, "E38-lab-cover-digi-%s.png" % th))
                    if "C2" in ONLY and E.play(pg) == "play":
                        pg.wait_for_timeout(1500); LD = pg.evaluate(LAB_DOC)
                c.close()
            finally:
                p.terminate()
            c = b.new_context(viewport={"width": W, "height": H}, color_scheme=th)
            c.add_init_script("try{localStorage.clear();localStorage.setItem('digichemjn.%s.reader.skin','digi');localStorage.setItem('digichemjn.%s.reader.theme','%s')}catch(e){}" % (nid, nid, th))
            pg = c.new_page(); pg.goto(url); pg.locator(".nbrw").first.wait_for(timeout=30000); pg.wait_for_timeout(1500)
            R = pg.evaluate(LES_COVER)
            if SHOTS: pg.screenshot(path=os.path.join(SHOTS, "E38-C1-lesen-cover-digi-%s.png" % th))
            pg.locator(".nbrw-play").first.click(); pg.wait_for_timeout(1500)
            RD = pg.evaluate(LES_DOC)
            if SHOTS: pg.screenshot(path=os.path.join(SHOTS, "E38-C2-lesen-doc-digi-%s.png" % th))
            c.close()
            judge(th, L, R, LD, RD)
        b.close()

if __name__ == "__main__":
    main()
    if JOUT:
        json.dump(rows, open(JOUT, "w"), indent=1, ensure_ascii=False)
    red = [r for r in rows if not r["ok"]]
    print("REGRESS-CSS-E38-%s %s (%d Zeilen, %d rot)" % ("+".join(ONLY), "OK" if rows and not red else "FAIL", len(rows), len(red)))
    sys.exit(0 if rows and not red else 1)
