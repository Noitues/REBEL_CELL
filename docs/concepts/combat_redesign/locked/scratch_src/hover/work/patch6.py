p = 'D:/rc_scratch/combat_redesign/locked/hover/src/hz_core.py'
s = open(p, encoding='utf-8').read()
old = s[s.index("def ram_mark(L, before, after):"):s.index("def pink_burst(")]
new = '''def _pip_x(kind, i):
    """pip centres from the HUD's own registry (obj2.resources_row: ram_pips / trace_pips boxes, RAM_P 32, TR_P 28)"""
    import obj2
    if kind == 'ram':
        b = hud2.R['ram_pips']
        return b[0] + 4 + 13.8 + i * obj2.RAM_P, (b[1] + b[3]) / 2
    b = hud2.R['trace_pips']
    return b[0] + 4 + 12.8 + i * obj2.TR_P, (b[1] + b[3]) / 2


def ram_mark(L, before, after):
    for i in range(after, before):
        x, y = _pip_x('ram', i)
        HL.pencil_oval(L, x, y, 18.5, 18.5, seed=11 + i, w=3.2, ink=1.6)


def ram_plus(L, n_at):
    """refund: the HUD already draws the refunded coin (plus and rays); the plan rings it in GAIN pencil"""
    x, y = _pip_x('ram', n_at)
    HL.pencil_oval(L, x, y, 21, 21, seed=41, w=3.2, ink=1.6, col=GAIN)


def trace_mark(L, before, after):
    for i in range(before, after):
        x, y = _pip_x('trace', i)
        HL.pencil_box(L, (x - 13, y - 13, x + 13, y + 13), seed=21 + i, w=3.0, ink=1.6, pad=2)


'''
s = s.replace(old, new)
open(p, 'w', encoding='utf-8').write(s)
p = 'D:/rc_scratch/combat_redesign/locked/hover/src/hz_plates.py'
s = open(p, encoding='utf-8').read()
old = s[s.index("        r0, r1 = T_HALO + 4, CB.ring_geom(2)[1] - 2\n"):s.index("        bursts = []\n        for b in burns:")]
new = '''        r0, r1 = T_HALO + 4, CB.ring_geom(2)[1] - 6
        hw = 21.5
        poly = [ppx(C, r1, 60 * sec - hw + 2 * hw * i / 24) for i in range(25)] + [ppx(C, r0, 60 * sec + hw - 2 * hw * i / 24) for i in range(25)]
        HL.tint_poly(L, poly, PINK, 46)
        # flame tongues drawn as a proposal, rising in the empty outer cell of the column (clear of tokens, tags and the digit)
        for q, off in enumerate((-13.0, -6.5, 6.5, 13.0)):
            pts = []
            top = r1 - 4 - (6 if q in (1, 2) else 0)
            for i in range(16):
                r = r1 - 44 + (top - (r1 - 44)) * i / 15
                wob = math.sin(i * 1.1 + q * 1.7) * 2.4 * (1 - i / 18)
                pts.append(ppx(C, r, 60 * sec + off + wob / r * 57.3))
            HL.pencil(L, pts, w=3.4, ink=1.6, seed=11 + q, grain=True, cap=True)
        HL.pencil_poly(L, poly, w=2.8, ink=1.6, seed=9)
'''
s = s.replace(old, new)
s = s.replace("        Lt.sector(sec, T_HALO + 2, CB.ring_geom(2)[1] + 2, 31, 3)", "        Lt.sector(sec, T_HALO + 2, CB.ring_geom(2)[1] - 4, 22.5, 2)")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
