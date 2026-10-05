"""Round 41 v3 combat HUD: nudges above each wheel (CCW left, CW right), the name sticker above RAM, no forecast /
NEXT plates; a result chip next to each HP (this turn if SEND IT now) with a hover tooltip (breakdown).

python combat43.py worst | typical | frame <k...> | gif
"""
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
import stack42 as Q
import combat42 as C42
import combat41 as C41
import specs14 as S
import sat2 as S2
import make_combat as MC
from frames import INK
from slicelib import f_num, f_ui, f_mono, glyph_rgba
from preview15 import dashed_poly
from make_sat2 import save_gif

W, H = 1920, 1080
PLAYER, BOSS = C41.PLAYER, C41.BOSS
PINK, ORANGE = (255, 61, 168), (255, 140, 26)
HPG, RED, CYAN, YEL = (123, 224, 123), (255, 70, 90), (92, 225, 255), (255, 214, 64)
KEEP = {  # hand box checked against the HP readouts below
"status bar": (634, 10, 1288, 76), "hand": (655, 852, 1362, 1080), "RAM + piles": (26, 950, 640, 1062),
        "buttons + SEND IT": (1366, 932, 1830, 1066)}
NUDGE = {"player": [(192, 216, "PI_SPIN_CCW", "Q"), (770, 216, "PI_SPIN_CW", "E")],
         "boss": [(1150, 216, "PI_SPIN_CCW", "A"), (1748, 216, "PI_SPIN_CW", "D")]}
STICKER_XY = (24, 846)
P_HP = (481, 790)      # centre-top of the player HP number
B_HP = (1500, 878)


def nudge(d, img, x, y, gname, key, acc):
    r = 27
    d.ellipse([x - r, y - r, x + r, y + r], fill=(16, 14, 22, 240), outline=acc + (255,), width=3)
    g = glyph_rgba(gname, 34, 2)
    img.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))
    if key:
        d.text((x, y + r + 10), key, font=f_ui(14, b"Bold Condensed"), fill=(190, 190, 205), anchor="mm")
    return (x - r - 2, y - r - 2, x + r + 2, y + r + (20 if key else 2))


def hp_and_chips(img, cx, y, hp, hpmax, chips):
    """chips: [(kind, glyph, text)] in forecast order:
    dmg (red, final damage) | abs (blue, '(N [shield])' absorbed) | gain (green, '+N [shield]') |
    other (red, '-N [icon]') | status (icon + xN)."""
    d = ImageDraw.Draw(img)
    f = f_num(62)
    s = "%d/%d" % (hp, hpmax)
    tw = f.getlength(s)
    x0 = cx - tw / 2 - 40
    d.text((x0, y), s, font=f, fill=HPG + (255,), stroke_width=3, stroke_fill=(6, 16, 8, 255))
    x = x0 + tw + 12
    boxes = [(x0, y + 4, x0 + tw, y + 66)]
    fc = f_num(30)
    chip_boxes = []
    COL = {"dmg": RED, "abs": CYAN, "gain": HPG, "other": RED, "status": (255, 176, 60)}
    for kind, gname, txt in chips:
        col = COL[kind]
        if kind == "abs":  # no box: '(4 [shield])' in blue
            parts = [("(", None), (txt, None), (None, gname), (")", None)]
            xs = x
            for t_, g_ in parts:
                if t_:
                    d.text((xs, y + 19), t_, font=fc, fill=col + (255,))
                    xs += fc.getlength(t_) + (2 if t_ != "(" else 0)
                else:
                    g = glyph_rgba(g_, 24, 2, fill=col)
                    img.alpha_composite(g, (int(xs + 2), int(y + 37 - g.height / 2)))
                    xs += g.width + 2
            chip_boxes.append([x, y + 18, xs, y + 56])
            x = xs + 10
            continue
        g = glyph_rgba(gname, 26, 2, fill=col) if gname else None
        w = (g.width + 6 if g else 0) + fc.getlength(txt) + 14
        bx = [x, y + 18, x + w, y + 56]
        d.rounded_rectangle(bx, radius=8, fill=(12, 10, 18, 240), outline=col + (255,), width=2)
        if kind in ("dmg",):  # number first, no icon: the big final damage
            d.text((x + 7, y + 19), txt, font=fc, fill=col + (255,))
        elif kind == "status":
            img.alpha_composite(g, (int(x + 4), int(y + 37 - g.height / 2)))
            d.text((x + g.width + 8, y + 23), txt, font=f_num(24), fill=(255, 235, 200, 255))
        else:
            d.text((x + 7, y + 19), txt, font=fc, fill=col + (255,))
            img.alpha_composite(g, (int(x + 9 + fc.getlength(txt)), int(y + 37 - g.height / 2)))
        chip_boxes.append(bx)
        x += w + 8
    boxes.append((boxes[0][2] + 12, y + 18, x, y + 56))
    return boxes, chip_boxes

def tooltip(img, anchor_box, lines, acc):
    d = ImageDraw.Draw(img)
    f1, f2 = f_ui(17, b"Bold SemiCondensed"), f_mono(15, False)
    w = max(f2.getlength(l) for l in lines[1:]) + 28
    h = 34 + 22 * (len(lines) - 1) + 10
    x1 = anchor_box[2]
    x0 = min(x1 - w, W - w - 10)
    y1 = anchor_box[1] - 12
    y0 = y1 - h
    d.rounded_rectangle([x0, y0, x0 + w, y1], radius=8, fill=(10, 9, 16, 245), outline=acc + (255,), width=2)
    d.polygon([(anchor_box[0] + 20, y1), (anchor_box[0] + 34, y1), (anchor_box[0] + 27, y1 + 10)], fill=acc + (255,))
    d.text((x0 + 14, y0 + 8), lines[0], font=f1, fill=acc + (255,))
    for j, ln in enumerate(lines[1:]):
        col = (255, 120, 130) if "=" in ln and "HP" in ln else ((140, 230, 255) if "SHIELD" in ln and "+" in ln else (220, 220, 230))
        d.text((x0 + 14, y0 + 34 + j * 22), ln, font=f2, fill=col + (255,))
    # cursor on the chip
    cx, cy = anchor_box[0] + 30, anchor_box[1] + 26
    d.polygon([(cx, cy), (cx + 16, cy + 30), (cx + 6, cy + 27), (cx + 1, cy + 40), (cx - 4, cy + 38), (cx + 1, cy + 25), (cx - 9, cy + 24)],
              fill=(255, 255, 255, 255), outline=INK + (255,))


def sticker():
    body = Image.new("RGBA", (330, 62), (0, 0, 0, 0))
    db = ImageDraw.Draw(body)
    db.rounded_rectangle([0, 0, 329, 61], radius=12, fill=PINK + (255,))
    db.text((18, 6), "CELL-9 // BREAKER", font=f_num(40), fill=(14, 12, 20, 255))
    return MC.vinyl(body, border=7, tilt=2)


def screen(worst, rot_p=0.0, rot_b=0.0, hover=None, pop=1.0, tip=True, marks=True):
    clean, jpg = C41.base_plate()
    M = 600
    canvas = Image.new("RGBA", (W + 2 * M, H + 2 * M), (0, 0, 0, 0))
    canvas.alpha_composite(clean.convert("RGBA"), (M, M))
    ex_all = Image.new("L", canvas.size, 0)
    P = S.player()
    B, bm = S.boss("meridian", 1)
    for spec, sat, cfg, is_p, rot, hv in ((P, S2.BOTNET_DRONE, PLAYER, True, rot_p, hover), (B, C41.COURIER, BOSS, False, rot_b, None)):
        img, cc, al = C42.wheel(spec, sat, worst, is_p, cfg["r"], rot, hv, pop)
        ox, oy = int(M + cfg["c"][0] - cc[0]), int(M + cfg["c"][1] - cc[1])
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sh.putalpha(img.split()[3].point(lambda v: int(v * 0.5)).filter(ImageFilter.GaussianBlur(10)))
        canvas.alpha_composite(sh, (ox + 6, oy + 12))
        canvas.alpha_composite(img, (ox, oy))
        ex_all.paste(al, (ox, oy), al)
    ea = np.asarray(ex_all, np.float32) / 255
    off_pct = float(100 * (ea.sum() - ea[M:M + H, M:M + W].sum()) / max(1, ea.sum()))
    shot = canvas.crop((M, M, M + W, M + H))
    ein = ea[M:M + H, M:M + W]
    d = ImageDraw.Draw(shot)
    boxes = {}
    for name, bx in KEEP.items():
        shot.paste(jpg.crop(bx), bx[:2])
        boxes[name] = bx
    st = sticker()
    shot.alpha_composite(st, STICKER_XY)
    boxes["name sticker"] = (STICKER_XY[0] + 18, STICKER_XY[1] + 18, STICKER_XY[0] + st.width - 18, STICKER_XY[1] + st.height - 18)
    for who, acc in (("player", PINK), ("boss", ORANGE)):
        for k, (x, y, gname, key) in enumerate(NUDGE[who]):
            boxes["%s nudge %s" % (who, "CCW" if k == 0 else "CW")] = nudge(d, shot, x, y, gname, key, acc)
    if worst:  # both resolving slices carry OVERCLOCKED x2 (x1.5) on this screen
        pc_ = [("dmg", None, "-21"), ("status", "ST_OVERCLOCKED", "x2")]
        bc_ = [("dmg", None, "-14"), ("abs", "SHIELD", "4"), ("gain", "SHIELD", "+4"), ("status", "ST_OVERCLOCKED", "x2")]
    else:
        pc_ = [("dmg", None, "-14")]
        bc_ = [("dmg", None, "-8"), ("abs", "SHIELD", "4"), ("gain", "SHIELD", "+4")]
    pb, pchips = hp_and_chips(shot, P_HP[0], P_HP[1], 41, 60, pc_)
    bb, bchips = hp_and_chips(shot, B_HP[0], B_HP[1], 340, 400, bc_)
    boxes["player HP + result"] = (pb[0][0], pb[0][1], pb[1][2], pb[0][3])
    boxes["boss HP + result"] = (bb[0][0], bb[0][1], bb[1][2], bb[0][3])
    hits = []
    for name, (x0, y0, x1, y1) in boxes.items():
        x0, y0, x1, y1 = (int(max(0, x0)), int(max(0, y0)), int(min(W, x1)), int(min(H, y1)))
        hits.append((name, float((ein[y0:y1, x0:x1] > 0.3).mean())))
    if marks:
        for name, cov in hits:
            if cov > 0.02:
                x0, y0, x1, y1 = boxes[name]
                dashed_poly(d, [(x0 - 3, y0 - 3), (x1 + 3, y0 - 3), (x1 + 3, y1 + 3), (x0 - 3, y1 + 3)], (255, 40, 60), 4, dash=14, gap=8)
                s = "%s hides %d%%" % (name, round(100 * cov))
                f = f_ui(15, b"Bold SemiCondensed")
                d.rounded_rectangle([x0, y0 - 24, x0 + f.getlength(s) + 12, y0 - 4], radius=4, fill=(255, 40, 60))
                d.text((x0 + 6, y0 - 23), s, font=f, fill=(255, 255, 255))
    if tip:
        if worst:
            lines = ["IF YOU SEND IT NOW  -  THE MANIFEST", "YOU: ZERO-DAY 12 x1.5 OVERCLOCKED = 18",
                     "   - its SHIELD 4 (absorbed)", "   = -14 HP  (340 -> 326)",
                     "IT: EXPLOIT 14 x1.5 OVERCLOCKED -> -21 HP to you", "    Priority Routing: +4 SHIELD",
                     "    status on its slice: OVERCLOCKED x2"]
        else:
            lines = ["IF YOU SEND IT NOW  -  THE MANIFEST", "YOU: ZERO-DAY 12 (GOOD)", "   - its SHIELD 4 (absorbed)",
                     "   = -8 HP  (340 -> 332)", "IT: EXPLOIT 14 (PERFECT) -> -14 HP to you", "    Priority Routing: +4 SHIELD"]
        tooltip(shot, bchips[0], lines, ORANGE)
    return shot, off_pct, hits


def still(worst):
    shot, off, hits = screen(worst, hover=2 if worst else None)
    lab = ("WORST CASE v4" if worst else "TYPICAL v4") + "  |  off-screen %d%%" % round(off)
    d = ImageDraw.Draw(shot)
    f = f_num(26)
    tw = f.getlength(lab)
    d.rounded_rectangle([W - tw - 30, H - 40, W - 10, H - 6], radius=6, fill=(10, 9, 16, 230), outline=YEL, width=2)
    d.text((W - tw - 20, H - 40), lab, font=f, fill=YEL)
    name = "combat_worst_case_v4.png" if worst else "combat_typical_v4.png"
    shot.convert("RGB").save(os.path.join(OUT, name))
    json.dump(dict(off=off, hits=hits), open(os.path.join(SCR, name + ".json"), "w"))
    print(name, "off %.1f" % off, [(n_, round(100 * cv)) for n_, cv in hits if cv > 0.005], flush=True)


def frame(k):
    rp, rb, pop, cap, dur = C42.frame_states()[k]
    shot, off, hits = screen(True, rp, rb, None, pop, tip=False, marks=False)
    d = ImageDraw.Draw(shot)
    f = f_num(28)
    tw = f.getlength(cap)
    d.rounded_rectangle([W / 2 - tw / 2 - 14, 84, W / 2 + tw / 2 + 14, 126], radius=8, fill=(10, 9, 16, 235), outline=YEL, width=2)
    d.text((W / 2 - tw / 2, 88), cap, font=f, fill=YEL)
    shot.convert("RGB").resize((960, 540), Image.LANCZOS).save(os.path.join(SCR, "g4_%02d.png" % k))
    print("frame", k, flush=True)


def gif():
    st = C42.frame_states()
    fr = [Image.open(os.path.join(SCR, "g4_%02d.png" % k)).convert("RGB") for k in range(len(st))]
    save_gif(fr, [s[4] for s in st], "combat_worst_case_spin_v4.gif")


if __name__ == "__main__":
    os.makedirs(SCR, exist_ok=True)
    w = sys.argv[1]
    if w in ("worst", "typical"):
        still(w == "worst")
    elif w == "frame":
        for k in sys.argv[2:]:
            frame(int(k))
    elif w == "gif":
        gif()
    print("done")
