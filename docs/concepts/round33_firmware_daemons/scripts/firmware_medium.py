"""firmware_medium.png: two media for a Firmware chip, compared. A = socketed die (hardware), B = sticker-chip (vinyl).

python firmware_medium.py
"""
import math
from PIL import Image, ImageDraw, ImageFilter

import fwlib as F
import fwfx as X
import firmware_socket as FS
L = F.L


def sticker_chip(fid, s, gloss=0.22, seed=5):
    art = F.chip(fid, s, flat=True, led=True)
    return L.sticker_from_art(art, border=5, gloss_k=gloss, seed=seed)


def tile_sticker(prog, val, tier, state, fid, sc, gloss=0.22, lift=0.0):
    im, (cx, cy), (x, y) = FS.tile_chip(prog, val, tier, state, None, sc)
    sd = sticker_chip(fid, max(16, int(F.CHIP_MASTER * sc)), gloss=gloss)
    return L.place_sticker(im, sd, x, y - lift, angle=-8, scale=1.0, hover=lift / 10.0)


def main():
    img = F.bg(seed=9)
    d = F.header(img, "FIRMWARE MEDIUM  -  two options",
                 "Same 18 glyphs, same corner. The question is the material: is a chip a piece of the Cell's hardware, or a vinyl sticker?")
    for col, (title, sub, colr) in enumerate((("A  SOCKETED DIE  (recommended)", "hardware: a faceted chip, pins in the bezel, rarity LED", L.LIME),
                                              ("B  STICKER-CHIP", "vinyl: the chip printed on a die-cut sticker, slapped on the bezel", (255, 140, 200)))):
        x0 = 32 + col * 950
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([x0, 112, x0 + 920, 1062], radius=14, fill=(18, 16, 26, 255), outline=colr + (255,), width=3 if col == 0 else 2)
        d.text((x0 + 24, 124), title, font=L.f_num(38), fill=colr + (255,))
        d.text((x0 + 26, 172), sub, font=L.f_mono(16), fill=(200, 200, 215, 255))
        # hero tile
        if col == 0:
            hero, _, _ = FS.tile_chip("EXPLOIT", 10, 3, None, "overvolt", 0.9)
            lit, _, _ = FS.tile_chip("EXPLOIT", 10, 3, None, "overvolt", 0.9, lit=1.0)
        else:
            hero = tile_sticker("EXPLOIT", 10, 3, None, "overvolt", 0.9)
            lit = tile_sticker("EXPLOIT", 10, 3, None, "overvolt", 0.9, gloss=0.9, lift=6)
        img.alpha_composite(hero, (x0 + 20, 210))
        img.alpha_composite(lit, (x0 + 470, 210))
        d = ImageDraw.Draw(img)
        d.text((x0 + 20 + hero.width / 2, 500), "idle", font=L.f_mono(15), fill=(180, 180, 195, 255), anchor="mm")
        d.text((x0 + 470 + lit.width / 2, 500), "TRIGGER: " + ("LED + lip flare, pins hot, gold trace" if col == 0 else "gloss sweep + corner lifts (no light)"),
               font=L.f_mono(15), fill=(180, 180, 195, 255), anchor="mm")
        # small wheels
        sl = [("EXPLOIT", 6, 1, None), ("FIREWALL", 5, 1, None), ("PROXY", 4, 1, None),
              ("PATCH", 4, 1, None), ("ZERO-DAY", 12, 1, None), ("NULL", None, 1, None)]
        fw = ["leech", "static_coat", None, "nanite_mesh", "tracer", None]
        if col == 0:
            w = F.socket_wheel(sl, fw, 110, "small110")
            w6 = F.socket_wheel(sl, fw, 60, "small")
        else:
            w = F.wheel_cached(sl, 110, "small110").copy()
            w6 = F.wheel_cached(sl, 60, "small").copy()
            for (ww, r) in ((w, 110), (w6, 60)):
                for i, f in enumerate(fw):
                    if f:
                        x, y, a = F.socket_pos(6, i, r, ww.width)
                        sd = sticker_chip(f, F.chip_px(r) + 2)
                        ww2 = L.place_sticker(ww, sd, x, y, angle=-a * 0.0 - 8, shadow=0.6)
                        ww.paste(ww2)
        img.alpha_composite(w, (x0 + 60, 530))
        img.alpha_composite(w6, (x0 + 400, 580))
        img.alpha_composite(F.grey(w6), (x0 + 600, 580))
        d = ImageDraw.Draw(img)
        d.text((x0 + 60 + w.width / 2, 788), "r = 110", font=L.f_mono(13), fill=(170, 170, 185, 255), anchor="mm")
        d.text((x0 + 400 + w6.width / 2, 730), "r = 60", font=L.f_mono(13), fill=(170, 170, 185, 255), anchor="mm")
        d.text((x0 + 600 + w6.width / 2, 730), "grey", font=L.f_mono(13), fill=(170, 170, 185, 255), anchor="mm")
        # verdict
        if col == 0:
            pro = ["+ slices are CRT hardware: a chip SOCKETS into it (GDD 6.1 word)",
                   "+ the LED is a light source: the trigger cue is free and loud",
                   "+ rarity reads twice (LED colour + pips) and survives r = 60",
                   "+ swapping / ejecting is physical: pins out, chip pops",
                   "- one more 3D-looking object; keep facets to 3 tones"]
        else:
            pro = ["+ sticker = 'never changes' (UI kit rule): fits 'kept for the run'",
                   "+ cheapest to build: one texture per chip",
                   "- reads as a label, not a part: it doesn't CHANGE the slice",
                   "- no light: a trigger can't glow, so the cue must be FX on top",
                   "- white die-cut border clashes with the tier III gold border",
                   "- stickers are already words and verbs; this blurs the rule"]
        for k, s in enumerate(pro):
            d.text((x0 + 40, 830 + k * 34), s, font=L.f_mono(17), fill=((170, 255, 150) if s[0] == "+" else (255, 150, 150)) + (255,))
    p = L.pen(L.GP_YELLOW, seed=33)
    p.text("this one", 790, 150, 38, angle=-6)
    p.arrow([(690, 152), (590, 152), (490, 144)], width=7, head=16)
    img = L.ink(img, p)
    L.save(img, "firmware_medium.png")


if __name__ == "__main__":
    main()
