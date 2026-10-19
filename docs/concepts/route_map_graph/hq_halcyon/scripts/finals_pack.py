"""Halcyon v3: the values (golden-plate measures) and rooms json for the packed finals, plus the occluder counts.

python finals_pack.py        after `python hq_compose.py stills` has written ../H_*_v3.png and ../plates/H_*_v3_plate.png
Writes ../H_*_v3_values.json and ../H_*_v3_rooms.json (the Aurelian layout: world + px of each room's front quad).
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "golden_plates", "scripts"))
sys.dont_write_bytecode = True
import gcheck as GC  # noqa: E402
import hq_cam as CR  # noqa: E402
import hq_graph as G  # noqa: E402

ROOT = os.path.dirname(HERE)
BIG = "D:/rc_scratch/hq_fix/halcyon"
STEM = {"H_overview": "hq_halcyon_overview", "H_decision_E": "hq_halcyon_decision"}
stills = CR.stills()
for n in ("H_overview", "H_decision_S", "H_decision_E", "H_hover_S", "H_hover_E"):
    plate = os.path.join(ROOT, "plates", n + "_v3_plate.png")
    if not os.path.exists(plate):
        continue
    if n in STEM:
        r = GC.check(STEM[n], plate, BIG + "/bl_stills/%s_index.npy" % n, BIG + "/chk")
        v = r["vals"]
    else:
        import make_plate as MP
        import numpy as np
        from PIL import Image
        L = MP.luma(np.asarray(Image.open(plate).convert("RGB"), np.float32) / 255.0)
        v = dict(median=float((np.median(L))), under_010=float((L < 0.10).mean()), over_085=float((L > 0.85).mean()))
    op = os.path.join(BIG, "occ_%s.json" % n)
    if os.path.exists(op):
        o = json.load(open(op))
        v["occluders"] = dict(rooms_in_frame=o["rooms"], rooms_hit=o["rooms_hit"], buildings_above_stub=o["buildings"],
                              band_occluders=o.get("band_occluders"), pad_px=12, per_room=o["per_room"])
    json.dump(v, open(os.path.join(ROOT, n + "_v3_values.json"), "w"), indent=1, default=float)
    pose = stills[n][0]
    rooms = {}
    for i in G.NODES:
        if i == "start":
            continue
        q = [pose.proj(p, w=2560) for p in G.room_front(i)]
        rooms[i] = dict(world=[[round(c, 2) for c in p] for p in G.room_front(i)],
                        px=[[round(c[0], 1), round(c[1], 1)] if c else None for c in q])
    json.dump(dict(res=[2560, 1440], cam=n, rooms=rooms), open(os.path.join(ROOT, n + "_v3_rooms.json"), "w"), indent=1)
    print("packed", n)
