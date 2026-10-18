"""Aurelian HQ: pack the finals (scratch/final -> ../H_*_v1.png, ../plates/, ../H_*_v1_values.json, ../H_*_v1_rooms.json).

python finals_pack.py
"""
import json
import os
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aur_env  # noqa: E402

aur_env.setup()
import hq_cam as CR  # noqa: E402
import hq_graph as G  # noqa: E402

NAMES = ["H_overview", "H_decision", "H_decision_cavea", "H_hover"]
SRC = os.path.join(aur_env.SCR, "final")
DST = aur_env.ROOT
os.makedirs(os.path.join(DST, "plates"), exist_ok=True)
vals = json.load(open(os.path.join(SRC, "values.json")))
stills = CR.stills()
for n in NAMES:
    shutil.copy(os.path.join(SRC, n + ".png"), os.path.join(DST, n + "_v1.png"))
    shutil.copy(os.path.join(SRC, n + "_plate.png"), os.path.join(DST, "plates", n + "_v1_plate.png"))
    json.dump(vals[n], open(os.path.join(DST, n + "_v1_values.json"), "w"), indent=1)
    pose, shot = stills[n]
    rooms = {}
    for i in G.NODES:
        if i == "start":
            continue
        q = [pose.proj(p, w=2560) for p in G.room_front(i)]
        rooms[i] = dict(world=[[round(v, 2) for v in p] for p in G.room_front(i)],
                        px=[[round(v[0], 1), round(v[1], 1)] if v else None for v in q])
    json.dump(dict(res=[2560, 1440], cam=n, rooms=rooms), open(os.path.join(DST, n + "_v1_rooms.json"), "w"), indent=1)
    print("packed", n)
