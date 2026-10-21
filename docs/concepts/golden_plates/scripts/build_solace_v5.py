"""Promote the Solace HQ v5 plates (lime helix, park + plinth; designer 2026-10-21) to the golden set.
python build_solace_v5.py   (CPU only; reads the v5 final plates and Object Index passes from D:/rc_scratch/solace_v1/hq_v5)"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_plate as MP  # noqa: E402

GP = os.path.normpath(os.path.join(HERE, ".."))
C = os.path.normpath(os.path.join(GP, ".."))
HQ = os.path.join(C, "solace_vertical", "hq")
SCR = "D:/rc_scratch/solace_v1/hq_v5/"
OV = json.load(open(SCR + "scratch/ov_stills.json", encoding="utf-8"))
ACC = [{"check": "landmark_ratio", "note": "v5 lime helix in the park: 3.20x overview / 3.21x decision above 2.0, pre-accepted (designer approved the plate as rendered, 2026-10-21)"}]
for view in ("overview", "decision"):
    fr = "H_" + view
    p = OV[fr]["pose"]
    cam = MP.pose_from_loc_tgt(p["loc"], p["tgt"], p["lens"], p["shift_x"], p["shift_y"])
    cam["yaw"], cam["pitch"], cam["dist"] = p["yaw"], p["pitch"], p["dist"]
    cam["zoom_job"] = OV[fr].get("zoom")
    e = dict(stem="hq_solace_" + view, kind="hq", view=view, corp="solace", beauty=os.path.join(HQ, "H_%s_v5.png" % view), look="aaa2",
             exempt={"hover_cut": False, "red_seq": False, "flash": False}, camera=cam, accepted=ACC,
             index=SCR + "out/bl_stills/%s_index.npy" % fr,
             source=dict(final="solace_vertical/hq/H_%s_v5.png" % view, commit="v5",
                         pose="D:/rc_scratch/solace_v1/hq_v5/scratch/ov_stills.json[%s] (same cameras as v4; hq_cam unchanged)" % fr,
                         index_pass="solace_v1/hq_v5/out/bl_stills/%s_index.npy (the final run's own Object Index pass; 2560 x 1440, 64 spp)" % fr,
                         yaw_convention="rig: 0 = north, clockwise; loc/tgt in Blender world BU (x east, y north, z up)"),
             pending=["layout_seed, run id, anim_t, fixture run_graph and inputs hashes: no derive run exists for this render"])
    r = MP.build_plate(e, GP)
    v = r["vals"]
    print(e["stem"], r["res"], "med %.4f u10 %.3f o85 %.4f ratio %s mean %s peak %s id %s align %s" % (
        v["median"], v["under_010"], v["over_085"], MP.r4(v["ratio_median"]), MP.r4(v["ratio_mean"]), MP.r4(v["ratio_peak"]), r["has_id"], MP.r4(r["align"])))
    print(json.dumps(v["checks"]["status"]), json.dumps(v["composition"]))
