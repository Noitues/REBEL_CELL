p = 'D:/rc_scratch/combat_redesign/locked/fx_o30/src/o30_seq.py'
s = open(p, encoding='utf-8').read()
a = """def r_settle(t, red, cv):
    al = AL_BOARD()
    k = E.e_io3(E.seg(t, 0, 260))
    return cv * (1 - k) + al * k"""
b = """LANES = ((RHO > 425) & (RHO < 482)).astype(np.float32)[..., None]


def r_settle(t, red, cv):
    \"\"\"hand-off before RINGS STEP: the landed Worm 3 and the spent gun marks leave ring 0, and the old landing arcs, the clear
    wash and the brace stamp lift off the lanes, in one 260 ms dissolve (fx_rings_step lifts the arcs in its own 0-160 ms
    anticipate when it plays alone; in the sequence that lift moves here so it never shares a window with the tape arrow)\"\"\"
    al = AL_BOARD()
    tgt = al * (1 - LANES) + E.clean_empty(SK) * LANES
    k = E.e_io3(E.seg(t, 0, 260))
    return cv * (1 - k) + tgt * k"""
assert a in s; s = s.replace(a, b)
a = """        ('rings_step', 'fx_rings_step', ph_end('fx_rings_step'), r_rings, 'keep'),"""
b = """        ('rings_step', 'fx_rings_step', ph_end('fx_rings_step'), r_rings, rings_setup),"""
assert a in s; s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
