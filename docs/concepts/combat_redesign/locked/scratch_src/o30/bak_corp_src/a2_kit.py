"""R2 ACTIONS kit.  focus_brackets (3 options, ONE drawing for help / UNDO / SEND IT / cards / cells / slices) and the RAM coin refund token (merged).
Everything at 1080p coordinates, drawn into an L2 layer (2x)."""
import sys, math
sys.dont_write_bytecode = True
from a_kit import *      # LIME, wax, pink, tally, vinyl2, ... (R1 kit, unchanged parts)

FB_W = 4.0               # lime stroke
FB_INK = 4.5             # ink keyline total extra


def _rot(pts, c, deg):
    if not deg:
        return pts
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(c[0] + (x - c[0]) * ca - (y - c[1]) * sa, c[1] + (x - c[0]) * sa + (y - c[1]) * ca) for x, y in pts]


def _stroke(L, arms, col, w):
    for p in arms:
        L.line(list(p), INK, w + FB_INK)
    for p in arms:
        L.line(list(p), col, w)


def fb_arms(shape, g, arm=None, grow=4.0):
    """returns (corner arms, frame polyline, mid ticks) for a shape.
    rect:   g=dict(box=(x0,y0,x1,y1), tilt=deg)         circle: g=dict(c=(x,y), r=r)
    band:   g=dict(ri,ro,a0,a1)  (cells, slices; polar, arms follow the arc and the radial edge)"""
    arms, frame, ticks = [], [], []
    if shape in ('rect', 'circle'):
        if shape == 'circle':
            (cx, cy), r = g['c'], g['r']
            x0, y0, x1, y1 = cx - r, cy - r, cx + r, cy + r
            tilt = 0
        else:
            x0, y0, x1, y1 = g['box']
            tilt = g.get('tilt', 0)
        x0, y0, x1, y1 = x0 - grow, y0 - grow, x1 + grow, y1 + grow
        a = arm or max(8.0, min(26.0, 0.26 * min(x1 - x0, y1 - y0)))
        cc = ((x0 + x1) / 2, (y0 + y1) / 2)
        raw = [[(x0, y0 + a), (x0, y0), (x0 + a, y0)], [(x1 - a, y0), (x1, y0), (x1, y0 + a)],
               [(x0, y1 - a), (x0, y1), (x0 + a, y1)], [(x1 - a, y1), (x1, y1), (x1, y1 - a)]]
        arms = [_rot(p, cc, tilt) for p in raw]
        frame = _rot([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], cc, tilt)
        mids = [((x0 + x1) / 2, y0, 0, 1), ((x0 + x1) / 2, y1, 0, -1), (x0, (y0 + y1) / 2, 1, 0), (x1, (y0 + y1) / 2, -1, 0)]
        for mx, my, dx, dy in mids:
            ticks.append(_rot([(mx, my), (mx + dx * 7, my + dy * 7)], cc, tilt))
    else:
        ri, ro, a0, a1 = g['ri'], g['ro'], g['a0'], g['a1']
        ar = arm or 24.0
        ri, ro = ri - grow * 0.5, ro + grow * 0.5
        for r_edge, rs in ((ri, 1), (ro, -1)):
            for ang, sg in ((a0, 1), (a1, -1)):
                da = ar / r_edge * 57.3
                corner = ppx(C, r_edge, ang)
                along = [ppx(C, r_edge, ang + sg * da * k / 4) for k in range(5)]
                rad = ppx(C, r_edge + rs * ar, ang)
                arms.append(along[::-1] + [corner, rad])
        n = 24
        frame = [ppx(C, ro, a0 + (a1 - a0) * i / n) for i in range(n + 1)] + [ppx(C, ri, a1 - (a1 - a0) * i / n) for i in range(n + 1)]
        frame.append(frame[0])
        am, rm = (a0 + a1) / 2, (ri + ro) / 2
        ticks = [[ppx(C, ri, am), ppx(C, ri + 7, am)], [ppx(C, ro, am), ppx(C, ro - 7, am)],
                 [ppx(C, rm, a0), ppx(C, rm, a0 + 7 / rm * 57.3)], [ppx(C, rm, a1), ppx(C, rm, a1 - 7 / rm * 57.3)]]
    return arms, frame, ticks


def focus_brackets(L, shape, g, opt='A', w=FB_W, arm=None, grow=4.0, col=LIME):
    """THE focus mark (bible 2.10). A: four lime L-brackets 4 px + 4.5 px ink, 4 px off the element.
    B: A + a short lock tick at each edge midpoint.  C: A + a 1.4 px lime hairline frame at 45 percent."""
    arms, frame, ticks = fb_arms(shape, g, arm, grow)
    if opt == 'C':
        L.line(frame, INK + (110,), 3.2)
        L.line(frame, col + (115,), 1.4)
    _stroke(L, arms, col, w)
    if opt == 'B':
        _stroke(L, ticks, col, max(2.4, w - 1.0))


# ---------------------------------------------------------------------------- refund token: the RAM coin + 3 px INK plus
def coin(L, cx, cy, size, plus_w=3.0, ring=True):
    import obj2      # ASSEMBLY (Y4): the one RAM coin, refund token = plus=True
    obj2.draw_coin(L, cx, cy, size, 'lit', plus=True)


def refund_token(L, cx, cy, size, opt='A'):
    """one coin; fixed ladder board 44 / row 30 / chip 26 / strip 20.  A: pale cyan star (board), halo (row, chip), coin only (strip).
    B (variant): cyan ray ticks around the coin at board, row and chip, coin only at the strip."""
    big, mid = size >= 40, 24 <= size < 40
    if opt == 'A':
        if big:
            n = 8
            pts = []
            for i in range(2 * n):
                rr = size * (0.80 if i % 2 == 0 else 0.52)
                a = math.radians(-90 + 180 * i / n)
                pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
            L.poly(pts, fill=(190, 244, 255), outline=INK, w=2)
        elif mid:
            r = size / 2 + 3.2
            L.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, w=4.4)
            L.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(190, 244, 255), w=2.0)
    else:
        if big or mid:
            n = 8 if big else 6
            for i in range(n):
                a = 360 / n * i + 22
                p0, p1 = ppx((cx, cy), size * 0.62, a), ppx((cx, cy), size * (0.88 if big else 0.82), a)
                L.line([p0, p1], INK, 5.0)
                L.line([p0, p1], (190, 244, 255), 2.4)
    coin(L, cx, cy, size * (0.9 if big else 0.92 if mid else 1.0))
