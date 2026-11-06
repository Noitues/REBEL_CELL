"""scan the lifted card's free positions on one plate's board (bad_lift only), wide dx range"""
import sys, os
sys.dont_write_bytecode = True
import numpy as np
import hv_plates as P
import hv_core as V
import hv_comp as K
from scipy import ndimage as ndi

pid = sys.argv[1] if len(sys.argv) > 1 else 'h02'
lift = sys.argv[2] if len(sys.argv) > 2 else 'Brace'
hand = ['Brace', 'Spin3', 'Trigger', 'Twist'] if len(sys.argv) <= 3 else sys.argv[3].split(',')
f_live, f_plan = P.frames([('Brace', 2)], hand) if pid == 'h02' else P.frames([], hand)
K.reset_all()
bg = K.board('p1', f_plan, f_plan, P.ftag(f_plan, V.CORP), True)
K.button_masks(True)
H, W, C = 1080, 1920, V.C
yy, xx = np.mgrid[0:H, 0:W]
rho = np.hypot(xx - C[0], yy - C[1])
btn = ndi.binary_dilation(K.BTN['send'] | K.BTN['undo'], iterations=2)
arcs = ndi.binary_dilation(V.MASKS['arcs'], iterations=V.Z.LIFT_ARC_GAP)
r459 = rho < V.FH.HAND_MIN_R + V.Z.LIFT_CLEAR
below = yy > K.HAND_BOTTOM
base = V.FH.slots(len(hand))
print('slots', [(round(s['cx']), round(s['cy']), round(s['ang'], 2)) for s in base])
print('C', C, 'HAND_MIN_R', V.FH.HAND_MIN_R, 'LIFT_CLEAR', V.Z.LIFT_CLEAR, 'LIFT_S', V.FH.LIFT_S, 'CARD_SCALE', V.FH.CARD_SCALE)
hov = hand.index(lift)
for ls in (1.10, 1.04, 1.0, 0.96):
    m, w2, h2 = K._card_mask(lift, False, 'hover', ls * V.FH.CARD_SCALE, 0.0)
    print('== scale', ls, 'mask', m.shape)
    for cy in range(788, 885, 12):
        row = []
        for dx in range(-80, 260, 8):
            x0, y0 = K._place(m, base[hov]['cx'] + dx, cy)
            full = np.zeros((H, W), bool)
            K._paste(full, m, x0, y0)
            a = int((full & r459).sum()); b = int((full & arcs).sum()); c = int((full & btn).sum()); d = int((full & below).sum())
            row.append('.' if a + b + c + d == 0 else ('r' if a else ('a' if b else ('b' if c else 'y'))))
        print(cy, ''.join(row))
