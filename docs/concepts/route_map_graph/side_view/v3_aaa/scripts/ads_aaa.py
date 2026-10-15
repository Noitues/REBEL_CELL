"""V3 AAA: our own ad art for the billboards, blade signs and holo panels (CRITIQUE §3 #7). Seeded, PIL only.

python ads_aaa.py  ->  ../scratch/ads/<name>.png
Every word and mark is ours: the four corps (Meridian, Solace, Halcyon, Orbital, emblems from emblems20.py) and invented
products. Colours stay in the district pair (magenta / cyan) plus violet and red: no lime, route orange or pencil yellow.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import ui31 as K  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "scratch", "ads")
EMB = os.path.join(os.path.dirname(HERE), "scratch", "emblems")
MAG, CYA, VIO, RED, PALE = (255, 42, 138), (42, 212, 255), (138, 61, 255), (255, 42, 42), (230, 225, 245)


def grad(w, h, top, bot):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bot)))
    return im


def emblem(name, px, col):
    a = Image.open(os.path.join(EMB, name + ".png")).convert("RGBA").split()[3].resize((px, px), Image.LANCZOS)
    im = Image.new("RGBA", (px, px), col + (255,))
    im.putalpha(a)
    return im


def text(im, xy, s, font, size, col, anchor="la"):
    d = ImageDraw.Draw(im)
    d.text(xy, s, font=K.F(font, size), fill=col, anchor=anchor)


def frame(im, col, w=10):
    d = ImageDraw.Draw(im)
    d.rectangle((w // 2, w // 2, im.width - w // 2, im.height - w // 2), outline=col, width=w)


def glowify(im, k=0.5, r=10):
    """Add a soft glow of the art onto itself (screen light bleeding into the panel)."""
    import numpy as np
    g = np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32)
    return Image.fromarray(np.clip(np.asarray(im, np.float32) + k * g, 0, 255).astype(np.uint8))


def ad_solace():
    im = grad(1024, 576, (40, 6, 40), (8, 2, 18))
    d = ImageDraw.Draw(im)
    cx, cy = 760, 300
    for k in range(10):
        a = 2 * math.pi * k / 10
        pts = [(cx, cy), (cx + 170 * math.cos(a - 0.22), cy + 170 * math.sin(a - 0.22) * 0.7),
               (cx + 230 * math.cos(a), cy + 230 * math.sin(a) * 0.7), (cx + 170 * math.cos(a + 0.22), cy + 170 * math.sin(a + 0.22) * 0.7)]
        d.polygon(pts, outline=MAG, width=4)
    d.ellipse((cx - 46, cy - 46, cx + 46, cy + 46), fill=MAG)
    im.paste(emblem("solace", 120, PALE), (60, 50), emblem("solace", 120, PALE))
    text(im, (60, 210), "SLEEP IS A", K.ANTON, 84, PALE)
    text(im, (60, 300), "PRESCRIPTION", K.ANTON, 84, MAG)
    text(im, (64, 430), "SOLACE DOSE+  //  ASK YOUR CLINIC", K.MONO, 28, (210, 180, 230))
    frame(im, MAG)
    return glowify(im)


def ad_halcyon():
    im = grad(1024, 576, (0, 24, 40), (0, 6, 14))
    d = ImageDraw.Draw(im)
    for k in range(9):
        y = 120 + k * 42
        d.line([(560, y), (1000, y - 120)], fill=CYA, width=3)
    im.paste(emblem("halcyon", 150, CYA), (790, 360), emblem("halcyon", 150, CYA))
    text(im, (60, 70), "HALCYON", K.ANTON, 120, CYA)
    text(im, (60, 230), "CLEAN AIR.", K.ANTON, 76, PALE)
    text(im, (60, 315), "CLEAN BLOOD.", K.ANTON, 76, PALE)
    text(im, (64, 460), "FILTER MASKS  ·  LUNG PLANS  ·  24H", K.MONO, 28, (160, 220, 235))
    frame(im, CYA)
    return glowify(im)


def ad_orbital():
    im = grad(1024, 576, (14, 6, 40), (2, 2, 10))
    d = ImageDraw.Draw(im)
    cx, cy = 740, 290
    d.ellipse((cx - 120, cy - 120, cx + 120, cy + 120), outline=CYA, width=6)
    for k, (rx, ry, rot) in enumerate(((230, 70, -0.3), (260, 90, 0.4), (200, 50, 1.1))):
        pts = []
        for t in range(73):
            a = 2 * math.pi * t / 72
            x, y = rx * math.cos(a), ry * math.sin(a)
            pts.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
        d.line(pts, fill=VIO if k % 2 else MAG, width=4)
    im.paste(emblem("orbital", 110, PALE), (60, 50), emblem("orbital", 110, PALE))
    text(im, (60, 190), "THE SKY", K.ANTON, 96, PALE)
    text(im, (60, 300), "IS LEASED", K.ANTON, 96, CYA)
    text(im, (64, 440), "ORBITAL  LEO-9  //  NOW BOOKING", K.MONO, 28, (190, 200, 240))
    frame(im, VIO)
    return glowify(im)


def ad_meridian():
    im = grad(1024, 576, (34, 4, 22), (6, 2, 8))
    d = ImageDraw.Draw(im)
    for k in range(4):
        x0 = 560 + k * 105
        d.rectangle((x0, 300 - k * 40, x0 + 95, 470), outline=MAG, width=5)
        for j in range(5):
            d.line([(x0 + 10 + j * 18, 310 - k * 40), (x0 + 10 + j * 18, 460)], fill=MAG, width=2)
    im.paste(emblem("meridian", 120, PALE), (60, 40), emblem("meridian", 120, PALE))
    text(im, (60, 190), "WE MOVE.", K.ANTON, 100, PALE)
    text(im, (60, 305), "YOU WAIT.", K.ANTON, 100, MAG)
    text(im, (64, 450), "MERIDIAN FREIGHT  ·  LANE 15 DEPOT", K.MONO, 28, (230, 170, 200))
    frame(im, MAG)
    return glowify(im)


def ad_noodle():
    im = grad(1024, 576, (40, 4, 6), (10, 2, 4))
    d = ImageDraw.Draw(im)
    cx, cy = 760, 330
    d.chord((cx - 190, cy - 140, cx + 190, cy + 170), 0, 180, outline=RED, width=8)
    d.line([(cx - 200, cy + 15), (cx + 200, cy + 15)], fill=RED, width=8)
    for k in range(3):
        d.line([(cx - 60 + k * 50, cy - 10), (cx - 20 + k * 50, cy - 200)], fill=PALE, width=5)
    text(im, (60, 80), "KAIRO", K.ANTON, 140, RED)
    text(im, (60, 250), "NOODLE", K.ANTON, 110, PALE)
    text(im, (64, 420), "HAND-PULLED SINCE 2061  //  OPEN LATE", K.MONO, 28, (240, 190, 190))
    frame(im, RED)
    return glowify(im)


def ad_volta():
    im = grad(1024, 576, (6, 10, 36), (2, 2, 10))
    d = ImageDraw.Draw(im)
    x0, y0 = 700, 90
    d.rounded_rectangle((x0, y0, x0 + 170, y0 + 400), radius=30, outline=CYA, width=7)
    d.polygon([(x0 + 95, y0 + 90), (x0 + 40, y0 + 230), (x0 + 90, y0 + 230), (x0 + 70, y0 + 330), (x0 + 135, y0 + 180),
               (x0 + 88, y0 + 180)], fill=MAG)
    text(im, (60, 90), "VOLTA", K.ANTON, 150, CYA)
    text(im, (60, 270), "STAY UP.", K.ANTON, 90, PALE)
    text(im, (64, 420), "ZERO SUGAR  ·  ALL CHARGE", K.MONO, 30, (180, 210, 240))
    frame(im, CYA)
    return glowify(im)


def blade(word, col, sub):
    im = grad(256, 1024, (16, 4, 24), (4, 2, 10))
    d = ImageDraw.Draw(im)
    y = 60
    for ch in word:
        text(im, (128, y), ch, K.ANTON, 100, col, "mt")
        y += 112
    d.line([(30, y + 10), (226, y + 10)], fill=col, width=4)
    text(im, (128, y + 30), sub, K.MONO, 26, PALE, "mt")
    frame(im, col, 8)
    return glowify(im, 0.6)


def holo_panel(word="ORBITAL", sub="LEO-9  ·  LIFT-OFF 03:40", col=CYA, mark=None):
    """A holo panel: big word, a sub line, 4 px scanlines and a +-3 px RGB split (on black = transparent when added)."""
    im = Image.new("RGB", (1024, 576), (0, 0, 0))
    d = ImageDraw.Draw(im)
    if mark:
        e = emblem(mark, 130, col)
        im.paste(e, (447, 20), e)
    text(im, (512, 250 if mark else 200), word, K.ANTON, 150, col, "mm")
    text(im, (512, 390 if mark else 340), sub, K.MONO, 38, PALE, "mm")
    d.rectangle((20, 20, 1004, 556), outline=col, width=6)
    for y in range(0, 576, 4):
        d.line([(0, y), (1024, y)], fill=(0, 0, 0), width=1)
    r, g, b = im.split()
    r = r.transform(im.size, Image.AFFINE, (1, 0, -3, 0, 1, 0))
    b = b.transform(im.size, Image.AFFINE, (1, 0, 3, 0, 1, 0))
    return Image.merge("RGB", (r, g, b))


ADS = {"solace": ad_solace, "halcyon": ad_halcyon, "orbital": ad_orbital, "meridian": ad_meridian, "noodle": ad_noodle,
       "volta": ad_volta, "holo_orbital": lambda: holo_panel(mark="orbital"),
       "holo_halcyon": lambda: holo_panel("HALCYON", "CLEAN AIR  ·  CLEAN BLOOD", MAG, "halcyon"),
       "blade_hotel": lambda: blade("HOTEL", MAG, "CAPSULES"), "blade_clinic": lambda: blade("CLINIC", CYA, "24 H"),
       "blade_solace": lambda: blade("SOLACE", VIO, "DOSE+")}

if __name__ == "__main__":
    random.seed(9)
    os.makedirs(OUT, exist_ok=True)
    for k, fn in ADS.items():
        fn().save(os.path.join(OUT, k + ".png"))
    print("ads", len(ADS))
