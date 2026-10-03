"""Round 31 -> netrun_map.png: the netrun route through a corp Site, planned in grease pencil on an
intercepted corp site plan (paper = corp artifact). Nodes are die-cut stickers (node kinds don't change);
the plan (walked route, live choices, numbers, ticks) is yellow grease pencil; the threat (the Rack's
guardian) is red. Live info (route choices with Heat cost, the key) sits on the Cell's CRT.

7 layers, 2-4 nodes, Racks at layer 4 (optional) and 7 (final), Modem in layers 3-5 (GDD 4.2).

python netrun_map.py
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageFilter

import r31lib as L
import sticker_lib19 as SL

BG = os.path.join(L.CONCEPTS, "round26_hq_targets", "site_meridian_night.jpg")
MER = (255, 140, 26)
PAPER_BOX = (60, 150, 1500, 1040)

KIND = {
    "router": dict(col=(40, 36, 52), ring=(92, 225, 255), name="ROUTER"),
    "elite": dict(col=(120, 40, 14), ring=MER, name="ELITE"),
    "terminal": dict(col=(14, 60, 36), ring=(61, 255, 139), name="TERMINAL"),
    "modem": dict(col=(90, 16, 60), ring=(255, 61, 168), name="MODEM"),
    "rack": dict(col=(60, 30, 8), ring=MER, name="SERVER RACK"),
}

# layer -> list of (kind, y)
X = [215, 395, 575, 755, 935, 1115, 1330]
LAYERS = [
    [("router", 360), ("router", 600), ("router", 840)],
    [("router", 300), ("terminal", 560), ("router", 820)],
    [("modem", 420), ("elite", 650), ("router", 890)],
    [("router", 330), ("rack", 560), ("terminal", 800)],
    [("elite", 420), ("modem", 640), ("terminal", 880)],
    [("router", 360), ("elite", 600), ("router", 840)],
    [("rack", 600)],
]
EDGES = [
    [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)],
    [(0, 0), (1, 0), (1, 1), (2, 2), (2, 1)],
    [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)],
    [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)],
    [(0, 0), (1, 1), (1, 0), (2, 2), (2, 1)],
    [(0, 0), (1, 0), (2, 0)],
]
WALKED = [(0, 1), (1, 1), (2, 0)]   # (layer, index): layer-3 Modem is where the operative stands
CURRENT = (2, 0)
NEXT = [(3, 0), (3, 1)]


def pos(l, i):
    return X[l], LAYERS[l][i][1]


def icon(kind, px):
    S = 2
    out_px = px
    px = max(px, 110)
    P = px * S
    im = Image.new("RGBA", (P, P), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    k = KIND[kind]
    if kind == "rack":
        d.rounded_rectangle([4 * S, 2 * S, P - 4 * S, P - 2 * S], radius=10 * S, fill=k["col"] + (255,), outline=L.INK + (255,), width=3 * S)
        d.rounded_rectangle([9 * S, 7 * S, P - 9 * S, P - 7 * S], radius=7 * S, outline=k["ring"] + (255,), width=4 * S)
        n = 5
        for j in range(n):
            y0 = 18 * S + j * (P - 36 * S) / n
            d.rectangle([20 * S, y0, P - 20 * S, y0 + (P - 36 * S) / n - 5 * S], fill=(28, 22, 18, 255), outline=(120, 80, 40, 255), width=S)
            for q in range(3):
                d.ellipse([26 * S + q * 9 * S, y0 + 4 * S, 31 * S + q * 9 * S, y0 + 9 * S], fill=(255, 190, 60, 255) if (j + q) % 2 else (80, 255, 140, 255))
            d.rectangle([P - 44 * S, y0 + 5 * S, P - 26 * S, y0 + 8 * S], fill=(150, 120, 90, 255))
    else:
        d.ellipse([3 * S, 3 * S, P - 3 * S, P - 3 * S], fill=k["col"] + (255,), outline=L.INK + (255,), width=3 * S)
        d.ellipse([8 * S, 8 * S, P - 8 * S, P - 8 * S], outline=k["ring"] + (255,), width=4 * S)
        g = None
        if kind == "router":
            g = L.glyph("slice_exploit", int(P * 0.5), ow=2 * S)
        elif kind == "elite":
            g = L.glyph("slice_zero_day", int(P * 0.54), fill=(255, 220, 160), ow=2 * S)
        if g is not None:
            im.alpha_composite(g, ((P - g.width) // 2, (P - g.height) // 2))
        if kind == "terminal":
            x0, y0, x1, y1 = P * 0.26, P * 0.3, P * 0.74, P * 0.66
            d.rounded_rectangle([x0, y0, x1, y1], radius=4 * S, fill=(10, 30, 18, 255), outline=(255, 255, 255, 255), width=3 * S)
            d.text((x0 + 7 * S, (y0 + y1) / 2), ">_", font=L.f_mono(int(P * 0.2)), fill=(61, 255, 139, 255), anchor="lm")
            d.rectangle([P * 0.42, y1, P * 0.58, y1 + 6 * S], fill=(255, 255, 255, 255))
        if kind == "modem":
            x0, y0, x1, y1 = P * 0.3, P * 0.38, P * 0.7, P * 0.72
            d.rounded_rectangle([x0, y0, x1, y1], radius=4 * S, fill=(255, 255, 255, 255), outline=L.INK + (255,), width=2 * S)
            d.arc([P * 0.38, P * 0.24, P * 0.62, P * 0.5], 180, 360, fill=(255, 255, 255, 255), width=4 * S)
            d.text((P / 2, (y0 + y1) / 2 + S), "M", font=L.font(L.ANTON, int(P * 0.22)), fill=(140, 20, 90, 255), anchor="mm")
    return im.resize((out_px, out_px), Image.LANCZOS)


_sd = {}


def node_sd(kind, px, grey=False):
    key = (kind, px, grey)
    if key not in _sd:
        sd = L.sticker_from_art(icon(kind, px), border=5, seed=sum(map(ord, kind)) % 97)
        _sd[key] = L.greyscale(sd, 0.75) if grey else sd
    return _sd[key]


def site_plan():
    w, h = PAPER_BOX[2] - PAPER_BOX[0], PAPER_BOX[3] - PAPER_BOX[1]
    im = L.paper(w, h, seed=21, tint=(234, 228, 212))
    d = ImageDraw.Draw(im, "RGBA")
    rng = random.Random(4)
    plan = (66, 96, 132)
    # city section as a printed plan: blocks between streets
    streets_x = [120, 300, 480, 660, 840, 1020, 1190]
    streets_y = [210, 460, 700]
    for sx in streets_x:
        d.rectangle([sx - 14, 70, sx + 14, h - 40], fill=(214, 208, 192, 255))
    for sy in streets_y:
        d.rectangle([20, sy - 14, w - 20, sy + 14], fill=(214, 208, 192, 255))
    for i in range(len(streets_x) - 1):
        for j in range(len(streets_y) + 1):
            x0, x1 = streets_x[i] + 22, streets_x[i + 1] - 22
            y0 = (streets_y[j - 1] + 22) if j > 0 else 84
            y1 = (streets_y[j] - 22) if j < len(streets_y) else h - 50
            n = rng.randint(1, 2)
            for q in range(n):
                cy0 = y0 + (y1 - y0) * q / n + 6
                cy1 = y0 + (y1 - y0) * (q + 1) / n - 6
                bx0 = x0 + rng.uniform(4, 18)
                bx1 = x1 - rng.uniform(4, 30)
                by0 = cy0 + rng.uniform(2, 12)
                by1 = cy1 - rng.uniform(2, 12)
                if by1 - by0 < 30:
                    continue
                d.rectangle([bx0, by0, bx1, by1], fill=(226, 220, 204, 255), outline=plan + (150,), width=2)
                if rng.random() < 0.5:
                    mx = (bx0 + bx1) / 2 + rng.uniform(-20, 20)
                    d.line([(mx, by0), (mx, by1)], fill=plan + (90,), width=1)
    for sx in streets_x:
        for y in range(80, h - 40, 22):
            d.line([(sx, y), (sx, y + 10)], fill=plan + (90,), width=1)
    # the depot (target building) at the right: heavy outline + hatch
    tx0, ty0, tx1, ty1 = 1205, 300, 1420, 760
    d.rectangle([tx0, ty0, tx1, ty1], fill=(255, 210, 160, 120), outline=(180, 80, 10, 255), width=5)
    for hx in range(tx0 - (ty1 - ty0), tx1, 16):
        d.line([(max(tx0, hx), ty0 + max(0, tx0 - hx)), (min(tx1, hx + (ty1 - ty0)), min(ty1, ty0 + (tx1 - hx)))], fill=(180, 80, 10, 70), width=2)
    d.text(((tx0 + tx1) / 2, ty1 + 26), "DEPOT 15  //  RACK HALL", font=L.font(L.TYPE_B, 18), fill=(150, 64, 10, 255), anchor="mm")
    # street labels
    f = L.font(L.TYPE, 15)
    for sy, nm in zip(streets_y, ("QUAY ROAD", "LANE 15", "CONTAINER YARD ACCESS")):
        d.text((40, sy - 9), nm, font=f, fill=plan + (220,))
    # header
    d.rectangle([0, 0, w, 62], fill=(28, 22, 18, 255))
    d.text((24, 31), "MERIDIAN FREIGHT SYSTEMS", font=L.font(L.ANTON, 30), fill=MER + (255,), anchor="lm")
    d.text((420, 32), "NETWORK TOPOLOGY  //  SITE 15  //  T2  //  INTERNAL", font=L.font(L.TYPE_B, 18), fill=(230, 220, 200, 255), anchor="lm")
    # printed roads between nodes (thin plan lines = every road)
    for l, edges in enumerate(EDGES):
        for a, b in edges:
            p0, p1 = pos(l, a), pos(l + 1, b)
            q0 = (p0[0] - PAPER_BOX[0], p0[1] - PAPER_BOX[1])
            q1 = (p1[0] - PAPER_BOX[0], p1[1] - PAPER_BOX[1])
            d.line([q0, q1], fill=plan + (170,), width=3)
    # layer ruler
    for l, x in enumerate(X):
        d.text((x - PAPER_BOX[0], h - 24), "L%d" % (l + 1), font=L.font(L.TYPE_B, 16), fill=plan + (220,), anchor="mm")
    st = L.stamp("CONFIDENTIAL", 30, angle=-6, seed=3)
    im.alpha_composite(st, (w - st.width - 30, 72))
    return im


def route_panel():
    c = L.CRT(360, 330, L.YEL, "NEXT", tag="FROM THE MODEM", seed=51)
    rows = [("1", "router", "ROUTER", "HEAT +0", "fight, common chip"), ("2", "rack", "SERVER RACK", "HEAT +3", "optional, banks Schematics")]
    y = 56
    for n, k, nm, ht, sub in rows:
        c.text((20, y), n, 40, L.YEL, fnt=L.f_num(44))
        c.paste(icon(k, 52), 58, y + 2)
        c.text((124, y + 4), nm, 22, (255, 255, 255), fnt=L.f_num(26))
        c.text((124, y + 36), sub, 14, (200, 190, 140))
        c.text((340, y + 8), ht, 16, L.HEAT if ht != "HEAT +0" else (150, 220, 150), anchor="ra")
        y += 92
    c.rule(y + 2, dash=True)
    c.text((20, y + 14), "ahead: 2 elites, 1 modem, 2 terminals", 14, (170, 170, 150))
    c.text((20, y + 36), "end: SERVER RACK (guarded)", 14, MER)
    return c.finish()


def key_panel():
    c = L.CRT(360, 330, L.CYAN, "ROUTE KEY", seed=52)
    y = 52
    for k in ("router", "elite", "terminal", "modem", "rack"):
        c.paste(icon(k, 40), 20, y)
        c.text((74, y + 8), KIND[k]["name"], 18, (230, 240, 245))
        y += 46
    c.text((210, 60), "tick  = visited", 14, (190, 200, 150))
    c.text((210, 84), "ring  = you", 14, (190, 200, 150))
    c.text((210, 108), "1 2   = choices", 14, (190, 200, 150))
    c.text((210, 132), "grey  = cut off", 14, (190, 200, 150))
    c.text((210, 156), "solid = walked", 14, (190, 200, 150))
    c.text((210, 180), "dash  = what-if", 14, (190, 200, 150))
    return c.finish()


def main():
    img = L.backdrop(BG, blur=6, dim=0.4, sat=0.7)
    img = L.vignette(img, 0.75)
    plan = L.rotate_rgba(site_plan(), 0)
    img = L.drop_shadow(img, plan, PAPER_BOX[0], PAPER_BOX[1], blur=20, off=(14, 22), op=0.7)
    img = L.paste(img, L.tape(160, 40, angle=-6, seed=3), 1180, 132)
    # nodes
    reach = set()
    frontier = {CURRENT}
    for l in range(CURRENT[0], 6):
        nxt = set()
        for (ll, a) in frontier:
            for (ea, eb) in EDGES[ll]:
                if ea == a:
                    nxt.add((ll + 1, eb))
        reach |= nxt
        frontier = nxt
    walked = set(WALKED)
    for l, layer in enumerate(LAYERS):
        for i, (k, y) in enumerate(layer):
            x = X[l]
            px = 120 if (k == "rack" and l == 6) else 78
            past = l < CURRENT[0] or (l == CURRENT[0] and (l, i) != CURRENT)
            grey = (past and (l, i) not in walked) or (l > CURRENT[0] and (l, i) not in reach)
            sd = node_sd(k, px, grey=grey)
            img = L.place_sticker(img, sd, x, y, angle=((l * 7 + i * 13) % 9) - 4, opacity=0.75 if grey else 1.0)
    # grease pencil: walked route (solid), ticks, current ring, numbered choices (dashed what-if)
    p = L.pen(L.GP_YELLOW, seed=61)
    route = [(X[l], LAYERS[l][i][1]) for l, i in WALKED]
    route = [(60, 600)] + route
    p.stroke(SL.catmull(p.wobble(route, 1.5), 14), width=10)
    for (l, i) in WALKED[:-1]:
        x, y = pos(l, i)
        p.stroke(SL.catmull([(x + 34, y - 46), (x + 44, y - 34), (x + 68, y - 70)], 6), width=8, taper=False)
    cx, cy = pos(*CURRENT)
    p.circle(cx, cy, 62, 58, width=10)
    for n, (l, i) in enumerate(NEXT):
        x, y = pos(l, i)
        pts = SL.catmull([(cx + 50, cy + (y - cy) * 0.1), ((cx + x) / 2, (cy + y) / 2 + (-20 if n == 0 else 20)), (x - (70 if l == 3 and i == 1 else 50), y)], 16)
        for j in range(0, len(pts) - 3, 6):
            p.stroke(pts[j:j + 4], width=8, taper=False)
        p.text(str(n + 1), x - 10, y - (88 if i == 1 else 68), 46)
    img = L.ink(img, p)
    # the operative's token on the current node (the crowbar emblem, Breaker)
    tok = L.sticker_from_art(L.glyph("slice_exploit", 60, fill=(255, 61, 168), ow=4), border=6, seed=77)
    img = L.place_sticker(img, tok, cx + 44, cy - 52, angle=-18, hover=0.5)
    # red: the Rack's guardian
    pr = L.pen(L.GP_RED, seed=62)
    rx, ry = pos(6, 0)
    pr.circle(rx, ry, 100, 104, width=10)
    pr.text("LOGISTICS DIRECTOR", rx - 20, ry + 150, 30, angle=-4)
    img = L.ink(img, pr)
    # live panels (CRT) + header
    img = L.paste(img, route_panel(), 1540, 150)
    img = L.paste(img, key_panel(), 1540, 500)
    sd = L.sticker_word(["NETRUN"], 72, fills=["yellow"], seed=63)
    img = L.place_sticker(img, sd, 230, 72, angle=-3)
    strip = L.CRT(860, 42, L.CYAN, None, header=False, seed=53)
    strip.text((16, 10), "ROUTE  //  MERIDIAN DEPOT 15  //  T2  //  LAYER 3 OF 7  //  HEAT 52", 19, L.CYAN)
    img = L.paste(img, strip.finish(scan=0.15), 430, 50)
    grid = L.sticker_word(["GRID VIEW"], 40, fills=[(232, 230, 238)], seed=64, extrude=4)
    img = L.place_sticker(img, grid, 1710, 900, angle=2)
    sq = L.sticker_word(["SAVE & QUIT"], 34, fills=[(232, 230, 238)], seed=65, extrude=4)
    img = L.place_sticker(img, sq, 1710, 990, angle=-1.5)
    img = L.bloom(img, 0.18, 0.8, 8)
    L.save(img, "netrun_map.png")


if __name__ == "__main__":
    main()
