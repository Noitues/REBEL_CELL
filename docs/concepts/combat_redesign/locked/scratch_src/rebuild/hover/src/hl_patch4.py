p = 'hv_comp.py'
s = open(p, encoding='utf-8').read()
s = s.replace("""    def rest_feasible():
        \"\"\"the resting layouts that pass, cheapest first (lazily)\"\"\"
        for cost, fan, pre, push, rest in rest_opts:""", """    def rest_feasible(opts):
        \"\"\"the resting layouts that pass, in the order given (lazily)\"\"\"
        for cost, fan, pre, push, rest in opts:""", 1)
s = s.replace("""        for fr in rest_feasible():
            cost, fan, pre, push, rest, sl, cards = fr
            return dict(""", """        for fr in rest_feasible(rest_opts):
            cost, fan, pre, push, rest, sl, cards = fr
            return dict(""", 1)
a = s.index("    best, tried, n_fr = None, 0, 0\n")
b = s.index("    HL_STATS.update(tried=tried, feasible_rest_tried=n_fr")
new = '''    ST = dict(best=None, tried=0, n_fr=0)

    def try_rest(fr):
        cost0, fan, pre, push, rest, sl, cards = fr
        best = ST['best']
        ST['n_fr'] += 1
        rm = np.zeros((H, W), bool)
        for c in cards:
            rm |= _region_mask(c, 'cost') | _region_mask(c, 'rules')
        S_rm = _integral(rm)
        s = sl[hov]
        for c_l, ls, cy, dx, m, w2, h2, x0, y0 in lift_free(s['cx']):
            c_ = cost0 + c_l
            if best is not None and c_ >= best['cost']:
                return
            ST['tried'] += 1
            if _fast_hit(S_rm, rm, m, x0, y0):
                continue
            ST['best'] = dict(cards=cards, lift=dict(name=lift, role='lift', cx=float(s['cx'] + dx), cy=float(cy), ang=0.0, scale=float(ls * FH.CARD_SCALE),
                                                     w2=w2, h2=h2, _m=(m, x0, y0), lift_s=ls, dx=dx), fan=fan, pre=pre, push=push, rest=rest, cost=c_)
            return
    # warm start: the layouts that open the widest gap after the lifted card (and before it), so the full pass below can prune by cost
    warm = sorted(rest_opts, key=lambda o: (-(o[3] - o[2]), o[0]))
    k_w = 0
    for fr in rest_feasible(warm):
        try_rest(fr)
        k_w += 1
        if ST['best'] is not None or k_w >= 40:
            break
    for fr in rest_feasible(rest_opts):
        if ST['best'] is not None and fr[0] >= ST['best']['cost']:
            break
        try_rest(fr)
    best, tried, n_fr = ST['best'], ST['tried'], ST['n_fr']
'''
s = s[:a] + new + s[b:]
open(p, 'w', encoding='utf-8').write(s)
print('ok')
