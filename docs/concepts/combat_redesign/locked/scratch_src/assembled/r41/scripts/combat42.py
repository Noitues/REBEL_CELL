"""Round 41 v2 combat screens.

python combat42.py worst | typical | sheet | frame <k> | gif
"""
import copy
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
SCR = os.path.join(OUT, "scratch")

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import stack42 as Q            # sets the v2 drone size first
import sat2 as S2
import stack41 as K
import specs14 as S
import combat41 as C41
from frames import INK
from slicelib import R_OUT, R_IN, f_num, f_ui, f_mono
from preview15 import dashed_poly
from make_sat2 import city, fit_into, trim, at_r, save_gif

W, H = C41.W, C41.H
PLAYER, BOSS = C41.PLAYER, C41.BOSS
SIZE = (2000, 2000)
SEGS_WORST = ["SEG_hangar", "SEG_x2", "SEG_pierce"]
SEGS_TYP = ["SEG_x2", "SEG_pierce", "SEG_blank"]


def wheel(spec, sat, worst, is_player, r_px, rot=0.0, hover=None, pop=1.0, lod=False):
    spec = copy.deepcopy(spec)
    if is_player:
        spec["slot_tier"] = {0: 3, 1: 2, 2: 1, 3: 2, 4: 3, 5: 1} if worst else {0: 2, 3: 1}
    else:
        spec["corp_tier"] = 3
    spec["variant"] = "v2w" if worst else "v2t"
    h = S2.host_image(spec, rot, hp_number=False)
    c = S2.Comp(h, SIZE)
    top = h[2]["top_r"]
    if is_player:
        segs = SEGS_WORST if worst else SEGS_TYP
        ext = [(k, 120 * k + rot) for k in range(3)] if worst else [(0, rot)]
        Q.ring_locked(c, segs, ext, rot=rot)
    for i in range(6):
        if is_player and (worst or i == 1):
            K.firmware_socket(c, i, rot)
        if worst or i == (3 if is_player else 4):
            C41.state_overlay(c, i, rot, i, 2 + i % 4 if worst else 1)
    if is_player:
        K.sub_needle(c, 1, rot)
    for i in range(6):
        C41.read_block(c, spec, i, rot)
    needle = int(round(((-rot) % 360) / 60.0)) % 6   # the slot under the needle
    par_slots = list(range(6)) if worst else ([] if is_player else [3])
    drone_slots = list(range(6)) if worst else ([1] if is_player else [2])
    n = 2 if worst else 1
    par_out = {}
    for i in par_slots:
        st = pop if i == needle else 0.0
        r_in, r_out = K.parasite(c, i, rot, top, st, lit=1 if st >= 1 else None, lod=lod)
        par_out[i] = r_out
    for i in drone_slots:
        a = 60 * i + rot
        if hover == i:
            Q.drones_full(c, sat, a, n, spec, rot, par_r_out=par_out.get(i), lod=lod)
        else:
            Q.drones_band(c, sat, a, n, par_r_out=par_out.get(i))
    yy, xx = np.mgrid[0:c.H, 0:c.W].astype(np.float32)
    outside = np.hypot(xx - c.C[0], yy - c.C[1]) > c.RA + 4
    full = c.image()
    al = np.asarray(full.split()[3], np.float32) / 255 * outside
    k = r_px / R_OUT
    img = full.resize((int(c.W * k), int(c.H * k)), Image.LANCZOS)
    alim = Image.fromarray((al * 255).astype(np.uint8)).resize(img.size, Image.BILINEAR)
    return img, (c.C[0] * k, c.C[1] * k), alim


def screen(worst, rot_p=0.0, rot_b=0.0, hover=None, pop=1.0, label=None, marks=True):
    clean, jpg = C41.base_plate()
    M = 600
    canvas = Image.new("RGBA", (W + 2 * M, H + 2 * M), (0, 0, 0, 0))
    canvas.alpha_composite(clean.convert("RGBA"), (M, M))
    ex_all = Image.new("L", canvas.size, 0)
    P = S.player()
    B, bm = S.boss("meridian", 1)
    for spec, sat, cfg, is_p, rot, hv in ((P, S2.BOTNET_DRONE, PLAYER, True, rot_p, hover), (B, C41.COURIER, BOSS, False, rot_b, None)):
        img, cc, al = wheel(spec, sat, worst, is_p, cfg["r"], rot, hv, pop)
        ox, oy = int(M + cfg["c"][0] - cc[0]), int(M + cfg["c"][1] - cc[1])
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sh.putalpha(img.split()[3].point(lambda v: int(v * 0.5)).filter(ImageFilter.GaussianBlur(10)))
        canvas.alpha_composite(sh, (ox + 6, oy + 12))
        canvas.alpha_composite(img, (ox, oy))
        ex_all.paste(al, (ox, oy), al)
    ea = np.asarray(ex_all, np.float32) / 255
    off_pct = 100 * (ea.sum() - ea[M:M + H, M:M + W].sum()) / max(1, ea.sum())
    shot = canvas.crop((M, M, M + W, M + H))
    ein = ea[M:M + H, M:M + W]
    d = ImageDraw.Draw(shot)
    hits = []
    for name, (x0, y0, x1, y1) in C41.HUD.items():
        shot.paste(jpg.crop((x0, y0, x1, y1)), (x0, y0))
        hits.append((name, float((ein[y0:y1, x0:x1] > 0.3).mean())))
    if marks:
        for name, cov in hits:
            x0, y0, x1, y1 = C41.HUD[name]
            if cov > 0.02:
                dashed_poly(d, [(x0 - 3, y0 - 3), (x1 + 3, y0 - 3), (x1 + 3, y1 + 3), (x0 - 3, y1 + 3)], (255, 40, 60), 4, dash=14, gap=8)
                s = "%s hides %d%%" % (name, round(100 * cov))
                f = f_ui(15, b"Bold SemiCondensed")
                ty = y0 - 24 if y0 > 30 else y1 + 6
                d.rounded_rectangle([x0, ty, x0 + f.getlength(s) + 12, ty + 20], radius=4, fill=(255, 40, 60))
                d.text((x0 + 6, ty + 1), s, font=f, fill=(255, 255, 255))
    if label:
        f = f_num(26)
        tw = f.getlength(label)
        d.rounded_rectangle([W - tw - 30, H - 40, W - 10, H - 6], radius=6, fill=(10, 9, 16, 230), outline=(255, 214, 64), width=2)
        d.text((W - tw - 20, H - 40), label, font=f, fill=(255, 214, 64))
    return shot, off_pct, hits


def still(worst):
    shot, off, hits = screen(worst, hover=2 if worst else None, label=None)
    lab = ("WORST CASE v2" if worst else "TYPICAL v2") + "  |  off-screen %d%%" % round(off)
    d = ImageDraw.Draw(shot)
    f = f_num(26)
    tw = f.getlength(lab)
    d.rounded_rectangle([W - tw - 30, H - 40, W - 10, H - 6], radius=6, fill=(10, 9, 16, 230), outline=(255, 214, 64), width=2)
    d.text((W - tw - 20, H - 40), lab, font=f, fill=(255, 214, 64))
    name = "combat_worst_case_v2.png" if worst else "combat_typical_v2.png"
    shot.convert("RGB").save(os.path.join(OUT, name))
    json.dump(dict(off=float(off), hits=[(n_, float(v)) for n_, v in hits]), open(os.path.join(SCR, name + ".json"), "w"))
    print(name, "off %.1f" % off, [(n_, round(100 * cv)) for n_, cv in hits], flush=True)


# ------------------------------------------------------------------ drones v2 sheet
def sheet():
    Wd, Hd = 1920, 1080
    Sh = Image.new("RGBA", (Wd, Hd), (16, 15, 22, 255))
    d = ImageDraw.Draw(Sh)
    d.rectangle([0, 0, 8, 64], fill=(255, 214, 64))
    d.text((26, 6), "DRONES v2  +  LOCKED INNER RING", font=f_num(44), fill=(255, 255, 255))
    d.text((26, 56), "Drones 27 % smaller. Not hovered: a thin band (current effect + HP). Hovered: full mini-wheels. "
                     "Stem only without a parasite; on a parasite the drone sits right on it.", font=f_mono(14, False), fill=(185, 185, 200))
    P = S.player()
    cases = [("COLLAPSED  (no parasite)", None, False), ("HOVERED  (no parasite: short stem)", None, True),
             ("COLLAPSED  (on a parasite)", 0.0, False), ("HOVERED  (on a parasite: no stem)", 0.0, True)]
    tw = 470
    for k, (title, par, hov) in enumerate(cases):
        x0 = 10 + k * (tw + 6)
        Sh.alpha_composite(city(tw, 560, 40 + k), (x0, 84))
        spec = copy.deepcopy(P)
        h = S2.host_image(spec, 0.0, hp_number=False)
        c = S2.Comp(h, SIZE)
        top = h[2]["top_r"]
        Q.ring_locked(c, SEGS_TYP, [(0, 0.0)])
        for i in range(6):
            C41.read_block(c, spec, i, 0.0)
        ro = None
        if par is not None:
            _, ro = K.parasite(c, 1, 0.0, top, 0.0)
        if hov:
            Q.drones_full(c, S2.BOTNET_DRONE, 60, 2, spec, 0.0, par_r_out=ro)
        else:
            Q.drones_band(c, S2.BOTNET_DRONE, 60, 2, par_r_out=ro, hovered=False)
        sx, sy = c.PP(c.RA + 70, 60)
        crop = (int(sx - 420), int(sy - 380), int(sx + 420), int(sy + 520))
        fit_into(Sh, c.image(crop=crop), (x0 + 4, 116, x0 + tw - 4, 640))
        d.text((x0 + 10, 90), title, font=f_ui(15, b"Bold SemiCondensed"), fill=(255, 214, 64))
    y0 = 660
    Sh.alpha_composite(city(940, 410, 9), (10, y0))
    d.text((20, y0 + 6), "INNER RING (locked look): textures + extension into the aligned slices", font=f_ui(15, b"Bold SemiCondensed"), fill=(255, 255, 255))
    h = S2.host_image(P, 0.0, hp_number=False)
    c = S2.Comp(h, SIZE)
    Q.ring_locked(c, SEGS_WORST, [(k, 120 * k) for k in range(3)])
    for i in range(6):
        C41.read_block(c, P, i, 0.0)
    fit_into(Sh, trim(at_r(c, 180)), (14, y0 + 30, 946, y0 + 406))
    rules = ["RULES", "- drones: 0.22 of the host (was 0.30)",
             "- no parasite: short stem, drone at RA + 30",
             "- on a parasite: no stem, drone on its edge",
             "- default COLLAPSED: one band, a tile per drone",
             "  (current glyph + value, HP pips)",
             "- HOVER the slice (or aim a card at a drone):",
             "  the band blooms into the full mini-wheels",
             "- inner ring: locked round 39/40 textures; each",
             "  segment extends into its aligned slice"]
    for j, ln in enumerate(rules):
        d.text((980, y0 + 10 + j * 26), ln, font=f_mono(16, False), fill=(255, 214, 64) if j == 0 else (215, 215, 225))
    Sh.convert("RGB").save(os.path.join(OUT, "drones_v2.png"))
    print("sheet", flush=True)


# ------------------------------------------------------------------ gif (both spinners)
NP, NB = 14, 9    # ticks each wheel spins
STEPS = 12


def frame_states():
    out = [(0.0, 0.0, 1.0, "NOW (parasites popped on the needle slices)", 1200)]
    for s in range(1, STEPS + 1):
        q = s / STEPS
        q = 1 - (1 - q) ** 2.2
        out.append((12 * NP * q, 12 * NB * q, 0.0, "SPINNING: parasites stay attached, drones collapsed", 90))
    for p in (0.33, 0.66, 1.0):
        out.append((12 * NP, 12 * NB, p, "SETTLED: the parasite under each needle pops up", 110 if p < 1 else 1600))
    return out


def frame(k):
    rp, rb, pop, cap, dur = frame_states()[k]
    shot, off, hits = screen(True, rp, rb, None, pop, label=None, marks=False)
    d = ImageDraw.Draw(shot)
    f = f_num(28)
    tw = f.getlength(cap)
    d.rounded_rectangle([W / 2 - tw / 2 - 14, 80, W / 2 + tw / 2 + 14, 122], radius=8, fill=(10, 9, 16, 235), outline=(255, 214, 64), width=2)
    d.text((W / 2 - tw / 2, 84), cap, font=f, fill=(255, 214, 64))
    shot.convert("RGB").resize((960, 540), Image.LANCZOS).save(os.path.join(SCR, "gf_%02d.png" % k))
    print("frame", k, flush=True)


def gif():
    st = frame_states()
    fr = [Image.open(os.path.join(SCR, "gf_%02d.png" % k)).convert("RGB") for k in range(len(st))]
    save_gif(fr, [s[4] for s in st], "combat_worst_case_spin.gif")


if __name__ == "__main__":
    os.makedirs(SCR, exist_ok=True)
    w = sys.argv[1]
    if w in ("worst", "typical"):
        still(w == "worst")
    elif w == "sheet":
        sheet()
    elif w == "frame":
        for k in sys.argv[2:]:
            frame(int(k))
    elif w == "gif":
        gif()
    print("done")
