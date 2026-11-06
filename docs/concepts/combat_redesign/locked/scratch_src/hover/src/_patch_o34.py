p = 'kcard2.py'
s = open(p, encoding='utf-8').read()
s = s.replace('''    if x and not ctx['nw']:
        sx0, sx1 = ctx['R']['art'][0] + 12, ctx['R']['art'][2] - 12
        tw = cv.tw('×' + x, 34)''', '''    if x:
        sx0, sx1 = ctx['R']['art'][0] + 12, ctx['R']['art'][2] - 12
        tw = cv.tw('×' + x, 34) if not ctx['nw'] else (int(x) - 1) * 8 + 4 + 2        # O4: nowords = a tally of x strokes''')
s = s.replace('''    x = ctx['c'].get('x')
    if not x or ctx['nw']:
        return
    px = 34''', '''    x = ctx['c'].get('x')
    if not x:
        return
    if ctx['nw']:      # O4: the multiplier as a white tally (same form as the loud tab's 1-stroke tally: 4 px white bar, 1 px INK keyline, r 1.5)
        mx, my = ctx['mult_xy']
        for i in range(int(x)):
            cv.rect([mx + 1 + i * 8, my - 11, mx + 5 + i * 8, my + 9], fill=(255, 255, 255), outline=INK_, w=1.0, r=1.5)
        return
    px = 34''')
open(p, 'w', encoding='utf-8').write(s)

p = 'r2_sched.py'
s = open(p, encoding='utf-8').read()
s = s.replace('''def live_label(L, a0, txt):''', '''def live_label(L, a0, txt, n=2):''')
s = s.replace('''    L.line([(x - 5 * nx, y - 5 * ny), (x + 5 * nx, y + 5 * ny)], INK, 2.8)
    return a_start + lab_deg + 4''', '''    L.line([(x - 5 * nx, y - 5 * ny), (x + 5 * nx, y + 5 * ny)], INK, 2.8)
    if not NOW['words']:       # O4: nowords = '+' then an n-stroke white tally (same strokes as the ring tags and sector digits)
        for i in range(n):
            xx, yy = ppx(C, RM, a_start + 0.9 + (11.0 + i * 5.4) / RM * 57.3)
            L.rect([xx - 2.6, yy - 7.8, xx + 2.6, yy + 7.8], fill=INK, r=1)
            L.rect([xx - 1.4, yy - 7.0, xx + 1.4, yy + 7.0], fill=(244, 247, 252), r=1)
    return a_start + lab_deg + 4''')
s = s.replace("a_end = live_label(L, cum, txt)", "a_end = live_label(L, cum, txt, v)")
open(p, 'w', encoding='utf-8').write(s)

p = 'wc2.py'
s = open(p, encoding='utf-8').read()
old = '''        if soak and kind in ('N', 'B'):     # fix 7: soak X carries the ink chevron notch at its crossing, 4.2 px wide (was 3.4, N only)
            p = [(x - 4, y - 5), (x + 2, y), (x - 4, y + 5)]
            L.line(p, INK, 4.2)'''
new = '''        if soak and kind in ('N', 'B'):     # O3: one 5 px INK diamond notch at the crossing only (1 px INK keyline); the four arms stay continuous
            d_ = 2.5
            L.poly([(x, y - d_), (x + d_, y), (x, y + d_), (x - d_, y)], fill=INK, outline=INK, w=1.0)'''
assert old in s
s = s.replace(old, new)
open(p, 'w', encoding='utf-8').write(s)

p = 'r2_ground.py'
s = open(p, encoding='utf-8').read()
s = s.replace("HULL_LIFT_F = 0.57 / 0.84 ", "HULL_LIFT_F = 0.50 / 0.84 ")
open(p, 'w', encoding='utf-8').write(s)
