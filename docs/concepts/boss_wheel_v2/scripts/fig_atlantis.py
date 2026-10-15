"""Boss Wheel v2: Tethys Deep (Atlantis) figures as layered silhouette masks.

Same contract as fig_roman: dict of L masks ('back', 'main', 'detail', 'glint', optional 'eye', 'ink', 'lure').
Unit box 400 x 300, t = idle seconds, act = 0..1 action progress.
"""
import math

from shapes import Pen, leg

UW, UH = 400, 300


def _pens(px, names=("back", "main", "detail", "glint", "eye", "ink"), fit=1.0, ax=200.0, ay=150.0):
    k = px / UW
    size = (px, int(UH * k))
    kk = k * fit
    ox, oy = ax * k - ax * kk, ay * k - ay * kk
    return {n: Pen(size, kk, ox, oy) for n in names}, k


def _out(pens):
    return {n: p.m for n, p in pens.items()}


# ------------------------------------------------------------------ diver helmet (shared: figure, hub, needle)
def helmet(p, det, gl, eye, cx, cy, s, ang=0.0, face=0.0):
    """Brass standard diving helmet, 3/4 side facing right. (cx,cy) = dome centre, s = scale (dome radius 1 = 40)."""
    R_ = 40 * s
    p.ell(cx, cy, R_, R_ * 1.02)
    p.rrect(cx - R_ * 1.05, cy + R_ * 0.55, cx + R_ * 1.05, cy + R_ * 1.15, 6 * s)          # breastplate collar
    # front port (glass) + side port
    eye.ell(cx + R_ * 0.42, cy + R_ * 0.02, R_ * 0.40, R_ * 0.42)
    gl.ell(cx + R_ * 0.42, cy + R_ * 0.02, R_ * 0.50, R_ * 0.52)
    gl.ell(cx + R_ * 0.42, cy + R_ * 0.02, R_ * 0.40, R_ * 0.42, fill=0)
    for j in range(3):                                                         # port grille bars
        det.line([(cx + R_ * (0.12 + j * 0.3), cy - R_ * 0.4), (cx + R_ * (0.12 + j * 0.3), cy + R_ * 0.44)], 2.2 * s)
    gl.ell(cx - R_ * 0.45, cy - R_ * 0.18, R_ * 0.2, R_ * 0.22)
    gl.ell(cx - R_ * 0.45, cy - R_ * 0.18, R_ * 0.13, R_ * 0.15, fill=0)
    for j in range(8):                                                         # bolts on the collar
        gl.dot((cx - R_ * 0.95 + j * R_ * 0.27, cy + R_ * 0.85), 2.6 * s)
    gl.rrect(cx - R_ * 0.18, cy - R_ * 1.12, cx + R_ * 0.18, cy - R_ * 0.92, 2 * s)      # top valve


# ------------------------------------------------------------------ SHIM: the diver fires the harpoon
def diver(px, t=0.0, act=0.0):
    pens, k = _pens(px, fit=0.95)
    p, b, det, gl, eye = pens["main"], pens["back"], pens["detail"], pens["glint"], pens["eye"]
    bob = 4 * math.sin(t * 1.2)
    hx, hy = 150, 92 + bob
    # body: suit, weighted boots, kick
    kick = math.sin(t * 2.4) * 10
    p.blob([(hx - 40, hy + 36), (hx + 30, hy + 30), (hx + 40, hy + 80), (hx + 20, hy + 128), (hx - 34, hy + 124), (hx - 50, hy + 80)])
    p.limb([(hx - 20, hy + 120), (hx - 44, hy + 160 + kick), (hx - 70, hy + 186 + kick)], 30, 22)
    p.limb([(hx + 10, hy + 120), (hx + 2, hy + 166 - kick), (hx - 16, hy + 196 - kick)], 30, 22)
    p.rrect(hx - 96, hy + 180 + kick, hx - 56, hy + 198 + kick, 5)
    p.rrect(hx - 40, hy + 188 - kick, hx + 2, hy + 206 - kick, 5)
    # air tank on the back
    p.rrect(hx - 70, hy + 30, hx - 40, hy + 112, 12)
    # arms forward with the speargun
    recoil = -8 * act if act < 0.3 else -8 * (1 - act)
    p.limb([(hx + 10, hy + 46), (hx + 60, hy + 64), (hx + 100 + recoil, hy + 62)], 22, 16)
    p.limb([(hx + 0, hy + 56), (hx + 40, hy + 82), (hx + 84 + recoil, hy + 78)], 20, 15)
    gx = hx + 76 + recoil
    p.rrect(gx, hy + 56, gx + 110, hy + 72, 5)                                 # gun barrel
    p.poly([(gx + 10, hy + 70), (gx + 30, hy + 70), (gx + 22, hy + 100), (gx + 8, hy + 98)])   # grip
    gl.line([(gx + 4, hy + 58), (gx + 106, hy + 58)], 2.4)
    # the harpoon: loaded, or flying with its tether
    fly = 0 if act <= 0.05 else 110 * min(1, (act - 0.05) / 0.5)
    sx = gx + 110 + fly
    gl.limb([(sx - 70, hy + 62), (sx + 10, hy + 62)], 4, 4)
    gl.poly([(sx + 10, hy + 54), (sx + 34, hy + 62), (sx + 10, hy + 70)])
    gl.poly([(sx - 4, hy + 62), (sx + 6, hy + 50), (sx + 10, hy + 60)])
    if fly > 0:
        det.line([(gx + 110, hy + 64), (sx - 70, hy + 70 + 6 * math.sin(t * 9))], 1.6)
    # helmet on top
    helmet(p, det, gl, eye, hx + 6, hy, 1.12)
    # bubbles from the valve
    for j in range(5):
        yy = hy - 60 - ((t * 40 + j * 24) % 120)
        gl.ell(hx + 10 + 8 * math.sin(j + t * 3), yy, 3 + j % 3, 3 + j % 3)
        gl.ell(hx + 10 + 8 * math.sin(j + t * 3), yy, 1.8 + j % 3 * 0.8, 1.8 + j % 3 * 0.8, fill=0)
    return _out(pens)


# ------------------------------------------------------------------ OVERFLOW: the anglerfish lunges
def angler(px, t=0.0, act=0.0):
    pens, k = _pens(px, fit=0.84, ax=180)
    p, b, det, gl, eye = pens["main"], pens["back"], pens["detail"], pens["glint"], pens["eye"]
    x0 = 190 + 50 * act
    y0 = 160 + 3 * math.sin(t * 1.1)
    gape = 0.25 + 0.75 * act + 0.08 * math.sin(t * 2)
    # body: a big round head tapering into the tail (faces right)
    body = [(x0 + 80, y0 - 70), (x0 + 20, y0 - 92), (x0 - 50, y0 - 72), (x0 - 110, y0 - 30), (x0 - 150, y0 - 10),
            (x0 - 150, y0 + 14), (x0 - 108, y0 + 30), (x0 - 40, y0 + 64), (x0 + 30, y0 + 74), (x0 + 84, y0 + 50)]
    p.blob(body)
    # tail fin
    tw = 10 * math.sin(t * 3)
    p.poly([(x0 - 140, y0), (x0 - 196, y0 - 44 + tw), (x0 - 182, y0 + tw * 0.2), (x0 - 200, y0 + 44 + tw)])
    # dorsal + pectoral fins (spiny)
    for j in range(4):
        bx = x0 - 30 - j * 26
        p.poly([(bx, y0 - 70 + j * 10), (bx - 18, y0 - 106 + j * 12), (bx - 26, y0 - 64 + j * 10)])
    p.poly([(x0 - 20, y0 + 40), (x0 - 70, y0 + 92 + tw), (x0 - 50, y0 + 44)])
    # the mouth: upper jaw stays, lower jaw drops open
    mx, my = x0 + 84, y0 - 4
    p.poly([(mx - 6, my - 64), (mx + 36, my - 40), (mx + 30, my - 18), (mx - 4, my - 12)])
    jaw = gape * 52
    p.poly([(mx - 4, my + 10), (mx + 40, my + 20 + jaw * 0.6), (mx + 30, my + 40 + jaw), (mx - 20, my + 56)])
    # the gape (cut) with teeth
    p.poly([(mx - 4, my - 14), (mx + 30, my - 18), (mx + 38, my + 20 + jaw * 0.6), (mx - 4, my + 12)], fill=0)
    for j in range(6):
        u = j / 5
        tx = mx + 2 + 30 * u
        det.poly([(tx - 4, my - 16 - u * 2), (tx, my - 2 + jaw * 0.2), (tx + 4, my - 16 - u * 2)])
        det.poly([(tx - 4, my + 14 + jaw * 0.55 * u), (tx, my - 2 + jaw * 0.3 * u), (tx + 4, my + 14 + jaw * 0.55 * u)])
    gl.ell(mx - 16, my - 44, 7, 7)                                              # eye
    eye.ell(mx - 16, my - 44, 4, 4)
    # the illicium and its lure (glint = lit)
    lx = mx + 50 + 12 * math.sin(t * 1.4)
    ly = my - 120 - 6 * math.cos(t * 1.4)
    p.limb([(mx - 14, my - 66), (mx + 10, my - 120), (lx - 10, ly - 10), (lx, ly)], 5, 3)
    gl.ell(lx, ly + 6, 9, 10)
    eye.ell(lx, ly + 6, 6, 7)
    # bioluminescent dots along the flank
    for j in range(7):
        det.ell(x0 - 110 + j * 26, y0 + 8 + 8 * math.sin(j), 3, 3)
    return _out(pens)


# ------------------------------------------------------------------ SANDBOX: the pressure dome
def dome(px, t=0.0, act=0.0):
    pens, k = _pens(px, fit=0.95)
    p, b, det, gl, eye = pens["main"], pens["back"], pens["detail"], pens["glint"], pens["eye"]
    cx, gy = 200, 248
    R_ = 108 + 6 * act
    # seabed + the habitat base ring
    p.blob([(40, gy + 14), (120, gy + 2), (280, gy + 2), (360, gy + 14), (330, gy + 30), (70, gy + 30)])
    p.rrect(cx - R_ - 14, gy - 22, cx + R_ + 14, gy + 4, 8)
    for j in range(10):
        gl.dot((cx - R_ + j * R_ * 0.222, gy - 10), 3.2)
    # inside: a little skyline of the habitat (back layer)
    for j, (x, h) in enumerate(((-60, 54), (-30, 80), (0, 104), (30, 70), (58, 46))):
        b.rrect(cx + x - 12, gy - 22 - h, cx + x + 12, gy - 22, 3)
        det.rrect(cx + x - 4, gy - 22 - h + 10, cx + x + 4, gy - 22 - h + 18, 1)
    b.limb([(cx, gy - 126), (cx, gy - 150)], 3, 2)
    # the dome: a glass hemisphere drawn as glint ring + vertical ribs
    gl.ell(cx, gy - 22, R_, R_)
    gl.ell(cx, gy - 22, R_ - 4, R_ - 4, fill=0)
    gl.rrect(cx - R_ - 10, gy - 24, cx + R_ + 10, gy + 50, 0, fill=0)
    for j in range(5):
        a = math.radians(-160 + j * 35)
        gl.limb([(cx + (R_ - 2) * math.cos(a), gy - 22 + (R_ - 2) * math.sin(a) * 1.0), (cx + (R_ - 2) * math.cos(a) * 0.15, gy - 22 - R_ + 2)], 2.4, 2.4)
    # the dome glass itself (eye = soft fill, used as translucent glass)
    eye.ell(cx, gy - 22, R_ - 4, R_ - 4)
    eye.rrect(cx - R_, gy - 22, cx + R_, gy + 40, 0, fill=0)
    return _out(pens)


# ------------------------------------------------------------------ DETOUR: an octopus jets away in an ink cloud
def octo_ink(px, t=0.0, act=0.0):
    pens, k = _pens(px, fit=0.95)
    p, b, det, gl, eye, ink = (pens[n] for n in ("main", "back", "detail", "glint", "eye", "ink"))
    jet = act
    ox, oy = 250 + 60 * jet, 120 - 30 * jet + 4 * math.sin(t * 1.3)
    # ink cloud billowing behind (left, below)
    r = 0
    for j in range(9):
        ang = math.radians(200 + j * 15)
        cxp = 150 - 50 * jet + 70 * math.cos(ang) * (0.6 + 0.6 * jet)
        cyp = 190 + 40 * math.sin(ang) * (0.6 + 0.5 * jet)
        rr = (38 + 10 * math.sin(j * 1.7 + t)) * (0.7 + 0.6 * jet)
        ink.ell(cxp, cyp, rr, rr * 0.9)
    ink.ell(150 - 30 * jet, 190, 70 * (0.7 + 0.6 * jet), 52 * (0.7 + 0.6 * jet))
    # mantle (head) pointing up-right, arms trailing down-left (jetting pose)
    tilt = -30
    mantle = [(ox + 10, oy - 64), (ox + 46, oy - 50), (ox + 56, oy - 10), (ox + 34, oy + 22), (ox - 4, oy + 30), (ox - 30, oy + 10), (ox - 30, oy - 30)]
    p.blob(mantle)
    gl.ell(ox + 4, oy + 8, 7, 6)
    eye.ell(ox + 4, oy + 8, 3.5, 2.2)
    for j in range(6):
        sp = (j - 2.5) * 9
        wv = 10 * math.sin(t * 3 + j)
        p.limb([(ox - 10 + sp * 0.4, oy + 20), (ox - 50 + sp - wv, oy + 70 + abs(sp) * 0.4),
                (ox - 100 + sp * 1.4 + wv, oy + 110 + abs(sp) * 0.6), (ox - 150 + sp * 1.8, oy + 130 + sp)], 16, 3)
    for j in range(5):
        det.ell(ox - 60 + j * -12, oy + 80 + j * 8, 2.4, 2.4)
    return _out(pens)


# ------------------------------------------------------------------ INFECT: the jellyfish stings
def jelly(px, t=0.0, act=0.0, scale=1.0):
    pens, k = _pens(px, fit=0.95)
    p, b, det, gl, eye = pens["main"], pens["back"], pens["detail"], pens["glint"], pens["eye"]
    pulse = 0.5 + 0.5 * math.sin(t * 2.2)
    cx, cy = 200, 92 + 6 * pulse
    bw = (78 + 10 * pulse) * scale
    bh = (60 - 8 * pulse) * scale
    bell = [(cx - bw, cy + bh * 0.45), (cx - bw * 0.9, cy - bh * 0.5), (cx - bw * 0.4, cy - bh), (cx + bw * 0.4, cy - bh),
            (cx + bw * 0.9, cy - bh * 0.5), (cx + bw, cy + bh * 0.45)]
    for j in range(8):          # scalloped margin
        x = cx + bw - j * bw * 2 / 7
        bell.append((x, cy + bh * (0.45 + 0.12 * (j % 2))))
    p.blob(bell, n=6)
    # inner radial canals + gonads (detail)
    for j in range(4):
        a = math.radians(200 + j * 47)
        det.ell(cx + bw * 0.42 * math.cos(a), cy - bh * 0.1 + bh * 0.3 * math.sin(a), bw * 0.16, bh * 0.14)
    # oral arms (frilly) + long tentacles; act = lash down and out
    lash = act
    for j in range(5):
        x = cx - 40 + j * 20
        wv = 12 * math.sin(t * 2 + j)
        p.limb([(x, cy + bh * 0.4), (x + wv, cy + 70), (x - wv + lash * (j - 2) * 20, cy + 140 + 40 * lash)], 12, 3)
    for j in range(9):
        x = cx - bw * 0.9 + j * bw * 0.225
        wv = 16 * math.sin(t * 1.6 + j * 0.8)
        b.limb([(x, cy + bh * 0.45), (x + wv, cy + 90), (x - wv + lash * (j - 4) * 26, cy + 170 + 40 * lash),
                (x + wv * 0.5 + lash * (j - 4) * 36, cy + 230 + 30 * lash)], 3.2, 1.2)
    # stinging sparks at tentacle tips on act
    if act > 0.2:
        for j in range(9):
            x = cx - bw * 0.9 + j * bw * 0.225 + act * (j - 4) * 36
            y = cy + 230 + 30 * act
            for q in range(4):
                a = math.radians(q * 90 + 45 + j * 10)
                gl.limb([(x, y), (x + 12 * act * math.cos(a), y + 12 * act * math.sin(a))], 2.2, 1)
    # rim photophores
    for j in range(12):
        x = cx - bw + j * bw * 2 / 11
        gl.dot((x, cy + bh * 0.48), 3)
    return _out(pens)


# ------------------------------------------------------------------ hub A: the giant octopus eye
def octo_eye(px, t=0.0, look=0.0, blink=0.0, wrath=0.0):
    """Box 400x400: the eye of the giant octopus, horizontal bar pupil, wrinkled lids, skin papillae."""
    k = px / 400
    size = (px, px)
    pens = {n: Pen(size, k) for n in ("main", "detail", "glint", "eye", "pupil")}
    p, det, gl, ey, pu = (pens[n] for n in ("main", "detail", "glint", "eye", "pupil"))
    cx, cy = 200, 200
    p.ell(cx, cy, 200, 200)
    # wrinkle folds around the eye
    for j in range(7):
        rr = 110 + j * 14
        det.limb([(cx - rr, cy + 10 + j * 3), (cx - rr * 0.6, cy - rr * 0.55), (cx, cy - rr * 0.72), (cx + rr * 0.6, cy - rr * 0.55), (cx + rr, cy + 10 + j * 3)], 3.5, 2)
    # papillae dots
    for j in range(40):
        a = j * 2.4
        rr = 120 + (j * 37) % 70
        det.dot((cx + rr * math.cos(a), cy + rr * math.sin(a)), 3 + (j % 3))
    # the eye ball (iris = eye), lids close with blink
    open_ = max(0.05, 1 - blink)
    ey.blob([(cx - 112, cy + 4), (cx - 60, cy - 70 * open_), (cx + 10, cy - 84 * open_), (cx + 80, cy - 62 * open_), (cx + 116, cy + 2),
             (cx + 70, cy + 60 * open_), (cx, cy + 72 * open_), (cx - 70, cy + 56 * open_)])
    pw = 50 - 14 * wrath
    pu.blob([(cx - pw + look * 16, cy), (cx - pw * 0.6 + look * 16, cy - 14 * open_), (cx + pw * 0.6 + look * 16, cy - 16 * open_),
             (cx + pw + look * 16, cy), (cx + pw * 0.6 + look * 16, cy + 15 * open_), (cx - pw * 0.6 + look * 16, cy + 13 * open_)])
    gl.ell(cx - 40, cy - 36 * open_, 13, 8 * open_)
    # heavy lid rims
    det.limb([(cx - 124, cy + 6), (cx - 64, cy - 84 * open_), (cx + 12, cy - 98 * open_), (cx + 84, cy - 74 * open_), (cx + 128, cy + 4)], 16, 12)
    det.limb([(cx - 124, cy + 6), (cx - 70, cy + 66 * open_), (cx, cy + 82 * open_), (cx + 74, cy + 70 * open_), (cx + 128, cy + 4)], 12, 10)
    return {n: q.m for n, q in pens.items()}


def helmet_front(px, t=0.0, glow=1.0):
    """Hub/needle: brass diving helmet seen from the front, the face port glowing. Box 400x400."""
    k = px / 400
    size = (px, px)
    pens = {n: Pen(size, k) for n in ("main", "detail", "glint", "eye")}
    p, det, gl, ey = (pens[n] for n in ("main", "detail", "glint", "eye"))
    cx, cy = 200, 186
    p.ell(cx, cy, 128, 132)
    p.rrect(cx - 168, cy + 90, cx + 168, cy + 190, 30)
    ey.ell(cx, cy + 6, 70, 74)
    gl.ell(cx, cy + 6, 86, 90)
    gl.ell(cx, cy + 6, 70, 74, fill=0)
    for j in range(3):
        det.line([(cx - 40 + j * 40, cy - 64), (cx - 40 + j * 40, cy + 76)], 7)
    for sgn in (-1, 1):
        gl.ell(cx + sgn * 104, cy + 6, 26, 30)
        gl.ell(cx + sgn * 104, cy + 6, 18, 22, fill=0)
        ey.ell(cx + sgn * 104, cy + 6, 18, 22)
    for j in range(12):
        gl.dot((cx - 150 + j * 27.3, cy + 140), 7)
    gl.rrect(cx - 26, cy - 150, cx + 26, cy - 122, 6)
    return {n: q.m for n, q in pens.items()}


def tentacle(p, pts, w0, w1, suckers=None, sk=1.0):
    """A tapered tentacle along a spline; suckers drawn on the underside into a second pen."""
    p.limb(pts, w0, w1, n=14)
    if suckers is not None:
        from bw_kit import catmull
        cl = catmull(pts, 14, False)
        n = len(cl)
        for j in range(2, n - 2, 3):
            x, y = cl[j]
            xa, ya = cl[j - 1]
            xb, yb = cl[j + 1]
            dx, dy = xb - xa, yb - ya
            ln = math.hypot(dx, dy) or 1
            nx, ny = -dy / ln, dx / ln
            w = (w0 + (w1 - w0) * j / n) / 2
            suckers.ell(x + nx * w * 0.55, y + ny * w * 0.55, w * 0.32 * sk, w * 0.32 * sk)


def preview_items():
    return [("diver 0", diver(400, 0, 0)), ("diver 1", diver(400, 0.3, 0.7)), ("angler 0", angler(400, 0, 0)), ("angler 1", angler(400, 0, 1)),
            ("dome", dome(400, 0, 0)), ("octo ink 0", octo_ink(400, 0, 0)), ("octo ink 1", octo_ink(400, 0, 1)), ("jelly 0", jelly(400, 0, 0)),
            ("jelly 1", jelly(400, 0.4, 1)), ("eye", octo_eye(400, 0, 0)), ("helmet", helmet_front(400))]
