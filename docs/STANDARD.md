# Der Standard — Complex Numbers v1.1

**Ab sofort ist `Complex_Numbers_Step_by_Step_v1.1.ipynb` das Vorbild für jedes
neue Notebook.** Wer ein neues baut, kopiert `complex/` und tauscht den Inhalt —
er erfindet die Form nicht neu.

Alles hier ist am fertigen Notebook **gemessen**, nicht aus dem Gedächtnis
geschrieben. Kategorien: Struktur und Inhalt (→ `notebooks/KATEGORIEN.md`).

---

## Stand 06.10.: Aufbau einer Notebook-Datei

*Entscheidung Nutzer 06.10. (E24.3, `plan/STOP.md`); Reihenfolge `plan/ZIELPLAN.md` Stufe 2–3.*

- **Zelle 1 (Markdown):** eine Textzeile — „▶ Führen Sie die Zelle darunter aus / Run the cell below“.
  Kein Cover, kein Play-Knopf, keine Timeline vor dem Lauf; das alte Vor-Play-Cover in der Titelzelle entfällt.
- **Zelle 2 (Code), eine sichtbare Zeile:**
  - Lite-Seite: `import digichemjn; digichemjn.show("<id>")` (Toolkit als vorinstalliertes Paket).
  - Download-Datei: erste Zeile Kommentar/`#@title`, darunter `%pip`-Bootstrap für fehlende Pakete und das
    komprimierte Toolkit, zugeklappt.
- **Ausgabe:** erst die Vorschau (bisheriges Cover) mit Play/Modus/Sprache/Login, dann das Dokument.
- **Grund:** auf fremden Geräten läuft vor dem ersten Ausführen kein JS (Trust-Modell).
- **Kernel-Metadaten:** Standard `python3` / `language_info python`.

Die Abschnitte unten sind **überholt, soweit oben anders**.

---

## 1. Das Maß

| | Complex Numbers v1.1 |
|---|---|
| Zellen | 2 |
| Kapitel | 7 |
| Unterabschnitte (Intro + Appendix) | 10 |
| Aufgaben | 9 (`t1`–`t7`, `q1` Quiz, `b1` eigene Daten) |
| Sperren | 6 Kapitel · 6 Aufgaben · 6 Coding |
| Quellen (`BIB`) | 7 |
| Schlagwörter | 9 |
| Dauer laut Metadaten | 90–120 Minuten |

**Jedes** Kapitel hat alle drei Teile: Visualisierung, Aufgabe, Coding-Aufgabe.
Keine Ausnahme — 7 von 7. Das ist der Teil des Standards, der am leichtesten
verwässert und am meisten trägt.

Fünf bis acht Kapitel sind der Korridor. Weniger heißt, der Abschnitt gehört
zu einem anderen; mehr heißt, er zerfällt in zwei Notebooks.

---

## 2. Der Aufbau einer Datei

```
build_<name>.py
chapters/
  _setup_<kürzel>.py   Profil · Stil · Metadaten · Seed · Aufgabenregister · BIB
  setup.py             👋 „Setup and how the numbers are drawn"
  howto.py             👋 „How to use this notebook"
  teaches.py           👋 „What you will be able to do"   (die Lernziele)
  roadmap.py           👋 „The route through this notebook"
  c01.py … c0N.py      📚 die Kapitel
  summary.py           📑 „Summary"
  glossary.py          📑 „Glossary"
  remarks.py           📑 „Remarks and limits"
  refs.py              📑 „References and licence"
  quiz.py              📑 „Multiple choice quiz"            (q1)
  byod.py              📑 „Bring your own data: …"          (b1)
  progress.py          das Panel, immer zuletzt
```

Die Reihenfolge in `build_*.py` ist bindend: `refs.py` steht **vor** Quiz und
BYOD, weil seine Liste von einem Finalizer geschrieben wird, und die beiden
Abschnitte, in denen der Leser etwas *tut*, sollen am Ende der Timeline stehen.

---

## 3. Der Bauplan eines Kapitels

Ein Kapitel ist eine Datei und endet mit genau einem `build_chapter(...)`:

```python
_intro = "Ein Absatz: was dieses Kapitel behauptet" + cite(1) + " …"

info = concept_box(_intro,
    r"$…$",                                  # die Formel
    variables=[("x", "was x ist"), …],       # jedes Symbol benannt
    extra_html="…")                          # die Herleitung in Prosa

viz  = [viz_intro_box("", "Was man hier sehen soll …")]
viz += slider_plot(_render, {"p": FloatSlider(...)}, readout_fn=_read)

practice = [
  exercise_box("", taskline("<b>Die Aufgabe</b>") + "<div>…</div>"),
  numeric_answer([("re", "Re(z) ="), ("im", "Im(z) =")], _ans, task="tN"),
  code_fold("def f(x):\n    return ...\n", _check,
            task="tN", locked_by="tN-1", solution="…"),
]

interp = interpretation_box("Was man mitnimmt, in zwei Sätzen.")

build_chapter(N, "Titel", info=info, viz=viz, practice=practice,
              interp=interp, locked_by="tN-1", task="tN")
```

**Die Pflichtteile und warum sie es sind:**

| Teil | Pflicht | Warum |
|---|---|---|
| `info` mit Formel und benannten Variablen | ja | eine Formel ohne benannte Symbole ist eine Zierde |
| `viz` mit **mindestens einem Regler** | ja | ohne Regler ist es ein Bild, kein Notebook |
| `readout_fn` am Regler | ja | die Zahl neben dem Bild ist der halbe Erkenntnisgewinn |
| `exercise_box` + `numeric_answer` | ja | der Standardweg, ohne Programmieren |
| `code_fold` mit `solution=` | ja | der zweite Weg, ausdrücklich optional |
| `interp` | ja | ein Kapitel, das nicht sagt, was es bedeutet, ist Stoff, kein Lehrstoff |
| `locked_by` an **beiden** Stellen | ja | sonst bricht die Kette lautlos |

**Rückmeldungen sind diagnostisch, nicht binär.** Eine Prüffunktion erkennt die
typischen Fehler und benennt sie:

```python
def _ans_tN(v):
    if abs(v["x"] - want) > tol() * max(1, want):
        if abs(v["x"] - haeufiger_fehler) < .5:
            return False, "Das ist … — hier ist aber … gefragt."
        return False, "Rechne … ; der erste Schritt ist …"
    return True, "Richtig: …"
```

Das ist der teuerste und der wichtigste Teil eines Kapitels. Eine Aufgabe mit
„falsch" als einziger Antwort ist keine Aufgabe.

---

## 4. Was in `_setup_*.py` gehört

- `use_profile("biophysics")` · `use_style("quiet")`
- `set_notebook("<id>", "<Titel>")` — die **id** trägt den Fortschritt, nie der
  Dateiname
- `set_metadata(...)`: Titel, Untertitel, Autor:innen, Institution, Lizenz
  (CC BY-SA 4.0), `version=NB_VERSION`, Zielgruppe, Vorkenntnisse, Dauer,
  9 Schlagwörter, **Quelle mit Seitenzahlen**
- `inject_style()`
- Der **Seed**: `notebook_seed(int(_NBID, 16) % 100000)` und daraus `TV` — jede
  Aufgabe bekommt ihre Zahlen von dort, keine steht fest im Text
- `register_tasks([...])` mit Label je Aufgabe
- `BIB` — mindestens 5 Einträge, davon eine Primärquelle

---

## 5. Die Lernziele

`teaches.py` führt 6–7 Ziele, jedes mit **Stufe** (K3 basic / K4 intermediate /
K5 advanced) und jedes gekoppelt an **eine Aufgabe und eine Quizfrage**. Ein
Ziel, das nirgends geprüft wird, ist eine Absichtserklärung.

---

## 6. Prüfen, bevor etwas als fertig gilt

Sieben Suiten, alle grün, sonst ist es nicht fertig:

```
test_links · test_nb · test_checks · test_gating · test_answers · test_fixed · test_js
```

`test_checks` und `test_gating` prüfen genau die Regeln dieses Dokuments:
Sperrketten vorhanden, jede Aufgabe mit Anker, Kapitel nach der Entsperrbox
offen und seine Aufgabe zu.

**Zwei Suiten müssen bei jedem neuen Notebook mitwachsen** — das gehört zum
Lieferumfang, nicht hinterher:

- `test_answers.py` kennt die Lösungen fest (`_SETS_SOL` für Sets). Ohne
  eigenen Lösungsblock ist die Suite für das neue Notebook blind.
- `test_links.py` trägt die Notebook-Liste fest im Kopf (`NBS = [...]`). Wer
  nicht dort steht, wird nie geprüft; ein Eintrag ohne gebaute Datei lässt die
  Suite mit `FileNotFoundError` abbrechen — gemessen am 2026-09-24.

---

## 7. Was der Standard *nicht* vorschreibt

Die Oberfläche. Farben, Formen, Schriften, Stile stehen in
`notebooks/OBERFLAECHE.md` und gehören dem Toolkit, nicht dem einzelnen
Notebook. Ein Notebook, das eigene Farben setzt, ist kaputt.
