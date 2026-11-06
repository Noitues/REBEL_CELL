"""hud_rows (2026-11-04 round 2, call C8; reviewer's question 3): ONE row grid for the board HUD and the hover HUD, so no row moves when a hover
starts.  The board bill now has, at all times, the hover set's room round the hero digits (the pencil ring's top and bottom runs,
HERO_ROOM_T / HERO_ROOM_B, and its wider digit gaps) and four NEXT row slots (OPT_SLOTS: the NEXT row plus three option rows at
OPT_PITCH).  Empty slots stay empty; h04 fills them with the Twist option rows, p2 with its three plan options (the former option chips, now
rows in the reserved slots).  On p3 the resolve log takes the option-row space (no hover starts during the resolve beat; every row above it is
unchanged).

The numbers are the hover set's (rebuild/hover/src/hv_core.py: HERO_ROOM_T 19, HERO_ROOM_B 26, HERO_DX 16, HERO_GAP 32, OPT_PITCH 30), so
the hover HUD equals the board HUD when hv_core uses hud2.bill_box with OPT['rows'] / OPT['draw'] instead of adding its own room.
ROWS (filled on every draw) holds the row y positions for the checks (rb_checks: HUD rows)."""
import sys
sys.dont_write_bytecode = True

HERO_ROOM_T = 19
HERO_ROOM_B = 26
HERO_DX = 16
HERO_GAP = 32
OPT_PITCH = 30
OPT_BAND = 26
OPT_SLOTS = 4                      # the NEXT row + three option rows (h04: four Twist options)
OPT_GLYPH_PX = 20                  # plan glyphs in an option row (the chips used 24 in a 38 px chip)
OPT_PAIR_PX = 24                   # the option's LANDS -> THROUGH pair (Anton 24, cap 20.6; the chips used 26)
OPT_SEL_W = 3                      # the selected / best option's neutral TEXT_HI edge (VISUAL_PLAN A.5 2026-11-04)
PANEL_GAP = 4                      # bill -> WIN -> RAM panel gap (hud2 G['gap'] 8 kept after the header).  2026-11-04 round 2 (C6 x C8): with the
                                   # option rows reserved the p2 HUD ends at the RAM row; 4 px per gap gives the straight-up lift its room
REFUND_TAB_W = 96                  # the REFUND tab under the RAM coin (rb2: 112): its right edge clears the lifted card's left edge
OPT = {'rows': None, 'draw': None}  # hover hook: rows (a list) and draw(L, f, yy, rows) draw the option NEXT rows into the slots
ROWS = {}


def bill_h(reserve=True):
    import rb2_patch as RB2
    return RB2.BILL_H + HERO_ROOM_T + HERO_ROOM_B + ((OPT_SLOTS - 1) * OPT_PITCH if reserve else 0)


def install(R, A):
    import hud2 as H
    import f1_hand as FH
    import rb2_patch as RB2
    import rb3_patch as RB3
    from cv_lib import NOW
    RB2.REFUND_TAB_W = REFUND_TAB_W

    def hero_pair(L, x, y, lands, through):
        """hero_pair with the ring room: labels keep their row, the digits sit HERO_ROOM_T lower, digit -> arrow -> digit gaps HERO_GAP"""
        if not NOW['words']:
            return hero_nw(L, x, y, lands, through)
        tcol = H.HARM if through else H.GAINC
        wl = L.tw(str(lands), 58, 'anton')
        wt = L.tw(str(through), 58, 'anton')
        H.rowtag(L, x, y - 40 - HERO_ROOM_T, 'LANDS', centre=x + wl / 2)
        L.text((x, y), str(lands), 58, 'anton', fill=H.WHITE, anchor='lm', stroke=4)
        ax = x + wl + HERO_GAP
        H.arrow(L, ax, y, H.THI, 40, 14)
        xt = ax + 40 + HERO_GAP
        H.rowtag(L, xt, y - 40 - HERO_ROOM_T, 'THROUGH', centre=xt + wt / 2)
        L.text((xt, y), str(through), 58, 'anton', fill=tcol, anchor='lm', stroke=4)
        H.reg('hero_pair', (x - 6, y - 52 - HERO_ROOM_T, xt + wt + 8, y + 38))
        H.reg('row_tags_hero', H.R['hero_pair'])
        H.R['_hero_xy'] = dict(y=y, lands=(x, wl), through=(xt, wt), arrow=(ax, 40))

    def hero_nw(L, x, y, lands, through):
        sw, sh, sp = 13, 30, 17
        e1 = x
        for i in range(lands):
            xi = x + i * sp + (i // 5) * 12
            L.rect([xi, y - sh / 2, xi + sw, y + sh / 2], fill=H.WHITE + (255,), outline=H.INK, w=2, r=3)
            e1 = xi + sw
        ax = e1 + HERO_GAP
        H.arrow(L, ax, y, H.THI, 38, 14)
        xt = ax + 38 + HERO_GAP
        e2 = xt
        for i in range(through):
            xi = xt + i * sp + (i // 5) * 12
            L.rect([xi, y - sh / 2, xi + sw, y + sh / 2], fill=H.HARM + (255,), outline=H.INK, w=2, r=3)
            e2 = xi + sw
        H.reg('hero_nowords_proxy', (x - 6, y - 24, e2 + 6, y + 24))
        H.R['_hero_xy'] = dict(y=y, lands=(x, e1 - x), through=(xt, max(0, e2 - xt)), arrow=(ax, 38), nw=True)
    H.hero_pair, H.hero_nw = hero_pair, hero_nw

    def option_row(L, cy, name, plan, soak, eq, sel=False, refund=False):
        """one plan option in a reserved option-row slot: plan glyphs, name, outcome bar, LANDS -> THROUGH; the best / selected row takes
        the neutral TEXT_HI edge"""
        sx0, sx1 = H.G['sx0'], H.G['sx1']
        box = (sx0, cy - OPT_BAND / 2, sx1, cy + OPT_BAND / 2)
        H.inset(L, box)
        if sel:
            L.rect(list(box), outline=H.THI, w=OPT_SEL_W, r=5)
        x = H.G['ox'] + 12
        items = [c[0] for c in plan if c[0] in H.GL]
        for i, nm in enumerate(items):
            L.glyph(H.GL[nm], OPT_GLYPH_PX, (x + OPT_GLYPH_PX / 2, cy), H.CYAN if nm == 'Brace' else H.THI)
            x += OPT_GLYPH_PX + 4
            if i < len(items) - 1:
                L.ellipse([x, cy - 1.6, x + 3, cy + 1.4], fill=H.TLO)
                x += 5
        if soak:
            x += 6
            H.dest_funnel(L, x + 12, cy + 2, pip=False)
            x += 28
        if refund:
            x += 4
            H.coin(L, x + 10, cy, 20, True)
            x += 24
        H.chip_name(L, H.G['ox'] + 196, cy, name)
        H.chip_bar(L, H.G['ox'] + H.CHIP_BAR_DX, cy, eq)
        if NOW['words']:
            xr = H.G['px1'] - 20
            ln, th = eq['lands'], eq['through']
            wt = L.tw(str(th), OPT_PAIR_PX, 'anton')
            L.text((xr, cy + 1), str(th), OPT_PAIR_PX, 'anton', fill=H.HARM if th else H.GAINC, anchor='rm', stroke=2.5)
            H.arrow(L, xr - wt - 34, cy, H.THI, 24, 7)
            L.text((xr - wt - 42, cy + 1), str(ln), OPT_PAIR_PX, 'anton', fill=H.WHITE, anchor='rm', stroke=2.5)
        H.reg('option_row_%s' % name, box)

    def bill_box(L, f, y, pencil=False, plan_tag=None, twist_pay=None, extra=None, reserve=True, options=None):
        eq = f['pv']['eq']
        rows = OPT['rows']
        H.G['bill_h'] = bill_h(reserve)
        H.el_bill_frame(L, y)
        x = H.G['ox'] + 56
        e = H.hp_tally(L, f, x, y + 46 + HERO_ROOM_T)
        if pencil:
            H.el_plan_underline(L, f, y)
        H.hero_pair(L, e + 34 + HERO_DX, y + 54 + HERO_ROOM_T, eq['lands'], eq['through'])
        if plan_tag:
            H.el_best_tag(L, y, plan_tag)
        yy = y + HERO_ROOM_T + HERO_ROOM_B
        H.el_eq_row(L, f, yy, eq)
        H.el_split_row(L, f, yy, eq)
        if rows and OPT['draw'] is not None:
            OPT['draw'](L, f, yy, rows)
        else:
            H.el_next_row(L, f, yy, twist_pay)
        slots = [yy + RB2.NX_YY + k * OPT_PITCH for k in range(OPT_SLOTS if reserve else 1)]
        if options and reserve:
            for k, o in enumerate(options[:OPT_SLOTS - 1]):
                option_row(L, slots[k + 1], *o)
        ROWS.update(bill_top=y, bill_bottom=y + H.G['bill_h'], hero_label_y=y + 54 + HERO_ROOM_T - 40 - HERO_ROOM_T, hero_digit_y=y + 54 + HERO_ROOM_T,
                    eq_label_y=yy + RB2.EQ_LY, eq_y=yy + RB2.EQ_YY, split_label_y=yy + RB2.SP_LY, split_y=yy + RB2.SP_YY, next_y=yy + RB2.NX_YY,
                    slots=slots, reserve=reserve, options=len(options or []), hover_rows=len(rows or []))
        H.reg('_bill_room', (H.G['px0'], y, H.G['px1'], y + H.G['bill_h']))
        return y + H.G['bill_h']
    H.bill_box = bill_box

    def draw_hud(L, f, beat, extra=None):
        H.R.clear()
        ROWS.clear()
        extra = extra or {}
        f = dict(f)
        if extra.get('through0'):
            pv = dict(f['pv']); eq = dict(pv['eq']); eq.update(through=0, absorbed=eq['absorbed'] + eq['through']); pv['eq'] = eq; pv['hp_after'] = f['hp']; f['pv'] = pv
        if extra.get('waves3'):
            f['waves_left'] = 3
        if extra.get('hp_gone'):
            f['hp'] = 11
        if extra.get('trig_lands'):
            pv = dict(f['pv']); eq = dict(pv['eq']); eq['tower_from_trigger'] = 2; pv['eq'] = eq; f['pv'] = pv
        if extra.get('soaked'):
            pv = dict(f['pv']); eq = dict(pv['eq']); eq.update(soaked=3, absorbed=3); pv['eq'] = eq; f['pv'] = pv
        J = H.J
        yb = H.header(L, f)
        y = yb + H.G['gap']
        pencil = beat == 'p2'
        tp = J['twist_payoff'] if beat in ('p2', 'p3') else None
        options = None
        if beat == 'p2':
            options = [('TRIGGER ONLY', J['meta']['lines']['trigger'][0], J['meta']['lines']['trigger'][1], J['f2t']['pv']['eq'], False, J['f2t']['refunds'] > 0),
                       ('BRACE + SOAK ONLY', J['meta']['lines']['brace'][0], J['meta']['lines']['brace'][1], J['f2b']['pv']['eq'], False, False),
                       ('BEST: ALL THREE', J['meta']['hero'], J['meta']['hero_end'], f['pv']['eq'], True, f['refunds'] > 0)]
        y0 = y
        y = H.bill_box(L, f, y, pencil=pencil, plan_tag='BEST LINE' if beat in ('p2', 'p3') else None, twist_pay=tp,
                       reserve=beat != 'p3', options=options) + PANEL_GAP
        if options:
            for nm in ('option_chips', 'option_plan_glyphs', 'option_name_label', 'option_outcome_bar', 'option_pair'):
                H.reg(nm, (H.G['px0'], ROWS['slots'][1] - OPT_BAND / 2, H.G['px1'], ROWS['slots'][-1] + OPT_BAND / 2))
        if beat == 'p3':
            ROWS['chain_top'] = y
            y = H.chain_strip(L, f, y) + PANEL_GAP
            for nm in ('chain_step_discs', 'chain_step_glyphs', 'chain_step_names', 'chain_result_tallies', 'chain_result_prose'):
                H.reg(nm, H.R['chain_strip'])
        ROWS['obj_top'] = y
        y = H.objectives_row(L, f, y) + PANEL_GAP
        ROWS['ram_top'] = y
        y = H.ram_row(L, f, y)
        ROWS['hud_bottom'] = y
        H.reg('_column', (H.G['px0'], 12, H.G['px1'], y))
        H.reg('layout_grid', (H.G['px0'] - 40, 0, H.G['px1'] + 24, y + 20))
        H.reg('terminal_plate_kit', (H.G['px0'] - 12, 6, H.G['px1'] + 12, y + 8))
        H.reg('hud_scrim', (H.G['px0'] - 120, 0, 1920, 640))
        H.reg('row_tags', H.R['bill_frame'])
        return y
    H.draw_hud = draw_hud
    _oui = FH.ui_img

    def ui_img(kind, nw, f=None, seed=0):
        """the YOU strip rides with the hero row (HERO_ROOM_T lower, as on every hover plate)"""
        im, (x0, y0) = _oui(kind, nw, f, seed)
        if kind == 'you':
            return im, (x0, y0 + HERO_ROOM_T)
        return im, (x0, y0)
    FH.ui_img = ui_img
