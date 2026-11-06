p='nr_city_part.py'
s=open(p,encoding='utf-8').read()
def rep(a,b):
    global s
    assert a in s, a[:70]
    s=s.replace(a,b,1)
rep("            for _ in range(2):\n                if R2.random() > 0.5: continue","            if math.hypot(i - TREE_CLEAR[0], j - TREE_CLEAR[1]) < TREE_CLEAR[2]: continue\n            for _ in range(2):\n                if R2.random() > TREE_P: continue")
rep("                s = R2.uniform(3.6, 6.4)","                s = R2.uniform(2.6, 4.6)")
rep("def build_trees(reg, focus, rad):","TREE_CLEAR = [0, 0, 0]\nTREE_P = 0.18\ndef build_trees(reg, focus, rad):")
rep("    CAMS['f3'] = (LOT(-37.0, -33.5, 14.0), LOT(-37.0, -23.0, 11.0), 24)","    CAMS['f3'] = (LOT(-37.0, -31.8, 22.0), LOT(-37.0, -22.0, 9.0), 24)\n    TREE_CLEAR[:] = [-37.0, -31.8, 7.0] if FRAME == 'f3' else ([-78.0, -36.5, 6.0] if FRAME == 'f4' else [0, 0, 0])\n    os.environ['NR_WINSCALE'] = os.environ.get('NR_WINSCALE', '2.6' if FRAME == 'f2' else '1.0')")
open(p,'w',encoding='utf-8').write(s)
