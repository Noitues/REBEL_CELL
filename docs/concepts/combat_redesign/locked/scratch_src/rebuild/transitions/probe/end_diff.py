"""end_diff.py: where the T6 frame at 0.80 s (and 0.70, 0.76) differs from the bare room; prints the bbox and count of pixels over 2."""
import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/rebuild/transitions/src')
from fx3lib import *
import fx3 as M
ref = np.clip(K1ROOM + 0.5, 0, 255).astype(np.uint8).astype(int)
for t in (0.70, 0.76, 0.80):
    log = []
    a = np.asarray(to_pil(M.t6(t, log)).convert('RGB')).astype(int)
    d = np.abs(a - ref).max(-1)
    ys, xs = np.nonzero(d > 2)
    print(t, 'max', int(d.max()), 'px>2', len(xs), 'bbox', (xs.min(), ys.min(), xs.max(), ys.max()) if len(xs) else None, 'glyph draws', len(log))
    if len(log):
        print('   tags', sorted(set(str(l[-1])[:30] if isinstance(l, (list, tuple)) else str(l)[:30] for l in log))[:10])
