import sys, json
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
import rb_checks as RC, rb_tokens as T
for sfx, png in (('p1', 'p1_decide'), ('p2', 'p2_preview')):
    c = json.load(open(RC.WORK + 'chk_%s.json' % sfx))
    unc = c['rb'].get('uncaptured_text', [])
    from collections import Counter
    print(sfx, 'uncaptured', len(unc), Counter((u['text'], u['font'], u['size'], tuple(u['canvas'] or ())) for u in unc).most_common(30))
    M = RC.load_masks(sfx)
    rgb = np.asarray(Image.open('D:/rc_scratch/combat_redesign/locked/rebuild/board/%s.png' % png).convert('RGB')).astype(float)
    L = T.lstar(T.lum(rgb))
    for k in ('plan', 'twist_badge', 'adj'):
        if k in M:
            m = M[k] & (L > 92)
            ys, xs = np.nonzero(m)
            print(k, 'px>92', m.sum(), 'bbox', (xs.min(), ys.min(), xs.max(), ys.max()) if len(xs) else None, 'sample', [tuple(int(v) for v in rgb[ys[i], xs[i]]) for i in range(0, len(xs), max(1, len(xs)//6))][:6])
