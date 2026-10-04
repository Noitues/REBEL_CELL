"""Round 32 -> options_overview.png: five ways to lay out the netrun route (combined, separate, hybrid, own idea),
side by side, each with a thumbnail, three ratings (readability, art reuse, GDD fit) and pros / cons.

python overview.py   (needs route_b.png and route_c.png built first)
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageFilter

import r31lib as L
import r32ui as U
import sticker_lib19 as SL

CITY = os.path.join(L.CONCEPTS, "round30_meridian_castle", "city_night_hq_v6.jpg")
TW, TH = 362, 230


def city_crop(cx, cy, w, h):
    src = Image.open(CITY).convert("RGB")
    sw, sh = src.size
    box = (int(cx * sw - w / 2), int(cy * sh - h / 2), int(cx * sw + w / 2), int(cy * sh + h / 2))
    return src.crop(box).resize((TW * 2, TH * 2), Image.LANCZOS).convert("RGBA")


def mini_pad(img, x, y, r, col, lit=1.0):
    q = [(x, y - r * 0.5), (x + r, y), (x, y + r * 0.5), (x - r, y)]
    return U.pad(img, q, col, lit=lit, glow=0.6, k=0.8, pins=False)


def thumb_a():
    """A: the netrun drawn on the city itself around Meridian: an iso lattice of real sockets, 7 columns."""
    im = city_crop(0.70, 0.40, 980, 623)
    im = L.darken_rect(im, (-50, -50, 800, 520), a=70, blur=30)
    o = (60, 330)
    u = (88, -40)   # layer step along a map street
    v = (44, 26)    # row step across it
    nodes = {}
    rows = [[0, 1, 2], [0, 2], [0, 1, 2], [1, 2], [0, 1], [0, 2], [1]]
    for l, rr in enumerate(rows):
        for r in rr:
            nodes[(l, r)] = (o[0] + u[0] * l + v[0] * (r - 1) + 40, o[1] + u[1] * l + v[1] * (r - 1))
    walked = [(0, 1), (1, 0), (2, 1)]
    inl = U.Inlay((TW * 2, TH * 2), 0.8)
    keys = sorted(nodes)
    for (l, r) in keys:
        for (l2, r2) in keys:
            if l2 == l + 1 and abs(r2 - r) <= 1:
                a, b = nodes[(l, r)], nodes[(l2, r2)]
                mid = (a[0] + u[0] * 0.5, a[1] + u[1] * 0.5)
                col = U.LIME if ((l, r) in walked and (l2, r2) in walked) else U.MER
                inl.trace([a, mid, (mid[0] + (b[0] - mid[0]) * 0.0 + v[0] * (r2 - r), mid[1] + v[1] * (r2 - r)), b] if r2 != r else [a, b],
                          col, width=2.2, lanes=2, gap=3.5, glow=0.7, alpha=1.0 if col == U.LIME else 0.7)
    im = inl.lay(im)
    for k, (x, y) in nodes.items():
        im = mini_pad(im, x, y, 20, U.LIME if k in walked else U.MER, 1.0 if k in walked else 0.7)
    p = L.pen(L.GP_YELLOW, seed=5)
    p.size = im.size
    p.mask = Image.new("L", (im.width * SL.SS, im.height * SL.SS), 0)
    p.d = ImageDraw.Draw(p.mask)
    x, y = nodes[(2, 1)]
    p.circle(x, y, 34, 22, width=7)
    im = p.ink(im)
    return im.resize((TW, TH), Image.LANCZOS)


def thumb_crop(path, box):
    im = Image.open(os.path.join(L.OUT, path)).convert("RGBA").crop(box)
    return im.resize((TW, TH), Image.LANCZOS)


def thumb_d():
    a = thumb_a().crop((40, 0, 40 + 120, TH))
    c = Image.open(os.path.join(L.OUT, "route_c.png")).convert("RGBA").crop((150, 330, 1650, 1080)).resize((120, 60), Image.LANCZOS)
    b = Image.open(os.path.join(L.OUT, "route_b.png")).convert("RGBA").crop((420, 40, 1500, 1060)).resize((112, 106), Image.LANCZOS)
    im = Image.new("RGBA", (TW, TH), (10, 9, 16, 255))
    im.alpha_composite(a, (0, 0))
    im = L.darken_rect(im, (0, 0, 120, TH), a=60, blur=4)
    im.alpha_composite(c, (TW - 124, 22))
    im.alpha_composite(b, (TW - 120, 108))
    d = ImageDraw.Draw(im)
    for y0, y1 in ((22, 82), (108, 214)):
        d.rectangle([TW - 126, y0 - 2, TW - 2, y1 + 2], outline=U.LIME + (255,), width=2)
    # the zoom: lime brackets from the picked Site on the map out to each route view
    d.line([(96, 92), (TW - 128, 22)], fill=U.LIME + (180,), width=2)
    d.line([(96, 120), (TW - 128, 82)], fill=U.LIME + (180,), width=2)
    d.line([(96, 120), (TW - 124, 108)], fill=(255, 140, 26, 180), width=2)
    d.line([(96, 150), (TW - 124, 214)], fill=(255, 140, 26, 180), width=2)
    d.rectangle([84, 88, 108, 152], outline=U.LIME + (255,), width=2)
    for (x, y, s, c) in ((14, 16, "1 PICK", U.LIME), (150, 44, "2 SITE: C", U.LIME), (150, 196, "2 HQ: B", U.MER)):
        d.text((x, y), s, font=L.f_mono(13), fill=c + (255,), anchor="lm")
    return im


def thumb_e():
    """E: siege rings. The 7 layers as rings of the blocks around the target, closing in on it (iso ellipses)."""
    im = city_crop(0.69, 0.66, 980, 623)
    im = L.darken_rect(im, (-50, -50, 800, 520), a=80, blur=30)
    cx, cy = 360, 250
    inl = U.Inlay((TW * 2, TH * 2), 0.8)
    rings = [300, 250, 200, 155, 112, 72]
    n_per = [4, 3, 4, 3, 3, 2]
    nodes = []
    for ri, (R, n) in enumerate(zip(rings, n_per)):
        pts = [(cx + R * math.cos(a / 60 * 2 * math.pi), cy + R * 0.5 * math.sin(a / 60 * 2 * math.pi)) for a in range(61)]
        inl.trace(pts, U.MER, width=1.6, lanes=1, gap=3, glow=0.3, alpha=0.5, pads=False)
        for j in range(n):
            a = math.radians(200 + j * (140 / max(1, n - 1)) - ri * 8)
            nodes.append((ri, (cx + R * math.cos(a), cy + R * 0.5 * math.sin(a))))
    spiral = [nodes[1][1], nodes[5][1], nodes[8][1], nodes[12][1]]
    inl.trace(spiral + [(cx - 30, cy - 4)], U.LIME, width=2.4, lanes=2, gap=4, glow=1.0, pads=False)
    im = inl.lay(im)
    for ri, (x, y) in nodes:
        im = mini_pad(im, x, y, 18, U.MER, 0.7)
    for (x, y) in spiral:
        im = mini_pad(im, x, y, 18, U.LIME, 1.0)
    p = L.pen(L.GP_RED, seed=6)
    p.size = im.size
    p.mask = Image.new("L", (im.width * SL.SS, im.height * SL.SS), 0)
    p.d = ImageDraw.Draw(p.mask)
    p.circle(cx, cy - 30, 70, 60, width=8)
    im = p.ink(im)
    return im.resize((TW, TH), Image.LANCZOS)


CARDS = [
    dict(letter="A", title="COMBINED: ON THE CITY MAP", sub="zoom into the Site; real street sockets", raid=["same pads and links as raids, so the", "raid view must hide 20 netrun nodes", "per Site; one crowded map"], thumb=thumb_a,
         rate=(2, 5, 3), col=U.CYAN,
         pros=[["one map, one node language (raid", "pads + inlay links); little new art"], ["every run leaves marks on the city"]],
         cons=[["a street grid is not a 7-layer graph:", "15-20 nodes on busy iso art read", "poorly at map scale"], ["a pad means a fight here, a Site", "in raids"], ["every Site needs ~20 sockets round it"]]),
    dict(letter="B", title="SEPARATE: BUILDING CLIMB", sub="cutaway keep: floors = layers, rooms", raid=["raids unchanged on the city map;", "the cutaway is its own view (the HQ", "you raid is the HQ you climb)"], thumb=lambda: thumb_crop("route_b.png", (230, 40, 1690, 968)),
         rate=(5, 2, 4), col=U.MER, built="route_b.png",
         pros=[["up = progress, boss on top: reads", "at a glance"], ["the target finally has an inside;", "room light shows type and state"]],
         cons=[["a room kit per corp: the most art"], ["low Sites (depot, hospital) are not", "7 floors tall"], ["vertical on 16:9: 4 rooms a floor max"]]),
    dict(letter="C", title="SEPARATE: TRANSIT PATH", sub="the link to the Site, unrolled", raid=["the walked link IS the one the GDD", "opens on a clear: it shows lime on the", "city and raids can travel it"], thumb=lambda: thumb_crop("route_c.png", (330, 300, 1530, 1062)),
         rate=(5, 4, 5), col=U.LIME, built="route_c.png",
         pros=[["the run IS the link (tier chain):", "walked traces turn lime, later", "carry raids"], ["left to right, 7 columns; raid pads", "+ street kit reused; Site at the end"]],
         cons=[["corridor dressing per link", "(procedural; must not look samey)"], ["same direction every run"]]),
    dict(letter="D", title="HYBRID", sub="pick on the map; play C (Sites), B (HQ)", raid=["raids and claims stay on the city", "map; the route views only add to it", "(the link lights up after a run)"], thumb=thumb_d,
         rate=(5, 4, 5), col=U.PINK,
         pros=[["choose on the real city (A), play", "in a readable view; a zoom ties", "them into one world"], ["the HQ boss run gets its own climb"]],
         cons=[["two route views to build and test"], ["the zoom must stay under 1 s and", "be skippable"]]),
    dict(letter="E", title="OWN IDEA: SIEGE RINGS", sub="combined, local: rings close in", raid=["the rings could seed the claimed", "Site's defence sockets (needs a GDD", "rule; not in the game yet)"], thumb=thumb_e,
         rate=(3, 5, 4), col=U.CYAN,
         pros=[["the Site is the bullseye: layers are", "rings of its blocks closing in"], ["same city art and pads as raids"]],
         cons=[["radial: which way is forward?"], ["the far side hides behind the", "building"], ["rings crowd the iso view"]]),
]


def card(img, x, y, w, h, c):
    p = L.CRT(w, h, c["col"], c["title"], seed=ord(c["letter"]))
    th = c["thumb"]()
    p.paste(th, (w - TW) // 2, 64)
    p.text((14, 50), c["sub"], 14, (190, 200, 210))
    yy = 64 + TH + 16
    for lab, v in zip(("READABLE", "ART REUSE", "GDD FIT"), c["rate"]):
        p.text((16, yy), lab, 15, (200, 210, 220))
        p.bar(130, yy + 1, 5, v, w=26, h=14, gap=5, col=c["col"] if c["col"] != U.CYAN else (120, 210, 240))
        p.text((w - 16, yy), "%d/5" % v, 15, (200, 210, 220), anchor="ra")
        yy += 26
    yy += 6
    p.rule(yy, dash=True)
    yy += 10
    for sign, items, col in (("+", c["pros"], (150, 240, 160)), ("-", c["cons"], (255, 150, 140))):
        for b in items:
            for n, s in enumerate(b):
                p.text((16, yy), (sign + " " if n == 0 else "  ") + s, 14, col)
                yy += 19
            yy += 3
        yy += 6
    p.rule(yy, dash=True)
    p.text((16, yy + 10), "CITY + RAIDS", 14, c["col"])
    yy += 32
    for s in c["raid"]:
        p.text((16, yy), s, 14, (170, 210, 230))
        yy += 19
    im = p.finish()
    img = L.paste(img, im, x, y)
    sd = L.sticker_word([c["letter"]], 46, fills=[("grad", tuple(min(255, v + 60) for v in c["col"]), c["col"])], seed=ord(c["letter"]), extrude=4)
    img = L.place_sticker(img, sd, x + w - 48, y + 18, angle=-6)
    return img


def main():
    img = Image.new("RGBA", (1920, 1080), (9, 8, 14, 255))
    bg = L.backdrop(CITY, blur=10, dim=0.28, sat=0.6)
    img = Image.alpha_composite(img, bg)
    img = L.vignette(img, 0.7)
    img = L.place_sticker(img, L.sticker_word(["NETRUN ROUTE"], 58, fills=["yellow"], seed=31), 230, 58, angle=-2)
    d = ImageDraw.Draw(img)
    d.text((470, 44), "ONE MAP OR SEPARATE?  FIVE LAYOUTS FOR THE SAME RUN", font=L.f_ui(28, b"Bold"), fill=(240, 240, 245, 255), anchor="lm")
    d.text((470, 80), "GDD 4.2: one operative, one Site, ~15 min; 7 layers of 2-4 nodes; Server Racks at L4 (optional) and L7 (final, holds the Exploit on T2+)",
           font=L.f_mono(16), fill=(170, 190, 200, 255), anchor="lm")
    w, gap, x0, y0, h = 365, 12, 22, 118, 712
    xs = []
    for i, c in enumerate(CARDS):
        x = x0 + i * (w + gap)
        xs.append(x)
        img = card(img, x, y0, w, h, c)
    # pencil: the two built ones, and the recommendation
    p = L.pen(L.GP_YELLOW, seed=33)
    p.text("BUILT: route_b", xs[1] + w / 2, y0 + h + 22, 26, angle=-2)
    p.text("BUILT: route_c", xs[2] + w / 2, y0 + h + 22, 26, angle=-2)
    p.text("PICK THIS", xs[3] + w / 2, y0 + h + 22, 30, angle=-3)
    img = L.ink(img, p)
    c = L.CRT(1876, 172, U.LIME, "RECOMMENDATION", tag="D = A + C + B", seed=41)
    c.text((18, 52), "D, the hybrid. Choose the target on the real city (the city map you already have), then zoom into a route view built for reading:", 18, (235, 245, 235))
    c.text((18, 80), "  * every Site netrun runs along its LINK (C): the walked traces turn lime, so the link the GDD opens on a clear is the one you drew;", 17, (210, 235, 200))
    c.text((18, 106), "  * the corp HQ boss run is a CLIMB (B) up the HQ you have seen all campaign (Meridian's keep, Halcyon's tiers, Solace's helix).", 17, (210, 235, 200))
    c.text((18, 134), "Raids stay on the city map with the same pads and inlay links: a node means the same thing in every view. Mid-run raids zoom out to the map and back.", 16, (170, 200, 180))
    img = L.paste(img, c.finish(), 22, 892)
    img = L.bloom(img, 0.12, 0.82, 8)
    L.save(img, "options_overview.png")


if __name__ == "__main__":
    main()
