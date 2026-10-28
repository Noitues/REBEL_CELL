import json, sys
for b in sys.argv[1:]:
    s = json.load(open('D:/rc_scratch/tide_concepts/p2_work/%s/spec.json' % b))
    print(b, {k: len(v) for k, v in s.items() if isinstance(v, list)}, s['samples'], s['spill_samples'])
    print('  ribbons', [(r['id'], round(r['w'], 1), r.get('alpha'), round(r['s1'] - r['s0'])) for r in s['ribbons']])
