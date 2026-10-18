import os
import time

import na04_fixtures as F
from netrun_art import io
from netrun_art.checks import data_checks as D
from netrun_art.checks import image_checks as IC

SEEDS = ["12345", "987654321", "18446744073709551615"]
CFG = IC.load_config()


def test_determinism_three_seeds(tmp_path):
    spec = F.write_producer(tmp_path)
    t0 = time.time()
    recs = D.check_determinism(spec, SEEDS)
    assert len(recs) == 3 and all(r["status"] == "pass" for r in recs)
    assert time.time() - t0 < 20.0


def test_determinism_detects_nondeterminism(tmp_path):
    p = tmp_path / "bad.py"
    p.write_text("import os\n\ndef produce(seed):\n    return {'x': {'pid': os.getpid()}}\n")
    recs = D.check_determinism(str(p) + ":produce", SEEDS[:1])
    assert recs[0]["status"] == "fail"


def test_seed_sensitivity_three_pairs(tmp_path):
    recs = D.check_seed_sensitivity(F.write_producer(tmp_path), SEEDS)
    assert len(recs) == 3 and all(r["status"] == "pass" for r in recs)
    same = D.check_seed_sensitivity(F.write_producer(tmp_path), ["5", "5"])
    assert same[0]["status"] == "fail"


def test_key_independence(tmp_path):
    prod = D.load_producer(F.write_producer(tmp_path).replace(":produce", ":placements"))
    a = prod("77")
    b = prod("77", rename={"1:2": "1:9"})
    assert D.check_key_independence(a, b, ("1:2", "1:9"))["status"] == "pass"
    assert D.check_key_independence(a, b, "1:2")["status"] == "fail"  # the new key 1:9 is not declared changed
    b2 = dict(b)
    b2["2:2"] = {"x": 0.12345}
    assert D.check_key_independence(a, b2, ("1:2", "1:9"))["status"] == "fail"


def test_parity_self_and_mutation(tmp_path):
    obj = {"version": 1, "rooms": {"L1N0": {"front": [[0.0, 1.5, 2.0]]}}, "edges": [{"a": "x", "b": "y"}]}
    a = str(tmp_path / "a.json")
    io.dump(obj, a)
    assert D.compare_json_files(a, a)["status"] == "pass"
    raw = open(a, "rb").read()
    i = raw.index(b"1.5")
    b = str(tmp_path / "b.json")
    open(b, "wb").write(raw[:i] + b"2" + raw[i + 1:])  # one byte: 1.5 -> 2.5
    r = D.compare_json_files(a, b)
    assert r["status"] == "fail" and "$.rooms.L1N0.front[0][1]" in r["note"]
    c = str(tmp_path / "c.json")
    open(c, "wb").write(raw[:i] + b"\x00" + raw[i + 1:])  # not parseable: byte offset is reported
    r = D.compare_json_files(a, c)
    assert r["status"] == "fail" and f"byte {i}" in r["note"]


def test_first_diff_path():
    assert D.first_diff_path({"a": [1, {"b": 2}]}, {"a": [1, {"b": 3}]}) == "$.a[1].b"
    assert D.first_diff_path({"a": [1]}, {"a": [1, 2]}) == "$.a[1]"
    assert D.first_diff_path({"a": 1}, {"a": 1}) is None


RAIL = {"pts": [[0.0, 0.0], [30.0, 0.0], [60.0, 0.0]], "half_clear": 4.5, "deck_z": 17.5, "side_cap": 15.5,
        "side_d": 7.2}


def test_rail_footprints_and_heights():
    z = {"rail": dict(RAIL)}
    ok = F.city_with({"1:1": [(F.square(0, 20, 10, 30), 0.0, 40.0)], "1:2": [(F.square(10, 6, 20, 12), 0.0, 12.0)]})
    assert D.check_rail_footprints(z, ok)["status"] == "pass"
    assert D.check_rail_heights(z, ok)["status"] == "pass"
    near = F.city_with({"1:3": [(F.square(10, 3, 20, 12), 0.0, 12.0)]})
    assert D.check_rail_footprints(z, near)["status"] == "fail"
    tall = F.city_with({"1:4": [(F.square(10, 6, 20, 12), 0.0, 20.0)]})
    assert D.check_rail_heights(z, tall)["status"] == "fail"
    over = F.city_with({"1:5": [(F.square(10, -5, 20, 5), 0.0, 5.0)]})  # polygon straddles the rail
    assert D.check_rail_footprints(z, over)["status"] == "fail"


def test_piers_and_one_line():
    streets = [{"lot": [6, 6], "along_i": True, "along_j": False, "traffic": 0.5}]
    city = F.city_with({}, streets)
    z = {"rail": dict(RAIL, piers=[[1.0, -1.0]])}  # x/6+6 = 6.17, 6 - y/6 = 6.17 -> lot (6, 6)
    assert D.check_piers(z, city)["status"] == "pass"
    z2 = {"rail": dict(RAIL, piers=[[1.0, -1.0], [30.0, 0.0]])}
    assert D.check_piers(z2, city)["status"] == "fail"
    assert D.check_piers({"rail": dict(RAIL)}, city)["status"] == "n/a"
    assert D.check_one_line(z, dict(RAIL))["status"] == "pass"
    moved = dict(RAIL, pts=[[0.0, 0.0], [30.0, 0.1], [60.0, 0.0]])
    assert D.check_one_line(z, moved)["status"] == "fail"


def _derive(path_z=2.0):
    q = [[0.0, 0.0, 1.0], [4.0, 0.0, 1.0], [4.0, 0.0, 3.0], [0.0, 0.0, 3.0]]
    return {"rooms": {"L1N0": {"front": q, "back": q, "bld": "1:1"}, "L2N0": {"front": q, "back": q, "bld": "1:1"}},
            "edges": [{"a": "L1N0", "b": "L2N0", "path": [[0.0, -1.0, path_z], [10.0, -1.0, path_z]]}]}


def test_links_openings_foreground():
    own = F.city_with({"1:1": [(F.square(-1, -0.5, 5, 5), 0.0, 10.0)]})
    d = _derive()
    assert D.check_openings(d, own)["status"] == "pass"
    assert D.check_links(d, own)["status"] == "pass"
    other = F.city_with({"1:1": [(F.square(-1, -0.5, 5, 5), 0.0, 10.0)], "9:9": [(F.square(5, -2, 9, 0), 0.0, 10.0)]})
    assert D.check_links(d, other)["status"] == "fail"
    inside = F.city_with({"1:1": [(F.square(20, 20, 30, 30), 0.0, 10.0)], "9:9": [(F.square(-1, -1, 5, 1), 0.0, 10.0)]})
    assert D.check_openings(d, inside)["status"] == "fail"
    assert D.check_foreground(d, {"items": [{"kind": "stall", "pos": [20.0, 20.0, 1.0]}]}, 0.5)["status"] == "pass"
    assert D.check_foreground(d, {"items": [{"kind": "stall", "pos": [2.0, 0.2, 2.0]}]}, 0.5)["status"] == "fail"


def _beam(bid, x, cone=30.0, blend=1.0, shadow=False, mat="beam_shaft", media=True):
    return {"bid": bid, "pos": [x, 0.0], "top": 30.0,
            "spot": {"cone_deg": cone, "blend": blend, "shadow": shadow, "media_linked": media},
            "shaft": {"material": mat, "shadow": False}}


def test_beams():
    good = {"route_bids": ["r"], "beams": [_beam("a", 0.0), _beam("b", 50.0), _beam("c", 100.0, cone=70.0, blend=0.8)]}
    assert D.check_beam_config(good, CFG)["status"] == "pass"
    assert D.check_beam_layout(good, CFG)["status"] == "pass"
    for bad in (_beam("x", 0.0, cone=9.0), _beam("x", 0.0, blend=0.7), _beam("x", 0.0, shadow=True),
                _beam("x", 0.0, mat="glow")):
        assert D.check_beam_config({"beams": [bad]}, CFG)["status"] == "fail"
    assert D.check_beam_config({"beams": [_beam("x", 0.0, cone=5.0, media=False)]}, CFG)["status"] == "pass"
    assert D.check_beam_layout({"beams": [_beam("a", 0.0), _beam("b", 44.0)]}, CFG)["status"] == "fail"
    assert D.check_beam_layout({"route_bids": ["a"], "beams": [_beam("a", 0.0)]}, CFG)["status"] == "fail"
    seven = {"beams": [_beam(str(i), 100.0 * i) for i in range(7)]}
    assert D.check_beam_layout(seven, CFG)["status"] == "fail"


def test_occlusion():
    city = F.city_with({"1:1": [(F.square(0, 0, 4, 4), 0.0, 2.0)]})
    blk = {"params": {"occ_ghost": 0.2, "occ_stub": 3.8},
           "buildings": [{"bid": "1:1", "cut_height": 2.0, "opacity": 0.5}]}
    assert D.check_occlusion({"occlusion": blk}, city, CFG)["status"] == "pass"  # stub is min(3.8, top 2.0)
    blk2 = {"params": blk["params"], "buildings": [{"bid": "1:1", "cut_height": 2.0, "opacity": 0.1}]}
    assert D.check_occlusion({"occlusion": blk2}, city, CFG)["status"] == "fail"
    blk3 = {"params": blk["params"], "buildings": [{"bid": "1:1", "cut_height": 1.0, "opacity": 0.5}]}
    assert D.check_occlusion({"occlusion": [blk3]}, city, CFG)["status"] == "fail"


def test_data_suite_time_reported(tmp_path):
    inputs = {"producer": F.write_producer(tmp_path), "seeds": SEEDS}
    recs, secs = D.run_data_suite(inputs, CFG)
    assert secs < 20.0
    assert len(recs) == 6 and all(r["status"] == "pass" for r in recs)
