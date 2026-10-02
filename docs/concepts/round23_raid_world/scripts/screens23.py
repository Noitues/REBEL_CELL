"""Round 23 raid world: slow / freeze field v3 (ground layer, under the units) and Rigger field repair v3 (the node
diamond's locked health fill rises south -> north; hovered = the diegetic number counts up).

python screens23.py [slow] [repair] [contact]
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as LY  # noqa: E402
import finish19 as FN  # noqa: E402
import ui19 as U  # noqa: E402
import roof20 as RF  # noqa: E402
import screens20 as S20  # noqa: E402
import screens21 as S21  # noqa: E402
import screens22 as S22  # noqa: E402
import netdecal21 as N21  # noqa: E402  (the raid UI's locked health read, copied from round22_raid_ui)

OUT = os.path.dirname(HERE)
S20.OUT = S21.OUT = S22.OUT = OUT
S21.BCAM = "S_bonus_nh"
import types  # noqa: E402
FN.ND = types.SimpleNamespace(Net=N21.Net)   # finish19 builds its decal Net from this: every frame gets health_pad()
SL = U.SL
W, H = LY.W, LY.H
to_pil, to_f, P = S20.to_pil, S20.to_f, S20.P
Fx, PS, save_gif = S21.Fx, S21.PS, S21.save_gif
TAG = "S_bonus_nh"

_ground = {}


def ground_mask():
    """1 where the pixel is street / sidewalk (z < 0.45 m): the field is a ground decal, units and buildings occlude it."""
    if "m" not in _ground:
        Pp = FN.passes(TAG)
        z = Pp.pos[..., 2]
        m = ((z < 0.45) & (z > -0.5)).astype(np.float32)
        im = Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        _ground["m"] = np.asarray(im, np.float32) / 255.0
        FN.LY.CAM.update(FN.CAM_DEFAULT)
    return _ground["m"]


# ------------------------------------------------------------------ 1. slow / freeze v3: under the units
def fx_slow_v3(t, lev):
    cls = "ghost"
    img = S21.bonus_base(cls, heat=False)
    img = S21.with_beacon(img, cls, t)
    cx, cy, R = 10, -120, 30
    freeze = lev and 0.42 <= t < 0.9
    fz = 0.0 if not freeze else min(1.0, (t - 0.42) / 0.22)
    fx = Fx()
    S22.dashed_ground_ring(fx, cx, cy, R, S22.ICE_W if freeze else S22.SLOW_BLUE, phase=t * 0.6, width=5, k=1.4)
    if not freeze or fz < 1:
        for k in range(3):
            q = (t * 0.7 + k / 3) % 1.0
            S22.dashed_ground_ring(fx, cx, cy, R * (1 - 0.75 * q), S22.SLOW_BLUE, n=int(34 * (1 - 0.6 * q)), phase=-t, width=3,
                                   k=0.9 * (1 - q) * (1 - fz))
    if freeze:
        fx.poly(S21.ground_poly(cx, cy, R), S22.ICE_B, k=0.12 * fz)
        rng = np.random.default_rng(7)
        for i in range(46):
            a = 2 * math.pi * i / 46 + rng.uniform(-0.03, 0.03)
            L = R * rng.uniform(0.18, 0.42) * fz
            wd = rng.uniform(0.05, 0.09)
            b0 = (cx + R * math.cos(a - wd), cy + R * math.sin(a - wd))
            b1 = (cx + R * math.cos(a + wd), cy + R * math.sin(a + wd))
            tip = (cx + (R - L) * math.cos(a), cy + (R - L) * math.sin(a))
            fx.poly([PS(*b0), PS(*tip), PS(*b1)], S22.ICE_B, k=0.45)
            fx.line([PS(*b0), PS(*tip), PS(*b1)], S22.ICE_W, 2, 0.8)
    # ground layer: only where the street is visible, so the units (and buildings) stay on top
    g = ground_mask()
    fx.add *= g[..., None]
    out = fx.comp(img, glow=0.35)
    tx, ty = S21.threat_px(0)
    fx2 = Fx()
    if freeze and fz > 0.6:                     # the frozen unit itself gets the ice skin (on the unit, on purpose)
        reg = out[int(ty) - 50:int(ty) + 30, int(tx) - 60:int(tx) + 60]
        unit = 1 - g[int(ty) - 50:int(ty) + 30, int(tx) - 60:int(tx) + 60][..., None]
        reg[:] = reg * (1 - 0.5 * unit) + unit * (reg.mean(axis=2, keepdims=True) * 0.5 + 0.38) * (np.array(S22.ICE_B, np.float32) / 255) * 0.6
        gm = np.asarray(Image.open(os.path.join(U.GLYPHS, "state_frozen.png")).split()[3].resize((50, 50)), np.float32) / 255
        fx2.add[int(ty) - 104:int(ty) - 54, int(tx) - 25:int(tx) + 25] += gm[..., None] * np.array(S22.ICE_W, np.float32) / 255 * 1.3
        fx2.text(tx, ty + 56, "FROZEN 1 STEP", 24, (200, 240, 255))
    else:
        fx2.text(tx, ty + 56, "SLOWED  -1 STEP", 22, S22.SLOW_BLUE)
    return fx2.comp(out)


# ------------------------------------------------------------------ 2. repair v3: the locked health fill rises
HP = {"safe": (0.3, 20), "core": (0.45, 50)}


def health_number(img, key, now, mx, col, alpha=1.0):
    """The raid UI's hover number (round 21 ui20.health_float): numeral + 10-segment holo bar above the north point."""
    x, y = PS(*LY.NODES[key][:2])
    y -= 64
    im = to_pil(img).convert("RGBA")
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.line([(x, y + 18), (x, y + 44)], fill=col + (int(120 * alpha),), width=1)
    d.text((x, y), "%d/%d" % (now, mx), font=U.F(SL.ANTON, 30), fill=col + (int(255 * alpha),), anchor="mm",
           stroke_width=1, stroke_fill=(10, 20, 10, int(200 * alpha)))
    for i in range(10):
        on = i < round(now / mx * 10)
        xa = x - 34 + i * 7
        d.rectangle([xa, y + 16, xa + 5, y + 21], fill=col + ((int(230 * alpha),) if on else (int(50 * alpha),)))
    im.alpha_composite(lay)
    return to_f(im)


def hp_col(frac):
    return (212, 255, 0) if frac > 0.66 else (255, 196, 40) if frac > 0.33 else (255, 128, 112)


def fx_repair_v3(t, lev, hover=False):
    cls, col = "rigger", RF.CLASS_RGB["rigger"]
    u = min(1.0, max(0.0, (t - 0.1) / 0.62))
    u = u * u * (3 - 2 * u)
    hs = {"safe": HP["safe"][0] + (1 - HP["safe"][0]) * u}
    if lev:
        hs["core"] = HP["core"][0] + (1 - HP["core"][0]) * u

    def extra(net):
        for (corp, ui, x, y, a, up, hp) in LY.THREATS_BONUS:
            net.threat_ring(x, y, hp=hp, state="down")
        for k, h in hs.items():
            net.health_pad(k, "home" if k == "core" else "holds", health=h, t=t)
    shares = [("safe", "core", cls)] if lev else []
    dec = S20.world_decor("B", slot="stationed", cls=cls, t=0.3, boosts=[("safe", cls)], shares=shares, routes=("r3",),
                          skip=tuple(hs), extra=extra)
    img = FN.finish(TAG, "night", decorate=dec, seed=1, tilt=0.0, rain=False, fog=0.0)
    img = S21.with_beacon(img, cls, t)
    fx = Fx()
    active = 0.08 <= t < 0.8
    for k in hs:                                  # the liked field-repair effect: '+' marks and streaks rising, sparks
        sx, sy = PS(*LY.NODES[k][:2])
        a0 = 1.0 if active else 0.15
        for i in range(7):
            q = (t * 1.6 + i / 7) % 1.0
            x = sx - 40 + (i * 37) % 80
            y = sy - 10 - 150 * q
            fx.line([(x - 7, y), (x + 7, y)], col, 4, 1.3 * (1 - q) * a0)
            fx.line([(x, y - 7), (x, y + 7)], col, 4, 1.3 * (1 - q) * a0)
        for i in range(5):
            q = (t * 2.2 + i / 5) % 1.0
            x = sx - 30 + i * 15
            fx.line([(x, sy - 20 - 120 * q), (x, sy - 50 - 120 * q)], (190, 255, 190), 2, 0.9 * (1 - q) * a0)
        for i in range(8):                        # green sparks spiral into the socket
            q = (t * 2 + i / 8) % 1.0
            a = 2 * math.pi * (q + i / 8)
            fx.disc(sx + 50 * (1 - q) * math.cos(a), sy + 22 * (1 - q) * math.sin(a), 4, col, 1.3 * (1 - q) * a0)
    fx.text(560 if lev else 990, 600 if lev else 700, "WAVE 1 CLEARED", 36 if lev else 30, (235, 240, 250))
    out = fx.comp(img)
    if hover:                                     # hovered node: the diegetic number counts up with the fill
        h = hs["safe"]
        out = health_number(out, "safe", int(round(h * HP["safe"][1])), HP["safe"][1], hp_col(h))
        sx, sy = PS(*LY.NODES["safe"][:2])
        cur = to_pil(out).convert("RGBA")
        p = (sx + 40, sy + 30)
        ImageDraw.Draw(cur).polygon([p, (p[0] + 7, p[1] + 30), (p[0] + 14, p[1] + 21), (p[0] + 28, p[1] + 20)], fill=(246, 243, 236, 255),
                                    outline=(14, 12, 20, 255))
        out = to_f(cur)
    return out


CROPS = {"slow": (113, 360, 1393, 1080), "repair": (392, 648, 1112, 1053), "repair_lev": (60, 400, 1180, 1030)}


def panel(fn, t, lev, head, key, **kw):
    pil = to_pil(fn(t, lev, **kw)).crop(CROPS.get(key + ("_lev" if lev else ""), CROPS[key])).resize((S21.PW, S21.PH), Image.LANCZOS)
    d = ImageDraw.Draw(pil)
    d.rectangle([0, 0, 300, 26], fill=(5, 13, 28))
    d.text((8, 13), head, font=U.F(SL.MONO, 15), fill=(92, 225, 255) if not lev else (255, 222, 30), anchor="lm")
    return pil


def gif(key, nm, who, fn, b_txt, l_txt, lhead, rhead, rkw=None, lkw=None, n=18):
    PW, PH = S21.PW, S21.PH
    GW, GH = 2 * PW + 30, PH + 112
    base = Image.new("RGB", (GW, GH), (8, 7, 14))
    d = ImageDraw.Draw(base)
    d.text((10, 8), "PROPOSAL  //  " + nm, font=U.F(SL.ANTON, 26), fill=(255, 222, 30))
    d.text((10 + U.F(SL.ANTON, 26).getlength("PROPOSAL  //  " + nm) + 20, 22), who, font=U.F(SL.MONO, 15), fill=(92, 225, 255))
    d.text((10, 52 + PH + 8), b_txt, font=U.F(SL.MONO, 13), fill=(190, 225, 240))
    d.text((20 + PW, 52 + PH + 8), l_txt, font=U.F(SL.MONO, 13), fill=(255, 222, 30))
    frames = []
    for f in range(n):
        im = base.copy()
        im.paste(panel(fn, f / n, False, lhead, key, **(lkw or {})), (10, 50))
        im.paste(panel(fn, f / n, True, rhead, key, **(rkw or {})), (20 + PW, 50))
        frames.append(im)
        print(key, f, flush=True)
    return save_gif(frames, "bonus_%s_v3.gif" % key, [100] * n)


def contact():
    from PIL import ImageSequence
    names = ["bonus_slow_v3.gif", "bonus_repair_v3.gif"]
    sheet = Image.new("RGB", (2 * 960 + 30, 640), (10, 9, 16))
    d = ImageDraw.Draw(sheet)
    d.text((14, 12), "ROUND 23  RAID WORLD: SLOW FIELD UNDER THE UNITS, REPAIR = THE HEALTH FILL RISES", font=U.F(SL.ANTON, 28), fill=(255, 222, 30))
    for i, nme in enumerate(names):
        fr = [f.convert("RGB") for f in ImageSequence.Iterator(Image.open(os.path.join(OUT, nme)))]
        im = fr[len(fr) * 2 // 3]
        k = 960 / im.size[0]
        im = im.resize((960, int(im.size[1] * k)), Image.LANCZOS)
        sheet.paste(im, (10 + i * 970, 60))
        d.text((14 + i * 970, 60 + im.size[1] + 6), nme, font=U.F(SL.MONO, 15), fill=(92, 225, 255))
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=86)
    print("saved contact_sheet.jpg")


if __name__ == "__main__":
    which = sys.argv[1:] or ["slow", "repair", "contact"]
    if "slow" in which:
        gif("slow", "B  SLOW FIELD v3", "GHOST  (GDD: entering threats delayed 1 step)", fx_slow_v3,
            "a ground decal UNDER the units: slow blue dashed rings drift inward",
            "freeze: ice crystals grow inward on the street; the frozen unit is iced over", "BASE", "LEVELLED UP")
    if "repair" in which:
        gif("repair", "E  FIELD REPAIR v3", "RIGGER  (GDD: node regains integrity after each wave)", fx_repair_v3,
            "the socket's health fill rises south -> north; hovered: the number counts up",
            "adjacent node (CORE) refills too", "BASE  (hovered)", "LEVELLED UP", lkw=dict(hover=True))
    if "contact" in which:
        contact()
