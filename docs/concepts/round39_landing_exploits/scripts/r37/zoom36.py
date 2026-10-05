"""Round 36 -> five mixed-media city > link transitions (GIFs <= 3 MB) + zoom_compare.png.

  zoom_a_wheel.gif     THE WHEEL AS A LENS: a spinner slaps onto the chosen link, spins, and its hub opens onto the
                       transit view; the ring flies past the camera.
  zoom_b_peel.gif      STICKER PEEL: the city map is a sticker; it peels back from the corner and the transit view is
                       printed underneath.
  zoom_c_pencil.gif    GREASE-PENCIL DIVE: the pencil rings the chosen Site (the selection mark), the ring becomes a
                       lens and the camera dives through it.
  zoom_d_crt.gif       CRT CHANNEL CHANGE: the map collapses to a scanline and a dot, then the link's channel opens.
  zoom_e_terminal.gif  TERMINAL CONNECT: the Cell's terminal types the connection, binary rain falls along the link and
                       washes the map away; the rain thins onto the transit view.

python zoom36.py [a|b|c|d|e|cmp|all]
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

import r31lib as L
import r32ui as U
import r35ui as R
import sticker_lib19 as SL
import city_view as CV
import states36 as S6

W, H = 1920, 1080
GSIZE = (800, 450)
_cache = {}


def sources():
    if not _cache:
        city = S6.city_png("a", label=False).convert("RGB")
        tr = S6.transit_png("a", label=False).convert("RGB")
        nodes, links = CV.NET
        sel = CV.pick_selected()
        nb = [a if b == sel else b for (a, b) in links if sel in (a, b) and nodes[a if b == sel else b]["state"] == "owned"][0]
        _cache.update(city=city, tr=tr, a=nodes[nb]["xy"], b=nodes[sel]["xy"])
    return _cache


def save(name, frames, durs):
    out = os.path.join(L.OUT, name)
    size = U.save_gif(frames, durs, out, size=GSIZE)
    if size > 3_000_000:
        size = U.save_gif(frames, durs, out, size=(720, 405))
    print("wrote", out, size)


def zoom_crop(img, c, z):
    w, h = W / z, H / z
    cx = min(max(c[0], w / 2), W - w / 2)
    cy = min(max(c[1], h / 2), H - h / 2)
    return img.crop((int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))).resize((W, H), Image.LANCZOS)


# ------------------------------------------------------------------ A: the wheel as a lens
SLICES = [((255, 196, 40), "CRIT"), ((255, 61, 168), "ATK"), ((255, 61, 168), "ATK"), ((255, 61, 168), "ATK"), ((92, 225, 255), "DEF"),
          ((120, 116, 130), "MISS")]


def wheel(R_out, R_in, rot):
    S = 2
    P = int(R_out * 2 + 40) * S
    im = Image.new("RGBA", (P, P), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = P / 2
    ro, ri = R_out * S, R_in * S
    d.ellipse([c - ro - 10 * S, c - ro - 10 * S, c + ro + 10 * S, c + ro + 10 * S], fill=(246, 243, 236, 255))
    d.ellipse([c - ro - 4 * S, c - ro - 4 * S, c + ro + 4 * S, c + ro + 4 * S], fill=(20, 17, 24, 255))
    for i, (col, lab) in enumerate(SLICES):
        a0 = rot + i * 60 - 90
        d.pieslice([c - ro, c - ro, c + ro, c + ro], a0, a0 + 60, fill=col + (255,), outline=(20, 17, 24, 255), width=4 * S)
        am = math.radians(a0 + 30)
        rr = (ro + ri) / 2
        f = L.f_num(int((ro - ri) * 0.32))
        d.text((c + rr * math.cos(am), c + rr * math.sin(am)), lab, font=f, fill=(20, 17, 24, 255), anchor="mm")
    d.ellipse([c - ri - 6 * S, c - ri - 6 * S, c + ri + 6 * S, c + ri + 6 * S], fill=(20, 17, 24, 255))
    hole = Image.new("L", (P, P), 0)
    ImageDraw.Draw(hole).ellipse([c - ri, c - ri, c + ri, c + ri], fill=255)
    a = ImageChops.subtract(im.split()[3], hole)
    im.putalpha(a)
    # pointer
    d = ImageDraw.Draw(im)
    d.polygon([(c, c - ro - 30 * S), (c - 16 * S, c - ro - 58 * S), (c + 16 * S, c - ro - 58 * S)], fill=(246, 243, 236, 255),
              outline=(20, 17, 24, 255), width=3 * S)
    return im.resize((P // S, P // S), Image.LANCZOS)


def lens_frame(city, tr, c, R_out, R_in, rot, inner_zoom):
    base = city.convert("RGBA")
    hole = Image.new("L", (W, H), 0)
    ImageDraw.Draw(hole).ellipse([c[0] - R_in, c[1] - R_in, c[0] + R_in, c[1] + R_in], fill=255)
    inner = tr.convert("RGBA")
    base = Image.composite(inner, base, hole)
    wl = wheel(R_out, R_in, rot)
    sh = Image.new("RGBA", wl.size, (0, 0, 0, 0))
    sh.putalpha(wl.split()[3].filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.6)))
    base.alpha_composite(sh, (int(c[0] - wl.width / 2 + 10), int(c[1] - wl.height / 2 + 16)))
    base.alpha_composite(wl, (int(c[0] - wl.width / 2), int(c[1] - wl.height / 2)))
    return base.convert("RGB")


def opt_a():
    s = sources()
    city, tr = s["city"], s["tr"]
    mid = ((s["a"][0] + s["b"][0]) / 2, (s["a"][1] + s["b"][1]) / 2)
    frames, durs = [city], [900]
    # the wheel slaps on (scale 1.3 -> 1), the hub shows the city behind (a closed lens) then opens
    for k, (ro, rot) in enumerate(((190, -30), (150, 0))):
        frames.append(lens_frame(city, city, mid, ro, ro * 0.32, rot, 1))
        durs.append(90)
    for k in range(4):
        frames.append(lens_frame(city, zoom_crop(city, mid, 1 + k * 0.4), mid, 150, 48 + k * 6, 60 * (k + 1), 1))
        durs.append(80)
    # the hub opens onto the transit view, the ring grows past the camera while it spins
    for k, ro in enumerate((220, 420, 820, 1500)):
        frames.append(lens_frame(city, tr, (mid[0] + (960 - mid[0]) * (k + 1) / 4, mid[1] + (540 - mid[1]) * (k + 1) / 4), ro, ro * 0.62,
                                 300 + 50 * k, 1))
        durs.append(90)
    frames.append(tr)
    durs.append(1600)
    save("zoom_a_wheel.gif", frames, durs)


# ------------------------------------------------------------------ B: sticker peel
def peel_frame(city, tr, s_px):
    Cn = np.array([W, H], np.float32)
    u = np.array([-1.0, -0.6], np.float32)
    u /= np.linalg.norm(u)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    t = (xx - Cn[0]) * u[0] + (yy - Cn[1]) * u[1]
    peeled = t < s_px
    # flap: the reflection of the peeled region over the fold line t = s
    rx = xx - 2 * (t - s_px) * u[0]
    ry = yy - 2 * (t - s_px) * u[1]
    flap = (t >= s_px) & (t < 2 * s_px) & (rx >= 0) & (rx < W) & (ry >= 0) & (ry < H) & \
        (((rx - Cn[0]) * u[0] + (ry - Cn[1]) * u[1]) < s_px)
    a_city = np.asarray(city, np.float32)
    a_tr = np.asarray(tr, np.float32)
    out = np.where(peeled[..., None], a_tr, a_city)
    # shadow of the flap on the revealed print
    shm = Image.fromarray((flap * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18))
    sh = np.asarray(shm, np.float32)[..., None] / 255
    shift = np.roll(np.roll(sh, 18, 0), 10, 1)
    out = out * (1 - 0.55 * shift * peeled[..., None])
    # the flap: sticker backing (adhesive side), lighter at the fold, with a die-cut white rim
    k = np.clip((t - s_px) / max(1.0, s_px), 0, 1)
    back = np.stack([224 - 40 * k, 221 - 40 * k, 214 - 40 * k], axis=-1)
    out = np.where(flap[..., None], back, out)
    edge = Image.fromarray((flap * 255).astype(np.uint8)).filter(ImageFilter.FIND_EDGES)
    e = np.asarray(edge.filter(ImageFilter.MaxFilter(3)), np.float32)[..., None] / 255
    out = out * (1 - e) + np.array([40, 34, 44], np.float32) * e
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def opt_b():
    s = sources()
    city, tr = s["city"], s["tr"]
    frames, durs = [city], [900]
    # a corner lifts (hover), then the peel runs across the whole sheet
    for sp in (60, 160, 340, 620, 960, 1340, 1800):
        frames.append(peel_frame(city, tr, sp))
        durs.append(140 if sp < 300 else 95)
    frames.append(tr)
    durs.append(1600)
    save("zoom_b_peel.gif", frames, durs)


# ------------------------------------------------------------------ C: grease-pencil dive
def pencil_ring(img, c, rx, ry, frac, width=10, seed=5):
    p = L.pen(L.GP_YELLOW, seed=seed)
    n = 34
    total = (2 * math.pi + 0.55) * frac
    pts = []
    for i in range(int(n * frac) + 2):
        a = -2.2 + total * min(1.0, i / max(1, n * frac))
        kk = 1 + 0.07 * i / n
        pts.append((c[0] + rx * kk * math.cos(a), c[1] + ry * kk * math.sin(a)))
    if len(pts) > 2:
        p.stroke(SL.catmull(pts, 6), width=width)
    return L.ink(img.convert("RGBA"), p)


def opt_c():
    s = sources()
    city, tr = s["city"], s["tr"]
    b = s["b"]
    frames, durs = [city], [800]
    for fr in (0.35, 0.7, 1.0):
        frames.append(pencil_ring(city, (b[0], b[1] - 14), 70, 52, fr).convert("RGB"))
        durs.append(90)
    durs[-1] = 260
    # the ring becomes a lens: outside darkens, the camera dives through the ring
    for k, z in enumerate((1.6, 2.8, 5.0, 9.0)):
        cz = zoom_crop(city, b, z)
        r = 70 * z * 0.9
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).ellipse([960 - r, 540 - r * 0.75, 960 + r, 540 + r * 0.75], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(10))
        inner = Image.blend(cz, tr, min(1.0, 0.25 + k * 0.28))
        dark = ImageEnhance.Brightness(cz).enhance(0.25)
        img = Image.composite(inner, dark, m)
        img = pencil_ring(img, (960, 540), r, r * 0.75, 1.0, width=10 + 4 * k, seed=6)
        frames.append(img.convert("RGB"))
        durs.append(100)
    frames.append(tr)
    durs.append(1600)
    save("zoom_c_pencil.gif", frames, durs)


# ------------------------------------------------------------------ D: CRT channel change
def crt_fx(img, k=1.0):
    a = np.asarray(img, np.float32)
    r = np.roll(a[..., 0], int(6 * k), 1)
    b = np.roll(a[..., 2], -int(6 * k), 1)
    a = np.stack([r, a[..., 1], b], -1)
    a[::3] *= 0.7
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def squash(img, sx, sy, bright=1.0):
    bg = Image.new("RGB", (W, H), (4, 4, 8))
    w, h = max(2, int(W * sx)), max(2, int(H * sy))
    im = ImageEnhance.Brightness(img.resize((w, h), Image.BILINEAR)).enhance(bright)
    bg.paste(im, ((W - w) // 2, (H - h) // 2))
    return bg


def osd(img, text):
    im = img.convert("RGBA")
    d = ImageDraw.Draw(im)
    d.text((1840, 70), text, font=L.f_mono(46), fill=(120, 255, 140, 255), anchor="ra", stroke_width=3, stroke_fill=(0, 30, 0, 255))
    return im.convert("RGB")


def opt_d():
    s = sources()
    city, tr = s["city"], s["tr"]
    frames, durs = [city], [800]
    frames.append(crt_fx(city, 1.5))
    durs.append(70)
    for sy in (0.35, 0.06, 0.006):
        frames.append(squash(crt_fx(city, 2), 1.0, sy, 1.6))
        durs.append(70)
    frames.append(squash(Image.new("RGB", (W, H), (240, 255, 250)), 0.08, 0.006))
    durs.append(70)
    frames.append(squash(Image.new("RGB", (W, H), (255, 255, 255)), 0.01, 0.01))
    durs.append(110)
    frames.append(Image.new("RGB", (W, H), (4, 4, 8)))
    durs.append(120)
    for sy in (0.006, 0.12, 0.6):
        frames.append(osd(squash(crt_fx(tr, 2), 1.0, sy, 1.5), "CH 15  DEPOT 15"))
        durs.append(70)
    frames.append(osd(crt_fx(tr, 0.8), "CH 15  DEPOT 15"))
    durs.append(400)
    frames.append(tr)
    durs.append(1500)
    save("zoom_d_crt.gif", frames, durs)


# ------------------------------------------------------------------ E: terminal connect + binary rain
LINES = ["> jack --from RELAY_4 --to DEPOT_15", "  routing via border link ... ok", "  handshake ......... ok", "> CONNECTED"]


def term(img, n_lines, cursor=True):
    c = L.CRT(720, 220, R.LIME, "CELL://JACK", tag="CELL-9", seed=97)
    for i, ln in enumerate(LINES[:n_lines]):
        c.text((20, 56 + i * 36), ln, 22, R.LIME if not ln.startswith("> C") else (255, 255, 255))
    if cursor:
        c.d.rectangle([20 + 13 * len(LINES[min(n_lines, len(LINES)) - 1]), 56 + (n_lines - 1) * 36, 34 + 13 * len(LINES[min(n_lines, len(LINES)) - 1]),
                       80 + (n_lines - 1) * 36], fill=R.LIME + (255,))
    return L.paste(img.convert("RGBA"), c.finish(), 600, 420).convert("RGB")


def rain(base, cover, a, b, t, seed=3):
    """Columns of 0/1 fall; density peaks along the link and spreads; cover = how much of the screen the rain has eaten."""
    rng = random.Random(seed)
    im = base.convert("RGBA")
    m = Image.new("L", (W, H), 0)
    dm = ImageDraw.Draw(m)
    d = ImageDraw.Draw(im)
    f = L.f_mono(20)
    for col in range(0, W, 20):
        # link proximity: the column's distance to the link line's x span
        tt = min(1, max(0, (col - a[0]) / max(1, b[0] - a[0])))
        ly = a[1] + (b[1] - a[1]) * tt
        near = math.exp(-abs(col - (a[0] + b[0]) / 2) / 600)
        head = (ly - 300 + rng.random() * 200) + t * 2400 * (0.5 + near)
        length = 300 + 900 * cover
        for k in range(int(length / 22)):
            y = head - k * 22
            if 0 <= y < H:
                v = max(0, 255 - k * 9)
                d.text((col, y), rng.choice("01"), font=f, fill=(212, 255, 0, v) if k else (255, 255, 255, 255))
        dm.rectangle([col, 0, col + 20, head - length * 0.3], fill=int(255 * min(1, cover * 1.3)))
    return im.convert("RGB"), m


def opt_e():
    s = sources()
    city, tr = s["city"], s["tr"]
    a, b = s["a"], s["b"]
    frames, durs = [city], [700]
    for n in (1, 2, 3, 4):
        frames.append(term(city, n))
        durs.append(220 if n < 4 else 360)
    black = Image.new("RGB", (W, H), (4, 6, 4))
    for i, (t, cov) in enumerate(((0.15, 0.2), (0.3, 0.5), (0.45, 0.85))):
        img, m = rain(term(city, 4, cursor=False), cov, a, b, t)
        img = Image.composite(black, img, m)
        img, _ = rain(img, cov, a, b, t, seed=4)
        frames.append(img)
        durs.append(110)
    for i, (t, cov) in enumerate(((0.6, 0.6), (0.75, 0.3), (0.9, 0.08))):
        under = Image.composite(black, tr, Image.new("L", (W, H), int(255 * cov)))
        img, _ = rain(under, cov, a, b, t, seed=5 + i)
        frames.append(img)
        durs.append(110)
    frames.append(tr)
    durs.append(1500)
    save("zoom_e_terminal.gif", frames, durs)


# ------------------------------------------------------------------ comparison strip
def compare():
    from PIL import ImageSequence
    rows = [("zoom_a_wheel.gif", "A  WHEEL LENS", "the spinner's hub opens onto the link"),
            ("zoom_b_peel.gif", "B  STICKER PEEL", "the map peels; the run is printed under it"),
            ("zoom_c_pencil.gif", "C  PENCIL DIVE", "ring the Site, dive through the ring"),
            ("zoom_d_crt.gif", "D  CRT CHANNEL", "scanline collapse, the link's channel opens"),
            ("zoom_e_terminal.gif", "E  TERMINAL JACK-IN", "typed connect, binary rain along the link")]
    tw, th = 300, 169
    img = Image.new("RGBA", (W, H), (9, 8, 14, 255))
    img = L.place_sticker(img, L.sticker_word(["CITY > LINK: FIVE WAYS IN"], 44, fills=["yellow"], seed=61), 420, 48, angle=-2)
    for r, (fn, title, sub) in enumerate(rows):
        g = Image.open(os.path.join(L.OUT, fn))
        fr = [f.convert("RGB").copy() for f in ImageSequence.Iterator(g)]
        pick = [fr[int(i * (len(fr) - 1) / 4)] for i in range(5)]
        y = 100 + r * 186
        d = ImageDraw.Draw(img)
        d.text((22, y + 20), title, font=L.f_ui(26, b"Bold"), fill=U.CYAN + (255,))
        d.text((22, y + 60), sub, font=L.f_mono(15), fill=(200, 210, 220, 255))
        for i, p in enumerate(pick):
            x = 360 + i * (tw + 10)
            img.alpha_composite(p.resize((tw, th), Image.LANCZOS).convert("RGBA"), (x, y))
            d.rectangle([x, y, x + tw, y + th], outline=(90, 100, 120, 255), width=1)
    p = L.pen(L.GP_YELLOW, seed=62)
    p.circle(190, 100 + 186 * 0 + 50, 170, 60, width=8)
    p.text("PICK", 300, 100 + 30, 30, angle=-8)
    img = L.ink(img, p)
    L.save(img, "zoom_compare.png")


if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv) > 1 else "all"
    for k, fn in (("a", opt_a), ("b", opt_b), ("c", opt_c), ("d", opt_d), ("e", opt_e), ("cmp", compare)):
        if w in (k, "all"):
            fn()
