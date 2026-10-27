DigiChemJN — Quellen-Bündel (Stand 2026-10-26, v1.83)

Arbeitsweise, Bauen, Prüfen: Projekt-Anweisungen + plan/STOP.md, plan/ZIELPLAN.md.
Bauen:  cd complex && python3 build_complex.py ;  cd modeling && python3 build_modeling.py
Ausgang A (E36): jeder build_*.py legt dist/huelle/<TOOLKIT_VERSION>/ + dist/inhalt/<id>/<NB_VERSION>/ an (toolkit/paket.py; DIGICHEM_DIST=0 lässt es weg). dist/ gehört nicht ins Bündel.
Packen: python3 pack_bundle.py pack <baum> notebooks/quellen-buendel.txt
Alte Schnappschüsse und Notizen (24.09.): PC Desktop\DigiChem\Archiv\nur-im-buendel\2026-10-08\
