/* E36 J1 (2026-10-19, Werkstatt JS) — DER LADER DER HÜLLE (plan/ARCHITEKTUR.md, claude/VERTRAG-E36.md).
   lesen.html?nb=<id>&v=<NB_VERSION>[&lang=en|de][&inhalt=<wurzel>] zeigt ein Notebook ohne Kernel und ohne Jupyter:
     1. meta.json des Pakets (inhalt/<id>/<v>/; ohne v: inhalt/<id>/aktuell.json → v) und manifest.json der eigenen Hülle;
        verlangt das Paket eine andere Hülle (meta.toolkit) und gibt es sie: einmal dorthin (tk= verhindert Schleifen),
        sonst weiter mit dieser.
     2. parallel: alle Stylesheets der Hülle (<link>, abgewartet), die Lesefassung der Sprache, daten.json, reader.js.
     3. Lesefassung in <body>, data-nbrw-id / data-nbrw-v daran, reader.js (_NBRW_REHYD + 20-reader.js) direkt
        dahinter ausgeführt — mit Id und Version an den Platzhaltern, wie _nbread_js() es im Notebook tut. Damit
        liest und schreibt das Lesefenster dieselben Schlüssel digichemjn.<id>.* wie in Jupyter (PyCharm, VS Code).
   Ein Fehler → ein Satz auf der Seite (en + de), nie leeres Weiß. window.DIGICHEMJN: {id, v, toolkit, lang, meta, daten, pyodide,
   zeit{…ms seit Navigation}}; <html data-nbl=laden|bereit|fehler>; Ereignis 'digichemjn:bereit' am window. */
(function () {
  'use strict';
  var W = window, D = document, NS = W.DIGICHEMJN = W.DIGICHEMJN || {}, Z = NS.zeit = {};
  var OK = /^[A-Za-z0-9_][A-Za-z0-9_.-]{0,79}$/;
  function now() { return Math.round(W.performance && W.performance.now ? W.performance.now() : 0); }
  function mark(k) { Z[k] = now(); }
  var Q = {};
  W.location.search.replace(/^\?/, '').split('&').forEach(function (kv) {
    var i = kv.indexOf('='); if (!kv) return;
    try { Q[decodeURIComponent(i < 0 ? kv : kv.slice(0, i))] = i < 0 ? '' : decodeURIComponent(kv.slice(i + 1).replace(/\+/g, ' ')); } catch (e) {}
  });
  D.documentElement.setAttribute('data-nbl', 'laden');
  function msg(en, de) {
    var p = D.getElementById('nbl-msg');
    if (!p) { p = D.createElement('p'); p.id = 'nbl-msg'; p.setAttribute('role', 'status'); D.body.appendChild(p); }
    p.style.cssText = 'font:15px system-ui,sans-serif;margin:24px 16px';
    p.textContent = en + ' · ' + de;
  }
  function fail(en, de, why) {
    D.documentElement.setAttribute('data-nbl', 'fehler'); NS.fehler = String(why || en);
    msg(en, de);
    if (W.console) W.console.warn('digichemjn lesen:', why || en);
  }
  function get(url, how) {
    return W.fetch(url, { credentials: 'same-origin' }).then(function (r) {
      if (!r.ok) throw new Error(url + ' ' + r.status);
      return how === 'json' ? r.json() : r.text();
    });
  }
  var id = Q.nb || '', v = Q.v || '';
  if (!OK.test(id) || (v && !OK.test(v)) || /\.\./.test(id + v)) {
    fail('No notebook given (lesen.html?nb=<id>&v=<version>).', 'Kein Notebook angegeben (lesen.html?nb=<id>&v=<Version>).', 'nb/v'); return;
  }
  // the packages live beside the shell (dist/inhalt/ next to dist/huelle/<TV>/) or under &inhalt= — same origin only
  var base;
  try {
    base = new W.URL(Q.inhalt ? Q.inhalt.replace(/\/?$/, '/') : '../../inhalt/', W.location.href);
    if (base.origin !== W.location.origin) throw new Error('origin');
  } catch (e) { fail('The content address is not allowed.', 'Die Inhalts-Adresse ist nicht erlaubt.', 'inhalt'); return; }
  NS.id = id;
  msg('Loading …', 'Wird geladen …');
  mark('start');
  var vP = v ? W.Promise.resolve(v) : get(new W.URL(id + '/aktuell.json', base).href, 'json').then(function (j) {
    if (!j || !OK.test(String(j.v || ''))) throw new Error('aktuell.json'); return String(j.v);
  });
  var pkg = null;
  W.Promise.all([get('manifest.json', 'json'), vP.then(function (vv) {
    v = vv; pkg = new W.URL(id + '/' + vv + '/', base);
    return get(new W.URL('meta.json', pkg).href, 'json');
  })]).then(function (r) {
    var man = r[0], meta = r[1]; mark('meta');
    if (!meta || (meta.id && meta.id !== id)) throw new Error('meta.json: id ' + (meta && meta.id) + ' ≠ ' + id);
    // both spellings of the files (claude/VERTRAG-E36.md): manifest css[]/js{} or dateien{leser.css, leser.js};
    // meta langs/title or sprachen/titel
    var dt = man.dateien || {};
    man.css = man.css || (dt['leser.css'] ? [dt['leser.css'].datei] : []);
    man.js = man.js || { reader: dt['leser.js'] && dt['leser.js'].datei };
    meta.langs = meta.langs || meta.sprachen; meta.title = meta.title || meta.titel;
    var tk = String(meta.toolkit || man.toolkit || '');
    if (tk && tk !== man.toolkit && !('tk' in Q) && OK.test(tk)) {
      // the package was built against another shell: go there if it is on the server, else stay with this one
      return get('../' + tk + '/manifest.json', 'json').then(function () {
        W.location.replace('../' + tk + '/lesen.html' + W.location.search + (W.location.search ? '&' : '?') + 'tk=' + encodeURIComponent(man.toolkit));
        return null;
      }, function () { NS.andereHuelle = tk; return [man, meta]; });
    }
    return [man, meta];
  }).then(function (r) {
    if (!r) return null;
    var man = r[0], meta = r[1];
    var langs = (meta.langs && meta.langs.length ? meta.langs : [meta.lang || 'en']).filter(function (l) { return /^[a-z]{2}$/.test(l); });
    var st = null; try { st = W.localStorage.getItem('digichemjn.' + id + '.reader.lang'); } catch (e) {}
    var nav = /^de/i.test((W.navigator && W.navigator.language) || '') ? 'de' : 'en';
    var lang = [Q.lang, st, nav, meta.lang, langs[0]].filter(function (l) { return l && langs.indexOf(l) >= 0; })[0] || 'en';
    NS.v = v; NS.toolkit = man.toolkit; NS.lang = lang; NS.meta = meta; NS.manifest = man;
    // E38a J2: Python in the window from our own server — manifest.pyodide (claude/VERTRAG-E36.md: "<url>"|null),
    // relative to this page; the reader (20-reader.js py()) takes NS.pyodide, null → its fixed jsDelivr address
    NS.pyodide = null;
    if (typeof man.pyodide === 'string' && man.pyodide) {
      try { var pu = new W.URL(man.pyodide.replace(/\/?$/, '/'), W.location.href); if (/^https?:$/.test(pu.protocol)) NS.pyodide = pu.href; } catch (e) {}
    }
    D.documentElement.lang = lang;
    var t = meta.title && (meta.title[lang] || meta.title.en); if (t) D.title = String(t);
    var css = (man.css || []).map(function (h) {
      return new W.Promise(function (ok) {
        var l = D.createElement('link'); l.rel = 'stylesheet'; l.href = h;
        l.onload = ok; l.onerror = function () { NS.cssFehler = (NS.cssFehler || []).concat(h); ok(); };
        D.head.appendChild(l);
      });
    });
    var js = man.js || {};
    if (!js.reader) throw new Error('manifest.json: js.reader');
    return W.Promise.all([
      get(new W.URL('lesefassung.' + lang + '.html', pkg).href, 'text'),
      get(new W.URL('daten.json', pkg).href, 'json').then(null, function () { return null; }),   // optional (VERTRAG)
      get(js.reader, 'text'),
      W.Promise.all(css).then(function () { mark('css'); })
    ]);
  }).then(function (r) {
    if (!r) return;
    var html = r[0], code = r[2]; NS.daten = r[1]; mark('geladen');
    // parsed inert (<template>: no picture loads, nothing runs) and moved into the page in one step
    var box = D.createElement('template'); box.innerHTML = html;
    var root = box.content.querySelector('.nbreading');
    if (!root) throw new Error('lesefassung: no .nbreading');
    root.setAttribute('data-nbrw-id', id); root.setAttribute('data-nbrw-v', v);
    var m = D.getElementById('nbl-msg'); if (m) m.parentNode.removeChild(m);
    D.body.appendChild(root);
    // the reader finds its reading version as the script's previous sibling (document.currentScript), as in an output
    var s = D.createElement('script');
    s.text = code.replace(/__NBREADV__/g, NS.toolkit || '').replace(/__NBREADID__/g, id);
    root.parentNode.insertBefore(s, root.nextSibling);
    if (!root.getAttribute('data-nbrw')) throw new Error('reader did not start');
    mark('bereit');
    D.documentElement.setAttribute('data-nbl', 'bereit');
    try { W.dispatchEvent(new W.CustomEvent('digichemjn:bereit', { detail: { id: id, v: v } })); } catch (e) {}
  }).then(null, function (e) {
    fail('This notebook could not be loaded.', 'Dieses Notebook konnte nicht geladen werden.', e && e.message);
  });
})();
