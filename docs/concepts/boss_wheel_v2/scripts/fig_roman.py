"""Boss Wheel v2: Aurelian Concord (Roman) figures as layered silhouette masks.

Each figure function draws into Pens and returns a dict of named L masks at the requested pixel size:
  'back'  (depth layer behind, lit less), 'main' (the figure), 'detail' (interior lines to light), 'glint' (metal).
Unit box is 400 x 300 (x right, y down), ground line y = 262. t = idle time in seconds, act = 0..1 action progress.
"""
import math

from PIL import Image

from shapes import Pen, leg

UW, UH = 400, 300
GROUND = 262


def _pens(px, names=("back", "main", "detail", "glint"), flip=False, fit=1.0, ax=200.0, ay=GROUND):
    """fit < 1 shrinks the figure about the anchor (ax, ay) (unit coords) so it sits inside the slice window."""
    k = px / UW
    size = (px, int(UH * k))
    kk = k * fit
    ox, oy = ax * k - ax * kk, ay * k - ay * kk
    if flip:
        ox = ax * k + ax * kk
    return {n: Pen(size, kk, ox, oy, flip=flip) for n in names}, k


def _out(pens):
    return {n: p.m for n, p in pens.items()}


# ------------------------------------------------------------------ horse
def horse(p, det, x, y, s, ph, head_up=0.0):
    """Galloping horse facing right; (x,y) barrel centre; ph = gallop phase 0..1."""
    def T(pts):
        return [(x + a * s, y + b * s) for a, b in pts]
    S = math.sin(2 * math.pi * ph)
    Cc = math.cos(2 * math.pi * ph)
    rise = -4 * S
    y += rise * s
    body = [(-64, -8), (-48, -24), (-10, -27), (30, -26), (58, -18), (72, 0), (62, 20), (18, 26), (-30, 23), (-60, 16), (-74, 2)]
    p.blob(T(body))
    # neck + head (stretched forward)
    hu = head_up * 10
    p.limb(T([(42, -14), (70, -44 - hu), (90, -64 - hu)]), 44 * s, 24 * s)
    head = [(82, -82), (98, -86), (118, -72), (136, -54), (138, -44), (128, -40), (108, -50), (88, -58)]
    p.blob(T([(a, b - hu) for a, b in head]))
    p.poly(T([(88, -80 - hu), (80, -100 - hu), (96, -84 - hu)]))   # ear
    # mane streaming back
    for j in range(7):
        bx, by = 52 + j * 6.5, -30 - j * 8 - hu * j / 7
        p.poly(T([(bx, by), (bx - 26 - j * 2, by - 6 + 4 * math.sin(ph * 6.28 + j)), (bx + 6, by - 8)]))
    # tail streaming
    for j, (dy, ln) in enumerate(((-10, 70), (-2, 62), (6, 54))):
        w = 6 * math.sin(ph * 6.28 + j)
        p.limb(T([(-70, -6 + j * 3), (-100, dy - 14 + w), (-70 - ln, dy - 8 - w)]), 10 * s, 2 * s)
    # legs: front pair reaches, hind pair drives
    for k_, off in ((0, 0.0), (1, 0.18)):
        q = math.sin(2 * math.pi * (ph + off))
        c = math.cos(2 * math.pi * (ph + off))
        fold = max(0.0, c)
        a1 = 95 - 48 * q
        a2 = a1 + 10 + 85 * fold
        a3 = a2 - 20 - 40 * fold
        leg(p, T([(52 - k_ * 10, 10)])[0], 26 * s, 26 * s, 20 * s, a1, a2, a3, 20 * s, 11 * s, 8 * s, hoof=5 * s)
        a1 = 85 + 45 * q
        a2 = a1 - 50 - 30 * (1 - fold)
        a3 = a2 + 60
        leg(p, T([(-50 - k_ * 8, 6)])[0], 30 * s, 28 * s, 22 * s, a1, a2, a3, 26 * s, 12 * s, 8 * s, hoof=5 * s)
    # harness detail
    det.line(T([(40, -20), (58, 4)]), 3 * s)
    det.line(T([(108, -56 - hu), (118, -64 - hu)]), 3 * s)


def chariot(px, t=0.0, act=0.0, flip=False):
    """SHIM (attack): a two-horse chariot charging. act: 0 = trotting in place, 1 = full charge (lunge right)."""
    pens, k = _pens(px, flip=flip, fit=0.9, ax=190)
    p, b, det, gl = pens["main"], pens["back"], pens["detail"], pens["glint"]
    ph = (t * 1.6 + act * 1.2) % 1.0
    lunge = 70 * (act ** 0.6) - 30 * act * act
    lean = 8 * act
    X = 240 + lunge
    # back horse (depth)
    horse(b, pens["detail"], X + 26, 168, 0.92, (ph + 0.35) % 1, head_up=0.3)
    horse(p, det, X, 180, 1.0, ph, head_up=0.0)
    # pole and yoke
    p.limb([(X - 110, 200), (X - 40, 176), (X + 50, 160)], 6, 5)
    # car
    cx = X - 132
    p.blob([(cx - 34, 150), (cx + 14, 148), (cx + 34, 130), (cx + 40, 156), (cx + 34, 212), (cx - 30, 214), (cx - 40, 186)])
    gl.line([(cx + 34, 132), (cx + 40, 156), (cx + 34, 210)], 4)
    # wheel with spokes (cut)
    wx, wy, wr = cx - 4, 222, 38
    p.ell(wx, wy, wr, wr)
    spin = t * 520 + act * 300
    for j in range(8):
        a = math.radians(spin + j * 45)
        a2 = math.radians(spin + j * 45 + 30)
        p.poly([(wx + 8 * math.cos(a), wy + 8 * math.sin(a)), (wx + 30 * math.cos(a), wy + 30 * math.sin(a)),
                (wx + 30 * math.cos(a2), wy + 30 * math.sin(a2)), (wx + 8 * math.cos(a2), wy + 8 * math.sin(a2))], fill=0)
    det.ell(wx, wy, 6, 6)
    gl.ell(wx, wy, wr - 1, wr - 1)
    gl.ell(wx, wy, wr - 5, wr - 5, fill=0)
    # charioteer
    hx, hy = cx + 6 + lean, 96
    p.limb([(cx - 8, 150), (cx - 2, 124), (hx - 2, hy + 18)], 22, 26)          # legs + hips
    p.blob([(hx - 18, hy + 12), (hx + 14, hy + 4), (hx + 20, hy + 34), (hx + 4, hy + 56), (hx - 20, hy + 50)])  # torso
    p.ell(hx + 6, hy - 6, 12, 13)                                              # head
    p.blob([(hx - 6, hy - 18), (hx + 16, hy - 20), (hx + 22, hy - 8), (hx - 8, hy - 6)])  # helmet
    for j in range(6):                                                         # horsehair crest
        a = -150 + j * 14
        p.limb([(hx + 4, hy - 18), (hx + 4 + 30 * math.cos(math.radians(a)) - 8, hy - 22 + 18 * math.sin(math.radians(a)))], 6, 2)
    # cloak flowing back
    fl = math.sin(t * 7) * 6
    p.blob([(hx - 14, hy + 8), (hx - 50, hy + 2 + fl), (hx - 92, hy + 10 - fl), (hx - 70, hy + 30 + fl), (hx - 30, hy + 44), (hx - 12, hy + 36)])
    # arms: reins forward, whip raised back
    p.limb([(hx + 12, hy + 16), (hx + 40, hy + 30), (hx + 64, hy + 24)], 9, 7)
    wa = -60 + 70 * act + 10 * math.sin(t * 5)
    ex, ey = hx - 4 + 30 * math.cos(math.radians(wa - 120)), hy + 10 + 30 * math.sin(math.radians(wa - 120))
    p.limb([(hx - 6, hy + 14), (ex, ey)], 9, 7)
    det.line([(hx + 64, hy + 24), (X + 100, 112 + 12)], 1.8)                   # reins
    det.line([(hx + 64, hy + 24), (X + 126, 100 + 12)], 1.8)
    wh = [(ex, ey), (ex - 30, ey - 40), (ex - 10, ey - 80), (ex + 40, ey - 96)]
    p.limb(wh[:2], 3, 2)
    det.line(wh[1:], 2)
    # dust kicked up
    return _out(pens)


# ------------------------------------------------------------------ lion
def lion(px, t=0.0, act=0.0, flip=False):
    """OVERFLOW (crit): an arena lion. act 0 = crouched, tail lashing; 1 = mid-leap, claws out, roaring."""
    pens, k = _pens(px, flip=flip, fit=0.9, ax=190)
    p, det, gl = pens["main"], pens["detail"], pens["glint"]
    a = act
    lift = -60 * math.sin(math.pi * min(1, a * 1.1)) if a > 0 else 0
    x0 = 190 + 50 * a
    y0 = 196 + lift - 4 * math.sin(t * 2.1) * (1 - a)
    tilt = -14 * a
    def R(pts):
        c, s_ = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
        return [(x0 + u * c - v * s_, y0 + u * s_ + v * c) for u, v in pts]
    stretch = 1 + 0.25 * a
    body = [(-90 * stretch, -10), (-60 * stretch, -26), (0, -30), (40, -34), (62, -22), (66, 6), (40, 24), (-20, 26), (-70 * stretch, 22), (-98 * stretch, 8)]
    p.blob(R(body))
    # mane: a ragged cloud around the neck and head
    mx, my = 62, -30
    pts = []
    for j in range(22):
        ang = 2 * math.pi * j / 22
        rr = (44 if j % 2 == 0 else 32) + 6 * math.sin(j * 1.7 + t * 2)
        pts.append((mx + rr * math.cos(ang) * 0.95, my + rr * math.sin(ang) * 1.05))
    p.poly(R(pts))
    # head + muzzle; jaw drops open on act
    hx, hy = 96, -30
    p.blob(R([(hx - 18, hy - 22), (hx + 10, hy - 26), (hx + 34, hy - 10), (hx + 40, hy + 2), (hx + 30, hy + 8), (hx + 4, hy + 6), (hx - 16, hy + 8)]))
    jaw = 6 + 22 * a
    p.blob(R([(hx + 2, hy + 4), (hx + 34, hy + 4 + jaw * 0.5), (hx + 30, hy + 10 + jaw), (hx + 4, hy + 14 + jaw * 0.6)]))
    if a > 0.1:
        det.poly(R([(hx + 26, hy + 6), (hx + 30, hy + 14), (hx + 33, hy + 6)]))   # fang
        det.poly(R([(hx + 14, hy + 6), (hx + 18, hy + 14), (hx + 21, hy + 6)]))
    p.poly(R([(hx - 6, hy - 22), (hx - 2, hy - 38), (hx + 8, hy - 24)]))    # ear
    gl.dot(R([(hx + 12, hy - 12)])[0], 3.2)                                 # eye glint
    # legs
    if a < 0.5:
        q = math.sin(t * 1.3) * 3
        leg(p, R([(40, 10)])[0], 30, 26, 14, 112 + q, 96, 20, 22, 14, 11)
        leg(p, R([(30, 12)])[0], 30, 26, 14, 100, 84, 10, 20, 13, 10)
        leg(p, R([(-70 * stretch, 6)])[0], 40, 30, 16, 120, 60, 10, 30, 14, 11)
        leg(p, R([(-80 * stretch, 8)])[0], 40, 30, 16, 130, 66, 6, 28, 13, 10)
    else:
        e = (a - 0.5) * 2
        leg(p, R([(40, 8)])[0], 34, 30, 14, 10 - 10 * e, -20, 30, 22, 14, 11)
        leg(p, R([(30, 10)])[0], 34, 30, 14, 30 - 10 * e, 0, 40, 20, 13, 10)
        leg(p, R([(-70 * stretch, 6)])[0], 44, 34, 18, 160, 130, 170, 30, 14, 11)
        leg(p, R([(-80 * stretch, 8)])[0], 44, 34, 18, 170, 140, 180, 28, 13, 10)
        for c_ in (R([(100, 40)])[0], R([(108, 30)])[0]):                    # claws
            for j in range(3):
                det.poly([(c_[0] + j * 5, c_[1]), (c_[0] + j * 5 + 9, c_[1] + 6), (c_[0] + j * 5 + 3, c_[1] + 2)])
    # tail lashing with tuft
    sw = math.sin(t * 2.6) * 30 * (1 - a) + 30 * a
    tail = R([(-96 * stretch, 0), (-130, -10 - sw * 0.4), (-160, -40 - sw), (-170, -70 - sw * 0.6)])
    p.limb(tail, 9, 5)
    p.ell(tail[-1][0], tail[-1][1], 9, 12, ang=20)
    return _out(pens)


# ------------------------------------------------------------------ shields
def scutum(p, det, gl, cx, cy, w, h, curve=0.18, emblem=True, lean=0.0):
    """A curved rectangular legion shield seen from the front: plate, rim, boss, wing emblem."""
    pts = [(cx - w / 2, cy - h / 2), (cx, cy - h / 2 - h * curve * 0.25), (cx + w / 2, cy - h / 2),
           (cx + w / 2 + lean, cy + h / 2), (cx, cy + h / 2 + h * curve * 0.25), (cx - w / 2 + lean, cy + h / 2)]
    p.poly(pts)
    gl.ell(cx + lean / 2, cy, w * 0.15, w * 0.15)
    if emblem:
        for sgn in (-1, 1):
            det.limb([(cx + sgn * w * 0.12, cy), (cx + sgn * w * 0.3, cy - h * 0.14), (cx + sgn * w * 0.42, cy - h * 0.28)], w * 0.07, w * 0.02)
            det.limb([(cx + sgn * w * 0.12, cy + h * 0.04), (cx + sgn * w * 0.3, cy + h * 0.12), (cx + sgn * w * 0.4, cy + h * 0.3)], w * 0.05, w * 0.015)
        det.line([(cx, cy - h * 0.44), (cx, cy - h * 0.14)], w * 0.04)
        det.line([(cx, cy + h * 0.14), (cx, cy + h * 0.44)], w * 0.04)


def testudo(px, t=0.0, act=0.0, flip=False):
    """DEFRAG (block): a testudo. act 0 = shields slightly apart, 1 = locked shut with a clang."""
    pens, k = _pens(px, flip=flip)
    p, b, det, gl = pens["main"], pens["back"], pens["detail"], pens["glint"]
    gap = 10 * (1 - act) + 2
    w, h = 62, 92
    # roof row (tilted shields seen from below, back layer)
    for j in range(5):
        cx = 200 + (j - 2) * (w + gap) * 0.86
        b.poly([(cx - w * 0.45, 92), (cx + w * 0.45, 92), (cx + w * 0.5, 122), (cx - w * 0.5, 122)])
    # spear tips poking up between roof shields
    for j in range(4):
        cx = 200 + (j - 1.5) * (w + gap) * 0.86
        b.limb([(cx, 124), (cx + 4, 56)], 3, 2)
        b.poly([(cx + 4 - 5, 60), (cx + 4, 38), (cx + 4 + 5, 60)])
    # front wall: 2 rows x 4
    for row in range(2):
        for j in range(4):
            cx = 200 + (j - 1.5) * (w + gap)
            cy = 172 + row * (h * 0.58)
            scutum(p, det, gl, cx, cy, w, h * 0.62 if row == 0 else h * 0.66)
    # legs under the wall
    for j in range(8):
        x = 120 + j * 22
        p.limb([(x, 236), (x + 3 * math.sin(t * 2 + j), 262)], 7, 6)
    return _out(pens)


def secutor(px, t=0.0, act=0.0, flip=False):
    """SANDBOX (shield): a secutor crouched behind his great scutum, raking up a sand barrier. act = shield slams down."""
    pens, k = _pens(px, flip=flip)
    p, b, det, gl = pens["main"], pens["back"], pens["detail"], pens["glint"]
    dy = -14 * (1 - act) + 4 * math.sin(t * 1.4) * (1 - act)
    # fighter behind (back layer): smooth egg helmet with eye holes, shoulder, sword arm
    hx, hy = 236, 118 + dy
    b.blob([(hx - 26, hy + 6), (hx - 20, hy - 26), (hx + 4, hy - 38), (hx + 26, hy - 20), (hx + 26, hy + 14), (hx - 6, hy + 20)])
    b.blob([(hx - 10, hy - 38), (hx + 2, hy - 54), (hx + 12, hy - 38)])     # fin crest
    b.ell(hx - 40, hy + 60, 46, 44)                                       # shoulders hunched
    b.limb([(hx + 20, hy + 40), (hx + 64, hy + 30), (hx + 92, hy - 4)], 16, 10)   # sword arm
    b.limb([(hx + 92, hy - 4), (hx + 104, hy - 46)], 7, 2)                # gladius
    det.ell(hx + 12, hy - 8, 4, 3)
    det.ell(hx + 2, hy - 8, 4, 3)
    # the great scutum
    scutum(p, det, gl, 196, 182 + dy * 0.6, 120, 150, curve=0.22)
    # sand berm
    for j in range(9):
        x = 110 + j * 24
        p.ell(x, 258, 26, 10 + 4 * math.sin(j * 1.3))
    return _out(pens)


# ------------------------------------------------------------------ crowd + laurel (VERDICT)
def laurel(p, cx, cy, r, leaves=9, open_deg=50, lw=24, ww=9, k=1.0):
    for side in (-1, 1):
        for j in range(leaves):
            a = math.radians(90 + side * (open_deg / 2 + j * (300 - open_deg) / 2 / leaves))
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            tang = a + side * math.pi / 2
            for sgn in (-1, 1):
                ang = tang + sgn * 0.6
                L_ = lw * (0.75 + 0.25 * (j / leaves)) * k
                p.blob([(x, y), (x + L_ * 0.5 * math.cos(ang) + ww * k * math.cos(ang + 1.57) * 0.5, y + L_ * 0.5 * math.sin(ang) + ww * k * math.sin(ang + 1.57) * 0.5),
                        (x + L_ * math.cos(ang), y + L_ * math.sin(ang)),
                        (x + L_ * 0.5 * math.cos(ang) - ww * k * math.cos(ang + 1.57) * 0.5, y + L_ * 0.5 * math.sin(ang) - ww * k * math.sin(ang + 1.57) * 0.5)], n=4)
        # stem
        pts = [(cx + r * math.cos(math.radians(90 + side * (open_deg / 2 + j * (300 - open_deg) / 2 / leaves))),
                cy + r * math.sin(math.radians(90 + side * (open_deg / 2 + j * (300 - open_deg) / 2 / leaves)))) for j in range(leaves)]
        p.limb(pts, 4 * k, 2 * k)


def crowd(px, t=0.0, act=0.0, flip=False, fill_k=1.0):
    """VERDICT (special): tiers of the crowd under a gilt laurel. act = arms shoot up, thumbs down."""
    pens, k = _pens(px, flip=flip)
    p, b, det, gl = pens["main"], pens["back"], pens["detail"], pens["glint"]
    # laurel wreath, gilt, floating
    bob = 3 * math.sin(t * 1.5)
    laurel(gl, 200, 96 + bob, 64, leaves=8, open_deg=60, lw=32, ww=12)
    # tiers: back row small heads, front row big
    rows = [(196, 24, 13, b, 0.0), (252, 34, 19, p, 1.3)]
    for ri, (y, spacing, hr, pen, ph0) in enumerate(rows):
        n = int(420 / spacing)
        for j in range(n):
            if (j * 7 + ri * 3) % 11 == 0 and fill_k < 1.0:
                continue
            x = j * spacing - 10 + (spacing / 2 if ri % 2 else 0)
            bob_ = 3 * math.sin(t * 3.0 + j * 0.9 + ph0)
            pen.ell(x, y - hr * 1.6 + bob_, hr * 0.8, hr)                           # head
            pen.ell(x, y + bob_ * 0.3, hr * 1.5, hr * 1.2)                          # shoulders
            raise_ = act > 0 and (j + ri) % 2 == 0
            if raise_ or (j * 5 + ri) % 9 == 0:
                up = act if raise_ else 0.25 + 0.25 * math.sin(t * 2 + j)
                ax = x + hr * 1.1
                ay = y - hr * (1.6 + 2.8 * up)
                pen.limb([(x + hr * 0.9, y - hr * 0.4), (ax, ay)], hr * 0.5, hr * 0.45)
                pen.ell(ax, ay, hr * 0.42, hr * 0.42)                                # fist
                if raise_ and act > 0.4:
                    pen.limb([(ax, ay), (ax, ay + hr * 0.95)], hr * 0.22, hr * 0.18)  # thumb down
    return _out(pens)


# ------------------------------------------------------------------ hub portrait: emperor bust (profile, faces left)
def emperor(px, t=0.0, look=0.0, flip=False, wrath=0.0):
    """Hub: the emperor's marble bust in profile with a gilt laurel. Box 400x400. look -1..1 = gaze (eye glow)."""
    k = px / 400
    size = (px, px)
    pens = {n: Pen(size, k, flip=flip) for n in ("main", "detail", "glint", "eye")}
    p, det, gl, ey = pens["main"], pens["detail"], pens["glint"], pens["eye"]
    tilt = 3 * math.sin(t * 0.7) + 4 * wrath
    cx, cy = 200, 196
    def R(pts):
        c, s_ = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
        return [(cx + (u - cx) * c - (v - cy) * s_, cy + (u - cx) * s_ + (v - cy) * c) for u, v in pts]
    # head profile facing left
    head = [(236, 88), (196, 84), (164, 98), (150, 118), (147, 138), (142, 148), (128, 176), (124, 182), (138, 186),
            (134, 194), (140, 198), (135, 205), (141, 212), (142, 226), (156, 238), (184, 240), (196, 250), (202, 272),
            (252, 276), (270, 240), (290, 214), (300, 170), (292, 124), (268, 98)]
    p.blob(R(head), n=6)
    # nostril and lip cuts
    p.limb(R([(128, 181), (136, 179)]), 2.2, 1.6, fill=0)
    p.limb(R([(137, 198), (146, 199)]), 2.0, 1.4, fill=0)
    # neck + bust with toga folds
    p.blob(R([(196, 250), (262, 250), (276, 300), (330, 318), (360, 360), (370, 400), (40, 400), (60, 352), (110, 318), (176, 300)]), n=6)
    for j in range(5):
        det.limb(R([(120 + j * 40, 400), (150 + j * 30, 340 + j * 4), (200 + j * 18, 312)]), 5, 3)
    # hair curls (detail)
    for j in range(8):                                        # curls on the back of the skull only
        a = math.radians(-60 + j * 17)
        c_ = R([(250 + 44 * math.cos(a), 160 + 60 * math.sin(a))])[0]
        det.ell(c_[0], c_[1], 7, 5, ang=math.degrees(a))
    # ear, brow, eye socket
    det.ell(*R([(238, 178)])[0], 9, 14)
    det.limb(R([(150, 140), (166, 136), (184, 142)]), 5, 3)
    ex, ey_ = R([(164 + 3 * look, 152)])[0]
    ey.ell(ex, ey_, 7, 4.5)
    # laurel crown (gilt)
    for j in range(9):
        a = math.radians(200 + j * 16)
        x, y = 222 + 70 * math.cos(a), 150 + 66 * math.sin(a)
        for sgn in (-1, 1):
            ang = a + 1.57 + sgn * 0.7
            gl.blob(R([(x, y), (x + 13 * math.cos(ang) + 4 * math.cos(ang + 1.57), y + 13 * math.sin(ang) + 4 * math.sin(ang + 1.57)),
                       (x + 24 * math.cos(ang), y + 24 * math.sin(ang)),
                       (x + 13 * math.cos(ang) - 4 * math.cos(ang + 1.57), y + 13 * math.sin(ang) - 4 * math.sin(ang + 1.57))]), n=4)
    gl.limb(R([(282, 150), (296, 176), (290, 206)]), 6, 2)   # ribbons
    gl.limb(R([(280, 156), (304, 190), (306, 222)]), 5, 2)
    return {n: q.m for n, q in pens.items()}


# ------------------------------------------------------------------ needle rig: the pulvinar box + the arm
def hand(p, det, wx, wy, s, gesture, ang=0.0):
    """A fist with the thumb out. gesture: -1 = thumb down, 0 = sideways, 1 = up (continuous). (wx,wy) = wrist."""
    a = math.radians(ang)
    def T(u, v):
        return (wx + (u * math.cos(a) - v * math.sin(a)) * s, wy + (u * math.sin(a) + v * math.cos(a)) * s)
    fist = [(0, -14), (22, -18), (40, -12), (44, 6), (38, 20), (16, 22), (0, 16)]
    p.blob([T(u, v) for u, v in fist])
    for j in range(4):
        det.line([T(26 + j * 0.5, -12 + j * 8), T(42, -10 + j * 8)], 2.2 * s)
    th = -90 * gesture         # thumb angle relative to the fist: up = -90, down = +90
    ta = math.radians(th)
    base = (16, -6) if gesture >= 0 else (16, 14)
    tip = (base[0] + 30 * math.cos(ta) + 4, base[1] + 30 * math.sin(ta))
    p.limb([T(*base), T((base[0] + tip[0]) / 2 + 2, (base[1] + tip[1]) / 2), T(*tip)], 15 * s, 11 * s)
    return T(*tip)


def pulvinar(px, gesture=0.0, t=0.0, arm=1.0, fire=0.0):
    """The emperor's box: columns, pediment, awning, drape; the arm reaches out over the ledge.
    Box 400x300 (centre x 200, ledge y 210). gesture -1..1 for the thumb."""
    k = px / 400
    size = (px, int(300 * k))
    pens = {n: Pen(size, k) for n in ("back", "main", "detail", "glint", "drape", "arm")}
    b, p, det, gl, dr, am = (pens[n] for n in ("back", "main", "detail", "glint", "drape", "arm"))
    # the box interior (dark) and the seated figure silhouette
    b.rrect(110, 70, 290, 214, 4)
    # pediment
    p.poly([(96, 74), (200, 22), (304, 74)])
    p.poly([(116, 68), (200, 32), (284, 68)], fill=0)
    p.poly([(124, 64), (200, 38), (276, 64)])
    p.rrect(84, 70, 316, 106, 3)
    # columns
    for x in (112, 288):
        p.rrect(x - 10, 104, x + 10, 210, 3)
        p.rrect(x - 14, 104, x + 14, 112, 2)
        p.rrect(x - 14, 200, x + 14, 212, 2)
        for j in range(3):
            det.line([(x - 5 + j * 5, 114), (x - 5 + j * 5, 198)], 1.6)
    # ledge / balustrade
    p.rrect(84, 206, 316, 226, 3)
    p.rrect(96, 226, 304, 236, 2)
    gl.line([(84, 207), (316, 207)], 2.0)
    # the drape over the ledge with fringe
    dr.blob([(132, 214), (268, 214), (262, 262), (230, 254), (200, 268), (170, 254), (138, 262)])
    for j in range(14):
        x = 140 + j * 9
        gl.line([(x, 258 + 4 * math.sin(j)), (x, 266 + 4 * math.sin(j))], 2.2)
    # the emperor seated in the shadow (just a silhouette with laurel glint)
    det.ell(200, 128, 18, 20)
    det.blob([(166, 210), (172, 160), (200, 146), (228, 160), (234, 210)])
    for j in range(5):
        a = math.radians(200 + j * 30)
        gl.ell(200 + 20 * math.cos(a), 122 + 18 * math.sin(a), 4, 2.4, ang=math.degrees(a) + 90)
    # the arm, reaching out over the ledge to the right of the blade
    if arm > 0:
        sx, sy = 230, 184
        ex, ey = sx + 70 * arm, sy + 30 * arm
        dr.limb([(sx, sy), (sx + 34, sy + 26), (ex, ey)], 34, 28)              # toga sleeve (purple)
        am.limb([(ex - 6, ey - 2), (ex + 30 * arm, ey + 4)], 20, 18)          # forearm
        tip = hand(am, det, ex + 28 * arm, ey + 4, 1.55, gesture, ang=0)
        gl.limb([(sx + 4, sy + 14), (sx + 36, sy + 40), (ex - 2, ey + 14)], 4, 3)  # gilt hem
    return {n: q.m for n, q in pens.items()}
