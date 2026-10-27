"""Run the notebook's mega-cell head-less and dump its widget tree as JSON.

The tree is what the HTML build is generated from: every HTML widget carries its
finished markup, and the interactive widgets (sliders, number boxes, radio
buttons, buttons, outputs) are recorded with the parameters the JS runtime needs.
"""
import json, io, contextlib, sys
import matplotlib; matplotlib.use("Agg")
import IPython.display as ipd
SEEN = []
ipd.display = lambda *a, **k: SEEN.append(a[0] if a else None)

NB = sys.argv[1] if len(sys.argv) > 1 else \
     "/home/claude/work/complex/Complex_Numbers_Step_by_Step.ipynb"
src = "\n".join(l for l in "".join(json.load(open(NB))["cells"][-1]["source"]).splitlines()
                if not l.strip().startswith("%pip"))
G = {"__name__": "__main__", "display": ipd.display}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src, "mega", "exec"), G)

# Every exercise is locked behind the previous one in the notebook; the locked
# ones are not in the displayed tree at all. Open them all before serialising —
# the HTML runtime re-implements the gate itself.
for _k in G["_TASKS"]["order"]:
    G["_open_lock"]("chapter", _k)
    G["_open_lock"]("practice", _k)

def node(w, depth=0):
    cn = type(w).__name__
    if cn in ("HTML", "HTMLMath"):
        # IPython.display.HTML (a raw block) vs ipywidgets.HTML (a widget)
        v = getattr(w, "value", None)
        if v is None:
            v = getattr(w, "data", "")
        return {"t": "html", "v": v}
    if cn == "Accordion":
        titles = [w.get_title(i) for i in range(len(w.children))]
        return {"t": "acc", "titles": titles, "cls": list(w._dom_classes),
                "open": (w.selected_index == 0),
                "kids": [node(k, depth+1) for k in w.children]}
    if cn in ("VBox", "HBox", "Box", "GridBox"):
        return {"t": "box", "dir": "h" if cn == "HBox" else "v",
                "cls": list(w._dom_classes), "kids": [node(k, depth+1) for k in w.children]}
    if cn in ("FloatSlider", "IntSlider"):
        return {"t": "slider", "desc": w.description, "min": w.min, "max": w.max,
                "step": w.step, "value": w.value}
    if cn in ("FloatText", "IntText", "Text"):
        return {"t": "num", "desc": w.description, "value": w.value}
    if cn == "RadioButtons":
        return {"t": "radio", "options": [str(o) for o in w.options]}
    if cn == "Dropdown":
        return {"t": "dropdown", "desc": w.description,
                "options": [str(o) for o in w.options], "value": str(w.value)}
    if cn == "Button":
        return {"t": "button", "label": w.description, "cls": list(w._dom_classes)}
    if cn == "Textarea":
        return {"t": "textarea", "value": w.value}
    if cn == "Output":
        return {"t": "out"}
    if cn == "ToggleButton":
        return {"t": "toggle", "label": w.description}
    return {"t": "?" + cn}

tree = [node(w) for w in SEEN if w is not None and hasattr(w, "_dom_classes") or
        type(w).__name__ in ("HTML", "Accordion")]
raw = []
for w in SEEN:
    if w is None:
        continue
    cn = type(w).__name__
    if cn == "HTML" and not hasattr(w, "value"):
        continue
    try:
        raw.append(node(w))
    except Exception as e:
        raw.append({"t": "err", "v": repr(e)})
# the pieces the HTML build needs beyond the widget tree
CAP = {"css": [], "js": []}
class _RH:
    def __init__(self, v): CAP["css"].append(v)
class _RJ:
    def __init__(self, v): CAP["js"].append(v)
_saveI, _saveJ = G["IHTML"], G["Javascript"]
G["IHTML"], G["Javascript"] = _RH, _RJ
G["inject_style"]()
G["IHTML"], G["Javascript"] = _saveI, _saveJ

frames = {k: v for k, v in G.items()
          if k.endswith("_frames") and isinstance(v, list) and v and isinstance(v[0], str)}
labels = {k: v for k, v in G.items()
          if k.endswith("_labels") and isinstance(v, list)}

json.dump({"tree": raw,
           "css": "".join(CAP["css"]),
           "panel": (G["_PROG"].__setitem__("final", True), G["_prog_html"]())[1],
           "frames": frames, "labels": labels,
           "tv": {k: ({"re": v.real, "im": v.imag} if isinstance(v, complex) else v)
                  for k, v in (G.get("TV") or {}).items()},
           "tol": G["tol"](),
           "quiz": G.get("QUIZ"),
           "struct": G["_STRUCT"],
           "tasks": {"order": G["_TASKS"]["order"], "label": G["_TASKS"]["label"],
                     "anchor": G["_TASKS"]["anchor"], "has_code": G["_TASKS"]["has_code"]},
           "notebook": G["NOTEBOOK"]},
          open("/home/claude/work/html/tree.json", "w"), ensure_ascii=False)
def count(n, acc):
    acc[n["t"]] = acc.get(n["t"], 0) + 1
    for k in n.get("kids", []): count(k, acc)
    return acc
acc = {}
for n in raw: count(n, acc)
print("top-level nodes:", len(raw))
print("node types:", dict(sorted(acc.items(), key=lambda kv: -kv[1])))
