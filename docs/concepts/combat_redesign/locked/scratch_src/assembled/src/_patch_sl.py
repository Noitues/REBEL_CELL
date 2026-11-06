import re
p='xf_tower.py'
s=open(p,encoding='utf8').read()
s=s.replace("from xf_gfx import *\n","from xf_gfx import *\nimport xf_slices as XS\n",1)
s=s.replace("    ink(cv, mg, MAG, 0.07, seed + 21)\n    mg_in = mg\n","    fillc, texc, texop = XS.palette(VAR[0], w['t'])\n    ink(cv, mg, fillc, 0.07, seed + 21)\n    mg_in = mg\n",1)
old=s[s.index("    cov = 0.62 * np.clip((100.0 - rr) / 28.0, 0, 1) ** 1.2"):s.index("    # 4. stencil highlight")]
new='''    # per-type texture, tone-on-tone, cleared around the icon and kept off the key edge
    tx = XS.texture(XS.TEXKIND[w['t']], cv, am, CT)
    tx = tx * np.clip((to_icon - 28.0) / 8.0, 0, 1) * shrink(mg_in, 3.2 * ss)
    ink(cv, tx, texc, 0.0, seed + 22, texop)
'''
s=s.replace(old,new,1)
open(p,'w',encoding='utf8').write(s)
