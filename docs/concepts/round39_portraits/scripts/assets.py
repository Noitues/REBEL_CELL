"""Round 31: pre-render the locked slice tiles (round 17 kit, V2 strong tiers) and wheels into scratch/assets.

python assets.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib17"))
OUT = os.path.dirname(HERE)
CACHE = os.path.join(OUT, "scratch", "assets")

import slicekit as K

K.TIER_STYLE = "a"
K.TIER_STRENGTH = 2

TILES = [
    ("EXPLOIT", 6, 1), ("EXPLOIT", 8, 2), ("EXPLOIT", 10, 3),
    ("FIREWALL", 5, 1), ("FIREWALL", 7, 2), ("PATCH", 3, 1), ("PATCH", 4, 2),
    ("VIRUS", 3, 1), ("PROXY", 4, 1), ("ZERO-DAY", 12, 1), ("ZERO-DAY", 15, 2), ("SANDBOX", 8, 1),
    ("NULL", None, 1), ("TROJAN", 1, 1),
]
WHEEL_A = [("EXPLOIT", 6, 1, None), ("FIREWALL", 5, 1, None), ("PROXY", 4, 1, None),
           ("VIRUS", 3, 1, None), ("ZERO-DAY", 12, 1, None), ("NULL", None, 1, None)]
WHEEL_B = [("EXPLOIT", 8, 2, None), ("FIREWALL", 5, 1, None), ("PROXY", 4, 1, None),
           ("VIRUS", 3, 1, None), ("ZERO-DAY", 12, 1, None), ("NULL", None, 1, None)]


def name(p, v, k):
    return "tile_%s_%s_%d.png" % (p.replace("-", ""), v, k)


def main():
    os.makedirs(CACHE, exist_ok=True)
    for p, v, k in TILES:
        fn = os.path.join(CACHE, name(p, v, k))
        if not os.path.exists(fn):
            K.tile(p, v, t=0.45, tier=k, scale=0.5, seed=len(p) + k).save(fn)
            print(fn, flush=True)
    for key, sl in (("wheel_a", WHEEL_A), ("wheel_b", WHEEL_B)):
        fn = os.path.join(CACHE, key + ".png")
        if not os.path.exists(fn):
            K.wheel(sl, t=0.45, r_px=170).save(fn)
            print(fn, flush=True)


if __name__ == "__main__":
    main()


BIG = [("EXPLOIT", 6, 1), ("EXPLOIT", 8, 2), ("EXPLOIT", 10, 3), ("SANDBOX", 8, 1), ("PATCH", 4, 2), ("ZERODAY", 15, 2), ("TROJAN", 1, 1), ("NULL", None, 1)]
WHEEL_C = [("EXPLOIT", 8, 2, None), ("FIREWALL", 7, 2, None), ("PROXY", 4, 1, None),
           ("VIRUS", 3, 1, None), ("ZERO-DAY", 12, 1, None), ("NULL", None, 1, None)]


def big():
    os.makedirs(CACHE, exist_ok=True)
    for p, v, k in BIG:
        prog = "ZERO-DAY" if p == "ZERODAY" else p
        fn = os.path.join(CACHE, "big_" + name(prog, v, k))
        if not os.path.exists(fn):
            K.tile(prog, v, t=0.45, tier=k, scale=0.8, seed=len(p) + k).save(fn)
            print(fn, flush=True)
    fn = os.path.join(CACHE, "wheel_c.png")
    if not os.path.exists(fn):
        K.wheel(WHEEL_C, t=0.45, r_px=280).save(fn)
        print(fn, flush=True)


if __name__ == "__main__":
    big()
