p = 'D:/rc_scratch/combat_redesign/locked/fx_o30/src/o30_seq.py'
s = open(p, encoding='utf-8').read()
a = """    for nm, fid, dur, r, setup in S:
        out.append(dict(name=nm, fid=fid, start=t0, dur=int(dur), render=r, setup=setup))
        t0 += int(dur) + GAP"""
b = """    for nm, fid, dur, r, setup in S:
        out.append(dict(name=nm, fid=fid, start=t0, dur=int(dur), render=r, setup=setup))
        t0 += int(dur) + GAP_AFTER.get(nm, GAP)"""
assert a in s; s = s.replace(a, b)
a = "GAP = 100\n"
b = """GAP = 100
# O-30: the END TURN hand-off holds 400 ms before RINGS STEP (100 ms everywhere else).  Measured: with 100 ms, the clear wash
# leaving and the rings-step cells / tape arrow put 4 flashes inside one second in a 60 px tile at the tape (x 810, y 240).
GAP_AFTER = {'settle': 400}
"""
assert a in s; s = s.replace(a, b, 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
