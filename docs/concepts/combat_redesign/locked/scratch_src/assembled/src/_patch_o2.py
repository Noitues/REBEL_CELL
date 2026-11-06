p = 'r2_sched.py'
s = open(p, encoding='utf-8').read()
s = s.replace('''def hold_cell(L, a0, a1, k, opt):''', '''SKIP_LABELS = [False]      # O2: the hold glyph + label text are drawn in a later pass (above the bezel spokes)


def hold_label(L, a0, k, opt, live=False):
    x, y = ppx(C, RM, a0 + 7.2)
    if live:
        hold_glyph(L, x, y, ORG_HI)
        arc_text2(L, RM - 0.5, a0 + 28, 'HOLD THIS TURN', 18, (255, 240, 214), 'mono', bold=0.4, keyline=1.4)
    else:
        hold_glyph(L, x, y, ORG_HI, 1.0 if opt == 'P' else 0.92)
        arc_text2(L, RM - 0.5, a0 + 25, 'HOLD ' + NAMES[k].split()[0], 18, ORG_PALE if opt == 'P' else ORG_HI, 'mono', bold=0.3)


def labels(L, sched, sel={}):
    """O2: every hold cell's glyph and text, drawn after the bezel spoke layer"""
    cum = 0
    for k, v in enumerate(sched):
        if v == 0:
            hold_label(L, cum, k, sel.get('hold', 'P'), live=(k == 0))
            cum += 40
        else:
            cum += 60 * v


def hold_cell(L, a0, a1, k, opt):''')
s = s.replace('''    x, y = ppx(C, RM, a0 + 7.2)
    hold_glyph(L, x, y, ORG_HI, 1.0 if opt == 'P' else 0.92)
    arc_text2(L, RM - 0.5, a0 + 25, 'HOLD ' + nm, 18, ORG_PALE if opt == 'P' else ORG_HI, 'mono', bold=0.3)
''', '''    if SKIP_LABELS[0]:
        return
    x, y = ppx(C, RM, a0 + 7.2)
    hold_glyph(L, x, y, ORG_HI, 1.0 if opt == 'P' else 0.92)
    arc_text2(L, RM - 0.5, a0 + 25, 'HOLD ' + nm, 18, ORG_PALE if opt == 'P' else ORG_HI, 'mono', bold=0.3)
''')
s = s.replace('''    x, y = ppx(C, RM, a0 + 7.2)
    hold_glyph(L, x, y, ORG_HI)
    arc_text2(L, RM - 0.5, a0 + 28, 'HOLD THIS TURN', 18, (255, 240, 214), 'mono', bold=0.4, keyline=1.4)
''', '''    if SKIP_LABELS[0]:
        return
    x, y = ppx(C, RM, a0 + 7.2)
    hold_glyph(L, x, y, ORG_HI)
    arc_text2(L, RM - 0.5, a0 + 28, 'HOLD THIS TURN', 18, (255, 240, 214), 'mono', bold=0.4, keyline=1.4)
''')
open(p, 'w', encoding='utf-8').write(s)

p = 'asm_r2.py'
s = open(p, encoding='utf-8').read()
s = s.replace("    S2.schedule(L, f['schedule'], {})\n", "    S2.SKIP_LABELS[0] = True                       # O2: hold glyphs + text are drawn after the spoke layer\n    S2.schedule(L, f['schedule'], {})\n    S2.SKIP_LABELS[0] = False\n")
s = s.replace('''    bg.alpha_composite(Lsp.done())
''', '''    bg.alpha_composite(Lsp.done())
    Llb = L2()                   # O2: the schedule labels (HOLD NEXT / HOLD THEN text + hold glyphs) above the spoke layer
    S2.labels(Llb, f['schedule'], {})
    bg.alpha_composite(Llb.done())
''')
s = s.replace('''    if check:
        try:''', '''    if check:
        for e_ in AU.BADGE_LOG:        # O1: badge box vs ring tags, HP tray, chevron column, glyph = 0 px
            for k_ in ('tag', 'tray', 'chev', 'glyph'):
                B10.AD('%s unit %d %s badge (%s side) px on %s' % (beat, e_['uid'], e_['badge'], e_['side'], k_), e_['hits'][k_], 0)
        try:''')
open(p, 'w', encoding='utf-8').write(s)
