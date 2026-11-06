p='nr_city_part.py'
s=open(p,encoding='utf-8').read()
def rep(a,b):
    global s
    assert a in s, a[:70]
    s=s.replace(a,b,1)
rep("    CAMS['f3'] = (LOT(-37.0, -31.8, 22.0), LOT(-37.0, -22.0, 9.0), 24)","    CAMS['f3'] = (LOT(-37.5, -27.1, 15.0), LOT(-37.5, -21.0, 10.0), 22)")
rep("TREE_CLEAR[:] = [-37.0, -31.8, 7.0] if FRAME == 'f3'","TREE_CLEAR[:] = [-37.5, -27.1, 6.0] if FRAME == 'f3'")
rep("    def blvd(i): return -23.5 if i < -46 else (-25.0 if i > -41 else -23.5 + (-1.5) * (i + 46) / 5.0)","    def blvd(i): return -23.55")
# street colour lines from the real street data
rep("def build_trees(reg, focus, rad):","""def build_street_lines(reg, focus, rad):
    i0, i1, j0, j1 = reg
    for a in CITY['streets']:
        i, j, ai, aj, tr, col = a
        if not (i0 <= i <= i1 and j0 <= j <= j1) or col == '000000' or col == '': continue
        if math.hypot(i - focus[0], j - focus[1]) > rad: continue
        c = hexc('#' + col, 2.4 if tr > 0.3 else 1.1)
        w = 0.5 + 1.2 * min(1.0, tr)
        cx, cy = lot_xy(i + 0.5, j + 0.5); z = gz(cx, cy) + 0.07
        if ai: quad_flat('flat', [(cx - LM / 2, cy - w, z), (cx + LM / 2, cy - w, z), (cx + LM / 2, cy + w, z), (cx - LM / 2, cy + w, z)], c)
        if aj: quad_flat('flat', [(cx - w, cy - LM / 2, z), (cx + w, cy - LM / 2, z), (cx + w, cy + LM / 2, z), (cx - w, cy + LM / 2, z)], c)

def build_trees(reg, focus, rad):""")
rep("    build_trees(cfgs['reg'], (cfgs['tree'][0], cfgs['tree'][1]), cfgs['tree'][2])","    build_trees(cfgs['reg'], (cfgs['tree'][0], cfgs['tree'][1]), cfgs['tree'][2])\n    if FRAME == 'f2': build_street_lines(cfgs['reg'], (-45, -26), 55)")
open(p,'w',encoding='utf-8').write(s)
