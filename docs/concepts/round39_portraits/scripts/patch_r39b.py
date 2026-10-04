"""Round 39 patch 2: Breaker hood no longer wraps under the chin (visor only); Ghost headband sits tight
on the wrap (it read as a helmet ring) and the lower fold that read as a chin strap is gone.

python patch_r39b.py
"""
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bust_rig.py")
s = open(P, encoding="utf8").read()
assert "chin cut" not in s, "already patched"
R = [
    ('        boolean(hood, box((0, -1.2, -0.6), (1.75, 1.3, 2.8), rot=(math.radians(-14), 0, 0)))',
     '        boolean(hood, box((0, -1.2, -0.6), (1.75, 1.3, 2.8), rot=(math.radians(-14), 0, 0)))\n'
     '        boolean(hood, box((0, -0.55, -1.15), (3.0, 1.1, 0.9)))  # chin cut'),
    ('        for z_, t_ in ((-0.35, 12), (0.5, -10)):', '        for z_, t_ in ((0.5, -10),):'),
    ('            hb = torus(wid + 0.1, 0.06, (0, 0.02, 0.36), rot=(math.radians(-6), 0, 0), maj=14)\n            hb.scale = (1, 1.12, 1)',
     '            hb = torus(wid + 0.06, 0.055, (0, 0.02, 0.36), rot=(math.radians(-6), 0, 0), maj=14)\n            hb.scale = (1, 1.03, 1)'),
]
for a, b in R:
    assert a in s, a[:60]
    s = s.replace(a, b)
open(P, "w", encoding="utf8").write(s)
print("patched")
