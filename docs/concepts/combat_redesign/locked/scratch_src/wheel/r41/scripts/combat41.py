"""Round 41: worst-case and typical combat screens in the locked round 31 layout.

python combat41.py worst | typical

Base: round 31's Meridian combat (combat_meridian.jpg) for the HUD, the round 31 backdrop loop (frame 6, no HUD)
for the wheel areas. Wheels are re-rendered with this round's stack (D4 + every layer) at the locked positions:
player centre (481, 490) r = 220, boss centre (1438, 520) r = 236. HUD panels are pasted back ON TOP, as in the game,
and every HUD panel that hides wheel content is outlined in red with the share of its area that is covered.
"""
import copy
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
R31 = os.path.join(OUT, "..", "round31_meridian_combat")

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import sat2 as S2
import sat3 as S3
import stack41 as K
import specs14 as S
import roster_wheel as RW
from frames import INK
from slicelib import R_OUT, R_IN, f_num, f_ui, f_mono, glyph_rgba, icon_block, shadowed
from preview15 import dashed_poly

W, H = 1920, 1080
PLAYER = dict(c=(481, 490), r=220)
BOSS = dict(c=(1438, 520), r=236)
SIZE = (2300, 2300)
COURIER = dict(name="COURIER DRONE", theme="meridian", slots=[("EXPLOIT", 3), ("FIREWALL", 3)], hp=5, hpmax=5)
STATES = [("ST_OVERCLOCKED", (255, 176, 60), "x1.5"), ("ST_CORRUPTED", (255, 70, 160), None), ("ST_ENCRYPTED", (92, 225, 255), None),
          ("ST_PARASITE", (200, 90, 255), "x0.5"), ("ST_LOCKED", (180, 190, 210), None), ("ST_FROZEN", (150, 220, 255), None)]
HUD = {  # locked HUD panels in combat_meridian.jpg
    "status bar": (634, 10, 1288, 76), "player forecast": (30, 84, 433, 202), "boss forecast": (1558, 84, 1914, 202),
    "name sticker": (78, 734, 428, 834), "player HP + NEXT": (420, 795, 715, 860), "boss HP + NEXT": (1345, 862, 1712, 932),
    "hand": (655, 852, 1362, 1080), "RAM + piles": (26, 950, 640, 1062), "buttons + SEND IT": (1366, 932, 1830, 1066),
    "nudge Q": (160, 660, 216, 724), "nudge E": (744, 660, 800, 724),
}


def base_plate():
    jpg = Image.open(os.path.join(R31, "combat_meridian.jpg")).convert("RGB").resize((W, H))
    g = Image.open(os.path.join(R31, "meridian_backdrop_motion.gif"))
    g.seek(6)
    bd = g.convert("RGB").resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2.5))
    a = np.asarray(bd, np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    pool = np.zeros((H, W), np.float32)
    for wh in (PLAYER, BOSS):
        q = np.hypot(xx - wh["c"][0], yy - wh["c"][1]) / (wh["r"] * 1.25)
        pool = np.maximum(pool, np.exp(-q ** 4))
    dim = 0.80 * (1 - 0.5 * pool)
    clean = Image.fromarray(np.clip(a * dim[..., None], 0, 255).astype(np.uint8))
    return clean, jpg


def state_overlay(c, slot, rot, k, stacks):
    gname, col, rule = STATES[k % len(STATES)]
    a = 60 * slot + rot
    mask = Image.new("L", (c.W, c.H), 0)
    ImageDraw.Draw(mask).polygon([c.PP(R_OUT - 12, a - 27 + 54 * j / 40) for j in range(41)] +
                                 [c.PP(R_IN + 12, a + 27 - 54 * j / 40) for j in range(41)], fill=255)
    wash = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wash)
    for j in range(10):
        r = R_IN + 20 + j * 22
        wd.line([c.PP(r, a - 27 + 54 * q / 30) for q in range(31)], fill=col + (60,), width=8)
    out = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
    out.paste(wash, (0, 0), mask)
    c.top.alpha_composite(out)
    bx, by = c.PP(R_OUT - 46, a + 21)
    d = ImageDraw.Draw(c.top)
    r = 22
    d.ellipse([bx - r, by - r, bx + r, by + r], fill=(20, 16, 10, 255), outline=col + (255,), width=3)
    g = glyph_rgba(gname, 30, 2, fill=col)
    c.top.alpha_composite(g, (int(bx - g.width / 2), int(by - g.height / 2)))
    f = f_num(20)
    s = "x%d" % stacks
    tw = f.getlength(s)
    d.rounded_rectangle([bx + 8, by - r - 10, bx + 18 + tw, by - r + 14], radius=5, fill=INK + (255,), outline=col + (255,), width=2)
    d.text((bx + 13, by - r - 10), s, font=f, fill=(255, 240, 220, 255))
    if rule:
        d.rounded_rectangle([bx - 20, by + r + 2, bx + 22, by + r + 22], radius=4, fill=col + (255,))
        d.text((bx - 15, by + r + 1), rule, font=f_num(17), fill=INK + (255,))


def read_block(c, spec, slot, rot):
    sl = spec["slots"][slot]
    val = sl["value"]
    if sl["program"] == "NULL" or (sl.get("special") and sl["special"] != "tariff"):
        val = None
    blk = shadowed(icon_block(sl["program"], val, 60, 1, glyph=RW.SPECIAL_GLYPH.get(sl.get("special"))), 1)
    x, y = c.PP(R_IN + 0.6 * (R_OUT - R_IN), 60 * slot + rot)
    c.top.alpha_composite(blk, (int(x - blk.width / 2), int(y - blk.height / 2)))


def wheel(spec, sat, worst, is_player, r_px):
    """Returns (RGBA wheel image at r_px, centre px, extras-only alpha image)."""
    spec = copy.deepcopy(spec)
    if is_player:
        spec["slot_tier"] = {0: 3, 1: 2, 2: 1, 3: 2, 4: 3, 5: 1} if worst else {0: 2, 3: 1}
    else:
        spec["corp_tier"] = 3
    spec["variant"] = "w41" if worst else "t41"
    h = S2.host_image(spec, 0.0, hp_number=False)
    c = S2.Comp(h, SIZE)
    top = h[2]["top_r"]
    slots = range(6) if worst else ([1] if is_player else [2])
    for i in range(6):
        if is_player and (worst or i == 1):
            K.ring_extension(c, i, 0.0)
        if is_player and (worst or i in (1,)):
            K.firmware_socket(c, i, 0.0)
        if worst or i == (3 if is_player else 4):
            state_overlay(c, i, 0.0, i, 2 + i % 4 if worst else 1)
    if is_player:
        K.sub_needle(c, 1, 0.0)
    for i in range(6):
        read_block(c, spec, i, 0.0)
    extras = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
    par_slots = range(6) if worst else ([] if is_player else [3])
    for i in par_slots:
        st = 1.0 if i == 0 else 0.0
        K.parasite(c, i, 0.0, top, st, lit=1 if st else None)
    for i in (range(6) if worst else slots):
        n = 2 if worst else 1
        par = (1.0 if i == 0 else 0.0) if (worst or i in par_slots) else None
        K.put_drones(c, sat, 60 * i, n, spec, r_dock=K.drone_r(c, par, top) if par is not None else None)
    # extras-only alpha: everything drawn outside the host's frame edge
    yy, xx = np.mgrid[0:c.H, 0:c.W].astype(np.float32)
    outside = np.hypot(xx - c.C[0], yy - c.C[1]) > c.RA + 4
    full = c.image()
    al = np.asarray(full.split()[3], np.float32) / 255 * outside
    k = r_px / R_OUT
    img = full.resize((int(c.W * k), int(c.H * k)), Image.LANCZOS)
    alim = Image.fromarray((al * 255).astype(np.uint8)).resize(img.size, Image.BILINEAR)
    return img, (c.C[0] * k, c.C[1] * k), alim


def build(worst):
    clean, jpg = base_plate()
    canvas = Image.new("RGBA", (W + 1200, H + 1200), (0, 0, 0, 0))   # margin to measure off-screen spill
    M = 600
    canvas.alpha_composite(clean.convert("RGBA"), (M, M))
    ex_all = Image.new("L", canvas.size, 0)
    P = S.player()
    B, bm = S.boss("meridian", 1)
    for spec, sat, cfg, is_p in ((P, S2.BOTNET_DRONE, PLAYER, True), (B, COURIER, BOSS, False)):
        img, cc, al = wheel(spec, sat, worst, is_p, cfg["r"])
        ox, oy = int(M + cfg["c"][0] - cc[0]), int(M + cfg["c"][1] - cc[1])
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sh.putalpha(img.split()[3].point(lambda v: int(v * 0.5)).filter(ImageFilter.GaussianBlur(10)))
        canvas.alpha_composite(sh, (ox + 6, oy + 12))
        canvas.alpha_composite(img, (ox, oy))
        ex_all.paste(al, (ox, oy), al)
        print("wheel", is_p, flush=True)
    ea = np.asarray(ex_all, np.float32) / 255
    off = ea.sum() - ea[M:M + H, M:M + W].sum()
    off_pct = 100 * off / max(1, ea.sum())
    shot = canvas.crop((M, M, M + W, M + H))
    ein = ea[M:M + H, M:M + W]
    d = ImageDraw.Draw(shot)
    hits = []
    for name, (x0, y0, x1, y1) in HUD.items():
        shot.paste(jpg.crop((x0, y0, x1, y1)), (x0, y0))
        cov = float((ein[y0:y1, x0:x1] > 0.3).mean())
        hits.append((name, cov))
    for name, cov in hits:
        x0, y0, x1, y1 = HUD[name]
        if cov > 0.02:
            pts = [(x0 - 3, y0 - 3), (x1 + 3, y0 - 3), (x1 + 3, y1 + 3), (x0 - 3, y1 + 3)]
            dashed_poly(d, pts, (255, 40, 60), 4, dash=14, gap=8)
            s = "%s hides %d%%" % (name, round(100 * cov))
            f = f_ui(15, b"Bold SemiCondensed")
            tw = f.getlength(s)
            ty = y0 - 24 if y0 > 30 else y1 + 6
            d.rounded_rectangle([x0, ty, x0 + tw + 12, ty + 20], radius=4, fill=(255, 40, 60))
            d.text((x0 + 6, ty + 1), s, font=f, fill=(255, 255, 255))
    lab = "WORST CASE" if worst else "TYPICAL"
    f = f_num(26)
    d.rounded_rectangle([W - 330, H - 40, W - 10, H - 6], radius=6, fill=(10, 9, 16, 230), outline=(255, 214, 64), width=2)
    d.text((W - 320, H - 40), "%s  |  off-screen %d%%" % (lab, round(off_pct)), font=f, fill=(255, 214, 64))
    name = "combat_worst_case.png" if worst else "combat_typical.png"
    shot.convert("RGB").save(os.path.join(OUT, name))
    with open(os.path.join(OUT, "scratch", name + ".txt"), "w") as fh:
        fh.write("offscreen %.1f\n" % off_pct)
        for n_, cov in hits:
            fh.write("%s %.1f\n" % (n_, 100 * cov))
    print(name, "off %.1f" % off_pct, [(n_, round(100 * cv)) for n_, cv in hits], flush=True)


if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "scratch"), exist_ok=True)
    build(sys.argv[1] == "worst")
