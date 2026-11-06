"""Round 40 build: python make_r40.py sheet | replace | options | trigger"""
import copy
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import sat2 as S2
import sat3 as S3
import specs14 as S
import roster as RS
from frames import INK
from slicelib import f_num, f_ui, f_mono, R_OUT
from make_sat2 import city, tag, fit_into, trim, at_r, save_gif, botnet, care_swarm, P_SATS, E_SATS, NEW_DRONE

BG = (16, 15, 22)
YEL = (255, 214, 64)
WHITE = (255, 255, 255)
PAR = (214, 60, 255)
SIZE = (1760, 1760)


def header(Sh, title, sub, col=YEL):
    d = ImageDraw.Draw(Sh)
    d.rectangle([0, 0, 8, 64], fill=col)
    d.text((26, 6), title, font=f_num(44), fill=WHITE)
    d.text((26, 56), sub, font=f_mono(14, False), fill=(185, 185, 200))
    return d


def labelled(c, cap, scale=0.38, seed=5):
    im = c.image(scale=scale)
    base = city(im.width, im.height, seed)
    base.alpha_composite(im)
    d = ImageDraw.Draw(base)
    d.rectangle([0, 0, base.width, 52], fill=(10, 9, 16, 240))
    d.text((14, 8), cap, font=f_num(30), fill=WHITE)
    return base


# ================================================================== replace
def replace_frames(eb, host=None):
    """yields (comp, caption, duration)"""
    host = host or S2.host_image(eb, 0.0, hp_number=True)
    a = 120.0
    old = dict(S2.CARE_DRONE, hp=2)
    others = [(0, S2.CARE_DRONE), (4, S2.CARE_DRONE)]
    hover_r = S2.dock_r(host[2]["hp_r"] - 36) + 300
    out = []

    def base(dock_glow=1.0, with_dock=True):
        c = S3.compose(eb, others, host=host, size=(2400, 2400))
        if with_dock:
            S3.dock(c, a, old, eb, glow=dock_glow)
        return c

    def hover(c, k, bob=0.0, alpha=1.0, r=None):
        rr = hover_r if r is None else r
        c.put_sat(NEW_DRONE, a, offset=rr - S2.dock_r(c.RA) + bob, alpha=alpha)
        x, y = c.PP(rr + bob, a)
        d = ImageDraw.Draw(c.top)
        R = S2.SAT_R + 18
        circ = [(x + R * math.cos(math.radians(j * 6)), y + R * math.sin(math.radians(j * 6))) for j in range(60)]
        S2.dashed_poly(d, circ, (255, 214, 64, int(255 * k)), 5, dash=16, gap=10)
    # 1 now
    c = base()
    c.put_sat(old, a, state=dict(hp=2))
    out.append((c, "1  NOW: a drone (2 HP) docked on slice 3", 1200))
    # 2 the new drone arrives and hovers, waiting
    for k, q in enumerate((0.3, 0.6, 1.0)):
        c = base()
        c.put_sat(old, a, state=dict(hp=2))
        hover(c, 1.0, r=hover_r + 400 * (1 - q), alpha=0.4 + 0.6 * q)
        out.append((c, "2  NEW drone arrives and HOVERS, waiting", 120 if q < 1 else 700))
    # 3 old one undocks into GREEN bits that stream back to the core
    for k, q in enumerate((0.1, 0.25, 0.4, 0.55, 0.7, 0.85, 1.0)):
        c = base(dock_glow=1 - q)
        sx, sy = c.PP(S2.dock_r(c.RA), a)
        if q < 0.6:
            sim, sc = S2.render_sat(old, a, state=dict(hp=2))
            K = S2.SAT_K
            sim = sim.resize((int(sim.width * K), int(sim.height * K)), Image.LANCZOS)
            sim = S3.dissolve(sim, q / 0.6)
            c.top.alpha_composite(sim, (int(sx - sc[0] * K), int(sy - sc[1] * K)))
        S3.green_stream(c.top, sx, sy, c.C[0], c.C[1], q)
        hover(c, 1.0, bob=8 * math.sin(q * 6.28))
        out.append((c, "3  the OLD drone undocks: GREEN bits return to the core", 110))
    # 4 core pulse + the new one installs
    for k, q in enumerate((0.0, 0.35, 0.7, 1.0)):
        c = base(dock_glow=q)
        d = ImageDraw.Draw(c.top)
        if k == 0:
            for rr, al in ((150, 200), (200, 120)):
                d.ellipse([c.C[0] - rr, c.C[1] - rr, c.C[0] + rr, c.C[1] + rr], outline=(123, 224, 123, al), width=10)
        e = q * q * (3 - 2 * q)
        r = hover_r + (S2.dock_r(c.RA) - hover_r) * e
        if q < 1:
            hover(c, 1 - q, r=r)
        else:
            c.put_sat(NEW_DRONE, a)
        out.append((c, "4  NEW drone installs" if q < 1 else "4  INSTALLED", 130 if q < 1 else 1500))
    return out


def replace_gif():
    eb = care_swarm()
    fr, du = [], []
    for c, cap, dur in replace_frames(eb):
        fr.append(labelled(c, cap, 0.30).convert("RGB"))
        du.append(dur)
        print("f", cap[:20], flush=True)
    save_gif(fr, du, "replace.gif")


# ================================================================== satellites v3 sheet
def sheet():
    W, H = 1920, 1500
    Sh = Image.new("RGBA", (W, H), BG + (255,))
    d = header(Sh, "SATELLITES v3  -  blended docking, replace", "The docked slice's own outline swells out of the rim into one curved lobe that wraps the satellite "
                   "(no added struts or clamps). Replace: the old satellite returns to the core as green bits; the new one waits, then installs.")
    pb, eb = botnet(), care_swarm()
    for k, (spec, sats, title) in enumerate(((pb, P_SATS, "PLAYER  BOTNET  r = 220"), (eb, E_SATS, "ENEMY  CARE SWARM  r = 220"))):
        x0 = 10 + k * 645
        Sh.alpha_composite(city(635, 760, 20 + k), (x0, 84))
        c = S3.compose(spec, sats, size=SIZE)
        fit_into(Sh, trim(at_r(c, 220)), (x0 + 4, 114, x0 + 631, 840))
        d.text((x0 + 10, 90), title, font=f_ui(15, b"Bold SemiCondensed"), fill=WHITE)
    x0 = 1300
    Sh.alpha_composite(city(610, 470, 33), (x0, 84))
    d.text((x0 + 10, 90), "THE DOCK, close up: the slice outline (its program colour) becomes the lobe", font=f_ui(14, b"Bold SemiCondensed"), fill=YEL)
    c = S3.compose(eb, E_SATS, size=SIZE)
    sx, sy = c.PP(S2.dock_r(c.RA), 120)
    cx, cy = (sx + c.C[0]) / 2 + 40, (sy + c.C[1]) / 2 + 40
    det = c.image(crop=(int(cx - 330), int(cy - 250), int(cx + 330), int(cy + 250)))
    fit_into(Sh, det, (x0 + 6, 116, x0 + 604, 548))
    Sh.alpha_composite(city(610, 280, 44), (x0, 560))
    d.text((x0 + 10, 566), "r = 60", font=f_ui(15, b"Bold SemiCondensed"), fill=YEL)
    for k, (spec, sats) in enumerate(((pb, P_SATS), (eb, E_SATS))):
        c = S3.compose(spec, sats, size=SIZE, lod=True)
        fit_into(Sh, trim(at_r(c, 60)), (x0 + 20 + k * 300, 590, x0 + 290 + k * 300, 834))
    y0 = 870
    d.line([(20, y0 - 8), (1900, y0 - 8)], fill=(60, 60, 74))
    d.text((24, y0), "REPLACE  (a new satellite on an occupied slice; see replace.gif)", font=f_num(28), fill=YEL)
    frames = replace_frames(eb)
    pick = [frames[0], frames[3], frames[7], frames[10], frames[-1]]
    tw = 374
    for k, (c, cap, dur) in enumerate(pick):
        x = 10 + k * (tw + 6)
        Sh.alpha_composite(city(tw, 570, 60 + k), (x, y0 + 44))
        a = 120.0
        cx, cy = c.PP(S2.dock_r(c.RA) + 110, a)
        im = c.image(crop=(int(cx - 560), int(cy - 600), int(cx + 560), int(cy + 600)))
        fit_into(Sh, im, (x + 4, y0 + 96, x + tw - 4, y0 + 610))
        for j, ln in enumerate(S3_wrap(cap, 34)):
            d.text((x + 10, y0 + 52 + j * 18), ln, font=f_mono(13, False), fill=(215, 215, 225))
    Sh.convert("RGB").save(os.path.join(OUT, "satellites_v3.png"))
    print("sheet", flush=True)


def S3_wrap(s, n):
    out, cur = [], ""
    for w in s.split():
        if cur and len(cur) + len(w) + 1 > n:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    out.append(cur)
    return out


# ================================================================== parasite: needle options
def player():
    return S.player()


ROT_LAND = 300.0  # the parasited slot 1 (EXPLOIT 6) under the needle


def options():
    W, H = 1920, 1300
    Sh = Image.new("RGBA", (W, H), BG + (255,))
    d = header(Sh, "PARASITE RING v2  -  on the PLAYER's wheel, 3 needle layouts", "Thinner ring, big glyph + value per sub-slice (faded red), real slice effects incl. ones that help the BOSS "
                   "(PATCH heals the boss). Only in effect when the NEEDLE lands on the host slice.", PAR)
    P = player()
    h = S2.host_image(P, rot=ROT_LAND, hp_number=True)
    top = h[2]["top_r"]
    names = {"A": "A  BEYOND THE TIP  (recommended)", "B": "B  UNDER THE BLADE", "C": "C  AT THE SLICE ROOT"}
    verdict = {"A": ["+ needle and ring never overlap", "+ all 3 sub-slices always visible", "+ beam = obvious trigger link", "- adds height above the wheel"],
               "B": ["+ compact, sits in the blade band", "- the blade HIDES the sub-slice", "  in line, exactly the one that", "  triggers"],
               "C": ["+ reads as the anti-inner-ring", "+ nothing added outside the wheel", "- small at the root; crowds the", "  host slice and the hub"]}
    for k, L in enumerate("ABC"):
        x0 = 10 + k * 637
        Sh.alpha_composite(city(627, 840, 40 + k), (x0, 84))
        c = S2.Comp(h, SIZE)
        ri, ro, a0, sp = S3.parasite2(c, 1, L, rot=ROT_LAND, top=top, lit=1)
        S3.link(c, L, ri, ro, top)
        im = c.image(crop=(int(c.C[0] - 520), int(c.C[1] - 860), int(c.C[0] + 520), int(c.C[1] + 300)), scale=0.6)
        fit_into(Sh, im, (x0 + 4, 120, x0 + 623, 830))
        d.text((x0 + 10, 90), names[L], font=f_num(26), fill=YEL if L == "A" else WHITE)
        for j, ln in enumerate(verdict[L]):
            d.text((x0 + 14, 128 + j * 18), ln, font=f_mono(14, False), fill=(130, 230, 140) if ln.startswith("+") else ((255, 140, 150) if ln.startswith("-") else (215, 215, 225)))
    y0 = 940
    d.line([(20, y0 - 8), (1900, y0 - 8)], fill=(60, 60, 74))
    Sh.alpha_composite(city(700, 350, 51), (10, y0))
    d.text((20, y0 + 6), "A on the player wheel, r = 220 (parasite on EXPLOIT 6, away from the needle)", font=f_ui(14, b"Bold SemiCondensed"), fill=YEL)
    h0 = S2.host_image(P, rot=0.0, hp_number=False)
    c = S2.Comp(h0, SIZE)
    S3.parasite2(c, 1, "A", rot=0.0, top=h0[2]["top_r"])
    fit_into(Sh, trim(at_r(c, 140)), (14, y0 + 30, 706, y0 + 346))
    Sh.alpha_composite(city(300, 350, 52), (720, y0))
    d.text((730, y0 + 6), "r = 60", font=f_ui(14, b"Bold SemiCondensed"), fill=YEL)
    c = S2.Comp(S2.host_image(P, rot=0.0, hp_number=False), SIZE)
    S3.parasite2(c, 1, "A", rot=0.0, top=h0[2]["top_r"], lod=True)
    fit_into(Sh, trim(at_r(c, 60)), (730, y0 + 30, 1010, y0 + 346))
    rules = ["SUB-SLICES (reuse real effects)", "EXPLOIT 4   hits YOU for 4", "PATCH 6     heals the BOSS 6",
             "DOSE        corrupts your slice", "",
             "- latches onto either wheel; mostly a boss inflicts it", "  on the PLAYER's wheel",
             "- only in effect when the needle lands on the host", "  slice: the sub-slice in line with the tick fires",
             "  (on top of your own slice)", "- 3 turns (pips), then it drops off; cleansable"]
    for j, ln in enumerate(rules):
        d.text((1040, y0 + 8 + j * 26), ln, font=f_mono(16, False), fill=YEL if j == 0 else (215, 215, 225))
    Sh.convert("RGB").save(os.path.join(OUT, "parasite_needle_options.png"))
    print("options", flush=True)


# ================================================================== trigger gif (layout A)
def trigger():
    P = player()
    fr, du = [], []
    N = 9
    rot0 = ROT_LAND - 12 * N
    h0 = S2.host_image(P, rot=rot0, hp_number=True)
    top = h0[2]["top_r"]

    def make(rot, host, cap, dur, lit=None, beam=0.0, tagtxt=None):
        c = S2.Comp(host, SIZE)
        ri, ro, a0, sp = S3.parasite2(c, 1, "A", rot=rot, top=top, lit=lit)
        if beam > 0:
            S3.link(c, "A", ri, ro, top, k=beam)
        im = c.image(crop=(int(c.C[0] - 860), int(c.C[1] - 900), int(c.C[0] + 860), int(c.C[1] + 640)), scale=0.45)
        base = city(im.width, im.height, 8)
        base.alpha_composite(im)
        d = ImageDraw.Draw(base)
        d.rectangle([0, 0, base.width, 50], fill=(10, 9, 16, 240))
        d.text((14, 8), cap, font=f_num(28), fill=WHITE)
        if tagtxt:
            tag(d, (base.width // 2, 80), tagtxt[0], tagtxt[1], (255, 150, 160), size=26)
        fr.append(base.convert("RGB"))
        du.append(dur)
        print("f", cap[:20], flush=True)
    make(rot0, h0, "1  a PARASITE rides your EXPLOIT 6 slice", 1400)
    steps = 10
    for s in range(1, steps + 1):
        q = s / steps
        q = q * q * (3 - 2 * q)
        rot = rot0 + 12 * N * q
        make(rot, S2.host_image(P, rot=rot, hp_number=True), "2  SEND IT: your wheel spins, the parasite rides along", 90)
    hL = S2.host_image(P, rot=ROT_LAND, hp_number=True)
    make(ROT_LAND, hL, "3  the NEEDLE lands on the host slice", 900)
    for b in (0.4, 0.8, 1.0):
        make(ROT_LAND, hL, "4  the sub-slice in line with the tick fires", 120 if b < 1 else 400, lit=1, beam=b)
    make(ROT_LAND, hL, "4  the sub-slice in line with the tick fires", 2200, lit=1, beam=1.0,
         tagtxt=("YOU: EXPLOIT 6   |   PARASITE: PATCH 6 -> BOSS +6 HP", "the parasite's effect fires as well as your slice"))
    save_gif(fr, du, "parasite_trigger.gif")


if __name__ == "__main__":
    {"sheet": sheet, "replace": replace_gif, "options": options, "trigger": trigger}[sys.argv[1]]()
    print("done")
