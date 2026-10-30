"""Round 35 shared UI: the corp-paper operative DOSSIER, the Site INFO window (holo; TIER / REWARDS / NODE TYPE only),
the two Heat options (A: the Cell's terminal strip; B: diegetic, the city reacts + the corp's watch level on the dossier),
node-state colours (round 35 rules), and the GIF writer.

States: OWNED = lime (the Cell's); AVAILABLE = corp colour, bright; NOT YET = WHITE; PAST / VISITED = GREY.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import r31lib as L
import r32ui as U
import sticker_lib19 as SL

MER = U.MER
LIME = U.LIME
WHITE = (236, 234, 244)
GREY = (118, 114, 128)
GOLD = (255, 206, 72)
TYPEF = L.TYPE
TYPEB = L.TYPE_B

OPERATIVE = dict(name="CELL-9", cls="BREAKER", rank="R1", hp="52 / 60", ram="6, +4 a turn, max 12",
                 wheel="CRIT  ATK  ATK  ATK  DEF  MISS", core="+1 spin on all cards", deck="14 cards",
                 station="node's assets +50% damage", glyph="slice_exploit")


def dossier(w=400, h=520, op=OPERATIVE, heat_stamp=None, seed=7):
    """The corp's file on the operative: intercepted paper (Courier), corp letterhead, photo, stamps."""
    im = L.paper(w, h, seed=seed, tint=(236, 230, 214))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, 54], fill=(28, 22, 18, 255))
    d.text((16, 27), "MERIDIAN", font=L.font(L.ANTON, 26), fill=MER + (255,), anchor="lm")
    d.text((140, 20), "FREIGHT SECURITY", font=L.font(TYPEB, 14), fill=(230, 220, 200, 255), anchor="lm")
    d.text((140, 38), "PERSON OF INTEREST // FILE", font=L.font(TYPEF, 13), fill=(200, 190, 170, 255), anchor="lm")
    # photo: the class emblem as a grainy print, clipped corner
    px, py, pw, ph = 18, 72, 118, 138
    d.rectangle([px, py, px + pw, py + ph], fill=(40, 36, 44, 255), outline=(20, 18, 22, 255), width=2)
    g = L.glyph(op["glyph"], 86, fill=(230, 200, 210), ow=0)
    im.alpha_composite(g, (px + (pw - g.width) // 2, py + 12))
    d.text((px + pw / 2, py + ph - 14), op["name"], font=L.font(TYPEB, 16), fill=(230, 226, 220, 255), anchor="mm")
    tape = L.tape(70, 22, angle=-18, seed=seed)
    im.alpha_composite(tape, (px - 14, py - 14))
    f, fb = L.font(TYPEF, 15), L.font(TYPEB, 15)
    rows = [("SUBJECT", op["name"]), ("CLASS", op["cls"]), ("RANK", op["rank"]), ("HP", op["hp"]), ("RAM", "6 (+4)")]
    y = 76
    for a, b in rows:
        d.text((150, y), a, font=f, fill=(90, 80, 70, 255))
        d.text((236, y), b, font=fb, fill=(30, 26, 30, 255))
        y += 26
    y = 226
    d.line([(16, y - 8), (w - 16, y - 8)], fill=(120, 110, 96, 255), width=1)
    for a, b in (("WHEEL", op["wheel"]), ("HUB CORE", op["core"]), ("DECK", op["deck"])):
        d.text((18, y), a, font=f, fill=(90, 80, 70, 255))
        d.text((18, y + 18), b, font=fb, fill=(30, 26, 30, 255))
        y += 46
    # the raid-placement (station) effect, boxed like a flagged clause
    d.rectangle([14, y + 2, w - 14, y + 66], outline=(150, 40, 40, 255), width=2)
    d.text((24, y + 10), "IF STATIONED ON A NODE (RAIDS):", font=L.font(TYPEB, 14), fill=(150, 40, 40, 255))
    d.text((24, y + 34), op["station"], font=L.font(TYPEB, 17), fill=(30, 26, 30, 255))
    st = L.stamp("AT LARGE", 18, angle=-6, seed=seed + 1)  # round 36: beside the SUBJECT name
    im.alpha_composite(st, (w - st.width - 4, 56))
    if heat_stamp:
        st2 = L.stamp(heat_stamp, 22, angle=6, seed=seed + 2)
        im.alpha_composite(st2, (w - st2.width - 14, h - st2.height - 8))
    return L.rotate_rgba(im, 1.2)


def node_info(canvas, box, title, tier, rewards, ntype, decrypted=True, special=None):
    """The Site info window (holo, decrypted corp intel): TIER, REWARDS, NODE TYPE. Nothing else."""
    canvas = U.holo(canvas, box, MER, title, seed=sum(map(ord, title)) % 50)
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(canvas)
    if not decrypted:
        d.text((x0 + 18, y0 + 70), "ENCRYPTED", font=L.f_ui(26, b"Bold"), fill=(255, 210, 170, 255))
        d.text((x0 + 18, y0 + 104), "tier, rewards and type unknown", font=L.f_mono(15), fill=(220, 190, 170, 255))
        return canvas
    rows = [("TIER", tier), ("TYPE", ntype)] + [("REWARDS" if i == 0 else "", r) for i, r in enumerate(rewards)]
    y = y0 + 64
    for a, b in rows:
        d.text((x0 + 18, y), a, font=L.f_mono(15), fill=(255, 200, 150, 255), anchor="lm")
        d.text((x0 + 116, y), b, font=L.f_ui(18, b"SemiBold"), fill=(255, 236, 214, 255), anchor="lm")
        y += 28
    if special:
        canvas = U.chip(canvas, (x0 + 18, y1 - 26), special, GOLD, 14, anchor="lm", bright=True)
    canvas = U.chip(canvas, (x1 - 98, y1 - 26), "DECRYPTED", LIME, 13)
    return canvas


def heat_strip(canvas, xy, heat=41, band="NOTICED", w=420):
    """Heat option A: the Cell's own terminal, a compact strip."""
    c = L.CRT(w, 64, L.HEAT, None, header=False, seed=91)
    c.text((14, 32), "HEAT", 16, L.HEAT, anchor="lm")
    c.text((66, 33), str(heat), 34, L.HEAT, anchor="lm", fnt=L.f_num(40))
    c.text((116, 20), band, 15, (255, 190, 130), anchor="lm")
    bx, by, bw = 116, 36, w - 132
    c.d.rectangle([bx, by, bx + bw, by + 10], fill=(40, 20, 16, 255))
    c.d.rectangle([bx, by, bx + int(bw * heat / 100), by + 10], fill=L.HEAT + (255,))
    for v in (25, 50, 75):
        x = bx + bw * v / 100
        c.d.line([(x, by - 4), (x, by + 14)], fill=(255, 230, 200, 255), width=2)
    return L.paste(canvas, c.finish(scan=0.15), *xy)


def heat_diegetic(canvas, beams, cops, k=1.0):
    """Heat option B: the city reacts (the locked H1 language): searchlight cones on the streets, police strobes."""
    W, H = canvas.size
    lay = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(lay)
    for (sx, sy, tx, ty, r) in beams:
        ang = math.atan2(ty - sy, tx - sx)
        px, py = -math.sin(ang), math.cos(ang)
        d.polygon([(sx, sy), (tx + px * r, ty + py * r * 0.55), (tx - px * r, ty - py * r * 0.55)], fill=int(70 * k))
        d.ellipse([tx - r, ty - r * 0.55, tx + r, ty + r * 0.55], fill=int(120 * k))
    lay = lay.filter(ImageFilter.GaussianBlur(10))
    canvas = SL.over(canvas, (220, 235, 255), lay)
    for i, (x, y) in enumerate(cops):
        for col, dx in (((255, 40, 50), -10), ((60, 120, 255), 10)):
            g = Image.new("L", (W, H), 0)
            ImageDraw.Draw(g).ellipse([x + dx - 26, y - 14, x + dx + 26, y + 14], fill=int(200 * k))
            canvas = SL.over(canvas, col, g.filter(ImageFilter.GaussianBlur(9)))
    return canvas


def tier_badge(canvas, x, y, tier, col, key=False, size=15):
    """The tier printed on the node itself; tier-3 key nodes get a gold key plate."""
    if key:
        r = 17
        d = ImageDraw.Draw(canvas)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(30, 22, 6, 240), outline=GOLD + (255,), width=3)
        g = L.glyph("placeholder_key", 22, fill=GOLD, ow=0)
        canvas.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))
        return canvas
    return U.chip(canvas, (x, y), "T%d" % tier, col, size, bright=col not in (WHITE, GREY), fill_a=235)
