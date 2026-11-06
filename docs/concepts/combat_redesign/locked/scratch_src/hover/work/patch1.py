import re
p = 'D:/rc_scratch/combat_redesign/locked/hover/src/hz_core.py'
s = open(p, encoding='utf-8').read()
s = s.replace("""    cy = (box[1] + box[3]) / 2 - 7
    if pl['through'] != lv['through']:
        tw = L.tw(str(pl['through']), 58, 'anton')
        xt = box[2] - 8 - tw
        HL.pencil_oval(L, xt + tw / 2, cy, tw / 2 + 12, 31, seed=3); out.append('through')
    if pl['lands'] != lv['lands']:
        lw = L.tw(str(pl['lands']), 58, 'anton')
        HL.pencil_oval(L, box[0] + 6 + lw / 2, cy, lw / 2 + 12, 31, seed=4); out.append('lands')""",
"""    cy = (box[1] + box[3]) / 2 - 3
    if pl['through'] != lv['through']:
        tw = L.tw(str(pl['through']), 58, 'anton')
        xt = box[2] - 8 - tw
        HL.pencil_oval(L, xt + tw / 2, cy, tw / 2 + 11, 26, seed=3); out.append('through')
    if pl['lands'] != lv['lands']:
        lw = L.tw(str(pl['lands']), 58, 'anton')
        HL.pencil_oval(L, box[0] + 6 + lw / 2, cy, lw / 2 + 11, 26, seed=4); out.append('lands')""")
s = s.replace('''def you_mark(L, f_live, f_plan):
    """the YOU strip's HP after the turn changes: a pencil box round the strip's pip run"""
    if f_live['pv']['hp_after'] != f_plan['pv']['hp_after']:
        HL.pencil_box(L, (1136, 106, 1396, 142), seed=31, pad=3)
        return True
    return False''', '''def you_pip_x(i):
    g, k = divmod(i, 5)
    return 1068 + 72 + g * (5 * 15.6 + 8) + k * 15.6        # lw_ui.you_strip: xs + group + pitch; pip 12.6 x 17 at y 123


def you_mark(L, f_live, f_plan):
    """the YOU strip's HP after the turn changes: a pencil ring round exactly the pips that change (kept <-> lost at END TURN)"""
    a, b = sorted((f_live['pv']['hp_after'], f_plan['pv']['hp_after']))
    if a == b:
        return False
    x0, x1 = you_pip_x(a), you_pip_x(b - 1) + 12.6
    HL.pencil_oval(L, (x0 + x1) / 2, 123, (x1 - x0) / 2 + 9, 17, seed=31, w=3.0, ink=1.6)
    return [a, b]''')
s = s.replace('''def _set_hand(hand, played=()):''', '''_oslots = FH.slots
HOV = {'i': None, 'dx': 0.0}


def _slots(n):
    sl = _oslots(n)
    if HOV['i'] is not None and HOV['dx']:
        sl[HOV['i']]['cx'] += HOV['dx']
    return sl


FH.slots = _slots


def _set_hand(hand, played=()):''')
s = s.replace('''    hand_lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    FH.draw_hand(hand_lay, A.J, 'p1', nw=not words, lift=lift, dim_others=(HAND_K / FH.REST_V) if lift is not None else (HAND_K / FH.REST_V))''',
'''    HOV['i'] = hand.index(lift) if lift is not None else None
    yy_, xx_ = np.mgrid[0:H, 0:W]
    d_ = np.hypot(xx_ - C[0], yy_ - C[1])
    for dx in range(0, 121, 6):            # the lifted card slides right until no pixel of it falls inside wheel radius 455 (O-29 fix 3)
        HOV['dx'] = float(dx)
        hand_lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        FH.draw_hand(hand_lay, A.J, 'p1', nw=not words, lift=lift, dim_others=HAND_K / FH.REST_V)
        hm = np.asarray(hand_lay.split()[3]) >= 128
        if not (hm & (d_ < FH.HAND_MIN_R)).any():
            break
    HOV['used_dx'] = HOV['dx']''')
open(p, 'w', encoding='utf-8').write(s)
print('ok')
