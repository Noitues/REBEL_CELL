"""Round 27: city-map crop of the Cell's district -> ../scratch/mapcrops/rc27[_dispatch].png

Round 25 city_hq_v3.py pipeline (the round 6 restyler over the game's own layout, night theme) as a sub-view at
zoom 1.0 (city px = crop px), with the round 27 district:
  - grid27.patch: no fist streets, the regular grid completed through the district, the empty strips built over;
  - the canyon's shophouses replace the city buildings facing grid street j = 36 (cfg27: same rule as hq27.py) and
    come in as the Blender map sprite (hq27.py map view: ortho 2:1 iso, city buildings as holdout);
  - PAINTED ROOFS: every roof whose projected map position is inside the crest carries the Cell's paint
    (cfg27.painted, same test as Blender). Home: crude red with lime / pink graffiti and drips.
    DISPATCH: harsh glowing red, glitch bars torn sideways, black corruption blocks.
python map27.py [home|dispatch]
"""
import json
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

import numpy as np
from PIL import Image, ImageFilter
import lowpoly
from lowpoly import SS
import views as V
import restyle
from restyle import View
import citydata as CD
import grid27
import cfg27
from city_hq_v3 import edges
from toon import paint_texture

CW, CH = 1700, 1300
LIME, PINK = (212, 255, 0), (255, 61, 168)


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
    body = rgb * np.array([0.80, 0.55, 0.60], np.float32)  # the Cell district's deep red-brown
    tex = np.asarray(paint_texture(Image.fromarray((np.clip(body, 0, 1) * 255).astype(np.uint8))), np.float32) / 255
    rgb = tex * (1 - hot) + rgb * hot
    rgb = rgb * (1 - inkm[..., None] * 0.85) + np.array([0.05, 0.04, 0.08]) * inkm[..., None] * 0.85
    alpha = np.maximum(a, inkm * (np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)), np.float32) / 255))
    glow = np.clip((rgb.max(axis=2) - 0.55) / 0.45, 0, 1)[..., None] * rgb * alpha[..., None]
    g = np.asarray(Image.fromarray((glow * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10)), np.float32) / 255
    out = np.concatenate([np.clip(rgb + g * 0.6, 0, 1), alpha[..., None]], axis=2)
    return Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA")


def edit_layout(d, cfg):
    L = CD.Lots(d)
    hq_ctx = {i for i, c in enumerate(d["contexts"]) if c["kind"] == "hq"}
    keep = []
    for p in d["prims"]:
        ci = p.get("ctx", -1)
        if ci in hq_ctx:
            continue
        if p["t"] == "ext" and ci >= 0 and d["contexts"][ci]["kind"] == "bld":
            q = L.pts(p["b"])
            c = (sum(x for x, _ in q) / len(q), sum(y for _, y in q) / len(q))
            if cfg.removed(*c):
                continue
            p["_lot"] = c
        keep.append(p)
    alive = {p["ctx"] for p in keep if p["t"] == "ext"}
    d["prims"] = [p for p in keep if p["t"] == "ext" or p.get("ctx", -1) < 0 or p["ctx"] in alive or d["contexts"][p["ctx"]]["kind"] != "bld"]
    return L


def paint_2d(d, gl, top, seed, disp, k):
    """The Cell's paint on one roof polygon (crop px)."""
    r = random.Random(seed)
    n = len(top)
    tc = (sum(p[0] for p in top) / n, sum(p[1] for p in top) / n)
    rag = [(tc[0] + (x - tc[0]) * r.uniform(0.9, 1.0) + r.uniform(-0.5, 0.5), tc[1] + (y - tc[1]) * r.uniform(0.9, 1.0) + r.uniform(-0.35, 0.35))
           for (x, y) in top]
    xs, ys = [p[0] for p in rag], [p[1] for p in rag]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    S = lambda pts: [(x * SS, y * SS) for (x, y) in pts]
    if not disp:
        col = (int(226 * r.uniform(0.88, 1.06)), int(30 * r.uniform(0.6, 1.2)), 40)
        d.polygon(S(rag), fill=col)
        for _ in range(r.randint(1, 3)):  # graffiti strokes over the red: lime and pink tags
            c = LIME if r.random() < 0.55 else PINK
            a = (r.uniform(min(xs), max(xs)), r.uniform(min(ys), max(ys)))
            b = (a[0] + r.uniform(-0.5, 0.5) * w, a[1] + r.uniform(-0.5, 0.5) * h)
            d.line(S([a, b]), fill=c, width=max(1, int(r.uniform(0.9, 1.7) * k * SS)))
            gl.line(S([a, b]), fill=tuple(int(v * 0.35) for v in c), width=max(1, int(2.0 * k * SS)))
        low = sorted(range(n), key=lambda q: -top[q][1])[:2]  # drips down the front
        for q in low:
            for _ in range(r.randint(1, 3)):
                x = top[q][0] + r.uniform(-4, 4) * k
                y = top[q][1]
                ln = r.uniform(3, 12) * k
                ww = r.uniform(0.6, 1.2) * k
                d.polygon(S([(x - ww, y), (x + ww, y), (x, y + ln)]), fill=col)
    else:
        col = (255, 18, 32)
        d.polygon(S(rag), fill=col)
        gl.polygon(S(rag), fill=(170, 8, 18))
        for _ in range(r.randint(2, 4)):  # glitch: bars torn sideways past the roof edge, black corruption blocks
            y0 = r.uniform(min(ys), max(ys))
            hh = r.uniform(0.6, 2.2) * k
            off = r.uniform(-0.45, 0.45) * w
            x0, x1 = min(xs) + off, max(xs) + off
            c = (10, 6, 10) if r.random() < 0.45 else (255, 120, 120)
            d.rectangle([x0 * SS, y0 * SS, x1 * SS, (y0 + hh) * SS], fill=c)
            if c != (10, 6, 10):
                gl.rectangle([x0 * SS, y0 * SS, x1 * SS, (y0 + hh) * SS], fill=(200, 30, 40))
        for _ in range(r.randint(1, 3)):
            bx, by = r.uniform(min(xs), max(xs)), r.uniform(min(ys), max(ys))
            s = r.uniform(1.2, 3.0) * k
            d.rectangle([bx * SS, by * SS, (bx + s * 1.6) * SS, (by + s) * SS], fill=(10, 6, 10))


def install_paint(cfg, disp, off):
    """Paint = a stencil: each roof gets the part of its top that lies inside the crest (cfg27.pieces_screen)."""
    orig = restyle.Restyler.ext

    def ext(self, d, pr, gl):
        orig(self, d, pr, gl)
        if "_lot" not in pr or pr["ts"] <= 0.3:
            return
        v = self.v
        base = v.pts(pr["b"])
        n = len(base)
        z0, hh, ts = pr["z0"] * v.s, pr["h"] * v.s, pr["ts"]
        c = (sum(p[0] for p in base) / n, sum(p[1] for p in base) / n)
        top = [(c[0] + (p[0] - c[0]) * ts, c[1] + (p[1] - c[1]) * ts - z0 - hh) for p in base]
        if not v.visible(top):
            return
        for k, piece in enumerate(cfg.pieces_screen(top, *off)):
            paint_2d(d, gl, piece, pr["key"] * 31 + int(pr["z0"]) + k, disp, v.k)

    restyle.Restyler.ext = ext


def render(state):
    disp = state == "dispatch"
    d = json.load(open(os.path.join(SRC, "city_layout.json")))
    info = grid27.patch(d)
    cfg = cfg27.Cfg(info["palm"], streets={(s["i"], s["j"]) for s in d["streets"]})
    L = edit_layout(d, cfg)
    X, Y = L.iso(*cfg.P)
    x0, y0 = X - CW / 2, Y - 120 - CH / 2
    install_paint(cfg, disp, (L.ox - x0, L.oy - y0))
    V.set_theme("night")
    view = View(x0, y0, 1.0, CW, CH)
    lowpoly.W, lowpoly.H = CW, CH
    img = V.ViewRestyler(d, view, "night", False).render().convert("RGBA")
    tag = "rc27_canyon%s" % ("_dispatch" if disp else "")
    if os.path.exists(os.path.join(MAP, tag + "_map_beauty.png")):
        sp = sprite(tag)
        sp = sp.resize((int(sp.width / 2), int(sp.height / 2)), Image.LANCZOS)
        cx, cy = X - x0, Y - 450 - y0
        img.alpha_composite(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2)))
    else:
        print("no sprite yet", tag)
    if os.environ.get("CREST_DEBUG"):  # outline the crest (projected rule) for checking
        from PIL import ImageDraw
        dd = ImageDraw.Draw(img)
        for r in cfg.crest_rects(L.ox - x0, L.oy - y0):
            dd.rectangle(list(r), outline=(0, 255, 0), width=2)
    os.makedirs(DST, exist_ok=True)
    img.convert("RGB").save(os.path.join(DST, tag + ".png"))
    print("map crop", tag, flush=True)


if __name__ == "__main__":
    import subprocess
    jobs = sys.argv[1:] or ["home", "dispatch"]
    if len(jobs) == 1:
        render(jobs[0])
    else:
        for job in jobs:
            subprocess.run([sys.executable, os.path.abspath(__file__), job], check=True)
