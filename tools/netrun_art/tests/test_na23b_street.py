"""NA-23b: the street span rule (smallest visible route room in the OVERVIEW pose reaches `room_px_target`) and the street
capacity on every corporation x seeds 1..4 (PIPELINE_SPEC 12.6 "every room")."""
import pytest

from netrun_art import layout
from netrun_art.derive import street as S
from netrun_art.tests import synth

CORPS = ("halcyon", "meridian", "orbital", "rebel_cell", "solace")


def _chosen(w):
    city = layout.apply_layout_rules(w["city"], w["net"])
    layers = S.layer_nodes(w["run_graph"])
    _, pts = S.select_link(w["net"], w["site"])
    best = S.choose_street(S.LY.merged_buildings(city), S.LY.link_legs(city, pts), layers, S.RULES)
    score, li, side, a, c, fr, asg, ok, start_left = best
    return city, layers, fr[0]["nrm"], start_left, asg


@pytest.mark.parametrize("seed", [101, 103, 108, 111])
def test_span_is_the_smallest_that_reaches_the_target(seed):
    w = synth.make_world(seed)
    city, layers, nrm, sl, asg = _chosen(w)
    rows = S.span_scan(asg, layers, nrm, sl, S.RULES)
    assert [r["span"] for r in rows] == list(range(1, S.RULES["span_max"] + 1))
    want = next(r["span"] for r in rows if r["min_px"] >= S.RULES["room_px_target"])
    assert S.choose_span(asg, layers, nrm, sl, S.RULES) == want
    d = S.derive_street(city, w["net"], w["run_graph"], w["site"])
    assert d["span"] == want
    # every smaller span leaves its smallest room under the target
    assert all(r["min_px"] < S.RULES["room_px_target"] for r in rows if r["span"] < want)


def test_span_uses_the_smallest_room_not_the_first():
    # seed 101: the first room clears 46 px at span 1 but the smallest does not (45.6), so the span is 2
    w = synth.make_world(101)
    city, layers, nrm, sl, asg = _chosen(w)
    rows = S.span_scan(asg, layers, nrm, sl, S.RULES)
    assert rows[0]["min_px"] < S.RULES["room_px_target"] <= rows[1]["min_px"]
    assert S.derive_street(city, w["net"], w["run_graph"], w["site"])["span"] == 2


def test_fallback_layers_are_reported_and_keep_span_one():
    w = synth.make_world(105)
    city, layers, nrm, sl, asg = _chosen(w)
    rows = S.span_scan(asg, layers, nrm, sl, S.RULES)
    assert rows[1]["fallback"] == [1, 3]        # span 2: layers 1 and 3 sit in buildings without the floors
    rooms = S.room_boxes(asg, layers, 2, S.RULES)
    assert sorted({rm["layer"] for rm in rooms.values() if rm["span"] == 1}) == rows[1]["fallback"]
    assert rows[0]["fallback"] == []


def test_span_scan_is_deterministic():
    w = synth.make_world(102)
    city, layers, nrm, sl, asg = _chosen(w)
    assert S.span_scan(asg, layers, nrm, sl, S.RULES) == S.span_scan(asg, layers, nrm, sl, S.RULES)


@pytest.mark.parametrize("corp", CORPS)
@pytest.mark.parametrize("seed", [1, 2, 3, 4])
def test_every_corp_and_seed_derives(corp, seed):
    w = synth.make_world(seed, corp)
    city = layout.apply_layout_rules(w["city"], w["net"])
    d = S.derive_street(city, w["net"], w["run_graph"], w["site"])
    assert d["span"] in range(1, S.RULES["span_max"] + 1)
    assert len(d["rooms"]) == len(w["run_graph"]["nodes"])


# ---- the game's own city (fixtures g1..g3 from `dump_game_worlds.gd`, trimmed around the Site's link) -------------------

def _decode(v):
    if isinstance(v, str) and v.startswith("~"):
        return float.fromhex(v[1:])
    if isinstance(v, list):
        return [_decode(e) for e in v]
    if isinstance(v, dict):
        return {k: _decode(e) for k, e in v.items()}
    return v


def _game(name):
    import json
    import os
    from netrun_art.tests.gen_fixtures import FIX
    with open(os.path.join(FIX, "inputs", name + ".json"), encoding="utf-8") as f:
        return _decode(json.load(f))


def _fit(w):
    city = w["city"]
    layers = S.layer_nodes(w["run_graph"])
    _, pts = S.select_link(w["net"], w["site"])
    return S.choose_street_fitting(S.LY.merged_buildings(city), S.LY.link_legs(city, pts), layers, S.RULES)


def test_game_meridian_seed_1_derives_without_the_ladder():
    for name in ("g1", "g3"):
        w = _game(name)
        assert w["corp"] == "meridian"
        best, step = _fit(w)
        assert step == 0 and best[7]
        assert S.derive_street(w["city"], w["net"], w["run_graph"], w["site"])["kind"] == "street"


def test_a_slanted_first_leg_no_longer_loses_the_frontage():
    # solace t1_i on the game city: the routed link starts off the street axis, so the raw leg reads as a y leg
    w = _game("g2")
    city = w["city"]
    layers = S.layer_nodes(w["run_graph"])
    _, pts = S.select_link(w["net"], w["site"])
    legs = S.LY.link_legs(city, pts)
    B = S.LY.merged_buildings(city)
    raw = S.choose_street(B, legs, layers, S.RULES)
    assert not raw[5] or not raw[7]                          # as before: no frontage
    best, step = S.choose_street_fitting(B, legs, layers, S.RULES)
    assert step == 1 and best[5] and best[7]
    d = S.derive_street(city, w["net"], w["run_graph"], w["site"])
    assert len(d["rooms"]) == len(w["run_graph"]["nodes"])


def test_square_legs_makes_axis_aligned_legs_and_keeps_aligned_ones():
    legs = [[0.0, 0.0], [10.0, 2.0], [10.0, 9.0]]
    sq = S.square_legs(legs)
    assert sq == [[0.0, 0.0], [10.0, 0.0], [10.0, 2.0], [10.0, 9.0]]
    assert S.square_legs(sq) == sq
    assert S.square_legs([[0.0, 0.0], [3.0, 7.0]]) == [[0.0, 0.0], [0.0, 7.0], [3.0, 7.0]]


def test_a_street_that_fits_is_never_changed_by_the_ladder():
    w = synth.make_world(101)
    city = layout.apply_layout_rules(w["city"], w["net"])
    layers = S.layer_nodes(w["run_graph"])
    _, pts = S.select_link(w["net"], w["site"])
    legs = S.LY.link_legs(city, pts)
    B = S.LY.merged_buildings(city)
    best, step = S.choose_street_fitting(B, legs, layers, S.RULES)
    assert step == 0 and best == S.choose_street(B, legs, layers, S.RULES)
