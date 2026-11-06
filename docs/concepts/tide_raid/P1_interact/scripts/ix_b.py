"""P1 sequence 2 (drag and drop) and 3 (what-if / forecast scrub).   python ix_b.py [name ...]"""
import sys, time
from ix_lib import *

SLOT_C = (1342, 986)
SHIFT_E = {'t2_intel': ('SHIFT', 'E')}
CARD_IDX = {'D': 0, 'N': 1}


def classify(w, typ, programs):
    """target class of every Site for a card of `typ`: occupied | none | match | maybe | dud (see NOTES 'type matching')."""
    known = {r: w.routes[r] for r in KN}
    sealed = {r: w.routes[r] for r in 'ABC'}
    out = {}
    for sid, s in w.sites.items():
        if sid in programs:
            out[sid] = ('occupied', None)
        elif s['state'] == 'DOWN':
            out[sid] = ('none', None)
        elif any(r['typ'] == typ and sid in r['sites'] for r in known.values()):
            out[sid] = ('match', typ)
        elif any(sid in r['sites'] for r in sealed.values()):
            out[sid] = ('maybe', None)
        elif any(sid in r['sites'] for r in known.values()):
            bt = [r['typ'] for r in known.values() if sid in r['sites']][0]
            out[sid] = ('dud', bt)
        else:
            out[sid] = ('none', None)
    return out


def draw_targets(cv, w, typ, programs, k=1.0, skip=(), labels=True):
    cl = classify(w, typ, programs)
    for sid, (c, bt) in cl.items():
        if sid in skip:
            continue
        B = w.sites[sid]['B']
        if c == 'match':
            mk_match(cv, B, typ, k=k)
        elif c == 'maybe':
            mk_maybe(cv, B, k=.85 * k)
        elif c == 'dud':
            mk_dud(cv, B, typ, bt, k=.8 * k)
        elif c == 'occupied':
            pad_ring(cv, B, GREY, r=44, k=.6 * k, fill=.0, w=2.6, dash=(8, 6))
    return cl


def cursor(cv, p, k=1.0):
    p = np.array(p, float)
    pts = [p, p + (0, 30), p + (8, 23), p + (14, 36), p + (20, 33), p + (14, 21), p + (25, 21)]
    ly = Lyr(pbox(pts, 10))
    ly.poly([tuple(x) for x in pts], 255)
    ol = Lyr(pbox(pts, 10))
    ol.line([tuple(x) for x in pts] + [tuple(pts[0])], 5, 255)
    cv.over(INK, np.maximum(ol.m, ly.m), .95 * k, ly.off)
    cv.over(WHITE, ly.m, 1.0 * k, ly.off)


def socket(cv, c, k=1.0, sc=.9, ang=0):
    """the empty hand slot a dragged card left behind: a dashed card outline."""
    w_, h_ = 104 * sc, 140 * sc
    ly = Lyr((c[0] - w_, c[1] - h_, c[0] + w_, c[1] + h_))
    ly.rr(c[0] - w_ / 2, c[1] - h_ / 2, c[0] + w_ / 2, c[1] + h_ / 2, 12, 255, outline=True, ow=2.4)
    m = ly.m
    # dash it by a stripe mask
    yy, xx = np.mgrid[0:m.shape[0], 0:m.shape[1]]
    m = m * (((xx + yy) // 7) % 2 == 0)
    cv.neon(m.astype(np.float32), LATT_D, core=.8 * k, g1=None, g2=None, off=ly.off)


def tether(cv, a, b, col=None, k=1.0, bend=-60):
    a = np.array(a, float); b = np.array(b, float)
    mid = (a + b) / 2 + np.array([0, bend])
    pts = EB.bez(a, tuple(mid), b)
    ly = Lyr(pbox(pts, 12))
    ly.line(pts, 2.4, 255, dash=(7, 6))
    cv.over(INK, blur(ly.m, 2.5) * 1.8, .7 * k, ly.off)
    cv.neonL(ly, WHITE * .9 if col is None else col, core=.95 * k, g1=(2, .35 * k), g2=None)
    return pts


def drag_card(cv, pos, typ, verb='GUARD', ang=-8, sc=1.08, k=1.0, echoes=()):
    for (p, kk) in echoes:
        hy.vcard(cv, p, verb, typ, ang, k=kk, sc=sc * .96)
    hy.vcard(cv, pos, verb, typ, ang, lime=True, k=k, sc=sc)


def base_scene(w, typ, programs, grade=.5, k_other=.5, extra_hole=None, ends=None, runs=None, route_hi=None, heads=True):
    """plan-state world for a drag: the matching beam lit, the rest quiet."""
    ks = {r: (1.0 if w.routes[r]['typ'] == typ else k_other) for r in KN}
    hole = None
    for r in KN:
        if ks[r] >= 1.0:
            P = PX(w.routes[r]['path'])
            h = hole_path(P.sub(w.routes[r]['ext'], P.L, 6), 140)
            hole = h if hole is None else np.maximum(hole, h)
    if extra_hole is not None:
        hole = np.maximum(hole, extra_hole) if hole is not None else extra_hole
    prog = dict(programs)
    cv = plan_base(w, grade=grade, hole=hole, ks=ks, sealed_k=.55, lock_k=.5, hunter_k=.4, home_k=.9, programs=prog, ends=ends, heads=heads, runs=runs)
    return cv


def hud_hand_slots(cv, w, hand_skip=(), lifts=None, filled=(None, None), ks=None, flash=False, hl=None):
    hy.hud(cv, 44, 50, 80, 8, 0)
    cs = hand_custom(cv, skip=hand_skip, lifts=lifts, ks=ks)
    slots(cv, SLOT_C, list(filled), k=.95, limit_flash=flash, hl=hl)
    return cs


def slot_card(cs, i):
    return cs[i]


# =============================================================== 02 drag and drop
def f_02a_pickup():
    """PICK UP: the card leaves the hand (a dashed socket stays), the ghost follows the pointer, and every legal Site lights
    by class. Only the D street is lit; sealed-only Sites get a fog '?' (their type is hidden); wrong-type Sites go grey."""
    w = World('default')
    cl_pos = (700, 735)
    cv = base_scene(w, 'D', SHIFT_E, grade=.52)
    draw_targets(cv, w, 'D', SHIFT_E)
    cs = hud_hand_slots(cv, w, hand_skip=(0,), filled=(('SHIFT', 'E'), None))
    socket(cv, cs[0])
    tether(cv, (cs[0][0], cs[0][1] - 60), (cl_pos[0] - 10, cl_pos[1] + 66), bend=40)
    drag_card(cv, cl_pos, 'D')
    cursor(cv, (cl_pos[0] - 20, cl_pos[1] - 36))
    a = Ann()
    a.title('02a  DRAG  ·  pick up', 'a D GUARD card: only places that can stop a D beam light up')
    a.note('1  ghost card: lime halo, lifted, tilted;\nits hand slot stays as a dashed socket', (cs[0][0] - 330, cs[0][1] - 130), to=(cs[0][0], cs[0][1] - 30))
    w_ = w.sites
    a.note('2  MATCH: D hue pad + dart = a known D beam crosses here', (360, 330), to=(w_['t1_b']['B'][0], w_['t1_b']['B'][1] - 106))
    a.note('3  "?" fog pad: only a sealed route crosses;\nits type is hidden, so it is never a promise', (1500, 380), to=(w_['t3_b']['B'][0], w_['t3_b']['B'][1] - 106))
    a.note('4  grey pad, D != E: legal but it stops nothing', (1150, 262), to=(w_['t3_core']['B'][0], w_['t3_core']['B'][1] - 106))
    a.note('5  occupied: dashed grey pad', (1030, 700), to=(w_['t2_intel']['B'][0], w_['t2_intel']['B'][1] + 6))
    a.note('6  guard slots: 1 of 2 used', (SLOT_C[0] + 10, SLOT_C[1] - 90), to=(SLOT_C[0] - 20, SLOT_C[1] - 30))
    emit('02a_drag_pickup', cv, a)


def stop_preview(cv, w, site, tier='HOLDS', typ='D', route='K1', old_tier='SITES_LOST', old_site='t1_c'):
    """the what-if carriers for a guard at `site` stopping `route`: new ring + block + tile (dashed), old ring + tile ghosts."""
    P = PX(w.routes[route]['path'])
    s = w.visit(route, site)
    B = w.sites[site]['B']
    ob = w.sites[old_site]['B']
    if site != old_site:
        old_ring(cv, ob, old_tier, r=40)
    else:
        old_ring(cv, ob, old_tier, r=46)
    pv_ring(cv, B, tier, r=46)
    pv_block(cv, P, s - 2, tier)
    return B, P, s


def f_02b_snap_target():
    """OVER A MATCH SITE: the card magnetises, the Site takes the lime brackets, a ghost program stands in the street and the
    carriers preview the new tier (dashed = not yet committed). Release here = place."""
    w = World('default')
    site = 't1_c'
    B = w.sites[site]['B']
    P1 = PX(w.routes['K1']['path'])
    s_stop = w.visit('K1', site)
    cv = base_scene(w, 'D', SHIFT_E, grade=.55, ends={'K1': s_stop + 20}, heads=False,
                    extra_hole=hole_disc(B, 320, 260))
    hy.dead_trail(cv, P1, s_stop + 40, P1.L - 4, k=.8)
    for sid in ('t3_c', 't2_virus', 't1_b'):
        mk_match(cv, w.sites[sid]['B'], 'D', k=.4, strong=False, r=40)
    ui.firewall(cv, B, 'D', mode='ghost', k=1.0)
    ui.firewall(cv, B, 'D', mode='up', k=.5)
    stop_preview(cv, w, site)
    tp = (B[0] - 6, B[1] - 190)
    hy.leader(cv, B + np.array([0, -62]), np.array(tp) + np.array([0, 28]), k=.8)
    old_tile(cv, (tp[0] - 70, tp[1]), 'SITES_LOST', r=22)
    arrow_chip(cv, (tp[0] - 46, tp[1]), (tp[0] - 34, tp[1]), k=.9, w=2.0, head=7)
    pv_tile(cv, tp, 'HOLDS', None, r=30)
    halo_site(cv, B)
    pos = (B[0] + 190, B[1] + 176)
    tether(cv, (pos[0] - 60, pos[1] - 60), (B[0] + 40, B[1] + 20), col=TYPE_COL['D'], bend=-40)
    hud_hand = hud_hand_slots(cv, w, hand_skip=(0,), filled=(('SHIFT', 'E'), None))
    socket(cv, hud_hand[0])
    drag_card(cv, pos, 'D', sc=.9, ang=-4)
    cursor(cv, (pos[0] - 14, pos[1] - 40))
    a = Ann()
    a.title('02b  DRAG  ·  over a valid Site', 'snap radius 90 px: the nearest legal Site wins; the card tilts toward it')
    a.note('1  lime brackets = this is the drop target', (B[0] - 360, B[1] - 40), to=(B[0] - 70, B[1] + 4))
    a.note('2  ghost wall in the type hue', (B[0] - 380, B[1] + 140), to=(B[0] + 34, B[1] - 14))
    a.note('3  carriers preview the new tier:\nring + block + tile, dashed outer line = not committed\nthe old amber ring and tile stay as ghosts', (B[0] + 400, B[1] - 250), to=(tp[0] + 30, tp[1] + 8))
    a.note('4  D beam now ends here; the rest of its\nroute is a dead dotted trail', (B[0] + 470, B[1] + 20), to=tuple(P1.at(s_stop + 120)[0]))
    emit('02b_drag_over_match', cv, a)


def f_02c_dud():
    """OVER A WRONG-TYPE SITE (soft invalid): legal but it stops nothing. The ghost wall goes grey, the pad shows
    [D glyph != E glyph], the card shakes (echoes), and no outcome preview appears: nothing would change."""
    w = World('default')
    site = 't3_core'
    B = w.sites[site]['B']
    cv = base_scene(w, 'D', SHIFT_E, grade=.58, extra_hole=hole_disc(B, 300, 240))
    for sid in ('t3_c', 't2_virus', 't1_c', 't1_b'):
        mk_match(cv, w.sites[sid]['B'], 'D', k=.35, strong=False, r=40)
    ui.firewall(cv, B, 'D', mode='ghost', k=.8)
    P3 = PX(w.routes['K3']['path'])
    mk_dud(cv, B, 'D', 'E', k=1.0)
    halo_site(cv, B, k=.8)
    pos = (B[0] + 230, B[1] + 190)
    cs = hud_hand_slots(cv, w, hand_skip=(0,), filled=(('SHIFT', 'E'), None))
    socket(cv, cs[0])
    tether(cv, (pos[0] - 60, pos[1] - 60), (B[0] + 40, B[1] + 20), col=GREY, bend=-40)
    drag_card(cv, pos, 'D', sc=.9, ang=-4, k=.85, echoes=[((pos[0] - 26, pos[1] + 4), .3), ((pos[0] + 26, pos[1] - 4), .3)])
    cursor(cv, (pos[0] - 14, pos[1] - 40))
    a = Ann()
    a.title('02c  DRAG  ·  wrong type (soft invalid)', 'legal, flagged: it can be dropped, but it will be a dud')
    a.note('1  reason, wordless: [card type] != [beam type]', (B[0] - 330, B[1] - 150), to=(B[0], B[1] - 106))
    a.note('2  no tier preview: the tally would not move', (B[0] + 420, B[1] - 130), to=(B[0] + 36, B[1] - 20))
    a.note('3  card jitters +-26 px (two echoes) instead of snapping', (pos[0] + 240, pos[1] + 70), to=(pos[0] + 28, pos[1]))
    emit('02c_drag_over_dud', cv, a)


def f_02d_occupied():
    """OVER AN OCCUPIED SITE (hard invalid): the red grease circle-slash sits on the standing program; the card does not
    tilt toward it and, on release, flies home (see 02f)."""
    w = World('default')
    site = 't2_intel'
    B = w.sites[site]['B']
    cv = base_scene(w, 'D', SHIFT_E, grade=.58, extra_hole=hole_disc(B, 300, 240))
    for sid in ('t3_c', 't2_virus', 't1_c', 't1_b'):
        mk_match(cv, w.sites[sid]['B'], 'D', k=.35, strong=False, r=40)
    halo_site(cv, B, k=.7)
    refuse(cv, (B[0] - 40, B[1] - 8), r=34)
    pos = (B[0] + 140, B[1] + 260)
    cs = hud_hand_slots(cv, w, hand_skip=(0,), filled=(('SHIFT', 'E'), None))
    socket(cv, cs[0])
    tether(cv, (pos[0] - 60, pos[1] - 60), (B[0] + 40, B[1] + 30), col=GREASE_R, bend=-40)
    drag_card(cv, pos, 'D', sc=.9, ang=-2, k=.8)
    cursor(cv, (pos[0] - 14, pos[1] - 40))
    a = Ann()
    a.title('02d  DRAG  ·  occupied (hard invalid)', 'the red grease circle-slash is the one refusal mark, everywhere')
    a.note('1  circle-slash on the standing program', (B[0] - 380, B[1] - 130), to=(B[0] - 40, B[1] - 12))
    a.note('2  tether goes red, no ghost wall, no preview', (B[0] + 400, B[1] + 90), to=(B[0] + 60, B[1] + 56))
    emit('02d_drag_over_occupied', cv, a)


def f_02e_snap():
    """SNAP: release over a match. The card becomes the program (wall solid, ring flash), the carriers commit (solid), the
    slot socket fills, the hand re-fans over the gap. This is the +4f settle frame."""
    w = World('default')
    site = 't1_c'
    B = w.sites[site]['B']
    P1 = PX(w.routes['K1']['path'])
    s_stop = w.visit('K1', site)
    progs = dict(SHIFT_E)
    progs[site] = ('GUARD', 'D')
    ks = {'K1': 1.0, 'K2': .55, 'K3': .55}
    cv = plan_base(w, grade=.25, ks=ks, ends={'K1': s_stop + 20}, programs=progs, sealed_k=.7, lock_k=.7, hunter_k=.6, heads=False)
    hy.dead_trail(cv, P1, s_stop + 40, P1.L - 4, k=.7)
    hy.target_ring(cv, B, 'HOLDS', r=46)
    hy.stop_block(cv, P1, s_stop - 2, 'HOLDS')
    ui.flash(cv, B + np.array([30, -12]), 90, TIER['HOLDS'] * .3 + WHITE * .7, .5)
    ui.shock(cv, B + np.array([0, 8]), 70, TIER['HOLDS'], w=3.4, k=.9)
    ui.shock(cv, B + np.array([0, 8]), 112, TIER['HOLDS'], w=2.0, k=.5)
    ui.bits(cv, B + np.array([30, -12]), TYPE_COL['D'] * .6 + WHITE * .4, n=34, r=90, seed=4)
    tp = (B[0] - 6, B[1] - 190)
    hy.leader(cv, B + np.array([0, -62]), np.array(tp) + np.array([0, 28]), k=.8)
    hy.hex_tile(cv, tp, 'HOLDS', None, r=30)
    cs = hud_hand_slots(cv, w, hand_skip=(0,), filled=(('SHIFT', 'E'), ('GUARD', 'D')), hl=1)
    socket(cv, cs[0], k=.35)
    a = Ann()
    a.title('02e  DRAG  ·  snap / place', 'drop 12 f + settle 4 f; flash on landing; carriers go from dashed to solid')
    a.note('1  wall solidifies, ring flash + one shock ring', (B[0] - 400, B[1] - 20), to=(B[0] + 34, B[1] - 14))
    a.note('2  dashed outlines drop away: the preview is now the plan', (B[0] + 450, B[1] - 260), to=(tp[0] + 30, tp[1] + 6))
    a.note('3  the slot fills with the card\'s verb + type', (SLOT_C[0] + 10, SLOT_C[1] - 120), to=(SLOT_C[0] + 38, SLOT_C[1] - 24))
    a.note('4  the empty hand slot closes in 8 f', (cs[0][0] - 280, cs[0][1] - 110), to=(cs[0][0], cs[0][1] - 40))
    emit('02e_drag_snap', cv, a)


def f_02f_cancel():
    """CANCEL: release over nothing, press cancel, or drop on a refusal. The card eases back to its socket along its tether
    (3 echo ghosts), the target lights fade to the soft-hover level, no state changed."""
    w = World('default')
    cv = base_scene(w, 'D', SHIFT_E, grade=.42)
    draw_targets(cv, w, 'D', SHIFT_E, k=.45)
    cs = hud_hand_slots(cv, w, hand_skip=(0,), filled=(('SHIFT', 'E'), None))
    socket(cv, cs[0], k=1.0)
    a_ = np.array([850, 620.0])
    b_ = np.array(cs[0], float)
    pts = EB.bez(a_, (700, 640), (b_[0], b_[1] - 20))
    ech = [(np.array(pts[i]), .22 + .12 * j) for j, i in enumerate((6, 12, 18))]
    pos = np.array(pts[21])
    tether(cv, (a_[0], a_[1] + 20), (pos[0], pos[1] - 20), bend=0)
    drag_card(cv, tuple(pos), 'D', sc=.98, ang=-6, k=.9, echoes=[(tuple(p), kk) for p, kk in ech])
    cursor(cv, (a_[0] - 14, a_[1] - 30), k=.8)
    a = Ann()
    a.title('02f  DRAG  ·  cancel', 'Esc / B / right-click / drop on nothing: eases home in 10 f, no state changes')
    a.note('1  fast-out, soft-in over the tether; 3 echoes = the path', (900, 760), to=(pts[10][0], pts[10][1]))
    a.note('2  pad lights drop to the 45% hover level', (1100, 450), to=(w.sites['t1_b']['B'][0] + 4, w.sites['t1_b']['B'][1] - 106))
    a.note('3  the socket brightens: the slot it returns to', (cs[0][0] - 330, cs[0][1] - 130), to=(cs[0][0], cs[0][1] - 20))
    emit('02f_drag_cancel', cv, a)


def f_02g_limit():
    """THE 2-GUARD LIMIT: both slots are full. Any drag refuses everywhere: red slots, a circle-slash under the pointer, and
    the two placed programs grow a pick-up handle (take one back to place another)."""
    w = World('default')
    progs = dict(SHIFT_E)
    progs['t1_c'] = ('GUARD', 'D')
    site = 't1_b'
    B = w.sites[site]['B']
    ks = {'K1': .5, 'K2': 1.0, 'K3': .5}
    P2 = PX(w.routes['K2']['path'])
    hole = np.maximum(hole_path(P2.sub(520, P2.L, 6), 140), hole_disc(B, 320, 260))
    cv = plan_base(w, grade=.55, hole=hole, ks=ks, programs=progs, sealed_k=.5, lock_k=.5, hunter_k=.4)
    for sid in ('t3_b', 't2_breach'):
        pad_ring(cv, w.sites[sid]['B'], GREY, r=40, k=.55, fill=0, w=2.6, dash=(3, 7))
    refuse(cv, (B[0] + 6, B[1] - 10), r=36)
    halo_site(cv, B, k=.7)
    for sid in ('t1_c', 't2_intel'):
        b = w.sites[sid]['B']
        ui.glyph_disc(cv, (b[0] + 40, b[1] - 120), 17, WHITE * .9, lambda l, c_, r_: act_glyph_mask(l, c_, r_), gscale=.7, k=.95, ring_w=2.4)
    cs = hud_hand_slots(cv, w, hand_skip=(1,), filled=(('SHIFT', 'E'), ('GUARD', 'D')), flash=True)
    socket(cv, cs[1])
    pos = (B[0] + 190, B[1] + 200)
    tether(cv, (pos[0] - 60, pos[1] - 60), (B[0] + 40, B[1] + 20), col=GREASE_R, bend=-40)
    drag_card(cv, pos, 'N', sc=.9, ang=-4, k=.8)
    cursor(cv, (pos[0] - 14, pos[1] - 40))
    a = Ann()
    a.title('02g  DRAG  ·  the 2-guard limit', 'solace_tide_max_placed = 2, shown as two physical sockets')
    a.note('1  both sockets red: full', (SLOT_C[0] - 10, SLOT_C[1] - 100), to=(SLOT_C[0] + 10, SLOT_C[1] - 30))
    a.note('2  every Site refuses (grey dotted),\nthe one under the pointer gets the red slash', (B[0] - 400, B[1] - 160), to=(B[0], B[1] - 12))
    w_ = w.sites
    a.note('3  placed programs show a hand: grab one to take it back,\nwhich empties a socket and re-opens every target', (1000, 760), to=(w_['t2_intel']['B'][0] + 40, w_['t2_intel']['B'][1] - 120))
    emit('02g_drag_limit', cv, a)


def act_glyph_mask(ly, c, r):
    """a small open hand / grab glyph for 'take this back'."""
    ly.rr(c[0] - r * .55, c[1] - r * .1, c[0] + r * .55, c[1] + r * .8, r * .2, 255)
    for i in range(4):
        x = c[0] - r * .42 + i * r * .28
        ly.rr(x - r * .1, c[1] - r * .75, x + r * .1, c[1] - r * .0, r * .1, 255)


# =============================================================== 03 forecast scrub / what-if
def whatif_frame(name, site, title, sub, dud=False, notes=None):
    w = World('default')
    B = w.sites[site]['B']
    P1 = PX(w.routes['K1']['path'])
    s_stop = w.visit('K1', site)
    oldt = BASE12
    newt = list(BASE12) if dud else with_guards(BASE12, d_at=site)
    ends = None if dud else {'K1': s_stop + 20}
    cv = base_scene(w, 'D', SHIFT_E, grade=.4, k_other=.6, ends=ends, heads=False, extra_hole=hole_disc(B, 300, 240))
    if not dud:
        hy.dead_trail(cv, P1, s_stop + 40, P1.L - 4, k=.8)
        old_ring(cv, w.sites['t1_c']['B'], 'SITES_LOST', r=44 if site != 't1_c' else 46)
        old_tile(cv, (w.sites['t1_c']['B'][0] - 6 - 70, w.sites['t1_c']['B'][1] - 190), 'SITES_LOST', r=22)
        ui.firewall(cv, B, 'D', mode='ghost')
        ui.firewall(cv, B, 'D', mode='up', k=.5)
        pv_ring(cv, B, 'HOLDS', r=46)
        pv_block(cv, P1, s_stop - 2, 'HOLDS')
        tp = (B[0] - 6 + (0 if site == 't1_c' else 0), B[1] - 190 if site == 't1_c' else B[1] - 150)
        hy.leader(cv, B + np.array([0, -62]), np.array(tp) + np.array([0, 28]), k=.8)
        pv_tile(cv, tp, 'HOLDS', None, r=30)
    else:
        mk_dud(cv, B, 'D', 'E', k=1.0)
        ui.firewall(cv, B, 'D', mode='ghost', k=.8)
    halo_site(cv, B, k=.9)
    hm = w.home
    tray(cv, 100, 842, 650, 1004)
    tally_diff(cv, oldt, newt, (hm[0] + 12, 962), row=46)
    if dud:
        ui.glyph_disc(cv, (hm[0] - 214, 962), 17, WHITE * .9, g_equal_walls, gscale=.62, k=.95, ring_w=2.4)
    else:
        arrow_chip(cv, (hm[0] + 218, 916), (hm[0] + 218, 948), k=.9, w=2.4, head=9)
    hy.home_chip(cv, hm, 6, k=.9)
    cs = hud_hand_slots(cv, w, hand_skip=(0,), filled=(('SHIFT', 'E'), None))
    socket(cv, cs[0])
    pos = (B[0] + 200, B[1] + 190) if site != 't3_c' else (B[0] - 60, B[1] + 230)
    tether(cv, (pos[0] - 50, pos[1] - 60), (B[0] + 36, B[1] + 20), col=(GREY if dud else TYPE_COL['D']), bend=-40)
    drag_card(cv, pos, 'D', sc=.9, ang=-4, k=.9)
    cursor(cv, (pos[0] - 14, pos[1] - 40))
    a = Ann()
    a.title(title, sub)
    for n in (notes or []):
        a.note(*n[:2], to=n[2] if len(n) > 2 else None)
    emit(name, cv, a)
    return w


def f_03a_whatif_t3c():
    whatif_frame('03a_whatif_t3c', 't3_c', '03a  WHAT-IF  ·  card over t3_c (scrub 1 of 4)', 'hover = preview; release = place. Dashed = uncommitted',
                 notes=[('1  the D beam would stop here, 3 Sites early:\nblock + ring move up the street', (1100, 760), (1188 + 8, 586)),
                        ('2  old amber ring + tile stay as ghosts at t1_c', (440, 400), (542, 520)),
                        ('3  tally: old row (small) above, new row below;\na white hairline and underline follow every outcome that changed', (800, 840), (460, 936))])


def f_03b_whatif_t2v():
    whatif_frame('03b_whatif_t2v', 't2_virus', '03b  WHAT-IF  ·  card over t2_virus (scrub 2 of 4)', 'the pointer moved: ring and block slid along the street, the tally held',
                 notes=[('1  block jumped to t2_virus', (1230, 760), (887 + 6, 655)),
                        ('2  same outcomes, different Site at risk', (660, 420), (542, 520))])


def f_03c_whatif_t1c():
    whatif_frame('03c_whatif_t1c', 't1_c', '03c  WHAT-IF  ·  card over t1_c (scrub 3 of 4)', 'the old ring and the new ring share the Site: amber outside, teal inside',
                 notes=[('1  ring changes tier in place: ghost amber\nring outside, dashed teal ring inside', (300, 400), (500, 560)),
                        ('2  tile: ghost old tile -> dashed new tile', (760, 330), (520, 400))])


def f_03d_whatif_dud():
    whatif_frame('03d_whatif_t3b', 't3_b', '03d  WHAT-IF  ·  card over t3_b (scrub 4 of 4)', 'nothing changes: the ghost row equals the new row, a = mark says so',
                 dud=True,
                 notes=[('1  no ring, no block, no tile: nothing to preview', (1000, 780), (1211, 480)),
                        ('2  tally rows identical: no hairlines, no underlines, = badge', (700, 880), (230, 962))])


if __name__ == '__main__':
    want = sys.argv[1:] or [k[2:] for k in list(globals()) if k.startswith('f_0')]
    for n in want:
        t = time.time()
        globals()['f_' + n]()
        print(n, round(time.time() - t, 1), 's')
