"""Tethys THE WATER LEVEL, raid view with the Head gauge: R_head_HIGH (1920 x 1080), a 2D mock over the Grid capture.

Base: GRID_VIEW_current.jpg (read only). At HIGH the drowned quarter is a water sheet over a warped district field from
the Tethys source (bottom left); its shoreline is a bright 3 px line that sits further out than the RISING baseline
(a faint second ring). LOWER nodes inside the sheet (Compiler Rack, Vault Terminal, Proxy Relay) are dimmed to 55 %
with the waterline across the pin and the sealed-hatch glyph; UPPER nodes stay dry. Pins are drawn ABOVE the sheet, so
the water never hides a node. The tide gauge sits top left under the top bar. Rule: median of the map stays near the
Grid's (the sheet is abyss blue, not black).
Run:  python tethys_raid.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw

import solace_lib as L
import tethys_hq as TQ
import theme_lib as T

W, H = T.W, T.H
SRC = (300.0, 960.0)                      # the Tethys source district (bottom left of the map)
ABYSS = TQ.ABYSS
# raid nodes read off the Grid capture (output px): (x, y, role)
NODES = [(190, 790, "Home Server", "UPPER"), (180, 930, "Compiler Rack", "LOWER"), (300, 1010, "Vault Terminal", "LOWER"),
         (520, 940, "Proxy Relay", "LOWER"), (800, 850, "Relay", "UPPER"), (790, 690, "Firewall Relay", "UPPER"),
         (836, 497, "Safehouse", "UPPER"), (1435, 685, "Relay", "UPPER")]


def field():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = xx - SRC[0], yy - SRC[1]
    base = np.hypot(dx, 1.8 * dy)
    u = xx * 0.866 + yy * 0.5
    v = -xx * 0.5 + yy * 0.866
    warp = 140.0 * (L.fbm(u * 0.006, v * 0.025, 11, 4) + L.fbm(v * 0.006, u * 0.025, 13, 4) - 1.0)
    return base + warp, xx, yy


def render(step="HIGH"):
    base = T.grid_base()
    prot = T.grid_protect(base)
    mm = T.map_mask()
    D, xx, yy = field()
    # shoreline distances (the quantile of the map area that is wet at each Head)
    inmap = mm > 0.5
    qs = {"LOW": 0.18, "RISING": 0.30, "HIGH": 0.46, "FALLING": 0.36}
    thr = float(np.quantile(D[inmap], qs[step]))
    thr_base = float(np.quantile(D[inmap], qs["RISING"]))
    wet = L.smoothstep(thr + 12, thr - 12, D) * mm
    cover = wet * (1 - prot)
    # the water sheet: abyss tint over the districts, with a soft caustic shimmer; protected links and labels stay
    cau = 0.5 + 0.5 * np.sin(xx * 0.05 + 4 * L.fbm(xx * 0.012, yy * 0.012, 5, 3)) * np.sin(yy * 0.07 + 3 * L.fbm(yy * 0.01, xx * 0.01, 9, 3))
    tint = base * np.array([0.45, 0.75, 0.95], np.float32) * 0.9 + ABYSS * 1.4 + cau[..., None] * np.array([0.02, 0.07, 0.08], np.float32)
    out = base * (1 - 0.72 * cover[..., None]) + tint * (0.72 * cover[..., None])
    gy, gx = np.gradient(D)
    gm = np.sqrt(gx * gx + gy * gy) + 1e-3
    dist = np.abs(D - thr) / gm
    edge = np.clip(2.4 - dist, 0, 1) * mm * (1 - 0.7 * prot)
    out = out * (1 - edge[..., None] * 0.9) + (edge * 0.95)[..., None] * np.array([0.88, 1.0, 1.0], np.float32)
    if step in ("HIGH", "FALLING"):
        db = np.abs(D - thr_base) / gm
        e2 = np.clip(1.6 - db, 0, 1) * mm * (1 - 0.7 * prot) * 0.5
        out = out * (1 - e2[..., None] * 0.6) + (e2 * 0.7)[..., None] * np.array([0.55, 0.9, 1.0], np.float32)
    # keep the map median near the Grid base (the sheet is a tint, so only lift the dry part a touch if needed)
    tm = float(np.median(L.luma(base)))
    out = T.fit_median(out, tm, (1 - cover) * (1 - prot) * 0.5 + 0.0, tol=0.004)
    return np.clip(out, 0, 1), D, thr, wet


def pins(img, D, thr, step):
    lay = T.canvas()
    d = ImageDraw.Draw(lay)
    S = L.SS
    closed = step == "HIGH"
    for (x, y, name, lvl) in NODES:
        low = lvl == "LOWER"
        wetp = float(D[int(y), int(x)]) < thr
        drown = low and wetp
        col = (150, 255, 70)
        r = 24
        a = 255 if not (drown and closed) else 170
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=(6, 16, 28, 215), outline=col + (a,), width=3 * S)
        if drown and closed:
            d.ellipse([(x - r + 3) * S, (y - r + 3) * S, (x + r - 3) * S, (y + r - 3) * S], fill=(4, 20, 50, 110))
            d.line([((x - r - 4) * S, (y + 9) * S), ((x + r + 4) * S, (y + 9) * S)], fill=(225, 255, 255, 255), width=2 * S)
            TQ.sealed_hatch(d, x + 24, y - 26, 10)
        else:
            d.ellipse([(x - 6) * S, (y - 6) * S, (x + 6) * S, (y + 6) * S], fill=col + (255,))
        TQ.level_glyph(d, x - 24, y - 28, low, TQ.PHOTO8 + (255,) if low else (255, 190, 100, 255))
        T.text(d, x + r + 8, y + 2, name, 14, (230, 245, 245, 255))
    return T.flat(img, lay)


def main():
    od = T.out_dir("tethys")
    res = {}
    out, D, thr, wet = render("HIGH")
    res["map_with_theme"] = L.metrics(out)
    img = pins(out, D, thr, "HIGH")
    lay = TQ.gauge_layer("HIGH", x=70, y=118)
    d = ImageDraw.Draw(lay)
    T.chipbox(d, 330, 150, "SUBMERGED: LOWER NODES  TURRETS MUTED", TQ.PHOTO8 + (255,), 14, fill=(6, 12, 24, 230))
    T.chipbox(d, 330, 188, "SHORELINE  +HIGH  (faint ring = RISING)", (170, 210, 235, 255), 13, fill=(6, 12, 24, 230))
    img = T.flat(img, lay)
    T.save(img, os.path.join(od, "R_head_HIGH.png"))
    res["R_head_HIGH"] = L.metrics(img)
    res["base"] = L.metrics(T.grid_base())
    print(res, flush=True)


if __name__ == "__main__":
    main()
