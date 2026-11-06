"""hv_ranges_fix.py : hv_ranges.py -> the collide numbers are dicts: sum their values"""
import io
p = 'D:/rc_scratch/combat_redesign/locked/rebuild/hover/src/hv_ranges.py'
s = io.open(p, encoding='utf-8').read()
a = s[s.index("print('collide'"):s.index("print('dashes'")]
b = ("tot = lambda v: sum(v.values()) if isinstance(v, dict) else v\n"
     "print('collide', rng([tot(c['collide'].get('hover_vs_marks_px')) for c in C.values()]), rng([tot(c['collide'].get('occlusion_px')) for c in C.values()]),\n"
     "      rng([tot(c['collide'].get('mark_pairs_px')) for c in C.values()]))\n")
s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
