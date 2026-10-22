"""Silhouette soft-IoU (the ART_BIBLE 5.2 16 px rule, at 16 px, 42 px) of each new icon against the five shipped kinds and the
other two new kinds; and Machado 2009 colour-vision ΔE76 of the kind accent colours. Prints markdown."""
import sys
import json
import numpy as np
sys.path.insert(0, "D:/rc_scratch/solace_v1/nodes/scripts")
from common import *
import icons


def alpha_at(img, px):
    """alpha of a 130-canvas sticker scaled to `px` wide, centred on a (px+4)^2 canvas; a 0..1 array."""
    s = img.resize((px, int(round(px * img.height / img.width))), Image.LANCZOS).split()[3]
    c = Image.new("L", (px + 4, px + 4), 0)
    c.paste(s, ((px + 4 - s.width) // 2, (px + 4 - s.height) // 2))
    return np.asarray(c, dtype=np.float32) / 255.0


def iou(a, b):
    return float(np.minimum(a, b).sum() / max(1e-6, np.maximum(a, b).sum()))


def run():
    out = {}
    ex = {k: shipped(k) for k in ("fight", "elite", "event", "shop", "rack")}
    for px in (16, 42):
        out[px] = {}
        exa = {k: alpha_at(v, px) for k, v in ex.items()}
        for dr in "ABC":
            na = {k: alpha_at(icons.make(dr, k).render(1.0, ss=4), px) for k in icons.KINDS}
            for k, a in na.items():
                worst_ex = max(((iou(a, b), n) for n, b in exa.items()), key=lambda t: t[0])
                others = [(iou(a, b), n) for n, b in na.items() if n != k]
                worst_new = max(others, key=lambda t: t[0])
                out[px][(dr, k)] = (worst_ex, worst_new)
    return out


MACH = {
    "protan": np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]),
    "deutan": np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
    "tritan": np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]),
}


def lin(c):
    c = np.asarray(c, dtype=np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def delin(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255


def lab(rgb):
    c = lin(rgb)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = M @ c / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def sim(rgb, kind):
    if kind == "normal":
        return np.asarray(rgb, dtype=np.float64)
    return delin(MACH[kind] @ lin(rgb))


def de(a, b, kind):
    return float(np.linalg.norm(lab(sim(a, kind)) - lab(sim(b, kind))))


# the sticker's identity colour as the eye reads it: the accent ring colour of each kind
ACC = {"fight": (108, 247, 255), "elite": (255, 140, 26), "event": (78, 255, 158), "shop": (98, 169, 255), "rack": (255, 160, 42),
       "rest": icons.KIND["rest"]["acc"], "workshop": icons.KIND["workshop"]["acc"], "cache": icons.KIND["cache"]["acc"]}

if __name__ == "__main__":
    r = run()
    for px in (16, 42):
        print("\nSilhouette soft IoU at %d px (max against a shipped kind / max against another new kind)" % px)
        print("| dir | REST | WORKSHOP | CACHE |")
        print("|---|---|---|---|")
        for dr in "ABC":
            cells = []
            for k in icons.KINDS:
                (a, an), (b, bn) = r[px][(dr, k)]
                cells.append("%.2f (%s) / %.2f (%s)" % (a, an, b, bn))
            print("| %s | %s |" % (dr, " | ".join(cells)))
    print("\nΔE76 under Machado 2009 (severity 1) of each new accent against the nearest shipped accent")
    print("| kind | normal | protan | deutan | tritan |")
    print("|---|---|---|---|---|")
    for k in icons.KINDS:
        cells = []
        for v in ("normal", "protan", "deutan", "tritan"):
            best = min(((de(ACC[k], ACC[o], v), o) for o in ("fight", "elite", "event", "shop", "rack")), key=lambda t: t[0])
            cells.append("%.0f (%s)" % best)
        print("| %s | %s |" % (k, " | ".join(cells)))
    print("\nnew against new")
    for a, b in (("rest", "workshop"), ("rest", "cache"), ("workshop", "cache")):
        print(a, b, ", ".join("%s %.0f" % (v, de(ACC[a], ACC[b], v)) for v in ("normal", "protan", "deutan", "tritan")))
