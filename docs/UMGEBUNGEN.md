# Umgebungen — was wo geht, und wie man es prüft

*Angelegt 05.10. von der Werkstatt Python (E22.3). JS ergänzt Erkennung und Play, CSS das Rückfall-Aussehen. Was hier
„nicht gemessen“ heißt, ist nicht gemessen — der Container hat weder PyCharm noch ein Google-Konto.*

## Gefährliche Knöpfe und Einstellungen (E23.0, Werkstatt Python, 06.10.)

Das Notebook hat genau zwei Zellen: die Titelzelle (Markdown, Deckblatt) und die versteckte Mega-Zelle, deren **Ausgabe**
das ganze Dokument ist. Beide Zellen tragen `deletable: false`, `editable: false`; die Mega-Zelle dazu
`jupyter.source_hidden`, Colab `cellView: form` + `#@title`. **Kein Zustand lebt nur in der Ausgabe:** Fortschritt, Modus,
Sprache, Seed liegen im Browser (`localStorage`) bzw. in `~/.digichemjn` (JupyterLite: `.digichemjn` im Browser-Laufwerk).
Jeder Schaden an der Ausgabe ist deshalb **ein Klick ▶ Play / Run All** — nichts geht verloren (gemessen für „Clear Outputs“, s. u.).

Was der Leser sieht, wenn die Ausgabe fehlt (py-E23.0):
- **Erste Zeile der Mega-Zelle** (sichtbar in JupyterLab, Notebook 7, Lite, VS Code als eingeklappte Zelle; in Colab als
  Formular-Titel): „DigiChemJN · No document? ▶ Play / Run All draws it · Kein Dokument? ▶ Play / Run All zeigt es an“.
- **Deckblatt** (vor dem ersten Lauf, oder geöffnet ohne gespeicherte Ausgabe): ein gestrichelter Kasten unter Play, en + de:
  „Nur dieses Deckblatt und kein Dokument darunter? … Drücken Sie ▶ Play oder Run ▸ Run All Cells …“ (`.nbcover-gone`).
- *Offen (JS/CSS E23.16a/c):* nach „Clear Outputs“ im laufenden Lab bleibt die Titelzelle ausgeblendet (`.nbtitle-cell`,
  06-marks), sichtbar ist dann nur die erste Zeile. Das Deckblatt zurückholen, wenn `.nbfeed` fehlt, ist JS/CSS.

| Umgebung | Knopf / Einstellung | was passiert | rückgängig | gemessen? |
|---|---|---|---|---|
| JupyterLab 4.6 | *Edit ▸ Delete Cells*, `D D`, `X` (Ausschneiden) | nichts: Zelle ist nicht löschbar (2 → 2 Zellen) | – | ja (Delete, `D D`: py_e23_0, Matrix; `X`: Probe) |
| JupyterLab 4.6 | `M` / `Y` (Zelltyp ändern) | Dialog „Cell is read-only, its type cannot be changed!“, nichts ändert sich | OK klicken | ja |
| JupyterLab 4.6 | `Shift+M` (Zellen zusammenführen), `Enter` (bearbeiten) | nichts | – | ja |
| JupyterLab 4.6 | *Edit ▸ Clear Outputs of All Cells* | Dokument und Zeitleiste weg, sichtbar nur die erste Zeile (s. o.) | ▶ Play bzw. *Run ▸ Run All Cells*: Dokument zurück, Fortschritt, Modus, Sprache gleich (gemessen: a[1, 9] c[0, 7] s[1, 0, 0] → gleich) | ja |
| JupyterLab 4.6 | *Kernel ▸ Restart Kernel and Clear Outputs of All Cells* | vermutlich wie „Clear Outputs“ | ▶ Play / Run All | nein |
| JupyterLab 4.6 | *View ▸ Collapse All Outputs* (bzw. Klick auf den blauen Balken links der Ausgabe) | Dokument zugeklappt, nur ein Platzhalter | *View ▸ Expand All Outputs* oder Klick auf den Platzhalter | ja |
| JupyterLab 4.6 | *Kernel ▸ Restart Kernel* (ohne Run All) | Dokument bleibt stehen, reagiert aber vermutlich nicht mehr (Widgets ohne Kernel) | ▶ Play / Run All | nein (Dialog nicht bestätigt) |
| JupyterLab 4.6 | Datei ohne Ausgaben gespeichert/weitergegeben | beim nächsten Öffnen nur Deckblatt + erste Zeile | ▶ Play / Run All | nein |
| JupyterLab 4.6 | *Expand All Code* / Klick auf „•••“ der Mega-Zelle | zeigt den Quelltext (harmlos, aber lang) | *Collapse All Code* | teilweise (Expand All Code zeigte nichts Neues) |
| Notebook 7 | wie JupyterLab (gleiche Oberfläche, gleiche Befehle) | wie oben | wie oben | nein |
| JupyterLite | wie JupyterLab; dazu: Browserdaten löschen / privates Fenster | Notebook-Änderungen, Fortschritt, Modus, Seed weg (alles liegt im Browser) | nicht rückgängig; Konto-Code vorher sichern (👤) | nein |
| Colab | *Edit ▸ Clear all outputs* | Dokument weg, sichtbar der Formular-Titel (erste Zeile) | ▶ / *Runtime ▸ Run all* | nein |
| Colab | *Runtime ▸ Disconnect and delete runtime* | `~/.digichemjn` (Modus, Seed, Sprache des Kernels) weg; Fortschritt im Browser bleibt (nicht gemessen) | Modus/Sprache neu wählen, Run all | nein |
| Colab | *Edit ▸ Notebook settings ▸ Omit code cell output when saving* | gespeicherte Kopie ohne Dokument | Run all | nein |
| Colab | *Show code* am Formular | zeigt den Quelltext | *Hide code* | nein |
| Colab | Zelle löschen (Papierkorb) | ob Colab `deletable: false` beachtet, ist **nicht gemessen** | *Edit ▸ Undo* | nein |
| VS Code | *Clear All Outputs* (Leiste oben) | Dokument weg, sichtbar die erste Zeile | *Run All* | nein |
| VS Code | Zelle löschen / bearbeiten | ob VS Code `deletable`/`editable` beachtet, ist **nicht gemessen** | Strg+Z | nein |
| VS Code | Einstellung `notebook.output.scrolling` / Textlimit | lange Ausgabe in einem Scrollkasten oder abgeschnitten | Einstellung zurück | nein |
| PyCharm | *Clear Outputs* | feste Kopie weg | *Run All* | nein |
| Binder | lange ohne Aktivität, Tab zu | Sitzung und Dateien weg; Fortschritt im Browser hängt an der Binder-Adresse (nicht gemessen) | neu starten; Konto-Code sichern | nein |

*Die Liste „gefährliche Knöpfe“ aus der Chronik 06.10. (Dirigent), auf die STOP E23.0 verweist, lag beim Schreiben
(06.10. 00:3x UTC) nicht im Projekt; diese Tabelle ist aus Messung (Lab) und Kenntnis der Oberflächen. Dirigent: bitte abgleichen.*

## PyCharm / DataSpell

**Befund (Video 1, E22):** Play tut nichts; nach manuellem Lauf steht die Ausgabe als roher HTML-Text da.

**Ursache, gemessen an dem, was PyCharm bekommt** (Kernel mit `PYCHARM_HOSTED=1`, alle iopub-Nachrichten, v1.62/v1.63):
das ganze Dokument sind ipywidgets. 7 Widget-Ausgaben tragen nur `application/vnd.jupyter.widget-view+json` und `text/plain`;
der `text/plain` eines Widgets ist sein `repr` — `Accordion(children=(VBox(children=(HTML(value='<div class="nbtitle …` —
das ist der rohe HTML-Text. Dazu 7 Ausgaben `<IPython.core.display.Javascript object>`. Ein Front-End, das keine Widgets
zeichnet, zeigt genau das.

**Rückfall (py-E22.3):** erkennt der Kernel PyCharm (`PYCHARM_HOSTED`, `TERMINAL_EMULATOR` mit „JetBrains“), trägt jede
Widget-Ausgabe zusätzlich `text/html`: eine **feste Kopie** des Dokuments (Text, Formeln, Abbildungen; Akkordeons als
`<details>`, Knöpfe und Felder sichtbar, aber ohne Wirkung), oben eine Zeile, was fehlt und wo es geht. `text/plain` ist
leer, ebenso bei den Javascript-Ausgaben. In JupyterLab, Lite, Colab, VS Code kommt nichts dazu (geprüft: 0 zusätzliche
`text/html` ohne die Variable). Größe der Ausgaben in PyCharm: ~1,05 MB statt ~0,59 MB.

**Play (js-E22.3):** Play auf dem Cover ist ein Knopf in der Markdown-Titelzelle; was ihn wirken lässt, ist unser Skript —
und das läuft erst, wenn eine Ausgabe der Mega-Zelle es ausführt. **Vor dem ersten Lauf kann Play in PyCharm deshalb nichts
tun** (kein Skript von uns auf der Seite; das sagt der Cover-Text, Python). Läuft unser Skript in einer Ausgabe von PyCharm,
VS Code oder Colab (Kernel-Wort `data-nbenv`), startet Play **nichts**, zeigt keine Ladeansicht und nennt sofort den Weg:
„In PyCharm this button cannot start the notebook. Do this instead: restart the kernel, then “Run All” (▶▶) above the
notebook.“ (deutsch: „… kann dieser Knopf das Notebook nicht starten. So geht es: …“). Ein Tastenkürzel nennt der Text nicht —
PyCharms Belegung ist hier nicht gemessen. Automatisch geprüft (mit gesetztem Kernel-Wort, im echten Lab): `js_e22` J22.3.

**Prüfschritt mit dem Nutzer (PC):**
1. Notebook in PyCharm öffnen, Kernel starten, *Run All* (Play auf dem Cover braucht JS — siehe oben).
2. Erwartet: statt `Accordion(children=…` die Zeile „Dieses Fenster zeigt keine Jupyter-Widgets …“ bzw. „This window does
   not draw Jupyter widgets …“ und darunter das Dokument als lesbarer Text mit Abbildungen; kein `<IPython.core.display…>`.
3. Wenn PyCharm doch Widgets zeichnet: dann muss das interaktive Dokument erscheinen (Widgets haben Vorrang). Bitte Bild.
4. Nach dem Lauf Play auf dem Cover anklicken: erwartet die Zeile „In PyCharm this button cannot start the notebook …“ unter
   dem Knopf und **kein** Neustart. Bleibt alles still, läuft unser Skript in PyCharms Ausgabe nicht (dann bitte Bild + ob
   `application/javascript`-Ausgaben dort laufen).
5. Offen, nur dort messbar: wirkt die `<style>`-Ausgabe (287 KB) auf die anderen Ausgaben, oder steht jede Ausgabe in einem
   eigenen Rahmen? Laufen `application/javascript`-Ausgaben? Gibt es eine Größengrenze für eine Ausgabe?

Automatisch geprüft in `test_regress` Stufe 2: `tests/regress/py_e22p.py` (Kernel-Nachrichten + feste Kopie in Chromium).

## VS Code (code-server) — gemessen E32 K2, Werkstatt Python, 13.10. ~03 UTC, Vorlage v1.78

*Messung: `tests/env_vscode.py` (kein Tor-Skript, braucht `DIGICHEM_CODE_SERVER`), code-server 4.104.3 = VS Code 1.104.3,
Chromium 141 (Playwright), 1400 × 900. Bilder `E32-K2-vscode-*.png` (SendUserFile 13.10.).*

**Woran es scheitert (ehrlich):** die **Jupyter-Erweiterung lässt sich hier nicht installieren** — `open-vsx.org` und der
Marketplace sind vom Container-Proxy gesperrt (403 auf CONNECT); `ms-python.python`/`ms-toolsai.jupyter` „not found“.
Selbst bauen aus den Quellen (`microsoft/vscode-jupyter` v2025.8.0, git ging) wurde in diesem unbeaufsichtigten Lauf nicht
freigegeben. Folge: **kein Kernel in VS Code, keine Widgets** → Schicht B (Widgets gezeichnet) ist **nicht gemessen**.
Gemessen ist, was VS Code **ohne** Erweiterung mit den **gespeicherten Ausgaben** macht (Datei vorher per nbconvert
ausgeführt — dieselben Ausgaben, die ein eigener Run All liefert; Zeichnen übernimmt VS Codes eingebauter Renderer, alle
Ausgaben in **einem** Webview-iframe, jede in eigenem Container).

| Punkt | Ergebnis (hell · dunkel · VS Code dunkel + OS hell) |
|---|---|
| Run All (Datei wie gebaut) | Knopf da; VS Code fragt „Select Kernel → Install/Enable suggested extensions Python + Jupyter“ — ohne Erweiterung läuft nichts |
| Startzeile (Markdown) | gerendert, fett, en + de wie gewollt; **Breadcrumb/Outline zeigen sie roh** („`&#9654;&ensp;Run the cell below …`“) — Entities statt Zeichen (Python, Titelzelle) |
| Codezelle | **ganz offen** (VS Code ignoriert `source_hidden`): 23 Zeilen, Komprimat eine Zeile, `#@title` als erste Zeile |
| welche Schicht | **Lesefenster (C)**: 1 Lesefassung, 1 Fenster `.nbrw`, 0 Widget-Ansichten, 0 `.acc-root`, 0 Lab-Werkzeuge, 0 rohe `Accordion(…)`-Texte, 1 Titelkarte — in allen drei Läufen |
| Zeit bis Fenster | 12,5–13,0 s nach Quick Open (inkl. Laden der Oberfläche); nbconvert-Lauf der Vorlage 6,1 s |
| Vorschau | Fenster 600 px; **▶ Play liegt unter dem ersten Fensterbild** (Play-Unterkante 648 px > 600) — man muss im Fenster erst scrollen |
| Play (Maus) | → Dokument (`data-nbrw-view=doc`), Panel sichtbar — in allen drei Läufen |
| Mausrad | über dem Fenster scrollt **das Fenster** (0 → 1500 px), der Editor bewegt sich 0 px; am Fensterende geht das Rad an den Editor weiter (wie gewollt) |
| hell/dunkel | Fenster folgt **`prefers-color-scheme` des OS, nicht dem VS-Code-Thema**: VS Code dunkel + OS hell → weißes Fenster auf `#1f1f1f`. VS Code meldet sein Thema im Webview (`body.vscode-dark`, `--vscode-editor-background`) — nutzbar (JS/CSS) |
| unter dem Fenster | ~7 leere „…“-Zeilen (VS Codes Platzhalter für Ausgaben ohne sichtbaren Inhalt: Javascript-/Widget-Ausgaben mit leerem `text/plain`) |
| Konsole | 0 Fehler von uns; 2 × 404 `vsda` sind code-server-intern |

**Nach K1 noch einmal:** nicht nötig — JS meldet (Chronik 13.10. 02:4x), dass K1 schon in v1.78 steckt (E31 W1, Lab-Weg nur bei
echtem Lab-DOM, Fenster fest 600 px); `PATCH-js-E32` ändert `toolkit/js` nicht. Die Messung oben **ist** der K1-Stand.
**Für eine echte Schicht-B-Messung** braucht es die Jupyter-Erweiterung: entweder Netz zu open-vsx.org freigeben, oder die
`.vsix` (ms-toolsai.jupyter + ms-python.python, passend zu VS Code 1.104) ins Projekt/Container legen.

## Netzanfragen (E32 K3, `tests/regress/env_offline_requests.py`, Vorlage v1.78)

Lab (Run All + Play, dann 10 s): 144 Anfragen, **0 an fremde Hosts** · Lesefenster (PyCharm-Nachbau, 10 s Vorschau, Play,
10 s Dokument, kein ▶): **0 fremde**, Pyodide 0× angefragt. Zähler-Selbsttest (fremdes `<img>`) je Zeile gesehen. Im Quelltext
steht als einzige fremde Adresse `cdn.jsdelivr.net` (Pyodide, nur nach Klick auf ▶); `www.w3.org` sind SVG-Namensräume.

## Colab · Notebook 7 · Binder

Noch nicht eingetragen (E19.4: Erkennung `data-nbenv`, Metadaten `cellView: form` + `#@title`). Colab: E32 K1 (JS).
Gefährliche Knöpfe: Tabelle oben.
