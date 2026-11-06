import json, sys
for nm in sys.argv[1:]:
    r = json.load(open('D:/rc_scratch/combat_redesign/locked/rebuild/hover/chk/%s.json' % nm))
    h = r['hand']
    print(nm, {k: v for k, v in h.items() if k != 'cards'})
    for c in h['cards']:
        print('   ', {k: (round(v, 1) if isinstance(v, float) else v) for k, v in c.items() if k not in ('poly', 'mask')})
