import sys, time
from m2 import *
t0 = time.time()
fr = Frame()
K1, K2, K3 = route('K1'), route('K2'), route('K3')
fr.dread([(K1, 1100, 1.0)])
fr.apply_dark(0.45)
fr.plum([((1650, 470), 190)], k=0.4)
for sid in ['t1_a', 't1_b', 't1_c', 't2_intel', 't2_virus', 't2_breach', 't3_b', 't3_c', 't3_core', 't1_d']:
    tower(fr, sid, 'hero' if sid in ('t1_a', 't1_b', 't1_c', 't2_intel', 't2_virus') else 'quiet')
tier_ring(fr, 't1_c', 'HOLDS'); tier_ring(fr, 't1_b', 'SITES_LOST'); tier_ring(fr, 't2_intel', 'UNTOUCHED'); tier_ring(fr, 't1_a', 'UNTOUCHED', frac=.5)
stop_block(fr, K1, 1500, 'HOLDS'); 
home_marks(fr, 44, 50, preview=6)
ribbon(fr, K1, 520, K1.L - 5, gain=1.0)
ribbon(fr, K2, 520, K2.L - 5, gain=.5)
ribbon(fr, K3, 520, K3.L - 5, gain=.5)
for R, s in ((K1, 1030), (K2, 700), (K3, 800)):
    head(fr, R.typ, R.pos(s), R.ang(s))
for sid, t in (('t1_c', 'HOLDS'), ('t1_b', 'SITES_LOST'), ('t2_intel', 'UNTOUCHED')):
    tag(fr, sid, t)
cage(fr)
img = fr.resolve()
Image.fromarray(u8(img)).save('D:/rc_scratch/tide_concepts/p2m_work/static.png')
o = camera(img)
Image.fromarray(u8(finish(o))).save('D:/rc_scratch/tide_concepts/p2m_work/static_o.png')
print(time.time() - t0)
