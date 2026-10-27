"""E26.3 (2026-10-11, Python) — THE TEXT THE CELL RUNS.

Since E26.3 the notebook's code cell is short: a few lines and one line of
cargo (toolkit/shortcell.py). The suites that READ the cell (search a rule,
walk its AST, exec it in plain Python) read what the cargo unpacks to — the
cell as it was up to v1.73, byte for byte. A cell without cargo comes back as
it is, so the suites still read older builds.
    import megasrc; text = megasrc.expand(cell_source)"""
import os, sys
_TK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "toolkit")
if _TK not in sys.path:
    sys.path.insert(0, _TK)
from shortcell import expand  # noqa: E402,F401
