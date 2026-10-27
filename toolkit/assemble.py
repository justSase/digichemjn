r"""Ladeteil — puts toolkit/chapter_template.py back together at BUILD time.

2026-09-28 (S · Aufteilung, Hauptwerkstatt). The toolkit used to be one file of
~13 000 lines, so three workshops could not work on it at once. The CSS and the
two big page scripts now live in their own files:

    toolkit/css/NN-*.css   the stylesheet of inject_style()   (Werkstatt CSS)
    toolkit/js/01-jump.js  the page script of inject_jump()    (Werkstatt JS)
    toolkit/js/1N-rail-*.js the panel script of nbrail_js()    (Werkstatt JS)

chapter_template.py keeps a marker line where each file goes:
    /*@include css/01-base.css*/      //@include js/10-rail-host.js
template() replaces every marker line by the file's text, verbatim, and returns
the ONE text that is embedded in the notebook — exactly what chapter_template.py
was before the split (proved: Complex v1.16 byte-identical, sha 015c3df5…).
The notebook stays ONE file that runs everywhere; nothing is read at run time.

RULES FOR THE PIECES (they are cut out of Python string literals, verbatim):
  * css/*.css is the body of a NORMAL string formatted with `% DESIGN`:
    write %% for a literal percent sign, %(name)s takes a value from DESIGN,
    and a backslash is a Python escape (write \\ for one backslash).
  * js/*.js is the body of a RAW string: verbatim, but never three double
    quotes in a row. __JUMPV__ / __NBRAILV__ become TOOLKIT_VERSION.
  * The ORDER is the order of the markers (the cascade and the script depend on
    it). The numbers in the names only sort the folder. A piece is not a whole
    unit on its own: the rail pieces are one function body cut in ten.
  * A new file must get a marker line, a removed file must lose it — template()
    refuses a file without a marker, a marker without a file, and a piece that
    does not end in a newline.
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
_MARK = re.compile(r"^(?:/\*@include ([\w./-]+)\*/|//@include ([\w./-]+))\n", re.M)


def _read(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as f:
        return f.read()


def template(minify=True):
    src = _read("chapter_template.py")
    used = []

    def put(m):
        rel = m.group(1) or m.group(2)
        text = _read(rel)
        if not text.endswith("\n"):
            raise SystemExit("assemble: %s does not end in a newline" % rel)
        used.append(rel)
        return text

    out = _MARK.sub(put, src)
    if re.search(r"^[ \t]*(?:/\*|//)[ \t]*@include", out, re.M):
        raise SystemExit("assemble: a marker line was not understood (indented? typo?)")
    have = sorted("%s/%s" % (d, f) for d in ("css", "js")
                  for f in os.listdir(os.path.join(HERE, d))
                  if f.endswith("." + d))
    if sorted(used) != have or len(used) != len(set(used)):
        raise SystemExit("assemble: markers %s do not match the files %s"
                         % (sorted(used), have))
    return _minify(out) if minify else out


# 2026-09-29 (Paket 21c, Applikation) — THE NOTEBOOK CARRIES MINIFIED CSS AND
# JS; THE SOURCES STAY AS THEY ARE. Measured on v1.29 (rcssmin/rjsmin): CSS
# 399 → 225 KB, JS 371 → 152 KB. Only the built text is minified, here, after
# the pieces are put in — toolkit/css and toolkit/js are what people read and
# patch. Each block is minified as a whole (the ten rail pieces are one
# function body, not ten scripts).
#   * CSS is the body of a Python string formatted with `% DESIGN`, so the
#     Python layer is taken off first (%(name)s, %%, \\), the CSS is
#     minified, and the layer is put back. Any other `%` or backslash escape
#     stops the build instead of being guessed at.
#   * JS is the body of a raw string: verbatim JS, minified as it is.
# rcssmin/rjsmin are regex tokenizers (no parser): comments and blank space go,
# strings, regex and template literals stay, and a line break stays where JS's
# automatic semicolons need it.
_CSS_BLOCK = re.compile(r'(css = """\n<style[^>]*>)((?:(?!""").)*?)(</style>""" % DESIGN)', re.S)
_JS_BLOCK = re.compile(r'(r"""\n)((?:(?!""").)*?)(\n\s*"""\.replace\("__(?:JUMPV|NBLOADV|NBRAILV)__")', re.S)


def _min_css(body):
    import rcssmin
    ph = {}
    def keep(m):
        ph["NBPH%dHPBN" % len(ph)] = m.group(0)
        return "NBPH%dHPBN" % (len(ph) - 1)
    t = re.sub(r"%\(\w+\)s", keep, body).replace("%%", "\x00")
    if "%" in t or "\x00".join(re.split(r"\\\\", t)).count("\\"):
        raise SystemExit("assemble: CSS has a % or a backslash escape the minifier does not know")
    t = t.replace("\\\\", "\\").replace("\x00", "%")
    t = rcssmin.cssmin(t)
    t = t.replace("\\", "\\\\").replace("%", "%%")
    for k, v in ph.items():
        t = t.replace(k, v)
    return t


def _min_js(body):
    import rjsmin
    return rjsmin.jsmin(body)


def _minify(src):
    n = [0, 0]
    def css(m):
        n[0] += 1
        return m.group(1) + _min_css(m.group(2)) + m.group(3)
    def js(m):
        n[1] += 1
        return m.group(1) + _min_js(m.group(2)) + m.group(3)
    out = _JS_BLOCK.sub(js, _CSS_BLOCK.sub(css, src))
    if n != [1, 3]:
        raise SystemExit("assemble: expected 1 CSS and 3 JS blocks to minify, found %s" % n)
    for m in list(_CSS_BLOCK.finditer(out)) + list(_JS_BLOCK.finditer(out)):
        if '"""' in m.group(2) or m.group(2).endswith("\\"):
            raise SystemExit("assemble: a minified block would end its Python string")
    return out


if __name__ == "__main__":
    import hashlib, sys
    t = template()
    print("assembled %d bytes, sha256 %s" % (len(t.encode()), hashlib.sha256(t.encode()).hexdigest()[:16]))
