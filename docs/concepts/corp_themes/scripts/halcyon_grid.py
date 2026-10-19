"""Halcyon THE EYE, Grid stills: G_scan, G_spotted, G_fixed2, G_fixed1 (1920 x 1080), a 2D mock over the Grid capture.

Provisional rules (themes/halcyon.md "Art answers"): the Eye is a 90 degree wedge from the HQ marker, steps 45 deg,
Spotted territory = a district (with its Sites) whose bearing is in the wedge, 2 difficulty pips (1 = spotted,
2 = FIXED), fixed area = wedge centred on the Exploit Site bearing rounded to 45 deg, +25 % damage chip in raid mode.
Palette: white-teal for light, amber on the Eye hardware only, red only for consequence marks (badge, pips).
Run:  python halcyon_grid.py
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw

import solace_lib as L
import theme_lib as T

W, H = T.W, T.H
CORP = "halcyon"
MARK = (240, 820)                          # the Halcyon HQ marker on the map (output px)
RAD = 1330.0                               # wedge radius
EXPLOIT = (852, 360)                       # the Exploit Site used for FIXED (Patch Distribution Node)
TEAL = np.array([0.55, 0.95, 0.93], np.float32)
TEAL8 = (140, 240, 235)
AMBER8 = (255, 170, 40)
RED8 = (240, 50, 60)
CELL = 330.0


def bearing_deg(x, y):
    """Screen bearing from the marker: 0 = east, counter clockwise positive (up is +90)."""
    return math.degrees(math.atan2(-(y - MARK[1]), x - MARK[0]))


def in_wedge(x, y, az, r=RAD):
    d = (bearing_deg(x, y) - az + 180) % 360 - 180
    return (abs(d) <= 45.0) & (np.hypot(x - MARK[0], y - MARK[1]) <= r)


def district_ids():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = xx * 0.866 + yy * 0.5
    v = -xx * 0.5 + yy * 0.866
    cu, cv = np.floor(u / CELL).astype(np.int32), np.floor(v / CELL).astype(np.int32)
    ids = (cu + 50) * 200 + (cv + 50)
    return ids, xx, yy


def spotted_mask(ids, xx, yy, az):
    """Per-pixel 0/1: district centroid (pixels inside the map) is in the wedge."""
    mm = T.map_mask(0) > 0.5
    out = np.zeros(ids.shape, np.float32)
    for i in np.unique(ids[mm]):
        sel = (ids == i) & mm
        if sel.sum() < 4000:
            continue
        cx, cy = float(xx[sel].mean()), float(yy[sel].mean())
        if in_wedge(cx, cy, az, RAD * 1.0):
            out[ids == i] = 1.0
    return out * mm


def wedge_poly(az, r=RAD, n=40):
    pts = [MARK]
    for k in range(n + 1):
        a = math.radians(az - 45 + 90 * k / n)
        pts.append((MARK[0] + r * math.cos(a), MARK[1] - r * math.sin(a)))
    return pts


def render(name, az, mode, pips, fixed_left=0, show_dial=True):
    base = T.grid_base()
    prot = T.grid_protect(base)
    mm = T.map_mask()
    ids, xx, yy = district_ids()
    sp = spotted_mask(ids, xx, yy, az) if mode in ("spotted", "fixed") else np.zeros((H, W), np.float32)
    spb = L.blur(sp, 2.0)
    # wedge light: white-teal, soft near the marker, 12 % fill (scan) / 18 % (fixed), edges drawn later
    wm = T.shape_mask(lambda d: d.polygon(wedge_poly(az), fill=255), 1.5)
    rr = np.hypot(xx - MARK[0], yy - MARK[1])
    fall = 1.0 - 0.55 * L.smoothstep(100, RAD, rr)
    k_w = {"scan": 0.26, "spotted": 0.16, "fixed": 0.22}[mode] * wm * fall * mm
    out = base.copy()
    free = 1 - 0.85 * prot
    dimk = (1 - wm) * mm * (1 - 0.7 * prot) * {"scan": 0.5, "spotted": 0.42, "fixed": 0.5}[mode]
    out = out * (1 - dimk[..., None])
    out = out * (1 - (k_w * free)[..., None]) + (k_w * free)[..., None] * TEAL[None, None, :] * 0.95
    if mode in ("spotted", "fixed"):
        # cold 45 deg hatch, 12 px spacing, ~25 % alpha, on the spotted districts; scan lines travel with it
        hat = L.hatch(H, W, 12, 2)
        ha = hat * spb * (1 - prot) * (0.25 if mode == "spotted" else 0.34)
        out = out * (1 - ha[..., None]) + ha[..., None] * TEAL[None, None, :]
        # darken the clean, un-spotted part slightly so the territory reads without the hue (grid base is bright cyan links)
        clean = (1 - spb) * mm * (1 - prot)
        out = out * (1 - 0.18 * clean[..., None])
    out = np.clip(out, 0, 1)
    lay = T.canvas()
    d = ImageDraw.Draw(lay)
    S = L.SS
    # dashed teal border of the spotted territory (district id changes between spotted / clean)
    if mode in ("spotted", "fixed"):
        edge = (np.abs(np.diff(sp, axis=1, prepend=sp[:, :1])) + np.abs(np.diff(sp, axis=0, prepend=sp[:1])) > 0.5) & (mm > 0.5)
        ey, ex = np.where(edge)
        for y0, x0 in zip(ey[::3], ex[::3]):
            if ((x0 // 10) + (y0 // 10)) % 2 == 0:
                d.rectangle([x0 * S, y0 * S, (x0 + 2) * S, (y0 + 2) * S], fill=TEAL8 + (235,))
    # wedge edge lines
    pts = wedge_poly(az)
    if mode == "fixed":
        a = 245
        d.line([(p[0] * S, p[1] * S) for p in (pts[0], pts[1])], fill=(235, 255, 252, a), width=3 * S)
        d.line([(p[0] * S, p[1] * S) for p in (pts[0], pts[-1])], fill=(235, 255, 252, a), width=3 * S)
        d.line([(p[0] * S, p[1] * S) for p in pts[1:]], fill=TEAL8 + (200,), width=2 * S)
        # the blade: one white line across the sector at mid radius, perpendicular to the axis
        ax = math.radians(az)
        rb = RAD * 0.62
        for off in (-45, 45):
            pass
        p0 = (MARK[0] + rb * math.cos(math.radians(az - 45)), MARK[1] - rb * math.sin(math.radians(az - 45)))
        p1 = (MARK[0] + rb * math.cos(math.radians(az + 45)), MARK[1] - rb * math.sin(math.radians(az + 45)))
        d.line([(p0[0] * S, p0[1] * S), (p1[0] * S, p1[1] * S)], fill=(255, 255, 255, 215), width=2 * S)
    else:
        d.line([(p[0] * S, p[1] * S) for p in (pts[0], pts[1])], fill=TEAL8 + (190,), width=2 * S)
        d.line([(p[0] * S, p[1] * S) for p in (pts[0], pts[-1])], fill=TEAL8 + (190,), width=2 * S)
        d.line([(p[0] * S, p[1] * S) for p in pts[1:]], fill=TEAL8 + (110,), width=S)
    # eye dial: 8 octant ticks around the marker, NOW bright, next 3 dimmer (the Eye steps +45 deg per ended netrun)
    if show_dial:
        R0 = 78
        for k in range(8):
            a = math.radians(k * 45)
            x0, y0 = MARK[0] + (R0 - 6) * math.cos(a), MARK[1] - (R0 - 6) * math.sin(a)
            x1, y1 = MARK[0] + (R0 + 6) * math.cos(a), MARK[1] - (R0 + 6) * math.sin(a)
            step = ((k * 45 - az) % 360) / 45
            if step == 0:
                col, wd = (255, 255, 255, 255), 4
            elif step in (1, 2, 3):
                col, wd = TEAL8 + (int(210 - 50 * step),), 2
            else:
                col, wd = (120, 140, 145, 150), 1
            d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=col, width=wd * S)
        d.arc([(MARK[0] - R0) * S, (MARK[1] - R0) * S, (MARK[0] + R0) * S, (MARK[1] + R0) * S], 0, 360, fill=TEAL8 + (110,), width=S)
        a = math.radians(az)
        d.polygon([((MARK[0] + (R0 + 16) * math.cos(a)) * S, (MARK[1] - (R0 + 16) * math.sin(a)) * S),
                   ((MARK[0] + (R0 + 4) * math.cos(a + 0.12)) * S, (MARK[1] - (R0 + 4) * math.sin(a + 0.12)) * S),
                   ((MARK[0] + (R0 + 4) * math.cos(a - 0.12)) * S, (MARK[1] - (R0 + 4) * math.sin(a - 0.12)) * S)], fill=(255, 255, 255, 255))
    # the Eye marker on the HQ marker: amber rim on the hardware, teal iris
    d.ellipse([(MARK[0] - 46) * S, (MARK[1] - 46) * S, (MARK[0] + 46) * S, (MARK[1] + 46) * S], fill=(8, 14, 18, 225), outline=TEAL8 + (230,), width=2 * S)
    T.eye_glyph(d, MARK[0], MARK[1], 36, AMBER8 + (255,), TEAL8 + (255,), lw=3)
    if mode == "fixed":
        # lock-on: crosshair ring with 4 ticks round the marker, 2 pips below (filled = remaining)
        for k in range(4):
            a = math.radians(k * 90 + 45)
            d.line([((MARK[0] + 50 * math.cos(a)) * S, (MARK[1] - 50 * math.sin(a)) * S),
                    ((MARK[0] + 62 * math.cos(a)) * S, (MARK[1] - 62 * math.sin(a)) * S)], fill=(255, 255, 255, 255), width=3 * S)
        d.ellipse([(MARK[0] - 56) * S, (MARK[1] - 56) * S, (MARK[0] + 56) * S, (MARK[1] + 56) * S], outline=(255, 255, 255, 255), width=2 * S)
        pip_row(d, MARK[0], MARK[1] + 98, 2, fixed_left)
        # the Exploit Site that fixed the Eye: bearing line, rounded to 45 deg
        d.line([(MARK[0] * S, MARK[1] * S), (EXPLOIT[0] * S, EXPLOIT[1] * S)], fill=(255, 255, 255, 60), width=S)
        T.chipbox(d, MARK[0] + 66, MARK[1] + 150, "FIXED  %d NETRUN%s LEFT" % (fixed_left, "S" if fixed_left != 1 else ""), (255, 255, 255, 255), 15)
    # SEEN badges (red eye badge) on the nodes inside the spotted districts + the chip for the raid hook
    if mode in ("spotted", "fixed"):
        for (nx, ny) in NODES:
            if in_wedge(nx, ny, az, RAD):
                bx, by = nx + 20, ny - 26
                d.ellipse([(bx - 11) * S, (by - 11) * S, (bx + 11) * S, (by + 11) * S], fill=(40, 6, 10, 245), outline=RED8 + (255,), width=2 * S)
                T.eye_glyph(d, bx, by, 8, RED8 + (255,), RED8 + (255,), lw=1, pupil=False)
    # header: eye glyph + difficulty pips + state word, in the strip under the top bar (map side)
    header(d, mode, pips, az)
    out = T.flat(out, lay)
    return out


NODES = [(135, 372), (190, 522), (97, 594), (147, 620), (836, 497), (841, 650), (790, 690), (1435, 545), (1435, 685),
         (180, 850), (180, 930), (165, 1005), (790, 852), (790, 1055), (1200, 698), (868, 215), (856, 360)]


def pip_row(d, cx, cy, n, filled):
    S = L.SS
    for k in range(n):
        x = cx + (k - (n - 1) / 2) * 30
        if k < filled:
            d.ellipse([(x - 10) * S, (cy - 10) * S, (x + 10) * S, (cy + 10) * S], fill=RED8 + (255,), outline=(255, 210, 210, 255), width=2 * S)
        else:
            d.ellipse([(x - 10) * S, (cy - 10) * S, (x + 10) * S, (cy + 10) * S], fill=(10, 8, 10, 200), outline=RED8 + (200,), width=2 * S)


def header(d, mode, pips, az):
    S = L.SS
    x0, y0, x1, y1 = 70, 108, 790, 150
    T.panel(d, (x0, y0, x1, y1), fill=(8, 14, 18, 225), outline=(140, 200, 205, 235))
    T.eye_glyph(d, x0 + 34, (y0 + y1) / 2, 15, AMBER8 + (255,), TEAL8 + (255,), lw=2)
    word = {"scan": "THE EYE  SCANNING  %03d DEG" % (az % 360), "spotted": "SPOTTED TERRITORY  IN THE EYE",
            "fixed": "THE EYE  FIXED ON EXPLOIT"}[mode]
    T.text(d, x0 + 64, (y0 + y1) / 2, word, 18, (235, 250, 250, 255))
    if pips is not None:
        T.text(d, x1 - 170, (y0 + y1) / 2, "DIFFICULTY", 13, (170, 200, 205, 255), "lm")
        pip_row(d, x1 - 40, (y0 + y1) / 2, 2, pips)


def chip_layer(img, mode, az):
    lay = T.canvas()
    d = ImageDraw.Draw(lay)
    if mode in ("spotted", "fixed"):
        T.chipbox(d, 70, 176, "RAID: +25 % DAMAGE HERE", RED8 + (255,), 14, fill=(30, 6, 10, 235))
        T.chipbox(d, 70 + 280, 176, "SEEN", RED8 + (255,), 14, fill=(30, 6, 10, 235))
    return T.flat(img, lay)


STILLS = [
    ("G_scan", dict(az=0, mode="scan", pips=None)),
    ("G_spotted", dict(az=0, mode="spotted", pips=1)),
    ("G_fixed2", dict(az=45, mode="fixed", pips=2, fixed_left=2)),
    ("G_fixed1", dict(az=45, mode="fixed", pips=2, fixed_left=1)),
]


def main(which):
    od = T.out_dir(CORP)
    res = {}
    for name, kw in STILLS:
        if which != "all" and name not in which:
            continue
        mode = kw["mode"]
        img = render(name, kw["az"], mode, kw["pips"], kw.get("fixed_left", 0))
        img = chip_layer(img, mode, kw["az"])
        T.save(img, os.path.join(od, name + ".png"))
        res[name] = T.vals(img)
        print(name, res[name], flush=True)
    return res


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "all"
    main(a if a == "all" else a.split(","))
