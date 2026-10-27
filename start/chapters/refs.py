# The list is written LAST and shown HERE. Its numbers follow the order the
# sources first appear in the text, so it cannot be filled in while chapters are
# still to come — and the two activity sections (quiz, own data) now come after
# this one. So the box is placed empty and filled by a finalizer.
_refs_box = note_box("")
_meta_box = HTML(layout=_w(), value="")

def _fill_references():
    _items = ""
    for _n, _sid in enumerate(_CITEREG["order"], start=1):
        _items += ("<div id='%s' style='margin:8px 0;text-align:left'>"
                   "<b>[%d]</b>&emsp;%s</div>" % (_aid("ref%d" % _n), _n, BIB[_sid]))
    _refs_box.value = _refs_box.value.replace(
        "<!--REFS-->", "<div style='max-width:820px;margin:0 auto'>%s</div>" % _items)
    set_metadata(objectives=OBJECTIVES)
    _meta_box.value = metadata_box().value

_refs_box.value = _refs_box.value.replace("</div></div>", "<!--REFS--></div></div>")
on_notebook_built(_fill_references)
build_chapter(None, "References and licence", icon="📚", chapter_open=False,
  anchor="references", info=_refs_box, body=[_meta_box])
