"""Round 34 -> route_d_city.png: hybrid D, the city-view plan. On the locked city map (round 30 v6), the run starts
from a node the Cell owns (Relay 4, a lime raid node). From there the Sites open outward toward Meridian HQ:
  * the Cell's nodes and walked links       = lime (the raid nodes, unchanged);
  * reachable now (a finite set, 3 Sites)   = bright pads in the corp colour, numbered;
  * not reachable yet but PLANNABLE         = dimmed grey pads and links: visible, intel-dim, the pencil can plan through them;
  * the plan                                = yellow grease pencil: solid to the next run, dashed what-ifs on to the HQ;
  * the HQ's guardian                       = red pencil.
Nodes sit on the map's own iso street lattice; links follow its streets (Manhattan along the two iso axes).

python route_d_city.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw

import r31lib as L
import r32ui as U
import sticker_lib19 as SL

CITY = os.path.join(L.CONCEPTS, "round30_meridian_castle", "city_night_hq_v6.jpg")
CROP = (820, 330, 2340, 1185)
O, S = (430, 960), 96


def iso(i, j):
    return (O[0] + S * (i - j), O[1] - S * 0.5 * (i + j))


# key: (lattice i, j, state, label, kind)   state: cell | start | reach | plan | hq
NODES = {
    "home": (1, -1, "cell", "HOME SERVER", "home"),
    "fw": (0, -1, "cell", "FIREWALL RELAY", "fw"),
    "proxy": (2, 0, "cell", "PROXY 2", "relay"),
    "relay4": (3, 1, "start", "RELAY 4", "relay"),
    "depot15": (5, 1, "reach", "T1  DEPOT 15", "site"),
    "yard9": (4, 3, "reach", "T1  YARD 9", "site"),
    "scrub": (4, 0, "reach", "HEAT  SCRUB RECORDS", "site"),
    "cust22": (7, 2, "plan", "T2  CUSTOMS 22", "site"),
    "port31": (5, 4, "plan", "T2  PORT 31", "site"),
   "lane15": (9, 3, "plan", "T3  LANE 15", "site"),
    "tariff40": (7, 5, "plan", "T3  TARIFF 40", "site"),
    "hq": (11.2, 2.6, "hq", "MERIDIAN HQ", "hq"),
}
# (a, b, kind)  kind: cell (lime, walked/owned) | open (reachable now) | plan (not yet open) | locked (a cross-link)
LINKS = [
    ("home", "fw", "cell"), ("home", "proxy", "cell"), ("proxy", "relay4", "cell"),
    ("relay4", "depot15", "open"), ("relay4", "yard9", "open"), ("relay4", "scrub", "open"),
    ("depot15", "cust22", "plan"), ("yard9", "port31", "plan"),
    ("cust22", "lane15", "plan"), ("port31", "tariff40", "plan"),
    ("lane15", "hq", "plan"), ("tariff40", "hq", "plan"),
    ("cust22", "port31", "locked"),
]
PLAN = ["relay4", "depot15", "cust22", "lane15", "hq"]


def pos(k):
    i, j = NODES[k][0], NODES[k][1]
    return iso(i, j)


def street_path(a, b):
    """Along the map's streets: first the i axis, then the j axis (an iso L with a short chamfer)."""
    ia, ja = NODES[a][0], NODES[a][1]
    ib, jb = NODES[b][0], NODES[b][1]
    p0, pc, p1 = iso(ia, ja), iso(ib, ja), iso(ib, jb)
    if abs(ia - ib) < 1e-6 or abs(ja - jb) < 1e-6:
        return [p0, p1]
    return [p0, pc, p1]


def diamond(x, y, r):
    return [(x, y - r * 0.5), (x + r, y), (x, y + r * 0.5), (x - r, y)]


def cell_icon(kind, px, col):
    """The Cell's raid-node pictograms (round 21 key): relay = up arrows, firewall = wall, home = heart."""
    im = Image.new("RGBA", (px * 2, px * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    P = px * 2
    if kind == "relay":
        for k in (-1, 0, 1):
            x = P / 2 + k * P * 0.22
            d.line([(x, P * 0.78), (x, P * 0.3)], fill=col + (255,), width=P // 12)
            d.line([(x - P * 0.1, P * 0.42), (x, P * 0.28), (x + P * 0.1, P * 0.42)], fill=col + (255,), width=P // 12)
    elif kind == "fw":
        for r in range(3):
            for c in range(3 - r % 2):
                x0 = P * 0.18 + c * P * 0.22 + (P * 0.11 if r % 2 else 0)
                y0 = P * 0.66 - r * P * 0.18
                d.rectangle([x0, y0, x0 + P * 0.19, y0 + P * 0.15], fill=col + (255,))
    else:
        d.ellipse([P * 0.2, P * 0.25, P * 0.52, P * 0.55], fill=col + (255,))
        d.ellipse([P * 0.48, P * 0.25, P * 0.8, P * 0.55], fill=col + (255,))
        d.polygon([(P * 0.22, P * 0.45), (P * 0.78, P * 0.45), (P * 0.5, P * 0.8)], fill=col + (255,))
    return im.resize((px, px), Image.LANCZOS)


def tier_pips(img, x, y, n, col):
    d = ImageDraw.Draw(img)
    for k in range(n):
        xx = x - (n - 1) * 7 + k * 14
        d.rectangle([xx - 4, y - 4, xx + 4, y + 4], fill=col + (255,), outline=(10, 10, 14, 255))
    return img


def city_layer(base, plan=True, labels=True, numbers=True):
    img = base.copy()
    inl = U.Inlay()
    # the Cell's link coming in from the home district edge
    for a, b, kind in LINKS:
        pts = street_path(a, b)
        if kind == "cell":
            inl.trace(pts, U.LIME, width=2.8, lanes=3, gap=5, glow=1.0)
        elif kind == "open":
            inl.trace(pts, U.MER, width=2.6, lanes=3, gap=5, glow=0.9)
        elif kind == "plan":
            inl.trace(pts, (176, 172, 196), width=2.2, lanes=2, gap=5, glow=0.15, alpha=0.85)
    img = inl.lay(img)
    d = ImageDraw.Draw(img)
    # locked cross-link: grey dashes (opens with an Intel Exploit or an objective)
    for a, b, kind in LINKS:
        if kind != "locked":
            continue
        pts = street_path(a, b)
        dash = U.cut_poly
        tot = U.polyline_len(pts)
        s = 0
        while s < tot:
            seg = dash(pts, s / tot, min(1, (s + 10) / tot))
            if len(seg) > 1:
                d.line(seg, fill=(150, 146, 168, 170), width=3)
            s += 18
        mx, my = U.point_at(pts, 0.5)
        img = U.chip(img, (mx, my - 18), "LOCKED", (150, 146, 168), 12)
    # pads
    for k, (i, j, st, label, kind) in sorted(NODES.items(), key=lambda kv: iso(kv[1][0], kv[1][1])[1]):
        x, y = iso(i, j)
        if st in ("cell", "start"):
            r = 40 if st == "start" else 32
            img = U.pad(img, diamond(x, y, r), U.LIME, lit=1.0, glow=1.0 if st == "start" else 0.7)
            ic = cell_icon(kind, 26 if st == "start" else 22, U.LIME)
            img.alpha_composite(ic, (int(x - ic.width / 2), int(y - ic.height / 2)))
        elif st == "reach":
            img = U.pad(img, diamond(x, y, 34), U.MER, lit=1.0, glow=0.9)
            img = tier_pips(img, x, y, 1 if label.startswith("T1") else 0, U.MER)
        elif st == "plan":
            img = U.pad(img, diamond(x, y, 30), (176, 172, 196), lit=0.75, glow=0.15, fill_a=200)
            img = tier_pips(img, x, y, int(label[1]), (120, 116, 136))
        elif st == "hq":
            pass
    # the HQ: a big corp-colour socket ring round the castle (the boss Site), not reachable yet
    hx, hy = pos("hq")
    img = U.pad(img, diamond(hx, hy + 30, 150), (180, 120, 70), lit=0.45, glow=0.25, fill_a=0)
    # labels: terminal chips (live state), dim for plannable
    if labels:
        for k, (i, j, st, label, kind) in NODES.items():
            x, y = iso(i, j)
            if st == "hq":
                continue
            col = {"cell": U.LIME, "start": U.LIME, "reach": U.MER, "plan": (150, 146, 168)}[st]
            img = U.chip(img, (x, y + 36) if st not in ("start", "cell") else (x - 100, y), label, col, 14 if st != "plan" else 13,
                         fill_a=230 if st != "plan" else 150, bright=(st == "start"))
    # reachable now: a finite set, numbered on the Cell's terminal chips
    if numbers:
        reach = [k for k in NODES if NODES[k][2] == "reach"]
        reach.sort(key=lambda k: pos(k)[0])
        for n, k in enumerate(reach):
            x, y = pos(k)
            img = U.chip(img, (x - 46, y - 26), str(n + 1), U.MER, 18, bright=True)
    if plan:
        p = L.pen(L.GP_YELLOW, seed=341)
        # the next run: solid along the open link; later runs: dashed what-ifs through the greyed Sites
        first = street_path(PLAN[0], PLAN[1])
        p.stroke(SL.catmull(p.wobble(U.offset_poly(first, -14), 1.0), 10), width=9)
        U.arrow_head(p, U.offset_poly(first, -14)[-2:], width=8, head=20)
        for a, b in zip(PLAN[1:-1], PLAN[2:]):
            U.dashed_along(p, street_path(a, b), offset=-14, t0=0.14, t1=0.74, width=8)
        sx, sy = pos("relay4")
        p.circle(sx, sy, 66, 40, width=9)
        for n, k in enumerate(PLAN[1:-1]):
            x, y = pos(k)
            p.text("RUN %d" % (n + 1), x - 4, y - 56, 26, angle=-8)
        img = L.ink(img, p)
        pr = L.pen(L.GP_RED, seed=342)
        pr.circle(hx, hy + 6, 170, 110, width=10)
        pr.text("THE MANIFEST", hx + 120, hy + 150, 34, angle=-6)
        img = L.ink(img, pr)
    return img


def base_map():
    im = Image.open(CITY).convert("RGB").crop(CROP).resize((1920, 1080), Image.LANCZOS).convert("RGBA")
    # the city dims a step so the network reads (the city map HUD's own treatment)
    lay = Image.new("RGBA", im.size, (8, 6, 14, 92))
    return Image.alpha_composite(im, lay)


def hud(img):
    img = L.darken_rect(img, (-200, -200, 440, 1300), a=150, blur=50)
    img = L.darken_rect(img, (1500, -200, 2200, 1300), a=150, blur=50)
    img = L.place_sticker(img, L.sticker_word(["THE GRID"], 62, fills=["yellow"], seed=31), 180, 62, angle=-3)
    strip = L.CRT(1000, 44, U.CYAN, None, header=False, seed=343)
    strip.text((16, 12), "CAMPAIGN 03  //  MERIDIAN FREIGHT  //  PLAN: RELAY 4 > MERIDIAN HQ", 19, U.CYAN)
    img = L.paste(img, strip.finish(scan=0.15), 440, 36)
    # PLAN: the pencilled runs, forecast on the Cell's terminal
    c = L.CRT(400, 330, L.YEL, "PLAN", tag="PENCIL, 4 RUNS", seed=344)
    rows = [("RUN 1", "T1  DEPOT 15", "+8", "reachable now", U.MER),
            ("RUN 2", "T2  CUSTOMS 22", "+10", "Exploit: Customs Keys", (190, 186, 200)),
            ("RUN 3", "T3  LANE 15", "+11", "opens the HQ link", (190, 186, 200)),
            ("BOSS", "MERIDIAN HQ", "", "the climb (THE KEEP)", (255, 120, 100))]
    y = 52
    for a, b, h, sub, col in rows:
        c.text((16, y), a, 16, L.YEL)
        c.text((100, y - 2), b, 20, col)
        c.text((384, y), ("HEAT " + h) if h else "", 15, L.HEAT, anchor="ra")
        c.text((100, y + 24), sub, 14, (160, 160, 150))
        y += 58
    c.rule(y - 4, dash=True)
    c.text((16, y + 6), "Heat 41 now  >  about 70 before the boss", 15, L.HEAT)
    img = L.paste(img, c.finish(), 24, 128)
    c = L.CRT(400, 250, U.CYAN, "MAP KEY", seed=345)
    keys = [(U.LIME, "the Cell's nodes + walked links"), (U.MER, "reachable now: 3 Sites, numbered"),
            ((150, 146, 168), "plannable: visible, not reachable yet"), ((150, 146, 168), "- - locked cross-link"),
            (L.GP_YELLOW, "pencil: your plan (solid = next run)"), (L.GP_RED, "pencil: the HQ's guardian")]
    y = 52
    for col, s in keys:
        c.d.polygon(diamond(30, y + 9, 13), fill=col + (255,))
        c.text((54, y), s, 15, (215, 225, 230))
        y += 31
    img = L.paste(img, c.finish(), 24, 474)
    c = L.CRT(400, 150, U.PINK, "RUNNER", tag="READY", seed=346)
    c.paste(L.glyph("slice_exploit", 40, fill=U.PINK, ow=3), 16, 54)
    c.text((72, 52), "CELL-9  BREAKER  R1", 19, (240, 240, 245))
    c.text((72, 80), "T1 access  //  HP 60 / 60", 16, (255, 140, 170))
    c.text((16, 116), "starts at RELAY 4 (your node)", 15, U.LIME)
    img = L.paste(img, c.finish(), 24, 740)
    img = U.term_button(img, (24, 906, 424, 976), "BACK TO HQ", "[ESC]")
    # right: the selected reachable Site (decrypted intel) + the run forecast
    hb = (1516, 128, 1898, 392)
    img = U.holo(img, hb, U.MER, "SITE 15  //  DEPOT 15", seed=347)
    img = U.meridian_seal(img, (1858, 166), 30)
    d = ImageDraw.Draw(img)
    rows = [("TIER", "T1  (opens CUSTOMS 22)"), ("GUARD", "PORT AUTHORITY"), ("RACK", "Schematics + armory"), ("LINK", "RELAY 4 > DEPOT 15"),
            ("LENGTH", "7 layers, ~15 min")]
    y = 204
    for a, b in rows:
        d.text((1534, y), a, font=L.f_mono(15), fill=(255, 200, 150, 255), anchor="lm")
        d.text((1620, y), b, font=L.f_ui(18, b"SemiBold"), fill=(255, 236, 214, 255), anchor="lm")
        y += 30
    img = U.chip(img, (1800, 372), "DECRYPTED // 7F-A2", U.LIME, 14)
    c = L.CRT(382, 250, U.CYAN, "IF CLEARED", tag="FORECAST", seed=348)
    for n, (a, b, col) in enumerate((("SCHEMATICS", "+9", (120, 255, 150)), ("HEAT", "+8  (41 > 49)", L.HEAT),
                                    ("OPENS", "T2 CUSTOMS 22", U.MER), ("LINK", "lime, raids too", U.LIME), ("RAID", "none (Heat < 50)", (160, 160, 150)))):
        c.text((16, 54 + n * 38), a, 16, (190, 200, 210))
        c.text((366, 54 + n * 38), b, 17, col, anchor="ra")
    img = L.paste(img, c.finish(), 1516, 410)
    img = L.place_sticker(img, L.sticker_word(["JACK IN"], 84, fills=["pink"], seed=8), 1708, 862, angle=-3)
    d = ImageDraw.Draw(img)
    d.text((1708, 960), "into the link: RELAY 4 > DEPOT 15", font=L.f_mono(15), fill=(220, 220, 230, 255), anchor="mm")
    return img


def main():
    img = city_layer(base_map())
    img = hud(img)
    img = L.bloom(img, 0.12, 0.82, 8)
    L.save(img, "route_d_city.png")


if __name__ == "__main__":
    main()
