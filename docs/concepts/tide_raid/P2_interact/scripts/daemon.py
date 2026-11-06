"""Black ICE daemons. Each beam type has its own silhouette (shape first, hue second):
  D DRONE     thin chain of diamond links, sharp arrowhead with swept wings        (blue)
  N NETRUNNER braided double strand (sine rope) with rungs, square cursor-head     (magenta)
  E ENFORCER  fat armoured hazard-striped blocks, blunt horned ram-head, one lens  (signal yellow)
Black ICE = black body, neon rim, white-hot spine: it reads against plum and against a lit lattice."""
import math
import numpy as np
from lib import *

GAP = {'D': 15.0, 'N': 4.0, 'E': 23.0}
HW = {'D': 9.5, 'N': 8.0, 'E': 14.0}
LEN = {'D': 190.0, 'N': 200.0, 'E': 170.0}
HEAD_LEN = {'D': 26, 'N': 20, 'E': 26}


def lane(pts, d):
    """offset a polyline sideways by d px (right-hand traffic: opposing worms use opposite lanes)."""
    if abs(d) < .01:
        return pts
    out = []
    n = len(pts)
    for i in range(n):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        t = b - a
        L = np.hypot(*t)
        t = t / L if L > 1e-6 else np.array([1., 0.])
        out.append(pts[i] + np.array([-t[1], t[0]]) * d)
    return np.array(out)


def extend_back(pts, vec=(0.84, -0.54), length=520):
    v = np.array(vec) * length
    return np.vstack([pts[0] + v, pts])


def _frame(path, s):
    p, ang = at(path, s)
    u = np.array([math.cos(ang), math.sin(ang)])
    return p, u, np.array([-u[1], u[0]])


def head_shape(typ, p, u, n, sc=1.0):
    """returns dict of polygons (fill, rim lines) for the head, centred on p, pointing along u."""
    if typ == 'D':
        tip = p + u * 30 * sc
        b1 = p - u * 2 * sc + n * 13 * sc
        b2 = p - u * 2 * sc - n * 13 * sc
        w1 = p - u * 17 * sc + n * 23 * sc
        w2 = p - u * 17 * sc - n * 23 * sc
        return {'fill': [[tip, b1, p - u * 10 * sc, b2]], 'rim': [[tip, b1, w1, p - u * 8 * sc, w2, b2, tip]], 'eye': (p + u * 7 * sc, 3.6 * sc)}
    if typ == 'N':
        r = 14 * sc
        c = p + u * 4 * sc
        sq = [c + u * r + n * r, c + u * r - n * r, c - u * r - n * r, c - u * r + n * r]
        notch = [c + u * r * 1.0 + n * r * .35, c + u * r * 1.0 - n * r * .35]
        return {'fill': [sq], 'rim': [sq + [sq[0]]], 'cursor': (c, u, n, r), 'ant': [[c + u * r + n * r * .7, c + u * (r + 12 * sc) + n * r * 1.1],
                                                                                     [c + u * r - n * r * .7, c + u * (r + 12 * sc) - n * r * 1.1]]}
    # E: blunt ram with two forward horns
    c = p + u * 2 * sc
    hw = 19 * sc
    body = [c + u * 14 * sc + n * hw, c + u * 14 * sc - n * hw, c - u * 14 * sc - n * (hw + 3 * sc), c - u * 14 * sc + n * (hw + 3 * sc)]
    horn1 = [c + u * 14 * sc + n * hw, c + u * 33 * sc + n * (hw + 5 * sc), c + u * 14 * sc + n * (hw - 9 * sc)]
    horn2 = [c + u * 14 * sc - n * hw, c + u * 33 * sc - n * (hw + 5 * sc), c + u * 14 * sc - n * (hw - 9 * sc)]
    return {'fill': [body, horn1, horn2], 'rim': [body + [body[0]], horn1 + [horn1[0]], horn2 + [horn2[0]]], 'eye': (c + u * 6 * sc, 6.0 * sc)}


def daemon_masks(path, s_head, typ, length=None, mode='full', sc=1.0, phase=0.0):
    length = (LEN[typ] if length is None else length) * sc
    gap = GAP[typ] * sc
    hw0 = HW[typ] * sc
    bpts = sub(path, max(0, s_head - length * 2.7 - 40), s_head + 60, 20)
    bb = pbox(bpts, 70)
    fill, rim, spine, accent = Lyr(bb), Lyr(bb), Lyr(bb), Lyr(bb)
    nseg = int(length / gap)
    ghost = mode == 'ghost'
    if typ == 'N':
        # two braided strands sampled finely, tapering toward the tail
        step = 3.0
        ns = int(length / step)
        S0 = []
        S1 = []
        for i in range(ns + 1):
            s = s_head - 14 * sc - i * step
            if s < 0:
                break
            p, u, n = _frame(path, s)
            t = i / ns
            A = (9.5 - 5.0 * t) * sc
            ph = (s + phase) / 11.0
            S0.append(p + n * A * math.sin(ph))
            S1.append(p - n * A * math.sin(ph))
            if i % 4 == 2 and not ghost:  # rungs
                rim.line([tuple(S0[-1]), tuple(S1[-1])], 1.6 * sc, int(255 * (1 - t * .7)) )
        wv = 4.2 * sc
        for st in (S0, S1):
            if len(st) > 2:
                if not ghost:
                    fill.line([tuple(q) for q in st], wv + 4.5 * sc, 255)
                for i in range(0, len(st) - 1, 6):
                    seg = st[i:i + 7]
                    v = int(255 * (1 - .75 * i / max(len(st), 1)))
                    rim.line([tuple(q) for q in seg], wv, v)
                    spine.line([tuple(q) for q in seg], wv * .38, v)
    else:
        for i in range(nseg, 0, -1):
            s = s_head - (HEAD_LEN[typ] * .6 + i * gap) * sc
            if s < 0:
                continue
            p, u, n = _frame(path, s)
            t = i / nseg
            v = int(255 * (1 - .72 * t))
            w = hw0 * (1 - .45 * t)
            if typ == 'D':
                hl = gap * .62
                q = [p + u * hl, p + n * w, p - u * hl, p - n * w]
                if not ghost:
                    fill.poly([tuple(x) for x in q], 255)
                rim.line([tuple(x) for x in q + [q[0]]], 2.0 * sc, v)
                spine.ell(tuple(p), 1.7 * sc, v=v)
            else:
                hl = gap * .46
                q = [p + u * hl + n * w, p + u * hl - n * w, p - u * hl - n * w, p - u * hl + n * w]
                if not ghost:
                    fill.poly([tuple(x) for x in q], 255)
                rim.line([tuple(x) for x in q + [q[0]]], 2.6 * sc, v)
                # hazard stripes: two diagonal bars
                for k in (-.45, .35):
                    sp = [p + u * (hl * k - 3 * sc) + n * w * .9, p + u * (hl * k + 3 * sc) + n * w * .9,
                          p + u * (hl * k + 3 * sc + 5 * sc) - n * w * .9, p + u * (hl * k - 3 * sc + 5 * sc) - n * w * .9]
                    accent.poly([tuple(x) for x in sp], int(v * .85))
    # head
    p, u, n = _frame(path, s_head)
    hs = head_shape(typ, p, u, n, sc)
    for poly in hs['fill']:
        if not ghost:
            fill.poly([tuple(x) for x in poly], 255)
    for line in hs['rim']:
        rim.line([tuple(x) for x in line], 3.0 * sc if not ghost else 2.0 * sc, 255)
    if 'eye' in hs and not ghost:
        spine.ell(tuple(hs['eye'][0]), hs['eye'][1], v=255)
    if 'cursor' in hs and not ghost:
        c, u2, n2, r = hs['cursor']
        q = [c + u2 * r * .45 + n2 * r * .45, c + u2 * r * .45 - n2 * r * .45, c - u2 * r * .45 - n2 * r * .45, c - u2 * r * .45 + n2 * r * .45]
        spine.poly([tuple(x) for x in q], 255)
        for a in hs['ant']:
            rim.line([tuple(x) for x in a], 2.0 * sc, 255)
    if typ == 'E' and not ghost:
        # lens ring around the eye
        accent.ell(tuple(hs['eye'][0]), hs['eye'][1] * 1.9, v=255, outline=True, ow=1.6)
    return fill, rim, spine, accent


def draw_daemon(cv, path, s_head, typ, mode='full', length=None, sc=1.0, alpha=1.0, phase=0.0, trail=True):
    col = TYPE_COL[typ]
    fill, rim, spine, accent = daemon_masks(path, s_head, typ, length, mode, sc, phase)
    OF = rim.off
    if mode == 'ghost':
        cv.neon(rim.m, col, core=.75 * alpha, g1=(3, .35 * alpha), g2=None, off=OF)
        return
    if mode == 'dead':
        cv.over(INK, fill.m, .85 * alpha, OF)
        cv.add(col * .35 + np.array([.12, .1, .14], np.float32), rim.m, .8 * alpha, OF)
        return
    # speed streaks behind the tail (motion read in a still)
    if trail:
        tl = Lyr(rim.im and (OF[0], OF[1], OF[0] + rim.w, OF[1] + rim.h), pad=0)
        ln = (LEN[typ] if length is None else length) * sc
        for k in (-5, 0, 5):
            a = s_head - ln * .85
            b = s_head - ln * 1.35
            if b > 0 or a > 0:
                pts = sub(path, max(0, b), max(0, a), 4)
                if len(pts) > 1:
                    pp = lane(pts, k)
                    tl.line([tuple(x) for x in pp], 1.2, 140, dash=(5, 7))
        cv.add(col, tl.m, .45 * alpha, tl.off)
    cv.add(col, blur(fill.m, 9), .28 * alpha, OF)            # underglow: black ICE still lights its street
    cv.over(INK, fill.m, .93 * alpha, OF)
    cv.neon(rim.m, col, core=1.0 * alpha, g1=(3.5, .85 * alpha), g2=(13, .65 * alpha), off=OF)
    cv.add(col * .9, accent.m, .95 * alpha, OF)
    cv.add(WHITE, spine.m, .95 * alpha, OF)
    cv.add(col, blur(spine.m, 4), .5 * alpha, OF)
