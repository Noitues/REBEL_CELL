"""Round 26: city-map crops of the Cell's district for each base idea -> ../scratch/mapcrops/<idea>[_dispatch].png

Same pipeline as round 25 city_hq_v3.py (the round 6 restyler over the game's own layout, night theme), rendered as a
sub-view round the fist at zoom 1.0 (city px = crop px). Per idea, using the SAME rules as the Blender scene
(idea_cfg.py): the city buildings that make way for the hero are taken out; for PAINTED ROOFS the roofs that carry
paint are painted here too (ragged red fill + drips); then the hero's Blender map sprite (hq26.py map view: ortho,
the game's 2:1 iso, city buildings as holdout) is inked and pasted at its lot.
python map26.py [idea[:dispatch] ...]
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "city_r6"))
sys.path.insert(0, HERE)
OUT = os.path.dirname(HERE)
SRC = os.path.join(OUT, "..", "round6_city_restyle")
MAP = os.path.join(OUT, "scratch", "map")
DST = os.path.join(OUT, "scratch", "mapcrops")

from PIL import Image, ImageDraw, ImageFont
import lowpoly
from lowpoly import SS
import views as V
import restyle
from restyle import View
import citydata as CD
import idea_cfg as IC
from city_hq_v3 import edges
import numpy as np
from PIL import ImageFilter
from toon import paint_texture


def sprite(tag):
    """round 25 sprite() (beauty + the map's ink from part id / normal / silhouette, soft glow), toned for the
    round 6 map: the lit body darker and painterly (the restyler's paint texture), the neon kept hot."""
    b = np.asarray(Image.open(os.path.join(MAP, tag + "_map_beauty.png")).convert("RGBA"), np.float32) / 255
    n = np.asarray(Image.open(os.path.join(MAP, tag + "_map_normal.png")).convert("RGB"), np.float32) / 255
    i = np.asarray(Image.open(os.path.join(MAP, tag + "_map_id.png")).convert("RGB"), np.float32) / 255
    a = b[..., 3]
    ink = (edges(i, 0.04) | edges(n, 0.45)) & (a > 0.5)
    ink = ink | edges(a[..., None], 0.5)
    inkm = np.asarray(Image.fromarray((ink * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) / 255
    rgb = b[..., :3]
    lum = rgb.max(axis=2)
    hot = np.clip((lum - 0.6) / 0.3, 0, 1)[..., None]
    body = rgb * np.array([0.80, 0.70, 0.80], np.float32)  # the Cell district's darker, redder grade
    tex = np.asarray(paint_texture(Image.fromarray((np.clip(body, 0, 1) * 255).astype(np.uint8))), np.float32) / 255
    rgb = tex * (1 - hot) + rgb * hot
    rgb = rgb * (1 - inkm[..., None] * 0.85) + np.array([0.05, 0.04, 0.08]) * inkm[..., None] * 0.85
    alpha = np.maximum(a, inkm * (np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)), np.float32) / 255))
    glow = np.clip((rgb.max(axis=2) - 0.55) / 0.45, 0, 1)[..., None] * rgb * alpha[..., None]
    g = np.asarray(Image.fromarray((glow * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10)), np.float32) / 255
    out = np.concatenate([np.clip(rgb + g * 0.6, 0, 1), alpha[..., None]], axis=2)
    return Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA")

CW, CH = 1700, 1300  # crop, city px (zoom 1.0)


def edit_layout(d, cfg, idea):
    L = CD.Lots(d)
    fist = CD.fist_lots(d, L)
    keep = []
    hq_ctx = {i for i, c in enumerate(d["contexts"]) if c["kind"] == "hq"}
    for p in d["prims"]:
        ci = p.get("ctx", -1)
        if ci in hq_ctx:
            continue  # the old HQ drawings (round 25 v3 rule); the base is the Blender sprite
        if p["t"] == "ext" and ci >= 0 and d["contexts"][ci]["kind"] == "bld":
            q = L.pts(p["b"])
            c = (sum(x for x, _ in q) / len(q), sum(y for _, y in q) / len(q))
            if cfg.removed(idea, *c) or CD.near_fist(c, fist, 0.9):
                continue
            p["_lot"] = c
        keep.append(p)
    alive = {p["ctx"] for p in keep if p["t"] == "ext"}
    d["prims"] = [p for p in keep if p["t"] == "ext" or p.get("ctx", -1) < 0 or p["ctx"] in alive or d["contexts"][p["ctx"]]["kind"] != "bld"]
    return L


def install_paint(cfg, idea, disp):
    """Wrap Restyler.ext: after a building is drawn, paint its roof if the idea says so (same test as hq26.py)."""
    orig = restyle.Restyler.ext

    def ext(self, d, pr, gl):
        orig(self, d, pr, gl)
        if "_lot" not in pr or pr["ts"] <= 0.3 or not cfg.painted(idea, pr["_lot"][0], pr["_lot"][1], pr["z0"] + pr["h"]):
            return
        v = self.v
        base = v.pts(pr["b"])
        n = len(base)
        z0, hh, ts = pr["z0"] * v.s, pr["h"] * v.s, pr["ts"]
        c = (sum(p[0] for p in base) / n, sum(p[1] for p in base) / n)
        top = [(c[0] + (p[0] - c[0]) * ts, c[1] + (p[1] - c[1]) * ts - z0 - hh) for p in base]
        if not v.visible(top):
            return
        r = random.Random(pr["key"] * 31 + int(pr["z0"]))
        tc = (sum(p[0] for p in top) / n, sum(p[1] for p in top) / n)
        rag = [(tc[0] + (x - tc[0]) * r.uniform(0.8, 0.97) + r.uniform(-0.6, 0.6), tc[1] + (y - tc[1]) * r.uniform(0.8, 0.97) + r.uniform(-0.4, 0.4))
               for (x, y) in top]
        col = (230, 22, 34) if disp else (int(196 * r.uniform(0.85, 1.08)), 24, 32)
        d.polygon([(x * SS, y * SS) for (x, y) in rag], fill=col)
        if disp:
            gl.polygon([(x * SS, y * SS) for (x, y) in rag], fill=(150, 10, 18))
        # roller stripe
        a, b = rag[0], rag[1 % n]
        cc, dd = rag[-1], rag[-2 % n]
        t = r.uniform(0.2, 0.6)
        p0 = (a[0] + (cc[0] - a[0]) * t, a[1] + (cc[1] - a[1]) * t)
        p1 = (b[0] + (dd[0] - b[0]) * t, b[1] + (dd[1] - b[1]) * t)
        d.line([(p0[0] * SS, p0[1] * SS), (p1[0] * SS, p1[1] * SS)], fill=tuple(min(255, int(x * 1.18)) for x in col), width=max(1, int(1.6 * v.k * SS)))
        # drips down the front (the lowest roof corners on screen)
        low = sorted(range(n), key=lambda k: -top[k][1])[:2]
        for k in low:
            for _ in range(r.randint(1, 3)):
                x = top[k][0] + r.uniform(-4, 4) * v.k
                y = top[k][1]
                ln = r.uniform(3, min(16, max(4, hh * 0.5))) * v.k
                w = r.uniform(0.6, 1.3) * v.k
                d.polygon([((x - w) * SS, y * SS), ((x + w) * SS, y * SS), (x * SS, (y + ln) * SS)], fill=col)
        if disp and r.random() < 0.55:  # tar slash across the paint
            d.line([(rag[0][0] * SS, rag[0][1] * SS), (rag[n // 2][0] * SS, rag[n // 2][1] * SS)], fill=(10, 8, 12), width=max(1, int(2.2 * v.k * SS)))

    restyle.Restyler.ext = ext


def render(job):
    idea, _, state = job.partition(":")
    disp = state == "dispatch"
    d = json.load(open(os.path.join(SRC, "city_layout.json")))
    lay = json.load(open(os.path.join(OUT, "scratch", "layout", "rc26.json")))
    cfg = IC.Cfg(lay)
    L = edit_layout(d, cfg, idea)
    install_paint(cfg, idea, disp)
    X, Y = L.iso(*cfg.P)
    x0, y0 = X - CW / 2, Y - 170 - CH / 2
    V.set_theme("night")
    view = View(x0, y0, 1.0, CW, CH)
    lowpoly.W, lowpoly.H = CW, CH
    img = V.ViewRestyler(d, view, "night", False).render().convert("RGBA")
    tag = "rc26_%s%s" % (idea, "_dispatch" if disp else "")
    sp_path = os.path.join(MAP, tag + "_map_beauty.png")
    if os.path.exists(sp_path):
        sp = sprite(tag)
        sp = sp.resize((int(sp.width / 2), int(sp.height / 2)), Image.LANCZOS)
        cx, cy = X - x0, Y - 450 - y0
        img.alpha_composite(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2)))
    else:
        print("no sprite for", tag)
    img = img.convert("RGB")
    os.makedirs(DST, exist_ok=True)
    img.save(os.path.join(DST, tag + ".png"))
    print("map crop", tag, flush=True)


if __name__ == "__main__":
    import subprocess
    jobs = sys.argv[1:] or IC.IDEAS
    if len(jobs) == 1:
        render(jobs[0])
    else:  # one process per job (the paint hook patches the restyler class)
        for job in jobs:
            subprocess.run([sys.executable, os.path.abspath(__file__), job], check=True)
