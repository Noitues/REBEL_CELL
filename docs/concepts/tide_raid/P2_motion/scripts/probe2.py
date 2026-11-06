from m2 import *
for rid in ('K1','K2','K3','A','B','C'):
    R = route(rid)
    out = []
    for sid in list(world().sites):
        B, t = site(sid)
        d = np.hypot(*(R.P - B).T)
        i = int(d.argmin())
        if d[i] < 90: out.append((sid, i, round(float(d[i]))))
    print(rid, R.typ, round(R.L), sorted(out, key=lambda x: x[1]))
    print('  start px', R.pos(520), 'end', R.pos(R.L - 5))
print({sid: (site(sid)[0].round().tolist(), site(sid)[1]) for sid in world().sites})
print('hq', world().hq, 'home', world().home)
