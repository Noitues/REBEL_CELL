p = 'D:/rc_scratch/combat_redesign/locked/fx_o30/src/fx_eff.py'
s = open(p, encoding='utf-8').read()
s = s.replace("RED_SHIELD = dict(fin=(0, 100), fout=(600, 760), ease='out3')", "RED_SHIELD = dict(fin=(0, 100), fout=(600, 760), ease='out3', chev_out=None)")
s = s.replace("RED_BRACE = dict(fin=(0, 120), fout=(760, 920), ease='out3')", "RED_BRACE = dict(fin=(0, 120), fout=(760, 920), ease='out3', chev_out=None)")
a = """    i, o = _red_k(t, RED_SHIELD)
    pa = i * o
    return pa, 0.18 * pa, pa"""
b = """    i, o = _red_k(t, RED_SHIELD)
    pa = i * o
    co = RED_SHIELD.get('chev_out')
    ca = pa if co is None else i * (1 - seg(t, co[0], co[1]))
    return pa, 0.18 * pa, ca"""
assert a in s; s = s.replace(a, b)
a = """def brace_reduce_alpha(t):
    \"\"\"(clamp + lane + chevron alpha, stamp alpha) of the reduce-motion brace block; the stamp stays\"\"\"
    i, o = _red_k(t, RED_BRACE)
    return i * o, i"""
b = """def brace_reduce_alpha(t):
    \"\"\"(clamp + lane alpha, stamp alpha) of the reduce-motion brace block; the stamp stays\"\"\"
    i, o = _red_k(t, RED_BRACE)
    return i * o, i


def brace_reduce_chev(t):
    \"\"\"alpha of the crumpled chevrons in the reduce-motion brace block\"\"\"
    i, o = _red_k(t, RED_BRACE)
    co = RED_BRACE.get('chev_out')
    return i * o if co is None else i * (1 - seg(t, co[0], co[1]))"""
assert a in s; s = s.replace(a, b)
a = """        chev_al = clamp_al
        lane_al = clamp_al"""
b = """        chev_al = brace_reduce_chev(t)
        lane_al = clamp_al"""
assert a in s; s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
