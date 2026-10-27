# DigiChemJN

Interaktive Lehr-Notebooks (Open Educational Resources) der Fakultät für Chemie und Pharmazie, Universität Freiburg.
Inhalte unter **CC BY-SA 4.0** (laut Antrag); Lizenz für den Code: noch offen.

Dieses Repo ist die **Quelle**: Kapiteldateien, Toolkit, Bau und Tests. Fertige Notebooks (`.ipynb`) und die Pakete für die digi App
(`dist/`) entstehen beim Bauen und kommen als **Release** dazu, nicht in den Baum.

## Bauen

    python3 -m pip install -r repo/requirements-build.txt   # matplotlib 3.10 (sonst anderer Build)
    cd vorlage  && python3 build_vorlage.py
    cd complex  && python3 build_complex.py
    cd modeling && python3 build_modeling.py

Jeder Bau schreibt die `.ipynb` und `dist/` (Hülle + Inhaltspaket, siehe `toolkit/paket.py`).

## Aufbau

| Ordner | Inhalt |
|---|---|
| `toolkit/` | gemeinsamer Werkzeugkasten (Python, `css/`, `js/`) |
| `vorlage/` | die Vorlage: jeder Baustein einmal — Prüfstrecke für alles |
| `complex/`, `modeling/`, `sets/`, `start/`, `ml/` | Notebooks (Kapiteldateien + Bau) |
| `tests/` | Suiten und Regressionstests (Playwright, echtes JupyterLab) |
| `repo/` | Vorlagen für die spätere Veröffentlichung (Lite-Seite) |

Stand: v1.82 (19.10.2026). Arbeitsweise und Runden: Claude-Projekt „DigiChem | Sase“.
