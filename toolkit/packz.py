r"""E20.1 (2026-10-02, Applikation) — THE STYLESHEET AND THE SCRIPTS TRAVEL PACKED.

The mega-cell carried CSS and JS as plain string literals: 465 KB of its
704 KB (v1.58). They are text the kernel only hands on to the page, so the
build now writes each of them as zlib + base64 and the cell unpacks it when it
runs — the page gets exactly the same text as before.

    pack(src) -> (src, rows)

`src` is the finished cell (after slim). Every string literal of at least
MIN bytes whose value starts with "\n<style" or "\n(function" (the stylesheet,
the panel script, the jump script, the loading view) is replaced by

    __import__("zlib").decompress(__import__("base64").b64decode("…")).decode()

— an expression with the same value, self-contained (no helper that a cut
cell could lose). The literal's VALUE is packed (ast), not its spelling, so a
normal string with escapes and a raw string come out the same. pack() checks
itself: every packed expression is evaluated again and must equal the value it
replaced, byte for byte, and the new cell must still parse. `rows` lists
(lineno, bytes before, bytes after, sha256 of the value) for the build log.

UNPACK(src) is the reverse for the suites: it puts every packed value back as
a literal (repr), so a test that searches the stylesheet or a script for a rule
reads the text the page will get."""
import ast, base64, hashlib, re, zlib

MIN = 4000
_HEAD = ("\n<style", "\n(function")
_EXPR = '__import__("zlib").decompress(__import__("base64").b64decode("%s")).decode()'
_RE = re.compile(r'__import__\("zlib"\)\.decompress\(__import__\("base64"\)\.b64decode\("([A-Za-z0-9+/=]+)"\)\)\.decode\(\)')


def _offsets(src):
    starts, n = [0], 0
    for line in src.splitlines(keepends=True):
        n += len(line)
        starts.append(n)
    return starts


def pack(src):
    tree = ast.parse(src)
    lits = [n for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and len(n.value.encode()) >= MIN and n.value.startswith(_HEAD)]
    off = _offsets(src)
    rows, out, last = [], [], 0
    for n in sorted(lits, key=lambda n: (n.lineno, n.col_offset)):
        # col_offset counts UTF-8 bytes; the line is turned into str offsets
        a_line, b_line = src[off[n.lineno - 1]:off[n.lineno]], src[off[n.end_lineno - 1]:off[n.end_lineno]]
        a = off[n.lineno - 1] + len(a_line.encode()[:n.col_offset].decode())
        b = off[n.end_lineno - 1] + len(b_line.encode()[:n.end_col_offset].decode())
        if ast.literal_eval(src[a:b]) != n.value:
            raise SystemExit("packz: literal at line %d not found where ast says" % n.lineno)
        raw = n.value.encode()
        expr = _EXPR % base64.b64encode(zlib.compress(raw, 9)).decode()
        if eval(expr) != n.value:
            raise SystemExit("packz: packed literal at line %d does not unpack to itself" % n.lineno)
        out.append(src[last:a]); out.append(expr); last = b
        rows.append((n.lineno, len(src[a:b].encode()), len(expr.encode()),
                     hashlib.sha256(raw).hexdigest()))
    out.append(src[last:])
    new = "".join(out)
    ast.parse(new)
    return new, rows


def unpack(src):
    return _RE.sub(lambda m: repr(zlib.decompress(base64.b64decode(m.group(1))).decode()), src)


def values(src):
    """sha256 of every packed value in `src` (for the proof in the chronicle)."""
    return [hashlib.sha256(zlib.decompress(base64.b64decode(m.group(1)))).hexdigest()
            for m in _RE.finditer(src)]
