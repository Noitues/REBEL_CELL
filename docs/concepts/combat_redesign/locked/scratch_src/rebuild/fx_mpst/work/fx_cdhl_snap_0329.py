"""fx_cdhl (2026-11-03 rebuild): the C corp, D damage, H harm and L life effects (plus P shield_block, for the block-vs-break sheet only) on
the rebuilt board.  Each effect: box (screen crop), pre / post base, state(t) (0..1 post share inside state_region), draw(lay, t, ctx) into the
UNDER layer (below the HUD and the hand), draw_over only for the effects allowed to cross the HUD (hp_through, refund), keys (ms, caption), timing.

Review fixes carried here (locked/REVIEW_RESPONSE.md):
  1.6   every effect composites under the HUD and the hand (fxk_lib.frame_parts); hp_through and refund draw above it, as allowed
  1.8   kill marks in the cause colour: the KO burst, its core and the shards are CELL_PINK (our kill); no GAIN, FOCUS or lime in any effect
        but L (fxk_lib.colour_guard measures it per frame)
  2.10  loudness order damage > kill > block > state (measured: peak area x value, fx_build): fx_grow and fx_ward_on are a thin scan line and a
        4-frame flash on the new mark only (were a whole-cell slab and a third of a ring in gold); fx_gun_hit is a cell-sized comic hit frame
        (starburst R 44, was 22); the kill flare is on the token disc only (was the whole cell at 70 %)
  2.11  every effect is 600 ms or less (VfxTier T2), with no per-effect override (asserted in E())
  3.10  the FX-P plate (block, and its shards in the break) is its own stock, pink-tinted paper P_STOCK #F6C8DE, not the card bone PAPER
Materials (unchanged in kind):
  C corp   : a clean vector scan line in the skin's own enamel ink (neutral ENAMEL, Solace celadon, Meridian rust), then one 4-frame flash on
             the new mark only; BOSS_GOLD for the ward.  Flat, no texture.
  D damage : player-owned comic hit frame: painted pink tracer, ink-keylined pink starburst with a white core, converging speed lines,
             flat vector shards (pink / pink tint / ink), never textured.
  H harm   : misregistered red print: X-only halftone flood (no round dots), black krackle with a 2 px red misregistration, red stencil X.
  L life   : the one soft rising glow in the set: brush strokes, plus signs and four-point sparkles; GAIN green on dark, mint on the green
             REPAIR wedge, NET_CYAN for the RAM coin.
"""
import math, json
import numpy as np
from PIL import Image, ImageFilter
from fxk_lib import *

GEO1 = json.load(open(W + 'geo_neutral_p1.json'))      # f1 (decide / p1) tokens and HP ticks on the rebuilt board
GEO3 = json.load(open(W + 'geo_neutral_p3.json'))      # f2 (resolve / p3)
PIPS3 = GEO3['pips']
TOK1 = {k: tuple(v) for k, v in GEO1['tokens'].items()}
TOK3 = {k: tuple(v) for k, v in GEO3['tokens'].items()}
GOUT = (84, 92, 120)
GIN = (14, 16, 30)


# ======================================================================== shared pieces
def gone_tick(lay, pip, op=1.0):
    aa, ab, r0, r1 = pip[:4]
    lay.poly(band(r0, r1, aa, ab, 4), fill=GIN + (255,), outline=GOUT, w=1.0, op=op)


def tick_flash(lay, pip, op, col=PINK):
    aa, ab, r0, r1 = pip[:4]
    lay.poly(band(r0 - 2, r1 + 2, aa - 1, ab + 1, 4), fill=col + (255,), op=op)


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


def tracer(lay, p0, p1, u, w0=2.2, w1=5.6, col=PINK, op=1.0):
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
    lay.poly(left + right[::-1], fill=col + (255,), outline=INK, w=1.6, op=op)


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


def burst(lay, cx, cy, R, k=1.0, n=9, rot=0.3, seed=3, core=True, col=PINK, core_col=WHITE, core_k=0.50, op=1.0):
    if k <= 0 or op <= 0:
        return
    pts = starburst(cx, cy, R * k, R * k * 0.46, n, rot, 0.16, seed)
    lay.poly(pts, fill=col + (255,), outline=INK, w=2.8, op=op)
    if core:
        p2 = starburst(cx, cy, R * k * core_k, R * k * core_k * 0.5, n, rot + 0.15, 0.1, seed + 1)
        lay.poly(p2, fill=core_col + (255,), op=op)


TOWER_CLIP = 199.0             # D speed lines on a ring cell stop at the tower rim (r 196 + keyline): they never cross the player's slices


def speed_lines(lay, cx, cy, r_in, r_out, n, u, seed=5, col=WHITE, op=1.0, wmax=2.6, clip_tower=True):
    """converging speed lines: tapered spikes from r_out toward the hit, drawn in on u 0..1 then retracting; clipped off the tower"""
    if op <= 0 or u <= 0:
        return
    rng = np.random.RandomState(seed)
    polys = []
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.12, 0.12)
        ro = r_out * rng.uniform(0.85, 1.1)
        ri = lerp(ro, r_in, u)
        w = rng.uniform(1.3, wmax)
        ca, sa = math.cos(a), math.sin(a)
        polys.append([(cx + ca * ro - sa * w, cy + sa * ro + ca * w), (cx + ca * ri, cy + sa * ri), (cx + ca * ro + sa * w, cy + sa * ro - ca * w)])
    if not clip_tower:
        lay.polys(polys, col + (255,), outline=INK, w=1.2, op=op)
        return
    tl = Lay((lay.x0, lay.y0, lay.x1, lay.y1), lay.ss)
    tl.polys(polys, col + (255,), outline=INK, w=1.2)
    tl.erase_circle(C[0], C[1], TOWER_CLIP)
    lay.comp(tl.im, op)


def shards(lay, cx, cy, u, n=7, dist=44, size=7, seed=7, cols=(PINK, PINKCORE, INK), op=1.0, dirs=None):
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
        lay.poly(pts, fill=c + (255,), outline=INK if c != INK else PINKCORE, w=1.1, op=op)


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


def krackle(lay, p0, ang, length, seed, u=1.0, op=1.0, w=2.4):
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


def x_flood(lay, region, front_r, r_hi, dens, s=None, pitch=6.0, op=1.0, w=1.8, col=HARM):
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
        return dens * (0.62 + 0.38 * k)
    grid_X(lay, region, d, pitch=pitch, col=col, op=op, misreg=(1.6, 1.2), w=w)


def chev(lay, r, ang, w=13, h=8, th=4.6, col=HARM, op=1.0):
    """a HOT threat chevron pointing inward on the radius r at angle ang (the board's chevron grammar)"""
    tip = ppx(r, ang)
    t = math.radians(ang)
    ux, uy = math.sin(t), -math.cos(t)       # outward
    px_, py_ = math.cos(t), math.sin(t)      # tangent
    a = (tip[0] + ux * h + px_ * w, tip[1] + uy * h + py_ * w)
    b = (tip[0] + ux * h - px_ * w, tip[1] + uy * h - py_ * w)
    lay.line([a, tip, b], col, th, op=op, key=1.8)


_DM = {}


def diff_mask(lay, skin, pre, post, region, thr=10):
    """the post-state's new pixels (post vs pre, as composited) inside region, at the layer's supersampled size: the 'new mark' a C flash sits on"""
    k = (skin, pre, post, lay.x0, lay.y0, lay.x1, lay.y1, lay.ss)
    if k not in _DM:
        x0, y0, x1, y1 = lay.x0, lay.y0, lay.x1, lay.y1
        d = np.abs(base(skin, post)[y0:y1, x0:x1] - base(skin, pre)[y0:y1, x0:x1]).max(axis=2) > thr
        m = Image.fromarray((d * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))
        m = np.asarray(m.resize((lay.w * lay.ss, lay.h * lay.ss), Image.BILINEAR)).astype(np.float32) / 255.0
        _DM[k] = m * lay.poly_mask(region)
    return _DM[k]


# ======================================================================== D damage
GUN0 = ((560.0, 353.0), (416.0, 330.0))          # sector 0 BURST gun -> Worm 2 (the p3 tracer and its hit star)
GUN4 = ((361.0, 607.0), (535.0, 893.0))          # sector 4 BURST gun -> warded Packet 6 (gold ward mark)
GUN_R = 44.0                                     # review 2.10: the gun hit frame is cell-sized (the old 22 px star was the quietest event)


def d_gun_hit(lay, t, c):
    (p0, p1) = GUN0
    red = c.reduce
    u = 1.0 if red else eout(seg(t, 0, 80))
    tracer(lay, p0, p1, u, op=1 - seg(t, 300, 460))
    if t >= 80 or red:
        k = 1.0 if red else eback(seg(t, 80, 140))
        fade = 1 - seg(t, 300, 520) if not red else 1 - seg(t, 300, 500)
        if not red:
            speed_lines(lay, p1[0], p1[1], GUN_R * 0.7, GUN_R * 2.3, 14, math.sin(math.pi * seg(t, 80, 300)), op=fade, seed=5)
            shards(lay, p1[0], p1[1], seg(t, 100, 420), n=8, dist=GUN_R * 1.6, size=8, op=1 - seg(t, 330, 420))
        burst(lay, p1[0], p1[1], GUN_R, k * (1 - 0.25 * seg(t, 300, 520)), n=11, seed=3, op=fade)
    if t >= 140 or red:
        gone_tick(lay, PIPS3['2'][1])
        if not red:
            tick_flash(lay, PIPS3['2'][1], 1 - seg(t, 140, 230))


def d_strike(lay, t, c):
    tx, ty = TOK3['7']
    hx_, hy_ = tx + 22, ty - 70          # the hit lands mid-cell between the token and its ticks
    red = c.reduce
    a = (hx_ - 76, hy_ + 62)
    b = (hx_ + 70, hy_ - 56)
    us = 1.0 if red else eout(seg(t, 0, 90))
    fade = 1 - seg(t, 340, 560)
    if t < 560:
        sl = (lerp(a[0], b[0], us), lerp(a[1], b[1], us))
        L = math.hypot(sl[0] - a[0], sl[1] - a[1]) or 1
        nx, ny = -(sl[1] - a[1]) / L, (sl[0] - a[0]) / L
        mid = ((a[0] + sl[0]) / 2, (a[1] + sl[1]) / 2)
        wd = 8.0
        pts = [a, (mid[0] + nx * wd, mid[1] + ny * wd), sl, (mid[0] - nx * wd * 0.6, mid[1] - ny * wd * 0.6)]
        lay.poly(pts, fill=PINK + (255,), outline=INK, w=2.0, op=fade)
        lay.line([(lerp(a[0], sl[0], 0.15), lerp(a[1], sl[1], 0.15)), (lerp(a[0], sl[0], 0.8), lerp(a[1], sl[1], 0.8))], WHITE, 2.0, op=fade)
    if t >= 90 or red:
        k = 1.0 if red else eback(seg(t, 90, 150))
        if not red:
            speed_lines(lay, hx_, hy_, 38, 104, 16, math.sin(math.pi * seg(t, 90, 300)), op=fade, seed=9)
            shards(lay, hx_, hy_, seg(t, 100, 420), n=9, dist=68, size=8, op=1 - seg(t, 340, 420), seed=11)
        burst(lay, hx_, hy_, 52, k * (1 - 0.2 * seg(t, 340, 560)), n=12, seed=5, op=fade)
    if t >= 150 or red:
        for i in (1, 2):
            gone_tick(lay, PIPS3['7'][i])
        if not red:
            for i in (1, 2):
                tick_flash(lay, PIPS3['7'][i], 1 - seg(t, 150, 240))


TRIG_Y = Image.open(W + 'trig_yel.png').convert('RGBA')
TRIG_P = Image.open(W + 'trig_pink.png').convert('RGBA')
PAYLOAD = TOK3['4']
X3, X4 = (536.0, 785.0), (325.0, 667.0)
TRIG_R = 40.0


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


_TM = {}


def d_trigger_hit(lay, t, c):
    red = c.reduce
    route = trig_route()
    ign = 1.0 if red else seg(t, 0, 240)
    # pencil route (yellow) under, painted pink front to back over it
    if not red:
        lay.line(route, (255, 226, 0), 3.0, op=(1 - seg(t, 240, 320)) * 0.95, key=1.2)
    lay.line(partial(route, ign), PINK, 4.6, key=1.6, op=1 - seg(t, 420, 600))
    sx3 = 1 if (t >= 120 or red) else 0
    sx4 = 1 if (t >= 240 or red) else 0
    k_ = (lay.x0, lay.y0, lay.x1, lay.y1, lay.ss)
    if k_ not in _TM:
        ss = lay.ss
        yy, xx = np.mgrid[0:lay.h * ss, 0:lay.w * ss]
        X = xx / ss + lay.x0
        Y = yy / ss + lay.y0
        _TM[k_] = ((np.hypot(X - X3[0], Y - X3[1]) < 70).astype(np.float32), (np.hypot(X - X4[0], Y - X4[1]) < 70).astype(np.float32))
    m3, m4 = _TM[k_]
    paste_global(lay, TRIG_Y, mask=m3 * (1 - sx3) + m4 * (1 - sx4))
    paste_global(lay, TRIG_P, mask=m3 * sx3 + m4 * sx4)
    for (x, y), t0, sd in ((X3, 120, 3), (X4, 240, 4)):
        if t >= t0 or red:
            tt = t - t0
            k = 1.0 if red else eback(seg(tt, 0, 60))
            fd = 1 - seg(tt, 200, 340) if not red else 1.0
            if not red:
                speed_lines(lay, x, y, TRIG_R * 0.7, TRIG_R * 2.2, 12, math.sin(math.pi * seg(tt, 0, 220)), op=fd, seed=sd)
                shards(lay, x, y, seg(tt, 20, 300), n=7, dist=TRIG_R * 1.5, size=7, op=1 - seg(tt, 230, 300), seed=sd + 20)
            burst(lay, x, y, TRIG_R, k, n=11, seed=sd, op=fd)


KILL_TOK = TOK3['2']


def d_kill(lay, t, c):
    """review 1.8: every kill mark is in the cause colour (CELL_PINK, our guns): pink KO burst with a pink-tint core, pink / tint / slate shards.
    review 2.10: the 2-frame flare is on the token disc only, at 55 % (was the whole cell at 70 %), so the kill sits under every damage hit."""
    tx, ty = KILL_TOK
    red = c.reduce
    if not red and 16 <= t < 50:
        lay.circle(tx, ty, 29, fill=WHITE + (255,), op=0.55)
    if red and t < 200:
        lay.circle(tx, ty, 29, fill=PINKCORE + (255,), op=0.30)
    if t >= 34 or red:
        k = 1.0 if red else eback(seg(t, 34, 100))
        fd = 1 - seg(t, 300, 520) if not red else 1 - seg(t, 300, 500)
        if not red:
            speed_lines(lay, tx, ty, 32, 70, 12, math.sin(math.pi * seg(t, 34, 240)), op=fd, seed=13, col=PINKCORE, wmax=2.0)
            shards(lay, tx, ty, seg(t, 50, 460), n=10, dist=66, size=8, seed=17, cols=(PINK, PINKCORE, (96, 100, 126)), op=1 - seg(t, 360, 460))
        burst(lay, tx, ty, 34, k * (1 - 0.25 * seg(t, 300, 520)), n=12, seed=21, core_col=PINKCORE, core_k=0.5, op=fd)


def kill_state(t, c):
    return 1.0 if c.reduce and t >= 200 else eio(seg(t, 160, 380))


RIC_GLINT = 24.0               # review 2.10: a block (ricochet) sits over every state change and under a kill: glint radius (was 15)
RIC_SPARKS = 14                # steel sparks (was 9)
RIC_GOLD_W = 5.2               # the gold streak's max half width (was 3.4)


def d_ricochet(lay, t, c):
    """steel: the shot meets an armour cap (L10 steel) and glances; no starburst, no HP lost"""
    tx, ty = TOK3['5']
    r_, a_ = polar(tx, ty)
    capc = ppx(r_ - 29, a_)          # the cap faces the tower
    red = c.reduce
    ring = []
    for rr in (31.0, 35.5):          # the latent armour cap (stand-in): a steel L10 double band on the token's tower side
        ring.append([(tx + rr * math.sin(math.radians(a_ + 180 + d)), ty - rr * math.cos(math.radians(a_ + 180 + d))) for d in range(-48, 49, 6)])
    lay.lines(ring, STEELHI, 2.2, key=1.2)
    p0 = GUN0[0]
    u = 1.0 if red else eout(seg(t, 0, 80))
    tracer(lay, p0, capc, u, op=1 - seg(t, 220, 380))
    if t >= 80 or red:
        tt = t - 80
        g = 1.0 if red else math.sin(math.pi * seg(tt, 0, 120))
        sparkle(lay, capc[0], capc[1], RIC_GLINT * g + 2, WHITE, op=1 - seg(tt, 160, 300) if not red else 1.0, rot=0.4)
        if not red:
            rng = np.random.RandomState(31)
            base_a = math.atan2(capc[1] - p0[1], capc[0] - p0[0])
            nrm = math.atan2(capc[1] - ty, capc[0] - tx)
            refl = 2 * nrm - base_a + math.pi
            uu = seg(tt, 0, 240)
            sp = []
            for i in range(RIC_SPARKS):
                a = refl + rng.uniform(-0.7, 0.7)
                d0 = 6 + 58 * eout(uu) * rng.uniform(0.6, 1.0)
                d1 = d0 - 12 * (1 - uu) - 3
                sp.append([(capc[0] + math.cos(a) * d1, capc[1] + math.sin(a) * d1), (capc[0] + math.cos(a) * d0, capc[1] + math.sin(a) * d0)])
            lay.lines(sp, STEELHI, 2.2, op=1 - seg(tt, 160, 300), key=0.8)


def d_ricochet_gold(lay, t, c):
    p0, p1 = GUN4
    red = c.reduce
    u = 1.0 if red else eout(seg(t, 0, 80))
    tracer(lay, p0, p1, u, op=1 - seg(t, 240, 420))
    if t >= 80 or red:
        tt = t - 80
        uu = 1.0 if red else eout(seg(tt, 0, 200))
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        end = (p1[0] + 78, p1[1] - 52)
        ctrl = (p1[0] + math.cos(ang) * 30, p1[1] + math.sin(ang) * 30)
        cur = bez(p1, ctrl, end, 24)
        part = partial(cur, uu)
        fd = 1 - seg(tt, 220, 380) if not red else 1.0
        if len(part) > 2:
            thin = 1 - 0.6 * seg(tt, 130, 280)
            lay.poly(ribbon(part, lambda k: (0.6 + RIC_GOLD_W * k * thin) if k < 0.85 else (0.6 + RIC_GOLD_W * 0.85 * thin) * (1 - k) / 0.15 + 0.3), fill=GOLD_HI + (255,), outline=INK, w=1.6, op=fd)
        g = 1.0 if red else math.sin(math.pi * seg(tt, 0, 120))
        lay.circle(p1[0], p1[1], 4 + 9 * g, fill=None, outline=GOLD_HI, w=2.4, op=fd * (0.9 if not red else 0.6))
        sparkle(lay, p1[0], p1[1], RIC_GLINT * 0.8 * g + 2, GOLD_HI, op=fd if not red else 0.8, rot=0.3)


FW_TOK = [TOK3['5']]


def d_firewall(lay, t, c):
    red = c.reduce
    for ring, t0 in ((0, 0), (1, 60), (2, 120)):
        r0, r1 = RING[ring]
        depth = 0.6 * (r1 - r0)
        rise = 1.0 if red else eout(seg(t, t0, t0 + 160))
        die = 0.0 if red else seg(t, 380, 600)
        hk = rise * (1 - 0.7 * die)
        op = 1 - die                              # fully gone at 600 ms (was 1 - 0.95 die: a 5 % flickering residue past the T2 cap)
        if hk <= 0.01 or op <= 0.0:
            continue
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
                for j in range(m + 1):
                    k = j / m
                    wk = ww * (1 - k) ** 0.8 * (1 + 0.25 * math.sin(math.pi * k))
                    pts.append(ppx(r0 + 1 + hh * k, ac - wk + lean * k * k / (r0 / 57.3)))
                for j in range(m, -1, -1):
                    k = j / m
                    wk = ww * (1 - k) ** 0.8 * (1 + 0.25 * math.sin(math.pi * k))
                    pts.append(ppx(r0 + 1 + hh * k, ac + wk + lean * k * k / (r0 / 57.3)))
                dst.append(pts)
        base_b = band(r0 + 1, r0 + 1 + depth * hk * 0.28, -28, 28, 30)
        lay.polys(tongues + [base_b], PINK + (255,), outline=INK, w=1.9, op=op)
        lay.polys(cores, (255, 158, 210, 255), op=op)
    for (x, y) in FW_TOK:                      # never over a unit token: the flames are cut clear of the disc
        lay.erase_circle(x, y, 31)
    if t >= 220 or red:
        for i in (0, 1):
            gone_tick(lay, PIPS3['5'][i])


# ======================================================================== C corp (review 2.10: state changes are the quietest family)
def c_scan(lay, ring, a0, a1, u, col, trail_deg=9.0, trail_op=0.0, w=1.6, op=1.0):
    """the FX-C scan line: one clean 1.6 px vector line in the skin enamel (1 px ink key) at the angle a0 + (a1 - a0) u across a ring cell,
    (trail_op > 0 adds a flat trail; the set uses none: no slab, no trail)"""
    if op <= 0 or u <= 0 or u >= 1:
        return
    r0, r1 = RING[ring]
    e = lerp(a0, a1, u)
    sg = 1 if a1 > a0 else -1
    tr0 = e - sg * trail_deg
    if (tr0 - a0) * sg < 0:
        tr0 = a0
    if abs(e - tr0) > 0.2:
        lay.poly(arc_pts(r1 - 1, tr0, e, 12) + arc_pts(r0 + 1, e, tr0, 12), fill=col + (255,), op=trail_op * op)
    lay.line([ppx(r1 - 1, e), ppx(r0 + 1, e)], col, w, op=op, key=1.0)


def c_mark_flash(lay, c, pre, post, region, t, t0, t1, col, op=0.55):
    """one flat 4-frame flash on the new mark only (the post-state's changed pixels), never on the whole cell"""
    if t0 <= t < t1:
        m = diff_mask(lay, c.skin, pre, post, region)
        lay.mask_op(m, col, op)


GROW_REGION = band(268, 331, -33, 33, 30)


def c_grow(lay, t, c):
    if c.reduce:
        return
    col = CORP_ENAMEL[c.skin][0]
    c_scan(lay, 1, -30.0, 30.0, eio(seg(t, 0, 133)), col)
    c_mark_flash(lay, c, 'p3', 'p3grow', GROW_REGION, t, 133, 200, col, op=0.40)


def grow_state(t, c):
    if c.reduce:
        return eio(seg(t, 0, 200))
    return 1.0 if t >= 133 else 0.0


WARD_REGION = band(326, 388, 92, 125, 20)


def _ward_loz():
    """the ward lozenge's centre on the rebuilt board: the centroid of what p3 adds over the unwarded p3alt inside WARD_REGION"""
    x0, y0, x1, y1 = 820, 520, 930, 640
    d = np.abs(base('neutral', 'p3')[y0:y1, x0:x1] - base('neutral', 'p3alt')[y0:y1, x0:x1]).max(axis=2) > 24
    m = poly_mask_full(WARD_REGION, (x0, y0, x1, y1), 0) > 0.5
    ys, xs = np.nonzero(d & m)
    return (x0 + float(xs.mean()), y0 + float(ys.mean())) if len(xs) else ppx(333, 93)


WARD_LOZ = _ward_loz()


def c_ward_on(lay, t, c):
    """the boss acts: one gold scan line across the warded unit's cell in the Adjuster's sector, then the lozenge (post-state) with one
    4-frame flash on the lozenge only and one thin gold ping.  The old Adjuster pulse, gold slab and the 180 deg gold flood are retired."""
    if c.reduce:
        return
    c_scan(lay, 2, 90.0, 150.0, eio(seg(t, 0, 133)), GOLD_HI)
    c_mark_flash(lay, c, 'p3alt', 'p3', WARD_REGION, t, 133, 200, GOLD_HI, op=0.5)
    if t >= 133:
        k = seg(t, 133, 360)
        lay.circle(WARD_LOZ[0], WARD_LOZ[1], 9 + 16 * eout(k), fill=None, outline=GOLD_HI, w=1.6 * (1 - k) + 0.5, op=0.9 * (1 - k))


def ward_state(t, c):
    if c.reduce:
        return eio(seg(t, 0, 200))
    return 1.0 if t >= 133 else 0.0


# ======================================================================== H harm
def h_hit_land(variant):
    def draw(lay, t, c):
        s = 3
        red = c.reduce
        ax = 60 * s
        reg = wedge(s, 118, 177)
        if t < 120:
            u = 1.0 if red else ein(seg(t, 0, 80))
            for i in range(3):
                r = lerp(232 + i * 11, 184 + i * 7, u)
                chev(lay, r, ax, op=1 - seg(t, 80, 120) if not red else 0.0)
        if not red and 80 <= t < 114:
            lay.line(wedge(s) + [wedge(s)[0]], HARM, 3.6, op=1.0, key=1.2)          # the wedge frame flashes HARM once (2 frames)
        front = lerp(177, 118, 1.0 if red else eout(seg(t, 80, 200)))
        dens = 0.8 if red else seg(t, 80, 130) * (1 - seg(t, 300, 560))
        x_flood(lay, reg, front, 177, dens, s=s, op=1.0)
        if not red:
            ku = seg(t, 100, 190)
            ko = 1 - seg(t, 260, 440)
            for i, (da, ln) in enumerate(((-16, 32), (2, 38), (17, 30))):
                krackle(lay, ppx(176, ax + da), ax + 180 + da * 1.2, ln, 50 + i, ku, ko)
        if variant == 'worm' and (t >= 140 or red):
            k = 1.0 if red else eback(seg(t, 140, 200))
            hx_, hy_ = ppx(185, ax - 14)
            s_ = 7 * k
            hook = [(hx_ - s_ * 0.2, hy_ - s_ * 1.2), (hx_ - s_ * 0.2, hy_ + s_ * 0.5), (hx_ + s_ * 0.2, hy_ + s_ * 0.95), (hx_ + s_ * 0.85, hy_ + s_ * 0.5), (hx_ + s_ * 0.9, hy_ + s_ * 0.05)]
            lay.line(hook, HARM, 3.0, key=1.6)
        if variant == 'adjuster' and not red:
            g = math.sin(math.pi * seg(t, 80, 170))
            lay.poly(band(178, 190, ax - 26, ax + 26, 20), fill=GOLD + (255,), outline=INK, w=1.4, op=g)
        if variant == 'adjuster' and red:
            lay.poly(band(178, 190, ax - 26, ax + 26, 20), fill=None, outline=GOLD, w=1.6, op=0.9)
        if t >= 200 or red:
            tower_pip_dark(lay, s, 1)
    return draw


PLATE = band(150, 188, 60 - 22, 60 + 22, 24)


def plate_draw(lay, dx=0.0, dy=0.0, op=1.0):
    """review 3.10: the FX-P block plate on its own stock (pink-tinted paper), with its torn fibre edge and the painted L10 double line"""
    P = [(x + dx, y + dy) for x, y in PLATE]
    lay.poly([(x + 3, y + 4) for x, y in P], fill=INK + (255,), op=op * 0.9)                  # hard shadow
    lay.poly(P, fill=P_STOCK + (255,), outline=INK, w=2.2, op=op)
    lay.line([(x + dx, y + dy) for x, y in arc_pts(185.5, 60 - 21, 60 + 21, 16)], P_STOCK_EDGE, 1.4, op=op)
    for rr in (156.0, 160.5):
        lay.line([(x + dx, y + dy) for x, y in arc_pts(rr, 60 - 19, 60 + 19, 16)], PINKD, 1.6, op=op)


def plate_shards():
    """the plate cut into 5 shards by jagged radial cuts"""
    cuts = [38, 47, 56, 65, 74, 82]
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
    if t < 120 and not red:
        u = eout(seg(t, 0, 90))
        for i in range(3):
            chev(lay, lerp(222 + i * 10, 196 + i * 7, u), ax - 8 + i * 8, op=1)
    dk = 1.0 if red else eio(seg(t, 160, 420))
    lay.poly(wedge(s), fill=INK + (255,), op=0.62 * dk)
    front = lerp(177, 118, 1.0 if red else eout(seg(t, 110, 260)))
    dens = 0.7 if red else seg(t, 110, 160) * (1 - seg(t, 320, 560))
    x_flood(lay, wedge(s, 118, 177), front, 177, dens, s=s)
    if t < 100 and not red:
        plate_draw(lay)
        cu = seg(t, 20, 90)
        lay.line(partial(jag(ppx(188, 52), ppx(150, 66), 6, 3, 2), cu), WHITE, 1.6, key=0.9)
    else:
        u = 0.55 if red else seg(t, 100, 460)
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
            op = 1 - (0 if red else seg(t, 320, 460))
            lay.poly([(x + 2, y + 3) for x, y in P], fill=INK + (255,), op=op * 0.85)
            lay.poly(P, fill=P_STOCK + (255,), outline=INK, w=1.8, op=op)
    if not red:
        ku = seg(t, 110, 210)
        ko = 1 - seg(t, 300, 500)
        for i, (da, ln) in enumerate(((-18, 34), (-2, 40), (15, 30))):
            krackle(lay, ppx(176, ax + da), ax + 180 + da, ln, 70 + i, ku, ko)
    if t >= 260 or red:
        tower_pip_dark(lay, s, 0)
        tower_pip_dark(lay, s, 1)


BLOCK_TINT = 0.0              # review 2.10: the block's pink wedge tint (was 0.45) is retired: a block sits under a kill and every hit
BLOCK_SPARKS = 10             # white sparks off the plate (was 16)
BLOCK_JOLT = 1.0              # px the plate jolts on impact (was 2.2)


def p_shield_block(lay, t, c):
    """P protect (for the block-vs-break sheet only): ONE intact plate on its own P stock, white sparks, flat pink wedge tint, no red"""
    s = 1
    red = c.reduce
    ax = 60 * s
    if t >= 80 or red:
        tl = Lay((lay.x0, lay.y0, lay.x1, lay.y1), lay.ss)
        tl.poly(wedge(s), fill=PINK + (255,))
        tl.erase_circle(*seat_xy(s), TOWER['seat'])
        lay.comp(tl.im, BLOCK_TINT * (1.0 if red else (seg(t, 80, 130) * (1 - seg(t, 300, 480)))))
    jolt = 0.0 if red else BLOCK_JOLT * math.sin(math.pi * seg(t, 80, 140))
    jx, jy = math.sin(math.radians(ax)) * -jolt, -math.cos(math.radians(ax)) * -jolt
    if t < 120 or red:
        u = 1.0 if red else eout(seg(t, 0, 80))
        for i in range(3):
            chev(lay, lerp(222 + i * 10, 194 + i * 9, u), ax - 8 + i * 8, op=1 - seg(t, 90, 120) if not red else 1.0)
    plate_draw(lay, jx, jy)
    if (80 <= t < 330) and not red:
        uu = seg(t, 80, 280)
        rng = np.random.RandomState(8)
        sp = []
        for i in range(BLOCK_SPARKS):
            a = math.radians(ax) + rng.uniform(-1.3, 1.3)
            cx, cy = ppx(190, ax + rng.uniform(-16, 16))
            d0 = 5 + 34 * eout(uu) * rng.uniform(0.6, 1.0)
            d1 = d0 - 14 * (1 - uu) - 5
            sp.append([(cx + math.sin(a) * d1, cy - math.cos(a) * d1), (cx + math.sin(a) * d0, cy - math.cos(a) * d0)])
        lay.lines(sp, WHITE, 2.0, op=1 - seg(t, 200, 330), key=1.0)
        sparkle(lay, *ppx(192, ax - 4), 11 * math.sin(math.pi * seg(t, 80, 220)) + 0.5, WHITE)


def h_slice_crack(lay, t, c):
    s = 4
    red = c.reduce
    ax = 60 * s
    if not red:
        dens = seg(t, 0, 50) * (1 - seg(t, 200, 420))
        x_flood(lay, wedge(s, 124, 177), 124, 177, dens, s=s)
        if 30 <= t < 64:
            lay.line(wedge(s) + [wedge(s)[0]], HARM, 3.2, op=1.0, key=1.2)          # one 2-frame HARM frame flash
    crk = jag(ppx(178, ax + 13), ppx(124, ax + 21.5), 7, 3.2, 12)
    br = jag(crk[4], ppx(150, ax + 7), 3, 2.0, 13)
    u = 1.0 if red else eout(seg(t, 50, 220))
    lay.lines([partial(crk, u)] + ([partial(br, seg(u, 0.6, 1.0))] if u > 0.6 else []), WHITE, 2.2, key=1.2)
    if not red and 50 <= t < 260:
        tip = partial(crk, u)[-1]
        sparkle(lay, tip[0], tip[1], 7, WHITE, op=1 - seg(t, 200, 260))
    if not red:
        ku = seg(t, 40, 140)
        ko = 1 - seg(t, 220, 400)
        for i, (da, ln) in enumerate(((-15, 28), (6, 32))):
            krackle(lay, ppx(176, ax + da), ax + 180 + da, ln, 90 + i, ku, ko)
    if t >= 180 or red:
        tower_pip_dark(lay, s, 1)


def h_slice_break(lay, t, c):
    s = 2
    red = c.reduce
    ax = 60 * s
    if not red:
        dens = seg(t, 0, 50) * (1 - seg(t, 160, 360))
        x_flood(lay, wedge(s, 118, 177), 118, 177, dens, s=s)
        if 30 <= t < 64:
            lay.line(wedge(s) + [wedge(s)[0]], HARM, 3.4, op=1.0, key=1.2)
    bk = 1.0 if red else eio(seg(t, 130, 400))
    lay.poly(wedge(s), fill=INK + (255,), op=0.72 * bk)
    hf = 1.0 if red else seg(t, 170, 450)
    if hf > 0:
        sx, sy = seat_xy(s)
        circ = [(sx + 36 * math.cos(i * math.pi / 18), sy + 36 * math.sin(i * math.pi / 18)) for i in range(36)]
        grid_X(lay, circ, lambda x, y: hf * (0.5 + 0.5 * clamp(1 - math.hypot(x - sx, y - sy) / 40)), pitch=5.0, col=(30, 26, 40), key=False, w=1.6)
    if t >= 100 or red:
        k = 1.0 if red else eback(seg(t, 100, 170), 2.2)
        cx, cy = ppx(158, ax + 15)
        S = 9 * k
        bar = 3.4 * k
        for sg in (1, -1):
            lay.line([(cx - S, cy - sg * S), (cx + S, cy + sg * S)], HARM, 2 * bar, key=1.6)
    if not red:
        ku = seg(t, 40, 140)
        ko = 1 - seg(t, 220, 400)
        for i, (da, ln) in enumerate(((-17, 30), (4, 34))):
            krackle(lay, ppx(176, ax + da), ax + 180 + da, ln, 110 + i, ku, ko)
    if t >= 220 or red:
        tower_pip_dark(lay, s, 0)
        tower_pip_dark(lay, s, 1)


# ---- hp_through: six diamonds from the landing arc to the YOU strip (crosses the HUD: allowed, review 1.6)
def you_segments():
    """the YOU strip's pending (hatched HARM) segments on the rebuilt HUD (p1 above layer): (cx, cy, w, h, y0, y1)"""
    a = above('neutral', 'p1')
    x0, x1, y0, y1 = 1080, 1420, 95, 150
    reg = a[y0:y1, x0:x1]
    red_ = (reg[:, :, 0] > 180) & (reg[:, :, 1] < 120) & (reg[:, :, 2] < 110) & (reg[:, :, 3] > 200)
    cols = red_.sum(0) > 3
    segs = []
    x = 0
    while x < len(cols):
        if cols[x]:
            xa = x
            while x < len(cols) and cols[x]:
                x += 1
            rows = np.where(red_[:, xa:x].any(1))[0]
            segs.append((x0 + xa, x0 + x - 1, y0 + rows.min(), y0 + rows.max()))
        x += 1
    return [((a_ + b_) / 2.0, (c_ + d_) / 2.0, (b_ - a_ + 1), (d_ - c_ + 1), c_, d_) for a_, b_, c_, d_ in segs if b_ - a_ > 6]


YOUSEG = None
HT_SRC = ppx(436, 47)
HT_CTRL = (1010, 130)
HT_FLIGHT = 300                  # ms per diamond; 20 ms stagger, so the last lands at 60 + 5 * 20 + 300 = 460
HT_DIAMOND = 10.5                # half-diagonal of a flying diamond (was 7.5): damage ranks first (review 2.10)
HT_SLAP = 0.60                   # the slap's opacity on the YOU strip (T2: 60 % local at most)


def h_hp_through_under(lay, t, c):
    return


def h_hp_through(lay, t, c):
    global YOUSEG
    if YOUSEG is None:
        YOUSEG = you_segments()
    red = c.reduce
    segs = YOUSEG[-6:]
    n = len(segs)
    lead = None
    paths = []
    for i, (sx, sy, sw, sh, sy0, sy1) in enumerate(segs):
        t0 = 60 + i * 20
        u = 1.0 if red else eio(seg(t, t0, t0 + HT_FLIGHT))
        lift = 0 if red else eout(seg(t, i * 12, i * 12 + 80))
        p0 = (HT_SRC[0] + (i - 2.5) * 7, HT_SRC[1] - 9 * lift)
        cur = bez(p0, HT_CTRL, (sx, sy), 60)
        paths.append((cur, u))
        if not red and i == 0 and 0 < u < 1:
            lead = (cur, u)
    if lead is not None:
        cur, u = lead
        a0 = max(0.0, u - 0.22)
        pts = [partial(cur, a0 + (u - a0) * k / 16)[-1] for k in range(17)]
        if math.dist(pts[0], pts[-1]) > 4:
            lay.poly(ribbon(pts, lambda k: 0.4 + 4.6 * k), fill=HARM + (255,), outline=INK, w=1.4, op=0.85)
    for cur, u in paths:
        if red or u >= 1.0:
            continue
        q = partial(cur, u)[-1]
        s_ = HT_DIAMOND
        lay.poly([(q[0], q[1] - s_), (q[0] + s_, q[1]), (q[0], q[1] + s_), (q[0] - s_, q[1])], fill=HARM + (255,), outline=INK, w=1.8)
    x0 = min(s[0] - s[2] / 2 for s in segs) - 3
    x1 = max(s[0] + s[2] / 2 for s in segs) + 3
    ya = min(s[4] for s in segs) - 13
    yb = max(s[5] for s in segs) + 13
    ta = 60 + (n - 1) * 20 + HT_FLIGHT
    if not red:
        sl = math.sin(math.pi * seg(t, ta - 60, ta + 60))
        if sl > 0:                    # one red slap on the taped strip
            lay.poly([(x0 - 18, ya + 2), (x1 + 18, ya), (x1 + 16, yb), (x0 - 16, yb + 2)], fill=HARM + (255,), outline=INK, w=1.6, op=HT_SLAP * sl)
    dk = 1.0 if red else seg(t, ta - 20, ta + 120)
    for (sx, sy, sw, sh, sy0, sy1) in segs:
        lay.poly([(sx - sw / 2, sy0), (sx + sw / 2, sy0), (sx + sw / 2, sy1), (sx - sw / 2, sy1)], fill=(26, 24, 34, 255), outline=INK, w=1.2, op=dk)


# ======================================================================== L life
REFUND_AT = (440.0, 762.0)      # the refund coin the wheel keeps at the Trigger kill (rebuilt p3)
RAM_SLOT = (1219.0, 613.0)      # the refunded RAM coin on the rebuilt HUD RAM row (p3)
RF_REGION = [(1196, 588), (1290, 588), (1290, 640), (1282, 640), (1282, 684), (1156, 684), (1156, 640), (1196, 640)]   # the RAM slot + the REFUND tab
RF_LAND = 400
RF_COIN_K = 1.0                 # the flying coin at the RAM coin's own size (was 1.5 x with a 22 px glow): gain ranks with state (review 2.10)


def ram_coin(lay, x, y, k, op=1.0):
    r = 12.5 * k
    lay.circle(x, y, r + 2.2, fill=INK + (255,), op=op)
    lay.circle(x, y, r, fill=CYAN + (255,), op=op)
    plus_sign(lay, x, y, 6.6 * k, INK, op=op, key=CYAN)


def l_refund_under(lay, t, c):
    return


def l_refund(lay, t, c):
    """crosses the HUD (allowed, review 1.6): the coin pops at the kill and flies one curve to the RAM row; the pre-state (base p3rf) shows the RAM
    slot empty and no REFUND tab until the coin lands"""
    red = c.reduce
    if red:
        if t < 300:
            ram_coin(lay, REFUND_AT[0], REFUND_AT[1], 1.0, op=1 - seg(t, 150, 300))
        return
    if t < RF_LAND:
        k = eback(seg(t, 0, 90), 2.0)
        u = eio(seg(t, 90, RF_LAND))
        cur = bez(REFUND_AT, (900, 560), RAM_SLOT, 60)
        q = partial(cur, u)[-1]
        a0_ = max(0.0, u - 0.15)
        pts = [partial(cur, a0_ + (u - a0_) * j / 16)[-1] for j in range(17)]
        if math.dist(pts[0], pts[-1]) > 4:
            lay.poly(ribbon(pts, lambda k_: 0.3 + 2.6 * k_), fill=CYAN + (255,), outline=INK, w=1.0, op=0.6)
        ram_coin(lay, q[0], q[1], k * RF_COIN_K)
    else:
        k = seg(t, RF_LAND, RF_LAND + 200)
        lay.circle(RAM_SLOT[0], RAM_SLOT[1], 14 + 12 * eout(k), fill=None, outline=CYAN, w=2.0 * (1 - k) + 0.4, op=1 - k)


def refund_state(t, c):
    if c.reduce:
        return 1.0
    return 1.0 if t >= RF_LAND else 0.0


CLR_R, CLR_A = 436.0, 70.0      # the check sits on Worm 3's landing arc (lane r 436, sectors 1-2)


def l_clear(lay, t, c):
    """review 2.10 (gain ranks with state, under every block): no wash along the arc (it swept 118 deg of the lane); the GAIN check stamps in
    once with a short glow that fades, two small sparkles.  The check stays (the still)."""
    red = c.reduce
    k = 1.0 if red else eback(seg(t, 0, 100), 2.0)
    if k > 0:
        cx, cy = ppx(CLR_R + 2, CLR_A)
        S = 16 * k
        chk = [(cx - S * 0.9, cy - S * 0.05), (cx - S * 0.25, cy + S * 0.6), (cx + S * 1.0, cy - S * 0.85)]
        if not red:
            lay.glow(lambda g: g.line(chk, GAIN, 7), blur=4, op=0.45 * (1 - seg(t, 100, 360)))
        lay.line(chk, GAIN, 5.6, key=2.0)
    if not red:
        for i, (da, dr, t0) in enumerate(((-9, -16, 100), (12, 14, 160))):
            g = math.sin(math.pi * seg(t, t0, t0 + 200))
            if g > 0:
                x, y = ppx(CLR_R + dr, CLR_A + da)
                sparkle(lay, x, y, 5 * g, (236, 255, 230))


def l_repair_mend(lay, t, c):
    s = 5
    red = c.reduce
    ax = 60 * s
    wd = wedge(s)
    fill_k = 1.0 if red else eio(seg(t, 260, 400))
    tower_pip_mend(lay, s, 1, fill_k)
    if red:
        sx, sy = seat_xy(s)
        for (dx, dy) in ((-22, -30), (24, -26)):
            plus_sign(lay, sx + dx, sy + dy, 6.5, MINT)
        return
    m = lay.poly_mask(wd)
    g = Lay((lay.x0, lay.y0, lay.x1, lay.y1), lay.ss)
    strokes = []
    for i in range(0, 6, 2):          # review 2.10: three strokes (was six) and a fainter glow; gain ranks with state
        a = ax - 20 + i * 8
        r = 100 + (i % 3) * 24
        x, y = ppx(r, a)
        t0 = i * 30
        u = seg(t, t0, t0 + 300)
        if u <= 0 or u >= 1:
            continue
        rise = 56 * eout(u)
        L = 32 + 10 * (i % 2)
        k = math.sin(math.pi * u)
        p = [(x + 2.5 * math.sin(j * 0.7 + i), y - rise + L * (1 - j / 9.0)) for j in range(10)]
        strokes.append((p, k))
    for p, k in strokes:
        rb = ribbon(p, lambda q: (0.5 + 6.0 * k * math.sin(math.pi * min(1.0, q * 1.15)) ** 0.7))
        g.poly(rb, fill=MINT + (255,), outline=INK, w=1.2)
    gl = g.im.copy()
    a = np.asarray(gl).copy()
    a[:, :, 3] = (a[:, :, 3] * m).astype(np.uint8)
    gl = Image.fromarray(a, 'RGBA')
    lay.comp(gl.filter(ImageFilter.GaussianBlur(4 * lay.ss)), 0.25 * (1 - seg(t, 380, 600)))
    lay.comp(gl, 1.0)
    for i, (dx, t0) in enumerate(((-24, 80), (26, 200))):
        u = seg(t, t0, t0 + 300)
        if 0 < u < 1:
            sx, sy = seat_xy(s)
            k = math.sin(math.pi * u)
            plus_sign(lay, sx + dx, sy - 8 - 48 * eout(u), 6.2 * k + 0.5, MINT, op=k)
    if 260 <= t < 520:
        x, y = ppx(167, (wedge_pip(s, 1)[0] + wedge_pip(s, 1)[1]) / 2)
        k = math.sin(math.pi * seg(t, 260, 520))
        sparkle(lay, x, y - 4, 8 * k, WHITE)


# ======================================================================== registry
def E(id, fam, title, box, pre, draw, keys, timing, iho, still, keep, reduce_note, skins=('neutral',), post=None, state=None, state_region=None,
      source='', scope='', variant_of=None, tier='core', kind='damage', draw_over=None, peak=2):
    assert timing['total'] <= T2_CAP_MS, (id, timing['total'])                       # review 2.11: the T2 cap, no override
    assert all(v[1] <= T2_CAP_MS for v in timing['phases'].values()), id
    assert keys[-1][0] <= T2_CAP_MS, id
    return dict(id=id, fam=fam, title=title, box=box, pre=pre, post=post, state=state, state_region=state_region, draw=draw, keys=keys,
                timing=timing, iho=iho, still=still, keep=keep, reduce_note=reduce_note, skins=skins, dur=timing['total'], source=source,
                scope=scope, variant_of=variant_of, tier=tier, kind=kind, draw_over=draw_over, peak=peak)


def T(total, phases, easing):
    return dict(total=total, phases=phases, easing=easing)


SK3 = ('neutral', 'solace', 'meridian')
FX = []
# ---- C corp (kind 'state': the quietest)
FX.append(E('fx_grow', 'C', 'A unit grows one more hit', (360, 170, 715, 335), 'p3', c_grow,
            [(0, 'anticipate: two solid chevrons'), (70, 'scan line crosses the cell'), (150, 'flash on the new hollow chevron only'), (250, 'settle: hollow growth chevron'), (400, 'settled')],
            T(400, dict(scan=[0, 133], flash=[133, 200]), dict(scan='ease-in-out cubic', flash='step (4 frames, 40 % on the new mark)')),
            (133, 67, 0, 'in ease-in-out scan line; hold = 4-frame flash on the new chevron; no out (the chevron is the post-state)'),
            'One clean 1.6 px scan line in the corp\'s own enamel ink (neutral ENAMEL, Solace celadon, Meridian rust) crosses the unit cell, then one flat 4-frame flash on the new hollow growth chevron only. No slab, no whole-cell flash.',
            'one thin vector scan line, no texture, no slab; the only flash is on the new mark; the hollow chevron is the only state change.',
            'No scan or flash: the hollow chevron fades in over 200 ms (ease-in-out).', skins=SK3, post='p3grow', state=grow_state,
            state_region=GROW_REGION, source='f2 Packet 5 (ring +1, sector 0); post-state rendered with one more landing hit (land_hit = hit + 1), which the board draws as the hollow growth chevron', scope='cell-wide (a line)', tier='lower', kind='state', peak=2))
FX.append(E('fx_ward_on', 'C', 'Ward applies to units in the Adjuster sector', (690, 470, 918, 860), 'p3alt', c_ward_on,
            [(0, 'anticipate: unit not warded'), (70, 'gold scan line in the Adjuster sector'), (150, 'lozenge, 4-frame flash on it'), (260, 'one thin gold ping'), (400, 'settle: unit warded')],
            T(400, dict(scan=[0, 133], flash=[133, 200], ping=[133, 360]), dict(scan='ease-in-out cubic', flash='step (4 frames, 50 % on the lozenge)', ping='ease-out cubic')),
            (133, 67, 160, 'in ease-in-out scan line; hold = 4-frame flash on the lozenge; out ease-out ping'),
            'One BOSS_GOLD scan line crosses the warded unit\'s cell inside the Adjuster\'s sector (60 deg, not the whole cell), the gold ward lozenge is there when it passes, with one 4-frame flash on the lozenge only and one thin gold ping.',
            'gold is the boss colour only; one thin line, one flash on the new lozenge, one thin ping; flat, no texture, no slab, no Adjuster pulse.',
            'No scan, flash or ping: the lozenge fades in over 200 ms.', skins=SK3, post='p3', state=ward_state,
            state_region=WARD_REGION, source='f2 Packet 6 (ring +2, warded) next to the Adjuster (ring +1, sector 2); pre-state rendered unwarded', scope='cell-wide (a line)', tier='lower', kind='state', peak=2))
# ---- D damage
FX.append(E('fx_gun_hit', 'D', 'Gun shot hits a unit', (250, 230, 600, 460), 'p3', d_gun_hit,
            [(0, 'anticipate'), (50, 'tracer paints'), (110, 'hit frame opens'), (180, 'peak: starburst, speed lines, shards'), (380, 'shards out, tick gone'), (600, 'settle: tick gone')],
            T(600, dict(tracer=[0, 80], burst=[80, 140], speed_lines=[80, 300], shards=[100, 420], tick=[140, 230], out=[300, 520]), dict(tracer='ease-out cubic', burst='ease-out back (overshoot)', speed_lines='sine in/out', shards='ease-out cubic', out='linear')),
            (140, 160, 220, 'in ease-out tracer + ease-out-back burst; out linear fade'),
            'A painted pink tracer from the BURST gun to the Worm\'s cell, a cell-sized comic hit frame (keylined pink starburst R 44 with a white core), 14 converging speed lines and flat shards; the struck HP tick flashes pink and goes to the gone socket.',
            'pink painted tracer, keylined pink starburst with a white core the size of the cell, speed lines converge on the star; the tick ends as a gone socket (no hatch after the hit).',
            'Tracer and burst appear at full size for 300 ms, then fade 200 ms; no speed lines, no shards; the tick goes gone on the same frame.', skins=SK3,
            source='f2 guns: sector 0 BURST, 2 shots hit Worm 2 (shot 1 shown)', scope='cell-wide', kind='damage', peak=3))
FX.append(E('fx_strike', 'D', 'Strike card hits for 2', (90, 280, 400, 580), 'p3', d_strike,
            [(0, 'anticipate'), (60, 'the slash crosses the cell'), (130, 'peak: big starburst, speed lines'), (300, 'two ticks gone'), (600, 'settle')],
            T(600, dict(slash=[0, 90], burst=[90, 150], speed_lines=[90, 300], shards=[100, 420], ticks=[150, 240], out=[340, 560]), dict(slash='ease-out cubic', burst='ease-out back', speed_lines='sine', shards='ease-out cubic', out='linear')),
            (150, 190, 220, 'in ease-out slash + ease-out-back burst; out linear'),
            'A bigger pink starburst (R 52) plus one painted slash with a white core; the two struck ticks flash pink and go to gone sockets.',
            'a bigger version of the gun hit frame plus one painted slash with a white core; pink ownership.',
            'Slash and burst shown full at once for 300 ms, fade 200 ms; no speed lines or shards.', skins=SK3,
            source='latent (Strike is not in this hand): Strike (2) on Packet 7, ring +2 sector 5', scope='cell-wide', kind='damage', peak=2))
FX.append(E('fx_trigger_hit', 'D', 'Trigger hits units along its path', (240, 600, 720, 900), 'p3', d_trigger_hit,
            [(0, 'anticipate: pencil route'), (100, 'pencil burns to paint'), (170, 'first hit frame (sector 3)'), (290, 'second hit frame (sector 4)'), (600, 'settle: painted marks')],
            T(600, dict(ignite=[0, 240], burst_s3=[120, 460], burst_s4=[240, 580], route_out=[420, 600]), dict(ignite='linear (front to back)', bursts='ease-out back', out='linear')),
            (240, 100, 260, 'in linear ignition front to back; bursts ease-out back; out linear'),
            'The yellow pencil route from the Payload ignites into pink paint front to back, and a hit frame (starburst R 40, speed lines, shards) pops at each struck cell in sector order (3 then 4); the hit marks end painted pink.',
            'pencil ignites into pink paint front to back; a hit frame per struck cell, in sector order, one at a time.',
            'Route shown painted at once; the two bursts appear together for 300 ms, no speed lines.', skins=SK3,
            source='f2 trigs: Trigger resolves Payload 4, its hits land on Packet 1 in sectors 3 and 4 (tlog trig_unit)', scope='cell-wide, one hit frame per struck cell', kind='damage', peak=3))
FX.append(E('fx_kill', 'D', 'A unit dies', (195, 240, 690, 575), 'p3', d_kill,
            [(0, 'anticipate: the dying cell (pink L7)'), (33, 'flare: 2 frames on the token'), (110, 'KO burst, speed lines'), (280, 'shards, cell empties'), (600, 'settle: empty cell')],
            T(600, dict(flare=[17, 50], burst=[34, 100], speed_lines=[34, 240], shards=[50, 460], empty=[160, 380], out=[300, 520]), dict(flare='step (2 frames, 55 % on the token)', burst='ease-out back', shards='ease-out cubic', empty='ease-in-out cubic', out='linear')),
            (100, 200, 300, 'in 2-frame step flare + ease-out-back burst; out linear, cell empties ease-in-out'),
            'One 2-frame flare on the token disc only (55 %), a KO starburst in the cause colour (CELL_PINK with a pink-tint core, no word) at the token, pink shards fly, and the cell is left empty.',
            'every kill mark in the cause colour (pink: our guns); one 2-frame flare on the TOKEN only; KO burst with NO word; shards; empty cell.',
            'No flare: a 30 % pink-tint disc holds on the token for 200 ms while the burst shows; the cell empties with a 220 ms fade.', skins=SK3, post='p3kill', state=kill_state,
            state_region=band(206, 279, 266, 394, 60), source='f2: Worm 2 dies to the sector 0 guns (fate dies); post-state rendered with Worm 2 and its shots removed (empty cell)', scope='cell-wide', kind='kill', peak=2))
FX.append(E('fx_ricochet', 'D', 'Shot glances off armour (steel)', (340, 190, 600, 380), 'p3', d_ricochet,
            [(0, 'anticipate: armour cap'), (50, 'tracer'), (110, 'tracer meets the cap, glint'), (210, 'sparks fan away'), (500, 'settle: HP unchanged')],
            T(500, dict(tracer=[0, 80], glint=[80, 200], sparks=[80, 380], out=[220, 380]), dict(tracer='ease-out cubic', glint='sine', sparks='ease-out cubic', out='linear')),
            (80, 120, 180, 'in ease-out tracer; glint sine; out linear'),
            'A tracer meets the steel armour cap; a white glint and steel sparks fan away. No starburst, no HP lost.',
            'NO starburst, NO HP lost: a white glint and steel sparks off the cap (steel = armour).',
            'Tracer and glint shown still for 300 ms; no sparks.', skins=SK3,
            source='latent (no armoured unit in E10): stand-in steel cap drawn on Packet 5', scope='cell-wide', kind='block', peak=2))
FX.append(E('fx_ricochet_gold', 'D', 'Shot weakened by the ward (gold)', (420, 730, 650, 945), 'p3', d_ricochet_gold,
            [(0, 'anticipate'), (50, 'tracer toward the ward'), (140, 'gold streak glances'), (280, 'streak at full length'), (500, 'settle: no HP lost')],
            T(500, dict(tracer=[0, 80], streak=[80, 280], ring=[80, 200], out=[240, 460]), dict(tracer='ease-out cubic', streak='ease-out cubic', out='linear')),
            (80, 160, 220, 'in ease-out tracer; streak ease-out; out linear'),
            'Same beat, gold: the streak (BOSS_GOLD highlight) curves off the ward; no starburst. In E10 the warded shots deal 0 (h 0), so no tick changes.',
            'as fx_ricochet, with the variant mark: a curved GOLD streak; gold = ward.',
            'Tracer and the full streak shown still for 300 ms.', skins=SK3, variant_of='fx_ricochet',
            source='f2 guns: sector 4 BURST, 2 shots warded by Packet 6 (result ward, h 0)', scope='cell-wide', kind='block', peak=2))
FX.append(E('fx_firewall_burn', 'D', 'Firewall burns a sector', (330, 110, 745, 365), 'p3', d_firewall,
            [(0, 'anticipate'), (70, 'flames catch in ring NOW'), (150, 'band steps out to ring +1'), (300, 'peak: a band per ring, 60 % deep'), (520, 'embers fade, ticks gone')],
            T(600, dict(ring0=[0, 160], ring1=[60, 220], ring2=[120, 280], ticks=[220, 220], embers=[380, 600]), dict(rise='ease-out cubic', flicker='sine 7 Hz on tongue height (no luminance swing)', embers='linear')),
            (280, 100, 220, 'in ease-out rise, 60 ms ring stagger; hold with a 7 Hz height flicker; out linear'),
            'In each ring cell of the column a low pink flame band rises from the inner edge to 60 % of the cell depth, inked, lighter pink core, no white; the band steps outward ring by ring; struck ticks go to gone sockets.',
            'a low PINK flame band per ring cell, 60 % of the cell depth, inked, no white cores; steps out ring by ring.',
            'All three bands appear at full height at once, no flicker, hold 300 ms, fade 200 ms.', skins=SK3,
            source='latent (Firewall is not in this hand): Firewall (2) on sector 0; Packet 5 loses its 2 ticks', scope='cell-wide, one band per ring', tier='lower', kind='damage', peak=3))
# ---- H harm (all damage)
FX.append(E('fx_hit_land', 'H', 'Landing hit, one slice pip lost', (405, 590, 670, 790), 'p1', h_hit_land(None),
            [(0, 'anticipate: chevrons land'), (97, 'impact: frame flashes HARM'), (170, 'flood rolls in, krackle'), (360, 'flood fades, pip gone'), (600, 'settle: pip gone')],
            T(600, dict(chevrons=[0, 80], frame_flash=[80, 114], flood=[80, 200], krackle=[100, 440], flood_out=[300, 560], pip=[200, 200]), dict(chevrons='ease-in cubic', frame_flash='step (2 frames)', flood='ease-out cubic', out='linear')),
            (200, 100, 260, 'in ease-in chevrons, 2-frame frame flash, ease-out flood; out linear'),
            'Three HOT chevrons slam in from the trim, the wedge frame flashes HARM once, a red X-halftone flood rolls in over the outer 60 % (the icon seat stays clear), black krackle with red misregistration at the rim; the hatched pip goes dark.',
            'flood over the outer part only, never on the icon seat; frame flashes HARM once; X-only dots (never round, so it never reads as the BURST Ben-Day).',
            'No chevron travel or krackle: the flood holds at 80 % density for 300 ms and fades; the pip goes dark on the same frame.',
            source='f1 Packet 1 lands on sector 3 SHIELD (3 hits, 1 pip through)', scope='slice-wide (outer part)', kind='damage', peak=2))
FX.append(E('fx_hit_land_worm', 'H', 'Hit-land variant: worm wear (hook mark)', (405, 590, 670, 790), 'p1', h_hit_land('worm'),
            [(0, 'anticipate'), (97, 'impact'), (170, 'flood and krackle, hook stamps'), (360, 'flood fades'), (600, 'settle: pip gone, hook stays')],
            T(600, dict(as_parent=[0, 600], hook=[140, 200]), dict(hook='ease-out back')),
            (200, 100, 260, 'as fx_hit_land; hook ease-out back'),
            'As fx_hit_land, then a red hook mark stamps on the rim and stays as the wear mark.', 'as fx_hit_land, plus the hook; the variant mark is the only change.',
            'As the parent; the hook appears without overshoot.', variant_of='fx_hit_land', source='f1 Worm 3 lands (wear flag); shown on sector 3', scope='slice-wide', kind='damage', peak=2))
FX.append(E('fx_hit_land_adjuster', 'H', 'Hit-land variant: Adjuster strike (gold rim flash)', (405, 590, 670, 790), 'p1', h_hit_land('adjuster'),
            [(0, 'anticipate'), (97, 'impact'), (125, 'gold rim flash'), (360, 'flood fades'), (600, 'settle')],
            T(600, dict(as_parent=[0, 600], gold_flash=[80, 170]), dict(gold_flash='sine, once')),
            (200, 100, 260, 'as fx_hit_land; one sine gold flash'),
            'As fx_hit_land plus ONE gold rim flash in BOSS_GOLD (gold = the boss).', 'as fx_hit_land, plus one gold rim flash; the variant mark is the only change.',
            'As the parent; the gold rim shows as a thin outline, no flash.', variant_of='fx_hit_land', source='latent: Adjuster strike (adj.strike false in E10)', scope='slice-wide', kind='damage', peak=2))
FX.append(E('fx_shield_break', 'H', 'Our shield slice breaks while blocking', (565, 320, 785, 560), 'p1', h_shield_break,
            [(0, 'anticipate: plate under load'), (60, 'hairline crack'), (150, 'plate splits, flood starts'), (300, 'shards fly, wedge darkens'), (600, 'settle: wedge dark, shield gone')],
            T(600, dict(load=[0, 90], crack=[20, 90], split=[100, 100], shards=[100, 460], flood=[110, 260], krackle=[110, 500], dark=[160, 420], pips=[260, 260]), dict(load='ease-out cubic', shards='ease-out cubic + gravity', flood='ease-out cubic', dark='ease-in-out cubic')),
            (160, 160, 280, 'in ease-out load + crack; shards ease-out + gravity; dark ease-in-out (stays)'),
            'The same P-stock plate as the block (pink-tinted paper, review 3.10), but in 5 shards flying out; a red X-halftone flood and black krackle behind it; the wedge ends dark and both pips go dark.',
            'the same plate (its own P stock) as the block, but in shards; red flood and krackle; wedge ENDS dark. Block and break are never alike in one frame.',
            'No shard flight or krackle: the plate shows split in place (shards offset 55 %) for 300 ms; flood at 70 %; the wedge darkens in one 300 ms fade.',
            source='f1 sector 1 SHIELD, hp 2 -> 0', scope='slice-wide', kind='damage', peak=2))
FX.append(E('fx_slice_crack', 'H', 'Slice goes 2 to 1 (cracked)', (335, 515, 525, 725), 'p1', h_slice_crack,
            [(0, 'anticipate'), (47, 'flood, frame flash'), (130, 'crack runs, white tip, krackle'), (230, 'crack done, pip gone'), (500, 'settle: cracked, one pip left')],
            T(500, dict(flood=[0, 420], frame_flash=[30, 64], crack=[50, 220], tip=[50, 260], krackle=[40, 400], pip=[180, 180]), dict(flood='linear', crack='ease-out cubic')),
            (220, 40, 240, 'in ease-out crack; flood linear'),
            'A red X flood over the outer part with one HARM frame flash, a jagged white crack from the rim beside the icon (never across it) that stays as the cracked mark, short krackle; one pip left.',
            'a jagged WHITE crack beside the icon, never across it, stays; one pip left.',
            'No flood pulse or tip spark: the crack draws in 150 ms linear.', source='f1 sector 4 BURST, hp 2 -> 1', scope='slice-wide', kind='damage', peak=2))
FX.append(E('fx_slice_break', 'H', 'Slice goes to 0, ability lost', (570, 515, 740, 710), 'p1', h_slice_break,
            [(0, 'anticipate'), (47, 'flood, frame flash'), (150, 'X stamps in the outer corner'), (300, 'black-out over a halftone fade'), (600, 'settle: dark wedge, X stays')],
            T(600, dict(flood=[0, 360], frame_flash=[30, 64], stamp=[100, 170], blackout=[130, 400], halftone=[170, 450], pips=[220, 220]), dict(stamp='ease-out back (strong)', blackout='ease-in-out cubic', halftone='linear')),
            (170, 230, 200, 'in ease-out-back stamp; black-out ease-in-out (stays)'),
            'Wedge black-out with a red stencil X in the outer corner (never on the icon); the icon fades out behind an ink X-halftone.',
            'black-out of the wedge, red stencil X in the OUTER corner only, halftone fade over the icon; the X stays.',
            'No flood or overshoot: black-out, X and halftone fade in together over 300 ms.', source='f1 sector 2 TURRET, hp 2 -> 0', scope='slice-wide', kind='damage', peak=2))
FX.append(E('fx_hp_through', 'H', 'HP gets through, diamonds fly to YOU', (700, 40, 1440, 330), 'p1', h_hp_through_under,
            [(0, 'anticipate'), (60, 'diamonds lift off the arc'), (260, 'flight on one curve, ribbon trail'), (460, 'arrival: the strip takes the slap'), (600, 'settle: segments dark')],
            T(600, dict(lift=[0, 140], flight=[60, 460], slap=[400, 520], dark=[440, 580]), dict(lift='ease-out cubic', flight='ease-in-out cubic, 20 ms stagger', slap='sine, once', dark='linear')),
            (160, 300, 140, 'in ease-out lift + ease-in-out flight, 20 ms stagger; hold = sine slap; out linear'),
            'Six red diamonds lift off the landing arc and ride ONE shared curve to their own YOU segments; the taped YOU strip takes one red slap; the six hatched segments go dark. One of the three effects allowed to cross the HUD.',
            'six diamonds ride ONE smooth curve, board and HUD in one frame; the YOU strip stays the taped player paper; red slap then dark.',
            'No flight: the six hatched segments go dark in a 200 ms fade, no slap.', source='f1 pv: through 6, HP 15 -> 9', scope='arc to HUD (crosses the HUD: allowed)',
            kind='damage', draw_over=h_hp_through, peak=2))
# ---- L life (kind 'gain', ranked with state)
FX.append(E('fx_refund', 'L', 'Trigger-kill refund, +1 RAM', (410, 480, 1300, 800), 'p3rf', l_refund_under,
            [(0, 'anticipate: RAM slot empty'), (70, 'coin pops with a plus'), (250, 'coin flies, ribbon trail'), (420, 'lands: RAM coin and REFUND tab'), (600, 'settle')],
            T(600, dict(pop=[0, 90], flight=[90, 400], light=[400, 600]), dict(pop='ease-out back (overshoot)', flight='ease-in-out cubic', light='ease-out cubic')),
            (90, 310, 200, 'in ease-out-back pop; hold = ease-in-out flight; out ease-out ring'),
            'A NET_CYAN RAM coin with a plus pops at the refund mark and flies one curve to the RAM row; the RAM coin and its REFUND tab appear when it lands, with a soft glow ring. One of the three effects allowed to cross the HUD.',
            'the RAM coin is NET_CYAN (the terminal) with a plus; it pops at the kill and flies to the RAM row on one curve.',
            'No flight: the coin fades at the refund mark (150 ms) and the RAM slot and tab show at once.', skins=SK3, post='p3', state=refund_state,
            state_region=RF_REGION, source='f2: Trigger kills Packet 1, refund 1 RAM (ram 3 + 1)', scope='cell to HUD (crosses the HUD: allowed)',
            kind='gain', draw_over=l_refund, peak=2))
FX.append(E('fx_clear', 'L', 'Nothing gets through (arc check)', (790, 175, 1010, 570), 'p3', l_clear,
            [(0, 'anticipate: the arc'), (50, 'check stamps in'), (130, 'check with its glow, sparkles'), (250, 'glow fades'), (400, 'settle: the check stays')],
            T(400, dict(check=[0, 100], glow=[100, 360], sparkles=[100, 360]), dict(check='ease-out back', glow='linear', sparkles='sine')),
            (100, 0, 260, 'in ease-out-back stamp; out linear glow'),
            'A painted GAIN check stamps in on the landing arc with a short soft glow and two small sparkles; the check stays. No wash along the arc.',
            'a GAIN green check on the arc; the one soft glow family; a still with a short stamp.',
            'No stamp, glow or sparkles: the check shows at once.', skins=SK3,
            source='f2: Worm 3 lands on sectors 1-2, soaked and braced, THROUGH 0', scope='arc', tier='still', kind='gain', peak=3))
FX.append(E('fx_repair_mend', 'L', 'Repair mends one pip', (330, 360, 510, 590), 'p3', l_repair_mend,
            [(0, 'anticipate: mend-pending pip'), (120, 'strokes rise through the wedge'), (240, 'peak: strokes, plus signs'), (380, 'pip lands'), (600, 'settle: pip restored')],
            T(600, dict(strokes=[0, 450], plus=[80, 560], pip_fill=[260, 400], glow_out=[380, 600]), dict(strokes='ease-out cubic rise, sine width', pip_fill='ease-in-out cubic')),
            (260, 140, 200, 'in ease-out rise, sine width; pip ease-in-out; out linear glow'),
            'Mint brush strokes with a soft glow rise through the green REPAIR wedge with plus signs; the mend-pending pip (GAIN outline) fills.',
            'rising strokes, plus signs, the pip fills; the only soft rising glow in the set. On the green REPAIR wedge the strokes are mint with an ink key (GAIN green would vanish on it).',
            'No strokes or glow: two static plus signs and the pip fills over 200 ms.',
            source='latent (REPAIR slice mend preview, sector 5); mend-pending pip drawn as a stand-in', scope='slice-wide', tier='lower', kind='gain', peak=2))

SHIELD_BLOCK = E('fx_shield_block', 'P', 'Our shield slice blocks (for the comparison only)', (565, 320, 785, 560), 'p1', p_shield_block,
                 [(0, 'anticipate'), (60, 'chevrons hit the plate'), (150, 'peak: white sparks off the plate'), (300, 'sparks out'), (500, 'settle: plate intact')],
                 T(500, dict(chevrons=[0, 80], jolt=[80, 140], sparks=[80, 330], tint=[80, 480]), dict(chevrons='ease-out cubic', sparks='ease-out cubic')),
                 (80, 220, 180, 'in ease-out chevrons; sparks ease-out; out linear'),
                 'ONE intact plate on its own P stock (pink-tinted paper #F6C8DE, review 3.10; not the card bone), chevrons stop and spark white, hard shadow, no red, no glow, no wedge tint.',
                 'intact plate on the P stock, painted L10 double line, white sparks, no red, hard shadow, no glow.', 'Plate still; no sparks or jolt.',
                 source='same sector as the break (sector 1) so the two read side by side', scope='slice-wide', kind='block', peak=2)
BYID = {f['id']: f for f in FX}
BYID['fx_shield_block'] = SHIELD_BLOCK
KIND_ORDER = ('damage', 'kill', 'block', 'state')        # review 2.10; 'gain' (L) is ranked with 'state'
