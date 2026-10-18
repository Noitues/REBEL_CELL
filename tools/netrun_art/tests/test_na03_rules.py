import math

import pytest

from netrun_art import contract, layout, rig
from netrun_art.derive import street as ST
from netrun_art.tests import producer, synth


def test_rule1_sweep_200_seeds():
    """3.3 rule 1: after the layout rules no border-link frontage building is under 6 real floors, and the hero sign
    rule holds (one blade + band per route column, the pair alternates district_a / district_b)."""
    bad = []
    for seed in range(1000, 1200):
        w = synth.make_world(seed)
        city = layout.apply_layout_rules(w["city"], w["net"])
        d = ST.derive_street(city, w["net"], w["run_graph"], w["site"])
        byid = {b["bid"]: b for b in layout.merged_buildings(city)}
        for bid, h, fl, ts in d["frontage"]:
            if int(byid[bid]["h"] / ST.FLOOR_BU) < 6:
                bad.append((seed, bid, "frontage under 6 floors"))
        from netrun_art import dress
        signs = dress.signs(d, dress.PRESET)
        cols = sorted(d["col_info"], key=lambda c: c["layer"])
        if sorted(s["bid"] for s in signs) != sorted(c["bid"] for c in cols):
            bad.append((seed, "-", "sign per column"))
        for k, c in enumerate(cols):
            s = next(x for x in signs if x["bid"] == c["bid"])
            if s["pal"] == s["band_pal"] or s["pal"] != dress.SIGN_PAL[k % 2]:
                bad.append((seed, c["bid"], "hero sign palette"))
    assert bad == []


def test_border_link_definition():
    net = {"nodes": [{"id": "a", "lot": [0, 0], "state": "core"}, {"id": "b", "lot": [1, 0], "state": "corporate"},
                     {"id": "c", "lot": [2, 0], "state": "cleared"}, {"id": "d", "lot": [3, 0], "state": "owned"}],
           "links": [{"a": "a", "b": "b", "state": "open", "pts": []}, {"a": "b", "b": "c", "state": "open", "pts": []},
                     {"a": "c", "b": "d", "state": "open", "pts": []}, {"a": "a", "b": "d", "state": "open", "pts": []},
                     {"a": "b", "b": "d", "state": "locked", "pts": []}, {"a": "b", "b": "d", "state": "opened", "pts": []}]}
    got = [(l["a"], l["b"], l["state"]) for l in layout.border_links(net)]
    assert got == [("a", "b", "open"), ("b", "d", "opened")]


def test_layout_rules_noop_without_border_link_and_pure():
    w = synth.make_world(5)
    net = dict(w["net"], links=[dict(l, state="locked") for l in w["net"]["links"]])
    before = str(w["city"])
    out = layout.apply_layout_rules(w["city"], net)
    assert out == w["city"] and str(w["city"]) == before


def test_layout_rules_raise_and_step_back():
    w = synth.make_world(7)
    st = {}
    out = layout.apply_layout_rules(w["city"], w["net"], stats=st)
    assert st["frontage"] > 0 and st["raised"] > 0 and st["moved"] > 0
    a = {b["bid"]: b for b in w["city"]["buildings"]}
    changed = [b for b in out["buildings"] if b != a[b["bid"]]]
    assert changed
    for b in changed:
        o = a[b["bid"]]
        assert b["parts"][0]["h"] >= o["parts"][0]["h"]


def test_floors_and_taper():
    b = dict(h=19.0, ts=1.0, x0=0, x1=6, y0=0, y1=6, axis=0)
    assert ST.floors(b) == 10
    t = dict(b, ts=0.5)
    assert ST.floors(t) < 10


@pytest.mark.parametrize("nrm", [(0.0, 1.0), (0.0, -1.0), (1.0, 0.0), (-1.0, 0.0)])
def test_quad_normalisation_all_four_cases(nrm):
    if nrm[0] == 0:
        q = [[0, 5, 0], [4, 5, 0], [4, 5, 2], [0, 5, 2]]
    else:
        q = [[5, 0, 0], [5, 4, 0], [5, 4, 2], [5, 0, 2]]
    n = ST.normalise_quad(q, nrm)
    right = (nrm[1], -nrm[0])
    assert (n[1][0] - n[0][0]) * right[0] + (n[1][1] - n[0][1]) * right[1] > 0
    assert n[0][2] == n[1][2] < n[2][2] == n[3][2]
    assert n[0][:2] == n[3][:2] and n[1][:2] == n[2][:2]


def test_derive_v2_conventions():
    out = producer.produce_world(synth.make_world(8))
    d = out["derive_street"]
    assert contract.validate_derive(d) == []
    a, c = d["street"]["a"], d["street"]["c"]
    for ci in d["col_info"]:
        assert ci["u0"] < ci["u1"] and ci["u1"] > 0 and ci["u0"] < math.hypot(c[0] - a[0], c[1] - a[1])
    # rig yaw: the camera looks along nrm, so yaw0 = atan2(nrm.x, nrm.y); OVERVIEW is offset by +-7.2
    ov = d["overview"]
    off = ov["yaw"] - rig.yaw_of_nrm(d["nrm"])
    assert abs(abs(off) - 7.2) < 1e-6 and (off > 0) == d["start_left"]
    dec = d["decision"]
    assert abs(abs(dec["yaw"] - rig.yaw_of_nrm(d["nrm"])) - 24.0) < 1e-6
    # frame fill: the first-decision rooms fit the usable area
    p = rig.Pose.from_json(dec)
    pts = [q for r in d["rooms"].values() if r["layer"] == 1 for q in rig.room_corners(r)]
    x0, y0, x1, y1 = rig.bbox_px(p, pts)
    assert (x1 - x0) <= 0.66 * rig.UW + 1 and (y1 - y0) <= 0.70 * rig.UH + 1
    assert d["span"] in (1, 2) and d["version"] == 2


def test_readers_reject_unknown():
    d = producer.produce_world(synth.make_world(9))["derive_street"]
    assert contract.validate_derive(dict(d, version=3))
    bad = dict(d, edges=[dict(d["edges"][0], type="tube")] + d["edges"][1:])
    assert contract.validate_derive(bad)
    r = dict(d["rooms"])
    k = sorted(r)[0]
    r[k] = dict(r[k], kind="elevator")
    assert contract.validate_derive(dict(d, rooms=r))
    r[k] = dict(r[k], kind="cache")          # accepted
    assert contract.validate_derive(dict(d, rooms=r)) == []
    dr = producer.produce_world(synth.make_world(9))["dress_street"]
    bad_dress = dict(dr, lamps=[dict(dr["lamps"][0], pal="red")] + dr["lamps"][1:])
    assert contract.validate_dress(bad_dress)
    assert contract.validate_dress(dict(dr, version=2))
    assert contract.validate_poses(dict(producer.produce_world(synth.make_world(9))["poses_street"], version=2))


def test_derive_error_reports_why():
    w = synth.make_world(3)
    city = layout.apply_layout_rules(w["city"], w["net"])
    rg = dict(w["run_graph"])
    rg["nodes"] = rg["nodes"] + [dict(id="L8N0", layer=8, index=0, type="router", elite=False)] * 0
    short = dict(city, buildings=[b for b in city["buildings"] if b["hq"]])
    with pytest.raises(ST.DeriveError):
        ST.derive_street(short, w["net"], rg, w["site"])
