"""STREET-CAM (art-pass A-025 / A-026): the street rig follows the plate camera rule, and the derive logs a leg-extension retry."""
import math

import pytest

from netrun_art import layout, rig as RG
from netrun_art.derive import street as S
from netrun_art.tests import synth


def _derive(seed):
    w = synth.make_world(seed)
    city = layout.apply_layout_rules(w["city"], w["net"])
    return w, S.derive_street(city, w["net"], w["run_graph"], w["site"])


@pytest.mark.parametrize("seed", [101, 104, 108, 111])
def test_overview_and_decision_use_the_plate_distance_shift_and_a_frontage_normal_yaw(seed):
    _, d = _derive(seed)
    ov, dec = d["overview"], d["decision"]
    assert ov["dist"] == RG.RIG["ov_dist"] == 114.62
    assert (ov["shift_x"], ov["shift_y"]) == (-0.0548, 0.1172)
    assert dec["dist"] == RG.RIG["dec_dist"] == 42.10
    assert (dec["shift_x"], dec["shift_y"]) == (0.0345, 0.0002)
    assert ov["lens"] == 40.0 and ov["pitch"] == 2.0 and dec["lens"] == 30.0 and dec["pitch"] == 9.0
    yaw0 = RG.yaw_of_nrm(d["nrm"])
    for pose in (ov, dec):
        off = (pose["yaw"] - yaw0 + 180.0) % 360.0 - 180.0
        assert abs(off) <= RG.RIG["yaw_max"] + 1e-9        # the camera looks along the frontage normal (+- the rig bias)
    # the overview looks at the frontage within 0.3 * yaw_max of its normal: the wall fills the frame, no cross street view
    off_ov = (ov["yaw"] - yaw0 + 180.0) % 360.0 - 180.0
    assert abs(off_ov) == pytest.approx(RG.RIG["ov_yaw_k"] * RG.RIG["yaw_max"])


def test_the_rooms_clear_the_span_rule_at_the_plate_distance():
    for seed in (101, 103, 105, 108, 111):
        w = synth.make_world(seed)
        city = layout.apply_layout_rules(w["city"], w["net"])
        d = S.derive_street(city, w["net"], w["run_graph"], w["site"])
        ov = RG.Pose.from_json(d["overview"])
        rooms = d["rooms"]
        px = [S.room_px(ov, r) for r in rooms.values() if r["span"] == d["span"]]
        px = [p for p in px if p is not None]
        assert px and min(px) >= S.RULES["room_px_target"]


def test_a_retry_is_logged_in_the_derive_output(monkeypatch):
    w = synth.make_world(101)
    city = layout.apply_layout_rules(w["city"], w["net"])
    plain = S.derive_street(city, w["net"], w["run_graph"], w["site"])
    assert "retry" not in plain and "retry_step" not in plain
    real = S.choose_street_fitting
    monkeypatch.setattr(S, "choose_street_fitting", lambda *a, **k: (real(*a, **k)[0], 3))
    d = S.derive_street(city, w["net"], w["run_graph"], w["site"])
    assert d["retry"] == "leg_extend" and d["retry_step"] == 3
    monkeypatch.setattr(S, "choose_street_fitting", lambda *a, **k: (real(*a, **k)[0], 1))
    assert "retry" not in S.derive_street(city, w["net"], w["run_graph"], w["site"])
