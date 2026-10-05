"""Round 38 build: python make_sat.py sheet | gif   (renders cached in ../scratch/r)"""
import copy
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
SCR = os.path.join(OUT, "scratch")
RC = os.path.join(SCR, "r")

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import sat as SA
import specs14 as S
import roster as RS
import d4corp as D
from frames import INK
from slicelib import f_num, f_ui, f_mono, R_OUT

BG = (16, 15, 22)
YEL = (255, 214, 64)
WHITE = (255, 255, 255)


def botnet():
    s, m = RS.class_spec("botnet")
    s = copy.deepcopy(s)
    s["key"] = "botnet"
    s["drones"] = []
    s["hp"] = (38, 45)
    return s


def care_swarm():
    s = S.enemy("care_swarm", "solace", "regular")[0]
    s["drones"] = []
    return s


P_SATS = [(1, SA.BOTNET_DRONE), (3, SA.BOTNET_DRONE)]           # Botnet: drones on the two DEPLOY slices
E_SATS = [(0, SA.CARE_DRONE), (2, SA.CARE_DRONE), (4, SA.CARE_DRONE)]  # Care Swarm: 3 satellites


def cached(name, fn):
    os.makedirs(RC, exist_ok=True)
    p, j = os.path.join(RC, name + ".png"), os.path.join(RC, name + ".json")
    if os.path.exists(p):
        m = json.load(open(j))
        return Image.open(p).convert("RGBA"), tuple(m["c"]), m["meta"]
    im, c, meta = fn()
    im.save(p)
    json.dump(dict(c=c, meta={k: v for k, v in meta.items() if k != "bb"}), open(j, "w"))
    print("rendered", name, flush=True)
    return im, c, meta


def city(w, h, seed=3, k=0.30):
    src = Image.open(os.path.join(OUT, "..", "round6_city_restyle", "views", "restyle_night_full.png")).convert("RGB")
    rng = np.random.default_rng(seed)
    x = int(rng.integers(0, src.width - w))
    y = int(rng.integers(0, src.height - h))
    t = src.crop((x, y, x + w, y + h)).filter(ImageFilter.GaussianBlur(3))
    return Image.fromarray((np.asarray(t, np.float32) * k).astype(np.uint8)).convert("RGBA")


def label(d, xy, text, sub=None, col=WHITE, anchor="lm", size=20):
    f = f_num(size)
    fs = f_ui(13, b"Bold SemiCondensed")
    tw = max(f.getlength(text), fs.getlength(sub) if sub else 0)
    h = size + (18 if sub else 0) + 10
    x, y = xy
    x0 = x if anchor == "lm" else (x - tw - 16 if anchor == "rm" else x - tw / 2 - 8)
    y0 = y - h / 2
    d.rounded_rectangle([x0, y0, x0 + tw + 16, y0 + h], radius=6, fill=(10, 9, 16, 235), outline=col, width=2)
    d.text((x0 + 8, y0 + 3), text, font=f, fill=col)
    if sub:
        d.text((x0 + 8, y0 + size + 5), sub, font=fs, fill=(200, 200, 215))


def leader(d, p0, p1, col=WHITE):
    d.line([p0, p1], fill=INK, width=5)
    d.line([p0, p1], fill=col, width=2)
    d.ellipse([p0[0] - 4, p0[1] - 4, p0[0] + 4, p0[1] + 4], fill=col)


def fit_into(sheet, im, c, box, valign=0.5):
    x0, y0, x1, y1 = box
    k = min((x1 - x0) / im.width, (y1 - y0) / im.height, 1.0)
    im2 = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    ox = int(x0 + (x1 - x0 - im2.width) / 2)
    oy = int(y0 + (y1 - y0 - im2.height) * valign)
    sheet.alpha_composite(im2, (ox, oy))
    return ox + c[0] * k, oy + c[1] * k, k


def sat_pos(c, meta, i, rot=0.0, k=1.0, N=0):
    a = 60 * i + SA.DOCK_OFF + rot + 12 * N
    return (c[0] + meta["Rd"] * math.sin(math.radians(a)) * 1, c[1] - meta["Rd"] * math.cos(math.radians(a)))


# ================================================================== sheet
def sheet():
    W, H = 1920, 1560
    Sh = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(Sh)
    d.rectangle([0, 0, 8, 64], fill=YEL)
    d.text((26, 6), "SATELLITES  -  docked mini-wheels (D4 + C slices)", font=f_num(44), fill=WHITE)
    d.text((26, 56), "GDD 2.7: a satellite docks on one slice and rides it; own mini-wheel, pointer, intent and HP; resolves after its host; "
                     "nudged on its own; takes a pointer attack aimed at its slice (bodyguard).", font=f_mono(14, False), fill=(185, 185, 200))
    pb, eb = botnet(), care_swarm()
    # ---- row 1: hero hosts at r = 220
    for k, (name, spec, sats, title) in enumerate((
            ("p220", pb, P_SATS, "PLAYER  BOTNET  r = 220  -  2 drones (5 HP; ATK 3 / DEF 3) on the DEPLOY slices"),
            ("e220", eb, E_SATS, "ENEMY  CARE SWARM (Solace)  r = 220  -  3 Care Drones (4 HP; ATK 3 / ATK 3 / DEF 2)"))):
        x0 = 10 + k * 645
        Sh.alpha_composite(city(635, 760, 20 + k), (x0, 84))
        im, c, meta = cached(name, lambda spec=spec, sats=sats: SA.compose(spec, sats, 220, hp_number=True))
        cx, cy, kk = fit_into(Sh, im, c, (x0 + 4, 116, x0 + 631, 840))
        d.text((x0 + 10, 90), title, font=f_ui(15, b"Bold SemiCondensed"), fill=WHITE)
    # ---- right column: anatomy + r = 60
    x0 = 1300
    Sh.alpha_composite(city(610, 470, 33), (x0, 84))
    d.text((x0 + 10, 90), "ANATOMY  (one Care Drone, enlarged)", font=f_ui(15, b"Bold SemiCondensed"), fill=YEL)
    sim, sc = SA.render_sat(SA.CARE_DRONE, 0)
    sim = sim.crop(sim.split()[3].getbbox())
    kk = 330 / sim.height
    sim2 = sim.resize((int(sim.width * kk), int(sim.height * kk)), Image.LANCZOS)
    ax, ay = x0 + 300 - sim2.width // 2, 118
    Sh.alpha_composite(sim2, (ax, ay))
    mid = (ax + sim2.width / 2, ay + sim2.height * 0.6)
    label(d, (x0 + 395, 140), "OWN POINTER", "D4 blade, faces out from the host", YEL)
    leader(d, (ax + sim2.width / 2 + 10, ay + 30), (x0 + 395, 140), YEL)
    label(d, (x0 + 395, 230), "2-3 SLICES", "15 or 10 ticks each, corp screens", WHITE)
    leader(d, (ax + sim2.width - 50, ay + 190), (x0 + 395, 230))
    label(d, (x0 + 395, 320), "HP IN THE HUB", "number + one pip per HP", (123, 224, 123))
    leader(d, (mid[0] + 10, mid[1] + 10), (x0 + 395, 320), (123, 224, 123))
    label(d, (x0 + 10, 470), "30-TICK RIM", "corp bezel, lit active slice", WHITE)
    leader(d, (ax + 30, ay + 250), (x0 + 120, 470))
    for j, ln in enumerate(("ON THE HOST: a clamp plate on the host rim marks the docked slice;",
                            "the satellite sits 22 deg clockwise of the slice centre, past the HP arc.")):
        d.text((x0 + 10, 512 + j * 16), ln, font=f_mono(12, False), fill=(190, 190, 205))
    Sh.alpha_composite(city(610, 270, 44), (x0, 566))
    d.text((x0 + 10, 572), "r = 60  (hosts at combat-roster size; satellites scale with the host)", font=f_ui(15, b"Bold SemiCondensed"), fill=YEL)
    for k, (name, spec, sats) in enumerate((("p60", pb, P_SATS), ("e60", eb, E_SATS))):
        im, c, meta = cached(name, lambda spec=spec, sats=sats: SA.compose(spec, sats, 60, lod=True))
        fit_into(Sh, im, c, (x0 + 20 + k * 300, 600, x0 + 290 + k * 300, 830))
    # ---- row 2: states
    y0 = 870
    d.line([(20, y0 - 8), (1900, y0 - 8)], fill=(60, 60, 74))
    tiles = state_tiles(eb)
    tw = 374
    for k, (title, sub, im) in enumerate(tiles):
        x = 10 + k * (tw + 6)
        Sh.alpha_composite(city(tw, 680, 60 + k), (x, y0))
        fit_into(Sh, im, (0, 0), (x + 4, y0 + 74, x + tw - 4, y0 + 676))
        d.text((x + 10, y0 + 6), title, font=f_num(26), fill=YEL)
        for j, ln in enumerate(sub):
            d.text((x + 10, y0 + 40 + j * 16), ln, font=f_mono(12, False), fill=(205, 205, 218))
    Sh.convert("RGB").save(os.path.join(OUT, "satellites.png"))
    print("sheet", flush=True)


def crop_around(im, c, meta, i, rot=0.0, w=340, h=440, toward=0.22):
    sx, sy = sat_pos(c, meta, i, rot)
    cx = sx + (c[0] - sx) * toward
    cy = sy + (c[1] - sy) * toward
    return im.crop((int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2)))


def state_tiles(eb):
    out = []
    # 1 docked
    im, c, meta = cached("e220", lambda: SA.compose(eb, E_SATS, 220, hp_number=True))
    t = crop_around(im, c, meta, 2)
    out.append(("1  DOCKED", ["rides slice 3 (DEFEND 4); clamp plate", "on the host rim; resolves after", "the host when that slice resolves"], t))
    # 2 nudged individually
    st = {2: dict(srot=-12.0)}
    im, c, meta = cached("e220_nudge", lambda: SA.compose(eb, E_SATS, 220, states=st, hp_number=True))
    t = crop_around(im, c, meta, 2)
    dd = ImageDraw.Draw(t)
    sx, sy = sat_pos(c, meta, 2)
    ox = sx - (sx + (c[0] - sx) * 0.22 - 170)
    oy = sy - (sy + (c[1] - sy) * 0.22 - 220)
    rr = meta["Rd"] * 0 + 82
    for side, lab in ((-1, "<"), (1, ">")):  # its own nudge buttons
        bx, by = ox + side * (rr + 18), oy + 70
        dd.ellipse([bx - 20, by - 20, bx + 20, by + 20], fill=(16, 14, 22, 235), outline=(255, 214, 64) if side > 0 else (150, 150, 165), width=3)
        dd.text((bx, by), lab, font=f_num(26), fill=WHITE, anchor="mm")
    dd.text((ox + rr + 46, oy + 70), "+1", font=f_num(28), fill=(255, 214, 64), anchor="lm", stroke_width=2, stroke_fill=INK)
    out.append(("2  NUDGED ON ITS OWN", ["its own < > (and NUDGE cards aimed", "at it) turn only the mini-wheel:", "here +1 tick, host untouched"], t))
    # 3 carried by a spin: locked preview (chevrons for the top needle + dashed ghost satellites)
    im, c, meta = cached("e220_pv", lambda: SA.compose(eb, E_SATS, 220, ghosts=[(i, 9) for i, _ in E_SATS], chase=(9, 1.0), hp_number=True))
    out.append(("3  CARRIED BY A SPIN", ["HEAVY SPIN 9 preview: chevrons for", "the top needle, a dashed ghost", "where each satellite ENDS UP"], im))
    # 4 bodyguard
    st = {0: dict(guard=200.0, hp=1)}
    im, c, meta = cached("e220_guard", lambda: SA.compose(eb, E_SATS, 220, states=st, hp_number=True))
    t = crop_around(im, c, meta, 0, w=400, h=520, toward=0.45)
    dd = ImageDraw.Draw(t)
    out.append(("4  BODYGUARD", ["your EXPLOIT 3 hits the host pointer", "on slice 1: the docked drone takes", "it instead (4 -> 1 HP, red pips)"], t))
    # 5 destroyed
    st = {2: dict(dead=True, hp=0)}
    im, c, meta = cached("e220_dead", lambda: SA.compose(eb, E_SATS, 220, states=st, hp_number=True))
    t = crop_around(im, c, meta, 2)
    out.append(("5  DESTROYED", ["0 HP: greyed, cracked, then it", "undocks and falls away (gif);", "the slice is unguarded again"], t))
    return out


# ================================================================== gif
def gif():
    eb = care_swarm()
    frames, durs = [], []
    N = 9
    Wf = 640

    def add(im, c, cap, dur, extra=None):
        canvas = Image.new("RGBA", (980, 960), BG + (255,))
        canvas.alpha_composite(city(980, 960, 5))
        k = min(940 / im.width, 860 / im.height)
        im2 = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
        ox, oy = (980 - im2.width) // 2, 80 + (870 - im2.height) // 2
        canvas.alpha_composite(im2, (ox, oy))
        d = ImageDraw.Draw(canvas)
        d.rectangle([0, 0, 980, 60], fill=(10, 9, 16, 240))
        d.text((16, 10), cap, font=f_num(34), fill=WHITE)
        if extra:
            extra(d, ox, oy, k)
        frames.append(canvas.resize((Wf, int(960 * Wf / 980)), Image.LANCZOS).convert("RGB"))
        durs.append(dur)
        print("frame", cap[:24], flush=True)

    host0 = SA.host_image(eb, 0.0, hp_number=True)
    im, c, meta = SA.compose(eb, E_SATS, 220, host=host0)
    add(im, c, "1  NOW: 3 satellites docked on Care Swarm", 1500)
    for ph in (0.25, 0.5, 0.75, 1.0):
        im, c, meta = SA.compose(eb, E_SATS, 220, host=host0, chase=(N, ph), ghosts=[(i, N) for i, _ in E_SATS] if ph >= 1 else None)
        add(im, c, "2  hover HEAVY SPIN 9: preview", 140 if ph < 1 else 1500)
    steps = 10
    for s in range(1, steps + 1):
        q = s / steps
        q = q * q * (3 - 2 * q)
        rot = 12 * N * q
        h = SA.host_image(eb, rot, hp_number=True)
        im, c, meta = SA.compose(eb, E_SATS, 220, host=h, rot=rot, ghosts=[(i, N) for i, _ in E_SATS] if s < steps else None)
        add(im, c, "3  SEND IT: the spin carries every satellite", 90 if s < steps else 1200)
    rot = 12 * N
    hN = SA.host_image(eb, rot, hp_number=True)
    for sr in (-4.0, -8.0, -12.0):
        im, c, meta = SA.compose(eb, E_SATS, 220, host=hN, rot=rot, states={2: dict(srot=sr)})
        add(im, c, "4  NUDGE one satellite: only its mini-wheel turns", 160 if sr > -12 else 1200)
    for hp, dead, cap, dur in ((1, False, "5  BODYGUARD: it takes the hit (4 -> 1)", 1200), (0, True, "6  DESTROYED: 0 HP", 1400)):
        st = {2: dict(srot=-12.0, hp=hp, guard=60.0 + rot + 22 + 180 if not dead else None, dead=dead)}
        im, c, meta = SA.compose(eb, E_SATS, 220, host=hN, rot=rot, states=st)
        add(im, c, cap, dur)
    q = [f.quantize(colors=192, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
    p = os.path.join(OUT, "satellite_motion.gif")
    q[0].save(p, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=True)
    print("gif KB", os.path.getsize(p) // 1024, len(frames), flush=True)


if __name__ == "__main__":
    {"sheet": sheet, "gif": gif}[sys.argv[1]]()
    print("done")
