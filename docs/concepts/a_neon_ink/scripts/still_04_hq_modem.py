"""04 - the Modem cyber shop, with the vertical MODEM / CYBER SHOP neon sign redrawn
in ink, glass shop UI, zine stickers and marker on the glass.
blender -b --factory-startup --python still_04_hq_modem.py -- <out.png>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ni_lib import *
from ni_parts import *
from ni_city_scene import *


def tube_letters(pl, text, x, y, h, color, hand, vertical=False, gap=1.18, core_w=None, w=22):
    """Neon tube lettering: a hollow double-line tube (body, dark core, hot filament)."""
    cx, cy = x, y
    for ch in text:
        st, adv = marker_word_strokes(ch, cx, cy, h, slant=0.0, hand=hand, jit=0.0, kern=0.0)
        for _, s in st:
            s2 = catmull(s, 6)
            ink(pl, "tube_halo", s2, color, w * 3.2, 0.10, None, 0, taper=0)
            ink(pl, "tube", s2, color, w, 1, hand, 0.25, taper=0.95)
            ink(pl, "tube", s2, "#16040E", w * 0.55, 1, None, 0, taper=0.95)
            ink(pl, "tube", s2, mix_hex(color, "#FFFFFF", 0.55), max(1.6, w * 0.12), 0.9, None, 0, taper=0.9)
        if vertical:
            cy += h * gap
        else:
            cx = adv + h * 0.05


def circuit(pl, x0, y0, x1, y1, hand, color, n=26, seed=3):
    r = random.Random(seed)
    for i in range(n):
        x = r.uniform(x0, x1); y = r.uniform(y0, y1)
        pts = [(x, y)]
        for k in range(r.randint(2, 4)):
            px, py = pts[-1]
            if k % 2 == 0:
                L = r.uniform(20, 70) * r.choice([-1, 1]); pts.append((min(max(px + L, x0), x1), py))
            else:
                L = r.uniform(12, 40); d = r.choice([-1, 1]); pts.append((px + L * d, py + L))
        ink(pl, "trace", pts, color, 1.6, 0.8, hand, 0.2, taper=1.0)
        ex, ey = pts[-1]
        ink(pl, "trace", ellipse(ex, ey, 4.5, 4.5, 10), color, 1.6, 0.9, None, 0, closed=True)
        fill_poly(pl, "trace", ellipse(x, y, 2.6, 2.6, 8), color, 0.9)


def chip_icon(pl, x, y, s, color, hand):
    fill_poly(pl, "ink", rect(x - s, y - s, 2 * s, 2 * s), "#0A1424", 1)
    ink(pl, "ink", rect(x - s, y - s, 2 * s, 2 * s), color, 2.2, 1, hand, .3, closed=True)
    ink(pl, "ink", rect(x - s * .45, y - s * .45, s * .9, s * .9), color, 1.4, 1, hand, .3, closed=True)
    for i in range(5):
        t = -s + (i + .5) * 2 * s / 5
        for (a, b) in (((x + t, y - s), (x + t, y - s - 10)), ((x + t, y + s), (x + t, y + s + 10)),
                       ((x - s, y + t), (x - s - 10, y + t)), ((x + s, y + t), (x + s + 10, y + t))):
            ink(pl, "ink", [a, b], color, 1.4, 0.9, None, 0)


def buy_chip(pl, x, y, label, hand, accent="acid", w=150):
    fill_poly(pl, "panel", rect(x, y, w, 40), "#0A1A10" if accent == "acid" else "#1A0A14", 0.95)
    ink(pl, "ink", rect(x, y, w, 40), accent, 1.8, 1, hand, .4, closed=True)
    pl.text(label, x + w / 2, y + 28, 20, accent, FONT_MONO, align="CENTER")


def slice_item(pl, x, y, kind, val, hand):
    c = SLICE[kind]
    pts = [(x - 60, y - 30), (x + 60, y - 30), (x + 44, y + 44), (x - 44, y + 44)]
    arc = [(x - 60 + 120 * t, y - 30 - 14 * math.sin(math.pi * t)) for t in [i / 12 for i in range(13)]]
    shape = arc + [(x + 44, y + 44), (x - 44, y + 44)]
    # depth: an offset back copy (thickness) + the lit face
    fill_poly(pl, "ink", [(px + 6, py + 8) for px, py in shape], "#05070C", 1)
    fill_poly(pl, "ink", shape, c, 0.3)
    ink(pl, "ink", shape, c, 2.6, 1, hand, .4, closed=True)
    ink(pl, "ink", [(px + 6, py + 8) for px, py in shape[len(arc) - 1:len(arc) + 1]], c, 1, 0.6, None, 0)
    glyph(pl, "ink", kind, x, y + 2, 30, "#FFFFFF", hand, 2.6)
    pl.text(str(val), x, y + 36, 22, "#FFFFFF", FONT_ANTON, align="CENTER")


def zine_sticker_hex(pl, x, y, r, hand, rot=0.2):
    hexp = [(x + r * math.cos(rot + i * math.pi / 3), y + r * math.sin(rot + i * math.pi / 3)) for i in range(6)]
    hexb = [(x + (r + 8) * math.cos(rot + i * math.pi / 3), y + (r + 8) * math.sin(rot + i * math.pi / 3)) for i in range(6)]
    fill_poly(pl, "shadow", [(px + 6, py + 8) for px, py in hexb], "#000000", 0.5)
    fill_poly(pl, "paper", hexb, "#FBFAF6", 1)
    fill_poly(pl, "paper", hexp, "pink", 1)
    ink(pl, "art", hexp, "ink", 2.4, 1, hand, .5, closed=True)
    # raised fist, inked (original motif)
    ink(pl, "art", [(x - 16, y + 30), (x - 18, y - 2), (x - 22, y - 16), (x - 8, y - 26), (x + 16, y - 24), (x + 20, y - 6), (x + 14, y + 30)], "ink", 3, 1, hand, .5, smooth=True)
    for i in range(3):
        ink(pl, "art", [(x - 12 + i * 10, y - 24), (x - 11 + i * 10, y - 12)], "ink", 1.6, 1, hand, .3)


def zine_sticker_eye(pl, x, y, r, hand):
    fill_poly(pl, "shadow", ellipse(x + 6, y + 8, r + 8, r + 8, 30), "#000000", 0.5)
    fill_poly(pl, "paper", ellipse(x, y, r + 8, r + 8, 30), "#FBFAF6", 1)
    fill_poly(pl, "paper", ellipse(x, y, r, r, 30), "note_yellow", 1)
    ink(pl, "art", ellipse(x, y, r * .7, r * .38, 24), "ink", 3, 1, hand, .5, closed=True)
    fill_poly(pl, "art", ellipse(x, y, r * .2, r * .2, 12), "ink", 1)
    ink(pl, "art", [(x - r * .75, y + r * .75), (x + r * .75, y - r * .75)], "harm", 6, 1, hand, .4)
    ink(pl, "art", ellipse(x, y, r, r, 30), "ink", 2, 1, hand, .5, closed=True)


def zine_strip(pl, x, y, w, h, rot, text, hand, bg="acid"):
    cx, cy = x + w / 2, y + h / 2
    T = lambda pts: rot_pts(pts, cx, cy, rot)
    fill_poly(pl, "shadow", T([(px + 6, py + 8) for px, py in rect(x - 6, y - 6, w + 12, h + 12)]), "#000000", 0.5)
    fill_poly(pl, "paper", T(rect(x - 6, y - 6, w + 12, h + 12)), "#FBFAF6", 1)
    fill_poly(pl, "paper", T(rect(x, y, w, h)), bg, 1)
    ink(pl, "art", T(rect(x, y, w, h)), "ink", 2, 1, hand, .4, closed=True)
    tx, ty = T([(cx, cy + h * 0.28)])[0]
    pl.text(text, tx, ty, h * 0.62, "ink", FONT_ANTON, align="CENTER", rot=-rot)


def main():
    sc = reset_scene(16)
    hand = Hand(404)
    city, cplanes, pal = make_city(31, "night", bands=[(99999, 5.0)], detail=0.7, u=30, ox=1100, oy=300, hq=None,
                                   prefix="bgcity", fade_far=False)
    scrim = Plane("scrim", ("s",), blur=0)
    fill_poly(scrim, "s", rect(-10, -10, W + 20, H + 20), "#02030A", 0.55)
    # ---- the sign (left): frame, circuit, MODEM tubes, CYBER SHOP tubes
    sign = Plane("sign", ("mount", "trace", "tube_halo", "tube", "frame"), blur=0)
    spill = Plane("spill", ("add",), blur=60, blend={"add": "ADD"})
    sx, sy, sw, sh = 44, 78, 470, 960
    fill_poly(sign, "mount", rect(sx, sy, sw, sh), "#07030A", 0.92)
    # brackets + bolts (it is hardware, hung off the wall)
    for yy in (sy + 120, sy + sh - 160):
        fill_poly(sign, "mount", rect(sx + sw - 6, yy, 70, 22), "#1B1D21", 1)
        ink(sign, "mount", rect(sx + sw - 6, yy, 70, 22), "#5A606A", 1.4, 1, hand, .3, closed=True)
    # rounded neon frame (double tube)
    rr = 44
    def rrect(x, y, w, h, r):
        pts = []
        for (cx, cy, a0) in ((x + w - r, y + r, -math.pi / 2), (x + w - r, y + h - r, 0), (x + r, y + h - r, math.pi / 2), (x + r, y + r, math.pi)):
            pts += [(cx + r * math.cos(a0 + math.pi / 2 * i / 8), cy + r * math.sin(a0 + math.pi / 2 * i / 8)) for i in range(9)]
        return pts
    for inset, wv in ((10, 9), (26, 4)):
        p = rrect(sx + inset, sy + inset, sw - 2 * inset, sh - 2 * inset, rr - inset * 0.5)
        ink(sign, "tube_halo", p, "pink", wv * 4, 0.10, None, 0, closed=True)
        ink(sign, "frame", p, "pink", wv, 1, hand, 0.4, closed=True)
        ink(sign, "frame", p, "#FFD0EA", max(1.2, wv * 0.25), 0.9, None, 0, closed=True)
    circuit(sign, sx + 40, sy + 50, sx + sw - 40, sy + 640, hand, "#C0307A", n=34, seed=5)
    # MODEM, vertical, big hollow tubes
    tube_letters(sign, "MODEM", sx + sw / 2 - 44, sy + 160, 100, "pink", Hand(12), vertical=True, gap=1.2, w=22)
    # CYBER SHOP in cyan
    tube_letters(sign, "CYBER", sx + 70, sy + 800, 62, "cyan", Hand(13), w=12)
    tube_letters(sign, "SHOP", sx + 110, sy + 900, 62, "cyan", Hand(14), w=12)
    # pink spill from the sign onto the wall and the nearest glass panel (feedback 10)
    fill_poly(spill, "add", ellipse(sx + sw / 2, sy + sh / 2, 380, 560, 40), "pink", 0.22)
    fill_poly(spill, "add", ellipse(sx + sw / 2 + 120, sy + 880, 260, 160, 40), "cyan", 0.14)
    # hanging cables from the sign
    for i in range(3):
        a = (sx + 60 + i * 150, sy + sh - 4)
        pts = [(a[0] + 40 * t + 20 * math.sin(t * 3 + i), a[1] + 120 * t * t) for t in [j / 16 for j in range(17)]]
        ink(sign, "mount", pts, "pink" if i != 1 else "#2A2F3A", 2.4, 0.8, hand, 0.4)
    # ---- glass shop UI
    ui = Plane("ui", ("panel", "scan", "ink"), blur=0)
    fill_poly(ui, "panel", rect(0, 0, W, 50), "#040A16", 0.92)
    ink(ui, "panel", [(0, 50), (W, 50)], "cyan", 1.2, 0.7, hand, .3)
    ui.text("05  MODEM // CYBER SHOP", 560, 33, 16, "#F2F6FF", FONT_MONO)
    for i, (lab, val, c) in enumerate((("HEAT", "34", "amber"), ("HP", "60/60", "gain"), ("CYCLES", "120", "#F2F6FF"), ("CARDS", "10", "cyan"))):
        x = 1060 + i * 205
        ui.text(lab, x, 33, 15, "#7A889C", FONT_MONO)
        ui.text(val, x + 80, 34, 22, c, FONT_ANTON)
    PAN = {"MICROCHIPS": (600, 84, 620, 360), "CARDS": (1250, 84, 640, 360), "SLICES": (600, 474, 620, 320),
           "REMOVE A CARD": (1250, 474, 640, 320)}
    for t, (x, y, w, h) in PAN.items():
        glass_panel(ui, x, y, w, h, t, hand, accent="pink")
    # sign light on the MICROCHIPS / SLICES panels' left edges
    for (x, y, w, h) in (PAN["MICROCHIPS"], PAN["SLICES"]):
        for i in range(8):
            fill_poly(ui, "panel", rect(x + i * 10, y, 10, h), "pink", 0.08 * (8 - i) / 8)
    # microchips
    for i, (nm, d1, d2, price) in enumerate((("BARBED WIRE", "DEF slice also deals", "2 dmg to the pointer.", "141"),
                                             ("SHUNT", "Resolves the neighbour", "on the side you land.", "129"))):
        x = 620 + i * 300; y = 150
        chip_icon(ui, x + 60, y + 70, 36, "cyan" if i == 0 else "violet", Hand(50 + i))
        ui.text(nm, x + 120, y + 60, 22, "#F2F6FF", FONT_MONO)
        ui.text(d1, x + 120, y + 88, 15, "#AFC0D6", FONT_MONO)
        ui.text(d2, x + 120, y + 108, 15, "#AFC0D6", FONT_MONO)
        buy_chip(ui, x + 120, y + 150, "BUY " + price, Hand(60 + i))
    # slices
    for i, (k, v) in enumerate((("def", 5), ("atk", 10), ("evd", 2))):
        x = 700 + i * 200; y = 600
        slice_item(ui, x, y, k, v, Hand(70 + i))
        buy_chip(ui, x - 70, y + 84, "BUY 100", Hand(80 + i), w=140)
    # remove a card: shredder + mini spinner
    rx, ry = 1300, 560
    fill_poly(ui, "ink", rect(rx, ry + 40, 150, 40), "#0A1424", 1)
    ink(ui, "ink", rect(rx, ry + 40, 150, 40), "acid", 2, 1, hand, .4, closed=True)
    for i in range(9):
        ink(ui, "ink", [(rx + 10 + i * 16, ry + 84), (rx + 12 + i * 16, ry + 130)], "#AFC0D6", 1.6, 0.8, hand, .4)
    buy_chip(ui, rx, ry + 150, "SHRED 50", hand, accent="harm", w=150)
    minispin = Plane("minispin", ("shadow", "spill", "body", "line", "slice", "glyph", "hub", "needle", "sheen"), blur=0)
    spinner(minispin, minispin, 1720, 640, 92, [("atk", 8), ("crit", 6), ("miss", 6), ("def", 10)], "op", Hand(88), needle=0.9,
            hp=(60, 60), accent="pink")
    ui.text("SOCKET INTO SLOT 1: CRIT 12", 620, 420, 16, "#AFC0D6", FONT_MONO)
    # JACK OUT button: washed DISCONNECT under the marker
    bx, by, bw, bh = 1250, 830, 640, 190
    fill_poly(ui, "panel", rect(bx, by, bw, bh), "#050D1C", 0.92)
    ink(ui, "panel", rect(bx, by, bw, bh), "cyan", 1.2, 0.5, hand, .4, closed=True)
    ui.text("DISCONNECT", bx + bw / 2, by + 118, 64, "#2C5566", FONT_MONO, align="CENTER")
    for yy in range(by + 6, by + bh, 4):
        ink(ui, "scan", [(bx + 4, yy), (bx + bw - 4, yy)], "#050D1C", 1.4, 0.55, None, 0, taper=0)
    # ---- stickers: cards for sale + zine stickers on the glass (no glow)
    stick = Plane("stickers", ("shadow", "paper", "art", "tape"), glow=False)
    for i, (t, c, colr, art, pr) in enumerate((("MIRROR FLIP", 3, "paper2", "spin", "69"), ("ENCRYPT", 1, "cyan", "shield", "61"),
                                              ("TAP TAP", 2, "note_pink", "bolt", "75"))):
        x = 1290 + i * 200
        sticker_card(stick, x, 150, 150, 206, [-0.05, 0.03, 0.07][i], t, c, colr, Hand(90 + i), art=art)
        buy_chip(ui, x + 6, 380, "BUY " + pr, Hand(95 + i), w=138)
    zine_sticker_hex(stick, 1225, 470, 52, Hand(101), rot=0.3)
    zine_sticker_eye(stick, 575, 810, 50, Hand(102))
    zine_strip(stick, 820, 850, 250, 56, -0.08, "NO REFUNDS", Hand(103), bg="acid")
    zine_strip(stick, 900, 930, 300, 50, 0.05, "SHRED YOUR PAST", Hand(104), bg="note_pink")
    # ---- marker on the glass (no glow): JACK OUT over DISCONNECT, a circle + note
    mk = Plane("marker", ("ink",), glow=False)
    mh = Hand(105)
    st, _ = marker_word_strokes("JACK OUT", bx + 40, by + 132, 90, slant=0.2, hand=Hand(106))
    for _, s in st:
        ink(mk, "ink", s, "pink", 18, 1, mh, 0.5, smooth=True, w_profile=marker_profile)
    for (dx, L) in ((60, 64), (205, 40), (380, 86), (520, 30)):
        drip(mk, "ink", bx + dx, by + 132, L, 9, "pink", hand=mh)
    # circle the card you want
    ink(mk, "ink", ellipse(1567, 262, 118, 150, 40, -0.4, 2 * math.pi + 0.2, 0.08), "pink", 7, 1, mh, 2.0, taper=0.2)
    st, _ = marker_word_strokes("THIS ONE!", 1460, 470, 34, slant=0.15, hand=Hand(107))
    for _, s in st:
        ink(mk, "ink", s, "pink", 7, 1, mh, 0.4, smooth=True, w_profile=marker_profile)
    planes = cplanes + [scrim, spill, sign, ui, minispin, stick, mk]
    render(sc, planes, out_path("04_hq_modem.png"), bloom=(0.22, 0.8, 0.82))


main()
