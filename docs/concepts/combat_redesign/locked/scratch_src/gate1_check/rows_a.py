import json, sys
d = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/checks.json'))
for plate, v in d['rb_checks'].items():
    a = v['a_cell_contrast']
    print('==', plate, 'pass', a['pass_'], 'occNOW', a['occ_now_L_range'])
    for r in a['rows']:
        print('   r%d s%d u%s %-8s %-8s occ %5.1f emp %5.1f ratio %5.2f gated %s px %d' % (r['ring'], r['sector'], r['unit'], r['kind'], r['state'], r['occ_L'], r['empty_L'], r['ratio'], r['gated'], r['px']))
    print('   rings', json.dumps(a['rings']))
print(d['rb_checks']['p1_decide']['a_cell_contrast']['rule'])
