"""frames per street leg of the daemon run (corner to corner) from the speed table."""
from stage import *
import beats_b as B
D = B.dmn()
P = D.P
p = P.p
d = np.diff(p, axis=0)
ang = np.unwrap(np.arctan2(d[:, 1], d[:, 0]))
# corners = places where heading changes by > 0.5 rad inside 30 px
cs = []
for i in range(1, len(p) - 1):
    pass
pts = P.sub(0, P.L, 1.0)
dd = np.diff(pts, axis=0)
hd = np.unwrap(np.arctan2(dd[:, 1], dd[:, 0]))
turn = np.abs(hd[20:] - hd[:-20])
idx = np.where(turn > .7)[0]
corners = []
for i in idx:
    s = i + 10
    if not corners or s - corners[-1] > 60:
        corners.append(s)
print('v0 px/f', round(D.v0, 2), 'arrive f', D.f_arr, 's0', D.S_START, 's_stop', round(D.s_stop))
bounds = [D.S_START] + [c for c in corners if D.S_START < c < D.s_stop - 40] + [D.s_stop - 40]
fr = []
for a, b in zip(bounds[:-1], bounds[1:]):
    fa = min([f for f, s in D.table.items() if s >= a] or [D.f_arr])
    fb = min([f for f, s in D.table.items() if s >= b] or [D.f_arr])
    fr.append((int(a), int(b), int(b - a), fb - fa))
for x in fr:
    print('leg s %d-%d  %d px  %d f  %.1f px/f' % (x[0], x[1], x[2], x[3], x[2] / max(x[3], 1)))
