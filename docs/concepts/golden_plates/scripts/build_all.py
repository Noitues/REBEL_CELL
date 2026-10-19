"""Build the 12.8 golden plate set from the renders that already exist (no Blender, no GPU).

python build_all.py            writes docs/concepts/golden_plates/*.png|json and prints a summary table
Index passes live outside the repo (D:/rc_scratch/..., *_index.npy, not committed). A plate whose pass or camera is
missing is written with what exists and listed as pending: nothing is invented.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_plate as MP  # noqa: E402

GP = os.path.normpath(os.path.join(HERE, ".."))
C = os.path.normpath(os.path.join(GP, ".."))                       # docs/concepts
RMG = os.path.join(C, "route_map_graph")
SCR = "D:/rc_scratch/"
REPO = os.path.normpath(os.path.join(C, "..", ".."))
NO_FLASH = {"hover_cut": False, "red_seq": False, "flash": False}


def git_commit(path):
    rel = os.path.relpath(path, REPO).replace("\\", "/")
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=REPO, capture_output=True).returncode == 0
    if not tracked:
        return "untracked"
    r = subprocess.run(["git", "log", "-1", "--format=%h", "--", rel], cwd=REPO, capture_output=True, text=True)
    return r.stdout.strip() or "untracked"


def hq_pose(corp_dir, frame):
    ov = json.load(open(os.path.join(RMG, corp_dir, "scratch", "ov_stills.json"), encoding="utf-8"))[frame]
    p = ov["pose"]
    cam = MP.pose_from_loc_tgt(p["loc"], p["tgt"], p["lens"], p["shift_x"], p["shift_y"])
    dy = abs((cam["yaw"] - p["yaw"] + 180) % 360 - 180)
    dp = abs(cam["pitch"] - p["pitch"])
    if dy > 0.3 or dp > 0.3:
        raise SystemExit("pose mismatch %s %s: yaw %s/%s pitch %s/%s" % (corp_dir, frame, cam["yaw"], p["yaw"], cam["pitch"], p["pitch"]))
    cam["yaw"], cam["pitch"], cam["dist"] = p["yaw"], p["pitch"], p["dist"]      # keep the job's own numbers
    cam["zoom_job"] = ov.get("zoom")
    return cam


def hq_entry(corp, view, png_rel, corp_dir, frame, index_rel, accepted=None, extra=None):
    png = os.path.join(RMG, png_rel)
    e = dict(stem="hq_%s_%s" % (corp, view), kind="hq", view=view, corp=corp, beauty=png, look="aaa2", exempt=NO_FLASH,
             camera=hq_pose(corp_dir, frame), accepted=accepted or [],
             index=(SCR + index_rel + "_index.npy") if index_rel else None,
             source=dict(final=os.path.relpath(png, C).replace("\\", "/"), commit=git_commit(png),
                         pose="route_map_graph/%s/scratch/ov_stills.json[%s] (job_stills_final_0.json holds the same pose)" % (corp_dir, frame),
                         index_pass=(index_rel + "_index.npy") if index_rel else None,
                         yaw_convention="rig: 0 = north, clockwise; loc/tgt in Blender world BU (x east, y north, z up)"),
             pending=["layout_seed, run id, anim_t, fixture run_graph and inputs hashes: no derive run exists for this render"])
    if corp == "rebel_cell":
        e["class_map"] = {3: 1}          # AD 2026-10-18: pass 3 (the MAINFRAME sign quad) is landmark, class 1
    if extra:
        e.update(extra)
    if not index_rel:
        e["pending"].append("id.png: no Object Index pass exists for this render; re-render with the pass to produce it")
    return e


def tethys_extra(png_name):
    v = json.load(open(os.path.join(RMG, "hq_tethys", png_name.replace(".png", "_values.json"))))
    return dict(extra_values={"ratio_mean": v["ratio_mean"], "ratio_peak": v["ratio_peak"]},
                extra_values_note="ratio_mean / ratio_peak copied from %s (post_tethys disc mask round the station, not id.png classes); "
                                  "ratio_median stays null until an id pass exists" % png_name.replace(".png", "_values.json"))


def entries():
    E = []
    ob = "hq_rev/"
    # Halcyon v2 (decision = variant E)
    E.append(hq_entry("halcyon", "overview", "hq_halcyon/plates/H_overview_v2_plate.png", "hq_halcyon", "H_overview",
                      ob + "halcyon/bl_stills/H_overview",
                      accepted=[{"check": "R-VAL-1", "note": "approved HQ overview plate median 0.109, pre-accepted 2026-10-18 (12.8)"}]))
    E.append(hq_entry("halcyon", "decision", "hq_halcyon/plates/H_decision_E_v2_plate.png", "hq_halcyon", "H_decision_E",
                      ob + "halcyon/bl_stills/H_decision_E"))
    # Solace v4
    sol = [{"check": "landmark_ratio", "note": "2.56x above 2.0 pre-accepted (Solace 2.8x accepted 2026-10-16, Q5; 12.8)"}]
    E.append(hq_entry("solace", "overview", "hq_solace/plates/H_overview_v4_plate.png", "hq_solace", "H_overview",
                      ob + "solace/v4/bl_stills/H_overview", accepted=sol))
    E.append(hq_entry("solace", "decision", "hq_solace/plates/H_decision_v4_plate.png", "hq_solace", "H_decision",
                      ob + "solace/v4/bl_stills/H_decision", accepted=sol))
    # Orbital v2
    E.append(hq_entry("orbital", "overview", "hq_orbital/plates/H_overview_v2_plate.png", "hq_orbital", "H_overview",
                      ob + "orbital/bl_stills/H_overview"))
    E.append(hq_entry("orbital", "decision", "hq_orbital/plates/H_decision_v2_plate.png", "hq_orbital", "H_decision",
                      ob + "orbital/bl_stills/H_decision"))
    # Meridian v3 (Gatehouse Gantry)
    E.append(hq_entry("meridian", "overview", "hq_meridian_v3/plates/H_overview_v3_plate.png", "hq_meridian_v3", "H_overview",
                      "meridian_v3/bl_stills/H_overview"))
    E.append(hq_entry("meridian", "decision", "hq_meridian_v3/plates/H_decision_v3_plate.png", "hq_meridian_v3", "H_decision",
                      "meridian_v3/bl_stills/H_decision"))
    # Rebel Cell v3
    E.append(hq_entry("rebel_cell", "overview", "hq_rebel_cell/plates/H_overview_v3_plate.png", "hq_rebel_cell", "H_overview",
                      ob + "rebel_cell/v3/bl_stills/H_overview"))
    E.append(hq_entry("rebel_cell", "decision", "hq_rebel_cell/plates/H_decision_v3_plate.png", "hq_rebel_cell", "H_decision",
                      ob + "rebel_cell/v3/bl_stills/H_decision"))
    # Tethys v2: no index pass (the Tethys pipeline writes rgb / emit / z only). Cameras from the preset + render logs.
    t_acc = [{"check": "landmark_ratio", "note": "peak 3.7x above 2.0 (overview) pre-accepted 2026-10-18 (12.8)"}]
    ov = MP.pose_from_loc_tgt([-233.0, 180.0, 161.0], [-329.0, 275.0, 0.0], 30.0, 0.0, 0.0)
    # tgt refined by fitting tethys/final4/t_over_aaa_rooms.json (28 room anchors, mean error 0.8 px); preset: lens 30, layout yaw 135 -> rig -45,
    # pitch 50, dist 210, sy 0. loc = tgt - fwd * dist.
    yaw, pit, dist = -45.0, 50.0, 210.0
    tgt = [-328.75, 275.25, 0.0]
    fx = math.sin(math.radians(yaw)) * math.cos(math.radians(pit))
    fy = math.cos(math.radians(yaw)) * math.cos(math.radians(pit))
    fz = -math.sin(math.radians(pit))
    ov = dict(loc=[tgt[0] - fx * dist, tgt[1] - fy * dist, tgt[2] - fz * dist], tgt=tgt, yaw=yaw, pitch=pit, dist=dist, lens=30.0,
              shift_x=0.0, shift_y=0.0,
              loc_note="tgt fitted to 28 room anchors of D:/rc_scratch/tethys/final4/t_over_aaa_rooms.json (+-0.25 BU); render log: loc (-233,180,161) tgt (-329,275,0)")
    yaw, pit, dist = 90.0 - 118.0, 40.0, 142.0
    tgt = [-340.0, 288.0, 0.0]
    fx = math.sin(math.radians(yaw)) * math.cos(math.radians(pit))
    fy = math.cos(math.radians(yaw)) * math.cos(math.radians(pit))
    fz = -math.sin(math.radians(pit))
    dec = dict(loc=[tgt[0] - fx * dist, tgt[1] - fy * dist, tgt[2] - fz * dist], tgt=tgt, yaw=yaw, pitch=pit, dist=dist, lens=30.0,
               shift_x=-0.056, shift_y=-0.017,
               loc_note="exact from tethys_preset.CAMS['t_dec'] (target_xy, layout yaw 118 -> rig -28); render log: loc (-289,192,91) tgt (-340,288,0)")
    for view, pngn, cam in (("overview", "H_overview_v2_plate.png", ov), ("decision", "H_decision_v2_plate.png", dec)):
        png = os.path.join(RMG, "hq_tethys", pngn)
        tcam = "t_over" if view == "overview" else "t_dec"
        e = dict(stem="hq_tethys_" + view, kind="hq", view=view, corp="tethys", beauty=png, look="aaa2", exempt=NO_FLASH, camera=cam,
                 index=SCR + "tethys/idpass/%s_aaa_index.npy" % tcam, accepted=t_acc if view == "overview" else [],
                 source=dict(final="route_map_graph/hq_tethys/" + pngn, commit=git_commit(png),
                             pose="tethys_preset.CAMS t_over / t_dec (layout yaw converted to rig: rig = 90 - layout)",
                             index_pass="tethys/idpass/%s_aaa_index.npy (ID re-render 2026-10-18: tethys_build.py + city_idpass.py, same cameras, spp 40, beauty median unchanged)" % tcam,
                             yaw_convention="rig: 0 = north, clockwise; Blender world BU"),
                 pending=["layout_seed, run id, anim_t, fixture run_graph and inputs hashes: no derive run exists for this render"])
        e["extra_values_note"] = "ratio_peak 3.72 / 3.10 and ratio_mean 1.88 / 1.57 of the 2026-10-17 post_tethys disc mask are superseded by the id-class ratios"
        E.append(e)
    # Aurelian v2 finals (2560 x 1440, Cycles 64 spp, 2026-10-18 AD round 3: outside-in route, arcade, occlusion fix); index passes from the same final run
    aur = [{"check": "landmark_ratio", "note": "Aurelian ratios 2.2-2.5 above 2.0 are warns, accepted like Solace (AD 2026-10-18)"}]
    E.append(hq_entry("aurelian", "overview", "hq_aurelian/plates/H_overview_v2_plate.png", "hq_aurelian", "H_overview",
                      "aurelian/big/bl_stills/H_overview", accepted=aur))
    E.append(hq_entry("aurelian", "decision", "hq_aurelian/plates/H_decision_v2_plate.png", "hq_aurelian", "H_decision",
                      "aurelian/big/bl_stills/H_decision", accepted=aur))
    # Street (rule-based street_r2, 1920 x 1080): poses from the render job; no Object Index pass was written
    sj = json.load(open(SCR + "street_r2/job_finals_s1_ov_closed_dec_closed.json"))
    sp = {f["name"]: f for f in sj["frames"]}
    for view, pngn, fr in (("overview", "01_OVERVIEW_closed_s1_plate.png", "F_ov_closed"),
                           ("decision", "02_DECISION_closed_s1_plate.png", "F_dec_closed")):
        p = sp[fr]["persp"]
        cam = MP.pose_from_loc_tgt(p["loc"], p["tgt"], p["lens"], p["sx"], p["sy"])
        cam["yaw_note"] = "yaw / pitch / dist derived from loc and tgt (the job stores loc, tgt, lens, sx, sy only)"
        png = os.path.join(RMG, "street_r2", "plates", pngn)
        E.append(dict(stem="street_" + view, kind="street", view=view, corp="", beauty=png, look="aaa2", exempt=NO_FLASH, camera=cam,
                      index=SCR + "idpass/street/%s_index.npy" % fr, accepted=[],
                      source=dict(final="route_map_graph/street_r2/plates/" + pngn, commit=git_commit(png),
                                  pose="D:/rc_scratch/street_r2/job_finals_s1_ov_closed_dec_closed.json frame %s (art seed 1, walls closed); storyboard t %s" % (fr, sp[fr].get("t")),
                                  index_pass="idpass/street/%s_index.npy (ID re-render 2026-10-18: r2_scene.py _idpass, same seed 1, cameras and 40 spp)" % fr,
                                  yaw_convention="rig: 0 = north, clockwise; Blender world BU"),
                      pending=["layout_seed (art seed 1 is recorded in source, the 12.8 decimal u64 is not), run id, anim_t, run_graph, inputs hashes: street_r2 predates derive v2"]))
    # City A2 hero frames (3840 x 2160): camera from the render log + CAMS['hero'] of city_preset.py (A2 mode)
    cam = dict(loc=[12.0, -960.0, 615.0], tgt=[12.0, -12.0, 0.0], yaw=0.0, pitch=33.0, dist=1130.0, lens=28.0, shift_x=0.0, shift_y=0.0,
               loc_note="loc / tgt are the render log's CAM line (rounded to 1 BU); lens, pitch, dist, shift from CAMS['hero'] (A2 mode: layout yaw 90 -> rig 0, target_ab (2,-2))",
               yaw_note="perspective hero camera, NOT the orthographic yaw 135 / pitch 40 of 4.2 that 12.8 lists: the finished art uses this camera")
    for view, pngn, logn, look in (("night", "city_all_corps_night.png", "hero_aaa.log", "aaa2"), ("day", "city_all_corps_day.png", "hero_day.log", None)):
        png = os.path.join(C, "city_all_corps", pngn)
        E.append(dict(stem="city_a2_" + view, kind="city", view="city", corp="", beauty=png, look=look, exempt=NO_FLASH, camera=cam,
                      index=SCR + "city_all_corps/idpass/hero_%s_index.npy" % ("aaa" if view == "night" else "day"), accepted=[], day=(view == "day"),
                      source=dict(final="city_all_corps/" + pngn, commit=git_commit(png),
                                  pose="D:/rc_scratch/city_all_corps/a2final/%s (CAM line) + city_preset.CAMS['hero']" % logn,
                                  index_pass="city_all_corps/idpass/hero_%s_index.npy (ID re-render 2026-10-18: city_render.py + city_idpass.py, same cameras, 80 spp)" % ("aaa" if view == "night" else "day"),
                                  yaw_convention="rig: 0 = north, clockwise; Blender world BU"),
                      pending=[
                               "camera.ortho: 12.8 asks yaw 135 / pitch 40 ortho; the plate is the perspective hero frame, AD to confirm which the build session should match",
                               "layout_seed, run id, anim_t, inputs hashes: city A2 predates derive v2"]))
    return E


def main():
    rows = []
    for e in entries():
        r = MP.build_plate(e, GP)
        v = r["vals"]
        rows.append((e, r))
        print("%-22s %s  med %.4f u10 %.3f o85 %.4f ratio %s id %s align %s" % (
            e["stem"], r["res"], v["median"], v["under_010"], v["over_085"], MP.r4(v["ratio_median"]), r["has_id"], MP.r4(r["align"])), flush=True)
    json.dump([{"stem": e["stem"], "commit": e["source"]["commit"], "final": e["source"]["final"],
                "has_id": r["has_id"], "align": MP.r4(r["align"]),
                "status": r["vals"]["checks"]["status"], "median": MP.r4(r["vals"]["median"]),
                "under": MP.r4(r["vals"]["under_010"]), "over": MP.r4(r["vals"]["over_085"]),
                "ratio_median": MP.r4(r["vals"]["ratio_median"]), "ratio_peak": MP.r4(r["vals"]["ratio_peak"]),
                "pending": e["pending"]} for e, r in rows],
              open(os.path.join(os.environ.get("TEMP", "."), "golden_summary.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
