/* E26 Teil 2 (2026-10-11, Werkstatt JS) — THE READING WINDOW.
   Where every output is a page of its own and no widget is drawn (PyCharm,
   JCEF 122; prototype measured by the conductor 11.10.), the reading version
   (.nbreading, E26.1) is the whole notebook — 30 000 px of one output the IDE
   scrolls as a block. This script, shipped INSIDE that output (_nbread_js),
   puts it into a window of fixed height that scrolls in itself, with a panel
   on the right: one mark per chapter, the current chapter, a thumb, the lens
   A−/A+ and the window height ↕−/↕+ (both kept per notebook). The wheel over
   the window moves the window, not the IDE (own handler, passive:false,
   preventDefault only while the window can still move — at its ends the wheel
   goes on to the IDE). No full-screen API: it destroys the output in PyCharm.
   It never starts where a notebook front end hosts the output (JupyterLab,
   Notebook 7, classic, nbconvert's page: the page scrolls there) or where our
   widgets are drawn (.acc-root: the live document takes over) — and it steps
   back if they appear later. Without script the reading version stays as it is.
   Class contract with CSS (15-reader.css, travels in the same output):
   .nbrw[data-nbrw-theme][data-nbrw-skin] (--nbrw-h, --nbrw-zoom) > .nbrw-win
   (the reading version) + .nbrw-panel > .nbrw-bar > button.nbrw-btn[data-act],
   .nbrw-cur, .nbrw-track > .nbrw-thumb + .nbrw-mark[data-kind][data-st]
   (.is-active, span.nbrw-lab). The few rules below are only a fallback: they
   sit in <head>, before the reading output's own <style>, and every one of
   them is matched by a rule of 15-reader.css that comes later and wins.

   E26 Teil 3 (2026-10-11, Werkstatt JS) — „LESEFENSTER WIE LAB“
   (claude/VERTRAG-nbrw-E26.3.md). Only this path changes; JupyterLab/Lite
   never reach past hosted() below (lab_same).
   1. THE PREVIEW FIRST. The window opens on the cover (.nbrw-cover: title
      card, EN|DE, timeline, mode cards, ▶ Play, account line) — Python's, or
      built here from the card and the contents list. Play → the document in
      the same window (nothing steered across outputs); „◂ Vorschau“ in the
      panel goes back. Language and mode act at once on cover and document
      (both languages in the markup as [data-nbrw-l], CSS hides one).
   2. THE AXIS IS THE WINDOW'S MIDDLE. The window spans the whole output; the
      panel lies over its right side and is never wider than half of it; the
      window keeps the panel's width free on BOTH sides (--nbrw-side), so the
      column (860 px, as the reading version) is centred on the window's
      middle with the panel open, closed or at any lens.
   3. EVERYTHING IN THE WINDOW. Gating like Lab (a chapter waits for its
      exercise: [data-nbrw-gate], 🔒 on the mark and on the cover), XP bar in
      the panel, accordions (<details data-acc>) kept per notebook, the mode
      (plain|calc|code|both) hides what it leaves out, progress per notebook
      in localStorage. Coding: the stub in a coloured field and „▶ Ausführen
      im Fenster“ — Python in the browser (Pyodide, fixed version, jsDelivr,
      loaded at the first click only, never embedded); the check the kernel
      ships as text (data-check, the tests of pruefe()). No network → the
      honest sentence + „In Zwischenablage“ + pruefe("t1", …). Never a call to
      the Jupyter server.

   E31 (2026-10-12, Werkstatt JS; claude/VERTRAG-E31-js.md) — „WIE IN LAB“,
   the reader's videos of v1.77 in PyCharm:
   T2 the tools are a floating column on the left, loose buttons, no box
      (Lab's .nbcorner); S1 under them the window's scroll bar (Lab's .nbsb:
      thumb = the visible share, drag proportional, a click on the track goes
      there). P1 the timeline panel on the right is pulled open by its GRIP
      (Lab's .nbgrip: a round knob on the panel's left edge at the reading
      height — sideways = the panel's width, up/down = the reading height
      (L1), a click folds/unfolds; kept per notebook), never past the window's
      middle; wider than the free margin it lies OVER the document on its own
      surface. M1 the marker stands on the rail at the reading height, lit,
      and takes the kind and state of the mark it is passing (Lab's
      .nbmap-here); .is-moving while the document runs (the trail). Z1 the
      free margins are equal on both sides (--nbrw-side), so the column, the
      title card and the cover keep the window's middle whatever the panel
      does. G1 the size of the controls (tools, panel, marks, grip, marker,
      hover box) is a setting of its own (⊖/⊕, --nbgs, 80 … 150 %), apart
      from the lens (🔍) and the text size (A). T1 the preview's timeline is
      ONE row like Lab's: a line, the marks on it, the names alternating
      above and below, never wrapped; wider than the room it scrolls
      sideways. W1 the window never steps back unless the page is a real
      JupyterLab/Notebook page (hosted below): a host that draws the widget
      outputs of the same cell into the same page (PyCharm on a second run,
      Colab) left the window with nothing (v1.77, video 1: [4] empty). */
(function () {
  var V = '__NBREADV__', ID = '__NBREADID__';
  var me = document.currentScript;
  var root = null;
  if (me) { var p = me.previousElementSibling; if (p && p.classList && p.classList.contains('nbreading')) root = p; }
  // an unclosed tag in the markup puts this script INSIDE the reading version (Complex v1.73: two concept boxes) — then it is ours
  if (!root && me && me.closest) root = me.closest('.nbreading');
  if (!root) { var all = document.querySelectorAll('.nbreading:not([data-nbrw])'); root = all.length ? all[all.length - 1] : null; }
  if (!root || root.getAttribute('data-nbrw')) return;
  var D = root.ownerDocument, W = D.defaultView;
  var HOSTED = '.jp-NotebookPanel,.jp-Notebook,#notebook';
  // E31 W1: our widgets in the page count only on a real notebook page (Lab, Notebook 7, classic) — PyCharm or
  // Colab may draw the cell's widget outputs into the same page; the window stays (behauptete bisher: any .acc-root)
  function hosted() { return !!(root.closest && root.closest(HOSTED)) || (!!D.querySelector(HOSTED) && !!D.querySelector('.acc-root,.nb-live')); }
  if (hosted()) return;
  root.setAttribute('data-nbrw', V);

  var K = 'digichemjn.' + (ID || 'nb') + '.reader';
  function load(k, d) { try { var v = W.localStorage.getItem(K + '.' + k); return v == null ? d : v; } catch (e) { return d; } }
  function save(k, v) { try { W.localStorage.setItem(K + '.' + k, String(v)); } catch (e) {} }
  // E30 (E29 D7 in the window): the text size, independent of the lens — the
  // stylesheet reads --nbfs (1 = 100 %) on .nbrw; kept per notebook with the
  // window's other values (K.fs, env_multi M6), 90 … 150 % in steps of 10
  var FS = { min: 90, max: 150, step: 10, std: 100 }, FSK = K + '.fs';
  function fsLv() { var v = NaN; try { v = parseFloat(W.localStorage.getItem(FSK)); } catch (e) {} return v >= FS.min && v <= FS.max ? v : FS.std; }
  function fsSet(v) {
    v = Math.max(FS.min, Math.min(FS.max, Math.round(v / FS.step) * FS.step));
    try { if (v === FS.std) W.localStorage.removeItem(FSK); else W.localStorage.setItem(FSK, String(v)); } catch (e) {}
    fsApply(); return v;
  }
  function fsApply() {
    var v = fsLv();
    wrap.style.setProperty('--nbfs', String(Math.round(v) / 100)); wrap.setAttribute('data-nbfs', String(v));
    fsV.textContent = v + ' %'; fsV.value = v + ' %';
  }
  // E31 G1: the size of the controls, apart from the lens and the text size — --nbgs (1 = 100 %) on .nbrw,
  // kept per notebook (K.gs), 80 … 150 % in steps of 10; JS draws the controls' geometry × gs
  var GS = { min: 80, max: 150, step: 10, std: 100 }, GSK = K + '.gs';
  function gsLv() { var v = NaN; try { v = parseFloat(W.localStorage.getItem(GSK)); } catch (e) {} return v >= GS.min && v <= GS.max ? v : GS.std; }
  function gsSet(v) {
    v = Math.max(GS.min, Math.min(GS.max, Math.round(v / GS.step) * GS.step));
    try { if (v === GS.std) W.localStorage.removeItem(GSK); else W.localStorage.setItem(GSK, String(v)); } catch (e) {}
    gsApply(); return v;
  }
  var gs = 1;
  function gsApply() {
    var v = gsLv(); gs = v / 100;
    wrap.style.setProperty('--nbgs', String(gs)); wrap.setAttribute('data-nbgs', String(v));
    gsV.textContent = v + ' %'; gsV.value = v + ' %';
    if (ready) { sizeCtl(); place(); drawMarks(); }
  }
  // E33 B1b: the window is as tall as the screen less the IDE's own bars (screen.availHeight − HRAND) — a
  // fixed number of the display, never of the frame (innerHeight = the content: Colab's feedback, E32 K1); ↕ stays
  var HMIN = 300, HMAX = 2400, HSTEP = 100, HRAND = 240;
  function hDef() {
    var s = 0; try { s = (W.screen && (W.screen.availHeight || W.screen.height)) || 0; } catch (e) {}
    return s > 0 ? Math.min(HMAX, Math.max(HMIN, Math.round((s - HRAND) / 10) * 10)) : 600;
  }
  var H0 = hDef();
  // E38a J1: in the shell's own page (lesen.html — the loader marks <html data-nbl> and sets window.DIGICHEMJN; the
  // App shows it in its own frame) nothing of an IDE sits around the window: it is as tall as that page's viewport
  // less the frame's own edge and follows it (resize, phone bars); ↕ goes there and its key 'h' is neither read nor
  // written (shared with Jupyter). The rule screen − HRAND and ↕ stay for Jupyter hosts, PyCharm, VS Code, Colab.
  var HULL = !!(W.DIGICHEMJN && D.documentElement.hasAttribute('data-nbl'));
  // E26.3: the lens like Lab — 100 % in the middle, 60 … 150 %
  var Z = [0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5];
  var THEMES = ['', 'dark', 'light'], SKINS = ['digi', 'minimal', 'cyber', 'fairy'], MODES = ['plain', 'calc', 'code', 'both'];   // E34: digi first
  // panel open / closed (px; CSS E26.3 measured 44). E33 B5: NOT × gs any more — the controls' size is the tool
  // column's only; the panel and its marks scale like Lab's with the panel's width and the lens (ks, place())
  var PW = 168, PWC = 44, KCAP = 2, ks = 1;
  var pwOpen = parseFloat(load('pw', '')) || 0;  // E31 P1: the open panel's width the reader dragged (px; 0 = standard)
  var h = HULL ? H0 : Math.min(HMAX, Math.max(HMIN, parseFloat(load('h', H0)) || H0));
  var zi = Z.indexOf(parseFloat(load('z', 1))); if (zi < 0) zi = 4;
  var th = THEMES.indexOf(load('theme', '')); if (th < 0) th = 0;
  // E34: nothing stored = the standard „digi“; a stored word this build does not know = minimal (nobody moved).
  // Light/dark stays „as the host“ here: inside a light VS Code/PyCharm the window is light (E33 D).
  var sk0 = load('skin', ''), sk = sk0 ? SKINS.indexOf(sk0) : 0; if (sk < 0) sk = 1;
  var popen = load('panel', 'open') !== 'closed';
  var BI = !!root.querySelector('[data-nbrw-l]');          // both languages in the markup
  var lg0 = /^de/.test(root.getAttribute('lang') || D.documentElement.lang || '') ? 'de' : 'en';
  var lg = BI && /^(en|de)$/.test(load('lang', '')) ? load('lang', '') : lg0;
  var mode = load('mode', '');
  if (MODES.indexOf(mode) < 0) mode = MODES.indexOf(root.getAttribute('data-nbrw-mode') || '') >= 0 ? root.getAttribute('data-nbrw-mode') : 'both';
  var de, L, T;
  var LT = {
    de: { 'a-': 'Lupe kleiner', 'a+': 'Lupe größer', 'f-': 'Schrift kleiner', 'f+': 'Schrift größer', fsT: 'Schriftgröße (Doppelklick: Standard)',
      'g-': 'Bedienelemente kleiner', 'g+': 'Bedienelemente größer', gsT: 'Größe der Bedienelemente (Doppelklick: Standard)',
      grip: 'Ziehen: seitwärts = Breite des Panels, auf/ab = Lesehöhe · Klick: Panel auf/zu', sb: 'Bildlaufleiste: ziehen oder in die Rinne klicken',
      'h-': 'Fenster niedriger', 'h+': 'Fenster höher', theme: 'Hell/dunkel: ',
      k: { title: 'Titel', group: 'Teil', chap: 'Kapitel', sub: 'Abschnitt', viz: 'Abbildung', calc: 'Aufgabe', code: 'Programmieraufgabe',
           end: 'Ende des geführten Teils', yoc: 'Eigene Zellen' },
      st: { open: 'offen', solved: 'gelöst', wrong: 'falsch beantwortet', skipped: 'übersprungen', locked: 'gesperrt' },
      tip: 'Klick: öffnen und auf die Lesehöhe · noch einmal: zuklappen', tipGo: 'Klick: auf die Lesehöhe', tasks: 'Aufgaben',
      yocT: 'Eigene Zellen laufen in JupyterLab bzw. auf der Lite-Seite.', locked: '\uD83D\uDD12 Noch gesperrt',
      rl: 'Lesehöhe: nach oben oder unten ziehen', lname: { en: 'Englisch', de: 'Deutsch' },
      only: 'Dieses Dokument liegt nur auf %s vor (so gebaut) — Panel und Inhaltsverzeichnis folgen ihm; die Vorschau ist zweisprachig.',
      skin: 'Stil: ', auto: 'automatisch', dark: 'dunkel', light: 'hell', top: 'Anfang', nav: 'Lesefenster',
      cover: 'Vorschau', pin: 'Panel einklappen', pout: 'Panel ausklappen', xp: 'Fortschritt', play: 'Play',
      playT: 'Zum Dokument', lang: 'Sprache', modeT: 'Was möchten Sie üben?',
      modes: { plain: ['\u00B6', 'Nur lesen', 'nur Text und Abbildungen'], calc: ['\u270E', 'Stift & Papier', 'nur die Rechenaufgaben'],
               code: ['\u2328', 'Code', 'nur die Programmieraufgaben'], both: ['\u270E\u2328', 'Beides', 'rechnen und programmieren'] },
      tl: 'Ihr Weg durch dieses Notebook', acct: 'Konto \u25B8',
      acctT: 'Ihr Fortschritt bleibt in diesem Browser, je Notebook. Anmelden mit Name + Passwort: in JupyterLab bzw. auf der Lite-Seite.',
      lock: '\uD83D\uDD12 Dieses Kapitel öffnet sich, sobald %s beantwortet ist: richtig, falsch oder übersprungen.' },
    en: { 'a-': 'Zoom out', 'a+': 'Zoom in', 'f-': 'Smaller text', 'f+': 'Larger text', fsT: 'Text size (double click: standard)',
      'g-': 'Smaller controls', 'g+': 'Larger controls', gsT: 'Size of the controls (double click: standard)',
      grip: 'Drag: sideways = the panel\'s width, up/down = the reading height · click: open/fold the panel', sb: 'Scroll bar: drag it or click the track',
      'h-': 'Shorter window', 'h+': 'Taller window', theme: 'Light/dark: ',
      k: { title: 'Title', group: 'Part', chap: 'Chapter', sub: 'Section', viz: 'Figure', calc: 'Exercise', code: 'Coding',
           end: 'End of the guided part', yoc: 'Your own cells' },
      st: { open: 'open', solved: 'solved', wrong: 'answered wrong', skipped: 'skipped', locked: 'locked' },
      tip: 'Click: open it and bring it to the reading height · again: fold it', tipGo: 'Click: to the reading height', tasks: 'exercises',
      yocT: 'Your own cells run in JupyterLab or on the Lite page.', locked: '\uD83D\uDD12 Still locked',
      rl: 'Reading height: drag up or down', lname: { en: 'English', de: 'German' },
      only: 'This document exists in %s only (built so) — the panel and the contents follow it; the preview is bilingual.',
      skin: 'Style: ', auto: 'automatic', dark: 'dark', light: 'light', top: 'Start', nav: 'Reading window',
      cover: 'Preview', pin: 'Fold the panel', pout: 'Unfold the panel', xp: 'Progress', play: 'Play',
      playT: 'To the document', lang: 'Language', modeT: 'What do you want to practise?',
      modes: { plain: ['\u00B6', 'Plain', 'text and figures only'], calc: ['\u270E', 'Pen & paper', 'only the calculating exercises'],
               code: ['\u2328', 'Code', 'only the coding exercises'], both: ['\u270E\u2328', 'Both', 'calculate and code'] },
      tl: 'Your route through this notebook', acct: 'Account \u25B8',
      acctT: 'Your progress stays in this browser, per notebook. Sign in with name + password: in JupyterLab or on the Lite page.',
      lock: '\uD83D\uDD12 This chapter opens once %s is answered: right, wrong or skipped.' } };
  var TT = {
    de: { ok: '\u2713 richtig, gut gemacht!', bad: 'Noch nicht, weiter so.', num: 'Bitte in jedes Feld eine Zahl, z. B. 2,5.',
      pick: 'Bitte zuerst eine Antwort wählen.', lock: '\uD83D\uDD12 Öffnet sich, sobald die Aufgabe davor beantwortet ist.',
      clock: '\uD83D\uDD12 Öffnet sich, sobald die Programmieraufgabe davor beantwortet ist (pruefe).',
      copied: 'Kopiert: in eine neue Zelle darunter einfügen, ausfüllen, ausführen.', nocopy: 'Bitte markieren und mit Strg+C kopieren.',
      csolved: '\u2713 im Kernel gelöst.', cwrong: 'Im Kernel geprüft: noch nicht.', mcalc: 'Aufgabe', mcode: 'Programmieraufgabe',
      run: '\u25B6 Ausführen im Fenster', clip: 'In Zwischenablage', pyload: 'Python wird geladen, einmalig ~10 s \u2026',
      pypkg: 'Pakete werden geladen: ', pyrun: 'Läuft \u2026', pydone: 'Fertig.', pyerr: 'Fehler im Code — nichts gewertet.',
      pyoff: 'Python im Fenster ist hier nicht verfügbar (kein Internet oder CDN gesperrt). Kopieren Sie den Code in eine neue Zelle '
        + 'und prüfen Sie ihn dort mit %s — der Fortschritt zählt genauso.', nochk: 'Ausgeführt (diese Aufgabe prüft nur der Kernel: %s).' },
    en: { ok: '\u2713 correct, well done!', bad: 'Not there yet, keep going.', num: 'Enter a number in every box, for example 2.5.',
      pick: 'Pick one of the options first.', lock: '\uD83D\uDD12 Opens once the exercise before it is answered.',
      clock: '\uD83D\uDD12 Opens once the coding exercise before it is answered (pruefe).',
      copied: 'Copied: paste into a new cell below, fill in, run.', nocopy: 'Select it and copy with Ctrl+C.',
      csolved: '\u2713 solved in the kernel.', cwrong: 'Checked in the kernel: not yet.', mcalc: 'Exercise', mcode: 'Coding',
      run: '\u25B6 Run in the window', clip: 'Copy to clipboard', pyload: 'Loading Python, once, ~10 s \u2026',
      pypkg: 'Loading packages: ', pyrun: 'Running \u2026', pydone: 'Done.', pyerr: 'Error in the code — nothing counted.',
      pyoff: 'Python in the window is not available here (no internet, or the CDN is blocked). Copy the code into a new cell '
        + 'and check it there with %s — the progress counts the same.', nochk: 'Ran (only the kernel checks this exercise: %s).' } };
  // E33 B3/B6: the words of the tools Lab has and the window lacked (⌨ ⚙ 👤 ✉) and of the account
  var LX = {
    de: { kbd: 'Tastatur', gear: 'Einstellungen', acct: 'Konto', fb: 'Feedback', close: 'Schließen', mode: 'Modus', lang: 'Sprache',
      kl: [['↑ / ↓', 'Fenster zeilenweise'], ['Bild↑ / Bild↓, Leertaste', 'eine Fensterhöhe'], ['Pos1 / Ende', 'Anfang / Ende'],
           ['Griff: ↑ ↓', 'Lesehöhe'], ['Griff: ← →', 'Breite des Panels'], ['Griff: Enter', 'Panel auf/zu'],
           ['Strg + Enter (im Code)', '▶ Ausführen im Fenster'], ['Strg + Mausrad', 'Zoom des Browsers (nicht unser)']],
      kn: 'Klicken Sie zuerst ins Fenster. Mehr Tasten (Zellen, Kernel) gibt es in JupyterLab.',
      fb0: 'Feedback, Fehler und Kontakt: per E-Mail an die Adresse im Notebook (Titelkarte/Anhang).',
      fbS: 'So läuft es hier: Lesefenster ohne Kernel (PyCharm, VS Code …).',
      out: 'Nicht angemeldet', inB: 'Angemeldet', name: 'Name', pw: 'Passwort', pw8: 'Passwort (8 oder mehr)', pw2: 'Passwort noch einmal',
      bIn: 'Anmelden', bNew: 'Neues Konto', bMk: 'Konto anlegen', bNo: 'Abbrechen', bOut: 'Abmelden', bCode: 'Meinen Code zeigen',
      bCopy: 'Kopieren', code: 'Konto-Code DCJ1.… (von einem anderen Gerät, sonst leer lassen)',
      none: 'In diesem Browser gibt es noch kein Konto: „Neues Konto“ oder Konto-Code + Passwort.',
      noName: 'Dieser Name gehört zu keinem Konto in diesem Browser.', made: 'Konto angelegt und angemeldet (nur dieses Notebook).',
      inOk: 'Angemeldet. Ihre Einstellungen gelten für dieses Notebook.', outOk: 'Abgemeldet. Ihr Fortschritt bleibt in diesem Browser.',
      busy: 'Einen Moment …', copied: 'Kopiert.', codeT: 'Ihr Konto-Code — mit dem Passwort außerhalb dieses Browsers aufbewahren:',
      note: 'Name und Passwort gelten in diesem Browser. Auf ein anderes Gerät nehmen Sie das Konto mit dem Konto-Code mit. '
        + 'Ein Passwort lässt sich nicht zurücksetzen.' },
    en: { kbd: 'Keyboard', gear: 'Settings', acct: 'Account', fb: 'Feedback', close: 'Close', mode: 'Mode', lang: 'Language',
      kl: [['↑ / ↓', 'the window line by line'], ['PgUp / PgDn, Space', 'one window height'], ['Home / End', 'start / end'],
           ['Grip: ↑ ↓', 'reading height'], ['Grip: ← →', 'the panel\'s width'], ['Grip: Enter', 'open/fold the panel'],
           ['Ctrl + Enter (in code)', '▶ Run in the window'], ['Ctrl + wheel', 'the browser\'s zoom (not ours)']],
      kn: 'Click into the window first. More keys (cells, kernel) are in JupyterLab.',
      fb0: 'Feedback, errors and contact: by e-mail to the address in the notebook (title card/appendix).',
      fbS: 'Running here: the reading window without a kernel (PyCharm, VS Code …).',
      out: 'Not logged in', inB: 'Logged in', name: 'Name', pw: 'Password', pw8: 'Password (8 or more)', pw2: 'Password again',
      bIn: 'Log in', bNew: 'New account', bMk: 'Create account', bNo: 'Cancel', bOut: 'Log out', bCode: 'Show my code',
      bCopy: 'Copy', code: 'Account code DCJ1.… (from another device, else leave empty)',
      none: 'There is no account in this browser yet: „New account“ or account code + password.',
      noName: 'No account in this browser has this name.', made: 'Account created and logged in (this notebook only).',
      inOk: 'Logged in. Your settings hold for this notebook.', outOk: 'Logged out. Your progress stays in this browser.',
      busy: 'One moment …', copied: 'Copied.', codeT: 'Your account code — keep it, with the password, outside this browser:',
      note: 'Name and password hold in this browser. To another device you take the account with the account code. '
        + 'There is no password reset.' } };
  function X(k) { return LX[de ? 'de' : 'en'][k]; }
  function setLang(x) { de = x === 'de'; L = LT[x]; T = TT[x]; }      // the words; lg (the reader's choice) is set apart (E30 B2)
  setLang(lg);

  // fallback look (see the head comment): before every other style of the page
  // E26.3 KORREKTUR (Tabs unabhängig): nothing of this window is shared with another notebook in the same page —
  // the fallback style carries the notebook's id, the API sits under its id, localStorage keys carry it (K)
  var st = D.createElement('style'); st.setAttribute('data-nbrw-fallback', V); st.setAttribute('data-nbrw-id', ID);
  st.textContent =
    '.nbrw.nbrw{position:relative;display:block;box-sizing:border-box;border:1px solid rgba(120,132,145,.45);border-radius:8px;overflow:hidden}' +
    '.nbrw .nbrw-win{position:relative;box-sizing:border-box;height:var(--nbrw-h,600px);overflow-y:auto;overflow-x:hidden;scrollbar-width:none}' +
    '.nbrw .nbrw-win::-webkit-scrollbar{display:none;width:0;height:0}.nbrw .nbrw-win:focus{outline:none}' +
    '.nbrw .nbrw-win>.nbreading{font-size:calc(15px * var(--nbrw-zoom,1))}' +
    '.nbrw .nbrw-panel{position:absolute;top:0;right:0;bottom:0;width:150px;box-sizing:border-box;display:flex;flex-direction:column;gap:8px;' +
    'padding:8px 8px 10px;border-left:1px solid rgba(120,132,145,.45);font:12px/1.35 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;user-select:none;z-index:2}' +
    '.nbrw .nbrw-bar{display:flex;flex-wrap:wrap;gap:4px;justify-content:center}' +
    '.nbrw .nbrw-btn{min-width:30px;height:28px;padding:0 6px;box-sizing:border-box;cursor:pointer;font:600 12px/1 system-ui,sans-serif;' +
    'color:inherit;background:transparent;border:1px solid rgba(120,132,145,.55);border-radius:6px}' +
    '.nbrw .nbrw-cur{font-weight:700;text-align:center;padding:2px 2px 4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}' +
    '.nbrw .nbrw-track{position:relative;flex:1 1 auto;min-height:120px;margin:0 0 0 14px;border-left:4px solid rgba(120,132,145,.35);border-radius:2px}' +
    '.nbrw .nbrw-thumb{position:absolute;left:-5px;width:6px;min-height:24px;box-sizing:border-box;background:currentColor;opacity:.5;border-radius:3px;cursor:grab}' +
    '.nbrw .nbrw-mark{position:absolute;left:-9px;display:flex;align-items:center;gap:6px;max-width:124px;transform:translateY(-50%);' +
    'cursor:pointer;text-decoration:none;color:inherit;background:transparent;border:0;padding:0;font:inherit}' +
    '.nbrw .nbrw-mark::before{content:"";flex:0 0 auto;width:12px;height:12px;box-sizing:border-box;border-radius:50%;border:2px solid currentColor;background:transparent}' +
    '.nbrw .nbrw-mark.is-active::before{background:currentColor}' +
    '.nbrw .nbrw-lab{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px}.nbrw .nbrw-mark.is-active .nbrw-lab{font-weight:700}' +
    // E26.3 — only what CSS (15-reader.css) does not yet know: cover, panel folded, XP, lock line, code field
    '.nbrw .nbrw-btn.nbrw-wide{width:100%}' +
    '.nbrw[data-nbrw-panel=closed] .nbrw-cur,.nbrw[data-nbrw-panel=closed] .nbrw-xp,.nbrw[data-nbrw-panel=closed] .nbrw-lab{display:none!important}' +
    '.nbrw .nbrw-tools{position:absolute;top:0;left:0;bottom:0;box-sizing:border-box;display:flex;flex-direction:column;gap:8px;padding:8px;' +
    'border-right:1px solid var(--rw-line,rgba(120,132,145,.45));font:12px/1.35 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;' +
    'user-select:none;z-index:2;overflow:hidden;background:var(--rw-surf,transparent);color:var(--rw-ink,inherit)}' +
    '.nbrw[data-nbrw-panel=closed] .nbrw-tools{padding:8px 4px}.nbrw[data-nbrw-panel=closed] .nbrw-tools .nbrw-bar{flex-direction:column;align-items:center}' +
    '.nbrw .nbrw-foot{display:flex;align-items:center;gap:6px;flex:0 0 auto}.nbrw .nbrw-foot .nbrw-cur{flex:1 1 auto;min-width:0;border:0;padding:0}' +
    '.nbrw[data-nbrw-panel=closed] .nbrw-panel{padding:8px 4px 10px}.nbrw[data-nbrw-panel=closed] .nbrw-track{margin-left:12px}' +
    '.nbrw .nbrw-xp{font-size:11px}.nbrw .nbrw-xp-bar{height:6px;border-radius:3px;background:rgba(120,132,145,.3);overflow:hidden;margin-top:3px}' +
    '.nbrw .nbrw-xp-fill{height:100%;width:0;background:#2f8f5f;transition:width .25s}' +
    '.nbrw .nbrw-cover{padding:22px 10px 30px;text-align:center}' +
    '.nbrw .nbrw-cv-lang{display:flex;justify-content:flex-end;gap:2px;margin:0 0 8px}' +
    '.nbrw .nbrw-cv-lang button,.nbrw .nbrw-mode-opt,.nbrw .nbrw-play{cursor:pointer;font:inherit;color:inherit;background:transparent;border:1.5px solid rgba(120,132,145,.55)}' +
    '.nbrw .nbrw-cv-lang button{padding:2px 8px;border-radius:6px;font-size:.8em;font-weight:700}' +
    '.nbrw .nbrw-cv-lang button[aria-pressed=true]{border-color:#2f78b5}' +
    '.nbrw .nbrw-cv-t{font-size:.78em;font-weight:800;letter-spacing:2px;text-transform:uppercase;opacity:.7;margin:18px 0 9px}' +
    '.nbrw .nbrw-cv-tl{display:flex;flex-wrap:wrap;justify-content:center;gap:10px 4px;max-width:760px;margin:0 auto}' +
    '.nbrw .nbrw-cv-dot{display:inline-flex;align-items:center;gap:4px;font-size:12px}' +
    '.nbrw .nbrw-cv-dot::before{content:"";width:11px;height:11px;border-radius:50%;border:2px solid #2f78b5;background:#2f78b5;box-sizing:border-box}' +
    '.nbrw .nbrw-cv-dot[data-kind=calc]::before,.nbrw .nbrw-cv-dot[data-kind=code]::before{width:8px;height:8px;border-radius:2px;background:transparent}' +
    '.nbrw .nbrw-cv-dot[data-kind=code]::before{border-color:#7b4fd6}.nbrw .nbrw-cv-dot[data-st=solved]::before{background:#2f8f5f;border-color:#2f8f5f}' +
    '.nbrw .nbrw-cv-dot[data-st=locked]{opacity:.5}.nbrw .nbrw-cv-lab{margin-right:8px}' +
    '.nbrw .nbrw-modes{display:flex;justify-content:center;gap:10px;flex-wrap:wrap}' +
    '.nbrw .nbrw-mode-opt{display:flex;flex-direction:column;align-items:center;gap:2px;width:150px;padding:10px 10px 9px;border-radius:12px}' +
    '.nbrw .nbrw-mode-opt[aria-checked=true]{border-color:#3fa877;box-shadow:0 0 0 3px rgba(63,168,119,.22)}' +
    '.nbrw .nbrw-mode-ic{font-size:20px;line-height:1.2}.nbrw .nbrw-mode-l{font-weight:800;font-size:.9em}.nbrw .nbrw-mode-d{font-size:.74em;line-height:1.3}' +
    '.nbrw .nbrw-play{display:inline-flex;align-items:center;justify-content:center;width:84px;height:84px;margin:22px auto 6px;padding:0 0 0 6px;border-radius:50%;font-size:30px;border:2px solid #2f78b5}' +
    '.nbrw .nbrw-play-lab{display:block;font-weight:800;font-size:.82em;letter-spacing:2.4px;text-transform:uppercase}' +
    '.nbrw .nbrw-mark[data-kind=chap][data-st=locked]::before,.nbrw .nbrw-cv-dot[data-st=locked]::before{content:"\\1F512";border:0;background:none;font-size:10px;line-height:12px}' +
    '.nbrw .nbrw-acct{margin:14px auto 0;font-size:.85em;opacity:.85;max-width:560px}.nbrw .nbrw-acct summary{cursor:pointer}' +
    '.nbrw .nbrw-lockmsg{margin:10px auto;padding:10px 14px;border:1px dashed rgba(120,132,145,.7);border-radius:10px;font-weight:600;text-align:center}' +
    '.nbrw .nbrw-code{position:relative;margin:8px 0;border:1px solid rgba(120,132,145,.55);border-radius:6px;font:.93em/1.45 ui-monospace,Consolas,"DejaVu Sans Mono",monospace}' +
    '.nbrw .nbrw-hl-k{color:#8b3fbf!important}.nbrw .nbrw-hl-s{color:#2f8f5f!important}.nbrw .nbrw-hl-c{color:#7a8794!important;font-style:italic}' +
    '.nbrw .nbrw-hl-n{color:#b5560c!important}.nbrw .nbrw-hl-f{color:#1d5c8a!important}' +
    '.nbrw .nbrw-run{margin:2px 6px 2px 0;padding:4px 12px;cursor:pointer;font:600 .86em/1.4 system-ui,sans-serif;border:1px solid #2f78b5;border-radius:6px;color:inherit;background:transparent}' +
    '.nbrw .nbrw-runst{font-size:.86em;opacity:.85}.nbrw .nbrw-out{margin:6px 0;padding:6px 10px;max-height:240px;overflow:auto;white-space:pre-wrap;' +
    'border-left:3px solid rgba(120,132,145,.6);font:.86em/1.4 ui-monospace,Consolas,monospace}.nbrw .nbrw-out[data-err="1"]{border-left-color:#c0392b}' +
    // E30 B6 — the timeline like Lab: kinds, pips, the reading-height marker, the hover/lock box, the language line, the text size
    '.nbrw .nbrw-mark[data-kind=group]::before{width:11px;height:11px;border-radius:2px;transform:rotate(45deg);background:#4a5866;border-color:#4a5866}' +
    '.nbrw .nbrw-mark[data-kind=title]::before{width:14px;height:14px;margin-left:-2px;background:#2f78b5;border-color:#2f78b5}' +
    '.nbrw .nbrw-mark[data-kind=sub]::before{width:8px;height:8px;margin-left:2px}' +
    '.nbrw .nbrw-mark[data-kind=end]::before,.nbrw .nbrw-mark[data-kind=yoc]::before{border-radius:2px;width:10px;height:10px}' +
    '.nbrw .nbrw-mark[data-kind=yoc]::before{border-style:dashed}' +
    '.nbrw .nbrw-mark.is-sel::before{box-shadow:0 0 0 3px rgba(47,120,181,.35)}' +
    '.nbrw .nbrw-mark.nbrw-crowd .nbrw-lab,.nbrw .nbrw-mark.nbrw-crowd .nbrw-pips{visibility:hidden}' +
    '.nbrw .nbrw-mark .nbrw-lab{min-width:0;flex:0 1 auto}' +
    '.nbrw .nbrw-pips{display:inline-flex;align-items:center;gap:3px;flex:0 0 auto}' +
    '.nbrw .nbrw-pip{width:8px;height:8px;box-sizing:border-box;border:1.5px solid #2f78b5;border-radius:2px;cursor:pointer}' +
    '.nbrw .nbrw-pip[data-kind=code]{border-color:#7b4fd6}.nbrw .nbrw-pip[data-st=solved]{background:#2f8f5f;border-color:#2f8f5f}' +
    '.nbrw .nbrw-pip[data-st=wrong]{border-color:#c0392b}.nbrw .nbrw-pip[data-st=locked]{opacity:.45;border-style:dashed}' +
    '.nbrw[data-nbrw-panel=closed] .nbrw-pips{display:none!important}' +
    // the reading height: a knob LEFT of the rail with a short line to it — never over a mark's dot (a click there is the mark's)
    '.nbrw .nbrw-rl{position:absolute;left:-21px;width:11px;height:11px;margin-top:-5.5px;box-sizing:border-box;border-radius:50%;' +
    'background:#2f78b5;box-shadow:0 0 0 2px rgba(47,120,181,.25),0 0 8px rgba(47,120,181,.45);cursor:ns-resize;z-index:3;touch-action:none}' +
    '.nbrw .nbrw-rl::after{content:"";position:absolute;left:10px;top:4.5px;width:9px;height:2px;background:#2f78b5;pointer-events:none}' +
    '.nbrw .nbrw-tip{position:absolute;z-index:6;min-width:150px;max-width:260px;box-sizing:border-box;flex-direction:column;gap:3px;padding:8px 11px;' +
    'border-radius:10px;font:12px/1.4 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;white-space:pre-line;pointer-events:none;' +
    'background:var(--rw-surf,#fff);color:var(--rw-ink,#1f2933);border:1px solid var(--rw-line,#c3ced8);box-shadow:0 4px 14px rgba(0,0,0,.18)}' +
    '.nbrw .nbrw-tip-h{display:block;text-align:center;font-weight:700}.nbrw .nbrw-tip-t{display:block;text-align:left;color:var(--rw-q,inherit)}' +
    '.nbrw .nbrw-langnote{margin:6px auto 4px;max-width:640px;padding:6px 12px;border:1px dashed rgba(120,132,145,.6);border-radius:8px;' +
    'font-size:12px;line-height:1.4;text-align:center;opacity:.9}' +
    '.nbrw .nbrw-fs .nbfs-val{min-width:44px;text-align:center;font:600 12px/28px system-ui,sans-serif;cursor:pointer;user-select:none}' +
    // E31 — the floating tool column (T2), its scroll bar (S1), the grip (P1/L1), the marker (M1), the reading line, the
    // preview's one-row timeline (T1). Geometry is set inline by place()/sizeCtl() (× --nbgs); colours here and in 15-reader
    '.nbrw .nbrw-tools .nbrw-row{display:flex;justify-content:center;gap:var(--nbrw-tgap,4px);flex:0 0 auto}' +
    '.nbrw .nbrw-tools .nbrw-val{display:block;text-align:center;font:600 10px/1.2 system-ui,sans-serif;opacity:.75;cursor:pointer;user-select:none}' +
    '.nbrw .nbrw-sb{position:relative;flex:1 1 auto;min-height:40px;align-self:center;border-radius:4px;cursor:pointer;' +
    'background:var(--rw-track,rgba(120,132,145,.25))}' +
    '.nbrw .nbrw-sb>.nbrw-thumb{position:absolute;left:0;right:0;width:auto;min-height:24px;border-radius:4px;cursor:grab;' +
    'background:var(--rw-acc,#2f78b5);opacity:.6}' +
    '.nbrw .nbrw-grip{position:absolute;z-index:5;box-sizing:border-box;display:flex;align-items:center;justify-content:center;' +
    'border-radius:50%;border:2px solid var(--rw-acc,#2f78b5);background:var(--rw-surf,#fff);color:var(--rw-acc,#2f78b5);' +
    'font:700 14px/1 system-ui,sans-serif;cursor:grab;touch-action:none;user-select:none;box-shadow:0 1px 4px rgba(0,0,0,.18)}' +
    '.nbrw .nbrw-grip:hover,.nbrw .nbrw-grip[data-drag]{background:var(--rw-acc,#2f78b5);color:var(--rw-surf,#fff)}' +
    '.nbrw .nbrw-grip[data-drag]{cursor:grabbing}.nbrw .nbrw-grip::after{display:none!important}' +
    '.nbrw .nbrw-line{position:absolute;z-index:4;height:0;pointer-events:none;border-top:1px dashed var(--rw-acc,#2f78b5);opacity:.35}' +
    '.nbrw .nbrw-line[data-drag]{border-top-style:solid;opacity:.8}' +
    '.nbrw .nbrw-marker{position:absolute;z-index:3;box-sizing:border-box;border-radius:50%;pointer-events:none;' +
    'background:var(--rw-acc,#2f78b5);box-shadow:0 0 0 3px rgba(47,120,181,.25),0 0 10px rgba(47,120,181,.55);transition:border-radius .2s}' +
    '.nbrw .nbrw-marker:is([data-kind=calc],[data-kind=code],[data-kind=end],[data-kind=yoc]){border-radius:3px}' +
    '.nbrw .nbrw-marker[data-kind=group]{border-radius:2px;transform:rotate(45deg)}' +
    '.nbrw .nbrw-marker[data-st=solved]{background:#2f8f5f}.nbrw .nbrw-marker[data-st=locked]{opacity:.6}' +
    '.nbrw .nbrw-marker::after{content:"";position:absolute;left:50%;width:2px;margin-left:-1px;bottom:50%;height:0;opacity:0;' +
    'background:linear-gradient(to top,var(--rw-acc,#2f78b5),transparent);transition:height .5s ease-out,opacity .5s ease-out}' +
    '.nbrw .nbrw-marker[data-dir=up]::after{bottom:auto;top:50%;background:linear-gradient(to bottom,var(--rw-acc,#2f78b5),transparent)}' +
    '.nbrw .nbrw-marker.is-moving::after{height:28px;opacity:.7;transition:none}' +
    '.nbrw .nbrw-cv-tl[data-nbrw-row]{display:block!important;position:relative!important;max-width:100%!important;padding:0!important;margin:14px auto 8px!important}' +
    '.nbrw .nbrw-cv-tl[data-nbrw-row]::before{display:none!important}' +
    '.nbrw .nbrw-cv-scroll{position:relative;overflow-x:auto;overflow-y:hidden;scrollbar-width:thin;margin:0 auto}' +
    '.nbrw .nbrw-cv-in{position:relative;margin:0 auto}' +
    '.nbrw .nbrw-cv-line{position:absolute;height:4px;margin-top:-2px;border-radius:2px;background:var(--rw-track,rgba(120,132,145,.35))}' +
    '.nbrw .nbrw-cv-tl[data-nbrw-row] .nbrw-cv-dot{position:absolute!important;display:block!important;width:0;height:0;padding:0;margin:0}' +
    '.nbrw .nbrw-cv-tl[data-nbrw-row] .nbrw-cv-dot::before{position:absolute;left:0;top:0;transform:translate(-50%,-50%);margin:0!important}' +
    '.nbrw .nbrw-cv-tl[data-nbrw-row] .nbrw-cv-lab{position:absolute!important;left:0;transform:translateX(-50%);white-space:nowrap!important;' +
    'max-width:none!important;display:block!important;-webkit-line-clamp:none!important;overflow:visible!important;margin:0!important}' +
    '.nbrw .nbrw-cv-tl[data-nbrw-row] .nbrw-cv-dot[data-side=up] .nbrw-cv-lab{bottom:12px}' +
    '.nbrw .nbrw-cv-tl[data-nbrw-row] .nbrw-cv-dot[data-side=down] .nbrw-cv-lab{top:12px}' +
    '.nbrw .nbrw-cv-tl[data-nbrw-row] .nbrw-cv-dot:is([data-kind=title],[data-kind=group]) .nbrw-cv-lab{text-transform:uppercase;letter-spacing:.12em;font-weight:800}' +
    // E33 — the drawers (⌨ ⚙ 👤 ✉), the account form, the cover timeline's description line (B2); fallback only
    '.nbrw .nbrw-drawer{position:absolute;z-index:7;box-sizing:border-box;padding:10px 12px 12px;border-radius:10px;' +
    'font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.4;background:var(--rw-surf,#fff);color:var(--rw-ink,#1f2933);' +
    'border:1px solid var(--rw-line,#c3ced8);box-shadow:0 6px 18px rgba(0,0,0,.2)}' +
    '.nbrw .nbrw-dr-h{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:0 0 8px;font-size:1.1em}' +
    '.nbrw .nbrw-dr-t{margin:10px 0 4px;font-size:.8em;font-weight:800;letter-spacing:.1em;text-transform:uppercase;opacity:.75}' +
    '.nbrw .nbrw-dr-row{display:flex;flex-wrap:wrap;gap:4px}.nbrw .nbrw-dr-n,.nbrw .nbrw-acct-note{margin:8px 0 0;font-size:.88em;opacity:.8}' +
    '.nbrw .nbrw-dbtn{cursor:pointer;font:inherit;color:inherit;background:transparent;border:1px solid var(--rw-line,rgba(120,132,145,.55));border-radius:6px;padding:3px 9px}' +
    '.nbrw .nbrw-dbtn[aria-checked=true],.nbrw .nbrw-dbtn[aria-pressed=true],.nbrw .nbrw-dbtn.is-primary{border-color:var(--rw-acc,#2f78b5);font-weight:700}' +
    '.nbrw .nbrw-dr-x{border:0;padding:0 4px;font-size:1.2em;line-height:1}' +
    '.nbrw .nbrw-keys{border-collapse:collapse;width:100%}.nbrw .nbrw-keys td{padding:2px 6px 2px 0;vertical-align:top}' +
    '.nbrw .nbrw-keys kbd{font:600 .92em ui-monospace,Consolas,monospace;white-space:nowrap}' +
    '.nbrw .nbrw-acct-form{display:flex;flex-direction:column;gap:6px;text-align:left}' +
    '.nbrw .nbrw-acct-in{font:inherit;color:inherit;background:transparent;padding:4px 8px;border:1px solid var(--rw-line,rgba(120,132,145,.55));border-radius:6px}' +
    '.nbrw .nbrw-acct-me{font-weight:700}.nbrw .nbrw-acct-msg:empty{display:none}.nbrw .nbrw-acct-msg[data-kind=err]{color:#c0392b}' +
    '.nbrw .nbrw-acct-msg[data-kind=ok]{color:#2f8f5f}.nbrw .nbrw-acct-f{max-width:340px;margin:8px auto 0}' +
    '.nbrw .nbrw-cv-desc[hidden]{display:block!important;visibility:hidden}.nbrw .nbrw-cv-desc{height:1.45em;max-width:640px;margin:2px auto 0;font-size:12px;line-height:1.45;text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}' +
    '.nbrw .nbrw-cv-desc b{margin-right:.5em}.nbrw .nbrw-cv-dot.is-hov::before,.nbrw .nbrw-cv-dot.is-pin::before{box-shadow:0 0 0 3px rgba(47,120,181,.35)}' +
    '.nbrw .nbrw-mark.nbrw-noname .nbrw-lab{display:none}' +
    '.nbrw .nbrw-cv-dot:is([data-kind=title],[data-kind=group]){cursor:pointer}.nbrw .nbrw-cv-dot.is-shut::before{opacity:.55}';
  var hd = D.head || D.documentElement; hd.insertBefore(st, hd.firstChild);

  function imp(el, k, v) { if (v == null || v === '') el.style.removeProperty(k); else el.style.setProperty(k, v, 'important'); }
  function mk(tag, cls, txt) { var e = D.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }

  var wrap = mk('div', 'nbrw'); wrap.setAttribute('data-nbrw-v', V); wrap.setAttribute('data-nbrw-id', ID);
  var win = mk('div', 'nbrw-win'); win.tabIndex = 0;
  win.setAttribute('role', 'region'); win.setAttribute('aria-label', L.nav);
  win.style.overscrollBehavior = 'contain';   // E33 B1c: at its ends the wheel stays in the window (was: on to the IDE)
  var pan = mk('div', 'nbrw-panel');
  root.parentNode.insertBefore(wrap, root);
  win.appendChild(root); wrap.appendChild(win); wrap.appendChild(pan);

  // ---- E26.3 · 1: cover | document inside the reading version -------------
  // everything but the styles and Python's cover goes into .nbrw-doc
  var cover = root.querySelector('.nbrw-cover'), ownCover = !cover;
  var doc = mk('div', 'nbrw-doc');
  [].slice.call(root.childNodes).forEach(function (n) {
    if (n.nodeType === 1 && (n.tagName === 'STYLE' || n === cover)) return;
    doc.appendChild(n);
  });
  if (ownCover) { cover = mk('div', 'nbrw-cover'); cover.setAttribute('data-nbrw-own', '1'); }
  root.appendChild(cover); root.appendChild(doc);
  var view = '', docTop = -1;           // E33 B4: -1 = never shown: the document's start (below the room above it)

  // E31 T2: the tools are a floating column on the left like Lab's corner (.nbcorner): loose buttons, no box,
  // in rows of two — ◂ preview · 🔍−/🔍+ lens · A−/A+ text size · ⊖/⊕ controls · ↕−/↕+ window height · ◐ ✿ —
  // and under them the window's scroll bar (S1, Lab's .nbsb)
  var top = mk('div', 'nbrw-top nbrw-row');
  var bCover = mk('button', 'nbrw-btn nbrw-wide'); bCover.type = 'button'; bCover.setAttribute('data-act', 'cover');
  bCover.addEventListener('click', function (e) { e.preventDefault(); setView('cover'); });
  top.appendChild(bCover);
  var bar = mk('div', 'nbrw-bar');
  var B = {};
  function btn(a, t, into) {
    var b = mk('button', 'nbrw-btn', t); b.type = 'button'; b.setAttribute('data-act', a);
    b.addEventListener('click', function (e) { e.preventDefault(); act(a); });
    into.appendChild(b); B[a] = b; return b;
  }
  var rows = {};
  [['zoom', [['a-', '🔍−'], ['a+', '🔍+']]], ['h', [['h-', '↕−'], ['h+', '↕+']]],
   ['look', [['theme', '◐'], ['skin', '✿']]]].forEach(function (r) {
    var row = rows[r[0]] = mk('div', 'nbrw-row nbrw-bar'); r[1].forEach(function (a) { btn(a[0], a[1], row); });
  });
  // E30 (E29 D7): A−/A+ the text size; E31 G1: ⊖/⊕ the controls — each with its value under it (double click = 100 %)
  var fsRow = mk('div', 'nbrw-fs nbrw-bar'), fsV = mk('output', 'nbfs-val nbrw-val');
  var fsBtns = fsRow.appendChild(mk('div', 'nbrw-row'));
  btn('f-', 'A−', fsBtns); btn('f+', 'A+', fsBtns); fsRow.appendChild(fsV);
  fsV.addEventListener('dblclick', function (e) { e.preventDefault(); fsSet(FS.std); });
  var gsRow = mk('div', 'nbrw-gs nbrw-bar'), gsV = mk('output', 'nbgs-val nbrw-val');
  var gsBtns = gsRow.appendChild(mk('div', 'nbrw-row'));
  btn('g-', '⊖', gsBtns); btn('g+', '⊕', gsBtns); gsRow.appendChild(gsV);
  gsV.addEventListener('dblclick', function (e) { e.preventDefault(); gsSet(GS.std); });
  // E33 B4: the panel's second fold button (under the timeline, beside the chapter's name) is gone from the panel —
  // the grip folds it, and like Lab's column (its half-round ‹ under the lens) the tool column keeps one
  var foot = mk('div', 'nbrw-foot'), bPan = mk('button', 'nbrw-btn', '›'); bPan.type = 'button'; bPan.setAttribute('data-act', 'panel');
  bPan.addEventListener('click', function (e) { e.preventDefault(); act('panel'); });
  B.panel = bPan; top.appendChild(bPan);
  var cur = mk('div', 'nbrw-cur');
  foot.appendChild(cur);
  // E33 B6: the tools Lab has and the window lacked — ⌨ keys · ⚙ settings (mode, language, feedback) · 👤 account
  // · ✉ feedback — at the foot of the column as in Lab (.nbcorner: ⌨ ⚙ 👤); each opens a drawer beside the column
  var low = mk('div', 'nbrw-row nbrw-low'), low2 = mk('div', 'nbrw-row nbrw-low'), low3 = mk('div', 'nbrw-row nbrw-low');
  // names as css-E33 (VERTRAG-E33-css B6): kbd · gear · mode · acct · fb
  [['kbd', '\u2328', low], ['gear', '\u2699', low], ['mode', '\u270E', low2], ['acct', '\uD83D\uDC64', low2], ['fb', '\u2709', low3]].forEach(function (a) {
    var b = mk('button', 'nbrw-btn nbrw-tool', a[1]); b.type = 'button'; b.setAttribute('data-act', a[0]); b.setAttribute('aria-expanded', 'false');
    b.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); drawer(drw.getAttribute('data-kind') === a[0] ? '' : a[0]); });
    a[2].appendChild(b); B[a[0]] = b;
  });
  var drw = mk('div', 'nbrw-drawer'); drw.setAttribute('role', 'dialog'); imp(drw, 'display', 'none');
  var xp = mk('div', 'nbrw-xp'), xpT = mk('div', 'nbrw-xp-t'), xpB = mk('div', 'nbrw-xp-bar'), xpF = mk('div', 'nbrw-xp-fill');
  xpB.appendChild(xpF); xp.appendChild(xpT); xp.appendChild(xpB);
  var track = mk('div', 'nbrw-track');
  // S1: the scroll bar in the tool column (.nbrw-sb; the thumb keeps its class .nbrw-thumb)
  var sb = mk('div', 'nbrw-sb'), thumb = mk('div', 'nbrw-thumb nbrw-sb-th');
  sb.setAttribute('role', 'scrollbar'); sb.setAttribute('aria-orientation', 'vertical'); sb.appendChild(thumb);
  // P1/L1: the grip (Lab's .nbgrip) at the panel's left edge on the reading height; it keeps .nbrw-rl (the
  // reading-height knob of E30); M1: the marker on the rail; the reading line across the window while dragging
  var rlm = mk('div', 'nbrw-rl nbrw-grip'); rlm.setAttribute('role', 'slider'); rlm.tabIndex = 0;
  var marker = mk('div', 'nbrw-marker'); marker.setAttribute('aria-hidden', 'true');
  var rline = mk('div', 'nbrw-line'); rline.setAttribute('aria-hidden', 'true');
  track.appendChild(marker);
  var tools = mk('div', 'nbrw-tools');
  [top, rows.zoom, fsRow, gsRow, rows.h, rows.look, sb, low, low2, low3].forEach(function (x) { tools.appendChild(x); });
  if (HULL) rows.h.setAttribute('aria-hidden', 'true');      // E38a J1: the page sets the height (hidden in sizeCtl)
  pan.appendChild(xp); pan.appendChild(track); pan.appendChild(foot);
  wrap.appendChild(tools); wrap.appendChild(rlm); wrap.appendChild(rline); wrap.appendChild(drw);
  var tip = mk('div', 'nbrw-tip'); tip.setAttribute('role', 'tooltip'); imp(tip, 'display', 'none');
  var tipH = tip.appendChild(mk('b', 'nbrw-tip-h')), tipS = tip.appendChild(mk('span', 'nbrw-tip-t'));
  wrap.appendChild(tip);
  var note = mk('div', 'nbrw-langnote'); note.setAttribute('role', 'note'); imp(note, 'display', 'none');
  doc.insertBefore(note, doc.firstChild);
  // E33 B4 — ROOM TO SCROLL above the title and below the end (≈ one window height each): a click on Title or on
  // „End of the guided part“ brings it to the reading height wherever that stands (the window could not go there)
  var padT = mk('div', 'nbrw-pad'), padB = mk('div', 'nbrw-pad');
  [padT, padB].forEach(function (p, i) { p.setAttribute('data-at', i ? 'bottom' : 'top'); p.setAttribute('aria-hidden', 'true'); imp(p, 'pointer-events', 'none'); imp(p, 'margin', '0'); imp(p, 'padding', '0'); });
  doc.insertBefore(padT, doc.firstChild); doc.appendChild(padB);
  function padTop() { return padT.offsetHeight || 0; }
  function padDoc() {
    var hh = Math.max(HMIN, Math.round(win.clientHeight || h)), o = padT.offsetHeight;
    if (Math.abs(o - hh) < 1) return;
    imp(padT, 'height', hh + 'px'); imp(padB, 'height', hh + 'px');
    if (view === 'doc' && o > 0) win.scrollTop += hh - o;           // the text stays where it was
  }
  // E31 T2/G1: the controls' geometry, × gs — inline (!important): the column floats, no box (15-reader painted
  // the old one); buttons square, the scroll bar 8 px, the panel's buttons and marks × gs
  var TB = 34, TG = 4;                          // Lab's tool button (34 px, css-E31 T2)
  function sizeCtl() {
    var b = Math.round(TB * gs), g = Math.max(2, Math.round(TG * gs)), tw = 2 * b + g;
    imp(tools, 'border', '0'); imp(tools, 'background', 'transparent'); imp(tools, 'box-shadow', 'none');
    imp(tools, 'padding', '0'); imp(tools, 'gap', Math.round(6 * gs) + 'px'); imp(tools, 'overflow', 'visible');
    wrap.style.setProperty('--nbrw-tgap', g + 'px');
    // the column does not fold with the panel (15-reader stacks .nbrw-bar and hid the text size when the panel was shut)
    [].forEach.call(tools.querySelectorAll('.nbrw-row'), function (r) { imp(r, 'display', 'flex'); imp(r, 'flex-direction', 'row'); imp(r, 'flex-wrap', 'nowrap'); imp(r, 'justify-content', 'center'); imp(r, 'gap', g + 'px'); imp(r, 'align-items', 'center'); });
    [fsRow, gsRow].forEach(function (r) { imp(r, 'display', 'flex'); imp(r, 'flex-direction', 'column'); imp(r, 'gap', '1px'); imp(r, 'align-items', 'center'); });
    if (HULL) imp(rows.h, 'display', 'none');                   // E38a J1: no ↕ in lesen.html
    [].forEach.call(tools.querySelectorAll('.nbrw-btn'), function (x) {
      imp(x, 'height', b + 'px'); imp(x, 'min-width', b + 'px'); imp(x, 'font-size', Math.round(12 * gs * 10) / 10 + 'px');
      imp(x, 'padding', '0'); imp(x, 'line-height', '1');
      if (x.parentNode && x.parentNode.classList.contains('nbrw-row')) imp(x, 'width', b + 'px');
    });
    [fsV, gsV].forEach(function (o) { imp(o, 'font-size', Math.round(10 * gs * 10) / 10 + 'px'); imp(o, 'min-width', '0'); imp(o, 'line-height', '1.2'); });
    imp(sb, 'width', Math.round(8 * gs) + 'px');
    // E33 B5: everything of the PANEL × ks (the panel's width over its standard × the lens, Lab's --nbk × --nbzf):
    // grip, marker, hover box, chapter line, XP — never × gs (the tools' size)
    var gp = Math.round(28 * ks);
    imp(rlm, 'width', gp + 'px'); imp(rlm, 'height', gp + 'px'); imp(rlm, 'margin', '0'); imp(rlm, 'font-size', Math.round(14 * ks) + 'px');
    imp(rlm, 'left', 'auto'); imp(rlm, 'right', 'auto'); imp(rlm, 'box-shadow', '');
    var mk0 = Math.round(12 * ks);
    imp(marker, 'width', mk0 + 'px'); imp(marker, 'height', mk0 + 'px');
    imp(tip, 'font-size', Math.round(12 * ks * 10) / 10 + 'px'); imp(tip, 'max-width', Math.round(260 * ks) + 'px'); imp(tip, 'min-width', Math.round(150 * ks) + 'px');
    imp(cur, 'font-size', Math.round(12 * ks * 10) / 10 + 'px'); imp(xpT, 'font-size', Math.round(11 * ks * 10) / 10 + 'px');
    wrap.style.setProperty('--nbrw-pk', String(Math.round(ks * 1000) / 1000));
    return tw;
  }

  function label() {
    ['h+', 'h-', 'a+', 'a-', 'f+', 'f-', 'g+', 'g-'].forEach(function (k) { B[k].title = L[k]; B[k].setAttribute('aria-label', L[k]); });
    fsV.title = L.fsT; gsV.title = L.gsT; rlm.title = L.grip; rlm.setAttribute('aria-label', L.rl); sb.title = L.sb;
    rlm.textContent = popen ? '\u203A' : '\u2039';
    var t = L.theme + (th ? L[THEMES[th]] : L.auto), s = L.skin + SKINS[sk];
    B.theme.title = t; B.theme.setAttribute('aria-label', t); B.theme.classList.toggle('is-on', th > 0);
    B.skin.title = s; B.skin.setAttribute('aria-label', s);
    var pt = popen ? L.pin : L.pout;
    B.panel.textContent = popen ? '\u203A' : '\u2039'; B.panel.title = pt; B.panel.setAttribute('aria-label', pt);
    B.panel.setAttribute('aria-expanded', String(popen));
    bCover.textContent = '\u25C2';          // the word only for screen readers and tests (the column is narrow)
    var bw = bCover.appendChild(mk('span', 'nbrw-sr', ' ' + L.cover)); imp(bw, 'display', 'none');
    bCover.title = L.cover; bCover.setAttribute('aria-label', L.cover);
    win.setAttribute('aria-label', L.nav);
  }
  // colours: the reading version's own (fallback only — 15-reader.css paints .nbrw with !important)
  // E33 D (VS Code, K2): the window followed the OS's scheme, not VS Code's theme — VS Code's webview tells it on
  // <body> (vscode-dark | vscode-light | vscode-high-contrast[-light]) and in --vscode-editor-background; on
  // „automatic“ the window takes that (data-nbrw-host=vscode), the reader's ◐ still wins
  function hostTheme() {
    var b = D.body, c = (b && b.className) || '', v = '';
    if (/\bvscode-high-contrast-light\b|\bvscode-light\b/.test(c)) return 'light';
    if (/\bvscode-(dark|high-contrast)\b/.test(c)) return 'dark';
    try { v = W.getComputedStyle(D.documentElement).getPropertyValue('--vscode-editor-background').trim(); } catch (e) {}
    var m = /^#([0-9a-f]{6})$/i.exec(v) || /^#([0-9a-f]{3})$/i.exec(v);
    if (!m) return '';
    var x = m[1].length === 3 ? m[1].replace(/./g, '$&$&') : m[1], r = parseInt(x.slice(0, 2), 16), g = parseInt(x.slice(2, 4), 16), bl = parseInt(x.slice(4, 6), 16);
    return 0.2126 * r + 0.7152 * g + 0.0722 * bl < 128 ? 'dark' : 'light';
  }
  function paint() {
    var ht = hostTheme();
    if (ht) wrap.setAttribute('data-nbrw-host', 'vscode'); else wrap.removeAttribute('data-nbrw-host');
    if (th) wrap.setAttribute('data-nbrw-theme', THEMES[th]); else if (ht) wrap.setAttribute('data-nbrw-theme', ht); else wrap.removeAttribute('data-nbrw-theme');
    wrap.setAttribute('data-nbrw-skin', SKINS[sk]);
    wrap.style.color = ''; wrap.style.backgroundColor = '';
    var cs = W.getComputedStyle(root);
    wrap.style.color = cs.color; wrap.style.backgroundColor = cs.backgroundColor;
  }

  // the visible words of an element in the chosen language
  function txt(el) {
    if (!el) return '';
    if (!BI) return (el.textContent || '').trim();
    var c = el.cloneNode(true);
    var sl = de ? 'de' : 'en';          // the language shown now (E30 B2: the document's where it has only one)
    [].forEach.call(c.querySelectorAll('[data-nbrw-l]'), function (x) { if (x.getAttribute('data-nbrw-l') !== sl) x.remove(); });
    return (c.textContent || '').replace(/\s+/g, ' ').trim();
  }

  // ---- E30 B6 (2026-10-12, Werkstatt JS) — THE TIMELINE LIKE LAB -----------
  // Lab's rail cannot come into this window: it lives in another output (in
  // PyCharm another page), it is ~700 KB of script bound to the widgets' DOM
  // (Collapse headers, .jp-WindowedPanel) — and Lab must not change (lab_same).
  // So this window keeps ONE panel of its own, and it follows Lab's model:
  // the ENTRIES are what Lab's timeline shows, read from the reading version —
  // the title card, every fold (<details data-acc>: group, chapter, viz,
  // practice, code; a chapter of the contents list is 'chap', the other
  // sections 'sub'), the end of the guided part, your own cells. A mark stands
  // at the height of its heading in the window (the timeline is the window's
  // map, 1:1, as Lab's rail stands beside the document); what is folded away
  // or hidden by the mode has no mark. A chapter's mark carries one pip per
  // exercise with its state. The marker on the timeline is the READING
  // HEIGHT (drag it): a click on a mark opens its fold (and the folds around
  // it) and puts its heading on that line; it stays there (pinned) while
  // folds open or close, pictures come, the lens or the text size change —
  // until the reader scrolls himself. A click on the chosen, open mark folds
  // it (it stays on the line). A locked chapter (its mark, its pips) is no
  // place to go: a box says why (Lab E29 D3). Hover: the name alone in line 1,
  // then what it is and its state.
  var chaps = [], ents = [], sel = null, pin = null;
  function byId(id) { try { return root.querySelector('[id="' + id.replace(/["\\]/g, '\\$&') + '"]'); } catch (e) { return null; } }
  function titleCard() {
    return [].filter.call(doc.children, function (e) { return e.tagName === 'DIV' && /text-align:\s*center/.test(e.getAttribute('style') || '') && e.querySelector('[class*="nbtitle"]'); })[0] || null;
  }
  function collect() {
    chaps = [];
    [].forEach.call(root.querySelectorAll('ol.nbread-toc a[href^="#"]'), function (a) {
      var t = byId(decodeURIComponent(a.getAttribute('href').slice(1)));
      if (t) chaps.push({ el: t, a: a, title: txt(a) });
    });
    ents = [];
    var card = titleCard(), seen = [];
    if (card) ents.push({ kind: 'title', el: card });
    [].forEach.call(doc.querySelectorAll('details[data-acc]'), function (d) {
      var k = d.getAttribute('data-kind') || '', e = { det: d, el: d, kind: 'sub' };
      if (k === 'group') e.kind = 'group';
      else if (k === 'chapter') {
        // a chapter's anchor (span#nbr-…) stands just BEFORE its fold, in its own .nbread-b
        chaps.forEach(function (c, i) {
          var p = c.el.parentElement, n = p && p.nextElementSibling;
          if (e.kind !== 'chap' && (n === d || (c.el.closest && c.el.closest('details[data-kind=chapter]') === d))) { e.kind = 'chap'; e.ch = i; c.e = e; }
        });
      } else if (k === 'viz') e.kind = 'viz';
      else if (k === 'practice' || k === 'code') {
        e.kind = k === 'code' ? 'code' : 'calc';
        tasks.forEach(function (t) { if (!e.t && t.key && t.kind === e.kind && d.contains(t.el)) e.t = t; });
        if (e.t) seen.push(e.t); else e.kind = 'sub';
      }
      ents.push(e);
    });
    tasks.forEach(function (t) { if (t.key && seen.indexOf(t) < 0) ents.push({ kind: t.kind, el: t.el, t: t }); });
    var end = doc.querySelector('.nbread-end'); if (end) ents.push({ kind: 'end', el: end });
    var yo = doc.querySelector('[id^="nbr-nbyoc"]'); if (yo) ents.push({ kind: 'yoc', el: yo });
    ents.sort(function (a, b) { return a.el === b.el ? 0 : before(a.el, b.el) ? -1 : 1; });
    readTpl();
    ents.forEach(function (e) { e.tn = tplN[e.kind === 'title' ? '#title' : e.kind === 'yoc' ? '#yoc' : anchorBefore(e.det || e.el)] || null; });
    // the chapter an entry belongs to: the chapter fold around it (Appendix, end, own cells belong to none)
    var folds = chaps.some(function (c) { return !!c.e; });
    ents.forEach(function (e) {
      e.ci = e.kind === 'chap' ? e.ch : -1;
      if (e.kind !== 'chap') chaps.forEach(function (c, i) { if (folds ? c.e && c.e.det.contains(e.el) : (c.el === e.el || before(c.el, e.el))) e.ci = i; });
      if (e.t) e.t.ent = e;
    });
  }
  function before(a, b) { return !!(a.compareDocumentPosition(b) & 4); }   // a comes before b
  // E30 (claude/VERTRAG-E30-py.md, B6): Python ships Lab's panel markup as an inert <template class="nbrw-rail">
  // whose targets are the reading version's ids — the marks take Lab's names ("Chapter 1: …", "Figure 1: …",
  // "Coding 1: y_von()") and Lab's hover words from it; without it, the names of the reading version's headings
  var tplN = {}, tplLg = '';
  function readTpl() {
    tplN = {};
    var tp = root.querySelector('template.nbrw-rail'), c = tp && tp.content;
    tplLg = tp ? (tp.getAttribute('data-lang') || lgDoc) : '';
    if (!c) return;
    [].forEach.call(c.querySelectorAll('a.nbmap-node'), function (a) {
      var k = a.getAttribute('data-target') || (a.getAttribute('data-top') ? '#title' : a.getAttribute('data-bottom') ? '#yoc' : '');
      if (k) tplN[k.replace(/^#?nbr-/, '')] = a;
    });
  }
  function anchorBefore(el) {     // the anchor (span#nbr-…) in the .nbread-b just before a fold or the end line
    for (var x = el.previousElementSibling, n = 0; x && n < 3; x = x.previousElementSibling, n++) {
      var sp = x.classList && x.classList.contains('nbread-b') ? x.querySelector('span[id]') : null;
      if (sp) return sp.id.replace(/^nbr-/, '');
    }
    return '';
  }
  function tplName(a) {
    var sl = de ? 'de' : 'en', l = a.querySelector('.nbmap-lab'), q = a.querySelector('.nbtasklab');
    if (!(l && l.querySelector('[data-nbrw-l]')) && tplLg && tplLg !== sl) return '';     // only the other language: not ours
    return (l && txt(l)) || (q && txt(q)) || '';
  }
  function tplTitle(a) {
    var sl = de ? 'de' : 'en', t = '';
    try { var j = JSON.parse(a.getAttribute('data-nbl-' + sl) || 'null'); if (j && j.title) t = j.title; } catch (x) {}
    if (!t && (!tplLg || tplLg === sl)) t = a.getAttribute('title') || '';
    return t.replace(/\s+/g, ' ').trim();
  }
  function chapOf(el) { var k = -1; chaps.forEach(function (c, i) { if (c.el === el || before(c.el, el)) k = i; }); return k; }
  function topOf(el) {
    var t = el;    // a hidden target (a locked chapter, a mode-hidden task) measures at its first shown neighbour
    while (t && t !== root && !t.getClientRects().length) t = t.previousElementSibling || t.parentElement;
    return (t || el).getBoundingClientRect().top - win.getBoundingClientRect().top + win.scrollTop;
  }
  function reveal(el) {      // open the accordions around a target
    for (var x = el.parentElement; x && x !== root; x = x.parentElement) if (x.tagName === 'DETAILS' && !x.open) x.open = true;
  }
  // the box a mark stands beside: a fold's head (its summary), the title card, else the element; null when not drawn
  function head(e) {
    if (e.det) { var su = e.det.querySelector(':scope>summary'); return (su && su.querySelector('.nbread-h')) || su || e.det; }   // the heading, not its margins
    if (e.kind === 'title') return e.el.querySelector('[class*="nbtitle-card"]') || e.el;
    return e.el;
  }
  function midY(e) {         // the middle of its head in the window's content (scrollTop units)
    var x = head(e);
    if (!x || !x.getClientRects().length) return null;
    var r = x.getBoundingClientRect();
    if (!(r.height > 0) && e.kind !== 'yoc' && e.kind !== 'end') return null;
    return r.top + r.height / 2 - win.getBoundingClientRect().top + win.scrollTop;
  }
  function lockedE(e) { return e.ci >= 0 && !!(chaps[e.ci] && chaps[e.ci].locked); }
  function stE(e) {
    if (e.kind === 'chap') return lockedE(e) ? 'locked' : 'open';
    if (e.t) return lockedE(e) ? 'locked' : (e.t.el.getAttribute('data-st') || 'open');
    return lockedE(e) ? 'locked' : 'open';
  }
  function nameOf(e) {
    var tn = e.tn ? tplName(e.tn) : '';
    if (tn) return tn;
    if (e.kind === 'chap') return chaps[e.ch].title;
    if (e.kind === 'title') { var h = e.el.querySelector('[class*="nbtitle-h"]'); return txt(h || e.el); }
    if (e.t) return (e.kind === 'code' ? T.mcode : T.mcalc) + ' ' + e.t.key.replace(/^t/, '');
    if (e.kind === 'yoc') return L.k.yoc;
    return txt(head(e)).replace(/^[^\p{L}\p{N}]+/u, '');
  }
  function tasksOf(ci) { return tasks.filter(function (t) { return t.key && !t.off && (t.ent ? t.ent.ci : chapOf(t.el)) === ci; }); }
  var marks = [];
  function drawMarks() {
    marks.forEach(function (m) { m.remove(); }); marks = [];
    tasks.forEach(function (t) { t.mark = null; t.pips = []; });
    ents.forEach(function (e) { e.mark = null; });
    if (view !== 'doc') { rlm.style.display = 'none'; return; }
    ents.forEach(function (e, i) {
      if (e.t && e.t.off) return;                                     // the mode leaves it out
      if (e.kind !== 'chap' && lockedE(e)) return;                   // inside a locked chapter: no mark (Lab: nbgone); its pips stand at the chapter
      var m = mk('button', 'nbrw-mark'), st = stE(e); m.type = 'button';
      e.name = nameOf(e);
      m.setAttribute('data-kind', e.kind); m.setAttribute('data-st', st); m.setAttribute('data-e', String(i));
      if (e.kind === 'chap') m.setAttribute('data-ch', String(e.ch));
      if (e.t) m.setAttribute('data-task', e.t.key);
      m.setAttribute('aria-label', (st === 'locked' ? '\uD83D\uDD12 ' : '') + e.name);
      m.appendChild(mk('span', 'nbrw-lab', e.name));
      if (e.kind === 'chap') {                                        // one pip per exercise of this chapter, with its state
        var ps = tasksOf(e.ch);
        if (ps.length) {
          var pw = mk('span', 'nbrw-pips');
          ps.forEach(function (t) {
            var p = mk('span', 'nbrw-pip'); p.setAttribute('data-kind', t.kind); p.setAttribute('data-task', t.key);
            p.setAttribute('data-st', lockedE(e) ? 'locked' : (t.el.getAttribute('data-st') || 'open'));
            pw.appendChild(p); t.pips.push(p);
          });
          m.appendChild(pw);
        }
      }
      m.addEventListener('click', function (ev) {
        ev.preventDefault(); ev.stopPropagation();
        var p = ev.target && ev.target.closest ? ev.target.closest('.nbrw-pip') : null, t = p ? taskBy(p.getAttribute('data-kind'), p.getAttribute('data-task')) : null;
        hit(t && t.ent && !t.off ? t.ent : e, ev, m);
      });
      m.addEventListener('mouseenter', function () { tipOn(e, m); });
      m.addEventListener('focus', function () { tipOn(e, m); });
      m.addEventListener('mouseleave', tipOff); m.addEventListener('blur', tipOff);
      track.appendChild(m); marks.push(m); e.mark = m;
      if (e.t) e.t.mark = m;
      if (e === sel) m.classList.add('is-sel');
    });
    curI = -2; sync();
  }
  // the marks follow the window (1:1): a mark is shown while its head is drawn and inside the timeline
  // E31 G1: a mark is drawn × gs (dot, name, pips together, from the rail); M1: the marker on the rail at the
  // reading height takes the kind and state of the mark passing it; the grip and the line stand on that height
  var here = null;
  function pos() {
    if (view !== 'doc') return;
    var tr = track.getBoundingClientRect(), wr = win.getBoundingClientRect(), th = track.clientHeight, last = -99, tp = win.scrollTop;
    var crowd = 14 * ks, lw = Math.max(20, ((pan.clientWidth || 0) - (track.offsetLeft || 0) - 16 * ks) / ks);      // E33 B5: × ks, not gs
    var ry = Math.round(rlNow() + wr.top - tr.top), best = null, bd = 1e9;
    ents.forEach(function (e) {
      var m = e.mark; if (!m) return;
      var y = midY(e), ty = y == null ? null : Math.round(y - tp + wr.top - tr.top);
      var on = ty != null && ty >= 0 && ty <= th;
      if (on) {
        imp(m, 'display', ''); m.style.top = ty + 'px';
        imp(m, 'transform', ks === 1 ? '' : 'translateY(-50%) scale(' + ks + ')'); imp(m, 'transform-origin', ks === 1 ? '' : '9px 50%');
        imp(m, 'max-width', Math.round(lw) + 'px');
        m.classList.toggle('nbrw-noname', lw < 84);     // E33 B4: the rail in the middle — too little room right of it: no name (Lab: the hover box)
        m.classList.toggle('nbrw-crowd', ty - last < crowd); if (ty - last >= crowd) last = ty;
        var d = Math.abs(ty - ry); if (d < bd) { bd = d; best = e; }
      } else imp(m, 'display', 'none');
      e.ty = on ? ty : null;
    });
    here = best && bd <= 12 * ks ? best : null;
    var mk0 = marker.offsetWidth || 14;
    if (ry >= 0 && ry <= th) {
      imp(marker, 'display', ''); marker.style.top = Math.round(ry - mk0 / 2) + 'px'; marker.style.left = Math.round(-2 - mk0 / 2) + 'px';
      marker.setAttribute('data-kind', here ? here.kind : 'here'); marker.setAttribute('data-st', here ? stE(here) : 'open');
    } else imp(marker, 'display', 'none');
    gripAt();
  }
  function gripAt() {         // the grip on the panel's left edge, the line from the column's left to the panel, both on the reading height
    var on = view === 'doc' && pan.style.getPropertyValue('display') !== 'none';
    imp(rlm, 'display', on ? 'flex' : 'none'); if (!on) { imp(rline, 'display', 'none'); return; }
    var W0 = wrap.getBoundingClientRect(), wr = win.getBoundingClientRect(), pr = pan.getBoundingClientRect(), g = rlm.offsetWidth || 28;
    var y = Math.round(wr.top - W0.top + rlNow());
    rlm.style.top = Math.round(y - g / 2) + 'px'; rlm.style.left = Math.round(pr.left - W0.left - g / 2) + 'px';
    var show = rlDrag || rlm.matches(':hover');
    imp(rline, 'display', show ? 'block' : 'none'); rline.classList.toggle('is-on', !!show);
    if (show) { rline.style.top = y + 'px'; rline.style.left = Math.round(wr.left - W0.left + (parseFloat(win.style.paddingLeft) || 0)) + 'px';
      rline.style.width = Math.max(0, Math.round(pr.left - wr.left - (parseFloat(win.style.paddingLeft) || 0))) + 'px'; }
    if (rlDrag) rline.setAttribute('data-drag', '1'); else rline.removeAttribute('data-drag');
  }
  // M1: the trail while the document runs (Lab E25 q), the direction for its side
  var movT = 0, lastTop = 0;
  function moving() {
    var t = win.scrollTop; if (Math.abs(t - lastTop) < 1) return;
    marker.setAttribute('data-dir', t > lastTop ? 'down' : 'up'); lastTop = t;
    marker.classList.add('is-moving'); W.clearTimeout(movT);
    movT = W.setTimeout(function () { marker.classList.remove('is-moving'); }, 160);
  }
  // ---- the reading height (Lab E9.1: marker, line and the chosen heading are one height) ----
  var rl = NaN;
  function rlMax() { return Math.max(40, Math.round(win.clientHeight * 0.7)); }
  function rlNow() { var v = rl > 0 ? rl : Math.round(win.clientHeight * 0.25); return Math.max(24, Math.min(rlMax(), v)); }
  // E31 P1/L1 — THE GRIP like Lab's (.nbgrip, 14-rail-grip-zoom E9.1): the first 4 px decide the axis —
  // sideways is the panel's width (the edge follows the pointer), up and down the reading height (the chosen
  // heading goes with the line); no move = a click: the panel opens or folds
  var rlDrag = null;
  rlm.addEventListener('pointerdown', function (e) {
    if (e.button) return;
    rlDrag = { x: e.clientX, y: e.clientY, r: rlNow(), w: pan.offsetWidth || 0, ax: null };
    try { rlm.setPointerCapture(e.pointerId); } catch (x) {}
    rlm.setAttribute('data-drag', '1'); rlm.classList.add('is-drag'); wrap.setAttribute('data-drag', '1');
    e.preventDefault(); e.stopPropagation(); tipOff(); gripAt();
  });
  rlm.addEventListener('pointermove', function (e) {
    if (!rlDrag) { gripAt(); return; }
    var dx = e.clientX - rlDrag.x, dy = e.clientY - rlDrag.y;
    if (!rlDrag.ax) { if (Math.max(Math.abs(dx), Math.abs(dy)) < 4) return; rlDrag.ax = Math.abs(dx) > Math.abs(dy) ? 'x' : 'y'; }
    if (rlDrag.ax === 'y') {
      rl = Math.max(24, Math.min(rlMax(), Math.round(rlDrag.r + dy)));
      if (pin) pinFix();           // the chosen heading goes with the line (Lab E11.4)
      sync();
    } else keep(function () { setPw(rlDrag.w - dx); });
  });
  function rlUp(e) {
    if (!rlDrag) return;
    var d = rlDrag; rlDrag = null; rlm.removeAttribute('data-drag'); rlm.classList.remove('is-drag'); wrap.removeAttribute('data-drag');
    if (d.ax === 'x' && !popen && d.w > pwLim().pc + 1) pwOpen = d.w;      // shut by dragging: it opens again at the width it had
    if (!d.ax) { if (e && e.type === 'pointerup') act('panel'); }
    else if (d.ax === 'y') save('rl', rl);
    else save('pw', pwOpen);
    gripAt();
  }
  rlm.addEventListener('pointerup', rlUp); rlm.addEventListener('pointercancel', rlUp);
  rlm.addEventListener('mouseenter', gripAt); rlm.addEventListener('mouseleave', function () { W.setTimeout(gripAt, 0); });
  rlm.addEventListener('keydown', function (e) {        // the grip by keys: ↑/↓ the reading height, ←/→ the width, Enter folds
    var k = e.key, st = e.shiftKey ? 40 : 10;
    if (k === 'ArrowUp' || k === 'ArrowDown') { rl = Math.max(24, Math.min(rlMax(), rlNow() + (k === 'ArrowDown' ? st : -st))); save('rl', rl); if (pin) pinFix(); sync(); }
    else if (k === 'ArrowLeft' || k === 'ArrowRight') { keep(function () { setPw((pan.offsetWidth || 0) + (k === 'ArrowLeft' ? st : -st)); }); save('pw', pwOpen); }
    else if (k === 'Enter' || k === ' ') act('panel');
    else return;
    e.preventDefault(); e.stopPropagation();
  });
  // ---- a click on a mark ----------------------------------------------------
  function maxTop() { return Math.max(0, win.scrollHeight - win.clientHeight); }
  var pinSet = -1, layT = 0;
  function now() { return W.performance ? W.performance.now() : Date.now(); }
  function pinFix() {        // the pinned heading back on the line (after a change of size)
    if (!pin || view !== 'doc') return;
    var y = midY(pin.e); if (y == null) return;
    var to = Math.max(0, Math.min(maxTop(), Math.round(y - rlNow())));
    if (Math.abs(to - win.scrollTop) >= 1) win.scrollTop = to;
    pinSet = win.scrollTop;
  }
  // like Lab (E23.15 Nach-Runde): a scroll that is neither ours nor follows a change of size, and leaves the
  // pinned heading off the line, is someone else's (a script, a find) — the anchor lets go
  function pinScroll() {
    if (!pin || Math.abs(win.scrollTop - pinSet) < 1 || now() - layT < 150) { if (pin) pinSet = win.scrollTop; return; }
    var y = midY(pin.e);
    if (y == null || Math.abs(y - win.scrollTop - rlNow()) > 2) free(); else pinSet = win.scrollTop;
  }
  function free() { pin = null; }            // the reader scrolls himself: the anchor lets go
  function selMark() { marks.forEach(function (m) { m.classList.toggle('is-sel', !!sel && m === sel.mark); }); }
  function go(e) {           // open the way to it, its heading on the reading height, hold it there
    if (view !== 'doc') setView('doc');
    reveal(e.det || e.el);
    if (e.det && !e.det.open) e.det.open = true;
    pin = { e: e }; pinFix();
    [60, 200, 500].forEach(function (t) { W.setTimeout(function () { if (pin && pin.e === e) pinFix(); }, t); });
    sync();
  }
  function hit(e, ev, m) {
    tipOff();
    if (lockedE(e)) { hint(e, m); return; }                          // E29 D3: no jump, the reason
    if (sel === e && e.det && e.det.open && !(ev && ev.detail > 1)) {
      e.det.open = false; sel = null; selMark();                    // the chosen, open mark folds; it stays on the line
      pin = { e: e }; pinFix(); later(); return;
    }
    sel = e; selMark(); go(e);
  }
  function jump(i) { var c = chaps[i]; if (!c) return; if (c.e) { sel = c.e; selMark(); go(c.e); } else { if (view !== 'doc') setView('doc'); reveal(c.el); free(); win.scrollTop = Math.round(topOf(c.el)); sync(); } }
  // ---- hover box and lock box: beside the panel, at the mark's height --------
  function boxAt(m) {
    imp(tip, 'display', 'flex');
    var wr = wrap.getBoundingClientRect(), mr = m.getBoundingClientRect(), pl = pan.getBoundingClientRect().left - wr.left;
    var bw = tip.offsetWidth || 220, bh = tip.offsetHeight || 50;
    tip.style.left = Math.max(4, Math.round(pl - bw - 8 - (rlm.offsetWidth || 0) / 2)) + 'px';
    tip.style.top = Math.max(4, Math.min(wrap.clientHeight - bh - 4, Math.round(mr.top + mr.height / 2 - wr.top - bh / 2))) + 'px';
  }
  var tipT = 0;
  function tipOn(e, m) {
    if (tip.getAttribute('data-kind') === 'lock' && tip.style.display !== 'none') return;
    var st = stE(e), say;
    if (st === 'locked') say = gateMsg(e) || T.lock;
    else if (e.kind === 'chap') {
      var ts = tasksOf(e.ch), sv = ts.filter(function (t) { return stOf(t) === 'solved'; }).length;
      say = L.k.chap + ' ' + (e.ch + 1) + (ts.length ? ' \u00B7 ' + sv + ' / ' + ts.length + ' ' + L.tasks + ' ' + L.st.solved : '') + '\n' + L.tip;
    } else if (e.t) say = L.k[e.kind] + ' \u00B7 ' + (L.st[st] || st) + '\n' + L.tip;
    else if (e.kind === 'yoc') say = L.yocT;
    else if (e.kind === 'title' || e.kind === 'end') say = (e.kind === 'end' ? '' : L.k.title + '\n') + L.tipGo;
    else say = L.k[e.kind] + '\n' + (e.det ? L.tip : L.tipGo);
    var tt = e.tn && st !== 'locked' ? tplTitle(e.tn) : '';             // Lab's own words for it, when they add something
    if (tt && tt.replace(/^\d+\s*\u00B7\s*/, '') !== e.name && e.name.indexOf(tt.replace(/^\d+\s*\u00B7\s*/, '')) < 0) say = tt + '\n' + say;
    tipH.textContent = (st === 'locked' ? '\uD83D\uDD12 ' : '') + e.name; tipS.textContent = say;
    tip.setAttribute('data-kind', 'tip'); tip.setAttribute('data-e', String(ents.indexOf(e)));
    boxAt(m);
  }
  function tipOff() { if (tip.getAttribute('data-kind') !== 'lock') imp(tip, 'display', 'none'); }
  function gateMsg(e) { for (var i = 0; i < gates.length; i++) if (gates[i].lock && gates[i].ch === e.ci) return gates[i].msg.textContent.replace(/^\uD83D\uDD12\s*/, ''); return ''; }
  function hint(e, m) {
    tipH.textContent = L.locked; tipS.textContent = gateMsg(e) || T.lock;
    tip.setAttribute('data-kind', 'lock'); tip.setAttribute('data-e', String(ents.indexOf(e)));
    boxAt(m);
    W.clearTimeout(tipT);
    tipT = W.setTimeout(function () { tip.removeAttribute('data-kind'); imp(tip, 'display', 'none'); }, 4000);
  }
  D.addEventListener('pointerdown', function (ev) {
    if (tip.getAttribute('data-kind') !== 'lock' || (ev.target && ev.target.closest && ev.target.closest('.nbrw-mark'))) return;
    tip.removeAttribute('data-kind'); imp(tip, 'display', 'none');
  }, true);
  var curI = -2;
  function sync() {
    var sh = win.scrollHeight, ch = win.clientHeight, tk = sb.clientHeight, tp = win.scrollTop;     // E31 S1: the bar on the left
    var tl = Math.max(24, Math.round(tk * Math.min(1, ch / Math.max(1, sh))));
    var y = sh > ch ? Math.round((tk - tl) * tp / (sh - ch)) : 0;
    thumb.style.height = tl + 'px'; thumb.style.top = y + 'px';
    if (view !== 'doc') return;
    pos();
    var k = -1, line = tp + rlNow() + 2;
    for (var i = 0; i < chaps.length; i++) {
      var my = chaps[i].e ? midY(chaps[i].e) : null;
      if ((my != null ? my : topOf(chaps[i].el)) <= line) k = i;
    }
    if (k !== curI) {
      curI = k;
      cur.textContent = k >= 0 ? chaps[k].title : L.top;
      marks.forEach(function (m) { if (m.getAttribute('data-kind') !== 'chap') return; var j = +m.getAttribute('data-ch'); m.classList.toggle('is-active', j === k); m.setAttribute('aria-current', j === k ? 'true' : 'false'); });
      wrap.setAttribute('data-nbrw-ch', String(k));
    }
  }
  function keep(fn) {      // keep the pinned heading on the line, else the chapter in view at its place, while the layout changes
    var a = !pin && view === 'doc' && curI >= 0 ? chaps[curI] : null, off = a ? win.scrollTop - topOf(a.el) : 0, r = win.scrollTop / Math.max(1, win.scrollHeight);
    fn();
    if (pin) pinFix(); else win.scrollTop = a ? Math.round(topOf(a.el) + off) : r * win.scrollHeight;
    drawMarks();
  }

  // ---- E26.3 · 2: the axis = the window's middle ---------------------------
  // the panel lies over the window's right side (never past the middle); the
  // window keeps its width free on both sides, so the column stays centred
  // E30 B5 (PyCharm dark: the column shifted, the panel cut at the right) —
  // the window is never wider than the part of its page one can see: a host
  // page that makes the output wider than its frame (a margin, a scroll bar, a
  // wide neighbour) would cut the panel and move the axis. The width is taken
  // from what is visible; the axis is the middle of that.
  function fit() {
    imp(wrap, 'max-width', ''); imp(wrap, 'margin-left', ''); imp(wrap, 'margin-right', '');
    var vw = D.documentElement.clientWidth || W.innerWidth || 0, pe = wrap.parentElement;
    if (!pe || vw < 200) return;
    if (W.scrollX || W.pageXOffset) W.scrollTo(0, W.scrollY || W.pageYOffset || 0);
    var p = pe.getBoundingClientRect(), vl = Math.max(p.left, 0), vr = Math.min(p.right, vw);
    if (p.right > vw + 0.5 || p.left < -0.5) {           // the parent reaches past the frame: the visible part, the left gap mirrored
      var g = p.left >= 0 ? Math.min(p.left, 16) : 0;
      imp(wrap, 'max-width', Math.max(280, Math.floor(vr - vl - g)) + 'px');
      imp(wrap, 'margin-left', Math.round(vl - p.left) + 'px'); imp(wrap, 'margin-right', 'auto');
    }
  }
  // E31 P1/Z1/T2: the panel's width is the reader's (the grip), from the closed rail to the window's middle;
  // the free margins are EQUAL on both sides — the tool column's room on the left, the panel's on the right,
  // the larger of the two, the panel's part at most a quarter of the window: a wider panel lies over the
  // document on its own surface (as Lab's), the column keeps the window's middle
  function pwLim() {
    var ww = wrap.clientWidth || 0, pc = Math.round(PWC * Z[zi]);           // E33 B5: shut, as wide as the lens draws its marks (Lab)
    return { pc: pc, min: pc + 60, max: Math.max(pc + 60, Math.floor(ww / 2) - 14) };
  }
  function setPw(w) {
    var l = pwLim();
    if (w < l.pc + 30) { popen = false; }
    else { popen = true; pwOpen = Math.max(l.min, Math.min(l.max, Math.round(w))); }
    save('panel', popen ? 'open' : 'closed'); place(); label();
  }
  function place() {
    fit();
    var ww = wrap.clientWidth || 0, M = Math.round(8 * gs), l = pwLim();
    var po = Math.max(l.min, Math.min(l.max, pwOpen || PW));
    var pw = view === 'doc' ? (popen ? po : l.pc) : 0;
    // E33 B5 — the panel's factor like Lab's: 1 up to the standard width, then × width / standard (capped), × the lens
    ks = Z[zi] * (popen ? Math.min(KCAP, Math.max(1, po / PW)) : 1);
    var tw = sizeCtl(), pad = Math.round(8 * ks);
    var side = view === 'doc' ? Math.max(tw + 2 * M, l.pc + 8, Math.min(pw + 8, Math.round(ww * 0.25))) : 0;
    wrap.setAttribute('data-nbrw-panel', popen ? 'open' : 'closed');
    wrap.setAttribute('data-nbrw-over', pw + 8 > side ? '1' : '0');
    wrap.style.setProperty('--rw-pw', Math.round((pw || PW) / ks) + 'px');
    wrap.style.setProperty('--nbrw-pw', pw + 'px');
    wrap.style.setProperty('--nbrw-side', side + 'px');
    imp(pan, 'width', pw + 'px');
    imp(pan, 'display', pw ? '' : 'none');
    imp(pan, 'padding', pad + 'px ' + pad + 'px ' + Math.round(10 * ks) + 'px');
    imp(pan, 'gap', pad + 'px');
    // E33 B4: the timeline in the MIDDLE of the panel (Lab's rail), open or shut; the names to the right of it
    imp(track, 'margin-left', Math.max(4, Math.round((pw - 2 * pad) / 2 - 2)) + 'px');
    imp(tools, 'width', tw + 'px'); imp(tools, 'left', M + 'px'); imp(tools, 'top', M + 'px'); imp(tools, 'bottom', M + 'px');
    imp(tools, 'display', view === 'doc' ? 'flex' : 'none');
    imp(win, 'margin-right', '0px'); imp(win, 'margin-left', '0px'); imp(win, 'width', 'auto');
    imp(win, 'padding-left', side + 'px'); imp(win, 'padding-right', side + 'px');
    if (view !== 'doc') { imp(rlm, 'display', 'none'); imp(rline, 'display', 'none'); drawer(''); }
    padDoc();
  }

  // ---- E33 B6/B3 (2026-10-13, Werkstatt JS) — THE DRAWERS OF ⌨ ⚙ 👤 ✉ -----------
  // Lab's column ends in ⌨ ⚙ 👤; the window had none of them. Each opens ONE drawer beside the tool column (over
  // the document, never past the window): ⌨ the keys that work here, ⚙ mode and language (what Lab's ⚙ offers
  // without a kernel), 👤 the account, ✉ feedback (E29 P5: one line of text, the address from the notebook — no
  // form, no mailto:). The drawer is a tool: its size × gs. A click outside or Esc closes it.
  var drwKind = '';
  function dbtn(t, cls, fn) { var b = mk('button', 'nbrw-dbtn' + (cls ? ' ' + cls : ''), t); b.type = 'button'; b.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); fn(b); }); return b; }
  function fbText() {
    var tp = root.querySelector('template.nbrw-rail'), to = tp && tp.content ? tp.content.querySelector('.nbfb-to') : null;
    var a = to ? to.textContent.trim() : '';
    return a ? (de ? 'Feedback, Fehler und Kontakt: per E-Mail an ' : 'Feedback, errors and contact: by e-mail to ') + a : X('fb0');
  }
  function drawer(k) {
    drwKind = k || '';
    drw.setAttribute('data-kind', drwKind);
    ['kbd', 'gear', 'mode', 'acct', 'fb'].forEach(function (a) { B[a].setAttribute('aria-expanded', String(a === drwKind)); B[a].classList.toggle('is-on', a === drwKind); });
    drw.innerHTML = '';
    if (!drwKind) { imp(drw, 'display', 'none'); return; }
    var hd = drw.appendChild(mk('div', 'nbrw-dr-h')); hd.appendChild(mk('b', '', X(drwKind)));
    hd.appendChild(dbtn('×', 'nbrw-dr-x', function () { drawer(''); })).setAttribute('aria-label', X('close'));
    var bd = drw.appendChild(mk('div', 'nbrw-dr-b'));
    if (drwKind === 'kbd') {
      var tb = bd.appendChild(mk('table', 'nbrw-keys'));
      X('kl').forEach(function (r) { var tr = tb.appendChild(mk('tr')); tr.appendChild(mk('td')).appendChild(mk('kbd', '', r[0])); tr.appendChild(mk('td', '', r[1])); });
      bd.appendChild(mk('p', 'nbrw-dr-n', X('kn')));
    } else if (drwKind === 'mode') {
      var ms = bd.appendChild(mk('div', 'nbrw-dr-row')); ms.setAttribute('role', 'radiogroup');
      MODES.forEach(function (m) {
        var o = ms.appendChild(dbtn(L.modes[m][0] + ' ' + L.modes[m][1], 'nbrw-dr-mode', function () { setMode(m, true); drawer('mode'); }));
        o.setAttribute('data-mode', m); o.setAttribute('role', 'radio'); o.setAttribute('aria-checked', String(m === mode)); o.title = L.modes[m][2];
      });
      bd.appendChild(mk('p', 'nbrw-dr-n', L.modes[mode][2]));
    } else if (drwKind === 'gear') {
      if (BI) {
        bd.appendChild(mk('div', 'nbrw-dr-t', X('lang')));
        var lr = bd.appendChild(mk('div', 'nbrw-dr-row'));
        ['en', 'de'].forEach(function (x) { lr.appendChild(dbtn(x.toUpperCase(), 'nbrw-dr-lang', function () { applyLang(x, true); drawer('gear'); })).setAttribute('aria-pressed', String(x === lg)); });
      }
      bd.appendChild(mk('div', 'nbrw-dr-t', X('fb'))); bd.appendChild(mk('p', 'nbrw-fb', fbText()));
    } else if (drwKind === 'fb') {
      bd.appendChild(mk('p', 'nbrw-fb', fbText())); bd.appendChild(mk('p', 'nbrw-dr-n', X('fbS') + ' · v' + V));
    } else acForm(bd);
    imp(drw, 'display', 'block');
    var W0 = wrap.getBoundingClientRect(), tr0 = tools.getBoundingClientRect(), br = B[drwKind].getBoundingClientRect();
    imp(drw, 'font-size', Math.round(12 * gs * 10) / 10 + 'px'); imp(drw, 'width', Math.round(300 * gs) + 'px');
    imp(drw, 'max-height', Math.max(120, wrap.clientHeight - 16) + 'px'); imp(drw, 'overflow', 'auto');
    imp(drw, 'left', Math.round(tr0.right - W0.left + 8) + 'px');
    imp(drw, 'top', Math.round(Math.max(8, Math.min(wrap.clientHeight - drw.offsetHeight - 8, br.top - W0.top))) + 'px');
    var f = drw.querySelector('input'); if (f) try { f.focus({ preventScroll: true }); } catch (e) {}
  }
  D.addEventListener('pointerdown', function (e) {
    if (!drwKind || !e.target || !e.target.closest) return;
    if (e.target.closest('.nbrw-drawer') === drw || e.target.closest('.nbrw-tool')) return;
    drawer('');
  }, true);
  drw.addEventListener('keydown', function (e) { if (e.key === 'Escape') { var k = drwKind; e.preventDefault(); drawer(''); try { B[k || 'gear'].focus(); } catch (x) {} } e.stopPropagation(); });
  drw.addEventListener('wheel', function (e) { e.stopPropagation(); if (drw.scrollHeight <= drw.clientHeight) e.preventDefault(); }, { passive: false });
  imp(drw, 'overscroll-behavior', 'contain');

  // ---- E33 B3 — THE ACCOUNT IN THE WINDOW, as Lab's (12-rail-series-role) ---------------------------------------
  // One record per browser (digichemjn.account.v1: person id, favourites, the password's check — never the
  // password), ON per notebook (digichemjn.acct.on.<id>, E25 o): the same keys as Lab, so where Lab and the window
  // share a browser they share the account. New account: a name (free, kept in this browser only) + the password
  // twice. Log in: name + password (an account of this browser), or the account code DCJ1.… + password (from
  // another device: Lab's sealed code — PBKDF2-SHA-256 300 000, AES-GCM, deflate). Logged in: the favourites
  // (style, light/dark, language, mode) hold for this notebook; „Show my code“ seals settings + this window's
  // progress; log out. No server: the code is the only bridge (the drawer says so).
  var ACK = 'digichemjn.account.v1', ACON = 'digichemjn.acct.on.' + (ID || 'nb'), B32 = '0123456789ABCDEFGHJKMNPQRSTVWXYZ', AC_IT = 300000;
  var ACM = { typo: ['This code has a typo: a character is missing or changed.', 'Dieser Code hat einen Tippfehler: ein Zeichen fehlt oder ist anders.'],
    password: ['This password does not open this code.', 'Dieses Passwort öffnet diesen Code nicht.'],
    form: ['This code is from a newer version of the notebooks.', 'Dieser Code stammt aus einer neueren Version der Notebooks.'],
    insecure: ['Accounts need a secure page (https or localhost); this page is not one.', 'Konten brauchen eine sichere Seite (https oder localhost); diese ist keine.'],
    'short': ['The password needs at least 8 characters.', 'Das Passwort braucht mindestens 8 Zeichen.'],
    nomatch: ['The two passwords are not the same.', 'Die beiden Passwörter sind nicht gleich.'],
    wrongpw: ['That is not the password of this account.', 'Das ist nicht das Passwort dieses Kontos.'] };
  function acSay(k) { var m = ACM[k]; return m ? m[de ? 1 : 0] : String(k); }
  function lsGet(k) { try { return W.localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { if (v == null) W.localStorage.removeItem(k); else W.localStorage.setItem(k, v); } catch (e) {} }
  function acGet() { var a = null; try { a = JSON.parse(lsGet(ACK) || 'null'); } catch (e) {} if (!a || !a.id) return null; a.on = lsGet(ACON) === '1'; return a; }
  function acSave(a) { var r = {}; for (var x in a) if (x !== 'on') r[x] = a[x]; lsSet(ACK, JSON.stringify(r)); lsSet(ACON, a.on ? '1' : null); }
  function acReady() { return !!(W.crypto && W.crypto.subtle && W.isSecureContext !== false && W.TextEncoder); }
  function acRnd(n) { var a = new W.Uint8Array(n); W.crypto.getRandomValues(a); return a; }
  function acNewId() { var b = acRnd(12), s = ''; for (var i = 0; i < 12; i++) s += B32[b[i] & 31] + (i === 3 || i === 7 ? '-' : ''); return 'DCJ-' + s; }
  function u8(s) { return new W.TextEncoder().encode(s); }
  function b64(u) { var s = ''; for (var i = 0; i < u.length; i++) s += String.fromCharCode(u[i]); return W.btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); }
  function unb64(s) { s = s.replace(/-/g, '+').replace(/_/g, '/'); var r = W.atob(s + '==='.slice((s.length + 3) % 4)), u = new W.Uint8Array(r.length); for (var i = 0; i < r.length; i++) u[i] = r.charCodeAt(i); return u; }
  function acCheck(s) { var x = 0x811c9dc5; for (var i = 0; i < s.length; i++) { x ^= s.charCodeAt(i); x = Math.imul(x, 0x01000193) >>> 0; } return B32[(x >>> 5) & 31] + B32[x & 31]; }
  function acZip(u, back) {
    if (!W.CompressionStream) return W.Promise.reject(new Error('nozip'));
    var S = back ? new W.DecompressionStream('deflate-raw') : new W.CompressionStream('deflate-raw');
    return new W.Response(new W.Blob([u]).stream().pipeThrough(S)).arrayBuffer().then(function (b) { return new W.Uint8Array(b); });
  }
  function acKey(pw, salt, bits) {
    var C = W.crypto.subtle;
    return C.importKey('raw', u8(pw), 'PBKDF2', false, ['deriveKey', 'deriveBits']).then(function (k) {
      var p = { name: 'PBKDF2', salt: salt, iterations: AC_IT, hash: 'SHA-256' };
      return bits ? C.deriveBits(p, k, 256) : C.deriveKey(p, k, { name: 'AES-GCM', length: 256 }, false, ['encrypt', 'decrypt']);
    });
  }
  function acVer(pw, vs) { return acKey(pw, vs, true).then(function (b) { return W.crypto.subtle.digest('SHA-256', b); }).then(function (x) { return b64(new W.Uint8Array(x)); }); }
  var FAV = { skin: { digi: 'd', minimal: 'm', cyber: 'c', retro: 'r', fairy: 'f', anime: 'a' }, theme: { auto: 'a', light: 'l', dark: 'd' }, lang: { en: 'e', de: 'd' },
              role: { reader: 'r' }, mode: { both: 'b', calc: 'c', code: 'k', plain: 'p' } }, FAVO = ['skin', 'theme', 'lang', 'role', 'mode'];
  function favNow() { return { skin: SKINS[sk], theme: THEMES[th] || 'auto', lang: lg, role: 'reader', mode: mode }; }
  function favPack(f) { return FAVO.map(function (k) { return FAV[k][f[k]] || '-'; }).join(''); }
  function favUnpack(s) { var f = {}; FAVO.forEach(function (k, i) { f[k] = ''; for (var w in FAV[k]) if (FAV[k][w] === s.charAt(i)) f[k] = w; }); return f; }
  function favApply(f) {           // the account's favourites, for this notebook (the window's own keys)
    if (!f) return;
    if (f.skin && SKINS.indexOf(f.skin) >= 0) { sk = SKINS.indexOf(f.skin); save('skin', f.skin); }
    if (f.theme) { th = Math.max(0, THEMES.indexOf(f.theme === 'auto' ? '' : f.theme)); save('theme', THEMES[th]); }
    paint(); label();
    if (f.mode && MODES.indexOf(f.mode) >= 0) setMode(f.mode, true);
    if (BI && (f.lang === 'en' || f.lang === 'de')) applyLang(f.lang, true);
  }
  var ST2C = { solved: 'd', wrong: 'f', skipped: 's' }, C2ST = { d: 'solved', f: 'wrong', s: 'skipped' };
  function progStr() {            // this window's progress in Lab's words: o f s d per exercise, written | coding | difficulty
    var a = '', c = '', d = '';
    tasks.forEach(function (t) { if (!t.key) return; var x = ST2C[stOf(t)] || 'o'; if (t.kind === 'code') c += x; else { a += x; d += '-'; } });
    return a + '|' + c + '|' + d;
  }
  function progTake(p) {          // the further state wins (Lab's acMerge), per exercise
    var R = { o: 0, f: 1, s: 2, d: 3 }, q = String(p || '').split('|'), ia = 0, ic = 0;
    tasks.forEach(function (t) {
      if (!t.key) return;
      var x = t.kind === 'code' ? (q[1] || '').charAt(ic++) : (q[0] || '').charAt(ia++), now0 = ST2C[stOf(t)] || 'o';
      if (x && R[x] > R[now0]) save((t.kind === 'code' ? 'code.' : 'task.') + t.key, C2ST[x]);
    });
    gate();
  }
  function acSeal(a, pw) {
    var text = ['1', a.id.replace(/^DCJ-|-/g, ''), favPack(a.fav || {}), (ID || 'nb') + '=' + progStr()].join('~');
    var salt = acRnd(16), iv = acRnd(12), plain = u8(text), flag = 0x11;
    return acZip(plain).catch(function () { flag = 0x10; return plain; }).then(function (z) {
      return acKey(pw, salt).then(function (k) { return W.crypto.subtle.encrypt({ name: 'AES-GCM', iv: iv }, k, z); }).then(function (ct) {
        ct = new W.Uint8Array(ct); var all = new W.Uint8Array(29 + ct.length);
        all[0] = flag; all.set(salt, 1); all.set(iv, 17); all.set(ct, 29);
        var head = 'DCJ1.' + b64(all); return head + '.' + acCheck(head);
      });
    });
  }
  function acOpen(code, pw) {
    var c = String(code || '').replace(/\s+/g, ''), m = /^(DCJ1\.[A-Za-z0-9_-]+)\.([0-9A-Z]{2})$/.exec(c), all;
    if (!m || acCheck(m[1]) !== m[2]) return W.Promise.reject(new Error('typo'));
    try { all = unb64(m[1].slice(5)); } catch (e) { return W.Promise.reject(new Error('typo')); }
    if (all.length < 45 || (all[0] !== 0x11 && all[0] !== 0x10)) return W.Promise.reject(new Error('typo'));
    return acKey(pw, all.slice(1, 17)).then(function (k) { return W.crypto.subtle.decrypt({ name: 'AES-GCM', iv: all.slice(17, 29) }, k, all.slice(29)); })
      .then(function (z) { z = new W.Uint8Array(z); return all[0] === 0x11 ? acZip(z, true) : z; }, function () { throw new Error('password'); })
      .then(function (u) {
        var p = new W.TextDecoder().decode(u).split('~');
        if (p[0] !== '1' || !/^[0-9A-Z]{12}$/.test(p[1] || '')) throw new Error('form');
        var map = {}; p.slice(3).forEach(function (e) { var q = e.indexOf('='); if (q > 0) map[e.slice(0, q)] = e.slice(q + 1); });
        return { id: 'DCJ-' + p[1].slice(0, 4) + '-' + p[1].slice(4, 8) + '-' + p[1].slice(8), fav: favUnpack(p[2] || ''), map: map };
      });
  }
  var acUi = { step: '', msg: '', kind: 'info', code: '' };
  function acSet(o) { acUi.clear = o.kind === 'ok'; for (var k in o) acUi[k] = o[k]; acAll(); acUi.clear = false; }
  function acAll() {
    if (drwKind === 'acct') { var b = drw.querySelector('.nbrw-dr-b'); if (b) acForm(b); }
    [].forEach.call(cover.querySelectorAll('.nbrw-acct-f'), acForm);
    acLine();
  }
  function acLine() {            // the cover's „Account ▸“ line says who is in
    var a = acGet(), s = cover.querySelector('details.nbrw-acct > summary');
    wrap.setAttribute('data-nbrw-acct', a && a.on ? 'in' : 'out');
    if (s) s.setAttribute('data-in', a && a.on ? '1' : '0');
    B.acct.title = X('acct') + (a && a.on ? ' · ' + (a.name || a.id) : '');
  }
  function acForm(box) {
    var a = acGet(), st = a && a.on ? 'in' : (acUi.step === 'new' ? 'new' : 'out'), kept = {};
    if (box.__st === st) [].forEach.call(box.querySelectorAll('input'), function (i) { if (i.value) kept[i.className] = i.value; });
    if (acUi.clear) { kept = {}; }
    box.__st = st; box.innerHTML = '';
    var f = box.appendChild(mk('form', 'nbrw-acct-form')); f.setAttribute('data-step', st);
    f.addEventListener('submit', function (e) { e.preventDefault(); });
    f.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter' || !e.target || e.target.tagName !== 'INPUT') return;
      e.preventDefault(); var b = f.querySelector('.is-primary'); if (b) b.click();
    });
    function inp(cls, ph, type, ac) { var i = mk('input', 'nbrw-acct-in ' + cls); i.type = type || 'text'; i.placeholder = ph; i.setAttribute('aria-label', ph); if (ac) i.setAttribute('autocomplete', ac); i.spellcheck = false; f.appendChild(i); return i; }
    function go(t, d, fn, cls) { var b = dbtn(t, 'nbrw-acct-btn' + (cls ? ' ' + cls : ''), fn); b.setAttribute('data-do', d); f.appendChild(b); return b; }
    function val(c) { var i = f.querySelector('.' + c); return i ? i.value : ''; }
    if (st === 'in') {
      f.appendChild(mk('div', 'nbrw-acct-me', X('inB') + ': ' + (a.name || a.id))).title = a.id;
      inp('nbrw-acct-pw', X('pw'), 'password', 'current-password');
      go(X('bCode'), 'code', function () { acCode(val('nbrw-acct-pw')); }, 'is-primary');
      go(X('bOut'), 'out', function () { a.on = false; acSave(a); acSet({ msg: X('outOk'), kind: 'ok', code: '' }); });
      if (acUi.code) {
        var cb = f.appendChild(mk('div', 'nbrw-acct-code')); cb.appendChild(mk('div', '', X('codeT')));
        var ct = cb.appendChild(mk('code', '', acUi.code)); imp(ct, 'word-break', 'break-all'); imp(ct, 'white-space', 'normal'); imp(ct, 'display', 'block');
        cb.appendChild(dbtn(X('bCopy'), 'nbrw-acct-btn', function () { copyTxt(acUi.code, ct, function (ok) { acSet({ msg: ok ? X('copied') : T.nocopy, kind: ok ? 'ok' : 'info' }); }); }));
      }
    } else if (st === 'new') {
      inp('nbrw-acct-name', X('name'), 'text', 'username');
      inp('nbrw-acct-pw1', X('pw8'), 'password', 'new-password'); inp('nbrw-acct-pw2', X('pw2'), 'password', 'new-password');
      go(X('bMk'), 'mk', function () { acNew(val('nbrw-acct-name'), val('nbrw-acct-pw1'), val('nbrw-acct-pw2')); }, 'is-primary');
      go(X('bNo'), 'no', function () { acSet({ step: '', msg: '' }); });
    } else {
      f.appendChild(mk('div', 'nbrw-acct-me', X('out')));
      inp('nbrw-acct-name', X('name'), 'text', 'username'); inp('nbrw-acct-pw', X('pw'), 'password', 'current-password');
      inp('nbrw-acct-code', X('code'), 'text', 'off');
      go(X('bIn'), 'in', function () { acIn(val('nbrw-acct-name'), val('nbrw-acct-pw'), val('nbrw-acct-code')); }, 'is-primary');
      go(X('bNew'), 'new', function () { acSet({ step: 'new', msg: '' }); });
    }
    var m = f.appendChild(mk('div', 'nbrw-acct-msg', acUi.msg || '')); m.setAttribute('role', 'status'); m.setAttribute('data-kind', acUi.kind || 'info');
    f.appendChild(mk('div', 'nbrw-acct-note', X('note')));
    [].forEach.call(f.querySelectorAll('input'), function (i) { if (kept[i.className]) i.value = kept[i.className]; });
  }
  function busy() { acSet({ msg: X('busy'), kind: 'info' }); }
  function acNew(name, p1, p2) {
    if (!acReady()) return acSet({ msg: acSay('insecure'), kind: 'err' });
    if (String(p1 || '').length < 8) return acSet({ msg: acSay('short'), kind: 'err' });
    if (p1 !== p2) return acSet({ msg: acSay('nomatch'), kind: 'err' });
    busy();
    var vs = acRnd(16);
    acVer(p1, vs).then(function (vh) {
      var a = { v: 1, id: acNewId(), name: String(name || '').trim().slice(0, 40), on: true, fav: favNow(), vs: b64(vs), vh: vh };
      acSave(a); save('fav', a.id); acSet({ step: '', msg: X('made'), kind: 'ok', code: '' });
    }, function () { acSet({ msg: acSay('insecure'), kind: 'err' }); });
  }
  function acIn(name, pw, code) {
    if (!acReady()) return acSet({ msg: acSay('insecure'), kind: 'err' });
    busy();
    if (String(code || '').trim()) {
      acOpen(code, pw).then(function (d) {
        var vs = acRnd(16);
        return acVer(pw, vs).then(function (vh) {
          var a = { v: 1, id: d.id, name: String(name || '').trim().slice(0, 40) || (acGet() || {}).name || '', on: true, fav: d.fav, vs: b64(vs), vh: vh };
          acSave(a); save('fav', a.id); progTake(d.map[ID] || d.map[ID + '.both']); favApply(d.fav); acSet({ msg: X('inOk'), kind: 'ok', code: '' });
        });
      }).catch(function (e) { acSet({ msg: acSay(e && ACM[e.message] ? e.message : 'typo'), kind: 'err' }); });
      return;
    }
    var a = acGet();
    if (!a) return acSet({ msg: X('none'), kind: 'err' });
    if (a.name && String(name || '').trim() && String(name).trim().toLowerCase() !== a.name.toLowerCase()) return acSet({ msg: X('noName'), kind: 'err' });
    acVer(pw, unb64(a.vs)).then(function (vh) {
      if (vh !== a.vh) return acSet({ msg: acSay('wrongpw'), kind: 'err' });
      a.on = true; acSave(a); save('fav', a.id); favApply(a.fav); acSet({ msg: X('inOk'), kind: 'ok', code: '' });
    }, function () { acSet({ msg: acSay('wrongpw'), kind: 'err' }); });
  }
  function acCode(pw) {
    var a = acGet(); if (!a) return;
    if (!acReady()) return acSet({ msg: acSay('insecure'), kind: 'err' });
    busy();
    acVer(pw, unb64(a.vs)).then(function (vh) {
      if (vh !== a.vh) return acSet({ msg: acSay('wrongpw'), kind: 'err' });
      a.fav = favNow(); acSave(a);
      return acSeal(a, pw).then(function (c) { acSet({ code: c, msg: '', kind: 'ok' }); });
    }).catch(function () { acSet({ msg: acSay('insecure'), kind: 'err' }); });
  }
  function copyTxt(s, el, done) {
    function old() { try { var r = D.createRange(), q = W.getSelection(); r.selectNodeContents(el); q.removeAllRanges(); q.addRange(r); done(D.execCommand('copy')); } catch (e) { done(false); } }
    try { if (W.navigator.clipboard && W.isSecureContext) { W.navigator.clipboard.writeText(s).then(function () { done(true); }, old); return; } } catch (e) {}
    old();
  }
  function acCover() {           // the cover's „Account ▸“: the same form — in Python's box (VERTRAG-E33-py B3), else in place of its line
    var d = cover.querySelector('details.nbrw-acct'); if (!d) return;
    var f = d.querySelector('.nbrw-acct-f') || d.querySelector('.nbacct[data-where]');
    if (f && f.hasAttribute('data-where')) {        // Python's empty box: ours from now on — Lab's script (same page in VS Code) must not fill it
      f.setAttribute('data-nbrw-where', f.getAttribute('data-where')); f.removeAttribute('data-where'); f.classList.add('nbrw-acct-f');
    }
    if (!f) {
      [].forEach.call(d.children, function (c) { if (c.tagName !== 'SUMMARY') imp(c, 'display', 'none'); });      // v1.78's „in JupyterLab“ line
      f = d.appendChild(mk('div', 'nbrw-acct-f'));
    }
    acForm(f); acLine();
  }
  // a logged-in reader: the account's favourites hold for this notebook (once per start, E25 o)
  function acStart() { var a = acGet(); if (a && a.on && a.fav && load('fav', '') !== a.id) { save('fav', a.id); favApply(a.fav); } acLine(); }

  function act(a) {
    if ((a === 'h+' || a === 'h-') && HULL) return;
    if (a === 'h+' || a === 'h-') keep(function () {
      h = Math.min(HMAX, Math.max(HMIN, h + (a === 'h+' ? HSTEP : -HSTEP))); save('h', h);
      wrap.style.setProperty('--nbrw-h', h + 'px');
    });
    else if (a === 'a+' || a === 'a-') keep(function () {
      zi = Math.min(Z.length - 1, Math.max(0, zi + (a === 'a+' ? 1 : -1))); save('z', Z[zi]);
      wrap.style.setProperty('--nbrw-zoom', String(Z[zi]));
      place();                                     // E33 B5: the panel's marks follow the lens
    });
    else if (a === 'f+' || a === 'f-') keep(function () { fsSet(fsLv() + (a === 'f+' ? FS.step : -FS.step)); });
    else if (a === 'g+' || a === 'g-') keep(function () { gsSet(gsLv() + (a === 'g+' ? GS.step : -GS.step)); });
    else if (a === 'theme') { th = (th + 1) % THEMES.length; save('theme', THEMES[th]); paint(); label(); }
    else if (a === 'skin') keep(function () { sk = (sk + 1) % SKINS.length; save('skin', SKINS[sk]); paint(); label(); });
    else if (a === 'panel') keep(function () { popen = !popen; save('panel', popen ? 'open' : 'closed'); place(); label(); });
  }

  // the wheel: the window, not the IDE. E33 B1c (video 2): it stays in the window at its top and bottom too —
  // nothing goes on to the IDE (out of the window: the IDE's scroll bar); an inner box that can still move in that
  // direction (an output, a field) keeps its own. B4: faster with the hand like Lab's D9 — the notches of the last
  // 0.35 s count (one alone ×1, each more +0.45 × (1 + lens − 1), at most ×3.5, ×5 at the lens ceiling); a
  // touchpad (small steps) is never accelerated; and the step follows the lens, as Lab's (more lens, more px)
  var hand = { ts: [], dir: 0 };
  function wheelAcc(e, d) {
    var notch = e.deltaMode !== 0 || (Math.abs(e.deltaY) >= 50 && Math.abs(e.deltaY - Math.round(e.deltaY)) < 0.01);
    if (!notch) { hand.ts = []; return 1; }
    var t = now(), dir = d > 0 ? 1 : -1, z = Z[zi], zc = Z[Z.length - 1];
    if (dir !== hand.dir) { hand.ts = []; hand.dir = dir; }
    hand.ts = hand.ts.filter(function (x) { return t - x < 350; }); hand.ts.push(t);
    var up = Math.max(0, z - 1) / Math.max(0.01, zc - 1), k = 0.45 * (1 + Math.max(0, z - 1)), cap = 3.5 + 1.5 * Math.min(1, up);
    return (hand.a = Math.min(cap, 1 + k * (hand.ts.length - 1)));
  }
  function wheel(e) {
    if (e.ctrlKey || e.metaKey) return;
    var dy = e.deltaY * (e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? win.clientHeight : 1);
    if (!dy || Math.abs(e.deltaX) > Math.abs(e.deltaY)) return;
    for (var x = e.target; x && x !== win && x !== wrap && x.nodeType === 1; x = x.parentElement) {
      if (x.scrollHeight > x.clientHeight + 1) {
        var oy = W.getComputedStyle(x).overflowY;
        if ((oy === 'auto' || oy === 'scroll') && (dy > 0 ? x.scrollTop + x.clientHeight < x.scrollHeight - 1 : x.scrollTop > 0)) return;
      }
    }
    e.preventDefault();
    var max = win.scrollHeight - win.clientHeight;
    dy = dy * wheelAcc(e, dy) * Math.max(1, Z[zi]);
    if ((dy > 0 && win.scrollTop < max - 0.5) || (dy < 0 && win.scrollTop > 0.5)) {
      free(); tipOff();
      win.scrollTop = Math.max(0, Math.min(max, win.scrollTop + dy));
    }
  }
  wrap.addEventListener('wheel', wheel, { passive: false });
  win.addEventListener('scroll', function () { pinScroll(); moving(); sync(); }, { passive: true });
  win.style.overflowAnchor = 'none';                                // the pin keeps the place, not the browser's anchoring
  win.addEventListener('touchstart', free, { passive: true });     // a finger on the window: the reader's own scroll

  // keys while the window has the focus
  win.addEventListener('keydown', function (e) {
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    var t = e.target; if (t && /^(INPUT|TEXTAREA|SELECT|BUTTON)$/.test(t.tagName)) return;
    var ch = win.clientHeight, d = { ArrowDown: 40, ArrowUp: -40, PageDown: ch * 0.9, PageUp: -ch * 0.9, ' ': e.shiftKey ? -ch * 0.9 : ch * 0.9 }[e.key];
    if (e.key === 'Home') { free(); win.scrollTop = view === 'doc' ? padTop() : 0; e.preventDefault(); return; }       // E33 B4: the start, not the room above it
    if (e.key === 'End') { free(); win.scrollTop = view === 'doc' ? Math.max(0, Math.round(topOf(padB) - win.clientHeight)) : win.scrollHeight; e.preventDefault(); return; }
    if (d) { free(); win.scrollTop += d; e.preventDefault(); }
  });

  // links inside the reading version (table of contents) jump in the window, never move the page
  root.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href^="#"]') : null;
    if (!a) return;
    var t = byId(decodeURIComponent(a.getAttribute('href').slice(1)));
    if (!t) return;
    e.preventDefault();
    // E30: a chapter of the contents list goes like its mark (open, on the reading height, held); anything else to the line too
    for (var i = 0; i < chaps.length; i++) if (chaps[i].el === t && chaps[i].e) { sel = chaps[i].e; selMark(); go(chaps[i].e); return; }
    if (view !== 'doc') setView('doc');
    reveal(t); free(); win.scrollTop = Math.max(0, Math.round(topOf(t) - rlNow())); sync();
  });

  // the thumb: drag (proportional), click on the track = go there (E31 S1: the scroll bar of the tool column)
  var drag = null;
  thumb.addEventListener('pointerdown', function (e) {
    drag = { y: e.clientY, t: win.scrollTop }; free();
    try { thumb.setPointerCapture(e.pointerId); } catch (x) {}
    e.preventDefault(); e.stopPropagation();
  });
  thumb.addEventListener('pointermove', function (e) {
    if (!drag) return;
    var tk = sb.clientHeight, tl = thumb.offsetHeight, sh = win.scrollHeight, ch = win.clientHeight;
    win.scrollTop = drag.t + (e.clientY - drag.y) * (sh - ch) / Math.max(1, tk - tl);
  });
  function undrag() { drag = null; }
  thumb.addEventListener('pointerup', undrag); thumb.addEventListener('pointercancel', undrag);
  sb.addEventListener('click', function (e) {
    if (e.target !== sb) return;
    free();
    var r = sb.getBoundingClientRect(), tl = thumb.offsetHeight;
    var f = Math.min(1, Math.max(0, (e.clientY - r.top - tl / 2) / Math.max(1, r.height - tl)));
    win.scrollTop = f * (win.scrollHeight - win.clientHeight);
  });

  // ---- E26 Teil 2 (Python workshop): exercises, sliders, copy lines -------
  // Markup and data come from the kernel (_nbrw_* in chapter_template.py):
  // .nbrw-task[data-kind=calc][data-task][data-st][data-a] (answers +
  // tolerances of this run, base64 JSON), .nbrw-slider[data-z] (pictures,
  // base64 zlib JSON), .nbrw-copy[data-kind=code][data-guard]. A state kept
  // here wins over the kernel's start state: K.task.<t> (this page),
  // K.code.<t> (written by pruefe() in a cell of the same notebook, or by
  // ▶ in the window).
  var DONE = { solved: 1, wrong: 1, skipped: 1 };
  var tasks = [];
  function dec(s) { try { return JSON.parse(W.atob(s || '')); } catch (e) { return null; } }
  function decTxt(s) {      // base64 of UTF-8 text
    try { var b = W.atob(s || ''), u = new W.Uint8Array(b.length); for (var i = 0; i < b.length; i++) u[i] = b.charCodeAt(i); return new W.TextDecoder().decode(u); }
    catch (e) { return ''; }
  }
  function num(s) {
    s = String(s == null ? '' : s).replace(/\s+/g, '').replace(/[\u2212\u2013]/g, '-').replace(',', '.');
    return /^[-+]?(\d+\.?\d*|\.\d+)(e[-+]?\d+)?$/i.test(s) ? parseFloat(s) : null;
  }
  function stOf(t) {
    var v = load((t.kind === 'code' ? 'code.' : 'task.') + t.key, '');
    return DONE[v] ? v : (t.st0 === 'locked' ? 'open' : t.st0);
  }
  function taskBy(kind, key) { for (var i = 0; i < tasks.length; i++) if (tasks[i].kind === kind && tasks[i].key === key) return tasks[i]; return null; }
  function gate() {               // like Lab: a task waits for the one before it; code waits for its guard
    var prev = null, byKey = {};
    tasks.forEach(function (t) { if (t.kind === 'code') byKey[t.key] = t; });
    tasks.forEach(function (t) {
      var s = stOf(t), lock = false;
      if (t.kind === 'calc') { lock = !!(prev && !DONE[stOf(prev)]); if (t.key && !t.off) prev = t; }
      else { var g = byKey[t.guard]; lock = !!(t.guard && (g ? !g.off && !DONE[stOf(g)] : t.st0 === 'locked')); }
      if (t.off) lock = false;
      if (lock && !DONE[s]) s = 'locked';
      t.el.setAttribute('data-st', s);
      [].forEach.call(t.el.querySelectorAll('input,textarea,.nbrw-check,.nbrw-run'), function (x) { x.disabled = s === 'locked'; });
      if (s === 'locked') { t.fb.textContent = t.kind === 'code' ? T.clock : T.lock; t.fb.removeAttribute('data-ok'); }
      else if (t.fb.textContent === TT.de.lock || t.fb.textContent === TT.en.lock || t.fb.textContent === TT.de.clock || t.fb.textContent === TT.en.clock) t.fb.textContent = '';
      if (t.mark) t.mark.setAttribute('data-st', s);
      (t.pips || []).forEach(function (p) { p.setAttribute('data-st', s); });
    });
    gateChaps(); xpPaint(); tlPaint();
  }
  // E26.3 · 3: chapters wait for their exercise ([data-nbrw-gate="calc:t2"])
  var gates = [];
  function gateChaps() {
    var any = false;
    chaps.forEach(function (c) { c.locked = false; });
    gates.forEach(function (g) {
      var t = taskBy(g.kind, g.key), lock = !!(t && !t.off && !DONE[stOf(t)]);
      if (lock !== g.lock) {
        any = true; g.lock = lock;
        imp(g.el, 'display', lock ? 'none' : g.disp);
        g.el.setAttribute('data-st', lock ? 'locked' : 'open');
        imp(g.msg, 'display', lock ? 'block' : 'none');
      }
      g.msg.textContent = L.lock.replace('%s', (g.kind === 'code' ? T.mcode : T.mcalc) + ' ' + g.key.replace(/^t/, ''));
      if (lock && g.ch >= 0 && chaps[g.ch]) chaps[g.ch].locked = true;
    });
    if (any && ready) later();
  }
  function xpPaint() {
    var n = 0, s = 0;
    tasks.forEach(function (t) { if (t.off || !t.key) return; n++; if (stOf(t) === 'solved') s++; });
    xpT.textContent = L.xp + ' ' + s + ' / ' + n;
    xpF.style.width = (n ? Math.round(100 * s / n) : 0) + '%';
    xp.setAttribute('data-n', String(n)); xp.setAttribute('data-solved', String(s));
    imp(xp, 'display', n ? '' : 'none');
  }
  function judge(t) {
    if (t.el.getAttribute('data-st') === 'locked') return;
    var a = t.a || {}, ok;
    if (a.c != null) {
      var r = t.el.querySelector('input[type=radio]:checked');
      if (!r) { t.fb.textContent = T.pick; t.fb.removeAttribute('data-ok'); return; }
      ok = +r.value === +a.c;
    } else {
      var f = a.f || [], bad = false;
      ok = f.length > 0;
      f.forEach(function (x) {
        var inp = t.el.querySelector('.nbrw-input[data-f="' + x[0] + '"]'), v = num(inp && inp.value);
        if (v == null) { bad = true; return; }
        var d = Math.abs(v - x[1]);
        if (x[3] > 0) { d = ((v - x[1]) % x[3] + x[3]) % x[3]; d = Math.min(d, x[3] - d); }
        if (!(d <= x[2] + 1e-12)) ok = false;
      });
      if (bad) { t.fb.textContent = T.num; t.fb.removeAttribute('data-ok'); return; }
    }
    t.fb.textContent = ok ? T.ok : T.bad; t.fb.setAttribute('data-ok', ok ? '1' : '0');
    var was = stOf(t);
    if (ok) save('task.' + t.key, 'solved'); else if (was !== 'solved') save('task.' + t.key, 'wrong');
    gate();
  }
  // the stub is the <code> child of .nbrw-copy — not the <code>pruefe()</code> in its sentence (v1.73 copied that one)
  function codeEl(el) { var c = [].filter.call(el.children, function (x) { return x.tagName === 'CODE'; }); return c[c.length - 1] || null; }
  function pruefeLine(t) {
    var c = t.code0 || '', m = /^\s*pruefe\(.*$/m.exec(c);
    return m ? m[0].trim() : 'pruefe("' + t.key + '")';
  }
  function codeText(t) {     // what goes to the clipboard: the field as it is now + the pruefe line
    if (!t.ta) return t.code0 || '';
    var v = t.ta.value.replace(/\s+$/, '');
    return /^\s*pruefe\(/m.test(v) ? v + '\n' : v + '\n\n' + pruefeLine(t) + '\n';
  }
  function copyOf(t) {
    var c = codeEl(t.el), tx = codeText(t);
    function done(okc) { t.fb.textContent = okc ? T.copied : T.nocopy; t.fb.removeAttribute('data-ok'); }
    function old() {
      try {
        var r = D.createRange(), sel = W.getSelection();
        if (t.ta) { t.ta.focus(); t.ta.select(); } else { r.selectNodeContents(c); sel.removeAllRanges(); sel.addRange(r); }
        done(D.execCommand('copy'));
      } catch (e) { done(false); }
    }
    try { if (W.navigator.clipboard && W.isSecureContext) { W.navigator.clipboard.writeText(tx).then(function () { done(true); }, old); return; } } catch (e) {}
    old();
  }

  // ---- E26.3 · 3: the coding field and ▶ in the window ----------------------
  var KW = /^(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)$/;
  function esc(s) { return s.replace(/&/g, '&amp;').replace(/[<]/g, '&lt;').replace(/>/g, '&gt;'); }
  function hl(src) {
    var re = /(#[^\n]*)|('{3}[\s\S]*?(?:'{3}|$)|"{3}[\s\S]*?(?:"{3}|$)|'(?:\\.|[^'\\\n])*'?|"(?:\\.|[^"\\\n])*"?)|(\b\d+(?:\.\d*)?(?:[eE][-+]?\d+)?j?\b)|([A-Za-z_]\w*)/g;
    var out = '', i = 0, m, prevDef = false;
    while ((m = re.exec(src))) {
      out += esc(src.slice(i, m.index)); i = re.lastIndex;
      var w = m[0], c = m[1] ? 'c' : m[2] ? 's' : m[3] ? 'n' : KW.test(w) ? 'k' : prevDef ? 'f' : '';
      prevDef = m[4] ? (w === 'def' || w === 'class') : false;
      out += c ? '<span class="nbrw-hl-' + c + '">' + esc(w) + '</span>' : esc(w);
    }
    return out + esc(src.slice(i)) + '\n';
  }
  function field(t) {
    var c = codeEl(t.el); if (!c) return;
    var src = (t.code0 || '').replace(/^\s*pruefe\(.*$\n?/m, '').replace(/\s+$/, '') + '\n';
    var box = mk('div', 'nbrw-code'), pre = mk('pre', 'nbrw-hl'), ta = mk('textarea', 'nbrw-ta');
    pre.setAttribute('aria-hidden', 'true');
    ta.spellcheck = false; ta.setAttribute('autocomplete', 'off'); ta.setAttribute('autocapitalize', 'off');
    ta.setAttribute('aria-label', T.mcode + ' ' + t.key.replace(/^t/, ''));
    ta.value = load('src.' + t.key, src);
    var S = 'margin:0;padding:8px 10px;box-sizing:border-box;font:inherit;line-height:inherit;white-space:pre;tab-size:4;overflow:auto;border:0;letter-spacing:0;word-spacing:0;';
    pre.style.cssText = S;
    ta.style.cssText = S + 'position:absolute;inset:0;width:100%;height:100%;resize:none;outline:none;';
    imp(ta, 'color', 'transparent'); imp(ta, 'background-color', 'transparent'); imp(ta, 'caret-color', 'currentColor');
    imp(ta, 'position', 'absolute'); imp(pre, 'position', 'relative'); imp(box, 'position', 'relative');
    imp(box, 'flex', '1 1 100%'); imp(box, 'width', '100%');      // a whole line, even in a flex row of .nbrw-copy
    box.appendChild(pre); box.appendChild(ta);
    function draw() { pre.innerHTML = hl(ta.value); pre.scrollTop = ta.scrollTop; pre.scrollLeft = ta.scrollLeft; }
    ta.addEventListener('input', function () { draw(); save('src.' + t.key, ta.value); });
    ta.addEventListener('scroll', function () { pre.scrollTop = ta.scrollTop; pre.scrollLeft = ta.scrollLeft; });
    ta.addEventListener('keydown', function (e) {
      if (e.key === 'Tab' && !e.shiftKey && !e.ctrlKey && !e.altKey) {
        e.preventDefault(); var a = ta.selectionStart, b = ta.selectionEnd;
        ta.value = ta.value.slice(0, a) + '    ' + ta.value.slice(b); ta.selectionStart = ta.selectionEnd = a + 4; draw();
      } else if (e.key === 'Enter' && (e.shiftKey || e.ctrlKey)) { e.preventDefault(); run(t); }
    });
    ta.addEventListener('wheel', function (e) { e.stopPropagation(); }, { passive: true });
    imp(c, 'display', 'none');
    var row = mk('div', 'nbrw-runrow'), rb = mk('button', 'nbrw-run'), rs = mk('span', 'nbrw-runst'), out = mk('pre', 'nbrw-out');
    rb.type = 'button'; rs.setAttribute('role', 'status'); imp(out, 'display', 'none');
    imp(row, 'flex', '1 1 100%'); imp(out, 'flex', '1 1 100%'); imp(out, 'box-sizing', 'border-box'); imp(out, 'width', '100%');
    rb.addEventListener('click', function (e) { e.preventDefault(); run(t); });
    row.appendChild(rb); row.appendChild(rs);
    c.parentNode.insertBefore(box, c.nextSibling);
    box.parentNode.insertBefore(row, box.nextSibling);
    row.parentNode.insertBefore(out, row.nextSibling);
    t.ta = ta; t.rb = rb; t.rs = rs; t.out = out; t.draw = draw;
    draw();
  }
  function fieldLabels() {
    tasks.forEach(function (t) {
      if (t.rb) t.rb.textContent = T.run;
      if (t.cb) t.cb.textContent = T.clip;
    });
  }
  var PYV = '0.27.7', PYCDN = 'https://cdn.jsdelivr.net/pyodide/v' + PYV + '/full/', PYURL = PYCDN;
  // E38a J2: in lesen.html the shell's loader hands over manifest.pyodide (own server, absolute, ends in /) as
  // window.DIGICHEMJN.pyodide; in Jupyter there is none → jsDelivr as before (the .ipynb runs anywhere)
  function pyUrl() {
    var u = W.DIGICHEMJN && W.DIGICHEMJN.pyodide;
    return typeof u === 'string' && /^https?:\/\/[^\s]+\/$/.test(u) ? u : PYCDN;
  }
  var pyP = null, pyOk = false;
  function py() {           // Pyodide once, at the first ▶ (browser cache after that)
    if (pyP) return pyP;
    PYURL = pyUrl();
    pyP = new W.Promise(function (ok, no) {
      var to = W.setTimeout(function () { no(new Error('timeout')); }, 90000);
      function go() {
        if (!W.loadPyodide) { W.clearTimeout(to); no(new Error('no loader')); return; }
        W.loadPyodide({ indexURL: PYURL }).then(function (P) { W.clearTimeout(to); pyOk = true; ok(P); },
                                               function (e) { W.clearTimeout(to); no(e); });
      }
      if (W.loadPyodide) { go(); return; }
      var s = D.createElement('script'); s.src = PYURL + 'pyodide.js'; s.async = true; s.crossOrigin = 'anonymous';
      s.onload = go; s.onerror = function () { W.clearTimeout(to); no(new Error('load')); };
      (D.head || D.documentElement).appendChild(s);
    });
    pyP.then(null, function () { pyP = null; });          // another click may try again
    return pyP;
  }
  function said(t, s, off) { t.rs.textContent = s; if (off) t.rs.setAttribute('data-off', '1'); else t.rs.removeAttribute('data-off'); }
  function outp(t, s, err) {
    t.out.textContent = s; t.out.setAttribute('data-err', err ? '1' : '0');
    imp(t.out, 'display', s ? 'block' : 'none');
  }
  function offline(t) {
    var pl = pruefeLine(t); if (!/,/.test(pl)) pl = pl.replace(/\)\s*$/, ', \u2026)');
    said(t, T.pyoff.replace('%s', pl), true);
    if (t.cb) { imp(t.cb, 'display', ''); t.cb.textContent = T.clip; }
  }
  function trim(msg) {      // a Python traceback without Pyodide's own frames
    var ls = String(msg || '').split('\n'), o = [], skip = false;
    ls.forEach(function (l) {
      if (/^\s*File "\/lib\/python/.test(l)) { skip = true; return; }
      if (skip && /^\s{4}/.test(l)) return;
      skip = false; o.push(l);
    });
    return o.join('\n').trim();
  }
  function run(t) {
    if (t.busy || t.el.getAttribute('data-st') === 'locked') return;
    t.busy = true; t.rb.disabled = true;
    if (!pyOk) said(t, T.pyload);
    var src = t.ta.value, chk = decTxt(t.el.getAttribute('data-check')),
        pk = (t.el.getAttribute('data-pkgs') || '').split(/[\s,]+/).filter(Boolean);
    function end() { t.busy = false; t.rb.disabled = t.el.getAttribute('data-st') === 'locked'; }
    py().then(function (P) {
      var need = pk.length ? P.loadPackage(pk) : W.Promise.resolve();
      if (pk.length) said(t, T.pypkg + pk.join(', '));
      return need.then(function () { return P.loadPackagesFromImports(src + '\n' + chk); }).then(function () {
        said(t, T.pyrun);
        var buf = [];
        P.setStdout({ batched: function (s) { buf.push(s); } }); P.setStderr({ batched: function (s) { buf.push(s); } });
        var ns = P.globals.get('dict')();
        return P.runPythonAsync(src, { globals: ns }).then(function () {
          if (!chk) { outp(t, buf.join('\n'), false); said(t, T.nochk.replace('%s', pruefeLine(t))); return; }
          return P.runPythonAsync(chk + '\n_nbrw_r = _nbrw_check(globals())', { globals: ns }).then(function () {
            var r = ns.get('_nbrw_r'), ok = false, tip = '';
            try { var a = r && r.toJs ? r.toJs() : r; ok = !!(a && a[0]); tip = a && a[1] != null ? String(a[1]) : ''; } catch (x) {}
            if (r && r.destroy) r.destroy();
            outp(t, buf.join('\n'), false);
            t.fb.textContent = (ok ? T.ok : T.bad) + (tip ? ' ' + tip : ''); t.fb.setAttribute('data-ok', ok ? '1' : '0');
            if (ok) save('code.' + t.key, 'solved'); else if (stOf(t) !== 'solved') save('code.' + t.key, 'wrong');
            said(t, T.pydone); gate();
          });
        }, function (e) {
          outp(t, (buf.length ? buf.join('\n') + '\n' : '') + trim(e && e.message), true);
          said(t, T.pyerr);
        });
      });
    }).then(end, function () { offline(t); end(); });
  }

  [].forEach.call(root.querySelectorAll('.nbrw-task,.nbrw-copy'), function (el) {
    var t = { el: el, kind: el.getAttribute('data-kind') === 'code' ? 'code' : 'calc', key: el.getAttribute('data-task') || '',
              st0: el.getAttribute('data-st') || 'open', guard: el.getAttribute('data-guard') || '',
              a: dec(el.getAttribute('data-a')), fb: el.querySelector('.nbrw-fb'), disp: el.style.getPropertyValue('display') };
    if (!t.fb) { t.fb = mk('span', 'nbrw-fb'); el.appendChild(t.fb); }
    if (t.kind === 'calc') {
      var b = el.querySelector('.nbrw-check');
      if (b) b.addEventListener('click', function (e) { e.preventDefault(); judge(t); });
      el.addEventListener('keydown', function (e) { if (e.key === 'Enter' && e.target && e.target.tagName === 'INPUT') { e.preventDefault(); judge(t); } });
    } else {
      var cd = codeEl(el); t.code0 = cd ? cd.textContent : '';
      t.cb = el.querySelector('.nbrw-copybtn');
      if (t.cb) t.cb.addEventListener('click', function (e) { e.preventDefault(); copyOf(t); });
      if (t.key) field(t);
    }
    if (t.key || t.kind === 'calc') tasks.push(t);
  });
  W.addEventListener('storage', function (e) {     // pruefe() in another cell (output) of this notebook
    if (!e.key || e.key.indexOf(K + '.code.') !== 0) return;
    gate();
    tasks.forEach(function (t) {
      if (t.kind === 'code' && e.key === K + '.code.' + t.key) {
        t.fb.textContent = e.newValue === 'solved' ? T.csolved : T.cwrong; t.fb.setAttribute('data-ok', e.newValue === 'solved' ? '1' : '0');
      }
    });
  });
  // sliders over pictures drawn by the kernel
  function inflate(b64) {
    var bin = W.atob(b64), u = new W.Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
    return new W.Response(new W.Blob([u]).stream().pipeThrough(new W.DecompressionStream('deflate'))).text().then(JSON.parse);
  }
  [].forEach.call(root.querySelectorAll('.nbrw-slider[data-z]'), function (el) {
    if (!W.DecompressionStream || !W.Blob || !W.Response) return;           // too old a browser: the start picture stays
    var fig = el.querySelector('.nbrw-fig'), rs = el.querySelectorAll('.nbrw-range'), os = el.querySelectorAll('.nbrw-val');
    inflate(el.getAttribute('data-z')).then(function (P) {
      var cur0 = 0;
      function show(s, j) {
        var c = P.c[s]; if (!c) return;
        [].forEach.call(rs, function (r, q) {
          var cq = P.c[q], jj = q === s ? j : cq.d;
          r.value = String(jj);
          if (os[q]) os[q].textContent = os[q].getAttribute('data-desc') + ' = ' + cq.l[jj];
        });
        var f = c.i[j] || 0;
        if (f !== cur0 && P.f[f] != null) { fig.innerHTML = P.f[f]; cur0 = f; }
        el.setAttribute('data-frame', String(f));
      }
      [].forEach.call(rs, function (r) {
        r.style.display = ''; r.addEventListener('input', function () { show(+r.getAttribute('data-s'), +r.value); });
      });
      [].forEach.call(os, function (o) { o.style.display = ''; });
      // E33 B4: the slider and its value on the column's axis (the value's box ran to the right edge, the pair sat left)
      if (/flex/.test(W.getComputedStyle(el).display)) {
        imp(el, 'justify-content', 'center'); imp(el, 'column-gap', '12px');
        [].forEach.call(os, function (o) { imp(o, 'flex', '0 0 auto'); imp(o, 'width', 'auto'); imp(o, 'min-width', '5.5em'); });
      }
      el.setAttribute('data-ready', '1');
      el.__nbrwShow = show;
    }, function () {});
  });

  // ---- E26.3 · 3: the mode hides what it leaves out --------------------------
  var only = [].slice.call(root.querySelectorAll('[data-nbrw-only]')).map(function (el) { return { el: el, k: el.getAttribute('data-nbrw-only'), disp: el.style.getPropertyValue('display') }; });
  function offFor(kind) { return mode === 'plain' || (kind === 'calc' && mode === 'code') || (kind === 'code' && mode === 'calc'); }
  function setMode(m, user) {
    if (MODES.indexOf(m) < 0) return;
    mode = m; if (user) save('mode', m);
    wrap.setAttribute('data-nbrw-mode', m);
    tasks.forEach(function (t) {
      t.off = offFor(t.kind);
      if (t.off) imp(t.el, 'display', 'none'); else if (ready) imp(t.el, 'display', t.disp === 'none' ? '' : t.disp);
    });
    only.forEach(function (o) { imp(o.el, 'display', offFor(o.k) ? 'none' : (o.disp === 'none' ? '' : o.disp)); });
    [].forEach.call(cover.querySelectorAll('.nbrw-mode-opt[data-mode]'), function (o) {
      var on = o.getAttribute('data-mode') === m; o.setAttribute('aria-checked', String(on)); o.classList.toggle('on', on);
    });
    gate();
    if (ready) later();
  }

  // ---- E26.3 · 1: language ---------------------------------------------------
  // E30 B2 (PyCharm: title and document English, contents and panel German) —
  // ONE LANGUAGE IN THE WINDOW. The preview is bilingual and follows EN|DE.
  // The document follows it where its markup carries both languages
  // ([data-nbrw-l] inside the folds); a document built in one language only
  // keeps the panel, the marks, the contents list and every word of this
  // script in ITS language, and one line says so (in the chosen one).
  var lgDoc = lg0, docBI = false;
  function eff() { return view === 'cover' || docBI || lg === lgDoc ? lg : lgDoc; }
  function langView() {
    var x = eff();
    setLang(x);
    root.setAttribute('lang', x); wrap.setAttribute('data-nbrw-lang', x);
    chaps.forEach(function (c) { c.title = txt(c.a); });
    label(); fieldLabels();
    var off = view === 'doc' && x !== lg;
    note.textContent = off ? LT[lg].only.replace('%s', LT[lg].lname[x]) : '';
    note.setAttribute('lang', lg);
    imp(note, 'display', off ? 'block' : 'none');
    gate(); curI = -2;
    if (ready) { drawMarks(); later(); if (drwKind) drawer(drwKind); acAll(); }
  }
  function applyLang(x, user) {
    lg = x; if (user) save('lang', x);
    setLang(x);
    [].forEach.call(cover.querySelectorAll('[data-lang]'), function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-lang') === x)); });
    if (ownCover) { chaps.forEach(function (c) { c.title = txt(c.a); }); buildCover(); }
    langView();
  }

  // ---- E26.3 · 1: the cover (Python's, or built here) ------------------------
  function buildCover() {
    cover.innerHTML = '';
    if (BI) {
      var lr = mk('div', 'nbrw-cv-lang nbrw-lang'); lr.setAttribute('role', 'group'); lr.setAttribute('aria-label', L.lang);
      ['en', 'de'].forEach(function (x) { var b = mk('button', '', x.toUpperCase()); b.type = 'button'; b.setAttribute('data-lang', x); b.setAttribute('aria-pressed', String(x === lg)); lr.appendChild(b); });
      cover.appendChild(lr);
    }
    var card = [].filter.call(doc.children, function (e) { return e.tagName === 'DIV' && /text-align:\s*center/.test(e.getAttribute('style') || '') && e.querySelector('[class*="nbtitle"]'); })[0];
    if (card) {
      var cc = card.cloneNode(true);
      [].forEach.call(cc.querySelectorAll('[id]'), function (x) { x.removeAttribute('id'); });
      cover.appendChild(cc);
    }
    cover.appendChild(mk('div', 'nbrw-cv-t nbrw-cv-h', L.tl));
    cover.appendChild(mk('div', 'nbrw-cv-tl'));
    cover.appendChild(mk('div', 'nbrw-cv-t nbrw-cv-h', L.modeT));
    var ms = mk('div', 'nbrw-modes'); ms.setAttribute('role', 'radiogroup'); ms.setAttribute('aria-label', L.modeT);
    MODES.forEach(function (m) {
      var o = mk('button', 'nbrw-mode-opt'), d = L.modes[m]; o.type = 'button'; o.setAttribute('role', 'radio'); o.setAttribute('data-mode', m);
      o.setAttribute('aria-checked', String(m === mode));
      o.appendChild(mk('span', 'nbrw-mode-ic', d[0])); o.appendChild(mk('b', 'nbrw-mode-l', d[1])); o.appendChild(mk('span', 'nbrw-mode-d', d[2]));
      ms.appendChild(o);
    });
    cover.appendChild(ms);
    var pl = mk('button', 'nbrw-play', '\u25B6'); pl.type = 'button'; pl.setAttribute('data-nbrw-act', 'play'); pl.title = L.playT;
    pl.setAttribute('aria-label', L.play + ' \u2014 ' + L.playT);
    var row = cover.appendChild(mk('div', 'nbrw-cv-row'));
    row.appendChild(pl); row.appendChild(mk('span', 'nbrw-play-lab', L.play));     // like Lab: the ring, its name under it
    var ac = mk('details', 'nbrw-acct'); ac.appendChild(mk('summary', '', L.acct)); ac.appendChild(mk('div', '', L.acctT));
    cover.appendChild(ac);
    tlPaint();
    if (ready) acCover();
  }
  // E31 T1 — THE PREVIEW'S TIMELINE LIKE LAB'S: ONE row. A line, the marks on it in the document's order
  // (title, parts, chapters, figures, exercises of this mode, the end), the names of title, parts and chapters
  // alternating below and above the line on one line each — never wrapped, never stacked; wider than the room,
  // the row scrolls sideways (Lab E13). Python ships the place empty (.nbrw-cv-tl); one drawn by Python stays.
  var tlSig = '';
  function tlPaint() {
    var tl = cover.querySelector('.nbrw-cv-tl'); if (!tl || !chaps.length) return;
    if (tl.getAttribute('data-nbrw-py') === '1') return;
    var its = [];
    ents.forEach(function (e) {
      if (e.kind === 'sub' || e.kind === 'yoc' || (e.t && e.t.off)) return;
      var st = stE(e), nm = '';
      if (e.kind === 'chap') nm = chaps[e.ch].title;
      else if (e.kind === 'title' || e.kind === 'group' || e.kind === 'end') nm = nameOf(e);
      its.push({ e: e, k: e.kind, st: st, nm: nm });
    });
    var sig = its.map(function (x) { return x.k + x.st + x.nm; }).join('|') + (de ? 'd' : 'e');
    if (sig === tlSig && tl.querySelector('.nbrw-cv-in')) { tlLay(); return; }
    tlSig = sig;
    tl.innerHTML = ''; tl.setAttribute('data-nbrw-row', '1');
    var sc = tl.appendChild(mk('div', 'nbrw-cv-scroll')), inn = sc.appendChild(mk('div', 'nbrw-cv-in'));
    inn.appendChild(mk('div', 'nbrw-cv-line'));
    var side = 'down';
    its.forEach(function (x) {
      var d = mk('span', 'nbrw-cv-dot'); d.setAttribute('data-kind', x.k); d.setAttribute('data-st', x.st);
      if (x.k === 'chap') d.setAttribute('data-ch', String(x.e.ch));
      if (x.e.t) { d.setAttribute('data-task', x.e.t.key); d.title = (x.k === 'code' ? T.mcode : T.mcalc) + ' ' + x.e.t.key.replace(/^t/, ''); }
      if (x.nm) {
        d.setAttribute('data-side', side); side = side === 'down' ? 'up' : 'down';
        d.appendChild(mk('span', 'nbrw-cv-lab', x.nm));
      }
      // E33 B2: no browser tooltip — the description line under the row says it (Lab E15.4)
      d.removeAttribute('title'); d.setAttribute('data-nm', (x.st === 'locked' ? '\uD83D\uDD12 ' : '') + (x.nm || nameOf(x.e)));
      d.setAttribute('data-desc', cvDesc(x.e, x.st)); d.setAttribute('data-e', String(ents.indexOf(x.e)));
      d.style.zIndex = '1';
      inn.appendChild(d);
    });
    var dsc = mk('div', 'nbrw-cv-desc'); dsc.setAttribute('role', 'status'); tl.appendChild(dsc);      // last child of the row (css-E33 B2)
    cvShow(null);
    tlLay();
  }
  // E33 B2 — THE PREVIEW'S TIMELINE ANSWERS LIKE LAB'S (17-rail-marker E15.4/E16.5): hover over a mark → the line under
  // the row says its name and what it is (a FIXED room: nothing below moves, E29 P3); a click pins it, again lets
  // go; a click on Title or a part (Introduction, Content, Appendix) folds the row behind it up to the next part
  // (Title: all but itself and the end) and unfolds it again
  var cvPin = null, cvShut = {};
  function cvDesc(e, st) {
    if (st === 'locked') return gateMsg(e) || T.lock;
    var tt = e.tn ? tplTitle(e.tn) : '';
    if (e.kind === 'chap') { var ts = tasksOf(e.ch), sv = ts.filter(function (t) { return stOf(t) === 'solved'; }).length;
      return L.k.chap + ' ' + (e.ch + 1) + (ts.length ? ' \u00B7 ' + sv + ' / ' + ts.length + ' ' + L.tasks + ' ' + L.st.solved : ''); }
    if (e.kind === 'title' || e.kind === 'group') return (e.kind === 'title' ? L.k.title : L.k.group) + ' \u00B7 ' + (de ? 'Klick: ein-/ausklappen' : 'click: fold/unfold');
    if (e.t) return (tt && tt.indexOf(nameOf(e)) < 0 ? tt + ' \u00B7 ' : '') + L.k[e.kind] + ' \u00B7 ' + (L.st[st] || st);
    return tt || L.k[e.kind] || '';
  }
  function cvShow(d) {
    var dsc = cover.querySelector('.nbrw-cv-desc'); if (!dsc) return;
    var x = d || cvPin;
    dsc.innerHTML = '';
    if (!x) { dsc.setAttribute('data-on', '0'); dsc.hidden = true; return; }
    dsc.setAttribute('data-on', '1'); dsc.hidden = false;
    dsc.appendChild(mk('b', '', x.getAttribute('data-nm') || '')); dsc.appendChild(mk('span', '', x.getAttribute('data-desc') || ''));
  }
  function cvFold() {             // the dots behind a shut Title / part
    var ds = [].slice.call(cover.querySelectorAll('.nbrw-cv-dot')), hide = false, by = null;
    ds.forEach(function (d) {
      var k = d.getAttribute('data-kind'), i = d.getAttribute('data-e');
      if (k === 'group' || k === 'end') { if (by && (by === 'group' || k === 'end')) { hide = false; by = null; } }
      d.__fold = hide && k !== 'end';
      d.classList.toggle('is-shut', !!cvShut[i]);
      if (!hide && cvShut[i] && (k === 'title' || k === 'group')) { hide = true; by = k; }
      if (k === 'title') { var tl = d.closest('.nbrw-cv-tl'); if (tl) { if (cvShut[i]) tl.setAttribute('data-nbrw-fold', '1'); else tl.removeAttribute('data-nbrw-fold'); } }
    });
  }
  cover.addEventListener('pointerover', function (e) {
    var d = e.target && e.target.closest ? e.target.closest('.nbrw-cv-dot') : null;
    [].forEach.call(cover.querySelectorAll('.nbrw-cv-dot.is-hov'), function (x) { if (x !== d) x.classList.remove('is-hov'); });
    if (d) { d.classList.add('is-hov'); cvShow(d); }
  });
  cover.addEventListener('pointerout', function (e) {
    var d = e.target && e.target.closest ? e.target.closest('.nbrw-cv-dot') : null, t = e.relatedTarget && e.relatedTarget.closest ? e.relatedTarget.closest('.nbrw-cv-dot') : null;
    if (d && d !== t) { d.classList.remove('is-hov'); if (!t) cvShow(null); }
  });
  function tlLay() {        // the places: measured, so the names of one side never touch (Lab's alternating names)
    var tl = cover.querySelector('.nbrw-cv-tl[data-nbrw-row]'); if (!tl || !tl.getClientRects().length) return;
    var sc = tl.querySelector('.nbrw-cv-scroll'), inn = tl.querySelector('.nbrw-cv-in'), ln = tl.querySelector('.nbrw-cv-line');
    cvFold();
    var ds = [].slice.call(inn.querySelectorAll('.nbrw-cv-dot')).filter(function (d) { imp(d, 'display', d.__fold ? 'none' : ''); return !d.__fold; });
    if (!ds.length) return;
    imp(sc, 'position', 'relative'); imp(inn, 'position', 'relative'); imp(inn, 'margin', '0 auto'); imp(ln, 'position', 'absolute');
    // the line's colour is CSS's (css-E31 T1); only where nothing paints it (Python's reset in .nbreading) a fallback
    imp(ln, 'background', ''); if (/rgba\(0, 0, 0, 0\)|transparent/.test(W.getComputedStyle(ln).backgroundColor)) imp(ln, 'background', 'var(--rw-sec,#55636f)');
    imp(ln, 'height', '4px'); imp(ln, 'margin-top', '-2px'); imp(ln, 'z-index', '0'); imp(ln, 'opacity', '.85');
    var GAP = 10, STEP = 16, x = 0, prev = null, last = { up: -1e9, down: -1e9 }, lh = 0, xs = [], lo = 0, hi = 0;
    ds.forEach(function (d) {
      var lb = d.querySelector('.nbrw-cv-lab'), w = lb ? lb.offsetWidth : 0, sd = d.getAttribute('data-side');
      if (lb) lh = Math.max(lh, lb.offsetHeight);
      x = prev == null ? 0 : x + (lb || prev ? STEP + 6 : STEP);
      if (lb) { x = Math.max(x, last[sd] + GAP + w / 2); last[sd] = x + w / 2; lo = Math.min(lo, x - w / 2); hi = Math.max(hi, x + w / 2); }
      hi = Math.max(hi, x); xs.push(x); prev = lb || true;
    });
    var pad = 8 - lo, W0 = Math.ceil(hi - lo + 16), mid = Math.round(lh + 16);
    ds.forEach(function (d, i) { d.style.left = Math.round(xs[i] + pad) + 'px'; d.style.top = mid + 'px'; });
    ln.style.left = Math.round(xs[0] + pad) + 'px'; ln.style.width = Math.max(0, Math.round(xs[xs.length - 1] - xs[0])) + 'px'; ln.style.top = mid + 'px';
    inn.style.width = W0 + 'px'; inn.style.height = (2 * mid) + 'px';
    var room = Math.max(120, (tl.parentElement ? tl.parentElement.clientWidth : 600) - 24);
    sc.style.width = Math.min(W0, room) + 'px';
  }
  cover.addEventListener('click', function (e) {
    var b = e.target && e.target.closest ? e.target.closest('button,[data-nbrw-act]') : null;
    var cd = e.target && e.target.closest ? e.target.closest('.nbrw-cv-dot') : null;
    if (cd && cover.contains(cd)) {       // E33 B2: Title/parts fold the row; any other mark pins its line
      e.preventDefault(); var k = cd.getAttribute('data-kind'), i = cd.getAttribute('data-e');
      if (k === 'title' || k === 'group') { cvShut[i] = !cvShut[i]; tlLay(); cvShow(cd); }
      else { var was = cover.querySelector('.nbrw-cv-dot.is-pin'); if (was) was.classList.remove('is-pin'); cvPin = was === cd ? null : cd; if (cvPin) cd.classList.add('is-pin'); cvShow(cvPin); }
      return;
    }
    if (!b || !cover.contains(b)) return;
    if (b.getAttribute('data-nbrw-act') === 'play') { e.preventDefault(); setView('doc'); }
    else if (b.hasAttribute('data-lang') && BI) { e.preventDefault(); applyLang(b.getAttribute('data-lang'), true); }
    else if (b.hasAttribute('data-mode')) { e.preventDefault(); setMode(b.getAttribute('data-mode'), true); }
  });

  function setView(v) {
    if (v === view && ready) return;
    if (view === 'doc' && v === 'cover') docTop = win.scrollTop;
    view = v;
    wrap.setAttribute('data-nbrw-view', v);
    imp(cover, 'display', v === 'cover' ? 'block' : 'none');
    imp(doc, 'display', v === 'doc' ? 'block' : 'none');
    tip.removeAttribute('data-kind'); imp(tip, 'display', 'none');
    if (ready) langView();
    place();
    if (v === 'doc') {
      drawMarks();
      padDoc(); win.scrollTop = docTop < 0 ? padTop() : docTop;
      try { win.focus({ preventScroll: true }); } catch (e) {}
    } else { win.scrollTop = 0; drawMarks(); tlLay(); }
    sync();
  }

  // accordions (<details>): open/closed kept per notebook
  [].forEach.call(root.querySelectorAll('details[data-acc]'), function (d) {
    var id = d.getAttribute('data-acc'), v = load('acc.' + id, '');
    if (v === '1') d.open = true; else if (v === '0') d.open = false;
    d.addEventListener('toggle', function () { save('acc.' + id, d.open ? '1' : '0'); if (ready) later(); });
  });

  // ---- start ---------------------------------------------------------------
  var ready = false;
  wrap.style.setProperty('--nbrw-h', h + 'px');
  wrap.style.setProperty('--nbrw-zoom', String(Z[zi]));
  collect();
  docBI = !!doc.querySelector('details[data-acc] [data-nbrw-l]');
  rl = parseFloat(load('rl', '')) || NaN;
  fsApply(); gsApply();
  gates = [].map.call(root.querySelectorAll('[data-nbrw-gate]'), function (el) {
    var g = (el.getAttribute('data-nbrw-gate') || '').split(':'), kind = g.length > 1 ? g[0] : 'calc', key = g.length > 1 ? g[1] : g[0];
    var msg = mk('div', 'nbrw-lockmsg'); msg.setAttribute('role', 'note'); imp(msg, 'display', 'none');
    el.parentNode.insertBefore(msg, el);
    return { el: el, kind: kind === 'code' ? 'code' : 'calc', key: key, msg: msg, lock: false, disp: el.style.getPropertyValue('display'), ch: chapOf(el) };
  });
  if (ownCover) buildCover();
  else if (cover.querySelector('.nbrw-cv-tl') && cover.querySelector('.nbrw-cv-tl').children.length) cover.querySelector('.nbrw-cv-tl').setAttribute('data-nbrw-py', '1');
  paint(); label(); fieldLabels();
  applyLang(lg, false);
  setMode(mode, false);
  ready = true;
  setView('cover');
  acCover(); acStart();
  try { if (D.body) new W.MutationObserver(function () { paint(); }).observe(D.body, { attributes: true, attributeFilter: ['class', 'style'] }); } catch (e) {}
  // E33 B1a: after a run, the window to the top of what one sees — where the host lets a frame scroll its page
  // (measured in the rebuilt hosts; JCEF/VS Code may ignore it: then nothing happens)
  W.setTimeout(function () {
    try { var r = wrap.getBoundingClientRect(); if (r.top < -2 || r.top > 8 || W.frameElement) wrap.scrollIntoView({ block: 'start', inline: 'nearest' }); } catch (e) {}
  }, 250);
  try {
    var mq = W.matchMedia('(prefers-color-scheme: dark)');
    (mq.addEventListener ? mq.addEventListener.bind(mq, 'change') : mq.addListener.bind(mq))(function () { paint(); });
  } catch (e) {}
  var redo = null;
  // E38a J1: lesen.html — the window fills the viewport (its top on the page + the frame's edge = the rest).
  // A viewport under HMIN is a frame that grows with its content (an IDE's output, js_e36 L5): there the rule of
  // the screen gives the start, the frame follows it, and the next pass fills that frame — a fixed point. Never
  // taller than the screen (a host that adds to the content's height on every pass stops there).
  function hFit() {
    if (!HULL) return false;
    var ih = W.innerHeight || D.documentElement.clientHeight || 0, sh = 0;
    if (!ih || !wrap.parentNode) return false;
    try { sh = (W.screen && (W.screen.availHeight || W.screen.height)) || 0; } catch (e) {}
    var y = wrap.getBoundingClientRect().top + (W.pageYOffset || D.documentElement.scrollTop || 0),
        edge = Math.max(0, Math.min(40, wrap.offsetHeight - win.offsetHeight)),
        n = ih < HMIN ? H0 : Math.floor(ih - y - edge);
    n = Math.max(HMIN, Math.min(HMAX, n, sh > 0 ? sh : HMAX));
    if (n === h) return false;
    h = n; wrap.style.setProperty('--nbrw-h', h + 'px');
    return true;
  }
  if (HULL) {
    hFit();
    W.addEventListener('resize', function () { if (ready) keep(hFit); else hFit(); });
  }
  function later() { layT = now(); if (redo) return; redo = W.setTimeout(function () { redo = null; place(); drawMarks(); if (view === 'cover') tlLay(); }, 120); }
  try { new W.ResizeObserver(later).observe(root); new W.ResizeObserver(later).observe(track); new W.ResizeObserver(later).observe(wrap); } catch (e) { W.addEventListener('resize', later); }
  // E30: the pinned heading stays on the reading height through every change of size (after layout, before paint)
  try { new W.ResizeObserver(function () { layT = now(); if (pin) { pinFix(); pos(); } }).observe(doc); } catch (e) {}
  W.addEventListener('resize', later);

  // our widgets drawn after all (a front end that draws them late): the live document takes over
  function back() {
    if (!wrap.parentNode || !hosted()) return;
    padT.remove(); padB.remove();
    while (doc.firstChild) root.insertBefore(doc.firstChild, doc);
    doc.remove();
    if (ownCover) cover.remove(); else imp(cover, 'display', 'none');
    gates.forEach(function (g) { g.msg.remove(); });
    wrap.parentNode.insertBefore(root, wrap); wrap.remove(); st.remove();
    root.removeAttribute('data-nbrw');
  }
  [1500, 4000].forEach(function (t) { W.setTimeout(back, t); });
  var api = { v: V, id: ID, root: root, win: win, jump: jump, view: function () { return view; }, show: setView, mode: function () { return mode; },
              lang: function () { return lg; }, height: function () { return h; }, zoom: function () { return Z[zi]; },
              // E30 (tests): the reading height in the window, the pinned entry, the shown language, the text size
              line: function () { return rlNow(); }, pinned: function () { return pin ? ents.indexOf(pin.e) : -1; },
              shown: function () { return eff(); }, fs: function (v) { return v === undefined ? fsLv() : fsSet(v); },
              // E31: the controls' size, the panel's width, the marker's mark
              gs: function (v) { return v === undefined ? gsLv() : gsSet(v); }, pw: function (v) { if (v !== undefined) keep(function () { setPw(v); }); return pan.offsetWidth; },
              here: function () { return here ? ents.indexOf(here) : -1; },
              // E33: the standard height (B1b), the drawer (B6), the account (B3), the panel's factor (B5), the wheel's
              // last acceleration (B4)
              h0: H0, drawer: function (k) { if (k !== undefined) drawer(k); return drwKind; },
              acct: function () { var a = acGet(); return a ? { id: a.id, name: a.name || '', on: !!a.on } : null; },
              ks: function () { return ks; }, acc: function () { return hand.a || 1; } };
  try { (W.__nbReaders = W.__nbReaders || {})[ID] = api; } catch (e) {}
  W.__nbReader = api;          // the last one started (tests of a single notebook); per notebook: __nbReaders[id]
})();
