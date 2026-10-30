"""Round 35 -> city_view.png: the city grid at a closer zoom, with a denser Site network and map panning.

No planning UI (the plan lives in the player's head). The view shows only nodes, what they are, and links:
  OWNED      lime   the Cell's territory (raid nodes)
  AVAILABLE  orange every unowned Site across a border link from ANY owned node (no cap: the graph decides)
  NOT YET    white  everything else, still visible with its tier
  PAST       grey   Sites already run and used up (cleared, not claimed)
Tier sits on each node; tier-3 nodes that carry a Central Server key get a gold key plate. The parts of the city that
don't matter to this campaign are greyed a little. The TARGET (Meridian HQ, the Central Server) keeps its red circle.

python city_view.py   (also used by the transition GIFs: city_layer(), NET)
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

import r31lib as L
import r32ui as U
import r35ui as R
import sticker_lib19 as SL

CITY = os.path.join(L.CONCEPTS, "round30_meridian_castle", "city_night_hq_v6.jpg")
CROP = (860, 420, 2140, 1140)
O, S = (450.6, 1005.2), 76.0
HQ = (1483.0, 210.0)
HALCYON = (1365.0, 935.0)
CELLC = (604.0, 1005.0)


def iso(i, j):
    return (O[0] + S * (i - j), O[1] - S * 0.5 * (i + j))


def blocked(x, y):
    """Keep nodes out from under the panels."""
    return (x < 400 and y < 600) or (x < 390 and y > 800) or (x > 1460 and 540 < y < 1040) or (650 < x < 1270 and y < 110) or y > 1010


def build_net(seed=35):
    rng = random.Random(seed)
    nodes = {}
    for i2 in range(-6, 26):
        for j2 in range(-14, 14):
            i, j = i2, j2
            x, y = iso(i, j)
            if not (60 < x < 1880 and 60 < y < 1040) or blocked(x, y):
                continue
            if math.hypot((x - HALCYON[0]) / 1.6, y - HALCYON[1]) < 150:
                continue  # Halcyon's grounds: another corp's grid
            if math.hypot(x - HQ[0], (y - HQ[1] - 30) * 1.6) < 200 or (1370 < x < 1610 and 60 < y < 120):
                continue
            if rng.random() > 0.5:
                continue
            nodes[(i, j)] = dict(xy=(x + rng.uniform(-8, 8), y + rng.uniform(-4, 4)))
    links = set()
    keys = sorted(nodes)
    for (i, j) in keys:
        for di, dj in ((1, 0), (0, 1)):
            for k in (1, 2):
                n = (i + di * k, j + dj * k)
                if n in nodes:
                    links.add(((i, j), n))
                    break
    # tiers by progress toward the HQ
    a = np.array(CELLC), np.array(HQ)
    v = a[1] - a[0]
    for k, n in nodes.items():
        p = float(np.dot(np.array(n["xy"]) - a[0], v) / np.dot(v, v))
        n["p"] = p
        n["tier"] = 1 if p < 0.45 else (2 if p < 0.7 else 3)
        n["state"] = "owned" if p < 0.2 else "white"
    past = sorted([k for k in nodes if 0.2 <= nodes[k]["p"] < 0.3], key=lambda k: (nodes[k]["p"], k))[:2]
    for k in past:
        nodes[k]["state"] = "past"
    for (a_, b_) in links:
        for x, y in ((a_, b_), (b_, a_)):
            if nodes[x]["state"] == "owned" and nodes[y]["state"] == "white":
                nodes[y]["state"] = "available"
    # three tier-3 nodes carry the Central Server keys
    t3 = sorted([k for k in nodes if nodes[k]["tier"] == 3], key=lambda k: (iso(*k)[0], k))
    for k in (t3[1], t3[len(t3) // 2], t3[-2]):
        nodes[k]["key"] = True
    return nodes, sorted(links)


NET = build_net()


def link_state(nodes, a, b):
    sa, sb = nodes[a]["state"], nodes[b]["state"]
    if sa == "owned" and sb == "owned":
        return "owned"
    if "owned" in (sa, sb) and "available" in (sa, sb):
        return "border"
    if "past" in (sa, sb) and ("owned" in (sa, sb) or sa == sb):
        return "past"
    return "white"


def base_map():
    im = Image.open(CITY).convert("RGB").crop(CROP).resize((1920, 1080), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(2, 60, 2))
    # grey out what doesn't matter to this campaign: outside the network's band, and the other corps' districts
    yy, xx = np.mgrid[0:1080, 0:1920].astype(np.float32)
    # the band from the Cell's district to the HQ
    p0, p1 = np.array(CELLC), np.array(HQ)
    v = p1 - p0
    t = np.clip(((xx - p0[0]) * v[0] + (yy - p0[1]) * v[1]) / (v @ v), 0, 1)
    dx, dy = xx - (p0[0] + v[0] * t), yy - (p0[1] + v[1] * t)
    dist = np.sqrt(dx * dx + dy * dy)
    m = np.clip((dist - 430) / 260, 0, 1)
    m = np.maximum(m, np.clip(1 - np.hypot((xx - HALCYON[0]) / 1.3, yy - HALCYON[1] - 30) / 230, 0, 1) * 0.9)
    a = np.asarray(im, np.float32)
    g = a.mean(axis=2, keepdims=True)
    a = a * (1 - m[..., None] * 0.75) + g * m[..., None] * 0.75
    a = a * (1 - m[..., None] * 0.38)
    a = a * 0.86  # the map dims a step under the network (city HUD treatment)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def diamond(x, y, r):
    return [(x, y - r * 0.5), (x + r, y), (x, y + r * 0.5), (x - r, y)]


COL = {"owned": R.LIME, "available": R.MER, "white": R.WHITE, "past": R.GREY}


def city_layer(base, selected=None, badges=True):
    nodes, links = NET
    img = base.copy()
    inl = U.Inlay()
    for a, b in links:
        st = link_state(nodes, a, b)
        pa, pb = nodes[a]["xy"], nodes[b]["xy"]
        if st == "owned":
            inl.trace([pa, pb], R.LIME, width=2.6, lanes=3, gap=4.5, glow=1.0, pads=False)
        elif st == "border":
            inl.trace([pa, pb], R.MER, width=2.6, lanes=3, gap=4.5, glow=0.9, pads=False)
        elif st == "past":
            inl.trace([pa, pb], R.GREY, width=2.0, lanes=2, gap=4.0, glow=0.0, alpha=0.85, pads=False)
        else:
            inl.trace([pa, pb], R.WHITE, width=1.6, lanes=2, gap=3.5, glow=0.15, alpha=0.8, pads=False)
    img = inl.lay(img)
    for k in sorted(nodes, key=lambda k: nodes[k]["xy"][1]):
        n = nodes[k]
        x, y = n["xy"]
        st = n["state"]
        r = 20 if st in ("owned", "available") else 16
        img = U.pad(img, diamond(x, y, r), COL[st], lit={"owned": 1.0, "available": 1.0, "white": 0.85, "past": 0.6}[st],
                    glow={"owned": 0.7, "available": 0.9}.get(st, 0.1), fill_a=215, k=0.85)
        if n.get("key"):  # a tier-3 key node: a second, gold socket ring + the gold key plate
            img = U.pad(img, diamond(x, y, r + 16), R.GOLD, lit=1.0, glow=0.9, fill_a=0, k=0.9, pins=False)
        if badges and st != "owned":
            img = R.tier_badge(img, x, y - 24, n["tier"], COL[st], key=n.get("key", False), size=13)
    # the TARGET: Meridian HQ, the Central Server (red pencil circle, labelled)
    hx, hy = HQ
    img = U.pad(img, diamond(hx, hy + 70, 110), (255, 120, 90), lit=0.6, glow=0.3, fill_a=0, k=1.4)
    pr = L.pen(L.GP_RED, seed=351)
    pr.circle(hx, hy + 30, 190, 120, width=10)
    pr.text("TARGET", hx - 210, hy + 160, 40, angle=-8)
    img = L.ink(img, pr)
    img = U.chip(img, (hx, hy + 170), "CENTRAL SERVER  //  KEYS 0 / 3", R.GOLD, 14)
    if selected:
        x, y = nodes[selected]["xy"]
        d = ImageDraw.Draw(img)
        for (cx, cy, sx, sy) in ((x - 38, y - 30, 1, 1), (x + 38, y - 30, -1, 1), (x - 38, y + 22, 1, -1), (x + 38, y + 22, -1, -1)):
            d.line([(cx, cy), (cx + sx * 12, cy)], fill=R.LIME + (255,), width=3)
            d.line([(cx, cy), (cx, cy + sy * 12)], fill=R.LIME + (255,), width=3)
    return img


def minimap(w=320, h=180, view=CROP):
    src = Image.open(CITY).convert("RGB")
    sw, sh = src.size
    mm = src.resize((w, h), Image.BILINEAR)
    mm = ImageEnhance.Brightness(ImageEnhance.Color(mm).enhance(0.45)).enhance(0.6).convert("RGBA")
    d = ImageDraw.Draw(mm)
    k = w / sw
    d.rectangle([view[0] * k, view[1] * k, view[2] * k, view[3] * k], outline=R.LIME + (255,), width=2)
    hx, hy = 1856 * k, 480 * k
    d.ellipse([hx - 6, hy - 6, hx + 6, hy + 6], outline=(255, 60, 60, 255), width=2)
    cx, cy = 1180 * k, 1100 * k
    d.ellipse([cx - 9, cy - 5, cx + 9, cy + 5], fill=R.LIME + (200,))
    c = L.CRT(w + 24, h + 70, U.CYAN, "MINIMAP", tag="DRAG / WASD", seed=353)
    c.paste(mm, 12, 46)
    c.text((12, h + 52), "lime = you   red = target   box = view", 13, (170, 200, 210))
    return c.finish()


def pan_cues(img):
    """Edge chevrons: the map continues (the Cell's home district down-left, more Sites up and right)."""
    d = ImageDraw.Draw(img)
    for (x, y, ang, s) in ((960, 18, -90, "MORE SITES"), (1902, 540, 0, ""), (960, 1062, 90, "")):
        a = math.radians(ang)
        for k in (0, 14):
            px, py = x - math.cos(a) * k, y - math.sin(a) * k
            pts = [(px + math.cos(a) * 10, py + math.sin(a) * 10),
                   (px + math.cos(a + 2.4) * 12, py + math.sin(a + 2.4) * 12),
                   (px + math.cos(a - 2.4) * 12, py + math.sin(a - 2.4) * 12)]
            d.polygon(pts, fill=U.CYAN + (200 - k * 6,))
    return img


SELECTED = None


def pick_selected():
    nodes, _ = NET
    av = sorted([k for k in nodes if nodes[k]["state"] == "available"], key=lambda k: (nodes[k]["xy"][0], k))
    return av[-1]


def hud(img, sel):
    nodes, _ = NET
    img = L.place_sticker(img, L.sticker_word(["THE GRID"], 58, fills=["yellow"], seed=31), 168, 56, angle=-3)
    img = R.heat_strip(img, (700, 22), 41, "NOTICED", w=520)
    dz = R.dossier()
    dz = dz.resize((int(dz.width * 0.86), int(dz.height * 0.86)), Image.LANCZOS)
    img = L.drop_shadow(img, dz, 22, 112, blur=14, off=(8, 12), op=0.6)
    img = L.paste(img, minimap(), 22, 812)
    n = nodes[sel]
    x, y = n["xy"]
    box = (1480, 560, 1898, 770)
    img = R.node_info(img, box, "DEPOT 15", "T%d" % n["tier"], ["+9 Schematics, Firmware", "1 armory asset"], "Logistics depot")
    d = ImageDraw.Draw(img)
    d.line([(x + 40, y), (box[0], box[1] + 30)], fill=R.LIME + (160,), width=2)
    img = L.place_sticker(img, L.sticker_word(["JACK IN"], 78, fills=["pink"], seed=8), 1690, 880, angle=-3)
    d = ImageDraw.Draw(img)
    d.text((1690, 966), "from any owned node across the border", font=L.f_mono(15), fill=(220, 220, 230, 255), anchor="mm")
    # the key (states only) + the pan hints, one terminal strip along the foot
    c = L.CRT(1080, 46, U.CYAN, None, header=False, seed=354)
    x0 = 16
    for col, s in ((R.LIME, "owned"), (R.MER, "available"), (R.WHITE, "not yet"), (R.GREY, "already run")):
        c.d.polygon(diamond(x0 + 12, 23, 12), fill=col + (255,))
        x0 += 30 + int(c.text((x0 + 30, 13), s, 15, (215, 225, 230))) + 24
    c.text((x0 + 10, 13), "|   DRAG / WASD  pan    WHEEL  zoom    TAB  next available", 15, U.CYAN)
    img = L.paste(img, c.finish(scan=0.15), 400, 1026)
    return img


def render(selected=True):
    sel = pick_selected()
    img = city_layer(base_map(), selected=sel if selected else None)
    img = pan_cues(img)
    return img, sel


def main():
    img, sel = render()
    img = hud(img, sel)
    img = L.bloom(img, 0.12, 0.82, 8)
    L.save(img, "city_view.png")


if __name__ == "__main__":
    main()
