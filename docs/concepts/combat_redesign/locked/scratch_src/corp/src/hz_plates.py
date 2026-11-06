"""hz_plates: the 11 hover plates (one per card effect type) on the final locked board.  build(pid, words) -> (RGB image, report dict).
Every plan value comes from the E10 sim (hover_sim.frame with the card played): towers at plan angle, plan guns, plan landing arcs, plan bill.
Ghosts are the sim's plan units drawn by the board's own unit / arc code at 74 percent, never shifted copies."""
import sys, os, copy, math, json
sys.dont_write_bytecode = True
import hz_core as Z
from hz_core import *

SLIP = {}


def make(pid, words, beat, f_board, f_hud, f_live, lit_fn, marks_fn, hand, lift, ghosts_fn=None, veil=None, arcs_skip=(), hide=(), played=(),
         assert_beat=None, top_fn=None, insets=(), allowed=(), hover_unit=None, note=''):
    reset_checks()
    tag = ftag(f_board, Z.CORP + ('nw' if not words else ''))
    bg = board(beat, f_board, f_hud, tag, words, arcs_skip=arcs_skip, hide_units=hide, hover_unit=hover_unit)
    run_board_asserts(assert_beat or ('p1' if beat in ('p1', 'nowords') else beat), f_board, pid)
    ghosts = []
    if veil is not None:
        ghosts.append(veil)
    if ghosts_fn:
        ghosts.extend(ghosts_fn())
    Lt = HL.Lit()
    lit_fn(Lt)
    mask = Lt.mask()
    NOW['words'] = words
    Z.CAP['on'] = False
    Lm = L2()
    changed = marks_fn(Lm) or {}
    top = []
    if top_fn:
        Lx = L2()
        top_fn(Lx)
        top.append(Lx.done())
    Z.CAP['on'] = True
    hand_lay, stick = ui_layers(words, f_hud, hand, lift, played)
    img = compose(bg, mask, ghosts, [Lm.done()], hand_lay, stick, insets=[i['layer'] for i in insets], top=top)
    rep = dict(plate=pid, corp=Z.CORP, words=words, beat=beat, card=lift, hand=list(hand), played=list(played),
               asserts=dict(total=len(LOGD), passed=sum(1 for x in LOGD if x['ok']), failed=[x for x in LOGD if not x['ok']]),
               insets=[dict(name=i['name'], asserts=i['asserts']) for i in insets],
               collisions=collision_report(allowed), squint=squint_set(img, mask), dash_calls=len(R.DASH_LOG), dot_calls=len(R.DOT_LOG),
               bill=dict(live=[f_live['pv']['eq']['lands'], f_live['pv']['eq']['through']], plan=[f_hud['pv']['eq']['lands'], f_hud['pv']['eq']['through']],
                         ram=[f_live['ram'], f_hud['ram']], trace=[f_live['trace'], f_hud['trace']], hp_after=[f_live['pv']['hp_after'], f_hud['pv']['hp_after']]),
               marks=changed, note=note, z_order=dict(Z.Z_ORDER), lift_dx=Z.HOV.get('dx'), lift_cy=Z.HOV.get('lift_cy'), corners=list(Z.CORNER_LOG),
               lift_scale=Z.HOV.get('lift_s'), lift_min_r=Z.HOV.get('lift_min_r'), hud_ring_fits=list(Z.FIT_LOG))
    if not words:
        rep['alnum_text_calls'] = sorted(set(t for t in TEXTLOG if any(ch.isalnum() for ch in t)))
    return img, rep


# ------------------------------------------------------------------------------------------------ insets
INSET_FRAME = (8, 12, 22)


def inset_layer(name, crop_img, box_xy, words, scale):
    """a variant board crop on a terminal frame, with the card name (the game's own word) on a tab"""
    x0, y0 = box_xy
    c = crop_img.resize((int(crop_img.width * scale), int(crop_img.height * scale)), Image.LANCZOS)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    L = L2()
    w, h = c.width, c.height
    L.rect([x0 - 6, y0 - 6, x0 + w + 6, y0 + h + 6], fill=(5, 9, 18, 255), outline=(92, 225, 255, 255), w=2.4, r=6)
    lay.alpha_composite(L.done())
    lay.paste(c, (x0, y0))
    L2_ = L2()
    L2_.rect([x0 - 6, y0 - 6, x0 + w + 6, y0 + h + 6], outline=(92, 225, 255, 255), w=2.4, r=6)
    if words and name:
        tw = L2_.tw(name, 20, 'anton')
        L2_.rect([x0 + 4, y0 - 18, x0 + 4 + tw + 20, y0 + 10], fill=(5, 9, 18, 255), outline=(92, 225, 255, 255), w=2.0, r=4)
        L2_.text((x0 + 14, y0 - 4), name, 20, 'anton', fill=(242, 246, 255), anchor='lm')
    lay.alpha_composite(L2_.done())
    return lay


def variant(pid, words, beat, f_board, f_hud, f_live, lit_fn, marks_fn, crop, name, xy, scale, arcs_skip=(), ghosts_fn=None, veil=None):
    """render a variant plan on the full board, dim + marks, crop it for an inset; its own draw asserts"""
    reset_checks()
    tag = ftag(f_board, Z.CORP + ('nw' if not words else ''))
    bg = board(beat, f_board, f_hud, tag, words, arcs_skip=arcs_skip)
    run_board_asserts('p1', f_board, pid)
    gh = [veil] if veil is not None else []
    if ghosts_fn:
        gh.extend(ghosts_fn())
    Lt = HL.Lit()
    lit_fn(Lt)
    mask = Lt.mask()
    NOW['words'] = words
    Z.CAP['on'] = False
    Lm = L2()
    marks_fn(Lm)
    Z.CAP['on'] = True
    img = HL.dim_image(bg.convert('RGB'), mask, k=K_DIM, desat=DESAT).convert('RGBA')
    for g in gh:
        img.alpha_composite(g)
    img.alpha_composite(Lm.done())
    asserts = dict(total=len(LOGD), passed=sum(1 for x in LOGD if x['ok']), failed=[x for x in LOGD if not x['ok']])
    cr = img.convert('RGB').crop(crop)
    return dict(name=name, layer=inset_layer(name, cr, xy, words, scale), asserts=asserts)


# ================================================================================================ h01 Spin 3 (insets Spin 2, Nudge)
SPIN = {'Spin3': (('Spin3', 3), 3, ['Brace', 'Spin3', 'Trigger', 'Twist']), 'Spin2': (('Spin2', 2), 2, ['Brace', 'Spin2', 'Trigger', 'Twist']),
        'Nudge': (('Nudge', 1), 1, ['Brace', 'Nudge', 'Trigger', 'Twist'])}


def _spin_parts(card):
    act, n, hand = SPIN[card]
    f_live, f_plan = frames([act], hand)

    def lit(Lt):
        lit_tower(Lt)
        lit_ring(Lt, 0)
        lit_guns(Lt, f_plan)
        lit_arcs_of(Lt, f_plan)
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L, words=True):
        # the tower turns n sectors clockwise: one PLAN arrow in the gap between the tower halo and ring NOW
        a0 = 6.0
        a1 = a0 + 60 * n - 12
        pc(L, HL.arc(205.5, a0, a1, max(20, 14 * n)), w=10, head=17)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        got = bill_marks(L, f_live, f_plan, NOW['words'])
        yb = you_mark(L, f_live, f_plan)
        return dict(bill_rings=got, you_box=yb, rot=f_plan['rot'])
    return f_live, f_plan, hand, lit, marks


def spin(words=True):
    insets = []
    for i, card in enumerate(('Spin2', 'Nudge')):
        fl, fp, hd, lit, mk = _spin_parts(card)
        cx, cy = C
        crop = (int(cx - 232), int(cy - 232), int(cx + 232), int(cy + 232))
        insets.append(variant('h01_' + card.lower(), words, 'p1' if words else 'nowords', fp, fp, fl, lit, mk, crop,
                              {'Spin2': 'SPIN 2', 'Nudge': 'NUDGE'}[card], (1104 + i * 286, 414), 0.56))
    f_live, f_plan, hand, lit, marks = _spin_parts('Spin3')
    return make('h01', words, 'p1' if words else 'nowords', f_plan, f_plan, f_live, lit, marks, hand, 'Spin3', insets=insets,
                note='tower, guns, tracers and landings at the plan angle (rot %d); insets: Spin 2 and Nudge, each its own sim plan' % f_plan['rot'])


# ================================================================================================ h02 Brace
def brace(words=True, aim=2):
    hand = H4
    f_live, f_plan = frames([('Brace', aim)], hand)
    fb = copy.deepcopy(f_plan)
    fb['brace_sectors'] = []
    for w in fb['wheel']:
        w['brace'] = False
    nw = not words
    sec = [w['sector'] for w in f_plan['wheel'] if w['brace']][0]

    def ghosts():
        tl = tower_layer(f_plan, ftag(f_plan, Z.CORP + ('nw' if nw else '')), nw)
        m = wedge_mask(171.0, 199.0, 60 * sec - 30, 60 * sec + 30)
        a = np.asarray(tl.split()[3]).astype(np.float32) * (np.asarray(m).astype(np.float32) / 255.0) * GHOST_A
        tl.putalpha(Image.fromarray(a.astype(np.uint8)))
        return [tl]

    def lit(Lt):
        lit_tower(Lt)
        lit_arcs_of(Lt, f_plan)
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        for s in range(6):
            if s != sec:
                focus_slice(L, s)
        HL.pencil_poly(L, wedge_pts(sec, 172.5, 196.5, 29.0), w=2.8, ink=1.7, seed=sec + 3)
        focus_slice(L, sec, thick=True)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        got = bill_marks(L, f_live, f_plan, words)
        yb = you_mark(L, f_live, f_plan)
        # the block on the landing arcs: a pencil bar just outside the arc that now stops at the clamp
        bars = []
        for it in RA.layout_items(f_plan):
            u = it['u']
            for q in range(u['w']):
                s_ = (it['s0'] + q) % 6
                if u.get('land_brace', {}).get(str(s_)):
                    r = LANES[min(it['lane'], 2)] + HALF + 5
                    HL.pencil(L, HL.arc(r - 2.5, 60 * (it['s0'] + q) - 16, 60 * (it['s0'] + q) - 2), w=3.4, ink=1.8, seed=s_)
                    bars.append([u['id'], s_])
        return dict(bill_rings=got, you_box=yb, braced_sector=sec, clamp_bars=bars)
    return make('h02', words, 'p1' if words else 'nowords', fb, f_plan, f_live, lit, marks, hand, 'Brace', ghosts_fn=ghosts,
                note='clamp plate = the plan tower (Brace on sector %d) cut to the plate band at 74 percent; board at plan values without the plate' % sec)


# ================================================================================================ h03 Trigger (inset: after Twist)
def _trigger_parts(cards, words, hand=H4):
    f_live, f_plan = frames(cards, hand)
    tgt_id = [a[1] for a in cards if a[0] == 'Trigger'][0]
    fb = copy.deepcopy(f_plan)
    live_ids = {u['id']: u for u in f_live['units']}
    victims = [u['id'] for u in f_plan['units'] if u['trigdead']]
    for u in f_plan['units']:
        if u['trigdead']:
            replace_unit(fb, as_dying(live_ids[u['id']]))
        elif u['consumed']:
            replace_unit(fb, as_waiting(live_ids[u['id']]))
    tgt = uby(f_live, tgt_id)
    legal = [a[1] for a in HS.legal(hand=['Trigger'], ram=9)]
    kills = [e for e in f_plan['tlog'] if e[0] == 'trig_unit']

    def lit(Lt):
        lit_cells(Lt, f_live, set(legal) | set(victims))
        lit_arcs_of(Lt, f_plan)
        for e in kills:
            Lt.sector(e[1], CB.ring_geom(0)[0] - 4, CB.ring_geom(tgt['dep'])[1] + 2, 30, 2)
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        for uid in legal:
            if uid != tgt_id:
                focus_cell(L, uby(f_live, uid))
        r0 = CB.ring_geom(tgt['dep'])[1] - 8
        for e in kills:
            ang = 60 * e[1] + 12
            r1 = CB.ring_geom(e[2])[0] + 22
            pc(L, [ppx(C, r0, ang), ppx(C, r1, ang)], w=12, head=17, tail_dot=True)
        bursts = []
        for e in kills:
            if e[7] == 0 or True:
                v = uby(f_live, e[3])
                if v['id'] in victims and v['id'] not in [b[0] for b in bursts]:
                    x, y = AU.token_pos(v)
                    pink_burst(L, x + 26, y + 4, 21, 3)
                    bursts.append([v['id'], round(x), round(y)])
        if f_plan['refunds']:
            v = uby(f_live, victims[0])
            a_ = (cell_angle_span(v)[0] + cell_angle_span(v)[1]) / 2 + 2
            cx, cy = ppx(C, CB.ring_geom(0)[0] - 0, a_)
        focus_cell(L, tgt, thick=True)
        if f_plan['refunds']:
            ram_plus(L, f_plan['ram'] - 1)
        else:
            ram_mark(L, f_live['ram'], f_plan['ram'])
        got = bill_marks(L, f_live, f_plan, NOW['words'])
        yb = you_mark(L, f_live, f_plan)
        trace_mark(L, f_live['trace'], f_plan['trace'])
        return dict(bill_rings=got, you_box=yb, kills=kills, victims=victims, refunds=f_plan['refunds'], bursts=bursts)
    return f_live, f_plan, fb, lit, marks, tgt_id


def trigger(words=True):
    ins = []
    flx, fpx, fbx, litx, mkx, _ = _trigger_parts([('Twist', (1, 1)), ('Trigger', 4)], words)
    cr = (1072, 76, 1896, 386)
    ins.append(variant('h03_after_twist', words, 'p1' if words else 'nowords', fbx, fpx, flx, litx, mkx, cr, 'TWIST + TRIGGER', (1110, 420), 0.62))
    f_live, f_plan, fb, lit, marks, tgt_id = _trigger_parts([('Trigger', 4)], words)
    return make('h03', words, 'p1' if words else 'nowords', fb, f_plan, f_live, lit, marks, H4, 'Trigger', insets=ins,
                note='the Payload resolves now down sectors 3 and 4 into the Packet on ring NOW (all 5 HP, killed, 1 RAM refunded); inset: the bill of Twist then Trigger')


# ================================================================================================ h04 Twist
def twist(words=True, ring=1, d=1):
    hand = H4
    f_live, f_plan = frames([('Twist', (ring, d))], hand)
    changed = [u['id'] for u in f_plan['units'] if u['dep'] == ring and uby(f_live, u['id']).get('land_sectors') != u.get('land_sectors')]

    def lit(Lt):
        lit_ring(Lt, 1)
        lit_ring(Lt, 2)
        lit_arcs_of(Lt, f_plan)
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        r = rmid(ring)
        a_mid = 60
        pc(L, HL.arc(r + 6, a_mid - 22 * d, a_mid + 22 * d, 20), w=14, head=20)
        ro = 2 if ring == 1 else 1
        focus_tag(L, ro, f_plan)
        focus_tag(L, ring, f_plan, thick=True)
        # pencil edge on the landings that move: the plan arcs of the twisted ring
        edged = []
        for it in RA.layout_items(f_plan, set(changed)):
            rr = LANES[min(it['lane'], 2)]
            HL.pencil(L, HL.arc(rr + HALF + 2.0, it['a0'] + 3, it['a1'] - 2), w=2.6, ink=1.5, seed=it['u']['id'], cap=False)
            edged.append([it['u']['id'], it['u']['land_sectors']])
        got = bill_marks(L, f_live, f_plan, NOW['words'])
        return dict(bill_rings=got, moved_landings=edged, twr=f_plan['twr'])

    def top(L):
        P2m.twist_badge(L, f_plan, 'A')
    return make('h04', words, 'p1' if words else 'nowords', f_plan, f_plan, f_live, lit, marks, hand, 'Twist', top_fn=top,
                note='landing arcs at the plan values (ring +%d turns one extra sector): %s' % (ring, {u: uby(f_plan, u)['land_sectors'] for u in changed}))


# ================================================================================================ h05 Strike
def strike(words=True, aim=5):
    hand = ['Strike', 'Brace', 'Trigger', 'Twist']
    f_live, f_plan = frames([('Strike', aim)], hand)
    fb = copy.deepcopy(f_plan)
    lv = uby(f_live, aim)
    pu = uby(f_plan, aim)
    if pu['trigdead']:
        replace_unit(fb, as_dying(lv))
    else:
        u2 = copy.deepcopy(pu)
        u2['lose'] = [0, lv['hp'] - pu['hp'] + pu['lose'][1]]
        u2['hp'] = lv['hp']
        replace_unit(fb, u2)
    legal = [a[1] for a in HS.legal(hand=['Strike'], ram=9)]

    def lit(Lt):
        lit_cells(Lt, f_live, {u for u in legal if u})
        if 0 in legal:
            lit_adjuster(Lt, f_live)
        lit_arcs_of(Lt, f_plan)
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        for u in f_live['units']:
            if u['id'] != aim and u['id'] in legal and u['w'] < 6:
                focus_cell(L, u)
        if 0 in legal:
            focus_adj(L, f_live)
        x, y = AU.token_pos(lv)
        ta = math.degrees(math.atan2(x - C[0], -(y - C[1])))
        bx, by = ppx(C, math.hypot(x - C[0], y - C[1]), ta + 9.5)
        pink_burst(L, bx, by, 20, 5)
        HL.speed_lines(L, bx, by, math.degrees(math.atan2(by - y, bx - x)), 5, 24, 46, PINK)
        focus_cell(L, lv, thick=True)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        got = bill_marks(L, f_live, f_plan, NOW['words'])
        return dict(bill_rings=got, killed=bool(pu['trigdead']), hp_lost=lv['hp'] - (0 if pu['trigdead'] else pu['hp']))
    return make('h05', words, 'p1' if words else 'nowords', fb, f_plan, f_live, lit, marks, hand, 'Strike',
                note='Strike on unit %d (%s, ring +%d): %s' % (aim, lv['kind'], lv['dep'], 'killed, its HP hatched as lost at END TURN, its landing arc gone' if pu['trigdead'] else 'HP hatched'))


# ================================================================================================ h06 Shove (inset: a bump)
def _bump_parts(words, uid=1, d=1):
    hand = ['Shove', 'Brace', 'Trigger', 'Twist']
    f_live, f_plan = frames([('Shove', (uid, d))], hand)
    fb = copy.deepcopy(f_plan)
    hit = []
    for u in f_plan['units']:
        lu = uby(f_live, u['id'])
        if u['hp'] < lu['hp']:
            u2 = copy.deepcopy(u)
            u2['lose'] = [0, (lu['hp'] - u['hp']) + u['lose'][1]]
            u2['hp'] = lu['hp']
            replace_unit(fb, u2)
            hit.append(u['id'])
    u0 = uby(f_live, uid)

    def lit(Lt):
        lit_cells(Lt, f_live, set(hit) | {uid})
        lit_arcs_of(Lt, f_plan, set(hit))

    def marks(L):
        r = rmid(u0['dep'])
        a_edge = 60 * (u0['s'] + u0['w'] - 1) + 30 if d > 0 else 60 * u0['s'] - 30
        pc(L, HL.arc(r + 9, a_edge - 40 * d, a_edge - 6 * d, 16), w=12, head=17)
        bx, by = ppx(C, r + 9, a_edge)
        pink_burst(L, bx, by, 20, 2)
        focus_cell(L, u0, thick=True)
    return f_live, f_plan, fb, lit, marks, hit


def shove(words=True, uid=5, d=1):
    hand = ['Shove', 'Brace', 'Trigger', 'Twist']
    ins = []
    bl, bp, bb, blit, bmk, hit = _bump_parts(words)
    u1 = uby(bl, 1)
    ex, ey = ppx(C, rmid(0), 60 * (u1['s'] + u1['w'] - 1) + 30)
    cr = (int(ex - 175), int(ey - 150), int(ex + 175), int(ey + 150))
    ins.append(variant('h06_bump', words, 'p1' if words else 'nowords', bb, bp, bl, blit, bmk, cr, 'SHOVE (BUMP)', (1110, 420), 0.86))
    f_live, f_plan = frames([('Shove', (uid, d))], hand)
    u0 = uby(f_live, uid)
    u1 = uby(f_plan, uid)
    fb = copy.deepcopy(f_plan)
    replace_unit(fb, as_waiting(u0))
    rows = {}

    def ghosts():
        g, rr = ghost_units(f_plan, {uid}, words)
        rows['r'] = rr
        assert_ghost_rows('h06', f_plan, {uid}, rr)
        return [g]
    veil = veil_cells(f_live, {uid}, 0.6)
    legal = sorted({a[1][0] for a in HS.legal(hand=['Shove'], ram=9)})

    def lit(Lt):
        lit_ring(Lt, 0)
        lit_ring(Lt, 1)
        lit_arcs_of(Lt, f_plan)
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        for u in f_live['units']:
            if u['id'] in legal and u['id'] != uid and u['w'] < 6:
                focus_cell(L, u)
        r = rmid(u0['dep']) - 15
        a_from = 60 * u0['s'] + 6
        a_to = 60 * u1['s'] + (6 if d > 0 else -6)
        if d > 0 and a_to < a_from:
            a_to += 360
        pc(L, HL.arc(r, a_from, a_to - 8 * d, 20), w=12, head=17)
        focus_cell(L, u0, thick=True)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        got = bill_marks(L, f_live, f_plan, NOW['words'])
        trace_mark(L, f_live['trace'], f_plan['trace'])
        return dict(bill_rings=got, moved=[uid, [u0['dep'], u0['s']], [u1['dep'], u1['s']]], plan_landing=u1.get('land_sectors'), bump_inset_hit=hit)
    return make('h06', words, 'p1' if words else 'nowords', fb, f_plan, f_live, lit, marks, hand, 'Shove', ghosts_fn=ghosts, veil=veil, insets=ins,
                note='ghost = the plan frame unit %d at sector %d with its plan landing arc; inset: Shove into a neighbour (sim bump, 1 HP each)' % (uid, u1['s']))


# ================================================================================================ h07 Pull
def pull(words=True, uid=7):
    hand = ['Pull', 'Brace', 'Trigger', 'Twist']
    f_live, f_plan = frames([('Pull', uid)], hand)
    u0 = uby(f_live, uid)
    u1 = uby(f_plan, uid)
    fb = copy.deepcopy(f_plan)
    # the board keeps the unit at its origin (veiled); the ghost is the plan unit one ring in
    fb['units'] = [x for x in fb['units'] if x['id'] != uid] + [as_waiting(u0)]

    def ghosts():
        g, rr = ghost_units(f_plan, {uid}, words)
        assert_ghost_rows('h07', f_plan, {uid}, rr)
        return [g]
    veil = veil_cells(f_live, {uid}, 0.6)

    def lit(Lt):
        lit_cells(Lt, f_live, {uid})
        lit_cells(Lt, f_plan, {uid})
        lit_arcs_of(Lt, f_plan, {uid})
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        a = 60 * u0['s'] + 17
        pc(L, [ppx(C, CB.ring_geom(u0['dep'])[1] - 6, a), ppx(C, rmid(u1['dep']) + 4, a)], w=14, head=20)
        focus_cell(L, u0, thick=True)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        got = bill_marks(L, f_live, f_plan, NOW['words'])
        trace_mark(L, f_live['trace'], f_plan['trace'])
        return dict(bill_rings=got, moved=[uid, [u0['dep'], u0['s']], [u1['dep'], u1['s']]], k=[u0['fate']['k'], u1['fate']['k']])
    return make('h07', words, 'p1' if words else 'nowords', fb, f_plan, f_live, lit, marks, hand, 'Pull', ghosts_fn=ghosts, veil=veil,
                note='the only legal Pull: unit %d moves ring +%d -> +%d, lands a turn sooner (k %d -> %d)' % (uid, u0['dep'], u1['dep'], u0['fate']['k'], u1['fate']['k']))


# ================================================================================================ h08 Hold
def hold(words=True):
    hand = ['Hold', 'Brace', 'Trigger', 'Twist']
    f_live, f_plan = frames([('Hold', 0)], hand)

    def lit(Lt):
        Lt.annulus(BAND[0] - 6, BAND[1] + 6)
        for dp in range(3):
            lit_ring(Lt, dp)
        lit_arcs_of(Lt, f_plan)
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        # the schedule step slides one slot later: a PLAN arrow outside the rim, alongside the tape
        pc(L, HL.arc(516, 14, 84, 30), w=12, head=17)
        moved = []
        for u in f_plan['units']:
            lu = uby(f_live, u['id'])
            if lu.get('land_sectors') != u.get('land_sectors') or lu['fate']['kind'] != u['fate']['kind']:
                moved.append([u['id'], lu.get('land_sectors'), u.get('land_sectors'), u['fate']['kind']])
        for it in RA.layout_items(f_plan, {m[0] for m in moved}):
            rr = LANES[min(it['lane'], 2)]
            HL.pencil(L, HL.arc(rr + HALF + 2.0, it['a0'] + 3, it['a1'] - 2), w=2.6, ink=1.5, seed=it['u']['id'], cap=False)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        got = bill_marks(L, f_live, f_plan, NOW['words'])
        return dict(bill_rings=got, schedule=[f_live['schedule'], f_plan['schedule']], landings_changed=moved)
    return make('h08', words, 'p1' if words else 'nowords', f_plan, f_plan, f_live, lit, marks, hand, 'Hold',
                note='schedule %s -> %s; landing arcs recomputed by the sim' % (f_live['schedule'], f_plan['schedule']))


# ================================================================================================ h09 Firewall
def firewall(words=True, sec=0):
    hand = ['Firewall', 'Brace', 'Trigger', 'Twist']
    f_live, f_plan = frames([('Firewall', sec)], hand)
    burns = fw_hits([('Firewall', sec)], hand)
    fb = copy.deepcopy(f_plan)
    for b in burns:
        u = uby(fb, b['uid'])
        u['lose'] = [u['lose'][0], u['lose'][1] + b['hp_lost']]
    legal = [a[1] for a in HS.legal(hand=['Firewall'], ram=9)]
    bids = [b['uid'] for b in burns]

    def lit(Lt):
        Lt.sector(sec, T_HALO + 2, CB.ring_geom(2)[1] - 4, 22.5, 2)
        lit_cells(Lt, f_live, set(bids))
        lit_arcs_of(Lt, f_plan, set(bids))
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        for s in legal:
            if s != sec:
                focus_col(L, s)
        r0, r1 = T_HALO + 4, CB.ring_geom(2)[1] - 13
        hw = 21.5
        poly = [ppx(C, r1, 60 * sec - hw + 2 * hw * i / 24) for i in range(25)] + [ppx(C, r0, 60 * sec + hw - 2 * hw * i / 24) for i in range(25)]
        HL.tint_poly(L, poly, PINK, 46)
        # flame tongues drawn as a proposal, rising in the empty outer cell of the column (clear of tokens, tags and the digit)
        for q, off in enumerate((-13.0, -6.5, 6.5, 13.0)):
            pts = []
            top = r1 - 4 - (6 if q in (1, 2) else 0)
            for i in range(16):
                r = r1 - 44 + (top - (r1 - 44)) * i / 15
                wob = math.sin(i * 1.1 + q * 1.7) * 2.4 * (1 - i / 18)
                pts.append(ppx(C, r, 60 * sec + off + wob / r * 57.3))
            HL.pencil(L, pts, w=3.4, ink=1.6, seed=11 + q, grain=True, cap=True)
        HL.pencil_poly(L, poly, w=2.8, ink=1.6, seed=9)
        bursts = []
        for b in burns:
            if b['hp_lost'] <= 0:          # an armoured unit that loses nothing gets no burst (burst = a hit that lands)
                continue
            u = uby(f_live, b['uid'])
            x, y = AU.token_pos(u)
            ta = math.degrees(math.atan2(x - C[0], -(y - C[1])))
            bx, by = ppx(C, math.hypot(x - C[0], y - C[1]), ta + 8.5)
            pink_burst(L, bx, by, 17, u['id'])
            bursts.append(b)
        focus_col(L, sec, thick=True)
        ram_mark(L, f_live['ram'], f_plan['ram'])
        got = bill_marks(L, f_live, f_plan, NOW['words'])
        trace_mark(L, f_live['trace'], f_plan['trace'])
        return dict(bill_rings=got, burns=burns, legal_columns=legal)
    return make('h09', words, 'p1' if words else 'nowords', fb, f_plan, f_live, lit, marks, hand, 'Firewall',
                note='burns from the sim (hurt wrapped in the plan preview): %s' % burns)


# ================================================================================================ h10 soak toggle (no card)
def soak(words=True, idx=1):
    hand = H4
    f_live, f_plan = frames([], hand, opt=[idx])
    sec = [w['sector'] for w in f_plan['wheel'] if w['soak']][0]

    def lit(Lt):
        lit_tower(Lt)
        lit_arcs_of(Lt, f_plan)
        lit_bill(Lt)

    def marks(L):
        for s in range(6):
            if s != sec:
                focus_slice(L, s)
        HL.pencil_poly(L, wedge_pts(sec, T_IN + 1, T_PAGE + 2, 29.5), w=2.8, ink=1.7, seed=sec + 3)
        focus_slice(L, sec, thick=True)
        got = bill_marks(L, f_live, f_plan, NOW['words'])
        yb = you_mark(L, f_live, f_plan)
        return dict(bill_rings=got, you_box=yb, soak_sector=sec, soaked=f_plan['pv']['eq']['soaked'])
    return make('h10', words, 'p1' if words else 'nowords', f_plan, f_plan, f_live, lit, marks, hand, None,
                note='END TURN soak on the slice at sector %d (sim option [%d]): THROUGH %d -> %d, HP after %d -> %d' % (
                    sec, idx, f_live['pv']['eq']['through'], f_plan['pv']['eq']['through'], f_live['pv']['hp_after'], f_plan['pv']['hp_after']))


# ================================================================================================ h11 unit hover (the kept p2b form)
def unit(words=True):
    hand = H4
    f = copy.deepcopy(A.J['f1'])
    hv = A.J['hover']
    uid = hv['id']
    u = uby(f, uid)
    land = [h[0] for h in hv['fate']['hits']]
    path = hv['path']

    def lit(Lt):
        lit_cells(Lt, f, {uid})
        for s in land:
            Lt.sector(s, T_IN - 4, T_HALO + 2, 30, 2)
        for (d_, s_) in path:
            ri, ro = CB.ring_geom(d_)
            Lt.sector(s_, ri - 1, ro + 1, 30, 1)
        lit_arcs_of(Lt, f, {uid})
        lit_bill(Lt)
        Lt.box(1086, 398, 1396, 560, 8)
        Lt.line((900, 575), (1092, 480), 14)

    def marks(L):
        for s in land:
            HL.pencil(L, HL.arc(T_HALO + 4.5, 60 * s - 25, 60 * s + 25, 14), w=3.4, ink=1.8, seed=s + 40, cap=False)
        focus_cell(L, u, thick=True)
        return dict(route=path, lands_on=land)

    def top(L):
        if not words:
            H2m.hover_tag_nowords(L, f)
    beat = 'p2b' if words else 'nowords'
    return make('h11', words, beat, f, f, f, lit, marks, hand, None, top_fn=top, assert_beat='p2b', hover_unit=uid,
                note='the p2b form: the board draws the route, the cell brackets and the tag (content parked, note 8); hover dim at 0.40 / 0.45 on top')


BUILD = {'h01': spin, 'h02': brace, 'h03': trigger, 'h04': twist, 'h05': strike, 'h06': shove, 'h07': pull, 'h08': hold, 'h09': firewall, 'h10': soak, 'h11': unit}
NAMES = {'h01': 'h01_tower_turn', 'h02': 'h02_brace', 'h03': 'h03_trigger', 'h04': 'h04_twist', 'h05': 'h05_strike', 'h06': 'h06_shove', 'h07': 'h07_pull',
         'h08': 'h08_hold', 'h09': 'h09_firewall', 'h10': 'h10_soak', 'h11': 'h11_unit'}
