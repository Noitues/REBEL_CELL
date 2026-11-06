p = 'D:/rc_scratch/combat_redesign/locked/fx_o30/src/fx_eff.py'
s = open(p, encoding='utf-8').read()
key = '# ============================================================================ P: protect'
assert key in s and 'def shield_reduce_alpha' not in s
helper = '''# ---- reduce-motion timing for the two P blocks (O-30: reduce motion must never flash more than full motion)
# fin / fout: fade-in and fade-out windows (ms); ease 'out3' (the step-4 form) or 'io3'
RED_SHIELD = dict(fin=(0, 100), fout=(600, 760), ease='out3')
RED_BRACE = dict(fin=(0, 120), fout=(760, 920), ease='out3')


def _red_k(t, R):
    a, b = R['fin']
    c, d = R['fout']
    if R['ease'] == 'out3':
        return e_out3(seg(t, a, b)), 1 - seg(t, c, d)
    return e_io3(seg(t, a, b)), 1 - e_io3(seg(t, c, d))


def shield_reduce_alpha(t):
    """(plate alpha, tint alpha, chevron alpha) of the reduce-motion shield block"""
    i, o = _red_k(t, RED_SHIELD)
    pa = i * o
    return pa, 0.18 * pa, pa


def brace_reduce_alpha(t):
    """(clamp + lane + chevron alpha, stamp alpha) of the reduce-motion brace block; the stamp stays"""
    i, o = _red_k(t, RED_BRACE)
    return i * o, i


'''
s = s.replace(key, helper + key, 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
