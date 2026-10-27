# Final-Kriterien — woran Complex als „final“ gemessen wird

*Dirigent, Stand 01.10. (E4–E13 eingearbeitet). Wo eine spätere Nutzerentscheidung einer älteren widerspricht, gilt die
spätere; die Quelle steht kursiv dabei. Gemessen wird im **echten JupyterLab unter Playwright**, 4 Stile × hell/dunkel wo
sichtbar, 1400 × 900 und 1920 × 1080, mit **Gegenprobe** gegen die Version vor der Änderung (muss dort rot sein, wo sich
etwas geändert hat).*

## Pakete 1–14

- **1:** `test_fuzz_code` inkl. `runs` grün; eigener Code, der `_unlock_next` ruft → Panel-Sperren = Dokument-Sperren nach ≤ 3 s.
- **2:** erste How-to-Zeile fehlt; Controls-Fenster nennt alle Tasten aus `KEYS` (gegen die tatsächliche Belegung geprüft); 📚-Fenster: kein „series“/„across every notebook“, jedes Textelement `scrollHeight ≤ clientHeight`, keine zwei Textboxen überlappen; jeder Chip hat sein Symbol; Titelmarke = Titelkarte ±2 px.
- **3:** Reset + „Yes“: Fortschritt 0, Seed/Stil/Schwierigkeit/andere Notebooks unverändert; „Cancel“: alles unverändert; ohne Rückfrage kein Reset (auch Tastatur).
- **4:** nach richtiger Antwort und nach Skip: Leuchtmarker und nächste offene Marke auf der Lesehöhe ±2 px nach der Sprungzeit; *nach Skip lässt sich die nächste Aufgabe aus der Timeline öffnen*. *Nach falscher Antwort **kein** Sprung (E8.3).*
- **5:** Klick auf jeden Pip im 📚-Fenster und im Panel → dieselbe Landung wie die Timeline-Marke (±2 px), *bei Panel 0 % und 100 %*; gesperrt → keine Landung.
- **6:** *(E11.1, E12.4)* YOC ist kein Akkordeon, im Dokument kein „＋ Your own cell“-Knopf. Hover über die YOC-Marke → Box „＋ Add your cell“ in Stilfarben; 5 Klicks → 5 neue Code-Zellen, jede auf der Lesehöhe ±2 px, Editor fokussiert; neue Zelle trägt Stilfläche/-schrift, hell und dunkel.
- **7:** Namen ≥ 4,5 : 1 am schlechtesten Punkt (`lab_contrast --overlay`); Tooltip-Farben = Stilfarben; Skipped-Symbol Mitte = Zeilenmitte ±1 px.
- **8:** jede Marke dreht beim Hover/Auswählen (Winkel ≠ 0), Zeichen darin 0° (`lab_marks`), retro dreht nicht; vier Aufgabenarten, vier verschiedene Formen.
- **9 (K3):** Pips unter/neben dem Namen ohne Überlappung; Kontrast Marker gegen jede XP-Füllung ≥ 3 : 1; Lasche/Knopf und Panel teilen Farbe/Rand; gesperrte Überschrift/Falte trägt Schloss + „LOCKED“, ≥ 4,5 : 1, *ohne Kasten (E4.1)*.
- **10:** *(E4.2, E11.3)* Mausrad gleitet, größter Frameschritt ≤ 20 px; Dokument-Pixel je Raste **sinken mit der Lupe** (Obergrenze < 150 % < 100 % < 60 %, Verhältnisse nennen; ganz reingezoomt deutlich langsamer); Lesehöhe bleibt.
- **11:** je Stil unterschiedliche `animation-*`/`transition-*`; nichts > 1,5 s; `prefers-reduced-motion` schaltet ab.
- **12/12b:** Sweep ≥ 200 Seeds × 3 Stufen: 0 nicht einstellbare Lösungen; gentle: jede Eingabe/jedes Ergebnis ganzzahlig/,5, k√2, Winkel aus π/4, π/6, 0 Ausnahmen; `test_answers` grün.
- **13:** neuer Seed → jede Aufgabenzahl ändert sich in ≤ 2 s ohne Run All; Checks nehmen neue Lösungen, lehnen alte ab; Fortschritt bleibt.
- **14:** vor Play: Cover-Unterkante ≥ Fensterunterkante, 0 sichtbare Codezeilen (`elementFromPoint`), 900 und 1080 px.

## E4–E13 (Kern)

- **Start/Reset (E4.3, E12.2):** Title ist der Spawnpunkt: nach Öffnen, Play/Run All und Reset steht die Titelmarke auf der Lesehöhe ±2 px, Marker auf Title; Ladeansicht hebt sich ohne sichtbaren Sprung (`scrollTop`-Verlauf ohne Umkehr).
- **Scrollbereich (E12.2, ersetzt E9.2):** ganz oben (auch weiter hochscrollen) Titelmarke − Lesehöhe 0 ±2 px, ganz unten YOC-Marke − Lesehöhe 0 ±2 px; keine Luft davor/danach; Lupe 60/100/150 %.
- **Lesehöhe (E9.1, E11.4, E11.5, E11.9):** Knopf, Marker und `.nbreadfix` auf einer Höhe ±1 px; Knopf senkrecht ziehen verschiebt alle drei und das Dokument gleich weit; Wert bleibt nach Neuladen; Lupen-Zoom hält den Dokumentpunkt auf der Lesehöhe ±2 px, auch nach Verschieben; keine gestrichelte Linie; Knopf zeigt dezent ↑↓.
- **Scrollbar (E12.3, ersetzt E9.1-Cursor/E11.6):** links in der Werkzeugspalte zwischen den Widgets, 0 Überlappung mit Knöpfen; Daumen-Anteil = Scroll-Anteil ±0,01 bei 0/¼/½/¾/1; Ziehen am Daumen scrollt proportional; Rinne und Daumen sichtbar (Daumen : Rinne ≥ 3 : 1).
- **Pfeil am Knopf (E12.1):** kippt an der Panelbreite, ab der der letzte Name unsichtbar ist, Δ ≤ 2 px, Lupe 60/100/150 %.
- **Marker und Spur (E11.8, E12.5):** Marker und Leuchten auf der Lesehöhe zentriert ±1 px; die Spur liegt **nur hinter** dem Marker (runter → darüber, Umkehr → darunter), gleich breit wie der Kopf, kein Keil, kein `clip-path`.
- **Zoom (E9.3, E9.4, E11.10):** bei Lupe 60/100/150 % und Obergrenze: jede Marke auf der Mitte ihrer Pille ±2 px, alle Panelgrößen (Symbole, Namen, Pips, Wörter, XP-Füllung) × Lupe ±5 %, 0 Überlappungen, 0 abgeschnittene Namen bei 100 %; Obergrenze = Inhalt füllt die Breite.
- **Akkordeons (E9.6, E11.1, E11.2):** Title zu klappt im Dokument alles außer YOC/eigenen Zellen **und** blendet in der Timeline alle Punkte darunter aus (sichtbar: Titelmarke, YOC, „Own cell n“); wieder auf → vorher offene Punkte offen; **kein doppelter Titel**.
- **Pips (E9.8):** Modus both: zwei Pips je Aufgabe nebeneinander.
- **Modus (E9.9, E8.7, E8.16):** ⚙-Wechsel wirkt beim nächsten Lauf bzw. „Rebuild now“; Kapitel bleiben in jedem Modus gesperrt bis zur Vorgängeraufgabe.
- **Fenster (E11.7, E11.12, ersetzt E9.10):** feste Größe (unabhängig von der Panelbreite), links mittig am Rand, Controls-Aussehen, eins zur Zeit; schließt per ×, Esc und Klick außerhalb; jedes Fenster öffnet 10/10 (auch 📚).
- **Cover (E8.21, E9.11, E12.6, E13):** eine Reihe, durchgehender Strahl ohne Lücken, Marken in natürlicher Größe (±1 px gegenüber 1920 px), folgt Modus und Profilstand; zu lang → Verlauf nur an der Seite mit weiteren Punkten + Scrollleiste darunter (Daumen-Länge = sichtbarer Anteil ±2 px, Title und YOC erreichbar); Startausschnitt zeigt den Profilstand; vor Play ebenso eine Reihe; 1024 × 768, 1400 × 900, 1920 × 1080.
- **Eigene Zellen (E9.13, E8.11):** Restore-Angebot nach neuer Version, Inhalt gleich; eigene Zelle per Marke ein-/ausklappbar.
- **Tasten (E9.14, E10):** keine JupyterLab-/Browser-Belegung überschrieben; K und ↑ im Befehlsmodus springen nicht über Title hinaus.
- **Fremde Notebooks (E8.23):** in einem zweiten Tab unverändert (Prompts, Collapser, keine `nb-*`-Klassen).
- **Retro (E10, E11.13):** hell = Leinen (B), dunkel = Bütten (A), Texturmaßstab wie die anderen Stile.
- **Größe/Tempo (21):** Mega-Zelle ≤ 700 000 B; Kernel-Lauf ≤ 3 s (nbclient, Median aus 3).
- **Suiten:** alle sechs grün, jede geänderte Zusicherung mit Satz „behauptete bisher …“ in der Chronik.
