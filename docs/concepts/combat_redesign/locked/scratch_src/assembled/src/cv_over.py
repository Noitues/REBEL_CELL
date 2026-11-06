"""Board overlay: HP ring, wave bezel (schedule cells, sector digits, needle), ring labels, unit cells (token + value + HP + arrival),
slice HP badges + threat trim, line-of-fire with numbers. Everything at 2x then downscaled; every number comes from the frame dict (the sim)."""
import sys
sys.dont_write_bytecode = True
from cv_lib import *
from cv_board import ring_geom, slice_value

ORG_D = (60, 30, 8)


def cpt(dep, s, t=0, n=0, rr=None):
    """screen point in cell (dep,s): t along the cell (clockwise), n outward."""
    ri, ro = ring_geom(dep)
    r = (ri + ro) / 2 + n if rr is None else rr
    a = 60 * s
    x, y = ppx(C, r, a)
    th = math.radians(a)
    return (x + t * math.cos(th), y + t * math.sin(th))


def sec_pt(s, r, off=0):
    return ppx(C, r, 60 * s + off)


# ------------------------------------------------------------------ HP ring (bible 3.2 HP arc, predicted loss hatched)
def hp_ring(L, hp, hp_after, mx):
    r0, r1 = RS['hp0'] + 1, RS['hp1'] - 1
    n = mx
    for i in range(n):
        a0, a1 = 360 * i / n + 0.8, 360 * (i + 1) / n - 0.8
        on = i < hp
        lost = hp_after <= i < hp
        col = (RED if lost else GREEN) if on else (38, 58, 42)
        L.poly(L.band(C, r0, r1, a0, a1), fill=col)
        if lost:
            m = (a0 + a1) / 2
            L.line([ppx(C, r0 + 2, m - 1.6), ppx(C, r1 - 2, m + 1.6)], (255, 235, 240), 1.3)


# ------------------------------------------------------------------ wave bezel
def sched_label(v):
    return 'HOLD' if v == 0 else '+%d' % v


def bezel(L, sched, twist=None, caption=True):
    """WAVE TURNS schedule as bezel cells (amendment 3): span = steps x 60 deg from the needle; rail text >= 16 px."""
    b0, b1 = RS['bz0'] + 3, RS['bz0'] + 29
    for i in range(60):
        a = 6 * i
        L.line([ppx(C, RS['bz1'] - 7, a), ppx(C, RS['bz1'] - (3 if i % 10 else 1), a)], (255, 190, 110) if i % 10 == 0 else (150, 100, 55), 1.2)
    names = ['THIS TURN', 'NEXT', 'THEN']
    cum = 0
    for k, v in enumerate(sched):
        span = 60 * v if v else 14
        a0, a1 = cum + 0.8, cum + span - 0.8
        live = k == 0
        col = YEL if (twist and k == 0) else ORANGE
        L.poly(L.band(C, b0, b1, a0, a1), fill=(255, 150, 40) if live else ORG_D, outline=col, w=1.6)
        txt = '%s %s' % (sched_label(v), names[k])
        lab_deg = len(txt) * 10.2 / ((b0 + b1) / 2) * 57.3
        if v:
            nch = int(span / 12)
            for j in range(nch):
                am = a0 + (a1 - a0) * (j + 0.5) / nch
                if am < a0 + 6 + lab_deg + 4:
                    continue
                p = [ppx(C, b0 + 5, am - 2.4), ppx(C, (b0 + b1) / 2, am + 2.4), ppx(C, b1 - 5, am - 2.4)]
                L.line(p, (255, 230, 170) if live else (170, 100, 35), 1.8)
            am = a0 + 6 + lab_deg / 2
            L.arc_text(C, (b0 + b1) / 2 - 1, am, txt, 17, INK if live else (255, 190, 110), 'mono')
        cum += span if v else 14
    if caption:
        L.arc_text(C, (b0 + b1) / 2, 330, 'WAVE TURNS', 17, (255, 190, 110), 'mono')
    return cum


def sector_digits(L, cols=None):
    for s in range(6):
        x, y = sec_pt(s, RS['bz1'] - 4)
        L.ellipse([x - 15, y - 15, x + 15, y + 15], fill=(10, 9, 16), outline=ORANGE, w=3)
        L.text((x, y + 1), str(s), 22, 'anton', fill=WHITE)
    x0, y0 = ppx(C, RS['bz0'] - 6, 0)
    L.poly([(x0, y0 + 2), (x0 - 11, y0 - 26), (x0 + 11, y0 - 26)], fill=(245, 245, 250), outline=INK, w=2)


def ring_labels(L, extra=None):
    """NOW / +1 / +2 on the ring gutter at 30 deg: ring depth stated in words and in the lane's own line style."""
    for d in range(3):
        ri, ro = ring_geom(d)
        x, y = ppx(C, (ri + ro) / 2, 30)
        lane = LANE[d]
        s = lane['name']
        w = L.tw(s, 20, 'anton') + 14
        L.rect([x - w / 2, y - 13, x + w / 2, y + 13], fill=(8, 10, 18, 245), outline=lane['col'], w=2, r=6)
        L.text((x, y + 1), s, 20, 'anton', fill=lane['col'], anchor='mm')


# ------------------------------------------------------------------ lane style borders (threat trim)
def cell_border(L, dep, s, strong=True, alpha=255):
    ri, ro = ring_geom(dep)
    lane = LANE[dep]
    pts = L.band(C, ri + 4, ro - 4, 60 * s - 27, 60 * s + 27)
    pts = pts + [pts[0]]
    L.line(pts, tuple(lane['col']) + (alpha,), lane['w'], dash=lane['dash'])


def lane_base_style(L, x, y, r, dep, fillcol):
    lane = LANE[dep]
    L.ellipse([x - r, y - r, x + r, y + r], fill=tuple(int(v * 0.72) for v in fillcol) + (255,))
    if lane['dash'] is None:
        L.ellipse([x - r, y - r, x + r, y + r], outline=lane['col'], w=lane['w'])
    else:
        n = 14
        for i in range(n):
            a0 = 360 * i / n
            L.line(L.arc_pts((x, y), r, a0, a0 + 360 / n * 0.55, 6), lane['col'], lane['w'])


def arrow(L, x, y, col, s=7, w=3):
    L.line([(x - s, y), (x + s, y)], col, w)
    L.poly([(x + s + 1, y), (x + 1, y - s * 0.9), (x + 1, y + s * 0.9)], fill=col)


def unit_cells(L, f, show_arrival=True, only=None, skip=None, nowords=False, glyph_only=False):
    """single file along each cell's own axis: [glyph token][was ->][value][HP][arrival]. Plain text with ink stroke (no loose chips).
    A wounded unit reads in ONE form everywhere: old -> new (e.g. 24 -> 10)."""
    ids = []
    items = [dict(u, adj=False) for u in f['units']]
    ad = f['adjuster']
    items.append(dict(id='ADJ', kind='Adjuster', dep=ad['ring'], s=ad['s'], hp=ad['hp'], mxhp=f['ehp'], raw=f['_adj_hit'], plan=f['_adj_hit'], killed=False,
                      hp_after=f['_adj_hp_after'], land=ad['s'], adj=True, g=0))
    for u in items:
        if only is not None and u['id'] not in only:
            continue
        if skip is not None and u['id'] in skip:
            continue
        dep, s = u['dep'], u['s']
        x, y = cpt(dep, s)
        kc = KCOL[u['kind']]
        cell_border(L, dep, s)
        dead = u['killed']
        val = u['raw'] if u['plan'] is None else u['plan']
        wounded = (u['plan'] is not None and u['plan'] != u['raw'] and not u.get('adj'))
        a, b = u['hp'], u['hp_after']
        change = (dep >= 1 or u.get('adj')) and b != a
        if dep == 0 and not u.get('adj') and dead:
            change, b = True, 0
        seq = ['glyph'] + (['was'] if wounded else []) + ['val', 'hp'] + (['arr'] if (show_arrival and dep >= 1) else [])
        if glyph_only:
            seq = ['glyph']
        step = 50
        n = len(seq)
        th = math.radians(60 * s)
        tx, ty = math.cos(th), math.sin(th)
        L0 = (n * step) / 2 + 8

        def plate(dd, x=x, y=y, tx=tx, ty=ty, L0=L0):
            dd.line([((x - tx * L0) * 2, (y - ty * L0) * 2), ((x + tx * L0) * 2, (y + ty * L0) * 2)], fill=(4, 6, 14, 165), width=46 * 2)
        L.glow(plate, blur=5)
        for k, it in enumerate(seq):
            t = (k - (n - 1) / 2) * step * (-1 if s >= 3 else 1)
            px, py = cpt(dep, s, t, 0)
            if it == 'glyph':
                lane_base_style(L, px, py, 27, dep, kc)
                L.glyph(KIND[u['kind']][1], 42, (px, py), WHITE)
            elif it == 'was':
                L.text((px - 8, py + 1), '%d' % u['raw'], 22, 'mono', fill=(230, 235, 245), anchor='mm', stroke=2)
                arrow(L, px + 14, py, AMBER, 6, 3)
            elif it == 'val':
                col = AMBER if wounded else (WHITE if not dead else (170, 170, 180))
                L.text((px, py + 1), str(val), 36, 'anton', fill=col, anchor='mm', stroke=2.2)
                if dead:
                    L.line([(px - 20, py + 14), (px + 20, py - 14)], RED, 4)
            elif it == 'hp':
                txt = '%d>%d' % (a, b) if change else str(a)
                col = RED if change else GREEN
                wid = L.tw(txt, 19, 'anton') + 17
                L.glyph('X_HP', 14, (px - wid / 2 + 7, py), col)
                L.text((px + 7, py + 1), txt, 19, 'anton', fill=col, anchor='mm', stroke=2)
            elif it == 'arr':
                lane = LANE[dep]
                sd = str(u['land'])
                arrow(L, px - 12, py, lane['col'], 7, 3)
                L.text((px + 12, py + 1), sd, 22, 'anton', fill=WHITE, anchor='mm', stroke=2)
        ids.append((u['id'], dep, s, (x, y)))
    return ids


def aim_lines(L, f):
    """this turn's guns (the default fire): cyan radial tracer from the firing slice to its target with the shot number; a gun with no target says so."""
    for e in f['log']:
        if e[0] != 'fire':
            continue
        s, dep = e[1], e[5]
        if e[3] is None:
            L.line([sec_pt(s, RS['s1'] + 2), sec_pt(s, RS['c0'] + 20)], CYAN, 2, dash=(4, 8))
            xx_, yy_ = sec_pt(s, RS['c0'] + 34)
            L.rect([xx_ - 52, yy_ - 12, xx_ + 52, yy_ + 12], fill=(6, 12, 24, 235), outline=CYAN, w=2, r=6)
            L.text((xx_, yy_ + 1), 'NO TARGET', 16, 'mono', fill=CYAN)
            continue
        p0 = sec_pt(s, RS['s1'] + 2)
        p1 = cpt(dep, s, 0, -22)
        L.line([p0, p1], CYAN, 2.5, dash=(8, 5))
        x, y = p1
        L.ellipse([x - 5, y - 5, x + 5, y + 5], fill=CYAN)
        tx_, ty_ = cpt(dep, s, -88, -6)
        if e[4]:
            lab = '-%d' % e[4]
            w_ = L.tw(lab, 22, 'anton') + 14
            L.rect([tx_ - w_ / 2, ty_ - 14, tx_ + w_ / 2, ty_ + 14], fill=(6, 12, 24, 245), outline=CYAN, w=2.5, r=6)
            L.text((tx_, ty_ + 1), lab, 22, 'anton', fill=CYAN)


def slice_badges(L, f, beat, cons):
    """HP badge per slice (bible 3.8 outer clockwise corner). States: holds-at-1 vs BROKEN are different words and shapes."""
    for w in f['wheel']:
        s = w['sector']
        a, b = w['hp'], w['hp_after']
        x, y = sec_pt(s, 146, 21)
        up = b > a
        txt = '%d>%d' % (a, b) if b != a else str(a)
        broken = b == 0 and a > 0
        holds = (w['t'] == 'SHIELD' and b == 1 and a > 1)
        col = GREEN if (b == a or up) else (RED if broken else AMBER)
        wd = L.tw(txt, 20, 'anton') + 30
        L.rect([x - wd / 2, y - 14, x + wd / 2, y + 14], fill=(6, 10, 18, 245), outline=col, w=2.5, r=7)
        L.glyph('X_HP', 15, (x - wd / 2 + 13, y), col)
        L.text((x + 8, y + 1), txt, 20, 'anton', fill=col, anchor='mm')
        blocked = [e for e in f['log'] if e[0] == 'hit' and e[3] == s and e[6] > 0]
        if beat == 'p3' and blocked and not broken:
            lab = 'BLOCKED %d' % blocked[0][6]
            lw_ = L.tw(lab, 16, 'mono') + 12
            L.rect([x - lw_ / 2, y + 16, x + lw_ / 2, y + 36], fill=(6, 10, 18, 245), outline=CYAN, w=2, r=5)
            L.text((x, y + 27), lab, 16, 'mono', fill=CYAN, anchor='mm')
        elif broken or holds:
            lab = 'BROKEN' if broken else 'HOLDS 1'
            lw_ = L.tw(lab, 16, 'mono') + 12
            L.rect([x - lw_ / 2, y + 16, x + lw_ / 2, y + 36], fill=(6, 10, 18, 245), outline=col, w=2, r=5)
            L.text((x, y + 27), lab, 16, 'mono', fill=col, anchor='mm')
        if broken and beat != 'p3':
            for k in range(-6, 7):
                a0 = 60 * s + k * 4.2
                L.line([ppx(C, RS['s0'] + 10, a0), ppx(C, RS['s1'] - 6, a0 + 6)], (255, 80, 70, 150), 2)


def threat_trim(L, f):
    """amendment 4: red LED trim on the slice that will be hit this turn (solid) and next turn (pink dashed)."""
    now = {}
    for e in f['log']:
        if e[0] == 'hit':
            now[e[3]] = now.get(e[3], 0) + e[4]
    nxt = f['next']['raw_per_sector']
    for s in range(6):
        if s in now:
            L.line(L.arc_pts(C, RS['s1'] - 1, 60 * s - 25, 60 * s + 25), RED, 5)
        elif nxt[s]:
            L.line(L.arc_pts(C, RS['s1'] - 1, 60 * s - 25, 60 * s + 25), (255, 61, 168), 2.5, dash=(8, 5))
