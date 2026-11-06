"""run hv_comp.hand_layout on one plate's cached board with stage counts"""
import sys, os, time
sys.dont_write_bytecode = True
import numpy as np
import hv_plates as P
import hv_core as V
import hv_comp as K

pid = sys.argv[1] if len(sys.argv) > 1 else 'h02'
lift = sys.argv[2] if len(sys.argv) > 2 else 'Brace'
hand = ['Brace', 'Spin3', 'Trigger', 'Twist'] if len(sys.argv) <= 3 else sys.argv[3].split(',')
f_live, f_plan = P.frames([('Brace', 2)], hand) if pid == 'h02' else P.frames([], hand)
K.reset_all()
bg = K.board('p1', f_plan, f_plan, P.ftag(f_plan, V.CORP), True)
K.button_masks(True)
# instrument
orig_hit = K._hit
t = time.time()
lay = K.hand_layout(hand, lift, False)
print('time', round(time.time() - t, 1))
print('STATS1', K.HL_STATS)
if lay is None:
    print('NONE')
    # count feasible resting layouts
    K.N_REST_KEEP = 10 ** 6
    lay2 = None
    print('rest only (lift None, all cards resting):', None if lay2 is None else (lay2['n_rest_feasible'], lay2['fan'], lay2['push']))
else:
    print({k: v for k, v in lay.items() if k not in ('cards', 'lift')})
    print('lift', {k: v for k, v in lay['lift'].items() if k != '_m'})
    for c in lay['cards']:
        print('  ', c['name'], round(c['cx']), round(c['cy']), round(c['ang'], 2))
print('STATS', K.HL_STATS)
