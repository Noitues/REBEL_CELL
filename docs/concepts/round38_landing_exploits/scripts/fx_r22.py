"""Round 22: drone destroyed v3, Heat v4, SEND IT sticker, apply CORRUPTED v3 (temporary labels).

RULES (kept from round 21 + new):
- any effect caused by a card stems from the card play (slap -> dissolve A -> bits from the slap point);
- labels / word stickers are TEMPORARY: they slap on, hold briefly, then dissolve into 0/1 bits. Nothing
  persists on a slice except its status overlay + corner badge (the locked state-overlay system).

python fx_r22.py [drone_destroyed_v3 corrupt_apply_v3 heat send_it]
python fx_r22.py test <name> <t> ...
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
import fx_r21 as R21
import heat_alts as HA
import sticker_lib19 as SL
from fxlib import seg, lerp, lerp2, bez, ease_out_cubic, ease_in_cubic, ease_in_out, ease_out_back
from slicelib import f_num, f_ui, bloom

OUT = P.OUT
W, H = 1920, 1080
PC, BC = P.PLAYER["c"], P.BOSS["c"]
PR, BR = P.PLAYER["r"], P.BOSS["r"]
pt, wedge = EB.pt, EB.wedge
CORRUPT, ORANGE = EB.CORRUPT, EB.ORANGE
FILL_PINK = ("grad", (255, 96, 172), (222, 18, 112))
FILL_GREY = ("grad", (150, 146, 156), (104, 100, 112))


# ================================================================== SEND IT sticker (raid START DEFENSE format)
_ST = {}
SEND_C = (1700, 990)


def send_sticker(state="idle"):
    key = state
    if key not in _ST:
        fills = [FILL_GREY] if state == "disabled" else [FILL_PINK]
        art = SL.lettering(["SEND IT"], 74, fills, key_w=6, extrude=9, seed=21, jitter=4.0, track=1, holo_seed=61)
        gk = 1.0 if state == "hover" else 0.22
        curl = dict(corner="tr", amount=0.12) if state == "hover" else None
        sd = SL.build_sticker(art, border=15, material="gloss", seed=21, close=15 * 1.25, gloss_k=gk, curl=curl)
        if state == "disabled":
            im = sd["img"]
            g = im.convert("LA").convert("RGBA")
            g.putalpha(im.split()[3])
            sd = dict(sd, img=g)
        _ST[key] = sd
    return _ST[key]


def execute_word(img, c, state):
    """The washed-out system word the marker/sticker is slapped over (overlay rule: verbs over system words)."""
    f = P.mono(96)
    txt = "EXECUTE"
    tw = f.getlength(txt)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x, y = c[0] - tw / 2 - 20, c[1] - 112
    a = 120 if state != "disabled" else 80
    d.rectangle([x - 16, y - 2, x + tw + 16, y + 112], fill=(20, 40, 50, int(a * 0.6)), outline=(150, 210, 230, a), width=2)
    d.text((x, y), txt, font=f, fill=(170, 220, 236, a + 30))
    d.text((x + 2, y + 112 + 4), "> turn_resolve.exe  [SPACE]", font=P.mono(16), fill=(170, 220, 236, a))
    for yy in range(int(y - 2), int(y + 112), 3):  # scanlines wash it out
        d.line([(x - 16, yy), (x + tw + 16, yy)], fill=(0, 0, 0, 70))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.6)))


def draw_send_it(img, state="idle"):
    execute_word(img, SEND_C, state)
    sd = send_sticker(state)
    kw = dict(angle=-3)
    if state == "hover":
        kw.update(scale=1.05, hover=0.6)
    elif state == "pressed":
        kw.update(scale=0.97, squash=(1.04, 0.9), hover=0.0, shadow=0.6)
    elif state == "disabled":
        kw.update(opacity=0.8, shadow=0.5)
    out = SL.place(img, sd, SEND_C[0], SEND_C[1], **kw)
    if state == "disabled":
        d = ImageDraw.Draw(out)
        f = f_ui(18, b"Bold Condensed")
        s = "RESOLVING..."
        d.rounded_rectangle([SEND_C[0] - 70, SEND_C[1] + 52, SEND_C[0] + 70, SEND_C[1] + 78], radius=6, fill=(10, 9, 15, 235))
        d.text((SEND_C[0] - f.getlength(s) / 2, SEND_C[1] + 54), s, font=f, fill=(170, 170, 185, 255))
    if state == "hover":
        FX.cursor(out, SEND_C[0] + 60, SEND_C[1] + 10)
    if state == "pressed":
        FX.cursor(out, SEND_C[0] + 60, SEND_C[1] + 12, True)
    return out


def stickers_r22(img):
    """plates.stickers with the round 22 SEND IT (CELL-9 name plate unchanged)."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    body = Image.new("RGBA", (330, 62), (0, 0, 0, 0))
    db = ImageDraw.Draw(body)
    db.rounded_rectangle([0, 0, 329, 61], radius=12, fill=MC.PINK + (255,))
    db.text((18, 6), "CELL-9 // BREAKER", font=f_num(40), fill=MC.INK + (255,))
    st = MC.vinyl(body, border=7, tilt=4)
    ov.alpha_composite(st, (PC[0] - PR - 200, PC[1] + int(PR * 0.98)))
    img.alpha_composite(ov)
    img.paste(draw_send_it(img.copy(), "idle"), (0, 0))


P.stickers = stickers_r22  # every round 22 frame uses the restyled SEND IT


def send_it():
    states = ["idle", "hover", "pressed", "disabled"]
    base = R20.scene2()
    R20.dress(base)
    full = base.copy()
    cw, ch = 620, 340
    gap = 16
    S = Image.new("RGB", (2 * cw + 3 * gap + 960 + gap, 2 * (ch + gap) + 170), (14, 13, 20))
    d = ImageDraw.Draw(S)
    d.text((gap, 10), "SEND IT  -  vinyl sticker over the washed-out EXECUTE", font=f_num(44), fill=(255, 255, 255))
    S.paste(full.convert("RGB").resize((960, 540), Image.LANCZOS), (gap, 70))
    d.text((gap, 70 + 546), "combat screen, idle", font=P.mono(18), fill=(190, 190, 205))
    for k, stt in enumerate(states):
        b = R20.scene2()
        R20.dress(b)  # dress already draws idle; redraw the button area in this state
        clean = R20.scene2()
        # restore the area under the button, then draw the state
        box = (SEND_C[0] - 330, SEND_C[1] - 150, 1920, 1080)
        P.hud(clean, next_p=False, next_e=False)
        EB.hand(clean)
        b.paste(clean.crop(box), box[:2])
        b = draw_send_it(b, stt)
        crop = b.convert("RGB").crop((1300, 780, 1920, 1080)).resize((cw, cw * 300 // 620))
        x = gap + 960 + gap + (k % 2) * (cw + gap)
        y = 70 + (k // 2) * (ch + gap)
        S.paste(crop, (x, y))
        d.text((x, y + crop.height + 4), stt.upper(), font=f_num(24), fill=(255, 214, 64))
    notes = ["Same toolkit as the raid START DEFENSE sticker (sticker_lib19: Anton keyline lettering, pink gradient, extrude, white die-cut,",
             "gloss 0.22 at rest). HOVER: lift 0.6 + x1.05, corner curl 0.12, full gloss sweep. PRESSED: squash 1.04/0.90, shadow snaps in.",
             "DISABLED (while resolving): greyscale vinyl, 80 %, RESOLVING chip. EXECUTE = the system word underneath, mono, scanlined, 30 % alpha."]
    for i, ln in enumerate(notes):
        d.text((gap, 70 + 2 * (ch + gap) + 10 + i * 26), ln, font=P.mono(18), fill=(200, 200, 214))
    S.save(os.path.join(OUT, "send_it_sticker.png"), optimize=True)
    print("send_it_sticker.png", flush=True)


# ================================================================== temporary labels -> binary dissolve
class TempLabel:
    """A label sprite that pops in, holds, then dissolves left to right into 0/1 bits that drift up and fade."""

    def __init__(self, sprite, c, t0, hold=700, col=(255, 255, 255), cell=10, seed=3, slap=True):
        self.s, self.c, self.t0, self.hold, self.col, self.cell, self.slap = sprite, c, t0, hold, col, cell, slap
        rng = np.random.default_rng(seed)
        a = np.asarray(sprite.split()[3])
        h, w = a.shape
        self.cells = []
        for y in range(0, h, cell):
            for x in range(0, w, cell):
                if a[y:y + cell, x:x + cell].mean() > 70:
                    blk = np.asarray(sprite)[y:y + cell, x:x + cell]
                    m = blk[..., 3] > 60
                    cc = tuple(int(v) for v in blk[..., :3][m].mean(axis=0)) if m.any() else col
                    if min(cc) > 200:
                        cc = col
                    self.cells.append(dict(x=x, y=y, d=x / max(1, w) * 220 + rng.uniform(0, 60), vx=rng.normal(0, 30), vy=-rng.uniform(60, 140),
                                           ch="01"[int(rng.random() < 0.5)], col=cc))
        self.w, self.h = w, h

    def draw(self, img, fx, t):
        a = t - self.t0
        if a < 0:
            return
        t_d = self.hold
        if a < t_d:
            if self.slap:
                EB.slap(img, self.s, self.c, a, 160)
            else:
                k = ease_out_back(seg(a, 0, 140), 2.0)
                FX.paste_c(img, self.s, self.c[0], self.c[1], scale=max(0.05, k))
            return
        b = a - t_d
        m = np.asarray(self.s.split()[3]).copy()
        x0, y0 = self.c[0] - self.w / 2, self.c[1] - self.h / 2
        any_left = False
        for q in self.cells:
            u = b - q["d"]
            if u < 0:
                any_left = True
                continue
            m[q["y"]:q["y"] + self.cell, q["x"]:q["x"] + self.cell] = 0
            if u < 520:
                s = u / 1000
                px = x0 + q["x"] + self.cell / 2 + q["vx"] * s
                py = y0 + q["y"] + self.cell / 2 + q["vy"] * s
                FX.paste_c(fx, FX.glyph(q["ch"], 15, q["col"], core=max(0, 1 - u / 80), rim=0.8), px, py, alpha=1 - seg(u, 300, 520))
        if any_left:
            sp = self.s.copy()
            sp.putalpha(Image.fromarray(m))
            FX.paste_c(img, sp, self.c[0], self.c[1])


def chip_sprite(text, col, glyph=None, size=22):
    tmp = Image.new("RGBA", (900, 120), (0, 0, 0, 0))
    EB.chip(tmp, 4, 60, text, col, glyph, 999, size=size)
    return tmp.crop(tmp.getbbox())


# ================================================================== apply CORRUPTED v3
def flat_badge(img, c, k=1.0, size=22):
    """The locked state-overlay corner badge: printed on the slice (no vinyl margin, no drop shadow)."""
    if k <= 0.01:
        return
    s = size * k
    d = ImageDraw.Draw(img)
    d.polygon([(c[0], c[1] - s), (c[0] + s, c[1]), (c[0], c[1] + s), (c[0] - s, c[1])], fill=(26, 8, 18, 255), outline=CORRUPT + (255,), width=3)
    if k > 0.6:
        g = EB.icon("status_corrupted", int(s * 0.95), CORRUPT, outline=False)
        img.alpha_composite(g, (int(c[0] - g.width / 2), int(c[1] - g.height / 2)))


CA_LABEL = None


def corrupt_apply_v3(t):
    global CA_LABEL
    if CA_LABEL is None:
        CA_LABEL = TempLabel(chip_sprite("CORRUPTED: 3 self-dmg, -1 RAM", CORRUPT, "status_corrupted"), (BC[0] - BR * 1.45, BC[1] - BR * 0.62),
                             0, hold=800, col=CORRUPT, slap=False, seed=5)
    chip0, badge0 = EB.chip, R20.badge
    t_end = None

    def chip(img, x, y, text, *a, **k):  # the rule chip is drawn by TempLabel instead
        if text.startswith("CORRUPTED"):
            return
        return chip0(img, x, y, text, *a, **k)

    holder = {}

    def badge(img, c, size=22, age=None):  # flat, printed badge (no vinyl sticker)
        holder["t"] = age
        flat_badge(img, c, ease_out_back(seg(age if age is not None else 999, 0, 160), 2.2), size)

    EB.chip, R20.badge = chip, badge
    try:
        img = R21.corrupt_apply_v2(t)
    finally:
        EB.chip, R20.badge = chip0, badge0
    if "t" in holder and holder["t"] is not None:
        t0 = t - holder["t"] + 80
        CA_LABEL.t0 = t0
        fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
        CA_LABEL.draw(img, fx, t)
        img = EB.emit(img, fx, 0.4)
    return img


# ================================================================== drone destroyed v3 (the drone's own HP reads 0)
def drone_sticker(hp):
    s = 40
    body = Image.new("RGBA", (2 * s + 4, 2 * s + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    d.polygon(EB.hex_poly((s + 2, s + 2), s, 30), fill=(30, 14, 8, 255), outline=ORANGE + (255,))
    d.polygon(EB.hex_poly((s + 2, s + 2), s - 5, 30), outline=ORANGE + (255,))
    g = EB.icon("special_drone", 40, ORANGE)
    body.alpha_composite(g, ((body.width - g.width) // 2, (body.height - g.height) // 2 - 2))
    hot = hp == 0
    d.rounded_rectangle([s - 12, 2 * s - 12, s + 16, 2 * s + 4], radius=4, fill=((90, 10, 20) if hot else (10, 9, 15)) + (255,),
                        outline=((255, 80, 90) if hot else ORANGE) + (255,), width=2)
    d.text((s - 5, 2 * s - 14), str(hp), font=f_num(16), fill=(255, 255, 255, 255))
    return MC.vinyl(body, border=5, shadow=0.55)


SPR = {}


def spr(hp):
    if hp not in SPR:
        SPR[hp] = drone_sticker(hp)
    return SPR[hp]


def drone_destroyed_v3(t):
    chip0, pop0 = EB.chip, DS.number_pop

    def chip(img, x, y, text, *a, **k):
        if text in ("DRONE DESTROYED", "DRONE  HP 0"):
            return
        return chip0(img, x, y, text, *a, **k)

    def pop(*a, **k):
        k.pop("sub", None)
        return pop0(*a, **k)

    # the HP on the drone ticks 5 -> 0 over 150 ms from the impact
    hp = 5
    if t >= R20.T_IMP:
        hp = max(0, 5 - int((t - R20.T_IMP) / 30))
    R20.DRONE_SPR = (spr(hp), PIECES0)  # the sticker shows its live HP; it breaks apart reading 0
    EB.chip, DS.number_pop = chip, pop
    try:
        img = R20.drone_destroyed(t)
    finally:
        EB.chip, DS.number_pop = chip0, pop0
    # flash the HP plate as it hits 0
    if R20.T_IMP <= t < R20.T_IMP + 260 and t < R20.T_POP:
        q = seg(t, R20.T_IMP, R20.T_IMP + 260)
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        c = (R20.DOCK[0] + 2, R20.DOCK[1] + 34)
        ImageDraw.Draw(lay).ellipse([c[0] - 22, c[1] - 16, c[0] + 22, c[1] + 16], fill=(255, 120, 120, int(200 * (1 - q))))
        img = EB.emit(img, lay.filter(ImageFilter.GaussianBlur(5)), 0.6)
    return img


def _pieces_from(sprite):
    w, h = sprite.size
    c = (w / 2, h / 2)
    out = []
    for k in range(6):
        m = Image.new("L", sprite.size, 0)
        a0, a1 = math.radians(k * 60 - 90), math.radians(k * 60 - 30)
        ImageDraw.Draw(m).polygon([c, (c[0] + 90 * math.cos(a0), c[1] + 90 * math.sin(a0)), (c[0] + 90 * math.cos(a1), c[1] + 90 * math.sin(a1))], fill=255)
        piece = sprite.copy()
        piece.putalpha(ImageChops.multiply(sprite.split()[3], m))
        bb = piece.getbbox()
        if bb:
            am = (a0 + a1) / 2
            out.append(dict(im=piece.crop(bb), off=((bb[0] + bb[2]) / 2 - c[0], (bb[1] + bb[3]) / 2 - c[1]), dir=am))
    return out


PIECES0 = _pieces_from(drone_sticker(0))


# ================================================================== Heat v4
TARGET_ALARMS = [(870, 320), (1060, 330)]


def searchlights_away(img, t):
    beams = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    db = ImageDraw.Draw(beams)
    for k, (o, base_tx, ty) in enumerate((((150, 760), 260, -60), ((1800, 700), 1680, -60))):  # rooftops at the screen sides
        sweep = math.sin(t / (1500 + 300 * k) + k * 1.7)
        tx = base_tx + 190 * sweep
        L = math.hypot(tx - o[0], ty - o[1])
        nx, ny = -(ty - o[1]) / L, (tx - o[0]) / L
        wdt = 80
        db.polygon([(o[0] + nx * 6, o[1] + ny * 6), (o[0] - nx * 6, o[1] - ny * 6), (tx - nx * wdt, ty - ny * wdt), (tx + nx * wdt, ty + ny * wdt)],
                   fill=(235, 245, 255, 120))
        db.ellipse([o[0] - 14, o[1] - 8, o[0] + 14, o[1] + 8], fill=(255, 255, 240, 230))
    return HA.additive(img, beams.filter(ImageFilter.GaussianBlur(8)), 1.0)


def target_alarms(img, t):
    old = R21.ALARMS
    R21.ALARMS = TARGET_ALARMS
    try:
        return R21.alarms(img, t + 400)
    finally:
        R21.ALARMS = old


def city_v4(img, t, lvl):
    if lvl == 0:
        return R21.city_v3(img, t, 0)
    if lvl == 2:
        return R21.city_v3(img, t, 2)
    img = searchlights_away(img, t)
    return target_alarms(img, t)


def heat_frame(lvl, t):
    img = HA.world(city_v4, t, lvl)
    HA.ui(img)
    HA.heat_chip(img, lvl)
    return img


DESC = ["3 alarm beacons on side buildings; nothing on the target (r21)",
        "2 searchlights sweeping the sky over side blocks + 2 alarms ON the target",
        "13 police lights + 2 searchlights on the target (r21); no tint"]


def heat():
    frames, durs = [], []
    for lvl in range(3):
        for t in range(0, 1680, 120):
            frames.append(heat_frame(lvl, t + lvl * 5000).convert("RGB").resize((960, 540), Image.LANCZOS))
            durs.append(120)
    durs[-1] = 600
    s = FX.save_gif(frames, durs, os.path.join(OUT, "heat_city_v4.gif"))
    print("heat_city_v4.gif", s // 1024, "KB", flush=True)
    cw, ch, gap = 800, 450, 14
    S = Image.new("RGB", (3 * cw + 4 * gap, ch + 120), (14, 13, 20))
    d = ImageDraw.Draw(S)
    d.text((gap, 10), "HEAT H1 v4  -  CITY REACTS (backdrop only)", font=f_num(44), fill=(255, 255, 255))
    for lvl, (heat_, word, col) in enumerate(HA.LEVELS):
        x = gap + lvl * (cw + gap)
        S.paste(heat_frame(lvl, 600 + lvl * 5000).convert("RGB").resize((cw, ch), Image.LANCZOS), (x, 66))
        d.text((x, 66 + ch + 6), "HEAT %d  %s" % (heat_, word), font=f_num(26), fill=col)
        d.text((x, 66 + ch + 40), DESC[lvl], font=f_ui(18, b"SemiBold"), fill=(200, 200, 214))
    S.save(os.path.join(OUT, "heat_city_v4_strip.png"), optimize=True)
    print("heat strip", flush=True)


# ------------------------------------------------------------------ run
SINGLE = {
    "drone_destroyed_v3": (drone_destroyed_v3, 2000, DS.GIF_CROP, (960, 540)),
    "corrupt_apply_v3": (corrupt_apply_v3, 3000, DS.GIF_CROP, (960, 540)),
}


def run(name):
    fn, T, crop, size = SINGLE[name]
    frames, durs = [], []
    for t in range(0, T, int(FX.DT)):
        frames.append(fn(t).convert("RGB"))
        durs.append(int(FX.DT))
    R20.gifout("fx_%s.gif" % name, frames, durs, crop, size)


if __name__ == "__main__":
    args = sys.argv[1:] or list(SINGLE) + ["heat", "send_it"]
    if args[0] == "test":
        name = args[1]
        for a in args[2:]:
            im = heat_frame(int(a), 600) if name == "heat" else SINGLE[name][0](int(a))
            im.convert("RGB").save(os.path.join(P.SCR, "t_%s_%s.png" % (name, a)))
            print("test", name, a, flush=True)
        sys.exit()
    for a in args:
        if a in SINGLE:
            run(a)
        elif a == "heat":
            heat()
        elif a == "send_it":
            send_it()
