_intro = note_box(
  "Along the right-hand edge of the window runs a rail, and across the top a toolbar. They are "
  "one instrument. This chapter is the only one you cannot do without touching it, so put the "
  "mouse on the rail while you read.")

info = note_box(
  "<b>The rail is the notebook's table of contents</b> — one bar per chapter, one circle per "
  "exercise, one dot per section — laid out so that every mark sits at the height of the thing "
  "it stands for. Click any of them and the document goes there, opening whatever was folded "
  "shut on the way.<br><br>"
  "<b>The rail is also the scrollbar.</b> The bright vertical marker is your position in the "
  "document; drag it and the page follows. The front end's own scrollbar is hidden while the "
  "rail is there, because two bars saying the same thing is one too many. The marker is white "
  "in the dark theme and blue in the light one — in both it is the one thing on screen wearing "
  "the colour of attention.<br><br>"
  "<b>The rail is the progress display.</b> Green fills it up to the open padlock; a solved "
  "exercise is a filled circle, a skipped one keeps an amber ring and a ⤼, one you gave up on "
  "gets a red ✗, and everything still shut is grey.<br><br>"
  "<b>Two sliders, top right.</b> <i>Doc</i> scales the reading matter — the text and the "
  "pictures — and deliberately leaves the instrument alone, so that shrinking the document does "
  "not shrink the thing you navigate it with. <i>Panel</i> sets how wide the rail is, and as it "
  "narrows the rail drops detail in a fixed order rather than squashing it: first the labels, "
  "then the emoji, then the circles, then the bars, then the dots, until a single line is left "
  "that goes on thinning. A double-click on either slider puts it back to 100 %.<br><br>"
  "<b>The rest of the toolbar.</b> Difficulty sits at the far left, next to full screen and the "
  "light/dark switch. In the middle are your progress chip and the statistics badge — ✓ solved, "
  "⤼ skipped, ✗ given up, out of the total, counted across every notebook of the series this "
  "browser has seen.")

_LADDER = [("labels", 85), ("emoji", 70), ("circles", 58), ("bars", 46), ("dots", 36)]

def _render_c05(panel=100):
    fig, ax = fixed_canvas(figsize=(7.4, 3.8), left=.10, right=.97, top=.92, bottom=.18)
    theme_axes(ax, grid=False)
    ax.set_xlim(15, 160); ax.set_ylim(0, 6)
    cols = [PAL["z2"], PAL["aux"], PAL["sum"], PAL["warn"], PAL["z"]]
    for i, (name, thr) in enumerate(_LADDER):
        y = 5.2 - i
        alive = panel >= thr
        ax.plot([thr, 160], [y, y], color=cols[i], lw=7, alpha=.85 if alive else .18,
                solid_capstyle="butt", zorder=2)
        ax.plot([15, thr], [y, y], color="#dfe4e9", lw=7, solid_capstyle="butt", zorder=1)
        ax.text(157, y + .32, name, fontsize=9, ha="right", color=cols[i],
                fontweight="bold" if alive else "normal")
        ax.text(thr, y - .45, "%d %%" % thr, fontsize=8, ha="center", color="#8b98a5")
    ax.axvline(panel, color=PLOT_INK, lw=2.2, zorder=4)
    ax.set_yticks([]); ax.set_xlabel("Panel slider  [%]")
    return fig

def _read_c05(panel=100):
    alive = [n for n, t in _LADDER if panel >= t]
    return readout([("Panel", "%d %%" % panel),
                    ("still drawn", ", ".join(alive) if alive else "only the line"),
                    ("next to go", next((n for n, t in _LADDER if panel >= t > panel - 15),
                                        "—")),
                    ("rail width", "%d px" % max(4, round(3.0 * panel)))])

viz = [viz_intro_box("",
    "The detail ladder, as a set of thresholds. Drag <b>panel</b> and each stripe dies at its "
    "own percentage. Then do the same with the real <i>Panel</i> slider in the toolbar and "
    "watch the rail beside you lose exactly these things in exactly this order — the picture is "
    "not an illustration of the behaviour, it is a plot of the numbers that produce it.")]
viz += slider_plot(_render_c05, {"panel": IntSlider(value=100, min=15, max=160, step=5,
                                                    description="panel")},
                   readout_fn=_read_c05)

def _ans_c05(v):
    if abs(v["text"] - 80) > 2.5:
        if abs(v["text"] - 85) <= 2.5:
            return False, ("Nearly — at 85 % the labels are still there. Take it one step "
                           "further down and look again.")
        return False, ("Not yet. Set the Panel slider to 100 % and step down by 5 until the "
                       "chapter names beside the bars disappear; you entered %g." % v["text"])
    if abs(v["dots"] - 35) > 2.5:
        if v["dots"] > 40:
            return False, ("The dots outlast the circles and the bars — keep going down. "
                           "You entered %g." % v["dots"])
        return False, ("Close. The dots survive to the last step before the rail becomes a bare "
                       "line; you entered %g." % v["dots"])
    return True, ("Correct: the labels go at 80 %, the dots at 35 %, and what is left below that "
                  "is one line that keeps on thinning.")

practice = [
  exercise_box("", taskline(
    "<b>Use the Panel slider in the toolbar.</b> Start at 100 % and step down, watching the rail.")
    + "<div>Give the <b>first setting at which the chapter names are gone</b>, and the "
      "<b>first setting at which the small dots are gone too</b>. Both to the nearest 5 %. "
      "Double-click the slider when you are done to put it back.</div>"),
  numeric_answer([("text", "names gone at [%] ="), ("dots", "dots gone at [%] =")],
                 _ans_c05, task="t5"),
]

interp = interpretation_box(
  "A panel that shrinks by squashing becomes unreadable at every size. One that shrinks by "
  "<b>dropping the least load-bearing thing first</b> stays readable at every size, and still "
  "says something useful when it is four pixels wide — you are here, this much is done. That is "
  "worth having on a laptop screen with a lecture beside it, and it is the reason the ladder has "
  "a fixed order instead of a font size.")

build_chapter(5, "The rail, the marker and the two sliders", info=info, intro=_intro, viz=viz,
              practice=practice, interp=interp, task="t5", locked_by="t4")
