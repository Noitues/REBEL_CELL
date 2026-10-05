"""Round 24: HQ updates on the city map (round 6 restyled city, night view).

python city_hq_v2.py            -> ../city_night_hq_v2.png (2560 x 1440, same framing and labels as
                                   round6_city_restyle/views/restyle_night_full.png) and ../hq_updates.png
The game's exported layout (round6_city_restyle/city_layout.json, read-only) is edited in memory:
  - MERIDIAN: two ship-to-shore gantry cranes flank the Freight Ziggurat (its crest is a crane hook + container);
  - ORBITAL: a LAUNCH PAD on the tether platform: pad, rocket with nose cone and fins, service gantry with arms,
    exhaust steam; HQ neon moved to the round 17 ice-white palette;
  - HALCYON: the floating halo is removed and replaced by the EYE crest (amber almond, iris, pupil, glint, lashes);
  - SOLACE: the Double Helix already matches its helix crest; its neon is moved from mint to the round 17 lime;
  - REBEL_CELL: no tower; its fist-shaped roads already match the fist crest (unchanged).
New parts are inserted as the game's own primitive kinds right after each HQ's own primitives, so the round 6
restyler draws them in painter order with the same facets, toon bands, ink and neon.
"""
import colorsys
import copy
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "city_r6"))
OUT = os.path.dirname(HERE)
SRC = os.path.join(OUT, "..", "round6_city_restyle")

from PIL import Image, ImageDraw, ImageFont
import lowpoly
import views as V
from restyle import View, labels

CTX = {"solace": 3855, "meridian": 4138, "orbital": 6795, "halcyon": 7237}
TA, TB = 34.0, 17.0
HQK = 2.0
LIME = (0.588, 1.0, 0.275, 1.0)
ICE = (0.80, 0.94, 1.0, 1.0)
CYAN = (0.36, 0.88, 1.0, 1.0)
AMBER = (1.0, 0.72, 0.22, 1.0)
ORANGE = (1.0, 0.55, 0.10, 1.0)
DARK = (0.078, 0.106, 0.173, 1.0)
INKD = (0.05, 0.04, 0.06, 1.0)


class City:
    def __init__(self, data):
        self.d = data
        self.ox, self.oy = data["camera"]
        self.rects = {c["terr"]: c["rect"] for c in data["contexts"] if c["kind"] == "hq"}
        self.new = {k: [] for k in CTX}

    def iso(self, x, y, z=0.0):
        return [self.ox + (x - y) * TA, self.oy + (x + y) * TB - z]

    def centre(self, corp):
        r = self.rects[corp]
        return r[0] + 5.0, r[1] + 5.0

    # primitives in the export's own format
    def ext(self, corp, pts, z0, h, ts=1.0, ink=None, key=990, lit=0.25):
        b = []
        for (x, y) in pts:
            b += self.iso(x, y)
        self.new[corp].append({"b": b, "ctx": CTX[corp], "fill": list(DARK), "h": h, "ink": list(ink or ORANGE),
                               "key": key, "lit": lit, "t": "ext", "ts": ts, "z0": z0})

    def box(self, corp, x0, y0, x1, y1, z0, h, **kw):
        self.ext(corp, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, h, **kw)

    def ngon(self, corp, cx, cy, r, n, z0, h, ts=1.0, rot=0.0, **kw):
        self.ext(corp, [(cx + r * math.cos(rot + 2 * math.pi * i / n), cy + r * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)], z0, h, ts, **kw)

    def ink(self, corp, p0, p1, col, w=1.4):
        a, b = self.iso(*p0), self.iso(*p1)
        self.new[corp].append({"c": [list(col)], "ctx": CTX[corp], "glow": True, "p": a + b, "t": "ink", "w": w})

    def inks(self, corp, pts, col, w=1.4):
        for p, q in zip(pts, pts[1:]):
            self.ink(corp, p, q, col, w)

    def poly_screen(self, corp, pts, col):
        flat = []
        for p in pts:
            flat += [p[0], p[1]]
        self.new[corp].append({"c": [list(col)], "ctx": CTX[corp], "p": flat, "t": "poly"})

    def ink_screen(self, corp, a, b, col, w):
        self.new[corp].append({"c": [list(col)], "ctx": CTX[corp], "glow": True, "p": [a[0], a[1], b[0], b[1]], "t": "ink", "w": w})

    # ------------------------------------------------------------------ MERIDIAN: cranes
    def meridian(self):
        cx, cy = self.centre("meridian")
        k = HQK
        for side in (0, 1):
            # crane straddling the front-left (+y) edge, or the front-right (+x) edge
            def L(u, v):  # u along the edge, v outward from the ziggurat
                return (cx + u, cy + 4.3 + v) if side == 0 else (cx + 4.3 + v, cy + u)
            u0 = -3.4 if side == 0 else -0.4
            legs = [(u0, 0.0), (u0 + 3.0, 0.0), (u0, 2.6), (u0 + 3.0, 2.6)]
            top = 420.0
            for (u, v) in legs:
                x, y = L(u, v)
                self.box("meridian", x - 0.28, y - 0.28, x + 0.28, y + 0.28, 0.0, top, ink=ORANGE, key=990)
            # portal beam + the boom (long, out over the yard and back over the ziggurat)
            ua, ub = u0 - 0.3, u0 + 3.3
            xa, ya = L(ua, -0.3)
            xb, yb = L(ub, 2.9)
            self.box("meridian", min(xa, xb), min(ya, yb), max(xa, xb), max(ya, yb), top, 22.0, ink=ORANGE, key=991)
            um = u0 + 1.5
            p0, p1 = L(um - 0.45, -6.0), L(um + 0.45, 9.0)
            self.box("meridian", min(p0[0], p1[0]), min(p0[1], p1[1]), max(p0[0], p1[0]), max(p0[1], p1[1]), top + 22, 18.0, ink=ORANGE, key=992)
            # hazard stripes along the boom
            n = 20
            for i in range(n):
                a, b = L(um - 0.47, -6.0 + 15.0 * i / n), L(um - 0.47, -6.0 + 15.0 * (i + 0.5) / n)
                self.ink("meridian", (a[0], a[1], top + 31), (b[0], b[1], top + 31), ORANGE if i % 2 == 0 else INKD, 6.0)
            # apex + tie rods (the A-frame)
            ap = L(um, 1.3)
            self.ink("meridian", (ap[0], ap[1], top + 40), (ap[0], ap[1], top + 170), ORANGE, 4.0)
            for v in (-5.6, 8.6):
                q = L(um, v)
                self.ink("meridian", (ap[0], ap[1], top + 170), (q[0], q[1], top + 40), (0.95, 0.68, 0.39, 0.95), 2.2)
            # trolley + cables + a hanging container out over the yard
            tq = L(um, 6.4)
            self.ink("meridian", (tq[0], tq[1], top + 22), (tq[0], tq[1], 190), (0.6, 0.6, 0.66, 0.9), 1.6)
            c0, c1 = L(um - 1.4, 5.9), L(um + 1.4, 6.9)
            self.box("meridian", min(c0[0], c1[0]), min(c0[1], c1[1]), max(c0[0], c1[0]), max(c0[1], c1[1]), 140, 50,
                     ink=[(0.2, 0.5, 1.0, 1.0), (0.9, 0.2, 0.15, 1.0)][side], key=993)
            # red beacons at the boom tips
            for v in (-6.0, 9.0):
                q = L(um, v)
                self.ink("meridian", (q[0], q[1], top + 40), (q[0], q[1], top + 48), (1.0, 0.15, 0.12, 1.0), 6.0)

    # ------------------------------------------------------------------ ORBITAL: launch pad
    def orbital(self):
        cx, cy = self.centre("orbital")
        k = HQK
        z = 22.0 * k
        rx, ry = cx - 2.0, cy + 2.4  # rocket on the front-left of the tether platform
        self.ngon("orbital", rx, ry, 1.5, 10, z, 10, ink=CYAN, key=995)
        for i in range(10):  # pad ring lights
            a = 2 * math.pi * i / 10
            self.ink("orbital", (rx + 1.6 * math.cos(a), ry + 1.6 * math.sin(a), z + 10), (rx + 1.6 * math.cos(a + 0.3), ry + 1.6 * math.sin(a + 0.3), z + 10), CYAN, 3.5)
        # service gantry (behind-left of the rocket) with two swing arms
        gx, gy = rx - 1.7, ry - 1.4
        self.box("orbital", gx - 0.5, gy - 0.5, gx + 0.5, gy + 0.5, z + 10, 600, ink=ICE, key=996)
        for zz in range(int(z + 40), int(z + 600), 40):
            a, b = self.iso(gx - 0.52, gy + 0.52, zz), self.iso(gx + 0.52, gy + 0.52, zz + 34)
            self.ink_screen("orbital", a, b, (0.80, 0.94, 1.0, 0.8), 1.6)
        for za in (z + 300, z + 470):
            self.ink("orbital", (gx + 0.5, gy + 0.5, za), (rx - 0.7, ry - 0.5, za), ICE, 4.0)
        self.ink("orbital", (gx, gy, z + 610), (gx, gy, z + 622), (1.0, 0.15, 0.12, 1.0), 6.0)
        # the rocket: booster, upper stage, nose cone, fins, ring bands
        self.ngon("orbital", rx, ry, 0.95, 12, z + 10, 400, ts=0.97, ink=ICE, key=997)
        self.ngon("orbital", rx, ry, 0.92, 12, z + 410, 120, ts=0.9, ink=ICE, key=998)
        self.ngon("orbital", rx, ry, 0.83, 12, z + 530, 110, ts=0.04, ink=CYAN, key=999)
        for zz in (z + 90, z + 410, z + 526):
            pts = [(rx + 1.0 * math.cos(math.pi * 0.25 + math.pi * i / 8), ry + 1.0 * math.sin(math.pi * 0.25 + math.pi * i / 8), zz) for i in range(9)]
            self.inks("orbital", pts, CYAN, 4.0)
        for a in (math.pi * 0.25, math.pi * 0.75):  # fins (screen-space triangles at the base)
            p = self.iso(rx + 0.95 * math.cos(a), ry + 0.95 * math.sin(a), z + 14)
            q = self.iso(rx + 1.9 * math.cos(a), ry + 1.9 * math.sin(a), z + 10)
            t = self.iso(rx + 0.95 * math.cos(a), ry + 0.95 * math.sin(a), z + 140)
            self.poly_screen("orbital", [p, q, t], (0.70, 0.86, 1.0, 1.0))
        # steam / exhaust clouds round the pad (translucent)
        for i, (dx, dy, r) in enumerate(((-2.2, 0.8, 70), (1.6, 1.8, 60), (0.2, 2.5, 84), (-0.8, -1.8, 50))):
            c = self.iso(rx + dx, ry + dy, z + 10)
            pts = [(c[0] + r * math.cos(2 * math.pi * j / 10) * (1 + 0.2 * ((j * 7 + i) % 3)), c[1] - r * 0.45 + r * 0.45 * math.sin(2 * math.pi * j / 10)) for j in range(10)]
            self.poly_screen("orbital", pts, (0.86, 0.92, 1.0, 0.22))

    # ------------------------------------------------------------------ HALCYON: eye crest
    def halcyon(self):
        prims = self.d["prims"]
        ci = CTX["halcyon"]
        self.d["prims"] = [p for p in prims if not (p.get("ctx") == ci and p["t"] == "ink" and abs(p.get("w", 0) - 1.8) < 1e-3)]
        base = next(c["base"] for c in self.d["contexts"] if c["kind"] == "hq" and c["terr"] == "halcyon")
        k = HQK
        ex, ey = base[0], base[1] - 190.0 * k - 190.0
        R, hgt = 150.0, 86.0

        def almond(sx, sy):
            up = [(ex + R * sx * math.cos(math.pi * (1 - t / 24)), ey - hgt * sy * math.sin(math.pi * t / 24)) for t in range(25)]
            lo = [(ex + R * sx * math.cos(math.pi * t / 24), ey + hgt * sy * math.sin(math.pi * t / 24)) for t in range(1, 24)]
            return up + lo
        self.poly_screen("halcyon", almond(1.0, 1.0), (0.10, 0.06, 0.20, 1.0))  # dark eye socket
        ring = almond(1.0, 1.0)
        for p, q in zip(ring, ring[1:] + ring[:1]):  # lids as a thick amber line, not a filled blob
            self.ink_screen("halcyon", p, q, AMBER, 7.0)
        iris = [(ex + 52 * math.cos(2 * math.pi * j / 20), ey + 52 * math.sin(2 * math.pi * j / 20)) for j in range(20)]
        self.poly_screen("halcyon", iris, (0.92, 0.60, 0.14, 1.0))
        pupil = [(ex + 22 * math.cos(2 * math.pi * j / 16), ey + 22 * math.sin(2 * math.pi * j / 16)) for j in range(16)]
        self.poly_screen("halcyon", pupil, (0.06, 0.03, 0.10, 1.0))
        gl = [(ex + 17 + 9 * math.cos(2 * math.pi * j / 10), ey - 19 + 9 * math.sin(2 * math.pi * j / 10)) for j in range(10)]
        self.poly_screen("halcyon", gl, (1.0, 0.96, 0.88, 1.0))
        for j in range(-2, 3):  # lashes / rays
            a = math.radians(-90 + j * 26)
            x0, y0 = ex + (R - 4) * math.cos(a) * 0.95, ey + (hgt + 4) * math.sin(a)
            self.ink_screen("halcyon", (x0, y0), (x0 + 46 * math.cos(a), y0 + 46 * math.sin(a)), AMBER, 6.0)
        for p in self.d["prims"]:  # lift the HALCYON roof sign clear of the eye
            if p["t"] == "sign" and p.get("ctx") == ci:
                p["p"] = [p["p"][0], ey - hgt - 90]
        # mast from the apex up to the eye
        self.ink_screen("halcyon", (base[0], base[1] - 190.0 * k), (base[0], ey + hgt), (0.642, 0.632, 1.0, 0.9), 2.0)

    # ------------------------------------------------------------------ palette: Solace lime, Orbital ice
    def recolor(self, corp, target, sat_min=0.3):
        th, _, _ = colorsys.rgb_to_hls(*target[:3])
        for p in self.d["prims"]:
            if p.get("ctx") != CTX[corp]:
                continue
            for key in ("c", "ink"):
                if key not in p:
                    continue
                cols = p[key] if key == "c" else [p[key]]
                out = []
                for c in cols:
                    h, l, s = colorsys.rgb_to_hls(*c[:3])
                    if s > sat_min and l > 0.35:
                        r, g, b = colorsys.hls_to_rgb(th, max(l, 0.55), min(1.0, s * 1.1))
                        c = [r, g, b, c[3]]
                    out.append(c)
                if key == "c":
                    p["c"] = out
                else:
                    p["ink"] = out[0]
        terr = next(t for t in self.d["territories"] if t["id"] == corp)
        for b in self.d["beacons"]:
            if abs(b["p"][0] - terr["screen"][0]) < 260 and abs(b["p"][1] - terr["screen"][1]) < 900:
                b["col"] = list(target)

    def apply(self):
        self.meridian()
        self.orbital()
        self.halcyon()
        self.recolor("solace", LIME)
        self.recolor("orbital", ICE, sat_min=0.25)
        prims = self.d["prims"]
        for corp in sorted(CTX, key=lambda c: -max(i for i, p in enumerate(prims) if p.get("ctx") == CTX[c])):
            last = max(i for i, p in enumerate(prims) if p.get("ctx") == CTX[corp] and p["t"] != "sign")
            prims[last + 1:last + 1] = self.new[corp]
        return self.d


def render_full(data, path):
    V.set_theme("night")
    vw = data["view"]
    full = View(0, 0, vw["zoom"], vw["w"], vw["h"])
    lowpoly.W, lowpoly.H = full.w, full.h
    img = V.ViewRestyler(data, full, "night", False).render()
    img = labels(img, data, full)
    img = img.resize((2560, 1440), Image.LANCZOS)
    img.save(path, optimize=True)
    return img


def hq_sheet(before, after, data):
    k = 2560 / data["view"]["w"] * data["view"]["zoom"]
    terr = {t["id"]: t for t in data["territories"]}
    rows = [("meridian", "MERIDIAN  -  Freight Ziggurat gains two ship-to-shore CRANES (crest: crane hook + container)", (40, -150), 400),
            ("orbital", "ORBITAL  -  Tether platform adds a LAUNCH PAD: rocket, service gantry, steam; ice-white neon", (-40, -180), 400),
            ("halcyon", "HALCYON  -  the halo is replaced by the EYE crest (amber almond, iris, lashes)", (0, -200), 400),
            ("solace", "SOLACE  -  Double Helix already matches the helix crest; neon moved to round 17 lime", (0, -250), 400),
            ("rebel_cell", "REBEL_CELL  -  no tower: the fist-shaped roads match the fist crest (unchanged)", (0, -120), 400)]
    tile = 440
    W = 40 + 2 * (tile + 20) + 20
    H = 70 + len(rows) * (tile + 60)
    sh = Image.new("RGB", (W * 2 // 2, H), (14, 13, 20))
    d = ImageDraw.Draw(sh)
    f1 = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 34)
    f2 = ImageFont.truetype("C:/Windows/Fonts/bahnschrift.ttf", 17)
    d.text((20, 18), "HQ UPDATES  -  before (round 6)  |  after (round 24)", font=f1, fill=(240, 236, 226))
    for i, (corp, cap, off, size) in enumerate(rows):
        t = terr[corp]
        cx, cy = t["screen"][0] * k + off[0], t["screen"][1] * k + off[1]
        box = (int(cx - size / 2), int(cy - size / 2), int(cx + size / 2), int(cy + size / 2))
        y = 70 + i * (tile + 60)
        d.text((20, y), cap, font=f2, fill=(220, 216, 206))
        for j, im in enumerate((before, after)):
            c = im.crop(box).resize((tile, tile), Image.LANCZOS)
            sh.paste(c, (20 + j * (tile + 20), y + 26))
            d.text((26 + j * (tile + 20), y + 30), ("BEFORE", "AFTER")[j], font=f2, fill=(255, 214, 64))
    sh.save(os.path.join(OUT, "hq_updates.png"), optimize=True)


if __name__ == "__main__":
    data = json.load(open(os.path.join(SRC, "city_layout.json")))
    orig = copy.deepcopy(data)
    data = City(data).apply()
    after = render_full(data, os.path.join(OUT, "city_night_hq_v2.png"))
    print("wrote city_night_hq_v2.png", flush=True)
    before = Image.open(os.path.join(SRC, "views", "restyle_night_full.png")).convert("RGB")
    hq_sheet(before, after, orig)
    print("wrote hq_updates.png", flush=True)
