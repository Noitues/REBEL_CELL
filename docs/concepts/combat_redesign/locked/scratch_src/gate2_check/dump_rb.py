"""dump_rb.py <checks.json> [plate ...] -- print a rows, b marks, room ref, d lowest, c smallest per plate."""
import sys, json

d = json.load(open(sys.argv[1], encoding='utf-8'))
rb = d['rb_checks']
plates = sys.argv[2:] or list(rb.keys())
for p in plates:
    r = rb[p]
    print('==', p)
    a = r['a_cell_contrast']
    for row in a['rows']:
        print('  a', {k: row.get(k) for k in ('ring', 'sector', 'unit', 'kind', 'state', 'occ_L', 'empty_L', 'ratio', 'gated', 'pass_', 'px')})
    for ring, v in a['rings'].items():
        print('  a ring', ring, json.dumps(v)[:400])
    print('  a occ_now', a.get('occ_now_L_range'), 'adj', a.get('adjuster_hp'))
    b = r['b_value_order']
    for s in b['sorted']:
        print('  b fam %-34s p95 %5.1f med %5.1f mean %5.1f px %d' % (s['family'], s['p95'], s['median'], s['mean'], s['px']))
    for k, v in b['marks'].items():
        print('  b mark %-28s fam %s p95 %s p99 %s med %s px %s %s' % (k, v.get('family'), v.get('p95'), v.get('p99'), v.get('median'), v.get('px'), v.get('rules')))
    print('  b probes', b.get('probes'), 'room_ref', b.get('room_ref'), 'fail', b.get('failures'))
    c = r['c_cap_height']
    print('  c n', c['n'], 'fail', c['n_fail'], 'smallest', [(s['text'], s['cap_px'], s['where']) for s in c['smallest'][:6]], 'parked', c['parked']['n'], c['parked']['smallest_cap_px'], 'uncapt', c['uncaptured_text'])
    dd = r['d_palette']
    rows = sorted(dd['rows'], key=lambda x: x['dE'])
    print('  d n', dd['n_pairs'], 'fail', dd['failures'][:5])
    for x in rows[:8]:
        print('    d', x['group'], x['a'], x['a_hex'], x['b'], x['b_hex'], x['dE'])
