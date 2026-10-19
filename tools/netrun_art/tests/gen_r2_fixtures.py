"""Street r2 golden fixtures (P2-P4 step 1): the art-pass plate's own input at art seed 1, and the art-pass output on it.

Run from `tools/`:  `python -m netrun_art.tests.gen_r2_fixtures [art-pass checkout]`  (default `$R2_ART_PASS`, else the designer's
art-pass worktree). Needs Python with PIL (the sign fonts). It

1. runs the art-pass `street_r2` modules from a temp copy (`r2_oracle`): `layout_pass(1)`, `plan_pass(1)`, `kit_face` /
   `roof_clutter` on the cases of `r2_cases`, and the sign textures with their PIL draw calls recorded;
2. runs our port (`netrun_art.r2`) on the same input and asserts it equals the art-pass output EXACTLY (no rounding);
3. writes the committed fixtures `fixtures/r2/inputs/*` (exact doubles as hex strings) and `fixtures/r2/expected/*` (canonical text
   of the art-pass output, 1e-6): only the expected side comes from the art-pass, nothing of the art-pass code is committed.

The city is cut to the buildings within `RADIUS` BU of the street midpoint: the plan reads nothing farther (checked: the cut city
gives the same plan as the whole city).
"""
import json
import math
import os
import sys
from typing import Any, Dict, List

from netrun_art.r2 import canon, onecity as OC, rules, signs
from netrun_art.r2.kits import Faces, kit_face, new_accs, roof_clutter
from netrun_art.tests import r2_cases, r2_oracle

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures", "r2")
SEED = 1
RADIUS = 300.0
DEFAULT_ART = os.environ.get("R2_ART_PASS", r"D:\rc_art\art-pass")


def jr(v: Any) -> Any:
    """JSON round trip (tuples become lists, as in the art-pass output files)."""
    return json.loads(json.dumps(v))


def slim_building(b: Dict[str, Any]) -> Dict[str, Any]:
    """The fields of a lot record the rules read."""
    return dict(ci=b["ci"], key=b["key"], terr=b["terr"], q=b["q"], z0=b["z0"], h=b["h"], ts=b["ts"])


def cut_city(raw: Dict[str, Any], D: Dict[str, Any]) -> Dict[str, Any]:
    """The raw v3 city restricted to `RADIUS` BU around the street midpoint, with the one HQ position the layout pass reads."""
    mid = ((D["a"][0] + D["c"][0]) / 2, (D["a"][1] + D["c"][1]) / 2)
    keep = []
    for b in raw["city"]["buildings"]:
        i = OC.bld_info(b)
        if math.hypot((i["x0"] + i["x1"]) / 2 - mid[0], (i["y0"] + i["y1"]) / 2 - mid[1]) <= RADIUS:
            keep.append(slim_building(b))
    return dict(buildings=keep, hqs=dict(meridian=raw["city"]["hqs"]["meridian"]))


def run_port_kits(cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Our port on the kit cases, recorded in the shape of the oracle driver."""
    import random
    out = []
    for cs in cases:
        r = random.Random(cs["seed"])
        if cs["op"] == "face":
            accs = new_accs()
            kit_face(cs["kit"], cs["a"], cs["c"], cs["z0"], cs["z1"], cs["nx"], cs["ny"], cs["col"], r, accs, module=cs["module"],
                     fl=cs.get("fl", 1.9), lit_low=cs.get("lit_low"), lite=cs.get("lite", False), rh=cs.get("rh"))
            out.append({k: v.faces for k, v in accs.items()})
        else:
            solid, neon, kinds, ants = Faces(), Faces(), set(), []
            roof_clutter(cs["kit"], cs["top"], cs["zt"], r, solid, neon, kinds, ants)
            out.append(dict(faces=solid.faces, prims=solid.prims, neon=neon.faces, kinds=sorted(kinds), ants=[list(a) for a in ants]))
    return out


def kit_expected(cases: List[Dict[str, Any]], results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Per case: a short name, the face counts per material, and the digest of the recorded output."""
    rows = []
    for cs, res in zip(cases, results):
        if cs["op"] == "face":
            counts = {k: len(v) for k, v in res.items()}
        else:
            counts = dict(faces=len(res["faces"]), prims=len(res["prims"]), neon=len(res["neon"]), ants=len(res["ants"]))
        rows.append(dict(name="%s:%s:%s" % (cs["op"], cs["kit"], cs["uid"]), counts=counts, digest=canon.digest(res)))
    return rows


def main(art_root: str) -> None:
    work = os.path.join(os.environ.get("TEMP", "."), "r2_oracle_work")
    print("art-pass", r2_oracle.art_commit(art_root))
    ref = r2_oracle.run(art_root, SEED, work)
    raw = r2_oracle.raw_inputs(art_root)
    D = ref["derive"]
    city = cut_city(raw, D)
    links = [dict(a=l["a"], b=l["b"], state=l["state"], pts=l["pts"]) for l in raw["net"]["links"] if l["state"] == "border"]
    inp = dict(seed=SEED, city=city, links=links, derive=D)
    # ---- the port on the cut city equals the art-pass output on the whole city
    city2, log = rules.layout_pass(SEED, city, links, D)
    plan = rules.plan_pass(SEED, D, city2, jr(log))
    assert jr(plan) == ref["plan"], "port plan differs from the art-pass plan"
    assert jr(log) == {k: v for k, v in ref["layout_log"].items()}, "port layout log differs"
    ref_h = {"%d_%d" % (b["ci"], b["key"]): b["h"] for b in ref["buildings"]}
    heights = {"%d_%d" % (b["ci"], b["key"]): b["h"] for b in city2["buildings"]}
    assert all(ref_h[k] == v for k, v in heights.items()), "port heights differ from the art-pass layout"
    os.makedirs(os.path.join(FIX, "inputs"), exist_ok=True)
    os.makedirs(os.path.join(FIX, "expected"), exist_ok=True)
    canon.dump_input(inp, os.path.join(FIX, "inputs", "s1_layout.json"))
    write(os.path.join(FIX, "expected", "s1_layout.json"), canon.dumps(dict(heights=heights, log=log)))
    write(os.path.join(FIX, "expected", "s1_plan.json"), canon.dumps(plan))
    # ---- facade kits
    cases = r2_cases.kit_cases(plan)
    ref_k = r2_oracle.run_kits(art_root, work, cases)
    mine = run_port_kits(cases)
    assert jr(mine) == ref_k, "port kit output differs from the art-pass kits"
    canon.dump_input(dict(cases=r2_cases.pack(cases)), os.path.join(FIX, "inputs", "s1_kits.json"))
    write(os.path.join(FIX, "expected", "s1_kits.json"), canon.dumps(kit_expected(cases, mine)))
    # ---- sign textures
    sg = r2_oracle.run_signs(art_root, work, jr(plan))
    meas = signs.TableMeasure(sg["measure"])
    specs = signs.make(plan, meas)
    assert jr(specs) == sg["specs"], "port sign draw lists differ from the art-pass textures"
    canon.dump_input(dict(plan=r2_cases.pack_signs(plan), measure=sg["measure"]), os.path.join(FIX, "inputs", "s1_signs.json"))
    write(os.path.join(FIX, "expected", "s1_signs.json"), canon.dumps(specs))
    # ---- stream vectors (the Mersenne Twister / key text contract)
    write_streams()
    with open(os.path.join(FIX, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(README.format(commit=r2_oracle.art_commit(art_root)))
    print("wrote", FIX, "| checks:", {k: v.get("ok") for k, v in plan["checks"].items()})


def write_streams() -> None:
    """The stream vectors (no art-pass needed): cases with float keys as hex strings, and the expected draws."""
    os.makedirs(os.path.join(FIX, "inputs"), exist_ok=True)
    os.makedirs(os.path.join(FIX, "expected"), exist_ok=True)
    canon.dump_input(dict(cases=r2_cases.STREAM_CASES, ops=r2_cases.STREAM_OPS, raw=r2_cases.RAW_SEEDS), os.path.join(FIX, "inputs", "streams.json"))
    write(os.path.join(FIX, "expected", "streams.json"), canon.dumps(r2_cases.stream_vectors(), 2))


def write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


README = """# street r2 fixtures (P2-P4 step 1)

Regenerate with `python -m netrun_art.tests.gen_r2_fixtures [art-pass checkout]` from `tools/` (needs the art-pass worktree and PIL).
Source: art-pass `street_r2` scripts at {commit}, art seed 1 (the plate). Nothing of the art-pass code is committed.

- `inputs/s1_layout.json`  the v3 city cut to 300 BU around the street (lot records), the 10 border links, and the plate's street
  derivation (`derive_v3`). Floats are hex strings (exact doubles). Input of `layout_pass` and `plan_pass`.
- `inputs/s1_kits.json`    the facade-kit cases (`r2_cases.kit_cases` of the plan); `seed` values are decimal strings (u64).
- `inputs/s1_signs.json`   the plan's signs and megastructure, and the glyph boxes the plate's fonts gave (`measure` rows).
- `expected/s1_layout.json` heights after `layout_pass` (lot units) and its log. `s1_plan.json` the plan (signs, props, rhythm, kits, ...).
- `expected/s1_kits.json`  per kit case: face counts and the SHA-256 of the canonical record. `s1_signs.json` the sign draw lists.

Expected files are the canonical text of `netrun_art.r2.canon` (floats to 1e-6); the GDScript twin must reproduce them byte for byte.
"""

if __name__ == "__main__":
    if sys.argv[1:] == ["--streams"]:
        write_streams()
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ART)
