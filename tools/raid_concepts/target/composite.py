"""Composite the raid target frames: grade + bloom on the Blender render, then the 2D UI (Pillow).

    python composite.py --dir D:/rc_tmp/raid_design_lab/target/final [--frames plan,reveal,impact]

Reads <dir>/<frame>_raw.png + <frame>_nodes.json, writes <dir>/<frame>.png (1920x1080).
Everything is deterministic (seeded grain).
"""
import argparse
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
FONTS = os.path.join(ROOT, "assets", "fonts")
W, H = 1920, 1080
K = 2  # UI supersample

# palette (docs/STYLE_GUIDE.md section 2 + the raid's own)
COBALT = (0x3D, 0x6B, 0xFF)
COBALT_HOT = (0x9F, 0xC0, 0xFF)
GOLD = (0xFF, 0xD2, 0x4D)
AMBER = (0xFF, 0xB0, 0x20)
EMBER = (0xFF, 0x6A, 0x1A)
ACID = (0xD4, 0xFF, 0x00)
RED = (0xFF, 0x3D, 0x4D)
PAPER = (0xF2, 0xEE, 0xE4)
GLASS = (5, 13, 28)
GREY = (0x8A, 0x92, 0xA6)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), int(size * K))


F_ANTON = lambda s: font("Anton-Regular.ttf", s)
F_MONO = lambda s: font("ShareTechMono-Regular.ttf", s)
F_COND = lambda s: font("IBMPlexSansCondensed-Medium.ttf", s)


class Ui:
    def __init__(self):
        self.img = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img, "RGBA")

    def p(self, v):
        return [(x * K, y * K) for x, y in v]

    def rect(self, box, fill=None, outline=None, width=0, r=0):
        b = [box[0] * K, box[1] * K, box[2] * K, box[3] * K]
        if r:
            self.d.rounded_rectangle(b, radius=r * K, fill=fill, outline=outline, width=int(width * K))
        else:
            self.d.rectangle(b, fill=fill, outline=outline, width=int(width * K))

    def circle(self, c, rad, fill=None, outline=None, width=0):
        self.d.ellipse([(c[0] - rad) * K, (c[1] - rad) * K, (c[0] + rad) * K, (c[1] + rad) * K],
                       fill=fill, outline=outline, width=int(width * K))

    def line(self, pts, fill, width=2):
        self.d.line(self.p(pts), fill=fill, width=int(width * K), joint="curve")

    def poly(self, pts, fill=None, outline=None):
        self.d.polygon(self.p(pts), fill=fill, outline=outline)

    def arc(self, c, rad, a0, a1, fill, width):
        self.d.arc([(c[0] - rad) * K, (c[1] - rad) * K, (c[0] + rad) * K, (c[1] + rad) * K], a0, a1,
                   fill=fill, width=int(width * K))

    def dashed_circle(self, c, rad, fill, width=3, n=16):
        for i in range(n):
            a0 = i * 360 / n
            self.arc(c, rad, a0, a0 + 360 / n * 0.55, fill, width)

    def text(self, xy, s, f, fill, anchor="la", track=0):
        if track:
            # manual letter spacing
            total = sum(self.d.textlength(ch, font=f) for ch in s) + track * K * (len(s) - 1)
            x = xy[0] * K
            if anchor[0] == "m":
                x -= total / 2
            elif anchor[0] == "r":
                x -= total
            for ch in s:
                self.d.text((x, xy[1] * K), ch, font=f, fill=fill, anchor="l" + anchor[1])
                x += self.d.textlength(ch, font=f) + track * K
        else:
            self.d.text((xy[0] * K, xy[1] * K), s, font=f, fill=fill, anchor=anchor)

    def glyph_tile(self, size):
        t = Image.new("RGBA", (size * K * 2, size * K * 2), (0, 0, 0, 0))
        return t, ImageDraw.Draw(t, "RGBA")

    def paste_tile(self, tile, c):
        self.img.alpha_composite(tile, (int(c[0] * K - tile.width / 2), int(c[1] * K - tile.height / 2)))


def a(c, al):
    return (c[0], c[1], c[2], int(al))


# ---------------------------------------------------------------- glyphs
def wrench(ui, c, size, color):
    """The DOWN wrench: a handle with an open-jaw head, 45 degrees."""
    t, td = ui.glyph_tile(size)
    s = size * K
    cx, cy = t.width / 2, t.height / 2
    # handle
    td.rounded_rectangle([cx - s * 0.11, cy - s * 0.1, cx + s * 0.11, cy + s * 0.62], radius=s * 0.1, fill=color)
    # head
    td.ellipse([cx - s * 0.3, cy - s * 0.62, cx + s * 0.3, cy - s * 0.02], fill=color)
    # jaw
    td.polygon([(cx - s * 0.1, cy - s * 0.7), (cx + s * 0.1, cy - s * 0.7), (cx + s * 0.07, cy - s * 0.3), (cx - s * 0.07, cy - s * 0.3)],
               fill=(0, 0, 0, 0))
    t = t.rotate(40, resample=Image.BICUBIC)
    ui.paste_tile(t, c)


def flame(ui, c, size, color):
    s = size
    pts = [(c[0], c[1] - s), (c[0] + s * 0.55, c[1] - s * 0.1), (c[0] + s * 0.45, c[1] + s * 0.55),
           (c[0], c[1] + s * 0.85), (c[0] - s * 0.45, c[1] + s * 0.55), (c[0] - s * 0.55, c[1] - s * 0.05),
           (c[0] - s * 0.15, c[1] + s * 0.1)]
    ui.poly(pts, fill=color)
    ui.poly([(c[0], c[1] + s * 0.2), (c[0] + s * 0.22, c[1] + s * 0.55), (c[0], c[1] + s * 0.7), (c[0] - s * 0.22, c[1] + s * 0.55)],
            fill=(255, 220, 140))


def spoof_icon(ui, c, size, color, w=5):
    s = size
    ui.line([(c[0] - s * 0.9, c[1] - s * 0.6), (c[0] - s * 0.3, c[1]), (c[0] - s * 0.9, c[1] + s * 0.6)], color, w)
    ui.line([(c[0] - s * 0.1, c[1] - s * 0.6), (c[0] + s * 0.5, c[1]), (c[0] - s * 0.1, c[1] + s * 0.6)], color, w)
    ui.line([(c[0] + s * 0.85, c[1] - s * 0.65), (c[0] + s * 0.85, c[1] + s * 0.65)], color, w)


def hunter_icon(ui, c, size, color, w=5, crossed=False):
    s = size
    ui.line([(c[0], c[1] - s * 0.9), (c[0], c[1] + s * 0.4)], color, w)
    ui.poly([(c[0] - s * 0.5, c[1] + s * 0.3), (c[0] + s * 0.5, c[1] + s * 0.3), (c[0], c[1] + s * 0.95)], fill=color)
    if crossed:
        ui.line([(c[0] - s * 0.95, c[1] - s * 0.8), (c[0] + s * 0.95, c[1] + s * 0.95)], RED, w + 1)


def shape(ui, kind, c, size, color, width=5, fill=None):
    s = size
    if kind == "square":
        ui.rect([c[0] - s, c[1] - s, c[0] + s, c[1] + s], fill=fill, outline=color, width=width, r=3)
    elif kind == "circle":
        ui.circle(c, s * 1.08, fill=fill, outline=color, width=width)
    else:
        ui.poly([(c[0], c[1] - s * 1.15), (c[0] + s * 1.15, c[1] + s * 0.85), (c[0] - s * 1.15, c[1] + s * 0.85)],
                fill=fill, outline=color)
        if fill is None:
            pts = [(c[0], c[1] - s * 1.15), (c[0] + s * 1.15, c[1] + s * 0.85), (c[0] - s * 1.15, c[1] + s * 0.85), (c[0], c[1] - s * 1.15)]
            ui.line(pts, color, width)


def badge_value(ui, c, value, state="live"):
    """The asset's value: a dark disc, a warm ring, the number."""
    ring = {"live": GOLD, "ghost": a(GOLD, 200), "dark": GREY, "down": (120, 126, 142)}[state]
    ui.circle((c[0], c[1] + 3), 31, fill=(0, 0, 0, 90))
    ui.circle(c, 29, fill=(8, 11, 26, 240))
    if state == "ghost":
        ui.dashed_circle(c, 27, ring, 4, 14)
    else:
        ui.circle(c, 27, outline=ring, width=4)
    col = {"live": GOLD, "ghost": a(GOLD, 220), "dark": GREY, "down": (150, 156, 170)}[state]
    ui.text(c, str(value), F_ANTON(34), col, "mm")


def chip(ui, c, label, color, f=None, pad=14, h=32, icon=None):
    f = f or F_COND(20)
    w = ui.d.textlength(label, font=f) / K + pad * 2 + (28 if icon else 0)
    x0, y0 = c[0] - w / 2, c[1] - h / 2
    ui.rect([x0, y0, x0 + w, y0 + h], fill=(6, 10, 22, 235), outline=color, width=2, r=6)
    tx = c[0] + (14 if icon else 0)
    ui.text((tx, c[1] + 1), label, f, color, "mm", track=1.5)
    if icon:
        icon(ui, (x0 + 24, c[1]), color)
    return w


# ---------------------------------------------------------------- grade
def grade(raw):
    im = np.asarray(raw.convert("RGB").resize((W, H), Image.LANCZOS), dtype=np.float32) / 255.0
    lum = (im @ np.array([0.299, 0.587, 0.114], dtype=np.float32))
    # bloom from the bright, saturated light
    mask = np.clip((lum - 0.62) / 0.45, 0, 1)[..., None]
    src = Image.fromarray((np.clip(im * mask, 0, 1) * 255).astype(np.uint8))
    bloom = np.zeros_like(im)
    for rad, wgt in ((4, 0.18), (14, 0.28), (46, 0.34), (120, 0.26)):
        bloom += np.asarray(src.filter(ImageFilter.GaussianBlur(rad)), dtype=np.float32) / 255.0 * wgt
    out = im + bloom
    # filmic-ish curve
    out = 1.0 - np.exp(-out * 1.35)
    out = out ** 0.95
    # slight lift of the shadows toward navy, vignette
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx / W) - 0.5) ** 2 * 1.2 + ((yy / H) - 0.52) ** 2) * 1.35
    vig = np.clip(1.0 - (d - 0.38) * 0.95, 0.35, 1.0)[..., None]
    out = out * vig + np.array([0.012, 0.018, 0.045], dtype=np.float32) * (1 - vig)
    # subtle chromatic split at the edges
    shift = 2
    out[:, shift:, 0] = out[:, :-shift, 0] * 0.5 + out[:, shift:, 0] * 0.5
    out[:, :-shift, 2] = out[:, shift:, 2] * 0.5 + out[:, :-shift, 2] * 0.5
    rng = np.random.default_rng(1337)
    out += (rng.random((H, W, 1), dtype=np.float32) - 0.5) * 0.004
    return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")


def finalize(base, ui, glow=0.75):
    layer = ui.img.resize((W, H), Image.LANCZOS)
    arr = np.asarray(layer, dtype=np.float32) / 255.0
    # glow from the UI's bright strokes
    rgb = arr[..., :3] * arr[..., 3:4]
    bright = np.clip((rgb.max(axis=2, keepdims=True) - 0.55) / 0.45, 0, 1) * rgb
    g_src = Image.fromarray((np.clip(bright, 0, 1) * 255).astype(np.uint8))
    g = np.zeros((H, W, 3), dtype=np.float32)
    for rad, wgt in ((3, 0.5), (10, 0.5), (28, 0.45)):
        g += np.asarray(g_src.filter(ImageFilter.GaussianBlur(rad)), dtype=np.float32) / 255.0 * wgt
    b = np.asarray(base, dtype=np.float32) / 255.0
    b = np.clip(b + g * glow, 0, 1)
    out = Image.fromarray((b * 255 + 0.5).astype(np.uint8), "RGB").convert("RGBA")
    out.alpha_composite(layer)
    return out.convert("RGB")


# ---------------------------------------------------------------- shared HUD
def hud_top(ui, frame, heat=50):
    ui.rect([0, 0, W, 104], fill=(2, 4, 12, 170))
    ui.line([(0, 104), (W, 104)], a(AMBER, 120), 2)
    # HEAT meter
    flame(ui, (62, 52), 20, EMBER)
    bx0, bx1, by0, by1 = 104, 560, 40, 64
    ui.rect([bx0, by0, bx1, by1], fill=(14, 18, 36, 255), outline=(70, 80, 120, 255), width=2)
    fw = (bx1 - bx0) * heat / 100.0
    ui.rect([bx0 + 2, by0 + 2, bx0 + fw, by1 - 2], fill=EMBER)
    ui.rect([bx0 + 2, by0 + 2, bx0 + fw, by0 + 9], fill=(255, 170, 90))
    for pct, lab in ((25, ""), (50, "+1 BEAM"), (75, "+2 BEAMS")):
        x = bx0 + (bx1 - bx0) * pct / 100.0
        ui.line([(x, by0 - 8), (x, by1 + 8)], PAPER if pct == 50 else (120, 130, 170), 3 if pct == 50 else 2)
        if lab:
            ui.text((x, by1 + 26), lab, F_MONO(17), PAPER if pct == 50 else (150, 160, 200), "mm")
    ui.poly([(bx0 + fw, by0 - 12), (bx0 + fw - 8, by0 - 24), (bx0 + fw + 8, by0 - 24)], fill=PAPER)
    ui.text((bx1 + 22, 52), str(heat), F_ANTON(52), EMBER, "lm")
    # RAID n/3
    ui.text((780, 38), "RAID", F_MONO(18), (170, 180, 215), "mm", track=3)
    for i in range(3):
        c = (742 + i * 38, 70)
        if i == 0:
            ui.circle(c, 11, fill=a(GOLD, 255), outline=GOLD, width=3)
        else:
            ui.circle(c, 11, outline=(110, 120, 160), width=3)


def hud_home(ui, hp_after, flash=False):
    ui.text((1040, 38), "HOME", F_MONO(18), (170, 180, 215), "mm", track=3)
    for i in range(3):
        x = 1004 + i * 36
        if i < hp_after:
            ui.rect([x, 56, x + 26, 82], fill=GOLD)
        else:
            ui.rect([x, 56, x + 26, 82], outline=RED, width=3)
            ui.line([(x + 3, 59), (x + 23, 79)], RED, 3)
            ui.line([(x + 23, 59), (x + 3, 79)], RED, 3)


def hud_chain(ui, frame):
    """The sweep chain top right: beam 1, beam 2 (sealed or revealed), the hunter."""
    x0, y = 1380, 56
    ui.text((x0 - 36, 28), "SWEEP", F_MONO(18), (170, 180, 215), "lm", track=3)
    xs = [x0, x0 + 110, x0 + 220]
    ui.line([(xs[0] + 24, y + 6), (xs[1] - 24, y + 6)], a(COBALT, 190), 4)
    ui.line([(xs[1] + 24, y + 6), (xs[2] - 24, y + 6)], a(COBALT, 190), 4)
    c1, c2, c3 = [(x, y + 6) for x in xs]
    done = frame in ("reveal", "impact")
    ui.circle(c1, 22, fill=COBALT if not done else (24, 36, 90), outline=COBALT_HOT, width=2)
    ui.text(c1, "1", F_ANTON(26), PAPER, "mm")
    if frame == "plan":
        ui.dashed_circle(c2, 22, COBALT_HOT, 3, 12)
        ui.text(c2, "?", F_ANTON(28), COBALT_HOT, "mm")
    else:
        act = frame == "reveal"
        ui.circle(c2, 22, fill=COBALT if act else (24, 36, 90), outline=PAPER if act else COBALT_HOT, width=3 if act else 2)
        ui.text(c2, "2", F_ANTON(26), PAPER, "mm")
    act3 = frame == "impact"
    ui.circle(c3, 22, fill=COBALT if act3 else (14, 20, 54), outline=PAPER if act3 else COBALT, width=3 if act3 else 2)
    hunter_icon(ui, c3, 9, PAPER if act3 else COBALT_HOT, 3)
    ui.text((x0 - 36, 94), "", F_MONO(14), PAPER, "lm")


def draw_downs(ui, N, which):
    for key, dy in which:
        x, y = N[key]
        c = (x, y - 56)
        ui.circle(c, 31, fill=(0, 0, 0, 90))
        ui.circle(c, 29, fill=(18, 20, 28, 245), outline=(150, 156, 172), width=4)
        wrench(ui, c, 38, (205, 210, 225, 255))


# ---------------------------------------------------------------- frames
def kit_tray(ui):
    """The kit: the three levers the player placed this leg (warm, the cell's side of the board)."""
    ui.rect([470, 902, 1450, 1050], fill=(2, 5, 14, 205), r=10)
    ui.line([(470, 902), (1450, 902)], a(AMBER, 170), 2)
    ui.text((498, 922), "KIT", F_MONO(18), (200, 210, 235), "lm", track=4)
    items = [("GHOST", "hides one asset", "g"), ("DECOY", "beam stops here", "d"), ("GO DARK", "no income", "k")]
    for i, (nm, sub, kind) in enumerate(items):
        x0 = 490 + i * 320
        ui.rect([x0, 938, x0 + 300, 1038], fill=(10, 14, 30, 245), outline=AMBER if kind != "k" else GREY, width=3, r=10)
        c = (x0 + 52, 988)
        if kind == "g":
            ui.dashed_circle(c, 26, GOLD, 5, 12)
        elif kind == "d":
            ui.poly([(c[0], c[1] - 30), (c[0] + 30, c[1]), (c[0], c[1] + 30), (c[0] - 30, c[1])], outline=GOLD)
            ui.line([(c[0], c[1] - 30), (c[0] + 30, c[1]), (c[0], c[1] + 30), (c[0] - 30, c[1]), (c[0], c[1] - 30)], GOLD, 5)
        else:
            ui.circle(c, 27, fill=(10, 12, 18, 255), outline=GREY, width=5)
        ui.text((x0 + 100, 972), nm, F_ANTON(32), PAPER, "lm", track=2)
        ui.text((x0 + 100, 1008), sub, F_MONO(16), (170, 180, 215), "lm")
        ui.rect([x0 + 222, 948, x0 + 290, 970], fill=ACID, r=5)
        ui.text((x0 + 256, 959), "PLACED", F_MONO(13), (14, 18, 8), "mm")


def frame_plan(N, ui):
    hud_top(ui, "plan", 50)
    hud_home(ui, 3)
    hud_chain(ui, "plan")
    # value badges
    for key, val, st in (("r1c0", 4, "live"), ("r1c1", 8, "dark"), ("r1c3", 8, "live"), ("r2c2", 4, "live"),
                         ("r3c2", 8, "live"), ("r2c3", 8, "ghost")):
        x, y = N[key]
        badge_value(ui, (x, y - 54), val, st)
    # levers: pills under the placed nodes
    x, y = N["r2c3"]
    chip(ui, (x + 118, y + 52), "GHOST", GOLD)
    x, y = N["r1c2"]
    chip(ui, (x - 128, y + 52), "DECOY", GOLD)
    x, y = N["r1c1"]
    chip(ui, (x, y + 104), "DARK", GREY)
    # HOME tag
    x, y = N["home"]
    chip(ui, (x + 178, y + 218), "HOME", PAPER)
    # sealed candidates above the pylons, beam 1 badge
    for key, kind in (("p_r2_right", "square"), ("p_r3_right", "circle"), ("p_r1_left", "triangle")):
        x, y = N[key]
        c = (x, y + 52)
        ui.circle(c, 40, fill=(6, 10, 26, 235))
        shape(ui, kind, c, 20, COBALT_HOT, 5)
        ui.circle((c[0] + 32, c[1] - 30), 15, fill=COBALT, outline=PAPER, width=2)
        ui.text((c[0] + 32, c[1] - 30), "?", F_ANTON(20), PAPER, "mm")
    x, y = N["p_r1_right"]
    c = (x, y + 52)
    ui.circle(c, 34, fill=COBALT, outline=PAPER, width=3)
    ui.text(c, "1", F_ANTON(40), PAPER, "mm")
    # hunter chevrons down column c3 and its tag
    x0, y0 = N["hunt_top"]
    x1, y1 = N["hunt_bot"]
    for i in range(1, 6):
        t = i / 6.0
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        ui.poly([(cx - 17, cy - 8), (cx, cy + 12), (cx + 17, cy - 8), (cx, cy)], fill=a(COBALT_HOT, 200))
    chip(ui, (x1 + 8, y1 + 38), "HUNTER", COBALT_HOT, icon=lambda u, c, col: hunter_icon(u, c, 8, col, 3))
    # legend
    kit_tray(ui)


def frame_reveal(N, ui):
    hud_top(ui, "reveal", 50)
    hud_home(ui, 3)
    hud_chain(ui, "reveal")
    for key, val, st in (("r1c0", 4, "live"), ("r1c1", 8, "dark"), ("r3c2", 8, "live"), ("r2c3", 8, "ghost")):
        x, y = N[key]
        badge_value(ui, (x, y - 54), val, st)
    draw_downs(ui, N, [("r1c3", 0)])
    x, y = N["r1c3"]
    ui.text((x + 44, y - 56), "8", F_ANTON(26), (150, 156, 170), "lm")
    # the real line's marker blazes, the other two collapse
    x, y = N["p_r2_right"]
    c = (x, y + 56)
    ui.circle(c, 52, fill=a(COBALT, 70))
    ui.circle(c, 44, fill=(10, 20, 70, 245))
    shape(ui, "square", c, 24, PAPER, 6, fill=COBALT)
    ui.text((c[0], c[1] + 1), "2", F_ANTON(36), PAPER, "mm")
    for key, kind in (("p_r3_right", "circle"), ("p_r1_left", "triangle")):
        x, y = N[key]
        c = (x, y + 52)
        ui.circle(c, 34, fill=(6, 10, 26, 150))
        shape(ui, kind, c, 17, a(COBALT, 130), 4)
        ui.line([(c[0] - 26, c[1] - 26), (c[0] + 26, c[1] + 26)], a(RED, 190), 4)
        ui.line([(c[0] + 26, c[1] - 26), (c[0] - 26, c[1] + 26)], a(RED, 190), 4)
    # headline
    ui.text((90, 150), "BEAM 2 UNSEALED", F_ANTON(58), COBALT_HOT, "lm", track=8)
    # the SKIP target: a bracketed reticle on the node the line will hit
    x, y = N["r2c2"]
    cx, cy = x, y + 38
    rr = 82
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py = cx + sx * rr, cy + sy * rr * 0.78
            ui.line([(px, py - sy * 28), (px, py), (px - sx * 28, py)], ACID, 5)
    badge_value(ui, (x, y - 54), 4, "live")
    chip(ui, (x - 150, y + 58), "SKIP TARGET", ACID, F_COND(20))
    # the JAM target: the hunter column
    xa, ya = N["hunt_top"]
    xb, yb = N["hunt_bot"]
    for i in range(1, 7):
        t = i / 7.0
        cx, cy = xa + (xb - xa) * t, ya + (yb - ya) * t
        ui.poly([(cx - 19, cy - 9), (cx, cy + 14), (cx + 19, cy - 9), (cx, cy)], fill=a(AMBER, 235))
    x1, y1 = N["hunt_top"]
    chip(ui, (x1 + 150, y1 + 40), "JAM TARGET", AMBER, icon=lambda u, c, col: hunter_icon(u, c, 8, col, 3))
    # spoof panel
    py0, py1 = 862, 1034
    ui.rect([410, py0 - 24, 1510, py1 + 18], fill=(2, 5, 14, 205), r=10)
    ui.line([(410, py0 - 24), (1510, py0 - 24)], a(AMBER, 170), 2)
    ui.text((440, py0 - 4), "SPOOF", F_MONO(20), (200, 210, 235), "lm", track=4)
    # decide-bar draining
    ui.rect([560, py0 - 11, 1450, py0 - 3], fill=(30, 36, 60, 255))
    ui.rect([560, py0 - 11, 560 + 890 * 0.62, py0 - 3], fill=AMBER)
    cards = [("S", "SKIP", "spoof", 440, "+2 HEAT"), ("J", "JAM", "jam", 1030, "+2 HEAT")]
    for key, name, kind, x0, cost in cards:
        ui.rect([x0, py0 + 14, x0 + 450, py1], fill=(10, 14, 30, 245), outline=AMBER, width=3, r=10)
        ui.rect([x0 + 18, py0 + 40, x0 + 92, py0 + 114], fill=ACID, r=8)
        ui.text((x0 + 55, py0 + 77), key, F_ANTON(52), (14, 18, 8), "mm")
        if kind == "spoof":
            spoof_icon(ui, (x0 + 160, py0 + 77), 26, AMBER, 7)
        else:
            hunter_icon(ui, (x0 + 160, py0 + 77), 26, AMBER, 7, crossed=True)
        ui.text((x0 + 214, py0 + 62), name, F_ANTON(60), PAPER, "lm", track=3)
        ui.text((x0 + 216, py0 + 118), cost, F_MONO(22), EMBER, "lm", track=1)
    # the countdown ring, between the cards
    c = (960, py0 + 95)
    ui.circle(c, 52, fill=(4, 8, 20, 255))
    ui.circle(c, 48, outline=(40, 48, 80), width=6)
    ui.arc(c, 48, -90, -90 + 360 * 0.62, AMBER, 7)
    ui.text((c[0], c[1] + 2), "2", F_ANTON(58), PAPER, "mm")


def frame_impact(N, ui):
    hud_top(ui, "impact", 50)
    hud_home(ui, 2)
    hud_chain(ui, "impact")
    for key, val, st in (("r1c0", 4, "live"), ("r1c1", 8, "dark"), ("r3c2", 8, "live"), ("r2c3", 8, "ghost")):
        x, y = N[key]
        badge_value(ui, (x, y - 54), val, st)
    draw_downs(ui, N, [("r1c3", 0), ("r2c2", 0)])
    for key in ("r1c3", "r2c2"):
        x, y = N[key]
        chip(ui, (x - 96, y + 18), "DOWN", (210, 215, 230), F_COND(20))
    # HOME takes the hit: -1 rises off it
    x, y = N["home"]
    ui.text((x + 56, y - 78), "-1", F_ANTON(86), RED, "lm")
    # hunter tag at the head
    x, y = N["hunt_head"]
    chip(ui, (x + 110, y - 36), "THE HUNTER", COBALT_HOT, icon=lambda u, c, col: hunter_icon(u, c, 8, col, 3))
    # outcome stamp arriving: ghost trail, then the stamp (slightly oversize, tilted)
    st = Image.new("RGBA", (860 * K, 400 * K), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st, "RGBA")
    fA, fB = F_ANTON(176), F_ANTON(70)
    col = RED
    sd.rounded_rectangle([20 * K, 20 * K, 840 * K, 380 * K], radius=18 * K, outline=col, width=12 * K, fill=(30, 4, 10, 200))
    sd.rounded_rectangle([44 * K, 44 * K, 816 * K, 356 * K], radius=10 * K, outline=a(col, 190), width=4 * K)
    sd.text((430 * K, 148 * K), "HOME -1", font=fA, fill=col, anchor="mm")
    sd.text((430 * K, 288 * K), "HOLDS", font=fB, fill=ACID, anchor="mm")
    # stamp texture: scratches (deterministic)
    rng = np.random.default_rng(5)
    alpha = np.asarray(st.split()[3], dtype=np.float32)
    nz = (rng.random(alpha.shape, dtype=np.float32) > 0.07).astype(np.float32)
    nz = np.asarray(Image.fromarray((nz * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)), dtype=np.float32) / 255.0
    st.putalpha(Image.fromarray((alpha * np.clip(nz * 1.25, 0, 1)).astype(np.uint8)))
    st = st.rotate(6, resample=Image.BICUBIC, expand=True)
    scale = 0.6
    st = st.resize((int(st.width * scale), int(st.height * scale)), Image.LANCZOS)
    pos = (int(330 * K), int(760 * K))
    for i, al in ((2, 0.10), (1, 0.22)):
        g = st.copy()
        g.putalpha(g.split()[3].point(lambda v, al=al: int(v * al)))
        ui.img.alpha_composite(g, (pos[0] - i * 26 * K, pos[1] - i * 16 * K))
    ui.img.alpha_composite(st, pos)
    # speed streaks behind the stamp
    for i in range(7):
        yy = 800 + i * 24
        ui.line([(720 + i * 10, yy), (1010, yy)], a(RED, 70 + i * 8), 3)


FRAMES = {"plan": frame_plan, "reveal": frame_reveal, "impact": frame_impact}


def run(dirn, names):
    for nm in names:
        raw = Image.open(os.path.join(dirn, nm + "_raw.png"))
        nodes = json.load(open(os.path.join(dirn, nm + "_nodes.json")))
        rw = nodes.pop("_res")[0]
        sc = W / float(rw)
        N = {k: (v[0] * sc, v[1] * sc) for k, v in nodes.items()}
        base = grade(raw)
        ui = Ui()
        FRAMES[nm](N, ui)
        out = finalize(base, ui)
        path = os.path.join(dirn, nm + ".png")
        out.save(path, optimize=True)
        print(path, os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--frames", default="plan,reveal,impact")
    ar = ap.parse_args()
    run(ar.dir, ar.frames.split(","))
