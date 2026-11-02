"""overlay-level wheel_core options: slice bars + pip states + break X + brace + soak, threat trim, HP ring, nudge, gun tracers + results."""
import sys, math
sys.dont_write_bytecode = True
import wc_base as WB
from wc_base import *
INDIGO = (118, 128, 255)       # proposed SOAK token (open call 1): clear of schedule orange, trace violet, lane blue
SOCKC = (22, 26, 36)


def show_slices(f):
    """latent-state showcase wheel (not game content): one slice per state"""
    w = f['wheel']
    def st(i, hp, ha, soaked=0, soak=False, brace=False):
        w[i].update(hp=hp, hp_after=ha, soaked=soaked, soak=soak, brace=brace)
    st(0, 1, 1); st(1, 2, 0); st(2, 2, 1); st(3, 1, 2); st(4, 2, 0, soaked=1, soak=True); st(5, 0, 0)


def pip_states(w):
    mx, hp, ha, sk = w['mx'], w['hp'], w.get('hp_after', w['hp']), w.get('soaked', 0)
    out = []
    for i in range(mx):
        if i < ha and i < hp: out.append('lit')
        elif i < ha: out.append('mend')
        elif i < hp: out.append('soak' if (hp - 1 - i) < sk else 'harm')
        else: out.append('gone')
    return out


def cap(L, r, a0, a1, col, w):
    pts = L.arc_pts(C, r, a0, a1, 8)
    L.line(pts, col, w)
    for p in (pts[0], pts[-1]):
        L.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=col)


def capsule(L, r, a0, a1, col, w, ink=2.2):
    cap(L, r, a0, a1, INK, w + ink * 2)
    cap(L, r, a0, a1, col, w)


def slash(L, r, am, w, col=(255, 255, 255), lw=2.4):
    p = [ppx(C, r - w * 0.7, am - 2.6 * 57.3 / r * 0.5), ppx(C, r + w * 0.7, am + 2.6 * 57.3 / r * 0.5)]
    L.line(p, INK, lw + 2.4); L.line(p, col, lw)


def plus(L, r, am, s=3.4, col=(255, 255, 255), lw=1.8):
    x, y = ppx(C, r, am)
    L.line([(x - s, y), (x + s, y)], INK, lw + 2); L.line([(x, y - s), (x, y + s)], INK, lw + 2)
    L.line([(x - s, y), (x + s, y)], col, lw); L.line([(x, y - s), (x, y + s)], col, lw)


def bar_family(fam, r=131.0, w=6.0, ln=17.0, gp=5.0):
    def draw_slice(L, w_, s):
        sts = pip_states(w_)
        n = len(sts)
        span = n * ln + (n - 1) * gp
        a = 60 * s - span / 2
        for i, st in enumerate(sts):
            a0, a1 = a + i * (ln + gp), a + i * (ln + gp) + ln
            am = (a0 + a1) / 2
            if fam == 'A':       # solid grammar: shape first
                if st == 'lit': capsule(L, r, a0, a1, GREEN, w)
                elif st == 'harm': capsule(L, r, a0, a1, REDC, w); slash(L, r, am, w)
                elif st == 'soak':
                    capsule(L, r, a0, a1, INDIGO, w)
                    p = [ppx(C, r - w * 0.7, am - 2.2), ppx(C, r + w * 0.1, am), ppx(C, r - w * 0.7, am + 2.2)]
                    L.line(p, INK, 3.2)
                elif st == 'mend': capsule(L, r, a0, a1, GREEN, w); cap(L, r, a0 + 1.2, a1 - 1.2, (8, 16, 12), w - 3.4); plus(L, r, am)
                else: capsule(L, r, a0, a1, SOCKC, w - 1, ink=1.6); cap(L, r, a0 + 0.6, a1 - 0.6, (10, 12, 18), w - 3)
            elif fam == 'B':     # hollow = lost: outline only
                if st == 'lit': capsule(L, r, a0, a1, GREEN, w)
                elif st == 'harm': capsule(L, r, a0, a1, REDC, w); cap(L, r, a0 + 1.4, a1 - 1.4, (14, 8, 12), w - 3.6); slash(L, r, am, w, REDC, 2.2)
                elif st == 'soak':
                    capsule(L, r, a0, a1, INDIGO, w); cap(L, r, a0 + 1.4, a1 - 1.4, (10, 10, 24), w - 3.6)
                    for q in (-1, 1):
                        p = [ppx(C, r - 2.2, am + q * 2.6), ppx(C, r + 0.4, am + q * 0.4), ppx(C, r - 2.2, am - q * 1.8)]
                    L.line([ppx(C, r + 1.8, am - 2.0), ppx(C, r - 1.4, am), ppx(C, r + 1.8, am + 2.0)], INDIGO, 2.2)
                elif st == 'mend':
                    pts = L.arc_pts(C, r, a0, a1, 8); L.line(pts, GREEN, w, dash=(3, 3)); plus(L, r, am, 3.0, GREEN)
                else: cap(L, r, a0, a1, (30, 36, 48), 2.0)
            else:                # C: butt-capped plates on a slimmer, inner track
                rr = r - 2
                def plate(col, a0=a0, a1=a1, ww=w + 1.5):
                    pts = L.band(C, rr - ww / 2, rr + ww / 2, a0, a1)
                    return pts
                pts = plate(None); L.poly(pts, fill=SOCKC + (255,), outline=INK, w=3.0)
                inner = L.band(C, rr - w / 2 + 0.6, rr + w / 2 - 0.6, a0 + 0.8, a1 - 0.8)
                if st == 'lit': L.poly(inner, fill=GREEN)
                elif st == 'harm':
                    L.poly(inner, fill=REDC)
                    for q in range(3):
                        am2 = a0 + 3 + q * 5
                        L.line([ppx(C, rr - w / 2, am2), ppx(C, rr + w / 2, am2 + 2.6)], (255, 255, 255), 1.8)
                elif st == 'soak':
                    L.poly(inner, fill=INDIGO)
                    L.poly([ppx(C, rr - w / 2, am - 2.6), ppx(C, rr + 0.5, am), ppx(C, rr - w / 2, am + 2.6)], fill=INK)
                elif st == 'mend':
                    L.line(inner + [inner[0]], GREEN, 1.8); plus(L, rr, am, 3.0, GREEN)
                else: L.line(inner + [inner[0]], (70, 82, 98), 1.2)
    return draw_slice


def x_mark(L, x, y, r, col, ink_w=3.0, lw=5.0):
    for sgn in (1, -1):
        pts = [(x - r, y - sgn * r), (x + r, y + sgn * r)]
        L.line(pts, INK, lw + ink_w * 2)
    for sgn in (1, -1):
        L.line([(x - r, y - sgn * r), (x + r, y + sgn * r)], col, lw)


def break_family(kind):
    def f(L, s, soaked=False):
        col = INDIGO if soaked else REDC
        am = 60 * s
        if kind == 'A':       # corner X + hatch dim of the whole wedge
            L.poly(L.band(C, RS['s0'] + 4, RS['s1'] - 14, am - 26, am + 26), fill=(4, 4, 10, 120))
            for q in range(-9, 10):
                L.line([ppx(C, RS['s0'] + 8, am + q * 2.8), ppx(C, RS['s1'] - 16, am + q * 2.8 + 8)], col + (90,), 1.4)
            x, y = ppx(C, 112, am + 18); x_mark(L, x, y, 9, col)
        elif kind == 'B':     # dim preview + badge disc with X at the hub-side corner
            L.poly(L.band(C, RS['s0'] + 4, RS['s1'] - 14, am - 26, am + 26), fill=(4, 4, 10, 150))
            x, y = ppx(C, 62, am - 14)
            L.ellipse([x - 15, y - 15, x + 15, y + 15], fill=(12, 6, 10), outline=col, w=3.4)
            x_mark(L, x, y, 6.5, col, 1.6, 3.6)
        else:                 # hazard stripes on the outer third, X at the rim corner
            for q in range(-8, 9):
                L.line([ppx(C, 100, am + q * 3.0), ppx(C, 124, am + q * 3.0 + 6)], col + (150,), 3.0)
            x, y = ppx(C, 104, am + 20); x_mark(L, x, y, 10, col, 3.2, 5.6)
    return f


def stage_factory(fam='cur', brk='cur', soak_rim=True):
    """replacement for tower_slice_bars: bars from a family, break X from a family, brace + soak marks from E10"""
    if fam == 'cur' and brk == 'cur':
        return None
    cur_stage = tower_slice_bars
    drawer = bar_family(fam) if fam != 'cur' else None
    bk = break_family(brk) if brk != 'cur' else None

    def stage(L, f):
        if drawer is None:
            # e10 bars, but break X replaced: run e10 with the X suppressed
            f2 = json.loads(json.dumps(f))
            for w in f2['wheel']:
                pass
            cur_stage(L, f)
        else:
            for w in f['wheel']:
                s = w['sector']
                drawer(L, w, s)
                if w.get('brace'): brace_plate(L, s)
                if w.get('soak'): soak_marks(L, s)
        if bk:
            for w in f['wheel']:
                if w.get('hp', 0) > 0 and w.get('hp_after', w['hp']) == 0:
                    bk(L, w['sector'], soaked=bool(w.get('soaked')))
    return stage


# ------------------------------------------------------------------ threat trim
def trim_factory(kind):
    def trim(L, f):
        seen = {}
        for u in f['units']:
            fz = u['fate']
            if fz['kind'] != 'lands' or u['consumed'] or u['trigdead']: continue
            for (sec, sl, hit, tohp) in fz['hits']:
                seen.setdefault(sec, set()).add(fz['k'])
        R = 140.0
        PAL = (150, 190, 255)
        def arc(a0, a1, k, r=R):
            if k == 0:
                pts = L.arc_pts(C, r, a0, a1); L.line(pts, INK, 9.5); L.line(pts, REDC, 5.5)
            elif k == 1:
                pts = L.arc_pts(C, r, a0, a1); L.line(pts, INK, 8); L.line(pts, PAL, 3.6, dash=(8, 5))
            else:
                pts = L.arc_pts(C, r, a0, a1); L.line(pts, INK, 6.5); L.line(pts, (236, 240, 255), 2.2, dash=(4, 6))
        for sec, ks in seen.items():
            m = 60 * sec
            ks = sorted(ks)
            if kind == 'A':          # fixed thirds: [later | next | now] positions
                zones = {2: (-26, -9), 1: (-8, 8), 0: (9, 26)}
                for k in ks: arc(m + zones[k][0], m + zones[k][1], k)
            elif kind == 'B':        # priority lane full length, others as end beads
                k0 = ks[0]; arc(m - 24, m + 24, k0)
                for j, k in enumerate(ks[1:]):
                    for sgn in (-1,):
                        x, y = ppx(C, R, m - 24 - 3.2 - j * 3.8)
                        L.ellipse([x - 3.4, y - 3.4, x + 3.4, y + 3.4], fill=(236, 240, 255) if k == 2 else (150, 190, 255), outline=INK, w=1.6)
            else:                    # stacked but inside the wedge rim: now r140, next r136.5 (shorter), later r133 hairline
                rs = {0: 140.5, 1: 137.2, 2: 134.2}
                span = {0: 25, 1: 22, 2: 20}
                for k in ks: arc(m - span[k], m + span[k], k, rs[k])
    return trim


# ------------------------------------------------------------------ HP ring
def hp_ring_factory(kind):
    def ring(L, hp, hp_after, mx):
        if kind == 'A':       # 6 px, groups of 5 with wide gaps, harm red + slash
            r0, r1 = 149.5, 155.5
        elif kind == 'B':
            r0, r1 = 148.5, 156.5
        else:
            r0, r1 = 150.0, 155.0
        L.poly(L.band(C, r0 - 1.6, r1 + 1.6, 0, 359.9), fill=(4, 5, 9, 255))
        for i in range(mx):
            g = (i // 5)
            a0 = 360 * i / mx + 0.9 + (0.0)
            a1 = 360 * (i + 1) / mx - 0.9
            if i % 5 == 0: a0 += 1.6
            if i % 5 == 4: a1 -= 1.6
            on = i < hp
            lost = hp_after <= i < hp
            if not on:
                L.poly(L.band(C, r0, r1, a0, a1), fill=(24, 34, 28), outline=(60, 80, 66), w=1.0); continue
            if lost:
                if kind == 'B':
                    L.poly(L.band(C, r0, r1, a0, a1), fill=(16, 8, 10), outline=REDC, w=2.0)
                else:
                    L.poly(L.band(C, r0, r1, a0, a1), fill=REDC)
                m = (a0 + a1) / 2
                p = [ppx(C, r0 - 0.5, m - 1.4), ppx(C, r1 + 0.5, m + 1.4)]
                L.line(p, INK, 3.6); L.line(p, (255, 255, 255), 1.6)
            else:
                L.poly(L.band(C, r0, r1, a0, a1), fill=GREEN)
    return ring


# ------------------------------------------------------------------ nudge
def nudge_factory(kind):
    if kind == 'A':
        return lambda L: None
    def n(L):
        for sg in (-1, 1):
            x, y = ppx(C, RS['bz0'] + 11, sg * 3.2)
            p = [(x - 5 * sg, y - 7), (x + 3 * sg, y), (x - 5 * sg, y + 7)]
            if kind == 'B':
                L.line(p, INK, 5.6); L.line(p, CYAN, 2.4)
            else:
                L.line(p, INK, 6.5); L.line(p, (40, 90, 110), 3.6)
    return n


# ------------------------------------------------------------------ gun tracers
def guns_factory(kind):
    def g(L, f):
        for gn in f['guns']:
            s = gn['sector']
            shots = [sh for sh in gn['shots'] if sh['uid'] is not None]
            if not shots:
                continue
            n = len(shots)
            for i, sh in enumerate(shots):
                off = 24 + (i - (n - 1) / 2) * 9
                d = sh['dep']; ri, ro = CB.ring_geom(d)
                p0 = pt(RS['s1'] + 3, 60 * s, off)
                rend = (ri + ro) / 2
                p1 = pt(rend - (0 if d == 1 else 0), 60 * s, off * 0.6)
                if kind == 'A':       # long dash 12/6, round muzzle bead small, result spark
                    L.line([p0, p1], INK, 7); L.line([p0, p1], CYAN, 3.4, dash=(12, 6))
                elif kind == 'B':     # solid core + faint
                    L.line([p0, p1], INK, 7.4); L.line([p0, p1], CYAN, 3.6)
                else:                 # short dash 6/5 matching nothing else
                    L.line([p0, p1], INK, 7); L.line([p0, p1], CYAN, 3.4, dash=(6, 5))
                x, y = p1
                if sh['result'] == 'hit':
                    spark(L, x, y, kind)
                else:
                    ricochet(L, x, y, GOLD if sh['result'] == 'ward' else STEEL_HI)
    return g


def spark(L, x, y, kind):
    r = 9 if kind != 'C' else 10
    pts = []
    for i in range(16):
        a = math.radians(i * 22.5 - 90)
        rr = r * 1.7 if i % 2 == 0 else r * 0.62
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    L.poly(pts, fill=(255, 255, 255), outline=INK, w=2.6)


def ricochet(L, x, y, col):
    L.line([(x - 12, y + 6), (x, y - 4), (x + 12, y - 12)], INK, 7); L.line([(x - 12, y + 6), (x, y - 4), (x + 12, y - 12)], col, 3.4)
    L.line([(x - 4, y + 12), (x + 6, y + 4)], INK, 6); L.line([(x - 4, y + 12), (x + 6, y + 4)], col, 2.6)


def show_guns(f):
    f['guns'][0]['shots'] = [dict(sh, result='armor') for sh in f['guns'][0]['shots']]
    f['guns'][1]['shots'] = [dict(sh, result='shield') for sh in f['guns'][1]['shots']]
    f['guns'][2]['shots'] = [dict(sh, result='ward') for sh in f['guns'][2]['shots']]


def pop(L, x, y):
    for i in range(8):
        a = math.radians(i * 45)
        p = [(x + 6 * math.cos(a), y + 6 * math.sin(a)), (x + 13 * math.cos(a), y + 13 * math.sin(a))]
        L.line(p, INK, 5.4); L.line(p, CYAN, 2.4)
    L.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(8, 20, 30), outline=CYAN, w=2.2)


def results_factory(kind):
    base = guns_factory('A')
    def g(L, f):
        base(L, f)
        for gn in f['guns']:
            s = gn['sector']
            shots = [sh for sh in gn['shots'] if sh['uid'] is not None]
            for i, sh in enumerate(shots):
                if sh['result'] == 'shield':
                    off = 24 + (i - (len(shots) - 1) / 2) * 9
                    ri, ro = CB.ring_geom(sh['dep']); x, y = pt((ri + ro) / 2, 60 * s, off * 0.6)
                    L.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(10, 10, 20), outline=INK, w=1)
                    pop(L, x, y)
    return g


def burst_pair_factory(kind):
    base = guns_factory('A')
    def g(L, f):
        base(L, f)
        for gn in f['guns']:
            s = gn['sector']; n = len([1 for sh in gn['shots'] if sh['uid'] is not None])
            for i in range(n):
                off = 24 + (i - (n - 1) / 2) * 9
                x, y = pt(RS['s1'] + 3, 60 * s, off)
                if kind == 'A':
                    L.ellipse([x - 3.2, y - 3.2, x + 3.2, y + 3.2], fill=CYAN, outline=INK, w=1.6)
                elif kind == 'B':
                    p = [pt(RS['s1'] - 2, 60 * s, off), pt(RS['s1'] + 7, 60 * s, off)]
                    L.line(p, INK, 6.5); L.line(p, CYAN, 3.4)
                else:
                    q = [pt(RS['s1'] + 8, 60 * s, off - 3), pt(RS['s1'] + 1, 60 * s, off), pt(RS['s1'] + 8, 60 * s, off + 3)]
                    L.line(q, INK, 5.6); L.line(q, CYAN, 2.4)
    return g


def ricochet2(L, x, y, col, kind):
    if kind == 'A':
        ricochet(L, x, y, col)
    elif kind == 'B':      # bar the shot hits + a bent-back arrow
        L.line([(x - 12, y + 9), (x + 12, y - 9)], INK, 8); L.line([(x - 12, y + 9), (x + 12, y - 9)], col, 4)
        p = [(x - 10, y - 12), (x - 2, y - 3), (x - 12, y + 0)]
        L.line(p, INK, 5.4); L.line(p, col, 2.4)
    else:                  # ring bump with a bounce tick
        L.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(10, 10, 18), outline=INK, w=5)
        L.ellipse([x - 10, y - 10, x + 10, y + 10], outline=col, w=3)
        L.line([(x - 18, y + 12), (x - 8, y + 4)], INK, 5.6); L.line([(x - 18, y + 12), (x - 8, y + 4)], col, 2.6)


def results_factory(kind):
    base = guns_factory(kind)
    def g(L, f):
        base(L, f)
        for gn in f['guns']:
            s = gn['sector']
            shots = [sh for sh in gn['shots'] if sh['uid'] is not None]
            for i, sh in enumerate(shots):
                off = 24 + (i - (len(shots) - 1) / 2) * 9
                ri, ro = CB.ring_geom(sh['dep']); x, y = pt((ri + ro) / 2, 60 * s, off * 0.6)
                if sh['result'] in ('armor', 'ward'):
                    ricochet2(L, x + 2, y - 2, GOLD if sh['result'] == 'ward' else STEEL_HI, kind)
                elif sh['result'] == 'shield':
                    pop(L, x, y)
    return g
