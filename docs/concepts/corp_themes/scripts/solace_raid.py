"""Solace THE BLOOM, raid hook: R_20, R_58 -> R_60, R_90 (1920 x 1080), a 2D mock over the Grid capture.

Base: D:/Godot/rebel_cell/docs/art_review/PLAN2/GRID_VIEW_current.jpg (read only, 800 x 453, upscaled 2.4x).
The infected district is a distance field from the Solace source district, warped along the street directions; its
threshold is the quantile that makes the infected AREA of the map equal the percent. Links, nodes and labels are
protected by a brightness / colour matte (the capture is flat, so this stands in for "district fill under the links").
Run:  python solace_raid.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import solace_lib as L

BASE = "D:/Godot/rebel_cell/docs/art_review/PLAN2/GRID_VIEW_current.jpg"
W, H = 1920, 1080
MAP = (0, 40 * 2.4, 612 * 2.4, 453 * 2.4)         # map area (x0, y0, x1, y1): left of the legend panel, under the top bar
SRC = (150 * 2.4, 395 * 2.4)                      # the Solace source district (bottom left of the map)
LEVELS = {"R_20": (0.20, 2), "R_60": (0.60, 4), "R_90": (0.90, 7)}        # percent, "+n%/step" chip (placeholder rates)


def load_base():
    im = Image.open(BASE).convert("RGB").resize((int(800 * 2.4), int(453 * 2.4)), Image.LANCZOS)
    im = im.crop((0, 0, W, H)).filter(ImageFilter.UnsharpMask(1.6, 70, 2))
    return np.asarray(im, np.float32) / 255.0


def protect(base):
    """Links, nodes, labels and text: bright or green/cyan-saturated pixels, grown 2 px. 1 = never touched."""
    r, g, b = base[..., 0], base[..., 1], base[..., 2]
    Lm = L.luma(base)
    bright = L.smoothstep(0.42, 0.6, Lm)
    green = L.smoothstep(0.08, 0.2, g - np.maximum(r, b) * 0.95) * L.smoothstep(0.3, 0.5, g)
    m = np.maximum(bright, green)
    im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.0))
    return np.asarray(im, np.float32) / 255.0


def district_field():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = xx - SRC[0], yy - SRC[1]
    base_d = np.hypot(dx, 1.8 * dy)
    u = xx * 0.866 + yy * 0.5                    # the two street directions of the iso grid
    v = -xx * 0.5 + yy * 0.866
    warp = 150.0 * (L.fbm(u * 0.006, v * 0.025, 5, 4) + L.fbm(v * 0.006, u * 0.025, 9, 4) - 1.0)
    return base_d + warp, xx, yy


def render(base, prot, D, pct, rate):
    x0, y0, x1, y1 = MAP
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    inmap = ((xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)).astype(np.float32)
    inmap = L.blur(inmap, 1.5)
    thr = float(np.quantile(D[inmap > 0.5], pct))
    k = L.smoothstep(thr + 14, thr - 14, D)                      # 1 inside the infected district (soft 14 px)
    cover = k * inmap * (1 - prot)
    Lm = L.luma(base)
    wash_a = 0.62 + 0.30 * pct
    plum = L.PLUM[None, None, :] * 1.3
    tinted = base * (0.34 - 0.12 * pct) + plum * (0.70 + 0.30 * pct)
    # 45 degree hatch, 2 px lines on an 8 px pitch, pink at alpha 0.35; coverage thins with the percent
    hat = L.hatch(H, W, 8, 2)
    dens = L.fbm(xx * 0.01, yy * 0.01, 21, 3)
    hat = hat * (dens < (0.35 + 0.65 * pct)).astype(np.float32)
    out = base * (1 - cover[..., None] * wash_a) + tinted * (cover[..., None] * wash_a)
    out = out * (1 - (hat * cover * 0.35)[..., None]) + (hat * cover * 0.35)[..., None] * L.PINK[None, None, :]
    # the front: a pink hairline where the district ends (distance in px from the contour)
    gy, gx = np.gradient(D)
    dist = np.abs(D - thr) / (np.sqrt(gx * gx + gy * gy) + 1e-3)
    edge = np.clip(2.2 - dist, 0, 1) * inmap * (1 - 0.8 * prot)
    out = out * (1 - edge[..., None] * 0.9) + (edge * 0.9)[..., None] * L.PINK[None, None, :] * 0.9
    out = np.clip(out, 0, 1)
    # lift the clean part so the Grid median holds (the plum wash is dark)
    tm = float(np.median(L.luma(base)))
    unc = (1 - cover)[..., None]
    dim = (1 - L.smoothstep(0.4, 0.8, L.luma(base)))[..., None]
    def med(gn):
        return float(np.median(L.luma(np.clip(out * (1 + (gn - 1) * unc * dim), 0, 1))))
    if med(1.0) < tm - 0.012:
        lo, hi = 1.0, 1.7
        for _ in range(8):
            mid = (lo + hi) / 2
            if med(mid) < tm - 0.004:
                lo = mid
            else:
                hi = mid
        out = np.clip(out * (1 + (hi - 1) * unc * dim), 0, 1)
    return out, thr, cover


def gauge(img, pct, rate):
    """POPULATION INFECTED nn%: a wide strip under the top bar (map side), with the +n%/step chip and the CITY LOST cap."""
    S = L.SS
    lay = L.canvas((W, H))
    d = ImageDraw.Draw(lay)
    PINK = L.PINK8 + (255,)
    x0, x1, y0, y1 = 70, 1250, 100, 140               # 40 px = 3.7 % of the frame height
    d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=(12, 6, 14, 225), outline=(150, 100, 130, 230), width=S)
    fx = x0 + (x1 - x0) * pct
    d.rectangle([(x0 + 1) * S, (y0 + 1) * S, fx * S, (y1 - 1) * S], fill=(48, 18, 38, 255))
    for xx in range(int(x0), int(fx), 8):
        d.line([(xx * S, (y1 - 1) * S), ((xx + 38) * S, (y0 + 1) * S)], fill=(150, 56, 100, 120), width=S)
    d.line([(fx * S, (y0 - 4) * S), (fx * S, (y1 + 4) * S)], fill=PINK, width=2 * S)
    L.spore(d, fx + 14, (y0 + y1) / 2, 10, PINK, w=1.8)
    for q in (0.25, 0.5, 0.75):
        xx = x0 + (x1 - x0) * q
        d.line([(xx * S, (y1 - 6) * S), (xx * S, y1 * S)], fill=(210, 210, 222, 220), width=S)
    d.rectangle([(x1 - 3) * S, (y0 - 2) * S, (x1 + 90) * S, (y1 + 2) * S], fill=(26, 8, 18, 235), outline=PINK, width=S)
    d.text(((x1 + 45) * S, ((y0 + y1) / 2) * S), "CITY LOST", font=L.font(15 * S), fill=PINK, anchor="mm")
    d.text(((x0 + 12) * S, ((y0 + y1) / 2) * S), "POPULATION INFECTED  %d%%" % round(pct * 100), font=L.font(20 * S), fill=(255, 236, 244, 255), anchor="lm")
    L.chip(d, fx - 24, y1 + 26, "+%d%%/STEP" % rate, L.PINK8, 15, glyph=False, anchor="rm")
    return L.flatten(img, lay)


def main():
    base = load_base()
    prot = protect(base)
    D, _, _ = district_field()
    res = {"base": L.metrics(base)}
    os.makedirs(L.OUT, exist_ok=True)
    for name, (pct, rate) in LEVELS.items():
        out, thr, cover = render(base, prot, D, pct, rate)
        mt = L.metrics(out)
        out = gauge(out, pct, rate)
        L.save_png(out, os.path.join(L.OUT, name + ".png"))
        res[name] = dict(pct=pct, plate=mt, still=L.metrics(out), infected_area=round(float((cover > 0.5).sum() / ((MAP[2] - MAP[0]) * (MAP[3] - MAP[1]))), 3))
        print(name, res[name], flush=True)
    os.makedirs(L.SCRATCH, exist_ok=True)
    json.dump(res, open(os.path.join(L.SCRATCH, "raid_values.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
