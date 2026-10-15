"""Storyboard: the CITY FILL rule (pure python, deterministic, seed 9950) - the city around the netrun street, so the HQ
aerial and the dive see a whole city in the AAA-2 kit instead of the side-view stage set.

Rule (inputs: the r3 stage bounds, the route camera poses from sb_cams, the preset's "city_fill" keys):
  1. a street grid: E-W streets (the netrun street's road continued, then every `block_y`), N-S streets every `block_x`;
  2. every block is split into lots (recursive seeded split, `lot` sizes, alley gaps) and each lot holds one building;
  3. the r3 stage (route row, mid row, far city: STAGE) is left untouched; lots overlapping it are dropped;
  4. lots in the APPROACH corridor (where the dive lands, south of the street) are flagged `hide` (hidden by the render
     driver once they leave the frame during the dive, so they never pop);
  5. height: a downtown falloff from the street, seeded spread; then capped so that
       a) seen from every route camera (OVERVIEW, DECISION) a fill building that projects into the frame stays under the
          r3 skyline (its top's elevation tan below 0.85 x that of the lowest far-layer roof), so the approved views keep
          their skyline;
       b) seen from the AERIAL, no building in front of the netrun street covers it (its top projects below the street's
          protected box) - the "never hide the route" rule of v3_dynamic, applied to the HQ framing;
  6. the Cell's network: CORE = the tallest lot in the block nearest `core_at` (relative to the relay); the owned nodes =
     the tallest lot in each of the next N blocks by distance from CORE (ties by block id); links = a Manhattan MST along
     street centre lines; the relay (route column 0) is the network's frontier node and the TARGET column the Site.
     Pinned Sites (exploits, Heat objectives) = seeded picks among blocks in a distance band, on frame.
Outputs: build() -> dict(buildings=[...], streets=[...], network=dict(...)).
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import cam_rig as R  # noqa: E402
import sgraph3 as G  # noqa: E402

CFG = dict(
    seed=9950,
    region=(-1650.0, -1450.0, 1850.0, 1450.0),   # x0, y0, x1, y1
    road_y=(-40.0, -9.0),                         # the netrun street's road (r3 street geometry)
    block_x=170.0, block_y=165.0, street_w=24.0,
    lot=(16.0, 46.0), alley=(2.0, 5.0), inset=4.0,
    h_down=(18.0, 96.0), h_far=(12.0, 52.0), h_scale=700.0,     # downtown heights near the street, falling off
    stage=(-275.0, -62.0, 475.0, 335.0),         # the r3 stage set (route row, mid row, far layers): untouched
    approach=(-215.0, -420.0, 395.0, -62.0),      # the dive's landing corridor (south of the street)
    skyline_k=0.85, far_low=(110.0, 260.0),      # lowest far-layer roof z at its depth y
    n_owned=7, core_at=(-420.0, 200.0), n_pins=6,
)

STAGE_CAMS = None


def _cams():
    import sb_cams as SB
    return SB


def _elev(p, P):
    """Elevation tan of world point P from pose p's camera (horizontal distance)."""
    c = p.loc()
    d = math.hypot(P[0] - c[0], P[1] - c[1])
    return (P[2] - c[2]) / max(d, 1e-3)


def _in_frame(p, pts, margin=0.0):
    q = [p.proj(P) for P in pts]
    q = [v for v in q if v]
    if not q:
        return False
    xs, ys = [v[0] for v in q], [v[1] for v in q]
    return max(xs) > -margin and min(xs) < R.W + margin and max(ys) > -margin and min(ys) < R.H + margin


def _overlap(a, b):
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def streets():
    c = CFG
    x0, y0, x1, y1 = c["region"]
    ys = [sum(c["road_y"]) / 2.0]
    y = ys[0]
    while y - c["block_y"] > y0:
        y -= c["block_y"]
        ys.append(y)
    y = 350.0 + c["street_w"] / 2                    # the first street north of the stage
    while y < y1:
        ys.append(y)
        y += c["block_y"]
    xs = []
    x = 100.0
    while x > x0:
        xs.append(x)
        x -= c["block_x"]
    x = 100.0 + c["block_x"]
    while x < x1:
        xs.append(x)
        x += c["block_x"]
    return sorted(xs), sorted(ys)


def _split(r, rect, out, lo, hi):
    x0, y0, x1, y1 = rect
    w, h = x1 - x0, y1 - y0
    if w <= hi and h <= hi:
        out.append(rect)
        return
    if w >= h:
        s = r.uniform(0.35, 0.65) * w
        s = max(lo, min(w - lo, s))
        _split(r, (x0, y0, x0 + s, y1), out, lo, hi)
        _split(r, (x0 + s, y0, x1, y1), out, lo, hi)
    else:
        s = r.uniform(0.35, 0.65) * h
        s = max(lo, min(h - lo, s))
        _split(r, (x0, y0, x1, y0 + s), out, lo, hi)
        _split(r, (x0, y0 + s, x1, y1), out, lo, hi)


def build(aerial=True):
    c = CFG
    SB = _cams()
    r = random.Random(c["seed"])
    xs, ys = streets()
    hw = c["street_w"] / 2
    rx0, ry0, rx1, ry1 = c["region"]
    gx = [rx0 - 40] + xs + [rx1 + 40]
    gy = [ry0 - 40] + ys + [ry1 + 40]
    blocks = []
    for i in range(len(gx) - 1):
        for j in range(len(gy) - 1):
            bx0, bx1 = gx[i] + hw + c["inset"], gx[i + 1] - hw - c["inset"]
            by0, by1 = gy[j] + hw + c["inset"], gy[j + 1] - hw - c["inset"]
            # the netrun street's road edge is the r3 road, not the grid's half width
            if abs(gy[j] - sum(c["road_y"]) / 2) < 1:
                by0 = c["road_y"][1] + c["inset"]
            if abs(gy[j + 1] - sum(c["road_y"]) / 2) < 1:
                by1 = c["road_y"][0] - c["inset"]
            if bx1 - bx0 < 10 or by1 - by0 < 10:
                continue
            blocks.append(dict(id=len(blocks), rect=(bx0, by0, bx1, by1)))
    rcx = (G.col_x(0)[0] + G.col_x(G.LAST)[1]) / 2
    prot = [(x, y, z) for x in (G.col_x(0)[0] - 4, G.col_x(G.LAST)[1] + 4) for y in (-40.0, 16.0) for z in (0.0, 30.0)]
    pq = [SB.AERIAL.proj(P) for P in prot] if aerial else [(0, 0), (1, 1)]
    pbox = (min(q[0] for q in pq), min(q[1] for q in pq), max(q[0] for q in pq), max(q[1] for q in pq))
    cams = (SB.OVERVIEW, SB.DECISION)
    route_cams = (SB.OVERVIEW, SB.DECISION, SB.HOVER1, SB.HOVER2)
    path = [SB.dive_pose(k / 60.0).loc() for k in range(61)] if aerial else []
    far_e = {id(p): _elev(p, (0.0, c["far_low"][1], c["far_low"][0])) for p in cams}
    blds = []
    for b in blocks:
        lots = []
        _split(r, b["rect"], lots, *c["lot"])
        for lot in lots:
            x0, y0, x1, y1 = lot
            g = (r.uniform(*c["alley"]), r.uniform(*c["alley"]), r.uniform(*c["alley"]), r.uniform(*c["alley"]))
            x0, y0, x1, y1 = x0 + g[0] / 2, y0 + g[1] / 2, x1 - g[2] / 2, y1 - g[3] / 2
            d = math.hypot((x0 + x1) / 2 - rcx, max(0.0, abs((y0 + y1) / 2 + 25.0) - 60.0))
            kdown = math.exp(-d / c["h_scale"])
            lo = c["h_far"][0] + (c["h_down"][0] - c["h_far"][0]) * kdown
            hi = c["h_far"][1] + (c["h_down"][1] - c["h_far"][1]) * kdown
            h = lo + (hi - lo) * (r.random() ** 1.7)
            style = r.choices(["block", "setback", "tower", "slab", "drum"], [0.38, 0.2, 0.16, 0.16, 0.10])[0]
            seed = r.randrange(1 << 30)
            rect = (x0, y0, x1, y1)
            if x1 - x0 < 6 or y1 - y0 < 6 or _overlap(rect, c["stage"]):
                continue
            hide = False
            if any(x0 - 12 < p.loc()[0] < x1 + 12 and y0 - 12 < p.loc()[1] < y1 + 12 for p in route_cams):
                continue            # never build round a route camera
            if _overlap(rect, c["approach"]) or y0 < c["road_y"][0] - 20.0:
                # 4: the landing corridor: no route camera may see the lot at all (cap, else drop), and the dive's
                # camera path keeps 15 BU of clearance
                for _ in range(30):
                    pts = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (0.0, h)]
                    if any(_in_frame(p, pts, 4) for p in route_cams):
                        h *= 0.85
                    else:
                        break
                if any(_in_frame(p, [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (0.0, h)], 4)
                       for p in route_cams):
                    continue
                for (cx, cy, cz) in path:
                    if x0 - 6 < cx < x1 + 6 and y0 - 6 < cy < y1 + 6:
                        h = min(h, cz - 15.0)
                if h < 5.0:
                    continue
            # 5a: under the r3 skyline from every route camera that sees it
            for p in cams:
                pts = [(x, y, h) for x in (x0, x1) for y in (y0, y1)]
                if _in_frame(p, pts, 40):
                    e = far_e[id(p)] * c["skyline_k"]
                    cmax = min(p.loc()[2] + e * math.hypot(x - p.loc()[0], y - p.loc()[1]) for x in (x0, x1) for y in (y0, y1))
                    h = min(h, max(6.0, cmax))
            # 5b: never cover the netrun street in the aerial
            if aerial and (y0 + y1) / 2 < c["road_y"][0]:
                for _ in range(24):
                    q = [SB.AERIAL.proj((x, y, h)) for x in (x0, x1) for y in (y0, y1)]
                    q = [v for v in q if v]
                    bb = (min(v[0] for v in q), min(v[1] for v in q), max(v[0] for v in q), max(v[1] for v in q))
                    if _overlap(bb, (pbox[0], pbox[1], pbox[2], pbox[3] + 8)) and h > 6.0:
                        h *= 0.85
                    else:
                        break
            blds.append(dict(id=len(blds), block=b["id"], rect=rect, h=round(h, 2), style=style, seed=seed, hide=hide))
    if not aerial:
        return dict(blocks=blocks, buildings=blds, net_blocks=net_blocks(blocks, blds))
    net = network(blocks, blds, r)
    return dict(buildings=blds, streets=dict(xs=xs, ys=ys, w=c["street_w"]), blocks=blocks, network=net,
                region=c["region"], road_y=c["road_y"])


def _bc(b):
    x0, y0, x1, y1 = b["rect"]
    return ((x0 + x1) / 2, (y0 + y1) / 2)


def net_blocks(blocks, blds):
    """The Cell's territory by geometry only (no heights): the block nearest the core anchor, then the n_owned blocks
    nearest it (block centres, ties by id). Used to frame the HQ aerial before the heights are capped for it."""
    c = CFG
    relay = (sum(G.col_x(0)) / 2, G.DY[0] + 6.0)
    ca = (relay[0] + c["core_at"][0], relay[1] + c["core_at"][1])
    have = {b["block"] for b in blds}
    usable = [bk for bk in blocks if bk["id"] in have]
    core_b = sorted(usable, key=lambda bk: (math.hypot(_bc(bk)[0] - ca[0], _bc(bk)[1] - ca[1]), bk["id"]))[0]
    near = sorted([bk for bk in usable if bk["id"] != core_b["id"]],
                  key=lambda bk: (math.hypot(_bc(bk)[0] - _bc(core_b)[0], _bc(bk)[1] - _bc(core_b)[1]), bk["id"]))
    return [core_b] + near[:c["n_owned"]]


def network(blocks, blds, r):
    """The Cell's network (rule 6)."""
    c = CFG
    SB = _cams()
    relay = (sum(G.col_x(0)) / 2, G.DY[0] + 6.0, G.roof_z(0) + 2.0)
    site = (sum(G.col_x(G.LAST)) / 2, G.DY[G.LAST] + 6.0, G.roof_z(G.LAST) + 6.0)
    ca = (relay[0] + c["core_at"][0], relay[1] + c["core_at"][1])
    by_block = {}
    for b in blds:
        by_block.setdefault(b["block"], []).append(b)
    usable = [bk for bk in blocks if bk["id"] in by_block]

    def bdist(bk, p):
        x0, y0, x1, y1 = bk["rect"]
        return math.hypot((x0 + x1) / 2 - p[0], (y0 + y1) / 2 - p[1])

    def tallest(bid):
        return sorted(by_block[bid], key=lambda b: (-b["h"], b["id"]))[0]
    nb = net_blocks(blocks, blds)
    core_b = nb[0]
    core = tallest(core_b["id"])
    near = nb[1:]
    owned = []
    for bk in near:
        t = tallest(bk["id"])
        if t["hide"] and bdist(bk, relay) < 260:
            pass
        owned.append(t)
        if len(owned) >= c["n_owned"]:
            break
    nodes = [dict(id="core", kind="core", pos=(_bc(core)[0], _bc(core)[1], core["h"] + 2.0), bld=core["id"])]
    for k, b in enumerate(owned):
        nodes.append(dict(id="own%d" % k, kind="owned", pos=(_bc(b)[0], _bc(b)[1], b["h"] + 2.0), bld=b["id"]))
    nodes.append(dict(id="relay", kind="relay", pos=relay))
    # MST (Prim, Manhattan distance, deterministic)
    pts = {n["id"]: n["pos"] for n in nodes}
    ids = [n["id"] for n in nodes]
    inn = {"core"}
    links = []
    while len(inn) < len(ids):
        best = None
        for a in sorted(inn):
            for b in ids:
                if b in inn:
                    continue
                d = abs(pts[a][0] - pts[b][0]) + abs(pts[a][1] - pts[b][1])
                if best is None or (d, a, b) < best:
                    best = (d, a, b)
        inn.add(best[2])
        links.append((best[1], best[2]))
    # pinned Sites: seeded picks in a distance band from the street, on the aerial frame, not the network's blocks
    used = {core_b["id"]} | {b["block"] for b in owned}
    cand = []
    for bk in usable:
        if bk["id"] in used:
            continue
        d = bdist(bk, (93.0, -25.0))
        if 150 < d < 900:
            t = tallest(bk["id"])
            q = SB.AERIAL.proj((_bc(t)[0], _bc(t)[1], t["h"]))
            if q and 330 < q[0] < 1880 and 110 < q[1] < 860:
                cand.append((bk["id"], t))
    cand.sort(key=lambda v: v[0])
    r2 = random.Random(c["seed"] + 7)
    r2.shuffle(cand)
    pins = []
    kinds = ["exploit", "heat", "heat", "exploit", "heat", "cleared"]
    for bid, t in cand:
        p = (_bc(t)[0], _bc(t)[1], t["h"] + 2.0)
        if all(math.hypot(p[0] - q["pos"][0], p[1] - q["pos"][1]) > 150 for q in pins):
            pins.append(dict(id="pin%d" % len(pins), kind=kinds[len(pins) % len(kinds)], pos=p, bld=t["id"]))
        if len(pins) >= c["n_pins"]:
            break
    return dict(nodes=nodes, links=links, pins=pins, relay=relay, site=site)


def street_path(a, b, ys):
    """A Manhattan path between two ground points along the street grid: drop to the nearest E-W street, run along it,
    then up the N-S street nearest the target (all at z 0.3)."""
    sy = min(ys, key=lambda y: (abs(y - a[1]) + abs(y - b[1]), y))
    return [(a[0], a[1], 0.3), (a[0], sy, 0.3), (b[0], sy, 0.3), (b[0], b[1], 0.3)]


if __name__ == "__main__":
    import json
    d = build()
    print("buildings", len(d["buildings"]), "hide", sum(b["hide"] for b in d["buildings"]),
          "blocks", len(d["blocks"]))
    print("network", [(n["id"], [round(v) for v in n["pos"]]) for n in d["network"]["nodes"]])
    print("links", d["network"]["links"])
    print("pins", [(p["kind"], [round(v) for v in p["pos"]]) for p in d["network"]["pins"]])
    out = os.path.join(os.path.dirname(HERE), "scratch", "cityfill.json")
    json.dump(d, open(out, "w"))
    print("saved", out)
