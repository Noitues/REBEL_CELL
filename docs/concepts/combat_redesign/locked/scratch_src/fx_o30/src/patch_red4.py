p = 'D:/rc_scratch/combat_redesign/locked/fx_o30/src/fx_eff.py'
s = open(p, encoding='utf-8').read()
s = s.replace("ease='out3', chev_out=None)\nRED_BRACE", "ease='out3', chev_out=None, shadow=1.0)\nRED_BRACE")
s = s.replace("RED_BRACE = dict(fin=(0, 120), fout=(760, 920), ease='out3', chev_out=None)", "RED_BRACE = dict(fin=(0, 120), fout=(760, 920), ease='out3', chev_out=None, shadow=1.0)")
a = """        sh = shadow(lp, (3, 5), 0.55)
        base = over(base, sh, pa)"""
b = """        sh = shadow(lp, (3, 5), 0.55 * (RED_SHIELD.get('shadow', 1.0) if reduce else 1.0))
        base = over(base, sh, pa)"""
assert a in s; s = s.replace(a, b)
a = """        base = over(base, shadow(lc, (3, 5), 0.55), clamp_al)"""
b = """        base = over(base, shadow(lc, (3, 5), 0.55 * (RED_BRACE.get('shadow', 1.0) if reduce else 1.0)), clamp_al)"""
assert a in s; s = s.replace(a, b)
a = """    if R['ease'] == 'out3':"""
b = """    if R['ease'] == 'lin':
        return seg(t, a, b), 1 - seg(t, c, d)
    if R['ease'] == 'out3':"""
assert a in s; s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
