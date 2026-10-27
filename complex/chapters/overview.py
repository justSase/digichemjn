def _link(target, label):
    a = _aid(target)
    return ("<a class='nbjump' data-target='%s' href='#%s' "
            "style='color:var(--nbskin-acc,#2c6e91);text-decoration:none;font-weight:600'>%s</a>" % (a, a, label))

_rows = "".join(
    "<div style='margin:5px 0'>%s</div>" % _link(t, l) for t, l in [
        ("grp_intro",   "👋&nbsp; Introduction — setup, how to use this notebook, learning objectives"),
        ("ch1", "1.&nbsp; Why complex numbers?"),
        ("ch2", "2.&nbsp; The complex plane"),
        ("ch3", "3.&nbsp; Addition and subtraction"),
        ("ch4", "4.&nbsp; Multiplication and conjugation"),
        ("ch5", "5.&nbsp; Absolute value and division"),
        ("ch6", "6.&nbsp; Polar form and Euler's relation"),
        ("ch7", "7.&nbsp; The geometry of multiplication"),
        ("grp_appendix", "📑&nbsp; Appendix — remarks, summary, glossary, references, quiz, your own data"),
    ])

build_chapter(None, "Contents", icon="🧭", chapter_open=False, anchor="overview",
    info=note_box("<div style='text-align:center'>" + _rows + "</div>"))
