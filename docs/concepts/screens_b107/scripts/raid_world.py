"""B-107 item 1 RAID, re-cut to the raid look brief (game-v2 RAID_LOOK_BRIEF.md, v47) as one design: the five moments on the
living semi-isometric city (set 8's district, set 8's camera, every frame), then the result HOLD / TARGET ACQUIRED, plus the
raid mark sheet. Writes screens_b107/raid/*.png.

Pieces reused read-only from the set 8 sources in D:/rc_scratch/raid_v3/src (the city at the raid camera, the district grid,
the v42 slot rule `dock_rules.slots_of`, threat icons v4, class beacons, gear tags, device badges); the chrome is this set's kit.
Slots are COMPUTED by the v42 rule (route cells within dockRadius of the post, one piece each), never hand placed.

    python raid_world.py [a b c d e hold lost marks]      (no argument = all)
"""
import os, sys, math
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SRC = 'D:/rc_scratch/raid_v3/src'
sys.path.insert(1, SRC)
_cwd = os.getcwd(); os.chdir(SRC)
import raid_v3_city as V
import raid_kit as RK
import raid_c as C
import raid_d as D
import dock_rules as DR
os.chdir(_cwd)
from kit import *            # noqa (this set's chrome: K, S, font, text, sticker, stamp, chip, glass, paper, pencil ...)
from raid_screens import corp_ink_stamp

assert RK.SS == K, 'one canvas: the set 8 pieces and this kit share the 2x supersample'
G = V.G
OUTR = OUT + 'raid/'
os.makedirs(OUTR, exist_ok=True)
c3 = lambda c: tuple(c[:3])

# ------------------------------------------------------------------ the crew on the set 8 vinyl (class -> set 8 look)
RK.OPS['MAKO'] = dict(RK.OPS['KAI'], wpn='RAIL', stars=2, lvl=2, reach=2)        # GUNNER: orange octagon
RK.OPS['OZZY'] = dict(RK.OPS['VEX'], wpn='JAMMER', stars=1, lvl=1, reach=1)      # HACKER: blue tag
RK.OPS['NYX'] = dict(RK.OPS['MOTH'], wpn='SMG', stars=1, lvl=1, reach=1)         # FIXER: green hex
RK.OPS['URSA'] = dict(RK.OPS['RUNE'], wpn='SHOTGUN', stars=1, lvl=1, reach=1)    # SAPPER: violet shield
OCOL = {o: RK.OPS[o]['col'][0] for o in ('MAKO', 'OZZY', 'NYX', 'URSA')}

# ------------------------------------------------------------------ the raid (v47 shape): a route of three stops
TARGET, T_CORE = (3, 3), (3, 2)          # d4: the claimed site under attack (MAKO's post); its core cell d3 on the street
THEN, N_CORE = (0, 2), (1, 2)            # a3: one more claimed site on the way (NYX's post)
HQ, H_CORE = (0, 5), (1, 5)              # a6: our HQ (URSA stationed); b6 the street door
LANE_A = [(6, 5), (5, 5), (4, 5), (4, 4), (4, 3), (4, 2), (3, 2)]    # in from the east along street 6, up avenue e
LANE_B = [(2, 0), (2, 1), (2, 2), (3, 2)]                           # in from the north down street c
ENT_A, ENT_B = (7, 5), (2, -1)
LEG_1 = [(3, 2), (2, 2), (1, 2)]                                    # target -> then (survivors walk on)
LEG_2 = [(1, 2), (1, 3), (1, 4), (1, 5)]                            # then -> HQ
N_LANES = [[(2, 0), (1, 0), (1, 1), (1, 2)], LEG_1[::-1][:0] + [(3, 2), (2, 2), (1, 2)]]   # at THEN: from the north + the carried
H_LANES = [[(1, 2), (1, 3), (1, 4), (1, 5)], [(4, 5), (3, 5), (2, 5), (1, 5)]]

T_PATHS = [LANE_A + [TARGET], LANE_B + [TARGET]]
SLOT_MAKO = DR.slots_of(TARGET, T_PATHS, TARGET)[0]
SLOT_NYX = DR.slots_of(THEN, T_PATHS, TARGET, supporter=True)[0]
T_SLOTS = sorted(set(SLOT_MAKO) | set(SLOT_NYX), key=DR.cid)
N_SLOTS = DR.slots_of(THEN, [N_LANES[0] + [THEN], N_LANES[1] + [THEN]], THEN)[0]
H_SLOTS = DR.slots_of(HQ, [H_LANES[0] + [HQ], H_LANES[1] + [HQ]], HQ)[0]
print('target slots', [G.name(*c) for c in T_SLOTS], 'MAKO', len(SLOT_MAKO), 'NYX', len(SLOT_NYX))
print('then slots', [G.name(*c) for c in N_SLOTS], 'hq slots', [G.name(*c) for c in H_SLOTS])

DOCK_R1 = {'NYX': (2, 1)}                # NYX's SMG docked on c2 (the supporter docks on its own side)
DEV_R1 = {(4, 4): 'BARRICADE'}           # a barricade holds e5 (one piece per slot)
HOVER = (4, 3)                           # MAKO's RAIL held over e4
REACH_HOVER = [(4, 2), (4, 4), (4, 5), (3, 2), (5, 3)]  # what the rail hits from e4 (reach 2 down the lanes, drawn on cells)


def P(c, lift=0.0):
    return G.cc(c[0], c[1], lift)


# ================================================================== base
def base(dim=1.0):
    """city_plate (the native capture at the raid camera), pushed bolder: more contrast, the neon back"""
    cp = V.city_plate(dim * 1.08)
    arr = np.asarray(cp.convert('RGB')).astype(np.float32) / 255
    lum = arr @ np.array([.299, .587, .114], np.float32)
    arr = np.clip((arr - .5) * 1.18 + .5 + (arr - lum[..., None]) * .45, 0, 1)
    img = Image.fromarray((arr * 255).astype(np.uint8)).convert('RGBA').resize((W * K, H * K), Image.LANCZOS)
    return img


def ground(img, fn):
    """draw a set 8 ground mark (masked to the street) on its own overlay and composite"""
    ov = V.blank(); fn(ov); img.alpha_composite(ov)


def lane_tint(img, cells, entry, end, col=(255, 60, 70)):
    ground(img, lambda ov: V.route_ground(ov, cells, entry, end, col))


def lanes_ground(img, lanes):
    for cells, ent, end in lanes:
        lane_tint(img, cells, ent, end)


def lane_pencil(img, cells, entry, end, col=RED, w=7, seed=3):
    pts = V.route_line(cells, entry, end, k=.55)
    arrow_hand(img, pts, col, w, head=20, seed=seed)


def lane_letter(img, entry, letter, col=RED):
    x, y = P(entry)
    ellipse(img, [x - 22, y - 22, x + 22, y + 22], fill=INK, outline=col, width=4)
    text(img, (x, y + 1), letter, font('anton', 30), WHITE, 'mm')


def wave_stack(img, entry, units, dx=0, dy=-64):
    """the incoming wave of this round, per street: unit icons (v4) with counts, above the lane's entry (exact, nothing hidden)"""
    x, y = P(entry)
    n = len(units)
    w = 74 * n + 16
    rrect(img, [x + dx - w / 2, y + dy - 40, x + dx + w / 2, y + dy + 40], 14, fill=(10, 14, 26, 235), outline=(236, 250, 248, 200), width=2)
    for k, (kind, cnt) in enumerate(units):
        ux = x + dx - w / 2 + 16 + 37 + k * 74
        ico = V.icon_img(kind, 1.0, 17, True)
        img.alpha_composite(ico, (int(S(ux) - ico.width / 2), int(S(y + dy - 8) - ico.height / 2)))
        text(img, (ux, y + dy + 26), 'x%d' % cnt, font('anton', 24), WHITE, 'mm')


def stop_mark(img, cell, kind, label=None, current=False):
    """route stop marks on the building: TARGET (corp red crosshair ring), THEN (white dashed ring), END (HQ heart),
    FELL (red strike over the ring), HELD (lime ring + tick)"""
    x, y = P(cell, lift=7)
    if current:
        for r_, a in ((92, 70), (76, 140)):
            ellipse(img, [x - r_, y - r_ * .62, x + r_, y + r_ * .62], outline=(255, 70, 80, a), width=5)
    if kind in ('TARGET', 'FELL'):
        ellipse(img, [x - 54, y - 34, x + 54, y + 34], outline=RED, width=7)
        for a in (0, 90, 180, 270):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            line(img, [(x + ca * 40, y + sa * 25), (x + ca * 66, y + sa * 41)], RED, 6)
    elif kind == 'THEN':
        for a0 in range(0, 360, 24):
            pts = [(x + 52 * math.cos(math.radians(a)), y + 33 * math.sin(math.radians(a))) for a in range(a0, a0 + 14, 2)]
            line(img, pts, WHITE, 5)
    elif kind == 'END':
        poly(img, shape_pts('hex', x, y - 6, 40), fill=INK)
        poly(img, shape_pts('hex', x, y - 6, 34), fill=PINK, outline=WHITE, width=3)
        put_glyph(img, 'picto_hp', x, y - 6, 38, WHITE)
    elif kind == 'HELD':
        ellipse(img, [x - 54, y - 34, x + 54, y + 34], outline=LIME, width=7)
    if kind == 'FELL':
        cross(img, x, y, 70, RED, 11)
    if kind == 'HELD':
        tick(img, x - 22, y, 46, LIME, 9)
    if label:
        f = font('anton', 30)
        col = {'TARGET': RED, 'FELL': RED, 'THEN': WHITE, 'END': PINK, 'HELD': LIME}[kind]
        fg = WHITE if kind in ('TARGET', 'FELL', 'END') else INK
        wl = tw(label, f) + 28
        lx = x - 70 if cell == TARGET else x
        rrect(img, [lx - wl / 2, y - 98, lx + wl / 2, y - 58], 8, fill=col, outline=INK, width=3)
        text(img, (lx, y - 78), label, f, fg, 'mm')


def route_dots(img, cells, col=WHITE, gap=18, r=7, struck=False, start=None, end=None):
    """the raid's route from stop to stop: a bold dotted line along the street cells (ink-edged dots), arrow into the next stop"""
    pts = [P(c) for c in cells]
    if start:
        pts = [start] + pts
    if end:
        pts = pts + [end]
    seg = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / gap))
        seg += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    for (x, y) in seg[1:]:
        ellipse(img, [x - r - 2, y - r - 2, x + r + 2, y + r + 2], fill=INK)
        ellipse(img, [x - r, y - r, x + r, y + r], fill=GREY if struck else col)
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    a = math.atan2(y1 - y0, x1 - x0)
    tip = (x1 - 30 * math.cos(a), y1 - 30 * math.sin(a))
    poly(img, [tip, (tip[0] - 26 * math.cos(a - .5), tip[1] - 26 * math.sin(a - .5)), (tip[0] - 26 * math.cos(a + .5), tip[1] - 26 * math.sin(a + .5))],
         fill=GREY if struck else col, outline=INK, width=3)


def post(img, oid, cell, alpha=1.0):
    ov = V.blank(); D.beacon(ov, oid, cell[0], cell[1], alpha=alpha); img.alpha_composite(ov)


def docked(img, oid, cell, stars=None):
    ov = V.blank()
    D.pad(ov, oid, cell); D.docked(ov, oid, cell, stars)
    img.alpha_composite(ov)


def tether(img, oid, cell, bcell, bow=.16):
    ov = V.blank(); D.tether(ov, oid, cell, bcell, bow); img.alpha_composite(ov)


def dev_on(img, cell, kind):
    x, y = P(cell)
    RK.stick(img, C.dev_c(kind), x, y - 8, -14, scale=.5)


def slots(img, cells, lit=()):
    ground(img, lambda ov: D.slots(ov, cells, lit=lit))


def share_pill(img, oid, x, y):
    """supporter share: a link pill in the supporter's colour, the value left open (N %: a still-moving number)"""
    top = OCOL[oid]
    rrect(img, [x - 62, y - 17, x + 62, y + 17], 17, fill=INK, outline=top + (255,), width=3)
    ellipse(img, [x - 52, y - 11, x - 30, y + 11], fill=(70, 70, 86, 255), outline=WHITE, width=2)
    img_d = ImageDraw.Draw(img)
    img_d.pieslice(S([x - 52, y - 11, x - 30, y + 11]), -90, 0, fill=top + (255,))
    text(img, (x - 4, y), 'N%', font('anton', 24), WHITE, 'mm')
    for ox in (-6, 6):
        ellipse(img, [x + 34 + ox - 8, y - 6, x + 34 + ox + 8, y + 6], outline=WHITE, width=2)


def unit_on(img, kind, cell, hp=1.0, count=None, dx=0, dy=0, alpha=1.0, pips=()):
    x, y = P(cell)
    ov = V.blank(); V.unit(ov, kind, x + dx, y + dy, hp=hp, count=count, alpha=alpha, pips=pips); img.alpha_composite(ov)


def kill_bits(img, kind, cell, dx=0, dy=0, seed=3):
    x, y = P(cell)
    ov = V.blank(); V.unit_bits(ov, kind, x + dx, y + dy, seed=seed); img.alpha_composite(ov)


def shot(img, a, b, col):
    (x0, y0), (x1, y1) = a, b
    gl = Image.new('RGBA', img.size, (0, 0, 0, 0))
    line(gl, [(x0, y0 - 24), (x1, y1 - 30)], col[:3] + (255,), 9)
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(S(5))))
    line(img, [(x0, y0 - 24), (x1, y1 - 30)], (255, 255, 255, 255), 3)


def reach_cells(img, cells, col):
    """weapon reach on the street: the cells it hits, hatched in the owner's colour (pencil), no panel"""
    for c in cells:
        q = G.quad(c[0], c[1], .1)
        poly(img, q, fill=col[:3] + (60,))
        for t in np.linspace(.15, .85, 5):
            a = (q[0][0] + (q[1][0] - q[0][0]) * t, q[0][1] + (q[1][1] - q[0][1]) * t)
            b = (q[3][0] + (q[2][0] - q[3][0]) * t, q[3][1] + (q[2][1] - q[3][1]) * t)
            pencil_line(img, [a, b], col[:3] + (255,), 3, seed=int(t * 100) + c[0] * 7 + c[1])
        pencil_line(img, q + [q[0]], col[:3] + (255,), 4, seed=c[0] * 13 + c[1])


# ================================================================== chrome
def hq_tape(img, hq=20, of=20, lost=0, x=24, y=20):
    """HQ integrity: the heart and a segmented tape, the lost segments struck red (a number only when it is real)"""
    rrect(img, [x, y, x + 470, y + 64], 10, fill=PAPER, outline=INK, width=3)
    put_glyph(img, 'picto_hp', x + 34, y + 32, 40, PINK)
    for k in range(of):
        sx = x + 66 + k * 15.5
        live = k < hq
        hit = hq <= k < hq + lost
        rect(img, [sx, y + 16, sx + 11, y + 48], fill=(70, 200, 90, 255) if live else ((255, 60, 70, 255) if hit else (190, 186, 176, 255)),
             outline=INK, width=1)
        if hit:
            line(img, [(sx - 2, y + 50), (sx + 13, y + 14)], INK, 3)
    text(img, (x + 456, y + 33), '%d/%d' % (hq, of) if not lost else '%d' % (hq,), font('anton', 36), RED if lost else INK, 'rm')


def heat_chip(img, heat=50, x=24, y=110):
    rrect(img, [x, y, x + 150, y + 54], 10, fill=NAVY, outline=CYAN, width=2)
    put_glyph(img, 'placeholder_burn', x + 30, y + 27, 32, (255, 120, 40, 255))
    text(img, (x + 60, y + 27), str(heat), font('anton', 36), WHITE, 'lm')


def credits_chip(img, cr, x=190, y=110, delta=None):
    rrect(img, [x, y, x + 190, y + 54], 10, fill=NAVY, outline=CYAN, width=2)
    ellipse(img, [x + 12, y + 11, x + 44, y + 43], fill=YEL, outline=INK, width=3)
    text(img, (x + 28, y + 28), '$', font('anton', 22), INK, 'mm')
    text(img, (x + 58, y + 27), str(cr), font('anton', 36), WHITE, 'lm')
    if delta:
        text(img, (x + 120, y + 27), delta, font('anton', 30), LIME, 'lm')


def stop_banner(img, stops, cur, x=700, y=18):
    """top centre: the route as three chips, TARGET > THEN > END, the current one lit, fallen ones struck"""
    f = font('anton', 30)
    rrect(img, [x - 20, y, x + 560, y + 66], 12, fill=NAVY, outline=CYAN, width=2)
    text(img, (x, y + 33), 'STOP %d/3' % (cur + 1), font('anton', 30), CYAN, 'lm')
    xx = x + 140
    for k, (lab, st) in enumerate(stops):
        wl = tw(lab, f) + 26
        fill = {'cur': RED, 'fell': (60, 60, 72, 255), 'next': INK, 'held': LIME, 'end': INK}[st]
        edge = {'cur': WHITE, 'fell': GREY, 'next': WHITE, 'held': INK, 'end': PINK}[st]
        rrect(img, [xx, y + 12, xx + wl, y + 54], 8, fill=fill, outline=edge, width=3)
        text(img, (xx + wl / 2, y + 33), lab, f, INK if st == 'held' else (GREY if st == 'fell' else WHITE), 'mm')
        if st == 'fell':
            line(img, [(xx + 4, y + 50), (xx + wl - 4, y + 16)], RED, 5)
        xx += wl
        if k < len(stops) - 1:
            text(img, (xx + 16, y + 33), '>', font('anton', 34), WHITE, 'mm')
            xx += 32


def crew_col(img, states, x=40, y=210):
    """the crew as their vinyl stickers, two by two, one short mark each: HERE (the post at this stop), HELPS (supporter),
    AT HQ, OFF (not in this fight), FELL BACK"""
    pos = [(x + 88, y + 70), (x + 300, y + 70), (x + 88, y + 270), (x + 300, y + 270)]
    for (oid, st), (cx, cy) in zip(states, pos):
        grey = st in ('OFF', 'FELL BACK')
        RK.stick(img, C.op_c(oid, grey=grey), cx, cy, -4 if cx < x + 200 else 4, scale=.78)
        RK.stick(img, C.wpn_c(RK.OPS[oid]['wpn'], RK.OPS[oid]['stars']), cx + 62, cy - 54, 8, scale=.5)
        col = {'HERE': RED, 'HELPS': OCOL[oid] + (255,), 'AT HQ': PINK, 'OFF': GREY, 'FELL BACK': AMB, 'DEFENDS': PINK}[st]
        f = font('anton', 24)
        wl = tw(st, f) + 22
        rrect(img, [cx - wl / 2, cy + 74, cx + wl / 2, cy + 106], 7, fill=col, outline=INK, width=3)
        text(img, (cx, cy + 90), st, f, WHITE if st not in ('HELPS',) else INK, 'mm')


def big_sticker(img, label, cx, cy, fill, fg=INK, w=None, h=96, rot=-4, size=68):
    w = w or tw(label, font('anton', size)) + 70
    sticker(img, label, cx, cy, w, h, fill, fg, rot=rot, size=size)


def button(img, label, cx, cy, fill=PINK, fg=WHITE, key=None):
    big_sticker(img, label, cx, cy, fill, fg, h=74, size=50, rot=-3)
    if key:
        chip(img, cx - 40, cy + 54, key, font('mono', 18), WHITE, NAVY, CYAN)


def forecast_strip(img, items, box=(560, 960, 1360, 1018)):
    """the exact forecast, one line of glyphs and numbers: per lane, then the verdict (and only then where it goes next)"""
    x0, y0, x1, y1 = box
    rrect(img, box, 12, fill=NAVY, outline=CYAN, width=2)
    x = x0 + 20
    cy = (y0 + y1) / 2
    for it in items:
        k = it[0]
        if k == 'lane':
            ellipse(img, [x, cy - 17, x + 34, cy + 17], fill=INK, outline=RED, width=3)
            text(img, (x + 17, cy + 1), it[1], font('anton', 22), WHITE, 'mm'); x += 44
        elif k == 'ico':
            ico = V.icon_img(it[1], 1.0, 12, True)
            img.alpha_composite(ico, (int(S(x + 16) - ico.width / 2), int(S(cy) - ico.height / 2))); x += 36
        elif k == 'glyph':
            put_glyph(img, it[1], x + 16, cy, 30, it[2]); x += 38
        elif k == 'txt':
            f = font('anton', 30)
            text(img, (x, cy), it[1], f, it[2], 'lm'); x += tw(it[1], f) + 10
        elif k == 'sep':
            text(img, (x + 8, cy), '.', font('anton', 30), DIM, 'mm'); x += 22
        elif k == 'verdict':
            f = font('anton', 30)
            wl = tw(it[1], f) + 24
            rrect(img, [x, cy - 21, x + wl, cy + 21], 8, fill=it[2], outline=INK, width=3)
            text(img, (x + wl / 2, cy + 1), it[1], f, INK if it[2] in (LIME, YEL) else WHITE, 'mm'); x += wl + 10


def corp_order(img, x=1500, y=26, rot=3):
    """the one corp document: the intercepted raid order, folded small (seal, heat, the route in three words)"""
    L = layer(380, 230)
    paper(L, (20, 20, 360, 210), col=PAPER, edge=True, clip=True, seed=5)
    text(L, (44, 46), 'SOLACE', font('anton', 34), CORP_INK)
    text(L, (44, 88), 'RAID ORDER . HEAT 50', font('mono', 20), INK)
    text(L, (44, 122), 'D4 > A3 > HQ', font('anton', 40), INK)
    stamp(L, 'INTERCEPTED', 250, 186, RED, rot=-4, size=22)
    rotate_paste(img, L, x + 180, y + 110, rot)


def armory(img, x=1420, y=200, w=480, h=560, resupply=False):
    """ARMORY before round 1 (big: weapons, devices, reroll, the bank) vs RESUPPLY between rounds (two offers, no reroll)"""
    if resupply:
        glass(img, (x, y, x + w, y + 300), edge=AMB, fill=(26, 18, 6, 240), ticks=True)
        text(img, (x + 24, y + 22), 'RESUPPLY', font('anton', 48), AMB)
        text(img, (x + 26, y + 82), 'pick 1 of 2', font('marker', 26), WHITE)
        RK.stick(img, C.wpn_c('SHOTGUN', 1, cost=3), x + 120, y + 190, -4, scale=.9)
        RK.stick(img, C.dev_c('MINE', cost=2), x + 350, y + 190, 5, scale=.72)
        return
    glass(img, (x, y, x + w, y + h), edge=LIME, fill=(8, 20, 12, 242), ticks=True)
    text(img, (x + 24, y + 20), 'ARMORY', font('anton', 56), LIME)
    text(img, (x + 270, y + 46), 'before round 1', font('marker', 22), WHITE)
    offers = [('w', 'RAIL', 1, 4), ('w', 'SMG', 1, 3), ('w', 'SHOTGUN', 2, 5), ('w', 'JAMMER', 1, 3)]
    for k, (_, nm, st, cost) in enumerate(offers):
        cx = x + 128 + (k % 2) * 228; cy = y + 150 + (k // 2) * 100
        RK.stick(img, C.wpn_c(nm, st, cost=cost), cx, cy, (-1) ** k * 3, scale=.82)
    for k, (dv, cost) in enumerate((('BARRICADE', 2), ('MINE', 2))):    # TAR / SHOCK / GATE have no sticker glyph yet (glyph review 4)
        cx = x + 128 + k * 228; cy = y + 380
        RK.stick(img, C.dev_c(dv, cost=cost), cx, cy, (-1) ** k * 4, scale=.62)
    rrect(img, [x + 24, y + 470, x + 190, y + 528], 10, fill=NAVY, outline=CYAN, width=2)
    put_glyph(img, 'picto_again', x + 56, y + 499, 34, WHITE)
    text(img, (x + 92, y + 499), '2', font('anton', 34), YEL, 'lm')
    rrect(img, [x + 210, y + 470, x + 456, y + 528], 10, fill=NAVY, outline=CYAN, width=2)
    ellipse(img, [x + 224, y + 483, x + 256, y + 515], fill=YEL, outline=INK, width=3)
    text(img, (x + 240, y + 500), '$', font('anton', 22), INK, 'mm')
    text(img, (x + 270, y + 499), '12', font('anton', 36), WHITE, 'lm')


def slot_count(img, used, total, x, y):
    """scarcity, said once: the slot tile glyph, used / total"""
    rrect(img, [x, y, x + 178, y + 54], 10, fill=NAVY, outline=CYAN, width=2)
    q = [(x + 32, y + 12), (x + 56, y + 27), (x + 32, y + 42), (x + 8, y + 27)]
    poly(img, q, fill=(92, 225, 255, 60), outline=CYAN, width=3)
    text(img, (x + 70, y + 27), '%d/%d' % (used, total), font('anton', 36), WHITE, 'lm')


def label_tag(img, x, y, s, col=WHITE, size=28):
    f = font('marker', size)
    wl = tw(s, f) + 20
    rrect(img, [x - 10, y - size * .75, x + wl - 10, y + size * .75], 6, fill=(8, 10, 18, 215))
    text(img, (x, y), s, f, col, 'lm')


def caption(img, s):
    frame_caption(img, s)


def save(img, name):
    img = vignette(img, .3)
    out = img.convert('RGB').resize((W, H), Image.LANCZOS)
    out.save(OUTR + name)
    print('wrote raid/' + name)
    return out


# ================================================================== the five moments
def common_route(img, cur, fell=(), held=()):
    """route + stop marks; cur = index of the stop being fought (0 target, 1 then, 2 HQ)"""
    route_dots(img, LEG_1[1:], col=WHITE, struck=0 in held, start=P(TARGET, 7), end=P(THEN, 4))
    route_dots(img, LEG_2[1:], col=WHITE, struck=0 in held, start=P(THEN, 7), end=P(HQ, 4))
    for k, (cell, kind, lab) in enumerate(((TARGET, 'TARGET', 'TARGET'), (THEN, 'THEN', 'THEN'), (HQ, 'END', 'END . HQ'))):
        if k in fell:
            stop_mark(img, cell, 'FELL', 'FELL')
        elif k in held:
            stop_mark(img, cell, 'HELD', 'HELD')
        else:
            stop_mark(img, cell, kind, lab, current=(k == cur))


def plate_a():
    """(a) REVIEW: the city with the raid announced and its route: TARGET > THEN > END at our HQ; the wave per street"""
    img = base()
    lanes_ground(img, [(LANE_A, ENT_A, TARGET), (LANE_B, ENT_B, TARGET)])
    lane_pencil(img, LANE_A, ENT_A, TARGET, seed=3); lane_pencil(img, LANE_B, ENT_B, TARGET, seed=5)
    post(img, 'MAKO', TARGET); post(img, 'NYX', THEN); post(img, 'URSA', HQ)
    common_route(img, 0)
    lane_letter(img, ENT_A, 'A'); lane_letter(img, ENT_B, 'B')
    wave_stack(img, ENT_A, [('trooper', 3), ('riot', 1), ('bike', 2)], dx=180, dy=-6)
    wave_stack(img, ENT_B, [('drone', 2), ('heavy', 1)], dx=150, dy=10)
    # forecast, pencil, on the city: falls in round 3, 3 walk on to A3; HQ safe
    label_tag(img, 1010, 520, 'falls R3', RED, 32)
    label_tag(img, 960, 268, '3 walk on', YEL, 30)
    label_tag(img, 470, 520, 'HQ safe', LIME, 30)
    hq_tape(img); heat_chip(img); credits_chip(img, 12)
    stop_banner(img, [('D4', 'cur'), ('A3', 'next'), ('HQ', 'end')], 0)
    corp_order(img)
    crew_col(img, [('MAKO', 'HERE'), ('NYX', 'HELPS'), ('URSA', 'AT HQ'), ('OZZY', 'OFF')], y=620)
    big_sticker(img, 'RAID INCOMING', 1600, 440, RED, WHITE, rot=-5, size=64)
    forecast_strip(img, [('lane', 'A'), ('ico', 'trooper'), ('txt', '3', WHITE), ('ico', 'riot'), ('txt', '1', WHITE), ('ico', 'bike'), ('txt', '2', WHITE),
                         ('sep',), ('lane', 'B'), ('ico', 'drone'), ('txt', '2', WHITE), ('ico', 'heavy'), ('txt', '1', WHITE), ('sep',),
                         ('verdict', 'FALLS R3', RED), ('txt', '> A3 x3', YEL)])
    button(img, 'TO THE ARMORY', 1700, 1000, LIME, INK, key='SPACE')
    caption(img, 'B-107 RAID 1 REVIEW = brief (a): the city, the raid announced, its route TARGET > THEN > END at our HQ')
    return save(img, 'raid_a_review_route.png')


def plate_b():
    """(b) SHOP + PLACE: setup at the target, the Armory open, MAKO's rail held: its free slots lit, one hovered with its reach"""
    img = base()
    lanes_ground(img, [(LANE_A, ENT_A, TARGET), (LANE_B, ENT_B, TARGET)])
    used = set(DOCK_R1.values()) | set(DEV_R1)
    lit = [c for c in SLOT_MAKO if c not in used]
    slots(img, T_SLOTS, lit=lit)
    lane_pencil(img, LANE_A, ENT_A, TARGET, seed=3); lane_pencil(img, LANE_B, ENT_B, TARGET, seed=5)
    reach_cells(img, REACH_HOVER, OCOL['MAKO'])
    post(img, 'MAKO', TARGET, alpha=.5); post(img, 'NYX', THEN, alpha=.5)
    tether(img, 'NYX', DOCK_R1['NYX'], THEN)
    docked(img, 'NYX', DOCK_R1['NYX'])
    x, y = P(DOCK_R1['NYX']); share_pill(img, 'NYX', x + 96, y + 30)
    for c, dv in DEV_R1.items():
        dev_on(img, c, dv)
    hx, hy = P(HOVER)
    pencil_circle(img, hx, hy, 50, 32, YEL, 6)
    hand(img, (hx + 40, hy - 70), '+2', 44, YEL)
    RK.stick(img, C.wpn_c('RAIL', 2), hx + 70, hy + 70, 8, scale=1.0, lift=14)       # the held card, lifted
    stop_mark(img, TARGET, 'TARGET', 'TARGET', current=True)
    lane_letter(img, ENT_A, 'A'); lane_letter(img, ENT_B, 'B')
    wave_stack(img, ENT_A, [('trooper', 3), ('riot', 1), ('bike', 2)], dx=180, dy=-6)
    wave_stack(img, ENT_B, [('drone', 2), ('heavy', 1)], dx=150, dy=10)
    hq_tape(img); heat_chip(img); credits_chip(img, 12)
    stop_banner(img, [('D4', 'cur'), ('A3', 'next'), ('HQ', 'end')], 0)
    slot_count(img, len(used), len(T_SLOTS), 1236, 104)
    crew_col(img, [('MAKO', 'HERE'), ('NYX', 'HELPS'), ('URSA', 'AT HQ'), ('OZZY', 'OFF')], y=620)
    armory(img)
    forecast_strip(img, [('txt', 'R1', CYAN), ('lane', 'A'), ('glyph', 'placeholder_shield', LIME), ('txt', '0', LIME), ('sep',),
                         ('lane', 'B'), ('glyph', 'raid_leak', RED), ('txt', '1', RED), ('sep',), ('verdict', 'HOLDS', LIME),
                         ('txt', 'with rail: B 0', YEL)])
    button(img, 'SEND IT', 1700, 1000, PINK, WHITE, key='SPACE')
    caption(img, 'B-107 RAID 2 SHOP + 3 PLACE = brief (b): setup at the target, ARMORY open, a weapon held: its free slots lit')
    return save(img, 'raid_b_setup_armory.png')


def plate_c():
    """(c) EXECUTE: a round running; shots leave the docked guns; the exact forecast says this round holds, the next falls"""
    img = base()
    lanes_ground(img, [(LANE_A, ENT_A, TARGET), (LANE_B, ENT_B, TARGET)])
    lane_pencil(img, LANE_A, ENT_A, TARGET, seed=3); lane_pencil(img, LANE_B, ENT_B, TARGET, seed=5)
    post(img, 'MAKO', TARGET); post(img, 'NYX', THEN)
    tether(img, 'NYX', DOCK_R1['NYX'], THEN)
    docked(img, 'MAKO', HOVER); docked(img, 'NYX', DOCK_R1['NYX'])
    for c, dv in DEV_R1.items():
        dev_on(img, c, dv)
    # units on the lanes (round 2): A held at the barricade, B coming down street c
    unit_on(img, 'trooper', (4, 5), hp=.6, dx=-10); unit_on(img, 'riot', (5, 5), hp=1.0, dx=10)
    unit_on(img, 'heavy', (2, 0), hp=.8); unit_on(img, 'drone', (2, 1), hp=.35, pips=('J',))
    kill_bits(img, 'bike', (4, 4), dx=-30, dy=-10, seed=5)
    shot(img, P(HOVER), P((4, 5)), OCOL['MAKO']); shot(img, P(DOCK_R1['NYX']), P((2, 1)), OCOL['NYX'])
    common_route(img, 0)
    hq_tape(img); heat_chip(img); credits_chip(img, 6)
    stop_banner(img, [('D4', 'cur'), ('A3', 'next'), ('HQ', 'end')], 0)
    crew_col(img, [('MAKO', 'HERE'), ('NYX', 'HELPS'), ('URSA', 'AT HQ'), ('OZZY', 'OFF')], y=620)
    # tick bar and round chips (glass, top right)
    glass(img, (1440, 110, 1890, 230), edge=CYAN, fill=NAVY)
    text(img, (1462, 128), 'ROUND 2/3', font('anton', 40), WHITE)
    for k in range(8):
        rect(img, [1462 + k * 52, 186, 1506 + k * 52, 212], fill=CYAN if k < 5 else (40, 50, 70, 255), outline=INK, width=2)
    for k, sp in enumerate(('1x', '2x', 'END')):
        rrect(img, [1450 + k * 150, 250, 1580 + k * 150, 300], 8, fill=CYAN if k == 1 else NAVY, outline=CYAN, width=2)
        text(img, (1515 + k * 150, 275), sp, font('anton', 28), INK if k == 1 else WHITE, 'mm')
    forecast_strip(img, [('txt', 'R2', CYAN), ('verdict', 'HOLDS', LIME), ('glyph', 'raid_kills', WHITE), ('txt', '4/6', WHITE), ('sep',),
                         ('txt', 'R3', CYAN), ('verdict', 'FALLS', RED), ('txt', '> A3 x3', YEL)], box=(520, 960, 1400, 1018))
    caption(img, 'B-107 RAID 4 EXECUTE = brief (c): a round running, the exact forecast (this round holds; R3 falls, 3 walk on)')
    return save(img, 'raid_c_round_running.png')


def plate_d():
    """(d) the site falls; the raid walks on with its survivors to the next stop; a small fight starts there (RESUPPLY)"""
    img = base()
    lanes_ground(img, [(N_LANES[0], (1, -1), THEN), ([(3, 2), (2, 2), (1, 2)], (4, 2), THEN)])
    slots(img, N_SLOTS)
    post(img, 'MAKO', TARGET, alpha=.35); post(img, 'NYX', THEN)
    common_route(img, 1, fell=(0,))
    # MAKO falls back alive (to HQ): an amber pencil arrow from the dim post
    tx, ty = P(TARGET, 9)
    arrow_hand(img, [(tx - 20, ty + 40), (820, 560), (650, 470)], AMB, 6, head=20, seed=9)
    label_tag(img, 760, 600, 'MAKO falls back', AMB, 26)
    # the carried survivors on the route, with the carry mark (count + chevrons)
    for k, (kind, cell, dx) in enumerate((('riot', (2, 2), -10), ('heavy', (2, 2), 30), ('trooper', (3, 2), 0))):
        unit_on(img, kind, cell, hp=(.7, .5, .4)[k], dx=dx, dy=(-6, 8, 0)[k])
    cx, cy = P((2, 2))
    rrect(img, [cx - 4, cy + 26, cx + 130, cy + 66], 10, fill=AMB, outline=INK, width=3)
    text(img, (cx + 63, cy + 46), 'x3 carried', font('anton', 26), INK, 'mm')
    # the new stop's own wave from the north (not yet played)
    lane_letter(img, (1, -1), 'C')
    wave_stack(img, (1, -1), [('trooper', 2), ('bike', 1)], dx=150, dy=10)
    hq_tape(img); heat_chip(img); credits_chip(img, 7)
    stop_banner(img, [('D4', 'fell'), ('A3', 'cur'), ('HQ', 'end')], 1)
    crew_col(img, [('MAKO', 'FELL BACK'), ('NYX', 'HERE'), ('URSA', 'AT HQ'), ('OZZY', 'OFF')], y=620)
    armory(img, resupply=True)
    big_sticker(img, 'D4 FELL', 1290, 360, RED, WHITE, rot=-7, size=60)
    forecast_strip(img, [('txt', 'A3', CYAN), ('glyph', 'raid_kills', WHITE), ('txt', '3+3', WHITE), ('sep',), ('verdict', 'HOLDS', LIME),
                         ('txt', 'HQ safe', LIME)], box=(560, 960, 1360, 1018))
    button(img, 'SEND IT', 1700, 1000, PINK, WHITE, key='SPACE')
    caption(img, 'brief (d): the site falls, the raid walks on with its 3 survivors; a small fight at A3 (RESUPPLY, 2 offers)')
    return save(img, 'raid_d_site_falls.png')


def plate_e():
    """(e) the HQ stop: only HQ-stationed operatives defend; every unit that gets in costs 1 HQ integrity"""
    img = base()
    lanes_ground(img, [(H_LANES[0], (1, 1), HQ), (H_LANES[1], (5, 5), HQ)])
    slots(img, H_SLOTS)
    post(img, 'URSA', HQ); post(img, 'MAKO', TARGET, alpha=.3); post(img, 'NYX', THEN, alpha=.35)
    docked(img, 'URSA', (1, 4))
    common_route(img, 2, fell=(0, 1))
    hx, hy = P(HQ, 7)
    # units getting in: each one a -1 off the HQ tape, red bursts on the door
    for k, (kind, dx, dy) in enumerate((('riot', -40, 10), ('heavy', 10, -20), ('trooper', 56, 6))):
        unit_on(img, kind, H_CORE, hp=.5, dx=dx, dy=dy, alpha=.85)
    gl = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ellipse(gl, [hx - 130, hy - 80, hx + 130, hy + 80], fill=(255, 30, 50, 140))
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(S(26))))
    for k, (dx, dy) in enumerate(((-70, -120), (0, -150), (70, -118))):
        big_sticker(img, '-1', hx + dx + 40, hy + dy - 40, RED, WHITE, w=86, h=70, rot=(-8, 4, 10)[k], size=50)
    unit_on(img, 'bike', (2, 5), hp=.0, alpha=.0)
    kill_bits(img, 'bike', (2, 5), seed=11)
    shot(img, P((1, 4)), P((2, 5)), OCOL['URSA'])
    hq_tape(img, 17, 20, lost=3)
    big_sticker(img, 'HQ -3', 330, 140, RED, WHITE, rot=-6, size=56, h=84)
    heat_chip(img, 50, x=24, y=200); credits_chip(img, 9, x=190, y=200)
    stop_banner(img, [('D4', 'fell'), ('A3', 'fell'), ('HQ', 'cur')], 2)
    crew_col(img, [('URSA', 'DEFENDS'), ('MAKO', 'FELL BACK'), ('NYX', 'FELL BACK'), ('OZZY', 'OFF')], y=620)
    label_tag(img, 1080, 620, 'HQ crew only', WHITE, 26)
    forecast_strip(img, [('txt', 'HQ', PINK), ('glyph', 'raid_leak', RED), ('txt', '3 in', RED), ('sep',), ('glyph', 'picto_hp', PINK),
                         ('txt', '20 > 17', RED), ('sep',), ('glyph', 'raid_kills', WHITE), ('txt', '1', WHITE)], box=(560, 960, 1360, 1018))
    caption(img, 'brief (e): the HQ stop. URSA (stationed at HQ) defends alone; 3 units get in: HQ integrity 20 > 17, one per unit')
    return save(img, 'raid_e_hq_stop.png')


def plate_result(lost=False):
    """RESULTS / REWARD: HOLD (the raid ends at the target, nothing lost, the pay flies to the HUD) or the lost variant
    stamped TARGET ACQUIRED in Solace's corporate ink (the corp's colour on what it took)"""
    img = base(.8 if lost else 1.0)
    if lost:
        for cell in (TARGET, THEN):
            x, y = P(cell, 6)
            gl = Image.new('RGBA', img.size, (0, 0, 0, 0))
            ellipse(gl, [x - 120, y - 80, x + 120, y + 80], fill=(40, 230, 150, 120))
            img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(S(20))))
        common_route(img, -1, fell=(0, 1))
        post(img, 'URSA', HQ)
        hq_tape(img, 16, 20, lost=4)
        stop_banner(img, [('D4', 'fell'), ('A3', 'fell'), ('HQ', 'cur')], 2)
        credits_chip(img, 7, delta='+7'); heat_chip(img, 50)
        crew_col(img, [('URSA', 'DEFENDS'), ('MAKO', 'FELL BACK'), ('NYX', 'FELL BACK'), ('OZZY', 'OFF')], y=620)
        corp_ink_stamp(img, 'TARGET ACQUIRED', 1080, 560, rot=-10, size=112)
        # what the corp took, as marks only: two site stickers in Solace teal, HQ -4
        for k, (lab, x) in enumerate((('D4', 1500), ('A3', 1690))):
            sticker(img, lab, x, 260, 150, 80, (40, 230, 150, 255), INK, rot=(-4, 5)[k], size=52)
            stamp(img, 'SOLACE', x, 330, CORP_INK, rot=-6, size=30)
        big_sticker(img, 'HQ -4', 1600, 470, RED, WHITE, rot=4, size=60, h=88)
        label_tag(img, 1440, 560, 'retake: tier easier', WHITE, 24)
        button(img, 'CONTINUE', 1700, 1000, WHITE, PINK, key='SPACE')
        caption(img, 'B-107 RAID 5 RESULT, lost: TARGET ACQUIRED in Solace ink; both stops fell, HQ 20 > 16, the crew alive, +7 kills')
        return save(img, 'raid_f_result_lost.png')
    lanes_ground(img, [(LANE_A, ENT_A, TARGET), (LANE_B, ENT_B, TARGET)])
    post(img, 'MAKO', TARGET); post(img, 'NYX', THEN)
    docked(img, 'MAKO', HOVER); docked(img, 'NYX', DOCK_R1['NYX'])
    for c, dv in DEV_R1.items():
        dev_on(img, c, dv)
    common_route(img, -1, held=(0,))
    for c in ((4, 5), (2, 1), (4, 3)):
        kill_bits(img, 'trooper', c, seed=c[0] * 3 + c[1])
    hq_tape(img); heat_chip(img, 47); credits_chip(img, 21, delta='+9')
    stop_banner(img, [('D4', 'held'), ('A3', 'next'), ('HQ', 'end')], 0)
    crew_col(img, [('MAKO', 'HERE'), ('NYX', 'HELPS'), ('URSA', 'AT HQ'), ('OZZY', 'OFF')], y=620)
    big_sticker(img, 'HELD', 1010, 170, LIME, INK, rot=-6, size=96, h=124)
    # the pay flies to where it lands: credits to the purse, XP to the crew, the salvage to the locker
    for (x, y, lab) in ((128, 600, '+2 XP'), (340, 600, '+1 XP')):
        rrect(img, [x - 56, y - 20, x + 56, y + 20], 8, fill=LIME, outline=INK, width=3)
        text(img, (x, y), lab, font('anton', 26), INK, 'mm')
    big_sticker(img, 'LEVEL UP', 200, 540, LIME, INK, rot=-5, size=36, h=56)
    RK.stick(img, C.wpn_c('SHOTGUN', 1), 1600, 330, -4, scale=1.0)
    label_tag(img, 1500, 420, 'salvage kept', LIME, 28)
    big_sticker(img, '+9', 480, 190, YEL, INK, rot=5, size=60, h=84)
    label_tag(img, 1440, 560, 'route called off', WHITE, 26)
    forecast_strip(img, [('glyph', 'raid_kills', WHITE), ('txt', '8/8', WHITE), ('sep',), ('glyph', 'raid_leak', LIME), ('txt', '0', LIME), ('sep',),
                         ('glyph', 'picto_hp', PINK), ('txt', '20/20', LIME), ('sep',), ('glyph', 'placeholder_burn', AMB), ('txt', '50 > 47', AMB)])
    button(img, 'CONTINUE', 1700, 1000, WHITE, PINK, key='SPACE')
    caption(img, 'B-107 RAID 5 RESULT, held: D4 HELD, the raid ends; +9 cr, XP to the crew, salvage kept; the rest of the route called off')
    return save(img, 'raid_f_result_held.png')


# ================================================================== the raid mark sheet
def plate_marks():
    """every raid mark at plate size, on the street they live on (crops of the district), one label each"""
    img = Image.new('RGBA', (W * K, H * K), (12, 13, 20, 255))
    text(img, (40, 26), 'RAID MARKS', font('anton', 64), LIME)
    text(img, (370, 52), 'v47 shape . v42 slots . Solace only . every mark at plate size', font('mono', 22), DIM)

    def tile(x, y, w, h, title, fn, crop):
        """a district crop with marks drawn by fn, pasted at (x, y)"""
        b = base()
        fn(b)
        cx0, cy0, cx1, cy1 = crop
        piece = b.crop(tuple(S([cx0, cy0, cx1, cy1]))).resize((S(w), S(h)), Image.LANCZOS)
        img.alpha_composite(piece, (S(x), S(y)))
        rect(img, [x, y, x + w, y + h], outline=GREY, width=2)
        rrect(img, [x, y + h - 40, x + w, y + h], 0, fill=(8, 10, 18, 230))
        text(img, (x + 12, y + h - 20), title, font('anton', 26), WHITE, 'lm')

    def m_slots(b):
        lit = [c for c in SLOT_MAKO if c not in set(DOCK_R1.values()) | set(DEV_R1)]
        slots(b, T_SLOTS, lit=lit[:3])
        docked(b, 'NYX', DOCK_R1['NYX'])
        for c, dv in DEV_R1.items():
            dev_on(b, c, dv)
        slot_count(b, 2, len(T_SLOTS), 1160, 330)
    tile(30, 110, 600, 300, 'SLOTS: empty . lit . weapon . device . 2/10', m_slots, (800, 250, 1400, 550))

    def m_reach(b):
        reach_cells(b, REACH_HOVER, OCOL['MAKO'])
        docked(b, 'MAKO', HOVER)
    tile(660, 110, 600, 300, 'WEAPON REACH on cells', m_reach, (840, 300, 1440, 600))

    def m_support(b):
        post(b, 'NYX', THEN); tether(b, 'NYX', DOCK_R1['NYX'], THEN); docked(b, 'NYX', DOCK_R1['NYX'])
        x, y = P(DOCK_R1['NYX']); share_pill(b, 'NYX', x - 70, y + 34)
        post(b, 'MAKO', TARGET)
    tile(1290, 110, 600, 300, 'POST . SUPPORTER LINK . share N%', m_support, (680, 140, 1280, 440))

    def m_route(b):
        common_route(b, 1, fell=(0,))
    tile(30, 440, 600, 300, 'ROUTE: TARGET/FELL . THEN . END', m_route, (480, 160, 1080, 460))

    def m_units(b):
        lanes_ground(b, [(LANE_A, ENT_A, TARGET)])
        unit_on(b, 'trooper', (4, 5), hp=1.0); unit_on(b, 'riot', (5, 5), hp=.6); unit_on(b, 'heavy', (6, 5), hp=.4)
        unit_on(b, 'drone', (4, 4), hp=1.0, pips=('J',)); unit_on(b, 'bike', (4, 3), hp=.8, pips=('S',))
        kill_bits(b, 'trooper', (4, 2), seed=4)
        wave_stack(b, ENT_A, [('trooper', 3), ('riot', 1)], dx=-60, dy=-90)
    tile(660, 440, 600, 300, 'UNITS (v4) . HP . status . wave', m_units, (900, 330, 1500, 630))

    def m_hq(b):
        post(b, 'URSA', HQ)
        hx, hy = P(HQ, 7)
        unit_on(b, 'riot', H_CORE, hp=.5, dx=-30); unit_on(b, 'trooper', H_CORE, hp=.5, dx=30)
        for k, dx in enumerate((-50, 40)):
            big_sticker(b, '-1', hx + dx + 30, hy - 140, RED, WHITE, w=86, h=70, rot=(-6, 8)[k], size=50)
        stop_mark(b, HQ, 'END', None)
    tile(1290, 440, 600, 300, 'HQ DAMAGE: -1 per unit in', m_hq, (380, 110, 980, 410))

    # verdicts + devices + chrome (flat)
    y = 790
    text(img, (40, y), 'VERDICT', font('anton', 34), WHITE)
    for k, (lab, col) in enumerate((('HOLDS', LIME), ('FALLS', RED), ('HELD', LIME), ('FELL', RED))):
        x = 40 + k * 150
        rrect(img, [x, y + 50, x + 132, y + 98], 8, fill=col, outline=INK, width=3)
        text(img, (x + 66, y + 74), lab, font('anton', 32), INK if col == LIME else WHITE, 'mm')
    hq_tape(img, 17, 20, lost=3, x=40, y=y + 130)
    text(img, (680, y), 'STREET DEVICES (v42)', font('anton', 34), WHITE)
    for k, dv in enumerate(('BARRICADE', 'MINE', 'TAR', 'SHOCK', 'GATE')):
        x = 720 + k * 120
        ov = V.blank(); D.dev_badge(ov, dv, x, y + 90, r=30); img.alpha_composite(ov)
        text(img, (x, y + 150), dv, font('mono', 18), DIM, 'mm')
    text(img, (680, y + 190), 'no-mark = "device here" (slot refused)', font('mono', 18), DIM)
    text(img, (1340, y), 'REFUSALS . CHROME', font('anton', 34), WHITE)
    for k, kind in enumerate(('taken', 'far')):
        ov = V.blank(); D.refuse_badge(ov, kind, 1380 + k * 90, y + 80, r=24); img.alpha_composite(ov)
    text(img, (1340, y + 120), 'taken . too far', font('mono', 18), DIM)
    stop_banner(img, [('D4', 'fell'), ('A3', 'cur'), ('HQ', 'end')], 1, x=1340, y=y + 150)
    frame_caption(img, 'raid mark sheet (brief item 2): slots, reach, devices, units, supporter link, route stops, verdict, HQ damage')
    return save(img, 'raid_marks.png')


PLATES = dict(a=plate_a, b=plate_b, c=plate_c, d=plate_d, e=plate_e, hold=lambda: plate_result(False), lost=lambda: plate_result(True),
              marks=plate_marks)

if __name__ == '__main__':
    for k in (sys.argv[1:] or list(PLATES)):
        PLATES[k]()
