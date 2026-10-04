"""Round 35 -> three cleaner city > link transitions (GIFs) + building_language.png.

  transition_1_zoom.gif    ONE CAMERA. The iso city zooms straight down onto the link (same buildings, same camera, no
                           cut). At city scale the link is one orange trace; as the camera arrives it splits into the
                           run's nodes and branches.
  transition_2_unfold.gif  THE LINK UNFOLDS. On the city map everything but the chosen link dims; the link straightens
                           and widens into a strip, and the strip IS the transit view (a wipe along the link direction).
  transition_3_bits.gif    JACK IN. The map dissolves into bits (the locked card dissolve A) except the link; the transit
                           view assembles from bits along the link, start node first.

  building_language.png    The same iso kit at three zooms: city (1300), raid (640), netrun transit (355).

python transitions.py [1|2|3|lang|all]
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import r31lib as L
import r32ui as U
import r35ui as R
import sticker_lib19 as SL
import city_view as CV
import transit_view as TV

SIZE = (800, 450)


def transit_final():
    A = TV.load()
    bg = Image.open(os.path.join(U.FIN, "iso_transit.png"))
    return TV.compose(bg, A, ["start"], "start", ui=1.0), TV.compose(bg, A, ["start"], "start", ui=0.0), A


def t1():
    anims = json.load(open(os.path.join(U.BL, "iso_anim_anchors.json")))
    TV.load()
    frames, durs = [], []
    n = len(anims)
    for f in range(n):
        A = anims[f]
        bg = Image.open(os.path.join(U.FIN, "iso_f%02d.png" % f)).convert("RGBA").resize((1920, 1080), Image.LANCZOS)
        bg = ImageEnhance.Brightness(bg).enhance(0.82)
        t = f / (n - 1)
        if t < 0.55:
            a, b = A["nodes"]["start"]["c"], A["nodes"]["final"]["c"]
            inl = U.Inlay()
            inl.trace([a, b], R.MER, width=3.0, lanes=3, gap=4, glow=1.0, pads=False)
            img = inl.lay(bg)
            for p, col in ((a, R.LIME), (b, R.MER)):
                img = U.pad(img, CV.diamond(p[0], p[1], 22), col, lit=1.0, glow=0.9, k=0.9)
            if f == 0:
                img = R.heat_strip(img, (700, 22), 41, "NOTICED", w=520)
                img = L.place_sticker(img, L.sticker_word(["JACK IN"], 78, fills=["pink"], seed=8), 1690, 900, angle=-3)
        else:
            k = (t - 0.55) / 0.45
            full = TV.compose(bg, A, ["start"], "start", ui=0.0)
            img = Image.blend(bg, full, min(1.0, 0.35 + k)).convert("RGBA")
        frames.append(img.convert("RGB"))
        durs.append(900 if f == 0 else 120)
    fin, _, _ = transit_final()
    frames.append(fin.convert("RGB"))
    durs.append(1800)
    out = os.path.join(L.OUT, "transition_1_zoom.gif")
    print("wrote", out, U.save_gif(frames, durs, out, size=(720, 405)))


def city_with_link():
    img, sel = CV.render(selected=True)
    nodes, links = CV.NET
    # the chosen link: from the owned neighbour to the selected Site
    nb = [a if b == sel else b for (a, b) in links if sel in (a, b) and nodes[a if b == sel else b]["state"] == "owned"]
    return img, nodes[nb[0]]["xy"], nodes[sel]["xy"]


def t2():
    city, a, b = city_with_link()
    fin, fin_bg, A = transit_final()
    frames, durs = [], []
    frames.append(CV.hud(city.copy(), CV.pick_selected()).convert("RGB"))
    durs.append(1000)
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    # 1) everything but the link dims
    for k in (0.5, 1.0):
        m = Image.new("L", city.size, 0)
        ImageDraw.Draw(m).line([a, b], fill=255, width=int(60 * k))
        m = m.filter(ImageFilter.GaussianBlur(20))
        dim = ImageEnhance.Brightness(ImageEnhance.Color(city).enhance(1 - 0.7 * k)).enhance(1 - 0.6 * k)
        img = Image.composite(city, dim, m)
        frames.append(img.convert("RGB"))
        durs.append(130)
    # 2) zoom/rotate so the link lies along the transit view's diagonal (the views share the iso axes: no rotation needed)
    sA, sB = A["nodes"]["start"]["c"], A["nodes"]["final"]["c"]
    L0 = math.hypot(b[0] - a[0], b[1] - a[1])
    L1 = math.hypot(sB[0] - sA[0], sB[1] - sA[1])
    zf = L1 / L0
    for i, t in enumerate((0.33, 0.66, 1.0)):
        z = 1 + (zf - 1) * t
        cx = mid[0] + ((sA[0] + sB[0]) / 2 - mid[0]) * 0
        w, h = 1920 / z, 1080 / z
        tgt = (mid[0] - ((sA[0] + sB[0]) / 2 - 960) / z, mid[1] - ((sA[1] + sB[1]) / 2 - 540) / z)
        box = (tgt[0] - w / 2, tgt[1] - h / 2, tgt[0] + w / 2, tgt[1] + h / 2)
        base = ImageEnhance.Brightness(ImageEnhance.Color(city).enhance(0.3)).enhance(0.4)
        fr = base.crop(tuple(int(v) for v in box)).resize((1920, 1080), Image.LANCZOS)
        # the strip (the transit view) opens along the link
        strip = Image.new("L", (1920, 1080), 0)
        half = 40 + 320 * t
        d = ImageDraw.Draw(strip)
        ux, uy = (sB[0] - sA[0]) / L1, (sB[1] - sA[1]) / L1
        nx, ny = -uy, ux
        p0 = (sA[0] - ux * 300, sA[1] - uy * 300)
        p1 = (sB[0] + ux * 300, sB[1] + uy * 300)
        d.polygon([(p0[0] + nx * half, p0[1] + ny * half), (p1[0] + nx * half, p1[1] + ny * half),
                   (p1[0] - nx * half, p1[1] - ny * half), (p0[0] - nx * half, p0[1] - ny * half)], fill=255)
        strip = strip.filter(ImageFilter.GaussianBlur(6))
        img = Image.composite(fin_bg.convert("RGBA"), fr, strip)
        e = ImageFilter.FIND_EDGES
        edge = strip.filter(e).point(lambda v: 255 if v > 8 else 0).filter(ImageFilter.MaxFilter(3))
        img = SL.over(img, R.MER, edge)
        frames.append(img.convert("RGB"))
        durs.append(130)
    frames.append(Image.blend(fin_bg.convert("RGB"), fin.convert("RGB"), 0.5))
    durs.append(120)
    frames.append(fin.convert("RGB"))
    durs.append(1800)
    out = os.path.join(L.OUT, "transition_2_unfold.gif")
    print("wrote", out, U.save_gif(frames, durs, out, size=SIZE))


def bitmask(size, t, seed, origin, cell=16):
    """1 where bits have arrived: cells light up by distance from origin plus jitter."""
    W, H = size
    gw, gh = W // cell + 1, H // cell + 1
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:gh, 0:gw].astype(np.float32)
    d = np.hypot(xx * cell - origin[0], (yy * cell - origin[1]) * 1.6) / 2000.0
    thr = d + rng.random((gh, gw)) * 0.35
    m = (thr < t * 1.35).astype(np.uint8) * 255
    return Image.fromarray(m).resize((gw * cell, gh * cell), Image.NEAREST).crop((0, 0, W, H))


def bits_overlay(img, mask, col, seed):
    rng = random.Random(seed)
    d = ImageDraw.Draw(img)
    f = L.f_mono(16)
    edge = np.asarray(mask.filter(ImageFilter.FIND_EDGES))
    ys, xs = np.nonzero(edge[::16, ::16])
    for y, x in list(zip(ys, xs))[:: max(1, len(ys) // 260)]:
        d.text((x * 16 + 2, y * 16), rng.choice("01"), font=f, fill=col + (230,))
    return img


def t3():
    city, a, b = city_with_link()
    cityh = CV.hud(city.copy(), CV.pick_selected())
    fin, fin_bg, A = transit_final()
    frames, durs = [cityh.convert("RGB")], [1000]
    black = Image.new("RGBA", (1920, 1080), (6, 5, 10, 255))
    linkm = Image.new("L", (1920, 1080), 0)
    ImageDraw.Draw(linkm).line([a, b], fill=255, width=26)
    for i, t in enumerate((0.3, 0.6, 1.0)):
        gone = bitmask((1920, 1080), t, 5, (1920 - a[0], 1080 - a[1]))
        gone = Image.fromarray(np.minimum(np.asarray(gone), 255 - np.asarray(linkm)))
        img = Image.composite(black, cityh, gone)
        img = bits_overlay(img, gone, R.LIME, 10 + i)
        frames.append(img.convert("RGB"))
        durs.append(130)
    sA = A["nodes"]["start"]["c"]
    for i, t in enumerate((0.3, 0.55, 0.8, 1.0)):
        came = bitmask((1920, 1080), t, 9, sA)
        img = Image.composite(fin_bg.convert("RGBA") if t < 1 else fin, black, came)
        img = bits_overlay(img, came, R.MER, 20 + i)
        frames.append(img.convert("RGB"))
        durs.append(130)
    frames.append(fin.convert("RGB"))
    durs.append(1800)
    out = os.path.join(L.OUT, "transition_3_bits.gif")
    print("wrote", out, U.save_gif(frames, durs, out, size=SIZE))


def lang():
    W, H = 1920, 1080
    img = Image.new("RGBA", (W, H), (9, 8, 14, 255))
    img = L.place_sticker(img, L.sticker_word(["ONE CITY KIT"], 54, fills=["yellow"], seed=41), 210, 56, angle=-2)
    d = ImageDraw.Draw(img)
    d.text((440, 50), "same iso camera (35 deg, ortho), same lot grid, one building per lot: only the zoom changes",
           font=L.f_ui(24, b"SemiBold"), fill=(235, 235, 240, 255), anchor="lm")
    tw, th = 616, 347
    rows = [("iso_city.png", "CITY GRID", "ortho 1300: Sites + links over the city; districts read as texture"),
            ("iso_raid.png", "RAID", "ortho 640: nodes in buildings (uplink pads), lime Cell links, threats"),
            ("iso_transit.png", "NETRUN TRANSIT", "ortho 355: the run's nodes sit on the same lanes and lots")]
    for i, (fn, title, sub) in enumerate(rows):
        x = 22 + i * (tw + 22)
        im = Image.open(os.path.join(U.FIN, fn)).convert("RGBA").resize((tw, th), Image.LANCZOS)
        if i == 1:
            A = json.load(open(os.path.join(U.BL, "iso_raid_anchors.json")))
            k = tw / 1920
            inl = U.Inlay((tw, th), 0.6)
            sel = ["start", "1_2", "2_1", "3_1", "4_2", "5_2", "6_2"]
            pts = [(A["nodes"][s]["c"][0] * k, A["nodes"][s]["c"][1] * k) for s in sel]
            inl.trace(pts, R.LIME, width=2.5, lanes=2, gap=3, glow=0.8, pads=False)
            im = inl.lay(im)
            for p in pts:
                im = U.pad(im, CV.diamond(p[0], p[1], 12), R.LIME, lit=1.0, glow=0.6, k=0.6, pins=False)
        if i == 2:
            A = TV.load()
            full = TV.compose(Image.open(os.path.join(U.FIN, fn)), A, TV.WALKED, "2_1", ui=0.0)
            im = full.resize((tw, th), Image.LANCZOS)
        img.alpha_composite(im, (x, 130))
        d = ImageDraw.Draw(img)
        d.rectangle([x, 130, x + tw, 130 + th], outline=U.CYAN + (255,), width=2)
        d.text((x, 500), title, font=L.f_ui(28, b"Bold"), fill=U.CYAN + (255,))
        d.text((x, 540), sub, font=L.f_mono(16), fill=(200, 210, 220, 255))
    # a close-up crop at the same pixel scale, to show the buildings are the same objects
    for i, (fn, box) in enumerate((("iso_city.png", (880, 470, 1040, 560)), ("iso_raid.png", (800, 420, 1120, 600)),
                                   ("iso_transit.png", (560, 330, 1200, 690)))):
        x = 22 + i * (tw + 22)
        im = Image.open(os.path.join(U.FIN, fn)).convert("RGBA").crop(box).resize((tw, 347), Image.LANCZOS)
        img.alpha_composite(im, (x, 600))
        d = ImageDraw.Draw(img)
        d.rectangle([x, 600, x + tw, 947], outline=(120, 130, 150, 255), width=1)
        d.text((x, 960), "the same block, enlarged", font=L.f_mono(15), fill=(160, 170, 180, 255))
    c = L.CRT(1876, 70, U.CYAN, None, header=False, seed=42)
    c.text((16, 12), "RULE: buildings are individual per lot everywhere (no merged city blocks). Height, roof trim and window grid come", 17, (220, 235, 240))
    c.text((16, 38), "from one seeded lot table, so a building seen in a netrun is the same one the raid defends and the city map shows.", 17, (220, 235, 240))
    img = L.paste(img, c.finish(scan=0.15), 22, 996)
    L.save(img, "building_language.png")


if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv) > 1 else "all"
    for k, fn in (("1", t1), ("2", t2), ("3", t3), ("lang", lang)):
        if w in (k, "all"):
            fn()
