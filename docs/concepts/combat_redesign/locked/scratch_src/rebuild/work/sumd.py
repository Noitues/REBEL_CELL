"""sumd.py: minimum dE76 per palette group, per skin (from rebuild/board/checks.json)"""
import json
J = json.load(open('D:/rc_scratch/combat_redesign/locked/rebuild/board/checks.json'))
for p in ('p1_decide', 'p1_decide_solace', 'p1_decide_meridian'):
    d = J['rb_checks'][p]['d_palette']
    g = {}
    for r in d['rows']:
        if r.get('dE') is None:
            continue
        k = r['group']
        if k not in g or r['dE'] < g[k]['dE']:
            g[k] = r
    print(p, 'pairs', d['n_pairs'], 'fails', len(d['failures']))
    for k, r in g.items():
        print('   %-34s min %5.1f  %s vs %s  gated=%s' % (k, r['dE'], r['a'], r['b'], r.get('pass_')))
