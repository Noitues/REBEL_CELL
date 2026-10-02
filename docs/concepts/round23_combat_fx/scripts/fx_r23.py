"""Round 23: CORRUPTED as the locked full-slice glitch overlay (no badge, no rule chip), and the temporary-label
rule applied to EVADED, CHECKPOINT, PHASE 2 and DELETED.

python fx_r23.py [corrupt_apply_v4 corrupt_tick_v3 evade_v4 respin_v2 phase_change_v3 enemy_defeated_v2 board]
python fx_r23.py test <name> <t> ...
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import plates as P
import fxlib as FX
import damage_shards as DS
import effects_batch1 as EB
import fx_r20 as R20
import fx_r21 as R21
import fx_r22 as R22  # noqa: F401  (installs the locked SEND IT sticker on every frame)
from fxlib import seg, lerp
from slicelib import f_num

OUT = P.OUT
W, H = 1920, 1080
PC, BC = P.PLAYER["c"], P.BOSS["c"]
PR, BR = P.PLAYER["r"], P.BOSS["r"]
pt, wedge = EB.pt, EB.wedge
PINK_G = np.array([1.0, 0.16, 0.62], np.float32)
GREEN_G = np.array([0.18, 1.0, 0.50], np.float32)
CORRUPT = EB.CORRUPT


# ================================================================== the locked CORRUPTED overlay, in screen space
def glitch(img, c, r, slot, t, seed=1, k=1.0, front=None, side="left", spike=0.0):
    """Round 14/15 CORRUPTED (overlays.corrupted) on one slice of a composited frame:
    1 tear bands (whole rows of the slice, bezel included, slide sideways),
    2 pink / green split of the outline and the bright content,
    3 pink / green colour bands on the screen + scanline flicker,
    4 a bright tear line sweeping down.
    The read block (glyph + value) only gets 35 % of 2-4. `front`: screen x of a wipe; side='left' keeps
    the glitch left of it, 'right' keeps it right of it. `spike` 0..1 doubles the tear amplitude."""
    if k <= 0.01:
        return img
    poly = wedge(c, r * 0.37, r * 1.02, slot[0] - 1, slot[1] + 1, 30)
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    pad = 26
    box = (int(max(0, min(xs) - pad)), int(max(0, min(ys) - pad)), int(min(W, max(xs) + pad)), int(min(H, max(ys) + pad)))
    crop = img.crop(box).convert("RGB")
    src = np.asarray(crop, np.float32) / 255
    h, w = src.shape[:2]
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon([(x - box[0], y - box[1]) for x, y in poly], fill=255)
    mask = np.asarray(m.filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
    mdil = np.asarray(m.filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.GaussianBlur(2)), np.float32) / 255
    frame = int(t / 83) % 12
    rng = np.random.default_rng(seed * 31 + frame)
    reg = src.copy()
    # 1 tear bands
    for _ in range(5 + int(3 * spike)):
        y0 = int(rng.random() * h)
        hh = int(3 + rng.random() * 12)
        dx = int((rng.random() - 0.5) * 2 * (6 + 14 * rng.random()) * (1 + spike))
        reg[y0:y0 + hh] = np.roll(src[y0:y0 + hh], dx, axis=1)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # read window (glyph + value block)
    rc = pt(c, r * 0.70, (slot[0] + slot[1]) / 2)
    win = np.exp(-(((xx + box[0] - rc[0]) / (r * 0.26)) ** 2 + ((yy + box[1] - rc[1]) / (r * 0.18)) ** 2) * 1.6)
    thin = 1 - 0.65 * win
    # 2 pink / green split
    lum = reg.max(axis=2)
    gy, gx = np.gradient(mask)
    edge = np.clip(np.hypot(gx, gy) * 2.5, 0, 1)
    sig = np.clip(edge + np.clip(lum - 0.45, 0, 1) * 0.9, 0, 1)
    kk = int(3 + 2 * math.sin(2 * math.pi * (t / 1000) * 3))
    add = np.roll(sig, kk, axis=1)[..., None] * PINK_G * 0.85 + np.roll(sig, -kk, axis=1)[..., None] * GREEN_G * 0.75
    reg = reg + add * thin[..., None]
    # 3 colour bands + scanlines
    band = np.sin(yy / 5 + frame * 1.7) * np.sin(yy / 17 - frame * 0.9)
    tint = np.where((band > 0.35)[..., None], PINK_G, np.where((band < -0.45)[..., None], GREEN_G, 0.0))
    reg = reg + tint * (0.22 * (np.abs(band) > 0.35) * mask * thin)[..., None]
    scan = (np.floor(yy / 2) % 2 == 0) * mask
    reg = reg * (1 - 0.18 * scan * thin)[..., None]
    # 4 tear line sweeping down
    ty = ((t % 1000) / 1000) * h
    tear = np.exp(-((yy - ty) / 1.2) ** 2) * mask
    reg = reg + (PINK_G * 0.6 + GREEN_G * 0.4) * (tear * 0.9)[..., None]
    a = np.clip(mdil, 0, 1) * k
    if front is not None:
        fx_ = front - box[0]
        sel = (xx < fx_) if side == "left" else (xx >= fx_)
        a = a * sel
    out = src * (1 - a[..., None]) + np.clip(reg, 0, 1) * a[..., None]
    res = img.copy()
    res.paste(Image.fromarray((out * 255 + 0.5).astype(np.uint8)).convert("RGBA"), box[:2])
    return res


def wedge_xrange(c, r, slot):
    poly = wedge(c, r * 0.37, r * 1.02, *slot)
    return min(p[0] for p in poly) - 10, max(p[0] for p in poly) + 10


# ================================================================== temporary labels (round 22 rule) for locked effects
_TL = {}


def _templabel_slap(orig_slap, bag):
    def slap(img, sprite, c, age, dur=200):
        words = [getattr(EB, "WORD_E", None), getattr(EB, "WORD_D", None), getattr(R20, "CHECK", None), getattr(R20, "PHASE_W", None)]
        if any(sprite is w_ for w_ in words if w_ is not None):
            key = id(sprite)
            if key not in _TL:
                _TL[key] = R22.TempLabel(sprite, c, 0, hold=750, col=(255, 255, 255), slap=True, seed=key % 97)
            lab = _TL[key]
            lab.c = c
            lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            EB.slap = orig_slap  # TempLabel slaps with the real slap (no recursion)
            try:
                lab.draw(img, lay, age)
            finally:
                EB.slap = slap
            bag.append(lay)
            return
        return orig_slap(img, sprite, c, age, dur)
    return slap


TEMP_CHIPS = ("2 NEEDLES: hits land twice", "-4 RAM", "-1 RAM")


def _templabel_chip(orig_chip, bag):
    def chip(img, x, y, text, col, glyph=None, age=0, size=26):
        if text in TEMP_CHIPS:
            if age < 0:
                return
            key = ("chip", text)
            if key not in _TL:
                tmp = Image.new("RGBA", (900, 120), (0, 0, 0, 0))
                orig_chip(tmp, 4, 60, text, col, glyph, 999, size)  # the unpatched chip (no recursion)
                sp = tmp.crop(tmp.getbbox())
                _TL[key] = R22.TempLabel(sp, (x + sp.width / 2, y), 0, hold=900, col=col, slap=False, seed=len(text))
            lab = _TL[key]
            lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            lab.draw(img, lay, age)
            bag.append(lay)
            return
        return orig_chip(img, x, y, text, col, glyph, age, size)
    return chip


def with_temp_labels(fn, t):
    bag = []
    s0, c0 = EB.slap, EB.chip
    EB.slap, EB.chip = _templabel_slap(s0, bag), _templabel_chip(c0, bag)
    try:
        img = fn(t)
    finally:
        EB.slap, EB.chip = s0, c0
    for lay in bag:
        img = EB.emit(img, lay, 0.35)
    return img


# ================================================================== CORRUPTED apply v4
B_SLOT = R20.B_SLOT


def corrupt_apply_v4(t):
    st = R21.STREAM
    bars0, badge0, front0, chip0 = R20.draw_bars, R20.badge, R20.front_x, EB.chip
    R20.draw_bars = lambda *a, **k: None
    R20.badge = lambda *a, **k: None
    R20.front_x = lambda bars, tt, a_, b_: (-500, 0, 0)  # hides round 21's white wipe line

    def chip(img, x, y, text, *a, **k):
        if text.startswith("CORRUPTED"):
            return
        return chip0(img, x, y, text, *a, **k)

    EB.chip = chip
    try:
        img = R21.corrupt_apply_v2(t)
    finally:
        R20.draw_bars, R20.badge, R20.front_x, EB.chip = bars0, badge0, front0, chip0
    st = R21.STREAM
    t_hit = int(min(c["rel"] + 40 + c["tr"] for c in st.cells)) + 60
    if t >= t_hit:
        x0, x1 = wedge_xrange(BC, BR, B_SLOT)
        fr = lerp(x0, x1, seg(t, t_hit, t_hit + 320))  # the overlay takes the slice left to right as the bits land
        spike = 1.0 - seg(t, t_hit, t_hit + 500)
        img = glitch(img, BC, BR, B_SLOT, t, seed=7, k=1.0, front=fr if t < t_hit + 330 else None, side="left", spike=spike)
    return img


# ================================================================== CORRUPTED tick v3
C_SLOT = R20.C_SLOT
TX0, TX1 = wedge_xrange(PC, PR, C_SLOT)
HP_END = EB.arc_seg_poly("player", 19, R20.MP)[1]


def tick_bits():
    rng = np.random.default_rng(55)
    items = []
    poly = wedge(PC, PR * 0.4, PR * 0.96, C_SLOT[0] + 3, C_SLOT[1] - 3, 20)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon(poly, fill=255)
    ma = np.asarray(m)
    mid = pt(PC, PR * 1.42, 118)
    for y in range(int(PC[1] - PR), int(PC[1]), 24):
        for x in range(int(TX0), int(TX1), 22):
            if 0 <= y < H and 0 <= x < W and ma[y, x] > 0:
                tr = 300 + 340 * (x - TX0) / (TX1 - TX0)
                items.append(dict(s=(x, y), c=(mid[0] + rng.normal(0, 40), mid[1] + rng.normal(0, 40)),
                                  e=(HP_END[0] + rng.normal(0, 8), HP_END[1] + rng.normal(0, 6)), t=tr, tr=rng.uniform(420, 600),
                                  col=(255, 41, 158) if rng.random() < 0.6 else (46, 255, 128)))
    return items


class ColBits(R20.Bits):
    def draw(self, layer, t, col=None):
        """Same flight as R20.Bits, but each bit keeps its own pink or green colour."""
        for q in self.p:
            a = t - q["t"]
            if a < 0:
                continue
            from fxlib import bez
            if a < q["hold"]:
                FX.paste_c(layer, FX.glyph(q["ch"], q["px"], q["col"], core=1.0, rim=0.9), q["s"][0], q["s"][1])
                continue
            u = (a - q["hold"]) / q["tr"]
            if u >= 1:
                continue
            p = bez(q["s"], q["c"], q["e"], u ** 1.5)
            FX.paste_c(layer, FX.glyph(q["ch"], lerp(q["px"], q["px"] * 0.6, u), q["col"], core=max(0, 1 - a / 120), rim=0.9), p[0], p[1],
                       alpha=1 - seg(u, 0.8, 1))


TB = ColBits(tick_bits(), CORRUPT, px=(17, 22), seed=56)
T_REFORM = (1500, 1800)


def corrupt_tick_v3(t):
    hit = t >= 1000
    img = R20.scene2(p_state=(38, 0) if hit else (41, 0))
    R20.dress(img, hp_p=38 if t >= 1150 else 41, ram=4 if t >= 900 else 5)
    # standing glitch -> resolve spike (300-460) -> wipes L->R into bits (300-640) -> re-forms L->R (1500-1800)
    if t < 300:
        img = glitch(img, PC, PR, C_SLOT, t, seed=3)
    elif t < 700:
        fr = lerp(TX0, TX1, seg(t, 300, 640))
        img = glitch(img, PC, PR, C_SLOT, t, seed=3, front=fr, side="right", spike=1.0 - seg(t, 300, 460))
    elif t >= T_REFORM[0]:
        fr = lerp(TX0, TX1, seg(t, *T_REFORM))
        img = glitch(img, PC, PR, C_SLOT, t, seed=3, front=fr if t < T_REFORM[1] else None, side="left")
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    if 300 <= t < 380:
        d.polygon(wedge(PC, PR * 0.38, PR * 0.98, *C_SLOT), fill=(255, 255, 255, int(150 * (1 - (t - 300) / 80))))
    TB.draw(fx, t)
    if 960 <= t < 1100:
        poly, c = EB.arc_seg_poly("player", 19, R20.MP)
        d.polygon(poly, fill=(255, 255, 255, int(230 * (1 - (t - 960) / 140))))
    DS.tracer(fx, pt(PC, PR * 0.7, 60), (PC[0] + 380, 760), EB.RAM_PIP, seg(t, 600, 880), CORRUPT, width=5)
    EB.RB.draw(fx, t - 880)
    img = EB.emit(img, fx, 0.45)
    pb, eb, _, _ = P.hp_boxes()
    a = pt(PC, PR * 1.3, 100)
    DS.number_pop(img, "-3", CORRUPT, (a[0] + 20, a[1]), ((pb[0] + pb[2]) / 2, (pb[1] + pb[3]) / 2), t - 640, 420, size=60)
    EB.chip(img, EB.RAM_PIP[0] + 40, EB.RAM_PIP[1] - 70, "-1 RAM", CORRUPT, None, t - 900, size=24)
    return img


# ================================================================== run
SINGLE = {
    "corrupt_apply_v4": (corrupt_apply_v4, 2400, DS.GIF_CROP, (960, 540), False),
    "corrupt_tick_v3": (corrupt_tick_v3, 2200, (40, 120, 920, 1080), (642, 700), True),
    "evade_v4": (R21.evade_v3, 2700, (0, 0, 1920, 1080), (960, 540), True),
    "respin_v2": (R20.respin, 3500, DS.GIF_CROP, (960, 540), True),
    "phase_change_v3": (R21.phase_change_v2, 3400, (900, 0, 1920, 1000), (612, 600), True),
    "enemy_defeated_v2": (EB.defeated, 3300, (1040, 40, 1840, 1000), (600, 720), True),
}


def frame(name, t):
    fn, T, crop, size, temp = SINGLE[name]
    return with_temp_labels(fn, t) if temp else fn(t)


def run(name):
    fn, T, crop, size, temp = SINGLE[name]
    _TL.clear()
    frames, durs = [], []
    for t in range(0, T, int(FX.DT)):
        frames.append(frame(name, t).convert("RGB"))
        durs.append(int(FX.DT))
    R20.gifout("fx_%s.gif" % name, frames, durs, crop, size)


BOARD = [
    ("corrupt_apply_v4", 200, "APPLY  CARD SLAPS", BC, ["CORRUPT PACKET slaps on the boss wheel", "(squash, shadow snap)."]),
    ("corrupt_apply_v4", 700, "APPLY  DISSOLVE A", BC, ["The card decodes into pink 0/1 that", "swirl into the slice under the needle."]),
    ("corrupt_apply_v4", 1180, "APPLY  OVERLAY TAKES", BC, ["As bits land the glitch takes the slice", "left to right (tears doubled 500 ms)."]),
    ("corrupt_apply_v4", 2000, "APPLY  RESULT", BC, ["Only the CORRUPTED glitch overlay:", "no badge, no rule chip."]),
    ("corrupt_tick_v3", 160, "TICK  STANDING", PC, ["Locked full-slice glitch: tears, pink/", "green split, bands, sweeping tear line."]),
    ("corrupt_tick_v3", 480, "TICK  RESOLVE + WIPE", PC, ["Flash, tears spike; the glitch wipes L->R", "into pink/green bits."]),
    ("corrupt_tick_v3", 960, "TICK  -3 HP, -1 RAM", PC, ["Bits run round the rim to HP; bolt", "cracks a RAM pip (chip is temporary)."]),
    ("corrupt_tick_v3", 1700, "TICK  RE-FORMS", PC, ["The status persists: the glitch writes", "back on L->R."]),
]


def board():
    cells = []
    for name, t, lab, c, caps in BOARD:
        _TL.clear()
        img = frame(name, t).convert("RGB")
        w, h = 760, 640
        x0 = int(min(max(0, c[0] - w / 2), 1920 - w))
        y0 = int(min(max(0, c[1] - h / 2), 1080 - h))
        cells.append((img.crop((x0, y0, x0 + w, y0 + h)).resize((475, 400), Image.LANCZOS), lab, "%d ms" % t, caps))
    FX.storyboard(cells, os.path.join(OUT, "fx_corrupted_storyboard.png"),
                  "CORRUPTED  -  apply v4 (from the card play) and tick v3 (locked glitch overlay)",
                  "Crops of the 1920x1080 D4 screen at 0.625. The slice carries ONLY the round 14/15 CORRUPTED glitch overlay; no badge, no tooltip.",
                  cols=4)
    print("board", flush=True)


# ================================================================== respin v3: RESPIN word (temporary), UNDO greys + lock
def undo_box():
    from slicelib import f_ui, f_mono
    f = f_ui(19, b"Bold SemiCondensed")
    tw = max(f.getlength("RESPIN"), f_mono(12).getlength("4 RAM  [R]")) + 28
    bx = 1370 + tw + 12
    tw2 = max(f.getlength("UNDO"), f_mono(12).getlength("[Z]")) + 28
    return (bx, 1006, bx + tw2, 1058)


def undo_locked(img, k):
    """Subtle: the UNDO button greys out and a small lock tick appears on its corner (no word)."""
    if k <= 0:
        return img
    from slicelib import f_ui, f_mono
    x0, y0, x1, y1 = undo_box()
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    a = int(255 * k)
    d.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=(22, 21, 28, a), outline=(80, 78, 92, a), width=2)
    d.text((x0 + 14, y0 + 5), "UNDO", font=f_ui(19, b"Bold SemiCondensed"), fill=(110, 108, 120, a))
    d.text((x0 + 14, y0 + 31), "[Z]", font=f_mono(12), fill=(90, 88, 100, a))
    cx, cy = x1 - 4, y0 + 2
    d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=(14, 13, 20, a), outline=(170, 168, 180, a), width=2)
    d.arc([cx - 4, cy - 8, cx + 4, cy], 180, 360, fill=(200, 198, 210, a), width=2)
    d.rectangle([cx - 5, cy - 3, cx + 5, cy + 5], fill=(200, 198, 210, a))
    img = img.copy()
    img.alpha_composite(lay)
    return img


def respin_v3(t):
    if not getattr(R20, "_R23_RESPIN", False):
        R20.CHECK = EB.vinyl_word("RESPIN", (240, 240, 236), size=40, tilt=-4)
        R20._R23_RESPIN = True
    img = R20.respin(t)
    return undo_locked(img, seg(t, R20.T_RS[1] + 60, R20.T_RS[1] + 260))


SINGLE["respin_v3"] = (respin_v3, 3500, (0, 0, 1920, 1080), (960, 540), True)  # full frame: the UNDO button is in view


if __name__ == "__main__":
    args = sys.argv[1:] or list(SINGLE) + ["board"]
    if args[0] == "test":
        name = args[1]
        for a in args[2:]:
            frame(name, int(a)).convert("RGB").save(os.path.join(P.SCR, "t_%s_%s.png" % (name, a)))
            print("test", name, a, flush=True)
        sys.exit()
    for a in args:
        if a in SINGLE:
            run(a)
        elif a == "board":
            board()
