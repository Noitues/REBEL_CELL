"""rb2_patch (2026-11-03 rebuild, stage 2): the remaining IMPL items of locked/REVIEW_RESPONSE.md, installed by lw_render right after rb_patch
(env RB2=0 skips it).  Every number here is a named knob; the value targets live in rb_tokens.

  1.5   the bill: every count is written as an Anton digit, the pip tally follows it as the second (smaller) mark; the operators are typeset
        (Anton '-' '+' '='); the SPLIT row is a written sum (ABSORBED + SOAK + YOU, no icon string); the NEXT row is COLD at 70 % value with its
        turn pip, its counts as digits under the SPLIT columns and hollow COLD tallies.  nowords keeps the full-size tallies and vector operators.
  3.7   WITHOUT TWIST: digits (2 -> 1), no "00 -> |" tally
  3.11  the resolve log: digits before its tallies (its words were already Mono 23, cap 16.1)
  2.14  wave tickets: kind glyphs and W tags at full value on every ticket (time stays on the ticket edge value and the turn pips); the wave
        count shows once: WAVES 6 LEFT on word plates, the six pips only on nowords (where the number is hidden)
  3.5   Heat: the atlas flame (round17 glyphs/placeholder_burn.png, "the shared 2-peak flame"), CRT_AMBER fill, ink outline 0.075 x size
  3.6   REFUND tag off the wheel: the board keeps the refund coin at the kill; the REFUND tag is a terminal tab docked under the refunded
        RAM coin (S material on the S plate)
  3.14  YOU strip: bigger segments (13.6 x 22) and an L7 hatch at a 5.4 px pitch, 1.5 px lines, so it stays a cross-hatch at 1x
  2.7   the hand: whole card visible with >= 12 px above y 1080 (hand_search.py): left 1035, cy0 904, fan 4 deg kept; p2 lift dx -24, cy 812
  2.3   played slots: upright (no fan tilt), card_render._liner draws the flat torn-paper outline"""
import math, sys, os
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageFilter
import rb_tokens as T

SRC = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/') + '/'

# ------------------------------------------------------------------ bill layout (y offsets inside the bill plate)
BILL_H = 216
EQ_BAND, EQ_LY, EQ_YY = (74, 126), 87, 111
SP_BAND, SP_LY, SP_YY = (130, 182), 143, 167
NX_BAND, NX_YY = (186, 212), 199
NUM_PX = 24                  # Anton digit of a bill count: cap 20.6 px
NUM_PX_SMALL = 22            # NEXT row, WITHOUT TWIST, resolve log: cap 18.9 px
NUM_GAP = 7                  # digit -> its tally
NUM_STROKE = 2.0
STW, STH, STP, STG = 6, 13, 8, 13      # the tally as the second mark: 6 x 13 r3, pitch 8, group gap 13
OP_PX = 40                   # typeset operator, Anton (its '+' ink is 14 x 19 px, '-' 12 px wide)
COLD_CHROMA = 0.45           # VISUAL_PLAN C: COLD = 45 % chroma (with NEXT_V value), filled
OP_GUT_MAX = 72              # widest gutter the eq row spreads to
SP_GUT = 58                  # split / next row gutter holding the '+'
NEXT_V = 0.70                # VISUAL_PLAN C: the NEXT row is COLD at 70 % value
TURN_PIP_R = 3.0             # the COLD turn pip before NEXT (6 px round, TEXT_MID)
# ------------------------------------------------------------------ wave tickets
TICKET_W, TICKET_H = 84, 70
TICKET_GLYPH_PX = 27         # kind glyph box; ink height measured >= 16 px (rb2 notes)
TICKET_TAG_Y, TICKET_GLYPH_Y, TICKET_BAR_Y = 15, 42, 60
# ------------------------------------------------------------------ Heat
HEAT_PX = 24                 # atlas flame box
HEAT_INK = 0.075             # outline width / size (ART_BIBLE 3.5)
# ------------------------------------------------------------------ REFUND tab under the RAM row
REFUND_TAB_W, REFUND_TAB_H, REFUND_TAB_GAP = 112, 32, 6
# ------------------------------------------------------------------ YOU strip (3.14)
YOU_SEG_W, YOU_SEG_H, YOU_SEG_P, YOU_GROUP_GAP = 13.6, 22.0, 16.4, 8.0
YOU_HATCH_PITCH, YOU_HATCH_W = 5.4, 1.5
# ------------------------------------------------------------------ hand (2.7) and played slots (2.3)
HAND_LEFT_CX, HAND_CY0 = 1035, 904
LIFT_DX, LIFT_CY2, LIFT_PUSH = -24, 812, 16

_A = [None]


def install(R, A, SKIN):
    _A[0] = A
    _bill()
    _chain()
    _waves()
    _tickets()
    _heat()
    _refund()
    _you()
    _hand(R)


# ======================================================================================== bill (1.5, 3.7)
def _bill():
    import hud2 as H
    from cv_lib import NOW
    THI, TMID, TLO = H.THI, H.TMID, H.TLO
    INK = H.INK
    H.G['bill_h'] = BILL_H
    KCOL = {'raw': H.RAW62, 'yel': H.PLAN, 'cyan': H.CYAN, 'braced': H.CYAN, 'rider': H.LAV, 'lands': H.HARM, 'absorb': H.CYAN,
            'soak': H.SOAK, 'through': H.HARM, 'ptl': H.HARM, 'lose': H.HARM}
    vk = lambda c, k: tuple(int(round(q * k)) for q in c[:3])

    def stpos(n):
        return [i * STP + (i // 5) * (STG - (STP - STW)) for i in range(n)]

    def stw(n):
        return (stpos(n)[-1] + STW) if n else STW

    def cold(c):
        """VISUAL_PLAN C, COLD (turn +1): 45 % chroma, 70 % value, filled (R51: 'hollow is growth only on chevrons')"""
        g = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
        return tuple(int(round((g + (q - g) * COLD_CHROMA) * NEXT_V)) for q in c[:3])

    def small_tally(L, x, y, kind, n, val=1.0, hollow=False):
        """the second mark: n small segments in groups of 5 (0 = one gone socket); hollow=True draws the COLD forecast (filled, desaturated)"""
        if n == 0:
            L.rect([x, y - STH / 2, x + STW, y + STH / 2], fill=(8, 14, 22), outline=vk(TLO, val), w=1.4, r=2)
            return x + STW
        col = cold(KCOL[kind]) if hollow else vk(KCOL[kind], val)
        for o in stpos(n):
            box = [x + o, y - STH / 2, x + o + STW, y + STH / 2]
            L.rect(box, fill=col, outline=INK, w=1.1, r=2)
            if kind == 'soak' and not hollow:
                cx = x + o + STW / 2
                L.line([(cx - 1.8, y - 2.0), (cx, y + 1.0), (cx + 1.8, y - 2.0)], INK, 1.4)
        return x + stw(n)

    def dw(L, n, px):
        return L.tw(str(n), px, 'anton')

    def group_w(L, n, px=NUM_PX):
        if not NOW['words']:
            return H.twidth(n)
        return dw(L, n, px) + NUM_GAP + stw(n)

    def num_tally(L, x, y, kind, n, px=NUM_PX, val=1.0, hollow=False, dcol=None):
        """a count: its Anton digit, then the small tally.  nowords: the full-size tally alone (the plate's number proxy)"""
        if not NOW['words']:
            if hollow:
                col = cold(KCOL[kind])
                if n == 0:
                    H.seg(L, x, y, 'gone', al=255)
                    return x + H.SEGW
                for o in H.tpos(n):
                    L.rect([x + o, y - 6.5, x + o + H.SEGW, y + 6.5], fill=col, outline=INK, w=1.4, r=3)
                return x + H.twidth(n)
            return H.tally(L, x, y, kind, n)
        c = vk(dcol or THI, val)
        L.text((x, y + 1), str(n), px, 'anton', fill=c, anchor='lm', stroke=NUM_STROKE)
        x += dw(L, n, px) + NUM_GAP
        return small_tally(L, x, y, kind, n, val, hollow)

    from PIL import ImageFont
    _opf = ImageFont.truetype(SRC + 'fonts/Anton-Regular.ttf', OP_PX * 4)

    def op(L, x, y, o, val=1.0):
        """a typeset operator (Anton), centred on the row by its own ink box (Anton's '+' sits low on the line)"""
        if not NOW['words']:
            return H.opdraw(L, x, y, o, al=255)
        bb = _opf.getbbox(o, anchor='mm')
        dy = -(bb[1] + bb[3]) / 2 / 4.0
        L.text((x, y + dy), o, OP_PX, 'anton', fill=vk(THI, val), anchor='mm', stroke=2.2)

    H._rb2 = dict(num_tally=num_tally, group_w=group_w, op=op, small_tally=small_tally, stw=stw)

    def el_eq_row(L, f, y, eq):
        sx0, sx1 = H.G['sx0'], H.G['sx1']
        H.inset(L, (sx0, y + EQ_BAND[0], sx1, y + EQ_BAND[1]))
        items = [('RAW', 'raw', eq['raw0'], None)]
        if eq['triggered']:
            items.append(('TRIG', 'yel', eq['triggered'], '-'))
        if eq['tower_from_trigger']:
            items.append(('TRIG LANDS', 'ptl', eq['tower_from_trigger'], '+'))
        items += [('SHOT', 'cyan', eq['shot_down'], '-'), ('BRACE', 'braced', eq['braced'], '-'), ('RIDER', 'rider', eq['rider'], '-'),
                  ('LANDS', 'lands', eq['lands'], '=')]
        ly, yy = y + EQ_LY, y + EQ_YY
        cws = [max(H.ttw(L, nm, H.LBL_PX, 'mono', H.LBL_TRK), group_w(L, n)) for nm, k, n, o in items]
        avail = sx1 - sx0 - 32
        gut = min(OP_GUT_MAX, (avail - sum(cws)) / max(1, len(items) - 1))
        x = sx0 + 16 + max(0, (avail - sum(cws) - gut * (len(items) - 1)) / 2)
        bx = {}
        for (nm, kind, n, o), cw in zip(items, cws):
            if o:
                op(L, x - gut / 2, yy, o)
            gw = group_w(L, n)
            H.tag(L, x + cw / 2, ly, nm, 'mm')
            num_tally(L, x + (cw - gw) / 2, yy, kind, n)
            bx[nm] = (x, cw)
            x += cw + gut
        for k in ('eq_row', 'eq_labels', 'operators', 'tally_segments'):
            H.reg(k, (sx0, y + EQ_BAND[0], sx1, y + EQ_BAND[1]))
        if 'BRACE' in bx and 'RIDER' in bx:
            H.reg('empty_socket', (bx['BRACE'][0] - 4, y + EQ_BAND[0] + 2, bx['RIDER'][0] + bx['RIDER'][1] + 4, y + EQ_BAND[1] - 2))
        if 'TRIG' in bx:
            H.reg('trig_groups', (bx['TRIG'][0] - 14, y + EQ_BAND[0] + 2, bx['TRIG'][0] + bx['TRIG'][1] + 14, y + EQ_BAND[1] - 2))
    H.el_eq_row = el_eq_row

    def split_cols(L, f, eq):
        nx = f['next']
        g = [('ABSORBED', 'absorb', eq['absorbed'], nx['absorbed']), ('SOAK', 'soak', eq['soaked'], nx['slost']), ('YOU', 'through', eq['through'], nx['taken'])]
        x = H.G['sx0'] + 16
        x += H.ttw(L, 'SPLIT', H.LBL_PX, 'mono', H.LBL_TRK) + 30
        cols = {}
        for gi, (nm, kind, n, m) in enumerate(g):
            gmax = max(group_w(L, n), group_w(L, m, NUM_PX_SMALL))
            cw = max(H.ttw(L, nm, H.LBL_PX, 'mono', H.LBL_TRK), gmax)
            cols[nm] = dict(x=x, cw=cw, xg=x + (cw - gmax) / 2, kind=kind, n=n, m=m, op_x=(x - SP_GUT / 2) if gi else None)
            x += cw + SP_GUT
        return cols, x - SP_GUT

    def el_split_row(L, f, y, eq):
        sx0, sx1 = H.G['sx0'], H.G['sx1']
        H.inset(L, (sx0, y + SP_BAND[0], sx1, y + SP_BAND[1]))
        ly, yy = y + SP_LY, y + SP_YY
        H.rowtag(L, sx0 + 16, yy, 'SPLIT')
        cols, xe = split_cols(L, f, eq)
        for nm, c in cols.items():
            if c['op_x'] is not None:
                op(L, c['op_x'], yy, '+')
            H.tag(L, c['x'] + c['cw'] / 2, ly, nm, 'mm')
            num_tally(L, c['xg'], yy, c['kind'], c['n'])
        H.R['_split_cols'] = cols
        H.reg('split_row', (sx0, y + SP_BAND[0], sx1, y + SP_BAND[1]))
        H.reg('route_arrows', (sx0 + 16, y + SP_BAND[0] + 4, xe, y + SP_BAND[1] - 4))
    H.el_split_row = el_split_row

    def el_next_row(L, f, y, tw_pay=None):
        sx0, sx1 = H.G['sx0'], H.G['sx1']
        yg = y + NX_YY
        H.inset(L, (sx0, y + NX_BAND[0], sx1, y + NX_BAND[1]))
        x = sx0 + 16
        L.ellipse([x - TURN_PIP_R, yg - TURN_PIP_R, x + TURN_PIP_R, yg + TURN_PIP_R], fill=vk(TMID, 1.0), outline=INK, w=1.0)
        H.txt(L, x + 10, yg, 'NEXT', H.LBL_PX, vk(TMID, NEXT_V), 'mono', 'lm', H.LBL_TRK)
        cols = H.R.get('_split_cols') or split_cols(L, f, f['pv']['eq'])[0]
        e_all = sx0 + 100
        for nm, c in cols.items():
            if c['op_x'] is not None:
                op(L, c['op_x'], yg, '+', NEXT_V)
            e = num_tally(L, c['xg'], yg, c['kind'], c['m'], px=NUM_PX_SMALL, val=NEXT_V, hollow=True)
            e_all = max(e_all, e)
        H.reg('next_row', (sx0, y + NX_BAND[0], sx1, y + NX_BAND[1]))
        if tw_pay:
            without_twist(L, f, yg, tw_pay, f['next'], e_all + 22)
    H.el_next_row = el_next_row

    def without_twist(L, f, yg, tp, nx, xmin):
        """3.7: the twist's payoff as digits: without the twist you take wo next turn, with it wi (COLD: a forecast)"""
        wo, wi = tp['without']['taken'], nx['taken']
        lab_w = H.ttw(L, 'WITHOUT TWIST', H.LBL_PX, 'mono', H.LBL_TRK)
        cold = T.COLD_CHEV
        if NOW['words']:
            need = 24 + 8 + lab_w + 12 + dw(L, wo, NUM_PX_SMALL) + 10 + 26 + 10 + dw(L, wi, NUM_PX_SMALL)
        else:
            need = 24 + 8 + H.twidth(wo) + 10 + 26 + 10 + H.twidth(wi)
        xt = max(xmin, sx1_() - 16 - need)
        L.ellipse([xt, yg - 12, xt + 24, yg + 12], fill=(30, 26, 6), outline=H.PLAN, w=2.2)
        L.glyph(H.GL['Twist'], 17, (xt + 12, yg), H.PLAN)
        x = xt + 32
        if NOW['words']:
            x += H.txt(L, x, yg, 'WITHOUT TWIST', H.LBL_PX, H.PLAN, 'mono', 'lm', H.LBL_TRK) + 12
            L.text((x, yg + 1), str(wo), NUM_PX_SMALL, 'anton', fill=cold, anchor='lm', stroke=NUM_STROKE)
            x += dw(L, wo, NUM_PX_SMALL) + 10
        else:
            for o in H.tpos(wo):
                L.rect([x + o, yg - 6.5, x + o + H.SEGW, yg + 6.5], fill=cold, outline=INK, w=1.4, r=3)
            x += H.twidth(wo) + 10
        H.arrow(L, x, yg, H.PLAN, 26, 7)
        x += 36
        if NOW['words']:
            L.text((x, yg + 1), str(wi), NUM_PX_SMALL, 'anton', fill=cold, anchor='lm', stroke=NUM_STROKE)
            e = x + dw(L, wi, NUM_PX_SMALL)
        else:
            e = H.tally(L, x, yg, 'through', wi)
        H.reg('without_twist_row', (xt - 8, yg - 16, e + 10, yg + 16))

    def sx1_():
        return H.G['sx1']
    H.without_twist = without_twist


# ======================================================================================== resolve log digits (3.11 / 1.5)
def _chain():
    import hud2 as H
    from cv_lib import NOW

    def chain_strip(L, f, y):
        steps = f['chain']
        h = H.G['chain_h']
        x0, x1, ox = H.G['px0'], H.G['px1'], H.G['ox']
        ph = H.G['chain_pad'] + len(steps) * h
        H.P(L, (x0, y, x1, y + ph), 'chain')
        yy = y + H.G['chain_pad'] / 2
        xt0, xp0 = ox + 236, ox + 236 + 160
        nt = H._rb2['num_tally']
        for i, st in enumerate(steps):
            cy = yy + h / 2
            if i:
                L.line([(x0 + 10, yy), (x1 - 10, yy)], H.CYAN + (46,), 1.2)
            if NOW['words']:
                L.text((ox + 14, cy + 1), str(i + 1), H.LBL_PX, 'mono', fill=H.TMID + (255,), anchor='mm')
            H.chain_glyph(L, st, ox + 50, cy)
            H.txt(L, ox + 76, cy, st['name'], H.LBL_PX, H.TMID, 'mono', 'lm', H.LBL_TRK)
            xt = xt0
            kinds = {'raw': 'lands'}
            for k_, n in st['pips']:
                if k_ in ('txt', 'refund') or not n:
                    continue
                xt = nt(L, xt, cy, kinds.get(k_, k_), n, px=NUM_PX_SMALL) + 16
            for k_, n in st['pips']:
                if k_ == 'refund':
                    H.coin(L, xt + 9, cy, 20, True)
                    xt += 28
            for k_, n in st['pips']:
                if k_ == 'txt':
                    H.txt(L, max(xp0, xt + 12), cy, n, H.LBL_PX, H.TMID, 'mono', 'lm', 0.0)
            H.reg('chain_row_%d' % i, (x0, yy, x1, yy + h))
            yy += h
        H.reg('chain_strip', (x0, y, x1, y + ph))
        return y + ph
    H.chain_strip = chain_strip


# ======================================================================================== the wave count shows once (2.14)
def _waves():
    import hud2 as H
    from cv_lib import NOW
    _o = H.el_waves_left

    def el_waves_left(L, f, box, xr):
        """word plates: WAVES n LEFT only (the six pips repeated the number); nowords: the pips carry the count (the number is hidden)"""
        if not NOW['words']:
            return _o(L, f, box, xr)
        cy = (box[1] + box[3]) / 2
        s = 'WAVES %d LEFT' % f['waves_left']
        wc = L.tw(s, 20, 'anton') + 22
        xc = xr - wc
        L.rect([xc, cy - 15, xc + wc, cy + 15], fill=(26, 14, 4, 235), outline=H.SCHED, w=2, r=6)
        L.text((xc + wc / 2, cy + 1.5), s, 20, 'anton', fill=H.SCHED, anchor='mm')
        H.reg('waves_left', (xc - 6, box[1], xr + 6, box[3]))
    H.el_waves_left = el_waves_left


# ======================================================================================== wave tickets at full value (2.14)
def _tickets():
    import f1_board as FB
    import r2_glyphs as RG
    from gram import INK as GINK, TMID, BED, SCHED as GSCHED
    from cv_lib import NOW
    import rb_patch as RBP
    FULL = (235, 240, 248)

    def queue_tickets(L, f, arcs):
        fut = [a for a in arcs if a['state'] == 'future']
        order = list(reversed(fut))
        x, y0 = 24, 24
        tw_, th_ = TICKET_W, TICKET_H
        vals = {0: 1.0, 1: 0.70, 2: 0.50}
        for i, a in enumerate(order):
            n = a['wave'] + 1
            j = len(order) - 1 - i
            val = vals.get(j, 0.5)
            sc = lambda c: tuple(int(BED[q] + (c[q] - BED[q]) * val) for q in range(3))
            box = [x, y0, x + tw_, y0 + th_]
            FB.ticket(L, box, sc((217, 225, 234)), bool(a.get('climax')))      # time: the ticket edge value (W6 50, W5 70, W4 100 %) + turn pips
            if NOW['words']:
                L.text((x + 8, y0 + TICKET_TAG_Y), 'W%d' % n, RBP.TICKET_TXT, 'mono', fill=FULL, anchor='lm')
            units = a['units']
            slot = (tw_ - 10) / max(1, len(units))
            for ui, (kind, wd) in enumerate(units):
                cx = x + 5 + slot * ui + slot / 2
                RG.kind_glyph(L, kind, TICKET_GLYPH_PX, (cx, y0 + TICKET_GLYPH_Y), FULL)
                bw = 4
                bx0 = cx - (wd * bw + (wd - 1) * 1.6) / 2
                for b in range(wd):
                    L.rect([bx0 + b * (bw + 1.6), y0 + TICKET_BAR_Y, bx0 + b * (bw + 1.6) + bw, y0 + TICKET_BAR_Y + 3.4], fill=(226, 233, 242, 255), r=1)
            for p in range(j):
                px = x + tw_ - 12 - p * 10
                L.ellipse([px - 4.6, y0 + TICKET_TAG_Y - 4.6, px + 4.6, y0 + TICKET_TAG_Y + 4.6], fill=GINK)
                L.ellipse([px - 3.0, y0 + TICKET_TAG_Y - 3.0, px + 3.0, y0 + TICKET_TAG_Y + 3.0], fill=TMID)
            if a.get('climax'):
                for t in range(3):
                    bx = x + 9 + t * 9
                    L.poly([(bx, y0 + th_ - 3), (bx + 4, y0 + th_ - 3), (bx + 7, y0 + th_ - 8.5), (bx + 3, y0 + th_ - 8.5)], fill=GSCHED, outline=(12, 10, 22), w=1.0)
            x += tw_ + 8
        return x
    FB.queue_tickets = queue_tickets


# ======================================================================================== Heat: the atlas flame (3.5)
_FL = {}


def flame_stamp(px, k, col):
    key = (px, k, tuple(col))
    if key in _FL:
        return _FL[key]
    from r2_glyphs import INK
    s = int(round(px * k))
    iw = max(1.5, s * HEAT_INK)
    pad = int(iw) + 3
    src = Image.open(SRC + 'glyphs/ATLAS_BURN.png').convert('RGBA')
    m = src.split()[3]
    bb = m.getbbox()
    m = m.crop(bb)
    sc = s / max(m.size)
    m = m.resize((max(1, int(round(m.width * sc))), max(1, int(round(m.height * sc)))), Image.LANCZOS)
    big = Image.new('L', (s + 2 * pad, s + 2 * pad), 0)
    big.paste(m, (pad + (s - m.width) // 2, pad + (s - m.height) // 2))
    dil = big.filter(ImageFilter.GaussianBlur(iw * 0.55)).point(lambda v: 255 if v > 38 else int(v * 255 / 38))
    out = Image.new('RGBA', big.size, (0, 0, 0, 0))
    out.paste(tuple(INK) + (255,), mask=dil)
    out.paste(tuple(col) + (255,), mask=big)
    _FL[key] = out
    return out


def _heat():
    import obj2 as O2

    def draw_flame(L, cx, cy):
        im = flame_stamp(HEAT_PX, L.k, T.TOKENS['CRT_AMBER'])
        L.im.alpha_composite(im, (int(round(cx * L.k - im.width / 2)), int(round(cy * L.k - im.height / 2))))
    O2.draw_flame = draw_flame


# ======================================================================================== REFUND tag off the wheel (3.6)
def _refund():
    import a2_plan as P2
    import obj2 as O2
    import hud2 as H
    from cv_lib import NOW

    def refund_place(L, f, opt='A', tok='A', words=True):
        """the board keeps only the refund coin at the kill (X: fx_refund); the REFUND word is on the HUD, under the refunded RAM coin"""
        from cv_lib import C, ppx
        x, y = ppx(C, P2.rmid(0) - 1, 203)
        P2.refund_token(L, x, y, 44, tok)
    P2.refund_place = refund_place
    _orr = O2.resources_row

    def resources_row(L, f, y):
        yb = _orr(L, f, y)
        bx = O2.R.get('ram_refund')
        if not f.get('refunds') or bx is None:
            return yb
        cx = (bx[0] + bx[2]) / 2
        t0 = yb + REFUND_TAB_GAP
        box = (cx - REFUND_TAB_W / 2, t0, cx + REFUND_TAB_W / 2, t0 + REFUND_TAB_H)
        L.line([(cx, yb - 2), (cx, t0 + 2)], H.CYAN, 2.0)                     # the tab hangs from the refunded coin's bay
        H.P(L, box, 'plate')
        if NOW['words']:
            H.txt(L, cx, t0 + REFUND_TAB_H / 2, 'REFUND', H.LBL_PX, H.CYAN, 'mono', 'mm', H.LBL_TRK)
        else:
            H.coin(L, cx, t0 + REFUND_TAB_H / 2, 18, True)
        O2.R['refund_tab'] = box
        return t0 + REFUND_TAB_H
    O2.resources_row = resources_row
    H.ram_row = resources_row


# ======================================================================================== YOU strip (3.14)
def _you():
    import st_ui
    import lw_ui as LU
    from xf_gfx import Cv, rough, grow, shift, shrink, hatch_field, hx, TONER, MAG, ANTON, xtext, copier_edge, GAINC, HARMC
    from xf_cards import rect

    def you_strip(f, ss=3, nw=False):
        x0, y0, w, h = 1068, 96, 346, 52
        cv = Cv(x0, y0, w, h, ss)
        strip = LU.jag_rect(cv, x0 + 8, y0 + 6, x0 + w - 8, y0 + h - 6, -0.4, 17)
        LU.sticker(cv, strip, 17, halo=3.2, key=2.2)
        cv.paint(copier_edge(cv, strip, 5, 2.4, 0.5, (0.0, 1.0)), TONER)
        if nw:
            cv.paint(rect(cv, x0 + 18, y0 + 16, x0 + 58, y0 + 36), MAG)
        else:
            xtext(cv, 'YOU', x0 + 40, y0 + 27, 31, ANTON, fill=TONER, off=(1.8, 1.8), off_col=MAG, wob=0.2, track=0.6, rot=-2, seed=2)
        n_pend = f['hp'] - f['pv']['hp_after']
        n_lit = f['pv']['hp_after']
        xs = x0 + 72
        hf = hatch_field(cv, (45, 135), YOU_HATCH_PITCH, YOU_HATCH_W, 301, 0.2)
        for i in range(15):
            g, k = divmod(i, 5)
            xx = xs + g * (5 * YOU_SEG_P + YOU_GROUP_GAP) + k * YOU_SEG_P
            m = rough(rect(cv, xx, y0 + 27 - YOU_SEG_H / 2, xx + YOU_SEG_W, y0 + 27 + YOU_SEG_H / 2), cv, 0.3, 6.0, 200 + i)
            cv.paint(grow(m, 1.5 * ss), TONER)
            if i < n_lit:
                cv.paint(m, GAINC)
                cv.paint(np.clip(m - shift(m, 0.8 * ss, 1.2 * ss), 0, 1) * m, LU.WH, 0.8)
            elif i < n_lit + n_pend:
                cv.paint(m, hx('1A0E12'))
                inner = shrink(m, 1.2 * ss)
                cv.paint(hf * inner, HARMC)
                cv.paint(np.clip(inner - shrink(inner, 1.4 * ss), 0, 1), HARMC)
        return cv.to_image(), (x0, y0)
    st_ui.you_strip = you_strip
    LU.you_strip = you_strip


# ======================================================================================== hand (2.7) and played slots (2.3)
def _hand(R):
    import f1_hand as FH
    import rb_patch as RBP
    FH.LEFT_CX, FH.CY0 = HAND_LEFT_CX, HAND_CY0
    RBP.LIFT_DX, RBP.LIFT_CY2, RBP.LIFT_PUSH = LIFT_DX, LIFT_CY2, LIFT_PUSH

    def draw_hand(base, J, beat, nw=False, lift=None, dim_others=None):
        """rb_patch's hand with the played slots upright (2.3: a flat torn-paper outline, no fan tilt)"""
        hand, played, hov = FH.hand_lists(J, beat)
        if lift is not None:
            hov = hand.index(lift)
        n = len(hand) + len(played)
        sl = FH.slots(n)
        own = beat == 'p2' and lift is None
        push = RBP.LIFT_PUSH if own else FH.HOV_PUSH
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
            FH.put(base, Image.fromarray(a_.astype(np.uint8), 'RGBA'), s['cx'], s['cy'], s['ang'], FH.CARD_SCALE)
        for j, nm in enumerate(played):
            s = sl[len(hand) + j]
            FH.put(base, FH.played_slot(nm, nw), s['cx'], s['cy'], 0.0, FH.CARD_SCALE, shadow=False)
        if hov is not None:
            s = sl[hov]
            im = FH.card_hi(hand[hov], nw, 'hover')
            FH.put(base, im, s['cx'] + (RBP.LIFT_DX if own else 0), RBP.LIFT_CY2 if own else FH.LIFT_CY, 0, FH.LIFT_S * FH.CARD_SCALE, shadow=True, off=(6, 12), blur=10)
        return sl
    FH.draw_hand = draw_hand
