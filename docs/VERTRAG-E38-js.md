# VERTRAG E38 — was der Leser (20-reader.js) aus `daten.json` liest (angelegt: Werkstatt JS, 27.10. ~02:40 UTC; Python ergänzt/widerspricht hier)

Quelle im Leser: `window.DIGICHEMJN.daten` (lesen.html, Lader) **oder** `<script type="application/json" data-nbrw-daten>` in der Lesefassung
(Ausgabe ohne Lader, z. B. P3/IDE). Fehlt ein Feld, fehlt nur der Knopf — nie ein leerer. Alle Felder optional, nur ergänzt (VERTRAG-E36 bleibt).

**Text** = `"…"` | `{"en": …, "de": …}` | `{"gentle": …, "standard": …, "strict": …}` (verschachtelbar). HTML wie in der Lesefassung (vertraut, eigener Bau).

## J1 Aufgaben — `aufgaben[]` (Rechnen) und `code[]` (Programmieren), Schlüssel `task`
- `hinweise` (oder `hints`): Liste von Texten, Stufen in Reihenfolge (Labs `hint_steps`). Bei `strict` zeigt der Leser keine (Labs `hints_on()`).
- `loesung` (oder `solution`): Text, oder `{"intro": Text, "code": "<python>"}` (Labs `solution_box(intro, code)`); bei `code[]` darf es
  der reine Quelltext sein.
- Überspringen braucht keine Daten (jede Aufgabe mit `task`).
- Zustände wie Lab: Überspringen → `skipped` (+ weiter zur nächsten), Lösung Rechnen → `skipped`, Lösung Code → `wrong` (✗ aufgegeben).

## J2 Schwierigkeit — Toleranz wie Labs `tol()`
- `schwierigkeit`: `{"stufen": {"gentle": {"tol": 0.02}, "standard": {"tol": 0.005}, "strict": {"tol": 0.001}}, "gebaut": "standard"}`
  (fehlt es: Labs `_DIFF`). Ein Feld, dessen Toleranz = `stufen[gebaut].tol`, folgt der Stufe; eigene Toleranzen bleiben.
- optional je Aufgabe `toleranz`: `{"gentle": [je Feld], "standard": [...], "strict": [...]}` (gewinnt).
- `seed`: `{"value": n, "fixed": bool}` (gibt es schon) — wird angezeigt. `gating.order` (gibt es schon) = Reihenfolge des Fortschrittscodes
  (= Labs `_TASKS["order"]`; Code ist Labs `progress_code()`, Schlüssel `_CODE_KEY`).

## J3 Regler — `regler[nr]` (nr = Reihenfolge der `.nbrw-slider[data-z]`)
- `py`: `{"code": "<python, definiert fn und alles, was sie braucht (ohne Toolkit-Import)>", "fn": "<name>",
  "params": [{"name": "a", "min": 0, "max": 10, "step": 0.5, "value": 2.0}, …] (je Steuerung in Reihenfolge), "pkgs": ["numpy", "matplotlib"]}`.
- Der Leser ruft `fn(**kw)` → matplotlib-Figur → SVG (Pyodide, Agg). Nicht-numerische Steuerungen bleiben Stufen, ihr Wert = Label.
- Die Bilder in `data-z` bleiben die Vorschau (sofort); ohne `py` bleibt alles wie bisher.

## Python (27.10. ~05 Berlin, `PATCH-py-P2/P3/P4-390392ba`) — bestätigt, geliefert, ein Widerspruch
- **J1 bestätigt.** `hinweise` = `{"en": [...], "de": [...]}` (j1Pick löst es), `loesung` = `{"intro": {en,de}, "code": {en,de}, "warn": {en,de}}` | null
  (`warn` = Labs Satz unter dem Knopf). Zusätzlich je Aufgabe `ueberspringen` (bool), oben `texte{en|de: {skip{answer|code: {skip,fail,done}}, solution}}`
  (Labs Sätze) und `regeln{answer|code}` (Kette, wartet_auf, öffnet bei solved/wrong/skipped, Lösung zählt als skipped bzw. wrong). Alles aus denselben
  Aufrufen wie die Lab-Knöpfe (`_nbrw_daten`), geprüft durch Drücken der Lab-Knöpfe im Kernel (`py_e38_p2`). Die Vorlage hat jetzt deutsche Hinweise
  (`vorlage/chapters/de.txt`) — vorher auch im deutschen Lab englisch (J1f misst „einsetzen“: jetzt echt).
- **J2 bestätigt.** `schwierigkeit.gebaut` da; `toleranz{stufe: [je Feld]}` in der Reihenfolge von `data-a`; dazu `toleranz_felder [[feld, "stufe"|"eigen"]]`.
  Gemessen gegen Labs Prüf-Funktionen je Stufe (± 0,9/1,1 · tol).
- **J3 Widerspruch, abwärtsgleich gelöst.** Ein `fn(**kw)` → Figur → `savefig(svg)` ist NICHT das Bild der Vorschau: ohne `fig_to_html` fehlen die
  Farben als CSS-Variablen (hell/dunkel, Stil), die Schrift-Variable, die px-Größe und die Readout-Zeile (k03). Darum liegt das Programm unter
  `regler[nr].live` (kein `py`; der Leser nimmt `r.py || r.live`) = `{code, fn: "_nbrw_r", params, pkgs, html: "_nbrw_render", spec, start, dpi}`, und
  `code` definiert `_nbrw_svg(_f, _kw)` neu (läuft nach J3SVG): es gibt das `<svg>` des Toolkit-Bildes — Zeichen für Zeichen = `data-z` für die Werte des
  Baus (`py_e38_p4` L1s), Menü-Beschriftung → Wert. **Bitte JS:** künftig `html` aufrufen (fertiges HTML wie ein data-z-Bild, mit Readout-Zeile) statt
  `_nbrw_svg`. Gemessen: volle Pyodide 0.27.7 (numpy 2.0, matplotlib 3.8.4, lokal unter `/pyodide/0.27.7/`) zeichnet das Startbild pixelgleich zu `data-z`
  (0 px > 40), erstes Bild ≈ 5 s nach Start (Pyodide 2 s, Pakete 1 s, erstes Bild 2,2 s), danach ≈ 60–80 ms je Bild.
- `nr` in daten.json = Reihenfolge ALLER `.nbrw-slider`; ohne `data-z` (Zeitbudget) weicht sie von „mit data-z“ ab — im Bau ist das Budget aus
  (alle haben `data-z`), also gleich.
- **P3:** in der .ipynb steht `script[type=application/json][data-nbrw-daten='<id>']` als erstes Kind von `.nbreading` (= daten.json). Der Leser startet in
  JupyterLab/NB7 nicht (`hosted()`) — P3 setzt die Ausgabe dort in `iframe[data-digichemjn-rahmen]` (srcdoc, gleicher Ursprung, eigene Seite, wie VS Code/
  PyCharm). **Für JS:** startet der Leser neben einer Paket-Ausgabe selbst (z. B. Marke `.nbreading[data-nbrw-paket]`), fällt der Rahmen weg.
