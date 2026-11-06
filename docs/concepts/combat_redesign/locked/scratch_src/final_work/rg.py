import sys
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import lw_render as LW
A = LW.R.A
print([A.CB9.ring_geom(d) for d in range(3)])
import gram as G
print('HOT', getattr(G, 'HOT', None), 'FAR', getattr(G, 'FAR', None))
import gramlib as GL
for n in dir(GL):
    if n.isupper() and isinstance(getattr(GL, n), tuple) and len(getattr(GL, n)) in (3, 4):
        print(n, getattr(GL, n))
