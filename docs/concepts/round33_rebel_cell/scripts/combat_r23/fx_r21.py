"""Round 21: card-sourced CORRUPTED, evade v3, drone destroyed v2, phase change v2, RAM gain origins, Heat v3.

RULE (round 21): any effect caused by a card stems from the CARD PLAY: the sticker slaps on the target wheel,
dissolves (dissolve A bit stream), and the effect's bits leave from that slap point.

python fx_r21.py [corrupt_apply_v2 evade_v3 drone_destroyed_v2 phase_change_v2 ram_origins heat]
python fx_r21.py test <name> <t> ...
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
import effects_batch1 as EB
import card_play as CP
import fx_r20 as R20
import heat_alts as HA
from fxlib import seg, lerp, lerp2, bez, ease_out_cubic, ease_in_cubic, ease_in_out, ease_out_back
from slicelib import f_num, f_ui

OUT = P.OUT
W, H = 1920, 1080
PC, BC = P.PLAYER["c"], P.BOSS["c"]
PR, BR = P.PLAYER["r"], P.BOSS["r"]
pt, wedge = EB.pt, EB.wedge
CORRUPT, GREEN, ORANGE, RAM_C = EB.CORRUPT, EB.GREEN, EB.ORANGE, R20.RAM_C


# ================================================================== 1 apply CORRUPTED from the card play
CARD_I = 2                       # CORRUPT PACKET
SLAP = (BC[0], BC[1] + 6)
SLAP_ANG = -4.0
SLICE_T = pt(BC, BR * 0.70, 0)   # the slice under the needle (EXPLOIT 14)
T_IN = (0, 300)
T_DROP = (300, 380)
T_SQ = (380, 540)
T_DIS = (540, 900)


def face():
    return CP.card_face(CARD_I, 196, 262)


class SliceStream(CP.BitStream):
    """Dissolve A, re-aimed: the bits leave the slapped card and swirl up into the target slice."""

    def __init__(self):
        super().__init__(face(), SLAP, SLAP_ANG, *T_DIS, seed=21)
        rng = np.random.default_rng(22)
        for c in self.cells:
            c["col"] = CORRUPT if c["col"] != (250, 248, 240) else (255, 225, 238)
            e = (SLICE_T[0] + rng.normal(0, 46), SLICE_T[1] + rng.normal(0, 26))
            s = c["s"]
            side = 1 if s[0] >= BC[0] else -1
            c["e"] = e
            c["c"] = (BC[0] + side * rng.uniform(150, 230), BC[1] - BR * rng.uniform(0.2, 0.5))


STREAM = None


def card_st(t):
    if t < T_IN[1]:  # last stretch of the drag onto the wheel
        q = ease_out_cubic(seg(t, *T_IN))
        c = lerp2((1290, 860), (SLAP[0], SLAP[1] - 14), q)
        return dict(c=c, sx=1.1, sy=1.1, ang=lerp(8, SLAP_ANG - 2, q), peel=0.07, sh=((22, 34), 16, 0.38))
    if t < T_SQ[0]:
        p = ease_in_cubic(seg(t, *T_DROP))
        k = lerp(1.1, 1.0, p)
        return dict(c=lerp2((SLAP[0], SLAP[1] - 14), SLAP, p), sx=k, sy=k, ang=lerp(SLAP_ANG - 2, SLAP_ANG, p), peel=lerp(0.07, 0, p),
                    sh=(lerp2((22, 34), (2, 3), p), lerp(16, 2, p), lerp(0.38, 0.7, p)))
    q = seg(t, *T_SQ)
    if q < 0.35:
        w = ease_out_cubic(q / 0.35)
        sx, sy = lerp(1, 1.13, w), lerp(1, 0.86, w)
    elif q < 0.7:
        w = ease_in_out((q - 0.35) / 0.35)
        sx, sy = lerp(1.13, 0.97, w), lerp(0.86, 1.04, w)
    else:
        w = ease_in_out((q - 0.7) / 0.3)
        sx, sy = lerp(0.97, 1, w), lerp(1.04, 1, w)
    return dict(c=SLAP, sx=sx, sy=sy, ang=SLAP_ANG, peel=0.0, sh=((2, 3), 2, 0.7))


def hand_without_played(img):
    """The played card has left the hand: the other four close the gap."""
    idx = [i for i in range(5) if i != CARD_I]
    for j, i in enumerate(idx):
        x, y, r = P.hand_slot(j, 4)
        FX.place(img, CP.card_face(i, 144, 192), x, y + 96, 1, 1, r, shadow=((3, 5), 3, 0.55))


def corrupt_apply_v2(t):
    global STREAM
    if STREAM is None:
        STREAM = SliceStream()
    t_arr = max(c["rel"] + 40 + c["tr"] for c in STREAM.cells)
    t_hit = int(min(c["rel"] + 40 + c["tr"] for c in STREAM.cells)) + 60
    img = R20.scene2()
    h0 = EB.hand
    EB.hand = hand_without_played
    try:
        R20.dress(img, ram=4 if t >= T_SQ[0] else 5)
    finally:
        EB.hand = h0
    if t < T_DIS[0]:
        CP.draw_card(img, card_st(t), face(), gloss_t=seg(t, T_SQ[0], T_SQ[0] + 160) if T_SQ[0] <= t < T_SQ[0] + 160 else None)
    else:
        left = STREAM.card_left(t)
        if left.getbbox():
            FX.place(img, left, SLAP[0], SLAP[1], 1, 1, SLAP_ANG, shadow=((2, 3), 2, 0.7))
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    if T_SQ[0] <= t < T_SQ[0] + 120:
        q = seg(t, T_SQ[0], T_SQ[0] + 120)
        r = lerp(150, 230, ease_out_cubic(q))
        d.ellipse([SLAP[0] - r, SLAP[1] - r * 1.15, SLAP[0] + r, SLAP[1] + r * 1.15], outline=(255, 255, 255, int(150 * (1 - q))), width=4)
    if t >= T_DIS[0]:
        STREAM.draw(fx, t)
    # the slice soaks the bits up: it brightens per arrival, then the tear writes on
    t0, t1 = t_hit, t_hit + 320
    if t0 <= t < t0 + 110:
        d.polygon(wedge(BC, BR * 0.38, BR * 0.98, *R20.B_SLOT), fill=(255, 255, 255, int(170 * (1 - (t - t0) / 110))))
    if t0 <= t < t1 + 40:
        fx_, _, _ = R20.front_x(R20.B_BARS, t, t0, t1)
        m = Image.new("L", img.size, 0)
        ImageDraw.Draw(m).polygon(wedge(BC, BR * 0.38, BR * 0.98, *R20.B_SLOT), fill=255)
        ln = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(ln).rectangle([fx_ - 2, 0, fx_ + 2, H], fill=(255, 220, 235, 230))
        ln.putalpha(ImageChops.multiply(ln.split()[3], m))
        fx.alpha_composite(ln)
    if t >= t0:
        fx_, _, _ = R20.front_x(R20.B_BARS, t, t0, t1)
        R20.draw_bars(img, R20.B_BARS, BC, BR, R20.B_SLOT, front=fx_, side="left")
    img = EB.emit(img, fx, 0.4)
    if t >= t1 + 60:
        R20.badge(img, pt(BC, BR * 0.93, R20.B_SLOT[1] - 8), 24, t - t1 - 60)
        EB.chip(img, BC[0] - BR * 2.0, BC[1] - BR * 0.62, "CORRUPTED: 3 self-dmg, -1 RAM", CORRUPT, "status_corrupted", t - t1 - 140, size=22)
    if t < T_DROP[1] + 300:
        cur = card_st(min(t, T_DROP[0]))["c"]
        FX.cursor(img, cur[0] + 40, cur[1] - 60, t < T_DROP[0])
    return img


# ================================================================== 2 evade v3
T_ATK = 520
T_LIFT = 760
T_FLY = (820, 1620)
TOK_CTRL = (700, -320)
TOK_END = (-180, -160)
A_PATH = (R20.B_BLADE, (980, 60), R20.P_PTR)
FRAC_LIFT = 0.42


def token_pos(t):
    if t < T_FLY[0]:
        return R20.TOKEN
    return bez(R20.TOKEN, TOK_CTRL, TOK_END, seg(t, *T_FLY) ** 1.2)


def attack_head(t):
    if t < T_ATK:
        return None
    if t < T_LIFT:
        return bez(*A_PATH, FRAC_LIFT * seg(t, T_ATK, T_LIFT))
    base = bez(*A_PATH, FRAC_LIFT + 0.05 * seg(t, T_LIFT, T_LIFT + 140))
    w = ease_in_out(seg(t, T_FLY[0] + 120, T_FLY[0] + 440))  # veers only once the token is well up and away
    return lerp2(base, token_pos(max(t - 150, T_FLY[0] + 260)), w)


def evade_v3(t):
    if EB.TOK is None:
        EB.TOK = EB.token_sticker()
    if EB.WORD_E is None:
        EB.WORD_E = EB.vinyl_word("EVADED", GREEN, size=54, tilt=5)
    img = R20.scene2()
    R20.dress(img)
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    if 0 <= t < 120:
        d.polygon(wedge(PC, PR * 0.38, PR * 0.98, 270, 330), fill=GREEN + (int(150 * (1 - t / 120)),))
    EB.ES.draw(fx, t)
    if t >= T_ATK:
        hist = [attack_head(t - k * 22) for k in range(12)]
        hist = [h for h in hist if h is not None]
        al = R20.edge_alpha(hist[0])
        if al > 0.01 and len(hist) > 1:
            for k in range(len(hist) - 1):
                d.line([hist[k], hist[k + 1]], fill=ORANGE + (int(255 * al * (1 - k / len(hist))),), width=max(3, int(14 * (1 - k / len(hist)))))
            h0 = hist[0]
            d.ellipse([h0[0] - 11, h0[1] - 11, h0[0] + 11, h0[1] + 11], fill=(255, 255, 255, int(255 * al)))
    img = EB.emit(img, fx, 0.45)
    if 300 <= t < T_LIFT:
        EB.slap(img, EB.TOK, R20.TOKEN, t - 300, 180)
        if t >= 460:
            EB.chip(img, R20.TOKEN[0] + 44, R20.TOKEN[1] - 4, "EVADE 1", GREEN, None, t - 460, size=20)
    elif t >= T_LIFT:
        p = token_pos(t)
        al = R20.edge_alpha(p)
        if al > 0.01:
            lift = ease_out_back(seg(t, T_LIFT, T_LIFT + 120), 2.0)
            f = EB.TOK.copy()
            f.putalpha(f.split()[3].point(lambda v: int(v * al)))
            FX.place(img, f, p[0], p[1], 1 + 0.2 * lift, 1 + 0.2 * lift, -25 * seg(t, *T_FLY), shadow=((10 * lift + 4, 14 * lift + 6), 8, 0.35 * al))
    if t >= 1100:
        EB.slap(img, EB.WORD_E, (PC[0] + PR * 0.98, PC[1] + PR * 0.5), t - 1100, 200)
    return img


# ================================================================== 3 drone destroyed v2 (no DESTROYED chip, no BODYGUARD label)
def drone_destroyed_v2(t):
    chip0, pop0 = EB.chip, DS.number_pop

    def chip(img, x, y, text, *a, **k):
        if text == "DRONE DESTROYED":
            return
        return chip0(img, x, y, text, *a, **k)

    def pop(*a, **k):
        k.pop("sub", None)
        return pop0(*a, **k)

    EB.chip, DS.number_pop = chip, pop
    try:
        return R20.drone_destroyed(t)
    finally:
        EB.chip, DS.number_pop = chip0, pop0


# ================================================================== 4 phase change v2 (needle bits from the crossed pip)
def pip_point():
    meta = R20.ph_sprites()[0][2]
    return P.arc_point("boss", 230 - 100 * 0.66, meta, 0.5)


def make_needle_bits():
    pp = pip_point()
    base = pt(BC, BR * 1.05, 180)
    items = []
    rng = np.random.default_rng(31)
    for k in range(28):
        s = (pp[0] + rng.normal(0, 10), pp[1] + rng.normal(0, 10))
        c = ((s[0] + base[0]) / 2 + rng.normal(0, 30), max(s[1], base[1]) + 70 + rng.normal(0, 20))  # runs along under the arc
        e = (base[0] + rng.normal(0, 14), base[1] + rng.normal(0, 10))
        items.append(dict(s=s, c=c, e=e, t=R20.T_NEEDLE[0] - 420 + k * 12, tr=360, hold=50))
    return R20.Bits(items, ORANGE, px=(22, 30), seed=32)


def phase_change_v2(t):
    if not isinstance(getattr(R20, "_NB21", None), R20.Bits):
        R20._NB21 = make_needle_bits()
        R20.NEEDLE_BITS = R20._NB21
    img = R20.phase_change(t)
    # the crossed pip keeps glowing while it feeds the needle
    tt = t - R20.T_STOP if t >= R20.T_PH_HIT + R20.T_STOP else t
    if R20.T_NEEDLE[0] - 460 <= tt < R20.T_NEEDLE[0] + 120:
        pp = pip_point()
        q = seg(tt, R20.T_NEEDLE[0] - 460, R20.T_NEEDLE[0] + 120)
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        r = 22 + 8 * math.sin(q * 12)
        ImageDraw.Draw(lay).ellipse([pp[0] - r, pp[1] - r, pp[0] + r, pp[1] + r], fill=(255, 220, 120, int(200 * (1 - q * 0.6))))
        img = EB.emit(img, lay.filter(ImageFilter.GaussianBlur(6)), 0.6)
    return img


# ================================================================== 5 RAM gain: three origins
PIP = R20.PIP
TURN_C = (960, 40)
DECK_C = (478, 990)
ORIGINS = {
    "a": ("A  CLASS CORE", PC, lambda s: (s[0] - 260, s[1] + 260)),
    "b": ("B  TURN BANNER  (recommended)", TURN_C, lambda s: (960, 760)),
    "c": ("C  DECK / TERMINAL", DECK_C, lambda s: (s[0] - 40, s[1] - 170)),
}
_RB = {}


def ram_bits(key):
    if key not in _RB:
        _, src, ctrl = ORIGINS[key]
        rng = np.random.default_rng(40 + ord(key))
        items = []
        for k in range(16):
            s = (src[0] + rng.normal(0, 18), src[1] + rng.normal(0, 12))
            c0 = ctrl(src)
            items.append(dict(s=s, c=(c0[0] + rng.normal(0, 50), c0[1] + rng.normal(0, 40)), e=PIP(1 + k // 4), t=200 + k * 30,
                              tr=520 if key == "b" else 420, hold=40))
        _RB[key] = R20.Bits(items, RAM_C, px=(30, 38), seed=41)
    return _RB[key]


def ram_origin(t, key):
    bits = ram_bits(key)
    n_on = 1
    for i in range(1, 5):
        if t >= max(q["t"] + q["hold"] + q["tr"] for q in bits.p[(i - 1) * 4:i * 4]):
            n_on = i + 1
    img = R20.scene2()
    R20.dress(img, status="TURN 4   |   FREE NUDGE 1", ram=n_on)
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    src = ORIGINS[key][1]
    if 0 <= t < 300:
        q = t / 300
        if key == "a":
            r = PR * lerp(0.2, 0.42, q)
            d.ellipse([src[0] - r, src[1] - r, src[0] + r, src[1] + r], outline=RAM_C + (int(230 * (1 - q)),), width=6)
        elif key == "b":  # the TURN plate ticks over: a flash band across it
            d.rounded_rectangle([660, 10, 1260, 76], radius=10, outline=RAM_C + (int(255 * (1 - q)),), width=6)
            d.rectangle([660 + 600 * q - 30, 12, 660 + 600 * q + 30, 74], fill=(255, 255, 255, int(160 * (1 - q))))
        else:  # the deck's top edge lights like a terminal waking
            d.rounded_rectangle([446, 945, 516, 1040], radius=8, outline=RAM_C + (int(255 * (1 - q)),), width=5)
    bits.draw(fx, t)
    for i in range(1, 5):
        ta = max(q["t"] + q["hold"] + q["tr"] for q in bits.p[(i - 1) * 4:i * 4])
        if ta <= t < ta + 200:
            x, y = PIP(i)
            fl = 1 - (t - ta) / 200
            d.rectangle([x - 10, y - 18, x + 10, y + 18], fill=(255, 255, 255, int(255 * fl)))
    img = EB.emit(img, fx, 0.6)
    if t >= 1300:
        DS.number_pop(img, "+4 RAM", RAM_C, (300, 900), (300, 900), t - 1300, 2000, size=50)
    return img


def ram_origins():
    cw, chh = 640, 360
    frames, durs = [], []
    cols = {}
    for t in range(0, 1900, 40):
        S = Image.new("RGB", (3 * cw + 4 * 8, chh + 44), (14, 13, 20))
        d = ImageDraw.Draw(S)
        for j, key in enumerate("abc"):
            im = ram_origin(t, key).convert("RGB").resize((cw, chh), Image.LANCZOS)
            x = 8 + j * (cw + 8)
            S.paste(im, (x, 44))
            d.text((x + 4, 6), ORIGINS[key][0], font=f_num(30), fill=(255, 214, 64) if key == "b" else (255, 255, 255))
            if t in (240, 640, 1000, 1560):
                cols.setdefault(t, []).append(im)
        frames.append(S)
        durs.append(40)
    durs[-1] = 900
    s = FX.save_gif(frames, durs, os.path.join(OUT, "fx_ram_gain_origins.gif"), size=frames[0].size)
    print("fx_ram_gain_origins.gif", s // 1024, "KB", flush=True)
    # strip: 4 moments x 3 origins
    sw, sh = 480, 270
    St = Image.new("RGB", (3 * sw + 4 * 10 + 120, 4 * sh + 5 * 10 + 150), (14, 13, 20))
    d = ImageDraw.Draw(St)
    d.text((10, 8), "RAM GAIN  -  where does the +4 come from?", font=f_num(42), fill=(255, 255, 255))
    for j, key in enumerate("abc"):
        d.text((130 + j * (sw + 10), 62), ORIGINS[key][0], font=f_num(24), fill=(255, 214, 64) if key == "b" else (255, 255, 255))
    for i, t in enumerate((240, 640, 1000, 1560)):
        y = 96 + i * (sh + 10)
        d.text((10, y + sh / 2 - 14), "%d ms" % t, font=P.mono(22), fill=(255, 214, 64))
        for j, im in enumerate(cols[t]):
            St.paste(im.resize((sw, sh), Image.LANCZOS), (130 + j * (sw + 10), y))
    y = 96 + 4 * (sh + 10)
    for k, ln in enumerate(["RECOMMENDED B: the +4 is a per-TURN refill (GDD), so it drops out of the TURN N plate as it ticks over and falls down the",
                            "centre gap (never across a wheel) into the meter. A ties RAM to the class (wrong: every class gets +4); C reads as 'drawing cards'."]):
        d.text((10, y + k * 26), ln, font=P.mono(19), fill=(255, 214, 64))
    St.save(os.path.join(OUT, "fx_ram_gain_origins_strip.png"), optimize=True)
    print("strip", flush=True)


# ================================================================== 6 Heat v3 (backdrop only, dialled down)
ALARMS = [(110, 640), (1660, 300), (1840, 820)]  # side buildings only: never the target building


def alarms(img, t):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cores = []
    for i, (x, y) in enumerate(ALARMS):
        ph = ((t + i * 370) % 1100) / 1100
        on = 0.5 + 0.5 * math.cos(2 * math.pi * ph)
        col = (255, 60, 40) if i != 1 else (255, 170, 40)
        d.ellipse([x - 70, y - 44, x + 70, y + 44], fill=col + (int(170 * on),))
        cores.append((x, y, col, on))
        # a small rotating beacon beam
        a = 2 * math.pi * ph
        d.polygon([(x, y), (x + 120 * math.cos(a - 0.18), y + 50 * math.sin(a - 0.18)), (x + 120 * math.cos(a + 0.18), y + 50 * math.sin(a + 0.18))],
                  fill=col + (int(90 * on),))
    img = HA.additive(img, lay.filter(ImageFilter.GaussianBlur(14)), 1.0)
    dc = ImageDraw.Draw(img)
    for x, y, col, on in cores:
        dc.rectangle([x - 6, y - 6, x + 6, y + 6], fill=col + (255,))
        dc.rectangle([x - 2, y - 2, x + 2, y + 2], fill=(255, 255, 255, int(255 * on)))
    return img


def city_v3(img, t, lvl):
    if lvl == 0:
        return alarms(img, t)
    b = dict(R20.BANDS[lvl - 1])  # FLAGGED = old NOTICED, HUNTED = old FLAGGED
    b["wash"] = 0.0               # no siren tint at any band
    old = R20.BANDS
    R20.BANDS = [b, b, b]
    try:
        return R20.city_v2(img, t, 0)
    finally:
        R20.BANDS = old


def heat_frame(lvl, t):
    img = HA.world(city_v3, t, lvl)
    HA.ui(img)
    HA.heat_chip(img, lvl)
    return img


DESC = ["3 alarm beacons on side buildings; nothing on the target",
        "9 police lights + 1 searchlight on the target (was NOTICED)",
        "13 police lights + 2 searchlights (was FLAGGED); no siren tint"]


def heat():
    frames, durs = [], []
    for lvl in range(3):
        for t in range(0, 1680, 120):
            frames.append(heat_frame(lvl, t + lvl * 5000).convert("RGB").resize((960, 540), Image.LANCZOS))
            durs.append(120)
    durs[-1] = 600
    s = FX.save_gif(frames, durs, os.path.join(OUT, "heat_city_v3.gif"))
    print("heat_city_v3.gif", s // 1024, "KB", flush=True)
    cw, ch, gap = 800, 450, 14
    S = Image.new("RGB", (3 * cw + 4 * gap, ch + 120), (14, 13, 20))
    d = ImageDraw.Draw(S)
    d.text((gap, 10), "HEAT H1 v3  -  CITY REACTS, dialled down (backdrop only)", font=f_num(44), fill=(255, 255, 255))
    for lvl, (heat_, word, col) in enumerate(HA.LEVELS):
        x = gap + lvl * (cw + gap)
        S.paste(heat_frame(lvl, 600 + lvl * 5000).convert("RGB").resize((cw, ch), Image.LANCZOS), (x, 66))
        d.text((x, 66 + ch + 6), "HEAT %d  %s" % (heat_, word), font=f_num(26), fill=col)
        d.text((x, 66 + ch + 40), DESC[lvl], font=f_ui(18, b"SemiBold"), fill=(200, 200, 214))
    S.save(os.path.join(OUT, "heat_city_v3_strip.png"), optimize=True)
    print("heat strip", flush=True)


# ------------------------------------------------------------------ run
SINGLE = {
    "corrupt_apply_v2": (corrupt_apply_v2, 2400, DS.GIF_CROP, (960, 540)),
    "evade_v3": (evade_v3, 2000, (0, 0, 1920, 1080), (960, 540)),
    "drone_destroyed_v2": (drone_destroyed_v2, 2000, DS.GIF_CROP, (960, 540)),
    "phase_change_v2": (phase_change_v2, 2800, (900, 0, 1920, 1000), (612, 600)),
}


def run(name):
    fn, T, crop, size = SINGLE[name]
    frames, durs = [], []
    for t in range(0, T, int(FX.DT)):
        frames.append(fn(t).convert("RGB"))
        durs.append(int(FX.DT))
    R20.gifout("fx_%s.gif" % name, frames, durs, crop, size)


if __name__ == "__main__":
    args = sys.argv[1:] or list(SINGLE) + ["ram_origins", "heat"]
    if args[0] == "test":
        name = args[1]
        for a in args[2:]:
            if name == "ram":
                im = ram_origin(int(a.split(":")[1]), a.split(":")[0])
                a = a.replace(":", "_")
            elif name == "heat":
                im = heat_frame(int(a), 600)
            else:
                im = SINGLE[name][0](int(a))
            im.convert("RGB").save(os.path.join(P.SCR, "t_%s_%s.png" % (name, a)))
            print("test", name, a, flush=True)
        sys.exit()
    for a in args:
        if a in SINGLE:
            run(a)
        elif a == "ram_origins":
            ram_origins()
        elif a == "heat":
            heat()
