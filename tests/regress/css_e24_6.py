"""test_regress — Werkstatt CSS, Eilauftrag E24 (2026-10-06). Real JupyterLab
under Playwright; read off the page (classes, storage, getComputedStyle,
getBoundingClientRect), nothing from our sources.

    python3 tests/regress/css_e24_6.py <notebook.ipynb> [lab] [fresh|old]
    (also a module of tests/regress/run.py: TESTS at the end)

  C24.6  retro is not offered any more (Nutzer 06.10.): the 🎨 button cycles
         minimal → cyber → fairy → minimal and never puts `nbskin-retro` on
         the page; the 👤 window offers no "retro"; a saved "retro" (profile
         key, a class left by an older tab, an account favourite) comes back
         as minimal: no retro class, storage "minimal", favourite "minimal".
         E34 (JS, 19.10.): four styles, digi the standard — minimal → cyber → fairy → digi →
         minimal; 👤 offers digi too (behauptete bisher: minimal → cyber → fairy → minimal).
Gegenprobe v1.65 (76ef1b1e): see the chronicle 06.10., Werkstatt CSS (E24)."""
import sys, os, json, warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import css_e21 as C

SKINCLS = "() => [].filter.call(document.body.classList, function(c){ return c.indexOf('nbskin-') === 0; }).join(',') || 'minimal'"

def c6(pg, ctx):
    bad = []
    # (1) the 🎨 button's cycle
    pg.evaluate("() => { window.__nbStore.set('digichemjn.skin.v1', 'minimal'); window.__nbApplySkin(); }")
    seq = []
    for _ in range(5):
        ok = pg.evaluate("() => { var b = document.querySelector('#nbpanel-root .nbbtn.nbskin'); if (!b) return false; b.click(); return true; }")
        if not ok: return False, "BAD no 🎨 button"
        pg.wait_for_timeout(350)
        seq.append(pg.evaluate(SKINCLS).replace("nbskin-", ""))
    if seq != ["cyber", "fairy", "digi", "minimal", "cyber"]: bad.append("🎨 cycle %s" % seq)
    # (2) a saved retro, and a class an older tab left on the page
    r = pg.evaluate("""() => { window.__nbStore.set('digichemjn.skin.v1', 'retro');
        document.body.classList.add('nbskin-retro'); window.__nbApplySkin();
        return {cls: [].filter.call(document.body.classList, function(c){ return c.indexOf('nbskin-') === 0; }).join(','),
                st: window.__nbStore.get('digichemjn.skin.v1')}; }""")
    if r["cls"] or r["st"] != "minimal": bad.append("saved retro → class %r, storage %r" % (r["cls"], r["st"]))
    # (3) the 👤 window
    pg.evaluate("() => { var b = document.querySelector('#nbpanel-root .nbbtn.nbprofile'); if (b) b.click(); }")
    opts = None
    for _ in range(20):
        pg.wait_for_timeout(250)
        opts = pg.evaluate("() => { var s = document.querySelector('select.nbpref[data-k=\"skin\"]'); return s ? [].map.call(s.options, function(o){ return o.value; }) : null; }")
        if opts: break
    pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
    if not opts: bad.append("BAD 👤 skin choice not found")
    elif "retro" in opts or not all(k in opts for k in ("digi", "minimal", "cyber", "fairy")): bad.append("👤 offers %s" % opts)
    # (4) an account whose favourite is retro
    a = pg.evaluate("""() => { var K = 'digichemjn.account.v1', old = localStorage.getItem(K);
        if (!window.__nbAcct) return null;
        localStorage.setItem(K, JSON.stringify({v: 1, id: 'DCJ-TEST-E246-0000', on: true, fav: {skin: 'retro'}}));
        // E25.o: logged in is the notebook's own key now (the record's `on` is not read)
        var OK = window.__nbAcct.onKey ? window.__nbAcct.onKey() : null, oldOn = OK ? localStorage.getItem(OK) : null;
        if (OK) localStorage.setItem(OK, '1');
        window.__nbFavDone = null; window.__nbAcct.applyFav(true);
        var rec = JSON.parse(localStorage.getItem(K) || '{}');
        var out = {fav: rec.fav && rec.fav.skin, st: window.__nbStore.get('digichemjn.skin.v1'),
                   cls: document.body.classList.contains('nbskin-retro')};
        if (old === null) localStorage.removeItem(K); else localStorage.setItem(K, old);
        if (OK) { if (oldOn === null) localStorage.removeItem(OK); else localStorage.setItem(OK, oldOn); }
        window.__nbFavDone = null; return out; }""")
    if a is None: bad.append("BAD no __nbAcct")
    elif a["fav"] != "minimal" or a["st"] != "minimal" or a["cls"]: bad.append("account favourite retro → %s" % a)
    pg.evaluate(C.SET, [ctx.get("skin", "minimal"), ctx.get("theme", "light")]); pg.wait_for_timeout(400)
    return (not bad), ("; ".join(bad) or "🎨 %s, saved retro → minimal, 👤 %s, favourite → minimal" % (seq, opts))

TESTS = [
    ("C24.6 E24.6 retro nicht wählbar, gespeichertes retro → minimal", c6),
]

def main():
    nb = sys.argv[1]; C.NB = nb
    C.ENV = sys.argv[2] if len(sys.argv) > 2 else "lab"
    C.STORE = sys.argv[3] if len(sys.argv) > 3 else "fresh"
    only = sys.argv[4].split(",") if len(sys.argv) > 4 and sys.argv[4] else None
    styles = (os.environ.get("C24_STYLES") or "minimal/light").split(",")
    from playwright.sync_api import sync_playwright
    red = 0
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=C.CHROME)
        ctx, pg, errs = C.open_nb(b)
        for st in styles:
            s, t = st.split("/")
            pg.evaluate(C.SET, [s, t]); pg.wait_for_timeout(800)
            for name, fn in TESTS:
                key = name.split()[0]
                if only and key not in only: continue
                try: ok, d = fn(pg, {"skin": s, "theme": t, "nb": nb})
                except Exception as e: ok, d = False, "BAD exception %s" % str(e)[:300]
                red += not ok
                print("%-4s %s %s/%s · %s" % ("ok" if ok else "RED", key, s, t, d[:900])); sys.stdout.flush()
        if errs: red += 1; print("RED Seitenfehler", errs[:3])
        b.close()
    print("css_e24_6: %d rot" % red); sys.exit(1 if red else 0)

if __name__ == "__main__":
    main()
