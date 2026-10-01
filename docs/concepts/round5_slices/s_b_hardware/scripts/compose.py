"""Pillow: compose the Blender renders into the deliverables.

python compose.py  ->  programs_sheet.png, wheel_player.png, wheel_enemy.png, small_and_grey.png
(reads WORK/sheet.png, WORK/player.png, WORK/enemy.png)
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageOps

import common as C
import ui

MATERIAL = {
    "ATTACK": "anodised pink aluminium, crowbar notch",
    "CRITICAL": "cracked glass over a hot core",
    "DEFEND": "cyan anodised heat-sink fins",
    "SHIELD": "frosted acrylic, caged glowing cube",
    "EVADE": "green carbon weave, mirror tiles",
    "HEAL": "PCB, green tape, fresh solder",
    "AFFLICT": "violet silicone, pustules",
    "DEPLOY": "lavender plate, ribbon, seam",
    "MISS": "bare primer, rivets",
}
PLATE = {"ATTACK": 0.5, "CRITICAL": 0.62, "DEFEND": 0.6, "SHIELD": 0.45, "EVADE": 0.55,
         "HEAL": 0.6, "AFFLICT": 0.5, "DEPLOY": 0.45, "MISS": 0.3}
W, H = 1920, 1080


def w2p(x, y, cx=960.0, cy=540.0, ppu=C.PPU):
    return cx + x * ppu, cy - y * ppu


def dress(render, labels, ppu=C.PPU, plate_k=1.0, bloom_gain=0.6):
    """render: RGBA render. labels: list of (typ, ticks, value, px, py, angle_deg).
    Returns (tiles_layer, glow_layer)."""
    pl = Image.new("L", render.size, 0)
    for typ, t, v, x, y, ang in labels:
        ch = ui.chord_px(t, ppu)
        g = min(ch * 0.34, 62 * ppu / C.PPU)
        wide = t >= 5
        w = (g * 2.6 if wide else g * 1.6)
        h = (g * 1.5 if wide else g * 2.6)
        p = ui.plate(render.size, x, y, w, h, ang, PLATE[typ] * plate_k)
        pl = Image.fromarray(np.maximum(np.array(pl), np.array(p)))
    base = ui.apply_plates(render, pl)
    glow = ui.bloom(render, thresh=215, radius=max(3, int(10 * ppu / C.PPU)), gain=bloom_gain)
    for typ, t, v, x, y, ang in labels:
        _, _, kind = C.PROGRAMS[typ]
        lab = ui.label(kind, v, ui.chord_px(t, ppu), wide=t >= 5, scale=ppu / C.PPU)
        ui.place(base, lab, x, y, ang)
    return base, glow


def finish(bg, layer, glow, shadow=True):
    if shadow:
        bg.alpha_composite(ui.drop_shadow(layer))
    bg.alpha_composite(layer)
    return ui.add_glow(bg, glow)


def footer(img, title, sub):
    d = ImageDraw.Draw(img)
    d.rectangle([0, H - 84, 800, H], fill=(8, 6, 12, 235))
    d.rectangle([0, H - 84, 6, H], fill=(255, 61, 168, 255))
    ui.text(img, (22, H - 78), title, 34, path=C.FONT_NUM)
    ui.text(img, (22, H - 32), sub, 19, fill=(200, 196, 210, 255), path=C.FONT_MONO)


# ---------------------------------------------------------------- programs sheet
def programs_sheet():
    r = Image.open(os.path.join(C.WORK, "sheet.png")).convert("RGBA")
    labels = []
    for typ, t, v, hx, hy in C.SHEET:
        x, y = w2p(hx, hy + C.R_ANCHOR)
        labels.append((typ, t, v, x, y, 0.0))
    layer, glow = dress(r, labels)
    bg = ui.background(W, H, (120, 90, 200))
    img = finish(bg, layer, glow)
    d = ImageDraw.Draw(img)
    ui.text(img, (40, 26), "HARDWARE MATERIALS", 44, path=C.FONT_NUM)
    ui.text(img, (44, 84), "s_b_hardware  |  every program is a bevelled slab of salvaged tech  |  "
            "Blender Cycles tiles, glyph + value overlaid", 19, fill=(190, 186, 205, 255), path=C.FONT_MONO)
    for i, (typ, t, v, hx, hy) in enumerate(C.SHEET):
        name, hexc, _ = C.PROGRAMS[typ]
        x, ytop = w2p(hx, hy + C.R_IN * math.cos(C.half_angle(t)))
        col = tuple(int(c * 255) for c in C.hexrgb(hexc)) + (255,)
        if i < 9:
            ui.text(img, (x, ytop + 12), name, 28, fill=col, path=C.FONT_NUM, anchor="ma")
            ui.text(img, (x, ytop + 50), "%s  %d-tick" % (typ, t), 15, fill=(170, 166, 185, 255),
                    path=C.FONT_MONO, anchor="ma")
            ui.text(img, (x, ytop + 68), MATERIAL[typ], 15, fill=(140, 136, 155, 255),
                    path=C.FONT_MONO, anchor="ma")
        else:
            ui.text(img, (x, ytop + 12), "%s  %d TICKS" % (name, t), 24, fill=col, path=C.FONT_NUM,
                    anchor="ma")
    xr, yr = w2p(5.8, -3.0)
    ui.text(img, (1450, 770), "WIDTH VARIANTS", 30, path=C.FONT_NUM)
    for k, line in enumerate(["Same material, same atlas cell:",
                              "fins re-flow to the arc, the label",
                              "keeps 34% of the chord. At 5 ticks",
                              "the glyph sits beside the value."]):
        ui.text(img, (1452, 812 + k * 24), line, 17, fill=(185, 180, 200, 255), path=C.FONT_MONO)
    img.convert("RGB").save(os.path.join(C.OUT, "programs_sheet.png"))


# ---------------------------------------------------------------- wheels
WCX, WCY = 960, 470


def wheel_layer(kind):
    """The dressed wheel (transparent) on a W x H canvas, wheel centre at (WCX, WCY)."""
    r = Image.open(os.path.join(C.WORK, kind + ".png")).convert("RGBA")
    full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    full.paste(r, (WCX - r.width // 2, WCY - r.height // 2))
    spec = C.PLAYER_WHEEL if kind == "player" else C.ENEMY_WHEEL
    labels = []
    for typ, t, v, cdeg in C.wheel_slices(spec):
        a = math.radians(cdeg)
        x, y = w2p(C.R_ANCHOR * math.cos(a), C.R_ANCHOR * math.sin(a), WCX, WCY)
        labels.append((typ, t, v, x, y, cdeg - 90.0))
    layer, glow = dress(full, labels, plate_k=0.8 if kind == "enemy" else 1.0)
    # hub text
    if kind == "player":
        ui.text(layer, (WCX, WCY - 22), "BREAKER", 46, path=C.FONT_NUM, anchor="mm")
        ui.text(layer, (WCX, WCY + 26), "salvage rig", 19, fill=(255, 150, 210, 255), anchor="mm")
    else:
        ui.text(layer, (WCX, WCY - 30), "COLLECTIONS", 34, path=C.FONT_NUM, anchor="mm")
        ui.text(layer, (WCX, WCY + 6), "AGENT", 34, path=C.FONT_NUM, anchor="mm")
        ui.text(layer, (WCX, WCY + 44), "Meridian Freight", 18, fill=(255, 160, 70, 255), anchor="mm")
    return layer, glow


def hp_arc(img, hp, hpmax, col=(110, 230, 120)):
    d = ImageDraw.Draw(img)
    n = 28
    r0, r1 = 452, 482
    a0, a1 = 152.0, 28.0  # screen angles (deg, y down) under the wheel, left to right
    for i in range(n):
        aa = math.radians(a0 + (a1 - a0) * (i + 0.5) / n)
        pass
        da = math.radians((a1 - a0) / n * 0.32)
        pts = []
        for rr, s in ((r0, -1), (r1, -1), (r1, 1), (r0, 1)):
            pts.append((WCX + rr * math.cos(aa + s * da), WCY + rr * math.sin(aa + s * da)))
        on = i < round(n * hp / hpmax)
        d.polygon(pts, fill=col + (255,) if on else (40, 50, 44, 255))
    ui.text(img, (WCX, WCY + 545), "%d/%d" % (hp, hpmax), 64, fill=col + (255,), path=C.FONT_NUM, anchor="mb")


def wheel_image(kind):
    layer, glow = wheel_layer(kind)
    tint = (255, 61, 168) if kind == "player" else (255, 138, 30)
    bg = ui.background(W, H, tint, seed=5 if kind == "player" else 6)
    img = finish(bg, layer, glow)
    if kind == "player":
        hp_arc(img, 60, 60)
        footer(img, "PLAYER WHEEL  -  salvaged hardware programs",
               "10 programs on 30 ticks, one material family each")
    else:
        hp_arc(img, 40, 40)
        footer(img, "ENEMY WHEEL  -  Meridian, corporate machined",
               "steel hub band | orange powder-coat | hazard rim")
        side_legend(img)
    return img


def side_legend(img):
    """The inlay rule: every Meridian slice is the same machined part; only glyph and inlay change."""
    x0, y0 = 1480, 250
    ui.text(img, (x0, y0 - 56), "TYPE = GLYPH + INLAY", 30, path=C.FONT_NUM)
    ui.text(img, (x0, y0 - 18), "same part, same finish", 17, fill=(190, 186, 200, 255), path=C.FONT_MONO)
    d = ImageDraw.Draw(img)
    for k, typ in enumerate(("ATTACK", "DEFEND", "AFFLICT", "SHIELD", "EVADE", "CRITICAL", "MISS")):
        name, hexc, kind = C.PROGRAMS[typ]
        col = tuple(int(c * 255) for c in C.hexrgb(hexc))
        y = y0 + 16 + k * 66
        # swatch: steel | orange | inlay | hazard
        d.rounded_rectangle([x0, y, x0 + 190, y + 54], 6, fill=(214, 104, 28, 255),
                            outline=(150, 152, 158, 255), width=3)
        d.rectangle([x0 + 3, y + 3, x0 + 26, y + 51], fill=(150, 152, 158, 255))
        d.rectangle([x0 + 140, y + 3, x0 + 187, y + 51], fill=(18, 18, 20, 255))
        for s in range(-12, 50, 12):
            d.polygon([(x0 + 140 + s, y + 51), (x0 + 146 + s, y + 51), (x0 + 158 + s, y + 3),
                       (x0 + 152 + s, y + 3)], fill=(255, 194, 26, 255))
        d.rectangle([x0 + 188, y + 3, x0 + 190, y + 51], fill=(150, 152, 158, 255))
        d.rectangle([x0 + 132, y + 3, x0 + 139, y + 51], fill=col + (255,))
        lab = ui.label(kind, 0 if typ == "MISS" else 6, 120, wide=True, scale=0.6)
        img.alpha_composite(lab, (x0 + 34, y + 27 - lab.height // 2))
        ui.text(img, (x0 + 210, y + 27), name, 26, fill=col + (255,), path=C.FONT_NUM, anchor="lm")


def small_lod(size_r=60):
    """r = 60 rebuilt the way the game would: tile art downscaled (texture LOD), plates
    stronger, labels drawn natively at small size with a minimum glyph of 10 px."""
    r = Image.open(os.path.join(C.WORK, "player.png")).convert("RGBA")
    k = size_r / (C.R_OUT * C.PPU)
    n = int(round(r.width * k))
    sr = r.resize((n, n), Image.LANCZOS)
    ppu = C.PPU * k
    c = n / 2.0
    labels = []
    for typ, t, v, cdeg in C.wheel_slices(C.PLAYER_WHEEL):
        a = math.radians(cdeg)
        x, y = w2p(C.R_ANCHOR * math.cos(a), C.R_ANCHOR * math.sin(a), c, c, ppu)
        labels.append((typ, t, v, x, y, cdeg - 90.0))
    layer, glow = dress(sr, labels, ppu=ppu, plate_k=1.4)
    bg = ui.background(n, n, (255, 61, 168), seed=5)
    bg.alpha_composite(layer)
    return bg


def small_and_grey(player_img_layer):
    layer, glow = player_img_layer
    bg = ui.background(W, H, (255, 61, 168), seed=5)
    hero = finish(bg, layer, glow)
    hp_arc(hero, 60, 60)
    R = 470
    crop = hero.crop((WCX - R, WCY - R - 10, WCX + R, WCY + R - 10))
    out = ui.background(W, H, (80, 80, 90), seed=8)
    g = ImageOps.grayscale(crop).convert("RGBA").resize((900, 900), Image.LANCZOS)
    out.alpha_composite(g, (1000, 110))
    ui.text(out, (1000, 40), "HERO SIZE, GREYSCALE", 34, path=C.FONT_NUM)
    ui.text(out, (1002, 82), "r = 360 px wheel, shown at 0.96", 17, fill=(180, 176, 190, 255), path=C.FONT_MONO)
    # r = 60: (a) the hero frame shrunk, (b) the LOD build (labels drawn at size)
    k = 60.0 / 360.0
    sz = int(round(crop.width * k))
    naive = crop.resize((sz, sz), Image.LANCZOS)
    lod = small_lod(60)
    ui.text(out, (60, 40), "r = 60 px, ACTUAL SIZE", 34, path=C.FONT_NUM)
    x = 60
    for im, cap in ((naive, "A: hero shrunk"), (ImageOps.grayscale(naive).convert("RGBA"), "A grey"),
                    (lod, "B: LOD labels"), (ImageOps.grayscale(lod).convert("RGBA"), "B grey")):
        out.alpha_composite(im, (x, 100 + (sz - im.height) // 2))
        ui.text(out, (x, 100 + sz + 6), cap, 16, fill=(180, 176, 190, 255), path=C.FONT_MONO)
        x += sz + 50
    ui.text(out, (60, 320), "ZOOMED x3 (nearest), A left, B right", 26, path=C.FONT_NUM)
    za = naive.resize((sz * 3, sz * 3), Image.NEAREST)
    zb = lod.resize((lod.width * 3, lod.height * 3), Image.NEAREST)
    out.alpha_composite(za, (30, 370))
    out.alpha_composite(zb, (30 + za.width + 10, 370 + (za.height - zb.height) // 2))
    ui.text(out, (60, 370 + za.height + 20),
            "B = what Godot should do below ~r 120: same tile art, label drawn at a 10 px minimum,",
            16, fill=(190, 186, 200, 255), path=C.FONT_MONO)
    ui.text(out, (60, 370 + za.height + 42), "plate 1.4x darker, shader FX off.", 16,
            fill=(190, 186, 200, 255), path=C.FONT_MONO)
    out.convert("RGB").save(os.path.join(C.OUT, "small_and_grey.png"))


def main():
    programs_sheet()
    for kind in ("player", "enemy"):
        wheel_image(kind).convert("RGB").save(os.path.join(C.OUT, "wheel_%s.png" % kind))
    small_and_grey(wheel_layer("player"))
    print("composed ->", C.OUT)


if __name__ == "__main__":
    main()
