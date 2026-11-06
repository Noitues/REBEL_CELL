"""P1 sequence 8 (onboarding without text) + two extra refusal frames (02h none, 02i same).   python ix_f.py [name ...]"""
import sys, time
from ix_lib import *
from ix_lib import _brackets
from ix_b import (cursor, tether, drag_card, socket, SHIFT_E, mk_match, draw_targets, slots, SLOT_C, base_scene, hud_hand_slots,
                  classify, stop_preview)


# ------------------------------------------------------------------ the ghost hand (a demo cursor, never the player's)
def ghost_hand(cv, tip, k=1.0, closed=False, sc=1.0):
    """a dashed white outline of a hand: index finger out (open) or a fist (closed, holding a card). Only demos use it."""
    t = np.array(tip, float)
    if not closed:
        pts = [(0, 0), (7, 0), (8, 24), (14, 22), (15, 15), (22, 15), (22, 24), (28, 24), (28, 34), (30, 46), (20, 62), (4, 62), (-2, 48), (-10, 34),
               (-4, 31), (1, 38), (0, 0)]
    else:
        pts = [(0, 10), (8, 2), (16, 8), (24, 2), (32, 10), (32, 28), (30, 46), (20, 62), (4, 62), (-2, 48), (-8, 30), (0, 28), (0, 10)]
    P = [tuple(t + np.array(p) * sc) for p in pts]
    ly = Lyr(pbox(P, 16))
    ly.line(P, 2.6, 255, dash=(6, 4))
    fl = Lyr(pbox(P, 16))
    fl.poly(P, 255)
    cv.over(INK, blur(fl.m, 2) * 1.1, .55 * k, fl.off)
    cv.add(WHITE, fl.m, .10 * k, fl.off)
    cv.neonL(ly, WHITE * .95, core=1.0 * k, g1=(2, .5 * k), g2=None)


def echo_rings(cv, c, col, n=3, r0=26, dr=16, k=1.0, iso=True):
    for i in range(n):
        r = r0 + i * dr
        ly = Lyr((c[0] - r - 8, c[1] - r * K - 8, c[0] + r + 8, c[1] + r * K + 8)) if iso else Lyr((c[0] - r - 8, c[1] - r - 8, c[0] + r + 8, c[1] + r + 8))
        ly.line(ring_pts(c, r, 60, k=(K if iso else 1.0)), 2.6, 255)
        cv.neonL(ly, col, core=.95 * k * (1 - i * .28), g1=(2, .4 * k), g2=None)


def spotlight_scene(w, ks, sealed_k=.18, lock_k=.2, hunter_k=.15, hand_ks=None, programs=None, ends=None, heads_on=True, lifts=None, lime=None,
                    site_hi=('t1_c',), grade=.55):
    R = w.routes['K1']
    P1 = PX(R['path'])
    hole = hole_path(P1.sub(R['ext'], P1.L, 6), 150)
    cv = plan_base(w, grade=grade, hole=hole, ks=ks, sealed_k=sealed_k, lock_k=lock_k, hunter_k=hunter_k, home_k=.9, programs=programs or {}, ends=ends,
                   heads=heads_on, site_k={s: (1.0 if s in site_hi else .3) for s in w.sites})
    return cv


def f_08a_first_raid():
    """FIRST RAID, STAGED: one beam, one card, one target. Everything else is present but held back at 20%. The D head and the
    one Site that can stop it pulse in the D hue (concentric echo rings). No panel, no arrow, no word."""
    w = World('default')
    cv = spotlight_scene(w, {'K1': 1.0, 'K2': .2, 'K3': .2})
    tc = w.sites['t1_c']['B']
    mk_match(cv, tc, 'D', k=1.0, strong=True, r=46)
    echo_rings(cv, tc, TYPE_COL['D'], n=3, r0=56, dr=16, k=.9)
    R = w.routes['K1']
    hp = PX(R['path']).at(R['ext'] + RUN['K1'])[0]
    echo_rings(cv, hp, TYPE_COL['D'], n=3, r0=30, dr=16, k=.9, iso=False)
    hy.hud(cv, 44, 50, 80, 8, 0)
    cs = hand_custom(cv, lifts={0: 40}, ks={1: .3, 2: .3, 3: .3, 4: .3})
    a = Ann()
    a.title('08a  ONBOARDING  ·  the first raid', 'staged by dimming, not by hiding: the grammar is there from minute one')
    a.note('1  one beam in full light: its head and the one Site\nthat can stop it ring out in the same D hue', (hp[0] - 120, hp[1] - 190), tuple(hp))
    a.note('2  one card lifted; the others sit at 30%', (cs[0][0] - 330, cs[0][1] - 170), (cs[0][0] - 20, cs[0][1] - 40))
    a.note('3  the other beams, the sealed routes and the hunter are\nheld back at 15-20% (they brighten from raid 2 on)', (620, 330), (w.sites['t2_intel']['B'][0], w.sites['t2_intel']['B'][1] - 100))
    a.note('4  the match is shown by SAME COLOUR + SAME SHAPE:\ndart on the beam, dart on the card tab, dart on the pad', (tc[0] + 520, tc[1] + 200), (tc[0], tc[1] - 106))
    emit('08a_first_raid', cv, a)


DEMO = {}


def demo_frame(step):
    w = World('default')
    site = 't1_c'
    B = np.array(w.sites[site]['B'], float)
    P1 = PX(w.routes['K1']['path'])
    s_stop = w.visit('K1', site)
    placed = step >= 4
    prog = {site: ('GUARD', 'D')} if placed else {}
    ends = {'K1': s_stop + 20} if placed else None
    ks = {'K1': 1.0, 'K2': .2, 'K3': .2}
    cv = spotlight_scene(w, ks, programs=prog, ends=ends, heads_on=not placed)
    card_home = card_centres(HAND, 992)[0]
    if step == 1:
        mk_match(cv, B, 'D', k=.8, strong=True, r=46)
        hand_custom(cv, lifts={0: 22}, ks={1: .3, 2: .3, 3: .3, 4: .3})
        ghost_hand(cv, (card_home[0] - 6, card_home[1] - 56), k=.95)
        echo_rings(cv, (card_home[0], card_home[1] - 20), WHITE * .9, n=2, r0=34, dr=14, k=.7, iso=False)
        hy.hud(cv, 44, 50, 80, 8, 0)
    elif step in (2, 3):
        mk_match(cv, B, 'D', k=.8 if step == 2 else .5, strong=True, r=46)
        cs = hand_custom(cv, skip=(0,), ks={1: .3, 2: .3, 3: .3, 4: .3})
        socket(cv, cs[0])
        pos = (700, 760) if step == 2 else (B[0] + 170, B[1] + 176)
        if step == 3:
            ui.firewall(cv, B, 'D', mode='ghost')
            ui.firewall(cv, B, 'D', mode='up', k=.5)
            stop_preview(cv, w, site)
            halo_site(cv, B)
        tether(cv, (cs[0][0], cs[0][1] - 60), (pos[0] - 10, pos[1] + 66), bend=40)
        drag_card(cv, pos, 'D', sc=.95 if step == 2 else .9, ang=-8)
        ghost_hand(cv, (pos[0] - 24, pos[1] - 40), k=.95, closed=True)
        hy.hud(cv, 44, 50, 80, 8, 0)
    else:
        hy.target_ring(cv, B, 'HOLDS', r=46)
        hy.stop_block(cv, P1, s_stop - 2, 'HOLDS')
        hy.dead_trail(cv, P1, s_stop + 40, P1.L - 4, k=.7)
        hy.head(cv, P1, s_stop - 52, 'D', sc=2.0)
        ui.flash(cv, B + np.array([30, -12]), 90, TIER['HOLDS'] * .3 + WHITE * .7, .5)
        ui.shock(cv, B + np.array([0, 8]), 70, TIER['HOLDS'], w=3.4, k=.9)
        tp = (B[0] - 6, B[1] - 190)
        hy.leader(cv, B + np.array([0, -62]), np.array(tp) + np.array([0, 28]), k=.8)
        hy.hex_tile(cv, tp, 'HOLDS', None, r=30)
        cs = hand_custom(cv, skip=(0,), ks={1: .3, 2: .3, 3: .3, 4: .3})
        socket(cv, cs[0], k=.35)
        slots(cv, SLOT_C, [('GUARD', 'D'), None], k=.95)
        ghost_hand(cv, (card_home[0] + 90, card_home[1] - 150), k=.45)
        hy.hud(cv, 44, 50, 80, 8, 0)
    return cv, w


def f_08b_demo():
    """GHOST-HAND DEMO: the first time a card is idle for 6 s on raid 1, a dashed white hand plays the whole move once (grab,
    carry, drop, result) and vanishes. Four beats, 1:1 crops of the real frames."""
    crops = []
    for step in (1, 2, 3, 4):
        cv, w = demo_frame(step)
        a = Ann()
        titles = {1: 'the hand taps the lifted card', 2: 'it carries the card (closed hand)', 3: 'it hovers the lit Site: the preview shows', 4: 'it lets go: wall, block, tile, the head stops'}
        a.title('08b-%d  GHOST HAND' % step, titles[step])
        emit('08b_demo_%d' % step, cv, a)
        crops.append(Image.open(CLD + '08b_demo_%d.jpg' % step).convert('RGB').resize((960, 540), Image.LANCZOS))
    sheet = Image.new('RGB', (W, H), (8, 6, 20))
    for i, im in enumerate(crops):
        sheet.paste(im, ((i % 2) * 960, (i // 2) * 540))
    dr = ImageDraw.Draw(sheet)
    f = font(26, False, 700, 78)
    for i, t in enumerate(['1  tap', '2  carry', '3  hover = preview', '4  release = placed']):
        x, y = (i % 2) * 960 + 14, (i // 2) * 540 + 12
        dr.rounded_rectangle((x, y, x + 250, y + 40), 8, fill=(246, 241, 228), outline=(10, 10, 28), width=2)
        dr.text((x + 14, y + 6), t, font=f, fill=(10, 10, 28))
    dr.line([(960, 0), (960, 1080)], fill=(8, 6, 20), width=6)
    dr.line([(0, 540), (1920, 540)], fill=(8, 6, 20), width=6)
    sheet.save(OUTD + 'boards/08b_ghost_hand_board.jpg', quality=93, subsampling=0)
    print('saved 08b board')


def type_plate(cv, c, typ, k=1.0, filled=True, sc=3.0):
    """one slot of the type key: the head silhouette big + a short sample of its body; empty slots are dashed outlines."""
    bx = (c[0] - 74, c[1] - 66, c[0] + 74, c[1] + 66)
    o = Lyr(bx)
    o.poly(hy.hexpts(c, 62), 255)
    cv.overL(o, INK, .9 * k)
    e = Lyr(bx)
    e.line(hy.hexpts(c, 62) + [hy.hexpts(c, 62)[0]], 2.6, 255, dash=None if filled else (5, 6))
    cv.neonL(e, TYPE_COL[typ] if filled else GREY, core=(1.0 if filled else .9) * k, g1=(3, .6 * k) if filled else None, g2=None)
    hy.head(cv, None, 0, typ, sc=sc * .62, mode='full' if filled else 'ghost', k=(1.0 if filled else .8) * k, col=None if filled else GREY,
            flat=((c[0] + 6, c[1] - 8), (1, 0)))
    if filled:
        seg = np.array([[c[0] - 46, c[1] + 36], [c[0] + 46, c[1] + 36]])
        P = PX(seg)
        hy.ribbon(cv, P, typ, 0, P.L, k=.95, w=6.0, chev=False)


def f_08c_type_code():
    """THE TYPE CODE, TAUGHT BY A LINK: the first time a head is focused, a type key slot opens (head silhouette + body sample)
    and dashed hairlines join it to the same shape on the card tab and on the target pad. N and E are empty dashed slots,
    filled when their first beam is met (progressive, wordless)."""
    w = World('default')
    R = w.routes['K1']
    P1 = PX(R['path'])
    hp = np.array(P1.at(R['ext'] + RUN['K1'])[0])
    cv = spotlight_scene(w, {'K1': 1.0, 'K2': .25, 'K3': .25}, hunter_k=.2)
    tc = w.sites['t1_c']['B']
    mk_match(cv, tc, 'D', k=.9, strong=True, r=46)
    cs = hand_custom(cv, lifts={0: 30}, ks={1: .4, 2: .4, 3: .4, 4: .4})
    # focus on the head
    ly = Lyr((hp[0] - 60, hp[1] - 60, hp[0] + 60, hp[1] + 60))
    ly.line(hy.hexpts(hp, 44) + [hy.hexpts(hp, 44)[0]], 3.4, 255)
    cv.neonL(ly, LIME, core=1.0, g1=(4, .9), g2=(12, .6))
    # the key: three slots on the street side, D filled
    kx, ky = 1180, 226
    for i, t in enumerate('DNE'):
        type_plate(cv, (kx + (1 - i) * 150, ky), t, filled=(t == 'D'))
    # links: head -> key slot, key slot -> card tab, key slot -> pad chip
    def link(a, b, bend):
        pts = EB.bez(np.array(a, float), tuple((np.array(a) + np.array(b)) / 2 + np.array(bend)), np.array(b, float))
        l2 = Lyr(pbox(pts, 12))
        l2.line(pts, 2.2, 255, dash=(5, 6))
        cv.over(INK, blur(l2.m, 2.5) * 1.8, .65, l2.off)
        cv.neonL(l2, WHITE * .92, core=.95, g1=(2, .35), g2=None)
    link(hp + (0, -40), (kx + 150, ky + 62), (60, -20))
    link((kx + 150 - 30, ky + 62), (cs[0][0] + 8, cs[0][1] - 64), (-500, 200))
    link((kx + 150 - 62, ky), (tc[0], tc[1] - 126), (-260, -40))
    hy.hud(cv, 44, 50, 80, 8, 0)
    a = Ann()
    a.title('08c  ONBOARDING  ·  the type code', 'same shape, same hue, joined by a hairline; the empty slots wait for N and E')
    a.note('1  head focused (lime hex)', (hp[0] - 120, hp[1] + 120), tuple(hp + (0, 44)))
    a.note('2  type key: the head silhouette big + a sample of its body\n(chain links = D). N and E slots are dashed and empty', (kx + 520, ky - 20), (kx + 150, ky))
    a.note('3  hairlines run to the card tab and to the pad chip:\nsame dart, three places', (cs[0][0] + 300, cs[0][1] - 270), (cs[0][0] + 8, cs[0][1] - 64))
    emit('08c_type_code', cv, a)


def f_08d_tier_code():
    """THE TIER CODE, TAUGHT BY A RAMP: the first time a tile appears, a wheatpaste strip is stuck near HOME: the five tiers in a row,
    light to heavy, over a wedge that thickens left to right. A hairline joins the live tile to its slot on the ramp."""
    w = World('default')
    site = 't1_c'
    B = np.array(w.sites[site]['B'], float)
    P1 = PX(w.routes['K1']['path'])
    s_stop = w.visit('K1', site)
    cv = plan_base(w, grade=.4, ks={'K1': 1.0, 'K2': .5, 'K3': .5}, sealed_k=.4, lock_k=.4, hunter_k=.3, programs={site: ('GUARD', 'D')},
                   ends={'K1': s_stop + 20}, heads=False)
    hy.dead_trail(cv, P1, s_stop + 40, P1.L - 4, k=.7)
    hy.target_ring(cv, B, 'HOLDS', r=46)
    hy.stop_block(cv, P1, s_stop - 2, 'HOLDS')
    tp = (B[0] - 6, B[1] - 190)
    hy.leader(cv, B + np.array([0, -62]), np.array(tp) + np.array([0, 28]), k=.8)
    hy.hex_tile(cv, tp, 'HOLDS', None, r=30)
    # the ramp strip near HOME, on the ground
    hm = w.home
    x0, y0 = 110, 958
    L = 480
    strip = Lyr((x0 - 20, y0 - 80, x0 + L + 20, y0 + 70))
    strip.rr(x0, y0 - 56, x0 + L, y0 + 52, 14, 255)
    cv.over(INK, blur(strip.m, 8) * 1.4, .7, strip.off)
    cv.over(PAPER, strip.m, .94, strip.off)
    # the wedge (severity): thin -> thick
    wd = Lyr((x0 - 20, y0 - 80, x0 + L + 20, y0 + 70))
    wd.poly([(x0 + 24, y0 + 40), (x0 + L - 24, y0 + 40), (x0 + L - 24, y0 + 12), (x0 + 24, y0 + 38)], 255)
    cv.over(hexc('2A2240'), wd.m, .9, wd.off)
    cols = TIERS
    xs = [x0 + 56 + i * ((L - 112) / 4) for i in range(5)]
    for i, t in enumerate(cols):
        pos = (xs[i], y0 - 12)
        hy.hex_tile(cv, pos, t, None, r=26, k=1.0 if t == 'HOLDS' else .9)
    # the live slot: a white bracket and a hairline from the tile
    sl = Lyr((xs[1] - 44, y0 - 60, xs[1] + 44, y0 + 40))
    sl.line(hy.hexpts((xs[1], y0 - 12), 40) + [hy.hexpts((xs[1], y0 - 12), 40)[0]], 3, 255)
    cv.neonL(sl, WHITE, core=1.0, g1=(3, .6), g2=None)
    pts = EB.bez(np.array(tp) + np.array([0, 40]), ((tp[0] + xs[1]) / 2 - 120, (tp[1] + y0) / 2), np.array((xs[1], y0 - 56)), 22)
    ll = Lyr(pbox(pts, 12))
    ll.line(pts, 2.2, 255, dash=(5, 6))
    cv.neonL(ll, WHITE * .9, core=.95, g1=(2, .35), g2=None)
    hy.hud(cv, 44, 50, 80, 8, 0)
    hand_custom(cv, ks={i: .5 for i in range(5)})
    a = Ann()
    a.title('08d  ONBOARDING  ·  the tier code', 'a ramp sticker, stuck once at the first tile: five tiles, light to heavy, over a thickening wedge')
    a.note('1  the live tile and its slot on the ramp are joined by a hairline', (tp[0] + 430, tp[1] - 60), (tp[0] + 20, tp[1] + 30))
    a.note('2  left to right: UNTOUCHED, HOLDS, SITES LOST, DAMAGED, BREACHED;\nthe wedge grows with severity (a non-hue channel)', (x0 + 760, y0 - 200), (x0 + L - 60, y0 + 28))
    a.note('3  appears once per profile, fades in 20 f, sits 3 s, never returns;\nreduce-motion: appears, no fade', (x0 + 760, y0 - 90), (x0 + L - 20, y0 - 30))
    emit('08d_tier_code', cv, a)


def f_08e_progressive():
    """PROGRESSIVE DISCLOSURE (a staging suggestion, rule-free: only the light level changes): raid 1 = one beam in light,
    raid 2 = two beams, raid 3+ = the full grammar. Same frame, three light levels."""
    imgs = []
    for lab, ks, sk, lk, hk, hks in (('raid 1', {'K1': 1.0, 'K2': .2, 'K3': .2}, .18, .2, .15, {1: .3, 2: .3, 3: .3, 4: .3}),
                                     ('raid 2', {'K1': 1.0, 'K2': 1.0, 'K3': .2}, .3, .3, .2, {1: 1.0, 2: .3, 3: .3, 4: .3}),
                                     ('raid 3+', {'K1': 1.0, 'K2': 1.0, 'K3': 1.0}, .8, .8, .75, {})):
        w = World('default')
        cv = plan_base(w, grade=0.0, ks=ks, sealed_k=sk, lock_k=lk, hunter_k=hk, programs={}, heads=True)
        hy.hud(cv, 44, 50, 80, 8, 0)
        hand_custom(cv, ks=hks)
        im = to_img(finish(cv, vig=.38, scan=.07, fringe=1.5)).resize((960, 540), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((12, 70, 190, 112), 8, fill=(246, 241, 228), outline=(10, 10, 28), width=2)
        d.text((26, 78), lab, font=font(28, False, 700, 78), fill=(10, 10, 28))
        imgs.append(im)
    sheet = Image.new('RGB', (W, H), (8, 6, 20))
    sheet.paste(imgs[0], (0, 0))
    sheet.paste(imgs[1], (960, 0))
    sheet.paste(imgs[2], (0, 540))
    # legend cell: three light levels as swatches
    d = ImageDraw.Draw(sheet)
    d.text((980, 570), '08e  ONBOARDING  ·  progressive light', font=font(34, False, 800, 75), fill=(240, 243, 255))
    rows = [('raid 1', 'one beam, one card, one target in full light; all else 15-30%'),
            ('raid 2', 'a second beam and its card join; sealed routes at 30%'),
            ('raid 3+', 'locks and hunter at working light; the full grammar'),
            ('', ''),
            ('rule-free:', 'nothing is hidden or removed, only dimmed; if the rules deal'),
            ('', 'fewer beams early, the dim levels simply read 100% for what exists')]
    for i, (a_, b_) in enumerate(rows):
        d.text((980, 630 + i * 46), a_, font=font(26, False, 800, 75), fill=(255, 255, 255))
        d.text((1100, 632 + i * 46), b_, font=font(24, False, 560, 78), fill=(190, 198, 225))
    sheet.save(OUTD + 'boards/08e_progressive_board.jpg', quality=93, subsampling=0)
    print('saved 08e')


# =============================================================== two more refusal frames for the reasons board
def reason_frame(name, site, kind, title, sub, notes):
    w = World('default')
    B = np.array(w.sites[site]['B'], float)
    progs = dict(SHIFT_E)
    if kind == 'same':
        progs['t1_c'] = ('GUARD', 'D')
    cv = base_scene(w, 'D', progs, grade=.58, extra_hole=hole_disc(B, 300, 240))
    if kind == 'none':
        mk_none(cv, B, k=1.0)
        halo_site(cv, B, k=.6)
    else:
        mk_same(cv, B, 'D', k=1.0)
        halo_site(cv, B, k=.8)
        ui.firewall(cv, B, 'D', mode='ghost', k=.6)
    for sid in ('t3_c', 't2_virus', 't1_b') if kind != 'same' else ('t3_c', 't2_virus'):
        mk_match(cv, w.sites[sid]['B'], 'D', k=.35, strong=False, r=40)
    pos = (B[0] + 200, B[1] + 190)
    cs = hud_hand_slots(cv, w, hand_skip=(0,), filled=(('SHIFT', 'E'), ('GUARD', 'D') if kind == 'same' else None))
    socket(cv, cs[0])
    tether(cv, (pos[0] - 60, pos[1] - 60), (B[0] + 40, B[1] + 20), col=GREY, bend=-40)
    drag_card(cv, pos, 'D', sc=.9, ang=-4, k=.85)
    cursor(cv, (pos[0] - 14, pos[1] - 40))
    a = Ann()
    a.title(title, sub)
    for n in notes:
        a.note(*n[:2], to=n[2])
    emit(name, cv, a)


def f_02h_none():
    reason_frame('02h_drag_over_none', 't1_d', 'none', '02h  DRAG  ·  no beam reaches here',
                 'nothing lights: a grey hollow ring cut by a hairline, the card does not tilt, a drop does nothing',
                 [('1  hollow ring + slash: not a target (no beam, or the Site is DOWN)', (700, 500), (600 - 30, 716 - 6))])


def f_02i_same():
    reason_frame('02i_drag_over_same', 't1_b', 'same', '02i  DRAG  ·  already covered',
                 'legal, flagged: another D guard upstream already stops this beam, so this one would change no outcome',
                 [('1  "=" chip: the standing wall already answers this', (1000, 380), (630, 520 - 106))])


if __name__ == '__main__':
    want = sys.argv[1:] or [k[2:] for k in list(globals()) if k.startswith('f_0')]
    for n in want:
        t = time.time()
        globals()['f_' + n]()
        print(n, round(time.time() - t, 1), 's')
