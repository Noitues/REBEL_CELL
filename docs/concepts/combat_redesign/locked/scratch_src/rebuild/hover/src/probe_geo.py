"""print board geometry constants used by the hover marks (read only)"""
import sys, os
sys.dont_write_bytecode = True
import hv_core as V
print('HALF', V.RA.HALF, 'LANES', V.RA.LANE_R, 'rings', [V.CB.ring_geom(d) for d in range(3)], 'tokens', V.T.TOKENS.get('PLAN'))
print('LIFT', V.FH.LIFT_S, V.FH.LIFT_CY, V.FH.CARD_SCALE, V.FH.REST_V, 'slots', V.FH.slots(4))
print('path_pts', V.A.H2.path_pts(V.A.J['f1'])[:3], '...', len(V.A.H2.path_pts(V.A.J['f1'])))
