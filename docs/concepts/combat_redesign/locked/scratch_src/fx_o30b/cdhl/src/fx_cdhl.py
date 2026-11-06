"""fx_cdhl: the C corp, D damage, H harm and L life effects (plus P shield_block for the block-vs-break sheet) on the locked final board.
Each effect: box (screen crop), pre / post base, state(t) (0..1 post share inside state_region), draw(lay, t, ctx), keys (ms, caption), timing.
Materials:
  C corp   : the corp's own frame enamel as a flat opaque shutter slab with a hard 2 px edge in the corp edge colour (neutral steel,
             Solace porcelain / lime edge with a rounded membrane lip, Meridian stencil paint / oxide edge with a notched lip); one flat flash.
  D damage : player-owned comic hit frame: painted pink tracer, ink-keylined pink starburst with a white core, converging speed lines,
             flat vector shards (pink / paper / ink), never textured.
  H harm   : misregistered red print: X-only halftone flood (no round dots, so it never reads as the spinner's Ben-Day), black krackle
             with a 2 px red misregistration, red stencil X.
  L life   : the one soft rising glow in the set: brush strokes, plus signs and four-point sparkles; GAIN green on dark, mint on the
             green REPAIR wedge, NET_CYAN for the RAM coin.
"""
import math, json
import numpy as np
from PIL import Image
from fxk_lib import *

GEO = json.load(open(W + 'geo_neutral_p3.json'))
GEO1 = json.load(open(W + 'geom.json'))
PIPS3 = GEO['pips']
GOUT = (84, 92, 120)
GIN = (14, 16, 30)


# ======================================================================== shared pieces
def gone_tick(lay, pip, op=1.0):
    aa, ab, r0, r1 = pip[:4]
    lay.poly(band(r0, r1, aa, ab, 4), fill=GIN + (255,), outline=GOUT, w=1.0, op=op)


def wedge_pip(s, i, n=2):
    """the tower slice pips (xf_tower.draw_pips): 36 px blocks, 6 px gap, centred on the slice axis at r 167"""
    bl, bg, R = 36.0, 6.0, TOWER['pip_r']
    cr = lambda px: math.degrees(px / R)
    tot = n * bl + (n - 1) * bg
    a = 60 * s - cr(tot) / 2 + cr(i * (bl + bg))
    return (a, a + cr(bl))


def tower_pip_dark(lay, s, i, op=1.0):
    a0, a1 = wedge_pip(s, i)
    R, w = TOWER['pip_r'], TOWER['pip_w']
    lay.poly(band(R - w / 2 - 0.8, R + w / 2 + 0.8, a0 + 0.3, a1 - 0.3, 6), fill=(22, 20, 30, 255), outline=INK, w=1.6, op=op)


def tower_pip_mend(lay, s, i, fill_k, op=1.0):
    a0, a1 = wedge_pip(s, i)
    R, w = TOWER['pip_r'], TOWER['pip_w']
    lay.poly(band(R - w / 2 - 0.8, R + w / 2 + 0.8, a0 + 0.3, a1 - 0.3, 6), fill=(22, 20, 30, 255), outline=INK, w=1.6, op=op)
    lay.poly(band(R - w / 2 + 0.6, R + w / 2 - 0.6, a0 + 0.8, a1 - 0.8, 6), fill=None, outline=GAIN, w=1.6, op=op)
    if fill_k > 0:
        am = a0 + 0.8 + (a1 - a0 - 1.6) * fill_k
        lay.poly(band(R - w / 2 + 0.6, R + w / 2 - 0.6, a0 + 0.8, am, 6), fill=GAIN + (255,), op=op)


def seat_xy(s):
    return ppx(TOWER['icon_r'], 60 * s)


def seat_clear(s):
    """the slice region minus the icon seat (r 37 around the icon): floods and dark-outs never cover the icon type ring"""
    pass


def tracer(lay, p0, p1, u, w0=2.2, w1=5.2, col=PINK, op=1.0):
    """painted tracer: a tapered brush stroke, ink keyline"""
    if u <= 0 or op <= 0:
        return
    x0, y0 = p0
    x1, y1 = lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u)
    L = math.hypot(x1 - x0, y1 - y0) or 1
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    n = 10
    left, right = [], []
    for i in range(n + 1):
        k = i / n
        ww = lerp(w0, w1, k) / 2
        x, y = lerp(x0, x1, k), lerp(y0, y1, k)
        left.append((x + nx * ww, y + ny * ww))
        right.append((x - nx * ww, y - ny * ww))
    pts = left + right[::-1]
    lay.poly(pts, fill=col + (255,), outline=INK, w=1.6, op=op)


def ribbon(pts, wf):
    """a tapered ribbon polygon along pts; wf(k) = half width at fraction k"""
    n = len(pts)
    L, R_ = [], []
    for i in range(n):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        w = wf(i / max(1, n - 1))
        L.append((pts[i][0] + nx * w, pts[i][1] + ny * w))
        R_.append((pts[i][0] - nx * w, pts[i][1] - ny * w))
    return L + R_[::-1]


def burst(lay, cx, cy, R, k=1.0, n=9, rot=0.3, seed=3, core=True, col=PINK, op=1.0):
    if k <= 0 or op <= 0:
        return
    pts = starburst(cx, cy, R * k, R * k * 0.46, n, rot, 0.16, seed)
    lay.poly(pts, fill=col + (255,), outline=INK, w=2.6, op=op)
    if core:
        p2 = starburst(cx, cy, R * k * 0.52, R * k * 0.26, n, rot + 0.15, 0.1, seed + 1)
        lay.poly(p2, fill=WHITE + (255,), op=op)


def speed_lines(lay, cx, cy, r_in, r_out, n, u, seed=5, col=WHITE, op=1.0):
    """converging speed lines: tapered spikes from r_out toward the hit, drawn in on u 0..1 then retracting"""
    if op <= 0 or u <= 0:
        return
    rng = np.random.RandomState(seed)
    polys = []
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.12, 0.12)
        ro = r_out * rng.uniform(0.85, 1.1)
        ri = lerp(ro, r_in, u)
        w = rng.uniform(1.2, 2.4)
        ca, sa = math.cos(a), math.sin(a)
        polys.append([(cx + ca * ro - sa * w, cy + sa * ro + ca * w), (cx + ca * ri, cy + sa * ri), (cx + ca * ro + sa * w, cy + sa * ro - ca * w)])
    lay.polys(polys, col + (255,), outline=INK, w=1.2, op=op)


def shards(lay, cx, cy, u, n=7, dist=44, size=7, seed=7, cols=(PINK, PAPER, INK), op=1.0, dirs=None):
    if u <= 0 or op <= 0:
        return
    rng = np.random.RandomState(seed)
    for i in range(n):
        a = (dirs[i % len(dirs)] if dirs else 2 * math.pi * i / n) + rng.uniform(-0.3, 0.3)
        d = dist * eout(u) * rng.uniform(0.7, 1.15)
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
        s = size * rng.uniform(0.7, 1.2) * (1 - 0.35 * u)
        rot = rng.uniform(0, 6.28) + u * rng.uniform(-4, 4)
        pts = [(x + s * math.cos(rot + k * 2.1 + rng.uniform(-0.3, 0.3)), y + s * math.sin(rot + k * 2.1)) for k in range(3)]
        c = cols[i % len(cols)]
        lay.poly(pts, fill=c + (255,), outline=INK if c != INK else PAPER, w=1.1, op=op)


def sparkle(lay, cx, cy, r, col=WHITE, op=1.0, rot=0.0):
    pts = []
    for i in range(8):
        a = rot + math.pi * i / 4
        rr = r if i % 2 == 0 else r * 0.22
        pts.append((cx + rr * math.sin(a), cy - rr * math.cos(a)))
    lay.poly(pts, fill=col + (255,), outline=INK, w=0.9, op=op)


def plus_sign(lay, cx, cy, s, col, op=1.0, key=INK):
    t = s * 0.36
    pts = [(cx - t, cy - s), (cx + t, cy - s), (cx + t, cy - t), (cx + s, cy - t), (cx + s, cy + t), (cx + t, cy + t), (cx + t, cy + s),
           (cx - t, cy + s), (cx - t, cy + t), (cx - s, cy + t), (cx - s, cy - t), (cx - t, cy - t)]
    lay.poly(pts, fill=col + (255,), outline=key, w=1.4, op=op)


def krackle(lay, p0, ang, length, seed, u=1.0, op=1.0, w=2.2):
    """black krackle with a red misregistration: a forked jagged line from p0 heading ang (screen degrees, 0 = up)"""
    if op <= 0 or u <= 0:
        return
    rng = np.random.RandomState(seed)
    t = math.radians(ang)
    p1 = (p0[0] + math.sin(t) * length * u, p0[1] - math.cos(t) * length * u)
    main = jag(p0, p1, 6, length * 0.12, seed)
    fk = []
    if u > 0.4:
        j = main[3]
        t2 = t + rng.choice([-1, 1]) * rng.uniform(0.5, 0.9)
        fk = jag(j, (j[0] + math.sin(t2) * length * 0.45 * u, j[1] - math.cos(t2) * length * 0.45 * u), 3, length * 0.07, seed + 1)
    for dx, dy, col, ww in ((2.0, 1.5, HARM, w), (0, 0, INK, w)):
        pl = [[(x + dx, y + dy) for x, y in main]] + ([[(x + dx, y + dy) for x, y in fk]] if fk else [])
        lay.lines(pl, col, ww, op)


def x_flood(lay, region, front_r, r_hi, dens, s=None, pitch=6.5, op=1.0, seed=0, col=HARM):
    """red X halftone flood rolling in from r_hi to front_r; the icon seat of slice s stays clear"""
    if op <= 0 or dens <= 0:
        return
    sx, sy = seat_xy(s) if s is not None else (None, None)

    def d(x, y):
        r, a = polar(x, y)
        if r < front_r:
            return 0.0
        if sx is not None and math.hypot(x - sx, y - sy) < TOWER['seat'] + 3:
            return 0.0
        k = clamp((r - front_r) / max(1.0, (r_hi - front_r)))
        return dens * (0.55 + 0.45 * k)
    grid_X(lay, region, d, pitch=pitch, col=col, op=op, misreg=(1.6, 1.2), w=1.5)


def chev(lay, r, ang, w=13, h=8, th=4.6, col=HARM, op=1.0):
    """a HOT threat chevron pointing inward on the radius r at angle ang (the board's chevron grammar)"""
    tip = ppx(r, ang)
    t = math.radians(ang)
    ux, uy = math.sin(t), -math.cos(t)       # outward
    px_, py_ = math.cos(t), math.sin(t)      # tangent
    a = (tip[0] + ux * h + px_ * w, tip[1] + uy * h + py_ * w)
    b = (tip[0] + ux * h - px_ * w, tip[1] + uy * h - py_ * w)
    lay.line([a, tip, b], col, th, op=op, key=1.8)


def hatch_strip(lay, pts, col, pitch=4.0, w=1.2, op=1.0):
    pass


# ======================================================================== D damage
GUN0 = ((560.0, 353.0), (416.0, 330.0))          # sector 0 BURST gun -> Worm 2 (p3 tracer and star)
GUN4 = ((361.0, 607.0), (535.0, 893.0))          # sector 4 BURST gun -> warded Packet 6 (gold ward mark)


def d_gun_hit(lay, t, c):
    (p0, p1) = GUN0
    red = c.reduce
    u = 1.0 if red else eout(seg(t, 0, 100))
    tracer(lay, p0, p1, u, op=1 - seg(t, 300, 480))
    if t >= 100:
        k = 1.0 if red else eback(seg(t, 100, 170))
        fade = 1 - seg(t, 330, 520)
        if not red:
            speed_lines(lay, p1[0], p1[1], 24, 62, 12, math.sin(math.pi * seg(t, 100, 280)), op=fade)
            shards(lay, p1[0], p1[1], seg(t, 120, 460), n=6, dist=46, op=1 - seg(t, 360, 460))
        burst(lay, p1[0], p1[1], 22, k * (1 - 0.25 * seg(t, 330, 520)), op=fade)
    if t >= 170:
        gone_tick(lay, PIPS3['2'][1])
        if not red:
            aa, ab, r0, r1 = PIPS3['2'][1][:4]
            lay.poly(band(r0 - 2, r1 + 2, aa - 1, ab + 1, 4), fill=PINK + (255,), op=1 - seg(t, 170, 260))


def d_strike(lay, t, c):
    u7 = GEO1['f1']['units']['7']
    tx, ty = u7['tok']
    hx_, hy_ = tx + 22, ty - 70          # the hit lands mid-cell between the token and its ticks
    red = c.reduce
    a = (hx_ - 70, hy_ + 58)
    b = (hx_ + 64, hy_ - 52)
    us = 1.0 if red else eout(seg(t, 0, 120))
    fade = 1 - seg(t, 380, 640)
    if t < 640:
        sl = (lerp(a[0], b[0], us), lerp(a[1], b[1], us))
        L = math.hypot(sl[0] - a[0], sl[1] - a[1]) or 1
        nx, ny = -(sl[1] - a[1]) / L, (sl[0] - a[0]) / L
        mid = ((a[0] + sl[0]) / 2, (a[1] + sl[1]) / 2)
        wd = 7.0
        pts = [a, (mid[0] + nx * wd, mid[1] + ny * wd), sl, (mid[0] - nx * wd * 0.6, mid[1] - ny * wd * 0.6)]
        lay.poly(pts, fill=PINK + (255,), outline=INK, w=2.0, op=fade)
        lay.line([(lerp(a[0], sl[0], 0.15), lerp(a[1], sl[1], 0.15)), (lerp(a[0], sl[0], 0.8), lerp(a[1], sl[1], 0.8))], WHITE, 2.0, op=fade)
    if t >= 120:
        k = 1.0 if red else eback(seg(t, 120, 200))
        if not red:
            speed_lines(lay, hx_, hy_, 34, 86, 16, math.sin(math.pi * seg(t, 120, 330)), op=fade, seed=9)
            shards(lay, hx_, hy_, seg(t, 130, 520), n=9, dist=60, size=8, op=1 - seg(t, 420, 520), seed=11)
        burst(lay, hx_, hy_, 34, k * (1 - 0.2 * seg(t, 380, 640)), n=11, seed=5, op=fade)
    if t >= 200:
        for i in (1, 2):
            gone_tick(lay, GEO['pips']['7'][i])
        if not red:
            for i in (1, 2):
                aa, ab, r0, r1 = GEO['pips']['7'][i][:4]
                lay.poly(band(r0 - 2, r1 + 2, aa - 1, ab + 1, 4), fill=PINK + (255,), op=1 - seg(t, 200, 300))


TRIG_Y = Image.open(W + 'trig_yel.png').convert('RGBA')
TRIG_P = Image.open(W + 'trig_pink.png').convert('RGBA')
PAYLOAD = tuple(GEO1['f2']['units']['4']['tok'])
X3, X4 = (536.0, 785.0), (325.0, 667.0)


def trig_route():
    p = [PAYLOAD]
    p += jag(PAYLOAD, X3, 1, 0, 1)[1:]
    p += arc_pts(245, 180, 239, 20)[1:]
    return p


def paste_global(lay, im, op=1.0, mask=None):
    """paste a full-plate RGBA layer (1920x1080) into the crop layer"""
    cr = im.crop((lay.x0, lay.y0, lay.x1, lay.y1)).resize((lay.w * lay.ss, lay.h * lay.ss), Image.LANCZOS)
    if mask is not None:
        a = np.asarray(cr).copy()
        a[:, :, 3] = (a[:, :, 3] * mask).astype(np.uint8)
        cr = Image.fromarray(a, 'RGBA')
    lay.comp(cr, op)


def d_trigger_hit(lay, t, c):
    red = c.reduce
    route = trig_route()
    ign = 1.0 if red else seg(t, 0, 420)
    # pencil route (yellow) under, painted pink front to back over it
    lay.line(route, (255, 226, 0), 3.0, op=(1 - seg(t, 420, 520)) * 0.95, key=1.2)
    lay.line(partial(route, ign), PINK, 4.4, key=1.6, op=1 - seg(t, 650, 900))
    # the two hit Xs: pencil -> paint in sector order
    tY = TRIG_Y
    sx3 = (1 if t >= 230 or red else 0)
    sx4 = (1 if t >= 420 or red else 0)
    ss = lay.ss
    yy, xx = np.mgrid[0:lay.h * ss, 0:lay.w * ss]
    X = xx / ss + lay.x0
    Y = yy / ss + lay.y0
    m3 = (np.hypot(X - X3[0], Y - X3[1]) < 70).astype(np.float32)
    m4 = (np.hypot(X - X4[0], Y - X4[1]) < 70).astype(np.float32)
    paste_global(lay, tY, mask=m3 * (1 - sx3) + m4 * (1 - sx4))
    paste_global(lay, TRIG_P, mask=m3 * sx3 + m4 * sx4)
    for (x, y), t0, sd in ((X3, 230, 3), (X4, 420, 4)):
        if t >= t0 or red:
            tt = t - t0
            k = 1.0 if red else eback(seg(tt, 0, 70))
            fd = 1 - seg(tt, 200, 330)
            if red and t0 == 420:
                fd = 1.0
            if not red:
                speed_lines(lay, x, y, 22, 54, 10, math.sin(math.pi * seg(tt, 0, 180)), op=fd, seed=sd)
            burst(lay, x, y, 20, k, seed=sd, op=fd)
    if red:
        pass


def d_kill(lay, t, c):
    u2 = GEO1['f2']['units']['2']
    tx, ty = u2['tok']
    red = c.reduce
    cell = band(214, 271, 270, 390, 60)
    if not red and 16 <= t < 50:
        lay.poly(cell, fill=WHITE + (255,), op=0.70)       # one 2-frame flare on the cell only
    if red and t < 200:
        lay.poly(cell, fill=WHITE + (255,), op=0.25)       # reduce: a 25 percent tint, held, no flare
    if t >= 34 or red:
        k = 1.0 if red else eback(seg(t, 34, 110))
        fd = 1 - seg(t, 330, 560)
        if not red:
            speed_lines(lay, tx, ty, 34, 82, 14, math.sin(math.pi * seg(t, 34, 260)), op=fd, seed=13)
            shards(lay, tx, ty, seg(t, 60, 560), n=10, dist=72, size=8, seed=17, cols=(PINK, PAPER, (96, 100, 126)), op=1 - seg(t, 440, 560))
        burst(lay, tx, ty, 36, k * (1 - 0.25 * seg(t, 330, 560)), n=12, seed=21, op=fd)


def kill_state(t, c):
    return 1.0 if c.reduce and t >= 200 else eio(seg(t, 200, 420))


def d_ricochet(lay, t, c):
    """steel: the shot meets an armour cap (L10 steel) and glances; no starburst, no HP lost"""
    u5 = GEO1['f2']['units']['5']
    tx, ty = u5['tok']
    r_, a_ = polar(tx, ty)
    capc = ppx(r_ - 29, a_)          # the cap faces the tower
    red = c.reduce
    # the latent armour cap (stand-in): a steel L10 double band on the token's tower side
    cap = [ppx(r_, a_ + d) for d in ()]  # placeholder (unused)
    ring = []
    for rr in (31.0, 35.5):
        ring.append([(tx + rr * math.sin(math.radians(a_ + 180 + d)), ty - rr * math.cos(math.radians(a_ + 180 + d))) for d in range(-48, 49, 6)])
    lay.lines(ring, STEELHI, 2.2, key=1.2)
    p0 = GUN0[0]
    u = 1.0 if red else eout(seg(t, 0, 100))
    tracer(lay, p0, capc, u, op=1 - seg(t, 250, 420))
    if t >= 100 or red:
        tt = t - 100
        g = 1.0 if red else math.sin(math.pi * seg(tt, 0, 120))
        sparkle(lay, capc[0], capc[1], 16 * g + 2, WHITE, op=1 - seg(tt, 160, 300) if not red else 1.0, rot=0.4)
        if not red:
            # steel sparks fan away from the cap (reflected around the cap normal)
            rng = np.random.RandomState(31)
            base_a = math.atan2(capc[1] - p0[1], capc[0] - p0[0])
            nrm = math.atan2(capc[1] - ty, capc[0] - tx)
            refl = 2 * nrm - base_a + math.pi
            uu = seg(tt, 0, 260)
            sp = []
            for i in range(9):
                a = refl + rng.uniform(-0.7, 0.7)
                d0 = 6 + 46 * eout(uu) * rng.uniform(0.6, 1.0)
                d1 = d0 - 12 * (1 - uu) - 3
                sp.append([(capc[0] + math.cos(a) * d1, capc[1] + math.sin(a) * d1), (capc[0] + math.cos(a) * d0, capc[1] + math.sin(a) * d0)])
            lay.lines(sp, STEELHI, 1.6, op=1 - seg(tt, 180, 320), key=0.8)


def d_ricochet_gold(lay, t, c):
    p0, p1 = GUN4
    red = c.reduce
    u = 1.0 if red else eout(seg(t, 0, 100))
    tracer(lay, p0, p1, u, op=1 - seg(t, 260, 440))
    if t >= 100 or red:
        tt = t - 100
        uu = 1.0 if red else eout(seg(tt, 0, 220))
        # a curved gold streak glancing off the ward (boss gold); no starburst
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        end = (p1[0] + 78, p1[1] - 52)
        ctrl = (p1[0] + math.cos(ang) * 30, p1[1] + math.sin(ang) * 30)
        cur = bez(p1, ctrl, end, 24)
        part = partial(cur, uu)
        fd = 1 - seg(tt, 260, 420) if not red else 1.0
        if len(part) > 2:
            thin = 1 - 0.6 * seg(tt, 150, 300)
            lay.poly(ribbon(part, lambda k: (0.6 + 3.4 * k * thin) if k < 0.85 else (0.6 + 3.4 * 0.85 * thin) * (1 - k) / 0.15 + 0.3), fill=GOLD + (255,), outline=INK, w=1.6, op=fd)
        g = 1.0 if red else math.sin(math.pi * seg(tt, 0, 120))
        lay.circle(p1[0], p1[1], 4 + 7 * g, fill=None, outline=GOLD, w=2.0, op=fd * (0.9 if not red else 0.6))


FW_TOK = [tuple(GEO1['f2']['units']['5']['tok'])]


def d_firewall(lay, t, c):
    red = c.reduce
    for ring, t0 in ((0, 0), (1, 130), (2, 260)):
        r0, r1 = RING[ring]
        depth = 0.6 * (r1 - r0)
        rise = 1.0 if red else eout(seg(t, t0, t0 + 200))
        die = 0.0 if red else seg(t, 700, 1000)
        hk = rise * (1 - 0.7 * die)
        if hk <= 0.01:
            continue
        op = 1 - 0.85 * die
        rng = np.random.RandomState(40 + ring)
        n = 7 + ring
        tongues, cores = [], []
        for i in range(n):
            ac = -27 + 54 * (i + 0.5) / n + rng.uniform(-1.5, 1.5)
            hw = 54.0 / n * rng.uniform(0.62, 0.8)
            fl = 1.0 if red else 0.88 + 0.12 * math.sin(t / 1000.0 * 2 * math.pi * 7 + i * 1.9 + ring)
            h = depth * hk * rng.uniform(0.62, 1.0) * fl
            lean = rng.uniform(-0.35, 0.35) * hw
            for (dst, hh, ww) in ((tongues, h, hw), (cores, h * 0.55, hw * 0.5)):
                pts = []
                m = 10
                for j in range(m + 1):          # left flank, base -> tip
                    k = j / m
                    wk = ww * (1 - k) ** 0.8 * (1 + 0.25 * math.sin(math.pi * k))
                    pts.append(ppx(r0 + 1 + hh * k, ac - wk + lean * k * k / (r0 / 57.3)))
                for j in range(m, -1, -1):
                    k = j / m
                    wk = ww * (1 - k) ** 0.8 * (1 + 0.25 * math.sin(math.pi * k))
                    pts.append(ppx(r0 + 1 + hh * k, ac + wk + lean * k * k / (r0 / 57.3)))
                dst.append(pts)
        # a low base band joins the tongues (one inked shape)
        base_b = band(r0 + 1, r0 + 1 + depth * hk * 0.28, -28, 28, 30)
        lay.polys(tongues + [base_b], PINK + (255,), outline=INK, w=1.9, op=op)
        lay.polys(cores, (255, 158, 210, 255), op=op)
    for (x, y) in FW_TOK:                      # never over a unit token: the flames are cut clear of the disc
        lay.erase_circle(x, y, 31)
    if t >= 330 or red:
        for i in (0, 1):
            gone_tick(lay, PIPS3['5'][i])


# ======================================================================== C corp
def c_slab(lay, ring, a0, e, skin, op, col=None, edge=None, reverse=False, lipw=2.4):
    """the corp enamel shutter over a ring cell from a0 to the leading edge e (degrees); its lip shape is the corp material"""
    r0, r1 = RING[ring]
    sl, ed = CORP_ENAMEL[skin]
    col = col or sl
    edge = edge or ed
    if op <= 0:
        return
    span = e - a0
    if abs(span) < 0.2:
        return
    sgn = 1 if span > 0 else -1
    # lip: neutral straight, Solace rounded membrane bulge, Meridian stencil notch
    lip = []
    n = 14
    for i in range(n + 1):
        k = i / n
        r = lerp(r1 - 1, r0 + 1, k)
        if skin == 'solace':
            off = 4.2 * math.sin(math.pi * k)
        elif skin == 'meridian':
            off = 0.0 if (k < 0.35 or k > 0.65) else -3.6
        else:
            off = 0.0
        lip.append(ppx(r, e + sgn * math.degrees(off / r)))
    pts = arc_pts(r1 - 1, a0, e, 30) + lip + arc_pts(r0 + 1, e, a0, 30)
    lay.poly(pts, fill=col + (255,), op=op)
    lay.line(lip, edge, lipw, op=min(1.0, op * 1.3), key=1.0)


def c_grow(lay, t, c):
    red = c.reduce
    sk = c.skin
    a0, a1 = -30.0, 30.0
    if red:
        if t < 300:
            pass
        return
    if t < 250:
        e = lerp(a0, a1, eio(seg(t, 0, 250)))
        c_slab(lay, 1, a0, e, sk, 0.72)
    elif t < 317:
        c_slab(lay, 1, a0, a1 + 0.01, sk, 0.92, lipw=0.01)            # the flat flash: the whole cell, 4 frames
    else:
        k = seg(t, 317, 460)
        c_slab(lay, 1, a0 + (a1 - a0) * eio(k), a1 + 0.01, sk, 0.72 * (1 - k))
    if t >= 300:
        k = seg(t, 300, 560)
        cx, cy = ppx(299.5, 0)
        sl, ed = CORP_ENAMEL[sk]
        lay.circle(cx, cy, 8 + 34 * eout(k), fill=None, outline=ed, w=2.2 * (1 - k) + 0.6, op=1 - k)


def grow_state(t, c):
    if c.reduce:
        return eio(seg(t, 0, 200))
    return 1.0 if t >= 280 else 0.0


ADJ_CELL = band(271, 328, 90, 150, 30)


def c_ward_on(lay, t, c):
    red = c.reduce
    if not red:
        p = math.sin(math.pi * seg(t, 0, 220))
        lay.poly(ADJ_CELL, fill=GOLD + (255,), op=0.22 * p)
        lay.line(ADJ_CELL + [ADJ_CELL[0]], (255, 236, 150), 4.4, op=p, key=1.4)
    a0, a1 = 90.0, 270.0
    if red:
        return
    if 150 <= t < 450:
        e = lerp(a0, a1, eio(seg(t, 150, 450)))
        c_slab(lay, 2, max(a0, e - 50), e, 'neutral', 0.55, col=GOLD, edge=(255, 236, 160))
    if 450 <= t < 517:
        lay.poly(band(329, 384, a0, a1, 90), fill=GOLD + (255,), op=0.42)          # one flat gold flash
    if t >= 470:
        k = seg(t, 470, 700)
        u6 = GEO1['f2']['units']['6']
        tx, ty = u6['tok']
        bx, by = tx + 8, ty + 40
        lay.circle(tx, ty, 30 + 26 * eout(k), fill=None, outline=GOLD, w=2.0 * (1 - k) + 0.6, op=1 - k)


def ward_state(t, c):
    if c.reduce:
        return eio(seg(t, 0, 200))
    return 1.0 if t >= 470 else 0.0


# ======================================================================== H harm
def h_hit_land(variant):
    def draw(lay, t, c):
        s = 3
        red = c.reduce
        ax = 60 * s
        reg = wedge(s, 124, 177)
        # chevrons slam in from the trim (r 228 -> 182)
        if t < 140:
            u = 1.0 if red else ein(seg(t, 0, 100))
            for i in range(3):
                r = lerp(232 + i * 11, 184 + i * 7, u)
                chev(lay, r, ax, op=1 - seg(t, 100, 140))
        if not red and 100 <= t < 134:
            lay.line(wedge(s) + [wedge(s)[0]], HARM, 3.4, op=1.0, key=1.2)          # the wedge frame flashes HARM once (2 frames)
        front = lerp(177, 124, 1.0 if red else eout(seg(t, 100, 260)))
        dens = 1.0 if red else seg(t, 100, 160) * (1 - seg(t, 330, 620))
        if red:
            dens = 0.8
        x_flood(lay, reg, front, 177, dens, s=s, op=1.0, seed=3)
        if not red:
            ku = seg(t, 120, 220)
            ko = 1 - seg(t, 300, 520)
            for i, (da, ln) in enumerate(((-16, 30), (2, 36), (17, 28))):
                krackle(lay, ppx(176, ax + da), ax + 180 + da * 1.2, ln, 50 + i, ku, ko)
        if variant == 'worm' and t >= 160:
            k = 1.0 if red else eback(seg(t, 160, 230))
            hx_, hy_ = ppx(185, ax - 14)
            s_ = 7 * k
            hook = [(hx_ - s_ * 0.2, hy_ - s_ * 1.2), (hx_ - s_ * 0.2, hy_ + s_ * 0.5), (hx_ + s_ * 0.2, hy_ + s_ * 0.95), (hx_ + s_ * 0.85, hy_ + s_ * 0.5), (hx_ + s_ * 0.9, hy_ + s_ * 0.05)]
            lay.line(hook, HARM, 3.0, key=1.6)
        if variant == 'adjuster' and not red:
            g = math.sin(math.pi * seg(t, 100, 200))
            lay.poly(band(178, 190, ax - 26, ax + 26, 20), fill=GOLD + (255,), outline=INK, w=1.4, op=g)
        if variant == 'adjuster' and red:
            lay.poly(band(178, 190, ax - 26, ax + 26, 20), fill=None, outline=GOLD, w=1.6, op=0.9)
        if t >= 260 or red:
            tower_pip_dark(lay, s, 1)
    return draw


PLATE_S = 1
PLATE = band(150, 188, 60 - 22, 60 + 22, 24)


def plate_draw(lay, dx=0.0, dy=0.0, op=1.0):
    P = [(x + dx, y + dy) for x, y in PLATE]
    lay.poly([(x + 3, y + 4) for x, y in P], fill=INK + (255,), op=op * 0.9)                  # hard shadow
    lay.poly(P, fill=PAPER + (255,), outline=INK, w=2.2, op=op)
    for rr in (156.0, 160.0):                                                                    # the L10 double line
        lay.line([(x + dx, y + dy) for x, y in arc_pts(rr, 60 - 19, 60 + 19, 16)], INK, 1.3, op=op)


def plate_shards():
    """the plate cut into 6 shards by jagged radial and one tangential cut"""
    cuts = [38, 46.5, 55, 63, 71.5, 82]
    out = []
    rng = np.random.RandomState(4)
    for i in range(len(cuts) - 1):
        a0, a1 = cuts[i], cuts[i + 1]
        j0 = rng.uniform(-2, 2)
        j1 = rng.uniform(-2, 2)
        pts = arc_pts(188, a0 + j0 * 0.3, a1 + j1 * 0.3, 4) + [ppx(169, a1 + j1), ppx(150, a1 + j1 * 0.4)] + arc_pts(150, a1 + j1 * 0.4, a0 + j0 * 0.4, 4) + [ppx(169, a0 + j0)]
        out.append(pts)
    return out


SHARDS = plate_shards()


def h_shield_break(lay, t, c):
    s = 1
    red = c.reduce
    ax = 60 * s
    if t < 140:
        u = 1.0 if red else eout(seg(t, 0, 110))
        for i in range(3):
            chev(lay, lerp(222 + i * 10, 196 + i * 7, u), ax - 8 + i * 8, op=1)
    # wedge goes dark (stays)
    dk = 1.0 if red else eio(seg(t, 200, 500))
    lay.poly(wedge(s), fill=INK + (255,), op=0.62 * dk)
    lay.circle(*seat_xy(s), TOWER['seat'] - 2, fill=INK + (255,), op=0.0)
    front = lerp(177, 124, 1.0 if red else eout(seg(t, 130, 300)))
    dens = (1.0 if red else seg(t, 130, 190)) * (1 - (0 if red else seg(t, 380, 680)) * 0.7)
    if red:
        dens = 0.7
    x_flood(lay, wedge(s, 118, 177), front, 177, dens, s=s, seed=5)
    if t < 120 and not red:
        plate_draw(lay)
        cu = seg(t, 20, 110)
        lay.line(partial(jag(ppx(188, 52), ppx(150, 66), 6, 3, 2), cu), WHITE, 1.6, key=0.9)
    else:
        u = 0.55 if red else seg(t, 120, 520)
        for i, sh in enumerate(SHARDS):
            cx = sum(p[0] for p in sh) / len(sh)
            cy = sum(p[1] for p in sh) / len(sh)
            r_, a_ = polar(cx, cy)
            spread = (i - 2) * 0.9
            d = 46 * eout(u)
            dx = math.sin(math.radians(a_ + spread * 6)) * d + spread * 4 * eout(u)
            dy = -math.cos(math.radians(a_ + spread * 6)) * d + 18 * u * u
            rot = (i - 2.5) * 0.5 * eout(u)
            P = [((x - cx) * math.cos(rot) - (y - cy) * math.sin(rot) + cx + dx, (x - cx) * math.sin(rot) + (y - cy) * math.cos(rot) + cy + dy) for x, y in sh]
            op = 1 - (0 if red else seg(t, 380, 560))
            lay.poly([(x + 2, y + 3) for x, y in P], fill=INK + (255,), op=op * 0.85)
            lay.poly(P, fill=PAPER + (255,), outline=INK, w=1.8, op=op)
    if not red:
        ku = seg(t, 130, 240)
        ko = 1 - seg(t, 360, 600)
        for i, (da, ln) in enumerate(((-18, 34), (-2, 40), (15, 30))):
            krackle(lay, ppx(176, ax + da), ax + 180 + da, ln, 70 + i, ku, ko)
    if t >= 300 or red:
        tower_pip_dark(lay, s, 0)
        tower_pip_dark(lay, s, 1)


def p_shield_block(lay, t, c):
    """P protect (for the block-vs-break sheet only): ONE intact plate, white sparks, flat pink wedge tint, no red"""
    s = 1
    red = c.reduce
    ax = 60 * s
    tint = 1.0 if red else math.sin(math.pi * seg(t, 100, 420)) if t < 260 else 1 - seg(t, 260, 520) * 0.0
    if t >= 100 or red:
        tl = Lay((lay.x0, lay.y0, lay.x1, lay.y1), lay.ss)
        tl.poly(wedge(s), fill=PINK + (255,))
        tl.erase_circle(*seat_xy(s), TOWER['seat'])
        lay.comp(tl.im, 0.45 * (1.0 if red else (seg(t, 100, 160) * (1 - seg(t, 360, 560)))))
    jolt = 0.0 if red else 2.2 * math.sin(math.pi * seg(t, 100, 170))
    jx, jy = math.sin(math.radians(ax)) * -jolt, -math.cos(math.radians(ax)) * -jolt
    if t < 150 or red:
        u = 1.0 if red else eout(seg(t, 0, 100))
        for i in range(3):
            chev(lay, lerp(222 + i * 10, 194 + i * 9, u), ax - 8 + i * 8, op=1 - seg(t, 110, 150) if not red else 1.0)
    plate_draw(lay, jx, jy)
    if (t >= 100 and t < 380) and not red:
        uu = seg(t, 100, 330)
        rng = np.random.RandomState(8)
        sp = []
        for i in range(16):
            a = math.radians(ax) + rng.uniform(-1.3, 1.3)
            cx, cy = ppx(190, ax + rng.uniform(-16, 16))
            d0 = 5 + 44 * eout(uu) * rng.uniform(0.6, 1.0)
            d1 = d0 - 16 * (1 - uu) - 5
            sp.append([(cx + math.sin(a) * d1, cy - math.cos(a) * d1), (cx + math.sin(a) * d0, cy - math.cos(a) * d0)])
        lay.lines(sp, WHITE, 2.4, op=1 - seg(t, 240, 380), key=1.0)
        sparkle(lay, *ppx(192, ax - 4), 13 * math.sin(math.pi * seg(t, 100, 260)) + 0.5, WHITE)


def h_slice_crack(lay, t, c):
    s = 4
    red = c.reduce
    ax = 60 * s
    if not red:
        dens = seg(t, 0, 60) * (1 - seg(t, 140, 300))
        x_flood(lay, wedge(s, 148, 177), 148, 177, dens, s=s, seed=8)
    crk = jag(ppx(178, ax + 13), ppx(124, ax + 21.5), 7, 3.2, 12)
    br = jag(crk[4], ppx(150, ax + 7), 3, 2.0, 13)
    u = 1.0 if red else eout(seg(t, 60, 260))
    lay.lines([partial(crk, u)] + ([partial(br, seg(u, 0.6, 1.0))] if u > 0.6 else []), WHITE, 2.0, key=1.2)
    if not red and 60 <= t < 300:
        tip = partial(crk, u)[-1]
        sparkle(lay, tip[0], tip[1], 6, WHITE, op=1 - seg(t, 240, 300))
    if t >= 200 or red:
        tower_pip_dark(lay, s, 1)


def h_slice_break(lay, t, c):
    s = 2
    red = c.reduce
    ax = 60 * s
    if not red:
        dens = seg(t, 0, 60) * (1 - seg(t, 160, 380))
        x_flood(lay, wedge(s, 124, 177), 124, 177, dens, s=s, seed=9)
    bk = 1.0 if red else eio(seg(t, 150, 450))
    lay.poly(wedge(s), fill=INK + (255,), op=0.72 * bk)
    # halftone fade over the icon: ink X screen on the seat
    hf = 1.0 if red else seg(t, 200, 500)
    if hf > 0:
        sx, sy = seat_xy(s)
        circ = [(sx + 36 * math.cos(i * math.pi / 18), sy + 36 * math.sin(i * math.pi / 18)) for i in range(36)]
        grid_X(lay, circ, lambda x, y: hf * (0.5 + 0.5 * clamp(1 - math.hypot(x - sx, y - sy) / 40)), pitch=5.0, col=(30, 26, 40), key=False, w=1.6)
    # red stencil X in the outer corner only
    if t >= 120 or red:
        k = 1.0 if red else eback(seg(t, 120, 200), 2.2)
        cx, cy = ppx(158, ax + 15)
        S = 9 * k
        bar = 3.4 * k
        for sg in (1, -1):
            p = [(cx - S, cy - sg * S), (cx + S, cy + sg * S)]
            lay.line(p, HARM, 2 * bar, key=1.6)
    if t >= 250 or red:
        tower_pip_dark(lay, s, 0)
        tower_pip_dark(lay, s, 1)


# ---- hp_through: six diamonds from the landing arc to the YOU strip
def you_segments():
    im = base('neutral', 'p1')
    reg = im[110:138, 1270:1400]
    red_ = (reg[:, :, 0] > 180) & (reg[:, :, 1] < 110) & (reg[:, :, 2] < 100)
    cols = red_.sum(0) > 4
    segs = []
    x = 0
    while x < len(cols):
        if cols[x]:
            x0 = x
            while x < len(cols) and cols[x]:
                x += 1
            segs.append((1270 + x0, 1270 + x - 1))
        x += 1
    return [((a + b) / 2.0, 123.5, (b - a + 1)) for a, b in segs if b - a > 6]


YOUSEG = None
HT_SRC = ppx(436, 47)


def h_hp_through(lay, t, c):
    global YOUSEG
    if YOUSEG is None:
        YOUSEG = you_segments()
    red = c.reduce
    segs = YOUSEG[-6:]
    n = len(segs)
    ctrl = (1010, 120)
    lead = None
    for i, (sx, sy, sw) in enumerate(segs):
        t0 = 120 + i * 30
        u = 1.0 if red else eio(seg(t, t0, t0 + 560))
        lift = 0 if red else eout(seg(t, i * 20, i * 20 + 120))
        p0 = (HT_SRC[0] + (i - 2.5) * 7, HT_SRC[1] - 9 * lift)
        cur = bez(p0, ctrl, (sx, sy), 60)
        if red or u >= 1.0:
            continue
        if i == 0 and 0 < u < 1:
            lead = (cur, u)
    if lead is not None:
        cur, u = lead
        a0 = max(0.0, u - 0.22)
        pts = [partial(cur, a0 + (u - a0) * k / 16)[-1] for k in range(17)]
        if math.dist(pts[0], pts[-1]) > 4:
            lay.poly(ribbon(pts, lambda k: 0.4 + 4.6 * k), fill=HARM + (255,), outline=INK, w=1.4, op=0.85)
    for i, (sx, sy, sw) in enumerate(segs):
        t0 = 120 + i * 30
        u = 1.0 if red else eio(seg(t, t0, t0 + 560))
        lift = 0 if red else eout(seg(t, i * 20, i * 20 + 120))
        p0 = (HT_SRC[0] + (i - 2.5) * 7, HT_SRC[1] - 9 * lift)
        cur = bez(p0, ctrl, (sx, sy), 60)
        if red or u >= 1.0:
            continue
        q = partial(cur, u)[-1]
        s_ = 7.5
        lay.poly([(q[0], q[1] - s_), (q[0] + s_, q[1]), (q[0], q[1] + s_), (q[0] - s_, q[1])], fill=HARM + (255,), outline=INK, w=1.8)
    # arrival: a red slap on the strip, then the hatched segments go dark
    x0 = min(s[0] - s[2] / 2 for s in segs) - 3
    x1 = max(s[0] + s[2] / 2 for s in segs) + 3
    ta = 120 + (n - 1) * 30 + 560
    if not red:
        sl = math.sin(math.pi * seg(t, ta - 80, ta + 100))
        if sl > 0:
            lay.poly([(x0 - 6, 108), (x1 + 6, 106), (x1 + 4, 141), (x0 - 4, 139)], fill=HARM + (255,), outline=INK, w=1.6, op=0.72 * sl)
    dk = 1.0 if red else seg(t, ta + 40, ta + 220)
    for (sx, sy, sw) in segs:
        lay.poly([(sx - sw / 2, 114), (sx + sw / 2, 114), (sx + sw / 2, 133), (sx - sw / 2, 133)], fill=(26, 24, 34, 255), outline=INK, w=1.2, op=dk)


# ======================================================================== L life
REFUND_AT = (444.0, 762.0)
RAM_SLOT = (1213.0, 513.0)
RAM_EMPTY = (1245.0, 513.0)


def ram_coin(lay, x, y, k, op=1.0):
    r = 12.5 * k
    lay.circle(x, y, r + 2.2, fill=INK + (255,), op=op)
    lay.circle(x, y, r, fill=CYAN + (255,), op=op)
    plus_sign(lay, x, y, 6.6 * k, INK, op=op, key=CYAN)


def l_refund(lay, t, c):
    red = c.reduce
    # pre-state: the RAM slot shows empty until the coin lands
    land = 650
    if t < land and not red:
        src = base(c.skin, 'p3')
        sx, sy = int(RAM_EMPTY[0]), int(RAM_EMPTY[1])
        tx, ty = int(RAM_SLOT[0]), int(RAM_SLOT[1])
        patch = src[sy - 23:sy + 23, sx - 17:sx + 17]
        im = Image.fromarray(patch.astype(np.uint8), 'RGB').convert('RGBA')
        big = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        big.paste(im, (tx - 17, ty - 23))
        # also hide the refund rays around the slot
        src2 = base(c.skin, 'p3')
        bg = Image.fromarray(src2[ty - 23:ty + 23, tx - 30:tx - 17].astype(np.uint8), 'RGB').convert('RGBA')
        paste_global(lay, big)
    if red:
        if t < 300:
            ram_coin(lay, REFUND_AT[0], REFUND_AT[1], 1.0, op=1 - seg(t, 150, 300))
        return
    if t < land:
        k = eback(seg(t, 0, 150), 2.0)
        u = eio(seg(t, 150, land))
        cur = bez(REFUND_AT, (900, 560), RAM_SLOT, 60)
        q = partial(cur, u)[-1]
        a0_ = max(0.0, u - 0.2)
        pts = [partial(cur, a0_ + (u - a0_) * k / 16)[-1] for k in range(17)]
        if math.dist(pts[0], pts[-1]) > 4:
            lay.glow(lambda g: g.poly(ribbon(pts, lambda k: 0.5 + 11 * k), fill=CYAN + (255,)), blur=5, op=0.6)
            lay.poly(ribbon(pts, lambda k: 0.3 + 7 * k), fill=(200, 246, 255, 255), outline=INK, w=1.2, op=0.9)
        lay.glow(lambda g: g.circle(q[0], q[1], 22 * k, fill=CYAN + (255,)), blur=6, op=0.55)
        ram_coin(lay, q[0], q[1], k * 1.6)
    else:
        k = seg(t, land, land + 260)
        lay.circle(RAM_SLOT[0], RAM_SLOT[1], 14 + 18 * eout(k), fill=None, outline=CYAN, w=2.4 * (1 - k) + 0.5, op=1 - k)
        lay.glow(lambda g: g.circle(RAM_SLOT[0], RAM_SLOT[1], 15, fill=CYAN + (255,)), blur=6, op=0.5 * (1 - k))


CLR_A = (62.0, 96.0)


def l_clear(lay, t, c):
    red = c.reduce
    r = 436.0
    a0, a1 = 31.0, 149.0
    u = 1.0 if red else eio(seg(t, 0, 240))
    e = lerp(a0, a1, u)
    op = 0.55 if red else 0.55 * (1 - 0.45 * seg(t, 400, 800))
    lay.glow(lambda g: g.poly(band(r - 10, r + 10, a0 + 2, e, 40), fill=GAIN + (255,)), blur=4, op=op * 0.9)
    lay.poly(band(r - 8, r + 8, a0 + 2, e, 40), fill=GAIN + (255,), op=op * 0.55)
    k = 1.0 if red else eback(seg(t, 160, 300), 2.0)
    if k > 0:
        cx, cy = ppx(r + 2, 70)
        S = 20 * k
        chk = [(cx - S * 0.9, cy - S * 0.05), (cx - S * 0.25, cy + S * 0.6), (cx + S * 1.0, cy - S * 0.85)]
        lay.glow(lambda g: g.line(chk, GAIN, 7), blur=4, op=0.5)
        lay.line(chk, GAIN, 6.4, key=2.0)
    if not red:
        for i, (da, dr, t0) in enumerate(((-9, -16, 300), (8, 18, 360), (14, -12, 420))):
            g = math.sin(math.pi * seg(t, t0, t0 + 260))
            if g > 0:
                x, y = ppx(r + dr, 70 + da)
                sparkle(lay, x, y, 7 * g, (236, 255, 230))


def l_repair_mend(lay, t, c):
    s = 5
    red = c.reduce
    ax = 60 * s
    wd = wedge(s)
    fill_k = 1.0 if red else eio(seg(t, 380, 560))
    tower_pip_mend(lay, s, 1, fill_k)
    if red:
        sx, sy = seat_xy(s)
        for (dx, dy) in ((-22, -30), (24, -26)):
            plus_sign(lay, sx + dx, sy + dy, 6.5, MINT)
        return
    m = lay.poly_mask(wd)
    g = Lay((lay.x0, lay.y0, lay.x1, lay.y1), lay.ss)
    rng = np.random.RandomState(61)
    strokes = []
    for i in range(6):
        a = ax - 20 + i * 8
        r = 100 + (i % 3) * 24
        x, y = ppx(r, a)
        t0 = i * 45
        u = seg(t, t0, t0 + 420)
        if u <= 0 or u >= 1:
            continue
        rise = 60 * eout(u)
        L = 34 + 10 * (i % 2)
        k = math.sin(math.pi * u)
        p = [(x + 2.5 * math.sin(j * 0.7 + i), y - rise + L * (1 - j / 9.0)) for j in range(10)]
        strokes.append((p, k))
    for p, k in strokes:
        rb = ribbon(p, lambda q: (0.5 + 6.5 * k * math.sin(math.pi * min(1.0, q * 1.15)) ** 0.7))
        g.poly(rb, fill=MINT + (255,), outline=INK, w=1.2)
    gl = g.im.copy()
    a = np.asarray(gl).copy()
    a[:, :, 3] = (a[:, :, 3] * m).astype(np.uint8)
    gl = Image.fromarray(a, 'RGBA')
    from PIL import ImageFilter as _F
    lay.comp(gl.filter(_F.GaussianBlur(5 * lay.ss)), 0.6 * (1 - seg(t, 550, 900)))
    lay.comp(gl, 1.0)
    for i, (dx, t0) in enumerate(((-24, 120), (6, 200), (26, 280), (-6, 360))):
        u = seg(t, t0, t0 + 420)
        if 0 < u < 1:
            sx, sy = seat_xy(s)
            k = math.sin(math.pi * u)
            plus_sign(lay, sx + dx, sy - 8 - 52 * eout(u), 6.5 * k + 0.5, MINT, op=k)
    if 380 <= t < 700:
        x, y = ppx(167, (wedge_pip(s, 1)[0] + wedge_pip(s, 1)[1]) / 2)
        k = math.sin(math.pi * seg(t, 380, 700))
        sparkle(lay, x, y - 4, 9 * k, WHITE)


# ======================================================================== registry
def E(id, fam, title, box, pre, draw, keys, timing, still, keep, reduce_note, skins=('neutral',), post=None, state=None, state_region=None,
      dur=None, source='', scope='', variant_of=None, tier='core'):
    return dict(id=id, fam=fam, title=title, box=box, pre=pre, post=post, state=state, state_region=state_region, draw=draw, keys=keys,
                timing=timing, still=still, keep=keep, reduce_note=reduce_note, skins=skins, dur=dur or timing['total'], source=source,
                scope=scope, variant_of=variant_of, tier=tier)


def T(total, phases, easing):
    return dict(total=total, phases=phases, easing=easing)


SK3 = ('neutral', 'solace', 'meridian')
FX = []
# ---- C corp
FX.append(E('fx_grow', 'C', 'A unit grows one more hit', (360, 170, 715, 335), 'p3', c_grow,
            [(0, 'anticipate: two solid chevrons'), (120, 'shutter wipes the cell'), (280, 'flat flash, the new hollow chevron'), (380, 'shutter opens, ring ping'), (650, 'settle: hollow growth chevron')],
            T(650, dict(wipe=[0, 250], flash=[250, 317], open=[317, 460], ping=[300, 560]), dict(wipe='ease-in-out cubic', flash='step (4 frames)', open='ease-in-out cubic', ping='ease-out cubic')),
            'The corp enamel shutter (the corp\'s own frame enamel, flat, no texture) wipes the unit cell, one flat 4-frame flash, the new hollow growth chevron is there when it opens, a thin ring ping in the corp edge colour.',
            'flat corp enamel slab with a hard lip (neutral straight, Solace rounded membrane lip, Meridian notched stencil lip); one flash; the hollow chevron is the only state change.',
            'No shutter or ping: the hollow chevron fades in over 200 ms (ease-in-out).', skins=SK3, post='p3grow', state=grow_state,
            state_region=band(268, 331, -33, 33, 30), source='f2 Packet 5 (ring +1, sector 0); post-state rendered with one more landing hit (land_hit = hit + 1), which the board draws as the hollow growth chevron', scope='cell-wide', tier='lower'))
FX.append(E('fx_ward_on', 'C', 'Ward applies to units in the Adjuster sector', (690, 470, 918, 860), 'p3alt', c_ward_on,
            [(0, 'anticipate'), (120, 'the Adjuster edge pulses gold'), (245, 'gold scan wipes the unit cell'), (480, 'flat gold flash, lozenge'), (750, 'settle: unit warded')],
            T(750, dict(pulse=[0, 220], wipe=[150, 450], flash=[450, 517], ping=[470, 700]), dict(pulse='sine', wipe='ease-in-out cubic', flash='step (4 frames, 42 %)', ping='ease-out cubic')),
            'The Adjuster cell edge pulses gold, a gold shutter scan crosses the warded unit\'s cell, one flat gold flash, and the gold ward lozenge is on the token when it clears.',
            'gold is the boss colour only: gold scan, gold flash, the gold lozenge; flat, no texture.',
            'No pulse, scan or flash: the lozenge fades in over 200 ms.', skins=SK3, post='p3', state=ward_state,
            state_region=band(326, 388, 92, 125, 20), source='f2 Packet 6 (ring +2, warded) next to the Adjuster (ring +1, sector 2); pre-state rendered unwarded', scope='cell-wide', tier='lower'))
# ---- D damage
FX.append(E('fx_gun_hit', 'D', 'Gun shot hits a unit', (270, 250, 600, 450), 'p3', d_gun_hit,
            [(0, 'anticipate'), (60, 'tracer paints'), (140, 'burst opens'), (210, 'peak: starburst, speed lines, shards'), (400, 'shards out, tick gone'), (600, 'settle: tick gone')],
            T(600, dict(tracer=[0, 100], burst=[100, 170], speed_lines=[100, 280], shards=[120, 460], tick=[170, 260], out=[300, 520]), dict(tracer='ease-out cubic', burst='ease-out back (overshoot)', speed_lines='sine in/out', shards='ease-out cubic', out='linear')),
            'A painted pink tracer from the BURST gun to the Worm\'s cell, a keylined pink starburst with a white core, converging speed lines, flat shards; the struck HP tick flashes pink and goes to the gone socket.',
            'pink painted tracer, keylined pink starburst with a white core, speed lines converge on the star; the tick ends as a gone socket (no hatch after the hit).',
            'Tracer and burst appear at full size for 300 ms, then fade 200 ms; no speed lines, no shards; the tick goes gone on the same frame.', skins=SK3,
            source='f2 guns: sector 0 BURST, 2 shots hit Worm 2 (shot 1 shown)', scope='cell-wide'))
FX.append(E('fx_strike', 'D', 'Strike card hits for 2', (110, 300, 380, 560), 'p3', d_strike,
            [(0, 'anticipate'), (70, 'the slash crosses the cell'), (160, 'peak: big starburst, speed lines'), (320, 'two ticks gone'), (700, 'settle')],
            T(700, dict(slash=[0, 120], burst=[120, 200], speed_lines=[120, 330], shards=[130, 520], ticks=[200, 300], out=[380, 640]), dict(slash='ease-out cubic', burst='ease-out back', speed_lines='sine', shards='ease-out cubic', out='linear')),
            'A bigger pink starburst plus one painted slash with a white core; the two struck ticks flash pink and go to gone sockets.',
            'a bigger version of the gun starburst plus one painted slash with a white core; pink ownership.',
            'Slash and burst shown full at once for 300 ms, fade 200 ms; no speed lines or shards.', skins=SK3,
            source='latent (Strike is not in this hand): Strike (2) on Packet 7, ring +2 sector 5', scope='cell-wide'))
FX.append(E('fx_trigger_hit', 'D', 'Trigger hits units along its path', (240, 600, 720, 900), 'p3', d_trigger_hit,
            [(0, 'anticipate: pencil route'), (200, 'pencil burns to paint'), (260, 'first starburst (sector 3)'), (450, 'second starburst (sector 4)'), (900, 'settle: painted marks')],
            T(900, dict(ignite=[0, 420], burst_s3=[230, 560], burst_s4=[420, 750], route_out=[650, 900]), dict(ignite='linear (front to back)', bursts='ease-out back', out='linear')),
            'The yellow pencil route from the Payload ignites into pink paint front to back, and a starburst pops at each struck cell in sector order (3 then 4); the hit marks end painted pink.',
            'pencil ignites into pink paint front to back; a starburst per struck cell, in sector order, one at a time.',
            'Route shown painted at once; the two bursts appear together for 300 ms, no speed lines.', skins=SK3,
            source='f2 trigs: Trigger resolves Payload 4, its hits land on Packet 1 in sectors 3 and 4 (tlog trig_unit)', scope='cell-wide, one burst per struck cell'))
FX.append(E('fx_kill', 'D', 'A unit dies', (195, 240, 690, 575), 'p3', d_kill,
            [(0, 'anticipate: lost ticks'), (33, 'flare: 2 frames on the cell'), (120, 'KO burst, speed lines'), (300, 'shards, cell empties'), (600, 'settle: empty cell')],
            T(600, dict(flare=[17, 50], burst=[34, 110], speed_lines=[34, 260], shards=[60, 560], empty=[200, 420], out=[330, 560]), dict(flare='step (2 frames, 70 %)', burst='ease-out back', shards='ease-out cubic', empty='ease-in-out cubic', out='linear')),
            'One 2-frame white flare on the unit\'s cell only (70 %), a KO starburst at the token with no word, shards fly, and the cell is left empty.',
            'one 2-frame flare on the CELL only (never the frame); KO burst with NO word; shards; empty cell.',
            'No flare: a 25 % white tint holds on the cell for 200 ms while the burst shows; the cell empties with a 220 ms fade.', skins=SK3, post='p3kill', state=kill_state,
            state_region=band(206, 279, 266, 394, 60), source='f2: Worm 2 dies to the sector 0 guns (fate dies); post-state rendered with Worm 2 and its shots removed (empty cell)', scope='cell-wide'))
FX.append(E('fx_ricochet', 'D', 'Shot glances off armour (steel)', (340, 190, 600, 380), 'p3', d_ricochet,
            [(0, 'anticipate: armour cap'), (60, 'tracer'), (130, 'tracer meets the cap, glint'), (230, 'sparks fan away'), (500, 'settle: HP unchanged')],
            T(500, dict(tracer=[0, 100], glint=[100, 220], sparks=[100, 360], out=[250, 420]), dict(tracer='ease-out cubic', glint='sine', sparks='ease-out cubic', out='linear')),
            'A tracer meets the steel armour cap; a white glint and steel sparks fan away. No starburst, no HP lost.',
            'NO starburst, NO HP lost: a white glint and steel sparks off the cap (steel = armour).',
            'Tracer and glint shown still for 300 ms; no sparks.', skins=SK3,
            source='latent (no armoured unit in E10): stand-in steel cap drawn on Packet 5', scope='cell-wide'))
FX.append(E('fx_ricochet_gold', 'D', 'Shot weakened by the ward (gold)', (420, 730, 650, 945), 'p3', d_ricochet_gold,
            [(0, 'anticipate'), (60, 'tracer toward the ward'), (160, 'gold streak glances'), (300, 'streak at full length'), (500, 'settle: no HP lost')],
            T(500, dict(tracer=[0, 100], streak=[100, 320], ring=[100, 220], out=[260, 520]), dict(tracer='ease-out cubic', streak='ease-out cubic', out='linear')),
            'Same beat, gold: the streak curves off the ward; no starburst. In E10 the warded shots deal 0 (h 0), so no tick changes.',
            'as fx_ricochet, with the variant mark: a curved GOLD streak; gold = ward.',
            'Tracer and the full streak shown still for 300 ms.', skins=SK3, variant_of='fx_ricochet',
            source='f2 guns: sector 4 BURST, 2 shots warded by Packet 6 (result ward, h 0)', scope='cell-wide'))
FX.append(E('fx_firewall_burn', 'D', 'Firewall burns a sector', (330, 110, 745, 365), 'p3', d_firewall,
            [(0, 'anticipate'), (100, 'flames catch in ring NOW'), (260, 'band steps out to ring +1'), (520, 'peak: a band per ring, 60 % deep'), (850, 'embers fade, ticks gone')],
            T(1000, dict(ring0=[0, 200], ring1=[130, 330], ring2=[260, 460], ticks=[330, 330], embers=[700, 1000]), dict(rise='ease-out cubic', flicker='sine 9 Hz on tongue height (no luminance swing)', embers='linear')),
            'In each ring cell of the column a low pink flame band rises from the inner edge to 60 % of the cell depth, inked, lighter pink core, no white; the band steps outward ring by ring; struck ticks go to gone sockets.',
            'a low PINK flame band per ring cell, 60 % of the cell depth, inked, no white cores; steps out ring by ring.',
            'All three bands appear at full height at once, no flicker, hold 500 ms, fade 300 ms.', skins=SK3,
            source='latent (Firewall is not in this hand): Firewall (2) on sector 0; Packet 5 loses its 2 ticks', scope='cell-wide, one band per ring', tier='lower'))
# ---- H harm
FX.append(E('fx_hit_land', 'H', 'Landing hit, one slice pip lost', (405, 590, 670, 790), 'p1', h_hit_land(None),
            [(0, 'anticipate: chevrons land'), (117, 'impact: frame flashes HARM'), (200, 'flood rolls in, krackle'), (400, 'flood fades, pip gone'), (700, 'settle: pip gone')],
            T(700, dict(chevrons=[0, 100], frame_flash=[100, 134], flood=[100, 260], krackle=[120, 520], flood_out=[330, 620], pip=[260, 260]), dict(chevrons='ease-in cubic', frame_flash='step (2 frames)', flood='ease-out cubic', out='linear')),
            'Three HOT chevrons slam in from the trim, the wedge frame flashes HARM once, a red X-halftone flood rolls in over the outer half (the icon seat stays clear), black krackle with red misregistration at the rim; the hatched pip goes dark.',
            'flood over the outer half only, never on the icon seat; frame flashes HARM once; X-only dots (never round, so it never reads as the BURST Ben-Day).',
            'No chevron travel or krackle: the flood holds at 80 % density for 300 ms and fades; the pip goes dark on the same frame.',
            source='f1 Packet 1 lands on sector 3 SHIELD (3 hits, 1 pip through)', scope='slice-wide (outer half)'))
FX.append(E('fx_hit_land_worm', 'H', 'Hit-land variant: worm wear (hook mark)', (405, 590, 670, 790), 'p1', h_hit_land('worm'),
            [(0, 'anticipate'), (117, 'impact'), (200, 'flood and krackle, hook stamps'), (400, 'flood fades'), (700, 'settle: pip gone, hook stays')],
            T(700, dict(as_parent=[0, 700], hook=[160, 230]), dict(hook='ease-out back')),
            'As fx_hit_land, then a red hook mark stamps on the rim and stays as the wear mark.', 'as fx_hit_land, plus the hook; the variant mark is the only change.',
            'As the parent; the hook appears without overshoot.', variant_of='fx_hit_land', source='f1 Worm 3 lands (wear flag); shown on sector 3', scope='slice-wide'))
FX.append(E('fx_hit_land_adjuster', 'H', 'Hit-land variant: Adjuster strike (gold rim flash)', (405, 590, 670, 790), 'p1', h_hit_land('adjuster'),
            [(0, 'anticipate'), (117, 'impact'), (150, 'gold rim flash'), (400, 'flood fades'), (700, 'settle')],
            T(700, dict(as_parent=[0, 700], gold_flash=[100, 200]), dict(gold_flash='sine, once')),
            'As fx_hit_land plus ONE gold rim flash (gold = the boss).', 'as fx_hit_land, plus one gold rim flash; the variant mark is the only change.',
            'As the parent; the gold rim shows as a thin outline, no flash.', variant_of='fx_hit_land', source='latent: Adjuster strike (adj.strike false in E10)', scope='slice-wide'))
FX.append(E('fx_shield_break', 'H', 'Our shield slice breaks while blocking', (565, 320, 785, 560), 'p1', h_shield_break,
            [(0, 'anticipate: plate under load'), (80, 'hairline crack'), (180, 'plate splits, flood starts'), (330, 'shards fly, wedge darkens'), (700, 'settle: wedge dark, shield gone')],
            T(700, dict(load=[0, 110], crack=[20, 110], split=[120, 120], shards=[120, 560], flood=[130, 300], krackle=[130, 600], dark=[200, 500], pips=[300, 300]), dict(load='ease-out cubic', shards='ease-out cubic + gravity', flood='ease-out cubic', dark='ease-in-out cubic')),
            'The same paper plate as the block, but in 5 shards flying out; a red X-halftone flood and black krackle behind it; the wedge ends dark and both pips go dark.',
            'the same plate as the block, but in shards; red flood and krackle; wedge ENDS dark. Block and break are never alike in one frame.',
            'No shard flight or krackle: the plate shows split in place (shards offset 55 %) for 300 ms; flood at 70 %; the wedge darkens in one 300 ms fade.',
            source='f1 sector 1 SHIELD, hp 2 -> 0', scope='slice-wide'))
FX.append(E('fx_slice_crack', 'H', 'Slice goes 2 to 1 (cracked)', (335, 515, 525, 725), 'p1', h_slice_crack,
            [(0, 'anticipate'), (60, 'flood pulse at the rim'), (160, 'crack runs, white tip'), (260, 'crack done, pip gone'), (500, 'settle: cracked, one pip left')],
            T(500, dict(flood=[0, 300], crack=[60, 260], tip=[60, 300], pip=[200, 200]), dict(flood='linear', crack='ease-out cubic')),
            'A jagged white crack runs from the rim beside the icon (never across it) and stays as the cracked mark; one pip left.',
            'a jagged WHITE crack beside the icon, never across it, stays; one pip left.',
            'No flood pulse or tip spark: the crack draws in 150 ms linear.', source='f1 sector 4 BURST, hp 2 -> 1', scope='slice-wide'))
FX.append(E('fx_slice_break', 'H', 'Slice goes to 0, ability lost', (570, 515, 740, 710), 'p1', h_slice_break,
            [(0, 'anticipate'), (90, 'flood'), (180, 'X stamps in the outer corner'), (330, 'black-out over a halftone fade'), (650, 'settle: dark wedge, X stays')],
            T(650, dict(flood=[0, 380], stamp=[120, 200], blackout=[150, 450], halftone=[200, 500], pips=[250, 250]), dict(stamp='ease-out back (strong)', blackout='ease-in-out cubic', halftone='linear')),
            'Wedge black-out with a red stencil X in the outer corner (never on the icon); the icon fades out behind an ink X-halftone.',
            'black-out of the wedge, red stencil X in the OUTER corner only, halftone fade over the icon; the X stays.',
            'No flood or overshoot: black-out, X and halftone fade in together over 300 ms.', source='f1 sector 2 TURRET, hp 2 -> 0', scope='slice-wide'))
FX.append(E('fx_hp_through', 'H', 'HP gets through, diamonds fly to YOU', (700, 40, 1420, 330), 'p1', h_hp_through,
            [(0, 'anticipate'), (100, 'diamonds lift off the arc'), (420, 'flight on one curve, ribbon trail'), (900, 'arrival: the strip takes the slap'), (1150, 'settle: segments dark')],
            T(1150, dict(lift=[0, 220], flight=[120, 880], slap=[800, 980], dark=[920, 1100]), dict(lift='ease-out cubic', flight='ease-in-out cubic, 40 ms stagger', slap='sine, once', dark='linear')),
            'Six red diamonds lift off the landing arc and ride ONE shared curve to their own YOU segments; the taped YOU strip takes one red slap; the six hatched segments go dark.',
            'six diamonds ride ONE smooth curve, board and HUD in one frame; the YOU strip stays the taped player paper; red slap then dark.',
            'No flight: the six hatched segments go dark in a 200 ms fade, no slap.', source='f1 pv: through 6, HP 15 -> 9', scope='arc to HUD'))
# ---- L life
FX.append(E('fx_refund', 'L', 'Trigger-kill refund, +1 RAM', (410, 480, 1280, 800), 'p3', l_refund,
            [(0, 'anticipate'), (110, 'coin pops with a plus'), (400, 'coin flies, ribbon trail'), (680, 'lands: the RAM coin lights'), (900, 'settle')],
            T(900, dict(pop=[0, 150], flight=[150, 650], light=[650, 910]), dict(pop='ease-out back (overshoot)', flight='ease-in-out cubic', light='ease-out cubic')),
            'A NET_CYAN RAM coin with a plus pops at the refund mark and flies one curve to the RAM row; the new coin lights with a soft glow ring.',
            'the RAM coin is NET_CYAN (the terminal) with a plus; it pops at the kill and flies to the RAM row on one curve.',
            'No flight: the coin fades at the refund mark (150 ms) and the RAM slot lights at once.', skins=SK3,
            source='f2: Trigger kills Packet 1, refund 1 RAM (ram 3 + 1)', scope='cell to HUD'))
FX.append(E('fx_clear', 'L', 'Nothing gets through (arc check)', (790, 175, 1010, 570), 'p3', l_clear,
            [(0, 'anticipate: the arc'), (150, 'green wash sweeps the arc'), (260, 'check paints in'), (450, 'check with sparkles'), (800, 'settle')],
            T(800, dict(wash=[0, 240], check=[160, 300], sparkles=[300, 680], wash_settle=[400, 800]), dict(wash='ease-in-out cubic', check='ease-out back', sparkles='sine')),
            'A GAIN wash sweeps the landing arc and a painted GAIN check stamps in; the arc stays lightly washed.',
            'a GAIN green check on the arc; the one soft glow family.',
            'No sweep or sparkles: wash and check fade in over 200 ms.', skins=SK3,
            source='f2: Worm 3 lands on sectors 1-2, soaked and braced, THROUGH 0', scope='arc', tier='still'))
FX.append(E('fx_repair_mend', 'L', 'Repair mends one pip', (330, 360, 510, 590), 'p3', l_repair_mend,
            [(0, 'anticipate: mend-pending pip'), (160, 'strokes rise through the wedge'), (330, 'peak: strokes, plus signs'), (520, 'pip lands'), (900, 'settle: pip restored')],
            T(900, dict(strokes=[0, 645], plus=[120, 780], pip_fill=[380, 560], glow_out=[550, 900]), dict(strokes='ease-out cubic rise, sine width', pip_fill='ease-in-out cubic')),
            'Mint brush strokes with a soft glow rise through the green REPAIR wedge with plus signs; the mend-pending pip (GAIN outline) fills.',
            'rising strokes, plus signs, the pip fills; the only soft rising glow in the set. On the green REPAIR wedge the strokes are mint with an ink key (GAIN green would vanish on it).',
            'No strokes or glow: two static plus signs and the pip fills over 200 ms.',
            source='latent (REPAIR slice mend preview, sector 5); mend-pending pip drawn as a stand-in', scope='slice-wide', tier='lower'))

SHIELD_BLOCK = E('fx_shield_block', 'P', 'Our shield slice blocks (for the comparison only)', (565, 320, 785, 560), 'p1', p_shield_block,
                 [(0, 'anticipate'), (80, 'chevrons hit the plate'), (180, 'peak: white sparks, pink tint'), (320, 'sparks out'), (560, 'settle: plate intact')],
                 T(560, dict(chevrons=[0, 100], jolt=[100, 170], sparks=[100, 380], tint=[100, 560]), dict(chevrons='ease-out cubic', sparks='ease-out cubic')),
                 'ONE intact paper plate, chevrons stop and spark white, a flat pink wedge tint, hard shadow, no red, no glow.',
                 'intact plate, L10 double line, white sparks, no red, hard shadow, no glow.', 'Plate and tint still; no sparks or jolt.',
                 source='same sector as the break (sector 1) so the two read side by side', scope='slice-wide')
BYID = {f['id']: f for f in FX}
