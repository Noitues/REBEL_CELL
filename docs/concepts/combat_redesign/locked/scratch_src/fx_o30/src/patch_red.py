"""patch the fx_eff COPY: reduce-motion timing of shield_block and brace_block becomes data (RED_SHIELD / RED_BRACE)"""
p = 'D:/rc_scratch/combat_redesign/locked/fx_o30/src/fx_eff.py'
s = open(p, encoding='utf-8').read()
a = """    if reduce:
        pa = e_out3(seg(t, 0, 100)) * (1 - seg(t, 600, 760))
        tint_al = 0.18 * pa
        chev_r = [r_out + 9, r_out + 24]
        chev_al = pa
        ps, impact_k = 1.0, -1"""
b = """    if reduce:
        pa, tint_al, chev_al = shield_reduce_alpha(t)
        chev_r = [r_out + 9, r_out + 24]
        ps, impact_k = 1.0, -1"""
assert a in s
s = s.replace(a, b)
a2 = """    if reduce:
        lane_k, clamp_al, cs, stamp_al, stamp_s = 1.0, e_out3(seg(t, 0, 120)) * (1 - seg(t, 760, 920)), 1.0, e_out3(seg(t, 0, 120)), 1.0"""
b2 = """    if reduce:
        clamp_al, stamp_al = brace_reduce_alpha(t)
        lane_k, cs, stamp_s = 1.0, 1.0, 1.0"""
assert a2 in s
s = s.replace(a2, b2)
helper = '''

# ---- reduce-motion timing for the two P blocks (O-30: reduce motion must never flash more than full motion)
# fin / fout: fade-in and fade-out windows (ms), ease: 'out3' (old) or 'io3'
RED_SHIELD = dict(fin=(0, 100), fout=(600, 760), ease='out3')
RED_BRACE = dict(fin=(0, 120), fout=(760, 920), ease='out3')


def _red_k(t, R):
    a, b = R['fin']
    c, d = R['fout']
    e = e_out3 if R['ease'] == 'out3' else e_io3
    return e(seg(t, a, b)), (1 - (seg(t, c, d) if R['ease'] == 'out3' else e_io3(seg(t, c, d))))


def shield_reduce_alpha(t):
    """(plate alpha, tint alpha, chevron alpha) of the reduce-motion shield block"""
    i, o = _red_k(t, RED_SHIELD)
    pa = i * o
    return pa, 0.18 * pa, pa


def brace_reduce_alpha(t):
    """(clamp + lane + chevron alpha, stamp alpha) of the reduce-motion brace block; the stamp stays"""
    i, o = _red_k(t, RED_BRACE)
    return i * o, i


def plate_shape('''
s = s.replace('\n\ndef plate_shape(', helper, 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
