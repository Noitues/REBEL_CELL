"""Round 20: corrupt tick v2, evade v2, Heat H1 polish, combat FX batch 2.

python fx_r20.py corrupt_tick_v2 evade_v2      # fx_corrupt_tick_v2.gif, fx_evade_v2.gif
python fx_r20.py heat                          # heat_city_v2.gif + heat_city_v2_strip.png
python fx_r20.py batch2                        # 6 x fx_<name>.gif + fx_batch2_storyboard.png
python fx_r20.py test <name> <t> ...           # single frames into scratch/
"""
import copy
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

import plates as P
import make_combat as MC
import make_sheets as MS
import fxlib as FX
import damage_shards as DS
import effects_batch1 as EB
from fxlib import seg, lerp, lerp2, bez, ease_out_cubic, ease_in_cubic, ease_in_out, ease_out_back
from slicelib import f_num, f_ui, f_mono, PROGRAMS, R_OUT, bloom

OUT = P.OUT
W, H = 1920, 1080
PC, BC = P.PLAYER["c"], P.BOSS["c"]
PR, BR = P.PLAYER["r"], P.BOSS["r"]
pt, wedge = EB.pt, EB.wedge
CORRUPT, VIOLET, GREEN, ORANGE, CYAN = EB.CORRUPT, EB.VIOLET, EB.GREEN, EB.ORANGE, EB.CYAN
RAM_C = (92, 225, 255)
YEL = (255, 214, 64)
GREY = (190, 186, 200)
MP, MB = EB.MP, EB.MB


# ------------------------------------------------------------------ shared
def scene2(p_sprite=None, b_sprite=None, p_state=None, b_state=None):
    """City + player + boss sprites (any of them overridden) + bloom."""
    img = P.city().copy()
    if p_sprite is None:
        p_sprite = P.wheel("player")[:2] if p_state is None else P.wheel_hp("player", *p_state)[:2]
    if b_sprite is None:
        b_sprite = P.wheel("boss")[:2] if b_state is None else P.wheel_hp("boss", *b_state)[:2]
    for kind, (im, c) in (("player", p_sprite), ("boss", b_sprite)):
        img.alpha_composite(im, P.wheel_pos(kind, c))
    return bloom(img.convert("RGB"), 1, 0.32, 0.66).convert("RGBA")


def dress(img, status=None, **hud):
    P.hud(img, next_p=False, next_e=False, **hud)
    if status:
        MC.status_bar(img, status, "NETRUN // MERIDIAN FREIGHT // LANE 15 DEPOT // BOSS: THE MANIFEST")
    P.stickers(img)
    EB.hand(img)
    return img


_SP = {}


def spin_any(kind, rot, blur, cheap=False):
    """A wheel at `rot` with rotational blur on the slice disc only. cheap=True rotates the rot-0 render
    (glyph blocks turn too: only used while the blur hides them)."""
    key = (kind, round(rot, 1), round(blur, 1), cheap)
    if key in _SP:
        return _SP[key]
    r = PR if kind == "player" else BR
    if cheap:
        bw, bc, _ = P.wheel(kind, 0.0, 1)
        base = bw.rotate(-rot, resample=Image.BILINEAR, center=bc)
        src = (bw, bc)
    else:
        bw, bc, _ = P.wheel(kind, round(rot % 360, 1), 1)
        base = bw
    n = max(1, int(abs(blur) / 1.5))
    if n > 1:
        acc = np.zeros((bw.height, bw.width, 4), np.float32)
        for k in range(n):
            a = -k / (n - 1) * blur
            im = bw.rotate(-(rot + a), resample=Image.BILINEAR, center=bc) if cheap else base.rotate(-a, resample=Image.BILINEAR, center=bc)
            acc += np.asarray(im, np.float32)
        acc /= n
    else:
        acc = np.asarray(base, np.float32)
    yy, xx = np.mgrid[0:bw.height, 0:bw.width]
    rho = np.hypot(xx - bc[0], yy - bc[1])
    m = (np.clip((rho - r * 0.37) / 4, 0, 1) * np.clip((r * 0.985 - rho) / 4, 0, 1))[..., None]
    ref = np.asarray(P.wheel(kind, 0.0, 1)[0] if cheap else base, np.float32)
    out = ref * (1 - m) + acc * m
    res = (Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA"), bc)
    if len(_SP) < 60:
        _SP[key] = res
    return res


def wheel_spec(tag, spec, kind="boss", ss=2):
    import frames as F
    p = os.path.join(MS.RC, tag + ".png")
    j = os.path.join(MS.RC, tag + ".json")
    os.makedirs(MS.RC, exist_ok=True)
    if os.path.exists(p) and os.path.exists(j):
        m = json.load(open(j))
        im, c, meta = Image.open(p).convert("RGBA"), tuple(m["centre"]), m["meta"]
    else:
        im, c, meta = F.render("d4", spec, ss=ss)
        im.save(p)
        json.dump(dict(centre=c, meta=meta, ss=ss), open(j, "w"))
        print("rendered", tag, flush=True)
    r = PR if kind == "player" else BR
    k = r / (R_OUT * ss)
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    return im, (c[0] * k, c[1] * k), meta


class Bits:
    """Glyph particles that hold, then fly a Bezier to their target (one per entry)."""

    def __init__(self, items, col, px=(22, 30), seed=1, hold=60):
        rng = np.random.default_rng(seed)
        self.p = []
        for it in items:
            d = dict(it)
            d.setdefault("ch", "01"[int(rng.random() < 0.5)])
            d.setdefault("px", rng.uniform(*px))
            d.setdefault("hold", hold)
            self.p.append(d)
        self.col = col

    def last(self):
        return max(q["t"] + q["hold"] + q["tr"] for q in self.p)

    def draw(self, layer, t, col=None):
        col = col or self.col
        for q in self.p:
            a = t - q["t"]
            if a < 0:
                continue
            if a < q["hold"]:
                FX.paste_c(layer, FX.glyph(q["ch"], q["px"], col, core=1.0, rim=0.9), q["s"][0], q["s"][1])
                continue
            u = (a - q["hold"]) / q["tr"]
            if u >= 1:
                continue
            p = bez(q["s"], q["c"], q["e"], u ** 1.5)
            ch = q["ch"] if int(a / 90) % 2 == 0 else ("1" if q["ch"] == "0" else "0")
            FX.paste_c(layer, FX.glyph(ch, lerp(q["px"], q["px"] * 0.6, u), col, core=max(0, 1 - a / 120), rim=0.9), p[0], p[1],
                       alpha=1 - seg(u, 0.8, 1))


def bars_in(c, r, slot, seed, n=11):
    """Fixed CORRUPTED tear bars inside a slice (screen rects: x0, x1, y, h)."""
    rng = np.random.default_rng(seed)
    out = []
    for k in range(n):
        a = rng.uniform(slot[0] + 6, slot[1] - 6)
        rr = rng.uniform(r * 0.45, r * 0.92)
        x, y = pt(c, rr, a)
        w = rng.uniform(26, 78)
        out.append((x - w / 2, x + w / 2, y, rng.choice([4, 5, 6])))
    return out


def draw_bars(img, bars, c, r, slot, front=None, side="right", alpha=1.0):
    """Bars clipped to the slice; front = wipe x (side='right' keeps x > front, 'left' keeps x < front)."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for x0, x1, y, h in bars:
        if front is not None:
            if side == "right":
                x0 = max(x0, front)
            else:
                x1 = min(x1, front)
        if x1 - x0 < 1:
            continue
        d.rectangle([x0, y - h / 2, x1, y + h / 2], fill=CORRUPT + (int(215 * alpha),))
        d.line([(x0, y - h / 2), (x1, y - h / 2)], fill=(255, 190, 210, int(200 * alpha)), width=1)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).polygon(wedge(c, r * 0.38, r * 0.98, *slot), fill=255)
    lay.putalpha(ImageChops.multiply(lay.split()[3], m))
    img.alpha_composite(lay)


def badge(img, c, size=22, age=None):
    s = size
    body = Image.new("RGBA", (2 * s + 6, 2 * s + 6), (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    q = s + 3
    d.polygon([(q, 2), (2 * s + 4, q), (q, 2 * s + 4), (2, q)], fill=(26, 8, 18, 255), outline=CORRUPT + (255,), width=3)
    g = EB.icon("status_corrupted", int(s * 1.0), CORRUPT, outline=False)
    body.alpha_composite(g, ((body.width - g.width) // 2, (body.height - g.height) // 2))
    st = MC.vinyl(body, border=4, shadow=0.5)
    if age is None:
        FX.place(img, st, c[0], c[1])
    else:
        EB.slap(img, st, c, age, 180)


def front_x(bars, t, t0, t1):
    xs0 = min(b[0] for b in bars) - 8
    xs1 = max(b[1] for b in bars) + 8
    return lerp(xs0, xs1, seg(t, t0, t1)), xs0, xs1


def wipe_bits(bars, t0, t1, target_fn, col_seed, step=10):
    xs0 = min(b[0] for b in bars) - 8
    xs1 = max(b[1] for b in bars) + 8
    rng = np.random.default_rng(col_seed)
    items = []
    for x0, x1, y, h in bars:
        x = x0 + step / 2
        while x < x1:
            tr = t0 + (t1 - t0) * (x - xs0) / (xs1 - xs0)
            e, cc = target_fn(rng, (x, y))
            items.append(dict(s=(x, y), c=cc, e=e, t=tr, tr=rng.uniform(420, 600)))
            x += step
    return items


def gifout(name, frames, durs, crop, size):
    EB.gif(name, frames, durs, crop, size)


# ================================================================== 1 CORRUPTED tick v2
C_SLOT = EB.C_SLOT
P_BARS = bars_in(PC, PR, C_SLOT, 31)
HP_END = EB.arc_seg_poly("player", 19, MP)[1]


def _to_hp(rng, s):
    mid = pt(PC, PR * 1.42, 118)
    return (HP_END[0] + rng.normal(0, 8), HP_END[1] + rng.normal(0, 6)), (mid[0] + rng.normal(0, 40), mid[1] + rng.normal(0, 40))


CT_BITS = Bits(wipe_bits(P_BARS, 300, 640, _to_hp, 5), CORRUPT, px=(20, 26), seed=6)
T_REFORM = (1500, 1800)


def corrupt_tick_v2(t):
    hit = t >= 1000
    img = scene2(p_state=(38, 0) if hit else (41, 0))
    dress(img, hp_p=38 if t >= 1150 else 41, ram=4 if t >= 900 else 5)
    # standing bars; the wipe (300-640 ms) turns them into bits left to right; they re-tear in faintly
    if t < 300:
        draw_bars(img, P_BARS, PC, PR, C_SLOT)
    elif t < 700:
        fx_, _, _ = front_x(P_BARS, t, 300, 640)
        draw_bars(img, P_BARS, PC, PR, C_SLOT, front=fx_, side="right")
    elif t >= T_REFORM[0]:
        fx_, _, _ = front_x(P_BARS, t, *T_REFORM)
        draw_bars(img, P_BARS, PC, PR, C_SLOT, front=fx_, side="left", alpha=0.9)
    badge(img, pt(PC, PR * 0.93, C_SLOT[1] - 8))
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    if 300 <= t < 680:  # the wipe front: a thin bright scan line
        fx_, _, _ = front_x(P_BARS, t, 300, 640)
        m = Image.new("L", img.size, 0)
        ImageDraw.Draw(m).polygon(wedge(PC, PR * 0.38, PR * 0.98, *C_SLOT), fill=255)
        ln = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(ln).rectangle([fx_ - 2, 0, fx_ + 2, H], fill=(255, 220, 235, 230))
        ln.putalpha(ImageChops.multiply(ln.split()[3], m))
        fx.alpha_composite(ln)
    CT_BITS.draw(fx, t)
    if 960 <= t < 1100:
        poly, c = EB.arc_seg_poly("player", 19, MP)
        d.polygon(poly, fill=(255, 255, 255, int(230 * (1 - (t - 960) / 140))))
    DS.tracer(fx, pt(PC, PR * 0.7, 60), (PC[0] + 380, 760), EB.RAM_PIP, seg(t, 600, 880), CORRUPT, width=5)
    EB.RB.draw(fx, t - 880)
    img = EB.emit(img, fx, 0.45)
    pb, eb, _, _ = P.hp_boxes()
    a = pt(PC, PR * 1.3, 100)
    DS.number_pop(img, "-3", CORRUPT, (a[0] + 20, a[1]), ((pb[0] + pb[2]) / 2, (pb[1] + pb[3]) / 2), t - 640, 420, size=60, sub="CORRUPTED")
    EB.chip(img, EB.RAM_PIP[0] + 40, EB.RAM_PIP[1] - 70, "-1 RAM", CORRUPT, None, t - 900, size=24)
    return img


# ================================================================== 2 evade v2
TOKEN = EB.TOKEN
P_PTR = EB.P_PTR
B_BLADE = EB.B_BLADE
T_LIFT = 1000
T_FLY = (1080, 1850)
TOK_END = (-160, -140)
TOK_CTRL = (430, 70)


def token_pos(t):
    if t < T_FLY[0]:
        return TOKEN
    u = seg(t, *T_FLY) ** 1.25
    return bez(TOKEN, TOK_CTRL, TOK_END, u)


A_PATH = (B_BLADE, (980, 60), P_PTR)


def attack_head(t):
    if t < 860:
        return None
    if t < T_LIFT:
        return bez(*A_PATH, 0.82 * seg(t, 860, T_LIFT))
    base = bez(*A_PATH, min(0.9, 0.82 + 0.08 * seg(t, T_LIFT, T_LIFT + 120)))
    w = ease_in_out(seg(t, T_LIFT, T_LIFT + 300))
    tgt = token_pos(t - 170)
    return lerp2(base, tgt, w)


def edge_alpha(p):
    if p is None:
        return 0.0
    return max(0.0, min(1.0, min(p[0], p[1]) / 170.0))


def evade_v2(t):
    if EB.TOK is None:
        EB.TOK = EB.token_sticker()
    if EB.WORD_E is None:
        EB.WORD_E = EB.vinyl_word("EVADED", GREEN, size=54, tilt=5)
    img = scene2()
    dress(img)
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    if 0 <= t < 120:
        d.polygon(wedge(PC, PR * 0.38, PR * 0.98, 270, 330), fill=GREEN + (int(150 * (1 - t / 120)),))
    EB.ES.draw(fx, t)
    # the attack: a comet whose head chases the token once it lifts off
    if t >= 860:
        hist = [attack_head(t - k * 22) for k in range(12)]
        hist = [h for h in hist if h is not None]
        al = edge_alpha(hist[0])
        if al > 0.01 and len(hist) > 1:
            for k in range(len(hist) - 1):
                a = int(255 * al * (1 - k / len(hist)))
                d.line([hist[k], hist[k + 1]], fill=ORANGE + (a,), width=max(3, int(14 * (1 - k / len(hist)))))
            h0 = hist[0]
            d.ellipse([h0[0] - 11, h0[1] - 11, h0[0] + 11, h0[1] + 11], fill=(255, 255, 255, int(255 * al)))
            # it sheds a few orange bits as it chases
            if t > T_LIFT and int(t / 40) % 2 == 0:
                FX.paste_c(fx, FX.glyph("01"[int(t / 80) % 2], 20, ORANGE, rim=0.9), hist[3][0] if len(hist) > 3 else h0[0],
                           hist[3][1] if len(hist) > 3 else h0[1], alpha=0.8 * al)
    img = EB.emit(img, fx, 0.45)
    # token: slaps on, waits, lifts at the hit, then flies off to the top-left, chased; fades at the edge
    if 520 <= t < T_LIFT:
        EB.slap(img, EB.TOK, TOKEN, t - 520, 180)
        if t >= 700:
            EB.chip(img, TOKEN[0] + 44, TOKEN[1] - 4, "EVADE 1", GREEN, None, t - 700, size=20)
    elif t >= T_LIFT:
        p = token_pos(t)
        al = edge_alpha(p)
        if al > 0.01:
            lift = ease_out_back(seg(t, T_LIFT, T_LIFT + 120), 2.0)
            k = 1 + 0.2 * lift
            f = EB.TOK.copy()
            f.putalpha(f.split()[3].point(lambda v: int(v * al)))
            FX.place(img, f, p[0], p[1], k, k, -25 * seg(t, *T_FLY), shadow=((10 * lift + 4, 14 * lift + 6), 8, 0.35 * al))
    if t >= 1300:
        EB.slap(img, EB.WORD_E, (PC[0] + PR * 0.98, PC[1] + PR * 0.5), t - 1300, 200)
    return img


# ================================================================== 3 Heat H1 polish
import heat_alts as HA

LIGHTS2 = [(840, 650), (1110, 610), (720, 890), (1190, 870), (990, 430), (130, 910), (1830, 700), (610, 330), (870, 780),
           (1060, 800), (800, 520), (1130, 500), (300, 470), (1660, 300), (60, 600), (1880, 520), (200, 240), (1300, 960)]
BANDS = [dict(lights=9, alpha=200, r=95, per=820, beams=1, beam_a=40, helis=0, wash=0.05),
         dict(lights=13, alpha=190, r=105, per=650, beams=2, beam_a=48, helis=0, wash=0.08),
         dict(lights=18, alpha=180, r=115, per=480, beams=3, beam_a=54, helis=2, wash=0.11)]


def city_v2(img, t, lvl):
    b = BANDS[lvl]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cores = []
    for i, (x, y) in enumerate(LIGHTS2[:b["lights"]]):
        ph = ((t + i * 137) % b["per"]) / b["per"]
        col = HA.RED if ph < 0.5 else HA.BLUE
        on = 0.55 + 0.45 * math.sin(math.pi * ((ph * 2) % 1))
        r = b["r"]
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=col + (int(b["alpha"] * on),))
        cores.append((x, y, col))
    img = HA.additive(img, lay.filter(ImageFilter.GaussianBlur(26)), 1.0)
    dc = ImageDraw.Draw(img)
    for x, y, col in cores:  # the car light bars themselves
        dc.rectangle([x - 8, y - 3, x + 8, y + 3], fill=col + (255,))
        dc.rectangle([x - 3, y - 1, x + 3, y + 1], fill=(255, 255, 255, 255))
    # a faint red/blue wash over the whole backdrop alternates with the sirens (backdrop only)
    ph = (t % b["per"]) / b["per"]
    wash = Image.new("RGBA", (W, H), (HA.RED if ph < 0.5 else HA.BLUE) + (int(255 * b["wash"]),))
    img = HA.additive(img, wash, 1.0)
    beams = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    db = ImageDraw.Draw(beams)
    for k in range(b["beams"]):
        o = ((520, 1400, 960)[k], -60)
        sweep = math.sin(t / (1700 - 300 * k) + k * 2.0)
        tx = 960 + 230 * sweep
        ty = 520 + 70 * math.cos(t / 1300 + k)
        L = math.hypot(tx - o[0], ty - o[1])
        nx, ny = -(ty - o[1]) / L, (tx - o[0]) / L
        wdt = 75
        db.polygon([(o[0] + nx * 8, o[1] + ny * 8), (o[0] - nx * 8, o[1] - ny * 8), (tx - nx * wdt, ty - ny * wdt), (tx + nx * wdt, ty + ny * wdt)],
                   fill=(255, 245, 220, b["beam_a"]))
        db.ellipse([tx - wdt * 1.15, ty - wdt * 0.58, tx + wdt * 1.15, ty + wdt * 0.58], fill=(255, 245, 220, b["beam_a"] + 34))
    if b["beams"]:
        img = HA.additive(img, beams.filter(ImageFilter.GaussianBlur(10)), 1.0)
    if b["helis"]:
        dh = ImageDraw.Draw(img)
        for (c, f), dx in list(zip(HA.HELIS, (60, -40)))[:b["helis"]]:
            cx = c[0] + dx * math.sin(t / 2000)
            HA.heli(dh, (cx, c[1]), 0.9, t, f)
    return img


def heat_frame(lvl, t):
    img = HA.world(city_v2, t, lvl)
    HA.ui(img)
    HA.heat_chip(img, lvl)
    return img


def heat():
    frames, durs = [], []
    for lvl in range(3):
        for t in range(0, 1680, 120):
            frames.append(heat_frame(lvl, t + lvl * 5000).convert("RGB").resize((960, 540), Image.LANCZOS))
            durs.append(120)
    durs[-1] = 600
    s = FX.save_gif(frames, durs, os.path.join(OUT, "heat_city_v2.gif"))
    print("heat_city_v2.gif", s // 1024, "KB", flush=True)
    cw, ch, gap = 800, 450, 14
    S = Image.new("RGB", (3 * cw + 4 * gap, ch + 150), (14, 13, 20))
    d = ImageDraw.Draw(S)
    d.text((gap, 10), "HEAT H1 v2  -  CITY REACTS (backdrop only)", font=f_num(44), fill=(255, 255, 255))
    for lvl, (heat_, word, col) in enumerate(HA.LEVELS):
        x = gap + lvl * (cw + gap)
        S.paste(heat_frame(lvl, 600 + lvl * 5000).convert("RGB").resize((cw, ch), Image.LANCZOS), (x, 66))
        d.text((x, 66 + ch + 6), "HEAT %d  %s" % (heat_, word), font=f_num(26), fill=col)
        b = BANDS[lvl]
        d.text((x, 66 + ch + 40), "%d police lights (%.2f s), %d searchlight%s%s, %d %% siren wash" % (
            b["lights"], b["per"] / 1000, b["beams"], "" if b["beams"] == 1 else "s", ", 2 helicopters" if b["helis"] else "", int(b["wash"] * 100)),
               font=f_ui(18, b"SemiBold"), fill=(200, 200, 214))
    S.save(os.path.join(OUT, "heat_city_v2_strip.png"), optimize=True)
    print("strip done", flush=True)


# ================================================================== batch 2
# --- a) nudge + resistance absorb (on the boss)
E_BTN = (PC[0] + PR * 1.32, PC[1] + PR * 0.86)
RES_C = (BC[0] - BR * 1.85, BC[1] - BR * 0.8)


def nudge_rot(t):
    if 300 <= t < 620:  # strain against resistance, spring back
        q = seg(t, 300, 620)
        return 3.0 * math.sin(math.pi * min(1, q * 1.6)) * (1 - q) ** 0.5
    if t >= 1300:
        q = seg(t, 1300, 1560)
        return 12 * ease_out_back(q, 1.8)
    return 0.0


def btn_flash(img, c, t0, t):
    a = t - t0
    if 0 <= a < 220:
        d = ImageDraw.Draw(img)
        r = 24 + 16 * ease_out_cubic(a / 220)
        d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=(255, 255, 255, int(255 * (1 - a / 220))), width=4)
        if a < 90:
            d.ellipse([c[0] - 22, c[1] - 22, c[0] + 22, c[1] + 22], fill=(255, 255, 255, 120))


def res_chip(img, t):
    """RESIST 1: a grey shield pip by the boss; it cracks into bits when it eats the tick."""
    if t < 420:
        EB.chip(img, RES_C[0] - 10, RES_C[1], "RESIST 1", GREY, "special_weight", 0, size=22)
    elif t < 1400:
        q = seg(t, 420, 1200)
        EB.chip(img, RES_C[0] - 10, RES_C[1], "RESIST 0", (110, 106, 120), "special_weight", 0, size=22)


RES_BURST = DS.Burst((RES_C[0] + 20, RES_C[1]), -60, 120, 14, (18, 24), (200, 420), GREY, 71, gravity=500, life=(320, 480))


def nudge(t):
    rot = nudge_rot(t)
    v = abs(nudge_rot(t) - nudge_rot(t - 40))
    img = scene2(b_sprite=spin_any("boss", round(rot * 2) / 2, v * 0.6) if rot != 0 else None)
    free = 0 if t >= 300 else 1
    dress(img, status="TURN 3   |   FREE NUDGE %d" % free, ram=4 if t >= 1300 else 5)
    btn_flash(img, E_BTN, 260, t)
    btn_flash(img, E_BTN, 1260, t)
    res_chip(img, t)
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    RES_BURST.draw(fx, t - 420)
    if 1300 <= t < 1900:  # one notch on the ring + a tick trail
        al = 1 - seg(t, 1600, 1900)
        rr = BR * 1.075
        d.arc([BC[0] - rr, BC[1] - rr, BC[0] + rr, BC[1] + rr], -90, -90 + min(12, rot), fill=MC.GP_YELLOW + (int(230 * al),), width=8)
        th = math.radians(-90 + 12)
        d.line([(BC[0] + (rr - 12) * math.cos(th), BC[1] + (rr - 12) * math.sin(th)), (BC[0] + (rr + 12) * math.cos(th), BC[1] + (rr + 12) * math.sin(th))],
               fill=(255, 250, 220, int(255 * al)), width=4)
    img = EB.emit(img, fx, 0.45)
    if 440 <= t < 1300:
        EB.chip(img, BC[0] - BR * 1.85, BC[1] - BR * 0.55, "ABSORBED  0 TICKS", GREY, None, t - 440, size=24)
    if t >= 1320:
        EB.chip(img, BC[0] - BR * 1.85, BC[1] - BR * 0.3, "NUDGE +1   (1 RAM)", YEL, None, t - 1320, size=24)
    return img


# --- b) respin (player wheel)
RESPIN_BTN = (1370 + 50, 1010 + 26)
PIP = lambda i: (30 + 120 + i * 22 + 8, 958 + 47)
SPIN_TOTAL = 720 + 156.0
T_RS = (700, 1900)


def rs_rot(t):
    return SPIN_TOTAL * ease_out_cubic(seg(t, *T_RS)) if t >= T_RS[0] else 0.0


RS_BITS = Bits([dict(s=PIP(i), c=(PIP(i)[0] + 120, 760), e=(PC[0] + np.random.default_rng(i * 7 + k).normal(0, 12), PC[1] + np.random.default_rng(i * 9 + k).normal(0, 12)),
                     t=260 + i * 60 + k * 30, tr=380) for i in range(1, 5) for k in range(3)], RAM_C, px=(22, 28), seed=8)
CHECK = None


def respin(t):
    global CHECK
    if CHECK is None:
        CHECK = EB.vinyl_word("CHECKPOINT", (240, 240, 236), size=40, tilt=-4)
    rot = rs_rot(t)
    v = abs(rot - rs_rot(t - 40))
    if rot == 0:
        ps = None
    elif v > 7:
        ps = spin_any("player", rot, min(60, v * 0.8), cheap=True)
    else:
        ps = spin_any("player", round(rot * 2) / 2 % 360, v * 0.6)
    img = scene2(p_sprite=ps)
    dress(img, ram=1 if t >= 240 else 5, ram_spend=4 if t < 240 else 0)
    btn_flash(img, RESPIN_BTN, 160, t)
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    RS_BITS.draw(fx, t)
    for i in range(1, 5):  # the 4 spent pips crack
        if 240 <= t < 360:
            x, y = PIP(i)
            d.rectangle([x - 8, y - 15, x + 8, y + 15], fill=(255, 255, 255, int(220 * (1 - (t - 240) / 120))))
    if T_RS[0] <= t < T_RS[0] + 220:  # hub kick
        q = seg(t, T_RS[0], T_RS[0] + 220)
        r = PR * lerp(0.35, 1.0, ease_out_cubic(q))
        d.ellipse([PC[0] - r, PC[1] - r, PC[0] + r, PC[1] + r], outline=(200, 245, 255, int(220 * (1 - q))), width=5)
    if T_RS[1] - 40 <= t < T_RS[1] + 260:  # landing ring on the blade window
        q = seg(t, T_RS[1] - 40, T_RS[1] + 260)
        c = (PC[0], PC[1] - PR * 1.26)
        r = 26 + 34 * ease_out_cubic(q)
        d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=(255, 255, 255, int(230 * (1 - q))), width=5)
    img = EB.emit(img, fx, 0.5)
    EB.chip(img, PIP(5)[0] + 60, PIP(5)[1] - 66, "-4 RAM", RAM_C, None, t - 260, size=24)
    if t >= T_RS[1] + 60:
        EB.slap(img, CHECK, (PC[0] + PR * 0.82, PC[1] - PR * 1.18), t - T_RS[1] - 60, 200)
    return img


# --- c) apply CORRUPTED (boss EXPLOIT 14, top slice)
B_SLOT = (-30, 30)
B_BARS = bars_in(BC, BR, B_SLOT, 44, n=12)
CA_BITS = Bits([dict(s=(P.hand_slot(2, 5)[0] + np.random.default_rng(k).normal(0, 40), P.hand_slot(2, 5)[1] + 90 + np.random.default_rng(k + 99).normal(0, 50)),
                     c=(1040 + np.random.default_rng(k + 5).normal(0, 80), 330 + np.random.default_rng(k + 6).normal(0, 60)),
                     e=(BC[0] + np.random.default_rng(k + 7).normal(0, 40), BC[1] - BR * 0.68 + np.random.default_rng(k + 8).normal(0, 22)),
                     t=k * 12, tr=460, hold=0) for k in range(40)], CORRUPT, px=(28, 36), seed=9)


def corrupt_apply(t):
    img = scene2()
    dress(img)
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    CA_BITS.draw(fx, t)
    if 820 <= t < 920:
        d.polygon(wedge(BC, BR * 0.38, BR * 0.98, *B_SLOT), fill=(255, 255, 255, int(170 * (1 - (t - 820) / 100))))
    if 820 <= t < 1160:  # tears write on left to right (the mirror of the tick's wipe)
        fx_, _, _ = front_x(B_BARS, t, 820, 1140)
        m = Image.new("L", img.size, 0)
        ImageDraw.Draw(m).polygon(wedge(BC, BR * 0.38, BR * 0.98, *B_SLOT), fill=255)
        ln = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(ln).rectangle([fx_ - 2, 0, fx_ + 2, H], fill=(255, 220, 235, 230))
        ln.putalpha(ImageChops.multiply(ln.split()[3], m))
        fx.alpha_composite(ln)
    if t >= 820:
        fx_, _, _ = front_x(B_BARS, t, 820, 1140)
        draw_bars(img, B_BARS, BC, BR, B_SLOT, front=fx_, side="left")
    if 820 <= t < 940:
        DS.pixel_tear(img, (int(BC[0] - 140), int(BC[1] - BR * 0.98), int(BC[0] + 140), int(BC[1] - BR * 0.4)), int(t), 1.4)
    img = EB.emit(img, fx, 0.5)
    if t >= 1180:
        badge(img, pt(BC, BR * 0.93, B_SLOT[1] - 8), 24, t - 1180)
        EB.chip(img, BC[0] - BR * 2.0, BC[1] - BR * 0.62, "CORRUPTED: 3 self-dmg, -1 RAM", CORRUPT, "status_corrupted", t - 1260, size=22)
    return img


# --- d) drone destroyed
DOCK = EB.DOCK
P_BLADE = (PC[0], PC[1] - PR * 1.12)
T_IMP = 420
T_POP = 720


def hex_pieces():
    spr = EB.drone_sticker()
    w, h = spr.size
    c = (w / 2, h / 2)
    out = []
    for k in range(6):
        m = Image.new("L", spr.size, 0)
        a0, a1 = math.radians(k * 60 - 90), math.radians(k * 60 - 30)
        ImageDraw.Draw(m).polygon([c, (c[0] + 90 * math.cos(a0), c[1] + 90 * math.sin(a0)), (c[0] + 90 * math.cos(a1), c[1] + 90 * math.sin(a1))], fill=255)
        piece = spr.copy()
        piece.putalpha(ImageChops.multiply(spr.split()[3], m))
        bb = piece.getbbox()
        if bb:
            am = (a0 + a1) / 2
            out.append(dict(im=piece.crop(bb), off=((bb[0] + bb[2]) / 2 - c[0], (bb[1] + bb[3]) / 2 - c[1]), dir=am))
    return spr, out


DRONE_SPR = None
DD_BURST = DS.Burst(DOCK, 200, 360, 34, (24, 34), (260, 620), ORANGE, 81, gravity=420, life=(460, 720))


def drone_destroyed(t):
    global DRONE_SPR
    if DRONE_SPR is None:
        DRONE_SPR = hex_pieces()
    spr, pieces = DRONE_SPR
    img = scene2()
    dress(img, hp_e=340)
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    # the shot is aimed at the boss pointer; the docked drone bends it to itself (bodyguard)
    if t < T_IMP:
        DS.tracer(fx, P_BLADE, (1000, 40), DOCK, seg(t, T_IMP - 260, T_IMP), (255, 120, 215), width=8)
    if T_IMP <= t < T_IMP + 90:
        DS.flash_disc(fx, DOCK, 46, 0.65)
    clamp_in = pt(BC, BR * 1.0, EB.DOCK_A)
    clamp_out = pt(BC, BR * 1.10, EB.DOCK_A)
    if t < T_POP:
        d.line([clamp_in, clamp_out], fill=ORANGE + (255,), width=5)
    elif t < T_POP + 300:  # the clamp springs open
        q = ease_out_back(seg(t, T_POP, T_POP + 200), 2.5)
        a = EB.DOCK_A - 40 * q
        d.line([clamp_in, pt(BC, BR * 1.10, a)], fill=ORANGE + (int(255 * (1 - seg(t, T_POP + 150, T_POP + 300))),), width=5)
    if T_POP <= t < T_POP + 200:
        q = seg(t, T_POP, T_POP + 200)
        r = lerp(30, 130, ease_out_cubic(q))
        d.ellipse([DOCK[0] - r, DOCK[1] - r, DOCK[0] + r, DOCK[1] + r], outline=(255, 220, 170, int(230 * (1 - q))), width=6)
    DD_BURST.draw(fx, t - T_POP)
    img = EB.emit(img, fx, 0.55)
    sh = DS.shake(t, T_IMP, 3, 120, seed=9)
    if t < T_POP:
        s = spr
        if t >= T_IMP:  # cracks grow over the hex
            s = spr.copy()
            ds = ImageDraw.Draw(s)
            g = seg(t, T_IMP, T_POP - 40)
            rng = np.random.default_rng(3)
            c = (s.width / 2, s.height / 2)
            for k in range(5):
                a = rng.uniform(0, 2 * math.pi)
                L = 44 * min(1, g * 1.3)
                ds.line([c, (c[0] + L * math.cos(a), c[1] + L * math.sin(a)), (c[0] + L * 1.2 * math.cos(a + 0.3), c[1] + L * 1.2 * math.sin(a + 0.3))],
                        fill=(255, 255, 255, 255), width=3)
        FX.place(img, s, DOCK[0] + sh[0], DOCK[1] + sh[1])
    else:
        a_ = t - T_POP
        for i, p in enumerate(pieces):
            s_ = a_ / 1000
            sp = 260 + 40 * i
            x = DOCK[0] + p["off"][0] + math.cos(p["dir"]) * sp * s_
            y = DOCK[1] + p["off"][1] + math.sin(p["dir"]) * sp * s_ + 0.5 * 900 * s_ * s_
            al = 1 - seg(a_, 200, 520)
            if al > 0:
                im = p["im"]
                if a_ > 120:
                    k = max(2, int(lerp(1, 8, seg(a_, 120, 500))))
                    im = im.resize((max(1, im.width // k), max(1, im.height // k)), Image.NEAREST).resize(im.size, Image.NEAREST)
                FX.paste_c(img, im, x, y, alpha=al, angle=200 * s_ * (1 if i % 2 else -1))
    if T_IMP <= t < T_POP:
        EB.chip(img, DOCK[0] - 80, DOCK[1] - 74, "DRONE  HP 0", ORANGE, None, t - T_IMP, size=22)
    eb = P.hp_boxes()[1]
    DS.number_pop(img, "-5", (255, 120, 215), (DOCK[0] - 100, DOCK[1] - 10), (DOCK[0] - 60, DOCK[1] - 160), t - T_IMP, 600, size=64, sub="DRONE (BODYGUARD)")
    if t >= T_POP + 200:
        EB.chip(img, DOCK[0] - 120, DOCK[1] + 70, "DRONE DESTROYED", ORANGE, "special_drone", t - T_POP - 200, size=24)
    return img


# --- e) boss phase change (HP crosses 66 %: phase 2, a second needle at tick 15)
def phase_specs():
    import roster as RS
    p1, p2, m = RS.boss_specs("meridian")
    out = []
    for s, hp in ((p1, 270), (p1, 262), (p2, 262)):
        s = copy.deepcopy(s)
        s["hp"] = (hp, m["hp"])
        s["pred"] = 0
        s["key"] = "the_manifest"
        s["hp_number"] = False
        out.append(s)
    return out


PH = None
T_PH_HIT = 240
T_STOP = 120
T_FLIP = (620, 900)
T_NEEDLE = (1100, 1500)


def ph_sprites():
    global PH
    if PH is None:
        a, b, c = phase_specs()
        PH = [wheel_spec("r20_phase1_270", a), wheel_spec("r20_phase1_262", b), wheel_spec("r20_phase2_262", c)]
    return PH


def draw_needle(img, ang, grow, value):
    """The new needle: an orange crowned blade extruding out of the bezel at clock angle `ang`."""
    if grow <= 0:
        return
    L = 34 * grow
    lay = Image.new("RGBA", (140, 190), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx = 70
    y_tip = 186
    y_top = y_tip - 26 - L * 1.25
    poly = [(cx, y_tip), (cx - 26, y_tip - 70), (cx - 32, y_tip - 70), (cx - 32, y_top), (cx + 32, y_top), (cx + 32, y_tip - 70), (cx + 26, y_tip - 70)]
    poly = [(x, max(y, y_top)) for x, y in poly]
    d.polygon(poly, fill=(255, 150, 40, 255), outline=(14, 10, 8, 255))
    s = lay.rotate(-ang, resample=Image.BICUBIC, expand=True)
    mid = pt(BC, BR * 0.93 + 93, ang)
    sd, _ = FX.drop_shadow(s, (6, 10), 5, 0.5)
    img.alpha_composite(sd, (int(mid[0] - sd.width / 2), int(mid[1] - sd.height / 2)))
    if grow > 0.7:  # upright value window beside the blade (the boss HP number sits right below)
        w = pt(BC, BR * 1.12, ang)
        EB.chip(img, w[0] + 34, w[1] - 6, value, (255, 150, 40), None, 0, size=26)


NEEDLE_BITS = Bits([dict(s=(BC[0] + np.random.default_rng(k).normal(0, 30), BC[1] + np.random.default_rng(k + 1).normal(0, 30)),
                         c=(BC[0] + np.random.default_rng(k + 2).normal(0, 140), BC[1] + BR * 0.6),
                         e=pt(BC, BR * 1.05 + np.random.default_rng(k + 3).normal(0, 20), 180 + np.random.default_rng(k + 4).normal(0, 8)),
                         t=T_NEEDLE[0] - 300 + k * 10, tr=300, hold=0) for k in range(24)], ORANGE, px=(22, 30), seed=10)
PHASE_W = None


def phase_change(t_real):
    global PHASE_W
    if PHASE_W is None:
        PHASE_W = EB.vinyl_word("PHASE 2", (255, 150, 40), size=60, tilt=-5)
    sp = ph_sprites()
    t = t_real if t_real < T_PH_HIT else (T_PH_HIT if t_real < T_PH_HIT + T_STOP else t_real - T_STOP)
    if t < T_PH_HIT:
        bs = sp[0]
    elif t < (T_FLIP[0] + T_FLIP[1]) / 2:
        bs = sp[1]
    else:
        bs = sp[2]
    sh = DS.shake(t, T_PH_HIT, 4, 160, seed=4) if t >= T_PH_HIT else (0, 0)
    img = P.city().copy()
    pw, pc, _ = P.wheel("player")
    img.alpha_composite(pw, P.wheel_pos("player", pc))
    bpos = P.wheel_pos("boss", bs[1])
    bim = bs[0]
    # banner flip (scale-y through 0), the swap happens at the midpoint
    cut = int(bs[1][1] - BR * 1.36)
    if T_FLIP[0] <= t < T_FLIP[1]:
        q = seg(t, *T_FLIP)
        k = abs(math.cos(math.pi * q))
        bim = bim.copy()
        top = bim.crop((0, 0, bim.width, cut))
        clear = Image.new("RGBA", (bim.width, cut), (0, 0, 0, 0))
        bim.paste(clear, (0, 0))
        hh = max(1, int(cut * k))
        if hh > 2:
            sq = top.resize((top.width, hh), Image.BILINEAR)
            bim.alpha_composite(sq, (0, int((cut - hh) * 0.8)))
    img.alpha_composite(bim, (bpos[0] + sh[0], bpos[1] + sh[1]))
    img = bloom(img.convert("RGB"), 1, 0.32, 0.66).convert("RGBA")
    hp_e = 270 if t_real < T_PH_HIT + T_STOP + 300 else 262
    dress(img, hp_e=hp_e)
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    imp = (BC[0], BC[1] - BR * 0.74)
    if t < T_PH_HIT:
        DS.tracer(fx, P_BLADE, (960, 60), imp, seg(t, T_PH_HIT - 220, T_PH_HIT), (255, 200, 235), width=8)
    if T_PH_HIT <= t_real < T_PH_HIT + T_STOP + 80:
        d.ellipse([BC[0] - BR * 1.1, BC[1] - BR * 1.1, BC[0] + BR * 1.1, BC[1] + BR * 1.1], fill=(255, 255, 255, int(110 * (1 - seg(t_real, T_PH_HIT, T_PH_HIT + T_STOP + 80)))))
        DS.flash_disc(fx, imp, 50, 0.7)
    # the phase threshold on the HP arc fires: a ring out from the pip
    if T_PH_HIT + 60 <= t < T_PH_HIT + 460:
        q = seg(t, T_PH_HIT + 60, T_PH_HIT + 460)
        a = 230 - 100 * 0.66
        c = P.arc_point("boss", a, bs[2])
        r = lerp(10, 70, ease_out_cubic(q))
        d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=(255, 220, 120, int(255 * (1 - q))), width=5)
    NEEDLE_BITS.draw(fx, t)
    g = ease_out_back(seg(t, *T_NEEDLE), 1.6)
    if T_NEEDLE[0] <= t < T_NEEDLE[0] + 200:
        c = pt(BC, BR * 1.05, 180)
        DS.flash_disc(fx, c, 34, 0.6 * (1 - seg(t, T_NEEDLE[0], T_NEEDLE[0] + 200)))
    img = EB.emit(img, fx, 0.5)
    draw_needle(img, 180, g, "24")
    eb = P.hp_boxes()[1]
    DS.number_pop(img, "-8", (255, 120, 215), (imp[0] + 140, imp[1] - 50), ((eb[0] + eb[2]) / 2, (eb[1] + eb[3]) / 2), t_real - T_PH_HIT - T_STOP, 360, size=64)
    if t >= 1600:
        EB.slap(img, PHASE_W, (BC[0] - BR * 1.05, BC[1] - BR * 1.2), t - 1600, 200)
    if t >= 1760:
        EB.chip(img, BC[0] - BR * 1.55, BC[1] - BR * 0.9, "2 NEEDLES: hits land twice", (255, 150, 40), None, t - 1760, size=22)
    return img


# --- f) RAM gain (turn start, +4)
RG_BITS = Bits([dict(s=(PC[0] + np.random.default_rng(k).normal(0, 16), PC[1] + np.random.default_rng(k + 1).normal(0, 16)),
                     c=(PC[0] - 260 + np.random.default_rng(k + 2).normal(0, 60), PC[1] + 260 + np.random.default_rng(k + 3).normal(0, 40)),
                     e=PIP(1 + k // 4), t=200 + k * 30, tr=420, hold=40) for k in range(16)], RAM_C, px=(30, 38), seed=12)


def ram_gain(t):
    n_on = 1
    for i in range(1, 5):
        if t >= max(q["t"] + q["hold"] + q["tr"] for q in RG_BITS.p[(i - 1) * 4:i * 4]):
            n_on = i + 1
    img = scene2()
    dress(img, status="TURN 4   |   FREE NUDGE 1", ram=n_on)
    fx = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fx)
    if 0 <= t < 260:  # the core pulses at turn start
        q = t / 260
        r = PR * lerp(0.2, 0.42, q)
        d.ellipse([PC[0] - r, PC[1] - r, PC[0] + r, PC[1] + r], outline=RAM_C + (int(230 * (1 - q)),), width=6)
    RG_BITS.draw(fx, t)
    for i in range(1, 5):
        ta = max(q["t"] + q["hold"] + q["tr"] for q in RG_BITS.p[(i - 1) * 4:i * 4])
        if ta <= t < ta + 200:
            x, y = PIP(i)
            fl = 1 - (t - ta) / 200
            d.rectangle([x - 10, y - 18, x + 10, y + 18], fill=(255, 255, 255, int(255 * fl)))
            d.ellipse([x - 26, y - 26, x + 26, y + 26], outline=RAM_C + (int(200 * fl),), width=3)
    if t >= 1300:  # the meter plate glows once full
        q = seg(t, 1300, 1700)
        d.rounded_rectangle([28, 956, 432, 1052], radius=10, outline=RAM_C + (int(200 * (1 - q)),), width=6)
    img = EB.emit(img, fx, 0.6)
    if t >= 1250:
        DS.number_pop(img, "+4 RAM", RAM_C, (300, 900), (300, 900), t - 1250, 2000, size=50)
    return img


# ------------------------------------------------------------------ run
BATCH2 = {
    "nudge_resist": (nudge, 2200, DS.GIF_CROP, (960, 540),
                     [(300, "E PRESSED (FREE)", BC), (520, "ABSORBED", BC), (1360, "NUDGE +1 (1 RAM)", BC), (1700, "LANDED 1 TICK", BC)],
                     [["Free nudge spent; the boss wheel", "strains 3 deg against RESIST 1."],
                      ["It springs back; the resist pip cracks", "into grey bits: ABSORBED, 0 ticks."],
                      ["Second press costs 1 RAM: one 12 deg", "step with overshoot (out-back 1.8)."],
                      ["Yellow notch + 1-tick trail on the", "telemetry ring, then it fades."]]),
    "respin": (respin, 2600, DS.GIF_CROP, (960, 540),
               [(320, "4 RAM PAID", (420, 760)), (800, "SPIN UP", PC), (1400, "SETTLING", PC), (2120, "CHECKPOINT", PC)],
               [["RESPIN pressed: 4 pips flash, crack,", "and stream as cyan bits into the hub."],
                ["Hub kick ring; 2 turns + 13 ticks", "(876 deg) ease-out, blur by speed."],
                ["Real renders take over below 7", "deg/frame so glyphs stay upright."],
                ["Landing ring on the blade window;", "CHECKPOINT vinyl slaps on (no undo past)."]]),
    "corrupt_apply": (corrupt_apply, 2200, DS.GIF_CROP, (960, 540),
                      [(300, "VIOLET STREAM", (1100, 520)), (920, "FLASH + TEAR ON", BC), (1080, "BARS WRITE L->R", BC), (1500, "BADGE + RULE CHIP", BC)],
                      [["CORRUPT PACKET's bits arc from the", "hand to the slice under the needle."],
                       ["White flash, 120 ms pixel tear on", "the slice."],
                       ["Tear bars write on left to right", "(the mirror of the tick's wipe)."],
                       ["Diamond badge slaps on the outer", "corner; the rule chip explains it."]]),
    "drone_destroyed": (drone_destroyed, 2000, DS.GIF_CROP, (960, 540),
                        [(300, "SHOT BENDS TO DRONE", (1000, 300)), (560, "CRACKS", DOCK), (840, "POP", DOCK), (1200, "DESTROYED", DOCK)],
                        [["Aimed at the needle, the shot bends", "to the docked drone (bodyguard)."],
                         ["Flash, shake 3 px; white cracks grow", "over the hex; HP 0 chip."],
                         ["Hex splits in 6, shockwave, 34 big", "orange 0/1; the clamp springs open."],
                         ["Pieces pixelate and fall; DRONE", "DESTROYED chip; -5 number."]]),
    "phase_change": (phase_change, 2800, (900, 0, 1920, 1000), (612, 600),
                     [(260, "HIT-STOP", BC), (760, "BANNER FLIPS", BC), (1300, "NEW NEEDLE", BC), (2000, "PHASE 2", BC)],
                     [["HP crosses 66 %: 120 ms hit-stop,", "white flash; the phase pip rings."],
                      ["The banner flips (scale-y through 0)", "from PHASE 1 to PHASE 2."],
                      ["Orange bits pour to the bezel; a", "crowned needle extrudes at tick 15."],
                      ["PHASE 2 vinyl + rule chip: hits now", "land at both needles."]]),
    "ram_gain": (ram_gain, 2000, (0, 330, 960, 1080), (692, 540),
                 [(160, "CORE PULSE", (430, 760)), (560, "BITS TO PIPS", (430, 760)), (900, "PIPS FILL", (430, 760)), (1500, "+4 RAM", (430, 760))],
                 [["Turn start: the class core pulses", "cyan (RAM comes from the core)."],
                  ["16 cyan 0/1 swing down and round", "into the RAM meter, 4 per pip."],
                  ["Each pip flashes white -> cyan as", "its bits land (left to right)."],
                  ["The plate glows once; +4 RAM rises.", "Reduce effects: pips fill, number only."]]),
}


def run(name, table):
    fn, T, crop, size, keys, caps = table[name]
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
            cells.append((img.convert("RGB").crop((x0, y0, x0 + w, y0 + h)).resize((475, 400), Image.LANCZOS),
                          "%s  %s" % (name.upper().replace("_", " "), k[1]), "%d ms" % t, caps[ki]))
    gifout("fx_%s.gif" % name, frames, durs, crop, size)
    return cells


def batch2():
    cells = []
    for n in BATCH2:
        cells += run(n, BATCH2)
    FX.storyboard(cells, os.path.join(OUT, "fx_batch2_storyboard.png"),
                  "COMBAT FX  -  batch 2 (nudge + resistance, respin, apply CORRUPTED, drone destroyed, boss phase, RAM gain)",
                  "4 key frames per effect (crops of the 1920x1080 D4 screen at 0.625). Same language as batch 1; glyph bursts 22-34 px so they read full-screen.",
                  cols=4,
                  note_lines=["tiers: nudge, respin, RAM gain T1-T2; apply CORRUPTED, drone destroyed T2; boss phase change T3 (hit-stop + banner + needle).",
                              "reduce effects: no streams/bursts/blur; wheels step to their end rotation in one 120 ms tween; chips, badges and needles appear with a 1-frame outline."])


SINGLE = {
    "corrupt_tick_v2": (corrupt_tick_v2, 2000, (40, 120, 920, 1080), (642, 700),
                        [(200, "STANDING", PC), (480, "WIPE L->R", PC), (900, "BITS -> HP", PC), (1700, "RE-TEAR", PC)],
                        [[""], [""], [""], [""]]),
    "evade_v2": (evade_v2, 2400, (0, 0, 1920, 1080), (960, 540),
                 [(600, "TOKEN", PC), (1100, "LIFT", PC), (1500, "CHASE", (500, 300)), (2000, "GONE", (500, 300))], [[""], [""], [""], [""]]),
}


if __name__ == "__main__":
    args = sys.argv[1:] or ["corrupt_tick_v2", "evade_v2", "heat", "batch2"]
    if args[0] == "test":
        name = args[1]
        fn = (BATCH2.get(name) or SINGLE.get(name))[0]
        for a in args[2:]:
            fn(int(a)).convert("RGB").save(os.path.join(P.SCR, "t_%s_%s.png" % (name, a)))
            print("test", name, a, flush=True)
        sys.exit()
    for a in args:
        if a in SINGLE:
            run(a, SINGLE)
        elif a == "heat":
            heat()
        elif a == "batch2":
            batch2()
        elif a in BATCH2:
            run(a, BATCH2)
