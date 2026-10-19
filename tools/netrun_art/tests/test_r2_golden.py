"""Street r2 port (P2-P4 step 1): golden tests against the art-pass plate.

The fixtures (`fixtures/r2/`) are the art-pass `street_r2` output for the plate's own input at art seed 1, written by
`gen_r2_fixtures.py`, which also asserts at generation time that our port equals the art-pass modules exactly (no rounding). Here the
committed side is checked: the port on the committed input reproduces the committed expected text. `test_live_*` repeats the exact
comparison against a real art-pass checkout when one is present (R2_ART_PASS or the designer's worktree), and skips otherwise."""
import json
import os

import pytest

from netrun_art.r2 import canon, rules, signs
from netrun_art.tests import gen_r2_fixtures as GEN
from netrun_art.tests import r2_cases

FIX = GEN.FIX


def _read(*p):
    with open(os.path.join(FIX, *p), encoding="utf-8", newline="") as f:
        return f.read()


@pytest.fixture(scope="module")
def inp():
    return canon.load_input(os.path.join(FIX, "inputs", "s1_layout.json"))


@pytest.fixture(scope="module")
def laid(inp):
    city2, log = rules.layout_pass(inp["seed"], inp["city"], inp["links"], inp["derive"])
    return city2, log


@pytest.fixture(scope="module")
def plan(inp, laid):
    city2, log = laid
    return rules.plan_pass(inp["seed"], inp["derive"], city2, json.loads(json.dumps(log)))


def test_layout_pass_reproduces_the_plate(laid):
    city2, log = laid
    heights = {"%d_%d" % (b["ci"], b["key"]): b["h"] for b in city2["buildings"]}
    assert canon.dumps(dict(heights=heights, log=log)) == _read("expected", "s1_layout.json")


def test_plan_pass_reproduces_the_plate(plan):
    assert canon.dumps(plan) == _read("expected", "s1_plan.json")


def test_the_plate_plan_passes_its_own_rule_checks(plan):
    """R-REP-1 (max_same_module_run), R-DET-2 (props.facade, dressing.signs) and the silhouette / material / horizon checks."""
    ck = plan["checks"]
    assert {k: v["ok"] for k, v in ck.items()} == {k: True for k in ("frontage.silhouette", "materials.mix", "repetition.guard",
                                                                     "dressing.signs", "props.facade", "horizon.break")}
    assert ck["repetition.guard"]["max_same_module_run"] <= 2
    assert ck["props.facade"]["blocked_by_opening"] == [] and ck["props.facade"]["lamps_in_front_of_openings"] == 0
    assert ck["dressing.signs"]["off_face"] == [] and ck["dressing.signs"]["heroes"] == ck["dressing.signs"]["route_columns"]


def test_facade_kits_reproduce_the_plate():
    d = canon.load_input(os.path.join(FIX, "inputs", "s1_kits.json"))
    cases = r2_cases.unpack(d["cases"])
    rows = GEN.kit_expected(cases, GEN.run_port_kits(cases))
    assert canon.dumps(rows) == _read("expected", "s1_kits.json")
    assert {cs["kit"] for cs in cases} == {"glass_curtain", "panel_grille", "lit_atrium"}


def test_sign_draw_lists_reproduce_the_plate():
    d = canon.load_input(os.path.join(FIX, "inputs", "s1_signs.json"))
    specs = signs.make(r2_cases.unpack_signs(d["plan"]), signs.TableMeasure(d["measure"]))
    assert canon.dumps(specs) == _read("expected", "s1_signs.json")


def test_a_word_never_clips_its_sign():
    """The fit-to-sign rule: the chosen size fits the field, one size more does not (or the search ceiling is reached)."""
    d = canon.load_input(os.path.join(FIX, "inputs", "s1_signs.json"))
    m = signs.TableMeasure(d["measure"])
    specs = signs.make(r2_cases.unpack_signs(d["plan"]), m)
    n = 0
    for sid, sp in specs.items():
        for op in sp["ops"]:
            if op["op"] == "text" and sp["w"] and (op["font"], op["size"], op["s"]) in m.table:      # blade letters were fitted as "W"
                bw, bh = m(op["font"], op["size"], op["s"])
                assert bw <= sp["w"] and bh <= sp["h"], sid
                n += 1
    assert n > 50


def test_the_streams_are_the_plates():
    """Key text, art seed and Mersenne Twister draws of the committed vectors (the GDScript twin must reproduce them)."""
    assert canon.dumps(r2_cases.stream_vectors(), 2) == _read("expected", "streams.json")


# ------------------------------------------------------------------------------------------------ live comparison with the art-pass
ART = GEN.DEFAULT_ART


def _live_ok():
    try:
        import PIL  # noqa: F401
    except ImportError:
        return False
    return os.path.isdir(os.path.join(ART, "docs", "concepts", "route_map_graph", "street_r2", "scripts"))


@pytest.mark.skipif(not _live_ok(), reason="no art-pass checkout (set R2_ART_PASS) or no PIL")
def test_live_port_equals_the_art_pass_modules_exactly(tmp_path):
    from netrun_art.tests import r2_oracle
    work = str(tmp_path / "w")
    ref = r2_oracle.run(ART, GEN.SEED, work)
    raw = r2_oracle.raw_inputs(ART)
    D = ref["derive"]
    city = GEN.cut_city(raw, D)
    links = [dict(a=l["a"], b=l["b"], state=l["state"], pts=l["pts"]) for l in raw["net"]["links"] if l["state"] == "border"]
    city2, log = rules.layout_pass(GEN.SEED, city, links, D)
    assert GEN.jr(log) == ref["layout_log"]
    plan = rules.plan_pass(GEN.SEED, D, city2, GEN.jr(log))
    assert GEN.jr(plan) == ref["plan"]
    cases = r2_cases.kit_cases(plan)
    assert GEN.jr(GEN.run_port_kits(cases)) == r2_oracle.run_kits(ART, work, cases)
    sg = r2_oracle.run_signs(ART, work, GEN.jr(plan))
    assert GEN.jr(signs.make(plan, signs.TableMeasure(sg["measure"]))) == sg["specs"]
