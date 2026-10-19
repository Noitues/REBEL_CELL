"""NA-21 parity inputs: the exact (unrounded) inputs of the 12 fixture seeds, plus the derive and dress reference outputs.

Run from `tools/`:  `python -m netrun_art.tests.gen_inputs`. The GDScript twins (`scripts/netrun_art/`) run on these inputs and
must reproduce `fixtures/expected/<seed>_{street,hq}_{derive,poses}.json` byte for byte (PIPELINE_SPEC 12.6, 12.8).

Input encoding (`fixtures/inputs/<seed>.json`, compact JSON): every float is the string `"~<float.hex()>"` with trailing hex
zeros trimmed, so the GDScript reader rebuilds the identical double (a decimal parser may be off by one ulp; the canonical 1e-4
files cannot be the input because the Python derive runs on unrounded values). Ints stay ints.
"""
import json
import os
from typing import Any

from netrun_art import dress, io, layout, poses, zoning
from netrun_art.derive import game_partial
from netrun_art.derive import street as STREET
from netrun_art.hq import slots as SLOTS
from netrun_art.tests import synth
from netrun_art.tests.gen_fixtures import EXPECTED, FIX, SEEDS

INPUTS = os.path.join(FIX, "inputs")


def hexf(x: float) -> str:
    """`"~0x1.8p+3"`: the hex form of a float with the zero tail of the mantissa trimmed."""
    h = float(x).hex()
    if "p" not in h:
        return "~" + h
    m, e = h.split("p")
    if "." in m:
        m = m.rstrip("0").rstrip(".")
    return "~" + m + "p" + e


def encode(v: Any) -> Any:
    """Floats to hex strings, recursively (tuples to lists)."""
    if isinstance(v, bool) or v is None or isinstance(v, (int, str)):
        return v
    if isinstance(v, float):
        return hexf(v)
    if isinstance(v, (list, tuple)):
        return [encode(e) for e in v]
    if isinstance(v, dict):
        return {k: encode(e) for k, e in v.items()}
    raise TypeError(type(v).__name__)


def world(seed: int):
    """`(w, zoned city)`: the synthetic world and its city after layout and zoning."""
    w = synth.make_world(seed)
    city = layout.apply_layout_rules(w["city"], w["net"])
    zoned = zoning.zone(city, placeholder_rail=True)
    return w, zoning.apply_zoning(city, zoned)


def main() -> None:
    os.makedirs(INPUTS, exist_ok=True)
    for s in SEEDS:
        w, city = world(int(s))
        run = w["run_graph"]["run"]
        ps = game_partial(w["seed"], run, "street")
        ph = game_partial(w["seed"], run, "hq", [w["corp"]])
        d_s = STREET.derive_street(city, w["net"], w["run_graph"], w["site"], ps)
        d_h = SLOTS.derive_hq(city, w["run_graph"], w["corp"], ph)
        data = dict(seed=w["seed"], site=w["site"], corp=w["corp"], city=city, net=w["net"], run_graph=w["run_graph"],
                    partial_street=ps, partial_hq=ph)
        with open(os.path.join(INPUTS, s + ".json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(encode(data), f, separators=(",", ":"), sort_keys=True)
            f.write("\n")
        io.dump(d_s, os.path.join(EXPECTED, f"{s}_street_derive.json"))
        io.dump(d_h, os.path.join(EXPECTED, f"{s}_hq_derive.json"))
        io.dump(dress.dress_street(d_s, city), os.path.join(EXPECTED, f"{s}_street_dress.json"))
        # the poses are built from the derive objects themselves; they must equal gen_fixtures' files
        p = poses.build_poses(d_s, city, w["run_graph"], w["net"])
        assert io.canonical_dumps(p) == open(os.path.join(EXPECTED, f"{s}_street_poses.json"), encoding="utf-8", newline="").read()
    print("wrote inputs for", len(SEEDS), "seeds")


if __name__ == "__main__":
    main()
