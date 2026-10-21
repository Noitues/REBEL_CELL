"""Combat-wheel frame mockup (2D, PIL) over the graffiti street render. Concept only, not a UI change.

python graf_panel_combat.py <street_plate.png> <out.png>
Runs the round-41/44 combat screen builder (round41_wheel_stack/scripts, read-only) with its backdrop swapped for the
graffiti street plate (the art-deco panel used the same route), then repaints each wheel's frame as a throw-up ring on the
wall: black outline, fluoro gradient fill, white highlight dots, paint drips off the bottom, a few tags on the bezel. The
slices stay the CRT "Screens & Data" art and the live numbers stay bare Anton (ART_BIBLE 1.2).
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

P7 = r"D:/rc_art/art-pass/docs/concepts/round41_wheel_stack"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
sys.path.insert(0, P7 + "/scripts")
os.chdir(P7 + "/scripts")

import combat41 as C41  # noqa: E402
import graf_atlas as GA  # noqa: E402

W, H = 1920, 1080
S = 3


def street_backdrop(path):
    a = np.asarray(Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    pool = np.zeros((H, W), np.float32)
    for wh in (C41.PLAYER, C41.BOSS):
        q = np.hypot(xx - wh["c"][0], yy - wh["c"][1]) / (wh["r"] * 1.3)
        pool = np.maximum(pool, np.exp(-q ** 4))
    dim = 0.85 * (1 - 0.55 * pool)
    dim *= 1 - 0.5 * np.clip((yy - 800) / 260, 0, 1)
    soft = np.asarray(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(3.0)), np.float32)
    a = a * (1 - 0.6 * pool[..., None]) + soft * 0.6 * pool[..., None]
    return Image.fromarray(np.clip(a * dim[..., None], 0, 255).astype(np.uint8))


def ring_mask(cx, cy, r0, r1):
    m = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], fill=255)
    d.ellipse([cx - r0, cy - r0, cx + r0, cy + r0], fill=0)
    return m


def paint(layer, mask, col):
    layer.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", mask.size, col).split(), mask)))


def graf_wheel(img, c, r, c0, c1, seed):
    """the wheel frame as a throw-up ring: overspray halo, black outline, gradient fill, highlights, drips, tags."""
    rng = random.Random(seed)
    cx, cy, R = c[0] * S, c[1] * S, r * S
    layer = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    r0, r1 = R * 1.03, R * 1.17
    fill = ring_mask(cx, cy, r0, r1)
    # drips off the lower half of the ring
    dr = Image.new("L", fill.size, 0)
    dd = ImageDraw.Draw(dr)
    for _ in range(14):
        a = rng.uniform(0.15, 0.85) * math.pi        # lower half (y down)
        x, y = cx + math.cos(a) * r1 * 0.98, cy + math.sin(a) * r1 * 0.98
        L, w = rng.uniform(0.08, 0.35) * R, rng.uniform(0.010, 0.02) * R
        dd.line([(x, y - w), (x, y + L)], fill=255, width=int(w))
        dd.ellipse([x - w * 0.7, y + L - w * 0.5, x + w * 0.7, y + L + w], fill=255)
    fill = Image.fromarray(np.maximum(np.asarray(fill), np.asarray(dr)))
    outline = GA.dilate(fill, 0.035 * R)
    halo = GA.dilate(fill, 0.09 * R).filter(ImageFilter.GaussianBlur(0.06 * R))
    paint(layer, halo.point(lambda v: int(v * 0.5)), c1)
    paint(layer, outline, (8, 6, 12))
    light = GA.dilate(fill, 0.012 * R)
    paint(layer, light, (250, 250, 245))
    grad = GA.grad_fill(fill.size, c0, c1, rng)
    layer.alpha_composite(Image.merge("RGBA", (*grad.split(), fill)))
    hd = ImageDraw.Draw(layer)
    for _ in range(46):   # highlight dots and short cut lines on the ring
        a = rng.uniform(0, math.tau)
        rr = rng.uniform(r0 + 0.015 * R, r1 - 0.03 * R)
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        s = rng.uniform(0.006, 0.014) * R
        hd.ellipse([x - s, y - s, x + s, y + s], fill=(255, 255, 255, 235))
    # 30 tick notches as black paint slashes across the fill (the wheel's 30 ticks)
    for k in range(30):
        a = -math.pi / 2 + k * math.tau / 30
        w = int(0.010 * R) if k % 5 else int(0.018 * R)
        hd.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * (r0 + (r1 - r0) * (0.55 if k % 5 else 0.85)),
                                                                   cy + math.sin(a) * (r0 + (r1 - r0) * (0.55 if k % 5 else 0.85)))],
                fill=(8, 6, 12, 255), width=w)
    # two tags written over the upper bezel
    for k in range(2):
        tim, _ = GA.tag(rng, int(0.16 * R))
        a = -math.pi / 2 + rng.uniform(-0.9, 0.9)
        x, y = cx + math.cos(a) * r1 * 1.02 - tim.width / 2, cy + math.sin(a) * r1 * 1.02 - tim.height / 2
        layer.alpha_composite(tim, (int(x), int(y)))
    small = layer.resize((W, H), Image.LANCZOS)
    img.alpha_composite(small)


def main():
    plate, out = sys.argv[1], sys.argv[2]
    _orig = C41.base_plate
    _jpg = _orig()[1]
    bd = street_backdrop(plate)
    C41.base_plate = lambda: (bd, _jpg)
    import combat44 as C44
    shot, off, hits = C44.screen(False, hover=None)
    shot = shot.convert("RGBA")
    keep = shot.copy()
    graf_wheel(shot, C41.PLAYER["c"], C41.PLAYER["r"], (255, 61, 168), (176, 77, 255), 41)
    graf_wheel(shot, C41.BOSS["c"], C41.BOSS["r"], (255, 140, 26), (255, 40, 90), 44)
    # the HUD boxes the frame must never cover (cards row, HP plates, the SEND IT sticker): restored from the base screen
    for bx in ((1236, 726, 1602, 892), (370, 776, 570, 850), (1360, 860, 1790, 940)):
        shot.paste(keep.crop(bx), bx[:2])
    shot.convert("RGB").save(out)
    print("combat mockup", out, "off-screen %.1f" % off)


if __name__ == "__main__":
    main()
