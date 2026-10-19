"""Solace THE BLOOM, HQ full form: H_bloom_overview (1920 x 1080).

Over the Solace v4 HQ OVERVIEW plate (hq_solace/plates/H_overview_v4_plate.png, read only). The Bloom is a skin layer
in TUBE coordinates: the v4 strand geometry (hq_graph.tube_pt) is re-projected with the OVERVIEW pose, front-facing
quads are painted far to near into a (z, phi, tower) buffer, and every pixel then decodes to its height and angle round
its strand. One number, the front floor coordinate, sets the same height on both towers; the tongues are functions of
phi only, so they run along the strand, i.e. they follow the helix. Node windows and the UP stair keep a keep-out.
Then the v4 route chrome is composed on top (hq_compose.compose), then the BLOOM gauge and chips.
Run (from this folder):  python solace_hq.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw

import solace_lib as L

HQS = os.path.join(L.REPO, "docs", "concepts", "route_map_graph", "hq_solace")
sys.path.insert(0, os.path.join(HQS, "scripts"))
import hq_graph as G          # noqa: E402
import hq_compose as C        # noqa: E402
import hq_overlay as O        # noqa: E402

PW, PH = 2560, 1440
K = PW / 1920.0
WALKED = ["start", "A1", "A2", "B2", "B3", "B4", "B5", "B6"]
FRONT_LAYER = 4.0              # the Bloom reaches route layer 4 (floor 12)
OP_LAYER = 6                   # the operative is on B6, so the gap is 2.0 (CLOSE, provisional rule: <= 2.0)
Z_TOP = 5.0 + 27 * 12.5


def front_z(layer):
    """World height of the front for a (float) route layer: the window of layer 1 is floor 3 ... 8 is floor 24."""
    RF = G.RF
    if layer <= 1:
        f = RF[0] + (layer - 1) * 3.0
    else:
        i = min(int(math.floor(layer)) - 1, len(RF) - 2)
        t = layer - 1 - i
        f = RF[i] + (RF[i + 1] - RF[i]) * t
    return G.win_z(f) + 6.0


def paint_buffer(pose, zmax, dz=0.5, dphi=2.5):
    """(z16, phi8, tower) buffer of the front-facing strand skin, far to near. RGBA image at PW x PH."""
    cam = np.array(pose.loc(), np.float64)
    quads = []
    nphi = int(round(360.0 / dphi))
    zs = np.arange(G.PODIUM_H, zmax, dz)
    for ti, t in enumerate(("A", "B")):
        for z in zs:
            for k in range(nphi):
                p0, p1 = math.radians(k * dphi), math.radians((k + 1) * dphi)
                pm = (p0 + p1) / 2
                c, rv, n = G.tower_frame(t, (z + dz / 2 - G.PODIUM_H) / G.FH)
                tx = (n[1], -n[0])
                nrm = np.array([n[0] * math.cos(pm) + tx[0] * math.sin(pm), n[1] * math.cos(pm) + tx[1] * math.sin(pm), 0.0])
                P = np.array(G.tube_pt(t, z + dz / 2, pm))
                if np.dot(nrm, cam - P) <= 0:
                    continue
                quads.append((float(np.linalg.norm(cam - P)), t, ti, z, p0, p1, dz))
    quads.sort(key=lambda q: -q[0])
    img = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for dist, t, ti, z, p0, p1, dzq in quads:
        pts = [G.tube_pt(t, z, p0), G.tube_pt(t, z, p1), G.tube_pt(t, z + dzq, p1), G.tube_pt(t, z + dzq, p0)]
        q = [pose.proj(p) for p in pts]
        if any(v is None for v in q):
            continue
        zc = z + dzq / 2
        zi = int(zc / 400.0 * 65535)
        pc = ((p0 + p1) / 2) % (2 * math.pi)
        d.polygon([(v[0] * K, v[1] * K) for v in q], fill=(zi >> 8, zi & 255, int(pc / (2 * math.pi) * 255), 255 if ti == 0 else 128))
    return img


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def skin_fields(buf):
    a = np.asarray(buf)
    ten = a[..., 3]
    mask = ten > 0
    z = ((a[..., 0].astype(np.int32) << 8) | a[..., 1]).astype(np.float32) / 65535.0 * 400.0
    phi = a[..., 2].astype(np.float32) / 255.0 * 2 * np.pi
    tow = np.where(ten == 255, 0, 1)
    return mask, z, phi, tow


def tongues(phi, z, tow, z0, seed=11):
    """Front height per pixel: a spiral swell plus tongues that are functions of phi (they run along the strand)."""
    s = phi * G.RT
    ph0 = np.where(tow == 0, 0.0, math.pi)
    swell = 4.5 * np.cos(phi - ph0 - 0.6)
    tg = L.fbm(s * 0.22 + tow * 17.0, np.zeros_like(s) + 3.0, seed, 3)
    tongue = 17.0 * L.smoothstep(0.42, 0.72, tg)
    ragged = 2.2 * (L.fbm(z * 0.45, s * 0.9, seed + 4, 3) - 0.5)
    return z0 + swell + tongue + ragged


def veins(phi, z, tow, d, seed=5):
    """Veins: contours of noise stretched along the strand, drifting with the twist. Width ~0.4 BU."""
    s = phi * G.RT + tow * 31.0
    def n(sv, zv):
        return L.fbm(sv * 0.30 + zv * 0.006, zv * 0.035, seed, 4)
    e = 0.25
    n0 = n(s, z)
    gs = (n(s + e, z) - n(s - e, z)) / (2 * e)
    gz = (n(s, z + e) - n(s, z - e)) / (2 * e)
    dist = np.abs(n0 - 0.5) / (np.sqrt(gs * gs + gz * gz) + 1e-3)           # BU from the contour
    line = np.clip(1.0 - dist / 0.45, 0, 1)
    dens = L.fbm(s * 0.08, z * 0.02, seed + 9, 2)
    keep = L.smoothstep(0.38, 0.55, dens)
    return line * keep * (0.5 + 0.5 * L.smoothstep(0.0, 25.0, d))


def keepout(phi, z):
    """Strand-space keep-out: the inward node windows of the route floors (+12 %) and the UP stair band."""
    k = np.zeros_like(z)
    for t, ti in (("A", 0), ("B", 1)):
        pass
    return k


def bloom_plate(plate, pose):
    P = np.asarray(plate, np.float32) / 255.0
    z0 = front_z(FRONT_LAYER)
    buf = paint_buffer(pose, z0 + 90.0)
    mask, z, phi, tow = skin_fields(buf)
    ys, xs = np.where(mask)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    sl = (slice(y0, y1), slice(x0, x1))
    m, zc, pc, tw = mask[sl], z[sl], phi[sl], tow[sl]
    zf = tongues(pc, zc, tw, z0)
    d = zf - zc                                           # BU below the local front (positive = infected)
    kp = np.zeros_like(zc)
    for ti, t in enumerate(("A", "B")):
        sel = (tw == ti)
        pin, pst = G.phi_in(t), G.stair_phi(t)
        dph = np.abs((pc - pin + np.pi) % (2 * np.pi) - np.pi)
        dpst = np.abs((pc - pst + np.pi) % (2 * np.pi) - np.pi)
        win = np.zeros_like(zc)
        for f in G.RF:
            zw = G.win_z(f)
            win = np.maximum(win, (np.abs(zc - zw) < G.WB * 1.25 + 0.6) & (dph < math.radians(70 * 1.12)))
        stair = dpst < (1.5 + 0.8) / G.RT
        kp = np.where(sel, np.maximum(win, stair.astype(np.float32)), kp)
    kp = L.blur(kp.astype(np.float32), 1.2)
    cover = m * L.smoothstep(-0.2, 0.6, d) * (1 - kp)
    edge = m * np.exp(-((d - 0.1) / 0.28) ** 2) * (d > -0.8) * (1 - kp)
    sub = P[sl]
    Lm = L.luma(sub)
    pn = (L.PINK / 0.4518)[None, None, :]
    plum_n = (L.PLUM / 0.0830)[None, None, :]
    t = np.clip(Lm / 0.6, 0, 1) ** 0.8
    body = plum_n * (0.050 + 0.020 * t)[..., None]
    # windows / lit pixels: green-white -> pink-dim near the front, darker deeper in
    bright = L.smoothstep(0.30, 0.60, Lm)
    deep = L.smoothstep(2.0, 70.0, d)
    win = pn * (np.minimum(0.55 * Lm, 0.42) * (1 - 0.5 * deep))[..., None]
    inf = body * (1 - bright[..., None]) + win * bright[..., None]
    hat = L.hatch(y1 - y0, x1 - x0, 7, 2) * L.smoothstep(1.0, 6.0, d)
    inf = inf + (hat * 0.05)[..., None] * pn * 0.5
    vn = veins(pc, zc, tw, d) * (1 - kp) * m
    inf = np.minimum(inf + (vn * 0.95)[..., None] * L.PINK[None, None, :], 1.0)
    out = sub * (1 - cover[..., None]) + inf * cover[..., None]
    out = out + (edge * 0.9)[..., None] * L.PINK[None, None, :] * 0.95
    full = P.copy()
    full[sl] = np.clip(out, 0, 1)
    # plinth: the source. Planter edge lights green -> pink on the podium footprint (no haze, no beams)
    foot = [pose.proj((sx * 64.0, sy * 50.0, G.PODIUM_H)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    if all(v is not None for v in foot):
        pm = Image.new("L", (PW, PH), 0)
        ImageDraw.Draw(pm).polygon([(v[0] * K, v[1] * K) for v in foot], fill=255)
        pmask = np.asarray(pm, np.float32) / 255.0
        r, g, b = full[..., 0], full[..., 1], full[..., 2]
        green = L.smoothstep(0.05, 0.25, g - np.maximum(r, b) * 1.1) * pmask
        lum = L.luma(full)
        shift = np.stack([lum * 1.0, lum * 0.32, lum * 0.62], -1)
        full = full * (1 - green[..., None]) + shift * green[..., None]
    return np.clip(full, 0, 1), (y0, y1, x0, x1), m, zc, tw, d, kp


def gauge_overlay(img01, A, mt):
    """BLOOM gauge (right edge, below THE SEQUENCE panel), INFECTED hairlines and chips on the rooms behind the front."""
    S = L.SS
    h, w = img01.shape[:2]
    lay = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    k = w / 1920.0
    PINK = L.PINK8 + (255,)
    # rooms behind the front: pink hairline on the outer edge of the oval / frame ONLY
    seen = set()
    for i in G.NODES:
        if i in ("start", "srv"):
            continue
        r = A["rooms"].get(i)
        if not r or not r["vis"] or G.LAYER[i] > FRONT_LAYER:
            continue
        sc = O.room_scale(A, i)
        cx, cy = O.sticker_xy(A, i, sc)
        rr = 29 * sc
        d.ellipse([(cx - rr) * k * S, (cy - rr) * k * S, (cx + rr) * k * S, (cy + rr) * k * S], outline=PINK, width=int(1.5 * k * S))
        seen.add(i)
    for i in sorted(seen):
        if G.LAYER[i] < FRONT_LAYER - 1:
            continue                                         # chips on the two highest infected layers; hairlines on all
        sc = O.room_scale(A, i)
        cx, cy = O.sticker_xy(A, i, sc)
        side = -1 if G.TOWER[i] == "A" else 1
        L.chip(d, (cx + side * 46 * sc) * k, cy * k, "INFECTED", L.PINK8, int(12 * k), glyph=True, anchor="lm" if side > 0 else "rm")
    # gauge
    x, y0, y1, gw = 1893 * k, 260 * k, 1000 * k, 13 * k
    top, bot = 9.0, 0.0

    def Y(v):
        return y1 - (v - bot) / (top - bot) * (y1 - y0)
    d.rectangle([(x - gw / 2) * S, y0 * S, (x + gw / 2) * S, y1 * S], fill=(10, 6, 14, 215), outline=(120, 90, 110, 220), width=S)
    fy = Y(FRONT_LAYER)
    d.rectangle([(x - gw / 2 + 1) * S, fy * S, (x + gw / 2 - 1) * S, (y1 - 1) * S], fill=(46, 18, 36, 255))
    for yy in range(int(fy), int(y1), int(6 * k)):
        d.line([((x - gw / 2 + 1) * S, yy * S), ((x + gw / 2 - 1) * S, (yy - 6 * k) * S)], fill=(160, 60, 105, 150), width=S)
    d.line([((x - gw / 2 - 5 * k) * S, fy * S), ((x + gw / 2 + 5 * k) * S, fy * S)], fill=PINK, width=int(2 * S))
    for n in range(1, 9):
        yy = Y(n)
        d.line([((x - gw / 2 - 7 * k) * S, yy * S), ((x - gw / 2) * S, yy * S)], fill=(215, 215, 225, 230), width=S)
        d.text(((x - gw / 2 - 10 * k) * S, yy * S), "L%d" % n, font=L.font(int(11 * k) * S), fill=(200, 200, 212, 220), anchor="rm")
    d.text(((x - gw / 2 - 10 * k) * S, Y(9) * S), "TARGET", font=L.font(int(10 * k) * S), fill=(255, 120, 120, 230), anchor="rm")
    oy = Y(OP_LAYER)
    d.polygon([((x + gw / 2 + 3 * k) * S, oy * S), ((x + gw / 2 + 12 * k) * S, (oy - 6 * k) * S), ((x + gw / 2 + 12 * k) * S, (oy + 6 * k) * S)], fill=(150, 255, 70, 255))
    L.spore(d, x, y0 - 22 * k, 10 * k, PINK, w=1.8)
    d.text((x * S, (y0 - 42 * k) * S), "BLOOM", font=L.font(int(14 * k) * S), fill=PINK, anchor="mm")
    L.chip(d, x - 40 * k, fy, "CLOSE  FRONT -%.1f" % (OP_LAYER - FRONT_LAYER), L.PINK8, int(12 * k), glyph=False, anchor="rm")
    return L.flatten(img01, lay)


def main():
    ov = json.load(open(os.path.join(HQS, "scratch", "ov_stills.json")))["H_overview"]
    ov["walked"], ov["mt"] = WALKED, len(WALKED) - 1
    pose = O.pose_of(ov["pose"])
    plate = Image.open(os.path.join(HQS, "plates", "H_overview_v4_plate.png")).convert("RGB")
    G.set_shot({}) if hasattr(G, "set_shot") else None
    clean_img = C.compose(plate, ov)
    bl, box, m, zc, tw, d, kp = bloom_plate(plate, pose)
    bplate = Image.fromarray((bl * 255 + 0.5).astype(np.uint8))
    still = C.compose(bplate, ov)
    A = O.anchors(pose, WALKED, ov["mt"])
    s01 = np.asarray(still, np.float32) / 255.0
    s01 = gauge_overlay(s01, A, ov["mt"])
    out = Image.fromarray((np.clip(s01, 0, 1) * 255 + 0.5).astype(np.uint8)).resize((1920, 1080), Image.LANCZOS)
    os.makedirs(L.OUT, exist_ok=True)
    out.save(os.path.join(L.OUT, "H_bloom_overview.png"))
    clean_img.resize((1920, 1080), Image.LANCZOS).save(os.path.join(L.SCRATCH, "H_clean_overview.png"))
    P0 = np.asarray(plate, np.float32) / 255.0
    # landmark / local background ratio on the tower mask (clean vs bloom)
    y0, y1, x0, x1 = box
    ring = np.zeros((PH, PW), bool)
    mk = np.zeros((PH, PW), bool)
    mk[y0:y1, x0:x1] = m
    from PIL import ImageFilter
    big = np.asarray(Image.fromarray((mk * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(61)), np.float32) > 0
    ring = big & ~mk

    def ratio(a):
        Lm = L.luma(a)
        return float(Lm[mk].mean() / max(Lm[ring].mean(), 1e-4))
    res = dict(clean=L.metrics(P0), bloom=L.metrics(bl), ratio_clean=round(ratio(P0), 2), ratio_bloom=round(ratio(bl), 2),
               still=L.metrics(np.asarray(out, np.float32) / 255.0))
    print(res)
    json.dump(res, open(os.path.join(L.SCRATCH, "hq_values.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
