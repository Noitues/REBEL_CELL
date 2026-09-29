"""03 - the same city at HUNTED Heat: helicopters, searchlights, drones, heat glitch.
blender -b --factory-startup --python still_03_heat.py -- <out.png>
Then: python post_03_glitch.py <out.png>  (tear bands; the chroma split is in the compositor)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ni_lib import *
from ni_parts import *
from ni_city_scene import *
import still_02_city_night as s02

s02.NODES.update({"T3": (-4.5, 15.5)})
s02.LINKS.extend([("T3", "HQ", "threat"), ("T2", "C2", "threat")])


def helicopter(pl, x, y, s, hand, ang=0.0):
    body = rot_pts(ellipse(x, y, 34 * s, 15 * s, 24), x, y, ang)
    fill_poly(pl, "air", body, "#0A0A12", 1.0)
    ink(pl, "air", body, "#E8EEFF", 2.4, 1, hand, 0.4, closed=True)
    tail = rot_pts([(x + 30 * s, y - 2 * s), (x + 86 * s, y - 10 * s)], x, y, ang)
    ink(pl, "air", tail, "#E8EEFF", 3.0, 1, hand, 0.3, taper=0.5)
    fin = rot_pts([(x + 82 * s, y - 10 * s), (x + 90 * s, y - 26 * s)], x, y, ang)
    ink(pl, "air", fin, "#E8EEFF", 2.0, 1, hand, 0.3)
    # canopy
    ink(pl, "air", rot_pts(ellipse(x - 16 * s, y - 2 * s, 12 * s, 8 * s, 14, math.pi, 2 * math.pi), x, y, ang), "cyan", 1.6, 1, hand, .2)
    # skids
    for dy in (16, 20):
        ink(pl, "air", rot_pts([(x - 30 * s, y + dy * s), (x + 22 * s, y + dy * s)], x, y, ang), "#E8EEFF", 1.2, 0.8, hand, .2)
    # rotor disc: motion-blurred hairline arcs
    for k in range(6):
        rr = 90 * s * (0.8 + 0.04 * k)
        a0 = hand.r.uniform(0, 6.28)
        ink(pl, "rotor", ellipse(x, y - 22 * s, rr, rr * 0.28, 30, a0, a0 + 2.2), "#E8EEFF", 0.9, 0.35, None, 0)
    ink(pl, "rotor", ellipse(x, y - 22 * s, 92 * s, 26 * s, 48), "#E8EEFF", 0.6, 0.18, None, 0, closed=True)
    # nav + siren lights
    fill_poly(pl, "air", ellipse(*rot_pts([(x - 10 * s, y - 16 * s)], x, y, ang)[0], 5, 5, 10), "police_red", 1)
    fill_poly(pl, "air", ellipse(*rot_pts([(x + 6 * s, y - 16 * s)], x, y, ang)[0], 5, 5, 10), "police_blue", 1)
    return rot_pts([(x - 24 * s, y + 8 * s)], x, y, ang)[0]


def drone(pl, x, y, s, hand):
    for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        ink(pl, "air", [(x, y), (x + dx * 14 * s, y + dy * 7 * s)], "#C8D0E0", 1.6, 1, hand, .1)
        ink(pl, "air", ellipse(x + dx * 14 * s, y + dy * 7 * s, 8 * s, 3 * s, 12), "#C8D0E0", 1.0, 0.7, None, 0, closed=True)
    fill_poly(pl, "air", ellipse(x, y, 6 * s, 4 * s, 10), "#0A0A12", 1)
    fill_poly(pl, "air", ellipse(x, y + 1, 2.6 * s, 2.6 * s, 8), "police_red", 1)


def add_heat(sc, city, order, hand):
    P = city.P
    search = Plane("search", ("cone", "pool"), blur=5, blend={"cone": "ADD", "pool": "ADD"})
    air = Plane("air", ("rotor", "air"), blur=0)
    flick = Plane("flicker", ("wash",), blur=26, blend={"wash": "ADD"})
    helis = [(1300, 250, 1.7, 0.12, (1110, 690)), (400, 330, 1.45, -0.1, (660, 900)), (1700, 560, 1.25, 0.2, (1560, 890))]
    for (x, y, s, a, pool) in helis:
        src = helicopter(air, x, y, s, hand, a)
        px, py = pool
        rx, ry = 150, 74
        fill_poly(search, "cone", [src, (px - rx, py), (px + rx, py)], "#DDE8FF", 0.16)
        fill_poly(search, "cone", [src, (px - rx * .5, py), (px + rx * .5, py)], "#DDE8FF", 0.08)
        fill_poly(search, "pool", ellipse(px, py, rx, ry, 40), "#DDE8FF", 0.30)
        fill_poly(search, "pool", ellipse(px, py, rx * .6, ry * .6, 40), "#FFFFFF", 0.22)
        ink(search, "pool", ellipse(px, py, rx, ry, 40), "#FFFFFF", 1.4, 0.5, hand, 0.8, closed=True)
    r = random.Random(33)
    for i in range(16):
        x, y = r.uniform(150, 1800), r.uniform(160, 900)
        drone(air, x, y, r.uniform(0.8, 1.2), hand)
        # scanning fan (thin red, additive)
        fill_poly(search, "cone", [(x, y + 4), (x - 30, y + 110), (x + 30, y + 110)], "police_red", 0.07)
        ink(search, "cone", [(x - 30, y + 110), (x + 30, y + 110)], "police_red", 1.2, 0.6, None, 0)
    # red/blue rim flicker on corp buildings (<=1 Hz in game; frozen here mid-alternation)
    for i in range(14):
        x, y = r.uniform(900, 1900), r.uniform(150, 900)
        fill_poly(flick, "wash", ellipse(x, y, r.uniform(60, 140), r.uniform(40, 90), 24),
                  "police_red" if i % 2 else "police_blue", 0.22)
    # HUD: Heat banner (glass) + incursion warning
    ui = Plane("ui_heat", ("panel", "scan", "ink"), blur=0)
    glass_panel(ui, W - 520, 24, 492, 118, "HEAT // HUNTED", hand, accent="harm")
    fill_poly(ui, "ink", rect(W - 500, 96, 452, 14), "#2A0A0E", 1)
    fill_poly(ui, "ink", rect(W - 500, 96, 452 * 0.82, 14), "harm", 1)
    for i in range(1, 4):
        ink(ui, "ink", [(W - 500 + 452 * i / 4, 92), (W - 500 + 452 * i / 4, 114)], "#FFFFFF", 1, 0.6, None, 0)
    ui.text("82", W - 44, 80, 46, "harm", FONT_ANTON, align="RIGHT")
    ui.text("INCURSION ROUTE -> HQ   ETA 2 TURNS", W - 500, 134, 16, "#FFB3A8", FONT_MONO)
    order = order[:-1] + [flick, search, air, order[-1], ui]
    return order


if __name__ == "__main__":
    sc, order = s02.build("heat", extra=add_heat)
    render(sc, order, out_path("03_heat.png"), bloom=(0.2, 0.75, 0.8), chroma=1.5)
