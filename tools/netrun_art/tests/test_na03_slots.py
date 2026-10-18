import pytest

from netrun_art import contract
from netrun_art.hq import orbit, slots
from netrun_art.tests import synth

RECT = (-27.0, -9.0, -9.0, 9.0)      # an 18 x 18 BU lot


def graph(counts):
    nodes, edges = [], []
    for l, n in enumerate(counts, 1):
        for k in range(n):
            nodes.append(dict(id=f"L{l}N{k}", layer=l, index=k, type="router", elite=False))
    for l in range(1, len(counts)):
        for k in range(counts[l]):
            edges.append(dict(a=f"L{l}N{min(k, counts[l - 1] - 1)}", b=f"L{l + 1}N{k}"))
    return dict(version=1, run="r", layers=len(counts), nodes=nodes, edges=edges)


GRAPHS = {
    "gdd_7x2to4": graph([2, 3, 4, 2, 3, 4, 1]),
    "five_wide": graph([1, 6, 5, 6, 1]),
    "nine_deep": graph([3, 2, 4, 3, 2, 4, 3, 2, 1]),
}


@pytest.mark.parametrize("name", sorted(GRAPHS))
def test_every_node_placed_no_overlap_inside_lot(name):
    g = GRAPHS[name]
    rooms = slots.place_slots(g, RECT, "hq:meridian", 3)
    assert sorted(rooms) == sorted(n["id"] for n in g["nodes"])
    assert slots.overlaps(rooms) == []
    assert all(slots.inside_rect(r, RECT) for r in rooms.values())


def test_three_graphs_differ():
    shapes = {name: tuple(sorted(r["layer"] for r in slots.place_slots(g, RECT, "hq:x").values())) for name, g in GRAPHS.items()}
    assert len(set(shapes.values())) == 3


def test_deterministic_and_order_independent():
    g = GRAPHS["gdd_7x2to4"]
    a = slots.place_slots(g, RECT, "hq:m")
    g2 = dict(g, nodes=list(reversed(g["nodes"])))
    assert slots.place_slots(g2, RECT, "hq:m") == a


def test_fixture_hq_in_real_lot():
    w = synth.make_world(7)
    d = slots.derive_hq(w["city"], w["run_graph"], w["corp"])
    rect = slots.hq_lot_rect(w["city"], w["corp"])
    assert contract.validate_derive(d) == []
    assert all(slots.inside_rect(r, rect) for r in d["rooms"].values())
    assert slots.overlaps(d["rooms"]) == []
    assert "street" not in d and d["kind"] == "hq" and all(e["type"] == "hq" for e in d["edges"])


def test_lot_too_small():
    with pytest.raises(slots.SlotError):
        slots.place_slots(GRAPHS["five_wide"], (0, 3.0, 0, 3.0), "hq:x")


def test_orbit_faces_and_visibility():
    g = GRAPHS["gdd_7x2to4"]
    rooms = slots.place_slots(g, RECT, "hq:m")
    for r in rooms.values():
        n = orbit.room_normal(r)
        assert abs(n[0] ** 2 + n[1] ** 2 - 1) < 1e-9
    r = rooms["L1N0"]
    dec = orbit.hq_decision(rooms, None, ["L1N0", "L1N1"], 0, 7)
    assert dec.dist >= orbit.HQ_RIG["dmin"] - 1e-9
    hov = orbit.hq_hover(dec, r)
    assert hov.dist < dec.dist
    assert orbit.visible_room(r, dec) in (True, False)


def test_first_decision_frames_the_entrance_slot():
    g = GRAPHS["gdd_7x2to4"]
    rooms = slots.place_slots(g, RECT, "hq:m")
    comp = slots.plan_compound(RECT, 7)
    slots.set_entrance(comp, orbit.hq_overview(rooms, comp, ["L1N0", "L1N1"], None))
    ent = comp["entrance"]
    first = ["L1N0", "L1N1"]
    plain = orbit.hq_decision(rooms, None, first, 0, 7)
    framed = orbit.hq_decision(rooms, None, first, 0, 7, None, ent)
    assert framed.to_json() != plain.to_json()                              # the anchor changes the framing
    assert framed.proj(ent) is not None                                     # and the anchor is in view
    cur = orbit.hq_decision(rooms, "L1N0", first, 0, 7, None, ent)
    assert cur.to_json() == orbit.hq_decision(rooms, "L1N0", first, 0, 7).to_json()   # a real current ignores it


def _yaw_pose(look_xy):
    """A pose whose view direction in plan is `look_xy` (the camera sits on the opposite side)."""
    import math
    return orbit.Pose([0.0, 0.0, 0.0], math.degrees(math.atan2(look_xy[0], look_xy[1])), 30.0, 50.0, 50.0)


def test_entrance_face_follows_overview_camera_and_ties_n_e_s_w():
    comp = slots.plan_compound(RECT, 7)
    cx, cy, h = comp["centre"][0], comp["centre"][1], comp["half"][0]
    east = slots.set_entrance(dict(comp), _yaw_pose((-1.0, 0.0)))        # looking west: the camera sits east
    assert east["entry_nrm"] == [1.0, 0.0] and east["entrance"] == [cx + h, cy, 0.0]
    south = slots.set_entrance(dict(comp), _yaw_pose((0.0, 1.0)))
    assert south["entry_nrm"] == [0.0, -1.0] and south["entrance"] == [cx, cy - h, 0.0]
    # corner overviews tie two faces exactly: N before E before S before W
    assert slots.set_entrance(dict(comp), _yaw_pose((-1.0, -1.0)))["entry_nrm"] == [0.0, 1.0]     # camera NE: N
    assert slots.set_entrance(dict(comp), _yaw_pose((-1.0, 1.0)))["entry_nrm"] == [1.0, 0.0]      # camera SE: E
    assert slots.set_entrance(dict(comp), _yaw_pose((1.0, 1.0)))["entry_nrm"] == [0.0, -1.0]      # camera SW: S
    assert slots.set_entrance(dict(comp), _yaw_pose((1.0, -1.0)))["entry_nrm"] == [0.0, 1.0]      # camera NW: N
    slots.LANDMARK_ENTRIES["zz"] = {"entry": [1.0, 2.0, 0.5], "entry_nrm": [0, 1]}
    try:
        o = slots.set_entrance(dict(comp), _yaw_pose((0.0, 1.0)), "zz")
        assert o["entrance"] == [cx + 1.0, cy + 2.0, 0.5] and o["entry_nrm"] == [0.0, 1.0]
    finally:
        del slots.LANDMARK_ENTRIES["zz"]
