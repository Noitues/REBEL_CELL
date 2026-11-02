import f1_geo
import sys
import gram_render as R
import o_arcs
print(o_arcs.LANE_R, o_arcs.HALF)
R.A2.LANE_R[:] = [436, 453, 470]
im = R.render('p1', cfg=dict(time='A'))
im.save('../out/t_geo.png')
