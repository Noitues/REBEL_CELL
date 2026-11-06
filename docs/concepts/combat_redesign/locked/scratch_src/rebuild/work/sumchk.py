"""sumchk.py: summary of rebuild/board/checks.json rb_* sections (c failures by source, d minimum dE per group, a/e per plate)"""
import json
J = json.load(open('D:/rc_scratch/combat_redesign/locked/rebuild/board/checks.json'))
print('all_pass', J['all_pass'])
rc = J['rb_checks']
srcs = {}
for p, r in rc.items():
    c = r['c_cap_height']
    for f in c['failures']:
        srcs.setdefault(f.get('where'), set()).add((f['text'], f['cap_px']))
    a = r['a_cell_contrast']
    ratios = [x['ratio'] for x in a['rows'] if x['gated']]
    print('%-22s pass %s  a NOW %s min ratio %s  c n_fail %d  e %s' % (p, r['pass'], a['occ_now_L_range'], min(ratios) if ratios else None, c['n_fail'],
          (r['e_hand']['hand_x_send_px'], r['e_hand']['hand_x_undo_px'], r['e_hand']['lifted_vs_sibling'])))
print('c failures by source:', {k: sorted(v) for k, v in srcs.items()})
d = rc['p1_decide']['d_palette']
print('d keys', [k for k in d.keys()])
for k, v in d.items():
    if isinstance(v, list) and v and isinstance(v[0], dict) and 'dE' in v[0]:
        m = min(v, key=lambda q: q['dE'])
        print('  d', k, 'n', len(v), 'min', m)
