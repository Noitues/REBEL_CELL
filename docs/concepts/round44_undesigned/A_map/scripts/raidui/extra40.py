"""Round 40: the raid-WORLD animations re-run in the one city (same compat district, same locked raid-UI decals).
Ports of round23_raid_world/screens23.py (slow v3, repair v3), round22_raid_world/screens22.py (unit_health) and the
round 19/20/35 Heat spotlights, drawn on setup_h1 through the finish19 adapter (post40).

  28_bonus_slow.gif     slow field under the units (blue dashed rings drift inward); levelled = ice crystals grow
                        inward, the unit is iced over (FROZEN 1 STEP)
  29_bonus_repair.gif   the node's locked health fill rises south -> north; hovered: the number counts up; levelled: the
                        linked CORE refills too; green '+' marks / streaks / sparks
  30_unit_health.gif    the unit's corp-colour disc drains top-down on the street + its v4 icon; status pips ride the
                        dashed corp ring (SLOWED > FROZEN > BURNING + EXPOSED); heading only on hover
  31_spotlights.gif     a chopper circles the Vault, its spot wobbles on the node (EXPOSED ticks); drones with mini spots
python extra40.py [28 29 30 31]
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("NET36", "net_scope.json")
import screens21 as S  # noqa: E402
from screens21 import LY, N, P, U, V, base, deco, gif, seg, ease  # noqa: E402
sys.path.insert(1, os.path.dirname(HERE))
import icons22 as IC  # noqa: E402
import r35ui as R35  # noqa: E402

SLOW = (90, 170, 255)
ICE_W, ICE_B = (225, 248, 255), (150, 215, 255)
RIG = (123, 224, 123)
INK = (10, 8, 16, 255)


def _layer(fr):
    return Image.new("RGBA", (fr.w, fr.h), (0, 0, 0, 0))


def _add(fr, lay, glow=0.8):
    a = np.asarray(lay, np.float32) / 255.0
    rgb, al = a[..., :3], a[..., 3:4]
    img = fr.img * (1 - al) + rgb * al
    if glow:
        b = np.asarray(lay.filter(ImageFilter.GaussianBlur(7)), np.float32) / 255.0
        img = img + b[..., :3] * b[..., 3:4] * glow
    fr.img = np.clip(img, 0, 1)
    return fr


def L(fr, x, y, z=0.0):
    p = P(x, y, z)
    return p[0] - fr.ox, p[1] - fr.oy


def gpoly(fr, cx, cy, R, n=64):
    return [L(fr, cx + R * math.cos(2 * math.pi * k / n), cy + R * math.sin(2 * math.pi * k / n)) for k in range(n)]


def dashed_ring(d, fr, cx, cy, R, col, a=255, width=4, n=40, phase=0.0, gap=0.45):
    for i in range(n):
        a0 = 2 * math.pi * (i + phase) / n
        a1 = 2 * math.pi * (i + phase + 1 - gap) / n
        d.line([L(fr, cx + R * math.cos(a0 + (a1 - a0) * q / 4), cy + R * math.sin(a0 + (a1 - a0) * q / 4)) for q in range(5)],
               fill=col + (int(max(0, min(255, a))),), width=width)


def tag(fr, text, col=(92, 225, 255)):
    lay = _layer(fr)
    d = ImageDraw.Draw(lay)
    w = U.F(U.SL.MONO, 14).getlength(text)
    d.rectangle([10, 10, 26 + w, 36], fill=(5, 13, 28, 230))
    d.text((18, 23), text, font=U.F(U.SL.MONO, 14), fill=col + (255,), anchor="lm")
    return _add(fr, lay, 0)


def hp_col(frac):
    return (212, 255, 0) if frac > 0.66 else (255, 196, 40) if frac > 0.33 else (255, 128, 112)


def bbox(keys, w0=800, h0=450, pad=150):
    xs, ys = zip(*[P(*N[k][:2]) for k in keys])
    w = max(w0, int(max(xs) - min(xs) + 2 * pad))
    h = max(h0, int(max(ys) - min(ys) + 2 * pad))
    w = max(w, int(h * 16 / 9))
    h = int(w * 9 / 16)
    return S.boxc((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2 - 20, w, h)


# ------------------------------------------------------------------ 28 slow / freeze field (Ghost on the Safehouse)
def g28(t, i):
    sx, sy = N["safe"][:2]
    R = 34.0
    route = LY.route_points("r3")
    b = S.boxc(*P(sx, sy - 6), 800, 450)
    lev = t >= 0.5
    u = (t % 0.5) / 0.5
    freeze = lev and u >= 0.3
    fz = 0.0 if not freeze else min(1.0, (u - 0.3) / 0.25)
    um = 0.212 + 0.06 * (u if not freeze else 0.45)                 # slowed: creeps inside the field; frozen: stops
    (x, y), hd = V.path_point(route, um)
    fr = base("setup_h1", deco(forecast={}, rings=[(x, y, 0.8, "live")]), b, None)
    lay = _layer(fr)
    d = ImageDraw.Draw(lay)
    if freeze:
        d.polygon(gpoly(fr, sx, sy, R), fill=ICE_B + (int(40 * fz),))
        rng = np.random.default_rng(7)
        for k in range(46):
            a = 2 * math.pi * k / 46 + rng.uniform(-0.03, 0.03)
            Lk = R * rng.uniform(0.18, 0.42) * fz
            wd = rng.uniform(0.05, 0.09)
            tri = [L(fr, sx + R * math.cos(a - wd), sy + R * math.sin(a - wd)), L(fr, sx + (R - Lk) * math.cos(a), sy + (R - Lk) * math.sin(a)),
                   L(fr, sx + R * math.cos(a + wd), sy + R * math.sin(a + wd))]
            d.polygon(tri, fill=ICE_B + (115,))
            d.line(tri, fill=ICE_W + (205,), width=2)
    dashed_ring(d, fr, sx, sy, R, ICE_W if freeze else SLOW, 255, 5, phase=t * 0.6)
    if fz < 1:
        for k in range(3):
            q = (u * 0.7 + k / 3) % 1.0
            dashed_ring(d, fr, sx, sy, R * (1 - 0.75 * q), SLOW, 230 * (1 - q) * (1 - fz), 3, n=int(34 * (1 - 0.6 * q)) + 4, phase=-u)
    fr = _add(fr, lay, 0.6)                                        # ground layer first: the unit stands on it
    iced = freeze and fz > 0.6
    fr = V.paste_sprite(fr, "INSPECTOR", hd, x, y, tint=(190, 235, 255) if iced else None)
    px, py = L(fr, x, y)
    lay = _layer(fr)
    d = ImageDraw.Draw(lay)
    if iced:
        g = IC.glyph_mask("state_frozen", 40)
        lay.paste(Image.new("RGBA", g.size, ICE_W + (255,)), (int(px - 20), int(py - 96)), g)
    d.text((px, py + 44), "FROZEN 1 STEP" if iced else "SLOWED  -1 STEP", font=U.F(U.SL.ANTON, 22),
           fill=(ICE_W if iced else SLOW) + (255,), anchor="mm", stroke_width=2, stroke_fill=INK)
    fr = _add(fr, lay, 0.3)
    return tag(fr, "GHOST  //  SLOW FIELD" + ("  LEVELLED: FREEZE" if lev else "  BASE"), (255, 222, 30) if lev else (92, 225, 255))


# ------------------------------------------------------------------ 29 field repair (Rigger on the Safehouse)
HP = {"safe": 0.3, "core": 0.45}


def g29(t, i):
    lev = t >= 0.5
    tt = (t % 0.5) / 0.5
    u = ease(seg(tt, 0.1, 0.72))
    hs = {"safe": HP["safe"] + (1 - HP["safe"]) * u}
    if lev:
        hs["core"] = HP["core"] + (1 - HP["core"]) * u
    b = bbox(["safe", "core"]) if lev else S.boxc(*P(N["safe"][0], N["safe"][1] - 4), 800, 450)
    fr = base("setup_h1", deco(forecast={}, health=hs), b, "g29_%d_%d" % (lev, int(u * 40)))
    active = 0.08 <= tt < 0.85
    lay = _layer(fr)
    d = ImageDraw.Draw(lay)
    for k in hs:                                   # the liked field-repair effect: '+' marks, streaks, sparks
        x0, y0 = L(fr, *N[k][:2])
        a0 = 1.0 if active else 0.15
        for j in range(7):
            q = (tt * 1.6 + j / 7) % 1.0
            x = x0 - 40 + (j * 37) % 80
            y = y0 - 10 - 150 * q
            al = int(255 * (1 - q) * a0)
            d.line([(x - 7, y), (x + 7, y)], fill=RIG + (al,), width=4)
            d.line([(x, y - 7), (x, y + 7)], fill=RIG + (al,), width=4)
        for j in range(5):
            q = (tt * 2.2 + j / 5) % 1.0
            x = x0 - 30 + j * 15
            d.line([(x, y0 - 20 - 120 * q), (x, y0 - 50 - 120 * q)], fill=(190, 255, 190, int(220 * (1 - q) * a0)), width=2)
        for j in range(8):
            q = (tt * 2 + j / 8) % 1.0
            a = 2 * math.pi * (q + j / 8)
            xx, yy = x0 + 50 * (1 - q) * math.cos(a), y0 + 22 * (1 - q) * math.sin(a)
            d.ellipse([xx - 4, yy - 4, xx + 4, yy + 4], fill=RIG + (int(255 * (1 - q) * a0),))
    fr = _add(fr, lay, 0.8)
    if not lev:                                    # hovered: the diegetic number counts up with the fill
        h = hs["safe"]
        mx = N["safe"][5][1]
        fr = V.health_float(fr, "safe", int(round(h * mx)), mx, col=hp_col(h))
        x0, y0 = L(fr, *N["safe"][:2])
        lay = _layer(fr)
        p = (x0 + 40, y0 + 30)
        ImageDraw.Draw(lay).polygon([p, (p[0] + 7, p[1] + 30), (p[0] + 14, p[1] + 21), (p[0] + 28, p[1] + 20)], fill=(246, 243, 236, 255), outline=INK)
        fr = _add(fr, lay, 0)
    lay = _layer(fr)
    ImageDraw.Draw(lay).text((fr.w - 24, fr.h - 24), "WAVE 1 CLEARED", font=U.F(U.SL.ANTON, 30 if not lev else 44), fill=(235, 240, 250, 255),
                             anchor="rb", stroke_width=2, stroke_fill=INK)
    fr = _add(fr, lay, 0)
    return tag(fr, "RIGGER  //  FIELD REPAIR" + ("  LEVELLED: + CORE" if lev else "  BASE (hovered)"), (255, 222, 30) if lev else (92, 225, 255))


# ------------------------------------------------------------------ 30 unit health + status ring (icons v4)
def ground_unit(fr, x, y, corp, hp, t, r=16.0, statuses=(), heading=None):
    lay = _layer(fr)
    d = ImageDraw.Draw(lay)
    col = IC.CORP_RGB[corp]
    pts = gpoly(fr, x, y, r, 48)
    ys = [p[1] for p in pts]
    level = max(ys) - (max(ys) - min(ys)) * hp
    m = Image.new("L", lay.size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    lo = Image.new("L", lay.size, 0)
    ImageDraw.Draw(lo).rectangle([0, level, lay.size[0], lay.size[1]], fill=255)
    lay.paste(Image.new("RGBA", lay.size, col + (115,)), (0, 0), ImageChops.multiply(m, lo))
    lay.paste(Image.new("RGBA", lay.size, col + (35,)), (0, 0), ImageChops.multiply(m, ImageChops.invert(lo)))
    d.line(pts + [pts[0]], fill=col + (210,), width=2)
    R = r * 1.45
    dashed_ring(d, fr, x, y, R, IC.RING_RGB[corp], 255, 4, n=24, phase=t)
    for k, st in enumerate(statuses):
        a = -math.pi / 3 + k * 0.5
        px, py = L(fr, x + R * math.cos(a), y + R * math.sin(a))
        d.ellipse([px - 16, py - 16, px + 16, py + 16], fill=INK)
        d.ellipse([px - 14, py - 14, px + 14, py + 14], fill=IC.STATUS[st][0] + (255,))
        g = IC.glyph_mask(IC.STATUS[st][1], 20)
        lay.paste(Image.new("RGBA", g.size, INK), (int(px - 10), int(py - 10)), g)
    if heading is not None:
        tip = L(fr, x + (R + 6) * math.cos(heading), y + (R + 6) * math.sin(heading))
        l_ = L(fr, x + (R - 1) * math.cos(heading + 0.3), y + (R - 1) * math.sin(heading + 0.3))
        r_ = L(fr, x + (R - 1) * math.cos(heading - 0.3), y + (R - 1) * math.sin(heading - 0.3))
        d.polygon([tip, l_, r_], fill=(255, 222, 30, 255), outline=(255, 250, 220, 255))
    return _add(fr, lay, 0.5)


def g30(t, i):
    rt = LY.route_points("r1")
    (x, y), hd = V.path_point(rt, 0.215 + 0.035 * t)
    (x2, y2), _ = V.path_point(rt, 0.3)
    head = math.atan2(y2 - y, x2 - x)
    b = S.boxc(*P(*V.path_point(rt, 0.232)[0]), 800, 450)          # fixed camera: the unit drives through it
    hp = 1.0 - 0.85 * t
    st = () if t < 0.2 else ("SLOWED",) if t < 0.45 else ("FROZEN",) if t < 0.7 else ("BURNING", "EXPOSED")
    hover = 0.3 <= t < 0.62
    fr = base("setup_h1", deco(forecast={}), b, "g30")
    fr = V.paste_sprite(fr, "BAILIFF", hd, x, y)
    fr = ground_unit(fr, x, y, "HALCYON", hp, t * 2, statuses=st, heading=head if hover else None)
    ic = IC.unit_icon("HALCYON", 1, size=74, hp=hp, statuses=st, heading=head if hover else None, ring_phase=t * 2)
    lay = _layer(fr)
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([fr.w - 214, 14, fr.w - 14, 250], 10, fill=(5, 9, 20, 225), outline=(60, 70, 100, 255))
    lay.alpha_composite(ic, (int(fr.w - 114 - ic.width / 2), int(128 - ic.height / 2)))
    d.text((fr.w - 196, 24), "HP %d / 15" % round(15 * hp), font=U.F(U.SL.MONO, 16), fill=IC.CORP_RGB["HALCYON"] + (255,))
    d.text((fr.w - 196, 214), ", ".join(st).lower() or "no status", font=U.F(U.SL.MONO, 13), fill=(190, 225, 240, 255))
    d.text((fr.w - 196, 232), "hover: heading" if hover else "zoomed out: the icon", font=U.F(U.SL.MONO, 12), fill=(255, 222, 30, 255))
    fr = _add(fr, lay, 0)
    return tag(fr, "UNIT HEALTH + STATUS RING  //  HALCYON BAILIFF")


# ------------------------------------------------------------------ 31 Heat spotlights (EXPOSED)
def g31(t, i):
    vx, vy = N["relay"][:2]                                         # the Relay: no bright defence on it, the ticks read
    b = S.boxc(*P(vx, vy - 10), 960, 540)
    a = 2 * math.pi * t
    wx = 5 * (0.7 * math.sin(2 * math.pi * 3 * t) + 0.3 * math.sin(2 * math.pi * 7 * t))
    wy = 5 * (0.7 * math.cos(2 * math.pi * 2 * t) + 0.3 * math.sin(2 * math.pi * 5 * t))
    tx, ty = vx + wx, vy + wy
    pools = [(tx, ty, 20.0, 0.5)]                                   # dimmer: the EXPOSED ticks must read through
    drones = []
    for k in range(3):
        da = a * (1 if k % 2 else -1) + k * 2.1
        dx, dy = vx + (55 + 12 * k) * math.cos(da), vy + (55 + 12 * k) * math.sin(da)
        pools.append((dx, dy, 8.0, 0.35))
        drones.append((dx, dy))
    img = S.FN.finish("setup_h1", "night", decorate=deco(forecast={}, exposed=("relay",), t=t), net_cls=S.ND.Net, box=b, seed=1,
                      pools=pools, t=t)
    fr = S.Frame(img, b)
    hx, hy = vx + 70 * math.cos(a), vy + 70 * math.sin(a)
    sh = L(fr, hx, hy, 110)
    beams = [(sh[0], sh[1], *L(fr, tx, ty), 64)]
    for (dx, dy) in drones:
        beams.append((*L(fr, dx, dy, 40), *L(fr, dx, dy), 24))
    im = Image.fromarray((np.clip(fr.img, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    im = R35.heat_diegetic(im, beams, [], k=0.9).convert("RGBA")
    d = ImageDraw.Draw(im)
    hxl, hyl = sh
    ah = L(fr, hx + 8 * math.cos(a + math.pi / 2), hy + 8 * math.sin(a + math.pi / 2), 110)
    f2 = (ah[0] - hxl, ah[1] - hyl)
    nf = math.hypot(*f2) or 1.0
    f2 = (f2[0] / nf, f2[1] / nf)
    sd = (-f2[1], f2[0])
    d.line([(hxl - 20 * f2[0], hyl - 20 * f2[1]), (hxl - 44 * f2[0], hyl - 44 * f2[1])], fill=(110, 100, 150, 255), width=4)
    d.polygon([(hxl + 24 * f2[0], hyl + 24 * f2[1]), (hxl - 22 * f2[0] + 9 * sd[0], hyl - 22 * f2[1] + 9 * sd[1]),
               (hxl - 22 * f2[0] - 9 * sd[0], hyl - 22 * f2[1] - 9 * sd[1])], fill=(130, 120, 175, 255), outline=INK)
    rot = (i * 0.9) % math.pi
    for q in (rot, rot + math.pi / 2):
        d.line([(hxl - 30 * math.cos(q), hyl - 14 * math.sin(q)), (hxl + 30 * math.cos(q), hyl + 14 * math.sin(q))], fill=(210, 210, 230, 150), width=2)
    d.ellipse([hxl - 3, hyl - 3, hxl + 3, hyl + 3], fill=(255, 50, 50, 255) if (i // 2) % 2 else (60, 120, 255, 255))
    for (dx, dy) in drones:
        x_, y_ = L(fr, dx, dy, 40)
        d.rectangle([x_ - 6, y_ - 3, x_ + 6, y_ + 3], fill=(90, 86, 110, 255), outline=INK)
        for sx_ in (-8, 8):
            d.ellipse([x_ + sx_ - 4, y_ - 5, x_ + sx_ + 4, y_ - 1], outline=(200, 200, 220, 160))
        d.ellipse([x_ - 2, y_ + 1, x_ + 2, y_ + 5], fill=(255, 60, 60, 255))
    fr.img = np.asarray(im.convert("RGB"), np.float32) / 255.0
    return tag(fr, "HEAT 75  //  SPOT-LIT NODE = EXPOSED", (255, 176, 0))


# ------------------------------------------------------------------ 21 node TAKEN v2 (round 23: normal weight, ABOVE the node)
def g21v2(t, i):
    px, py = P(*N["proxy"][:2])
    b = S.boxc(px + 100, py + 10)
    removed = t > 0.55
    fr = base("setup_h1", deco(st={"proxy": "burnt" if removed else "seized"}, forecast={}), b, "g21v2%d" % removed)
    pen = S.V2.Pencil(fr, 21)
    pen.text("TAKEN", px + 2, py - 58, 22, V.R_PEN, 4.0, progress=seg(t, 0.12, 0.38))
    return pen.composite(wipe=seg(t, 0.62, 0.82))


EXTRA = [
    ("21_node_taken_v2.gif", 22, g21v2, "Node TAKEN (v2)", "normal-weight TAKEN written above the node, holds, wipes like DOWN"),
    ("28_bonus_slow.gif", 24, g28, "Station bonus: slow field (Ghost)",
     "round 23 v3 on the one city: a ground layer under the units, slow blue dashed rings drift inward (SLOWED -1 STEP); "
     "levelled: ice crystals grow inward from the edge, the unit is iced over (FROZEN 1 STEP)"),
    ("29_bonus_repair.gif", 24, g29, "Station bonus: field repair (Rigger)",
     "round 23 v3: the socket's locked health fill rises south > north; hovered: the number + 10-segment bar count up; "
     "levelled: the linked CORE refills too; '+' marks, streaks, sparks"),
    ("30_unit_health.gif", 24, g30, "Unit health + status ring (icons v4)",
     "round 22: on the street the unit stands in its corp-colour disc, which drains top-down; the dashed corp ring carries "
     "SLOWED > FROZEN > BURNING + EXPOSED pips; heading arrow only on hover; the v4 icon (zoomed out) carries the same"),
    ("31_spotlights.gif", 16, g31, "Heat spotlights (EXPOSED)",
     "a police chopper circles the Relay, its spot wobbles on the node, which wears the white EXPOSED hazard ticks; three "
     "drones circle with mini spots"),
]


if __name__ == "__main__":
    only = sys.argv[1:]
    for name, n, fn, ttl, txt in EXTRA:
        if only and not any(name.startswith(o) for o in only):
            continue
        S.gif(name, n, fn, dur=100, size=(800, 450))
    print("extra done", flush=True)
