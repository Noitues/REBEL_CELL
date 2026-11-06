"""Exports the plates hero facades (p3_look.pick_heroes) and sign walls (p2_signs.signs) as world-space rects to content/look/city_facades.tres (a CityFacadeSet).
Walls: kind 0 = facade facing +Z (u along world x), 1 = facing +X (u along world z); plane = the fixed coordinate; u0..u1 along the wall, v0..v1 world height.
usage: python bake_facades.py <out.tres>   Written as a file (no python from stdin)."""
import json
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, "D:/rc_art/art-pass/docs/concepts/tide_raid/P3_plates/scripts")
import numpy as np
import p1lib as L
import p1_comp as C
import p2_signs as S2
import p3_look as P3

COLS = [(1.0, 0.42, 0.10), (0.80, 0.93, 1.0), (1.0, 0.42, 0.10), (0.12, 0.85, 0.62), (0.80, 0.93, 1.0), (1.0, 0.30, 0.22)]


def f(x):
    return round(float(x), 3)


geo = dict(np.load(L.WORK + "geo.npz"))
Pw = np.load(L.WORK + C.REC)["P"]
sg = S2.signs(geo, Pw)
heroes = P3.pick_heroes(geo, Pw)
seed = 3
signs = []
for i, w in enumerate(sg["walls"]):
    typ = (i + seed) % 4
    wu = w["u1"] - w["u0"]
    wv = w["v1"] - w["v0"]
    sw = min(wu * 0.85, 13.0) if typ != 3 else min(wu * 0.35, 3.2)
    sh = min(wv * 0.36, 14.0) if typ != 3 else min(wv * 0.62, 30.0)
    uc = (w["u0"] + w["u1"]) / 2
    vc = w["v0"] + wv * (0.62 if typ != 3 else 0.5)
    col = COLS[(i * 5 + seed) % len(COLS)]
    hero = bool(sg["hero"] and abs(sg["hero"]["cx"] - w["cx"]) < 1e-3 and abs(sg["hero"]["cy"] - w["cy"]) < 1e-3)
    signs.append(dict(kind=0 if w["kind"] == "Z" else 1, plane=f(w["plane"]), u0=f(w["u0"]), u1=f(w["u1"]), v0=f(w["v0"]), v1=f(w["v1"]), uc=f(uc), vc=f(vc), sw=f(sw), sh=f(sh), typ=typ, idx=i,
                      color=[f(c) for c in col], hero=hero))
hs = []
for i, w in enumerate(heroes):
    hs.append(dict(kind=0 if w["kind"] == "Z" else 1, plane=f(w["plane"]), u0=f(w["u0"]), u1=f(w["u1"]), v0=f(w["v0"]), v1=f(w["v1"]), idx=i))


def dstr(d):
    parts = []
    for k, v in d.items():
        if isinstance(v, list):
            v = "Color(%s, %s, %s, 1)" % tuple(v)
        elif isinstance(v, bool):
            v = "true" if v else "false"
        parts.append('"%s": %s' % (k, v))
    return "{" + ", ".join(parts) + "}"


with open(sys.argv[1], "w", newline="\n") as fh:
    fh.write('[gd_resource type="Resource" script_class="CityFacadeSet" load_steps=2 format=3]\n\n')
    fh.write('[ext_resource type="Script" path="res://scripts/city3d/city_facade_set.gd" id="1"]\n\n[resource]\nscript = ExtResource("1")\n')
    fh.write("seed = 7\n")
    fh.write("heroes = Array[Dictionary]([" + ", ".join(dstr(d) for d in hs) + "])\n")
    fh.write("signs = Array[Dictionary]([" + ", ".join(dstr(d) for d in signs) + "])\n")
print("heroes", len(hs), "signs", len(signs), "hero sign", [s["idx"] for s in signs if s["hero"]])
