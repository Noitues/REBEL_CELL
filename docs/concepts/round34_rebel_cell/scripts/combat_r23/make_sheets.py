"""Round 13 wheel frame sheets.

python make_sheets.py render [d1 d2 ...]   # wheel renders -> ../scratch/r (cached PNG + json)
python make_sheets.py sheets               # d1.png .. d4.png, compare.jpg
python make_sheets.py combat d3 d4         # combat_d3_d4 style screens (one per frame)
python make_sheets.py all
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
SCR = os.path.join(OUT, "scratch")
RC = os.path.join(SCR, "r")

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import frames as F
import combat_specs as CS
from slicelib import f_num, f_ui, f_mono, R_OUT

FRAMES = ["d1", "d2", "d3", "d4"]
W, H = 1920, 1080
BG = (16, 15, 22)
INK = (10, 8, 16)
TITLE = {
    "d1": ("D1  BLADE & WINDOW", "notched blade pointer carries the live value in its window; active slice lifted, outlined, the rest dimmed"),
    "d2": ("D2  INSTRUMENT READOUT", "long gauge needle on a hub collar, hub CRT reads the slice (second read), 30-tick scale, slice brackets"),
    "d3": ("D3  LAYERED STACK", "machined bezel over a recessed slice disc, glass, cast shadows; physical pointer, counterweight, split-flap value"),
    "d4": ("D4  LENS & RAIL  (my pick)", "D1 blade + window, D3-lite bezel and shadows, and the telemetry ring turns into the active slice's readout rail"),
}
ACC = {"d1": (255, 61, 168), "d2": (92, 225, 255), "d3": (200, 200, 210), "d4": (255, 214, 64)}
NOTES = {
    "d1": ["UNDER POINTER: value twice (blade window + slice), slice lifted",
           "  6% + cream outline; other slices dimmed to 66%.",
           "r=60: blade scaled x1.55 in LOD so the window still shows 12.",
           "BOSS EXTRAS:",
           " 1 nameplate banner IS the blade's mount (struts to bezel)",
           " 2 bolted armour band + corp crest lugs at 3 and 9 o'clock",
           " 3 crowned orange blade + red HITS YOU threat tab",
           " + phase pips on the HP arc (kept from round 11)"],
    "d2": ["UNDER POINTER: brackets + lit hairline on the slice, needle",
           "  tip on the 30-tick scale, hub CRT: name, glyph, value, pips.",
           "Needle is bold off-glass, a hairline across the screen, and",
           "  passes UNDER the glyph/value block. r=60: hub = value only.",
           "BOSS EXTRAS:",
           " 1 counter-rotating red threat ring with NEXT needle marks",
           " 2 hub readout turns hostile: ATK > YOU + corp watermark",
           " 3 ambient radar sweep across the face (corp colour)"],
    "d3": ["UNDER POINTER: pointer lamp spot-lights the slice, the rest",
           "  sit in the bezel's shadow (70%); split-flap shows the value.",
           "Depth: disc -6, bezel 0, hub +5, pointer +10, glass -14.",
           "BOSS EXTRAS:",
           " 1 riveted armour collar outside the machined bezel",
           " 2 embossed corp crest bosses at 3 and 9 o'clock",
           " 3 orange-anodised bezel + heavier pointer (+ phase pips)"],
    "d4": ["UNDER POINTER: value 3x - blade window, lifted slice, and the",
           "  telemetry rail (+-50 deg) in the slice colour:",
           "  'ZERO-DAY 12 // CRIT // PERFECT'. Others dimmed to 68%.",
           "r=60: rail = solid colour arc, hub shows HP (41).",
           "BOSS EXTRAS:",
           " 1 nameplate banner as the blade mount, crowned blade",
           " 2 counter-rotating threat ring + NEXT needle telegraphs",
           " 3 corp crest lugs on the threat ring (+ phase pips)"],
}


# ------------------------------------------------------------------ render cache
def spec(kind):
    if kind == "player":
        return CS.player(41, 14)[0]
    return CS.boss(340, 8)[0]


def cached(fr, kind, ss=2, lod=False, rot=0.0, tilt=0.0, hp_number=False, tag=None):
    os.makedirs(RC, exist_ok=True)
    name = tag or "%s_%s_%s%s" % (fr, kind, "lod" if lod else "hero", "_hp" if hp_number else "")
    p = os.path.join(RC, name + ".png")
    j = os.path.join(RC, name + ".json")
    if os.path.exists(p) and os.path.exists(j):
        m = json.load(open(j))
        return Image.open(p).convert("RGBA"), tuple(m["centre"]), m["meta"], m["ss"]
    im, c, meta = F.render(fr, spec(kind), ss=ss, lod=lod, rot=rot, tilt=tilt, hp_number=hp_number)
    im.save(p)
    json.dump(dict(centre=c, meta=meta, ss=ss), open(j, "w"))
    print("rendered", name, flush=True)
    return im, c, meta, ss


def render_all(which):
    for fr in which:
        for kind in ("player", "boss"):
            cached(fr, kind, hp_number=True)
            cached(fr, kind, lod=True)
            cached(fr, kind)          # combat (no HP number; the HUD draws it)
    if "d3" in which:
        parallax_frames()


PARALLAX = [(-1.0, -22.0, "SPIN  tilt L  (blur)"), (0.0, -7.0, "SLOWING  centred"), (1.0, 0.0, "LANDED  tilt R")]


def parallax_frames():
    out = []
    for k, (t, rot, lab) in enumerate(PARALLAX):
        im, c, meta, ss = cached("d3", "player", ss=1, rot=rot, tilt=t * 2.2, tag="d3_par%d" % k)
        out.append((im, c))
    return out


# ------------------------------------------------------------------ helpers
def fit(im, c, ss, r):
    return F.fit(im, c, ss, r)


def grey(im):
    g = ImageOps.grayscale(im.convert("RGB")).convert("RGBA")
    g.putalpha(im.split()[3])
    return g


def label(d, x, y, t, col=(200, 200, 212), size=17, anchor="la"):
    d.text((x, y), t, font=f_ui(size, b"Bold SemiCondensed"), fill=col, anchor=anchor)


def paste_c(sheet, im, cx, cy, c):
    sheet.alpha_composite(im, (int(cx - c[0]), int(cy - c[1])))


def place_box(sheet, im, c, ss, box, r_want, cy_frac=0.5):
    """Fit a wheel into box (x0,y0,x1,y1) at r_want, shrinking if needed; centre horizontally on the hub."""
    x0, y0, x1, y1 = box
    r = r_want
    while True:
        a, ac = fit(im, c, ss, r)
        left, right = ac[0], a.width - ac[0]
        if max(left, right) * 2 <= (x1 - x0) and a.height <= (y1 - y0):
            break
        r *= 0.96
    cx = (x0 + x1) / 2
    top = y0 + ((y1 - y0) - a.height) * cy_frac
    sheet.alpha_composite(a, (int(cx - ac[0]), int(top)))
    return r, (cx, top + ac[1]), a, ac


def backdrop_tile(w, h, seed=3):
    """A dim night-city strip so the wheels are judged on something like the real backdrop."""
    src = Image.open(os.path.join(OUT, "..", "..", "round11_combat_target", "target_building_night.png")).convert("RGB")
    rng = np.random.default_rng(seed)
    x = int(rng.integers(0, max(1, src.width - w)))
    y = int(rng.integers(0, max(1, src.height - h)))
    t = src.crop((x, y, x + w, y + h)).filter(ImageFilter.GaussianBlur(2.5))
    a = np.asarray(t, np.float32) * 0.42
    return Image.fromarray(a.astype(np.uint8)).convert("RGBA")


# ------------------------------------------------------------------ sheets
def sheet(fr):
    S = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(S)
    acc = ACC[fr]
    d.rectangle([0, 0, 8, 64], fill=acc)
    d.text((26, 6), TITLE[fr][0], font=f_num(46), fill=(255, 255, 255))
    d.text((26 + f_num(46).getlength(TITLE[fr][0]) + 24, 26), TITLE[fr][1], font=f_mono(17, False), fill=(185, 185, 200))
    # columns: A player hero, B boss, C close-up / small / grey / notes
    for (x0, x1) in ((10, 650), (660, 1290)):
        S.alpha_composite(backdrop_tile(x1 - x0, 1000, seed=x0 + len(fr)), (x0, 72))
    pim, pc, pmeta, pss = cached(fr, "player", hp_number=True)
    r, cen, a, ac = place_box(S, pim, pc, pss, (14, 100, 646, 1070), 220)
    label(d, 22, 80, "PLAYER  r=%d  (1080p hero size)" % round(r), (235, 235, 245))
    bim, bc, bmeta, bss = cached(fr, "boss", hp_number=True)
    rb, cenb, _, _ = place_box(S, bim, bc, bss, (664, 100, 1286, 1070), 220)
    label(d, 672, 80, "BOSS  THE MANIFEST  r=%d  (combat: r=236)" % round(rb), (235, 235, 245))
    # C: under-pointer close-up from the hero master
    cx0, cy0 = 1300, 72
    k = 0.62  # master-scale crop -> 0.62 x master = ~1.0 x hero ... shown at 1.85 x hero
    crop_w, crop_h = 610, 300
    big, bcen = fit(pim, pc, pss, 360 * k * 1.6)
    top_r = pmeta.get("top_r", R_OUT + 120)
    cy_c = bcen[1] - (R_OUT + 20) * k * 1.6 * 0.5 - (top_r - R_OUT) * k * 0.4
    box = (int(bcen[0] - crop_w / 2), int(bcen[1] - (top_r + 20) * k * 1.6), 0, 0)
    crop = big.crop((box[0], box[1], box[0] + crop_w, box[1] + crop_h))
    tile = backdrop_tile(crop_w, crop_h, 11)
    tile.alpha_composite(crop)
    S.alpha_composite(tile, (cx0, cy0 + 26))
    d.rectangle([cx0, cy0 + 26, cx0 + crop_w - 1, cy0 + 26 + crop_h - 1], outline=(70, 70, 84))
    label(d, cx0, cy0 + 2, "ACTIVE SLICE UNDER THE POINTER  (x%.1f of hero)" % (k * 1.6 * 360 / r), (235, 235, 245))
    # small r=60 + greyscale
    y_row = cy0 + 26 + crop_h + 12
    label(d, cx0, y_row, "r=60  PLAYER / BOSS  (LOD)", (235, 235, 245))
    label(d, cx0 + 330, y_row, "GREYSCALE  (hero frame)", (235, 235, 245))
    tile = backdrop_tile(320, 230, 21)
    S.alpha_composite(tile, (cx0, y_row + 24))
    for j, kind in enumerate(("player", "boss")):
        im, c, m, ss = cached(fr, kind, lod=True)
        place_box(S, im, c, ss, (cx0 + j * 160, y_row + 30, cx0 + 160 + j * 160, y_row + 250), 60)
    S.alpha_composite(backdrop_tile(280, 230, 31).convert("L").convert("RGBA"), (cx0 + 330, y_row + 24))
    place_box(S, grey(pim), pc, pss, (cx0 + 330, y_row + 28, cx0 + 610, y_row + 250), 110)
    # notes (+ d3 parallax strip)
    ny = y_row + 24 + 240
    if fr == "d3":
        label(d, cx0, ny, "PARALLAX WHILE SPINNING  (depth x tilt, shown x2.2)", (235, 235, 245))
        fx = cx0
        for kk, (t, rot, lab) in enumerate(PARALLAX):
            im, c, m, ss = cached("d3", "player", ss=1, rot=rot, tilt=t * 2.2, tag="d3_par%d" % kk)
            sm, scn = fit(im, c, 1, 64)
            if kk == 0:
                sm = spin_blur(sm, scn, 64)
            tile = backdrop_tile(198, 198, 40 + kk)
            S.alpha_composite(tile, (fx, ny + 24))
            paste_c(S, sm, fx + 99, ny + 24 + 18 + (180 - sm.height) / 2 + scn[1], scn)
            label(d, fx + 4, ny + 26, lab, (255, 220, 120), 14)
            fx += 205
        ny += 236
    for i, ln in enumerate(NOTES[fr]):
        d.text((cx0, ny + 4 + i * 21), ln, font=f_mono(16, False), fill=(255, 220, 120) if ln.startswith("BOSS") else (205, 205, 218))
    S.convert("RGB").save(os.path.join(OUT, fr + ".png"))
    print("sheet", fr, flush=True)


def spin_blur(im, c, r):
    """Rotational blur on the slice disc only (fast spin)."""
    acc = np.zeros((im.height, im.width, 4), np.float32)
    n = 9
    for k in range(n):
        a = (k - n // 2) * 1.6
        acc += np.asarray(im.rotate(a, resample=Image.BICUBIC, center=c), np.float32)
    acc /= n
    yy, xx = np.mgrid[0:im.height, 0:im.width]
    rho = np.hypot(xx - c[0], yy - c[1]) / r * R_OUT
    m = ((rho > 132) & (rho < R_OUT - 8)).astype(np.float32)[..., None]
    base = np.asarray(im, np.float32)
    out = base * (1 - m) + acc * m
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def compare():
    S = Image.new("RGBA", (W, 1000), BG + (255,))
    d = ImageDraw.Draw(S)
    d.text((20, 6), "ROUND 13  WHEEL FRAMES  -  heroes (top) and bosses (bottom)", font=f_num(40), fill=(255, 255, 255))
    for i, fr in enumerate(FRAMES):
        x0 = 10 + i * 477
        S.alpha_composite(backdrop_tile(467, 920, 50 + i), (x0, 60))
        im, c, m, ss = cached(fr, "player", hp_number=True)
        place_box(S, im, c, ss, (x0 + 4, 100, x0 + 463, 520), 150)
        im, c, m, ss = cached(fr, "boss", hp_number=True)
        place_box(S, im, c, ss, (x0 + 4, 540, x0 + 463, 975), 150)
        label(d, x0 + 8, 66, TITLE[fr][0], ACC[fr] if fr != "d3" else (230, 230, 240), 22)
    S.convert("RGB").save(os.path.join(OUT, "compare.jpg"), quality=90)
    print("compare", flush=True)


# ------------------------------------------------------------------ combat
def combat(fr):
    import make_combat as MC
    os.makedirs(MC.CACHE, exist_ok=True)
    for key, kind in (("player_b", "player"), ("boss", "boss")):
        im, c, meta, ss = cached(fr, kind)
        k = 1.0 / ss
        im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
        im.save(os.path.join(MC.CACHE, key + ".png"))
        with open(os.path.join(MC.CACHE, key + ".txt"), "w") as f:
            f.write("%d %d" % (c[0] * k, c[1] * k))
        MC.META[key] = dict(hp_r=meta["hp_r"], ptr_r=meta["ptr_r"])
    MC.SAVE_NAME = "combat_%s.png" % fr
    MC.compose("boss", "night")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    args = sys.argv[2:] or FRAMES
    if what in ("render", "all"):
        render_all(args if what == "render" else FRAMES)
    if what in ("sheets", "all"):
        for fr in (args if what == "sheets" else FRAMES):
            sheet(fr)
        compare()
    if what == "combat":
        for fr in args:
            combat(fr)
    print("done")
