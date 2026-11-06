import re
s = open('f1_hand.py').read()
# card_hi via card_render
i = s.index('def card_hi(')
j = s.index('def shadow_under(')
new = '''import card_render as CR


def card_hi(name, nw, mode='normal'):
    """2x image of one card from the locked WPAP card renderer (canvas = card + 18 px margin each side at 1x)"""
    key = (name, nw, mode)
    if key in _mem:
        return _mem[key]
    st = {'mode': mode, 'nowords': bool(nw)}
    im = CR.draw_card(name, 176 * 2, st)
    _mem[key] = im
    return im


'''
s = s[:i] + new + s[j:]
# played slot
i = s.index('def played_slot(')
j = s.index('def slots(')
s = s[:i] + '''def played_slot(name, nw, size_scale=CARD_SCALE):
    """a played card leaves the locked card's solid blue-grey liner (never dashed) with the ghost glyph and PLAYED"""
    return card_hi(name, nw, 'played')


''' + s[j:]
# remove F1 PLAYED lettering
i = s.index("        if not nw:\n            lay = Canvas(260, 80")
j = s.index("    if hov is not None:\n        s = sl[hov]")
s = s[:i] + s[j:]
# lifted
s = s.replace("        im = card_hi(hand[hov], nw)\n        k = LIFT_S","        im = card_hi(hand[hov], nw, 'hover')\n        k = LIFT_S")
s = s.replace("        pp = pink_print(sm)\n        base.alpha_composite(pp, (int(s['cx'] - pp.width / 2), int(LIFT_CY - pp.height / 2)))\n","")
open('f1_hand.py','w').write(s)
