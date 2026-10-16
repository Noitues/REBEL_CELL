"""Meridian v3: the freight line's centreline in the HQ's local frame (pure python, no Blender).

Source of truth: the city's polyline D:/rc_scratch/city_all_corps/meridian_rail.json (world one-city BU, the HQ centre
`hq_centre`, points gate -> seawall terminal, `deck_z` 17.5). Local HQ-kit units = (world - hq_centre) / k_units
(0.2375, PIPELINE_SPEC 8.6), so the deck stands at 17.5 / 0.2375 = 73.7 kit BU.

v3 routing (DESIGN.md): the line runs E-W along the lot's N edge THROUGH the castle (the two rail gates), at grade;
out of the W rail gate it eases north onto the city line's first westbound leg (the city's y 255 = local y 138.9),
climbs on the city's ramp to the deck at the city's corner (-117, 255) and from there follows the city polyline
corner for corner to the seawall terminal. East of the lot it runs on at grade into the city (the inland line).

    import meridian_rail as MR
    pts = MR.centreline(cp)      # [(x, y, z)] local kit BU, east -> west -> the port; cp = PRESET["hq"]["compound"]
    MR.segments(cp, hw)          # [(ax, ay, bx, by, hw)] for the city corridors (no buildings on the line)
"""
import json
import math
import os

FALLBACK = {"hq_centre": [18.0, 222.0], "deck_z": 17.5,
            "points": [[23.0, 247.6, 0.7], [23.0, 256.0, 0.958], [21.0, 255.0, 1.271], [-117.0, 255.0, 17.5],
                       [-117.0, 471.0, 17.5], [-177.0, 471.0, 17.5], [-177.0, 501.0, 17.5], [-189.0, 501.0, 17.5],
                       [-248.431, 560.431, 8.7]]}


def city_line(cp):
    rc = cp["rail"]
    path = rc.get("json")
    try:
        d = json.load(open(path)) if path and os.path.exists(path) else FALLBACK
    except (OSError, ValueError):
        d = FALLBACK
    k = rc["k_units"]
    hx, hy = d["hq_centre"]
    return [((x - hx) / k, (y - hy) / k, z / k) for (x, y, z) in d["points"]], d["deck_z"] / k


def centreline(cp):
    rc = cp["rail"]
    yc = sum(rc["y"]) / 2.0
    L = cp["lot"]
    pts, deck = city_line(cp)
    # the city's first westbound leg (index 2 -> 3): its y, and the corner where the deck is reached
    y_w = pts[3][1]
    x_deck = pts[3][0]
    out = [(rc["x_east"], yc, 0.0), (L + 2.0, yc, 0.0), (-L - 2.0, yc, 0.0)]
    # the ease north (a smoothstep S-curve) from the W rail gate onto the city leg
    x0, x1 = -L - 10.0, -L - 10.0 - rc["ease_len"]
    n = 10
    for i in range(n + 1):
        t = i / n
        e = t * t * (3 - 2 * t)
        out.append((x0 + (x1 - x0) * t, yc + (y_w - yc) * e, 0.0))
    out.append((x_deck, y_w, deck))
    out += [tuple(p) for p in pts[4:]]
    # z: at grade to the ramp start, then linear by length to the deck at the city corner (the city's own ramp)
    acc, s = [0.0], 0.0
    for a, b in zip(out, out[1:]):
        s += math.hypot(b[0] - a[0], b[1] - a[1])
        acc.append(s)
    i_r = next(i for i, p in enumerate(out) if p[0] <= -L - 2.0)
    i_d = next(i for i, p in enumerate(out) if abs(p[0] - x_deck) < 1e-6 and abs(p[2] - deck) < 1e-6)
    res = []
    for i, p in enumerate(out):
        if i <= i_r:
            z = 0.0
        elif i < i_d:
            z = deck * (acc[i] - acc[i_r]) / max(acc[i_d] - acc[i_r], 1.0)
        else:
            z = p[2]
        res.append((p[0], p[1], z))
    return res


def segments(cp, hw):
    c = centreline(cp)
    return [(a[0], a[1], b[0], b[1], hw) for a, b in zip(c, c[1:])]


# ------------------------------------------------------------ the truck RING ROAD and its highway exits (designer
# round 2: "a ring of WIDER roads ... leading off to highway on-ramps at the lot edges"; the city agent hubs the city
# highways here, so the exits are data: name, start point on the ring's outer kerb, heading (deg from north, clockwise)
def exits(cp):
    rg = cp["ring"]
    r1 = rg["r"][1]
    out = []
    for (name, side, u) in rg["exits"]:
        if side == "S":
            out.append(dict(name=name, p=(u, -r1, 0.0), heading=180.0))
        elif side == "W":
            out.append(dict(name=name, p=(-r1, u, 0.0), heading=270.0))
        elif side == "E":
            out.append(dict(name=name, p=(r1, u, 0.0), heading=90.0))
        else:
            out.append(dict(name=name, p=(u, r1, 0.0), heading=0.0))
    return out


def highways(cp):
    """{name: [(x, y, z)]}: each exit's on-ramp (grade -> deck over `ramp` BU) then the elevated highway straight out."""
    rg = cp["ring"]
    hw = {}
    for e in exits(cp):
        a = math.radians(e["heading"])
        ux, uy = math.sin(a), math.cos(a)
        x0, y0, _ = e["p"]
        pts = []
        for s in (0.0, rg["ramp"] * 0.5, rg["ramp"], rg["ramp"] + 120.0, rg["reach"]):
            z = rg["deck_z"] * (0.5 - 0.5 * math.cos(math.pi * min(1.0, s / rg["ramp"])))
            pts.append((x0 + ux * s, y0 + uy * s, z))
        hw[e["name"]] = pts
    return hw


def highway_segments(cp, hw_):
    out = []
    for pts in highways(cp).values():
        out += [(a[0], a[1], b[0], b[1], hw_) for a, b in zip(pts, pts[1:])]
    return out


if __name__ == "__main__":
    import hq_preset as HP
    for p in centreline(HP.PRESET["hq"]["compound"]):
        print("%8.1f %8.1f %6.1f" % p)
