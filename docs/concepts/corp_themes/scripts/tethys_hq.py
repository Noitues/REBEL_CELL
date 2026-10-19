"""Tethys THE WATER LEVEL, HQ stills (1920 x 1080): H_dec_{LOW,RISING,HIGH,FALLING}, H_ov_LOW, H_ov_HIGH.

Over the hq_tethys v2 plates (read only). The camera is fitted from the rooms json and the Z pass gives every pixel a
world position (tethys_lib), so the water plane is composited at its true Head height (LOW +0.6, RISING +2.5,
HIGH +5.0, FALLING +3.2 BU over the dry street; the plates have the RISING baseline baked in):
  * the water surface keeps its place (it is already the baseline plane) but its caustics follow the Head (x0.5 / 1 /
    0.7 / 0.9) and it takes foam at the dam toe when HIGH / FALLING;
  * every pixel of the drowned quarter between the baseline and the new height goes under (abyss tint, windows shift
    to cyan-green); at LOW the band between the new height and the baseline is shown dry (warm lift);
  * the dam face carries the tide: a thin white-cyan waterline at the true height, wet tint below it (HIGH), the
    darker tide-mark band above it (FALLING), dry concrete (LOW);
  * LOWER rooms are drowned and sealed at HIGH: dimmed to 55 %, abyss tint, red sealed-hatch glyph. They never vanish.
Run:  python tethys_hq.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw

import solace_lib as L
import theme_lib as T
import tethys_lib as TL

W, H = T.W, T.H
CORP = "tethys"
ABYSS = np.array([0.02, 0.10, 0.20], np.float32)
PHOTO8 = (124, 242, 228)                 # photophore #7CF2E4
TRENCH8 = (6, 17, 42)                    # trench #06112A
ABYSS8 = (40, 120, 200)
RED8 = (200, 38, 78)
SEQ = ["LOW", "RISING", "HIGH", "FALLING"]
STATION = (-348.0, 294.0)


def radial(sc):
    return np.hypot(sc.wx - STATION[0], sc.wy - STATION[1])


def apply_head(sc, step, seed=3):
    h = TL.HEAD[step]
    P = sc.plate.copy()
    Hh, Ww = P.shape[:2]
    wz = np.nan_to_num(sc.wz, nan=-999.0)
    wz = np.where(sc.valid, wz, -999.0)
    r = radial(sc)
    r = np.where(sc.valid, r, 1e4)
    surf = sc.valid & (np.abs(wz - TL.BASE_WATER) < 0.3) & (r < 93)
    dam = sc.valid & (r >= 90) & (r <= 101) & (wz > -1) & (wz < 14)
    quarter = sc.valid & (r < 93) & ~surf
    lum = L.luma(P)
    yy, xx = np.mgrid[0:Hh, 0:Ww].astype(np.float32)
    out = P.copy()
    # caustics follow the Head
    ck = {"LOW": 0.5, "RISING": 1.0, "HIGH": 0.7, "FALLING": 0.9}[step]
    hi = P - np.stack([L.boxblur(P[..., c], 5, 1) for c in range(3)], -1)
    sm = L.blur(surf.astype(np.float32), 2.0)[..., None]
    out = out + (ck - 1.0) * hi * sm
    if step == "LOW":
        out = out * (1 - 0.10 * sm)
    if step == "HIGH":
        out = out * (1 - 0.08 * sm) + 0.05 * sm * ABYSS[None, None, :]
    # structures going under (HIGH / FALLING): baseline < z < h
    if h > TL.BASE_WATER + 0.05:
        band = (quarter | dam) & (wz > TL.BASE_WATER + 0.25) & (wz < h)
        k = np.clip((h - wz) / 3.0, 0, 1) * 0.30 + 0.45
        k = k * band
        win = np.clip((lum - 0.25) / 0.5, 0, 1)[..., None]
        tinted = out * np.array([0.45, 0.8, 0.85], np.float32)[None, None, :] * 0.8 + ABYSS[None, None, :] * 0.5
        tinted = tinted * (1 - 0.0 * win) + win * (out * np.array([0.35, 1.0, 0.8], np.float32)[None, None, :] * 0.7)
        kk = L.blur(k.astype(np.float32), 1.2)[..., None]
        out = out * (1 - kk) + tinted * kk
    wetf = dam & (wz > -1) & (wz < h)
    kw = L.blur(wetf.astype(np.float32), 1.0)[..., None] * (0.30 + 0.25 * np.clip((h - wz) / 5.0, 0, 1)[..., None])
    out = out * (1 - kw) + (out * np.array([0.55, 0.85, 1.0], np.float32)[None, None, :] * 0.8 + ABYSS[None, None, :] * 0.35) * kw
    # LOW: the band between the new height and the baseline is dry (warm concrete lift)
    if h < TL.BASE_WATER - 0.05:
        dryb = (quarter | dam) & (wz > h) & (wz < TL.BASE_WATER - 0.1)
        kd = L.blur(dryb.astype(np.float32), 1.2)[..., None] * 0.45
        warm = out * np.array([1.30, 1.12, 0.92], np.float32)[None, None, :] + 0.02
        out = out * (1 - kd) + warm * kd
    # dam face: tide mark band above the water (FALLING), wet sheen below
    if step == "FALLING":
        tide = dam & (wz >= h) & (wz < h + 1.4)
        kt = L.blur(tide.astype(np.float32), 1.0)[..., None] * 0.6
        out = out * (1 - kt) + (out * np.array([0.62, 0.55, 0.45], np.float32)[None, None, :]) * kt
    # the waterline: the only place where warm meets cool. White-cyan, 2 px, with a 5 px soft meniscus
    gz, gx_ = np.gradient(wz)
    steep = (np.hypot(gz, gx_) > 0.03) & (np.hypot(gz, gx_) < 3.0)
    ln = np.exp(-((wz - h) / 0.30) ** 2) * (dam | quarter) * sc.valid * (~surf) * steep * (np.abs(wz - TL.BASE_WATER) > 0.3 if h == TL.BASE_WATER else 1.0)
    ln = np.clip(ln, 0, 1)
    glow = L.blur(ln.astype(np.float32), 3.0)
    out = out + (glow * 0.35)[..., None] * np.array([0.7, 1.0, 1.0], np.float32)[None, None, :]
    out = out * (1 - ln[..., None] * 0.9) + (ln * 0.95)[..., None] * np.array([0.88, 1.0, 1.0], np.float32)[None, None, :]
    # foam at the dam toe, HIGH and FALLING
    if step in ("HIGH", "FALLING"):
        fn = L.fbm(xx * 0.03, yy * 0.12, seed, 3)
        foam = surf * (r > 84) * L.smoothstep(0.55, 0.75, fn) * (0.5 if step == "HIGH" else 0.3)
        out = out + foam[..., None] * np.array([0.8, 0.95, 1.0], np.float32)[None, None, :] * 0.5
    return np.clip(out, 0, 1), h


def gauge_layer(step, x=44, y=112):
    """Vertical tide gauge: NOW + next 3 Head steps (22 x 150 px column, 4 cells), photophore NOW outline."""
    S = L.SS
    lay = T.canvas()
    d = ImageDraw.Draw(lay)
    cw, ch = 46, 40
    i0 = SEQ.index(step)
    d.rectangle([x * S, y * S, (x + cw + 150) * S, (y + 4 * ch + 36) * S], fill=(6, 12, 24, 215), outline=(90, 150, 190, 235), width=S)
    T.text(d, x + 10, y + 16, "HEAD", 15, PHOTO8 + (255,))
    for k in range(4):
        st = SEQ[(i0 + k) % 4]
        a = (255, 200, 150, 110)[k]
        cy0 = y + 32 + k * ch
        col = (ABYSS8 if k else PHOTO8) + (a if k else 255,)
        d.rectangle([(x + 8) * S, cy0 * S, (x + cw) * S, (cy0 + ch - 3) * S], fill=TRENCH8 + (255,), outline=(PHOTO8 if k == 0 else (60, 90, 120)) + (255,), width=(2 if k == 0 else 1) * S)
        # wave profile glyph, 30 px wide
        gx0, gy0 = x + 14, cy0 + ch / 2 - 1
        shape = {"LOW": [0.35, 0.35, 0.35, 0.35], "RISING": [0.2, 0.35, 0.6, 0.85], "HIGH": [0.85, 0.7, 0.9, 0.85], "FALLING": [0.85, 0.6, 0.35, 0.2]}[st]
        pts = [(gx0 + i * 10, gy0 + 9 - v * 18) for i, v in enumerate(shape)]
        d.line([(px * S, py * S) for px, py in pts], fill=col, width=2 * S)
        T.text(d, x + cw + 10, cy0 + ch / 2 - 1, st, 14 if k else 17, (235, 250, 250, a if k else 255))
        if st == "FALLING":
            d.polygon([((x + cw - 12) * S, (cy0 + 12) * S), ((x + cw - 4) * S, (cy0 + 12) * S), ((x + cw - 8) * S, (cy0 + 20) * S)], fill=(255, 255, 255, a))
    return lay


def sealed_hatch(d, cx, cy, r):
    S = L.SS
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=(24, 4, 10, 245), outline=RED8 + (255,), width=2 * S)
    d.line([((cx - r * 0.7) * S, cy * S), ((cx + r * 0.7) * S, cy * S)], fill=RED8 + (255,), width=3 * S)
    d.ellipse([(cx - r * 0.38) * S, (cy - r * 0.38) * S, (cx + r * 0.38) * S, (cy + r * 0.38) * S], outline=RED8 + (255,), width=S)


def level_glyph(d, cx, cy, lower, col):
    S = L.SS
    if lower:
        for k in range(2):
            pts = [(cx - 8 + i * 4, cy + k * 4 + (2 if i % 2 else -2)) for i in range(5)]
            d.line([(x * S, y * S) for x, y in pts], fill=col, width=int(1.6 * S))
    else:
        d.polygon([((cx) * S, (cy - 5) * S), ((cx + 6) * S, (cy + 4) * S), ((cx - 6) * S, (cy + 4) * S)], outline=col, width=int(1.6 * S))


# decision-view route pins (mapped from the composed v2 still to the nearest room anchor) and links
DEC_PINS = {"fist": "lock", "cw": "cw_mid", "w1": "outer_0", "e1": "inner_0", "f1": "mid_0", "g1": "main_deck", "d2": "deck_2",
            "d4": "deck_4", "tg": "vent_cap", "s1": "inner_1", "e2": "outer_1"}
DEC_LINKS = [("fist", "cw", "walked"), ("cw", "w1", "walked"), ("w1", "e1", "next"), ("w1", "f1", "next"), ("e1", "g1", "ahead"),
             ("e1", "d2", "ahead"), ("d2", "d4", "ahead"), ("d4", "tg", "ahead"), ("f1", "s1", "ahead"), ("s1", "e2", "ahead")]
COL = {"walked": (150, 255, 70), "next": (255, 150, 30), "ahead": (235, 235, 245)}


def pins_layer(sc, step, view):
    S = L.SS
    k = 0.75
    lay = T.canvas()
    d = ImageDraw.Draw(lay)
    closed = step == "HIGH"
    if view == "dec":
        pos = {n: tuple(v * k for v in sc.px(rn)) for n, rn in DEC_PINS.items()}
        for a, b, st in DEC_LINKS:
            lower = (DEC_PINS[b] in TL.LOWER) and closed
            col = COL[st] + (255,)
            if st == "ahead":
                T.pattern_line(d, [pos[a], pos[b]], col if not lower else (120, 140, 160, 200), 3, "dashed", dash=(14, 8))
            else:
                T.pattern_line(d, [pos[a], pos[b]], col, 5, "solid")
        for n, rn in DEC_PINS.items():
            x, y = pos[n]
            lower = rn in TL.LOWER
            st = "walked" if n in ("fist", "cw", "w1") else ("next" if n in ("e1", "f1") else "ahead")
            col = COL[st]
            r = 24
            drown = lower and closed
            d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=(8, 16, 26, 235), outline=col + (255 if not drown else 150,), width=4 * S)
            if drown:
                d.ellipse([(x - r + 3) * S, (y - r + 3) * S, (x + r - 3) * S, (y + r - 3) * S], fill=(4, 20, 50, 150))
                sealed_hatch(d, x + 20, y - 22, 10)
                # the waterline across the pin at its base
                d.line([((x - r) * S, (y + 8) * S), ((x + r) * S, (y + 8) * S)], fill=(225, 255, 255, 255), width=2 * S)
            else:
                d.ellipse([(x - 6) * S, (y - 6) * S, (x + 6) * S, (y + 6) * S], fill=col + (255,))
            level_glyph(d, x - 20, y - 26, lower, PHOTO8 + (255,) if lower else (255, 190, 100, 255))
    else:
        for rn, v in sc.rooms.items():
            x, y = v["px"][0] * k, v["px"][1] * k
            if not (20 < x < W - 20 and 20 < y < H - 20):
                continue
            lower = rn in TL.LOWER
            drown = lower and closed
            col = (235, 235, 245) if not drown else (130, 150, 175)
            r = 8
            d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=(8, 16, 26, 230), outline=col + (255,), width=2 * S)
            if drown:
                d.line([((x - 5) * S, y * S), ((x + 5) * S, y * S)], fill=RED8 + (255,), width=2 * S)
            if lower:
                level_glyph(d, x + 14, y - 12, True, PHOTO8 + (230,))
    return lay


def finish(view, step, name):
    sc = TL.Scene(view)
    if view == "dec":      # the decision Z pass is not planar enough to place the water plane (see the report): pins and gauge only
        out, h = sc.plate.copy(), TL.HEAD[step]
    else:
        out, h = apply_head(sc, step)
    plate_m = L.metrics(out)
    img = np.asarray(Image.fromarray((out * 255 + 0.5).astype(np.uint8)).resize((W, H), Image.LANCZOS), np.float32) / 255.0
    plate_m = L.metrics(img)
    img = T.flat(img, pins_layer(sc, step, view))
    lay = gauge_layer(step)
    d = ImageDraw.Draw(lay)
    T.chipbox(d, 44, 82, "WATER %+.1f BU   %s" % (h, "SEALED: LOWER ROOMS DROWNED" if step == "HIGH" else ("OPEN" if step != "FALLING" else "OPEN  EBB")), PHOTO8 + (255,), 15, fill=(6, 12, 24, 230))
    img = T.flat(img, lay)
    T.save(img, os.path.join(T.out_dir(CORP), name + ".png"))
    return dict(plate=plate_m, still=L.metrics(img))


def main(which="all"):
    res = {}
    jobs = [("ov", s, "H_ov_" + s) for s in SEQ] + [("dec", "LOW", "H_dec_LOW"), ("dec", "HIGH", "H_dec_HIGH")]
    for view, step, name in jobs:
        if which != "all" and name not in which:
            continue
        res[name] = finish(view, step, name)
        print(name, res[name], flush=True)
    return res


if __name__ == "__main__":
    main(sys.argv[1].split(",") if len(sys.argv) > 1 else "all")
