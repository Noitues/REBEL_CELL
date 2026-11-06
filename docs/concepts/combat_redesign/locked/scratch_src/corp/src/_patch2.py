p='xf_slices.py'
s=open(p,encoding='utf8').read()
s=s.replace("def tex_scales(u, v, r=7.2, h=3.6, lw=1.15)","def tex_scales(u, v, r=10.5, h=5.0, lw=1.9)")
s=s.replace("def tex_plus(u, v, p=11.0, hl=3.4, ht=0.95)","def tex_plus(u, v, p=13.0, hl=4.4, ht=1.35)")
s=s.replace("def tex_dots(u, v, p=9.5, r=2.9)","def tex_dots(u, v, p=10.0, r=3.3)")
open(p,'w',encoding='utf8').write(s)
p='xf_tower.py'
s=open(p,encoding='utf8').read()
old="""        cv.paint(reg, TONER, 0.5)
        hf = hatch_cached(cv, (45, 135), 6.0, 1.7, 77)
        cv.paint(hf * reg, col, 0.9)
"""
new="""        cv.paint(reg, TONER, 0.24)
        hf = hatch_cached(cv, (45, 135), 6.4, 1.6, 77)
        cv.paint(np.clip(grow(hf, 0.85 * ss), 0, 1) * reg, TONER, 0.92)       # black casing so the red reads on every slice ink
        cv.paint(hf * reg, col, 1.0)
"""
assert old in s
s=s.replace(old,new)
open(p,'w',encoding='utf8').write(s)
