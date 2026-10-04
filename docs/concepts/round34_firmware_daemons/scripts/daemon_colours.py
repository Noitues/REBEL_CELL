"""daemon_colours.png: round 33 vs round 34 trigger-family phosphors. ACTION moves from pink to violet-lavender and MISS
darkens to a true red, so the pair separates in colour, in greyscale and under protan / deutan / tritan simulation
(Machado 2009, severity 1.0, applied in linear RGB). Delta E = CIE76 in Lab.

python daemon_colours.py
"""
import itertools
import numpy as np
from PIL import Image, ImageDraw

import fwlib as F
L = F.L

OLD = {"PERFECT": (255, 214, 64), "MISS": (255, 84, 96), "TURN": (92, 225, 255), "ACTION": (255, 92, 190),
       "RUN": (150, 255, 110), "HEAT": (255, 140, 60)}
NEW = dict(F.FAM)
SIMS = {
    "normal": np.eye(3),
    "protan": np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]),
    "deutan": np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
    "tritan": np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]),
}


def lin(c):
    c = np.asarray(c, np.float64) / 255
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255


def sim_rgb(rgb, m):
    return tuple(int(v) for v in np.round(srgb(m @ lin(rgb))))


def sim_img(img, m):
    a = np.asarray(img.convert("RGBA"), np.float64)
    rgb = lin(a[..., :3])
    out = srgb(np.einsum("ij,hwj->hwi", m, rgb))
    a[..., :3] = out
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


def lab(rgb):
    c = lin(rgb)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    x, y, z = (M @ c) / np.array([0.95047, 1.0, 1.08883])
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return np.array([116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))])


def dE(a, b):
    return float(np.linalg.norm(lab(a) - lab(b)))


def luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def main():
    img = F.bg(seed=21)
    d = F.header(img, "DAEMON PHOSPHORS  -  MISS vs ACTION separated",
                 "Round 33 MISS red and ACTION pink were neighbours. Round 34: ACTION = violet-lavender (lighter), MISS = deeper red (darker). Checked in colour, greyscale and three colour-blind simulations.")
    sims = list(SIMS.items()) + [("grey", None)]
    # ---- 1: the pair, old vs new, as tiles (Fault Tolerance = MISS, Tuning Fork = ACTION)
    F.section(d, 32, 118, "THE PAIR  (Fault Tolerance = MISS, Tuning Fork = ACTION)", L.CYAN)
    for row, (lab_, pal) in enumerate((("ROUND 33", OLD), ("ROUND 34", NEW))):
        y = 196 + row * 180
        d = ImageDraw.Draw(img)
        d.text((40, y + 50), lab_, font=L.f_num(30), fill=(240, 240, 248, 255))
        F.FAM.update(pal)
        tiles = [F.daemon_tile("fault_tolerance", 96, t=0.3), F.daemon_tile("tuning_fork", 96, t=0.3)]
        for k, (sn, m) in enumerate(sims):
            x = 210 + k * 236
            for j, t in enumerate(tiles):
                tt = F.grey(t) if m is None else sim_img(t, m)
                img.alpha_composite(tt, (x + j * 104, y))
            d = ImageDraw.Draw(img)
            if row == 0:
                d.text((x + 100, 178), sn.upper(), font=L.f_mono(16), fill=(200, 200, 215, 255), anchor="mm")
            a, b = pal["MISS"], pal["ACTION"]
            if m is None:
                txt = "luma %d vs %d" % (luma(a), luma(b))
                ok = abs(luma(a) - luma(b)) > 40
            else:
                e = dE(sim_rgb(a, m), sim_rgb(b, m))
                txt = "dE %.0f" % e
                ok = e > 40
            d.text((x + 100, y + 116), txt, font=L.f_mono(16), fill=((150, 255, 120) if ok else (255, 110, 110)) + (255,), anchor="mm")
    F.FAM.update(NEW)
    # ---- 2: the full palette under each sim, with the closest pair
    d = ImageDraw.Draw(img)
    F.section(d, 32, 560, "ALL SIX FAMILIES (round 34)  -  closest pair per view", L.CYAN)
    fams = list(NEW.keys())
    for k, (sn, m) in enumerate(sims):
        x = 40 + k * 372
        y = 610
        d.text((x, y), sn.upper(), font=L.f_num(24), fill=(230, 230, 240, 255))
        cols = {}
        for j, f in enumerate(fams):
            c = NEW[f]
            if m is None:
                g = int(luma(c))
                sc = (g, g, g)
            else:
                sc = sim_rgb(c, m)
            cols[f] = sc
            yy = y + 40 + j * 46
            d.rounded_rectangle([x, yy, x + 60, yy + 36], radius=6, fill=sc + (255,))
            mk = Image.new("RGBA", (36, 36), sc + (0,))
            mk.putalpha(F.icon({"PERFECT": "kernel_sync", "MISS": "fault_tolerance", "TURN": "warm_boot", "ACTION": "tuning_fork", "RUN": "salvager", "HEAT": "cold_exit"}[f], 36))
            tile_bg = Image.new("RGBA", (44, 40), (10, 10, 16, 255))
            tile_bg.alpha_composite(mk, (4, 2))
            img.alpha_composite(tile_bg, (x + 68, yy - 2))
            d = ImageDraw.Draw(img)
            d.text((x + 122, yy + 18), f, font=L.f_mono(15), fill=(210, 210, 222, 255), anchor="lm")
        if m is None:
            pairs = sorted((abs(luma(NEW[a]) - luma(NEW[b])), a, b) for a, b in itertools.combinations(fams, 2))
            v, a, b = pairs[0]
            txt = "closest luma: %s / %s  %d" % (a, b, v)
        else:
            pairs = sorted((dE(cols[a], cols[b]), a, b) for a, b in itertools.combinations(fams, 2))
            v, a, b = pairs[0]
            txt = "closest: %s / %s  dE %.0f" % (a, b, v)
        d.text((x, y + 330), txt, font=L.f_mono(13), fill=(255, 214, 120, 255))
        e = dE(cols["MISS"], cols["ACTION"]) if m is not None else abs(luma(NEW["MISS"]) - luma(NEW["ACTION"]))
        d.text((x, y + 350), "MISS / ACTION: %s %.0f" % ("luma" if m is None else "dE", e), font=L.f_mono(13), fill=(150, 255, 120, 255))
    notes = ["Colour is the second cue: every Daemon has its own sigil, and the tooltip names the family.",
             "Other pairs that stay close under CVD (PERFECT / RUN, RUN / HEAT) never share a sigil and never fire on the same hook; the family word is in every tooltip."]
    for k, s in enumerate(notes):
        d.text((40, 1012 + k * 22), s, font=L.f_mono(15), fill=(190, 200, 215, 255))
    L.save(img, "daemon_colours.png")


if __name__ == "__main__":
    main()
