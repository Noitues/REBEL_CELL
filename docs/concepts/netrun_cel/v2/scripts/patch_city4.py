p='nr_city_part.py'
s=open(p,encoding='utf-8').read()
def rep(a,b):
    global s
    assert a in s, a[:70]
    s=s.replace(a,b,1)
rep("            for _ in range(2):\n                if R2.random() > TREE_P: continue","            for _ in range(TREE_N):\n                if R2.random() > TREE_P: continue")
rep("                s = R2.uniform(2.6, 4.6)","                s = R2.uniform(*TREE_S)")
rep("TREE_P = 0.18","TREE_P = 0.18\nTREE_N = 2\nTREE_S = (2.6, 4.6)")
rep("def lot_class_col(i, j):\n    t = (i, j)","def lot_class_col(i, j):\n    t = (i, j)\n    if FRAME == 'f2':\n        if t in PLAZA: return hexc('#4a4a70')\n        if t in PARK and t not in STREET: return hexc('#1f7a42')\n        if t in STREET: return hexc('#2c2842')\n        return hexc('#38335a')")
rep("    TREE_CLEAR[:] =","    if FRAME == 'f2':\n        TREE_P = 0.95; TREE_N = 3; TREE_S = (4.0, 7.0)\n    TREE_CLEAR[:] =")
rep("    global FOCUS_L, TEXT_COLL, WS","    global FOCUS_L, TEXT_COLL, WS, TREE_P, TREE_N, TREE_S")
rep("'0.85' if FRAME == 'f2' else '0.5'","'1.7' if FRAME == 'f2' else '0.5'")
open(p,'w',encoding='utf-8').write(s)
