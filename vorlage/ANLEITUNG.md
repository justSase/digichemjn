# Vorlage — Baukasten und Anleitung

Die Vorlage ist **das** Entwicklungs-Notebook (Dauerregel 12.10.: „nur die Vorlage“): jeder Baustein des Toolkits steht
hier mindestens einmal mit Platzhaltertext; was hier fehlt, gilt als ungeprüft. `tests/test_vorlage_cover.py` liest die
Tabellen unten und wird rot, wenn eine öffentliche Funktion des Toolkits in keiner Tabelle steht oder ein Baustein nicht
an der genannten Stelle aufgerufen wird. Bauen: `cd vorlage && python3 build_vorlage.py`. Prüfen: die Tor-Skripte nehmen
ohne Angabe die Vorlage (`--nb vorlage`; Complex nur auf Zuruf: `--nb complex`).

Kapitel: `k01`/`k02` = die Grundform (Idee + Formel · Abbildung mit Regler · Rechenaufgabe mit Hinweisen · Coding ·
Kernaussage). `k03`–`k05` = der Baukasten (alle weiteren Aufgabenformen, Kästen, Abbildungen).

## Neues Notebook aus der Vorlage

1. Ordner `vorlage/` kopieren, z. B. nach `bioinfo/`. `build_vorlage.py` umbenennen (`build_bioinfo.py`), darin
   `nbid-vorlage` → `nbid-bioinfo`, Ausgabename `"Vorlage_v"` → `"Bioinformatics_v"`, Titel/Untertitel/Leitsatz der Titelkarte.
2. `chapters/_setup.py`: `set_notebook("bioinfo", "Titel")`, `set_metadata(...)`, persönliche Zahlen in `_draw_tv`,
   Lernziele `register_goals`, Aufgaben `register_tasks` (je Kapitel eine: t1, t2, …), Literatur `BIB`.
3. Kapitel: die Kapitel behalten, die passen (Grundform `k01`), nicht gebrauchte Baukasten-Kapitel aus `CONTENT` nehmen,
   neue als `k06.py` … anlegen und in `build_*.py` unter `CONTENT` eintragen. Ab Kapitel 2: `locked_by="t<vorige>"` am
   Kapitel **und** am `code_fold` (sonst wartet die Coding-Kette nicht).
   **Lesefenster (PyCharm):** jede Rechenaufgabe bekommt `answer=lambda: {"feld": wert}` (oder `(wert, toleranz[, periode])`;
   Toleranz `None` = `tol()`), `choice_answer` den Index der richtigen Option, `target_exercise` je Regler `(wert, toleranz)`.
   Namen je Kapitel eindeutig (alles läuft in **einem** Namensraum: `_a` in k01, `_a2` in k02, `_phi4` in k04).
4. Texte auf **Englisch** im Quelltext; Deutsch in `chapters/de.txt` (Paare `en:`/`de:`, genau das Literal, Sie-Form).
5. Kartentexte der Vorschau: `chapters/cards.txt` (+ `cards.de.txt`); der Build nennt fehlende Schlüssel.
   **Vorschau zweisprachig (E29):** EN|DE schaltet jeden Text der Vorschau sofort um (`card_facts.cover_two`) — dafür
   braucht **jeder** Text der Titelkarte und der Zeitleiste (Untertitel, Leitsatz, Ziele, Kapitel-, Abbildungs- und
   Aufgabennamen) ein Paar in `de.txt` und jede Karte (auch `end`, `cell`) eine Zeile in `cards.de.txt`. Fehlt eines, bleibt
   dort Englisch stehen (Test: `tests/regress/py_e29.py`). Reihe des Notebooks: Eintrag in `toolkit/card_facts.py` `SERIES`.
6. Bauen: `cd bioinfo && python3 build_bioinfo.py` → meldet Karten, Deutsch-Einträge, Zeilen der kurzen Zelle, Größe.
Gemeinsames Aussehen/Verhalten kommt aus `toolkit/` — dort nichts für ein einzelnes Notebook ändern.

## Alle Notebooks bauen aus der Vorlage

Complex, Modeling, Start, Sets, ML werden nachgezogen, wenn der Nutzer sagt „Vorlage passt“:
1. `build_<nb>.py` = `build_vorlage.py` mit eigenem Titel, `nbid-…`, Ausgabenamen, `SETUP` und Kapitellisten
   (`FOUNDATIONAL`, `CONTENT`, `APPENDIX`, `PROGRESS`) — sonst **nichts** abweichen lassen (`diff` zeigt nur Namen).
2. `chapters/_setup_<nb>.py` aus `_setup.py`: Werte, Ziele, Aufgaben, Literatur, `set_time_rule` des Notebooks.
3. Inhaltskapitel bleiben die eigenen; Fundament (`controls`, `howto`, `teaches`, `roadmap`, `conclusion`, `refs`,
   `progress`) aus der Vorlage übernehmen und nur die Texte anpassen.
4. Prüfen: `python3 tests/test_vorlage_cover.py` (Spalte T3: was das Notebook nutzt, muss ein Baustein sein) und das Tor mit
   `--nb <nb>`.

## Neuen Baustein anlegen

1. **Funktion** in `toolkit/chapter_template.py` (öffentlich = ohne `_`; Markup → Python, Aussehen → `toolkit/css/`,
   Verhalten → `toolkit/js/`). Für das Lesefenster: Daten mit `_nbrw_reg(...)` anmelden wie `numeric_answer`.
2. **Platzhalter-Beispiel** in der Vorlage: in das passende Baukasten-Kapitel (`k03`–`k05`) oder ein neues `k06.py`
   (dann in `CONTENT`, `register_tasks`, `cards.txt`). Platzhaltertext, kurze Abbildung (Kernel-Lauf klein halten).
3. **Zeile** in die Tabelle „Bausteine“ unten: Name · Datei der Vorlage (zuerst) · wofür. Ist es kein Baustein (nur intern
   oder nur für den Leser), eine Zeile unter „Infrastruktur“.
4. `python3 tests/test_vorlage_cover.py` — findet die neue Funktion selbst: ohne Zeile rot (T1), ohne Aufruf an der
   genannten Stelle rot (T2).

## Bausteine (Kapitel)

| Baustein | Vorlage-Stelle | wofür |
|---|---|---|
| `build_chapter` | `k01.py` (alle Kapitel; `locked_by` ab `k02.py`) | setzt ein Kapitel zusammen: Kasten, Abbildung, Übung, Kernaussage, Sperre |
| `concept_box` | `k01.py`, mit Konstanten `k03.py` | Idee + Formel + Variablen (ein Kasten je Kapitel) |
| `info_box` | `k03.py` | ältere Formelkarte (bleibt für alte Kapitel) |
| `note_box` | `k03.py` (Kurzsatz `intro=`), `k05.py`, Fundament | Textkasten ohne Formel |
| `intro_box` | `k04.py` | kleine Karte ganz oben im Kapitel |
| `warn_box` | `k03.py` | roter Kasten: Grenze, Falle |
| `interpretation_box` | `k01.py`, mit Titel `k03.py` | Kernaussage unter dem Kapitel |
| `conclusion` | `conclusion.py` | Fazit als zusammenhängender Text wie in Publikationen: Zusammenfassung · Einordnung · Ausblick (Absätze, keine Liste) |
| `viz_intro_box` | `k01.py`, mit Tabelle `k03.py` | Beschreibung über der Abbildung |
| `exercise_box` | `k01.py` | Aufgabentext |
| `taskline` | `k01.py` | erste Zeile der Aufgabe |
| `formula_line` | `k04.py` | Formelzeile in einem Textkasten |
| `cite` | `k01.py`, `k03.py` (Quelle 2) | Quellenmarke → Literaturliste (`BIB` in `_setup.py`, `refs.py`) |
| `imath` | `k04.py` | Formel im Fließtext |
| `dmath` | `k05.py` | abgesetzte Formel |
| `math_img` | `k05.py` | Formel als Bild |
| `fnum` | `k03.py` | Zahl kurz für die Anzeige |
| `readout` | `k03.py` | Ablesezeile unter der Abbildung |
| `make_table` | `k03.py` | Tabelle (in `viz_intro_box`) |
| `highlight_code` | `k05.py` | gefärbter Code als HTML |
| `center` | `k05.py` | mittig auf der Hauptachse |
| `fixed_canvas` | `k01.py` | Abbildung mit fester Achsenbox |
| `theme_axes` | `k01.py` | Achsen im Notebook-Stil |
| `theme_legend` | `k03.py` | Legende im Notebook-Stil |
| `argand_axes` | `k04.py`, `k05.py` | Ebene mit Achsen durch den Ursprung |
| `fig_to_html` | `k04.py` | Abbildung → HTML (für `frame_player`) |
| `plot_html` | `k05.py` | feste Abbildung ohne Regler |
| `slider_plot` | `k01.py` (1 Regler), `k03.py` (2 + Menü), `k04.py` (3) | Abbildung mit Reglern; Lesefenster: vorberechnete Bilder |
| `frame_player` | `k04.py` | Schritte durch vorbereitete Bilder |
| `numeric_answer` | `k01.py`, Winkel mit Periode `k04.py` | Zahl eintippen, prüfen |
| `choice_answer` | `k03.py` | eine Option wählen |
| `target_exercise` | `k05.py` | Regler aufs Ziel stellen (Lesefenster: Felder) |
| `hint_steps` | `k01.py`, mit `forbid` `k04.py` | Hinweise Schritt für Schritt |
| `code_fold` | `k01.py`, `locked_by` ab `k02.py` | freiwilliges Coding (Lesefenster: Pyodide/`pruefe`) |
| `editable_exercise` | `k05.py` | Code-Feld mit Selbstprüfung (ohne Wertung) |
| `editable_runner` | `k05.py` | Code-Feld mit Ausgabe |
| `solution_box` | `k05.py` | Lösung hinter einem Knopf |
| `personal` | `k01.py` | Text mit persönlichen Zahlen (neu nach Seed) |
| `on_reseed` | `k01.py` | eigene Werte nach neuem Seed |
| `tol` | `k01.py` | Toleranz nach Schwierigkeit |

## Setup und Fundament

| Funktion | Vorlage-Stelle | wofür |
|---|---|---|
| `use_profile` | `_setup.py` | Fachstandard |
| `use_style` | `_setup.py` | Aussehen der Kästen |
| `set_notebook` | `_setup.py` | Kennung + Titel |
| `set_metadata` | `_setup.py` | OER-Datensatz |
| `inject_style` | `_setup.py` | Stylesheet einmal |
| `notebook_seed` | `_setup.py` | Seed des Laufs |
| `notebook_mode` | `_setup.py` | Modus des Laufs |
| `personal_draw` | `_setup.py` | persönliche Zahlen je Seed |
| `register_goals` | `_setup.py` | Lernziele |
| `register_tasks` | `_setup.py` | Aufgaben t1 … |
| `set_time_rule` | `_setup.py` | Minuten je Element |
| `notebook_start` | `_setup.py` | Titel auf der Zeitleiste |
| `title_card` | `build_vorlage.py` | Titelkarte im Dokument |
| `group_start` | `build_vorlage.py` | Gruppe beginnen (Einleitung, Inhalt, Anhang) |
| `group_end` | `build_vorlage.py` | Gruppe schließen |
| `notebook_end` | `build_vorlage.py` | Endkarte + letzter Balken |
| `lang_store` | `controls.py` | Sprache merken |
| `lang_page_js` | `controls.py` | Sprache an die Seite |
| `seed_store` | `controls.py` | Seed merken |
| `seed_forget` | `controls.py` | Seed vergessen |
| `reseed` | `controls.py` | neue Zahlen ohne Neulauf |
| `set_mode` | `controls.py` | Modus für den nächsten Lauf |
| `mode_page_js` | `controls.py` | Modus an die Seite |
| `set_difficulty` | `controls.py` | Schwierigkeit |
| `progress_code` | `controls.py` | Fortschritt als Code |
| `apply_progress_code` | `controls.py` | Code einspielen |
| `merge_progress_code` | `controls.py` | Code zusammenführen |
| `reset_progress` | `controls.py` | von vorn |
| `goals_table_html` | `teaches.py` | Lernziele als Tabelle |
| `metadata_box` | `refs.py` | OER-Datensatz im Anhang |
| `goal_strings` | `refs.py` | Ziele für den Datensatz |
| `time_budget_text` | `refs.py` | Zeitangabe |
| `on_notebook_built` | `refs.py` | Arbeit nach dem letzten Kapitel (Literaturliste) |
| `progress_panel` | `progress.py` | das Panel (zuletzt) |

## Infrastruktur (kein Baustein)

| Funktion | aufgerufen von | wofür |
|---|---|---|
| `pruefe` | Leser (Kopierzeile aus `code_fold`) | Coding im Lesefenster prüfen |
| `lang_stored` | Toolkit | gemerkte Sprache lesen |
| `notebook_lang` | Toolkit | Sprache des Laufs |
| `inject_jump` | Toolkit | Sprung-Skript |
| `loading_screen` | Toolkit | Ladebild |
| `nbrail_js` | Toolkit | Panel-Skript |
| `hints_seen` | Toolkit | geöffnete Hinweise |
| `kernel_env` | Toolkit | Umgebung erkennen (nur Wortlaut) |
| `seed_stored` | Toolkit | gemerkter Seed |
| `progress_store` | Toolkit | Fortschritt merken |
| `progress_stored` | Toolkit | gemerkter Fortschritt |
| `progress_forget` | Toolkit | Fortschritt vergessen |
| `mode_stored` | Toolkit | gemerkter Modus |
| `mode_store` | Toolkit | Modus merken |
| `mode_inbox` | Toolkit | Modus von der Seite |
| `builds_answer` | Toolkit | baut der Modus Rechenaufgaben? |
| `builds_code` | Toolkit | baut der Modus Coding? |
| `plain` | Toolkit | Modus „plain“? |
| `hints_on` | Toolkit | Hinweise erlaubt? |
| `structure` | Toolkit | Struktur lesen |
| `ornament_sprite` | Toolkit | Ornament-Vorrat |
| `ornament` | Toolkit (`notebook_end`) | ein Ornament |
| `progress_mirror` | Toolkit | Panel-Zwilling |
| `goals` | Toolkit | Lernziele lesen |
| `element_counts` | Toolkit | Elemente zählen |
| `time_budget` | Toolkit | Minuten rechnen |
| `card_chapters` | Toolkit/Build | Kapitel für die Titelkarte |
| `card_facts` | Toolkit/Build | Fakten der Titelkarte |
| `card_facts_html` | Toolkit/Build | Titelkarte als HTML |
| `card_timeline` | Toolkit/Build | Zeitleiste als Daten |
| `task_solved` | Toolkit (Aufgaben) | richtig (Rechnen) |
| `task_code_solved` | Toolkit (Aufgaben) | richtig (Code) |
| `task_code_skipped` | Toolkit (Aufgaben) | Code später |
| `task_code_bypassed` | Toolkit (Aufgaben) | Code aufgegeben |
| `task_wrong` | Toolkit (Aufgaben) | falsch eingegeben |
| `task_skipped` | Toolkit (Aufgaben) | später |
| `task_bypassed` | Toolkit (Aufgaben) | aufgegeben |
| `task_solution_opened` | Toolkit (Aufgaben) | Lösung geöffnet |
| `skip_button` | Toolkit (`build_chapter`, `code_fold`) | „Später“-Knopf |

## Ruhend

| Funktion | seit | wofür |
|---|---|---|
| `completion_button` | E25.l (MCQ/BYOD raus) | „durchgearbeitet“ für Kapitel ohne Prüfung |
| `run_all_button` | E24.3 (Erststart wie ein normales Notebook) | grüner „Alle Zellen“-Knopf |
