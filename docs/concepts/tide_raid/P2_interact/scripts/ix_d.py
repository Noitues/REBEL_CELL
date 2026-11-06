"""P1 sequence 6 (controller / keyboard).   python ix_d.py [name ...]"""
import sys, time
from ix_lib import *
from ix_lib import _brackets
from ix_b import cursor, tether, drag_card, socket, SHIFT_E, mk_match, draw_targets, slots, SLOT_C


def num_badge(cv, c, n, r=15, k=1.0, col=None):
    """a game-UI order badge: small hex chip with the order number."""
    col = WHITE * .92 if col is None else col
    bx = (c[0] - r - 6, c[1] - r - 6, c[0] + r + 6, c[1] + r + 6)
    o, e = Lyr(bx), Lyr(bx)
    o.poly(hy.hexpts(c, r + 3), 255)
    e.line(hy.hexpts(c, r) + [hy.hexpts(c, r)[0]], 2.4, 255)
    cv.overL(o, INK, .93 * k)
    cv.neonL(e, col, core=1.0 * k, g1=(2, .5 * k), g2=None)
    ui.ntext(cv, (c[0], c[1] + 1), str(n), int(r * 1.15), col, stroke=2, white=.2, k=k, glow=False)


def order_nodes(w):
    """focus order of the MAP zone: the three beam heads, then Sites by distance from the corp HQ along the threat
    (min arclength over every route that crosses them, ties by id), then HOME, the sealed locks, the hunter eye."""
    nodes = []
    for r in KN:
        R = w.routes[r]
        nodes.append(('head', r, tuple(PX(R['path']).at(R['ext'] + RUN[r])[0] + np.array([0, -34]))))
    dist = {}
    for sid, s in w.sites.items():
        if s['state'] == 'DOWN':
            continue
        vs = [w.visit(r, sid) for r in w.routes if sid in w.routes[r]['sites']]
        if vs:
            dist[sid] = min(vs)
    for sid in sorted(dist, key=lambda s: (dist[s], s)):
        B = w.sites[sid]['B']
        nodes.append(('site', sid, (B[0], B[1] - 92)))
    nodes.append(('home', 'home', (w.home[0], w.home[1] - 96)))
    for i, L in enumerate('ABC'):
        nodes.append(('lock', L, tuple(lock_pos(w, i))))
    cs = []
    for h in w.hunters:
        pt, _ = at(h['path'], plen(h['path']) * .72)
        cs.append(pt)
    nodes.append(('eye', 'eye', (np.mean([p[0] for p in cs]), min(p[1] for p in cs) - 120)))
    return nodes


def f_06a_focus_order():
    """THE FOCUS ORDER (map zone): beams (heads) -> Sites HQ-to-HOME -> HOME -> locks -> eye; the hand and the response discs
    are two more zones reached with LB/RB and LT. DOWN and off-line Sites are skipped; the order is deterministic (rule 7)."""
    w = World('default')
    cv = plan_base(w, grade=.5, ks={'K1': .7, 'K2': .7, 'K3': .7}, sealed_k=.45, lock_k=.8, hunter_k=.8, site_k={s: .6 for s in w.sites})
    nodes = order_nodes(w)
    # order path: a dotted spline with arrowheads between consecutive nodes
    for i in range(len(nodes) - 1):
        a, b = np.array(nodes[i][2], float), np.array(nodes[i + 1][2], float)
        mid = (a + b) / 2 + np.array([0, -26])
        pts = EB.bez(a, tuple(mid), b, 18)
        ly = Lyr(pbox(pts, 10), ss=2)
        ly.line(pts, 1.8, 255, dash=(3, 5))
        cv.over(INK, blur(ly.m, 2) * 1.6, .6, ly.off)
        cv.neonL(ly, WHITE * .8, core=.8, g1=None, g2=None)
        d = np.array(pts[-4]) - np.array(pts[-1])
        # arrowhead near the end, shortened by the badge radius
        u = (np.array(pts[-1]) - np.array(pts[-5]))
        u = u / (np.hypot(*u) + 1e-6)
        tip = np.array(pts[-1]) - u * 18
        n = np.array([-u[1], u[0]])
        ar = Lyr(pbox([tip], 14))
        ar.poly([tuple(tip), tuple(tip - u * 9 + n * 5), tuple(tip - u * 9 - n * 5)], 255)
        cv.neonL(ar, WHITE * .9, core=.9, g1=None, g2=None)
    for i, (kind, ident, p) in enumerate(nodes):
        num_badge(cv, p, i + 1, r=14 if kind != 'home' else 17, col=(WHITE * .92 if kind not in ('lock', 'eye') else FOGC * .4 + WHITE * .6))
    # skipped Sites: a hairline strike
    for sid in ('t1_a', 't1_d'):
        mk_none(cv, w.sites[sid]['B'], k=.9)
    hy.hud(cv, 44, 50, 80, 8, 0)
    cs = hand_custom(cv, ks={})
    for i, c in enumerate(cs):
        ly = Lyr((c[0] - 20, c[1] - 90, c[0] + 20, c[1] - 56))
        ly.text((c[0], c[1] - 76), chr(97 + i), 24, 255)
        cv.over(INK, blur(ly.m, 3) * 1.8, .8, ly.off)
        cv.neonL(ly, WHITE * .92, core=1.0, g1=(2, .4), g2=None)
    prompt_row(cv, (960, 850), [([('shoulder', 'LB'), ('shoulder', 'RB')], 'cycle'), ([('shoulder', 'LT'), ('shoulder', 'RT')], 'pick')], k=1.0)
    a = Ann()
    a.title('06a  CONTROLLER  ·  focus order', 'one deterministic walk: threat first, then the Sites it crosses, then HOME, then what is hidden')
    n_ = {n[1]: n for n in nodes}
    a.note('1-3  beam heads (the way to focus a beam)', (n_['K1'][2][0] + 120, n_['K1'][2][1] - 150), n_['K2'][2])
    a.note('4-11  Sites ordered by distance from the corp HQ\nalong the threat; ties by site id', (950, 210), n_['t3_core'][2])
    a.note('12  HOME', (w.home[0] + 160, w.home[1] - 190), n_['home'][2])
    a.note('13-15  sealed locks     16  hunter eye', (nodes[-4][2][0] - 220, nodes[-4][2][1] - 130), nodes[-3][2])
    a.note('DOWN and off-line Sites are skipped (nothing to do there)', (w.sites['t1_d']['B'][0] + 300, w.sites['t1_d']['B'][1] + 30), (w.sites['t1_d']['B'][0] + 36, w.sites['t1_d']['B'][1] - 8))
    a.note('a-e  the hand is its own zone: LB / RB cycle it, wrapping;\nwhile a card is carried they cycle the valid targets instead', (500, 880 - 70), (cs[0][0] - 20, cs[0][1] - 76))
    emit('06a_focus_order', cv, a)


def f_06b_snap():
    """CURSOR SNAPPING: the stick picks the next target inside a +-45 deg cone, scored distance x (1 + 2 x angle/45).
    Pushing east from t1_b: t2_breach is nearer but 24 deg off; t2_intel is farther but dead ahead and wins."""
    w = World('default')
    a_site, b_site, c_site = 't1_b', 't2_intel', 't2_breach'
    A = np.array(w.sites[a_site]['B'], float)
    Bp = np.array(w.sites[b_site]['B'], float)
    Cp = np.array(w.sites[c_site]['B'], float)
    cv = plan_base(w, grade=.5, ks={'K1': .7, 'K2': .7, 'K3': .7}, sealed_k=.45, lock_k=.6, hunter_k=.5, site_k={s: .6 for s in w.sites})
    # the cone
    ang = 0.0
    cone = Lyr(pbox([A, A + (520, -520), A + (520, 520)], 10), ss=1)
    pts = [tuple(A + np.array([0, -60]))] + [tuple(A + np.array([0, -60]) + 520 * np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])) for a in np.linspace(-45, 45, 30)]
    cone.poly(pts, 255)
    cv.add(WHITE, blur(cone.m, 6), .09, cone.off)
    ce = Lyr(pbox([A, A + (520, -520), A + (520, 520)], 10), ss=2)
    ce.line([pts[0], pts[1]], 1.6, 255, dash=(4, 6))
    ce.line([pts[0], pts[-1]], 1.6, 255, dash=(4, 6))
    cv.neonL(ce, WHITE * .8, core=.6, g1=None, g2=None)
    # candidate lines: thickness = preference
    for tgt, wd, kk in ((Cp, 1.8, .55), (Bp, 4.0, 1.0)):
        ly = Lyr(pbox([A, tgt], 20))
        ly.line([tuple(A + (0, -60)), tuple(tgt + (0, -92))], wd, 255)
        cv.over(INK, blur(ly.m, 2.5) * 1.8, .7 * kk, ly.off)
        cv.neonL(ly, WHITE * .92, core=.95 * kk, g1=(2, .4 * kk), g2=None)
    # old focus ghost (40% lime), new focus
    _brackets(cv, A + (0, 6), 88, .35)
    halo_site(cv, Bp)
    for sid, s in ((a_site, 'old'),):
        pass
    # candidate score pips
    for tgt, n in ((Cp, 2), (Bp, 1)):
        num_badge(cv, tgt + (60, -120), n, r=13)
    hy.hud(cv, 44, 50, 80, 8, 0)
    hand_custom(cv, ks={i: .6 for i in range(5)})
    prompt_row(cv, (960, 884), [(('stick', 'R'), 'cycle')], k=1.0)
    a = Ann()
    a.title('06b  CONTROLLER  ·  cursor snapping', 'stick = a direction, never a free pointer: it jumps to the best target in a cone')
    a.note('1  focus was here (ghost brackets, 35%)', (A[0] - 330, A[1] - 150), tuple(A + (0, 6)))
    a.note('2  +-45 deg cone from the stick direction', (A[0] + 330, A[1] + 220), tuple(A + (300, 160)))
    a.note('3  score = distance x (1 + 2 x angle / 45):\nt2_breach 140 px at 24 deg = 3.1   t2_intel 219 px at 0 deg = 2.2\nlowest wins; thick line = the winner', (A[0] + 620, A[1] - 330), tuple(Bp + (0, -92)))
    a.note('4  deadzone 0.35, 12 f repeat after the first press, never lands on a skipped Site', (A[0] + 520, A[1] + 320), None)
    emit('06b_cursor_snap', cv, a)


def f_06c_prompts():
    """BUTTON PROMPTS AS GLYPHS: a pill that follows the focus. Pad glyphs (a four-dot diamond with the pressed one filled,
    bumpers lit, stick arrows) + an action icon; the keyboard variant swaps only the glyphs. Carrying a card over a valid Site."""
    w = World('default')
    site = 't1_c'
    B = np.array(w.sites[site]['B'], float)
    P1 = PX(w.routes['K1']['path'])
    s_stop = w.visit('K1', site)
    cv = plan_base(w, grade=.5, ks={'K1': 1.0, 'K2': .5, 'K3': .5}, sealed_k=.5, lock_k=.5, hunter_k=.4, programs=SHIFT_E, ends={'K1': s_stop + 20}, heads=False,
                   site_k={s: .55 for s in w.sites})
    hy.dead_trail(cv, P1, s_stop + 40, P1.L - 4, k=.8)
    ui.firewall(cv, B, 'D', mode='ghost')
    stop = (B, P1, s_stop)
    old_ring(cv, B, 'SITES_LOST', r=46)
    pv_ring(cv, B, 'HOLDS', r=46)
    pv_block(cv, P1, s_stop - 2, 'HOLDS')
    halo_site(cv, B)
    pos = (B[0] + 470, B[1] + 230)
    cs = hand_custom(cv, skip=(0,))
    socket(cv, cs[0])
    hy.hud(cv, 44, 50, 80, 8, 0)
    slots(cv, SLOT_C, [('SHIFT', 'E'), None], k=.95)
    drag_card(cv, pos, 'D', sc=.9, ang=-4)
    # the pill: place / cancel / next target, anchored under the focused Site
    prompt_row(cv, (B[0] + 190, B[1] + 118), [(('face', 'S'), 'place'), (('face', 'E'), 'cancel'), ([('shoulder', 'LT'), ('shoulder', 'RT')], 'cycle')], k=1.0)
    # keyboard variant, same slot, lower
    prompt_row(cv, (B[0] + 190, B[1] + 200), [(('key', 'Enter'), 'place'), (('key', 'Esc'), 'cancel'), ([('key', 'Tab')], 'cycle')], k=.9)
    # mouse variant
    prompt_row(cv, (B[0] + 190, B[1] + 282), [(('mouse', 'L'), 'place'), (('mouse', 'R'), 'cancel')], k=.8)
    a = Ann()
    a.title('06c  PROMPTS AS GLYPHS', 'the pill follows the focus; pad, keyboard and mouse differ only in the glyph, the action icon is shared')
    a.note('1  pad: face button diamond, the pressed one filled\n(layout-neutral: no A/B/X/Y letters, works on any pad)', (B[0] + 700, B[1] + 40), (B[0] + 340, B[1] + 118))
    a.note('2  keyboard variant', (B[0] + 700, B[1] + 150), (B[0] + 340, B[1] + 200))
    a.note('3  mouse variant (left = place, right = cancel)', (B[0] + 700, B[1] + 330), (B[0] + 330, B[1] + 282))
    a.note('4  action icons: place = card into hex, cancel = x, cycle = < >', (B[0] - 180, B[1] + 380), (B[0] + 120, B[1] + 130))
    emit('06c_prompts', cv, a)


def wheel(cv, c, cards, sel, r=150, k=1.0):
    """the card wheel (LT held): the hand laid out on a ring, the selected sector lime; centre = the selected card big."""
    ring = Lyr((c[0] - r - 90, c[1] - r - 90, c[0] + r + 90, c[1] + r + 90))
    ring.ell(c, r + 74, v=255)
    ring.ell(c, r - 78, v=0)
    cv.overL(ring, INK, .78 * k)
    ed = Lyr((c[0] - r - 90, c[1] - r - 90, c[0] + r + 90, c[1] + r + 90))
    ed.ell(c, r + 74, v=255, outline=True, ow=2)
    ed.ell(c, r - 78, v=255, outline=True, ow=2)
    cv.neonL(ed, LATT_D, core=.8 * k, g1=(3, .4), g2=None)
    n = len(cards)
    for i, (verb, typ) in enumerate(cards):
        a = math.radians(-90 + i * 360 / n)
        p = (c[0] + r * math.cos(a), c[1] + r * math.sin(a))
        sp = Lyr((c[0] - r - 90, c[1] - r - 90, c[0] + r + 90, c[1] + r + 90))
        a0, a1 = -90 + i * 360 / n - 180 / n, -90 + i * 360 / n + 180 / n
        for rr_ in (r - 78, r + 74):
            pass
        sp.line([(c[0] + (r - 78) * math.cos(math.radians(a0)), c[1] + (r - 78) * math.sin(math.radians(a0))),
                 (c[0] + (r + 74) * math.cos(math.radians(a0)), c[1] + (r + 74) * math.sin(math.radians(a0)))], 1.6, 255)
        cv.neonL(sp, LATT_D, core=.5 * k, g1=None, g2=None)
        hy.vcard(cv, p, verb, typ, 0, lime=(i == sel), k=k * (1.0 if i == sel else .75), sc=.62 if i != sel else .72)
    verb, typ = cards[sel]
    ui.glyph_disc(cv, c, 58, TYPE_COL[typ], lambda l, c_, r_: g_type(l, typ, c_, r_), gscale=.62, k=k, ring_w=3)


def f_06d_radial():
    """RADIAL CARD WHEEL (hold LT / hold R): 5 sectors, right stick or mouse direction picks, release = pick up. The map behind
    shows the soft pre-drag preview of the highlighted card. Faster than cycling when the hand is full."""
    w = World('default')
    sel = 0
    cv = base_scene_soft(w, 'D')
    wheel(cv, (960, 700), HAND, sel)
    hy.hud(cv, 44, 50, 80, 8, 0)
    prompt_row(cv, (960, 928), [(('shoulder', 'LB'), 'wheel'), (('stick', 'R'), 'pick'), (('face', 'S'), 'pick')], k=1.0)
    a = Ann()
    a.title('06d  RADIAL  ·  hold LB / Q', 'a card wheel at the bottom third; the map previews the highlighted card softly')
    a.note('1  5 sectors in hand order, top = card a; the wheel clamps\nto the screen so it never covers HOME or the HQ', (500, 620), (800, 640))
    a.note('2  centre shows the type glyph big: the code is re-taught every pick', (1500, 800), (1010, 700))
    a.note('3  behind: D street lit, MATCH pads at 55% (the same preview as card hover)', (400, 330), (w.sites['t1_b']['B'][0], w.sites['t1_b']['B'][1] - 106))
    emit('06d_radial_wheel', cv, a)


def base_scene_soft(w, typ):
    R = w.routes['K1']
    P1 = PX(R['path'])
    hole = hole_path(P1.sub(R['ext'], P1.L, 6), 140)
    cv = plan_base(w, grade=.55, hole=hole, ks={'K1': 1.0, 'K2': .4, 'K3': .4}, sealed_k=.45, lock_k=.45, hunter_k=.35, home_k=.9,
                   site_k={s: (1.0 if s in ('t3_c', 't2_virus', 't1_c', 't1_b') else .4) for s in w.sites})
    for sid in ('t3_c', 't2_virus', 't1_c', 't1_b'):
        mk_match(cv, w.sites[sid]['B'], typ, k=.6, strong=False, r=40)
    return cv


def f_06e_shoulder():
    """SHOULDER CYCLE (LB / RB, Q / E): the lifted card walks along the hand, wrapping; each press previews the neighbour's
    type glyph above the prompt so the player sees what the next press gives."""
    w = World('default')
    sel = 1
    cv = base_scene_soft(w, 'N')
    hy.hud(cv, 44, 50, 80, 8, 0)
    cs = hand_custom(cv, lifts={sel: 44}, lime=sel, ks={i: .85 for i in range(5) if i != sel})
    # side prompts with next/prev type glyph
    for side, nb, btn in ((-1, 0, 'LB'), (1, 2, 'RB')):
        x = cs[sel][0] + side * 190
        y = cs[sel][1] - 150
        _pill(cv, x - 84, y - 32, x + 84, y + 32, k=1.0)
        draw_btn(cv, (x - side * 40, y), 'shoulder', btn, r=22)
        type_chip(cv, (x + side * 42, y), HAND[nb][1], 18)
    prompt_row(cv, (960, 862), [(('key', 'Q'), 'cycle'), (('key', 'E'), 'cycle'), (('key', '1-5'), 'pick')], k=.9)
    a = Ann()
    a.title('06e  SHOULDER CYCLE  ·  LB / RB   Q / E', 'the quiet alternative to the wheel: one card at a time, wraps around')
    a.note('1  the selected card lifts 44 px and takes the lime halo', (cs[sel][0] - 480, cs[sel][1] - 290), (cs[sel][0] - 30, cs[sel][1] - 50))
    a.note('2  each side pill shows the type glyph of the card\nthat press would select', (cs[sel][0] + 520, cs[sel][1] - 250), (cs[sel][0] + 190, cs[sel][1] - 150))
    a.note('3  map previews the N street for the selected card (soft)', (500, 330), (w.sites['t2_breach']['B'][0], w.sites['t2_breach']['B'][1] - 106))
    emit('06e_shoulder_cycle', cv, a)


def _pill(cv, x0, y0, x1, y1, k=1.0, col=None):
    ui.crt_chip(cv, x0, y0, x1, y1, col=LATT_D if col is None else col, k=k, r=(y1 - y0) / 2)


if __name__ == '__main__':
    want = sys.argv[1:] or [k[2:] for k in list(globals()) if k.startswith('f_0')]
    for n in want:
        t = time.time()
        globals()['f_' + n]()
        print(n, round(time.time() - t, 1), 's')
