"""rb_patch (2026-11-03 rebuild): the IMPL fixes from locked/REVIEW_RESPONSE.md, installed by lw_render after every other layer (env RB=0 skips it).

  1.1        enemy cells: occupied glass lifted to its own value (ring NOW L* 44, +1 37, +2 31) with a programme screen (inset frosted panel + enamel
             frame); empty glass L* 21 / 16 / 12; HP ticks 9.5 px tall (were 7.5); the lit span is the width read, interior sector rules kept
  1.2 + 2.9  the K clock is one machined gunmetal (median L* 45-55): THIS TURN cell, HOLD plates and +N plates; SCHEDULE orange only on the live
             step (edge, L5 chevrons, glow); the tape remap to silver is retired.  HOT chevrons get a white-hot core (L9) so they rank second only
             to SEND IT.  Token glyphs are capped (L* 83) below the HOT marks.  Resting hand at 0.85 value, the lifted card at 0.93
  2.15       tower slice inks at L* 60-72 (rb_tokens.SLICE_INK, own colour + texture per slice type, DR-4 / DR-7); paper sliver and stencil
             highlight capped with them; the icon discs (seat + glyph) carry the peak; O-28 seats kept
  1.3 + 1.4  corp skins: neutral slate cell fills with a low-chroma tint; the corp hue only on the rim, bezel lip, crest and cell edges
             (rb_tokens.SKIN_INKS, dE >= 15 from Cell lime / GAIN / FOCUS / HARM); Meridian's orange is container rust, off SCHEDULE
  1.8        kill marks and kill ghosts in the cause colour (CELL_PINK: our kills), never GAIN
  2.12       FAR landing marks carry their number (hit count before the chevrons, HP-through count after the diamonds)
  2.13       Adjuster: a solid gold HP edge (square segments cut by ink, no beads), no white slash; the one HP it loses this END TURN is the
             L7 cross-hatch in the cause colour (pink), the only hatch on the boss
  BOSS_GOLD  re-picked (rb_tokens): #FFC428 failed the palette check against CRT_AMBER and RESIST_GOLD
  text       every text this board draws is >= 16 px cap height (bezel labels, ticket tags, hub name, hint line, nameplate)"""
import math, sys, os
sys.dont_write_bytecode = True
import numpy as np
import rb_tokens as T

HERE = 'D:/rc_scratch/combat_redesign/locked/corp/'
CACHE = HERE + 'work/rb_cache/'

# ------------------------------------------------------------------ knobs (value targets are in rb_tokens)
OCC_L = (44.5, 38.0, 32.0)          # occupied glass fill, mean L* per ring (NOW, +1, +2), before the skin's material
OCC_GRAD = (0.80, 1.14)             # luminance factor inner edge -> outer edge across the cell (the glass bowl)
SCREEN_LIFT = 1.10                  # the programme screen panel: luminance over the glass
SCREEN_INSET = 6.0                  # px
EMPTY_L = (21.0, 16.0, 12.0)        # empty glass fill, L* per ring
SKIN_UNIT_K = 0.30                  # strength of the skin's cell material on occupied glass (the material shows, the value stays)
SKIN_EMPTY_K = 0.80                 # ... and on empty glass
PIP_H = 9.5                         # enemy HP tick height (was 7.5)
TOKEN_GLYPH = (200, 206, 216)       # unit glyph on the token (L* ~83, below the HOT marks)
HOT_CORE_W = 2.8                    # px, the white-hot core in a HOT chevron
GUN_FILL = (110, 117, 128)          # K clock gunmetal (L* ~49)
GUN_LIGHT = (150, 158, 170)         # engraved highlight
GUN_GROOVE = (40, 44, 52)
SCHED = T.TOKENS['SCHEDULE']
BEZEL_TXT = 23                      # px mono on the bezel: cap 16.1
HOLD_CELL_DEG = 40.0                # a hold cell's arc (r2_sched.labels)
LABEL_LOG = []                      # (text, start deg, end deg, track, clear of every digit) per bezel label
LABEL_TRACKS = (1.0, 0.96, 0.92, 0.88)     # mono advance factors tried in order when a label does not fit between the digits
LABEL_DIGIT_MARGIN = 2.0            # px kept between a label and a digit boss's punched hole
LABEL_END_MARGIN = 2.0              # px kept before a hold cell's far end
TICKET_TXT = 23
HUB_TXT = 19.0                      # px Anton for the hub name: cap 16.3
HINT_TXT = 23
NAME_SUB_TXT = 23
REST_V = 0.82                       # the resting hand's value
LIFT_V = 0.92                       # the lifted card's value
LIFT_DX, LIFT_CY2, LIFT_PUSH = -28, 832, 16     # p2 lift layout (rb_lift.py search: 0 px on sibling cost hex / rules line, buttons, r455)
TW_SLIVER_V = 0.70                  # paper sliver and stencil highlight inside a wedge (L* ~71)
TW_SEAT_PAPER_V = 0.90
TW_GLYPH_V = 0.92                   # the icon glyph: the tower's peak
TW_HUB_V = 0.90
FAR_NUM_PX = 19.0                   # Anton digit on FAR landing marks (cap 16.3)
BOSS_SEG_H = 12.0                   # Adjuster HP track height (two-direction hatch needs >= 12)
HUD_LBL_PX = 23                     # every HUD word (bill, chips, chain, objectives, resources), mono: cap 16.1 (was 18: cap 12.6)
HUD_LBL_TRK = 0.02                  # its tracking (was 0.08 at 18): the rows keep their width
HUD_SPLIT = (131, 151, 22, 17)      # split row: label y, tally y (were 133 / 150), gap after a route (28), '+' offset (21)
HUD_TW_XMIN_GAP = 22                # WITHOUT TWIST: min gap after the NEXT tallies (was 40)
HUD_CHIP_BAR_DX = 456               # option chip outcome bar x (was 444)
HUD_OBJ_MIN_GAP = 22                # objectives row wraps to its 2 x 2 grid below this gap per challenge
HOVER_TAG_Y0, HOVER_TAG_GAP = 404, 20      # hover tag top: the old fixed y, or the HUD bottom + this gap when the HUD is taller
_A = None
HUD_WIN_PX = 23                     # WIN (was 22: cap 15.4)
HUD_CHAIN_H = 30                    # chain strip row pitch (was 23)
REFUND_PX, REFUND_W, REFUND_H = 23, 104, 30     # the REFUND tag on the board


def _lin(c):
    c = np.asarray(c, np.float64) / 255.0
    return np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)


def _srgb(l):
    l = np.clip(l, 0, 1)
    return tuple(int(round(v * 255)) for v in np.where(l > 0.0031308, 1.055 * l ** (1 / 2.4) - 0.055, 12.92 * l))


def at_lstar(col, L):
    """the colour with its hue and saturation kept and its luminance set to L* (linear-light scaling, clipped)"""
    l = _lin(col)
    y = 0.2126 * l[0] + 0.7152 * l[1] + 0.0722 * l[2]
    yt = float(T.y_of_lstar(L))
    return _srgb(l * (yt / max(y, 1e-6)))


def scale_y(col, k):
    l = _lin(col)
    return _srgb(l * k)


def install(R, A, SKIN):
    os.makedirs(CACHE, exist_ok=True)
    R.WORK = CACHE                          # tower cache: the rebuild's own (the tower changed)
    _boss_gold()
    _tower()
    _cells(R, A)
    _units(A)
    _hot(A)
    _clock(A)
    _kills(A)
    _far_numbers(A)
    _adjuster(A)
    _skins()
    _hand(R)
    _text()
    global _A
    _A = A
    _hud()


# ======================================================================================== HUD words >= 16 px cap (1.5, 3.6 size, 3.11)
def _hud():
    import hud2 as H2
    import obj2 as O2
    import a2_plan as P2
    H2.LBL_PX, H2.LBL_TRK = HUD_LBL_PX, HUD_LBL_TRK
    O2.LBL_PX, O2.WIN_PX, O2.TRK = HUD_LBL_PX, HUD_WIN_PX, HUD_LBL_TRK
    H2.G['chain_h'] = HUD_CHAIN_H
    H2.SPLIT_LY, H2.SPLIT_YY, H2.SPLIT_GAP, H2.SPLIT_OP = HUD_SPLIT
    H2.TW_XMIN_GAP, H2.CHIP_BAR_DX = HUD_TW_XMIN_GAP, HUD_CHIP_BAR_DX
    O2.OBJ_MIN_GAP = HUD_OBJ_MIN_GAP
    # the hover tag (parked content, E10 form) sat at a fixed y 404 "under the HUD bottom"; the HUD is taller now, so it follows the HUD bottom
    import a2_hover as H2V
    _oht, _ohtn = H2V.hover_tag, H2V.hover_tag_nowords

    def _tag_y():
        hb = _A.INFO.get('hud_bottom')
        H2V.TAG_Y0 = max(HOVER_TAG_Y0, int(math.ceil(hb)) + HOVER_TAG_GAP) if hb else HOVER_TAG_Y0

    def hover_tag(L, f, opt='A', bottom=944):
        _tag_y()
        return _oht(L, f, opt, bottom)

    def hover_tag_nowords(L, f, bottom=944):
        _tag_y()
        return _ohtn(L, f, bottom)
    H2V.hover_tag, H2V.hover_tag_nowords = hover_tag, hover_tag_nowords
    P2.REFUND_PX, P2.REFUND_W, P2.REFUND_H = REFUND_PX, REFUND_W, REFUND_H


# ======================================================================================== BOSS_GOLD
def _boss_gold():
    old = T.BOSS_GOLD_OLD
    new = T.BOSS_GOLD
    src = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/').lower()
    for m in list(sys.modules.values()):
        f = getattr(m, '__file__', None)
        if not f or not f.replace('\\', '/').lower().startswith(src):
            continue
        for k, v in list(vars(m).items()):
            if isinstance(v, tuple) and len(v) in (3, 4) and tuple(v[:3]) == old:
                setattr(m, k, tuple(new) + tuple(v[3:]))


# ======================================================================================== 2.15 tower
def _tower():
    import lw_tower as LT
    import xf_slices as XS
    from xf_gfx import ink, grow, shrink, shift, extrude, rough, poly, blur, toner_noise, MAG, TONER, plate_shift
    from scipy import ndimage as ndi
    from f1_lib import pol
    WHITE_ = LT.WHITE_
    f01 = lambda c: np.array(c, np.float32) / 255.0
    _opal = XS.palette

    def palette(var, t):
        if var == 'A' and t in T.SLICE_INK:
            return f01(T.SLICE_INK[t]), f01(T.SLICE_TEX[t]), XS.PAL['A'][t]['op']
        return _opal(var, t)
    XS.palette = palette
    LT.FILL_K = 1.0

    def draw_wedge(cv, w, seed):
        ss = cv.ss
        s = w['sector']
        am = 60 * s
        m = LT.wedge_mask(cv, s, seed)
        kb = grow(m, LT.KEY_W * ss)
        cv.paint(extrude(kb, 3.6 * ss, 4.4 * ss), TONER)
        cv.paint(kb, TONER)
        cv.paint(m, WHITE_ * TW_SLIVER_V)                                    # the paper sliver, capped with the inks
        fillc, texc, texop = XS.palette('A', w['t'])
        mg = np.clip(shift(m, -2.8 * ss, -2.3 * ss) * grow(m, 1.6 * ss), 0, 1)
        ink(cv, mg, fillc * LT.FILL_K, 0.11, seed + 21)
        ic = pol(LT.CT, LT.ICON_R, am)
        X, Y = cv.grid()
        to_icon = np.hypot(X - ic[0], Y - ic[1])
        tx = LT.texture(LT.TEXKIND[w['t']], cv, am, ic)
        tx = tx * np.clip((to_icon - (LT.SEAT_KEY + 2.5)) / 5.0, 0, 1) * shrink(mg * m, 3.6 * ss)
        ink(cv, tx, texc, 0.04, seed + 22, min(1.0, texop * LT.TEX_K))
        hl = np.clip(m - shift(m, 4.6 * ss, 5.0 * ss), 0, 1) * mg
        hl = hl * np.clip((to_icon - (LT.SEAT_KEY + 2)) / 6.0, 0, 1)
        cv.paint(rough(hl, cv, 0.4, 5.0, seed + 23), WHITE_ * TW_SLIVER_V, 0.92)
        return m
    LT.draw_wedge = draw_wedge

    def draw_seat(cv, w, seed):
        ss = cv.ss
        am = 60 * w['sector']
        ic = pol(LT.CT, LT.ICON_R, am)
        rng = np.random.default_rng(seed + 400 + w['sector'])
        fillc, texc, _ = XS.palette('A', w['t'])
        key = poly(cv, LT.jag_ring(ic, LT.SEAT_KEY, rng, (6, 10), 0.5))
        pap = poly(cv, LT.jag_ring(ic, LT.SEAT_PAPER, rng, (6, 10), 0.45))
        dsc = poly(cv, LT.jag_ring((ic[0] - 0.8, ic[1] - 0.7), LT.SEAT_R, rng, (6, 10), 0.35))
        cv.paint(extrude(key, 2.4 * ss, 2.8 * ss), TONER)
        cv.paint(key, TONER)
        cv.paint(pap, WHITE_ * TW_SEAT_PAPER_V)
        ink(cv, dsc, fillc, 0.05, seed + 41 + w['sector'])
        inner = shrink(dsc, 1.0 * ss)
        cv.paint(np.clip(inner - shift(inner, -2.6 * ss, -2.4 * ss), 0, 1) * inner, texc, 0.55)
    LT.draw_seat = draw_seat

    def draw_icon(cv, w):
        ss = cv.ss
        am = 60 * w['sector']
        c = pol(LT.CT, LT.ICON_R, am)
        white, dark = LT.icon_masks(w, ss)
        n = white.shape[0]
        x0, y0 = int(round(c[0] * ss - n / 2)), int(round(c[1] * ss - n / 2))
        wm = np.clip((ndi.gaussian_filter(white, 0.5 * ss * 0.5) - 0.45) * 6, 0, 1)
        from xf_gfx import to_cv_array
        wf = to_cv_array(cv, wm, x0, y0)
        df = to_cv_array(cv, np.clip(dark, 0, 1), x0, y0)
        full = np.clip(wf + df, 0, 1)
        cv.paint(extrude(grow(full, 1.6 * ss), 2.0 * ss, 2.2 * ss), TONER)
        cv.paint(grow(full, 1.8 * ss), TONER)
        if df.max() > 0:
            cv.paint(df, TONER)
            hf = LT.hatch_cached(cv, (45,), 3.0, 0.8, 5)
            cv.paint(hf * df, LT.SHEET, 0.5)
        cv.paint(wf, WHITE_ * TW_GLYPH_V)
        return full
    LT.draw_icon = draw_icon

    def draw_hub(cv, name='BREAKER', seed=0):
        """the hub: pink starburst, key, paper disc, a smaller bolt above and ONE name tile big enough for a 16 px cap"""
        from xf_gfx import xtext, ANTON
        ss = cv.ss
        c = LT.CT
        rng = np.random.default_rng(seed + 5)
        pts = []
        n = 13
        for k in range(n * 2):
            rr = (LT.R_HUB - 0.2) if k % 2 == 0 else (LT.R_HUB - 6.2)
            rr *= 1 + rng.uniform(-0.03, 0.03)
            a = math.radians(k * 180.0 / n + 3)
            pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
        burst = poly(cv, pts)
        cv.paint(grow(burst, 2.6 * ss), TONER)
        ink(cv, plate_shift(burst, cv, -2.6, -2.2), MAG, 0.06, seed + 2)
        disc = poly(cv, LT.jag_ring(c, 36.6, rng, (6, 10), 0.5))
        cv.paint(grow(disc, 2.2 * ss), TONER)
        cv.paint(disc, WHITE_ * TW_HUB_V)
        sp = toner_noise(cv, seed + 9, 0.9, 0.9)
        cv.paint(blur(sp, 0.3 * ss) * disc, TONER, 0.3)
        by = c[1] - (19.0 if name else 0.0)
        s_ = 0.78 if name else 1.5
        bolt = [(c[0] + 2.5 * s_, by - 9 * s_), (c[0] - 5.0 * s_, by + 1.0 * s_), (c[0] - 0.5 * s_, by + 1.0 * s_), (c[0] - 3.0 * s_, by + 9.5 * s_), (c[0] + 5.5 * s_, by - 2.0 * s_), (c[0] + 0.5 * s_, by - 2.0 * s_)]
        bm = poly(cv, bolt)
        cv.paint(plate_shift(bm, cv, 1.4, 1.2), MAG)
        ink(cv, bm, TONER, 0.0, seed + 4)
        if name:
            tw_, th_ = 66.0, 22.0
            ty = c[1] + 6.0
            t = LT.rect_rot(cv, c[0] - tw_ / 2, ty - th_ / 2, c[0] + tw_ / 2, ty + th_ / 2, -2.0)
            cv.paint(shift(t, 1.6 * ss, 1.8 * ss), MAG)
            cv.paint(grow(t, 0.4 * ss), TONER)
            ink(cv, t, TONER, 0.0, seed + 50)
            xtext(cv, name, c[0], ty + 0.6, HUB_TXT, ANTON, fill=WHITE_ * TW_HUB_V, rot=-2.0, wob=0.05, track=0.6, seed=seed + 60, grain=0.0)
    LT.draw_hub = draw_hub


# ======================================================================================== 1.1 cells
def _cells(R, A):
    import f1_board as FB
    import gram as G
    import gram_render as GR
    import wr_cells as WCL
    import wr2_cells as W2C
    import lw_install as LI
    from wr_geo import cell_poly, unit_bounds, radial_ext
    from cv_lib import C, ppx
    ENAMEL = (217, 225, 234)
    mix = FB._mixc

    def screen(L, u):
        """the occupied cell: kind-slate frosted glass at the ring's value, lit toward the outer edge"""
        wash = G.kind_wash(u['kind'], u['dep'], ramp=(0.0, 0.0, 0.0))
        base = at_lstar(wash, OCC_L[u['dep']])
        lo, hi = scale_y(base, OCC_GRAD[0]), scale_y(base, OCC_GRAD[1])
        WCL._gradient_fill(L, u, lambda t: mix(lo, hi, min(1.0, t)))
        b0, b1 = unit_bounds(u)
        if u['w'] < 6:
            FB.helix(L, u, base, u['dep'], b0, b1)
    FB.screen = screen
    W2C.screen = screen
    GR.W2C.screen = screen

    def empty_cell(L, dep, s):
        b0, b1 = 60 * s - 30, 60 * s + 30
        fill = at_lstar((38, 50, 70), EMPTY_L[dep])
        poly = cell_poly(dep, b0, b1, kind='empty')
        L.poly(poly, fill=fill + (255,))
        L.line(poly + [poly[0]], mix(fill, ENAMEL, 0.22), 1.4)
        FB.helix(L, None, fill, dep, b0, b1)
    FB.empty_cell = empty_cell
    W2C.empty_cell = empty_cell
    GR.W2C.empty_cell = empty_cell

    def programme_screen(L, u):
        """the unit's programme screen: an inset frosted panel (luminance x SCREEN_LIFT) with a 1.2 px enamel frame, under every mark"""
        if u['w'] == 6:
            return
        b0, b1 = unit_bounds(u)
        dep = u['dep']
        wash = G.kind_wash(u['kind'], dep, ramp=(0.0, 0.0, 0.0))
        base = at_lstar(wash, OCC_L[dep])
        inner = cell_poly(dep, b0, b1, SCREEN_INSET, SCREEN_INSET, kind='unit', tin=SCREEN_INSET)
        Tl = L2(L.k)                                   # translucent pieces go on their own layer (PIL draw replaces RGBA, it does not blend)
        Tl.poly(inner, fill=scale_y(base, SCREEN_LIFT) + (110,))
        Tl.line(inner + [inner[0]], mix(base, ENAMEL, 0.55) + (200,), 1.2)
        L.im.alpha_composite(Tl.im)
    from cv_lib import L2

    def over(L, fn, *a):
        Tl = L2(L.k)
        fn(Tl, *a)
        L.im.alpha_composite(Tl.im)
    _orig = LI._orig_paint
    from cs_skin import region_apply

    def paint_cells(L, f, beat, which=None, with_base=True):
        s = LI.SK[0]
        import corp_kinds as CK
        restore = CK.use(getattr(s, 'kind_gain', None))
        try:
            _orig(L, f, beat, which=which, with_base=with_base)
            polys_e, polys_u, us = [], [], []
            if with_base:
                cov = A.WCL.covered(f)
                for dep in range(3):
                    for sc in range(6):
                        if (dep, sc) not in cov:
                            polys_e.append((dep, cell_poly(dep, 60 * sc - 30, 60 * sc + 30, kind='empty')))
            for u in A.WCL.live_units(f):
                if which is not None and u['id'] not in which:
                    continue
                if u['w'] == 6:
                    continue
                b0, b1 = unit_bounds(u)
                polys_u.append((u['dep'], cell_poly(u['dep'], b0, b1, kind='unit')))
                us.append(u)
            if polys_e:
                region_apply(L, [p for _, p in polys_e], lambda X, Y, RH, TH: s.cell(X, Y, RH, TH, empty=True), strength=SKIN_EMPTY_K)
            if polys_u:
                region_apply(L, [p for _, p in polys_u], lambda X, Y, RH, TH: s.cell(X, Y, RH, TH, empty=False), strength=SKIN_UNIT_K)
            for u in us:
                programme_screen(L, u)
            for (dep, p) in polys_e:
                over(L, s.cell_detail, p, dep, True, 0)
            for (dep, p) in polys_u:
                over(L, s.cell_detail, p, dep, False, 0)
            if hasattr(s, 'empty_marks') and polys_e:
                s.empty_marks(L, polys_e)
        finally:
            restore()
    LI.paint_cells = paint_cells
    R.paint_cells = paint_cells


# ======================================================================================== 1.1 HP ticks, 1.2 token glyph cap
def _units(A):
    import wr2_lib
    import asm_units as AU
    import wr2_units as W2U
    import e8lib as E8
    wr2_lib.PIP_H = PIP_H

    def token(L, u, dead=False, badges=True):
        x, y = E8.token_pos(u)
        Rr = wr2_lib.TOK_R
        W2U.halo(L, x, y, Rr)
        W2U.disc(L, x, y, Rr, u['kind'], dead)
        W2U.ring(L, x, y, Rr, u['dep'], dead)
        dying = u['fate']['kind'] == 'dies'
        if badges and not dead:
            if u['warded']:
                AU.CTX['L'] = L
                side, h = AU.pick_side(u, 'dia', 15)
                size, ov = AU.fit_badge(u, 'dia', 15, 11, side)
                h = AU.hits(u, 'dia', size, side)
                while (h['tag'] + h['tray'] + h['chev'] + h['glyph'] + h['band']) > 0 and size > 8:
                    size -= 1
                    h = AU.hits(u, 'dia', size, side)
                AU.BADGE_LOG.append(dict(uid=u['id'], kind=u['kind'], badge='warded', size=size * 2, overlap_px=ov, side=side, hits=h))
                AU.warded_badge(L, u, size, side)
            if dying:
                AU.CTX['L'] = L
                side, h = AU.pick_side(u, 'disc', 13)
                size, ov = AU.fit_badge(u, 'disc', 13, 9, side)
                h = AU.hits(u, 'disc', size, side)
                while (h['tag'] + h['tray'] + h['chev'] + h['glyph'] + h['band']) > 0 and size > 6:
                    size -= 1
                    h = AU.hits(u, 'disc', size, side)
                AU.BADGE_LOG.append(dict(uid=u['id'], kind=u['kind'], badge='dead', size=size * 2, overlap_px=ov, side=side, hits=h))
                AU.dead_badge(L, u, size, side)
        W2U.gly(L, AU.KIND[u['kind']][1], 37, (x, y), (150, 150, 160) if dead else TOKEN_GLYPH)
        if u.get('df') == 'armor' and not dead:
            ang = math.degrees(math.atan2(x - AU.C[0], -(y - AU.C[1])))
            W2U.armor_cue(L, x, y, Rr, ang)
        return x, y
    AU.token = token


# ======================================================================================== 1.2 HOT marks
def _hot(A):
    import gram as G
    import gramlib as GL
    import wr2_units as W2U
    import cv_board as CB
    import e8lib as E8
    _ost = W2U.stack

    def stack(L, u, ang, n_solid, n_hollow, dim=0.0):
        _ost(L, u, ang, n_solid, n_hollow, dim)
        if u['dep'] != 0 or u['fate']['kind'] == 'dies':
            return
        st = W2U.chev_params(u, n_solid + n_hollow)
        ri, ro = CB.ring_geom(u['dep'])
        for i in range(n_solid):
            r = ri + st['start'] + i * st['pitch']
            p = [E8.pt(r + st['depth'], ang, -st['half'] * 0.86), E8.pt(r, ang, 0), E8.pt(r + st['depth'], ang, st['half'] * 0.86)]
            L.line(p, T.HOT_CORE, HOT_CORE_W)
    W2U.stack = stack
    _oac = G.arc_chevrons

    def arc_chevrons(L, r, th, x0, ns, ng, opt, k):
        _oac(L, r, th, x0, ns, ng, opt, k)
        if k != 0:
            return
        p = G.A2.CH[opt]
        for i in range(ns):
            xc = x0 + p['pitch'] / 2 + i * p['pitch']
            fr = G.A2.Fr(r, th, xc)
            q = [fr.q(-p['hw'] * 0.82, p['dp'] / 2 * 0.82), fr.q(0, -p['dp'] / 2 * 0.82), fr.q(p['hw'] * 0.82, p['dp'] / 2 * 0.82)]
            L.line(q, T.HOT_CORE, HOT_CORE_W * 0.9)
    G.arc_chevrons = arc_chevrons


# ======================================================================================== 1.2 + 2.9 the clock: one gunmetal, orange on the live step only
def _clock(A):
    import r2_sched as S2
    import o_sched as OS
    import lw_skin
    from cv_lib import C, ppx, NOW
    from o_sched import cell_pts, B0, B1, RM, NAMES
    import r2_glyphs as GLY
    INK = (12, 10, 22)
    lw_skin.NeutralTape.remap = classmethod(lambda cls, im: im.convert('RGBA'))      # the silver remap is retired: the clock draws its own material

    def engraved(L, p):
        """the gunmetal plate: ink keyline, fill, an engraved groove inside the edge with its light lip below (light from the top-left)"""
        L.poly(p, fill=GUN_FILL, outline=INK, w=3.2)

    def groove(L, a0, a1, b0=B0, b1=B1):
        for rr, col, w in ((b1 - 3.6, GUN_GROOVE, 1.4), (b1 - 4.8, GUN_LIGHT, 1.0), (b0 + 3.4, GUN_GROOVE, 1.4), (b0 + 4.6, GUN_LIGHT, 1.0)):
            n = max(6, int(abs(a1 - a0) / 1.5))
            L.line([ppx(C, rr, a0 + (a1 - a0) * i / n) for i in range(n + 1)], col, w)

    def live_cell(L, a0, a1, opt):
        a0 = a0 + 1.4
        tip = 5.5
        p = cell_pts(B0, B1, a0, a1 - 0.6, 'arrow', tip=tip)
        k = L.k
        L.glow(lambda d: d.polygon([(x * k, y * k) for x, y in p], fill=SCHED + (255,)), blur=4, strength=0.30)       # L9: live at this END TURN
        engraved(L, p)
        groove(L, a0 + 2.0, a1 - 8.0)
        L.poly(p, fill=None, outline=SCHED, w=2.2)                                                                    # the live step's SCHEDULE edge
        return a0 + 7
    S2.live_cell = live_cell

    def live_label(L, a0, txt, n=2):
        px = BEZEL_TXT
        from bb_lib import mono
        f = mono(int(px * L.k))
        lab_w = f.getlength(txt[1:]) / L.k
        lab_deg = math.degrees(lab_w / RM)
        a_start = a0 + 7
        x, y = ppx(C, RM, a_start + 0.9)
        th = math.radians(a_start + 0.9)
        mid = a_start + 3.2 + lab_deg / 2 + 0.6
        OS.arc_text2(L, RM + 0.6, mid, txt[1:], px, GUN_LIGHT, 'mono', bold=0.0)          # engraved lip
        OS.arc_text2(L, RM - 0.4, mid, txt[1:], px, INK, 'mono', bold=0.45)
        ux, uy = math.cos(th), math.sin(th)
        nx, ny = math.sin(th), -math.cos(th)
        L.line([(x - 6 * ux, y - 6 * uy), (x + 6 * ux, y + 6 * uy)], INK, 3.0)
        L.line([(x - 6 * nx, y - 6 * ny), (x + 6 * nx, y + 6 * ny)], INK, 3.0)
        if not NOW['words']:
            for i in range(n):
                xx, yy = ppx(C, RM, a_start + 0.9 + (11.0 + i * 5.4) / RM * 57.3)
                L.rect([xx - 2.6, yy - 7.8, xx + 2.6, yy + 7.8], fill=INK, r=1)
                L.rect([xx - 1.4, yy - 7.0, xx + 1.4, yy + 7.0], fill=(244, 247, 252), r=1)
            return a_start + math.degrees(24 / RM) + 4
        return a_start + lab_deg + 5
    S2.live_label = live_label

    def chevrons(L, a0, a1, a_text_end, opt):
        """L5 chevrons in SCHEDULE orange: the live step's direction of travel"""
        pitch = 26.0 / RM * 57.3
        am = a_text_end + pitch * 0.6
        amax = a1 - 9.0
        while am <= amax:
            p = [ppx(C, B1 - 5.0, am - 3.0), ppx(C, RM, am + 3.0), ppx(C, B0 + 5.0, am - 3.0)]
            L.line(p, INK, 5.6)
            L.line(p, SCHED, 3.0)
            am += pitch
    S2.chevrons = chevrons

    def hold_glyph(L, x, y, col, size=1.0):
        s = size
        L.ellipse([x - 14 * s, y - 14 * s, x + 14 * s, y + 14 * s], fill=GUN_GROOVE, outline=INK, w=3.0)
        L.ellipse([x - 12.4 * s, y - 12.4 * s, x + 12.4 * s, y + 12.4 * s], fill=GUN_GROOVE, outline=col, w=1.8)
        GLY.stamp(L, 'hold', 16.5 * s, (x, y), col)

    def _label_mid(a0, txt, px):
        from bb_lib import mono
        f = mono(int(px * 2))
        w = f.getlength(txt) / 2
        return a0 + 7.2 + math.degrees((14 + 7) / RM) + math.degrees(w / 2 / RM), w

    def _clear_mid(lo, hi, txt, px):
        """the label's centre angle: the first position from lo (its old start) whose span, plus the digit boss and a 3 px margin, crosses no
        sector digit and ends before hi.  The 23 px words are longer than the old 18 px ones; placed from the glyph they ran under digit 3."""
        from bb_lib import mono
        span0 = math.degrees(mono(int(px * 2)).getlength(txt) / 2 / RM)
        rd = math.degrees((S2.BOSS_R + S2.DIGIT_GAP + LABEL_DIGIT_MARGIN) / RM)
        for tr in LABEL_TRACKS:             # full advance first; tighter mono advance only when the cell is too short
            span = span0 * tr
            s = lo
            while s + span <= hi:
                if all(((da - (s - rd)) % 360.0) >= span + 2 * rd for da in S2.DIGIT_ANG):
                    LABEL_LOG.append((txt, round(s, 2), round(s + span, 2), tr, True))
                    return s + span / 2, tr
                s += 0.25
        LABEL_LOG.append((txt, round(lo, 2), round(lo + span0, 2), 1.0, False))
        return lo + span0 / 2, 1.0

    def hold_label(L, a0, k, opt, live=False, a1=None):
        x, y = ppx(C, RM, a0 + 7.2)
        txt = 'HOLD THIS TURN' if live else 'HOLD ' + NAMES[k].split()[0]
        a1 = a0 + HOLD_CELL_DEG if a1 is None else a1
        mid, tr = _clear_mid(a0 + 7.2 + math.degrees((14 + 7) / RM), a1 - 0.8 - math.degrees(LABEL_END_MARGIN / RM), txt, BEZEL_TXT)
        hold_glyph(L, x, y, SCHED if live else GUN_LIGHT)
        OS.arc_text2(L, RM + 0.6, mid, txt, BEZEL_TXT, GUN_LIGHT, 'mono', bold=0.0, track=tr)
        OS.arc_text2(L, RM - 0.4, mid, txt, BEZEL_TXT, INK, 'mono', bold=0.35, track=tr)
    S2.hold_label = hold_label

    def hold_cell(L, a0, a1, k, opt):
        p = cell_pts(B0, B1, a0 + 0.8, a1 - 0.8)
        engraved(L, p)
        groove(L, a0 + 1.6, a1 - 1.6)
        if S2.SKIP_LABELS[0]:
            return
        hold_label(L, a0, k, opt, a1=a1)
    S2.hold_cell = hold_cell

    def hold_live(L, a0, a1, opt):
        p = cell_pts(B0, B1, a0 + 1.4, a1 - 0.6)
        k = L.k
        L.glow(lambda d: d.polygon([(x * k, y * k) for x, y in p], fill=SCHED + (255,)), blur=4, strength=0.30)
        engraved(L, p)
        groove(L, a0 + 2.0, a1 - 2.0)
        L.poly(p, fill=None, outline=SCHED, w=2.2)
        if S2.SKIP_LABELS[0]:
            return
        hold_label(L, a0, 0, opt, live=True, a1=a1)
    S2.hold_live = hold_live
    _opc = OS.plus_cell

    def plus_cell(L, opt, a0, a1, v, k):
        """+N steps in later turns: the same gunmetal, no orange (orange is the live step only)"""
        p = cell_pts(B0, B1, a0 + 0.8, a1 - 0.8, 'arrow', tip=5.5)
        engraved(L, p)
        groove(L, a0 + 1.6, a1 - 7.0)
        txt = '+%d %s' % (v, NAMES[k])
        mid, tr = _clear_mid(a0 - 5.0 + 7.2 + math.degrees((14 + 7) / RM), a1 - 7.0, txt, BEZEL_TXT)
        OS.arc_text2(L, RM + 0.6, mid, txt, BEZEL_TXT, GUN_LIGHT, 'mono', track=tr)
        OS.arc_text2(L, RM - 0.4, mid, txt, BEZEL_TXT, INK, 'mono', bold=0.35, track=tr)
    OS.plus_cell = plus_cell
    S2.S.plus_cell = plus_cell


# ======================================================================================== 1.8 kill marks in the cause colour
def _kills(A):
    import asm_units as AU
    import wr2_units as W2U
    from wr2_lib import INKC
    PINK = T.TOKENS['CELL_PINK']

    def x_badge(L, bx, by, r, s, w_ink, w):
        L.ellipse([bx - r - 2.5, by - r - 2.5, bx + r + 2.5, by + r + 2.5], fill=INKC)
        L.ellipse([bx - r, by - r, bx + r, by + r], fill=(40, 8, 26), outline=PINK, w=3.0 if r > 12 else 2.2)
        for a_, b_ in (((bx - s, by - s), (bx + s, by + s)), ((bx + s, by - s), (bx - s, by + s))):
            L.line([a_, b_], INKC, w_ink)
        for a_, b_ in (((bx - s, by - s), (bx + s, by + s)), ((bx + s, by - s), (bx - s, by + s))):
            L.line([a_, b_], PINK, w)

    def dead_badge(L, u, r, side='out'):
        bx, by = AU.badge_xy(u, AU.BADGE_D, side)
        x_badge(L, bx, by, r, 5.4 * r / 14.0, 7.2, 3.6)
    AU.dead_badge = dead_badge

    def w2_dead_badge(L, u):
        bx, by = W2U._side(u, W2U.TOK_R + 14 + 1)
        x_badge(L, bx, by, 14, 5.4, 7.2, 3.6)
    W2U.dead_badge = w2_dead_badge
    _og = W2U.ghost

    def ghost(L, u, kind, beat='p2'):
        if kind == 'consumed':
            return _og(L, u, kind, beat)
        # trigger-killed ghost: the shared ghost, the outline in the cause colour (our pink, pencil in hover beats), the X badge in pink
        import wr_units as WU
        import e8lib as E8
        KIND, TOK_R = W2U.KIND, W2U.TOK_R
        poly = WU.u_poly(u)
        ghostc = W2U.mix(W2U.kind_wash(u['kind'], u['dep']), W2U.BED, 0.62)
        L.poly(poly, fill=ghostc + (255,))
        W2U.wax_outline(L, poly, W2U.PLAN, 4.0, seed=u['id'] * 7 + 1)
        x, y = E8.token_pos(u)
        L.ellipse([x - TOK_R - 1.5, y - TOK_R - 1.5, x + TOK_R + 1.5, y + TOK_R + 1.5], fill=INKC)
        L.ellipse([x - TOK_R, y - TOK_R, x + TOK_R, y + TOK_R], fill=(58, 54, 66))
        W2U.ring(L, x, y, TOK_R, u['dep'], dead=True)
        W2U.gly(L, KIND[u['kind']][1], 34, (x, y), (176, 172, 186))
        bx, by = W2U._side(u, TOK_R + 14)
        x_badge(L, bx, by, 11, 4.2, 5.6, 2.8)
    W2U.ghost = ghost


# ======================================================================================== 2.12 FAR marks carry their number
def _far_numbers(A):
    import gram as G
    INK = (12, 10, 22)
    _oac = G.arc_chevrons
    _oad = G.arc_diamonds

    from cv_lib import NOW

    def num(L, x, y, n, col):
        if NOW['words']:
            L.text((x, y + 0.5), str(n), FAR_NUM_PX, 'anton', fill=col, anchor='mm', stroke=1.8)
            return
        # nowords: the number as upright tally strokes (the plate's digit proxy), same colour, ink keyline
        p, w, h = 5.0, 2.6, 12.0
        x0 = x - (n - 1) * p / 2
        for i in range(n):
            xi = x0 + i * p
            L.line([(xi, y - h / 2), (xi, y + h / 2)], INK, w + 3.0)
        for i in range(n):
            xi = x0 + i * p
            L.line([(xi, y - h / 2), (xi, y + h / 2)], col, w)

    def arc_chevrons(L, r, th, x0, ns, ng, opt, k):
        _oac(L, r, th, x0, ns, ng, opt, k)
        if k == 2 and ns + ng:
            fr = G.A2.Fr(r, th, x0 - 9.0)
            num(L, fr.x, fr.y, ns + ng, G.grade((235, 210, 205), 1))
    G.arc_chevrons = arc_chevrons

    def arc_diamonds(L, r, th, x0, n, opt, k):
        _oad(L, r, th, x0, n, opt, k)
        if k == 2 and n:
            d = G.A2.DI[opt]
            fr = G.A2.Fr(r, th, x0 + d['pitch'] * n + 8.0)
            num(L, fr.x, fr.y, n, G.grade((235, 210, 205), 1))
    G.arc_diamonds = arc_diamonds


# ======================================================================================== 2.13 the Adjuster
def _adjuster(A):
    import wr2_boss as W2B
    import gramlib as GL
    import wr2_units as W2U
    from wr_geo import radial_ext
    from cv_lib import C, ppx
    from wr2_lib import INKC
    GOLD = T.BOSS_GOLD

    def hp_bar(L, a, ang):
        """a solid gold HP edge: one track, square segments cut by 1.6 px ink, a wider cut between the two groups of 5; the HP lost this END TURN
        is the L7 cross-hatch in the cause colour (our pink); gone HP = dark socket"""
        n = a['mx']
        ha = a.get('hp_after', a['hp'])
        ra, rb = radial_ext(a['ring'])
        r1 = rb - 1.5 - 4.5
        r0 = r1 - BOSS_SEG_H
        rm = (r0 + r1) / 2
        seg, gp, grp = 17.0, 1.6, 5.0
        tot = n * seg + (n - 1) * gp + grp
        a_start = ang - math.degrees(tot / 2 / rm)
        pos, x = [], 0.0
        for i in range(n):
            if i == 5:
                x += grp
            pos.append((a_start + math.degrees(x / rm), a_start + math.degrees((x + seg) / rm)))
            x += seg + gp
        band = W2U.arc_band(r0 - 1.6, r1 + 1.6, pos[0][0] - math.degrees(1.6 / rm), pos[-1][1] + math.degrees(1.6 / rm))
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
        # the engraved highlight along the kept track (one line, no beads)
        if ha > 0:
            L.line(L.arc_pts(C, r1 - 1.6, pos[0][0] + 0.3, pos[ha - 1][1] - 0.3, 30), T.BOSS_GOLD_HI, 1.0)
    W2B.hp_bar = hp_bar


# ======================================================================================== 1.3 + 1.4 corp skins
def _skins():
    import cs_skin as CS
    from cs_skin import Acc, sstep, vor, mixc
    from cv_lib import C, ppx
    SL = dict(T.SKIN_INKS_RETIRED['solace'], **T.SKIN_INKS['solace'])     # 2026-11-04 round 2: rb4_patch re-inks every Solace piece in teal (C16)
    MR = T.SKIN_INKS['meridian']
    SLATE_TINT_S = (44, 54, 52)       # Solace: a cool green-grey tint (low chroma) over the slate
    SLATE_TINT_M = (56, 52, 48)       # Meridian: a warm steel-grey tint

    # ---------------------------------------------------------------- Solace
    S = CS.Solace
    S.kind_gain = (1.0, 1.0, 1.0)
    S.pal = dict(S.pal, primary=SL['leaf'], glass=SLATE_TINT_S, glass_hi=(150, 170, 160), edge=SL['leaf'], strand_a=SL['leaf'], strand_b=SL['leaf_deep'],
                 porcelain=SL['porcelain'], nucleus=(150, 170, 160))

    def s_cell(self, X, Y, RHO, TH, empty=False):
        """lab glass: neutral slate with a low-chroma cool tint; the membrane network and bubbles are the material (no hue, no rose nuclei)"""
        P = self.pal
        acc = Acc(X.shape)
        acc.add(SLATE_TINT_S, 0.30)
        f1, f2, ids, pts = vor(X, Y, 30.0, 11)
        acc.add(P['glass_hi'], (1 - sstep(0.0, 1.5, f2 - f1)) * 0.12)
        g1, g2, bid, bp = vor(X, Y, 44.0, 23)
        rr = 3.0 + ((bid * 131) % 7).astype(np.float32)
        keep = ((bid * 53) % 3 == 0).astype(np.float32)
        acc.add((210, 225, 218), (1 - sstep(0.0, 0.9, np.abs(g1 - rr))) * keep * 0.14)
        acc.add((220, 235, 228), np.clip(np.cos(np.radians(TH - 315)), 0, 1) ** 2 * 0.05)
        return acc.rgb, acc.a
    S.cell = s_cell

    def s_bezel(self, X, Y, RHO, TH):
        acc = Acc(X.shape)
        u = np.clip((RHO - 388) / 34.0, 0, 1)
        acc.add((20, 26, 26), 1.0)
        acc.add((44, 54, 52), 0.35 + 0.25 * np.sin(np.pi * u))
        f1, f2, ids, pts = vor(X, Y, 26.0, 5)
        acc.add((120, 140, 132), (1 - sstep(0.0, 1.4, f2 - f1)) * 0.10)
        lip = (1 - sstep(0.0, 1.2, np.abs(RHO - 389.2))) + (1 - sstep(0.0, 1.2, np.abs(RHO - 420.8)))
        acc.add(SL['leaf_deep'], np.clip(lip, 0, 1) * 0.85)                 # the corp hue on the bezel lip
        return acc.rgb, acc.a
    S.bezel = s_bezel

    def s_annulus(self, X, Y, RHO, TH):
        acc = Acc(X.shape)
        acc.add((10, 14, 14), 0.55)
        f1, f2, ids, pts = vor(X, Y, 34.0, 31)
        acc.add((110, 130, 122), (1 - sstep(0.0, 1.4, f2 - f1)) * 0.08)
        return acc.rgb, acc.a
    S.annulus = s_annulus

    def s_arcframe(self, X, Y, RHO, TH):
        acc = Acc(X.shape)
        acc.add((22, 28, 28), 0.55)
        return acc.rgb, acc.a
    S.arcframe = s_arcframe

    def s_cell_detail(self, L, poly, dep, empty, seed):
        pp = poly + [poly[0]]
        L.line(pp, mixc(SL['leaf_deep'], (10, 20, 16), 0.15 if not empty else 0.45) + (200 if not empty else 130,), 1.3)      # corp hue on the cell edge
    S.cell_detail = s_cell_detail

    def s_token_frame(self, L, x, y, R, kind, dep):
        P = self.pal
        Ro = R + 6.0
        L.ellipse([x - Ro - 1.6, y - Ro - 1.6, x + Ro + 1.6, y + Ro + 1.6], fill=(8, 14, 12))
        L.ellipse([x - Ro, y - Ro, x + Ro, y + Ro], fill=(96, 108, 104))          # porcelain, glazed down to mid value
        L.line(L.arc_pts((x, y), Ro - 1.6, 280, 360 + 40, 14), (150, 162, 158), 1.6)
        L.ellipse([x - R - 1.8, y - R - 1.8, x + R + 1.8, y + R + 1.8], fill=(8, 14, 12))
        L.ellipse([x - 2.2, y - Ro + 0.2, x + 2.2, y - Ro + 4.6], fill=SL['leaf'], outline=(8, 14, 12), w=0.8)
    S.token_frame = s_token_frame

    def s_disc_frame(self, L, x, y, R):
        Ro = R + 3.6
        L.ellipse([x - Ro - 1.2, y - Ro - 1.2, x + Ro + 1.2, y + Ro + 1.2], fill=(8, 14, 12))
        L.ellipse([x - Ro, y - Ro, x + Ro, y + Ro], fill=(96, 108, 104))
        L.ellipse([x - R - 1.4, y - R - 1.4, x + R + 1.4, y + R + 1.4], fill=(8, 14, 12))
    S.disc_frame = s_disc_frame

    def s_ticket(self, L, box, nearest, climax):
        x0, y0, x1, y1 = box
        pts = [(x0 + 7, y0), (x1 - 7, y0), (x1, y0 + 7), (x1, y1 - 7), (x1 - 7, y1), (x0 + 7, y1), (x0, y1 - 7), (x0, y0 + 7)]
        L.poly(pts, fill=(30, 36, 36, 255))
        L.line(pts + [pts[0]], (8, 14, 12), 4.4)
        L.line(pts + [pts[0]], SL['leaf'] if nearest else SL['leaf_deep'], 1.8)
        self.crest(L, x1 - 13, y0 + 13, 0.62)
    S.ticket = s_ticket

    # ---------------------------------------------------------------- Meridian
    M = CS.Meridian
    M.kind_gain = (1.0, 1.0, 1.0)
    M.pal = dict(M.pal, primary=MR['rust'], hazard_a=MR['rust'], edge=MR['rust'], oxide=SLATE_TINT_M)
    M.HAZ_DESAT = 0.0

    def m_cell(self, X, Y, RHO, TH, empty=False):
        """container steel: neutral slate with a low-chroma warm tint; the corrugation is the material"""
        acc = Acc(X.shape)
        acc.add(SLATE_TINT_M, 0.30)
        rib = self._rib(RHO, TH, 6.5)
        acc.add((16, 14, 12), (1 - rib) ** 2 * 0.16)
        acc.add((200, 196, 190), rib ** 3 * 0.07)
        return acc.rgb, acc.a
    M.cell = m_cell

    def m_bezel(self, X, Y, RHO, TH):
        acc = Acc(X.shape)
        u = np.clip((RHO - 388) / 34.0, 0, 1)
        acc.add((30, 30, 32), 1.0)
        acc.add((70, 70, 72), 0.30 + 0.2 * np.sin(np.pi * u))
        acc.add((16, 14, 12), (1 - self._rib(RHO, TH, 5.0)) ** 2 * 0.12)
        lip_in = 1 - sstep(0.0, 0.8, np.abs(RHO - 389.6) - 1.4)
        lip_out = 1 - sstep(0.0, 0.8, np.abs(RHO - 420.4) - 1.4)
        acc.add((14, 12, 11), np.maximum(lip_in, lip_out) * 0.95)
        # one solid rust line on the outer lip (a striped 3 px lip read as a bead row: dot_audit runs on p2b Meridian, 9.3 px pitch)
        acc.add(MR['rust'], lip_out * 0.90)
        return acc.rgb, acc.a
    M.bezel = m_bezel

    def m_annulus(self, X, Y, RHO, TH):
        acc = Acc(X.shape)
        acc.add((18, 17, 16), 0.55)
        acc.add((14, 12, 10), (1 - self._rib(RHO, TH, 7.0)) ** 2 * 0.12)
        return acc.rgb, acc.a
    M.annulus = m_annulus

    def m_arcframe(self, X, Y, RHO, TH):
        acc = Acc(X.shape)
        acc.add((30, 28, 26), 0.55)
        return acc.rgb, acc.a
    M.arcframe = m_arcframe

    def m_rim(self, X, Y, RHO, TH):
        acc = Acc(X.shape)
        u = np.clip((RHO - 489.0) / 11.0, 0, 1)
        acc.add((14, 12, 11), 1.0)
        ph = (TH / 360.0 * 311 + (RHO - 489.0) / 10.0) % 1.0
        stripe = np.where(ph < 0.5, 1.0, 0.0).astype(np.float32)
        k = 0.86 + 0.14 * np.sin(np.pi * u) + 0.10 * np.cos(np.radians(TH - 315))
        acc.add(np.array(MR['rust'], np.float32)[None, None] * k[..., None], stripe * 0.94)
        return acc.rgb, acc.a
    M.rim = m_rim

    def m_cell_detail(self, L, poly, dep, empty, seed):
        pp = poly + [poly[0]]
        L.line(pp, mixc(MR['rust'], (12, 8, 6), 0.10 if not empty else 0.45) + (200 if not empty else 130,), 1.3)      # rust paint on the cell edge
        n = len(poly) // 2
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        for idx in (0, n - 1, n, len(poly) - 1):
            px, py = poly[idx]
            d = math.hypot(cx - px, cy - py) + 1e-6
            self._rivet(L, px + (cx - px) / d * 6.0, py + (cy - py) / d * 6.0)
    M.cell_detail = m_cell_detail

    def m_token_frame(self, L, x, y, R, kind, dep):
        Ro = R + 6.5
        oc = lambda r: [(x + r * math.cos(math.radians(22.5 + 45 * i)), y + r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
        L.poly(oc(Ro + 1.6), fill=(10, 8, 7))
        L.poly(oc(Ro), fill=(92, 92, 96))                                          # container steel, neutral
        o8 = oc(Ro - 1.2)
        L.line(o8[4:7], (150, 150, 156), 1.5)
        L.line(o8[0:3], (50, 50, 54), 1.5)
        L.ellipse([x - R - 1.8, y - R - 1.8, x + R + 1.8, y + R + 1.8], fill=(10, 8, 7))
        for i in range(4):
            a = math.radians(45 + 90 * i)
            cx, cy = x + (Ro - 2.2) * math.cos(a) * 0.98, y + (Ro - 2.2) * math.sin(a) * 0.98
            L.rect([cx - 2.5, cy - 2.5, cx + 2.5, cy + 2.5], fill=MR['rust'], outline=(10, 8, 7), w=0.8, r=0.6)
    M.token_frame = m_token_frame

    def m_disc_frame(self, L, x, y, R):
        Ro = R + 3.6
        oc = lambda r: [(x + r * math.cos(math.radians(22.5 + 45 * i)), y + r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
        L.poly(oc(Ro + 1.3), fill=(10, 8, 7))
        L.poly(oc(Ro), fill=(92, 92, 96))
        L.ellipse([x - R - 1.4, y - R - 1.4, x + R + 1.4, y + R + 1.4], fill=(10, 8, 7))
    M.disc_frame = m_disc_frame

    def m_ticket(self, L, box, nearest, climax):
        x0, y0, x1, y1 = box
        pts = [(x0 + 2, y0), (x1 - 2, y0), (x1, y0 + 2), (x1, y1 - 2), (x1 - 2, y1), (x0 + 2, y1), (x0, y1 - 2), (x0, y0 + 2)]
        L.poly(pts, fill=(34, 33, 34, 255))
        L.line(pts + [pts[0]], (10, 8, 7), 4.4)
        L.line(pts + [pts[0]], MR['rust_hi'] if nearest else MR['rust'], 1.8)
        for (cx, cy) in ((x0 + 5, y0 + 5), (x1 - 5, y0 + 5), (x0 + 5, y1 - 5), (x1 - 5, y1 - 5)):
            self._rivet(L, cx, cy, 1.2)
    M.ticket = m_ticket


# ======================================================================================== hand values
def _hand(R):
    import f1_hand as FH
    FH.REST_V = REST_V
    _och = FH.card_hi

    def card_hi(name, nw, mode='normal'):
        im = _och(name, nw, mode)
        if mode != 'hover':
            return im
        key = ('rb_lift', name, nw)
        if key not in FH._mem:
            a = np.asarray(im).astype(np.float32)
            a[..., :3] *= LIFT_V
            from PIL import Image
            FH._mem[key] = Image.fromarray(a.astype(np.uint8), 'RGBA')
        return FH._mem[key]
    FH.card_hi = card_hi

    def draw_hand(base, J, beat, nw=False, lift=None, dim_others=None):
        """f1_hand.draw_hand with the p2 lift layout from rb_lift.py: the lifted card LIFT_DX left and at LIFT_CY2, so it covers no sibling's
        cost hex or rules line (AD review 2.6 test); every other beat and every hover plate keeps f1_hand's layout"""
        hand, played, hov = FH.hand_lists(J, beat)
        if lift is not None:
            hov = hand.index(lift)
        n = len(hand) + len(played)
        sl = FH.slots(n)
        own = beat == 'p2' and lift is None
        push = LIFT_PUSH if own else FH.HOV_PUSH
        if hov is not None:
            for k_ in range(hov + 1, n):
                sl[k_]['cx'] += push
        for i, nm in enumerate(hand):
            if i == hov:
                continue
            s = sl[i]
            ci = FH.card_hi(nm, nw)
            a_ = np.asarray(ci).astype(np.float32)
            a_[..., :3] *= FH.REST_V * (dim_others or 1.0)
            from PIL import Image
            FH.put(base, Image.fromarray(a_.astype(np.uint8), 'RGBA'), s['cx'], s['cy'], s['ang'], FH.CARD_SCALE)
        for j, nm in enumerate(played):
            s = sl[len(hand) + j]
            FH.put(base, FH.played_slot(nm, nw), s['cx'], s['cy'], s['ang'], FH.CARD_SCALE, shadow=False)
        if hov is not None:
            s = sl[hov]
            im = FH.card_hi(hand[hov], nw, 'hover')
            FH.put(base, im, s['cx'] + (LIFT_DX if own else 0), LIFT_CY2 if own else FH.LIFT_CY, 0, FH.LIFT_S * FH.CARD_SCALE, shadow=True, off=(6, 12), blur=10)
        return sl
    FH.draw_hand = draw_hand


# ======================================================================================== text >= 16 px cap on this board
def _text():
    import f1_board as FB
    import a2_stick as AS
    import lw_ui
    from cv_lib import NOW
    TXT_MID = AS.TXT_MID if hasattr(AS, 'TXT_MID') else (175, 192, 214)

    def hint_line(L, opt, cx, y, words=True):
        s = '> turn_resolve.exe' if words else '>'
        px = HINT_TXT
        tw = L.tw(s, px, 'mono') if words else 10
        x0 = cx - (tw + 14) / 2
        if not words:
            L.line([(x0, y - 6), (x0 + 7, y), (x0, y + 6)], TXT_MID, 2.6)
            L.rect([x0 + tw + 4, y - 7, x0 + tw + 12, y + 7], fill=TXT_MID + (255,), r=1)
            return
        L.text((x0, y), s, px, 'mono', fill=TXT_MID, anchor='lm')
        L.rect([x0 + tw + 4, y - 8, x0 + tw + 12, y + 8], fill=TXT_MID + (255,), r=1)
    AS.hint_line = hint_line
    _oxt = lw_ui.xtext

    def xtext(cv, txt, x, y, px, *a, **k):
        if txt == '// BREAKER':
            px = max(px, NAME_SUB_TXT)
        return _oxt(cv, txt, x, y, px, *a, **k)
    lw_ui.xtext = xtext
    # wave queue: the W tags at 23 px mono, glyphs and width bars moved down to make room
    import gram as G
    from gram import INK as GINK, TMID, BED, SCHED as GSCHED
    import r2_glyphs as RG

    def queue_tickets(L, f, arcs):
        fut = [a for a in arcs if a['state'] == 'future']
        order = list(reversed(fut))
        x = 24
        tw_, th_ = 84, 64
        y0 = 24
        vals = {0: 1.0, 1: 0.70, 2: 0.50}
        for i, a in enumerate(order):
            n = a['wave'] + 1
            j = len(order) - 1 - i
            val = vals.get(j, 0.5)
            sc = lambda c: tuple(int(BED[q] + (c[q] - BED[q]) * val) for q in range(3))
            box = [x, y0, x + tw_, y0 + th_]
            FB.ticket(L, box, sc((217, 225, 234)), bool(a.get('climax')))
            if NOW['words']:
                L.text((x + 8, y0 + 15), 'W%d' % n, TICKET_TXT, 'mono', fill=sc((235, 240, 248)), anchor='lm')
            units = a['units']
            slot = (tw_ - 10) / max(1, len(units))
            for ui, (kind, wd) in enumerate(units):
                cx = x + 5 + slot * ui + slot / 2
                RG.kind_glyph(L, kind, 22, (cx, y0 + 39), sc((235, 240, 248)))
                bw = 4
                bx0 = cx - (wd * bw + (wd - 1) * 1.6) / 2
                for b in range(wd):
                    L.rect([bx0 + b * (bw + 1.6), y0 + 53, bx0 + b * (bw + 1.6) + bw, y0 + 56.4], fill=sc((226, 233, 242)) + (255,), r=1)
            for p in range(j):
                px = x + tw_ - 12 - p * 10
                L.ellipse([px - 4.6, y0 + 15 - 4.6, px + 4.6, y0 + 15 + 4.6], fill=GINK)
                L.ellipse([px - 3.0, y0 + 15 - 3.0, px + 3.0, y0 + 15 + 3.0], fill=TMID)
            if a.get('climax'):
                for t in range(3):
                    bx = x + 9 + t * 9
                    L.poly([(bx, y0 + th_ - 3), (bx + 4, y0 + th_ - 3), (bx + 7, y0 + th_ - 8.5), (bx + 3, y0 + th_ - 8.5)], fill=GSCHED, outline=(12, 10, 22), w=1.0)
            x += tw_ + 8
        return x
    FB.queue_tickets = queue_tickets
