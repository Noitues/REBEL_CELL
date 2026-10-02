"""Round 11 slice sheet -> ../slices_r11.png (1920 x 1080).

Top: the two reworked slices as they ship in the mockups.
  EVADE (PROXY): round 6 double-chevron icon over a road-sign detour (hard 90-degree turn, packet takes it).
  AFFLICT (VIRUS): biohazard icon (round 10 option C) over the ooze effect (round 10 option B).
  Each at hero size, inside an r = 60 wheel (colour + greyscale), and as greyscale hero tiles.
Bottom: kept in the library, not in use: the blotch effect (reserved for BURN / TORCH / DISSOLVE-type
programs), two Guy Fawkes-style mask backdrops (program TBD), and the poison-vial icon (reserved).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
CACHE = os.path.join(OUT, "scratch", "slices11")

from PIL import Image, ImageDraw, ImageOps
from slicelib import render_tile_image, f_num, f_ui, f_mono, bloom, PROGRAMS, R_OUT, glyph_rgba
import screens10 as S10
import combat_specs as CS
import combat_wheel as CWL


def grey(im):
    a = im.split()[3]
    g = ImageOps.grayscale(im.convert("RGB")).convert("RGBA")
    g.putalpha(a)
    return g


def render_assets():
    os.makedirs(CACHE, exist_ok=True)
    S10.select(virus="OOZE", proxy="TURN")
    for prog, val in (("PROXY", 4), ("VIRUS", 3)):
        render_tile_image(prog, 60, val, 0.55, ss=2, opts=dict(upright=True), scale=0.95, seed=3).save(os.path.join(CACHE, "hero_%s.png" % prog))
    spec, _ = CS.player(41)
    w, _c = CWL.render(spec, ss=2, lod=True)
    w = w.crop(w.getbbox())
    k = 60 / R_OUT
    w.resize((int(w.width * k), int(w.height * k)), Image.LANCZOS).save(os.path.join(CACHE, "small.png"))
    w, _c = CWL.render(spec, ss=2)
    w = w.crop(w.getbbox())
    k = 150 / R_OUT
    w.resize((int(w.width * k), int(w.height * k)), Image.LANCZOS).save(os.path.join(CACHE, "mid.png"))
    S10.select(virus="BURN")
    render_tile_image("VIRUS", 60, None, 0.55, ss=2, opts=dict(upright=True, icons=False), scale=0.72, seed=3).save(os.path.join(CACHE, "burn.png"))
    for opt in ("BIG", "CROWD"):
        S10.select(maskbg=opt)
        render_tile_image("MASKBG", 60, None, 0.4, ss=2, opts=dict(upright=True, icons=False), scale=0.72, seed=3).save(os.path.join(CACHE, "mask_%s.png" % opt))
    S10.select(virus="OOZE", proxy="TURN", maskbg=None)
    print("assets done", flush=True)


def label(d, x, y, t1, t2, col):
    d.text((x, y), t1, font=f_ui(20, b"Bold SemiCondensed"), fill=col)
    if t2:
        d.text((x, y + 26), t2, font=f_mono(14, False), fill=(185, 185, 195))


def compose():
    W, H = 1920, 1080
    im = Image.new("RGB", (W, H), (11, 10, 16))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 4):
        d.line([(0, y), (W, y)], fill=(14, 13, 20))
    d.text((40, 20), "ROUND 11 SLICES", font=f_num(54), fill=(255, 255, 255))
    d.text((44, 84), "Screens & Data (C)  |  upright glyph + value  |  EVADE and AFFLICT as used in the combat mockups, plus the reserved library",
           font=f_mono(17, False), fill=(190, 190, 200))
    g, v = PROGRAMS["PROXY"]["col"], PROGRAMS["VIRUS"]["col"]
    # ---------------- top: in use
    d.rectangle([0, 128, 8, 560], fill=(255, 214, 64))
    d.text((26, 124), "IN USE", font=f_num(34), fill=(255, 214, 64))
    hp = Image.open(os.path.join(CACHE, "hero_PROXY.png"))
    hv = Image.open(os.path.join(CACHE, "hero_VIRUS.png"))
    im.paste(hp, (30, 176), hp)
    im.paste(hv, (30 + hp.width + 30, 176), hv)
    ly = 176 + hp.height + 6
    label(d, 36, ly, "EVADE  (PROXY)  double chevron", "road-sign detour: hard 90-degree turn,", g)
    d.text((36, ly + 46), "the packet takes it; old road struck out", font=f_mono(14, False), fill=(185, 185, 195))
    label(d, 66 + hp.width, ly, "AFFLICT  (VIRUS)  biohazard", "ooze slides from the rim, drips, pools;", v)
    d.text((66 + hp.width, ly + 46), "cells under the pools turn violet", font=f_mono(14, False), fill=(185, 185, 195))
    x = 110 + 2 * hp.width
    mid = Image.open(os.path.join(CACHE, "mid.png"))
    im.paste(mid, (x, 150), mid)
    d.text((x + 10, 150 + mid.height - 6), "r = 150 (Breaker mock)", font=f_mono(14, False), fill=(170, 170, 180))
    sm = Image.open(os.path.join(CACHE, "small.png"))
    sx = x + mid.width + 26
    im.paste(sm, (sx, 190), sm)
    gs = grey(sm)
    im.paste(gs, (sx, 190 + sm.height + 20), gs)
    d.text((sx, 190 + sm.height + 2), "r = 60", font=f_mono(14, False), fill=(170, 170, 180))
    d.text((sx, 190 + 2 * sm.height + 22), "r = 60 grey", font=f_mono(14, False), fill=(170, 170, 180))
    gx = sx + sm.width + 30
    d.text((gx, 150), "GREYSCALE", font=f_ui(18, b"Bold SemiCondensed"), fill=(220, 220, 230))
    for i, h in enumerate((hp, hv)):
        t = grey(h).resize((int(h.width * 0.55), int(h.height * 0.55)), Image.LANCZOS)
        im.paste(t, (gx, 180 + i * (t.height + 18)), t)
    # ---------------- bottom: library
    d.rectangle([0, 600, 8, 1050], fill=(150, 150, 170))
    d.text((26, 596), "LIBRARY  -  kept, not in use", font=f_num(34), fill=(200, 200, 215))
    y0 = 650
    burn = Image.open(os.path.join(CACHE, "burn.png"))
    im.paste(burn, (30, y0), burn)
    label(d, 36, y0 + burn.height + 6, "reserved: BURN/DISSOLVE effect", "round 10 VIRUS A screen:", (230, 150, 255))
    d.text((36, y0 + burn.height + 52), "blotches eat a hex dump", font=f_mono(14, False), fill=(185, 185, 195))
    xx = 30 + 330
    for opt, t2 in (("BIG", "one large mask, glitch band, RGB split"), ("CROWD", "anonymous crowd, one mask lit")):
        m = Image.open(os.path.join(CACHE, "mask_%s.png" % opt))
        im.paste(m, (xx, y0), m)
        label(d, xx + 6, y0 + m.height + 6, "mask backdrop - program TBD", t2, (210, 215, 235))
        xx += 330
    # reserved vial icon
    px0, py0 = xx + 10, y0 + 10
    d.rounded_rectangle([px0, py0, px0 + 200, py0 + 200], radius=16, fill=(30, 18, 40), outline=(120, 70, 160), width=2)
    gl = glyph_rgba("VIAL", 150, 11)
    im.paste(gl, (px0 + 100 - gl.width // 2, py0 + 100 - gl.height // 2), gl)
    label(d, px0 + 4, y0 + 236, "reserved icon", "poison vial (round 10 VIRUS A icon)", (230, 150, 255))
    # notes
    nx = 1430
    notes = [
        ("EVADE", g, ["Icon back to round 6's double chevron.", "Screen: a road-sign detour (hard turn)", "replaces the zigzag hops that read as", "lightning. The bend sits in the top band,", "the shaft beside the value block, so the", "read plate never covers the turn."]),
        ("AFFLICT", v, ["Biohazard icon + ooze screen.", "Peak brightness kept below EXPLOIT."]),
        ("GUY FAWKES MASK", (210, 215, 235), ["No longer an icon: a screen backdrop", "for a program still to be chosen."]),
    ]
    yy = 640
    for head, col, lines in notes:
        d.text((nx, yy), head, font=f_ui(20, b"Bold SemiCondensed"), fill=col)
        yy += 28
        for ln in lines:
            d.text((nx, yy), ln, font=f_mono(14, False), fill=(200, 200, 210))
            yy += 19
        yy += 12
    im = bloom(im, 1, 0.35, 0.62)
    im.save(os.path.join(OUT, "slices_r11.png"))
    print("saved slices_r11.png", flush=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("render", "all"):
        render_assets()
    if what in ("compose", "all"):
        compose()

