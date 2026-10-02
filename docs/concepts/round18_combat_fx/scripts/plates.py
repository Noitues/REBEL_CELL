"""Round 18: combat plates for the FX renders.

Rebuilds the locked round 13 D4 combat screen (combat_d4.png) as separate layers so the FX scripts can
animate on it: city base + light spill, the two D4 wheels (the boss can be re-rendered at any rotation),
the HUD (HP numbers drawn per frame), the hand of vinyl sticker cards, and the overlay stickers.

python plates.py warm          # render + cache the wheels (scratch/r), write scratch/plate_check.png
"""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
SCR = os.path.join(OUT, "scratch")
os.makedirs(SCR, exist_ok=True)

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import make_sheets as MS
import make_combat as MC
from slicelib import f_num, f_ui, f_mono, bloom, R_OUT

W, H = 1920, 1080
PINK, ORANGE, YELLOW, RED, HPG, INK = MC.PINK, MC.ORANGE, MC.YELLOW, MC.RED, MC.HPG, MC.INK
GP_YELLOW, GP_RED = MC.GP_YELLOW, MC.GP_RED
PLAYER, BOSS = MC.PLAYER, MC.BOSS
FONT_DIR = os.path.normpath(os.path.join(OUT, "..", "..", "..", "assets", "fonts"))


def mono(px):
    """Share Tech Mono (the game's glyph font, OFL)."""
    from PIL import ImageFont
    return ImageFont.truetype(os.path.join(FONT_DIR, "ShareTechMono-Regular.ttf"), int(px))


def anton(px):
    from PIL import ImageFont
    return ImageFont.truetype(os.path.join(FONT_DIR, "Anton-Regular.ttf"), int(px))


_W = {}


def wheel(kind, rot=0.0, ss=2):
    """D4 wheel sprite at screen scale; returns (RGBA, centre in sprite px, meta)."""
    key = (kind, round(rot, 2), ss)
    if key in _W:
        return _W[key]
    tag = "d4_%s_r%06.2f_s%d" % (kind, rot, ss)
    im, c, meta, s = MS.cached("d4", kind, ss=ss, rot=rot, tag=tag)
    r = PLAYER["r"] if kind == "player" else BOSS["r"]
    k = r / (R_OUT * s)
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    out = (im, (c[0] * k, c[1] * k), meta)
    _W[key] = out
    return out


def wheel_hp(kind, hp, pred, ss=2):
    """D4 wheel at another HP state (the HP arc drains for real): cached in scratch/r."""
    key = (kind, "hp", hp, pred, ss)
    if key in _W:
        return _W[key]
    import frames as F
    import combat_specs as CS
    tag = "d4_%s_hp%d_p%d_s%d" % (kind, hp, pred, ss)
    p = os.path.join(MS.RC, tag + ".png")
    j = os.path.join(MS.RC, tag + ".json")
    os.makedirs(MS.RC, exist_ok=True)
    if os.path.exists(p) and os.path.exists(j):
        m = json.load(open(j))
        im, c, meta = Image.open(p).convert("RGBA"), tuple(m["centre"]), m["meta"]
    else:
        spec = CS.player(hp, pred)[0] if kind == "player" else CS.boss(hp, pred)[0]
        im, c, meta = F.render("d4", spec, ss=ss)
        im.save(p)
        json.dump(dict(centre=c, meta=meta, ss=ss), open(j, "w"))
        print("rendered", tag, flush=True)
    r = PLAYER["r"] if kind == "player" else BOSS["r"]
    k = r / (R_OUT * ss)
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    out = (im, (c[0] * k, c[1] * k), meta)
    _W[key] = out
    return out


def hp_scene(p_state=(41, 14), b_state=(340, 8), p_off=(0, 0), b_off=(0, 0), bloom_on=True):
    """City + both wheels at the given (hp, pred) states, each with an optional shake offset."""
    key = ("hp", p_state, b_state, p_off, b_off)
    if key in _BG:
        return _BG[key].copy()
    img = city().copy()
    pw, pc, _ = wheel("player") if p_state == (41, 14) else wheel_hp("player", *p_state)
    bw, bc, _ = wheel("boss") if b_state == (340, 8) else wheel_hp("boss", *b_state)
    pp = wheel_pos("player", pc)
    bp = wheel_pos("boss", bc)
    img.alpha_composite(pw, (pp[0] + p_off[0], pp[1] + p_off[1]))
    img.alpha_composite(bw, (bp[0] + b_off[0], bp[1] + b_off[1]))
    if bloom_on:
        img = bloom(img.convert("RGB"), 1, 0.32, 0.66).convert("RGBA")
    if len(_BG) < 40:
        _BG[key] = img.copy()
    return img


def hp_point(kind, hp, hpmax, meta, frac_r=0.5):
    """Screen position on the HP arc at the fill end for `hp` (combat_wheel.draw_hp geometry:
    30 segments from 230 deg toward 130 deg, 0 = top, clockwise; ring R+14..R+36 master px)."""
    n = 30
    on_n = round(n * hp / hpmax)
    ang = 230 - 100 * on_n / n
    return arc_point(kind, ang, meta, frac_r), ang


def arc_point(kind, ang, meta, frac_r=0.5):
    c = PLAYER["c"] if kind == "player" else BOSS["c"]
    r = PLAYER["r"] if kind == "player" else BOSS["r"]
    rm = meta["hp_r"] - 29 + 22 * frac_r  # measured on the render: arc mid at hp_r - 18 master px
    k = r / R_OUT
    a = math.radians(ang)
    return (c[0] + rm * k * math.sin(a), c[1] - rm * k * math.cos(a))


def wheel_pos(kind, c):
    cc = PLAYER["c"] if kind == "player" else BOSS["c"]
    return (int(cc[0] - c[0]), int(cc[1] - c[1]))


_BG = {}


def city(boss_im=None):
    """City base with light spill and contact shadows, no wheels (cached)."""
    if "city" in _BG:
        return _BG["city"]
    pw, pc, _ = wheel("player")
    bw, bc, _ = wheel("boss")
    pools = [(PLAYER["c"], PLAYER["r"] * 1.12), (BOSS["c"], BOSS["r"] * 1.12)]
    base = MC.target_base("boss", "night", pools)
    emit = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    emit.alpha_composite(pw, wheel_pos("player", pc))
    emit.alpha_composite(bw, wheel_pos("boss", bc))
    base = MC.light_spill(base, emit, k=1.4, add=0.14)
    img = MC.to_rgba(base)
    sh = Image.new("L", (W, H), 0)
    ds = ImageDraw.Draw(sh)
    for (c, R) in ((PLAYER["c"], PLAYER["r"] * 1.14), (BOSS["c"], BOSS["r"] * 1.14)):
        ds.ellipse([c[0] - R, c[1] - R + 14, c[0] + R, c[1] + R + 14], fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    shl = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    shl.putalpha(sh)
    img.alpha_composite(shl)
    _BG["city"] = img
    return img


def scene(boss_rot=0.0, boss_sprite=None, bloom_on=True):
    """City + both wheels (+ bloom). boss_sprite overrides the boss (e.g. a motion-blurred one)."""
    key = ("scene", round(boss_rot, 2), boss_sprite is None)
    if boss_sprite is None and key in _BG:
        return _BG[key].copy()
    img = city().copy()
    pw, pc, _ = wheel("player")
    img.alpha_composite(pw, wheel_pos("player", pc))
    if boss_sprite is None:
        bw, bc, _ = wheel("boss", boss_rot)
    else:
        bw, bc = boss_sprite
    img.alpha_composite(bw, wheel_pos("boss", bc))
    if bloom_on:
        img = bloom(img.convert("RGB"), 1, 0.32, 0.66).convert("RGBA")
    if boss_sprite is None:
        _BG[key] = img.copy()
    return img


def spin_sprite(rot, blur_deg, ss=1):
    """The real boss render at `rot` (glyph blocks stay upright, as in game) with a trailing rotational
    blur of `blur_deg` on the slice disc only (fast spin)."""
    bw, bc, meta = wheel("boss", rot, ss)
    n = max(1, int(abs(blur_deg) / 1.2))
    if n <= 1:
        return bw, bc
    acc = np.zeros((bw.height, bw.width, 4), np.float32)
    for k in range(n):
        a = -k / (n - 1) * blur_deg  # trail behind the motion (clockwise motion = positive rot)
        acc += np.asarray(bw.rotate(-a, resample=Image.BILINEAR, center=bc), np.float32)
    acc /= n
    yy, xx = np.mgrid[0:bw.height, 0:bw.width]
    rho = np.hypot(xx - bc[0], yy - bc[1])
    r = BOSS["r"]
    hub = r * 0.37
    ring = r * 0.985
    m = np.clip((rho - hub) / 4, 0, 1) * np.clip((ring - rho) / 4, 0, 1)
    m = m[..., None]
    base = np.asarray(bw, np.float32)
    out = base * (1 - m) + acc * m
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA"), bc


# ------------------------------------------------------------------ HUD
def ram_meter(img, x, y, have, maxr, spend, label):
    """make_combat.ram_meter with a free caption (it hard-codes CORRUPT PACKET)."""
    d = ImageDraw.Draw(img)
    MC.plate(d, [x, y, x + 400, y + 92], (92, 225, 255))
    d.text((x + 20, y + 6), "RAM", font=f_ui(16, b"Bold SemiCondensed"), fill=(190, 190, 205, 255))
    d.text((x + 20, y + 26), "%d/%d" % (have, maxr), font=f_num(40), fill=(92, 225, 255, 255))
    cx = x + 120
    for i in range(maxr):
        x0 = cx + i * 22
        box = [x0, y + 32, x0 + 16, y + 62]
        if i < have - spend:
            d.rounded_rectangle(box, radius=3, fill=(92, 225, 255, 255))
        elif i < have:
            d.rounded_rectangle(box, radius=3, fill=(20, 40, 50, 255), outline=(220, 250, 255, 255), width=2)
            d.line([(x0 + 2, y + 58), (x0 + 14, y + 36)], fill=(220, 250, 255, 255), width=2)
        else:
            d.rounded_rectangle(box, radius=3, fill=(26, 34, 42, 255))
    if label:
        d.text((cx, y + 68), label, font=f_mono(13, False), fill=(200, 230, 240, 255))


def hud(img, hp_p=41, hp_e=340, ram=5, ram_spend=0, next_p=True, next_e=True, show_tags=True, ram_label="",
        boss_tag=("EXPLOIT", 14)):
    MC.status_bar(img, "TURN 3   |   FREE NUDGE 1", "NETRUN // MERIDIAN FREIGHT // LANE 15 DEPOT // BOSS: THE MANIFEST")
    meta_p = wheel("player")[2]
    meta_b = wheel("boss")[2]
    pb = MC.hp_number(img, PLAYER["c"], PLAYER["r"] * meta_p["hp_r"] / 436, hp_p, 60)
    if next_p:
        MC.next_plate(img, int(pb[2]) + 16, int(pb[1]) + 12, hp_p - 14, -14, HPG)
    eb = MC.hp_number(img, BOSS["c"], BOSS["r"] * meta_b["hp_r"] / 436, hp_e, 400)
    if next_e:
        MC.next_plate(img, int(eb[2]) + 16, int(eb[1]) + 12, hp_e - 8, -8, ORANGE)
    MC.nudge_buttons(img, PLAYER["c"], PLAYER["r"])
    if show_tags:
        MC.forecast_tag(img, 30, 84, "YOU", "ZERO-DAY", 12, 2,
                        [("HIT 12 - SHIELD 4 = 8", PINK), ("RING x2 ON PERFECT", (200, 200, 215))], PINK, width=400)
        MC.forecast_tag(img, 1590, 84, "THE MANIFEST", boss_tag[0], boss_tag[1], 3,
                        [("HIT 14 > YOU", RED), ("+4 SHIELD", ORANGE)], ORANGE, width=322)
    ram_meter(img, 30, 958, ram, 12, ram_spend, ram_label)
    MC.piles(img, 450, 958)
    bx = MC.small_button(img, 1370, 1010, "RESPIN", "4 RAM  [R]", (92, 225, 255))
    MC.small_button(img, bx, 1006, "UNDO", "[Z]", (190, 190, 205))
    return pb, eb


def hp_boxes():
    """Screen boxes of the two HP numbers (for anchoring pops)."""
    tmp = Image.new("RGBA", (W, H))
    meta_p = wheel("player")[2]
    meta_b = wheel("boss")[2]
    pb = MC.hp_number(tmp, PLAYER["c"], PLAYER["r"] * meta_p["hp_r"] / 436, 41, 60)
    eb = MC.hp_number(tmp, BOSS["c"], BOSS["r"] * meta_b["hp_r"] / 436, 340, 400)
    return pb, eb, meta_p, meta_b


def stickers(img):
    """The two locked overlay stickers: CELL-9 name plate and SEND IT."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    body = Image.new("RGBA", (330, 62), (0, 0, 0, 0))
    db = ImageDraw.Draw(body)
    db.rounded_rectangle([0, 0, 329, 61], radius=12, fill=PINK + (255,))
    db.text((18, 6), "CELL-9 // BREAKER", font=f_num(40), fill=INK + (255,))
    st = MC.vinyl(body, border=7, tilt=4)
    ov.alpha_composite(st, (PLAYER["c"][0] - PLAYER["r"] - 200, PLAYER["c"][1] + int(PLAYER["r"] * 0.98)))
    body = Image.new("RGBA", (300, 112), (0, 0, 0, 0))
    db = ImageDraw.Draw(body)
    db.polygon([(16, 0), (300, 0), (284, 112), (0, 112)], fill=YELLOW + (255,))
    db.text((30, 0), "SEND IT", font=f_num(86), fill=INK + (255,))
    db.text((206, 88), "[SPACE]", font=f_mono(14), fill=INK + (255,))
    st = MC.vinyl(body, border=8, tilt=-3)
    ov.alpha_composite(st, (1536, 912))
    img.alpha_composite(ov)


# ------------------------------------------------------------------ hand
CARDS = MC.CARDS
HAND_CX, HAND_Y = 1010, 846


def hand_slot(i, n):
    off = i - (n - 1) / 2
    rot = -off * 4.5
    return HAND_CX + off * 128, HAND_Y + abs(off) ** 1.6 * 10 - 6, rot


_C = {}


def card_body(i, w, h):
    """The card face WITHOUT the vinyl margin/shadow (for peel/curl), and the vinyl version."""
    key = (i, w, h)
    if key not in _C:
        _C[key] = MC.card_img(CARDS[i], w, h)
    return _C[key]


def plate_check():
    t = time.time()
    img = scene()
    hud(img)
    n = len(CARDS)
    for i in range(n):
        c = card_body(i, 144, 192)
        x, y, r = hand_slot(i, n)
        c = c.rotate(r, resample=Image.BICUBIC, expand=True)
        img.alpha_composite(c, (int(x - c.width / 2), int(y)))
    stickers(img)
    img.convert("RGB").save(os.path.join(SCR, "plate_check.png"))
    print("plate", round(time.time() - t, 1), "s")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "warm"
    if what == "warm":
        t = time.time()
        wheel("player")
        print("player", round(time.time() - t, 1), flush=True)
        t = time.time()
        wheel("boss")
        print("boss", round(time.time() - t, 1), flush=True)
        plate_check()
