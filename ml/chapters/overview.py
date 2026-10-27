# Chapter overview (table of contents) — mirrors the three groups the notebook
# is organised into. Links carry class "nbjump" + data-target so the click
# handler can expand a collapsed group/chapter before scrolling; the href="#id"
# is a native fallback when the accordions are already open.
_ov_groups = [
    ("👋  Introduction", "grp_intro", [
        ("Setup", "setup"),
        ("How this notebook works", "howto"),
        ("What this notebook teaches", "teaches"),
        ("Topic roadmap", "roadmap"),
    ]),
    ("📚  Content", "grp_content", [
        ("1. What is machine learning?", "ch1"),
        ("2. The building block: A line", "ch2"),
        ("3. Measuring error: The loss", "ch3"),
        ("4. Learning by rolling downhill (gradient descent)", "ch4"),
        ("5. From a line to a probability: The sigmoid", "ch5"),
        ("6. Over- and underfitting", "ch6"),
        ("7. Neural networks: Neurons, activations &amp; a tiny network", "ch7"),
        ("8. Unsupervised learning: Clustering", "ch8"),
        ("9. From words to vectors: Tokenisation &amp; embeddings", "ch9"),
        ("10. Attention: The heart of the transformer", "ch10"),
        ("11. A tiny language model: Next-token prediction &amp; temperature", "ch11"),
        ("12. What LLMs are and are not", "ch12"),
        ("13. Evaluation &amp; good practice", "ch13"),
    ]),
    ("📑  Appendix", "grp_appendix", [
        ("Remarks", "remarks"),
        ("Summary", "summary"),
        ("Glossary", "glossary"),
        ("References & Literature", "references"),
        ("Multiple-choice quiz", "quiz"),
        ("Bring your own data", "byod"),
    ]),
]

import re as _re
def _gap(lbl):
    # put the number in a fixed-width right-aligned box so the titles line up
    # whether the number is one or two digits (1. … 14.)
    m = _re.match(r"^(\d+)\.\s+(.*)$", lbl)
    if not m:
        return lbl
    # number left-aligned (flush with the un-numbered items like Glossary), then
    # a fixed-width gap so every title starts at the same left column
    return ("<span style='display:inline-block;width:1.9em;text-align:left'>%s.</span>%s"
            % (m.group(1), m.group(2)))

_ov_html = ("<div style='text-align:center;color:#5b6b7b;font-size:.82em;text-transform:uppercase;"
            "letter-spacing:1.6px;margin-bottom:14px'>click a chapter to jump there</div>")
for _title, _ganchor, _items in _ov_groups:
    # the section title itself is a link that jumps to (and expands) the section header
    _ov_html += ("<div style='margin:16px 0 8px;padding-bottom:4px;border-bottom:2px solid #cdd6dd'>"
                 "<a class='nbjump' data-target='%s' href='#%s' style='color:#33566b;font-weight:800;"
                 "font-size:1.02em;letter-spacing:.3px;text-decoration:none'>%s</a></div>"
                 % (_aid(_ganchor), _aid(_ganchor), _title))
    _ov_html += "".join(
        "<div style='margin:6px 0 6px 10px'><a class='nbjump' data-target='%s' href='#%s' "
        "style='color:#3b444d;font-weight:600;text-decoration:none;font-size:1.04em'>%s</a></div>"
        % (_aid(a), _aid(a), _gap(label))
        for label, a in _items)

build_chapter(None, "Content overview", info=note_box(_ov_html, grey=True),
              icon="🧭", anchor="overview", outer_class="acc-group")
