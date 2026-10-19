"""Halcyon THE EYE, HQ netrun, WATCH state: H_overview (1920 x 1080).

Base: hq_halcyon v2 OVERVIEW plate (read only) + its composed still H_overview_v2.png. The route chrome and UI of the
composed still are recovered as the pixels that differ from the plate (dilated); the theme (90 degree sector on the
ground, gobo edge lines from the turret, blade line, ring) is drawn UNDER them, so no route room or UI is ever covered.
Run:  python halcyon_hq.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import solace_lib as L
import theme_lib as T

HQ = os.path.join(T.ROUTE, "hq_halcyon")
W, H = 2560, 1440
K = 1920 / 2560.0
TEAL = np.array([0.62, 0.98, 0.95], np.float32)
TEAL8 = (140, 240, 235)
SC = 2560 / 2000.0                         # coordinates below are read off the 2000 px wide preview


def P(x, y):
    return (x * SC, y * SC)


APEX = P(1190, 215)
CEN = P(1190, 800)


def main():
    plate = np.asarray(Image.open(os.path.join(HQ, "plates", "H_overview_v2_plate.png")).convert("RGB"), np.float32) / 255.0
    comp = np.asarray(Image.open(os.path.join(HQ, "H_overview_v2.png")).convert("RGB"), np.float32) / 255.0
    chrome = (np.abs(comp - plate).max(axis=2) > 0.04).astype(np.float32)
    chrome_d = np.asarray(Image.fromarray((chrome * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(21)).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255.0
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # sector on the ground: a perspective ellipse centred below the pyramid, 90 deg wide, facing NE (towards the lit face)
    rx, ry = 1150.0, 520.0
    gx, gy = CEN[0] + 30, CEN[1] + 130
    ang = np.degrees(np.arctan2(-(yy - gy) / ry, (xx - gx) / rx))        # 0 = east (screen right), +90 = up the screen
    rr = np.hypot((xx - gx) / rx, (yy - gy) / ry)
    az = 20.0
    dd = (ang - az + 180) % 360 - 180
    sect = (np.abs(dd) < 45) * (1 - L.smoothstep(0.75, 1.0, rr)) * L.smoothstep(0.12, 0.3, rr)
    sect = L.blur(sect.astype(np.float32), 3)
    edge = np.exp(-((np.abs(dd) - 45) / 1.0) ** 2) * (rr < 1.0) * (rr > 0.14)
    # light is cold white-teal; added only where the plate is dark (a wash, not a hotspot), never near chrome
    keep = 1 - chrome_d
    lift = sect * (0.14 + 0.16 * (1 - np.clip(L.luma(plate) / 0.35, 0, 1))) * keep
    out = plate + lift[..., None] * TEAL[None, None, :] * 0.9
    # sector edge + ring lines, thin
    lay = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    S = 2
    for sgn in (-1, 1):
        pts = []
        for t in np.linspace(0.14, 1.0, 30):
            a = np.radians(az + sgn * 45)
            pts.append(((gx + rx * t * np.cos(a)) * S, (gy - ry * t * np.sin(a)) * S))
        d.line(pts, fill=(225, 255, 252, 235), width=4 * S)
    pts = []
    for a in np.linspace(az - 45, az + 45, 50):
        pts.append(((gx + rx * np.cos(np.radians(a))) * S, (gy - ry * np.sin(np.radians(a))) * S))
    d.line(pts, fill=TEAL8 + (170,), width=2 * S)
    # the blade: one white line across the sector (WATCH)
    for t in (0.58,):
        p0 = (gx + rx * t * np.cos(np.radians(az - 45)), gy - ry * t * np.sin(np.radians(az - 45)))
        p1 = (gx + rx * t * np.cos(np.radians(az + 45)), gy - ry * t * np.sin(np.radians(az + 45)))
        d.line([(p0[0] * S, p0[1] * S), (p1[0] * S, p1[1] * S)], fill=(255, 255, 255, 230), width=4 * S)
    # gobo lines from the turret down to the two sector corners on the ground
    for sgn in (-1, 1):
        a = np.radians(az + sgn * 45)
        q = (gx + rx * 0.95 * np.cos(a), gy - ry * 0.95 * np.sin(a))
        d.line([(APEX[0] * S, (APEX[1] + 30) * S), (q[0] * S, q[1] * S)], fill=(225, 255, 252, 70), width=S)
    lay = lay.resize((W, H), Image.LANCZOS)
    a = np.asarray(lay, np.float32) / 255.0
    al = a[..., 3:4] * keep[..., None]
    out = out * (1 - al) + a[..., :3] * al
    out = np.clip(out, 0, 1)
    plate_vals = L.metrics(out)
    final = out * (1 - chrome[..., None]) + comp * chrome[..., None]
    # keep the soft chrome rim: blend with the dilated matte edge
    fin = Image.fromarray((final * 255 + 0.5).astype(np.uint8)).resize((1920, 1080), Image.LANCZOS)
    od = T.out_dir("halcyon")
    fin.save(os.path.join(od, "H_overview.png"))
    f = np.asarray(fin, np.float32) / 255.0
    print("plate_clean", L.metrics(plate), "plate_theme", plate_vals, "still", L.metrics(f))


if __name__ == "__main__":
    main()
