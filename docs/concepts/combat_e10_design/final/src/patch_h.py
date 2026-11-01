import re
p = 'D:/rc_scratch/combat_polish/E7_waves/E10/src/dump10.py'
t = open(p).read()
i = t.index('def make_chain():')
j = t.index("f2['chain'] = make_chain()")
new = '''def make_chain():
    f = f2
    eq = f['pv']['eq']
    tl = f['tlog']
    hits_ = [e for e in f['log'] if e[0] == 'hit']
    fires_ = [e for e in f['log'] if e[0] == 'fire' and e[3] is not None]
    pips1 = sum(e[5] for e in tl if e[0] == 'trig_unit')
    c = []
    c.append(dict(name='TWIST', glyph='C_TWIST', col=[255, 226, 0], pips=[['txt', 'ring +1 turns']]))
    c.append(dict(name='TRIGGER', glyph='C_TRIG', col=[255, 226, 0], pips=[['yel', pips1], ['txt', TRIGS[0]['kind'] + ' dead: refund'], ['refund', 1]]))
    c.append(dict(name='BRACE', glyph='C_BRACE', col=[255, 244, 214], pips=[['txt', 'one slice']]))
    c.append(dict(name='GUNS', glyph='C_STRIKE', col=[92, 225, 255], pips=[['cyan', len(fires_)], ['txt', 'shots']]))
    land = [['raw', sum(e[4] for e in hits_)]]
    if eq['braced']:
        land += [['txt', 'brace'], ['braced', eq['braced']]]
    if eq['rider']:
        land += [['txt', 'rider'], ['rider', eq['rider']]]
    c.append(dict(name='LANDS', glyph='X_SKULL', col=[255, 68, 51], pips=land))
    c.append(dict(name='RINGS STEP', glyph='C_PULL', col=[255, 140, 26], pips=[['txt', 'W4 enters']]))
    return c


'''
t = t[:i] + new + t[j:]
open(p, 'w').write(t)

p = 'D:/rc_scratch/combat_polish/E7_waves/E10/src/build10.py'
t = open(p).read()


def rep(old, new):
    global t
    assert t.count(old) == 1, (t.count(old), old[:90])
    t = t.replace(old, new)


# chain strip rows 26 high
rep("    steps = f['chain']\n    h = 29", "    steps = f['chain']\n    h = 26")
# refund icon in the chain strip: bigger burst + cyan pip with plus
rep("""            elif kind == 'refund':
                burst(L, x + 12, cy, 6, 12, 8)
                L.rect([x + 28, cy - 8, x + 50, cy + 8], fill=CYAN, outline=INK, w=2, r=3)
                x += 62""", """            elif kind == 'refund':
                burst(L, x + 14, cy, 7, 14, 9)
                L.rect([x + 30, cy - 9, x + 56, cy + 9], fill=CYAN, outline=INK, w=2, r=3)
                L.line([(x + 43, cy - 5), (x + 43, cy + 5)], INK, 3)
                L.line([(x + 38, cy), (x + 48, cy)], INK, 3)
                x += 68""")
# RAM terminal 48 high
rep("    terminal(L, (X0 - 4, y, X1, y + 54))\n    label(L, X0 + 12, y + 27, 'RAM', CRT_TXT, 16)", "    terminal(L, (X0 - 4, y, X1, y + 48))\n    label(L, X0 + 12, y + 24, 'RAM', CRT_TXT, 16)")
rep("        L.rect([bx, y + 14, bx + 28, y + 40], fill=CYAN if i < f['ram'] else (20, 34, 52), outline=CYAN, w=2, r=4)", "        L.rect([bx, y + 11, bx + 28, y + 37], fill=CYAN if i < f['ram'] else (20, 34, 52), outline=CYAN, w=2, r=4)")
rep("""            burst(L, bx + 14, y + 27, 20, 31, 12)
            L.rect([bx, y + 14, bx + 28, y + 40], fill=CYAN, outline=INK, w=2.4, r=4)
            L.line([(bx + 14, y + 20), (bx + 14, y + 34)], INK, 3.4)
            L.line([(bx + 7, y + 27), (bx + 21, y + 27)], INK, 3.4)""", """            burst(L, bx + 14, y + 24, 20, 30, 12)
            L.rect([bx, y + 11, bx + 28, y + 37], fill=CYAN, outline=INK, w=2.4, r=4)
            L.line([(bx + 14, y + 17), (bx + 14, y + 31)], INK, 3.4)
            L.line([(bx + 7, y + 24), (bx + 21, y + 24)], INK, 3.4)""")
rep("    label(L, X0 + 230, y + 27, 'TRACE', CRT_TXT, 16)", "    label(L, X0 + 230, y + 24, 'TRACE', CRT_TXT, 16)")
rep("        L.rect([bx, y + 14, bx + 26, y + 40], fill=(160, 60, 255) if on else (28, 20, 44), outline=(160, 60, 255), w=2, r=4)", "        L.rect([bx, y + 11, bx + 26, y + 37], fill=(160, 60, 255) if on else (28, 20, 44), outline=(160, 60, 255), w=2, r=4)")
rep("""                L.line([(bx + q, y + 40), (bx + q + 8, y + 14)], (255, 255, 255, 110), 2)""", """                L.line([(bx + q, y + 37), (bx + q + 8, y + 11)], (255, 255, 255, 110), 2)""")
rep("    label(L, X0 + 520, y + 27, 'ENDS = HEAT', AMBER, 16)\n    seg_run(L, X0 + 640, y + 27, 'gold', f['pv']['trace_after'], 11, 18) if f['pv']['trace_after'] else None\n    return y + 58",
    "    label(L, X0 + 520, y + 24, 'ENDS = HEAT', AMBER, 16)\n    seg_run(L, X0 + 640, y + 24, 'gold', f['pv']['trace_after'], 11, 18) if f['pv']['trace_after'] else None\n    return y + 52")
# option chip: refund icon
rep("def option_chip(L, y, name, plan, soak, eq, sel=False, solid=True):", "def option_chip(L, y, name, plan, soak, eq, sel=False, solid=True, refund=False):")
rep("""        x += 18
    label(L, X0 + 190, y + 20, name, YEL if sel else WHITE, 16)""", """        x += 18
    if refund:
        burst(L, x + 12, y + 20, 5, 11, 8)
        L.rect([x + 26, y + 12, x + 44, y + 28], fill=CYAN, outline=INK, w=1.6, r=3)
        L.line([(x + 35, y + 15), (x + 35, y + 25)], INK, 2.6)
        L.line([(x + 30, y + 20), (x + 40, y + 20)], INK, 2.6)
        x += 50
    label(L, X0 + 190 if x < X0 + 185 else x + 8, y + 20, name, YEL if sel else WHITE, 16)""")
rep("J['meta']['lines']['trigger'][1], J['f2t']['pv']['eq'])", "J['meta']['lines']['trigger'][1], J['f2t']['pv']['eq'], refund=J['f2t']['refunds'] > 0)")
rep("J['meta']['hero_end'], f['pv']['eq'], sel=True)", "J['meta']['hero_end'], f['pv']['eq'], sel=True, refund=f['refunds'] > 0)")
# NEXT row twist payoff
rep("""    seg_run(L, x, yg, 'slice', nx['slost'], 11, 14, al)
    return y + h + 8""", """    seg_run(L, x, yg, 'slice', nx['slost'], 11, 14, al)
    if twist_pay:
        xt = X0 + 372
        L.ellipse([xt - 12, yg - 12, xt + 12, yg + 12], fill=(30, 26, 6), outline=YEL, w=2.2)
        L.glyph('C_TWIST', 17, (xt, yg), YEL)
        lw = label(L, xt + 20, yg, 'WITHOUT TWIST', YEL, 16)
        for i in range(twist_pay['without']['taken']):
            L.rect([xt + 28 + lw + i * 15, yg - 8, xt + 38 + lw + i * 15, yg + 8], fill=None, outline=RED, w=2.4, r=3)
        L.text((xt + 36 + lw + twist_pay['without']['taken'] * 15 + 20, yg), '>', 20, 'anton', fill=YEL, anchor='mm')
        for i in range(nx['taken']):
            seg(L, xt + 44 + lw + twist_pay['without']['taken'] * 15 + 24 + i * 15, yg, 'through', 10, 16)
    return y + h + 8""")
rep("def bill_box(L, f, y, pencil=False, plan_tag=None):", "def bill_box(L, f, y, pencil=False, plan_tag=None, twist_pay=None):")
rep("    y = bill_box(L, f, 66, pencil=(beat == 'p2'), plan_tag=('BEST LINE' if beat in ('p2', 'p3') else None))", "    y = bill_box(L, f, 66, pencil=(beat == 'p2'), plan_tag=('BEST LINE' if beat in ('p2', 'p3') else None), twist_pay=(J['twist_payoff'] if beat in ('p2', 'p3') else None))")
open(p, 'w').write(t)
print('ok')
