"""Parity sheet helpers (pure parts): the camera table and the numbers table."""
from netrun_art import parity_sheet as P

POSE = {"loc": [0.0, -10.0, 5.0], "tgt": [0.0, 0.0, 5.0], "dist": 10.0, "yaw": 0.0, "pitch": 2.0, "lens": 40.0,
        "shift_x": 0.0, "shift_y": 0.1}


def test_camera_table_zero_delta_for_equal_poses():
    t = P.camera_table(POSE, POSE)
    assert "| lens mm | 40.0000 | 40.0000 | +0.0000 |" in t
    assert "horizontal FOV deg" in t and "|d| 0.00" in t


def test_camera_table_reports_dist_delta():
    other = dict(POSE, dist=12.5)
    assert "+2.5000" in P.camera_table(POSE, other)


def test_numbers_table_lists_failing_checks_only_when_they_differ():
    t = P.numbers_table({"median": 0.1}, {"median": 0.2}, {"R-A": "pass", "R-B": "pass"}, {"R-A": "fail", "R-B": "pass"})
    assert "| R-A | pass | fail |" in t and "R-B" not in t
