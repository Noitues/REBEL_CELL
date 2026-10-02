"""Round 17: animated card-play preview (preview.gif + preview_storyboard.png).

Example: The Civic Core (Halcyon boss) with 2 needles (ticks 0 and 20) and 1 docked Civic Drone; the player
hovers HEAVY SPIN 9.
- The slices turn 9 ticks clockwise, so a needle reads the slice that is now 9 ticks anticlockwise of it:
  needle 1 (top) lands at -108 deg, right beside real needle 2 (-120 deg); needle 2 lands at +132 deg.
- The drone rides its slice: it ends 9 ticks clockwise, from +40 deg to +148 deg.
Only ONE directional set: large ghosted chevrons outside the rim from needle 1 to its landing, chasing in the
direction of travel; other needles and the drone are inferred (ghosts only, no extra trace).

python preview17.py      # writes ../preview.gif and ../preview_storyboard.png
"""
import copy
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import frames as F
from frames import P, Q, INK
import d4corp as D
import specs14 as S
import preview16 as PV
from preview15 import dashed_poly
from slicelib import R_OUT, R_IN, PROGRAMS, f_num, f_ui, f_mono, glyph_rgba
import roster_wheel as RW

SS = 1
N = 9
WHITE = (255, 255, 255)
YEL = (255, 214, 64)
DRONE_A = 40.0


def spec():
    s, m = S.boss("halcyon", 2)
    s = copy.deepcopy(s)
    s["pointers"] = [0, 20]
    s["drones"] = [dict(name="Civic Drone", hp=5)]
    s["drone_angles"] = [DRONE_A]
    s["full_blades"] = True
    s["corp_tier"] = 3
    s["variant"] = "pv17"
    s["boss"] = dict(s["boss"], sub="HALCYON CIVIC  |  BOSS  |  PHASE 2")
    return s


def base():
    sp = spec()
    im, c, meta = D.render(sp, ss=SS, hp_number=True)
    full = Image.new("RGBA", (F.CW * SS, F.CH * SS), (0, 0, 0, 0))
    full.alpha_composite(im, (int(F.CX * SS - c[0]), int(F.CY * SS - c[1])))
    Ls = D.slice_layers(sp, SS, False, 0.0)
    return sp, full, meta, Ls


def chevron(d, gd, a, r, size, alpha, direction=-1):
    """A large chevron at angle a on radius r, pointing along the travel direction (anticlockwise = -1)."""
    w = size
    da = math.degrees(w / r)
    tip = P(r, a + direction * da * 0.55, SS)
    l0, l1 = P(r + w * 0.62, a - direction * da * 0.45, SS), P(r - w * 0.62, a - direction * da * 0.45, SS)
    m0, m1 = P(r + w * 0.62, a - direction * da * 1.0, SS), P(r - w * 0.62, a - direction * da * 1.0, SS)
    notch = P(r, a, SS)
    poly = [l0, tip, l1, m1, notch, m0]
    if alpha > 0.02:
        gd.polygon(poly, fill=YEL + (int(230 * alpha),))
    col = tuple(int(WHITE[i] * (1 - alpha) + YEL[i] * alpha) for i in range(3))
    d.polygon(poly, fill=col + (int(50 + 205 * alpha),), outline=INK + (int(90 + 165 * alpha),), width=int(3 * SS))


def label(d, xy, text, sub=None, col=WHITE, anchor="mm", size=24):
    f = f_num(int(size * SS))
    fs = f_ui(int(15 * SS), b"Bold SemiCondensed")
    tw = max(f.getlength(text), fs.getlength(sub) if sub else 0)
    x, y = xy
    h = (size + (20 if sub else 0) + 12) * SS
    if anchor == "mm":
        x0, y0 = x - tw / 2 - 10 * SS, y - h / 2
    elif anchor == "lm":
        x0, y0 = x, y - h / 2
    else:  # rm
        x0, y0 = x - tw - 20 * SS, y - h / 2
    d.rounded_rectangle([x0, y0, x0 + tw + 20 * SS, y0 + h], radius=7 * SS, fill=(10, 9, 16, 235), outline=col + (255,), width=int(2 * SS))
    d.text((x0 + 10 * SS, y0 + 4 * SS), text, font=f, fill=col + (255,))
    if sub:
        d.text((x0 + 10 * SS, y0 + (size + 8) * SS), sub, font=fs, fill=(200, 200, 215, 255))


def leader(d, p0, p1, col=WHITE):
    d.line([p0, p1], fill=INK + (255,), width=int(5 * SS))
    d.line([p0, p1], fill=col + (255,), width=int(2.5 * SS))
    d.ellipse([p0[0] - 5 * SS, p0[1] - 5 * SS, p0[0] + 5 * SS, p0[1] + 5 * SS], fill=col + (255,), outline=INK + (255,))


def overlay(sp, meta, Ls, state):
    """state: dict(hover, chase (0..1 or None), ghosts (0..1), labels set)."""
    F.set_centre()
    im, d = F.layer(SS)
    gl, gd = F.layer(SS)
    RA = meta["hp_r"] - 36
    top = meta["top_r"]
    R_ch = RA + 62
    a1 = 0.0
    a_land1 = a1 - 12 * N
    a2 = sp["pointers"][1] * 12.0
    a2 = a2 if a2 <= 180 else a2 - 360
    a_land2 = a2 - 12 * N
    a_d_end = DRONE_A + 12 * N
    acc = D.acc_of(sp)
    # --- chevron chase (one set, needle 1 only)
    ch = state.get("chase")
    if ch is not None:
        n_ch = N
        head = ch * (n_ch + 1.5)
        for j in range(n_ch):
            a = a1 - 12 * (j + 0.6)
            if ch >= 1.0:
                al = 0.35  # held: all ghosted
            else:
                dist = head - (j + 1)
                al = 0.18 + 0.82 * math.exp(-(dist / 1.1) ** 2) if dist > -1.5 else 0.10
                if dist > 1.5:
                    al = max(al, 0.35)
            chevron(d, gd, a, R_ch, 64, al)
    g = state.get("ghosts", 0.0)
    if g > 0:
        gim, gdr = F.layer(SS)
        ggl, ggd = F.layer(SS)
        for k, (a_l) in enumerate((a_land1, a_land2)):
            L = Ls[D.index_at(sp, a_l)]
            pc = PROGRAMS[L["prog"]]["col"]
            wp = F.wedge_pts(L["a0"] + 1.2, L["a0"] + L["span"] - 1.2, R_IN + 4, R_OUT - 4, SS, 50)
            ggd.polygon(wp, outline=pc + (255,), width=int(10 * SS))
            dashed_poly(gdr, wp, pc + (255,), int(4.5 * SS), dash=12 * SS, gap=8 * SS)
            gdr = PV.ghost_blade(gim, gdr, ggd, SS, a_l, RA, top, 1.0, L, pc, k + 1, 2)
        # ghost drone at its end spot
        R_dr = RA + 74
        x, y = P(R_dr, a_d_end, SS)
        r = 46 * SS
        circ = [(x + r * math.cos(math.radians(j * 6)), y + r * math.sin(math.radians(j * 6))) for j in range(60)]
        fill = Image.new("RGBA", gim.size, (0, 0, 0, 0))
        ImageDraw.Draw(fill).ellipse([x - r, y - r, x + r, y + r], fill=acc + (120,))
        gim.alpha_composite(fill)
        gdr = ImageDraw.Draw(gim)
        dashed_poly(gdr, circ, acc + (255,), int(4 * SS), dash=10 * SS, gap=6 * SS)
        gg = glyph_rgba("DRONE", int(46 * SS), 2 * SS)
        gg.putalpha(gg.split()[3].point(lambda v: int(v * 0.85)))
        gim.alpha_composite(gg, (int(x - gg.width / 2), int(y - gg.height / 2)))
        if g < 1:
            for lay in (gim, ggl):
                lay.putalpha(lay.split()[3].point(lambda v: int(v * g)))
        F.add_glow_img = None
        im.alpha_composite(ggl.filter(ImageFilter.GaussianBlur(6 * SS)))
        im.alpha_composite(gim)
        d = ImageDraw.Draw(im)
    gd2 = ImageDraw.Draw(gl)
    # --- labels
    lab = state.get("labels", set())
    if "now" in lab:
        p = P(top - 30, a1, SS)
        label(d, (p[0] + 90 * SS, p[1]), "NEEDLE 1  (now)", "the top needle", col=WHITE, anchor="lm")
        p = P(top - 10, a2, SS)
        label(d, (p[0] - 40 * SS, p[1] + 70 * SS), "NEEDLE 2  (now)", col=WHITE)
        p = P(RA + 74, DRONE_A, SS)
        leader(d, (p[0] + 40 * SS, p[1] - 30 * SS), (p[0] + 110 * SS, p[1] - 110 * SS))
        label(d, (p[0] + 110 * SS, p[1] - 110 * SS), "DRONE  (now)", "docked on the CITATION slice", col=acc, anchor="lm")
    if "dir" in lab:
        label(d, ((F.CX + 230) * SS, (F.CY - 590) * SS), "SPIN 9: the wheel turns 9 ticks", "chevrons = needle 1's path to its landing", col=YEL, anchor="lm", size=22)
    if "land" in lab:
        p = P(top - 30, a_land1, SS)
        q = ((F.CX - 600) * SS, (F.CY - 160) * SS)
        leader(d, p, (q[0] + 120 * SS, q[1] + 26 * SS), YEL)
        label(d, q, "1 LANDS HERE", "right beside real needle 2", col=YEL, anchor="lm")
        p = P(top - 20, a_land2, SS)
        label(d, (p[0] + 50 * SS, p[1] - 60 * SS), "2 LANDS HERE", "inferred: same 9 ticks", col=YEL, anchor="lm")
        p = P(RA + 74, a_d_end, SS)
        leader(d, (p[0] + 10 * SS, p[1] + 44 * SS), (p[0] - 20 * SS, p[1] + 100 * SS), acc)
        label(d, (p[0] - 20 * SS, p[1] + 124 * SS), "DRONE ENDS HERE", "it rides its slice, 9 ticks clockwise", col=acc, anchor="mm")
    out = gl.filter(ImageFilter.GaussianBlur(7 * SS))
    out.alpha_composite(im)
    return out


CROP = (F.CX - 700, F.CY - 700, F.CX + 700, F.CY + 600)


def frame(full, ov, caption, card=None):
    cw, chh = int((CROP[2] - CROP[0]) * SS), int((CROP[3] - CROP[1]) * SS)
    bg = Image.open(os.path.join(OUT, "..", "round6_city_restyle", "views", "restyle_night_full.png")).convert("RGB")
    bg = bg.crop((300, 100, 300 + cw, 100 + chh)).filter(ImageFilter.GaussianBlur(3))
    img = Image.fromarray((np.asarray(bg, np.float32) * 0.30).astype(np.uint8)).convert("RGBA")
    off = (int(-CROP[0] * SS), int(-CROP[1] * SS))
    img.alpha_composite(full, off)
    img.alpha_composite(ov, off)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, img.width, 64], fill=(10, 9, 16, 235))
    d.text((18, 10), caption, font=f_num(40), fill=(255, 255, 255))
    if card is not None:
        img.alpha_composite(card, (24, 116))
        d.rounded_rectangle([24, 78, 170, 110], radius=6, fill=(10, 9, 16, 235), outline=YEL)
        d.text((36, 80), "HOVERED", font=f_ui(20, b"Bold SemiCondensed"), fill=YEL)
    return img


def main():
    import make_combat as MC
    sp, full, meta, Ls = base()
    card = MC.card_img([c for c in MC.CARDS if c["name"] == "HEAVY SPIN"][0], 160, 214)
    seq = []  # (state, caption, card?, duration ms, storyboard label or None)
    seq.append((dict(labels={"now"}), "1  NOW: 2 needles + 1 docked drone", False, 1800, "1  NOW"))
    seq.append((dict(labels={"now"}), "2  HOVER HEAVY SPIN 9", True, 900, "2  HOVER"))
    steps = 12
    for i in range(steps + 1):
        c = i / steps
        lab = {"dir"}
        sb = "3  CHEVRON CHASE" if i == steps // 2 else None
        seq.append((dict(chase=c, labels=lab), "3  the chevrons chase from needle 1 to its landing", True, 90, sb))
    for i in range(1, 5):
        g = i / 4
        sb = "4  GHOSTS APPEAR" if i == 2 else None
        seq.append((dict(chase=1.0, ghosts=g, labels={"dir"}), "4  ghosts at every landing", True, 90, sb))
    seq.append((dict(chase=1.0, ghosts=1.0, labels={"land"}), "5  where each needle lands, where the drone ends", True, 2600, "5  LANDINGS (hold)"))
    seq.append((dict(chase=1.0, ghosts=1.0, labels=set()), "6  held while the card stays hovered", True, 1200, "6  CLEAN HOLD"))
    frames, durs, board = [], [], []
    cache = {}
    for st, cap, has_card, dur, sb in seq:
        key = repr(sorted((k, (sorted(v) if isinstance(v, set) else v)) for k, v in st.items())) + cap
        if key not in cache:
            ov = overlay(sp, meta, Ls, st)
            cache[key] = frame(full, ov, cap, card if has_card else None)
        fr = cache[key]
        frames.append(fr)
        durs.append(dur)
        if sb:
            board.append((sb, fr))
        print("frame", cap[:30], flush=True)
    gw = 820
    gif = [f.resize((gw, int(f.height * gw / f.width)), Image.LANCZOS).convert("RGB").quantize(colors=192, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
    p = os.path.join(OUT, "preview.gif")
    gif[0].save(p, save_all=True, append_images=gif[1:], duration=durs, loop=0, optimize=True)
    print("gif KB", os.path.getsize(p) // 1024, flush=True)
    # storyboard: 6 key frames, 3 x 2
    W, H = 1920, 1080
    sb = Image.new("RGBA", (W, H), (16, 15, 22, 255))
    d = ImageDraw.Draw(sb)
    d.text((20, 8), "CARD-PLAY PREVIEW  -  storyboard (HEAVY SPIN 9 on The Civic Core: 2 needles + 1 drone)", font=f_num(36), fill=(255, 255, 255))
    tw, th = 620, 500
    for i, (lab, fr) in enumerate(board[:6]):
        x, y = 15 + (i % 3) * (tw + 12), 60 + (i // 3) * (th + 14)
        k = min(tw / fr.width, th / fr.height)
        t_ = fr.resize((int(fr.width * k), int(fr.height * k)), Image.LANCZOS)
        sb.alpha_composite(t_, (x + (tw - t_.width) // 2, y))
        d.rectangle([x, y, x + tw - 1, y + th - 1], outline=(70, 70, 84))
    sb.convert("RGB").save(os.path.join(OUT, "preview_storyboard.png"))
    print("storyboard", len(board), flush=True)


if __name__ == "__main__":
    main()
