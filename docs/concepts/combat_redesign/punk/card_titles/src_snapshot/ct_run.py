import sys, os, time
sys.dont_write_bytecode = True
MODE = sys.argv[1]
os.environ['RC_TITLE'] = MODE if MODE in 'ABCD' or MODE == 'orig' else 'orig'
import numpy as np
from PIL import Image
OUT = 'D:/rc_scratch/combat_redesign/punk/card_titles/out/'
what = sys.argv[2] if len(sys.argv) > 2 else 'hand'
import f1_render as R
import f1_hand as FH
if what == 'bg':
    t = time.time()
    R.render('p1', with_ui=False).save(OUT + 'bg_noui.png')
    print('bg', round(time.time() - t, 1))
elif what == 'hand':
    bg = Image.open(OUT + 'bg_noui.png').convert('RGBA')
    X0, Y0, X1, Y1 = 800, 730, 1700, 1080
    crop = bg.crop((X0, Y0, X1, Y1)).resize(((X1 - X0) * 2, (Y1 - Y0) * 2), Image.LANCZOS)
    hand, played, hov = FH.hand_lists(R.A.J, 'p1')
    sl = FH.slots(len(hand))
    for i, nm in enumerate(hand):
        s = sl[i]
        ci = FH.card_hi(nm, False)
        a = np.asarray(ci).astype(np.float32); a[..., :3] *= FH.REST_V
        ci = Image.fromarray(a.astype(np.uint8), 'RGBA')
        FH.put(crop, ci, (s['cx'] - X0) * 2, (s['cy'] - Y0) * 2, s['ang'], FH.CARD_SCALE * 2, off=(8, 16), blur=14)
    crop.convert('RGB').save(OUT + 'hand2x_%s.png' % MODE)
    print('hand', MODE)
elif what == 'plate':
    t = time.time()
    R.render('p1').save(OUT + 'plate_%s.png' % MODE)
    print('plate', MODE, round(time.time() - t, 1))
