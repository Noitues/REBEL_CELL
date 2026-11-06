"""hv_plates: the 11 hover plates (one per card effect type) on the REBUILT board.  build(pid, words) -> (RGB image, report dict).
Every plan value comes from the E10 sim (hover_sim.frame with the card played, read only).  Ghosts are the sim's plan units drawn by the
board's own unit and arc code at 74 percent.  Ported from corp/src/hz_plates.py (read only) with the review fixes:
  2.4  no inset copies the HUD (h03's TWIST + TRIGGER bill is gone); h04 splits NEXT into one row per Twist option (ART_BIBLE 3.22)
  2.5  pencil (7 px wax + 3 px ink, grain) everywhere; real rings in the bill's new ring room; the YOU change is an underline under the strip
  2.6  hand layout searched per plate (hv_comp.hand_layout)
  3.8  the hovered and the best option rows are neutral (TEXT_HI edge, TEXT_HI star)
  3.9  one RAM treatment (the RAM row's own coin states)
  3.13 h02 Brace (and h10 Soak, the same slice hover): the five non-aimed slices dim with the rings
Inset contents are board crops only (h01 towers, h06 cells); the tower insets are rendered without words, so no text in them is drawn small."""
import sys, os, copy, math, json
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
import hv_core as V
import hv_comp as K
from hv_core import Z, R, A, FH, HL, C, W, H, L2, ppx, NOW, CB, RA, AU, hud2, MASKS, LOGD, HS, obj2, CORP
from hv_core import pc, wax_stroke, PLAN, FOCUS, INKC
from hv_comp import focus_slice, focus_cell, focus_adj, focus_col, focus_tag

frames, uby, as_dying, as_waiting, replace_unit, ftag = Z.frames, Z.uby, Z.as_dying, Z.as_waiting, Z.replace_unit, Z.ftag
lit_tower, lit_arcs_of, lit_cells, lit_ring, lit_adjuster, lit_guns = Z.lit_tower, Z.lit_arcs_of, Z.lit_cells, Z.lit_ring, Z.lit_adjuster, Z.lit_guns
T_IN, T_OUT, T_PAGE, T_HALO = Z.T_IN, Z.T_OUT, Z.T_PAGE, Z.T_HALO
LANES, HALF, rmid = Z.LANES, Z.HALF, Z.rmid
H4 = Z.H4
GHOST_A = Z.GHOST_A
PINK = HL.PINK
INSET_GAP = 14            # px between the HUD bottom and an inset frame
INSET_SEP = 22             # px between two insets


def lit_bill(Lt):
    V.lit_bill(Lt)


def lit_res(Lt):
    V.lit_res(Lt)


def grow_poly(pts, d):
    """offset a cell polygon outward by d px (vertex normals of the closed outline), so a pencil's inner ink edge sits on the cell edge"""
    n = len(pts)
    cx = sum(p[0] for p in pts) / n
    cy = sum(p[1] for p in pts) / n
    out = []
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        n1 = (b[1] - a[1], -(b[0] - a[0]))
        n2 = (c[1] - b[1], -(c[0] - b[0]))
        l1, l2 = math.hypot(*n1) or 1.0, math.hypot(*n2) or 1.0
        nx, ny = n1[0] / l1 + n2[0] / l2, n1[1] / l1 + n2[1] / l2
        ln = math.hypot(nx, ny) or 1.0
        nx, ny = nx / ln, ny / ln
        if (b[0] - cx) * nx + (b[1] - cy) * ny < 0:
            nx, ny = -nx, -ny
        out.append((b[0] + nx * d, b[1] + ny * d))
    return out


PEN_OUT = V.PEN_W / 2 + V.PEN_INK + 0.5      # pencil centre line offset so its inner ink edge touches the shape's edge


VEIL_INSET = 2.0          # px the origin veil keeps inside the cell edge: on the edge line its AA stair-steps read as a dot run


def veil_cells(f, ids, k=0.6):
    """hz_core.veil_cells, inset VEIL_INSET px from the cell outline (the board's own cell edge stays as drawn)"""
    L = L2()
    for u in f['units']:
        if u['id'] in ids and u['w'] < 6:
            HL.tint_poly(L, grow_poly(HL.cell_poly_unit(u), -VEIL_INSET), (8, 10, 20), 255 * k)
    return L.done()


def pencil_cell(L, u, seed=1, out=PEN_OUT):
    """the ghost's pencil outline outside its cell: the cell's own HP ticks and marks stay clear"""
    wax_stroke(L, grow_poly(HL.cell_poly_unit(u), out), seed=seed, cap=False, closed=True)


C17_OUT = PEN_OUT + 2.0   # h04's landing-change outline: its inner ink edge 2.5 px off the cell (the ghost outline's 0.5 px put its outer edge
                          # on the end of the +2 cell's radial keyline at (369, 244): the keyline's AA steps plus that end read as a 5-dot run)


def pencil_arc(L, r, a0, a1, seed=1):
    wax_stroke(L, HL.arc(r, a0, a1), seed=seed, cap=True)


# ------------------------------------------------------------------------------------------------ assembly
def make(pid, words, beat, f_board, f_hud, f_live, lit_fn, marks_fn, hand, lift, ghosts_fn=None, veil=None, arcs_skip=(), hide=(), played=(),
         assert_beat=None, top_fn=None, insets=(), allowed=(), hover_unit=None, note='', pre_board=None, post_board=None):
    K.reset_all()
    if pre_board:
        pre_board()
    # the REFUND tab clears the lifted card (hv_core.TAB): the lift's left edge and top, from the same layout the hand is drawn with
    V.TAB.update(lift_left=None, lift_top=None, shift=0.0)
    if lift is not None:
        lay0 = K.hand_layout_r2(list(hand), lift, not words)
        if lay0.get('lift'):
            m_, x0_, y0_ = lay0['lift']['_m']
            ys_, xs_ = np.nonzero(m_)
            V.TAB.update(lift_left=float(x0_ + xs_.min()), lift_top=float(y0_ + ys_.min()))
    try:
        tag = ftag(f_board, CORP + ('nw' if not words else ''))
        bg = K.board(beat, f_board, f_hud, tag, words, arcs_skip=arcs_skip, hide_units=hide, hover_unit=hover_unit, assert_beat=assert_beat)
    finally:
        if post_board:
            post_board()
    ghosts = []
    if veil is not None:
        ghosts.append(veil)
    if ghosts_fn:
        ghosts.extend(ghosts_fn())
    Lt = HL.Lit()
    lit_fn(Lt)
    mask = lit_you(Lt.mask())
    NOW['words'] = words
    Z.CAP['on'] = False
    Lm = L2()
    changed = marks_fn(Lm) or {}
    top = []
    if top_fn:
        Lx = L2()
        top_fn(Lx)
        top.append(V.done_box(Lx))
    Z.CAP['on'] = True
    # insets: board crops on a terminal frame, under the HUD bottom.  Round 2: the hand no longer moves for them (C6: the fan keeps its slots),
    # so they are fitted into the free band between the HUD (hud_rows bottom, 569 / 607 with the REFUND tab: C8 made it taller) and the hand
    ins_layers, ins_boxes, forbid = [], [], None
    if insets:
        ins_layers, ins_boxes = place_insets(insets, hand, lift, words)
    hand_lay, stick = K.ui_layers(words, hand, lift, forbid)
    img = K.compose(bg, mask, ghosts, [V.done_box(Lm)], hand_lay, stick, insets=ins_layers, top=top)
    rep = dict(plate=pid, corp=CORP, words=words, beat=beat, card=lift, hand_cards=list(hand), played=list(played),
               asserts=dict(total=len(LOGD), passed=sum(1 for x in LOGD if x['ok']), failed=[x for x in LOGD if not x['ok']]),
               insets=[dict(name=i['name'], asserts=i['asserts'], source=i.get('source'), box=b['box']) for i, b in zip(insets, ins_boxes)],
               bill=dict(live=[f_live['pv']['eq']['lands'], f_live['pv']['eq']['through']], plan=[f_hud['pv']['eq']['lands'], f_hud['pv']['eq']['through']],
                         ram=[f_live['ram'], f_hud['ram']], trace=[f_live['trace'], f_hud['trace']], hp_after=[f_live['pv']['hp_after'], f_hud['pv']['hp_after']]),
               marks=changed, note=note, z_order=dict(Z.Z_ORDER), corners=list(Z.CORNER_LOG), hud_ring_fits=list(V.FIT_LOG), hand=dict(K.HV_HAND),
               snap=dict(K.SNAP), lit_mask=None)
    if not words:
        rep['alnum_text_calls'] = sorted(set(t for t in Z.TEXTLOG if any(ch.isalnum() for ch in t)))
    # dash / dot draw calls: the board's (from its render, kept in the cache snap) + the hover marks' own
    miss = str(K.SNAP.get('cache', '')).startswith('miss')
    rep['dash_calls'] = int(K.SNAP.get('dash') or 0) + len(R.DASH_LOG) - (int(K.SNAP.get('dash') or 0) if miss else 0)
    rep['dot_calls'] = int(K.SNAP.get('dot') or 0) + len(R.DOT_LOG) - (int(K.SNAP.get('dot') or 0) if miss else 0)
    STATE.clear()
    STATE.update(mask=np.asarray(mask), img=img, f_board=f_board, beat=beat, hover_unit=hover_unit, hud_hero_full=MASKS.get('hud_hero', np.zeros((H, W), bool)).copy())
    rep['collisions'] = Z.collision_report(allowed)
    rep['squint'] = Z.squint_set(img, mask)
    return img, rep


STATE = {}
YOU_LIT_PAD = 2           # px: the YOU strip's lit mask is its own alpha grown by this (the die-cut edge and its soft rim)


def lit_you(mask):
    """C8: the YOU strip is part of the HUD, so when the bill is lit the whole strip is lit.  Its die-cut edge pokes 6 px left of the bill
    frame (x 1066-1072), which the bill box alone left at the hover dim: the strip's left keyline read darker than the board's (#862E5E for
    #FF3DA8) and broke the bill plate's keyline column."""
    ym = K.YOU_MASK.get('you')
    if ym is None:
        return mask
    mk = np.asarray(mask).copy()
    bb = V.hud_box('bill')
    if mk[int((bb[1] + bb[3]) / 2), int((bb[0] + bb[2]) / 2)] < 250:
        return mask
    from scipy import ndimage as ndi
    mk[ndi.binary_dilation(ym, iterations=YOU_LIT_PAD)] = 255
    return Image.fromarray(mk, 'L')


def inset_layer(name, crop_img, xy, words, disc=None):
    """a variant board crop on a terminal frame (cyan edge), with the card name (the game's own word) on a tab; disc = clip the crop to a circle"""
    x0, y0 = xy
    c = crop_img
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    L = L2()
    w, h = c.width, c.height
    L.rect([x0 - 6, y0 - 6, x0 + w + 6, y0 + h + 6], fill=(5, 9, 18, 255), outline=(92, 225, 255, 255), w=2.4, r=6)
    lay.alpha_composite(L.done())
    if disc:
        m = Image.new('L', (w * 4, h * 4), 0)
        ImageDraw.Draw(m).ellipse([0, 0, w * 4 - 1, h * 4 - 1], fill=255)
        c = c.convert('RGBA')
        c.putalpha(m.resize((w, h), Image.LANCZOS))
        lay.alpha_composite(c, (x0, y0))
    else:
        lay.paste(c, (x0, y0))
    L2_ = L2()
    L2_.rect([x0 - 6, y0 - 6, x0 + w + 6, y0 + h + 6], outline=(92, 225, 255, 255), w=2.4, r=6)
    if words and name:
        tw = L2_.tw(name, 22, 'anton')
        L2_.rect([x0 + 4, y0 - 20, x0 + 4 + tw + 20, y0 + 10], fill=(5, 9, 18, 255), outline=(92, 225, 255, 255), w=2.0, r=4)
        L2_.text((x0 + 14, y0 - 5), name, 22, 'anton', fill=(242, 246, 255), anchor='lm')
    lay.alpha_composite(L2_.done())
    return lay, (x0 - 6, y0 - 22 if (words and name) else y0 - 6, x0 + w + 6, y0 + h + 6)


INSET_HAND_GAP = 6        # px kept between an inset frame and the hand (the lifted card, its print and drop included)
INSET_TAB = 22            # px the name tab rises above the frame (inset_layer)
INSET_SCALES = tuple(round(0.50 - 0.01 * i, 2) for i in range(0, 26))     # disc insets: 0.50 down to 0.25 of the board crop
RECT_MIN_H = 110          # rect insets (the 1x bump crop) are trimmed in height (centred), never scaled, down to this


def place_insets(insets, hand, lift, words):
    """round 2: the insets right-aligned under the HUD, in the band the hand leaves free.  A disc inset (h01 towers, rendered without words) is
    scaled from its full-size board crop (0.50 at most, as round 1); a rect inset (h06 bump, a 1x crop) is trimmed in height around its centre, so
    no word in it is drawn small.  Returns (layers, boxes); each inset's 'source' records the scale / trim used."""
    hb = (K.SNAP.get('hud_rows') or {}).get('hud_bottom') or K.SNAP.get('hud_bottom') or A.INFO.get('hud_bottom')
    hl = K.hand_layout_r2(list(hand), lift, not words)
    handm = np.zeros((H, W), bool)
    for c in hl['cards'] + ([hl['lift']] if hl.get('lift') else []):
        K._paste(handm, *c['_m'])
    from scipy import ndimage as _ndi
    handm = _ndi.binary_dilation(handm, iterations=INSET_HAND_GAP)
    K.button_masks(words)
    btn = K.BTN['send'] | K.BTN['undo']
    block = handm | _ndi.binary_dilation(btn, iterations=INSET_HAND_GAP)
    y0 = int(hb + INSET_GAP + (INSET_TAB + 2 if words else 6))
    xr = int(V.hud_box('bill')[2]) + 6

    def sized(s):
        out = []
        for ins in insets:
            full = ins['full']
            if ins.get('disc'):
                out.append(full.resize((int(round(full.width * s)), int(round(full.height * s))), Image.LANCZOS))
            else:
                out.append(full)
        return out

    def fits(crops):
        tot = sum(c.width + 12 for c in crops) + INSET_SEP * (len(crops) - 1)
        x = xr - tot
        boxes = []
        for c in crops:
            b = (x - 6, y0 - (INSET_TAB if words else 6), x + c.width + 6, y0 + c.height + 6)
            boxes.append(((x, y0), b))
            x = b[2] + INSET_SEP + 6
        ok = all(not block[max(0, b[1]):b[3], max(0, b[0]):b[2]].any() for _, b in boxes)
        return ok, boxes

    chosen = None
    for s in INSET_SCALES:
        crops = sized(s)
        # rect insets: trim to the free height at this x (the free band under the HUD), centred on the crop's centre
        for i, ins in enumerate(insets):
            if ins.get('disc'):
                continue
            c = crops[i]
            for hh in range(c.height, RECT_MIN_H - 1, -2):
                cc = c.crop((0, (c.height - hh) // 2, c.width, (c.height - hh) // 2 + hh))
                trial = list(crops)
                trial[i] = cc
                if fits(trial)[0]:
                    crops[i] = cc
                    break
            else:
                crops[i] = c.crop((0, (c.height - RECT_MIN_H) // 2, c.width, (c.height - RECT_MIN_H) // 2 + RECT_MIN_H))
        ok, boxes = fits(crops)
        if ok:
            chosen = (s, crops, boxes)
            break
    if chosen is None:
        s = INSET_SCALES[-1]
        crops = sized(s)
        ok, boxes = fits(crops)
        chosen = (s, crops, boxes)
    s, crops, boxes = chosen
    layers, out = [], []
    for ins, c, ((x, y), b) in zip(insets, crops, boxes):
        lay, box = inset_layer(ins['name'], c, (x, y), words, ins.get('disc'))
        layers.append(lay)
        out.append(dict(name=ins['name'], box=box))
        src = ins.setdefault('source', {})
        src.update(placed_scale=(s * ins.get('scale0', 1.0)) if ins.get('disc') else ins.get('scale0', 1.0), placed_size=[c.width, c.height],
                   full_size=[ins['full'].width, ins['full'].height], fits_band=bool(ok), hud_bottom=hb, band_top_y=y0)
        ins['crop'] = c
    return layers, out


def variant(pid, words, beat, f_board, f_hud, f_live, lit_fn, marks_fn, crop, name, scale, disc=None, ghosts_fn=None, veil=None, board_words=None):
    """a variant plan on the full board (its own board render and draw asserts), dim + marks, cropped (and scaled) for an inset"""
    K.reset_all()
    bw = words if board_words is None else board_words
    tag = ftag(f_board, CORP + ('nw' if not bw else ''))
    bg = K.board(beat if bw else 'nowords', f_board, f_hud, tag, bw)
    asserts = dict(total=len(LOGD), passed=sum(1 for x in LOGD if x['ok']), failed=[x for x in LOGD if not x['ok']])
    gh = [veil] if veil is not None else []
    if ghosts_fn:
        gh.extend(ghosts_fn())
    Lt = HL.Lit()
    lit_fn(Lt)
    mask = Lt.mask()
    NOW['words'] = bw
    Z.CAP['on'] = False
    V.PEN['cap'] = False
    Lm = L2()
    marks_fn(Lm)
    V.PEN['cap'] = True
    Z.CAP['on'] = True
    img = HL.dim_image(bg.convert('RGB'), mask, k=Z.K_DIM, desat=Z.DESAT).convert('RGBA')
    for g in gh:
        img.alpha_composite(g)
    img.alpha_composite(V.done_box(Lm))
    cr = img.convert('RGB').crop(crop)
    full = cr
    if scale != 1.0:
        cr = cr.resize((int(round(cr.width * scale)), int(round(cr.height * scale))), Image.LANCZOS)
    # round 2: 'full' is the 1x board crop; place_insets scales a disc inset from it (at most `scale`) or trims a rect inset
    return dict(name=name, crop=cr, full=full, scale0=1.0, asserts=asserts, disc=disc,
                source=dict(crop=list(crop), scale_max=scale, board_words=bw))


# ================================================================================================ h01 Spin 3 (insets Spin 2, Nudge)
SPIN = {'Spin3': (('Spin3', 3), 3, ['Brace', 'Spin3', 'Trigger', 'Twist']), 'Spin2': (('Spin2', 2), 2, ['Brace', 'Spin2', 'Trigger', 'Twist']),
        'Nudge': (('Nudge', 1), 1, ['Brace', 'Nudge', 'Trigger', 'Twist'])}
SPIN_ARC_R, SPIN_ARC_W = 205.5, 9      # the PLAN arrow in the 17 px gap between the tower halo (r197) and ring NOW (r214)
INSET_DISC_R, INSET_SCALE = 214, 0.5   # h01 tower insets: the tower and its arrow (r <= 214), at half size, no words


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

    def marks(L):
        a0 = 6.0
        a1 = a0 + 60 * n - 12
        pc(L, HL.arc(SPIN_ARC_R, a0, a1, max(20, 14 * n)), w=SPIN_ARC_W, head=17)
        got = V.bill_marks(L, f_live, f_plan, NOW['words'])
        yb = V.you_mark(L, f_live, f_plan)
        return dict(bill_rings=got, you_underline=yb, rot=f_plan['rot'])
    return f_live, f_plan, hand, lit, marks


def spin(words=True):
    insets = []
    cx, cy = C
    rr = INSET_DISC_R
    crop = (int(cx - rr), int(cy - rr), int(cx + rr), int(cy + rr))
    for card in ('Spin2', 'Nudge'):
        fl, fp, hd, lit, mk = _spin_parts(card)
        insets.append(variant('h01_' + card.lower(), words, 'p1', fp, fp, fl, lit, mk, crop, {'Spin2': 'SPIN 2', 'Nudge': 'NUDGE'}[card], INSET_SCALE,
                              disc=True, board_words=False))
    f_live, f_plan, hand, lit, marks = _spin_parts('Spin3')
    return make('h01', words, 'p1' if words else 'nowords', f_plan, f_plan, f_live, lit, marks, hand, 'Spin3', insets=insets,
                note='tower, guns, tracers and landings at the plan angle (rot %d); insets: Spin 2 and Nudge, each its own sim plan, tower crops '
                     'without words' % f_plan['rot'])


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
        tl = Z.tower_layer(f_plan, ftag(f_plan, CORP + ('nw' if nw else '')), nw)
        m = Z.wedge_mask(171.0, 199.0, 60 * sec - 30, 60 * sec + 30)
        a = np.asarray(tl.split()[3]).astype(np.float32) * (np.asarray(m).astype(np.float32) / 255.0) * GHOST_A
        tl.putalpha(Image.fromarray(a.astype(np.uint8)))
        return [tl]

    def lit(Lt):
        # 3.13: only the aimed slice, the hub (its HP ring changes) and the landings that hit the aimed slice stay lit; the other five dim
        Lt.disc(T_IN + 1)
        Lt.sector(sec, T_IN - 2, T_HALO + 3, 30, 2)
        hit_ids = {it['u']['id'] for it in RA.layout_items(f_plan) if any((it['s0'] + q) % 6 == sec for q in range(it['u']['w']))}
        lit_arcs_of(Lt, f_plan, hit_ids or None)
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        for s in range(6):
            if s != sec:
                focus_slice(L, s)
        focus_slice(L, sec, thick=True)
        got = V.bill_marks(L, f_live, f_plan, words)
        yb = V.you_mark(L, f_live, f_plan)
        bars = []
        for it in RA.layout_items(f_plan):
            u = it['u']
            for q in range(u['w']):
                s_ = (it['s0'] + q) % 6
                if u.get('land_brace', {}).get(str(s_)):
                    r = LANES[min(it['lane'], 2)] + HALF + PEN_OUT
                    pencil_arc(L, r, 60 * (it['s0'] + q) - 17, 60 * (it['s0'] + q) - 3, seed=s_)
                    bars.append([u['id'], s_])
        return dict(bill_rings=got, you_underline=yb, braced_sector=sec, clamp_bars=bars, lit='hub + aimed slice + its landings (3.13)')
    return make('h02', words, 'p1' if words else 'nowords', fb, f_plan, f_live, lit, marks, hand, 'Brace', ghosts_fn=ghosts,
                note='clamp plate = the plan tower (Brace on sector %d) cut to the plate band at 74 percent; board at plan values without the plate; '
                     'the five non-aimed slices dim (3.13)' % sec)


# ================================================================================================ h03 Trigger (2.4: no inset; no copy of the HUD)
def trigger(words=True, hand=H4):
    cards = [('Trigger', 4)]
    f_live, f_plan = frames(cards, hand)
    tgt_id = 4
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
            v = uby(f_live, e[3])
            if v['id'] in victims and v['id'] not in [b[0] for b in bursts]:
                x, y = AU.token_pos(v)
                Z.pink_burst(L, x + 26, y + 4, 21, 3)
                bursts.append([v['id'], round(x), round(y)])
        focus_cell(L, tgt, thick=True)
        got = V.bill_marks(L, f_live, f_plan, NOW['words'])
        yb = V.you_mark(L, f_live, f_plan)
        return dict(bill_rings=got, you_underline=yb, kills=kills, victims=victims, refunds=f_plan['refunds'], bursts=bursts,
                    ram=[f_live['ram'], f_plan['ram']], trace=[f_live['trace'], f_plan['trace']])
    return make('h03', words, 'p1' if words else 'nowords', fb, f_plan, f_live, lit, marks, hand, 'Trigger',
                note='the Payload resolves now down sectors 3 and 4 into the Packet on ring NOW (all 5 HP, killed, 1 RAM refunded: the RAM row '
                     'shows it in its own coin states, 3.9); no inset (2.4)')


# ================================================================================================ h04 Twist (2.4: one NEXT row per option)
RING_TAG = {1: '+1 W2', 2: '+2 W3'}


def twist(words=True, ring=1, d=1):
    hand = H4
    f_live, f_plan = frames([('Twist', (ring, d))], hand)
    changed = [u['id'] for u in f_plan['units'] if u['dep'] == ring and uby(f_live, u['id']).get('land_sectors') != u.get('land_sectors')]
    opts = []
    for a in HS.legal(hand=['Twist'], ram=9):
        fo, _, _ = HS.frame([a], None, 'tw', hand=hand)
        rg, dd = a[1]
        opts.append(dict(ring=rg, d=dd, tag=RING_TAG.get(rg, '+%d' % rg), next=fo['next'], sel=(rg, dd) == (ring, d)))
    best_taken = min(o['next']['taken'] for o in opts)
    for o in opts:
        o['best'] = o['next']['taken'] == best_taken and sum(1 for q in opts if q['next']['taken'] == best_taken) < len(opts)

    def pre():
        V.OPT['rows'] = opts

    def post():
        V.OPT['rows'] = None

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
        # C17 (review N3): the PLAN halo sits only on the legal rings.  Round 1 edged the changed landing arcs in pencil on the frame band (r ~484,
        # 8921 PLAN px at r 480-500: "the whole board").  Round 2: the units whose landing the Twist changes get the pencil outline on their own
        # cell, on the twisted ring (the ghost grammar: "this unit's plan changes"); 0 PLAN px on the frame band
        edged = []
        for uid in changed:
            u = uby(f_plan, uid)
            if u['w'] < 6:
                pencil_cell(L, u, seed=uid, out=C17_OUT)
                edged.append([uid, u['dep'], u.get('land_sectors')])
        got = V.bill_marks(L, f_live, f_plan, NOW['words'])
        return dict(bill_rings=got, moved_landings_cells=edged, twr=f_plan['twr'], option_rows=[{k: v for k, v in o.items()} for o in opts])

    def top(L):
        Z.P2m.twist_badge(L, f_plan, 'A')
    return make('h04', words, 'p1' if words else 'nowords', f_plan, f_plan, f_live, lit, marks, hand, 'Twist', top_fn=top, pre_board=pre, post_board=post,
                note='landing arcs at the plan values (ring +%d turns one extra sector): %s; NEXT split into one row per option (%d options)' % (
                    ring, {u: uby(f_plan, u)['land_sectors'] for u in changed}, len(opts)))


# ================================================================================================ h05 Strike
def strike(words=True, aim=5):
    hand = ['Brace', 'Strike', 'Trigger', 'Twist']          # the showcase card in Spin 3's slot (slot 1): a slot-0 lift has no room in the 4-card fan
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
        Z.pink_burst(L, bx, by, 20, 5)
        HL.speed_lines(L, bx, by, math.degrees(math.atan2(by - y, bx - x)), 5, 24, 46, PINK)
        focus_cell(L, lv, thick=True)
        got = V.bill_marks(L, f_live, f_plan, NOW['words'])
        return dict(bill_rings=got, killed=bool(pu['trigdead']), hp_lost=lv['hp'] - (0 if pu['trigdead'] else pu['hp']))
    return make('h05', words, 'p1' if words else 'nowords', fb, f_plan, f_live, lit, marks, hand, 'Strike',
                note='Strike on unit %d (%s, ring +%d): %s' % (aim, lv['kind'], lv['dep'], 'killed, its HP hatched as lost at END TURN, its landing arc gone'
                                                              if pu['trigdead'] else 'HP hatched'))


# ================================================================================================ h06 Shove (inset: a bump)
BUMP_CROP = (300, 220)          # h06 bump inset: a 1x crop (no scaling, so any word in it stays at board size)


def _bump_parts(words, uid=1, d=1):
    hand = ['Brace', 'Shove', 'Trigger', 'Twist']          # the showcase card in Spin 3's slot (slot 1): a slot-0 lift has no room in the 4-card fan
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
        Z.pink_burst(L, bx, by, 20, 2)
        focus_cell(L, u0, thick=True)
    return f_live, f_plan, fb, lit, marks, hit


def shove(words=True, uid=5, d=1):
    hand = ['Brace', 'Shove', 'Trigger', 'Twist']          # the showcase card in Spin 3's slot (slot 1): a slot-0 lift has no room in the 4-card fan
    ins = []
    bl, bp, bb, blit, bmk, hit = _bump_parts(words)
    u1 = uby(bl, 1)
    ex, ey = ppx(C, rmid(0), 60 * (u1['s'] + u1['w'] - 1) + 30)
    cw, ch = BUMP_CROP
    cr = (int(ex - cw / 2), int(ey - ch / 2), int(ex + cw / 2), int(ey + ch / 2))
    ins.append(variant('h06_bump', words, 'p1', bb, bp, bl, blit, bmk, cr, 'SHOVE', 1.0))
    f_live, f_plan = frames([('Shove', (uid, d))], hand)
    u0 = uby(f_live, uid)
    u1 = uby(f_plan, uid)
    fb = copy.deepcopy(f_plan)
    replace_unit(fb, as_waiting(u0))
    rows = {}

    def ghosts():
        g, rr = ghost_units(f_plan, {uid}, words)
        rows['r'] = rr
        Z.assert_ghost_rows('h06', f_plan, {uid}, rr)
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
        got = V.bill_marks(L, f_live, f_plan, NOW['words'])
        return dict(bill_rings=got, moved=[uid, [u0['dep'], u0['s']], [u1['dep'], u1['s']]], plan_landing=u1.get('land_sectors'), bump_inset_hit=hit)
    return make('h06', words, 'p1' if words else 'nowords', fb, f_plan, f_live, lit, marks, hand, 'Shove', ghosts_fn=ghosts, veil=veil, insets=ins,
                note='ghost = the plan frame unit %d at sector %d with its plan landing arc; inset: Shove into a neighbour (sim bump, 1 HP each)' % (uid, u1['s']))


def ghost_units(f_plan, ids, words, beat='p1', alpha=GHOST_A):
    """hz_core.ghost_units with the 7 px pencil outline drawn OUTSIDE the ghost cell (its HP ticks stay clear)"""
    g, rows = Z.ghost_units(f_plan, ids, words, beat, alpha, outline=False)
    Lo = L2()
    for u in f_plan['units']:
        if u['id'] in ids and not (u['consumed'] or u['trigdead']) and u['w'] < 6:
            pencil_cell(Lo, u, seed=u['id'])
    g.alpha_composite(V.done_box(Lo))
    return g, rows


# ================================================================================================ h07 Pull
def pull(words=True, uid=7):
    hand = ['Brace', 'Pull', 'Trigger', 'Twist']          # the showcase card in Spin 3's slot (slot 1): a slot-0 lift has no room in the 4-card fan
    f_live, f_plan = frames([('Pull', uid)], hand)
    u0 = uby(f_live, uid)
    u1 = uby(f_plan, uid)
    fb = copy.deepcopy(f_plan)
    fb['units'] = [x for x in fb['units'] if x['id'] != uid] + [as_waiting(u0)]

    def ghosts():
        g, rr = ghost_units(f_plan, {uid}, words)
        Z.assert_ghost_rows('h07', f_plan, {uid}, rr)
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
        got = V.bill_marks(L, f_live, f_plan, NOW['words'])
        return dict(bill_rings=got, moved=[uid, [u0['dep'], u0['s']], [u1['dep'], u1['s']]], k=[u0['fate']['k'], u1['fate']['k']])
    return make('h07', words, 'p1' if words else 'nowords', fb, f_plan, f_live, lit, marks, hand, 'Pull', ghosts_fn=ghosts, veil=veil,
                note='the only legal Pull: unit %d moves ring +%d -> +%d, lands a turn sooner (k %d -> %d)' % (uid, u0['dep'], u1['dep'], u0['fate']['k'], u1['fate']['k']))


# ================================================================================================ h08 Hold
def hold(words=True):
    hand = ['Brace', 'Hold', 'Trigger', 'Twist']          # the showcase card in Spin 3's slot (slot 1): a slot-0 lift has no room in the 4-card fan
    f_live, f_plan = frames([('Hold', 0)], hand)

    def lit(Lt):
        Lt.annulus(Z.BAND[0] - 6, Z.BAND[1] + 6)
        for dp in range(3):
            lit_ring(Lt, dp)
        lit_arcs_of(Lt, f_plan)
        lit_bill(Lt)
        lit_res(Lt)

    def marks(L):
        pc(L, HL.arc(516, 14, 84, 30), w=12, head=17)
        moved = []
        for u in f_plan['units']:
            lu = uby(f_live, u['id'])
            if lu.get('land_sectors') != u.get('land_sectors') or lu['fate']['kind'] != u['fate']['kind']:
                moved.append([u['id'], lu.get('land_sectors'), u.get('land_sectors'), u['fate']['kind']])
        for it in RA.layout_items(f_plan, {m[0] for m in moved}):
            rr = LANES[-1] + HALF + PEN_OUT
            pencil_arc(L, rr, it['a0'] + 3, it['a1'] - 2, seed=it['u']['id'])
        got = V.bill_marks(L, f_live, f_plan, NOW['words'])
        return dict(bill_rings=got, schedule=[f_live['schedule'], f_plan['schedule']], landings_changed=moved)
    return make('h08', words, 'p1' if words else 'nowords', f_plan, f_plan, f_live, lit, marks, hand, 'Hold',
                note='schedule %s -> %s; landing arcs recomputed by the sim' % (f_live['schedule'], f_plan['schedule']))


# ================================================================================================ h09 Firewall
def firewall(words=True, sec=0):
    hand = ['Brace', 'Firewall', 'Trigger', 'Twist']          # the showcase card in Spin 3's slot (slot 1): a slot-0 lift has no room in the 4-card fan
    f_live, f_plan = frames([('Firewall', sec)], hand)
    burns = Z.fw_hits([('Firewall', sec)], hand)
    fb = copy.deepcopy(f_plan)
    for b in burns:
        u = uby(fb, b['uid'])
        u['lose'] = [u['lose'][0], u['lose'][1] + b['hp_lost']]
    legal = [a[1] for a in HS.legal(hand=['Firewall'], ram=9)]
    bids = [b['uid'] for b in burns]

    def lit(Lt):
        # the whole column of cells is lit (a 45 deg wedge left the corners of the NOW cell dim: half its glass read dimmed while it was gated lit)
        Lt.sector(sec, T_HALO + 2, CB.ring_geom(2)[1] - 4, 30.0, 2)
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
        K.value_tint(poly, PINK, 46 / 255.0)          # hue only: the column's glass keeps its value (empty cells stay the ring's dark)
        # flame tongues drawn as a proposal (pencil), rising in the outer cell of the column, clear of tokens, tags and the digit
        for q, off in enumerate((-12.0, 0.0, 12.0)):
            pts = []
            top = r1 - 6 - (6 if q == 1 else 0)
            for i in range(16):
                r = r1 - 40 + (top - (r1 - 40)) * i / 15
                wob = math.sin(i * 1.1 + q * 1.7) * 2.4 * (1 - i / 18)
                pts.append(ppx(C, r, 60 * sec + off + wob / r * 57.3))
            wax_stroke(L, pts, seed=11 + q, cap=True)
        bursts = []
        for b in burns:
            if b['hp_lost'] <= 0:
                continue
            u = uby(f_live, b['uid'])
            x, y = AU.token_pos(u)
            ta = math.degrees(math.atan2(x - C[0], -(y - C[1])))
            bx, by = ppx(C, math.hypot(x - C[0], y - C[1]), ta + 8.5)
            Z.pink_burst(L, bx, by, 17, u['id'])
            bursts.append(b)
        focus_col(L, sec, thick=True)
        got = V.bill_marks(L, f_live, f_plan, NOW['words'])
        return dict(bill_rings=got, burns=burns, legal_columns=legal)
    return make('h09', words, 'p1' if words else 'nowords', fb, f_plan, f_live, lit, marks, hand, 'Firewall',
                note='burns from the sim (hurt wrapped in the plan preview): %s' % burns)


# ================================================================================================ h10 soak toggle (no card)
def soak(words=True, idx=1):
    hand = H4
    f_live, f_plan = frames([], hand, opt=[idx])
    sec = [w['sector'] for w in f_plan['wheel'] if w['soak']][0]

    def lit(Lt):
        # the same slice hover as Brace (3.13): the soaked slice, the hub and the landings on it stay lit; the other five dim
        Lt.disc(T_IN + 1)
        Lt.sector(sec, T_IN - 2, T_HALO + 3, 30, 2)
        hit_ids = {it['u']['id'] for it in RA.layout_items(f_plan) if any((it['s0'] + q) % 6 == sec for q in range(it['u']['w']))}
        lit_arcs_of(Lt, f_plan, hit_ids or None)
        lit_bill(Lt)

    def marks(L):
        for s in range(6):
            if s != sec:
                focus_slice(L, s)
        focus_slice(L, sec, thick=True)
        got = V.bill_marks(L, f_live, f_plan, NOW['words'])
        yb = V.you_mark(L, f_live, f_plan)
        return dict(bill_rings=got, you_underline=yb, soak_sector=sec, soaked=f_plan['pv']['eq']['soaked'], lit='hub + soaked slice + its landings (3.13)')
    return make('h10', words, 'p1' if words else 'nowords', f_plan, f_plan, f_live, lit, marks, hand, None,
                note='END TURN soak on the slice at sector %d (sim option [%d]): THROUGH %d -> %d, HP after %d -> %d' % (
                    sec, idx, f_live['pv']['eq']['through'], f_plan['pv']['eq']['through'], f_live['pv']['hp_after'], f_plan['pv']['hp_after']))


# ================================================================================================ h11 unit hover (the kept p2b form, FOCUS and pencil fixed)
def unit(words=True):
    hand = H4
    f = copy.deepcopy(A.J['f1'])
    hv = A.J['hover']
    uid = hv['id']
    u = uby(f, uid)
    land = [h[0] for h in hv['fate']['hits']]
    path = hv['path']
    saved = {}

    def pre():
        # the board's own p2b route (a thin wax line) and cell bracket (a_kit lime, joined) are replaced: the route is the L5 arrowed outline in
        # pencil and the cell gets the four FOCUS corners (both drawn by marks below)
        saved['path'], saved['cell'] = A.H2.hover_path, A.H2.hover_cell
        A.H2.hover_path = lambda *a, **k: None
        A.H2.hover_cell = lambda *a, **k: None

    def post():
        A.H2.hover_path, A.H2.hover_cell = saved['path'], saved['cell']

    def lit(Lt):
        lit_cells(Lt, f, {uid})
        for s in land:
            Lt.sector(s, T_IN - 4, T_HALO + 2, 30, 2)
        for (d_, s_) in path:
            ri, ro = CB.ring_geom(d_)
            Lt.sector(s_, ri - 1, ro + 1, 30, 1)
        lit_arcs_of(Lt, f, {uid})
        lit_bill(Lt)
        tb = K.SNAP.get('hover_tag_box') or A.INFO.get('hover_tag_box')
        if tb:
            Lt.box(tb[0] - 4, tb[1] - 4, tb[2] + 4, tb[3] + 4, 8)
            Lt.line((tb[0] - 190, tb[1] + (tb[3] - tb[1]) * 0.5 + 60), (tb[0] + 6, tb[1] + (tb[3] - tb[1]) * 0.5), 16)

    def marks(L):
        pts = A.H2.path_pts(f)
        pc(L, pts, w=12, head=18, tail_dot=True)
        for s in land:
            pencil_arc(L, (T_HALO + CB.ring_geom(0)[0]) / 2.0, 60 * s - 25, 60 * s + 25, seed=s + 40)
        focus_cell(L, u, thick=True)
        return dict(route=path, lands_on=land)

    def top(L):
        if not words:
            Z.H2m.hover_tag_nowords(L, f)
    beat = 'p2b' if words else 'nowords'
    return make('h11', words, beat, f, f, f, lit, marks, hand, None, top_fn=top, assert_beat='p2b', hover_unit=uid, pre_board=pre, post_board=post,
                note='the p2b form: the board draws the cell, the dim and the tag (content parked, note 8); the route is the L5 pencil outline and '
                     'the cell has the four FOCUS corners')


PEN_OUT = V.PEN_W / 2 + V.PEN_INK + 0.5
BUILD = {'h01': spin, 'h02': brace, 'h03': trigger, 'h04': twist, 'h05': strike, 'h06': shove, 'h07': pull, 'h08': hold, 'h09': firewall, 'h10': soak, 'h11': unit}
NAMES = {'h01': 'h01_tower_turn', 'h02': 'h02_brace', 'h03': 'h03_trigger', 'h04': 'h04_twist', 'h05': 'h05_strike', 'h06': 'h06_shove', 'h07': 'h07_pull',
         'h08': 'h08_hold', 'h09': 'h09_firewall', 'h10': 'h10_soak', 'h11': 'h11_unit'}
