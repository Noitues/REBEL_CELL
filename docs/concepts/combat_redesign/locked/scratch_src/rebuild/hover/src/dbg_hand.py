"""debug the hand layout search on one plate's board cache: which rule blocks the resting cards and the lifted card"""
import sys, os, json
sys.dont_write_bytecode = True
import numpy as np
import hv_plates as P
import hv_core as V
import hv_comp as K
from scipy import ndimage as ndi

pid = sys.argv[1] if len(sys.argv) > 1 else 'h02'
lift = sys.argv[2] if len(sys.argv) > 2 else 'Brace'
hand = ['Brace', 'Spin3', 'Trigger', 'Twist'] if len(sys.argv) <= 3 else sys.argv[3].split(',')
# board from cache: replay make() up to the board
f_live, f_plan = P.frames([('Brace', 2)], hand) if pid == 'h02' else P.frames([], hand)
K.reset_all()
fb = f_plan
bg = K.board('p1', fb, f_plan, P.ftag(fb, V.CORP), True)
K.button_masks(True)
H, W, C = 1080, 1920, V.C
yy, xx = np.mgrid[0:H, 0:W]
rho = np.hypot(xx - C[0], yy - C[1])
btn = ndi.binary_dilation(K.BTN['send'] | K.BTN['undo'], iterations=2)
n = len(hand)
hov = hand.index(lift)
base = V.FH.slots(n)
print('slots', base)
for push in (16, 0, -16):
    for fan in (0, -8):
        print('== fan', fan, 'push', push)
        for i, nm in enumerate(hand):
            if i == hov:
                continue
            s = base[i]
            cx = s['cx'] + fan + (push if i > hov else 0)
            m, w2, h2 = K._card_mask(nm, False, 'normal', V.FH.CARD_SCALE, s['ang'])
            x0, y0 = K._place(m, cx, s['cy'])
            full = np.zeros((H, W), bool)
            K._paste(full, m, x0, y0)
            print('  ', nm, 'r455', int((full & (rho < 455)).sum()), 'btn', int((full & btn).sum()), 'below', int((full & (yy > 1067)).sum()),
                  'minr', round(float(rho[full].min()), 1), 'ymax', int(np.nonzero(full.any(1))[0].max()), 'x', x0, x0 + m.shape[1])
lm, w2, h2 = K._card_mask(lift, False, 'hover', 1.10 * V.FH.CARD_SCALE, 0.0)
print('lift mask', lm.shape)
arcs = ndi.binary_dilation(V.MASKS['arcs'], iterations=3)
for cy in (800, 832, 866):
    for dx in (-40, 0, 40):
        x0, y0 = K._place(lm, base[hov]['cx'] + dx, cy)
        full = np.zeros((H, W), bool)
        K._paste(full, lm, x0, y0)
        print('lift cy', cy, 'dx', dx, 'r459', int((full & (rho < 459)).sum()), 'arcs', int((full & arcs).sum()), 'btn', int((full & btn).sum()),
              'below', int((full & (yy > 1067)).sum()), 'ymax', int(np.nonzero(full.any(1))[0].max()), 'minr', round(float(rho[full].min()), 1))
