"""Halcyon THE EYE, street netrun light form, FIXED (2 left): S_fixed (1920 x 1080).

2D compositing over the street_r2 DECISION plate (read only), reusing solace_street.Scene (Z pass + camera + room
quads). The far-skyline mast stands in the gap between the two facades, above and beside every room hull (+10 %);
its beam drops through the gap onto a ground pool with a ring, the blade line, gobo edge lines. The wash is light
linked to building faces (Z pass valid and above the street) and never touches room quads or route links.
Run:  python halcyon_street.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw

import solace_lib as L
import solace_street as SSt
import theme_lib as T

W, H = T.W, T.H
MAST = (905, 205)                  # eye turret centre (output px), in the dark gap between the facades
POOL = (985, 940)
TEAL = np.array([0.62, 0.98, 0.95], np.float32)
TEAL8 = (140, 240, 235)
AMBER8 = (255, 170, 40)
RED8 = (240, 50, 60)


def build(sc, left=2):
    km, vis = SSt.keep_masks(sc)
    P = sc.plate.copy()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rooms_m = L.blur(L.poly_mask(H, W, list(vis.values()), grow=0.10, feather=0), 2.5)
    # --- the beam: a narrow shaft from the mast to the pool, additive, fog modulated, under the rooms
    s = 1.0 if left == 2 else 0.85
    t = np.clip((yy - MAST[1]) / (POOL[1] - MAST[1]), 0, 1)
    cx = MAST[0] + (POOL[0] - MAST[0]) * t
    halfw = 8 + 150 * t ** 1.3
    prof = np.exp(-((xx - cx) / np.maximum(halfw, 1)) ** 2 * 1.6)
    fog = 0.7 + 0.5 * L.fbm(xx * 0.01, yy * 0.012, 5, 3)
    beam = prof * (yy > MAST[1]) * (yy < POOL[1] + 10) * (0.55 - 0.30 * t) * fog * s
    beam = beam * (1 - 0.9 * rooms_m)
    out = P + beam[..., None] * TEAL[None, None, :] * 0.55
    # --- the wash on building faces near the beam (light linked: valid Z, above the street), never on rooms / links
    face = sc.valid & (sc.wz > 1.5)
    wd = np.exp(-((xx - cx) / 520.0) ** 2) * (yy < 800)
    wash = wd * face * (1 - km) * 0.07 * s
    out = out + (wash * L.luma(P) ** 0.5)[..., None] * TEAL[None, None, :] * 0.9
    # --- ground pool decal with the closed ring (2 left) or four arcs (1 left); fades to 0 above 2 BU
    ground = (sc.wz < 1.0) & sc.valid
    rx, ry = 300.0, 62.0
    q = np.hypot((xx - POOL[0]) / rx, (yy - POOL[1]) / ry)
    pool = (1 - L.smoothstep(0.35, 1.0, q)) * 0.20 * s
    pool = pool * np.where(ground | (yy > 900), 1.0, 0.0) * (1 - km)
    out = out + pool[..., None] * TEAL[None, None, :] * 0.55
    return out, vis, km, q, rooms_m, cx


def overlay(out, vis, q, left):
    lay = T.canvas()
    d = ImageDraw.Draw(lay)
    S = L.SS
    # gobo edge lines: the 90 degree sector from the mast, seen as two thin lines onto the ground pool
    for sx in (-1, 1):
        d.line([(MAST[0] * S, (MAST[1] + 40) * S), ((POOL[0] + sx * 300) * S, (POOL[1] - 8) * S)], fill=(225, 255, 252, 120), width=S)
    # pool ring: closed ring for 2 left, four arcs for 1 left; ticks around it
    rx, ry = 300.0, 62.0
    box = [(POOL[0] - rx) * S, (POOL[1] - ry) * S, (POOL[0] + rx) * S, (POOL[1] + ry) * S]
    if left == 2:
        d.ellipse(box, outline=(235, 255, 252, 230), width=2 * S)
    else:
        for k in range(4):
            d.arc(box, k * 90 + 12, k * 90 + 78, fill=(235, 255, 252, 230), width=2 * S)
    for k in range(24):
        a = np.radians(k * 15)
        x0, y0 = POOL[0] + (rx - 2) * np.cos(a), POOL[1] + (ry - 1) * np.sin(a)
        x1, y1 = POOL[0] + (rx + 12) * np.cos(a), POOL[1] + (ry + 4) * np.sin(a)
        d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=(235, 255, 252, 200), width=S)
    # the blade: one white line across the pool (<= 0.70)
    d.line([((POOL[0] - rx * 0.86) * S, (POOL[1] + 4) * S), ((POOL[0] + rx * 0.86) * S, (POOL[1] - 12) * S)], fill=(255, 255, 255, 175), width=2 * S)
    # the mast: amber almond rim, dilated teal iris (+20 %)
    T.eye_glyph(d, MAST[0], MAST[1], 46, AMBER8 + (255,), TEAL8 + (255,), lw=3)
    d.line([(MAST[0] * S, (MAST[1] - 28) * S), (MAST[0] * S, (MAST[1] - 150) * S)], fill=(120, 130, 135, 255), width=3 * S)
    d.line([(MAST[0] * S, (MAST[1] + 30) * S), (MAST[0] * S, (MAST[1] + 90) * S)], fill=(120, 130, 135, 255), width=5 * S)
    return T.flat(out, lay)


def header(img, left):
    lay = T.canvas()
    d = ImageDraw.Draw(lay)
    S = L.SS
    x0, y0, x1, y1 = 1560, 98, 1880, 150
    T.panel(d, (x0, y0, x1, y1), fill=(8, 14, 18, 225), outline=(140, 200, 205, 235))
    cx, cy = x0 + 34, (y0 + y1) / 2
    # lock-on glyph: eye in a thin ring with 4 ticks
    d.ellipse([(cx - 22) * S, (cy - 22) * S, (cx + 22) * S, (cy + 22) * S], outline=(255, 255, 255, 255), width=2 * S)
    for k in range(4):
        a = np.radians(45 + 90 * k)
        d.line([((cx + 22 * np.cos(a)) * S, (cy - 22 * np.sin(a)) * S), ((cx + 30 * np.cos(a)) * S, (cy - 30 * np.sin(a)) * S)], fill=(255, 255, 255, 255), width=2 * S)
    T.eye_glyph(d, cx, cy, 15, AMBER8 + (255,), TEAL8 + (255,), lw=2)
    T.text(d, x0 + 78, cy, "FIXED", 20, (235, 250, 250, 255))
    for k in range(2):
        px = x1 - 60 + k * 30
        if k < left:
            d.ellipse([(px - 9) * S, (cy - 9) * S, (px + 9) * S, (cy + 9) * S], fill=RED8 + (255,), outline=(255, 210, 210, 255), width=2 * S)
        else:
            d.ellipse([(px - 9) * S, (cy - 9) * S, (px + 9) * S, (cy + 9) * S], fill=(10, 8, 10, 200), outline=RED8 + (200,), width=2 * S)
    return T.flat(img, lay)


def main():
    sc = SSt.Scene()
    od = T.out_dir("halcyon")
    P0 = sc.plate
    res = {"clean_plate": L.metrics(P0)}
    for name, left in (("S_fixed", 2),):
        out, vis, km, q, rooms_m, cx = build(sc, left)
        plate_theme = np.clip(out, 0, 1)
        res["plate_with_theme_no_ui"] = L.metrics(plate_theme)
        img = overlay(plate_theme, vis, q, left)
        res["plate_with_marks_no_ui"] = L.metrics(img)
        img = L.flatten(img, SSt.route_layer(sc, vis, None, None))
        ui = np.asarray(SSt.chrome(img), np.float32) / 255.0
        ui = header(ui, left)
        # proof: theme pixels inside room hulls (+10 %) must be zero: compare the theme-only delta there
        delta = np.abs(plate_theme - P0).max(axis=2)
        res["theme_delta_in_room_hulls_max"] = round(float((delta * (rooms_m > 0.99)).max()), 4)
        T.save(ui, os.path.join(od, name + ".png"))
        res[name] = L.metrics(ui)
        print(name, res, flush=True)
    return res


if __name__ == "__main__":
    main()
