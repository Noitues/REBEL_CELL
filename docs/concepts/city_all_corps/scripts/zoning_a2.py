"""City-all-corps round 4: the A2 layout source (pure Python + numpy + PIL; no Blender).

    python zoning_a2.py     -> D:/rc_scratch/city_all_corps/zoned_a2.json, a2_fields.npz, zoning_map_a2.png

Converts docs/concepts/city_planner/city_A2.json ("Horseshoe Bay A2": metres, origin at the centre, +X east, +Y north,
+-10 km) into the zoned structure the build reads. SCALE (city_preset.A2): 1 lot = 100 m = 6 BU (1 BU = 16.67 m); the plan's
20 km square is 200 lots, about the lot count of the legacy map + ring, so density and the hero camera stay comparable.
Lot coords x = X / 100 + CX, y = CY - Y / 100 (lot y points south); every polygon / polyline below is in lots.

What is taken from the JSON: ocean + lakes + rivers + canals (water), the drowned quarter and its dams, the Bay Barrier
and sea walls, the district polygons (the Old City = REBEL_CELL, six corps), the HQ positions (the colour-influence
centres), the roads (ring R1 / outer ring R2, motorways, truck roads, arterials) with their interchanges and ramps, the
rails (freight, commuter, metro) and stations, the port (terminal, piers, yard), parks, plazas, cemeteries, industry,
informal housing, the airport, the spaceport, the corporate walls, markets and the landmark glyphs.
Not mapped: terrain hills (the city is built flat), the undercity, drone corridors, ferries, checkpoints, neighbourhood
names, the offshore wind farm (see NOTES.md, Layout A2).

Building rules kept from the legacy build: colour by HQ proximity (city_rules.district_weights, own polygon boosted),
the REBEL_CELL (Old City) in the sprawl palette, an organic suburb edge (value noise on the R2 outline), lower suburbs.
The districts' buildings are generated here (map style: sub-lots of a cell); the suburbs are drawn by city_world_a2.py
from the cell classes in a2_fields.npz.
"""
import json
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import city_preset as CP  # noqa: E402
import city_rules as RU  # noqa: E402

A = CP.A2
S = A["m_per_lot"]
CX, CY = RU.CX, RU.CY
I0, J0, N = A["grid"]
SS = 4

J = json.load(open(CP.A2_JSON))
CORP_OF = {"centre": "rebel_cell"}      # district id -> corp key


def lot(p):
    return (p[0] / S + CX, -p[1] / S + CY)


def lots(poly):
    return [lot(p) for p in poly]


def to_px(p):
    return ((p[0] - I0) * SS, (p[1] - J0) * SS)


def raster(polys=(), lines=(), width_cells=0.0):
    """-> bool [N, N] (index [row j, col i]): cells whose supersampled coverage is over half. polys / lines in lots."""
    im = Image.new("L", (N * SS, N * SS), 0)
    d = ImageDraw.Draw(im)
    for q in polys:
        if len(q) >= 3:
            d.polygon([to_px(p) for p in q], fill=255)
    for ln in lines:
        pts = [to_px(p) for p in ln]
        if len(pts) >= 2:
            d.line(pts, fill=255, width=max(1, int(round(width_cells * SS))), joint="curve")
    a = np.asarray(im, np.float32).reshape(N, SS, N, SS).mean((1, 3)) / 255.0
    return a > 0.5


def dist_to(mask):
    """chamfer distance (cells) from every cell to the nearest True cell of mask."""
    INF = 1e9
    d = np.where(mask, 0.0, INF).astype(np.float64)
    for _ in range(2):
        for j in range(N):
            for i in range(N):
                v = d[j, i]
                if i > 0:
                    v = min(v, d[j, i - 1] + 1.0)
                if j > 0:
                    v = min(v, d[j - 1, i] + 1.0)
                    if i > 0:
                        v = min(v, d[j - 1, i - 1] + 1.414)
                    if i < N - 1:
                        v = min(v, d[j - 1, i + 1] + 1.414)
                d[j, i] = v
        for j in range(N - 1, -1, -1):
            for i in range(N - 1, -1, -1):
                v = d[j, i]
                if i < N - 1:
                    v = min(v, d[j, i + 1] + 1.0)
                if j < N - 1:
                    v = min(v, d[j + 1, i] + 1.0)
                    if i < N - 1:
                        v = min(v, d[j + 1, i + 1] + 1.414)
                    if i > 0:
                        v = min(v, d[j + 1, i - 1] + 1.414)
                d[j, i] = v
    return d


def box_blur(a, r, passes=3):
    for _ in range(passes):
        for ax in (0, 1):
            c = np.cumsum(np.pad(a, [(r + 1, r) if k == ax else (0, 0) for k in range(2)], mode="edge"), axis=ax)
            hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + N), axis=ax)
            lo = np.take(c, np.arange(0, N), axis=ax)
            a = (hi - lo) / (2 * r + 1)
    return a


def smooth(x, e0, e1):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def vnoise(shape_xy, cell, seed):
    """value noise on the raster (cells)."""
    ii, jj = np.meshgrid(np.arange(N), np.arange(N))
    out = np.zeros((N, N))
    gx, gy = ii / cell, jj / cell
    x0, y0 = np.floor(gx).astype(int), np.floor(gy).astype(int)
    fx, fy = gx - x0, gy - y0
    sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)

    def h(x, y):
        return np.array([[RU._hash01(seed, int(xx), int(yy)) for xx, yy in zip(rx, ry)] for rx, ry in zip(x, y)])
    v00, v10, v01, v11 = h(x0, y0), h(x0 + 1, y0), h(x0, y0 + 1), h(x0 + 1, y0 + 1)
    out = (v00 * (1 - sx) + v10 * sx) * (1 - sy) + (v01 * (1 - sx) + v11 * sx) * sy
    return out


def seg_d(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy or 1e-9
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - (a[0] + dx * t), p[1] - (a[1] + dy * t))


def in_poly(p, q):
    ins = False
    n = len(q)
    for i in range(n):
        (x0, y0), (x1, y1) = q[i], q[(i + 1) % n]
        if (y0 > p[1]) != (y1 > p[1]) and p[0] < (x1 - x0) * (p[1] - y0) / ((y1 - y0) or 1e-12) + x0:
            ins = not ins
    return ins


def main():
    # ------------------------------------------------------------------ water
    ocean_l = lots(J["terrain"]["ocean_polygon"])
    lakes_l = [lots(l["polygon"]) for l in J["terrain"]["lakes"]]
    ocean = raster([ocean_l])
    lake = raster(lakes_l)
    river = np.zeros((N, N), bool)
    for r in J["terrain"]["rivers"]:
        pl = lots(r["polyline"])
        w = (r["width_start_m"] + r["width_end_m"]) / 2.0 / S
        river |= raster(lines=[pl], width_cells=max(1.0, w * 1.6))      # a river reads at least one cell wide
    dq = J["drowned_quarter"]
    drowned_l = lots(dq["polygon"])
    drowned = raster([drowned_l])
    water = ocean | lake | river
    wet_all = water | drowned
    # ------------------------------------------------------------------ districts (the Old City is REBEL_CELL)
    names = [""]
    dist_id = np.zeros((N, N), np.int8)
    polys = {}
    for d in J["districts"]:
        corp = CORP_OF.get(d["id"], d["id"])
        names.append(corp)
        polys[corp] = lots(d["polygon"])
    for k, corp in enumerate(names):
        if k == 0:
            continue
        m = raster([polys[corp]])
        dist_id[m & (dist_id == 0)] = k
    # ------------------------------------------------------------------ roads / rails (lots) with classes, z and widths
    roads = []
    mi = 0
    for r in J["roads"]:
        cls = r["class"]
        pl = lots(r["polyline"])
        rec = dict(id=r["id"], name=r["name"], cls=cls, closed=bool(r["closed"]), pts=[list(p) for p in pl],
                   tunnels=[[list(p) for p in lots(t)] for t in r.get("tunnels", [])],
                   bridges=[[list(p) for p in lots(b)] for b in r.get("bridges", [])])
        if cls == "ring":
            outer = "Outer" in r["name"]
            rec["z"] = A["z"]["ring2" if outer else "ring"]
            rec["w"] = A["width"]["ring2" if outer else "ring"]
        elif cls == "motorway":
            rec["z"] = A["z"]["motorway"][mi % 2]
            rec["w"] = A["width"]["motorway"]
            mi += 1
        elif cls == "truck":
            rec["z"] = A["z"]["truck"]
            rec["w"] = A["width"]["truck"]
        else:
            rec["z"], rec["w"] = 0.0, r["width_m"] / 16.67
        roads.append(rec)
    rails = []
    for r in J["rails"]:
        rails.append(dict(id=r["id"], name=r["name"], kind=r["kind"], pts=[list(p) for p in lots(r["polyline"])],
                          tunnels=[[list(p) for p in lots(t)] for t in r.get("tunnels", [])], closed=bool(r["closed"])))
    stations = [dict(name=s["name"], kind=s["kind"], pos=list(lot(s["position"])), lines=s["lines"]) for s in J["stations"]]
    inter = []
    for ix in J["interchanges"]:
        inter.append(dict(id=ix["id"], type=ix["type"], pos=list(lot(ix["position"])), roads=ix["roads"],
                          ramps=[[list(p) for p in lots(rp)] for rp in ix["ramps"]]))
    # ------------------------------------------------------------------ land-use rasters
    parks = raster([lots(p["polygon"]) for p in J["parks"]])
    plazas = raster([lots(p["polygon"]) for p in J["plazas"]])
    cemetery = raster([lots(p["polygon"]) for p in J["cemeteries"]])
    industry = raster([lots(p["polygon"]) for p in J["industry"]])
    informal = raster([lots(p["polygon"]) for p in J["informal_housing"]])
    ap = J["airport"]
    airport = raster([lots(ap["polygon"])])
    port = J["port"]
    port_t = raster([lots(port["terminal_polygon"])] + [lots(port["intermodal_yard"])])
    sp = J["spaceport"]
    spx, spy = lot(sp["ring_centre"])
    spaceport = np.zeros((N, N), bool)
    for j in range(N):
        for i in range(N):
            if math.hypot(i + I0 + 0.5 - spx, j + J0 + 0.5 - spy) < sp["exclusion_radius_m"] / S * 0.55:
                spaceport[j, i] = True
    # corridors: cells near elevated roads / rails / ramps / arterials stay free of buildings
    cl = A["clear"]
    corridor = np.zeros((N, N), bool)
    for r in roads:
        c = cl["ring" if r["cls"] == "ring" else r["cls"]] if r["cls"] in ("ring", "motorway", "truck", "arterial") else 0.0
        if c > 0:
            corridor |= raster(lines=[[tuple(p) for p in r["pts"]]], width_cells=2 * c + 0.6)
    for r in rails:
        c_ = cl["rail"] if r["kind"] == "freight" else cl["rail_light"]
        corridor |= raster(lines=[[tuple(p) for p in r["pts"]]], width_cells=2 * c_ + 0.4)
    for ix in inter:
        for rp in ix["ramps"]:
            corridor |= raster(lines=[[tuple(p) for p in rp]], width_cells=2 * cl["ramp"] + 0.4)
    # HQ lots (lots) and landmark footprints
    hq = {}
    for l in J["landmarks"]:
        if l["kind"] == "hq":
            hq[l["district"]] = list(lot(l["pos"]))
    hq["rebel_cell"] = list(lot(J["meta"].get("old_city_centre_m", [100.0, 600.0])))
    hq = {k: [round(v[0], 2), round(v[1], 2)] for k, v in hq.items()}
    LMK = [k for k in sorted(hq) if CP.LANDMARK_FP.get(k)]

    def in_fp(k, x, y, m_lots):
        dx, dy = (x - hq[k][0]) * CP.U, -(y - hq[k][1]) * CP.U
        return RU.in_footprint(k, dx, dy, m_lots * CP.U)

    # ------------------------------------------------------------------ cell classes
    # 0 water  1 drowned  2 corridor  3 park  4 plaza  5 cemetery  6 industry  7 informal  8 airport  9 port  10 spaceport
    # 11 district (built here)  12 suburb (built by the world)  13 outside the outer ring (sparse)
    r2 = next(r for r in roads if "Outer" in r["name"])
    r2_in = raster([[tuple(p) for p in r2["pts"]]])
    sd_in = dist_to(~r2_in)           # cells inside: distance to the outline
    sd_out = dist_to(r2_in)
    sd = np.where(r2_in, sd_in, -sd_out)
    nz = vnoise(None, 9.0, 4101) * 0.65 + vnoise(None, 3.5, 4102) * 0.35
    sd_n = sd + A["edge_noise"] * (nz * 2 - 1)
    sub_m = sd_n > 0
    core = dist_id > 0
    cls = np.full((N, N), 13, np.int8)
    cls[sub_m] = 12
    cls[core] = 11
    for m, v in ((spaceport, 10), (port_t, 9), (airport, 8), (informal, 7), (industry, 6), (cemetery, 5), (plazas, 4), (parks, 3),
                 (corridor, 2), (drowned, 1), (water, 0)):
        cls[m] = v
    # u: the urban factor (1 in the districts, sub_u in the suburbs, 0 beyond), soft
    u_core = box_blur(core.astype(np.float64), 3)
    u_sub = A["sub_u"] * smooth(sd_n, A["sub_edge"][0], A["sub_edge"][1])
    u = np.maximum(u_core, u_sub)
    u[wet_all] = np.maximum(u[wet_all], 0.0)
    np.savez_compressed(CP.A2_FIELDS, u=u.astype(np.float32), dist=dist_id, cls=cls, i0=I0, j0=J0, n=N, names=np.array(names))
    RU._FLD.clear()
    # ------------------------------------------------------------------ the sea bed (distance from the land)
    land = ~wet_all
    d_land = dist_to(land)
    # the drowned quarter: the ground subsides toward its middle (levee at the edge)
    d_edge = dist_to(~drowned)
    dmax = max(1.0, float(d_edge[drowned].max())) if drowned.any() else 1.0
    s0, s1 = CP.WATER["subside"]
    lagoon = []
    for j in range(N):
        for i in range(N):
            if drowned[j, i] and not (ocean[j, i]):
                lagoon.append([I0 + i, J0 + j, round(s0 + (s1 - s0) * min(1.0, d_edge[j, i] / dmax) ** 1.2, 2)])
    # ------------------------------------------------------------------ buildings in the districts (map style)
    rr = random.Random(CP.SEEDS["zoning"])
    hq_ab = {k: RU.ab(*hq[k]) for k in hq}
    arterial_polys = [[tuple(p) for p in r["pts"]] for r in roads if r["cls"] == "arterial"]
    out_b = []
    key = 100000
    centre_of = {}
    for d in J["districts"]:
        centre_of[CORP_OF.get(d["id"], d["id"])] = lot(d["centre"])
    dn = {k: names[k] for k in range(len(names))}
    wet_set = {(c[0], c[1]): c[2] for c in lagoon}
    per = A["core_period"]
    for j in range(N):
        for i in range(N):
            if cls[j, i] not in (11, 1):
                continue
            ci, cj = I0 + i, J0 + j
            wet = cls[j, i] == 1
            if not wet and (ci % per == per - 1 or cj % per == per - 1):
                continue                                           # a street line
            if wet and (ci % per == per - 1 or cj % per == per - 1):
                continue
            cx, cy = ci + 0.5, cj + 0.5
            if any(in_fp(k, cx, cy, CP.ZONING["fp_margin"]) for k in LMK):
                continue
            corp = dn[int(dist_id[j, i])] if dist_id[j, i] > 0 else "tethys"
            if cls[j, i] == 1:
                corp = "tethys"
            a_, b_ = RU.ab(cx, cy)
            uu = RU.urban_u(a_, b_)
            cen = centre_of.get(corp, (cx, cy))
            dc = math.hypot(cx - cen[0], cy - cen[1])
            gain = 1.0 + A["centre_gain"] * math.exp(-dc / A["centre_r"]) - 0.35
            med = A["bld_med"].get(corp, 30.0) * gain
            nsub = 2 if rr.random() < 0.9 else 1
            subs = [(0.0, 0.0), (0.5, 0.0), (0.0, 0.5), (0.5, 0.5)] if nsub == 2 else [(0.0, 0.0)]
            sz = 0.5 if nsub == 2 else 1.0
            for (ox, oy) in subs:
                if nsub == 2 and rr.random() < 0.08:
                    continue
                ins = rr.uniform(0.04, 0.10) if nsub == 2 else rr.uniform(0.08, 0.16)
                x0, x1 = ci + ox + ins, ci + ox + sz - ins
                y0, y1 = cj + oy + ins, cj + oy + sz - ins
                h = min(A["bld_max"], med * math.exp(rr.gauss(0.0, A["bld_sigma"])))
                if wet:
                    h = min(h, 120.0)
                key += 1
                b = dict(q=[[x0, y0], [x1, y0], [x1, y1], [x0, y1]], z0=0.0, h=round(h, 1), ts=1.0, ink=[0.5, 0.5, 0.5], terr=corp, ci=-1,
                         key=key, c=[(x0 + x1) / 2, (y0 + y1) / 2], sub=wet_set.get((ci, cj), 0.0) if wet else 0.0, wet=1 if wet else 0, crest=0,
                         u=round(uu, 3), art=0, border=0)
                out_b.append(b)
    # H2: the district of every non-drowned building by HQ influence (own polygon boosted), seeded per key
    for b in out_b:
        if b["wet"]:
            b["terr"] = "tethys"
            continue
        a_, b_ = RU.ab(*b["c"])
        w, w0 = RU.district_weights(a_, b_, hq_ab, max(b["u"], 0.05))
        b["terr"] = RU.draw_district(b["key"], w, w0)
        # border / arterial flags (the full crown trim and lane glow stay on arterials and district borders)
        i_, j_ = int(math.floor(b["c"][0])) - I0, int(math.floor(b["c"][1])) - J0
        if 1 <= i_ < N - 1 and 1 <= j_ < N - 1:
            nb = {int(dist_id[j_ + dj, i_ + di]) for di in (-1, 0, 1) for dj in (-1, 0, 1)}
            b["border"] = 1 if len(nb) > 1 else 0
        b["art"] = 1 if any(min(seg_d(b["c"], pl[k], pl[k + 1]) for k in range(len(pl) - 1)) < 1.2 for pl in arterial_polys[:0]) else 0
    # ------------------------------------------------------------------ export
    ports = dict(poly=[list(p) for p in lots(port["terminal_polygon"])], yard=[list(p) for p in lots(port["intermodal_yard"])],
                 terminus=list(lot(port["freight_rail_terminus"])), gate=list(lot(port["truck_gate"])),
                 piers=[dict(base=list(lot(p["base"])), length=p["length_m"] / S, width=p["width_m"] / S, bearing=p["bearing_deg"]) for p in port["piers"]])
    airp = dict(poly=[list(p) for p in lots(ap["polygon"])], runways=[dict(c=list(lot(r["centre"])), length=r["length_m"] / S, bearing=r["bearing_deg"]) for r in ap["runways"]],
                centre=list(lot(ap["centre"])))
    walls = {}
    for d in J["districts"]:
        if d.get("wall"):
            walls[CORP_OF.get(d["id"], d["id"])] = dict(pts=[list(p) for p in lots(d["wall"])], gates=[list(p) for p in lots(d.get("gates", []))])
    glyphs = [dict(kind=l["kind"].replace("glyph:", ""), name=l["name"], pos=list(lot(l["pos"]))) for l in J["landmarks"] if l["kind"] != "hq"]
    dams = [dict(name=d["name"], kind=d["kind"], pts=[list(p) for p in lots(d["polyline"])]) for d in J["defences"]["dams_and_barriers"]]
    swalls = [dict(name=d["name"], pts=[list(p) for p in lots(d["polyline"])]) for d in J["defences"]["sea_walls"]]
    O = dict(
        layout="a2", centre=[CX, CY], U=CP.U, KH=CP.KH, hq=hq, landmarks=LMK, buildings=out_b, tiles=[], plazas=[], arterials=[],
        lagoon_cells=lagoon, b_coast=0.0, b_split=0.0, lagoda_a=[0, 0], bay=dict(depth=0, width=1, ac=0, head_start=1, head_k=0), lagoon_a=[0, 0],
        clusters=[], terr_count={}, hq_old={}, aqueduct=[[0, 0], [1, 1]], corr_cells=[], fist=[], n_crest=0,
        a2=dict(grid=[I0, J0, N], roads=roads, rails=rails, stations=stations, interchanges=inter, port=ports, airport=airp, walls=walls,
                glyphs=glyphs, dams=dams, sea_walls=swalls, ocean=[list(p) for p in ocean_l], drowned=[list(p) for p in drowned_l],
                pier_city=dict(pos=list(lot(dq["pier_city"]["position"])), radius=dq["pier_city"]["radius_m"] / S),
                spaceport=dict(centre=[spx, spy], ring=sp["ring_radius_m"] / S, excl=sp["exclusion_radius_m"] / S, azimuth=sp["launch_azimuth_deg"]),
                markets=[dict(name=m["name"], pos=list(lot(m["position"]))) for m in J["markets"]],
                centres={k: list(v) for k, v in centre_of.items()}, d_land_max=float(d_land.max())),
    )
    O["terr_count"] = {k: sum(1 for b in out_b if b["terr"] == k) for k in sorted({b["terr"] for b in out_b})}
    os.makedirs(CP.SCR, exist_ok=True)
    json.dump(O, open(CP.ZONED, "w"))
    np.save(os.path.join(CP.SCR, "a2_dland.npy"), d_land.astype(np.float32))
    print("A2 buildings", len(out_b), O["terr_count"], "lagoon cells", len(lagoon))
    print("cells: land", int(land.sum()), "water", int(water.sum()), "drowned", int(drowned.sum()), "classes",
          {int(k): int((cls == k).sum()) for k in np.unique(cls)})
    print("hq", hq)
    return O, cls, dist_id, u


def draw_map(O, cls, dist_id, u, path):
    pal = {0: (10, 24, 60), 1: (20, 60, 140), 2: (60, 60, 64), 3: (30, 90, 40), 4: (120, 120, 110), 5: (50, 70, 50), 6: (90, 80, 70),
           7: (130, 70, 40), 8: (50, 50, 70), 9: (150, 110, 50), 10: (80, 40, 110), 11: (150, 120, 90), 12: (70, 70, 80), 13: (30, 30, 36)}
    Z = 5
    im = Image.new("RGB", (N * Z, N * Z), (0, 0, 0))
    px = im.load()
    for j in range(N):
        for i in range(N):
            c = pal[int(cls[j, i])]
            if cls[j, i] == 11:
                dc = {1: (200, 130, 80), 2: (190, 60, 90), 3: (50, 200, 150), 4: (130, 110, 230), 5: (255, 150, 30), 6: (190, 170, 100), 7: (60, 190, 160), 8: (90, 140, 255)}
                c = tuple(int(v * 0.6) for v in (150, 150, 150))
            for dy in range(Z):
                for dx in range(Z):
                    px[i * Z + dx, j * Z + dy] = c
    d = ImageDraw.Draw(im)

    def f(p):
        return ((p[0] - I0) * Z, (p[1] - J0) * Z)
    cols = {"ring": (255, 255, 255), "motorway": (255, 235, 160), "truck": (255, 150, 60), "arterial": (140, 140, 150), "collector": None}
    for r in O["a2"]["roads"]:
        c = cols.get(r["cls"])
        if c:
            d.line([f(p) for p in r["pts"]], fill=c, width=3 if r["cls"] in ("ring", "motorway") else 1)
    for ix in O["a2"]["interchanges"]:
        for rp in ix["ramps"]:
            d.line([f(p) for p in rp], fill=(120, 240, 255), width=1)
    for r in O["a2"]["rails"]:
        c = {"freight": (255, 120, 20), "commuter": (255, 80, 200), "metro": (80, 200, 255)}[r["kind"]]
        d.line([f(p) for p in r["pts"]], fill=c, width=1)
    for k, v in O["hq"].items():
        x, y = f(v)
        d.ellipse([x - 7, y - 7, x + 7, y + 7], outline=(255, 255, 255), width=2)
        d.text((x + 9, y - 5), k, fill=(255, 255, 255))
    for b in O["buildings"][::7]:
        x, y = f(b["c"])
        px[int(x), int(y)] = (255, 255, 255)
    im.save(path)


if __name__ == "__main__":
    O, cls, dist_id, u = main()
    draw_map(O, cls, dist_id, u, os.path.join(CP.SCR, "zoning_map_a2.png"))
