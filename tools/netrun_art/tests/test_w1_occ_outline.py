"""W1 OCC-OUTLINE: the HQ face band samples each landmark's own face outline (art-pass d591aa84), square face as fallback."""
import math

from netrun_art import occlusion, rig
from netrun_art.hq import slots
from netrun_art.hq.face_outlines import FACE_OUTLINES


def _band_room(face_y, x0, x1, out_sign):
    back = face_y - out_sign
    return {"front": [[x0, face_y, 0], [x1, face_y, 0], [x1, face_y, 3], [x0, face_y, 3]],
            "back": [[x0, back, 0], [x1, back, 0], [x1, back, 3], [x0, back, 3]], "layer": 1, "floor": 0, "span": 1, "bld": "b"}


def _seg_dist(p, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / ((vx * vx + vy * vy) or 1.0)))
    return math.hypot(p[0] - a[0] - vx * t, p[1] - a[1] - vy * t)


def _outline_dist(p, outline):
    return min(_seg_dist(p, outline[i], outline[(i + 1) % len(outline)]) for i in range(len(outline)))


def test_outline_hit_lies_on_polyline_with_outward_normal():
    assert len(FACE_OUTLINES) == 7
    for corp, ol in FACE_OUTLINES.items():
        for deg in range(0, 360, 3):
            hit = occlusion.outline_hit(ol, math.radians(deg))
            assert hit is not None, (corp, deg)
            assert _outline_dist(hit[:2], ol) < 1e-6
            assert hit[0] * hit[2] + hit[1] * hit[3] > -1e-9


def test_round_compound_band_has_no_mid_air_points():
    ol = FACE_OUTLINES["solace"]
    pose = rig.Pose([0, 0, 0], 0.0, 0.0, 60.0, 36.0)
    rooms = {"a": _band_room(0.0, -1, 1, -1)}
    pts = occlusion.hq_band_points(rooms, ["a"], [0.0, 0.0], pose, rig.REF_W, rig.REF_H, outline=ol)
    assert pts
    assert all(_outline_dist([p[0], p[1]], ol) <= 0.01 for p in pts)


def test_band_without_outline_uses_square_face():
    ol = FACE_OUTLINES["solace"]
    pose = rig.Pose([0, 0, 0], 0.0, 0.0, 60.0, 36.0)
    rooms = {"a": _band_room(0.0, -1, 1, -1)}                  # tier face y = 0
    sq = occlusion.hq_band_points(rooms, ["a"], [0.0, 10.0], pose, rig.REF_W, rig.REF_H)
    assert sq and all(p[1] == 0.0 for p in sq)
    assert sq == occlusion.hq_band_points(rooms, ["a"], [0.0, 10.0], pose, rig.REF_W, rig.REF_H, outline=None)
    assert sq != occlusion.hq_band_points(rooms, ["a"], [0.0, 10.0], pose, rig.REF_W, rig.REF_H, outline=ol)


def test_tethys_entry_not_snapped_to_outline():
    e = slots.LANDMARK_ENTRIES["tethys"]["entry"]
    assert e == [30.0, 8.2, 5.0]
    assert _outline_dist(e[:2], FACE_OUTLINES["tethys"]) > 1.0
