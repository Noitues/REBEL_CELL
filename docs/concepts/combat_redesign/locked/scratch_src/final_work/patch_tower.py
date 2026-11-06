"""O-29 fix 9: loudness knobs on the locked tower (page value, pink halo value, texture strength)"""
P = 'D:/rc_scratch/combat_redesign/locked/corp/src/lw_tower.py'
s = open(P, newline='').read()
nl = '\r\n' if '\r\n' in s else '\n'
rep = [
    ("PAGE_V = 0.86\n", "PAGE_V = 0.86\nHALO_K = 1.0          # O-29 fix 9: value of the pink scissor halo (1 = full CELL_PINK)\nTEX_K = 1.0           # O-29 fix 9: strength of the slice texture (Ben-Day rings, dots, scales, plus)\n"),
    ("    ink(cv, halo, MAG, 0.10, seed + 4)\n", "    ink(cv, halo, MAG * HALO_K, 0.10, seed + 4)\n"),
    ("    ink(cv, tx, texc, 0.04, seed + 22, texop)\n", "    ink(cv, tx, texc, 0.04, seed + 22, min(1.0, texop * TEX_K))\n"),
]
for a, b in rep:
    a, b = a.replace('\n', nl), b.replace('\n', nl)
    assert s.count(a) == 1, a
    s = s.replace(a, b)
open(P, 'w', newline='').write(s)
print('ok')
