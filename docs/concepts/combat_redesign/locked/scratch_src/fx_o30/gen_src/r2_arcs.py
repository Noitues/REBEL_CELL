"""R2 outer_rings LANDING ARCS: landing_arc_frame (+ the LATENT full-circle width-6 arc), arc_glyph_disc, arc_wear_mark, arc_now_dot, arc_turn_dots, arc_chevrons,
arc_diamonds, arc_check, arc_soak_chevron, arc_brace_glyph, arc_twist_mark.  Selectors 'P' pick, 'V' the one variant.
Layout runs in px along the arc; every mark is oriented to the arc's tangent AT ITS OWN position (R1 oriented to the arc start)."""
import sys, math, copy
sys.dont_write_bytecode = True
from e10lib import *
import e10lib as E
import o_arcs as A
from o_arcs import LANE_R, HALF, REDC, GAINC, NETC, PLANC, INKD, REG, P, diamond, check, chev_one, lane_base_style
import r2_glyphs as GL

HARM = (255, 68, 51)
HARM_UP = __import__("asm_tokens").HARM_UP      # fix 2
GAIN = (123, 224, 123)
NET = (92, 225, 255)
SOAK = __import__('asm_tokens').SOAK           # token SOAK #6A6CFF, always with the chevron notch
PLAN = (255, 226, 0)


class Fr:
    """local frame at arc position (r, th + px): q(a, b) = a along clockwise travel, b radially OUTWARD"""
    def __init__(self, r, th, px):
        self.ang = th + px * 57.3 / r
        self.x, self.y = ppx(C, r, self.ang)
        a = math.radians(self.ang)
        self.tx, self.ty = math.cos(a), math.sin(a)
        self.nx, self.ny = math.sin(a), -math.cos(a)

    def q(self, a, b):
        return (self.x + self.tx * a + self.nx * b, self.y + self.ty * a + self.ny * b)


def rseg(fr, hl, hh, rad=3.0, n=3):
    """rounded segment (HP grammar r3): half length along, half height radial"""
    pts = []
    for cx, cy, a0 in ((hl - rad, hh - rad, 0), (-(hl - rad), hh - rad, 90), (-(hl - rad), -(hh - rad), 180), (hl - rad, -(hh - rad), 270)):
        for i in range(n + 1):
            t = math.radians(a0 + 90 * i / n)
            pts.append(fr.q(cx + rad * math.cos(t), cy + rad * math.sin(t)))
    return pts


# ----------------------------------------------------------------------------- arc_glyph_disc
def disc(L, r, th, px, u, lane, opt):
    fr = Fr(r, th, px)
    R = 13.5 if opt == 'P' else 12.0          # 27 px exact board token; V = 24 px
    kc = KCOL[u['kind']]
    L.ellipse([fr.x - R - 1.4, fr.y - R - 1.4, fr.x + R + 1.4, fr.y + R + 1.4], fill=INK)
    lane_base_style(L, fr.x, fr.y, R, u['dep'], kc)
    GL.kind_glyph(L, u['kind'], 21 if opt == 'P' else 18.5, (fr.x, fr.y))
    return 2 * R + 6


# ----------------------------------------------------------------------------- arc_wear_mark (HP grammar: lost now = HARM + white slash + ink)
def wear(L, r, th, px, opt):
    fr = Fr(r, th, px)
    hl, hh = (10.0, 5.6) if opt == 'P' else (11.0, 6.2)
    pts = rseg(fr, hl, hh)
    L.poly(pts, fill=HARM, outline=INK, w=2.4)
    s0, s1 = fr.q(-3.4, 6.6), fr.q(3.4, -6.6)
    L.line([s0, s1], INK, 4.6 if opt == 'P' else 5.2)
    L.line([s0, s1], WHITE, 2.0 if opt == 'P' else 2.6)
    return 2 * hl + 8


# ----------------------------------------------------------------------------- arc_twist_mark
def twist_mark(L, r, th, px, opt, dirn):
    fr = Fr(r, th, px)
    R = 10.5 if opt == 'P' else 10.5
    L.ellipse([fr.x - R - 1.2, fr.y - R - 1.2, fr.x + R + 1.2, fr.y + R + 1.2], fill=INK)
    L.ellipse([fr.x - R, fr.y - R, fr.x + R, fr.y + R], fill=(12, 10, 4), outline=PLAN, w=1.4 if opt == 'P' else 2.0)
    GL.stamp(L, 'twist', 15.0 if opt == 'P' else 14.0, (fr.x, fr.y), WHITE)
    return 2 * R + 6


# ----------------------------------------------------------------------------- arc_now_dot
def now_dot(L, r, th, px, opt):
    fr = Fr(r, th, px)
    R = 9.0 if opt == 'P' else 10.0
    L.ellipse([fr.x - R - 1.4, fr.y - R - 1.4, fr.x + R + 1.4, fr.y + R + 1.4], fill=INK)
    L.ellipse([fr.x - R, fr.y - R, fr.x + R, fr.y + R], fill=HARM, outline=WHITE, w=2.0 if opt == 'P' else 2.4)
    return 2 * R + 8


# ----------------------------------------------------------------------------- arc_turn_dots
def turn_dots(L, r, th, px, k, opt):
    w = 12 + k * 13
    f0 = Fr(r, th, px)
    pts = [P(r + 8.5, th, px), P(r + 8.5, th, px + w), P(r - 8.5, th, px + w), P(r - 8.5, th, px)]
    # pill: round the ends with the segment helper at the slot's own tangent
    fm = Fr(r, th, px + w / 2)
    pill = rseg(fm, w / 2, 9.0, 7.0, 4)
    L.poly(pill, fill=(14, 16, 28), outline=INK, w=3.2)
    L.poly(pill, fill=None, outline=(150, 164, 190), w=1.2)
    rd = 4.8 if opt == 'P' else 5.4
    for i in range(k):
        fd = Fr(r, th, px + 12 + i * 13)
        L.ellipse([fd.x - rd, fd.y - rd, fd.x + rd, fd.y + rd], fill=WHITE, outline=INK, w=1.2)
    return w + 6


# ----------------------------------------------------------------------------- arc_chevrons (22 x 10, inward everywhere)
CH = {'P': dict(hw=11, dp=10, pitch=25, ink=9.8, col=5.8), 'V': dict(hw=11, dp=12, pitch=26, ink=9.8, col=5.4)}


def chev_width(n, opt):
    return n * CH[opt]['pitch']


def chevrons(L, r, th, x0, ns, ng, opt):
    p = CH[opt]
    for i in range(ng + ns):
        hollow = i >= ns
        xc = x0 + p['pitch'] / 2 + i * p['pitch']
        fr = Fr(r, th, xc)
        q = [fr.q(-p['hw'], p['dp'] / 2), fr.q(0, -p['dp'] / 2), fr.q(p['hw'], p['dp'] / 2)]      # apex toward the tower
        if hollow:
            L.line(q, INK, p['ink'] + 2.2)
            L.line(q, HARM_UP, p['col'] + 1.8)
            L.line(q, INKD, max(1.6, p['col'] - 1.8))
        else:
            L.line(q, INK, p['ink'])
            L.line(q, HARM_UP, p['col'])


# ----------------------------------------------------------------------------- arc_diamonds (later turns darker, never hollow)
DI = {'P': dict(pitch=22, rw=10.5, rh=12.5), 'V': dict(pitch=21, rw=9.2, rh=11.2)}
DARK = {0: HARM_UP, 1: HARM, 2: (178, 48, 38)}      # fix 2: one value step up per tier


def diam_width(n, opt):
    return n * DI[opt]['pitch']


def diamonds(L, r, th, x0, n, opt, k):
    d = DI[opt]
    for i in range(n):
        fr = Fr(r, th, x0 + d['pitch'] / 2 + i * d['pitch'])
        diamond(L, fr.x, fr.y, d['rw'], d['rh'], fill=DARK.get(k, DARK[2]), ink=2.6)


# ----------------------------------------------------------------------------- arc_check (GAIN check in the empty diamond slot)
def check_mark(L, r, th, x0, opt, width=24):
    fr = Fr(r, th, x0 + width / 2)
    big = opt == 'V'
    rw, rh = (12.5, 14.5) if big else (12, 14)
    diamond(L, fr.x, fr.y, rw, rh, fill=(8, 22, 12), outline=INK, ow=4.4)
    diamond(L, fr.x, fr.y, rw, rh, fill=None, outline=GAIN, ow=2.0)
    check(L, fr.x, fr.y + 0.5, 0.86 if big else 0.78, GAIN, 6.4, 3.2)


# ----------------------------------------------------------------------------- arc_soak_chevron (SOAK pip with the chevron notch)
def soak_mark(L, r, th, x0, opt, width=24):
    fr = Fr(r, th, x0 + width / 2)
    hl, hh = (11.5, 6.6) if opt == 'P' else (11.5, 7.4)
    L.poly(rseg(fr, hl, hh), fill=SOAK, outline=INK, w=3.4)      # fix 7: 1 px INK keyline (was 2.4)
    nt = [fr.q(-3.4, 4.4), fr.q(3.2, 0), fr.q(-3.4, -4.4)]       # ink chevron notch pointing along travel
    L.line(nt, INK, 5.0 if opt == 'P' else 5.6)                  # fix 7: notch 3.4 -> 5.0 px


# ----------------------------------------------------------------------------- arc_brace_glyph (NET_CYAN + clamp-plate silhouette)
def brace_mark(L, r, th, x0, opt, width=24):
    fr = Fr(r, th, x0 + width / 2)
    GL.stamp(L, 'brace', 22.0 if opt == 'P' else 20.0, (fr.x, fr.y), NET)


# ----------------------------------------------------------------------------- landing_arc_frame
def frame(L, r, a0, a1, lane, opt):
    col_lane = lane['col']
    dash = lane['dash']
    da = 57.3 / r
    cap = HALF * da
    n = max(8, int((a1 - a0) / 3))
    ae = a1 - 0.9 * HALF * da
    outer = [ppx(C, r + HALF, a0 + cap + (ae - a0 - cap) * i / n) for i in range(n + 1)]
    inner = [ppx(C, r - HALF, ae - (ae - a0 - cap) * i / n) for i in range(n + 1)]
    tipp = [ppx(C, r, a1)]
    start = [ppx(C, r + HALF * math.cos(math.radians(t)), a0 + cap - cap * math.sin(math.radians(t))) for t in range(0, 181, 20)]
    pts = outer + tipp + inner + start
    L.poly(pts, fill=(7, 9, 17, 214))
    L.line(pts + [pts[0]], INK, 6.4)
    L.line(pts + [pts[0]], col_lane, 2.8 if opt == 'P' else 2.2, dash=dash)


# ----------------------------------------------------------------------------- the whole arc
def layout_items(f, only=None, extra=None):
    items = []
    units = list(f['units']) + list(extra or [])
    for u in units:
        if u['consumed'] or u['trigdead']:
            continue
        if only is not None and u['id'] not in only:
            continue
        fz = u['fate']
        if fz['kind'] != 'lands' or 'land_hit' not in u:
            continue
        s0 = E._land_start(u['land_sectors'])
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
    return items


def landing_arcs(L, f, sel, only=None, extra=None):
    items = layout_items(f, only, extra)
    S = lambda key: sel.get(key, 'P')
    for it in items:
        u, k = it['u'], it['k']
        r = LANE_R[min(it['lane'], 2)]
        a0, a1 = it['a0'], it['a1']
        lane = LANE[u['dep']]
        frame(L, r, a0, a1, lane, S('frame'))
        wd = disc(L, r, a0, 22, u, lane, S('disc'))
        px = 22 + wd / 2 + 3
        if u.get('wear'):
            px += wear(L, r, a0, px + 12, S('wear'))
        if f.get('twr') and f['twr'][1] and f['twr'][0] == u['dep'] and k > 0:
            px += twist_mark(L, r, a0, px + 13, S('twist'), f['twr'][1]) + 2
        if k == 0:
            px += now_dot(L, r, a0, px + 11, S('now'))
        else:
            px += turn_dots(L, r, a0, px, k, S('turn'))
        ng = max(0, u['land_hit'] - min(u['hit'], u['land_hit']))
        ns = u['land_hit'] - ng
        for q in range(u['w']):
            sec = (it['s0'] + q) % 6
            th = 60 * (it['s0'] + q)
            thr = u['land_through'].get(str(sec), 0)
            sk = u['land_soak'].get(str(sec), 0)
            br = u['land_brace'].get(str(sec), 0)
            REG['arcs'].append(dict(uid=u['id'], sector=sec, solid=ns, hollow=ng, diamonds=thr, soak=sk, brace=br, check=int(not thr and not br and not sk), k=k, now_dot=int(k == 0), wear=int(bool(u.get('wear'))), lane=it['lane']))
            n_items = ns + ng
            wch = chev_width(n_items, S('achev'))
            gap = 14
            wdi = diam_width(thr, S('diam')) + sk * 24 + (26 if br else 0) + (26 if (not thr and not br and not sk) else 0)
            tot = wch + gap + wdi
            x0 = -tot / 2
            chevrons(L, r, th, x0, ns, ng, S('achev'))
            x1 = x0 + wch + gap
            if br:
                brace_mark(L, r, th, x1, S('brace'))
                x1 += 26
            if thr:
                diamonds(L, r, th, x1, thr, S('diam'), k)
                x1 += diam_width(thr, S('diam'))
            for i in range(sk):
                soak_mark(L, r, th, x1, S('soak'))
                x1 += 24
            if not thr and not br and not sk:
                check_mark(L, r, th, x1, S('check'))
    return items


def full_circle_unit(uid=99):
    """LATENT landing_arc_full_circle: a width-6 Ring unit landing on lane 0 (all six sectors), for rendering only"""
    thr = {'0': 2, '1': 1, '2': 0, '3': 2, '4': 1, '5': 3}
    return dict(id=uid, kind='Ring', dep=0, s=0, w=6, hp=6, mx=6, sh=0, shmx=0, hit=3, grown=1, df='plain', warded=False, consumed=False, trigdead=False,
                fate={'kind': 'lands', 'k': 0, 'hits': [], 'tohp': 8}, lose=[0, 0], land_hit=4, land_sectors=[0, 1, 2, 3, 4, 5], wear=0, jam=0,
                land_through=thr, land_soak={str(i): 0 for i in range(6)}, land_brace={str(i): 0 for i in range(6)}, land_abs={str(i): 0 for i in range(6)})
