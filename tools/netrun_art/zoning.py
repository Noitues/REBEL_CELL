"""zoning: districts, HQ lots, landmark clearances, the coast, arterials and the freight-rail line (spec 3.4, 3.7).

Ports the rules of `CAC/zoning.py` 306a6865 that survive in the A2 pipeline (spec 3.4: Z1-Z3 and L1 are legacy only; the
districts and the HQ lots are READ from `city.json`: `buildings[].terr`, `hqs{}`), with the numbers of
`CAC/city_preset.py` 16c427cd converted to BU. Rules kept: Z4 the coast, L2 landmark clearances, T1 arterials, L4 the
rail polyline (a centripetal Catmull-Rom from the Meridian north gate to the port; an optional `city["rails"]` polyline
from the planner JSON wins) with its corridor clearing and rail-side height cap (`zoned.json` `rail` object, O-C / O-H).
`zoned.json` v1 is in BU plan coordinates, heights above local ground. It uses no RNG. Standard library only.
"""
import copy
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

from . import layout as LY

R2 = math.sqrt(2.0)
ZONING: Dict[str, Any] = dict(          # CAC/city_preset.py ZONING / RAIL / CURVES, lots converted to BU by `zone`
    landmark_r_lots=5.6, arterial_tr=0.55, arterial_len=36, run_gap=3, coast_margin_lots=0.8, step_bu=3.0,
    gate_u=5.0, wall_s=28.0, gate_out=6.0, port_depth_lots=13.0, port_entry_share=0.7, s_bend=5.0,
    rail_w=4.8, clear_margin_bu=2.1, deck_z=17.5, side_cap=15.5, side_d_lots=1.2, pier_step=7.0, ramp=60.0, end_ramp=45.0,
    signal_step=36.0)


def ab(x: float, y: float) -> Tuple[float, float]:
    """Plan BU -> screen-aligned `(a right, b away from the map camera)` in BU (the 45 degree frame of `zoning.ab`)."""
    return (x + y) / R2, (y - x) / R2


def from_ab(a: float, b: float) -> List[float]:
    """Inverse of `ab`."""
    return [(a - b) / R2, (a + b) / R2]


def catmull_rom(pts: Sequence[Sequence[float]], step: float, alpha: float = 0.5) -> List[List[float]]:
    """Centripetal Catmull-Rom through `pts`, sampled about every `step` BU (first and last points kept)."""
    P = [list(p) for p in pts]
    ext = [[2 * P[0][0] - P[1][0], 2 * P[0][1] - P[1][1]]] + P + [[2 * P[-1][0] - P[-2][0], 2 * P[-1][1] - P[-2][1]]]
    out: List[List[float]] = [P[0]]
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        t = [0.0]
        for a, b in ((p0, p1), (p1, p2), (p2, p3)):
            t.append(t[-1] + max(math.hypot(b[0] - a[0], b[1] - a[1]), 1e-9) ** alpha)
        n = max(1, int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / step + 0.5))
        for k in range(1, n + 1):
            u = t[1] + (t[2] - t[1]) * k / n
            pt = []
            for d in range(2):
                a1 = [(t[1] - u) / (t[1] - t[0]) * p0[d] + (u - t[0]) / (t[1] - t[0]) * p1[d],
                      (t[2] - u) / (t[2] - t[1]) * p1[d] + (u - t[1]) / (t[2] - t[1]) * p2[d],
                      (t[3] - u) / (t[3] - t[2]) * p2[d] + (u - t[2]) / (t[3] - t[2]) * p3[d]]
                b1 = [(t[2] - u) / (t[2] - t[0]) * a1[0] + (u - t[0]) / (t[2] - t[0]) * a1[1],
                      (t[3] - u) / (t[3] - t[1]) * a1[1] + (u - t[1]) / (t[3] - t[1]) * a1[2]]
                pt.append((t[2] - u) / (t[2] - t[1]) * b1[0] + (u - t[1]) / (t[2] - t[1]) * b1[1])
            out.append(pt)
    return out


def _centre(b: Dict[str, Any]) -> Tuple[float, float]:
    xs = [p[0] for pt in b["parts"] for p in pt["poly"]]
    ys = [p[1] for pt in b["parts"] for p in pt["poly"]]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


def hq_centres(city: Dict[str, Any]) -> Dict[str, List[float]]:
    """Plan BU centre of each HQ lot (`city.hqs`, `[i, j, w, h]` in lots)."""
    ol, lb = city["origin_lot"], city["lot_bu"]
    return {k: LY.lot_to_plan([v[0] + v[2] / 2, v[1] + v[3] / 2], ol, lb) for k, v in sorted(city["hqs"].items())}


def arterials(city: Dict[str, Any], z: Dict[str, Any]) -> List[Dict[str, Any]]:
    """T1: street-tile runs of at least `arterial_len` tiles with mean traffic >= `arterial_tr`, both axes."""
    ol, lb = city["origin_lot"], city["lot_bu"]
    rows: Dict[int, List[Dict[str, Any]]] = {}
    cols: Dict[int, List[Dict[str, Any]]] = {}
    for s in city["streets"]:
        if s["along_i"] and not s["along_j"]:
            rows.setdefault(s["lot"][1], []).append(s)
        elif s["along_j"] and not s["along_i"]:
            cols.setdefault(s["lot"][0], []).append(s)
    out = []
    for axis, lines, k in (("x", rows, 0), ("y", cols, 1)):
        for line in sorted(lines):
            ts = sorted(lines[line], key=lambda s: s["lot"][k])
            run = [ts[0]]
            for t in ts[1:] + [None]:
                if t is not None and 1 <= t["lot"][k] - run[-1]["lot"][k] <= z["run_gap"]:
                    run.append(t)
                    continue
                tr = sum(r["traffic"] for r in run) / len(run)
                if len(run) >= z["arterial_len"] and tr >= z["arterial_tr"]:
                    a0, a1 = run[0]["lot"], run[-1]["lot"]
                    out.append(dict(axis=axis, line=line, a=LY.lot_to_plan([a0[0] + 0.5, a0[1] + 0.5], ol, lb),
                                    b=LY.lot_to_plan([a1[0] + 0.5, a1[1] + 0.5], ol, lb), tr=tr, n=len(run)))
                if t is not None:
                    run = [t]
    return out


def rail_line(city: Dict[str, Any], hq: Dict[str, List[float]], coast_b: float, z: Dict[str, Any]) -> List[List[float]]:
    """The freight-rail polyline in BU: the planner `city["rails"][0]["pts"]` when present, else a smooth S from the
    Meridian north gate to the port entry on the coast (`CAC/zoning.py` L4)."""
    lb = city["lot_bu"]
    if city.get("rails"):
        return [list(p) for p in city["rails"][0]["pts"]]
    mx, my = hq.get("meridian") or next(iter(hq.values()))
    gate = [mx + z["gate_u"], my + z["wall_s"] + z["gate_out"]]
    ga, gb = ab(*gate)
    amin = min(ab(*_centre(b))[0] for b in city["buildings"])
    amax = max(ab(*_centre(b))[0] for b in city["buildings"])
    ea = amin + (amax - amin) * z["port_entry_share"]
    eb = coast_b - z["port_depth_lots"] * lb * 0.25
    da, db = ea - ga, eb - gb
    dl = math.hypot(da, db) or 1.0
    mid = from_ab(ga + da * 0.5 - db / dl * z["s_bend"], gb + db * 0.5 + da / dl * z["s_bend"])
    lead = [gate[0] - z["gate_u"] * 3, gate[1]]
    return catmull_rom([lead, gate, mid, from_ab(ea, eb)], z["step_bu"])


def zone(city: Dict[str, Any], key_locations: Optional[Dict[str, Any]] = None, preset: Optional[Dict[str, Any]] = None,
         layout_seed: Optional[str] = None) -> Dict[str, Any]:
    """`zoned.json` v1 from city.json (districts and HQ lots are read, not computed).

    Keys: `version`, `layout_seed`, `districts{bid: terr}`, `hq{corp: {lot, centre}}`, `clearances{corp: {centre, r,
    bids}}`, `coast{b, direction}`, `arterials[]`, `rail{pts, w, half_clear, deck_z, side_cap, side_d, pier_step, ramp,
    end_ramp, signal_step, piers}`, `rail_cleared[bid]` (footprints in the corridor), `rail_capped[bid]` (tops above
    `side_cap` within `side_d`). Key-location buildings are never listed in `rail_cleared` or `clearances`.
    """
    z = dict(ZONING, **(preset or {}))
    lb = city["lot_bu"]
    keep = {l["bid"] for l in (key_locations or {}).get("locations", [])}
    hq = hq_centres(city)
    cen = {b["bid"]: _centre(b) for b in city["buildings"]}
    coast_b = max(ab(*c)[1] for c in cen.values()) + z["coast_margin_lots"] * lb
    clearances = {}
    for corp, c in hq.items():
        r = z["landmark_r_lots"] * lb
        bids = sorted(b["bid"] for b in city["buildings"]
                      if not b["hq"] and b["bid"] not in keep and math.hypot(cen[b["bid"]][0] - c[0], cen[b["bid"]][1] - c[1]) < r)
        clearances[corp] = dict(centre=c, r=r, bids=bids)
    pts = rail_line(city, hq, coast_b, z)
    half = z["rail_w"] / 2 + z["clear_margin_bu"]
    rail = dict(pts=pts, w=z["rail_w"], half_clear=half, deck_z=z["deck_z"], side_cap=z["side_cap"],
                side_d=z["side_d_lots"] * lb, pier_step=z["pier_step"], ramp=z["ramp"], end_ramp=z["end_ramp"],
                signal_step=z["signal_step"])
    tiles = LY.street_cells(city)
    piers, run, nxt = [], 0.0, 0.0
    for a, b in zip(pts, pts[1:]):
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        while nxt <= run + seg and seg > 0:
            t = (nxt - run) / seg
            p = [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]
            lot = LY.plan_to_lot(p, city["origin_lot"], lb)
            if (math.floor(lot[0]), math.floor(lot[1])) in tiles:
                piers.append(p)
            nxt += z["pier_step"]
        run += seg
    rail["piers"] = piers
    cleared, capped = [], []
    from .checks.data_checks import poly_rail_dist
    for b in sorted(city["buildings"], key=lambda q: q["bid"]):
        if b["hq"] or b["bid"] in keep:
            continue
        if any(poly_rail_dist(pt["poly"], pts, half) < half for pt in b["parts"]):
            cleared.append(b["bid"])
        elif any(pt["z0"] + pt["h"] > rail["side_cap"] and poly_rail_dist(pt["poly"], pts, rail["side_d"]) <= rail["side_d"]
                 for pt in b["parts"]):
            capped.append(b["bid"])
    return dict(version=1, layout_seed=layout_seed or city["layout_seed"], districts={b["bid"]: b["terr"] for b in city["buildings"]},
                hq={k: dict(lot=city["hqs"][k], centre=c) for k, c in hq.items()}, clearances=clearances,
                coast=dict(b=coast_b, direction="+b"), arterials=arterials(city, z), rail=rail, rail_cleared=cleared,
                rail_capped=capped)


def apply_zoning(city: Dict[str, Any], zoned: Dict[str, Any]) -> Dict[str, Any]:
    """city.json with the rail corridor cleared and the rail-side tops capped (a new dict)."""
    out = copy.deepcopy(city)
    gone = set(zoned["rail_cleared"])
    cap = zoned["rail"]["side_cap"]
    capped = set(zoned["rail_capped"])
    out["buildings"] = [b for b in out["buildings"] if b["bid"] not in gone]
    for b in out["buildings"]:
        if b["bid"] in capped:
            for pt in b["parts"]:
                if pt["z0"] >= cap:
                    pt["h"] = 0.0
                pt["h"] = max(0.0, min(pt["h"], cap - pt["z0"]))
            b["parts"] = [pt for pt in b["parts"] if pt["h"] > 0.0] or b["parts"][:1]
    return out
