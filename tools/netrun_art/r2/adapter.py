"""Adapter: our street derive (`derive.street.derive_street`: rooms, columns, frontage bids, poses) and the game city -> the r2 rule
input, so a Godot street gets a plate-style facade / sign plan.

The r2 rules read three things: the street derivation `D` (leg, side, route columns, room fronts, the two cameras), the buildings as
BU records (merged: base footprint, top height, taper), and the district per building. The game already applies its own layout rules
(`layout.apply_rules`: silhouette, horizon), so only the dressing plan runs on the result; the horizon spikes the plan needs
are picked with the r2 selection (`rules.horizon_pick`) over the heights the game city already has.

Everything is keyed by the building's `bid` (it takes the place of the plate's `ci_key` uid), so a building's streams are
`art_seed(seed, stream, bid)`: adding or removing another building never moves its facade, signs or words. `seed` is the u64 art seed
(the city's `layout_seed`, an int or its decimal string; a signed GDScript seed is its two's-complement u64)."""
from typing import Any, Dict, List

from .. import layout as LY
from . import onecity as OC
from . import rules
from .streams import M64


def seed_of(layout_seed: Any) -> int:
    """The u64 art seed of a city's layout seed."""
    return int(layout_seed) & M64


def street_derivation(d: Dict[str, Any]) -> Dict[str, Any]:
    """The r2 `D` of a street derive `d`: leg ends, side, route column uids, room fronts, OVERVIEW / DECISION cameras."""
    a, c = list(d["street"]["a"]), list(d["street"]["c"])
    nrm = list(d["nrm"])
    ax = 0 if abs(a[1] - c[1]) < 1e-6 else 1
    dirn = 1 if c[ax] > a[ax] else -1
    side = int(round(nrm[1] * dirn)) if ax == 0 else int(round(-nrm[0] * dirn))
    cols = [b for _, b in d["columns"]]
    rooms = {rid: dict(front=[list(p) for p in r["front"]], bld_uid=r["bld"], floor=r["floor"], span=r["span"]) for rid, r in d["rooms"].items()}
    return dict(a=a, c=c, nrm=nrm, side=side, column_uids=list(cols), route_uids=list(cols), rooms=rooms,
                overview=camera(d["overview"]), decision=camera(d["decision"]))


def camera(pose: Dict[str, Any]) -> Dict[str, Any]:
    """The r2 camera dict of a v2 pose (`loc`, `lens`, `shift_x`, `shift_y`, `yaw`, `pitch`). The rig yaw is 0 = +y, clockwise; the r2
    (layout36) yaw is 0 = +x, counter-clockwise, so `yaw_l36 = 90 - yaw` (`rig.yaw_to_rig` is its own inverse)."""
    return dict(yaw=90.0 - pose["yaw"], pitch=pose["pitch"], persp=dict(loc=list(pose["loc"]), lens=pose["lens"], sx=pose["shift_x"], sy=pose["shift_y"]))


def buildings(city: Dict[str, Any]) -> List[Dict[str, Any]]:
    """BU records of the street-level buildings (merged with their stacked parts), in `bid` text order, in the shape of
    `onecity.merged_buildings`; `uid` is the bid."""
    byid = {b["bid"]: b for b in city["buildings"]}
    out = []
    for bi in LY.merged_buildings(city):
        base = byid[bi["bid"]]["parts"][bi["base"]]
        out.append(dict(key=bi["key"], uid=bi["bid"], q=[list(p) for p in base["poly"]], x0=bi["x0"], x1=bi["x1"], y0=bi["y0"], y1=bi["y1"],
                        z0=bi["z0"], h=bi["h"], ts=bi["ts"], top=bi["h"], parts=[bi["key"]], parts_uid=[bi["bid"]]))
    return out


def r2_input(city: Dict[str, Any], d: Dict[str, Any], seed: Any) -> Dict[str, Any]:
    """`dict(seed, D, merged, terr, layout_log)`: the arguments of `rules.plan_pass` for the street `d` of `city`."""
    D = street_derivation(d)
    merged = buildings(city)
    terr = {b["bid"]: b.get("terr", "") for b in city["buildings"]}
    pick, _med = rules.horizon_pick(seed_of(seed), merged, D, set(D["column_uids"]))
    log = dict(spikes=[dict(key=bi["uid"], z=round(top, 1), sx=round(sx, 3), far=round(far, 1)) for top, sx, far, bi in pick])
    return dict(seed=seed_of(seed), D=D, merged=merged, terr=terr, layout_log=log)


def plan_street(city: Dict[str, Any], d: Dict[str, Any], seed: Any) -> Dict[str, Any]:
    """The r2 dressing plan of the derived street `d` on `city`, deterministic per bid and art seed."""
    x = r2_input(city, d, seed)
    return rules.plan_pass(x["seed"], x["D"], None, x["layout_log"], merged=x["merged"], terr=x["terr"])
