"""Builds wheel_enemy.png, wheel_enemy_2.png, wheel_player.png, wheel_boss.png.
Usage: python build_wheels.py [names...]   (default: all)
"""
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import slicelib as sl
import themes as th
import wheel as wl
from data import WHEELS, STILL_T

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CACHE = {}


def get_wheel(key, **kw):
    if key in _CACHE:
        return _CACHE[key]
    W = WHEELS[key]
    theme = key.split("_")[0]
    img = wl.render_wheel(theme, W["slices"], W["name"], W["corp"], t=STILL_T.get(theme, 0.3),
                          seed=hash(key) % 97 if False else sum(map(ord, key)) % 97, **kw)
    _CACHE[key] = img
    return img


def pair(left, right, title, sub, fname, lscale=0.80, rscale=0.80):
    lt, rt = left.split("_")[0], right.split("_")[0]
    frame = wl.background(seed=11, tints=[(480, 470, th.THEMES[lt]["col"], 420),
                                          (1440, 470, th.THEMES[rt]["col"], 420)])
    for key, cx, sc in ((left, 480, lscale), (right, 1440, rscale)):
        img = get_wheel(key)
        wl.place(frame, img, cx, 455, sc)
        hp, hpm = WHEELS[key]["hp"]
        wl.hp_arc(frame, cx, 455, (sl.R_OUT + 90) * sc, hp, hpm)
        theme = key.split("_")[0]
        f = sl.font(26, "SemiBold")
        lab = th.THEMES[theme]["name"]
        d = ImageDraw.Draw(frame)
        bb = f.getbbox(lab)
        c = tuple(int(v * 255) for v in sl.hexrgb(th.THEMES[theme]["col"]))
        d.text((cx - (bb[2] - bb[0]) / 2, 18), lab, font=f, fill=c + (255,))
    wl.caption(frame, title, sub)
    frame.convert("RGB").save(os.path.join(OUT, fname))
    print("wrote", fname)


def boss():
    W = WHEELS["halcyon_boss"]
    img = wl.render_wheel("halcyon", W["slices"], W["name"], W["corp"], t=0.35, seed=41, boss=True,
                          rich=True, phase=(2, 3))
    frame = wl.background(seed=12, tints=[(700, 470, th.HALCYON, 520), (700, 470, "#FFCF6E", 240)])
    sc = 0.86
    wl.place(frame, img, 700, 460, sc)
    wl.hp_arc(frame, 700, 460, (sl.R_OUT + 112) * sc, W["hp"][0], W["hp"][1],
              notches=((2 / 3, "P2"), (1 / 3, "P3")))
    # regular Halcyon wheel for comparison
    reg = WHEELS["halcyon"]
    rimg = wl.render_wheel("halcyon", reg["slices"], reg["name"], reg["corp"], t=0.35, seed=42)
    wl.place(frame, rimg, 1560, 330, 0.42)
    d = ImageDraw.Draw(frame)
    f = sl.font(26, "SemiBold")
    d.text((1390, 40), "HALCYON CIVIC  -  regular", font=f, fill=(140, 123, 255, 255))
    d.text((40, 30), "HALCYON CIVIC  //  BOSS", font=sl.font(40), fill=(255, 205, 110, 255))
    lines = [
        "Boss = richer Halcyon theme:",
        "- heavier bezel: two colonnade tiers,",
        "  gilt trim, crenellated rim, hovering",
        "  halo ring on struts",
        "- tiles: gold counter-flow on the civic",
        "  rings + a gilded halo ring line",
        "- phase marker: PHASE II / III plaque",
        "  with diamond pips on the bezel; the",
        "  HP arc carries P2 / P3 notches",
    ]
    f2 = sl.mono(19, False)
    y = 600
    for ln in lines:
        d.text((1380, y), ln, font=f2, fill=(215, 210, 240, 255))
        y += 28
    wl.caption(frame, "HALCYON BOSS (phase 2 of 3)",
               "heavier bezel, gilded counter-flow, phase plaque + pips, HP arc phase notches")
    frame.convert("RGB").save(os.path.join(OUT, "wheel_boss.png"))
    print("wrote wheel_boss.png")


if __name__ == "__main__":
    which = sys.argv[1:] or ["enemy", "enemy2", "player", "boss"]
    t0 = time.time()
    if "enemy" in which:
        pair("meridian", "solace", "ENEMY WHEELS: MERIDIAN vs SOLACE",
             "one material family per corp; type = glyph + accent rim/tab; container steel | sterile glass",
             "wheel_enemy.png")
    if "enemy2" in which:
        pair("orbital", "rebel", "ENEMY WHEELS: ORBITAL vs REBEL_CELL",
             "star map + solar cells | corrupted Cell PCB, scan-glitch bars, inverted hexagon",
             "wheel_enemy_2.png")
    if "player" in which:
        pair("player", "meridian", "PLAYER (neutral) vs ENEMY (Meridian)",
             "player: slice = type colour; enemy: slice = corp material, type only as accent",
             "wheel_player.png")
    if "boss" in which:
        boss()
    print("%.1fs" % (time.time() - t0))
