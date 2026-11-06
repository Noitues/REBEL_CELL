"""Normalise script encodings (strip BOM, LF endings) and report folder size."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
for f in os.listdir(HERE):
    if f.endswith(".py"):
        p = os.path.join(HERE, f)
        b = open(p, "rb").read()
        nb = b.lstrip(b"\xef\xbb\xbf").replace(b"\r\n", b"\n")
        if nb != b:
            open(p, "wb").write(nb)
            print("normalised", f)
root = os.path.dirname(HERE)
tot = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(root) for f in fs)
print("folder MB %.1f" % (tot / 1e6))
