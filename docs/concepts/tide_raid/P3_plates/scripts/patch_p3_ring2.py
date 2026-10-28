for fn in ('p1_spec.py', 'p2_tex.py'):
    s = open(fn).read()
    s = s.replace("TIER_R = {'UNTOUCHED': 9.5, 'HOLDS': 10.5, 'SITES_LOST': 10.5, 'DAMAGED': 11.5, 'BREACHED': 12.5}",
                  "TIER_R = {'UNTOUCHED': 11.4, 'HOLDS': 12.6, 'SITES_LOST': 12.6, 'DAMAGED': 13.8, 'BREACHED': 15.0}     # P3: x1.2 (the tower fills the middle of the ring)")
    if fn == 'p1_spec.py':
        s = s.replace("r=r * 1.05, col=c, strength=1.1 * k, power=1.5, z=0.42, ghost=ghost))", "r=r * 1.05, col=c, strength=(0.0 if tier == 'SITES_LOST' else 0.5) * k, power=1.5, z=0.42, ghost=ghost))")
        s = s.replace("pad_strength=2.0 * k))", "pad_strength=1.1 * k))")
    open(fn, 'w').write(s)
print('ok')
