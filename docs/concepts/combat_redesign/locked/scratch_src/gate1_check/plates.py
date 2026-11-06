import numpy as np
from lab import *
T = {'SOAK': '3A7EF3', 'SCHEDULE': 'FF8C1A', 'BOSS_GOLD': 'D69A1A', 'TRACE_VIOLET': 'A03CFF', 'NET_CYAN': '5CE1FF', 'CELL_PINK': 'FF3DA8', 'PLAN': 'FFE200', 'HARM': 'FF4433', 'GAIN': '7BE07B', 'REPAIR': '3FB59A', 'SHIELD': '5E9BE0'}
for p in ['p1_decide', 'p2_preview']:
    im = load(p); Lb = lab(im)
    for nm, (x0, y0, x1, y1), ref in [('TOWER plate (Brace)', (995, 955, 1075, 978), '006E66'), ('WAVE plate (Trigger)', (1330, 945, 1400, 968), 'B4AAFF'), ('WAVE plate (lifted Trigger p2)', (1300, 860, 1390, 885), 'B4AAFF')]:
        if 'p2' in nm and p != 'p2_preview': continue
        sub = Lb[y0:y1, x0:x1].reshape(-1, 3)
        d = np.linalg.norm(sub - lab(hex2rgb(ref)), axis=1)
        near = sub[d < np.percentile(d, 40)]
        c = np.median(near, axis=0)
        ds = sorted((float(np.linalg.norm(c - lab(hex2rgb(v)))), k) for k, v in T.items())
        print('%-12s %-30s rendered Lab (%.1f %.1f %.1f) vs hex dE %.1f | nearest tokens: %s' % (p, nm, *c, float(np.linalg.norm(c - lab(hex2rgb(ref)))), ', '.join('%s %.1f' % (k, d_) for d_, k in ds[:3])))
