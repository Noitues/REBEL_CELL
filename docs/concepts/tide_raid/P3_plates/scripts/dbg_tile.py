import sys
sys.argv=['x']
import p1_final as F
import p1_beats
B = p1_beats.forecast(False)
w = B.w
for sid in ('t1_c','t1_b','t2_intel','t1_a'):
    s = w.sites[sid]
    print(sid, s['tier'], s['B'], F.tile_anchor(w, sid, 34))
print('home', w.home)
