"""stock_de.py <hex> [...]: Lab and the nearest refs (dE76) of a candidate FX-P plate stock, against the same refs as pick_stock.py"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
import rb_tokens as T
ref = dict(T.TOKENS)
ref.update(T.NEUTRALS)
ref.update({'slice_' + k: v for k, v in T.SLICE_INK.items()})
ref.update({'CARD_BONE': T.hx('F1EAD6'), 'HIT_PAPER': T.HIT_PAPER, 'K_TYPE': T.K_TYPE, 'CREAM_HP': T.CREAM_HP, 'CREAM': T.hx('FFF4D6'),
            'HOT_CORE': T.HOT_CORE, 'COLD_CHEV': T.COLD_CHEV, 'HARM_UP': T.HARM_UP, 'PAPER_F2EEE4': T.hx('F2EEE4')})
for h in sys.argv[1:]:
    rgb = T.hx(h)
    lab = T.lab(np.array(rgb, np.float64))
    ds = sorted((T.de76(rgb, v), k) for k, v in ref.items())
    print(h, 'Lab', [round(float(x), 1) for x in lab], 'nearest', [(k, round(float(d), 1)) for d, k in ds[:5]])
