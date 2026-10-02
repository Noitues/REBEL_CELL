"""Round 19 / 3: combat effects, batch 1 (see ../effects_list.md).

fx_block_shield, fx_heal, fx_corrupt_tick, fx_drone, fx_evade, fx_enemy_defeated (+ fx_batch1_storyboard.png).
Same language as round 18: 0/1 glyphs in the source slice's colour, vinyl stickers for words/objects, additive
glow with light spill, damage numbers in Anton; no spray.

python effects_batch1.py [name ...]     # default: all six, then the storyboard
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

import plates as P
import make_combat as MC
import fxlib as FX
import damage_shards as DS
from fxlib import seg, lerp, lerp2, bez, ease_out_cubic, ease_in_cubic, ease_in_out, ease_out_back
from slicelib import f_num, f_ui, f_mono, PROGRAMS
from card_play import card_face

OUT = P.OUT
PC, BC = P.PLAYER["c"], P.BOSS["c"]
PR, BR = P.PLAYER["r"], P.BOSS["r"]
CYAN = PROGRAMS["FIREWALL"]["col"]
GREEN = PROGRAMS["PROXY"]["col"]
HEALG = PROGRAMS["PATCH"]["col"]
VIOLET = PROGRAMS["VIRUS"]["col"]
CORRUPT = (255, 70, 120)
ORANGE = (255, 120, 48)
PINK = PROGRAMS["EXPLOIT"]["col"]
SHIELD_COL = (205, 240, 255)
G17 = os.path.normpath(os.path.join(OUT, "..", "round17_slice_system", "glyphs"))  # read-only
MP = P.wheel("player")[2]
MB = P.wheel("boss")[2]


# ------------------------------------------------------------------ helpers
def pt(c, r, a):
    """Clock angle (deg from top, clockwise) -> screen."""
    return (c[0] + r * math.sin(math.radians(a)), c[1] - r * math.cos(math.radians(a)))


def wedge(c, r0, r1, a0, a1, n=24):
    o = [pt(c, r1, a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    return o + [pt(c, r0, a1 - (a1 - a0) * i / n) for i in range(n + 1)]


_I = {}


def icon(name, px, col=(255, 255, 255), outline=True):
    key = (name, px, col, outline)
    if key in _I:
        return _I[key]
    a = Image.open(os.path.join(G17, name + ".png")).convert("RGBA").split()[3].resize((px, px), Image.LANCZOS)
    pad = max(2, px // 10)
    out = Image.new("RGBA", (px + 2 * pad, px + 2 * pad), (0, 0, 0, 0))
    if outline:
        rim = Image.new("L", out.size, 0)
        rim.paste(a, (pad, pad))
        rim = rim.filter(ImageFilter.MaxFilter(2 * (pad // 2) + 1))
        dk = Image.new("RGBA", out.size, (12, 10, 22, 255))
        dk.putalpha(rim)
        out.alpha_composite(dk)
    body = Image.new("RGBA", (px, px), col + (255,))
    body.putalpha(a)
    out.alpha_composite(body, (pad, pad))
    _I[key] = out
    return out


def hand(img):
    for i in range(5):
        x, y, r = P.hand_slot(i, 5)
        FX.place(img, card_face(i, 144, 192), x, y + 96, 1, 1, r, shadow=((3, 5), 3, 0.55))


def screen(p_state=(41, 0), b_state=(340, 0), hp_p=41, hp_e=340, ram=5, p_off=(0, 0), b_off=(0, 0), no_boss=False):
    if no_boss:
        img = boss_less(p_state)
    else:
        img = P.hp_scene(p_state, b_state, p_off, b_off)
    P.hud(img, hp_p=hp_p, hp_e=hp_e, ram=ram, next_p=False, next_e=False)
    P.stickers(img)
    hand(img)
    return img


_BL = {}


def boss_less(p_state):
    if p_state not in _BL:
        img = P.city().copy()
        pw, pc, _ = P.wheel("player") if p_state == (41, 14) else P.wheel_hp("player", *p_state)
        img.alpha_composite(pw, P.wheel_pos("player", pc))
        from slicelib import bloom
        _BL[p_state] = bloom(img.convert("RGB"), 1, 0.32, 0.66).convert("RGBA")
    return _BL[p_state].copy()


def vinyl_word(text, col, ink=MC.INK, size=64, tilt=0.0, pad=(22, 6)):
    f = P.anton(size)
    tw = int(f.getlength(text))
    body = Image.new("RGBA", (tw + 2 * pad[0], size + 2 * pad[1] + 18), (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    d.rounded_rectangle([0, 0, body.width - 1, body.height - 1], radius=12, fill=col + (255,))
    d.text((pad[0], pad[1]), text, font=f, fill=ink + (255,))
    return MC.vinyl(body, border=7, tilt=tilt, shadow=0.55)


def slap(img, sprite, c, age, dur=200):
    """Vinyl slap: drop from x1.35, squash 1.12/0.88 at contact, settle."""
    if age < 0:
        return
    q = seg(age, 0, dur)
    if q < 0.4:
        k = lerp(1.35, 1.0, ease_in_cubic(q / 0.4))
        sx = sy = k
    elif q < 0.7:
        w = ease_out_cubic((q - 0.4) / 0.3)
        sx, sy = lerp(1.0, 1.12, w), lerp(1.0, 0.88, w)
    else:
        w = ease_in_out((q - 0.7) / 0.3)
        sx, sy = lerp(1.12, 1.0, w), lerp(0.88, 1.0, w)
    FX.place(img, sprite, c[0], c[1], sx, sy, 0)


def chip(img, x, y, text, col, glyph=None, age=0, size=26):
    if age < 0:
        return
    s = lerp(1.4, 1.0, ease_out_back(seg(age, 0, 140), 2.0))
    f = f_num(int(size * s))
    tw = f.getlength(text)
    gw = int(size * 1.1 * s) if glyph else 0
    w, h = int(tw + gw + 28), int(size * 1.45 * s)
    im = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w, h], radius=7, fill=(10, 9, 15, 240), outline=col + (255,), width=3)
    if glyph:
        g = icon(glyph, max(8, gw - 6), col)
        im.alpha_composite(g, (8, (h - g.height) // 2 + 1))
    d.text((12 + gw, (h - size * s * 1.2) / 2), text, font=f, fill=col + (255,))
    img.alpha_composite(im, (int(x), int(y - h / 2)))


def emit(img, fx, k=0.5):
    if fx.getbbox():
        img = FX.glow_add(img, fx, 5, 20, k)
        img.alpha_composite(fx)
    return img


class Stream:
    """0/1 glyphs flying from sources to targets along Beziers (ease-in), white-hot at birth."""

    def __init__(self, pairs, t0, spread_ms, travel, col, seed, px=(16, 22), bow=0.35, chars="01"):
        rng = np.random.default_rng(seed)
        self.p = []
        for i, (s, e) in enumerate(pairs):
            mx, my = (s[0] + e[0]) / 2, (s[1] + e[1]) / 2
            nx, ny = -(e[1] - s[1]), e[0] - s[0]
            k = bow * (0.6 + 0.8 * rng.random()) * (1 if rng.random() < 0.5 else -1) if bow else 0
            c = (mx + nx * k, my + ny * k)
            self.p.append(dict(s=s, c=c, e=e, t=t0 + spread_ms * i / max(1, len(pairs) - 1) + rng.uniform(0, 40),
                               tr=travel * rng.uniform(0.8, 1.2), ch=chars[int(rng.integers(0, len(chars)))], px=rng.uniform(*px)))
        self.col = col

    def arrival(self, i):
        q = self.p[i]
        return q["t"] + q["tr"]

    def draw(self, layer, t):
        for q in self.p:
            a = t - q["t"]
            if a < 0 or a > q["tr"]:
                continue
            u = a / q["tr"]
            p = bez(q["s"], q["c"], q["e"], u ** 1.6)
            FX.paste_c(layer, FX.glyph(q["ch"], lerp(q["px"], q["px"] * 0.6, u), self.col, core=max(0, 1 - a / 90), rim=0.8), p[0], p[1],
                       alpha=1 - seg(u, 0.85, 1))


def arc_seg_poly(kind, i, meta):
    """HP arc segment i (combat_wheel.draw_hp geometry)."""
    a0 = 230 - 100 * (i + 0.88) / 30
    a1 = 230 - 100 * (i + 0.12) / 30
    pts = [P.arc_point(kind, a0 + (a1 - a0) * j / 4, meta, 0) for j in range(5)]
    pts += [P.arc_point(kind, a1 - (a1 - a0) * j / 4, meta, 1) for j in range(5)]
    return pts, P.arc_point(kind, (a0 + a1) / 2, meta)


def gif(name, frames, durs, crop, size):
    out = [f.convert("RGB").crop(crop).resize(size, Image.LANCZOS) for f in frames]
    durs[-1] = 900
    s = FX.save_gif(out, durs, os.path.join(OUT, name), size=size)
    print(name, s // 1024, "KB", flush=True)


# ================================================================== 1 block + shield
WALL_A = (42, 112)  # player wall arc (clock deg), facing the boss
HEX_A = (238, 302)  # boss shield arc, facing the player


def wall_bricks():
    out = []
    n = 9
    r0, r1, r2 = PR * 1.12, PR * 1.20, PR * 1.28
    for course, (ra, rb) in enumerate(((r0, r1), (r1 + 1, r2))):
        for i in range(n - course):
            off = 0.5 * course
            b0 = WALL_A[0] + (WALL_A[1] - WALL_A[0]) * (i + off) / n + 0.7
            b1 = WALL_A[0] + (WALL_A[1] - WALL_A[0]) * (i + off + 1) / n - 0.7
            out.append(dict(poly=wedge(PC, ra, rb, b0, b1, 4), c=pt(PC, (ra + rb) / 2, (b0 + b1) / 2), course=course))
    for i in range(0, n, 2):  # crenellations
        b = WALL_A[0] + (WALL_A[1] - WALL_A[0]) * (i + 0.5) / n
        out.append(dict(poly=wedge(PC, r2 + 1, r2 + 13, b - 2.2, b + 2.2, 2), c=pt(PC, r2 + 7, b), course=2))
    return out


BRICKS = wall_bricks()


def hexes():
    out = []
    for row, rr in enumerate((BR * 1.15, BR * 1.27)):
        n = 7 - row
        for i in range(n):
            a = HEX_A[0] + (HEX_A[1] - HEX_A[0]) * (i + 0.5 + 0.5 * row) / 7
            out.append(dict(c=pt(BC, rr, a), a=a))
    out.sort(key=lambda h: abs(h["a"] - 270))
    return out


HEXES = hexes()


def hex_poly(c, r, rot=0):
    return [(c[0] + r * math.cos(math.radians(60 * k + rot)), c[1] + r * math.sin(math.radians(60 * k + rot))) for k in range(6)]


def block_shield(t):
    img = screen()
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    # player FIREWALL slice (slot 4: clock 210-270) resolves
    if 0 <= t < 120:
        d.polygon(wedge(PC, PR * 0.38, PR * 0.98, 210, 270), fill=CYAN + (int(150 * (1 - t / 120)),))
    S1.draw(fx, t)
    for i, b in enumerate(BRICKS):
        tb = 300 + i * 28
        a = t - tb
        if a < 0:
            continue
        settle = 1 - 0.4 * seg(t, 1100, 1500)
        flash = max(0.0, 1 - a / 90)
        col = tuple(int(lerp(v, 255, flash)) for v in CYAN)
        poly = b["poly"]
        if a < 80:
            k = lerp(1.3, 1.0, ease_out_back(a / 80, 2.0))
            poly = [(b["c"][0] + (x - b["c"][0]) * k, b["c"][1] + (y - b["c"][1]) * k) for x, y in poly]
        d.polygon(poly, fill=col + (int(230 * settle),), outline=(8, 30, 40, int(255 * settle)))
        if b["course"] < 2 and a > 60:
            FX.paste_c(fx, FX.glyph("01"[i % 2], 11, (10, 40, 50), outline=False), b["c"][0], b["c"][1], alpha=0.8 * settle)
    if t > 1500:  # standing indicator: a slow shimmer runs along the wall
        u = ((t - 1500) % 1200) / 1200
        a = WALL_A[0] + (WALL_A[1] - WALL_A[0]) * u
        d.line([pt(PC, PR * 1.11, a), pt(PC, PR * 1.29, a)], fill=(255, 255, 255, 150), width=4)
    # boss shield from its hub
    if 1300 <= t < 1500:
        q = seg(t, 1300, 1500)
        r = BR * lerp(0.37, 0.95, ease_out_cubic(q))
        d.ellipse([BC[0] - r, BC[1] - r, BC[0] + r, BC[1] + r], outline=SHIELD_COL + (int(200 * (1 - q)),), width=5)
    for i, h in enumerate(HEXES):
        th = 1420 + i * 45
        a = t - th
        if a < 0:
            continue
        k = ease_out_back(seg(a, 0, 120), 2.2)
        wave = max(0.0, 1 - abs(t - (1950 + i * 25)) / 90)
        settle = 1 - 0.45 * seg(t, 2100, 2400)
        col = tuple(int(lerp(v, 255, max(wave, max(0, 1 - a / 100)))) for v in SHIELD_COL)
        poly = hex_poly(h["c"], 17 * k, 0)
        d.polygon(poly, fill=col + (int(110 * settle + 60 * wave),), outline=col + (int(255 * settle),))
        d.polygon(hex_poly(h["c"], 9 * k, 0), outline=col + (int(160 * settle),))
    img = emit(img, fx, 0.45)
    pb, eb, _, _ = P.hp_boxes()
    chip(img, pb[0], pb[1] - 30, "BLOCK 5", CYAN, "slice_firewall", t - 760)
    chip(img, eb[0], eb[1] - 30, "SHIELD 4", SHIELD_COL, "placeholder_shield", t - 1900)
    return img


S1 = Stream([(pt(PC, PR * 0.68 + np.random.default_rng(i).uniform(-30, 30), 240 + np.random.default_rng(i + 50).uniform(-20, 20)), b["c"])
             for i, b in enumerate(BRICKS[:16])], 80, 300, 300, CYAN, 3, bow=0.25)


# ================================================================== 2 heal
HEAL_SEGS = list(range(14, 18))  # 27 -> 35: on_n 14 -> 18


def heal(t):
    done = t >= 1250
    img = screen(p_state=(35, 0) if done else (27, 0), hp_p=35 if t >= 1150 else 27)
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    # a soft green pulse wells up under the arc first
    if 0 <= t < 1200:
        q = min(1.0, t / 300) * (1 - seg(t, 900, 1200))
        for i in HEAL_SEGS:
            poly, c = arc_seg_poly("player", i, MP)
            d.ellipse([c[0] - 46, c[1] - 46, c[0] + 46, c[1] + 46], fill=HEALG + (int(110 * q),))
            d.polygon(poly, outline=HEALG + (int(255 * q),))
    HS.draw(fx, t)
    if not done:
        for k, i in enumerate(HEAL_SEGS):
            ta = max(HS.arrival(j) for j in range(k * 6, k * 6 + 6))
            if t >= ta:
                poly, c = arc_seg_poly("player", i, MP)
                fl = max(0.0, 1 - (t - ta) / 220)
                col = tuple(int(lerp(v, 255, fl)) for v in MC.HPG)
                d.polygon(poly, fill=col + (255,))
    img = emit(img, fx, 0.6)
    pb, eb, _, _ = P.hp_boxes()
    c0 = arc_seg_poly("player", 16, MP)[1]
    DS.number_pop(img, "+8", HEALG, (c0[0] + 200, c0[1] + 10), ((pb[0] + pb[2]) / 2, (pb[1] + pb[3]) / 2), t - 820, 420, size=64)
    return img


def heal_stream():
    pairs = []
    rng = np.random.default_rng(9)
    for k, i in enumerate(HEAL_SEGS):
        c = arc_seg_poly("player", i, MP)[1]
        for j in range(6):
            a = 230 - 100 * (i + 0.5) / 30 + rng.uniform(-40, 40)
            s = pt(PC, PR * rng.uniform(1.5, 1.9), a)
            pairs.append((s, c))
    return Stream(pairs, 120, 520, 420, HEALG, 4, px=(30, 40), bow=0.2, chars="+1+0")


HS = heal_stream()


# ================================================================== 3 CORRUPTED tick
C_SLOT = (30, 90)  # player EXPLOIT 6 (slot 1)
RAM_PIP = (150 + 4 * 22 + 8, 958 + 47)  # the 5th RAM pip (make_combat.ram_meter geometry)


def corrupt_overlay(img, t, spasm=0.0):
    """Round 17 CORRUPTED state, simplified: violet tear bands inside the slice + the diamond badge."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(int(t // 120) if spasm <= 0 else int(t // 40) + 999)
    for k in range(9 + int(8 * spasm)):
        a = rng.uniform(C_SLOT[0] + 4, C_SLOT[1] - 4)
        r = rng.uniform(PR * 0.42, PR * 0.95)
        x, y = pt(PC, r, a)
        w = rng.uniform(20, 70) * (1 + spasm)
        xl = x - w / 2 + rng.normal(0, 6 * (1 + 3 * spasm))
        d.rectangle([min(xl, x + w / 2 - 2), y - 2, x + w / 2, y + 3], fill=CORRUPT + (int(150 + 80 * spasm),))
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).polygon(wedge(PC, PR * 0.38, PR * 0.98, *C_SLOT), fill=255)
    lay.putalpha(ImageChops.multiply(lay.split()[3], m))
    img.alpha_composite(lay)
    c = pt(PC, PR * 0.93, C_SLOT[1] - 8)
    dd = ImageDraw.Draw(img)
    s = 20
    dd.polygon([(c[0], c[1] - s), (c[0] + s, c[1]), (c[0], c[1] + s), (c[0] - s, c[1])], fill=(20, 8, 16, 255), outline=CORRUPT + (255,), width=3)
    g = icon("status_corrupted", 20, CORRUPT, outline=False)
    img.alpha_composite(g, (int(c[0] - g.width / 2), int(c[1] - g.height / 2)))


def corrupt_tick(t):
    hit = t >= 1000
    img = screen(p_state=(38, 0) if hit else (41, 0), hp_p=38 if t >= 1150 else 41, ram=4 if t >= 900 else 5)
    sp = 1.0 if 300 <= t < 520 else 0.0
    corrupt_overlay(img, t, sp)
    if 300 <= t < 460:
        DS.pixel_tear(img, (int(PC[0] + 20), int(PC[1] - PR * 0.95), int(PC[0] + PR * 0.98), int(PC[1] - 10)), int(t), 1.6)
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    if 300 <= t < 380:
        d.polygon(wedge(PC, PR * 0.38, PR * 0.98, *C_SLOT), fill=(255, 255, 255, int(160 * (1 - (t - 300) / 80))))
    CS1.draw(fx, t)
    # the drained HP segment flashes then goes dark
    if 960 <= t < 1100:
        poly, c = arc_seg_poly("player", 19, MP)
        d.polygon(poly, fill=(255, 255, 255, int(230 * (1 - (t - 960) / 140))))
    # -1 RAM: a violet bolt to the RAM meter, the pip cracks
    DS.tracer(fx, pt(PC, PR * 0.7, 60), (PC[0] + 380, 760), RAM_PIP, seg(t, 600, 880), CORRUPT, width=5)
    RB.draw(fx, t - 880)
    img = emit(img, fx, 0.5)
    pb, eb, _, _ = P.hp_boxes()
    DS.number_pop(img, "-3", CORRUPT, (pt(PC, PR * 1.3, 100)[0] + 20, pt(PC, PR * 1.3, 100)[1]), ((pb[0] + pb[2]) / 2, (pb[1] + pb[3]) / 2), t - 380, 560, size=60, sub="CORRUPTED")
    chip(img, RAM_PIP[0] + 40, RAM_PIP[1] - 70, "-1 RAM", CORRUPT, None, t - 900, size=24)
    return img


def corrupt_stream():
    pairs = []
    rng = np.random.default_rng(12)
    end = arc_seg_poly("player", 19, MP)[1]
    for j in range(16):
        s = pt(PC, PR * rng.uniform(0.5, 0.9), rng.uniform(*C_SLOT))
        pairs.append((s, (end[0] + rng.normal(0, 8), end[1] + rng.normal(0, 6))))
    st = Stream(pairs, 380, 300, 520, VIOLET, 13, px=(24, 30), bow=0.0)
    for q in st.p:  # bow outward around the rim (drips run down the outside, never across the face)
        mid = pt(PC, PR * 1.45, 120)
        q["c"] = (mid[0] + rng.normal(0, 30), mid[1] + rng.normal(0, 30))
    return st


CS1 = corrupt_stream()
RB = DS.Burst(RAM_PIP, -90, 160, 10, (12, 16), (200, 420), CORRUPT, 31, gravity=600, life=(300, 450))


# ================================================================== 4 drone deploy + attack
DOCK_A = 300.0
DOCK = pt(BC, BR * 1.17, DOCK_A)
P_PTR = (PC[0], PC[1] - PR * 0.74)


def drone_sticker():
    s = 40
    body = Image.new("RGBA", (2 * s + 4, 2 * s + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    d.polygon(hex_poly((s + 2, s + 2), s, 30), fill=(30, 14, 8, 255), outline=ORANGE + (255,))
    d.polygon(hex_poly((s + 2, s + 2), s - 5, 30), outline=ORANGE + (255,))
    g = icon("special_drone", 40, ORANGE)
    body.alpha_composite(g, ((body.width - g.width) // 2, (body.height - g.height) // 2 - 2))
    d.rounded_rectangle([s - 12, 2 * s - 12, s + 16, 2 * s + 4], radius=4, fill=(10, 9, 15, 255), outline=ORANGE + (255,), width=2)
    d.text((s - 5, 2 * s - 14), "5", font=f_num(16), fill=(255, 255, 255, 255))
    return MC.vinyl(body, border=5, shadow=0.55)


DRONE = None


def drone(t):
    global DRONE
    if DRONE is None:
        DRONE = drone_sticker()
    hit = t >= 2050
    img = screen(p_state=(38, 0) if hit else (41, 0), hp_p=38 if t >= 2350 else 41)
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    if 0 <= t < 200:  # hub pulse
        q = t / 200
        r = BR * lerp(0.2, 0.42, q)
        d.ellipse([BC[0] - r, BC[1] - r, BC[0] + r, BC[1] + r], outline=ORANGE + (int(220 * (1 - q)),), width=6)
    DST.draw(fx, t)
    if 560 <= t < 700:  # the bits pack into a hex
        q = seg(t, 560, 700)
        d.polygon(hex_poly(DOCK, 44 * (1.4 - 0.4 * q), 30), outline=ORANGE + (int(255 * (1 - q)),), width=4)
    # drone docks: slap + clamp
    recoil = 0
    if 1780 <= t < 1980:
        recoil = 8 * math.sin(math.pi * seg(t, 1780, 1980))
    if t >= 640:
        if t >= 700:
            cl = pt(BC, BR * 1.0, DOCK_A)
            d.line([cl, pt(BC, BR * 1.10, DOCK_A)], fill=ORANGE + (255,), width=5)
        dx = recoil * math.sin(math.radians(DOCK_A))
        dy = -recoil * math.cos(math.radians(DOCK_A))
    # attack: the eye charges, then a mini tracer to your pointer slice
    if 1500 <= t < 1800:
        q = seg(t, 1500, 1800)
        r = 18 + 30 * q
        d.ellipse([DOCK[0] - r, DOCK[1] - r, DOCK[0] + r, DOCK[1] + r], outline=(255, 220, 160, int(255 * q)), width=3)
    DS.tracer(fx, DOCK, (1000, 200), P_PTR, seg(t, 1800, 2050), ORANGE, width=5)
    if 2050 <= t < 2110:
        DS.flash_disc(fx, P_PTR, 26, 0.6)
    DB.draw(fx, t - 2050)
    img = emit(img, fx, 0.5)
    if t >= 640:
        slap(img, DRONE, (DOCK[0] + dx, DOCK[1] + dy), t - 640, 180)
        if 760 <= t < 1500:
            chip(img, DOCK[0] - 60, DOCK[1] - 90, "DRONE  HP 5", ORANGE, None, t - 760, size=20)
    pb, eb, _, _ = P.hp_boxes()
    DS.number_pop(img, "-3", ORANGE, (P_PTR[0] + 90, P_PTR[1] - 30), ((pb[0] + pb[2]) / 2, (pb[1] + pb[3]) / 2), t - 2050, 360, size=56, sub="DRONE")
    return img


def drone_stream():
    rng = np.random.default_rng(21)
    pairs = []
    for j in range(26):
        s = (BC[0] + rng.normal(0, 30), BC[1] + rng.normal(0, 30))
        a = rng.uniform(0, 2 * math.pi)
        e = (DOCK[0] + 30 * math.cos(a) * rng.random(), DOCK[1] + 30 * math.sin(a) * rng.random())
        pairs.append((s, e))
    return Stream(pairs, 120, 260, 300, ORANGE, 22, px=(16, 22), bow=0.3)


DST = drone_stream()
DB = DS.Burst(P_PTR, -110, 80, 9, (13, 18), (420, 720), ORANGE, 23)


# ================================================================== 5 evade
TOKEN_A = 62.0
TOKEN = pt(PC, PR * 1.2, TOKEN_A)
B_BLADE = (BC[0], BC[1] - BR * 1.12)


def token_sticker():
    body = Image.new("RGBA", (74, 74), (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    d.ellipse([0, 0, 73, 73], fill=(14, 40, 18, 255), outline=GREEN + (255,), width=4)
    g = icon("slice_proxy", 40, GREEN)
    body.alpha_composite(g, ((74 - g.width) // 2, (74 - g.height) // 2))
    return MC.vinyl(body, border=5, shadow=0.0)


TOK = None


def dodge_x(t):
    if t < 1060:
        return 0.0
    if t < 1140:
        return -34 * ease_out_cubic(seg(t, 1060, 1140))
    return -34 * (1 - ease_in_out(seg(t, 1400, 1700)))


def evade(t):
    global TOK
    if TOK is None:
        TOK = token_sticker()
    dx = int(round(dodge_x(t)))
    img = screen(p_off=(dx, 0))
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    if 0 <= t < 120:  # PROXY slice (slot 5: clock 270-330) resolves
        d.polygon(wedge(PC, PR * 0.38, PR * 0.98, 270, 330), fill=GREEN + (int(150 * (1 - t / 120)),))
    ES.draw(fx, t)
    # after-images at the old position while it dodges
    if 1060 <= t < 1360:
        pw, pc, _ = P.wheel("player")
        pos = P.wheel_pos("player", pc)
        al = 1 - seg(t, 1060, 1360)
        for col, off, a in (((60, 255, 255), 14, 0.16), ((255, 60, 200), -10, 0.12)):
            g = Image.new("RGBA", pw.size, col + (0,))
            g.putalpha(pw.split()[3].point(lambda v: int(v * a * al)))
            fx.alpha_composite(g, (pos[0] + off, pos[1]))
    # the hit flies at where the pointer was, passes through, fizzles
    far = (PC[0] - 230, PC[1] - PR * 0.95)
    DS.tracer(fx, B_BLADE, (980, 60), P_PTR, seg(t, 860, 1080), ORANGE, width=6)
    if 1080 <= t < 1300:
        DS.tracer(fx, P_PTR, ((P_PTR[0] + far[0]) / 2, (P_PTR[1] + far[1]) / 2 - 20), far, seg(t, 1080, 1220), (150, 140, 130), width=4)
    FZ.draw(fx, t - 1220)
    img = emit(img, fx, 0.45)
    # token sticker: slaps on at 520, peels off and flies away when the hit is cancelled
    tk = (TOKEN[0] + dx, TOKEN[1])
    if 520 <= t < 1100:
        slap(img, TOK, tk, t - 520, 180)
        if t >= 700:
            chip(img, tk[0] + 44, tk[1] - 4, "EVADE 1", GREEN, None, t - 700, size=20)
    elif 1100 <= t < 1500:
        q = seg(t, 1100, 1500)
        f, pad = FX.peel(TOK, min(0.45, q * 1.2), "bl")
        f.putalpha(f.split()[3].point(lambda v: int(v * (1 - seg(q, 0.5, 1)))))
        FX.place(img, f, tk[0] + 120 * q, tk[1] - 160 * q * q, 1, 1, 30 * q, shadow=((12, 18), 10, 0.3))
    if t >= 1160:
        w = WORD_E
        slap(img, w, (PC[0] - PR * 1.0, PC[1] - PR * 1.12), t - 1160, 200)
    return img


ES = Stream([(pt(PC, PR * np.random.default_rng(i).uniform(0.5, 0.9), np.random.default_rng(i + 7).uniform(275, 325)),
              (TOKEN[0] + np.random.default_rng(i + 3).normal(0, 8), TOKEN[1] + np.random.default_rng(i + 4).normal(0, 8))) for i in range(12)],
            100, 220, 320, GREEN, 41, bow=0.35, chars=">01")
FZ = DS.Burst((PC[0] - 230, PC[1] - PR * 0.95), 200, 70, 10, (12, 16), (140, 300), (150, 140, 130), 42, gravity=300, life=(260, 420), dim=0.7)
WORD_E = None


# ================================================================== 6 enemy defeated
def pieces():
    """Cut the boss render into its parts: 6 slices, the hub, 8 outer-ring chunks, banner + blade."""
    bw, bc, meta = P.wheel_hp("boss", 0, 0)
    a = np.asarray(bw)
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rho = np.hypot(xx - bc[0], yy - bc[1])
    ang = (np.degrees(np.arctan2(xx - bc[0], -(yy - bc[1]))) + 360) % 360  # clock deg
    pos = P.wheel_pos("boss", bc)
    out = []
    rh = BR * 0.37

    def add(mask, kind, col_hint=None):
        if mask.sum() < 50:
            return
        ys, xs = np.nonzero(mask)
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        sub = a[y0:y1, x0:x1].copy()
        sub[..., 3] = (sub[..., 3] * mask[y0:y1, x0:x1]).astype(np.uint8)
        im = Image.fromarray(sub, "RGBA")
        c = (pos[0] + (x0 + x1) / 2, pos[1] + (y0 + y1) / 2)
        rgb = sub[..., :3][sub[..., 3] > 100]
        col = tuple(int(v) for v in (rgb.mean(axis=0) if len(rgb) else (200, 120, 60)))
        col = tuple(min(255, int(v * 1.5)) for v in col)
        out.append(dict(im=im, c=c, kind=kind, col=col))

    top = yy < bc[1] - BR * 1.32
    for i in range(6):
        a0 = (i * 60 - 30) % 360
        m = (rho >= rh) & (rho < BR * 1.0) & (((ang - a0) % 360) < 60) & ~top
        add(m.astype(np.float32), "slice")
    add(((rho < rh)).astype(np.float32), "hub")
    for i in range(8):
        a0 = i * 45 + 10
        m = (rho >= BR * 1.0) & (((ang - a0) % 360) < 45) & ~top
        add(m.astype(np.float32), "ring")
    add(top.astype(np.float32), "banner")
    return out


T_HIT = 240
T_BREAK = 760
T_HUB = 1000
T_WORD = 1700
PCS = None
WORD_D = None


def defeated(t_real):
    global PCS, WORD_D
    if PCS is None:
        PCS = pieces()
        rng = np.random.default_rng(77)
        for p in PCS:
            vx, vy = p["c"][0] - BC[0], p["c"][1] - BC[1]
            L = max(1.0, math.hypot(vx, vy))
            sp = rng.uniform(140, 300) * (0.4 if p["kind"] == "hub" else 1.0)
            p["v"] = (vx / L * sp, vy / L * sp - rng.uniform(80, 220))
            p["w"] = rng.uniform(-120, 120)
            p["delay"] = rng.uniform(0, 160) + (240 if p["kind"] == "hub" else 0) + (60 if p["kind"] == "banner" else 0)
            p["burst"] = DS.Burst(p["c"], math.degrees(math.atan2(p["v"][1], p["v"][0])), 120, 9 if p["kind"] != "hub" else 26,
                                  (14, 22) if p["kind"] != "hub" else (20, 30), (160, 420), p["col"], int(rng.integers(0, 1e6)), gravity=500,
                                  life=(420, 700))
        WORD_D = vinyl_word("DELETED", ORANGE, size=72, tilt=-6)
    # hit-stop on the killing blow
    t = t_real if t_real < T_HIT else (T_HIT if t_real < T_HIT + 120 else t_real - 120)
    broken = t >= T_BREAK
    hp_e = 24 if t_real < T_HIT + 520 else 0
    if broken:
        img = screen(p_state=(41, 0), no_boss=True, hp_e=0)
    else:
        sh = DS.shake(t, T_HIT + 120, 4, 160, seed=5) if t >= T_HIT else (0, 0)
        img = screen(p_state=(41, 0), b_state=(24, 0), b_off=sh, hp_e=hp_e)
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    imp = (BC[0], BC[1] - BR * 0.74)
    if t < T_HIT:
        DS.tracer(fx, (PC[0], PC[1] - PR * 1.12), (960, 60), imp, seg(t, T_HIT - 220, T_HIT), (255, 200, 235), width=9)
    if T_HIT <= t < T_BREAK:
        if t < T_HIT + 100:
            DS.flash_disc(fx, imp, 60, 0.7)
        # cracks grow from the impact and run along every slice seam
        g = seg(t, T_HIT, T_BREAK - 60)
        rng = np.random.default_rng(5)
        for k in range(6):
            a = k * 60 - 30
            L = BR * (0.37 + 0.63 * min(1, g * 1.4 - k * 0.05))
            if L > BR * 0.37:
                pts = [pt(BC, BR * 0.37, a)]
                for j in range(1, 6):
                    r = BR * 0.37 + (L - BR * 0.37) * j / 5
                    pts.append(pt(BC, r, a + rng.normal(0, 1.5)))
                d.line(pts, fill=(255, 255, 255, 230), width=3)
        DS.cracks(fx, imp, t - T_HIT, 9, n=10, dur=T_BREAK - T_HIT)
        if t >= T_BREAK - 100:  # last beat before the break: everything flashes
            d.ellipse([BC[0] - BR, BC[1] - BR, BC[0] + BR, BC[1] + BR], fill=(255, 255, 255, int(120 * seg(t, T_BREAK - 100, T_BREAK))))
    if broken:
        a_t = t - T_BREAK
        for p in PCS:
            age = a_t - p["delay"]
            if age < 0:
                FX.paste_c(img, p["im"], p["c"][0], p["c"][1])
                continue
            s = age / 1000
            x = p["c"][0] + p["v"][0] * s
            y = p["c"][1] + p["v"][1] * s + 0.5 * 900 * s * s
            al = 1 - seg(age, 250, 700)
            if al > 0:
                im = p["im"]
                if age > 150:  # pixel break-up as it falls
                    k = max(2, int(lerp(1, 10, seg(age, 150, 650))))
                    im = im.resize((max(1, im.width // k), max(1, im.height // k)), Image.NEAREST).resize(im.size, Image.NEAREST)
                FX.paste_c(img, im, x, y, alpha=al, angle=p["w"] * s)
            p["burst"].draw(fx, age)
        if T_HUB <= t < T_HUB + 160:
            q = seg(t, T_HUB, T_HUB + 160)
            r = BR * lerp(0.3, 1.1, ease_out_cubic(q))
            d.ellipse([BC[0] - r, BC[1] - r, BC[0] + r, BC[1] + r], outline=(255, 230, 200, int(220 * (1 - q))), width=6)
    img = emit(img, fx, 0.5)
    eb = P.hp_boxes()[1]
    if broken:  # boss HP readout: 0, greyed
        dd = ImageDraw.Draw(img)
        dd.rectangle([eb[0] - 6, eb[1] - 4, eb[2] + 8, eb[3] + 6], fill=(14, 13, 20, 255))
        dd.text((eb[0], eb[1]), "0/400", font=f_num(62), fill=(120, 120, 130, 255), stroke_width=3, stroke_fill=(6, 6, 8, 255))
    DS.number_pop(img, "-24", PINK, (imp[0] + 150, imp[1] - 60), ((eb[0] + eb[2]) / 2, (eb[1] + eb[3]) / 2), t_real - T_HIT - 120, 380, size=90, crit=True, sub="LETHAL")
    if t >= T_WORD:
        slap(img, WORD_D, (BC[0], BC[1] - 20), t - T_WORD, 220)
    return img


# ================================================================== run
EFFECTS = {
    "block_shield": (block_shield, 2700, DS.GIF_CROP, (960, 540), (960, 540),
                     [(200, "BLOCK: STREAM", PC), (520, "BRICKS LAY", PC), (1700, "SHIELD HEXES", BC), (2200, "BOTH STANDING", (960, 520))],
                     [["FIREWALL slice flashes; 16 cyan 0/1", "fly to the rim facing the enemy."],
                      ["Bricks pop 1.3 -> 1 (28 ms apart),", "crenels last; BLOCK 5 chip at HP."],
                      ["Hub pulse; 13 hex plates tile out", "from the middle, a ripple runs across."],
                      ["Wall settles 60 % + shimmer; hexes", "45 %; chips hold until spent/expired."]]),
    "heal": (heal, 1900, (200, 420, 860, 1080), (660, 660), (840, 840),
             [(240, "GREEN WELL", PC), (520, "GLYPHS IN", PC), (900, "SEGMENTS RELIGHT", PC), (1400, "+8 -> HP", PC)],
             [["A soft green well under the arc", "(where the HP will return)."],
              ["24 '+' / 0 / 1 glyphs rise in from", "outside, below the wheel."],
              ["Each segment flashes white -> green", "as its 6 glyphs arrive."],
              ["+8 pops, flies to HP: 27 -> 35;", "the arc is redrawn at 35."]]),
    "corrupt_tick": (corrupt_tick, 1900, (40, 120, 920, 1080), (642, 700), (880, 960),
                     [(100, "CORRUPTED (STANDING)", PC), (340, "SPASM", PC), (720, "DRIP + BOLT", PC), (1200, "-3 HP, -1 RAM", PC)],
                     [["Violet tear bands + diamond badge", "on your EXPLOIT 6."],
                      ["It resolves: white flash, the tears", "spasm, pixel tear 160 ms."],
                      ["Violet bits drip round the rim to the", "HP arc; a bolt hits the RAM meter."],
                      ["-3 to HP (41 -> 38), the 5th RAM pip", "cracks into 0/1: -1 RAM."]]),
    "drone": (drone, 2900, DS.GIF_CROP, (960, 540), (960, 540),
              [(300, "BITS LEAVE THE HUB", BC), (720, "DOCK (SLAP)", BC), (1680, "EYE CHARGES", BC), (2200, "DRONE HIT", (900, 400))],
              [["Hub pulse; 26 orange 0/1 stream", "to the dock point on the rim."],
               ["They pack into a hex, the drone", "sticker slaps on, a clamp locks."],
               ["Its lens ring charges 300 ms", "(the forecast already shows it)."],
               ["Mini tracer -> your pointer slice:", "S-tier shards, -3, recoil 8 px."]]),
    "evade": (evade, 2300, DS.GIF_CROP, (960, 540), (960, 540),
              [(400, "EVADE TOKEN", PC), (1040, "HIT INCOMING", (700, 360)), (1180, "SIDE-STEP", PC), (1500, "EVADED", PC)],
              [["PROXY resolves: green '>>' bits form", "a token sticker on the rim."],
               ["The boss EXPLOIT flies at your", "pointer (forecast said HIT 14)."],
               ["The wheel steps 34 px (80 ms), RGB", "after-images; the hit passes through."],
               ["It fizzles into grey bits; the token", "peels off; EVADED slaps on."]]),
    "enemy_defeated": (defeated, 2700, (1040, 40, 1840, 1000), (600, 720), (800, 960),
                       [(240, "KILLING BLOW", BC), (560, "CRACKS RUN", BC), (1040, "BREAK APART", BC), (2200, "DELETED", BC)],
                       [["Crit -24 = LETHAL; hit-stop 120 ms,", "flash, shake 4 px."],
                        ["Cracks grow from the hit and along", "every slice seam (500 ms)."],
                        ["Slices, hub, ring and banner fly", "apart, pixelate, shed 0/1."],
                        ["DELETED vinyl slaps where the wheel", "was; HP reads 0/400 in grey."]]),
}


def run(name):
    global WORD_E
    if WORD_E is None:
        WORD_E = vinyl_word("EVADED", GREEN, size=54, tilt=5)
    fn, T, crop, size, cell_crop, keys, caps = EFFECTS[name]
    frames, durs, cells = [], [], []
    keyt = {int(round(k[0] / FX.DT) * FX.DT): (k, ki) for ki, k in enumerate(keys)}
    for t in range(0, T, int(FX.DT)):
        img = fn(t)
        frames.append(img.convert("RGB"))
        durs.append(int(FX.DT))
        if t in keyt:
            k, ki = keyt[t]
            c = k[2]
            w, h = 760, 640
            x0 = int(min(max(0, c[0] - w / 2), 1920 - w))
            y0 = int(min(max(0, c[1] - h / 2), 1080 - h))
            cells.append((img.convert("RGB").crop((x0, y0, x0 + w, y0 + h)).resize((475, 400), Image.LANCZOS), k[1], t, ki))
    gif("fx_%s.gif" % name, frames, durs, crop, size)
    return [(im, "%s  %s" % (name.upper().replace("_", " "), lab), "%d ms" % t, caps[ki]) for (im, lab, t, ki) in cells]


def main(names):
    allc = []
    for n in names:
        allc += run(n)
        print("done", n, flush=True)
    if len(names) == len(EFFECTS):
        FX.storyboard(allc, os.path.join(OUT, "fx_batch1_storyboard.png"),
                      "COMBAT FX  -  batch 1 (block/shield, heal, CORRUPTED tick, drone, evade, enemy defeated)",
                      "4 key frames per effect (crops of the 1920x1080 D4 screen at 0.625). 0/1 glyphs in the source slice colour; words are vinyl stickers.",
                      cols=4,
                      note_lines=["layer order: wheels | status overlays | FX (additive, spill) | HUD | stickers (tokens, drones, words) | numbers. All T2 except enemy defeated (T3).",
                                  "reduce effects: no streams/bursts/after-images; chips + numbers set at once; walls/hexes/drone/badges appear with a 1-frame outline."])


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "test":
        name = args[1]
        if WORD_E is None:
            WORD_E = vinyl_word("EVADED", GREEN, size=54, tilt=5)
        for a in args[2:]:
            EFFECTS[name][0](int(a)).convert("RGB").save(os.path.join(P.SCR, "fx_%s_%s.png" % (name, a)))
            print("test", name, a, flush=True)
    else:
        main(args or list(EFFECTS))
