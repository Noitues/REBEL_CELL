"""commit_look.py <skin> <t...>: save the full-motion commit frames at 1x (board left half crop) for looking -> work/look1x/commit_<t>.png"""
import sys
sys.dont_write_bytecode = True
import numpy as np
import mp_eff as E
from mp_lib import to_img, ME
skin = sys.argv[1]
for t in sys.argv[2:]:
    f = np.clip(E.FX['fx_commit']['render'](float(t), skin, False), 0, 255)
    to_img(f).crop((120, 160, 1080, 1000)).save(ME + 'work/look1x/commit_%s.png' % t)
    print('ok', t, flush=True)
