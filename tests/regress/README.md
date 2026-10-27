# tests/regress — was der Nutzer schon abgenommen hat (E21.0)

**Pflicht ab E21:** jede Werkstatt vor dem Abliefern, die Hauptwerkstatt nach **jedem** Zusammenführen und vor **jedem**
Zurückschreiben. Ein roter Test = kein Zurückschreiben, der Patch geht an die Werkstatt zurück.

    python3 tests/regress/run.py complex/Complex_Numbers_Step_by_Step_v<X>.ipynb modeling/Introduction_to_Modeling_v<X>.ipynb
    #   --quick                minimal · hell · frisch (zum Entwickeln, nicht als Tor)
    #   --only "B1"            nur Tests, deren Name das enthält
    #   --lite-url URL         Lite-Zeilen gegen eine gebaute Lite-Seite (sonst NOT RUN = rot)
    #   --json out.json        Tabelle für die Chronik
    #   --scripts none|all|a.py,b.py   Stufe 2: die eigenständigen lab_*.py aus scripts.txt (Vorgabe all)
Exit 0 = `REGRESS OK`. Das Tor ist die volle Matrix mit Stufe 2 (ohne Schalter).

**Stufe 2:** `scripts.txt` listet die Messskripte der Werkstätten (`lab_yoc`, `lab_seed`, `lab_flow` …), die seit E12 nicht
mehr vor dem Ausliefern liefen (Befund Dirigent). Je Notebook ein Lauf auf demselben Server, Exit 0 = grün. Wer ein Skript
besitzt, hält seine Zeile aktuell (Argumente mit `{nb}`, `{out}`).

**Matrix:** Notebook × Umgebung (lab; lite mit `--lite-url`) × Stil (minimal, cyber) × hell/dunkel × Speicher (frisch, alt, **pair**).
„pair“ = das andere Notebook der Befehlszeile wird im selben JupyterLab-Fenster zuerst geöffnet und gelaufen, das geprüfte
steht als zweites vorn (so arbeitet der Nutzer: Complex und Modeling offen). Braucht zwei Notebooks auf der Befehlszeile.
Ein eigener JupyterLab-Server mit eigenem HOME je Lauf; je Zeile ein **eigener** Browser-Kontext, alle Kernel beendet,
`~/.digichemjn` geleert, eine frische Kopie des Notebooks, Run All. Dunkel wird wie beim Leser gesetzt: im JupyterLab-Theme (seit E15.3 ist das
die Wahl). „alt“ = `fixtures/storage_old.json` vor dem Laden eingespielt (gebrauchter Browser, Schlüssel wie vor
E15.7/E16.10). Eine echte Kopie aus dem Browser des Nutzers ersetzt die Datei 1 : 1.

**Ein Testmodul** = `tests/regress/<werkstatt>_e<n>.py` mit

    TESTS = [("B1 title mark folds", fn), …]        # fn(pg, ctx) -> (ok: bool, detail: str)

`pg` = Playwright-Seite nach Run All, `ctx` = {nb, id, env, skin, theme, storage, errs}. Ein Modul ohne `TESTS` wird
nicht importiert (eigenständige Skripte bleiben, was sie sind). Reihenfolge: `hw_` zuerst, dann nach Namen; Tests,
die das Notebook verändern (Zelle anlegen, Modus wechseln), stehen am Ende ihres Moduls.

**Regeln für einen Test**

1. Messen im Browser (`getBoundingClientRect`, `getComputedStyle`, DOM) — nie das eigene Markup lesen.
2. Kommt ein Test nicht an seine Vorbedingung, gibt er `False, "BAD …"` zurück — **nie** `True`. Ein übersprungener
   Test ist der Weg, auf dem eine Suite wegen des Fehlers grün wird.
3. **Gegenprobe:** jeder Test läuft zuerst gegen die Version, in der der Nutzer den Fehler sah (v1.60/v1.61). Wo der
   Nutzer einen Fehler sieht, muss er dort **rot** sein — sonst prüft er das Falsche. Ergebnis in die Chronik.
4. Ein Test, der nach einer Änderung rot wird: zuerst fragen, **was er bisher behauptet hat**.

`hw_e21.py` (Hauptwerkstatt): B5 Panel ruht 3 s · Werkzeugfenster 10/10 (B4) · B1 Title (Marke, Karte) · B2 Code
färbt live · B3 YOC Hover-Box + Zelle · dazu je Zeile Seitenfehler = 0. Die Werkstätten schärfen oder ersetzen sie
(mit Satz „behauptete bisher …“).
