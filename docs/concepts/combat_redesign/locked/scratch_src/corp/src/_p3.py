p='de_kinds.py'
s=open(p).read()
s=s.replace("import cs_skin as CS\n","import cs_skin as CS\nimport corp_kinds as CK\n")
s=s.replace("""    L = L2()
    FB.screen(L, u)""","""    L = L2()
    restore = CK.use(getattr(skin, 'kind_gain', None) if skin is not None else None)
    FB.screen(L, u)
    restore()""")
s=s.replace("""if __name__ == '__main__':""","""def solve(skin, base_min, cap=3.0):
    \"\"\"smallest gain per ring (steps of 0.05) with skinned min dE >= base_min[ring]\"\"\"
    gains = [1.0, 1.0, 1.0]
    for dep in range(3):
        g = 1.0
        while g <= cap:
            skin.kind_gain = tuple(gains[:dep] + [g] + [1.0] * (2 - dep))
            r = measure_ring(skin, dep)
            if r['min'] >= base_min[dep]:
                break
            g = round(g + 0.05, 2)
        gains[dep] = min(g, cap)
    skin.kind_gain = tuple(gains)
    return tuple(gains)


def measure_ring(skin, dep):
    cols = {k: swatch(skin, k, dep) for k in KINDS}
    labs = {k: rgb2lab(c) for k, c in cols.items()}
    pr = [de2000(labs[a], labs[b]) for i, a in enumerate(KINDS) for b in KINDS[i + 1:]]
    return dict(min=min(pr), mean=sum(pr) / len(pr))


if __name__ == '__main__':""")
s=s.replace("""    res = {n: measure(n, s) for n, s in skins.items()}""","""    res = {}
    res['unskinned'] = measure('unskinned', None)
    base_min = [res['unskinned']['ring%d' % d]['min'] for d in range(3)]
    for n in ('neutral', 'solace', 'meridian'):
        sk = skins[n]
        res[n + '_before'] = measure(n, sk)
        if n != 'neutral' and 'nosolve' not in extra:
            res[n + '_gain'] = list(solve(sk, base_min))
        res[n] = measure(n, sk)""")
s=s.replace("""    for n, r in res.items():
        print""","""    for n, r in res.items():
        if isinstance(r, list):
            print(n, r); continue
        print""")
open(p,'w').write(s)
