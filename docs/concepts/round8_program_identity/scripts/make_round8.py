"""Round 8 deliverables: bold program identity in the V2 (living programs) wheel.

python make_round8.py [library|wheels|anim|small|all]
"""
import math
import os
import sys
import textwrap
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
CACHE = os.path.join(OUT, "scratch", "renders")

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from slicelib import PROGRAMS, CORPS, f_num, f_ui, f_mono, bloom, to_img, render_slice, R_OUT, R_IN
import roster as RS
import versions as V
import icons8 as I

CAT_COL = {"ATTACK": (255, 70, 110), "DEFENCE": (92, 225, 255), "UTILITY": (123, 224, 123)}
LIBRARY = [
    ("ATTACK", "aggressive: skulls, fire, poison", [
        ("EXPLOIT", "EXPLOIT", None, 6, ["flaming_skull", "fire", "bomb"]),
        ("ZERO-DAY", "ZERO-DAY", None, 12, ["skull", "skull_fuse", "crossbones"]),
        ("VIRUS", "VIRUS", None, 3, ["poison_vial", "bio_bug", "storm_cloud"]),
        ("TROJAN", "TROJAN", None, 2, ["trojan_horse", "envelope_bomb"]),
        ("PHISHING *", "VIRUS", "HOOK", 2, ["phish_hook", "hook_password"]),
    ]),
    ("DEFENCE", "solid: wall, steel door, safe, lock, shield", [
        ("FIREWALL", "FIREWALL", None, 5, ["burning_wall", "wall_shield"]),
        ("SANDBOX", "SANDBOX", None, 8, ["vault_door", "steel_safe"]),
        ("SHIELD *", "SANDBOX", "SHIELDG", 8, ["riveted_shield", "blast_door"]),
        ("ENCRYPT *", "SANDBOX", "LOCK", 3, ["padlock_password", "padlock"]),
    ]),
    ("UTILITY", "tools: mask, key, lens, chip, cloud", [
        ("PROXY", "PROXY", None, 4, ["anon_mask", "cloud"]),
        ("PATCH", "PATCH", None, 3, ["key", "fingerprint", "chip_repair"]),
        ("NULL", "NULL", None, None, ["magnifier_static", "unplugged_chip"]),
        ("RECON *", "PROXY", "LENS", 1, ["magnifier_code", "debug_bug", "password"]),
    ]),
]
ANIM = [("EXPLOIT", "flaming_skull", "flames flicker"), ("ZERO-DAY", "skull", "jaw chatters, glitch slice"),
        ("VIRUS", "poison_vial", "poison drips, bubbles rise"), ("FIREWALL", "burning_wall", "the wall burns"),
        ("SANDBOX", "vault_door", "bolts slide, wheel turns: seals"), ("PROXY", "anon_mask", "the mask glitches")]


def tile(prog, glyph, value, name, t=0.3, scale=1.0, ss=2, span=36):
    pad = 10
    Ro = R_OUT * ss
    w = int(2 * Ro * math.sin(math.radians(span / 2)) + 2 * pad * ss)
    h = int(Ro - R_IN * ss * math.cos(math.radians(span / 2)) + 2 * pad * ss)
    canvas = np.zeros((h, w, 4), np.float32)
    opts = {"art": True, "art_map": {prog: name}, "plate": 0.55}
    render_slice(canvas, w / 2, Ro + pad * ss, prog, -span / 2, span, value, t, "player", ss, opts, seed=3, glyph=glyph)
    im = Image.fromarray((np.clip(canvas, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")
    return im.resize((int(w / ss * scale), int(h / ss * scale)), Image.LANCZOS)


def background(W, H, tint, seed=3, dim=1.0):
    yy = np.linspace(0, 1, H)[:, None, None]
    top = np.array([0.055, 0.045, 0.075], np.float32)
    bot = np.array([0.02, 0.02, 0.03], np.float32)
    arr = np.tile(top + (bot - top) * yy, (1, W, 1))
    rng = np.random.default_rng(seed)
    city = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(city)
    x = 0
    while x < W:
        bw = int(rng.integers(80, 220))
        bh = int(rng.integers(int(H * 0.25), int(H * 0.6)))
        d.rectangle([x, H - bh, x + bw, H], fill=(14, 13, 20))
        for wy in range(H - bh + 20, H, 26):
            for wx in range(x + 12, x + bw - 12, 22):
                if rng.random() < 0.25:
                    d.rectangle([wx, wy, wx + 8, wy + 10], fill=(55, 50, 75))
        x += bw + int(rng.integers(6, 30))
    city = np.asarray(city.filter(ImageFilter.GaussianBlur(5)), np.float32) / 255
    yy2, xx2 = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.exp(-(((xx2 - W * 0.35) / (W * 0.45)) ** 2 + ((yy2 - H * 0.45) / (H * 0.6)) ** 2))[..., None]
    arr = arr + city * 0.7 + g * (np.array(tint, np.float32) / 255) * 0.10
    return to_img(arr * dim)


def paste(dst, im, x, y):
    dst.paste(im, (int(x), int(y)), im)


def fit(im, w, h):
    k = min(w / im.width, h / im.height)
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)


def grey(im):
    a = im.split()[3]
    g = ImageOps.grayscale(im.convert("RGB")).convert("RGBA")
    g.putalpha(a)
    return g


# ----------------------------------------------------------------- library
def make_library():
    pw = 1000
    W = 3 * pw + 40
    H = 2280
    im = background(W, H, (255, 70, 110), seed=81)
    d = ImageDraw.Draw(im)
    d.text((30, 14), "PROGRAM IDENTITY LIBRARY  -  primary image + alternates, as 3-tick slice tiles", font=f_num(54), fill=(255, 255, 255))
    d.text((34, 78), "top: the slice tile as it plays (art behind glyph + value, dark plate kept); below: the raw image. "
                     "* = proposed new program/variant the designer asked to see (PHISHING, SHIELD, ENCRYPT, RECON).",
           font=f_mono(17, False), fill=(190, 190, 200))
    for c, (cat, sub, rows) in enumerate(LIBRARY):
        x0 = 20 + c * pw
        col = CAT_COL[cat]
        d.rectangle([x0, 120, x0 + pw - 30, 126], fill=col)
        d.text((x0, 134), cat, font=f_num(46), fill=col)
        d.text((x0 + f_num(46).getlength(cat) + 16, 154), sub, font=f_mono(16, False), fill=(200, 200, 210))
        y = 200
        for (label, prog, glyph, val, names) in rows:
            d.text((x0, y + 80), label, font=f_num(34), fill=PROGRAMS[prog]["col"] if "*" not in label else col)
            d.text((x0, y + 120), PROGRAMS[prog]["kind"] if "*" not in label else "proposal", font=f_ui(16, b"Bold SemiCondensed"), fill=(170, 170, 180))
            for k, n in enumerate(names):
                tl = tile(prog, glyph, val, n, scale=0.92)
                tx = x0 + 200 + k * 262
                paste(im, tl, tx, y)
                lab = n.replace("_", " ")
                f = f_ui(17, b"Bold SemiCondensed")
                tc = (255, 255, 255) if k == 0 else (180, 180, 190)
                d.text((tx + tl.width / 2 - f.getlength(lab) / 2, y + tl.height + 2), lab, font=f, fill=tc)
                raw = I.art(n, 130, 0.3)
                d.rounded_rectangle([tx + tl.width / 2 - 70, y + tl.height + 26, tx + tl.width / 2 + 70, y + tl.height + 166], radius=10, fill=(16, 14, 22), outline=(60, 60, 72))
                paste(im, raw, tx + tl.width / 2 - 65, y + tl.height + 31)
                if k == 0:
                    fp = f_ui(13, b"Bold Condensed")
                    d.rounded_rectangle([tx + 6, y + 6, tx + 72, y + 26], radius=4, fill=col)
                    d.text((tx + 12, y + 8), "PRIMARY", font=fp, fill=(10, 8, 16))
            y += 410
            print("lib", label, flush=True)
    im = bloom(im, 1, 0.3, 0.65)
    im.save(os.path.join(OUT, "identity_library.png"))


# ----------------------------------------------------------------- wheels
def wheel_specs():
    b, bm = RS.class_spec("breaker")
    b["key"] = "breaker"
    g, gm = RS.class_spec("ghost")
    g["key"] = "ghost"
    e, em = RS.enemy_spec("drone_dispatcher")
    e["key"] = "drone_dispatcher"
    m, _, mm = RS.boss_specs("meridian")
    m["key"] = "the_manifest"
    return [("wheel_breaker", b, "BREAKER", (255, 61, 168)), ("wheel_ghost", g, "GHOST", (92, 225, 255)),
            ("wheel_enemy_meridian", e, "DRONE DISPATCHER  (Meridian)", CORPS["meridian"]["col"]),
            ("boss_manifest", m, "THE MANIFEST  (Meridian boss)", CORPS["meridian"]["col"])]


def make_wheels():
    os.makedirs(CACHE, exist_ok=True)
    for key, spec, title, acc in wheel_specs():
        t0 = time.time()
        hero = V.render_v(spec, 2, ss=2)
        lod = V.render_v(spec, 2, ss=1, lod=True)
        hero.save(os.path.join(CACHE, key + ".png"))
        lod.save(os.path.join(CACHE, key + "_lod.png"))
        im = background(1920, 1080, acc, seed=len(key))
        w = hero.crop(hero.getbbox())
        w = fit(w, 1150, 1060)
        paste(im, w, 20 + (1150 - w.width) / 2, 10 + (1060 - w.height) / 2)
        im = bloom(im, 1, 0.4, 0.62)
        d = ImageDraw.Draw(im)
        x = 1220
        d.text((x, 24), title, font=f_num(52 if len(title) < 20 else 40), fill=acc)
        d.text((x + 2, 90), "V2 living programs  |  bold identity art  |  telemetry readout ring", font=f_ui(20, b"SemiBold"), fill=(220, 220, 230))
        y = 140
        d.text((x + 2, y), "SLICES  (content data -> program -> image)", font=f_ui(19, b"Bold SemiCondensed"), fill=acc)
        y += 34
        seen = []
        for sl in spec["slots"]:
            nm = I.SPECIAL_ART.get(sl.get("special")) or I.PRIMARY.get(sl["program"])
            k = (sl["program"], sl.get("special"), sl["value"])
            if k in seen:
                continue
            seen.append(k)
            th = I.art(nm, 84, 0.3)
            paste(im, th, x, y)
            lab = sl["special"].upper() if sl.get("special") else sl["program"]
            v = "" if sl["program"] == "NULL" or (sl.get("special") and sl["special"] != "tariff") else " %d" % sl["value"]
            d.text((x + 100, y + 12), lab + v, font=f_num(30), fill=PROGRAMS[sl["program"]]["col"])
            d.text((x + 100, y + 50), nm.replace("_", " ") + "  (" + I.ART[nm][1] + ")", font=f_mono(15, False), fill=(200, 200, 210))
            y += 96
        y += 8
        notes = ["Border: the V2 telemetry ring (kept): scrolling class/corp readout + emblem badges.",
                 "Each screen: a dimmed copy of the program's own screen, a category glow, and the bold image;",
                 "the dark plate keeps the white glyph + value on top."]
        if spec["theme"] != "player":
            notes.append("Enemy: the corp skin shows through and the art is tinted 45% toward the corp colour.")
        if spec.get("boss"):
            notes.append("Boss: V2 hologram crown (face + emblem) and a 2nd ring of 12 enemy programs, same art.")
        for n in notes:
            for ln in textwrap.wrap(n, 68):
                d.text((x + 2, y), ln, font=f_mono(15, False), fill=(185, 185, 195))
                y += 20
        im.save(os.path.join(OUT, key + ".png"))
        print("wheel", key, round(time.time() - t0, 1), flush=True)


# ----------------------------------------------------------------- animation
def make_anim():
    nf = 24
    sc = 0.7
    cw, ch = 250, 290
    W, H = 3 * cw, 2 * ch + 50
    frames = []
    for fi in range(nf):
        t = fi / nf
        im = Image.new("RGB", (W, H), (10, 9, 14))
        d = ImageDraw.Draw(im)
        d.text((10, 8), "ROUND 8  -  program identity, animated", font=f_num(28), fill=(255, 255, 255))
        for i, (prog, name, note) in enumerate(ANIM):
            tl = tile(prog, None, PROGRAMS[prog]["val"], name, t=t, scale=sc)
            x = (i % 3) * cw + (cw - tl.width) / 2
            y = 50 + (i // 3) * ch
            paste(im, tl, x, y)
            f = f_ui(17, b"Bold SemiCondensed")
            s = "%s: %s" % (prog, name.replace("_", " "))
            d.text(((i % 3) * cw + cw / 2 - f.getlength(s) / 2, y + tl.height + 4), s, font=f, fill=PROGRAMS[prog]["col"])
        frames.append(bloom(im, 1, 0.35, 0.62))
        print("frame", fi, flush=True)
    pal = [f.quantize(colors=128, method=Image.MEDIANCUT, dither=Image.NONE) for f in frames]
    pal[0].save(os.path.join(OUT, "anim.gif"), save_all=True, append_images=pal[1:], duration=83, loop=0, optimize=True)
    cols = [0, 3, 6, 9, 12, 15, 18, 21]
    tw = 240
    strip = Image.new("RGB", (300 + tw * len(cols), 60 + 6 * 250), (10, 9, 14))
    d = ImageDraw.Draw(strip)
    d.text((14, 12), "anim strip  -  8 samples of the 24-frame loop (12 fps)", font=f_num(30), fill=(255, 255, 255))
    for r, (prog, name, note) in enumerate(ANIM):
        y = 60 + r * 250
        d.text((14, y + 70), prog, font=f_num(32), fill=PROGRAMS[prog]["col"])
        for ln_i, ln in enumerate(textwrap.wrap(note, 22)):
            d.text((14, y + 112 + ln_i * 20), ln, font=f_mono(15, False), fill=(190, 190, 200))
        for c, fi in enumerate(cols):
            tl = tile(prog, None, PROGRAMS[prog]["val"], name, t=fi / nf, scale=0.9)
            tl = fit(tl, tw - 10, 240)
            paste(strip, tl, 300 + c * tw, y)
    strip = bloom(strip, 1, 0.3, 0.62)
    strip.save(os.path.join(OUT, "anim_strip.png"))


# ----------------------------------------------------------------- small + grey
def make_small():
    keys = [(k, title) for k, s, title, a in wheel_specs()]
    cw = 600
    W, H = 4 * cw + 40, 980
    im = background(W, H, (92, 225, 255), seed=12, dim=0.7)
    d = ImageDraw.Draw(im)
    d.text((30, 16), "SMALL + GREY  -  r = 60 small variant (colour, greyscale) and hero greyscale at r = 150", font=f_num(44), fill=(255, 255, 255))
    for i, (k, title) in enumerate(keys):
        x = 20 + i * cw
        lod = Image.open(os.path.join(CACHE, k + "_lod.png")).convert("RGBA")
        lod = lod.crop(lod.getbbox())
        kk = 60 / R_OUT
        s60 = lod.resize((int(lod.width * kk), int(lod.height * kk)), Image.LANCZOS)
        paste(im, s60, x + 60, 100)
        paste(im, grey(s60), x + 90 + s60.width, 100)
        hero = Image.open(os.path.join(CACHE, k + ".png")).convert("RGBA")
        hero = hero.crop(hero.getbbox())
        kk = 150 / R_OUT
        hg = grey(hero.resize((int(hero.width * kk), int(hero.height * kk)), Image.LANCZOS))
        hg = fit(hg, cw - 30, 520) if hg.height > 520 or hg.width > cw - 30 else hg
        paste(im, hg, x + (cw - hg.width) / 2, 390)
        f = f_num(26)
        d.text((x + cw / 2 - f.getlength(title) / 2, H - 46), title, font=f, fill=(230, 230, 240))
    im.save(os.path.join(OUT, "small_and_grey.png"))


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    t0 = time.time()
    if what in ("library", "all"):
        make_library()
    if what in ("wheels", "all"):
        make_wheels()
    if what in ("anim", "all"):
        make_anim()
    if what in ("small", "all"):
        make_small()
    print("done", what, round(time.time() - t0, 1))
