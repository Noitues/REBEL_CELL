"""raid_v3: the RAID screen in the Deface v3 look (the Takeover fight's look), first concept set.

    python raid_v3.py [plan place shop playback site aftermath sheet]      (default: all)

Writes r3_*.png and r3_sheet.jpg to docs/concepts/raid_v3/.  The raid itself follows prototype Variant B v39 (cell-grid tower
defence; words kept); the look follows ART_BIBLE 1.2 + the designer rulings of 2026-11-15 (status = sticker, value = pencil;
pencil may carry forecast numbers).  Toolkit: raid_kit.py (which imports the Takeover v3 scripts read-only).
"""
import math, os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import raid_kit as K
from raid_kit import (Wax, PEN_Y, PEN_R, SL, IR, TR, S, text, Layer, comp, INK, PAPER, HARM, CYAN, TEXT_HI, TEXT_MID, ANTON, MONO,
                      W, H, SS, F_all, base_image, glass, stick, S_GAIN, S_HARM, S_HI, S_PLAN, S_MID, TEAL, TEAL_D, TEAL_HI)

OUT = 'D:/rc_art/art-pass/docs/concepts/raid_v3/'
DOT = ('\u00b7', S_MID)

# =============================================================================================== the road raid (STATIC ALLEY)
G = K.Grid(7, 9, 624, 64, 96)
PA = [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2), (2, 3), (2, 4), (3, 4), (3, 5), (3, 6), (3, 7)]
PB = [(6, 0), (6, 1), (6, 2), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (4, 6), (3, 6)]
SAFE = (3, 8)
BARR = (2, 1)


def _pts(cells, entry, end=None):
    return [entry] + [G.cc(*c) for c in cells] + ([end] if end else [])


PATHS = [dict(id='A', cells=PA, pts=_pts(PA, (G.cc(0, 0)[0], G.y0 - 14), G.cc(*SAFE))),
         dict(id='B', cells=PB, pts=_pts(PB, (G.cc(6, 0)[0], G.y0 - 14)))]
ROUTE_A = _pts(PA, (G.cc(0, 0)[0], G.y0 - 8), (G.cc(*SAFE)[0], G.cc(*SAFE)[1] - 44))
ROUTE_B = _pts(PB, (G.cc(6, 0)[0], G.y0 - 8))

ROUNDS = [('ROUND 1 (now)  \u00b7  8 units', [('A', 'trooper', 'Trooper', 5), ('B', 'bike', 'Bike', 3)]),
          ('ROUND 2  \u00b7  9 units', [(None, 'trooper', 'Trooper', 4), (None, 'riot', 'Riot', 2), (None, 'bike', 'Bike', 3)]),
          ('ROUND 3  \u00b7  8 units', [(None, 'heavy', 'Heavy', 2), (None, 'drone', 'Drone', 3), (None, 'trooper', 'Trooper', 3)]),
          ('ROUND 4  \u00b7  9 units', [(None, 'wrecker', 'Wrecker', 1), (None, 'sniper', 'Sniper', 2), (None, 'trooper', 'Trooper', 6)])]

PLACED = {'KAI': (1, 2), 'VEX': (3, 2), 'MOTH': (1, 4)}
MAP_ANG = {'KAI': -5, 'VEX': 4, 'MOTH': 3, 'RUNE': -4}
MAP_K = 0.46


def op_on_map(img, oid, c, r, grid=G, k=MAP_K):
    x, y = grid.cc(c, r)
    stick(img, K.op_sticker(oid), x, y, MAP_ANG[oid], scale=k)
    o = K.OPS[oid]
    stick(img, K.wpn_sticker(o['wpn'], o['stars']), x + K.WPN_OFF[0] * k, y + K.WPN_OFF[1] * k, K.WPN_OFF[2], scale=k * 0.9)


def road_base(img, F, placed=PLACED, barricade=True, tags=True):
    K.draw_city(img, F, G, PATHS, open_cells=[SAFE])
    if tags:
        K.path_tag(img, F, G.cc(0, 0)[0] + 30, 30, 'A \u00b7 NEON AVENUE \u25b6 HQ')
        K.path_tag(img, F, G.cc(6, 0)[0] - 30, 30, 'B \u00b7 RAIL CUT \u25b6 HQ', anchor='r')
    return img


def road_objects(img, placed=PLACED, barricade=True):
    """runner objects on the map: the Safehouse, the barricade, the placed operatives"""
    x, y = G.cc(*SAFE)
    stick(img, K.place_sticker('SAFE', 'HOUSE', (255, 110, 196), (222, 24, 136)), x, y + 2, -3, scale=0.8)
    if barricade:
        bx, by = G.cc(*BARR)
        stick(img, K.dev_sticker('BARRICADE'), bx - 26, by, 88, scale=0.56)
    for oid, (c, r) in placed.items():
        op_on_map(img, oid, c, r)


def road_routes(pr):
    K.route(pr, ROUTE_A, off=31)
    K.route(pr, ROUTE_B, off=31)
    K.entry_mark(pr, G.cc(0, 0)[0], 30, 'A')
    K.entry_mark(pr, G.cc(6, 0)[0], 30, 'B')


def left_col(img, F, where, core=8, lose=0, credits=7, cost=0, rnd=(1, 4), title='RAID: STATIC ALLEY', kills=None, skip=(),
             weapons=None, counts=None, undo=True):
    K.core_tape(img, F, title, core, 8 if core <= 8 and title.endswith('ALLEY') else 6, lose)
    K.rows(img, F, rnd[0], rnd[1], credits, cost)
    K.crew(img, F, where, kills=kills, skip=skip, weapons=weapons)
    K.left_foot(img, F, counts or [('ON MAP', sum(1 for v in where.values() if v and not v.startswith('away'))),
                                   ('BENCH', 4 - len([v for v in where.values() if v])), ('DEVICES', 1)], undo=undo)


def right_col(img, F, site='STATIC ALLEY', rounds=ROUNDS, state='ready', peeled=None, system='START ROUND 1', locked=False):
    K.incoming(img, F, site, 25, rounds)
    K.shop_sheet(img, F, peeled=peeled)
    if locked:                                              # during playback the sheet can't be peeled
        L = Layer()
        L.d.rectangle([S(1404), S(492), S(1898), S(834)], fill=(6, 8, 12, 150))
        text(L.d, (1651, 752), 'shop opens after the round', F['m20'], TEXT_HI + (255,))
        comp(img, L)
    K.send_it(img, F, system=system, state=state)


def plan_pencil(py, pr, leak=True):
    # A holds at c2: the yellow stop bar at the wall, "holds c2", the wall's hp forecast
    x0, y0, x1, y1 = G.box(*BARR)
    K.pen_stop(py, x0 - 10, y0 + 12, y1 - 12)
    py.text('holds c2', 770, 116, 30, angle=-5)
    K.pen_arrow_num(py, 6, 3, 926, 198, 32)
    if leak:
        # B: 2 leak, a red arrow to the Safehouse, 8 -> 6 by it
        pr.text('2 leak', 1240, 470, 32, angle=-6)
        pr.arrow([(1236, 500), (1252, 620), (1222, 744), (1120, 846), (1024, 874)], width=7, head=20)
        K.pen_arrow_num(pr, 8, 6, 800, 880, 34)


# ---------------------------------------------------------------- 1. plan
def plate_plan():
    F = F_all(); img = base_image()
    road_base(img, F)
    K.token(img, 'trooper', *G.cc(0, 0), 8, count=5)
    K.token(img, 'bike', *G.cc(6, 0), 6, count=3)
    road_objects(img)
    py, pr = Wax(PEN_Y, 1), Wax(PEN_R, 2)
    road_routes(pr)
    plan_pencil(py, pr)
    py.ink_ss(img); pr.ink_ss(img)
    left_col(img, F, {'KAI': 'b3', 'VEX': 'd3', 'MOTH': 'b5'}, lose=2)
    right_col(img, F)
    K.hud_line(img, F, 'FORECAST', [('A holds at c2', S_GAIN), DOT, ('B 2 leak', S_HARM), DOT, ('Core 8 \u2192 6', S_HARM), DOT,
                                    ('6/8 killed', S_HI)])
    return img


# ---------------------------------------------------------------- 2. place (RUNE peeled, hovering e6)
HOVER = (4, 5)
BEST = [((4, 5), '+3'), ((4, 4), '+2'), ((6, 5), '+1')]


def legal_cells(occupied):
    road = set(PA) | set(PB) | {SAFE}
    out = []
    for c in range(G.cols):
        for r in range(G.rows):
            if (c, r) in road or (c, r) in occupied:
                continue
            if any(abs(c - a) <= 1 and abs(r - b) <= 1 for a, b in road):
                out.append((c, r))
    return out


def plate_place():
    F = F_all(); img = base_image()
    road_base(img, F)
    # system: the legal cells, dashed cyan (pencil loops on ~20 cells would be noise)
    L = Layer(); d = L.d
    for c, r in legal_cells(set(PLACED.values())):
        x0, y0, x1, y1 = G.box(c, r)
        IR.dash_poly(d, [(x0 + 9, y0 + 9), (x1 - 9, y0 + 9), (x1 - 9, y1 - 9), (x0 + 9, y1 - 9), (x0 + 9, y0 + 9)],
                     (70, 160, 190), 2, on=7, off=6)
    comp(img, L)
    K.token(img, 'trooper', *G.cc(0, 0), 8, count=5)
    K.token(img, 'bike', *G.cc(6, 0), 6, count=3)
    road_objects(img)
    py, pr = Wax(PEN_Y, 3), Wax(PEN_R, 4)
    road_routes(pr)
    plan_pencil(py, pr, leak=False)
    # the preview: reach hatched (Chebyshev 1 round e6), the hovered cell circled, kills-if-placed in the best 3 cells
    x0, y0, _, _ = G.box(HOVER[0] - 1, HOVER[1] - 1)
    _, _, x1, y1 = G.box(HOVER[0] + 1, HOVER[1] + 1)
    K.pen_hatch_box(py, x0 + 4, y0 + 4, x1 - 4, y1 - 4)
    hx, hy = G.cc(*HOVER)
    py.circle(hx, hy, 42, 42, width=7, start=-2.2, over=0.5, tilt=0)
    for (c, r), s_ in BEST:
        x, y = G.cc(c, r)
        py.text(s_, x, y + 2, 40 if s_ == '+3' else 34, angle=-6)
    # the plan line from the parked sticker to the cell (stops outside the circle)
    py.arrow([(500, 410), (640, 372), (800, 368), (936, 420), (1000, 500), (1022, 548)], width=7, head=22)
    # B no longer leaks: the red "2 leak" struck through in yellow, 0 beside it; the Safehouse is safe
    pr.text('2 leak', 1240, 470, 32, angle=-6)
    py.text('0', 1250, 520, 38, angle=-6)
    py.text('safe', 838, 880, 34, angle=-6)
    py.ink_ss(img); pr.ink_ss(img)
    ps = Wax(PEN_Y, 33)                                     # the strike goes over the red word, so it is inked after it
    ps.stroke(ps.wobble([(1186, 478), (1294, 462)], 0.6), 6, taper=False)
    ps.ink_ss(img)
    left_col(img, F, {'KAI': 'b3', 'VEX': 'd3', 'MOTH': 'b5'}, skip=('RUNE',))
    # RUNE peeled: liner outline at its slot, the sticker parked above it (lift, curl), its weapon riding with it
    sx, sy, sa = K.CREW_POS['RUNE']
    K.liner(img, K.op_sticker('RUNE'), sx, sy, sa)
    px_, py_ = 404, 446
    stick(img, K.op_sticker('RUNE', curl=0.42), px_, py_, 7, scale=1.0, lift=1.0)
    stick(img, K.wpn_sticker('SHOTGUN', 1), px_ + 74, py_ - 70, 16, scale=0.82, lift=1.0)
    right_col(img, F)
    K.hud_line(img, F, 'IF PLACED e6', [('B 2 leak', S_HARM), ('\u2192', S_MID), ('0 leak', S_GAIN), DOT, ('Core safe', S_GAIN), DOT,
                                        ('8/8 killed', S_HI)])
    return img


# ---------------------------------------------------------------- 3. shop (buy SHOTGUN, slap it on RUNE: merge 1 -> 2 stars)
def plate_shop():
    F = F_all(); img = base_image()
    road_base(img, F)
    K.token(img, 'trooper', *G.cc(0, 0), 8, count=5)
    K.token(img, 'bike', *G.cc(6, 0), 6, count=3)
    road_objects(img)
    py, pr = Wax(PEN_Y, 5), Wax(PEN_R, 6)
    road_routes(pr)
    plan_pencil(py, pr)
    py.ink_ss(img); pr.ink_ss(img)
    left_col(img, F, {'KAI': 'b3', 'VEX': 'd3', 'MOTH': 'b5'}, lose=2, cost=3)
    # the bought SHOTGUN: peeled from the sheet, slapped down onto RUNE's own SHOTGUN (two identical stickers, stacked)
    sx, sy, sa = K.CREW_POS['RUNE']
    wx, wy = sx + K.WPN_OFF[0], sy + K.WPN_OFF[1]
    stick(img, K.wpn_sticker('SHOTGUN', 1, cost=3, curl=0.16), wx - 8, wy - 54, 3, scale=0.84, lift=0.7)
    py = Wax(PEN_Y, 7)
    py.text('MERGE', 214, 702, 32, angle=-5)
    K.pen_star(py, 296, 700); py.text('+', 322, 702, 30); K.pen_star(py, 348, 700)
    py.arrow([(368, 702), (386, 700), (404, 701)], width=5, head=10)
    K.pen_star(py, 428, 700); K.pen_star(py, 454, 698)
    py.arrow([(534, 428), (546, 452), (534, 474)], width=5, head=12)
    py.ink_ss(img)
    right_col(img, F, peeled='SHOTGUN')
    K.hud_line(img, F, 'BUY', [('SHOTGUN on RUNE', S_PLAN), ('merges, 1 \u2192 2 stars', S_GAIN), DOT, ('3 credits: 7 \u2192 4', S_HI)])
    return img


# ---------------------------------------------------------------- 4. playback (tick 3 of 8)
def plate_playback():
    F = F_all(); img = base_image()
    road_base(img, F)
    # units still to enter (faint), the held trooper, the kill, the slowed bike
    K.token(img, 'trooper', *G.cc(0, 0), 8, count=3, alpha=0.35)
    K.token(img, 'bike', *G.cc(6, 0), 6, count=1, alpha=0.35)
    hx, hy = G.cc(1, 1)
    K.token(img, 'trooper', hx, hy, 4)
    bx, by = G.cc(5, 3)
    # glide: a short motion smear behind the bike
    L = Layer()
    for k in range(5):
        L.d.line([(S(bx - 6 + k * 3), S(by - 30 - k * 9)), (S(bx - 6 + k * 3), S(by - 44 - k * 9))], fill=(150, 170, 190, 120 - k * 20), width=S(2))
    comp(img, L)
    K.token(img, 'bike', bx, by, 3)
    placed = dict(PLACED, RUNE=HOVER)
    road_objects(img, placed=placed)
    # the statuses: stickers on the unit, the value (ticks) in pencil beside
    stick(img, K.status_sticker('H'), hx + 4, hy - 36, -6)
    stick(img, K.status_sticker('S'), bx - 28, by + 32, 6)
    # the chain callout as a temporary word sticker
    stick(img, K.word_sticker('HELD + BOMBARD \u00d72', (255, 110, 196), (222, 24, 136)), 944, 118, -4)
    py, pr = Wax(PEN_Y, 9), Wax(PEN_R, 10)
    road_routes(pr)
    py.text('2', hx - 26, hy - 66, 32, angle=-6)
    py.text('1', bx - 62, by + 40, 32, angle=-6)
    K.pen_arrow_num(py, 6, 4, 926, 198, 32)             # the barricade's hp, live
    for (x, y) in ((704, 344), (946, 364)):            # kill tallies by KAI and VEX
        py.x(x, y, 10, 6)
    py.ink_ss(img); pr.ink_ss(img)
    # FX: tracers from the shooters, the kill bursting into bits, damage pops
    K.tracer(img, G.cc(1, 2), (G.cc(0, 1)[0] + 10, G.cc(0, 1)[1] + 12), K.OPS['KAI']['col'][1])
    K.tracer(img, G.cc(3, 2), (bx - 12, by + 6), K.OPS['VEX']['col'][1])
    K.kill_burst(img, 'trooper', G.cc(0, 1)[0] - 6, G.cc(0, 1)[1] + 4, spread=44)
    K.pop(img, F, hx + 46, hy - 80, '\u22124')
    K.pop(img, F, bx + 2, by - 54, '\u22123')
    left_col(img, F, {'KAI': 'b3', 'VEX': 'd3', 'MOTH': 'b5', 'RUNE': 'e6'})
    right_col(img, F, state='busy', locked=True)
    K.hud_line(img, F, 'TICK 3/8', [('killed 2', S_GAIN), DOT, ('leaked 0', S_HI), DOT, ('1 held at a wall', S_HI), DOT,
                                    ('4 still to enter', S_MID)], ticks=(3, 8))
    return img


# =============================================================================================== 5. the site raid (SITE B2)
GS = K.Grid(11, 9, 564, 110, 72)
SA = [(5, r) for r in range(5)]
SB = [(c, 5) for c in range(5)]
SC = [(c, 5) for c in range(10, 5, -1)]
SITE, SCORE = (5, 5), (5, 6)
SPATHS = [dict(id='A', cells=SA, pts=[(GS.cc(5, 0)[0], GS.y0 - 8)] + [GS.cc(*c) for c in SA] + [GS.cc(*SITE)]),
          dict(id='B', cells=SB, pts=[(GS.x0 - 8, GS.cc(0, 5)[1])] + [GS.cc(*c) for c in SB] + [GS.cc(*SITE)]),
          dict(id='C', cells=SC, pts=[(GS.x1 + 8, GS.cc(10, 5)[1])] + [GS.cc(*c) for c in SC] + [GS.cc(*SITE)])]
SROUNDS = [('ROUND 1 (now)  \u00b7  7 units', [('A', 'trooper', 'Trooper', 3), ('B', 'riot', 'Riot', 2), ('C', 'drone', 'Drone', 2)]),
           ('ROUND 2  \u00b7  8 units', [(None, 'trooper', 'Trooper', 4), (None, 'bike', 'Bike', 2), (None, 'drone', 'Drone', 2)]),
           ('ROUND 3  \u00b7  9 units', [(None, 'heavy', 'Heavy', 2), (None, 'riot', 'Riot', 3), (None, 'trooper', 'Trooper', 4)])]


def plate_site():
    F = F_all(); img = base_image()
    K.draw_city(img, F, GS, SPATHS, open_cells=[SITE, SCORE], panel=(540, 40, 1380, 780), seed=7)
    K.path_tag(img, F, GS.cc(5, 0)[0] + 32, 76, 'A \u00b7 NORTH STAIR \u25b6 B2')
    K.path_tag(img, F, GS.x0 + 46, 434, 'B \u00b7 WEST YARD \u25b6 B2')
    K.path_tag(img, F, GS.x1 - 46, 434, 'C \u00b7 DOCK ROAD \u25b6 B2', anchor='r')
    K.token(img, 'trooper', *GS.cc(5, 0), 8, count=3, r=19)
    K.token(img, 'riot', *GS.cc(0, 5), 10, count=2, r=19)
    K.token(img, 'drone', *GS.cc(10, 5), 5, count=2, r=19)
    sx, sy = GS.cc(*SITE)
    stick(img, K.place_sticker('B2', 'SITE', (150, 236, 130), (62, 170, 70), shape='socket', w=96, h=84), sx, sy, -3, scale=0.78)
    cx, cy = GS.cc(*SCORE)
    stick(img, K.place_sticker('CORE', None, (255, 110, 196), (222, 24, 136), shape='hex', w=100, h=64), cx, cy + 4, 3, scale=0.62)
    L = Layer(); text(L.d, (cx + 60, cy + 4), '6/6', F['a34'], TEXT_HI + (255,), stroke=2, sfill=INK + (255,)); comp(img, L)
    op_on_map(img, 'KAI', 4, 4, grid=GS, k=0.4)
    op_on_map(img, 'VEX', 6, 4, grid=GS, k=0.4)
    py, pr = Wax(PEN_Y, 11), Wax(PEN_R, 12)
    for p, (ex, ey), lt in ((SPATHS[0], (GS.cc(5, 0)[0], 76), 'A'), (SPATHS[1], (GS.x0 + 22, 434), 'B'), (SPATHS[2], (GS.x1 - 22, 434), 'C')):
        K.route(pr, p['pts'][:-1] + [p['pts'][-2]] if False else p['pts'][:-1], off=24)
        K.entry_mark(pr, ex, ey, lt)
    # who defends: B2's own crew, and the supporter that C2 sends in from its side
    kx, ky = GS.cc(4, 4)
    vx, vy = GS.cc(6, 4)
    py.text('B2 crew', kx - 92, ky - 52, 30, angle=-6)
    py.arrow([(1350, 250), (1250, 300), (1130, 360), (1076, 400)], width=6, head=18)
    py.text('from C2', 1262, 248, 32, angle=-6)
    # forecast: B (riot) leaks 1 into the core
    pr.text('1 leak', 690, 596, 32, angle=-5)
    pr.arrow([(760, 600), (850, 612), (918, 590)], width=7, head=18)
    K.pen_arrow_num(pr, 6, 5, 1072, 590, 32)
    # the "who defends" note in the margin, under the map
    py.text('who defends B2', 1066, 812, 32, angle=-3)
    py.text('KAI   B2', 1010, 858, 30, angle=-3); py.tick(1090, 856, 12, 5)
    py.text('VEX   C2', 1010, 900, 30, angle=-3); py.tick(1090, 898, 12, 5)
    py.ink_ss(img); pr.ink_ss(img)
    K.chip(img, F, 580, 806, 'EVACUATE', '(E)', w=230, sub='B2 to the corp, crew walks')
    K.core_tape(img, F, 'RAID: SITE B2', 6, 6, 1)
    K.rows(img, F, 1, 3, 7)
    K.crew(img, F, {'KAI': 'e5', 'VEX': 'g5', 'MOTH': 'away:A1', 'RUNE': 'away:D4'})
    K.left_foot(img, F, [('ON MAP', 2), ('AWAY', 2), ('DEVICES', 0)])
    right_col(img, F, site='SITE B2', rounds=SROUNDS)
    K.hud_line(img, F, 'FORECAST', [('A 0 leak', S_GAIN), DOT, ('B 1 leak', S_HARM), DOT, ('C 0 leak', S_GAIN), DOT,
                                    ('Core 6 \u2192 5', S_HARM), DOT, ('6/7 killed', S_HI)])
    return img


# =============================================================================================== 6. aftermath: the corp's report
PW, PH = 760, 900
PCX, PCY, PANG = 940, 528, 2.0


def P(x, y):
    """paper-local (1x) -> screen, for the paper rotated PANG degrees counter-clockwise about its centre"""
    t = math.radians(PANG)
    dx, dy = x - PW / 2, y - PH / 2
    return (PCX + dx * math.cos(t) + dy * math.sin(t), PCY - dx * math.sin(t) + dy * math.cos(t))


REPORT = [('OPERATION', 'CLEAN SWEEP'), ('TARGET', 'Cell safehouse, grid d9'), ('DURATION', '4 rounds'), ('UNITS COMMITTED', '34'),
          ('UNITS LOST', '30'), ('UNITS THROUGH', '0'), ('TARGET DAMAGE', 'none'), ('OUTCOME', None), ('NEXT ACTION', 'review Heat, resubmit')]
RY0, RDY, RVX = 262, 50, 330


def report_paper(F):
    im = Image.new('RGBA', (S(PW), S(PH)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, S(PW), S(PH)], fill=(238, 233, 220, 255))
    rng = np.random.default_rng(4)
    for _ in range(900):
        x, y = rng.uniform(0, S(PW)), rng.uniform(0, S(PH))
        d.point((x, y), fill=(214, 207, 192, 255))
    T = lambda xy, s, f, col, anchor='lm': d.text((S(xy[0]), S(xy[1])), s, font=f, fill=col, anchor=anchor)
    T((48, 62), 'SOLACE', TR.font(ANTON, 50), TEAL_D + (255,))
    T((222, 68), 'Civic Assurance \u00b7 Field Operations', TR.font(MONO, 20), (40, 96, 100, 255))
    d.rectangle([S(48), S(102), S(PW - 48), S(105)], fill=TEAL_D + (255,))
    T((48, 152), 'AFTER-ACTION REPORT', TR.font(ANTON, 42), INK + (255,))
    T((48, 198), 'REF SOL-AAR-2611-07  \u00b7  SECTOR STATIC ALLEY  \u00b7  HEAT 25', TR.font(MONO, 18), (90, 84, 76, 255))
    fl, fv = TR.font(MONO, 20), TR.font(MONO, 25)
    for k, (lab, val) in enumerate(REPORT):
        y = RY0 + k * RDY
        T((48, y), lab, fl, (96, 90, 80, 255))
        if val is None:
            d.rectangle([S(RVX), S(y - 13), S(RVX + 250), S(y + 13)], fill=(18, 16, 20, 255))
        else:
            T((RVX, y), val, fv, INK + (255,))
        d.line([(S(48), S(y + 24)), (S(PW - 48), S(y + 24))], fill=(214, 206, 190, 255), width=S(1))
    y = RY0 + len(REPORT) * RDY + 70
    T((48, y), 'FIELD SUPERVISOR', TR.font(MONO, 18), (96, 90, 80, 255))
    d.line([(S(250), S(y + 10)), (S(560), S(y + 10))], fill=(120, 112, 100, 255), width=S(1.5))
    sig = [(262 + k * 14, y - 4 + 10 * math.sin(k * 1.3) * (1 if k % 3 else -0.6)) for k in range(18)]
    d.line([(S(x), S(yy)) for x, yy in sig], fill=(30, 40, 90, 255), width=S(2), joint='curve')
    T((48, PH - 40), 'SOLACE CIVIC ASSURANCE  \u00b7  INTERNAL  \u00b7  PAGE 1 OF 1', TR.font(MONO, 16), (130, 122, 108, 255))
    # CLASSIFIED: the corp's own stamp, in corp teal ink (a held raid is never red), worn
    st = Image.new('L', (S(330), S(96)), 0); sd = ImageDraw.Draw(st)
    sd.rectangle([S(4), S(4), S(326), S(92)], outline=255, width=S(5))
    sd.text((S(165), S(50)), 'CLASSIFIED', font=TR.font(ANTON, 58), fill=255, anchor='mm')
    noise = (np.random.default_rng(8).random((st.height, st.width)) > 0.22).astype(np.uint8) * 255
    st = SL.ImageChops.multiply(st, Image.fromarray(noise)).rotate(9, expand=True, resample=Image.BICUBIC)
    im.paste(Image.new('RGBA', st.size, (30, 120, 124, 220)), (S(PW - 380), S(118)), st)
    return im


def plate_aftermath():
    F = F_all(); img = base_image()
    road_base(img, F)
    road_objects(img, placed={})
    L = Layer(); L.d.rectangle([S(540), S(0), S(1390), S(H)], fill=(4, 6, 10, 150)); comp(img, L)
    paper = report_paper(F).rotate(PANG, expand=True, resample=Image.BICUBIC)
    sh = Image.new('RGBA', paper.size, (4, 3, 6, 0))
    sh.putalpha(paper.split()[3].filter(ImageFilter.GaussianBlur(S(10))).point(lambda v: int(v * 0.6)))
    x, y = int(S(PCX) - paper.width / 2), int(S(PCY) - paper.height / 2)
    img.alpha_composite(sh, (x + S(10), y + S(16)))
    img.alpha_composite(paper, (x, y))
    # the Cell's pencil on the corp's paper: circle the losses, 30/34, ticks
    py = Wax(PEN_Y, 13)
    cx, cy = P(RVX + 18, RY0 + 4 * RDY)
    py.circle(cx, cy, 44, 28, width=7, start=-2.4, over=0.5, tilt=-0.03)
    lx, ly = P(560, RY0 + 4 * RDY - 6)
    py.text('30/34', lx, ly, 60, angle=PANG - 6)
    for k, dx in ((5, 40), (6, 104)):
        tx, ty = P(RVX + dx, RY0 + k * RDY)
        py.tick(tx, ty, 13, 6)
    hx, hy = P(590, RY0 + 6 * RDY)
    py.text('HQ untouched', hx, hy, 32, angle=PANG - 4)
    py.ink_ss(img)
    # HELD, slapped over the corp's sign-off (yellow: never red)
    hx, hy = P(500, RY0 + 8 * RDY + 70)
    stick(img, K.verb_sticker('HELD', (255, 238, 96), (255, 182, 14), size=110), hx, hy, PANG - 7, scale=1.0)
    left_col(img, F, {}, kills={'KAI': 11, 'VEX': 9, 'MOTH': 4, 'RUNE': 6}, rnd=(4, 4), credits=12,
             counts=[('KILLED', 30), ('LEAKED', 0)], undo=False)
    # result panel (system) and CONTINUE
    L = Layer(); d = L.d
    x0, y0, x1, y1 = 1404, 18, 1898, 330
    glass(d, (x0, y0, x1, y1))
    text(d, (x0 + 18, y0 + 28), 'RESULT', F['m20'], TEXT_MID + (255,), anchor='lm')
    text(d, (x0 + 18, y0 + 80), 'HELD for 4 rounds', F['a48'], S_GAIN + (255,), anchor='lm')
    text(d, (x0 + 18, y0 + 138), '30 of 34 units killed, 0 leaked', F['a28'], S_HI + (255,), anchor='lm')
    d.line([(S(x0 + 14), S(y0 + 172)), (S(x1 - 14), S(y0 + 172))], fill=(40, 90, 110, 255), width=S(1.5))
    text(d, (x0 + 18, y0 + 206), 'HQ untouched', F['a28'], S_GAIN + (255,), anchor='lm')
    text(d, (x0 + 18, y0 + 250), 'Heat \u22121', F['a28'], S_GAIN + (255,), anchor='lm')
    text(d, (x0 + 120, y0 + 251), '25 \u2192 24', F['a28'], S_HI + (255,), anchor='lm')
    comp(img, L)
    K.send_it(img, F, system=None, word='CONTINUE', key='Continue [SPACE]')
    return img


# =============================================================================================== sheet
def sheet():
    names = [('r3_plan', 'plan', 'round 1 at rest: routes, wall holds c2, B leaks 2 (pencil = HUD line)'),
             ('r3_place', 'place', 'RUNE peeled: reach hatched, e6 circled, +3 / +2 / +1, IF PLACED line'),
             ('r3_shop', 'shop', 'sticker sheet: SHOTGUN peeled, slapped on RUNE, merge to 2 stars'),
             ('r3_playback', 'playback', 'tick 3/8: H and S stickers + pencil ticks, kill bits, pops'),
             ('r3_site', 'site raid', 'cross lanes on B2: B2 crew + C2 support, EVACUATE chip'),
             ('r3_aftermath', 'aftermath', "Solace after-action report, the Cell's pencil, HELD")]
    tw_, th_ = 700, 394
    pad, cap = 12, 58
    cols = 3
    sh = Image.new('RGB', (cols * tw_ + (cols + 1) * pad, 2 * (th_ + cap) + 3 * pad + 50), (14, 14, 18))
    d = ImageDraw.Draw(sh)
    f = ImageFont.truetype(MONO, 15); fa = ImageFont.truetype(ANTON, 22); fb = ImageFont.truetype(ANTON, 30)
    d.text((pad, 10), 'RAID in DEFACE v3: first concept set (cell grid under glass, Solace)', font=fb, fill=TEXT_HI)
    for k, (n, t, c) in enumerate(names):
        im = Image.open(OUT + n + '.png').resize((tw_, th_), Image.LANCZOS)
        x = pad + (k % cols) * (tw_ + pad); y = 54 + pad + (k // cols) * (th_ + cap + pad)
        sh.paste(im, (x, y))
        d.text((x + 4, y + th_ + 4), '%s   %s.png' % (t, n), font=fa, fill=TEXT_HI)
        d.text((x + 4, y + th_ + 34), c, font=f, fill=TEXT_MID)
    sh.save(OUT + 'r3_sheet.jpg', quality=90)
    print('ok', OUT + 'r3_sheet.jpg')


R = dict(plan=plate_plan, place=plate_place, shop=plate_shop, playback=plate_playback, site=plate_site, aftermath=plate_aftermath)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for n in (sys.argv[1:] or ['plan', 'place', 'shop', 'playback', 'site', 'aftermath', 'sheet']):
        if n == 'sheet':
            sheet(); continue
        img = R[n]()
        img.resize((W, H), Image.LANCZOS).convert('RGB').save(OUT + 'r3_%s.png' % n)
        print('ok', OUT + 'r3_%s.png' % n)
