"""E10 drawing library = e9lib + the PL10 asks:
 1. landing chips become BEZEL ARCS spanning the unit's landing sectors (red diamonds = HP that gets through, per sector; small dots = turns until it lands),
 2. growth chevrons are SOLID (hit now) + HOLLOW (growth still to come), same size, never a ghost, on the arcs and on the unit bodies,
 3. the Adjuster is a body on its ring (gold diamond + HP bar), not a skull on the bezel,
 4. SHIELD slices carry a shield icon (cv_board passes glyph='SHIELD'),
 5. unit bodies are darkened / desaturated pink so the red chevrons pop (cell post-grade + muted kind colours).
 Plus the E10 rules: the Trigger-kill refund (gold burst + a RAM pip), the Twist cue. Every count comes from the frame dicts built by dump10.py."""
import sys, math, os
sys.dont_write_bytecode = True
from e9lib import *
import e9lib as E9
import cv_lib as CVL

# ----------------------------------------------------------------------------- muted unit palette (pink = unit screens only, darkened / desaturated)
KCOL.update({'Packet': (176, 92, 150), 'Worm': (146, 100, 182), 'Jammer': (130, 120, 196), 'Payload': (170, 104, 158), 'Ring': (170, 104, 158)})
KSCREEN = {'Packet': (0.30, 0.58), 'Worm': (0.30, 0.58), 'Jammer': (0.30, 0.58), 'Payload': (0.30, 0.58), 'Ring': (0.30, 0.58)}   # (saturation keep, brightness) of the screen texture
REDC = (255, 68, 51)
REG = {'arcs': [], 'bodies': [], 'adj': None}     # what was actually drawn, checked against the frame by build10 (draw asserts)


def reg_reset():
    REG['arcs'] = []; REG['bodies'] = []; REG['adj'] = None
WARD_COL = GOLD


def unit_mask(f, keep_all=False, only=None, skip=None):
    """mask (L, 1x) of every drawn unit cell on the board"""
    from PIL import Image as _I, ImageDraw as _D
    m = _I.new('L', (W, H), 0)
    d = _D.Draw(m)
    for u in f['units']:
        if not keep_all and (u['consumed'] or u['trigdead']):
            continue
        if only is not None and u['id'] not in only:
            continue
        if skip is not None and u['id'] in skip:
            continue
        ri, ro = CB.ring_geom(u['dep'])
        a0, a1 = span(u)
        if u['w'] == 6:
            d.ellipse([C[0] - ro + 4, C[1] - ro + 4, C[0] + ro - 4, C[1] + ro - 4], fill=255)
            d.ellipse([C[0] - ri - 4, C[1] - ri - 4, C[0] + ri + 4, C[1] + ri + 4], fill=0)
            continue
        n = max(6, int(abs(a1 - a0) / 3))
        pts = [ppx(C, ro - 4, a0 + 3 + (a1 - a0 - 6) * i / n) for i in range(n + 1)] + [ppx(C, ri + 4, a1 - 3 - (a1 - a0 - 6) * i / n) for i in range(n + 1)]
        d.polygon(pts, fill=255)
    return m


def grade_units(board, f, keep_all=False, dim_ids=None, dim_k=0.5):
    """darken + desaturate the unit screens (the programme art is saturated magenta): pink keeps one job, but the red chevrons must pop on it"""
    import numpy as _np
    from PIL import Image as _I, ImageFilter as _F
    m = unit_mask(f, keep_all).filter(_F.GaussianBlur(0.8))
    a = _np.asarray(board, _np.float32).copy()
    mk = (_np.asarray(m, _np.float32) / 255.0)[..., None]
    rgb = a[..., :3]
    lum = (rgb * _np.array([0.299, 0.587, 0.114], _np.float32)).sum(-1, keepdims=True)
    sat_keep, bright = 0.46, 0.86
    g = (lum + (rgb - lum) * sat_keep) * bright
    g = g + _np.array([6, 3, 8], _np.float32)
    a[..., :3] = rgb * (1 - mk) + g * mk
    if dim_ids:
        md = (_np.asarray(unit_mask(f, keep_all, only=set(dim_ids)).filter(_F.GaussianBlur(0.8)), _np.float32) / 255.0)[..., None]
        a[..., :3] = a[..., :3] * (1 - md * (1 - dim_k))
    return _I.fromarray(_np.clip(a, 0, 255).astype(_np.uint8), 'RGBA')


KWASH = {'Packet': (124, 64, 104), 'Worm': (106, 68, 130), 'Jammer': (94, 86, 138), 'Payload': (118, 68, 106), 'Ring': (118, 68, 106)}


def lit_cell(L, u):
    """the unit's screen wash: a muted mauve per kind (darkened / desaturated pink, not saturated magenta), well above the dark empty sectors; the deepest ring a touch dimmer"""
    ri, ro = CB.ring_geom(u['dep'])
    a0, a1 = span(u)
    wc = KWASH.get(u['kind'], (118, 68, 106))
    al = (210, 196, 180)[u['dep']]
    fill = tuple(wc) + (al,)
    if u['w'] == 6:
        L.poly(L.band(C, ri + 4, ro - 4, a0, a0 + 359.9), fill=fill)
    else:
        L.poly(L.band(C, ri + 4, ro - 4, a0 + 3, a1 - 3), fill=fill)
    a = DEPTH_DIM[u['dep']]
    if a:
        if u['w'] == 6:
            L.poly(L.band(C, ri + 4, ro - 4, a0, a0 + 359.9), fill=(2, 3, 8, a))
        else:
            L.poly(L.band(C, ri + 4, ro - 4, a0 + 3, a1 - 3), fill=(2, 3, 8, a))


# ----------------------------------------------------------------------------- chevrons: solid (hit now) + hollow (growth to come), same size and weight
def _chev_pts(ri, ang, i, half=14):
    r = ri + 9 + i * 9.5
    return [pt(r + 9, ang, -half), pt(r, ang, 0), pt(r + 9, ang, half)]


def chev_stack_h(L, ri, ang, n_solid, n_hollow, col=REDC):
    """n_solid nested V chevrons pointing inward + n_hollow outlined ones stacked outward of them (a stem only on stacks of 2 or more)"""
    tot = n_solid + n_hollow
    for i in range(n_hollow):
        p = _chev_pts(ri, ang, n_solid + i)
        L.line(p, INK, 11.5)
        L.line(p, col, 7.4)
        L.line(p, (10, 6, 14), 3.6)
    for col_, w in ((INK, 10.5), (col, 6)):
        for i in range(n_solid):
            L.line(_chev_pts(ri, ang, i), col_, w)
    if tot > 1:
        L.line([pt(ri + 9, ang, 0), pt(ri - 5, ang, 0)], INK, 10.5)
        L.line([pt(ri + 9, ang, 0), pt(ri - 5, ang, 0)], col, 6)


def chevrons_h(L, u, hit, grow, col=REDC):
    ri, ro = CB.ring_geom(u['dep'])
    REG['bodies'].append(dict(uid=u['id'], solid=hit, hollow=grow, sectors=u['w']))
    for q in range(u['w']):
        chev_stack_h(L, ri, 60 * (u['s'] + q), hit, grow, col)


# ----------------------------------------------------------------------------- Adjuster: a body on its ring
def adjuster_body(L, a, hp_after=None):
    """a gold diamond body with an HP bar, docked on its ring in its sector (ring +1 here), the boss skull small inside it; armor = steel cap"""
    if a['hp'] <= 0:
        return
    d, s = a['ring'], a['s']
    ri, ro = CB.ring_geom(min(d, 2))
    ang = 60 * s
    # its cell: gold-edged glass
    L.poly(L.band(C, ri + 4, ro - 4, ang - 27, ang + 27), fill=(32, 26, 8, 190))
    pts = L.band(C, ri + 4, ro - 4, ang - 27, ang + 27)
    L.line(pts + [pts[0]], INK, 7)
    L.line(pts + [pts[0]], GOLD, 4)
    # HP bar along the outer edge (cream segments in a socket, lost HP slashed)
    n = a['mx']
    a0, a1 = ang - 22, ang + 22
    r0, r1 = ro - 15, ro - 7
    socket(L, r0 - 2.5, r1 + 2.5, a0 - 1, a1 + 1)
    sw = (a1 - a0) / n
    gap = 3.0 / ((r0 + r1) / 2) * 57.3
    ha = a.get('hp_after', a['hp']) if hp_after is None else hp_after
    REG['adj'] = dict(segments=a['hp'], lost=a['hp'] - ha, ring=d, sector=s)
    for i in range(n):
        if i < a['hp']:
            L.poly(L.band(C, r0, r1, a0 + i * sw + gap / 2, a0 + (i + 1) * sw - gap / 2), fill=CREAM, outline=INK, w=1.0)
            if i >= ha:
                m = a0 + (i + 0.5) * sw
                L.line([ppx(C, r0 - 1, m - sw * 0.35), ppx(C, r1 + 1, m + sw * 0.35)], RED, 2.6)
    if a['df'] == 'armor':
        L.poly(L.band(C, ro - 7, ro + 1, a0, a1), fill=STEEL, outline=INK, w=1.8)
    # the body: a gold diamond with a dark core and the skull small inside
    x, y = ppx(C, (ri + ro) / 2 - 3, ang)
    k = L.k
    L.glow(lambda dd: dd.ellipse([(x - 34) * k, (y - 34) * k, (x + 34) * k, (y + 34) * k], fill=(4, 6, 14, 200)), blur=4)
    R = 30
    dia = [(x, y - R), (x + R, y), (x, y + R), (x - R, y)]
    L.poly(dia, fill=(52, 40, 10, 255), outline=INK, w=8)
    L.poly(dia, fill=None, outline=GOLD, w=4.2)
    r2 = 21
    L.poly([(x, y - r2), (x + r2, y), (x, y + r2), (x - r2, y)], fill=None, outline=(255, 226, 120), w=1.6)
    L.glyph('X_SKULL', 24, (x, y), WHITE)
    if a.get('strike'):
        chev_stack(L, RS['bz1'] - 30, ang, a['hit'], REDC)


# ----------------------------------------------------------------------------- E10 refund: gold burst + a RAM pip popping
def burst(L, x, y, r0=11, r1=24, n=10, col=(255, 214, 64)):
    pts = []
    for i in range(2 * n):
        rr = r1 if i % 2 == 0 else r0
        a = math.radians(-90 + 180 * i / n)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    L.poly(pts, fill=col, outline=INK, w=2.6)
    L.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(255, 250, 220), outline=INK, w=1.6)


def ram_pip_pop(L, x, y):
    """a cyan RAM pip (the same shape as the RAM terminal's) with a plus, popping out of a small gold burst"""
    burst(L, x, y, 8, 17, 8)
    L.rect([x + 12, y - 8, x + 36, y + 8], fill=CYAN, outline=INK, w=2.2, r=3)
    L.line([(x + 24, y - 4.5), (x + 24, y + 4.5)], INK, 3)
    L.line([(x + 19.5, y), (x + 28.5, y)], INK, 3)


# ----------------------------------------------------------------------------- landing arcs (PL10 ask 1)
LANE_R = [425, 460, 495]
HALF = 15
CP = 21           # chevron pitch (px along the arc)
DP = 19           # diamond pitch


def _land_start(secs):
    ss = set(secs)
    for s0 in range(6):
        if {(s0 + i) % 6 for i in range(len(ss))} == ss:
            return s0
    return min(ss)


def _diamond(L, x, y, col, r=8):
    L.poly([(x, y - r - 1.5), (x + r, y), (x, y + r + 1.5), (x - r, y)], fill=col, outline=INK, w=2)


def _check(L, x, y):
    L.line([(x - 8, y + 1), (x - 2, y + 7), (x + 9, y - 7)], INK, 7)
    L.line([(x - 8, y + 1), (x - 2, y + 7), (x + 9, y - 7)], GREEN, 3.8)


def _chev_arc(L, r, ang, da, hollow, col=REDC):
    """one chevron on the arc at angle `ang`, pointing inward (toward the tower)"""
    h = 8 * da
    p = [ppx(C, r + 7, ang - h), ppx(C, r - 6, ang), ppx(C, r + 7, ang + h)]
    if hollow:
        L.line(p, INK, 11)
        L.line(p, col, 7)
        L.line(p, (8, 5, 12), 3.2)
    else:
        L.line(p, INK, 9.5)
        L.line(p, col, 5.4)


def landing_arcs(L, f, only=None, words=True):
    """one bezel arc per landing unit (alive, lands within 3 turns after our guns), spanning its landing sectors, drawn clockwise from its first sector.
    On the arc: [kind glyph][wear][twist][dots = turns until, red dot = this END TURN] then, per landing sector, [solid red chevrons = hit at landing + hollow = growth to come]
    [red diamonds = HP through] (cream clamp = braced, orange chevron = soaked pip, green check = nothing through). Arcs pack into the fewest radial lanes."""
    items = []
    for u in f['units']:
        if u['consumed'] or u['trigdead']:
            continue
        if only is not None and u['id'] not in only:
            continue
        fz = u['fate']
        if fz['kind'] != 'lands' or 'land_hit' not in u:
            continue
        s0 = _land_start(u['land_sectors'])
        a0, a1 = 60 * s0 - 29, 60 * (s0 + u['w'] - 1) + 29
        items.append(dict(u=u, k=fz['k'], a0=a0, a1=a1, s0=s0))
    items.sort(key=lambda it: (it['k'], it['a0'] % 360))
    lanes = []
    for it in items:
        e0, e1 = it['a0'] % 360, it['a0'] % 360 + (it['a1'] - it['a0'])
        lane = 0
        while True:
            clash = False
            for (l_, g0, g1) in lanes:
                if l_ != lane:
                    continue
                for sh in (-360, 0, 360):
                    if e0 < g1 + 2 + sh and g0 + sh < e1 + 2:
                        clash = True
            if not clash:
                break
            lane += 1
        lanes.append((lane, e0, e1))
        it['lane'] = lane
    for it in items:
        u, k = it['u'], it['k']
        r = LANE_R[min(it['lane'], 2)]
        a0, a1 = it['a0'], it['a1']
        col_lane = LANE[u['dep']]['col']
        dash = LANE[u['dep']]['dash']
        da = 57.3 / r
        pts = L.band(C, r - HALF, r + HALF, a0, a1)
        L.poly(pts, fill=(7, 9, 17, 205), outline=None)
        L.line(pts + [pts[0]], INK, 6)
        L.line(pts + [pts[0]], col_lane, 2.6, dash=dash)
        # start cluster: glyph disc, wear mark, twist mark, dots
        gx, gy = ppx(C, r, a0 + 24 * da)
        kc = KCOL[u['kind']]
        L.ellipse([gx - 19, gy - 19, gx + 19, gy + 19], fill=tuple(int(v * 0.62) for v in kc) + (255,), outline=col_lane, w=2.8)
        L.glyph(KIND[u['kind']][1], 28, (gx, gy), WHITE)
        cur = 24 + 24
        if u.get('wear'):
            x_, y_ = ppx(C, r, a0 + (cur + 10) * da)
            L.rect([x_ - 9, y_ - 9, x_ + 9, y_ + 9], fill=GREEN, outline=INK, w=1.6, r=2)
            L.line([(x_ - 4, y_ - 9), (x_, y_ - 2), (x_ - 2, y_ + 2), (x_ + 4, y_ + 9)], WHITE, 2.2)
            cur += 28
        if f.get('twr') and f['twr'][1] and f['twr'][0] == u['dep'] and k > 0:
            x_, y_ = ppx(C, r, a0 + (cur + 12) * da)
            L.ellipse([x_ - 12, y_ - 12, x_ + 12, y_ + 12], fill=(30, 26, 6), outline=YEL, w=2.4)
            L.glyph('C_TWIST', 17, (x_, y_), YEL)
            cur += 30
        if k == 0:
            x_, y_ = ppx(C, r, a0 + (cur + 10) * da)
            L.ellipse([x_ - 8, y_ - 8, x_ + 8, y_ + 8], fill=REDC, outline=WHITE, w=2.2)
            cur += 24
        else:
            for i in range(k):
                x_, y_ = ppx(C, r, a0 + (cur + 7 + i * 14) * da)
                L.ellipse([x_ - 5, y_ - 5, x_ + 5, y_ + 5], fill=WHITE, outline=INK, w=1.4)
            cur += 14 * k + 4
        # per landing sector, centred on the sector
        ng = max(0, u['land_hit'] - min(u['hit'], u['land_hit']))
        ns = u['land_hit'] - ng
        for q in range(u['w']):
            sec = (it['s0'] + q) % 6
            th = 60 * (it['s0'] + q)
            thr = u['land_through'].get(str(sec), 0)
            sk = u['land_soak'].get(str(sec), 0)
            br = u['land_brace'].get(str(sec), 0)
            n_items = ns + ng
            REG['arcs'].append(dict(uid=u['id'], sector=sec, solid=ns, hollow=ng, diamonds=thr, soak=sk, brace=br, check=int(not thr and not br and not sk), k=k, now_dot=int(k == 0), wear=int(bool(u.get('wear'))), lane=it['lane']))
            wch = n_items * CP
            wdi = (thr * DP) + (sk * 15) + (24 if br else 0) + (24 if (not thr and not br and not sk) else 0)
            tot = wch + 16 + wdi
            x0 = -tot / 2
            if q == 0:
                x0 = max(x0, (cur - 24) - 29 * (r / 57.3) * 0 + 0) if False else x0
            for i in range(n_items):
                _chev_arc(L, r, th + (x0 + CP / 2 + i * CP) * da, da, hollow=i >= ns)
            x1 = x0 + wch + 16
            if br:
                xx_, yy_ = ppx(C, r, th + (x1 + 12) * da)
                L.glyph('C_BRACE', 28, (xx_, yy_), CREAM)
                x1 += 24
            for i in range(thr):
                xx_, yy_ = ppx(C, r, th + (x1 + DP / 2 + i * DP) * da)
                _diamond(L, xx_, yy_, REDC)
            x1 += thr * DP
            for i in range(sk):
                ang_i = th + (x1 + 7.5 + i * 15) * da
                p = [ppx(C, r + 6, ang_i - 6.5 * da), ppx(C, r - 5, ang_i), ppx(C, r + 6, ang_i + 6.5 * da)]
                L.line(p, INK, 8.5)
                L.line(p, SOAK_C, 5)
            x1 += sk * 15
            if not thr and not br and not sk:
                xx_, yy_ = ppx(C, r, th + (x1 + 12) * da)
                _check(L, xx_, yy_)
    return items


# ----------------------------------------------------------------------------- gun tracers: the Adjuster is a body on its ring now, so its shots end in its cell (not on the rim)
def gun_tracers10(L, f):
    for g in f['guns']:
        s = g['sector']
        if not g['shots'] or g['shots'][0]['uid'] is None:
            L.line([ppx(C, RS['s1'] + 2, 60 * s), ppx(C, RS['c0'] + 14, 60 * s)], CYAN, 2, dash=(4, 8))
            if NOW['words']:
                xx_, yy_ = ppx(C, RS['c0'] + 30, 60 * s)
                L.rect([xx_ - 52, yy_ - 12, xx_ + 52, yy_ + 12], fill=(6, 12, 24, 235), outline=CYAN, w=2, r=6)
                L.text((xx_, yy_ + 1), 'NO TARGET', 16, 'mono', fill=CYAN)
            continue
        shots = [sh for sh in g['shots'] if sh['uid'] is not None]
        n = len(shots)
        for i, sh in enumerate(shots):
            off = 24 + (i - (n - 1) / 2) * 9
            d = sh['dep']
            ri, ro = CB.ring_geom(d)
            p0 = pt(RS['s1'] + 3, 60 * s, off)
            p1 = pt(ri + 16, 60 * s, off)
            L.line([p0, p1], INK, 6.5)
            L.line([p0, p1], CYAN, 3.6, dash=(10, 4))
            x, y = p1
            if sh['result'] == 'armor':
                L.glyph('X_BOUNCE', 26, pt(ri + 30, 60 * s, off + 18), STEEL_HI)
            elif sh['result'] == 'ward':
                L.glyph('X_BOUNCE', 26, pt(ri + 30, 60 * s, off + 18), GOLD)
            elif sh['result'] == 'sealed':
                L.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(10, 9, 16), outline=WHITE, w=2.4)
            elif sh['result'] == 'shield':
                L.ellipse([x - 8, y - 8, x + 8, y + 8], fill=CYAN, outline=INK, w=2)
                for a_ in range(0, 360, 60):
                    L.line([(x + 10 * math.cos(math.radians(a_)), y + 10 * math.sin(math.radians(a_))), (x + 15 * math.cos(math.radians(a_)), y + 15 * math.sin(math.radians(a_)))], CYAN, 2.4)
            else:
                L.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(255, 255, 255), outline=CYAN, w=2.6)
