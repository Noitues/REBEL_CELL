"""fit_ring on the h01 board (LANDS 13) as the plate calls it"""
import sys
sys.dont_write_bytecode = True
import hv_plates as P, hv_core as V, hv_comp as K
hand = ['Brace', 'Spin3', 'Trigger', 'Twist']
f_live, f_plan = P.frames([('Spin3', 3)], hand)
K.reset_all()
bg = K.board('p1', f_plan, f_plan, P.ftag(f_plan, V.CORP), True)
L = V.L2()
V.NOW['words'] = True
print(V.bill_marks(L, f_live, f_plan, True))
print(V.FIT_LOG)
