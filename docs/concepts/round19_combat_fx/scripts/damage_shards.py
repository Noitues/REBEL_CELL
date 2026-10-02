"""Round 18 / 2: binary damage shards on the D4 combat screen.

Four beats in one clip: (1) player hit on the boss slice under the pointer, (2) boss hit on the player's
HP arc (the drained segments shatter), (3) a CRIT (bigger burst, code streaks, RGB split, hit-stop),
(4) a blocked hit (shards bounce off the player's FIREWALL wall). Damage numbers pop, then fly into
the HP number, which ticks down; the wheel's HP arc is re-rendered at the new value.

python damage_shards.py        # damage_shards.gif + damage_shards_storyboard.png
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
from fxlib import seg, lerp, lerp2, bez, ease_out_cubic, ease_in_cubic, ease_in_out, ease_out_back
from slicelib import f_num, f_ui

OUT = P.OUT
PINK = (255, 61, 168)
ORANGE_HIT = (255, 120, 48)   # the boss EXPLOIT slice colour (Meridian orange)
CYAN = (92, 225, 255)
PC, BC = P.PLAYER["c"], P.BOSS["c"]
PR, BR = P.PLAYER["r"], P.BOSS["r"]
GIF_CROP = (240, 140, 1680, 950)  # 1440 x 810 -> 960 x 540

# ------------------------------------------------------------------ severity tiers (content config)
TIERS = [  # name, max dmg, shards, glyph px (min, max), speed (min, max), streaks, shake px
    ("S", 4, 9, (13, 18), (420, 720), 0, 0),
    ("M", 12, 18, (16, 24), (520, 960), 0, 2),
    ("L", 24, 30, (20, 30), (600, 1100), 2, 2),
    ("XL", 999, 44, (22, 34), (700, 1300), 7, 4),
]


def tier(dmg, crit=False):
    for t in TIERS:
        if dmg <= t[1]:
            return TIERS[-1] if crit else t
    return TIERS[-1]


# ------------------------------------------------------------------ shards
class Burst:
    """Closed-form particles: damped velocity, gravity, spin, 0/1 flip every 90 ms, white-hot core
    for 100 ms, fade over the last 40 % of life and 'bit rot' (the glyph breaks into 2-3 pixels)."""

    def __init__(self, origin, direction_deg, spread, count, px, speed, col, seed, gravity=260.0, damping=5.5,
                 life=(420, 650), dim=1.0, origins=None, delay=0):
        rng = np.random.default_rng(seed)
        self.p = []
        for i in range(count):
            o = origins[i % len(origins)] if origins else origin
            a = math.radians(direction_deg + rng.uniform(-spread / 2, spread / 2))
            v = rng.uniform(*speed)
            self.p.append(dict(o=(o[0] + rng.normal(0, 4), o[1] + rng.normal(0, 4)), vx=v * math.cos(a), vy=v * math.sin(a),
                               w=rng.uniform(-900, 900), a0=rng.uniform(-30, 30), px=rng.uniform(*px),
                               life=rng.uniform(*life), ch="01"[int(rng.random() < 0.5)], fl=rng.uniform(0, 90),
                               d=delay + rng.uniform(0, 30), rot=[(rng.normal(0, 5), rng.normal(0, 5)) for _ in range(3)]))
        self.col = col
        self.g = gravity
        self.k = damping
        self.dim = dim

    def pos(self, s, age):
        tt = age / 1000
        e = (1 - math.exp(-self.k * tt)) / self.k
        return s["o"][0] + s["vx"] * e, s["o"][1] + s["vy"] * e + 0.5 * self.g * tt * tt

    def draw(self, layer, age):
        d = ImageDraw.Draw(layer)
        for s in self.p:
            a = age - s["d"]
            if a < 0 or a > s["life"]:
                continue
            q = a / s["life"]
            x, y = self.pos(s, a)
            alpha = (1 - seg(q, 0.6, 1.0)) * self.dim
            col = self.col
            if q > 0.72:  # bit rot: the glyph breaks into pixels
                for dx, dy in s["rot"]:
                    r = max(1, s["px"] * 0.12)
                    d.rectangle([x + dx * (1 + q) - r, y + dy * (1 + q) - r, x + dx * (1 + q) + r, y + dy * (1 + q) + r],
                                fill=col + (int(255 * alpha),))
                continue
            ch = s["ch"] if int((a + s["fl"]) / 90) % 2 == 0 else ("1" if s["ch"] == "0" else "0")
            core = max(0.0, 1 - a / 100)
            g = FX.glyph(ch, s["px"], col, core=core, rim=0.35)
            FX.paste_c(layer, g, x, y, alpha=alpha, angle=s["a0"] + s["w"] * a / 1000)


class Streaks:
    """CRIT: straight code strings fly out along their velocity for 170 ms, then break into shards."""

    def __init__(self, origin, direction_deg, spread, n, col, seed, fly=170):
        rng = np.random.default_rng(seed)
        self.s = []
        for i in range(n):
            a = direction_deg - spread / 2 + spread * (i + 0.5) / n + rng.normal(0, 6)
            txt = " ".join("".join("01"[int(v)] for v in rng.integers(0, 2, 4)) for _ in range(2))
            L = rng.uniform(150, 230)
            self.s.append(dict(a=a, txt=txt, L=L))
        self.o = origin
        self.col = col
        self.fly = fly
        ends = [(origin[0] + s["L"] * math.cos(math.radians(s["a"])), origin[1] + s["L"] * math.sin(math.radians(s["a"]))) for s in self.s]
        self.after = Burst(origin, direction_deg, spread + 30, n * 6, (16, 26), (120, 340), col, seed + 1, origins=ends, delay=fly, life=(380, 560))

    def draw(self, layer, age):
        if age < 0:
            return
        if age < self.fly:
            q = ease_out_cubic(age / self.fly)
            f = P.mono(26)
            for s in self.s:
                dist = s["L"] * q
                x = self.o[0] + dist * math.cos(math.radians(s["a"]))
                y = self.o[1] + dist * math.sin(math.radians(s["a"]))
                tw = int(f.getlength(s["txt"])) + 12
                im = Image.new("RGBA", (tw, 40), (0, 0, 0, 0))
                ImageDraw.Draw(im).text((6, 4), s["txt"], font=f, fill=(255, 250, 245, 255), stroke_width=1, stroke_fill=self.col + (255,))
                im = im.rotate(-s["a"], resample=Image.BICUBIC, expand=True)
                layer.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
        self.after.draw(layer, age)


def cracks(layer, origin, age, seed, n=7, dur=200):
    if age < 0 or age > dur:
        return
    rng = np.random.default_rng(seed)
    d = ImageDraw.Draw(layer)
    al = int(255 * (1 - age / dur))
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi)
        pts = [origin]
        x, y = origin
        for k in range(4):
            a += rng.normal(0, 0.35)
            L = rng.uniform(18, 34)
            x, y = x + L * math.cos(a), y + L * math.sin(a)
            pts.append((x, y))
        d.line(pts, fill=(255, 255, 255, al), width=4 if i % 2 else 3)


def flash_disc(layer, c, r, alpha):
    d = ImageDraw.Draw(layer)
    d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=(255, 255, 255, int(255 * alpha)))


def wedge(c, r0, r1, a0, a1, n=18):
    """Screen-angle wedge (deg, 0 = east, clockwise)."""
    out = [(c[0] + r1 * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c[1] + r1 * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    out += [(c[0] + r0 * math.cos(math.radians(a1 - (a1 - a0) * i / n)), c[1] + r0 * math.sin(math.radians(a1 - (a1 - a0) * i / n))) for i in range(n + 1)]
    return out


def slice_flash(layer, alpha):
    ImageDraw.Draw(layer).polygon(wedge(BC, BR * 0.38, BR * 0.99, -120, -60), fill=(255, 255, 255, int(255 * alpha)))


def pixel_tear(img, box, seed, strength):
    """Digital damage: a few horizontal bands of the hit area slip sideways for 3 frames."""
    rng = np.random.default_rng(seed)
    reg = img.crop(box)
    a = np.asarray(reg).copy()
    h = a.shape[0]
    y = 0
    while y < h:
        bh = int(rng.integers(4, 16))
        if rng.random() < 0.55:
            dx = int(rng.normal(0, 10 * strength))
            a[y:y + bh] = np.roll(a[y:y + bh], dx, axis=1)
        y += bh
    img.paste(Image.fromarray(a), box[:2])


def region_rgb_split(img, box, dx):
    reg = img.crop(box).convert("RGB")
    r, g, b = reg.split()
    r = ImageChops.offset(r, -dx, 0)
    b = ImageChops.offset(b, dx, 0)
    img.paste(Image.merge("RGB", (r, g, b)).convert("RGBA"), box[:2])


def tracer(layer, p0, ctrl, p1, q, col, width=6):
    """The hit flying in: a short comet along a Bezier (white head, coloured tail)."""
    if q <= 0 or q >= 1:  # round 19 fix: the head no longer lingers after impact
        return
    d = ImageDraw.Draw(layer)
    pts = [bez(p0, ctrl, p1, max(0.0, q - 0.22 * (1 - k / 10))) for k in range(11)]
    for k in range(10):
        a = int(255 * (k + 1) / 10)
        d.line([pts[k], pts[k + 1]], fill=col + (a,), width=max(2, int(width * (k + 1) / 10)))
    hx, hy = pts[-1]
    d.ellipse([hx - width, hy - width, hx + width, hy + width], fill=(255, 255, 255, 255))


# ------------------------------------------------------------------ numbers
def number_pop(img, txt, col, start, target, age, fly_at, fly_dur=200, size=70, crit=False, sub=None):
    """Pop 1.5 -> 1 (ease-out-back, 120 ms), rise 24 px, then fly into the HP number (ease-in)."""
    if age < 0 or age > fly_at + fly_dur:
        return
    s = lerp(1.5, 1.0, ease_out_back(seg(age, 0, 120), 2.0))
    x, y = start[0], start[1] - 24 * ease_out_cubic(seg(age, 0, fly_at))
    if age > fly_at:
        q = ease_in_cubic(seg(age, fly_at, fly_at + fly_dur))
        x, y = lerp(x, target[0], q), lerp(y, target[1], q)
        s *= lerp(1.0, 0.45, q)
    f = P.anton(int(size * s))
    tw = int(f.getlength(txt)) + 24
    im = Image.new("RGBA", (tw, int(size * s * 1.5) + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((12, 4), txt, font=f, fill=(255, 255, 255, 255), stroke_width=max(2, int(5 * s)), stroke_fill=MC.INK + (255,))
    tint = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(tint).text((12, 4), txt, font=f, fill=col + (255,))
    tint = tint.crop((0, int(im.height * 0.45), im.width, im.height))  # lower half in the hit colour
    im.alpha_composite(tint, (0, int(im.height * 0.45)))
    if crit and age < fly_at:
        im = FX.rgb_split(im, 4)
    img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
    if sub and age < fly_at:
        fs = f_ui(20, b"Bold Condensed")
        sw = fs.getlength(sub) + 16
        d = ImageDraw.Draw(img)
        bx, by = x - sw / 2, y + size * 0.55
        d.rounded_rectangle([bx, by, bx + sw, by + 28], radius=5, fill=(10, 9, 15, 235), outline=col + (255,), width=2)
        d.text((bx + 8, by + 2), sub, font=fs, fill=col + (255,))


def caption(img, text):
    d = ImageDraw.Draw(img)
    f = P.mono(26)
    x, y = GIF_CROP[0] + 16, GIF_CROP[1] + 92
    tw = f.getlength(text)
    d.rounded_rectangle([x, y, x + tw + 24, y + 40], radius=6, fill=(10, 9, 15, 225), outline=(255, 214, 64, 255), width=2)
    d.text((x + 12, y + 6), text, font=f, fill=(255, 214, 64, 255))


# ------------------------------------------------------------------ the clip
MP = P.wheel("player")[2]
MB = P.wheel("boss")[2]
PB, EB, _, _ = P.hp_boxes()
P_HP_C = ((PB[0] + PB[2]) / 2, (PB[1] + PB[3]) / 2)
B_HP_C = ((EB[0] + EB[2]) / 2, (EB[1] + EB[3]) / 2)

P_BLADE = (PC[0], PC[1] - PR * 1.12)
B_BLADE = (BC[0], BC[1] - BR * 1.12)
B_SLICE = (BC[0], BC[1] - BR * 0.74)
P_ARC_HIT = P.arc_point("player", 173.3, MP)
WALL_ANG = 32.0  # player wheel, deg from top clockwise
WALL_HIT = (PC[0] + PR * 1.17 * math.sin(math.radians(WALL_ANG)), PC[1] - PR * 1.17 * math.cos(math.radians(WALL_ANG)))

I1, I2, I3, I4 = 240, 1340, 2480, 3780
HITSTOP = 120
T_END = 4900

B1 = Burst(B_SLICE, -112, 80, tier(8)[2], tier(8)[3], tier(8)[4], PINK, 11)
B2 = Burst(P_ARC_HIT, 168, 70, tier(14)[2], tier(14)[3], tier(14)[4], ORANGE_HIT, 12, gravity=200)
B3 = Burst(B_SLICE, -100, 150, tier(24, True)[2], tier(24, True)[3], tier(24, True)[4], PINK, 13, life=(480, 720))
S3 = Streaks(B_SLICE, -105, 150, 7, PINK, 14)
# blocked: most shards bounce off the wall (dim, heavy gravity); 3 small ones get through
B4 = Burst(WALL_HIT, -60, 80, 22, (14, 20), (200, 420), (190, 170, 160), 15, gravity=520, life=(380, 560), dim=0.85)
B4T = Burst(WALL_HIT, 150, 20, 3, (12, 14), (160, 220), ORANGE_HIT, 16, gravity=0, life=(260, 320), delay=40)


def hp_values(t):
    p_hp, b_hp = 41, 340
    p_state, b_state = (41, 14), (340, 8)
    if t >= I1 + 620 + 200:
        b_hp, b_state = 332, (332, 0)
    if t >= I2 + 560 + 200:
        p_hp, p_state = 27, (27, 0)
    if t >= I3 + HITSTOP + 640 + 200:
        b_hp, b_state = 308, (308, 0)
    if t >= I4 + 420 + 200:
        p_hp, p_state = 25, (25, 0)
    return p_hp, b_hp, p_state, b_state


def shake(t, at, px, dur=90, seed=0):
    a = t - at
    if a < 0 or a > dur or px <= 0:
        return (0, 0)
    rng = np.random.default_rng(int(a // 40) + seed * 100)
    k = 1 - a / dur
    return (int(rng.integers(-px, px + 1) * k), int(rng.integers(-px, px + 1) * k))


def frame(t_real, reduce=False):
    # crit hit-stop: hold the impact frame for 3 frames
    t = t_real
    if I3 <= t_real < I3 + HITSTOP:
        t = I3
    elif t_real >= I3 + HITSTOP:
        t = t_real - HITSTOP
    tt = t_real  # numbers/HP use real time after the stop
    p_hp, b_hp, p_state, b_state = hp_values(t_real)
    b_off = (0, 0)
    p_off = (0, 0)
    if not reduce:
        b_off = shake(t, I1, 2, seed=1)
        if t_real >= I3 + HITSTOP:
            b_off = shake(t_real, I3 + HITSTOP, 4, 140, seed=3)
        p_off = shake(t, I2, 2, seed=2)
        if t >= I4:
            p_off = shake(t, I4, 1, 60, seed=4)
    img = P.hp_scene(p_state, b_state, p_off, b_off)
    P.hud(img, hp_p=p_hp, hp_e=b_hp, next_p=False, next_e=False)
    P.stickers(img)
    from card_play import card_face
    for i in range(5):
        x, y, r = P.hand_slot(i, 5)
        FX.place(img, card_face(i, 144, 192), x, y + 96, 1, 1, r, shadow=((3, 5), 3, 0.55))
    if reduce:
        return img
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    # 1 player -> boss slice
    tracer(fx, P_BLADE, (960, 110), B_SLICE, seg(t, I1 - 200, I1), PINK)
    if 0 <= t - I1 < 80:
        slice_flash(fx, 0.55 * (1 - (t - I1) / 80))
        flash_disc(fx, B_SLICE, 34, 0.6)
    B1.draw(fx, t - I1)
    # 2 boss -> player HP arc
    tracer(fx, B_BLADE, (980, 960), P_ARC_HIT, seg(t, I2 - 220, I2), ORANGE_HIT)
    if 0 <= t - I2 < 80:
        flash_disc(fx, P_ARC_HIT, 30, 0.6)
        d = ImageDraw.Draw(fx)
        for k in range(14, 20):  # the six drained segments flash white, then become the shards
            a0 = 230 - 100 * (k + 0.88) / 30
            a1 = 230 - 100 * (k + 0.12) / 30
            pts = [P.arc_point("player", a0 + (a1 - a0) * j / 4, MP, fr) for fr in (0, 1) for j in (range(5) if fr == 0 else range(4, -1, -1))]
            d.polygon(pts, fill=(255, 255, 255, int(220 * (1 - (t - I2) / 80))))
    B2.draw(fx, t - I2)
    # 3 crit
    tracer(fx, P_BLADE, (960, 90), B_SLICE, seg(t, I3 - 180, I3), (255, 200, 235), width=9)
    if 0 <= t - I3 < 100:
        slice_flash(fx, 0.7 * (1 - (t - I3) / 100))
        flash_disc(fx, B_SLICE, 56, 0.7)
    cracks(fx, B_SLICE, t - I3, 21)
    S3.draw(fx, t - I3)
    b3 = Image.new("RGBA", img.size, (0, 0, 0, 0))
    B3.draw(b3, t - I3)
    if 0 <= t - I3 < 220:
        b3 = FX.rgb_split(b3, 3)
    fx.alpha_composite(b3)
    # 4 blocked
    tracer(fx, B_BLADE, (980, 60), WALL_HIT, seg(t, I4 - 220, I4), ORANGE_HIT)
    wall(fx, t)
    B4.draw(fx, t - I4)
    B4T.draw(fx, t - I4)
    # pixel tear on the hit slice (3 frames), RGB split of the boss region on the crit
    if 0 <= t_real - I1 < 120:
        pixel_tear(img, (int(B_SLICE[0] - 130), int(B_SLICE[1] - 70), int(B_SLICE[0] + 130), int(B_SLICE[1] + 70)), int(t_real), 1.0)
    if I3 <= t_real < I3 + HITSTOP + 120:
        region_rgb_split(img, (BC[0] - 300, BC[1] - 300, BC[0] + 300, BC[1] + 300), 6 if t_real < I3 + HITSTOP else 3)
        pixel_tear(img, (int(B_SLICE[0] - 170), int(B_SLICE[1] - 90), int(B_SLICE[0] + 170), int(B_SLICE[1] + 90)), int(t), 1.6)
    if fx.getbbox():
        img = FX.glow_add(img, fx, 5, 20, 0.5)
        img.alpha_composite(fx)
    # numbers
    number_pop(img, "-8", PINK, (B_SLICE[0] + 120, B_SLICE[1] - 40), B_HP_C, tt - I1, 620)
    number_pop(img, "-14", ORANGE_HIT, (P_ARC_HIT[0] + 150, P_ARC_HIT[1] - 10), P_HP_C, tt - I2, 560)
    number_pop(img, "-24", PINK, (B_SLICE[0] + 150, B_SLICE[1] - 60), B_HP_C, tt - I3 - HITSTOP, 640, size=96, crit=True, sub="CRIT  x2 PERFECT")
    number_pop(img, "-2", ORANGE_HIT, (WALL_HIT[0] + 170, WALL_HIT[1] + 30), P_HP_C, tt - I4, 420, size=54, sub="BLOCK 12  ->  2")
    return img


def wall(layer, t):
    """The player's FIREWALL block: a crenellated cyan wall stands outside the rim, between the hit and
    the wheel (round 17 rule). Pops 0.85 -> 1 in 100 ms before the hit, ripples on impact, fades."""
    a = t - (I4 - 120)
    if a < 0 or a > 1300:
        return
    s = lerp(0.85, 1.0, ease_out_back(seg(a, 0, 100), 2.0))
    al = (1 - seg(a, 900, 1300))
    rip = max(0.0, 1 - abs(t - I4) / 120) if t >= I4 - 20 else 0
    d = ImageDraw.Draw(layer)
    r0, r1 = PR * 1.08 * s, PR * 1.24 * s
    a0, a1 = WALL_ANG - 32, WALL_ANG + 32  # deg from top
    n = 8
    for i in range(n):
        b0 = a0 + (a1 - a0) * i / n + 0.6
        b1 = a0 + (a1 - a0) * (i + 1) / n - 0.6
        for row, (ra, rb) in enumerate(((r0, (r0 + r1) / 2 - 1), ((r0 + r1) / 2 + 1, r1))):
            off = 0.5 * (b1 - b0) * (row % 2)
            c0, c1 = b0 + off, b1 + off
            c1 = min(c1, a1)
            pts = [(PC[0] + ra * math.sin(math.radians(c0 + (c1 - c0) * j / 4)), PC[1] - ra * math.cos(math.radians(c0 + (c1 - c0) * j / 4))) for j in range(5)]
            pts += [(PC[0] + rb * math.sin(math.radians(c1 - (c1 - c0) * j / 4)), PC[1] - rb * math.cos(math.radians(c1 - (c1 - c0) * j / 4))) for j in range(5)]
            col = tuple(int(lerp(v, 255, rip * 0.7)) for v in CYAN)
            d.polygon(pts, fill=col + (int(225 * al),), outline=(10, 30, 40, int(255 * al)))
        if i % 2 == 0:  # crenellation on the outer (hit) side
            cm = (b0 + b1) / 2
            q0, q1 = cm - (b1 - b0) * 0.3, cm + (b1 - b0) * 0.3
            pts = [(PC[0] + r1 * math.sin(math.radians(q)), PC[1] - r1 * math.cos(math.radians(q))) for q in (q0, q1)]
            pts += [(PC[0] + (r1 + 14) * math.sin(math.radians(q)), PC[1] - (r1 + 14) * math.cos(math.radians(q))) for q in (q1, q0)]
            d.polygon(pts, fill=CYAN + (int(225 * al),), outline=(10, 30, 40, int(255 * al)))


# ------------------------------------------------------------------ outputs
KEYS = [  # time, label, crop centre, caption
    (120, "01 TRACER", B_SLICE, ["Hit flies 200 ms along a Bezier, white head,", "slice-colour tail (pre-roll before impact)."]),
    (320, "02 HIT ON SLICE  -8 (M)", B_SLICE, ["18 pink 0/1 shards, white-hot 100 ms; slice", "flash 80 ms + pixel tear 3 fr; shake 2 px."]),
    (720, "03 NUMBER -> HP", (BC[0] + 40, BC[1] + 200), ["-8 pops 1.5->1 (120 ms), rises, flies into", "the HP number at +620 ms; HP 340 -> 332."]),
    (1440, "04 HIT ON YOUR HP ARC  -14", P_ARC_HIT, ["The 6 drained arc segments flash white and", "burst as orange shards (attacker colour)."]),
    (2480, "05 CRIT: HIT-STOP", B_SLICE, ["3-frame freeze on impact: flash disc, cracks,", "RGB split of the wheel region (6 px)."]),
    (2720, "06 CRIT: STREAKS BREAK", B_SLICE, ["7 code streaks fly 170 ms then shatter;", "44 shards up to 36 px, RGB-split; shake 4 px."]),
    (3800, "07 BLOCKED: BOUNCE", WALL_HIT, ["FIREWALL wall pops 120 ms before the hit;", "dim shards bounce off, gravity 520 px/s2."]),
    (4120, "08 BLOCKED: 2 THROUGH", (WALL_HIT[0] + 20, WALL_HIT[1] + 160), ["3 shards pass the wall; -2 with a", "BLOCK 12 -> 2 equation chip; HP 27 -> 25."]),
]


def crop_at(img, c, w=760, h=520):
    x0 = int(min(max(0, c[0] - w / 2), 1920 - w))
    y0 = int(min(max(0, c[1] - h / 2), 1080 - h))
    return img.crop((x0, y0, x0 + w, y0 + h))


def tier_strip():
    """Peak frame (+120 ms) of each severity tier on the boss slice, plus the reduce-effects end state."""
    cells = []
    for k, (dmg, crit) in enumerate(((3, False), (8, False), (18, False), (30, True))):
        tr = tier(dmg, crit)
        img = P.hp_scene()
        P.hud(img, next_p=False, next_e=False)
        fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
        b = Burst(B_SLICE, -108, 80 + 12 * k, tr[2], tr[3], tr[4], PINK, 40 + k)
        if tr[5]:
            Streaks(B_SLICE, -105, 150, tr[5], PINK, 50 + k).draw(fx, 110)
        b.draw(fx, 120)
        if crit:
            fx = FX.rgb_split(fx, 5)
        img = FX.glow_add(img, fx, 5, 20, 0.5)
        img.alpha_composite(fx)
        number_pop(img, "-%d" % dmg, PINK, (B_SLICE[0] + 130, B_SLICE[1] - 40), B_HP_C, 120, 620, size=60 + 10 * k, crit=crit)
        im = crop_at(img, (B_SLICE[0] + 10, B_SLICE[1] - 40), 470, 380)
        cells.append((im, "%s  dmg %s  %d x %d-%dpx%s" % (tr[0], {0: "1-4", 1: "5-12", 2: "13-24", 3: "25+/crit"}[k], tr[2], tr[3][0], tr[3][1],
                                                                          " +%d str" % tr[5] if tr[5] else "")))
    # reduce effects: end state only
    img = P.hp_scene((41, 14), (332, 0))
    P.hud(img, hp_e=332, next_p=False, next_e=False)
    d = ImageDraw.Draw(img)
    fs = P.anton(34)
    x, y = EB[2] + 14, EB[1] + 14
    d.rounded_rectangle([x, y, x + 70, y + 48], radius=6, fill=(10, 9, 15, 240), outline=(255, 64, 72, 255), width=3)
    d.text((x + 12, y + 2), "-8", font=fs, fill=(255, 64, 72, 255))
    im = crop_at(img, (BC[0] + 40, BC[1] + 230), 470, 380)
    cells.append((im, "REDUCE: HP set at once, static chip"))
    gap = 14
    W = sum(c[0].width for c in cells) + gap * (len(cells) - 1)
    S = Image.new("RGB", (W, 380 + 40), (14, 13, 20))
    d = ImageDraw.Draw(S)
    x = 0
    for im, lab in cells:
        S.paste(im.convert("RGB"), (x, 0))
        d.text((x + 4, 386), lab, font=P.mono(17), fill=(255, 214, 64))
        x += im.width + gap
    return S


def main():
    frames, durs = [], []
    crops = {}
    keyt = {k[0]: k for k in KEYS}
    for t in range(0, T_END, int(FX.DT)):
        img = frame(t)
        cap = ("01  YOUR HIT ON THE BOSS SLICE   -8   tier M" if t < 1100 else
               "02  BOSS HIT ON YOUR HP ARC   -14   tier L" if t < 2240 else
               "03  CRIT   -24   tier XL + RGB split + hit-stop" if t < 3540 else
               "04  BLOCKED   14 - BLOCK 12 = 2")
        if t in keyt:
            crops[t] = crop_at(img.convert("RGB"), keyt[t][2])
        g = img.copy()
        caption(g, cap)
        frames.append(g.convert("RGB").crop(GIF_CROP).resize((960, 540), Image.LANCZOS))
        durs.append(int(FX.DT))
        if t % 400 == 0:
            print("t", t, flush=True)
    durs[-1] = 800
    size = FX.save_gif(frames, durs, os.path.join(OUT, "damage_shards.gif"))
    print("gif", size // 1024, "KB", flush=True)
    cells = [(crops[t], lab, "%d ms" % t, caps) for t, lab, c, caps in KEYS]
    FX.storyboard(cells, os.path.join(OUT, "damage_shards_storyboard.png"),
                  "DAMAGE SHARDS  -  binary 0/1 shards from the hit point",
                  "1:1 crops of the 1920x1080 D4 combat screen. Times from clip start (hits at 240 / 1340 / 2480 / 3780 ms). Row below: severity tiers at +120 ms, and reduce effects.",
                  cols=4, extra=tier_strip(),
                  note_lines=["layer order: wheels (HP arc re-drawn at the new value) | HUD | flash + tracer + shards (additive glow, light spill) | damage number | equation chip",
                              "shard colour = the ATTACKING slice's colour (both directions). Tier from damage after block; a crit always uses XL."])
    print("done", flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "test":
        for a in sys.argv[2:]:
            frame(int(a)).convert("RGB").save(os.path.join(P.SCR, "dst_%s.png" % a))
            print("test", a, flush=True)
    else:
        main()
