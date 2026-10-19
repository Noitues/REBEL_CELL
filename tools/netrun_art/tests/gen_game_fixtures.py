"""NA-23b: parity fixtures from the game's own city (not the synthetic grid).

`tools/netrun_art/dump_game_worlds.gd` writes the derive inputs of a started netrun on the game's city (`city`, `net`,
`run_graph`, `site`, `corp`, `seed`). This script trims such a world to the buildings and street lots around the Site's link
(the street derive reads nothing else), writes it as `fixtures/inputs/<name>.json` (floats as hex strings, like the 12
seeds) and the Python derive as `fixtures/expected/<name>_street_derive.json`. The GDScript twin must reproduce it byte for
byte (`tests/netrun_art/test_na23b_street.gd`).

Run from `tools/`:  `python -m netrun_art.tests.gen_game_fixtures <dump dir> g1=meridian_c7_1_m1_a g2=solace_c7_1_t1_i`
"""
import json
import os
import sys
from typing import Any, Dict

from netrun_art import io
from netrun_art import layout as LY
from netrun_art.derive import street as S
from netrun_art.tests.gen_fixtures import EXPECTED, FIX
from netrun_art.tests.gen_inputs import INPUTS, encode

WINDOW = 80.0          # BU around the link's bounding box kept (the legs extend 12 / 60 BU, the front band is 6.5)


def ints(v: Any) -> Any:
    """Whole floats back to ints (the dump went through Godot's JSON, which reads every number as a float; the contract
    files carry `layer`, `index` and the like as ints)."""
    if isinstance(v, float) and v.is_integer():
        return int(v)
    if isinstance(v, list):
        return [ints(e) for e in v]
    if isinstance(v, dict):
        return {k: ints(e) for k, e in v.items()}
    return v


def trim(w: Dict[str, Any]) -> Dict[str, Any]:
    """The world with `city.buildings` and `city.streets` cut to the window around the Site's link."""
    city = w["city"]
    _, pts = S.select_link(w["net"], w["site"])
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    lo_x, hi_x, lo_y, hi_y = min(xs) - WINDOW, max(xs) + WINDOW, min(ys) - WINDOW, max(ys) + WINDOW
    lot, org = city["lot_bu"], city["origin_lot"]
    out = dict(w, city=dict(city))
    keep = []
    for b in city["buildings"]:
        if b["hq"]:
            continue
        bi = LY.building_info(b)
        if bi and bi["x1"] > lo_x and bi["x0"] < hi_x and bi["y1"] > lo_y and bi["y0"] < hi_y:
            keep.append(b)
    out["city"]["buildings"] = keep
    out["city"]["streets"] = [s for s in city["streets"]
                              if lo_x < (s["lot"][0] + 0.5 - org[0]) * lot < hi_x and lo_y < -(s["lot"][1] + 0.5 - org[1]) * lot < hi_y]
    out["city"]["hqs"] = {}
    return out


def main(argv) -> None:
    src = argv[1]
    os.makedirs(INPUTS, exist_ok=True)
    for spec in argv[2:]:
        name, stem = spec.split("=")
        w = trim(json.load(open(os.path.join(src, stem + ".json"), encoding="utf-8")))
        w["run_graph"] = ints(w["run_graph"])
        d = S.derive_street(w["city"], w["net"], w["run_graph"], w["site"])
        data = dict(seed=w["seed"], site=w["site"], corp=w["corp"], city=w["city"], net=w["net"], run_graph=ints(w["run_graph"]))
        with open(os.path.join(INPUTS, name + ".json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(encode(data), f, separators=(",", ":"), sort_keys=True)
            f.write("\n")
        io.dump(d, os.path.join(EXPECTED, f"{name}_street_derive.json"))
        print(name, stem, "span", d["span"], "buildings", len(w["city"]["buildings"]))


if __name__ == "__main__":
    main(sys.argv)
