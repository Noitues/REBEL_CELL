"""skin_check: print parts of the port-2 skin table (exploration)."""
import json, sys

d = json.load(open(sys.argv[1], encoding='utf-8'))
for nm in ('solace', 'meridian', 'neutral'):
    s = d['skins'][nm]
    print('==', nm, s['cls'], s['kind_gain'], s['room'], s['c_scan_ink'], s['c_scan_key'])
    print('  pal', s['pal'])
    for m, v in s['methods'].items():
        if not v:
            continue
        print('  ', m, v['source'])
        for r in v['layers']:
            print('      ', json.dumps(r)[:230])
    print('  measured', s['measured_on_plates'])
print(json.dumps(d['clock'], indent=0)[:2500])
print(d['time_grade'])
print(d['cells']['kind_fill'], d['cells']['empty_fill'])
