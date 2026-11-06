p = 'D:/rc_scratch/combat_polish/E7_waves/E10/src/build10.py'
t = open(p).read()
old = "    if beat in ('p1', 'nowords'):\n        gun_tracers10(L, f)\n"
assert t.count(old) == 1
t = t.replace(old, "")
old2 = "    adjuster_body(L, f['adj'])\n"
assert t.count(old2) == 1
t = t.replace(old2, "    adjuster_body(L, f['adj'])\n    if beat in ('p1', 'nowords'):\n        gun_tracers10(L, f)\n")
open(p, 'w').write(t)
