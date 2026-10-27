"""E33 A1 (Python): the STATIC reading version keeps the other language in data-nbrw-o and the window's cover and
Lab's timeline in <script type=application/json data-nbrw-put> (toolkit _nbrw_bi enc, _nbrw_put). Where our script
runs, _NBRW_REHYD rebuilds the v1.78 markup (py_e33.py R1: equal element for element in a real page). Tests that read
the run's HTML as a string (py_e26_short, …) read it through rebuild(h): the same rebuild, in Python. Not a test
module (run.py skips files starting with "_")."""
import re, json, html as _h

_PUT = re.compile(r"<script type='application/json' data-nbrw-put>(.*?)</script>", re.S)
_ONE = re.compile(r"<(\w+)((?:\s[^<>]*?)?)\sdata-nbrw-o='([^']*)'([^<>]*)>")

def _close(h, tag, i):
    """index after the </tag> that closes the element whose start tag ends at i."""
    depth, rx = 1, re.compile(r"<(/?)%s\b[^>]*>" % tag)
    for m in rx.finditer(h, i):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return m.start(), m.end()
    return None

def rebuild(h):
    h = _PUT.sub(lambda m: json.loads(m.group(1)), h)
    def unstyle(m):
        t = m.group(0); o = re.search(r"\sdata-nbrw-s='([^']*)'", t)
        t = t[:o.start()] + t[o.end():]
        v = _h.unescape(o.group(1))
        return re.sub(r"""\sstyle=(["'])(.*?)\1""", (lambda _m: ' style="%s"' % v.replace('"', "&quot;")) if v else "", t, count=1)
    h = re.sub(r"<[^<>]*\sdata-nbrw-s='[^']*'[^<>]*>", unstyle, h)
    out, pos = [], 0
    while True:
        m = _ONE.search(h, pos)
        if not m:
            out.append(h[pos:]); break
        tag, pre, o, post = m.group(1), m.group(2), _h.unescape(m.group(3)), m.group(4)
        c = _close(h, tag, m.end())
        if not c:
            out.append(h[pos:]); break
        lm = re.search(r"data-nbrw-l='(\w\w)'", pre)
        run = lm.group(1) if lm else "en"; oth = "de" if run == "en" else "en"
        t = " data-nbrw-t" in pre
        inner = h[m.end():c[0]]
        me = "<%s%s%s>%s</%s>" % (tag, pre, post, inner, tag)
        ot = "<%s%s%s%s>%s</%s>" % (tag, pre.replace("data-nbrw-l='%s'" % run, "data-nbrw-l='%s'" % oth), post,
                                     " hidden" if t else "", o, tag)
        out.append(h[pos:m.start()]); out.append(ot + me if (not t and oth == "en") else me + ot)
        pos = c[1]
    return "".join(out)
