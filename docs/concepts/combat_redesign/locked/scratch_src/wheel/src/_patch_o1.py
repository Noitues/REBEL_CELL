import re
p = 'asm_units.py'
s = open(p, encoding='utf-8').read()

# 1. badge direction with side
s = s.replace('''def badge_dir(u):
    """unit vector''', '''CTX = {}            # set by draw_unit: frame, L, chevron counts (for the collision test)
ASSERT_LOG = []     # (name, unit, badge, side, counts) rows for the O1 asserts


def badge_dir(u, side='out'):
    """unit vector''')
s = s.replace("    vx, vy = -t[0] + n[0], -t[1] + n[1]\n", "    sg = 1.0 if side == 'out' else -1.0\n    vx, vy = -t[0] + sg * n[0], -t[1] + sg * n[1]\n")
s = s.replace('''def badge_xy(u, dist=BADGE_D):
    x, y = E8.token_pos(u)
    dx, dy = badge_dir(u)''', '''def badge_xy(u, dist=BADGE_D, side='out'):
    x, y = E8.token_pos(u)
    dx, dy = badge_dir(u, side)''')
s = s.replace('''def fit_badge(u, shape, size0, min_size):''', '''def _pts(shape, bx, by, size):
    """1 px grid points of the badge incl. its ink rim"""
    r = size + 2.5
    xs = np.arange(int(bx - r) - 1, int(bx + r) + 2)
    ys = np.arange(int(by - r) - 1, int(by + r) + 2)
    X, Y = np.meshgrid(xs + 0.5, ys + 0.5)
    if shape == 'dia':
        m = (np.abs(X - bx) + np.abs(Y - by)) <= r
    else:
        m = np.hypot(X - bx, Y - by) <= r
    return X[m], Y[m]


def _pol(X, Y):
    return np.hypot(X - C[0], Y - C[1]), np.degrees(np.arctan2(X - C[0], -(Y - C[1]))) % 360.0


def _adiff(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def hits(u, shape, size, side):
    """px of the badge (with rim) that fall on: ring tag boxes, HP tray, chevron column, token glyph"""
    bx, by = badge_xy(u, BADGE_D, side)
    X, Y = _pts(shape, bx, by, size)
    out = {}
    f, L = CTX.get('f'), CTX.get('L')
    n = 0
    if f is not None and L is not None:
        import r2_misc as M2
        m = np.zeros(X.shape, bool)
        for d in range(3):
            x, y, wd, _, _ = M2.tag_geom(L, d, f['rings_wave'][d], 'P')
            m |= (np.abs(X - x) <= wd / 2 + 2.0) & (np.abs(Y - y) <= 13 + 2.0)
        n = int(m.sum())
    out['tag'] = n
    rr, aa = _pol(X, Y)
    ly = W2U.cell_layout(u)
    per = max(1, u['mx'] // u['w'])
    mt = np.zeros(X.shape, bool)
    mc = np.zeros(X.shape, bool)
    ri, ro = CB.ring_geom(u['dep'])
    nh = CTX.get('nchev', 0)
    st = W2U.chev_params(u, nh) if nh else None
    for q in range(u['w']):
        a_start, tot, rm = W2U.tray_extent(u, q, per)
        a0 = a_start - math.degrees(2.6 / rm)
        a1 = a_start + math.degrees((tot + 2.6) / rm)
        inb = ((_adiff(aa, a0) >= 0) & (_adiff(aa, a1) <= 0) & (_adiff(a1, a0) >= 0))
        mt |= inb & (rr >= ly['t_in'] - 1.0) & (rr <= ly['t_out'] + 1.0)
        if st:
            axis = 60 * (u['s'] + q)
            lat = np.abs(np.radians(_adiff(aa, axis))) * rr
            rtop = ri + st['start'] + (nh - 1) * st['pitch'] + st['depth'] + 5.25 + 1.2 + 2.5
            mc |= (lat <= max(st['half'] + st['ink'] / 2.0, 17.0)) & (rr >= ri + st['start'] - 2.0) & (rr <= rtop)
    out['tray'] = int(mt.sum())
    out['chev'] = int(mc.sum())
    g, half = _glyph_grid(u['kind'])
    x0, y0 = E8.token_pos(u)
    gi = np.clip(((X - x0 + half) * SS).astype(int), 0, g.shape[1] - 1)
    gj = np.clip(((Y - y0 + half) * SS).astype(int), 0, g.shape[0] - 1)
    out['glyph'] = int(g[gj, gi].sum())
    return out


def pick_side(u, shape, size):
    """O1: try the outer start-cap diagonal; if the badge box touches a ring tag / HP tray / chevron column mirror it to the inner diagonal"""
    ho = hits(u, shape, size, 'out')
    if sum(ho.values()) == 0:
        return 'out', ho
    hi = hits(u, shape, size, 'in')
    if sum(hi.values()) < sum(ho.values()):
        return 'in', hi
    return 'out', ho


def fit_badge(u, shape, size0, min_size, side='out'):''')
s = s.replace("    dx, dy = badge_dir(u)\n    off = (dx * BADGE_D, dy * BADGE_D)", "    dx, dy = badge_dir(u, side)\n    off = (dx * BADGE_D, dy * BADGE_D)")
s = s.replace('''def warded_badge(L, u, size):
    bx, by = badge_xy(u)''', '''def warded_badge(L, u, size, side='out'):
    bx, by = badge_xy(u, BADGE_D, side)''')
s = s.replace('''def dead_badge(L, u, r):
    bx, by = badge_xy(u)''', '''def dead_badge(L, u, r, side='out'):
    bx, by = badge_xy(u, BADGE_D, side)''')
s = s.replace('''            size, ov = fit_badge(u, 'dia', 15, 11)       # 30 px lozenge, 16 px skull
            BADGE_LOG.append(dict(uid=u['id'], kind=u['kind'], badge='warded', size=size * 2, overlap_px=ov))
            warded_badge(L, u, size)''', '''            CTX['L'] = L
            side, h = pick_side(u, 'dia', 15)
            size, ov = fit_badge(u, 'dia', 15, 11, side)       # 30 px lozenge, 16 px skull
            h = hits(u, 'dia', size, side)
            BADGE_LOG.append(dict(uid=u['id'], kind=u['kind'], badge='warded', size=size * 2, overlap_px=ov, side=side, hits=h))
            warded_badge(L, u, size, side)''')
s = s.replace('''            size, ov = fit_badge(u, 'disc', 13, 9)       # 26 px badge
            BADGE_LOG.append(dict(uid=u['id'], kind=u['kind'], badge='dead', size=size * 2, overlap_px=ov))
            dead_badge(L, u, size)''', '''            CTX['L'] = L
            side, h = pick_side(u, 'disc', 13)
            size, ov = fit_badge(u, 'disc', 13, 9, side)       # 26 px badge
            h = hits(u, 'disc', size, side)
            BADGE_LOG.append(dict(uid=u['id'], kind=u['kind'], badge='dead', size=size * 2, overlap_px=ov, side=side, hits=h))
            dead_badge(L, u, size, side)''')
s = s.replace('''    dying = u['fate']['kind'] == 'dies'
    grow = max(0, u['land_hit'] - u['hit']) if (u['fate']['kind'] == 'lands' and 'land_hit' in u) else 0
''', '''    dying = u['fate']['kind'] == 'dies'
    grow = max(0, u['land_hit'] - u['hit']) if (u['fate']['kind'] == 'lands' and 'land_hit' in u) else 0
    CTX['f'] = f
    CTX['nchev'] = u['hit'] + grow
''')
s = s.replace("from e10lib import REG\n", "from e10lib import REG\nimport cv_board as CB\nfrom e10lib import C\n")
open(p, 'w', encoding='utf-8').write(s)
