"""O-29 fix 9b: FILL_K knob on the wedge spot ink (the seats keep the full ink so the slice type still reads)"""
P = 'D:/rc_scratch/combat_redesign/locked/corp/src/lw_tower.py'
s = open(P, newline='').read()
nl = '\r\n' if '\r\n' in s else '\n'
rep = [
    ("TEX_K = 1.0", "FILL_K = 1.0          # O-29 fix 9: value of the wedge spot ink (seats keep full ink)\nTEX_K = 1.0"),
    ("    ink(cv, mg, fillc, 0.11, seed + 21)\n", "    ink(cv, mg, fillc * FILL_K, 0.11, seed + 21)\n"),
]
for a, b in rep:
    a, b = a.replace('\n', nl), b.replace('\n', nl)
    assert s.count(a) == 1, a
    s = s.replace(a, b)
open(P, 'w', newline='').write(s)
print('ok')
