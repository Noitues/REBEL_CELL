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
    day = _ratio(tmp_path, "day_time", 1.1, {"kind": "city", "view": "city", "look": "aaa2", "time": "day"})
    assert day["status"] == "n/a" and day["value"] < 1.5 and "report only" in day["note"]
    night = _ratio(tmp_path, "night_low", 1.1, {"kind": "city", "view": "city", "look": "aaa2", "time": "night"})
    assert night["status"] == "fail"
    default = _ratio(tmp_path, "default_low", 1.1, {"kind": "city", "view": "city", "look": None})
    assert default["status"] == "fail"  # no time key = night; the old kind/look heuristic is gone


def test_day_stem_fallback_only_without_time_key(tmp_path):
    stem = _ratio(tmp_path, "stem_day", 1.1, {"kind": "city", "view": "city", "look": None, "stem": "city_a2_day"})
    assert stem["status"] == "n/a"
    night = _ratio(tmp_path, "stem_night", 1.1, {"kind": "city", "view": "city", "look": None, "stem": "city_a2_day",
                                                 "time": "night"})
    assert night["status"] == "fail"


def test_day_makes_value_band_and_focus_report_only(tmp_path):
    def run(name, time):
        folder = F.landmark_capture(tmp_path / name, lum_in=40, capture={"kind": "city", "view": "city", "look": "aaa2",
                                                                         "time": time})
        return by_id(IC.check_capture_folder(folder, CFG)[0])
    day, night = run("d", "day"), run("n", "night")
    for rid in ("R-VAL-1", "R-VAL-2", "R-VAL-3", "R-FOCUS-1"):
        assert day[rid]["status"] == "n/a" and "day" in day[rid]["note"]
    assert night["R-FOCUS-1"]["status"] in ("pass", "fail") and night["R-FOCUS-1"]["value"] is not None
    assert day["R-FOCUS-1"]["value"] == night["R-FOCUS-1"]["value"]  # value kept
    assert day["R-VAL-1"]["value"] == night["R-VAL-1"]["value"]


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


FRONT_BU = 40.0


def _route_folder(tmp_path, name, ids, depth=None):
    folder = F.make_capture(tmp_path / name, capture={"kind": "street", "view": "decision", "look": "aaa2"})
    Image.fromarray(ids).save(os.path.join(folder, "id.png"))
    if depth is not None:
        Image.fromarray(np.round(depth * 100.0).astype(np.uint16)).save(os.path.join(folder, "depth.png"))
    return by_id(IC.check_capture_folder(folder, CFG)[0])["12.6.route"]


def _room_ids(bg=0):
    ids = np.zeros((100, 160, 3), np.uint8)
    ids[..., 0] = bg
    ids[40:60, 60:80, 0] = 5
    ids[40:60, 60:80, 1] = 1
    return ids


def _depth(near_box=None, near_bu=FRONT_BU - 5.0):
    d = np.full((100, 160), FRONT_BU + 20.0, np.float32)
    d[40:60, 60:80] = FRONT_BU
    if near_box is not None:
        y0, y1, x0, x1 = near_box
        d[y0:y1, x0:x1] = near_bu
    return d


def test_route_never_occluded_by_depth(tmp_path):
    # city all around, but the neighbours are behind the room front: not counted
    assert _route_folder(tmp_path, "beside", _room_ids(2), _depth())["status"] == "pass"
    # level with the front (beside the column, within 1 BU) is not counted either
    assert _route_folder(tmp_path, "level", _room_ids(2), np.full((100, 160), FRONT_BU - 0.5, np.float32))["status"] == "pass"
    # a building in front: class 2, 5 BU nearer, inside the 12 px margin
    ids = _room_ids(0)
    ids[30:70, 83:92, 0] = 2
    rec = _route_folder(tmp_path, "front", ids, _depth((30, 70, 83, 92)))
    assert rec["status"] == "fail" and rec["value"] == 32 and "rooms 1" in rec["note"]
    # the same blob outside the 12 px margin (box ends at x 91; x 93 is clear)
    ids = _room_ids(0)
    ids[40:60, 93:100, 0] = 2
    assert _route_folder(tmp_path, "far", ids, _depth((40, 60, 93, 100)))["status"] == "pass"
    # exactly 1 BU nearer is not "more than 1 BU"
    ids = _room_ids(0)
    ids[30:70, 83:92, 0] = 2
    assert _route_folder(tmp_path, "onebu", ids, _depth((30, 70, 83, 92), FRONT_BU - 1.0))["status"] == "pass"
    # thinner than the 4 px erosion (a lamp post or cable) is wiped out
    ids = _room_ids(0)
    ids[30:70, 85:88, 0] = 2
    assert _route_folder(tmp_path, "thin", ids, _depth((30, 70, 85, 88)))["status"] == "pass"
    # no depth.png: n/a
    assert _route_folder(tmp_path, "nodepth", _room_ids(2))["status"] == "n/a"


def test_route_occlusion_ignores_cut_surfaces_and_na_cases():
    d = _depth((40, 60, 80, 90))
    ids = _room_ids(0)
    ids[40:60, 80:90, 0] = 2  # cut surface of a room column: class 2 with B > 0
    ids[40:60, 80:90, 2] = 1
    assert IC.route_occlusion_record(ids.astype(np.float32), CFG, d)["status"] == "pass"
    ids[40:60, 80:90, 2] = 0  # a cut or ghosted building stub: class 2, G = 255, B = 0
    ids[40:60, 80:90, 1] = 255
    assert IC.route_occlusion_record(ids.astype(np.float32), CFG, d)["status"] == "pass"
    ids[40:60, 80:90, 1] = 7  # same pixels without the stub encoding occlude
    assert IC.route_occlusion_record(ids.astype(np.float32), CFG, d)["status"] == "fail"
    ids[40:60, 80:90, 0] = 0
    ids[40:60, 80:90, 1] = 0
    assert IC.route_occlusion_record(np.zeros((100, 160, 3), np.float32), CFG, d)["status"] == "n/a"
    ids[..., 1] = 0
    assert IC.route_occlusion_record(ids.astype(np.float32), CFG, d)["status"] == "n/a"
    assert IC.route_occlusion_record(None, CFG, d)["status"] == "n/a"


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


def test_street_rep_uses_facade_band_on_both_views():
    band = [0.0, 0.1, 1.0, 0.8]
    for view in ("overview", "decision", "hover"):
        assert IC.default_ranges({"kind": "street", "view": view}, CFG)[1] == band
    assert IC.default_ranges({"kind": "hq", "view": "decision"}, CFG)[1] == [0.0, 0.0, 1.0, 1.0]
