"""skip_tab.py: the round-2 SKIP key hint of the resolve beat (call C12), drawn with the generator's own HUD kit (corp/src, read-only):
a terminal tab (hud2.P: navy glass at 93 %, NET_CYAN edge, r8, scanlines) docked under the HUD's bottom edge at its right end, hung on a
cyan hairline like the REFUND tab; inside, an inset key (hud2.inset) holding 'ANY KEY' and the word 'SKIP', both in the one HUD label
spec (Share Tech Mono at hud2.LBL_PX = 23 px, tracking LBL_TRK, cap height 16.1 px).  -> work/skip_tab.png (1920x1080 RGBA) and
work/skip_tab.json (boxes).  Nothing is written under corp/."""
import sys, os, json
sys.dont_write_bytecode = True
os.environ.setdefault('CORP', 'neutral')
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
ME = 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_mpst/'
sys.path.insert(0, SRC)
os.chdir(SRC)
_argv = sys.argv[:]
sys.argv = [sys.argv[0], 'p3']
import lw_render as LW
sys.argv = _argv
LW.R.WORK = ME + 'work/tower_cache_neutral/'
LW.R.FH.CACHE = ME + 'work/tower_cache_neutral/'
import hud2 as H
import numpy as np
from PIL import Image

# geometry: the p3 HUD's RAM / TRACE / HEAT plate, measured on the published round-2 p3_resolve.png (hud_probe.py): x 1072-1892, foot y 667
HUD_X1, HUD_FOOT = 1892, 667
TAB_GAP, TAB_H = 6, 32            # the REFUND tab's own gap and height (rb2_patch REFUND_TAB_GAP, REFUND_TAB_H)
PAD, KEY_PAD, GAP = 10, 7, 10     # tab side padding, key inset padding, key-to-word gap
KEY_WORD, WORD = 'ANY KEY', 'SKIP'


def draw():
    L = LW.R.L2()
    px, trk = H.LBL_PX, H.LBL_TRK
    wk = H.ttw(L, KEY_WORD, px, 'mono', trk)
    ww = H.ttw(L, WORD, px, 'mono', trk)
    w = PAD + KEY_PAD + wk + KEY_PAD + GAP + ww + PAD
    x1 = HUD_X1
    x0 = x1 - w
    t0 = HUD_FOOT + TAB_GAP
    box = (x0, t0, x1, t0 + TAB_H)
    cx = (x0 + x1) / 2
    L.line([(cx, HUD_FOOT - 2), (cx, t0 + 2)], H.CYAN, 2.0)                # hung on a hairline from the HUD's foot, as the REFUND tab
    H.P(L, box, 'plate')
    kb = (x0 + PAD, t0 + 4, x0 + PAD + KEY_PAD + wk + KEY_PAD, t0 + TAB_H - 4)
    H.inset(L, kb)
    cy = t0 + TAB_H / 2
    H.txt(L, kb[0] + KEY_PAD, cy, KEY_WORD, px, H.TMID, 'mono', 'lm', trk)
    H.txt(L, kb[2] + GAP, cy, WORD, px, H.CYAN, 'mono', 'lm', trk)
    im = L.done()
    return im, dict(tab=[round(v, 1) for v in box], key=[round(v, 1) for v in kb], word_x=round(kb[2] + GAP, 1), text_cy=cy, label_px=px, label_track=trk,
                    hud_x1=HUD_X1, hud_foot=HUD_FOOT, key_word=KEY_WORD, word=WORD)


if __name__ == '__main__':
    im, geo = draw()
    os.makedirs(ME + 'work', exist_ok=True)
    im.save(ME + 'work/skip_tab.png')
    a = np.asarray(im)[..., 3]
    ys, xs = np.nonzero(a > 8)
    geo['alpha_bbox'] = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    json.dump(geo, open(ME + 'work/skip_tab.json', 'w'), indent=1)
    print('ok', geo, flush=True)
