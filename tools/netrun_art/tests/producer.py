"""The NA-03 pure pipeline on a synthetic world, as a function of the layout seed (used by tests, hashes and NA-04 checks).

`produce(layout_seed)` -> `{file name: object}` for the street run and the HQ run of that seed. `python -m
netrun_art.tests.producer <seed>` prints the data hash (for the fresh-process determinism test).
"""
import sys
from typing import Any, Dict

from netrun_art import dress, layout, poses, zoning
from netrun_art.checks import data_checks as DC
from netrun_art.derive import game_partial
from netrun_art.derive import street as STREET
from netrun_art.hq import slots as SLOTS
from netrun_art.tests import synth


def produce_world(w: Dict[str, Any]) -> Dict[str, Any]:
    """All outputs of one synthetic world."""
    city = layout.apply_layout_rules(w["city"], w["net"])
    zoned = zoning.zone(city)
    city = zoning.apply_zoning(city, zoned)
    run = w["run_graph"]["run"]
    d_s = STREET.derive_street(city, w["net"], w["run_graph"], w["site"], game_partial(w["seed"], run, "street"))
    d_h = SLOTS.derive_hq(city, w["run_graph"], w["corp"], game_partial(w["seed"], run, "hq", [w["corp"]]))
    return {"city": city, "zoned": zoned, "derive_street": d_s, "derive_hq": d_h,
            "poses_street": poses.build_poses(d_s, city, w["run_graph"], w["net"]),
            "poses_hq": poses.build_poses(d_h, city, w["run_graph"]),
            "dress_street": dress.dress_street(d_s, city)}


def produce(layout_seed: str) -> Dict[str, Any]:
    """Producer for `checks.data_checks.load_producer`."""
    return produce_world(synth.make_world(int(layout_seed)))


if __name__ == "__main__":
    print(DC.data_hash(produce(sys.argv[1])))
