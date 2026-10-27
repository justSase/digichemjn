# The settings that need Python live here; everything that is pure appearance
# (full screen, light/dark, text size) is a button in the pinned panel.
_diff = Dropdown(options=[("Gentle — wide tolerance, full hints", "gentle"),
                          ("Standard", "standard"),
                          ("Strict — tight tolerance, minimal hints", "strict")],
                 value=DIFFICULTY["level"], description="Difficulty:",
                 layout=Layout(width="330px"), style={"description_width": "initial"})
# The dropdown lives in the toolbar now, so it carries nothing but itself: a
# paragraph explaining what changed has no room up there, and the dropdown's own
# option labels already say it ("Gentle — wide tolerance, full hints").
def _set_diff(ch):
    set_difficulty(ch["new"])
_diff.observe(_set_diff, "value")

_diff_box = VBox([_diff], layout=Layout(width="auto"))
_diff_box.add_class("nbctl-difficulty")

# start over — the same button the panel's drawer borrows
_reset_btn = Button(description="↺  Reset this notebook",
                    layout=Layout(width="220px", height="36px"))
_reset_btn.add_class("nbgiveup")
_reset_out = HTML(layout=_w(), value="")
_reset_armed = {"on": False}

def _do_reset(_b):
    if not _reset_armed["on"]:
        _reset_armed["on"] = True
        _reset_btn.description = "↺  Click again to confirm"
        _reset_out.value = ("<div class='nbwarn' style='text-align:center;font-size:.9em'>"
                            "This clears every answer and locks the chapters again.</div>")
        return
    nk = reset_progress()
    _reset_armed["on"] = False
    _reset_btn.description = "↺  Reset this notebook"
    _reset_out.value = ("<div class='nbok' style='text-align:center;font-size:.9em'>"
                        "Reset — %d exercises are open again.</div>" % nk)
_reset_btn.on_click(_do_reset)
_reset_box = VBox([center(_reset_btn), center(_reset_out)], layout=Layout(width="100%"))
_reset_box.add_class("nbctl-reset")



# ---- carrying progress between sessions and machines ----------------------
_code_out = HTML(layout=_w(), value="")
_code_in  = Text(placeholder="paste a progress code here",
                 layout=Layout(width="420px"))
_btn_show = Button(description="Show my progress code", layout=Layout(width="220px", height="36px"))
_btn_load = Button(description="Restore from code",     layout=Layout(width="190px", height="36px"))
_btn_show.add_class("sc-btn"); _btn_load.add_class("nbunlock")

def _show_code(_b):
    _code_out.value = ("<div class='nbink' style='text-align:center;font-size:.9em;margin-top:4px'>"
                       "Copy this and keep it — pasting it back restores your state:</div>"
                       "<pre style='%s;margin:6px auto 0;text-align:left;max-width:640px;"
                       "white-space:pre-wrap;word-break:break-all'>%s</pre>"
                       % (_CODE_PRE, progress_code()))
def _load_code(_b):
    ok, msg = apply_progress_code(_code_in.value)
    _code_out.value = ("<div class='%s' style='text-align:center;font-weight:700;margin-top:6px'>"
                       "%s</div>" % ("nbok" if ok else "nbwarn", msg))
_btn_show.on_click(_show_code); _btn_load.on_click(_load_code)
_code_box = VBox([center(_btn_show), center(_code_in),
                  HBox([_btn_load], layout=Layout(width="100%", justify_content="center")),
                  center(_code_out)], layout=Layout(width="100%"))
_code_box.add_class("nbctl-code")

# Both blocks are STASHED, not shown: the panel's ⚙ drawer adopts them, so the
# settings exist in exactly one place instead of two that can disagree.
_stash = VBox([_diff_box, _reset_box, _code_box], layout=Layout(width="100%"))
_stash.add_class("nbctl-stash")
display(_stash)
