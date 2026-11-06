"""rb3_patch (2026-11-04, gate 1 of the 2026-11-03 rebuild): the items the independent gate failed or measured against the claims, installed by
lw_render right after rb2_patch (env RB3=0 skips it).  Every number is a named knob here or in rb_tokens.

  1.2   "HOT second under SEND IT": the enemy HP ticks (CREAM, L* 96), the sector digits (white, L* ~100) and the ring tags (ENAMEL type with a
        glow, L* 96) outranked the HOT chevrons.  HP ticks drop to CREAM_HP (L* 84, E mark), the digits, ring tags, W tags, ticket glyphs and
        nowords tallies to K_TYPE (L* 84, K type).  Ticket edges keep their time value (W6 50, W5 70, W4 100 %) on the K type.
  d     TURRET slice ink re-picked off BOSS_GOLD (rb_tokens), Solace porcelain off PAPER (rb_tokens)
  3.8   the BEST LINE chip and the BEST option chip: neutral (TEXT_HI type on the terminal plate, TEXT_MID edge) with a filled star;
        the selected option chip takes the neutral TEXT_HI selection edge.  PLAN yellow stays on pencil marks and the WITHOUT TWIST what-if row
  a     occupied glass +1 / +2 lifted and empty glass lowered so occupied / brightest empty cell >= 3 on every ring (was: vs the ring's mean empty)
  a     the dying unit (it dies at this END TURN) keeps its lit glass, so the gun tracers end on a cell that reads occupied; its loss is the L7
        cross-hatch in the cause colour (CELL_PINK: our guns) clipped to the cell with a solid 2 px edge (VISUAL_PLAN B, L7 "a dying unit's cell");
        its chevrons are dimmed (they will not land).  The 62 % gone veil is retired
  2.13  the Adjuster's HP track splits its two groups of five round the diamond plate, so no segment sits under the plate or the hit star
  3.11  the resolve log names the unit the Trigger kills from the state's own tlog (f2: trig_refund Packet); the hand-written prose said Payload
  1.2   HOT chevron core 3.2 px (was 2.8): HOT stays above COLD on peak value with the ring NOW glass lit"""
import math, sys, os
sys.dont_write_bytecode = True
import numpy as np
import rb_tokens as T

# ------------------------------------------------------------------ knobs
OCC_L = (44.5, 39.5, 34.5)          # occupied glass fill per ring (NOW, +1, +2), mean L* before the skin material (rb_patch had 44.5 / 38 / 32)
EMPTY_L = (19.5, 14.5, 11.0)        # empty glass fill per ring (rb_patch had 21 / 16 / 12)
HOT_CORE_W = 3.2                    # px (rb_patch 2.8)
DYING_CHEV_DIM = 0.55               # the dying unit's chevrons: mixed 55 % toward the bed (they will not land)
KILL_HATCH_PITCH = 8.5              # px between L7 lines (each direction)
KILL_HATCH_W = 1.6                  # px L7 line
KILL_HATCH_A = 150                  # alpha of the hatch lines over the glass (of 255)
KILL_EDGE_W = 2.0                   # the solid L7 edge round the dying cell
KILL_INSET = 3.0                    # px the hatch sits inside the cell outline
EMPTY_EDGE_MIX = 0.30               # empty cell edge: fill mixed this far toward ENAMEL (rb_patch 0.22; see _empty_edge)
KILL_POCKET_MIN = 0.55             # glass pockets between hatch lines smaller than this share of a whole diamond are filled (edge band)
ADJ_CLEAR = 5.0                     # px kept between an Adjuster HP segment and the diamond plate (ink + glow included)
ADJ_SEG, ADJ_GAP = 16.0, 1.6        # segment length and ink cut along the track (rb_patch 17 / 1.6)
BEST_STAR_R = 9.0                   # the BEST star (filled TEXT_HI, ink keyline)
SEL_EDGE_W = 3                      # the selected option chip's neutral edge
THI = (242, 246, 255)
TMID = (175, 192, 214)
INK = (12, 10, 22)
INFO = {}


def install(R, A, SKIN):
    import rb_patch as RBP
    RBP.OCC_L, RBP.EMPTY_L, RBP.HOT_CORE_W = OCC_L, EMPTY_L, HOT_CORE_W
    _hp_ticks()
    _digits(A)
    _ring_tags(A)
    _tickets()
    _best()
    _dying(A)
    _adjuster()
    _plan_yellow()
    _hit_star()
    _chain_log()
    _empty_edge()
    _e_structure()


# ======================================================================================== E structure: the armour rail edge at L* ~81
def _e_structure():
    """the armour rail's top edge (STEEL_HI #E2E9F6) is a thin bright line; after the LANCZOS downsample of the 2x layers it read L* 100 on the
    ring +1 tray, over the HOT marks.  It drops to STEEL_HI_E (L* ~81)."""
    import gram as G
    import wr2_lib as W2L
    import wr2_units as W2U
    import cv_lib as CVL
    import gramlib as GL
    import asm_units as AU
    # only the armour rail edge is changed: the enamel override (ENAMEL_E) was tried and changed none of the bright 1 px ring lines it was
    # aimed at (they are drawn elsewhere; final/NOTES.md "2026-11-04 gate 1", Not done), so it is not installed
    for m in (G, GL, W2U, W2L, AU):
        for nm in ('STEELC_HI', 'STEEL_HI'):
            if hasattr(m, nm):
                setattr(m, nm, T.STEEL_HI_E)


# ======================================================================================== empty cells: a fainter enamel edge
def _empty_edge():
    """rb_patch's empty cell edge is the fill mixed 22 % toward ENAMEL at 1.4 px.  With the empty glass lowered for check a, that 1 px line sits
    alone between the ring gap's ink and the dark glass, at the DoG threshold of dot_audit, and its anti-aliasing beaded into a five-dot run
    beside the hover-faded dying cell on p2b.  EMPTY_EDGE_MIX 0.30 lifts the edge clearly over the threshold, so it reads (and measures) as one
    continuous hairline everywhere; 0.14 (under it) beaded the edge on other empty cells instead.  Same polygon, same width, same helix motif."""
    import f1_board as FB
    import wr2_cells as W2C
    import gram_render as GR
    import rb_patch as RBP
    from wr_geo import cell_poly
    ENAMEL = (217, 225, 234)

    def empty_cell(L, dep, s):
        b0, b1 = 60 * s - 30, 60 * s + 30
        fill = RBP.at_lstar((38, 50, 70), RBP.EMPTY_L[dep])
        poly = cell_poly(dep, b0, b1, kind='empty')
        L.poly(poly, fill=fill + (255,))
        L.line(poly + [poly[0]], FB._mixc(fill, ENAMEL, EMPTY_EDGE_MIX), 1.4)
        FB.helix(L, None, fill, dep, b0, b1)
    FB.empty_cell = empty_cell
    W2C.empty_cell = empty_cell
    GR.W2C.empty_cell = empty_cell


# ======================================================================================== 1.2 enemy HP ticks: CREAM at L* 84
def _set_cream(c):
    import wr2_units as W2U
    import wr2_lib as W2L
    import gramlib as GL
    for m in (W2U, W2L, GL):
        for nm in ('CREAMC', 'CREAM'):
            if hasattr(m, nm):
                setattr(m, nm, c)


def _hp_ticks():
    _set_cream(T.CREAM_HP)
    # hover plates (p2b): the units not hovered are drawn on their own layer and faded to DIM_K alpha.  Their ticks are drawn in the full CREAM
    # (L* 96) so that, faded, they keep reading as solid segments (at CREAM_HP the faded tick split into two DoG peaks and three ticks read as a
    # six-dot row in dot_audit); faded, they sit at L* ~45, under every lit mark.
    import f1_render as F1
    _odu, _orr = F1.draw_units, F1._render
    st = {'hover': False}

    def _render(beat='p1', *a, **k):
        st['hover'] = beat == 'p2b' or k.get('hover_unit') is not None
        try:
            return _orr(beat, *a, **k)
        finally:
            st['hover'] = False

    def draw_units(L, f, beat, skip=None, only=None, *a, **k):
        if st['hover'] and skip is not None and only is None:
            _set_cream(T.CREAM_FADED)
            try:
                return _odu(L, f, beat, skip=skip, only=only, *a, **k)
            finally:
                _set_cream(T.CREAM_HP)
        return _odu(L, f, beat, skip=skip, only=only, *a, **k)
    F1._render, F1.draw_units = _render, draw_units


# ======================================================================================== 1.2 the sector digits: K type at L* 84
def _digits(A):
    S2 = A.S2
    _od = S2.digits

    def nowords_code(L, x, y, s):
        """words off: zero ring for sector 0, tallies 1-5 (same disc), in the K type"""
        if s == 0:
            L.ellipse([x - 5.8, y - 8.0, x + 5.8, y + 8.0], outline=T.K_TYPE, w=2.6)
        else:
            w, pitch, h = 2.8, 4.1, 13.0
            x0 = x - (s - 1) * pitch / 2
            for i in range(s):
                xx = x0 + i * pitch
                L.rect([xx - w / 2 - 0.8, y - h / 2 - 0.8, xx + w / 2 + 0.8, y + h / 2 + 0.8], fill=INK, r=1)
                L.rect([xx - w / 2, y - h / 2, xx + w / 2, y + h / 2], fill=T.K_TYPE, r=1)
    S2.nowords_code = nowords_code

    def digits(L, opt):
        old = S2.WHITE
        S2.WHITE = T.K_TYPE
        try:
            return _od(L, opt)
        finally:
            S2.WHITE = old
    S2.digits = digits


# ======================================================================================== 1.2 ring tags: K type at L* 84 (graded per ring), no glow
def _ring_tags(A):
    import f1_board as FB
    import r2_misc as M2
    import gram_render as GR
    from cv_lib import NOW
    K = T.K_TYPE

    def ring_tags(L, f, opt):
        for d in range(3):
            w_ = f['rings_wave'][d]
            x, y, wd, depth, wv = M2.tag_geom(L, d, w_, opt)
            box = [x - wd / 2, y - 13, x + wd / 2, y + 13]
            if not NOW['words']:
                L.rect(box, fill=(8, 10, 18, 250), outline=INK, w=2.4, r=6)
                M2.lane_swatch(L, x - 16, x + 16, y - 5, d)
                if w_ >= 0:
                    M2.tally_bars(L, x, y + 6, w_ + 1, FB.grade2(K, d), h=8, pitch=5.4, w=2.6)
                continue
            c = FB.grade2(K, d)
            L.rect(box, fill=(8, 10, 18, 250), outline=INK, w=5.0, r=6)
            L.rect(box, outline=c, w=(2.6, 1.8, 1.4)[d], r=6)
            tx0 = x - wd / 2 + 9
            if depth.startswith('+'):
                FB.OM.plus_glyph(L, tx0 + 3, y, c, 4.2, 2.4)
                tx0 += 10
                txt = depth[1:] + ((' ' + wv) if wv else '')
            else:
                txt = depth + ((' ' + wv) if wv else '')
            L.text((tx0, y + 1), txt, 20, 'anton', fill=c, anchor='lm', stroke=1.4)
            if d == 0:
                FB.end_notch(L, box[0] - 9, y, 90, col=c, s=5.2)
            else:
                for i in range(d):
                    xx = box[0] - 8 - 10 * i
                    L.ellipse([xx - 4.6, y - 4.6, xx + 4.6, y + 4.6], fill=INK)
                    L.ellipse([xx - 3.0, y - 3.0, xx + 3.0, y + 3.0], fill=TMID)
    M2.ring_tags = ring_tags
    GR.A.M2.ring_tags = ring_tags
    A.M2.ring_tags = ring_tags


# ======================================================================================== 1.2 wave tickets: glyphs, W tag and bars in the K type
def _tickets():
    import f1_board as FB
    import r2_glyphs as RG
    import rb2_patch as RB2
    import rb_patch as RBP
    from gram import INK as GINK, TMID as GTMID, BED, SCHED as GSCHED
    from cv_lib import NOW
    K = T.K_TYPE

    def queue_tickets(L, f, arcs):
        fut = [a for a in arcs if a['state'] == 'future']
        order = list(reversed(fut))
        x, y0 = 24, 24
        tw_, th_ = RB2.TICKET_W, RB2.TICKET_H
        vals = {0: 1.0, 1: 0.70, 2: 0.50}
        for i, a in enumerate(order):
            n = a['wave'] + 1
            j = len(order) - 1 - i
            val = vals.get(j, 0.5)
            sc = lambda c: tuple(int(BED[q] + (c[q] - BED[q]) * val) for q in range(3))
            box = [x, y0, x + tw_, y0 + th_]
            FB.ticket(L, box, sc(K), bool(a.get('climax')))                   # time: the ticket edge value (W6 50, W5 70, W4 100 %) + turn pips
            if NOW['words']:
                L.text((x + 8, y0 + RB2.TICKET_TAG_Y), 'W%d' % n, RBP.TICKET_TXT, 'mono', fill=K, anchor='lm')
            units = a['units']
            slot = (tw_ - 10) / max(1, len(units))
            for ui, (kind, wd) in enumerate(units):
                cx = x + 5 + slot * ui + slot / 2
                RG.kind_glyph(L, kind, RB2.TICKET_GLYPH_PX, (cx, y0 + RB2.TICKET_GLYPH_Y), K)
                bw = 4
                bx0 = cx - (wd * bw + (wd - 1) * 1.6) / 2
                for b in range(wd):
                    L.rect([bx0 + b * (bw + 1.6), y0 + RB2.TICKET_BAR_Y, bx0 + b * (bw + 1.6) + bw, y0 + RB2.TICKET_BAR_Y + 3.4], fill=K + (255,), r=1)
            for p in range(j):
                px = x + tw_ - 12 - p * 10
                L.ellipse([px - 4.6, y0 + RB2.TICKET_TAG_Y - 4.6, px + 4.6, y0 + RB2.TICKET_TAG_Y + 4.6], fill=GINK)
                L.ellipse([px - 3.0, y0 + RB2.TICKET_TAG_Y - 3.0, px + 3.0, y0 + RB2.TICKET_TAG_Y + 3.0], fill=GTMID)
            if a.get('climax'):
                for t in range(3):
                    bx = x + 9 + t * 9
                    L.poly([(bx, y0 + th_ - 3), (bx + 4, y0 + th_ - 3), (bx + 7, y0 + th_ - 8.5), (bx + 3, y0 + th_ - 8.5)], fill=GSCHED, outline=INK, w=1.0)
            x += tw_ + 8
        return x
    FB.queue_tickets = queue_tickets


# ======================================================================================== 3.8 BEST: a neutral chip with a star
def star_pts(x, y, r, k=0.45):
    return [(x + (r if i % 2 == 0 else r * k) * math.cos(math.radians(-90 + 36 * i)), y + (r if i % 2 == 0 else r * k) * math.sin(math.radians(-90 + 36 * i))) for i in range(10)]


def best_star(L, x, y, r=BEST_STAR_R):
    """the BEST mark: a filled TEXT_HI five-point star with an ink keyline (the objectives' challenge stars are hollow outlines)"""
    L.poly(star_pts(x, y + 0.5, r + 2.2), fill=INK + (255,))
    L.poly(star_pts(x, y + 0.5, r), fill=THI + (255,))


def _best():
    import hud2 as H

    def el_best_tag(L, y, txtm='BEST LINE'):
        """best_line_tag (3.8): neutral terminal chip, TEXT_MID edge, a filled star then the words in TEXT_HI; never PLAN yellow"""
        xr = H.G['px1'] - 20
        w = H.ttw(L, txtm, H.LBL_PX, 'mono', H.LBL_TRK)
        x0 = xr - w - 20 - 2 * BEST_STAR_R - 8
        L.rect([x0, y + 6, xr, y + 30], fill=(10, 16, 28, 245), outline=TMID, w=1.8, r=6)
        best_star(L, x0 + 10 + BEST_STAR_R, y + 18)
        H.txt(L, xr - 10 - w, y + 18, txtm, H.LBL_PX, THI, 'mono', 'lm', H.LBL_TRK)
        H.reg('best_line_tag', (x0 - 8, y, xr + 8, y + 38))
    H.el_best_tag = el_best_tag

    def chip_name(L, x, cy, name):
        """option_name_label: TEXT_MID; the BEST line gets the filled star and its name in TEXT_HI (no PLAN yellow)"""
        if name.startswith('BEST: '):
            best_star(L, x + BEST_STAR_R, cy)
            xx = x + 2 * BEST_STAR_R + 8
            w = H.txt(L, xx, cy, 'BEST: ', H.LBL_PX, THI, 'mono', 'lm', H.LBL_TRK)
            H.txt(L, xx + w + 1, cy, name[6:], H.LBL_PX, THI, 'mono', 'lm', H.LBL_TRK)
        else:
            H.txt(L, x, cy, name, H.LBL_PX, H.TMID, 'mono', 'lm', H.LBL_TRK)
    H.chip_name = chip_name

    def option_chip(L, y, name, plan, soak, eq, sel=False, refund=False):
        h = H.G['chip_h']
        H.P(L, (H.G['px0'], y, H.G['px1'], y + h), 'chip', sel, col=THI if sel else None, w=SEL_EDGE_W if sel else None)
        cy = y + h / 2
        ox = H.G['ox']
        H.chip_glyphs(L, ox + 12, cy, plan, soak, refund)
        H.chip_name(L, ox + 196, cy, name)
        H.chip_bar(L, ox + H.CHIP_BAR_DX, cy, eq)
        H.chip_pair(L, cy, eq)
        return y + h + H.G['chip_gap']
    H.option_chip = option_chip


# ======================================================================================== a: the dying unit keeps its lit glass; L7 pink hatch
def kill_hatch(L, u):
    """L7 cross-hatch in the cause colour (CELL_PINK: our guns kill it at this END TURN) clipped to the unit's cell, with a solid 2 px edge"""
    from cv_lib import L2
    from wr_geo import cell_poly, unit_bounds
    from PIL import Image, ImageDraw
    PINK = T.TOKENS['CELL_PINK']
    b0, b1 = unit_bounds(u)
    poly = cell_poly(u['dep'], b0, b1, kind='unit')
    inner = cell_poly(u['dep'], b0, b1, KILL_INSET, KILL_INSET, kind='unit', tin=KILL_INSET)
    k = L.k
    W, H_ = L.im.size
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    x0, y0, x1, y1 = int(min(xs)) - 4, int(min(ys)) - 4, int(max(xs)) + 5, int(max(ys)) + 5
    w, h = (x1 - x0) * k, (y1 - y0) * k
    lines = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(lines)
    step = KILL_HATCH_PITCH * k
    span = w + h
    t = -span
    while t < span:
        d.line([(t, 0), (t + h, h)], fill=255, width=max(1, int(round(KILL_HATCH_W * k))))
        d.line([(t + h, 0), (t, h)], fill=255, width=max(1, int(round(KILL_HATCH_W * k))))
        t += step
    clip = Image.new('L', (w, h), 0)
    ImageDraw.Draw(clip).polygon([((x - x0) * k, (y - y0) * k) for x, y in inner], fill=255)
    ln = np.asarray(lines, np.float32) / 255.0
    cl = np.asarray(clip, np.float32) / 255.0
    # the glass pockets the clip cuts small along the cell edge read as a row of dots at 1x (dot_audit on the hover-faded p2b): every pocket
    # under KILL_POCKET_MIN of a whole diamond is filled with the hatch, so the edge reads as one L7 band
    from scipy import ndimage as _ndi
    glass = (cl > 0.5) & (ln < 0.5)
    lab, n = _ndi.label(glass)
    if n:
        ar = _ndi.sum(glass, lab, range(1, n + 1))
        full = float(np.percentile(ar, 90))
        small = np.zeros(n + 1, bool)
        small[1:] = ar < KILL_POCKET_MIN * full
        ln = np.maximum(ln, small[lab].astype(np.float32))
    a = ln * cl * KILL_HATCH_A
    lay = Image.new('RGBA', (w, h), PINK + (0,))
    lay.putalpha(Image.fromarray(a.astype(np.uint8), 'L'))
    L.im.alpha_composite(lay, (x0 * k, y0 * k))
    Tl = L2(k)
    Tl.line(inner + [inner[0]], PINK + (230,), KILL_EDGE_W)
    L.im.alpha_composite(Tl.im)


def _dying(A):
    import asm_units as AU
    import wr2_units as W2U
    _odu = AU.draw_unit

    def draw_unit(L, u, f, beat):
        if u['fate']['kind'] != 'dies':
            return _odu(L, u, f, beat)
        AU.CTX['f'] = f
        AU.CTX['nchev'] = u['hit']
        W2U.chevrons(L, u, u['hit'], 0, dim=DYING_CHEV_DIM)
        W2U.outline(L, u)
        kill_hatch(L, u)
        W2U.hp_row(L, u, u['hp'], u['mx'], lose=u['lose'][1], shield=u['sh'], shmx=u['shmx'])
        if u['df'] == 'armor':
            W2U.armour_rails(L, u)
        AU.token(L, u)
    AU.draw_unit = draw_unit
    A.AU.draw_unit = draw_unit
    _ow = W2U.draw_unit

    def w2_draw_unit(L, u, f, beat):
        if u['fate']['kind'] != 'dies':
            return _ow(L, u, f, beat)
        if u['warded']:
            W2U.warded(L, u)
        W2U.chevrons(L, u, u['hit'], 0, dim=DYING_CHEV_DIM)
        W2U.outline(L, u)
        kill_hatch(L, u)
        W2U.hp_row(L, u, u['hp'], u['mx'], lose=u['lose'][1], shield=u['sh'], shmx=u['shmx'])
        if u['df'] == 'armor':
            W2U.armour_rails(L, u)
        W2U.token(L, u)
        W2U.dead_badge(L, u)
    W2U.draw_unit = w2_draw_unit


# ======================================================================================== 2.13 the Adjuster's HP clears its diamond plate
def _adjuster():
    import wr2_boss as W2B
    import gramlib as GL
    import wr2_units as W2U
    import cv_board as CB
    from wr_geo import radial_ext
    from cv_lib import C, ppx
    from wr2_lib import INKC
    import rb_patch as RBP
    GOLD = T.BOSS_GOLD
    DIA_R = 36.0 + 5.0 + 3.0                    # wr2_boss.diamond: half-diagonal 36, ink 10 px wide (5 outside), glow 3

    def inside_diamond(x, y, cx, cy, pad):
        return abs(x - cx) + abs(y - cy) <= DIA_R + pad * math.sqrt(2)

    def hp_bar(L, a, ang):
        """the solid gold HP edge (rb_patch), its two groups of five placed either side of the diamond plate (gate 1: the plate and the gun's hit
        star hid about 2.5 of the 10 segments)"""
        n = a['mx']
        ha = a.get('hp_after', a['hp'])
        ra, rb = radial_ext(a['ring'])
        r1 = rb - 1.5 - 4.5
        r0 = r1 - RBP.BOSS_SEG_H
        rm = (r0 + r1) / 2
        ri, ro = CB.ring_geom(min(a['ring'], 2))
        cx, cy = ppx(C, (ri + ro) / 2 - 3, ang)
        # the diamond's angular extent on the track (inner and outer track edge, plus the clearance)
        da = 0.0
        while da < 40:
            if not any(inside_diamond(*ppx(C, rr, ang + da), cx, cy, ADJ_CLEAR) or inside_diamond(*ppx(C, rr, ang - da), cx, cy, ADJ_CLEAR)
                       for rr in (r0 - 1.6, rm, r1 + 1.6)):
                break
            da += 0.1
        half = n // 2
        pos = []
        # group 1 runs counter-clockwise from the diamond's near edge, group 2 clockwise; HP index 0 is the first segment of group 1 (far end)
        a_lo = ang - da
        a_hi = ang + da
        g1 = []
        x = 0.0
        for i in range(half):
            e = a_lo - math.degrees(x / rm)
            s = e - math.degrees(ADJ_SEG / rm)
            g1.append((s, e))
            x += ADJ_SEG + ADJ_GAP
        g1.reverse()
        g2 = []
        x = 0.0
        for i in range(n - half):
            s = a_hi + math.degrees(x / rm)
            g2.append((s, s + math.degrees(ADJ_SEG / rm)))
            x += ADJ_SEG + ADJ_GAP
        pos = g1 + g2
        INFO['adj_track'] = dict(diamond_half_deg=round(da, 2), first=round(pos[0][0], 2), last=round(pos[-1][1], 2), cell=(ang - 30, ang + 30))
        for grp in (g1, g2):
            band = W2U.arc_band(r0 - 1.6, r1 + 1.6, grp[0][0] - math.degrees(1.6 / rm), grp[-1][1] + math.degrees(1.6 / rm))
            L.poly(band, fill=INKC + (255,))
        for i, (p0, p1) in enumerate(pos):
            core = W2U.arc_band(r0, r1, p0, p1)
            if i >= a['hp']:
                L.poly(core, fill=(14, 16, 30, 255))
            elif i >= ha:
                rad = 1.0
                core2 = W2U.arc_band(r0 + rad, r1 - rad, p0 + math.degrees(rad / rm), p1 - math.degrees(rad / rm))
                GL.seg_shape(L, core2, rad, 'ours', ink_w=0.8, pitch=4.2, lw=1.4, glow=False)
            else:
                L.poly(core, fill=GOLD + (255,))
        for grp, idx in ((g1, range(0, half)), (g2, range(half, n))):
            kept = [i for i in idx if i < ha]
            if kept:
                L.line(L.arc_pts(C, r1 - 1.6, pos[kept[0]][0] + 0.3, pos[kept[-1]][1] - 0.3, 30), T.BOSS_GOLD_HI, 1.0)
    W2B.hp_bar = hp_bar

    import wr_units as WU
    import rb_patch as RBP_

    def diamond(L, a, ang):
        """wr2_boss.diamond with E-mark values (1.2): the skull is the unit-glyph value (rb_patch.TOKEN_GLYPH, L* 83, not white) and the inner
        edge is BOSS_GOLD_HI (not the pale gold #FFE278, L* 91): no E mark outranks the tower"""
        ri, ro = CB.ring_geom(min(a['ring'], 2))
        x, y = ppx(C, (ri + ro) / 2 - 3, ang)
        k = L.k
        Rr = 36
        L.glow(lambda dd: dd.polygon([((x) * k, (y - Rr - 3) * k), ((x + Rr + 3) * k, y * k), (x * k, (y + Rr + 3) * k), ((x - Rr - 3) * k, y * k)], fill=(12, 10, 22, 191)), blur=4)
        dia = [(x, y - Rr), (x + Rr, y), (x, y + Rr), (x - Rr, y)]
        L.poly(dia, fill=(52, 40, 10, 255), outline=INKC, w=10)
        L.poly(dia, fill=None, outline=GOLD, w=5)
        r2 = Rr - 9
        L.poly([(x, y - r2), (x + r2, y), (x, y + r2), (x - r2, y)], fill=None, outline=T.BOSS_GOLD_HI, w=2.4)
        WU.gly(L, 'X_SKULL', 24, (x, y + 0.5), RBP_.TOKEN_GLYPH)
    W2B.diamond = diamond


# ======================================================================================== the twist badge in PLAN yellow (it was pure #FFFF00)
def _plan_yellow():
    """the twist badge is a N plan mark: PLAN yellow at PLAN_BADGE_V value (its outline edge read L* 97 at full PLAN, over the HOT p95).  The
    other pencil marks keep full PLAN (p99 90-91)."""
    import a2_plan as P2
    P2.YEL = T.TOKENS['PLAN']
    _otb = P2.twist_badge

    def twist_badge(L, f, opt='A'):
        old = P2.YEL
        P2.YEL = tuple(int(round(c * T.PLAN_BADGE_V)) for c in T.TOKENS['PLAN'])
        try:
            return _otb(L, f, opt)
        finally:
            P2.YEL = old
    P2.twist_badge = twist_badge


# ======================================================================================== the gun hit star: HIT_PAPER, not white
def _hit_star():
    """the gun hit star (xf_guns.burst, installed over f1_guns.make_guns by lw_render) is filled with PAPERC #FBFAF4 (L* 98), the brightest
    pixel on the board after SEND IT; the tracer's highlight uses the same paper at 55 %.  It is a P mark (our guns): HIT_PAPER (L* 86) keeps
    it the loudest thing on its cell and under the HOT marks (VISUAL_PLAN A.1)."""
    import f1_guns as G
    import xf_guns as XG
    G.WHITE = T.HIT_PAPER
    XG.PAPERC = T.HIT_PAPER


# ======================================================================================== 3.11 the resolve log names the unit the Trigger kills
def _chain_log():
    import hud2 as H
    _ocs = H.chain_strip

    def fix(f):
        kills = [e[1] for e in f.get('tlog', []) if e and e[0] == 'trig_refund']
        if not kills:
            return f['chain']
        out = []
        for st in f['chain']:
            st = dict(st)
            if st['name'] == 'TRIGGER':
                pips = []
                for k_, n in st['pips']:
                    if k_ == 'txt' and str(n).endswith('dead: refund'):
                        new = '%s dead: refund' % kills[0]
                        if new != n:
                            INFO.setdefault('chain_fix', []).append(dict(was=n, now=new, source='tlog trig_refund'))
                        n = new
                    pips.append((k_, n))
                st['pips'] = pips
            out.append(st)
        return out

    def chain_strip(L, f, y):
        f2 = dict(f)
        f2['chain'] = fix(f)
        return _ocs(L, f2, y)
    H.chain_strip = chain_strip
