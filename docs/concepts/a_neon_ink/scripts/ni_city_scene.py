"""Builds the inked city as a stack of depth-band planes (shared by stills 01-03)."""
import math, random
from ni_lib import *
from ni_parts import *

HQ = (2.45, 14.05)


def band_of(y, bands):
    for i, (lim, _) in enumerate(bands):
        if y < lim:
            return i
    return len(bands) - 1


def make_city(seed=11, mode="night", bands=None, detail=1.0, u=34.0, ox=960, oy=540, hq=HQ, highways=True,
              cables=True, prefix="city", fade_far=True):
    pal = {"night": PAL_NIGHT, "desat": PAL_DESAT, "heat": PAL_HEAT}[mode]
    bands = bands or [(120, 7.0), (260, 4.5), (400, 2.0), (960, 0.0), (99999, 5.0)]
    city = City(seed, u=u, ox=ox, oy=oy, hq=hq, extent=46)
    planes = []
    ground = Plane(prefix + "_ground", ("bg", "streets"), blur=1.5)
    planes.append(ground)
    fill_poly(ground, "bg", rect(-10, -10, W + 20, H + 20), "#05070D" if mode != "heat" else "#07050A", 1.0)
    # ground grid hairlines + marker-stroke streets (pink, loose)
    r = random.Random(seed + 1)
    for k in range(-34, 36, 5):
        s = k - 0.5
        for (a, b) in ((city.P(s, -40), city.P(s, 40)), (city.P(-40, s), city.P(40, s))):
            ink(ground, "streets", [a, b], pal["line"], 0.8, 0.18, None, 0)
        if mode == "night" and r.random() < 0.35:
            a, b = city.P(s, -40), city.P(s, 40)
            ink(ground, "streets", [a, b], "pink", 3.5, 0.18, city.hand, 1.5, taper=0.4)
    bplanes = []
    for i, (lim, bl) in enumerate(bands):
        p = Plane("%s_b%d" % (prefix, i), ("ink", "fx", "traffic", "cables"), blur=bl)
        if fade_far:
            p.opacity = [0.55, 0.72, 0.9, 1.0, 1.0][min(i, 4)]
        bplanes.append(p)
    for b in city.buildings:
        y = city.depth_y(b)
        bi = band_of(y, bands)
        det = detail * (0.55 if bi == 0 else 1.0)
        city.draw_building(bplanes[bi], b, pal, det)
    if highways:
        city.add_highway([(-40, 5.5), (-10, 5.5), (30, 5.5)], 1.5, 1.1, seed=1)
        city.add_highway([(0.5, -40), (0.5, -6), (1.5, -1), (5.5, 1.2), (12, 0.7), (40, 0.5)], 3.0, 1.2, seed=2)
        city.add_highway([(-40, -4.5), (-8, -4.5), (-2, -6), (6, -9.5), (10.5, -14), (10.5, -40)], 4.6, 1.3, seed=3,
                         color_hi="#CFF6FF", color_tail="#FF3DA8")
        city.add_highway([(20.5, -40), (20.5, 40)], 2.2, 1.0, seed=4)
        city.add_highway([(-40, 25.5), (8, 25.5), (12, 23), (15.5, 18), (15.5, -40)], 3.6, 1.2, seed=5, color_hi="#CFF6FF", color_tail="#FF3DA8")
        for hw in city.highways:
            if mode == "desat":
                hw["hi"], hw["tail"] = "#6A7888", "#6A5060"
            gp = city.highway_runs(hw)
            run = []; cur_b = None
            for g in gp:
                sy = city.P(g[0], g[1])[1]
                sx = city.P(g[0], g[1])[0]
                if sx < -200 or sx > W + 200 or sy < -300 or sy > H + 400:
                    if run:
                        city.draw_highway_segment(bplanes[cur_b], hw, run, pal, detail); run = []
                    continue
                bi = band_of(sy, bands)
                if cur_b is not None and bi != cur_b and run:
                    city.draw_highway_segment(bplanes[cur_b], hw, run + [g], pal, detail)
                    run = []
                cur_b = bi; run.append(g)
            if run:
                city.draw_highway_segment(bplanes[cur_b], hw, run, pal, detail)
    if cables:
        # pink cables strung between roofs across streets (the Cell's wiring)
        rr = random.Random(seed + 5)
        bl = [b for b in city.buildings if b["kind"] == "bld"]
        for _ in range(int(40 * detail)):
            a = rr.choice(bl)
            cands = [b for b in bl if 0.8 < abs((b["x"] - a["x"])) + abs(b["y"] - a["y"]) < 4.5]
            if not cands:
                continue
            b = rr.choice(cands)
            pa, pb = city.roof_point(a, rr.random(), rr.random()), city.roof_point(b, rr.random(), rr.random())
            bi = band_of(max(city.depth_y(a), city.depth_y(b)), bands)
            city.cable(bplanes[bi], "cables", pa, pb, rr.uniform(10, 40), "pink" if mode != "desat" else "#5A4660",
                       rr.choice([0.9, 1.3, 2.0]), 0.85, city.hand)
        if hq:
            hqb = [b for b in city.buildings if b["kind"] == "hq"][0]
            bi = band_of(city.depth_y(hqb), bands)
            near = sorted(bl, key=lambda b: abs(b["x"] - hqb["x"]) + abs(b["y"] - hqb["y"]))[:9]
            for j, b in enumerate(near):
                pa = city.P(hqb["x"] + hqb["w"] * (0.2 + 0.1 * j), hqb["y"] + hqb["d"], hqb["h"] * rr.uniform(0.5, 0.95))
                pb = city.roof_point(b, 0.5, 0.5)
                city.cable(bplanes[bi], "cables", pa, pb, rr.uniform(20, 60), "pink", rr.choice([1.2, 2.2]), 0.9, city.hand)
    planes += bplanes
    return city, planes, pal


def fog_planes(seed, patches, prefix="fog", color="#9AB8E0"):
    """Patchy fog: blobs on three planes with different blur (near = softest)."""
    r = random.Random(seed)
    out = []
    for name, blur, op in (("far", 6, 0.06), ("mid", 16, 0.05), ("near", 40, 0.09)):
        p = Plane("%s_%s" % (prefix, name), ("fog",), blur=blur, glow=True)
        for (x, y, rx, ry) in patches.get(name, []):
            for k in range(5):
                fill_poly(p, "fog", ellipse(x + r.uniform(-rx * .4, rx * .4), y + r.uniform(-ry * .3, ry * .3),
                                            rx * r.uniform(.4, .8), ry * r.uniform(.4, .8), 28), color, op)
        out.append(p)
    return out


def flyers(city, pl, seed, n=14, mode="night"):
    r = random.Random(seed); hand = city.hand
    for i in range(n):
        gx, gy = r.uniform(-12, 22), r.uniform(-12, 22)
        z = r.uniform(5.5, 10)
        x, y = city.P(gx, gy, z)
        if not (40 < x < W - 40 and 40 < y < H - 40):
            continue
        ang = r.choice([0.46, -0.46, math.pi + 0.46, math.pi - 0.46])
        L = r.uniform(80, 220)
        tx, ty = x - math.cos(ang) * L, y - math.sin(ang) * L
        c1 = r.choice(["cyan", "pink", "#FFFFFF", "amber"]) if mode != "heat" else r.choice(["harm", "#FFFFFF", "amber"])
        ink(pl, "trail", [(tx, ty), (x, y)], c1, 3.0, 0.5, None, 0, w_profile=lambda t: 0.2 + 0.8 * t)
        ink(pl, "trail", [(tx, ty), (x, y)], "#FFFFFF", 0.8, 0.5, None, 0, w_profile=lambda t: t)
        # body: small inked wedge (car) with a shadow line down to its height
        body = rot_pts([(x - 14, y - 5), (x + 12, y - 4), (x + 16, y), (x + 12, y + 4), (x - 14, y + 5)], x, y, ang)
        fill_poly(pl, "body", body, "#0B1020", 1.0)
        ink(pl, "body", body, c1, 1.6, 1, hand, 0.2, closed=True)
        fill_poly(pl, "body", ellipse(*rot_pts([(x + 15, y)], x, y, ang)[0], 3, 3, 8), "#FFFFFF", 1)
        gx2, gy2 = city.P(gx, gy, 0)
        ink(pl, "trail", [(x, y + 8), (gx2, gy2)], c1, 0.6, 0.12, None, 0)


def holo(city, pl, b, seed, w=120, h=70, col_a="violet", col_b="cyan", side="left", z_off=1.4):
    """Projected hologram billboard: a projector on the roof, a light cone, and a
    floating quad with illegible type."""
    r = random.Random(seed); hand = Hand(seed)
    P = city.P
    base = P(b["x"] + b["w"] * .5, b["y"] + b["d"], b["h"])
    # the quad floats beside the building, sheared to the iso face
    cx, cy = base[0] + (-1 if side == "left" else 1) * (w * 0.55), base[1] - z_off * city.u
    sh = 0.5 if side == "left" else -0.5
    quad = [(cx - w / 2, cy - h / 2 - sh * w / 2 * 0.577), (cx + w / 2, cy - h / 2 + sh * w / 2 * 0.577),
            (cx + w / 2, cy + h / 2 + sh * w / 2 * 0.577), (cx - w / 2, cy + h / 2 - sh * w / 2 * 0.577)]
    fill_poly(pl, "beam", [base, quad[2], quad[3]], col_a, 0.10)
    fill_poly(pl, "beam", [base, quad[0], quad[1]], col_a, 0.06)
    ink(pl, "beam", [base, quad[0]], col_a, 0.8, 0.5, None, 0)
    ink(pl, "beam", [base, quad[3]], col_a, 0.8, 0.5, None, 0)
    fill_poly(pl, "holo", quad, col_a, 0.20)
    ink(pl, "holo", quad, col_b, 1.6, 0.95, hand, 0.4, closed=True)
    # scanlines
    for i in range(1, 9):
        t = i / 9
        a = (quad[0][0] + (quad[3][0] - quad[0][0]) * t, quad[0][1] + (quad[3][1] - quad[0][1]) * t)
        bb = (quad[1][0] + (quad[2][0] - quad[1][0]) * t, quad[1][1] + (quad[2][1] - quad[1][1]) * t)
        ink(pl, "holo", [a, bb], col_b, 0.6, 0.25, None, 0)
    # a logo mark + illegible copy
    lx, ly = quad[0][0] + w * .22, (quad[0][1] + quad[3][1]) / 2
    k = r.randint(0, 2)
    if k == 0:
        ink(pl, "holo", ellipse(lx, ly, h * .25, h * .25, 20), "#FFFFFF", 2.2, 1, hand, .3, closed=True)
    elif k == 1:
        ink(pl, "holo", [(lx - h * .25, ly + h * .2), (lx, ly - h * .25), (lx + h * .25, ly + h * .2)], "#FFFFFF", 2.2, 1, hand, .3, closed=True)
    else:
        ink(pl, "holo", [(lx - h * .2, ly - h * .2), (lx + h * .2, ly + h * .2)], "#FFFFFF", 2.4, 1, hand, .3)
        ink(pl, "holo", [(lx + h * .2, ly - h * .2), (lx - h * .2, ly + h * .2)], "#FFFFFF", 2.4, 1, hand, .3)
    tx = quad[0][0] + w * .45
    ty = (quad[0][1] + quad[1][1]) / 2 + h * .22
    for li in range(3):
        scribble_text(pl, "holo", tx, ty + li * h * 0.2 + sh * 4, w * 0.48, h * 0.1, "#FFFFFF" if li == 0 else col_b, hand,
                      0.9, 1.1 if li == 0 else 0.8)
    return quad


def grid_overlay(city, pl, seed, hq=HQ, mode="night", nodes=None, links=None):
    """Raid grid: nodes and links drawn ON the ground plane (same plane, no risers)."""
    P = city.P; hand = Hand(seed)
    ptxt = {}
    def node_pt(n):
        return nodes[n]
    for (a, b, kind) in links:
        (ax, ay), (bx, by) = nodes[a], nodes[b]
        # route along the street grid: L-shaped on the plane
        mid = (bx, ay)
        pts = [P(ax, ay), P(*mid), P(bx, by)]
        ink(pl, "under", pts, "#000000", 11, 0.75, None, 0, taper=0)
        if kind == "claimed":
            ink(pl, "link", pts, "acid", 4.0, 1, hand, 0.5, taper=0.8)
        elif kind == "threat":
            ink(pl, "link", pts, "orange" if mode != "heat" else "harm", 2.6, 1, hand, 0.4, taper=0.8)
            # chevrons along it
            for seg in ((pts[0], pts[1]), (pts[1], pts[2])):
                (x0, y0), (x1, y1) = seg
                dl = math.hypot(x1 - x0, y1 - y0)
                if dl < 30:
                    continue
                ux, uy = (x1 - x0) / dl, (y1 - y0) / dl
                for t in range(1, int(dl / 44)):
                    cx, cy = x0 + ux * t * 44, y0 + uy * t * 44
                    ink(pl, "link", [(cx - ux * 8 - uy * 7, cy - uy * 8 + ux * 7), (cx, cy), (cx - ux * 8 + uy * 7, cy - uy * 8 - ux * 7)],
                        "orange" if mode != "heat" else "harm", 2.0, 1, None, 0)
        else:
            ink(pl, "link", pts, "cyan", 1.8, 0.9, hand, 0.4, taper=0.8)
            for t in range(0, 12):
                pass
    for name, (gx, gy) in nodes.items():
        x, y = P(gx, gy)
        big = name == "HQ"
        rx, ry = (city.u * 1.0, city.u * 0.5) if big else (city.u * 0.62, city.u * 0.31)
        fill_poly(pl, "under", ellipse(x, y, rx * 1.25, ry * 1.25, 30), "#000000", 0.7)
        colr = "pink" if big else ("acid" if name.startswith("C") else ("orange" if name.startswith("T") else "cyan"))
        if mode == "heat" and name.startswith("T"):
            colr = "harm"
        ink(pl, "node", ellipse(x, y, rx, ry, 36), colr, 3.2, 1, hand, 0.5, closed=True)
        ink(pl, "node", ellipse(x, y, rx * 0.66, ry * 0.66, 30), colr, 1.2, 0.8, hand, 0.4, closed=True)
        fill_poly(pl, "node", [(x - rx * .3, y), (x, y - ry * .3), (x + rx * .3, y), (x, y + ry * .3)], colr, 0.9)
        # corner brackets on the plane (targetable)
        if big:
            for sx in (-1, 1):
                ink(pl, "node", [(x + sx * rx * 1.5, y - ry * .5), (x + sx * rx * 1.5, y), (x + sx * rx * 1.25, y + ry * 0.4)], colr, 2.2, 1, hand, .3)
    return


def glass_panel(pl, x, y, w, h, title, hand, accent="pink", op=0.88):
    fill_poly(pl, "panel", rect(x, y, w, h), "#050D1C", op)
    ink(pl, "panel", rect(x, y, w, h), "cyan", 1.4, 0.8, hand, 0.4, closed=True)
    ink(pl, "panel", [(x + 14, y + 40), (x + w - 14, y + 40)], accent, 2.0, 1, hand, 0.5, taper=0.6)
    # scanlines
    for yy in range(int(y) + 4, int(y + h), 6):
        ink(pl, "scan", [(x + 2, yy), (x + w - 2, yy)], "#5CE1FF", 0.5, 0.05, None, 0, taper=0)
    pl.text(title, x + 16, y + 30, 20, "cyan", FONT_MONO)
