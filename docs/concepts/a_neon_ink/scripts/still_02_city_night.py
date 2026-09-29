"""02 - the City Grid at night (NEON INK).
blender -b --factory-startup --python still_02_city_night.py -- <out.png>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ni_lib import *
from ni_parts import *
from ni_city_scene import *

MODE = "night"
NODES = {"HQ": (5.5, 15.5), "C2": (10.5, 10.5), "C1": (15.5, 5.5), "N1": (20.5, 0.5), "N2": (5.5, 0.5),
         "N3": (-4.5, 0.5), "T2": (10.5, -9.5), "T1": (5.5, -19.5), "N4": (-4.5, -9.5)}
LINKS = [("HQ", "C2", "claimed"), ("C2", "C1", "claimed"), ("C1", "N1", "open"), ("C2", "N2", "open"),
         ("N2", "N3", "open"), ("N2", "T2", "threat"), ("T2", "T1", "threat"), ("N3", "N4", "open")]


def build(mode=MODE, extra=None):
    sc = reset_scene(16)
    city, planes, pal = make_city(11, mode)
    hand = Hand(99)
    # light spill from the HQ + signs onto the street (additive)
    spill = Plane("spill", ("add",), blur=30, blend={"add": "ADD"})
    hqb = [b for b in city.buildings if b["kind"] == "hq"][0]
    bx, by = city.P(hqb["x"] + hqb["w"], hqb["y"] + hqb["d"])
    fill_poly(spill, "add", ellipse(bx - 40, by - 10, 260, 110, 40), "pink", 0.30)
    fill_poly(spill, "add", ellipse(bx - 60, by - 300, 140, 300, 40), "pink", 0.10)
    # holograms on tall buildings in the focus band
    holo_pl = Plane("holo", ("beam", "holo"), blur=0.6, blend={"beam": "ADD"})
    talls = sorted([b for b in city.buildings if b["kind"] == "bld" and b["h"] > 3.0 and 420 < city.depth_y(b) < 940
                    and 200 < city.P(b["x"], b["y"])[0] < W - 200], key=lambda b: -b["h"])
    used = []
    k = 0
    for b in talls:
        p = city.P(b["x"], b["y"], b["h"])
        if any(math.hypot(p[0] - q[0], p[1] - q[1]) < 330 for q in used) or abs(p[0] - bx) < 220:
            continue
        used.append(p)
        ca, cb = [("violet", "cyan"), ("pink", "white"), ("cyan", "white"), ("#7FA8FF", "acid")][k % 4]
        holo(city, holo_pl, b, 300 + k, w=130 + 20 * (k % 3), h=74, col_a=ca, col_b=cb, side="left" if k % 2 else "right",
             z_off=0.8 + 0.4 * (k % 3))
        k += 1
        if k >= 6:
            break
    fly = Plane("flyers", ("trail", "body"), blur=0.0)
    flyers(city, fly, 21, 22, mode)
    fogs = fog_planes(5, {"far": [(300, 120, 380, 80), (1500, 60, 420, 70), (900, 260, 300, 50)],
                          "mid": [(1300, 420, 260, 60), (380, 600, 240, 70)],
                          "near": [(120, 1020, 420, 140), (1720, 980, 380, 150), (1100, 1080, 300, 90)]},
                      color="#9AB8E0" if mode != "heat" else "#6A4A66")
    grid = Plane("grid", ("under", "link", "node"), blur=0.0)
    grid_overlay(city, grid, 8, mode=mode, nodes=NODES, links=LINKS)
    # tiny glass HUD (context only)
    ui = Plane("ui", ("panel", "scan", "ink"), blur=0)
    glass_panel(ui, 28, 24, 470, 104, "GRID // SPRAWL 04", hand)
    ui.text("23:47  NIGHT CYCLE   SITES 3/9", 44, 106, 18, "#AFC0D6", FONT_MONO)
    for i, (lab, c) in enumerate((("HQ", "pink"), ("CLAIMED", "acid"), ("OPEN", "cyan"), ("THREAT", "orange"))):
        x = 60 + i * 150; y = 1040
        fill_poly(ui, "panel", rect(x - 30, y - 22, 140, 32), "#050D1C", 0.8)
        ink(ui, "ink", ellipse(x - 12, y - 6, 9, 5, 16), c, 2.2, 1, hand, .2, closed=True)
        ui.text(lab, x + 4, y + 1, 16, "#CFF6FF", FONT_MONO)
    order = planes[:1] + [spill] + planes[1:4] + fogs[:1] + planes[4:5] + fogs[1:2] + [holo_pl] + planes[5:] + [fly, grid] + fogs[2:] + [ui]
    if extra:
        order = extra(sc, city, order, hand)
    return sc, order


if __name__ == "__main__":
    sc, order = build()
    render(sc, order, out_path("02_city_night.png"), bloom=(0.22, 0.65, 0.8))
