"""Generate a self-contained HTML version of the Complex Numbers notebook.

Input : tree.json (produced by extract.py — the notebook's own widget tree,
        its CSS, its pre-rendered formula/plot images and its seeded values)
Output: Complex_Numbers.html — one file, no kernel, no network.

What changes compared with the notebook:
  * accordions become <details>, so they work without ipywidgets;
  * sliders drive a <canvas> re-implementation of the matplotlib figure
    (plots.js); a figure without a port keeps its matplotlib PNG;
  * the answer checks are ported to JS (checks.js) with the same tolerances;
  * progress is the same localStorage record as the notebook, so both versions
    of THIS notebook feed the same series total.
"""
import json, re, os, html as H

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "tree.json")))
NBID = D["notebook"]["id"]

def esc(s): return H.escape(s, quote=True)

# ----------------------------------------------------------------- helpers
def is_read(n):   return n["t"] == "html" and "nbread" in (n.get("v") or "")[:120]
def is_plot(n):   return n["t"] == "html" and 'class="nbplot"' in (n.get("v") or "")
def is_feed(n):   return n["t"] == "html" and 'class="nbfeed"' in (n.get("v") or "")[:60]
def flat(n):
    """A box that only wraps a single child adds nothing in HTML."""
    while n["t"] == "box" and len(n.get("kids") or []) == 1 and not n.get("cls"):
        n = n["kids"][0]
    return n

FIG_SEQ = {}      # chapter anchor -> running number, so figure ids are stable
def fig_id(ctx, kind):
    base = (ctx["anchor"] or "x")
    if base.startswith("prac_"): base = base[5:]
    key = "%s-%s" % (base, kind)
    FIG_SEQ[key] = FIG_SEQ.get(key, 0) + 1
    return key if FIG_SEQ[key] == 1 else "%s%d" % (key, FIG_SEQ[key])

def slider_html(fig, s, i):
    sid = "%s-s%d" % (fig, i)
    return ("<label class='nbsl' for='%s'><span class='nbsl-lab'>%s</span>"
            "<input type='range' id='%s' data-fig='%s' data-key='%s' min='%s' max='%s' "
            "step='%s' value='%s'><output class='nbsl-val'>%s</output></label>"
            % (sid, esc(s["desc"] or ""), sid, fig, s["desc"] or ("p%d" % i),
               s["min"], s["max"], s["step"], s["value"], s["value"]))

def dropdown_html(fig, dd, i):
    opts = "".join("<option%s>%s</option>" % (" selected" if o == dd["value"] else "", esc(o))
                   for o in dd["options"])
    return ("<label class='nbsl'><span class='nbsl-lab'>%s</span>"
            "<select data-fig='%s' data-key='op'>%s</select></label>"
            % (esc(dd["desc"] or "mode"), fig, opts))

ANCHORS = {}
for _e in json.load(open(os.path.join(HERE, "tree.json")))["struct"]:
    if _e.get("anchor"):
        ANCHORS[_e["anchor"]] = _e

# ----------------------------------------------------------------- walker
def _prefl(nodes):
    """Rows of number boxes (or of sliders) are laid out in boxes of their own;
    unwrap them so a cluster reads as one run of fields."""
    outn = []
    for n in nodes:
        n = flat(n)
        kids = [flat(k) for k in (n.get("kids") or [])]
        if n["t"] == "box" and kids and all(k["t"] in ("num", "slider") for k in kids):
            outn += kids
        else:
            outn.append(n)
    return outn

def walk(nodes, ctx, out):
    nodes = _prefl(nodes)
    i = 0
    while i < len(nodes):
        n = flat(nodes[i])
        t = n["t"]

        # --- a figure: sliders (+ dropdown) → readout → plot image ----------
        if t in ("slider", "dropdown"):
            j, sl, dd = i, [], None
            while j < len(nodes):
                m = flat(nodes[j])
                if m["t"] == "slider": sl.append(m)
                elif m["t"] == "dropdown": dd = m
                else: break
                j += 1
            read = plot = None
            look = j
            while look < len(nodes) and look < j + 2:
                m = flat(nodes[look])
                if m["t"] != "html": break
                if is_plot(m): plot = m; look += 1; break
                if read is None: read = m
                look += 1
            if plot is not None:
                j = look
            else:
                read = None          # no picture → these were plain controls
            if plot is None and read is None:          # a plain control, not a figure
                for s_ in sl:
                    out.append("<div class='nbsliders'>%s</div>" % slider_html("ctl", s_, 0))
                if dd is not None:
                    out.append("<div class='nbsliders'>%s</div>"
                               % dropdown_html("nbdifficulty", dd, 0))
                i = j
                continue
            kind = "target" if ctx.get("in_practice") else "viz"
            fid = fig_id(ctx, kind)
            ctrl = "".join(slider_html(fid, s, k) for k, s in enumerate(sl))
            if dd is not None: ctrl += dropdown_html(fid, dd, len(sl))
            png = ""
            if plot is not None:
                m = re.search(r'src="([^"]+)"', plot["v"])
                if m: png = m.group(1)
            out.append(
                "<div class='nbfig' data-fig='%s' data-task='%s'>"
                "<div class='nbsliders'>%s</div>"
                "<div class='nbread-slot'>%s</div>"
                "<div class='nbcanvas-wrap'><canvas class='nbcanvas' width='700' height='700'></canvas>"
                "<img class='nbplot nbfallback' src='%s' alt='figure'></div></div>"
                % (fid, ctx.get("task") or "", ctrl, (read or {}).get("v", ""), png))
            i = j
            continue

        # --- typed numbers + check button -----------------------------------
        if t == "num":
            j, boxes = i, []
            while j < len(nodes) and flat(nodes[j])["t"] == "num":
                boxes.append(flat(nodes[j])); j += 1
            btn = None
            while j < len(nodes):
                m = flat(nodes[j])
                if m["t"] == "button": btn = m; j += 1; break
                if m["t"] == "out": break
                j += 1
            if j < len(nodes) and flat(nodes[j])["t"] == "out": j += 1
            task = ctx.get("task") or ""
            fields = "".join(
                "<label class='nbnum'><span>%s</span>"
                "<input type='number' step='any' data-task='%s' data-key='k%d'></label>"
                % (esc(b["desc"] or ""), task, k) for k, b in enumerate(boxes))
            ctx["task"] = None
            out.append("<div class='nbans' data-task='%s' data-kind='num'>"
                       "<div class='nbfields'>%s</div>"
                       "<div class='nbcheck'><button class='sc-btn' data-check='%s'>%s</button></div>"
                       "<div class='nbfeedback'></div></div>"
                       % (task, fields, task, esc((btn or {}).get("label") or "Check answer")))
            i = j
            continue

        # --- one of several options ------------------------------------------
        if t == "radio":
            task = ctx.get("task") or ctx.get("extra_task") or ""
            j = i + 1
            btn = None
            while j < len(nodes):
                m = flat(nodes[j])
                if m["t"] == "button": btn = m; j += 1; break
                if m["t"] == "out": break
                j += 1
            if j < len(nodes) and flat(nodes[j])["t"] == "out": j += 1
            name = "r-%s-%d" % (task or "x", i)
            opts = "".join(
                "<label class='nbopt'><input type='radio' name='%s' data-task='%s' value='%d'>"
                "<span>%s</span></label>" % (name, task, k, esc(o))
                for k, o in enumerate(n["options"]))
            ctx["task"] = None
            out.append("<div class='nbans' data-task='%s' data-kind='choice'>"
                       "<div class='nbopts'>%s</div>"
                       "<div class='nbcheck'><button class='sc-btn' data-check='%s'>%s</button></div>"
                       "<div class='nbfeedback'></div></div>"
                       % (task, opts, task, esc((btn or {}).get("label") or "Check answer")))
            i = j
            continue

        # --- the optional code route ------------------------------------------
        if t == "textarea":
            j = i + 1
            while j < len(nodes) and flat(nodes[j])["t"] in ("button", "out"):
                j += 1
            out.append("<div class='nbcode'><pre class='nbstub'>%s</pre>"
                       "<div class='nbink nbcode-note'>The code route needs a Python kernel — "
                       "open this chapter in the notebook version to run it. "
                       "Everything else on this page works without one.</div></div>"
                       % esc(n.get("value") or ""))
            i = j
            continue

        # --- reveal the solution ----------------------------------------------
        if t == "button" and "sol-btn" in (n.get("cls") or []):
            j = i + 1
            note = body = ""
            if j < len(nodes) and flat(nodes[j])["t"] == "html":
                note = flat(nodes[j])["v"]; j += 1
            if j < len(nodes) and flat(nodes[j])["t"] == "html":
                body = flat(nodes[j])["v"]; j += 1
            out.append("<details class='nbsol' data-task='%s'><summary class='sol-btn'>%s</summary>"
                       "%s<div class='nbsol-body'>%s</div></details>"
                       % (ctx.get("task") or "", esc(n.get("label") or "Solution"), note, body))
            i = j
            continue

        # --- plain content -----------------------------------------------------
        if t == "html":
            v = n.get("v") or ""
            m = re.match(r'\s*<span id="([a-zA-Z0-9_\-]+)__', v)
            if m:                       # a chapter anchor: it also says which task follows
                a = m.group(1)
                ctx["anchor"] = a
                if a in ANCHORS:          # a practice anchor has no entry of its own
                    ctx["task"] = ANCHORS[a].get("task")
                out.append("<span class='nbanchor' id='%s'></span>" % a)
                i += 1
                continue
            if not is_feed(n):
                out.append(v)
            i += 1
            continue

        if t == "acc":
            for k, title in enumerate(n["titles"]):
                cls = " ".join(n.get("cls") or [])
                kid = n["kids"][k]
                sub = dict(ctx)
                task = ""
                if "acc-practice" in cls or "Practice" in title:
                    sub["in_practice"] = True
                if "acc-chapter" in cls and "Practice" not in title and "code" not in title:
                    task = ctx.get("task") or ""
                out.append("<details class='nbacc %s'%s data-lockfor='%s'>"
                           "<summary class='acc-pill'>%s</summary>"
                           "<div class='nbacc-body'>"
                           % (cls, " open" if n.get("open") else "", task, esc(title)))
                walk([kid], sub, out)
                out.append("</div></details>")
            i += 1
            continue

        if t == "box":
            kids = n.get("kids") or []
            cls = " ".join(n.get("cls") or [])
            sub = dict(ctx)
            out.append("<div class='nb%s %s'>" % ("hbox" if n.get("dir") == "h" else "vbox", cls))
            walk(kids, sub, out)
            out.append("</div>")
            i += 1
            continue

        if t == "button":
            lab = n.get("label") or ""
            if "nb-runall" in (n.get("cls") or []):
                i += 1; continue                      # nothing to run here
            out.append("<button class='sc-btn nbplain'>%s</button>" % esc(lab))
            i += 1
            continue

        i += 1
    return out

# --------------------------------------------------------------- assemble
# which chapter/task a subtree belongs to: the anchors come in front of each
# chapter, and _STRUCT says which task hangs on it
def top_walk(nodes):
    out, ctx = [], {"anchor": None, "task": None}
    for n in nodes:
        n = flat(n)
        if n["t"] == "html":
            m = re.match(r'\s*<span id="([a-zA-Z0-9_\-]+)__', n.get("v") or "")
            if m:
                a = m.group(1)
                ctx = {"anchor": a, "task": (ANCHORS.get(a) or {}).get("task")}
                out.append("<span class='nbanchor' id='%s'></span>" % a)
                continue
        walk([n], ctx, out)
    return out

parts = []
for top in D["tree"]:
    if top["t"].startswith("?"):          # Javascript payloads of the notebook
        continue
    if is_feed(top) or (top["t"] == "box" and top.get("kids") and is_feed(flat(top["kids"][0]))):
        continue
    parts += top_walk([top])

BODY = "\n".join(parts)

TITLE = ("<div class='nbtitle'><div class='nbtitle-card'>"
         "<div class='nbtitle-h'>Complex Numbers</div>"
         "<div class='nbtitle-s'>Principles of Biophysics &amp; Computational methods "
         "&mdash; section 1.2</div></div>"
         "<div class='nbtitle-sub'>From one impossible equation to rotation in the plane</div>"
         "<div class='nbtitle-note'>This is the kernel-free HTML edition: every exercise, "
         "slider and plot works in the browser alone. The optional code exercises need the "
         "notebook version.</div></div>")

def _rail(panel):
    """_prog_html() is <div class=nbfeed>RAIL</div> + the inline strip; the page
    mounts the rail alone."""
    head = panel.split('<div class="nbprog"')[0]
    i = head.find(">") + 1
    body = head[i:]
    if body.rstrip().endswith("</div>"):
        body = body.rstrip()[: -len("</div>")]
    return body

def read(name):
    return open(os.path.join(HERE, name), encoding="utf-8").read()

page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Complex Numbers &mdash; DigiChemJN</title>
%(css)s
<style>%(extra)s</style>
</head>
<body class="nbhtml">
<div id="nbpanel-root" class="nbpanel-host ready">%(rail)s</div>
%(title)s
<main class="nbmain">
%(body)s
</main>
<script>window.NBDATA = %(data)s;</script>
<script>%(plots)s</script>
<script>%(checks)s</script>
<script>%(runtime)s</script>
</body></html>
""" % {"css": D["css"],
       "extra": read("extra.css"),
       "rail": _rail(D["panel"]),
       "title": TITLE,
       "body": BODY,
       "data": json.dumps({"id": NBID, "notebook": D["notebook"], "tv": D["tv"],
                           "tasks": D["tasks"], "struct": D["struct"],
                           "frames": D["frames"], "labels": D["labels"],
                           "quiz": D["quiz"]}, ensure_ascii=False),
       "plots": read("plots.js"), "checks": read("checks.js"), "runtime": read("runtime.js")}

out = os.path.join(HERE, "Complex_Numbers.html")
open(out, "w", encoding="utf-8").write(page)
print("wrote %s — %.1f KB, %d figures, %d answer blocks"
      % (out, len(page) / 1024.0, BODY.count("class='nbfig'"), BODY.count("class='nbans'")))
