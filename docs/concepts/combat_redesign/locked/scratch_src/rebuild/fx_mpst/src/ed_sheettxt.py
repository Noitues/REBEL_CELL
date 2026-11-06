"""ed_sheettxt.py: one-off text fix in mp_sheets.py: the arrow stub lengths are the ARROW_STUB values in mp_eff.py"""
P = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/src/mp_sheets.py'
s = open(P, encoding='utf-8').read()
a = 'on the spin, twist, shove and rings step it is a stub (60 / 30 / 30 / 40 deg) that runs ahead of the mover and is eaten when it arrives.'
b = 'on the spin, twist, shove, rings step and Hold it is a stub (60 / 30 / 30 / 32 / 22 deg, mp_eff.ARROW_STUB) that runs ahead of the mover and is eaten when it arrives; the pull and the bump keep their short whole arrow.'
assert s.count(a) == 1
s = s.replace(a, b)
open(P, 'w', encoding='utf-8').write(s)
print('ok')
