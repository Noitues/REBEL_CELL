"""Round 22 raid world: Rigger idle (blink / angry), Phantom vs Botnet colours, slow + repair v2, icons v4 + unit health.

python screens22.py [name ...]  names: rigger beacons slow repair bonuses icons toggle health contact
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as LY  # noqa: E402
import finish19 as FN  # noqa: E402
import ui19 as U  # noqa: E402
import roof20 as RF  # noqa: E402
import screens20 as S20  # noqa: E402
import screens21 as S21  # noqa: E402
import icons22 as IC  # noqa: E402

OUT = os.path.dirname(HERE)
S20.OUT = S21.OUT = OUT
SL = U.SL
W, H = LY.W, LY.H
canvas, paste, crop, label, title = S20.canvas, S20.paste, S20.crop, S20.label, S20.title
to_pil, to_f, P, scene_cam, paste_rgba = S20.to_pil, S20.to_f, S20.P, S20.scene_cam, S20.paste_rgba
TXT, DIM = S20.TXT, S20.DIM
Fx, PS, ground_poly, save_gif = S21.Fx, S21.PS, S21.ground_poly, S21.save_gif
S21.KEY_COLS[:] = list(RF.CLASS_RGB.values()) + [(212, 255, 0), (92, 225, 255), (255, 68, 51), (255, 176, 0), (150, 92, 255),
                                                 (255, 128, 16), (108, 255, 40), (120, 236, 255), (190, 240, 255), (90, 170, 255)]


def save(img, name):
    to_pil(img).save(os.path.join(OUT, name), optimize=True)
    print("saved", name, flush=True)


# ------------------------------------------------------------------ 1. Rigger: goggles blink, sometimes angry
def rigger_mask(blink=0.0, angry=0.0):
    """The round 6 Rigger emblem (goggles + cable smile) rebuilt with a blink (lenses close to a slit) and an angry
    face (lenses cut by slanted brows, the cable smile turns into a frown)."""
    S = 512
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    h = 100 * (1 - 0.88 * blink)
    for i, x in enumerate((150, 362)):
        d.ellipse([x - 100, 240 - h, x + 100, 240 + h], fill=255)
        hi = max(0.0, h - 40)
        if hi > 4:
            d.ellipse([x - 60, 240 - hi, x + 60, 240 + hi], fill=0)
        if angry > 0:                                      # brow: slanted bar, INNER end low (a scowl), cuts the lens top
            inner = x + 120 if i == 0 else x - 120
            outer = x - 120 if i == 0 else x + 120
            yi, yo = 112 + 95 * angry, 112 - 10 * angry
            d.polygon([(outer, 0), (inner, 0), (inner, yi), (outer, yo)], fill=0)
            d.polygon([(outer, yo - 34), (inner, yi - 34), (inner, yi + 4), (outer, yo + 4)], fill=255)
    d.rectangle([240, 220, 272, 260], fill=255)
    if angry < 0.5:
        d.arc([60, 250, 452, 500], 20, 160, fill=255, width=26)
    else:                                                  # frown
        d.arc([110, 380, 402, 560], 200, 340, fill=255, width=26)
    return m


RIGGER_SEQ = ([("idle", 0, 0)] * 5 + [("blink", 1, 0), ("blink", 0.5, 0)] + [("idle", 0, 0)] * 5 + [("blink", 1, 0), ("idle", 0, 0)] * 1 +
              [("angry", 0, a) for a in (0.4, 1, 1, 1, 1, 1, 1)] + [("angry", 0.6, 1), ("angry", 0, 0.5)] + [("idle", 0, 0)] * 2)


def rigger_gif():
    n = len(RIGGER_SEQ)
    tw, th = 520, 470
    frames, durs = [], []
    for f, (state, blink, angry) in enumerate(RIGGER_SEQ):
        S21.EMBLEM_OVERRIDE["rigger"] = rigger_mask(blink, angry)
        tile = S21.r3_tile("rigger", (f % 12) / 12, (tw, th))
        if angry > 0.9:                                    # the cone flares and jitters while angry
            tile = np.clip(tile * (1.0 + 0.12 * math.sin(f * 2.1)), 0, 1)
        im = Image.new("RGB", (tw + 300, th + 60), (8, 7, 14))
        im.paste(to_pil(tile), (0, 60))
        d = ImageDraw.Draw(im)
        d.text((12, 14), "RIGGER  //  STATION BEACON IDLE", font=U.F(SL.ANTON, 26), fill=RF.CLASS_RGB["rigger"])
        big = rigger_mask(blink, angry).resize((200, 200), Image.LANCZOS)
        im.paste(Image.new("RGB", (200, 200), RF.CLASS_RGB["rigger"]), (tw + 50, 110), big)
        tag = {"idle": "idle: cable rings climb", "blink": "the goggles BLINK", "angry": "...and sometimes it gets ANGRY"}[state]
        d.text((tw + 20, 350), tag, font=U.F(SL.MONO, 16), fill=(255, 222, 30) if state != "idle" else (190, 225, 240))
        d.text((tw + 20, 380), "blink every ~3 s, angry 1 in ~6 loops", font=U.F(SL.MONO, 12), fill=(150, 165, 185))
        d.text((tw + 20, 400), "(or when its node takes damage)", font=U.F(SL.MONO, 12), fill=(150, 165, 185))
        frames.append(im)
        durs.append(70 if state == "blink" else 110)
        print("rigger", f, flush=True)
    S21.EMBLEM_OVERRIDE.clear()
    return save_gif(frames, "operator_rigger.gif", durs)


def beacons_v2():
    """operators_r3 with the new Phantom (pale lilac) / Botnet (indigo) colours + the angry Rigger still."""
    cv = S21.operators_r3()
    sw = [("ghost", "GHOST"), ("phantom", "PHANTOM  v2 pale lilac"), ("botnet", "BOTNET  v2 indigo"), ("hivemind", "HIVEMIND")]
    return cv, sw


def colour_strip():
    cv = canvas()
    cv = title(cv, "CLASS COLOURS V2", "PHANTOM AND BOTNET SEPARATED: PHANTOM -> PALE LILAC (AN AFTERIMAGE), BOTNET -> INDIGO-BLUE (A SWARM); "
                                     "HIVEMIND KEEPS THE VIOLET")
    tw, th = 440, 380
    for i, c in enumerate(("ghost", "phantom", "botnet", "hivemind")):
        x = 40 + i * 460
        cv = paste(cv, S21.r3_tile(c, 0.3, (tw, th)), x, 150)
        cv = label(cv, x, 540, c.upper(), 26, RF.CLASS_RGB[c], font=SL.ANTON)
        cv = label(cv, x, 580, "#%02X%02X%02X" % RF.CLASS_RGB[c], 14, DIM)
    old = {"phantom": (150, 130, 255), "botnet": (176, 140, 255)}
    cv = label(cv, 40, 640, "ROUND 21 (too close)", 16, (235, 240, 250))
    for i, c in enumerate(("phantom", "botnet")):
        im = to_pil(cv)
        ImageDraw.Draw(im).rectangle([40 + i * 140, 670, 160 + i * 140, 730], fill=old[c])
        cv = to_f(im)
        cv = label(cv, 40 + i * 140, 736, c, 12, DIM)
    cv = label(cv, 400, 640, "ROUND 22", 16, (235, 240, 250))
    for i, c in enumerate(("ghost", "phantom", "botnet", "hivemind", "breaker", "wrecker", "rigger", "overclocker")):
        im = to_pil(cv)
        ImageDraw.Draw(im).rectangle([400 + i * 140, 670, 520 + i * 140, 730], fill=RF.CLASS_RGB[c])
        cv = to_f(im)
        cv = label(cv, 400 + i * 140, 736, c, 12, DIM)
    S21.EMBLEM_OVERRIDE["rigger"] = rigger_mask(0, 1)
    cv = paste(cv, S21.r3_tile("rigger", 0.3, (330, 285)), 40, 780)
    S21.EMBLEM_OVERRIDE["rigger"] = rigger_mask(1, 0)
    cv = paste(cv, S21.r3_tile("rigger", 0.3, (330, 285)), 390, 780)
    S21.EMBLEM_OVERRIDE.clear()
    cv = label(cv, 740, 800, "RIGGER: angry (left), blink (right)  -> operator_rigger.gif", 16, RF.CLASS_RGB["rigger"])
    return cv


# ------------------------------------------------------------------ 2. slow / freeze v2, repair v2
SLOW_BLUE = (90, 170, 255)
ICE_W = (225, 248, 255)
ICE_B = (150, 215, 255)


def dashed_ground_ring(fx, cx, cy, R, col, n=40, phase=0.0, width=4, k=1.2, gap=0.45):
    for i in range(n):
        a0 = 2 * math.pi * (i + phase) / n
        a1 = 2 * math.pi * (i + phase + 1 - gap) / n
        pts = [PS(cx + R * math.cos(a0 + (a1 - a0) * q / 4), cy + R * math.sin(a0 + (a1 - a0) * q / 4)) for q in range(5)]
        fx.line(pts, col, width, k)


def fx_slow_v2(t, lev):
    cls = "ghost"
    img = S21.bonus_base(cls, heat=False)
    img = S21.with_beacon(img, cls, t)
    cx, cy, R = 10, -120, 30
    freeze = lev and 0.42 <= t < 0.9
    fz = 0.0 if not freeze else min(1.0, (t - 0.42) / 0.22)
    fx = Fx()
    # the dashed outline carries the effect
    dashed_ground_ring(fx, cx, cy, R, ICE_W if freeze else SLOW_BLUE, phase=t * 0.6, width=5, k=1.4)
    if not freeze or fz < 1:
        for k in range(3):                                   # SLOW: slow blue dashed rings drifting inward
            q = (t * 0.7 + k / 3) % 1.0
            dashed_ground_ring(fx, cx, cy, R * (1 - 0.75 * q), SLOW_BLUE, n=int(34 * (1 - 0.6 * q)), phase=-t, width=3,
                               k=0.9 * (1 - q) * (1 - fz))
    if freeze:                                                # FROZEN: crystals grow from the edge inward + translucent fill
        fx.poly(ground_poly(cx, cy, R), ICE_B, k=0.1 * fz)
        rng = np.random.default_rng(7)
        for i in range(46):
            a = 2 * math.pi * i / 46 + rng.uniform(-0.03, 0.03)
            L = R * rng.uniform(0.18, 0.42) * fz
            wd = rng.uniform(0.05, 0.09)
            base0 = (cx + R * math.cos(a - wd), cy + R * math.sin(a - wd))
            base1 = (cx + R * math.cos(a + wd), cy + R * math.sin(a + wd))
            tip = (cx + (R - L) * math.cos(a), cy + (R - L) * math.sin(a))
            tri = [PS(*base0), PS(*tip), PS(*base1)]
            fx.poly(tri, ICE_B, k=0.38)
            fx.line([PS(*base0), PS(*tip), PS(*base1)], ICE_W, 2, 0.75)
            if i % 3 == 0 and fz > 0.5:                       # side spurs
                m_ = (cx + (R - L * 0.5) * math.cos(a), cy + (R - L * 0.5) * math.sin(a))
                sp = (cx + (R - L * 0.75) * math.cos(a + 0.08), cy + (R - L * 0.75) * math.sin(a + 0.08))
                fx.line([PS(*m_), PS(*sp)], ICE_W, 2, 1.0)
    out = fx.comp(img, glow=0.45)
    tx, ty = S21.threat_px(0)
    fx2 = Fx()
    if freeze and fz > 0.6:
        reg = out[int(ty) - 50:int(ty) + 30, int(tx) - 60:int(tx) + 60]
        reg[:] = reg * 0.5 + (reg.mean(axis=2, keepdims=True) * 0.5 + 0.38) * (np.array(ICE_B, np.float32) / 255) * 0.6
        g = np.asarray(Image.open(os.path.join(U.GLYPHS, "state_frozen.png")).split()[3].resize((50, 50)), np.float32) / 255
        fx2.add[int(ty) - 104:int(ty) - 54, int(tx) - 25:int(tx) + 25] += g[..., None] * np.array(ICE_W, np.float32) / 255 * 1.3
        fx2.text(tx, ty + 56, "FROZEN 1 STEP", 24, (200, 240, 255))
    else:
        fx2.text(tx, ty + 56, "SLOWED  -1 STEP", 22, SLOW_BLUE)
    return fx2.comp(out)


def fx_repair_v2(t, lev):
    """Health goes UP: green integrity cells stack upward in a column over the socket, '+' marks and streaks rise."""
    cls, col = "rigger", RF.CLASS_RGB["rigger"]
    u = min(1.0, max(0.0, (t - 0.1) / 0.62))
    integ = {"safe": round(0.3 + 0.7 * u, 2)}
    if lev:
        integ["core"] = round(0.45 + 0.55 * u, 2)
    img = S21.bonus_base(cls, heat=False, integ=integ, rings="down", shares=(("safe", "core", cls),) if lev else ())
    img = S21.with_beacon(img, cls, t)
    fx = Fx()
    for (wx, wy, v0, on, dy) in ((10, -120, 0.3, True, -10), (10, -50, 0.45, lev, 200)):
        if not on:
            continue
        sx, sy = PS(wx, wy)
        bx, by = sx + 80, sy + dy
        v = v0 + (1 - v0) * u
        n = 10
        for k in range(n):                                   # the integrity column: cells stack bottom -> top
            y0 = by - k * 18
            lit = (k + 0.5) / n <= v
            new = lit and (k + 0.5) / n > v - 0.1 and u < 1
            fx.poly([(bx - 18, y0), (bx + 18, y0), (bx + 18, y0 - 13), (bx - 18, y0 - 13)], col if lit else (40, 60, 40),
                    k=(1.8 if new else 1.0) if lit else 0.5)
        fx.line([(bx - 22, by + 3), (bx + 22, by + 3)], col, 2, 1.0)
        for k in range(7):                                   # '+' marks rising straight up from the socket
            q = (t * 1.6 + k / 7) % 1.0
            x = sx - 40 + (k * 37) % 80
            y = sy - 10 - 150 * q
            a = 1.3 * (1 - q) * (0.2 if u >= 1 else 1)
            fx.line([(x - 7, y), (x + 7, y)], col, 4, a)
            fx.line([(x, y - 7), (x, y + 7)], col, 4, a)
        for k in range(5):                                   # vertical streaks
            q = (t * 2.2 + k / 5) % 1.0
            x = sx - 30 + k * 15
            fx.line([(x, sy - 20 - 120 * q), (x, sy - 50 - 120 * q)], (190, 255, 190), 2, 0.9 * (1 - q) * (0.2 if u >= 1 else 1))
        if 0.1 <= t < 0.8:
            S21.float_up(fx, bx + 40, by - 18 * 10 * v - 10, "+%d" % int(round(20 * (v - v0))), col, 0.2, 28)
    fx.text(1100, 520, "WAVE 1 CLEARED", 40, (235, 240, 250))
    return fx.comp(img)


S21.BCROP["slow"] = (113, 360, 1393, 1080)
S21.BCROP["repair"] = (113, 360, 1393, 1080)
V2 = [("slow", "B  SLOW FIELD v2", "GHOST  (GDD: entering threats delayed 1 step)", fx_slow_v2,
       "the dashed edge carries it: slow blue dashed rings drift inward",
       "freeze: ice crystals grow from the edge inward, light-blue translucent fill"),
      ("repair", "E  FIELD REPAIR v2", "RIGGER  (GDD: node regains integrity after each wave)", fx_repair_v2,
       "health goes UP: a column of integrity cells stacks upward, + marks rise",
       "adjacent node (CORE) repairs too")]


def bonus_gifs_v2():
    n = 18
    PW, PH = S21.PW, S21.PH
    for key, nm, who, fn, b_txt, l_txt in V2:
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
            im.paste(S21.bonus_panel(fn, f / n, False, "BASE", key), (10, 50))
            im.paste(S21.bonus_panel(fn, f / n, True, "LEVELLED UP", key), (20 + PW, 50))
            frames.append(im)
            print(key, f, flush=True)
        save_gif(frames, "bonus_%s_v2.gif" % key, [100] * n)


def station_bonuses_v2():
    """The round 21 sheet with B and E swapped for v2 (same layout)."""
    for i, b in enumerate(S21.BONUSES):
        for v in V2:
            if b[0] == v[0]:
                S21.BONUSES[i] = v
    cv = S21.station_bonuses()
    return cv


# ------------------------------------------------------------------ 3. vehicle icons v4, unit health, toggle v3
def ground_unit(fx, cam, x, y, corp, hp, t=0.0, r=9.0, statuses=(), heading=None):
    """On the street: the unit's FILLED disc (corp colour) drains from the top of the screen down; the dashed corp ring
    (bigger) carries status pips and, on hover, the heading arrow."""
    pts = [P(x + r * math.cos(2 * math.pi * i / 48), y + r * math.sin(2 * math.pi * i / 48), 0.1, cam=cam) for i in range(48)]
    ys = [p[1] for p in pts]
    top, bot = min(ys), max(ys)
    level = bot - (bot - top) * hp
    col = IC.CORP_RGB[corp]
    m = fx._mask(lambda d: d.polygon(pts, fill=255))
    yy = np.arange(fx.h, dtype=np.float32)[:, None]
    fx.add += (m * (yy >= level) * 0.26)[..., None] * (np.array(col, np.float32) / 255)
    fx.add += (m * (yy < level) * 0.08)[..., None] * (np.array(col, np.float32) / 255)
    fx.line(pts + [pts[0]], col, 2, 0.8)
    R = r * 1.45
    for i in range(24):
        a0, a1 = 2 * math.pi * (i + t) / 24, 2 * math.pi * (i + t + 0.55) / 24
        seg = [P(x + R * math.cos(a0 + (a1 - a0) * q / 3), y + R * math.sin(a0 + (a1 - a0) * q / 3), 0.1, cam=cam) for q in range(4)]
        fx.line(seg, IC.RING_RGB[corp], 4, 1.3)
    for i, st in enumerate(statuses):
        a = -math.pi / 3 + i * 0.5
        p = P(x + R * math.cos(a), y + R * math.sin(a), 0.1, cam=cam)
        fx.disc(p[0], p[1], 16, (14, 12, 20), 0.0)
        g = IC.glyph_mask(IC.STATUS[st][1], 22)
        fx.disc(p[0], p[1], 15, IC.STATUS[st][0], 1.2)
        fx.txt.paste(Image.new("RGBA", g.size, (14, 12, 20, 255)), (int(p[0] - 11), int(p[1] - 11)), g)
    if heading is not None:
        tip = P(x + (R + 5) * math.cos(heading), y + (R + 5) * math.sin(heading), 0.1, cam=cam)
        l = P(x + (R - 1) * math.cos(heading + 0.3), y + (R - 1) * math.sin(heading + 0.3), 0.1, cam=cam)
        rr = P(x + (R - 1) * math.cos(heading - 0.3), y + (R - 1) * math.sin(heading - 0.3), 0.1, cam=cam)
        fx.poly([tip, l, rr], (255, 222, 30), 2.4)
        fx.line([tip, l, rr, tip], (255, 250, 220), 2, 1.2)


def vehicle_icons_v4():
    cv = canvas()
    cv = title(cv, "VEHICLE ICONS V4", "SHAPE = TYPE  //  FILL = CORP COLOUR = HEALTH (DRAINS TOP DOWN)  //  DASHED CORP RING = STATUSES + "
                                       "HEADING (HOVER)  //  LANDER IS ORBITAL'S SPECIAL")
    corps = list(IC.CORP_RGB)
    x0, y0 = 300, 150
    for j, c in enumerate(corps):
        cv = label(cv, x0 + j * 150, y0, c, 16, IC.CORP_RGB[c], font=SL.ANTON, anchor="ma")
    desc = {"FAST": "chevron badge  //  >> (raised)", "HEAVY": "thick block  //  weight", "SPECIAL": "hexagon  //  its verb",
            "FLYING": "drone diamond  //  4 rotors"}
    for i, t in enumerate(IC.TYPES):
        y = y0 + 80 + i * 140
        cv = label(cv, 40, y - 10, t, 30, (235, 240, 250), font=SL.ANTON)
        cv = label(cv, 40, y + 30, desc[t], 12, DIM)
        for j, c in enumerate(corps):
            names = ["CHOPPER / DRONE"] if t == "FLYING" else [IC.UNIT_NAMES[c][ui] for ui in range(3) if IC.unit_type(c, ui) == t]
            cv = paste_rgba(cv, IC.icon(t, c, size=54), x0 + j * 150, y + 6)
            cv = label(cv, x0 + j * 150, y + 66, " / ".join(names), 11, (230, 236, 245), anchor="ma")
    # health + ring legend
    cv = label(cv, 40, 790, "HEALTH (fill drains from the top)", 15, U.CYAN)
    for i, hp in enumerate((1.0, 0.75, 0.5, 0.25, 0.08)):
        cv = paste_rgba(cv, IC.icon("HEAVY", "HALCYON", size=50, hp=hp), 100 + i * 120, 880)
        cv = label(cv, 100 + i * 120, 940, "%d%%" % round(hp * 100), 12, DIM, anchor="ma")
    cv = label(cv, 700, 790, "RING: STATUSES + HEADING (hover / select)", 15, U.CYAN)
    demo = [(("SLOWED",), None, "slowed"), (("FROZEN",), None, "frozen"), (("BURNING", "EXPOSED"), None, "burning + exposed"),
            ((), -2.4, "hover: heading"), (("CORRUPTED",), -0.4, "upgraded + corrupted")]
    for i, (st, hd, nm) in enumerate(demo):
        cv = paste_rgba(cv, IC.icon("FAST", "MERIDIAN", up=(i == 4), size=50, hp=0.7, statuses=st, heading=hd), 760 + i * 130, 880)
        cv = label(cv, 760 + i * 130, 950, nm, 11, DIM, anchor="ma")
    cv = label(cv, 40, 1000, "REBEL_CELL's ring dashes are paled toward white; every ring is bigger than its icon so statuses sit clear of it.", 12, TXT)
    # right: the 30 at map scale
    lay = json.load(open(os.path.join(FN.SRC, "veh_layout.json")))
    img = S20.vehicle_matrix_img()
    k = lay["ortho"] / 440.0
    full = to_pil(img).resize((int(W * k), int(H * k)), Image.LANCZOS)
    xs = [it["px"] for it in lay["items"]]
    ys = [it["py"] for it in lay["items"]]
    bx = (int((min(xs) - 70) * k), int((min(ys) - 60) * k), int((max(xs) + 70) * k), int((max(ys) + 40) * k))
    strip = full.crop(bx)
    fit = min(560 / strip.size[0], 300 / strip.size[1])
    strip = strip.resize((int(strip.size[0] * fit), int(strip.size[1] * fit)), Image.LANCZOS)
    sx, sy = 1120, 190
    cv = paste(cv, np.asarray(strip, np.float32) / 255, sx, sy)
    cv = label(cv, sx, sy - 24, "MAP SCALE: the 30 models", 13, U.CYAN)
    tile = np.zeros((strip.size[1], strip.size[0], 3), np.float32) + np.array([0.09, 0.08, 0.14], np.float32)
    rng = np.random.default_rng(3)
    for it in lay["items"]:
        tile = paste_rgba(tile, IC.unit_icon(it["corp"], it["col"] // 2, up=it["up"], size=20, hp=float(rng.choice([1, 1, 0.7, 0.4]))),
                          (it["px"] * k - bx[0]) * fit, (it["py"] * k - bx[1]) * fit)
    cv = paste(cv, tile, sx, sy + strip.size[1] + 50)
    cv = label(cv, sx, sy + strip.size[1] + 26, "THE SAME 30 AS V4 ICONS (some damaged)", 13, U.CYAN)
    return cv


def toggle_v3():
    cv = canvas()
    cv = title(cv, "VEHICLE / ICON TOGGLE V3", "ON THE STREET EACH UNIT STANDS IN ITS DRAINING HEALTH DISC + DASHED CORP RING; ZOOMED OUT THE ICON CARRIES BOTH")
    cam = scene_cam("W_close")
    close = FN.finish("W_close", "night", decorate=S20.world_decor("B", routes=("r1", "r3")), seed=1, tilt=0.0)
    fx = Fx()
    st = {0: ("SLOWED",), 2: ("BURNING",), 5: ("FROZEN",)}
    for i, (corp, ui, x, y, a, up, hp) in enumerate(LY.THREATS_V2):
        ground_unit(fx, cam, x, y, corp, hp, t=0.2, statuses=st.get(i, ()), heading=a if i == 2 else None)
    close = fx.comp(close)
    cv = paste(cv, close, 40, 150, (1000, 563))
    cv = label(cv, 40, 724, "CLOSE-UP: filled disc = health (drains top-down); dashed corp ring = statuses; arrow on hover (HAULER +)", 14, (235, 240, 250))
    full_cam = scene_cam("B_full")
    cx, cy = P(104, -82, 0, cam=full_cam)
    cw, ch = 1150, 647
    box = (int(cx - cw / 2), int(cy - ch / 2) + 30, int(cx + cw / 2), int(cy + ch / 2) + 30)
    dw, dh = 820, 461
    sk = dw / cw
    iv = crop(FN.finish("B_full", "night", decorate=S20.world_decor("B", routes=("r1", "r3")), seed=1), box, (dw, dh))
    for i, (corp, ui, x, y, a, up, hp) in enumerate(LY.THREATS_V2):
        px, py = P(x, y, 0, cam=full_cam)
        iv = paste_rgba(iv, IC.unit_icon(corp, ui, up=up, size=24, hp=hp, statuses=st.get(i, ())), (px - box[0]) * sk, (py - box[1]) * sk)
    cv = paste(cv, iv, 1060, 150)
    cv = label(cv, 1060, 622, "ZOOMED OUT: v4 icons (fill = health, ring = statuses); no heading", 14, (235, 240, 250))
    for i, (corp, ui, x, y, a, up, hp) in enumerate(LY.THREATS_V2[:7]):
        cv = paste_rgba(cv, IC.unit_icon(corp, ui, up=up, size=44, hp=hp, statuses=st.get(i, ())), 90 + i * 135, 870)
        cv = label(cv, 90 + i * 135, 935, IC.UNIT_NAMES[corp][ui] + (" +" if up else ""), 12, (230, 236, 245), anchor="ma")
        cv = label(cv, 90 + i * 135, 953, "HP %d%%" % round(hp * 100), 10, IC.CORP_RGB[corp], anchor="ma")
    rows = [("kv", "MAP ZOOM", "0.45x", (190, 225, 240)), ("kv", "UNITS", "ICONS (auto)", U.LIME), ("t", "hold [V]: show models", (150, 190, 205)),
            ("t", "hover: heading arrow + tag", (150, 190, 205))]
    cv = U.put_panel(cv, U.terminal("VIEW", rows, w=330), 1060, 680)
    return cv


def unit_health_gif():
    n = 24
    cam = scene_cam("W_close")
    base = FN.finish("W_close", "night", decorate=S20.world_decor("B", routes=("r1", "r3")), seed=1, tilt=0.0)
    corp, ui, x, y, a, up, _ = LY.THREATS_V2[2]                       # Meridian hauler +
    px, py = P(x, y, 0, cam=cam)
    box = (int(px - 360), int(py - 260), int(px + 360), int(py + 200))
    frames = []
    for f in range(n):
        t = f / n
        hp = 1.0 - 0.85 * t
        stl = ()
        if t >= 0.2:
            stl = ("SLOWED",)
        if t >= 0.45:
            stl = ("FROZEN",)
        if t >= 0.7:
            stl = ("BURNING", "EXPOSED")
        hover = 0.3 <= t < 0.62
        fx = Fx()
        ground_unit(fx, cam, x, y, corp, hp, t=t * 2, statuses=stl, heading=a if hover else None)
        img = to_pil(crop(fx.comp(base), box)).resize((600, 383), Image.LANCZOS)
        im = Image.new("RGB", (1000, 450), (8, 7, 14))
        im.paste(img, (10, 56))
        ic = IC.unit_icon(corp, ui, up=up, size=100, hp=hp, statuses=stl, heading=a if hover else None, ring_phase=t * 2)
        im.paste(ic, (800 - ic.size[0] // 2, 250 - ic.size[1] // 2), ic)
        d = ImageDraw.Draw(im)
        d.text((10, 12), "UNIT HEALTH + STATUS RING", font=U.F(SL.ANTON, 26), fill=(255, 222, 30))
        d.text((630, 66), "HP %d / 15" % round(15 * hp), font=U.F(SL.MONO, 18), fill=IC.CORP_RGB[corp])
        d.text((630, 410), ", ".join(stl).lower() or "no status", font=U.F(SL.MONO, 15), fill=(190, 225, 240))
        d.text((630, 430), "hover: heading" if hover else "", font=U.F(SL.MONO, 13), fill=(255, 222, 30))
        frames.append(im)
        print("health", f, flush=True)
    return save_gif(frames, "unit_health.gif", [110] * n)


def contact():
    from PIL import ImageSequence
    names = ["operator_rigger.gif", "class_colours_v2.png", "station_bonuses.png", "bonus_slow_v2.gif", "bonus_repair_v2.gif",
             "vehicle_icons_v4.png", "vehicle_toggle_v3.png", "unit_health.gif"]
    tw, th, cols = 600, 338, 3
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols + 40, th * rows + 24 * rows + 80), (10, 9, 16))
    d = ImageDraw.Draw(sheet)
    d.text((14, 16), "ROUND 22  RAID WORLD: RIGGER IDLE, CLASS COLOURS, SLOW / REPAIR V2, ICONS V4 + UNIT HEALTH", font=U.F(SL.ANTON, 30), fill=(255, 222, 30))
    for i, nme in enumerate(names):
        im = Image.open(os.path.join(OUT, nme))
        if nme.endswith(".gif"):
            fr = [f.convert("RGB") for f in ImageSequence.Iterator(im)]
            im = fr[len(fr) * 2 // 3]
        im = im.convert("RGB")
        k = min(tw / im.size[0], th / im.size[1])
        im = im.resize((int(im.size[0] * k), int(im.size[1] * k)), Image.LANCZOS)
        x, y = 10 + (i % cols) * (tw + 10), 70 + (i // cols) * (th + 24)
        sheet.paste(im, (x, y))
        d.text((x + 4, y + th + 2), nme, font=U.F(SL.MONO, 15), fill=(92, 225, 255))
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=86)
    print("saved contact_sheet.jpg")


if __name__ == "__main__":
    which = sys.argv[1:] or ["rigger", "colours", "bonusgifs", "bonuses", "icons", "toggle", "health", "contact"]
    if "rigger" in which:
        rigger_gif()
    if "colours" in which:
        save(colour_strip(), "class_colours_v2.png")
    if "bonusgifs" in which:
        bonus_gifs_v2()
    if "bonuses" in which:
        save(station_bonuses_v2(), "station_bonuses.png")
    if "icons" in which:
        save(vehicle_icons_v4(), "vehicle_icons_v4.png")
    if "toggle" in which:
        save(toggle_v3(), "vehicle_toggle_v3.png")
    if "health" in which:
        unit_health_gif()
    if "contact" in which:
        contact()
