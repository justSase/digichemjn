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
set -e
(cd start    && python3 build_start.py)
(cd complex  && python3 build_complex.py)
(cd sets     && python3 build_sets.py)
(cd ml       && python3 build_main.py)
(cd modeling && python3 build_modeling.py)
