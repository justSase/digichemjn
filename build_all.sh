#!/bin/sh
# Rebuild EVERY notebook. The toolkit is shared, so a change to
# toolkit/chapter_template.py only reaches a notebook once it is rebuilt —
# always run this, never a single build script on its own.
#
# 2026-09-25 — sets WAS MISSING HERE. This script said "EVERY notebook" and
# built four of five, so anyone who trusted it shipped a Sets notebook on
# whatever toolkit it was last built with. Nothing failed, nothing went red:
# the stale file was simply still there from before. That is the failure mode
# this project keeps paying for — a green run that is green because of the bug.
# There are five. Count them.
#
# 2026-10-27 (E39a A1, Speicher): start/ und ml/ sind aus dem Buendel ausgelagert
# (C:/DigiChem/archiv/buendel-auslagerung-2026-10-27.tar.gz). Fehlt ein Ordner,
# sagt das Skript es laut - gebaut wird, was da ist.
set -e
b() { if [ -d "$1" ]; then (cd "$1" && python3 "$2"); else echo "UEBERSPRUNGEN: $1/ (ausgelagert 2026-10-27)"; fi; }
b start    build_start.py
b complex  build_complex.py
b sets     build_sets.py
b ml       build_main.py
b modeling build_modeling.py
