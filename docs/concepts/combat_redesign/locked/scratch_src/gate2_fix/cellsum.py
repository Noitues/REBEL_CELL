"""cellsum.py: per ring, the lowest gated occupied/empty ratio across the plates in rebuild/board/checks.json (rb_checks a), and the
occupied / reference-empty L* ranges"""
import json, sys
sys.dont_write_bytecode = True
R = json.load(open('D:/rc_scratch/combat_redesign/locked/rebuild/board/checks.json'))['rb_checks']
lo = {}
occ = {}
ref = {}
for name, r in R.items():
    a = r['a_cell_contrast']
    for row in a['rows']:
        if not row.get('gated'):
            continue
        d = row['ring']
        if d not in lo or row['ratio'] < lo[d][0]:
            lo[d] = (row['ratio'], name, row['kind'], row['state'])
        occ.setdefault(d, []).append(row['occ_L'])
        ref.setdefault(d, []).append(row['empty_L'])
for d in sorted(lo):
    print('ring', d, 'lowest ratio %.2f %s %s %s' % lo[d], 'occ L* %.1f-%.1f' % (min(occ[d]), max(occ[d])), 'ref empty L* %.1f-%.1f' % (min(ref[d]), max(ref[d])))
