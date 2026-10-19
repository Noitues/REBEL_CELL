"""Street r2 adapter fixtures: the plan of the game-shaped synthetic worlds (the NA-21 fixture seeds) through `r2.adapter`.

Run from `tools/`:  `python -m netrun_art.tests.gen_r2_adapter`. The inputs are the existing `fixtures/inputs/<seed>.json` (exact doubles);
the GDScript twin derives the street (NA-23b twin, already byte-identical), adapts it and plans it, and must reproduce
`fixtures/r2/expected/adapter_<seed>.json`. The first seed is written whole; the others as a digest per plan section."""
import os
from typing import Any, Dict

from netrun_art.derive import street as STREET
from netrun_art.r2 import adapter, canon, rules
from netrun_art.tests import gen_inputs

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures", "r2", "expected")
SEEDS = (101, 105, 108)


def adapted_plan(seed: int) -> Dict[str, Any]:
    """The r2 plan of the street of synthetic world `seed`, through the adapter."""
    w, city = gen_inputs.world(seed)
    d = STREET.derive_street(city, w["net"], w["run_graph"], w["site"])
    return adapter.plan_street(city, d, w["seed"])


def main() -> None:
    os.makedirs(FIX, exist_ok=True)
    digests = {}
    for s in SEEDS:
        plan = adapted_plan(s)
        digests[str(s)] = {k: canon.digest(v) for k, v in plan.items()}
        if s == SEEDS[0]:
            with open(os.path.join(FIX, "adapter_%d.json" % s), "w", encoding="utf-8", newline="\n") as f:
                f.write(canon.dumps(plan))
    with open(os.path.join(FIX, "adapter_digests.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(canon.dumps(digests))
    print("wrote adapter fixtures for", SEEDS)


if __name__ == "__main__":
    main()
