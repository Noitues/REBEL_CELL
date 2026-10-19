"""Solace THE BLOOM, street netrun light form: S_clean, S_creep, S_close, S_catch, S_caught_strip (1920 x 1080).

2D compositing over the street_r2 DECISION plate (read only). The Bloom is a WORLD-SPACE field: the plate's Z pass and
the camera in anchors_F_dec_closed.json (street_r2 render_s1, D:/rc_scratch) give every pixel a world x (the street
axis) and height, so the front advances along the street in route-layer units and the fingers follow the facades.
No new render. Run:  python solace_street.py [all|S_creep,...]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw

import solace_lib as L

R2 = os.path.join(L.REPO, "docs", "concepts", "route_map_graph", "street_r2")
SBS = os.path.join(L.REPO, "docs", "concepts", "route_map_graph", "storyboard", "scripts")
RENDER = "D:/rc_scratch/street_r2/render_s1"
W, H = 1920, 1080

# route layer -> world x of the layer's column (measured from the plate's depth pass; L0..L7), extrapolated 19 BU/layer
LX = [132.7, 113.7, 101.9, 87.0, 82.2, 80.4, 73.7, 66.0]
OP_LAYER, OP_ROOM = 1, "L1_1"           # the mock operative (current room); the DECISION camera is unchanged
WALKED = ["L0_0", "L1_1"]

# BLOOM states. gap = layers from the front to the operative. CLOSE <= 2.0, CATCHING <= 1.0 (provisional rules).
STATES = {
    "S_clean": None,
    "S_creep": dict(state="CREEPING", gap=3.0, tend=44.0, tend_h=9.0, vein=0.55, band=0.0, wash=0.0, front_chip=False),
    "S_close": dict(state="CLOSE", gap=1.6, tend=24.0, tend_h=6.0, vein=0.8, band=0.55, wash=0.0, front_chip=True),
    "S_catch": dict(state="CATCHING", gap=0.7, tend=15.0, tend_h=4.5, vein=1.0, band=1.0, wash=1.0, front_chip=True),
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
        R, C = M[:3, :3], M[:3, 3]
        z = np.load(os.path.join(RENDER, "F_dec_closed_z.npy"))[..., 0]
        f, s, sh = self.A["lens"], self.A["sensor"], self.A["shift"]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        xn = (xx / W - 0.5 + sh[0]) * s / f
        yn = -((yy - H / 2 + sh[1] * W) / W) * s / f
        v = np.stack([xn * z, yn * z, -z], -1)
        P = C[None, None, :] + v @ R.T
        self.valid = z < 140.0
        P = np.where(self.valid[..., None], P, 0.0)
        self.wx, self.wy, self.wz = [L.boxblur(P[..., i], 3) for i in range(3)]   # tame the Z pass noise
        self.plate = np.asarray(Image.open(os.path.join(R2, "plates", "02_DECISION_closed_s1_plate.png")).convert("RGB"),
                                np.float32) / 255.0
        self.rooms = self.A["rooms"]
        self.edges = self.A["edges"]

    def room_layer(self, rid):
        return int(rid[1:].split("_")[0])

    def visible_rooms(self):
        out = {}
        for k, v in self.rooms.items():
            q = v["front"]
            cx = sum(p[0] for p in q) / 4
            cy = sum(p[1] for p in q) / 4
            if 60 < cx < W - 20 and 150 < cy < 1000:
                out[k] = q
        return out

    def link_mask(self):
        im = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(im)
        for e in self.edges:
            pts = [tuple(p) for p in e["pts"]]
            d.line(pts, fill=255, width=22)
        return L.blur(np.asarray(im, np.float32) / 255.0, 3.0)


def bloom_field(sc, front_layer, tend_bu=15.0, tend_h=4.5, seed=7):
    """Returns cover (0..1), edge hairline (0..1), depth-behind-front in BU."""
    fx = layer_x(front_layer)
    ground = sc.wz < 0.7
    fing = 7.5 * (L.fbm(sc.wz * 0.5, sc.wy * 0.08, seed, 3) - 0.35) + 3.5 * (L.fbm(sc.wz * 1.7, sc.wx * 0.05, seed + 5, 2) - 0.5)
    local = fx + 1.1 * np.clip(sc.wz, 0, 14) - fing
    tn = L.fbm(sc.wy * 0.35, sc.wz * 0.9, seed + 3, 3)                # tendrils crawl low, ahead of the wash
    tend = tend_bu * L.smoothstep(0.42, 0.58, tn) * (1 - L.smoothstep(0.4, tend_h, sc.wz))
    local = local - tend
    d = sc.wx - local                                   # BU behind the (local) front
    cover = L.smoothstep(-0.04, 0.14, d) * sc.valid
    edge = np.exp(-((d - 0.02) / 0.07) ** 2) * (d > -0.2) * sc.valid
    return cover, edge, d


def veins(sc, d, vein_k, seed=7):
    g = sc.wz < 0.7
    u = np.where(g, sc.wx * 0.30, sc.wx * 0.20 + sc.wy * 0.04)
    v = np.where(g, sc.wy * 0.55, sc.wz * 0.55)
    out = 0.0
    for k, (sc_u, sc_v, wgt) in enumerate(((1.0, 1.0, 1.0), (1.9, 1.7, 0.7))):
        n = L.fbm(u * sc_u, v * sc_v, seed + 31 * k, 4)
        gy, gx = np.gradient(n)
        gr = np.sqrt(gx * gx + gy * gy) + 1e-4
        dist = np.abs(n - 0.5) / gr                     # pixels from the contour
        ln = np.clip(1.0 - dist / 0.9, 0, 1)
        dens = L.fbm(u * 0.35 + 9, v * 0.35 + 3, seed + 77 + k, 2)
        keep = L.smoothstep(0.52 - 0.28 * vein_k, 0.66 - 0.2 * vein_k, dens)
        out = np.maximum(out, ln * keep * wgt)
    out = out * (0.45 + 0.55 * L.smoothstep(0.0, 9.0, d))     # sparse near the front, denser deeper in
    return out


def apply_bloom(sc, st, keepm):
    P = sc.plate.copy()
    f = OP_LAYER - st["gap"]
    cover, edge, d = bloom_field(sc, f, st["tend"], st["tend_h"])
    cover = cover * (1 - keepm)
    edge = edge * (1 - keepm)
    Lm = L.luma(P)
    pn = (L.PINK / 0.4518)[None, None, :]
    plum_n = (L.PLUM / 0.0830)[None, None, :]
    t = np.clip(Lm / 0.5, 0, 1) ** 0.8
    body = plum_n * (0.040 + 0.030 * t)[..., None]
    bright = L.smoothstep(0.42, 0.7, Lm)
    win = pn * np.minimum(0.22 * Lm, 0.14)[..., None]
    infected = body * (1 - bright[..., None]) + win * bright[..., None]
    hat = L.hatch(H, W) * L.smoothstep(0.0, 3.0, d)          # 45 degree hatch: reads without the hue
    infected = infected + (hat * 0.35 * 0.06)[..., None] * pn
    vn = veins(sc, d, st["vein"]) * (1 - keepm)
    infected = np.minimum(infected + (vn * 0.66)[..., None] * L.PINK[None, None, :], 1.0)
    out = P * (1 - cover[..., None]) + infected * cover[..., None]
    out = out + (edge * 0.75)[..., None] * L.PINK[None, None, :]
    yy = np.arange(H, dtype=np.float32)[:, None] / H
    if st["band"] > 0:                                       # the bottom-edge band, 6 % of the frame
        bh = 0.06
        band = L.smoothstep(1 - bh - 0.004, 1.0, yy) * st["band"] * np.ones((1, W), np.float32)
        line = np.exp(-((yy - (1 - bh)) / 0.0012) ** 2) * st["band"] * np.ones((1, W), np.float32)
        out = out * (1 - 0.55 * band[..., None]) + 0.55 * band[..., None] * (L.PLUM[None, None, :] * 0.5)
        out = out + (line * 0.55)[..., None] * L.PINK[None, None, :]
    if st["wash"] > 0:                                       # CATCHING: plum fills the lower third, veins climb
        w3 = L.smoothstep(0.62, 1.0, yy) * st["wash"] * np.ones((1, W), np.float32)
        n = L.fbm(np.arange(W)[None, :] * 0.012, yy * 9.0, 41, 3)
        w3 = np.clip(w3 * (0.55 + 0.9 * n), 0, 1) * (1 - keepm)
        out = out * (1 - 0.6 * w3[..., None]) + 0.6 * w3[..., None] * (L.PLUM[None, None, :] * 0.55)
        sy = np.arange(H, dtype=np.float32)[:, None] * np.ones((1, W), np.float32)
        v2 = L.fbm(np.arange(W)[None, :] * 0.02, sy * 0.012, 61, 4)
        gy, gx = np.gradient(v2)
        ln = np.clip(1.3 - np.abs(v2 - 0.5) / (np.sqrt(gx * gx + gy * gy) + 1e-4), 0, 1)
        ln = ln * L.smoothstep(0.66, 0.9, yy) * st["wash"] * (1 - keepm)
        out = out + (ln * 0.66)[..., None] * L.PINK[None, None, :]
    out = np.clip(out, 0, 1)
    # the value rule: the frame median stays within +-0.01 of the clean frame. The Bloom body is dark, so the exposure of
    # the clean part lifts a little (bisected gain on the uncovered pixels, never over 1.6).
    target = L.luma(P).__array__()
    tm = float(np.median(L.luma(sc.plate)))
    lo, hi = 1.0, 1.6
    unc = (1 - cover)[..., None]
    dim = (1 - L.smoothstep(0.4, 0.8, L.luma(P)))[..., None]
    def med(g):
        return float(np.median(L.luma(np.clip(out * (1 + (g - 1) * unc * dim), 0, 1))))
    if med(1.0) < tm - 0.004:
        for _ in range(8):
            mid = (lo + hi) / 2
            if med(mid) < tm - 0.002:
                lo = mid
            else:
                hi = mid
        out = np.clip(out * (1 + (hi - 1) * unc * dim), 0, 1)
    return out, f


def keep_masks(sc):
    vis = sc.visible_rooms()
    km = L.poly_mask(H, W, list(vis.values()), grow=0.10, feather=2.5)
    km = np.maximum(km, sc.link_mask())
    return km, vis


def route_layer(sc, vis, f_layer, st):
    """Mock route marks (links, room frames, token) and the Bloom chips, on a supersampled RGBA layer."""
    S = L.SS
    lay = L.canvas((W, H))
    d = ImageDraw.Draw(lay)
    walked_pairs = {(WALKED[i], WALKED[i + 1]) for i in range(len(WALKED) - 1)}
    for e in sc.edges:
        a, b = e["a"], e["b"]
        if a not in sc.rooms or b not in sc.rooms:
            continue
        pts = [tuple(p) for p in e["pts"]]
        if (a, b) in walked_pairs:
            d.line([(x * S, y * S) for x, y in pts], fill=(150, 255, 70, 255), width=5 * S, joint="curve")
        else:
            seg = [(x * S, y * S) for x, y in pts]
            for i in range(len(seg) - 1):
                x0, y0 = seg[i]
                x1, y1 = seg[i + 1]
                n = max(1, int(np.hypot(x1 - x0, y1 - y0) / (14 * S)))
                for k in range(n):
                    t0, t1 = k / n, (k + 0.55) / n
                    d.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0), (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)],
                           fill=(235, 235, 245, 210), width=3 * S)
    infected = {rid: (f_layer is not None) and (sc.room_layer(rid) <= f_layer) for rid in vis}
    for rid, q in vis.items():
        poly = [(x * S, y * S) for x, y in q]
        if infected[rid]:
            d.polygon(poly, fill=(36, 16, 28, 150))            # plum wash behind the room
        col, w = (235, 235, 245, 200), 2
        if rid in WALKED:
            col, w = (150, 255, 70, 255), 3
        if rid == OP_ROOM:
            col, w = (150, 255, 70, 255), 5
        d.line(poly + [poly[0]], fill=col, width=w * S, joint="curve")
        if infected[rid]:                                      # pink hairline on the outer edge of the frame only
            cx = sum(p[0] for p in q) / 4
            cy = sum(p[1] for p in q) / 4
            o = [(((x - cx) * 1.035 + cx) * S, ((y - cy) * 1.035 + cy) * S) for x, y in q]
            d.line(o + [o[0]], fill=L.PINK8 + (255,), width=int(1.4 * S))
    q = vis.get(OP_ROOM)
    if q:
        cx = sum(p[0] for p in q) / 4
        cy = sum(p[1] for p in q) / 4
        r = 22
        d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=(12, 20, 24, 255), outline=(150, 255, 70, 255), width=4 * S)
        d.ellipse([(cx - 6) * S, (cy - 6) * S, (cx + 6) * S, (cy + 6) * S], fill=(150, 255, 70, 255))
    if st:
        done = set()
        for rid, q in sorted(vis.items()):
            if infected[rid]:
                n = sc.room_layer(rid)
                if n in done:
                    continue
                done.add(n)
                L.chip(d, min(p[0] for p in q) + 4, min(p[1] for p in q) - 15, "INFECTED", L.PINK8, 13)
        if st["front_chip"]:
            n = int(np.floor(f_layer)) + 1
            cands = sorted(k for k in vis if sc.room_layer(k) == n)
            if cands:
                q = vis[cands[len(cands) // 2]]
                L.chip(d, min(p[0] for p in q) + 4, min(p[1] for p in q) - 15, "FRONT -%.1f" % st["gap"], L.PINK8, 14)
    return lay


def gauge_layer(st, f_layer):
    """Vertical BLOOM gauge on the right screen edge: ticks = route layers, marker = operative, plum fill to the front."""
    S = L.SS
    lay = L.canvas((W, H))
    d = ImageDraw.Draw(lay)
    x, y0, y1, w = 1876, 150, 990, 13
    top, bot = 7.6, -2.6

    def Y(v):
        return y1 - (v - bot) / (top - bot) * (y1 - y0)
    d.rectangle([(x - w / 2) * S, y0 * S, (x + w / 2) * S, y1 * S], fill=(10, 6, 14, 200), outline=(120, 90, 110, 200), width=S)
    fy = Y(f_layer)
    d.rectangle([(x - w / 2 + 1) * S, fy * S, (x + w / 2 - 1) * S, (y1 - 1) * S], fill=(46, 18, 36, 255))
    for yy in range(int(fy), y1, 6):                         # 45 degree hatch in the fill
        d.line([((x - w / 2 + 1) * S, yy * S), ((x + w / 2 - 1) * S, (yy - 6) * S)], fill=(160, 60, 105, 140), width=S)
    d.line([((x - w / 2 - 5) * S, fy * S), ((x + w / 2 + 5) * S, fy * S)], fill=L.PINK8 + (255,), width=2 * S)
    for n in range(0, 8):
        yy = Y(n)
        d.line([((x - w / 2 - 7) * S, yy * S), ((x - w / 2) * S, yy * S)], fill=(215, 215, 225, 230), width=S)
        d.text(((x - w / 2 - 10) * S, yy * S), "L%d" % n, font=L.font(11 * S), fill=(200, 200, 212, 220), anchor="rm")
    oy = Y(OP_LAYER)
    d.polygon([((x + w / 2 + 3) * S, oy * S), ((x + w / 2 + 12) * S, (oy - 6) * S), ((x + w / 2 + 12) * S, (oy + 6) * S)], fill=(150, 255, 70, 255))
    L.spore(d, x, y0 - 22, 10, L.PINK8 + (255,), w=1.8)
    d.text((x * S, (y0 - 42) * S), "BLOOM", font=L.font(14 * S), fill=L.PINK8 + (255,), anchor="mm")
    L.chip(d, x - 46, fy, "%s  -%.1f" % (st["state"], st["gap"]), L.PINK8, 12, glyph=False, anchor="rm")
    return lay


def chrome(img01):
    sys.path.insert(0, R2 + "/scripts")
    sys.path.insert(1, SBS)
    import sb_reveal as RV
    import sb_ui as U
    import sb_cams as SB
    A = json.load(open(os.path.join(RENDER, "anchors_F_dec_closed.json")))
    im = Image.fromarray((np.clip(img01, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    ui = RV.route_chrome(im, A, 0.0, 1.0)
    return U.title(ui.convert("RGB"), SB.T["b6"] - 0.1)


def caught(img, vis, k, fade):
    """CAUGHT one-shot: the current room's window floods pink-white (k 0..1), then goes black (fade 0..1)."""
    q = vis[OP_ROOM]
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in q], fill=255)
    a = np.asarray(m, np.float32) / 255.0
    glow = L.blur(a, 40) * k
    core = L.blur(a, 1.5) * k
    out = img + glow[..., None] * L.PINK[None, None, :] * 0.9
    out = out * (1 - core[..., None]) + core[..., None] * L.WHITE_PINK[None, None, :]
    if fade > 0:
        out = out * (1 - fade * 0.92)
        out = out * (1 - (L.blur(a, 1.5) * fade)[..., None])
    return np.clip(out, 0, 1)


def finish(sc, name, flood_k=0.0, fade=0.0):
    st = STATES[name]
    f = None if st is None else OP_LAYER - st["gap"]
    km, vis = keep_masks(sc)
    P = sc.plate.copy() if st is None else apply_bloom(sc, st, km)[0]
    mt = L.metrics(P)
    img = L.flatten(P, route_layer(sc, vis, f, st))
    ui = np.asarray(chrome(img), np.float32) / 255.0
    if flood_k > 0 or fade > 0:
        ui = caught(ui, vis, flood_k, fade)
    if st:
        ui = L.flatten(ui, gauge_layer(st, f))
    return ui, mt


def main(which):
    sc = Scene()
    res = {}
    for name in STATES:
        if which != "all" and name not in which:
            continue
        img, mt = finish(sc, name)
        L.save_png(img, os.path.join(L.OUT, name + ".png"))
        res[name] = dict(plate=mt, still=L.metrics(img))
        print(name, res[name], flush=True)
    if which == "all" or "S_caught_strip" in which:
        spec = [(0, 0.0, 0.0), (8, 0.45, 0.0), (16, 1.0, 0.0), (23, 1.0, 1.0)]
        sheet = Image.new("RGB", (1920, 1080))
        d = ImageDraw.Draw(sheet)
        for i, (fr, k, fade) in enumerate(spec):
            img, _ = finish(sc, "S_catch", flood_k=k, fade=fade)
            fim = Image.fromarray((img * 255 + 0.5).astype(np.uint8)).resize((960, 540), Image.LANCZOS)
            sheet.paste(fim, ((i % 2) * 960, (i // 2) * 540))
            d.text(((i % 2) * 960 + 12, (i // 2) * 540 + 520), "CAUGHT  f%02d" % fr, font=L.font(16), fill=(255, 70, 150), anchor="lm")
        sheet.save(os.path.join(L.OUT, "S_caught_strip.png"))
        res["S_caught_strip"] = "frames 0/8/16/23 as a 2x2 of 960x540"
    os.makedirs(L.SCRATCH, exist_ok=True)
    json.dump(res, open(os.path.join(L.SCRATCH, "street_values_%s.json" % ("all" if which == "all" else "part")), "w"), indent=1)


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "all"
    main(a if a == "all" else a.split(","))
