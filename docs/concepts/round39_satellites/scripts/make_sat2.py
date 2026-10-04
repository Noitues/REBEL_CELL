"""Round 39 build: python make_sat2.py sheet | gif | psheet | pgif"""
import copy
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
SCR = os.path.join(OUT, "scratch")

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import sat2 as S2
import specs14 as S
import roster as RS
from frames import INK
from slicelib import f_num, f_ui, f_mono, R_OUT

BG = (16, 15, 22)
YEL = (255, 214, 64)
WHITE = (255, 255, 255)
PINK = (255, 150, 210)
SIZE = (1760, 1760)          # fixed composite canvas: the host's exact centre is always at (880, 880)


def botnet():
    s, m = RS.class_spec("botnet")
    s = copy.deepcopy(s)
    s["key"] = "botnet"
    s["hp"] = (38, 45)
    return s


def care_swarm():
    return S.enemy("care_swarm", "solace", "regular")[0]


P_SATS = [(1, S2.BOTNET_DRONE), (3, S2.BOTNET_DRONE)]
E_SATS = [(0, S2.CARE_DRONE), (2, S2.CARE_DRONE), (4, S2.CARE_DRONE)]
NEW_DRONE = dict(S2.CARE_DRONE, name="CARE DRONE NEW")


def city(w, h, seed=3, k=0.30):
    src = Image.open(os.path.join(OUT, "..", "round6_city_restyle", "views", "restyle_night_full.png")).convert("RGB")
    rng = np.random.default_rng(seed)
    x = int(rng.integers(0, src.width - w))
    y = int(rng.integers(0, src.height - h))
    t = src.crop((x, y, x + w, y + h)).filter(ImageFilter.GaussianBlur(3))
    return Image.fromarray((np.asarray(t, np.float32) * k).astype(np.uint8)).convert("RGBA")


def tag(d, xy, text, sub=None, col=WHITE, anchor="mm", size=24):
    f = f_num(size)
    fs = f_ui(int(size * 0.62), b"Bold SemiCondensed")
    tw = max(f.getlength(text), fs.getlength(sub) if sub else 0)
    h = size + (int(size * 0.85) if sub else 0) + 12
    x, y = xy
    x0 = x - tw / 2 - 10 if anchor == "mm" else (x if anchor == "lm" else x - tw - 20)
    y0 = y - h / 2
    d.rounded_rectangle([x0, y0, x0 + tw + 20, y0 + h], radius=7, fill=(10, 9, 16, 235), outline=col, width=3)
    d.text((x0 + 10, y0 + 4), text, font=f, fill=col)
    if sub:
        d.text((x0 + 10, y0 + size + 6), sub, font=fs, fill=(200, 200, 215))


def fit_into(sheet, im, box, valign=0.5):
    x0, y0, x1, y1 = box
    k = min((x1 - x0) / im.width, (y1 - y0) / im.height, 1.0)
    im2 = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    sheet.alpha_composite(im2, (int(x0 + (x1 - x0 - im2.width) / 2), int(y0 + (y1 - y0 - im2.height) * valign)))


def trim(im, pad=10):
    bb = im.split()[3].point(lambda v: 255 if v > 4 else 0).getbbox()
    return im.crop((max(0, bb[0] - pad), max(0, bb[1] - pad), bb[2] + pad, bb[3] + pad))


def at_r(c, r_px, crop=None):
    return c.image(scale=r_px / R_OUT, crop=crop)


def sat_crop(c, i, rot=0.0, w=520, h=560, toward=0.30):
    a = 60 * i + rot
    sx, sy = c.PP(S2.dock_r(c.RA), a)
    cx, cy = sx + (c.C[0] - sx) * toward, sy + (c.C[1] - sy) * toward
    return (int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))


# ================================================================== satellites sheet
def sheet():
    W, H = 1920, 1600
    Sh = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(Sh)
    d.rectangle([0, 0, 8, 64], fill=YEL)
    d.text((26, 6), "SATELLITES v2  -  centred on their slice, rounded cradle, bigger slice read", font=f_num(44), fill=WHITE)
    d.text((26, 56), "Each satellite is centred on the slice it docks to and orbits the host's exact centre. A new satellite on an occupied slice OVERWRITES the old one. "
                     "Not nudgeable by default.", font=f_mono(14, False), fill=(185, 185, 200))
    pb, eb = botnet(), care_swarm()
    for k, (spec, sats, title) in enumerate(((pb, P_SATS, "PLAYER  BOTNET  r = 220  -  drones on the two DEPLOY slices"),
                                              (eb, E_SATS, "ENEMY  CARE SWARM  r = 220  -  3 Care Drones"))):
        x0 = 10 + k * 645
        Sh.alpha_composite(city(635, 780, 20 + k), (x0, 84))
        c = S2.compose(spec, sats, size=SIZE)
        fit_into(Sh, trim(at_r(c, 220)), (x0 + 4, 114, x0 + 631, 860))
        d.text((x0 + 10, 90), title, font=f_ui(15, b"Bold SemiCondensed"), fill=WHITE)
    x0 = 1300
    Sh.alpha_composite(city(610, 500, 33), (x0, 84))
    d.text((x0 + 10, 90), "ANATOMY  (one Care Drone, enlarged)", font=f_ui(15, b"Bold SemiCondensed"), fill=YEL)
    sim, sc = S2.render_sat(S2.CARE_DRONE, 0)
    sim = trim(sim)
    k = 340 / sim.height
    sim2 = sim.resize((int(sim.width * k), int(sim.height * k)), Image.LANCZOS)
    ax, ay = x0 + 210 - sim2.width // 2, 118
    Sh.alpha_composite(sim2, (ax, ay))
    tags = [("OWN POINTER", "faces out from the host", YEL, 150),
            ("GLYPH | VALUE", "bigger, spread along the slice", WHITE, 250),
            ("HP IN THE HUB", "number + one pip per HP", (123, 224, 123), 350),
            ("CRADLE", "hugs the host rim, waisted neck,", (205, 205, 220), 450)]
    for t, s, col, y in tags:
        tag(d, (x0 + 400, y), t, s, col, anchor="lm", size=20)
    d.text((x0 + 10, 560), "collar ring round the satellite (see the hosts)", font=f_mono(12, False), fill=(190, 190, 205))
    Sh.alpha_composite(city(610, 280, 44), (x0, 590))
    d.text((x0 + 10, 596), "r = 60", font=f_ui(15, b"Bold SemiCondensed"), fill=YEL)
    for k, (spec, sats) in enumerate(((pb, P_SATS), (eb, E_SATS))):
        c = S2.compose(spec, sats, size=SIZE, lod=True)
        fit_into(Sh, trim(at_r(c, 60)), (x0 + 20 + k * 300, 620, x0 + 290 + k * 300, 864))
    # states
    y0 = 900
    d.line([(20, y0 - 8), (1900, y0 - 8)], fill=(60, 60, 74))
    tw = 374
    tiles = []
    c = S2.compose(eb, E_SATS, size=SIZE)
    tiles.append(("1  DOCKED", ["centred on slice 3 (DEFEND 4);", "the cradle hugs the rim, collar", "rings the satellite"], at_r(c, 300, sat_crop(c, 2))))
    c = S2.compose(eb, E_SATS, size=SIZE, ghosts=[(i, 9) for i, _ in E_SATS], chase=(9, 1.0))
    tiles.append(("2  CARRIED BY A SPIN", ["HEAVY SPIN 9 preview: chevrons for", "the top needle + a dashed ghost where", "each satellite ENDS UP (locked)"], trim(at_r(c, 150))))
    c = S2.compose(eb, E_SATS, size=SIZE, states={0: dict(guard=180.0, hp=1)})
    tiles.append(("3  BODYGUARD", ["your EXPLOIT 3 aimed at the host", "pointer hits the drone docked on", "that slice instead (4 -> 1 HP)"], at_r(c, 300, sat_crop(c, 0, toward=0.22, w=620, h=760))))
    tiles.append(("4  OVERWRITE", ["a new satellite on an occupied", "slice replaces the old one: the old", "is knocked off and bit-bursts"], overwrite_strip(eb)))
    c = S2.compose(eb, E_SATS, size=SIZE, states={2: dict(hidden=True)})
    sx, sy = c.PP(S2.dock_r(c.RA), 120)
    c.put_sat(S2.CARE_DRONE, 120, state=dict(hp=0), alpha=0.35, grey=True)
    S2.bit_burst(c.top, sx, sy, 0.32, seed=5, radius=300)
    tiles.append(("5  DESTROYED", ["0 HP: binary-bit explosion (flash,", "shock ring, 0/1 bits blast out and", "fall); the cradle retracts"], at_r(c, 300, sat_crop(c, 2, w=700, h=700))))
    for k, (title, sub, im) in enumerate(tiles):
        x = 10 + k * (tw + 6)
        Sh.alpha_composite(city(tw, 690, 60 + k), (x, y0))
        fit_into(Sh, im, (x + 4, y0 + 76, x + tw - 4, y0 + 686))
        d.text((x + 10, y0 + 6), title, font=f_num(26), fill=YEL)
        for j, ln in enumerate(sub):
            d.text((x + 10, y0 + 40 + j * 16), ln, font=f_mono(12, False), fill=(205, 205, 218))
    d.text((24, H - 22), "NUDGE: not a default satellite verb. Drone classes may get 'nudge a drone' as a class ability (note only).",
           font=f_mono(13, False), fill=(170, 170, 185))
    Sh.convert("RGB").save(os.path.join(OUT, "satellites_v2.png"))
    print("sheet", flush=True)


def overwrite_frame(eb, step, host=None, rot=0.0):
    """step 0..1: 0-0.4 new drone arrives from outside; 0.4-0.75 old knocked off + bit burst; 0.75-1 new docked."""
    c = S2.compose(eb, [(0, S2.CARE_DRONE), (4, S2.CARE_DRONE), (2, S2.CARE_DRONE)], size=SIZE, host=host, rot=rot,
                   states={2: dict(hidden=True)})
    a = 120 + rot
    old = dict(S2.CARE_DRONE, hp=2)
    if step < 0.4:
        q = step / 0.4
        c.put_sat(old, a, state=dict(hp=2))
        c.put_sat(NEW_DRONE, a, offset=520 * (1 - q) + 260, alpha=0.5 + 0.5 * q)
        lab = "NEW DRONE incoming"
    elif step < 0.75:
        q = (step - 0.4) / 0.35
        c.put_sat(NEW_DRONE, a)
        sx, sy = c.PP(S2.dock_r(c.RA) + 60 + 220 * q, a + 22 * q)
        oc = S2.Comp((c.him, c.hc, c.meta), SIZE)
        old_img, oc_c = S2.render_sat(old, a + 40 * q, state=dict(hp=2))
        k = S2.SAT_K
        old_img = S2.greyed(old_img.resize((int(old_img.width * k), int(old_img.height * k)), Image.LANCZOS))
        old_img = S2.fade(old_img, max(0.0, 1 - q * 1.1))
        c.top.alpha_composite(old_img, (int(sx - oc_c[0] * k), int(sy - oc_c[1] * k)))
        S2.bit_burst(c.top, sx, sy, q * 0.9, seed=8, radius=240)
        lab = "OLD DRONE knocked off"
    else:
        c.put_sat(NEW_DRONE, a)
        lab = "OVERWRITTEN"
    return c, lab


def overwrite_strip(eb):
    parts = []
    for st in (0.15, 0.55, 0.9):
        c, lab = overwrite_frame(eb, st)
        im = at_r(c, 200, sat_crop(c, 2, w=1000, h=760, toward=-0.05))
        d = ImageDraw.Draw(im)
        tag(d, (im.width // 2, 26), lab, col=YEL if lab != "OVERWRITTEN" else PINK, size=22)
        parts.append(im)
    W = max(p.width for p in parts)
    out = Image.new("RGBA", (W, sum(p.height for p in parts)), (0, 0, 0, 0))
    y = 0
    for p in parts:
        out.alpha_composite(p, ((W - p.width) // 2, y))
        y += p.height
    return out


# ================================================================== satellites gif
def frame(c, cap, scale=0.36):
    im = c.image(scale=scale)
    base = city(im.width, im.height, 5)
    base.alpha_composite(im)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, base.width, 52], fill=(10, 9, 16, 240))
    d.text((14, 8), cap, font=f_num(30), fill=WHITE)
    # centre marker: proves every frame shares the host's exact centre
    cx, cy = c.C[0] * scale, c.C[1] * scale
    d.line([(cx - 6, cy), (cx + 6, cy)], fill=(255, 214, 64, 160), width=1)
    return base.convert("RGB")


def save_gif(frames, durs, name, max_kb=3900):
    for colors in (192, 128, 96):
        q = [f.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
        p = os.path.join(OUT, name)
        q[0].save(p, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=True)
        if os.path.getsize(p) // 1024 <= max_kb:
            break
    print(name, os.path.getsize(p) // 1024, "KB", len(frames), flush=True)


def gif():
    eb = care_swarm()
    fr, du = [], []
    h0 = S2.host_image(eb, 0.0, hp_number=True)
    fr.append(frame(S2.compose(eb, E_SATS, host=h0, size=SIZE), "1  NOW: 3 satellites, each centred on its slice")); du.append(1400)
    for ph in (0.25, 0.5, 0.75, 1.0):
        c = S2.compose(eb, E_SATS, host=h0, size=SIZE, chase=(9, ph), ghosts=[(i, 9) for i, _ in E_SATS] if ph >= 1 else None)
        fr.append(frame(c, "2  hover HEAVY SPIN 9: preview")); du.append(130 if ph < 1 else 1400)
    steps = 10
    for s in range(1, steps + 1):
        q = s / steps
        q = q * q * (3 - 2 * q)
        rot = 108 * q
        h = S2.host_image(eb, rot, hp_number=True)
        c = S2.compose(eb, E_SATS, host=h, rot=rot, size=SIZE, ghosts=[(i, 9 * (1 - q) / 1.0) for i, _ in E_SATS] if False else None)
        fr.append(frame(c, "3  SEND IT: satellites orbit the host's exact centre")); du.append(90 if s < steps else 1100)
    rot = 108.0
    hN = S2.host_image(eb, rot, hp_number=True)
    # after the spin, slot 4 sits under the host pointer: bodyguard, then destroyed
    c = S2.compose(eb, E_SATS, host=hN, rot=rot, size=SIZE, states={4: dict(guard=180.0, hp=1)})
    fr.append(frame(c, "4  BODYGUARD: the drone takes the hit (4 -> 1)")); du.append(1200)
    a4 = 240 + rot
    for k, q in enumerate((0.05, 0.2, 0.4, 0.6, 0.85)):
        c = S2.compose(eb, E_SATS, host=hN, rot=rot, size=SIZE, states={4: dict(hidden=True)})
        sx, sy = c.PP(S2.dock_r(c.RA), a4)
        if q < 0.3:
            c.put_sat(S2.CARE_DRONE, a4, state=dict(hp=0), alpha=1 - q * 2, grey=True)
        S2.bit_burst(c.top, sx, sy, q, seed=5, radius=300)
        fr.append(frame(c, "5  DESTROYED: binary-bit explosion")); du.append(110 if k < 4 else 700)
    sats_left = [(0, S2.CARE_DRONE), (2, S2.CARE_DRONE)]
    for k, st in enumerate((0.0, 0.2, 0.35, 0.5, 0.62, 0.72, 0.95)):
        c = S2.compose(eb, [(0, S2.CARE_DRONE)], host=hN, rot=rot, size=SIZE)
        c2, lab = overwrite_frame_on(c, st, rot)
        fr.append(frame(c2, "6  " + ("OVERWRITE: a new drone lands on an occupied slice" if lab != "OVERWRITTEN" else "OVERWRITTEN: old drone lost")))
        du.append(140 if k < 6 else 1500)
    save_gif(fr, du, "satellite_motion_v2.gif")


def overwrite_frame_on(c, step, rot):
    a = 120 + rot
    c.cradle(a, S2.sat_acc(S2.CARE_DRONE))
    old = dict(S2.CARE_DRONE, hp=2)
    if step < 0.4:
        q = step / 0.4
        c.put_sat(old, a, state=dict(hp=2))
        c.put_sat(NEW_DRONE, a, offset=520 * (1 - q) + 260, alpha=0.5 + 0.5 * q)
        return c, "incoming"
    if step < 0.75:
        q = (step - 0.4) / 0.35
        c.put_sat(NEW_DRONE, a)
        sx, sy = c.PP(S2.dock_r(c.RA) + 60 + 220 * q, a + 22 * q)
        old_img, oc_c = S2.render_sat(old, a + 40 * q, state=dict(hp=2))
        k = S2.SAT_K
        old_img = S2.greyed(old_img.resize((int(old_img.width * k), int(old_img.height * k)), Image.LANCZOS))
        old_img = S2.fade(old_img, max(0.0, 1 - q * 1.1))
        c.top.alpha_composite(old_img, (int(sx - oc_c[0] * k), int(sy - oc_c[1] * k)))
        S2.bit_burst(c.top, sx, sy, q * 0.9, seed=8, radius=240)
        return c, "knocked"
    c.put_sat(NEW_DRONE, a)
    return c, "OVERWRITTEN"


# ================================================================== parasite ring
def boss():
    b, m = S.boss("solace", 1)
    return b


def psheet():
    W, H = 1920, 1180
    Sh = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(Sh)
    d.rectangle([0, 0, 8, 64], fill=(214, 60, 255))
    d.text((26, 6), "PARASITE RING  -  boss mechanic (concept): an anti-inner-ring", font=f_num(44), fill=WHITE)
    d.text((26, 56), "It latches onto ONE host slice and grows a temporary partial THIRD ring over that slice's arc, outside the frame, "
                     "with 3 small slices of NEGATIVE effects on the host slice.", font=f_mono(14, False), fill=(185, 185, 200))
    b = boss()
    h = S2.host_image(b, hp_number=True)
    c = S2.Comp(h, SIZE)
    S2.parasite(c, 1, lit=0)
    Sh.alpha_composite(city(1000, 1070, 7), (10, 84))
    big = trim(at_r(c, 220))
    fit_into(Sh, big, (14, 110, 1006, 1150))
    d.text((20, 92), "RENEWAL ENGINE (Solace boss)  r = 220  -  parasite on slice 2 (EXPLOIT 14)", font=f_ui(16, b"Bold SemiCondensed"), fill=(214, 60, 255))
    x0 = 1020
    Sh.alpha_composite(city(890, 560, 9), (x0, 84))
    d.text((x0 + 10, 92), "ANATOMY", font=f_ui(16, b"Bold SemiCondensed"), fill=YEL)
    a_mid = 60
    sx, sy = c.PP(c.RA + 130, a_mid)
    crop = (int(sx - 330), int(sy - 260), int(sx + 330), int(sy + 300))
    det = c.image(scale=1.0, crop=crop)
    k = 520 / det.height
    det = det.resize((int(det.width * k), int(det.height * k)), Image.LANCZOS)
    Sh.alpha_composite(det, (x0 + 10, 118))
    lines = [("PARTIAL 3RD RING", "spans only the host slice's arc, past", "the frame; rides the slice on spins"),
             ("3 NEGATIVE SLICES", "x0.5 output | -2 RAM | CORRUPT", "the anti-inner-ring"),
             ("LATCH CLAWS", "tendrils into the host rim", ""),
             ("TURNS LEFT", "3 pips; it drops off at 0", "")]
    for j, (t_, s1, s2) in enumerate(lines):
        y = 150 + j * 120
        tag(d, (x0 + 560, y), t_, s1, (214, 60, 255) if j < 2 else WHITE, anchor="lm", size=22)
        if s2:
            d.text((x0 + 570, y + 34), s2, font=f_mono(12, False), fill=(200, 200, 215))
    Sh.alpha_composite(city(890, 500, 11), (x0, 660))
    d.text((x0 + 10, 668), "RULES (proposal)", font=f_ui(16, b"Bold SemiCondensed"), fill=YEL)
    rules = ["- latches onto one slice (boss phase move); it rides that slice",
             "  through spins and flips, like a satellite",
             "- when the host slice resolves, the parasite sub-slice in line",
             "  with the pointer tick applies its NEGATIVE modifier to it:",
             "  x0.5 output, -2 RAM to the owner, or CORRUPTED",
             "- temporary: 3 turns (pips), then it detaches",
             "- mocked on the boss wheel as briefed; OPEN: does the boss latch",
             "  it onto the PLAYER's wheel (an attack you outlast or cleanse)?",
             "- example: EXPLOIT 14 resolving in line with x0.5 -> 7"]
    for j, ln in enumerate(rules):
        d.text((x0 + 14, 700 + j * 22), ln, font=f_mono(15, False), fill=(210, 210, 222))
    d.text((x0 + 14, 920), "r = 60", font=f_ui(16, b"Bold SemiCondensed"), fill=YEL)
    c60 = S2.Comp(S2.host_image(b, hp_number=False), SIZE)
    S2.parasite(c60, 1, lod=True)
    fit_into(Sh, trim(at_r(c60, 60)), (x0 + 10, 940, x0 + 300, 1150))
    Sh.convert("RGB").save(os.path.join(OUT, "parasite_ring.png"))
    print("psheet", flush=True)


def pgif():
    b = boss()
    h = S2.host_image(b, hp_number=True)
    fr, du = [], []

    def fr_(c, cap, dur, extra=None):
        im = c.image(scale=0.5)
        base = city(im.width, im.height, 6)
        base.alpha_composite(im)
        dd = ImageDraw.Draw(base)
        dd.rectangle([0, 0, base.width, 52], fill=(10, 9, 16, 240))
        dd.text((14, 8), cap, font=f_num(30), fill=WHITE)
        if extra:
            extra(dd, c)
        fr.append(base.convert("RGB"))
        du.append(dur)
    c = S2.Comp(h, SIZE)
    fr_(c, "1  boss phase: the PARASITE latches on", 1000)
    for k, p in enumerate((0.1, 0.25, 0.4, 0.55, 0.7, 0.85, 1.0)):
        c = S2.Comp(h, SIZE)
        S2.parasite(c, 1, prog=p)
        fr_(c, "2  claws grip slice 2; the ring grows", 120 if p < 1 else 1300)

    def ex(dd, c):
        x, y = c.PP(c.RA + 200, 20)
        tag(dd, (x * 0.5, y * 0.5 - 60), "EXPLOIT 14  x0.5  =  7", "this turn, in line with the pointer tick", PINK, anchor="lm", size=26)
    for turns, lit, cap in ((3, 0, "3  when slice 2 resolves: x0.5 applies"), (2, None, "4  2 turns left"), (1, None, "5  1 turn left")):
        c = S2.Comp(h, SIZE)
        S2.parasite(c, 1, lit=lit, turns=turns)
        fr_(c, cap, 1300, ex if lit == 0 else None)
    for k, p in enumerate((0.75, 0.45, 0.15)):
        c = S2.Comp(h, SIZE)
        S2.parasite(c, 1, prog=p, turns=0)
        fr_(c, "6  0 turns: it detaches", 140)
    c = S2.Comp(h, SIZE)
    fr_(c, "6  0 turns: it detaches", 900)
    save_gif(fr, du, "parasite_ring.gif")


if __name__ == "__main__":
    {"sheet": sheet, "gif": gif, "psheet": psheet, "pgif": pgif}[sys.argv[1]]()
    print("done")
