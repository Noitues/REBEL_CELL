"""NA-04b: report-only city day ratio, pre-accepted warns (config), 12.6 route never occluded, plate drift compare."""
import os

import na04_fixtures as F
import numpy as np
from netrun_art import io
from netrun_art.checks import drift as D
from netrun_art.checks import image_checks as IC
from PIL import Image

CFG = IC.load_config()


def by_id(recs):
    return {r["id"]: r for r in recs}


def _ratio(tmp_path, name, lum, capture):
    folder = F.landmark_capture(tmp_path / name, lum_in=int(36 * lum), capture=capture)
    return by_id(IC.check_capture_folder(folder, CFG)[0])["12.2"]


def test_city_day_ratio_is_report_only(tmp_path):
    low = _ratio(tmp_path, "day_low", 1.1, {"kind": "city", "view": "city", "look": None})
    assert low["status"] == "n/a" and low["value"] < 1.5 and "report only" in low["note"]
    by_time = _ratio(tmp_path, "day_time", 1.1, {"kind": "city", "view": "city", "look": "aaa2", "time": "day"})
    assert by_time["status"] == "n/a"
    night = _ratio(tmp_path, "night_low", 1.1, {"kind": "city", "view": "city", "look": "aaa2"})
    assert night["status"] == "fail"


def test_pre_accepted_warns_are_config_and_flag_new(tmp_path):
    accepted = {e["stem"]: e["value"] for e in CFG["landmark_ratio"]["pre_accepted"]}
    assert accepted == {"hq_tethys_decision": 2.02, "city_a2_night": 2.8}
    cap = {"kind": "hq", "view": "decision", "look": "aaa2", "stem": "hq_tethys_decision"}
    ok = _ratio(tmp_path, "t_ok", 2.05, cap)
    assert ok["status"] == "warn" and "pre-accepted" in ok["note"]
    new = _ratio(tmp_path, "t_new", 2.6, cap)
    assert new["status"] == "warn" and "NEW" in new["note"]
    other = _ratio(tmp_path, "t_other", 2.05, dict(cap, stem="hq_halcyon_decision"))
    assert other["status"] == "warn" and "pre-accepted" not in other["note"]
    night = _ratio(tmp_path, "n_ok", 2.8, {"kind": "city", "view": "city", "look": "aaa2", "stem": "city_a2_night"})
    assert night["status"] == "warn" and "pre-accepted" in night["note"]


def test_tethys_overview_ratio_passes_with_id_mask(tmp_path):
    cap = {"kind": "hq", "view": "overview", "look": "aaa2", "stem": "hq_tethys_overview"}
    assert _ratio(tmp_path, "t_over", 1.81, cap)["status"] == "pass"


def _route_folder(tmp_path, name, ids):
    folder = F.make_capture(tmp_path / name, capture={"kind": "street", "view": "decision", "look": "aaa2"})
    Image.fromarray(ids).save(os.path.join(folder, "id.png"))
    return by_id(IC.check_capture_folder(folder, CFG)[0])["12.6.route"]


def _room_ids(bg=0):
    ids = np.zeros((100, 160, 3), np.uint8)
    ids[..., 0] = bg
    ids[40:60, 60:80, 0] = 5
    ids[40:60, 60:80, 1] = 1
    return ids


def test_route_never_occluded_fixtures(tmp_path):
    assert _route_folder(tmp_path, "clean", _room_ids(0))["status"] == "pass"
    near = _route_folder(tmp_path, "near", _room_ids(2))  # city all around: inside the 12 px margin
    assert near["status"] == "fail" and near["value"] > 0
    far = _room_ids(0)
    far[40:60, 93:100, 0] = 2  # room box grown 12 px ends at x 91; x 93 is clear
    assert _route_folder(tmp_path, "far", far)["status"] == "pass"
    far[40:60, 91:100, 0] = 2  # column 91 is the last inside the margin
    rec = _route_folder(tmp_path, "touch", far)
    assert rec["status"] == "fail" and rec["value"] == 20 and "rooms 1" in rec["note"]


def test_route_occlusion_ignores_cut_surfaces_and_na_cases():
    ids = _room_ids(0)
    ids[40:60, 80:90, 0] = 2  # cut surface of a room column: class 2 with B > 0
    ids[40:60, 80:90, 2] = 1
    assert IC.route_occlusion_record(ids.astype(np.float32), CFG)["status"] == "pass"
    assert IC.route_occlusion_record(np.zeros((100, 160, 3), np.float32), CFG)["status"] == "n/a"
    ids[..., 1] = 0
    assert IC.route_occlusion_record(ids.astype(np.float32), CFG)["status"] == "n/a"
    assert IC.route_occlusion_record(None, CFG)["status"] == "n/a"


def _plate(folder, stem, lum, capture, values=None):
    ids = np.zeros((100, 160, 3), np.uint8)
    ids[..., 0] = 2
    ids[30:70, 50:110, 0] = 1
    a = np.full((100, 160, 3), 36, np.uint8)
    a[30:70, 50:110] = lum
    os.makedirs(str(folder), exist_ok=True)
    Image.fromarray(a).save(os.path.join(str(folder), stem + ".png"))
    Image.fromarray(ids).save(os.path.join(str(folder), stem + "_id.png"))
    io.dump(dict(capture, stem=stem), os.path.join(str(folder), stem + "_capture.json"))
    if values is not None:
        io.dump(values, os.path.join(str(folder), stem + "_values.json"))


def test_drift_compare_flags_only_beyond_tolerance(tmp_path):
    plates = tmp_path / "plates"
    cap = {"kind": "hq", "view": "overview", "look": "aaa2"}
    _plate(plates, "p_same", 61, cap)
    work = tmp_path / "work"
    rows, _ = D.drift_rows(str(plates), str(work), CFG)
    ours = {r["check"]: r["ours"] for r in rows if r["plate"] == "p_same"}
    assert "12.2 ratio" in ours  # no values.json: rows exist, verdict n/a
    vals = {"median": ours["R-VAL-1"], "under_010": ours["R-VAL-2"], "over_085": ours["R-VAL-3"],
            "ratio_median": ours["12.2 ratio"] + 0.5, "composition": {"R-REP-1": None},
            "checks": {"baseline": [], "pre_accepted": [], "report_only": [], "status": {}}}
    _plate(plates, "p_same", 61, cap, vals)
    rows, _ = D.drift_rows(str(plates), str(work), CFG)
    verdict = {r["check"]: r["verdict"] for r in rows if r["plate"] == "p_same"}
    assert verdict["R-VAL-1"] == "ok" and verdict["12.2 ratio"].startswith("DRIFT")
    md = D.to_markdown(rows)
    assert "| p_same | 12.2 ratio |" in md
