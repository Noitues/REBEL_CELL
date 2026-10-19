"""Street r2 port: determinism, locality of the streams, the config twin, and the adapter on game-shaped worlds."""
import copy
import json
import os

import pytest

from netrun_art.derive import street as STREET
from netrun_art.r2 import adapter, canon, config, kits, rules, streams
from netrun_art.tests import gen_r2_adapter, gen_r2_fixtures as GEN
from netrun_art.tests import gen_inputs, r2_cases
from netrun_art import gen_street_r2_config as GENCFG


@pytest.fixture(scope="module")
def inp():
    return canon.load_input(os.path.join(GEN.FIX, "inputs", "s1_layout.json"))


@pytest.fixture(scope="module")
def merged(inp):
    city2, log = rules.layout_pass(inp["seed"], inp["city"], inp["links"], inp["derive"])
    return city2, json.loads(json.dumps(log))


# ---------------------------------------------------------------- streams and config
def test_art_seed_is_the_plate_formula_and_not_the_na02_one():
    import hashlib  # noqa: F401
    h = 0xcbf29ce484222325
    for b in json.dumps([1, "art/frontage", "1_2"]).encode():
        h = ((h ^ b) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    assert streams.art_seed(1, "frontage", "1_2") == h
    from netrun_art import seeds
    assert streams.art_seed(1, "frontage", "1_2") != seeds.art_seed(1, "frontage", "1_2")
    assert streams.art_seed(1, "lamp", 12.34567, -1) == streams.art_seed(1, "lamp", 12.3457, -1)     # float keys round to 4 decimals


def test_street_r2_tres_is_what_the_gen_script_writes():
    text = open(config.PATH, encoding="utf-8", newline="").read()
    want = ['[gd_resource type="Resource" script_class="StreetR2ConfigData" load_steps=2 format=3]', "",
            '[ext_resource type="Script" path="res://scripts/data/street_r2_config_data.gd" id="1_cfg"]', "", "[resource]",
            'script = ExtResource("1_cfg")'] + [f"{k} = {GENCFG.val(v)}" for k, v in GENCFG.fields()]
    assert text == "\n".join(want) + "\n"
    assert config.R["props.facade"]["kinds"] == GENCFG.RULES_R2["props_facade"]["kinds"]
    assert list(config.R["props.facade"]["kinds"]) == ["ac", "pipe", "awning", "small_sign", "lit_room"]       # weights follow this order
    assert config.R["horizon.break"]["spike_spacing"] == 1.0 / 6.0


# ---------------------------------------------------------------- determinism and locality
def test_plan_is_a_pure_function_of_its_input(inp, merged):
    city2, log = merged
    a = rules.plan_pass(inp["seed"], inp["derive"], city2, log)
    b = rules.plan_pass(inp["seed"], inp["derive"], copy.deepcopy(city2), copy.deepcopy(log))
    assert canon.dumps(a) == canon.dumps(b)
    c = rules.plan_pass(2, inp["derive"], city2, log)
    assert canon.dumps(a) != canon.dumps(c)
    assert c["checks"]["dressing.signs"]["route_columns"] == a["checks"]["dressing.signs"]["route_columns"]    # the street itself does not move


def test_removing_a_far_building_moves_no_other_buildings_facade(inp, merged):
    """Spec 3.5: every draw is keyed by content ids, so a building's rhythm and its facade props survive an unrelated building going."""
    city2, log = merged
    a = rules.plan_pass(inp["seed"], inp["derive"], city2, log)
    front = set(a["front"])
    drop = next(b for b in rules.OC.merged_buildings(city2["buildings"]) if b["uid"] not in front and b["uid"] in a["rhythm"]
                and b["uid"] not in set(a["spikes"]))
    c2 = copy.deepcopy(city2)
    c2["buildings"] = [b for b in c2["buildings"] if "%d_%d" % (b["ci"], b["key"]) != drop["uid"]]
    b = rules.plan_pass(inp["seed"], inp["derive"], c2, log)
    assert drop["uid"] not in b["rhythm"]
    assert all(canon.dumps(b["rhythm"][k]) == canon.dumps(v) for k, v in a["rhythm"].items() if k != drop["uid"] and k in b["rhythm"])
    keep = [p for p in a["props"] if p["key"] != drop["uid"]]
    assert canon.dumps(keep) == canon.dumps([p for p in b["props"]])


def test_facade_kits_are_deterministic_and_stay_on_their_face(inp, merged):
    city2, log = merged
    plan = rules.plan_pass(inp["seed"], inp["derive"], city2, log)
    cases = r2_cases.kit_cases(plan)
    assert canon.dumps(GEN.kit_expected(cases, GEN.run_port_kits(cases))) == canon.dumps(GEN.kit_expected(cases, GEN.run_port_kits(cases)))
    face = [c for c in cases if c["op"] == "face" and c.get("rh") and not c.get("lite")][:3]
    ax = plan["axis"]
    for cs, r in zip(face, GEN.run_port_kits(face)):
        along = [p[ax] for acc in r.values() for f in acc for p in f["pts"]]
        out = [p[1 - ax] for acc in r.values() for f in acc for p in f["pts"]]
        lo, hi = sorted((cs["a"][ax], cs["c"][ax]))
        assert along and min(along) >= lo - 1e-6 and max(along) <= hi + 1e-6, "cells stay between the face ends"
        assert max(abs(v - cs["a"][1 - ax]) for v in out) <= 1.6, "relief, ledges and balconies stay within 1.6 BU of the face"


def test_sign_rectangles_sit_on_their_building(inp, merged):
    city2, log = merged
    plan = rules.plan_pass(inp["seed"], inp["derive"], city2, log)
    assert plan["checks"]["dressing.signs"]["off_face"] == []
    kinds = {s["kind"] for s in plan["signs"]}
    assert {"shopfront", "shop_sign", "hero_blade", "hero_wall"} & kinds
    assert all(s["tex"]["style"] in ("box", "blade", "wall", "ad", "holo", "shop") for s in plan["signs"])


# ---------------------------------------------------------------- the adapter on game-shaped worlds
@pytest.mark.parametrize("seed", [101, 105])
def test_adapted_street_has_a_plate_style_plan(seed):
    w, city = gen_inputs.world(seed)
    d = STREET.derive_street(city, w["net"], w["run_graph"], w["site"])
    x = adapter.r2_input(city, d, w["seed"])
    assert x["D"]["column_uids"] == [b for _, b in d["columns"]]
    assert x["D"]["side"] in (1, -1)
    plan = rules.plan_pass(x["seed"], x["D"], None, x["layout_log"], merged=x["merged"], terr=x["terr"])
    ck = plan["checks"]
    assert ck["dressing.signs"]["ok"] and ck["props.facade"]["ok"] and ck["repetition.guard"]["ok"] and ck["horizon.break"]["ok"]
    assert set(plan["route"]) == {b for _, b in d["columns"]}
    bids = {b["bid"] for b in city["buildings"]}
    assert {s["key"] for s in plan["signs"]} <= bids and set(plan["kits"]) <= bids
    # keyed by bid and art seed: the same street twice is the same plan; another art seed changes the dressing, not the street
    again = adapter.plan_street(city, d, w["seed"])
    assert canon.dumps(again) == canon.dumps(plan)
    other = adapter.plan_street(city, d, int(w["seed"]) + 1)
    assert canon.dumps(other) != canon.dumps(plan) and other["route"] == plan["route"] and other["front"] == plan["front"]


def test_adapter_camera_projects_like_the_rig():
    w, city = gen_inputs.world(101)
    d = STREET.derive_street(city, w["net"], w["run_graph"], w["site"])
    from netrun_art import rig
    from netrun_art.r2 import onecity
    D = adapter.street_derivation(d)
    for name in ("overview", "decision"):
        pose = rig.Pose.from_json(d[name])
        for p in ([d["street"]["a"][0] + 3.0, d["street"]["a"][1] + 2.0, 5.0], [d["street"]["c"][0], d["street"]["c"][1], 1.0]):
            a, b = pose.proj(p), onecity.proj(D[name], p)
            assert a is not None and abs(a[0] - b[0]) < 1e-6 and abs(a[1] - b[1]) < 1e-6


def test_adapter_fixtures_are_current():
    """`adapter_*.json` is what the adapter produces now (the GDScript twin reproduces it)."""
    plan = gen_r2_adapter.adapted_plan(gen_r2_adapter.SEEDS[0])
    got = canon.dumps(plan)
    want = open(os.path.join(gen_r2_adapter.FIX, "adapter_%d.json" % gen_r2_adapter.SEEDS[0]), encoding="utf-8", newline="").read()
    assert got == want
    digs = json.load(open(os.path.join(gen_r2_adapter.FIX, "adapter_digests.json"), encoding="utf-8"))
    for s in gen_r2_adapter.SEEDS[1:]:
        p = gen_r2_adapter.adapted_plan(s)
        assert {k: canon.digest(v) for k, v in p.items()} == digs[str(s)]
