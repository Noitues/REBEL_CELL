"""city_map_hud.png: the campaign City Grid HUD over round 30's city_night_hq_v6.jpg.

Media: THE GRID title + JACK IN = stickers; resources, Heat, crew, map key, IF CLEARED, the raid alert
= terminal (the Cell's systems, live values); the selected Site's corp file = decrypted Halcyon holo;
the plan (circle + arrow) = yellow grease pencil; the forecast raid route = red dashed grease pencil
(dashed = what-if, per the locked path rules).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from PIL import Image, ImageChops, ImageDraw, ImageFilter  # noqa: E402

import sticker_lib31 as SL  # noqa: E402
import ui31 as U  # noqa: E402

W, H = 1920, 1080
SRC = os.path.join(U.CONC, 'round30_meridian_castle', 'city_night_hq_v6.jpg')
OUT = os.path.join(U.ROOT, 'city_map_hud.png')

HEAT = 58
BANDS = [(0, 25, 'COOL', U.CYAN), (25, 50, 'NOTICED', U.AMBER), (50, 75, 'FLAGGED', (255, 120, 40)),
         (75, 100, 'HUNTED', U.HARM)]


def base():
    import defist
    img = defist.night_v6().resize((W, H), Image.LANCZOS)
    a = np.asarray(img, np.float32)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    # keep the map bright in the middle, sink the HUD edges a little
    k = 0.92 - 0.30 * np.clip(1 - x / 430, 0, 1) - 0.30 * np.clip((x - 1480) / 440, 0, 1) \
        - 0.25 * np.clip(1 - y / 140, 0, 1) - 0.25 * np.clip((y - 900) / 180, 0, 1)
    a = a * np.clip(k, 0.45, 1)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA')


def diamond(img, c, col, r=18, fill_a=0.55, pips=0, ring=False, glow=0.8):
    x, y = c
    pts = [(x, y - r / 2), (x + r, y), (x, y + r / 2), (x - r, y)]
    m = Image.new('L', img.size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    img = U.add_glow(img, m, col, 10, glow)
    img = U.over(img, tuple(int(c_ * 0.35) for c_ in col), m, 0.9)
    inner = Image.new('L', img.size, 0)
    ImageDraw.Draw(inner).polygon([(x, y - r / 4), (x + r / 2, y), (x, y + r / 4), (x - r / 2, y)], fill=255)
    img = U.over(img, col, inner, fill_a)
    e = ImageChops.subtract(m, SL.erode(m, 2))
    img = U.over(img, col, e)
    d = U.BD(img)
    for k in range(pips):
        px = x - (pips - 1) * 7 + k * 14
        d.rectangle([px - 4, y + r / 2 + 6, px + 4, y + r / 2 + 12], fill=col + (255,), outline=(8, 8, 12, 255))
    if ring:
        d.ellipse([x - r - 10, y - r / 2 - 10, x + r + 10, y + r / 2 + 10], outline=col + (200,), width=2)
    return img


def link(img, a, b, col, w=3, k=0.9):
    m = Image.new('L', img.size, 0)
    ImageDraw.Draw(m).line([a, b], fill=255, width=w)
    img = U.add_glow(img, m, col, 6, 0.7)
    return U.over(img, col, m, k)


def dashed(pen, pts, width=6, dash=26, gap=16):
    path = SL.catmull(pen.wobble(pts, 1.2), 16)
    acc, on, seg = 0.0, True, [path[0]]
    for i in range(1, len(path)):
        a, b = path[i - 1], path[i]
        acc += math.hypot(b[0] - a[0], b[1] - a[1])
        seg.append(b)
        if acc >= (dash if on else gap):
            if on and len(seg) > 1:
                pen.stroke(seg, width, taper=False)
            on, acc, seg = not on, 0.0, [b]
    if on and len(seg) > 1:
        pen.stroke(seg, width, taper=False)
    ex, ey = path[-1]
    px, py = path[-5]
    ang = math.atan2(ey - py, ex - px)
    for s in (-0.5, 0.5):
        hx, hy = ex + 22 * math.cos(ang + math.pi + s), ey + 22 * math.sin(ang + math.pi + s)
        pen.stroke([(hx, hy), (ex, ey)], width, taper=False)


def portrait(img, c, cls, col, dead=False):
    x, y = c
    r = 24
    hexpts = [(x + r * math.cos(math.radians(60 * k + 30)), y + r * math.sin(math.radians(60 * k + 30))) for k in range(6)]
    d = U.BD(img)
    d.polygon(hexpts, fill=(18, 24, 40, 255), outline=col + (255,), width=2)
    g = {'BREAKER': 'slice_zero_day', 'GHOST': 'slice_proxy', 'RIGGER': 'slice_firewall', 'BOTNET': 'slice_trojan'}[cls]
    img = U.paste_glyph(img, g, (x, y), 28, (110, 110, 120) if dead else (255, 255, 255))
    return img


def main():
    img = base()
    # ---------------------------------------------------------------- map layer: Cell turf + Sites
    home = (936, 905)
    cell_nodes = [home, (1030, 842), (1118, 796), (850, 820)]
    for a, b in ((home, (1030, 842)), ((1030, 842), (1118, 796)), (home, (850, 820))):
        img = link(img, a, b, U.LIME)
    img = diamond(img, home, U.PINK, 24, 0.9, ring=True)
    for c in cell_nodes[1:]:
        img = diamond(img, c, U.LIME, 18, 0.8)
    hal = U.CORP['halcyon']
    sites = [((1206, 652), 2, True), ((1300, 600), 3, False), ((1250, 860), 1, False), ((1420, 700), 1, False),
             ((1110, 700), 1, False)]
    img = link(img, (1118, 796), (1206, 652), (150, 150, 170), 2, 0.6)
    img = link(img, (1206, 652), (1300, 600), (150, 150, 170), 2, 0.4)
    for c, tier, sel in sites:
        img = diamond(img, c, hal, 18, 0.55, pips=tier, ring=sel)
    img = diamond(img, (780, 760), (140, 140, 150), 16, 0.3, glow=0.2)          # cleared, neutral
    # pencil: plan + raid forecast
    pr = U.Pencil(img.size, U.PEN_R, seed=17)
    dashed(pr, [(1440, 690), (1380, 740), (1270, 780), (1150, 800)], 6)
    img = pr.ink(img)
    py = U.Pencil(img.size, U.PEN_Y, seed=18)
    py.circle(1206, 650, 48, 30, width=7)
    py.arrow([(1124, 780), (1150, 730), (1180, 690)], width=7, head=20)
    img = py.ink(img)
    # ---------------------------------------------------------------- title + top bar
    t = U.sticker('THE GRID', 58, U.FILL_YELLOW, seed=22)
    img = U.place(img, t, 176, 64, angle=-3)
    img = U.over(img, (4, 6, 14), U.rect_mask(img.size, (30, 112, 520, 142), chamfer=8), 0.78)
    U.text(img, (40, 126), 'CAMPAIGN 03  //  HALCYON CIVIC  //  ICE 5', U.F(U.MONO, 18), U.CYAN, 'la', 1.2)
    img = U.term_panel(img, (372, 18, 1180, 96), None, hexbg=False, chamfer=12, header=False, glow=0.4, alpha=228)
    res = [('SCHEMATICS', '42', 'picto_hp', U.CYAN, None), ('EXPLOITS', '2/3', 'picto_breach', U.PINK, '3 to breach'),
           ('SITES', '7', 'picto_target', U.LIME, None), ('ARMORY', '5', 'placeholder_shield', U.CYAN, None),
           ('RUNS', '9', 'picto_spin', (200, 200, 214), None)]
    x = 392
    for nm, v, g, col, note in res:
        img = U.paste_glyph(img, g, (x + 16, 57), 30, col)
        U.text(img, (x + 40, 40), nm, U.F(U.MONO, 15), (130, 160, 190), 'la', 1.0)
        U.text(img, (x + 40, 58), v, U.F(U.MONO, 30), U.WHITE, 'la', 1.0)
        if note:
            U.text(img, (x + 40 + U.F(U.MONO, 30).getlength(v) + 10, 74), note, U.F(U.MONO, 13), col, 'la', 0.6)
        x += {'SCHEMATICS': 150, 'EXPLOITS': 220, 'SITES': 120, 'ARMORY': 130, 'RUNS': 120}[nm]
    # ---------------------------------------------------------------- Heat meter
    hb = (1210, 18, 1900, 166)
    img = U.term_panel(img, hb, 'HEAT  //  SUSPECT FILE', accent=(255, 120, 40), tag='FLAGGED', tag_col=(255, 120, 40), seed=5)
    U.live_number(img, (1230, 92), str(HEAT), 64, (255, 120, 40))
    bx0, bx1, by = 1320, 1878, 74
    d = U.BD(img)
    for lo, hi, word, col in BANDS:
        xa, xb = bx0 + (bx1 - bx0) * lo / 100, bx0 + (bx1 - bx0) * hi / 100
        cur = lo <= HEAT < hi
        d.rectangle([xa + 1, by - 10, xb - 1, by + 10], fill=col + (70 if not cur else 120,))
        fill_to = min(xb, bx0 + (bx1 - bx0) * HEAT / 100)
        if fill_to > xa:
            m = U.rect_mask(img.size, (xa + 1, by - 10, fill_to - 1, by + 10))
            img = U.over(img, col, m, 0.95)
            d = U.BD(img)
        U.text(img, ((xa + xb) / 2, by + 24), word, U.F(U.MONO, 15), col if cur else (130, 136, 150), 'mm', 1.6)
    for th in (25, 50, 75):
        tx = bx0 + (bx1 - bx0) * th / 100
        d.line([(tx, by - 16), (tx, by + 14)], fill=(240, 240, 240, 255), width=2)
        U.text(img, (tx, by - 22), str(th), U.F(U.MONO, 13), (210, 210, 220), 'mm', 0.6)
    mx = bx0 + (bx1 - bx0) * HEAT / 100
    d.polygon([(mx - 8, by - 20), (mx + 8, by - 20), (mx, by - 10)], fill=(255, 255, 255, 255))
    U.text(img, (1230, 142), 'while >= 50: enemies +1 resistance    next: 60 complication  //  75 RAID', U.F(U.MONO, 15),
           (220, 190, 170), 'la', 0.5)
    # ---------------------------------------------------------------- crew roster
    cb = (20, 168, 412, 612)
    img = U.term_panel(img, cb, 'CREW', tag='3 ALIVE / 4', seed=7)
    crew = [('CELL-9', 'BREAKER', 2, '60/60', 'READY', U.GREEN, False, True),
            ('NOVA', 'GHOST', 1, '50/50', 'STATIONED S-12', U.CYAN, False, False),
            ('RIG-4', 'RIGGER', 0, '55/55', 'READY', U.GREEN, False, False),
            ('HEX', 'BOTNET', 1, '--', 'FLATLINED', (150, 150, 160), True, False)]
    for k, (nm, cls, rank, hp, st, col, dead, sel) in enumerate(crew):
        y0 = 214 + k * 88
        if sel:
            m = U.rect_mask(img.size, (30, y0 - 8, 402, y0 + 72), chamfer=8)
            img = U.over(img, U.PINK, m, 0.12)
            e = ImageChops.subtract(m, SL.erode(m, 2))
            img = U.over(img, U.PINK, e)
        img = portrait(img, (68, y0 + 32), cls, U.PINK if sel else (U.CYAN if not dead else (90, 90, 100)), dead)
        U.text(img, (104, y0 + 6), nm, U.F(U.MONO, 24), U.WHITE if not dead else (130, 130, 140), 'la', 1.4)
        U.text(img, (104, y0 + 36), '%s  R%d' % (cls, rank), U.F(U.MONO, 16), (130, 160, 190) if not dead else (110, 110, 120), 'la', 1.0)
        d = U.BD(img)
        for p in range(3):
            d.rectangle([224 + p * 12, y0 + 39, 232 + p * 12, y0 + 49], fill=(U.GOLD if p < rank else (50, 54, 66)) + (255,))
        U.text(img, (392, y0 + 8), hp, U.F(U.MONO, 18), U.WHITE if not dead else (110, 110, 120), 'ra', 0.8)
        U.text(img, (392, y0 + 38), st, U.F(U.MONO, 14), col, 'ra', 0.6)
        if dead:
            d.line([(102, y0 + 20), (200, y0 + 20)], fill=(160, 160, 170, 255), width=2)
        if sel:
            U.text(img, (104, y0 + 58), 'RUNS SITE 12', U.F(U.MONO, 13), U.PINK, 'la', 1.0)
    img = U.term_button(img, (36, 566, 220, 600), 'RECRUIT', None, 'idle')
    U.text(img, (232, 583), '15 SCHEMATICS', U.F(U.MONO, 15), (130, 160, 190), 'lm', 0.8)
    # ---------------------------------------------------------------- map key
    kb = (20, 630, 412, 860)
    img = U.term_panel(img, kb, 'MAP KEY', seed=8)
    rows = [('home', 'HOME SERVER  50/50'), ('cell', 'YOUR NODE / LINK'), ('corp', 'CORP SITE  pips = tier'),
            ('grey', 'CLEARED, NEUTRAL'), ('pen_y', 'YOUR PLAN (pencil)'), ('pen_r', 'RAID FORECAST (dashed)')]
    for k, (kind, s) in enumerate(rows):
        yy = 680 + k * 30
        if kind == 'home':
            img = diamond(img, (52, yy), U.PINK, 14, 0.9, glow=0.4)
        elif kind == 'cell':
            img = diamond(img, (52, yy), U.LIME, 14, 0.8, glow=0.4)
        elif kind == 'corp':
            img = diamond(img, (52, yy - 3), hal, 14, 0.55, pips=2, glow=0.4)
        elif kind == 'grey':
            img = diamond(img, (52, yy), (140, 140, 150), 14, 0.3, glow=0.1)
        else:
            p = U.Pencil(img.size, U.PEN_Y if kind == 'pen_y' else U.PEN_R, seed=k)
            if kind == 'pen_y':
                p.stroke([(36, yy + 2), (52, yy - 2), (68, yy)], 5)
            else:
                dashed(p, [(34, yy + 2), (50, yy - 1), (70, yy)], 5, dash=8, gap=6)
            img = p.ink(img)
        U.text(img, (84, yy), s, U.F(U.MONO, 17), (200, 214, 230), 'lm', 0.8)
    # ---------------------------------------------------------------- selected Site (holo) + IF CLEARED (terminal)
    sb = (1500, 186, 1900, 520)
    img = U.holo_panel(img, sb, 'halcyon', 'SITE 12  //  PRECINCT RELAY', seed=12)
    img = U.corp_seal(img, (1846, 238), 30, 'halcyon')
    lines = [('TIER', 'T2', None), ('DISTRICT', 'CIVIC SPRAWL', None), ('OBJECTIVE', 'EXTRACT INTEL', U.PINK),
             ('FINAL RACK', 'holds an EXPLOIT', None), ('GUARD', 'ELITE ENFORCER', None), ('NODE SLOT', 'RELAY / FIREWALL', None)]
    for k, (a, b, col) in enumerate(lines):
        yy = 290 + k * 32
        U.text(img, (1520, yy), a, U.F(U.MONO, 16), (180, 170, 240), 'la', 1.0)
        U.text(img, (1880, yy), b, U.F(U.MONO, 19), col or U.WHITE, 'ra', 0.8)
    d = U.BD(img)
    for p in range(2):
        d.rectangle([1520 + p * 16, 260, 1530 + p * 16, 270], fill=hal + (255,))
    img = U.term_panel(img, (1516, 474, 1884, 506), None, accent=U.GREEN, hexbg=False, chamfer=6, header=False, glow=0.4)
    U.text(img, (1700, 490), 'DECRYPTED  //  KEY 7F-A2', U.F(U.MONO, 15), U.GREEN, 'mm', 1.2)
    ib = (1500, 540, 1900, 790)
    img = U.term_panel(img, ib, 'IF CLEARED', tag='FORECAST', seed=13)
    gains = [('EXPLOIT', '+1 INTEL', U.PINK), ('SCHEMATICS', '+17', U.CYAN), ('HEAT', '+13  (58 > 71)', (255, 120, 40)),
             ('OPENS', 'SITE 19 (T3)', U.LIME), ('RAID', 'RETALIATION (heat 50+)', U.HARM)]
    for k, (a, b, col) in enumerate(gains):
        yy = 592 + k * 38
        U.text(img, (1520, yy), a, U.F(U.MONO, 18), (150, 176, 200), 'la', 1.2)
        U.text(img, (1880, yy), b, U.F(U.MONO, 20), col, 'ra', 0.8)
    # ---------------------------------------------------------------- raid alert (terminal) + entry
    rb = (440, 944, 1150, 1068)
    img = U.term_panel(img, rb, 'RAID PENDING', accent=U.HARM, tag='HEAT 50 CROSSED', tag_col=U.HARM, seed=21)
    U.text(img, (460, 988), 'HALCYON COMPLIANCE SWEEP', U.F(U.MONO, 19), U.WHITE, 'la', 1.0)
    U.text(img, (460, 1014), '6 units  //  3 entry sites', U.F(U.MONO, 16), (220, 170, 170), 'la', 0.6)
    U.text(img, (460, 1038), 'before the next netrun; scales with Heat', U.F(U.MONO, 16), (220, 170, 170), 'la', 0.4)
    img = U.term_button(img, (930, 994, 1130, 1050), 'RAID SETUP', '[R]', 'idle', accent=U.HARM)
    # nav + JACK IN
    img = U.term_button(img, (20, 990, 220, 1050), 'BACK TO HQ', '[ESC]', 'idle')
    img = U.term_button(img, (1172, 990, 1312, 1046), '< PREV', '[Q]', 'idle')
    img = U.term_button(img, (1324, 990, 1464, 1046), 'NEXT >', '[E]', 'idle')
    img = U.term_panel(img, (1500, 812, 1900, 862), None, hexbg=False, chamfer=8, header=False, glow=0.3)
    U.text(img, (1516, 837), 'RUNNER', U.F(U.MONO, 15), (130, 160, 190), 'lm', 1.0)
    img = portrait(img, (1610, 837), 'BREAKER', U.PINK)
    U.text(img, (1644, 837), 'CELL-9  BREAKER R2', U.F(U.MONO, 19), U.WHITE, 'lm', 0.8)
    j = U.sticker('JACK IN', 84, U.FILL_PINK, seed=31)
    img = U.place(img, U.focus_sticker(j), 1700, 960, angle=-3)
    img.convert('RGB').save(OUT)
    print('wrote', OUT)


if __name__ == '__main__':
    main()
