"""NA-11 parity fixtures: `fixtures/layout/<seed>.json` (raw synthetic city + net, hex floats) and the ruled heights
`fixtures/layout/<seed>_rules.json` of `layout.apply_rules(..., border_mode="all", route_tops=...)`.

Run from `tools/`:  `python -m netrun_art.tests.gen_layout_fixtures`. The GDScript twin (`NetrunArtLayoutRules`) must
reproduce every part height and base polygon of the rules file to 1e-4 BU (tests/netrun_art/test_na11_layout_rules.gd).
Same encoding as `gen_inputs` (`"~<float.hex()>"`), so the GDScript reader rebuilds the exact doubles.
"""
import json
import os
from typing import Any, Dict

from netrun_art import layout
from netrun_art.tests import synth
from netrun_art.tests.gen_inputs import encode
from netrun_art.tests.gen_fixtures import FIX

LAYOUT_DIR = os.path.join(FIX, "layout")
SEEDS = ["101", "102", "103"]


def route_tops_of(city: Dict[str, Any]) -> Dict[str, int]:
    """A deterministic route column set for the fixture: the first 3 street-level buildings by bid, top room floor 4."""
    return {b["bid"]: 4 for b in layout.merged_buildings(city)[:3]}


def ruled(seed: str) -> Dict[str, Any]:
    """`(raw world, ruled city)` of fixture seed `seed`."""
    w = synth.make_world(int(seed))
    return w, layout.apply_rules(w["city"], w["net"], route_tops=route_tops_of(w["city"]), border_mode="all")


def heights_of(city: Dict[str, Any]) -> Dict[str, Any]:
    """bid -> list of `{z0, h, poly}` per part: what the twin must reproduce."""
    return {b["bid"]: [{"z0": p["z0"], "h": p["h"], "poly": p["poly"]} for p in b["parts"]] for b in city["buildings"]}


def main() -> None:
    os.makedirs(LAYOUT_DIR, exist_ok=True)
    for s in SEEDS:
        w, out = ruled(s)
        with open(os.path.join(LAYOUT_DIR, s + ".json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(encode({"city": w["city"], "net": w["net"], "route_tops": route_tops_of(w["city"])}), f, separators=(",", ":"),
                      sort_keys=True)
        with open(os.path.join(LAYOUT_DIR, s + "_rules.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(encode(heights_of(out)), f, separators=(",", ":"), sort_keys=True)
    print("wrote", len(SEEDS), "layout fixtures")


if __name__ == "__main__":
    main()
