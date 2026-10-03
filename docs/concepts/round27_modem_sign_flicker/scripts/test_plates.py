import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
from PIL import Image
import flicker_sign as FS
out = os.path.join(HERE, '..', 'scratch')
for key, seq in (('market', 'market_more'), ('neonmodem', 'neonmodem'), ('repairs', 'repairs'), ('techhelp', 'techhelp')):
    t = time.time()
    s = FS.FlickerSign(key)
    ims = [s.state_normal()] + [s.state_word(seq, i) for i in range(len(FS.SEQUENCES[seq]))]
    row = Image.new('RGB', (390 * len(ims), 1174), (20, 20, 24))
    for i, r in enumerate(ims):
        row.paste(Image.fromarray((np.clip(r['rgb'], 0, 1) * 255).astype(np.uint8)), (390 * i, 0))
    row.save(os.path.join(out, 'plates_%s.png' % key))
    print(key, round(time.time() - t, 1), 's')
