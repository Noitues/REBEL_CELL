"""dress: the placement lists of the street dressing (spec 9, 4.1, 13.1; DERIVE_V2_REVIEW Q4.0-Q4.4 with AD resolutions).

Ports the PLACEMENT computations of `M44/onecity_build.py` c83e3b00 (lines 98-126) and `M44/onecity_cycles.py` c83e3b00
(lines 169-371, 612-648). The Blender side (`_light`, meshes, materials) is NA-05. Randomness is `splitmix64(art_seed(...))`
per object (spec 3.5 rule 3); the concept's `random.Random(<literal>)` calls are gone. Colours are palette ids, power is
relative 0..1, `u` is the signed distance in BU along `street.c - street.a` from `street.a`. Positions are plan BU with
height above local ground. The result is the typed lists of `dress_<run>.json` v1. Standard library only.
"""
import math
from typing import Any, Dict, List, Optional, Sequence

from . import seeds
from .layout import leg_axis

VERSION = 1
PALETTE_IDS = ("district_a", "district_b", "accent_warm", "accent_cool", "lamp_warm", "lamp_cool",
               "lane_head_a", "lane_head_b", "lane_tail_a", "lane_tail_b")
SIGN_PAL = ("district_a", "district_b")
BEAM_PAL = ("district_a", "district_b", "accent_warm", "district_b", "district_a", "accent_cool")
GLOW_PAL = ("accent_warm", "district_a", "district_b", "accent_warm", "accent_cool")
LAMP_PAL = ("lamp_cool", "lamp_warm")          # index 0 when k % 3 == 0
LANES = ((0.28, 1, "lane_head_a"), (0.62, 1, "lane_head_b"), (-0.3, -1, "lane_tail_a"), (-0.64, -1, "lane_tail_b"))

PRESET: Dict[str, Any] = dict(
    street_width=8.0,            # border street width (3.2 rule)
    lamp_step=6.0, lamp_inset=0.3, lamp_z=1.6, lamp_skip_margin=0.15,  # a lamp within this lateral margin of a route opening is shifted along the street (AD 2026-10-18 Q1)
    lamp_shift_steps=(0.8, 1.6, 2.4),  # shift candidates +/-, nearest first, + before -; last = art-pass lamp_shift_max (r2_config.py ed8675a8); none clear -> dropped
              # kerb offset = street_width / 2 - lamp_inset (audit row 37)
    wash_back=3.5, wash_z=0.4, wash_rise=0.55,
    ground_glow_step=9.0, ground_glow_depth=60.0, ground_glow_p=0.55, ground_glow_z=0.9, glow_pad=30.0,
    glow_jitter_u=0.8, glow_jitter_d=0.6, plinth_extra=0.2, glow_drift=0.12, glow_depth_step=0.8, glow_depth_from=2.0,
    sign_z0=2.2, sign_min_top=4.5, sign_top_gap=1.6, sign_panel=1.4, sign_min_panels=3, sign_w=0.8, sign_in=0.25,
    band_inset=0.4, band_drop=0.75, band_h=0.32,
    beams=6, beam_rise=1.35, beam_min_d=25.0, beam_max_d=170.0, beam_behind=12.0, beam_spacing=45.0, beam_up=0.5,
    beam_lx=(0.12, 0.30), beam_ly=(0.18, 0.12), beam_sweep=(4.5, 1.5), beam_sweep_on=False,
    front_far=18.0, front_pad=10.0, sky_lo=18.0, sky_hi=160.0, sky_r=180.0, sky_q=0.9, h_front_default=14.0,
    lane_period=80.0, lane_pad=120.0, lane_z=0.12, lane_len=(3.0, 16.0), lane_bright=(0.5, 1.3), lane_gap=(4.0, 22.0),
    t_loop=4.0, fog_pad=10.0, fog_top_min=80.0, fog_sky_k=2.5)   # fog top = max(240 / unit_scale 3.0, 2.5 * H_SKY)

Pt = Sequence[float]


def _stream(layout_seed: str, name: str, *keys: Any):
    return seeds.splitmix64(seeds.art_seed(layout_seed, name, *keys))


def _frame(derive: Dict[str, Any]) -> Dict[str, Any]:
    a, c = derive["street"]["a"], derive["street"]["c"]
    ax = leg_axis(a, c)
    nrm = derive["nrm"]
    sgn = 1.0 if c[ax] > a[ax] else -1.0
    return dict(a=a, c=c, ax=ax, sgn=sgn, nrm=nrm, length=abs(c[ax] - a[ax]), cline=a[1 - ax],
                ncross=nrm[1] if ax == 0 else nrm[0])


def _world(f: Dict[str, Any], u: float, cross: float, z: float) -> List[float]:
    """World xyz of street coordinate `u` and cross-axis coordinate `cross`."""
    along = f["a"][f["ax"]] + f["sgn"] * u
    return [along, cross, z] if f["ax"] == 0 else [cross, along, z]


def signs(derive: Dict[str, Any], p: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Hero blade signs, one per route column, sorted by bid. The `(hero_sign, bid)` stream is reserved (no draws)."""
    f = _frame(derive)
    out = []
    for k, ci in enumerate(sorted(derive["col_info"], key=lambda c: (c["layer"], c["bid"]))):
        z0 = p["sign_z0"]
        h = max(p["sign_min_top"], ci["top"] - p["sign_top_gap"]) - z0
        u = ci["u0"] + p["sign_in"]
        cross = ci["face"] - p["sign_in"] * f["ncross"]
        out.append(dict(bid=ci["bid"], layer=ci["layer"], pos=_world(f, u, cross, z0), nrm=list(f["nrm"]), w=p["sign_w"], h=h,
                        panels=max(p["sign_min_panels"], int(h / p["sign_panel"])), pal=SIGN_PAL[k % 2],
                        band_pal=SIGN_PAL[(k + 1) % 2]))
    return sorted(out, key=lambda s: s["bid"])


def lamps(derive: Dict[str, Any], p: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Kerb lamps every `lamp_step` BU, both kerbs (no stream); colour cool when the running index `k % 3 == 0`.
    A lamp whose `u` is inside a route opening's `[u0 - m, u1 + m]` on its side is shifted along the street to the nearest clear `u`
    (candidates +/-`lamp_shift_steps`, + first; art-pass r2_rules.py ed8675a8 streets.light), dropped only if none is clear; the others do not move."""
    f = _frame(derive)
    off = p["street_width"] / 2.0 - p["lamp_inset"]
    spans = {-1: [], 1: []}
    for r in derive["rooms"].values():
        us = sorted((q[f["ax"]] - f["a"][f["ax"]]) * f["sgn"] for q in r["front"])
        bside = 1 if r["front"][0][1 - f["ax"]] > f["cline"] else -1
        spans[bside].append((us[0] - p["lamp_skip_margin"], us[-1] + p["lamp_skip_margin"]))
    out, k, u = [], 0, 0.0
    while u < f["length"]:
        for side in (-1, 1):
            uu = None
            for d_ in (0.0,) + tuple(x * sg for x in p["lamp_shift_steps"] for sg in (1, -1)):
                if not any(lo <= u + d_ <= hi for lo, hi in spans[side]):   # else in front of a route opening (12.4.5c)
                    uu = u + d_
                    break
            if uu is not None:
                out.append(dict(u=uu, side=side, pos=_world(f, uu, f["cline"] + side * off, p["lamp_z"]),
                                pal=LAMP_PAL[0] if k % 3 == 0 else LAMP_PAL[1]))
            k += 1
        u += p["lamp_step"]
    return out


def washes(derive: Dict[str, Any], p: Dict[str, Any]) -> List[Dict[str, Any]]:
    """One wash spot per route column, pal by the index over the bid order (odd -> district_a)."""
    f = _frame(derive)
    cols: Dict[str, List[Dict[str, Any]]] = {}
    for r in derive["rooms"].values():
        cols.setdefault(r["bld"], []).append(r)
    out = []
    nrm = f["nrm"]
    for k, bid in enumerate(sorted(cols)):
        us = [(q[f["ax"]] - f["a"][f["ax"]]) * f["sgn"] for r in cols[bid] for q in r["front"]]
        face = cols[bid][0]["front"][0][1 - f["ax"]]
        umid = (min(us) + max(us)) / 2
        cross = face - p["wash_back"] * f["ncross"]
        n = math.sqrt(nrm[0] ** 2 + nrm[1] ** 2 + p["wash_rise"] ** 2)
        out.append(dict(u=umid, pos=_world(f, umid, cross, p["wash_z"]), dir=[nrm[0] / n, nrm[1] / n, p["wash_rise"] / n],
                        power=1.0, pal="district_a" if k % 2 else "district_b"))
    return sorted(out, key=lambda w: (w["u"], w["pos"]))


def glows(derive: Dict[str, Any], p: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Ground glows on a jittered grid; one stream per cell `(ground_glow, i, j)`.

    Draw order: keep (kept when uniform <= p), jitter_u, jitter_d, power, colour, then the drift r, g, b. The grid
    starts at u = -glow_pad with step `ground_glow_step`; depth starts at `plinth_off + 2` with step 0.8 x the grid step.
    """
    f = _frame(derive)
    step = p["ground_glow_step"]
    plinth = p["street_width"] / 2.0 + p["plinth_extra"]
    out = []
    i = 0
    while -p["glow_pad"] + step * i < f["length"] + p["glow_pad"]:
        u = -p["glow_pad"] + step * i
        j = 0
        while plinth + p["glow_depth_from"] + step * p["glow_depth_step"] * j < p["ground_glow_depth"]:
            d = plinth + p["glow_depth_from"] + step * p["glow_depth_step"] * j
            g = _stream(derive["layout_seed"], "ground_glow", i, j)
            if seeds.uniform(next(g)) <= p["ground_glow_p"]:
                ju = (seeds.uniform(next(g)) - 0.5) * p["glow_jitter_u"] * step
                jd = (seeds.uniform(next(g)) - 0.5) * p["glow_jitter_d"] * step
                power = 0.5 + 0.5 * seeds.uniform(next(g))
                pal = GLOW_PAL[int(seeds.uniform(next(g)) * len(GLOW_PAL))]
                drift = [(seeds.uniform(next(g)) - 0.5) * 2.0 * p["glow_drift"] for _ in range(3)]
                out.append(dict(cell=[i, j], pos=_world(f, u + ju, f["cline"] - f["ncross"] * (d + jd), p["ground_glow_z"]),
                                power=power, pal=pal, drift=drift))
            j += 1
        i += 1
    return out


def building_tops(city: Dict[str, Any]) -> List[Dict[str, Any]]:
    """`[{bid, c: (x, y), top}]` of every building (whole-building box centre, top of the highest part), sorted by bid."""
    out = []
    for b in sorted(city["buildings"], key=lambda q: q["bid"]):
        xs = [p[0] for pt in b["parts"] for p in pt["poly"]]
        ys = [p[1] for pt in b["parts"] for p in pt["poly"]]
        out.append(dict(bid=b["bid"], c=((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2),
                        top=max(pt["z0"] + pt["h"] for pt in b["parts"])))
    return out


def heights(derive: Dict[str, Any], built: Sequence[Dict[str, Any]], p: Dict[str, Any]) -> Dict[str, float]:
    """`H_FRONT` (median roof of the frontage across the street) and `H_SKY` (90th percentile roof behind it)."""
    f = _frame(derive)
    a = f["a"]
    mid = _world(f, f["length"] / 2, f["cline"], 0.0)[:2]

    def far(c: Pt) -> float:
        return (c[1] - a[1]) * f["nrm"][1] if f["ax"] == 0 else (c[0] - a[0]) * f["nrm"][0]
    lo, hi = sorted((a[f["ax"]], f["c"][f["ax"]]))
    fr = sorted(b["top"] for b in built if 0 < far(b["c"]) < p["front_far"]
                and lo - p["front_pad"] < b["c"][f["ax"]] < hi + p["front_pad"])
    sk = sorted(b["top"] for b in built if p["sky_lo"] < far(b["c"]) < p["sky_hi"]
                and math.hypot(b["c"][0] - mid[0], b["c"][1] - mid[1]) < p["sky_r"])
    h_front = fr[len(fr) // 2] if fr else p["h_front_default"]
    h_sky = sk[int(len(sk) * p["sky_q"])] if sk else 2.2 * h_front
    return dict(h_front=h_front, h_sky=h_sky)


def beams(derive: Dict[str, Any], built: Sequence[Dict[str, Any]], h_front: float, p: Dict[str, Any]) -> List[Dict[str, Any]]:
    """The K tallest non-route roofs that clear the frontage by `beam_rise` x H_FRONT; stream `(beams, bid)`.

    Draws: lean x, lean y, sweep, phase. `lean` is `[x_deg, y_deg]` (atan of the concept's lean components); `sweep_deg`
    is 0.0 (static, as the concept) unless the preset turns the sweep on.
    """
    f = _frame(derive)
    mid = _world(f, f["length"] / 2, f["cline"], 0.0)[:2]
    a = f["a"]
    route = set(derive["route_keys"])

    def far(c: Pt) -> float:
        return (c[1] - mid[1]) * f["nrm"][1] if f["ax"] == 0 else (c[0] - a[0]) * f["nrm"][0]
    cands = []
    for b in built:
        if b["bid"] in route or b["top"] < p["beam_rise"] * h_front:
            continue
        d = math.hypot(b["c"][0] - mid[0], b["c"][1] - mid[1])
        if p["beam_min_d"] < d < p["beam_max_d"] and far(b["c"]) > p["beam_behind"]:
            cands.append(b)
    cands.sort(key=lambda b: (-b["top"], b["bid"]))
    pick: List[Dict[str, Any]] = []
    for b in cands:
        if all(math.hypot(b["c"][0] - q["c"][0], b["c"][1] - q["c"][1]) > p["beam_spacing"] for q in pick):
            pick.append(b)
        if len(pick) >= p["beams"]:
            break
    out = []
    for k, b in enumerate(pick):
        g = _stream(derive["layout_seed"], "beams", b["bid"])
        lx = p["beam_lx"][0] + p["beam_lx"][1] * seeds.uniform(next(g))
        ly = p["beam_ly"][0] + p["beam_ly"][1] * seeds.uniform(next(g))
        sweep = p["beam_sweep"][0] + p["beam_sweep"][1] * seeds.uniform(next(g))
        phase = seeds.uniform(next(g))
        lx = lx if b["c"][0] > mid[0] else -lx
        ly = ly if f["ax"] == 0 else 0.0
        out.append(dict(bid=b["bid"], pos=[b["c"][0], b["c"][1], b["top"] + p["beam_up"]],
                        lean=[math.degrees(math.atan(lx)), math.degrees(math.atan(ly))],
                        sweep_deg=sweep if p["beam_sweep_on"] else 0.0, phase=phase, pal=BEAM_PAL[k % len(BEAM_PAL)]))
    return sorted(out, key=lambda q: q["bid"])


def streak_lanes(derive: Dict[str, Any], p: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Four traffic lanes; stream `(street_lanes, lane_id)`; per streak draws: length, brightness, gap.

    The lane length is `L = k * speed * T` (T the 4 s loop), so every streak wraps per streak modulo `L` and the loop is
    seamless. `speed` is `lane_period / T`; the lane runs from `a` to `b` (reversed for the opposite direction).
    """
    f = _frame(derive)
    half = p["street_width"] / 2.0
    cycle = p["lane_period"]
    k = max(1, int(math.ceil((f["length"] + 2 * p["lane_pad"]) / cycle)))
    L = k * cycle
    u_lo = -(L - f["length"]) / 2.0
    out = []
    for lane_id, (fr, dirn, pal) in enumerate(LANES):
        g = _stream(derive["layout_seed"], "street_lanes", lane_id)
        cross = f["cline"] + fr * half
        streaks, x = [], 0.0
        while x < L:
            ln = p["lane_len"][0] + (p["lane_len"][1] - p["lane_len"][0]) * seeds.uniform(next(g))
            br = p["lane_bright"][0] + (p["lane_bright"][1] - p["lane_bright"][0]) * seeds.uniform(next(g))
            gap = p["lane_gap"][0] + (p["lane_gap"][1] - p["lane_gap"][0]) * seeds.uniform(next(g))
            streaks.append(dict(u0=x, len=ln, gap=gap, bright=br))
            x += ln + gap
        a_pt, b_pt = _world(f, u_lo, cross, p["lane_z"])[:2], _world(f, u_lo + L, cross, p["lane_z"])[:2]
        if dirn < 0:
            a_pt, b_pt = b_pt, a_pt
        out.append(dict(lane_id=lane_id, a=a_pt, b=b_pt, z=p["lane_z"], speed=cycle / p["t_loop"], pal=pal, streaks=streaks))
    return out


def fog_fields(city: Dict[str, Any], h_sky: float, p: Dict[str, Any]) -> List[Dict[str, Any]]:
    """One fog box over the city extent (padded), from ground to `max(fog_top_min, 2.5 * H_SKY)`."""
    xs = [q[0] for b in city["buildings"] for pt in b["parts"] for q in pt["poly"]]
    ys = [q[1] for b in city["buildings"] for pt in b["parts"] for q in pt["poly"]]
    top = max(p["fog_top_min"], p["fog_sky_k"] * h_sky)
    pad = p["fog_pad"]
    return [dict(id="city", min=[min(xs) - pad, min(ys) - pad, 0.0], max=[max(xs) + pad, max(ys) + pad, top], density=1.0)]


def dress_street(derive: Dict[str, Any], city: Dict[str, Any], preset: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The typed placement lists of `dress_<run>.json` v1 for a street derive (a new dict)."""
    p = dict(PRESET, **(preset or {}))
    built = building_tops(city)
    h = heights(derive, built, p)
    return dict(version=VERSION, run=derive["run"], layout_seed=derive["layout_seed"], kind="street",
                signs=signs(derive, p), lamps=lamps(derive, p), washes=washes(derive, p), glows=glows(derive, p),
                beams=beams(derive, built, h["h_front"], p), streak_lanes=streak_lanes(derive, p),
                fog_fields=fog_fields(city, h["h_sky"], p))


def flatten_positions(dress: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Every list item with a `pos` as `{list, pos}` (what the 12.4.5c foreground check reads)."""
    out = []
    for name in ("signs", "lamps", "washes", "glows", "beams"):
        for it in dress.get(name, []):
            out.append(dict(list=name, pos=it["pos"]))
    return out
