"""Does full screen actually widen the column — and does anything collapse?"""
import json, io, contextlib, asyncio
import matplotlib; matplotlib.use("Agg")
import IPython.display as ipd
CAP={"css":[]}
ipd.display=lambda *a,**k: None
nb=json.load(open("/home/claude/work/complex/Complex_Numbers_Step_by_Step.ipynb"))
src="\n".join(l for l in "".join(nb["cells"][-1]["source"]).splitlines()
              if not l.strip().startswith("%pip"))
g={"__name__":"__main__","display":lambda *a,**k:None}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src,"<mega>","exec"),g)
class RH:
    def __init__(self,v): CAP["css"].append(v)
g["IHTML"]=RH; g["Javascript"]=lambda v: None
g["inject_style"]()
css="".join(CAP["css"])
# a faithful stand-in for one rendered box: ipywidgets puts the Layout's
# max-width INLINE on the widget node, and the box's own text wrapper is capped
# at 800px by the builder
BOX = ("<div class='widget-html jupyter-widget-html' style='width:fit-content;"
       "max-width:880px;margin:0 auto'>"
       "<div class='widget-html-content'>"
       "<div class='nbbox nbbox-concept' style='margin:12px auto;padding:16px 24px;"
       "border:1px solid #d6e2ec'>"
       "<div style='max-width:800px;margin:0 auto;text-align:justify'>"
       + ("Complex numbers turn rotation into multiplication. " * 14) +
       "</div></div></div></div>")
PAGE=("<!doctype html><html><head><meta charset='utf-8'>"+css+"</head>"
      "<body style='margin:0;background:#fff'>"
      "<div class='jp-NotebookPanel jp-mod-current' style='width:100%'>"
      "<div class='jp-Notebook'><div class='jp-Cell'><div class='jp-OutputArea'>"
      + BOX + "</div></div></div></div></body></html>")
async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg=await b.new_page(viewport={"width":1920,"height":800})
        await pg.set_content(PAGE)
        await pg.wait_for_timeout(200)
        def probe():
            return pg.evaluate("""() => {
              var w = document.querySelector('.widget-html');
              var box = document.querySelector('.nbbox');
              var txt = box.firstElementChild;
              return {widget: Math.round(w.getBoundingClientRect().width),
                      box: Math.round(box.getBoundingClientRect().width),
                      text: Math.round(txt.getBoundingClientRect().width),
                      height: Math.round(box.getBoundingClientRect().height),
                      overflow: document.documentElement.scrollWidth >
                                document.documentElement.clientWidth};
            }""")
        normal = await probe()
        await pg.evaluate("() => document.body.classList.add('nbfs')")
        await pg.wait_for_timeout(120)
        full = await probe()
        print("normal:", normal)
        print("nbfs  :", full)
        errs=[]
        if full["text"] <= normal["text"]:
            errs.append("full screen does not widen the text column (%d -> %d)"
                        % (normal["text"], full["text"]))
        if full["text"] < 1200:
            errs.append("the text column is still narrow in full screen (%d px)" % full["text"])
        if full["height"] >= normal["height"]:
            errs.append("the box got TALLER in full screen (%d -> %d) — the column collapsed"
                        % (normal["height"], full["height"]))
        if full["overflow"]:
            errs.append("the page overflows horizontally in full screen")
        print("FULL SCREEN WIDTH OK" if not errs else "FAILURES:\n- " + "\n- ".join(errs))
        await b.close()
asyncio.run(main())
