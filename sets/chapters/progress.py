# The panel is emitted at the END of the notebook (see build_complex.py): only
# then is the structure complete, so the panel that appears is the finished one.
_PROG["final"] = True
display(center(progress_panel()))
_PROG["final"] = False
