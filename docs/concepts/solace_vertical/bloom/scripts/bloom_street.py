"""Solace THE BLOOM v2, street netrun frames: {A,B,C}_street.png (1920 x 1080), CLOSE band, plus the gauge-strip source frames.

World-space composite over the golden street DECISION plate (a Cycles AAA-2 render; its Z pass and camera in
D:/rc_scratch/street_r2/render_s1 give every pixel a world x (street axis), y and height, so the front advances along the
street in route-layer units and the skin follows the facades). Overlays (route marks, TIDE gauge, red dashed forecast) in PIL.
Run:  python bloom_street.py [A,B,C] [CLOSE,CATCHING]
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw

import solace_lib as L
import bloom_skins as S
import bloom_gauge as G

RENDER = "D:/rc_scratch/street_r2/render_s1"
PLATE = "D:/rc_art/art-pass/docs/concepts/golden_plates/street_decision.png"
W, H = 1920, 1080
LX = [132.7, 113.7, 101.9, 87.0, 82.2, 80.4, 73.7, 66.0]      # world x of route layers L0..L7 (measured from the depth pass)
OP_LAYER, OP_ROOM = 1, "L1_1"
WALKED = ["L0_0", "L1_1"]
PACE_NODE = 0.715                                              # layers (spec example: T3, Heat NOTICED 110 %); display only
GAPS = {"CLOSE": 1.25, "CATCHING": 0.7}

PARAMS = {
    "A": dict(fq=0.55, zT=3.0, zM=9.0, seed=7, hpitch=9, vgain=0.85, ew=1.5, vw=1.3, keep_lo=0.45),
    "B": dict(fq=0.5, zT=1.6, zM=3.5, zC=4.5, cap=2.0, seed=7, tw=1.8, matv=0.30, matw=1.6, capp=0.7, gamma=1.3, lump=4.0, fibv=0.85),
    "C": dict(fq=0.45, zT=1.2, zM=6.0, bub=3.0, seed=7, rip=60.0, alpha=0.9, see=0.7, spec=0.5, seen=0.6, cau=0.0),
}


def layer_x(f):
    if f >= 0:
        i = min(int(np.floor(f)), len(LX) - 2)
        t = f - i
        return LX[i] + (LX[i + 1] - LX[i]) * t
    return LX[0] - 19.0 * f


class Scene:
    def __init__(self):
        self.A = json.load(open(os.path.join(RENDER, "anchors_F_dec_closed.json")))
        M = np.array(self.A["cam_world"])
        self.R, self.C = M[:3, :3], M[:3, 3]
        z = np.load(os.path.join(RENDER, "F_dec_closed_z.npy"))[..., 0]
        f, s, sh = self.A["lens"], self.A["sensor"], self.A["shift"]
        self.f, self.s, self.sh = f, s, sh
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        xn = (xx / W - 0.5 + sh[0]) * s / f
        yn = -((yy - H / 2 + sh[1] * W) / W) * s / f
        v = np.stack([xn * z, yn * z, -z], -1)
        P = self.C[None, None, :] + v @ self.R.T
        self.valid = z < 140.0
        P = np.where(self.valid[..., None], P, 0.0)
        self.wx, self.wy, self.wz = [L.boxblur(P[..., i], 3) for i in range(3)]
        self.sx, self.sy, self.sz = [L.boxblur(P[..., i], 9, 3) for i in range(3)]      # smoother texture coordinates
        self.plate = np.asarray(Image.open(PLATE).convert("RGB"), np.float32) / 255.0
        self.rooms, self.edges = self.A["rooms"], self.A["edges"]

    def proj(self, p):
        v = self.R.T @ (np.array(p, np.float64) - self.C)
        z = -v[2]
        xn, yn = v[0] / z, v[1] / z
        x = (xn * self.f / self.s - self.sh[0] + 0.5) * W
        y = -yn * self.f / self.s * W - self.sh[1] * W + H / 2
        return float(x), float(y)

    def room_layer(self, rid):
        return int(rid[1:].split("_")[0])

    def visible_rooms(self):
        out = {}
        for k, v in self.rooms.items():
            q = v["front"]
            cx, cy = sum(p[0] for p in q) / 4, sum(p[1] for p in q) / 4
            if 60 < cx < W - 20 and 150 < cy < 1000:
                out[k] = q
        return out

    def link_mask(self):
        im = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(im)
        for e in self.edges:
            d.line([tuple(p) for p in e["pts"]], fill=255, width=22)
        return L.blur(np.asarray(im, np.float32) / 255.0, 3)


def fields(sc, front_layer, tend=24.0, tend_h=6.0, seed=7):
    """d = BU behind the (ragged) front; u, v = texture coordinates in BU (facade: x, height; ground: x, y)."""
    fx = layer_x(front_layer)
    fing = 7.5 * (L.fbm(sc.sz * 0.5, sc.sy * 0.08, seed, 3) - 0.35) + 3.5 * (L.fbm(sc.sz * 1.7, sc.sx * 0.05, seed + 5, 2) - 0.5)
    local = fx + 1.1 * np.clip(sc.sz, 0, 14) - fing
    tn = L.fbm(sc.sy * 0.35, sc.sz * 0.9, seed + 3, 3)
    local = local - tend * S.SM(0.42, 0.58, tn) * (1 - S.SM(0.4, tend_h, sc.sz))
    d = sc.sx - local
    ground = sc.wz < 0.7
    u = sc.sx
    v = np.where(ground, sc.sy, sc.sz)
    return d, u, v


def keep_masks(sc):
    vis = sc.visible_rooms()
    km = L.poly_mask(H, W, list(vis.values()), grow=0.10, feather=2.5)
    return np.maximum(km, sc.link_mask()), vis


def route_layer(sc, vis, f_layer):
    """Route marks (links, room frames, token) on a supersampled RGBA layer. No text UI (build owns the FRONT chip)."""
    SSn = L.SS
    lay = L.canvas((W, H))
    d = ImageDraw.Draw(lay)
    walked_pairs = {(WALKED[i], WALKED[i + 1]) for i in range(len(WALKED) - 1)}
    for e in sc.edges:
        a, b = e["a"], e["b"]
        if a not in sc.rooms or b not in sc.rooms:
            continue
        pts = [tuple(p) for p in e["pts"]]
        if (a, b) in walked_pairs:
            d.line([(x * SSn, y * SSn) for x, y in pts], fill=(150, 255, 70, 255), width=5 * SSn, joint="curve")
        else:
            seg = [(x * SSn, y * SSn) for x, y in pts]
            for i in range(len(seg) - 1):
                x0, y0 = seg[i]
                x1, y1 = seg[i + 1]
                n = max(1, int(np.hypot(x1 - x0, y1 - y0) / (14 * SSn)))
                for k in range(n):
                    t0, t1 = k / n, (k + 0.55) / n
                    d.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0), (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)], fill=(235, 235, 245, 210), width=3 * SSn)
    for rid, q in vis.items():
        poly = [(x * SSn, y * SSn) for x, y in q]
        col, w = (235, 235, 245, 200), 2
        if rid in WALKED:
            col, w = (150, 255, 70, 255), 3
        if rid == OP_ROOM:
            col, w = (150, 255, 70, 255), 5
        d.line(poly + [poly[0]], fill=col, width=w * SSn, joint="curve")
    q = vis.get(OP_ROOM)
    if q:
        cx, cy = sum(p[0] for p in q) / 4, sum(p[1] for p in q) / 4
        r = 22
        d.ellipse([(cx - r) * SSn, (cy - r) * SSn, (cx + r) * SSn, (cy + r) * SSn], fill=(12, 20, 24, 255), outline=(150, 255, 70, 255), width=4 * SSn)
        d.ellipse([(cx - 6) * SSn, (cy - 6) * SSn, (cx + 6) * SSn, (cy + 6) * SSn], fill=(150, 255, 70, 255))
    return lay


def pencil_layer(sc, f_pred):
    """Red grease-pencil dashed forecast: where the front lands if the next node is entered (a wobbly dashed line across the
    street at the predicted front, climbing the far facade), placed with the street's world projection."""
    SSn = L.SS
    lay = L.canvas((W, H))
    d = ImageDraw.Draw(lay)
    fx = layer_x(f_pred)
    ys = np.linspace(-4, 26, 14)
    ground = [sc.proj((fx, y, 0.3)) for y in ys]
    wall = [sc.proj((fx + 1.1 * z, 24.0, z)) for z in np.linspace(0.3, 7.0, 6)]
    for pts, sd in ((ground, 4), (wall, 9)):
        pts = [p for p in pts if -50 < p[0] < W + 50 and -50 < p[1] < H + 50]
        if len(pts) > 1:
            G.wobble_line(d, pts, G.RED8 + (255,), 4.2, dash=(18, 11), seed=sd, amp=2.2)
    return lay


def render(sc, kind, band, with_ui=True, forecast=True, gauge_band=None, gauge=True):
    gap = GAPS[band]
    f = OP_LAYER - gap
    d, u, v = fields(sc, f)
    km, vis = keep_masks(sc)
    P = sc.plate
    cover = S.SM(-0.05, 0.15, d) * sc.valid * (1 - km)
    out = S.SKINS[kind](P, cover, d, u, v, dict(PARAMS[kind]))
    out, gain = S.lift_median(P, out, cover)
    mt = dict(plate=L.metrics(P), plate_bloom=L.metrics(out), gain=round(float(gain), 3))
    if not with_ui:
        return out, mt, f, vis
    img = L.flatten(out, route_layer(sc, vis, f))
    if forecast:
        img = L.flatten(img, pencil_layer(sc, f + PACE_NODE))
    gimg = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    if gauge:
        gb = gauge_band or band
        gg = G.tide_gauge(kind, gb, gap=GAPS.get(gb), w=170, h=600, forecast_gap=gap - PACE_NODE if (forecast and gb == band) else None)
        gimg.alpha_composite(gg, (W - 170 - 24, 96))
    return np.asarray(gimg.convert("RGB"), np.float32) / 255.0, mt, f, vis


def main(kinds, bands):
    sc = Scene()
    res = {}
    os.makedirs(L.SCRATCH + "/out", exist_ok=True)
    for k in kinds:
        for b in bands:
            t0 = time.time()
            img, mt, f, vis = render(sc, k, b)
            name = "%s_street" % k if b == "CLOSE" else "%s_street_%s" % (k, b.lower())
            dst = os.path.join(L.OUT if b == "CLOSE" else L.SCRATCH + "/out", name + ".png")
            L.save_png(img, dst)
            mt["still"] = L.metrics(img)
            mt["seconds"] = round(time.time() - t0, 1)
            res["%s_%s" % (k, b)] = mt
            print(k, b, mt, flush=True)
    json.dump(res, open(os.path.join(L.SCRATCH, "street_values_%s.json" % "".join(kinds)), "w"), indent=1)


if __name__ == "__main__":
    kinds = (sys.argv[1] if len(sys.argv) > 1 else "A,B,C").split(",")
    bands = (sys.argv[2] if len(sys.argv) > 2 else "CLOSE").split(",")
    main(kinds, bands)
