"""Round 24: render the four corp boss wheels (round 18 D4 corp code, phase 1, corp tier III) for the
combat composites. Writes ../../scratch/wheels/<corp>_boss.png + .json (centre, meta, ss)."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DST = os.path.join(HERE, "..", "..", "scratch", "wheels")
os.makedirs(DST, exist_ok=True)
import d4corp as D
import specs14 as S

for corp in (sys.argv[1:] or ["solace", "halcyon", "orbital", "rebel_cell"]):
    spec, meta_b = S.boss(corp, 1)
    spec["corp_tier"] = 3
    mx = spec["hp"][1]
    spec["hp"] = (int(mx * 0.85), mx)
    spec["pred"] = 8
    im, c, meta = D.render(spec, ss=2, hp_number=False)
    im.save(os.path.join(DST, corp + "_boss.png"))
    json.dump(dict(c=c, meta=meta, ss=2, name=meta_b["name"], hp=spec["hp"]), open(os.path.join(DST, corp + "_boss.json"), "w"))
    print("boss wheel", corp, im.size, flush=True)
