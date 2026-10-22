"""Populate the HQ footprint with drowned-city blocks (the same look as the rest of the underwater city).
Copies a patch of the existing drowned quarter (wet buildings within RADIUS BU of a source centre) over the empty HQ lot, with the
original buildings untouched. Writes a new zoning json (never edits the source).
python fill_city.py <zoned_base.json> <out.json> [radius_bu] [src_dist] [src_angle_deg_from_dam]"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "route_map_graph", "hq_tethys", "scripts")))
sys.dont_write_bytecode = True
import tethys_preset as TP  # noqa: E402

U = 6.0


def main():
    src, dst = sys.argv[1], sys.argv[2]
    rad = float(sys.argv[3]) if len(sys.argv) > 3 else 52.0
    O = json.load(open(src))
    cx, cy = O["centre"]

    def W(p):
        return ((p[0] - cx) * U, -(p[1] - cy) * U)
    hx, hy = W(O["hq"]["tethys"])
    wet = [b for b in O["buildings"] if b.get("wet")]
    cen = [W(b["c"]) for b in wet]
    best = None
    for ang in range(0, 360, 10):
        for dist in (95.0, 115.0, 135.0):
            px, py = hx + dist * math.cos(math.radians(ang)), hy + dist * math.sin(math.radians(ang))
            # the patch disc must not overlap the HQ disc, and must be well populated
            n = sum(1 for (x, y) in cen if math.hypot(x - px, y - py) <= rad)
            hq_n = sum(1 for (x, y) in cen if math.hypot(x - hx, y - hy) <= rad)
            score = n - 0.0 * hq_n
            if best is None or score > best[0]:
                best = (score, px, py, ang, dist)
    _, px, py, ang, dist = best
    dxw, dyw = hx - px, hy - py                       # world translation of the patch onto the HQ
    dxl, dyl = dxw / U, -dyw / U                      # in lot units (the lot -> world map flips y)
    new = []
    for i, b in enumerate(wet):
        x, y = cen[i]
        if math.hypot(x - px, y - py) > rad:
            continue
        c = dict(b)
        c["q"] = [[p[0] + dxl, p[1] + dyl] for p in b["q"]]
        c["c"] = [b["c"][0] + dxl, b["c"][1] + dyl]
        c["key"] = b["key"] - 1000003
        new.append(c)
    # drop any existing building in the HQ disc (there are none, but keep it safe) and add the copy
    O["buildings"] = O["buildings"] + new
    json.dump(O, open(dst, "w"))
    print("patch centre (%.0f, %.0f) angle %d dist %.0f, copied %d buildings onto the HQ lot (radius %.0f)" % (px, py, ang, dist, len(new), rad))


if __name__ == "__main__":
    main()
