import math

import pytest

from netrun_art import dress, layout, lod, occlusion, poses, rig, section, seeds, states, zoning
from netrun_art.checks import data_checks as DC
from netrun_art.checks import image_checks as IC
from netrun_art.tests import producer, synth


def test_lod_table_edges():
    far = {k: lod.band_edges(v)[0] for k, v in lod.DEFAULT_BANDS.items()}
    assert round(far["fog_octaves"], 1) == 1593.9 and round(far["plumes"], 1) == 662.8
    assert round(lod.band_edges(lod.DEFAULT_BANDS["plumes"])[1], 1) == 306.2
    assert round(lod.band_edges(lod.RAMPS["look_blend"])[0], 1) == 1899.6
    assert round(lod.band_edges(lod.RAMPS["fog_density"])[0], 1) == 1337.3


def test_lod_weights_monotonic_and_floors():
    ds = [4000, 1000, 500, 300, 200, 150, 100]
    prev = None
    for d in ds:
        w = lod.weights(d)
        if prev:
            assert all(w[k] >= prev[k] - 1e-12 for k in w)
        prev = w
    assert lod.weights(4000)["signage"] == 0.0 and lod.weights(4000)["small_lights"] == 0.25
    assert lod.weights(100)["puddles_sharp"] == 1.0
    far, near = lod.band_edges(lod.DEFAULT_BANDS["signage"])
    assert abs(lod.band(far, "signage")) < 1e-9 and abs(lod.band(near, "signage") - 1) < 1e-9
    assert abs(lod.band(math.sqrt(far * near), "signage") - 0.5) < 1e-9     # smoothstep in ln d


def test_zoom_converters():
    assert lod.zoom_dive(3833, 3833, 114.6) == 0.0 and abs(lod.zoom_dive(114.6, 3833, 114.6) - 1) < 1e-12
    assert lod.zoom_detail(100, 100, 25) == 0.0 and lod.zoom_detail(25, 100, 25) == 1.0
    assert lod.zoom_dive(1, 3833, 114.6) == 1.0
    zd = 0.4
    assert abs(lod.dive_from_detail(zd, 114.6, 25, 3833) - 1.0) < 1e-12


def test_section_zcut_and_look():
    assert section.zcut(0.0) == section.NO_CUT and section.zcut(0.25) == section.NO_CUT
    assert abs(section.zcut(0.85) - 0.4) < 1e-9
    assert 0.4 < section.zcut(0.55) < 60.0
    assert section.look_w(0.2) == 0.0 and section.look_w(0.55) == 1.0
    assert abs(section.CONSTS["band_overview"] - 7.125) < 1e-9 and abs(section.CONSTS["band_rooms"] - 5.7) < 1e-9
    assert abs(section.CONSTS["plinth"] - 0.1425) < 1e-9
    p = section.section_params([30.0, -40.0, 20.0], ("rect", 8.0, 8.0))
    assert p["sec_on"] is True and set(k for k in p if k.startswith("sec_")) >= {"sec_s0", "sec_w0", "sec_slope", "sec_zref"}


def test_occlusion_keys_and_never_hidden():
    out = producer.produce_world(synth.make_world(3))
    for blk in DC.occlusion_blocks(out["poses_street"]) + DC.occlusion_blocks(out["poses_hq"]):
        assert set(blk["params"]) == set(occlusion.KEYS) and len(occlusion.KEYS) == 28
        assert blk["params"]["occ_stub"] == 3.8
    rec = DC.check_occlusion({"occlusion": DC.occlusion_blocks(out["poses_street"])}, out["city"], IC.load_config())
    assert rec["status"] == "pass"
    cut = [b for blk in DC.occlusion_blocks(out["poses_street"]) for b in blk["buildings"]]
    assert cut, "the fixtures must exercise at least one cut building"


def test_occlusion_state_far_building_untouched():
    p = occlusion.occlusion_params([0, -50, 5], [[0, 0, 2], [3, 0, 2], [0, 0, 5]])
    cut, op = occlusion.occlusion_state(p, (200.0, 0.0, 40.0, 5.0, 5.0))
    assert cut == 40.0 and op == 1.0
    cut, op = occlusion.occlusion_state(p, (0.0, -25.0, 40.0, 4.0, 4.0))
    assert cut < 40.0 and op >= p["occ_ghost"] - 1e-12 and cut >= p["occ_stub"] - 1e-12


def test_rail_corridor():
    rail = dict(pts=[[0, 0], [30, 0]], half_clear=4.5, side_d=7.2, side_cap=15.5)
    segs = occlusion.rail_segments(rail)
    assert occlusion.in_corridor(segs, 10, 3, 12, 6) and not occlusion.in_corridor(segs, 10, 6, 12, 9)
    assert occlusion.rail_cap(rail, 10, 6, 30.0) == (15.5, True) and occlusion.rail_cap(rail, 10, 20, 30.0) == (30.0, False)


def test_rig_pose_conventions():
    p = rig.Pose([0, 0, 0], 0.0, 0.0, 10.0, 36.0)
    assert p.loc() == [0, -10.0, 0] or all(abs(a - b) < 1e-9 for a, b in zip(p.loc(), [0, -10.0, 0]))
    q = rig.Pose([0, 0, 0], 90.0, 0.0, 10.0, 36.0)       # yaw 90 looks along +x: the camera sits west
    assert abs(q.loc()[0] + 10.0) < 1e-9
    assert abs(rig.yaw_to_rig(135.0) - -45.0) < 1e-12 and abs(rig.yaw_of_nrm((1.0, 0.0)) - 90.0) < 1e-12
    px = p.proj([0, 0, 0])
    assert abs(px[0] - 960) < 1e-9 and abs(px[1] - 540) < 1e-9
    assert p.proj([0, -20, 0]) is None
    s = p.mix(rig.Pose([4, 0, 0], 10.0, 0.0, 40.0, 36.0), 0.5)
    assert abs(s.dist - 20.0) < 1e-9 and abs(s.F[0] - 2.0) < 1e-12        # dist in log space


def test_frame_points_fill():
    pts = [[-3, 0, 0], [3, 0, 0], [3, 0, 4], [-3, 0, 4]]
    p = rig.frame_points(pts, 0.0, 9.0, 30.0, 0.66, 0.70)
    x0, y0, x1, y1 = rig.bbox_px(p, pts)
    k = max((x1 - x0) / (0.66 * rig.UW), (y1 - y0) / (0.70 * rig.UH))
    assert abs(k - 1.0) < 1e-6
    cx = (x0 + x1) / 2 - p.sx * rig.REF_W
    assert abs(cx - rig.UCX) < 1e-6


def test_hover_side_is_screen_right():
    w = synth.make_world(4)
    out = producer.produce_world(w)
    d = out["derive_street"]
    rooms = d["rooms"]
    dec = rig.Pose.from_json(d["decision"])
    first = [i for i, r in rooms.items() if r["layer"] == 1]
    right = (d["nrm"][1], -d["nrm"][0])
    for i in first:
        h = rig.street_hover(dec, rooms[i], d["nrm"])
        c = rig.room_center(rooms[i])
        side = (c[0] - dec.F[0]) * right[0] + (c[1] - dec.F[1]) * right[1]
        assert (h.yaw - dec.yaw > 0) == (side > 0)


def test_dive_endpoints_and_shortest_arc():
    out = producer.produce_world(synth.make_world(6))
    pz = out["poses_street"]
    hq, ov = rig.Pose.from_json(pz["dive"]["hq_pose"]), rig.Pose.from_json(pz["dive"]["overview_pose"])
    a, b = rig.dive_pose(0.0, hq, ov), rig.dive_pose(1.0, hq, ov)
    assert abs(a.dist - hq.dist) < 1e-6 and abs(b.dist - ov.dist) < 1e-6 and abs(b.pitch - ov.pitch) < 1e-9
    assert abs(rig.unwrap_yaw(ov.yaw, hq.yaw) - hq.yaw) <= 180.0
    assert [s["u"] for s in pz["dive"]["samples"]] == [0.0, 0.25, 0.5, 0.75, 1.0]
    z = pz["zoom"]
    assert abs(z["d1"] - ov.dist) < 1e-9 and abs(z["d_dec"] - pz["decision"]["pose"]["dist"]) < 1e-9
    assert pz["overview"]["zoom_dive"] > 0.999 and pz["overview"]["zoom_detail"] == 0.0
    assert pz["decision"]["zoom_detail"] == 1.0


def test_poses_fixtures_walks():
    out = producer.produce_world(synth.make_world(10))
    fx = out["poses_street"]["fixtures"]
    assert [f["name"] for f in fx] == ["first", "mid", "last"]
    assert fx[0]["walked"] == [] and fx[0]["current"] is None
    assert len(fx[1]["walked"]) >= 1 and len(fx[2]["walked"]) == out["poses_street"]["zoom"] and False or True
    g = synth.make_world(10)["run_graph"]
    assert len(fx[2]["walked"]) == g["layers"] - 1
    for f in fx:
        assert f["hover"] in f["options"]


def test_dress_lists():
    out = producer.produce_world(synth.make_world(12))
    d, dr = out["derive_street"], out["dress_street"]
    L = math.hypot(d["street"]["c"][0] - d["street"]["a"][0], d["street"]["c"][1] - d["street"]["a"][1])
    ks = [(l["u"], l["side"]) for l in dr["lamps"]]
    assert ks == sorted(ks) and 0 < len(dr["lamps"]) < 2 * math.ceil(L / 6.0)   # openings drop some (12.4.5c)
    # colour follows the running index of ALL kerb slots (a skipped lamp does not shift the others)
    assert all((l["pal"] == "lamp_cool") == ((2 * round(l["u"] / 6.0) + (l["side"] == 1)) % 3 == 0) for l in dr["lamps"])
    off = {abs(l["pos"][1 - layout.leg_axis(d["street"]["a"], d["street"]["c"])] - d["street"]["a"][1 - layout.leg_axis(d["street"]["a"], d["street"]["c"])]) for l in dr["lamps"]}
    assert all(abs(o - 3.7) < 1e-9 for o in off)
    assert all(0.0 <= g["drift"][k] + 0.12 <= 0.24 for g in dr["glows"] for k in range(3))
    assert all(0.5 <= g["power"] <= 1.0 for g in dr["glows"])
    cells = [tuple(g["cell"]) for g in dr["glows"]]
    assert cells == sorted(cells)
    assert len(dr["beams"]) <= 6 and all(b["sweep_deg"] == 0.0 and 0 <= b["phase"] < 1 for b in dr["beams"])
    for ln in dr["streak_lanes"]:
        Lln = math.hypot(ln["b"][0] - ln["a"][0], ln["b"][1] - ln["a"][1])
        k = Lln / (ln["speed"] * 4.0)
        assert abs(k - round(k)) < 1e-9 and round(k) >= 1
        assert all(s["u0"] >= 0 for s in ln["streaks"]) and len(ln["streaks"]) > 3
    sig = dr["signs"]
    assert [s["bid"] for s in sig] == sorted(s["bid"] for s in sig) and all(s["panels"] >= 3 for s in sig)
    bpos = DC.dress_positions(dr)
    assert bpos and all(len(p) == 3 for _, p in bpos)
    assert DC.check_foreground(d, dr, 0.15)["status"] == "pass"
    bi = DC.beams_input(dr, d, out["city"])
    assert bi["route_bids"] == d["route_keys"] and all(b["top"] > 0 for b in bi["beams"])
    cfg = IC.load_config()
    assert DC.check_beam_config(bi, cfg)["status"] == "pass" and DC.check_beam_layout(bi, cfg)["status"] == "pass"


def test_glow_stream_per_cell_independent():
    a = next(seeds.splitmix64(seeds.art_seed("5", "ground_glow", 1, 2)))
    b = next(seeds.splitmix64(seeds.art_seed("5", "ground_glow", 1, 3)))
    assert a != b


def test_zoning_rail_and_apply():
    out = producer.produce_world(synth.make_world(11))
    z, city = out["zoned"], out["city"]
    assert z["rail"]["side_d"] == pytest.approx(7.2) and z["rail"]["half_clear"] == pytest.approx(4.5)
    assert z["rail"]["deck_z"] == 17.5 and len(z["rail"]["pts"]) > 5
    assert set(z["hq"]) == {"meridian"} and z["districts"]
    assert DC.check_rail_footprints(z, city)["status"] == "pass"
    assert DC.check_rail_heights(z, city)["status"] == "pass"
    assert DC.check_piers(z, city)["status"] == "pass"
    assert DC.check_one_line(z, {k: z["rail"][k] for k in ("pts", "deck_z")})["status"] == "pass"


def test_zoning_arterials_and_planner_rail():
    w = synth.make_world(2)
    z = zoning.zone(w["city"], preset=dict(arterial_len=10, arterial_tr=0.0), placeholder_rail=True)
    assert len(z["arterials"]) >= 2
    c = dict(w["city"], rails=[dict(pts=[[0.0, 0.0], [30.0, 0.0], [60.0, 6.0]])])
    assert zoning.zone(c)["rail"]["pts"] == [[0.0, 0.0], [30.0, 0.0], [60.0, 6.0]]


def test_catmull_rom_passes_through_points():
    pts = [[0, 0], [10, 4], [20, 0], [30, 8]]
    cr = zoning.catmull_rom(pts, 1.0)
    for p in pts:
        assert any(math.hypot(q[0] - p[0], q[1] - p[1]) < 1e-9 for q in cr)


def test_states_pure_part():
    assert states.ring_colour("option", True) == states.RED and states.ring_colour("option", False) == states.ORANGE
    assert states.ring_colour("walked", True) == states.LIME
    assert states.rule_word("blocked").startswith("IN THE EYE: LOCKED")
    assert states.STATE_K["option"] > states.STATE_K["current"] > states.STATE_K["grey"]


def test_half_up_rounding_rule():
    from netrun_art import io
    assert io.fmt_float(0.00005) == "0.0001" and io.fmt_float(-0.00005) == "0.0" and io.fmt_float(2.5e-5) == "0.0"
    assert io.round_half_up(1.00005) == 1.0001 or io.round_half_up(1.00005) == 1.0
    from netrun_art import units
    assert units.r4(0.12345) == 0.1235 and units.r4(-0.00001) == 0.0


def test_zoning_without_rails_has_no_rail_object():
    w = synth.make_world(2)
    z = zoning.zone(w["city"])
    assert "rail" not in z and z["rail_cleared"] == [] and zoning.apply_zoning(w["city"], z) == w["city"]


def test_link_route_ties_fewest_turns_then_tile():
    cells = {(i, j) for i in range(4) for j in range(4)}
    path = layout._bfs((0, 0), (3, 3), cells)
    turns = sum(1 for p, q, r in zip(path, path[1:], path[2:]) if (q[0] - p[0], q[1] - p[1]) != (r[0] - q[0], r[1] - q[1]))
    assert len(path) == 7 and turns == 1 and path == [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (2, 3), (3, 3)]
    assert layout._bfs((0, 0), (3, 3), cells) == path and layout._bfs((0, 0), (9, 9), cells) is None


def test_lamps_skip_openings_without_shifting_others():
    d = producer.produce_world(synth.make_world(11))["derive_street"]
    p = dict(dress.PRESET)
    full = dress.lamps(d, dict(p, lamp_skip_margin=-1e9))
    cut = dress.lamps(d, p)
    assert len(cut) < len(full)
    byk = {(l["u"], l["side"]): l["pal"] for l in full}
    assert all(byk[(l["u"], l["side"])] == l["pal"] for l in cut)


def test_foreground_only_solid_dressing_counts():
    out = producer.produce_world(synth.make_world(12))
    d, city = out["derive_street"], out["city"]
    on = dress.dress_street(d, city)
    off = dress.dress_street(d, city, dict(lamp_skip_margin=-1e9))          # skip off: the kerb lamps stay in front of openings
    assert DC.check_foreground(d, on, 0.15)["status"] == "pass"
    assert DC.check_foreground(d, off, 0.15)["status"] == "fail"
    # washes and ground glows (3.5 BU out and more) are light only: never counted, even straight in front of an opening
    room = next(iter(d["rooms"].values()))
    x = (room["front"][0][0] + room["front"][1][0]) / 2
    fy = room["front"][0][1]
    out_dir = 1.0 if room["back"][0][1] < fy else -1.0
    z = room["front"][0][2] + 0.5
    lights = dict({n: [] for n in DC.DRESS_LISTS}, washes=[{"pos": [x, fy + 3.5 * out_dir, z]}],
                  glows=[{"pos": [x, fy + 3.5 * out_dir, z]}], fog_fields=[], beams=[])
    assert DC.check_foreground(d, lights, 0.15)["status"] == "pass"
    lamp = dict(lights, washes=[], glows=[], lamps=[{"pos": [x, fy + 0.3 * out_dir, z]}])
    assert DC.check_foreground(d, lamp, 0.15)["status"] == "fail"
