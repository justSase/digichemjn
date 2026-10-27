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
    # 2026-09-28 (Paket 12b) — the numbers depend on the level now: draw them
    # again for the new one, in place (reseed, Paket 13)
    if _RESEED.get("draw"):
        reseed(SEED["value"])
_diff.observe(_set_diff, "value")

# R3 · 18 (Applikation) — WHAT THIS NOTEBOOK BUILDS: calculating, coding, or
# both. A fold that is not wanted is not built, so a change needs a new run:
# the choice is stored (set_mode) and the ▶ under it restarts and runs all —
# the same class the cover's Play carries, so the page's one handler does it.
# E16.11 — the fourth content, "plain": text and figures, no exercises
_MODE_TXT = {"both": "Both — calculate and code", "calc": "Only calculating",
             "code": "Only coding", "plain": "Plain — text and figures only"}
_mode = Dropdown(options=[(_MODE_TXT[m], m) for m in MODES],
                 value=MODE["value"], description="Content:",
                 layout=Layout(width="330px"), style={"description_width": "initial"})
# E9.9 (2026-09-30) — the button says that it rebuilds NOW; without it the
# choice waits for the next run (the note says so)
_mode_go = Button(description="▶  Rebuild now with this content",
                  layout=Layout(width="270px", height="36px"))
_mode_go.add_class("nbrunall"); _mode_go.add_class("sc-btn")
_mode_out = HTML(layout=_w(), value="")
_mode_row = center(_mode_go)        # shown only once a different choice is stored
def _mode_note(extra=""):
    _mode_out.value = extra + (
        "<div style='text-align:center;font-size:.85em;opacity:.8'>Now: <b>%s</b>. "
        "Each choice keeps its own progress.</div>" % _MODE_TXT[MODE["value"]])
# E8.16 — a hidden live output: the choice goes to the browser's store as well
# (mode_page_js), so the page does not put the dropdown back to an older choice
_mode_js = Output(layout=Layout(display="none"))
def _mode_to_page(v):
    js = mode_page_js(v)
    if not js:
        return
    _mode_js.clear_output()
    with _mode_js:
        display(Javascript(js))
def _set_mode(ch):
    # E8.16 — stored EVERY time, also when it is the mode this run was built
    # with: going back to it must overwrite a choice made in between
    ok = set_mode(ch["new"])
    if ok:
        _mode_to_page(ch["new"])
    if ch["new"] == MODE["value"]:
        _mode_note(); _mode_row.layout.display = "none"
        return
    _mode_row.layout.display = "flex" if ok else "none"
    _mode_note("<div class='%s' style='text-align:center;font-size:.9em'>%s</div>" % (
        ("nbok", "“%s” saved — it applies from the next run. ▶ rebuilds now."
         % _MODE_TXT[ch["new"]]) if ok else
        ("nbwarn", "Could not save this choice here.")))
_mode.observe(_set_mode, "value")
# E17.1 — the page finds this dropdown by class, not by its (now translated)
# labels; the options keep the order of MODES
_mode.add_class("nbctl-mode")
_mode_row.layout.display = "none"
_mode_note()

# E17.5 (2026-10-02, Applikation) — THE LANGUAGE. A profile value (all our
# notebooks follow it); the text is built for it, so a change needs a new
# run, like the content above. The page (cover, 👤) sets this dropdown to hand
# a choice to a server kernel (class nbctl-lang; options in LANGS order).
_LANG_TXT = {"en": "English", "de": "Deutsch"}
_lang = Dropdown(options=[(_LANG_TXT[l], l) for l in LANGS], value=LANG["value"],
                 description="Language · Sprache:",
                 layout=Layout(width="330px"), style={"description_width": "initial"})
_lang.add_class("nbctl-lang")
_lang_go = Button(description="▶  Rebuild now · Jetzt neu aufbauen",
                  layout=Layout(width="300px", height="36px"))
_lang_go.add_class("nbrunall"); _lang_go.add_class("sc-btn")
_lang_row = center(_lang_go)
_lang_out = HTML(layout=_w(), value="")
_lang_js = Output(layout=Layout(display="none"))
def _set_lang(ch):
    ok = lang_store(ch["new"])
    if ok:
        js = lang_page_js(ch["new"])
        _lang_js.clear_output()
        with _lang_js:
            display(Javascript(js))
    same = ch["new"] == LANG["value"]
    _lang_row.layout.display = "none" if same or not ok else "flex"
    _lang_out.value = "" if same else (
        "<div class='%s' style='text-align:center;font-size:.9em'>%s</div>" % (
            # E23.1: one language per run (the table gives the German)
            ("nbok", "Saved: %s from the next run." % _LANG_TXT[ch["new"]]) if ok else
            ("nbwarn", "Could not save this choice here.")))
_lang.observe(_set_lang, "value")
_lang_row.layout.display = "none"

_diff_box = VBox([_diff, _mode, _mode_row, _mode_out, _mode_js,
                  _lang, _lang_row, _lang_out, _lang_js], layout=Layout(width="auto"))
_diff_box.add_class("nbctl-difficulty")

# start over — the same button the panel's drawer borrows
# 2026-09-28 (R1 · Paket 3, Applikation) — RESET ASKS FIRST. Until now the
# first click armed the button ("Click again to confirm") and it stayed armed
# for good: any later click, or Enter on the focused button, wiped the record.
# Now the button only asks. "Are you sure?" with two buttons: Yes resets,
# Cancel changes nothing. Both are hidden until the question is asked, so no
# key and no single click can reset. What goes: this notebook's answers and
# its statistics (the ✓ ⤼ ✗ and the tolerance they were settled under). What
# stays: the seed, the style, light/dark, the difficulty, the other notebooks.
_reset_btn = Button(description="↺  Reset this notebook",
                    layout=Layout(width="220px", height="36px"))
_reset_btn.add_class("nbgiveup")
_reset_yes = Button(description="Yes, reset", layout=Layout(width="130px", height="34px"))
_reset_yes.add_class("nbgiveup")
_reset_no = Button(description="Cancel", layout=Layout(width="110px", height="34px"))
_reset_no.add_class("nbunlock")
_reset_ask = HBox([_reset_yes, _reset_no],
                  layout=Layout(width="100%", justify_content="center",
                                grid_gap="10px", display="none"))
_reset_out = HTML(layout=_w(), value="")

def _reset_hide():
    _reset_ask.layout.display = "none"
    _reset_btn.disabled = False

def _do_reset(_b):
    _reset_btn.disabled = True
    _reset_ask.layout.display = "flex"
    _reset_out.value = ("<div class='nbwarn' style='text-align:center;font-size:.9em'>"
                        "<b>Sure?</b> Clears answers and statistics of <b>this notebook</b> "
                        "and locks the chapters. Seed, style and settings stay.</div>")

def _reset_confirm(_b):
    if _reset_ask.layout.display == "none":      # never without the question
        return
    _reset_hide()
    nk = reset_progress()
    _reset_out.value = ("<div class='nbok' style='text-align:center;font-size:.9em'>"
                        "Reset: %d exercises open again.</div>" % nk)

def _reset_cancel(_b):
    _reset_hide()
    _reset_out.value = ("<div class='nbink' style='text-align:center;font-size:.9em'>"
                        "Nothing was reset.</div>")

_reset_btn.on_click(_do_reset)
_reset_yes.on_click(_reset_confirm)
_reset_no.on_click(_reset_cancel)
_reset_box = VBox([center(_reset_btn), _reset_ask, center(_reset_out)],
                  layout=Layout(width="100%"))
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
                       "Keep this code. Paste it back to restore:</div>"
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
# E17.5 — the page's way in for an account's progress (merged, never lowered):
# it writes a code into this hidden field; the answer lands in .nbctl-merge-res
_merge_in = Text(value="", layout=Layout(display="none"))
_merge_in.add_class("nbctl-merge")
_merge_out = HTML(value="", layout=Layout(display="none"))
def _merge(ch):
    if not ch["new"]:
        return
    ok, msg = merge_progress_code(ch["new"])
    _merge_out.value = "<div class='nbctl-merge-res' data-ok='%d'>%s</div>" % (ok, msg)
    _merge_in.value = ""
_merge_in.observe(_merge, "value")
_code_box.children = _code_box.children + (_merge_in, _merge_out)

# ---- the seed ------------------------------------------------------------
# 2026-09-28 (R2 · Paket 13) — IN PLACE, NOT A NEW RUN. Until 28f this control
# remembered a number and pressed Run All, so the page was rebuilt and every
# open fold and typed box was gone. Now the kernel draws the personal numbers
# again (reseed in the toolkit) and the exercises change where they stand; the
# answer boxes empty, the progress stays. The number is still stored, so the
# next run — on any machine — draws the same exercises.
_seed_in  = IntText(value=SEED["value"], description="Seed:",
                    layout=Layout(width="220px"),
                    style={"description_width": "initial"})
_seed_out = HTML(layout=_w(), value="")
_seed_set = Button(description="Use this seed", layout=Layout(width="170px", height="36px"))
_seed_rnd = Button(description="🎲  New random seed", layout=Layout(width="200px", height="36px"))
_seed_set.add_class("nbunlock"); _seed_rnd.add_class("sc-btn")

_SEED_NOTE = ("<div class='nbink' style='text-align:center;font-size:.88em;margin-top:6px'>"
              "Seed <b>%d</b> — %s.</div>")

def _seed_state(extra=""):
    _seed_out.value = extra + _SEED_NOTE % (
        SEED["value"],
        "pinned: same numbers next run" if SEED["fixed"]
        else "not pinned: new numbers next run")

def _seed_now(v, fixed):
    reseed(v, fixed=fixed)
    _seed_in.value = v
    _seed_state("<div class='nbok' style='text-align:center;font-size:.9em'>"
                "New numbers from seed %d. Progress kept.</div>" % v)

def _seed_apply(_b):
    v = int(_seed_in.value)
    if v < 0 or v > 99999999:
        _seed_out.value = ("<div class='nbwarn' style='text-align:center;font-size:.9em'>"
                           "A whole number, 0 to 99999999.</div>")
        return
    if not seed_store(v):
        _seed_out.value = ("<div class='nbwarn' style='text-align:center;font-size:.9em'>"
                           "Could not save this seed here. Nothing changed.</div>")
        return
    _seed_now(v, True)

def _seed_random(_b):
    seed_forget()
    import random as _rnd
    v = _rnd.randrange(100000)
    while v == SEED["value"]:
        v = _rnd.randrange(100000)
    _seed_now(v, False)

_seed_set.on_click(_seed_apply); _seed_rnd.on_click(_seed_random)
_seed_state()
_seed_box = VBox([center(_seed_in),
                  HBox([_seed_set, _seed_rnd],
                       layout=Layout(width="100%", justify_content="center")),
                  center(_seed_out)], layout=Layout(width="100%"))
_seed_box.add_class("nbctl-seed")

# Both blocks are STASHED, not shown: the panel's ⚙ drawer adopts them, so the
# settings exist in exactly one place instead of two that can disagree.
_stash = VBox([_diff_box, _reset_box, _code_box, _seed_box], layout=Layout(width="100%"))
_stash.add_class("nbctl-stash")
display(_stash)
