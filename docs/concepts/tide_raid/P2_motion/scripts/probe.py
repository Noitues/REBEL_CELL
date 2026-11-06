import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/tide_raid/P2_plates/scripts')
import numpy as np
from PIL import Image, ImageDraw
import p1lib as L
w = L.load_world()
im = Image.open('D:/rc_scratch/tide_concepts/p2_base/city_default.png').convert('RGB')
d = ImageDraw.Draw(im)
col = {'K1': (70, 144, 255), 'K2': (255, 64, 214), 'K3': (255, 238, 58)}
for k, r in w.routes.items():
    p = [tuple(q) for q in np.asarray(r['path'])]
    d.line(p, fill=col.get(k, (255, 255, 255)), width=3)
    print(k, r['typ'], len(p), r['ext'], r['sites'], p[0], p[-1])
for sid, s in w.sites.items():
    b = s['B']; d.ellipse([b[0]-8, b[1]-8, b[0]+8, b[1]+8], outline=(255, 255, 255)); d.text((b[0]+10, b[1]-6), sid + ' t%d' % s['tier'], fill=(255, 255, 255))
d.text((w.home[0], w.home[1]), 'HOME', fill=(255,255,255)); d.text((w.hq[0], w.hq[1]), 'HQ', fill=(255,255,255))
print('home', w.home, 'hq', w.hq)
for h in w.hunters:
    d.line([tuple(q) for q in np.asarray(h['path'])], fill=(255,255,255), width=2)
for k in ('A','B','C'):
    if k in w.routes: print(k)
im.save('D:/rc_scratch/tide_concepts/p2m_work/probe.png')
