import copy

import na04_fixtures as F
import numpy as np
from netrun_art.checks import image_checks as IC
from netrun_art.checks import metrics as M
from netrun_art.checks import reference as REF

CFG = IC.load_config()
AAA2 = {"kind": "hq", "view": "overview", "look": "aaa2"}


def by_id(recs):
    return {r["id"]: r for r in recs}


def test_good_frame_passes_value_band_any_size(tmp_path):
    for w, h in ((160, 100), (320, 180), (97, 53)):
        folder = F.make_capture(tmp_path / f"g{w}", w, h, capture=dict(AAA2, resolution=[w, h]))
        recs, measured = IC.check_capture_folder(folder, CFG)
        r = by_id(recs)
        assert [r[k]["status"] for k in ("R-VAL-1", "R-VAL-2", "R-VAL-3")] == ["pass"] * 3, (w, h, r)
        assert abs(measured["median"] - 36 / 255) < 1e-6


def test_dark_frame_fails_value_band(tmp_path):
    folder = F.make_capture(tmp_path / "dark", rows=lambda y, h: 10, capture=AAA2)
    r = by_id(IC.check_capture_folder(folder, CFG)[0])
    assert r["R-VAL-1"]["status"] == "fail" and r["R-VAL-2"]["status"] == "fail"


def test_median_warn_bands():
    stats = {"median": 0.10, "under_010": 0.3, "over_085": 0.0}
    r = by_id(IC.value_band_records(stats, {"look": "aaa2"}, CFG))
    assert r["R-VAL-1"]["status"] == "warn"
    stats["median"] = 0.18
    assert by_id(IC.value_band_records(stats, {"look": "aaa2"}, CFG))["R-VAL-1"]["status"] == "warn"
    stats["median"] = 0.20
    assert by_id(IC.value_band_records(stats, {"look": "aaa2"}, CFG))["R-VAL-1"]["status"] == "fail"
    stats["median"] = 0.08
    assert by_id(IC.value_band_records(stats, {"look": "aaa2"}, CFG))["R-VAL-1"]["status"] == "fail"


def test_exemptions_and_mainline():
    bad = {"median": 0.5, "under_010": 0.0, "over_085": 0.5}
    for cap in ({"look": "aaa2", "exempt": {"hover_cut": True}}, {"look": "blend", "look_blend": 0.5},
                {"look": "aaa2", "look_blend": 0.4}, {}):
        r = IC.value_band_records(bad, cap, CFG)
        assert all(x["status"] == "n/a" for x in r), cap
    ml = IC.value_band_records({"median": 0.214, "under_010": 0.0, "over_085": 0.5}, {"look": "mainline"}, CFG)
    assert ml[0]["status"] == "pass" and ml[1]["status"] == "n/a"
    ml = IC.value_band_records({"median": 0.30, "under_010": 0.0, "over_085": 0.0}, {"look": "mainline"}, CFG)
    assert ml[0]["status"] == "fail"


def test_resolution_mismatch_fails(tmp_path):
    folder = F.make_capture(tmp_path / "res", 160, 100, capture=dict(AAA2, resolution=[320, 180]))
    r = by_id(IC.check_capture_folder(folder, CFG)[0])
    assert r["12.0"]["status"] == "fail"


def test_landmark_ratio_pass_warn_fail(tmp_path):
    ok = F.landmark_capture(tmp_path / "ok", lum_in=int(36 * 1.7), capture=AAA2)
    assert by_id(IC.check_capture_folder(ok, CFG)[0])["12.2"]["status"] == "pass"
    warn = F.landmark_capture(tmp_path / "warn", lum_in=int(36 * 2.6), capture=AAA2)
    assert by_id(IC.check_capture_folder(warn, CFG)[0])["12.2"]["status"] == "warn"
    # oversized landmark: it fills most of the frame and is no brighter than its surroundings
    big = F.landmark_capture(tmp_path / "big", lum_in=40, lum_out=36, frac=0.9, capture=AAA2)
    r = by_id(IC.check_capture_folder(big, CFG)[0])["12.2"]
    assert r["status"] == "fail" and r["value"] < 1.5


def test_landmark_absent_rules(tmp_path):
    for kind, view, want in (("hq", "overview", "fail"), ("hq", "decision", "fail"), ("street", "overview", "n/a"),
                             ("city", "city", "n/a"), ("hq", "hover", "n/a")):
        folder = F.make_capture(tmp_path / f"{kind}{view}", ids=np.full((100, 160), 2, np.uint8),
                                capture={"kind": kind, "view": view, "look": "aaa2"})
        assert by_id(IC.check_capture_folder(folder, CFG)[0])["12.2"]["status"] == want, (kind, view)


def test_no_id_png_is_na(tmp_path):
    folder = F.make_capture(tmp_path / "noid", capture=AAA2)
    assert by_id(IC.check_capture_folder(folder, CFG)[0])["12.2"]["status"] == "n/a"


def test_scope_keys_and_nan_metric(tmp_path):
    folder = F.make_capture(tmp_path / "s", capture={"look": "aaa2"})  # no kind or view: scoped rules are n/a
    r = by_id(IC.check_capture_folder(folder, CFG)[0])
    assert r["R-SIL-1"]["status"] == "n/a" and "no kind" in r["R-SIL-1"]["note"]
    assert r["R-REP-1"]["status"] in ("pass", "n/a")  # flat frame: no tile has texture, so the metric is undefined
    folder = F.make_capture(tmp_path / "t", capture={"kind": "street", "view": "overview", "look": "aaa2"})
    r = by_id(IC.check_capture_folder(folder, CFG)[0])
    assert r["R-SIL-1"]["status"] in ("pass", "fail", "n/a")
    assert r["R-HOR-1"]["status"] == "n/a"  # city only


def test_renderer_tolerances_not_hard_coded(tmp_path):
    a = {"median": 0.14, "under_010": 0.30, "ratio": 1.7, "sobel_mean": 0.030, "hue_entropy_bits": 4.0}
    b = {"median": 0.15, "under_010": 0.33, "ratio": 1.8, "sobel_mean": 0.032, "hue_entropy_bits": 4.1}
    assert all(r["status"] == "pass" for r in IC.compare_renderers(a, b, CFG))
    c = dict(b, median=0.20)
    assert {r["id"]: r["status"] for r in IC.compare_renderers(a, c, CFG)}["RENDERER.median"] == "fail"
    tight = copy.deepcopy(CFG)
    tight["tolerance"]["renderer"]["median"] = 0.005  # the limit is read from the config
    assert {r["id"]: r["status"] for r in IC.compare_renderers(a, b, tight)}["RENDERER.median"] == "fail"
    rel = copy.deepcopy(CFG)
    rel["tolerance"]["renderer"]["relative"] = 0.01
    assert {r["id"]: r["status"] for r in IC.compare_renderers(a, b, rel)}["RENDERER.sobel_mean"] == "fail"


def test_same_image_blender_vs_godot_differs_only_by_tolerance(tmp_path):
    # the same scene as two captures of different size: resampling stays inside the tolerances
    cap = dict(AAA2)
    a = F.landmark_capture(tmp_path / "blender", lum_in=61, w=320, h=200, capture=cap)
    b = F.landmark_capture(tmp_path / "godot", lum_in=61, w=160, h=100, capture=cap)
    _, ma = IC.check_capture_folder(a, CFG)
    _, mb = IC.check_capture_folder(b, CFG)
    assert all(r["status"] == "pass" for r in IC.compare_renderers(ma, mb, CFG))


def test_metrics_basics():
    assert abs(float(M.luma(np.array([[[1.0, 1.0, 1.0]]], np.float32))[0, 0]) - 1.0) < 1e-6
    rgb = np.zeros((40, 80, 3), np.float32)
    rgb[..., 0] = 1.0  # pure red: chromatic, one hue, entropy 0
    p = M.palette(rgb, np.ones((40, 80), bool), CFG["composition"]["constants"])
    assert p["hue_entropy_bits"] == 0.0 and p["hue_top_share"] == 1.0
    assert np.isnan(M.palette(rgb[:2, :10], np.ones((2, 10), bool), CFG["composition"]["constants"])["hue_entropy_bits"])


def test_reference_scope_and_parse():
    assert REF.reference_scope("side", "c_aaa2r3", {}, False, False)
    assert not REF.reference_scope("netrun", "a_sb_hq", {}, False, False)
    row = "| x | custom | PASS 0.229 | **FAIL** 0.007 | " + " | ".join(["n/a"] * 12) + " |"
    parsed = REF.parse_rules_check("| image | role |\n|---|---|\n" + row + "\n")
    assert parsed["x"]["R-SIL-1"] == ("PASS", "0.229") and parsed["x"]["R-SIL-2"] == ("FAIL", "0.007")
    assert parsed["x"]["R-REP-1"] == ("n/a", None)
