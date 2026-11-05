"""diffmap.py <corp>: where the staged compose differs from the published plate (> 8/255): a 1x crop sheet of the worst areas and the
differing pixels' colours (compose vs published) for a look."""
import sys, os
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
HERE = 'D:/rc_scratch/combat_redesign/locked/round2/transitions/'
FIN = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
corp = sys.argv[1] if len(sys.argv) > 1 else 'neutral'
pub = FIN + ('p1_decide.png' if corp == 'neutral' else 'p1_decide_%s.png' % corp)
a = np.asarray(Image.open(HERE + 'layers/%s_p1_compose.png' % corp).convert('RGB')).astype(int)
b = np.asarray(Image.open(pub).convert('RGB')).astype(int)
d = np.abs(a - b).max(-1)
m = d > 8
ys, xs = np.nonzero(m)
print('px > 8:', int(m.sum()))
# tile counts (60 px)
cnt = m[:1080 // 60 * 60, :].reshape(18, 60, 32, 60).sum((1, 3))
order = np.dstack(np.unravel_index(np.argsort(-cnt.ravel()), cnt.shape))[0][:6]
for i, j in order:
    print('tile x%d y%d: %d px' % (j * 60, i * 60, cnt[i, j]))
# sample colours
idx = np.argsort(-d[m])[:12]
for k in idx:
    y, x = ys[k], xs[k]
    print((int(x), int(y)), 'compose', a[y, x].tolist(), 'published', b[y, x].tolist())
vis = (np.clip(d * 5, 0, 255)).astype(np.uint8)
Image.fromarray(vis).save(HERE + 'probe/diff_%s.png' % corp)
i, j = order[0]
x0, y0 = max(0, j * 60 - 90), max(0, i * 60 - 90)
crop = np.concatenate([a[y0:y0 + 240, x0:x0 + 240], b[y0:y0 + 240, x0:x0 + 240], np.repeat(vis[y0:y0 + 240, x0:x0 + 240, None], 3, -1)], 1)
Image.fromarray(crop.astype(np.uint8)).resize((720 * 2, 240 * 2), Image.NEAREST).save(HERE + 'probe/diffcrop_%s.png' % corp)
