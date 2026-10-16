"""Q6 decision sheet: the hover power cut, CURRENT vs one ALTERNATIVE, on the approved storyboard hover holds.

Re-composes the storyboard frames exactly as sb_ocfull.compose does (same plates, same UI), swapping only the 2D world
grade's hover cut (sb_ui.route_grade). CPU only; reads the storyboard scratch, writes only into decisions/.

python q6_power_cut.py -> ../Q6_power_cut.png (+ ../Q6_power_cut.json)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
RMG = os.path.dirname(os.path.dirname(HERE))
SBS = os.path.join(RMG, "storyboard", "scripts")
sys.path.insert(0, HERE)
sys.path.insert(1, SBS)
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import sheetlib as L  # noqa: E402
import sb_ocfull as OF  # noqa: E402
import sb_ui as U  # noqa: E402

OUT = os.path.dirname(HERE)

# The cut levels. CURRENT is what the approved storyboard ships (sb_ui.route_grade): outside x0.62, 25 % desaturated,
# the branch rooms keep their value and get a 0.5 type-colour glow. (Spec 9.4 lists V3 dynamic's 32 % / 40 % and the HQ's
# 3D 22 % + 2D 0.62; the one-city storyboard renders no 3D cut, so 0.62 is the whole cut there.)
LEVELS = {
    "none": None,
    "current": dict(level=0.62, desat=0.25, boost=1.00, glow=0.5),
    "alt": dict(level=0.20, desat=0.70, boost=1.35, glow=1.0),
}
MODE = {"k": "current"}
MASKS = {}


def route_grade(plate, A, st, cur, hover, hk, focus):
    """sb_ui.route_grade with the hover cut parameterised (everything before the cut is unchanged)."""
    P = LEVELS[MODE["k"]]
    W, H = U.W, U.H
    out = np.asarray(plate.convert("RGB"), np.float32) / 255.0
    br = U.G.branch(hover)[0] if hover else set()
    from PIL import ImageFilter
    dm = Image.new("L", (W, H), 0)
    dd = ImageDraw.Draw(dm)
    for e in A["edges"]:
        pts = [tuple(q) for q in e["pts"] if q is not None]
        if len(pts) > 1:
            dd.line(pts, fill=255, width=10)
    dm = np.asarray(dm.filter(ImageFilter.GaussianBlur(24)), np.float32) / 255.0
    out = out * (1 - 0.2 * np.clip(dm * 2.0, 0, 1))[..., None]
    if focus > 0:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dd_ = np.sqrt(((xx - U.R.UCX) / (W * 0.62)) ** 2 + ((yy - U.R.UCY) / (H * 0.62)) ** 2)
        out = out * (1 - 0.18 * np.clip(dd_ - 0.55, 0, 1)[..., None] * focus)
    keep = np.zeros((H, W), np.float32)
    if hover:
        for i in sorted(br | {cur}):
            p = U.C3.room_poly(A, i)
            if p:
                keep = np.maximum(keep, U.C3.poly_mask(p, grow=8, blur=8))
        MASKS["keep"] = keep
    if P and hover and hk > 0:
        l3 = (out[..., 0] * 0.3 + out[..., 1] * 0.59 + out[..., 2] * 0.11)[..., None]
        dim = (out * (1 - P["desat"]) + l3 * P["desat"]) * P["level"]
        cut = out * (1 - hk) + dim * hk
        lit = out * (1 + (P["boost"] - 1) * hk)
        out = lit * keep[..., None] + cut * (1 - keep[..., None])
    img = Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    if P and hover and hk > 0.05:
        for i in sorted(br, key=lambda n: (U.G.LAYER[n], U.G.K[n])):
            p = U.C3.room_poly(A, i)
            if p:
                m = Image.fromarray((U.C3.poly_mask(p) * 255).astype(np.uint8))
                img = U.K.add_glow(img, m, U.S.TYPE_COL[U.G.KIND[i]], 30, P["glow"] * hk)
    return img


U.route_grade = route_grade

FRAMES = [("HOVER OPTION 1 (Fight, L1)", 530), ("HOVER OPTION 2 (held hover moved)", 600)]
COLS = [("none", "NO CUT  (reference)", "the same frame with the cut switched off", L.DIM),
        ("current", "CURRENT  (approved storyboard)", "outside x0.62, 25 % desat; branch x1.0 + type glow 0.5", L.ORANGE),
        ("alt", "ALTERNATIVE  (blackout, route glows)", "outside x0.20, 70 % desat; branch x1.35 + type glow 1.0", L.LIME)]


def main():
    res = {}
    for name, f in FRAMES:
        for k, *_ in COLS:
            MODE["k"] = k
            OF._RU.clear() if hasattr(OF, "_RU") else None
            img = OF.compose(f, (1920, 1080)).convert("RGB")
            keep = MASKS.get("keep")
            y = L.luma(np.asarray(img))
            s = dict(L.stats(np.asarray(img)))
            if keep is not None:
                inside, outside = keep > 0.5, keep < 0.05
                s["branch_mean"] = float(y[inside].mean())
                s["outside_mean"] = float(y[outside].mean())
                s["outside_chroma"] = float(np.asarray(img, np.float32)[outside].std(axis=1).mean() / 255)
            res[(name, k)] = (img, s)
            print(name, k, {a: round(b, 3) for a, b in s.items()}, flush=True)

    Wd = 2400
    PAD = 14
    cw = (Wd - 2 * PAD - 2 * 10) // 3
    ch = round(cw * 9 / 16)
    head = 300
    rowh = ch + 110
    foot = 340
    sheet = Image.new("RGB", (Wd, head + rowh * len(FRAMES) + foot), L.BG)
    d = ImageDraw.Draw(sheet)
    f_t, f_h, f_b, f_s, f_m = L.font(44, True), L.font(26, True), L.font(22), L.font(19), L.font(20, mono=True)
    d.text((PAD + 10, 18), "Q6  HOVER POWER CUT  -  the current level and one alternative", font=f_t, fill=L.INK)
    L.para(d, (PAD + 10, 80),
           "Hovering an option dims everything outside the hovered branch (and the current room) so the branch reads as the "
           "one live route. These are the approved storyboard hover holds (frames 530 and 600), re-composed with the same "
           "plates and UI; only the 2D cut changes. Numbers under each frame: mean luma of the branch rooms and of the "
           "rest of the frame, and the frame median. The cut runs on the hover ease (0.30 s in, 0.35 s out) either way.",
           f_b, Wd - 40, fill=L.DIM)
    for c, (k, lab, sub, col) in enumerate(COLS):
        x = PAD + c * (cw + 10)
        d.text((x, 196), lab, font=f_h, fill=col)
        d.text((x, 234), sub, font=f_s, fill=L.DIM)
    y = head
    for name, f in FRAMES:
        for c, (k, *_r) in enumerate(COLS):
            x = PAD + c * (cw + 10)
            img, s = res[(name, k)]
            sheet.paste(img.resize((cw, ch), Image.LANCZOS), (x, y))
            col = COLS[c][3]
            d.rectangle((x, y, x + cw - 1, y + ch - 1), outline=col, width=2)
            if c == 0:
                d.text((x + 10, y + 8), name, font=f_h, fill=L.INK, stroke_width=3, stroke_fill=(0, 0, 0))
            ratio = s["branch_mean"] / max(1e-4, s["outside_mean"])
            d.text((x + 4, y + ch + 8), "branch %.3f   outside %.3f   ratio %.1fx" % (s["branch_mean"], s["outside_mean"], ratio),
                   font=f_m, fill=L.INK)
            d.text((x + 4, y + ch + 36), "frame median %.3f   <0.10 %4.1f %%" % (s["median"], s["under"] * 100), font=f_m, fill=L.DIM)
        y += rowh
    d.line((PAD, y, Wd - PAD, y), fill=(60, 60, 75), width=2)
    y += 18
    d.text((PAD + 10, y), "WHY THIS ALTERNATIVE", font=f_h, fill=L.INK)
    L.para(d, (PAD + 10, y + 40),
           "The current cut is already the gentle end: at x0.62 the city keeps most of its colour, and in motion the hover "
           "reads mostly through the camera ease, the tag and the pencil, not through the light. A gentler 'keep colour, "
           "desaturate only the city' option would sit almost on top of it. The useful comparison is the other end: a "
           "near-blackout where the branch is the only lit thing on screen, as ROUTE_REQUIREMENTS 2 describes "
           "('everything outside dims, the branch lights'). It also shows the cost: the city's neon, the reason the street "
           "looks expensive, goes away for as long as the cursor rests on an option.",
           f_b, Wd / 2 - 60, fill=L.INK)
    rx = Wd / 2 + 20
    d.text((rx, y), "RECOMMENDATION", font=f_h, fill=L.LIME)
    L.para(d, (rx, y + 40),
           "Take the ALTERNATIVE level, as one value for street and HQ: outside x0.20 with 70 % desaturation, the branch "
           "x1.35 with the type glow at 1.0. On these frames the branch-to-rest ratio goes from about 3x to 6x (the rest "
           "includes the UI panels) and the hovered route is the only colour left, which is the job of a hover. The cost "
           "is brief: the cut lasts only while the cursor rests and eases out in 0.35 s, and the pink street lanes still "
           "show through. Make it a preset value (hover.cut_level, hover.cut_desat, hover.branch_boost) so playtest can "
           "ease it toward x0.35 if it feels harsh, and run it as one 2D grade in Godot on both pages (drop the separate "
           "3D 22 % cut at the HQ). Hover frames stay exempt from the value band (12.1).",
           f_b, Wd / 2 - 50, fill=L.INK)
    sheet.save(os.path.join(OUT, "Q6_power_cut.png"), optimize=True)
    json.dump({"%s|%s" % k: v[1] for k, v in res.items()}, open(os.path.join(OUT, "Q6_power_cut.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
