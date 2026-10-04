"""Round 19 / 4: non-intrusive but obvious ways to show HEAT on the combat screen (the round 18 glitch stays
an option).

H1 CITY REACTS      the backdrop: police light spill, searchlights on the target building, helicopters
H2 FRAME GAUGE      a thermometer arc built into the player wheel's frame + the bezel warms
H3 TELEMETRY        the player's telemetry ring text turns into warnings (TRACE n% // FLAGGED //)
H4 SIREN SPILL      red / blue ambient light pulsing in from the screen edges
H5 TRACE LINE       a corp-colour trace line creeps round the screen border (length = Heat)

python heat_alts.py          # heat_alternatives.png + heat_city.gif + heat_trace.gif
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
from fxlib import seg, lerp, ease_in_out
from slicelib import f_num, f_ui, f_mono, bloom
from card_play import card_face

OUT = P.OUT
W, H = 1920, 1080
LEVELS = [(31, "NOTICED", (255, 190, 60)), (58, "FLAGGED", (255, 120, 48)), (82, "HUNTED", (255, 50, 60))]
RED, BLUE = (255, 40, 60), (60, 110, 255)
PC, PR = P.PLAYER["c"], P.PLAYER["r"]


def pt(c, r, a):
    return (c[0] + r * math.sin(math.radians(a)), c[1] - r * math.cos(math.radians(a)))


def additive(img, lay, k=1.0):
    a = np.asarray(lay, np.float32) / 255
    add = a[..., :3] * a[..., 3:] * k
    base = np.asarray(img.convert("RGB"), np.float32) / 255
    out = Image.fromarray((np.clip(base + add, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    return out


def world(city_fx=None, t=0, lvl=0):
    img = P.city().copy()
    if city_fx:
        img = city_fx(img, t, lvl)
    for kind in ("player", "boss"):
        w, c, _ = P.wheel(kind)
        img.alpha_composite(w, P.wheel_pos(kind, c))
    return bloom(img.convert("RGB"), 1, 0.32, 0.66).convert("RGBA")


def ui(img):
    P.hud(img)
    P.stickers(img)
    for i in range(5):
        x, y, r = P.hand_slot(i, 5)
        FX.place(img, card_face(i, 144, 192), x, y + 96, 1, 1, r, shadow=((3, 5), 3, 0.55))


def heat_chip(img, lvl):
    heat, word, col = LEVELS[lvl]
    d = ImageDraw.Draw(img)
    x, y, w = 760, 84, 400
    d.rounded_rectangle([x, y, x + w, y + 44], radius=8, fill=(10, 9, 15, 235), outline=col + (200,), width=2)
    d.text((x + 14, y + 4), "HEAT", font=f_num(30), fill=(255, 255, 255, 255))
    d.text((x + 82, y + 4), "%d" % heat, font=f_num(30), fill=col + (255,))
    bx0, bx1, by = x + 130, x + 290, y + 22
    d.rounded_rectangle([bx0, by - 6, bx1, by + 6], radius=4, fill=(40, 36, 46, 255))
    d.rounded_rectangle([bx0, by - 6, bx0 + (bx1 - bx0) * heat / 100, by + 6], radius=4, fill=col + (255,))
    for th in (25, 50, 75):
        tx = bx0 + (bx1 - bx0) * th / 100
        d.line([(tx, by - 10), (tx, by + 10)], fill=(255, 255, 255, 255), width=2)
    d.text((x + 302, y + 10), word, font=f_ui(20, b"Bold Condensed"), fill=col + (255,))


# ------------------------------------------------------------------ H1 city reacts
LIGHTS = [(840, 650), (1110, 610), (720, 890), (1190, 870), (990, 430), (130, 910), (1830, 700), (610, 330), (1300, 960),
          (300, 470), (1660, 300), (930, 980)]
HELIS = [((520, 190), 1), ((1180, 240), -1)]


def heli(d, c, s, t, facing):
    x, y = c
    k = facing
    d.ellipse([x - 34 * s, y - 13 * s, x + 30 * s, y + 13 * s], fill=(8, 8, 12, 255))
    d.polygon([(x - 30 * k * s, y - 4 * s), (x - 92 * k * s, y - 8 * s), (x - 92 * k * s, y + 2 * s), (x - 30 * k * s, y + 6 * s)], fill=(8, 8, 12, 255))
    d.line([(x - 96 * k * s, y - 18 * s), (x - 88 * k * s, y + 8 * s)], fill=(8, 8, 12, 255), width=int(3 * s))
    ph = (t / 60) % 2
    d.line([(x - 60 * s * (1 - ph), y - 20 * s), (x + 60 * s * (1 - ph), y - 20 * s)], fill=(30, 30, 38, 255), width=int(3 * s))
    d.line([(x, y - 13 * s), (x, y - 20 * s)], fill=(8, 8, 12, 255), width=int(3 * s))
    if int(t / 400) % 2 == 0:
        d.ellipse([x - 4, y + 8 * s, x + 4, y + 16 * s], fill=(255, 40, 40, 255))


def city_reacts(img, t, lvl):
    n_l = (5, 8, 12)[lvl]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i, (x, y) in enumerate(LIGHTS[:n_l]):
        per = (900, 700, 500)[lvl]
        ph = ((t + i * 137) % per) / per
        col = RED if ph < 0.5 else BLUE
        on = 0.55 + 0.45 * math.sin(math.pi * ((ph * 2) % 1))
        r = 70 + 20 * lvl
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=col + (int((150, 130, 120)[lvl] * on),))
    lay = lay.filter(ImageFilter.GaussianBlur(26))
    cores = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dc = ImageDraw.Draw(cores)
    for i, (x, y) in enumerate(LIGHTS[:n_l]):
        per = (900, 700, 500)[lvl]
        ph = ((t + i * 137) % per) / per
        col = RED if ph < 0.5 else BLUE
        dc.rectangle([x - 6, y - 3, x + 6, y + 3], fill=col + (255,))
    img = additive(img, lay, 1.0)
    img.alpha_composite(cores)
    # searchlights on the target building (none at NOTICED... one at FLAGGED, two at HUNTED)
    n_b = (0, 1, 2)[lvl] if lvl > 0 else 0
    if lvl == 0:
        n_b = 0
    beams = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    db = ImageDraw.Draw(beams)
    for k in range(n_b):
        o = (520 + 900 * k, -60)
        sweep = math.sin(t / (1700 - 400 * k) + k * 2.0)
        tx = 960 + 220 * sweep
        ty = 520 + 60 * math.cos(t / 1300 + k)
        L = math.hypot(tx - o[0], ty - o[1])
        nx, ny = -(ty - o[1]) / L, (tx - o[0]) / L
        wdt = 70
        db.polygon([(o[0] + nx * 8, o[1] + ny * 8), (o[0] - nx * 8, o[1] - ny * 8), (tx - nx * wdt, ty - ny * wdt), (tx + nx * wdt, ty + ny * wdt)],
                   fill=(255, 245, 220, 46))
        db.ellipse([tx - wdt * 1.1, ty - wdt * 0.55, tx + wdt * 1.1, ty + wdt * 0.55], fill=(255, 245, 220, 70))
    if n_b:
        img = additive(img, beams.filter(ImageFilter.GaussianBlur(10)), 1.0)
    if lvl == 2:
        dh = ImageDraw.Draw(img)
        for (c, f), dx in zip(HELIS, (60, -40)):
            cx = c[0] + dx * math.sin(t / 2000)
            heli(dh, (cx, c[1]), 0.9, t, f)
    return img


# ------------------------------------------------------------------ H2 frame gauge
def frame_gauge(img, t, lvl):
    heat, word, col = LEVELS[lvl]
    d = ImageDraw.Draw(img)
    a0, a1 = 228, 318
    r = PR * 1.36
    track = [pt(PC, r, a0 + (a1 - a0) * i / 40) for i in range(41)]
    d.line(track, fill=(20, 18, 26, 255), width=16, joint="curve")
    d.line(track, fill=(60, 56, 70, 255), width=10, joint="curve")
    fill_to = a0 + (a1 - a0) * heat / 100
    n = int(40 * heat / 100)
    for i in range(n):
        u = i / 40
        c = tuple(int(lerp(lerp(90, 255, min(1, u * 2)), lerp(255, 255, u), 0)) for _ in range(1))
        cc = (int(lerp(92, 255, min(1, u * 1.6))), int(lerp(225, 50, u)), int(lerp(255, 60, u)))
        d.line([track[i], track[i + 1]], fill=cc + (255,), width=10)
    for th in (25, 50, 75):
        a = a0 + (a1 - a0) * th / 100
        d.line([pt(PC, r - 13, a), pt(PC, r + 13, a)], fill=(255, 255, 255, 255), width=3)
    b = pt(PC, r, a0)
    d.ellipse([b[0] - 16, b[1] - 16, b[0] + 16, b[1] + 16], fill=(20, 18, 26, 255))
    d.ellipse([b[0] - 11, b[1] - 11, b[0] + 11, b[1] + 11], fill=(92, 225, 255, 255))
    tip = pt(PC, r, fill_to)
    d.ellipse([tip[0] - 8, tip[1] - 8, tip[0] + 8, tip[1] + 8], fill=col + (255,), outline=(255, 255, 255, 255), width=2)
    lp = pt(PC, r + 46, 268)
    d.text((lp[0] - 40, lp[1] - 14), "HEAT %d" % heat, font=f_num(26), fill=col + (255,), stroke_width=2, stroke_fill=(8, 8, 12, 255))
    # the bezel warms: a heat-colour glow on the rim (stronger per band)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([PC[0] - PR * 1.05, PC[1] - PR * 1.05, PC[0] + PR * 1.05, PC[1] + PR * 1.05], outline=col + (int(90 + 60 * lvl),), width=10)
    pulse = 0.75 + 0.25 * math.sin(t / 300)
    return additive(img, g.filter(ImageFilter.GaussianBlur(9)), (0.6 + 0.4 * lvl) * pulse)


# ------------------------------------------------------------------ H3 telemetry warnings
def telemetry(img, t, lvl):
    heat, word, col = LEVELS[lvl]
    span = (60, 110, 170)[lvl]
    a_mid = 270
    a0, a1 = a_mid - span / 2, a_mid + span / 2
    r = PR * 1.075
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    band = [pt(PC, r, a0 + (a1 - a0) * i / 60) for i in range(61)]
    d.line(band, fill=col + (255,), width=30, joint="curve")
    d.line([pt(PC, r - 15, a0 + (a1 - a0) * i / 60) for i in range(61)], fill=(10, 8, 12, 255), width=3)
    d.line([pt(PC, r + 15, a0 + (a1 - a0) * i / 60) for i in range(61)], fill=(10, 8, 12, 255), width=3)
    text = ("TRACE %d%% // %s // " % (heat, word)) * 6
    f = f_num(20)
    blink = lvl < 2 or int(t / 350) % 2 == 0
    a = a0 + 2 - (t / 40) % 10
    i = 0
    while a < a1 - 2 and i < len(text):
        ch = text[i]
        p = pt(PC, r, a)
        g = Image.new("RGBA", (22, 26), (0, 0, 0, 0))
        ImageDraw.Draw(g).text((4, -1), ch, font=f, fill=((10, 8, 12) if blink else (255, 255, 255)) + (255,))
        g = g.rotate(-(a + 90) + 180, resample=Image.BICUBIC, expand=True)
        if a > a0 + 1:
            lay.alpha_composite(g, (int(p[0] - g.width / 2), int(p[1] - g.height / 2)))
        a += 11.5 * 360 / (2 * math.pi * r)
        i += 1
    img.alpha_composite(lay)
    return img


# ------------------------------------------------------------------ H4 siren spill
_EDGE = {}


def siren(img, t, lvl):
    if "m" not in _EDGE:
        xx = np.linspace(0, 1, W, dtype=np.float32)[None, :]
        yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
        _EDGE["l"] = np.clip(1 - xx / 0.22, 0, 1) ** 2 * (1 - 0.3 * np.abs(yy - 0.5))
        _EDGE["r"] = np.clip((xx - 0.78) / 0.22, 0, 1) ** 2 * (1 - 0.3 * np.abs(yy - 0.5))
        _EDGE["m"] = 1
    k = (0.26, 0.36, 0.48)[lvl]
    per = (1400, 900, 550)[lvl]
    ph = (t % per) / per
    al = 0.5 + 0.5 * math.cos(2 * math.pi * ph)
    ar = 1 - al
    base = np.asarray(img.convert("RGB"), np.float32) / 255
    add = (_EDGE["l"][..., None] * np.array(RED, np.float32) / 255 * al + _EDGE["r"][..., None] * np.array(BLUE, np.float32) / 255 * ar) * k
    return Image.fromarray((np.clip(base + add, 0, 1) * 255).astype(np.uint8)).convert("RGBA")


# ------------------------------------------------------------------ H5 trace line
def trace(img, t, lvl, heat=None):
    hv, word, col = LEVELS[lvl]
    heat = hv if heat is None else heat
    m = 10
    per = [(W / 2, m), (W - m, m), (W - m, H - m), (m, H - m), (m, m), (W / 2, m)]
    total = 2 * (W - 2 * m) + 2 * (H - 2 * m)
    want = total * heat / 100
    pts, acc = [per[0]], 0.0
    head = per[0]
    for a, b in zip(per, per[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if acc + L >= want:
            u = (want - acc) / L
            head = (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
            pts.append(head)
            break
        pts.append(b)
        acc += L
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.line([(x, y) for x, y in [per[0]] + per[1:]], fill=(60, 56, 70, 110), width=3)
    d.line(pts, fill=col + (255,), width=9, joint="curve")
    pulse = 0.6 + 0.4 * math.sin(t / (220 - 50 * lvl))
    r = 12 + 6 * pulse
    d.ellipse([head[0] - r, head[1] - r, head[0] + r, head[1] + r], fill=(255, 255, 255, 255))
    for th in (25, 50, 75):
        want2 = total * th / 100
        acc2 = 0.0
        for a, b in zip(per, per[1:]):
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            if acc2 + L >= want2:
                u = (want2 - acc2) / L
                q = (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
                d.rectangle([q[0] - 6, q[1] - 6, q[0] + 6, q[1] + 6], outline=(255, 255, 255, 220), width=2)
                break
            acc2 += L
    img = additive(img, lay.filter(ImageFilter.GaussianBlur(8)), 0.9)
    img.alpha_composite(lay)
    return img  # no label: the HEAT chip carries the number (a label at the head would sit on HUD panels)
    d2 = ImageDraw.Draw(img)
    f = f_num(26)
    s = "TRACE %d%%  %s" % (heat, word)
    tw = f.getlength(s)
    tx = min(max(20, head[0] - tw / 2), W - tw - 40)
    ty = min(max(20, head[1] + 18), H - 60)
    if head[1] > H - 40:
        ty = head[1] - 54
    d2.rounded_rectangle([tx - 10, ty, tx + tw + 10, ty + 38], radius=6, fill=(10, 9, 15, 235), outline=col + (255,), width=2)
    d2.text((tx, ty + 2), s, font=f, fill=col + (255,))
    return img


OPTS = [
    ("H1  CITY REACTS", "police light spill, searchlights sweep the target building, helicopters at HUNTED (backdrop only)", "city"),
    ("H2  FRAME GAUGE", "thermometer arc in the player wheel's frame, 3 threshold ticks; the bezel warms", "post"),
    ("H3  TELEMETRY WARNINGS", "your telemetry ring text turns into TRACE n% // band // warnings, more ring per band", "post"),
    ("H4  SIREN SPILL", "red / blue light pulses in from the screen edges; brighter and faster per band", "post"),
    ("H5  TRACE LINE", "a trace line creeps round the screen border: its length IS the Heat (25/50/75 marks)", "post"),
]
FNS = [city_reacts, frame_gauge, telemetry, siren, trace]


def render(opt, lvl, t=600):
    if opt == 0:
        img = world(city_reacts, t, lvl)
        ui(img)
    else:
        img = world()
        if opt == 3:
            img = siren(img, t, lvl)
        ui(img)
        if opt in (1, 2):
            img = FNS[opt](img, t, lvl)
        if opt == 4:
            img = trace(img, t, lvl)
    heat_chip(img, lvl)
    return img


def sheet():
    cw, ch = 576, 324
    gap = 14
    lab_w = 300
    head = 136
    Wd = lab_w + 3 * (cw + gap) + gap
    Hd = head + len(OPTS) * (ch + gap) + 140
    S = Image.new("RGB", (Wd, Hd), (14, 13, 20))
    d = ImageDraw.Draw(S)
    d.text((gap, 12), "HEAT ON THE COMBAT SCREEN  -  5 non-intrusive alternatives  x  3 Heat bands", font=f_num(48), fill=(255, 255, 255))
    d.text((gap, 70), "Same D4 screen; the HEAT chip (top centre) is in every cell. None of these touches a slice value, HP number or card.",
           font=P.mono(19), fill=(170, 170, 188))
    for j, (heat, word, col) in enumerate(LEVELS):
        d.text((lab_w + gap + j * (cw + gap), head - 30), "HEAT %d  %s" % (heat, word), font=f_num(26), fill=col)
    for i, (name, desc, kind) in enumerate(OPTS):
        y = head + i * (ch + gap)
        d.rectangle([gap, y + 4, gap + 6, y + 40], fill=(255, 61, 168))
        d.text((gap + 16, y), name, font=f_num(30), fill=(255, 214, 64) if i == 0 else (255, 255, 255))
        words, lines, cur = desc.split(), [], ""
        fo = f_ui(19, b"SemiBold")
        for w_ in words:
            if fo.getlength((cur + " " + w_).strip()) > lab_w - 30:
                lines.append(cur)
                cur = w_
            else:
                cur = (cur + " " + w_).strip()
        lines.append(cur)
        for k, ln in enumerate(lines):
            d.text((gap + 16, y + 46 + k * 24), ln, font=fo, fill=(200, 200, 214))
        for j in range(3):
            im = render(i, j).convert("RGB").resize((cw, ch), Image.LANCZOS)
            S.paste(im, (lab_w + gap + j * (cw + gap), y))
        print("row", i, flush=True)
    y = head + len(OPTS) * (ch + gap) + 10
    for k, ln in enumerate([
        "RECOMMENDED: H1 CITY REACTS (yellow). It is diegetic (the city is hunting you), obvious at a glance at every band, and lives entirely on the",
        "backdrop layer behind the wheels, so it can never hide a value. H5 (border trace) is its quiet numeric twin. The screen glitch stays an Options extra.",
        "Gifs: heat_city.gif (H1) and heat_trace.gif (H5) run NOTICED -> FLAGGED -> HUNTED."]):
        d.text((gap, y + k * 28), ln, font=P.mono(20), fill=(255, 214, 64) if k < 2 else (190, 190, 205))
    S.save(os.path.join(OUT, "heat_alternatives.png"), optimize=True)
    print("sheet", S.size, flush=True)


def gif(opt, name, step=80, seg_ms=1600):
    frames, durs = [], []
    for lvl in range(3):
        for t in range(0, seg_ms, step):
            img = render(opt, lvl, t + lvl * 5000)
            frames.append(img.convert("RGB").resize((960, 540), Image.LANCZOS))
            durs.append(step)
    durs[-1] = 600
    s = FX.save_gif(frames, durs, os.path.join(OUT, name))
    print(name, s // 1024, "KB", flush=True)


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what == "test":
        for i in range(5):
            for j in (0, 2):
                render(i, j).convert("RGB").save(os.path.join(P.SCR, "ha_%d_%d.png" % (i, j)))
        print("test done")
    if what in ("all", "sheet"):
        sheet()
    if what in ("all", "gifs"):
        gif(0, "heat_city.gif")
        gif(4, "heat_trace.gif")
