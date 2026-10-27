"""Pack the source tree into notebooks/quellen-buendel.txt — and unpack it.

    python3 pack_bundle.py pack   <tree> <bundle.txt>
    python3 pack_bundle.py unpack <bundle.txt> <tree>

2026-09-25h — THE RULE IS CODE NOW. Until 25g it lived only as a paragraph in
the chronicle, and the one time it was re-typed it threw away six hand-written
sources. It asks WHAT a file is, not where it lies:
  out: .pyc .png .zip .log .ipynb .html   (built or binary)
  out: .json of 100 KB or more            (derived blobs; the 266-byte config stays)
  out: anything over 4 MB
  out: dist/ at the top (E36, 2026-10-19: the build's output A — hull and content packages)
Paths are sorted; each file is preceded by  \\n===DIGICHEMJN-DATEI::<path>===\\n .
Proof of the rule: packing the 25g tree reproduces the 25g bundle byte for byte
(sha256 6bbb00e043448d05…)."""
import os, re, sys
SEP = "\n===DIGICHEMJN-DATEI::%s===\n"
OUT_EXT = {".pyc", ".png", ".zip", ".log", ".ipynb", ".html"}
def wanted(path, size):
    ext = os.path.splitext(path)[1].lower()
    if ext in OUT_EXT: return False
    if ext == ".json" and size >= 100 * 1024: return False
    if size > 4 * 1024 * 1024: return False
    return True
def pack(tree, out):
    paths = []
    for root, dirs, files in os.walk(tree):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".ipynb_checkpoints")
                   and not (root == tree and d == "dist")]        # E36: dist/ = Bau-Ausgang (Hülle, Pakete)
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, tree).replace(os.sep, "/")
            if wanted(rel, os.path.getsize(full)): paths.append(rel)
    paths.sort()
    with open(out, "w", encoding="utf-8", newline="") as o:
        for p in paths:
            o.write(SEP % p)
            o.write(open(os.path.join(tree, p), encoding="utf-8", newline="").read())
    return paths
def unpack(bundle, tree):
    data = open(bundle, encoding="utf-8", newline="").read()
    parts = re.split(r"\n===DIGICHEMJN-DATEI::(.+?)===\n", data)
    assert parts[0] == "", "the bundle must start with a separator"
    for i in range(1, len(parts), 2):
        fp = os.path.join(tree, parts[i])
        os.makedirs(os.path.dirname(fp) or tree, exist_ok=True)
        with open(fp, "w", encoding="utf-8", newline="") as f: f.write(parts[i + 1])
    return len(parts) // 2
if __name__ == "__main__":
    cmd, a, b = sys.argv[1:4]
    n = pack(a, b) if cmd == "pack" else unpack(a, b)
    print(cmd, len(n) if isinstance(n, list) else n, "files")
