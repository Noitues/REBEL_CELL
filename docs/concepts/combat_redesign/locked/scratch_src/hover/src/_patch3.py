p='xf_slices.py'
s=open(p,encoding='utf8').read()
a=s.index("def tex_scales"); b=s.index("def texture(")
new='''def tex_scales(u, v, r=8.6, lw=1.9):
    """scalloped fish-scale rows: outward half-circles, rows one radius apart, alternate rows offset by one radius"""
    h = r
    out = np.zeros(u.shape, np.float32)
    j0 = int(np.floor(float(u.min()) / h)) - 2
    j1 = int(np.ceil(float(u.max()) / h)) + 1
    for j in range(j0, j1 + 1):
        uc = j * h
        off = (j % 2) * r
        vc = np.round((v - off) / (2 * r)) * (2 * r) + off
        d = np.hypot(u - uc, v - vc)
        ring = _aa(np.abs(d - r) - lw / 2) * (u >= uc - 0.3)
        out = np.maximum(out, ring)
    return out


'''
s=s[:a]+new+s[b:]
s=s.replace("def tex_plus(u, v, p=13.0, hl=4.4, ht=1.35)","def tex_plus(u, v, p=20.0, hl=6.6, ht=2.1)")
s=s.replace("'BURST':  dict(fill='E9E3D2', tex='8C846F'","'BURST':  dict(fill='F0EBDC', tex='A8A08A'")
open(p,'w',encoding='utf8').write(s)
