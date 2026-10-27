import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = await b.new_page()
        await pg.goto("file:///home/claude/work/portability/portability.html")
        await pg.wait_for_timeout(400)
        await pg.pdf(path="/mnt/user-data/outputs/DigiChemJN_Portability_Guide.pdf",
                     format="A4", print_background=True,
                     margin={"top":"19mm","bottom":"20mm","left":"17mm","right":"17mm"},
                     display_header_footer=True,
                     header_template="<div></div>",
                     footer_template="<div style='width:100%;font-family:sans-serif;"
                        "font-size:7pt;color:#8b98a5;padding:0 17mm;display:flex;"
                        "justify-content:space-between'><span>DigiChemJN &middot; "
                        "Portability Guide &middot; v0.9</span>"
                        "<span class='pageNumber'></span></div>")
        await b.close()
asyncio.run(main())
