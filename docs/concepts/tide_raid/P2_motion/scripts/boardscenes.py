"""Board-mode renderers (1920x1080, neutral camera) for the beats that are not one of the six motion tests: card draw, drag, hunter, poster, lost.
The six tests also render here through scenes2 (mode='board')."""
from scenes2 import *
import scenes2 as S2

DECK = np.array([1700.0, 985.0])


def std_scene(f=0, beams=.85):
    S = Scene()
    S.std_rings(0.6)
    S.rest_beams(beams, flow_t=f)
    S.plum_list = [((1650.0, 470.0), 190.0)]
    S.plum_k = .4
    return S


def rgba_layer():
    return Image.new('RGBA', (W, H), (0, 0, 0, 0))


def lay_arr(im):
    return np.asarray(im, np.float32) / 255


def cursor(im, p, k=1.0):
    d = ImageDraw.Draw(im)
    pts = [(0, 0), (0, 26), (7, 20), (12, 31), (17, 29), (12, 18), (21, 18)]
    q = [(p[0] + x, p[1] + y) for x, y in pts]
    d.polygon(q, fill=HD.c8(PAL['INK'], k))
    q2 = [(p[0] + 3 + (x - 3) * .8, p[1] + 3 + (y - 3) * .8) for x, y in pts]
    d.polygon(q, outline=HD.c8(PAL['WARM'], k), fill=HD.c8(PAL['WARM'], k))
    d.polygon([(p[0] + 4, p[1] + 6), (p[0] + 4, p[1] + 20), (p[0] + 8, p[1] + 16), (p[0] + 14, p[1] + 17)], fill=HD.c8(PAL['INK'], k * .0))


def bez(p0, p1, p2, t):
    return (1 - t) ** 2 * np.asarray(p0) + 2 * (1 - t) * t * np.asarray(p1) + t * t * np.asarray(p2)


# ------------------------------------------------------------------ 02 card draw
def b_draw(f, reduce=False, mode='board'):
    S = std_scene(f)
    fr = S.render(f)
    five = HD.slots_default()
    four = []
    for i in range(4):
        tt = i - 1.5
        four.append(dict(x=W / 2 + tt * 108, y=1000 + abs(tt) ** 1.6 * 8, ang=-tt * 3.4, typ=five[i]['typ'], glyph=five[i]['glyph']))
    tgt = five[4]
    t_re = e('OUT_CUBIC', f, 2, 10)
    slots = [dict(a, x=lerp(a['x'], b['x'], t_re) if not reduce else b['x'], y=lerp(a['y'], b['y'], t_re), ang=lerp(a['ang'], b['ang'], t_re)) for a, b in zip(four, five[:4])]
    # deck stack (card backs) stays
    slots.append(dict(x=DECK[0], y=DECK[1], ang=0, typ='D', back=True, sc=.9))
    ring = rgba_layer()
    if f < 2:
        lift = 6 * e('OUT_QUAD', f, 0, 2)
        slots.append(dict(x=DECK[0], y=DECK[1] - lift, ang=0, typ=tgt['typ'], glyph=tgt['glyph'], back=True, sc=1.0))
    elif f < 16:
        t = e('OUT_CUBIC', f, 2, 12)
        p = bez(DECK, (1480, 760), (tgt['x'], tgt['y']), t)
        ang = lerp(0, tgt['ang'], t)
        sx = 1.0
        back = True
        if 6 <= f < 10:
            tt = prog(f, 6, 10)
            sx = abs(math.cos(math.pi * tt))
            back = tt < .5
        elif f >= 10:
            back = False
        sy = 1.0
        if f >= 12:
            sq = math.sin(math.pi * prog(f, 12, 16))
            sy = 1 - .06 * sq
            d = ImageDraw.Draw(ring)
            r_ = 40 + 50 * e('OUT_CUBIC', f, 12, 16)
            d.ellipse([tgt['x'] - r_, tgt['y'] + 50 - r_ * .5, tgt['x'] + r_, tgt['y'] + 50 + r_ * .5], outline=HD.c8(PAL['LATT'], 1 - prog(f, 12, 16)), width=3)
        slots.append(dict(x=p[0], y=p[1], ang=ang, typ=tgt['typ'], glyph=tgt['glyph'], back=back, sx=max(sx, .05), sc=1.0 * sy))
    else:
        slots.append(dict(tgt))
    huds = [HD.hud_chips(), HD.hand(slots), lay_arr(ring)]
    return assemble(fr, f, reduce, mode, None, huds)


# ------------------------------------------------------------------ 03 drag and drop
def lime_ring(fr, sid, k=1.0):
    c, _ = site(sid)
    ro, ri = 11.5, 10.2
    P = Pl(bbox_pts(ell(c, ro + 2), 10))
    P.poly(ell(c, ro + .8), PAL['INK'], .9)
    P.poly(ell(c, ro), PAL['LIME'])
    P.poly(ell(c, ri), PAL['INK'], .9)
    P.clear_poly(ell(c, ri - .8))
    fr.pl(P, gk=.9, k=k)


def grease_slash(fr, sid, k=1.0):
    c, _ = site(sid)
    red = hexc('FF2A3A')
    P = Pl(bbox_pts(ell(c, 13), 10))
    for col, wd in ((PAL['WARM'], 7.0), (red, 4.2)):
        P.line(ell(c, 10.5, 72, a0=0, a1=2 * math.pi), col, wd)
        P.line([gs(c, -7.4, 7.4 * .0 + 7.4 * 0), gs(c, 7.4, -7.4)] if False else [gs(c, -7.4, -7.4), gs(c, 7.4, 7.4)], col, wd)
    fr.pl(P, gk=.5, k=k)


def b_drag_core(f, valid, mode='board', reduce=False):
    sid = 't2_intel'
    S = std_scene(f)
    tgtc, _ = site(sid)
    hand0 = HD.slots_default()
    start = np.array([hand0[2]['x'], hand0[2]['y']])
    tp = np.array([tgtc[0], tgtc[1] - 30])
    # carried card position
    t_f = e('IN_OUT_QUAD', f, 3, 10)
    pos = start + (tp - start) * t_f
    sc = 1.0
    ang = hand0[2]['ang'] * (1 - e('OUT_BACK', f, 0, 3))
    if f < 3:
        sc = 1 + .12 * e('OUT_BACK', f, 0, 3)
        pos = start + np.array([0, -20 * e('OUT_BACK', f, 0, 3)])
    elif f < 14:
        sc = 1.12
    tilt = (-9 * math.tanh((t_f - e('IN_OUT_QUAD', f - 1, 3, 10)) * 80)) if 3 <= f < 11 else 0
    k_card = 1.0
    hov = e('OUT_CUBIC', f, 10, 16)
    fx = []
    if valid:
        if 14 <= f < 26:
            tt = e('OUT_CUBIC', f, 14, 26)
            sc = lerp(1.12, .25, tt)
            pos = tp + (tp + np.array([0, 40]) - tp) * tt
            k_card = 1 - e('LINEAR', f, 22, 26)
        if f >= 26:
            k_card = 0.0
        if f >= 10 and f < 26:
            S.fx.append(lambda fr, hov=hov: (lime_ring(fr, sid, k=hov),))
            S.fx.append(lambda fr, hov=hov: (wall_quad(fr, tgtc + np.array([0, 12]), np.array([.707, -.707]), 15, 15, 'D', k=.35 * hov, tint=PAL['LIME'], gk=.3),))
        if f >= 24:
            h = 15 * e('OUT_CUBIC', f, 24, 32)
            S.fx.append(lambda fr, h=h: wall_quad(fr, tgtc + np.array([0, 12]), np.array([.707, -.707]), max(h, .5), 15, 'D', k=.9, tint=PAL['CAGE'], gk=.6))
            tr = prog(f, 24, 30)
            S.fx.append(lambda fr, tr=tr: hex_ripple(fr, tgtc, 20 + 110 * e('OUT_CUBIC', tr, 0, 1), PAL['CAGE'], 1 - tr, w=3.5) if 0 < tr < 1 else None)
        if f >= 10:
            S.tags.append(dict(sid=sid, tier='HOLDS', k=hov if f < 26 else 1.0))
            S.tags = [t for t in S.tags if t['sid'] != sid or t.get('tier') == 'HOLDS']
        card_k = k_card
    else:
        if 14 <= f < 20:
            pos = pos + np.array([6 * math.sin((f - 14) / 6.0 * 3 * 2 * math.pi), 0])
        if f >= 20:
            tt = e('OUT_CUBIC', f, 20, 32)
            pos = tp + (start - tp) * tt
            sc = lerp(1.12, 1.0, tt)
        if f >= 10:
            gk_ = hov * (1 - e('LINEAR', f, 30, 38))
            S.fx.append(lambda fr, g=gk_: grease_slash(fr, sid, k=g))
        card_k = 1.0
    fr = S.render(f)
    slots = [dict(s) for s in hand0]
    if f >= 3 and not (not valid and f >= 32) and not (valid and f >= 26):
        slots = [s for i, s in enumerate(slots) if i != 2] if not (not valid and f >= 30) else slots
    carried = dict(x=pos[0], y=pos[1], ang=ang + tilt, typ=hand0[2]['typ'], glyph=hand0[2]['glyph'], sc=sc, k=card_k)
    if card_k > .01 and not (not valid and f >= 32):
        slots.append(carried)
    cur = rgba_layer()
    if f < 26 or not valid:
        cursor(cur, (pos[0] + 8, pos[1] - 6), 1.0 if f < 32 else 0.0)
    return assemble(fr, f, reduce, mode, None, [HD.hud_chips(), HD.hand(slots), lay_arr(cur)])


def b_dragv(f, reduce=False, mode='board'):
    return b_drag_core(f, True, mode, reduce)


def b_dragi(f, reduce=False, mode='board'):
    return b_drag_core(f, False, mode, reduce)


# ------------------------------------------------------------------ 06 hunter
_H = {}


def hunter_routes():
    if not _H:
        for i, h in enumerate(world().hunters):
            _H[i] = Route('H%d' % i, path=h['path'], typ='E')
    return _H


def eye_icon(P, c, open_=0.0, look=0.0, col=None, r=34):
    col = PAL['WHITE'] if col is None else col
    oy = r * (.30 + .30 * open_)
    top = [(c[0] + x * r, c[1] - oy * math.cos(x * math.pi / 2) * 1.0) for x in np.linspace(-1, 1, 20)]
    bot = [(c[0] + x * r, c[1] + oy * math.cos(x * math.pi / 2) * 1.0) for x in np.linspace(1, -1, 20)]
    P.poly(top + bot, PAL['INK'], .9)
    P.line(top + bot + [top[0]], col, 3.0)
    ip = (c[0] + look * r * .35, c[1])
    P.circle(ip, r * (.22 + .10 * open_), col)
    P.circle(ip, r * .10, PAL['INK'])


def reticle(P, c, scale, col, thump=0.0, a=1.0):
    r = 46 * scale * (1 - .14 * thump)
    L_ = 16 * scale
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        x, y = c[0] + sx * r, c[1] + sy * r * .72
        P.line([(x - sx * L_, y), (x, y), (x, y - sy * L_ * .72)], PAL['INK'], 6.5, a)
        P.line([(x - sx * L_, y), (x, y), (x, y - sy * L_ * .72)], col, 3.4, a)


def dashed(P, pts, col, wpx, a, dash=14, gap=10, s0=0.0, s1=None):
    pts = np.asarray(pts, float)
    seg = np.hypot(*np.diff(pts, axis=0).T)
    cs = np.concatenate([[0], np.cumsum(seg)])
    s1 = cs[-1] if s1 is None else s1
    s = s0
    while s < s1:
        e_ = min(s + dash, s1)
        ss = np.arange(s, e_ + 1, 4.0)
        q = [(np.interp(v, cs, pts[:, 0]), np.interp(v, cs, pts[:, 1])) for v in ss]
        if len(q) > 1:
            P.line(q, col, wpx, a)
        s += dash + gap


def b_hunter(f, reduce=False, mode='board'):
    HR = hunter_routes()
    S = std_scene(f, beams=.7)
    S.rings = [r for r in S.rings if r['sid'] != 't2_intel']
    R0, R1 = HR[0], HR[1]
    # known E beam K3 stays as in the plan
    scan = math.sin(2 * math.pi * f / 24.0) if f < 16 else 0
    openk = e('OUT_BACK', f, 12, 16)
    fire = e('LINEAR', f, 64, 76)
    dim1 = (e('OUT_CUBIC', f, 26, 34) if not reduce else e('LINEAR', f, 26, 34))
    fr = S.render(f)
    # candidate streets: white dashes
    P = Pl((0, 0, W, H), ss=1)
    dashed(P, R0.P[:: 3], PAL['WARM'], 5.0, .95 - .0, s0=(f * 1.3) % 24)
    dashed(P, R1.P[:: 3], PAL['WARM'], 4.0, .95 * (1 - .78 * dim1), s0=(f * 1.3) % 24)
    fr.pl(P, gk=.3)
    P = Pl((0, 0, W, H), ss=1)
    mid0 = R0.pos(R0.L * .5)
    mid1 = R1.pos(R1.L * .5)
    eye_c = (mid0 + mid1) / 2 + np.array([0, -150])
    eye_icon(P, eye_c, open_=openk, look=scan)
    # struck-out street: X
    if dim1 > 0:
        c = mid1
        P.line([(c[0] - 22, c[1] - 16), (c[0] + 22, c[1] + 16)], PAL['INK'], 8, dim1)
        P.line([(c[0] + 22, c[1] - 16), (c[0] - 22, c[1] + 16)], PAL['INK'], 8, dim1)
        P.line([(c[0] - 22, c[1] - 16), (c[0] + 22, c[1] + 16)], PAL['WARM'], 4, dim1)
        P.line([(c[0] + 22, c[1] - 16), (c[0] - 22, c[1] + 16)], PAL['WARM'], 4, dim1)
    # reticle
    if f >= 16:
        t = e('OUT_EXPO', f, 16, 24) if not reduce else e('LINEAR', f, 16, 22)
        sc = lerp(3.2, 1.0, t) if not reduce else 1.0
        th = math.sin(math.pi * prog(f, 24, 28)) if not reduce else 0
        reticle(P, mid0, sc, PAL['WHITE'], thump=th, a=min(1, t * 1.5))
    fr.pl(P, gk=.7)
    if 24 <= f < 25 and not reduce:
        flash(fr, mid0, 140, PAL['WHITE'], .5)
    # fire: white ram runs, road turns yellow behind it
    if f >= 64:
        s = R0.L * fire
        ribbon(fr, R0, 0, max(s, 1), gain=1.1, flow=f * .2)
        if not reduce:
            head(fr, 'E', R0.pos(max(s, 2)), R0.ang(max(s, 2)), alpha=1.0, halo=2.0)
            flash(fr, R0.pos(max(s, 2)), 70, PAL['WHITE'], .5)
    return assemble(fr, f, reduce, mode, None, S2.std_huds())


# ------------------------------------------------------------------ 09 poster slam (optional DAMAGED beat; wordless)
def b_poster(f, reduce=False, mode='board'):
    S = std_scene(f)
    S.home = dict(hp=38, preview=0, crack=1.0)
    fr = S.render(f)
    cx, cy = 930.0, 600.0
    # pixel-block dissolve of the patch under the poster
    diss = e('LINEAR', f, 0, 10)
    if 0 < diss < 1 and not reduce:
        rng = np.random.RandomState(5)
        cell = 22
        P = Pl((cx - 330, cy - 260, cx + 330, cy + 260), ss=1)
        for yy in range(int(cy - 250), int(cy + 250), cell):
            for xx in range(int(cx - 320), int(cx + 320), cell):
                v = rng.rand()
                if v < diss and v > diss - .45:
                    P.poly([(xx, yy), (xx + cell - 2, yy), (xx + cell - 2, yy + cell - 2), (xx, yy + cell - 2)], PAL['DAMAGED'], .85)
        fr.pl(P, gk=.4)
    # poster
    if f >= 8 or reduce:
        t = e('IN_CUBIC', f, 8, 12) if not reduce else 1.0
        scale = lerp(1.5, 1.0, t)
        jit = (0, 0, 0.0)
        if not reduce and f >= 12:
            tt = prog(f, 12, 18)
            jit = (5 * math.sin(tt * 9) * (1 - tt), 3 * math.cos(tt * 7) * (1 - tt), 2.0 * math.sin(tt * 8) * (1 - tt))
        k = e('LINEAR', f, 8, 11)
        if reduce:
            k = e('LINEAR', f, 6, 12)
        w_, h_ = 420 * scale, 520 * scale
        c = (cx + jit[0], cy + jit[1])
        P = Pl((c[0] - w_ * .7, c[1] - h_ * .7, c[0] + w_ * .7, c[1] + h_ * .7), ss=2)
        ang = math.radians(jit[2] - 2.5)
        def rp(pts):
            ca, sa = math.cos(ang), math.sin(ang)
            return [(c[0] + x * ca - y * sa, c[1] + x * sa + y * ca) for x, y in pts]
        sh = rp([(-w_ / 2 + 14, -h_ / 2 + 22), (w_ / 2 + 14, -h_ / 2 + 22), (w_ / 2 + 14, h_ / 2 + 22), (-w_ / 2 + 14, h_ / 2 + 22)])
        P.poly(sh, PAL['INK'], .5 / max(scale, 1))
        P.poly(rp([(-w_ / 2, -h_ / 2), (w_ / 2, -h_ / 2), (w_ / 2, h_ / 2), (-w_ / 2, h_ / 2)]), hexc('FBF8EC'))
        P.line(rp([(-w_ / 2, -h_ / 2), (w_ / 2, -h_ / 2), (w_ / 2, h_ / 2), (-w_ / 2, h_ / 2), (-w_ / 2, -h_ / 2)]), PAL['INK'], 4)
        # big hex + heart-break glyph (wordless: damage = the glyph)
        hx = [(math.cos(math.radians(60 * i + 30)) * 150 * scale, math.sin(math.radians(60 * i + 30)) * 150 * scale - 40 * scale) for i in range(6)]
        P.poly(rp([(x + 0, y) for x, y in hx]), PAL['INK'])
        hx2 = [(x * .92, (y + 40 * scale) * .92 - 40 * scale) for x, y in hx]
        P.poly(rp(hx2), PAL['DAMAGED'])
        gc = rp([(0, -40 * scale)])[0]
        glyph(P, 'DAMAGED', gc, 150 * scale, PAL['INK'], wpx=10 * scale)
        # tally strokes along the bottom (pencil)
        for i in range(6):
            x0 = -100 * scale + i * 40 * scale
            P.line(rp([(x0, 150 * scale), (x0 + 8 * scale, 215 * scale)]), PAL['INK'], 7 * scale)
        # tape corners
        for sx, sy in ((-1, -1), (1, -1)):
            P.poly(rp([(sx * w_ / 2 - 40 * sx, sy * h_ / 2 - 6), (sx * w_ / 2 + 26 * sx, sy * h_ / 2 + 30 * (-sy) * -1), (sx * w_ / 2 + 26 * sx, sy * h_ / 2 + 44), (sx * w_ / 2 - 40 * sx, sy * h_ / 2 + 8)]), PAL['WARM'], .75)
        fr.pl(P, gk=.3, k=k)
        if not reduce and 12 <= f < 17:
            tt = prog(f, 12, 17)
            hex_ripple(fr, np.array([cx, cy + 180]), 60 + 260 * e('OUT_EXPO', tt, 0, 1), PAL['WARM'], .6 * (1 - tt), w=3)
    return assemble(fr, f, reduce, mode, None, S2.std_huds(hp=38, hp_col=PAL['DAMAGED']))


# ------------------------------------------------------------------ 11 city lost
def skull(P, c, s, col, a=1.0):
    P.circle((c[0], c[1] - 10 * s), 44 * s, PAL['INK'], a)
    P.circle((c[0], c[1] - 10 * s), 40 * s, col, a)
    P.poly([(c[0] - 26 * s, c[1] + 14 * s), (c[0] + 26 * s, c[1] + 14 * s), (c[0] + 20 * s, c[1] + 52 * s), (c[0] - 20 * s, c[1] + 52 * s)], col, a)
    P.circle((c[0] - 15 * s, c[1] - 8 * s), 11 * s, PAL['INK'], a)
    P.circle((c[0] + 15 * s, c[1] - 8 * s), 11 * s, PAL['INK'], a)
    P.poly([(c[0], c[1] + 6 * s), (c[0] - 6 * s, c[1] + 18 * s), (c[0] + 6 * s, c[1] + 18 * s)], PAL['INK'], a)
    for i in range(-2, 3):
        P.line([(c[0] + i * 8 * s, c[1] + 32 * s), (c[0] + i * 8 * s, c[1] + 50 * s)], PAL['INK'], 3 * s, a)


def b_lost(f, reduce=False, mode='board'):
    S = std_scene(f, beams=.4)
    taken = ['t1_a', 't1_b', 't1_c', 't1_d', 't2_breach', 't2_virus', 't2_intel']
    S.rings = [dict(sid=s, tier='SITES_LOST') for s in ('t1_a', 't1_b', 't1_c', 't2_intel')]
    S.tags = [dict(sid=s, tier='SITES_LOST', pips=0) for s in ('t1_c', 't1_b')]
    for s in taken:
        if s in S.towers:
            S.towers[s]['hs'] = .35
            S.towers[s]['tint'] = PAL['PLUM_MID']
    S.home = dict(hp=0, preview=0, crack=1.0, ring_k=.6, pool_k=.3)
    S.blocks = []
    fr = S.render(f)
    fl = e('IN_OUT_QUAD', f, 8, 56) if not reduce else e('LINEAR', f, 44, 56)
    Rr = 40 + 1900 * fl
    cens = [(site(s)[0] + np.array([0, -10]), Rr * (.6 if s != 't1_a' else 1.0)) for s in taken] + [(home_c(), Rr * .8)]
    if reduce:
        cens = [(c, 1900 * .55) for c, _ in cens]
    fr.plum(cens, k=1.0, t=f, step_pulse=0.0, dim_lights=.9)
    img = fr.resolve()
    ds = e('IN_OUT_QUAD', f, 20, 44) if not reduce else e('LINEAR', f, 20, 44)
    lum = (img * LUM).sum(-1, keepdims=True)
    img = img * (1 - .55 * ds) + lum * .55 * ds
    if not reduce and 44 <= f < 50:
        rng = np.random.RandomState(f)
        for _ in range(9):
            y0 = rng.randint(0, H - 60); hh = rng.randint(8, 50); dx = rng.randint(-60, 60)
            img[y0:y0 + hh] = np.roll(img[y0:y0 + hh], dx, axis=1)
    if f >= 0:
        # last hit flash (reuse the HOME-hit language) in the first frames
        if f < 4 and not reduce:
            tmp = Frame(city=img)
            flash(tmp, home_c() + np.array([0, -16]), 250, PAL['WHITE'], [.95, .95, .5, .2][f])
            img = tmp.resolve()
    # skull
    if f >= 56:
        t = e('OUT_BACK', f, 56, 62) if not reduce else 1.0
        sc = lerp(1.6, 1.0, t)
        jit = (0, 0)
        if not reduce and f < 60:
            jit = ((-1) ** f * 4, (-1) ** (f // 2) * 3)
        k = 1.0 if not reduce else e('LINEAR', f, 56, 68)
        c = (960 + jit[0], 520 + jit[1])
        P = Pl((c[0] - 200, c[1] - 200, c[0] + 200, c[1] + 220))
        skull(P, c, 2.0 * sc, hexc('F2C6D8'))
        tr = e('OUT_CUBIC', f, 60, 70)
        if tr > 0:
            P.line(ell_px(c, 150, a1=2 * math.pi * tr), hexc('F2C6D8'), 6)
        tmp = Frame(city=img)
        tmp.pl(P, gk=.5, k=k)
        img = tmp.resolve()
    return assemble(img, f, reduce, mode, None, S2.std_huds(hp=0, hp_col=PAL['BREACHED']))


def ell_px(c, r, n=60, a1=2 * math.pi):
    return [(c[0] + r * math.cos(-math.pi / 2 + t), c[1] + r * .8 * math.sin(-math.pi / 2 + t)) for t in np.linspace(0, a1, n)]


# board renderers keyed like the spec
def board_renderers():
    return {
        'jackin': lambda f: S2.b_jack(f + S2.T_IN, mode='board'),
        'jackout': lambda f: S2.b_jack(f + S2.T_OUT, mode='board'),
        'draw': lambda f: b_draw(f),
        'dragv': lambda f: b_dragv(f),
        'dragi': lambda f: b_dragi(f),
        'daemon': lambda f: S1.b_daemon(f, mode='board'),
        'lock': lambda f: S2.b_lock(f, mode='board'),
        'hunter': lambda f: b_hunter(f),
        'shield': lambda f: S2.b_shield(f + S2.F_SH, mode='board'),
        'home': lambda f: S2.b_home(f, mode='board', f_imp=6),
        'poster': lambda f: b_poster(f),
        'bloom': lambda f: S2.b_bloom(f, mode='board'),
        'lost': lambda f: b_lost(f),
    }
