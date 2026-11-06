"""ed_beat1.py: one-off edit of mp_beat.py (precompute the trace source frame)"""
p = 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_mpst/src/mp_beat.py'
s = open(p, encoding='utf-8').read()
a = "P3FULL = comp(B3, U3)\n"
assert s.count(a) == 1
s = s.replace(a, a + "P3PRE_FULL = None          # set below, once BFIX exists\n")
b = "BFIX = B3p * (1 - _cm[..., None]) + B3 * _cm[..., None]\n"
assert s.count(b) == 1
s = s.replace(b, b + "P3PRE_FULL = comp(BFIX, U3p)\n")
c = "comp(BFIX, U3p), TR_PIP, TR_SLOT)"
assert s.count(c) == 1
s = s.replace(c, "P3PRE_FULL, TR_PIP, TR_SLOT)")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
