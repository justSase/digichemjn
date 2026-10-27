# ---------------------------------------------------------------------------
# DigiChemJN · VORLAGE — Setup dieses Notebooks (Platzhalter)
# Kopieren: Ordner vorlage/ → <neues_notebook>/, dann ANLEITUNG.md folgen.
# ---------------------------------------------------------------------------
use_profile("biophysics")          # Fachstandard (Profile siehe toolkit)
use_style("quiet")
set_notebook("vorlage", "Notebook title")      # id (klein, mit -), Titel
# E30 B2: the texts in English, German in de.txt (the reading copy switches them too)
set_metadata(
    thema="vorlage.vorlage",                # E39a: Katalog-Schlüssel bereich.thema (eindeutig)
    kurse=[],                   # ("<HS> · <Vorlesung>", "<platz>"), …
    title="Notebook title",
    subtitle="Series, section (placeholder)",
    authors=["… enter the authors …"],
    institution="Fakultät für Chemie und Pharmazie, Albert-Ludwigs-Universität Freiburg",
    licence="CC BY-SA 4.0",
    licence_url="https://creativecommons.org/licenses/by-sa/4.0/",
    version=NB_VERSION,
    date="2026-10",
    doi="", repo="",
    audience="Audience (degree programme, semester)",
    prerequisites="Prior knowledge (placeholder)",
    keywords=["keyword 1", "keyword 2", "OER", "Jupyter", "DigiChemJN"],
    source="Source of the content (script, chapter, pages)",
)
inject_style()

# --- persönliche Werte je Seed (jede:r bekommt eigene Zahlen) --------------
VL_SEED = notebook_seed(int(_NBID, 16) % 100000)
VL_MODE = notebook_mode()
_rng = np.random.default_rng(VL_SEED)

def _draw_tv(rng, level=None):
    """Alle persönlichen Zahlen an EINER Stelle. Platzhalter: a, b ganze Zahlen."""
    return dict(a=int(rng.integers(2, 10)), b=int(rng.integers(2, 10)))

TV = _draw_tv(_rng)
personal_draw(lambda seed: TV.update(_draw_tv(np.random.default_rng(seed))))

# --- Lernziele: (K-Stufe, Niveau, Text) — erscheinen auf Titelkarte und im OER-Datensatz
register_goals([
 ("K3", "basic", "learning goal 1 (placeholder)"),
 ("K4", "intermediate", "learning goal 2 (placeholder)"),
])

# --- Aufgaben: (Schlüssel, Kurzname, Kapitel-Anker, Name auf der Zeitleiste)
register_tasks([
    ("t1", "1 · exercise", "ch1", "Exercise name 1 (placeholder)"),
    ("t2", "2 · exercise", "ch2", "Exercise name 2 (placeholder)"),
    ("t3", "3 · exercise", "ch3", "Exercise name 3 (placeholder)"),
    ("t4", "4 · exercise", "ch4", "Exercise name 4 (placeholder)"),
    ("t5", "5 · exercise", "ch5", "Exercise name 5 (placeholder)"),
])

# --- Minuten je Element für die Zeitangabe (Titelkarte, OER): hier die Standardwerte
set_time_rule(chapter=3, task=5, figure=2, coding=10)

QUIZ = []

# --- Literatur: Nummer → Eintrag; im Text mit cite(1)
BIB = {
 1: 'Autor:in, <i>Titel</i>, Verlag/Zeitschrift, Jahr.',
 2: 'Zweite Quelle (Platzhalter), <i>Titel</i>, Jahr.',
}

notebook_start()
