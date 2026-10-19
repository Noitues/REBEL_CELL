"""Tethys THE WATER LEVEL, flooded street netrun: S_flood_HIGH and S_flood_strip (1920 x 1080).

Over the street_r2 DECISION plate (read only) via solace_street.Scene (Z pass + camera + room quads). The water line is
ONE world-space plane at the Head height (LOW 0.5, RISING 2.5, FALLING 3.2, HIGH 4.0 BU; ground-floor rooms are 1.1-5 BU
tall, floor 2 starts at 4.1), so it cuts every facade at the same height and sits on the cut buildings too. Above the
line nothing changes; below it the facade goes abyss blue (windows shift cyan-green and dim), the street becomes a
water plane with a flipped, blurred, ripple-distorted reflection of the facades (strong at LOW, weak at HIGH).
Ground-floor rooms below the line are LOWER: dimmed 55 % with the sealed-hatch glyph at HIGH. They stay visible.
Run:  python tethys_street.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw

import solace_lib as L
import solace_street as SSt
import tethys_hq as TQ
import theme_lib as T

W, H = T.W, T.H
STREET_HEAD = {"LOW": 0.5, "RISING": 2.5, "HIGH": 4.0, "FALLING": 3.2}
ABYSS = TQ.ABYSS
SEQ = TQ.SEQ


def flood(sc, step, seed=4):
    h = STREET_HEAD[step]
    P = sc.plate.copy()
    wz, vs = T.nsmooth(np.nan_to_num(sc.wz, nan=0.0), sc.valid, 5)
    valid = sc.valid & vs
    wz = np.where(valid, wz, 99.0)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    under = valid & (wz < h)
    cont = under
    gnd = under & (wz < 0.8)
    fac = under & ~gnd
    # waterline row per column on the facade: the lowest row whose height is at or above the water; a running median
    # over 61 columns drops lamp posts and other thin things in front
    above = valid & (wz >= h) & (yy > 300)
    rows = np.where(above, yy, 0).max(axis=0)
    line_y = T.med_cols(rows.astype(np.float32), 61)
    # facade under the line: abyss tint, windows cyan-green, dimmed
    lum = L.luma(P)
    win = np.clip((lum - 0.28) / 0.45, 0, 1)[..., None]
    depth = np.clip((h - wz) / max(h, 1.0), 0, 1)[..., None]
    tinted = P * np.array([0.42, 0.78, 0.9], np.float32) * (0.78 - 0.25 * depth) + ABYSS * (0.45 + 0.35 * depth)
    tinted = tinted * (1 - win * 0.35) + win * (P * np.array([0.35, 1.0, 0.85], np.float32) * 0.55)
    kf = L.blur(fac.astype(np.float32), 1.2)[..., None]
    out = P * (1 - kf) + tinted * kf
    # street as a water plane: reflection of the facade (flip about the line), blurred, rippled; strength falls with Head
    refl_k = {"LOW": 0.55, "RISING": 0.40, "HIGH": 0.18, "FALLING": 0.30}[step]
    rip = 6.0 * (L.fbm(xx * 0.012, yy * 0.06, seed, 3) - 0.5) * (1.0 if step in ("LOW", "RISING") else 2.2)
    ly = line_y[None, :].astype(np.float32) * np.ones_like(yy)
    sy = np.clip(2 * ly - yy + rip, 0, H - 1).astype(np.int32)
    refl = P[sy, xx.astype(np.int32)]
    refl = np.stack([L.boxblur(refl[..., c], 3, 2) for c in range(3)], -1)
    rpl = 0.5 + 0.5 * np.sin(yy * 0.9 + 6.0 * L.fbm(xx * 0.01, yy * 0.05, seed + 2, 2))
    wat = P * np.array([0.30, 0.55, 0.75], np.float32) + ABYSS * 0.6
    wat = wat * (1 - refl_k) + (refl * np.array([0.8, 0.95, 1.0], np.float32)) * refl_k + (rpl * 0.03)[..., None]
    kg = L.blur(gnd.astype(np.float32), 1.5)[..., None]
    out = out * (1 - kg) + wat * kg
    # warm sodium lamps keep long warm streaks in the reflection (warm above, cool below)
    # the waterline: 2 px white-cyan on the facades + 6 px meniscus; foam flecks where it meets the walls
    steep = (np.abs(np.gradient(wz, axis=0)) > 0.015) & (np.abs(np.gradient(wz, axis=0)) < 0.5)
    ln = np.exp(-((wz - h) / 0.16) ** 2) * valid * steep
    ln = np.clip(L.blur(ln.astype(np.float32), 1.2) * 1.8, 0, 1) * (0.0 if step == "LOW" else 1.0)
    gl = L.blur(ln, 4.0)
    out = out + (gl * 0.30)[..., None] * np.array([0.7, 1.0, 1.0], np.float32)
    out = out * (1 - ln[..., None] * 0.85) + (ln * 0.95)[..., None] * np.array([0.9, 1.0, 1.0], np.float32)
    if step == "FALLING":
        tide = sc.valid & (wz >= h) & (wz < h + 1.4)
        kt = L.blur(tide.astype(np.float32), 1.0)[..., None] * 0.55
        out = out * (1 - kt) + out * np.array([0.62, 0.55, 0.45], np.float32) * kt
    if step == "HIGH":
        fl = L.fbm(xx * 0.08, yy * 0.2, seed + 7, 3)
        foam = L.smoothstep(0.62, 0.8, fl) * L.blur(ln, 6.0) * 2.0
        out = out + foam[..., None] * 0.35
    return np.clip(out, 0, 1), h, cont


def lower_rooms(sc, vis, h):
    """Rooms whose floor sill (z at the bottom edge of the quad) is below the water line."""
    res = {}
    for k, q in vis.items():
        cx = int(sum(p[0] for p in q) / 4)
        bot = int(max(p[1] for p in q)) - 4
        res[k] = float(sc.wz[min(H - 1, bot), cx]) < h
    return res


def room_marks(sc, vis, lowers, step):
    S = L.SS
    lay = T.canvas()
    d = ImageDraw.Draw(lay)
    closed = step == "HIGH"
    for rid, q in vis.items():
        low = lowers[rid]
        poly = [(x * S, y * S) for x, y in q]
        cx = sum(p[0] for p in q) / 4
        cy = sum(p[1] for p in q) / 4
        x1 = max(p[0] for p in q)
        y0 = min(p[1] for p in q)
        if low and closed:
            d.polygon(poly, fill=(2, 18, 46, 120))                       # dimmed, not hidden
            TQ.sealed_hatch(d, x1 - 20, y0 + 22, 11)
        TQ.level_glyph(d, x1 - 46, y0 + 24, low, TQ.PHOTO8 + (255,) if low else (255, 190, 100, 255))
    return lay


def render_plate(sc, step):
    out, h, cont = flood(sc, step)
    return out, h


def main():
    sc = SSt.Scene()
    od = T.out_dir("tethys")
    vis = sc.visible_rooms()
    res = {"clean": L.metrics(sc.plate)}
    # S_flood_HIGH: full composition with the route chrome and the gauge
    plates = {}
    for step in SEQ:
        out, h = render_plate(sc, step)
        plates[step] = out
        res["plate_" + step] = L.metrics(out)
    out = plates["HIGH"]
    lowers = lower_rooms(sc, vis, STREET_HEAD["HIGH"])
    img = L.flatten(out, SSt.route_layer(sc, vis, None, None))
    img = T.flat(img, room_marks(sc, vis, lowers, "HIGH"))
    ui = np.asarray(SSt.chrome(img), np.float32) / 255.0
    lay = TQ.gauge_layer("HIGH", x=1650, y=130)
    d = ImageDraw.Draw(lay)
    T.chipbox(d, 1650, 100, "WATER LINE +%.1f BU  SEALED" % STREET_HEAD["HIGH"], TQ.PHOTO8 + (255,), 14, fill=(6, 12, 24, 230))
    ui = T.flat(ui, lay)
    T.save(ui, os.path.join(od, "S_flood_HIGH.png"))
    res["S_flood_HIGH"] = L.metrics(ui)
    # S_flood_strip: the four Head steps, plates only (no UI), 2 x 2
    sh = Image.new("RGB", (1920, 1080))
    dr = ImageDraw.Draw(sh)
    for i, step in enumerate(SEQ):
        t = Image.fromarray((plates[step] * 255 + 0.5).astype(np.uint8)).resize((960, 540), Image.LANCZOS)
        sh.paste(t, ((i % 2) * 960, (i // 2) * 540))
        dr.text(((i % 2) * 960 + 14, (i // 2) * 540 + 20), "%s  +%.1f BU" % (step, STREET_HEAD[step]), font=L.font(22), fill=(124, 242, 228))
    sh.save(os.path.join(od, "S_flood_strip.png"))
    print(res, flush=True)
    return res


if __name__ == "__main__":
    main()
