"""Build every deliverable.  python make_all.py [sheet|player|enemy|small|gif|all]"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)

import numpy as np
from PIL import Image, ImageDraw, ImageOps
from slicelib import (PROGRAMS, ORDER, MERIDIAN, render_tile_image, f_num, f_mono, f_ui, bloom, R_OUT)
import wheel as WH

STATIC_T = {"EXPLOIT": 0.0, "ZERO-DAY": 0.62, "FIREWALL": 0.1, "SANDBOX": 0.25, "PROXY": 0.12,
            "PATCH": 0.55, "VIRUS": 0.55, "TROJAN": 0.6, "NULL": 0.0}
BLURB = {
    "EXPLOIT": "hex dump, injected line flashes",
    "ZERO-DAY": "noise resolves to skull, RGB split",
    "FIREWALL": "[#] brick wall, packets bounce",
    "SANDBOX": "window in a window, breathing",
    "PROXY": "net map, dashed path reroutes",
    "PATCH": "progress bar fills, +/- diff",
    "VIRUS": "corrupt pixels spread, datamosh",
    "TROJAN": "smiley flickers into payload",
    "NULL": "dead CRT, dot afterimage",
}


def label(d, x, y, w, title, col, sub, sub2=None):
    f1 = f_num(34)
    f2 = f_mono(14, bold=False)
    tw = f1.getlength(title)
    d.text((x + w / 2 - tw / 2, y), title, font=f1, fill=col)
    sw = f2.getlength(sub)
    d.text((x + w / 2 - sw / 2, y + 40), sub, font=f2, fill=(185, 185, 195))
    if sub2:
        sw = f2.getlength(sub2)
        d.text((x + w / 2 - sw / 2, y + 58), sub2, font=f2, fill=(130, 130, 140))


def sheet():
    im = WH.background(seed=7)
    im = Image.fromarray((np.asarray(im, np.float32) * 0.6).astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.text((40, 26), "SCREENS & DATA", font=f_num(54), fill=(255, 255, 255))
    d.text((40, 88), "every slice is a tiny CRT running its program  |  3-tick tiles, plus 2- and 5-tick variants, plus the Meridian dashboard skin",
           font=f_mono(17, bold=False), fill=(190, 190, 200))
    cell = 300
    row1 = ORDER[:6]
    x0 = (1920 - cell * 6) // 2
    for i, p in enumerate(row1):
        t = render_tile_image(p, 36, PROGRAMS[p]["val"], STATIC_T[p])
        x = x0 + i * cell + (cell - t.width) // 2
        im.paste(t, (x, 135), t)
        label(d, x0 + i * cell, 135 + t.height + 6, cell, p, PROGRAMS[p]["col"],
              PROGRAMS[p]["kind"] + "  |  3 ticks", BLURB[p])
    y2 = 560
    items = [("VIRUS", 36, "player"), ("TROJAN", 36, "player"), ("NULL", 36, "player"),
             ("EXPLOIT", 24, "player"), ("EXPLOIT", 60, "player"), ("EXPLOIT", 36, "corp"), ("FIREWALL", 36, "corp")]
    widths = []
    tiles = []
    for p, span, th in items:
        t = render_tile_image(p, span, PROGRAMS[p]["val"], STATIC_T[p] if th == "player" else 0.8, th)
        tiles.append(t)
        widths.append(max(t.width + 20, 200))
    gapx = (1920 - 60 - sum(widths)) / (len(items) - 1)
    x = 30
    for (p, span, th), t, w in zip(items, tiles, widths):
        tx = int(x + (w - t.width) / 2)
        im.paste(t, (tx, y2 + (250 - t.height)), t)
        if th == "corp":
            title, col = p, MERIDIAN
            s1, s2 = "MERIDIAN skin  |  " + PROGRAMS[p]["kind"], "type = glyph + accent strip"
        elif span != 36:
            title, col = "%s  %d-tick" % (p, span // 12), PROGRAMS[p]["col"]
            s1, s2 = ("glyph above value" if span < 54 else "wide: glyph beside value"), "same texture, re-cropped"
        else:
            title, col = p, PROGRAMS[p]["col"]
            s1, s2 = PROGRAMS[p]["kind"] + "  |  3 ticks", BLURB[p]
        label(d, int(x), y2 + 256, int(w), title, col, s1, s2)
        x += w + gapx
    im = bloom(im, 1, 0.35, 0.6)
    WH.caption(im, "round 5  /  s_c_screen_data  /  programs sheet",
               "shared: per-slice bezel + hairline + power LED, polar UV (arcs), barrel bulge, scanlines, phosphor glow, read plate")
    im.save(os.path.join(OUT, "programs_sheet.png"))


def frame_wheel(theme):
    if theme == "player":
        im = WH.background(seed=3)
        im = WH.glow_behind(im, 960, 470, 380, WH.PINK, 0.16)
        w = WH.render_wheel(WH.PLAYER_LAYOUT, "player", 0.3, name="GHOST.CELL", sub="operative core", hp=(52, 60))
        im.paste(w, (960 - WH.CX, 0), w)
        im = bloom(im, 1, 0.5, 0.55)
        WH.caption(im, "PLAYER WHEEL  -  9 programs on 30 ticks",
                   "EXPLOIT 4 | ZERO-DAY 2 | PROXY 3 | PATCH 3 | VIRUS 4 | TROJAN 3 | NULL 3 | FIREWALL 4 | SANDBOX 4")
        im.save(os.path.join(OUT, "wheel_player.png"))
    else:
        im = WH.background(seed=9)
        im = WH.glow_behind(im, 700, 470, 380, MERIDIAN, 0.14)
        w = WH.render_wheel(WH.ENEMY_LAYOUT, "corp", 0.6, name="COMPLIANCE\nMONITOR", sub="Meridian Systems", hp=(40, 40))
        im.paste(w, (700 - WH.CX, 0), w)
        # side panel: the full dashboard skin family
        d = ImageDraw.Draw(im)
        d.text((1250, 60), "MERIDIAN DASHBOARD SKIN", font=f_num(38), fill=MERIDIAN)
        d.text((1250, 104), "one material for every slice: slate glass, grid, orange widgets.",
               font=f_mono(15, bold=False), fill=(190, 190, 200))
        d.text((1250, 124), "type reads only from the glyph and the thin accent strip.",
               font=f_mono(15, bold=False), fill=(190, 190, 200))
        for i, p in enumerate(ORDER):
            t = render_tile_image(p, 36, PROGRAMS[p]["val"], 0.8, "corp", scale=0.62)
            cx = 1250 + (i % 3) * 205
            cy = 160 + (i // 3) * 245
            im.paste(t, (cx + (190 - t.width) // 2, cy), t)
            f = f_num(22)
            s = "%s / %s" % (p, PROGRAMS[p]["kind"])
            d.text((cx + 95 - f.getlength(s) / 2, cy + t.height + 4), s, font=f, fill=PROGRAMS[p]["col"])
        im = bloom(im, 1, 0.45, 0.6)
        WH.caption(im, "ENEMY WHEEL  -  Meridian compliance monitor", "corporate dashboard skin: bar charts, KPI, checklists, gauges, all orange; type by glyph + accent strip", MERIDIAN)
        im.save(os.path.join(OUT, "wheel_enemy.png"))


def small():
    im = WH.background(seed=4)
    im = Image.fromarray((np.asarray(im, np.float32) * 0.7).astype(np.uint8))
    d = ImageDraw.Draw(im)
    # hero, greyscale
    hero = WH.render_wheel(WH.PLAYER_LAYOUT, "player", 0.3, hp=(52, 60))
    k = 0.98
    hero = hero.resize((int(hero.width * k), int(hero.height * k)), Image.LANCZOS)
    hx = 1920 - hero.width - 10
    im.paste(hero, (hx, 10), hero)
    gx0 = hx
    # small: naive and LOD at r = 60 (scale 60/360)
    sc = 60 / R_OUT
    lod_opts = dict(glyph_scale=1.45, number_scale=1.15, tex_gain=0.55, plate=0.85)
    naive = WH.render_wheel(WH.PLAYER_LAYOUT, "player", 0.3, hp=None)
    lod = WH.render_wheel(WH.PLAYER_LAYOUT, "player", 0.3, opts=lod_opts, hp=None)
    d.text((40, 30), "r = 60 px", font=f_num(48), fill=(255, 255, 255))
    d.text((40, 84), "actual size (left) and 2.4x nearest zoom (right)", font=f_mono(16, bold=False), fill=(190, 190, 200))
    y = 130
    for lab, wim in (("straight downscale of the hero tile", naive), ("LOD: glyph x1.45, texture gain 0.55, plate 0.85", lod)):
        s = wim.resize((int(wim.width * sc), int(wim.height * sc)), Image.LANCZOS)
        cropbox = (int((WH.CX - 400) * sc), int((WH.CY - 445) * sc), int((WH.CX + 400) * sc), int((WH.CY + 410) * sc))
        s = s.crop(cropbox)
        im.paste(s, (60, y + 40), s)
        z = s.resize((int(s.width * 2.4), int(s.height * 2.4)), Image.NEAREST)
        im.paste(z, (240, y), z)
        d.text((60, y + z.height + 6), lab, font=f_mono(16, bold=False), fill=(220, 220, 230))
        y += z.height + 60
    im = bloom(im, 1, 0.45, 0.6)
    arr = np.asarray(im).copy()
    grey = np.asarray(ImageOps.grayscale(Image.fromarray(arr[:, gx0:])).convert("RGB"))
    arr[:, gx0:] = grey
    im = Image.fromarray(arr)
    d = ImageDraw.Draw(im)
    d.text((gx0 + 20, 990), "hero size, greyscale", font=f_num(36), fill=(255, 255, 255))
    WH.caption(im, "SMALL + GREY", "glyph/value contrast holds without colour; at r=60 the LOD pass keeps glyphs legible")
    im.save(os.path.join(OUT, "small_and_grey.png"))


def gif():
    progs = ORDER + ["EXPLOIT*"]
    sc = 0.62
    cw, chh = 196, 236
    W, H = cw * 5, chh * 2 + 50
    frames = []
    nf = 24
    for fi in range(nf):
        t = fi / nf
        im = Image.new("RGB", (W, H), (9, 8, 13))
        d = ImageDraw.Draw(im)
        d.text((12, 8), "SCREENS & DATA  -  shader loops", font=f_num(28), fill=(255, 255, 255))
        for i, p in enumerate(progs):
            corp = p.endswith("*")
            pn = p.rstrip("*")
            tile = render_tile_image(pn, 36, PROGRAMS[pn]["val"], t, "corp" if corp else "player", scale=sc)
            x = (i % 5) * cw + (cw - tile.width) // 2
            y = 50 + (i // 5) * chh
            im.paste(tile, (x, y), tile)
            f = f_num(22)
            s = "MERIDIAN EXPLOIT" if corp else pn
            col = MERIDIAN if corp else PROGRAMS[pn]["col"]
            d.text(((i % 5) * cw + cw / 2 - f.getlength(s) / 2, y + tile.height + 2), s, font=f, fill=col)
        frames.append(bloom(im, 1, 0.4, 0.6))
        print("frame", fi, flush=True)
    # strip: 8 time samples per program
    cols = [0, 3, 6, 9, 12, 15, 18, 21]
    sw = 6 * 0 + 170
    strip = Image.new("RGB", (220 + sw * len(cols), 60 + 200 * len(progs)), (9, 8, 13))
    d = ImageDraw.Draw(strip)
    d.text((14, 12), "shader_fx strip  -  t = 0 .. 7/8 of the loop (24 frames @ 12 fps)", font=f_num(30), fill=(255, 255, 255))
    for r, p in enumerate(progs):
        corp = p.endswith("*")
        pn = p.rstrip("*")
        d.text((14, 60 + r * 200 + 80), "MERIDIAN EXPLOIT" if corp else pn, font=f_num(30),
               fill=MERIDIAN if corp else PROGRAMS[pn]["col"])
        for c, fi in enumerate(cols):
            fr = frames[fi]
            x = (r % 5) * cw
            y = 50 + (r // 5) * chh
            tile = fr.crop((x + 8, y, x + cw - 8, y + 190))
            strip.paste(tile, (220 + c * sw, 60 + r * 200))
    strip.save(os.path.join(OUT, "shader_fx_strip.png"))
    pal = [f.quantize(colors=128, method=Image.MEDIANCUT, dither=Image.NONE) for f in frames]
    pal[0].save(os.path.join(OUT, "shader_fx.gif"), save_all=True, append_images=pal[1:], duration=83, loop=0, optimize=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    t0 = time.time()
    if what in ("sheet", "all"):
        sheet()
    if what in ("player", "all"):
        frame_wheel("player")
    if what in ("enemy", "all"):
        frame_wheel("corp")
    if what in ("small", "all"):
        small()
    if what in ("gif", "all"):
        gif()
    print("done", what, round(time.time() - t0, 1), "s")
