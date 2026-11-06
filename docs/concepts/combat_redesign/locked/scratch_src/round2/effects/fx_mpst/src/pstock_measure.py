"""pstock_measure.py: review 3.10, measured.
 1. On the published fx_P_protect.png: px within dE76 8 of the P stock #F6C8DE and of the card bone PAPER #F2EEE4, with their median L*.
 2. On the 60 fps frames (neutral, full motion, the hold frame of each block): the px the effect adds (marks on vs marks off, any channel
    > 6 levels) that sit within dE76 8 of the P stock, of its shade #D696B8 and of PAPER.
All L* are CIE L* (D65) through rb_tokens (the C/D/H/L designer's read-only maths).  -> work/pstock.json"""
import sys, json
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from mp_lib import ME, OUTD, P_STOCK, P_STOCK_D
sys.path.insert(1, 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_cdhl/src')
import fxk_lib as K
import mp_eff as E
RT = K.RT
PAPER = tuple(RT.TOKENS['PAPER']) if 'PAPER' in RT.TOKENS else (242, 238, 228)


def near(lab, c, d=8.0):
    return np.linalg.norm(lab - RT.lab(np.array(c, np.float64)), axis=-1) < d


out = dict(method=__doc__, p_stock=P_STOCK, p_stock_shade=P_STOCK_D, paper=PAPER,
           p_stock_L=round(float(RT.lab(np.array(P_STOCK, np.float64))[0]), 1), paper_L=round(float(RT.lab(np.array(PAPER, np.float64))[0]), 1),
           stock_vs_paper_dE76=round(float(np.linalg.norm(RT.lab(np.array(P_STOCK, np.float64)) - RT.lab(np.array(PAPER, np.float64)))), 1))
im = np.asarray(Image.open(OUTD + 'fx_P_protect.png').convert('RGB'), np.float64)
lab = RT.lab(im)
for nm, c in (('p_stock', P_STOCK), ('paper', PAPER)):
    m = near(lab, c)
    out['sheet_' + nm] = dict(px=int(m.sum()), median_L=round(float(np.median(lab[..., 0][m])), 1) if m.any() else None)
for fid, t in (('fx_shield_block', 380.0), ('fx_brace_block', 380.0), ('fx_soak_take', 450.0)):
    s = E.FX[fid]
    f = np.clip(s['render'](t, 'neutral', False), 0, 255)
    r = np.clip(s['render'](t, 'neutral', False, marks=False), 0, 255)
    add = np.abs(f - r).max(2) > 6
    la = RT.lab(f[add])
    out[fid] = dict(t_ms=t, added_px=int(add.sum()), p_stock_px=int(near(la, P_STOCK).sum()), p_stock_shade_px=int(near(la, P_STOCK_D).sum()),
                    paper_px=int(near(la, PAPER).sum()), median_L_of_p_stock_px=round(float(np.median(la[near(la, P_STOCK), 0])), 1) if near(la, P_STOCK).any() else None)
    print(fid, out[fid], flush=True)
print({k: v for k, v in out.items() if k != 'method' and not k.startswith('fx_')}, flush=True)
json.dump(out, open(ME + 'work/pstock.json', 'w'), indent=1)
