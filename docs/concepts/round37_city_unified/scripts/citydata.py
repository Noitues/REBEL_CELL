"""Round 25: the game's city layout (round6_city_restyle/city_layout.json, read-only) in LOT space.

The round 6 export stores everything as projected screen points (city px) of the game's iso map:
    X = ox + (x - y) * 34,   Y = oy + (x + y) * 17      (x, y in lots; heights as screen px)
This module inverts that projection so the Blender close-ups can rebuild the SAME streets (tile by tile, with
the game's lane colours and traffic), the same buildings (every extrusion's footprint, base, height and taper),
the plazas, traffic trails and REBEL_CELL's fist roads, around any point of the city.

python citydata.py      -> ../scratch/layout/<job>.json for every close-up / site / map-sprite job
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
SRC = os.path.join(OUT, "..", "round6_city_restyle", "city_layout.json")
DST = os.path.join(OUT, "scratch", "layout")
TA, TB = 34.0, 17.0
CORPS = ["meridian", "solace", "halcyon", "orbital", "rebel_cell"]


def load():
    return json.load(open(SRC))


class Lots:
    def __init__(self, d):
        self.d = d
        self.ox, self.oy = d["camera"]

    def inv(self, X, Y):
        a = (X - self.ox) / TA
        s = (Y - self.oy) / TB
        return ((a + s) / 2.0, (s - a) / 2.0)

    def iso(self, x, y):
        return (self.ox + (x - y) * TA, self.oy + (x + y) * TB)

    def pts(self, flat):
        return [self.inv(flat[i], flat[i + 1]) for i in range(0, len(flat), 2)]


def hq_centres(d):
    out = {}
    for c in d["contexts"]:
        if c["kind"] == "hq":
            r = c["rect"]
            out[c["terr"]] = (r[0] + r[2] / 2.0, r[1] + r[3] / 2.0)
    return out


def fist_lots(d, L):
    return [(L.inv(s[0], s[1]), L.inv(s[2], s[3])) for s in d["fist"]]


def rc_base_centre(d, L):
    """The Cell's base sits in the palm of the fist: the centroid of the fist road network."""
    segs = fist_lots(d, L)
    xs = [p[0] for s in segs for p in s]
    ys = [p[1] for s in segs for p in s]
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def street_cells(d):
    return {(s["i"], s["j"]) for s in d["streets"]}


def seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy or 1e-9
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + dx * t), py - (ay + dy * t))


def near_fist(p, segs, r):
    return any(seg_dist(p, a, b) < r for a, b in segs)


TERR_GRID = {}


def terr_grid(d, L):
    """lot cell -> territory id of the buildings standing there (the district a Site belongs to)."""
    if TERR_GRID:
        return TERR_GRID
    for c in d["contexts"]:
        if c["kind"] == "bld" and "cell" in c:
            x, y = c["cell"][0], c["cell"][1]
            TERR_GRID[(x, y)] = c.get("terr", "")
    return TERR_GRID


def find_site(d, centre, avoid, size=6, rmin=12, rmax=26, corp=None, L=None):
    """A street-free size x size lot square in the corp's own district, nearest to rmin.. from the HQ,
    away from `avoid` and from the fist roads."""
    cells = street_cells(d)
    tg = terr_grid(d, L)
    fist = fist_lots(d, L) if L else []
    best = None
    cx, cy = centre
    for i in range(int(cx - rmax), int(cx + rmax)):
        for j in range(int(cy - rmax), int(cy + rmax)):
            dd = math.hypot(i + size / 2 - cx, j + size / 2 - cy)
            if dd < rmin or dd > rmax:
                continue
            if any((a, b) in cells for a in range(i, i + size) for b in range(j, j + size)):
                continue
            if any(math.hypot(i + size / 2 - ax, j + size / 2 - ay) < ar for (ax, ay), ar in avoid):
                continue
            own = [tg.get((a, b)) for a in range(i - 2, i + size + 2) for b in range(j - 2, j + size + 2) if (a, b) in tg]
            if corp and (not own or sum(1 for o in own if o == corp) < 0.8 * len(own)):
                continue
            if corp != "rebel_cell" and fist and near_fist((i + size / 2, j + size / 2), fist, size + 3):
                continue
            # the close-up camera looks in from +x +y (lots): no HQ may stand between it and the Site
            sx_, sy_ = i + size / 2, j + size / 2
            if any(0 < (ax - sx_) + (ay - sy_) < 70 and abs((ax - sx_) - (ay - sy_)) < 22 for (ax, ay), _ in avoid):
                continue
            # prefer squares lying toward the viewer (+x+y) so the street they front is visible, then distance
            score = abs(dd - rmin) - 0.15 * ((i - cx) + (j - cy))
            if best is None or score < best[0]:
                best = (score, (i + size / 2.0, j + size / 2.0))
    return best[1] if best else None


def export(d, L, centre, radius, remove, path, extra=None):
    """Everything within `radius` lots of centre; buildings whose footprint centre lies in a `remove`
    zone ((x, y), r) are dropped (the HQ / base / site stands there)."""
    cx, cy = centre
    ctxs = d["contexts"]
    fist = fist_lots(d, L)

    def inside(p, r=radius):
        return math.hypot(p[0] - cx, p[1] - cy) < r

    def removed(p):
        return any(math.hypot(p[0] - a, p[1] - b) < r for (a, b), r in remove)

    tiles = []
    for s in d["streets"]:
        q = L.pts(s["p"])
        c = (sum(p[0] for p in q) / 4, sum(p[1] for p in q) / 4)
        if not inside(c):
            continue
        ab = L.pts(s["ab"]) if "ab" in s else None
        tiles.append(dict(q=q, ab=ab, col=s["col"][:3] if "col" in s else None, tr=s.get("traffic", 0.0), i=s["i"], j=s["j"]))
    blds = []
    for p in d["prims"]:
        if p["t"] != "ext":
            continue
        ci = p["ctx"]
        if ci < 0 or ctxs[ci]["kind"] == "hq":
            continue
        q = L.pts(p["b"])
        c = (sum(a[0] for a in q) / len(q), sum(a[1] for a in q) / len(q))
        if not inside(c) or removed(c):
            continue
        if near_fist(c, fist, 0.9):  # the fist roads stay readable (same rule on the v3 city map)
            continue
        blds.append(dict(q=q, z0=p["z0"], h=p["h"], ts=p["ts"], ink=p["ink"][:3], terr=ctxs[ci].get("terr", ""), ci=ci,
                         key=p["key"]))
    plazas = []
    for pz in d["plazas"]:
        q = L.pts(pz["p"])
        c = (sum(p[0] for p in q) / 4, sum(p[1] for p in q) / 4)
        if inside(c):
            plazas.append(dict(q=q, terr=pz["terr"]))
    trails = []
    for t in d["trails"]:
        a, b = L.inv(*t["a"]), L.inv(*t["b"])
        if inside(a):
            trails.append(dict(a=a, b=b, col=t["col"][:3]))
    fsegs = [dict(a=a, b=b) for a, b in fist if inside(a, radius + 20) or inside(b, radius + 20)]
    terr = {t["id"]: t["color"][:3] for t in d["territories"]}
    out = dict(centre=centre, radius=radius, tiles=tiles, buildings=blds, plazas=plazas, trails=trails, fist=fsegs,
               fist_col=d["colors"]["fist"][:3], fist_half=d["fist_half"], terr=terr, street=d["colors"]["street"][:3],
               ground=d["colors"]["ground"][:3])
    if extra:
        out.update(extra)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(out, open(path, "w"))
    return out


def jobs(d, L):
    """(job name, corp, kind, centre, remove zones). HQs sit on their 10 x 10 HQ lot; the Cell's base in the
    fist's palm; regular Sites in a street-free block of the district."""
    hq = hq_centres(d)
    hq["rebel_cell"] = rc_base_centre(d, L)
    out = []
    for corp in CORPS:
        c = hq[corp]
        out.append(("%s_hq" % corp, corp, "hq", c, [(c, 5.6 if corp != "rebel_cell" else 4.6)]))
    sites = {}
    terr = {t["id"]: tuple(t["at"]) for t in d["territories"]}
    for corp in CORPS:
        avoid = [((hq[c][0], hq[c][1]), 9.0) for c in hq]
        s = find_site(d, hq[corp], avoid, size=6 if corp != "rebel_cell" else 5, corp=corp, L=L)
        if s is None:
            s = find_site(d, hq[corp], avoid, size=4, rmin=10, rmax=34, corp=corp, L=L)
        sites[corp] = s
        out.append(("%s_site" % corp, corp, "site", s, [(s, 3.2)]))
    return out, hq, sites


if __name__ == "__main__":
    d = load()
    L = Lots(d)
    js, hq, sites = jobs(d, L)
    meta = {}
    for name, corp, kind, c, rem in js:
        r = 60 if kind == "hq" else 40
        if corp == "rebel_cell" and kind == "hq":
            r = 75
        if corp == "solace" and kind == "hq":  # the tallest HQ: its camera sees the farthest
            r = 90
        hqs = {k: v for k, v in hq.items()}
        o = export(d, L, c, r, rem + [(v, 5.6 if k != "rebel_cell" else 4.6) for k, v in hqs.items()], os.path.join(DST, name + ".json"),
                   extra=dict(corp=corp, kind=kind, hqs=hqs))
        meta[name] = dict(centre=c, screen=L.iso(*c), n_tiles=len(o["tiles"]), n_blds=len(o["buildings"]), n_fist=len(o["fist"]))
        print(name, meta[name], flush=True)
    json.dump(dict(jobs=meta, hq=hq, sites=sites), open(os.path.join(DST, "meta.json"), "w"), indent=1)
    segs = fist_lots(d, L)
    xs = [p[0] for s in segs for p in s]
    ys = [p[1] for s in segs for p in s]
    print("fist extent lots", min(xs), max(xs), min(ys), max(ys))
