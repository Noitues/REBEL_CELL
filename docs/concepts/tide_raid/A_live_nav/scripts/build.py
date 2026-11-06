"""Build all Live Nav frames.  python build.py [frame ...]   (no args = all)"""
import sys, os, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene import *

FR = OUT + 'frames/'
os.makedirs(FR, exist_ok=True)
PIPS12 = [TIER['BREACHED']] + [TIER['DAMAGED']] * 3 + [TIER['SITES_LOST']] * 5 + [TIER['HOLDS']] * 3
MINT, TEAL, AMB, ORG, RED = (TIER[k] for k in ('UNTOUCHED', 'HOLDS', 'SITES_LOST', 'DAMAGED', 'BREACHED'))
CAND_PIPS = {'cand0': [ORG, AMB, AMB, TEAL], 'cand1': [AMB, AMB, TEAL, MINT], 'cand2': [AMB, TEAL, TEAL, MINT]}
HAND = [('GUARD', 'D', 'held', False), ('GUARD', 'D', 'held', False), ('SHIFT', 'E', 'held', False), ('GUARD', 'E', 'held', False),
        ('GUARD', 'N', 'held', False), ('JAM', 'N', 'held', False), ('INFECTED', None, 'held', True), ('INFECTED', None, 'held', True)]


def scale_sprite(a, f):
    im = Image.fromarray((a * 255).astype(np.uint8))
    im = im.resize((max(1, int(im.width * f)), max(1, int(im.height * f))), Image.LANCZOS)
    return np.asarray(im, np.float32) / 255


def bloom_centers(sc, taken, growth=None, tongues=True, r=122):
    growth = growth or {}
    cs = []
    for sid in taken:
        n = sc.nodes[sid]
        cs.append((n[0], n[1] + 4, r * growth.get(sid, 1.0)))
    if tongues:
        for a, b, pts in sc.links:
            for x, y in ((a, b), (b, a)):
                if x in taken and y not in taken and sc.sites.get(y, {}).get('infected_front'):
                    for t, rr in ((0.35, 46), (0.7, 30)):
                        p, _ = point_at(pts if a == x else pts[::-1], poly_len(pts) * t)
                        cs.append((p[0], p[1], rr * growth.get(x, 1.0)))
    return cs


def common(sc, taken=(), growth=None, bloom_strength=1.0, tr=90, tr_dim=1.0, seed=2, front=True, bscene='decay'):
    cv = Canvas(base_city(bscene))
    if taken:
        bloom(cv, bloom_centers(sc, taken, growth), seed=3, strength=bloom_strength, front=front)
    sc.draw_wires(cv)
    if tr:
        traffic(cv, sc.link_pts, seed=seed, n=tr, only_dim=tr_dim)
    return cv


def pos_on(sc, name, frac, lift=0):
    r = sc.rib[name]
    p, _ = point_at(r['pts'], r['len'] * frac)
    return p + np.array([0, lift])


def draw_ghost(cv, sc, names, alpha=.75, phase=0.0):
    for n in names:
        r = sc.rib[n]
        ribbon(cv, r['pts'], r['typ'], r['w'], fill=GHOST, alpha=alpha, phase=phase, casing=2.2)


def grease_arrow(cv, p0, p1, bend=40, col=GREASE_Y, w=6):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    mid = (p0 + p1) / 2 + np.array([0, -bend])
    ts = np.linspace(0, 1, 18)
    curve = [(1 - t) ** 2 * p0 + 2 * (1 - t) * t * mid + t * t * p1 for t in ts]
    x0, y0 = int(min(c[0] for c in curve) - 30), int(min(c[1] for c in curve) - 30)
    x1, y1 = int(max(c[0] for c in curve) + 30), int(max(c[1] for c in curve) + 30)
    d = D(x1 - x0, y1 - y0, 3)
    pts = [(c[0] - x0, c[1] - y0) for c in curve]
    d.line([(x + 1.5, y + 2) for x, y in pts], w + 3, INK, a=.85)
    d.line(pts, w, col)
    a = math.atan2(pts[-1][1] - pts[-3][1], pts[-1][0] - pts[-3][0])
    tip = np.array(pts[-1])
    head = [tip + 20 * np.array([math.cos(a), math.sin(a)]), tip + 12 * np.array([math.cos(a + 2.4), math.sin(a + 2.4)]),
            tip + 12 * np.array([math.cos(a - 2.4), math.sin(a - 2.4)])]
    d.poly([tuple(h) for h in head], col, INK, 2.2)
    cv.sprite(d.out(), x0, y0)


def route_list(cv, entries, x=28, bottom=1052, phase=0):
    """compact 'route alternatives' list: ribbon swatch + type glyph + order/letter + odds pips. no sentences."""
    n = len(entries)
    ch = 44
    y = bottom - n * (ch + 6)
    for i, e in enumerate(entries):
        yy = y + i * (ch + 6)

        def fn(d, e=e):
            crt_chip(d, 3, 3, 297, ch - 3, cut=7, border=hexc('5BE3FF') if e.get('known') else hexc('8A86B8'))
            if e.get('fork'):
                g_fork(d, 110, 22, 9, hexc('E8E4F5'))
            else:
                g_type(d, e['typ'], 110, 22, 9, TYPE_COL[e['typ']], INK, 1.6)
            d.text(140, 22, e['label'], sfont(24), PAPER)
            for k, c in enumerate(e.get('pips', [])):
                d.rr(176 + k * 17, 11, 176 + k * 17 + 13, 33, 2, c, INK, 1)
        cv.sprite(spr(300, ch, fn, 3), x, yy)
        if not e.get('fork'):
            pts = np.array([[x + 14, yy + 22], [x + 90, yy + 22]])
            ribbon(cv, pts, e['typ'], 12 if e.get('known') else 8, fill=None if e.get('known') else GHOST, casing=2.2, phase=phase, dash=(14, 9), chev=22)
        else:
            pass


def ordering_chip(cv, xy, n, typ):
    bubble(cv, xy, typ=typ, label=str(n), size=1.25)


def std_entries(forecast=False):
    return [dict(typ='E', label='1', known=True, pips=[]), dict(typ='D', label='2', known=True, pips=[]),
            dict(typ='E', label='A', pips=CAND_PIPS['cand0'] if forecast else []),
            dict(typ='N', label='B', pips=CAND_PIPS['cand1'] if forecast else []),
            dict(typ='D', label='C', pips=CAND_PIPS['cand2'] if forecast else []),
            dict(typ='N', label='', fork=True, pips=[])]


STATES0 = {'t1_a': 'TAKEN', 't1_b': 'TAKEN'}


# =================================================================== frames
def f_decay(sc):
    cv = common(sc, taken=['t1_a', 't1_b'], growth={'t1_a': 1.0, 't1_b': .62}, seed=11)
    # pins: t1_a stamped TAKEN; t1_b caught mid-flip with the decay clock almost full
    sc.draw_pins(cv, {'t1_a': 'TAKEN', 't1_b': 'DOWN'}, clocks={'t1_b': .94},
                 rings={'t1_a': RED})
    origin_pin(cv, sc.hq)
    home_pin(cv, sc.home)
    # two new INFECTED cards flying from the fallen sites to the deck strip (motion trail)
    tgt = np.array([1180, 52])
    for k, sid in enumerate(['t1_a', 't1_b']):
        p0 = sc.nodes[sid] + np.array([0, -60])
        for j, t in enumerate([.28 + k * .1, .5 + k * .1, .72 + k * .1]):
            p = p0 + (tgt - p0) * t + np.array([0, -90 * math.sin(math.pi * t)])
            sp = scale_sprite(sticker('INFECTED', None, infected=True, rot=-14 + k * 10), .62 - j * .06)
            sp = sp.copy()
            sp[..., 3] *= (.35 + j * .3)
            cv.sprite(sp, p[0] - sp.shape[1] / 2, p[1] - sp.shape[0] / 2)
    hud(cv, infected=3, healthy=8, flash_inf=True)
    return cv


def f_draw(sc):
    cv = common(sc, taken=['t1_a', 't1_b'], seed=12)
    # route preview: the two known routes are being drawn from the corp origin, scan head leading
    for n, prog in (('known0', .72), ('known1', .52)):
        r = sc.rib[n]
        L = r['len'] * prog
        ribbon(cv, r['pts'], r['typ'], r['w'], alpha=.28, phase=0)
        ribbon(cv, r['pts'], r['typ'], r['w'], smax=L, phase=10)
        p, ang = point_at(r['pts'], L)
        glow_dot(cv, p, 9, TYPE_COL[r['typ']] * .6 + .4, 1.4)
        glow_dot(cv, p, 5, np.array([1, 1, 1.]), 1.6)
    sc.draw_pins(cv, STATES0, rings={'t1_a': RED, 't1_b': RED})
    origin_pin(cv, sc.hq, pulse=.55)
    home_pin(cv, sc.home)
    hud(cv, infected=3, healthy=8)
    # hand dealt from the deck: cards fan in with a smear trail from the deck (left)
    n = len(HAND)
    x0 = (W - n * 124) / 2 + 150
    for i, c in enumerate(HAND):
        rot = (i - (n - 1) / 2) * 1.6
        sp = sticker(*c[:3][:2], state=c[2], rot=rot, infected=c[3])
        yy = 1075 - 150 + abs(i - (n - 1) / 2) * 4
        k = max(0, 3 - i) if i < 3 else 0
        for g in range(3, 0, -1):          # motion smear toward the deck
            if i >= 5:
                g2 = sp.copy()
                g2[..., 3] *= .13 * (4 - g)
                cv.sprite(g2, x0 + i * 124 - g * 26, yy - g * 10)
        cv.sprite(sp, x0 + i * 124, yy)
    return cv


def place_defenses(cv, sc, flashes=None):
    """Barriers stand ON the ribbon at the district's junction. D guard at t1_c sits on the E ribbon (mismatch: faded)."""
    flashes = flashes or {}
    p, _ = point_at(sc.rib['known0']['pts'], sc.s_at('known0', 't1_c'))
    barrier(cv, p + np.array([-6, 4]), 'D', 'GUARD', flash=flashes.get('t1_c', 0), dim=.62)
    q, _ = point_at(sc.rib['known1']['pts'], sc.s_at('known1', 't1_d'))
    barrier(cv, q + np.array([-6, 4]), 'D', 'GUARD', flash=flashes.get('t1_d', 0))


def f_plan(sc, hud_kw=None):
    cv = common(sc, taken=['t1_a', 't1_b'], seed=13)
    draw_ghost(cv, sc, ['cand0', 'cand1', 'cand2'], alpha=.8)
    draw_ghost(cv, sc, ['hunter0', 'hunter1'], alpha=.7)
    for n in ('known0', 'known1'):
        r = sc.rib[n]
        ribbon(cv, r['pts'], r['typ'], r['w'], phase=14)
    # drop targets: ghost rings on every district a known beam crosses (valid = white ring, focus = lime D25)
    elig = ['t3_b', 't2_breach', 't1_c', 't3_d', 't2_d', 't1_d']
    rings = {s: PAPER for s in elig}
    sc.draw_pins(cv, STATES0, rings=rings, focus='t2_d')
    place_defenses(cv, sc)
    origin_pin(cv, sc.hq)
    home_pin(cv, sc.home)
    for n, (fr, typ, lab) in {'known0': (.5, 'E', '1'), 'known1': (.36, 'D', '2'), 'cand0': (.30, 'E', 'A'), 'cand1': (.52, 'N', 'B'), 'cand2': (.72, 'D', 'C')}.items():
        bubble(cv, pos_on(sc, n, fr), typ=typ, label=lab, size=1.25)
    for n in ('hunter0', 'hunter1'):
        bubble(cv, pos_on(sc, n, .5), typ='N', glyph='fork', size=1.2)
    # dragged vinyl card with grease-pencil arrow to the focused district
    tgt = sc.nodes['t2_d'] + np.array([0, -30])
    cp = tgt + np.array([210, 190])
    grease_arrow(cv, cp + np.array([-30, -50]), tgt + np.array([14, 8]), bend=55)
    cv.sprite(sticker('GUARD', 'D', rot=7), cp[0] - 68, cp[1] - 85, shadow=.5, sh_off=(8, 14), sh_blur=8)
    hud(cv, heat_to=85, infected=3, healthy=8)
    # hand: two spent slots where the placed cards were
    cards = [('GUARD', 'D', 'spent', False), ('GUARD', 'D', 'spent', False)] + HAND[2:]
    hand(cv, cards, lift={})
    route_list(cv, std_entries(), phase=14)
    nav_button(cv, (1790, 960), glyph='eye')
    return cv


def forecast_bands(sc):
    s = sc.s_at
    k1 = [(s('known0', 't2_breach'), MINT), (s('known0', 't1_c'), AMB), (sc.rib['known0']['len'] + 5, ORG)]
    k2s = s('known1', 't1_d')
    k2 = [(k2s - 14, MINT), (k2s + 40, TEAL)]
    return k1, k2, k2s


def f_forecast(sc, panels=True):
    cv = common(sc, taken=['t1_a', 't1_b'], seed=14)
    draw_ghost(cv, sc, ['cand0', 'cand1', 'cand2'], alpha=.55)
    draw_ghost(cv, sc, ['hunter0', 'hunter1'], alpha=.6)
    k1, k2, k2s = forecast_bands(sc)
    r1, r2 = sc.rib['known0'], sc.rib['known1']
    ribbon(cv, r2['pts'], 'D', r2['w'], bands=k2, smax=k2s + 40, phase=6)
    ribbon(cv, r2['pts'], 'D', 6, fill=GHOST, smin=k2s + 40, alpha=.55, casing=2, dash=(6, 10))
    ribbon(cv, r1['pts'], 'E', r1['w'], bands=k1, phase=20)
    rings = {'t1_c': AMB, 't1_d': TEAL, 't1_a': RED, 't1_b': RED}
    sc.draw_pins(cv, STATES0, rings=rings)
    place_defenses(cv, sc)
    origin_pin(cv, sc.hq)
    home_pin(cv, sc.home, PIPS12)
    for n, (fr, typ, lab, pips) in {'known0': (.5, 'E', '1', [AMB, ORG]), 'known1': (.36, 'D', '2', [TEAL]),
                                    'cand0': (.30, 'E', 'A', CAND_PIPS['cand0']), 'cand1': (.52, 'N', 'B', CAND_PIPS['cand1']),
                                    'cand2': (.72, 'D', 'C', CAND_PIPS['cand2'])}.items():
        bubble(cv, pos_on(sc, n, fr), typ=typ, label=lab, pips=pips, size=1.25)
    for n in ('hunter0', 'hunter1'):
        bubble(cv, pos_on(sc, n, .5), typ='N', glyph='fork', size=1.2)
    hud(cv, heat_to=85, infected=3, healthy=8)
    if panels:
        cards = [('GUARD', 'D', 'spent', False), ('GUARD', 'D', 'spent', False)] + HAND[2:]
        hand(cv, cards)
        route_list(cv, std_entries(True), phase=20)
    nav_button(cv, (1790, 960), glyph='chev')
    return cv


def mode_chips(cv, sel=1):
    """DEPLOY / HOLD / MOVE / SACRIFICE as nav-mode chips"""
    names = ['DEPLOY', 'HOLD', 'MOVE', 'SACRIFICE']
    cw, ch = 168, 150
    x0 = (W - (4 * cw + 3 * 22)) / 2 + 150
    y = 1080 - ch - 26
    for i, nm in enumerate(names):
        def fn(d, i=i, nm=nm):
            crt_chip(d, 4, 4, cw - 4, ch - 4, cut=12, border=hexc('5BE3FF') if i != sel else PAPER)
            cx, cy = cw / 2, 62
            if nm == 'DEPLOY':        # drop onto the map: down arrow into a ground ring
                d.ell(cx, cy + 24, 30, 11, out=INK, ow=7)
                d.ell(cx, cy + 24, 30, 11, out=hexc('E8E4F5'), ow=3.5)
                d.line([(cx, cy - 26), (cx, cy + 10)], 11, INK)
                d.line([(cx, cy - 26), (cx, cy + 10)], 6, hexc('E8E4F5'))
                d.poly([(cx - 17, cy + 4), (cx + 17, cy + 4), (cx, cy + 24)], hexc('E8E4F5'), INK, 2)
            elif nm == 'HOLD':        # shield with pause bars
                g_shield(d, cx, cy, 30, hexc('19C9B4'))
                d.rr(cx - 11, cy - 14, cx - 4, cy + 12, 1, INK)
                d.rr(cx + 4, cy - 14, cx + 11, cy + 12, 1, INK)
            elif nm == 'MOVE':        # swap arrows
                for sgn in (1, -1):
                    yy = cy + sgn * 13
                    d.line([(cx - sgn * 28, yy), (cx + sgn * 20, yy)], 7, INK)
                    d.line([(cx - sgn * 28, yy), (cx + sgn * 20, yy)], 4, hexc('E8E4F5'))
                    d.poly([(cx + sgn * 32, yy), (cx + sgn * 16, yy - 11), (cx + sgn * 16, yy + 11)], hexc('E8E4F5'), INK, 1.6)
            else:                     # sacrifice: broken pin + flame
                g_pin_body(d, cx, cy + 34, 17, hexc('E8E4F5'))
                g_flame(d, cx, cy - 14, 20, TIER['DAMAGED'], INK)
                g_flame(d, cx, cy - 6, 9, hexc('FFE08A'), INK, .8)
            d.text(cw / 2, ch - 28, nm, sfont(22), PAPER)
        cv.sprite(spr(cw, ch, fn, 3), x0 + i * (cw + 22), y, shadow=.35)
        if i == sel:   # D25 focus halo, lime
            cx0 = x0 + i * (cw + 22)
            d = D(cw + 30, ch + 30, 3)
            d.rr(10, 10, cw + 20, ch + 20, 14, None, INK, 8)
            d.rr(10, 10, cw + 20, ch + 20, 14, None, LIME, 4.5)
            cv.sprite(d.out(), cx0 - 15, y - 15)


def f_response(sc):
    cv = common(sc, taken=['t1_a', 't1_b'], seed=15)
    draw_ghost(cv, sc, ['cand1', 'cand2'], alpha=.28)
    draw_ghost(cv, sc, ['hunter0', 'hunter1'], alpha=.35)
    for n in ('known0', 'known1', 'cand0'):
        r = sc.rib[n]
        ribbon(cv, r['pts'], r['typ'], r['w'] if n != 'cand0' else 11, phase=26)
    sc.draw_pins(cv, STATES0, rings={'t1_a': RED, 't1_b': RED})
    place_defenses(cv, sc)
    origin_pin(cv, sc.hq)
    home_pin(cv, sc.home)
    for n, (fr, typ, lab) in {'known0': (.5, 'E', '1'), 'known1': (.36, 'D', '2'), 'cand0': (.30, 'E', 'A')}.items():
        bubble(cv, pos_on(sc, n, fr), typ=typ, label=lab, size=1.25)
    bubble(cv, pos_on(sc, 'cand1', .52), typ='N', label='B', size=1.0, dim=.4)
    bubble(cv, pos_on(sc, 'cand2', .72), typ='D', label='C', size=1.0, dim=.4)
    hud(cv, heat_to=85, infected=3, healthy=8)
    mode_chips(cv, sel=1)
    return cv


def spent(cv, sc, names, alpha=.55):
    for n in names:
        r = sc.rib[n]
        ribbon(cv, r['pts'], r['typ'], 6, fill=GHOST, alpha=alpha, casing=2, halo=False)


def puck(cv, pts, s, typ):
    p, ang = point_at(pts, s)
    glow_dot(cv, p, 14, TYPE_COL[typ] * .7 + .3, 1.3)
    d = D(64, 64, 4)
    g_type(d, typ, 32, 32, 14, TYPE_COL[typ] if typ != 'E' else E_CHALK, INK, 3)
    d.ell(32, 32, 5, fill=INK)
    cv.sprite(d.out(), p[0] - 32, p[1] - 32 - 6, shadow=.4)


def road_closed(cv, p, col=TEAL):
    d = D(70, 70, 4)
    g_nogo(d, 35, 35, 21, col)
    cv.sprite(d.out(), p[0] - 35, p[1] - 35, shadow=.4)


def f_shield(sc):
    """K2 (DRONE) reaches the D guard at t1_d: hex shield flash, beam crumbles into bits, road closed."""
    cv = common(sc, taken=['t1_a', 't1_b'], seed=16, tr=70)
    spent(cv, sc, ['known0'])
    draw_ghost(cv, sc, ['cand0', 'cand1', 'cand2', 'hunter0', 'hunter1'], alpha=.22)
    r2 = sc.rib['known1']
    k2s = sc.s_at('known1', 't1_d')
    ribbon(cv, r2['pts'], 'D', r2['w'], alpha=.3, fill=GHOST, casing=2)
    ribbon(cv, r2['pts'], 'D', r2['w'] + 3, smax=k2s - 10, phase=8, bands=[(k2s, D_BLUE)])
    # bright comet just before the guard
    ribbon(cv, r2['pts'], 'D', r2['w'] + 3, smin=k2s - 140, smax=k2s - 10, fill=hexc('BFD8FF'), phase=8, halo=False)
    ribbon(cv, r2['pts'], 'D', 6, fill=GHOST, smin=k2s + 20, alpha=.5, casing=2, dash=(6, 10))
    sc.draw_pins(cv, {'t1_a': 'TAKEN', 't1_b': 'TAKEN', 't1_c': 'DOWN'}, rings={'t1_a': RED, 't1_b': RED})
    origin_pin(cv, sc.hq)
    home_pin(cv, sc.home)
    place_defenses(cv, sc, {'t1_d': .55})
    gp, _ = point_at(r2['pts'], k2s)
    bits_burst(cv, gp + np.array([-34, -30]), hexc('BFE9FF'), n=40, seed=4, spread=52)
    puck(cv, r2['pts'], k2s - 26, 'D')
    pe, _ = point_at(r2['pts'], k2s + 52)
    road_closed(cv, pe)
    bubble(cv, pos_on(sc, 'known1', .24), typ='D', label='2', size=1.25)
    def paint(t, cx, cy):
        pa = np.array([[cx - 230, cy + 150], [cx - 60, cy + 40]])
        ribbon(t, pa, 'D', 46, phase=6, casing=6, dash=(64, 30), halo=False)
        ribbon(t, pa, 'D', 46, smin=60, fill=hexc('DCEBFF'), phase=6, casing=0, dash=(64, 30), halo=False, glow=False)
        barrier(t, (cx + 20, cy + 110), 'D', 'GUARD', flash=1.0, scale=2.7)
        bits_burst(t, (cx - 28, cy + 8), hexc('CFEFFF'), n=34, seed=9, spread=80, size=26)
        pp = D(150, 150, 3)
        g_nogo(pp, 75, 75, 52, TEAL)
        t.sprite(pp.out(), cx + 40, cy - 135, shadow=.4)
    lens_scene(cv, gp + np.array([-10, -40]), (330, 290), paint, rdest=160)
    hud(cv, heat=85, infected=3, healthy=8)
    return cv


def f_home_hit(sc):
    """sealed A (ENFORCER) slips past the mismatched guard and arrives: destination alert pulse."""
    cv = common(sc, taken=['t1_a', 't1_b'], seed=17, tr=60)
    spent(cv, sc, ['known0', 'known1'])
    draw_ghost(cv, sc, ['cand1', 'cand2', 'hunter0', 'hunter1'], alpha=.2)
    r = sc.rib['cand0']
    ribbon(cv, r['pts'], 'E', 15, phase=4)
    ribbon(cv, r['pts'], 'E', 15, smin=r['len'] - 220, fill=hexc('FFE2C9'), phase=4, halo=False, alpha=.9)
    sc.draw_pins(cv, {'t1_a': 'TAKEN', 't1_b': 'TAKEN', 't1_c': 'DOWN'}, rings={'t1_a': RED, 't1_b': RED})
    origin_pin(cv, sc.hq)
    place_defenses(cv, sc)
    pe, _ = point_at(sc.rib['known1']['pts'], sc.s_at('known1', 't1_d') + 52)
    road_closed(cv, pe, hexc('19C9B4'))
    # arrival
    hp = sc.home
    cv.add(TIER['DAMAGED'], blur(disc_mask(hp[0], hp[1] - 40, 150), 22) * .9)
    home_pin(cv, hp, PIPS12, pulse=.42, pulse_col=TIER['DAMAGED'], shake=5, hit=True)
    bits_burst(cv, hp + np.array([4, -60]), hexc('FFC39A'), n=60, seed=8, spread=75, size=13)
    # floating damage number
    d = D(260, 150, 4)
    d.text(130, 78, '-4', sfont(124, 4, 800, 70), TIER['DAMAGED'], stroke=6)
    cv.sprite(d.out(), hp[0] + 30, hp[1] - 270)
    hud(cv, home=40, home_delta='-4', heat=85, infected=3, healthy=8, shake=4, home_col=TIER['DAMAGED'])
    puck(cv, r['pts'], r['len'] - 46, 'E')
    return cv


def verdict_tag(cv, xy, tier='DAMAGED', word='DAMAGED', rot=-5, scale=1.0):
    """corp paper tag with a rubber-stamped verdict word (the one allowed word)"""
    w, h = 340, 150
    col = TIER[tier]

    def fn(d):
        d.rr(14, 22, w - 14, h - 22, 10, INK, a=.35)
        d.rr(10, 16, w - 20, h - 28, 10, PAPER, INK, 3)
        d.ell(34, h / 2 - 6, 9, fill=hexc('3A3A5A'), out=INK, ow=2)           # punched hole
        d.line([(34, h / 2 - 6), (4, h / 2 - 24)], 3, hexc('3A3A5A'))
        # stamp
        d.rr(66, 36, w - 38, h - 48, 8, None, col, 5)
        d.text((66 + w - 38) / 2 + 40, h / 2 - 8, word, sfont(42, 4, 800, 70), col)
        # broken-heart glyph = DAMAGED
        hx, hy = 94, h / 2 - 8
        d.ell(hx - 9, hy - 5, 11, fill=col)
        d.ell(hx + 9, hy - 5, 11, fill=col)
        d.poly([(hx - 20, hy), (hx + 20, hy), (hx, hy + 26)], col)
        d.line([(hx + 2, hy - 18), (hx - 5, hy), (hx + 5, hy + 8), (hx - 2, hy + 24)], 3.2, PAPER)
    a = spr(w, h, fn, 3)
    im = Image.fromarray((a * 255).astype(np.uint8)).rotate(rot, Image.BICUBIC)
    if scale != 1:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255
    cv.sprite(a, xy[0] - a.shape[1] / 2, xy[1] - a.shape[0] / 2, shadow=.4, sh_off=(5, 9), sh_blur=6)


def f_aftermath(sc):
    cv = common(sc, taken=['t1_a', 't1_b'], growth={'t1_a': 1.15, 't1_b': 1.1}, seed=18, tr=70)
    spent(cv, sc, ['known0', 'known1', 'cand0'], alpha=.4)
    sc.draw_pins(cv, {'t1_a': 'TAKEN', 't1_b': 'TAKEN', 't1_c': 'DOWN'}, rings={'t1_a': RED, 't1_b': RED},
                 clocks={'t1_c': .22})
    origin_pin(cv, sc.hq)
    place_defenses(cv, sc)
    home_pin(cv, sc.home, None)
    hp = sc.home
    cv_ring(cv, hp, 74, 8, ORG, .9, flat=.55)
    verdict_tag(cv, (hp[0] + 400, hp[1] + 190), scale=1.45)
    hud(cv, home=40, heat=85, infected=3, healthy=8)
    return cv


def action_dock(cv, sel=0):
    """HQ step: Explore-nearby style action coins with prices; no sentences."""
    acts = [('PATCH', g_plus, 6), ('REPAIR', g_wrench, 10), ('CLEAN', None, 10), ('COOL', g_snow, 25), ('BUILD', None, 20)]
    cw, ch = 150, 140
    x0 = (W - (5 * cw + 4 * 18)) / 2 + 150
    y = 1080 - ch - 26
    for i, (nm, gf, price) in enumerate(acts):
        def fn(d, i=i, nm=nm, gf=gf, price=price):
            crt_chip(d, 4, 4, cw - 4, ch - 4, cut=12, border=hexc('5BE3FF') if i != sel else PAPER)
            cx, cy = cw / 2, 56
            if gf is not None:
                gf(d, cx, cy, 24, hexc('E8E4F5') if i != 0 else hexc('19C9B4'))
            elif nm == 'CLEAN':   # an INFECTED card being wiped
                d.rr(cx - 20, cy - 28, cx + 20, cy + 28, 5, PLUM, hexc('E8E4F5'), 2.4)
                g_x(d, cx, cy, 11, GREASE_R)
                d.arc(cx + 4, cy + 4, 34, 200, 330, 8, INK)
                d.arc(cx + 4, cy + 4, 34, 200, 330, 4, TIER['UNTOUCHED'])
            else:
                d.rr(cx - 22, cy - 6, cx + 22, cy + 24, 3, hexc('E8E4F5'), INK, 2)
                d.poly([(cx - 26, cy - 6), (cx, cy - 28), (cx + 26, cy - 6)], hexc('E8E4F5'), INK, 2)
                g_plus(d, cx, cy + 10, 7, INK)
            d.ell(cw - 28, 28, 0.1)
            d.text(cw / 2, ch - 22, '%d' % price, sfont(30), hexc('FFD24A'))
            d.rr(cw / 2 - 40, ch - 22 - 2, cw / 2 - 40, ch - 22, 0)
        cv.sprite(spr(cw, ch, fn, 3), x0 + i * (cw + 18), y, shadow=.35)
        if i == sel:
            cx0 = x0 + i * (cw + 18)
            d = D(cw + 30, ch + 30, 3)
            d.rr(10, 10, cw + 20, ch + 20, 14, None, INK, 8)
            d.rr(10, 10, cw + 20, ch + 20, 14, None, LIME, 4.5)
            cv.sprite(d.out(), cx0 - 15, y - 15)
    # done check
    nav_button(cv, (1780, 960), glyph='chev')


def f_hq_step(sc):
    cv = common(sc, taken=['t1_a', 't1_b'], growth={'t1_a': 1.15, 't1_b': 1.1}, seed=19, tr=80)
    sc.draw_pins(cv, {'t1_a': 'TAKEN', 't1_b': 'TAKEN', 't1_c': 'DOWN'}, rings={'t1_a': RED, 't1_b': RED, 't1_c': TEAL},
                 clocks={'t1_c': .22})
    origin_pin(cv, sc.hq)
    # selected action REPAIR: a teal route from HOME to the DOWN site, repair pin pulsing there
    hp, cp = sc.home, sc.nodes['t1_c']
    link = None
    for a, b, pts in sc.links:
        if {a, b} == {'home', 't1_c'}:
            link = pts if a == 'home' else pts[::-1]
    if link is not None:
        ribbon(cv, link, 'D', 11, fill=TEAL, phase=5, dash=(18, 10))
    home_pin(cv, hp, None)
    cv_ring(cv, cp, 56, 4, TEAL, .9, flat=.55)
    d = D(80, 80, 4)
    d.ell(40, 40, 24, fill=TEAL, out=INK, ow=3)
    g_wrench(d, 40, 40, 14, PAPER)
    cv.sprite(d.out(), cp[0] - 40 + 36, cp[1] - 40 - 80, shadow=.4)
    hud(cv, home=40, heat=85, infected=3, healthy=8)
    action_dock(cv, sel=1)
    return cv


def f_city_lost():
    sc = Scene('lost')
    taken = ['t1_a', 't1_b', 't1_c', 't1_d']
    # everything in reach is eaten: bloom engulfs the territory
    ids = [s for s in sc.sites if s in sc.nodes]
    cv = Canvas(base_city('lost' if False else 'default'))
    cs = []
    for sid in ids:
        n = sc.nodes[sid]
        cs.append((n[0], n[1] + 4, 150))
    for p in sc.link_pts:
        for t in (.3, .6, .9):
            q, _ = point_at(p, poly_len(p) * t)
            cs.append((q[0], q[1], 85))
    cs += [(sc.home[0], sc.home[1], 150), (sc.hq[0], sc.hq[1], 120)]
    bloom(cv, cs, seed=5, strength=1.0)
    sc.draw_wires(cv)
    # dying wire: darken
    cv.img *= 0.92
    states = {s: 'TAKEN' for s in sc.sites}
    for s_ in ('t2_breach', 't2_intel', 't2_virus', 't2_d', 't3_b', 't3_c', 't3_d', 't3_core'):
        states[s_] = 'TAKEN'
    sc.draw_pins(cv, states)
    origin_pin(cv, sc.hq)
    home_pin(cv, sc.home)
    # red HARM vignette
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = np.clip(np.sqrt(((xx - 960) / 1000) ** 2 + ((yy - 540) / 620) ** 2) - .35, 0, 1)
    cv.over(hexc('FF1830'), v ** 1.2 * .62)
    cv.img *= (1 - .18)
    # skull stamp
    sk = D(560, 560, 3)
    g_skull(sk, 280, 270, 215, PAPER, hexc('2A0A18'))
    a = sk.out()
    cv.over(INK, blur(a[..., 3], 18) * .7, (700 - 280 + 0, 360 - 270 + 12 - 0))
    cv.sprite(a, 960 - 280, 400 - 270 + 30)
    # stamped word on corp paper
    st = D(900, 170, 3)
    st.rr(10, 10, 890, 160, 12, PAPER, INK, 4)
    st.rr(26, 24, 874, 146, 8, None, RED, 8)
    st.text(450, 86, 'CITY LOST', sfont(104, 3, 800, 70), RED)
    im = Image.fromarray((st.out() * 255).astype(np.uint8)).rotate(-3, Image.BICUBIC)
    cv.sprite(np.asarray(im, np.float32) / 255, 510, 790, shadow=.5, sh_off=(6, 10), sh_blur=8)
    hud(cv, home=40, heat=85, infected=11, healthy=8, lost_at=8)
    return cv


FRAMES = {
    '01_decay': lambda: f_decay(Scene('decay')),
    '02_draw': lambda: f_draw(Scene('decay')),
    '03_plan': lambda: f_plan(Scene('decay')),
    '04_forecast': lambda: f_forecast(Scene('decay')),
    '05_response': lambda: f_response(Scene('decay')),
    '06a_playout_shield': lambda: f_shield(Scene('decay')),
    '06b_playout_home_hit': lambda: f_home_hit(Scene('decay')),
    '07_aftermath': lambda: f_aftermath(Scene('decay')),
    '08_hq_step': lambda: f_hq_step(Scene('decay')),
    '09_city_lost': f_city_lost,
    '10_forecast_ALL_PANELS_REMOVED': lambda: f_forecast(Scene('decay'), panels=False),
}

if __name__ == '__main__':
    want = sys.argv[1:] or list(FRAMES)
    for k in want:
        t = time.time()
        cv = FRAMES[k]()
        cv.save(FR + k + '.png')
        print(k, round(time.time() - t, 1), 's', flush=True)
